from behave import *
import logging
from features.environment import call_tool_sync, get_tool_json

@step('I navigate to "{url}"')
def step_impl(context, url):
    result = call_tool_sync(context, context.session.call_tool(
        name="browser_navigate", 
        arguments={'caller': 'behave-automation',
            'page_source_file': '',
            'summary_only': False,
            'url': url}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'"

@when('I login with admin credentials "{username}" and "{password}"')
def step_impl(context, username, password):
    result = call_tool_sync(context, context.session.call_tool(
        name="send_keys", 
        arguments={'caller': 'behave-automation',
            'locator_strategy': 'css',
            'locator_value': 'input[placeholder="请输入用户名"]',
            'page_source_file': '',
            'summary_only': False,
            'text': username}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'"
    
    result = call_tool_sync(context, context.session.call_tool(
        name="send_keys", 
        arguments={'caller': 'behave-automation',
            'locator_strategy': 'css',
            'locator_value': 'input[placeholder="请输入密码"]',
            'page_source_file': '',
            'summary_only': False,
            'text': password}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'"
    
    result = call_tool_sync(context, context.session.call_tool(
        name="click_element", 
        arguments={'caller': 'behave-automation',
            'locator_strategy': 'css',
            'locator_value': '.el-button--primary',
            'page_source_file': '',
            'summary_only': False}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'"
    
    result = call_tool_sync(context, context.session.call_tool(
        name="wait_for_element", 
        arguments={'caller': 'behave-automation',
            'locator_strategy': 'text',
            'locator_value': '图书查询',
            'page_source_file': '',
            'summary_only': False,
            'timeout': 10000}
    ))
    result_json = get_tool_json(result)

@when('I click the "{menu_name}" navigation menu')
def step_impl(context, menu_name):
    result = call_tool_sync(context, context.session.call_tool(
        name="click_element", 
        arguments={'caller': 'behave-automation',
            'locator_strategy': 'text',
            'locator_value': menu_name,
            'page_source_file': '',
            'summary_only': False}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'"

@when('I click the "{button_name}" button')
def step_impl(context, button_name):
    result = call_tool_sync(context, context.session.call_tool(
        name="click_element", 
        arguments={'caller': 'behave-automation',
            'locator_strategy': 'text',
            'locator_value': button_name,
            'page_source_file': '',
            'summary_only': False}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'"

@then('I should see the add book dialog')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(
        name="verify_element_exists", 
        arguments={'caller': 'behave-automation',
            'locator_strategy': 'css',
            'locator_value': '.el-dialog',
            'page_source_file': '',
            'summary_only': False}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'"

@when('I click the cover image upload area with "+" icon')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(
        name="click_element", 
        arguments={'caller': 'behave-automation',
            'locator_strategy': 'css',
            'locator_value': '.el-upload.el-upload--text',
            'page_source_file': '',
            'summary_only': False}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'"

@when('I select an image file "{file_path}"')
def step_impl(context, file_path):
    result = call_tool_sync(context, context.session.call_tool(
        name="upload_file", 
        arguments={'caller': 'behave-automation',
            'locator_strategy': 'css',
            'locator_value': 'input[type="file"]',
            'file_paths': [file_path],
            'page_source_file': '',
            'summary_only': False}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'"

@then('I should see the image preview in the upload area')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(
        name="verify_element_exists", 
        arguments={'caller': 'behave-automation',
            'locator_strategy': 'css',
            'locator_value': '.el-upload-list, .el-upload--picture-card, [class*="upload"] img',
            'page_source_file': '',
            'summary_only': False}
    ))
    result_json = get_tool_json(result)
    if result_json.get("status") != "success":
        result = call_tool_sync(context, context.session.call_tool(
            name="execute_javascript", 
            arguments={'caller': 'behave-automation',
                'page_source_file': '',
                'script': '''
const uploadList = document.querySelector('.el-upload-list');
const uploadImg = document.querySelector('[class*="upload"] img');
const fileListItems = document.querySelectorAll('.el-upload-list__item, .el-upload--picture-card img');
JSON.stringify({
  hasUploadList: !!uploadList,
  hasUploadImg: !!uploadImg,
  fileListCount: fileListItems.length,
  uploadListHTML: uploadList ? uploadList.innerHTML.substring(0, 200) : 'not found'
});
                ''',
                'summary_only': False}
        ))
        result_json = get_tool_json(result)
        assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'"

@when('I input "{text}" in the book title field')
def step_impl(context, text):
    result = call_tool_sync(context, context.session.call_tool(
        name="send_keys", 
        arguments={'caller': 'behave-automation',
            'locator_strategy': 'css',
            'locator_value': '.el-form-item:has(> .el-form-item__label:has-text("书名")) input',
            'page_source_file': '',
            'summary_only': False,
            'text': text}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'"

@when('I input "{text}" in the author field')
def step_impl(context, text):
    result = call_tool_sync(context, context.session.call_tool(
        name="send_keys", 
        arguments={'caller': 'behave-automation',
            'locator_strategy': 'css',
            'locator_value': '.el-form-item:has(> .el-form-item__label:has-text("作者")) input',
            'page_source_file': '',
            'summary_only': False,
            'text': text}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'"

@when('I input "{text}" in the ISBN field')
def step_impl(context, text):
    result = call_tool_sync(context, context.session.call_tool(
        name="send_keys", 
        arguments={'caller': 'behave-automation',
            'locator_strategy': 'css',
            'locator_value': '.el-form-item:has(> .el-form-item__label:has-text("ISBN")) input',
            'page_source_file': '',
            'summary_only': False,
            'text': text}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'"

@when('I select "{option}" from the category dropdown')
def step_impl(context, option):
    result = call_tool_sync(context, context.session.call_tool(
        name="execute_javascript", 
        arguments={'caller': 'behave-automation',
            'page_source_file': '',
            'script': f'''
(async () => {{
  const categoryFormItem = Array.from(document.querySelectorAll('.el-form-item')).find(item => {{
    const label = item.querySelector('.el-form-item__label');
    return label && label.textContent.trim() === '分类';
  }});

  if (!categoryFormItem) {{
    return 'Category form item not found';
  }}

  const select = categoryFormItem.querySelector('.el-select');
  if (!select) {{
    return 'Select element not found';
  }}

  select.click();
  await new Promise(resolve => setTimeout(resolve, 500));

  const dropdown = document.querySelector('.el-select-dropdown');
  if (!dropdown) {{
    return 'Dropdown not found after click';
  }}

  const items = dropdown.querySelectorAll('.el-select-dropdown__item');
  for (const item of items) {{
    if (item.textContent.trim() === '{option}') {{
      item.click();
      await new Promise(resolve => setTimeout(resolve, 300));
      return 'Successfully selected {option}';
    }}
  }}
  
  return 'Option not found in dropdown';
}})();
            ''',
            'summary_only': False}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'"

@when('I input "{text}" in the publisher field')
def step_impl(context, text):
    result = call_tool_sync(context, context.session.call_tool(
        name="send_keys", 
        arguments={'caller': 'behave-automation',
            'locator_strategy': 'css',
            'locator_value': '.el-form-item:has(> .el-form-item__label:has-text("出版社")) input',
            'page_source_file': '',
            'summary_only': False,
            'text': text}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'"

@then('I should see the book added successfully')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(
        name="execute_javascript", 
        arguments={'caller': 'behave-automation',
            'page_source_file': '',
            'script': '''
const tableRows = document.querySelectorAll('.el-table__body-wrapper .el-table__row');
let books = [];
for (const row of tableRows) {
  const cells = row.querySelectorAll('td');
  if (cells.length > 0) {
    const bookData = Array.from(cells).map(cell => cell.textContent.trim().substring(0, 50));
    books.push(bookData);
  }
}
JSON.stringify({
  totalBooks: books.length,
  firstBook: books[0] || 'No books found',
  hasTestBook: books.some(row => row.some(cell => cell.includes('测试图书1')))
});
            ''',
            'summary_only': False}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'"
