import blf
import bpy
import gpu
import numpy as np
from gpu_extras.batch import batch_for_shader

# 区域内「非背景」深度像素占比 ≥ 此值（0–1）时判定为命中几何体。
# Blender 5.1+ 栅格会写入深度缓冲，不宜再用单点 min 深度判断。
DEPTH_CONTENT_RATIO_THRESHOLD = 0.08


def _depth_content_ratio(numpy_buffer, *, near_eps=1e-5, far_eps=1e-4):
    """返回扁平深度数组中视为有几何深度的像素比例（0–1）。"""
    d = np.asarray(numpy_buffer, dtype=np.float32).ravel()
    if d.size == 0:
        return 0.0
    valid = (d > near_eps) & (d < (1.0 - far_eps))
    return float(np.mean(valid))


def _depth_buffer_indicates_model(numpy_buffer):
    cr = _depth_content_ratio(numpy_buffer)
    print("check depth_content_ratio", cr)
    return cr >= DEPTH_CONTENT_RATIO_THRESHOLD


def get_gpu_buffer(xy, wh=(1, 1), centered=False):
    """ 用于获取当前视图的GPU BUFFER
    :params xy: 获取的左下角坐标,带X 和Y信息
    :type xy: list or set or tuple
    :params wh: 获取的宽度和高度信息
    :type wh: list or set or tuple
    :params centered: 是否按中心获取BUFFER
    :type centered: bool
    :return bpy.gpu.Buffer: 返回活动的GPU BUFFER
    """

    if isinstance(wh, (int, float)):
        wh = (wh, wh)
    elif len(wh) < 2:
        wh = (wh[0], wh[0])

    x, y, w, h = int(xy[0]), int(xy[1]), int(wh[0]), int(wh[1])
    if centered:
        x -= w // 2
        y -= h // 2

    depth_buffer = gpu.state.active_framebuffer_get().read_depth(x, y, w, h)
    return depth_buffer


def gpu_depth_ray_cast(x, y, data):
    """按区域内有效深度像素占比判断是否命中模型（见 DEPTH_CONTENT_RATIO_THRESHOLD）。"""
    from . import get_pref
    size = get_pref().depth_ray_size
    _buffer = get_gpu_buffer((x, y), wh=(size, size), centered=True)
    numpy_buffer = np.asarray(_buffer, dtype=np.float32).ravel()
    data['is_in_model'] = _depth_buffer_indicates_model(numpy_buffer)


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

    if w == 0 or h == 0:  # 没有绘制一个正确的区域
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
