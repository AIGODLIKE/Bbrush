import bpy

from ...utils import check_mouse_in_modal, check_mouse_in_depth_map_area


class BrushDrag(bpy.types.Operator):
    bl_idname = "bbrush.drag"
    bl_label = "Drag"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        is_in_modal = check_mouse_in_modal(context, event)
        print(context, event, self.bl_label, is_in_modal)

        if check_mouse_in_depth_map_area(event):
            # 缩放深度图
            bpy.ops.bbrush.depth('INVOKE_DEFAULT')
            return {"FINISHED"}
        elif not is_in_modal:
            # 旋转视图
            bpy.ops.view3d.rotate('INVOKE_DEFAULT')
            return {"FINISHED"}
        return {'PASS_THROUGH'}

    def execute(self, context):
        return {"FINISHED"}
