import bpy
import gpu
import numpy
import numpy as np

# 8 * 5
texture_cache = {
    # (i,j): texture
}

ws, hs = 8, 5

texture_draw_size = (235, 256)


def load_vn_image(image_path: str) -> bool:
    """反回是否加载正确的布尔值"""
    global texture_cache, texture_draw_size
    try:
        texture_dict = {}

        image = bpy.data.images.load(image_path, check_existing=True)
        w, h = image.size

        channels = image.channels
        pixels_len = w * h * channels

        np_data = numpy.zeros(pixels_len, dtype=np.float32)
        image.pixels.foreach_get(np_data)

        sized_data = np_data.reshape((h, w, channels))
        wf, hf = w / ws, h / hs
        wi, hi = int(wf), int(hf)  # 235 256
        assert wi == wf
        assert hi == hf
        # print(len(np_data), pixels_len, len(image.pixels))
        # print(wi, hi)
        temp_image = bpy.data.images.new(f"temp_{image_path}", wi, hi)
        for j in range(hs):
            for i in range(ws):
                data = sized_data[j * hi:(j + 1) * hi, i * wi:(i + 1) * wi, ::]
                temp_image.pixels.foreach_set(data.ravel())
                texture_dict[(i, j)] = gpu.texture.from_image(temp_image)

        for im in [image, temp_image]:
            bpy.data.images.remove(im)

        texture_draw_size = (wi, hi)
        texture_cache.clear()
        texture_cache.update(texture_dict)
        return True
    except RuntimeError as e:
        print("loading image failed", image_path, e.args)
    return False


def register():
    ...


def unregister():
    texture_cache.clear()
