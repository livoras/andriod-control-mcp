#!/bin/bash

# Build script for android-control-mcp package
# Usage: ./build.sh

set -e  # Exit on error

echo "🧹 Cleaning old build artifacts..."
rm -rf dist/ build/ src/android_control_mcp.egg-info/

echo "📦 Building package..."
python -m build

echo "✅ Build complete!"
echo ""
echo "📁 Distribution files created:"
ls -lah dist/

echo ""
echo "🚀 To install locally:"
echo "  pip install dist/android_control_mcp-*.whl"
echo ""
echo "📤 To upload to PyPI:"
echo "  python -m twine upload dist/*"
echo ""
echo "🔧 To test with uvx:"
echo "  uvx --from dist/android_control_mcp-*.whl android-control-mcp"