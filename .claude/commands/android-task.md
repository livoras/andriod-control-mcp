---
allowed-tools: mcp__android-control__android_get_screen_info, mcp__android-control__android_click, mcp__android-control__android_swipe, mcp__android-control__android_input_text, mcp__android-control__android_back, mcp__android-control__android_home, mcp__android-control__android_launch_app, mcp__android-control__android_list_apps, Read
description: 执行 Android 自动化任务 - 通用的 Android 操作命令
---

# Android 自动化任务执行

## 任务目标
执行用户指定的 Android 操作任务：$ARGUMENTS

## 执行原则

1. **视觉识别优先**
   - 首先获取屏幕截图和元素信息
   - 通过 Read 工具查看标注后的图片
   - 根据元素索引获取精确坐标

2. **操作验证**
   - 每个操作后获取新的屏幕状态
   - 确认操作效果是否符合预期
   - 出现异常及时调整策略

3. **智能交互**
   - 根据任务需求选择合适的操作方式
   - 优先使用点击和输入，避免复杂手势
   - 必要时使用滑动浏览更多内容

4. **任务分解**
   - 将复杂任务分解为简单步骤
   - 逐步执行并验证每个步骤
   - 保持操作的连贯性

## 常用操作模式

- **应用启动**：search_app → launch_app
- **内容搜索**：点击搜索框 → 输入关键词 → 确认
- **列表浏览**：滑动 → 查看内容 → 选择项目
- **表单填写**：定位输入框 → 输入内容 → 下一项
- **功能导航**：识别按钮 → 点击 → 进入页面

## 执行流程

1. 分析用户需求
2. 获取当前屏幕状态
3. 规划操作步骤
4. 逐步执行操作
5. 验证执行结果
6. 反馈完成情况

## 注意事项
- 保持操作的稳定性，避免过快操作
- 重要操作前先确认当前状态
- 遇到弹窗或异常及时处理