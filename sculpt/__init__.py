import bpy
from mathutils import Vector

from . import brush
from .keymap import BrushKeymap
from .runtime import BrushRuntime
from .shortcut_key import ShortcutKey
from .update_brush_shelf import UpdateBrushShelf
from .view_property import ViewProperty
from ..debug import DEBUG_LEFT_MOUSE, DEBUG_MODE_TOGGLE
from ..utils import get_pref, refresh_ui, is_bbruse_mode, check_pref, check_mouse_in_model, object_ray_cast
from ..utils.manually_manage_events import ManuallyManageEvents

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


class ManuallyManage50(ManuallyManageEvents):
    """由于5.0版本的拖动事件触发不灵敏,所以需要手动管理
    """

    def new_version_usage_method(self, context, event):
        context.window_manager.modal_handler_add(self)
        self.start_manually_manage_events(event)
        # CLICK_DRAG 在 5.0以上版本中拖动事件不易被触发
        if DEBUG_LEFT_MOUSE:
            print("left mouse",
                  "\t", event.value, event.type,
                  "\t", event.value_prev, event.type_prev,
                  )
        return {'RUNNING_MODAL'}

    @staticmethod
    def check_mouse_in_active_modal(context, event) -> bool:
        """检查鼠标是否在活动模型上"""
        obj = context.sculpt_object
        mouse = (event.mouse_region_x, event.mouse_region_y)
        result, location, normal, index = object_ray_cast(obj, context, mouse)
        return result

    def modal(self, context, event):
        global brush_runtime

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
            bpy.ops.sculpt.bbrush_drag("INVOKE_DEFAULT")
            return {"FINISHED"}
        return {"RUNNING_MODAL"}


class LeftMouse(bpy.types.Operator, ManuallyManage50):
    bl_idname = "sculpt.bbrush_left_mouse"
    bl_label = "Sculpt"
    bl_description = "LeftMouse"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_bbruse_mode()

    def invoke(self, context, event):
        global brush_runtime

        return self.new_version_usage_method(context, event)


def refresh_depth_map():
    from ..depth_map.gpu_buffer import clear_gpu_cache
    clear_gpu_cache()


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


class RightMouse(bpy.types.Operator, ManuallyManageEvents):
    bl_idname = "sculpt.bbrush_right_mouse"
    bl_label = "Sculpt"
    bl_description = "RightMouse"

    def invoke(self, context, event):
        if event.alt or event.shift or event.ctrl:
            return {"PASS_THROUGH"}

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
            bpy.ops.view3d.rotate("INVOKE_DEFAULT")  # 旋转视图
            return {"FINISHED"}
        return {"RUNNING_MODAL"}


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
