import time

from mathutils import Vector


class ManuallyManageEvents:
    """由于5.0版本的拖动事件触发不灵敏,所以需要手动管理
    但是这个没有处理长按的状态
    """

    start_mouse = None
    start_time = None

    def start_manually_manage_events(self,event):
        # 开始手动管理事件
        self.start_time = time.time()
        self.start_mouse = Vector((event.mouse_x, event.mouse_y))


    @property
    def event_running_time(self) -> float:
        return time.time() - self.start_time

    def check_is_moving(self, event) -> bool:
        now_mouse = Vector((event.mouse_x, event.mouse_y))
        is_move = event.type == "MOUSEMOVE" or now_mouse != self.start_mouse
        return is_move
