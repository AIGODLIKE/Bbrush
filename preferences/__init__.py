import bpy

from .depth_map import DepthMap
from .shortcut_key import ShortcutKey
from .topbar import TopBar
from .. import __package__ as base_name
from .. import sculpt


class Preferences(
    bpy.types.AddonPreferences,
    
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
        update=lambda self, context: sculpt.BBrushSculpt.toggle_object_mode()
    )

    depth_ray_size: bpy.props.IntProperty(
        name="Depth ray check size(px)",
        description="Check if the mouse is placed over the model, mouse cursor range size", default=30, min=10,
        max=300)

    def draw(self, context):
        layout = self.layout

        col = layout.box()
        col.label(text="Sculpt")
        col.prop(self, "always_use_bbrush_sculpt_mode")
        col.label(text="Tips:Automatically enter Bbrush mode when entering carving mode")
        col.prop(self, "depth_ray_size")

        self.draw_top_ber(layout)
        self.draw_depth(layout)
        self.draw_shortcut(layout)


def register():
    bpy.utils.register_class(Preferences)


def unregister():
    bpy.utils.unregister_class(Preferences)
