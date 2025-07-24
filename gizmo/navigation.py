import bpy

from ..utils.navigation import *
from ..utils.translate import translate_lines_text


class Navigation(bpy.types.Operator):
    bl_idname = "sculpt.navigation_view"
    bl_label = "Navigation"

    bl_options = {"REGISTER"}

    @classmethod
    def description(cls, context, properties):
        return translate_lines_text(
            "Bbrush view navigation",
            " ",
            "If you need to close it, you can adjust it in the plugin preference settings",
        )

    @classmethod
    def poll(cls, context):
        return context.space_data and context.space_data.region_3d

    def setup(self):
        self.in_modal = False
        self.rotate_index = (0, 0)
        self.start_mouse = Vector((0, 0))
        self.draw_points = ((0, 0), (0, 0))

    def invoke(self, context, event):
        return {"FINISHED", "PASS_THROUGH"}
        self.setup()
        self.in_modal = True
        self.start_rotate = context.space_data.region_3d.view_rotation
        self.last_mouse = self.start_mouse = Vector((event.mouse_region_x, event.mouse_region_y))

        update_view_rotate(context, self.rotate_index)
        self.refresh_rotate_index(context)
        return {"RUNNING_MODAL"}

    def exit(self, context, cancel):
        context.area.header_text_set(None)
        self.in_modal = False
        if cancel:
            context.space_data.region_3d.view_rotation = self.start_rotate

    def modal(self, context, event):
        start_mouse = self.start_mouse
        mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        move = 20

        diff_x = mouse.x - start_mouse.x
        diff_y = mouse.y - start_mouse.y

        is_x = abs(diff_x) > move
        is_y = abs(diff_y) > move
        if event.type == "LEFTMOUSE" and event.value == "RELEASE":
            self.exit(context, False)
            return {"FINISHED"}
        if is_x or is_y:
            w, h = self.rotate_index
            if is_y:
                if diff_y > 0:
                    h += 1
                else:
                    h -= 1
                h = max(0, min(h, 4))
            elif is_x:
                if diff_x > 0:
                    w += 1
                else:
                    w -= 1

                if w < 0:
                    w = 7
                elif w > 7:
                    w = 0
                w = max(0, min(w, 7))
            self.start_mouse = mouse
            self.rotate_index = (w, h)
            update_view_rotate(context, (w, h))

        return {"RUNNING_MODAL"}

    def refresh_rotate_index(self, context):
        if self.in_modal:
            return
        w_index, h_index = get_hw_index_from_2d(context)

        if 0 <= w_index < 8 and 0 <= h_index < 5:
            self.rotate_index = (w_index, h_index)


classes = (
    Navigation,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
