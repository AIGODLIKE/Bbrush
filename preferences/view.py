import bpy

from ..utils import get_property_rna_info


def get_input_property_info(x):
    return get_property_rna_info(bpy.types.PreferencesInput.bl_rna, x)


def get_view_property_info(x):
    return get_property_rna_info(bpy.types.PreferencesView.bl_rna, x)


class View:
    use_view: bpy.props.BoolProperty(name="Use view pref", default=True)
    view_rotate_method: bpy.props.EnumProperty(
        **{**get_input_property_info("view_rotate_method"), "default": "TRACKBALL"})
    view_rotate_sensitivity_turntable: bpy.props.FloatProperty(
        **get_input_property_info("view_rotate_sensitivity_turntable"))
    view_rotate_sensitivity_trackball: bpy.props.FloatProperty(
        **get_input_property_info("view_rotate_sensitivity_trackball"))
    use_rotate_around_active: bpy.props.BoolProperty(**get_input_property_info("use_rotate_around_active"))
    use_auto_perspective: bpy.props.BoolProperty(**get_input_property_info("use_auto_perspective"))
    use_mouse_depth_navigate: bpy.props.BoolProperty(**get_input_property_info("use_mouse_depth_navigate"))

    smooth_view: bpy.props.IntProperty(**get_view_property_info("smooth_view"))
    rotation_angle: bpy.props.FloatProperty(**get_view_property_info("rotation_angle"))

    def draw_view(self, layout):

        box = layout.column().box()
        box.prop(self, "use_view")
        
        box = box.column()
        box.active = self.use_view

        box.label(text="View")

        box.row().prop(self, "view_rotate_method", expand=True)
        if self.view_rotate_method == 'TURNTABLE':
            box.prop(self, "view_rotate_sensitivity_turntable")
        else:
            box.prop(self, "view_rotate_sensitivity_trackball")
        box.prop(self, "use_rotate_around_active")

        box.separator()

        col = box.column(heading="Auto")
        col.prop(self, "use_auto_perspective", text="Perspective")
        col.prop(self, "use_mouse_depth_navigate", text="Depth")

        col = box.column()
        col.prop(self, "smooth_view")
        col.prop(self, "rotation_angle")

        box.label(text="View preferences used when entering Bbrush mode")
