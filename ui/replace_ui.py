from functools import cache

import bpy

from ..utils.public import all_operator_listen, PublicClass

UiReplaceFunc = None


@cache
def restart_blender():
    return 'wm.restart_blender' in all_operator_listen()


def draw_restart_button(layout):
    if restart_blender():
        ops = layout.row()
        ops.alert = True
        ops.operator(operator="wm.restart_blender",
                     text="", emboss=False, icon='QUIT')


def append_top_editor_menus(self, context):
    pref = PublicClass.pref_()

    layout = self.layout
    region = context.region
    screen = context.screen

    # layout.label(text=self.__class__.__name__)
    # layout.label(text=region.alignment)
    # layout.label(text=pref.alignment)

    fs = screen.show_fullscreen
    cn = self.__class__.__name__
    if pref.alignment == 'LEFT':
        show = cn == "TOPBAR_MT_editor_menus" or (
                cn == "TOPBAR_HT_upper_bar" and region.alignment == "TOP" and pref.replace_top_bar and pref.sculpt)
    elif pref.alignment == 'CENTER':
        show = cn == "TOPBAR_HT_upper_bar" and region.alignment == "TOP"
    elif pref.alignment == 'RIGHT':
        show = cn == "TOPBAR_HT_upper_bar" and region.alignment == "RIGHT"
    else:
        show = False

    sculpt = pref.sculpt or pref.is_sculpt_mode
    if show and sculpt:
        sub_row = layout.row(align=True)
        icon = 'EVENT_ESC' if pref.sculpt else 'SCULPTMODE_HLT'
        text = "Bbrush" if pref.show_text else ''
        if not pref.always_use_sculpt_mode:
            sub_row.prop(pref,
                         'sculpt',
                         text=text,
                         icon=icon)
        if pref.sculpt:
            sub_row.prop(pref, 'always_use_sculpt_mode', emboss=True, icon='AUTO', text='')

            row = layout.row(align=True)
            row.prop(pref, 'depth_display_mode', emboss=True, )
            row.prop(pref, 'depth_scale', emboss=True, )
            row.prop(pref, 'show_shortcut_keys', emboss=True, icon='EVENT_K', text='')
            if pref.replace_top_bar:
                draw_restart_button(row)

        if fs and pref.sculpt and pref.replace_top_bar:
            layout.operator(
                "screen.back_to_previous",
                icon='SCREEN_BACK',
                text="Back to Previous",
            )


def replace_top_bar(replace: bool):
    global UiReplaceFunc
    cls = bpy.types.TOPBAR_HT_upper_bar

    if UiReplaceFunc is None:
        UiReplaceFunc = cls.draw

    if replace:
        cls.draw = append_top_editor_menus
    else:
        cls.draw = UiReplaceFunc


def update_top_bar():
    pref = PublicClass.pref_()

    if pref.replace_top_bar:
        show = pref.sculpt
    else:
        show = False
    replace_top_bar(show)


def register():
    bpy.types.TOPBAR_MT_editor_menus.prepend(append_top_editor_menus)
    bpy.types.TOPBAR_HT_upper_bar.append(append_top_editor_menus)


def unregister():
    if hasattr(bpy.types, 'TOPBAR_MT_editor_menus'):
        bpy.types.TOPBAR_MT_editor_menus.remove(append_top_editor_menus)
    if hasattr(bpy.types, 'TOPBAR_HT_upper_bar'):
        bpy.types.TOPBAR_HT_upper_bar.remove(append_top_editor_menus)
    replace_top_bar(False)
