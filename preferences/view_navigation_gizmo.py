import bpy


class ViewNavigationGizmo:
    use_view_navigation_gizmo: bpy.props.BoolProperty(name="Use view navigation Gizmo", default=True)
    view_navigation_gizmo_scale: bpy.props.FloatProperty(name="View navigation scale", default=1)

    view_navigation_gizmo_offset: bpy.props.IntVectorProperty(name="View navigation offset", default=(-60, 0), size=2,
                                                              max=0, min=-114514)

    def draw_view_navigation_gizmo(self, layout):
        box = layout.column().box()
        box.prop(self, "use_view_navigation_gizmo")
        box.prop(self, "view_navigation_gizmo_scale")
        box.prop(self, "view_navigation_gizmo_offset")
