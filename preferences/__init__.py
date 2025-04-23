import bpy

from .depth_map import DepthMap
from .. import __name__ as base_name


class Preferences(
    bpy.types.AddonPreferences,
    DepthMap,
):
    bl_idname = base_name


def register():
    bpy.utils.register_class(Preferences)


def unregister():
    bpy.utils.unregister_class(Preferences)
