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
    # Emulate 3 Button Mouse turns Alt+LMB into MMB; LeftMouse passes real MMB presses through.
    _add_keymap_item(km, "sculpt.bbrush_left_mouse", {"type": "MIDDLEMOUSE", "value": "PRESS", "any": True})
    _add_keymap_item(km, "sculpt.bbrush_right_mouse", {"type": "RIGHTMOUSE", "value": "PRESS", "any": True})

    for idname, event, properties in UPDATE_BRUSH_SHELF_KEYS:
        _add_keymap_item(km, idname, event, properties)
    # Resync the shelf when a modifier release was swallowed (e.g. by a popup).
    _add_keymap_item(km, "sculpt.bbrush_update_brush_shelf", {"type": "MOUSEMOVE", "value": "ANY", "any": True})

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


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


_MOUSE_CONFIRM = [
    ("CONFIRM", "RIGHTMOUSE", "ANY", True),
    ("CONFIRM", "MIDDLEMOUSE", "ANY", True),
    ("CONFIRM", "LEFTMOUSE", "ANY", True),
]

# ZBrush-style switching while navigating (e.g. Alt drag pans, releasing Alt mid-drag zooms).
VIEW_MODAL_ITEMS = {
    "View3D Rotate Modal": [
        *_MOUSE_CONFIRM,
        ("SWITCH_TO_ZOOM", "LEFT_CTRL", "ANY", False),
        ("SWITCH_TO_ZOOM", "RIGHT_CTRL", "ANY", False),
        ("AXIS_SNAP_ENABLE", "LEFT_SHIFT", "PRESS", False),
        ("AXIS_SNAP_ENABLE", "RIGHT_SHIFT", "PRESS", False),
        ("AXIS_SNAP_DISABLE", "LEFT_SHIFT", "RELEASE", False),
        ("AXIS_SNAP_DISABLE", "RIGHT_SHIFT", "RELEASE", False),
        ("SWITCH_TO_MOVE", "LEFT_ALT", "ANY", False),
        ("SWITCH_TO_MOVE", "RIGHT_ALT", "ANY", False),
    ],
    "View3D Move Modal": [
        *_MOUSE_CONFIRM,
        ("SWITCH_TO_ZOOM", "LEFT_ALT", "ANY", False),
        ("SWITCH_TO_ZOOM", "RIGHT_ALT", "ANY", False),
        ("SWITCH_TO_ZOOM", "LEFT_CTRL", "ANY", False),
        ("SWITCH_TO_ZOOM", "RIGHT_CTRL", "ANY", False),
    ],
    "View3D Zoom Modal": [
        *_MOUSE_CONFIRM,
        ("SWITCH_TO_ROTATE", "LEFT_CTRL", "RELEASE", False),
        ("SWITCH_TO_ROTATE", "RIGHT_CTRL", "RELEASE", False),
        ("SWITCH_TO_MOVE", "LEFT_CTRL", "PRESS", False),
        ("SWITCH_TO_MOVE", "RIGHT_CTRL", "PRESS", False),
        ("SWITCH_TO_MOVE", "LEFT_ALT", "ANY", False),
        ("SWITCH_TO_MOVE", "RIGHT_ALT", "ANY", False),
    ],
}

# Addon keyconfigs cannot hold modal keymaps, so the active keyconfig is patched while Bbrush mode runs.
# Items are tracked by signature instead of RNA pointers so a keyconfig rebuild cannot leave dangling refs.
_view_modal_state = {}


def _kmi_signature(kmi):
    return (kmi.propvalue, kmi.type, kmi.value, kmi.any, kmi.shift, kmi.ctrl, kmi.alt, kmi.oskey)


def start_view_modal_keymaps():
    if _view_modal_state:
        return
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.active
    if kc is None:
        return

    disabled = {}
    added = {}
    for km_name, items in VIEW_MODAL_ITEMS.items():
        km = kc.keymaps.get(km_name)
        if km is None:
            continue
        disabled[km_name] = []
        for kmi in km.keymap_items:
            if kmi.active:
                kmi.active = False
                disabled[km_name].append(_kmi_signature(kmi))
        added[km_name] = []
        for item in items:
            propvalue, event_type, value, any_mod = item
            kmi = km.keymap_items.new_modal(propvalue, event_type, value, any=any_mod)
            added[km_name].append(_kmi_signature(kmi))

    _view_modal_state.update({"keyconfig": kc.name, "disabled": disabled, "added": added})
    wm.keyconfigs.update()


def stop_view_modal_keymaps():
    if not _view_modal_state:
        return
    state = dict(_view_modal_state)
    _view_modal_state.clear()

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.get(state["keyconfig"])
    if kc is None:
        return

    for km_name, signatures in state["added"].items():
        km = kc.keymaps.get(km_name)
        if km is None:
            continue
        for sig in signatures:
            for kmi in km.keymap_items:
                if _kmi_signature(kmi) == sig:
                    km.keymap_items.remove(kmi)
                    break

    for km_name, signatures in state["disabled"].items():
        km = kc.keymaps.get(km_name)
        if km is None:
            continue
        pending = list(signatures)
        for kmi in km.keymap_items:
            sig = _kmi_signature(kmi)
            if not kmi.active and sig in pending:
                kmi.active = True
                pending.remove(sig)

    wm.keyconfigs.update()
