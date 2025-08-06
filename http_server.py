#!/usr/bin/env python3
"""
HTTP服务器 - 提供屏幕信息获取和点击操作接口
"""

from flask import Flask, jsonify, request, send_file, Response
import uiautomator2 as u2
from screen_utils import get_screen_info
import os
import time
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 输出中文字符而不是Unicode转义

# 全局设备连接
device = None

def get_device():
    """获取或创建设备连接"""
    global device
    if device is None:
        device = u2.connect()
    return device

def json_response(data, status_code=200):
    """创建JSON响应，确保中文字符正确显示"""
    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        status=status_code,
        mimetype='application/json; charset=utf-8'
    )

def add_click_points(screen_info):
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

@app.route('/get_screen_info', methods=['GET'])
def api_get_screen_info():
    """
    获取当前屏幕信息
    
    Returns:
        JSON: {
            "success": bool,
            "data": {
                "image_path": str,
                "parsed_image_path": str,
                "screen_info": dict
            },
            "error": str (如果失败)
        }
    """
    try:
        image_path, parsed_path, screen_info = get_screen_info()
        screen_info = add_click_points(screen_info)
        
        return json_response({
            "success": True,
            "data": {
                "image_path": image_path,
                "parsed_image_path": parsed_path,
                "screen_info": screen_info
            }
        })
    except Exception as e:
        return json_response({
            "success": False,
            "error": str(e)
        }, 500)

@app.route('/click', methods=['POST'])
def api_click():
    """
    点击指定坐标并返回点击后的屏幕信息
    
    Request Body:
        {
            "x": int,
            "y": int
        }
    
    Returns:
        JSON: {
            "success": bool,
            "data": {
                "clicked_position": {"x": int, "y": int},
                "before_click": {
                    "image_path": str,
                    "parsed_image_path": str,
                    "screen_info": dict
                },
                "after_click": {
                    "image_path": str,
                    "parsed_image_path": str,
                    "screen_info": dict
                },
                "clicked_element": dict (如果找到对应元素)
            },
            "error": str (如果失败)
        }
    """
    try:
        # 获取请求参数
        data = request.get_json()
        if not data or 'x' not in data or 'y' not in data:
            return json_response({
                "success": False,
                "error": "Missing required parameters: x, y"
            }, 400)
        
        x = int(data['x'])
        y = int(data['y'])
        
        # 获取点击前的屏幕信息
        before_image_path, before_parsed_path, before_screen_info = get_screen_info()
        before_screen_info = add_click_points(before_screen_info)
        
        # 查找点击位置对应的元素
        clicked_element = None
        screen_width = before_screen_info['device_info']['width']
        screen_height = before_screen_info['device_info']['height']
        
        # 将点击坐标转换为相对坐标
        rel_x = x / screen_width
        rel_y = y / screen_height
        
        # 查找包含该点的元素
        for element in before_screen_info['elements']:
            bbox = element.get('bbox', [])
            if len(bbox) == 4:
                x1, y1, x2, y2 = bbox
                if x1 <= rel_x <= x2 and y1 <= rel_y <= y2:
                    clicked_element = element
                    break
        
        # 执行点击操作
        d = get_device()
        d.click(x, y)
        
        # 等待页面响应
        time.sleep(1)
        
        # 获取点击后的屏幕信息
        after_image_path, after_parsed_path, after_screen_info = get_screen_info()
        after_screen_info = add_click_points(after_screen_info)
        
        # 构建响应
        response_data = {
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
                }
            }
        }
        
        if clicked_element:
            response_data["data"]["clicked_element"] = clicked_element
        
        return json_response(response_data)
        
    except Exception as e:
        return json_response({
            "success": False,
            "error": str(e)
        }, 500)

@app.route('/image/<path:filename>', methods=['GET'])
def serve_image(filename):
    """
    提供图片文件访问
    
    Args:
        filename: 图片文件名
    
    Returns:
        图片文件
    """
    try:
        # 从临时目录获取图片
        import tempfile
        file_path = os.path.join(tempfile.gettempdir(), filename)
        
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='image/png')
        else:
            return json_response({
                "success": False,
                "error": "Image not found"
            }), 404
    except Exception as e:
        return json_response({
            "success": False,
            "error": str(e)
        }, 500)

@app.route('/swipe', methods=['POST'])
def api_swipe():
    """
    执行滑动操作
    
    Request Body:
        {
            "direction": str ("up", "down", "left", "right") 或
            "start_x": int,
            "start_y": int,
            "end_x": int,
            "end_y": int,
            "duration": float (可选，默认0.5秒)
        }
    
    Returns:
        JSON: {
            "success": bool,
            "data": {
                "swipe_info": {"start": [x,y], "end": [x,y], "duration": float},
                "after_swipe": {
                    "image_path": str,
                    "parsed_image_path": str,
                    "screen_info": dict
                }
            },
            "error": str (如果失败)
        }
    """
    try:
        data = request.get_json()
        if not data:
            return json_response({
                "success": False,
                "error": "Missing request body"
            }, 400)
        
        d = get_device()
        duration = data.get('duration', 0.5)
        
        # 获取屏幕尺寸
        width = d.info["displayWidth"]
        height = d.info["displayHeight"]
        
        # 判断是方向滑动还是坐标滑动
        if 'direction' in data:
            direction = data['direction'].lower()
            # 计算滑动坐标
            if direction == "up":
                start_x, start_y = width // 2, height * 0.8
                end_x, end_y = width // 2, height * 0.2
            elif direction == "down":
                start_x, start_y = width // 2, height * 0.2
                end_x, end_y = width // 2, height * 0.8
            elif direction == "left":
                start_x, start_y = width * 0.8, height // 2
                end_x, end_y = width * 0.2, height // 2
            elif direction == "right":
                start_x, start_y = width * 0.2, height // 2
                end_x, end_y = width * 0.8, height // 2
            else:
                return json_response({
                    "success": False,
                    "error": "Invalid direction. Use: up, down, left, right"
                }, 400)
        else:
            # 使用提供的坐标
            required = ['start_x', 'start_y', 'end_x', 'end_y']
            if not all(key in data for key in required):
                return json_response({
                    "success": False,
                    "error": f"Missing required parameters: {required}"
                }, 400)
            
            start_x = int(data['start_x'])
            start_y = int(data['start_y'])
            end_x = int(data['end_x'])
            end_y = int(data['end_y'])
        
        # 执行滑动
        d.swipe(start_x, start_y, end_x, end_y, duration=duration)
        
        # 等待动画完成
        time.sleep(0.5)
        
        # 获取滑动后的屏幕信息
        after_image_path, after_parsed_path, after_screen_info = get_screen_info()
        after_screen_info = add_click_points(after_screen_info)
        
        return json_response({
            "success": True,
            "data": {
                "swipe_info": {
                    "start": [start_x, start_y],
                    "end": [end_x, end_y],
                    "duration": duration
                },
                "after_swipe": {
                    "image_path": after_image_path,
                    "parsed_image_path": after_parsed_path,
                    "screen_info": after_screen_info
                }
            }
        })
        
    except Exception as e:
        return json_response({
            "success": False,
            "error": str(e)
        }, 500)

@app.route('/input_text', methods=['POST'])
def api_input_text():
    """
    在当前焦点输入文本
    
    Request Body:
        {
            "text": str,
            "clear_first": bool (可选，是否先清空)
        }
    
    Returns:
        JSON: {
            "success": bool,
            "data": {
                "input_text": str,
                "after_input": {
                    "image_path": str,
                    "parsed_image_path": str,
                    "screen_info": dict
                }
            },
            "error": str (如果失败)
        }
    """
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return json_response({
                "success": False,
                "error": "Missing required parameter: text"
            }, 400)
        
        text = data['text']
        clear_first = data.get('clear_first', False)
        
        d = get_device()
        
        # 如果需要先清空
        if clear_first:
            d.clear_text()
            time.sleep(0.2)
        
        # 输入文本
        d.set_fastinput_ime(True)  # 启用快速输入
        d.send_keys(text)
        d.set_fastinput_ime(False)  # 关闭快速输入
        
        # 等待输入完成
        time.sleep(0.5)
        
        # 获取输入后的屏幕信息
        after_image_path, after_parsed_path, after_screen_info = get_screen_info()
        after_screen_info = add_click_points(after_screen_info)
        
        return json_response({
            "success": True,
            "data": {
                "input_text": text,
                "after_input": {
                    "image_path": after_image_path,
                    "parsed_image_path": after_parsed_path,
                    "screen_info": after_screen_info
                }
            }
        })
        
    except Exception as e:
        return json_response({
            "success": False,
            "error": str(e)
        }, 500)

@app.route('/back', methods=['POST'])
def api_back():
    """
    执行返回键操作
    
    Returns:
        JSON: {
            "success": bool,
            "data": {
                "action": "back",
                "after_action": {
                    "image_path": str,
                    "parsed_image_path": str,
                    "screen_info": dict
                }
            },
            "error": str (如果失败)
        }
    """
    try:
        d = get_device()
        
        # 执行返回操作
        d.press("back")
        
        # 等待动画完成
        time.sleep(0.5)
        
        # 获取操作后的屏幕信息
        after_image_path, after_parsed_path, after_screen_info = get_screen_info()
        after_screen_info = add_click_points(after_screen_info)
        
        return json_response({
            "success": True,
            "data": {
                "action": "back",
                "after_action": {
                    "image_path": after_image_path,
                    "parsed_image_path": after_parsed_path,
                    "screen_info": after_screen_info
                }
            }
        })
        
    except Exception as e:
        return json_response({
            "success": False,
            "error": str(e)
        }, 500)

@app.route('/home', methods=['POST'])
def api_home():
    """
    回到主屏幕
    
    Returns:
        JSON: {
            "success": bool,
            "data": {
                "action": "home",
                "after_action": {
                    "image_path": str,
                    "parsed_image_path": str,
                    "screen_info": dict
                }
            },
            "error": str (如果失败)
        }
    """
    try:
        d = get_device()
        
        # 执行home操作
        d.press("home")
        
        # 等待动画完成
        time.sleep(0.5)
        
        # 获取操作后的屏幕信息
        after_image_path, after_parsed_path, after_screen_info = get_screen_info()
        after_screen_info = add_click_points(after_screen_info)
        
        return json_response({
            "success": True,
            "data": {
                "action": "home",
                "after_action": {
                    "image_path": after_image_path,
                    "parsed_image_path": after_parsed_path,
                    "screen_info": after_screen_info
                }
            }
        })
        
    except Exception as e:
        return json_response({
            "success": False,
            "error": str(e)
        }, 500)

@app.route('/long_click', methods=['POST'])
def api_long_click():
    """
    长按指定坐标
    
    Request Body:
        {
            "x": int,
            "y": int,
            "duration": float (可选，默认1秒)
        }
    
    Returns:
        JSON: {
            "success": bool,
            "data": {
                "long_clicked_position": {"x": int, "y": int},
                "duration": float,
                "after_long_click": {
                    "image_path": str,
                    "parsed_image_path": str,
                    "screen_info": dict
                }
            },
            "error": str (如果失败)
        }
    """
    try:
        data = request.get_json()
        if not data or 'x' not in data or 'y' not in data:
            return json_response({
                "success": False,
                "error": "Missing required parameters: x, y"
            }, 400)
        
        x = int(data['x'])
        y = int(data['y'])
        duration = data.get('duration', 1.0)
        
        d = get_device()
        
        # 执行长按操作
        d.long_click(x, y, duration=duration)
        
        # 等待操作完成
        time.sleep(0.5)
        
        # 获取操作后的屏幕信息
        after_image_path, after_parsed_path, after_screen_info = get_screen_info()
        after_screen_info = add_click_points(after_screen_info)
        
        return json_response({
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
        })
        
    except Exception as e:
        return json_response({
            "success": False,
            "error": str(e)
        }, 500)

@app.route('/double_click', methods=['POST'])
def api_double_click():
    """
    双击指定坐标
    
    Request Body:
        {
            "x": int,
            "y": int
        }
    
    Returns:
        JSON: {
            "success": bool,
            "data": {
                "double_clicked_position": {"x": int, "y": int},
                "after_double_click": {
                    "image_path": str,
                    "parsed_image_path": str,
                    "screen_info": dict
                }
            },
            "error": str (如果失败)
        }
    """
    try:
        data = request.get_json()
        if not data or 'x' not in data or 'y' not in data:
            return json_response({
                "success": False,
                "error": "Missing required parameters: x, y"
            }, 400)
        
        x = int(data['x'])
        y = int(data['y'])
        
        d = get_device()
        
        # 执行双击操作
        d.double_click(x, y, duration=0.1)
        
        # 等待操作完成
        time.sleep(0.5)
        
        # 获取操作后的屏幕信息
        after_image_path, after_parsed_path, after_screen_info = get_screen_info()
        after_screen_info = add_click_points(after_screen_info)
        
        return json_response({
            "success": True,
            "data": {
                "double_clicked_position": {"x": x, "y": y},
                "after_double_click": {
                    "image_path": after_image_path,
                    "parsed_image_path": after_parsed_path,
                    "screen_info": after_screen_info
                }
            }
        })
        
    except Exception as e:
        return json_response({
            "success": False,
            "error": str(e)
        }, 500)

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        d = get_device()
        device_info = d.info
        return json_response({
            "success": True,
            "status": "healthy",
            "device_connected": True,
            "device_info": {
                "width": device_info.get("displayWidth"),
                "height": device_info.get("displayHeight"),
                "sdk": device_info.get("sdkInt")
            }
        })
    except Exception as e:
        return json_response({
            "success": False,
            "status": "unhealthy",
            "device_connected": False,
            "error": str(e)
        }), 503

if __name__ == '__main__':
    print("Starting HTTP Server...")
    print("Available endpoints:")
    print("  GET  /get_screen_info - 获取当前屏幕信息")
    print("  POST /click - 点击指定坐标并返回点击后的屏幕信息")
    print("  POST /swipe - 执行滑动操作（支持方向或坐标）")
    print("  POST /input_text - 在当前焦点输入文本")
    print("  POST /back - 返回键操作")
    print("  POST /home - 回到主屏幕")
    print("  POST /long_click - 长按指定坐标")
    print("  POST /double_click - 双击指定坐标")
    print("  GET  /image/<filename> - 获取截图文件")
    print("  GET  /health - 健康检查")
    print("\nServer running on http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)