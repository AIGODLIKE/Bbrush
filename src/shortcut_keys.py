SHORTCUT_KEYS = {
    'NORMAL': [
        {'doc': '视图操作'},
        {'tool': '平移视图', 'key': 'ALT+右键 or ALT+中键'},
        {'tool': '平移视图', 'key': 'ALT+左键 在空白区域拖拽'},
        {'tool': '平移视图', 'key': 'SHIFT+中键'},
        {'tool': '旋转视图', 'key': '右键'},
        {'tool': '旋转视图', 'key': '左键 在空白区域拖拽'},
        {'tool': '缩放视图', 'key': 'CTRL+中键 or CTRL+右键'},
        {'tool': '倾斜视图', 'key': 'SHIFT+左键 在空白区域拖拽'},

        {'doc': '雕刻'},
        {'tool': '雕刻', 'key': '左键 在模型上绘制'},
        {'tool': '反向雕刻', 'key': 'ALT+左键 在模型上绘制'},
        {'tool': '平滑', 'key': 'SHIFT+左键 在模型上绘制'},

        {'doc': '其它'},
        {'tool': '切换雕刻物体', 'key': 'ALT+左键 在其它模型上点击'},
    ],
    'MASK': [
        {'doc': '遮罩'},
        {'tool': '绘制遮罩', 'key': 'CTRL+左键 在模型上绘制'},
        {'tool': '擦除遮罩', 'key': 'CTRL+ALT+左键 在模型上绘制'},
        {'tool': '反转遮罩', 'key': 'CTRL+左键 在空白区域单击'},
        {'tool': '框选遮罩', 'key': 'CTRL+左键 从空白区域拖拽至模型上'},
        {'tool': '框选擦除遮罩', 'key': 'CTRL+ALT+左键 从空白区域拖拽至模型上'},
        {'tool': '淡化遮罩', 'key': 'CTRL+左键 在模型上单击'},
        {'tool': '清除遮罩', 'key': 'CTRL+左键 在空白区域绘制框'},
        {'tool': '锐化遮罩', 'key': 'CTRL+ALT+左键 在模型上单击'},
        {'tool': '填充遮罩', 'key': 'CTRL+ALT+左键 在空白区域绘制框'},

        {'doc': '其它'},
        {'tool': '生长遮罩', 'key': 'CTRL+小键盘+号 单击'},
        {'tool': '收缩遮罩', 'key': 'CTRL+小键盘-号 单击'},
        {'tool': '提高遮罩对比度', 'key': 'CTRL+上箭头 or CTRL+小键盘* 单击'},
        {'tool': '降低遮罩对比度', 'key': 'CTRL+下箭头 or CTRL+小键盘/ 单击'}
    ],
    'HIDE': [
        {'doc': '隐藏'},
        {'tool': '隐藏绘制框外', 'key': 'CTRL+SHIFT+左键 在模型上绘制'},
        {'tool': '隐藏绘制框内', 'key': 'CTRL+SHIFT+ALT+左键 在模型上绘制'},
        {'tool': '取消隐藏',
         'key': 'CTRL+SHIFT+左键 在空白区域点击(如果添加了多级细分修改器将会失效,这是Bl自身问题 tip:3.6以上已修复)'},
        {'tool': '反转隐藏',
         'key': 'CTRL+SHIFT+左键 or CTRL+SHIFT+ALT+左键 在空白区域绘制'},
    ],
}
