#!/usr/bin/env python3
"""
Android Control MCP Server
提供Android设备屏幕信息获取和控制功能的MCP工具
"""

import json
import time
import uiautomator2 as u2
from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from screen_utils import get_screen_info

# 创建MCP服务器
mcp = FastMCP("android-control")

# 全局设备连接
device = None

def get_device():
    """获取或创建设备连接"""
    global device
    if device is None:
        device = u2.connect()
    return device

def add_click_points(screen_info: Dict[str, Any]) -> Dict[str, Any]:
    """为可交互元素添加点击坐标"""
    width = screen_info['device_info']['width']
    height = screen_info['device_info']['height']
    
    for i, element in enumerate(screen_info.get('elements', [])):
        if element.get('interactivity', False) and element.get('bbox'):
            bbox = element['bbox']
            # 计算中心点坐标
            center_x = int((bbox[0] + bbox[2]) / 2 * width)
            center_y = int((bbox[1] + bbox[3]) / 2 * height)
            element['click_point'] = {
                'x': center_x,
                'y': center_y
            }
            # 添加元素索引便于引用
            element['index'] = i
    
    return screen_info

@mcp.tool()
def android_get_screen_info() -> Dict[str, Any]:
    """获取当前Android屏幕信息，包含截图、元素识别和点击坐标"""
    try:
        image_path, parsed_path, screen_info = get_screen_info()
        screen_info = add_click_points(screen_info)
        
        return {
            "success": True,
            "data": {
                "image_path": image_path,
                "parsed_image_path": parsed_path,
                "screen_info": screen_info
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def android_click(x: int, y: int) -> Dict[str, Any]:
    """点击Android屏幕指定坐标
    
    Args:
        x: X坐标
        y: Y坐标
    """
    try:
        # 获取点击前的屏幕信息
        before_image_path, before_parsed_path, before_screen_info = get_screen_info()
        before_screen_info = add_click_points(before_screen_info)
        
        # 查找点击位置对应的元素
        clicked_element = None
        screen_width = before_screen_info['device_info']['width']
        screen_height = before_screen_info['device_info']['height']
        
        # 转换为相对坐标
        rel_x = x / screen_width
        rel_y = y / screen_height
        
        for element in before_screen_info.get('elements', []):
            bbox = element.get('bbox', [])
            if len(bbox) == 4:
                if (bbox[0] <= rel_x <= bbox[2] and 
                    bbox[1] <= rel_y <= bbox[3]):
                    clicked_element = element
                    break
        
        # 执行点击
        d = get_device()
        d.click(x, y)
        
        # 等待UI更新
        time.sleep(1)
        
        # 获取点击后的屏幕信息
        after_image_path, after_parsed_path, after_screen_info = get_screen_info()
        after_screen_info = add_click_points(after_screen_info)
        
        return {
            "success": True,
            "data": {
                "clicked_position": {"x": x, "y": y},
                "before_click": {
                    "image_path": before_image_path,
                    "parsed_image_path": before_parsed_path,
                    "screen_info": before_screen_info
                },
                "after_click": {
                    "image_path": after_image_path,
                    "parsed_image_path": after_parsed_path,
                    "screen_info": after_screen_info
                },
                "clicked_element": clicked_element
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def android_swipe(
    direction: Optional[str] = None,
    start_x: Optional[int] = None,
    start_y: Optional[int] = None,
    end_x: Optional[int] = None,
    end_y: Optional[int] = None,
    duration: float = 0.5
) -> Dict[str, Any]:
    """在Android屏幕上滑动
    
    Args:
        direction: 滑动方向 (up/down/left/right)，与坐标二选一
        start_x: 起始X坐标
        start_y: 起始Y坐标
        end_x: 结束X坐标
        end_y: 结束Y坐标
        duration: 滑动持续时间(秒)
    """
    try:
        d = get_device()
        screen_width = d.info['displayWidth']
        screen_height = d.info['displayHeight']
        
        if direction:
            # 方向滑动
            if direction == 'up':
                d.swipe(screen_width // 2, screen_height * 0.7,
                       screen_width // 2, screen_height * 0.3, duration)
            elif direction == 'down':
                d.swipe(screen_width // 2, screen_height * 0.3,
                       screen_width // 2, screen_height * 0.7, duration)
            elif direction == 'left':
                d.swipe(screen_width * 0.7, screen_height // 2,
                       screen_width * 0.3, screen_height // 2, duration)
            elif direction == 'right':
                d.swipe(screen_width * 0.3, screen_height // 2,
                       screen_width * 0.7, screen_height // 2, duration)
            else:
                return {
                    "success": False,
                    "error": f"Invalid direction: {direction}"
                }
        elif all([start_x is not None, start_y is not None, 
                  end_x is not None, end_y is not None]):
            # 坐标滑动
            d.swipe(start_x, start_y, end_x, end_y, duration)
        else:
            return {
                "success": False,
                "error": "Either direction or all coordinates must be provided"
            }
        
        # 等待UI更新
        time.sleep(1)
        
        # 获取滑动后的屏幕信息
        after_image_path, after_parsed_path, after_screen_info = get_screen_info()
        after_screen_info = add_click_points(after_screen_info)
        
        return {
            "success": True,
            "data": {
                "after_swipe": {
                    "image_path": after_image_path,
                    "parsed_image_path": after_parsed_path,
                    "screen_info": after_screen_info
                }
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def android_input_text(text: str, clear_before: bool = False) -> Dict[str, Any]:
    """在当前焦点输入文本
    
    Args:
        text: 要输入的文本
        clear_before: 输入前是否清空
    """
    try:
        d = get_device()
        
        if clear_before:
            d.clear_text()
        
        # 使用快速输入法
        d.set_input_ime(True)
        d.send_keys(text)
        d.set_input_ime(False)
        
        # 等待输入完成
        time.sleep(0.5)
        
        # 获取输入后的屏幕信息
        after_image_path, after_parsed_path, after_screen_info = get_screen_info()
        after_screen_info = add_click_points(after_screen_info)
        
        return {
            "success": True,
            "data": {
                "input_text": text,
                "after_input": {
                    "image_path": after_image_path,
                    "parsed_image_path": after_parsed_path,
                    "screen_info": after_screen_info
                }
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def android_back() -> Dict[str, Any]:
    """Android返回键操作"""
    try:
        d = get_device()
        d.press("back")
        
        # 等待UI更新
        time.sleep(0.5)
        
        # 获取操作后的屏幕信息
        after_image_path, after_parsed_path, after_screen_info = get_screen_info()
        after_screen_info = add_click_points(after_screen_info)
        
        return {
            "success": True,
            "data": {
                "action": "back",
                "after_action": {
                    "image_path": after_image_path,
                    "parsed_image_path": after_parsed_path,
                    "screen_info": after_screen_info
                }
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def android_home() -> Dict[str, Any]:
    """回到Android主屏幕"""
    try:
        d = get_device()
        d.press("home")
        
        # 等待UI更新
        time.sleep(1)
        
        # 获取操作后的屏幕信息
        after_image_path, after_parsed_path, after_screen_info = get_screen_info()
        after_screen_info = add_click_points(after_screen_info)
        
        return {
            "success": True,
            "data": {
                "action": "home",
                "after_action": {
                    "image_path": after_image_path,
                    "parsed_image_path": after_parsed_path,
                    "screen_info": after_screen_info
                }
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def android_long_click(x: int, y: int, duration: float = 1.0) -> Dict[str, Any]:
    """长按Android屏幕指定坐标
    
    Args:
        x: X坐标
        y: Y坐标
        duration: 长按时间(秒)
    """
    try:
        d = get_device()
        d.long_click(x, y, duration)
        
        # 等待UI更新
        time.sleep(0.5)
        
        # 获取操作后的屏幕信息
        after_image_path, after_parsed_path, after_screen_info = get_screen_info()
        after_screen_info = add_click_points(after_screen_info)
        
        return {
            "success": True,
            "data": {
                "long_clicked_position": {"x": x, "y": y},
                "duration": duration,
                "after_long_click": {
                    "image_path": after_image_path,
                    "parsed_image_path": after_parsed_path,
                    "screen_info": after_screen_info
                }
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def android_double_click(x: int, y: int) -> Dict[str, Any]:
    """双击Android屏幕指定坐标
    
    Args:
        x: X坐标
        y: Y坐标
    """
    try:
        d = get_device()
        d.double_click(x, y)
        
        # 等待UI更新
        time.sleep(0.5)
        
        # 获取操作后的屏幕信息
        after_image_path, after_parsed_path, after_screen_info = get_screen_info()
        after_screen_info = add_click_points(after_screen_info)
        
        return {
            "success": True,
            "data": {
                "double_clicked_position": {"x": x, "y": y},
                "after_double_click": {
                    "image_path": after_image_path,
                    "parsed_image_path": after_parsed_path,
                    "screen_info": after_screen_info
                }
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# 主程序入口
if __name__ == "__main__":
    # 运行服务器
    mcp.run()