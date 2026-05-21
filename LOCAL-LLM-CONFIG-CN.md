# 本地 OpenAI 兼容接口配置指南

> 本文档说明如何配置和使用本地 OpenAI 兼容的大模型接口（如 Ollama、LM Studio、FastChat 等）。

---

## 📊 支持的本地 LLM 服务

| 服务 | 默认端口 | OpenAI 兼容 | 说明 |
|------|----------|-------------|------|
| **Ollama** | 11434 | ✅ | 最流行的本地 LLM 服务 |
| **LM Studio** | 1234 | ✅ | 图形界面，易于使用 |
| **FastChat** | 8000 | ✅ | 支持多模型 |
| **vLLM** | 8000 | ✅ | 高性能推理服务 |
| **LocalAI** | 8080 | ✅ | 完全兼容 OpenAI API |

---

## 🔧 配置方法

### 方法 1：使用环境变量（推荐）

在项目根目录创建 `.env` 文件：

```bash
# 本地 LLM 端点地址
LOCAL_LM_ENDPOINT=http://localhost:11434

# 本地 LLM 模型名称
LOCAL_LM_MODEL_NAME=qwen2.5:7b

# 本地 LLM API Key（可选，部分服务需要）
LOCAL_LM_API_KEY=your-api-key
```

### 方法 2：直接设置环境变量

**Windows PowerShell:**

```powershell
$env:LOCAL_LM_ENDPOINT = "http://localhost:11434"
$env:LOCAL_LM_MODEL_NAME = "qwen2.5:7b"
$env:LOCAL_LM_API_KEY = "your-api-key"
```

**Linux/macOS:**

```bash
export LOCAL_LM_ENDPOINT=http://localhost:11434
export LOCAL_LM_MODEL_NAME=qwen2.5:7b
export LOCAL_LM_API_KEY=your-api-key
```

---

## 📝 常见服务配置示例

### 1. Ollama 配置

**安装 Ollama:**
```powershell
# Windows
winget install Ollama.Ollama

# 或下载 https://ollama.com/download
```

**下载模型:**
```powershell
# 下载 Qwen2.5 7B 模型（支持中文）
ollama pull qwen2.5:7b

# 或下载其他模型
ollama pull llama3.1:8b
ollama pull mistral:7b
```

**配置 .env 文件:**
```bash
LOCAL_LM_ENDPOINT=http://localhost:11434
LOCAL_LM_MODEL_NAME=qwen2.5:7b
```

**验证服务:**
```powershell
# 检查模型列表
curl http://localhost:11434/api/tags

# 测试聊天
curl http://localhost:11434/v1/chat/completions `
  -H "Content-Type: application/json" `
  -d '{
    "model": "qwen2.5:7b",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

### 2. LM Studio 配置

**启动 LM Studio:**
1. 打开 LM Studio
2. 加载模型
3. 启动本地服务器（默认端口 1234）

**配置 .env 文件:**
```bash
LOCAL_LM_ENDPOINT=http://localhost:1234
LOCAL_LM_MODEL_NAME=local-model
```

### 3. vLLM 配置

**启动 vLLM 服务:**
```bash
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --port 8000
```

**配置 .env 文件:**
```bash
LOCAL_LM_ENDPOINT=http://localhost:8000
LOCAL_LM_MODEL_NAME=Qwen/Qwen2.5-7B-Instruct
```

---

## 🧪 测试配置

### 测试 LLM 连接

```python
# 在 playwright-mcp-server 目录下运行
python -c "
from llm.chat import LLMClient
client = LLMClient()
print(f'端点: {client.local_lm_endpoint}')
print(f'模型: {client.local_lm_model_name}')
print(f'本地 LLM 可用: {client.local_copilot_available()}')
"
```

### 测试图像分析

```python
# 在 playwright-mcp-server 目录下运行
python -c "
from llm.chat import LLMClient
client = LLMClient()

# 读取测试图片
with open('test.png', 'rb') as f:
    image_data = f.read()

# 测试图像分析
result = client.evaluate_task(
    task_info='描述截图中的内容',
    image_data=image_data
)
print(f'结果: {result.result}')
print(f'原因: {result.reason}')
"
```

---

## 🎯 使用场景

### 场景 1：仅使用本地 LLM

**配置:**
```bash
# 不设置 Azure OpenAI 环境变量
# 只设置本地 LLM 配置
LOCAL_LM_ENDPOINT=http://localhost:11434
LOCAL_LM_MODEL_NAME=qwen2.5:7b
```

**优先级:** 系统会自动使用本地 LLM

### 场景 2：Azure OpenAI 优先，本地 LLM 备用

**配置:**
```bash
# Azure OpenAI 配置
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com

# 本地 LLM 配置（备用）
LOCAL_LM_ENDPOINT=http://localhost:11434
LOCAL_LM_MODEL_NAME=qwen2.5:7b
```

**优先级:** 系统优先使用 Azure OpenAI，不可用时使用本地 LLM

---

## ⚠️ 注意事项

### 1. 模型要求

- **多模态支持** - 图像分析需要支持视觉的模型（如 qwen2.5-vl、llava 等）
- **上下文长度** - 建议至少 4096 tokens
- **中文支持** - 推荐使用 Qwen2.5、ChatGLM 等支持中文的模型

### 2. 性能要求

| 模型大小 | 最低内存 | 推荐 GPU | 推理速度 |
|----------|----------|----------|----------|
| 7B | 8GB | 6GB VRAM | 中等 |
| 13B | 16GB | 12GB VRAM | 较慢 |
| 70B | 64GB | 24GB VRAM | 很慢 |

### 3. 常见问题

**问题 1: 连接失败**
```
Error: Connection refused
```
**解决:** 确保本地 LLM 服务已启动，端口正确

**问题 2: 模型未找到**
```
Model 'xxx' not found
```
**解决:** 检查模型名称是否正确，模型是否已下载

**问题 3: 图像分析失败**
```
Error: Model does not support image_url
```
**解决:** 使用支持多模态的模型（如 qwen2.5-vl、llava）

---

## 📚 推荐模型

### 中文支持好的模型

| 模型 | 大小 | 多模态 | 下载命令 |
|------|------|--------|----------|
| **Qwen2.5:7b** | 7B | ❌ | `ollama pull qwen2.5:7b` |
| **Qwen2.5:14b** | 14B | ❌ | `ollama pull qwen2.5:14b` |
| **Qwen2.5-VL:7b** | 7B | ✅ | `ollama pull qwen2.5-vl:7b` |
| **LLaVA:7b** | 7B | ✅ | `ollama pull llava:7b` |

### 英文模型

| 模型 | 大小 | 多模态 | 下载命令 |
|------|------|--------|----------|
| **Llama3.1:8b** | 8B | ❌ | `ollama pull llama3.1:8b` |
| **Mistral:7b** | 7B | ❌ | `ollama pull mistral:7b` |

---

## 🔗 参考链接

- [Ollama 官方文档](https://ollama.com/)
- [LM Studio 官方文档](https://lmstudio.ai/)
- [vLLM 官方文档](https://docs.vllm.ai/)
- [OpenAI API 参考](https://platform.openai.com/docs/api-reference)
