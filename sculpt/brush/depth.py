import bpy
from mathutils import Vector

from ...utils import get_pref, check_mouse_in_depth_map_area
from ...utils.class_template import ScaleOperator, MoveOperator


class BrushDepthScale(bpy.types.Operator, ScaleOperator):
    bl_idname = "sculpt.bbrush_depth_scale"
    bl_label = "Depth Scale"

    def get_start_scale(self) -> float:
        pref = get_pref()
        return pref.depth_scale if pref is not None else 0.3

    def set_value(self, value):
        pref = get_pref()
        if pref is not None:
            pref.depth_scale = value


class BrushDepthMove(bpy.types.Operator, MoveOperator):
    bl_idname = "sculpt.bbrush_depth_move"
    bl_label = "Rotate View/Depth Move"
    text = "Depth map"

    def get_start_offset(self) -> Vector:
        pref = get_pref()
        if pref is None:
            return Vector((0, 0))
        return Vector(pref.depth_offset)

    def check_area(self, context, event):
        return check_mouse_in_depth_map_area(event)

    def set_offset(self, offset: Vector):
        pref = get_pref()
        if pref is not None:
            pref.depth_offset = offset
