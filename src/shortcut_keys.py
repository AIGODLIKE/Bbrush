from bpy.app.translations import pgettext as _
SHORTCUT_KEYS = {
    'NORMAL': [
        {'doc': 'View operations'},
        {'tool': 'Pan view', 'key': 'alt+right or alt+middle'},
        {'tool': 'Pan view', 'key': 'alt+left Drag in blank area'},
        {'tool': 'Pan view', 'key': 'shift+middle'},
        {'tool': 'Rotate view', 'key': 'mouse_right'},
        {'tool': 'Rotate view', 'key': 'left Drag in blank area'},
        {'tool': 'Zoom view', 'key': 'ctrl+middle or ctrl+right'},
        {'tool': 'Tilt view', 'key': 'shift+left Drag in blank area'},

        {'doc': 'Sculpt'},
        {'tool': 'Sculpt', 'key': 'left Paint on the model'},
        {'tool': 'Reverse sculpt', 'key': 'alt+left Paint on the model'},
        {'tool': 'Smooth', 'key': 'shift+left Paint on the model'},

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
        {'tool': 'Clear mask', 'key': 'ctrl+left Drag in blank area'},
        {'tool': 'Sharpen mask', 'key': 'ctrl+alt+left Click on the model'},
        {'tool': 'Fill mask', 'key': 'ctrl+alt+left Drag in blank area'},

        {'doc': 'Other'},
        {'tool': 'Grow mask', 'key': 'ctrl+Numpad+ Click'},
        {'tool': 'Shrink mask', 'key': 'ctrl+Numpad- Click'},
        {'tool': 'Increase contrast', 'key': 'ctrl+Up arrow or ctrl+Numpad* Click'},
        {'tool': 'Decrease contrast', 'key': 'ctrl+Down arrow or ctrl+Numpad/ Click'}
    ],
    'HIDE': [
        {'doc': 'Hide'},
        {'tool': 'Hide outside', 'key': 'ctrl+shift+left Paint on the model'},
        {'tool': 'Hide inside', 'key': 'ctrl+shift+alt+left Paint on the model'},
        {'tool': 'Unhide',
         'key': 'ctrl+shift+left Click in blank area'},
        {'tool': 'Invert visibility',
         'key': 'ctrl+shift+left or ctrl+shift+alt+left Drag in blank area'},
    ],
}
