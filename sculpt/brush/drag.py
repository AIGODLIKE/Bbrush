import time

import bmesh
import bpy
import gpu
import numpy as np
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from ...adapter import sculpt_invert_hide_face
from ...utils import (
    check_mouse_in_model,
    check_mouse_in_depth_map_area,
    check_area_in_model,
    get_brush_shape,
    get_active_tool,
    refresh_ui,
    line_to_convex_shell,
)
from ...utils.gpu import draw_text, draw_line, draw_smooth_line


def lasso_mask(lasso_path, value, is_use_front_faces_only):
    path = [{
        'name': '',
        'loc': i,
        'time': 0
    } for i in lasso_path]
    bpy.ops.paint.mask_lasso_gesture(
        'EXEC_DEFAULT', True,
        path=path, value=value, use_front_faces_only=is_use_front_faces_only)


def lasso_hide(
        lasso_path,
        action,
        area,
        use_front_faces_only,
):
    path = [{
        'name': '',
        'loc': i,
        'time': 0
    } for i in lasso_path]
    bpy.ops.paint.hide_show_lasso_gesture(
        'EXEC_DEFAULT', True,
        path=path,
        action=action,
        area=area,
        use_front_faces_only=use_front_faces_only,
    )


class DragDraw:
    draw_handle = None
    shaders = {}

    mouse_start = None
    mouse_move = None
    mouse = None
    mouse_route = None  # 鼠标路径
    mouse_route_convex_shell = None

    is_reverse = None

    indices = ((0, 1, 2), (2, 1, 3))
    segments = 64
    alpha = 0.5

    @property
    def color(self):
        if self.brush_mode == "HIDE":
            if self.is_reverse:
                return Vector((.6, 0, 0, self.alpha))
            else:
                return Vector((0, .6, 0, self.alpha))
        elif self.brush_mode == "MASK":
            if self.is_reverse:
                return Vector((.5, .5, .5, self.alpha))
            else:
                return Vector((0, 0, 0, self.alpha))
        return Vector((0, 0, 0, self.alpha))

    def draw_drag(self):
        draw_text(100, 100)
        for batch, shader in self.shaders.items():
            shader.uniform_float("color", self.color)
            batch.draw(shader)
        getattr(self, f"draw_{self.shape.lower()}")()

    def draw_box(self):
        x1, y1 = self.mouse_start
        x2, y2 = self.mouse
        vertices = ((x1, y1), (x2, y1), (x1, y2), (x2, y2))
        # draw area
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = batch_for_shader(shader,
                                 'TRIS', {"pos": vertices},
                                 indices=self.indices)
        shader.bind()
        shader.uniform_float("color", self.color)
        batch.draw(shader)

        # draw line
        vertices = ((x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1))
        draw_line(vertices, (1, 1, 1, 1), line_width=2)

        # draw cross
        line_length = 5
        x = int((x1 + x2) / 2)
        y = int((y1 + y2) / 2)
        draw_line(((x - line_length, y), (x + line_length, y)),
                  (1, 1, 1, 1),
                  line_width=1)
        draw_line(((x, y - line_length), (x, y + line_length)),
                  (1, 1, 1, 1),
                  line_width=1)

        text = f'{self.brush_mode}{"-" if self.is_reverse else "+"}'
        draw_text(min(x1, x2) + 2,
                  max(y1, y2),
                  text=text,
                  font_id=1,
                  size=15,
                  color=(1, 1, 1, 1))

    def draw_lasso(self):
        lines = self.mouse_route + [self.mouse, self.mouse_route[0]]
        draw_smooth_line(lines, Vector((1, 1, 1, self.alpha)), line_width=1)

    def draw_polyline(self):
        lines = self.mouse_route + [self.mouse, ]
        draw_smooth_line(lines, Vector((1, 1, 1, self.alpha)), line_width=1)

    def init_draw(self, context, event):
        self.mouse = self.mouse_start = Vector((event.mouse_region_x, event.mouse_region_y))
        self.mouse_route = [self.mouse, ]
        self.mouse_move = Vector((0, 0))
        self.is_reverse = event.alt
        self.shaders = {}

    def register_draw(self):
        self.__class__.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.__class__.draw_drag, (self,), 'WINDOW',
                                                                            'POST_PIXEL')

    def unregister_draw(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.__class__.draw_handle, 'WINDOW')
        self.__class__.draw_handle = None
        self.shaders.clear()

    def preview_area(self, lines):
        start_v = None
        last_v = None
        bm = bmesh.new()
        for index, co in enumerate(lines):
            co = [*co[:], 0]
            if last_v is not None:
                last_v = bm.verts.new(co, last_v)
            else:
                last_v = bm.verts.new(co)
            last_v.index = index
            if start_v is None:
                start_v = last_v
        bm.edges.new((last_v, start_v))
        bm.faces.new(bm.verts)

        bmesh.ops.triangulate(bm, faces=bm.faces)

        shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        shader.bind()
        pos = [v.co[:2] for v in bm.verts]
        indices = [list(i.index for i in face.verts) for face in bm.faces]

        batch = batch_for_shader(shader, "TRIS", {"pos": pos}, indices=indices)
        self.shaders.clear()
        self.shaders[batch] = shader


class DragBase(DragDraw):
    brush_mode = None
    active_tool = None
    shape = None  # ELLIPSE,BOX,POLYLINE,LASSO,CIRCULAR

    def init_drag_event(self, context, event):
        from .. import brush_runtime
        (active_tool, WorkSpaceTool, index) = get_active_tool(context)
        self.active_tool = active_tool.idname
        self.shape = get_brush_shape(active_tool.idname)
        self.brush_mode = brush_runtime.brush_mode
        self.register_draw()
        self.init_draw(context, event)

    def exit(self, context):
        self.unregister_draw()
        refresh_ui(context)

    def get_shape_in_model_up(self, context):
        data = np.array(self.mouse_route, dtype=np.float32)
        data.reshape((data.__len__(), 2))
        max_co = data.max(axis=0)
        min_co = data.min(axis=0)
        x = int(min_co[0])
        y = int(min_co[1])
        w = int(max_co[0] - x)
        h = int(max_co[1] - y)

        return check_area_in_model(context, x, y, w, h)

    def check_brush_in_model(self, context) -> bool:
        """检查绘制的笔刷是否画在了模型上"""

        if self.shape == "BOX":
            x1, y1 = self.mouse_start
            x2, y2 = self.mouse
            w, h = self.mouse_start - self.mouse
            in_modal = check_area_in_model(context, min(x1, x2), min(y1, y2), abs(w), abs(h))
            return in_modal
        else:
            if len(self.mouse_route) > 2:
                return self.get_shape_in_model_up(context)
            else:
                return True

    def execute(self, context):
        in_model = self.check_brush_in_model(context)
        is_move_mouse = len(self.mouse_route) > 3
        value = -1 if self.is_reverse else 1

        print("execute,", in_model, self.shape, self.brush_mode)

        if self.shape == "BOX":
            x1, y1 = self.mouse_start
            x2, y2 = self.mouse
            box_args = {'xmin': int(min(x1, x2)),
                        'xmax': int(max(x1, x2)),
                        'ymin': int(min(y1, y2)),
                        'ymax': int(max(y1, y2)),
                        }
            if self.brush_mode == "MASK":
                if in_model:
                    bpy.ops.paint.mask_box_gesture(
                        'EXEC_DEFAULT',
                        True,
                        **box_args,
                        value=-1 if self.is_reverse else 1,
                        use_front_faces_only=True,  # TODO
                    )
                else:
                    bpy.ops.paint.mask_flood_fill('EXEC_DEFAULT', True, mode='VALUE', value=0)
            elif self.brush_mode == "HIDE":
                if in_model:
                    if self.is_reverse:
                        bpy.ops.paint.hide_show('EXEC_DEFAULT', True, action='HIDE', area="Inside", **box_args)
                    else:
                        bpy.ops.paint.hide_show('EXEC_DEFAULT', True, action='HIDE', area='OUTSIDE', **box_args)
                else:
                    sculpt_invert_hide_face()
        elif self.shape in ("LASSO", "POLYLINE"):
            if self.brush_mode == "MASK":
                if in_model:
                    if is_move_mouse:
                        lasso_mask(self.mouse_route_convex_shell, value, False)
                else:
                    bpy.ops.paint.mask_flood_fill('EXEC_DEFAULT', True, mode='VALUE', value=0)
            elif self.brush_mode == "HIDE":
                if in_model:
                    if is_move_mouse:
                        lasso_hide(self.mouse_route_convex_shell, value,
                                   "HIDE",
                                   "Inside",
                                   False,
                                   )
                else:
                    sculpt_invert_hide_face()
        else:
            ...
            # get_shape_in_model_up
        return {"FINISHED"}


class BrushDrag(bpy.types.Operator, DragBase):
    bl_idname = "bbrush.drag"
    bl_label = "Drag"
    bl_options = {"REGISTER"}

    click_time = None

    def update_box_shape(self, context, event):
        self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))

    def update_lasso_shape(self, context, event):
        mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        last_mouse = self.mouse_route[-1]
        if last_mouse != mouse and (last_mouse - mouse).length > 5:
            try:
                preview_mouse_route = [*self.mouse_route, mouse]
                self.mouse_route_convex_shell = lines = line_to_convex_shell(preview_mouse_route)

                self.preview_area(lines)

                self.mouse_route.append(mouse)
            except (ValueError, KeyError) as e:
                print(e.__repr__())
                ...

    def update_polyline_shape(self, context, event):
        self.mouse = mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        try:

            preview_mouse_route = [*self.mouse_route, mouse]
            self.mouse_route_convex_shell = lines = line_to_convex_shell(preview_mouse_route)
            self.preview_area(lines)
        except (ValueError, KeyError) as e:
            print(e.__repr__())
            ...

    def start_modal(self, context, event):
        self.click_time = time.time()
        self.init_drag_event(context, event)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        is_in_modal = check_mouse_in_model(context, event)
        active_tool = ToolSelectPanelHelper.tool_active_from_context(bpy.context)

        print(self.bl_label, is_in_modal, self.brush_mode, active_tool.idname)
        if self.__class__.draw_handle is not None:
            return {"FINISHED"}

        if check_mouse_in_depth_map_area(event):
            bpy.ops.bbrush.depth_scale("INVOKE_DEFAULT")  # 缩放深度图
            return {"FINISHED"}
        elif active_tool and active_tool.idname in (
                "builtin.box_mask",
                "builtin.box_hide",
                "builtin.lasso_mask",
                "builtin.polyline_mask",
        ):
            return self.start_modal(context, event)
        elif not is_in_modal:
            from .. import brush_runtime
            if brush_runtime and brush_runtime.brush_mode != "SCULPT":  # 不是雕刻并且不在模型上
                return self.start_modal(context, event)
            else:
                bpy.ops.view3d.rotate("INVOKE_DEFAULT")  # 旋转视图
                return {"FINISHED"}
        return {"PASS_THROUGH"}

    def modal(self, context, event):
        """        拖动的时候不在模型上拖,执行其它操作        """
        print("drag_event", self.shape, self.is_reverse, event.value, event.type, len(self.mouse_route))

        self.is_reverse = event.alt

        is_press = event.value == "PRESS"
        is_release = event.value == "RELEASE"

        is_left = event.type == "LEFTMOUSE"
        is_right = event.type == "RIGHTMOUSE"
        is_esc = event.type == "ESC"
        is_ctrl = event.type == "LEFT_CTRL"

        if is_press and is_ctrl:
            self.brush_mode = "MASK" if self.brush_mode == "HIDE" else "HIDE"

        if is_press and is_esc:
            self.exit(context)
            return {'CANCELLED'}
        elif self.shape == "POLYLINE":
            if res := self.polyline_update(context, event):
                return res
        elif is_release and is_left:
            self.exit(context)
            return self.execute(context)

        getattr(self, f"update_{self.shape.lower()}_shape")(context, event)

        refresh_ui(context)
        return {"RUNNING_MODAL"}

    def polyline_update(self, context, event):
        is_press = event.value == "PRESS"
        is_release = event.value == "RELEASE"

        is_left = event.type == "LEFTMOUSE"
        is_right = event.type == "RIGHTMOUSE"
        is_esc = event.type == "ESC"
        is_ctrl = event.type == "LEFT_CTRL"

        click_time = bpy.context.preferences.inputs.mouse_double_click_time
        if is_press and is_left:
            mouse = Vector((event.mouse_region_x, event.mouse_region_y))
            last_mouse = self.mouse_route[-1]
            if (click_time / 1000) > (time.time() - self.click_time) and mouse == last_mouse:  # 双击确定
                self.exit(context)
                return self.execute(context)

            if mouse not in self.mouse_route:
                self.mouse_route.append(mouse)
            self.click_time = time.time()
        elif is_press and is_right:
            if len(self.mouse_route) > 1:
                self.mouse_route.pop()
            else:
                self.exit(context)
                return {'CANCELLED'}
