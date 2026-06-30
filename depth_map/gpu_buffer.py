from functools import cache

import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from ..utils import get_pref
from ..utils.gpu import apply_gpu_texture_filter
from ..adapter import is_5_0_up_version

# White background, black silhouette. Slight smoothstep for edge softening when GPU linear-filters.
_SILHOUETTE_FRAG_BODY = """
    float depth = texture(tex, texCoord).x;
    float silhouette = smoothstep(0.9995, 1.0, depth);
    FragColor = vec4(silhouette, silhouette, silhouette, 1.0);
"""

_silhouette_cache = {
    "key": None,
    "texture": None,
}


def _silhouette_cache_key(context, width, height):
    rv3d = context.space_data.region_3d
    view_matrix = rv3d.view_matrix
    return (
        width,
        height,
        tuple(round(v, 5) for row in view_matrix for v in row),
        len(bpy.context.window.modal_operators),
    )


def get_coord(st=(-1, -1), interval=(2, 2)):
    """输入一个起始坐标,反回一个坐标列表,三角面连接顺序是(0, 1, 2), (0, 2, 3)"""
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
            in vec2 texCoord;
            out vec4 FragColor;

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


def _read_silhouette_texture(context, width, height):
    global _silhouette_cache
    key = _silhouette_cache_key(context, width, height)
    if _silhouette_cache["key"] == key and _silhouette_cache["texture"] is not None:
        return _silhouette_cache["texture"]

    depth_buffer = gpu.state.active_framebuffer_get().read_depth(0, 0, width, height)
    texture = gpu.types.GPUTexture((width, height), format="DEPTH_COMPONENT32F", data=depth_buffer)
    apply_gpu_texture_filter(texture)

    _silhouette_cache["key"] = key
    _silhouette_cache["texture"] = texture
    return texture


def draw_shader_old(context, width, height):
    shader, batch = depth_shader()
    texture = _read_silhouette_texture(context, width, height)

    mv = gpu.matrix.get_model_view_matrix()
    shader.uniform_float("ModelViewProjectionMatrix", mv)
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

    depth_scale = get_pref().depth_scale
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
                )
            except Exception as e:
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
    global _silhouette_cache
    _silhouette_cache["key"] = None
    _silhouette_cache["texture"] = None
