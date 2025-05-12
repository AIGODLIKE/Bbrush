import bpy
from mathutils import Vector


class ScaleOperator:
    bl_options = {"REGISTER"}

    start_mouse = None
    start_scale = None

    def get_start_scale(self) -> float:
        return 0

    def set_value(self, value):
        ...

    def get_x_y(self, context, event):
        mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        diff_mouse = self.start_mouse - mouse
        x = 1 / context.region.width * (-1 * diff_mouse[0])
        y = 1 / context.region.height * diff_mouse[1]
        return x, y

    def invoke(self, context, event):
        self.start_mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        self.start_scale = self.get_start_scale()

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        from . import refresh_ui
        if event.value == "RELEASE":
            context.area.header_text_set(None)
            return {"FINISHED"}

        x, y = self.get_x_y(context, event)

        scale_value = self.start_scale + max(x, y) * 2
        self.set_value(scale_value)
        text = bpy.app.translations.pgettext_iface(f"{self.bl_label} value %.2f")
        context.area.header_text_set(text % scale_value)

        refresh_ui(context)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        return {"PASS_THROUGH"}


class MoveOperator:
    bl_options = {"REGISTER"}

    start_mouse = None
    start_offset = None

    def get_start_offset(self) -> Vector:
        return Vector((0, 0))

    def set_offset(self, offset: Vector):
        ...

    def check_area(self, context, event) -> bool:
        return True

    def get_offset(self, context, event):
        mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        diff_mouse = self.start_mouse - mouse
        diff_mouse[0] = diff_mouse[0] * -1
        return [int(i) for i in (self.start_offset + diff_mouse)]

    def invoke(self, context, event):
        if self.check_area(context, event):
            self.start_mouse = Vector((event.mouse_region_x, event.mouse_region_y))
            self.start_offset = self.get_start_offset()
            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}
        return {"PASS_THROUGH"}

    def modal(self, context, event):
        from . import refresh_ui
        if event.value == "RELEASE":
            context.area.header_text_set(None)
            return {"FINISHED"}

        x, y = offset = self.get_offset(context, event)
        self.set_offset(offset)
        text = bpy.app.translations.pgettext_iface(f"{getattr(self, 'text', self.bl_label)} offset x:%i y:%i")
        context.area.header_text_set(text % (x, y))

        refresh_ui(context)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        return {"PASS_THROUGH"}
