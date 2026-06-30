import bpy

is_3_6_up_version = bpy.app.version >= (3, 6, 0)
is_4_1_up_version = bpy.app.version >= (4, 1, 0)
is_5_0_up_version = bpy.app.version >= (5, 0, 0)


def sculpt_invert_hide_face():
    """Invert visible faces; version-specific sculpt operator wrapper."""
    if is_5_0_up_version:
        bpy.ops.paint.visibility_invert()
    elif is_4_1_up_version:
        bpy.ops.paint.visibility_invert()
    elif is_3_6_up_version:
        bpy.ops.sculpt.face_set_invert_visibility()
    else:
        bpy.ops.sculpt.face_set_change_visibility('EXEC_DEFAULT', True, mode='INVERT')


def operator_invoke_confirm(self, event, context, title, message) -> set:
    """Blender 4.1+ invoke_confirm requires title and message kwargs."""
    if bpy.app.version >= (4, 1, 0):
        return context.window_manager.invoke_confirm(
            **{
                "operator": self,
                "event": event,
                'title': title,
                'message': message,
            }
        )
    else:
        return context.window_manager.invoke_confirm(self, event)
