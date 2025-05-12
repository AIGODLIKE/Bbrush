from . import register_module

bl_info = {
    "name": "Bbrush",
    "author": "AIGODLIKE Community：小萌新",
    "version": (1, 3, 0),
    "blender": (4, 0, 0),
    "location": "Entering the sculpt mode will be displayed in the top bar",
    "description": "",
    "category": "AIGODLIKE"
}


def register():
    register_module.register()


def unregister():
    register_module.unregister()
