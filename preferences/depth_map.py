import bpy
import gpu
from ..utils import DISPLAY_ITEMS

class DepthMap:

    depth_display_mode: bpy.props.EnumProperty(
        name="Silhouette Display Mode",
        default="ONLY_SCULPT" if gpu.platform.device_type_get() != "AMD" else "NOT_DISPLAY",
        items=DISPLAY_ITEMS
    )

    depth_scale: bpy.props.FloatProperty(
        name="Silhouette image scaling",
        default=0.3,
        max=2,
        min=0.01,
    )
    depth_offset: bpy.props.IntVectorProperty(name="Silhouette image offset", default=(0, -80), size=2,
                                              max=114514, min=-114514)

    def draw_depth(self, layout):
        box = layout.box()
        box.label(text="Silhouette")
        box.prop(self, "depth_display_mode")
        box.prop(self, "depth_scale")
        row = box.row(align=True)
        row.prop(self, "depth_offset")
