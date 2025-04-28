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
    ("Window", {"space_type": 'EMPTY', "region_type": 'WINDOW'},
     {"items":
         [
         ], },),

    ("View3D Rotate Modal", {'space_type': 'EMPTY', 'region_type': 'WINDOW'}, {"items": []}),

    ("Sculpt", {'space_type': 'EMPTY', 'region_type': 'WINDOW'}, {
        "items": [
            ('object.transfer_mode', {'type': 'LEFTMOUSE', 'value': 'CLICK', 'alt': True}, None),
            ('view3d.rotate', {'type': 'RIGHTMOUSE', 'value': 'CLICK_DRAG'}, None),
            ('view3d.move', {'type': 'RIGHTMOUSE', 'value': 'PRESS', 'alt': True}, None),
            ('view3d.move', {'type': 'MIDDLEMOUSE', 'value': 'PRESS', 'alt': True}, None),
            ('view3d.zoom', {'type': 'RIGHTMOUSE', 'value': 'PRESS', 'ctrl': True}, None),
            ('view3d.zoom', {'type': 'RIGHTMOUSE', 'value': 'PRESS', 'alt': True}, None),

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

            *(item
              for item in sculpt_keymap[2]["items"] if item[0] not in ("sculpt.brush_stroke",)
              )
            # *_template_items_object_subdivision_set()

            # # Expand
            # ("sculpt.expand", {"type": 'A', "value": 'PRESS', "shift": True},
            #  {"properties": [
            #      ("target", "MASK"),
            #      ("falloff_type", "GEODESIC"),
            #      ("invert", False),
            #      ("use_auto_mask", False),
            #      ("use_mask_preserve", True),
            #  ]}),
            # ("sculpt.expand", {"type": 'A', "value": 'PRESS', "shift": True, "alt": True},
            #  {"properties": [
            #      ("target", "MASK"),
            #      ("falloff_type", "NORMALS"),
            #      ("invert", False),
            #      ("use_mask_preserve", True),
            #  ]}),
            # ("sculpt.expand", {"type": 'W', "value": 'PRESS', "shift": True},
            #  {"properties": [
            #      ("target", "FACE_SETS"),
            #      ("falloff_type", "GEODESIC"),
            #      ("invert", False),
            #      ("use_mask_preserve", False),
            #      ("use_modify_active", False),
            #  ]}),
            # ("sculpt.expand", {"type": 'W', "value": 'PRESS', "shift": True, "alt": True},
            #  {"properties": [
            #      ("target", "FACE_SETS"),
            #      ("falloff_type", "BOUNDARY_FACE_SET"),
            #      ("invert", False),
            #      ("use_mask_preserve", False),
            #      ("use_modify_active", True),
            #  ]}),
            # # Partial Visibility Show/hide
            # # Match keys from: `_template_items_hide_reveal_actions`, cannot use because arguments aren't compatible.
            # ("sculpt.face_set_change_visibility", {"type": 'H', "value": 'PRESS', "shift": True},
            #  {"properties": [("mode", 'TOGGLE')]}),
            # ("sculpt.face_set_change_visibility", {"type": 'H', "value": 'PRESS'},
            #  {"properties": [("mode", 'HIDE_ACTIVE')]}),
            # ("paint.hide_show_all", {"type": 'H', "value": 'PRESS', "alt": True},
            #  {"properties": [("action", "SHOW")]}),
            # ("paint.visibility_filter", {"type": 'PAGE_UP', "value": 'PRESS', "repeat": True},
            #  {"properties": [("action", 'GROW')]}),
            # ("paint.visibility_filter", {"type": 'PAGE_DOWN', "value": 'PRESS', "repeat": True},
            #  {"properties": [("action", 'SHRINK')]}),
            # ("sculpt.face_set_edit", {"type": 'W', "value": 'PRESS', "ctrl": True},
            #  {"properties": [("mode", 'GROW')]}),
            # ("sculpt.face_set_edit", {"type": 'W', "value": 'PRESS', "ctrl": True, "alt": True},
            #  {"properties": [("mode", 'SHRINK')]}),
            # # Subdivision levels
            # *_template_items_object_subdivision_set(),
            # ("object.subdivision_set", {"type": 'ONE', "value": 'PRESS', "alt": True, "repeat": True},
            #  {"properties": [("level", -1), ("relative", True)]}),
            # ("object.subdivision_set", {"type": 'TWO', "value": 'PRESS', "alt": True, "repeat": True},
            #  {"properties": [("level", 1), ("relative", True)]}),
            # # Mask
            # ("paint.mask_flood_fill", {"type": 'M', "value": 'PRESS', "alt": True},
            #  {"properties": [("mode", 'VALUE'), ("value", 0.0)]}),
            # ("paint.mask_flood_fill", {"type": 'I', "value": 'PRESS', "ctrl": True},
            #  {"properties": [("mode", 'INVERT')]}),
            # ("paint.mask_box_gesture", {"type": 'B', "value": 'PRESS'},
            #  {"properties": [("mode", 'VALUE'), ("value", 0.0)]}),
            # # Dynamic topology
            # ("sculpt.dyntopo_detail_size_edit", {"type": 'R', "value": 'PRESS'}, None),
            # ("sculpt.detail_flood_fill", {"type": 'R', "value": 'PRESS', "ctrl": True}, None),
            # # Remesh
            # ("object.voxel_remesh", {"type": 'R', "value": 'PRESS', "ctrl": True}, None),
            # ("object.voxel_size_edit", {"type": 'R', "value": 'PRESS'}, None),
            # # Color
            # ("sculpt.sample_color", {"type": 'X', "value": 'PRESS', "shift": True}, None),
            # ("paint.brush_colors_flip", {"type": 'X', "value": 'PRESS', }, None),
            # # Brush properties
            # ("brush.scale_size", {"type": 'LEFT_BRACKET', "value": 'PRESS', "repeat": True},
            #  {"properties": [("scalar", 0.9)]}),
            # ("brush.scale_size", {"type": 'RIGHT_BRACKET', "value": 'PRESS', "repeat": True},
            #  {"properties": [("scalar", 1.0 / 0.9)]}),
            #
            # *_template_paint_radial_control("sculpt", rotation=True),
            # # Stencil
            # ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS'},
            #  {"properties": [("mode", 'TRANSLATION')]}),
            # ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True},
            #  {"properties": [("mode", 'SCALE')]}),
            # ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "ctrl": True},
            #  {"properties": [("mode", 'ROTATION')]}),
            # ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "alt": True},
            #  {"properties": [("mode", 'TRANSLATION'), ("texmode", 'SECONDARY')]}),
            # ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True, "alt": True},
            #  {"properties": [("mode", 'SCALE'), ("texmode", 'SECONDARY')]}),
            # ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "ctrl": True, "alt": True},
            #  {"properties": [("mode", 'ROTATION'), ("texmode", 'SECONDARY')]}),
            # # Sculpt Session Pivot Point
            # ("sculpt.set_pivot_position", {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True},
            #  {"properties": [("mode", 'SURFACE')]}),
            # # Menus
            # ("wm.context_menu_enum", {"type": 'E', "value": 'PRESS', "alt": True},
            #  {"properties": [("data_path", "tool_settings.sculpt.brush.stroke_method")]}),
            # ("wm.context_toggle", {"type": 'S', "value": 'PRESS', "shift": True},
            #  {"properties": [("data_path", "tool_settings.sculpt.brush.use_smooth_stroke")]}),
            # op_menu_pie("VIEW3D_MT_sculpt_mask_edit_pie", {"type": 'A', "value": 'PRESS'}),
            # op_menu_pie("VIEW3D_MT_sculpt_automasking_pie", {"type": 'A', "alt": True, "value": 'PRESS'}),
            # op_menu_pie("VIEW3D_MT_sculpt_face_sets_edit_pie", {"type": 'W', "value": 'PRESS', "alt": True}),
            # *_template_items_context_panel("VIEW3D_PT_sculpt_context_menu", params.context_menu_event),
            # # Brushes
            # ("brush.asset_activate", {"type": 'V', "value": 'PRESS'},
            #  {"properties": [
            #      ("asset_library_type", 'ESSENTIALS'),
            #      ("relative_asset_identifier", "brushes/essentials_brushes-mesh_sculpt.blend/Brush/Draw"),
            #  ]}),
            # ("brush.asset_activate", {"type": 'S', "value": 'PRESS'},
            #  {"properties": [
            #      ("asset_library_type", 'ESSENTIALS'),
            #      ("relative_asset_identifier", "brushes/essentials_brushes-mesh_sculpt.blend/Brush/Smooth"),
            #  ]}),
            # ("brush.asset_activate", {"type": 'P', "value": 'PRESS'},
            #  {"properties": [
            #      ("asset_library_type", 'ESSENTIALS'),
            #      ("relative_asset_identifier", "brushes/essentials_brushes-mesh_sculpt.blend/Brush/Pinch/Magnify"),
            #  ]}),
            # ("brush.asset_activate", {"type": 'I', "value": 'PRESS'},
            #  {"properties": [
            #      ("asset_library_type", 'ESSENTIALS'),
            #      ("relative_asset_identifier", "brushes/essentials_brushes-mesh_sculpt.blend/Brush/Inflate/Deflate"),
            #  ]}),
            # ("brush.asset_activate", {"type": 'G', "value": 'PRESS'},
            #  {"properties": [
            #      ("asset_library_type", 'ESSENTIALS'),
            #      ("relative_asset_identifier", "brushes/essentials_brushes-mesh_sculpt.blend/Brush/Grab"),
            #  ]}),
            # ("brush.asset_activate", {"type": 'T', "value": 'PRESS', "shift": True},
            #  {"properties": [
            #      ("asset_library_type", 'ESSENTIALS'),
            #      ("relative_asset_identifier", "brushes/essentials_brushes-mesh_sculpt.blend/Brush/Scrape/Fill"),
            #  ]}),
            # ("brush.asset_activate", {"type": 'C', "value": 'PRESS'},
            #  {"properties": [
            #      ("asset_library_type", 'ESSENTIALS'),
            #      ("relative_asset_identifier", "brushes/essentials_brushes-mesh_sculpt.blend/Brush/Clay Strips"),
            #  ]}),
            # ("brush.asset_activate", {"type": 'C', "value": 'PRESS', "shift": True},
            #  {"properties": [
            #      ("asset_library_type", 'ESSENTIALS'),
            #      ("relative_asset_identifier", "brushes/essentials_brushes-mesh_sculpt.blend/Brush/Crease Polish"),
            #  ]}),
            # ("brush.asset_activate", {"type": 'K', "value": 'PRESS'},
            #  {"properties": [
            #      ("asset_library_type", 'ESSENTIALS'),
            #      ("relative_asset_identifier", "brushes/essentials_brushes-mesh_sculpt.blend/Brush/Snake Hook"),
            #  ]}),
            # ("brush.asset_activate", {"type": 'M', "value": 'PRESS'},
            #  {"properties": [
            #      ("asset_library_type", 'ESSENTIALS'),
            #      ("relative_asset_identifier", "brushes/essentials_brushes-mesh_sculpt.blend/Brush/Mask"),
            #  ]}),
            # # *_template_asset_shelf_popup("VIEW3D_AST_brush_sculpt", params.spacebar_action),
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
