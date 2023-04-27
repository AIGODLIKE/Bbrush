from ..utils.public import register_submodule_factory
from . import draw_depth, replace_ui, draw_shortcut_keys

module_tuple = (draw_depth,
                draw_shortcut_keys,
                replace_ui)

register_module, unregister_module = register_submodule_factory(module_tuple)


def register():
    register_module()


def unregister():
    unregister_module()
