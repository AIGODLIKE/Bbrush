import bpy
import gpu
import numpy
import numpy as np

from ...utils.gpu import apply_gpu_texture_filter

# 8 * 5
texture_cache = {
    # (i,j): texture
}

texture_draw_size = (235, 256)


def load_view_navigation_image(image_path: str) -> bool:
    """Return True when image load succeeded."""
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

        width_split, height_split = 8, 5
        wf, hf = w / width_split, h / height_split
        wi, hi = int(wf), int(hf)  # 235 256
        assert wi == wf
        assert hi == hf

        temp_image = bpy.data.images.new(f"temp_{image_path}", wi, hi)
        for w in range(width_split):
            for h in range(height_split):
                key = (w, height_split - h - 1)

                data = sized_data[h * hi:(h + 1) * hi, w * wi:(w + 1) * wi, ::]
                temp_image.pixels.foreach_set(data.ravel())

                texture_dict[key] = gpu.texture.from_image(temp_image)
                apply_gpu_texture_filter(texture_dict[key])

        for im in [image, temp_image]:
            bpy.data.images.remove(im)

        texture_draw_size = (wi, hi)
        texture_cache.clear()
        texture_cache.update(texture_dict)
        return True
    except RuntimeError as e:
        from ...utils import get_pref
        pref = get_pref()
        if pref is not None and pref.debug:
            print("loading image failed", image_path, e.args)
    return False


def register():
    ...


def unregister():
    from ...utils import clear_view_navigation_texture_cache
    texture_cache.clear()
    clear_view_navigation_texture_cache()
