# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import pytest
import json
import os
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.verify_tools import register_verify_tools


class TestVerifyTools:
    """Tests for verify tools"""

    @pytest.fixture
    def mock_session_manager(self):
        manager = MagicMock()
        mock_page = MagicMock()
        mock_page.content = AsyncMock(return_value="<html><body>Test</body></html>")
        mock_page.get_by_text = MagicMock()
        
        mock_locator = MagicMock()
        mock_locator.wait_for = AsyncMock()
        mock_locator.count = AsyncMock(return_value=1)
        mock_locator.inner_text = AsyncMock(return_value="text")
        mock_locator.input_value = AsyncMock(return_value="value")
        mock_locator.evaluate = AsyncMock(return_value="input")
        mock_locator.is_checked = AsyncMock(return_value=True)
        mock_locator.get_attribute = AsyncMock(return_value="active")
        mock_page.locator = MagicMock(return_value=mock_locator)
        
        manager.page = mock_page
        manager.gen_code_cache = []
        manager.gen_code_id = None
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
        register_verify_tools(mock_mcp, mock_session_manager)
        return mock_mcp._registered_tools

    @pytest.mark.asyncio
    async def test_verify_element_exists_success(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_element.count = AsyncMock(return_value=1)
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content = AsyncMock(return_value="<html></html>")
        
        result = await tools['verify_element_exists'](
            caller="test",
            locator_value=".my-class",
            locator_strategy="css"
        )
        response = json.loads(result)
        assert response["status"] == "success"

    @pytest.mark.asyncio
    async def test_verify_element_exists_not_found(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock(side_effect=Exception("Not visible"))
        mock_session_manager.page.locator.return_value = mock_element
        
        result = await tools['verify_element_exists'](
            caller="test",
            locator_value=".nonexistent",
            locator_strategy="css"
        )
        response = json.loads(result)
        assert response["status"] == "error"

    @pytest.mark.asyncio
    async def test_verify_element_not_exists_success(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.count = AsyncMock(return_value=0)
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content = AsyncMock(return_value="<html></html>")
        
        result = await tools['verify_element_not_exists'](
            caller="test",
            locator_value=".removed-element",
            locator_strategy="css"
        )
        response = json.loads(result)
        assert response["status"] == "success"

    @pytest.mark.asyncio
    async def test_verify_element_not_exists_still_exists(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.count = AsyncMock(return_value=1)
        mock_session_manager.page.locator.return_value = mock_element
        
        result = await tools['verify_element_not_exists'](
            caller="test",
            locator_value=".still-here",
            locator_strategy="css"
        )
        response = json.loads(result)
        assert response["status"] == "error"
        assert "still exists" in response["error"]

    @pytest.mark.asyncio
    async def test_verify_element_not_exists_exception_is_success(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.count = AsyncMock(side_effect=Exception("Element not found"))
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content = AsyncMock(return_value="<html></html>")
        
        result = await tools['verify_element_not_exists'](
            caller="test",
            locator_value=".gone-element",
            locator_strategy="css"
        )
        response = json.loads(result)
        assert response["status"] == "success"

    @pytest.mark.asyncio
    async def test_verify_element_attribute_equals(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_element.get_attribute = AsyncMock(return_value="active")
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content = AsyncMock(return_value="<html></html>")
        
        result = await tools['verify_element_attribute'](
            caller="test",
            locator_value=".btn",
            locator_strategy="css",
            attribute_name="class",
            expected_value="active",
            rule="=="
        )
        response = json.loads(result)
        assert response["status"] == "success"

    @pytest.mark.asyncio
    async def test_verify_element_attribute_not_equals(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_element.get_attribute = AsyncMock(return_value="inactive")
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content = AsyncMock(return_value="<html></html>")
        
        result = await tools['verify_element_attribute'](
            caller="test",
            locator_value=".btn",
            locator_strategy="css",
            attribute_name="class",
            expected_value="active",
            rule="!="
        )
        response = json.loads(result)
        assert response["status"] == "success"

    @pytest.mark.asyncio
    async def test_verify_element_attribute_contains(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_element.get_attribute = AsyncMock(return_value="btn-primary active")
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content = AsyncMock(return_value="<html></html>")
        
        result = await tools['verify_element_attribute'](
            caller="test",
            locator_value=".btn",
            locator_strategy="css",
            attribute_name="class",
            expected_value="active",
            rule="contains"
        )
        response = json.loads(result)
        assert response["status"] == "success"

    @pytest.mark.asyncio
    async def test_verify_element_attribute_equals_mismatch(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_element.get_attribute = AsyncMock(return_value="inactive")
        mock_session_manager.page.locator.return_value = mock_element
        
        result = await tools['verify_element_attribute'](
            caller="test",
            locator_value=".btn",
            locator_strategy="css",
            attribute_name="class",
            expected_value="active",
            rule="=="
        )
        response = json.loads(result)
        assert response["status"] == "error"

    @pytest.mark.asyncio
    async def test_verify_element_attribute_not_equals_mismatch(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_element.get_attribute = AsyncMock(return_value="active")
        mock_session_manager.page.locator.return_value = mock_element
        
        result = await tools['verify_element_attribute'](
            caller="test",
            locator_value=".btn",
            locator_strategy="css",
            attribute_name="class",
            expected_value="active",
            rule="!="
        )
        response = json.loads(result)
        assert response["status"] == "error"

    @pytest.mark.asyncio
    async def test_verify_element_attribute_contains_mismatch(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_element.get_attribute = AsyncMock(return_value="btn-primary")
        mock_session_manager.page.locator.return_value = mock_element
        
        result = await tools['verify_element_attribute'](
            caller="test",
            locator_value=".btn",
            locator_strategy="css",
            attribute_name="class",
            expected_value="active",
            rule="contains"
        )
        response = json.loads(result)
        assert response["status"] == "error"

    @pytest.mark.asyncio
    async def test_verify_element_attribute_default_rule(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_element.get_attribute = AsyncMock(return_value="active")
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content = AsyncMock(return_value="<html></html>")
        
        result = await tools['verify_element_attribute'](
            caller="test",
            locator_value=".btn",
            locator_strategy="css",
            attribute_name="class",
            expected_value="active",
            rule=""
        )
        response = json.loads(result)
        assert response["status"] == "success"

    @pytest.mark.asyncio
    async def test_verify_element_attribute_unsupported_rule(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_element.get_attribute = AsyncMock(return_value="active")
        mock_session_manager.page.locator.return_value = mock_element
        
        result = await tools['verify_element_attribute'](
            caller="test",
            locator_value=".btn",
            locator_strategy="css",
            attribute_name="class",
            expected_value="active",
            rule="matches"
        )
        response = json.loads(result)
        assert response["status"] == "error"

    @pytest.mark.asyncio
    async def test_verify_text_on_page_success(self, tools, mock_session_manager):
        mock_text_element = MagicMock()
        mock_text_element.wait_for = AsyncMock()
        mock_session_manager.page.get_by_text.return_value.first = mock_text_element
        mock_session_manager.page.content = AsyncMock(return_value="<html></html>")
        
        result = await tools['verify_text_on_page'](
            caller="test",
            text="Welcome"
        )
        response = json.loads(result)
        assert response["status"] == "success"

    @pytest.mark.asyncio
    async def test_verify_text_on_page_not_found(self, tools, mock_session_manager):
        mock_text_element = MagicMock()
        mock_text_element.wait_for = AsyncMock(side_effect=Exception("Text not found"))
        mock_session_manager.page.get_by_text.return_value.first = mock_text_element
        
        result = await tools['verify_text_on_page'](
            caller="test",
            text="NotPresent"
        )
        response = json.loads(result)
        assert response["status"] == "error"

    @pytest.mark.asyncio
    async def test_verify_element_attribute_with_xpath(self, tools, mock_session_manager):
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_element.get_attribute = AsyncMock(return_value="test-value")
        mock_session_manager.page.locator.return_value = mock_element
        mock_session_manager.page.content = AsyncMock(return_value="<html></html>")
        
        result = await tools['verify_element_attribute'](
            caller="test",
            locator_value="//div[@id='test']",
            locator_strategy="xpath",
            attribute_name="data-value",
            expected_value="test-value",
            rule="=="
        )
        response = json.loads(result)
        assert response["status"] == "success"
