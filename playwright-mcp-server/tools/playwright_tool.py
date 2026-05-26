# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from typing import Optional, List
from playwright.async_api import Page
import json
import os
import logging
from utils.logger import log_tool_call, get_mcp_logger
from playwright_session import smart_wait
from utils.response_format import format_tool_response, init_tool_response, handle_page_source
from utils.gen_code import record_calls
from utils.retry import retry_async

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
    @retry_async(max_retries=2, base_delay=1.0)
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
            if not await session_manager.is_browser_alive():
                logger.info("Browser session is dead, reinitializing...")
                await session_manager.reinitialize()
            
            page = session_manager.page
            await page.goto(url, wait_until="networkidle")
            resp["status"] = "success"
            
            if session_manager.should_fetch_page_source():
                page_source = await page.content()
                handle_page_source(resp, page_source, page_source_file, summary_only)
        except Exception as e:
            resp["error"] = repr(e)
            logger.error(f"Error navigating to URL: {e}")

        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def upload_file(
        caller: str,
        locator_value: str,
        file_paths: List[str],
        locator_strategy: str = "css",
        step: str = "",
        scenario: str = "",
        step_raw: str = "",
    ) -> str:
        """Upload one or multiple files to a file input element

        Args:
            caller: caller name
            locator_value: element locator value for file input element
            file_paths: list of absolute file paths to upload
            locator_strategy: strategy of the locator (e.g., 'css', 'xpath', 'id', 'text', 'role')
            step: step name
            step_raw: raw original step text
            scenario: scenario name
        """
        resp = init_tool_response()
        try:
            page = session_manager.page
            locator = get_playwright_locator(locator_strategy, locator_value)
            
            element = page.locator(locator)
            await element.wait_for(state="attached", timeout=5000)
            
            validated_paths = []
            for file_path in file_paths:
                abs_path = os.path.abspath(file_path)
                if not os.path.exists(abs_path):
                    raise FileNotFoundError(f"File not found: {abs_path}")
                validated_paths.append(abs_path)
            
            await element.set_input_files(validated_paths)
            resp["status"] = "success"
            resp["data"]["uploaded_files"] = validated_paths
        except Exception as e:
            logger.error(f"Error uploading files: {e}")
            resp["status"] = "error"
            resp["error"] = f"Failed to upload files: {str(e)}"
            
        if resp.get("status") != "error":
            await smart_wait(page, expected_delay=1.0, max_wait=3.0)
            if session_manager.should_fetch_page_source():
                page_source = await page.content()
                handle_page_source(resp, page_source, page_source_file="", summary_only=False)

        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def wait_for_download(
        caller: str,
        download_dir: str = "",
        timeout: int = 30000,
        step: str = "",
        scenario: str = "",
        step_raw: str = "",
    ) -> str:
        """Wait for file download to complete and return downloaded file information

        Args:
            caller: caller name
            download_dir: directory to save downloaded files (default: system downloads folder)
            timeout: timeout in milliseconds (default: 30000)
            step: step name
            step_raw: raw original step text
            scenario: scenario name
        """
        resp = init_tool_response()
        try:
            page = session_manager.page
            
            if not download_dir:
                download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            
            os.makedirs(download_dir, exist_ok=True)
            
            async with page.expect_download(timeout=timeout) as download_info:
                pass
            
            download = await download_info.value
            downloaded_path = os.path.join(download_dir, download.suggested_filename)
            await download.save_as(downloaded_path)
            
            resp["status"] = "success"
            resp["data"]["downloaded_file"] = downloaded_path
            resp["data"]["file_name"] = download.suggested_filename
            resp["data"]["file_size"] = os.path.getsize(downloaded_path) if os.path.exists(downloaded_path) else 0
        except Exception as e:
            logger.error(f"Error waiting for download: {e}")
            resp["status"] = "error"
            resp["error"] = f"Failed to download file: {str(e)}"

        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def verify_download_exists(
        caller: str,
        file_name: str = "",
        download_dir: str = "",
        step: str = "",
        scenario: str = "",
        step_raw: str = "",
    ) -> str:
        """Verify that a file was downloaded successfully

        Args:
            caller: caller name
            file_name: expected file name (optional, checks if any file exists in download_dir)
            download_dir: directory where files are downloaded (default: system downloads folder)
            step: step name
            step_raw: raw original step text
            scenario: scenario name
        """
        resp = init_tool_response()
        try:
            if not download_dir:
                download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            
            if file_name:
                file_path = os.path.join(download_dir, file_name)
                if os.path.exists(file_path):
                    resp["status"] = "success"
                    resp["data"]["file_exists"] = True
                    resp["data"]["file_path"] = file_path
                    resp["data"]["file_size"] = os.path.getsize(file_path)
                else:
                    resp["status"] = "success"
                    resp["data"]["file_exists"] = False
            else:
                if os.path.exists(download_dir):
                    files = os.listdir(download_dir)
                    resp["status"] = "success"
                    resp["data"]["file_exists"] = len(files) > 0
                    resp["data"]["files"] = files[-5:] if files else []
                else:
                    resp["status"] = "success"
                    resp["data"]["file_exists"] = False
        except Exception as e:
            logger.error(f"Error verifying download: {e}")
            resp["status"] = "error"
            resp["error"] = str(e)

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
            await smart_wait(page, expected_delay=1.0, max_wait=3.0)
            if session_manager.should_fetch_page_source():
                page_source = await page.content()
                handle_page_source(resp, page_source, page_source_file, summary_only)

        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def hover_element(
        caller: str,
        locator_value: str,
        locator_strategy: str = "css",
        step: str = "",
        scenario: str = "",
        step_raw: str = "",
        page_source_file: str = "",
        summary_only: bool = False,
    ) -> str:
        """Hover mouse over an element to trigger hover effects or dropdown menus

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
            await element.hover()
            resp["status"] = "success"
        except Exception as e:
            logger.error(f"Error hovering over element: {e}")
            resp["status"] = "error"
            resp["error"] = f"Element {locator_value} not found or not hoverable: {str(e)}"

        if resp.get("status") == "success":
            await smart_wait(page, expected_delay=1.0)
            if session_manager.should_fetch_page_source():
                page_source = await page.content()
                handle_page_source(resp, page_source, page_source_file, summary_only)
            
        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def scroll_page(
        caller: str,
        direction: str = "down",
        amount: int = 300,
        step: str = "",
        scenario: str = "",
        step_raw: str = "",
        page_source_file: str = "",
        summary_only: bool = False,
    ) -> str:
        """Scroll the page up or down to view content outside the viewport

        Args:
            caller: caller name
            direction: scroll direction, 'up' or 'down' (default: 'down')
            amount: number of pixels to scroll (default: 300)
            step: step name
            step_raw: raw original step text
            scenario: scenario name
            page_source_file: optional, save page source to this file path instead of embedding inline
            summary_only: optional, if true return agent-friendly summary instead of full page source
        """
        resp = init_tool_response()
        try:
            page = session_manager.page
            scroll_amount = amount if direction == "down" else -amount
            await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            resp["status"] = "success"
            resp["data"]["direction"] = direction
            resp["data"]["amount"] = amount
        except Exception as e:
            logger.error(f"Error scrolling page: {e}")
            resp["status"] = "error"
            resp["error"] = str(e)

        if resp.get("status") == "success":
            await smart_wait(page, expected_delay=0.5)
            if session_manager.should_fetch_page_source():
                page_source = await page.content()
                handle_page_source(resp, page_source, page_source_file, summary_only)
            
        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def scroll_to_element(
        caller: str,
        locator_value: str,
        locator_strategy: str = "css",
        step: str = "",
        scenario: str = "",
        step_raw: str = "",
        page_source_file: str = "",
        summary_only: bool = False,
    ) -> str:
        """Scroll the page to make a specific element visible in the viewport

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
            await element.wait_for(state="attached", timeout=5000)
            await element.scroll_into_view_if_needed()
            resp["status"] = "success"
        except Exception as e:
            logger.error(f"Error scrolling to element: {e}")
            resp["status"] = "error"
            resp["error"] = f"Element {locator_value} not found: {str(e)}"

        if resp.get("status") == "success":
            await smart_wait(page, expected_delay=0.5)
            if session_manager.should_fetch_page_source():
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
            await smart_wait(page, expected_delay=1.0, max_wait=3.0)
            if session_manager.should_fetch_page_source():
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
            if session_manager.should_fetch_page_source():
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
            if session_manager.should_fetch_page_source():
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
            if session_manager.should_fetch_page_source():
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
            if session_manager.should_fetch_page_source():
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
            if session_manager.should_fetch_page_source():
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
            if session_manager.should_fetch_page_source():
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
            if session_manager.should_fetch_page_source():
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
            if session_manager.should_fetch_page_source():
                page_source = await page.content()
                handle_page_source(resp, page_source, page_source_file, summary_only)

        return json.dumps(format_tool_response(resp))
