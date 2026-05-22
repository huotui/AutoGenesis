# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import json
import logging
from utils.logger import log_tool_call
from utils.response_format import format_tool_response, init_tool_response, handle_page_source
from utils.gen_code import record_calls
from tools.playwright_tool import get_playwright_locator
from utils.logger import get_mcp_logger
from llm.chat import LLMClient

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
    async def verify_visual_task(
        caller: str,
        screenshot_path: str,
        task_description: str,
        scenario: str = "",
        step_raw: str = "",
        step: str = "",
    ) -> str:
        """
        Read and analyze a screenshot, verify if the visual content matches the task description.

        Combines screenshot reading and visual analysis to verify UI content automatically.
        Ideal for visual verification in automated testing scenarios.

        Args:
            caller (str): Calling module/function identifier
            screenshot_path (str): Path to the screenshot image file
            task_description (str): Task to verify against the screenshot
            scenario (str): Test scenario name
            step_raw (str): Raw step text
            step (str): Current step description

        Returns:
            str: JSON response with status, verification result, reason, and error (if any)

        """
        resp = init_tool_response()
        try:
            if not screenshot_path.lower().endswith(".png"):
                raise ValueError("Only PNG format screenshots are supported.")
            
            with open(screenshot_path, "rb") as f:
                image_data = f.read()

            client = LLMClient()
            result = client.evaluate_task(task_info=task_description, image_data=image_data)

            resp["status"] = "success" if result.result else "error"
            resp["data"] = {
                "result": result.result,
                "reason": result.reason,
                "step_raw": step_raw,
            }
            if resp["status"] == "error":
                resp["error"] = result.reason
        except Exception as e:
            resp["status"] = "error"
            resp["error"] = repr(e)
            logger.error(f"Error in verify_visual_task: {e}")

        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    @record_calls(session_manager)
    async def evaluate_web_visual_task(
        caller: str,
        screenshot_path: str,
        task_description: str,
        scenario: str = "",
        step_raw: str = "",
        step: str = "",
    ) -> str:
        """
        Evaluate web page using both screenshot and page source with LLM.

        Uses AI to analyze the current page state by combining visual screenshot and HTML source.
        Ideal for complex UI verification that requires understanding both visual layout and DOM structure.

        Args:
            caller (str): Calling module/function identifier
            screenshot_path (str): Path to the screenshot image file
            task_description (str): Task description to evaluate
            scenario (str): Test scenario name
            step_raw (str): Raw step text
            step (str): Current step description

        Returns:
            str: JSON response with status, evaluation result, reason, and found elements (if any)

        """
        resp = init_tool_response()
        try:
            if not screenshot_path.lower().endswith(".png"):
                raise ValueError("Only PNG format screenshots are supported.")
            
            with open(screenshot_path, "rb") as f:
                image_data = f.read()

            page = session_manager.page
            page_source = await page.content()

            client = LLMClient()
            result = client.evaluate_web_task(
                task_info=task_description,
                page_source=page_source,
                image_data=image_data
            )

            resp["status"] = "success" if result.result else "error"
            resp["data"] = {
                "result": result.result,
                "reason": result.reason,
                "elements_found": result.elements_found if hasattr(result, 'elements_found') else [],
                "step_raw": step_raw,
            }
            if resp["status"] == "error":
                resp["error"] = result.reason
        except Exception as e:
            resp["status"] = "error"
            resp["error"] = repr(e)
            logger.error(f"Error in evaluate_web_visual_task: {e}")

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
