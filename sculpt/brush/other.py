import os

from bpy.utils.toolsystem import ToolDef


def get_dat_icon(name):
    from ...src import ICON_PATH
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


@ToolDef.from_fn
def circular_hide():
    return dict(
        idname='builtin.circular_hide',
        label='Circular mask',
        description='Draw circular mask',
        icon=get_dat_icon('brush.sculpt.circular_hide'),
        cursor='EYEDROPPER',
        widget=None,
        draw_settings=mask_draw_settings,
    )


@ToolDef.from_fn
def ellipse_hide():
    return dict(
        idname='builtin.ellipse_hide',
        label='Ellipse mask',
        description='Draw elliptical mask',
        icon=get_dat_icon('brush.sculpt.ellipse_hide'),
        cursor='EYEDROPPER',
        widget=None,
        draw_settings=mask_draw_settings,
    )
