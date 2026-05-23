from behave import *
import logging
from features.environment import call_tool_sync, get_tool_json

logger = logging.getLogger(__name__)


@given('I navigate to "https://www.chiphell.com/forum.php"')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(
        name="browser_navigate", 
        arguments={'caller': 'behave-automation',
            'page_source_file': '',
            'summary_only': False,
            'url': 'https://www.chiphell.com/forum.php'}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

@step('I click the "相关讨论" topic link')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(
        name="click_element", 
        arguments={'caller': 'behave-automation',
            'locator_strategy': 'css',
            'locator_value': 'a:has-text("相关讨论")',
            'page_source_file': '',
            'summary_only': False}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

@step('I should see the topic content page')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(
        name="get_page_title", 
        arguments={'caller': 'behave-automation', 'page_source_file': '', 'summary_only': False}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'"
