# RAGFlow 项目学习文档

## 目录

- [1. 项目概述](#1-项目概述)
- [2. 技术架构](#2-技术架构)
- [3. 核心功能](#3-核心功能)
- [4. 目录结构](#4-目录结构)
- [5. 快速开始](#5-快速开始)
- [6. 核心概念](#6-核心概念)
- [7. API接口](#7-api接口)
- [8. 配置说明](#8-配置说明)
- [9. 与RAGFlow-Plus对比](#9-与ragflow-plus对比)

---

## 1. 项目概述

### 1.1 项目介绍

**RAGFlow** 是由 [Infiniflow](https://github.com/infiniflow) 开发的领先开源检索增强生成（RAG）引擎，它将前沿的 RAG 技术与 Agent 能力相融合，为大型语言模型（LLM）创建一个卓越的上下文层。

RAGFlow 提供了一个简化的 RAG 工作流程，可适应任何规模的企业。借助融合上下文引擎和预构建的 Agent 模板，RAGFlow 使开发者能够将复杂数据转化为高精度、可投入生产环境的 AI 系统，具有卓越的效率和精确度。

### 1.2 核心价值

| 核心价值 | 描述 |
|---------|------|
| **质量输入，质量输出** | 基于深度文档理解的非结构化数据知识提取，支持从海量数据中找到精确信息 |
| **模板化分块** | 智能且可解释的分块策略，提供丰富的模板选项 |
| **可溯源的引用** | 通过可视化分块减少幻觉，快速查看关键引用和可追溯的引用来源 |
| **异构数据兼容** | 支持 Word、PPT、Excel、TXT、图片、扫描件、结构化数据、网页等多种格式 |
| **自动化 RAG 工作流** | 为个人和大型企业定制简化 RAG 编排，支持可配置的 LLM 和 Embedding 模型 |

### 1.3 主要特性

#### 最新更新 (2026年)

- **2026-03-24**: RAGFlow Skill on OpenClaw — 提供通过 OpenClaw 访问 RAGFlow 数据集的官方技能
- **2025-12-26**: 支持 AI Agent 的"记忆"功能
- **2025-11-19**: 支持 Gemini 3 Pro
- **2025-11-12**: 支持从 Confluence、S3、Notion、Discord、Google Drive 同步数据
- **2025-10-23**: 支持 MinerU 和 Docling 作为文档解析方法
- **2025-10-15**: 支持可编排的摄取管道
- **2025-08-08**: 支持 OpenAI 最新的 GPT-5 系列模型
- **2025-08-01**: 支持 Agentic 工作流和 MCP

### 1.4 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAGFlow System                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │   Web UI    │    │   API Server │    │  Agent Engine   │  │
│  │  (React)    │    │   (Flask)    │    │   (Python)      │  │
│  └─────────────┘    └─────────────┘    └─────────────────┘  │
│         │                  │                     │           │
│         └──────────────────┼─────────────────────┘           │
│                            │                                   │
│  ┌─────────────────────────┼─────────────────────────────┐    │
│  │              Core RAG Engine                           │    │
│  │  ┌───────────┐  ┌────────────┐  ┌──────────────────┐  │    │
│  │  │  DeepDoc  │  │   Vector   │  │     Rerank      │  │    │
│  │  │  (OCR)    │  │   Search   │  │    (Fusion)     │  │    │
│  │  └───────────┘  └────────────┘  └──────────────────┘  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                   │
│  ┌─────────────────────────┼─────────────────────────────┐    │
│  │           Storage & Indexing Layer                     │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────────┐  │    │
│  │  │Elasticsearch│  │    Redis    │  │    MinIO      │  │    │
│  │  │  /Infinity  │  │   (Cache)   │  │  (File Store) │  │    │
│  │  └─────────────┘  └─────────────┘  └───────────────┘  │    │
│  │  ┌─────────────┐  ┌─────────────┐                     │    │
│  │  │    MySQL    │  │  Sandbox    │                     │    │
│  │  │(Metadata)   │  │ (Executor) │                     │    │
│  │  └─────────────┘  └─────────────┘                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 技术架构

### 2.1 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | TypeScript, React, UmiJS | 用户界面和交互 |
| **后端** | Python 3.12+, Flask/Quart | API 服务和核心逻辑 |
| **数据库** | MySQL | 元数据和配置存储 |
| **向量存储** | Elasticsearch / Infinity | 向量检索和全文搜索 |
| **缓存** | Redis | 会话缓存和消息队列 |
| **对象存储** | MinIO | 文档和文件存储 |
| **沙箱执行** | gVisor | 代码执行环境（可选） |
| **开发语言** | Python 46%, TypeScript 33%, Go 10%, C++ 9% | - |

### 2.2 核心模块

```
RAGFlow
├── api/              # 后端 API 服务 (Flask/Quart)
│   ├── apps/         # API Blueprints (知识库、聊天等)
│   └── db/           # 数据库模型和服务
├── rag/              # 核心 RAG 逻辑
│   └── llm/          # LLM、Embedding 和 Rerank 模型抽象
├── deepdoc/          # 文档解析和 OCR 模块
├── agent/            # Agent 推理组件
├── memory/           # Agent 记忆模块
├── web/              # 前端应用 (React + UmiJS)
├── docker/           # Docker 部署配置
├── sdk/              # Python SDK
│   └── python/       # Python 客户端
└── test/             # 测试代码
```

### 2.3 系统架构说明

1. **用户界面层**: 基于 React 的 Web 界面，提供可视化操作
2. **API 网关层**: Flask/Quart 实现的 REST API 服务
3. **RAG 核心引擎**:
   - **DeepDoc**: 文档解析、OCR、布局识别
   - **向量检索**: Elasticsearch/Infinity 实现的高性能向量搜索
   - **Rerank**: 混合检索 + 融合重排序
4. **Agent 引擎**: 支持 Agentic 工作流、MCP 协议、代码执行
5. **存储层**: MySQL（元数据）、Elasticsearch（全文+向量）、Redis（缓存）、MinIO（文件）

---

## 3. 核心功能

### 3.1 文档处理与解析

#### 支持的文件格式

| 类别 | 格式 |
|------|------|
| **文档** | PDF, DOC, DOCX, TXT, MD, MDX |
| **表格** | CSV, XLSX, XLS |
| **图片** | JPEG, JPG, PNG, TIF, GIF |
| **幻灯片** | PPT, PPTX |
| **其他** | 扫描件、结构化数据、网页 |

#### 分块方法 (Chunk Methods)

| 方法 | 说明 | 适用场景 |
|------|------|----------|
| **naive** | 通用分块（默认） | 通用文档 |
| **manual** | 手动分块 | 需要人工干预的文档 |
| **qa** | Q&A 分块 | 问答类文档 |
| **table** | 表格分块 | Excel、表格类文档 |
| **paper** | 论文分块 | 学术论文 |
| **book** | 书籍分块 | 书籍、章节结构文档 |
| **laws** | 法律分块 | 法律条文、合同 |
| **presentation** | 演示分块 | PPT、幻灯片 |
| **picture** | 图片分块 | 图片说明 |
| **one** | 整篇文档 | 不分块 |
| **email** | 邮件分块 | 邮件对话 |
| **knowledge-graph** | 知识图谱分块 | 需要实体识别的文档 |

#### Parser 配置参数

```python
# naive 方法配置示例
parser_config = {
    "chunk_token_num": 512,       # 分块 token 数
    "delimiter": "\\n",           # 分隔符
    "html4excel": False,           # 是否将 Excel 转为 HTML
    "layout_recognize": True,     # 是否识别布局
    "raptor": {"use_raptor": False},      # RAPTOR 聚类
    "parent_child": {"use_parent_child": False, "children_delimiter": "\\n"}
}
```

### 3.2 向量检索与重排序

#### 检索流程

```
用户查询
    ↓
Embedding 模型编码
    ↓
向量相似度计算 (top_k=1024)
    ↓
可选: 关键词匹配 (BM25)
    ↓
混合检索融合 (vector_similarity_weight=0.3)
    ↓
可选: Rerank 重排序
    ↓
返回 top_n=6 个最相关块
    ↓
LLM 生成答案 (附带引用)
```

#### 检索参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `similarity_threshold` | 0.2 | 最小相似度阈值 |
| `vector_similarity_weight` | 0.3 | 向量相似度权重 (1-weight 为词项权重) |
| `top_k` | 1024 | 参与计算的候选块数 |
| `top_n` | 6 | 返回给 LLM 的块数 |
| `rerank_id` | None | 重排序模型 ID |
| `keyword` | False | 是否启用关键词匹配 |

### 3.3 Agent 能力

#### Agent 功能

- **Agentic Workflow**: 支持复杂的多步骤推理任务
- **MCP (Model Context Protocol)**: 支持 MCP 协议扩展
- **Memory**: 支持 Agent 记忆功能
  - `raw`: 原始记忆
  - `semantic`: 语义记忆
  - `episodic`: 情景记忆
  - `procedural`: 程序记忆
- **代码执行器**: 支持 Python/JavaScript 代码沙箱执行

#### Agent 模板

RAGFlow 提供预构建的 Agent 模板，简化常见场景的 Agent 开发。

### 3.4 数据同步

支持从多种外部数据源同步数据：

- Confluence
- S3 (Amazon S3 / 兼容存储)
- Notion
- Discord
- Google Drive

---

## 4. 目录结构

```
ragflow/
├── .agents/           # Agent 配置文件
├── .github/           # GitHub Actions 配置
├── admin/             # 管理后台
├── agent/             # Agent 核心模块
│   ├── xxx/
│   └── README.md
├── api/               # 后端 API 服务
│   ├── apps/          # API Blueprints
│   ├── db/            # 数据库服务
│   └── main.py        # 入口文件
├── bin/               # 二进制文件
├── cmd/               # Go CLI 命令
├── common/            # 通用工具和常量
├── conf/              # 配置文件
├── deepdoc/           # 文档解析模块
│   ├── README.md
│   ├── ocr/           # OCR 功能
│   └── parser/        # 解析器
├── docker/            # Docker 配置
│   ├── .env           # 环境变量
│   ├── docker-compose.yml
│   └── docker-compose-base.yml
├── docs/              # 文档
├── example/           # 示例代码
├── helm/              # Kubernetes Helm Chart
├── internal/          # Go 内部包
├── mcp/               # MCP 服务器
├── memory/            # Agent 记忆模块
├── rag/               # 核心 RAG 逻辑
│   ├── llm/           # LLM/Embedding/Rerank
│   └── nlp/           # NLP 工具
├── sdk/               # SDK
│   └── python/        # Python SDK
├── test/              # 测试代码
├── tools/             # 工具脚本
├── web/               # 前端应用
│   ├── src/           # React 源码
│   └── package.json
├── AGENTS.md          # Agent 项目说明
├── CLAUDE.md          # Copilot 说明
├── Dockerfile         # Docker 镜像构建
├── Dockerfile.deps    # 依赖层镜像
├── pyproject.toml     # Python 项目配置
└── README.md          # 项目说明
```

---

## 5. 快速开始

### 5.1 环境要求

| 要求 | 规格 |
|------|------|
| CPU | ≥ 4 核 (x86) |
| RAM | ≥ 16 GB |
| 磁盘 | ≥ 50 GB |
| Docker | ≥ 24.0.0 |
| Docker Compose | ≥ v2.26.1 |
| gVisor | 仅使用代码执行器时需要 |

### 5.2 Docker 部署

#### 步骤 1: 克隆代码

```bash
git clone https://github.com/infiniflow/ragflow.git
cd ragflow/docker
```

#### 步骤 2: 切换版本

```bash
git checkout -f v0.25.0
```

#### 步骤 3: 配置参数

CPU 模式（默认）:
```bash
docker compose -f docker-compose.yml up -d
```

GPU 模式（加速 DeepDoc）:
```bash
sed -i '1i DEVICE=gpu' .env
docker compose -f docker-compose.yml up -d
```

#### 步骤 4: 检查服务状态

```bash
docker logs -f docker-ragflow-cpu-1
```

看到以下输出表示成功:
```
 ____ ___ ______ ______ __
/ __ \\ / | / ____// ____// /____ _ __
/ /_/ // /| | / __ / /_ / // __ \| | /| / /
/ _, _// ___ |/ /_/ // __/ / // /_/ /| |/ |/ /
/_/ |_|/_/  |_|\____//_/ /_/ \____/ |__/|__/

* Running on all addresses (0.0.0.0)
```

#### 步骤 5: 访问 Web 界面

在浏览器中访问: `http://IP_OF_YOUR_MACHINE` (默认端口 80)

#### 步骤 6: 配置 LLM

编辑 `service_conf.yaml.template`，在 `user_default_llm` 中选择 LLM 厂商并配置 API Key。

### 5.3 源码开发部署

#### 前置条件

```bash
# 安装依赖工具
pipx install uv pre-commit
```

#### 安装 Python 依赖

```bash
cd ragflow/
uv sync --python 3.12
uv run python3 download_deps.py
pre-commit install
```

#### 启动依赖服务

```bash
docker compose -f docker/docker-compose-base.yml up -d
```

#### 配置 hosts

```bash
# /etc/hosts
127.0.0.1 es01 infinity mysql minio redis sandbox-executor-manager
```

#### 启动后端服务

```bash
source .venv/bin/activate
export PYTHONPATH=$(pwd)
bash docker/launch_backend_service.sh
```

#### 启动前端服务

```bash
cd web
npm install
npm run dev
```

### 5.4 vm.max_map_count 配置

Linux 系统需要配置:

```bash
# 检查当前值
sysctl vm.max_map_count

# 临时设置
sudo sysctl -w vm.max_map_count=262144

# 永久设置
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

---

## 6. 核心概念

### 6.1 RAG 原理

RAG（Retrieval-Augmented Generation）是一种结合检索和生成的 AI 架构：

```
┌─────────────────────────────────────────────────────────┐
│                      RAG Flow                            │
│                                                         │
│  1. 文档处理                                             │
│     文档 → 解析 → 分块 → Embedding → 向量存储            │
│                                                         │
│  2. 查询处理                                             │
│     用户查询 → Embedding → 向量检索 → 重排序             │
│                                                         │
│  3. 生成                                                 │
│     检索结果 + 提示词 → LLM → 带引用的答案               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 6.2 DeepDoc 文档解析

DeepDoc 是 RAGFlow 的核心文档解析模块，提供：

- **布局识别**: 自动识别文档中的标题、段落、表格、图片等元素
- **OCR 识别**: 对扫描文档和图片进行文字识别
- **多模态理解**: 使用多模态模型理解 PDF/DOCX 中的图片
- **表格解析**: 精确解析复杂表格结构

### 6.3 知识库 (Dataset)

知识库是 RAGFlow 中的核心概念，用于组织和管理文档：

| 属性 | 说明 |
|------|------|
| `name` | 知识库名称（最大128字符） |
| `embedding_model` | 嵌入模型（格式: `model_name@model_factory`） |
| `chunk_method` | 分块方法 |
| `permission` | 权限（`me` 或 `team`） |
| `description` | 描述 |

### 6.4 分块策略

#### 简单分块 (Naive)

按固定 token 数或分隔符分块，适合通用文档。

#### 智能分块

使用文档结构信息（标题层级、段落）进行语义分块。

#### RAPTOR 分块

使用聚类算法将相似的文本块组织在一起，形成层级结构。

#### Parent-Child 分块

维护父子块关系，检索时返回父块但使用子块进行匹配。

### 6.5 混合检索

RAGFlow 采用混合检索策略，结合：

1. **向量检索**: 基于语义相似度
2. **关键词检索**: 基于 BM25 的词项匹配

最终得分 = `vector_similarity_weight × 向量相似度 + (1 - vector_similarity_weight) × 词项相似度`

### 6.6 重排序

可选的重排序步骤，使用专门的 Rerank 模型对候选块进行二次排序，提高相关性。

---

## 7. API接口

### 7.1 Python SDK

#### 安装

```bash
pip install ragflow-sdk
```

#### 初始化

```python
from ragflow_sdk import RAGFlow

rag = RAGFlow(api_key="YOUR_API_KEY", base_url="http://YOUR_BASE_URL:9380")
```

#### 错误码

| 错误码 | 消息 | 说明 |
|--------|------|------|
| 400 | Bad Request | 无效的请求参数 |
| 401 | Unauthorized | 未授权访问 |
| 403 | Forbidden | 访问被拒绝 |
| 404 | Not Found | 资源未找到 |
| 500 | Internal Server Error | 服务器内部错误 |
| 1001 | Invalid Chunk ID | 无效的 Chunk ID |
| 1002 | Chunk Update Failed | Chunk 更新失败 |

### 7.2 知识库管理

#### 创建知识库

```python
dataset = rag.create_dataset(
    name="kb_1",
    description="My knowledge base",
    embedding_model="BAAI/bge-large-zh-v1.5@BAAI",
    chunk_method="naive",
    permission="me"
)
```

#### 上传文档

```python
dataset.upload_documents([
    {"display_name": "doc1.pdf", "blob": open("doc.pdf", "rb").read()},
    {"display_name": "doc2.txt", "blob": open("doc.txt", "rb").read()}
])
```

#### 解析文档

```python
# 异步解析
documents = dataset.list_documents(keywords="test")
ids = [doc.id for doc in documents]
dataset.async_parse_documents(ids)

# 同步解析（等待完成）
results = dataset.parse_documents(ids)
```

#### 检索

```python
chunks = rag.retrieve(
    question="What is RAG?",
    dataset_ids=[dataset.id],
    similarity_threshold=0.2,
    top_n=6
)
```

### 7.3 聊天助手

#### 创建聊天

```python
chat = rag.create_chat(
    name="My Assistant",
    dataset_ids=[dataset.id],
    llm_setting={
        "temperature": 0.1,
        "max_token": 512
    },
    prompt_config={
        "system": "You are a helpful assistant.",
        "empty_response": "抱歉，我没有找到相关信息。",
        "quote": True
    }
)
```

#### 对话

```python
session = chat.create_session(name="New Session")

# 发送消息
message = session.ask("How does RAG work?", stream=False)
print(message.content)

# 流式响应
for chunk in session.ask("Tell me more", stream=True):
    print(chunk.content)
```

### 7.4 OpenAI 兼容 API

```python
from openai import OpenAI

client = OpenAI(
    api_key="ragflow-api-key",
    base_url=f"http://ragflow_address/api/v1/chats_openai/<chat_id>"
)

response = client.chat.completions.create(
    model="model",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who are you?"}
    ],
    extra_body={
        "reference": True
    }
)
```

### 7.5 记忆管理

```python
# 创建记忆
memory = rag.create_memory(
    name="conversation_memory",
    memory_type="semantic",
    top_n=5
)

# 添加消息
rag.add_message(
    memory_id=[memory.id],
    agent_id=agent_id,
    session_id=session_id,
    user_input="Hello",
    agent_response="Hi, how can I help you?"
)

# 获取记忆
result = rag.list_memory(memory_type="semantic")
```

---

## 8. 配置说明

### 8.1 环境变量配置 (.env)

```bash
# 服务端口
SVR_HTTP_PORT=80

# MySQL 配置
MYSQL_PASSWORD=ragflow

# MinIO 配置
MINIO_PASSWORD=ragflow

# 文档引擎 (elasticsearch 或 infinity)
DOC_ENGINE=elasticsearch

# 设备 (cpu 或 gpu)
DEVICE=cpu

# RAGFlow 镜像版本
RAGFLOW_IMAGE=infiniflow/ragflow:v0.25.0
```

### 8.2 服务配置 (service_conf.yaml.template)

```yaml
# LLM 配置
user_default_llm: openai  # 可选: openai, azure_openai, gemini, local 等

# Embedding 配置
user_default_embedding: BAAI

# 向量维度
embedding_dim: 1024

# 上传文件大小限制 (MB)
max_upload_file_size: 128
```

### 8.3 支持的 LLM 厂商

| 厂商 | 配置项 |
|------|--------|
| OpenAI | `API_KEY`, `BASE_URL` |
| Azure OpenAI | `AZURE_API_KEY`, `AZURE_BASE_URL` |
| Gemini | `GEMINI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Ollama | `OLLAMA_BASE_URL` |
| Xinference | `XINFERENCE_BASE_URL` |
| LocalAI | `LOCALAI_BASE_URL` |
| MiniMax | `MINIMAX_API_KEY` |
| SiliconFlow | `SILICONFLOW_API_KEY` |

### 8.4 支持的 Embedding 模型

默认: `BAAI/bge-large-zh-v1.5@BAAI`

支持的模型格式: `model_name@model_factory`

---

## 9. 与RAGFlow-Plus对比

> **注意**: RAGFlow-Plus 相关信息在官方文档中较少，以下为基于公开信息的对比分析。

### 9.1 版本说明

RAGFlow 项目存在两个主要版本：

| 版本 | 说明 |
|------|------|
| **RAGFlow (开源版)** | 完全开源的社区版本，功能完整 |
| **RAGFlow-Plus (商业版)** | Infiniflow 提供的商业版本，可能包含额外的企业级功能 |

### 9.2 可能的差异

| 方面 | RAGFlow (开源) | RAGFlow-Plus (商业) |
|------|----------------|---------------------|
| **开源许可** | Apache 2.0 | 商业许可 |
| **部署方式** | 自托管 | 云服务 + 自托管 |
| **技术支术** | 社区支持 | 官方技术支持 |
| **企业特性** | 基础功能 | SSO、审计日志、团队管理等 |
| **性能优化** | 通用配置 | 企业级性能调优 |
| **更新频率** | 与开源版本同步 | 可能独立发布 |

### 9.3 核心功能对比

RAGFlow 开源版已经包含的核心功能：

- ✅ 深度文档理解
- ✅ 多种分块策略
- ✅ 混合检索 + 重排序
- ✅ Agentic Workflow
- ✅ MCP 支持
- ✅ 多数据源同步
- ✅ Python SDK
- ✅ HTTP API
- ✅ Web UI
- ✅ Docker 部署

> **建议**: 对于大多数用例，RAGFlow 开源版已经足够使用。如需企业级支持和管理功能，可考虑 RAGFlow-Plus。

---

## 参考资源

- **GitHub 仓库**: https://github.com/infiniflow/ragflow
- **官方网站**: https://ragflow.io/
- **在线演示**: https://cloud.ragflow.io
- **官方文档**: https://ragflow.io/docs/dev/
- **Discord 社区**: https://discord.gg/NjYzJD3GM3
- **Infinity 向量数据库**: https://github.com/infiniflow/infinity

---

*文档版本: v2.0*
*更新时间: 2026年4月*
*项目版本: RAGFlow v0.25.0*


---

## 10. API权限设计分析

### 10.1 认证机制

RAGFlow 采用双层安全模型实现 API 认证：

#### 10.1.1 两类 Token

| Token 类型 | 生成方式 | 用途 | 有效期 |
|-----------|---------|------|--------|
| **Session Token** | `/v1/user/login` 接口登录后返回 | Web 前端会话认证 | 通常1天 |
| **API Token** | `/v1/system/new_token` 接口生成 | 服务间通信、API集成 | 永久有效 |

#### 10.1.2 认证流程

认证核心代码位于 `api/apps/__init__.py` 的 `_load_user()` 函数：

```python
def _load_user():
    # 1. 解析 Authorization header
    authorization = request.headers.get("Authorization")
    
    # 2. 判断是否为 Bearer token
    if authorization.lower().startswith("bearer "):
        auth_token = parts[1]  # API Token 方式
    else:
        auth_token = authorization  # Session Token 方式
    
    # 3. 优先尝试 JWT 解码（Session Token）
    try:
        access_token = str(jwt.loads(auth_token))
        user = UserService.query(access_token=access_token, status=StatusEnum.VALID.value)
        if user:
            g.user = user[0]
            return user[0]
    except:
        pass
    
    # 4. JWT 失败则尝试 APIToken 表查询
    objs = APIToken.query(token=auth_token)
    if objs:
        user = UserService.query(id=objs[0].tenant_id, ...)
```

#### 10.1.3 路由保护装饰器

```python
def login_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        user = current_user  # 调用 _load_user()
        if not user:
            raise QuartAuthUnauthorized()  # 返回 401
        return await func(*args, **kwargs)
    return wrapper
```

### 10.2 核心数据模型

#### 10.2.1 用户与租户关系

```
┌─────────────────────────────────────────────────────────────┐
│                    RAGFlow 权限模型                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────────┐         ┌──────────────────────────┐   │
│   │     User     │──────────│    UserTenant            │   │
│   │───────────── │ 1:N     │──────────────────────────│   │
│   │ id           │         │ user_id (FK)             │   │
│   │ email        │         │ tenant_id (FK) ──────────┼───┼──┐
│   │ access_token │         │ role (owner/normal)       │   │  │
│   │ tenant_id    │─────────┤──────────────────────────│   │  │
│   └──────────────┘         └──────────────────────────┘   │  │
│                                                             │  │
│                     ┌──────────────────────────┐           │  │
│                     │        Tenant            │           │  │
│                     │──────────────────────────│           │  │
│                     │ id                       │◄──────────┘  │
│                     │ name                     │              │
│                     │ llm_id / embd_id        │              │
│                     └──────────────────────────┘              │
│                              │ 1:N                           │
│                              ▼                               │
│                     ┌──────────────────────────┐              │
│                     │    Knowledgebase        │              │
│                     │──────────────────────────│              │
│                     │ id                       │              │
│                     │ tenant_id (FK)           │              │
│                     │ permission (me|team)     │              │
│                     │ created_by               │              │
│                     └──────────────────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 10.2.2 关键表结构

**User 表** (`api/db/db_models.py`):
```python
class User(DataBaseModel):
    id = CharField(max_length=32, primary_key=True)
    access_token = CharField(max_length=255, null=True, index=True)
    email = CharField(max_length=255, unique=True)
    is_superuser = BooleanField(default=False)
    # ...
```

**Tenant 表**:
```python
class Tenant(DataBaseModel):
    id = CharField(max_length=32, primary_key=True)
    name = CharField(max_length=100)
    llm_id = CharField(max_length=128)
    embd_id = CharField(max_length=128)
    # ...
```

**UserTenant 表**:
```python
class UserTenant(DataBaseModel):
    id = CharField(max_length=32, primary_key=True)
    user_id = CharField(max_length=32)
    tenant_id = CharField(max_length=32)
    role = CharField(max_length=32)  # owner / normal
    # ...
```

**Knowledgebase 表**:
```python
class Knowledgebase(DataBaseModel):
    id = CharField(max_length=32, primary_key=True)
    tenant_id = CharField(max_length=32, null=False)
    name = CharField(max_length=128)
    permission = CharField(max_length=16, default="me")  # "me" 或 "team"
    created_by = CharField(max_length=32)
    # ...
```

**APIToken 表**:
```python
class APIToken(DataBaseModel):
    tenant_id = CharField(max_length=32)
    token = CharField(max_length=64)
    class Meta:
        primary_key = CompositeKey("tenant_id", "token")
```

### 10.3 权限控制机制

#### 10.3.1 知识库权限模式

RAGFlow 开源版仅支持两种知识库权限：

| 权限值 | 含义 | 访问控制 |
|--------|------|----------|
| `me` | 仅自己 | 仅 `created_by` 等于当前用户 ID |
| `team` | 团队可见 | `tenant_id` 等于当前用户的任一 `tenant_id` |

#### 10.3.2 权限检查函数

核心权限检查位于 `api/db/services/knowledgebase_service.py`：

```python
class KnowledgebaseService:
    @classmethod
    def accessible4deletion(cls, kb_id, user_id):
        """检查用户是否有权限删除知识库"""
        tenants = UserTenantService.query(user_id=user_id)
        for tenant in tenants:
            if cls.query(tenant_id=tenant.tenant_id, id=kb_id):
                return True
        return False
    
    @classmethod
    def accessible(cls, kb_id, user_id):
        """检查用户是否有权限访问知识库"""
        # 逻辑同上，检查是否属于同一租户
```

#### 10.3.3 知识库详情接口的权限检查

```python
@manager.route('/detail', methods=['GET'])
@login_required
async def detail():
    kb_id = request.args["kb_id"]
    
    # 通过 UserTenant 表检查用户属于哪些租户
    tenants = UserTenantService.query(user_id=current_user.id)
    for tenant in tenants:
        if KnowledgebaseService.query(tenant_id=tenant.tenant_id, id=kb_id):
            break
    else:
        return get_json_result(
            data=False, 
            message='Only owner of dataset authorized for this operation.',
            code=RetCode.OPERATIN_ERROR
        )
```

### 10.4 API 端点结构

#### 10.4.1 主要 API 分类

| 模块 | 路由前缀 | 功能 |
|------|----------|------|
| **用户认证** | `/v1/user/` | 登录、注册、获取当前用户信息 |
| **系统管理** | `/v1/system/` | Token 管理、API Key 操作 |
| **知识库** | `/v1/datasets` 或 `/v1/kb` | 创建、更新、删除、详情、列表 |
| **文档** | `/v1/documents` | 上传、下载、列表、解析 |
| **分块** | `/v1/chunks` | 检索、编辑、删除 |
| **对话** | `/v1/chats` | 创建会话、发送消息、流式响应 |
| **Agent** | `/v1/agents` | Agent 管理、工具调用 |

#### 10.4.2 认证方式差异

| 接口类型 | Authorization 格式 | 示例 |
|----------|-------------------|------|
| Session Token | `Authorization: <token>` (无 Bearer 前缀) | `Authorization: ImQ4YmQ2...` |
| API Token | `Authorization: Bearer <token>` | `Authorization: Bearer ragflow-xxx...` |

---

## 11. 多租户可行性分析

### 11.1 现有租户模型

RAGFlow 采用**基于用户-租户关联**的多租户架构：

```
用户 A ──┬── 租户 T1 (owner)
         └── 租户 T2 (normal) ─── 知识库 KB3, KB4

用户 B ──┬── 租户 T1 (normal) ─── 知识库 KB1, KB2
         └── 租户 T2 (owner)

用户 C ──┬── 租户 T3 (owner) ─── 知识库 KB5
```

### 11.2 数据隔离机制

#### 11.2.1 存储层隔离

| 数据类型 | 存储位置 | 隔离字段 |
|----------|----------|----------|
| 元数据 | MySQL | `tenant_id` |
| 向量索引 | Elasticsearch/Infinity | 按 `tenant_id` 创建不同索引 |
| 文件存储 | MinIO | 按 `tenant_id` 路径隔离 |
| 会话缓存 | Redis | 按 `tenant_id` key 前缀 |

#### 11.2.2 索引命名规范

向量索引命名遵循租户隔离原则：

```python
# api/rag/nlp/search.py
def index_name(tenant_id: str) -> str:
    """生成租户专属的索引名称"""
    return f"ragflow_{tenant_id}"
```

这确保不同租户的向量数据物理隔离。

### 11.3 多租户支持评估

#### 11.3.1 现有能力

| 方面 | 支持情况 | 说明 |
|------|----------|------|
| **租户隔离** | ✅ 完全支持 | 通过 `tenant_id` 字段隔离 |
| **用户多租户归属** | ✅ 支持 | 一个用户可属于多个租户 |
| **数据物理隔离** | ✅ 支持 | 索引、文件均按租户隔离 |
| **资源配额** | ⚠️ 有限支持 | 有 `credit` 字段但未完全实现 |
| **租户间数据共享** | ❌ 不支持 | 无跨租户访问机制 |

#### 11.3.2 改造建议

如需实现完整的企业级多租户：

```python
# 1. 扩展 Tenant 表，增加配额管理
class Tenant(DataBaseModel):
    # ... 现有字段 ...
    max_kb_count = IntegerField(default=10)       # 最大知识库数
    max_storage_gb = IntegerField(default=50)     # 最大存储 GB
    max_users = IntegerField(default=20)          # 最大用户数
    
# 2. 添加租户使用量统计
class TenantUsage(DataBaseModel):
    tenant_id = CharField(max_length=32)
    storage_used_gb = FloatField(default=0)
    kb_count = IntegerField(default=0)
```

### 11.4 团队管理（Tenant）

#### 11.4.1 团队角色

`UserTenant.role` 字段定义用户在团队中的角色：

| 角色 | 权限 |
|------|------|
| `owner` | 团队所有者，可管理团队成员、知识库 |
| `normal` | 普通成员，按知识库权限设置访问 |

#### 11.4.2 团队 API

```python
# 团队成员管理
POST /v1/tenants/{tenant_id}/members
DELETE /v1/tenants/{tenant_id}/members/{user_id}
GET /v1/tenants/{tenant_id}/members
```

---

## 12. 行级权限实现建议

### 12.1 现状与挑战

#### 12.1.1 开源版限制

RAGFlow 开源版**不包含细粒度的行级权限**：

- ❌ 无法指定某个用户只能访问知识库的部分文档
- ❌ 无法对文档级别设置不同权限
- ❌ 无法基于部门/角色动态分配访问权限

#### 12.1.2 企业版功能

RAGFlow 企业版（根据公开信息）提供：

- ✅ 部门/群组管理
- ✅ 知识库级权限配置（读/写/管理）
- ✅ 成员级权限授予/撤销

### 12.2 行级权限实现方案

#### 12.2.1 数据库层改造

**Step 1: 添加知识库-用户映射表**

```python
# api/db/db_models.py

class KnowledgebasePermission(DataBaseModel):
    """知识库用户权限映射表"""
    id = CharField(max_length=32, primary_key=True)
    kb_id = CharField(max_length=32, null=False, index=True)
    user_id = CharField(max_length=32, null=False, index=True)
    permission = CharField(max_length=16)  # read / write / manage
    granted_by = CharField(max_length=32)  # 授权人
    create_time = BigIntegerField()
    
    class Meta:
        db_table = "knowledgebase_permission"
        indexes = (
            (("kb_id", "user_id"), True),  # 联合唯一索引
        )
```

**Step 2: 扩展检索时的权限过滤**

```python
# api/db/services/retrieval_service.py

class RetrievalService:
    @classmethod
    async def retrieval_with_permission(
        cls, 
        query: str, 
        user_id: str, 
        kb_ids: list,
        **kwargs
    ):
        # 1. 获取用户有权限的知识库
        authorized_kb_ids = cls._get_authorized_kb_ids(user_id, kb_ids)
        
        if not authorized_kb_ids:
            return {"chunks": [], "total": 0}
        
        # 2. 仅在授权的知识库中检索
        return await cls._retrieval(
            query, 
            authorized_kb_ids, 
            **kwargs
        )
    
    @classmethod
    def _get_authorized_kb_ids(cls, user_id, requested_kb_ids):
        """获取用户有权限访问的知识库ID"""
        # 查询显式授权
        explicit = KnowledgebasePermission.query(
            user_id=user_id,
            kb_id__in=requested_kb_ids
        )
        
        # 合并租户级授权（permission=team 的知识库）
        tenant_auth = Knowledgebase.query(
            id__in=requested_kb_ids,
            permission="team",
            tenant_id__in=cls._get_user_tenant_ids(user_id)
        )
        
        # 合并创建者授权
        creator_auth = Knowledgebase.query(
            id__in=requested_kb_ids,
            created_by=user_id
        )
        
        return list(set([p.kb_id for p in explicit]) | 
                    set([kb.id for kb in tenant_auth]) |
                    set([kb.id for kb in creator_auth]))
```

#### 12.2.2 服务层改造

**知识库列表接口**

```python
# api/apps/kb_app.py

@manager.route('/list', methods=['GET'])
@login_required
async def list_kb():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    
    # 获取用户所属租户
    tenants = UserTenantService.query(user_id=current_user.id)
    tenant_ids = [t.tenant_id for t in tenants]
    
    # 获取显式授权的知识库
    explicit_kb_ids = [
        p.kb_id for p in KnowledgebasePermission.query(user_id=current_user.id)
    ]
    
    # 构建复合查询条件
    authorized_kbs = KnowledgebaseService.query(
        status=StatusEnum.VALID.value,
        pagination={
            "page": page,
            "page_size": page_size
        },
        filters=[
            # 条件1: 用户创建的
            Q(created_by=current_user.id) |
            # 条件2: 团队可见且属于用户租户
            Q(permission="team", tenant_id__in=tenant_ids) |
            # 条件3: 显式授权
            Q(id__in=explicit_kb_ids)
        ]
    )
    
    return get_json_result(data=authorized_kbs)
```

**知识库访问权限检查**

```python
# api/common/check_kb_permission.py

def check_kb_permission(kb_id: str, user_id: str, required_permission: str = "read") -> bool:
    """
    检查用户对知识库的权限
    
    Args:
        kb_id: 知识库ID
        user_id: 用户ID
        required_permission: 所需权限 (read/write/manage)
    
    Returns:
        bool: 是否有权限
    """
    # 1. 获取知识库信息
    ok, kb = KnowledgebaseService.get_by_id(kb_id)
    if not ok:
        return False
    
    # 2. 检查是否为创建者（拥有所有权限）
    if kb.created_by == user_id:
        return True
    
    # 3. 检查是否属于同一租户且权限为 team
    user_tenants = UserTenantService.query(user_id=user_id)
    if kb.permission == "team" and kb.tenant_id in [t.tenant_id for t in user_tenants]:
        # team 权限映射为 manage
        if required_permission in ["read", "write", "manage"]:
            return True
    
    # 4. 检查显式授权
    perm = KnowledgebasePermission.query(kb_id=kb_id, user_id=user_id)
    if perm:
        permission_levels = {"read": 1, "write": 2, "manage": 3}
        required_level = permission_levels.get(required_permission, 0)
        user_level = permission_levels.get(perm.permission, 0)
        return user_level >= required_level
    
    return False
```

#### 12.2.3 向量检索层改造

在检索时注入用户权限上下文：

```python
# rag/nlp/search.py

class RetrievalDealer:
    async def retrieval(self, query, tenant_ids, kb_ids, user_id=None, **kwargs):
        # 如果提供了 user_id，过滤掉无权限的 kb_ids
        if user_id and self._permission_filter_enabled:
            authorized_kb_ids = self._get_user_authorized_kb_ids(user_id, kb_ids)
            kb_ids = authorized_kb_ids
        
        if not kb_ids:
            return {"chunks": [], "total": 0}
        
        # 继续原有检索逻辑
        return await self._do_retrieval(query, tenant_ids, kb_ids, **kwargs)
```

#### 12.2.4 Chunk 级别的权限扩展

如需更细粒度（Chunk 级别）权限控制：

```python
# api/db/db_models.py

class ChunkPermission(DataBaseModel):
    """Chunk 用户权限映射表"""
    id = CharField(max_length=32, primary_key=True)
    chunk_id = CharField(max_length=64, null=False, index=True)
    user_id = CharField(max_length=32, null=False, index=True)
    create_time = BigIntegerField()
    
    class Meta:
        db_table = "chunk_permission"
```

在检索结果中过滤：

```python
# 检索后处理
async def filter_chunks_by_permission(chunks: list, user_id: str) -> list:
    # 批量获取用户有权限的 chunk_ids
    authorized = ChunkPermission.query(user_id=user_id)
    authorized_ids = {c.chunk_id for c in authorized}
    
    return [c for c in chunks if c.chunk_id in authorized_ids]
```

### 12.3 前端改造

#### 12.3.1 知识库列表组件

```typescript
// web/src/pages/datasets/index.tsx

// 知识库列表请求需要携带用户认证
const useFetchKnowledgeList = () => {
  const { data, loading, error, fetchMore } = useQuery(GET_KNOWLEDGE_LIST, {
    fetchPolicy: 'cache-and-network',
    // 后端自动根据 token 过滤
  });
  
  return { data, loading, error, fetchMore };
};
```

#### 12.3.2 权限配置 UI

```typescript
// 新增知识库权限配置弹窗

const KnowledgebasePermissionModal = ({ kbId, onClose }) => {
  const [members, setMembers] = useState([]);
  
  const handleGrantPermission = (userId, permission) => {
    api.grantKnowledgebasePermission(kbId, {
      user_id: userId,
      permission: permission  // read/write/manage
    });
  };
  
  return (
    <Modal title="配置知识库权限">
      <Select placeholder="选择用户">
        {/* 用户列表 */}
      </Select>
      <Select placeholder="选择权限">
        <Option value="read">读取</Option>
        <Option value="write">写入</Option>
        <Option value="manage">管理</Option>
      </Select>
      <Button onClick={handleGrantPermission}>授权</Button>
    </Modal>
  );
};
```

### 12.4 实施注意事项

| 方面 | 建议 |
|------|------|
| **向后兼容** | 保留原有的 `permission="me|team"` 逻辑，新增 `KnowledgebasePermission` 表作为扩展 |
| **性能优化** | 用户权限信息应缓存到 Redis，避免每次请求查询数据库 |
| **索引优化** | `KnowledgebasePermission` 表的 `(kb_id, user_id)` 应建立唯一复合索引 |
| **审计日志** | 权限变更应记录操作日志，便于安全审计 |
| **API 兼容性** | 保留原有 API 签名，新增可选参数以支持新功能 |
| **数据迁移** | 编写脚本将现有 `permission="team"` 的知识库自动迁移到新模型 |

---

## 13. 企业级扩展建议

### 13.1 SSO 单点登录

如需对接企业 SSO（如 LDAP、OAuth2、SAML）：

```python
# api/apps/sso_app.py

@manager.route('/sso/callback', methods=['GET'])
async def sso_callback():
    # 1. 接收 SSO Provider 的回调
    code = request.args.get("code")
    
    # 2. 调用 SSO Provider 获取用户信息
    user_info = await sso_provider.get_user_info(code)
    
    # 3. 查找或创建本地用户
    user = await UserService.find_or_create_by_sso(user_info)
    
    # 4. 生成 session token 并登录
    login_user(user)
    
    return redirect("/")
```

### 13.2 审计日志

```python
# api/db/db_models.py

class AuditLog(DataBaseModel):
    id = CharField(max_length=32, primary_key=True)
    user_id = CharField(max_length=32)
    tenant_id = CharField(max_length=32)
    action = CharField(max_length=64)  # create/update/delete/read
    resource_type = CharField(max_length=32)  # knowledgebase/document/chunk
    resource_id = CharField(max_length=32)
    ip_address = CharField(max_length=64)
    create_time = BigIntegerField()
```

### 13.3 资源配额管理

```python
# api/middleware/quota_check.py

async def check_tenant_quota(tenant_id: str, resource: str) -> bool:
    """检查租户资源配额"""
    tenant = TenantService.get_by_id(tenant_id)
    usage = TenantUsage.get_or_create(tenant_id)
    
    if resource == "knowledgebase":
        return usage.kb_count < tenant.max_kb_count
    elif resource == "storage":
        return usage.storage_used_gb < tenant.max_storage_gb
    
    return True
```
