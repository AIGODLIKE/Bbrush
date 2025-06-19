from math import degrees
from math import pi

import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector, Euler

from ..utils import get_pref, get_region_height, get_region_width


def get_draw_width_height() -> Vector:
    from ..src.view_navigation import texture_draw_size
    scale = get_pref().view_navigation_gizmo_scale
    w, h = texture_draw_size
    return Vector((int(w * scale), int(h * scale)))


def get_hw_view_rotation(hw):
    h, w = hw
    x, z = pi / 5, pi / 8,
    return Euler((h * x, 0, w * z), "XYZ").to_quaternion()


class ViewNavigationGizmo(bpy.types.Gizmo):
    bl_idname = "VIEW3D_GT_view_navigation"
    bl_label = "VIEW3D_GT_view_navigation"
    bl_options = {"UNDO", "GRAB_CURSOR"}

    __slots__ = (
        "draw_points",
        "start_mouse",
        "last_mouse",
        "start_rotate",
        "rotate_index",
        "start_rotate_index",
        # "now_rotate",
    )

    @classmethod
    def poll(cls, context):
        return context.space_data and context.space_data.region_3d

    def draw(self, context):
        from ..utils import get_view_navigation_texture
        pref = get_pref()

        texture = get_view_navigation_texture(*self.rotate_index)
        shader = gpu.shader.from_builtin('IMAGE')
        dw, dh = draw_size = get_draw_width_height()

        area = context.area
        area_wh = Vector((area.width, area.height))
        with gpu.matrix.push_pop():
            header_height = get_region_height(context, "HEADER") + get_region_height(context, "TOOL_HEADER")
            ui_width = get_region_width(context, "UI") + get_region_width(context, "HUD")
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
            blf.draw(0, str(context.area))
            gpu.matrix.translate((0, 10))
            blf.draw(0, str((dw, dh)))
            gpu.matrix.translate((0, -50))
            blf.draw(0, str(offset))
            gpu.matrix.translate((0, -100))
            blf.draw(0, str(self.draw_points))

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

        self.last_mouse = self.start_mouse = Vector((event.mouse_region_x, 0))
        self.start_rotate = context.space_data.region_3d.view_rotation
        self.start_rotate_index = self.rotate_index

        self.update_view_rotate(context, self.start_rotate_index)
        self.refresh_rotate_index(context)
        return {'RUNNING_MODAL'}

    def exit(self, context, cancel):
        context.area.header_text_set(None)
        print("exit")
        self.draw_points = None
        if cancel:
            context.space_data.region_3d.view_rotation = self.start_rotate

    def modal(self, context, event, tweak):
        # if event.
        if event.type == "LEFTMOUSE" and event.value == "RELEASE":
            self.exit(context, False)
            return {"FINISHED"}
        print("modal")
        return {'RUNNING_MODAL'}

    def refresh_rotate_index(self, context):
        # C.screen.areas[3].spaces[0].region_3d.view_rotation = Euler((pi/2,0,0)).to_quaternion()
        ox, _, oz, = x, _, z = context.space_data.region_3d.view_rotation.to_euler()

        xa, za = degrees(x), degrees(z)

        abs_x = abs(xa)
        abs_z = abs(za)
        if xa < 0:  # 负
            if abs_x < 90:
                xi = 0
            else:
                xi = 5
        else:
            if abs_x < 22.5:
                xi = 0
            else:
                xi = (abs_x - 22.5) // 45 + 1

        if za < 0:  # 负
            if abs_z < 22.5:
                zi = 0
            else:
                zi = abs_z // 45
        else:
            if abs_z < 22.5:
                zi = 0
            else:
                zi = 7 - ((abs_z - 22.5) // 45)

        xi = int(xi)
        zi = int(zi)

        print(xi, zi, x, z, "\t", xa, za)  # "\t", abs_x, abs_z

        if xi < 0 or xi > 4:
            return
        if zi < 0 or zi > 7:
            return
        self.rotate_index = (xi, zi)

    def update_view_rotate(self, context, rotate_index):
        rotation = get_hw_view_rotation(rotate_index)
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
