# AutoGenesis 中文操作文档

> 📚 **AutoGenesis** 是一个基于模型上下文协议（MCP）的 AI 驱动自动化测试框架，支持桌面应用（Windows/macOS）、移动应用（iOS/Android）和 Web 应用等多个平台。

---

## 📋 目录

1. [项目简介](#项目简介)
2. [环境准备](#环境准备)
3. [Windows 桌面应用测试](#windows-桌面应用测试)
4. [Web 应用测试](#web-应用测试)
5. [移动端测试](#移动端测试)
6. [BDD AI Toolkit VS Code 扩展](#bdd-ai-toolkit-vs-code-扩展)
7. [BDD 测试流程详解](#bdd-测试流程详解)
8. [常见问题排查](#常见问题排查)

---

## 项目简介

AutoGenesis 是一个 AI 驱动的自动化测试框架，核心特性包括：

- 🤖 **AI 辅助测试生成** - 基于 MCP 协议，AI 自动生成测试脚本
- 🎯 **BDD 格式支持** - 自动生成行为驱动开发（BDD）格式的测试代码
- 🖥️ **多平台支持** - Windows/macOS 桌面应用、iOS/Android 移动应用、Web 应用
- 🔄 **一键录制回放** - VS Code 扩展支持自然语言录制和一键回放
- 📸 **截图与分析** - 支持截图和 AI 截图分析功能

### 项目结构

```
AutoGenesis/
├── appium-mcp-server/       # 移动端/macOS MCP 服务器
├── playwright-mcp-server/   # Web 自动化 MCP 服务器
├── pywinauto-mcp-server/    # Windows 自动化 MCP 服务器
├── bdd_ai_toolkit/          # VS Code 扩展
└── behave-demo/             # BDD 测试示例
```

---

## 环境准备

### 前置要求

- **Python 3.10 或更高版本**
- **Windows 操作系统**（Windows 测试需要）
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

## Windows 桌面应用测试

### 1. 安装依赖

```powershell
cd pywinauto-mcp-server
uv sync
```

**依赖包括：**
- `pywinauto` - Windows UI 自动化库
- `mcp` - 模型上下文协议 SDK
- 其他必要的工具库

### 2. 配置应用信息

编辑 `conf/pywinauto_conf.json` 文件，配置要自动化的应用信息：

```json
{
  "PYWINAUTO_CONFIG": {
    "app_name": "你的应用名称",
    "exe": "C:\\Path\\To\\Your\\App.exe",
    "window_title_re": "窗口名称正则",
    "launch_args": ["--arg1", "--arg2"]
  }
}
```

**配置字段说明：**
- `app_name` - 应用名称（用于日志记录）
- `exe` - 应用可执行文件的完整路径
- `window_title_re` - 匹配主窗口标题的正则表达式
  - `".*Notepad"` - 匹配以 "Notepad" 结尾的窗口标题
  - `"Untitled.*"` - 匹配以 "Untitled" 开头的窗口标题
  - `"My App"` - 精确匹配 "My App"
- `launch_args` - （可选）启动应用时传递的命令行参数

### 3. 启动 MCP 服务器

```powershell
cd pywinauto-mcp-server
uv run python simple_server.py --transport sse
```

默认使用 SSE（Server-Sent Events）模式。

### 4. 配置 MCP 客户端

#### VS Code 配置

在项目根目录创建或编辑 `.vscode/mcp.json`：

**方式 1：SSE 模式**

```json
{
  "servers": {
    "auto-genesis-mcp-pywinauto-sse": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

**方式 2：stdio 模式（推荐本地开发使用）**

```json
{
  "servers": {
    "auto-genesis-mcp-pywinauto-stdio": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "c:\\Users\\username\\code\\AutoGenesis\\pywinauto-mcp-server",
        "python",
        "c:\\Users\\username\\code\\AutoGenesis\\pywinauto-mcp-server\\simple_server.py",
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

**注意：**
- **stdio 模式**：VS Code 自动启动和管理 MCP 服务器进程，适合本地开发
- **SSE 模式**：需要手动启动 MCP 服务器，适合远程服务器或多客户端场景
- 请将路径替换为你的实际项目路径

#### Cursor 配置

在 Cursor 设置中添加 MCP 服务器配置：

**方式 1：SSE 模式**

```json
{
  "mcpServers": {
    "auto-genesis-mcp-pywinauto-sse": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

**方式 2：stdio 模式**

```json
{
  "mcpServers": {
    "auto-genesis-mcp-pywinauto-stdio": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "c:\\Users\\username\\code\\AutoGenesis\\pywinauto-mcp-server",
        "python",
        "c:\\Users\\username\\code\\AutoGenesis\\pywinauto-mcp-server\\simple_server.py",
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

### 5. 使用 MCP 生成测试代码

#### 编写测试用例

项目已提供示例测试用例 `behave-demo/features/demo.feature`，可参考编写适合你 Windows 应用的测试用例。

示例：

```gherkin
Feature: Edge 浏览器测试

  Scenario: 打开 Edge 浏览器并访问 Bing 搜索
    Given 启动 Edge 浏览器
    When 导航到 "https://www.bing.com"
    Then 验证标签页标题包含 "Bing"
```

#### 生成测试代码

使用 `autoGenesis-win` skill 从场景自动生成测试代码：

```
使用 skill autoGenesis-win 执行场景：在 Edge 上测试 msn.com 网站
```

Skill 会自动完成：
- 从 `.feature` 文件中定位场景
- 解析所有场景步骤
- 通过 MCP 工具调用执行每个步骤
- 处理重试逻辑和错误恢复
- 生成 BDD 测试代码
- 将生成的代码保存到项目中

### 6. 运行生成的测试代码

#### 运行特定场景

```powershell
behave --name "场景名称"
```

#### 更多选项

```powershell
# 生成 JSON 报告
behave --format json -o reports/results.json

# 使用标签过滤
behave --tags=@smoke

# 详细输出
behave -v
```

### 支持的工具

#### 📱 应用管理
- **app_launch** - 启动应用
- **app_close** - 关闭应用
- **app_screenshot** - 截取应用窗口截图

#### 🎯 元素操作
- **element_click** - 点击元素
- **right_click** - 右键点击元素
- **enter_text** - 在元素中输入文本
- **send_keystrokes** - 发送键盘按键
- **select_item** - 选择列表项
- **open_folder** - 打开文件夹

#### 🖱️ 鼠标操作
- **mouse_drag_drop** - 鼠标拖放操作
- **mouse_hover** - 鼠标悬停
- **mouse_scroll** - 鼠标滚动

#### ✅ 验证工具
- **verify_element_exists** - 验证元素存在
- **verify_element_not_exist** - 验证元素不存在
- **verify_checkbox_state** - 验证复选框状态
- **verify_element_value** - 验证元素值
- **verify_elements_order** - 验证元素顺序
- **verify_visual_task** - 视觉验证任务

#### 🔧 代码生成
- **before_gen_code** - 初始化代码生成会话
- **preview_code_changes** - 预览生成的代码变更
- **confirm_code_changes** - 确认并应用代码变更

---

## Web 应用测试

### 1. 安装依赖

```powershell
cd playwright-mcp-server
uv sync
```

### 2. 安装 Playwright 浏览器

```powershell
uv run playwright install
```

### 3. 配置浏览器环境

从模板创建本地配置文件：

```powershell
cp conf/playwright_conf.template.json conf/playwright_conf.json
```

编辑 `conf/playwright_conf.json`：

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

**配置说明：**
- `browser_name` - 浏览器类型（chromium、firefox、webkit）
- `headless` - 是否使用无头模式（true/false）
- `viewport` - 浏览器窗口大小
  - `width` - 窗口宽度（像素）
  - `height` - 窗口高度（像素）
- `timeout` - 默认超时时间（毫秒）
- `slow_mo` - 减慢操作速度（毫秒，用于调试）

### 4. 启动 MCP 服务器

```powershell
cd playwright-mcp-server
uv run python simple_server.py --transport sse
```

### 5. 配置 MCP 客户端

#### VS Code 配置

**方式 1：SSE 模式**

```json
{
  "servers": {
    "auto-genesis-mcp-web": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

**方式 2：stdio 模式（推荐）**

```json
{
  "servers": {
    "auto-genesis-mcp-web": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "c:\\Users\\username\\projects\\AutoGenesis\\playwright-mcp-server",
        "python",
        "c:\\Users\\username\\projects\\AutoGenesis\\playwright-mcp-server\\simple_server.py",
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

#### Cursor 配置

**方式 1：SSE 模式**

```json
{
  "mcpServers": {
    "auto-genesis-mcp-web": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

**方式 2：stdio 模式**

```json
{
  "mcpServers": {
    "auto-genesis-mcp-web": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "c:\\Users\\username\\projects\\AutoGenesis\\playwright-mcp-server",
        "python",
        "c:\\Users\\username\\projects\\AutoGenesis\\playwright-mcp-server\\simple_server.py",
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

### 6. 指定 Behave 测试的 MCP 服务器名称

运行 behave 测试时，测试框架会自动从 `.vscode/mcp.json` 中发现名称以 `auto-genesis` 开头的 MCP 服务器。如果配置了多个 MCP 服务器或使用自定义服务器名称，可以通过编辑 `behave-demo/features/environment.py` 指定确切的服务器名称：

```python
# 设置为 .vscode/mcp.json 中的特定服务器名称以使用它。
# 留空则自动发现（优先 stdio 模式，匹配 "auto-genesis" 前缀）。
AUTO_GENESIS_MCP_SERVER = 'auto-genesis-mcp-web'
```

### 7. 使用 MCP 生成测试代码

#### 编写测试用例

示例：

```gherkin
Feature: Web 浏览器测试

  Scenario: 打开网页并验证标题
    Given 打开浏览器并导航到 "https://www.bing.com"
    When 页面标题应包含 "Bing"
    Then 验证搜索框存在
```

#### 生成测试代码

使用 `autoGenesis-run` skill 自动生成测试代码：

```
使用 skill autoGenesis-run 执行场景：测试 bing.com 网站
```

### 8. 运行生成的测试代码

在 `behave-demo` 目录中安装依赖：

```powershell
cd behave-demo
uv sync
```

#### 运行特定场景

```powershell
uv run python -m behave --name "场景名称"
```

#### 更多选项

```powershell
# 生成 JSON 报告
uv run python -m behave --format json -o reports/results.json

# 使用标签过滤
uv run python -m behave --tags=@smoke

# 详细输出
uv run python -m behave -v
```

### 可用的 MCP 工具

#### 浏览器导航
- `browser_navigate` - 导航到 URL
- `browser_close` - 关闭浏览器

#### 元素交互
- `find_element` - 查找页面元素
- `click_element` - 点击元素
- `send_keys` - 在元素中输入文本
- `get_text` - 获取元素文本内容
- `select_option` - 选择下拉选项
- `press_key` - 按下键盘按键

#### 页面信息
- `get_page_title` - 获取当前页面标题
- `get_page_url` - 获取当前页面 URL
- `wait_for_element` - 等待元素出现

#### 验证工具
- `verify_element_exists` - 验证元素存在
- `verify_element_not_exists` - 验证元素不存在
- `verify_element_attribute` - 验证元素属性值
- `verify_text_on_page` - 验证页面文本存在

#### 工具类
- `screenshot` - 截取截图
- `execute_javascript` - 执行 JavaScript 代码

---

## 移动端测试

### 1. 安装依赖

```powershell
cd appium-mcp-server
uv sync
```

### 2. 配置移动设备

编辑 `conf/appium_conf.json` 文件，配置移动设备信息：

```json
{
  "APPIUM_CONFIG": {
    "platformName": "Android",
    "deviceName": "emulator-5554",
    "app": "C:\\Path\\To\\Your\\App.apk",
    "automationName": "UiAutomator2"
  }
}
```

### 3. 启动 Appium 服务器

```powershell
cd appium-mcp-server
uv run python simple_server.py --transport sse
```

### 4. 配置 MCP 客户端

参考 Web 测试部分的配置方式，在 VS Code 或 Cursor 中配置 MCP 服务器。

### 5. 使用 MCP 生成测试代码

使用 `autoGenesis-mobile` skill 自动生成移动端测试代码。

---

## BDD AI Toolkit VS Code 扩展

### 功能特性

- 🎥 **AI 驱动的 BDD 测试录制** - 录制用户操作并自动生成 BDD 测试代码
- 🔄 **一键回放** - 自动回放录制的测试步骤
- 💬 **自然语言转自动化代码** - 将自然语言描述转换为自动化测试代码
- 🔗 **GitHub Copilot 集成** - 通过 MCP 协议与 GitHub Copilot 集成

### 安装

1. 在 VS Code 中打开扩展市场
2. 搜索 "BDD AI Toolkit"
3. 点击安装

### 使用

1. **录制测试**
   - 打开 BDD AI Toolkit 面板
   - 点击"开始录制"
   - 执行测试操作
   - 点击"停止录制"

2. **生成测试代码**
   - AI 会自动将录制的操作转换为 BDD 格式
   - 生成 `.feature` 文件和 step definitions

3. **回放测试**
   - 选择录制的测试场景
   - 点击"回放"按钮
   - 系统自动执行测试步骤

---

## BDD 测试流程详解

### 什么是 BDD？

行为驱动开发（BDD）是一种软件开发流程，通过使用自然语言描述系统行为来促进团队协作。

### Gherkin 语法

BDD 使用 Gherkin 语法编写测试场景：

```gherkin
Feature: 功能名称
  作为某个角色
  我想要执行某些操作
  以便于实现某个业务目标

  Scenario: 场景名称
    Given 前置条件
    When 执行操作
    Then 验证结果
```

### 测试执行流程

1. **编写 Feature 文件** - 使用 Gherkin 语法描述测试场景
2. **配置 MCP 服务器** - 在 `.vscode/mcp.json` 中配置 MCP 服务器
3. **生成 Step Definitions** - AI 自动生成步骤定义代码
4. **运行测试** - 使用 behave 执行测试
5. **查看结果** - 检查测试执行结果和报告

### 示例：完整的 Web 测试流程

#### 1. 创建 Feature 文件

创建 `features/web_test.feature`：

```gherkin
Feature: Web 测试

  Scenario: 验证百度标题
    Given 我导航到 "https://www.baidu.com"
    When 我获取页面标题
    Then 页面标题应包含 "百度"
```

#### 2. 配置 MCP 服务器

在 `.vscode/mcp.json` 中配置：

```json
{
  "servers": {
    "auto-genesis-playwright": {
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

#### 3. 运行测试

```powershell
cd behave-demo
uv run behave features/web_test.feature
```

#### 4. 查看结果

```
1 feature passed, 0 failed, 0 skipped
1 scenario passed, 0 failed, 0 skipped
3 steps passed, 0 failed, 0 skipped
```

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
uv sync
```

确保 Python 版本为 3.10 或更高。查看日志文件 `logs/mcp_server.log` 获取详细错误信息。

### Playwright 浏览器未安装

安装 Playwright 浏览器：

```powershell
uv run playwright install
```

### 找不到元素

- 确保目标应用已打开并处于活动状态
- 某些应用可能需要管理员权限
- 使用 `verify_element_exists` 检查元素是否可用
- 验证元素的标题、control_type 和 automation_id 是否正确

### 权限问题

- 以管理员身份运行 MCP 客户端或命令行
- 某些系统窗口可能受保护，无法自动化

### AI 客户端无法识别 MCP 工具

- 重启 VS Code 或 Cursor
- 检查 MCP 配置文件路径是否正确
- 确认 MCP 服务器已成功启动
- 验证 Python 路径配置

### 生成的代码无法运行

以详细模式运行测试查看日志：

```powershell
behave -v
```

检查配置文件并确保：
1. 目标应用已安装在系统中
2. 配置文件中的可执行文件路径正确
3. 窗口标题模式与应用匹配
4. 如需管理员权限，请以管理员身份运行

### 端口占用问题

如果启动服务时提示端口被占用，可以关闭占用端口的程序：

```powershell
# 查找占用端口的进程
netstat -ano | findstr :8000

# 关闭进程（替换 PID 为实际进程 ID）
taskkill /PID <PID> /F
```

---

## 高级配置

### Azure OpenAI 集成（可选）

#### 配置 Azure OpenAI

设置环境变量以集成 Azure OpenAI：

```powershell
$env:AZURE_OPENAI_ENDPOINT = "your-endpoint"
$env:AZURE_OPENAI_API_KEY = "your-api-key"
$env:AZURE_OPENAI_DEPLOYMENT = "your-deployment-name"
```

然后在 `llm/chat.py` 中配置 Azure OpenAI 凭据以启用截图分析功能。

### 无头模式

对于 CI/CD 流水线或服务器环境，在配置文件中启用无头模式：

**Playwright 配置（`conf/playwright_conf.json`）：**

```json
{
  "browser": {
    "browser_name": "chromium",
    "headless": true
  }
}
```

---

## 贡献指南

本项目欢迎贡献和建议。大多数贡献需要您同意贡献者许可协议（CLA），声明您有权并实际授予我们使用您贡献的权利。详情请访问 https://cla.opensource.microsoft.com。

提交拉取请求时，CLA 机器人会自动确定您是否需要提供 CLA 并适当装饰 PR（例如状态检查、评论）。只需按照机器人提供的说明操作即可。

本项目采用 [Microsoft 开源行为准则](https://opensource.microsoft.com/codeofconduct/)。有关更多信息，请参阅 [行为准则常见问题解答](https://opensource.microsoft.com/codeofconduct/faq/) 或通过 [opencode@microsoft.com](mailto:opencode@microsoft.com) 联系我们。

---

## 安全

Microsoft 认真对待我们软件产品和服务的安全性，这包括通过我们的 GitHub 组织管理的所有源代码库，其中包括 [Microsoft](https://github.com/Microsoft)、[Azure](https://github.com/Azure)、[DotNet](https://github.com/dotnet)、[AspNet](https://github.com/aspnet) 和 [Xamarin](https://github.com/xamarin)。

如果您认为在任何 Microsoft 拥有的仓库中发现了符合 [Microsoft 安全漏洞定义](https://aka.ms/security.md/definition) 的安全漏洞，请按照以下说明向我们报告。

### 报告安全问题

**请不要通过公共 GitHub 问题报告安全漏洞。**

相反，请通过 [https://msrc.microsoft.com/create-report](https://msrc.microsoft.com/create-report) 向 Microsoft 安全响应中心（MSRC）报告。

如果您希望在不登录的情况下提交，请发送电子邮件至 [secure@microsoft.com](mailto:secure@microsoft.com)。如果可能，请使用我们的 PGP 密钥加密您的消息；请从 [Microsoft 安全响应中心 PGP 密钥页面](https://aka.ms/security.md/msrc/pgp) 下载。

您应该在 24 小时内收到回复。如果由于某种原因没有收到，请通过电子邮件跟进以确保我们收到了您的原始消息。

---

## 商标

本项目可能包含项目、产品或服务的商标或标志。Microsoft 商标或标志的授权使用须遵守 [Microsoft 的商标和品牌指南](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general)。在本项目的修改版本中使用 Microsoft 商标或标志不得引起混淆或暗示 Microsoft 赞助。任何第三方商标或标志的使用均须遵守该第三方的政策。

---

## 许可证

请参阅 [LICENSE](LICENSE) 了解许可证信息。

---

## 联系方式

如有疑问或建议，请联系：autogenesis@microsoft.com
