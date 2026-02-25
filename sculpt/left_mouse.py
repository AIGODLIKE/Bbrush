import bpy
from mathutils import Vector

from ..debug import DEBUG_LEFT_MOUSE
from ..utils import object_ray_cast, check_mouse_in_model, is_bbruse_mode
from ..utils.manually_manage_events import ManuallyManageEvents


class LeftMouse(bpy.types.Operator, ManuallyManageEvents):
    bl_idname = "sculpt.bbrush_left_mouse"
    bl_label = "Sculpt"
    bl_description = "LeftMouse"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_bbruse_mode()

    def invoke(self, context, event):
        """由于5.0版本的拖动事件触发不灵敏,所以需要手动管理拖动及点击事件
        # CLICK_DRAG 在 5.0以上版本中拖动事件不易被触发
        """
        self.start_manually_manage_events(event)

        if DEBUG_LEFT_MOUSE:
            print("left mouse",
                  "\t", event.value, event.type,
                  "\t", event.value_prev, event.type_prev,
                  )

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    @staticmethod
    def check_mouse_in_active_modal(context, event) -> bool:
        """检查鼠标是否在活动模型上"""
        obj = context.sculpt_object
        mouse = (event.mouse_region_x, event.mouse_region_y)
        result, location, normal, index = object_ray_cast(obj, context, mouse)
        return result

    def modal(self, context, event):
        from . import brush_runtime

        is_release = event.value == "RELEASE"

        is_move = self.is_move(event)
        is_in_modal = check_mouse_in_model(context, event)
        is_in_active_modal = self.check_mouse_in_active_modal(context, event)

        if is_release:  # is_left_mouse and
            print("is_release", is_in_active_modal, is_in_modal)
            if is_in_modal and not is_in_active_modal:  # 点在了其它模型上
                try:
                    bpy.ops.object.transfer_mode("INVOKE_DEFAULT")
                finally:
                    return {"FINISHED"}  # 反直觉写法
            bpy.ops.sculpt.bbrush_click("INVOKE_DEFAULT")
            return {"FINISHED"}
        elif is_move:  # 不能使用PASSTHROUGH,需要手动指定事件
            brush_runtime.left_mouse = Vector((event.mouse_x, event.mouse_y))

            only_shift = event.shift and not event.alt and not event.ctrl
            print("is_move", only_shift, is_in_modal)
            if only_shift and not is_in_modal:
                bpy.ops.view3d.view_roll("INVOKE_DEFAULT", type="ANGLE")  # 倾斜视图
                return {"FINISHED"}
            if is_in_modal:
                if event.alt:
                    brush_mode = "INVERT"
                elif event.shift:
                    brush_mode = "SMOOTH"
                else:
                    brush_mode = "NORMAL"
                try:
                    bpy.ops.sculpt.brush_stroke("INVOKE_DEFAULT", mode=brush_mode)
                finally:  # 反直觉写法
                    return {"FINISHED"}
            bpy.ops.sculpt.bbrush_shape("INVOKE_DEFAULT")
            return {"FINISHED"}
        return {"RUNNING_MODAL"}
