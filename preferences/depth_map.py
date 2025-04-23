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
    depth_offset_x: bpy.props.IntProperty(
        name="Silhouette image offset X",
        default=0, max=114514, min=0)
    depth_offset_y: bpy.props.IntProperty(
        name="Silhouette image offset Y",
        default=80, max=114514, min=0)
