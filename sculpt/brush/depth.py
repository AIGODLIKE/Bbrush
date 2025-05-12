import bpy
from mathutils import Vector

from ...utils import get_pref, check_mouse_in_depth_map_area
from ...utils.class_template import ScaleOperator, MoveOperator


class BrushDepthScale(bpy.types.Operator, ScaleOperator):
    bl_idname = "bbrush.depth_scale"
    bl_label = "Depth Scale"

    def get_start_scale(self) -> float:
        return get_pref().depth_scale

    def set_value(self, value):
        get_pref().depth_scale = value


class BrushDepthMove(bpy.types.Operator, MoveOperator):
    bl_idname = "bbrush.depth_move"
    bl_label = "Rotate View/Depth Move"
    text = "Depth map"

    def get_start_offset(self) -> Vector:
        return Vector(get_pref().depth_offset)

    def check_area(self, context, event):
        return check_mouse_in_depth_map_area(event)

    def set_offset(self, offset: Vector):
        get_pref().depth_offset = offset
