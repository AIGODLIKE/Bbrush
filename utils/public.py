from functools import cache

import blf
import bpy
import gpu
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from ..src.shortcut_keys import SHORTCUT_KEYS


@cache
def get_pref():
    from .. import __package__ as __name__
    return bpy.context.preferences.addons[__name__].preferences


class PublicData:
    draw_shortcut_type = 'NORMAL'  # 绘制快捷键信息

    @property
    def draw_shortcut_keys(self):
        return SHORTCUT_KEYS[self.draw_shortcut_type]

    context: bpy.types.Context
    event: bpy.types.Event
    _handle = None
    not_key: bool
    only_ctrl: bool
    only_alt: bool
    only_shift: bool
    shift_alt: bool
    ctrl_alt: bool
    ctrl_shift: bool
    ctrl_shift_alt: bool

    @staticmethod
    def set_shortcut_keys(shortcut_type: str) -> None:
        """
        set draw shortcut info
        @param shortcut_type: str shortcut type
        """
        PublicData.draw_shortcut_type = shortcut_type


class PublicEvent(PublicData):
    def event_type(self, event_type):
        return self.event.type == event_type

    def event_value(self, event_value):
        return self.event.value == event_value

    @property
    def event_is_esc(self):
        return self.event_type('ESC')

    @property
    def event_is_w(self):
        return self.event_type('W')

    @property
    def event_is_f(self):
        return self.event_type('F')

    @property
    def event_is_r(self):
        return self.event_type('R')

    @property
    def event_is_tab(self):
        return self.event_type('TAB')

    @property
    def event_is_left(self):
        return self.event_type('LEFTMOUSE')

    @property
    def event_is_right(self):
        return self.event_type('RIGHTMOUSE')

    @property
    def event_is_space(self):
        return self.event_type('SPACE')

    @property
    def event_is_release(self):
        return self.event_value('RELEASE')

    @property
    def event_is_press(self):
        return self.event_value('PRESS')

    @property
    def event_key_enter(self):
        return self.event.type in ('RET', 'MIDDLEMOUSE')

    @property
    def event_key_middlemouse(self):
        return self.event.type == 'MIDDLEMOUSE'

    @property
    def event_left_mouse_release(self):
        return self.event_is_left and self.event_is_release

    @property
    def event_left_mouse_press(self):
        return self.event_is_left and self.event_is_press


class PublicDraw:

    @staticmethod
    def draw_text(x,
                  y,
                  text="Hello Word",
                  font_id=0,
                  size=10,
                  *,
                  color=(0.5, 0.5, 0.5, 1),
                  column=0):
        blf.position(font_id, x, y - (size * (column + 1)), 0)
        blf.size(font_id, size)
        blf.color(font_id, *color)
        blf.draw(font_id, text)

    @staticmethod
    def draw_shader(pos,
                    indices,
                    color=None,
                    *,
                    shader_name='POLYLINE_SMOOTH_COLOR',
                    draw_type='LINES',
                    ):

        shader = gpu.shader.from_builtin(shader_name)
        if draw_type == 'POINTS':
            batch = batch_for_shader(shader, draw_type, {'pos': pos})
        else:
            batch = batch_for_shader(shader,
                                     draw_type, {'pos': pos},
                                     indices=indices)

        shader.bind()
        if color:
            shader.uniform_float('color', color)

        batch.draw(shader)

    @staticmethod
    def draw_circle_2d(position, color, radius, *, segments=32):
        from math import sin, cos, pi
        import gpu
        from gpu.types import (
            GPUBatch,
            GPUVertBuf,
            GPUVertFormat,
        )

        if segments <= 0:
            raise ValueError("Amount of segments must be greater than 0.")

        with gpu.matrix.push_pop():
            gpu.matrix.translate(position)
            gpu.matrix.scale_uniform(radius)
            mul = (1.0 / (segments - 1)) * (pi * 2)
            verts = [(sin(i * mul), cos(i * mul)) for i in range(segments)]
            fmt = GPUVertFormat()
            pos_id = fmt.attr_add(id="pos",
                                  comp_type='F32',
                                  len=2,
                                  fetch_mode='FLOAT')
            vbo = GPUVertBuf(len=len(verts), format=fmt)
            vbo.attr_fill(id=pos_id, data=verts)
            batch = GPUBatch(type='LINE_STRIP', buf=vbo)
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch.program_set(shader)
            shader.uniform_float("color", color)
            batch.draw()

    def draw_2d_area(self, draw_data):
        pos_data = self.mouse_pos
        dl = draw_data.__len__()
        if dl > 3:
            area_draw_data = pos_data
            if self.mouse not in pos_data:
                area_draw_data = pos_data + [self.mouse_co]

            v, link = self.line_to_dit(area_draw_data, 1)

            self.draw_shader(v, link, (1, 1, 1, 1),
                             shader_name='UNIFORM_COLOR', draw_type='TRIS')


class PublicProperty:
    @property
    def is_sculpt_mode(self):
        context = bpy.context
        mode = context.mode
        return mode == 'SCULPT'

    @property
    def is_switch_sculpt_mode(self):
        pref = PublicClass.pref_()
        always_use = pref.always_use_bbrush_sculpt_mode
        return self.is_sculpt_mode and always_use and (not pref.sculpt)

    @property
    def is_exit_sculpt_mode(self):
        pref = PublicClass.pref_()
        return (not self.is_sculpt_mode) and pref.sculpt


class PublicClass(PublicProperty,
                  ):
    @staticmethod
    def cache_clear():
        get_pref.cache_clear()
        PublicClass.get_mouse_location_ray_cast.cache_clear()

    @staticmethod
    def pref_():
        return get_pref()

    @property
    def pref(self):
        return self.pref_()


    @staticmethod
    def tag_redraw(context):
        if context.area:
            context.area.tag_redraw()
        if context.region:
            context.region.tag_redraw()

    @staticmethod
    def tag_all_redraw(context):
        if context.screen:
            for area in context.screen.areas:
                area.tag_redraw()

    @classmethod
    def update_interface(cls):
        pref = cls.pref_()

        if pref.is_switch_sculpt_mode:
            pref.sculpt = True
            bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)
        elif pref.is_exit_sculpt_mode:
            pref.sculpt = False
            bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)

    @property
    def active_tool(self):
        return ToolSelectPanelHelper.tool_active_from_context(bpy.context)

    @property
    def active_tool_name(self):
        return self.active_tool.idname if self.active_tool else ''

    @property
    def is_builtin_brush_smooth_brush(self):
        return self.active_tool_name == 'builtin_brush.Smooth'


def register_submodule_factory(submodule_tuple):
    def register():
        for mod in submodule_tuple:
            mod.register()

    def unregister():
        for mod in reversed(submodule_tuple):
            mod.unregister()

    return register, unregister


class PublicOperator(PublicClass, Operator):
    is_click: BoolProperty(name='theKeyActionIsAClick', default=True,
                           options={'SKIP_SAVE'})

    bbrush_brush = {
        'bbrush.ellipse_mask': 'ELLIPSE',
        'bbrush.circular_mask': 'CIRCULAR',
        'bbrush.polygon_mask': 'POLYGON',
        'bbrush.square_mask': 'SQUARE',
    }
    annotate_brush = ('builtin.annotate',
                      'builtin.annotate_line',
                      'builtin.annotate_polygon',
                      'builtin.annotate_eraser')

    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT' and context.sculpt_object

    @staticmethod
    def get_event_key(event):
        alt = event.alt
        shift = event.shift
        ctrl = event.ctrl

        not_key = ((not ctrl) and (not alt) and (not shift))

        only_ctrl = (ctrl and (not alt) and (not shift))
        only_alt = ((not ctrl) and alt and (not shift))
        only_shift = ((not ctrl) and (not alt) and shift)

        shift_alt = ((not ctrl) and alt and shift)
        ctrl_alt = (ctrl and alt and (not shift))

        ctrl_shift = (ctrl and (not alt) and shift)
        ctrl_shift_alt = (ctrl and alt and shift)
        return not_key, only_ctrl, only_alt, only_shift, shift_alt, ctrl_alt, \
            ctrl_shift, ctrl_shift_alt

    @property
    def is_3d_view(self):
        context = self.context
        return context.space_data and (context.space_data.type
                                       == 'VIEW_3D')

    def set_event_key(self):
        (self.not_key,
         self.only_ctrl,
         self.only_alt,
         self.only_shift,
         self.shift_alt,
         self.ctrl_alt,
         self.ctrl_shift,
         self.ctrl_shift_alt) = self.get_event_key(
            self.event)

    def _set_ce(self, context, event):
        self.context = context
        self.event = event
        self.set_event_key()

    def _set_mouse(self, context, event):
        setattr(self, '_mouse_x',
                min(max(0, event.mouse_region_x), context.region.width))
        setattr(self, '_mouse_y',
                min(max(0, event.mouse_region_y), context.region.height))

    def init_invoke(self, context, event) -> None:
        self._set_ce(context, event)
        self._set_mouse(context, event)

    def init_modal(self, context, event) -> None:
        self.init_invoke(context, event)

    @property
    def mouse_co(self) -> Vector:
        return Vector((self._mouse_x, self._mouse_y))

    def handler_add(self, func, args):
        """将handler 添加放在modal内,不然有可能会出现坐标位置错误"""
        if not getattr(self, '_handle', None):
            self._handle = bpy.types.SpaceView3D.draw_handler_add(
                func, args, 'WINDOW', 'POST_PIXEL')

    def handler_remove(self):
        if getattr(self, '_handle', False):
            bpy.types.SpaceView3D.draw_handler_remove(
                self._handle, 'WINDOW')


class PublicExportPropertyOperator:
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = ".json"
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,
        # Max internal depth_buffer length, longer would be clamped.
    )

    @staticmethod
    def get_data(context) -> dict:
        return {'emm': 'emm_test'}

    def execute(self, context) -> set:
        import json
        try:
            data = self.get_data(context)
            _file = open(self.filepath,
                         'w+',
                         encoding='utf8')
            _file.write(json.dumps(data,
                                   separators=(',', ': '),
                                   indent=1,
                                   ensure_ascii=True))
            _file.close()
        except Exception as e:
            print(f'ERROR {self.filepath} writePropertyFileError')
            print(e)
        return {'FINISHED'}
