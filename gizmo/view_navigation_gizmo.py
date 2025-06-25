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


def get_draw_view_navigation_texture_width_height() -> Vector:
    """获取绘制纹理的宽高
    :return: Vector
    """
    from ..src.view_navigation import texture_draw_size
    scale = get_pref().view_navigation_gizmo_scale
    w, h = texture_draw_size
    return Vector((int(w * scale), int(h * scale)))


def get_wh_view_rotation(wh):
    """通过视图纹理的索引获取需要旋转的值"""
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


def get_view_matrix(context) -> Matrix:
    """获取视图的矩阵
    通过当前视图类型反回对应的矩阵
    PERSP 透视
    ORTHO 正交
    """
    view_perspective = context.space_data.region_3d.view_perspective
    perspective_matrix = context.space_data.region_3d.perspective_matrix.inverted()
    view_matrix = context.space_data.region_3d.view_matrix.inverted()
    view_rotation_matrix = perspective_matrix if view_perspective == "ORTHO" else view_matrix
    return view_rotation_matrix


def get_2d_rotation_axis_xy_angle(context) -> tuple[str, float, float]:
    """
    通过3D最近轴
    再将位置转换为2D坐标 2D计算旋转获取
    轴朝向和角度
    """
    view_rotation_matrix = get_view_matrix(context)
    view_perspective = context.space_data.region_3d.view_perspective

    origin = view_rotation_matrix @ Vector((0, 0, 0))  # 原点
    view_v = view_rotation_matrix @ Vector((0, 0, 1))  # 朝向点
    vector = ((origin - view_v) if view_perspective == "ORTHO" else (view_v - origin)).normalized()  # 最终方向矢量

    # 查找最近的轴向点
    min_length = 9999
    active = None
    for index, axis in enumerate(("X", "Y", "Z")):
        for b in (-1, 1):
            v = Vector((0, 0, 0))
            v[index] = b
            v = Matrix.Translation(origin) @ v
            if view_perspective == "ORTHO":
                name = f"-{axis}" if b != -1 else axis
            else:
                name = f"-{axis}" if b == -1 else axis

            length = (view_v - v).length
            if length < min_length:
                min_length = length
                active = name

    axis_2d_vector = Vector((0, 1))
    if value := {  # 通过每个轴向转换为2d坐标以进行带有符号的角度计算
        "Z": (Vector((vector.y, vector.z)), Vector((vector.x, vector.z)),),
        "-Z": (Vector((-vector.y, -vector.z)), Vector((vector.x, -vector.z)),),
        "-Y": (Vector((vector.z, -vector.y)), Vector((vector.x, -vector.y)),),
        "Y": (Vector((vector.z, vector.y)), Vector((-vector.x, vector.y)),),
        "X": (Vector((vector.z, vector.x)), Vector((vector.y, vector.x)),),
        "-X": (Vector((vector.z, -vector.x)), Vector((-vector.y, -vector.x)),)
    }.get(active):
        x_panel, y_panel = value
        x_2d_angle = 0 if x_panel == Vector((0, 0)) else axis_2d_vector.angle_signed(x_panel)
        y_2d_angle = 0 if y_panel == Vector((0, 0)) else axis_2d_vector.angle_signed(y_panel)

        return active, round(degrees(x_2d_angle), 2), round(degrees(y_2d_angle), 2)
    return active, 0, 0


def from_2d_get_axis_and_index(context) -> tuple[str, int, int]:
    """通过轴和2D的角度获取对应的2D坐标系 3*3"""
    axis, x_2d, y_2d = get_2d_rotation_axis_xy_angle(context)

    if x_2d > 22.5:
        x_index = 0
    elif x_2d < -22.5:
        x_index = 2
    else:
        x_index = 1

    if y_2d > 22.5:
        y_index = 2
    elif y_2d < -22.5:
        y_index = 0
    else:
        y_index = 1

    return axis, x_index, y_index


def get_hw_index_from_2d(context) -> tuple[int, int]:
    """
    视图矢量 -> 轴向,2D角度 -> 轴向,2D索引 -> 导航纹理索引
    """
    axis, x_2d_index, y_2d_index = from_2d_get_axis_and_index(context)
    key = (x_2d_index, y_2d_index)
    if value := {
        "X": {
            (0, 0): (7, 1),
            (0, 1): (6, 1),
            (0, 2): (5, 1),
            (1, 0): (7, 2),
            (1, 1): (6, 2),
            (1, 2): (5, 2),
            (2, 0): (7, 3),
            (2, 1): (6, 3),
            (2, 2): (5, 3),
        },
        "-X": {
            (0, 0): (3, 1),
            (0, 1): (2, 1),
            (0, 2): (1, 1),
            (1, 0): (3, 2),
            (1, 1): (2, 2),
            (1, 2): (1, 2),
            (2, 0): (3, 3),
            (2, 1): (2, 3),
            (2, 2): (1, 3),
        },
        "Y": {
            (0, 0): (5, 1),
            (0, 1): (4, 1),
            (0, 2): (3, 1),
            (1, 0): (5, 2),
            (1, 1): (4, 2),
            (1, 2): (3, 2),
            (2, 0): (5, 3),
            (2, 1): (4, 3),
            (2, 2): (3, 3),
        },
        "-Y": {
            (0, 0): (1, 1),
            (0, 1): (0, 1),
            (0, 2): (7, 1),
            (1, 0): (1, 2),
            (1, 1): (0, 2),
            (1, 2): (7, 2),
            (2, 0): (1, 3),
            (2, 1): (0, 3),
            (2, 2): (7, 3),
        },
        "Z": {
            (0, 0): (3, 1),
            (0, 1): (4, 1),
            (0, 2): (5, 1),
            (1, 0): (2, 1),
            (1, 1): (0, 0),
            (1, 2): (6, 1),
            (2, 0): (1, 1),
            (2, 1): (0, 1),
            (2, 2): (7, 1),
        },
        "-Z": {
            (0, 0): (1, 3),
            (0, 1): (0, 3),
            (0, 2): (7, 3),
            (1, 0): (2, 3),
            (1, 1): (4, 4),
            (1, 2): (6, 3),
            (2, 0): (3, 3),
            (2, 1): (4, 3),
            (2, 2): (5, 3),
        },
    }.get(axis):
        if wh_index := value.get(key):
            w, h = wh_index
            if axis in ("Z", "-Z") and key == (1, 1):
                view_rotation_matrix = get_view_matrix(context)
                x, y, z = view_rotation_matrix.to_euler()
                z_angle = degrees(z)

                abs_z_angle = abs(z_angle)
                if z_angle < 0:  # 负
                    if abs_z_angle < 22.5:
                        w = 0
                    elif abs_z_angle < 67.5:
                        w = 1
                    elif abs_z_angle < 112.5:
                        w = 2
                    elif abs_z_angle < 157.5:
                        w = 3
                    else:
                        w = 4
                else:
                    if abs_z_angle < 22.5:
                        w = 0
                    elif abs_z_angle < 67.5:
                        w = 7
                    elif abs_z_angle < 112.5:
                        w = 6
                    elif abs_z_angle < 157.5:
                        w = 5
                    else:
                        w = 4
            return w, h
    return 0, 0


def update_view_rotate(context, rotate_index):
    rotation = get_wh_view_rotation(rotate_index)
    context.space_data.region_3d.view_rotation = rotation


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
        "in_modal",
    )

    @classmethod
    def poll(cls, context):
        return context.space_data and context.space_data.region_3d

    def draw(self, context):
        from ..utils import get_view_navigation_texture
        pref = get_pref()
        gpu.state.blend_set("ALPHA")
        texture = get_view_navigation_texture(*self.rotate_index)
        dw, dh = draw_size = get_draw_view_navigation_texture_width_height()

        area = context.area
        area_wh = Vector((area.width, area.height))
        with gpu.matrix.push_pop():
            header_height = get_region_height(context, "HEADER") + get_region_height(context, "TOOL_HEADER")
            ui_width = get_region_width(context, "UI")  # + get_region_width(context, "HUD")
            area_offset = area_wh - draw_size
            draw_offset = Vector((-ui_width, -header_height)) + Vector(pref.view_navigation_gizmo_offset)
            offset = area_offset + draw_offset

            gpu.matrix.translate(offset)

            shader = gpu.shader.from_builtin("IMAGE")
            batch = batch_for_shader(
                shader, "TRI_FAN",
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

        if pref.debug:
            with gpu.matrix.push_pop():
                gpu.matrix.translate((0, -80))

                view_rotation_matrix = get_view_matrix(context)
                x, y, z = view_rotation_matrix.to_euler()
                x_angle, y_angle, z_angle = int(degrees(x)), int(degrees(y)), int(degrees(z))
                key = x_angle, y_angle, z_angle

                a = get_2d_rotation_axis_xy_angle(context)
                for text in (
                        context.area,
                        (dw, dh),
                        offset,
                        self.draw_points,
                        a,
                        from_2d_get_axis_and_index(context),
                        get_hw_index_from_2d(context),
                        view_rotation_matrix.to_euler(),
                        key,
                        self.rotate_index,
                ):
                    blf.draw(0, str(text))
                    gpu.matrix.translate((0, -20))

    def draw_select(self, context, select_id):
        self.draw(context)

    def test_select(self, context, mouse_pos):
        if self.draw_points is None:
            return -1
        x, y = mouse_pos
        (x1, y1), (x2, y2) = self.draw_points
        x_ok = x1 < x < x2
        y_ok = y1 < y < y2
        return 0 if x_ok and y_ok else -1

    def setup(self):
        self.in_modal = False
        self.rotate_index = (0, 0)
        self.start_mouse = Vector((0, 0))
        self.draw_points = ((0, 0), (0, 0))

    def invoke(self, context, event):
        self.in_modal = True
        self.start_rotate = context.space_data.region_3d.view_rotation
        self.last_mouse = self.start_mouse = Vector((event.mouse_region_x, event.mouse_region_y))

        update_view_rotate(context, self.rotate_index)
        self.refresh_rotate_index(context)
        return {"RUNNING_MODAL"}

    def exit(self, context, cancel):
        context.area.header_text_set(None)
        self.in_modal = False
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
            w, h = self.rotate_index
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

                if w < 0:
                    w = 7
                elif w > 7:
                    w = 0
                w = max(0, min(w, 7))
            self.start_mouse = mouse
            self.rotate_index = (w, h)
            update_view_rotate(context, (w, h))

        return {"RUNNING_MODAL"}

    def refresh_rotate_index(self, context):
        if self.in_modal:
            return
        w_index, h_index = get_hw_index_from_2d(context)

        if 0 <= w_index < 8 and 0 <= h_index < 5:
            self.rotate_index = (w_index, h_index)


class ViewNavigationGizmoGroup(bpy.types.GizmoGroup):
    bl_idname = "VIEW3D_GT_view_navigation_group"
    bl_label = "View Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"PERSISTENT", "SCALE", "SHOW_MODAL_ALL"}

    @classmethod
    def poll(cls, context):
        pref = get_pref()
        return pref.check_depth_map_is_draw(context)

    def draw_prepare(self, context):
        """context.area.tag_redraw() #在这里刷新会影响绘制速度"""
        self.view_navigation_gizmo.refresh_rotate_index(context)

    def setup(self, context):
        # 调整焦距控件
        self.view_navigation_gizmo = gz = self.gizmos.new(ViewNavigationGizmo.bl_idname)
        gz.use_draw_modal = True

    def refresh(self, context):
        self.view_navigation_gizmo.refresh_rotate_index(context)


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
