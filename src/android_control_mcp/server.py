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
from .screen_utils import get_screen_info

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
    """为元素添加索引（新格式已包含click_point）"""
    # 新格式已经在 screen_utils.py 中处理了 click_point 和 size
    # 这里只需要添加索引
    for i, element in enumerate(screen_info.get('elements', [])):
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
                # "image_path": image_path,
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
        
        # 新格式使用 click_point 和 size 判断
        for element in before_screen_info.get('elements', []):
            click_point = element.get('click_point', [])
            size = element.get('size', [])
            if len(click_point) == 2 and len(size) == 2:
                cx, cy = click_point
                w, h = size
                # 判断点击位置是否在元素范围内
                # 使用整数运算避免浮点数问题
                half_w = w // 2
                half_h = h // 2
                if (cx - half_w <= x <= cx + half_w and 
                    cy - half_h <= y <= cy + half_h):
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
                    # "image_path": before_image_path,
                    "parsed_image_path": before_parsed_path,
                    "screen_info": before_screen_info
                },
                "after_click": {
                    # "image_path": after_image_path,
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
                start_y_calc = int(screen_height * 0.7)
                end_y_calc = int(screen_height * 0.3)
                d.swipe(screen_width // 2, start_y_calc,
                       screen_width // 2, end_y_calc, duration)
            elif direction == 'down':
                start_y_calc = int(screen_height * 0.3)
                end_y_calc = int(screen_height * 0.7)
                d.swipe(screen_width // 2, start_y_calc,
                       screen_width // 2, end_y_calc, duration)
            elif direction == 'left':
                start_x_calc = int(screen_width * 0.7)
                end_x_calc = int(screen_width * 0.3)
                d.swipe(start_x_calc, screen_height // 2,
                       end_x_calc, screen_height // 2, duration)
            elif direction == 'right':
                start_x_calc = int(screen_width * 0.3)
                end_x_calc = int(screen_width * 0.7)
                d.swipe(start_x_calc, screen_height // 2,
                       end_x_calc, screen_height // 2, duration)
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
                    # "image_path": after_image_path,
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
def android_input_text(text: str, clear_before: bool = False, slowly: bool = False) -> Dict[str, Any]:
    """在当前焦点输入文本
    
    Args:
        text: 要输入的文本
        clear_before: 输入前是否清空
        slowly: 是否逐字输入（有打字动画效果）
    """
    try:
        d = get_device()
        
        if clear_before:
            d.clear_text()
        
        d.set_input_ime(True)
        
        if slowly:
            # 逐字输入，有打字动画效果
            for char in text:
                d.send_keys(char)
                time.sleep(0.03)  # 每个字符间隔0.03秒
        else:
            # 快速输入
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
                "input_mode": "slowly" if slowly else "fast",
                "after_input": {
                    # "image_path": after_image_path,
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
                    # "image_path": after_image_path,
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
                    # "image_path": after_image_path,
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
                    # "image_path": after_image_path,
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
                    # "image_path": after_image_path,
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
def android_launch_app(package_name: str) -> Dict[str, Any]:
    """直接通过包名启动Android应用
    
    Args:
        package_name: 应用包名 (如 com.tencent.wework)
    """
    try:
        d = get_device()
        d.app_start(package_name)
        
        # 等待应用启动
        time.sleep(2)
        
        # 获取启动后的屏幕信息
        after_image_path, after_parsed_path, after_screen_info = get_screen_info()
        after_screen_info = add_click_points(after_screen_info)
        
        # 获取当前应用信息
        current_app = d.app_current()
        
        return {
            "success": True,
            "data": {
                "launched_app": package_name,
                "current_app": current_app,
                "after_launch": {
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
def android_list_apps(filter_type: str = "all") -> Dict[str, Any]:
    """列出设备上的应用
    
    Args:
        filter_type: 过滤类型 (all/running/user)
    """
    try:
        d = get_device()
        
        if filter_type == "all":
            apps = d.app_list()
        elif filter_type == "running":
            apps = d.app_list_running()
        elif filter_type == "user":
            # 过滤出用户应用（排除系统应用）
            all_apps = d.app_list()
            apps = [app for app in all_apps if not app.startswith("com.android.") 
                   and not app.startswith("com.google.android.")]
        else:
            return {
                "success": False,
                "error": f"Invalid filter_type: {filter_type}"
            }
        
        return {
            "success": True,
            "data": {
                "filter_type": filter_type,
                "total_count": len(apps),
                "apps": apps
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def android_search_app(keyword: str) -> Dict[str, Any]:
    """按名称搜索应用
    
    Args:
        keyword: 搜索关键词
    """
    try:
        d = get_device()
        all_apps = d.app_list()
        
        # 搜索包含关键词的应用（不区分大小写）
        keyword_lower = keyword.lower()
        matched_apps = []
        
        for app in all_apps:
            # 检查包名是否包含关键词
            if keyword_lower in app.lower():
                matched_apps.append(app)
            # 特殊匹配规则
            elif keyword == "企业微信" and "wework" in app.lower():
                matched_apps.append(app)
            elif keyword == "微信" and app == "com.tencent.mm":
                matched_apps.append(app)
            elif keyword == "支付宝" and "alipay" in app.lower():
                matched_apps.append(app)
            elif keyword == "淘宝" and "taobao" in app.lower():
                matched_apps.append(app)
            elif keyword == "美团" and "meituan" in app.lower():
                matched_apps.append(app)
            elif keyword == "饿了么" and "eleme" in app.lower():
                matched_apps.append(app)
        
        return {
            "success": True,
            "data": {
                "keyword": keyword,
                "matched_count": len(matched_apps),
                "matched_apps": matched_apps
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def android_app_info() -> Dict[str, Any]:
    """获取当前运行应用信息"""
    try:
        d = get_device()
        current_app = d.app_current()
        
        # 获取更多设备信息
        device_info = d.info
        
        return {
            "success": True,
            "data": {
                "current_app": current_app,
                "device_info": {
                    "brand": device_info.get("brand"),
                    "model": device_info.get("model"),
                    "sdk": device_info.get("sdk"),
                    "android_version": device_info.get("version"),
                    "display_size": f"{device_info.get('displayWidth')}x{device_info.get('displayHeight')}"
                }
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def android_force_stop_app(package_name: str) -> Dict[str, Any]:
    """强制停止应用
    
    Args:
        package_name: 应用包名
    """
    try:
        d = get_device()
        d.app_stop(package_name)
        
        # 等待应用停止
        time.sleep(1)
        
        # 获取停止后的屏幕信息
        after_image_path, after_parsed_path, after_screen_info = get_screen_info()
        after_screen_info = add_click_points(after_screen_info)
        
        # 获取当前应用信息（确认是否已停止）
        current_app = d.app_current()
        
        return {
            "success": True,
            "data": {
                "stopped_app": package_name,
                "current_app": current_app,
                "after_stop": {
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