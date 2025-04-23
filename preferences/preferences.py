import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty
from bpy_types import AddonPreferences

from .utils import key
from .utils.public import PublicClass


class BBrushAddonPreferences(AddonPreferences, PublicClass):
    bl_idname = __package__


def register():
    bpy.utils.register_class(BBrushAddonPreferences)


def unregister():
    bpy.utils.unregister_class(BBrushAddonPreferences)
    key.unregister()
