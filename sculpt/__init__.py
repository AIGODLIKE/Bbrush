import bpy

from . import brush
from .handle import BrushHandle
from .key import BrushKey
from .shortcut_key import ShortcutKey
from .switch_brush_shelf import SwitchBrushShelf
from ..adapter import operator_invoke_confirm
from ..utils import get_pref, check_mouse_in_3d_area

"""
将整个模态作为一个操作符
进入BBrush模式即进入操作符模态
将所有内容退出
"""

brush_runtime: "BBrushSculpt|None" = None


class BBrushSculpt(
    bpy.types.Operator,
    BrushKey,
    BrushHandle,
    SwitchBrushShelf,
    ShortcutKey,
):
    bl_idname = "sculpt.bbrush_sculpt"
    bl_label = "BBrush sculpting"
    bl_description = "Sculpting in the style of Zbrush"
    bl_options = {"REGISTER"}

    def exit(self, context):
        global brush_runtime
        brush_runtime = None
        self.stop_shortcut_key()
        return super().exit(context)

    def invoke(self, context, event):
        global brush_runtime

        # 确保只有一个运行时
        if brush_runtime is not None:
            brush_runtime.is_exit = self.is_exit
            return {"CANCELLED"}
        else:
            if self.is_exit:  # 更新数据太快了
                self.is_exit = False
        brush_runtime = self

        self.start(context)
        self.update_brush_shelf(context, event)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event: "bpy.types.Event"):
        # print("modal", self.bl_idname, event.value, event.type)

        if event.value == "RELEASE" or event.value_prev == "RELEASE":
            self.refresh_depth_map()

        if event.type in {"TIMER", "MOUSEMOVE", "WINDOW_DEACTIVATE", "INBETWEEN_MOUSEMOVE"}:
            return {"PASS_THROUGH"}

        if check_mouse_in_3d_area(context, event):
            self.update_brush_shelf(context, event)

            if self.check_exit(context, event):
                pref = get_pref()
                if pref.always_use_bbrush_sculpt_mode and self.is_exit:
                    return operator_invoke_confirm(
                        self,
                        event,
                        context,
                        title="Exit Bbrush Mode?",
                        message="You have enabled the option to always use Brush mode in your preference settings"
                    )
                return self.exit(context)
            elif self.key_event(context, event):
                print("key_event", event.value, event.type)
                return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def execute(self, context):
        return {"FINISHED"}

    def refresh_depth_map(self):
        from ..depth_map.gpu_buffer import clear_cache
        clear_cache()


def register():
    brush.register()
    bpy.utils.register_class(BBrushSculpt)


def unregister():
    bpy.utils.unregister_class(BBrushSculpt)
    brush.unregister()
