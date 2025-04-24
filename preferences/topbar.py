import bpy


class TopBar:
    top_bar_show_text: bpy.props.BoolProperty(name="Display top text", default=False)

    def __update_top__(self, _):
        from ..topbar import update_top_bar
        update_top_bar()

    top_bar_replace: bpy.props.BoolProperty(name="Replace top bar", default=True, update=__update_top__)
    top_bar_alignment: bpy.props.EnumProperty(
        items=[
            ("LEFT", "Left", ""),
            ("CENTER", "Center", ""),
            ("RIGHT", "Right", ""),
        ],
        default="LEFT",
    )

    def draw_top_ber(self, layout):
        layout.label(text="Top bar")
        row = layout.box().row(align=True)
        row.prop(self, "top_bar_show_text")
        row.prop(self, "top_bar_replace")
        row.prop(self, "top_bar_alignment")
