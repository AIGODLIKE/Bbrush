import bpy
from bpy.props import IntProperty, FloatProperty


class ModalOperator(bpy.types.Operator):
    """Move an object with the mouse, example"""
    bl_idname = "object.modal_operator"
    bl_label = "Simple Modal Operator"
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        print(event.type, event.value)
        left_press = event.type == 'LEFTMOUSE' and event.value == 'PRESS'

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}
        elif event.shift and event.alt and left_press:
            bpy.ops.sculpt.brush_stroke('INVOKE_DEFAULT', mode='INVERT')
            return {'FINISHED'}
        elif event.shift and left_press:
            bpy.ops.sculpt.brush_stroke('INVOKE_DEFAULT', mode='NORMAL')
            return {'FINISHED'}
        elif left_press:
            return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object:
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}


def menu_func(self, context):
    self.layout.operator(ModalOperator.bl_idname, text=ModalOperator.bl_label)


def register():
    bpy.utils.register_class(ModalOperator)
    bpy.types.VIEW3D_MT_sculpt.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ModalOperator)
    bpy.types.VIEW3D_MT_sculpt.remove(menu_func)


if __name__ == "__main__":
    register()
