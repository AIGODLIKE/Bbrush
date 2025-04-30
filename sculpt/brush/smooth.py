import bpy

from ...utils import check_mouse_in_modal


class BrushSmooth(bpy.types.Operator):
    bl_idname = "bbrush.smooth"
    bl_label = "Smooth"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        is_in_modal = check_mouse_in_modal(context, event)
        print(context, event, self.bl_label, is_in_modal)
        if not is_in_modal:
            # 倾斜视图
            bpy.ops.view3d.view_roll('INVOKE_DEFAULT', type='ANGLE')
            return {"FINISHED"}

        return {'PASS_THROUGH'}

    def execute(self, context):
        return {"FINISHED"}
