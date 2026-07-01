import bpy

addon_keymaps = []

MASK_KEYS = [
    ("sculpt.mask_filter", {"type": "NUMPAD_PLUS", "value": "PRESS", "ctrl": True, "repeat": True},
     {"filter_type": "GROW", "auto_iteration_count": True}),
    ("sculpt.mask_filter", {"type": "NUMPAD_MINUS", "value": "PRESS", "ctrl": True, "repeat": True},
     {"filter_type": "SHRINK", "auto_iteration_count": True}),
    ("sculpt.mask_filter", {"type": "UP_ARROW", "value": "PRESS", "ctrl": True, "repeat": True},
     {"filter_type": "CONTRAST_INCREASE", "auto_iteration_count": True}),
    ("sculpt.mask_filter", {"type": "NUMPAD_ASTERIX", "value": "PRESS", "ctrl": True, "repeat": True},
     {"filter_type": "CONTRAST_INCREASE", "auto_iteration_count": True}),
    ("sculpt.mask_filter", {"type": "DOWN_ARROW", "value": "PRESS", "ctrl": True, "repeat": True},
     {"filter_type": "CONTRAST_DECREASE", "auto_iteration_count": True}),
    ("sculpt.mask_filter", {"type": "NUMPAD_SLASH", "value": "PRESS", "ctrl": True, "repeat": True},
     {"filter_type": "CONTRAST_DECREASE", "auto_iteration_count": True}),
]

UPDATE_BRUSH_SHELF_KEYS = [
    ("sculpt.bbrush_update_brush_shelf", {"type": "LEFT_CTRL", "value": "ANY", "any": True}, None),
    ("sculpt.bbrush_update_brush_shelf", {"type": "RIGHT_CTRL", "value": "ANY", "any": True}, None),
    ("sculpt.bbrush_update_brush_shelf", {"type": "LEFT_ALT", "value": "ANY", "any": True}, None),
    ("sculpt.bbrush_update_brush_shelf", {"type": "RIGHT_ALT", "value": "ANY", "any": True}, None),
    ("sculpt.bbrush_update_brush_shelf", {"type": "LEFT_SHIFT", "value": "ANY", "any": True}, None),
    ("sculpt.bbrush_update_brush_shelf", {"type": "RIGHT_SHIFT", "value": "ANY", "any": True}, None),
]

TOOL_KEYMAP_NAMES = (
    "3D View Tool: Sculpt, Box Mask",
    "3D View Tool: Sculpt, Lasso Mask",
    "3D View Tool: Sculpt, Line Mask",
    "3D View Tool: Sculpt, Polyline Mask",
    "3D View Tool: Sculpt, Box Hide",
    "3D View Tool: Sculpt, Lasso Hide",
    "3D View Tool: Sculpt, Line Hide",
    "3D View Tool: Sculpt, Polyline Hide",
    "3D View Tool: Sculpt, Box Trim",
)


def _add_keymap_item(km, idname, event, properties=None):
    kmi = km.keymap_items.new(idname, event["type"], event["value"], any=event.get("any", False))
    for key in ("ctrl", "alt", "shift", "repeat"):
        if key in event:
            setattr(kmi, key, event[key])
    if properties:
        for prop, value in properties.items():
            setattr(kmi.properties, prop, value)
    addon_keymaps.append((km, kmi))
    return kmi


def _register_sculpt_keymap(kc):
    km = kc.keymaps.new(name="Sculpt", space_type="EMPTY", region_type="WINDOW")

    _add_keymap_item(km, "sculpt.bbrush_left_mouse", {"type": "LEFTMOUSE", "value": "PRESS", "any": True})
    _add_keymap_item(km, "sculpt.bbrush_right_mouse", {"type": "RIGHTMOUSE", "value": "PRESS", "any": True})

    for idname, event, properties in UPDATE_BRUSH_SHELF_KEYS:
        _add_keymap_item(km, idname, event, properties)

    for idname, event, properties in MASK_KEYS:
        _add_keymap_item(km, idname, event, properties)


def _register_tool_keymaps(kc):
    for name in TOOL_KEYMAP_NAMES:
        km = kc.keymaps.new(name=name, space_type="VIEW_3D", region_type="WINDOW")
        _add_keymap_item(km, "sculpt.bbrush_left_mouse", {"type": "LEFTMOUSE", "value": "PRESS", "any": True})


def register():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is None:
        return

    _register_sculpt_keymap(kc)
    _register_tool_keymaps(kc)
    # Blender 5.1+ addon keyconfig does not support modal keymaps.
    # Gear-style rotate/move/zoom switching relies on default modal keymaps;
    # view3d_event() in left/right mouse still handles basic view navigation.


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
