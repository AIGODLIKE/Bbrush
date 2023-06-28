from . import preferences, update, bbrush_toolbar
from .bbrush_toolbar import BrushTool
from .. import ops, ui
from .public import register_submodule_factory, PublicClass

model_tuple = (
    ui,
    ops,
    update,
    preferences,
    bbrush_toolbar,
)

register_module, unregister_module = register_submodule_factory(model_tuple)


def register():
    register_module()
    PublicClass.cache_clear()
    PublicClass.pref_().sculpt = False


def unregister():
    BrushTool.toolbar_switch('ORIGINAL_TOOLBAR')
    unregister_module()
    PublicClass.cache_clear()
