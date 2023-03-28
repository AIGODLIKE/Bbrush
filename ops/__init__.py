import bpy
from .brush_mask import BBrushMask
from .brush_sculpt import BBrushSculpt
from .brush_switch import BBrushSwitch

class_tuple = (BBrushMask,
               BBrushSculpt,
               BBrushSwitch,)

register_class, unregister_class = bpy.utils.register_classes_factory(class_tuple)


def register():
    register_class()


def unregister():
    unregister_class()
