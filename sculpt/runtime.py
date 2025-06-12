from mathutils import Vector


class BrushRuntime:
    left_mouse = Vector((0, 0))  # 偏移䃼尝用

    shortcut_key_points = []  # 快捷键绘制区域判断用

    # SCULPT,SMOOTH,HIDE,MASK,ORIGINAL
    brush_mode = "NONE"
