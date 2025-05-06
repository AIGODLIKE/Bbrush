import bpy

from ...utils import check_mouse_in_modal, check_mouse_in_depth_map_area, get_brush_shape, get_active_tool


class DragBase:
    brush_mode = None
    active_tool = None
    shape = None

    def init_drag_event(self, context, event):
        from .. import brush_runtime
        (active_tool, WorkSpaceTool, index) = get_active_tool(context)
        self.active_tool = active_tool
        self.shape = get_brush_shape(active_tool)
        self.brush_mode = brush_runtime.brush_mode


class DragHide:

    def drag_hide_event(self, context, event):
        if event.value == "RELEASE":
            return {"FINISHED"}
        return {"RUNNING_MODAL"}


class DragMask:
    def drag_mask_event(self, context, event):
        if event.value == "RELEASE":
            return {"FINISHED"}
        return {"RUNNING_MODAL"}


class DragEvent(DragMask, DragHide, DragBase):

    def drag_event(self, context, event):
        if self.brush_mode == "HIDE":
            return self.drag_hide_event(context, event)
        elif self.brush_mode == "MASK":
            return self.drag_mask_event(context, event)

        return {"FINISHED"}


class BrushDrag(bpy.types.Operator, DragEvent):
    bl_idname = "bbrush.drag"
    bl_label = "Drag"
    bl_options = {"REGISTER"}

    def invoke(self, context, event):
        is_in_modal = check_mouse_in_modal(context, event)
        print(context, event, self.bl_label, is_in_modal)

        if check_mouse_in_depth_map_area(event):
            bpy.ops.bbrush.depth_scale("INVOKE_DEFAULT")  # 缩放深度图
            return {"FINISHED"}
        elif not is_in_modal:
            from .. import brush_runtime
            if brush_runtime and brush_runtime.brush_mode != "SCULPT":
                self.init_drag_event(context, event)  # 不是雕刻并且不在模型上
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
            else:
                bpy.ops.view3d.rotate("INVOKE_DEFAULT")  # 旋转视图
                return {"FINISHED"}
        return {"PASS_THROUGH"}

    def modal(self, context, event):
        """        拖动的时候不在模型上拖,执行其它操作        """
        return self.drag_event(context, event)

    def execute(self, context):
        return {"PASS_THROUGH"}
