import bpy

from ..utils.manually_manage_events import ManuallyManageEvents


class RightMouse(bpy.types.Operator, ManuallyManageEvents):
    bl_idname = "sculpt.bbrush_right_mouse"
    bl_label = "Sculpt"
    bl_description = "RightMouse"

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        self.start_manually_manage_events(event)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        is_move = self.is_move(event)
        is_release = event.value == "RELEASE"
        if is_release:
            bpy.ops.wm.call_panel("INVOKE_DEFAULT", name="VIEW3D_PT_sculpt_context_menu")
            return {"FINISHED"}
        elif is_move:  # 不能使用PASSTHROUGH,需要手动指定事件
            if event.alt:
                bpy.ops.view3d.move("INVOKE_DEFAULT")  # 平移视图
            elif event.ctrl:
                bpy.ops.view3d.zoom("INVOKE_DEFAULT")  # 缩放视图
            else:
                bpy.ops.view3d.rotate("INVOKE_DEFAULT")  # 旋转视图
            return {"FINISHED"}
        return {"RUNNING_MODAL"}
