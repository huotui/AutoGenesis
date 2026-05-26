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
        mock_page.goto = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html><body>Test</body></html>")
        mock_page.title = AsyncMock(return_value="Test Page")
        mock_page.url = "https://example.com"
        mock_page.keyboard = MagicMock()
        mock_page.keyboard.press = AsyncMock()
        mock_page.screenshot = AsyncMock()
        mock_page.evaluate = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.get_by_text = MagicMock()
        
        mock_locator = MagicMock()
        mock_locator.wait_for = AsyncMock()
        mock_locator.count = AsyncMock(return_value=1)
        mock_locator.click = AsyncMock()
        mock_locator.hover = AsyncMock()
        mock_locator.fill = AsyncMock()
        mock_locator.inner_text = AsyncMock(return_value="Some text")
        mock_locator.input_value = AsyncMock(return_value="input value")
        mock_locator.scroll_into_view_if_needed = AsyncMock()
        mock_locator.select_option = AsyncMock()
        mock_locator.get_attribute = AsyncMock(return_value="active")
        mock_locator.evaluate = AsyncMock(return_value="input")
        mock_locator.is_checked = AsyncMock(return_value=True)
        mock_page.locator = MagicMock(return_value=mock_locator)
        
        manager.page = mock_page
        manager.gen_code_cache = []
        manager.gen_code_id = None
        manager.close_async = AsyncMock()
        manager.close = MagicMock()
        manager.should_fetch_page_source = MagicMock(return_value=True)
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
        mock_session_manager.close_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_browser_close_error(self, tools, mock_session_manager):
        mock_session_manager.close_async = AsyncMock(side_effect=Exception("Close failed"))
        result = await tools['browser_close'](caller="test")
        response = json.loads(result)
        assert response["status"] == "error"

    @pytest.mark.asyncio
    async def test_find_element_success(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_element.count = AsyncMock(return_value=1)
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content = AsyncMock(return_value="<html></html>")
        
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
        mock_element.wait_for = AsyncMock(side_effect=Exception("Element not visible"))
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
        mock_element.wait_for = AsyncMock()
        mock_element.click = AsyncMock()
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content = AsyncMock(return_value="<html></html>")
        
        result = await tools['click_element'](
            caller="test",
            locator_value="#btn",
            locator_strategy="css"
        )
        response = json.loads(result)
        assert response["status"] == "success"
        mock_element.click.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_click_element_error(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock(side_effect=Exception("Not visible"))
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
        mock_element.wait_for = AsyncMock()
        mock_element.fill = AsyncMock()
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content = AsyncMock(return_value="<html></html>")
        
        result = await tools['send_keys'](
            caller="test",
            locator_value="#input",
            locator_strategy="css",
            text="hello world"
        )
        response = json.loads(result)
        assert response["status"] == "success"
        mock_element.fill.assert_awaited_once_with("hello world")

    @pytest.mark.asyncio
    async def test_send_keys_error(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock(side_effect=Exception("Not found"))
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
        mock_element.wait_for = AsyncMock()
        mock_element.inner_text = AsyncMock(return_value="Hello World")
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content = AsyncMock(return_value="<html></html>")
        
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
        mock_session_manager.page.content = AsyncMock(return_value="<html></html>")
        
        result = await tools['get_page_url'](caller="test")
        response = json.loads(result)
        assert response["status"] == "success"
        assert response["data"]["url"] == "https://example.com/page"

    @pytest.mark.asyncio
    async def test_wait_for_element_success(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content = AsyncMock(return_value="<html></html>")
        
        result = await tools['wait_for_element'](
            caller="test",
            locator_value=".dynamic-element",
            locator_strategy="css",
            timeout=10000
        )
        response = json.loads(result)
        assert response["status"] == "success"
        mock_element.wait_for.assert_awaited_once_with(state="visible", timeout=10000)

    @pytest.mark.asyncio
    async def test_wait_for_element_timeout(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock(side_effect=Exception("Timeout"))
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
        mock_element.wait_for = AsyncMock()
        mock_element.select_option = AsyncMock()
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content = AsyncMock(return_value="<html></html>")
        
        result = await tools['select_option'](
            caller="test",
            locator_value="#dropdown",
            option_value="option1"
        )
        response = json.loads(result)
        assert response["status"] == "success"
        mock_element.select_option.assert_awaited_once_with("option1")

    @pytest.mark.asyncio
    async def test_press_key_success(self, tools, mock_session_manager):
        mock_session_manager.page.content = AsyncMock(return_value="<html></html>")
        
        result = await tools['press_key'](
            caller="test",
            key="Enter"
        )
        response = json.loads(result)
        assert response["status"] == "success"
        mock_session_manager.page.keyboard.press.assert_awaited_once_with("Enter")

    @pytest.mark.asyncio
    async def test_screenshot_success(self, tools, mock_session_manager):
        result = await tools['screenshot'](
            caller="test",
            file_path="/tmp/screenshot.png"
        )
        response = json.loads(result)
        assert response["status"] == "success"
        assert response["data"]["screenshot_path"] == "/tmp/screenshot.png"
        mock_session_manager.page.screenshot.assert_awaited_once_with(
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

    @pytest.mark.asyncio
    async def test_upload_file_single_file(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_element.set_input_files = AsyncMock()
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content = AsyncMock(return_value="<html></html>")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            result = await tools['upload_file'](
                caller="test",
                locator_value="#file-input",
                locator_strategy="css",
                file_paths=[temp_path]
            )
            response = json.loads(result)
            assert response["status"] == "success"
            assert len(response["data"]["uploaded_files"]) == 1
            assert response["data"]["uploaded_files"][0].endswith(".txt")
            mock_element.set_input_files.assert_awaited_once()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_upload_file_multiple_files(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_element.set_input_files = AsyncMock()
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content = AsyncMock(return_value="<html></html>")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f1:
            f1.write("content 1")
            temp_path1 = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f2:
            f2.write("content 2")
            temp_path2 = f2.name
        
        try:
            result = await tools['upload_file'](
                caller="test",
                locator_value="#file-input",
                locator_strategy="css",
                file_paths=[temp_path1, temp_path2]
            )
            response = json.loads(result)
            assert response["status"] == "success"
            assert len(response["data"]["uploaded_files"]) == 2
            mock_element.set_input_files.assert_awaited_once()
        finally:
            if os.path.exists(temp_path1):
                os.unlink(temp_path1)
            if os.path.exists(temp_path2):
                os.unlink(temp_path2)

    @pytest.mark.asyncio
    async def test_upload_file_not_found(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_session_manager.page.locator.return_value = mock_element
        
        result = await tools['upload_file'](
            caller="test",
            locator_value="#file-input",
            locator_strategy="css",
            file_paths=["/nonexistent/path/file.txt"]
        )
        response = json.loads(result)
        assert response["status"] == "error"
        assert "File not found" in response["error"]

    @pytest.mark.asyncio
    async def test_upload_file_element_not_attached(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock(side_effect=Exception("Element not attached"))
        mock_session_manager.page.locator.return_value = mock_element
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            result = await tools['upload_file'](
                caller="test",
                locator_value="#missing-input",
                locator_strategy="css",
                file_paths=[temp_path]
            )
            response = json.loads(result)
            assert response["status"] == "error"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_wait_for_download_success(self, tools, mock_session_manager):
        mock_download = AsyncMock()
        mock_download.suggested_filename = "test_file.pdf"
        mock_download.save_as = AsyncMock()
        
        class MockDownloadInfo:
            @property
            async def value(self):
                return mock_download
        
        class MockExpectDownload:
            async def __aenter__(self):
                return MockDownloadInfo()
            async def __aexit__(self, *args):
                pass
        
        mock_session_manager.page.expect_download.return_value = MockExpectDownload()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = await tools['wait_for_download'](
                caller="test",
                download_dir=temp_dir,
                timeout=5000
            )
            response = json.loads(result)
            assert response["status"] == "success"
            assert response["data"]["file_name"] == "test_file.pdf"
            mock_download.save_as.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_wait_for_download_timeout(self, tools, mock_session_manager):
        class MockExpectDownloadTimeout:
            async def __aenter__(self):
                raise Exception("Timeout waiting for download")
            async def __aexit__(self, *args):
                pass
        
        mock_session_manager.page.expect_download.return_value = MockExpectDownloadTimeout()
        
        result = await tools['wait_for_download'](
            caller="test",
            download_dir="/tmp/downloads",
            timeout=1000
        )
        response = json.loads(result)
        assert response["status"] == "error"
        assert "Timeout" in response["error"]

    @pytest.mark.asyncio
    async def test_wait_for_download_default_dir(self, tools, mock_session_manager):
        mock_download = AsyncMock()
        mock_download.suggested_filename = "downloaded.txt"
        mock_download.save_as = AsyncMock()
        
        class MockDownloadInfo:
            @property
            async def value(self):
                return mock_download
        
        class MockExpectDownload:
            async def __aenter__(self):
                return MockDownloadInfo()
            async def __aexit__(self, *args):
                pass
        
        mock_session_manager.page.expect_download.return_value = MockExpectDownload()
        
        result = await tools['wait_for_download'](
            caller="test"
        )
        response = json.loads(result)
        assert response["status"] == "success"
        mock_download.save_as.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_verify_download_exists_with_filename(self, tools, mock_session_manager):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test_download.pdf")
            with open(test_file, 'w') as f:
                f.write("downloaded content")
            
            result = await tools['verify_download_exists'](
                caller="test",
                file_name="test_download.pdf",
                download_dir=temp_dir
            )
            response = json.loads(result)
            assert response["status"] == "success"
            assert response["data"]["file_exists"] is True
            assert response["data"]["file_size"] > 0

    @pytest.mark.asyncio
    async def test_verify_download_exists_file_not_found(self, tools, mock_session_manager):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = await tools['verify_download_exists'](
                caller="test",
                file_name="nonexistent.pdf",
                download_dir=temp_dir
            )
            response = json.loads(result)
            assert response["status"] == "success"
            assert response["data"]["file_exists"] is False

    @pytest.mark.asyncio
    async def test_verify_download_exists_any_file(self, tools, mock_session_manager):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "auto_download.txt")
            with open(test_file, 'w') as f:
                f.write("content")
            
            result = await tools['verify_download_exists'](
                caller="test",
                file_name="",
                download_dir=temp_dir
            )
            response = json.loads(result)
            assert response["status"] == "success"
            assert response["data"]["file_exists"] is True
            assert len(response["data"]["files"]) > 0

    @pytest.mark.asyncio
    async def test_verify_download_exists_empty_dir(self, tools, mock_session_manager):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = await tools['verify_download_exists'](
                caller="test",
                file_name="",
                download_dir=temp_dir
            )
            response = json.loads(result)
            assert response["status"] == "success"
            assert response["data"]["file_exists"] is False
