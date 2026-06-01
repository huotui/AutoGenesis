# 测试运行指南 - 支持两种格式

## 📋 格式说明

### 1. MCP 格式 (默认)
- **文件名**: `test_*.py` (不含 `_native` 后缀)
- **特点**: 
  - 基于 MCP 协议
  - 通过 `MCPClient` 调用浏览器操作
  - 支持 AI 驱动的自动生成
  - 内置 step/scenario 元数据
- **示例文件**: 
  - `testcase/test_bing.py`
  - `testcase/test_baidu.py`

### 2. 原生 Playwright 格式
- **文件名**: `test_*_native.py`
- **特点**:
  - 直接调用 Playwright API
  - 性能最佳,无额外开销
  - 代码更简洁,调试更容易
  - 适合 CI/CD 流水线
- **示例文件**: 
  - `testcase/test_bing_native.py`

## 🚀 运行测试

### 使用 run.py 脚本

```powershell
cd PPA-UI-Automation-master

# 运行所有测试(默认)
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

# 只运行 MCP 格式
pytest testcase/ -vs -k "not native" --asyncio-mode=auto

# 只运行原生 Playwright 格式
pytest testcase/ -vs -k "native" --asyncio-mode=auto

# 运行指定文件
pytest testcase/test_bing.py -vs --asyncio-mode=auto

# 运行并生成 Allure 报告
pytest testcase/ -vs --alluredir=./reports/tmp --clean-alluredir --asyncio-mode=auto
```

### 查看 Allure 报告

```powershell
# 生成报告
allure generate ./reports/tmp -o ./reports/UIReport --clean

# 启动服务查看报告
allure serve ./reports/tmp
```

## 📊 两种格式对比

| 特性 | MCP 格式 | 原生 Playwright 格式 |
|------|---------|---------------------|
| 性能 | 正常 | **最佳** |
| AI 支持 | ✅ 完整 | ❌ 有限 |
| 元数据 | ✅ step/scenario | ⚠️ 无 |
| 调试难度 | 较复杂(4层) | **简单**(2层) |
| 适用场景 | AI 自动生成 | CI/CD、性能敏感 |
