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
