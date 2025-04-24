import bpy

from .gpu_buffer import draw_gpu_buffer
from ..utils import get_pref, get_toolbar_width, is_bbruse_mode

handel = None

depth_buffer_check = {}


def check_is_draw(context):
    pref = get_pref()
    mode = pref.depth_display_mode
    is_sculpt = context.mode == "SCULPT"
    always = mode == "ALWAYS_DISPLAY"
    only_sculpt = (mode == "ONLY_SCULPT") and is_sculpt
    only_bbrush = (mode == "ONLY_BBRUSH") and is_sculpt and is_bbruse_mode()
    return always or only_sculpt or only_bbrush


def draw_depth():
    global depth_buffer_check

    pref = get_pref()
    context = bpy.context

    if check_is_draw(context):
        depth_scale = pref.depth_scale
        width = context.region.width
        height = context.region.height

        toolbar_width = get_toolbar_width() + pref.depth_offset_x
        header_height = get_toolbar_width("HEADER") + pref.depth_offset_y
        x1 = toolbar_width
        y1 = height - header_height
        x2 = int(width / 2 * depth_scale) + toolbar_width
        y2 = height - int(height / 2 * depth_scale) - header_height
        # 添加坐标 存起来笔刷的操作符判断鼠标有没有放在深度图上使用

        depth_buffer_check["wh"] = ((x1, x2), (y1, y2))

        w = 1 / width * toolbar_width * 2
        h = 1 / height * header_height * 2
        depth_buffer_check["translate"] = (w, -h, 0)
        draw_gpu_buffer(context, depth_buffer_check)

        """
        draw_gpu_buffer_new_buffer_funcs(sam_width, sam_height, width, height, sampling)
        """
    elif depth_buffer_check:
        depth_buffer_check = {}


def register():
    global handel
    handel = bpy.types.SpaceView3D.draw_handler_add(draw_depth, (), "WINDOW", "POST_PIXEL")


def unregister():
    global handel
    if handel:
        bpy.types.SpaceView3D.draw_handler_remove(handel, "WINDOW")
        handel = None
