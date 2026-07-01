import time

from mathutils import Vector

from . import get_pref


class ManuallyManageEvents:
    """Manual click/drag detection; Blender 5.0+ CLICK_DRAG is unreliable. Long-press not handled."""

    start_mouse = None
    start_time = None

    def start_manually_manage_events(self,event):
        # Start tracking press position/time
        self.start_time = time.time()
        self.start_mouse = Vector((event.mouse_x, event.mouse_y))


    @property
    def event_running_time(self) -> float:
        return time.time() - self.start_time

    def check_is_moving(self, event) -> bool:
        if self.start_mouse is None:
            return False
        now_mouse = Vector((event.mouse_x, event.mouse_y))
        dist = (now_mouse - self.start_mouse).length
        pref = get_pref()
        threshold = pref.mouse_move_threshold_px if pref is not None else 5
        if threshold <= 0:
            return dist > 0.0
        return dist >= float(threshold)
