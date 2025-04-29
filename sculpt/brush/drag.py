import bpy


class BrushDrag(bpy.types.Operator):
    bl_idname = "bbrush.drag"
    bl_label = "Drag"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        print(context, event, self.bl_label)
        from .. import brush_runtime

        return {'PASS_THROUGH'}

    def execute(self, context):
        return {"FINISHED"}
