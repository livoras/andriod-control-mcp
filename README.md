# Android Control MCP

MCP (Model Context Protocol) server for Android device control with AI-powered screen analysis.

## Features

- 📱 **Screen Analysis**: Capture and analyze Android screen with element detection
- 🎯 **Smart Clicking**: Auto-calculate click points for interactive elements
- 🔄 **Full Control**: Support click, swipe, input text, navigation operations
- 🖼️ **Visual Feedback**: Return screenshots and analysis for all operations
- 🤖 **AI Integration**: Works with OmniParser for intelligent UI understanding

## Installation

```bash
# Run directly from GitHub (recommended)
uvx --from git+https://github.com/livoras/andriod-control-mcp.git android-control-mcp

# Or install from GitHub
pip install git+https://github.com/livoras/andriod-control-mcp.git
```

## Usage

### As MCP Server

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "android-control": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/livoras/andriod-control-mcp.git",
        "android-control-mcp"
      ]
    }
  }
}
```

Or if installed locally:

```json
{
  "mcpServers": {
    "android-control": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "android_control_mcp"]
    }
  }
}
```

### Available Tools

- `android_get_screen_info` - Get current screen information with element detection
- `android_click(x, y)` - Click at specified coordinates
- `android_swipe(direction)` - Swipe in direction (up/down/left/right)
- `android_input_text(text)` - Input text at current focus
- `android_back()` - Press back button
- `android_home()` - Go to home screen
- `android_long_click(x, y)` - Long press at coordinates
- `android_double_click(x, y)` - Double click at coordinates

## Requirements

- Python 3.8+
- Android device with USB debugging enabled
- Docker (for OmniParser API)
- uiautomator2 (auto-installed)

## Setup

### 1. Start OmniParser API Service (Required)

The OmniParser API is required for UI element detection:

```bash
# Pull and run the OmniParser API container
docker pull khhhshhh/omniparser-api:with-models
docker run -d -p 8000:8000 --name omniparser khhhshhh/omniparser-api:with-models

# Verify it's running
curl http://localhost:8000/health
```

### 2. Setup Android Device

1. Enable USB debugging on your Android device
2. Connect device via USB
3. Verify connection: `adb devices`

### 3. Run the MCP Server

```bash
# Run directly with uvx
uvx --from git+https://github.com/livoras/andriod-control-mcp.git android-control-mcp
```

## Development

```bash
# Clone the repository
git clone https://github.com/livoras/andriod-control-mcp.git
cd andriod-control-mcp

# Install in development mode
pip install -e .

# Run directly
python -m android_control_mcp
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Issues

If you encounter any problems, please [file an issue](https://github.com/livoras/andriod-control-mcp/issues) on GitHub.