import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from ..utils import get_pref, get_region_height, get_region_width
from ..utils.navigation import *

"""
上下两个方向需要考虑旋转
带轴的旋转改修改为以活动轴作为中心左右角度和上下角度
来对每个轴进行区分
"""


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
        "is_hover",
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
        self.draw_tips(context)

    def draw_tips(self, context):
        pref = get_pref()
        if self.is_hover and pref.view_navigation_gizmo_show_tips:
            with gpu.matrix.push_pop():
                blf.position(0, 0, 0, 0)
                gpu.matrix.translate((context.area.width / 2, 0))

                asset_shelf = get_region_height(context, "ASSET_SHELF")
                asset_shelf_header = get_region_height(context, "ASSET_SHELF_HEADER")
                gpu.matrix.translate((0, asset_shelf + asset_shelf_header))

                for text in reversed((
                        "Bbrush view navigation",
                        " ",
                        "If you need to close it, you can adjust it in the addon preference settings",
                )):
                    gpu.matrix.translate((0, 10))
                    blf.draw(0, bpy.app.translations.pgettext_iface(text))

    def test_select(self, context, mouse_pos):
        if self.draw_points is None:
            return -1
        x, y = mouse_pos
        (x1, y1), (x2, y2) = self.draw_points
        x_ok = x1 < x < x2
        y_ok = y1 < y < y2
        is_hover = 0 if x_ok and y_ok else -1
        self.is_hover = is_hover == 0
        return is_hover

    def setup(self):
        self.is_hover = self.in_modal = False
        self.rotate_index = (0, 0)
        self.last_mouse = self.start_mouse = Vector((0, 0))
        self.draw_points = ((0, 0), (0, 0))

    def invoke(self, context, event):
        self.in_modal = True
        self.is_hover = False
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
