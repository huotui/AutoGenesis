# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import pytest
import json
import os
import asyncio
import tempfile
from unittest.mock import MagicMock, patch, AsyncMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.playwright_tool import get_playwright_locator, register_playwright_tools


class TestGetPlaywrightLocator:
    """Tests for get_playwright_locator function"""

    def test_css_selector(self):
        result = get_playwright_locator("css", ".my-class")
        assert result == ".my-class"

    def test_css_selector_alias(self):
        result = get_playwright_locator("css_selector", ".my-class")
        assert result == ".my-class"

    def test_xpath_selector(self):
        result = get_playwright_locator("xpath", "//div[@class='test']")
        assert result == "xpath=//div[@class='test']"

    def test_id_selector(self):
        result = get_playwright_locator("id", "my-id")
        assert result == "[id='my-id']"

    def test_text_selector(self):
        result = get_playwright_locator("text", "Click Me")
        assert result == "text=Click Me"

    def test_role_selector(self):
        result = get_playwright_locator("role", "button")
        assert result == "role=button"

    def test_test_id_selector(self):
        result = get_playwright_locator("test_id", "login-btn")
        assert result == "[data-testid='login-btn']"

    def test_label_selector(self):
        result = get_playwright_locator("label", "Username")
        assert result == "label=Username"

    def test_placeholder_selector(self):
        result = get_playwright_locator("placeholder", "Enter email")
        assert result == "input[placeholder='Enter email']"

    def test_default_css(self):
        result = get_playwright_locator(None, ".default")
        assert result == ".default"

    def test_empty_strategy_defaults_to_css(self):
        result = get_playwright_locator("", ".default")
        assert result == ".default"

    def test_unknown_strategy_returns_raw_value(self):
        result = get_playwright_locator("unknown", ".raw-selector")
        assert result == ".raw-selector"

    def test_whitespace_stripped(self):
        result = get_playwright_locator("  CSS  ", ".my-class")
        assert result == ".my-class"

    def test_case_insensitive(self):
        result = get_playwright_locator("CSS", ".my-class")
        assert result == ".my-class"

    def test_xpath_case_insensitive(self):
        result = get_playwright_locator("XPATH", "//div")
        assert result == "xpath=//div"


class TestPlaywrightTools:
    """Tests for Playwright MCP tools"""

    @pytest.fixture
    def mock_session_manager(self):
        manager = MagicMock()
        mock_page = MagicMock()
        manager.page = mock_page
        manager.gen_code_cache = []
        manager.gen_code_id = None
        manager.close = MagicMock()
        return manager

    @pytest.fixture
    def mock_mcp(self):
        mcp = MagicMock()
        registered_tools = {}

        def mock_tool_decorator():
            def decorator(func):
                registered_tools[func.__name__] = func
                return func
            return decorator

        mcp.tool = mock_tool_decorator
        mcp._registered_tools = registered_tools
        return mcp

    @pytest.fixture
    def tools(self, mock_mcp, mock_session_manager):
        register_playwright_tools(mock_mcp, mock_session_manager)
        return mock_mcp._registered_tools

    @pytest.mark.asyncio
    async def test_browser_navigate_success(self, tools, mock_session_manager):
        mock_session_manager.page.content.return_value = "<html><body>Test</body></html>"
        result = await tools['browser_navigate'](
            caller="test",
            url="https://example.com"
        )
        response = json.loads(result)
        assert response["status"] == "success"
        mock_session_manager.page.goto.assert_called_once_with(
            "https://example.com", wait_until="networkidle"
        )

    @pytest.mark.asyncio
    async def test_browser_navigate_error(self, tools, mock_session_manager):
        mock_session_manager.page.goto.side_effect = Exception("Navigation failed")
        result = await tools['browser_navigate'](
            caller="test",
            url="https://invalid-url.com"
        )
        response = json.loads(result)
        assert response["status"] == "error"
        assert "Navigation failed" in response["error"]

    @pytest.mark.asyncio
    async def test_browser_close_success(self, tools, mock_session_manager):
        result = await tools['browser_close'](caller="test")
        response = json.loads(result)
        assert response["status"] == "success"
        mock_session_manager.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_browser_close_error(self, tools, mock_session_manager):
        mock_session_manager.close.side_effect = Exception("Close failed")
        result = await tools['browser_close'](caller="test")
        response = json.loads(result)
        assert response["status"] == "error"

    @pytest.mark.asyncio
    async def test_find_element_success(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.count.return_value = 1
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content.return_value = "<html></html>"
        
        result = await tools['find_element'](
            caller="test",
            locator_value=".my-class",
            locator_strategy="css"
        )
        response = json.loads(result)
        assert response["status"] == "success"

    @pytest.mark.asyncio
    async def test_find_element_not_found(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for.side_effect = Exception("Element not visible")
        mock_session_manager.page.locator.return_value = mock_element
        
        result = await tools['find_element'](
            caller="test",
            locator_value=".nonexistent",
            locator_strategy="css"
        )
        response = json.loads(result)
        assert response["status"] == "error"

    @pytest.mark.asyncio
    async def test_click_element_success(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content.return_value = "<html></html>"
        
        result = await tools['click_element'](
            caller="test",
            locator_value="#btn",
            locator_strategy="css"
        )
        response = json.loads(result)
        assert response["status"] == "success"
        mock_element.click.assert_called_once()

    @pytest.mark.asyncio
    async def test_click_element_error(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for.side_effect = Exception("Not visible")
        mock_session_manager.page.locator.return_value = mock_element
        
        result = await tools['click_element'](
            caller="test",
            locator_value="#missing-btn",
            locator_strategy="css"
        )
        response = json.loads(result)
        assert response["status"] == "error"

    @pytest.mark.asyncio
    async def test_send_keys_success(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content.return_value = "<html></html>"
        
        result = await tools['send_keys'](
            caller="test",
            locator_value="#input",
            locator_strategy="css",
            text="hello world"
        )
        response = json.loads(result)
        assert response["status"] == "success"
        mock_element.fill.assert_called_once_with("hello world")

    @pytest.mark.asyncio
    async def test_send_keys_error(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for.side_effect = Exception("Not found")
        mock_session_manager.page.locator.return_value = mock_element
        
        result = await tools['send_keys'](
            caller="test",
            locator_value="#missing-input",
            locator_strategy="css",
            text="test"
        )
        response = json.loads(result)
        assert response["status"] == "error"

    @pytest.mark.asyncio
    async def test_get_text_success(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.inner_text.return_value = "Hello World"
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content.return_value = "<html></html>"
        
        result = await tools['get_text'](
            caller="test",
            locator_value=".text-element",
            locator_strategy="css"
        )
        response = json.loads(result)
        assert response["status"] == "success"
        assert response["data"]["text"] == "Hello World"

    @pytest.mark.asyncio
    async def test_get_page_title_success(self, tools, mock_session_manager):
        mock_session_manager.page.title.return_value = "My Page Title"
        mock_session_manager.page.content.return_value = "<html></html>"
        
        result = await tools['get_page_title'](caller="test")
        response = json.loads(result)
        assert response["status"] == "success"
        assert response["data"]["title"] == "My Page Title"

    @pytest.mark.asyncio
    async def test_get_page_url_success(self, tools, mock_session_manager):
        mock_session_manager.page.url = "https://example.com/page"
        mock_session_manager.page.content.return_value = "<html></html>"
        
        result = await tools['get_page_url'](caller="test")
        response = json.loads(result)
        assert response["status"] == "success"
        assert response["data"]["url"] == "https://example.com/page"

    @pytest.mark.asyncio
    async def test_wait_for_element_success(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content.return_value = "<html></html>"
        
        result = await tools['wait_for_element'](
            caller="test",
            locator_value=".dynamic-element",
            locator_strategy="css",
            timeout=10000
        )
        response = json.loads(result)
        assert response["status"] == "success"
        mock_element.wait_for.assert_called_once_with(state="visible", timeout=10000)

    @pytest.mark.asyncio
    async def test_wait_for_element_timeout(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for.side_effect = Exception("Timeout")
        mock_session_manager.page.locator.return_value = mock_element
        
        result = await tools['wait_for_element'](
            caller="test",
            locator_value=".slow-element",
            locator_strategy="css"
        )
        response = json.loads(result)
        assert response["status"] == "error"

    @pytest.mark.asyncio
    async def test_select_option_success(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content.return_value = "<html></html>"
        
        result = await tools['select_option'](
            caller="test",
            locator_value="#dropdown",
            option_value="option1"
        )
        response = json.loads(result)
        assert response["status"] == "success"
        mock_element.select_option.assert_called_once_with("option1")

    @pytest.mark.asyncio
    async def test_press_key_success(self, tools, mock_session_manager):
        mock_session_manager.page.content.return_value = "<html></html>"
        
        result = await tools['press_key'](
            caller="test",
            key="Enter"
        )
        response = json.loads(result)
        assert response["status"] == "success"
        mock_session_manager.page.keyboard.press.assert_called_once_with("Enter")

    @pytest.mark.asyncio
    async def test_screenshot_success(self, tools, mock_session_manager):
        result = await tools['screenshot'](
            caller="test",
            file_path="/tmp/screenshot.png"
        )
        response = json.loads(result)
        assert response["status"] == "success"
        assert response["data"]["screenshot_path"] == "/tmp/screenshot.png"
        mock_session_manager.page.screenshot.assert_called_once_with(
            path="/tmp/screenshot.png", full_page=True
        )

    @pytest.mark.asyncio
    async def test_screenshot_error(self, tools, mock_session_manager):
        mock_session_manager.page.screenshot.side_effect = Exception("Screenshot failed")
        result = await tools['screenshot'](
            caller="test",
            file_path="/invalid/path.png"
        )
        response = json.loads(result)
        assert response["status"] == "error"

    @pytest.mark.asyncio
    async def test_execute_javascript_success(self, tools, mock_session_manager):
        mock_session_manager.page.evaluate.return_value = "js_result"
        mock_session_manager.page.content.return_value = "<html></html>"
        
        result = await tools['execute_javascript'](
            caller="test",
            script="document.title"
        )
        response = json.loads(result)
        assert response["status"] == "success"
        assert response["data"]["result"] == "js_result"

    @pytest.mark.asyncio
    async def test_execute_javascript_error(self, tools, mock_session_manager):
        mock_session_manager.page.evaluate.side_effect = Exception("JS error")
        
        result = await tools['execute_javascript'](
            caller="test",
            script="invalidScript()"
        )
        response = json.loads(result)
        assert response["status"] == "error"

    @pytest.mark.asyncio
    async def test_navigate_with_page_source_file(self, tools, mock_session_manager):
        mock_session_manager.page.content.return_value = "<html><body>Test</body></html>"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            temp_path = f.name
        
        try:
            result = await tools['browser_navigate'](
                caller="test",
                url="https://example.com",
                page_source_file=temp_path
            )
            response = json.loads(result)
            assert response["status"] == "success"
            assert response["data"]["page_source_file"] == temp_path
            assert os.path.exists(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_navigate_with_summary_only(self, tools, mock_session_manager):
        mock_session_manager.page.content.return_value = "<html><body><div>Hello</div></body></html>"
        
        result = await tools['browser_navigate'](
            caller="test",
            url="https://example.com",
            summary_only=True
        )
        response = json.loads(result)
        assert response["status"] == "success"
        assert "page_source_summary" in response["data"]
