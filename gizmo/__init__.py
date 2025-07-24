from . import navigation
from . import view_navigation_gizmo


def register():
    navigation.register()
    view_navigation_gizmo.register()


def unregister():
    navigation.unregister()
    view_navigation_gizmo.unregister()
