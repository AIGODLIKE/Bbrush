BRUSH_SHELF_MODE = {
    # list(itertools.product(a,a,a))
    # (ctrl,alt,shift):SHELF_MODE
    (True, True, True): "HIDE",
    (True, False, True): "HIDE",

    (True, True, False): "MASK",
    (True, False, False): "MASK",

    (False, True, True): "SMOOTH",
    (False, False, True): "SMOOTH",

    (False, True, False): "NORMAL",
    (False, False, False): "NORMAL",
}


class SwitchBrushShelf:
    BRUSH_SHELF_MODE = "NONE"  # NORMAL,SMOOTH,HIDE,MASK,ORIGINAL

    def update_brush_shelf(self, context, event):
        """更新笔刷资产架"""
        key = (event.ctrl, event.alt, event.shift)
        shelf = BRUSH_SHELF_MODE[key]
        if shelf != self.BRUSH_SHELF_MODE:
            self.BRUSH_SHELF_MODE = shelf
            self.set_brush_shelf(shelf)

    def set_brush_shelf(self, shelf_mode):
        ...

    def restore_brush_shelf(self, context):
        """恢复资产架"""
        self.set_brush_shelf("ORIGINAL")
