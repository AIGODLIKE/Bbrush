import blf
import bpy
import gpu
import numpy as np
from gpu_extras.batch import batch_for_shader

# Hit geometry when non-background depth pixel ratio in the region is >= this value (0-1).
# Blender 5.1+ raster writes depth buffers; single-point min depth is unreliable.
DEPTH_CONTENT_RATIO_THRESHOLD = 0.08


def apply_gpu_texture_filter(gpu_tex) -> None:
    """Blender 5.1+ enable mipmap/linear filtering for smoother UI texture scaling."""
    try:
        if bpy.app.version < (5, 1):
            return
        gpu_tex.mipmap_mode(use_mipmap=True, use_filter=True)
        gpu_tex.anisotropic_filter(True)
    except Exception:
        return


def _depth_content_ratio(numpy_buffer, *, near_eps=1e-5, far_eps=1e-4):
    """Return ratio of flat depth samples considered geometry (0-1)."""
    d = np.asarray(numpy_buffer, dtype=np.float32).ravel()
    if d.size == 0:
        return 0.0
    valid = (d > near_eps) & (d < (1.0 - far_eps))
    return float(np.mean(valid))


def _depth_buffer_indicates_model(numpy_buffer):
    cr = _depth_content_ratio(numpy_buffer)
    return cr >= DEPTH_CONTENT_RATIO_THRESHOLD


def _clamp_read_rect(x, y, w, h):
    fb_w, fb_h = gpu.state.scissor_get()[2:]
    if fb_w <= 0 or fb_h <= 0:
        return 0, 0, 0, 0
    x = max(0, int(x))
    y = max(0, int(y))
    w = max(0, min(int(w), fb_w - x))
    h = max(0, min(int(h), fb_h - y))
    return x, y, w, h


def get_gpu_buffer(xy, wh=(1, 1), centered=False):
    """Read depth from the active viewport framebuffer.

    :param xy: Bottom-left corner (x, y).
    :param wh: Width and height of the read region.
    :param centered: When True, center the region on ``xy``.
    :return: Depth buffer from ``read_depth``.
    """

    if isinstance(wh, (int, float)):
        wh = (wh, wh)
    elif len(wh) < 2:
        wh = (wh[0], wh[0])

    x, y, w, h = int(xy[0]), int(xy[1]), int(wh[0]), int(wh[1])
    if centered:
        x -= w // 2
        y -= h // 2

    x, y, w, h = _clamp_read_rect(x, y, w, h)
    if w <= 0 or h <= 0:
        return np.zeros(0, dtype=np.float32)

    depth_buffer = gpu.state.active_framebuffer_get().read_depth(x, y, w, h)
    return depth_buffer


def gpu_depth_ray_cast(x, y, data):
    """POST_PIXEL handler: hit test via depth pixel ratio (see DEPTH_CONTENT_RATIO_THRESHOLD)."""
    from . import get_pref
    pref = get_pref()
    if pref is None:
        data["is_in_model"] = False
        return
    size = pref.depth_ray_size
    try:
        _buffer = get_gpu_buffer((x, y), wh=(size, size), centered=True)
        numpy_buffer = np.asarray(_buffer, dtype=np.float32).ravel()
        data["is_in_model"] = _depth_buffer_indicates_model(numpy_buffer)
    except ValueError:
        data["is_in_model"] = False


def get_mouse_location_ray_cast(context, x, y):
    view3d = context.space_data
    show_xray = view3d.shading.show_xray
    view3d.shading.show_xray = False
    data = {}
    space = bpy.types.SpaceView3D
    handler = space.draw_handler_add(gpu_depth_ray_cast, (x, y, data), 'WINDOW', 'POST_PIXEL')
    bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)
    space.draw_handler_remove(handler, 'WINDOW')
    view3d.shading.show_xray = show_xray
    return data.get('is_in_model', False)


def get_area_ray_cast(context, x, y, w, h):
    data = {}

    if w == 0 or h == 0:  # Invalid draw region
        return get_mouse_location_ray_cast(context, x, y)

    def get_ray_cast():
        buffer = get_gpu_buffer((x, y), wh=(w, h), centered=False)
        numpy_buffer = np.asarray(buffer, dtype=np.float32).ravel()
        data['is_in_model'] = _depth_buffer_indicates_model(numpy_buffer)

    view3d = context.space_data
    show_xray = view3d.shading.show_xray
    view3d.shading.show_xray = False
    handler = bpy.types.SpaceView3D.draw_handler_add(get_ray_cast, (), 'WINDOW', 'POST_PIXEL')
    bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)
    bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
    view3d.shading.show_xray = show_xray
    return data.get('is_in_model', False)


def draw_text(x,
              y,
              text="Hello Word",
              font_id=0,
              size=10,
              *,
              color=(0.5, 0.5, 0.5, 1),
              column=0):
    blf.position(font_id, x, y - (size * (column + 1)), 0)
    blf.size(font_id, size)
    blf.color(font_id, *color)
    blf.draw(font_id, text)


def draw_line(vertices, color, line_width=1):
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.line_width_set(line_width)
    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": vertices})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)
    gpu.state.line_width_set(1)


def draw_smooth_line(vertices, color, line_width=1):
    colors = []
    indices = []
    for index, v in enumerate(vertices):
        colors.append(color)
        if index == len(vertices) - 1:
            indices.append((0, len(vertices) - 1))
        else:
            indices.append((index, index + 1))

    gpu.state.line_width_set(line_width)

    poly_line = gpu.shader.from_builtin("POLYLINE_SMOOTH_COLOR")
    poly_line.uniform_float("lineWidth", line_width)
    poly_line.uniform_float("viewportSize", gpu.state.scissor_get()[2:])
    poly_line.bind()

    batch = batch_for_shader(poly_line, "LINES", {"pos": vertices, "color": colors}, indices=indices)
    batch.draw(poly_line)
    gpu.state.line_width_set(1)
