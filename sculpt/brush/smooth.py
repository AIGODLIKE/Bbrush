import bpy

from ...debug import DEBUG_SMOOTH
from ...utils import check_mouse_in_model, is_bbruse_mode


class BrushSmooth(bpy.types.Operator):
    bl_idname = "sculpt.bbrush_smooth"
    bl_label = "Smooth"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_bbruse_mode()

    def invoke(self, context, event):
        is_in_modal = check_mouse_in_model(context, event)
        if DEBUG_SMOOTH:
            print(self.bl_idname, context, event, self.bl_label, is_in_modal)
        if not is_in_modal:
            # 倾斜视图
            bpy.ops.view3d.view_roll("INVOKE_DEFAULT", type="ANGLE")
            return {"FINISHED"}
        return {"FINISHED", "PASS_THROUGH"}
