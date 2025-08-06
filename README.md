# Android Control MCP

AI-powered Android automation through MCP (Model Context Protocol). This server enables AI assistants like Claude to see and control Android devices by combining visual understanding with precise interaction capabilities.

## 🤖 Built for AI Assistants

This MCP server bridges AI models with Android devices, allowing natural language commands to be translated into precise device interactions. By leveraging **OmniParser** - a state-of-the-art screen understanding model - AI assistants can:

- **See** what's on the screen through intelligent element detection
- **Understand** UI layouts and interactive components  
- **Act** with precision using automatically calculated touch points
- **Verify** actions through visual feedback

## Core Technologies

### OmniParser - AI Vision
[OmniParser](https://github.com/microsoft/OmniParser) provides the visual understanding layer:
- 📊 **Element Detection**: Identifies all UI components (buttons, text, icons)
- 🎯 **Interaction Points**: Calculates precise click coordinates for each element
- 🏷️ **Content Recognition**: Extracts text and labels from UI elements
- 📐 **Layout Understanding**: Maps element relationships and screen structure

### UIAutomator2 - Device Control
[UIAutomator2](https://github.com/openatx/uiautomator2) provides the automation layer:
- 🎮 **Direct Control**: Native Android automation without root access
- ⚡ **Fast Execution**: High-performance device interaction
- 🔧 **Robust API**: Reliable touch, swipe, and input operations
- 📱 **Device Management**: App lifecycle and system control

## How It Works

1. **AI Request** → MCP Server receives command from AI assistant
2. **Screen Capture** → UIAutomator2 captures current Android screen
3. **Visual Analysis** → OmniParser analyzes UI elements and generates coordinates
4. **Action Execution** → UIAutomator2 performs the requested action
5. **Feedback** → Returns annotated screenshot and results to AI

## Features

- 📱 **AI Vision**: OmniParser-powered screen understanding
- 🎯 **Precise Control**: UIAutomator2-based reliable automation
- 🔄 **Full Coverage**: Complete Android control capabilities
- 🖼️ **Visual Feedback**: Annotated screenshots for AI verification
- 🚀 **Token Optimized**: Streamlined JSON format for efficient AI processing

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

### Available Tools for AI

#### Vision & Understanding
- `android_get_screen_info` - Capture screen and analyze UI elements with OmniParser
  - Returns interactive elements with click coordinates
  - Provides element types, content, and sizes
  - Optimized JSON format for minimal token usage

#### Precise Interaction
- `android_click(x, y)` - Click at AI-identified element coordinates
- `android_swipe(direction)` - Navigate with directional swipes
- `android_input_text(text, slowly)` - Type text with optional animation
- `android_long_click(x, y)` - Long press for context menus
- `android_double_click(x, y)` - Double tap interactions

#### Navigation
- `android_back()` - Navigate back
- `android_home()` - Return to home screen

#### App Management
- `android_launch_app(package_name)` - Direct app launch
- `android_search_app(keyword)` - Find apps by name (supports multiple languages)
- `android_list_apps(filter_type)` - List installed/running apps
- `android_app_info()` - Get current context information
- `android_force_stop_app(package_name)` - Force stop applications

## Requirements

- Python 3.8+
- Android device with USB debugging enabled
- Docker (for OmniParser API)
- uiautomator2 (auto-installed)

## Setup

### 1. Start OmniParser API Service (Required)

OmniParser is the AI vision system that enables understanding of Android screens:

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