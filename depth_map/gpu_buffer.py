from functools import cache
import time

import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from ..utils import get_pref
from ..adapter import is_5_0_up_version

# White background, black silhouette. The depth texture is drawn minified by depth_scale, so each
# fragment box-filters the geometry mask (depth < 1.0) over its footprint for anti-aliased edges.
_SILHOUETTE_FRAG_FUNCS = """
float geometry_mask(ivec2 size, vec2 p)
{
    vec2 q = p - 0.5;
    ivec2 c = ivec2(floor(q));
    vec2 f = q - vec2(c);
    ivec2 hi = size - 1;
    float m00 = texelFetch(tex, clamp(c, ivec2(0), hi), 0).x < 1.0 ? 1.0 : 0.0;
    float m10 = texelFetch(tex, clamp(c + ivec2(1, 0), ivec2(0), hi), 0).x < 1.0 ? 1.0 : 0.0;
    float m01 = texelFetch(tex, clamp(c + ivec2(0, 1), ivec2(0), hi), 0).x < 1.0 ? 1.0 : 0.0;
    float m11 = texelFetch(tex, clamp(c + ivec2(1, 1), ivec2(0), hi), 0).x < 1.0 ? 1.0 : 0.0;
    return mix(mix(m00, m10, f.x), mix(m01, m11, f.x), f.y);
}
"""

_SILHOUETTE_FRAG_BODY = """
    ivec2 size = textureSize(tex, 0);
    vec2 center = texCoord * vec2(size);
    float span = max(footprint, 1.0);
    int taps = int(clamp(ceil(span), 1.0, 8.0));
    float coverage = 0.0;
    for (int y = 0; y < taps; y++) {
        for (int x = 0; x < taps; x++) {
            vec2 offset = (vec2(x, y) + 0.5) / float(taps) - 0.5;
            coverage += geometry_mask(size, center + offset * span);
        }
    }
    float silhouette = 1.0 - coverage / float(taps * taps);
    FragColor = vec4(silhouette, silhouette, silhouette, 1.0);
"""

# Full-region depth readback stalls the GPU; while a view navigation modal runs, refresh at most this often.
_NAVIGATION_REFRESH_INTERVAL = 1 / 30

_silhouette_cache = {
    # region pointer: {"key", "texture", "time"}
}
_redraw_timer_pending = False


def _silhouette_cache_key(context, width, height):
    rv3d = context.space_data.region_3d
    view_matrix = rv3d.view_matrix
    window_matrix = rv3d.window_matrix
    window = getattr(context, "window", None)
    modal_count = len(window.modal_operators) if window is not None else 0
    return (
        width,
        height,
        tuple(round(v, 5) for row in view_matrix for v in row),
        tuple(round(v, 5) for row in window_matrix for v in row),
        round(rv3d.view_distance, 5),
        rv3d.view_perspective,
        modal_count,
    )


def get_coord(st=(-1, -1), interval=(2, 2)):
    """Return quad corner coords; triangle order (0, 1, 2), (0, 2, 3)."""
    x = st[0]
    y = st[1]
    int_x = interval[0]
    int_y = interval[1]
    return (
        (x, y), (x + int_x, y),
        (x + int_x, y + int_y), (x, y + int_y)
    )


@cache
def shader_50():
    """Blender gpu 5.0 api"""
    tex_coord_out = gpu.types.GPUStageInterfaceInfo("w")
    tex_coord_out.smooth('VEC2', "texCoord")

    shader_info = gpu.types.GPUShaderCreateInfo()
    shader_info.push_constant('MAT4', "ModelViewProjectionMatrix")
    shader_info.push_constant('FLOAT', "footprint")
    shader_info.vertex_in(0, 'VEC2', "pos")
    shader_info.vertex_in(1, 'VEC2', "texCoordIn")
    shader_info.vertex_out(tex_coord_out)
    shader_info.sampler(0, "FLOAT_2D", "tex")

    shader_info.fragment_out(0, 'VEC4', "FragColor")

    shader_info.vertex_source("""
        void main()
        {
            texCoord = texCoordIn;
            gl_Position = ModelViewProjectionMatrix * vec4(pos.xy, 0.0f, 1.0f);
        }
        """)

    shader_info.fragment_source(f"""
        {_SILHOUETTE_FRAG_FUNCS}
        void main()
        {{
        {_SILHOUETTE_FRAG_BODY}
        }}
        """)

    shader = gpu.shader.create_from_info(shader_info)
    return shader


@cache
def depth_shader():
    if is_5_0_up_version:
        shader = shader_50()
    else:
        vertex_shader = """
            uniform mat4 ModelViewProjectionMatrix;
            in vec2 pos;
            in vec2 texCoordIn;
            out vec2 texCoord;
            void main()
            {
                texCoord = texCoordIn;
                gl_Position = ModelViewProjectionMatrix * vec4(pos.xy, 0.0f, 1.0f);
            }
        """

        fragment_shader = f"""
            uniform sampler2D tex;
            uniform float footprint;
            in vec2 texCoord;
            out vec4 FragColor;
            {_SILHOUETTE_FRAG_FUNCS}
            void main()
            {{
            {_SILHOUETTE_FRAG_BODY}
            }}
        """
        shader = gpu.types.GPUShader(vertex_shader, fragment_shader)

    batch = batch_for_shader(
        shader, "TRIS",
        {
            "pos": get_coord(st=(0, -1), interval=(1, 1)),
            "texCoordIn": (
                (0, 0), (1, 0),
                (1, 1), (0, 1)),
        },
        indices=((0, 1, 2), (0, 2, 3))
    )
    batch.program_set(shader)
    shader.bind()
    return shader, batch


def _tag_view3d_redraw():
    global _redraw_timer_pending
    _redraw_timer_pending = False
    wm = getattr(bpy.context, "window_manager", None)
    if wm is None:
        return None
    for window in wm.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()
    return None


def _schedule_redraw():
    global _redraw_timer_pending
    if not _redraw_timer_pending:
        _redraw_timer_pending = True
        bpy.app.timers.register(_tag_view3d_redraw, first_interval=_NAVIGATION_REFRESH_INTERVAL)


def _read_silhouette_texture(context, width, height):
    region_key = context.region.as_pointer()
    entry = _silhouette_cache.get(region_key)
    key = _silhouette_cache_key(context, width, height)
    now = time.perf_counter()
    if entry is not None:
        if entry["key"] == key:
            return entry["texture"]
        same_size = entry["key"][:2] == key[:2]
        navigating = key[-1] > 0
        if same_size and navigating and now - entry["time"] < _NAVIGATION_REFRESH_INTERVAL:
            # Throttled; make sure the latest view still gets a refresh once navigation pauses.
            _schedule_redraw()
            return entry["texture"]

    depth_buffer = gpu.state.active_framebuffer_get().read_depth(0, 0, width, height)
    texture = gpu.types.GPUTexture((width, height), format="DEPTH_COMPONENT32F", data=depth_buffer)

    if entry is None and len(_silhouette_cache) >= 8:
        _silhouette_cache.clear()
    _silhouette_cache[region_key] = {"key": key, "texture": texture, "time": now}
    return texture


def draw_shader_old(context, width, height, depth_scale):
    shader, batch = depth_shader()
    texture = _read_silhouette_texture(context, width, height)

    mv = gpu.matrix.get_model_view_matrix()
    shader.bind()
    shader.uniform_float("ModelViewProjectionMatrix", mv)
    shader.uniform_float("footprint", 1.0 / max(depth_scale, 1e-3))
    shader.uniform_sampler("tex", texture)
    batch.draw()


def draw_box(x1, x2, y1, y2):
    indices = ((0, 1, 2), (2, 1, 3))
    color = [0, 0, 0, 0.5]

    vertices = ((x1, y1), (x2, y1), (x1, y2), (x2, y2))
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    batch = batch_for_shader(shader,
                             'TRIS', {"pos": vertices},
                             indices=indices)
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


def draw_gpu_buffer(context, depth_buffer):
    gpu.state.depth_mask_set(False)

    pref = get_pref()
    depth_scale = pref.depth_scale if pref is not None else 0.3
    if "draw_error" not in depth_buffer:
        with gpu.matrix.push_pop():
            gpu.matrix.scale([2, 2])
            gpu.matrix.translate([-0.5, -0.5, 0])
            gpu.matrix.translate(depth_buffer["translate"])
            gpu.matrix.scale([depth_scale, depth_scale])
            try:
                draw_shader_old(
                    context,
                    context.region.width,
                    context.region.height,
                    depth_scale,
                )
            except Exception as e:
                pref = get_pref()
                if pref is not None and pref.debug:
                    import traceback
                    traceback.print_exc()
                    traceback.print_stack()
                return e.args
    else:
        error_text = depth_buffer["draw_error"]
        draw_box(*depth_buffer["draw_box"])
        x, y = depth_buffer["text_location"]
        font_id = 0
        blf.position(font_id, x, y, 0)
        blf.draw(font_id, str(error_text))
        blf.position(font_id, x, y + 20, 0)
        blf.draw(font_id, "Drag Depth Map Error")


def clear_gpu_cache():
    _silhouette_cache.clear()
