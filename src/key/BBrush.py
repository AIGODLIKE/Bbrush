keyconfig_version = (4, 4, 32)
keyconfig_data = [
    ("Window", {"space_type": 'EMPTY', "region_type": 'WINDOW'},
     {"items":
         [
             ("wm.call_menu_pie", {"type": 'S', "value": 'PRESS', "ctrl": True},
              {"properties": [("name", 'MP7_TOOLS_MT_SAVE'), ], },
              ),
             ("wm.context_toggle",
              {"type": 'M', "value": 'PRESS', "shift": True, "ctrl": True, "alt": True},
              {"properties":
                   [("data_path",
                     "preferences.addons['bl_ext.user_default.development_kit'].preferences.activate_ui_info"),
                    ],
               },
              ),
             ("wm.context_toggle",
              {"type": 'RIGHTMOUSE', "value": 'PRESS', "ctrl": True, "alt": True},
              {"properties":
                   [("data_path", 'preferences.view.use_translate_interface'),
                    ],
               },
              ),
             ("wm.save_homefile", {"type": 'ACCENT_GRAVE', "value": 'PRESS', "ctrl": True, "alt": True},
              None),
             ("wm.console_toggle", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "ctrl": True, "alt": True},
              None),
         ],
     },
     ),

    ("View3D Rotate Modal", {'space_type': 'EMPTY', 'region_type': 'WINDOW'},
     {"items": [
     ]}
     ),

    ("Sculpt", {'space_type': 'EMPTY', 'region_type': 'WINDOW'},
     {
         "items": [
             ('object.transfer_mode', {'type': 'LEFTMOUSE', 'value': 'CLICK', 'alt': True}, None),
             ('view3d.rotate', {'type': 'RIGHTMOUSE', 'value': 'CLICK_DRAG'}, None),
             ('view3d.move', {'type': 'RIGHTMOUSE', 'value': 'PRESS', 'alt': True}, None),
             ('view3d.move', {'type': 'MIDDLEMOUSE', 'value': 'PRESS', 'alt': True}, None),
             ('view3d.zoom', {'type': 'RIGHTMOUSE', 'value': 'PRESS', 'ctrl': True}, None),
             ('view3d.zoom', {'type': 'RIGHTMOUSE', 'value': 'PRESS', 'alt': True}, None),

             ("sculpt.brush_stroke", {'type': 'LEFTMOUSE', 'value': 'PRESS', 'alt': True},
              {"properties": [("mode", "INVERT"), ]}),
             ("sculpt.brush_stroke", {'type': 'LEFTMOUSE', 'value': 'PRESS', 'shift': True},
              {"properties": [("mode", "SMOOTH"), ]}),
             ("sculpt.brush_stroke", {'type': 'LEFTMOUSE', 'value': 'PRESS'}, {"properties": [("mode", "NORMAL"), ]}),

             ("sculpt.brush_stroke", {'type': 'LEFTMOUSE', 'value': 'PRESS', "ctrl": True},
              {"properties": [("mode", "NORMAL"), ]}),
             ("sculpt.brush_stroke", {'type': 'LEFTMOUSE', 'value': 'PRESS', 'alt': True, "ctrl": True},
              {"properties": [("mode", "INVERT"), ]}),
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
          {"properties": [("ymin", 2), ("value", 1.0), ], },),
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
          {"properties": [("smooth_stroke_factor", 0.75), ], },),
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
