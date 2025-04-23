import os

from . import translate

ICON_PATH = os.path.join(os.path.dirname(__file__), 'icon')


def register():
    translate.register()


def unregister():
    translate.unregister()
