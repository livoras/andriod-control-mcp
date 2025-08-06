#!/usr/bin/env python3
"""
屏幕信息获取工具
"""

import uiautomator2 as u2
import os
import tempfile
from datetime import datetime
from typing import Tuple, Dict


def get_screen_info() -> Tuple[str, str, Dict]:
    """
    获取当前屏幕信息，自动处理锁屏情况
    
    Returns:
        tuple: (原始截图路径, 标注图片路径, 屏幕信息字典)
    """
    # 连接设备
    d = u2.connect()
    
    # 检查屏幕状态
    screen_on = d.info.get("screenOn", False)
    is_locked = False
    
    # 如果屏幕关闭，先点亮屏幕
    if not screen_on:
        d.screen_on()
        # 等待屏幕完全点亮
        import time
        time.sleep(0.5)
    
    # 检查是否在锁屏界面
    current_app = d.app_current()
    is_locked = False
    
    print(f"当前应用包名: {current_app['package']}")
    
    # 方法1: 通过屏幕元素内容判断（更可靠）
    # 检查是否有特定的锁屏文本
    screen_texts = []
    try:
        # 获取屏幕上的所有文本
        for elem in d(className="android.widget.TextView"):
            text = elem.info.get("text", "")
            if text:
                screen_texts.append(text)
        
        print(f"屏幕文本: {screen_texts[:5]}")  # 只打印前5个
        
        # 锁屏特征文本
        lock_keywords = ["仅限紧急呼叫", "滑动解锁", "向上滑动解锁", "Emergency calls only"]
        for text in screen_texts:
            if any(keyword in text for keyword in lock_keywords):
                is_locked = True
                print(f"检测到锁屏关键词: {text}")
                break
    except:
        pass
    
    # 方法2: 检查系统UI包
    if not is_locked and current_app["package"] in ["com.android.systemui", "com.miui.aod", "com.android.keyguard"]:
        is_locked = True
        print("检测到系统UI包，判定为锁屏")
    
    # 如果检测到锁屏，自动尝试解锁
    if is_locked:
        print("检测到锁屏状态，正在尝试解锁...")
        unlock_screen(d)
        # 重新检查是否还在锁屏
        current_app = d.app_current()
        # 再次检查锁屏文本
        still_locked = False
        try:
            for elem in d(className="android.widget.TextView"):
                text = elem.info.get("text", "")
                if any(keyword in text for keyword in ["仅限紧急呼叫", "滑动解锁", "Emergency calls only"]):
                    still_locked = True
                    break
        except:
            pass
        
        if not still_locked:
            is_locked = False
            print("✓ 解锁成功")
        else:
            print("✗ 仍在锁屏界面")
    
    # 创建临时文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = tempfile.gettempdir()
    
    # 生成文件路径
    image_path = os.path.join(temp_dir, f"screen_{timestamp}.png")
    parsed_image_path = os.path.join(temp_dir, f"screen_labeled_{timestamp}.png")
    
    # 截取屏幕
    d.screenshot(image_path)
    
    # 使用 OmniParser 解析
    from .omniparser import OmniParser
    parser = OmniParser()
    result = parser.parse(image_path, return_labeled=True)
    
    # 保存标注图片
    if result.get("labeled_image"):
        parser.save_labeled_image(result, parsed_image_path)
    
    # 构建屏幕信息
    screen_info = {
        "device_info": {
            "width": d.info["displayWidth"],
            "height": d.info["displayHeight"],
            "rotation": d.info.get("displayRotation", 0),
            "screen_on": screen_on,
            "screen_was_off": not screen_on,
            "is_locked": is_locked
        },
        "current_app": current_app,
        "elements": result["elements"],
        "total_elements": result["total"],
        "element_types": result["types"],
        "timestamp": timestamp
    }
    
    return image_path, parsed_image_path, screen_info


def find_elements_by_text(screen_info: Dict, text: str) -> list:
    """
    根据文本查找元素
    
    Args:
        screen_info: get_screen_info() 返回的屏幕信息
        text: 要查找的文本（支持部分匹配）
    
    Returns:
        list: 匹配的元素列表
    """
    matches = []
    for element in screen_info["elements"]:
        content = element.get("content", "")
        element_text = element.get("text", "")
        
        # 检查 content 字段
        if content and isinstance(content, str) and text in content:
            matches.append(element)
        # 检查 text 字段
        elif element_text and isinstance(element_text, str) and text in element_text:
            matches.append(element)
    return matches


def get_clickable_elements(screen_info: Dict) -> list:
    """
    获取所有可点击的元素
    
    Args:
        screen_info: get_screen_info() 返回的屏幕信息
    
    Returns:
        list: 可点击元素列表
    """
    return [e for e in screen_info["elements"] 
            if e.get("interactivity", False) or e.get("clickable", False)]


def unlock_screen(d: u2.Device, password: str = None) -> bool:
    """
    解锁屏幕 - 简单向上滑动
    
    Args:
        d: uiautomator2 设备对象
        password: 解锁密码（如果需要）
    
    Returns:
        bool: 是否成功解锁
    """
    width = d.info["displayWidth"]
    height = d.info["displayHeight"]
    
    # 向上滑动解锁
    print("正在向上滑动解锁...")
    d.swipe(width // 2, height * 0.9, width // 2, height * 0.1, duration=0.5)
    
    # 等待动画完成
    import time
    time.sleep(1)
    
    # 返回True，让后续代码检查是否真的解锁了
    return True


def convert_bbox_to_coordinates(bbox: list, screen_width: int, screen_height: int) -> Tuple[int, int]:
    """
    将相对坐标转换为绝对坐标（取中心点）
    
    Args:
        bbox: [x1, y1, x2, y2] 相对坐标
        screen_width: 屏幕宽度
        screen_height: 屏幕高度
    
    Returns:
        tuple: (x, y) 中心点的绝对坐标
    """
    x1, y1, x2, y2 = bbox
    center_x = int((x1 + x2) / 2 * screen_width)
    center_y = int((y1 + y2) / 2 * screen_height)
    return center_x, center_y


if __name__ == "__main__":
    # 测试函数
    print("获取屏幕信息...")
    image_path, parsed_path, info = get_screen_info()
    
    print(f"\n文件保存位置:")
    print(f"- 原始截图: {image_path}")
    print(f"- 标注图片: {parsed_path}")
    
    print(f"\n屏幕信息:")
    print(f"- 设备分辨率: {info['device_info']['width']}x{info['device_info']['height']}")
    print(f"- 屏幕状态: {'锁屏' if info['device_info']['is_locked'] else '已解锁'}")
    print(f"- 屏幕之前是否关闭: {'是' if info['device_info']['screen_was_off'] else '否'}")
    print(f"- 检测到元素: {info['total_elements']} 个")
    print(f"- 元素类型: {info['element_types']}")
    print(f"- 当前应用: {info['current_app']['package']}")
    
    # 查找文本
    text_elements = find_elements_by_text(info, "19:")
    if text_elements:
        print(f"\n找到包含 '19:' 的元素: {len(text_elements)} 个")