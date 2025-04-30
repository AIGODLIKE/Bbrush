import bpy

from ...utils import check_mouse_in_modal


class BrushClick(bpy.types.Operator):
    bl_idname = "bbrush.click"
    bl_label = "Click"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        from .. import brush_runtime
        return brush_runtime is not None

    def invoke(self, context, event):
        from .. import brush_runtime
        is_in_modal = check_mouse_in_modal(context, event)
        print(context, event, self.bl_label, is_in_modal)
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
