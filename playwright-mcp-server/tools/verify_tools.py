# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import json
import logging
from utils.logger import log_tool_call
from utils.response_format import format_tool_response, init_tool_response, handle_page_source
from utils.gen_code import record_calls
from tools.playwright_tool import get_playwright_locator
from utils.logger import get_mcp_logger

logger = get_mcp_logger()


def register_verify_tools(mcp, session_manager):
    """Register verify tools to MCP server."""

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def verify_element_exists(
        caller: str, locator_value: str, locator_strategy: str = "css", step: str = "", scenario: str = "", step_raw: str = ""
    ) -> str:
        """check/verify if an element exists/appears in the current page.

        Args:
            locator_value: required, element locator value
            locator_strategy: strategy of the locator (e.g., 'css', 'xpath', 'id', 'text', 'role')
            step: required, step name
            step_raw: required, raw original step text
            scenario: required, scenario name
        """
        resp = init_tool_response()
        try:
            page = session_manager.page
            locator = get_playwright_locator(locator_strategy, locator_value)
            
            element = page.locator(locator)
            # Wait for element to be attached to DOM, not necessarily visible
            await element.wait_for(state="attached", timeout=5000)
            
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
            handle_page_source(resp, page_source, "", False)

        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def verify_element_not_exists(
        caller: str, locator_value: str, locator_strategy: str = "css", step: str = "", scenario: str = "", step_raw: str = ""
    ) -> str:
        """check/verify if an element does not exist/disappear in the current page.

        Args:
            locator_value: required, element locator value
            locator_strategy: strategy of the locator (e.g., 'css', 'xpath', 'id', 'text', 'role')
            step: required, step name
            step_raw: required, raw original step text
            scenario: required, scenario name
        """
        resp = init_tool_response()
        try:
            page = session_manager.page
            locator = get_playwright_locator(locator_strategy, locator_value)
            
            element = page.locator(locator)
            count = await element.count()
            
            if count == 0:
                resp["status"] = "success"
            else:
                resp["status"] = "error"
                resp["error"] = f"Element {locator_value} still exists"
        except Exception as e:
            resp["status"] = "success"
            
        if resp.get("status") != "error":
            page_source = await page.content()
            handle_page_source(resp, page_source, "", False)

        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def verify_element_attribute(
        caller: str,
        locator_value: str,
        locator_strategy: str = "css",
        attribute_name: str = "",
        expected_value: str = "",
        rule: str = "",
        step: str = "",
        scenario: str = "",
        step_raw: str = "",
    ) -> str:
        """check/verify if an element has a specific attribute with the expected value under a specific rule.

        Args:
            locator_value: required, element locator value
            locator_strategy: strategy of the locator (e.g., 'css', 'xpath', 'id', 'text', 'role')
            attribute_name: required, name of the attribute to check
            expected_value: required, expected value of the attribute
            rule: the comparison rule to apply (e.g., "==","!=","contains" etc. (default is "==")
            step: required, step name
            step_raw: required, raw original step text
            scenario: required, scenario name
        """
        resp = init_tool_response()
        try:
            page = session_manager.page
            locator = get_playwright_locator(locator_strategy, locator_value)
            
            element = page.locator(locator)
            await element.wait_for(state="visible", timeout=5000)
            actual_value = await element.get_attribute(attribute_name)
            
            if rule == "":
                rule = "=="
            if rule == "==":
                if actual_value == expected_value:
                    resp["status"] = "success"
                else:
                    resp["status"] = "error"
                    resp["error"] = f"Element {locator_value} has {attribute_name}={actual_value}, expected {expected_value}"
            elif rule == "!=":
                if actual_value != expected_value:
                    resp["status"] = "success"
                else:
                    resp["status"] = "error"
                    resp["error"] = f"Element {locator_value} has {attribute_name}={actual_value}, not expected {expected_value}"
            elif rule == "contains":
                if expected_value in actual_value:
                    resp["status"] = "success"
                else:
                    resp["status"] = "error"
                    resp["error"] = f"Element {locator_value} does not contain {expected_value}, actual value is {actual_value}"
            else:
                raise ValueError(f"Unsupported rule: {rule}")
        except Exception as e:
            resp["error"] = repr(e)
            logger.error(f"Error verifying element attribute: {e}")
            
        if resp.get("status") != "error":
            page_source = await page.content()
            handle_page_source(resp, page_source, "", False)

        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def verify_text_on_page(
        caller: str,
        text: str,
        step: str = "",
        scenario: str = "",
        step_raw: str = "",
    ) -> str:
        """check/verify if text exists on the current page.

        Args:
            caller: caller name
            text: required, text to verify on page
            step: required, step name
            step_raw: required, raw original step text
            scenario: required, scenario name
        """
        resp = init_tool_response()
        try:
            page = session_manager.page
            
            try:
                await page.get_by_text(text).first.wait_for(state="visible", timeout=5000)
                resp["status"] = "success"
            except:
                resp["status"] = "error"
                resp["error"] = f"Text '{text}' not found on page"
        except Exception as e:
            resp["error"] = repr(e)
            logger.error(f"Error verifying text on page: {e}")
            
        if resp.get("status") != "error":
            page_source = await page.content()
            handle_page_source(resp, page_source, "", False)

        return json.dumps(format_tool_response(resp))
