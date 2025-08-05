#!/usr/bin/env python3
"""
截取当前屏幕并分析页面元素
"""

import uiautomator2 as u2
from omniparser import OmniParser
import time
from datetime import datetime
import json


def analyze_current_screen():
    try:
        # 连接设备
        print("连接 Android 设备...")
        d = u2.connect()
        print("✓ 设备连接成功")
        
        # 获取设备信息
        info = d.info
        print(f"设备屏幕: {info['displayWidth']}x{info['displayHeight']}")
        
        # 生成截图文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"screenshot_{timestamp}.png"
        
        # 截取屏幕
        print(f"\n截取屏幕...")
        d.screenshot(screenshot_path)
        print(f"✓ 截图保存到: {screenshot_path}")
        
        # 使用 OmniParser 分析
        print("\n使用 OmniParser 分析页面元素...")
        parser = OmniParser()
        
        # 解析图片，同时获取标注图
        result = parser.parse(screenshot_path, return_labeled=True)
        
        # 显示分析结果
        print(f"\n分析结果:")
        print(f"- 检测到元素总数: {result['total']}")
        print(f"- 元素类型统计: {result['types']}")
        
        # 显示前10个元素的详细信息
        print(f"\n前10个检测到的元素:")
        for i, element in enumerate(result['elements'][:10], 1):
            print(f"\n{i}. 类型: {element.get('type', 'unknown')}")
            if 'text' in element:
                print(f"   文本: {element['text']}")
            if 'bbox' in element:
                bbox = element['bbox']
                print(f"   位置: ({bbox[0]}, {bbox[1]}) - ({bbox[2]}, {bbox[3]})")
            if 'confidence' in element:
                print(f"   置信度: {element['confidence']:.2f}")
        
        # 保存标注图片
        if result.get('labeled_image'):
            labeled_path = f"labeled_{timestamp}.png"
            parser.save_labeled_image(result, labeled_path)
            print(f"\n✓ 标注图片保存到: {labeled_path}")
        
        # 保存完整的分析结果到 JSON
        json_path = f"analysis_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✓ 完整分析结果保存到: {json_path}")
        
        # 查找可点击的元素
        clickable_elements = [e for e in result['elements'] if e.get('clickable', False)]
        if clickable_elements:
            print(f"\n找到 {len(clickable_elements)} 个可点击元素")
            for i, elem in enumerate(clickable_elements[:5], 1):
                print(f"{i}. {elem.get('text', '(无文本)')} - 位置: {elem.get('bbox', '未知')}")
        
        return result
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        return None


def find_element_by_text(elements, target_text):
    """根据文本查找元素"""
    for element in elements:
        if 'text' in element and target_text in element['text']:
            return element
    return None


if __name__ == "__main__":
    print("=" * 60)
    print("Android 屏幕元素分析工具")
    print("=" * 60)
    
    result = analyze_current_screen()
    
    if result:
        print("\n" + "=" * 60)
        print("分析完成！")
        print("\n提示：")
        print("- 查看标注图片了解元素位置")
        print("- 查看 JSON 文件获取完整元素信息")
        print("- 可以根据元素坐标进行自动化点击操作")