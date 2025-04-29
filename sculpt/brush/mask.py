import bpy


class BrushMask(bpy.types.Operator):
    bl_idname = "bbrush.mask"
    bl_label = "Mask"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        print(context, event, self.bl_label)
        return {'PASS_THROUGH'}

    def execute(self, context):
        return {"FINISHED"}
