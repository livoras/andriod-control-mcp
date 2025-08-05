#!/usr/bin/env python3
"""
HTTP服务器 - 提供屏幕信息获取和点击操作接口
"""

from flask import Flask, jsonify, request, send_file
import uiautomator2 as u2
from screen_utils import get_screen_info
import os
import time

app = Flask(__name__)

# 全局设备连接
device = None

def get_device():
    """获取或创建设备连接"""
    global device
    if device is None:
        device = u2.connect()
    return device

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
        
        return jsonify({
            "success": True,
            "data": {
                "image_path": image_path,
                "parsed_image_path": parsed_path,
                "screen_info": screen_info
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

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
            return jsonify({
                "success": False,
                "error": "Missing required parameters: x, y"
            }), 400
        
        x = int(data['x'])
        y = int(data['y'])
        
        # 获取点击前的屏幕信息
        before_image_path, before_parsed_path, before_screen_info = get_screen_info()
        
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
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

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
            return jsonify({
                "success": False,
                "error": "Image not found"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        d = get_device()
        device_info = d.info
        return jsonify({
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
        return jsonify({
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
    print("  GET  /image/<filename> - 获取截图文件")
    print("  GET  /health - 健康检查")
    print("\nServer running on http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)