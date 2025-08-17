---
allowed-tools: Task, mcp__android-control__android_get_screen_info, mcp__android-control__android_click, mcp__android-control__android_swipe, mcp__android-control__android_input_text, mcp__android-control__android_launch_app, Read
description: 自动化点外卖流程 - 搜索美食、选择商家、下单
---

# 自动化点外卖任务

## 重要说明
**可以使用 Task 工具进行任务管理，但不要调用子 agent（如 general-purpose 等）。直接使用 MCP 工具完成具体操作。**

## 任务描述
帮助用户在美团外卖APP上自动完成点餐流程

## 参数说明
用户输入格式：`/order-food <用户需求>`
示例：
- `/order-food 麻辣烫` - 直接搜索麻辣烫
- `/order-food 想吃点水果` - 理解需求后搜索水果相关商家
- `/order-food 来点清淡的` - 搜索粥、汤、沙拉等清淡食物

## 执行步骤

1. **启动应用**
   - 直接使用 android_launch_app 启动美团外卖APP
   - **固定包名**：com.sankuai.meituan.takeoutnew

2. **搜索美食**
   - 获取当前屏幕状态
   - 点击搜索框
   - **重要**：如果搜索框右边有 X 号，先点击 X 号清空搜索框
   - 根据用户需求输入合适的搜索词（如："$ARGUMENTS"可能是"想吃点水果"，则搜索"水果"、"水果捞"等）
   - 确认搜索

3. **选择商家**
   - 分析搜索结果
   - 选择评分高、销量好的商家
   - 进入商家页面

4. **选择菜品**
   - 浏览菜单
   - 选择合适的菜品
   - 检查是否满足起送金额
   - 如需要，添加其他商品凑单

5. **确认订单**
   - 进入购物车
   - 点击去结算
   - 确认配送信息
   - 提交订单

6. **反馈结果**
   - 显示订单详情
   - 告知用户总金额
   - 等待用户确认支付

## 注意事项
- **重要**：必须使用美团外卖APP（com.sankuai.meituan.takeoutnew），而不是美团APP（com.sankuai.meituan）
- 需要理解用户的真实需求，将口语化表述转换为合适的搜索关键词
- 每步操作后需要读取屏幕状态确认结果
- 遇到问题时及时反馈给用户
- 保持操作的可追溯性