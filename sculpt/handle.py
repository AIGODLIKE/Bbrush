import bpy

from ..topbar import replace_top_bar
from ..utils import get_pref


class BrushHandle:
    use_mouse_emulate_3_button = None
    is_exit: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE"}, name="用于在模态的时候手动退出")

    def check_exit(self, context, event) -> bool:
        if self.is_exit:  # 这个用于顶部的退出按钮
            return True
        elif context.mode != "SCULPT":
            return True

        return False

    def exit(self, context):
        """退出Bbrush模式"""
        inputs = context.preferences.inputs
        inputs.use_mouse_emulate_3_button = self.use_mouse_emulate_3_button

        replace_top_bar(False)

        bpy.ops.wm.redraw_timer("EXEC_DEFAULT", False, type='DRAW', iterations=1)

        return {"FINISHED"}

    def start(self, context):
        """进入Bbrush模式"""
        pref = get_pref()

        replace_top_bar(True)

        inputs = context.preferences.inputs

        self.use_mouse_emulate_3_button = inputs.use_mouse_emulate_3_button
        inputs.use_mouse_emulate_3_button = pref.use_mouse_emulate_3_button

        bpy.ops.wm.redraw_timer("EXEC_DEFAULT", False, type='DRAW', iterations=1)

    @staticmethod
    def toggle_object_mode():
        """在用户切换模式时使用此方法"""
        if bpy.context.mode == "SCULPT" and get_pref().always_use_bbrush_sculpt_mode:
            bpy.ops.bbrush.bbrush_sculpt()
