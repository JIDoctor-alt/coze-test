# Enterprise Knowledge Base Platform

企业级知识库平台，基于 RAGFlow 进行二次开发，支持多租户、RBAC+ABAC 混合权限模型和行级权限控制。

## 功能特性

### 核心功能
- 🚀 **多租户支持**：完整的租户隔离和数据隔离
- 🔐 **RBAC+ABAC 混合权限**：支持角色权限和属性权限的精细化控制
- 📄 **文档管理**：支持多种格式文档的上传、解析和检索
- 🔍 **RAG 智能问答**：基于向量检索和 LLM 的智能问答能力
- 🛡️ **行级权限控制**：文档级别的权限过滤，保护敏感数据

### 权限模型

```
RBAC (基于角色)
    └── 用户 → 角色 → 权限
    
ABAC (基于属性)
    └── 用户属性 + 资源属性 + 环境属性 → 访问决策
```

#### 预定义角色
| 角色 | 说明 |
|------|------|
| super_admin | 超级管理员，拥有系统所有权限 |
| tenant_admin | 租户管理员，管理租户内所有资源 |
| kb_admin | 知识库管理员，管理指定知识库 |
| editor | 编辑者，上传和编辑文档 |
| viewer | 查看者，仅可查看文档 |
| guest | 访客，仅可查看公开内容 |

#### 行级权限属性
- **部门(department)**：按部门过滤文档访问
- **项目(project)**：按项目过滤文档访问
- **安全等级(security_level)**：public < internal < confidential < secret

## 项目结构

```
企业知识库平台/
├── src/
│   ├── api/                    # API接口
│   │   └── v1/
│   │       └── endpoints/       # 接口端点
│   │           ├── auth.py      # 认证接口
│   │           ├── users.py     # 用户管理
│   │           ├── knowledge_bases.py  # 知识库管理
│   │           └── documents.py # 文档管理
│   ├── core/                   # 核心模块
│   │   ├── auth/               # 认证模块
│   │   ├── config/             # 配置模块
│   │   ├── db/                 # 数据库模块
│   │   └── security/           # 安全模块（权限控制）
│   │       └── row_permission.py  # 行级权限过滤器
│   ├── models/                 # 数据模型
│   │   ├── tenant.py           # 租户
│   │   ├── user.py             # 用户
│   │   ├── knowledge_base.py   # 知识库
│   │   ├── document.py         # 文档
│   │   ├── permission.py       # 权限
│   │   └── role.py             # 角色
│   ├── schemas/                # Pydantic Schema
│   ├── services/               # 业务服务层
│   └── utils/                  # 工具模块
├── scripts/                    # 脚本
│   ├── init_db.sql             # 数据库初始化SQL
│   └── init_db.py              # Python初始化脚本
├── requirements.txt            # 依赖包
├── .env.example                # 环境变量示例
└── README.md
```

## 快速开始

### 环境要求

- Python 3.10+
- PostgreSQL 15+
- Redis 7+
- Elasticsearch 8.x (可选，用于向量检索)

### 1. 安装依赖

```bash
cd 企业知识库平台
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

### 3. 初始化数据库

#### 方式一：使用 SQL 脚本

```bash
psql -U postgres -d kb_db -f scripts/init_db.sql
```

#### 方式二：使用 Python 脚本

```bash
python scripts/init_db.py
```

### 4. 启动服务

```bash
# 开发模式
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8080

# 生产模式
uvicorn src.api.app:app --host 0.0.0.0 --port 8080 --workers 4
```

### 5. 访问服务

- API 文档：http://localhost:8080/docs
- 管理界面：http://localhost:8080/

### 默认账号

- 用户名：admin
- 密码：admin123

⚠️ **请在首次登录后立即修改密码！**

## API 接口

### 认证接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/auth/login` | POST | 用户登录 |
| `/api/v1/auth/register` | POST | 用户注册 |

### 用户管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/users/me` | GET | 获取当前用户信息 |
| `/api/v1/users/` | GET | 获取用户列表 |
| `/api/v1/users/{id}` | GET | 获取用户详情 |
| `/api/v1/users/` | POST | 创建用户 |
| `/api/v1/users/{id}` | PUT | 更新用户 |
| `/api/v1/users/{id}` | DELETE | 删除用户 |

### 知识库管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/kb/` | GET | 获取知识库列表 |
| `/api/v1/kb/{id}` | GET | 获取知识库详情 |
| `/api/v1/kb/` | POST | 创建知识库 |
| `/api/v1/kb/{id}` | PUT | 更新知识库 |
| `/api/v1/kb/{id}` | DELETE | 删除知识库 |
| `/api/v1/kb/permission` | POST | 分配权限 |
| `/api/v1/kb/{id}/permission/{user_id}` | DELETE | 撤销权限 |

### 文档管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/docs/` | GET | 获取文档列表 |
| `/api/v1/docs/{id}` | GET | 获取文档详情 |
| `/api/v1/docs/` | POST | 上传文档 |
| `/api/v1/docs/{id}` | PUT | 更新文档 |
| `/api/v1/docs/{id}` | DELETE | 删除文档 |
| `/api/v1/docs/{id}/status` | GET | 获取解析状态 |

## 行级权限使用示例

### Python 代码中使用

```python
from src.core.security.row_permission import RowPermissionFilter

# 创建权限过滤器
row_filter = RowPermissionFilter(db)

# 获取用户属性
user_attrs = row_filter.get_user_attributes(current_user)

# 构建文档查询过滤条件
filters = row_filter.build_document_filters(user_attrs, kb_id)

# 应用过滤
query = query.filter(and_(*filters))
```

### 向量检索时使用

```python
# 构建向量库检索的权限过滤
es_filters = row_filter.build_vector_search_filters(user_attrs, kb_ids)

# 在Elasticsearch查询中使用
{
    "query": {
        "bool": {
            "must": [
                {"vector": {"embedding": [...]}},
                es_filters
            ]
        }
    }
}
```

## 部署

### Docker Compose 部署

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/kb
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
```

### 阿里云部署

参考 [系统设计方案](./02-系统设计方案.md) 中的部署架构章节。

## 开发指南

### 代码规范

- 使用 Black 格式化代码
- 使用 isort 排序导入
- 遵循 PEP 8 规范

### 测试

```bash
pytest tests/
```

## 许可证

Proprietary - All Rights Reserved

## 参考项目

- [RAGFlow](https://github.com/infiniflow/ragflow)
- [RAGFlow-Plus](https://github.com/zstar1003/ragflow-plus)
- [MinerU](https://github.com/opendatalab/MinerU)
