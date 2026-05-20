# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from typing import Optional
from playwright.async_api import Page
import json
import time
import logging
from utils.logger import log_tool_call, get_mcp_logger
from utils.response_format import format_tool_response, init_tool_response, handle_page_source
from utils.gen_code import record_calls

logger = get_mcp_logger()


def get_playwright_locator(locator_strategy_str: str, locator_value: str):
    """Convert locator strategy to Playwright locator"""
    strategy_mapping = {
        "css": locator_value,
        "css_selector": locator_value,
        "xpath": f"xpath={locator_value}",
        "id": f"[id='{locator_value}']",
        "text": f"text={locator_value}",
        "role": f"role={locator_value}",
        "test_id": f"[data-testid='{locator_value}']",
        "label": f"label={locator_value}",
        "placeholder": f"input[placeholder='{locator_value}']",
    }
    
    locator_strategy_str = locator_strategy_str.strip().lower() if locator_strategy_str else "css"
    return strategy_mapping.get(locator_strategy_str, locator_value)


def register_playwright_tools(mcp, session_manager):
    """Register Playwright browser automation tools to MCP server."""

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def browser_navigate(
        caller: str,
        url: str,
        step: str = "",
        scenario: str = "",
        page_source_file: str = "",
        summary_only: bool = False
    ) -> str:
        """Navigate to a URL

        Args:
            caller: The caller identifier
            url: URL to navigate to
            step: Step description for logging
            scenario: Scenario description for logging
            page_source_file: optional, save page source to this file path instead of embedding inline
            summary_only: optional, if true return agent-friendly summary instead of full page source
        """
        resp = init_tool_response()
        try:
            page = session_manager.page
            await page.goto(url, wait_until="networkidle")
            resp["status"] = "success"
            
            page_source = await page.content()
            handle_page_source(resp, page_source, page_source_file, summary_only)
        except Exception as e:
            resp["error"] = repr(e)
            logger.error(f"Error navigating to URL: {e}")

        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def browser_close(caller: str, step: str = "", scenario: str = "") -> str:
        """Close browser"""
        resp = init_tool_response()
        try:
            await session_manager.close_async()
            resp["status"] = "success"
        except Exception as e:
            resp["error"] = repr(e)
            logger.error(f"Error closing browser: {e}")

        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def find_element(
        caller: str,
        locator_value: str,
        locator_strategy: str = "css",
        step: str = "",
        scenario: str = "",
        step_raw: str = "",
        page_source_file: str = "",
        summary_only: bool = False,
    ) -> str:
        """Find element on page, if element exists, return success, otherwise return error

        Args:
            locator_value: required, element locator value (e.g., element selector, id, etc.)
            locator_strategy: strategy of the locator (e.g., 'css', 'xpath', 'id', 'text', 'role')
            step: required, step name
            step_raw: required, raw original step text
            scenario: required, scenario name
            page_source_file: optional, save page source to this file path instead of embedding inline
            summary_only: optional, if true return agent-friendly summary instead of full page source
        """
        resp = init_tool_response()
        try:
            page = session_manager.page
            locator = get_playwright_locator(locator_strategy, locator_value)
            
            element = page.locator(locator)
            await element.wait_for(state="visible", timeout=5000)
            
            if await element.count() > 0:
                resp["status"] = "success"
            else:
                resp["status"] = "error"
                resp["error"] = f"Element {locator_value} not found"
        except Exception as e:
            resp["status"] = "error"
            resp["error"] = f"Element {locator_value} not found: {str(e)}"
            
        if resp.get("status") != "error":
            page_source = await page.content()
            handle_page_source(resp, page_source, page_source_file, summary_only)

        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def click_element(
        caller: str,
        locator_value: str,
        locator_strategy: str = "css",
        step: str = "",
        scenario: str = "",
        step_raw: str = "",
        page_source_file: str = "",
        summary_only: bool = False,
    ) -> str:
        """Click element

        Args:
            locator_value: element locator value
            locator_strategy: strategy of the locator (e.g., 'css', 'xpath', 'id', 'text', 'role')
            step: step name
            step_raw: raw original step text
            scenario: scenario name
            page_source_file: optional, save page source to this file path instead of embedding inline
            summary_only: optional, if true return agent-friendly summary instead of full page source
        """
        resp = init_tool_response()
        try:
            page = session_manager.page
            locator = get_playwright_locator(locator_strategy, locator_value)
            
            element = page.locator(locator)
            await element.wait_for(state="visible", timeout=5000)
            await element.click()
            resp["status"] = "success"
        except Exception as e:
            logger.error(f"Error clicking element: {e}")
            resp["status"] = "error"
            resp["error"] = f"Element {locator_value} not found or not clickable: {str(e)}"

        if resp.get("status") == "success":
            time.sleep(2)
            page_source = await page.content()
            handle_page_source(resp, page_source, page_source_file, summary_only)
            
        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def send_keys(
        caller: str,
        locator_value: str,
        locator_strategy: str = "css",
        text: str = "",
        step: str = "",
        scenario: str = "",
        step_raw: str = "",
        page_source_file: str = "",
        summary_only: bool = False,
    ) -> str:
        """Enter text in element

        Args:
            caller: caller name
            locator_value: element locator value
            locator_strategy: strategy of the locator (e.g., 'css', 'xpath', 'id', 'text', 'role')
            text: text to send
            step: step name
            step_raw: raw original step text
            scenario: scenario name
            page_source_file: optional, save page source to this file path instead of embedding inline
            summary_only: optional, if true return agent-friendly summary instead of full page source
        """
        resp = init_tool_response()
        try:
            page = session_manager.page
            locator = get_playwright_locator(locator_strategy, locator_value)
            
            element = page.locator(locator)
            # Wait for element to be attached to DOM
            await element.wait_for(state="attached", timeout=5000)
            # Try fill directly - Playwright will auto-wait for element to be editable
            await element.fill(text)
            resp["status"] = "success"
        except Exception as e:
            logger.error(f"Error entering text in element: {e}")
            resp["status"] = "error"
            resp["error"] = f"Element {locator_value} not found or not editable: {str(e)}"
            
        if resp.get("status") != "error":
            page_source = await page.content()
            handle_page_source(resp, page_source, page_source_file, summary_only)

        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def get_text(
        caller: str,
        locator_value: str,
        locator_strategy: str = "css",
        step: str = "",
        scenario: str = "",
        step_raw: str = "",
        page_source_file: str = "",
        summary_only: bool = False,
    ) -> str:
        """Get text content from element

        Args:
            caller: caller name
            locator_value: element locator value
            locator_strategy: strategy of the locator (e.g., 'css', 'xpath', 'id', 'text', 'role')
            step: step name
            step_raw: raw original step text
            scenario: scenario name
            page_source_file: optional, save page source to this file path instead of embedding inline
            summary_only: optional, if true return agent-friendly summary instead of full page source
        """
        resp = init_tool_response()
        try:
            page = session_manager.page
            locator = get_playwright_locator(locator_strategy, locator_value)
            
            element = page.locator(locator)
            await element.wait_for(state="visible", timeout=5000)
            text_content = await element.inner_text()
            
            resp["status"] = "success"
            resp["data"]["text"] = text_content
        except Exception as e:
            logger.error(f"Error getting text from element: {e}")
            resp["status"] = "error"
            resp["error"] = f"Element {locator_value} not found: {str(e)}"
            
        if resp.get("status") != "error":
            page_source = await page.content()
            handle_page_source(resp, page_source, page_source_file, summary_only)

        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def get_page_title(
        caller: str,
        step: str = "",
        scenario: str = "",
        step_raw: str = "",
        page_source_file: str = "",
        summary_only: bool = False,
    ) -> str:
        """Get current page title

        Args:
            caller: caller name
            step: step name
            step_raw: raw original step text
            scenario: scenario name
            page_source_file: optional, save page source to this file path instead of embedding inline
            summary_only: optional, if true return agent-friendly summary instead of full page source
        """
        resp = init_tool_response()
        try:
            page = session_manager.page
            title = await page.title()
            
            resp["status"] = "success"
            resp["data"]["title"] = title
        except Exception as e:
            logger.error(f"Error getting page title: {e}")
            resp["status"] = "error"
            resp["error"] = str(e)
            
        if resp.get("status") != "error":
            page_source = await page.content()
            handle_page_source(resp, page_source, page_source_file, summary_only)

        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def get_page_url(
        caller: str,
        step: str = "",
        scenario: str = "",
        step_raw: str = "",
        page_source_file: str = "",
        summary_only: bool = False,
    ) -> str:
        """Get current page URL

        Args:
            caller: caller name
            step: step name
            step_raw: raw original step text
            scenario: scenario name
            page_source_file: optional, save page source to this file path instead of embedding inline
            summary_only: optional, if true return agent-friendly summary instead of full page source
        """
        resp = init_tool_response()
        try:
            page = session_manager.page
            url = page.url
            
            resp["status"] = "success"
            resp["data"]["url"] = url
        except Exception as e:
            logger.error(f"Error getting page URL: {e}")
            resp["status"] = "error"
            resp["error"] = str(e)
            
        if resp.get("status") != "error":
            page_source = await page.content()
            handle_page_source(resp, page_source, page_source_file, summary_only)

        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def wait_for_element(
        caller: str,
        locator_value: str,
        locator_strategy: str = "css",
        timeout: int = 5000,
        step: str = "",
        scenario: str = "",
        step_raw: str = "",
        page_source_file: str = "",
        summary_only: bool = False,
    ) -> str:
        """Wait for element to appear on page

        Args:
            caller: caller name
            locator_value: element locator value
            locator_strategy: strategy of the locator (e.g., 'css', 'xpath', 'id', 'text', 'role')
            timeout: timeout in milliseconds (default: 5000)
            step: step name
            step_raw: raw original step text
            scenario: scenario name
            page_source_file: optional, save page source to this file path instead of embedding inline
            summary_only: optional, if true return agent-friendly summary instead of full page source
        """
        resp = init_tool_response()
        try:
            page = session_manager.page
            locator = get_playwright_locator(locator_strategy, locator_value)
            
            element = page.locator(locator)
            await element.wait_for(state="visible", timeout=timeout)
            
            resp["status"] = "success"
        except Exception as e:
            logger.error(f"Error waiting for element: {e}")
            resp["status"] = "error"
            resp["error"] = f"Element {locator_value} not found within timeout: {str(e)}"
            
        if resp.get("status") != "error":
            page_source = await page.content()
            handle_page_source(resp, page_source, page_source_file, summary_only)

        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def select_option(
        caller: str,
        locator_value: str,
        option_value: str,
        locator_strategy: str = "css",
        step: str = "",
        scenario: str = "",
        step_raw: str = "",
        page_source_file: str = "",
        summary_only: bool = False,
    ) -> str:
        """Select option from dropdown

        Args:
            caller: caller name
            locator_value: select element locator value
            option_value: option value to select
            locator_strategy: strategy of the locator (e.g., 'css', 'xpath', 'id', 'text', 'role')
            step: step name
            step_raw: raw original step text
            scenario: scenario name
            page_source_file: optional, save page source to this file path instead of embedding inline
            summary_only: optional, if true return agent-friendly summary instead of full page source
        """
        resp = init_tool_response()
        try:
            page = session_manager.page
            locator = get_playwright_locator(locator_strategy, locator_value)
            
            element = page.locator(locator)
            await element.wait_for(state="visible", timeout=5000)
            await element.select_option(option_value)
            
            resp["status"] = "success"
        except Exception as e:
            logger.error(f"Error selecting option: {e}")
            resp["status"] = "error"
            resp["error"] = f"Failed to select option: {str(e)}"
            
        if resp.get("status") != "error":
            page_source = await page.content()
            handle_page_source(resp, page_source, page_source_file, summary_only)

        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def press_key(
        caller: str,
        key: str,
        step: str = "",
        scenario: str = "",
        step_raw: str = "",
        page_source_file: str = "",
        summary_only: bool = False,
    ) -> str:
        """Press a keyboard key

        Args:
            caller: caller name
            key: key to press (e.g., 'Enter', 'Tab', 'Escape', 'ArrowDown')
            step: step name
            step_raw: raw original step text
            scenario: scenario name
            page_source_file: optional, save page source to this file path instead of embedding inline
            summary_only: optional, if true return agent-friendly summary instead of full page source
        """
        resp = init_tool_response()
        try:
            page = session_manager.page
            await page.keyboard.press(key)
            
            resp["status"] = "success"
        except Exception as e:
            logger.error(f"Error pressing key: {e}")
            resp["status"] = "error"
            resp["error"] = str(e)
            
        if resp.get("status") != "error":
            page_source = await page.content()
            handle_page_source(resp, page_source, page_source_file, summary_only)

        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def screenshot(
        caller: str,
        file_path: str,
        step: str = "",
        scenario: str = "",
        step_raw: str = "",
    ) -> str:
        """Take a screenshot of the current page

        Args:
            caller: caller name
            file_path: path to save the screenshot
            step: step name
            step_raw: raw original step text
            scenario: scenario name
        """
        resp = init_tool_response()
        try:
            page = session_manager.page
            await page.screenshot(path=file_path, full_page=True)
            
            resp["status"] = "success"
            resp["data"]["screenshot_path"] = file_path
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            resp["status"] = "error"
            resp["error"] = str(e)

        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def execute_javascript(
        caller: str,
        script: str,
        step: str = "",
        scenario: str = "",
        step_raw: str = "",
        page_source_file: str = "",
        summary_only: bool = False,
    ) -> str:
        """Execute JavaScript code on the page

        Args:
            caller: caller name
            script: JavaScript code to execute
            step: step name
            step_raw: raw original step text
            scenario: scenario name
            page_source_file: optional, save page source to this file path instead of embedding inline
            summary_only: optional, if true return agent-friendly summary instead of full page source
        """
        resp = init_tool_response()
        try:
            page = session_manager.page
            result = await page.evaluate(script)
            
            resp["status"] = "success"
            resp["data"]["result"] = str(result)
        except Exception as e:
            logger.error(f"Error executing JavaScript: {e}")
            resp["status"] = "error"
            resp["error"] = str(e)
            
        if resp.get("status") != "error":
            page_source = await page.content()
            handle_page_source(resp, page_source, page_source_file, summary_only)

        return json.dumps(format_tool_response(resp))
