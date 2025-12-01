from . import register_module

bl_info = {
    "name": "Bbrush",
    "author": "ACGGit Community(小萌新)",
    "version": (1, 4, 7),
    "blender": (4, 0, 0),
    "location": "Sculpt mode",
    "description": "Sculpting using only a pen and keyboard",
    "category": "AIGODLIKE"
}


def register():
    register_module.register()


def unregister():
    register_module.unregister()
