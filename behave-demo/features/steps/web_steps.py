# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from behave import *
import logging
from features.environment import call_tool_sync, get_tool_json

logger = logging.getLogger(__name__)


@given('I navigate to "{url}"')
def step_navigate(context, url):
    result = call_tool_sync(context, context.session.call_tool(
        name="browser_navigate",
        arguments={
            'caller': 'behave',
            'url': url
        }
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Navigation failed: {result_json.get('error')}"


@when('I input "{text}" in the search box')
def step_input_search(context, text):
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
    assert result_json.get("status") == "success", f"Input failed: {result_json.get('error')}"


@when('I click the search button')
def step_click_search(context):
    result = call_tool_sync(context, context.session.call_tool(
        name="click_element",
        arguments={
            'caller': 'behave',
            'locator_value': 'input[type="submit"]',
            'locator_strategy': 'css'
        }
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Click failed: {result_json.get('error')}"


@when('I wait for the search results to load')
def step_wait_results(context):
    import time
    time.sleep(3)
    result = call_tool_sync(context, context.session.call_tool(
        name="wait_for_element",
        arguments={
            'caller': 'behave',
            'locator_value': '#content_left',
            'locator_strategy': 'css',
            'timeout': 10000
        }
    ))
    result_json = get_tool_json(result)
    if result_json.get("status") != "success":
        result = call_tool_sync(context, context.session.call_tool(
            name="wait_for_element",
            arguments={
                'caller': 'behave',
                'locator_value': '#container',
                'locator_strategy': 'css',
                'timeout': 10000
            }
        ))
        result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Wait failed: {result_json.get('error')}"


@when('I get the page title')
def step_get_title(context):
    result = call_tool_sync(context, context.session.call_tool(
        name="get_page_title",
        arguments={
            'caller': 'behave'
        }
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Get title failed: {result_json.get('error')}"
    context.page_title = result_json.get("data", {}).get("title", "")


@then('the page title should contain "{expected_text}"')
def step_verify_title(context, expected_text):
    assert expected_text in context.page_title, \
        f"Expected title to contain '{expected_text}', got '{context.page_title}'"


@then('I should see text "{text}"')
def step_verify_text(context, text):
    result = call_tool_sync(context, context.session.call_tool(
        name="verify_text_on_page",
        arguments={
            'caller': 'behave',
            'text': text
        }
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Text verification failed: {result_json.get('error')}"


@then('I should see the search input box')
def step_verify_search_input(context):
    result = call_tool_sync(context, context.session.call_tool(
        name="verify_element_exists",
        arguments={
            'caller': 'behave',
            'locator_value': 'input[name="wd"]',
            'locator_strategy': 'css'
        }
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Element verification failed: {result_json.get('error')}"


@then('I should see the page heading')
def step_verify_heading(context):
    result = call_tool_sync(context, context.session.call_tool(
        name="verify_element_exists",
        arguments={
            'caller': 'behave',
            'locator_value': 'h1',
            'locator_strategy': 'css'
        }
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Element verification failed: {result_json.get('error')}"


@then('I should see the bing search box')
def step_verify_bing_search_box(context):
    result = call_tool_sync(context, context.session.call_tool(
        name="verify_element_exists",
        arguments={
            'caller': 'behave',
            'locator_value': '#sb_form_q',
            'locator_strategy': 'css'
        }
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Bing search box verification failed: {result_json.get('error')}"
