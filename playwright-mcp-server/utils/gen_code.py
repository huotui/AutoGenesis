# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import copy
import json
import re
import os
import sys
import time
import inspect
import logging
import functools
import pprint
import textwrap
from pathlib import Path


logger = logging.getLogger(__name__)


PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTCASE_DIR = os.path.join(PARENT_DIR, '../PPA-UI-Automation-master/testcase')
TARGET_TEST_FILE_DEFAULT = os.path.join(TESTCASE_DIR, "test_generated.py")

MCP_SERVER_INTERNAL_CALL = "mcp-server-internal-transfer-call"

PYTEST_HEADER_TEMPLATE = """import os
import pytest
import allure
import asyncio
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.mcp_client import MCPClient
from common.attach import readAttach_mcp
"""

NATIVE_PLAYWRIGHT_HEADER_TEMPLATE = """import os
import pytest
import allure
import asyncio
from playwright.async_api import async_playwright, expect
from common.attach import readAttach_mcp
"""

TOOL_PARAMS_REPLACE_MAP = {}


def need_parameterize(step_info: dict, parameterized_size: int) -> bool:
    return False

def normalize_step_text(step_text_raw: str, step_info: dict) -> tuple:
    return step_text_raw, {}

def replace_package_in_locator(tool_params: dict, parameterized_args: dict) -> tuple:
    modified_params = copy.deepcopy(tool_params)
    return modified_params, None, False

def generate_args_data_multi_param(step_info: dict):
    tool_params = step_info.get("tool_params", {})
    args_str = pprint.pformat(tool_params, indent=0)
    return args_str, False


def generate_step_definition(step_info) -> str:
    tool_name = step_info.get("tool_name")
    tool_params = step_info.get("tool_params", {})
    step_text = step_info.get("step_text_raw", "")
    scenario = step_info.get("scenario", "")
    
    if not step_text:
        step_text = tool_params.get("step", "")
    
    if not scenario:
        scenario = tool_params.get("scenario", "")
    
    code_text = ""
    
    if tool_name == "browser_navigate":
        url = tool_params.get("url", "")
        code_text = f'''
        await client.browser_navigate(
            url="{url}",
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "click_element":
        locator_value = tool_params.get("locator_value", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        code_text = f'''
        await client.click_element(
            locator_value="{locator_value}",
            locator_strategy="{locator_strategy}",
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "send_keys":
        locator_value = tool_params.get("locator_value", "")
        text = tool_params.get("text", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        code_text = f'''
        await client.send_keys(
            locator_value="{locator_value}",
            locator_strategy="{locator_strategy}",
            text="{text}",
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "press_key":
        key = tool_params.get("key", "")
        code_text = f'''
        await client.press_key(
            key="{key}",
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "hover_element":
        locator_value = tool_params.get("locator_value", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        code_text = f'''
        await client.hover_element(
            locator_value="{locator_value}",
            locator_strategy="{locator_strategy}",
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "select_option":
        locator_value = tool_params.get("locator_value", "")
        option_value = tool_params.get("option_value", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        code_text = f'''
        await client.select_option(
            locator_value="{locator_value}",
            option_value="{option_value}",
            locator_strategy="{locator_strategy}",
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "get_text":
        locator_value = tool_params.get("locator_value", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        code_text = f'''
        await client.get_text(
            locator_value="{locator_value}",
            locator_strategy="{locator_strategy}",
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "get_page_title":
        code_text = f'''
        await client.get_page_title(
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "get_page_url":
        code_text = f'''
        await client.get_page_url(
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "wait_for_element":
        locator_value = tool_params.get("locator_value", "")
        timeout = tool_params.get("timeout", 5000)
        locator_strategy = tool_params.get("locator_strategy", "css")
        code_text = f'''
        await client.wait_for_element(
            locator_value="{locator_value}",
            locator_strategy="{locator_strategy}",
            timeout={timeout},
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "find_element":
        locator_value = tool_params.get("locator_value", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        code_text = f'''
        await client.find_element(
            locator_value="{locator_value}",
            locator_strategy="{locator_strategy}",
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "scroll_page":
        direction = tool_params.get("direction", "down")
        amount = tool_params.get("amount", 300)
        code_text = f'''
        await client.scroll_page(
            direction="{direction}",
            amount={amount},
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "scroll_to_element":
        locator_value = tool_params.get("locator_value", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        code_text = f'''
        await client.scroll_to_element(
            locator_value="{locator_value}",
            locator_strategy="{locator_strategy}",
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "execute_javascript":
        script = tool_params.get("script", "")
        script_escaped = script.replace('\\', '\\\\').replace('"', '\\"')
        code_text = f'''
        await client.execute_javascript(
            script="{script_escaped}",
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "screenshot":
        code_text = f'''
        screenshot_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "log",
            "screenshot",
            "screenshot_{test_func_name}.png"
        )
        await client.screenshot(
            file_path=screenshot_path,
            step="{step_text}",
            scenario="{scenario}"
        )
        readAttach_mcp(screenshot_path, "{test_func_name}")
'''
    elif tool_name == "verify_element_exists":
        locator_value = tool_params.get("locator_value", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        code_text = f'''
        await client.verify_element_exists(
            locator_value="{locator_value}",
            locator_strategy="{locator_strategy}",
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "verify_element_not_exists":
        locator_value = tool_params.get("locator_value", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        code_text = f'''
        await client.verify_element_not_exists(
            locator_value="{locator_value}",
            locator_strategy="{locator_strategy}",
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "verify_text_on_page":
        text = tool_params.get("text", "")
        code_text = f'''
        await client.verify_text_on_page(
            text="{text}",
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "verify_element_value":
        locator_value = tool_params.get("locator_value", "")
        expected_value = tool_params.get("expected_value", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        code_text = f'''
        await client.verify_element_value(
            locator_value="{locator_value}",
            expected_value="{expected_value}",
            locator_strategy="{locator_strategy}",
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "verify_element_attribute":
        locator_value = tool_params.get("locator_value", "")
        attribute_name = tool_params.get("attribute_name", "")
        expected_value = tool_params.get("expected_value", "")
        rule = tool_params.get("rule", "==")
        locator_strategy = tool_params.get("locator_strategy", "css")
        code_text = f'''
        await client.verify_element_attribute(
            locator_value="{locator_value}",
            attribute_name="{attribute_name}",
            expected_value="{expected_value}",
            rule="{rule}",
            locator_strategy="{locator_strategy}",
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "verify_checkbox_state":
        locator_value = tool_params.get("locator_value", "")
        expected_state = tool_params.get("expected_state", "checked")
        locator_strategy = tool_params.get("locator_strategy", "css")
        code_text = f'''
        await client.verify_checkbox_state(
            locator_value="{locator_value}",
            expected_state="{expected_state}",
            locator_strategy="{locator_strategy}",
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "upload_file":
        locator_value = tool_params.get("locator_value", "")
        file_paths = tool_params.get("file_paths", [])
        locator_strategy = tool_params.get("locator_strategy", "css")
        file_paths_str = str(file_paths).replace("'", '"')
        code_text = f'''
        await client.upload_file(
            locator_value="{locator_value}",
            file_paths={file_paths_str},
            locator_strategy="{locator_strategy}",
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "wait_for_download":
        download_dir = tool_params.get("download_dir", "")
        timeout = tool_params.get("timeout", 30000)
        params_code = f'            step="{step_text}",\n            scenario="{scenario}"'
        if download_dir:
            params_code = f'            download_dir="{download_dir}",\n            timeout={timeout},\n' + params_code
        else:
            params_code = f'            timeout={timeout},\n' + params_code
        code_text = f'''
        await client.wait_for_download(
{params_code}
        )
'''
    elif tool_name == "verify_download_exists":
        file_name = tool_params.get("file_name", "")
        download_dir = tool_params.get("download_dir", "")
        params_code = f'            step="{step_text}",\n            scenario="{scenario}"'
        if file_name:
            params_code = f'            file_name="{file_name}",\n' + params_code
        if download_dir:
            params_code = f'            download_dir="{download_dir}",\n' + params_code
        code_text = f'''
        await client.verify_download_exists(
{params_code}
        )
'''
    elif tool_name == "verify_visual_task":
        screenshot_path = tool_params.get("screenshot_path", "")
        task_description = tool_params.get("task_description", "")
        code_text = f'''
        await client.verify_visual_task(
            screenshot_path="{screenshot_path}",
            task_description="{task_description}",
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    elif tool_name == "evaluate_web_visual_task":
        screenshot_path = tool_params.get("screenshot_path", "")
        task_description = tool_params.get("task_description", "")
        code_text = f'''
        await client.evaluate_web_visual_task(
            screenshot_path="{screenshot_path}",
            task_description="{task_description}",
            step="{step_text}",
            scenario="{scenario}"
        )
'''
    else:
        params_str = ", ".join([f'{k}="{v}"' if isinstance(v, str) else f'{k}={v}' for k, v in tool_params.items() if k not in ['caller', 'step_raw', 'page_source_file', 'summary_only']])
        code_text = f'''
        await client.{tool_name}({params_str})
'''
    
    return code_text


def generate_native_playwright_definition(step_info) -> str:
    tool_name = step_info.get("tool_name")
    tool_params = step_info.get("tool_params", {})
    step_text = step_info.get("step_text_raw", "")
    scenario = step_info.get("scenario", "")
    
    if not step_text:
        step_text = tool_params.get("step", "")
    
    if not scenario:
        scenario = tool_params.get("scenario", "")
    
    code_text = ""
    
    if tool_name == "browser_navigate":
        url = tool_params.get("url", "")
        code_text = f'''
        await page.goto("{url}")
        await page.wait_for_load_state("networkidle")
'''
    elif tool_name == "click_element":
        locator_value = tool_params.get("locator_value", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        locator = get_playwright_locator(locator_strategy, locator_value)
        code_text = f'''
        await page.locator("{locator}").click()
'''
    elif tool_name == "send_keys":
        locator_value = tool_params.get("locator_value", "")
        text = tool_params.get("text", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        locator = get_playwright_locator(locator_strategy, locator_value)
        code_text = f'''
        await page.locator("{locator}").fill("{text}")
'''
    elif tool_name == "press_key":
        key = tool_params.get("key", "")
        code_text = f'''
        await page.keyboard.press("{key}")
'''
    elif tool_name == "hover_element":
        locator_value = tool_params.get("locator_value", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        locator = get_playwright_locator(locator_strategy, locator_value)
        code_text = f'''
        await page.locator("{locator}").hover()
'''
    elif tool_name == "select_option":
        locator_value = tool_params.get("locator_value", "")
        option_value = tool_params.get("option_value", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        locator = get_playwright_locator(locator_strategy, locator_value)
        code_text = f'''
        await page.locator("{locator}").select_option("{option_value}")
'''
    elif tool_name == "get_text":
        locator_value = tool_params.get("locator_value", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        locator = get_playwright_locator(locator_strategy, locator_value)
        code_text = f'''
        text_content = await page.locator("{locator}").text_content()
'''
    elif tool_name == "get_page_title":
        code_text = f'''
        page_title = await page.title()
'''
    elif tool_name == "get_page_url":
        code_text = f'''
        page_url = page.url
'''
    elif tool_name == "wait_for_element":
        locator_value = tool_params.get("locator_value", "")
        timeout = tool_params.get("timeout", 5000)
        locator_strategy = tool_params.get("locator_strategy", "css")
        locator = get_playwright_locator(locator_strategy, locator_value)
        timeout_sec = timeout / 1000.0
        code_text = f'''
        await page.wait_for_selector("{locator}", timeout={timeout})
'''
    elif tool_name == "find_element":
        locator_value = tool_params.get("locator_value", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        locator = get_playwright_locator(locator_strategy, locator_value)
        code_text = f'''
        element = page.locator("{locator}")
'''
    elif tool_name == "scroll_page":
        direction = tool_params.get("direction", "down")
        amount = tool_params.get("amount", 300)
        scroll_value = amount if direction == "down" else -amount
        code_text = f'''
        await page.evaluate("window.scrollBy(0, {scroll_value})")
'''
    elif tool_name == "scroll_to_element":
        locator_value = tool_params.get("locator_value", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        locator = get_playwright_locator(locator_strategy, locator_value)
        code_text = f'''
        await page.locator("{locator}").scroll_into_view_if_needed()
'''
    elif tool_name == "execute_javascript":
        script = tool_params.get("script", "")
        script_escaped = script.replace('\\', '\\\\').replace('"', '\\"')
        code_text = f'''
        result = await page.evaluate("{script_escaped}")
'''
    elif tool_name == "screenshot":
        code_text = f'''
        screenshot_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "log",
            "screenshot",
            "screenshot_{test_func_name}.png"
        )
        await page.screenshot(path=screenshot_path)
        readAttach_mcp(screenshot_path, "{test_func_name}")
'''
    elif tool_name == "verify_element_exists":
        locator_value = tool_params.get("locator_value", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        locator = get_playwright_locator(locator_strategy, locator_value)
        code_text = f'''
        await expect(page.locator("{locator}")).to_be_visible()
'''
    elif tool_name == "verify_element_not_exists":
        locator_value = tool_params.get("locator_value", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        locator = get_playwright_locator(locator_strategy, locator_value)
        code_text = f'''
        await expect(page.locator("{locator}")).not_to_be_visible()
'''
    elif tool_name == "verify_text_on_page":
        text = tool_params.get("text", "")
        code_text = f'''
        await expect(page).to_contain_text("{text}")
'''
    elif tool_name == "verify_element_value":
        locator_value = tool_params.get("locator_value", "")
        expected_value = tool_params.get("expected_value", "")
        locator_strategy = tool_params.get("locator_strategy", "css")
        locator = get_playwright_locator(locator_strategy, locator_value)
        code_text = f'''
        await expect(page.locator("{locator}")).to_have_value("{expected_value}")
'''
    elif tool_name == "verify_element_attribute":
        locator_value = tool_params.get("locator_value", "")
        attribute_name = tool_params.get("attribute_name", "")
        expected_value = tool_params.get("expected_value", "")
        rule = tool_params.get("rule", "==")
        locator_strategy = tool_params.get("locator_strategy", "css")
        locator = get_playwright_locator(locator_strategy, locator_value)
        code_text = f'''
        await expect(page.locator("{locator}")).to_have_attribute("{attribute_name}", "{expected_value}")
'''
    elif tool_name == "verify_checkbox_state":
        locator_value = tool_params.get("locator_value", "")
        expected_state = tool_params.get("expected_state", "checked")
        locator_strategy = tool_params.get("locator_strategy", "css")
        locator = get_playwright_locator(locator_strategy, locator_value)
        if expected_state == "checked":
            code_text = f'''
        await expect(page.locator("{locator}")).to_be_checked()
'''
        else:
            code_text = f'''
        await expect(page.locator("{locator}")).not_to_be_checked()
'''
    elif tool_name == "upload_file":
        locator_value = tool_params.get("locator_value", "")
        file_paths = tool_params.get("file_paths", [])
        locator_strategy = tool_params.get("locator_strategy", "css")
        locator = get_playwright_locator(locator_strategy, locator_value)
        file_paths_str = str(file_paths).replace("'", '"')
        code_text = f'''
        async with page.expect_file_chooser() as fc_info:
            await page.locator("{locator}").click()
        file_chooser = await fc_info.value
        await file_chooser.set_files({file_paths_str})
'''
    elif tool_name == "wait_for_download":
        timeout = tool_params.get("timeout", 30000)
        code_text = f'''
        async with page.expect_download(timeout={timeout}) as download_info:
            pass
        download = await download_info.value
'''
    elif tool_name == "verify_download_exists":
        file_name = tool_params.get("file_name", "")
        code_text = f'''
        import glob
        download_dir = os.path.join(os.getcwd(), "downloads")
        files = glob.glob(os.path.join(download_dir, "{file_name if file_name else '*'}"))
        assert len(files) > 0, "Download file not found"
'''
    elif tool_name == "verify_visual_task":
        screenshot_path = tool_params.get("screenshot_path", "")
        task_description = tool_params.get("task_description", "")
        code_text = f'''
        await page.screenshot(path="{screenshot_path}")
        await readAttach_mcp("{screenshot_path}", "{test_func_name}")
'''
    elif tool_name == "evaluate_web_visual_task":
        screenshot_path = tool_params.get("screenshot_path", "")
        task_description = tool_params.get("task_description", "")
        code_text = f'''
        await page.screenshot(path="{screenshot_path}")
        await readAttach_mcp("{screenshot_path}", "{test_func_name}")
'''
    else:
        code_text = f'''
        pass
'''
    
    return code_text


def get_playwright_locator(strategy, value):
    if strategy == "css":
        return value
    elif strategy == "xpath":
        return f"xpath={value}"
    elif strategy == "id":
        return f"#{value}"
    elif strategy == "text":
        return f"text={value}"
    elif strategy == "role":
        return f"role={value}"
    else:
        return value


def extract_steps_from_cache(gen_code_id, gen_code_cache):
    dedupe_set = set()
    steps = []
    logger.info(f"Extracting cache size: {len(gen_code_cache)}")
    for item in gen_code_cache:
        if item.get("gen_code_id") != gen_code_id:
            continue
        
        step_text = item.get("step", "")
        key = (step_text.lower(), item.get("tool_name"))
        
        if key not in dedupe_set:
            dedupe_set.add(key)
            item["step_text_raw"] = step_text
            steps.append(item)
    
    logger.info(f"Extracted {len(steps)} steps")
    return steps


def gen_code_preview(session_manager, code_format: str = "mcp") -> dict:
    new_steps_code = []
    
    steps = extract_steps_from_cache(session_manager.gen_code_id, session_manager.gen_code_cache)
    logger.info(f"Processing {len(steps)} extracted steps with format: {code_format}")

    test_func_name = f"test_{session_manager.gen_code_id.replace('-', '_')[:30]}"
    
    for item in steps:
        item["test_func_name"] = test_func_name
        if code_format == "native":
            step_code = generate_native_playwright_definition(item)
        else:
            step_code = generate_step_definition(item)
        if step_code:
            new_steps_code.append(step_code)

    session_manager.proposed_changes = new_steps_code
    session_manager.new_steps_count = len(new_steps_code)
    session_manager.test_func_name = test_func_name
    session_manager.code_format = code_format
    
    if not new_steps_code:
        return {'diff_preview': 'No new code changes to apply', 'new_steps_code': []}
    
    max_show_size = 5
    new_steps_code_show = new_steps_code[:max_show_size]

    diff_preview = f"+++ New Code to Add ({len(new_steps_code)} new steps) +++\n"
    diff_preview += "".join(new_steps_code_show)
    if len(new_steps_code) > max_show_size:
        diff_preview += f"\n... and {len(new_steps_code) - max_show_size} more steps\n"
    
    return {'diff_preview': diff_preview, 'new_steps_code': new_steps_code}


def ensure_step_path_exists(step_file: str) -> bool:
    step_path = Path(step_file)
    try:
        parent_dir = step_path.parent
        if not parent_dir.exists():
            logger.info(f"Creating directory structure: {parent_dir}")
            parent_dir.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory structure for {step_path}: {str(e)}")
        return False


def read_step_files(step_path, max_depth=5, current_depth=0):
    existing_code = ""
    
    if current_depth > max_depth:
        logger.warning(f"Maximum recursion depth reached at {step_path}")
        return existing_code
    
    if not step_path.exists():
        logger.warning(f"Step path does not exist: {step_path}")
        return existing_code
        
    if step_path.is_dir():
        for py_file in step_path.glob("*.py"):
            try:
                logger.info(f"Reading step file: {py_file}")
                with open(py_file, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    if file_content:
                        existing_code += file_content + "\n\n"
            except Exception as e:
                logger.error(f"Error reading file {py_file}: {str(e)}")
        
        for subdir in step_path.iterdir():
            if subdir.is_dir():
                subdir_content = read_step_files(subdir, max_depth, current_depth + 1)
                if subdir_content:
                    existing_code += subdir_content + "\n\n"
    
    elif step_path.is_file() and step_path.suffix == '.py':
        try:
            with open(step_path, 'r', encoding='utf-8') as f:
                existing_code = f.read()
        except Exception as e:
            logger.error(f"Error reading file {step_path}: {str(e)}")
            
    return existing_code


def log_params(func, *args, **kwargs):
    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())
    tool_params = dict()
   
    args_no_name = []
    for i, arg in enumerate(args):
        if i < len(param_names):
            tool_params[param_names[i]] = arg
        else:
            args_no_name.append(repr(arg))
 
    for k, v in kwargs.items():
        tool_params[k] = v
    
    return tool_params


def record_calls(session_manager):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not session_manager.start_tool_execution(func.__name__):
                logger.warning(f"Tool execution blocked: {func.__name__} is already running")
                return json.dumps({
                    "status": "failed", 
                    "message": "Another tool is currently executing, please wait",
                    "error": "Tool execution blocked"
                })
            
            try:
                result = await func(*args, **kwargs)
                
                if isinstance(result, str):
                   json_result = json.loads(result)
                   if isinstance(json_result, str):
                       json_result = json.loads(json_result)
                else:
                    json_result = result

                if json_result.get("status") != "success":
                    return result  
                
                call_info = {}
                tool_params = log_params(func, *args, **kwargs)
                if tool_params.get('caller') == MCP_SERVER_INTERNAL_CALL:
                    logger.info(f"Internal call detected, no record: tool_name={func.__name__}, tool_params={tool_params}")
                    return result
                
                if session_manager.gen_code_id and (tool_params.get('step_raw', '') or tool_params.get('step', '')):
                    tool_params['caller'] = 'pytest-automation'
                    call_info['scenario'] = tool_params.pop('scenario', '')
                    step_raw = tool_params.pop('step_raw', '').strip()
                    step_ai = tool_params.pop('step', '').strip()
                    call_info['step'] = step_raw if step_raw else step_ai
                    call_info['gen_code_id'] = session_manager.gen_code_id
                    call_info['tool_name'] = func.__name__
                    call_info['tool_params'] = tool_params
                    session_manager.gen_code_cache.append(call_info)
                    logger.info(f"record_calls: call_info={call_info}")
 
                return result
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.error(f"Error record_calls: {repr(e)}")
                raise e
            finally:
                session_manager.finish_tool_execution(func.__name__)
               
        return wrapper
    return decorator

