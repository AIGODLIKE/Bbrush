import bpy
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
from mathutils import Vector

from .brush import BrushShortcutKeyScale, BrushShape
from ..debug import DEBUG_LEFT_MOUSE
from ..utils import object_ray_cast, check_mouse_in_model, is_bbruse_mode, get_pref, check_modal_operators, \
    check_mouse_in_depth_map_area, check_mouse_in_shortcut_key_area
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
        from . import brush_runtime
        from . import UpdateBrushShelf

        brush_runtime.left_mouse = Vector((event.mouse_x, event.mouse_y))

        UpdateBrushShelf.update_brush_shelf(context, event)
        active_tool = ToolSelectPanelHelper.tool_active_from_context(bpy.context)

        if check_mouse_in_depth_map_area(event):  # 缩放深度图
            bpy.ops.sculpt.bbrush_depth_scale("INVOKE_DEFAULT")
            return {"FINISHED"}
        elif check_mouse_in_shortcut_key_area(event) and BrushShortcutKeyScale.poll(context):  # 缩放快捷键
            bpy.ops.sculpt.bbrush_shortcut_key_scale("INVOKE_DEFAULT")
            return {"FINISHED"}

        elif active_tool and active_tool.idname == "builtin_brush.draw_face_sets":
            return self.brush_stroke(context, event)
        elif active_tool and "face_set" in active_tool.idname:
            # ("builtin.lasso_face_set",
            #  "builtin_brush.draw_face_sets",
            #  "builtin.line_face_set",
            #  "builtin.polyline_face_set",
            # "builtin.face_set_edit"
            #  "builtin.box_face_set",)
            return {"PASS_THROUGH"}
        elif active_tool and active_tool.idname in (
                "builtin.mask_by_color",
                "builtin.color_filter",
                "builtin.mesh_filter",
                "builtin.cloth_filter",

                "builtin.move",
                "builtin.rotate",
                "builtin.scale",
                "builtin.transform",

                "builtin.annotate",
                "builtin.annotate_line",
                "builtin.annotate_polygon",
                "builtin.annotate_eraser",
        ):
            return {"PASS_THROUGH"}

        self.start_manually_manage_events(event)

        in_run = check_modal_operators(self.bl_idname)
        if DEBUG_LEFT_MOUSE:
            print("left mouse",
                  self.bl_idname, in_run,
                  "\t", event.value, event.type,
                  "\t", event.value_prev, event.type_prev,
                  )

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        from . import UpdateBrushShelf
        UpdateBrushShelf.update_brush_shelf(context, event)

        is_release = event.value == "RELEASE"

        is_moving = self.check_is_moving(event)
        is_in_modal = check_mouse_in_model(context, event)
        is_in_active_modal = check_mouse_in_active_modal(context, event)
        active_tool = ToolSelectPanelHelper.tool_active_from_context(bpy.context)
        is_mask_box = active_tool and active_tool.idname in (
            "builtin_brush.Mask",  # 旧版本名称
            "builtin_brush.mask",
        )

        if is_release:  # 单击
            print("is_release", is_in_active_modal, is_in_modal)
            if is_in_modal and not is_in_active_modal:  # 点在了其它模型上
                try:
                    bpy.ops.object.transfer_mode("INVOKE_DEFAULT")
                finally:
                    return {"FINISHED"}  # 反直觉写法
            bpy.ops.sculpt.bbrush_click("INVOKE_DEFAULT")
            return {"FINISHED"}

        elif is_moving:  # 拖动不能使用PASSTHROUGH,需要手动指定事件
            only_shift = event.shift and not event.alt and not event.ctrl
            print("is_move", only_shift, is_in_modal)

            if active_tool and active_tool.idname == "builtin.line_mask":
                # 3D View Tool: Sculpt, Line Mask
                value = 0 if event.alt else 1
                bpy.ops.paint.mask_line_gesture('INVOKE_DEFAULT', value=value)
            elif active_tool and active_tool.idname == "builtin.line_hide":
                action = "SHOW" if event.alt else "HIDE"
                bpy.ops.paint.hide_show_line_gesture("INVOKE_DEFAULT", xstart=0, action=action)
            elif active_tool and active_tool.idname == "builtin.line_project":
                bpy.ops.sculpt.project_line_gesture("INVOKE_DEFAULT")

            elif active_tool and active_tool.idname == "builtin.box_trim":
                bpy.ops.sculpt.trim_box_gesture("INVOKE_DEFAULT")
            elif active_tool and active_tool.idname == "builtin.lasso_trim":
                bpy.ops.sculpt.trim_lasso_gesture("INVOKE_DEFAULT")
            elif active_tool and active_tool.idname == "builtin.polyline_trim":
                bpy.ops.sculpt.trim_polyline_gesture("INVOKE_DEFAULT")
            elif active_tool and active_tool.idname == "builtin.line_trim":
                bpy.ops.sculpt.trim_line_gesture("INVOKE_DEFAULT")

            elif active_tool and BrushShape.check_brush_supper(active_tool.idname):  # 优先查询支持的形状笔刷
                bpy.ops.sculpt.bbrush_shape("INVOKE_DEFAULT")
            elif is_in_modal and is_in_active_modal:
                return self.brush_stroke(context, event)
            else:  # 鼠标不在模型上
                if only_shift:
                    bpy.ops.view3d.view_roll("INVOKE_DEFAULT", type="ANGLE")  # 倾斜视图
                elif event.ctrl:  # 使用ctrl 或ctrl shift 的笔刷
                    bpy.ops.sculpt.bbrush_shape("INVOKE_DEFAULT")
                else:
                    from . import view3d_event
                    view3d_event(event)
            return {"FINISHED"}
        return {"RUNNING_MODAL"}

    @staticmethod
    def brush_stroke(context, event):
        mouse_offset_compensation(context, event)
        try:
            execute_brush_stroke(event)
        finally:  # 反直觉写法
            return {"FINISHED"}


def check_mouse_in_active_modal(context, event) -> bool:
    """检查鼠标是否在活动模型上"""
    obj = context.sculpt_object
    mouse = (event.mouse_region_x, event.mouse_region_y)
    result, location, normal, index = object_ray_cast(obj, context, mouse)
    return result


def execute_brush_stroke(event):
    if event.alt:
        brush_mode = "INVERT"
    elif event.shift:
        brush_mode = "SMOOTH"
    else:
        brush_mode = "NORMAL"
    bpy.ops.sculpt.brush_stroke("INVOKE_DEFAULT", mode=brush_mode)


def mouse_offset_compensation(context, event):
    """偏移补偿         在鼠标放在模型边缘的时候会出现不跟手的情况 对其进行优化"""
    pref = get_pref()
    if pref.enabled_drag_offset_compensation:
        from . import brush_runtime
        now_mouse = Vector((event.mouse_x, event.mouse_y))
        left = brush_runtime.left_mouse
        offset_mouse = (left - now_mouse) * pref.drag_offset_compensation + left
        print("mouse_offset_compensation", offset_mouse)
        context.window.cursor_warp(int(offset_mouse.x), int(offset_mouse.y))
