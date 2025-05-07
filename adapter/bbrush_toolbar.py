import os

import bpy
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
from bpy.utils.toolsystem import ToolDef


def get_dat_icon(name):
    from ..src import ICON_PATH
    return os.path.normpath(os.path.join(ICON_PATH, name))


def mask_draw_settings(context, layout, tool):
    props = tool.operator_properties("paint.mask_lasso_gesture")
    layout.prop(props, "use_front_faces_only", expand=False)


@ToolDef.from_fn
def circular_mask():
    return dict(
        idname='builtin.circular_mask',
        label='Circular mask',
        description='Draw circular mask',
        icon=get_dat_icon('brush.sculpt.circular_mask'),
        cursor='EYEDROPPER',
        widget=None,
        draw_settings=mask_draw_settings,
    )


@ToolDef.from_fn
def ellipse_mask():
    return dict(
        idname='builtin.ellipse_mask',
        label='Ellipse mask',
        description='Draw elliptical mask',
        icon=get_dat_icon('brush.sculpt.ellipse_mask'),
        cursor='EYEDROPPER',
        widget=None,
        draw_settings=mask_draw_settings,
    )


toolbar = ToolSelectPanelHelper._tool_class_from_space_type('VIEW_3D')._tools['SCULPT'].copy()
builtin_mask_brush = 'builtin_brush.Mask'


class BrushTool:
    active_brush: dict
    toolbar_dit: dict

    mask_brush = (
        builtin_mask_brush,
        'builtin.box_mask',
        'builtin.lasso_mask',
        'builtin.line_mask',
    )
    hide_brush = (
        'builtin.box_hide',
        'builtin.box_trim',
        'builtin.lasso_trim',
        'builtin.line_project',
    )

    @classmethod
    def update_toolbar(cls):
        cls.init_active_brush()
        cls.init_all_brush()

    @classmethod
    def tool_ops(cls, tools):
        # sculpt = cls.toolbar_dit['SCULPT']

        from collections.abc import Iterable
        for tool in tools:
            if isinstance(tool, ToolDef):
                cls.append_brush(tool)
            elif isinstance(tool, Iterable):
                cls.tool_ops(tool)
            elif getattr(tool, '__call__', False):
                if hasattr(bpy.context, "tool_settings"):
                    cls.tool_ops(tool(bpy.context))
            else:
                # if tool != sculpt[-1]:
                #     sculpt.append(tool)
                ...

    @classmethod
    def init_all_brush(cls):
        cls.toolbar_dit = {
            'SCULPT': [],
            'MASK': [],
            'HIDE': [],
            'ORIGINAL': toolbar.copy(),
        }
        mask = cls.toolbar_dit['MASK']

        cls.tool_ops(toolbar)

        mask.extend([bbrush_circular_mask,
                     bbrush_ellipse_mask,
                     bbrush_polygon_mask, ])

    @classmethod
    def append_brush(cls, brush):
        sculpt = cls.toolbar_dit['SCULPT']
        mask = cls.toolbar_dit['MASK']
        hide = cls.toolbar_dit['HIDE']
        idname = brush.idname
        if idname in cls.mask_brush:
            mask.append(brush)
        elif idname in cls.hide_brush:
            hide.append(brush)
        else:
            sculpt.append(brush)

    @classmethod
    def init_active_brush(cls):
        cls.active_brush = {  # 记录活动笔刷的名称
            'SCULPT': 'builtin_brush.Draw',
            'MASK': builtin_mask_brush,
            'HIDE': 'builtin.box_hide',
        }

    @classmethod
    def toolbar_switch(cls, mode):
        def set_tool(tool):
            tol = ToolSelectPanelHelper._tool_class_from_space_type('VIEW_3D')
            if tol._tools['SCULPT'] != tool:
                tol._tools['SCULPT'] = tool

        if mode in ('SCULPT',
                    'MASK',
                    'HIDE',
                    'ORIGINAL',
                    ):
            set_tool(cls.toolbar_dit[mode])


def register():
    BrushTool.update_toolbar()
    ...


def unregister():
    ...
