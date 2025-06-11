import bpy

from .utils import get_pref, is_bbruse_mode


def get_top_bar_text(pref, is_bbrush_mode):
    text = ""
    if is_bbrush_mode:
        return "ESC"
    if pref.top_bar_show_text:
        text = "BBrush"
    return text


def top_bar_draw(self, context):
    from .sculpt import FixBbrushError, BbrushExit, BbrushStart
    pref = get_pref()

    layout = self.layout

    is_bbrush_mode = is_bbruse_mode()

    if context.mode == "SCULPT":

        row = layout.row(align=True)
        row.separator(factor=2)

        sub_row = row.row(align=True)
        sub_row.alignment = "CENTER"
        if is_bbrush_mode:
            # sub_row.scale_x = 1.5
            sub_row.alert = is_bbrush_mode

        operator = BbrushExit.bl_idname if is_bbrush_mode else BbrushStart.bl_idname

        sub_row.operator(operator, text=get_top_bar_text(pref, is_bbrush_mode), icon="SCULPTMODE_HLT")
        
        if not is_bbrush_mode:
            FixBbrushError.draw_button(row)
            row.separator()

        if is_bbrush_mode:
            row.prop(pref, "always_use_bbrush_sculpt_mode", emboss=True, icon="AUTO", text="")

            row = layout.row(align=True)
            row.prop(pref, "show_shortcut_keys", emboss=True, icon="EVENT_K", text="")
            FixBbrushError.draw_button(row)
            text = "Silhouette Mode" if pref.top_bar_show_text else ""
            row.prop(pref, "depth_display_mode", emboss=True, text=text)
            row.separator(factor=5)


def register():
    bpy.types.VIEW3D_MT_editor_menus.append(top_bar_draw)


def unregister():
    bpy.types.VIEW3D_MT_editor_menus.remove(top_bar_draw)
