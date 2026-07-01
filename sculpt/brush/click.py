import bpy

from ...debug import DEBUG_CLICK
from ...utils import is_bbrush_mode, check_mouse_in_model


class BrushClick(bpy.types.Operator):
    bl_idname = "sculpt.bbrush_click"
    bl_label = "Bbrush Click"
    bl_description = "Handle click actions for mask and hide brush shelf modes"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        if not is_bbrush_mode():
            cls.poll_message_set("Bbrush mode is not active")
            return False
        return True

    def invoke(self, context, event):
        from .. import brush_runtime
        is_in_modal = check_mouse_in_model(context, event)

        if DEBUG_CLICK:
            print(self.bl_idname, is_in_modal, brush_runtime.brush_mode)
        if brush_runtime.brush_mode == "MASK":
            if is_in_modal:
                if event.alt and event.ctrl:
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
        return {"PASS_THROUGH", "FINISHED"}
