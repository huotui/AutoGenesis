<h1 align="center" style="margin: 30px 0 30px; font-weight: bold;">PPA-UI-Automation v1.0.0</h1>
<h4 align="center">基于 Python + Playwright + Allure 的 UI 自动化测试框架</h4>

## 框架简介

PPA-UI-Automation 是一套开源的 UI 自动化测试框架。

* 基于 Python + Playwright + Allure 构建
* 已搭建好完整的框架和基础设施，直接编写 UI 测试代码即可运行
* 支持 Allure 测试报告生成
* **支持两种测试格式**: MCP 格式(适合 AI 自动生成) 和原生 Playwright 格式(高性能)

## 安装依赖

```powershell
pip install pyaml
pip install playwright
python -m playwright install chromium
pip install allure-pytest
pip install pytest
pip install pytest-playwright
pip install mcp
pip install httpx
pip install pytest-asyncio
```

## 配置 allure 报告环境

* 下载地址: https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/
* 下载后解压,将 `bin` 目录添加到系统环境变量 PATH 中

## 项目主要目录

1. **common** (公共组件层) - MCP 客户端、文件操作等工具类
2. **testcase** (测试用例层) - 存放测试用例文件
3. **data** (数据层) - 测试数据配置文件
4. **log** (日志层) - 测试日志和截图
5. **reports** (报告层) - Allure 测试报告

## 测试格式说明

本项目支持**两种测试格式**,可根据需求选择:

### 1. MCP 格式 (默认,适合 AI 驱动)

**文件名规则**: `test_*.py` (不包含 `_native` 后缀)

**特点**:
- 基于 MCP (Model Context Protocol) 协议
- 通过 `MCPClient` 调用浏览器操作
- 支持 AI 驱动的自然语言测试生成
- 内置 `step` 和 `scenario` 元数据,便于测试报告追踪
- 支持执行轨迹记录,可自动生成可重复执行的测试代码

**示例文件**: 
- `testcase/test_bing.py` - Bing 搜索测试
- `testcase/test_baidu.py` - 百度搜索测试

**代码示例**:
```python
from common.mcp_client import MCPClient

async def test_example():
    client = MCPClient()
    try:
        await client.connect()
        await client.browser_navigate(url="https://www.baidu.com/")
        await client.send_keys(locator_value="#kw", text="playwright")
    finally:
        await client.close()
```

### 2. 原生 Playwright 格式 (高性能)

**文件名规则**: `test_*_native.py`

**特点**:
- 直接调用 Playwright API,无额外通信开销
- 性能最佳,适合 CI/CD 流水线
- 代码更简洁,调试更容易
- 适合需要极致性能的场景

**示例文件**: 
- `testcase/test_bing_native.py` - Bing 搜索测试(原生格式)

**代码示例**:
```python
from playwright.async_api import async_playwright, expect

async def test_example():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://www.baidu.com/")
        await page.locator("#kw").fill("playwright")
        await browser.close()
```

## 运行测试

### 使用 run.py 脚本 (推荐)

```powershell
cd PPA-UI-Automation-master

# 运行所有测试
python run.py

# 只运行 MCP 格式测试
python run.py --format mcp

# 只运行原生 Playwright 格式测试
python run.py --format native

# 运行指定测试文件
python run.py --test testcase/test_bing.py
```

### 使用 pytest 直接运行

```powershell
cd PPA-UI-Automation-master

# 运行所有测试
pytest testcase/ -vs --asyncio-mode=auto

# 只运行 MCP 格式 (文件名不含 _native)
pytest testcase/ -vs -k "not native" --asyncio-mode=auto

# 只运行原生 Playwright 格式 (文件名含 _native)
pytest testcase/ -vs -k "native" --asyncio-mode=auto

# 运行指定测试文件
pytest testcase/test_bing.py -vs --asyncio-mode=auto

# 运行指定测试函数
pytest testcase/test_bing.py::test_bing_search_microsoft -vs --asyncio-mode=auto
```

## 查看测试报告

### 生成 Allure 报告

```powershell
# 运行测试并生成报告数据
pytest testcase/ -vs --alluredir=./reports/tmp --clean-alluredir --asyncio-mode=auto

# 生成 HTML 报告
allure generate ./reports/tmp -o ./reports/UIReport --clean
```

### 启动 Allure 服务查看报告

```powershell
# 启动临时报告服务(自动打开浏览器)
allure serve ./reports/tmp
```

## 与 AutoGenesis 集成

本项目可与 [AutoGenesis](../.github/skills/autoGenesis-web/SKILL.md) 技能集成,实现 AI 驱动的测试生成:

1. 在 IDE 中配置 MCP 服务器
2. 使用自然语言描述测试场景
3. AI 自动执行测试步骤并记录执行轨迹
4. 自动生成可重复执行的 pytest 测试代码
5. 选择生成 MCP 格式或原生 Playwright 格式

**配置 MCP 服务器** (`.vscode/mcp.json`):
```json
{
  "servers": {
    "auto-genesis-mcp-web": {
      "command": "python",
      "args": [
        "d:\\workspace\\qoder\\AutoGenesis\\playwright-mcp-server\\simple_server.py",
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

## 常见问题

### 浏览器无法启动

确保已安装 Playwright 浏览器:
```powershell
python -m playwright install chromium
```

### 找不到元素

- 检查元素定位器是否正确
- 增加等待时间或使用 `wait_for_selector`
- 使用开发者工具检查页面结构

### 测试执行失败

- 查看控制台输出
- 检查 Allure 报告中的截图
- 查看 `log` 目录下的日志文件

## 许可证

MIT License
