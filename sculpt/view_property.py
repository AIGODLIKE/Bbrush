import bpy

from ..debug import DEBUG_VIEW_PREF
from ..utils import get_pref

property_items = {
    "inputs": [
        "view_rotate_method",
        "view_rotate_sensitivity_turntable",
        "view_rotate_sensitivity_trackball",
        "use_rotate_around_active",
        "use_auto_perspective",
        "use_mouse_depth_navigate",
    ],
    "view": [
        "smooth_view",
        "rotation_angle",
    ]
}

view_property_store = {}


class ViewProperty:
    """Temporarily apply Bbrush navigation prefs to Blender user preferences."""

    @staticmethod
    def start_view_property(context):
        global view_property_store
        pref = get_pref()
        if pref is None:
            return
        if pref.use_navigation_property:
            store = {}
            for p, v in property_items.items():
                prop = getattr(context.preferences, p)
                data = {}
                for i in v:
                    data[i] = getattr(prop, i)

                    value = getattr(pref, i)  # Bbrush pref value
                    setattr(prop, i, value)
                store[p] = data
            view_property_store = store
        if DEBUG_VIEW_PREF:
            print("start_view_property", pref.use_navigation_property, view_property_store)

    @staticmethod
    def restore_view_property(context, save_user_pref=False):
        global view_property_store
        pref = get_pref()
        if pref is not None and pref.use_navigation_property:
            for p, data in view_property_store.items():
                prop = getattr(context.preferences, p)
                for k, v in data.items():
                    setattr(prop, k, v)

        if DEBUG_VIEW_PREF and pref is not None:
            store = {}
            for p, v in property_items.items():
                prop = getattr(context.preferences, p)
                data = {}
                for i in v:
                    data[i] = getattr(prop, i)
                store[p] = data
            print("restore_view_property", pref.use_navigation_property, view_property_store)
            print("now pref", store)

        view_property_store.clear()
        if save_user_pref:
            bpy.ops.wm.save_userpref()
