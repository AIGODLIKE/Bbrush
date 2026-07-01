import os

from bpy.utils.toolsystem import ToolDef

CIRCULAR_MASK_ID = "bbrush.circular_mask"
ELLIPSE_MASK_ID = "bbrush.ellipse_mask"
CIRCULAR_HIDE_ID = "bbrush.circular_hide"
ELLIPSE_HIDE_ID = "bbrush.ellipse_hide"


def get_dat_icon(name):
    from ...src import ICON_PATH
    return os.path.normpath(os.path.join(ICON_PATH, name))


def mask_draw_settings(context, layout, tool):
    props = tool.operator_properties("paint.mask_lasso_gesture")
    layout.prop(props, "use_front_faces_only", expand=False)


@ToolDef.from_fn
def circular_mask():
    return dict(
        idname=CIRCULAR_MASK_ID,
        label="Circular mask",
        description="Draw circular mask",
        icon=get_dat_icon("brush.sculpt.circular_mask"),
        cursor="PAINT_CROSS",
        widget=None,
        draw_settings=mask_draw_settings,
    )


@ToolDef.from_fn
def ellipse_mask():
    return dict(
        idname=ELLIPSE_MASK_ID,
        label="Ellipse mask",
        description="Draw elliptical mask",
        icon=get_dat_icon("brush.sculpt.ellipse_mask"),
        cursor="PAINT_CROSS",
        widget=None,
        draw_settings=mask_draw_settings,
    )


@ToolDef.from_fn
def circular_hide():
    return dict(
        idname=CIRCULAR_HIDE_ID,
        label="Circular hide",
        description="Draw circular hide",
        icon=get_dat_icon("brush.sculpt.circular_hide"),
        cursor="PAINT_CROSS",
        widget=None,
        draw_settings=None,
    )


@ToolDef.from_fn
def ellipse_hide():
    return dict(
        idname=ELLIPSE_HIDE_ID,
        label="Ellipse hide",
        description="Draw elliptical hide",
        icon=get_dat_icon("brush.sculpt.ellipse_hide"),
        cursor="PAINT_CROSS",
        widget=None,
        draw_settings=None,
    )
