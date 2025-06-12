import bpy
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper, activate_by_id
from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active
from bpy.utils.toolsystem import ToolDef

from .brush import other
from ..debug import DEBUG_UPDATE_BRUSH_SHELF
from ..utils import refresh_ui, get_active_tool

active_brush_toolbar = {  # 记录活动笔刷的名称
    "SCULPT": "builtin.brush",
    "MASK": "builtin_brush.mask",
    "HIDE": "builtin.box_hide",
}
brush_shelf = {}

mask_brush = (
    "builtin_brush.Mask",  # 旧版本名称
    "builtin_brush.mask",
    "builtin.box_mask",
    "builtin.lasso_mask",
    "builtin.line_mask",
    "builtin.polyline_mask",
)

hide_brush = (
    "builtin.box_hide",
    "builtin.lasso_hide",
    "builtin.line_hide",
    "builtin.line_project",
    "builtin.polyline_hide",

    "builtin.line_trim",
    "builtin.box_trim",
    "builtin.lasso_trim",
    "builtin.polyline_trim",
)


def append_brush(brush):
    idname = brush.idname
    if idname in mask_brush:
        brush_shelf["MASK"].append(brush)
    elif idname in hide_brush:
        if idname == "builtin.line_project":
            brush_shelf["HIDE"].insert(4, brush)
            brush_shelf["HIDE"].insert(5, None)
        else:
            brush_shelf["HIDE"].append(brush)
    else:
        brush_shelf["SCULPT"].append(brush)


def tool_ops(tools):
    from collections.abc import Iterable
    for tool in tools:
        if isinstance(tool, ToolDef):
            append_brush(tool)
        elif hasattr(VIEW3D_PT_tools_active, "_tools_annotate") and tool == VIEW3D_PT_tools_active._tools_annotate[0]:
            brush_shelf["SCULPT"].append(tool)
        elif isinstance(tool, Iterable):
            tool_ops(tool)
        elif getattr(tool, "__call__", False):
            if hasattr(bpy.context, "tool_settings"):
                tool_ops(tool(bpy.context))
        else:
            brush_shelf["SCULPT"].append(tool)


BRUSH_SHELF_MODE = {
    # list(itertools.product(a,a,a))
    # (ctrl, alt, shift): SHELF_MODE
    (True, True, True): "HIDE",
    (True, False, True): "HIDE",

    (True, True, False): "MASK",
    (True, False, False): "MASK",

    # SMOOTH
    (False, True, True): "SCULPT",
    (False, False, True): "SCULPT",

    (False, True, False): "SCULPT",
    (False, False, False): "SCULPT",
}


def set_brush_shelf(shelf_mode):
    shelf = brush_shelf[shelf_mode]
    tol = ToolSelectPanelHelper._tool_class_from_space_type("VIEW_3D")
    if tol._tools["SCULPT"] != shelf:
        tol._tools["SCULPT"] = shelf


class UpdateBrushShelf(bpy.types.Operator):
    bl_idname = "sculpt.bbursh_update_brush_shelf"
    bl_label = "Update Brush Shelf"

    def invoke(self, context, event):
        self.update_brush_shelf(context, event)
        return {"PASS_THROUGH", "FINISHED"}

    # SCULPT,SMOOTH,HIDE,MASK,ORIGINAL
    brush_shelf_mode = "NONE"

    @classmethod
    def update_brush_shelf(cls, context, event):
        """更新笔刷资产架"""
        if context.space_data is None:
            # 可能在切换窗口
            # return
            ...

        key = (event.ctrl, event.alt, event.shift)
        mode = BRUSH_SHELF_MODE[key]  # 使用组合键来确认是否需要更新笔刷工具架

        if DEBUG_UPDATE_BRUSH_SHELF:
            print(cls.bl_idname, "\t", mode, "\t", event.type, event.value)

        (active_tool, work_space_tool, index) = get_active_tool(context)

        if mode != cls.brush_shelf_mode:
            if active_tool:
                active_brush_toolbar[cls.brush_shelf_mode] = active_tool.idname
            set_brush_shelf(mode)
            cls.brush_shelf_mode = mode
            refresh_ui(context)

        (active_tool, work_space_tool, index) = get_active_tool(context)
        if work_space_tool is None:
            tool = active_brush_toolbar[mode]
            cls_helper = ToolSelectPanelHelper._tool_class_from_space_type("VIEW_3D")
            (item, index) = cls_helper._tool_get_by_id(context, tool)
            if item:
                res = activate_by_id(context, "VIEW_3D", tool)
                # if res:
                #     bpy.ops.wm.tool_set_by_id(name=tool)

        from . import brush_runtime
        brush_runtime.brush_mode = mode

    @staticmethod
    def restore_brush_shelf(context):
        """恢复笔刷工具架"""
        global brush_shelf
        if DEBUG_UPDATE_BRUSH_SHELF:
            # import traceback
            # traceback.print_stack()
            print("restore_brush_shelf", brush_shelf.keys())
        if "ORIGINAL" in brush_shelf.keys():
            set_brush_shelf("ORIGINAL")

        brush_shelf.clear()

    @staticmethod
    def start_brush_shelf(context):
        """初始化工具架"""
        global brush_shelf

        origin_brush_toolbar = ToolSelectPanelHelper._tool_class_from_space_type("VIEW_3D")._tools["SCULPT"].copy()
        brush_shelf.update({
            "ORIGINAL": origin_brush_toolbar,
            "SCULPT": [],
            "HIDE": [],
            "MASK": [],
        })

        tool_ops(origin_brush_toolbar)
        brush_shelf["MASK"].extend((
            other.circular_mask,
            other.ellipse_mask,
        ))

        brush_shelf["HIDE"].extend((
            other.circular_hide,
            other.ellipse_hide,
        ))

        if DEBUG_UPDATE_BRUSH_SHELF:
            print("start_brush_shelf", brush_shelf.keys())
