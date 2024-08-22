import bpy

from .utils import reg

bl_info = {
    "name": "Bbrush",
    "author": "AIGODLIKE Community：小萌新",
    "version": (1, 2, 8),
    "blender": (4, 0, 0),
    "location": "Entering the sculpt mode will be displayed in the top bar",
    "description": "",
    "category": "AIGODLIKE"
}



def register():
    reg.register()


def unregister():
    reg.unregister()
