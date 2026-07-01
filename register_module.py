import bpy
from bpy.app.handlers import persistent

from . import depth_map, preferences, topbar, sculpt, src, gizmo
from .src import view_navigation
from .utils import register_submodule_factory, get_pref, is_bbruse_mode, get_context_mode

model_tuple = (
    preferences,
    src,
    sculpt,
    depth_map,
    gizmo,
    topbar,
)

register_module, unregister_module = register_submodule_factory(model_tuple)

owner = object()
_auto_handlers_active = False
_mode_subscribed = False


def try_toggle_bbrush_mode(is_start=False):
    """Toggle Bbrush mode on sculpt enter/exit, Blender startup, or forced mode."""
    is_bbruse = is_bbruse_mode()
    mode = get_context_mode()

    if mode == "SCULPT":
        pref = get_pref()
        if pref is not None and pref.always_use_bbrush_sculpt_mode and not is_bbruse:
            bpy.ops.sculpt.bbrush_start("INVOKE_DEFAULT")
    elif is_bbruse:
        bpy.ops.sculpt.bbrush_exit("INVOKE_DEFAULT", exit_always=False)
    else:
        ...


def start_update_bbrush_mode():
    """Called when Blender starts."""
    try_toggle_bbrush_mode()
    view_navigation.register()
    depth_map.refresh_draw_handler()


def on_object_mode_change():
    depth_map.refresh_draw_handler()
    if _auto_handlers_active:
        try_toggle_bbrush_mode()


def ensure_mode_subscribe():
    global _mode_subscribed
    if _mode_subscribed:
        return
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, 'mode'),
        owner=owner,
        args=(),
        notify=on_object_mode_change,
        options={"PERSISTENT"},
    )
    _mode_subscribed = True


def enable_auto_mode_handlers():
    global _auto_handlers_active
    if _auto_handlers_active:
        return
    _auto_handlers_active = True
    if load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_post)
    if not bpy.app.timers.is_registered(start_update_bbrush_mode):
        bpy.app.timers.register(start_update_bbrush_mode, first_interval=1, persistent=True)


def disable_auto_mode_handlers():
    global _auto_handlers_active
    if not _auto_handlers_active:
        return
    _auto_handlers_active = False
    if load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_post)
    if bpy.app.timers.is_registered(start_update_bbrush_mode):
        bpy.app.timers.unregister(start_update_bbrush_mode)


def sync_auto_mode_handlers():
    pref = get_pref()
    if pref is not None and pref.always_use_bbrush_sculpt_mode:
        enable_auto_mode_handlers()
    else:
        disable_auto_mode_handlers()


@persistent
def load_post(args):
    try_toggle_bbrush_mode()
    depth_map.refresh_draw_handler()


def register():
    register_module()
    ensure_mode_subscribe()
    sync_auto_mode_handlers()
    depth_map.refresh_draw_handler()


def unregister():
    global _mode_subscribed
    disable_auto_mode_handlers()
    view_navigation.unregister()
    sculpt.BbrushExit.exit(bpy.context, True)

    bpy.msgbus.clear_by_owner(owner)
    _mode_subscribed = False

    depth_map.remove_draw_handler()
    unregister_module()
