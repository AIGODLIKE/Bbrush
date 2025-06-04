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


class ViewProperty:
    """
    preferences/view.py
    """
    view_property_store = None

    def start_view_property(self, context):
        pref = get_pref()
        store = {}
        for p, v in property_items.items():
            prop = getattr(context.preferences, p)
            data = {}
            for i in v:
                data[i] = getattr(prop, i)

                value = getattr(pref, i)  # Bbrush pref value
                setattr(prop, i, value)
            store[p] = data
        self.view_property_store = store

    def restore_view_property(self, context):
        for p, data in self.view_property_store.items():
            prop = getattr(context.preferences, p)
            for k, v in data.items():
                setattr(prop, k, v)
        self.view_property_store = None
