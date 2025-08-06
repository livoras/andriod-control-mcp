#!/usr/bin/env python3
"""Android Control MCP - Command line entry point"""

from .server import mcp

def main():
    """Main entry point for the MCP server"""
    mcp.run()

if __name__ == "__main__":
    main()