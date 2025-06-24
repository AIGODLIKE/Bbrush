from math import degrees, radians

import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector, Euler, Matrix

from ..utils import get_pref, get_region_height, get_region_width

"""
上下两个方向需要考虑旋转
带轴的旋转改修改为以活动轴作为中心左右角度和上下角度
来对每个轴进行区分
"""


def get_draw_width_height() -> Vector:
    from ..src.view_navigation import texture_draw_size
    scale = get_pref().view_navigation_gizmo_scale
    w, h = texture_draw_size
    return Vector((int(w * scale), int(h * scale)))


def get_wh_view_rotation(wh):
    w, h = wh

    x = radians(45)
    z = {
        0: 0,
        1: -45,
        2: -90,
        3: -135,
        4: -180,
        5: 135,
        6: 90,
        7: 45,
    }.get(w)

    return Euler((h * x, 0, radians(z)), "XYZ").to_quaternion()


def from_axis_xy_angle_get_wh_index(axis, x, y) -> tuple[int, int]:
    """从轴的xy角度获取wh的索引"""


def get_view_matrix(context) -> Matrix:
    """获取视图的矩阵
    PERSP 透视
    ORTHO 正交
    """
    view_perspective = context.space_data.region_3d.view_perspective
    perspective_matrix = context.space_data.region_3d.perspective_matrix.inverted()
    view_matrix = context.space_data.region_3d.view_matrix.inverted()
    view_rotation_matrix = perspective_matrix if view_perspective == "ORTHO" else view_matrix
    return view_rotation_matrix


def get_2d_rotation_axis_xz(context) -> tuple[str, float, float]:
    view_rotation_matrix = get_view_matrix(context)
    view_perspective = context.space_data.region_3d.view_perspective

    origin = view_rotation_matrix @ Vector((0, 0, 0))
    view_v = view_rotation_matrix @ Vector((0, 0, 1))
    vector_direction = view_v, origin
    vector = ((origin - view_v) if view_perspective == "ORTHO" else (view_v - origin)).normalized()

    c = Vector((vector.y, vector.z))
    x_2d_angle = 0 if c == Vector((0, 0)) else c.angle_signed(Vector((0, 1)))

    e = Vector((vector.x, vector.y))
    y_2d_angle = 0 if e == Vector((0, 0)) else e.angle_signed(Vector((0, -1)))

    x, y, z = view_rotation_matrix.to_euler()
    x_angle, y_angle, z_angle = int(degrees(x)), int(degrees(y)), int(degrees(z))
    angle = x_angle, y_angle, z_angle

    min_length = 999
    active = None
    active_v = None
    for index, axis in enumerate(("X", "Y", "Z")):
        for b in (-1, 1):
            v = Vector((0, 0, 0))
            v[index] = b
            name = f"-{axis}" if b == -1 else axis
            length = (view_v - v).length
            if length < min_length:
                min_length = length
                active = name
                active_v = v

    if value := {
        "Z": {
            "X_PANEL": Vector((view_v.y, view_v.z)),
            "X_AXIS": Vector((0, 1)),
            "Y_PANEL": Vector((view_v.x, view_v.z)),
            "Y_AXIS": Vector((0, 1)),
        },
        "-Z": {
            "X_PANEL": Vector((view_v.y, view_v.z)),
            "X_AXIS": Vector((0, 1)),
            "Y_PANEL": Vector((view_v.x, view_v.z)),
            "Y_AXIS": Vector((0, 1)),
        },
        "-Y": {
            "X_PANEL": Vector((-view_v.z, -view_v.y)),
            "X_AXIS": Vector((0, 1)),
            "Y_PANEL": Vector((-view_v.z, view_v.x)),
            "Y_AXIS": Vector((0, 1)),
        },

    }.get(active):
        x_panel = value["X_PANEL"]
        x_axis = value["X_AXIS"]
        y_panel = value["Y_PANEL"]
        y_axis = value["Y_AXIS"]
        x_2d_angle = 0 if x_panel == Vector((0, 0)) else x_axis.angle_signed(x_panel)
        y_2d_angle = 0 if y_panel == Vector((0, 0)) else y_axis.angle_signed(y_panel)

    print()
    print("vector = ", vector.__repr__())
    print("vector_direction = ", vector_direction.__repr__())
    # print(min_length, active, active_v)
    return active, round(degrees(x_2d_angle), 2), round(degrees(y_2d_angle), 2)


def get_2d_rotation_xz(context) -> tuple[float, float]:
    view_rotation = context.space_data.region_3d.view_rotation
    z = Vector((0, 0, 1))
    z_l = z, Vector((0, 0, 0)),
    a = view_rotation @ z
    a_l = a, Vector((0, 0, 0))
    c = Vector((a.y, a.z))
    d = 0 if c == Vector((0, 0)) else c.angle_signed(Vector((0, 1)))

    y = Vector((0, -1, 0))
    y_l = y, Vector((0, 0, 0))
    e = Vector((a.x, a.y))

    f = 0 if e == Vector((0, 0)) else e.angle_signed(Vector((0, -1)))
    x, y, z = view_rotation.to_euler()
    x_angle, y_angle, z_angle = int(degrees(x)), int(degrees(y)), int(degrees(z))
    angle = x_angle, y_angle, z_angle

    # print("view_rotation = ", view_rotation.__repr__())
    # print("view_rotation_e = ", view_rotation.to_euler().__repr__())
    # print("x_angley_anglez_angle = ", angle.__repr__())
    # print("a = ", a.__repr__())
    # print("e = ", e.__repr__())
    # print("c = ", c.__repr__())
    # print("z_l = ", z_l)
    # print("y_l = ", y_l)
    # print()

    return round(degrees(d), 2), round(degrees(f), 2)


def get_hw_index_from_2d(context) -> tuple[int, int]:
    """通过3d视图转换成2d进行识别"""
    x_2d, z_2d = get_2d_rotation_xz(context)
    axis, x_2d, z_2d = get_2d_rotation_axis_xz(context)

    x_negative = x_2d < 0
    z_negative = z_2d < 0

    abs_x_angle = abs(x_2d)
    abs_z_angle = abs(z_2d)

    if z_negative:  # 负
        if abs_z_angle < 22.5:
            w_index = 0
        elif abs_z_angle < 67.5:
            w_index = 1
        elif abs_z_angle < 112.5:
            w_index = 2
        elif abs_z_angle < 157.5:
            w_index = 3
        else:
            w_index = 4
    else:
        if abs_z_angle < 22.5:
            w_index = 0
        elif abs_z_angle < 67.5:
            w_index = 7
        elif abs_z_angle < 112.5:
            w_index = 6
        elif abs_z_angle < 157.5:
            w_index = 5
        else:
            w_index = 4

    if x_negative:
        if abs_x_angle < 22.5:
            h_index = 4
        elif abs_x_angle < 67.5:
            h_index = 3
        elif abs_x_angle < 112.5:
            h_index = 2
        elif abs_x_angle < 157.5:
            h_index = 1
        else:
            h_index = 0
    else:
        if abs_x_angle < 22.5:
            h_index = 0
        else:
            h_index = (abs_x_angle - 22.5) // 45 + 1

    return w_index, h_index


class ViewNavigationGizmo(bpy.types.Gizmo):
    bl_idname = "VIEW3D_GT_view_navigation"
    bl_label = "VIEW3D_GT_view_navigation"
    bl_options = {"UNDO", "GRAB_CURSOR"}

    __slots__ = (
        "draw_points",
        "start_mouse",
        "last_mouse",
        "start_rotate",
        "rotate_index",  # (w, h)
    )

    @classmethod
    def poll(cls, context):
        return context.space_data and context.space_data.region_3d

    def draw(self, context):
        from ..utils import get_view_navigation_texture
        pref = get_pref()

        gpu.state.blend_set("ALPHA")
        texture = get_view_navigation_texture(*self.rotate_index)
        shader = gpu.shader.from_builtin("IMAGE")
        dw, dh = draw_size = get_draw_width_height()

        area = context.area
        area_wh = Vector((area.width, area.height))
        with gpu.matrix.push_pop():
            header_height = get_region_height(context, "HEADER") + get_region_height(context, "TOOL_HEADER")
            ui_width = get_region_width(context, "UI")  # + get_region_width(context, "HUD")
            area_offset = area_wh - draw_size
            draw_offset = Vector((-ui_width, -header_height)) + Vector(pref.view_navigation_gizmo_offset)
            offset = area_offset + draw_offset

            gpu.matrix.translate(offset)
            batch = batch_for_shader(
                shader, 'TRI_FAN',
                {
                    "pos": ((0, 0), (dw, 0), (dw, dh), (0, dh)),
                    "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),
                },
            )
            shader.uniform_sampler("image", texture)
            shader.bind()
            batch.draw(shader)

            x1, y1 = offset
            x2, y2 = offset + draw_size
            self.draw_points = ((x1, y1), (x2, y2))

        with gpu.matrix.push_pop():
            gpu.matrix.translate((0, -80))

            view_rotation = context.space_data.region_3d.view_rotation
            x, y, z = view_rotation.to_euler()
            x_angle, y_angle, z_angle = int(degrees(x)), int(degrees(y)), int(degrees(z))
            key = x_angle, y_angle, z_angle

            a = axis, x, y = get_2d_rotation_axis_xz(context)
            for text in (
                    context.area,
                    (dw, dh),
                    offset,
                    self.draw_points,
                    get_2d_rotation_xz(context),
                    a,
                    from_axis_xy_angle_get_wh_index(axis, x, y),
                    view_rotation.to_euler(),
                    key,
            ):
                blf.draw(0, str(text))
                gpu.matrix.translate((0, -20))

    def test_select(self, context, mouse_pos):
        if self.draw_points is None:
            return -1
        x, y = mouse_pos
        (x1, y1), (x2, y2) = self.draw_points
        x_ok = x1 < x < x2
        y_ok = y1 < y < y2
        # print(context.area, context, mouse_pos)
        return 0 if x_ok and y_ok else -1

    def setup(self):
        self.draw_points = ((0, 0), (0, 0))
        self.start_mouse = Vector((0, 0))
        self.rotate_index = (0, 0)

    def invoke(self, context, event):
        "C.screen.areas[3].spaces[0].region_3d.view_rotation = Euler((0,0,pi/2)).to_quaternion()"
        print("invoke", self)

        self.last_mouse = self.start_mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        self.start_rotate = context.space_data.region_3d.view_rotation

        self.update_view_rotate(context, self.rotate_index)
        self.refresh_rotate_index(context)
        return {'RUNNING_MODAL'}

    def exit(self, context, cancel):
        context.area.header_text_set(None)
        print("exit", cancel)
        if cancel:
            context.space_data.region_3d.view_rotation = self.start_rotate

    def modal(self, context, event, tweak):
        start_mouse = self.start_mouse
        mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        move = 20

        diff_x = mouse.x - start_mouse.x
        diff_y = mouse.y - start_mouse.y

        is_x = abs(diff_x) > move
        is_y = abs(diff_y) > move
        if event.type == "LEFTMOUSE" and event.value == "RELEASE":
            self.exit(context, False)
            return {"FINISHED"}
        if is_x or is_y:
            h, w = self.rotate_index
            if is_y:
                if diff_y > 0:
                    h += 1
                else:
                    h -= 1
                h = max(0, min(h, 4))
            elif is_x:
                if diff_x > 0:
                    w += 1
                else:
                    w -= 1

                print("aa w", w, diff_y)
                if w < 0:
                    w = 7
                elif w > 7:
                    w = 0
                w = max(0, min(w, 7))
                print("aa ff", w, diff_y)
            print("a", h, w)
            self.update_view_rotate(context, (h, w))
            self.rotate_index = (h, w)
            self.start_mouse = mouse

        # print("modal", self.rotate_index)
        return {'RUNNING_MODAL'}

    def refresh_rotate_index(self, context):
        view_rotation = context.space_data.region_3d.view_rotation
        x, y, z = view_rotation.to_euler()
        x_angle, y_angle, z_angle = int(degrees(x)), int(degrees(y)), int(degrees(z))
        key = x_angle, y_angle, z_angle

        if standard_view := {  # 标准视图 (x,y,z):(w, h)
            (90, 0, 0): (0, 2),  # 前
            (90, 0, 180): (4, 2),  # 后
            (90, 0, -90): (2, 2),  # 左
            (90, 0, 90): (6, 2),  # 右
            (0, 0, 0): (0, 0),  # 顶
            (180, 0, 0): (0, 4),  # 底

            (90, 0, -45): (1, 2),
            (90, 0, -135): (3, 2),
            (90, 0, 135): (5, 2),
            (90, 0, 45): (7, 2),
        }.get(key):
            self.rotate_index = standard_view
        else:
            w_index, h_index = get_hw_index_from_2d(context)

            if 0 > w_index < 7 and 0 > h_index < 4:
                self.rotate_index = (w_index, h_index)

    def update_view_rotate(self, context, rotate_index):
        rotation = get_wh_view_rotation(rotate_index)
        context.space_data.region_3d.view_rotation = rotation


def ui_scale():
    # return bpy.context.preferences.system.dpi * bpy.context.preferences.system.pixel_size / 72
    # since blender 4.0, the bpy.context.preferences.system.pixel_size will jump from 1~2 while the ui scale tweak from 1.18~1.19
    return bpy.context.preferences.system.dpi * 1 / 72


class ViewNavigationGizmoGroup(bpy.types.GizmoGroup):
    bl_idname = "VIEW3D_GT_view_navigation_group"
    bl_label = "Test Light Widget"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    bl_label = "View Gizmo"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'PERSISTENT', 'SCALE', 'SHOW_MODAL_ALL'}

    def draw_prepare(self, context):
        self.view_navigat.refresh_rotate_index(context)
        return
        # ui scale
        ui = ui_scale()
        region = context.region
        step = 30 * ui
        icon_scale = (80 * 0.35) / 2  # 14
        # 从屏幕右侧起
        start_x = region.width - (icon_scale * ui + step) / 2
        start_y = region.height

        # 检查是否启用区域重叠，若启用则加上宽度以符合侧面板移动
        if context.preferences.system.use_region_overlap:
            for region in context.area.regions:
                if region.type == 'UI':
                    start_x -= region.width
                elif region.type == 'HEADER':
                    start_y -= region.height

        # 检查是否开启坐标轴
        if context.preferences.view.mini_axis_type == 'MINIMAL':
            size = context.preferences.view.mini_axis_size * ui * 2  # 获取实际尺寸 此尺寸需要乘2
            start_y -= size + step * 2  #
        elif context.preferences.view.mini_axis_type == 'GIZMO':
            size = context.preferences.view.gizmo_size_navigate_v3d * ui * 1.2  # 获取实际尺寸 此尺寸需要乘1.2
            start_y -= size + step * 2  #
        elif context.preferences.view.mini_axis_type == 'NONE':
            start_y -= step * 2

            # 检查是否开启默认控件
        if context.preferences.view.show_navigate_ui:
            start_y -= (icon_scale * ui + step) * 3
        else:
            start_y -= step * 2 * ui

        for i, gz in enumerate(self.gizmos):
            gz.matrix_basis[0][3] = 100
            gz.matrix_basis[1][3] = 100
            gz.scale_basis = icon_scale

        context.area.tag_redraw()

    def setup(self, context):
        # 调整焦距控件
        self.view_navigat = gz = self.gizmos.new(ViewNavigationGizmo.bl_idname)
        gz.use_tooltip = True
        gz.use_draw_modal = True
        gz.alpha = .8
        gz.color = 0.08, 0.08, 0.08
        gz.color_highlight = 0.28, 0.28, 0.28
        gz.alpha_highlight = 0.8

        gz.scale_basis = (80 * 0.35) / 2  # Same as buttons defined in C

    def refresh(self, context):
        ob = context.object
        self.draw_prepare(context)
        self.view_navigat.refresh_rotate_index(context)


classes = (
    ViewNavigationGizmo,
    ViewNavigationGizmoGroup,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
