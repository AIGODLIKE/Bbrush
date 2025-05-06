import bpy


class DepthMap:
    depth_display_items = (
        ("ALWAYS_DISPLAY", "DisplayedAllTheTime",
         "Keep the silhouette displayed all the time, even when not in sculpting mode"),
        ("ONLY_SCULPT", "SculptModeOnly", "Display silhouette images only in sculpting mode"),
        ("ONLY_BBRUSH", "BbrushModeOnly", "Display silhouette images only in Bbrush mode"),
        ("NOT_DISPLAY", "NotShown", "Never display silhouette images at any time"),
    )

    depth_display_mode: bpy.props.EnumProperty(
        name="Silhouette Display Mode",
        default="ONLY_SCULPT",
        items=depth_display_items
    )

    depth_scale: bpy.props.FloatProperty(
        name="Silhouette image scaling",
        default=0.3,
        max=2,
        min=0.1,
        step=0.1
    )
    depth_offset: bpy.props.IntVectorProperty(name="Silhouette image offset", default=(0, 80), size=2,
                                              max=114514, min=0)

    def draw_depth(self, layout):
        row = layout.row(align=True)
        row.prop(self, "depth_display_mode")

        layout.label(text="Silhouette")
        box = layout.box()
        box.prop(self, "depth_scale")
        row = box.row(align=True)
        row.prop(self, "depth_offset")
