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

    with gpu.matrix.push_pop():

        gpu.matrix.reset()
        gpu.matrix.translate((-1, 1, 0))
        gpu.matrix.translate(cls.depth_buffer['translate'])

        depth_scale = cls.pref_().depth_scale
        gpu.matrix.scale((depth_scale, depth_scale))
        shader.uniform_sampler("image", depth_gpu_texture)
        batch.draw(shader)
