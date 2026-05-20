# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from behave import *
import logging
from features.environment import call_tool_sync, get_tool_json

logger = logging.getLogger(__name__)


# ==================== 百度搜索功能测试 ====================

@given('我打开百度首页')
def step_impl(context):
    """导航到百度首页"""
    result = call_tool_sync(context, context.session.call_tool(
        name="browser_navigate",
        arguments={
            'caller': 'behave',
            'url': 'https://www.baidu.com'
        }
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"导航失败: {result_json.get('error')}"


@when('我在搜索框输入 "{text}"')
def step_impl(context, text):
    """在百度搜索框输入文本"""
    import time
    
    # 等待搜索框可见
    result = call_tool_sync(context, context.session.call_tool(
        name="wait_for_element",
        arguments={
            'caller': 'behave',
            'locator_value': 'input[name="wd"]',
            'locator_strategy': 'css',
            'timeout': 10000
        }
    ))
    
    # 点击搜索框使其获得焦点
    result = call_tool_sync(context, context.session.call_tool(
        name="click_element",
        arguments={
            'caller': 'behave',
            'locator_value': 'input[name="wd"]',
            'locator_strategy': 'css'
        }
    ))
    
    time.sleep(1)  # 等待动画完成
    
    result = call_tool_sync(context, context.session.call_tool(
        name="send_keys",
        arguments={
            'caller': 'behave',
            'locator_value': 'input[name="wd"]',
            'locator_strategy': 'css',
            'text': text
        }
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"输入失败: {result_json.get('error')}"


@when('我点击搜索按钮')
def step_impl(context):
    """点击百度搜索按钮"""
    result = call_tool_sync(context, context.session.call_tool(
        name="click_element",
        arguments={
            'caller': 'behave',
            'locator_value': 'input[type="submit"]',
            'locator_strategy': 'css'
        }
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"点击失败: {result_json.get('error')}"


@then('搜索结果页面应该包含 "{text}"')
def step_impl(context, text):
    """验证搜索结果页面包含指定文本"""
    import time
    time.sleep(2)  # 等待搜索结果加载
    
    result = call_tool_sync(context, context.session.call_tool(
        name="verify_text_on_page",
        arguments={
            'caller': 'behave',
            'text': text
        }
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"文本验证失败: {result_json.get('error')}"


@then('页面标题应该包含 "{expected_text}"')
def step_impl(context, expected_text):
    """验证页面标题包含指定文本"""
    result = call_tool_sync(context, context.session.call_tool(
        name="get_page_title",
        arguments={
            'caller': 'behave'
        }
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"获取标题失败: {result_json.get('error')}"
    
    title = result_json.get("data", {}).get("title", "")
    assert expected_text in title, \
        f"期望标题包含 '{expected_text}', 实际标题为 '{title}'"


@then('搜索按钮应该存在')
def step_impl(context):
    """验证搜索按钮元素存在"""
    result = call_tool_sync(context, context.session.call_tool(
        name="verify_element_exists",
        arguments={
            'caller': 'behave',
            'locator_value': 'input[type="submit"]',
            'locator_strategy': 'css'
        }
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"元素验证失败: {result_json.get('error')}"
