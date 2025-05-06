import bpy
from mathutils import Vector

from ...utils import get_pref, refresh_ui, check_mouse_in_depth_map_area


class BrushDepthScale(bpy.types.Operator):
    bl_idname = "bbrush.depth_scale"
    bl_label = "Depth Scale"
    bl_options = {'REGISTER'}

    start_mouse = None
    start_scale = None

    def invoke(self, context, event):
        self.start_mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        self.start_scale = get_pref().depth_scale

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.value == "RELEASE":
            context.area.header_text_set(None)
            return {"FINISHED"}

        mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        diff_mouse = self.start_mouse - mouse
        x = 1 / context.region.width * (-1 * diff_mouse[0])
        y = 1 / context.region.height * diff_mouse[1]

        scale_value = get_pref().depth_scale = self.start_scale + max(x, y) * 2

        text = bpy.app.translations.pgettext_iface("Depth map zoom value %.2f")
        context.area.header_text_set(text % scale_value)

        refresh_ui(context)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        return {"PASS_THROUGH"}


class BrushDepthMove(bpy.types.Operator):
    bl_idname = "bbrush.depth_move"
    bl_label = "Depth Move"
    bl_options = {'REGISTER'}

    start_mouse = None
    start_offset = None

    def invoke(self, context, event):
        print(context, event, self.bl_label)
        if check_mouse_in_depth_map_area(event):
            self.start_mouse = Vector((event.mouse_region_x, event.mouse_region_y))
            self.start_offset = Vector(get_pref().depth_offset)

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        return {"PASS_THROUGH"}

    def modal(self, context, event):
        if event.value == "RELEASE":
            context.area.header_text_set(None)
            return {"FINISHED"}

        mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        diff_mouse = self.start_mouse - mouse
        diff_mouse[0] = diff_mouse[0] * -1

        x, y = get_pref().depth_offset = [int(i) for i in (self.start_offset + diff_mouse)]

        text = bpy.app.translations.pgettext_iface("Depth map offset x:%i y:%i")
        context.area.header_text_set(text % (x, y))

        refresh_ui(context)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        return {"PASS_THROUGH"}
