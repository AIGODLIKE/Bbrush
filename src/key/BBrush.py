import os

import bpy

# 'C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe'
# "C:\Program Files\Blender Foundation\Blender 4.4\4.4\scripts\presets\keyconfig\keymap_data\blender_default.py"
# bpy.app.binary_path
# bpy.ops.preferences.keyconfig_activate(filepath="C:\\Program Files\\Blender Foundation\\Blender 4.4\\4.4\\scripts\\presets\\keyconfig\\Blender.py")
# blender_default = bpy.utils.execfile(os.path.join(DIRNAME, "keymap_data", "blender_default.py"))


blender_version = ".".join((str(i) for i in bpy.app.version[:2]))
blender_default_file = os.path.join(os.path.dirname(bpy.app.binary_path), blender_version,
                                    "scripts", "presets", "keyconfig", "keymap_data", "blender_default.py")
blender_default = bpy.utils.execfile(os.path.normpath(blender_default_file))

params = blender_default.Params()
sculpt_keymap = blender_default.km_sculpt(params)

keyconfig_version = (4, 4, 32)
keyconfig_data = [
    ("Window", {"space_type": 'EMPTY', "region_type": 'WINDOW'}, {"items": [], },),
    ("View3D Rotate Modal", {'space_type': 'EMPTY', 'region_type': 'WINDOW'}, {"items": []}),

    ("Sculpt", {'space_type': 'EMPTY', 'region_type': 'WINDOW'}, {
        "items": [
            ('object.transfer_mode', {'type': 'LEFTMOUSE', 'value': 'CLICK', 'alt': True}, None),
            ('view3d.rotate', {'type': 'RIGHTMOUSE', 'value': 'CLICK_DRAG'}, None),
            ('view3d.move', {'type': 'RIGHTMOUSE', 'value': 'PRESS', 'alt': True}, None),
            ('view3d.move', {'type': 'MIDDLEMOUSE', 'value': 'PRESS', 'alt': True}, None),
            ('view3d.zoom', {'type': 'RIGHTMOUSE', 'value': 'PRESS', 'ctrl': True}, None),
            ('view3d.zoom', {'type': 'RIGHTMOUSE', 'value': 'PRESS', 'alt': True}, None),

            ("bbrush.smooth", {'type': 'LEFTMOUSE', 'value': 'CLICK_DRAG', 'shift': True}, None),
            ("bbrush.click", {'type': 'LEFTMOUSE', 'value': 'CLICK', 'any': True}, None),
            ("bbrush.drag", {'type': 'LEFTMOUSE', 'value': 'CLICK_DRAG', 'any': True}, None),

            ("sculpt.brush_stroke", {'type': 'LEFTMOUSE', 'value': 'CLICK_DRAG', 'alt': True},
             {"properties": [("mode", "INVERT"), ]}),
            ("sculpt.brush_stroke", {'type': 'LEFTMOUSE', 'value': 'CLICK_DRAG', 'shift': True},
             {"properties": [("mode", "SMOOTH"), ]}),
            ("sculpt.brush_stroke", {'type': 'LEFTMOUSE', 'value': 'CLICK_DRAG'},
             {"properties": [("mode", "NORMAL"), ]}),

            ("sculpt.brush_stroke", {'type': 'LEFTMOUSE', 'value': 'CLICK_DRAG', "ctrl": True},
             {"properties": [("mode", "NORMAL"), ]}),
            ("sculpt.brush_stroke", {'type': 'LEFTMOUSE', 'value': 'CLICK_DRAG', "ctrl": True, 'alt': True},
             {"properties": [("mode", "INVERT"), ]}),

            *(item for item in sculpt_keymap[2]["items"] if
              item[0] not in ("sculpt.brush_stroke", "paint.mask_lasso_gesture"))
        ]
     }
     ),

    # Mask
    ("3D View Tool: Sculpt, Box Mask",
     {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
     {"items": [
         ("paint.mask_box_gesture", {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True, "alt": True},
          {"properties": [("value", 0.0), ], },),
         ("paint.mask_box_gesture", {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True},
          {"properties": [("value", 1.0), ], },),
     ], },),
    ("3D View Tool: Sculpt, Lasso Mask",
     {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
     {"items": [
         ("paint.mask_lasso_gesture",
          {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True, "alt": True},
          {"properties": [("value", 0), ], },),
         ("paint.mask_lasso_gesture",
          {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True},
          {"properties": [("value", 1), ], },),
     ], },),
    ("3D View Tool: Sculpt, Line Mask",
     {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
     {"items": [
         ("paint.mask_line_gesture", {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True, "alt": True},
          {"properties": [("value", 0), ], },),
         ("paint.mask_line_gesture", {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True},
          {"properties": [("value", 1), ], },),
     ], },),
    ("3D View Tool: Sculpt, Polyline Mask",
     {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
     {"items": [
         ("paint.mask_polyline_gesture", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True, "alt": True},
          {"properties": [("value", 0), ], },),
         ("paint.mask_polyline_gesture", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
          {"properties": [("value", 1), ], },),
     ], },),

    # Hide
    ("3D View Tool: Sculpt, Box Hide", {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
     {"items": [
         ("bbrush.click", {'type': 'LEFTMOUSE', 'value': 'CLICK', 'any': True}, None),
         ("paint.hide_show", {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True, "shift": True},
          {"properties": [("action", 'HIDE'), ], },),
         ("paint.hide_show", {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True, "shift": True, "alt": True},
          {"properties": [("action", 'SHOW'), ], },),
         ("paint.hide_show_all", {"type": 'LEFTMOUSE', "value": 'CLICK', "ctrl": True, "shift": True},
          {"properties": [("action", 'SHOW'), ], },),
     ], },),
    ("3D View Tool: Sculpt, Lasso Hide", {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
     {"items": [
         ("paint.hide_show_lasso_gesture", {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True, "shift": True},
          {"properties": [("action", 'HIDE'), ], },),
         ("paint.hide_show_lasso_gesture",
          {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True, "shift": True, "alt": True},
          {"properties": [("action", 'SHOW'), ], },),
         ("paint.hide_show_all", {"type": 'LEFTMOUSE', "value": 'CLICK', "ctrl": True, "shift": True},
          {"properties": [("action", 'SHOW'), ], },),
     ], },),
    ("3D View Tool: Sculpt, Line Hide", {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
     {"items": [
         ("paint.hide_show_line_gesture", {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True, "shift": True},
          {"properties": [("xstart", 0), ("action", 'HIDE'), ], },),
         ("paint.hide_show_line_gesture",
          {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True, "shift": True, "alt": True},
          {"properties": [("xstart", 0), ("action", 'SHOW'), ], },),
         ("paint.hide_show_all", {"type": 'LEFTMOUSE', "value": 'CLICK', "ctrl": True, "shift": True},
          {"properties": [("action", 'SHOW'), ], },),
     ], },),
    ("3D View Tool: Sculpt, Polyline Hide", {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
     {"items": [
         ("paint.hide_show_polyline_gesture", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True, "shift": True},
          {"properties": [("action", 'HIDE'), ("area", 'Inside'), ], },),
         ("paint.hide_show_polyline_gesture",
          {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True, "shift": True, "alt": True},
          {"properties": [("action", 'SHOW'), ("area", 'Inside'), ], },),
     ], },),

    # Trim
    ("3D View Tool: Sculpt, Box Trim", {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
     {"items": [
         ("sculpt.trim_box_gesture", {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "any": True},
          {"properties": [], },),
     ], },),
    ("3D View Tool: Sculpt, Lasso Trim", {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
     {"items": [
         ("sculpt.trim_lasso_gesture", {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "any": True},
          {"properties": [("smooth_stroke_factor", 1), ], },),
     ], },),
    ("3D View Tool: Sculpt, Line Trim", {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
     {"items": [
         ("sculpt.trim_line_gesture", {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "any": True},
          {"properties": [("xstart", 0), ], },),
     ], },),
    ("3D View Tool: Sculpt, Polyline Trim", {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
     {"items": [
         ("sculpt.trim_polyline_gesture", {"type": 'LEFTMOUSE', "value": 'PRESS', "any": True},
          {"properties": [], },),
     ], },),

    ("3D View Tool: Sculpt, Line Project", {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
     {"items": [
         ("sculpt.project_line_gesture", {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "any": True},
          {"properties": [], },),
     ], },),

    # TODO 视图切换
]

if __name__ == "__main__":
    # Only add keywords that are supported.
    from bpy.app import version as blender_version

    keywords = {}
    if blender_version >= (2, 92, 0):
        keywords["keyconfig_version"] = keyconfig_version
    import os
    from bl_keymap_utils.io import keyconfig_import_from_data

    keyconfig_import_from_data(
        os.path.splitext(os.path.basename(__file__))[0],
        keyconfig_data,
        **keywords,
    )
