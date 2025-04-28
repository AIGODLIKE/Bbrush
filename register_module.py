import bpy

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


def update_bbrush_mode():
    """
    在切换模式的时候
    在启动Blender的时候
    """
    sculpt.BbrushSculpt.toggle_object_mode()


def register():
    register_module()

    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, 'mode'),
        owner=owner,
        args=(),
        notify=update_bbrush_mode,
    )

    bpy.app.timers.register(update_bbrush_mode, first_interval=0.1, persistent=True)


def unregister():
    unregister_module()

    bpy.msgbus.clear_by_owner(owner)

    if bpy.app.timers.is_registered(update_bbrush_mode):
        bpy.app.timers.unregister(update_bbrush_mode)
