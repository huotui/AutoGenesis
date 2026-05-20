# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional, Dict, Any
import logging
from utils.logger import get_mcp_logger

logger = get_mcp_logger()


class PlaywrightSessionManager:
    """Manages Playwright browser sessions"""
    
    def __init__(self, browser_config: dict):
        self._config = browser_config
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        
        # Code generation cache
        self.gen_code_cache = []
        self.gen_code_id = None
        self.steps_dir = None
        self.step_file_target = None
        self.proposed_changes = []
        self.new_steps_count = 0
        self.header_code = None
        
        # Tool execution guard
        self.is_executing = False
    
    def start_tool_execution(self, tool_name):
        if self.is_executing:
            logger.warning(f"Tool {tool_name} blocked: another tool is executing")
            return False
        self.is_executing = True
        logger.info(f"Tool {tool_name} started execution")
        return True

    def finish_tool_execution(self, tool_name):
        self.is_executing = False
        logger.info(f"Tool {tool_name} finished execution")
    
    async def initialize(self):
        """Initialize Playwright and launch browser (async)"""
        browser_config = self._config.get("browser", {})
        browser_name = browser_config.get("browser_name", "chromium")
        headless = browser_config.get("headless", False)
        viewport = browser_config.get("viewport", {"width": 1280, "height": 720})
        
        self._playwright = await async_playwright().start()
        
        # Launch browser based on type
        if browser_name == "chromium":
            self._browser = await self._playwright.chromium.launch(headless=headless)
        elif browser_name == "firefox":
            self._browser = await self._playwright.firefox.launch(headless=headless)
        elif browser_name == "webkit":
            self._browser = await self._playwright.webkit.launch(headless=headless)
        else:
            raise ValueError(f"Unsupported browser: {browser_name}")
        
        # Create browser context
        self._context = await self._browser.new_context(viewport=viewport)
        self._context.set_default_timeout(browser_config.get("timeout", 30000))
        
        # Create new page
        self._page = await self._context.new_page()
        
        logger.info(f"Browser launched: {browser_name} (headless={headless})")
    
    @property
    def page(self) -> Page:
        """Get current page instance"""
        if self._page is None:
            raise RuntimeError("Browser page not initialized")
        return self._page
    
    @property
    def browser(self) -> Browser:
        """Get browser instance"""
        return self._browser
    
    @property
    def context(self) -> BrowserContext:
        """Get browser context"""
        return self._context
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update configuration (requires restart for browser changes)"""
        logger.info("Configuration updated")
        self._config = new_config
    
    async def close_async(self):
        """Close browser and cleanup (async)"""
        try:
            if self._page:
                await self._page.close()
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
            logger.info("Browser session closed")
        except Exception as e:
            logger.error(f"Error closing browser session: {e}")
    
    def close(self):
        """Close browser and cleanup (sync wrapper for cleanup)"""
        try:
            if self._page:
                # In async mode, we can't call sync methods
                pass
            if self._playwright:
                pass
            logger.info("Browser session closed (async cleanup pending)")
        except Exception as e:
            logger.error(f"Error closing browser session: {e}")
    
    def clear_gen_code_cache(self):
        """Clear code generation cache"""
        self.gen_code_cache = []
        self.gen_code_id = None
        self.proposed_changes = []
        self.new_steps_count = 0
        self.header_code = None
