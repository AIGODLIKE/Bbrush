from ..utils.utils import register_submodule_factory,PublicClass
from . import draw_depth, replace_ui

module_tuple = (draw_depth,
                replace_ui)

register_module, unregister_module = register_submodule_factory(module_tuple)


def register():
    register_module()


def unregister():
    unregister_module()
