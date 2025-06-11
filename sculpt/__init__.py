import bpy
from mathutils import Vector

from . import brush
from .keymap import BrushKeymap
from .runtime import BrushRuntime
from .shortcut_key import ShortcutKey
from .update_brush_shelf import UpdateBrushShelf
from .view_property import ViewProperty
from ..debug import DEBUG_LEFT_MOUSE
from ..utils import get_pref, refresh_ui, is_bbruse_mode

"""
通过运行时切换

快捷键 keymap
更新笔刷栏
绘制快捷键
视图偏好设置属性
"""

brush_runtime: "BrushRuntime|None" = None


class BbrushStart(bpy.types.Operator):
    bl_idname = "brush.bbrush_start"
    bl_label = "Bbrush Start"

    def invoke(self, context, event):
        global brush_runtime

        # 确保只有一个运行时
        if brush_runtime is not None:
            return {"CANCELLED"}

        self.start(context, event)
        return self.execute(context)

    def execute(self, context):
        return {"FINISHED"}

    @staticmethod
    def start(context, event):
        global brush_runtime
        brush_runtime = BrushRuntime()

        UpdateBrushShelf.start_brush_shelf(context)
        UpdateBrushShelf.update_brush_shelf(context, event)

        BrushKeymap.start_key(context)
        ShortcutKey.start_shortcut_key()
        ViewProperty.start_view_property(context)
        refresh_ui(context)


class BbrushExit(bpy.types.Operator):
    bl_idname = "brush.bbrush_exit"
    bl_label = "Bbrush Exit"

    def execute(self, context):
        pref = get_pref()
        if pref.always_use_bbrush_sculpt_mode:
            pref.always_use_bbrush_sculpt_mode = False

        self.exit(context)
        return {"FINISHED"}

    @staticmethod
    def exit(context):
        global brush_runtime
        brush_runtime = None

        ShortcutKey.stop_shortcut_key()

        BrushKeymap.restore_key(context)
        UpdateBrushShelf.restore_brush_shelf(context)
        ViewProperty.restore_view_property(context)

        refresh_ui(context)

        if bpy.ops.wm.redraw_timer.poll():
            bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)


class FixBbrushError(bpy.types.Operator):
    bl_idname = "sculpt.bbrush_fix"
    bl_label = "BBrush fix"
    bl_description = "Fix Bbrush error"
    bl_options = {"REGISTER"}

    def execute(self, context):
        global brush_runtime
        from .keymap import BrushKeymap
        from .view_property import ViewProperty

        BbrushExit.exit(context)

        # if brush_runtime is not None:
        #     is_reference_error = False
        #     try:
        #         brush_runtime.brush_mode
        #     except ReferenceError:
        #         is_reference_error = True
        #
        #     if is_reference_error:
        #         fix_bbrush_error()
        #     else:
        #         BbrushExit.exit(context)
        #
        # BrushKeymap.restore_key()
        # ViewProperty.restore_view_property(context)
        return {"FINISHED"}

    @classmethod
    def draw_button(cls, layout):
        layout.operator(cls.bl_idname, text="", icon="EVENT_F")


class LeftMouse(bpy.types.Operator):
    bl_idname = "sculpt.bbrush_leftmouse"
    bl_label = "Sculpt"
    bl_description = "LeftMouse"
    bl_options = {"REGISTER"}

    is_run = None

    @classmethod
    def poll(cls, context):
        return is_bbruse_mode()

    def invoke(self, context, event):
        global brush_runtime

        if LeftMouse.is_run:
            return {"FINISHED", "PASS_THROUGH"}

        if event.value == "PRESS" and event.type == "LEFTMOUSE":
            brush_runtime.left_mouse = Vector((event.mouse_x, event.mouse_y))
        if DEBUG_LEFT_MOUSE:
            print(self.bl_idname, event.value, event.type)

        LeftMouse.is_run = True
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL", "PASS_THROUGH"}

    def modal(self, context, event: "bpy.types.Event"):
        if DEBUG_LEFT_MOUSE:
            print(event.value, event.type, event.value_prev, event.type_prev)

        if event.value == "RELEASE" or event.value_prev == "RELEASE":
            refresh_depth_map()

        is_release_leftmouse = event.value == "RELEASE" and event.type == "LEFTMOUSE"
        is_release_leftmouse_prev = event.value_prev == "RELEASE" and event.type_prev == "LEFTMOUSE"
        if is_release_leftmouse or is_release_leftmouse_prev:
            refresh_depth_map()
            if DEBUG_LEFT_MOUSE:
                print("exit leftmouse")
            LeftMouse.is_run = None
            return {"PASS_THROUGH", "FINISHED"}
        return {"PASS_THROUGH"}


def refresh_depth_map():
    from ..depth_map.gpu_buffer import clear_gpu_cache
    clear_gpu_cache()
    # if DEBUG_LEFT_MOUSE:
    # print("refresh_depth_map")


def try_start_bbrush_mode():
    """在用户切换模式时使用此方法"""
    if bpy.context.mode == "SCULPT" and get_pref().always_use_bbrush_sculpt_mode:
        bpy.ops.brush.bbrush_start("INVOKE_DEFAULT")


def fix_bbrush_error():
    global brush_runtime
    brush_runtime = None


class_list = [
    BbrushStart,
    BbrushExit,
    FixBbrushError,
    LeftMouse,
    UpdateBrushShelf,
]

register_class, unregister_class = bpy.utils.register_classes_factory(class_list)


def register():
    brush.register()
    register_class()


def unregister():
    brush.unregister()
    unregister_class()
