import bpy

from .depth_map import DepthMap
from .shortcut_key import ShortcutKey
from .topbar import TopBar
from .. import __name__ as base_name


class Preferences(
    bpy.types.AddonPreferences,
    
    TopBar,
    DepthMap,
    ShortcutKey,
):
    bl_idname = base_name

    use_mouse_emulate_3_button: bpy.props.BoolProperty(name="Use mouse emulate 3 Button")


    # sculpt: bpy.props.BoolProperty(name="Bbrush",
    #                                default=False,
    #                                options={"SKIP_SAVE"},
    #                                update=sculpt_update)

    always_use_bbrush_sculpt_mode: bpy.props.BoolProperty(
        name="Always use Bbrush sculpting mode",
        description=
        "If entering sculpting mode, Bbrush mode will automatically activate; "
        "if exiting sculpting mode, Bbrush mode will deactivate",
        default=False)

    depth_ray_size: bpy.props.IntProperty(
        name="Depth ray check size(px)",
        description="Check if the mouse is placed over the model, mouse cursor range size", default=100, min=10,
        max=300)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.prop(self, "depth_ray_size")
        box.prop(self, "always_use_bbrush_sculpt_mode")
        box.prop(self, "use_mouse_emulate_3_button")
        layout.separator()

        self.draw_top_ber(layout)
        layout.separator()

        self.draw_depth(box)
        layout.separator()

        self.draw_shortcut(layout)


def register():
    bpy.utils.register_class(Preferences)


def unregister():
    bpy.utils.unregister_class(Preferences)
