import bpy

from .. import __package__ as base_name


def get_pref():
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


def check_operator(operator: str) -> bool:
    return operator in all_operator_listen()


def is_bbruse_mode() -> bool:
    from ..sculpt import brush_runtime
    return brush_runtime is not None


def clear_cache():
    # is_bbruse_mode.cache_clear()
    ...
