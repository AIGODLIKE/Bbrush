import bpy

from .depth_map import DepthMap
from .shortcut_key import ShortcutKey
from .topbar import TopBar
from .view import View
from .. import __package__ as base_name
from .. import sculpt


class Preferences(
    bpy.types.AddonPreferences,

    View,
    TopBar,
    DepthMap,
    ShortcutKey,
):
    bl_idname = base_name

    always_use_bbrush_sculpt_mode: bpy.props.BoolProperty(
        name="Always use Bbrush sculpting mode",
        description=
        "If entering sculpting mode, Bbrush mode will automatically activate; "
        "if exiting sculpting mode, Bbrush mode will deactivate",
        default=False,
        update=lambda self, context: sculpt.try_toggle_bbrush_mode()
    )

    depth_ray_size: bpy.props.IntProperty(
        name="Depth ray check size(px)",
        description="Check if the mouse is placed over the model, mouse cursor range size", default=100, min=10,
        max=300)

    enabled_drag_offset_compensation: bpy.props.BoolProperty(name="Enabled drag offset compensation", default=True)
    drag_offset_compensation: bpy.props.FloatProperty(
        name="Drag offset compensation",
        description="Compensate for mouse position movement during drawing",
        min=0.1,
        default=0.5,
        max=2
    )

    def draw(self, context):
        from ..sculpt import FixBbrushError
        layout = self.layout

        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False

        box = col.box()
        box.label(text="Sculpt")
        box.prop(self, "always_use_bbrush_sculpt_mode")
        box.prop(self, "depth_ray_size")

        box.prop(self, "enabled_drag_offset_compensation")
        box.prop(self, "drag_offset_compensation")

        sub_col = box.column()

        sub_col.alert = True
        if self.always_use_bbrush_sculpt_mode:
            sub_col.label(text="Tips:Automatically enter Bbrush mode when entering carving mode")

        sub_col.alert = False
        sub_col.operator(FixBbrushError.bl_idname)
        ops = sub_col.operator("wm.url_open", icon="URL", text="Encountering a problem?")
        ops.url = "https://github.com/AIGODLIKE/Bbrush/issues/new"

        split = col.split()

        column = split.column()
        self.draw_top_ber(column)
        self.draw_view(column)

        column = split.column()
        self.draw_depth(column)
        self.draw_shortcut(column)


def register():
    bpy.utils.register_class(Preferences)


def unregister():
    bpy.utils.unregister_class(Preferences)
