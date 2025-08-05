#!/usr/bin/env python3
"""
截取当前屏幕并分析页面元素
"""

from screen_utils import get_screen_info
import json


def analyze_current_screen():
    image_path, parsed_image_path, screen_info = get_screen_info()
    screen_info_json = json.dumps(screen_info, ensure_ascii=False)
    return image_path, parsed_image_path, screen_info_json

if __name__ == "__main__":
    image_path, parsed_image_path, screen_info_json = analyze_current_screen()
    print(f"图片路径: {image_path}")
    print(f"标注图片: {parsed_image_path}")
    print(f"屏幕信息: {screen_info_json}")