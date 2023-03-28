import bpy
import gpu
import numpy as np
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
from gpu_extras.batch import batch_for_shader

from . import PublicClass


class Buffer(PublicClass):

    @classmethod
    def gpu_depth_ray_cast(cls, x, y, data):
        size = cls.pref_().depth_ray_size

        buffer = cls.get_gpu_buffer((x, y), wh=(size, size), centered=True)
        numpy_buffer = np.asarray(buffer, dtype=np.float32).ravel()
        min_depth = np.min(numpy_buffer)
        data['is_in_model'] = (not (min_depth == (0 or 1)))


def get_active_operator():
    """反回活动工具的操作符属性

    Returns:
        _type_: _description_
    """
    context = bpy.context
    space_type, mode = ToolSelectPanelHelper._tool_key_from_context(
        context)

    cls = ToolSelectPanelHelper._tool_class_from_space_type(space_type)
    item, tool, icon_value = cls._tool_get_active(
        context, space_type, mode, with_icon=True)
    return tool
