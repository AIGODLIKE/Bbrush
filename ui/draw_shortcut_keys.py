import blf
import bpy

from ..utils.public import PublicClass


class DrawShortcutKeys(PublicClass):
    handle: object

    font_info = {
        'font_id': 0,
        'handler': None,
    }

    def draw(self):
        if self.pref.sculpt and self.pref.show_shortcut_keys:
            font_id = self.font_info['font_id']
            font_size = self.pref.shortcut_show_size
            column_space_size = 10
            key_row_space = 150

            blf.size(font_id, 18 * font_size)
            blf.color(font_id, 1, 1, 1, 1)
            x = self.pref.shortcut_offset_x
            y = self.pref.shortcut_offset_y
            for index, item in enumerate(reversed(self.draw_shortcut_keys)):
                y += 18 * font_size + column_space_size
                if 'doc' in item:
                    blf.position(font_id, x - 10, y, 0)
                    blf.draw(font_id, item['doc'])
                else:
                    tool = item['tool']
                    key = item['key']
                    # draw tool
                    blf.position(font_id, x, y, 0)
                    blf.draw(font_id, tool)
                    # draw key
                    blf.position(font_id, (x + key_row_space) * font_size, y, 0)
                    blf.draw(font_id, key)

    @classmethod
    def register(cls):
        cls.handle = bpy.types.SpaceView3D.draw_handler_add(
            DrawShortcutKeys().draw,
            (),
            'WINDOW',
            'POST_PIXEL'
        )

    @classmethod
    def unregister(cls):
        handle = cls.handle
        if handle:
            bpy.types.SpaceView3D.draw_handler_remove(
                handle, 'WINDOW')


def register():
    DrawShortcutKeys.register()


def unregister():
    DrawShortcutKeys.unregister()
