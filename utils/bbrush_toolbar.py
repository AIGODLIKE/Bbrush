import os

import bpy
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
from bpy.utils.toolsystem import ToolDef


def get_dat_icon(name):
    from ..src import ICON_PATH
    return os.path.normpath(os.path.join(ICON_PATH, name))


def bbrush_mask_draw_settings(_context, layout, tool):
    props = tool.operator_properties("bbrush.mask")
    layout.prop(props, "use_front_faces_only", expand=False)


@ToolDef.from_fn
def bbrush_translate():
    def draw_settings(context, layout, _tool):
        if context.region.type not in {'UI', 'WINDOW'}:
            row = layout.row(align=True)
            row.prop(context.region, 'type')
            row.prop(context.region, 'type')
            row.prop(context.region, 'type')
            row.prop(context.region, 'type')
            row.prop(context.region, 'type')

    return dict(
        idname="bbrush.translate",
        label="BBrush Move BrushTool",
        description='用于移动雕刻原点的操作控制柄',
        icon="ops.transform.translate",
        cursor='EYEDROPPER',
        widget=None,
        draw_settings=draw_settings,
        keymap="3D View BrushTool: Sculpt, BBrush Move BrushTool",
    )


@ToolDef.from_fn
def bbrush_polygon_mask():
    return dict(
        idname='bbrush.polygon_mask',
        label='多边形绘制遮罩',
        description='绘制多边形遮罩',
        icon=get_dat_icon('brush.sculpt.polygons_mask'),
        cursor='EYEDROPPER',
        widget=None,
        draw_settings=bbrush_mask_draw_settings,
    )


@ToolDef.from_fn
def bbrush_square_mask():
    return dict(
        idname='bbrush.square_mask',
        label='方形绘制遮罩',
        description='绘制方形遮罩',
        icon=get_dat_icon('brush.sculpt.square_mask'),
        cursor='EYEDROPPER',
        widget=None,
        draw_settings=bbrush_mask_draw_settings,
    )


@ToolDef.from_fn
def bbrush_circular_mask():
    return dict(
        idname='bbrush.circular_mask',
        label='圆形绘制遮罩',
        description='绘制圆形遮罩',
        icon=get_dat_icon('brush.sculpt.circular_mask'),
        cursor='EYEDROPPER',
        widget=None,
        draw_settings=bbrush_mask_draw_settings,
    )


@ToolDef.from_fn
def bbrush_ellipse_mask():
    return dict(
        idname='bbrush.ellipse_mask',
        label='椭圆遮罩',
        description='绘制椭圆遮罩',
        icon=get_dat_icon('brush.sculpt.ellipse_mask'),
        cursor='EYEDROPPER',
        widget=None,
        draw_settings=bbrush_mask_draw_settings,
    )


@ToolDef.from_fn
def bbrush_mask_border():
    return dict(
        idname="builtin.box_mask",
        label="Box Mask",
        icon="ops.sculpt.border_mask",
        cursor='EYEDROPPER',
        widget=None,
        draw_settings=bbrush_mask_draw_settings,
    )


toolbar = ToolSelectPanelHelper._tool_class_from_space_type('VIEW_3D')._tools['SCULPT']
mask_brush = 'builtin_brush.Mask'


class BrushTool:
    MaskBrush = (
        mask_brush,
        'builtin.box_mask',
        'builtin.lasso_mask',
        'builtin.line_mask',
    )
    HideBrush = (
        'builtin.box_hide',
        'builtin.box_trim',
        'builtin.lasso_trim',
        'builtin.line_project',
    )

    @classmethod
    def update_toolbar(cls):
        sculpt = cls.TOOLBAR_Dit['SCULPT']
        mask = cls.TOOLBAR_Dit['MASK']
        hide = cls.TOOLBAR_Dit['HIDE']
        from collections.abc import Iterable
        def _tool(tool):
            for i in tool:
                if isinstance(i, ToolDef):
                    idname = i.idname
                    if idname in cls.MaskBrush:
                        mask.append(i)
                    elif idname in cls.HideBrush:
                        hide.append(i)
                    else:
                        sculpt.append(i)
                elif isinstance(i, Iterable):
                    _tool(i)
                elif getattr(i, '__call__', False):
                    _tool(i(bpy.context))
                else:
                    if i != sculpt[-1]:
                        sculpt.append(i)

        cls.init_active_brush()
        _tool(toolbar)
        mask.extend([bbrush_circular_mask,
                     bbrush_ellipse_mask,
                     bbrush_polygon_mask, ])

    @classmethod
    def init_active_brush(cls):
        cls.active_brush = cls._active_brush

    TOOLBAR_Dit = {
        'SCULPT': [],
        'MASK': [],
        'HIDE': [],
        'ORIGINAL_TOOLBAR': toolbar.copy(),
    }

    _active_brush = {  # 记录活动笔刷的名称
        'SCULPT': 'builtin_brush.Draw',
        'MASK': mask_brush,
        'HIDE': 'builtin.box_hide',
    }
    active_brush = _active_brush

    @classmethod
    def toolbar_switch(cls, mode):
        def set_tool(tool):
            tol = ToolSelectPanelHelper._tool_class_from_space_type('VIEW_3D')
            if tol._tools['SCULPT'] != tool:
                tol._tools['SCULPT'] = tool

        if mode in ('SCULPT',
                    'MASK',
                    'HIDE',
                    'ORIGINAL_TOOLBAR',
                    ):
            set_tool(cls.TOOLBAR_Dit[mode])


def register():
    BrushTool.update_toolbar()


def unregister():
    ...
