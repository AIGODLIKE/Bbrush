import bpy

from .click import BrushClick
from .hide import BrushHide
from .mask import BrushMask
from .sculpt import BrushSculpt

brush = [
    BrushMask,
    BrushSculpt,
    BrushClick,
    BrushHide,
]
register_class, unregister_class = bpy.utils.register_classes_factory(brush)


def register():
    register_class()


def unregister():
    unregister_class()
