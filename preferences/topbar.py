import bpy


class TopBar:
    top_bar_show_text: bpy.props.BoolProperty(name="Display top text", default=False)

    def draw_top_ber(self, layout):
        box = layout.box()
        box.label(text="Top bar")
        row = box.row(align=True)
        row.prop(self, "top_bar_show_text")
