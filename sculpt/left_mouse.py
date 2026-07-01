import bpy
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
from mathutils import Vector

from .brush import BrushShortcutKeyScale, BrushShape
from ..debug import DEBUG_LEFT_MOUSE
from ..utils import object_ray_cast, check_mouse_in_model, is_bbrush_mode, get_pref, check_modal_operators, \
    check_mouse_in_depth_map_area, check_mouse_in_shortcut_key_area
from ..utils.manually_manage_events import ManuallyManageEvents


class LeftMouse(bpy.types.Operator, ManuallyManageEvents):
    bl_idname = "sculpt.bbrush_left_mouse"
    bl_label = "Sculpt"
    bl_description = "Left mouse sculpting and view navigation in Bbrush mode"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_bbrush_mode()

    def invoke(self, context, event):
        """Manual click/drag handling; CLICK_DRAG is unreliable in Blender 5.0+."""
        from . import brush_runtime
        from . import UpdateBrushShelf

        brush_runtime.left_mouse = Vector((event.mouse_x, event.mouse_y))

        UpdateBrushShelf.update_brush_shelf(context, event)
        active_tool = ToolSelectPanelHelper.tool_active_from_context(bpy.context)

        if check_mouse_in_depth_map_area(event):  # Scale depth map
            bpy.ops.sculpt.bbrush_depth_scale("INVOKE_DEFAULT")
            return {"FINISHED"}
        elif check_mouse_in_shortcut_key_area(event) and BrushShortcutKeyScale.poll(context):  # Scale shortcut overlay
            bpy.ops.sculpt.bbrush_shortcut_key_scale("INVOKE_DEFAULT")
            return {"FINISHED"}

        elif active_tool and active_tool.idname == "builtin_brush.draw_face_sets":
            return self.brush_stroke(context, event)
        elif active_tool and "face_set" in active_tool.idname:
            """
            "builtin.lasso_face_set",
            "builtin_brush.draw_face_sets",
            "builtin.line_face_set",
            "builtin.polyline_face_set",
            "builtin.face_set_edit",
            "builtin.box_face_set",
            """
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
        # is_in_active_modal = check_mouse_in_active_modal(context, event)  # Unreliable with modifiers
        active_tool = ToolSelectPanelHelper.tool_active_from_context(bpy.context)

        if is_release:  # Click release
            if DEBUG_LEFT_MOUSE:
                print("is_release", is_in_modal)
            if is_in_modal:  # Clicked on another model
                try:
                    res = bpy.ops.object.transfer_mode("INVOKE_DEFAULT")  # Uses C-side GPU depth hit test
                    if "CANCELLED" in res:
                        bpy.ops.sculpt.bbrush_click("INVOKE_DEFAULT")
                finally:
                    return {"FINISHED"}  # Always finish from finally/else paths
            else:
                bpy.ops.sculpt.bbrush_click("INVOKE_DEFAULT")
                return {"FINISHED"}  # Always finish from finally/else paths
        elif is_moving:  # Drag: cannot use PASS_THROUGH; dispatch explicitly
            if DEBUG_LEFT_MOUSE:
                print("is_move", is_in_modal)

            only_shift = event.shift and not event.alt and not event.ctrl

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

            elif active_tool and BrushShape.check_brush_support(active_tool.idname):  # Shape-capable brushes first
                bpy.ops.sculpt.bbrush_shape("INVOKE_DEFAULT")
            elif is_in_modal:  # and is_in_active_modal #
                return self.brush_stroke(context, event)
            else:  # Mouse not over model
                if only_shift:
                    rv3d = context.region_data
                    if rv3d is not None and not rv3d.lock_rotation:
                        try:
                            bpy.ops.view3d.view_roll("INVOKE_DEFAULT", type="ANGLE")  # Roll view
                        except RuntimeError:
                            pass
                elif event.ctrl:  # Ctrl or ctrl+shift brush gestures
                    bpy.ops.sculpt.bbrush_shape("INVOKE_DEFAULT")
                else:
                    from . import view3d_event
                    view3d_event(context, event)
            return {"FINISHED"}
        return {"RUNNING_MODAL"}

    @staticmethod
    def brush_stroke(context, event):
        mouse_offset_compensation(context, event)
        try:
            execute_brush_stroke(event)
        finally:  # Always return FINISHED after stroke
            return {"FINISHED"}


def check_mouse_in_active_modal(context, event) -> bool:
    """Return True if ray cast hits the active sculpt object."""
    obj = context.sculpt_object
    if not obj:
        return False
    mouse = (event.mouse_region_x, event.mouse_region_y)

    depsgraph = context.evaluated_depsgraph_get()
    object_eval = obj.evaluated_get(depsgraph)

    result, location, normal, index = object_ray_cast(object_eval, context, mouse)
    return result


def execute_brush_stroke(event):
    """https://docs.blender.org/api/5.0/bpy.ops.sculpt.html#bpy.ops.sculpt.brush_stroke
    https://docs.blender.org/api/5.1/bpy.ops.sculpt.html#bpy.ops.sculpt.brush_stroke
    Invoke sculpt.brush_stroke; API changed in Blender 5.1."""
    args = {}
    if bpy.app.version >= (5, 1, 0):
        if event.alt:
            args["mode"] = "INVERT"
            args["brush_toggle"] = "None"
        elif event.shift:
            args["mode"] = "NORMAL"
            args["brush_toggle"] = "SMOOTH"
        else:
            args["mode"] = "NORMAL"
            args["brush_toggle"] = "None"
        # bpy.ops.sculpt.brush_stroke("INVOKE_DEFAULT", mode=args["mode"], brush_toggle=args["brush_toggle"])
    else:
        if event.alt:
            args["mode"] = "INVERT"
        elif event.shift:
            args["mode"] = "SMOOTH"
        else:
            args["mode"] = "NORMAL"
    bpy.ops.sculpt.brush_stroke("INVOKE_DEFAULT", **args)


def mouse_offset_compensation(context, event):
    """Compensate cursor drift when starting a stroke near mesh edges."""
    pref = get_pref()
    if pref is not None and pref.enabled_drag_offset_compensation:
        from . import brush_runtime
        now_mouse = Vector((event.mouse_x, event.mouse_y))
        left = brush_runtime.left_mouse
        offset_mouse = (left - now_mouse) * pref.drag_offset_compensation + left
        if DEBUG_LEFT_MOUSE:
            print("mouse_offset_compensation", offset_mouse)
        context.window.cursor_warp(int(offset_mouse.x), int(offset_mouse.y))
