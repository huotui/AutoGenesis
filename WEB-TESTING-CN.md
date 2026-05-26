# AutoGenesis Web 应用测试操作文档

> 📚 **AutoGenesis** 是一个基于模型上下文协议（MCP）的 AI 驱动自动化测试框架，本文档专注于 Web 应用测试功能。

---

## 📋 目录

1. [功能概述](#功能概述)
2. [环境准备](#环境准备)
3. [快速开始](#快速开始)
4. [配置浏览器](#配置浏览器)
5. [启动 MCP 服务器](#启动-mcp-服务器)
6. [配置 MCP 客户端](#配置-mcp-客户端)
7. [编写测试用例](#编写测试用例)
8. [生成测试代码](#生成测试代码)
9. [运行测试](#运行测试)
10. [重试配置策略](#重试配置策略)
11. [可用的 MCP 工具](#可用的-mcp-工具)
12. [BDD 测试流程详解](#bdd-测试流程详解)
13. [高级配置](#高级配置)
14. [常见问题排查](#常见问题排查)

---

## 功能概述

AutoGenesis Web 测试模块提供以下核心功能：

- 🤖 **AI 辅助测试生成** - 基于 MCP 协议，AI 自动生成测试脚本
- 🌐 **多浏览器支持** - Chromium、Firefox、WebKit
- 🎯 **BDD 格式支持** - 自动生成行为驱动开发（BDD）格式的测试代码
- 📸 **截图与分析** - 支持截图和 AI 截图分析功能
- 🔍 **高级元素定位** - 支持 CSS、XPath 等多种定位策略
- 🖱️ **丰富元素交互** - 支持点击、输入、悬停、滚动等操作
- 🔄 **异步架构** - 基于 asyncio 的高性能异步操作
- 🧠 **本地 LLM 支持** - 支持 Ollama、LM Studio 等本地大模型

---

## 环境准备

### 前置要求

- **Python 3.10 或更高版本**
- **uv 包管理器**（推荐，用于更快的依赖管理）
- **VS Code 或 Cursor** 编辑器

### 安装 uv

```powershell
# 安装 uv 以加速依赖管理
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或从 https://github.com/astral-sh/uv/releases/latest 下载
```

### 克隆项目

```powershell
git clone https://github.com/microsoft/AutoGenesis.git
cd AutoGenesis
```

---

## 快速开始

### 1. 安装依赖

```powershell
cd playwright-mcp-server
uv sync
```

**依赖包括：**
- `playwright` - Playwright Python 客户端
- `mcp` - 模型上下文协议 SDK
- `asyncio` - 异步编程支持
- 其他必要的工具库

### 2. 安装 Playwright 浏览器

```powershell
uv run playwright install
```

这会安装 Chromium、Firefox 和 WebKit 浏览器。

---

## 配置浏览器

### 创建配置文件

从模板创建本地配置文件：

```powershell
cp conf/playwright_conf.template.json conf/playwright_conf.json
```

### 编辑配置

打开 `conf/playwright_conf.json` 并配置浏览器设置：

```json
{
  "browser": {
    "browser_name": "chromium",
    "headless": false,
    "viewport": {
      "width": 1280,
      "height": 720
    },
    "timeout": 30000,
    "slow_mo": 500
  }
}
```

**配置字段说明：**

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `browser_name` | string | 浏览器类型 | `chromium`、`firefox`、`webkit` |
| `headless` | boolean | 是否使用无头模式 | `true`（无界面）、`false`（有界面） |
| `viewport.width` | number | 窗口宽度（像素） | `1280` |
| `viewport.height` | number | 窗口高度（像素） | `720` |
| `timeout` | number | 默认超时时间（毫秒） | `30000` |
| `slow_mo` | number | 减慢操作速度（毫秒） | `500`（用于调试） |

**浏览器类型选择：**
- `chromium` - Google Chrome / Microsoft Edge 内核
- `firefox` - Mozilla Firefox
- `webkit` - Safari 内核

---

## 启动 MCP 服务器

### SSE 模式（Server-Sent Events）

```powershell
cd playwright-mcp-server
uv run python simple_server.py --transport sse
```

服务器将在 `http://localhost:8000/sse` 启动。

### stdio 模式

```powershell
cd playwright-mcp-server
uv run python simple_server.py --transport stdio
```

stdio 模式通常由 VS Code 自动启动和管理，不需要手动运行。

---

## 配置 MCP 客户端

### VS Code 配置

在项目根目录创建或编辑 `.vscode/mcp.json`：

#### 方式 1：SSE 模式

```json
{
  "servers": {
    "auto-genesis-mcp-web": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

**注意：** 使用 SSE 模式需要先手动启动 MCP 服务器。

#### 方式 2：stdio 模式（推荐本地开发）

```json
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
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
        "LANG": "en_US.UTF-8",
        "LC_ALL": "en_US.UTF-8"
      }
    }
  }
}
```

**注意：** 请将路径替换为你的实际项目路径。

### Cursor 配置

#### 方式 1：SSE 模式

```json
{
  "mcpServers": {
    "auto-genesis-mcp-web": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

#### 方式 2：stdio 模式

```json
{
  "mcpServers": {
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
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
        "LANG": "en_US.UTF-8",
        "LC_ALL": "en_US.UTF-8"
      }
    }
  }
}
```

### 指定 Behave 测试的 MCP 服务器名称

运行 behave 测试时，测试框架会自动从 `.vscode/mcp.json` 中发现名称以 `auto-genesis` 开头的 MCP 服务器。

如果配置了多个 MCP 服务器，可以通过编辑 `behave-demo/features/environment.py` 指定确切的服务器名称：

```python
# 设置为 .vscode/mcp.json 中的特定服务器名称以使用它。
# 留空则自动发现（优先 stdio 模式，匹配 "auto-genesis" 前缀）。
AUTO_GENESIS_MCP_SERVER = 'auto-genesis-mcp-web'
```

---

## 编写测试用例

### Gherkin 语法基础

BDD 测试使用 Gherkin 语法编写，基本结构如下：

```gherkin
Feature: 功能名称
  作为某个角色
  我想要执行某些操作
  以便于实现某个业务目标

  Scenario: 场景名称
    Given 前置条件
    When 执行操作
    Then 验证结果
    And 额外验证
```

### 示例：Web 测试用例

创建 `behave-demo/features/web_test.feature`：

```gherkin
Feature: Web 浏览器测试

  Scenario: 验证百度标题
    Given 我导航到 "https://www.baidu.com"
    When 我获取页面标题
    Then 页面标题应包含 "百度"

  Scenario: 验证 example.com 元素
    Given 我导航到 "https://example.com"
    Then 我应该看到页面标题

  Scenario: 验证页面文本
    Given 我导航到 "https://example.com"
    Then 我应该看到文本 "Example Domain"
```

### 常用步骤关键词

| 关键词 | 说明 | 示例 |
|--------|------|------|
| `Given` | 前置条件 | `Given 我导航到 "https://example.com"` |
| `When` | 执行操作 | `When 我点击搜索按钮` |
| `Then` | 验证结果 | `Then 页面应包含搜索结果` |
| `And` | 额外步骤 | `And 我应该看到文本 "结果"` |

---

## 生成测试代码

### 使用 AI Skill 自动生成

项目提供了预配置的 skill 来简化测试执行流程。

#### 使用 autoGenesis-run skill

```
使用 skill autoGenesis-run 执行场景：测试 bing.com 网站
```

Skill 会自动完成：
1. 从 `.feature` 文件中定位场景
2. 解析所有场景步骤
3. 通过 MCP 工具调用执行每个步骤
4. 处理重试逻辑和错误恢复
5. 生成 BDD 测试代码
6. 将生成的代码保存到项目中

### 手动编写 Step Definitions

如果需要手动编写步骤定义，创建 `behave-demo/features/steps/web_steps.py`：

```python
from behave import given, when, then

@given('我导航到 "{url}"')
def step_impl(context, url):
    # 调用 MCP 工具导航到 URL
    result = context.session.call_tool(
        name="browser_navigate",
        arguments={'caller': 'behave', 'url': url}
    )
    # 处理结果...

@when('我获取页面标题')
def step_impl(context):
    # 调用 MCP 工具获取页面标题
    result = context.session.call_tool(
        name="get_page_title",
        arguments={'caller': 'behave'}
    )
    # 处理结果...

@then('页面标题应包含 "{text}"')
def step_impl(context, text):
    # 验证页面标题
    # ...
```

---

## 运行测试

### 安装 behave-demo 依赖

```powershell
cd behave-demo
uv sync
```

### 运行特定场景

```powershell
# 运行特定场景
uv run behave --name "验证百度标题"

# 运行整个 feature 文件
uv run behave features/web_test.feature

# 运行所有测试
uv run behave
```

### 常用运行选项

```powershell
# 生成 JSON 报告
uv run behave --format json -o reports/results.json

# 使用标签过滤
uv run behave --tags=@smoke

# 详细输出
uv run behave -v

# 不捕获输出（实时查看日志）
uv run behave --no-capture

# 停止在第一个失败
uv run behave --stop
```

### 重试配置策略

测试框架支持可配置的重试策略，用于处理不稳定的测试：

#### 重试模式

| 模式 | 说明 | 行为 |
|------|------|------|
| `step`（默认） | 单步重试 | 仅重试失败的 step，不会重新执行整个场景 |
| `scenario` | 场景重试 | 任何 step 失败时，从头开始重新执行整个场景 |

#### 通过环境变量配置

```powershell
# 设置重试模式：step 或 scenario
$env:RETRY_MODE = "step"

# 设置最大重试次数（默认：0 = 不重试）
$env:RETRY_MAX_ATTEMPTS = "3"
```

#### 使用示例

```powershell
# 单步重试，最多重试 3 次
$env:RETRY_MODE = "step"
$env:RETRY_MAX_ATTEMPTS = "3"
uv run behave

# 场景重试，最多重试 2 次（重新执行整个场景）
$env:RETRY_MODE = "scenario"
$env:RETRY_MAX_ATTEMPTS = "2"
uv run behave

# 不重试（默认行为）
uv run behave
```

#### 重试行为说明

- **单步重试模式**：当某个 step 失败时，仅重试该 step，最多重试配置的次数。场景中的其他 step 不会重新执行。
- **场景重试模式**：当任何 step 失败时，整个场景从第一个 step 开始重新执行，最多重试配置的次数。
- **默认设置**：默认不启用任何重试（`RETRY_MAX_ATTEMPTS=0`）

#### 重试输出示例

```
============================================================
STEP RETRY: 'I should see the borrow success message' failed (attempt 1/3)
Retrying step...
============================================================
```

### 查看测试结果

成功的测试输出示例：

```
Feature: Web 浏览器测试 # features/web_test.feature

  Scenario: 验证百度标题
    Given 我导航到 "https://www.baidu.com"
    When 我获取页面标题
    Then 页面标题应包含 "百度"

  Scenario: 验证 example.com 元素
    Given 我导航到 "https://example.com"
    Then 我应该看到页面标题

1 feature passed, 0 failed, 0 skipped
2 scenarios passed, 0 failed, 0 skipped
5 steps passed, 0 failed, 0 skipped
Took 0m5.077s
```

---

## 可用的 MCP 工具

### 浏览器导航

| 工具名称 | 说明 | 参数 |
|----------|------|------|
| `browser_navigate` | 导航到 URL | `url`（字符串） |
| `browser_close` | 关闭浏览器 | 无 |

### 元素交互

| 工具名称 | 说明 | 参数 |
|----------|------|------|
| `find_element` | 查找页面元素 | `locator_value`、`locator_strategy` |
| `click_element` | 点击元素 | `locator_value`、`locator_strategy` |
| `send_keys` | 在元素中输入文本 | `locator_value`、`text`、`locator_strategy` |
| `get_text` | 获取元素文本内容 | `locator_value`、`locator_strategy` |
| `select_option` | 选择下拉选项 | `locator_value`、`option_value`、`locator_strategy` |
| `press_key` | 按下键盘按键 | `key`（字符串） |
| `hover_element` | 鼠标悬停在元素上 | `locator_value`、`locator_strategy` |
| `scroll_page` | 滚动页面 | `direction`（up/down）、`amount`（像素） |
| `scroll_to_element` | 滚动到元素位置 | `locator_value`、`locator_strategy` |

### 页面信息

| 工具名称 | 说明 | 参数 |
|----------|------|------|
| `get_page_title` | 获取当前页面标题 | 无 |
| `get_page_url` | 获取当前页面 URL | 无 |
| `wait_for_element` | 等待元素出现 | `locator_value`、`locator_strategy`、`timeout` |

### 验证工具

| 工具名称 | 说明 | 参数 |
|----------|------|------|
| `verify_element_exists` | 验证元素存在 | `locator_value`、`locator_strategy` |
| `verify_element_not_exists` | 验证元素不存在 | `locator_value`、`locator_strategy` |
| `verify_element_attribute` | 验证元素属性值 | `locator_value`、`attribute`、`expected_value` |
| `verify_text_on_page` | 验证页面文本存在 | `text`（字符串） |

### 工具类

| 工具名称 | 说明 | 参数 |
|----------|------|------|
| `screenshot` | 截取截图 | `file_path`（可选） |
| `execute_javascript` | 执行 JavaScript 代码 | `script`（字符串） |

### 文件上传与下载

| 工具名称 | 说明 | 参数 |
|----------|------|------|
| `upload_file` | 上传单个或多个文件到文件输入元素 | `locator_value`、`file_paths`（列表）、`locator_strategy` |
| `wait_for_download` | 等待下载完成并返回下载文件信息 | `download_dir`（可选）、`timeout`（毫秒，默认30000） |
| `verify_download_exists` | 验证文件是否已下载成功 | `file_name`（可选）、`download_dir`（可选） |

**文件上传示例：**

```python
# 上传单个文件
upload_file(
    locator_value="#file-input",
    locator_strategy="css",
    file_paths=["/absolute/path/to/file.txt"]
)

# 上传多个文件
upload_file(
    locator_value="#file-input",
    locator_strategy="css",
    file_paths=["/path/to/file1.txt", "/path/to/file2.pdf"]
)
```

**文件下载示例：**

```python
# 等待下载完成（使用默认下载目录）
wait_for_download(
    timeout=30000
)

# 等待下载完成（指定下载目录）
wait_for_download(
    download_dir="./downloads",
    timeout=30000
)

# 验证特定文件已下载
verify_download_exists(
    file_name="downloaded_file.pdf",
    download_dir="./downloads"
)

# 验证下载目录中是否有任何文件
verify_download_exists(
    download_dir="./downloads"
)
```

**配置文件设置：**

在 `conf/playwright_conf.json` 中可以配置下载目录：

```json
{
  "browser": {
    "browser_name": "chromium",
    "headless": false,
    "download_dir": "./downloads"
  }
}
```

### 代码生成工具

| 工具名称 | 说明 | 参数 |
|----------|------|------|
| `before_gen_code` | 初始化代码生成会话 | 无 |
| `preview_code_changes` | 预览生成的代码变更 | 无 |
| `confirm_code_changes` | 确认并应用代码变更 | 无 |

---

## BDD 测试流程详解

### 什么是 BDD？

行为驱动开发（BDD）是一种软件开发流程，通过使用自然语言描述系统行为来促进团队协作。

### 完整测试流程

#### 1. 编写 Feature 文件

使用 Gherkin 语法描述测试场景：

```gherkin
Feature: 百度搜索功能

  Scenario: 搜索关键词
    Given 我导航到 "https://www.baidu.com"
    When 我在搜索框输入 "AutoGenesis"
    And 我点击搜索按钮
    Then 搜索结果应包含 "AutoGenesis"
```

#### 2. 配置 MCP 服务器

在 `.vscode/mcp.json` 中配置：

```json
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

#### 3. 生成 Step Definitions

AI 会自动生成步骤定义代码，或手动创建 `features/steps/web_steps.py`。

#### 4. 运行测试

```powershell
cd behave-demo
uv run behave features/baidu_search.feature
```

#### 5. 查看结果

检查测试执行结果和报告。

### 元素定位策略

Playwright 支持多种元素定位策略：

| 策略 | 说明 | 示例 |
|------|------|------|
| `css` | CSS 选择器 | `input[name="wd"]` |
| `xpath` | XPath 表达式 | `//input[@name="wd"]` |
| `id` | 元素 ID | `search-box` |
| `text` | 文本内容 | `text=点击这里` |

**示例：**

```python
# CSS 选择器
click_element(locator_value="input[name='wd']", locator_strategy="css")

# XPath
click_element(locator_value="//input[@name='wd']", locator_strategy="xpath")

# ID
click_element(locator_value="search-box", locator_strategy="id")
```

---

## 高级配置

### 本地 LLM 集成（可选）

#### 配置本地 LLM（如 Ollama、LM Studio）

设置环境变量以集成本地 LLM：

```powershell
$env:LOCAL_LM_ENDPOINT = "http://localhost:11434"
$env:LOCAL_LM_MODEL_NAME = "qwen2.5:7b"
$env:LOCAL_LM_API_KEY = "your-api-key"  # 可选
```

或在项目根目录创建 `.env` 文件：

```bash
LOCAL_LM_ENDPOINT=http://localhost:11434
LOCAL_LM_MODEL_NAME=qwen2.5:7b
LOCAL_LM_API_KEY=your-api-key
```

**配置项说明：**
- `LOCAL_LM_ENDPOINT` - 本地 LLM 服务端点地址（默认: http://localhost:11434）
- `LOCAL_LM_MODEL_NAME` - 使用的模型 ID/名称（例如: qwen2.5:7b, qwen2.5-vl:7b, llava:7b）
- `LOCAL_LM_API_KEY` - 本地 LLM API Key（可选，部分服务需要）

**支持的本地 LLM 服务：**

| 服务 | 默认端口 | 说明 |
|------|----------|------|
| **Ollama** | 11434 | 最流行的本地 LLM 服务 |
| **LM Studio** | 1234 | 图形界面，易于使用 |
| **FastChat** | 8000 | 支持多模型 |
| **vLLM** | 8000 | 高性能推理服务 |
| **LocalAI** | 8080 | 完全兼容 OpenAI API |

**推荐用于视觉任务的模型：**
- `qwen2.5-vl:7b` - 支持中文和图像分析
- `llava:7b` - 视觉语言模型
- `qwen2.5:7b` - 良好的中文支持（仅文本）

**测试本地 LLM 连接：**

```powershell
# 在 playwright-mcp-server 目录下运行
uv run python -c "
from llm.chat import LLMClient
client = LLMClient()
print(f'端点: {client.local_lm_endpoint}')
print(f'本地 LLM 可用: {client.local_copilot_available()}')
"
```

#### 配置 Azure OpenAI

设置环境变量以集成 Azure OpenAI：

```powershell
$env:AZURE_OPENAI_ENDPOINT = "your-endpoint"
$env:AZURE_OPENAI_API_KEY = "your-api-key"
$env:AZURE_OPENAI_DEPLOYMENT = "your-deployment-name"
```

然后在 `llm/chat.py` 中配置 Azure OpenAI 凭据以启用截图分析功能。

**注意：** 系统会优先使用 Azure OpenAI（如果已配置），在 Azure 不可用时自动回退到本地 LLM。

### 无头模式

对于 CI/CD 流水线或服务器环境，在配置文件中启用无头模式：

编辑 `conf/playwright_conf.json`：

```json
{
  "browser": {
    "browser_name": "chromium",
    "headless": true,
    "viewport": {
      "width": 1280,
      "height": 720
    },
    "timeout": 30000
  }
}
```

### 多浏览器测试

创建不同的配置文件来测试不同浏览器：

**Chromium 配置：**

```json
{
  "browser": {
    "browser_name": "chromium",
    "headless": false
  }
}
```

**Firefox 配置：**

```json
{
  "browser": {
    "browser_name": "firefox",
    "headless": false
  }
}
```

**WebKit 配置：**

```json
{
  "browser": {
    "browser_name": "webkit",
    "headless": false
  }
}
```

### 热重载配置

Playwright MCP 服务器支持配置文件热重载。修改 `conf/playwright_conf.json` 后，服务器会自动重新加载配置，无需重启。

---

## 常见问题排查

### MCP 服务器无法启动

**检查 Python 版本和依赖：**

```powershell
python --version
uv pip list
```

**重新同步依赖：**

```powershell
cd playwright-mcp-server
uv sync
```

确保 Python 版本为 3.10 或更高。

**查看日志文件：**

```powershell
cat logs/mcp_server.log
```

### Playwright 浏览器未安装

安装 Playwright 浏览器：

```powershell
uv run playwright install
```

### 找不到元素

**常见问题：**

1. **元素尚未加载** - 增加超时时间或使用 `wait_for_element`
2. **定位器不正确** - 检查 CSS/XPath 表达式
3. **元素在 iframe 中** - 需要先切换到 iframe
4. **元素被遮挡** - 使用 JavaScript 点击

**解决方案：**

```python
# 等待元素出现
wait_for_element(locator_value="input[name='wd']", locator_strategy="css", timeout=10000)

# 使用更具体的定位器
click_element(locator_value="#search-form input[name='wd']", locator_strategy="css")
```

### 元素不可交互

某些元素可能需要先点击或悬停才能交互：

```python
# 先点击父元素
click_element(locator_value="parent-element", locator_strategy="css")

# 然后输入文本
send_keys(locator_value="input[name='wd']", text="搜索内容", locator_strategy="css")
```

### 权限问题

- 确保浏览器有权限启动
- 某些网站可能需要登录或 Cookie

### AI 客户端无法识别 MCP 工具

- 重启 VS Code 或 Cursor
- 检查 MCP 配置文件路径是否正确
- 确认 MCP 服务器已成功启动
- 验证 Python 路径配置

### 生成的代码无法运行

以详细模式运行测试查看日志：

```powershell
uv run behave -v
```

检查：
1. 浏览器配置文件是否正确
2. 浏览器是否正常启动
3. MCP 服务器是否正常运行
4. 网络连接是否正常

### 端口占用问题

如果启动服务时提示端口被占用，可以关闭占用端口的程序：

```powershell
# 查找占用端口的进程
netstat -ano | findstr :8000

# 关闭进程（替换 PID 为实际进程 ID）
taskkill /PID <PID> /F
```

### 超时问题

增加超时时间：

**在配置文件中：**

```json
{
  "browser": {
    "timeout": 60000
  }
}
```

**在代码中：**

```python
wait_for_element(locator_value="selector", timeout=30000)
```

---

## 项目结构

```
playwright-mcp-server/
├── simple_server.py       # MCP 服务器主程序
├── playwright_session.py  # Playwright 会话管理器
├── pyproject.toml         # uv/项目配置
├── requirements.txt       # 依赖列表
├── conf/                  # 配置目录
│   ├── playwright_conf.json        # 浏览器配置
│   └── playwright_conf.template.json  # 配置模板
├── tools/                 # 工具模块
│   ├── playwright_tool.py # Playwright 自动化工具
│   ├── gen_code_tool.py   # 代码生成工具
│   └── verify_tools.py    # 验证工具
├── llm/                   # LLM 集成
│   ├── prompt.py          # LLM 提示词模板
│   └── chat.py            # LLM 聊天接口
├── utils/                 # 工具函数
├── logs/                  # 日志目录
└── WEB-README.md          # 文档（本文件）
```

---

## 示例测试用例

### 示例 1：验证页面标题

```gherkin
Feature: 页面标题验证

  Scenario: 验证百度标题
    Given 我导航到 "https://www.baidu.com"
    When 我获取页面标题
    Then 页面标题应包含 "百度"
```

### 示例 2：验证元素存在

```gherkin
Feature: 元素存在验证

  Scenario: 验证 example.com 有标题
    Given 我导航到 "https://example.com"
    Then 我应该看到页面标题
```

### 示例 3：验证页面文本

```gherkin
Feature: 页面文本验证

  Scenario: 验证 example.com 文本
    Given 我导航到 "https://example.com"
    Then 我应该看到文本 "Example Domain"
```

---

## 贡献指南

本项目欢迎贡献和建议。详情请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 联系方式

如有疑问或建议，请联系：autogenesis@microsoft.com

---

## 许可证

请参阅 [LICENSE](LICENSE) 了解许可证信息。
