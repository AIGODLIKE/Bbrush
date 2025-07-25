import os
from functools import cache

import bpy
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
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


def check_display_mode_is_draw(context, display_mode: str) -> bool:
    is_sculpt = context.mode == "SCULPT"
    always = display_mode == "ALWAYS_DISPLAY"
    only_sculpt = (display_mode == "ONLY_SCULPT") and is_sculpt
    only_bbrush = (display_mode == "ONLY_BBRUSH") and is_sculpt and is_bbruse_mode()
    return always or only_sculpt or only_bbrush


def check_pref() -> bool:
    return base_name in bpy.context.preferences.addons


def get_pref():
    """获取偏好设置"""
    return bpy.context.preferences.addons[base_name].preferences


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
    """通过笔刷id获取形状
    ELLIPSE,BOX,POLYLINE,LASSO,CIRCULAR
    """
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
    return "NONE"


def register_submodule_factory(submodule_tuple):
    """注册子模块"""

    def register():
        for mod in submodule_tuple:
            mod.register()

    def unregister():
        for mod in reversed(submodule_tuple):
            mod.unregister()

    return register, unregister


def all_operator_listen() -> list[str]:
    """反回所有操作符列表
    """
    from _bpy import ops
    submodules = set()
    for id_name in ops.dir():
        id_split = id_name.split("_OT_", 1)
        if len(id_split) == 2:
            submodules.add(id_split[0].lower() + '.' + id_split[1])
    return list(submodules)


def mouse_in_area_point_in(event, area_point):
    """输入一个event和xy的最大最小值,反回一个鼠标是否在此区域内的布尔值,如果在里面就反回True

    Args:
        event (bpy.types.Event): 输入操作符event
        area_point ((x,x),(y,y)): 输入x和y的坐标
    """
    x = area_point[0]
    y = area_point[1]
    mou_x, mou_y = event.mouse_region_x, event.mouse_region_y
    x_in = min(x) < mou_x < max(x)
    y_in = min(y) < mou_y < max(y)
    return x_in and y_in


def find_mouse_in_area(context, event) -> "bpy.types.Area|None":
    """查找在鼠标上的区域
    就是鼠标活动区域
    """
    mouse = Vector((event.mouse_x, event.mouse_y)).freeze()
    for area in context.screen.areas:
        xy = Vector((area.x, area.y)).freeze()
        aw = xy + Vector((area.width, area.height)).freeze()
        if xy.x < mouse.x < aw.x and xy.y < mouse.y < aw.y:
            return area
    return None


def check_mouse_in_3d_area(context, event) -> bool:
    """检查鼠标是否在3D Area"""
    if area := find_mouse_in_area(context, event):
        return area.type == "VIEW_3D"
    return False


def check_operator(operator: str) -> bool:
    """检查操作符是否注册"""
    return operator in all_operator_listen()


def check_mouse_in_model(context, event) -> bool:
    """检查鼠标是否在模型上
    使用gpu深度图快速测式
    """
    from .gpu import get_mouse_location_ray_cast
    return get_mouse_location_ray_cast(context, event)


def check_area_in_model(context, x, y, w, h) -> bool:
    """检查区域是否在模型上"""
    from .gpu import get_area_ray_cast
    return get_area_ray_cast(context, x, y, w, h)


def check_brush_is_annotate(brush_name: str) -> bool:
    """检查笔刷是否为注释"""
    return brush_name in ('builtin.annotate',
                          'builtin.annotate_line',
                          'builtin.annotate_polygon',
                          'builtin.annotate_eraser')


def check_mouse_in_depth_map_area(event) -> bool:
    """检查鼠标是否在深度图上"""
    from ..depth_map import depth_buffer_check
    return ("area_points" in depth_buffer_check) and mouse_in_area_point_in(event, depth_buffer_check["area_points"])


def check_mouse_in_shortcut_key_area(event) -> bool:
    """检查鼠标是否在快捷键上"""
    from ..sculpt import brush_runtime
    return (
            brush_runtime and
            brush_runtime.shortcut_key_points and
            mouse_in_area_point_in(event, brush_runtime.shortcut_key_points)
    )


def is_bbruse_mode() -> bool:
    """检查是否在BBrush模式"""
    from ..sculpt import brush_runtime
    return brush_runtime is not None


def refresh_ui(context):
    """刷新UI
    # bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)
    """
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
    """通过rna 获取属性的所有参数"""
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
