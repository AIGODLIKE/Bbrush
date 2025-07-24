import bpy

from ..utils import DISPLAY_ITEMS, check_display_mode_is_draw


class ViewNavigationGizmo:
    view_navigation_gizmo_display_mode: bpy.props.EnumProperty(
        name="Display Mode",
        default="ONLY_BBRUSH",
        items=DISPLAY_ITEMS
    )
    view_navigation_gizmo_scale: bpy.props.FloatProperty(name="View navigation scale", default=1)

    view_navigation_gizmo_offset: bpy.props.IntVectorProperty(
        name="View navigation offset",
        default=(-70, -90),
        size=2,
        max=0,
        min=-114514,
    )
    view_navigation_gizmo_show_tips: bpy.props.BoolProperty(name="Show tips", default=True)

    def draw_view_navigation_gizmo(self, layout):
        box = layout.column().box()
        box.label(text="View Navigation")
        box.prop(self, "view_navigation_gizmo_display_mode")
        box.prop(self, "view_navigation_gizmo_scale")
        box.prop(self, "view_navigation_gizmo_offset")
        box.prop(self, "view_navigation_gizmo_show_tips")

    def check_depth_map_is_draw(self, context):
        """检查深度图是否需要绘制"""
        return check_display_mode_is_draw(context, self.view_navigation_gizmo_display_mode)
