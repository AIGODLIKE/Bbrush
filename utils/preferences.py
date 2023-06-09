import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty
from bpy_types import AddonPreferences

from .public import ADDON_NAME, PublicClass
from . import key


class BBrushAddonPreferences(AddonPreferences, PublicClass):
    bl_idname = ADDON_NAME
    use_mouse_emulate_3_button: BoolProperty()

    layout: bpy.types.UILayout

    def sculpt_update(self, context):
        from ..ui.replace_ui import update_top_bar
        update_top_bar()
        inputs = context.preferences.inputs
        from .bbrush_toolbar import BrushTool
        if self.sculpt:
            BrushTool.toolbar_switch('SCULPT')
            self.use_mouse_emulate_3_button = inputs.use_mouse_emulate_3_button
            inputs.use_mouse_emulate_3_button = False
            key.register()
        else:
            BrushTool.toolbar_switch('ORIGINAL_TOOLBAR')
            inputs.use_mouse_emulate_3_button = self.use_mouse_emulate_3_button
            key.unregister()
        self.tag_all_redraw(context)

    sculpt: BoolProperty(name='Bbrush',
                         default=False,
                         options={'SKIP_SAVE'},
                         update=sculpt_update)

    depth_display_items = (
        ('ALWAYS_DISPLAY', '一直显示', '一直保持显示剪影图,即使不在雕刻模式'),
        ('ONLY_SCULPT', '仅雕刻模式', '仅在雕刻模式显示剪影图'),
        ('ONLY_BBRUSH', '仅Bbrush模式', '仅在Bbrush模式时,显示剪影图'),
        ('NOT_DISPLAY', '不显示', '任何时候都不显示剪影图'),
    )

    depth_display_mode: EnumProperty(name='剪影图显示模式',
                                     default='ONLY_SCULPT',
                                     items=depth_display_items)
    depth_scale: FloatProperty(name='剪影图缩放',
                               default=0.3,
                               max=2,
                               min=0.1,
                               step=0.1
                               )

    always_use_sculpt_mode: BoolProperty(
        name='始终使用Bbrush雕刻模式',
        description='如果进入雕刻模式则自动开启Bbrush模式,退出雕刻模式则退出Bbrush模式',
        default=False)

    depth_ray_size: IntProperty(
        name='深度射线检查大小(px)',
        description='检查鼠标是否放在模型上,鼠标范围大小', default=100, min=10,
        max=300)

    show_shortcut_keys: BoolProperty(
        name='显示快捷键',
        default=True
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'depth_display_mode')
        layout.prop(self, 'depth_scale')
        layout.prop(self, 'depth_ray_size')
        layout.prop(self, 'always_use_sculpt_mode')


def register():
    bpy.utils.register_class(BBrushAddonPreferences)


def unregister():
    bpy.utils.unregister_class(BBrushAddonPreferences)
    key.unregister()
