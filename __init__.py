from .utils import reg

bl_info = {
    "name": "Bbrush",
    "author": "AIGODLIKE Community(BlenderCN辣椒,小萌新)",
    "version": (1, 1, 0),
    "blender": (3, 4, 0),
    "location": "进入雕刻模式将会在顶栏显示",
    "description": "",
    "warning": "",
    "category": "3D View"
}


def register():
    reg.register()


def unregister():
    reg.unregister()
