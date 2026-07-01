import bpy
from bpy.app.handlers import persistent

from . import depth_map, preferences, topbar, sculpt, src, gizmo
from .src import view_navigation
from .utils import register_submodule_factory, get_pref, is_bbruse_mode

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


def try_toggle_bbrush_mode(is_start=False):
    """Toggle Bbrush mode on sculpt enter/exit, Blender startup, or forced mode."""
    is_bbruse = is_bbruse_mode()

    if bpy.context.mode == "SCULPT":
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


def object_mode_update_bbrush_mode():
    """Called when object mode changes."""
    try_toggle_bbrush_mode()


def load_subscribe():
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, 'mode'),
        owner=owner,
        args=(),
        notify=object_mode_update_bbrush_mode,
        options={"PERSISTENT"}
    )


def refresh_subscribe():
    """Refresh RNA message bus subscriptions."""
    bpy.msgbus.clear_by_owner(owner)
    load_subscribe()


@persistent
def load_post(args):
    refresh_subscribe()
    try_toggle_bbrush_mode()



def register():
    register_module()

    load_subscribe()
    bpy.app.handlers.load_post.append(load_post)

    bpy.app.timers.register(start_update_bbrush_mode, first_interval=1, persistent=True)


def unregister():
    view_navigation.unregister()
    sculpt.BbrushExit.exit(bpy.context, True)

    bpy.msgbus.clear_by_owner(owner)

    if bpy.app.timers.is_registered(start_update_bbrush_mode):
        bpy.app.timers.unregister(start_update_bbrush_mode)
    bpy.app.handlers.load_post.remove(load_post)

    unregister_module()
