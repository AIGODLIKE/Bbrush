import bpy
from bpy.app.handlers import persistent

from . import depth_map, preferences, topbar, sculpt, src
from .utils import register_submodule_factory, get_pref, is_bbruse_mode

model_tuple = (
    src,
    topbar,
    sculpt,
    depth_map,
    preferences,
)

register_module, unregister_module = register_submodule_factory(model_tuple)

owner = object()


def start_update_bbrush_mode():
    """在启动Blender的时候"""
    sculpt.try_toggle_bbrush_mode()


def object_mode_update_bbrush_mode():
    """在切换模式的时候"""
    sculpt.try_toggle_bbrush_mode()


def load_subscribe():
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, 'mode'),
        owner=owner,
        args=(),
        notify=object_mode_update_bbrush_mode,
        options={"PERSISTENT"}
    )


def refresh_subscribe():
    bpy.msgbus.clear_by_owner(owner)
    load_subscribe()


def bbrush_timer():
    pref = get_pref()

    if not is_bbruse_mode():
        sculpt.keymap.try_restore_keymap()
        sculpt.shortcut_key.try_setop_shortcut_key()
        sculpt.view_property.try_restore_view_property()
        sculpt.update_brush_shelf.try_restore_brush_shelf()

    return pref.refresh_interval


@persistent
def load_post(args):
    refresh_subscribe()
    sculpt.try_toggle_bbrush_mode()


@persistent
def depsgraph_update_post(a, b):
    ...


def register():
    register_module()

    load_subscribe()
    bpy.app.handlers.load_post.append(load_post)
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update_post)

    bpy.app.timers.register(start_update_bbrush_mode, first_interval=1, persistent=True)
    bpy.app.timers.register(bbrush_timer, first_interval=1, persistent=True)


def unregister():
    sculpt.BbrushExit.exit(bpy.context, True)

    bpy.msgbus.clear_by_owner(owner)

    if bpy.app.timers.is_registered(object_mode_update_bbrush_mode):
        bpy.app.timers.unregister(object_mode_update_bbrush_mode)
    if bpy.app.timers.is_registered(bbrush_timer):
        bpy.app.timers.unregister(bbrush_timer)
    bpy.app.handlers.load_post.remove(load_post)
    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update_post)

    unregister_module()
