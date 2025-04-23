from . import depth_map, preferences
from .utils import register_submodule_factory

model_tuple = (
    depth_map,
    preferences,
)

register_module, unregister_module = register_submodule_factory(model_tuple)


def register():
    register_module()


def unregister():
    unregister_module()
