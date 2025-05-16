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
    from .sculpt import BBrushSculpt
    pref = get_pref()

    layout = self.layout

    is_bbrush_mode = is_bbruse_mode()

    # layout.label(text=region.alignment)
    # layout.label(text=layout.alignment)
    if context.mode == "SCULPT":

        sub_row = layout.row(align=True)
        sub_row.separator(factor=2)

        if not pref.always_use_bbrush_sculpt_mode:
            ss = sub_row.row(align=True)
            ss.alignment = "CENTER"
            if is_bbrush_mode:
                # ss.scale_x = 1.5
                ss.alert = is_bbrush_mode

            ss.operator(BBrushSculpt.bl_idname, text=get_top_bar_text(pref, is_bbrush_mode),
                        icon="SCULPTMODE_HLT").is_exit = is_bbrush_mode
            if not is_bbrush_mode:
                ss.separator()

        if is_bbrush_mode:
            sub_row.prop(pref, "always_use_bbrush_sculpt_mode", emboss=True, icon="AUTO", text="")

            row = layout.row(align=True)
            row.prop(pref, "show_shortcut_keys", emboss=True, icon="EVENT_K", text="")
            text = "Silhouette Mode" if pref.top_bar_show_text else ""
            row.prop(pref, "depth_display_mode", emboss=True, text=text)

            row.separator()
            row.operator("wm.window_fullscreen_toggle", emboss=False, icon="FULLSCREEN_ENTER",
                         text="")  # "FULLSCREEN_EXIT"
            row.separator(factor=1)
            row.label(text="You are using BBrush mode")
            row.operator("wm.url_open",
                         text="Encountering a problem?",
                         emboss=False, icon="INTERNET"
                         ).url = "https://github.com/AIGODLIKE/Bbrush/issues/new"
            row.separator(factor=5)


def register():
    bpy.types.TOPBAR_MT_editor_menus.append(top_bar_draw)


def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(top_bar_draw)
