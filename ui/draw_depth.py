import bpy
import gpu
import numpy as np
from mathutils import Matrix
from gpu_extras.batch import batch_for_shader

from ..utils.public import PublicClass


def get_coord(st=(-1, -1), interval=(2, 2)):
    """输入一个起始坐标,反回一个坐标列表,三角面连接顺序是(0, 1, 2), (2, 0, 3)
    从左下到右上
    Args:
        st (tuple, optional): 输入的x和y的坐标. Defaults to (0, 0).
        interval (tuple, optional): 输入对角的相差坐标. Defaults to (2, 2).
    """
    x = st[0]
    y = st[1]
    int_x = interval[0]
    int_y = interval[1]
    return (
        (x, y), (x + int_x, y),
        (x + int_x, y + int_y), (x, y + int_y)
    )


def depth_shader():
    vertex_shader = '''
        uniform mat4 ModelViewProjectionMatrix;
        in vec2 pos;
        in vec2 texCoordIn;
        out vec2 texCoord;

        void main()
        {
            texCoord = texCoordIn;
            gl_Position = ModelViewProjectionMatrix * vec4(pos.xy, 0.0f, 1.0f);
        }
    '''

    fragment_shader = '''
        uniform sampler2D tex;
        in vec2 texCoord;
        out vec4 FragColor;

        void main()
        {
            FragColor = texture(tex, texCoord);
            if (FragColor.x != 1.0f)
                FragColor.xyz = vec3(0.0f,0.0f,0.0f);
            else
                FragColor.xyz = vec3(1.0f,1.0f,1.0f);
            FragColor.w = 1;

        }
    '''

    shader = gpu.types.GPUShader(vertex_shader, fragment_shader)
    batch = batch_for_shader(
        shader, 'TRIS',
        {
            "pos": get_coord(st=(0, -1), interval=(1, 1)),
            "texCoordIn": (
                (0, 0), (1, 0),
                (1, 1), (0, 1)),
        },
        indices=((0, 1, 2), (2, 0, 3))
    )
    batch.program_set(shader)
    shader.bind()
    return shader, batch


def reset_post_pixel_matrix(context):
    w = 2 / context.area.width
    h = 2 / context.area.height
    view_matrix = Matrix([[w, 0, 0, -1],
                          [0, h, 0, -1],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]])
    gpu.matrix.reset()
    gpu.matrix.load_matrix(view_matrix)
    gpu.matrix.load_projection_matrix(Matrix.Identity(4))


def get_toolbar_width(rt='TOOLS'):
    """
    enum in ['WINDOW', 'HEADER', 'CHANNELS', 'TEMPORARY', 'UI', 'TOOLS', 'TOOL_PROPS',
        'PREVIEW', 'HUD', 'NAVIGATION_BAR', 'EXECUTE', 'FOOTER', 'TOOL_HEADER', 'XR']
    rt = regions_type

    """
    for i in bpy.context.area.regions:
        if i.type == rt:
            if rt == 'TOOLS':
                return i.width
            elif rt == 'HEADER':
                return i.height


def draw_shader_old(width, height):
    shader, batch = depth_shader()
    depth_buffer = gpu.state.active_framebuffer_get().read_depth(0,
                                                                 0,
                                                                 width,
                                                                 height,
                                                                 )
    texture = gpu.types.GPUTexture(
        (width, height), format='DEPTH_COMPONENT32F', data=depth_buffer)

    mv = gpu.matrix.get_model_view_matrix()
    shader.uniform_float('ModelViewProjectionMatrix', mv)
    shader.uniform_sampler("tex", texture)
    batch.draw()


class DrawDepth(PublicClass):
    depth_buffer = {}

    @classmethod
    def register(cls):
        cls._draw_depth_handel = bpy.types.SpaceView3D.draw_handler_add(
            cls.draw_depth, (), 'WINDOW', 'POST_PIXEL')

    @classmethod
    def unregister(cls):
        bpy.types.SpaceView3D.draw_handler_remove(cls._draw_depth_handel, 'WINDOW')

    @classmethod
    def draw_gpu_buffer_new_buffer_funcs(cls, sam_width, sam_height, width, height, sampling):
        gpu.state.depth_mask_set(False)

        if (width, height) not in cls.depth_buffer:
            cls.depth_buffer.clear()
            depth = np.empty(shape=(width * height), dtype=np.float32)
            depth_buffer = gpu.types.Buffer('FLOAT', height * width, depth)
            sam_all_depth = np.empty(shape=(sam_height, sam_width, 3),
                                     dtype=np.float32)
            pos = ((0, -1), (0, 0), (1, 0), (1, -1))
            tex_coord = ((0, 0), (0, 1), (1, 1), (1, 0))

            shader = gpu.shader.from_builtin('2D_IMAGE')
            batch = batch_for_shader(
                shader,
                'TRI_FAN',
                {
                    "pos": pos,
                    "texCoord": tex_coord
                },
            )
            cls.depth_buffer[(width, height)] = [
                depth, depth_buffer, sam_all_depth, shader, batch
            ]
        else:
            depth, depth_buffer, sam_all_depth, shader, batch = cls.depth_buffer[(
                width, height)]
            gpu.state.active_framebuffer_get().read_depth(0,
                                                          0,
                                                          width,
                                                          height,
                                                          data=depth_buffer)
            sam_all_depth[:, :, 0] = sam_all_depth[:, :, 1] = sam_all_depth[:, :, 2] = sum(

                (depth.reshape(height, width)[i::sampling, ::sampling]
                 for i in range(sampling))) / sampling

        sam_all_depth = np.floor(sam_all_depth.ravel())

        sam_all_depth_buffer = gpu.types.Buffer('FLOAT', sam_width * sam_height * 3,
                                                sam_all_depth)
        depth_gpu_texture = gpu.types.GPUTexture((sam_width, sam_height),
                                                 format='RGB16F',
                                                 data=sam_all_depth_buffer)

        mv = gpu.matrix.get_model_view_matrix()
        p = gpu.matrix.get_projection_matrix()

        gpu.matrix.reset()
        gpu.matrix.translate((-1, 1, 0))
        gpu.matrix.translate(cls.depth_buffer['translate'])

        depth_scale = cls.pref_().depth_scale
        gpu.matrix.scale((depth_scale, depth_scale))
        shader.uniform_sampler("image", depth_gpu_texture)
        batch.draw(shader)

        gpu.matrix.load_projection_matrix(p)
        gpu.matrix.load_matrix(mv)

    @classmethod
    def draw_gpu_buffer(cls, context):
        gpu.state.depth_mask_set(False)

        mv = gpu.matrix.get_model_view_matrix()
        p = gpu.matrix.get_projection_matrix()
        depth_scale = cls.pref_().depth_scale

        gpu.matrix.reset()
        gpu.matrix.translate((-1, 1, 0))
        gpu.matrix.translate(cls.depth_buffer['translate'])
        gpu.matrix.scale((depth_scale, depth_scale))

        draw_shader_old(context.region.width,
                        context.region.height)  # 使用自定义着色器绘制,将会快很多

        gpu.matrix.load_projection_matrix(p)
        gpu.matrix.load_matrix(mv)

    @classmethod
    def draw_depth(cls):
        context = bpy.context
        pref = cls.pref_()
        mode = pref.depth_display_mode
        is_sculpt = (context.mode == 'SCULPT')
        always = (mode == 'ALWAYS_DISPLAY')
        only_sculpt = ((mode == 'ONLY_SCULPT') and is_sculpt)
        only_bbrush = ((mode == 'ONLY_BBRUSH') and is_sculpt and pref.sculpt)

        is_draw = (always or only_sculpt or only_bbrush)
        depth_scale = pref.depth_scale
        if is_draw:
            width = context.region.width
            height = context.region.height

            toolbar_width = get_toolbar_width() + pref.depth_offset_x
            header_height = get_toolbar_width(rt='HEADER') + pref.depth_offset_y
            x1 = toolbar_width
            y1 = height - header_height
            x2 = int(width / 2 * depth_scale) + toolbar_width
            y2 = height - int(height / 2 * depth_scale) - header_height
            # 添加坐标 存起来笔刷的操作符判断鼠标有没有放在深度图上使用
            cls.depth_buffer['wh'] = ((x1, x2), (y1, y2))

            w = 1 / width * toolbar_width * 2
            h = 1 / height * header_height * 2
            cls.depth_buffer['translate'] = (w, -h, 0)
            cls.draw_gpu_buffer(context)

            """
            draw_gpu_buffer_new_buffer_funcs(sam_width, sam_height, width, height, sampling)
            """
        else:
            cls.depth_buffer = {}


def register():
    DrawDepth.register()


def unregister():
    DrawDepth.unregister()
