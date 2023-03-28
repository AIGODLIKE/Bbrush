from . import preferences, update, bbrush_toolbar
from .. import ops, ui
from .utils import register_submodule_factory, PublicClass

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


def unregister():
    unregister_module()
    PublicClass.cache_clear()
