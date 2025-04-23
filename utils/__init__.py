import bpy

from .. import __package__ as base_name


def get_pref():
    return bpy.context.preferences.addons[base_name].preferences


def get_toolbar_width(region_type="TOOLS"):
    """
    enum in ["WINDOW", "HEADER", "CHANNELS", "TEMPORARY", "UI", "TOOLS", "TOOL_PROPS",
        "PREVIEW", "HUD", "NAVIGATION_BAR", "EXECUTE", "FOOTER", "TOOL_HEADER", "XR"]
    rt = regions_type

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
