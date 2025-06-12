import bpy

from ...utils import check_mouse_in_model, check_runtime_and_fix
from ...debug import DEBUG_CLICK

class BrushClick(bpy.types.Operator):
    bl_idname = "sculpt.bbrush_click"
    bl_label = "Sculpt"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        from .. import brush_runtime
        return brush_runtime is not None

    def invoke(self, context, event):
        check_runtime_and_fix()
        from .. import brush_runtime
        is_in_modal = check_mouse_in_model(context, event)

        if DEBUG_CLICK:
            print(self.bl_idname, is_in_modal, brush_runtime.brush_mode)

        if brush_runtime.brush_mode == "MASK":
            if is_in_modal:
                if event.alt:
                    bpy.ops.sculpt.mask_filter(filter_type='SHARPEN')
                else:
                    bpy.ops.sculpt.mask_filter(filter_type='SMOOTH')
            else:
                bpy.ops.paint.mask_flood_fill(mode='INVERT')
            return {"FINISHED"}
        elif brush_runtime.brush_mode == "HIDE":
            if is_in_modal:
                bpy.ops.paint.visibility_invert()
            else:
                bpy.ops.paint.hide_show_all(action='SHOW')
            return {"FINISHED"}
        return {"PASS_THROUGH"}

    def execute(self, context):
        return {"FINISHED"}
