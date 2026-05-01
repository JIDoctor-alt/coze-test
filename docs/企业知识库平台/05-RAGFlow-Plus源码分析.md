# RAGFlow-Plus源码分析

## 一、项目概览

### 1.1 项目信息

| 属性 | 信息 |
|------|------|
| GitHub地址 | https://github.com/zstar1003/ragflow-plus |
| 最新版本 | v0.5.0 (2025-08-10) |
| 开源协议 | AGPLv3 |
| 开发语言 | Python 46.4%, TypeScript 43.9%, Vue 6.4% |
| 提交次数 | 276+ commits |

### 1.2 项目定位

RAGFlow-Plus是RAGFlow的二次开发项目，定位为**中文应用场景的行业特解**，主要解决了RAG在实际企业应用中面临的"最后一公里"问题。

**核心改进方向：**
- 企业级权限管理体系
- 更强的文档解析能力
- 图文混合检索与输出
- 更友好的中文交互体验

---

## 二、系统架构分析

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAGFlow-Plus系统架构                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐              ┌─────────────────┐         │
│  │   前台系统       │              │   后台管理系统   │         │
│  │ ragflow-server  │              │ management-frontend│       │
│  │   (端口80)      │              │   (端口8888)    │         │
│  └────────┬────────┘              └────────┬────────┘         │
│           │                                │                   │
│           └────────────┬───────────────────┘                   │
│                        ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    management-backend                    │   │
│  │              (Flask + MinerU解析引擎)                  │   │
│  │                    (端口5000)                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                        │                                        │
├────────────────────────┼────────────────────────────────────────┤
│                        ▼                                        │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────────────┐   │
│  │  MySQL  │  Redis  │  MinIO  │   ES   │   vLLM推理服务   │   │
│  │ 数据库   │  缓存    │ 对象存储 │ 向量库  │   (可选GPU)     │   │
│  └─────────┴─────────┴─────────┴─────────┴─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 容器结构

| 容器名称 | 镜像 | 端口 | 内存占用 | 说明 |
|----------|------|------|----------|------|
| ragflowplus-server | ragflow | 80, 9380 | ~2GB | 前台主服务 |
| ragflowplus-management-frontend | management_web | 8888 | ~500MB | 后台前端 |
| ragflowplus-management-backend | management_server | 5000 | ~6GB | 后台后端(MinerU) |
| vllm-embedding | vllm | GPU | ~4GB | Embedding模型推理 |
| vllm-chat | vllm | GPU | ~4GB | Chat模型推理 |
| mysql | mysql:8.0 | 3306 | ~1GB | 关系数据库 |
| redis | redis | 6379 | ~200MB | 缓存服务 |
| es01 | elasticsearch | 9200 | ~2GB | 向量检索引擎 |
| minio | minio/minio | 9000 | ~500MB | 对象存储 |

**最低内存要求：12GB**（含GPU显存）

---

## 三、核心功能模块分析

### 3.1 后台管理系统（Management Module）

**技术栈：**
- 前端：Vue3 + TypeScript + v3-admin-vite
- 后端：Flask + SQLAlchemy

**功能模块：**

```
management/
├── user_mgmt/          # 用户管理
│   ├── user_controller.py
│   ├── user_service.py
│   └── user_model.py
├── team_mgmt/          # 团队管理
│   ├── team_controller.py
│   ├── team_service.py
│   └── team_model.py
├── kb_mgmt/            # 知识库管理
│   ├── kb_controller.py
│   ├── kb_service.py
│   └── kb_model.py
├── file_mgmt/          # 文件管理
│   ├── file_controller.py
│   ├── file_service.py
│   └── file_model.py
└── config_mgmt/        # 配置管理
    ├── model_config.py
    └── system_config.py
```

**权限层级设计：**
```
系统管理员
    └── 团队管理员
            └── 普通用户
                    └── 访客
```

### 3.2 用户权限体系实现

**数据库设计：**

```sql
-- 用户表
CREATE TABLE user (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(128) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    role ENUM('admin', 'team_admin', 'user', 'guest') DEFAULT 'user',
    team_id VARCHAR(36),
    status TINYINT DEFAULT 1,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 团队表
CREATE TABLE team (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    owner_id VARCHAR(36),
    settings JSON,
    created_at TIMESTAMP
);

-- 知识库权限表
CREATE TABLE kb_permission (
    id VARCHAR(36) PRIMARY KEY,
    kb_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36),
    team_id VARCHAR(36),
    permission ENUM('read', 'write', 'admin') DEFAULT 'read',
    created_at TIMESTAMP
);
```

**权限控制逻辑：**

```python
# rag/app.py - 权限验证装饰器
def require_permission(resource_type, permission_level):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = get_current_user_id()
            resource_id = kwargs.get('resource_id')
            
            if not check_permission(user_id, resource_type, resource_id, permission_level):
                raise PermissionDeniedError()
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

# 知识库访问权限检查
def check_kb_permission(user_id, kb_id, required_level):
    # 1. 检查是否为系统管理员
    if is_admin(user_id):
        return True
    
    # 2. 检查是否为知识库创建者
    if is_kb_creator(user_id, kb_id):
        return True
    
    # 3. 检查团队权限
    user_team = get_user_team(user_id)
    kb_team = get_kb_team(kb_id)
    if user_team == kb_team:
        return True
    
    # 4. 检查个人直接授权
    return check_direct_permission(user_id, kb_id, required_level)
```

### 3.3 数据隔离机制

**多租户数据隔离策略：**

```python
# rag/nlp/search.py - 检索时的数据隔离
class KnowledgeBaseSearch:
    def __init__(self, kb_id: str, user_id: str):
        self.kb_id = kb_id
        self.user_id = user_id
        self._validate_access()
    
    def _validate_access(self):
        """验证用户对知识库的访问权限"""
        kb = KnowledgeBaseService.get_by_id(self.kb_id)
        
        # 团队隔离
        if kb.tenant_id != get_user_tenant_id(self.user_id):
            raise AccessDeniedError("跨租户访问被拒绝")
        
        # 权限级别检查
        permission = get_user_kb_permission(self.user_id, self.kb_id)
        if permission < Permission.READ:
            raise AccessDeniedError("权限不足")

# MySQL连接时的租户过滤
class TenantQueryHelper:
    @staticmethod
    def apply_tenant_filter(query, user_id):
        tenant_id = get_user_tenant_id(user_id)
        return query.filter(
            or_(
                Model.tenant_id == tenant_id,
                Model.visibility == 'public'  # 公共知识库
            )
        )
```

---

## 四、MinerU解析引擎集成

### 4.1 MinerU vs DeepDoc对比

| 特性 | DeepDoc（原生） | MinerU（RAGFlow-Plus） |
|------|-----------------|------------------------|
| PDF解析 | 基于规则 | 基于模型 |
| 表格识别 | 基础 | 结构化还原 |
| 图片提取 | 简单提取 | 智能关联 |
| 中文排版 | 一般 | 优化良好 |
| OCR能力 | 内置基础 | 外接高精度OCR |
| 内存占用 | ~2GB | ~6GB |

### 4.2 MinerU集成架构

```python
# managementbackend/magic_pdf_parse.py
from magic_pdf.data.io import Reader2Dataset
from magic_pdf.model.PdfAnalyzeMode import PdfAnalyzeMode

class MinerUParser:
    def __init__(self, config_path: str = "/app/magic-pdf.json"):
        self.config = self._load_config(config_path)
    
    def parse_document(self, file_path: str, kb_id: str) -> ParseResult:
        """解析文档并返回结构化结果"""
        # 1. 读取文件
        doc_bytes = self._read_file(file_path)
        
        # 2. 预处理
        reader = Reader2Dataset(doc_bytes)
        
        # 3. 版面分析
        layout_result = self._analyze_layout(reader)
        
        # 4. 表格识别
        tables = self._extract_tables(layout_result)
        
        # 5. 图片提取与关联
        images = self._extract_and_link_images(layout_result)
        
        # 6. 文本提取
        text_blocks = self._extract_text(layout_result)
        
        # 7. 生成输出
        return ParseResult(
            blocks=text_blocks,
            tables=tables,
            images=images,
            metadata=self._generate_metadata()
        )
    
    def _extract_and_link_images(self, layout):
        """图片提取与文本关联"""
        images = []
        for img in layout.images:
            # 找到相邻文本块
            adjacent_text = self._find_adjacent_text(img.position, layout.text_blocks)
            
            images.append({
                'image_id': img.id,
                'image_path': img.storage_path,
                'position': img.position,
                'linked_text_blocks': [t.id for t in adjacent_text],
                'page_num': img.page_num
            })
        return images
```

### 4.3 解析配置

```json
// magic-pdf.json
{
    "model_list": [
        {
            "name": "uninet",
            "model_path": "/models/uninet",
            "device": "cuda"
        },
        {
            "name": "table",
            "model_path": "/models/table",
            "device": "cuda"
        }
    ],
    "parse_method": "ocr",  // ocr | txt
    "languages": ["chinese", "english"]
}
```

---

## 五、与原版RAGFlow的差异

### 5.1 功能差异对比

| 功能 | RAGFlow原版 | RAGFlow-Plus |
|------|-------------|--------------|
| 管理后台 | ❌ 无 | ✅ 独立后台系统 |
| 用户权限 | 基础（私有/团队） | 多级权限体系 |
| 文档解析 | DeepDoc | MinerU |
| 图片关联 | 基础 | 文本-图片深度绑定 |
| 文档撰写 | ❌ 无 | ✅ 文档模式 |
| 分词优化 | 简单split | 智能中文分词 |
| Excel解析 | 基础 | 独立解析管线 |
| 批量解析 | 并发（易卡住） | 串行（稳定） |

### 5.2 检索流程优化

RAGFlow-Plus对检索流程进行了多项优化：

```python
# rag/nlp/rag_tokenizer.py - 改进的分词器
class RAGTokenizer:
    def tokenize(self, text: str) -> List[str]:
        """改进的中文分词"""
        # 1. 预处理：全角转半角、繁转简
        text = self._preprocess(text)
        
        # 2. 按语言分段
        segments = self._split_by_language(text)
        
        # 3. 分段处理
        tokens = []
        for seg in segments:
            if self._is_chinese(seg):
                # 使用jieba分词
                tokens.extend(jieba.cut(seg))
            else:
                # 使用NLTK分词
                tokens.extend(word_tokenize(seg))
        
        # 4. 去停用词
        tokens = [t for t in tokens if not self._is_stopword(t)]
        
        return tokens

# rag/nlp/search.py - 检索权重优化
class HybridSearch:
    def search(self, query: str, kb_ids: List[str]):
        # 关键词检索（5%权重）
        keyword_results = self._keyword_search(query, kb_ids)
        
        # 向量检索（95%权重）
        vector_results = self._vector_search(query, kb_ids)
        
        # 融合排序
        return self._fusion_rank(keyword_results, vector_results, weights=[0.05, 0.95])
```

---

## 六、API设计

### 6.1 主要API端点

**前台系统API：**

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/datasets` | GET/POST | 知识库列表/创建 |
| `/api/v1/datasets/{id}` | GET/PUT/DELETE | 知识库CRUD |
| `/api/v1/datasets/{id}/documents` | POST | 上传文档 |
| `/api/v1/datasets/{id}/chunks` | GET | 获取解析块 |
| `/api/v1/retrieval` | POST | 检索测试 |
| `/api/v1/chats` | GET/POST | 对话管理 |
| `/api/v1/chats/{id}/chat` | POST | 发起对话 |

**后台管理API：**

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/admin/users` | GET/POST | 用户管理 |
| `/api/admin/users/{id}` | PUT/DELETE | 用户CRUD |
| `/api/admin/teams` | GET/POST | 团队管理 |
| `/api/admin/teams/{id}/members` | PUT | 团队成员管理 |
| `/api/admin/kb` | GET | 知识库管理 |
| `/api/admin/models` | GET/PUT | 模型配置 |
| `/api/admin/files` | GET/DELETE | 文件管理 |

### 6.2 权限验证

```python
# api/middleware/auth.py
class AuthMiddleware:
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        # 从请求头提取Token
        token = environ.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        
        if token:
            try:
                # 验证JWT
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                environ['user_id'] = payload['user_id']
                environ['tenant_id'] = payload['tenant_id']
                environ['role'] = payload['role']
            except jwt.ExpiredSignatureError:
                return self._unauthorized("Token已过期")
            except jwt.InvalidTokenError:
                return self._unauthorized("无效Token")
        
        return self.app(environ, start_response)

# 权限装饰器
def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(request, *args, **kwargs):
            if request.role not in roles:
                raise PermissionDeniedError(f"需要角色: {roles}")
            return f(request, *args, **kwargs)
        return wrapper
    return decorator
```

---

## 七、部署与配置

### 7.1 Docker Compose配置

```yaml
# docker/docker-compose.yml
version: '3.8'

services:
  ragflow:
    image: ${RAGFLOW_IMAGE}
    container_name: ragflowplus-server
    ports:
      - "${SVR_HTTP_PORT}:9380"
      - "80:80"
    volumes:
      - ./ragflow-logs:/ragflow/logs
    env_file: .env

  management-frontend:
    image: ${RAGFLOWPLUS_MANAGEMENT_WEB_IMAGE}
    container_name: ragflowplus-management-frontend
    ports:
      - "8888:80"

  management-backend:
    image: ${RAGFLOWPLUS_MANAGEMENT_SERVER_IMAGE}
    container_name: ragflowplus-management-backend
    ports:
      - "5000:5000"
    volumes:
      - ./magic-pdf.json:/root/magic-pdf.json
    environment:
      - MANAGEMENT_ADMIN_USERNAME=${MANAGEMENT_ADMIN_USERNAME:-admin}
      - MANAGEMENT_ADMIN_PASSWORD=${MANAGEMENT_ADMIN_PASSWORD:-12345678}
      - MANAGEMENT_JWT_SECRET=${MANAGEMENT_JWT_SECRET:-12345678}
```

### 7.2 环境变量配置

```bash
# .env
# RAGFlow配置
RAGFLOW_IMAGE=registry.cn-hangzhou.aliyuncs.com/infiniflow/ragflow:v0.15.0
SVR_HTTP_PORT=9380

# 后台管理系统
RAGFLOWPLUS_MANAGEMENT_WEB_IMAGE=registry.cn-hangzhou.aliyuncs.com/xxx/ragflow-plus-web:latest
RAGFLOWPLUS_MANAGEMENT_SERVER_IMAGE=registry.cn-hangzhou.aliyuncs.com/xxx/ragflow-plus-management:latest

# 管理员账户
MANAGEMENT_ADMIN_USERNAME=admin
MANAGEMENT_ADMIN_PASSWORD=YourSecurePassword123!
MANAGEMENT_JWT_SECRET=YourJWTSecretKey123!

# 时区
TIMEZONE=Asia/Shanghai
```

---

## 八、商业使用注意事项

### 8.1 许可证约束

**AGPLv3许可证要求：**

1. **衍生作品必须开源**：任何修改或组合的代码必须保持AGPLv3开源
2. **网络服务必须提供源码**：若作为网络服务提供，用户有权获取源码
3. **商用需谨慎**：
   - ✅ 允许：SaaS部署、企业内部使用
   - ✅ 允许：开源版本原样使用
   - ❌ 不允许：闭源商用（需获得所有版权持有人的书面授权）

### 8.2 依赖组件许可证

| 组件 | 许可证 | 注意事项 |
|------|--------|----------|
| RAGFlow | Apache 2.0 | 商业友好 |
| MinerU | AGPLv3 | 需开源衍生作品 |
| v3-admin-vite | MIT | 商业友好 |
| Vue | MIT | 商业友好 |

---

## 九、总结与建议

### 9.1 RAGFlow-Plus核心价值

| 改进点 | 对企业知识库的意义 |
|--------|-------------------|
| 后台管理系统 | 实现IT标准化管理，权限可控 |
| MinerU解析 | 文档解析质量提升，尤其是中文复杂排版 |
| 图文关联输出 | 技术文档、合同等场景更实用 |
| 数据隔离 | 多部门/多租户场景支持 |

### 9.2 技术选型建议

**适合采用RAGFlow-Plus的场景：**
- 需要多用户、多团队管理的知识库
- 文档包含大量表格、图片的技术文档
- 中文文档解析要求较高的场景
- 需要二次开发和定制的能力
- 愿意遵守AGPLv3开源协议

**可能需要额外工作的场景：**
- 超大规模部署（需优化向量检索性能）
- 完全闭源需求（需解决许可证问题）
- 移动端支持（目前主要Web端）

### 9.3 下一步建议

1. **深入代码层面**：参考项目文档 https://xdxsb.top/ragflow-plus/
2. **评估团队能力**：确认是否有能力进行AGPLv3合规管理
3. **原型验证**：先用Docker快速部署测试核心功能
4. **架构规划**：基于RAGFlow-Plus设计符合企业需求的扩展方案
