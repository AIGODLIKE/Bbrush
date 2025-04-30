import bpy

from .click import BrushClick
from .drag import BrushDrag
from .smooth import BrushSmooth

brush = [
    BrushDrag,
    BrushClick,
    BrushSmooth,
]

register_class, unregister_class = bpy.utils.register_classes_factory(brush)


def register():
    register_class()


def unregister():
    unregister_class()
