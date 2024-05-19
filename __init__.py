import bpy
from .utils import reg

bl_info = {
    "name": "Bbrush",
    "author": "AIGODLIKE Community：小萌新",
    "version": (1, 2, 4),
    "blender": (4, 0, 0),
    "location": "Entering the sculpt mode will be displayed in the top bar",
    "description": "",
    "category": "AIGODLIKE"
}


class TranslationHelper():
    def __init__(self, name: str, data: dict, lang='zh_CN'):
        self.name = name
        self.translations_dict = dict()

        for src, src_trans in data.items():
            key = ("Operator", src)
            self.translations_dict.setdefault(lang, {})[key] = src_trans
            key = ("*", src)
            self.translations_dict.setdefault(lang, {})[key] = src_trans

    def register(self):
        try:
            bpy.app.translations.register(self.name, self.translations_dict)
        except ValueError:
            pass

    def unregister(self):
        bpy.app.translations.unregister(self.name)


# Set
############
from . import zh_CN

Bbrush_zh_CN = TranslationHelper('Bbrush_zh_CN', zh_CN.data)
Bbrush_zh_HANS = TranslationHelper('Bbrush_zh_HANS', zh_CN.data, lang='zh_HANS')


def register():
    reg.register()

    if bpy.app.version < (4, 0, 0):
        Bbrush_zh_CN.register()
    else:
        Bbrush_zh_CN.register()
        Bbrush_zh_HANS.register()


def unregister():
    reg.unregister()

    if bpy.app.version < (4, 0, 0):
        Bbrush_zh_CN.unregister()
    else:
        Bbrush_zh_CN.unregister()
        Bbrush_zh_HANS.unregister()
