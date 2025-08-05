#!/usr/bin/env python3
"""
uiautomator2 测试脚本
测试基本功能：连接设备、获取设备信息、截图等
"""

import uiautomator2 as u2
import time
import os


def test_device_connection():
    """测试设备连接"""
    print("=" * 50)
    print("开始测试 uiautomator2 功能")
    print("=" * 50)
    
    try:
        # 连接设备（默认连接第一个设备）
        print("\n1. 尝试连接设备...")
        d = u2.connect()
        print("✓ 设备连接成功")
        
        # 获取设备信息
        print("\n2. 获取设备信息:")
        info = d.info
        print(f"   - 显示大小: {info.get('displayWidth')}x{info.get('displayHeight')}")
        print(f"   - 旋转角度: {info.get('displayRotation')}")
        print(f"   - SDK版本: {info.get('sdkInt')}")
        print(f"   - 产品名称: {info.get('productName')}")
        
        # 获取设备详细信息
        print("\n3. 获取设备详细信息:")
        device_info = d.device_info
        print(f"   - 品牌: {device_info.get('brand')}")
        print(f"   - 型号: {device_info.get('model')}")
        print(f"   - SDK: {device_info.get('sdk')}")
        
        # 测试截图功能
        print("\n4. 测试截图功能...")
        screenshot_path = "device_screenshot.png"
        d.screenshot(screenshot_path)
        if os.path.exists(screenshot_path):
            print(f"✓ 截图成功，保存在: {screenshot_path}")
        
        # 获取当前运行的应用
        print("\n5. 获取当前运行的应用:")
        current_app = d.app_current()
        print(f"   - 包名: {current_app.get('package')}")
        print(f"   - 活动: {current_app.get('activity')}")
        
        # 测试屏幕状态
        print("\n6. 屏幕状态:")
        screen_on = d.info.get('screenOn')
        print(f"   - 屏幕是否开启: {screen_on}")
        
        # 获取已安装应用列表（只显示前5个）
        print("\n7. 已安装应用（前5个）:")
        apps = d.app_list()[:5]
        for app in apps:
            print(f"   - {app}")
        
        print("\n✓ 所有测试完成!")
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        print("\n请确保:")
        print("1. Android 设备已通过 USB 连接")
        print("2. 已开启开发者选项和 USB 调试")
        print("3. 已安装 adb 工具")
        print("4. 运行 'adb devices' 可以看到设备")


if __name__ == "__main__":
    test_device_connection()