#!/usr/bin/env python3
"""
点击屏幕上的时间区域
"""

import uiautomator2 as u2
import time

def click_time_area():
    try:
        # 连接设备
        print("连接设备...")
        d = u2.connect()
        
        # 获取屏幕信息
        info = d.info
        width = info['displayWidth']
        height = info['displayHeight']
        print(f"屏幕尺寸: {width}x{height}")
        
        # 时间显示在屏幕上方区域，根据截图分析
        # 时间"18:59"大约在屏幕上方中间位置
        # x坐标约为屏幕宽度的一半，y坐标约为屏幕高度的10%左右
        x = width // 2
        y = int(height * 0.12)  # 时间区域大约在顶部12%的位置
        
        print(f"\n准备点击坐标: ({x}, {y})")
        
        # 执行点击
        d.click(x, y)
        print("✓ 点击完成")
        
        # 等待一下看效果
        time.sleep(2)
        
        # 再截个图看看点击后的效果
        d.screenshot("after_click_time.png")
        print("✓ 已保存点击后的截图: after_click_time.png")
        
    except Exception as e:
        print(f"✗ 错误: {e}")

if __name__ == "__main__":
    click_time_area()