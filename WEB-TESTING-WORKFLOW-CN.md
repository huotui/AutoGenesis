# AutoGenesis Web 测试 - 手动 vs AI 编写分工说明

> 本文档通过实际操作演示，说明在 Web 自动化测试中，哪些部分需要人工编写，哪些可以由 AI 自动生成。

---

## 📊 总览：分工比例

| 部分 | 编写方式 | 占比 | 说明 |
|------|----------|------|------|
| Feature 文件（测试场景） | **手动编写** | 20% | 需要理解业务需求 |
| Step Definitions（步骤定义） | **AI 生成** | 50% | 模式化代码，可自动生成 |
| 配置文件 | **手动编写** | 10% | 环境配置 |
| 调试和优化 | **人工+AI** | 20% | 协作完成 |

---

## 📝 第一部分：需要手动编写的内容

### 1. Feature 文件（测试场景描述）

**为什么需要手动编写？**
- 需要理解业务需求和用户场景
- 需要定义测试目标和验收标准
- 需要使用自然语言描述测试步骤

**示例：**

```gherkin
# 文件名：features/baidu_search.feature
# 这部分需要人工编写，因为需要理解业务需求

Feature: 百度搜索功能测试
  作为网站用户
  我想要使用百度搜索功能
  以便于快速找到需要的信息

  @smoke
  Scenario: 搜索关键词并验证结果
    Given 我打开百度首页
    When 我在搜索框输入 "AutoGenesis"
    And 我点击搜索按钮
    Then 搜索结果页面应该包含 "AutoGenesis"

  @regression
  Scenario: 验证百度首页元素
    Given 我打开百度首页
    Then 页面标题应该包含 "百度"
    And 搜索按钮应该存在
```

**人工需要决定的内容：**
- ✅ 测试什么功能？（百度搜索）
- ✅ 测试场景是什么？（搜索关键词、验证元素）
- ✅ 预期结果是什么？（搜索结果包含关键词）
- ✅ 使用什么标签？（@smoke、@regression）

### 2. 配置文件

**为什么需要手动编写？**
- 环境配置因项目而异
- 需要指定服务器路径和连接方式

**示例：**

```json
// 文件名：.vscode/mcp.json
// 这部分需要人工配置，因为路径因环境而异
{
  "servers": {
    "auto-genesis-mcp-web": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "d:\\workspace\\trae\\AutoGenesis\\playwright-mcp-server",
        "python",
        "d:\\workspace\\trae\\AutoGenesis\\playwright-mcp-server\\simple_server.py",
        "--transport",
        "stdio"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

```json
// 文件名：playwright-mcp-server/conf/playwright_conf.json
// 这部分需要人工配置，因为浏览器设置因需求而异
{
  "browser": {
    "browser_name": "chromium",
    "headless": false,
    "viewport": {
      "width": 1280,
      "height": 720
    },
    "timeout": 30000
  }
}
```

---

## 🤖 第二部分：可以 AI 生成的内容

### 1. Step Definitions（步骤定义代码）

**为什么可以 AI 生成？**
- 模式化的代码结构
- 每个 Gherkin 步骤对应一个函数
- 函数内部调用 MCP 工具，结构固定

**AI 生成的示例：**

```python
# 文件名：features/steps/baidu_steps.py
# 这部分可以由 AI 自动生成

from behave import *
import logging
from features.environment import call_tool_sync, get_tool_json

logger = logging.getLogger(__name__)


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
```

### 2. AI 如何生成 Step Definitions？

**生成规则：**

| Gherkin 步骤 | 生成的函数装饰器 | 调用的 MCP 工具 |
|--------------|------------------|-----------------|
| `Given 我打开百度首页` | `@given('我打开百度首页')` | `browser_navigate` |
| `When 我在搜索框输入 "{text}"` | `@when('我在搜索框输入 "{text}"')` | `send_keys` |
| `Then 页面标题应该包含 "{text}"` | `@then('页面标题应该包含 "{expected_text}"')` | `get_page_title` |

**生成逻辑：**
1. 解析 Feature 文件中的每个步骤
2. 根据步骤关键词（Given/When/Then）生成对应的装饰器
3. 根据步骤语义选择对应的 MCP 工具
4. 生成函数体，包括参数传递和结果验证

---

## 🔄 第三部分：人工 + AI 协作的内容

### 1. 调试和优化

**场景：** 百度搜索框元素不可见，需要特殊处理

**AI 生成的初始代码：**

```python
@when('我在搜索框输入 "{text}"')
def step_impl(context, text):
    """在百度搜索框输入文本"""
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
```

**问题：** 百度搜索框默认不可见，直接输入会超时

**人工分析 + AI 优化后的代码：**

```python
@when('我在搜索框输入 "{text}"')
def step_impl(context, text):
    """在百度搜索框输入文本"""
    import time
    
    # 人工发现：需要等待元素可见
    result = call_tool_sync(context, context.session.call_tool(
        name="wait_for_element",
        arguments={
            'caller': 'behave',
            'locator_value': 'input[name="wd"]',
            'locator_strategy': 'css',
            'timeout': 10000
        }
    ))
    
    # 人工发现：需要点击使元素获得焦点
    result = call_tool_sync(context, context.session.call_tool(
        name="click_element",
        arguments={
            'caller': 'behave',
            'locator_value': 'input[name="wd"]',
            'locator_strategy': 'css'
        }
    ))
    
    time.sleep(1)  # 等待动画完成
    
    # AI 生成：调用 send_keys 工具
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
```

### 2. 元素定位器选择

**人工需要决定：**
- 使用什么定位策略？（CSS、XPath、ID）
- 元素的特征是什么？

**AI 可以生成：**
- 根据定位策略生成正确的调用代码
- 处理参数传递和结果验证

---

## 📋 完整工作流程

### 步骤 1：人工编写 Feature 文件

```gherkin
# 人工编写：描述测试场景
Feature: 百度搜索功能测试
  Scenario: 搜索关键词并验证结果
    Given 我打开百度首页
    When 我在搜索框输入 "AutoGenesis"
    And 我点击搜索按钮
    Then 搜索结果页面应该包含 "AutoGenesis"
```

### 步骤 2：AI 生成 Step Definitions

```
# 使用 AI 命令
使用 skill autoGenesis-run 执行场景：搜索关键词并验证结果
```

AI 会自动生成 `baidu_steps.py` 文件。

### 步骤 3：人工调试和优化

如果测试失败，人工分析错误原因，AI 协助修复代码。

### 步骤 4：运行测试

```powershell
cd behave-demo
uv run behave features/baidu_search.feature
```

---

## 🎯 总结：分工建议

### ✅ 必须由人工完成的任务

1. **编写 Feature 文件** - 理解业务需求，定义测试场景
2. **配置环境** - 设置服务器路径、浏览器配置
3. **选择元素定位器** - 分析页面结构，选择合适的定位策略
4. **审查生成的代码** - 确保代码符合预期

### 🤖 可以 AI 完成的任务

1. **生成 Step Definitions** - 根据 Feature 文件自动生成步骤定义代码
2. **生成工具调用代码** - 根据步骤语义选择对应的 MCP 工具
3. **生成错误处理代码** - 添加 try-catch 和断言
4. **生成日志代码** - 添加日志记录

### 🔄 人工 + AI 协作的任务

1. **调试失败的测试** - 人工分析原因，AI 生成修复代码
2. **优化元素交互** - 人工发现特殊行为，AI 实现解决方案
3. **添加等待逻辑** - 人工判断需要等待，AI 生成等待代码

---

## 💡 最佳实践建议

1. **先写 Feature 文件** - 用自然语言描述测试场景
2. **让 AI 生成代码** - 使用 skill 自动生成 Step Definitions
3. **运行测试验证** - 检查生成的代码是否工作
4. **调试和优化** - 根据错误信息人工调整
5. **复用已有代码** - 相似的步骤可以复用已有的 Step Definitions

---

## 📚 参考文件

- Feature 文件示例：`behave-demo/features/baidu_search.feature`
- Step Definitions 示例：`behave-demo/features/steps/baidu_steps.py`
- 环境配置：`.vscode/mcp.json`
- 浏览器配置：`playwright-mcp-server/conf/playwright_conf.json`
