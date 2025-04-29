import bpy


class BrushClick(bpy.types.Operator):
    bl_idname = "bbrush.click"
    bl_label = "Click"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        print(context, event, self.bl_label)
        from .. import brush_runtime
        
        return {'PASS_THROUGH'}

    def execute(self, context):
        return {"FINISHED"}
