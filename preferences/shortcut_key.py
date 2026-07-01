import bpy


def update_show_shortcut_keys(self, context):
    from ..depth_map import refresh_draw_handler
    refresh_draw_handler(context)


class ShortcutKey:
    show_shortcut_keys: bpy.props.BoolProperty(
        name="Display shortcut keys",
        default=True,
        update=update_show_shortcut_keys,
    )
    shortcut_key_portability: bpy.props.BoolProperty(name="Shortcut Key Portability", default=True)

    shortcut_show_size: bpy.props.FloatProperty(name="Shortcut key display size", min=0.1, default=1, max=10)

    shortcut_offset: bpy.props.IntVectorProperty(
        name="Shortcut key offset",
        default=(10, 30),
        size=2,
        max=4096,
        min=0,
    )

    def draw_shortcut(self, layout):
        box = layout.box()
        box.label(text="Shortcut")

        box.prop(self, "show_shortcut_keys")
        box.prop(self, "shortcut_key_portability")
        box.prop(self, "shortcut_show_size")

        row = box.row(align=True)
        row.prop(self, "shortcut_offset")
