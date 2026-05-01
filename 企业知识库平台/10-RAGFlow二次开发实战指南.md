# RAGFlow-Plus 二次开发实战指南

> **📖 阅读说明**
> 
> 本指南专为基于 RAGFlow/RAGFlow-Plus 做企业级知识库平台二次开发的工程师编写。文档采用「精装房装修」类比，将复杂概念简单化，确保零基础开发者也能快速上手。
> 
> - **二开** = "买个精装房，按自己喜好重新装修"
> - **Docker** = "集装箱，把程序和所有依赖打包"
> - **API对接** = "两个系统之间打电话交流"
> - **GPU** = "图形加速卡，AI计算专用"
> - **热点地图** = "装修时最常改的地方标记出来"

---

## 目录

1. [开发环境搭建](#part-1-开发环境搭建)
2. [代码修改热点地图](#part-2-代码修改热点地图)
3. [关键接口对接指南](#part-3-关键接口对接指南)
4. [MinerU集成指南](#part-4-mineru集成指南)
5. [自定义开发实战](#part-5-自定义开发实战)
6. [部署与运维](#part-6-部署与运维)

---

# Part 1：开发环境搭建

## 1.1 Docker开发环境（完整开发栈）

> **🧠 概念解释**
> 
> Docker 就像「集装箱」，把 RAGFlow-Plus 需要的所有程序（Python 后端、Node.js 前端、MySQL 数据库、Redis 缓存等）全部打包成一个独立的环境。无论你的电脑是 Windows 还是 Linux，拿到这个集装箱就能直接运行。

### 1.1.1 前置条件检查

```bash
# 1. 检查 Docker 版本（必须 >= 24.0.0）
docker --version

# 2. 检查 Docker Compose 版本（必须 >= v2.26.1）
docker compose version

# 3. 检查系统参数（Elasticsearch 必须）
sysctl vm.max_map_count
# 输出应该 >= 262144

# 4. 如果不满足，执行以下命令（Linux）
sudo sysctl -w vm.max_map_count=262144

# 5. 永久生效（Linux）
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

### 1.1.2 克隆项目代码

```bash
# 克隆 RAGFlow-Plus 源码
git clone https://github.com/zstar1003/ragflow-plus.git
cd ragflow-plus

# 查看项目结构
ls -la
```

**RAGFlow-Plus 项目结构一览：**

```
ragflow-plus/
├── api/                    # 🐍 Python 后端服务（Quart 框架）
│   ├── apps/               # API 接口模块（*_app.py 文件）
│   ├── db/                 # 数据库操作（ORM）
│   └── ragflow_server.py   # 后端入口文件
├── web/                    # 🎨 前端项目（React + TypeScript）
├── management/            # 🖥️ 后台管理系统（Vue3 + Element Plus）
│   ├── server/            # 管理后台后端
│   └── web/              # 管理后台前端
├── deepdoc/               # 📄 文档解析引擎
├── rag/                   # 🔍 核心 RAG 逻辑
├── docker/                # 🐳 Docker 配置文件
│   ├── docker-compose.yml # 容器编排文件
│   ├── .env              # 环境变量配置
│   └── models/           # 本地模型存放目录
├── conf/                  # ⚙️ 配置文件
└── docs/                  # 📚 项目文档
```

### 1.1.3 一键启动完整开发环境

```bash
# 进入 docker 目录
cd docker

# 使用 docker-compose 启动所有服务
docker compose -f docker-compose.yml up -d

# 查看容器启动状态
docker compose -f docker-compose.yml ps

# 查看日志（确认启动成功）
docker logs -f ragflowplus-server
```

**启动成功的标志：**

```
 _______ ______ ______ ______ __
 / __ \ / | / ____// ____// /____ _ __
 / /_/ // /| | / __ / /_ / // __ \| | /| / /
 / _, _// ___ |/ /_/ // __/ / // /_/ /| |/ |/ /
 /_/ |_|/_/  |_|\____//_/ /_/ \____/ |__/|__/

 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:9380
```

### 1.1.4 访问系统

| 服务 | 访问地址 | 说明 |
|------|----------|------|
| 前台系统 | http://服务器IP:80 | 用户使用的知识库问答界面 |
| 后台管理系统 | http://服务器IP:8888 | 管理员使用的管理界面 |
| MinIO 控制台 | http://服务器IP:9001 | 对象存储管理（默认账号密码在 .env 中） |
| API 接口 | http://服务器IP:9380 | 开发者 API 入口 |

### 1.1.5 停止和清理

```bash
# 停止所有容器
docker compose -f docker-compose.yml down

# 停止并删除数据卷（⚠️ 会删除所有数据）
docker compose -f docker-compose.yml down -v
```

---

## 1.2 本地 IDE 配置

> **🧠 概念解释**
> 
> IDE（集成开发环境）就像「装修图纸工具箱」，帮助你更高效地编写、调试代码。

### 1.2.1 VS Code 配置（推荐）

**安装必要插件：**

```json
// .vscode/extensions.json - 推荐的插件列表
{
  "recommendations": [
    "ms-python.python",           // Python 支持
    "ms-python.vscode-pylance",  // Python 类型检查
    "ms-vscode.vscode-typescript-next", // TypeScript 支持
    "Vue.volar",                // Vue3 支持
    "esbenp.prettier-vscode",   // 代码格式化
    "chris-bently.gitlens",     // Git 可视化
    "ms-azuretools.vscode-docker" // Docker 支持
  ]
}
```

**Python 调试配置：**

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: 后端服务",
      "type": "debugpy",
      "request": "launch",
      "module": "quart",
      "args": ["-m", "ragflow_server"],
      "cwd": "${workspaceFolder}/api",
      "env": {
        "PYTHONPATH": "${workspaceFolder}",
        "FLASK_ENV": "development"
      },
      "console": "integratedTerminal"
    },
    {
      "name": "Python: 任务执行器",
      "type": "debugpy",
      "request": "launch",
      "module": "task_executor",
      "cwd": "${workspaceFolder}/api",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  ]
}
```

**IDE 设置：**

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/api/.venv/bin/python",
  "python.analysis.typeCheckingMode": "basic",
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "files.exclude": {
    "**/__pycache__": true,
    "**/.git": true,
    "**/node_modules": true
  }
}
```

### 1.2.2 PyCharm 配置

**配置步骤：**

1. **设置 Python 解释器**
   - `File` → `Settings` → `Project` → `Python Interpreter`
   - 选择 `Existing environment`，指向项目目录下的 `.venv`

2. **配置运行配置**
   - `Run` → `Edit Configurations`
   - 新建 `Python` 类型配置：
     - Script path: `api/ragflow_server.py`
     - Working directory: `${Project Root}`
     - Environment variables: 添加 `PYTHONPATH=${Project Root}`

3. **配置远程调试（可选）**
   - 如果需要调试 Docker 容器内的代码，使用 PyCharm 的 Docker 插件

---

## 1.3 前端开发环境

### 1.3.1 前台系统（React）

```bash
# 进入前端目录
cd web

# 安装依赖
npm install

# 启动开发服务器（热更新）
npm run dev
```

**技术栈说明：**

| 技术 | 用途 |
|------|------|
| React 18 | UI 框架 |
| TypeScript | 类型安全 |
| Vite | 构建工具 |
| Zustand | 状态管理 |
| Tailwind CSS | 样式框架 |
| TanStack Query | 数据请求 |

### 1.3.2 后台管理系统（Vue3）

```bash
# 进入管理后台前端目录
cd management/web

# 安装依赖
pnpm install

# 启动开发服务器
pnpm run dev
```

**技术栈说明：**

| 技术 | 用途 |
|------|------|
| Vue 3 | UI 框架 |
| Element Plus | 组件库 |
| Pinia | 状态管理 |
| Vue Router | 路由管理 |

### 1.3.3 前端目录结构

```
web/                          # 前台系统前端
├── src/
│   ├── api/                 # API 接口定义
│   │   ├── chat.ts         # 对话相关 API
│   │   ├── dataset.ts      # 知识库 API
│   │   └── document.ts     # 文档 API
│   ├── components/         # 公共组件
│   │   ├── Chat/          # 聊天组件
│   │   └── Document/      # 文档组件
│   ├── pages/              # 页面组件
│   ├── stores/             # Zustand 状态
│   └── utils/              # 工具函数
├── public/                  # 静态资源
└── package.json

management/web/               # 后台管理系统前端
├── src/
│   ├── api/                # API 接口
│   ├── views/              # 页面视图
│   ├── views/              # 页面视图
│   ├── router/             # 路由配置
│   ├── stores/             # Pinia 状态
│   └── styles/             # 样式文件
├── .env                     # 环境变量
└── package.json
```

---

## 1.4 源码开发环境（绕过 Docker）

> **💡 适用场景**
> 
> 如果你想直接在本地修改代码并运行，而不是每次修改后重新打包 Docker 镜像，可以使用源码开发模式。

### 1.4.1 后端源码开发

```bash
# 1. 安装 uv（Python 包管理工具）
pip install uv

# 2. 安装 Python 依赖
cd ragflow-plus
uv sync --python 3.12

# 3. 下载依赖模型
uv run python download_deps.py

# 4. 启动基础设施服务（MySQL、ES、Redis、MinIO）
docker compose -f docker/docker-compose-base.yml up -d

# 5. 添加 hosts 解析
echo "127.0.0.1 es01 mysql minio redis" | sudo tee -a /etc/hosts

# 6. 启动后端服务
source .venv/bin/activate
export PYTHONPATH=$(pwd)
bash docker/launch_backend_service.sh

# 7. 验证后端启动
curl http://localhost:9380/healthz
```

### 1.4.2 前端源码开发

```bash
# 前台系统
cd web
npm install
npm run dev  # 监听 8000 端口

# 后台管理系统
cd management/web
pnpm install
pnpm run dev  # 监听 5173 端口
```

---

## 1.5 数据库初始化

### 1.5.1 数据库连接信息

RAGFlow-Plus 使用以下数据库组件：

| 数据库 | 用途 | 默认端口 | 配置文件位置 |
|--------|------|----------|--------------|
| MySQL 8.0 | 元数据存储 | 3306 | docker/.env |
| Elasticsearch | 全文检索 + 向量存储 | 1200 | docker/.env |
| Redis (Valkey) | 缓存 + 任务队列 | 6379 | docker/.env |
| MinIO | 对象存储 | 9000 | docker/.env |

### 1.5.2 初始化脚本

首次启动时，MySQL 会自动执行初始化脚本：

```bash
# 查看初始化日志
docker logs ragflowplus-mysql 2>&1 | grep -i init

# 手动执行初始化（可选）
docker exec -i ragflowplus-mysql mysql -u root -p${MYSQL_PASSWORD} < docker/init.sql
```

### 1.5.3 常用数据库操作

```bash
# 连接 MySQL
docker exec -it ragflowplus-mysql mysql -u root -p

# 查看数据库
SHOW DATABASES;

# 使用 ragflow 数据库
USE ragflow;

# 查看用户表
SELECT id, email, nickname FROM user;

# 查看知识库表
SELECT id, name, tenant_id FROM knowledgebase;
```

---

## 1.6 调试配置

### 1.6.1 后端调试

**开启调试模式：**

```python
# 在 api/ragflow_server.py 中
import quart

app = quart.Quart(__name__)
app.debug = True  # 开启调试模式
```

**Docker 环境开启调试：**

```yaml
# docker/docker-compose.yml 中添加环境变量
environment:
  - FLASK_ENV=development
  - LOG_LEVEL=DEBUG
```

### 1.6.2 前端调试

**React DevTools：**
- 安装 Chrome 插件：`React Developer Tools`

**Vue DevTools：**
- 安装 Chrome 插件：`Vue.js devtools`

### 1.6.3 API 调试

```bash
# 获取 API Token
curl -X POST http://localhost:9380/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "your_password"}'

# 使用 Token 调用 API
curl http://localhost:9380/api/v1/datasets \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

# Part 2：代码修改热点地图

> **🧠 概念解释**
> 
> 热点地图就像「装修时最常改的地方」，告诉你二开时最可能需要修改的模块和文件。

## 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAGFlow-Plus 架构                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │   前台系统   │    │  后台管理系统  │    │   API 接口   │    │
│  │   (web/)    │    │ (management/) │    │   (api/)    │    │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    │
│         │                     │                     │            │
│  ┌──────▼─────────────────────▼─────────────────────▼───────┐  │
│  │                      核心业务逻辑层                          │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │  │
│  │  │  rag/   │  │deepdoc/ │  │ agent/  │  │graphrag/│    │  │
│  │  │ 检索生成 │  │文档解析  │  │  智能体  │  │ 知识图谱 │    │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                      数据存储层                          │  │
│  │  MySQL  │  Elasticsearch  │  Redis  │  MinIO        │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 2.2 后台管理系统新增功能

### 2.2.1 核心文件定位

| 功能模块 | 涉及文件 | 修改说明 |
|----------|----------|----------|
| 用户管理 | `management/server/src/models/user.py` | 用户数据模型 |
| | `management/server/src/routes/user.py` | 用户 API 路由 |
| | `management/server/src/services/user_service.py` | 用户业务逻辑 |
| 团队管理 | `management/server/src/models/team.py` | 团队数据模型 |
| | `management/server/src/routes/team.py` | 团队 API 路由 |
| 知识库管理 | `management/server/src/routes/dataset.py` | 知识库 API |
| 文件管理 | `management/server/src/routes/file.py` | 文件 API |
| 模型配置 | `management/server/src/routes/model.py` | 模型配置 API |
| 前端页面 | `management/web/src/views/*.vue` | Vue 页面组件 |

### 2.2.2 新增管理功能示例

**Step 1: 后端新增 API**

```python
# management/server/src/routes/custom_feature.py
from flask import Blueprint, request, jsonify
from ..services.custom_service import CustomService
from ..middleware.auth import admin_required

custom_bp = Blueprint('custom', __name__, url_prefix='/api/custom')

@custom_bp.route('/feature', methods=['POST'])
@admin_required
def create_feature():
    """创建自定义功能"""
    data = request.get_json()
    result = CustomService.create_feature(data)
    return jsonify({"code": 0, "data": result})

@custom_bp.route('/feature/<id>', methods=['GET'])
def get_feature(id):
    """获取功能详情"""
    result = CustomService.get_feature(id)
    return jsonify({"code": 0, "data": result})
```

**Step 2: 注册路由**

```python
# management/server/src/app.py
from .routes.custom_feature import custom_bp

def register_blueprints(app):
    app.register_blueprint(custom_bp)
```

**Step 3: 前端新增页面**

```vue
<!-- management/web/src/views/custom/Feature.vue -->
<template>
  <div class="custom-feature">
    <el-card>
      <template #header>
        <span>自定义功能</span>
      </template>
      <el-form :model="form" label-width="120px">
        <el-form-item label="功能名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submit">提交</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { createFeature } from '@/api/custom'

const form = reactive({
  name: ''
})

const submit = async () => {
  await createFeature(form)
}
</script>
```

**Step 4: 添加路由**

```typescript
// management/web/src/router/index.ts
{
  path: '/custom/feature',
  name: 'CustomFeature',
  component: () => import('@/views/custom/Feature.vue'),
  meta: { title: '自定义功能', requiresAdmin: true }
}
```

---

## 2.3 文档解析逻辑调整

### 2.3.1 核心文件定位

| 功能 | 文件路径 | 说明 |
|------|----------|------|
| PDF 解析 | `deepdoc/parser/pdf_parser.py` | PDF 解析入口 |
| Word 解析 | `deepdoc/parser/word_parser.py` | Word 解析 |
| Excel 解析 | `deepdoc/parser/excel_parser.py` | Excel 解析 |
| 布局识别 | `deepdoc/vision/layout_recognizer.py` | 视觉模型布局识别 |
| OCR 识别 | `deepdoc/vision/ocr.py` | 文字识别 |
| 表格识别 | `deepdoc/vision/table_structure_recognizer.py` | 表格结构识别 |
| 文本分块 | `rag/flow/chunker/` | 多种分块策略 |

### 2.3.2 解析流程图

```
用户上传文件
     │
     ▼
┌─────────────┐
│ 文件类型检测  │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│  PDF 解析   │────▶│  布局识别   │
└─────────────┘     └──────┬──────┘
       │                    │
       │              ┌─────▼─────┐
       │              │  OCR 识别 │
       │              └─────┬─────┘
       │                    │
       ▼              ┌─────▼─────┐
┌─────────────┐       │ 表格识别  │
│  Word 解析  │       └─────┬─────┘
└─────────────┘             │
       │              ┌─────▼─────┐
       │              │  文本分块  │
       │              └─────┬─────┘
       │                    │
       ▼              ┌─────▼─────┐
┌─────────────┐       │ Embedding │
│ Excel 解析  │       │ 向量生成   │
└─────────────┘       └─────┬─────┘
                             │
                       ┌─────▼─────┐
                       │ ES 存储   │
                       └───────────┘
```

### 2.3.3 自定义解析器示例

```python
# deepdoc/parser/custom_parser.py
from .base_parser import BaseParser
from pathlib import Path

class CustomParser(BaseParser):
    """自定义文档解析器示例"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.custom']
    
    def parse(self, file_path: str) -> dict:
        """
        解析自定义格式文档
        
        Args:
            file_path: 文件路径
            
        Returns:
            dict: 包含 text, tables, images 的字典
        """
        path = Path(file_path)
        
        # 1. 读取文件内容
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 2. 提取文本
        text_segments = self._extract_text(content)
        
        # 3. 提取表格（如果需要）
        tables = self._extract_tables(content)
        
        # 4. 提取图片（如果需要）
        images = self._extract_images(path)
        
        return {
            'text': text_segments,
            'tables': tables,
            'images': images,
            'metadata': {
                'file_name': path.name,
                'file_size': path.stat().st_size,
                'parser': 'custom_parser'
            }
        }
    
    def _extract_text(self, content: str) -> list:
        """提取文本段落"""
        # 实现自定义文本提取逻辑
        paragraphs = content.split('\n\n')
        return [{'text': p, 'bbox': None} for p in paragraphs if p.strip()]
    
    def _extract_tables(self, content: str) -> list:
        """提取表格数据"""
        # 实现自定义表格提取逻辑
        return []
    
    def _extract_images(self, path: Path) -> list:
        """提取图片"""
        # 实现自定义图片提取逻辑
        return []
```

---

## 2.4 对话能力增强

### 2.4.1 核心文件定位

| 功能 | 文件路径 | 说明 |
|------|----------|------|
| 对话入口 | `api/apps/chat_app.py` | 对话 API |
| 会话管理 | `api/apps/session_app.py` | 会话管理 |
| RAG 检索 | `rag/retrieval/` | 检索逻辑 |
| LLM 调用 | `rag/llm/` | 大模型封装 |
| Prompt 模板 | `rag/llm/` | 提示词管理 |
| 对话历史 | `rag/memory/` | 记忆模块 |

### 2.4.2 对话流程图

```
用户问题
    │
    ▼
┌─────────────────┐
│  问题预处理      │
│ (意图识别/改写)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  知识库检索      │
│ (向量+关键词)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  结果重排序      │
│   (Rerank)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Prompt 组装     │
│  + 历史上下文   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM 生成答案    │
│  + 引用标注      │
└────────┬────────┘
         │
         ▼
   返回用户答案
```

### 2.4.3 自定义对话模板

```python
# rag/llm/prompts/custom_template.py

CUSTOM_CHAT_TEMPLATE = """
【角色设定】
你是一个专业的{domain}领域助手，名为{name}。

【对话历史】
{history}

【检索到的参考内容】
{context}

【用户问题】
{question}

【回答要求】
1. 只根据参考内容回答，不要编造信息
2. 如果找不到答案，直接说明"我没有找到相关信息"
3. 回答要简洁、有条理
4. 需要标注参考来源，使用[来源]格式

【回答】
"""

def format_custom_prompt(
    question: str,
    context: list,
    history: str = "",
    domain: str = "通用",
    name: str = "小助手"
) -> str:
    """
    格式化自定义对话提示词
    
    Args:
        question: 用户问题
        context: 检索到的上下文
        history: 对话历史
        domain: 领域名称
        name: 助手名称
        
    Returns:
        str: 格式化后的提示词
    """
    context_str = "\n\n".join([
        f"[来源{i+1}] {item['text']}" 
        for i, item in enumerate(context)
    ])
    
    return CUSTOM_CHAT_TEMPLATE.format(
        domain=domain,
        name=name,
        history=history,
        context=context_str,
        question=question
    )
```

### 2.4.4 新增对话技能

```python
# rag/llm/skills/question_classifier.py

class QuestionClassifier:
    """问题分类器 - 增强对话理解能力"""
    
    def __init__(self):
        self.intent_keywords = {
            'factual': ['是什么', '什么是', '定义', '概念'],
            'procedural': ['怎么做', '如何', '方法', '步骤'],
            'comparative': ['区别', '比较', '不同', '差异'],
            'causal': ['为什么', '原因', '由于', '导致']
        }
    
    def classify(self, question: str) -> str:
        """
        识别问题类型
        
        Args:
            question: 用户问题
            
        Returns:
            str: 问题类型
        """
        question = question.lower()
        
        for intent, keywords in self.intent_keywords.items():
            if any(kw in question for kw in keywords):
                return intent
        
        return 'general'
    
    def get_response_strategy(self, intent: str) -> dict:
        """根据问题类型返回响应策略"""
        strategies = {
            'factual': {
                'prompt_type': 'definition',
                'max_context': 3,
                'temperature': 0.3
            },
            'procedural': {
                'prompt_type': 'instruction',
                'max_context': 5,
                'temperature': 0.5
            },
            'comparative': {
                'prompt_type': 'comparison',
                'max_context': 4,
                'temperature': 0.4
            },
            'causal': {
                'prompt_type': 'explanation',
                'max_context': 4,
                'temperature': 0.4
            },
            'general': {
                'prompt_type': 'general',
                'max_context': 3,
                'temperature': 0.7
            }
        }
        return strategies.get(intent, strategies['general'])
```

---

## 2.5 UI 定制

### 2.5.1 前台系统（web/）

| 定制内容 | 文件路径 | 修改说明 |
|----------|----------|----------|
| Logo | `web/public/` | 替换 logo.svg |
| 应用标题 | `web/src/conf.json` | 修改 appName |
| 登录页 | `web/src/pages/Login/` | 修改登录界面 |
| 主题色 | `web/src/styles/` | 修改 CSS 变量 |
| 组件样式 | `web/src/components/` | 修改组件 |

**修改 Logo 示例：**

```bash
# 1. 准备新的 logo 文件（SVG 格式）
# 2. 替换文件
cp your-logo.svg web/public/logo.svg

# 3. 修改应用标题
# web/src/conf.json
{
  "appName": "你的知识库名称",
  "version": "1.0.0"
}
```

**修改主题色示例：**

```css
/* web/src/styles/variables.css */
:root {
  /* 主色调 */
  --color-primary: #409EFF;      /* Element Plus 默认蓝 */
  --color-primary-light: #66b1ff;
  --color-primary-dark: #337ecc;
  
  /* 成功/警告/危险色 */
  --color-success: #67c23a;
  --color-warning: #e6a23c;
  --color-danger: #f56c6c;
  
  /* 背景色 */
  --bg-color: #ffffff;
  --bg-color-page: #f0f2f5;
}
```

### 2.5.2 后台管理系统（management/web/）

| 定制内容 | 文件路径 | 修改说明 |
|----------|----------|----------|
| Logo | `management/web/src/common/assets/images/layouts/` | 替换 logo 图片 |
| 应用标题 | `management/web/.env` | 修改 VITE_APP_TITLE |
| 主题色 | `management/web/src/styles/` | 修改 SCSS 变量 |
| 页面组件 | `management/web/src/views/` | 修改页面 |
| 水印 | `management/web/src/layouts/components/Footer/` | 移除或修改 |

**修改后台 Logo 示例：**

```bash
# 1. 替换 logo 文件
cp your-admin-logo.png management/web/src/common/assets/images/layouts/logo.png

# 2. 修改标题
# management/web/.env
VITE_APP_TITLE=你的管理系统名称

# 3. 移除水印
# management/web/src/layouts/components/Footer/index.vue
# 删除或注释水印相关代码
```

---

## 2.6 权限体系调整

### 2.6.1 权限相关文件

| 层级 | 文件路径 | 说明 |
|------|----------|------|
| 数据模型 | `api/db/db_models.py` | 权限相关数据表 |
| 权限服务 | `api/db/services/` | 权限检查逻辑 |
| 认证中间件 | `api/apps/auth/` | Token 验证 |
| API 装饰器 | `api/common/` | `@login_required` 等 |

### 2.6.2 权限模型设计

```python
# api/db/db_models.py - 权限相关模型

class Permission(Model):
    """权限表"""
    id = CharField(max_length=32, primary_key=True)
    name = CharField(max_length=64)           # 权限名称
    code = CharField(max_length=64, unique=True)  # 权限代码
    resource_type = CharField(max_length=32)  # 资源类型
    description = TextField(null=True)
    
class Role(Model):
    """角色表"""
    id = CharField(max_length=32, primary_key=True)
    name = CharField(max_length=64)
    description = TextField(null=True)
    is_system = BooleanField(default=False)   # 是否系统角色

class RolePermission(Model):
    """角色-权限关联表"""
    role_id = CharField(max_length=32)
    permission_id = CharField(max_length=32)
    
class UserRole(Model):
    """用户-角色关联表"""
    user_id = CharField(max_length=32)
    role_id = CharField(max_length=32)

class DatasetPermission(Model):
    """知识库级权限"""
    id = CharField(max_length=32, primary_key=True)
    dataset_id = CharField(max_length=32)
    user_id = CharField(max_length=32)
    permission_level = CharField(max_length=32)  # read/write/admin
```

### 2.6.3 权限检查装饰器

```python
# api/common/permission_decorators.py

from functools import wraps
from flask import jsonify

def require_permission(permission_code: str):
    """
    权限检查装饰器
    
    Args:
        permission_code: 所需权限代码
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 1. 检查用户是否登录
            if not current_user:
                return jsonify({"code": 401, "message": "未登录"})
            
            # 2. 检查用户是否具有所需权限
            if not PermissionService.check_user_permission(
                current_user.id, 
                permission_code
            ):
                return jsonify({"code": 403, "message": "权限不足"})
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_dataset_permission(level: str = 'read'):
    """
    知识库权限检查装饰器
    
    Args:
        level: 所需权限级别 (read/write/admin)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            dataset_id = kwargs.get('dataset_id')
            if not dataset_id:
                return jsonify({"code": 400, "message": "缺少知识库ID"})
            
            if not PermissionService.check_dataset_permission(
                current_user.id,
                dataset_id,
                level
            ):
                return jsonify({"code": 403, "message": "无权访问此知识库"})
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 使用示例
@router.route('/dataset/<dataset_id>', methods=['DELETE'])
@login_required
@require_dataset_permission('admin')
def delete_dataset(dataset_id):
    """删除知识库（需要管理员权限）"""
    pass
```

---

# Part 3：关键接口对接指南

## 3.1 API 认证和 Token 管理

### 3.1.1 获取 API Token

```python
# 方法 1: 使用用户名密码获取 Token
import requests

def get_token(base_url: str, email: str, password: str) -> str:
    """获取 API Token"""
    response = requests.post(
        f"{base_url}/api/v1/login",
        json={"email": email, "password": password}
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get('data', {}).get('token')
    else:
        raise Exception(f"登录失败: {response.text}")

# 使用
token = get_token("http://localhost:9380", "admin@example.com", "password")
```

```bash
# 方法 2: 使用 cURL
curl -X POST http://localhost:9380/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "your_password"}'
```

### 3.1.2 Token 管理最佳实践

```python
# api_client.py

import time
import requests
from typing import Optional

class RAGFlowClient:
    """RAGFlow API 客户端封装"""
    
    def __init__(self, base_url: str, email: str, password: str):
        self.base_url = base_url
        self.email = email
        self.password = password
        self._token: Optional[str] = None
        self._token_expires: float = 0
    
    @property
    def token(self) -> str:
        """获取 Token（自动续期）"""
        # 如果 Token 即将过期，自动刷新
        if not self._token or time.time() > self._token_expires - 300:
            self._refresh_token()
        return self._token
    
    def _refresh_token(self):
        """刷新 Token"""
        response = requests.post(
            f"{self.base_url}/api/v1/login",
            json={"email": self.email, "password": self.password}
        )
        
        if response.status_code == 200:
            data = response.json()
            self._token = data.get('data', {}).get('token')
            # 设置过期时间（假设 24 小时）
            self._token_expires = time.time() + 86400
        else:
            raise Exception(f"Token 刷新失败: {response.text}")
    
    def request(self, method: str, path: str, **kwargs) -> dict:
        """发送 API 请求"""
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {self.token}'
        
        response = requests.request(
            method,
            f"{self.base_url}{path}",
            headers=headers,
            **kwargs
        )
        
        return response.json()
    
    def get(self, path: str, **kwargs) -> dict:
        return self.request('GET', path, **kwargs)
    
    def post(self, path: str, **kwargs) -> dict:
        return self.request('POST', path, **kwargs)
    
    def put(self, path: str, **kwargs) -> dict:
        return self.request('PUT', path, **kwargs)
    
    def delete(self, path: str, **kwargs) -> dict:
        return self.request('DELETE', path, **kwargs)
```

---

## 3.2 知识库（Dataset）管理

### 3.2.1 创建知识库

```python
def create_dataset(
    client: RAGFlowClient,
    name: str,
    description: str = "",
    embedding_model: str = "BAAI/bge-large-zh-v1.5",
    chunk_method: str = "naive",
    language: str = "Chinese"
) -> dict:
    """
    创建知识库
    
    Args:
        client: RAGFlow 客户端
        name: 知识库名称
        description: 知识库描述
        embedding_model: 嵌入模型
        chunk_method: 分块方法
        language: 语言设置
        
    Returns:
        dict: 创建的知识库信息
    """
    payload = {
        "name": name,
        "description": description,
        "embedding_model": embedding_model,
        "chunk_method": chunk_method,
        "language": language,
        "permission": "me",  # me/team
        "parser_config": {
            "chunk_token_count": 128,
            "layout_recognize": True,
            "delimiter": "\\n!?。；！？"
        }
    }
    
    response = client.post("/api/v1/datasets", json=payload)
    return response.get('data', {})

# 使用示例
dataset = create_dataset(
    client=rag_client,
    name="企业知识库",
    description="存放企业内部文档",
    embedding_model="BAAI/bge-large-zh-v1.5",
    chunk_method="naive"
)
print(f"知识库 ID: {dataset['id']}")
```

```bash
# cURL 示例
curl -X POST http://localhost:9380/api/v1/datasets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "test_knowledge_base",
    "description": "测试知识库",
    "embedding_model": "BAAI/bge-large-zh-v1.5",
    "chunk_method": "naive",
    "language": "Chinese"
  }'
```

### 3.2.2 列出知识库

```python
def list_datasets(client: RAGFlowClient, page: int = 1, page_size: int = 50) -> list:
    """列出所有知识库"""
    params = {"page": page, "page_size": page_size}
    response = client.get("/api/v1/datasets", params=params)
    return response.get('data', {}).get('datasets', [])

# 使用示例
datasets = list_datasets(rag_client)
for ds in datasets:
    print(f"ID: {ds['id']}, Name: {ds['name']}")
```

### 3.2.3 删除知识库

```python
def delete_dataset(client: RAGFlowClient, dataset_id: str) -> bool:
    """删除知识库"""
    response = client.delete(f"/api/v1/datasets/{dataset_id}")
    return response.get('code') == 0

# 使用示例
delete_dataset(rag_client, "dataset_id_here")
```

---

## 3.3 文档上传和解析

### 3.3.1 上传文档

```python
def upload_document(
    client: RAGFlowClient,
    dataset_id: str,
    file_path: str,
    chunk_method: str = "naive"
) -> dict:
    """
    上传文档到知识库
    
    Args:
        client: RAGFlow 客户端
        dataset_id: 知识库 ID
        file_path: 本地文件路径
        chunk_method: 分块方法
        
    Returns:
        dict: 上传的文档信息
    """
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.split('/')[-1], f)}
        response = client.post(
            f"/api/v1/datasets/{dataset_id}/documents",
            files=files
        )
    
    return response.get('data', [{}])[0] if response.get('data') else {}

# 使用示例
doc_info = upload_document(
    rag_client,
    dataset_id="your_dataset_id",
    file_path="/path/to/document.pdf"
)
print(f"文档 ID: {doc_info.get('id')}")
```

```bash
# cURL 示例
curl -X POST http://localhost:9380/api/v1/datasets/{dataset_id}/documents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/your/document.pdf"
```

### 3.3.2 批量上传文档

```python
def upload_documents_batch(
    client: RAGFlowClient,
    dataset_id: str,
    file_paths: list
) -> list:
    """批量上传文档"""
    results = []
    
    for file_path in file_paths:
        try:
            result = upload_document(client, dataset_id, file_path)
            results.append({"path": file_path, "result": result, "success": True})
        except Exception as e:
            results.append({"path": file_path, "error": str(e), "success": False})
    
    return results

# 使用示例
files = [
    "/data/docs/manual.pdf",
    "/data/docs/guide.docx",
    "/data/docs/report.xlsx"
]
results = upload_documents_batch(rag_client, "dataset_id", files)
```

### 3.3.3 解析文档

```python
def parse_document(
    client: RAGFlowClient,
    dataset_id: str,
    document_ids: list
) -> dict:
    """
    解析文档
    
    Args:
        client: RAGFlow 客户端
        dataset_id: 知识库 ID
        document_ids: 文档 ID 列表
        
    Returns:
        dict: 解析任务信息
    """
    payload = {"document_ids": document_ids}
    response = client.post(
        f"/api/v1/datasets/{dataset_id}/chunks",
        json=payload
    )
    return response

# 使用示例
parse_result = parse_document(
    rag_client,
    dataset_id="your_dataset_id",
    document_ids=["doc_id_1", "doc_id_2"]
)
```

### 3.3.4 查询解析状态

```python
def get_parse_status(
    client: RAGFlowClient,
    dataset_id: str,
    document_id: str
) -> dict:
    """获取文档解析状态"""
    response = client.get(
        f"/api/v1/datasets/{dataset_id}/documents/{document_id}"
    )
    return response.get('data', {})

# 使用示例
import time

def wait_for_parsing(
    client: RAGFlowClient,
    dataset_id: str,
    document_id: str,
    timeout: int = 300
) -> bool:
    """等待文档解析完成"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status = get_parse_status(client, dataset_id, document_id)
        progress = status.get('progress', 0)
        print(f"解析进度: {progress}%")
        
        if status.get('run') == '1':
            return True
        elif status.get('run') == '-1':
            raise Exception(f"解析失败: {status.get('message', '未知错误')}")
        
        time.sleep(5)
    
    raise TimeoutError("解析超时")
```

---

## 3.4 对话接口

### 3.4.1 创建聊天会话

```python
def create_chat(
    client: RAGFlowClient,
    name: str,
    dataset_ids: list,
    llm_model: str = "gpt-4"
) -> dict:
    """
    创建聊天助手
    
    Args:
        client: RAGFlow 客户端
        name: 助手名称
        dataset_ids: 关联的知识库 ID 列表
        llm_model: LLM 模型
        
    Returns:
        dict: 聊天助手信息
    """
    payload = {
        "name": name,
        "dataset_ids": dataset_ids,
        "llm_model": llm_model,
        "top_n": 3,
        "rerank_model": "BAAI/bge-reranker-base",
        "temperature": 0.1,
        "prompt": {
            "similarity_threshold": 0.2,
            "keywords": True,
            "vector_similarity_weight": 0.3
        }
    }
    
    response = client.post("/api/v1/chats", json=payload)
    return response.get('data', {})

# 使用示例
chat = create_chat(
    rag_client,
    name="企业问答助手",
    dataset_ids=["dataset_id_1", "dataset_id_2"],
    llm_model="gpt-4"
)
print(f"聊天 ID: {chat['id']}")
```

### 3.4.2 发起对话

```python
def send_message(
    client: RAGFlowClient,
    chat_id: str,
    question: str,
    stream: bool = True
) -> dict:
    """
    发送消息并获取回复
    
    Args:
        client: RAGFlow 客户端
        chat_id: 聊天 ID
        question: 用户问题
        stream: 是否使用流式响应
        
    Returns:
        dict: 回复信息
    """
    # 1. 创建会话
    session_response = client.post(
        f"/api/v1/chats/{chat_id}/sessions",
        json={"name": "new_session"}
    )
    session_id = session_response.get('data', {}).get('id')
    
    # 2. 发送消息
    payload = {
        "question": question,
        "stream": stream
    }
    
    if stream:
        # 流式响应
        return stream_chat(client, chat_id, session_id, question)
    else:
        # 非流式响应
        response = client.post(
            f"/api/v1/chats/{chat_id}/completions",
            json={**payload, "session_id": session_id}
        )
        return response.get('data', {})

def stream_chat(client: RAGFlowClient, chat_id: str, session_id: str, question: str):
    """流式对话"""
    import sseclient
    
    response = requests.post(
        f"{client.base_url}/api/v1/chats/{chat_id}/completions",
        headers={'Authorization': f'Bearer {client.token}'},
        json={
            "question": question,
            "stream": True,
            "session_id": session_id
        },
        stream=True
    )
    
    # 处理 SSE 流
    client_response = sseclient.SSEClient(response)
    for event in client_response.events():
        if event.data:
            yield event.data
```

### 3.4.3 完整对话示例

```python
# complete_chat_example.py

import time

def complete_conversation_example():
    """完整对话流程示例"""
    
    # 1. 初始化客户端
    client = RAGFlowClient(
        base_url="http://localhost:9380",
        email="admin@example.com",
        password="your_password"
    )
    
    # 2. 获取知识库
    datasets = list_datasets(client)
    if not datasets:
        print("请先创建知识库")
        return
    
    dataset_id = datasets[0]['id']
    
    # 3. 创建聊天助手
    chat = create_chat(
        client,
        name="智能助手",
        dataset_ids=[dataset_id]
    )
    chat_id = chat['id']
    
    # 4. 开始对话
    questions = [
        "这个知识库包含哪些内容？",
        "如何上传新文档？",
        "支持哪些文件格式？"
    ]
    
    for question in questions:
        print(f"\n用户: {question}")
        print("助手: ", end="", flush=True)
        
        # 流式输出
        for chunk in stream_chat(client, chat_id, None, question):
            print(chunk, end="", flush=True)
        
        print("\n")
        time.sleep(1)

if __name__ == "__main__":
    complete_conversation_example()
```

---

## 3.5 用户权限代理

### 3.5.1 代理用户操作

```python
def proxy_user_operation(
    admin_client: RAGFlowClient,
    target_user_id: str,
    operation: str,
    **kwargs
) -> dict:
    """
    管理员代理用户操作
    
    Args:
        admin_client: 管理员客户端
        target_user_id: 目标用户 ID
        operation: 操作类型 (create_dataset, upload_file 等)
        **kwargs: 操作参数
        
    Returns:
        dict: 操作结果
    """
    # 构建代理请求
    payload = {
        "target_user_id": target_user_id,
        "operation": operation,
        "params": kwargs
    }
    
    response = admin_client.post("/api/v1/admin/proxy", json=payload)
    return response

# 使用示例
# 代理用户创建知识库
result = proxy_user_operation(
    admin_client,
    target_user_id="user_123",
    operation="create_dataset",
    name="代理创建的知识库"
)
```

### 3.5.2 权限继承检查

```python
def check_user_dataset_access(
    client: RAGFlowClient,
    user_id: str,
    dataset_id: str
) -> dict:
    """检查用户对知识库的访问权限"""
    response = client.get(
        f"/api/v1/permissions/check",
        params={"user_id": user_id, "dataset_id": dataset_id}
    )
    return response.get('data', {})

def grant_dataset_access(
    admin_client: RAGFlowClient,
    dataset_id: str,
    user_id: str,
    level: str = "read"
) -> bool:
    """
    授予用户知识库访问权限
    
    Args:
        admin_client: 管理员客户端
        dataset_id: 知识库 ID
        user_id: 用户 ID
        level: 权限级别 (read/write/admin)
    """
    payload = {
        "dataset_id": dataset_id,
        "user_id": user_id,
        "permission_level": level
    }
    
    response = admin_client.post("/api/v1/permissions/grant", json=payload)
    return response.get('code') == 0

# 使用示例
grant_dataset_access(
    admin_client,
    dataset_id="dataset_123",
    user_id="user_456",
    level="write"
)
```

---

# Part 4：MinerU 集成指南

## 4.1 MinerU 概述

> **🧠 概念解释**
> 
> MinerU 是上海人工智能实验室开源的高质量文档解析工具，能够将 PDF 等文档转换为 Markdown 和 JSON 格式。相比 RAGFlow 原生的 DeepDoc 解析器，MinerU 在表格识别、公式识别、图片处理等方面表现更优。

### 4.1.1 MinerU vs DeepDoc 对比

| 特性 | MinerU | DeepDoc |
|------|--------|---------|
| PDF 解析 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 表格识别 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 公式识别 | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 图片处理 | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 多语言 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 部署难度 | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 资源需求 | 较高（推荐 GPU） | 较低 |

---

## 4.2 MinerU 部署方式

### 4.2.1 Docker 部署（推荐）

```bash
# 1. 拉取 MinerU 镜像
docker pull opendatalab/mineru:sglang-latest

# 2. 下载模型（首次运行）
docker run --rm opendatalab/mineru:sglang-latest \
  mineru-models-download -s huggingface -m all

# 3. 启动服务
docker run -d \
  --name mineru-server \
  --gpus all \
  --shm-size 32g \
  -p 30000:30000 \
  --ipc=host \
  --restart always \
  -e MINERU_MODEL_SOURCE=local \
  opendatalab/mineru:sglang-latest \
  mineru-sglang-server --host 0.0.0.0 --port 30000

# 4. 验证服务
curl http://localhost:30000/health
```

### 4.2.2 Python 依赖部署

```bash
# 1. 创建虚拟环境
python -m venv mineru-env
source mineru-env/bin/activate  # Linux/Mac
# mineru-env\Scripts\activate  # Windows

# 2. 安装 MinerU
pip install -U "mineru[core]"

# 3. 下载模型
mineru-models-download -s huggingface -m all

# 4. 启动 API 服务
mineru-api --host 0.0.0.0 --port 8000

# 5. 验证
curl http://localhost:8000/docs
```

### 4.2.3 源码部署

```bash
# 1. 克隆源码
git clone https://github.com/opendatalab/MinerU.git
cd MinerU

# 2. 安装依赖
pip install -e ".[core]"

# 3. 下载模型
python scripts/download_models.py

# 4. 启动服务
python -m mineru.api.server
```

---

## 4.3 GPU 需求评估

### 4.3.1 不同场景的资源需求

| 场景 | 最低配置 | 推荐配置 | 并发能力 |
|------|----------|----------|----------|
| 个人/小团队 | RTX 3060 (12GB) | RTX 4090 (24GB) | 1-2 并发 |
| 中型企业 | RTX 4090 x1 | A100 40GB | 3-5 并发 |
| 大型企业 | A100 x2 或更多 | A100 80GB x2 | 10+ 并发 |

### 4.3.2 GPU 资源监控

```bash
# 查看 GPU 状态
nvidia-smi

# 实时监控 GPU 使用
watch -n 1 nvidia-smi

# 监控特定进程
nvidia-smi pmon -c 1
```

### 4.3.3 资源配置示例

```yaml
# docker-compose.yml 中添加 MinerU 服务
services:
  mineru:
    image: opendatalab/mineru:sglang-latest
    container_name: mineru-server
    ports:
      - "30000:30000"
    environment:
      - MINERU_MODEL_SOURCE=local
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    shm_size: '32gb'
    restart: unless-stopped
```

---

## 4.4 RAGFlow-Plus 中替换 DeepDoc

### 4.4.1 配置 MinerU 解析器

RAGFlow-Plus 已经内置了 MinerU 支持，只需要在后台管理系统中配置即可：

1. **登录后台管理系统** (http://服务器IP:8888)
2. **进入知识库管理** → **嵌入模型配置**
3. **配置 MinerU 解析服务地址**
4. **测试连接**

### 4.4.2 API 调用 MinerU

```python
# 直接调用 MinerU API
import requests

def parse_with_mineru(
    mineru_url: str,
    file_path: str,
    lang: str = "zh"
) -> dict:
    """
    使用 MinerU 解析文档
    
    Args:
        mineru_url: MinerU 服务地址
        file_path: 文件路径
        lang: 语言设置
        
    Returns:
        dict: 解析结果
    """
    with open(file_path, 'rb') as f:
        files = [('files', (file_path.split('/')[-1], f, 'application/pdf'))]
        data = {
            'lang_list': lang,
            'backend': 'pipeline',
            'parse_method': 'auto',
            'formula_enable': 'true',
            'table_enable': 'true',
            'return_md': 'true'
        }
        
        response = requests.post(
            f"{mineru_url}/file_parse",
            files=files,
            data=data
        )
    
    return response.json()

# 使用示例
result = parse_with_mineru(
    mineru_url="http://localhost:30000",
    file_path="/data/document.pdf",
    lang="zh"
)
```

---

## 4.5 解析效果对比测试

### 4.5.1 测试方法

```python
# test_parsing_comparison.py

import time
from pathlib import Path

def test_parsing_comparison():
    """解析效果对比测试"""
    
    test_files = [
        "/data/test/financial_report.pdf",
        "/data/test/technical_manual.pdf",
        "/data/test/contract.pdf",
        "/data/test/academic_paper.pdf"
    ]
    
    results = []
    
    for file_path in test_files:
        if not Path(file_path).exists():
            continue
        
        # 测试 DeepDoc
        start = time.time()
        deepdoc_result = parse_with_deepdoc(file_path)
        deepdoc_time = time.time() - start
        deepdoc_score = evaluate_parsing_quality(deepdoc_result)
        
        # 测试 MinerU
        start = time.time()
        mineru_result = parse_with_mineru("http://localhost:30000", file_path)
        mineru_time = time.time() - start
        mineru_score = evaluate_parsing_quality(mineru_result)
        
        results.append({
            'file': Path(file_path).name,
            'deepdoc': {'time': deepdoc_time, 'score': deepdoc_score},
            'mineru': {'time': mineru_time, 'score': mineru_score}
        })
    
    # 输出对比报告
    print("\n" + "="*60)
    print("解析效果对比报告")
    print("="*60)
    
    for r in results:
        print(f"\n文件: {r['file']}")
        print(f"  DeepDoc: 耗时 {r['deepdoc']['time']:.2f}s, 质量评分 {r['deepdoc']['score']:.2f}/100")
        print(f"  MinerU:  耗时 {r['mineru']['time']:.2f}s, 质量评分 {r['mineru']['score']:.2f}/100")
        
        winner = "MinerU" if r['mineru']['score'] > r['deepdoc']['score'] else "DeepDoc"
        print(f"  推荐: {winner}")

def evaluate_parsing_quality(result: dict) -> float:
    """评估解析质量（简化实现）"""
    # 实际项目中需要根据具体指标计算
    # 例如：表格识别率、公式识别率、文本完整度等
    return 75.0  # 示例返回值
```

### 4.5.2 评估指标

| 指标 | 说明 | 权重 |
|------|------|------|
| 文本准确率 | 提取文本与原文的匹配度 | 30% |
| 表格识别率 | 表格结构识别的完整度 | 25% |
| 公式识别率 | 数学公式识别的准确度 | 15% |
| 段落连贯性 | 段落边界划分的准确性 | 15% |
| 图片关联度 | 图片与文字的关联程度 | 15% |

---

# Part 5：自定义开发实战

## 5.1 新增自定义解析方法

### 5.1.1 解析器基类

```python
# rag/llm/parsers/base_parser.py

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class ParsedDocument:
    """解析后的文档数据结构"""
    content: str                    # 主文本内容
    chunks: List[str]              # 分块后的文本块
    tables: List[Dict]              # 提取的表格
    images: List[Dict]             # 提取的图片
    metadata: Dict                 # 元数据

class BaseParser(ABC):
    """文档解析器基类"""
    
    def __init__(self):
        self.supported_extensions: List[str] = []
    
    @abstractmethod
    def parse(self, file_path: str) -> ParsedDocument:
        """
        解析文档
        
        Args:
            file_path: 文件路径
            
        Returns:
            ParsedDocument: 解析结果
        """
        pass
    
    def can_parse(self, file_path: str) -> bool:
        """检查是否支持解析此文件"""
        ext = Path(file_path).suffix.lower()
        return ext in self.supported_extensions
    
    def chunk_text(self, text: str, chunk_size: int = 512) -> List[str]:
        """文本分块"""
        # 简单实现，可根据需求定制
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i+chunk_size])
            chunks.append(chunk)
        return chunks
```

### 5.1.2 注册自定义解析器

```python
# rag/llm/parsers/parser_registry.py

from typing import Dict, Type
from .base_parser import BaseParser

class ParserRegistry:
    """解析器注册表"""
    
    _parsers: Dict[str, Type[BaseParser]] = {}
    
    @classmethod
    def register(cls, name: str, parser_class: Type[BaseParser]):
        """注册解析器"""
        cls._parsers[name] = parser_class
    
    @classmethod
    def get_parser(cls, name: str) -> BaseParser:
        """获取解析器实例"""
        if name not in cls._parsers:
            raise ValueError(f"未找到解析器: {name}")
        return cls._parsers[name]()
    
    @classmethod
    def list_parsers(cls) -> list:
        """列出所有注册的解析器"""
        return list(cls._parsers.keys())

# 注册自定义解析器
from .custom_parser import CustomParser
ParserRegistry.register('custom', CustomParser)
```

---

## 5.2 集成新的 Embedding 模型

### 5.2.1 Embedding 模型抽象

```python
# rag/llm/embedding_model.py

from abc import ABC, abstractmethod
from typing import List
import numpy as np

class BaseEmbeddingModel(ABC):
    """Embedding 模型基类"""
    
    def __init__(self, model_name: str, dimension: int = 768):
        self.model_name = model_name
        self.dimension = dimension
    
    @abstractmethod
    def encode(self, texts: List[str]) -> np.ndarray:
        """
        将文本编码为向量
        
        Args:
            texts: 文本列表
            
        Returns:
            np.ndarray: 文本向量矩阵
        """
        pass
    
    @abstractmethod
    async def encode_async(self, texts: List[str]) -> np.ndarray:
        """异步编码"""
        pass
    
    def get_dimension(self) -> int:
        """获取向量维度"""
        return self.dimension
```

### 5.2.2 实现新模型

```python
# rag/llm/embedding/mymodel.py

from .base_embedding import BaseEmbeddingModel
import requests
import numpy as np

class MyEmbeddingModel(BaseEmbeddingModel):
    """自定义 Embedding 模型"""
    
    def __init__(self, model_name: str, api_url: str, api_key: str = None):
        super().__init__(model_name, dimension=1024)  # 根据实际模型设置维度
        self.api_url = api_url
        self.api_key = api_key
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """调用 API 获取文本向量"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json={"inputs": texts}
        )
        
        if response.status_code == 200:
            return np.array(response.json())
        else:
            raise Exception(f"Embedding API 调用失败: {response.text}")
    
    async def encode_async(self, texts: List[str]) -> np.ndarray:
        """异步调用"""
        import aiohttp
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                headers=headers,
                json={"inputs": texts}
            ) as response:
                result = await response.json()
                return np.array(result)
```

### 5.2.3 注册和使用

```python
# rag/llm/embedding/__init__.py

from .mymodel import MyEmbeddingModel
from .registry import EmbeddingModelRegistry

# 注册模型
EmbeddingModelRegistry.register('my-embedding-model', MyEmbeddingModel)

# 使用模型
model = EmbeddingModelRegistry.get('my-embedding-model')(
    model_name="my-embedding",
    api_url="http://localhost:8000/embed",
    api_key="your-api-key"
)

# 编码文本
texts = ["Hello world", "这是一段测试文本"]
vectors = model.encode(texts)
print(f"向量维度: {vectors.shape}")
```

---

## 5.3 新增对话模板

### 5.3.1 模板系统设计

```python
# rag/llm/prompts/template_manager.py

from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class PromptTemplate:
    """提示词模板"""
    name: str
    system_prompt: str
    user_template: str
    context_template: str
    
    def format(
        self,
        question: str,
        context: list,
        history: str = "",
        **kwargs
    ) -> Dict[str, str]:
        """
        格式化模板
        
        Returns:
            dict: 包含 'system' 和 'user' 键的字典
        """
        # 格式化上下文
        context_str = self._format_context(context)
        
        # 格式化用户问题
        user_content = self.user_template.format(
            question=question,
            context=context_str,
            history=history,
            **kwargs
        )
        
        return {
            "system": self.system_prompt,
            "user": user_content
        }
    
    def _format_context(self, context: list) -> str:
        """格式化上下文"""
        if not context:
            return "未找到相关参考内容"
        
        parts = []
        for i, item in enumerate(context, 1):
            source = item.get('source', '未知来源')
            text = item.get('text', '')
            parts.append(f"[{i}] 来源: {source}\n{text}")
        
        return "\n\n".join(parts)


class TemplateManager:
    """模板管理器"""
    
    def __init__(self):
        self._templates: Dict[str, PromptTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """加载默认模板"""
        # 通用问答模板
        self.register(PromptTemplate(
            name="default",
            system_prompt="你是一个知识库问答助手，请根据提供的参考内容回答用户问题。",
            user_template="参考内容:\n{context}\n\n用户问题: {question}\n\n请根据参考内容回答问题。",
            context_template=""
        ))
        
        # 详细回答模板
        self.register(PromptTemplate(
            name="detailed",
            system_prompt="你是一个专业的知识库助手，请提供详细、准确的回答。",
            user_template="""请根据以下参考内容回答问题，要求回答详细、有条理。

参考内容:
{context}

用户问题: {question}

请提供详细回答，并在回答中标明参考来源。""",
            context_template=""
        ))
    
    def register(self, template: PromptTemplate):
        """注册模板"""
        self._templates[template.name] = template
    
    def get(self, name: str) -> Optional[PromptTemplate]:
        """获取模板"""
        return self._templates.get(name)
    
    def list_templates(self) -> list:
        """列出所有模板"""
        return list(self._templates.keys())
```

### 5.3.2 使用自定义模板

```python
# 使用示例

manager = TemplateManager()

# 注册新模板
manager.register(PromptTemplate(
    name="legal",
    system_prompt="你是一个专业的法律顾问，请严谨、客观地回答法律问题。",
    user_template="""【法律参考】
{context}

【用户咨询】
{question}

【回答要求】
1. 回答应基于上述参考内容
2. 涉及具体法律条文时请注明
3. 如需进一步了解情况，请明确指出""",
    context_template=""
))

# 使用模板
template = manager.get("legal")
messages = template.format(
    question="劳动合同可以约定试用期多长？",
    context=[
        {"source": "劳动合同法", "text": "劳动合同期限三个月以上不满一年的，试用期不得超过一个月..."}
    ]
)

print(f"System: {messages['system']}")
print(f"User: {messages['user']}")
```

---

## 5.4 行级权限过滤

### 5.4.1 权限过滤中间件

```python
# rag/security/row_level_security.py

from typing import List, Callable, Any
from functools import wraps

class RowLevelSecurity:
    """行级权限安全控制"""
    
    def __init__(self):
        self._policies: dict = {}
    
    def register_policy(
        self,
        resource: str,
        filter_func: Callable[[str, dict], dict]
    ):
        """
        注册行级过滤策略
        
        Args:
            resource: 资源名称（如 'document', 'chunk'）
            filter_func: 过滤函数，接收 (user_id, query) 返回过滤后的查询条件
        """
        self._policies[resource] = filter_func
    
    def apply_filter(
        self,
        resource: str,
        user_id: str,
        query: dict
    ) -> dict:
        """应用行级过滤"""
        if resource not in self._policies:
            return query
        
        return self._policies[resource](user_id, query)


class DatasetPermissionFilter:
    """知识库级权限过滤器"""
    
    def __init__(self):
        self.rls = RowLevelSecurity()
        self._setup_policies()
    
    def _setup_policies(self):
        """设置权限策略"""
        
        # 文档访问策略
        self.rls.register_policy('document', self._filter_document)
        
        # 文本块访问策略
        self.rls.register_policy('chunk', self._filter_chunk)
    
    def _filter_document(self, user_id: str, query: dict) -> dict:
        """过滤文档查询"""
        # 获取用户可访问的知识库
        accessible_datasets = self._get_user_datasets(user_id)
        
        # 添加知识库过滤条件
        if 'dataset_id' not in query:
            query['dataset_id__in'] = accessible_datasets
        
        return query
    
    def _filter_chunk(self, user_id: str, query: dict) -> dict:
        """过滤文本块查询"""
        accessible_datasets = self._get_user_datasets(user_id)
        
        if 'dataset_id' not in query:
            query['dataset_id__in'] = accessible_datasets
        
        return query
    
    def _get_user_datasets(self, user_id: str) -> List[str]:
        """获取用户可访问的知识库列表"""
        # 从数据库获取用户权限
        from api.db.services import PermissionService
        return PermissionService.get_user_accessible_datasets(user_id)


# 使用装饰器
def row_level_filter(resource: str):
    """行级过滤装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取当前用户
            user_id = get_current_user_id()
            
            # 获取过滤器
            filter_instance = DatasetPermissionFilter()
            
            # 修改查询参数
            query = kwargs.get('query', {})
            filtered_query = filter_instance.rls.apply_filter(
                resource, user_id, query
            )
            kwargs['query'] = filtered_query
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 使用示例
@router.route('/api/v1/chunks', methods=['GET'])
@login_required
@row_level_filter('chunk')
def list_chunks(query: dict):
    """列出文本块（自动应用行级权限）"""
    chunks = ChunkService.query(**query)
    return {"data": chunks}
```

---

## 5.5 自定义前端主题

### 5.5.1 主题配置系统

```javascript
// web/src/theme/index.ts

export interface ThemeConfig {
  colors: {
    primary: string;
    secondary: string;
    success: string;
    warning: string;
    danger: string;
  };
  layout: {
    headerHeight: number;
    sidebarWidth: number;
    footerHeight: number;
  };
  typography: {
    fontFamily: string;
    fontSizeBase: number;
  };
}

export const defaultTheme: ThemeConfig = {
  colors: {
    primary: '#409EFF',
    secondary: '#909399',
    success: '#67C23A',
    warning: '#E6A23C',
    danger: '#F56C6C',
  },
  layout: {
    headerHeight: 60,
    sidebarWidth: 200,
    footerHeight: 50,
  },
  typography: {
    fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif',
    fontSizeBase: 14,
  },
};

export class ThemeManager {
  private currentTheme: ThemeConfig;

  constructor() {
    this.currentTheme = { ...defaultTheme };
  }

  applyTheme(theme: Partial<ThemeConfig>) {
    this.currentTheme = { ...this.currentTheme, ...theme };
    this.injectStyles();
  }

  private injectStyles() {
    const root = document.documentElement;
    
    // 应用颜色
    Object.entries(this.currentTheme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });
    
    // 应用布局
    Object.entries(this.currentTheme.layout).forEach(([key, value]) => {
      const cssVar = `--layout-${this.camelToKebab(key)}`;
      root.style.setProperty(cssVar, `${value}px`);
    });
    
    // 应用字体
    root.style.setProperty('--font-family', this.currentTheme.typography.fontFamily);
    root.style.setProperty('--font-size-base', `${this.currentTheme.typography.fontSizeBase}px`);
  }

  private camelToKebab(str: string): string {
    return str.replace(/([A-Z])/g, '-$1').toLowerCase();
  }
}
```

### 5.5.2 暗黑模式支持

```javascript
// web/src/theme/dark-mode.ts

export const darkTheme: ThemeConfig = {
  colors: {
    primary: '#409EFF',
    secondary: '#6f7681',
    success: '#3FB950',
    warning: '#d29922',
    danger: '#F85149',
  },
  layout: defaultTheme.layout,
  typography: defaultTheme.typography,
};

export function toggleDarkMode(enabled: boolean) {
  const themeManager = new ThemeManager();
  
  if (enabled) {
    themeManager.applyTheme(darkTheme);
    document.documentElement.classList.add('dark');
  } else {
    themeManager.applyTheme(defaultTheme);
    document.documentElement.classList.remove('dark');
  }
  
  // 保存用户偏好
  localStorage.setItem('darkMode', String(enabled));
}

export function initDarkMode() {
  const saved = localStorage.getItem('darkMode');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const enabled = saved ? saved === 'true' : prefersDark;
  
  toggleDarkMode(enabled);
}
```

---

# Part 6：部署与运维

## 6.1 生产环境 Docker 部署

### 6.1.1 生产环境配置

```yaml
# docker/docker-compose.prod.yml

version: '3.8'

services:
  # 前台服务
  ragflow:
    image: ${RAGFLOW_IMAGE}
    container_name: ragflow-prod-server
    restart: always
    ports:
      - "80:80"
      - "443:443"
      - "9380:9380"
    volumes:
      - ./ragflow-logs:/ragflow/logs
      - ./nginx/ragflow.conf:/etc/nginx/conf.d/ragflow.conf
      - ./nginx/proxy.conf:/etc/nginx/proxy.conf
    environment:
      - TZ=${TIMEZONE}
      - FLASK_ENV=production
      - LOG_LEVEL=INFO
    networks:
      - ragflow-prod
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # 管理后台前端
  management-frontend:
    image: ${MANAGEMENT_WEB_IMAGE}
    container_name: ragflow-prod-mgmt-frontend
    restart: always
    ports:
      - "8888:80"
    networks:
      - ragflow-prod

  # 管理后台后端
  management-backend:
    image: ${MANAGEMENT_SERVER_IMAGE}
    container_name: ragflow-prod-mgmt-backend
    restart: always
    ports:
      - "5000:5000"
    volumes:
      - ./ragflow-plus-logs:/app/logs
    environment:
      - FLASK_ENV=production
      - MANAGEMENT_JWT_SECRET=${JWT_SECRET}
    networks:
      - ragflow-prod

  # MySQL
  mysql:
    image: mysql:8.0
    container_name: ragflow-prod-mysql
    restart: always
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_PASSWORD}
      - MYSQL_DATABASE=ragflow
    volumes:
      - mysql-data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - ragflow-prod
    command: --max_connections=1000 --character-set-server=utf8mb4

  # Elasticsearch
  es01:
    image: elasticsearch:8.11.3
    container_name: ragflow-prod-es
    restart: always
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=true
      - ELASTIC_PASSWORD=${ES_PASSWORD}
    volumes:
      - es-data:/usr/share/elasticsearch/data
    networks:
      - ragflow-prod
    ulimits:
      memlock:
        soft: -1
        hard: -1

  # Redis
  redis:
    image: valkey/valkey:8
    container_name: ragflow-prod-redis
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD} --maxmemory 512mb
    volumes:
      - redis-data:/data
    networks:
      - ragflow-prod

  # MinIO
  minio:
    image: pgsty/minio:RELEASE.2026-03-25T00-00-00Z
    container_name: ragflow-prod-minio
    restart: always
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=${MINIO_USER}
      - MINIO_ROOT_PASSWORD=${MINIO_PASSWORD}
    volumes:
      - minio-data:/data
    networks:
      - ragflow-prod

networks:
  ragflow-prod:
    driver: bridge

volumes:
  mysql-data:
  es-data:
  redis-data:
  minio-data:
```

### 6.1.2 环境变量配置

```bash
# docker/.env.prod

# ==================== 基础配置 ====================
TIMEZONE=Asia/Shanghai

# ==================== MySQL ====================
MYSQL_PASSWORD=your_secure_mysql_password_here
MYSQL_PORT=3306
EXPOSE_MYSQL_PORT=5455

# ==================== Elasticsearch ====================
STACK_VERSION=8.11.3
ES_PORT=1200
ELASTIC_PASSWORD=your_secure_es_password_here

# ==================== Redis ====================
REDIS_PORT=6379
REDIS_PASSWORD=your_secure_redis_password_here

# ==================== MinIO ====================
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001
MINIO_USER=your_minio_user
MINIO_PASSWORD=your_secure_minio_password_here

# ==================== RAGFlow ====================
SVR_HTTP_PORT=9380
RAGFLOW_IMAGE=infiniflow/ragflow:v0.24.0

# ==================== 管理后台 ====================
MANAGEMENT_WEB_IMAGE=ragflow-plus/management-web:latest
MANAGEMENT_SERVER_IMAGE=ragflow-plus/management-server:latest
MANAGEMENT_ADMIN_USERNAME=admin
MANAGEMENT_ADMIN_PASSWORD=your_admin_password
MANAGEMENT_JWT_SECRET=your_very_long_jwt_secret_key_here

# ==================== HuggingFace ====================
HF_ENDPOINT=https://hf-mirror.com
```

### 6.1.3 启动命令

```bash
# 1. 备份生产数据（如果是升级）
./scripts/backup.sh

# 2. 拉取最新镜像
docker compose -f docker/docker-compose.prod.yml pull

# 3. 停止旧服务
docker compose -f docker/docker-compose.prod.yml down

# 4. 启动新服务
docker compose -f docker/docker-compose.prod.yml up -d

# 5. 检查服务状态
docker compose -f docker/docker-compose.prod.yml ps

# 6. 查看日志
docker compose -f docker/docker-compose.prod.yml logs -f
```

---

## 6.2 资源需求评估

### 6.2.1 硬件配置推荐

| 规模 | 用户数 | CPU | 内存 | 存储 | GPU | 说明 |
|------|--------|-----|------|------|-----|------|
| 小型 | ≤50 | 8 核 | 32GB | 500GB | RTX 3060 (可选) | 单机部署 |
| 中型 | 50-200 | 16 核 | 64GB | 1TB | RTX 4090 | 单机部署 |
| 大型 | 200-500 | 32 核 | 128GB | 2TB | A100 40GB | 分离部署 |
| 超大型 | 500+ | 64+ 核 | 256GB+ | 5TB+ | A100 80GB x2+ | 集群部署 |

### 6.2.2 资源监控脚本

```bash
#!/bin/bash
# scripts/monitor_resources.sh

echo "========== 系统资源监控 =========="
echo "时间: $(date)"
echo ""

echo "--- CPU 和内存 ---"
top -bn1 | head -5

echo ""
echo "--- 磁盘使用 ---"
df -h | grep -E "^/dev"

echo ""
echo "--- Docker 容器资源 ---"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

echo ""
echo "--- GPU 状态 ---"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv
else
    echo "GPU 未检测到"
fi
```

---

## 6.3 性能调优

### 6.3.1 数据库优化

```sql
-- MySQL 优化配置 (my.cnf)

[mysqld]
# 连接优化
max_connections = 1000
wait_timeout = 600

# 缓存优化
innodb_buffer_pool_size = 4G
query_cache_size = 256M

# 日志优化
innodb_log_file_size = 1G
innodb_flush_log_at_trx_commit = 2

# 字符集
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
```

### 6.3.2 Elasticsearch 优化

```json
// 索引模板优化配置
{
  "index_patterns": ["ragflow_*"],
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "refresh_interval": "5s",
      "index.mapping.total_fields.limit": 2000
    },
    "mappings": {
      "properties": {
        "text_vector": {
          "type": "dense_vector",
          "dims": 1024,
          "index": true,
          "similarity": "cosine"
        }
      }
    }
  }
}
```

### 6.3.3 应用层优化

```python
# rag/retrieval/optimized_retriever.py

class OptimizedRetriever:
    """优化后的检索器"""
    
    def __init__(self):
        self.cache_enabled = True
        self.cache_ttl = 3600  # 缓存 1 小时
        self.batch_size = 100  # 批量处理大小
    
    async def retrieve_with_cache(
        self,
        query: str,
        dataset_ids: list,
        top_k: int = 10
    ) -> list:
        """带缓存的检索"""
        cache_key = f"retrieve:{hashlib.md5(f'{query}:{dataset_ids}'.encode()).hexdigest()}"
        
        # 尝试从缓存获取
        cached = await self._get_cache(cache_key)
        if cached:
            return cached
        
        # 执行检索
        results = await self._do_retrieve(query, dataset_ids, top_k)
        
        # 写入缓存
        await self._set_cache(cache_key, results, ttl=self.cache_ttl)
        
        return results
```

---

## 6.4 备份恢复

### 6.4.1 备份脚本

```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/data/backups/ragflow"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="ragflow_backup_${DATE}"

mkdir -p ${BACKUP_DIR}

echo "开始备份 RAGFlow..."

# 1. 备份 MySQL
echo "备份 MySQL..."
docker exec ragflow-prod-mysql mysqldump -u root -p${MYSQL_PASSWORD} ragflow > ${BACKUP_DIR}/${BACKUP_NAME}_mysql.sql

# 2. 备份 Elasticsearch
echo "备份 Elasticsearch..."
curl -u elastic:${ELASTIC_PASSWORD} "http://localhost:1200/_snapshot/ragflow_backup/snapshot_${DATE}" \
  -X PUT -H 'Content-Type: application/json' -d '{"indices": "ragflow_*}'

# 3. 备份 MinIO 数据
echo "备份 MinIO..."
docker run --rm \
  -v minio-data:/data \
  -v ${BACKUP_DIR}:/backup \
  alpine tar czf /backup/${BACKUP_NAME}_minio.tar.gz -C /data .

# 4. 备份配置文件
echo "备份配置文件..."
cp -r docker/.env ${BACKUP_DIR}/${BACKUP_NAME}_env
cp -r docker/nginx ${BACKUP_DIR}/${BACKUP_NAME}_nginx

# 5. 清理旧备份（保留最近 7 天）
find ${BACKUP_DIR} -mtime +7 -delete

echo "备份完成: ${BACKUP_DIR}/${BACKUP_NAME}*"
```

### 6.4.2 恢复脚本

```bash
#!/bin/bash
# scripts/restore.sh

BACKUP_DIR="/data/backups/ragflow"
BACKUP_NAME=$1

if [ -z "$BACKUP_NAME" ]; then
  echo "用法: $0 <backup_name>"
  echo "可用备份:"
  ls -1 ${BACKUP_DIR} | grep .sql
  exit 1
fi

echo "警告: 此操作将覆盖现有数据！"
read -p "确认恢复? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "取消恢复"
  exit 0
fi

# 1. 停止服务
docker compose -f docker/docker-compose.prod.yml down

# 2. 恢复 MySQL
echo "恢复 MySQL..."
docker exec -i ragflow-prod-mysql mysql -u root -p${MYSQL_PASSWORD} ragflow < ${BACKUP_DIR}/${BACKUP_NAME}_mysql.sql

# 3. 恢复 MinIO
echo "恢复 MinIO..."
docker run --rm \
  -v minio-data:/data \
  -v ${BACKUP_DIR}:/backup \
  alpine tar xzf /backup/${BACKUP_NAME}_minio.tar.gz -C /data

# 4. 恢复配置文件
echo "恢复配置..."
cp ${BACKUP_DIR}/${BACKUP_NAME}_env docker/.env
cp -r ${BACKUP_DIR}/${BACKUP_NAME}_nginx docker/nginx

# 5. 启动服务
docker compose -f docker/docker-compose.prod.yml up -d

echo "恢复完成！"
```

---

## 6.5 监控告警

### 6.5.1 监控指标

| 指标类别 | 具体指标 | 告警阈值 |
|----------|----------|----------|
| 系统 | CPU 使用率 | > 80% |
| 系统 | 内存使用率 | > 85% |
| 系统 | 磁盘使用率 | > 90% |
| 应用 | API 响应时间 | > 3s |
| 应用 | 错误率 | > 5% |
| 应用 | 队列积压 | > 1000 |
| 数据库 | MySQL 连接数 | > 800 |
| 数据库 | 查询延迟 | > 500ms |

### 6.5.2 Prometheus 配置

```yaml
# monitoring/prometheus.yml

global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ragflow'
    static_configs:
      - targets: ['ragflow:9380']
    metrics_path: '/metrics'

  - job_name: 'mysql'
    static_configs:
      - targets: ['mysql-exporter:9104']

  - job_name: 'elasticsearch'
    static_configs:
      - targets: ['es-exporter:9114']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### 6.5.3 告警规则

```yaml
# monitoring/alerts.yml

groups:
  - name: ragflow_alerts
    rules:
      - alert: HighCPUUsage
        expr: cpu_usage_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CPU 使用率过高"
          description: "服务器 {{ $labels.instance }} CPU 使用率已超过 80%"

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "服务不可用"
          description: "服务 {{ $labels.job }} 已宕机超过 1 分钟"

      - alert: HighResponseTime
        expr: api_response_time_seconds > 3
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "API 响应时间过长"
          description: "API 平均响应时间超过 3 秒"
```

---

# 附录

## A. 常见问题 FAQ

### Q1: Docker 镜像拉取失败怎么办？

```bash
# 配置国内镜像源
# /etc/docker/daemon.json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}

# 重启 Docker
sudo systemctl restart docker
```

### Q2: 如何查看容器日志？

```bash
# 查看所有容器状态
docker compose -f docker/docker-compose.yml ps

# 查看特定容器日志
docker logs -f ragflowplus-server

# 查看最近 100 行日志
docker logs --tail 100 ragflowplus-server
```

### Q3: 知识库解析失败怎么排查？

1. 检查文档格式是否支持
2. 查看解析日志：`docker logs ragflowplus-server | grep -i parse`
3. 检查磁盘空间是否充足
4. 确认嵌入模型是否正常配置

### Q4: API 返回 401 未授权？

```python
# 确保请求包含正确的 Token
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
```

## B. 参考资源

- **RAGFlow 官方文档**: https://ragflow.io/docs/
- **RAGFlow-Plus 项目**: https://github.com/zstar1003/ragflow-plus
- **MinerU 文档**: https://github.com/opendatalab/MinerU
- **Python SDK**: https://github.com/infiniflow/ragflow-sdk-python

## C. 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0.0 | 2025-01 | 初始版本 |

---

> **📝 文档说明**
> 
> 本文档由 AI 助手基于 RAGFlow/RAGFlow-Plus 源码分析生成，旨在帮助开发者快速上手二次开发。文档会持续更新，如有问题或建议，欢迎提交 Issue。
>
> 最后更新: 2025 年 1 月
