import time

import bpy
from mathutils import Vector

from .gpu_buffer import draw_gpu_buffer, clear_gpu_cache
from ..debug import DEBUG_DEPTH_MAP
from ..utils import check_pref, get_pref, is_bbruse_mode, get_region_height, get_region_width, check_display_mode_is_draw

handel = None

depth_buffer_check = {
    # "wh": ((x1, x2), (y1, y2)),
    # "translate":w, -h, 0
    # "draw_error": "ERROR INFO"
}


def check_depth_map_is_draw(context):
    """Return True when the depth map overlay should draw."""
    if not check_pref():
        return False
    pref = get_pref()
    if pref is None:
        return False
    mode = pref.depth_display_mode
    return check_display_mode_is_draw(context, mode)


def draw_depth():
    if not check_pref():
        return
    pref = get_pref()
    if pref is None:
        return
    if DEBUG_DEPTH_MAP:
        start_time = time.time()
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
        if pref.debug:
            import traceback
            traceback.print_exc()
            traceback.print_stack()
            print(e.args)

    if check_depth_map_is_draw(context):
        filling_data(context)

        if draw_error := draw_gpu_buffer(context, depth_buffer_check):
            depth_buffer_check["draw_error"] = draw_error
            if pref.debug:
                print(draw_error)
        """
        draw_gpu_buffer_new_buffer_funcs(sam_width, sam_height, width, height, sampling)
        """
    elif depth_buffer_check:
        depth_buffer_check = {}

    if DEBUG_DEPTH_MAP:
        print("draw_depth time:", time.time() - start_time)


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

    # Clamp widget position inside the region
    ui_width = get_region_width(context, "UI")
    asset_shelf_height = get_region_height(context, "ASSET_SHELF") + get_region_height(context, "ASSET_SHELF_HEADER")
    limit_x = max(tools_width, min(width - ui_width - draw_width, location.x))
    limit_y = max(asset_shelf_height, min(height - header_height - draw_height, location.y))
    limitation = Vector((limit_x, limit_y))

    x1, y1 = limitation
    x2, y2 = limitation + draw_size

    # Store bounds for depth-map hit testing in brush operators
    depth_buffer_check["area_points"] = (x1, x2), (y1, y2)
    depth_buffer_check["draw_box"] = x1, x2, y1, y2
    depth_buffer_check["text_location"] = x1, y1

    # Normalized coords for GPU matrix placement
    w = 1 / width * x1
    h = 1 / height * (y1 + draw_height)
    depth_buffer_check["translate"] = w, h, 0


update_depth_map_modal_operators_len = 0  # Tracks modal operator count for depth refresh


def update_depth_map_by_modal_operators() -> bool:
    """Return True when view navigation modal operators finish (pan/zoom/rotate)."""
    global update_depth_map_modal_operators_len
    modal_operators_len = len(bpy.context.window.modal_operators)
    if update_depth_map_modal_operators_len != modal_operators_len:
        if modal_operators_len == 0:
            update_depth_map_modal_operators_len = modal_operators_len
            return True

    return False


def register():
    global handel
    handel = bpy.types.SpaceView3D.draw_handler_add(draw_depth, (), "WINDOW", "POST_PIXEL")


def unregister():
    global handel
    if handel:
        bpy.types.SpaceView3D.draw_handler_remove(handel, "WINDOW")
        handel = None
