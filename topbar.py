import bpy

from .utils import check_operator, get_pref

ORIGIN_TOP_BAR = None


def draw_restart_button(layout):
    if check_operator("wm.restart_blender"):
        ops = layout.row()
        ops.alert = True
        ops.operator(operator="wm.restart_blender",
                     text="", emboss=False, icon="QUIT")


def top_bar_draw(self, context):
    pref = get_pref()

    layout = self.layout
    region = context.region
    screen = context.screen

    fs = screen.show_fullscreen
    align = pref.top_bar_alignment

    name = self.__class__.__name__
    is_upper_bar = name == "TOPBAR_HT_upper_bar"
    is_editor_menu = name == "TOPBAR_MT_editor_menus"

    is_top_region = region.alignment == "TOP"
    is_right_region = region.alignment == "RIGHT"

    if align == "LEFT":
        show = is_editor_menu or (is_upper_bar and is_top_region)
    elif align == "CENTER":
        show = is_upper_bar and is_top_region
    elif align == "RIGHT":
        show = is_upper_bar and is_right_region
    else:
        show = False

    if show and context.mode == "SCULPT":
        sub_row = layout.row(align=True)
        icon = "EVENT_ESC" if pref.sculpt else "SCULPTMODE_HLT"
        text = "Bbrush" if pref.top_bar_show_text else ""
        if not pref.always_use_sculpt_mode:
            sub_row.prop(pref,
                         "sculpt",
                         text=text,
                         icon=icon)
            sub_row.separator()
        if pref.sculpt:
            sub_row.prop(pref, "always_use_sculpt_mode", emboss=True, icon="AUTO", text="")

            row = layout.row(align=True)
            row.prop(pref, "depth_display_mode", emboss=True, )
            row.prop(pref, "depth_scale", emboss=True, )
            row.prop(pref, "show_shortcut_keys", emboss=True, icon="EVENT_K", text="")
            draw_restart_button(row)

        if fs and pref.sculpt:
            layout.operator(
                "screen.back_to_previous",
                icon="SCREEN_BACK",
                text="Back to Previous",
            )


def replace_top_bar(replace: bool):
    global ORIGIN_TOP_BAR
    cls = bpy.types.TOPBAR_HT_upper_bar

    if ORIGIN_TOP_BAR is None:
        ORIGIN_TOP_BAR = cls.draw

    if replace:
        cls.draw = top_bar_draw
    else:
        cls.draw = ORIGIN_TOP_BAR


def update_top_bar():
    replace_top_bar(get_pref().sculpt)


def register():
    bpy.types.TOPBAR_MT_editor_menus.prepend(top_bar_draw)
    bpy.types.TOPBAR_HT_upper_bar.append(top_bar_draw)


def unregister():
    global ORIGIN_TOP_BAR

    bpy.types.TOPBAR_MT_editor_menus.remove(top_bar_draw)
    bpy.types.TOPBAR_HT_upper_bar.remove(top_bar_draw)

    replace_top_bar(False)

    ORIGIN_TOP_BAR = None
