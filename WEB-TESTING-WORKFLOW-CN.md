# AutoGenesis Web 测试 - 手动 vs AI 编写分工说明

> 本文档通过实际操作演示，说明在 Web 自动化测试中，哪些部分需要人工编写，哪些可以由 AI 自动生成。

---

## 📊 总览：分工比例

| 部分 | 编写方式 | 占比 | 说明 |
|------|----------|------|------|
| 测试用例设计 | **手动编写** | 20% | 需要理解业务需求 |
| Pytest 测试脚本 | **AI 生成** | 50% | 模式化代码，可自动生成 |
| 配置文件 | **手动编写** | 10% | 环境配置 |
| 调试和优化 | **人工+AI** | 20% | 协作完成 |

---

## 📝 第一部分：需要手动编写的内容

### 1. 测试用例设计

**为什么需要手动编写？**
- 需要理解业务需求和用户场景
- 需要定义测试目标和验收标准
- 需要确定测试步骤和预期结果

**示例：**

```python
# 文件名：testcase/test_baidu.py
# 这部分需要人工设计测试逻辑

import allure
from common.attach import readAttach
from playwright.sync_api import Page


@allure.epic("百度搜索功能")
@allure.title("搜索关键词并验证结果")
def test_search_keyword(page: Page):
    # 测试步骤需要人工设计
    page.goto("https://www.baidu.com")
    page.locator("#kw").click()
    page.locator("#kw").fill("AutoGenesis")
    page.get_by_role("button", name="百度一下").click()
    readAttach(page, "./log/screenshot/", "test_search_keyword")
```

**人工需要决定的内容：**
- ✅ 测试什么功能？（百度搜索）
- ✅ 测试场景是什么？（搜索关键词、验证元素）
- ✅ 预期结果是什么？（搜索结果包含关键词）
- ✅ 使用什么 Allure 标签？（epic、title）

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

### 1. Pytest 测试脚本

**为什么可以 AI 生成？**
- 模式化的代码结构
- 每个测试步骤对应固定的 Playwright API 调用
- 函数内部调用 MCP 工具，结构固定

**AI 生成的示例：**

```python
# 文件名：testcase/test_baidu.py
# 这部分可以由 AI 自动生成

import allure
from common.attach import readAttach
from playwright.sync_api import Page


@allure.epic("百度搜索功能")
@allure.title("搜索关键词并验证结果")
def test_search_keyword(page: Page):
    """百度搜索关键词测试"""
    # AI 生成：导航到百度首页
    page.goto("https://www.baidu.com")
    
    # AI 生成：在搜索框输入文本
    page.locator("#kw").click()
    page.locator("#kw").fill("AutoGenesis")
    
    # AI 生成：点击搜索按钮
    page.get_by_role("button", name="百度一下").click()
    
    # AI 生成：截图并附加到 Allure 报告
    readAttach(page, "./log/screenshot/", "test_search_keyword")


@allure.epic("百度搜索功能")
@allure.title("验证百度首页元素")
def test_baidu_home_elements(page: Page):
    """验证百度首页元素"""
    page.goto("https://www.baidu.com")
    
    # 验证搜索框存在
    search_box = page.locator("#kw")
    assert search_box.is_visible()
    
    # 验证搜索按钮存在
    search_button = page.get_by_role("button", name="百度一下")
    assert search_button.is_visible()
    
    readAttach(page, "./log/screenshot/", "test_baidu_home_elements")
```

### 2. AI 如何生成测试脚本？

**生成规则：**

| 测试步骤 | 生成的 Playwright API | 说明 |
|----------|----------------------|------|
| 导航到 URL | `page.goto(url)` | 页面导航 |
| 点击元素 | `page.locator(selector).click()` | 元素点击 |
| 输入文本 | `page.locator(selector).fill(text)` | 文本输入 |
| 验证元素存在 | `assert page.locator(selector).is_visible()` | 元素验证 |
| 获取文本 | `page.locator(selector).text_content()` | 文本获取 |

**生成逻辑：**
1. 解析测试步骤描述
2. 根据步骤语义选择对应的 Playwright API
3. 生成函数体，包括参数传递和结果验证
4. 添加 Allure 装饰器和截图代码

---

## 🔄 第三部分：人工 + AI 协作的内容

### 1. 调试和优化

**场景：** 百度搜索框元素不可见，需要特殊处理

**AI 生成的初始代码：**

```python
@allure.epic("百度搜索功能")
@allure.title("搜索关键词并验证结果")
def test_search_keyword(page: Page):
    page.goto("https://www.baidu.com")
    page.locator("#kw").fill("AutoGenesis")
    page.get_by_role("button", name="百度一下").click()
    readAttach(page, "./log/screenshot/", "test_search_keyword")
```

**问题：** 百度搜索框可能需要等待才能交互

**人工分析 + AI 优化后的代码：**

```python
@allure.epic("百度搜索功能")
@allure.title("搜索关键词并验证结果")
def test_search_keyword(page: Page):
    page.goto("https://www.baidu.com")
    
    # 人工发现：需要等待元素可见
    page.wait_for_selector("#kw", state="visible")
    
    # 人工发现：需要点击使元素获得焦点
    page.locator("#kw").click()
    page.locator("#kw").fill("AutoGenesis")
    
    page.get_by_role("button", name="百度一下").click()
    readAttach(page, "./log/screenshot/", "test_search_keyword")
```

### 2. 元素定位器选择

**人工需要决定：**
- 使用什么定位策略？（CSS、XPath、ID、role）
- 元素的特征是什么？

**AI 可以生成：**
- 根据定位策略生成正确的 Playwright API 调用
- 处理参数传递和结果验证

---

## 📋 完整工作流程

### 步骤 1：人工设计测试用例

```python
# 人工设计：描述测试场景
@allure.epic("百度搜索功能")
@allure.title("搜索关键词并验证结果")
def test_search_keyword(page: Page):
    # 测试步骤
    page.goto("https://www.baidu.com")
    page.locator("#kw").fill("AutoGenesis")
    page.get_by_role("button", name="百度一下").click()
    readAttach(page, "./log/screenshot/", "test_search_keyword")
```

### 步骤 2：AI 生成测试脚本

```
# 使用 AI 命令
使用 skill autoGenesis-web 执行场景：搜索关键词并验证结果
```

AI 会自动生成 `test_baidu.py` 文件。

### 步骤 3：人工调试和优化

如果测试失败，人工分析错误原因，AI 协助修复代码。

### 步骤 4：运行测试

```powershell
cd PPA-UI-Automation-master
pytest testcase/test_baidu.py -vs
```

---

## 🎯 总结：分工建议

### ✅ 必须由人工完成的任务

1. **设计测试用例** - 理解业务需求，定义测试场景
2. **配置环境** - 设置服务器路径、浏览器配置
3. **选择元素定位器** - 分析页面结构，选择合适的定位策略
4. **审查生成的代码** - 确保代码符合预期

### 🤖 可以 AI 完成的任务

1. **生成测试脚本** - 根据测试步骤自动生成 pytest 代码
2. **生成 API 调用代码** - 根据步骤语义选择对应的 Playwright API
3. **生成错误处理代码** - 添加 try-catch 和断言
4. **生成日志代码** - 添加日志记录

### 🔄 人工 + AI 协作的任务

1. **调试失败的测试** - 人工分析原因，AI 生成修复代码
2. **优化元素交互** - 人工发现特殊行为，AI 实现解决方案
3. **添加等待逻辑** - 人工判断需要等待，AI 生成等待代码

---

## 💡 最佳实践建议

1. **先设计测试用例** - 用自然语言描述测试场景
2. **让 AI 生成代码** - 使用 skill 自动生成 pytest 测试脚本
3. **运行测试验证** - 检查生成的代码是否工作
4. **调试和优化** - 根据错误信息人工调整
5. **复用已有代码** - 相似的测试可以复用已有的函数

---

## 📚 参考文件

- 测试用例示例：`PPA-UI-Automation-master/testcase/test_采购.py`
- 数据驱动示例：`PPA-UI-Automation-master/testcase/test_基础数据.py`
- 环境配置：`.vscode/mcp.json`
- 浏览器配置：`playwright-mcp-server/conf/playwright_conf.json`
