## 🚀 Initial Release v0.1.0

### Features
- 🤖 Complete MCP server implementation for Android device control
- 📱 8 Android control tools via MCP protocol:
  - `android_get_screen_info` - Get screen information with UI element detection
  - `android_click` - Click at specific coordinates
  - `android_swipe` - Swipe gestures
  - `android_input_text` - Text input
  - `android_back` - Back button
  - `android_home` - Home button
  - `android_long_click` - Long press
  - `android_double_click` - Double tap
- 🎯 OmniParser integration for UI element detection (bundled)
- 🔓 Automatic lock screen detection and unlock
- 📦 PyPI-ready package structure

### Installation

#### From GitHub Release
```bash
pip install https://github.com/livoras/andriod-control-mcp/releases/download/v0.1.0/android_control_mcp-0.1.0-py3-none-any.whl
```

#### From source
```bash
git clone https://github.com/livoras/andriod-control-mcp.git
cd andriod-control-mcp
pip install -e .
```

### Usage

Run as MCP server:
```bash
android-control-mcp
```

Or integrate in Python:
```python
from android_control_mcp import mcp
```

### Requirements
- Python 3.8+
- Android device with USB debugging enabled
- ADB installed and configured

### Note
OmniParser is bundled with the package for UI element detection functionality.