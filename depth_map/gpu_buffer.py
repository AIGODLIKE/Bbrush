from functools import cache

import blf
import gpu
from gpu_extras.batch import batch_for_shader

from ..utils import get_pref


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


@cache
def depth_shader():
    vertex_shader = """
        uniform mat4 ModelViewProjectionMatrix;
        in vec2 pos;
        in vec2 texCoordIn;
        out vec2 texCoord;

        void main()
        {
            texCoord = texCoordIn;
            gl_Position = ModelViewProjectionMatrix * vec4(pos.xy, 0.0f, 1.0f);
        }
    """

    fragment_shader = """
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
    """

    shader = gpu.types.GPUShader(vertex_shader, fragment_shader)
    batch = batch_for_shader(
        shader, "TRIS",
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


gpu_cache = {}  # 优化性能


def draw_shader_old(region_hash, width, height):
    shader, batch = depth_shader()
    key = region_hash, width, height

    if key in gpu_cache:
        texture = gpu_cache[key]
    else:
        depth_buffer = gpu.state.active_framebuffer_get().read_depth(0, 0, width, height)
        texture = gpu.types.GPUTexture((width, height), format="DEPTH_COMPONENT32F", data=depth_buffer)

        gpu_cache.clear()
        gpu_cache[key] = texture
        # print("refresh depth map")

    mv = gpu.matrix.get_model_view_matrix()
    shader.uniform_float("ModelViewProjectionMatrix", mv)
    shader.uniform_sampler("tex", texture)
    batch.draw()


def draw_box(x1, x2, y1, y2):
    indices = ((0, 1, 2), (2, 1, 3))
    color = [0, 0, 0, 0.5]

    vertices = ((x1, y1), (x2, y1), (x1, y2), (x2, y2))
    # draw area
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    batch = batch_for_shader(shader,
                             'TRIS', {"pos": vertices},
                             indices=indices)
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


def draw_gpu_buffer(context, depth_buffer):
    gpu.state.depth_mask_set(False)

    depth_scale = get_pref().depth_scale
    if "draw_error" not in depth_buffer:
        with gpu.matrix.push_pop():
            gpu.matrix.scale([2, 2])
            gpu.matrix.translate([-0.5, -0.5, 0])
            gpu.matrix.translate(depth_buffer["translate"])
            gpu.matrix.scale([depth_scale, depth_scale])
            try:
                draw_shader_old(
                    str(hash(context.region)),
                    context.region.width,
                    context.region.height)  # 使用自定义着色器绘制,将会快很多
            except Exception as e:
                return e.args
    else:
        error_text = depth_buffer["draw_error"]
        draw_box(*depth_buffer["draw_box"])
        x, y = depth_buffer["text_location"]
        font_id = 0
        blf.position(font_id, x, y, 0)
        blf.draw(font_id, error_text + f"{x} {y}")
        blf.position(font_id, x, y + 20, 0)
        blf.draw(font_id, "Drag Depth Map Error")


def clear_gpu_cache():
    global gpu_cache
    gpu_cache.clear()
