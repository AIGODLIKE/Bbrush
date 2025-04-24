import bpy

from .handle import BrushHandle
from ..adapter import operator_invoke_confirm
from ..utils import get_pref

"""
TOTO
将整个模态作为一个操作符
进入BBrush模式即进入操作符模态
将所有内容退出
"""

brush_runtime = None


class BbrushSculpt(
    bpy.types.Operator,
    BrushHandle,
):
    bl_idname = "bbrush.bbrush_sculpt"
    bl_label = "Bbrush sculpting"
    bl_description = "Sculpting in the style of Zbrush"
    bl_options = {"REGISTER"}

    def exit(self, context):
        global brush_runtime
        brush_runtime = None
        return super().exit(context)

    def invoke(self, context, event):
        global brush_runtime

        # 确保只有一个运行时
        if brush_runtime is not None:
            brush_runtime.is_exit = self.is_exit
            return {"CANCELLED"}
        brush_runtime = self

        self.start(context)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        pref = get_pref()
        if self.check_exit(context, event):
            if pref.always_use_bbrush_sculpt_mode and self.is_exit:
                return operator_invoke_confirm(
                    self,
                    event,
                    context,
                    title="Exit Bbrush Mode?",
                    message="You have enabled the option to always use Brush mode in your preference settings"
                )
            return self.exit(context)
        return {'PASS_THROUGH'}

    def execute(self, context):
        return {"FINISHED"}


def register():
    bpy.utils.register_class(BbrushSculpt)


def unregister():
    bpy.utils.unregister_class(BbrushSculpt)
