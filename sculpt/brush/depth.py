import bpy

from ...utils import check_mouse_in_modal


class BrushDepth(bpy.types.Operator):
    bl_idname = "bbrush.depth"
    bl_label = "Depth"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        is_in_modal = check_mouse_in_modal(context, event)
        print(context, event, self.bl_label, is_in_modal)


        return {'PASS_THROUGH'}

    # def depth_scale_update(self, context, event):
    #     co = self.mouse_co
    #     value = self.start_mouse - co
    #     x = 1 / context.region.width * (-1 * value[0])
    #     y = 1 / context.region.height * value[1]
    #
    #     value = self.pref.depth_scale = self.start_buffer_scale + max(x, y) * 2
    #     context.area.header_text_set(f'Depth map zoom value {value}')

    def execute(self, context):
        return {"FINISHED"}
