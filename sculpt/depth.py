class DepthUpdate:
    ...
    # def depth_scale_update(self, context, event):
    #     co = self.mouse_co
    #     value = self.start_mouse - co
    #     x = 1 / context.region.width * (-1 * value[0])
    #     y = 1 / context.region.height * value[1]
    #
    #     value = self.pref.depth_scale = self.start_buffer_scale + max(x, y) * 2
    #     context.area.header_text_set(f'Depth map zoom value {value}')
    #
    # def init_depth(self):
    #     from ..ui.draw_depth import DrawDepth
    #     _buffer = DrawDepth.depth_buffer
    #     self.draw_in_depth_up = ('wh' in _buffer) and self.mouse_in_area_in(self.event, _buffer['wh'])
