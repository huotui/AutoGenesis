---
name: autoGenesis-web-designer
description: Design comprehensive web test scenarios from requirements/docs/images/text using professional testing methodologies (boundary, positive, negative, edge cases). Generates BDD feature files and test commands, then invokes autoGenesis-web skill to execute tests. Trigger when user provides web requirements, screenshots, or feature descriptions and asks to generate test cases or test a web function.
---

# AutoGenesis Web Test Designer

Design professional web test scenarios from requirements documents, screenshots, or text descriptions, then automatically execute them using autoGenesis-web skill.

## Input

**Accepts any of the following:**
- **Requirements Document** - Text describing a web feature or functionality
- **Screenshots/Images** - Visual representation of a web page or UI component
- **Text Description** - Natural language description of what to test
- **URL + Feature Description** - Target web page and what needs testing

## Workflow

### Step 1: Analyze Requirements

Analyze the input using professional testing methodologies:

#### 1.1 Identify Test Dimensions

For each requirement, identify:
- **Functional Requirements** - What the feature should do
- **UI Elements** - Buttons, forms, inputs, dropdowns, etc.
- **User Interactions** - Click, type, select, hover, scroll
- **Expected Outcomes** - What should happen after actions
- **Error Conditions** - What happens when things go wrong

#### 1.2 Design Test Scenarios by Category

Apply these testing methodologies:

**Positive Tests (Happy Path)**:
- Normal user flow with valid inputs
- Expected behavior under standard conditions
- Success scenarios

**Negative Tests (Error Handling)**:
- Invalid inputs (empty, too long, wrong format)
- Missing required fields
- Unauthorized access attempts
- Network/timeout errors
- Unexpected user actions

**Boundary Tests**:
- Minimum/maximum values
- Edge cases (0, -1, MAX_INT, empty strings)
- Character limits
- Date boundaries
- File size limits

**Edge Cases**:
- Special characters (unicode, emoji, HTML tags, SQL injection attempts)
- Very long inputs
- Simultaneous actions
- Browser back/forward navigation
- Page refresh during operations
- Multiple tabs/windows

**State Tests**:
- Login/logout flows
- Session timeout
- Data persistence
- Form submission state
- Navigation state

### Step 2: Generate Feature Files

Create BDD feature files in Gherkin format:

```gherkin
Feature: [Feature Name]
  As a [user role]
  I want to [action]
  So that [benefit]

  @positive
  Scenario: [Positive scenario name]
    Given [precondition]
    When [action]
    Then [expected result]

  @negative
  Scenario: [Negative scenario name]
    Given [precondition]
    When [invalid action]
    Then [error message or validation]

  @boundary
  Scenario: [Boundary test scenario]
    Given [precondition]
    When [boundary action]
    Then [boundary validation]
```

### Step 3: Map Steps to MCP Tools

For each Given/When/Then step, map to appropriate MCP tools:

| Step Type | Common MCP Tools |
|-----------|------------------|
| **Navigation** | `browser_navigate`, `wait_for_element` |
| **Input** | `send_keys`, `click_element`, `select_option` |
| **Interaction** | `hover_element`, `scroll_page`, `press_key` |
| **Verification** | `verify_element_exists`, `verify_text_on_page`, `verify_checkbox_state`, `verify_element_value` |
| **AI Verification** | `verify_visual_task`, `evaluate_web_visual_task` |

### Step 4: Create Test Commands

Generate executable test commands:

```bash
# Run positive tests
cd behave-demo
uv run behave --tags=@positive

# Run negative tests
uv run behave --tags=@negative

# Run boundary tests
uv run behave --tags=@boundary

# Run all tests
uv run behave features/[feature_file].feature

# Run specific scenario
uv run behave --name "[Scenario Name]"
```

### Step 5: Invoke autoGenesis-web Skill

After generating the feature file and steps:

```
Use skill autoGenesis-web to execute scenario: [Scenario Name]
```

**Provide to autoGenesis-web:**
- The generated feature file content
- Scenario name to execute
- Any specific instructions or constraints

### Step 6: Review Results

After autoGenesis-web completes:
1. Review generated step code
2. Verify test coverage is comprehensive
3. Identify any missing test scenarios
4. Suggest additional test cases if needed

## Output

For each requirement, provide:

1. **Test Analysis Report** - Summary of test dimensions identified
2. **Feature File** - Complete BDD feature file with all scenarios
3. **Test Matrix** - Table showing requirement vs test coverage
4. **Execution Commands** - Ready-to-run test commands
5. **Step Definitions** - Generated via autoGenesis-web skill

## Example Workflow

### Input

User provides: "测试百度搜索功能，包括输入关键词搜索，验证搜索结果页面"

### Step 1: Analysis

**Test Dimensions Identified:**
- 搜索输入框
- 搜索按钮
- 搜索结果页面
- 空搜索、超长关键词、特殊字符
- 网络错误、超时

### Step 2: Generated Feature File

```gherkin
Feature: 百度搜索功能测试
  作为网站用户
  我想要使用百度搜索功能
  以便于快速找到需要的信息

  @positive
  Scenario: 正常搜索关键词
    Given 我打开百度首页
    When 我在搜索框输入 "AutoGenesis"
    And 我点击搜索按钮
    Then 搜索结果页面应该包含 "AutoGenesis"

  @negative
  Scenario: 空搜索关键词
    Given 我打开百度首页
    When 我点击搜索按钮
    Then 页面应该保持在百度首页或显示搜索建议

  @negative
  Scenario: 搜索特殊字符
    Given 我打开百度首页
    When 我在搜索框输入 "<script>alert('test')</script>"
    And 我点击搜索按钮
    Then 搜索结果页面不应该执行脚本

  @boundary
  Scenario: 搜索超长关键词
    Given 我打开百度首页
    When 我在搜索框输入 "[500字符的长字符串]"
    And 我点击搜索按钮
    Then 搜索结果页面应该正常显示或截断关键词

  @positive
  Scenario: 搜索后验证页面标题
    Given 我打开百度首页
    When 我在搜索框输入 "Microsoft"
    And 我点击搜索按钮
    Then 页面标题应该包含 "Microsoft"
```

### Step 3: Test Commands

```bash
# 运行所有百度搜索测试
cd behave-demo
uv run behave features/baidu_search.feature

# 只运行正向测试
uv run behave --tags=@positive

# 只运行反向测试
uv run behave --tags=@negative
```

### Step 4: Execute via autoGenesis-web

```
Use skill autoGenesis-web to execute scenario: 正常搜索关键词
```

## Best Practices

### Test Design Principles

1. **Coverage First** - Ensure every requirement has at least one positive and one negative test
2. **Independent Scenarios** - Each scenario should be self-contained
3. **Descriptive Names** - Scenario names should clearly describe what's being tested
4. **Tags for Organization** - Use @positive, @negative, @boundary, @smoke, @regression tags
5. **Reusable Steps** - Design Given/When/Then steps to be reusable across scenarios

### MCP Tool Selection

1. **Use `verify_visual_task`** - For complex UI layouts that are hard to verify with locators
2. **Use `evaluate_web_visual_task`** - When you need to analyze both visual and DOM state
3. **Use `verify_checkbox_state`** - For checkboxes, radio buttons, toggles
4. **Use `verify_element_value`** - For form inputs, dropdowns, textareas
5. **Use `hover_element`** - For dropdown menus, tooltips, hover effects
6. **Use `scroll_page`** - For long pages, infinite scroll, lazy loading

### Error Handling

1. **Wait for Elements** - Always wait for elements before interacting
2. **Alternative Locators** - Try CSS, XPath, ID, text strategies
3. **Retry Strategy** - If element not found, wait and retry
4. **Screenshot on Failure** - Capture state for debugging

## Configuration

Ensure the following are configured before running:

1. **Browser Config** - `playwright-mcp-server/conf/playwright_conf.json`
2. **MCP Server** - `.vscode/mcp.json` with playwright-mcp-server
3. **Dependencies** - `behave-demo/` directory with `uv sync` completed
4. **LLM Config** (Optional) - For AI-powered visual verification

## Skills Integration

This skill works in conjunction with:

- **autoGenesis-web** - Executes the generated scenarios
- **web-dev** - Can be used to create test web pages if needed

## Common Testing Patterns

### Login/Authentication Flow
```gherkin
@positive
Scenario: 正常登录
  Given 我导航到登录页面
  When 我输入用户名 "valid_user"
  And 我输入密码 "valid_password"
  And 我点击登录按钮
  Then 页面应该跳转到用户主页

@negative
Scenario: 错误密码登录
  Given 我导航到登录页面
  When 我输入用户名 "valid_user"
  And 我输入密码 "wrong_password"
  And 我点击登录按钮
  Then 页面应该显示错误提示

@boundary
Scenario: 空字段登录
  Given 我导航到登录页面
  When 我不输入用户名和密码
  And 我点击登录按钮
  Then 页面应该提示必填字段
```

### Form Submission
```gherkin
@positive
Scenario: 正常提交表单
  Given 我打开注册页面
  When 我填写所有必填字段
  And 我点击提交按钮
  Then 页面应该显示成功消息

@negative
Scenario: 必填字段缺失
  Given 我打开注册页面
  When 我只填写部分字段
  And 我点击提交按钮
  Then 页面应该提示缺失字段

@boundary
Scenario: 字段长度边界
  Given 我打开注册页面
  When 我输入最大长度的用户名
  And 我点击提交按钮
  Then 页面应该接受或提示超长
```

### Search Functionality
```gherkin
@positive
Scenario: 正常搜索
  Given 我打开搜索页面
  When 我输入有效关键词
  And 我执行搜索
  Then 搜索结果应该包含相关内容

@negative
Scenario: 空搜索
  Given 我打开搜索页面
  When 我不输入关键词
  And 我执行搜索
  Then 页面应该保持原样或显示提示

@boundary
Scenario: 特殊字符搜索
  Given 我打开搜索页面
  When 我输入特殊字符
  And 我执行搜索
  Then 页面应该正常处理或转义
```
