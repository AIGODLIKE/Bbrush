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

# Transparent texel border around each tile; with clamp-to-edge sampling everything outside the tile reads as transparent.
TEXTURE_PADDING = 1


def _neighbour_sum(data, kernel):
    """3x3 weighted neighbour sum over the first two axes (zero outside)."""
    h, w = data.shape[:2]
    padded = np.pad(data, ((1, 1), (1, 1)) + ((0, 0),) * (data.ndim - 2))
    result = np.zeros_like(data)
    for i in range(3):
        for j in range(3):
            result += kernel[i] * kernel[j] * padded[i:i + h, j:j + w]
    return result


def _smooth_tile(tile):
    """Pad a tile and anti-alias its 1-bit alpha edge (the source PNG is palettized)."""
    p = TEXTURE_PADDING
    out = np.pad(tile, ((p, p), (p, p), (0, 0)))
    rgb, alpha = out[..., :3], out[..., 3]

    # Bleed edge colours into transparent texels so softened/filtered edges have no fringe.
    for _ in range(2):
        weight = _neighbour_sum(alpha, (1, 1, 1))
        bleed = _neighbour_sum(rgb * alpha[..., None], (1, 1, 1))
        fill = (alpha <= 0) & (weight > 0)
        rgb[fill] = bleed[fill] / weight[fill][:, None]
        alpha = np.where(fill, 1e-6, alpha)

    out[..., 3] = _neighbour_sum(out[..., 3], (0.25, 0.5, 0.25))
    border = np.ones(out.shape[:2], dtype=bool)
    border[p:-p, p:-p] = False
    out[border, 3] = 0
    return out


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

        pad = TEXTURE_PADDING * 2
        temp_image = bpy.data.images.new(f"temp_{image_path}", wi + pad, hi + pad, alpha=True)
        for w in range(width_split):
            for h in range(height_split):
                key = (w, height_split - h - 1)

                data = sized_data[h * hi:(h + 1) * hi, w * wi:(w + 1) * wi, ::]
                if channels == 3:
                    data = np.concatenate((data, np.ones(data.shape[:2] + (1,), np.float32)), axis=2)
                temp_image.pixels.foreach_set(_smooth_tile(data).ravel())

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
