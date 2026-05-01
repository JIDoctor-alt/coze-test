# RAGFlow 企业知识库平台部署与运维手册

> **文档版本**: v1.0  
> **目标版本**: RAGFlow v0.25+ / RAGFlow-Plus v0.5+  
> **目标读者**: 企业IT运维工程师、系统架构师  
> **最后更新**: 2026年1月

---

## 零基础概念速成（必读）

在开始部署之前，让我们用生活中的比喻来理解这些专业术语：

| 专业术语 | 生活比喻 | 零基础解释 |
|---------|---------|-----------|
| **Docker** | 集装箱 | 把程序和它的"行李"（依赖库）打包成一个标准箱子，无论在哪里都能统一运输和运行 |
| **容器编排** | 码头调度员 | 一堆集装箱堆在一起，需要有人协调哪个先开、哪个后开，这就是"编排" |
| **负载均衡** | 多个窗口排队 | 银行开10个窗口，排队的人分散到各个窗口，速度就快了 |
| **高可用** | 备用车制度 | 一辆车坏了，备用车上，乘客不耽误行程 |
| **灾备** | 数据保险箱 | 把重要文件复印一份放在不同地方，火灾也不怕 |
| **向量数据库** | 智能书架 | 不是按书名找书，而是按"内容相似度"找书 |

---

## 目录

- [第一章：Docker部署详解](#第一章docker部署详解)
- [第二章：阿里云部署方案](#第二章阿里云部署方案)
- [第三章：生产环境配置](#第三章生产环境配置)
- [第四章：数据备份与恢复](#第四章数据备份与恢复)
- [第五章：监控与告警](#第五章监控与告警)
- [第六章：扩容与高可用](#第六章扩容与高可用)
- [附录：故障排查与常见问题](#附录故障排查与常见问题)

---

## 第一章：Docker部署详解

### 1.1 Docker核心概念（小白版）

**Docker = 集装箱标准化运输系统**

想象你要开一家餐厅：
- **传统方式**：在每个城市临时建厨房、买锅碗瓢盆、安装煤气管道...耗时耗力
- **Docker方式**：把整个厨房打包进集装箱，到哪个城市就用这个集装箱，省时省力

RAGFlow就是用Docker把以下"厨房设备"打包：
- Python后端服务（炒菜的大厨）
- React前端界面（餐厅门面）
- MySQL数据库（食材仓库账本）
- Elasticsearch向量库（智能书架系统）
- Redis缓存（临时工作台）
- MinIO文件存储（大冰箱）

### 1.2 系统要求与前置检查

#### 1.2.1 硬件要求

```
┌─────────────────────────────────────────────────────────────┐
│                    RAGFlow 硬件需求对照表                      │
├───────────────┬──────────────┬──────────────┬───────────────┤
│    场景       │    最小配置   │    推荐配置   │    高性能配置  │
├───────────────┼──────────────┼──────────────┼───────────────┤
│   开发测试     │  4核CPU      │  8核CPU       │  16核CPU       │
│               │  16GB内存    │  32GB内存     │  64GB内存      │
│               │  100GB磁盘   │  200GB磁盘    │  500GB磁盘     │
├───────────────┼──────────────┼──────────────┼───────────────┤
│   小规模生产   │  8核CPU      │  16核CPU      │  32核CPU       │
│  (<100用户)   │  32GB内存    │  64GB内存     │  128GB内存     │
│               │  500GB SSD  │  1TB SSD     │  2TB SSD      │
│               │  -           │  GPU可选      │  NVIDIA T4    │
├───────────────┼──────────────┼──────────────┼───────────────┤
│   中规模生产   │  16核CPU     │  32核CPU      │  64核CPU       │
│ (100-500用户) │  64GB内存    │  128GB内存    │  256GB内存     │
│               │  1TB SSD     │  2TB SSD     │  4TB SSD      │
│               │  NVIDIA T4   │  NVIDIA A10   │  NVIDIA A100  │
├───────────────┼──────────────┼──────────────┼───────────────┤
│   大规模生产   │  32核CPU     │  64核CPU      │  多节点集群    │
│ (>500用户)    │  128GB内存   │  256GB内存    │  按需扩展      │
│               │  2TB SSD    │  4TB SSD     │  分布式存储    │
│               │  NVIDIA A10  │  多卡A100    │  Kubernetes   │
└───────────────┴──────────────┴──────────────┴───────────────┘
```

#### 1.2.2 软件要求

```bash
# 1. 检查 Docker 版本（必须 >= 24.0.0）
docker --version
# 输出示例: Docker version 24.0.7, build afdd53b

# 2. 检查 Docker Compose 版本（必须 >= v2.26.1）
docker compose version
# 输出示例: Docker Compose version v2.26.1

# 3. 检查系统参数（Elasticsearch 必须）
sysctl vm.max_map_count
# 输出应该 >= 262144

# 4. 如果不满足，执行以下命令（Linux）
sudo sysctl -w vm.max_map_count=262144

# 5. 永久生效（Linux）
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

### 1.3 docker-compose.yml 完整解析

#### 1.3.1 RAGFlow 官方版 docker-compose 结构

```
ragflow/
├── docker/
│   ├── docker-compose.yml          # 主配置文件（服务定义）
│   ├── docker-compose-base.yml     # 基础设施配置（MySQL/ES/Redis/MinIO）
│   ├── .env                       # 环境变量配置
│   ├── service_conf.yaml.template  # 服务配置模板
│   ├── entrypoint.sh              # 启动脚本
│   └── ragflow-logs/             # 日志目录
```

#### 1.3.2 docker-compose.yml 详解（RAGFlow版）

```yaml
# ============================================================
# RAGFlow docker-compose.yml 完整解析
# ============================================================

# 使用 include 语法引用基础设施配置
include:
  - ./docker-compose-base.yml  # 引用基础服务配置

services:
  # ============================================
  # RAGFlow CPU 版本服务
  # ============================================
  ragflow-cpu:
    # 依赖关系：必须等 MySQL 健康检查通过后才启动
    depends_on:
      mysql:
        condition: service_healthy
    
    # 容器profile：使用 "docker compose --profile cpu up" 启动
    profiles:
      - cpu
    
    # Docker镜像配置
    image: ${RAGFLOW_IMAGE}
    # 官方镜像: infiniflow/ragflow:v0.25.1
    # 阿里云镜像: registry.cn-hangzhou.aliyuncs.com/infiniflow/ragflow:v0.25.1
    # 华为云镜像: swr.cn-north-4.myhuaweicloud.com/infiniflow/ragflow:v0.25.1
    
    # 启动命令配置
    command:
      - --enable-adminserver  # 启用管理服务器
    
    # 端口映射（主机端口:容器端口）
    ports:
      - ${SVR_WEB_HTTP_PORT}:80          # Web UI (默认80)
      - ${SVR_WEB_HTTPS_PORT}:443        # HTTPS (默认443)
      - ${SVR_HTTP_PORT}:9380            # API Server (默认9380)
      - ${ADMIN_SVR_HTTP_PORT}:9381      # Admin Server (默认9381)
      - ${SVR_MCP_PORT}:9382            # MCP Server (默认9382)
      - ${GO_HTTP_PORT}:9384            # Go HTTP (默认9384)
      - ${GO_ADMIN_PORT}:9383           # Go Admin (默认9383)
    
    # 数据卷挂载（主机目录:容器目录）
    volumes:
      - ./ragflow-logs:/ragflow/logs                    # 日志目录
      - ./service_conf.yaml.template:/ragflow/conf/service_conf.yaml.template  # 配置模板
      - ./entrypoint.sh:/ragflow/entrypoint.sh          # 启动脚本
    
    # 环境变量文件
    env_file:
      - .env
    
    # Docker网络
    networks:
      - ragflow
    
    # 重启策略：unless-stopped = 除非手动停止，否则自动重启
    restart: unless-stopped
    
    # 主机 hosts 映射（让容器能访问主机）
    extra_hosts:
      - "host.docker.internal:host-gateway"

  # ============================================
  # RAGFlow GPU 版本服务
  # ============================================
  ragflow-gpu:
    depends_on:
      mysql:
        condition: service_healthy
    profiles:
      - gpu
    image: ${RAGFLOW_IMAGE}
    command:
      - --enable-adminserver
    
    ports:
      - ${SVR_WEB_HTTP_PORT}:80
      - ${SVR_WEB_HTTPS_PORT}:443
      - ${SVR_HTTP_PORT}:9380
      - ${ADMIN_SVR_HTTP_PORT}:9381
      - ${SVR_MCP_PORT}:9382
      - ${GO_HTTP_PORT}:9384
      - ${GO_ADMIN_PORT}:9383
    
    volumes:
      - ./ragflow-logs:/ragflow/logs
      - ./service_conf.yaml.template:/ragflow/conf/service_conf.yaml.template
      - ./entrypoint.sh:/ragflow/entrypoint.sh
    
    env_file:
      - .env
    
    networks:
      - ragflow
    
    restart: unless-stopped
    
    extra_hosts:
      - "host.docker.internal:host-gateway"
    
    # GPU 配置（关键差异！）
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all              # 使用所有GPU
              capabilities: [gpu]    # GPU加速能力

# 网络定义
networks:
  ragflow:
    driver: bridge  # 桥接网络，容器间互通
```

#### 1.3.3 docker-compose-base.yml 详解（基础设施服务）

```yaml
# ============================================================
# docker-compose-base.yml - 基础设施服务配置
# ============================================================

services:
  # ============================================
  # Elasticsearch 向量数据库
  # ============================================
  es01:
    profiles:
      - elasticsearch  # 使用 --profile elasticsearch 启动
    
    image: elasticsearch:${STACK_VERSION}  # 默认 8.11.3
    
    volumes:
      - esdata01:/usr/share/elasticsearch/data  # 数据持久化
    
    ports:
      - ${ES_PORT}:9200  # 默认1200:9200
    
    environment:
      - node.name=es01
      - ELASTIC_PASSWORD=${ELASTIC_PASSWORD}
      - bootstrap.memory_lock=false
      - discovery.type=single-node  # 单节点模式
      - xpack.security.enabled=true
      - xpack.security.http.ssl.enabled=false
      - xpack.security.transport.ssl.enabled=false
      # 磁盘水位线（防止磁盘写满）
      - cluster.routing.allocation.disk.watermark.low=5gb
      - cluster.routing.allocation.disk.watermark.high=3gb
      - cluster.routing.allocation.disk.watermark.flood_stage=2gb
    
    # 内存限制
    mem_limit: ${MEM_LIMIT}  # 在.env中定义，默认约8GB
    
    # Linux内核限制
    ulimits:
      memlock:
        soft: -1
        hard: -1
    
    # 健康检查
    healthcheck:
      test: ["CMD-SHELL", "curl http://localhost:9200"]
      interval: 10s
      timeout: 10s
      retries: 120  # 最多重试120次（约20分钟）
    
    networks:
      - ragflow
    
    restart: unless-stopped

  # ============================================
  # Infinity 向量数据库（轻量替代方案）
  # ============================================
  infinity:
    profiles:
      - infinity
    
    image: infiniflow/infinity:v0.7.0-dev5
    
    volumes:
      - infinity_data:/var/infinity
      - ./infinity_conf.toml:/infinity_conf.toml  # 自定义配置
    
    command: ["-f", "/infinity_conf.toml"]
    
    ports:
      - ${INFINITY_THRIFT_PORT}:23817
      - ${INFINITY_HTTP_PORT}:23820
      - ${INFINITY_PSQL_PORT}:5432
    
    mem_limit: ${MEM_LIMIT}
    
    # 文件描述符限制（高并发必需）
    ulimits:
      nofile:
        soft: 500000
        hard: 500000
    
    healthcheck:
      test: ["CMD", "curl", "http://localhost:23820/admin/node/current"]
      interval: 10s
      timeout: 10s
      retries: 120
    
    networks:
      - ragflow
    
    restart: unless-stopped

  # ============================================
  # MySQL 数据库
  # ============================================
  mysql:
    image: mysql:8.4.2
    
    volumes:
      - mysql_data:/var/lib/mysql
      - ./mysql/conf:/etc/mysql/conf.d  # 自定义配置
    
    ports:
      - ${EXPOSE_MYSQL_PORT:-3306}:3306
    
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_PASSWORD}
      - MYSQL_DATABASE=${MYSQL_DBNAME}
    
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
      - --max_connections=1000
      - --max_allowed_packet=${MYSQL_MAX_PACKET}
    
    mem_limit: 2g
    
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 10s
      retries: 120
    
    networks:
      - ragflow
    
    restart: unless-stopped

  # ============================================
  # MinIO 对象存储
  # ============================================
  minio:
    image: minio/minio:latest
    
    volumes:
      - minio_data:/data
    
    ports:
      - ${MINIO_PORT}:9000        # API端口
      - ${MINIO_CONSOLE_PORT}:9001  # 控制台端口
    
    environment:
      - MINIO_ROOT_USER=${MINIO_USER}
      - MINIO_ROOT_PASSWORD=${MINIO_PASSWORD}
    
    command: ["server", "--console-address", ":9001", "/data"]
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3
    
    networks:
      - ragflow
    
    restart: unless-stopped

  # ============================================
  # Redis 缓存
  # ============================================
  redis:
    image: valkey/valkey:8  # Redis 8.0 兼容版本
    
    command:
      - "redis-server"
      - "--requirepass"
      - "${REDIS_PASSWORD}"
      - "--maxmemory=128mb"
      - "--maxmemory-policy=allkeys-lru"  # 内存满时删除所有key
    
    ports:
      - ${REDIS_PORT}:6379
    
    volumes:
      - redis_data:/data
    
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 10s
      retries: 120
    
    networks:
      - ragflow
    
    restart: unless-stopped

  # ============================================
  # TEI Embedding 服务（CPU版）
  # ============================================
  tei-cpu:
    profiles:
      - tei-cpu
    
    image: ${TEI_IMAGE_CPU}
    hostname: tei
    
    ports:
      - ${TEI_PORT:-6380}:80
    
    networks:
      - ragflow
    
    command:
      - "--model-id"
      - "/data/${TEI_MODEL}"
      - "--auto-truncate"
    
    restart: unless-stopped

  # ============================================
  # TEI Embedding 服务（GPU版）
  # ============================================
  tei-gpu:
    profiles:
      - tei-gpu
    
    image: ${TEI_IMAGE_GPU}
    hostname: tei
    
    ports:
      - ${TEI_PORT:-6380}:80
    
    networks:
      - ragflow
    
    command:
      - "--model-id"
      - "/data/${TEI_MODEL}"
      - "--auto-truncate"
    
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    
    restart: unless-stopped

  # ============================================
  # 数据卷定义（持久化存储）
  # ============================================
volumes:
  esdata01:
    driver: local
  mysql_data:
    driver: local
  minio_data:
    driver: local
  redis_data:
    driver: local
  tei_data:
    driver: local
  infinity_data:
    driver: local

# 网络定义
networks:
  ragflow:
    driver: bridge
```

### 1.4 环境变量配置（.env 文件详解）

```bash
# ============================================================
# .env 文件完整说明
# ============================================================

# ============================================
# 第一节：核心配置（必须修改）
# ============================================

# 向量数据库类型选择
# 可选值：elasticsearch / infinity / oceanbase / opensearch / seekdb
DOC_ENGINE=${DOC_ENGINE:-elasticsearch}

# 运行设备选择
# 可选值：cpu / gpu
DEVICE=${DEVICE:-cpu}

# 自动生成 compose profiles
COMPOSE_PROFILES=${DOC_ENGINE},${DEVICE}

# ============================================
# 第二节：Elasticsearch 配置
# ============================================

STACK_VERSION=${STACK_VERSION:-8.11.3}
ES_HOST=es01
ES_PORT=1200
# ⚠️ 生产环境必须修改！
ELASTIC_PASSWORD=infini_rag_flow

# ============================================
# 第三节：MySQL 配置
# ============================================

# ⚠️ 生产环境必须修改！
MYSQL_PASSWORD=infini_rag_flow
MYSQL_HOST=mysql
MYSQL_DBNAME=rag_flow
MYSQL_PORT=3306
EXPOSE_MYSQL_PORT=3306
MYSQL_MAX_PACKET=1073741824  # 1GB

# ============================================
# 第四节：MinIO 配置
# ============================================

MINIO_HOST=minio
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001
# ⚠️ 生产环境必须修改！
MINIO_USER=rag_flow
MINIO_PASSWORD=infini_rag_flow

# ============================================
# 第五节：Redis 配置
# ============================================

REDIS_HOST=redis
REDIS_PORT=6379
# ⚠️ 生产环境必须修改！
REDIS_PASSWORD=infini_rag_flow

# ============================================
# 第六节：服务端口配置
# ============================================

SVR_WEB_HTTP_PORT=80
SVR_WEB_HTTPS_PORT=443
SVR_HTTP_PORT=9380
ADMIN_SVR_HTTP_PORT=9381
SVR_MCP_PORT=9382
GO_HTTP_PORT=9384
GO_ADMIN_PORT=9383

# API 代理模式
# python = 纯Python服务部署（推荐）
# hybrid = Go + Python 混合部署
API_PROXY_SCHEME=python

# ============================================
# 第七节：RAGFlow 镜像配置
# ============================================

# 官方镜像
RAGFLOW_IMAGE=infiniflow/ragflow:v0.25.1

# 阿里云镜像（国内推荐）
# RAGFLOW_IMAGE=registry.cn-hangzhou.aliyuncs.com/infiniflow/ragflow:v0.25.1

# 华为云镜像
# RAGFLOW_IMAGE=swr.cn-north-4.myhuaweicloud.com/infiniflow/ragflow:v0.25.1

# ============================================
# 第八节：Embedding 服务配置
# ============================================

# TEI CPU 镜像
TEI_IMAGE_CPU=infiniflow/text-embeddings-inference:cpu-1.8

# TEI GPU 镜像
TEI_IMAGE_GPU=infiniflow/text-embeddings-inference:1.8

# Embedding 模型选择
# Qwen3-Embedding-0.6B：效果最好，需要25GB内存
# BAAI/bge-m3：效果较好，需要21GB内存
# BAAI/bge-small-en-v1.5：轻量版，仅需1.2GB内存
TEI_MODEL=${TEI_MODEL:-Qwen/Qwen3-Embedding-0.6B}

TEI_HOST=tei
TEI_PORT=6380

# ============================================
# 第九节：资源限制
# ============================================

# 容器最大内存限制（字节）
# 8GB = 8589934592
# 16GB = 17179869184
MEM_LIMIT=8073741824

# 文件上传大小限制（字节）
# 1GB = 1073741824
# MAX_CONTENT_LENGTH=1073741824

# 文档批处理大小
DOC_BULK_SIZE=${DOC_BULK_SIZE:-4}

# Embedding 批处理大小
EMBEDDING_BATCH_SIZE=${EMBEDDING_BATCH_SIZE:-16}

# ============================================
# 第十节：可选功能配置
# ============================================

# 时区设置
TZ=Asia/Shanghai

# HuggingFace 镜像（国内访问）
# HF_ENDPOINT=https://hf-mirror.com

# 用户注册开关
# 1 = 允许注册
# 0 = 禁止注册
REGISTER_ENABLED=1

# Sandbox 沙箱功能（代码执行）
# SANDBOX_ENABLED=1
# COMPOSE_PROFILES=${COMPOSE_PROFILES},sandbox

# MinerU PDF解析（效果好但慢）
# MINERU_DELETE_OUTPUT=0
# MINERU_BACKEND=pipeline

# ============================================
# 第十一节：阿里云OSS配置（可选）
# ============================================

# STORAGE_IMPL=OSS
# ACCESS_KEY=你的AccessKey
# SECRET_KEY=你的SecretKey
# ENDPOINT=http://oss-cn-hangzhou.aliyuncs.com
# REGION=cn-hangzhou
# BUCKET=ragflow65536
```

### 1.5 RAGFlow-Plus 版本的 docker-compose 差异

RAGFlow-Plus 在官方版基础上增加了后台管理系统，主要差异：

```yaml
# RAGFlow-Plus docker-compose.yml 核心差异

services:
  # 前台服务（与官方版类似）
  ragflowplus-server:
    image: ${RAGFLOW_IMAGE:-zstar1003/ragflow-plus:latest}
    ports:
      - "80:80"              # 前台 Web UI
      - "9380:9380"          # API Server
    # ...

  # 后台管理服务（RAGFlow-Plus特有）
  management-server:
    image: ${RAGFLOW_IMAGE:-zstar1003/ragflow-plus:latest}
    ports:
      - "8888:5000"          # 后台管理端口
    environment:
      - FLASK_ENV=production
    volumes:
      - ./management/logs:/app/logs
    depends_on:
      - mysql
      - redis
    networks:
      - ragflow
    restart: unless-stopped

  # 后台 Web UI（RAGFlow-Plus特有）
  management-web:
    image: node:18-alpine
    ports:
      - "8889:80"            # 后台管理前端
    volumes:
      - ./management/web:/app
    command: sh -c "npm install && npm run dev"
    networks:
      - ragflow
    restart: unless-stopped
```

**RAGFlow-Plus 端口对照表：**

| 服务 | 端口 | 说明 |
|------|------|------|
| 前台 Web UI | 80 | 用户使用的知识库问答界面 |
| 前台 API | 9380 | 开发者 API 入口 |
| 后台管理 UI | 8888 | 管理员使用的管理界面 |
| MinIO 控制台 | 9001 | 对象存储管理界面 |

### 1.6 快速启动命令

```bash
# ============================================================
# RAGFlow 快速启动
# ============================================================

# 1. 克隆项目
git clone https://github.com/infiniflow/ragflow.git
cd ragflow/docker

# 2. 配置环境变量（可选，修改密码）
vim .env
# 修改以下密码为强密码：
# ELASTIC_PASSWORD=你的强密码
# MYSQL_PASSWORD=你的强密码
# MINIO_PASSWORD=你的强密码
# REDIS_PASSWORD=你的强密码

# 3. 启动服务（CPU版本）
docker compose -f docker-compose.yml up -d

# 4. 启动服务（GPU版本）
sed -i '1i DEVICE=gpu' .env
docker compose -f docker-compose.yml up -d

# 5. 查看容器状态
docker compose -f docker-compose.yml ps

# 6. 查看日志
docker logs -f docker-ragflow-cpu-1

# 7. 访问系统
# 浏览器打开 http://服务器IP:80
# 初始化密钥在日志中查找：
docker logs docker-ragflow-cpu-1 | grep "API KEY"

# ============================================================
# RAGFlow-Plus 快速启动
# ============================================================

# 1. 克隆项目
git clone https://github.com/zstar1003/ragflow-plus.git
cd ragflow-plus/docker

# 2. 启动所有服务
docker compose -f docker-compose.yml up -d

# 3. 访问系统
# 前台：http://服务器IP:80
# 后台：http://服务器IP:8888
```

---

## 第二章：阿里云部署方案

### 2.1 阿里云部署架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           阿里云部署架构                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                              ┌─────────────┐                                 │
│                              │  负载均衡   │                                 │
│                              │   SLB       │                                 │
│                              │  (公网入口) │                                 │
│                              └──────┬──────┘                                 │
│                                     │                                        │
│                    ┌───────────────┼───────────────┐                       │
│                    │               │               │                       │
│                    ▼               ▼               ▼                       │
│             ┌──────────┐   ┌──────────┐   ┌──────────┐                       │
│             │  ECS-01  │   │  ECS-02  │   │  ECS-03  │                       │
│             │(RAGFlow) │   │(RAGFlow) │   │(RAGFlow) │                       │
│             │  GPU/T4  │   │  GPU/T4  │   │  GPU/T4  │                       │
│             └────┬─────┘   └────┬─────┘   └────┬─────┘                       │
│                  │               │               │                           │
│                  └───────────────┼───────────────┘                           │
│                                  │                                          │
│     ┌────────────────────────────┼────────────────────────────────────┐      │
│     │                            │                                     │      │
│     ▼                            ▼                                     ▼      │
│ ┌────────┐               ┌─────────────┐                      ┌─────────┐  │
│ │  VPC   │               │   内网连接   │                      │  安全组 │  │
│ │ 专用网络│               │             │                      │         │  │
│ └────────┘               └─────────────┘                      └─────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         阿里云托管服务                                 │    │
│  │  ┌────────┐  ┌────────────┐  ┌────────┐  ┌──────────┐  ┌─────────┐  │    │
│  │  │  RDS   │  │   Redis    │  │   OSS  │  │  日志服务 │  │  云监控  │  │    │
│  │  │ MySQL  │  │   缓存     │  │对象存储 │  │   SLS    │  │  ARM    │  │    │
│  │  └────────┘  └────────────┘  └────────┘  └──────────┘  └─────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 ECS 实例选型建议

#### 2.2.1 不同规模场景选型对照

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        阿里云 ECS 选型建议                                   │
├─────────────┬──────────────┬──────────────┬──────────────┬────────────────┤
│   场景      │    实例规格   │    CPU/内存   │    GPU      │    月费估算    │
├─────────────┼──────────────┼──────────────┼──────────────┼────────────────┤
│  开发测试    │  ecs.g7.large│  2核/8GB     │  无          │  ~300元        │
│  (<10用户)  │              │              │              │               │
├─────────────┼──────────────┼──────────────┼──────────────┼────────────────┤
│  小规模生产  │  ecs.g7.xlarge│  4核/16GB    │  无/NVIDIA T4│  ~800元/1500元 │
│  (<100用户) │              │              │              │               │
├─────────────┼──────────────┼──────────────┼──────────────┼────────────────┤
│  中等规模    │  ecs.g7.2xlarge│ 8核/32GB   │  NVIDIA T4   │  ~1500元       │
│  (100-300)  │              │              │  (15GB显存)  │               │
├─────────────┼──────────────┼──────────────┼──────────────┼────────────────┤
│  大规模生产  │  ecs.g8.4xlarge│ 16核/64GB  │  NVIDIA A10  │  ~4000元       │
│  (300-500)  │              │              │  (24GB显存)  │               │
├─────────────┼──────────────┼──────────────┼──────────────┼────────────────┤
│  企业级      │  ecs.g8.8xlarge│ 32核/128GB │  NVIDIA A100 │  ~12000元      │
│  (>500用户) │  × 3节点集群  │              │  (40GB显存)  │               │
└─────────────┴──────────────┴──────────────┴──────────────┴────────────────┘
```

#### 2.2.2 GPU 实例详细说明

**为什么需要 GPU？**

RAGFlow 的文档解析（DeepDoc）和 Embedding 模型都需要大量矩阵运算：
- CPU 处理：逐个计算，1000个向量需要 10秒
- GPU 处理：并行计算，1000个向量仅需 0.5秒

**阿里云 GPU 实例对比：**

| 实例类型 | GPU型号 | 显存 | 适用场景 | 性价比 |
|---------|--------|------|---------|--------|
| gn6v | NVIDIA V100 | 16GB | 追求高性能 | ★★★★☆ |
| gn6i | NVIDIA T4 | 16GB | 平衡性能与成本 | ★★★★★ |
| gn7i | NVIDIA A10 | 24GB | 大规模生产 | ★★★★☆ |
| gn7 | NVIDIA A100 | 40GB | 企业级/大规模 | ★★★☆☆ |

**推荐配置（中等规模，100-300用户）：**

```bash
# ECS 实例配置
实例规格: ecs.gn6i-c8g1.4xlarge
vCPU: 8核
内存: 32GB
GPU: NVIDIA T4 (16GB)
系统盘: 100GB SSD
数据盘: 500GB SSD
操作系统: Ubuntu 22.04 LTS
```

### 2.3 RDS/Redis/OSS 托管服务集成

#### 2.3.1 阿里云 RDS for MySQL 配置

**为什么用 RDS 而不是自建 MySQL？**

| 对比项 | 自建 MySQL | 阿里云 RDS |
|--------|-----------|-----------|
| 运维成本 | 需要 DBA 维护 | 全托管 |
| 可靠性 | 需要配置主从 | 自动备份/恢复 |
| 扩展性 | 手动扩容 | 一键升级 |
| 成本 | 服务器费用 | RDS费用 + 服务器费用 |

**RDS 配置步骤：**

```sql
-- 1. 创建数据库
CREATE DATABASE rag_flow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. 创建用户（限制IP访问）
CREATE USER 'ragflow'@'%' IDENTIFIED BY '你的强密码';
GRANT ALL PRIVILEGES ON rag_flow.* TO 'ragflow'@'%';

-- 3. 配置参数（建议）
-- character_set_server = utf8mb4
-- max_connections = 1000
-- innodb_buffer_pool_size = 4G (根据RDS规格调整)
```

**修改 docker-compose 配置：**

```yaml
# 删除 mysql 服务，修改 .env
# .env 文件修改
MYSQL_HOST=rm-xxxxx.mysql.rds.aliyuncs.com  # RDS内网地址
MYSQL_PORT=3306
MYSQL_PASSWORD=你的RDS密码
EXPOSE_MYSQL_PORT=  # 留空，不暴露端口
```

#### 2.3.2 阿里云 Redis 配置

```bash
# .env 文件修改
REDIS_HOST=r-xxxxx.redis.rds.aliyuncs.com  # Redis内网地址
REDIS_PORT=6379
REDIS_PASSWORD=你的Redis密码
```

#### 2.3.3 阿里云 OSS 配置

```bash
# .env 文件末尾添加
STORAGE_IMPL=OSS
ACCESS_KEY=你的AccessKeyID
SECRET_KEY=你的AccessKeySecret
ENDPOINT=http://oss-cn-hangzhou.aliyuncs.com
REGION=cn-hangzhou
BUCKET=ragflow-enterprise
```

### 2.4 安全组与网络配置

#### 2.4.1 安全组规则配置

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           阿里云安全组配置                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  入方向规则（Allow Inbound）：                                               │
│  ┌────────┬──────────┬─────────────────┬──────────────┬─────────────────┐    │
│  │  协议  │   端口   │     来源        │     说明     │     优先级      │    │
│  ├────────┼──────────┼─────────────────┼──────────────┼─────────────────┤    │
│  │  HTTP  │   80     │  0.0.0.0/0      │  Web UI      │      100       │    │
│  ├────────┼──────────┼─────────────────┼──────────────┼─────────────────┤    │
│  │  HTTPS │   443    │  0.0.0.0/0      │  HTTPS       │      100       │    │
│  ├────────┼──────────┼─────────────────┼──────────────┼─────────────────┤    │
│  │  SSH   │   22     │  你的IP/32      │  服务器管理   │       50       │    │
│  ├────────┼──────────┼─────────────────┼──────────────┼─────────────────┤    │
│  │  自定义│  8888    │  内部网络        │  后台管理    │      100       │    │
│  └────────┴──────────┴─────────────────┴──────────────┴─────────────────┘    │
│                                                                             │
│  ⚠️ 注意事项：                                                              │
│  1. SSH 端口只允许你的IP访问，不要对所有IP开放                               │
│  2. MySQL/Redis 端口不要暴露到公网                                          │
│  3. 生产环境建议关闭所有公网访问，通过VPN或跳板机管理                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 2.4.2 VPC 网络配置

```
最佳实践：使用专有网络 (VPC)

┌─────────────────────────────────────────────────────────────────┐
│                          VPC 网络                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│    ┌─────────────────────────────────────────────────────┐      │
│    │                  虚拟交换机 (VSwitch)                │      │
│    │                                                     │      │
│    │   ┌─────────┐   ┌─────────┐   ┌─────────┐        │      │
│    │   │ ECS-01  │   │ ECS-02  │   │ ECS-03  │        │      │
│    │   │ RAGFlow │   │ RAGFlow │   │ RAGFlow │        │      │
│    │   └─────────┘   └─────────┘   └─────────┘        │      │
│    │                                                     │      │
│    └─────────────────────────────────────────────────────┘      │
│                          │                                       │
│           ┌──────────────┼──────────────┐                       │
│           │              │              │                       │
│           ▼              ▼              ▼                        │
│    ┌───────────┐  ┌───────────┐  ┌───────────┐                │
│    │    RDS    │  │   Redis   │  │    OSS    │                │
│    │  (内网)   │  │  (内网)   │  │  (内网)   │                │
│    └───────────┘  └───────────┘  └───────────┘                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.5 阿里云部署完整脚本

```bash
#!/bin/bash
# ============================================================
# 阿里云 ECS 自动部署脚本
# ============================================================

# 1. 安装 Docker 和 Docker Compose
curl -fsSL https://get.docker.com | sh
apt install -y docker-compose-plugin

# 2. 配置 Docker 镜像加速
mkdir -p /etc/docker
cat > /etc/docker/daemon.json << EOF
{
  "registry-mirrors": [
    "https://docker.aliyun.com",
    "https://mirror.ccs.tencentyun.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
EOF

systemctl daemon-reload
systemctl restart docker

# 3. 配置系统参数
cat >> /etc/sysctl.conf << EOF
vm.max_map_count=262144
vm.swappiness=1
net.core.somaxconn=65535
EOF

sysctl -p

# 4. 克隆并配置 RAGFlow
git clone https://github.com/infiniflow/ragflow.git
cd ragflow/docker

# 5. 修改 .env 配置
cat > .env << EOF
# 基础配置
DOC_ENGINE=elasticsearch
DEVICE=gpu
COMPOSE_PROFILES=elasticsearch,gpu

# Elasticsearch
ES_PORT=1200
ELASTIC_PASSWORD=$(openssl rand -hex 24)

# MySQL（使用阿里云RDS）
MYSQL_HOST=rm-xxxxx.mysql.rds.aliyuncs.com
MYSQL_PORT=3306
MYSQL_PASSWORD=你的RDS密码
MYSQL_DBNAME=rag_flow
EXPOSE_MYSQL_PORT=

# MinIO
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001
MINIO_USER=ragflow
MINIO_PASSWORD=$(openssl rand -hex 24)

# Redis（使用阿里云Redis）
REDIS_HOST=r-xxxxx.redis.rds.aliyuncs.com
REDIS_PORT=6379
REDIS_PASSWORD=你的Redis密码

# 端口配置
SVR_WEB_HTTP_PORT=80
SVR_HTTP_PORT=9380

# RAGFlow 镜像（阿里云）
RAGFLOW_IMAGE=registry.cn-hangzhou.aliyuncs.com/infiniflow/ragflow:v0.25.1

# Embedding
TEI_IMAGE_CPU=infiniflow/text-embeddings-inference:cpu-1.8
TEI_IMAGE_GPU=infiniflow/text-embeddings-inference:1.8
TEI_MODEL=Qwen/Qwen3-Embedding-0.6B
COMPOSE_PROFILES=\${COMPOSE_PROFILES},tei-gpu

# 资源限制
MEM_LIMIT=25769803776  # 24GB

# 时区
TZ=Asia/Shanghai
EOF

# 6. 启动服务
docker compose -f docker-compose.yml up -d

# 7. 查看状态
docker compose -f docker-compose.yml ps

echo "部署完成！访问 http://服务器IP:80"
```

### 2.6 阿里云成本估算

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        月度成本估算（中等规模 200用户）                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                          ECS 成本                                    │    │
│  │  ┌─────────────────┬────────────┬─────────────┐                    │    │
│  │  │   配置          │   单价     │   数量      │    小计           │    │
│  │  ├─────────────────┼────────────┼─────────────┼─────────────┐    │    │
│  │  │ ecs.gn6i        │  ¥2,500/月 │     1      │   ¥2,500     │    │    │
│  │  │ (8核32G+T4)     │            │             │              │    │    │
│  │  └─────────────────┴────────────┴─────────────┴─────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         RDS 成本                                     │    │
│  │  ┌─────────────────┬────────────┬─────────────┐                    │    │
│  │  │   配置          │   单价     │   数量      │    小计           │    │
│  │  ├─────────────────┼────────────┼─────────────┼─────────────┐    │    │
│  │  │ rMySQL.basic    │  ¥400/月  │     1      │    ¥400      │    │    │
│  │  │ (2核4G)         │            │             │              │    │    │
│  │  └─────────────────┴────────────┴─────────────┴─────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         Redis 成本                                   │    │
│  │  ┌─────────────────┬────────────┬─────────────┐                    │    │
│  │  │   配置          │   单价     │   数量      │    小计           │    │
│  │  ├─────────────────┼────────────┼─────────────┼─────────────┐    │    │
│  │  │ redis.master    │  ¥200/月  │     1      │    ¥200      │    │    │
│  │  │ (1G)            │            │             │              │    │    │
│  │  └─────────────────┴────────────┴─────────────┴─────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         OSS 成本                                    │    │
│  │  ┌─────────────────┬────────────┬─────────────┐                    │    │
│  │  │   存储          │   单价     │   数量      │    小计           │    │
│  │  ├─────────────────┼────────────┼─────────────┼─────────────┐    │    │
│  │  │ 500GB存储       │  ¥50/月   │     1      │     ¥50      │    │    │
│  │  └─────────────────┴────────────┴─────────────┴─────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                           合计                                       │    │
│  │                                                                     │    │
│  │   ¥3,150/月  ≈  ¥94/天  ≈  ¥0.47/用户/天                          │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 第三章：生产环境配置

### 3.1 MySQL 生产优化

#### 3.1.1 MySQL 配置文件 (my.cnf)

```ini
# /docker/mysql/conf/custom.cnf
# RAGFlow 生产环境 MySQL 配置

[mysqld]
# 字符集
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# 连接配置
max_connections = 1000
max_connect_errors = 100000
wait_timeout = 600
interactive_timeout = 600

# 缓冲区配置
innodb_buffer_pool_size = 4G          # 建议设置为可用内存的70%
innodb_buffer_pool_instances = 4
innodb_log_file_size = 1G
innodb_log_buffer_size = 64M
innodb_flush_log_at_trx_commit = 2    # 性能优先

# 查询缓存（MySQL 8.0 已移除，此处保留仅供参考）
# query_cache_type = 0
# query_cache_size = 0

# 临时表和排序
tmp_table_size = 256M
max_heap_table_size = 256M
sort_buffer_size = 4M
join_buffer_size = 4M

# 主从复制配置（如果使用）
# log-bin = mysql-bin
# binlog_format = ROW
# expire_logs_days = 7

# 慢查询日志
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2

# 网络配置
max_allowed_packet = 1G
net_buffer_length = 16K

# 线程配置
thread_cache_size = 64
table_open_cache = 4096

[client]
default-character-set = utf8mb4
```

#### 3.1.2 MySQL 连接池配置

```yaml
# docker-compose.yml 中的 MySQL 配置
mysql:
  volumes:
    - mysql_data:/var/lib/mysql
    - ./mysql/conf:/etc/mysql/conf.d  # 挂载自定义配置
  
  environment:
    - MYSQL_ROOT_PASSWORD=${MYSQL_PASSWORD}
    - MYSQL_DATABASE=${MYSQL_DBNAME}
  
  command:
    - --character-set-server=utf8mb4
    - --collation-server=utf8mb4_unicode_ci
    - --max_connections=1000
    - --innodb-buffer-pool-size=4G
```

### 3.2 Elasticsearch 生产优化

#### 3.2.1 Elasticsearch 配置

```yaml
# docker-compose-base.yml 中的 ES 配置优化
es01:
  environment:
    # 集群配置
    - cluster.name=ragflow-cluster
    - discovery.type=single-node
    
    # 内存配置
    - bootstrap.memory_lock=true
    - indices.memory.index_buffer_size=20%
    
    # 性能配置
    - indices.queries.cache.size=15%
    - thread_pool.write.queue_size=1000
    - thread_pool.search.queue_size=1000
    
    # 磁盘配置
    - cluster.routing.allocation.disk.watermark.low=5gb
    - cluster.routing.allocation.disk.watermark.high=3gb
    - cluster.routing.allocation.disk.watermark.flood_stage=2gb
    
    # 快照配置
    - xpack.snapshot.enabled=true
  
  # 内存锁定（需要 ulimit 配置）
  ulimits:
    memlock:
      soft: -1
      hard: -1
  
  # 内存限制（根据主机可用内存调整）
  mem_limit: 8g
```

#### 3.2.2 Elasticsearch 索引优化

```json
// 创建索引时的优化配置
{
  "settings": {
    "number_of_shards": 2,           // 分片数（建议 2-3）
    "number_of_replicas": 1,          // 副本数（生产环境建议 1）
    "refresh_interval": "5s",         // 刷新间隔（不是实时搜索可设长）
    "translog": {
      "durability": "async"          // 异步同步，提高写入性能
    }
  }
}
```

### 3.3 Redis 生产配置

```yaml
# docker-compose-base.yml 中的 Redis 配置优化
redis:
  image: valkey/valkey:8
  
  command:
    - "redis-server"
    - "--requirepass"
    - "${REDIS_PASSWORD}"
    # 内存配置
    - "--maxmemory=512mb"            # 根据内存调整
    - "--maxmemory-policy=allkeys-lru"
    # 持久化配置
    - "--save=900 1"                 # 15分钟至少1个key变化则保存
    - "--save=300 10"                # 5分钟至少10个key变化则保存
    - "--appendonly=yes"             # 开启 AOF 持久化
    - "--appendfsync=everysec"       # 每秒同步一次
    # 性能配置
    - "--tcp-backlog=511"
    - "--timeout=0"
    - "--tcp-keepalive=300"
```

### 3.4 MinIO 生产配置

```yaml
# MinIO 生产配置
minio:
  image: minio/minio:latest
  
  command:
    - "server"
    - "/data"
    - "--console-address"
    - ":9001"
    - "--address"
    - ":9000"
    # 存储配置
    - "--storage-class.standard=EC:2"  # 纠删码模式，2块校验盘
    # API 配置
    - "--api-requests-max"
    - "10000"
    - "--api-cores"
    - "4"
  
  environment:
    - MINIO_ROOT_USER=${MINIO_USER}
    - MINIO_ROOT_PASSWORD=${MINIO_PASSWORD}
    # 通知配置（可选，用于告警）
    - MINIO_NOTIFY_WEBHOOK_ENABLE_primary="on"
    - MINIO_NOTIFY_WEBHOOK_ENDPOINT_primary="http://your-webhook-endpoint"
  
  volumes:
    - minio_data:/data
  
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
    interval: 30s
    timeout: 20s
    retries: 3
```

### 3.5 Nginx 反向代理配置

#### 3.5.1 Nginx 配置示例

```nginx
# /docker/nginx/nginx.conf

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct=$upstream_connect_time uht=$upstream_header_time urt=$upstream_response_time';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # 基础配置
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/rss+xml application/atom+xml image/svg+xml;

    # 文件上传大小
    client_max_body_size 2G;
    client_body_buffer_size 128k;

    # 代理配置
    upstream ragflow_backend {
        server ragflow-cpu:80 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    server {
        listen 80;
        server_name _;

        # 重定向到 HTTPS（生产环境建议开启）
        # return 301 https://$host$request_uri;

        location / {
            proxy_pass http://ragflow_backend;
            proxy_http_version 1.1;
            
            # 头信息
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # 超时配置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            # 缓冲配置
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
            proxy_busy_buffers_size 8k;
        }

        # API 路径
        location /v1 {
            proxy_pass http://ragflow_backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # WebSocket 支持（Agent 对话）
        location /ws {
            proxy_pass http://ragflow_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_read_timeout 86400s;
        }
    }

    # HTTPS 配置（生产环境）
    # server {
    #     listen 443 ssl http2;
    #     server_name your-domain.com;
    #
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #     ssl_session_timeout 1d;
    #     ssl_session_cache shared:SSL:50m;
    #     ssl_session_tickets off;
    #
    #     ssl_protocols TLSv1.2 TLSv1.3;
    #     ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    #     ssl_prefer_server_ciphers off;
    #
    #     # 其他配置同上...
    # }
}
```

#### 3.5.2 修改 docker-compose 挂载 Nginx 配置

```yaml
# 在 docker-compose.yml 中添加
ragflow-cpu:
  volumes:
    - ./ragflow-logs:/ragflow/logs
    - ./service_conf.yaml.template:/ragflow/conf/service_conf.yaml.template
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf  # 添加这一行
```

### 3.6 SSL 证书配置

#### 3.6.1 使用 Let's Encrypt 免费证书

```bash
#!/bin/bash
# 获取 Let's Encrypt 证书

# 1. 安装 certbot
apt update && apt install -y certbot python3-certbot-nginx

# 2. 停止 Nginx（如果正在运行）
docker stop ragflow-nginx 2>/dev/null || true

# 3. 获取证书
certbot certonly --standalone -d your-domain.com --agree-tos -n -m your-email@example.com

# 4. 证书会保存到
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem

# 5. 复制证书到 RAGFlow 目录
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /path/to/ragflow/docker/nginx/ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem /path/to/ragflow/docker/nginx/ssl/key.pem

# 6. 配置自动续期
crontab -e
# 添加以下行（每天检查续期）
0 0 * * * certbot renew --quiet
```

#### 3.6.2 证书自动续期脚本

```bash
#!/bin/bash
# /opt/scripts/renew-ssl.sh

# 停止 RAGFlow
cd /path/to/ragflow/docker
docker compose -f docker-compose.yml stop

# 续期证书
certbot renew --quiet

# 复制证书
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./nginx/ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./nginx/ssl/key.pem

# 重启 RAGFlow
docker compose -f docker-compose.yml start
```

---

## 第四章：数据备份与恢复

### 4.1 备份策略概述

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            数据备份策略                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                          备份类型                                    │   │
│  │                                                                     │   │
│  │   实时备份 ──────────────────────────────────────────────────────► │   │
│  │      │                                                           │   │
│  │      ▼                                                           │   │
│  │   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐   │   │
│  │   │  MySQL   │    │   Redis  │    │  MinIO   │    │Elastic-  │   │   │
│  │   │  Binlog  │    │  AOF/RDB │    │   快照   │    │  search  │   │   │
│  │   │  实时   │    │  实时    │    │  定时    │    │  快照    │   │   │
│  │   └──────────┘    └──────────┘    └──────────┘    └──────────┘   │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                          备份频率                                    │   │
│  │                                                                     │   │
│  │   ┌─────────┬─────────┬─────────┬─────────┬─────────┐             │   │
│  │   │  数据   │  频率   │  保留   │  存储   │  目标   │             │   │
│  │   ├─────────┼─────────┼─────────┼─────────┼─────────┤             │   │
│  │   │ MySQL   │ 每小时  │  7天    │ 本地+OSS│ RTO<1h  │             │   │
│  │   │ ES索引  │  每天   │  30天   │ 本地+OSS│ RTO<4h  │             │   │
│  │   │ MinIO   │  每天   │  30天   │ 本地+OSS│ RTO<4h  │             │   │
│  │   │ Redis   │  每6小时 │  3天   │ 本地    │ RTO<30m │             │   │
│  │   │ 配置    │  每次变更│ 永久   │ Git+OSS │ RTO<10m │             │   │
│  │   └─────────┴─────────┴─────────┴─────────┴─────────┘             │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 MySQL 备份方案

#### 4.2.1 自动备份脚本

```bash
#!/bin/bash
# /opt/backup/mysql-backup.sh
# MySQL 自动备份脚本

# 配置
BACKUP_DIR="/opt/backup/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
MYSQL_HOST="localhost"
MYSQL_PORT="3306"
MYSQL_USER="root"
MYSQL_PASSWORD="${MYSQL_PASSWORD}"
MYSQL_DATABASE="rag_flow"
RETENTION_DAYS=7

# OSS 配置（可选）
OSS_BUCKET="ragflow-backup"
OSS_ENDPOINT="oss-cn-hangzhou.aliyuncs.com"

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 执行备份
echo "[$(date)] 开始 MySQL 备份..."
mysqldump -h${MYSQL_HOST} -P${MYSQL_PORT} -u${MYSQL_USER} -p${MYSQL_PASSWORD} \
    --single-transaction \
    --quick \
    --lock-tables=false \
    --routines \
    --triggers \
    --events \
    --hex-blob \
    ${MYSQL_DATABASE} | gzip > ${BACKUP_DIR}/ragflow_${DATE}.sql.gz

# 验证备份
if [ $? -eq 0 ]; then
    echo "[$(date)] MySQL 备份成功: ragflow_${DATE}.sql.gz"
    
    # 计算备份大小
    BACKUP_SIZE=$(du -h ${BACKUP_DIR}/ragflow_${DATE}.sql.gz | cut -f1)
    echo "备份文件大小: ${BACKUP_SIZE}"
    
    # 上传到 OSS（可选）
    # ossutil cp ${BACKUP_DIR}/ragflow_${DATE}.sql.gz oss://${OSS_BUCKET}/mysql/
    
    # 清理过期备份
    find ${BACKUP_DIR} -name "ragflow_*.sql.gz" -mtime +${RETENTION_DAYS} -delete
    echo "[$(date)] 清理 ${RETENTION_DAYS} 天前的备份完成"
else
    echo "[$(date)] MySQL 备份失败!"
    exit 1
fi

# 记录备份日志
echo "[$(date)] MySQL 备份任务完成" >> /var/log/mysql-backup.log
```

#### 4.2.2 Docker 环境下的备份

```bash
#!/bin/bash
# Docker 环境下的 MySQL 备份

BACKUP_DIR="/opt/backup/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER_NAME="docker-mysql-1"

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 在容器内执行备份并导出
docker exec ${CONTAINER_NAME} mysqldump -u root -p${MYSQL_PASSWORD} \
    --single-transaction \
    --quick \
    rag_flow | gzip > ${BACKUP_DIR}/ragflow_${DATE}.sql.gz

echo "备份完成: ragflow_${DATE}.sql.gz"
```

#### 4.2.3 备份恢复脚本

```bash
#!/bin/bash
# /opt/backup/mysql-restore.sh
# MySQL 数据恢复脚本

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "用法: $0 <备份文件路径>"
    echo "示例: $0 /opt/backup/mysql/ragflow_20240101_120000.sql.gz"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "错误: 备份文件不存在: $BACKUP_FILE"
    exit 1
fi

echo "警告: 此操作将覆盖当前数据库!"
read -p "确认继续? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "操作已取消"
    exit 0
fi

CONTAINER_NAME="docker-mysql-1"
MYSQL_PASSWORD="${MYSQL_PASSWORD}"

# 停止 RAGFlow 服务
cd /path/to/ragflow/docker
docker compose stop ragflow-cpu ragflow-gpu

# 执行恢复
echo "开始恢复数据..."
gunzip -c $BACKUP_FILE | docker exec -i ${CONTAINER_NAME} mysql -u root -p${MYSQL_PASSWORD} rag_flow

if [ $? -eq 0 ]; then
    echo "数据恢复成功!"
else
    echo "数据恢复失败!"
    exit 1
fi

# 重启 RAGFlow 服务
docker compose start ragflow-cpu ragflow-gpu
echo "RAGFlow 服务已重启"
```

### 4.3 Elasticsearch 备份

#### 4.3.1 快照备份脚本

```bash
#!/bin/bash
# /opt/backup/es-backup.sh
# Elasticsearch 快照备份

ES_HOST="localhost"
ES_PORT="1200"
ES_USER="elastic"
ES_PASSWORD="${ELASTIC_PASSWORD}"
SNAPSHOT_REPO="/opt/backup/es-snapshots"
RETENTION_DAYS=30

# 创建快照仓库（首次运行需要）
create_repository() {
    curl -X PUT "http://${ES_HOST}:${ES_PORT}/_snapshot/ragflow_backup" \
        -u ${ES_USER}:${ES_PASSWORD} \
        -H 'Content-Type: application/json' \
        -d '{
            "type": "fs",
            "settings": {
                "location": "'${SNAPSHOT_REPO}'",
                "compress": true,
                "max_snapshot_bytes_per_sec": "100mb",
                "max_restore_bytes_per_sec": "100mb"
            }
        }'
}

# 执行快照备份
DATE=$(date +%Y%m%d_%H%M%S)
SNAPSHOT_NAME="ragflow_${DATE}"

echo "[$(date)] 开始 Elasticsearch 快照备份..."

# 创建快照
curl -X PUT "http://${ES_HOST}:${ES_PORT}/_snapshot/ragflow_backup/${SNAPSHOT_NAME}?wait_for_completion=true" \
    -u ${ES_USER}:${ES_PASSWORD} \
    -H 'Content-Type: application/json'

if [ $? -eq 0 ]; then
    echo "[$(date)] 快照创建成功: ${SNAPSHOT_NAME}"
    
    # 清理旧快照
    curl -X GET "http://${ES_HOST}:${ES_PORT}/_snapshot/ragflow_backup/_all" \
        -u ${ES_USER}:${ES_PASSWORD} | jq -r '.snapshots[] | select(.end_time_epoch < '$(date -d "-${RETENTION_DAYS} days" +%s)') | .snapshot' | \
        while read snapshot; do
            if [ -n "$snapshot" ]; then
                echo "删除旧快照: $snapshot"
                curl -X DELETE "http://${ES_HOST}:${ES_PORT}/_snapshot/ragflow_backup/${snapshot}" \
                    -u ${ES_USER}:${ES_PASSWORD}
            fi
        done
else
    echo "[$(date)] 快照创建失败!"
fi

# 备份索引配置
echo "[$(date)] 备份索引映射配置..."
curl -s "http://${ES_HOST}:${ES_PORT}/_all/_mapping" \
    -u ${ES_USER}:${ES_PASSWORD} > ${SNAPSHOT_REPO}/index_mappings_$(date +%Y%m%d).json

echo "[$(date)] Elasticsearch 备份任务完成"
```

#### 4.3.2 恢复脚本

```bash
#!/bin/bash
# /opt/backup/es-restore.sh
# Elasticsearch 数据恢复

SNAPSHOT_NAME=$1

if [ -z "$SNAPSHOT_NAME" ]; then
    # 列出可用快照
    curl -s "http://localhost:1200/_snapshot/ragflow_backup/_all" \
        -u elastic:${ELASTIC_PASSWORD} | jq '.snapshots[].snapshot'
    exit 0
fi

echo "警告: 此操作将恢复快照 ${SNAPSHOT_NAME} 的数据!"
read -p "确认继续? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    exit 0
fi

# 关闭索引（恢复前需要）
curl -X POST "http://localhost:1200/*/_close" \
    -u elastic:${ELASTIC_PASSWORD}

# 执行恢复
echo "开始恢复数据..."
curl -X POST "http://localhost:1200/_snapshot/ragflow_backup/${SNAPSHOT_NAME}/_restore?wait_for_completion=true" \
    -u elastic:${ELASTIC_PASSWORD}

# 打开索引
curl -X POST "http://localhost:1200/*/_open" \
    -u elastic:${ELASTIC_PASSWORD}

echo "Elasticsearch 数据恢复完成"
```

### 4.4 MinIO 文件备份

```bash
#!/bin/bash
# /opt/backup/minio-backup.sh
# MinIO 文件备份

MINIO_ENDPOINT="localhost:9000"
MINIO_ACCESS_KEY="${MINIO_USER}"
MINIO_SECRET_KEY="${MINIO_PASSWORD}"
BUCKET_NAME="ragflow"
BACKUP_DIR="/opt/backup/minio"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p ${BACKUP_DIR}

echo "[$(date)] 开始 MinIO 备份..."

# 使用 mc 客户端备份
docker run --rm \
    -e MC_HOST_local="http://${MINIO_ACCESS_KEY}:${MINIO_SECRET_KEY}@${MINIO_ENDPOINT}" \
    minio/mc:latest \
    mc mirror local/${BUCKET_NAME} ${BACKUP_DIR}/${BUCKET_NAME}_${DATE}

if [ $? -eq 0 ]; then
    echo "[$(date)] MinIO 备份成功"
    
    # 压缩备份
    tar -czf ${BACKUP_DIR}/${BUCKET_NAME}_${DATE}.tar.gz -C ${BACKUP_DIR} ${BUCKET_NAME}_${DATE}
    rm -rf ${BACKUP_DIR}/${BUCKET_NAME}_${DATE}
    
    # 清理旧备份
    find ${BACKUP_DIR} -name "${BUCKET_NAME}_*.tar.gz" -mtime +${RETENTION_DAYS} -delete
else
    echo "[$(date)] MinIO 备份失败!"
fi
```

### 4.5 Redis 持久化配置

```yaml
# Redis 持久化配置（推荐 AOF + RDB 混合模式）
redis:
  command:
    - "redis-server"
    - "--requirepass"
    - "${REDIS_PASSWORD}"
    # RDB 持久化
    - "--save=900 1"
    - "--save=300 10"
    - "--save=60 10000"
    # AOF 持久化
    - "--appendonly=yes"
    - "--appendfsync=everysec"
    - "--auto-aof-rewrite-percentage=100"
    - "--auto-aof-rewrite-min-size=64mb"
```

### 4.6 灾难恢复方案

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          灾难恢复方案 (DR)                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  恢复时间目标 (RTO) 与 恢复点目标 (RPO)                                       │
│  ┌─────────────────┬─────────────┬─────────────┐                            │
│  │     场景        │     RTO     │     RPO     │                            │
│  ├─────────────────┼─────────────┼─────────────┤                            │
│  │  单个服务故障    │    < 5分钟  │    0       │                            │
│  │  数据库损坏      │    < 1小时  │    1小时    │                            │
│  │  服务器宕机      │    < 4小时  │    4小时    │                            │
│  │  数据中心故障    │    < 24小时 │    24小时   │                            │
│  └─────────────────┴─────────────┴─────────────┘                            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        分级恢复流程                                   │   │
│  │                                                                     │   │
│  │   Level 1: 单服务故障                                               │   │
│  │   ┌─────────────────────────────────────────────────────────────┐  │   │
│  │   │  1. docker compose restart <服务名>                        │  │   │
│  │   │  2. 检查健康状态: docker compose ps                         │  │   │
│  │   │  3. 如需恢复: docker compose down && up -d                  │  │   │
│  │   └─────────────────────────────────────────────────────────────┘  │   │
│  │                                                                     │   │
│  │   Level 2: 数据库故障                                               │   │
│  │   ┌─────────────────────────────────────────────────────────────┐  │   │
│  │   │  1. 停止所有服务: docker compose stop                       │  │   │
│  │   │  2. 恢复 MySQL: gunzip < 备份.sql.gz | mysql               │  │   │
│  │   │  3. 恢复 ES: 执行快照恢复脚本                               │  │   │
│  │   │  4. 启动服务: docker compose start                          │  │   │
│  │   └─────────────────────────────────────────────────────────────┘  │   │
│  │                                                                     │   │
│  │   Level 3: 全量恢复                                                │   │
│  │   ┌─────────────────────────────────────────────────────────────┐  │   │
│  │   │  1. 使用最近备份重建所有服务                               │  │   │
│  │   │  2. 按依赖顺序启动: MySQL → Redis → ES → MinIO → RAGFlow │  │   │
│  │   │  3. 验证数据完整性                                          │  │   │
│  │   │  4. 更新 DNS/负载均衡                                       │  │   │
│  │   └─────────────────────────────────────────────────────────────┘  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 第五章：监控与告警

### 5.1 监控架构概述

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            监控架构                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         数据采集层                                   │   │
│  │                                                                     │   │
│  │   ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐      │   │
│  │   │ RAGFlow │  │ MySQL  │  │   ES   │  │ Redis  │  │ MinIO  │      │   │
│  │   │  服务   │  │        │  │        │  │        │  │        │      │   │
│  │   └────┬───┘  └────┬───┘  └────┬───┘  └────┬───┘  └────┬───┘      │   │
│  │        │           │           │           │           │          │   │
│  │        └───────────┴───────────┴───────────┴───────────┘          │   │
│  │                              │                                       │   │
│  │                              ▼                                       │   │
│  │                    ┌─────────────────┐                              │   │
│  │                    │  cAdvisor/Exporter │                              │   │
│  │                    │   容器指标采集器   │                              │   │
│  │                    └────────┬────────┘                              │   │
│  └─────────────────────────────┼───────────────────────────────────────┘   │
│                                │                                           │
│                                ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         时序数据存储                                 │   │
│  │                    ┌─────────────────┐                              │   │
│  │                    │   Prometheus    │                              │   │
│  │                    │   (时序数据库)   │                              │   │
│  │                    └────────┬────────┘                              │   │
│  └─────────────────────────────┼───────────────────────────────────────┘   │
│                                │                                           │
│                                ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         可视化展示层                                 │   │
│  │                    ┌─────────────────┐                              │   │
│  │                    │     Grafana     │                              │   │
│  │                    │   (仪表盘)      │                              │   │
│  │                    └─────────────────┘                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Prometheus 配置

```yaml
# /opt/monitoring/prometheus/prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'ragflow-prod'
    environment: 'production'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

rule_files:
  - "/etc/prometheus/rules/*.yml"

scrape_configs:
  # Prometheus 自身
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Docker 容器指标 (cAdvisor)
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  # RAGFlow 应用指标
  - job_name: 'ragflow'
    static_configs:
      - targets: ['ragflow-cpu:9380']
    metrics_path: '/probe'
    params:
      module: [http_2xx]

  # MySQL 指标 (mysqld_exporter)
  - job_name: 'mysql'
    static_configs:
      - targets: ['mysql-exporter:9104']

  # Redis 指标 (redis_exporter)
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  # Elasticsearch 指标
  - job_name: 'elasticsearch'
    static_configs:
      - targets: ['es01:9200']

  # MinIO 指标
  - job_name: 'minio'
    static_configs:
      - targets: ['minio:9000']
```

### 5.3 Docker Compose 监控配置

```yaml
# /opt/monitoring/docker-compose.yml

version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus/rules:/etc/prometheus/rules
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.enable-lifecycle'
    networks:
      - monitoring
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=你的Grafana密码
      - GF_USERS_ALLOW_SIGN_UP=false
    networks:
      - monitoring
    restart: unless-stopped

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    ports:
      - "8080:8080"
    networks:
      - monitoring
    restart: unless-stopped

  mysql-exporter:
    image: prom/mysqld-exporter:latest
    container_name: mysql-exporter
    environment:
      - DATA_SOURCE_NAME=root:${MYSQL_PASSWORD}@(mysql:3306)/
    networks:
      - monitoring
    depends_on:
      - mysql
    restart: unless-stopped

  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: redis-exporter
    environment:
      - REDIS_ADDR=redis:6379
      - REDIS_PASSWORD=${REDIS_PASSWORD}
    networks:
      - monitoring
    restart: unless-stopped

  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    volumes:
      - ./alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml
    ports:
      - "9093:9093"
    networks:
      - monitoring
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:

networks:
  monitoring:
    driver: bridge
```

### 5.4 告警规则设计

```yaml
# /opt/monitoring/prometheus/rules/ragflow-alerts.yml

groups:
  - name: ragflow-service
    rules:
      # 服务不可用告警
      - alert: RagflowServiceDown
        expr: up{job="ragflow"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "RAGFlow 服务不可用"
          description: "RAGFlow 服务已停止运行超过 1 分钟"

      # 服务响应慢告警
      - alert: RagflowHighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="ragflow"}[5m])) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "RAGFlow 响应时间过长"
          description: "P95 响应时间超过 5 秒"

  - name: resource-usage
    rules:
      # CPU 使用率高
      - alert: HighCPUUsage
        expr: rate(container_cpu_usage_seconds_total{name=~"ragflow.*"}[5m]) > 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "CPU 使用率过高"
          description: "容器 CPU 使用率超过 80% 超过 10 分钟"

      # 内存使用率高
      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes{name=~"ragflow.*"} / container_spec_memory_limit_bytes{name=~"ragflow.*"} > 0.85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "内存使用率过高"
          description: "容器内存使用率超过 85% 超过 5 分钟"

      # 磁盘空间不足
      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) < 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "磁盘空间不足"
          description: "根分区可用空间低于 10%"

  - name: database
    rules:
      # MySQL 连接数过高
      - alert: MySQLTooManyConnections
        expr: mysql_global_status_threads_connected > 800
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "MySQL 连接数过高"
          description: "MySQL 当前连接数 {{ $value }}，接近最大连接数"

      # MySQL 慢查询过多
      - alert: MySQLSlowQueries
        expr: rate(mysql_global_status_slow_queries[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "MySQL 慢查询过多"
          description: "MySQL 每秒慢查询数超过 10"

      # Redis 内存使用率高
      - alert: RedisHighMemory
        expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis 内存使用率过高"
          description: "Redis 内存使用率超过 90%"

  - name: elasticsearch
    rules:
      # Elasticsearch 集群健康
      - alert: ElasticsearchClusterRed
        expr: elasticsearch_cluster_health_status == 2
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Elasticsearch 集群状态异常"
          description: "Elasticsearch 集群状态为 RED"

      # Elasticsearch 磁盘空间
      - alert: ElasticsearchDiskLow
        expr: (elasticsearch_fs_available_bytes / elasticsearch_fs_total_bytes) < 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Elasticsearch 磁盘空间不足"
          description: "Elasticsearch 可用磁盘空间低于 10%"
```

### 5.5 日志聚合配置 (ELK)

```yaml
# Filebeat 配置 - 收集容器日志
filebeat.inputs:
  - type: container
    enabled: true
    paths:
      - /var/lib/docker/containers/*/*.log
    processors:
      - add_kubernetes_metadata:
          host: ${NODE_NAME}
          matchers:
            - logs_path:
                logs_path: "/var/lib/docker/containers/"

output.logstash:
  hosts: ["logstash:5044"]

# Logstash 配置
input {
  beats {
    port => 5044
  }
}

filter {
  if [container][name] =~ /ragflow/ {
    json {
      source => "message"
    }
    
    # 提取特定字段
    mutate {
      add_field => { "service" => "ragflow" }
    }
  }
  
  date {
    match => [ "time", "ISO8601" ]
    target => "@timestamp"
  }
}

output {
  elasticsearch {
    hosts => ["es01:9200"]
    index => "ragflow-logs-%{+YYYY.MM.dd}"
  }
}
```

### 5.6 健康检查脚本

```bash
#!/bin/bash
# /opt/scripts/health-check.sh
# 健康检查脚本

set -e

ES_HOST="localhost"
ES_PORT="1200"
MYSQL_HOST="localhost"
REDIS_HOST="localhost"
MINIO_HOST="localhost"

check_mysql() {
    echo "检查 MySQL..."
    docker exec docker-mysql-1 mysqladmin ping -h localhost -u root -p${MYSQL_PASSWORD} > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✓ MySQL 正常"
    else
        echo "✗ MySQL 异常"
        return 1
    fi
}

check_redis() {
    echo "检查 Redis..."
    docker exec docker-redis-1 redis-cli -a ${REDIS_PASSWORD} ping > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✓ Redis 正常"
    else
        echo "✗ Redis 异常"
        return 1
    fi
}

check_elasticsearch() {
    echo "检查 Elasticsearch..."
    curl -s -u elastic:${ELASTIC_PASSWORD} http://${ES_HOST}:${ES_PORT}/_cluster/health | grep -q '"status":"green"'
    if [ $? -eq 0 ]; then
        echo "✓ Elasticsearch 正常"
    else
        echo "✗ Elasticsearch 异常"
        return 1
    fi
}

check_minio() {
    echo "检查 MinIO..."
    curl -s -u ${MINIO_USER}:${MINIO_PASSWORD} http://${MINIO_HOST}:9000/minio/health/live | grep -q "ok"
    if [ $? -eq 0 ]; then
        echo "✓ MinIO 正常"
    else
        echo "✗ MinIO 异常"
        return 1
    fi
}

check_ragflow() {
    echo "检查 RAGFlow..."
    curl -s http://localhost:80/api/v1/health | grep -q "ok"
    if [ $? -eq 0 ]; then
        echo "✓ RAGFlow 正常"
    else
        echo "✗ RAGFlow 异常"
        return 1
    fi
}

# 执行所有检查
echo "=========================================="
echo "        RAGFlow 健康检查"
echo "=========================================="
echo "时间: $(date)"
echo "-------------------------------------------"

check_mysql || exit 1
check_redis || exit 1
check_elasticsearch || exit 1
check_minio || exit 1
check_ragflow || exit 1

echo "-------------------------------------------"
echo "所有检查通过！"
```

---

## 第六章：扩容与高可用

### 6.1 扩容策略概述

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            扩容策略                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        扩容决策树                                     │   │
│  │                                                                     │   │
│  │                        开始                                          │   │
│  │                          │                                           │   │
│  │                          ▼                                           │   │
│  │              ┌───────────────────────┐                              │   │
│  │              │   当前负载如何？       │                              │   │
│  │              └───────────┬───────────┘                              │   │
│  │                          │                                           │   │
│  │           ┌──────────────┼──────────────┐                            │   │
│  │           ▼              ▼              ▼                            │   │
│  │      < 50% CPU       50-80% CPU       > 80% CPU                       │   │
│  │      暂时不需要       准备扩容          立即扩容                      │   │
│  │           │              │              │                            │   │
│  │           │              ▼              ▼                            │   │
│  │           │     ┌──────────────┐  ┌──────────────┐                   │   │
│  │           │     │ 哪种瓶颈？   │  │ 哪种瓶颈？   │                   │   │
│  │           │     └──────┬───────┘  └──────┬───────┘                   │   │
│  │           │            │                 │                            │   │
│  │           │     ┌───────┴───────┐ ┌──────┴──────┐                     │   │
│  │           │     ▼               ▼ ▼             ▼                     │   │
│  │           │  CPU密集        I/O密集     水平扩展    增加硬件            │   │
│  │           │  增加CPU        增加磁盘    多实例部署   资源              │   │
│  │           │                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 水平扩容方案

#### 6.2.1 Docker Compose 水平扩展

```bash
# 当前架构：单节点
docker compose -f docker-compose.yml up -d ragflow-cpu

# 扩容为 3 个实例（需要配合负载均衡）
docker compose -f docker-compose.yml up -d --scale ragflow-cpu=3

# 使用 nginx 负载均衡（见下一节）
```

#### 6.2.2 负载均衡配置

```nginx
# nginx.conf - 负载均衡配置

upstream ragflow_backend {
    # 轮询策略（默认）
    server ragflow-01:80;
    server ragflow-02:80;
    server ragflow-03:80;
    
    # 权重配置（根据服务器性能调整）
    # server ragflow-01:80 weight=3;
    # server ragflow-02:80 weight=2;
    # server ragflow-03:80 weight=1;
    
    # 保持会话（重要！避免用户状态丢失）
    ip_hash;
    
    # 健康检查
    server ragflow-01:80 max_fails=3 fail_timeout=30s;
    server ragflow-02:80 max_fails=3 fail_timeout=30s;
    server ragflow-03:80 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://ragflow_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 6.3 MySQL 主从复制

#### 6.3.1 主从架构说明

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MySQL 主从复制架构                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│      写操作                              读操作                               │
│        │                                  │                                 │
│        ▼                                  ▼                                 │
│   ┌─────────┐                      ┌─────────┐                             │
│   │  负载   │                      │  负载   │                             │
│   │  均衡   │                      │  均衡   │                             │
│   └────┬────┘                      └────┬────┘                             │
│        │                                │                                  │
│        ▼                                ▼                                  │
│   ┌─────────┐                      ┌────┴────┐                             │
│   │  主库   │◄───── 复制 ─────────│  从库1  │                             │
│   │ (写)   │                      │  (读)   │                             │
│   └────┬───┘                      └─────────┘                             │
│        │                                │                                  │
│        │                          ┌─────┴─────┐                             │
│        │                          │  从库2    │                             │
│        │                          │  (读)    │                             │
│        │                          └──────────┘                             │
│        │                                                                   │
│        ▼                                                                   │
│   ┌─────────┐                                                             │
│   │  备份   │                                                             │
│   │         │                                                             │
│   └─────────┘                                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 6.3.2 主库配置 (master)

```ini
# /etc/mysql/conf.d/master.cnf

[mysqld]
server-id = 1
log_bin = /var/log/mysql/mysql-bin
binlog_format = ROW
binlog_expire_logs_seconds = 604800  # 7天
sync_binlog = 1

# 只复制特定数据库
binlog_do_db = rag_flow

# 复制限流
# max_allowed_packet = 256M
# slave_net_timeout = 60
```

#### 6.3.3 从库配置 (slave)

```ini
# /etc/mysql/conf.d/slave.cnf

[mysqld]
server-id = 2
log_bin = /var/log/mysql/mysql-bin
relay_log = /var/log/mysql/mysql-relay-bin
read_only = ON
super_read_only = ON

# 复制延迟告警
# slave_net_timeout = 60
# log_slave_updates = ON
```

#### 6.3.4 配置主从复制

```sql
-- 主库：创建复制用户
CREATE USER 'repl'@'%' IDENTIFIED BY 'repl_password';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';
FLUSH PRIVILEGES;

-- 主库：获取二进制日志位置
SHOW MASTER STATUS;
-- 记录 File 和 Position

-- 从库：配置主从复制
CHANGE MASTER TO
    MASTER_HOST='master-host',
    MASTER_USER='repl',
    MASTER_PASSWORD='repl_password',
    MASTER_LOG_FILE='mysql-bin.000001',
    MASTER_LOG_POS=123;

-- 从库：启动复制
START SLAVE;

-- 从库：检查复制状态
SHOW SLAVE STATUS\G
-- 确认 Slave_IO_Running 和 Slave_SQL_Running 都是 Yes
```

### 6.4 Elasticsearch 集群配置

#### 6.4.1 集群架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Elasticsearch 集群架构                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        ES 集群 (3节点)                               │   │
│  │                                                                     │   │
│  │   ┌──────────┐  ┌──────────┐  ┌──────────┐                        │   │
│  │   │  Master  │  │  Master  │  │  Master  │                        │   │
│  │   │  Node-1  │  │  Node-2  │  │  Node-3  │                        │   │
│  │   │ (数据节点)│  │ (数据节点)│  │ (数据节点)│                        │   │
│  │   └──────────┘  └──────────┘  └──────────┘                        │   │
│  │                                                                     │   │
│  │   配置：                                                            │   │
│  │   - 3个主节点（避免脑裂）                                            │   │
│  │   - 1个副本分片（数据安全性）                                        │   │
│  │   - 2个主分片（并行处理）                                            │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 6.4.2 集群配置示例

```yaml
# docker-compose-es-cluster.yml

services:
  es01:
    image: elasticsearch:${STACK_VERSION}
    container_name: es01
    environment:
      - node.name=es01
      - cluster.name=ragflow-cluster
      - discovery.seed_hosts=es02,es03
      - cluster.initial_master_nodes=es01,es02,es03
      - ELASTIC_PASSWORD=${ELASTIC_PASSWORD}
      - bootstrap.memory_lock=true
      - discovery.type=single-node  # 单节点模式，生产用上面配置
    volumes:
      - esdata01:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
      - "9300:9300"
    mem_limit: 4g
    ulimits:
      memlock:
        soft: -1
        hard: -1
    networks:
      - es-cluster
    healthcheck:
      test: ["CMD-SHELL", "curl -s http://localhost:9200 | grep -q 'cluster_name'"]
      interval: 30s
      timeout: 10s
      retries: 5

  es02:
    image: elasticsearch:${STACK_VERSION}
    container_name: es02
    environment:
      - node.name=es02
      - cluster.name=ragflow-cluster
      - discovery.seed_hosts=es01,es03
      - ELASTIC_PASSWORD=${ELASTIC_PASSWORD}
      - bootstrap.memory_lock=true
    volumes:
      - esdata02:/usr/share/elasticsearch/data
    mem_limit: 4g
    ulimits:
      memlock:
        soft: -1
        hard: -1
    networks:
      - es-cluster
    depends_on:
      - es01

  es03:
    image: elasticsearch:${STACK_VERSION}
    container_name: es03
    environment:
      - node.name=es03
      - cluster.name=ragflow-cluster
      - discovery.seed_hosts=es01,es02
      - ELASTIC_PASSWORD=${ELASTIC_PASSWORD}
      - bootstrap.memory_lock=true
    volumes:
      - esdata03:/usr/share/elasticsearch/data
    mem_limit: 4g
    ulimits:
      memlock:
        soft: -1
        hard: -1
    networks:
      - es-cluster
    depends_on:
      - es01

volumes:
  esdata01:
  esdata02:
  esdata03:

networks:
  es-cluster:
    driver: bridge
```

### 6.5 高可用方案总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           高可用架构总结                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        组件级高可用                                  │   │
│  │                                                                     │   │
│  │   组件          │  高可用方案           │  故障切换时间            │   │
│  │   ─────────────┼──────────────────────┼───────────────           │   │
│  │   RAGFlow      │  多实例 + 负载均衡    │    < 30秒                │   │
│  │   MySQL        │  主从切换            │    < 5分钟               │   │
│  │   Redis        │  主从 + 哨兵         │    < 30秒                │   │
│  │   Elasticsearch│  集群多节点          │    < 1分钟               │   │
│  │   MinIO        │  纠删码模式          │    < 5分钟               │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        推荐架构（中等规模）                          │   │
│  │                                                                     │   │
│  │                        ┌─────────────┐                              │   │
│  │                        │   负载均衡   │                              │   │
│  │                        │   (SLB)     │                              │   │
│  │                        └──────┬──────┘                              │   │
│  │                               │                                      │   │
│  │            ┌───────────────────┼───────────────────┐                  │   │
│  │            │                   │                   │                  │   │
│  │            ▼                   ▼                   ▼                  │   │
│  │      ┌──────────┐       ┌──────────┐       ┌──────────┐              │   │
│  │      │  RAGFlow │       │  RAGFlow │       │  RAGFlow │              │   │
│  │      │  实例-1  │       │  实例-2  │       │  实例-3  │              │   │
│  │      └────┬─────┘       └────┬─────┘       └────┬─────┘              │   │
│  │           │                   │                   │                  │   │
│  │           └───────────────────┼───────────────────┘                  │   │
│  │                               │                                      │   │
│  │         ┌──────────┬──────────┼──────────┬──────────┐               │   │
│  │         │          │          │          │          │               │   │
│  │         ▼          ▼          ▼          ▼          ▼               │   │
│  │    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐           │   │
│  │    │  RDS   │ │  Redis │ │   ES   │ │  MinIO │ │   OSS  │           │   │
│  │    │ 主从   │ │ 集群   │ │ 集群   │ │ 纠删码 │ │  备份  │           │   │
│  │    └────────┘ └────────┘ └────────┘ └────────┘ └────────┘           │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 附录：故障排查与常见问题

### A.1 启动失败排查

```bash
# 1. 检查 Docker 服务状态
systemctl status docker

# 2. 查看容器日志
docker logs -f docker-ragflow-cpu-1
docker logs -f docker-mysql-1
docker logs -f docker-es01-1

# 3. 检查端口占用
netstat -tlnp | grep -E "80|3306|9200|6379|9000"

# 4. 检查资源限制
docker stats

# 5. 检查网络连通性
docker exec docker-ragflow-cpu-1 ping mysql
docker exec docker-ragflow-cpu-1 ping es01
```

### A.2 常见问题与解决方案

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 服务启动缓慢 | ES 首次创建索引 | 等待 5-10 分钟 |
| 无法访问 Web UI | 端口未开放 | 检查安全组规则 |
| API 返回 502 | 后端服务未启动 | 检查 ragflow 日志 |
| 数据库连接失败 | 密码错误 | 检查 .env 配置 |
| 磁盘空间不足 | 日志未清理 | 清理日志或扩容 |
| 内存不足 (OOM) | 资源限制过小 | 调大 MEM_LIMIT |

### A.3 性能优化建议

```bash
# 1. 清理 Docker 资源
docker system prune -a --volumes

# 2. 清理日志文件
find /var/lib/docker/containers -name "*.log" -size +100M -exec truncate -s 0 {} \;

# 3. 优化 MySQL
docker exec docker-mysql-1 mysql -u root -p -e "OPTIMIZE TABLE rag_flow.document;"

# 4. 重建 ES 索引（谨慎操作）
curl -X POST "http://localhost:1200/_reindex" \
    -u elastic:${ELASTIC_PASSWORD} \
    -H 'Content-Type: application/json' \
    -d '{"source":{"index":"ragflow_doc"},"dest":{"index":"ragflow_doc_v2"}}'
```

### A.4 紧急联系方式

- **官方文档**: https://ragflow.io/docs
- **GitHub Issues**: https://github.com/infiniflow/ragflow/issues
- **社区论坛**: https://github.com/infiniflow/ragflow/discussions

---

## 文档版本历史

| 版本 | 日期 | 作者 | 说明 |
|------|------|------|------|
| v1.0 | 2026-01 | - | 初始版本，涵盖部署、运维、监控、扩容全流程 |

---

*本文档由 AI 生成，如有疑问请联系技术支持。*
