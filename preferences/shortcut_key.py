import bpy


class ShortcutKey:
    show_shortcut_keys: bpy.props.BoolProperty(
        name="Display shortcut keys",
        default=True
    )
    shortcut_offset_x: bpy.props.IntProperty(
        name="Shortcut key offset X",
        default=20, max=114514, min=0)
    shortcut_offset_y: bpy.props.IntProperty(
        name="Shortcut key offset Y",
        default=20, max=114514, min=0)
    shortcut_show_size: bpy.props.FloatProperty(name="Shortcut key display size", min=0.1, default=1, max=114)

    def draw_shortcut(self, layout):
        box = layout.box()
        box.label(text="Shortcut")

        box.prop(self, "show_shortcut_keys")
        box.prop(self, "shortcut_show_size")

        row = box.row(align=True)
        row.prop(self, "shortcut_offset_x")
        row.prop(self, "shortcut_offset_y")
