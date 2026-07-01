import bpy
from bpy.app.handlers import persistent

from . import depth_map, preferences, topbar, sculpt, src, gizmo
from .src import view_navigation
from .utils import register_submodule_factory, get_pref, is_bbrush_mode, get_context_mode

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
_load_post_draw_registered = False


def try_toggle_bbrush_mode(is_start=False):
    """Toggle Bbrush mode on sculpt enter/exit, Blender startup, or forced mode."""
    bbrush_active = is_bbrush_mode()
    mode = get_context_mode()

    if mode == "SCULPT":
        pref = get_pref()
        if pref is not None and pref.always_use_bbrush_sculpt_mode and not bbrush_active:
            bpy.ops.sculpt.bbrush_start("INVOKE_DEFAULT")
    elif bbrush_active:
        bpy.ops.sculpt.bbrush_exit("INVOKE_DEFAULT", exit_always=False)
    else:
        ...


def refresh_viewport_overlay():
    """Refresh draw handler and silhouette cache after file load or mode change."""
    depth_map.refresh_draw_handler()
    depth_map.clear_gpu_cache()


def start_update_bbrush_mode():
    """Called when Blender starts."""
    try_toggle_bbrush_mode()
    view_navigation.register()
    refresh_viewport_overlay()


def on_object_mode_change():
    refresh_viewport_overlay()
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


def ensure_load_post_draw():
    """Refresh silhouette draw handler whenever a .blend file finishes loading."""
    global _load_post_draw_registered
    if _load_post_draw_registered:
        return
    if load_post_draw not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_post_draw)
    _load_post_draw_registered = True


def enable_auto_mode_handlers():
    global _auto_handlers_active
    if _auto_handlers_active:
        return
    _auto_handlers_active = True
    if not bpy.app.timers.is_registered(start_update_bbrush_mode):
        bpy.app.timers.register(start_update_bbrush_mode, first_interval=1, persistent=True)


def disable_auto_mode_handlers():
    global _auto_handlers_active
    if not _auto_handlers_active:
        return
    _auto_handlers_active = False
    if bpy.app.timers.is_registered(start_update_bbrush_mode):
        bpy.app.timers.unregister(start_update_bbrush_mode)


def sync_auto_mode_handlers():
    pref = get_pref()
    if pref is not None and pref.always_use_bbrush_sculpt_mode:
        enable_auto_mode_handlers()
    else:
        disable_auto_mode_handlers()


@persistent
def load_post_draw(args):
    """File load hook: sculpt mode may already be active without a mode-change event."""
    refresh_viewport_overlay()


def _deferred_refresh_overlay():
    """One-shot refresh after register when context is still restricted."""
    refresh_viewport_overlay()
    return None


def register():
    register_module()
    ensure_mode_subscribe()
    ensure_load_post_draw()
    sync_auto_mode_handlers()
    refresh_viewport_overlay()
    bpy.app.timers.register(_deferred_refresh_overlay, first_interval=0.0)


def unregister():
    global _mode_subscribed, _load_post_draw_registered
    disable_auto_mode_handlers()
    view_navigation.unregister()
    sculpt.BbrushExit.exit(bpy.context, True)

    bpy.msgbus.clear_by_owner(owner)
    _mode_subscribed = False

    if load_post_draw in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_post_draw)
    _load_post_draw_registered = False

    if bpy.app.timers.is_registered(_deferred_refresh_overlay):
        bpy.app.timers.unregister(_deferred_refresh_overlay)

    depth_map.remove_draw_handler()
    unregister_module()
