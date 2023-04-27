这是一个模拟类似ZBrush雕刻方式的插件

# 快捷键

鼠标放在深度图上拖动可缩放

🐁:鼠标在模型上

```简化描述
. 表示单击操作
! 表示绘制操作
```

```
右键旋转视图
    旋转时按ctrl可缩放视图
alt 右键 平移视图
    平移时松开alt会切换成移动视图
alt 左键点模型 快速切换物体

shift 切换到平滑笔刷
ctrl 切换到mask笔刷类型
ctrl shift 切换到隐藏模型笔刷
```

### 绘制

```
鼠标在模型上：
    左 雕刻
    alt +左 反转雕刻
不在模型上:
    左键 旋转视图
    ctrl+左 框选遮罩
        alt反向
    shift+左 视图旋转 TODO
```

### 遮罩

Ctrl Press

```
ctrl +        生长遮罩
ctrl -        收缩遮罩
ctrl 向上箭头   提高遮罩对比度
ctrl 向下箭头   降低遮罩对比度

按下ctrl可以切换到隐藏笔刷
鼠标在模型上：
    左! 绘制遮罩
        +alt 反向
    左. 淡化遮罩
    左.+alt  锐化遮罩

不在模型上:
    左. 反转遮罩
    左! 清除遮罩
        alt 填充遮罩
```

[tip 多级细分后切换隐藏面将失效](https://projects.blender.org/blender/blender/issues/95419)

### 隐藏

Ctrl Shift Press

```
鼠标在模型上：
    左. 反转隐藏
    左! 绘制隐藏box
        +alt 绘制显示box
不在模型上:
    左. 显示所有
    左! 反转隐藏
```
