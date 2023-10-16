from time import time

import bpy
import gpu
import numpy as np
from bpy.props import BoolProperty
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from ..utils.log import log
from ..utils.public import PublicOperator, PublicDraw


def draw_line(vertices, color, line_width=1):
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.line_width_set(line_width)
    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": vertices})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)
    gpu.state.line_width_set(1.0)


def get_circular(x, y, segments=64):
    from math import sin, cos, pi
    if segments <= 0:
        raise ValueError('Amount of segments must be greater than 0.')
    mul = (1.0 / (segments - 1)) * (pi * 2)
    vert = [Vector((sin(i * mul) * x, cos(i * mul) * y)) for i in
            range(segments)]
    return vert


class MaskProperty(PublicOperator, PublicDraw):
    use_front_faces_only: BoolProperty(name='仅前面的面')
    is_click: BoolProperty(name='按键操作是单击', default=True,
                           options={'SKIP_SAVE'})

    is_esc = False
    alpha = 0.9

    @property
    def color(self):
        if self.only_ctrl:
            return Vector((0, 0, 0, self.alpha))
        elif self.ctrl_alt or self.only_alt:
            return Vector((.5, .5, .5, self.alpha))
        elif self.ctrl_shift:
            return Vector((0, .6, 0, self.alpha))
        elif self.ctrl_shift_alt:
            return Vector((.6, 0, 0, self.alpha))
        return Vector((0, 0, 0, self.alpha))

    @property
    def is_polygon_mode(self):
        return self.active_tool_name == 'bbrush.polygon_mask'

    is_box_mode = False

    def box_mode_update(self):
        brush = self.active_tool_name in ('builtin.box_mask',
                                          'builtin.box_hide',
                                          'builtin_brush.Mask')
        self.is_box_mode = brush

    @property
    def is_circular_mode(self):
        return self.active_tool_name == 'bbrush.circular_mask'

    @property
    def is_ellipse_mask_brush(self):
        return self.active_tool_name == 'bbrush.ellipse_mask'

    @property
    def is_lasso_mask_brush(self):
        return self.active_tool_name == 'builtin.lasso_mask'

    @property
    def is_line_mask_brush(self):
        return self.active_tool_name == 'builtin.line_mask'

    @property
    def is_bbrush_brush(self):  # 是bbrush的笔刷
        return self.is_polygon_mode or self.is_circular_mode or \
            self.is_ellipse_mask_brush

    @property
    def is_mask_brush(self):
        return self.active_tool_name == 'builtin_brush.Mask'

    @property
    def mouse_is_in_model_up(self):
        return self.get_mouse_location_ray_cast(self.context, self.event)

    @property
    def polygon_not_pos(self):
        return self.is_polygon_mode and (not self.mouse_pos)

    @property
    def is_exit_modal(self):
        # 除多边形需要左键和右键配合之外其它情况松开这两个键都退出
        other_exit = (
                         not self.is_polygon_mode) and \
                     self.event_left_mouse_release
        brush_exit = self.polygon_not_pos or other_exit
        return self.event_key_enter or brush_exit or self.is_esc

    @property
    def bbrush_mask_is_use_front_faces_only(self):
        return self.active_tool.operator_properties(
            "bbrush.mask"
        ).use_front_faces_only

    @property
    def paint_mask_box_gesture_mask_is_use_front_faces_only(self):
        return self.active_tool.operator_properties(
            "paint.mask_box_gesture"
        ).use_front_faces_only

    @property
    def is_use_front_faces_only(self):
        if self.is_box_mask_brush:
            return self.paint_mask_box_gesture_mask_is_use_front_faces_only
        else:
            return self.bbrush_mask_is_use_front_faces_only

    @property
    def is_box_mask_brush(self):
        return self.active_tool_name == 'builtin.box_mask'

    @property
    def is_lasso_trim_brush(self):
        return self.active_tool_name == 'builtin.lasso_trim'

    @property
    def is_box_trim_brush(self):
        return self.active_tool_name == 'builtin.box_trim'

    @property
    def is_line_project_brush(self):
        return self.active_tool_name == 'builtin.line_project'

    @property
    def is_normal_invoke(self):
        mask = self.is_lasso_mask_brush or self.is_line_mask_brush
        hide = self.is_line_project_brush or self.is_box_trim_brush or \
               self.is_lasso_trim_brush
        return mask or hide

class MaskClick(MaskProperty):

    @staticmethod
    def invert_sculpt_hide_face():
        is_3_6_up_version = bpy.app.version >= (3, 6, 0)
        if is_3_6_up_version:
            bpy.ops.sculpt.face_set_invert_visibility()
        else:
            mode = 'TOGGLE' if is_3_6_up_version else 'INVERT'
            bpy.ops.sculpt.face_set_change_visibility('EXEC_DEFAULT', True, mode='INVERT')

    def mask_click(self):
        in_model = self.mouse_is_in_model_up
        ops = bpy.ops
        sculpt = ops.sculpt
        paint = ops.paint
        if self.only_ctrl:
            self.mask_click_only_ctrl(in_model, sculpt, paint)
        elif self.ctrl_alt:
            self.mask_click_ctrl_alt(in_model, sculpt)
        elif self.only_alt:
            if in_model:  # 切换雕刻物体
                ops.object.transfer_mode('INVOKE_DEFAULT')
        elif self.shift_alt:
            if in_model:
                sculpt.face_set_change_visibility(
                    mode='TOGGLE')
                paint.mask_flood_fill(mode='INVERT')
                sculpt.face_set_change_visibility(
                    mode='TOGGLE')
        elif self.ctrl_shift:
            if in_model:
                self.invert_sculpt_hide_face()
            else:
                paint.hide_show('EXEC_DEFAULT',
                                True,
                                action='SHOW',
                                area='ALL')
        self.handler_remove()
        return {'FINISHED'}

    @staticmethod
    def mask_click_only_ctrl(in_model, sculpt, paint):
        if in_model:  # 平滑遮罩
            sculpt.mask_filter('EXEC_DEFAULT',
                               True,
                               filter_type='SMOOTH',
                               auto_iteration_count=True)
        else:  # 切换遮罩
            paint.mask_flood_fill('EXEC_DEFAULT',
                                  True,
                                  mode='INVERT',
                                  )

    @staticmethod
    def mask_click_ctrl_alt(in_model, sculpt):
        if in_model:  # 硬化遮罩
            sculpt.mask_filter('EXEC_DEFAULT',
                               True,
                               filter_type='SHARPEN',
                               auto_iteration_count=True)
        else:  # 切换遮罩
            sculpt.face_set_change_visibility('EXEC_DEFAULT',
                                              True,
                                              mode='TOGGLE')


class MaskDrawArea(MaskClick):
    indices = ((0, 1, 2), (2, 1, 3))
    segments = 64

    mouse_pos = list()
    start_mouse: Vector
    start_time: float

    @property
    def _xy(self):
        return self.mouse_co - self.start_mouse

    @property
    def _x(self):
        return self._xy[0]

    @property
    def _y(self):
        return self._xy[1]

    @property
    def poly_gon_draw(self):
        return self.mouse_pos + [self.mouse_co, self.mouse_pos[0]]

    @property
    def poly_gon_data(self):
        try:
            return self.line_to_convex_shell(self.mouse_pos)
        except ValueError as v:
            log.error(v.args)
            print(v.args)
            return self.mouse_pos

    @property
    def ellipse_data(self):
        circular = get_circular(abs(self._x), abs(self._y), self.segments)
        draw_data = list((np.add(i, self.start_mouse))
                         for i in circular)
        return draw_data

    @property
    def _circular_data(self):
        axis = max(abs(self._x), abs(self._y))
        circular = get_circular(axis, axis, self.segments)
        draw_data = list(i + self.start_mouse for i in circular)
        return draw_data

    def draw_lift_up_text(self):
        x1, y1 = self.start_mouse
        x2, y2 = self.mouse_co
        text = 'HIDE' if self.ctrl_shift or self.ctrl_shift_alt else 'MASK'
        self.draw_text(min(x1, x2),
                       max(y1, y2),
                       text=text,
                       font_id=1,
                       size=15,
                       color=(1, 1, 1, 1))

    def draw_box(self):
        x1, y1 = self.start_mouse
        x2, y2 = self.mouse_co

        vertices = ((x1, y1), (x2, y1), (x1, y2), (x2, y2))
        # draw area
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = batch_for_shader(shader,
                                 'TRIS', {"pos": vertices},
                                 indices=self.indices)
        shader.bind()
        shader.uniform_float("color", self.color)
        batch.draw(shader)

        # draw line
        vertices = ((x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1))
        self.draw_line(vertices, (1, 1, 1, 1), line_width=2)

        # draw cross
        line_length = 5
        x = int((x1 + x2) / 2)
        y = int((y1 + y2) / 2)
        self.draw_line(((x - line_length, y), (x + line_length, y)),
                       (1, 1, 1, 1),
                       line_width=1)
        self.draw_line(((x, y - line_length), (x, y + line_length)),
                       (1, 1, 1, 1),
                       line_width=1)
        self.draw_lift_up_text()

    def draw_2d_handles(self, context, event):
        gpu.state.blend_set('ALPHA')
        if self.is_box_mode:
            self.draw_box()
        elif self.is_ellipse_mask_brush:
            draw_line(self.ellipse_data, self.color, line_width=2)
        elif self.is_circular_mode:
            draw_line(self._circular_data, self.color, line_width=2)
        elif self.is_polygon_mode and self.mouse_pos:
            draw_line(self.poly_gon_draw, self.color, line_width=2)
        gpu.state.blend_set('NONE')


class MaskClickDrag(MaskDrawArea):
    def mask_ops_lasso_path(self, path_, value):
        path = [{
            'name': '',
            'loc': i,
            'time': 0
        } for i in path_]
        bpy.ops.paint.mask_lasso_gesture(
            'EXEC_DEFAULT',
            True,
            path=path,
            value=value,
            use_front_faces_only=self.is_use_front_faces_only
        )

    def exit_modal_handle(self):
        x1, y1 = self.start_mouse
        x2, y2 = self.mouse_co
        w, h = self.start_mouse - self.mouse_co
        in_modal = self.get_area_ray_cast(min(x1, x2), min(y1, y2),
                                          abs(w), abs(h))
        args = {'xmin': int(min(x1, x2)),
                'xmax': int(max(x1, x2)),
                'ymin': int(min(y1, y2)),
                'ymax': int(max(y1, y2)),
                }
        paint = bpy.ops.paint
        value = 0 if self.event.alt else 1

        if self.is_polygon_mode:
            self.exit_polygon_mode(value)
        elif self.is_ellipse_mask_brush:
            self.exit_ellipse_mask_brush(in_modal, value)
        elif self.is_circular_mode:
            if in_modal:
                self.mask_ops_lasso_path(self._circular_data, value)
            else:
                self.exit_exception()
        elif in_modal:
            self.exit_in_modal(paint, args)
        else:
            self.exit_exception()
        self.mouse_pos.clear()

    def exit_polygon_mode(self, value):
        if not len(self.mouse_pos):
            return
        if self.get_shape_in_model_up():
            self.mask_ops_lasso_path(self.poly_gon_data, value)
        else:
            bpy.ops.paint.mask_flood_fill(mode='VALUE', value=value)

    def exit_ellipse_mask_brush(self, in_modal, value):
        if in_modal:
            self.mask_ops_lasso_path(self.ellipse_data, value)
        else:
            self.exit_exception()

    def exit_in_modal(self, paint, args):
        if self.only_ctrl:
            paint.mask_box_gesture(
                'EXEC_DEFAULT',
                True,
                **args,
                value=1,
                use_front_faces_only=self.is_use_front_faces_only,
            )
        elif self.ctrl_alt:
            paint.mask_box_gesture(
                'EXEC_DEFAULT',
                True,
                **args,
                value=0,
                use_front_faces_only=self.is_use_front_faces_only,
            )
        elif self.ctrl_shift_alt:
            paint.hide_show(action='HIDE',
                            **args, )
        elif self.ctrl_shift:
            paint.hide_show('EXEC_DEFAULT',
                            True,
                            action='HIDE',
                            area='OUTSIDE',
                            **args, )

    def exit_exception(self):
        paint = bpy.ops.paint
        if self.only_ctrl:
            paint.mask_flood_fill('EXEC_DEFAULT',
                                  True,
                                  mode='VALUE',
                                  value=0)
        elif self.ctrl_alt:
            paint.mask_flood_fill('EXEC_DEFAULT',
                                  True,
                                  mode='VALUE',
                                  value=1)
        elif self.ctrl_shift_alt or self.ctrl_shift:
            self.invert_sculpt_hide_face()

    def event_move_update(self):
        """
        mouse_co_tmp: Vector  # 临时位置,记录空格按下时的鼠标位置
        """
        have_tmp = getattr(self, 'mouse_co_tmp', False)

        if have_tmp:
            move = have_tmp - self.mouse_co
            log.debug(f'move,{move, have_tmp}')
            self.start_mouse -= move
            setattr(self, 'mouse_co_tmp', self.mouse_co)
            for index, _ in enumerate(self.mouse_pos):
                self.mouse_pos[index] = self.mouse_pos[index] - move

        if self.event_is_space:
            if self.event_is_press:
                if not have_tmp:
                    setattr(self, 'mouse_co_tmp', self.mouse_co)

            elif self.event_is_release:
                if have_tmp:
                    delattr(self, 'mouse_co_tmp')

    def get_shape_in_model_up(self):
        data = np.array(self.mouse_pos, dtype=np.float32)
        data.reshape((data.__len__(), 2))
        max_co = data.max(axis=0)
        min_co = data.min(axis=0)
        x = int(min_co[0])
        y = int(min_co[1])
        w = int(max_co[0] - x)
        h = int(max_co[1] - y)
        try:
            return self.get_area_ray_cast(x, y, w, h)
        except ValueError as v:
            log.info(f'{v.args}\n获取形状投射错误')

    def polygons_mask(self):
        click_time = bpy.context.preferences.inputs.mouse_double_click_time
        if self.event_is_left and self.event_is_press:
            s_time = (time() - self.start_time)
            if click_time / 1000 > s_time:
                self.is_esc = True
            self.start_time = time()

            if self.mouse_co not in self.mouse_pos:
                self.mouse_pos.append(self.mouse_co)

        elif self.event_is_right and self.event_is_press:
            self.mouse_pos.pop()

    def mask_click_drag(self, context, event):
        log.debug(f'mask_click_drag {self.start_mouse, self.mouse_co}')
        mask = self.is_mask_brush and self.mouse_is_in_model_up
        if mask:
            if self.ctrl_alt:
                bpy.ops.sculpt.brush_stroke('INVOKE_DEFAULT',
                                            True,
                                            mode='INVERT')
            else:
                bpy.ops.sculpt.brush_stroke('INVOKE_DEFAULT',
                                            True,
                                            mode='NORMAL')
            log.debug('is_mask_brush')
            return {'FINISHED'}
        elif self.is_normal_invoke:
            return {'FINISHED', 'PASS_THROUGH'}

        if self.is_3d_view:
            if self.is_polygon_mode:
                self.mouse_pos.append(self.mouse_co)
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}


class BBrushMask(MaskClickDrag):
    bl_idname = 'bbrush.mask'
    bl_label = 'Bbrush遮罩'
    bl_description = '遮罩笔刷'
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        self.init_invoke(context, event)
        self.cache_clear()  # 清
        self.start_time = time()
        self.start_mouse = self.mouse_co
        self.box_mode_update()
        log.debug(f'invoke {self.start_mouse, self.mouse_co}')
        self.tag_redraw(context)
        log.debug(self.bl_idname)
        if self.is_click:
            return self.mask_click()
        else:
            return self.mask_click_drag(context, event)

    def modal(self, context, event):
        self.init_modal(context, event)
        self.handler_add(self.__class__.draw_2d_handles, (self, context, event))
        self.tag_redraw(context)

        log.debug(f'''modal {
        self.start_mouse,
        self.mouse_co,
        event.mouse_region_x,
        event.mouse_region_y,
        event,
        event.type,
        event.value,}''')
        if self.event_is_esc or self.is_exit_modal:
            self.handler_remove()
            context.area.header_text_set(None)
            self.exit_modal_handle()
            log.debug('exit modal\n')
            return {'FINISHED'}

        elif self.is_bbrush_brush and self.is_polygon_mode:
            self.polygons_mask()

        self.event_move_update()
        return {'RUNNING_MODAL'}
