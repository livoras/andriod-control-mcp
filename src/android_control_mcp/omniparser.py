"""
OmniParser SDK - 简单的 Python 客户端
"""

import requests
import json
from typing import Dict, Optional, Union
from pathlib import Path
import base64


class OmniParser:
    """OmniParser API 客户端"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        """
        初始化客户端
        
        Args:
            api_url: API 服务地址
        """
        self.api_url = api_url.rstrip('/')
        self._check_health()
    
    def _check_health(self):
        """检查服务是否可用"""
        try:
            resp = requests.get(f"{self.api_url}/", timeout=5)
            if resp.status_code != 200:
                print(f"Warning: API service may not be running properly")
        except:
            print(f"Warning: Cannot connect to API at {self.api_url}")
    
    def parse(self, 
              image: Union[str, bytes, Path], 
              return_labeled: bool = False) -> Dict:
        """
        解析图片中的 UI 元素
        
        Args:
            image: 图片路径或二进制数据
            return_labeled: 是否返回标注图片
            
        Returns:
            {
                "elements": [...],  # UI 元素列表
                "total": 96,        # 元素总数
                "types": {"text": 25, "icon": 71},  # 元素类型统计
                "labeled_image": "base64..."  # 标注图片 (可选)
            }
        """
        # 准备文件
        if isinstance(image, (str, Path)):
            with open(image, 'rb') as f:
                files = {'file': (Path(image).name, f, 'image/png')}
                return self._make_request(files, return_labeled)
        else:
            files = {'file': ('image.png', image, 'image/png')}
            return self._make_request(files, return_labeled)
    
    def _make_request(self, files: Dict, return_labeled: bool) -> Dict:
        """发送请求"""
        params = {'return_labeled_image': 'true'} if return_labeled else {}
        
        try:
            resp = requests.post(
                f"{self.api_url}/parse",
                files=files,
                params=params,
                timeout=30
            )
            
            if resp.status_code == 200:
                result = resp.json()
                # 简化返回格式
                return {
                    "elements": result.get("elements", []),
                    "total": result.get("total_elements", 0),
                    "types": result.get("element_types", {}),
                    "labeled_image": result.get("labeled_image", None)
                }
            else:
                raise Exception(f"API error: {resp.status_code} - {resp.text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
    
    def save_labeled_image(self, result: Dict, output_path: str):
        """保存标注图片"""
        if result.get("labeled_image"):
            image_data = base64.b64decode(result["labeled_image"])
            with open(output_path, 'wb') as f:
                f.write(image_data)
            print(f"Labeled image saved to: {output_path}")
        else:
            print("No labeled image in result")


# 便捷函数
def parse_image(image_path: str, api_url: str = "http://localhost:8000") -> Dict:
    """快速解析图片"""
    parser = OmniParser(api_url)
    return parser.parse(image_path)