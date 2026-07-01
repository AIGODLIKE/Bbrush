import bpy
from mathutils import Vector

from . import brush
from . import addon_keymap
from .left_mouse import LeftMouse
from .right_mouse import RightMouse
from .shortcut_key import ShortcutKey
from .update_brush_shelf import UpdateBrushShelf
from .view_property import ViewProperty
from ..debug import DEBUG_MODE_TOGGLE
from ..utils import get_pref, refresh_ui, get_context_mode, is_bbrush_mode

"""
Runtime toggles:
- addon keymap
- brush shelf updates
- shortcut key overlay
- view preference properties
"""

brush_runtime: "BrushRuntime|None" = None


def _first_space_view3d(context):
    """Resolve a SpaceView3D when operator context is not a 3D region."""
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
    left_mouse = Vector((0, 0))  # Drag offset compensation anchor

    shortcut_key_points = None  # Hit-test bounds for shortcut overlay

    show_floor = None  # Saved overlay.show_floor before entering Bbrush

    # SCULPT,SMOOTH,HIDE,MASK,ORIGINAL
    brush_mode = "NONE"


class BbrushStart(bpy.types.Operator):
    bl_idname = "sculpt.bbrush_start"
    bl_label = "Bbrush Start"
    bl_description = "Enter Bbrush sculpting mode with pen-friendly shortcuts"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        if get_context_mode(context) != "SCULPT":
            cls.poll_message_set("Available in sculpt mode only")
            return False
        if is_bbrush_mode():
            cls.poll_message_set("Bbrush mode is already active")
            return False
        return True

    def invoke(self, context, event):
        global brush_runtime

        if DEBUG_MODE_TOGGLE:
            print(self.bl_idname)

        if brush_runtime is not None:
            return {"CANCELLED"}

        self.start(context, event)
        return {"FINISHED"}

    @staticmethod
    def start(context, event):
        global brush_runtime
        from ..depth_map import refresh_draw_handler

        brush_runtime = BrushRuntime()

        if DEBUG_MODE_TOGGLE:
            print("start bbrush")

        UpdateBrushShelf.start_brush_shelf(context)
        UpdateBrushShelf.update_brush_shelf(context, event)

        ShortcutKey.start_shortcut_key()
        ViewProperty.start_view_property(context)
        refresh_ui(context)
        v3d = _first_space_view3d(context)
        if v3d is not None:
            brush_runtime.show_floor = v3d.overlay.show_floor
            v3d.overlay.show_floor = False

        refresh_draw_handler(context)


class BbrushExit(bpy.types.Operator):
    bl_idname = "sculpt.bbrush_exit"
    bl_label = "Bbrush Exit"
    bl_description = "Leave Bbrush sculpting mode and restore tool shelf settings"
    bl_options = {"REGISTER"}

    exit_always: bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        if not is_bbrush_mode():
            cls.poll_message_set("Bbrush mode is not active")
            return False
        return True

    def execute(self, context):
        if DEBUG_MODE_TOGGLE:
            print(self.bl_idname)
        pref = get_pref()
        if pref is not None and pref.always_use_bbrush_sculpt_mode and self.exit_always:
            pref.always_use_bbrush_sculpt_mode = False
        self.exit(context)
        return {"FINISHED"}

    @staticmethod
    def exit(context, un_reg=False):
        """
        :param context:
        :param un_reg: True when unregistering the addon
        :return:
        """
        global brush_runtime
        from ..depth_map import refresh_draw_handler

        if brush_runtime is not None:
            v3d = _first_space_view3d(context)
            if v3d is not None and brush_runtime.show_floor is not None:
                v3d.overlay.show_floor = brush_runtime.show_floor

        brush_runtime = None

        if DEBUG_MODE_TOGGLE:
            print("exit bbrush")

        ShortcutKey.stop_shortcut_key()
        UpdateBrushShelf.restore_brush_shelf()
        ViewProperty.restore_view_property(context, un_reg)

        refresh_ui(context)
        refresh_draw_handler(context)


class FixBbrushError(bpy.types.Operator):
    bl_idname = "sculpt.bbrush_fix"
    bl_label = "BBrush fix"
    bl_description = (
        "Reset Bbrush runtime state (tool shelf, shortcuts, navigation prefs). "
        "Available in sculpt mode only; Bbrush does not need to be active"
    )
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        from ..utils import get_context_mode
        if get_context_mode(context) != "SCULPT":
            cls.poll_message_set("Available in sculpt mode only")
            return False
        return True

    def execute(self, context):
        BbrushExit.exit(context)
        return {"FINISHED"}

    @classmethod
    def draw_button(cls, layout):
        layout.operator(cls.bl_idname, text="", icon="EVENT_F")


def refresh_depth_map():
    from ..depth_map.gpu_buffer import clear_gpu_cache
    clear_gpu_cache()


def view3d_event(context, event):
    """View navigation from modifier keys (pan/zoom/rotate)."""
    rv3d = getattr(context, "region_data", None)
    if rv3d is None or getattr(context, "space_data", None) is None:
        return

    try:
        if event.alt:
            bpy.ops.view3d.move("INVOKE_DEFAULT")  # Pan view
        elif event.ctrl:
            bpy.ops.view3d.zoom("INVOKE_DEFAULT")  # Zoom view
        elif not rv3d.lock_rotation:
            bpy.ops.view3d.rotate("INVOKE_DEFAULT")  # Rotate view
    except RuntimeError:
        pass


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
    addon_keymap.register()


def unregister():
    addon_keymap.unregister()
    brush.unregister()
    unregister_class()
