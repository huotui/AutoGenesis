
from behave import *
import logging
from features.environment import call_tool_sync, get_tool_json

# --- auto-generated step ---
@given('I navigate to https://www.bing.com')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(
        name="browser_navigate", 
        arguments={'caller': 'behave-automation',
            'page_source_file': '',
            'summary_only': False,
            'url': 'https://www.bing.com'}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

# --- auto-generated step ---
@step('I should see the Bing search box')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(
        name="verify_element_exists", 
        arguments={'caller': 'behave-automation',
            'locator_strategy': 'css',
            'locator_value': '#sb_form_q'}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 
