import bpy
from mathutils import Vector

from . import brush
from .keymap import BrushKeymap
from .left_mouse import LeftMouse
from .right_mouse import RightMouse
from .shortcut_key import ShortcutKey
from .update_brush_shelf import UpdateBrushShelf
from .view_property import ViewProperty
from ..debug import DEBUG_MODE_TOGGLE
from ..utils import get_pref, refresh_ui

"""
通过运行时切换

快捷键 keymap
更新笔刷栏
绘制快捷键
视图偏好设置属性
"""

brush_runtime: "BrushRuntime|None" = None


def _first_space_view3d(context):
    """从当前上下文或屏幕中解析一个 SpaceView3D（operator 非 3D 区域调用时 space_data 可能为 None）。"""
    sd = getattr(context, "space_data", None)
    if sd is not None and getattr(sd, "type", None) == "VIEW_3D":
        return sd
    area = getattr(context, "area", None)
    if area is not None and area.type == "VIEW_3D":
        s = area.spaces.active
        if s is not None and getattr(s, "type", None) == "VIEW_3D":
            return s
    screen = getattr(context, "screen", None)
    if screen is None:
        return None
    for a in screen.areas:
        if a.type != "VIEW_3D":
            continue
        s = a.spaces.active
        if s is not None and getattr(s, "type", None) == "VIEW_3D":
            return s
    return None


class BrushRuntime:
    left_mouse = Vector((0, 0))  # 偏移䃼尝用

    shortcut_key_points = []  # 快捷键绘制区域判断用

    # SCULPT,SMOOTH,HIDE,MASK,ORIGINAL
    brush_mode = "NONE"


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
        UpdateBrushShelf.update_brush_shelf(context, event)

        BrushKeymap.start_key(context)
        ShortcutKey.start_shortcut_key()
        ViewProperty.start_view_property(context)
        refresh_ui(context)
        v3d = _first_space_view3d(context)
        if v3d is not None:
            v3d.overlay.show_floor = False

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
        BbrushExit.exit(context)
        return {"FINISHED"}

    @classmethod
    def draw_button(cls, layout):
        layout.operator(cls.bl_idname, text="", icon="EVENT_F")


def refresh_depth_map():
    from ..depth_map.gpu_buffer import clear_gpu_cache
    clear_gpu_cache()


def view3d_event(event):
    """视图操作"""
    if event.alt:
        bpy.ops.view3d.move("INVOKE_DEFAULT")  # 平移视图
    elif event.ctrl:
        bpy.ops.view3d.zoom("INVOKE_DEFAULT")  # 缩放视图
    else:
        bpy.ops.view3d.rotate("INVOKE_DEFAULT")  # 旋转视图


class_list = [
    BbrushStart,
    BbrushExit,
    FixBbrushError,
    LeftMouse,
    RightMouse,
    UpdateBrushShelf,
]

register_class, unregister_class = bpy.utils.register_classes_factory(class_list)


def register():
    brush.register()
    register_class()


def unregister():
    brush.unregister()
    unregister_class()
