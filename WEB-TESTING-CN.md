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
10. [可用的 MCP 工具](#可用的-mcp-工具)
11. [Pytest 测试流程详解](#pytest-测试流程详解)
12. [高级配置](#高级配置)
13. [常见问题排查](#常见问题排查)

---

## 功能概述

AutoGenesis Web 测试模块提供以下核心功能：

- 🤖 **AI 辅助测试生成** - 基于 MCP 协议，AI 自动生成测试脚本
- 🌐 **多浏览器支持** - Chromium、Firefox、WebKit
- 🎯 **Pytest 格式支持** - 自动生成 pytest 格式的测试代码
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

---

## 编写测试用例

### Pytest 测试用例格式

测试用例使用 pytest 格式编写，基本结构如下：

```python
import allure
from common.attach import readAttach
from playwright.sync_api import Page


@allure.epic("模块名称")
@allure.title("测试场景标题")
def test_scenario_name(page: Page):
    # 测试步骤
    page.goto("https://example.com")
    page.locator("#selector").click()
    page.locator("#selector").fill("text")
    # 截图并附加到 Allure 报告
    readAttach(page, "./log/screenshot/", "test_scenario_name")
```

### 示例：Web 测试用例

创建 `PPA-UI-Automation-master/testcase/test_web.py`：

```python
import allure
from common.attach import readAttach
from playwright.sync_api import Page


@allure.epic("Web 浏览器测试")
@allure.title("验证百度标题")
def test_baidu_title(page: Page):
    page.goto("https://www.baidu.com/")
    page.locator("#kw").click()
    page.locator("#kw").fill("playwright")
    page.get_by_role("button", name="百度一下").click()
    readAttach(page, "./log/screenshot/", "test_baidu_title")
```

### 常用页面操作

| 操作 | 方法 | 示例 |
|------|------|------|
| 导航到 URL | `page.goto(url)` | `page.goto("https://example.com")` |
| 点击元素 | `page.locator(selector).click()` | `page.locator("#button").click()` |
| 输入文本 | `page.locator(selector).fill(text)` | `page.locator("#input").fill("text")` |
| 获取文本 | `page.locator(selector).text_content()` | `page.locator("#title").text_content()` |
| 等待元素 | `page.wait_for_selector(selector)` | `page.wait_for_selector("#element")` |
| 截图 | `page.screenshot(path=path)` | `page.screenshot(path="screenshot.png")` |

---

## 生成测试代码

### 使用 AI Skill 自动生成

项目提供了预配置的 skill 来简化测试执行流程。

#### 使用 autoGenesis-web skill

```
使用 skill autoGenesis-web 执行场景：测试 bing.com 网站
```

Skill 会自动完成：
1. 从 `.feature` 文件中定位场景
2. 解析所有场景步骤
3. 通过 MCP 工具调用执行每个步骤
4. 处理重试逻辑和错误恢复
5. 生成 pytest 测试代码
6. 将生成的代码保存到 `PPA-UI-Automation-master/testcase/` 目录中

### 手动编写测试用例

如果需要手动编写测试用例，创建 `PPA-UI-Automation-master/testcase/test_web.py`：

```python
import allure
from common.attach import readAttach
from playwright.sync_api import Page


@allure.epic("Web 测试")
@allure.title("导航到百度")
def test_navigate_to_baidu(page: Page):
    page.goto("https://www.baidu.com")
    readAttach(page, "./log/screenshot/", "test_navigate_to_baidu")
```

---

## 运行测试

### 安装依赖

```powershell
cd PPA-UI-Automation-master
pip install playwright pytest allure-pytest
playwright install
```

### 运行特定测试

```powershell
# 运行特定测试文件
pytest testcase/test_采购.py -vs

# 运行特定测试函数
pytest testcase/test_采购.py::test_playwright -vs

# 运行所有测试
pytest -vs --alluredir=./reports/tmp --clean-alluredir
```

### 常用运行选项

```powershell
# 生成 Allure 报告
pytest -vs --alluredir=./reports/tmp --clean-alluredir

# 使用标记过滤
pytest -vs -m smoke

# 详细输出
pytest -v

# 生成 HTML 报告并启动服务
python run.py
```

### 查看测试结果

成功的测试输出示例：

```
==================================== test session starts ====================================
testcase/test_采购.py::test_playwright PASSED

================================== 1 passed in 5.07s =========================================
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

### 代码生成工具

| 工具名称 | 说明 | 参数 |
|----------|------|------|
| `before_gen_code` | 初始化代码生成会话 | 无 |
| `preview_code_changes` | 预览生成的代码变更 | 无 |
| `confirm_code_changes` | 确认并应用代码变更 | 无 |

---

## Pytest 测试流程详解

### 什么是 Pytest？

Pytest 是一个 Python 测试框架，支持简单的单元测试和复杂的功能测试。

### 完整测试流程

#### 1. 编写测试用例

使用 pytest 格式编写测试用例：

```python
import allure
from common.attach import readAttach
from playwright.sync_api import Page


@allure.epic("百度搜索功能")
@allure.title("搜索关键词")
def test_search_keyword(page: Page):
    page.goto("https://www.baidu.com")
    page.locator("#kw").click()
    page.locator("#kw").fill("AutoGenesis")
    page.get_by_role("button", name="百度一下").click()
    readAttach(page, "./log/screenshot/", "test_search_keyword")
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

#### 3. 生成测试代码

AI 会自动生成 pytest 测试代码，或手动创建 `testcase/test_web.py`。

#### 4. 运行测试

```powershell
cd PPA-UI-Automation-master
pytest testcase/test_web.py -vs
```

#### 5. 查看结果

检查测试执行结果和 Allure 报告。

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
page.locator("input[name='wd']").click()

# XPath
page.locator("//input[@name='wd']").click()

# ID
page.locator("#search-box").click()
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

1. **元素尚未加载** - 增加超时时间或使用 `page.wait_for_selector()`
2. **定位器不正确** - 检查 CSS/XPath 表达式
3. **元素被遮挡** - 使用滚动或其他操作使元素可见

**解决方案：**

```python
# 等待元素加载
page.wait_for_selector("#element", timeout=10000)

# 滚动到元素
page.locator("#element").scroll_into_view_if_needed()

# 使用不同的定位策略
page.locator("text=按钮文本").click()
```

### 测试失败

**查看测试日志：**

```powershell
pytest testcase/test_web.py -vs
```

**查看 Allure 报告：**

```powershell
allure serve ./reports/tmp
```
