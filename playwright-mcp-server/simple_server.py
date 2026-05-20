# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import json
import os
import logging
import sys
import argparse
import asyncio
from anyio import BrokenResourceError
from mcp.server.fastmcp import FastMCP
from playwright_session import PlaywrightSessionManager
from tools.playwright_tool import register_playwright_tools
from tools.gen_code_tool import register_gen_code_tools
from tools.verify_tools import register_verify_tools
from tools.config_tool import register_config_tools
from utils.logger import log_tool_call, get_mcp_logger
from utils.config_manager import ConfigManager

logger = get_mcp_logger()

settings = {
    "log_level": "DEBUG"
}

# Create MCP server
mcp = FastMCP("playwright-mcp-server", log_level="INFO")

# Filter MCP low-level server INFO logs
def filter_mcp_lowlevel_logs():
    """Filter out MCP low-level server INFO level logs"""
    mcp_lowlevel_logger = logging.getLogger('mcp.server.lowlevel.server')
    mcp_lowlevel_logger.setLevel(logging.WARNING)

filter_mcp_lowlevel_logs()
session_manager = None  # Global access
config_manager = None  # Global config manager


def on_config_change(new_config):
    """Callback when configuration changes"""
    global session_manager
    if session_manager:
        logger.info("Configuration changed, updating session manager")
        session_manager.update_config(new_config)


async def main():
    global session_manager, config_manager
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", choices=["stdio", "sse"], default="sse")
    parser.add_argument("--config", type=str, help="Path to config file")
    args = parser.parse_args()

    # Initialize config manager with file watching
    config_manager = ConfigManager(args.config, on_config_change=on_config_change)
    BROWSER_CONFIG = config_manager.get_config()

    if not BROWSER_CONFIG:
        print("No browser configurations found. Please check your config file.")
        sys.exit(1)

    session_manager = PlaywrightSessionManager(browser_config=BROWSER_CONFIG)
    await session_manager.initialize()

    # Start watching for config file changes
    config_manager.start_watching()
    logger.info("Config file hot-reload enabled")

    # Register tools
    register_playwright_tools(mcp, session_manager)
    register_gen_code_tools(mcp, session_manager)
    register_verify_tools(mcp, session_manager)
    register_config_tools(mcp, config_manager)

    # Start MCP server
    try:
        if args.transport == "stdio":
            await mcp.run_stdio_async()
        else:
            await mcp.run_sse_async()
    except (BrokenResourceError, EOFError, ValueError) as e:
        logger.warning(f"[MCP] Cancel detected, exiting: {repr(e)}")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"[MCP] Unexpected error: {repr(e)}")
        sys.exit(1)
    finally:
        # Cleanup on shutdown
        if config_manager:
            config_manager.stop_watching()
        if session_manager:
            await session_manager.close_async()


if __name__ == "__main__":
    asyncio.run(main())
