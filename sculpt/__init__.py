import bpy
from mathutils import Vector

from . import brush
from .keymap import BrushKeymap
from .runtime import BrushRuntime
from .shortcut_key import ShortcutKey
from .update_brush_shelf import UpdateBrushShelf
from .view_property import ViewProperty
from ..debug import DEBUG_LEFT_MOUSE, DEBUG_MODE_TOGGLE
from ..utils import get_pref, refresh_ui, is_bbruse_mode, check_pref

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

        if DEBUG_MODE_TOGGLE:
            print(self.bl_idname)

        # 确保只有一个运行时
        if brush_runtime is not None:
            return {"CANCELLED"}

        self.start(context, event)
        return {"FINISHED"}


    @staticmethod
    def start(context, event):
        global brush_runtime
        brush_runtime = BrushRuntime()

        if DEBUG_MODE_TOGGLE:
            print("exit bbrush")

        UpdateBrushShelf.start_brush_shelf(context)
        UpdateBrushShelf.update_brush_shelf(context, event)

        BrushKeymap.start_key(context)
        ShortcutKey.start_shortcut_key()
        ViewProperty.start_view_property(context)
        refresh_ui(context)


class BbrushExit(bpy.types.Operator):
    bl_idname = "brush.bbrush_exit"
    bl_label = "Bbrush Exit"

    exit_always: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        if DEBUG_MODE_TOGGLE:
            print(self.bl_idname)
        pref = get_pref()
        if pref.always_use_bbrush_sculpt_mode and self.exit_always:
            pref["always_use_bbrush_sculpt_mode"] = False
        self.exit(context)
        return {"FINISHED"}

    @staticmethod
    def exit(context, un_reg=False):
        """
        :param context:
        :param un_reg: 是注销操作
        :return:
        """
        global brush_runtime
        brush_runtime = None

        if DEBUG_MODE_TOGGLE:
            print("exit bbrush")

        ShortcutKey.stop_shortcut_key()
        BrushKeymap.restore_key(context)
        UpdateBrushShelf.restore_brush_shelf()
        ViewProperty.restore_view_property(context, un_reg)

        refresh_ui(context)


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
        return {"FINISHED"}

    @classmethod
    def draw_button(cls, layout):
        layout.operator(cls.bl_idname, text="", icon="EVENT_F")


class LeftMouse(bpy.types.Operator):
    bl_idname = "sculpt.bbrush_leftmouse"
    bl_label = "Sculpt"
    bl_description = "LeftMouse"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_bbruse_mode()

    def invoke(self, context, event):
        global brush_runtime

        is_leftmouse = event.type == "LEFTMOUSE"
        is_release = event.value == "RELEASE"
        is_press = event.value == "PRESS"
        is_release_leftmouse_prev = event.value_prev == "RELEASE" and event.type_prev == "LEFTMOUSE"

        if is_press and is_leftmouse:
            brush_runtime.left_mouse = Vector((event.mouse_x, event.mouse_y))
        if is_release_leftmouse_prev or event.value == "RELEASE" or event.value_prev == "RELEASE":
            refresh_depth_map()
        if is_release and is_leftmouse:
            bpy.ops.sculpt.bbrush_click("INVOKE_DEFAULT")
            LeftMouse.is_run = None

        if DEBUG_LEFT_MOUSE:
            print("left mouse", "\t", event.value, event.type, "\t", event.value_prev, event.type_prev)
        return {"FINISHED", "PASS_THROUGH"}


def refresh_depth_map():
    from ..depth_map.gpu_buffer import clear_gpu_cache
    clear_gpu_cache()
    # if DEBUG_LEFT_MOUSE:
    # print("refresh_depth_map")


def try_toggle_bbrush_mode(is_start=False):
    """在用户切换物体模式时
    在启动Blender时
    在开启强制Bbrush模式时

    使用此方法"""
    is_bbruse = is_bbruse_mode()

    if bpy.context.mode == "SCULPT":
        if check_pref() and get_pref().always_use_bbrush_sculpt_mode and not is_bbruse:
            bpy.ops.brush.bbrush_start("INVOKE_DEFAULT")
    elif is_bbruse:
        bpy.ops.brush.bbrush_exit("INVOKE_DEFAULT", exit_always=False)
    else:
        ...


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
