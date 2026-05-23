# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional, Dict, Any
import logging
from utils.logger import get_mcp_logger

logger = get_mcp_logger()


async def smart_wait(page: Page, expected_delay: float = 1.0, max_wait: float = 5.0):
    """Intelligently wait for page stabilization after interaction.
    
    Replaces hard-coded time.sleep() with smart waiting that:
    1. Waits for network to be idle
    2. Waits for DOM to stabilize (no mutations for expected_delay ms)
    3. Caps at max_wait to avoid infinite waiting
    
    Args:
        page: Playwright page instance
        expected_delay: Expected page stabilization time in seconds
        max_wait: Maximum wait time in seconds
    """
    try:
        wait_method = getattr(page, 'wait_for_load_state', None)
        if wait_method and callable(wait_method):
            await wait_method("domcontentloaded", timeout=max_wait * 1000)
    except Exception:
        pass
    
    try:
        eval_method = getattr(page, 'evaluate', None)
        if eval_method and callable(eval_method):
            try:
                await eval_method(f"""
                    () => new Promise(resolve => {{
                        const observer = new MutationObserver(() => {{
                            clearTimeout(timeout);
                            timeout = setTimeout(() => {{
                                observer.disconnect();
                                resolve();
                            }}, {int(expected_delay * 1000)});
                        }});
                        observer.observe(document.body, {{ childList: true, subtree: true }});
                        const timeout = setTimeout(() => {{
                            observer.disconnect();
                            resolve();
                        }}, {int(max_wait * 1000)});
                    }})
                """)
            except TypeError:
                pass
    except Exception:
        pass


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
        extra_http_headers = browser_config.get("extra_http_headers", None)
        
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
        
        # Create browser context with optional extra HTTP headers
        context_options = {"viewport": viewport}
        if extra_http_headers:
            context_options["extra_http_headers"] = extra_http_headers
            logger.info(f"Custom HTTP headers configured: {list(extra_http_headers.keys())}")
        
        self._context = await self._browser.new_context(**context_options)
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
        """Close browser and cleanup (sync wrapper that schedules async cleanup)."""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.close_async())
            else:
                loop.run_until_complete(self.close_async())
            logger.info("Browser session closed (sync wrapper)")
        except Exception as e:
            logger.error(f"Error closing browser session: {e}")
    
    def clear_gen_code_cache(self):
        """Clear code generation cache"""
        self.gen_code_cache = []
        self.gen_code_id = None
        self.proposed_changes = []
        self.new_steps_count = 0
        self.header_code = None
    
    def should_fetch_page_source(self) -> bool:
        """Determine if page_source should be fetched (only during code generation)."""
        return self.gen_code_id is not None
