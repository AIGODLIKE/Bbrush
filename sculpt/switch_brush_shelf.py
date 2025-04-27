import bpy

from bl_ui.space_toolsystem_common import ToolSelectPanelHelper,activate_by_id,item_from_id
from bpy.utils.toolsystem import ToolDef

origin_brush_toolbar = ToolSelectPanelHelper._tool_class_from_space_type("VIEW_3D")._tools["SCULPT"].copy()
active_brush_toolbar = {  # 记录活动笔刷的名称
            "SCULPT": "builtin.brush",
            "MASK": "builtin_brush.mask",
            "HIDE": "builtin.box_hide",
        }

brush_shelf = {
    "ORIGINAL":origin_brush_toolbar,
    "SCULPT":[],
    "HIDE":[],
    "MASK":[],
}

mask_brush = (
    "builtin_brush.Mask", #旧版本名称
    "builtin_brush.mask",
    "builtin.box_mask",
    "builtin.lasso_mask",
    "builtin.line_mask",
    "builtin.polyline_mask",
)
hide_brush = (
    "builtin.box_hide",
    "builtin.box_trim",
    "builtin.lasso_trim",
    "builtin.line_project",
    "builtin.polyline_hide",
)


def append_brush(brush):
    idname = brush.idname
    if idname in mask_brush:
        brush_shelf["MASK"].append(brush)
    elif idname in hide_brush:
        brush_shelf["HIDE"].append(brush)
    else:
        brush_shelf["SCULPT"].append(brush)

def tool_ops(tools):
    from collections.abc import Iterable
    for tool in tools:
        if isinstance(tool, ToolDef):
            append_brush(tool)
        elif isinstance(tool, Iterable):
            tool_ops(tool)
        elif getattr(tool, "__call__", False):
            if hasattr(bpy.context, "tool_settings"):
                tool_ops(tool(bpy.context))
        else:
            # if tool != sculpt[-1]:
            #     sculpt.append(tool)
            ...
tool_ops(origin_brush_toolbar)

BRUSH_SHELF_MODE = {
    # list(itertools.product(a,a,a))
    # (ctrl,alt,shift):SHELF_MODE
    (True, True, True): "HIDE",
    (True, False, True): "HIDE",

    (True, True, False): "MASK",
    (True, False, False): "MASK",

    #SMOOTH
    (False, True, True): "SCULPT",
    (False, False, True): "SCULPT",

    (False, True, False): "SCULPT",
    (False, False, False): "SCULPT",
}


class SwitchBrushShelf:
    brush_mode = "NONE"  # SCULPT,SMOOTH,HIDE,MASK,ORIGINAL
    
    @staticmethod
    def update_ui(context):
        if context.area:
            context.area.tag_redraw()
        if context.region:
            context.region.tag_redraw()
        if context.screen:
            context.screen.update_tag()
        
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                for region in area.regions:
                    region.tag_redraw()
        # bpy.ops.wm.redraw_timer(type="DRAW", iterations=1)

    @staticmethod
    def get_active_tool(context) -> "()|None":
        return ToolSelectPanelHelper._tool_class_from_space_type("VIEW_3D")._tool_get_active(context,"VIEW_3D","SCULPT")
    
    def update_brush_shelf(self, context, event):
        """更新笔刷资产架"""
        if context.space_data is None:
            # 可能在切换窗口
            return
        
        key = (event.ctrl, event.alt, event.shift)
        mode = BRUSH_SHELF_MODE[key] #使用组合键来确认是否需要更新笔刷工具架
# (ToolDef(idname='builtin.brush', label='Brush', description=None, icon='brush.generic', cursor=None, widget_properties=None, widget=None, keymap=None, brush_type=None, data_block=None, operator=None, draw_settings=None, draw_cursor=None, options={'USE_BRUSHES'}), bpy.data.workspaces['雕刻']...WorkSpaceTool, 0)
        (active_tool,WorkSpaceTool,index) = self.get_active_tool(context)
        print("active_tool",type(active_tool),type(WorkSpaceTool),index)
       
            
        if mode != self.brush_mode:
            # set_tool = active_brush_toolbar[mode]

            if active_tool:
                active_brush_toolbar[self.brush_mode] = active_tool.idname
    
            self.set_brush_shelf(mode)

            print("update_brush_shelf",mode,self.brush_mode)
            # if set_tool:
                # self.update_ui(context)

            self.brush_mode = mode
            self.update_ui(context)

        (active_tool,WorkSpaceTool,index) = self.get_active_tool(context)
        if WorkSpaceTool is None:
            tool = active_brush_toolbar[mode]
            cls = ToolSelectPanelHelper._tool_class_from_space_type("VIEW_3D")
            (item, index) = cls._tool_get_by_id(context, tool)

            # item = _tool_get_by_id_active(context,tool)
            print("aaa",tool,type(item),index)
            if item:
                res = activate_by_id(context,"VIEW_3D",tool)
                print("activate_by_id",res)
                # bpy.ops.wm.tool_set_by_id(name=tool)

    def set_brush_shelf(self, shelf_mode):
        shelf = brush_shelf[shelf_mode]
        tol = ToolSelectPanelHelper._tool_class_from_space_type("VIEW_3D")
        if tol._tools["SCULPT"] != shelf:
            tol._tools["SCULPT"] = shelf
            


    def restore_brush_shelf(self, context):
        """恢复笔刷工具架"""
        self.set_brush_shelf("ORIGINAL")
        self.update_ui(context)
