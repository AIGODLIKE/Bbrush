import bpy

"""
TOTO
将整个模态作为一个操作符
进入BBrush模式即进入操作符模态
将所有内容退出
"""

brush_runtime = None


class BbrushSculpt(bpy.types.Operator):
    bl_idname = 'bbrush.bbrush_sculpt'
    bl_label = 'Bbrush sculpting'
    bl_description = 'Sculpting in the style of Zbrush'
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        global brush_runtime

        # 确保只有一个运行时
        if brush_runtime is not None:
            return {'CANCELLED'}
        brush_runtime = self

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        return {'RUNNING_MODAL'}

    def execute(self, context):
        return {"FINISHED"}


def register():
    ...


def unregister():
    ...
