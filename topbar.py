import bpy

from .utils import check_pref, get_pref, is_bbrush_mode, get_context_mode


def get_top_bar_text(pref, is_bbrush_mode):
    text = ""
    if is_bbrush_mode:
        return "ESC"
    if pref is not None and pref.top_bar_show_text:
        text = "BBrush"
    return text


def top_bar_draw(self, context):
    if not check_pref():
        return
    from .sculpt import FixBbrushError, BbrushExit, BbrushStart
    pref = get_pref()
    if pref is None:
        return

    layout = self.layout

    bbrush_active = is_bbrush_mode()

    if get_context_mode(context) == "SCULPT":

        row = layout.row(align=True)
        row.separator(factor=2)

        sub_row = row.row(align=True)
        sub_row.alignment = "CENTER"
        if bbrush_active:
            # sub_row.scale_x = 1.5
            sub_row.alert = bbrush_active

        operator = BbrushExit.bl_idname if bbrush_active else BbrushStart.bl_idname

        sub_row.operator(operator, text=get_top_bar_text(pref, bbrush_active), icon="SCULPTMODE_HLT")

        if not bbrush_active:
            FixBbrushError.draw_button(row)
            row.separator()

        if bbrush_active:
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
