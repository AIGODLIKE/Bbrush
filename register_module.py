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


@persistent
def load_post(args):
    refresh_subscribe()
    sculpt.try_toggle_bbrush_mode()


def update_depth_map():
    """Dot in Bbrush mode refresh depth map"""
    context = bpy.context
    pref = get_pref()
    if not is_bbruse_mode():
        if context.window_manager.keyconfigs.active.name == "BBrush":
            bpy.ops.wm.keyconfig_preset_remove("EXEC_DEFAULT", name="BBrush", remove_name=True)

        if pref.depth_display_mode in ("ALWAYS_DISPLAY", "ONLY_SCULPT") and depth_map.check_depth_map_is_draw(context):
            depth_map.gpu_buffer.clear_gpu_cache()
    return pref.depth_refresh_interval


def register():
    register_module()

    load_subscribe()
    bpy.app.handlers.load_post.append(load_post)

    bpy.app.timers.register(start_update_bbrush_mode, first_interval=1, persistent=True)
    bpy.app.timers.register(update_depth_map, first_interval=1, persistent=True)


def unregister():
    sculpt.BbrushExit.exit(bpy.context)

    bpy.msgbus.clear_by_owner(owner)

    if bpy.app.timers.is_registered(object_mode_update_bbrush_mode):
        bpy.app.timers.unregister(object_mode_update_bbrush_mode)
    if bpy.app.timers.is_registered(update_depth_map):
        bpy.app.timers.unregister(update_depth_map)
    bpy.app.handlers.load_post.remove(load_post)

    unregister_module()
