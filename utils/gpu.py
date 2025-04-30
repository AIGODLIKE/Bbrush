import bpy
import gpu
import numpy as np


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
