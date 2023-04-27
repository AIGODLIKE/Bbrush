import bpy
from bl_ui.properties_paint_common import UnifiedPaintPanel
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper

from ..utils.bbrush_toolbar import BrushTool
from ..utils.log import log
from ..utils.public import PublicOperator


class SwitchProperty(PublicOperator):
    is_esc = False

    @property
    def is_smoot_mode(self):
        return self.only_shift or self.shift_alt

    @property
    def is_mask_mode(self):
        return self.only_ctrl or self.ctrl_alt

    @property
    def is_hide_mode(self):
        return self.ctrl_shift or self.ctrl_shift_alt

    @property
    def is_exit(self):
        return (self.event.type in ('ESC', 'SPACE')) or self.not_key or self.is_esc

    @property
    def is_pass(self):
        space = self.event_is_space
        return (self.only_ctrl and self.event_is_tab) or \
            (space and self.ctrl_alt) or \
            (space and self.only_alt) or \
            (space and self.only_ctrl)

    @property
    def brushes(self):
        return ToolSelectPanelHelper._tool_class_from_space_type('VIEW_3D')._tools['SCULPT']

    @brushes.setter
    def _set_brushes(self, value):
        ToolSelectPanelHelper._tool_class_from_space_type('VIEW_3D')._tools['SCULPT'] = value

    @staticmethod
    def B_brushes(key):
        return BrushTool.TOOLBAR_Dit[key]

    @property
    def _hide_brushes(self):
        return self.B_brushes('HIDE')

    @property
    def _mask_brushes(self):
        return self.B_brushes('MASK')

    @property
    def _sculpt_brushes(self):
        return self.B_brushes('SCULPT')

    @property
    def active_hide_brush(self):
        return BrushTool.active_brush['HIDE']

    @staticmethod
    def set_hide_brush(value):
        BrushTool.active_brush['HIDE'] = value

    @property
    def active_mask_brush(self):
        return BrushTool.active_brush['MASK']

    @staticmethod
    def set_mask_brush(value):
        BrushTool.active_brush['MASK'] = value

    @property
    def active_sculpt_brush(self):
        return BrushTool.active_brush['SCULPT']

    @staticmethod
    def set_sculpt_brush(value):
        BrushTool.active_brush['SCULPT'] = value

    @property
    def active_not_in_active_brushes(self):  # 活动笔刷没在几个活动项里面
        return self.active_tool_name and self.active_tool_name != self.active_sculpt_brush and (
                self.active_tool_name not in BrushTool.active_brush.values())

    @property
    def is_change_brush(self):
        return self.active_not_in_active_brushes

    @property
    def mouse_is_in_model_up(self):
        return self.get_mouse_location_ray_cast(self.context, self.event)


class BBrushSwitch(SwitchProperty):
    bl_idname = 'bbrush.bbrush_switch'
    bl_label = '笔刷模式切换'
    bl_description = '切换笔刷内容,每个键的列表，有[雕刻,遮罩,隐藏]三个功能'

    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        self.init_invoke(context, event)
        log.debug(self.bl_idname)

        if self.is_3d_view:
            if self.is_change_brush:
                self.set_sculpt_brush(self.active_tool_name)
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}

    def modal(self, context, event):
        self.init_modal(context, event)
        self.update_shortcut_keys()

        if self.is_exit:
            self.set_shortcut_keys('NORMAL')
            return self.exit(context, event)
        elif self.is_pass:  # ctrl tab切换模式
            self.is_esc = True
            return {'PASS_THROUGH'}
        elif self.is_hide_mode:
            self.hide_mode()
        elif self.is_mask_mode:
            self.mask_mode()
        else:
            self.set_shortcut_keys('NORMAL')

        self.tag_redraw(context)  # 进行重绘，避免更改工具栏后内容还是旧的
        return self.event_ops(event)

    def event_ops(self, event):
        press = self.event_is_press
        if self.only_shift:
            setattr(self, '_tmp_brush', self.active_tool_name)
            bpy.ops.wm.tool_set_by_id(name="builtin_brush.Smooth")
        elif getattr(self, '_tmp_brush', False):
            bpy.ops.wm.tool_set_by_id(name=self._tmp_brush)
            delattr(self, '_tmp_brush')

        if press:
            if event.type == 'NUMPAD_PLUS':
                bpy.ops.sculpt.mask_filter('INVOKE_DEFAULT',
                                           filter_type='GROW',
                                           auto_iteration_count=True)
            elif event.type == 'NUMPAD_MINUS':
                bpy.ops.sculpt.mask_filter('INVOKE_DEFAULT',
                                           filter_type='SHRINK',
                                           auto_iteration_count=True)
            elif event.type in ('UP_ARROW', 'NUMPAD_ASTERIX'):
                bpy.ops.sculpt.mask_filter('INVOKE_DEFAULT',
                                           filter_type='CONTRAST_INCREASE',
                                           auto_iteration_count=False)
            elif event.type in ('DOWN_ARROW', 'NUMPAD_SLASH'):
                bpy.ops.sculpt.mask_filter('INVOKE_DEFAULT',
                                           filter_type='CONTRAST_DECREASE',
                                           auto_iteration_count=False)

        if self.is_smoot_mode:
            return self.smoot_mode()
        elif self.event_is_w and self.only_ctrl and press:
            bpy.ops.sculpt.face_sets_create('INVOKE_DEFAULT', mode='MASKED')
            bpy.ops.paint.mask_flood_fill(
                'INVOKE_DEFAULT', mode='VALUE', value=0)
            return {'RUNNING_MODAL'}
        return {'PASS_THROUGH'}

    def exit(self, context, event):
        BrushTool.toolbar_switch('SCULPT')
        if self.is_sculpt_mode:
            bpy.ops.wm.tool_set_by_id(name=BrushTool.active_brush['SCULPT'])

        if not self.active_tool:
            BrushTool.init_active_brush()

        # 闪退，原因未知
        self.tag_redraw(context)
        self.handler_remove()
        log.debug(BrushTool.active_brush)
        log.debug('exit BBrushSwitch \n')
        return {'FINISHED'}

    def hide_mode(self):
        if self.brushes != self._hide_brushes:
            BrushTool.toolbar_switch('HIDE')
            bpy.ops.wm.tool_set_by_id(name=BrushTool.active_brush['HIDE'])
        elif self.is_change_brush:
            self.set_hide_brush(self.active_tool_name)

    def mask_mode(self):
        if self.brushes != self._mask_brushes:
            BrushTool.toolbar_switch('MASK')
            bpy.ops.wm.tool_set_by_id(name=self.active_mask_brush)
        elif self.is_change_brush:
            self.set_mask_brush(self.active_tool_name)

    def smoot_mode(self):
        shift_ops = self.only_shift and not self.event_is_left

        if self.event_is_left and not self.mouse_is_in_model_up:
            bpy.ops.view3d.view_roll('INVOKE_DEFAULT', type='ANGLE')
            return {'PASS_THROUGH'}
        elif self.event_is_f or self.event_is_r or shift_ops:
            return {'PASS_THROUGH'}
        elif self.event_left_mouse_press:
            return self.switch_shift()
        elif self.event_key_middlemouse:
            bpy.ops.view3d.move('INVOKE_DEFAULT')
        return {'RUNNING_MODAL'}

    def switch_shift(self):
        settings = UnifiedPaintPanel.paint_settings(bpy.context)
        log.debug(f'event_left_mouse_press,{self.shift_alt}')
        brush = settings.brush
        try:
            # self.is_esc = True
            if self.shift_alt:
                setattr(self, 'or_dir', brush.direction)
                brush.direction = 'ENHANCE_DETAILS' if brush.direction == 'SMOOTH' else 'SMOOTH'
                # TODO ERROR bpy.ops.sculpt.brush_stroke('INVOKE_DEFAULT', mode='INVERT')
        except Exception as e:
            log.debug(e)
        bpy.ops.sculpt.brush_stroke('INVOKE_DEFAULT', mode='NORMAL')
        if getattr(self, 'or_dir', False):
            brush.direction = self.or_dir
            delattr(self, 'or_dir')
        return {'PASS_THROUGH'}

    def update_shortcut_keys(self):
        if self.is_exit or self.is_pass:
            self.set_shortcut_keys('NORMAL')
        if self.is_hide_mode:
            self.set_shortcut_keys('HIDE')
        elif self.is_mask_mode:
            self.set_shortcut_keys('MASK')
        else:
            self.set_shortcut_keys('NORMAL')
