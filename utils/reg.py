import bpy

from . import preferences, update
from .public import register_submodule_factory, PublicClass
from .. import ops, ui
from brush import bbrush_toolbar
from brush.bbrush_toolbar import BrushTool

model_tuple = (
    ui,
    ops,
    update,
    preferences,
    bbrush_toolbar,
)

register_module, unregister_module = register_submodule_factory(model_tuple)


def update_sculpt():
    PublicClass.pref_().sculpt = False


def register():
    register_module()
    PublicClass.cache_clear()
    bpy.app.timers.register(update_sculpt, first_interval=2)


def unregister():
    unregister_module()
    PublicClass.cache_clear()
