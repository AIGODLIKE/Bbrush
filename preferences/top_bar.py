import bpy


class TopBar:
    show_text: bpy.props.BoolProperty(name="Display top text", default=False)

    def __update_top__(self, context):
        from .ui.replace_ui import update_top_bar
        update_top_bar()

    replace_top_bar: bpy.props.BoolProperty(name="Replace top bar", default=True, update=__update_top__)
    top_bar_alignment: bpy.props.EnumProperty(
        items=[
            ("LEFT", "LIFT", ""),
            ("CENTER", "CENTER", ""),
            ("RIGHT", "RIGHT", ""),
        ],
        default="LEFT",
    )

    def draw_top_ber(self, layout):
        layout.label(text="Top bar")
        row = layout.box().row(align=True)
        row.prop(self, "show_text")
        row.prop(self, "replace_top_bar")
        row.prop(self, "top_bar_alignment")
