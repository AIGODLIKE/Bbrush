import blf
import bpy
import gpu

from ..utils import get_pref, get_region_height, get_region_width

"""绘制快捷键"""
SHORTCUT_KEYS = {
    'SCULPT': [
        {'doc': 'View operations'},
        {'tool': 'Pan view', 'key': 'alt+right or alt+middle'},
        {'tool': 'Pan view', 'key': 'alt+left Drag in blank area'},
        {'tool': 'Pan view', 'key': 'shift+middle'},
        {'tool': 'Rotate view', 'key': 'mouse_right'},
        {'tool': 'Rotate view', 'key': 'left Drag in blank area'},
        {'tool': 'Zoom view', 'key': 'ctrl+middle or ctrl+right'},
        {'tool': 'Tilt view', 'key': 'shift+left Drag in blank area'},

        {'doc': ' '},
        {'doc': 'Sculpt'},
        {'tool': 'Sculpt', 'key': 'left Paint on the model'},
        {'tool': 'Reverse sculpt', 'key': 'alt+left Paint on the model'},
        {'tool': 'Smooth', 'key': 'shift+left Paint on the model'},

        {'doc': ' '},
        {'doc': 'Other'},
        {'tool': 'Switch object', 'key': 'alt+left Click on other models'},
    ],
    'MASK': [
        {'doc': 'Mask'},
        {'tool': 'Draw mask', 'key': 'ctrl+left Paint on the model'},
        {'tool': 'Erase mask', 'key': 'ctrl+alt+left Paint on the model'},
        {'tool': 'Invert mask', 'key': 'ctrl+left Drag in blank area'},
        {'tool': 'Marquee mask', 'key': 'ctrl+left Drag from a blank area to the model'},
        {'tool': 'erase mask', 'key': 'ctrl+alt+left Drag from a blank area to the model'},
        {'tool': 'Fade mask', 'key': 'ctrl+left Click on the model'},
        {'tool': 'Sharpen mask', 'key': 'ctrl+alt+left Click on the model'},

        {'doc': ' '},
        {'tool': 'Clear mask', 'key': 'ctrl+left Drag in blank area'},
        {'tool': 'Fill mask', 'key': 'ctrl+alt+left Drag in blank area'},

        {'doc': ' '},
        {'doc': 'Other'},
        {'tool': 'Grow mask', 'key': 'ctrl+Numpad+ Click'},
        {'tool': 'Shrink mask', 'key': 'ctrl+Numpad- Click'},
        {'tool': 'Increase contrast', 'key': 'ctrl+Up arrow or ctrl+Numpad* Click'},
        {'tool': 'Decrease contrast', 'key': 'ctrl+Down arrow or ctrl+Numpad/ Click'}
    ],
    'HIDE': [
        {'doc': 'Hide'},
        {'tool': 'Hide outside', 'key': 'Paint on the model'},
        {'tool': 'Hide inside', 'key': '+alt Paint on the model'},
        {'tool': 'Unhide', 'key': 'Click in blank area'},
        {'tool': 'Invert visibility', 'key': 'Drag in blank area'},
        {'tool': 'Invert visibility', 'key': 'Click in model'},
    ],
}


class ShortcutKey:
    shortcut_key_handle = None

    font_info = {
        'font_id': 0,
        'handler': None,
    }
    shortcut_key_points = []

    @property
    def shortcut_key(self):
        if texts := SHORTCUT_KEYS.get(self.brush_mode):
            return texts
        return [{"doc": "EMM Test"}, ]

    def start_shortcut_key(self):
        space = bpy.types.SpaceView3D
        self.shortcut_key_handle = space.draw_handler_add(self.draw_shortcut_key, (), 'WINDOW', 'POST_PIXEL')
        self.shortcut_key_points = []

    def stop_shortcut_key(self, ):
        self.shortcut_key_points = None
        if handle := self.shortcut_key_handle:
            bpy.types.SpaceView3D.draw_handler_remove(handle, 'WINDOW')

    def draw_shortcut_key(self):
        from bpy.app.translations import pgettext_iface as translate
        context = bpy.context
        pref = get_pref()
        if pref.show_shortcut_keys:
            font_id = self.font_info['font_id']
            font_size = pref.shortcut_show_size
            column_space_size = 10
            key_row_space = 160

            blf.size(font_id, 18 * font_size)
            blf.color(font_id, 1, 1, 1, 1)

            offset_x, offset_y = pref.shortcut_offset

            header = get_region_height(context, "HEADER")
            tool_header = get_region_height(context, "TOOL_HEADER")
            asset_shelf = get_region_height(context, "ASSET_SHELF")
            asset_shelf_header = get_region_height(context, "ASSET_SHELF_HEADER")

            toolbar_width = get_region_width(context)
            header_height = header + tool_header

            x1 = toolbar_width + offset_x
            y1 = offset_y + asset_shelf + asset_shelf_header

            x2 = x1
            y2 = y1

            max_width = 0
            with gpu.matrix.push_pop():
                gpu.matrix.translate((x1, y1))
                for index, item in enumerate(reversed(self.shortcut_key)):
                    if 'doc' in item:
                        blf.position(font_id, 0, 0, 0)
                        text = translate(item['doc'])
                        blf.draw(font_id, text)
                        width, height = blf.dimensions(font_id, text)

                        y = height + column_space_size
                        y2 += y
                        gpu.matrix.translate((0, y))
                        if max_width < width:
                            max_width = width
                    else:
                        tool = translate(item['tool'])
                        key = translate(item['key'])
                        # draw tool
                        blf.position(font_id, 0, 0, 0)
                        blf.draw(font_id, tool)
                        tw, th = blf.dimensions(font_id, tool)

                        # draw key
                        off = key_row_space * font_size
                        blf.position(font_id, off, 0, 0)
                        blf.draw(font_id, key)
                        kw, kh = blf.dimensions(font_id, tool)

                        height = max(th, kh) + column_space_size
                        gpu.matrix.translate((0, height))
                        y2 += height
                        width = tw + kw + off
                        if max_width < width:
                            max_width = width

            x2 += max_width

            self.shortcut_key_points = (x1, x2, y1, y2)
