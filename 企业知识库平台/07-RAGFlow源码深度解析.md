# RAGFlow 源码深度解析 - 零基础小白教程

> **文档版本**: v1.0  
> **源码版本**: RAGFlow (最新, commit: 24af0875e)  
> **目标读者**: 零基础开发者，需要基于 RAGFlow 进行企业级知识库二次开发

---

## 目录

- [第一章：RAGFlow 小白入门](#第一章ragflow-小白入门)
- [第二章：项目架构全景图](#第二章项目架构全景图)
- [第三章：目录结构与模块划分](#第三章目录结构与模块划分)
- [第四章：DeepDoc 文档解析引擎（小白版"翻译官"）](#第四章deepdoc-文档解析引擎小白版翻译官)
- [第五章：RAG 核心引擎（小白版"图书馆管理员"）](#第五章rag-核心引擎小白版图书馆管理员)
- [第六章：API 接口详解](#第六章api-接口详解)
- [第七章：Agent 引擎（小白版"智能助手"）](#第七章agent-引擎小白版智能助手)
- [第八章：数据库与存储层](#第八章数据库与存储层)
- [第九章：二次开发实战指南](#第九章二次开发实战指南)
- [第十章：RAGFlow vs RAGFlow-Plus 对比](#第十章ragflow-vs-ragflow-plus-对比)
- [附录：关键代码示例](#附录关键代码示例)

---

## 第一章：RAGFlow 小白入门

### 1.1 什么是 RAGFlow？

**RAG = 给 AI 配了一个图书馆**

想象你问 AI 一个专业问题："2024年公司财务报告有哪些重点？"

没有 RAG 的 AI 只能靠"记忆"瞎猜，答案可能胡说八道。

有了 RAG 的 AI，会先**去图书馆查资料**，找到财务报告的相关章节，然后**基于真实资料回答**。这样答案既准确又有据可查！

### 1.2 RAGFlow 的核心能力

RAGFlow 是这个"AI 图书馆"的专业管理员，它能：

```
📚 自动整理书籍（文档解析）
   ├── 识别 PDF、Word、PPT、Excel、图片...
   ├── 理解表格、标题、段落结构
   └── 提取关键信息

📖 智能分块（Chunk = 把书拆成卡片）
   ├── 按章节分、按段落分、按表格分
   ├── 控制每张卡片的大小（512 tokens）
   └── 保持内容的连贯性

🔍 快速检索（向量检索 = 指纹匹配）
   ├── 把文字变成"数字指纹"
   ├── 意思相近的内容，指纹也相似
   └── 问问题时，找最相似的指纹

🤖 生成答案（RAG = 查资料+回答）
   ├── 找到相关资料片段
   ├── 让 AI 基于资料回答问题
   └── 附带引用来源
```

### 1.3 核心技术概念（小白版解释）

| 概念 | 小白版解释 | 比喻 |
|------|-----------|------|
| **RAG** | 查资料再回答 | 先翻书再答题 |
| **Embedding** | 把文字变成数字指纹 | 把每页书变成条形码 |
| **向量检索** | 在指纹库找相似指纹 | 用扫码枪找相似的书页 |
| **DeepDoc** | 文档翻译官 | 把各种格式转成统一格式 |
| **Chunk** | 把书拆成一页页卡片 | 图书馆的索引卡片 |
| **Re-ranking** | 复试精选 | 初筛后再精挑细选 |

### 1.4 RAGFlow 工作流程（完整图解）

```
用户上传文档                        用户提问
    │                                   │
    ▼                                   ▼
┌─────────────────┐            ┌─────────────────┐
│  1. 文档解析     │            │  1. 语义理解     │
│  (DeepDoc引擎)   │            │  (理解用户问题)   │
└────────┬────────┘            └────────┬────────┘
         │                              │
         ▼                              ▼
┌─────────────────┐            ┌─────────────────┐
│  2. 智能分块     │            │  2. 向量检索     │
│  (拆成小块)      │            │  (找相关片段)    │
└────────┬────────┘            └────────┬────────┘
         │                              │
         ▼                              ▼
┌─────────────────┐            ┌─────────────────┐
│  3. 向量化存储   │            │  3. Re-ranking   │
│  (存入向量库)    │            │  (精排精选)      │
└────────┬────────┘            └────────┬────────┘
         │                              │
         ▼                              ▼
    ┌────┴────┐                   ┌────┴────┐
    │ Elasticsearch │              │  4. LLM生成  │
    │    /Infinity │ ────────────▶│  (基于资料回答) │
    │  向量数据库  │              └────────┬────────┘
    └───────────┘                       │
                                       ▼
                                  ┌──────────┐
                                  │ 返回答案  │
                                  │ +引用来源 │
                                  └──────────┘
```

---

## 第二章：项目架构全景图

### 2.1 整体架构（企业级部署视角）

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           RAGFlow 系统架构                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐            │
│   │   Web UI     │    │   API Server │    │   Agent      │            │
│   │  (React)     │    │   (Quart)    │    │   Engine     │            │
│   │  端口 80     │    │   端口 9380   │    │   (Python)   │            │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘            │
│          │                   │                   │                      │
│          └───────────────────┼───────────────────┘                      │
│                              │                                          │
│   ┌─────────────────────────┼──────────────────────────────────────┐   │
│   │                Core RAG Engine (核心引擎)                        │   │
│   │  ┌─────────────┐  ┌─────────────┐  ┌────────────────────────┐  │   │
│   │  │   DeepDoc   │  │   Vector    │  │       Re-rank         │  │   │
│   │  │  (文档解析)  │  │   Search    │  │       (重排序)        │  │   │
│   │  │  OCR/布局识别│  │  (向量检索)  │  │                       │  │   │
│   │  └─────────────┘  └─────────────┘  └────────────────────────┘  │   │
│   │                                                                 │   │
│   │  ┌─────────────┐  ┌─────────────┐  ┌────────────────────────┐  │   │
│   │  │   Chunking  │  │  Embedding   │  │        LLM            │  │   │
│   │  │  (智能分块)  │  │  (向量化)    │  │     (对话生成)        │  │   │
│   │  └─────────────┘  └─────────────┘  └────────────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│   ┌─────────────────────────┼──────────────────────────────────────┐   │
│   │           Storage & Indexing Layer (存储与索引层)              │   │
│   │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │   │
│   │  │ Elasticsearch│ │    Redis     │ │    MinIO     │        │   │
│   │  │ /Infinity    │ │   (缓存)     │ │  (文件存储)   │        │   │
│   │  │  (向量库)    │ │             │ │              │        │   │
│   │  └──────────────┘ └──────────────┘ └──────────────┘        │   │
│   │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │   │
│   │  │    MySQL     │ │  Sandbox     │ │     Go       │        │   │
│   │  │ (元数据)     │ │ (代码执行)   │ │   Service    │        │   │
│   │  └──────────────┘ └──────────────┘ └──────────────┘        │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 技术栈详解

| 层级 | 技术选型 | 作用 | 小白版解释 |
|------|---------|------|-----------|
| **前端** | React + TypeScript | 用户界面 | 图书馆的查询终端 |
| **后端** | Python 3.12+ / Quart | API 服务 | 图书馆的管理系统 |
| **核心引擎** | Go + Python | 搜索引擎 | 图书检索的核心算法 |
| **数据库** | MySQL 8.0 | 元数据存储 | 图书目录索引卡 |
| **向量库** | Elasticsearch / Infinity | 向量检索 | 指纹识别系统 |
| **缓存** | Redis | 会话缓存 | 临时工作台 |
| **对象存储** | MinIO | 文件存储 | 图书仓库 |
| **容器编排** | Docker Compose | 服务部署 | 图书馆设备配置 |

### 2.3 Docker 容器编排分析

RAGFlow 使用 Docker Compose 进行容器编排，支持多种配置文件组合：

```yaml
# docker-compose.yml (主配置)
include:
  - ./docker-compose-base.yml  # 基础设施配置

services:
  ragflow-cpu:
    profiles: ["cpu"]           # CPU 版本
    image: ${RAGFLOW_IMAGE}
    ports:
      - "80:80"                 # Web UI
      - "9380:9380"             # API Server
      - "9381:9381"             # Admin Server
      - "9382:9382"             # MCP Server

  ragflow-gpu:
    profiles: ["gpu"]            # GPU 版本（支持 CUDA）
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

**基础设施容器**（在 `docker-compose-base.yml` 中定义）：

| 容器 | 镜像 | 端口 | 作用 |
|------|------|------|------|
| es01 | elasticsearch:8.x | 9200 | 向量检索引擎 |
| infinity | infiniflow/infinity | 23817/23820 | 备选向量引擎 |
| mysql | mysql:8.0 | 3306 | 关系数据库 |
| redis | redis | 6379 | 缓存服务 |
| minio | minio/minio | 9000/9001 | 对象存储 |
| sandbox-executor | ragflow | - | 代码沙箱执行器 |

---

## 第三章：目录结构与模块划分

### 3.1 顶级目录结构

```
ragflow/
├── agent/                # 🤖 Agent 引擎（智能助手核心）
│   ├── component/        # Agent 组件库
│   ├── templates/        # Agent 模板
│   ├── tools/            # Agent 工具集
│   └── sandbox/          # 代码沙箱
│
├── api/                  # 🌐 API 接口层
│   ├── apps/            # API 业务逻辑
│   │   ├── restful_apis/  # RESTful API 实现
│   │   ├── llm_app.py     # LLM 管理接口
│   │   └── services/       # API 服务层
│   ├── db/               # 数据库层
│   │   ├── db_models.py    # 数据模型定义
│   │   └── services/       # 数据库服务
│   └── utils/            # API 工具函数
│
├── deepdoc/              # 📄 DeepDoc 文档解析引擎
│   ├── parser/           # 各类文档解析器
│   └── vision/           # 视觉识别模块
│
├── rag/                  # 📚 RAG 核心引擎
│   ├── app/              # 分块策略（不同文档类型的处理）
│   ├── flow/             # RAG 处理流程
│   ├── llm/              # LLM 集成
│   ├── nlp/              # NLP 处理
│   ├── prompts/          # Prompt 模板
│   └── svr/              # 向量服务
│
├── internal/             # ⚙️ 内部核心模块（Go）
│   ├── engine/           # 搜索引擎引擎
│   ├── dao/              # 数据访问对象
│   └── server/           # Go 服务端
│
├── web/                  # 🎨 前端界面
│   └── src/              # React 源代码
│
├── docker/               # 🐳 Docker 配置
├── conf/                 # ⚙️ 配置文件
├── sdk/                  # 📦 SDK 开发包
├── admin/                # 👤 管理后台
└── docs/                 # 📖 文档
```

### 3.2 核心模块详解

#### 3.2.1 `deepdoc/` - 文档翻译官

**职责**：把各种格式的文档"翻译"成 AI 能理解的结构化文本

```
deepdoc/
├── parser/                    # 解析器集合
│   ├── __init__.py           # 解析器导出
│   ├── pdf_parser.py         # 📕 PDF 解析（85KB，最大最复杂）
│   ├── docx_parser.py        # 📄 Word 解析
│   ├── excel_parser.py       # 📊 Excel 解析
│   ├── ppt_parser.py         # 📽️ PPT 解析
│   ├── html_parser.py        # 🌐 网页解析
│   ├── markdown_parser.py    # 📝 Markdown 解析
│   ├── json_parser.py        # 📋 JSON 解析
│   ├── txt_parser.py         # 📃 纯文本解析
│   ├── epub_parser.py        # 📖 EPUB 电子书解析
│   ├── figure_parser.py      # 🖼️ 图片解析
│   ├── paddleocr_parser.py   # 🔤 OCR 文字识别
│   ├── mineru_parser.py      # 🤖 MinerU 智能解析
│   └── docling_parser.py     # 🤖 Docling 智能解析
│
└── vision/                    # 视觉识别
    └── ...                    # OCR 和图像处理
```

**核心解析器入口**（`deepdoc/parser/__init__.py`）：

```python
from .pdf_parser import RAGFlowPdfParser as PdfParser
from .docx_parser import RAGFlowDocxParser as DocxParser
from .excel_parser import RAGFlowExcelParser as ExcelParser
# ... 其他解析器

__all__ = [
    "PdfParser",      # PDF 解析器
    "DocxParser",     # Word 解析器
    "ExcelParser",    # Excel 解析器
    "PptParser",      # PPT 解析器
    "HtmlParser",     # 网页解析器
    # ...
]
```

#### 3.2.2 `rag/` - 图书馆管理员

**职责**：管理文档分块、向量化、检索的核心逻辑

```
rag/
├── app/                    # 📖 文档分块策略
│   ├── naive.py            # 普通文档分块（最常用）
│   ├── qa.py               # 问答对提取
│   ├── table.py            # 表格解析
│   ├── paper.py            # 学术论文
│   ├── book.py             # 书籍
│   ├── manual.py           # 用户手册
│   ├── laws.py             # 法律法规
│   ├── resume.py           # 简历
│   ├── tag.py              # 标签分类
│   └── picture.py          # 图片说明
│
├── flow/                   # 🔄 RAG 处理流程
│   ├── pipeline.py         # 处理流水线
│   ├── base.py            # 基础组件
│   ├── chunker/           # 分块器
│   │   ├── token_chunker.py  # 按 token 分块
│   │   └── title_chunker/   # 按标题分块
│   └── extractor/         # 信息提取器
│
├── llm/                    # 🤖 LLM 集成
│   ├── __init__.py        # 模型工厂
│   ├── chat_model.py      # 聊天模型
│   ├── embedding_model.py # 向量化模型
│   ├── rerank_model.py    # 重排模型
│   └── ocr_model.py       # OCR 模型
│
├── nlp/                    # 🗣️ NLP 处理
│   ├── __init__.py        # 核心 NLP 工具
│   ├── search.py          # 搜索逻辑
│   ├── query.py           # 查询处理
│   ├── rag_tokenizer.py   # 分词器
│   └── term_weight.py     # 词权重
│
├── prompts/                # 📝 Prompt 模板
│   └── generator.py       # 提示生成
│
└── svr/                    # 🖥️ 向量服务
    └── ...
```

#### 3.2.3 `api/` - API 网关

**职责**：提供 HTTP API 接口，连接前后端和核心引擎

```
api/
├── apps/
│   ├── restful_apis/      # RESTful API 实现
│   │   ├── document_api.py   # 文档管理 API (71KB)
│   │   ├── dataset_api.py    # 知识库 API (27KB)
│   │   ├── chat_api.py       # 对话 API (45KB)
│   │   ├── chunk_api.py      # 分块 API (20KB)
│   │   ├── agent_api.py      # Agent API (66KB)
│   │   ├── user_api.py       # 用户管理 API
│   │   ├── file_api.py       # 文件管理 API
│   │   └── ...
│   │
│   ├── llm_app.py         # LLM 配置 API
│   ├── __init__.py        # 认证和基础配置
│   └── services/          # API 业务服务
│
├── db/
│   ├── db_models.py      # 数据库模型定义
│   ├── services/         # 数据库服务层
│   │   ├── document_service.py   # 文档服务
│   │   ├── knowledgebase_service.py  # 知识库服务
│   │   ├── dialog_service.py     # 对话服务
│   │   └── ...
│   └── init_data.py      # 数据库初始化
│
└── utils/                # API 工具函数
```

**API 认证机制**（`api/apps/__init__.py`）：

```python
# 支持两种认证方式
def _load_user():
    # 方式1: JWT Token 认证
    # Authorization: Bearer <jwt_token>
    access_token = jwt.loads(auth_token)
    user = UserService.query(access_token=access_token)
    
    # 方式2: API Token 认证
    # Authorization: <api_token>
    objs = APIToken.query(token=auth_token)
    user = UserService.query(id=objs[0].tenant_id)
```

#### 3.2.4 `agent/` - 智能助手引擎

**职责**：实现 Agent 能力，支持复杂的多步骤任务

```
agent/
├── canvas.py              # 🎨 Agent 画布（DSL 执行引擎）
├── component/             # 📦 Agent 组件库
│   ├── base.py           # 组件基类
│   ├── llm.py            # LLM 调用组件
│   ├── retrieval.py      # 检索组件
│   ├── docs_generator.py # 文档生成组件
│   ├── categorize.py      # 分类组件
│   ├── invoke.py          # API 调用组件
│   ├── loop.py           # 循环组件
│   ├── iteration.py      # 迭代组件
│   └── ...
│
├── templates/            # 📋 Agent 模板
├── tools/               # 🔧 Agent 工具集
│   ├── search.py        # 搜索工具
│   ├── calculator.py    # 计算工具
│   └── ...
│
└── sandbox/             # 🏖️ 代码沙箱
```

---

## 第四章：DeepDoc 文档解析引擎（小白版"翻译官"）

### 4.1 DeepDoc 的职责

DeepDoc 是 RAGFlow 的**文档翻译官**，它的任务是：

```
📄 输入：各种格式的文档
   ├── PDF (扫描件、图文混排)
   ├── Word / Excel / PPT
   ├── 图片 (含文字)
   ├── 网页 / Markdown
   └── 其他格式...

🔄 处理：
   ├── OCR 文字识别（图片转文字）
   ├── 布局分析（识别标题、段落、表格）
   ├── 表格识别（表格转结构化数据）
   └── 结构提取（理解文档层次）

📤 输出：统一的结构化文本
   ├── 文本块 (text chunks)
   ├── 表格块 (table chunks)
   └── 图片块 (image chunks)
```

### 4.2 支持的文档格式

DeepDoc 支持的文件格式（定义在 `api/db/__init__.py`）：

```python
# 文档类型枚举
class FileType(StrEnum):
    # 文档类
    DOCUMENTS = "documents"
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"
    TXT = "txt"
    MARKDOWN = "markdown"
    
    # 表格类
    EXCEL = "excel"
    XLSX = "xlsx"
    CSV = "csv"
    
    # 演示类
    PPT = "ppt"
    PPTX = "pptx"
    
    # 其他
    HTML = "html"
    EPUB = "epub"
    JSON = "json"
    IMAGE = "image"
```

### 4.3 PDF 解析流程（最复杂）

PDF 解析是最复杂的部分，`deepdoc/parser/pdf_parser.py` 约 85KB，包含：

```python
# PDF 解析核心流程（简化版）

class RAGFlowPdfParser:
    def __call__(self, filename, from_page=0, to_page=MAXIMUM_PAGE_NUMBER):
        # 1️⃣ OCR 文字识别
        self.__images__(...)           # 从 PDF 提取图片
        
        # 2️⃣ 布局分析
        self._layouts_rec(...)         # 识别标题、段落、表格位置
        
        # 3️⃣ 表格识别
        self._table_transformer_job(...)  # 定位表格区域
        
        # 4️⃣ 文本合并
        self._text_merge(...)           # 合并相邻文本
        
        # 5️⃣ 表格提取
        tables = self._extract_table_figure(...)
        
        return sections, tables

    def __images__(self, ...):
        """OCR 处理：图片区域文字识别"""
        # 使用 PaddleOCR 进行文字识别
        # 支持多语言：中文、英文、日文、韩文等
        pass
    
    def _layouts_rec(self, ...):
        """布局识别：识别页面布局结构"""
        # 标题检测
        # 段落检测
        # 列表检测
        # 图片区域检测
        pass
    
    def _table_transformer_job(self, ...):
        """表格识别：定位表格位置"""
        # 使用模型识别表格边界
        pass
    
    def _text_merge(self):
        """文本合并：将分割的文本重新合并"""
        pass
```

### 4.4 OCR 集成（PaddleOCR）

RAGFlow 使用 PaddleOCR 进行文字识别：

```python
# deepdoc/parser/paddleocr_parser.py

class PaddleOCRParser:
    def __init__(self, lang='ch'):
        # 初始化 PaddleOCR
        # 支持语言：ch(中文), en(英文), japan, korean, french, german, etc.
        self.ocr = PaddleOCR(lang=lang, use_angle_cls=True)
    
    def parse(self, image):
        """识别图片中的文字"""
        result = self.ocr.ocr(image, cls=True)
        # 返回识别结果：[文本, 置信度, 位置]
```

### 4.5 不同解析方法（Parser Methods）

RAGFlow 支持多种文档解析方法（定义在 `rag/app/`）：

| 方法 | 文件 | 适用场景 | 分块策略 |
|------|------|---------|---------|
| **naive** | `naive.py` | 普通文档 | 按段落/标题分块 |
| **qa** | `qa.py` | 问答对文档 | 问答自动分离 |
| **table** | `table.py` | 表格文档 | 整表作为块 |
| **paper** | `paper.py` | 学术论文 | 按章节+引用分块 |
| **book** | `book.py` | 书籍 | 按章节分块 |
| **manual** | `manual.py` | 用户手册 | 按步骤分块 |
| **laws** | `laws.py` | 法律法规 | 按条款分块 |
| **resume** | `resume.py` | 简历 | 字段级分块 |
| **tag** | `tag.py` | 标签分类 | 按标签分类 |
| **picture** | `picture.py` | 图文混排 | 图片+描述分块 |

### 4.6 解析配置（Parser Config）

```python
# 解析器配置示例
parser_config = {
    # 通用配置
    "chunk_token_num": 512,           # 每个块的最大 token 数
    "delimiter": "\n",                 # 分块分隔符
    "layout_recognize": True,          # 启用布局识别
    
    # PDF 特定配置
    "pdf_parser": "deepdoc",           # 解析器：deepdoc | naive | naive2v
    "auto_join": True,                 # 自动合并短文本
    "render_version": "v1",            # 渲染版本
    
    # OCR 配置
    "ocr": True,                       # 启用 OCR
    "ocr_lang": "ch",                  # OCR 语言
    
    # 表格配置
    "table_row_count": 50,             # 表格行数限制
    "table_instruction": "",           # 表格说明
    
    # 特定方法配置
    "task_page_size": 12,             # 简历页数
    "raptor_max_tokens": 512,         # RAPTOR 块大小
}
```

---

## 第五章：RAG 核心引擎（小白版"图书馆管理员"）

### 5.1 RAG 引擎职责

RAG 引擎是整个系统的**核心**，它负责：

```
📖 文档管理
   ├── 文档上传和存储
   ├── 分块处理（Chunk）
   └── 向量化存储

🔍 检索查询
   ├── 语义理解
   ├── 向量检索
   ├── 关键词检索
   └── 混合检索 + Re-ranking

💬 对话生成
   ├── 上下文管理
   ├── Prompt 构建
   └── LLM 调用
```

### 5.2 文档分块（Chunking）策略

#### 5.2.1 Token 分块器（最常用）

```python
# rag/flow/chunker/token_chunker.py

class TokenChunkerParam:
    def __init__(self):
        self.delimiter_mode = "token_size"  # 分块模式
        self.chunk_token_size = 512         # 每块 token 数
        self.delimiters = ["\n"]            # 分隔符
        self.overlapped_percent = 0         # 重叠率（0-1）
        self.children_delimiters = []       # 子块分隔符

class TokenChunker:
    async def _invoke(self, **kwargs):
        # 1. 从上游获取文本块
        chunks = self._get_chunks_from_upstream()
        
        # 2. 按分隔符分割
        for chunk in chunks:
            # 使用分隔符（如换行）分割文本
            segments = split_by_delimiter(chunk["text"])
            
            # 3. 按 token 大小合并
            merged_chunks = merge_by_token_count(
                segments,
                max_tokens=self._param.chunk_token_size
            )
            
            # 4. 可选：添加重叠
            if self._param.overlapped_percent > 0:
                merged_chunks = add_overlap(
                    merged_chunks,
                    overlap_ratio=self._param.overlapped_percent
                )
```

#### 5.2.2 分块模式详解

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| `token_size` | 按 token 数量分块 | 通用场景 |
| `delimiter` | 按分隔符分块 | 结构化文档 |
| `one` | 不分块，整篇文档 | 短文档 |

### 5.3 向量化与检索

#### 5.3.1 向量化模型集成

RAGFlow 支持多种 Embedding 模型：

```python
# rag/llm/embedding_model.py

# 支持的 Embedding 模型
class EmbeddingModel:
    # OpenAI 系列
    "OpenAI": OpenAIEmbedding
    "Azure-OpenAI": AzureOpenAIEmbedding
    
    # 国内模型
    "Tongyi-Qianwen": TongyiEmbedding
    "ZHIPU-AI": ZhipuEmbedding
    "DeepSeek": DeepSeekEmbedding
    
    # 本地模型
    "BAAI": BAAIEmbedding  # BGE
    "Ollama": OllamaEmbedding
    "VLLM": VLLMEmbedding
    
    # ... 更多模型
```

#### 5.3.2 向量检索流程

```python
# rag/nlp/search.py

class Dealer:
    async def search(self, req, idx_names, kb_ids, emb_mdl):
        # 1️⃣ 获取查询向量
        q_vec = await self.get_vector(req["question"], emb_mdl)
        
        # 2️⃣ 构建混合检索表达式
        # 关键词检索
        matchText = self.qryr.question(req["question"])
        
        # 向量检索
        matchDense = MatchDenseExpr(...)
        
        # 混合检索（加权融合）
        fusionExpr = FusionExpr("weighted_sum", topk, {
            "weights": "0.05,0.95"  # 关键词5%，向量95%
        })
        
        # 3️⃣ 执行搜索
        res = await self.dataStore.search(
            src=fields,
            highlight_fields=["content_ltks"],
            filters=filters,
            match_exprs=[matchText, matchDense, fusionExpr],
            orderBy=orderBy
        )
        
        # 4️⃣ 结果后处理
        return self._prune_deleted_chunks(res)
```

#### 5.3.3 混合检索策略

```python
# 检索权重配置
{
    "vector_similarity_weight": 0.7,  # 向量相似度权重
    "keyword_similarity_weight": 0.3,  # 关键词权重
    
    # 或者精确权重
    "weights": "0.05,0.95"  # 关键词5%，向量95%
}
```

### 5.4 Re-ranking 机制

Re-ranking 是**复试精选**环节，对初筛结果进行精排：

```python
# 向量检索返回 topk=1024 个结果
# Re-ranking 精排后返回 topk=20-50 个结果

class RerankModel:
    def __init__(self, api_key, model_name):
        self.model = "BAAI/bge-reranker-v2-m3"
    
    def rerank(self, query, documents, top_k=20):
        """
        对文档进行重排序
        
        Args:
            query: 用户问题
            documents: 初筛文档列表
            top_k: 返回精排后的数量
        """
        # 计算相关性分数
        scores = self.model.predict(query, documents)
        
        # 按分数排序
        ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        
        return ranked[:top_k]
```

### 5.5 对话引擎

#### 5.5.1 LLM 集成

```python
# rag/llm/chat_model.py

class ChatModel:
    # 支持的模型
    "OpenAI": OpenAIChat
    "DeepSeek": DeepSeekChat
    "Claude": AnthropicChat
    "Gemini": GeminiChat
    "Qwen": TongyiChat
    "Ollama": OllamaChat
    # ... 40+ 模型
```

#### 5.5.2 Prompt 模板管理

```python
# rag/prompts/generator.py

# 默认 Prompt 配置
DEFAULT_PROMPT_CONFIG = {
    "system": (
        'You are an intelligent assistant. Please summarize the content '
        'of the dataset to answer the question. '
        'Please list the data in the dataset and answer in detail. '
        'When all dataset content is irrelevant to the question, '
        'your answer must include the sentence "The answer you are looking '
        'for is not found in the dataset!" '
        '\n\nHere is the knowledge base:\n'
        '{knowledge}\n'
        '\nThe above is the knowledge base.'
    ),
    "prologue": "Hi! I'm your assistant. What can I do for you?",
    "parameters": [{"key": "knowledge", "optional": False}],
    "empty_response": "Sorry! No relevant content was found!",
    "quote": True,  # 启用引用
}
```

#### 5.5.3 多轮对话管理

```python
# api/db/services/dialog_service.py

class DialogService:
    @classmethod
    async def async_chat(cls, tenant_id, dialog_id, user_id, query, **kwargs):
        # 1️⃣ 获取历史对话
        history = cls.get_history(dialog_id, limit=10)
        
        # 2️⃣ 检索相关知识
        chunks = await SearchService.search(
            query=query,
            kb_ids=dialog.kb_ids,
            topk=dialog.top_k
        )
        
        # 3️⃣ 构建 Prompt
        prompt = cls._build_prompt(query, chunks, history)
        
        # 4️⃣ 调用 LLM
        response = await chat_model.async_chat(prompt)
        
        # 5️⃣ 保存对话记录
        cls.save_message(dialog_id, user_id, query, response)
        
        return response
```

### 5.6 NLP 处理模块

```python
# rag/nlp/__init__.py

# 核心 NLP 工具
from rag.nlp import (
    rag_tokenizer,      # 分词器（支持中英文）
    query,             # 查询处理
    term_weight,       # 词权重计算
    synonym,           # 同义词处理
    naive_merge,       # 文本合并
)

# rag_tokenizer 功能
class RAGTokenizer:
    def tokenize(text):          # 分词
    def fine_grained_tokenize() # 细粒度分词
    def tradi2simp()            # 繁体转简体
    def strQ2B()               # 全角转半角
```

---

## 第六章：API 接口详解

### 6.1 API 概览

RAGFlow 提供完整的 RESTful API，端口 **9380**：

| API 分类 | 文件 | 说明 |
|---------|------|------|
| 知识库管理 | `dataset_api.py` | 创建/管理知识库 |
| 文档管理 | `document_api.py` | 上传/解析文档 |
| 分块管理 | `chunk_api.py` | 管理文档分块 |
| 对话管理 | `chat_api.py` | 创建/管理对话 |
| LLM 配置 | `llm_app.py` | 配置语言模型 |
| Agent | `agent_api.py` | Agent 相关 API |
| 用户管理 | `user_api.py` | 用户和权限 |

### 6.2 认证机制

```python
# API 认证方式

# 方式1: JWT Token (Web 登录)
Headers:
  Authorization: Bearer eyJhbGc...

# 方式2: API Token (开发调用)
Headers:
  Authorization: <your_api_token>
```

### 6.3 核心 API 示例

#### 6.3.1 创建知识库

```python
# POST /api/v1/datasets
# 创建新的知识库

import requests

response = requests.post(
    "http://localhost:9380/api/v1/datasets",
    headers={
        "Authorization": "Bearer <token>",
        "Content-Type": "application/json"
    },
    json={
        "name": "我的知识库",
        "description": "企业文档知识库",
        "embedding_model": "BAAI/bge-large-zh-v1.5",
        "chunk_method": "naive",  # 普通分块
        "permission": "me"        # 私有
    }
)

print(response.json())
```

**响应示例**：
```json
{
  "code": 0,
  "data": {
    "id": "d7b9c2e8f4a1...",
    "name": "我的知识库",
    "embedding_model": "BAAI/bge-large-zh-v1.5",
    "chunk_num": 0,
    "document_num": 0,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### 6.3.2 上传文档

```python
# POST /api/v1/datasets/{dataset_id}/documents/upload
# 上传文档到知识库

import requests

# 上传文件
with open("document.pdf", "rb") as f:
    response = requests.post(
        f"http://localhost:9380/api/v1/datasets/{dataset_id}/documents/upload",
        headers={"Authorization": "Bearer <token>"},
        files={"file": ("document.pdf", f, "application/pdf")}
    )

# 或者上传 URL
response = requests.post(
    f"http://localhost:9380/api/v1/datasets/{dataset_id}/documents/upload",
    headers={"Authorization": "Bearer <token>"},
    params={"url": "https://example.com/document.pdf"}
)
```

#### 6.3.3 解析文档

```python
# PUT /api/v1/datasets/{dataset_id}/documents/{document_id}
# 触发文档解析

response = requests.put(
    f"http://localhost:9380/api/v1/datasets/{dataset_id}/documents/{document_id}",
    headers={"Authorization": "Bearer <token>"},
    json={
        "run": 1,  # 触发解析
        "parser_config": {
            "chunk_token_num": 512,
            "layout_recognize": True,
            "ocr": True
        }
    }
)
```

#### 6.3.4 对话问答

```python
# POST /api/v1/chats/{chat_id}/completion
# 发起对话

response = requests.post(
    f"http://localhost:9380/api/v1/chats/{chat_id}/completion",
    headers={"Authorization": "Bearer <token>"},
    json={
        "question": "公司的年假政策是什么？",
        "stream": False  # 同步返回
    }
)

print(response.json())
```

**响应示例**：
```json
{
  "code": 0,
  "data": {
    "answer": "根据公司政策，员工每年享有带薪年假...",
    "reference": {
      "chunks": [
        {
          "content": "员工年假政策：\n1. 工作满1年，年假5天\n2. 工作满3年，年假10天...",
          "document_name": "员工手册.pdf",
          "similarity": 0.89
        }
      ]
    }
  }
}
```

### 6.4 API 接口清单

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/datasets` | POST | 创建知识库 |
| `/api/v1/datasets` | GET | 列出知识库 |
| `/api/v1/datasets/{id}` | GET | 获取知识库详情 |
| `/api/v1/datasets/{id}` | PUT | 更新知识库 |
| `/api/v1/datasets/{id}` | DELETE | 删除知识库 |
| `/api/v1/datasets/{id}/documents` | GET | 列出文档 |
| `/api/v1/datasets/{id}/documents/upload` | POST | 上传文档 |
| `/api/v1/datasets/{id}/documents/{doc_id}` | PUT | 更新文档/触发解析 |
| `/api/v1/datasets/{id}/documents/{doc_id}` | DELETE | 删除文档 |
| `/api/v1/chats` | POST | 创建对话 |
| `/api/v1/chats/{id}` | GET | 获取对话详情 |
| `/api/v1/chats/{id}/completion` | POST | 发送消息 |
| `/api/v1/chats/{id}/sessions` | GET | 获取会话列表 |
| `/api/v1/llm/factories` | GET | 列出 LLM 供应商 |
| `/api/v1/llm/set_api_key` | POST | 设置 API Key |
| `/api/v1/users` | GET | 列出用户 |
| `/api/v1/users` | POST | 创建用户 |

---

## 第七章：Agent 引擎（小白版"智能助手"）

### 7.1 Agent 是什么？

**Agent = 能自主规划和执行任务的智能助手**

它不只是回答问题，而是能：
- 理解复杂任务
- 分解成多个步骤
- 调用工具执行
- 根据结果调整策略

### 7.2 Agent 架构

```
┌─────────────────────────────────────────────────────────┐
│                      Agent Canvas                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   ┌──────────┐                                          │
│   │   Begin   │ ───▶  [开始节点]                        │
│   └──────────┘                                          │
│         │                                                │
│         ▼                                                │
│   ┌──────────┐                                          │
│   │ Retrieval│ ───▶  [检索组件]                         │
│   └──────────┘                                          │
│         │                                                │
│         ▼                                                │
│   ┌──────────┐                                          │
│   │   LLM    │ ───▶  [生成组件]                         │
│   └──────────┘                                          │
│         │                                                │
│         ▼                                                │
│   ┌──────────┐                                          │
│   │  Answer  │ ───▶  [输出组件]                         │
│   └──────────┘                                          │
│                                                          │
├─────────────────────────────────────────────────────────┤
│  DSL (Domain Specific Language): JSON 格式的流程定义     │
└─────────────────────────────────────────────────────────┘
```

### 7.3 Agent 组件库

```python
# agent/component/

# 核心组件
llm.py              # LLM 调用组件
retrieval.py        # 知识检索组件

# 逻辑组件
categorize.py        # 分类组件
switch.py           # 条件分支
loop.py             # 循环组件
iteration.py        # 迭代组件

# 数据组件
docs_generator.py   # 文档生成
excel_processor.py  # Excel 处理

# 外部交互
invoke.py           # API 调用
message.py          # 消息处理

# 变量操作
variable_assigner.py    # 变量赋值
variable_aggregator.py  # 变量聚合
```

### 7.4 Agent DSL 示例

```python
# Agent 流程定义（DSL）
dsl = {
    "components": {
        "begin": {
            "obj": {
                "component_name": "Begin",
                "params": {}
            },
            "downstream": ["retrieval_0"]
        },
        "retrieval_0": {
            "obj": {
                "component_name": "Retrieval",
                "params": {
                    "topk": 10,
                    "similarity_threshold": 0.3
                }
            },
            "downstream": ["generate_0"]
        },
        "generate_0": {
            "obj": {
                "component_name": "Generate",
                "params": {
                    "llm_id": "gpt-4",
                    "temperature": 0.7
                }
            },
            "downstream": ["answer_0"]
        },
        "answer_0": {
            "obj": {
                "component_name": "Answer",
                "params": {}
            },
            "downstream": []
        }
    },
    "path": ["begin"],
    "globals": {
        "sys.query": "",
        "sys.user_id": ""
    }
}
```

### 7.5 自定义 Agent 开发

```python
# 创建自定义 Agent 组件

from agent.component.base import ComponentBase, ComponentParamBase

class MyCustomComponentParam(ComponentParamBase):
    def __init__(self):
        super().__init__()
        self.my_param = ""

class MyCustomComponent(ComponentBase):
    component_name = "MyCustomComponent"
    
    async def _invoke(self, **kwargs):
        # 获取输入
        input_data = self.get_input()
        
        # 处理逻辑
        result = do_something(input_data, self._param.my_param)
        
        # 设置输出
        self.set_output("result", result)
```

---

## 第八章：数据库与存储层

### 8.1 数据库模型

RAGFlow 使用 MySQL 存储元数据，使用 Peewee ORM：

```python
# api/db/db_models.py

# 核心数据模型

class User(BaseModel):
    """用户表"""
    id = CharField(primary_key=True)
    email = CharField(unique=True)
    nickname = CharField()
    password = CharField()
    phone = CharField(null=True)
    status = CharField()  # 1=有效, 0=无效
    
class Tenant(BaseModel):
    """租户表"""
    id = CharField(primary_key=True)
    name = CharField()
    llm_api_key = TextField()  # 加密存储
    embedding_model = CharField()
    
class Knowledgebase(BaseModel):
    """知识库表"""
    id = CharField(primary_key=True)
    tenant_id = CharField()
    name = CharField()
    description = TextField()
    embedding_model = CharField()
    chunk_method = CharField()  # naive, qa, table, ...
    parser_config = JSONField()  # 解析配置
    status = CharField()
    
class Document(BaseModel):
    """文档表"""
    id = CharField(primary_key=True)
    kb_id = CharField()  # 所属知识库
    name = CharField()
    type = CharField()   # pdf, docx, ...
    size = IntegerField()  # 字节
    token_num = IntegerField()  # token 数
    chunk_num = IntegerField()  # 分块数
    progress = FloatField()  # 解析进度 0-1
    run = CharField()  # 解析状态
    status = CharField()
    
class Dialog(BaseModel):
    """对话表"""
    id = CharField(primary_key=True)
    tenant_id = CharField()
    name = CharField()
    kb_ids = JSONField()  # 关联知识库列表
    llm_id = CharField()
    prompt_config = JSONField()
    top_k = IntegerField()
    rerank_id = CharField(null=True)
    
class Conversation(BaseModel):
    """会话表（消息历史）"""
    id = CharField(primary_key=True)
    dialog_id = CharField()
    message = JSONField()  # 消息列表
    user_id = CharField()
```

### 8.2 服务层

```python
# api/db/services/

class DocumentService(CommonService):
    model = Document
    
    @classmethod
    def get_list(cls, kb_id, page, size):
        """获取文档列表"""
        pass
    
    @classmethod
    def update_progress(cls, doc_id, progress):
        """更新解析进度"""
        pass

class KnowledgebaseService(CommonService):
    model = Knowledgebase
    
    @classmethod
    def is_parsed_done(cls, kb_id):
        """检查知识库是否全部解析完成"""
        docs = DocumentService.get_by_kb_id(kb_id)
        return all(doc.run == "3" for doc in docs)  # 3=DONE

class DialogService(CommonService):
    model = Dialog
    
    @classmethod
    async def async_chat(cls, tenant_id, dialog_id, query):
        """异步对话处理"""
        pass
```

### 8.3 存储架构

```
┌─────────────────────────────────────────────┐
│              MinIO (对象存储)               │
│                                             │
│  /ragflow/                                  │
│    ├── {tenant_id}/                        │
│    │   ├── {kb_id}/                        │
│    │   │   ├── {doc_id}/                   │
│    │   │   │   ├── original/               │
│    │   │   │   │   └── document.pdf       │
│    │   │   │   └── thumbnails/             │
│    │   │   │       └── thumb.png           │
│    │   │   └── ...                         │
│    │   └── ...                             │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│     Elasticsearch / Infinity (向量存储)      │
│                                             │
│  Index: ragflow_{kb_id}                     │
│                                             │
│  Fields:                                    │
│  - docnm_kwd: 文档名                        │
│  - content_ltks: 分词文本                   │
│  - content_with_weight: 原始文本            │
│  - img_id: 图片ID                           │
│  - kb_id: 知识库ID                          │
│  - vector: 向量 [0.1, 0.2, ...]            │
│  - doc_id: 文档ID                           │
│  - chunk_order_int: 块顺序                  │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│              Redis (缓存)                   │
│                                             │
│  - 会话缓存: session:{session_id}          │
│  - 任务状态: task:{task_id}                │
│  - 进度追踪: progress:{task_id}            │
│  - 日志缓存: {flow_id}-{task_id}-logs      │
└─────────────────────────────────────────────┘
```

---

## 第九章：二次开发实战指南

### 9.1 开发环境准备

```bash
# 1. 克隆源码
git clone https://github.com/infiniflow/ragflow.git
cd ragflow

# 2. 启动基础服务
docker compose -f docker/docker-compose-base.yml up -d

# 3. 启动 RAGFlow（开发模式）
docker compose -f docker/docker-compose.yml --profile cpu up

# 4. 本地开发（可选）
python -m venv venv
source venv/bin/activate
pip install -e .
```

### 9.2 新增自定义解析方法

假设你想添加一个"合同解析器"：

```python
# 1. 在 rag/app/ 下创建 contract.py

from rag.app.naive import by_deepdoc
from rag.nlp import rag_tokenizer

def chunk(filename, binary=None, lang="Chinese", callback=None, **kwargs):
    """
    合同文档解析
    
    特殊处理：
    - 识别合同双方
    - 提取关键条款
    - 按章节分块
    """
    # 1️⃣ 使用 DeepDoc 解析
    sections, tables, _ = by_deepdoc(
        filename, binary, 
        from_page=0, to_page=1000,
        lang=lang, callback=callback
    )
    
    # 2️⃣ 合同特定处理
    res = []
    for section in sections:
        # 识别甲方乙方
        if "甲方" in section["text"]:
            res.append({
                "doc_type_kwd": "party_a",
                "content": section["text"]
            })
        elif "乙方" in section["text"]:
            res.append({
                "doc_type_kwd": "party_b", 
                "content": section["text"]
            })
        else:
            res.append({
                "doc_type_kwd": "text",
                "content": section["text"]
            })
    
    return res

# 2. 注册到解析器
# 在 rag/app/__init__.py 添加
from rag.app.contract import chunk as contract_chunk
```

### 9.3 集成新 Embedding 模型

```python
# 1. 在 rag/llm/embedding_model.py 添加

from rag.llm.base import BaseEmbedding

class MyEmbeddingModel(BaseEmbedding):
    _FACTORY_NAME = "MyEmbedding"
    
    def __init__(self, api_key, model_name="my-embedding-v1", **kwargs):
        self.api_key = api_key
        self.model_name = model_name
        # 初始化你的模型客户端
    
    def encode(self, texts, **kwargs):
        """文本向量化"""
        # 调用你的 Embedding API
        vectors = my_client.encode(texts)
        return vectors

# 2. 注册模型
EmbeddingModel["MyEmbedding"] = MyEmbeddingModel

# 3. 在前端或 API 中使用
# 设置 API Key 时选择 "MyEmbedding"
```

### 9.4 扩展对话能力

```python
# api/db/services/dialog_service.py

# 添加自定义对话模式

class DialogService:
    @classmethod
    async def async_chat_with_citation(cls, tenant_id, dialog_id, query, **kwargs):
        """
        带引用标注的对话模式
        """
        # 1️⃣ 检索相关片段
        chunks = await SearchService.search(
            query=query,
            kb_ids=dialog.kb_ids,
            topk=5
        )
        
        # 2️⃣ 构建带引用标注的 Prompt
        prompt = f"""
基于以下参考资料回答问题，每个回答标注出处：

参考资料：
{chr(10).join([f"[{i+1}] {c['content']}" for i, c in enumerate(chunks)])}

问题：{query}

请在回答中用 [编号] 标注参考来源。
"""
        
        # 3️⃣ 调用 LLM
        answer = await chat_model.async_chat(prompt)
        
        # 4️⃣ 格式化引用
        return cls._format_citation(answer, chunks)
```

### 9.5 关键配置项说明

```yaml
# conf/service_conf.yaml.template

# LLM 配置
LLM:
  model_source: "openai"  # openai | azure | ollama | 自定义
  api_key: ""             # API Key
  base_url: ""            # API Base URL
  
# Embedding 配置
Embedding:
  model: "BAAI/bge-large-zh-v1.5"
  dimension: 1024
  
# 向量存储配置
VectorStore:
  type: "elasticsearch"   # elasticsearch | infinity
  hosts: ["http://localhost:9200"]
  
# 文档存储配置
DocumentStore:
  type: "minio"
  endpoint: "localhost:9000"
  bucket: "ragflow"
  
# 缓存配置
Cache:
  type: "redis"
  host: "localhost"
  port: 6379
```

---

## 第十章：RAGFlow vs RAGFlow-Plus 对比

### 10.1 架构差异

| 维度 | RAGFlow | RAGFlow-Plus |
|------|---------|--------------|
| **开源协议** | Apache 2.0 | AGPLv3 |
| **前端** | React | Vue3 |
| **后台** | Flask (单服务) | Flask + 管理后台 |
| **文档解析** | DeepDoc | MinerU |
| **语言优化** | 通用 | 中文优先 |
| **权限体系** | 基础租户隔离 | 团队+角色+权限 |

### 10.2 功能差异

| 功能 | RAGFlow | RAGFlow-Plus |
|------|---------|--------------|
| 知识库管理 | ✅ 基础 | ✅ 增强 |
| 文档解析 | ✅ DeepDoc | ✅ MinerU |
| 多租户 | ✅ | ✅✅ 增强 |
| 权限控制 | ❌ | ✅ 团队+角色 |
| 管理后台 | ❌ | ✅ 独立后台 |
| 中文优化 | 一般 | 深度优化 |
| 图表检索 | ❌ | ✅ 支持 |

### 10.3 权限模型对比

**RAGFlow 基础权限**：
```
租户 (Tenant)
 └── 用户 (User)
      └── 知识库 (Knowledgebase) [私有/团队共享]
           └── 文档 (Document)
```

**RAGFlow-Plus 增强权限**：
```
系统 (System)
 └── 团队 (Team)
      ├── 角色 (Role) [管理员/成员/访客]
      └── 用户 (User) [可跨团队]
           └── 权限 (Permission)
                ├── 知识库级
                ├── 文档级
                └── 操作级 [读/写/删/管理]
```

### 10.4 文档解析引擎对比

| 维度 | DeepDoc (RAGFlow) | MinerU (RAGFlow-Plus) |
|------|------------------|----------------------|
| **开发者** | Infiniflow | MagicHub |
| **技术路线** | 规则+OCR | 深度学习模型 |
| **表格识别** | 好 | 更好 |
| **公式识别** | 一般 | 好 |
| **多语言** | 支持 | 支持 |
| **部署复杂度** | 低 | 高 (需要 GPU) |

### 10.5 二开建议

**选择 RAGFlow 的场景**：
- ✅ 需要保持 Apache 开源协议（商业友好）
- ✅ 部署简单为主
- ✅ 只需要基础的多租户隔离
- ✅ 对中文文档要求不是特别高

**选择 RAGFlow-Plus 的场景**：
- ✅ 需要完整的权限管理体系
- ✅ 中文文档为主，需要更好的解析效果
- ✅ 有 GPU 资源，可以运行 MinerU
- ✅ 需要管理后台
- ✅ 不介意 AGPL 协议（需要开源修改）

**混合方案**：
```
基于 RAGFlow 进行开发：
1. 使用 RAGFlow 的核心架构
2. 参考 RAGFlow-Plus 的权限设计
3. 根据需要引入 MinerU 的解析能力
```

---

## 附录：关键代码示例

### A.1 文档解析流程代码

```python
# 使用 DeepDoc 解析 PDF

from deepdoc.parser import PdfParser, PlainParser
from rag.nlp import rag_tokenizer

# 初始化解析器
parser = PdfParser()

# 解析 PDF
sections, tables = parser(
    "document.pdf",
    from_page=0,
    to_page=100,
    callback=lambda p, msg: print(f"{p:.1%} - {msg}")
)

# 打印结果
print(f"提取到 {len(sections)} 个文本块")
print(f"提取到 {len(tables)} 个表格")
```

### A.2 向量检索代码

```python
# 使用 rag 模块进行向量检索

from rag.nlp.search import Dealer
from api.db.services.llm_service import LLMBundle

# 初始化检索器
dealer = Dealer(dataStore)

# 获取 Embedding 模型
emb_model = LLMBundle(tenant_id, embedding_config)

# 执行检索
result = await dealer.search(
    req={
        "question": "公司的年假政策是什么？",
        "topk": 20,
        "size": 10
    },
    idx_names=[f"ragflow_{kb_id}"],
    kb_ids=[kb_id],
    emb_mdl=emb_model
)

print(f"检索到 {result.total} 个相关片段")
for chunk_id in result.ids[:5]:
    print(result.field[chunk_id]["content"][:100])
```

### A.3 LLM 调用代码

```python
# 调用 LLM 生成答案

from api.db.services.llm_service import LLMBundle
from rag.prompts.generator import kb_prompt

# 获取 Chat 模型
chat_model = LLMBundle(tenant_id, chat_config)

# 构建 Prompt
chunks = search_result["chunks"]
knowledge = kb_prompt({"chunks": chunks}, max_tokens=3000)

prompt = f"""基于以下知识回答问题：

{knowledge}

问题：{question}

回答："""

# 调用 LLM
response = await chat_model.async_chat(
    prompt,
    [{"role": "user", "content": prompt}],
    {"temperature": 0.3}
)

print(response)
```

---

## 总结

本文档对 RAGFlow 源码进行了深度解析，覆盖了：

1. **架构全景**：从整体架构到模块划分
2. **核心引擎**：DeepDoc 解析、RAG 检索、Agent 引擎
3. **API 接口**：完整的 RESTful API 说明
4. **二次开发**：新增解析器、集成模型、扩展功能
5. **选型建议**：RAGFlow vs RAGFlow-Plus 对比

**下一步建议**：
1. 克隆源码本地运行，理解系统全貌
2. 根据业务需求选择 RAGFlow 或 RAGFlow-Plus
3. 参考本文档进行二次开发
4. 关注官方 GitHub 获取最新动态

---

*文档生成时间：基于 RAGFlow 最新源码 (commit: 24af0875e)*

---

## 附录 B：常见问题与解决方案

### B.1 文档解析相关问题

#### 问题 1：PDF 解析失败

**症状**：上传 PDF 后，解析进度一直为 0

**排查步骤**：
```bash
# 1. 查看日志
docker compose logs -f ragflow-cpu | grep -i "parse\|error"

# 2. 检查文件格式
file document.pdf

# 3. 检查文件大小
ls -lh document.pdf

# 4. 检查 MinIO 存储
docker compose exec minio mc ls local/ragflow/
```

**常见原因**：
- 文件损坏或加密
- 文件过大（超过 100MB）
- PDF 版本不兼容

**解决方案**：
```python
# 方案1：使用 OCR 模式
parser_config = {
    "ocr": True,
    "ocr_lang": "ch",
    "pdf_parser": "deepdoc"
}

# 方案2：使用 naive 解析器
parser_config = {
    "pdf_parser": "naive"
}
```

#### 问题 2：表格识别不准确

**症状**：表格内容被错误拆分

**解决方案**：
```python
parser_config = {
    "table_row_count": 50,
    "table_instruction": "请保留表格结构",
    "layout_recognize": True
}
```

### B.2 向量检索相关问题

#### 问题 3：检索结果不相关

**排查步骤**：
```python
# 1. 检查 Embedding 模型
embedding_model = "BAAI/bge-large-zh-v1.5"

# 2. 检查检索参数
result = await dealer.search(
    req={
        "question": query,
        "topk": 20,
        "similarity_threshold": 0.1
    },
    ...
)

# 3. 启用 Re-ranking
rerank_id = "BAAI/bge-reranker-v2-m3"
```

#### 问题 4：向量检索超时

**解决方案**：
```yaml
# conf/service_conf.yaml
VectorStore:
  timeout: 30
  batch_size: 100
```

### B.3 LLM 调用相关问题

#### 问题 5：LLM 返回超时

**解决方案**：
```python
chat_config = {
    "timeout": 120,
    "max_retries": 3,
    "llm_id": "gpt-3.5-turbo"
}
```

#### 问题 6：API Key 无效

**解决方案**：
```python
# 在 RAGFlow UI 中重新配置
# 设置 -> LLM -> 添加新的 API Key

# 或者使用环境变量
export OPENAI_API_KEY="sk-..."
```

### B.4 性能优化建议

#### 优化 1：文档解析加速

```python
# 使用并发解析
async def parse_documents(documents):
    tasks = [parse_one(doc) for doc in documents]
    results = await asyncio.gather(*tasks)
    return results
```

#### 优化 2：向量检索加速

```python
# 使用批量检索
batch_size = 100
for i in range(0, len(queries), batch_size):
    batch = queries[i:i+batch_size]
    results = await dealer.batch_search(batch)
```

#### 优化 3：缓存优化

```python
# 启用 Redis 缓存
REDIS_CONN.set_obj("cache_key", data, expire=3600)
```

---

## 附录 C：源码目录索引

### C.1 核心文件快速定位

| 功能 | 文件路径 | 大小 | 说明 |
|------|---------|------|------|
| PDF 解析 | `deepdoc/parser/pdf_parser.py` | 85KB | 最大最复杂的解析器 |
| 分块策略 | `rag/app/naive.py` | 48KB | 最常用的分块方法 |
| 检索逻辑 | `rag/nlp/search.py` | 35KB | 核心检索算法 |
| API 入口 | `api/apps/restful_apis/document_api.py` | 71KB | 文档管理 API |
| 对话 API | `api/apps/restful_apis/chat_api.py` | 45KB | 对话管理 API |
| Agent 引擎 | `agent/canvas.py` | 34KB | Agent 流程编排 |
| 数据库模型 | `api/db/db_models.py` | 77KB | 所有数据库模型 |
| LLM 集成 | `rag/llm/__init__.py` | - | 模型工厂入口 |

### C.2 关键配置项

| 配置 | 位置 | 说明 |
|------|------|------|
| 服务配置 | `conf/service_conf.yaml.template` | 主配置文件 |
| 环境变量 | `docker/.env` | Docker 环境变量 |
| LLM 模型 | `rag/llm/__init__.py` | 支持的模型列表 |
| 解析器配置 | `api/db/init_data.py` | 默认解析器参数 |

---

## 附录 D：源码阅读建议

### D.1 推荐阅读顺序

对于初次接触 RAGFlow 的开发者，建议按以下顺序阅读源码：

1. **入门阶段**：
   - `README.md` - 项目概述
   - `docs/basics/` - 基础文档
   - `rag/app/naive.py` - 理解分块逻辑

2. **核心阶段**：
   - `rag/nlp/search.py` - 理解检索逻辑
   - `api/apps/restful_apis/` - 理解 API 设计
   - `api/db/db_models.py` - 理解数据模型

3. **进阶阶段**：
   - `deepdoc/parser/pdf_parser.py` - 理解文档解析
   - `agent/canvas.py` - 理解 Agent 编排
   - `rag/flow/pipeline.py` - 理解处理流程

### D.2 调试技巧

```python
# 1. 启用调试日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 2. 打印变量
print(f"DEBUG: {variable}")

# 3. 使用断点
import pdb; pdb.set_trace()
```

---

## 附录 E：版本演进历史

### E.1 主要版本特性

| 版本 | 时间 | 重要特性 |
|------|------|---------|
| v0.1 | 2024.03 | 初始版本发布 |
| v0.5 | 2024.06 | 支持 Agent 能力 |
| v0.8 | 2024.09 | 支持多种解析方法 |
| v0.10 | 2024.12 | 支持 MCP 协议 |
| v0.15 | 2025.03 | 支持 MinerU/Docling |
| v0.20 | 2025.06 | 支持 GraphRAG |
| v0.25 | 2025.09 | 支持 Agentic RAG |

### E.2 最新功能（2025年）

- ✅ 支持 Gemini 3 Pro
- ✅ 支持 GPT-5 系列
- ✅ 支持 Claude 4
- ✅ 支持 DeepSeek v4
- ✅ 支持 MCP Server
- ✅ 支持 Agentic Workflow
- ✅ 支持 Data Sync（Confluence, S3, Notion, Discord, Google Drive）

---

*文档生成时间：基于 RAGFlow 最新源码 (commit: 24af0875e)*

### E.3 技术路线图

根据 GitHub 提交记录和官方规划，RAGFlow 的发展方向包括：

1. **更强的文档理解**：引入更多 AI 模型提升解析质量
2. **多模态支持**：增强图片、视频理解能力
3. **实时同步**：支持更多数据源的实时同步
4. **企业级功能**：完善权限管理、审计日志等企业功能
5. **性能优化**：提升大规模数据处理能力

---

*文档完成 - 共 1968 行*
