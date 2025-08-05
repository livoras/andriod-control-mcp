#!/usr/bin/env python3
"""
控制屏幕开关
"""

import uiautomator2 as u2

def screen_control():
    try:
        # 连接设备
        print("连接设备...")
        d = u2.connect()
        
        # 检查屏幕状态
        screen_on = d.info.get('screenOn')
        print(f"当前屏幕状态: {'开启' if screen_on else '关闭'}")
        
        if not screen_on:
            # 点亮屏幕
            print("\n正在点亮屏幕...")
            d.screen_on()
            print("✓ 屏幕已点亮")
        else:
            print("\n屏幕已经是开启状态")
        
        # 再次确认状态
        screen_on_after = d.info.get('screenOn')
        print(f"\n操作后屏幕状态: {'开启' if screen_on_after else '关闭'}")
        
    except Exception as e:
        print(f"✗ 错误: {e}")

if __name__ == "__main__":
    screen_control()