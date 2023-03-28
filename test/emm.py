
def exit_handler(self, context, event):
    print('handler_remove')

    if getattr(self, 'mouse_path'):
        path = self.mouse_path
        if self.is_polygon_mode and (not self.polygon_not_pos):
            path = self.line_to_dit(self.mouse_pos)
            print(
                'self.polygon and not self.no_pos_data \n',
                path
            )

        if self.get_shape_in_model_up():
            path = [{
                'name': '',
                'loc': i,
                'start_time': 0
            } for i in path]
            print('path\n', len(path), self.mouse_path)
            bpy.ops.paint.mask_lasso_gesture(
                path=path,
                value=0 if event.alt else 1,
                use_front_faces_only=self.use_front_faces_only
            )
        else:
            if event.alt:
                value = 1
            else:
                value = 0
            bpy.ops.paint.mask_flood_fill(mode='VALUE', value=value)
    self.handler_remove()
    self.tag_redraw(context)
    return {'FINISHED'}

def sculpt_mode_handle(self, event):
    if self.only_ctrl or self.ctrl_alt:
        return self.mask_brush_handle(event)
    elif self.ctrl_shift or self.ctrl_shift_alt:
        return self.hide_brush_handle(event)
    elif self.only_shift:
        return self.smooth_brush_handle(event)
    # 在模型上绘制处理
    elif self.mouse_is_in_model_up and (not self.is_click):
        return self.mouse_is_in_model_up_handle(event)
    elif not self.is_click:  # 不在模型上绘制处理
        return self.mouse_not_in_model_up_handle(event)
    else:  # 其它情况
        print("其它情况 FINISHED_")
        if self.only_alt and self.mouse_is_in_model_up:  # 切换雕刻物体
            bpy.ops.object.transfer_mode('INVOKE_DEFAULT')
        elif self.shift_alt and self.mouse_is_in_model_up:  # 切换面组遮罩操作
            print('切换面组遮罩操作  or shift_alt')
            bpy.ops.sculpt.face_set_change_visibility(
                'INVOKE_DEFAULT', mode='TOGGLE')
            bpy.ops.paint.mask_flood_fill('INVOKE_DEFAULT', mode='INVERT')
            bpy.ops.sculpt.face_set_change_visibility(
                'INVOKE_DEFAULT', mode='TOGGLE')
        self.handler_remove()
        return {'FINISHED'}


def draw_2d_rectangle(self, context, event):
    gpu.state.blend_set('ALPHA')
    if getattr(self, 'tmp_mouse_reduce', False):
        self.start_mouse = self.mouse_co + self.tmp_mouse_reduce
    x1, y1 = self.start_mouse
    x2, y2 = self.mouse_co

    vertices = ((x1, y1), (x2, y1), (x1, y2), (x2, y2))
    indices = ((0, 1, 2), (2, 1, 3))

    # draw area
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader,
                             'TRIS', {"pos": vertices},
                             indices=indices)
    shader.bind()
    shader.uniform_float("color", self.color)
    batch.draw(shader)

    # draw text
    if self.only_ctrl or self.ctrl_alt:
        self.draw_text(min(x1, x2),
                       max(y1, y2),
                       text="MASK",
                       font_id=1,
                       size=15,
                       color=(1, 1, 1, 1))
    elif self.ctrl_shift or self.ctrl_shift_alt:
        self.draw_text(min(x1, x2),
                       max(y1, y2),
                       text="HIDE",
                       font_id=1,
                       size=15,
                       color=(1, 1, 1, 1))

    # draw line
    vertices = ((x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1))
    self.draw_line(vertices, (1, 1, 1, 1), line_width=0.5)

    # draw cross
    line_length = 5
    x = int((x1 + x2) / 2)
    y = int((y1 + y2) / 2)
    self.draw_line(((x - line_length, y), (x + line_length, y)), (1, 1, 1, 1),
                   line_width=1)
    self.draw_line(((x, y - line_length), (x, y + line_length)), (1, 1, 1, 1),
                   line_width=1)
    gpu.state.blend_set('NONE')


def invoke_draw_2d_box_mode_set(self, context, event):
    if self.is_draw_2d_box:
        self.handler_add(self.draw_2d_rectangle, (context, event))


def exit_draw_2d_ops_mask(self):
    if self.only_ctrl:
        bpy.ops.paint.mask_flood_fill('INVOKE_DEFAULT',
                                      mode='VALUE',
                                      value=0)
    elif self.ctrl_alt:
        bpy.ops.paint.mask_flood_fill('INVOKE_DEFAULT',
                                      mode='VALUE',
                                      value=1)
    elif self.ctrl_shift_alt or self.ctrl_shift:
        bpy.ops.sculpt.face_set_change_visibility('INVOKE_DEFAULT',
                                                  mode='INVERT')


def exit_draw_2d_ops(self, event):
    if self.is_draw_2d_box:
        x1, y1 = self.start_mouse
        x2, y2 = self.mouse_co
        w, h = self.start_mouse - self.mouse_co
        area_is_in_mode_up = self.get_area_ray_cast(min(x1, x2), min(y1, y2),
                                                    abs(w), abs(h))

        if area_is_in_mode_up:
            if self.only_ctrl:
                bpy.ops.paint.mask_box_gesture(xmin=min(x1, x2),
                                               xmax=max(x1, x2),
                                               ymin=min(y1, y2),
                                               ymax=max(y1, y2),
                                               value=1, use_front_faces_only=self.use_front_faces_only)
            elif self.ctrl_alt:
                bpy.ops.paint.mask_box_gesture(xmin=min(x1, x2),
                                               xmax=max(x1, x2),
                                               ymin=min(y1, y2),
                                               ymax=max(y1, y2),
                                               value=0)
            elif self.ctrl_shift_alt:
                bpy.ops.paint.hide_show(action='HIDE',
                                        xmin=min(x1, x2),
                                        xmax=max(x1, x2),
                                        ymin=min(y1, y2),
                                        ymax=max(y1, y2))
            elif self.ctrl_shift:
                bpy.ops.paint.hide_show(action='HIDE',
                                        area='OUTSIDE',
                                        xmin=min(x1, x2),
                                        xmax=max(x1, x2),
                                        ymin=min(y1, y2),
                                        ymax=max(y1, y2))
        else:
            self.exit_draw_2d_ops_mask()


def box_event_move_update(self, event):
    if event.type == 'SPACE':
        if event.value == 'PRESS':
            self.tmp_mouse_reduce = self.start_mouse - self.mouse_co
        elif event.value == 'RELEASE':
            if self.tmp_mouse_reduce:
                self.start_mouse = self.mouse_co + self.tmp_mouse_reduce
                del self.tmp_mouse_reduce


def box_mask_switch(self, event):
    left_press = self.only_ctrl and (event.type == 'LEFT_CTRL'
                                     and event.value == 'PRESS')
    # if left_press:
    #     if self.temp_hide_mode:
    #         self.temp_hide_mode = False
    #     else:
    #         self.temp_hide_mode = True


def draw_2d_box_data_update(self, event):
    self.box_event_move_update(event)
    # if self.only_ctrl or self.only_alt:  # 遮罩切换
    # self.box_mask_switch(event)


def mask_is_click(self, event):  # 单击遮罩处理
    not_key, only_ctrl, only_alt, only_shift, shift_alt, ctrl_alt, ctrl_shift, ctrl_shift_alt = self.get_event_key(
        event)

    if self.mouse_is_in_model_up:
        if only_ctrl:
            # bpy.ops.sculpt.mask_filter('INVOKE_DEFAULT', filter_type='SHRINK', auto_iteration_count=True)
            bpy.ops.sculpt.mask_filter('INVOKE_DEFAULT',
                                       filter_type='SMOOTH',
                                       auto_iteration_count=True)
            self.handler_remove()
            return {'FINISHED'}
        elif ctrl_alt:
            bpy.ops.sculpt.mask_filter('INVOKE_DEFAULT',
                                       filter_type='SHARPEN',
                                       auto_iteration_count=True)
            self.handler_remove()
            return {'FINISHED'}
    else:
        bpy.ops.paint.mask_flood_fill('INVOKE_DEFAULT', mode='INVERT')
        self.handler_remove()
        return {'FINISHED'}


def mask_is_brush(self, event):  # 绘制遮罩处理
    not_key, only_ctrl, only_alt, only_shift, shift_alt, ctrl_alt, ctrl_shift, ctrl_shift_alt = self.get_event_key(
        event)
    if self.mouse_is_in_model_up:
        if only_ctrl:
            bpy.ops.sculpt.brush_stroke('INVOKE_DEFAULT', mode='NORMAL')
            self.handler_remove()
            return {'FINISHED'}
        elif ctrl_alt:
            bpy.ops.sculpt.brush_stroke('INVOKE_DEFAULT', mode='INVERT')
            self.handler_remove()
            return {'FINISHED'}
    else:
        print('builtin_brush')
        self.is_esc = True
        return {'PASS_THROUGH'}


def mask_brush_handle(self, event):  # 遮罩笔刷处理
    not_key, only_ctrl, only_alt, only_shift, shift_alt, ctrl_alt, ctrl_shift, ctrl_shift_alt = self.get_event_key(
        event)
    print('遮罩笔刷处理 only_ctrl or ctrl_alt and builtin_brush', self.is_click)
    tool_name = self.active_tool.idname

    if self.is_click:
        return self.mask_is_click(event)
    elif tool_name in self.bbrush_brush:
        bpy.ops.bbrush.mask(
            'INVOKE_DEFAULT', mode=self.bbrush_brush[tool_name], use_front_faces_only=self.use_front_faces_only)
        return {'FINISHED'}
    elif self.is_builtin_brush:
        print('self.is_builtin_brush')
        return self.mask_is_brush(event)
    else:
        print('______run遮罩')
        self.is_esc = True
    return {'PASS_THROUGH'}  # 如果不反回则使用通过规则


def hide_brush_handle(self, event):  # 隐藏笔刷处理
    print('隐藏笔刷处理')
    if self.is_click and self.mouse_is_in_model_up:
        bpy.ops.sculpt.face_set_change_visibility(
            'INVOKE_DEFAULT', mode='TOGGLE')
    else:
        bpy.ops.sculpt.reveal_all()
        # bpy.ops.sculpt.face_set_change_visibility('INVOKE_DEFAULT',
        #                                           mode='SHOW_ALL')

    self.is_esc = True
    return {'RUNNING_MODAL'}


def smooth_brush_handle(self, event):  # shift处理
    not_key, only_ctrl, only_alt, only_shift, shift_alt, ctrl_alt, ctrl_shift, ctrl_shift_alt = self.get_event_key(
        event)
    print('shift处理')
    if only_shift and self.mouse_is_in_model_up:
        if self.is_builtin_brush:
            bpy.ops.sculpt.brush_stroke('INVOKE_DEFAULT', mode='SMOOTH')
            return {'FINISHED'}
        else:
            active_tool = self.active_tool
            bpy.ops.wm.tool_set_by_id(name="builtin_brush.Smooth")
            bpy.ops.sculpt.brush_stroke('INVOKE_DEFAULT', mode='SMOOTH')
            bpy.ops.wm.tool_set_by_id(name=str(active_tool))
            return {'FINISHED'}

    elif only_shift:  # 旋转视图操作
        print('only_shift')
        bpy.ops.view3d.view_roll('INVOKE_DEFAULT', type='ANGLE')
        self.handler_remove()
        return {'FINISHED'}
    else:
        self.is_esc = True
        return {'PASS_THROUGH'}
