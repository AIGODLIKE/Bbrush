v1.5.1 2026-10-19
Fix "Emulate 3 Button Mouse" (Alt+LMB) not working in Bbrush mode; physical middle mouse keeps Blender's default navigation
Restore ZBrush-style navigation switching (Alt to pan, release Alt to zoom, Ctrl to zoom) while rotating/panning/zooming; the default modal keymaps are restored when leaving Bbrush mode
Fix face set tools, mesh/cloth/color filters, transform and annotate tools being intercepted by Bbrush left mouse
Fix the brush shelf getting stuck in the wrong mode when a modifier key release is swallowed (e.g. by a popup)
Fix left/right mouse operators ending on unrelated key releases, and cancel properly on Esc / window switching
Fix distant geometry being treated as empty background in the depth map
Exiting Bbrush mode no longer saves user preferences unless they were actually changed and auto-save preferences is enabled
Silhouette (depth map) is now anti-aliased, and refreshes per viewport with throttled updates while navigating for better performance
Fix the diagonal white seam on the view navigation gizmo and smooth its jagged edges
Update minimum Blender version to 4.4, rename internal functions, optimize draw handler management and GPU cache, remove unused code

v1.5.1 2026-10-19
修复 Bbrush 模式下"模拟三键鼠标"(Alt+左键)无法使用的问题, 真实鼠标中键保持 Blender 默认导航
恢复旋转/平移/缩放视图过程中 ZBrush 式的切换(按 Alt 平移, 松开 Alt 缩放, Ctrl 缩放), 退出 Bbrush 模式时还原默认模态键位
修复面组工具、网格/布料/颜色滤镜、变换和标注工具被 Bbrush 左键拦截的问题
修复修饰键松开被弹窗等吞掉后笔刷架卡在错误模式的问题
修复左/右键操作被无关按键松开提前结束的问题, 按 Esc 或切换窗口时正确取消
修复深度图中远处模型被当作空背景的问题
退出 Bbrush 模式时不再无条件保存偏好设置, 仅在确实修改过且开启了自动保存偏好时保存
剪影(深度图)绘制抗锯齿, 按视图独立缓存, 导航时限频刷新以提升性能
修复视图导航 Gizmo 上从左下到右上的白色斜线, 并平滑其锯齿边缘
最低 Blender 版本更新为 4.4, 内部函数重命名, 优化绘制回调管理和 GPU 缓存, 移除无用代码
