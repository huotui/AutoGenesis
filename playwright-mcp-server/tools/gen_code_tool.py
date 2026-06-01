# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import json
import os
import re
import logging
import sys
import time
import uuid
from pathlib import Path
from utils.logger import log_tool_call
from utils.gen_code import PYTEST_HEADER_TEMPLATE, NATIVE_PLAYWRIGHT_HEADER_TEMPLATE, TESTCASE_DIR, TARGET_TEST_FILE_DEFAULT
from utils.gen_code import gen_code_preview
from utils.response_format import format_tool_response, init_tool_response
from utils.logger import get_mcp_logger


logger = get_mcp_logger()


def register_gen_code_tools(mcp, session_manager):
    """Register generate code tools to MCP server."""    
    
    @mcp.tool()
    @log_tool_call
    async def before_gen_code(feature_file: str = '', step_file: str = '', code_format: str = 'mcp') -> str:
        """
        Clear cache and initialize code generation session before executing test case steps.
        
        This function should only be called before the first step of a test case execution.
        It clears any existing code generation cache and sets up a new generation session
        with a unique ID.
        
        Args:
            feature_file (str, optional): Full absolute path to the .feature file containing BDD scenarios.
                If not specified, do not provide a random value.
            step_file (str, optional): Full absolute path to the Python step definition file (.py).
                If not specified, do not provide a random value.
            code_format (str, optional): Code generation format. 'mcp' for MCP-based tests (default),
                'native' for native Playwright tests with better performance.
                
        Returns:
            str: JSON response containing:
                - status: "success" or "error"
                - data: Dictionary with gen_code_id, steps_dir, and step_file_target
                - error: Error message if operation failed
         
        """
        try:
            resp = init_tool_response()
            session_manager.clear_gen_code_cache()
            session_manager.gen_code_id = str(uuid.uuid4())
            session_manager.code_format = code_format
            logger.info(f"[GEN CODE START]:{session_manager.gen_code_id}, format:{code_format}")
        
            if step_file and step_file.endswith('.py'):
                session_manager.step_file_target = step_file
            elif feature_file:
                feature_name = Path(feature_file).stem
                test_file_name = f"test_{feature_name}.py"
                session_manager.step_file_target = os.path.join(TESTCASE_DIR, test_file_name)
            else:
                session_manager.step_file_target = TARGET_TEST_FILE_DEFAULT

            session_manager.steps_dir = TESTCASE_DIR

            resp["status"] = "success"
            resp["data"] = {
                "gen_code_id": session_manager.gen_code_id,
                "steps_dir": session_manager.steps_dir,
                "step_file_target": session_manager.step_file_target,
                "code_format": code_format,
            }
        except Exception as e:
            resp["error"] = f"Error during code generation: {repr(e)}"
            logger.error(f"Error during code generation: {repr(e)}")
            raise e

        return json.dumps(format_tool_response(resp))
    
    @mcp.tool()
    @log_tool_call
    async def preview_code_changes(code_format: str = '') -> str:
        """Preview generated test code changes and confirm before applying"""
        resp = init_tool_response()
        
        if not session_manager.gen_code_id or not session_manager.gen_code_cache:
            resp["status"] = "success"
            resp["data"] = {"message": "No pending code changes to preview"}
            return json.dumps(format_tool_response(resp))
        
        format_to_use = code_format if code_format else getattr(session_manager, 'code_format', 'mcp')
        result = gen_code_preview(session_manager, format_to_use)
        resp["status"] = "success"
        resp["data"] = {"diff_preview": result.get('diff_preview'), "code_format": format_to_use}
        
        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    async def confirm_code_changes() -> str:
        """Confirm the previewed code changes and generate pytest test file"""
        resp = init_tool_response()
        
        if not hasattr(session_manager, 'proposed_changes') or not session_manager.proposed_changes:
            resp["status"] = "success"
            resp["data"] = {"message": "No pending code changes to confirm"}
            return json.dumps(format_tool_response(resp))
        
        try:
            test_file_path = Path(session_manager.step_file_target)
            
            test_func_name = getattr(session_manager, 'test_func_name', 
                                    f"test_{session_manager.gen_code_id.replace('-', '_')[:30]}")
            
            scenario_name = ""
            if session_manager.gen_code_cache:
                first_step = session_manager.gen_code_cache[0]
                scenario_name = first_step.get("scenario", "自动生成的测试场景")
            
            if not scenario_name:
                scenario_name = "自动生成的测试场景"
            
            code_format = getattr(session_manager, 'code_format', 'mcp')
            
            if code_format == "native":
                test_content = NATIVE_PLAYWRIGHT_HEADER_TEMPLATE + "\n"
                test_content += f'\n\n@allure.epic("{scenario_name}")\n'
                test_content += f'@allure.title("{scenario_name}")\n'
                test_content += f'@pytest.mark.asyncio\n'
                test_content += f'async def {test_func_name}():\n'
                test_content += f'    """{scenario_name}"""\n'
                test_content += f'    async with async_playwright() as p:\n'
                test_content += f'        browser = await p.chromium.launch(headless=False)\n'
                test_content += f'        context = await browser.new_context()\n'
                test_content += f'        page = await context.new_page()\n'
                test_content += f'        \n'
                test_content += f'        try:\n'
                
                has_screenshot = False
                for step_code in session_manager.proposed_changes:
                    test_content += step_code + "\n"
                    if "screenshot" in step_code:
                        has_screenshot = True
                
                if not has_screenshot:
                    test_content += f'            \n'
                    test_content += f'            screenshot_path = os.path.join(\n'
                    test_content += f'                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),\n'
                    test_content += f'                "log",\n'
                    test_content += f'                "screenshot",\n'
                    test_content += f'                "{test_func_name}.png"\n'
                    test_content += f'            )\n'
                    test_content += f'            await page.screenshot(path=screenshot_path)\n'
                    test_content += f'            readAttach_mcp(screenshot_path, "{test_func_name}")\n'
                
                test_content += f'        \n'
                test_content += f'        finally:\n'
                test_content += f'            await context.close()\n'
                test_content += f'            await browser.close()\n'
            else:
                test_content = PYTEST_HEADER_TEMPLATE + "\n"
                test_content += f'\n\n@allure.epic("{scenario_name}")\n'
                test_content += f'@allure.title("{scenario_name}")\n'
                test_content += f'@pytest.mark.asyncio\n'
                test_content += f'async def {test_func_name}():\n'
                test_content += f'    """{scenario_name}"""\n'
                test_content += f'    client = MCPClient()\n'
                test_content += f'    \n'
                test_content += f'    try:\n'
                test_content += f'        await client.connect()\n'
                test_content += f'        \n'
                test_content += f'        await asyncio.sleep(2)\n'
                
                has_screenshot = False
                for step_code in session_manager.proposed_changes:
                    test_content += step_code + "\n"
                    if "screenshot" in step_code:
                        has_screenshot = True
                
                if not has_screenshot:
                    test_content += f'        \n'
                    test_content += f'        screenshot_path = os.path.join(\n'
                    test_content += f'            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),\n'
                    test_content += f'            "log",\n'
                    test_content += f'            "screenshot",\n'
                    test_content += f'            "{test_func_name}.png"\n'
                    test_content += f'        )\n'
                    test_content += f'        await client.screenshot(\n'
                    test_content += f'            file_path=screenshot_path,\n'
                    test_content += f'            step="Take screenshot",\n'
                    test_content += f'            scenario="{scenario_name}"\n'
                    test_content += f'        )\n'
                    test_content += f'        readAttach_mcp(screenshot_path, "{test_func_name}")\n'
                
                test_content += f'    \n'
                test_content += f'    finally:\n'
                test_content += f'        await client.close()\n'
            
            test_file_path.parent.mkdir(parents=True, exist_ok=True)
            test_file_path.write_text(test_content, encoding='utf-8')
            
            session_manager.new_steps_count = len(session_manager.proposed_changes)
            resp["status"] = "success"
            resp["data"] = {
                "message": f"Generated pytest test file: {test_file_path}",
                "new_steps_count": session_manager.new_steps_count,
                "test_file_path": str(test_file_path),
                "test_func_name": test_func_name,
                "code_format": code_format
            }
            logger.info(f"Successfully generated test file: {test_file_path} (format: {code_format})")
        except Exception as e:
            result = f"Error generating test file: {str(e)}"
            logger.error(result)
            resp["status"] = "error"
            resp["error"] = result
            import traceback
            logger.error(traceback.format_exc())
        
        session_manager.clear_gen_code_cache()
        return json.dumps(format_tool_response(resp))


