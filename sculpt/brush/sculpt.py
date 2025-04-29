import bpy


class BrushSculpt(bpy.types.Operator):
    bl_idname = "bbrush.sculpt"
    bl_label = "Sculpt"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        print(context, event, self.bl_label)
        return {'PASS_THROUGH'}

    def execute(self, context):
        """不需要执行"""
        return {"FINISHED"}
