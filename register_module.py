from . import depth_map, preferences, topbar, sculpt
from .utils import register_submodule_factory

model_tuple = (
    topbar,
    sculpt,
    depth_map,
    preferences,
)

register_module, unregister_module = register_submodule_factory(model_tuple)

owner = object()


def object_mode_toggle():
    """在切换模式的时候进行判断"""
    sculpt.BbrushSculpt.toggle_object_mode()


def register():
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, 'mode'),
        owner=owner,
        args=(),
        notify=object_mode_toggle,
    )

    register_module()


def unregister():
    unregister_module()
    bpy.msgbus.clear_by_owner(owner)
