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
        if self.pref.show_shortcut_keys:
            font_id = self.font_info['font_id']
            font_size = 15
            blf.size(font_id, font_size, 72)
            blf.color(font_id, 1, 1, 1, 1)
            x = bpy.context.area.regions[2].width
            y = 10
            for index, item in enumerate(reversed(self.draw_shortcut_keys)):
                blf.position(font_id, x, y, 0)
                y += font_size
                blf.draw(font_id, item)

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
