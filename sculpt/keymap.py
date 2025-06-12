import os
import re
from os.path import dirname, join

import bpy

from ..debug import DEBUG_KEYMAP

brush_key_path = join(dirname(dirname(__file__)), "src", "key", "BBrush.py")

last_key_path = None


class BrushKeymap:
    preset_subdir = "keyconfig"

    @classmethod
    def get_key_preset_path(cls, name: str) -> "str|None":
        """
        scripts\modules\bpy_types.py
        """
        ext_valid = getattr(cls, "preset_extensions", {".py", ".xml"})

        filter_ext = lambda ext: ext.lower() in ext_valid
        searchpaths = bpy.utils.preset_paths(cls.preset_subdir)

        # collect paths
        files = []
        for directory in searchpaths:
            files.extend([
                (f, os.path.join(directory, f))
                for f in os.listdir(directory)
                if (not f.startswith("."))
                if ((filter_ext is None) or
                    (filter_ext(os.path.splitext(f)[1])))
            ])

        files.sort(
            key=lambda file_path:
            tuple(int(t) if t.isdigit() else t for t in re.split(r"(\d+)", file_path[0].lower())),
        )
        for (n, path) in files:
            if n[:-3] == name:
                return os.path.normpath(path)
        return None

    @classmethod
    def start_key(cls, context):
        """src/key/BBrush.py"""
        global last_key_path

        last_key = context.window_manager.keyconfigs.active.name
        last_key_path = cls.get_key_preset_path(last_key)
        if DEBUG_KEYMAP:
            print("start_key")
            print("last_key_path", last_key_path)
            print("brush_key_path", brush_key_path)
        bpy.ops.preferences.keyconfig_import("EXEC_DEFAULT", filepath=brush_key_path, keep_original=True)

    @staticmethod
    def restore_key(context):
        global last_key_path

        active_keyconfig = context.preferences.keymap.active_keyconfig
        if DEBUG_KEYMAP:
            print("restore_key", active_keyconfig, last_key_path)
        if active_keyconfig == "BBrush":
            bpy.ops.wm.keyconfig_preset_remove("EXEC_DEFAULT", name="BBrush", remove_name=True)
        if last_key_path:
            try:
                bpy.ops.preferences.keyconfig_activate("EXEC_DEFAULT", filepath=last_key_path)
                last_key_path = None
                if DEBUG_KEYMAP:
                    print("brush_key_path", brush_key_path)
                    print("active_keyconfig", context.window_manager.keyconfigs.active.name)
            except Exception as e:
                print("Error", e.args)


def try_restore_keymap():
    """在不是Bbrush模式时
    快捷键任未复位
    尝试修复"""
    context = bpy.context
    from ..utils import is_bbruse_mode
    if not is_bbruse_mode():
        if context.window_manager.keyconfigs.active.name == "BBrush":
            bpy.ops.wm.keyconfig_preset_remove("EXEC_DEFAULT", name="BBrush", remove_name=True)
            print("try_restore_keymap ok")
