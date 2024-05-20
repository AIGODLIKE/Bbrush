"""放置雕刻操作符
统一各版本操作符不同带来的bug
"""
import bpy

is_3_6_up_version = bpy.app.version >= (3, 6, 0)
is_4_1_up_version = bpy.app.version >= (4, 1, 0)


# 反转可见面
def sculpt_invert_hide_face():
    if is_4_1_up_version:
        bpy.ops.paint.visibility_invert()
    elif is_3_6_up_version:
        bpy.ops.sculpt.face_set_invert_visibility()
    else:
        bpy.ops.sculpt.face_set_change_visibility('EXEC_DEFAULT', True, mode='INVERT')


def normal_brush_handle(tool_name):
    if tool_name == 'builtin.mesh_filter':
        bpy.ops.sculpt.mesh_filter('INVOKE_DEFAULT',
                                   True, True)
    elif tool_name == "builtin.cloth_filter":
        bpy.ops.sculpt.cloth_filter('INVOKE_DEFAULT',
                                    True, True)
    elif tool_name == 'builtin.color_filter':
        bpy.ops.sculpt.color_filter(bpy.context,
                                    True, True)
    else:
        bpy.ops.sculpt.brush_stroke('INVOKE_DEFAULT',
                                    True,
                                    mode='NORMAL')
