import bpy

from .click import BrushClick
from .depth import BrushDepthScale, BrushDepthMove
from .drag import BrushDrag
from .smooth import BrushSmooth

# 通过行为来区分手势内容
brush = [
    BrushDepthScale,
    BrushDepthMove,
    BrushDrag,
    BrushClick,
    BrushSmooth,
]

register_class, unregister_class = bpy.utils.register_classes_factory(brush)


def register():
    register_class()


def unregister():
    unregister_class()
