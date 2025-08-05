#!/usr/bin/env python3
"""
启动 scrcpy 投屏
"""

import subprocess
import time

def start_scrcpy():
    print("启动 scrcpy 投屏...")
    print("-" * 50)
    print("控制说明：")
    print("- 鼠标点击 = 触摸")
    print("- 鼠标拖动 = 滑动")
    print("- 鼠标滚轮 = 上下滑动")
    print("- Cmd+C = 复制")
    print("- Cmd+V = 粘贴")
    print("- Cmd+F = 全屏")
    print("- Cmd+G = 调整窗口大小")
    print("-" * 50)
    
    try:
        # 启动 scrcpy，限制分辨率以提高性能
        subprocess.run(['scrcpy', '-m', '1024', '--window-title', 'Android Screen'])
    except KeyboardInterrupt:
        print("\n投屏已停止")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    start_scrcpy()