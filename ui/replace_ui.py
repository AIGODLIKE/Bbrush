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
    layout = self.layout
    region = context.region
    screen = context.screen
    right = region.alignment != 'RIGHT'

    pref = PublicClass.pref_()
    sculpt = pref.sculpt or pref.is_sculpt_mode

    if right and sculpt:

        sub_row = layout.row(align=True)
        icon = 'EVENT_ESC' if pref.sculpt else 'SCULPTMODE_HLT'
        text = "Bbrush" if pref.show_text else ''
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
            draw_restart_button(row)

        if screen.show_fullscreen and pref.sculpt:
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
    replace_top_bar(pref.sculpt)


def register():
    bpy.types.TOPBAR_MT_editor_menus.append(append_top_editor_menus)  # 顶部标题栏


def unregister():
    if hasattr(bpy.types, 'TOPBAR_MT_editor_menus'):
        bpy.types.TOPBAR_MT_editor_menus.remove(append_top_editor_menus)
    replace_top_bar(False)
