import os
import re
from os.path import dirname, join

import bpy

brush_key_path = join(dirname(dirname(__file__)), "src", "key", "BBrush.py")


class BrushKey:
    last_key_path = None

    preset_subdir = "keyconfig"
    preset_operator = "preferences.keyconfig_activate"

    def start_key(self, context):
        """src/key/BBrush.py"""
        last_key = context.window_manager.keyconfigs.active.name
        self.last_key_path = self.get_key_preset_path(last_key)
        print("last_key_path", self.last_key_path)
        bpy.ops.preferences.keyconfig_import("EXEC_DEFAULT", filepath=brush_key_path, keep_original=True)

    def restore_key(self, context):
        bpy.ops.wm.keyconfig_preset_remove("EXEC_DEFAULT", name="BBrush", remove_name=True)
        if self.last_key_path:
            try:
                bpy.ops.preferences.keyconfig_activate("EXEC_DEFAULT", filepath=self.last_key_path)
            except Exception as e:
                print("Error", e.args)
        else:
            print("未找到 last_key path")

    def get_key_preset_path(self, name: str) -> "str|None":
        ext_valid = getattr(self, "preset_extensions", {".py", ".xml"})

        filter_ext = lambda ext: ext.lower() in ext_valid
        filter_path = None
        searchpaths = bpy.utils.preset_paths(self.preset_subdir)

        # collect paths
        files = []
        for directory in searchpaths:
            files.extend([
                (f, os.path.join(directory, f))
                for f in os.listdir(directory)
                if (not f.startswith("."))
                if ((filter_ext is None) or
                    (filter_ext(os.path.splitext(f)[1])))
                if ((filter_path is None) or
                    (filter_path(f)))
            ])

        # Perform a "natural sort", so 20 comes after 3 (for example).
        files.sort(
            key=lambda file_path:
            tuple(int(t) if t.isdigit() else t for t in re.split(r"(\d+)", file_path[0].lower())),
        )
        for (n, path) in files:
            if n[:-3] == name:
                return os.path.normpath(path)
        return None
