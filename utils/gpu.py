import blf
import bpy
import gpu
import numpy as np
from gpu_extras.batch import batch_for_shader


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
    """获取深度图是否有不含0 1 的像素点"""
    from . import get_pref
    size = get_pref().depth_ray_size
    _buffer = get_gpu_buffer((x, y), wh=(size, size), centered=True)
    numpy_buffer = np.asarray(_buffer, dtype=np.float32).ravel()
    min_depth = np.min(numpy_buffer)
    data['is_in_model'] = (min_depth != (0 or 1))


def get_mouse_location_ray_cast(context, event):
    x, y = (event.mouse_region_x, event.mouse_region_y)
    view3d = context.space_data
    show_xray = view3d.shading.show_xray
    view3d.shading.show_xray = False
    data = {}
    space = bpy.types.SpaceView3D
    handler = space.draw_handler_add(gpu_depth_ray_cast, (x, y, data), 'WINDOW', 'POST_PIXEL')
    bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)
    space.draw_handler_remove(handler, 'WINDOW')
    view3d.shading.show_xray = show_xray
    return data['is_in_model']


def get_area_ray_cast(context, x, y, w, h):
    data = {}

    def get_ray_cast():
        buffer = get_gpu_buffer((x, y), wh=(w, h), centered=False)
        numpy_buffer = np.asarray(buffer, dtype=np.float32).ravel()
        min_depth = np.min(numpy_buffer)
        data['is_in_model'] = (min_depth != (0 or 1))

    view3d = context.space_data
    show_xray = view3d.shading.show_xray
    view3d.shading.show_xray = False
    handler = bpy.types.SpaceView3D.draw_handler_add(get_ray_cast, (), 'WINDOW', 'POST_PIXEL')
    bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)
    bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
    view3d.shading.show_xray = show_xray
    if 'is_in_model' in data:
        return data['is_in_model']
    return False


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
    gpu.state.line_width_set(1.0)
