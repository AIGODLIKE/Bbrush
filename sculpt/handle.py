import bpy
from mathutils import Vector

from ..utils import get_pref, is_bbruse_mode


class BrushHandle:
    use_mouse_emulate_3_button = None
    is_exit: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE"}, name="用于在模态的时候手动退出")

    mouse_press = None

    def check_exit(self, context, event) -> bool:
        if self.is_exit and is_bbruse_mode():  # 这个用于顶部的退出按钮
            return True
        elif context.mode != "SCULPT":
            return True

        return False

    def exit(self, context):
        """退出Bbrush模式"""

        self.restore_brush_shelf(context)
        self.restore_key(context)

        self.refresh_ui(context)

        return {"FINISHED"}

    def cancel(self, context):
        """在直接退出Blender的时候需要切换快捷键回默认"""
        self.exit(context)

    def start(self, context):
        """进入Bbrush模式"""

        self.start_key(context)
        self.start_shortcut_key()
        self.start_brush_shelf(context)
        self.refresh_ui(context)

    @staticmethod
    def toggle_object_mode():
        """在用户切换模式时使用此方法"""
        if bpy.context.mode == "SCULPT" and get_pref().always_use_bbrush_sculpt_mode:
            bpy.ops.sculpt.bbrush_sculpt("INVOKE_DEFAULT")

    def key_event(self, context, event) -> bool:
        if event.value == "PRESS":
            if event.type == 'NUMPAD_PLUS':
                bpy.ops.sculpt.mask_filter('EXEC_DEFAULT', True, filter_type='GROW', auto_iteration_count=True)
                return True
            elif event.type == 'NUMPAD_MINUS':
                bpy.ops.sculpt.mask_filter('EXEC_DEFAULT', True, filter_type='SHRINK', auto_iteration_count=True)
                return True
            elif event.type in ('UP_ARROW', 'NUMPAD_ASTERIX'):
                bpy.ops.sculpt.mask_filter('EXEC_DEFAULT', True, filter_type='CONTRAST_INCREASE',
                                           auto_iteration_count=False)
                return True
            elif event.type in ('DOWN_ARROW', 'NUMPAD_SLASH'):
                bpy.ops.sculpt.mask_filter('EXEC_DEFAULT', True, filter_type='CONTRAST_DECREASE',
                                           auto_iteration_count=False)
                return True
            elif event.type == "LEFTMOUSE":
                self.mouse_press = Vector((event.mouse_x, event.mouse_y))
        return False
