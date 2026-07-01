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


def needs_viewport_overlay(context=None) -> bool:
    """Return True when the viewport draw handler should be active."""
    if not check_pref():
        return False
    pref = get_pref()
    if pref is None:
        return False
    context = context or bpy.context
    if is_bbruse_mode():
        if pref.show_shortcut_keys:
            return True
        return check_depth_map_is_draw(context)
    return check_depth_map_is_draw(context)


def refresh_draw_handler(context=None):
    """Register or remove the viewport draw handler based on current needs."""
    global handel
    if needs_viewport_overlay(context):
        if handel is None:
            handel = bpy.types.SpaceView3D.draw_handler_add(draw_depth, (), "WINDOW", "POST_PIXEL")
    elif handel is not None:
        bpy.types.SpaceView3D.draw_handler_remove(handel, "WINDOW")
        handel = None


def remove_draw_handler():
    """Remove the viewport draw handler if registered."""
    global handel, depth_buffer_check
    if handel is not None:
        bpy.types.SpaceView3D.draw_handler_remove(handel, "WINDOW")
        handel = None
    depth_buffer_check = {}


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
    elif depth_buffer_check:
        depth_buffer_check = {}

    if DEBUG_DEPTH_MAP:
        print("draw_depth time:", time.time() - start_time)


def filling_data(context):
    global depth_buffer_check
    pref = get_pref()
    if pref is None:
        return
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
    pass


def unregister():
    remove_draw_handler()
    clear_gpu_cache()

