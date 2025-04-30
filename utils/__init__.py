import bpy
from mathutils import Vector

from .. import __package__ as base_name


def get_pref():
    """获取偏好设置"""
    return bpy.context.preferences.addons[base_name].preferences


def get_toolbar_width(region_type="TOOLS"):
    """
    enum in ["WINDOW", "HEADER", "CHANNELS", "TEMPORARY", "UI", "TOOLS", "TOOL_PROPS",
        "PREVIEW", "HUD", "NAVIGATION_BAR", "EXECUTE", "FOOTER", "TOOL_HEADER", "XR"]
    """
    for i in bpy.context.area.regions:
        if i.type == region_type:
            if region_type == "TOOLS":
                return i.width
            elif region_type == "HEADER":
                return i.height


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


def check_mouse_in_3d_area(context, event) -> bool:
    """检查鼠标是否在3D Area"""
    if area := find_mouse_in_area(context, event):
        return area.type == "VIEW_3D"
    return False


def check_operator(operator: str) -> bool:
    """检查操作符是否注册"""
    return operator in all_operator_listen()


def check_mouse_in_modal(context, event) -> bool:
    """检查鼠标是否在模型上
    使用gpu深度图快速测式
    """
    from .gpu import get_mouse_location_ray_cast
    return get_mouse_location_ray_cast(context, event)


def check_brush_is_annotate(brush_name: str) -> bool:
    """检查笔刷是否为注释"""
    return brush_name in ('builtin.annotate',
                          'builtin.annotate_line',
                          'builtin.annotate_polygon',
                          'builtin.annotate_eraser')


def is_bbruse_mode() -> bool:
    """检查是否在BBrush模式"""
    from ..sculpt import brush_runtime
    return brush_runtime is not None


def refresh_ui(context):
    """刷新UI"""
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


def clear_cache():
    """清理缓存"""
    ...
