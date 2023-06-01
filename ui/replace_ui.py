import inspect
from functools import cache

import bpy

from ..utils.public import all_operator_listen, PublicClass

G_UiReplaceDit = {}


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
        sub_row.alert = True
        sub_row.prop(pref,
                     'sculpt',
                     emboss=False,
                     icon='EVENT_ESC'
                     if pref.sculpt else 'SCULPTMODE_HLT')
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


def __set_menu_fun(origin_menu_class, origin_menu_class_path, replace,
                   replace_func, replace_func_path, menu_key):
    tmp_draw_funcs_list = []
    for i in origin_menu_class.draw._draw_funcs:
        func_path_ = inspect.getfile(i)
        if func_path_ == origin_menu_class_path and replace:
            G_UiReplaceDit[func_path_ + ' draw' +
                           origin_menu_class.__name__] = i
            tmp_draw_funcs_list.append(replace_func)
        elif func_path_ == replace_func_path and (not replace):
            tmp_draw_funcs_list.append(G_UiReplaceDit[menu_key])
        else:
            tmp_draw_funcs_list.append(i)
    origin_menu_class.draw._draw_funcs = tmp_draw_funcs_list
    del tmp_draw_funcs_list


def menu_item_replace(origin_menu_class, replace_func, replace):
    """
    :Menu_class     需要被替换的菜单类
    :replace_func   替换的菜单绘制方法
    :replace        替换的布尔值,真则替换,反之还原
    """

    global G_UiReplaceDit
    origin_menu_class_path = inspect.getfile(origin_menu_class)
    replace_func_path = inspect.getfile(replace_func)

    menu_key = origin_menu_class_path + ' draw' + origin_menu_class.__name__

    if getattr(origin_menu_class, 'draw', False) and (menu_key
                                                      not in G_UiReplaceDit):
        G_UiReplaceDit[menu_key] = origin_menu_class.draw

    if bpy.types.Header in origin_menu_class.__bases__:

        if replace:
            origin_menu_class.draw = replace_func
        else:
            if menu_key in G_UiReplaceDit:
                origin_menu_class.draw = G_UiReplaceDit[menu_key]
    elif getattr(origin_menu_class.draw, '_draw_funcs', False):  # 面板类的
        __set_menu_fun(origin_menu_class, origin_menu_class_path, replace,
                       replace_func, replace_func_path, menu_key)


def replace_top_bar(replace: bool):
    menu_item_replace(bpy.types.TOPBAR_HT_upper_bar,
                      append_top_editor_menus, replace)


def update_top_bar():
    pref = PublicClass.pref_()
    replace_top_bar(pref.sculpt)


def register():
    bpy.types.TOPBAR_MT_editor_menus.append(append_top_editor_menus)  # 顶部标题栏


def unregister():
    if hasattr(bpy.types, 'TOPBAR_MT_editor_menus'):
        bpy.types.TOPBAR_MT_editor_menus.remove(append_top_editor_menus)
    replace_top_bar(False)
