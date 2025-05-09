import bpy


class ShortcutKey:
    show_shortcut_keys: bpy.props.BoolProperty(
        name="Display shortcut keys",
        default=True
    )

    shortcut_show_size: bpy.props.FloatProperty(name="Shortcut key display size", min=0.1, default=1, max=114)

    shortcut_offset: bpy.props.IntVectorProperty(name="Shortcut key offset", default=(0, 10), size=2,
                                              max=114514, min=0)
    def draw_shortcut(self, layout):
        box = layout.box()
        box.label(text="Shortcut")

        box.prop(self, "show_shortcut_keys")
        box.prop(self, "shortcut_show_size")

        row = box.row(align=True)
        row.prop(self, "shortcut_offset")

