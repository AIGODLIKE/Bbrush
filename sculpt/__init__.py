import bpy
from mathutils import Vector

from . import brush
from .handle import BrushHandle
from .key import BrushKey
from .shortcut_key import ShortcutKey
from .switch_brush_shelf import SwitchBrushShelf
from .view_property import ViewProperty
from ..utils import get_pref, check_mouse_in_3d_area

"""
将整个模态作为一个操作符
进入BBrush模式即进入操作符模态
将所有内容退出

快捷键

"""

brush_runtime: "BBrushSculpt|None" = None


class BBrushSculpt(
    bpy.types.Operator,
    BrushKey,
    BrushHandle,
    SwitchBrushShelf,
    ShortcutKey,
    ViewProperty,
):
    bl_idname = "sculpt.bbrush_sculpt"
    bl_label = "BBrush sculpting"
    bl_description = "Sculpting in the style of Zbrush"
    bl_options = {"REGISTER"}

    left_mouse = Vector((0, 0))

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
        if event.value == "PRESS" and event.type == "LEFTMOUSE":
            self.left_mouse = Vector((event.mouse_x, event.mouse_y))

        if event.value == "RELEASE" or event.value_prev == "RELEASE":
            self.refresh_depth_map()

        if self.check_exit(context, event):
            pref = get_pref()
            if pref.always_use_bbrush_sculpt_mode and self.is_exit:
                pref.always_use_bbrush_sculpt_mode = False
            return self.exit(context)
        elif event.type in {"TIMER", "MOUSEMOVE", "WINDOW_DEACTIVATE", "INBETWEEN_MOUSEMOVE"}:
            return {"PASS_THROUGH"}
        elif check_mouse_in_3d_area(context, event):
            self.update_brush_shelf(context, event)

            if self.key_event(context, event):
                print("key_event", event.value, event.type)
                return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def execute(self, context):
        return {"FINISHED"}

    def refresh_depth_map(self):
        from ..depth_map.gpu_buffer import clear_cache
        clear_cache()


def fix_bbrush_error():
    global brush_runtime
    brush_runtime = None


class FixBbrushError(bpy.types.Operator):
    bl_idname = "sculpt.bbrush_fix"
    bl_label = "BBrush fix"
    bl_description = "Fix Bbrush error"
    bl_options = {"REGISTER"}

    def execute(self, context):
        global brush_runtime
        from .key import BrushKey
        from .view_property import ViewProperty

        if brush_runtime is not None:
            is_reference_error = False
            try:
                brush_runtime.brush_mode
            except ReferenceError:
                is_reference_error = True

            if is_reference_error:
                fix_bbrush_error()
            else:
                brush_runtime.is_exit = True

        BrushKey.restore_key()
        ViewProperty.restore_view_property(context)
        return {"FINISHED"}

    @classmethod
    def draw_button(cls, layout):
        layout.operator(cls.bl_idname, text="", icon="EVENT_F")


def register():
    brush.register()
    bpy.utils.register_class(BBrushSculpt)
    bpy.utils.register_class(FixBbrushError)


def unregister():
    bpy.utils.unregister_class(BBrushSculpt)
    bpy.utils.unregister_class(FixBbrushError)
    brush.unregister()
