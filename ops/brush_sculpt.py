import bpy
from mathutils import Vector

from ..utils.log import log
from ..utils.public import PublicOperator, PublicDraw


class OperatorProperty(PublicOperator, PublicDraw):
    alpha = 0.5
    start_mouse: Vector
    draw_in_depth_up: bool
    start_buffer_scale: float

    @property
    def is_builtin_brush(self):
        return self.active_tool_name.split(sep='.')[0] == 'builtin_brush'

    @property
    def is_annotate_brush(self):
        return self.active_tool_name in self.annotate_brush

    @property
    def mouse_is_in_model_up(self):
        return self.is_annotate_brush or self.get_mouse_location_ray_cast(
            self.context, self.event)

    @property
    def is_hide_mode(self):
        return self.active_tool_name == 'builtin.box_hide' and (
                self.ctrl_shift or self.ctrl_shift_alt)

    @property
    def is_make_mode(self):
        return (not self.mouse_is_in_model_up) and (
                self.only_ctrl or self.ctrl_alt) and self.is_builtin_brush

    @property
    def is_box_make_brush(self):
        return self.active_tool_name == 'builtin.box_mask'

    @property
    def is_draw_2d_box(self):
        return not self.is_click and (
                self.is_hide_mode or self.is_make_mode or
                self.is_box_make_brush)

    @property
    def is_exit(self):
        return self.event_is_left or self.event_is_right or self.event_is_esc

    @property
    def use_front_faces_only(self):
        return self.active_tool.operator_properties(
            "bbrush.mask").use_front_faces_only

    @property
    def color(self) -> Vector:
        if self.only_ctrl:
            return Vector((0, 0, 0, self.alpha))
        elif self.ctrl_alt:
            return Vector((.5, .5, .5, self.alpha))
        elif self.ctrl_shift_alt:
            return Vector((.6, 0, 0, self.alpha))
        elif self.ctrl_shift:
            return Vector((0, .6, 0, self.alpha))

        return Vector((1, 0, 0, 1))


class DepthUpdate(OperatorProperty):

    def depth_scale_update(self, context, event):
        co = self.mouse_co
        value = self.start_mouse - co
        x = 1 / context.region.width * (-1 * value[0])
        y = 1 / context.region.height * value[1]

        value = self.pref.depth_scale = self.start_buffer_scale + max(x, y) * 2
        context.area.header_text_set(f'深度图缩放值 {value}')

    def init_depth(self):
        from ..ui.draw_depth import DrawDepth
        _buffer = DrawDepth.depth_buffer
        self.draw_in_depth_up = ('wh' in _buffer) and self.mouse_in_area_in(
            self.event, _buffer['wh'])


class BBrushSculpt(DepthUpdate):
    bl_idname = 'bbrush.bbrush_sculpt'
    bl_label = 'Bbrush雕刻'
    bl_description = '使用Zbrush的方式雕刻'
    bl_options = {'REGISTER'}

    def invoke(self, context, event):

        log.debug(self.bl_idname)
        self.cache_clear()
        self.init_invoke(context, event)
        self.init_depth()

        self.start_mouse = self.mouse_co

        self.start_buffer_scale = self.pref.depth_scale
        if self.is_3d_view:
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}

    def modal(self, context, event):
        self.init_modal(context, event)
        self.tag_redraw(context)

        try:
            if self.is_exit:  # 退出模态操作
                context.area.header_text_set(None)
                log.info('ESC Bbrush Sculpt_____ FINISHED')
                return {'FINISHED'}

            elif self.draw_in_depth_up:  # 鼠标放在左上角深度图上操作
                log.debug('draw_in_depth_up')
                self.depth_scale_update(context, event)
                return {'RUNNING_MODAL'}
            else:
                return self.modal_handle()
        except Exception as e:
            log.error(e.args)
            return {'FINISHED'}

    def modal_handle(self):
        in_modal = self.mouse_is_in_model_up
        if in_modal:
            if self.only_alt:
                self.smooth_brush_handle()
            else:
                bpy.ops.sculpt.brush_stroke('INVOKE_DEFAULT',
                                            True,
                                            mode='NORMAL')
        else:
            if self.only_alt:
                bpy.ops.view3d.move('INVOKE_DEFAULT',
                                    True,
                                    )
            else:
                bpy.ops.view3d.rotate('INVOKE_DEFAULT',
                                      True,
                                      )
        return {'FINISHED'}

    def smooth_brush_handle(self):
        if self.is_builtin_brush_smooth_brush:
            ...
        else:
            bpy.ops.sculpt.brush_stroke('INVOKE_DEFAULT',
                                        True,
                                        mode='INVERT')
