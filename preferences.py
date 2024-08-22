import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty
from bpy_types import AddonPreferences

from .utils import key
from .utils.public import PublicClass


class BBrushAddonPreferences(AddonPreferences, PublicClass):
    bl_idname = __package__
    use_mouse_emulate_3_button: BoolProperty()

    layout: bpy.types.UILayout

    def sculpt_update(self, context):
        from .ui.replace_ui import update_top_bar
        update_top_bar()
        inputs = context.preferences.inputs
        from .adapter import Brush
        if self.sculpt:
            Brush.normal_brush()
            self.use_mouse_emulate_3_button = inputs.use_mouse_emulate_3_button
            inputs.use_mouse_emulate_3_button = False
            key.register()
        else:
            Brush.restore_brush()
            inputs.use_mouse_emulate_3_button = self.use_mouse_emulate_3_button
            key.unregister()
        self.tag_all_redraw(context)

    sculpt: BoolProperty(name='Bbrush',
                         default=False,
                         options={'SKIP_SAVE'},
                         update=sculpt_update)

    show_text: BoolProperty(name='Display top text', default=False)

    depth_display_items = (
        ('ALWAYS_DISPLAY', 'DisplayedAllTheTime',
         'Keep the silhouette displayed all the time, even when not in sculpting mode'),
        ('ONLY_SCULPT', 'SculptModeOnly', 'Display silhouette images only in sculpting mode'),
        ('ONLY_BBRUSH', 'BbrushModeOnly', 'Display silhouette images only in Bbrush mode'),
        ('NOT_DISPLAY', 'NotShown', 'Never display silhouette images at any time'),
    )

    depth_display_mode: EnumProperty(name='Silhouette Display Mode',
                                     default='ONLY_SCULPT',
                                     items=depth_display_items)
    depth_scale: FloatProperty(name='Silhouette image scaling',
                               default=0.3,
                               max=2,
                               min=0.1,
                               step=0.1
                               )
    depth_offset_x: IntProperty(
        name='Silhouette image offset X',
        default=0, max=114514, min=0)
    depth_offset_y: IntProperty(
        name='Silhouette image offset Y',
        default=80, max=114514, min=0)

    always_use_sculpt_mode: BoolProperty(
        name='Always use Bbrush sculpting mode',
        description=
        'If entering sculpting mode, Bbrush mode will automatically activate; if exiting sculpting mode, Bbrush mode will deactivate',
        default=False)

    depth_ray_size: IntProperty(
        name='Depth ray check size(px)',
        description="Check if the mouse is placed over the model, mouse cursor's range size", default=100, min=10,
        max=300)

    show_shortcut_keys: BoolProperty(
        name='Display shortcut keys',
        default=True
    )
    shortcut_offset_x: IntProperty(
        name='Shortcut key offset X',
        default=20, max=114514, min=0)
    shortcut_offset_y: IntProperty(
        name='Shortcut key offset Y',
        default=20, max=114514, min=0)
    shortcut_show_size: FloatProperty(name='Shortcut key display size', min=0.1, default=1, max=114)

    def __update_top__(self, context):
        from .ui.replace_ui import update_top_bar
        update_top_bar()

    replace_top_bar: BoolProperty(name='Replace top bar', default=True, update=__update_top__)
    alignment: EnumProperty(
        items=[
            ("LEFT", "LIFT", ""),
            ("CENTER", "CENTER", ""),
            ("RIGHT", "RIGHT", ""),
        ],
        default="LEFT",
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.prop(self, 'always_use_sculpt_mode')
        row = box.row(align=True)
        row.prop(self, 'depth_display_mode')
        row.prop(self, 'depth_ray_size')
        layout.separator()
        layout.label(text="Top bar")
        row = layout.box().row(align=True)
        row.prop(self, 'show_text')
        row.prop(self, 'replace_top_bar')
        row.prop(self, 'alignment')

        layout.separator()
        layout.label(text='Silhouette')
        box = layout.box()
        box.prop(self, 'depth_scale')
        row = box.row(align=True)
        row.prop(self, 'depth_offset_x')
        row.prop(self, 'depth_offset_y')

        layout.separator()
        layout.label(text='Shortcut')
        box = layout.box()
        box.prop(self, 'show_shortcut_keys')
        box.prop(self, 'shortcut_show_size')
        row = box.row(align=True)
        row.prop(self, 'shortcut_offset_x')
        row.prop(self, 'shortcut_offset_y')


def register():
    bpy.utils.register_class(BBrushAddonPreferences)


def unregister():
    bpy.utils.unregister_class(BBrushAddonPreferences)
    key.unregister()
