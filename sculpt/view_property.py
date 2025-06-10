from ..utils import get_pref

property_items = {
    "inputs": [
        "view_rotate_method",
        "view_rotate_sensitivity_turntable",
        "view_rotate_sensitivity_turntable",
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
    """
    preferences/view.py
    """

    @staticmethod
    def start_view_property(context):
        global view_property_store
        pref = get_pref()
        if pref.use_view:
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

    @staticmethod
    def restore_view_property(context):
        global view_property_store
        if get_pref().use_view:
            for p, data in view_property_store.items():
                prop = getattr(context.preferences, p)
                for k, v in data.items():
                    setattr(prop, k, v)
        view_property_store.clear()
