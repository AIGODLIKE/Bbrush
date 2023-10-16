import blf
import bpy
import gpu
import numpy as np
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator
from functools import cache
from gpu_extras.batch import batch_for_shader
from mathutils import Vector, geometry
from os.path import basename, dirname, realpath

from .log import log
from ..src.shortcut_keys import SHORTCUT_KEYS

ADDON_NAME = basename(dirname(dirname(realpath(__file__))))


@cache
def get_pref():
    return bpy.context.preferences.addons[ADDON_NAME].preferences


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


class PublicMath(PublicEvent):
    @staticmethod
    def to_vector(data):
        return [Vector(i).freeze() for i in data]

    @staticmethod
    def get_all_intersect_pos(pos):
        po_len = pos.__len__()
        indices_list = [(i - 1, i) for i in range(1, po_len)] + [
            (0, po_len - 1)]
        tmp_dict = {'intersect': {}, 'line': {i: [] for i in indices_list}}
        while indices_list:
            cur_line = indices_list.pop()
            if cur_line not in tmp_dict['line']:
                tmp_dict['line'][cur_line] = [pos[cur_line[0]],
                                              pos[cur_line[1]]]
            for line in indices_list:
                if line not in tmp_dict['line']:
                    tmp_dict['line'][line] = [pos[line[0]], pos[line[1]]]

                get_int = geometry.intersect_line_line_2d(
                    pos[cur_line[0]],
                    pos[cur_line[1]],
                    pos[line[0]],
                    pos[line[1]],
                )
                if get_int:
                    get_int = get_int.freeze()
                    tmp_dict['intersect'][get_int] = [cur_line, line]
                    tmp_dict['line'][line].append(get_int)
                    tmp_dict['line'][cur_line].append(get_int)
        return tmp_dict

    @staticmethod
    def to_left(startpoint, endpoint, co) -> bool:
        """测试co是否在 start_point->end_point 向量的左侧

        startpoint, endpoint 的z都为0  因为是 2d左边转换的
        """
        line1 = (endpoint - startpoint).to_3d()
        line2 = (co - startpoint).to_3d()
        return line1.cross(line2)[-1] > 0

    @staticmethod
    def find_closet(point_list, src_point):
        """从 点列表中查找 距离 src_point 最近的点
        """
        min_dist = 9999999999999
        find_point = None
        for v in point_list:
            if v == src_point:
                continue
            d = (v - src_point).magnitude
            if d < min_dist:
                find_point = v
                min_dist = d
        return find_point

    @staticmethod
    def circle_test(circle, new_obj=False):
        """绘制图案测试
        """
        if 'sss' in bpy.data.meshes:
            bpy.data.meshes.remove(bpy.data.meshes['sss'])
        me = bpy.data.meshes.new("sss")
        me.from_pydata(vertices=[v.to_3d() / 100 for v in circle],
                       edges=[(i, i + 1) for i in range(len(circle) - 1)],
                       faces=[])
        me.update()

        import bmesh
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.0001)
        bmesh.ops.triangle_fill(bm, edges=bm.edges[:])
        bm.to_mesh(me)
        bm.free()
        if new_obj:
            if "sss" not in bpy.data.objects:
                o = bpy.data.objects.new("sss", object_data=me)
            else:
                o = bpy.data.objects['sss']
                o.data = me
            if o.name not in bpy.context.scene.collection.objects:
                bpy.context.scene.collection.objects.link(o)

        return (i.vertices[:] for i in me.polygons)

    @classmethod
    def line_to_convex_shell(cls, pos, link=False):
        """提取多边形的外边框
        """
        # [v1, v2, v3, v1]
        pos = cls.to_vector(pos)
        pos_neibor = {
            k: [
                i - 1 if (i - 1) != -1 else len(pos) - 1, i + 1 if
                (i + 1) != len(pos) else 0
            ]
            for i, k in enumerate(pos)
        }

        convex_hull_2d = geometry.convex_hull_2d(pos)
        int_dict = cls.get_all_intersect_pos(pos.copy())
        from_idx = convex_hull_2d[0]
        from_point = pos[from_idx]
        origin_point = from_point
        end1_idx = end2_idx = 0

        # 查找 假设 查找到的都是端点线段
        end1_idx, end2_idx = pos_neibor[from_point]
        # 保证 end1_idx 为下一个起始点
        if cls.to_left(from_point, pos[end1_idx], pos[end2_idx]):
            end1_idx = end2_idx

        # 记录当前的 连线是哪个
        pair = (end1_idx, from_idx) if end1_idx < from_idx else \
            (from_idx, end1_idx)

        # 如果 第一次循环 的to_point 不为 端点
        if len(int_dict['line'][pair]) > 2:
            # 取左边点的最近交点
            find_point = cls.find_closet(int_dict['line'][pair], from_point)
            to_point = find_point
            try:
                from_idx = pos.index(find_point)
            except Exception as e:
                print(e)
                from_idx = -9999
        else:
            from_idx = end1_idx
            to_point = pos[end1_idx]

        circle = []
        counter = 0
        while True:
            circle.append(from_point)
            if (len(int_dict['line'][pair]) == 2) or (-1 < from_idx < len(pos)):
                # 如果为端点    查找端点对应的连线
                from_point = to_point
                end1_idx, end2_idx = pos_neibor[from_point]

                pair1 = (end1_idx, from_idx) if end1_idx < from_idx else \
                    (from_idx, end1_idx)
                pair2 = (end2_idx, from_idx) if end2_idx < from_idx else \
                    (from_idx, end2_idx)

                pair = (pair2 if pair1 == pair else pair1)
                #   判断当前线段是否存在交点，如果有则取 最近点，否则取端点
                find_point = cls.find_closet(int_dict['line'][pair], from_point)
                if len(int_dict['line'][pair]) > 2:
                    #   为交点
                    to_point = find_point
                    from_idx = -9999
                else:
                    #   为端点
                    from_idx = pair[0] if pair[1] == from_idx else pair[1]
                    to_point = pos[from_idx]
            else:
                #   不为端点 1.查找start_point对应线段上的所有交点   [(0, 1), (2, 3), None]
                pair1, pair2 = int_dict['intersect'][to_point]
                pair = (pair2 if pair1 == pair else pair1)

                #   2.对以上端点 与 line做ToLeft测试   线上的点
                left_point = []
                for v in int_dict['line'][pair]:
                    if cls.to_left(from_point, to_point, v):
                        #   在左边
                        left_point.append(v)
                #   取左边点的最近交点
                find_point = cls.find_closet(left_point, to_point)
                from_point, to_point = to_point, find_point
                try:
                    from_idx = pos.index(find_point)
                except IndexError as e:
                    from_idx = -9999
                    log.debug(e.args)
            #   退出条件
            if to_point == origin_point:
                circle.append(from_point)
                circle.append(origin_point)
                #   找到循环路径
                break
            counter += 1
            if counter > len(pos) * 12:
                break
        if link:
            return circle, cls.circle_test(circle, True)
        return circle


class PublicDraw:

    @staticmethod
    def draw_text(x,
                  y,
                  text="Hello Word",
                  font_id=0,
                  size=10,
                  *,
                  color=(0.5, 0.5, 0.5, 1),
                  dpi=72,
                  column=0):
        blf.position(font_id, x, y - (size * (column + 1)), 0)
        blf.size(font_id, size)
        blf.color(font_id, *color)

    @staticmethod
    def draw_line(vertices, color, line_width=1):
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.line_width_set(line_width)
        batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": vertices})
        shader.bind()
        shader.uniform_float("color", color)
        batch.draw(shader)
        gpu.state.line_width_set(1.0)

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
        always_use = pref.always_use_sculpt_mode
        return self.is_sculpt_mode and always_use and (not pref.sculpt)

    @property
    def is_exit_sculpt_mode(self):
        pref = PublicClass.pref_()
        return (not self.is_sculpt_mode) and pref.sculpt


class PublicClass(PublicProperty,
                  PublicMath,
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
    def get_area_ray_cast(x, y, w, h):
        data = {}

        def get_():
            _buffer = PublicClass.get_gpu_buffer((x, y), wh=(w, h),
                                                 centered=False)
            numpy_buffer = np.asarray(_buffer, dtype=np.float32).ravel()
            min_depth = np.min(numpy_buffer)
            data['is_in_model'] = (min_depth != (0 or 1))

        context = bpy.context
        view3d = context.space_data
        show_xray = view3d.shading.show_xray
        view3d.shading.show_xray = False
        _handle = bpy.types.SpaceView3D.draw_handler_add(
            get_, (), 'WINDOW',
            'POST_PIXEL')
        bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)
        bpy.types.SpaceView3D.draw_handler_remove(_handle, 'WINDOW')
        view3d.shading.show_xray = show_xray
        if 'is_in_model' in data:
            return data['is_in_model']
        return False

    @staticmethod
    def get_gpu_buffer(xy, wh=(1, 1), centered=False):
        """ 用于获取当前视图的GPU BUFFER
        :params xy: 获取的左下角坐标,带X 和Y信息
        :type xy: list or set
        :params wh: 获取的宽度和高度信息
        :type wh: list or set
        :params centered: 是否按中心获取BUFFER
        :type centered: bool
        :return bpy.gpu.Buffer: 返回活动的GPU BUFFER
        """

        if isinstance(wh, (int, float)):
            wh = (wh, wh)
        elif len(wh) < 2:
            wh = (wh[0], wh[0])

        x, y, w, h = int(xy[0]), int(xy[1]), int(wh[0]), int(wh[1])
        if centered:
            x -= w // 2
            y -= h // 2

        depth_buffer = gpu.state.active_framebuffer_get().read_depth(x, y, w, h)
        return depth_buffer

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

    @classmethod
    def gpu_depth_ray_cast(cls, x, y, data):
        size = cls.pref_().depth_ray_size

        _buffer = cls.get_gpu_buffer((x, y), wh=(size, size), centered=True)
        numpy_buffer = np.asarray(_buffer, dtype=np.float32).ravel()
        min_depth = np.min(numpy_buffer)
        data['is_in_model'] = (min_depth != (0 or 1))

    @cache
    def get_mouse_location_ray_cast(self, context, event):
        x, y = (event.mouse_region_x, event.mouse_region_y)
        view3d = context.space_data
        show_xray = view3d.shading.show_xray
        view3d.shading.show_xray = False
        data = {}
        sp = bpy.types.SpaceView3D
        han = sp.draw_handler_add(self.gpu_depth_ray_cast,
                                  (x, y, data), 'WINDOW',
                                  'POST_PIXEL')
        bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)
        sp.draw_handler_remove(han, 'WINDOW')
        view3d.shading.show_xray = show_xray
        log.debug('get_mouse_location_ray_cast\t' + str(data['is_in_model']))
        return data['is_in_model']

    @property
    def active_tool(self):
        return ToolSelectPanelHelper.tool_active_from_context(
            bpy.context)

    @property
    def active_tool_name(self):
        return self.active_tool.idname if self.active_tool else ''

    @property
    def is_builtin_brush_smooth_brush(self):
        return self.active_tool_name == 'builtin_brush.Smooth'


@cache
def all_operator_listen() -> list[str]:
    """反回所有操作符列表
    """
    from _bpy import ops as _ops_module
    _op_dir = _ops_module.dir
    submodules = set()
    for id_name in _op_dir():
        id_split = id_name.split("_OT_", 1)
        if len(id_split) == 2:
            submodules.add(id_split[0].lower() + '.' + id_split[1])
    return list(submodules)


def register_submodule_factory(submodule_tuple):
    def register():
        for mod in submodule_tuple:
            mod.register()

    def unregister():
        for mod in reversed(submodule_tuple):
            mod.unregister()

    return register, unregister


class PublicOperator(PublicClass, Operator):
    is_click: BoolProperty(name='按键操作是单击', default=True,
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

    def mouse_in_area_in(self, event, area):
        """输入一个event和xy的最大最小值,反回一个鼠标是否在此区域内的布尔值,如果在里面就反回True

        Args:
            event (bpy.types.Event): 输入操作符event
            area ((x,x),(y,y)): 输入x和y的坐标
        """
        x = area[0]
        y = area[1]
        mou_x, mou_y = self.mouse_co
        x_in = min(x) < mou_x < max(x)
        y_in = min(y) < mou_y < max(y)
        return x_in and y_in


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
            print(f'ERROR {self.filepath} 写入属性文件错误')
            print(e)
        return {'FINISHED'}
