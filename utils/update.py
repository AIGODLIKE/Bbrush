import bpy


def startup_timer():
    from .public import PublicClass
    PublicClass.update_interface()
    return 1 / 60


def object_mode_toggle():
    if not bpy.app.timers.is_registered(startup_timer):
        bpy.app.timers.register(startup_timer,
                                first_interval=0.1,
                                persistent=True)


owner = object()


def register():
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, 'mode'),
        owner=owner,
        args=(),
        notify=object_mode_toggle,
    )
    if not bpy.app.timers.is_registered(startup_timer):
        bpy.app.timers.register(startup_timer,
                                first_interval=3,
                                persistent=True)


def unregister():
    bpy.msgbus.clear_by_owner(owner)
    if bpy.app.timers.is_registered(startup_timer):
        bpy.app.timers.unregister(startup_timer)
