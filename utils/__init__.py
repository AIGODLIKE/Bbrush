import os
from functools import cache

import bpy
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d
from mathutils import Vector

from .line_to_convex_shell import line_to_convex_shell
from .. import __package__ as base_name

DISPLAY_ITEMS = (
    ("ALWAYS_DISPLAY", "Always display",
     "Keep the silhouette displayed all the time, even when not in sculpting mode"),
    ("ONLY_SCULPT", "Only Sculpt", "Display silhouette images only in sculpting mode"),
    ("ONLY_BBRUSH", "Only Bbrush", "Display silhouette images only in Bbrush mode"),
    ("NOT_DISPLAY", "Not Display", "Never display silhouette images at any time"),
)


def get_context_mode(context=None):
    """Return object mode string, or None when context is restricted (e.g. during register)."""
    context = context or bpy.context
    mode = getattr(context, "mode", None)
    if mode is not None:
        return mode
    obj = getattr(context, "object", None)
    if obj is not None:
        return getattr(obj, "mode", None)
    return None


def check_display_mode_is_draw(context, display_mode: str) -> bool:
    if display_mode == "ALWAYS_DISPLAY":
        return True
    mode = get_context_mode(context)
    if mode is None:
        return False
    is_sculpt = mode == "SCULPT"
    only_sculpt = (display_mode == "ONLY_SCULPT") and is_sculpt
    only_bbrush = (display_mode == "ONLY_BBRUSH") and is_sculpt and is_bbruse_mode()
    return only_sculpt or only_bbrush


def check_pref() -> bool:
    addon = bpy.context.preferences.addons.get(base_name)
    return addon is not None and addon.preferences is not None


def get_pref():
    """Return addon preferences."""
    addon = bpy.context.preferences.addons.get(base_name)
    if addon is None:
        return None
    return addon.preferences


def get_region(region_type, context=None) -> "None|bpy.types.Region":
    """
    enum in ["WINDOW", "HEADER", "CHANNELS", "TEMPORARY", "UI", "TOOLS", "TOOL_PROPS",
        "PREVIEW", "HUD", "NAVIGATION_BAR", "EXECUTE", "FOOTER", "TOOL_HEADER", "XR"]]
    region_types = set(region.type for area in bpy.context.screen.areas for region in area.regions)
    {
    'WINDOW',
     'ASSET_SHELF',
     'TOOL_HEADER',
     'ASSET_SHELF_HEADER',
     'HUD',
     'UI',
     'NAVIGATION_BAR',
     'TOOLS',
     'EXECUTE',
     'HEADER',
     'CHANNELS'
     }
    """
    area = bpy.context.area if context is None else context.area
    for region in area.regions:
        if region.type == region_type:
            return region
    return None


def get_toolbar_width(region_type="TOOLS"):
    for i in bpy.context.area.regions:
        if i.type == region_type:
            if region_type == "TOOLS":
                return i.width
            elif region_type in ("HEADER", "TOOL_HEADER"):
                return i.height
    return None


def get_region_height(context, region_type="TOOLS") -> int:
    if area := get_region(region_type, context):
        return area.height
    return 0


def get_region_width(context, region_type="TOOLS") -> int:
    if area := get_region(region_type, context):
        return area.width
    return 0


def get_active_tool(context) -> "(bpy.types.Tool, bpy.types.WorkSpaceTool, int)":
    return ToolSelectPanelHelper._tool_class_from_space_type("VIEW_3D")._tool_get_active(context, "VIEW_3D", "SCULPT")


def get_brush_shape(brush) -> str:
    """Map brush id to shape: ELLIPSE, BOX, POLYLINE, LASSO, CIRCULAR."""
    if brush in (
            "builtin_brush.mask",
            "builtin.box_mask",
            "builtin.box_hide",
            "builtin.box_trim",
    ):
        return "BOX"
    elif brush in (
            "builtin.polyline_mask",
            "builtin.polyline_hide",
            "builtin.polyline_trim",
            "builtin.line_mask",
    ):
        return "POLYLINE"
    elif brush in (
            "builtin.ellipse_hide",
            "builtin.ellipse_mask",
    ):
        return "ELLIPSE"
    elif brush in (
            "builtin.circular_mask",
            "builtin.circular_hide",
    ):
        return "CIRCULAR"
    elif brush in (
            "builtin.lasso_mask",
            "builtin.lasso_hide",
            "builtin.lasso_trim",
    ):
        return "LASSO"
    pref = get_pref()
    if pref is not None and pref.debug:
        print("brush not match shape", brush)
    return "NONE"


def register_submodule_factory(submodule_tuple):
    """Register/unregister factory for submodule tuples."""

    def register():
        for mod in submodule_tuple:
            mod.register()

    def unregister():
        for mod in reversed(submodule_tuple):
            mod.unregister()

    return register, unregister


def all_operator_listen() -> list[str]:
    """Return all registered operator idnames."""
    from _bpy import ops
    submodules = set()
    for id_name in ops.dir():
        id_split = id_name.split("_OT_", 1)
        if len(id_split) == 2:
            submodules.add(id_split[0].lower() + '.' + id_split[1])
    return list(submodules)


def mouse_in_area_point_in(event, area_point):
    """Return True if event mouse position is inside area_point bounds.

    Args:
        event: Operator event.
        area_point: ((x_min, x_max), (y_min, y_max)).
    """
    x = area_point[0]
    y = area_point[1]
    mou_x, mou_y = event.mouse_region_x, event.mouse_region_y
    x_in = min(x) < mou_x < max(x)
    y_in = min(y) < mou_y < max(y)
    return x_in and y_in


def find_mouse_in_area(context, event) -> "bpy.types.Area|None":
    """Return the screen area under the mouse cursor."""
    mouse = Vector((event.mouse_x, event.mouse_y)).freeze()
    for area in context.screen.areas:
        xy = Vector((area.x, area.y)).freeze()
        aw = xy + Vector((area.width, area.height)).freeze()
        if xy.x < mouse.x < aw.x and xy.y < mouse.y < aw.y:
            return area
    return None


def check_mouse_in_3d_area(context, event) -> bool:
    """Return True if the mouse is over a 3D View area."""
    if area := find_mouse_in_area(context, event):
        return area.type == "VIEW_3D"
    return False


def check_operator(operator: str) -> bool:
    """Return True if the operator idname is registered."""
    return operator in all_operator_listen()


def check_mouse_in_model(context, event) -> bool:
    """Return True if the mouse hits model geometry (GPU depth ray cast)."""
    from .gpu import get_mouse_location_ray_cast
    x, y = (event.mouse_region_x, event.mouse_region_y)
    return get_mouse_location_ray_cast(context, x, y)


def check_area_in_model(context, x, y, w, h) -> bool:
    """Return True if the rectangular region hits model geometry."""
    from .gpu import get_area_ray_cast
    return get_area_ray_cast(context, x, y, w, h)


def check_brush_is_annotate(brush_name: str) -> bool:
    """Return True if brush_name is an annotate tool."""
    return brush_name in ('builtin.annotate',
                          'builtin.annotate_line',
                          'builtin.annotate_polygon',
                          'builtin.annotate_eraser')


def check_mouse_in_depth_map_area(event) -> bool:
    """Return True if the mouse is over the depth map widget."""
    from ..depth_map import depth_buffer_check
    return ("area_points" in depth_buffer_check) and mouse_in_area_point_in(event, depth_buffer_check["area_points"])


def check_mouse_in_shortcut_key_area(event) -> bool:
    """Return True if the mouse is over the shortcut key overlay."""
    from ..sculpt import brush_runtime
    return (
            brush_runtime and
            brush_runtime.shortcut_key_points and
            mouse_in_area_point_in(event, brush_runtime.shortcut_key_points)
    )


def check_modal_operators(bl_idname: str) -> bool:
    """Return True if a modal operator with bl_idname is running."""
    for modal in bpy.context.window.modal_operators:
        if modal and modal.bl_idname == bl_idname:
            return True
    return False


def is_bbruse_mode() -> bool:
    """Return True when Bbrush sculpt runtime is active."""
    from ..sculpt import brush_runtime
    return brush_runtime is not None


def refresh_ui(context):
    """Tag view3d UI regions for redraw."""
    if context.area:
        context.area.tag_redraw()
    if context.region:
        context.region.tag_redraw()
    if context.screen:
        context.screen.update_tag()
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                for region in area.regions:
                    region.tag_redraw()


def get_property_rna_info(bl_rna, property_name: "str") -> "dict|None":
    """Return RNA metadata dict for a property on bl_rna."""
    if property_name in bl_rna.properties:
        prop = bl_rna.properties[property_name]

        data = {
            "name": prop.name,
            "description": prop.description,
        }

        # if prop.type == 'POINTER':
        #     pro = get_property(pro, exclude, reversal)
        # elif typ == 'COLLECTION':
        #     pro = __collection_data__(pro, exclude, reversal)
        if prop.type == 'ENUM':
            data["items"] = list(((i.identifier, i.name, i.description) for i in prop.enum_items))
        elif prop.type == "FLOAT" or prop.subtype == "COLOR":
            for key_a, key_b in {
                "hard_max": "max",
                "hard_min": "min",
                "soft_min": "soft_min",
                "soft_max": "soft_max",
                "step": "step",
            }.items():
                if value := getattr(prop, key_a, None):
                    data[key_b] = value

        if default := getattr(prop, "default", None):
            data["default"] = default

        if options := getattr(prop, "options", None):
            data["options"] = options

        if subtype := getattr(prop, "subtype", None):
            if subtype != "NONE":
                data["subtype"] = subtype

        # print("get_property_rna_info", property_name, data)
        return data
    return None


@cache
def get_view_navigation_texture(h, w):
    from ..src import view_navigation
    key = (h, w)
    if len(view_navigation.texture_cache) == 40 and key in view_navigation.texture_cache:
        return view_navigation.texture_cache[key]
    else:
        folder = os.path.dirname(os.path.dirname(__file__))
        default_file_path = os.path.join(folder, "src", "view_navigation", "Default.png")
        view_navigation.load_view_navigation_image(default_file_path)
        # print(view_navigation.texture_cache.keys())
        return view_navigation.texture_cache[key]


def clear_view_navigation_texture_cache():
    get_view_navigation_texture.cache_clear()


def object_ray_cast(obj, context, mouse):
    region = context.region
    region_data = context.region_data
    depsgraph = context.evaluated_depsgraph_get()

    mx = obj.matrix_world
    mxi = mx.inverted_safe()

    origin_3d = region_2d_to_origin_3d(region, region_data, mouse)
    direction_3d = region_2d_to_vector_3d(region, region_data, mouse)

    ray_origin = mxi @ origin_3d
    ray_direction = mxi.to_3x3() @ direction_3d

    return obj.ray_cast(depsgraph=depsgraph, origin=ray_origin, direction=ray_direction)
