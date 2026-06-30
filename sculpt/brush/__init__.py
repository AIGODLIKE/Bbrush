import bpy

from .click import BrushClick
from .depth import BrushDepthScale, BrushDepthMove
from .shape import BrushShape
from .shortcut_key import BrushShortcutKeyMove, BrushShortcutKeyScale

# Distinguish gestures by brush behavior
brush = [
    BrushShape,
    BrushClick,

    BrushDepthScale,
    BrushDepthMove,

    BrushShortcutKeyMove,
    BrushShortcutKeyScale,
]

register_class, unregister_class = bpy.utils.register_classes_factory(brush)


def register():
    register_class()


def unregister():
    unregister_class()
