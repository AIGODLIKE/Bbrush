import time

import bpy
from mathutils import Vector

from .gpu_buffer import draw_gpu_buffer, clear_gpu_cache
from ..utils import get_pref, is_bbruse_mode, get_region_height, get_region_width, refresh_ui,check_display_mode_is_draw

handel = None

depth_buffer_check = {
    # "wh": ((x1, x2), (y1, y2)),
    # "translate":w, -h, 0
    # "draw_error": "ERROR INFO"
}


def check_depth_map_is_draw(context):
    """检查深度图是否需要绘制"""
    pref = get_pref()
    mode = pref.depth_display_mode
    return check_display_mode_is_draw(context,mode)


def draw_depth():
    global depth_buffer_check
    context = bpy.context

    try:
        from ..sculpt import brush_runtime
        from ..sculpt.shortcut_key import ShortcutKey
        if is_bbruse_mode():
            ShortcutKey.draw_shortcut_key()
    except ReferenceError as e:
        from ..sculpt import BbrushExit
        BbrushExit.exit(context)

        import traceback
        traceback.print_exc()
        traceback.print_stack()
        print(e.args)

    if check_depth_map_is_draw(context):
        filling_data(context)

        if draw_error := draw_gpu_buffer(context, depth_buffer_check):
            depth_buffer_check["draw_error"] = draw_error
        """
        draw_gpu_buffer_new_buffer_funcs(sam_width, sam_height, width, height, sampling)
        """
    elif depth_buffer_check:
        depth_buffer_check = {}


def filling_data(context):
    global depth_buffer_check
    pref = get_pref()
    depth_scale = pref.depth_scale

    width = context.region.width
    height = context.region.height
    draw_width = int(width * depth_scale)
    draw_height = int(height * depth_scale)
    draw_size = Vector((draw_width, draw_height))

    depth_offset = Vector(pref.depth_offset)

    header_height = get_region_height(context, "HEADER") + get_region_height(context, "TOOL_HEADER")
    tools_width = get_region_width(context, "TOOLS")

    area_offset = Vector((tools_width, -header_height))

    location = depth_offset + area_offset + Vector((0, height - draw_height))

    # 限制位置
    ui_width = get_region_width(context, "UI")
    asset_shelf_height = get_region_height(context, "ASSET_SHELF") + get_region_height(context, "ASSET_SHELF_HEADER")
    limit_x = max(tools_width, min(width - ui_width - draw_width, location.x))
    limit_y = max(asset_shelf_height, min(height - header_height - draw_height, location.y))
    limitation = Vector((limit_x, limit_y))

    x1, y1 = limitation
    x2, y2 = limitation + draw_size

    # 添加坐标 存起来笔刷的操作符判断鼠标有没有放在深度图上使用
    depth_buffer_check["area_points"] = (x1, x2), (y1, y2)
    depth_buffer_check["draw_box"] = x1, x2, y1, y2
    depth_buffer_check["text_location"] = x1, y1

    # 修改为符合gpu绘制的坐标
    w = 1 / width * x1
    h = 1 / height * (y1 + draw_height)
    depth_buffer_check["translate"] = w, h, 0


update_depth_map_modal_operators_len = 0  # 更新深度图用


def update_depth_map_by_modal_operators() -> bool:
    """在移动缩放这些操作符会向场景的modal_operators添加操作符运行时
    用这个来进行判断并刷新"""
    global update_depth_map_modal_operators_len
    modal_operators_len = len(bpy.context.window.modal_operators)
    if update_depth_map_modal_operators_len != modal_operators_len:
        if modal_operators_len == 0:
            update_depth_map_modal_operators_len = modal_operators_len
            return True

    return False


update_depth_map_region_matrix = {}


def update_depth_map_by_matrix() -> bool:
    """用每个窗口的矩阵来判断"""
    global update_depth_map_modal_operators_len, update_depth_map_region_matrix
    print("update_depth_map_region_matrix", update_depth_map_region_matrix)

    # update_depth_map_region_matrix.clear()

    return False


def register():
    global handel
    handel = bpy.types.SpaceView3D.draw_handler_add(draw_depth, (), "WINDOW", "POST_PIXEL")


def unregister():
    global handel
    if handel:
        bpy.types.SpaceView3D.draw_handler_remove(handel, "WINDOW")
        handel = None
