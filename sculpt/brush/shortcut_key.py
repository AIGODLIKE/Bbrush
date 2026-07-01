import bpy
from mathutils import Vector

from ...utils import get_pref, check_mouse_in_shortcut_key_area
from ...utils.class_template import ScaleOperator, MoveOperator


class BrushShortcutKeyScale(bpy.types.Operator, ScaleOperator):
    bl_idname = "sculpt.bbrush_shortcut_key_scale"
    bl_label = "Shortcut Key Scale"

    @classmethod
    def poll(cls, context):
        pref = get_pref()
        if pref is None:
            return False
        return pref.show_shortcut_keys and pref.shortcut_key_portability

    def get_start_scale(self) -> float:
        pref = get_pref()
        return pref.shortcut_show_size if pref is not None else 1.0

    def set_value(self, value):
        pref = get_pref()
        if pref is not None:
            pref.shortcut_show_size = value

    def get_x_y(self, context, event):
        mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        diff_mouse = mouse - self.start_mouse
        x = 1 / context.region.width * diff_mouse[0]
        y = 1 / context.region.height * diff_mouse[1]
        return x, y


class BrushShortcutKeyMove(bpy.types.Operator, MoveOperator):
    bl_idname = "sculpt.bbrush_shortcut_key_move"
    bl_label = "Shortcut Key Move"

    @classmethod
    def poll(cls, context):
        pref = get_pref()
        if pref is None:
            return False
        return pref.show_shortcut_keys and pref.shortcut_key_portability and super().poll(context)

    def get_start_offset(self) -> Vector:
        pref = get_pref()
        if pref is None:
            return Vector((0, 0))
        return Vector(pref.shortcut_offset)

    def check_area(self, context, event):
        return check_mouse_in_shortcut_key_area(event)

    def set_offset(self, offset: Vector):
        pref = get_pref()
        if pref is not None:
            pref.shortcut_offset = offset

    def get_offset(self, context, event):
        mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        diff_mouse = mouse - self.start_mouse
        return [int(i) for i in (self.start_offset + diff_mouse)]
