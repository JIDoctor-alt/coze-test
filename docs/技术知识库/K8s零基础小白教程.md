# K8s零基础小白教程（上）

![K8s](https://www.coze.cn/s/JqVhDq6lmkg/)

## 教程概述

本教程专为Kubernetes（K8s）零基础小白设计，通过生动的比喻和实际案例，让你从零开始掌握K8s的核心知识。整个教程分为上、下两部分：

- **上半部分（第1-5篇）**：容器基础、K8s架构、核心资源对象、服务发现与网络、配置与存储
- **下半部分（第6-10篇）**：安全机制、资源管理、日志监控、Helm包管理、实战项目

### 学习路径图

```
容器基础 → K8s架构 → 核心资源对象 → 服务发现与网络 → 配置与存储
    ↓           ↓            ↓              ↓              ↓
 Docker命令  Master/Node   Pod/Deployment  Service/Ingress  ConfigMap/Secret
   Dockerfile   kubectl     StatefulSet     NetworkPolicy    PV/PVC
   Docker Compose             DaemonSet      CoreDNS         StorageClass
```

---

## 目录

1. [第一篇：容器基础](#第一篇容器基础)
2. [第二篇：K8s架构](#第二篇k8s架构)
3. [第三篇：核心资源对象](#第三篇核心资源对象)
4. [第四篇：服务发现与网络](#第四篇服务发现与网络)
5. [第五篇：配置与存储](#第五篇配置与存储)

---

# 第一篇：容器基础

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

## 前言：从集装箱到容器

想象一下，你是一个开网店的老板。以前发货是这样：每个客户定制一个专属包装盒，包装大小、材料、填充物都不一样。结果仓库乱成一锅粥，发货速度慢得跟蜗牛似的。

后来有个聪明人发明了**集装箱**。不管你卖的是鞋子、衣服还是电子产品，统统装进统一规格的集装箱里。轮船、火车、卡车都能运，全世界通用。

**Docker容器就是软件世界的集装箱。**

---

## 1.1 什么是容器？

### 一句话人话
**容器**是一个轻量级的、独立的、可运行的软件包，里面包含了程序运行所需的一切（代码、依赖库、环境变量、配置文件）。

### 生活比喻 🔥
就像**真空包装的方便食品**：
- 你不需要厨房（不需要配置运行环境）
- 打开就能吃（运行就能用）
- 携带方便（可以到处部署）
- 每次味道一样（环境一致）

### 核心概念

**容器的三大特性：**

| 特性 | 解释 | 比喻 |
|------|------|------|
| **轻量级** | 共享宿主机内核，不需要虚拟化整个操作系统 | 共用厨房 vs 每家一个厨房 |
| **独立性** | 容器之间互相隔离，互不干扰 | 公寓的各个房间 |
| **可移植性** | 一次构建，到处运行 | 集装箱全球通用 |

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

**⚠️ 小白易懵点**

> 很多人搞不清"镜像"和"容器"的区别：
> - **镜像（Image）**：就像菜谱，是只读的模板
> - **容器（Container）**：就像按照菜谱做出来的菜，是运行中的实例
> 
> 可以用菜谱做很多份菜，一个镜像也可以创建多个容器。

---

## 1.2 容器 vs 虚拟机

### 一句话人话
**虚拟机**是一台完整的电脑，**容器**是共享电脑资源的隔间。

### 生活比喻 🔥

**虚拟机 = 独栋别墅**
- 每栋别墅有独立的上下水系统、电网、供暖
- 隔音好，安全私密
- 建造和维护成本高（占用资源多）
- 建造时间长（启动慢）

**容器 = 合租公寓**
- 多人共享厨房、卫生间、客厅
- 节省空间和费用（共享资源）
- 隐私性稍差（隔离性较弱）
- 入住快（启动快）

### 核心对比表

| 对比项 | 虚拟机 | 容器 |
|--------|--------|------|
| 启动时间 | 分钟级 | 秒级 |
| 占用资源 | 完整操作系统，通常GB级 | 共享内核，MB级 |
| 隔离性 | 硬件级隔离，强 | 操作系统级隔离，弱 |
| 移植性 | 需要完整镜像 | 一次构建，到处运行 |
| 性能开销 | 5-15%开销 | 几乎无开销 |
| 密度 | 一台主机跑几个VM | 一台主机跑几十个容器 |

### 技术原理

**虚拟机架构：**
```
┌─────────────────────────────────────────────────────────┐
│                      物理服务器                          │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   虚拟机1    │  │   虚拟机2    │  │   虚拟机3    │     │
│  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │     │
│  │ │ GuestOS │ │  │ │ GuestOS │ │  │ │ GuestOS │ │     │
│  │ ├─────────┤ │  │ ├─────────┤ │  │ ├─────────┤ │     │
│  │ │  App1   │ │  │ │  App2   │ │  │ │  App3   │ │     │
│  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                │                │            │
│  ┌──────┴────────────────┴────────────────┴──────┐     │
│  │              Hypervisor (VMware/KVM)           │     │
│  └──────────────────────┬────────────────────────┘     │
└─────────────────────────┼───────────────────────────────┘
                          │
                    ┌─────┴─────┐
                    │   硬件    │
                    └───────────┘
```

**容器架构：**
```
┌─────────────────────────────────────────────────────────┐
│                      物理服务器                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   容器1     │  │   容器2     │  │   容器3     │     │
│  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │     │
│  │ │  App1   │ │  │ │  App2   │ │  │ │  App3   │ │     │
│  │ └────┬────┘ │  │ └────┬────┘ │  │ └────┬────┘ │     │
│  └──────┼──────┘  └──────┼──────┘  └──────┼──────┘     │
│         │                │                │            │
│  ┌──────┴────────────────┴────────────────┴──────┐     │
│  │              容器运行时 (containerd)            │     │
│  └──────────────────────┬────────────────────────┘     │
├─────────────────────────┼───────────────────────────────┤
│  ┌──────────────────────┴────────────────────────┐       │
│  │                 操作系统内核                   │       │
│  └──────────────────────┬────────────────────────┘       │
└─────────────────────────┼───────────────────────────────┘
                          │
                    ┌─────┴─────┐
                    │   硬件    │
                    └───────────┘
```

**💡 一句话总结**

> 容器比虚拟机更轻量、更快、更省资源，但隔离性稍弱。就像合租公寓比独栋别墅更经济实惠，但隐私性稍差。

---

## 1.3 Docker安装与基础命令

### 一句话人话
**Docker**是最流行的容器技术，学习K8s前必须掌握Docker基础。

### 安装Docker

**macOS/Windows 安装：**
```bash
# 下载 Docker Desktop
# https://www.docker.com/products/docker-desktop

# 安装后验证
docker --version
docker-compose --version
```

**Linux (Ubuntu) 安装：**
```bash
# 更新apt包索引
sudo apt-get update

# 安装依赖包
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# 添加Docker官方GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加Docker仓库
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 添加当前用户到docker组（免sudo）
sudo usermod -aG docker $USER

# 验证安装
docker --version
```

**⚠️ 小白易懵点**

> 如果遇到 "permission denied" 错误，记得把当前用户加入docker组：
> ```bash
> sudo usermod -aG docker $USER
> # 然后重新登录或执行
> newgrp docker
> ```

### 镜像基础命令

**拉取镜像（下载集装箱）：**
```bash
# 拉取官方镜像（不指定tag默认为latest）
docker pull nginx

# 拉取指定版本
docker pull nginx:1.25.4

# 拉取指定仓库的镜像
docker pull docker.io/library/nginx:latest

# 拉取私有仓库镜像（需要登录）
docker login your-registry.com
docker pull your-registry.com/your-project/your-image:tag
```

**查看镜像：**
```bash
# 列出本地所有镜像
docker images

# 列出镜像ID（简洁模式）
docker images -q

# 查看镜像详细信息
docker inspect nginx:latest

# 列出悬空镜像（没有标签的镜像）
docker images -f dangling=true
```

**删除镜像：**
```bash
# 删除指定镜像
docker rmi nginx:latest

# 强制删除
docker rmi -f nginx:latest

# 删除所有未使用的镜像
docker image prune

# 删除所有镜像（谨慎使用！）
docker rmi $(docker images -q)
```

**镜像构建：**
```bash
# 根据Dockerfile构建镜像
docker build -t my-app:1.0.0 .

# 指定构建上下文和Dockerfile路径
docker build -t my-app:1.0.0 -f ./docker/Dockerfile ./project

# 构建时传入构建参数
docker build --build-arg VERSION=1.0.0 -t my-app:1.0.0 .

# 构建时设置标签
docker build -t my-app:latest -t my-app:1.0.0 .
```

**⚠️ 小白易懵点**

> **docker build -t** 中的 `-t` 是 `--tag` 的缩写，用来设置镜像名称和标签。
> 
> 镜像命名规则：`[registry/][username/]name:tag`
> - `nginx:latest` → Docker Hub官方镜像
> - `my-username/my-app:1.0` → 个人镜像
> - `registry.company.com/project/app:1.0` → 私有仓库镜像

### 容器基础命令

**创建和启动容器：**
```bash
# 交互式创建并启动容器
docker run -it ubuntu:latest /bin/bash

# 守护式运行（后台运行）
docker run -d nginx:latest

# 命名容器
docker run -d --name my-nginx nginx:latest

# 端口映射（宿主机端口:容器端口）
docker run -d -p 8080:80 --name my-nginx nginx:latest

# 设置环境变量
docker run -d -e APP_ENV=production --name my-app my-app:1.0

# 挂载数据卷
docker run -d -v /host/path:/container/path --name my-app my-app:1.0

# 分配资源
docker run -d --memory="512m" --cpus="0.5" --name my-app my-app:1.0
```

**参数解释：**
| 参数 | 全称 | 作用 |
|------|------|------|
| `-i` | `--interactive` | 交互模式，保持STDIN打开 |
| `-t` | `--tty` | 分配伪终端 |
| `-d` | `--detach` | 后台运行 |
| `-p` | `--publish` | 端口映射 |
| `-e` | `--env` | 设置环境变量 |
| `-v` | `--volume` | 挂载数据卷 |
| `-w` | `--workdir` | 设置工作目录 |
| `--name` | - | 给容器命名 |
| `--rm` | - | 容器退出后自动删除 |
| `--memory` | - | 限制内存 |
| `--cpus` | - | 限制CPU |

**查看容器：**
```bash
# 列出正在运行的容器
docker ps

# 列出所有容器（包括已停止）
docker ps -a

# 只显示容器ID
docker ps -q

# 显示容器详细信息
docker inspect my-nginx

# 实时查看容器资源使用
docker stats

# 查看容器进程
docker top my-nginx
```

**启动/停止/重启：**
```bash
# 启动已停止的容器
docker start my-nginx

# 停止运行中的容器
docker stop my-nginx

# 强制停止（发送SIGKILL）
docker kill my-nginx

# 重启容器
docker restart my-nginx

# 暂停容器
docker pause my-nginx

# 恢复容器
docker unpause my-nginx
```

**删除容器：**
```bash
# 删除已停止的容器
docker rm my-nginx

# 强制删除（即使在运行）
docker rm -f my-nginx

# 删除所有已停止的容器
docker container prune

# 删除所有容器（谨慎使用！）
docker rm -f $(docker ps -aq)
```

**⚠️ 小白易懵点**

> **docker rm vs docker rmi**
> - `docker rm` 删除**容器**（Container）
> - `docker rmi` 删除**镜像**（Image）
> 
> 就像"删除菜"和"删除菜谱"的区别。

### 进入容器

```bash
# 进入运行中的容器（打开容器的终端）
docker exec -it my-nginx /bin/bash

# 在容器中执行单个命令
docker exec my-nginx ls /usr/share/nginx/html

# 指定用户进入
docker exec -it -u root my-nginx /bin/bash

# 分离模式进入（Ctrl+P, Ctrl+Q 退出）
docker attach my-nginx
```

**⚠️ 小白易懵点**

> `docker attach` 和 `docker exec` 的区别：
> - `attach`：进入容器的**主进程**终端，多个终端会共享同一个屏幕
> - `exec`：在容器中**新建一个进程**终端，不会影响主进程
> 
> 建议使用 `docker exec`，不会干扰容器的主进程。

### 日志和监控

```bash
# 查看容器日志
docker logs my-nginx

# 实时跟踪日志
docker logs -f my-nginx

# 显示最近50行日志
docker logs --tail 50 my-nginx

# 显示日志时间戳
docker logs -t my-nginx

# 查找包含特定内容的日志
docker logs my-nginx | grep "error"
```

### 完整实操：运行一个Web应用

```bash
# 1. 拉取一个简单的Web应用镜像
docker pull nginx:alpine

# 2. 创建本地目录用于存放网页
mkdir -p ~/my-website
echo "<h1>Hello Docker!</h1>" > ~/my-website/index.html

# 3. 运行容器
docker run -d \
  --name my-website \
  -p 8080:80 \
  -v ~/my-website:/usr/share/nginx/html:ro \
  nginx:alpine

# 4. 验证运行
docker ps

# 5. 访问测试
curl http://localhost:8080

# 6. 查看日志
docker logs my-website

# 7. 进入容器查看
docker exec -it my-website /bin/sh

# 8. 清理
docker stop my-website
docker rm my-website
```

**💡 一句话总结**

> Docker命令的规律：`docker + 操作 + 目标`，常用操作有 pull/run/ps/logs/exec/stop/rm 等。

---

## 1.4 Dockerfile编写

### 一句话人话
**Dockerfile**是容器的"菜谱"，告诉你如何从零构建一个镜像。

### 生活比喻 🔥

Dockerfile就像**泡面的说明书**：
1. 准备好面饼和调料包（基础镜像）
2. 撕开面饼包装（FROM）
3. 倒入热水（RUN）
4. 盖上盖子等待（等待）
5. 加入调料搅拌（COPY）

### 核心指令

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

| 指令 | 作用 | 类比 |
|------|------|------|
| `FROM` | 指定基础镜像 | 泡面包装 |
| `RUN` | 执行命令 | 加热水 |
| `COPY` | 复制文件 | 放调料 |
| `WORKDIR` | 设置工作目录 | 指定地点 |
| `EXPOSE` | 声明端口 | 开窗户 |
| `ENV` | 设置环境变量 | 贴标签 |
| `ARG` | 构建参数 | 备选材料 |
| `CMD` | 容器启动命令 | 开吃 |
| `ENTRYPOINT` | 容器主程序 | 正餐 |

### FROM - 基础镜像

```dockerfile
# 使用官方基础镜像
FROM ubuntu:22.04

# 使用官方运行时镜像（体积更小）
FROM python:3.11-slim

# 使用Alpine镜像（更小）
FROM node:18-alpine

# 使用 scratch（最原始，不包含任何系统）
FROM scratch
```

### RUN - 执行命令

```dockerfile
# 安装软件包
RUN apt-get update && apt-get install -y \
    curl \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# 创建目录
RUN mkdir -p /app

# 下载文件
RUN curl -o /app/app.jar https://example.com/app.jar

# 清理缓存（减小镜像体积）
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*
```

**⚠️ 小白易懵点**

> **多行RUN命令要合并**，因为Dockerfile的每一层都会占用空间。最好这样：
> ```dockerfile
> # 错误示范：产生多层镜像
> RUN apt-get update
> RUN apt-get install -y curl
> RUN apt-get install -y git
> RUN rm -rf /var/lib/apt/lists/*
> 
> # 正确示范：合并为一个RUN
> RUN apt-get update && \
>     apt-get install -y curl git && \
>     rm -rf /var/lib/apt/lists/*
> ```

### COPY - 复制文件

```dockerfile
# 复制当前目录的文件到容器的/app目录
COPY . /app

# 复制并重命名
COPY app.jar /app/application.jar

# 复制多个文件
COPY config.json package.json /app/

# 使用通配符
COPY *.js /app/

# 复制到远程目录（构建上下文中）
COPY ./src /app/src
```

### WORKDIR - 工作目录

```dockerfile
# 设置工作目录
WORKDIR /app

# 创建目录并设置为工作目录（目录不存在会自动创建）
WORKDIR /app/src

# 使用环境变量
WORKDIR $APP_HOME
```

### EXPOSE - 声明端口

```dockerfile
# 声明容器监听的端口
EXPOSE 80
EXPOSE 443
EXPOSE 8080
EXPOSE 80 443 8080
```

**⚠️ 小白易懵点**

> `EXPOSE` 只是**声明**，并不会真正打开端口。需要在运行时用 `-p` 参数映射：
> ```bash
> docker run -p 8080:80 my-image  # 才会真正打开端口
> ```

### ENV - 环境变量

```dockerfile
# 设置环境变量
ENV APP_ENV=production
ENV DB_HOST=localhost
ENV DB_PORT=3306

# 设置多个环境变量
ENV APP_NAME="MyApp" \
    APP_VERSION="1.0.0" \
    APP_PORT=8080
```

### ARG - 构建参数

```dockerfile
# 定义构建参数
ARG VERSION=1.0
ARG USER=admin

# 使用参数
RUN echo "Building version $VERSION"

# 在构建时传入
# docker build --build-arg VERSION=2.0 -t my-app .
```

**ARG vs ENV 的区别：**
| 特性 | ARG | ENV |
|------|-----|-----|
| 作用时机 | 构建时 | 运行时 |
| 是否保留在镜像 | 否 | 是 |
| 可在运行时覆盖 | 否 | 是 |

### CMD - 启动命令

```dockerfile
# 格式1：exec形式（推荐）
CMD ["python", "app.py"]

# 格式2：shell形式
CMD python app.py

# 格式3：作为ENTRYPOINT的参数
CMD ["--port", "8080"]
```

### ENTRYPOINT - 主程序入口

```dockerfile
# 定义主程序
ENTRYPOINT ["python", "app.py"]

# 组合使用ENTRYPOINT和CMD
ENTRYPOINT ["python", "app.py"]
CMD ["--help"]  # 默认参数
```

**CMD vs ENTRYPOINT 的区别：**
| 指令 | 作用 | 使用场景 |
|------|------|----------|
| CMD | 提供默认参数，可被覆盖 | 容器默认行为 |
| ENTRYPOINT | 定义主程序，不易被覆盖 | 必须运行的程序 |

### 完整示例：Node.js应用

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```dockerfile
# ============================================
# Node.js 应用 Dockerfile
# 适用于：Express/Koa/NestJS 等框架
# ============================================

# 1. 使用官方Node.js镜像作为构建阶段
FROM node:18-alpine AS builder

# 2. 设置工作目录
WORKDIR /app

# 3. 先复制 package.json（利用Docker缓存）
COPY package*.json ./

# 4. 安装依赖（包含devDependencies用于构建）
RUN npm ci --only=production=false

# 5. 复制源代码
COPY . .

# 6. 构建应用（如果是Next.js/Nuxt等SSR框架）
RUN npm run build

# ============================================
# 第二阶段：生产环境镜像
# ============================================
FROM node:18-alpine

# 7. 设置Node环境变量
ENV NODE_ENV=production

# 8. 创建应用目录
WORKDIR /app

# 9. 从构建阶段复制产物
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

# 10. 切换到非root用户运行（安全最佳实践）
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

USER nodejs

# 11. 暴露端口
EXPOSE 3000

# 12. 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# 13. 启动命令
CMD ["node", "dist/main.js"]
```

### 完整示例：Java Spring Boot应用

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```dockerfile
# ============================================
# Spring Boot 应用 Dockerfile
# 适用于：Spring Boot 2.x/3.x
# ============================================

# 第一阶段：Maven构建
FROM maven:3.9-eclipse-temurin-17 AS builder

WORKDIR /app

# 先复制 pom.xml（利用缓存）
COPY pom.xml ./

# 下载依赖（不在同一层，避免每次改动代码都重新下载）
RUN mvn dependency:go-offline -B

# 复制源代码
COPY src ./src

# 构建应用
RUN mvn clean package -DskipTests

# ============================================
# 第二阶段：运行阶段（JRE比JDK体积小很多）
# ============================================
FROM eclipse-temurin:17-jre-alpine

# 创建非root用户（安全）
RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -s /bin/sh -D appuser

WORKDIR /app

# 从构建阶段复制JAR包
COPY --from=builder /app/target/*.jar app.jar

# 修改文件所有者
RUN chown -R appuser:appgroup /app

# 切换用户
USER appuser

# JVM参数优化
ENV JAVA_OPTS="-Xms256m -Xmx512m -XX:+UseG1GC"

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

# 启动命令
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

### 完整示例：Python Flask应用

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```dockerfile
# ============================================
# Flask 应用 Dockerfile
# ============================================

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖（某些Python包需要编译）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# 启动命令
CMD ["python", "app.py"]
```

**⚠️ 小白易懵点**

> **HEALTHCHECK** 非常重要！它让Docker知道容器是否"健康"：
> - 不健康时，Docker可以自动重启容器
> - 在Docker Swarm或K8s中，健康检查决定Pod是否接收流量

**💡 一句话总结**

> Dockerfile编写原则：层数少、缓存好、体积小。用多阶段构建分离构建和运行环境，使用非root用户运行。

---

## 1.5 Docker Compose多容器编排

### 一句话人话
**Docker Compose**是用一个文件同时管理多个容器（服务），就像点一桌菜而不是一道道点。

### 生活比喻 🔥

想象你去餐厅吃饭：

**不用Docker Compose（单点）：**
```
服务员，我要一份宫保鸡丁
服务员，我要一碗米饭
服务员，我要一杯可乐
服务员，我要一份麻辣香锅
...
```
累死了！要跟服务员说很多次。

**用Docker Compose（套餐）：**
```
服务员，我要一个四人套餐（含：宫保鸡丁、米饭4碗、可乐4杯、麻辣香锅）
```
一个命令全搞定！

### Docker Compose安装

```bash
# 安装 Docker Desktop 后自带
docker-compose --version

# 或单独安装
sudo apt-get install docker-compose-plugin

# 验证
docker compose version
```

### docker-compose.yml 结构

```yaml
# ============================================
# Docker Compose 配置文件
# ============================================

# 版本（建议使用最新版本，但也要与Docker版本兼容）
version: '3.8'

# 服务定义（就是你要管理的容器）
services:
  # 服务名称（随便起，用于服务间互相访问）
  web:
    image: nginx:alpine                    # 使用哪个镜像
    container_name: my-web                # 容器名称
    ports:                                 # 端口映射
      - "8080:80"
    volumes:                               # 数据卷挂载
      - ./html:/usr/share/nginx/html:ro
    environment:                           # 环境变量
      - NGINX_HOST=example.com
      - NGINX_PORT=80
    depends_on:                            # 依赖关系（启动顺序）
      - api
    networks:                              # 所属网络
      - frontend
    restart: unless-stopped               # 重启策略

  api:
    image: node:18-alpine
    container_name: my-api
    working_dir: /app
    volumes:
      - ./api:/app
    command: npm start
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DB_HOST=db
      - DB_PORT=5432
    depends_on:
      db:
        condition: service_healthy        # 等待db健康后再启动
    networks:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 3s
      retries: 3

  db:
    image: postgres:15-alpine
    container_name: my-db
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secretpassword
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d myapp"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: my-redis
    command: redis-server --requirepass redispassword
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - backend
    restart: unless-stopped

# 数据卷定义（持久化存储）
volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

# 网络定义（让容器可以互相通信）
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # 内部网络，无法访问外网，更安全
```

### 常用命令

```bash
# 启动所有服务（后台运行）
docker compose up -d

# 启动所有服务（前台运行，可以看到日志）
docker compose up

# 重新构建并启动
docker compose up -d --build

# 停止并删除所有服务
docker compose down

# 停止并删除所有服务，以及数据卷
docker compose down -v

# 查看服务状态
docker compose ps

# 查看所有服务日志
docker compose logs

# 查看指定服务日志
docker compose logs -f api

# 执行命令（进入容器）
docker compose exec api sh

# 查看服务详情
docker compose config

# 扩展服务（启动多个实例）
docker compose up -d --scale api=3

# 暂停/恢复服务
docker compose pause/unpause

# 重启服务
docker compose restart
```

### 完整示例：WordPress博客

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: mysql:8.0
    container_name: wordpress_db
    restart: unless-stopped
    environment:
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: wordpress_password
      MYSQL_ROOT_PASSWORD: root_password
    volumes:
      - db_data:/var/lib/mysql
    networks:
      - wordpress_network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  wordpress:
    image: wordpress:php8.2-apache
    container_name: wordpress_app
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: wordpress_password
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - wordpress_data:/var/www/html
    ports:
      - "8080:80"
    networks:
      - wordpress_network

volumes:
  db_data:
  wordpress_data:

networks:
  wordpress_network:
    driver: bridge
```

**使用方式：**
```bash
# 启动
docker compose up -d

# 访问 http://localhost:8080 完成WordPress安装向导

# 停止并清理
docker compose down -v
```

### 完整示例：Spring Boot + MySQL + Redis

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
version: '3.8'

services:
  # Java后端服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: springboot-backend
    ports:
      - "8080:8080"
    environment:
      SPRING_PROFILES_ACTIVE: docker
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/myapp?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC
      SPRING_DATASOURCE_USERNAME: appuser
      SPRING_DATASOURCE_PASSWORD: apppassword
      SPRING_REDIS_HOST: redis
      SPRING_REDIS_PORT: 6379
      SPRING_REDIS_PASSWORD: redispass
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - app-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # MySQL数据库
  mysql:
    image: mysql:8.0
    container_name: mysql-db
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: myapp
      MYSQL_USER: appuser
      MYSQL_PASSWORD: apppassword
    volumes:
      - mysql_data:/var/lib/mysql
      - ./mysql/init:/docker-entrypoint-initdb.d  # 初始化SQL脚本
    ports:
      - "3306:3306"
    networks:
      - app-network
    command: --default-authentication-plugin=mysql_native_password --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-uroot", "-prootpass"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: redis-cache
    command: redis-server --requirepass redispass --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    restart: unless-stopped

  # Nginx反向代理（可选）
  nginx:
    image: nginx:alpine
    container_name: nginx-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/certs:/etc/nginx/certs:ro
    depends_on:
      - backend
    networks:
      - app-network
    restart: unless-stopped

volumes:
  mysql_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

**⚠️ 小白易懵点**

> **depends_on vs condition: service_healthy**
> - `depends_on`：只保证启动顺序，不保证服务真的可用
> - `condition: service_healthy`：等待依赖服务健康检查通过后再启动
> 
> 对于数据库等需要初始化时间的服务，建议使用健康检查。

**💡 一句话总结**

> Docker Compose让多容器管理变得简单，一个yml文件就能定义、启动、停止整套应用。

---

## 1.6 镜像分层与优化

### 一句话人话
**镜像分层**让构建更快、存储更省，就像搭积木，每块积木可以重复使用。

### 生活比喻 🔥

镜像分层就像**写小说**：

| 层级 | 小说类比 | Docker类比 |
|------|----------|------------|
| 第1层 | 世界观设定 | 操作系统（Ubuntu） |
| 第2层 | 人物设定 | 基础工具（curl、vim） |
| 第3层 | 情节设定 | 应用依赖（Python、Java） |
| 第4层 | 具体章节 | 你的代码 |
| 第5层 | 出版信息 | 启动命令 |

每本新小说可以复用前面的设定，就像Docker复用基础镜像层。

### 镜像分层原理

**Dockerfile的每一行指令都会创建新层：**
```
FROM ubuntu:22.04          # 层1: 基础系统（约77MB）
RUN apt-get update         # 层2: 更新索引（约0MB）
RUN apt-get install nginx  # 层3: 安装nginx（约50MB）
COPY app.py               # 层4: 复制代码（约1KB）
CMD ["python", "app.py"]  # 层5: 启动命令（约0MB）
```

**层的复用机制：**
```
镜像A: [层1][层2][层3][层4a]
镜像B: [层1][层2][层3][层4b]  # 前3层完全相同，只需存储一份
```

### 查看镜像分层

```bash
# 查看镜像的分层信息
docker history nginx:alpine

# 输出示例
IMAGE          CREATED        CREATED BY                                      SIZE      COMMENT
8dfd6c49f2c5   24 hours ago   CMD ["nginx" "-g" "daemon off;"]                 0B        buildkit.applyPackage
<missing>      24 hours ago   EXPOSE 80                                       0B        buildkit.export
<missing>      24 hours ago   COPY /docker-entrypoint.d ./docker-entryp…     4.61kB    buildkit.export
<missing>      24 hours ago   CMD ["/bin/sh" "-c" "#(nop)" "ENTRYPOINT[…     0B        buildkit.export
<missing>      2 weeks ago    /bin/sh -c #(nop)  CMD ["sh"]                  0B        
<missing>      2 weeks ago    /bin/sh -c #(nop) ADD file:xxx in /            7.89MB    
```

### 多阶段构建（重要优化）

**问题：** 构建Node.js应用时，需要完整的node_modules（包含编译工具），但运行时不需要。

**解决方案：** 多阶段构建，使用两个FROM。

```dockerfile
# ============================================
# 单阶段构建的问题（不推荐）
# ============================================
# 最终镜像包含：编译工具、源码、node_modules...
# 体积可能达到1GB以上

FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
CMD ["node", "dist/main.js"]

# 结果：镜像体积 = 基础系统 + node_modules(含devDeps) + 源码 + 构建产物
# 问题：包含很多运行时不需要的东西


# ============================================
# 多阶段构建（推荐）
# ============================================

# 阶段1：构建阶段
FROM node:18 AS builder
WORKDIR /app

# 复制依赖文件（利用Docker缓存）
COPY package*.json ./

# 安装所有依赖（包括devDependencies）
RUN npm ci

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 阶段2：运行阶段
FROM node:18-alpine AS runtime

# 创建非root用户
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

WORKDIR /app

# 只复制运行时需要的文件（构建产物和运行时依赖）
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

# 切换用户
USER nodejs

# 启动
CMD ["node", "dist/main.js"]

# 结果：只包含运行时需要的东西，体积可能只有200MB左右
```

### Java多阶段构建示例

```dockerfile
# ============================================
# Java 多阶段构建示例
# ============================================

# 阶段1：构建
FROM maven:3.9-eclipse-temurin-17 AS builder

WORKDIR /app

# 利用Maven缓存（先复制pom.xml）
COPY pom.xml .
# 下载依赖（如果pom.xml没变，这层会被缓存）
RUN mvn dependency:go-offline

# 复制源码并构建
COPY src ./src
RUN mvn clean package -DskipTests

# 阶段2：运行
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

# 只复制JAR包
COPY --from=builder /app/target/myapp.jar app.jar

# 启动
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### 镜像优化技巧

**1. 选择更小的基础镜像：**

| 镜像 | 大小 | 适用场景 |
|------|------|----------|
| `ubuntu:22.04` | ~77MB | 需要完整系统 |
| `debian:slim` | ~80MB | 通用场景 |
| `alpine` | ~3MB | 追求最小体积 |
| `scratch` | 0MB | Go/C静态编译程序 |
| `distroless` | ~20MB | 只运行二进制 |

**2. 优化顺序（利用缓存）：**

```dockerfile
# 好：先复制不常变化的依赖，再复制代码
COPY package*.json ./
RUN npm ci
COPY src/ ./src/

# 差：任何代码变化都会导致依赖重新安装
COPY . .
RUN npm ci
```

**3. 合并RUN指令：**

```dockerfile
# 差：多层，每层都占用空间
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git
RUN apt-get install -y vim
RUN rm -rf /var/lib/apt/lists/*

# 好：合并为一层
RUN apt-get update && \
    apt-get install -y curl git vim && \
    rm -rf /var/lib/apt/lists/*
```

**4. 清理缓存和临时文件：**

```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends my-package && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip install --no-cache-dir my-package
```

**5. 使用.dockerignore：**

```bash
# .dockerignore 文件
# 排除不需要的文件，减少构建上下文

# 版本控制
.git
.gitignore
*.md

# 开发文件
node_modules/
__pycache__/
*.pyc
*.pyo
.vscode/
.idea/

# 测试文件
test/
tests/
coverage/
*.test.js

# 构建产物
dist/
build/
target/

# 日志
*.log
logs/

# 环境文件
.env
.env.local
.env.*.local

# 本地文件
*.local
docker-compose*.yml
Dockerfile*
```

### 优化前后对比

```bash
# 查看镜像大小
docker images

# 优化前
# REPOSITORY   TAG       SIZE
# myapp        v1        1.23GB    (单阶段+未优化)

# 优化后
# myapp        v2        156MB     (多阶段+Alpine+清理)

# 节省约87%的空间！
```

**⚠️ 小白易懵点**

> **.dockerignore 很重要！**
> 
> 如果不写.dockerignore，`COPY . .` 会把所有文件都发送给Docker守护进程，包括：
> - `.git` 目录（可能很大）
> - `node_modules`（巨大！）
> - 本地测试文件
> 
> 这会导致构建变慢，甚至构建失败。

**💡 一句话总结**

> 镜像优化核心：多阶段构建 + 小基础镜像 + 合理分层 + .dockerignore + 清理缓存。

---

## 1.7 本章实战：完整项目Docker化

### 项目结构

```
my-springboot-app/
├── src/
│   └── main/
│       ├── java/
│       │   └── com/example/demo/
│       │       └── DemoApplication.java
│       └── resources/
│           └── application.yml
├── pom.xml
├── Dockerfile
├── docker-compose.yml
└── .dockerignore
```

### 完整Dockerfile

```dockerfile
# ============================================
# Spring Boot 应用完整 Dockerfile
# 作者：小白教程
# ============================================

# 第一阶段：Maven构建
FROM maven:3.9-eclipse-temurin-17 AS builder

WORKDIR /app

# 复制pom.xml（利用缓存）
COPY pom.xml ./

# 下载依赖（不在同一层，避免每次改动代码都重新下载）
RUN mvn dependency:go-offline -B

# 复制源代码
COPY src ./src

# 构建应用（跳过测试加快构建速度）
RUN mvn clean package -DskipTests

# ============================================
# 第二阶段：运行阶段
# ============================================
FROM eclipse-temurin:17-jre-alpine

# 添加标签
LABEL maintainer="xiaobai@example.com"
LABEL version="1.0.0"
LABEL description="Spring Boot Demo Application"

# 创建非root用户（安全最佳实践）
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup -H -s /bin/sh

WORKDIR /app

# 从构建阶段复制JAR包
COPY --from=builder /app/target/demo-0.0.1-SNAPSHOT.jar app.jar

# 修改文件所有者
RUN chown -R appuser:appgroup /app

# 切换用户
USER appuser

# JVM内存优化（根据容器资源调整）
ENV JAVA_OPTS="-Xms256m -Xmx512m -XX:+UseG1GC -XX:+HeapDumpOnOutOfMemoryError"

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

# 启动命令
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

### 完整docker-compose.yml

```yaml
version: '3.8'

services:
  # Spring Boot 应用
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: springboot-app
    ports:
      - "8080:8080"
    environment:
      # Spring Boot 配置
      SPRING_PROFILES_ACTIVE: docker
      # 数据库配置（引用下面的mysql服务）
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/demo?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC
      SPRING_DATASOURCE_USERNAME: demo
      SPRING_DATASOURCE_PASSWORD: demo123
      # Redis配置（引用下面的redis服务）
      SPRING_REDIS_HOST: redis
      SPRING_REDIS_PORT: 6379
      SPRING_REDIS_PASSWORD: redis123
      # 日志配置
      LOGGING_LEVEL_ROOT: INFO
      LOGGING_LEVEL_COM_EXAMPLE: DEBUG
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - app-network
    restart: unless-stopped
    # 健康检查已在Dockerfile中定义
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # MySQL 数据库
  mysql:
    image: mysql:8.0
    container_name: mysql-db
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: demo
      MYSQL_USER: demo
      MYSQL_PASSWORD: demo123
      TZ: Asia/Shanghai
    volumes:
      # 持久化数据
      - mysql_data:/var/lib/mysql
      # 初始化脚本
      - ./mysql/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
      # 配置文件
      - ./mysql/conf.d:/etc/mysql/conf.d:ro
    ports:
      - "3306:3306"
    networks:
      - app-network
    # MySQL 8.0 配置
    command: >
      --default-authentication-plugin=mysql_native_password
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_unicode_ci
      --max_connections=500
      --innodb_buffer_pool_size=256M
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-uroot", "-proot123"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: redis-cache
    command: >
      redis-server
      --requirepass redis123
      --appendonly yes
      --maxmemory 256mb
      --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "redis123", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    restart: unless-stopped

# 数据卷
volumes:
  mysql_data:
    driver: local
  redis_data:
    driver: local

# 网络
networks:
  app-network:
    driver: bridge
```

### 初始化SQL脚本

```sql
-- mysql/init.sql

-- 创建表
CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入测试数据
INSERT INTO users (username, password, email) VALUES
    ('admin', '$2a$10$...', 'admin@example.com'),
    ('test', '$2a$10$...', 'test@example.com');

-- 创建配置表
CREATE TABLE IF NOT EXISTS configs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### MySQL配置文件

```ini
# mysql/conf.d/custom.cnf

[mysqld]
# 字符集
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# 时区
default-time-zone = '+08:00'

# 连接数
max_connections = 500

# 缓冲区大小（根据可用内存调整）
innodb_buffer_pool_size = 256M

# 日志
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2

[client]
default-character-set = utf8mb4
```

### 使用步骤

```bash
# 1. 进入项目目录
cd my-springboot-app

# 2. 创建必要的目录
mkdir -p mysql/init mysql/conf.d

# 3. 构建并启动所有服务
docker compose up -d --build

# 4. 查看服务状态
docker compose ps

# 5. 查看日志
docker compose logs -f app

# 6. 查看所有日志
docker compose logs -f

# 7. 测试API
curl http://localhost:8080/actuator/health

# 8. 进入容器调试
docker compose exec app sh
docker compose exec mysql mysql -udemo -pdemo123 demo

# 9. 清理环境
docker compose down -v
```

---

## 第一篇总结

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### 关键知识点回顾

| 概念 | 一句话解释 |
|------|------------|
| 容器 | 轻量级、独立的软件包 |
| 镜像 | 容器的只读模板 |
| Dockerfile | 构建镜像的指令文件 |
| Docker Compose | 多容器编排工具 |
| 多阶段构建 | 用多个FROM分离构建和运行环境 |

### 命令速查表

```bash
# 镜像操作
docker pull <image>          # 拉取镜像
docker images                 # 列出镜像
docker rmi <image>           # 删除镜像
docker build -t <name> .     # 构建镜像

# 容器操作
docker run -d -p 8080:80 <image>   # 运行容器
docker ps                          # 查看运行中的容器
docker ps -a                        # 查看所有容器
docker logs <container>             # 查看日志
docker exec -it <container> /bin/sh # 进入容器
docker stop/start/restart <container> # 停止/启动/重启容器
docker rm <container>               # 删除容器

# Compose操作
docker compose up -d         # 启动服务
docker compose down          # 停止服务
docker compose logs -f       # 查看日志
docker compose ps            # 查看状态
docker compose exec <service> sh  # 进入容器
```

### 下一章预告

在下一章《K8s架构》中，我们将学习：
- 为什么需要容器编排
- Kubernetes的整体架构
- Master节点和控制平面的组件
- Node节点和工作负载
- kubectl命令行的安装和使用

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

**💡 一句话总结**

> Docker是K8s的基础！掌握好容器、镜像、Dockerfile和Docker Compose，K8s学习就成功了一半。

---

*感谢学习第一篇！有问题欢迎随时提问。*

# 第二篇：K8s架构

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

## 前言：从单兵作战到军团作战

想象一下这个场景：

**没有K8s的时候：**
你开了一家小饭馆，就你一个厨师。客人点菜，你做；客人多了，你一个人忙不过来，菜做糊了、服务差了、客人骂骂咧咧走了。

**有了K8s的时候：**
你开了一个连锁餐饮集团：
- **总部（Master）**：负责制定菜单、分配任务、监控质量
- **分店（Node）**：按照总部指令做饭、提供服务
- **服务员（Pod）**：具体执行上菜等任务
- **客户（用户）**：发出请求、享用服务

当客流增加时，总部自动调配更多人手到繁忙的分店；当某个分店出问题，总部迅速调走客人到其他分店。

**这就是Kubernetes——容器编排的"司令部"。**

---

## 2.1 为什么要容器编排？

### 一句话人话
**容器编排**就是自动管理多个容器的"大管家"，让容器集群像一台超级计算机一样工作。

### 生活比喻 🔥

**一个厨师 vs 连锁餐厅：**

| 场景 | 一个厨师 | 连锁餐厅（K8s） |
|------|----------|----------------|
| 多道菜 | 手忙脚乱 | 同时出餐，互不干扰 |
| 客人多了 | 做不过来 | 总部调人支援 |
| 厨师请假 | 餐馆关门 | 其他厨师顶上 |
| 菜品质量 | 看心情 | 标准化流程 |
| 食材管理 | 随便放 | 统一采购配送 |

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

**⚠️ 小白易懵点**

> **容器编排 ≠ 单一容器管理**
> - Docker管理的是**单个容器**
> - K8s管理的是**容器集群**（成百上千个容器）
> 
> 就像一个人可以管理自己的小房间，但要管理酒店大厦就需要物业管理系统。

### 容器编排要解决的问题

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        容器编排的核心问题                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. 【调度】哪个容器放到哪台机器？                                        │
│     → 根据资源情况自动分配（类似派单系统）                                 │
│                                                                         │
│  2. 【扩缩容】负载高了怎么加机器？低了怎么减？                             │
│     → 根据负载自动扩缩容（类似弹性计算）                                   │
│                                                                         │
│  3. 【自愈】某个容器挂了怎么办？                                          │
│     → 自动重启或重建（类似自动复活）                                      │
│                                                                         │
│  4. 【服务发现】多个容器怎么互相找到对方？                                  │
│     → 统一的服务注册与发现（类似电话总机）                                 │
│                                                                         │
│  5. 【负载均衡】请求来了发给谁？                                          │
│     → 均匀分配流量（类似排队叫号）                                       │
│                                                                         │
│  6. 【滚动更新】怎么平滑升级版本？                                         │
│     → 逐步替换容器（类似接力赛）                                          │
│                                                                         │
│  7. 【配置管理】配置变了怎么更新？                                         │
│     → 配置中心统一管理（类似中央控制室）                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 常见的容器编排工具

| 工具 | 开发公司 | 特点 | 市场占有率 |
|------|----------|------|------------|
| **Kubernetes** | Google/CNCF | 功能最全、生态最好 | ~78% |
| Docker Swarm | Docker公司 | 简单易用、适合小规模 | ~15% |
| Mesos | Apache | 通用、适合大数据 | ~5% |
| Nomad | HashiCorp | 轻量、简单 | ~2% |

**K8s = Kubernetes，因为K和s之间有8个字母，所以简称K8s**

---

## 2.2 K8s整体架构

### 一句话人话
**K8s采用Master-Node架构**，Master是"大脑"，Node是"四肢"，它们协同工作来管理容器集群。

### 架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Kubernetes 集群                                 │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         控制平面 (Control Plane)                      │    │
│  │                         也叫 Master 节点                              │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │    │
│  │  │   API       │ │    etcd     │ │ Scheduler   │ │ Controller  │   │    │
│  │  │   Server    │ │   (数据库)  │ │  (调度器)   │ │   Manager   │   │    │
│  │  │  (入口)     │ │             │ │             │ │ (控制器)    │   │    │
│  │  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘   │    │
│  │         │              │              │              │           │    │
│  └─────────┼──────────────┼──────────────┼──────────────┼───────────┘    │
│            │              │              │              │                 │
│            └──────────────┴──────────────┴──────────────┘                 │
│                                    │                                        │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │ kubectl 命令
                                     │
┌────────────────────────────────────┼────────────────────────────────────────┐
│                                    │                                        │
│  ┌─────────────────────────────────┴─────────────────────────────────────┐  │
│  │                          Node 节点 (工作节点)                          │  │
│  │                                                                      │  │
│  │   ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐ │  │
│  │   │     Node 1       │    │     Node 2       │    │     Node 3       │ │  │
│  │   │  ┌────────────┐  │    │  ┌────────────┐  │    │  ┌────────────┐  │ │  │
│  │   │  │   kubelet  │  │    │  │   kubelet  │  │    │  │   kubelet  │  │ │  │
│  │   │  │            │  │    │  │            │  │    │  │            │  │ │  │
│  │   │  │ kube-proxy │  │    │  │ kube-proxy │  │    │  │ kube-proxy │  │ │  │
│  │   │  │            │  │    │  │            │  │    │  │            │  │ │  │
│  │   │  │    CRI     │  │    │  │    CRI     │  │    │  │    CRI     │  │ │  │
│  │   │  │ (容器运行时)│  │    │  │ (容器运行时)│  │    │  │ (容器运行时)│  │ │  │
│  │   │  └─────┬──────┘  │    │  └─────┬──────┘  │    │  └─────┬──────┘  │ │  │
│  │   │        │         │    │        │         │    │        │         │ │  │
│  │   │  ┌─────┴──────┐  │    │  ┌─────┴──────┐  │    │  ┌─────┴──────┐  │ │  │
│  │   │  │  Pod   Pod │  │    │  │  Pod   Pod │  │    │  │  Pod   Pod │  │ │  │
│  │   │  │  +nginx +app│ │    │  │  +app  +db │  │    │  │  +app  +redis│ │  │
│  │   │  └────────────┘  │    │  └────────────┘  │    │  └────────────┘  │ │  │
│  │   └──────────────────┘    └──────────────────┘    └──────────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 通俗解释

**控制平面（Master） = 集团总部**
- 制定战略（API Server：接收指令）
- 存储档案（etcd：保存所有数据）
- 分配任务（Scheduler：决定谁做什么）
- 监督执行（Controller Manager：确保任务完成）

**Node节点 = 分店**
- 听从总部指挥（kubelet：执行任务）
- 维持秩序（kube-proxy：网络代理）
- 具体做菜（容器运行时：运行容器）

**⚠️ 小白易懵点**

> **Master vs Node 的区别**
> - **Master** 负责任务调度和管理决策（大脑）
> - **Node** 负责任务执行和工作负载运行（四肢）
> 
> 一个小集群可以只有1个Master，但生产环境建议3个Master做高可用。

---

## 2.3 控制平面组件（Master）

### 2.3.1 API Server - 集群入口

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

### 一句话人话
**API Server是K8s集群的"前台接待"**，所有操作都要经过它。

### 生活比喻 🔥

API Server就像**酒店前台**：
- 客人（用户）进来 → 前台登记
- 要房间（Pod）→ 前台分配
- 要叫餐（服务调用）→ 前台转接
- 要退房（删除资源）→ 前台办理

无论你要做什么操作，都必须经过前台。

### 技术细节

```yaml
# API Server 的核心职责
apiServer:
  # 1. 提供RESTful API接口
  endpoints:
    - /api/v1/namespaces/default/pods
    - /api/v1/namespaces/kube-system/services
    - /apis/apps/v1/deployments
  
  # 2. 认证授权
  authentication:
    - 验证用户身份（谁？）
    - 检查权限（能做什么？）
  
  # 3. 数据验证
  validation:
    - 确保请求数据格式正确
    - 拒绝非法操作
  
  # 4. 读写etcd
  storage:
    - 所有数据最终存储到etcd
```

### 访问API Server的方式

```bash
# 1. kubectl命令行（最常用）
kubectl get pods
kubectl create deployment nginx --image=nginx

# 2. REST API（程序调用）
curl -k https://kubernetes.default.svc/api/v1/namespaces/default/pods \
  -H "Authorization: Bearer $TOKEN"

# 3. Kubernetes Dashboard（Web界面）
# 需要安装dashboard插件
```

### 2.3.2 etcd - 数据存储

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

### 一句话人话
**etcd是K8s的"数据库+保险柜"**，所有集群状态都存储在这里。

### 生活比喻 🔥

etcd就像**酒店的中央档案室**：
- 所有房间的入住信息（Pod状态）
- 所有服务台的电话（Service配置）
- 所有钥匙的记录（ConfigMap）
- 所有贵重物品的保管（Secret）

**没有档案室，酒店就乱套了。**

### 技术细节

```bash
# etcd 的特点
etcd:
  # 1. 分布式键值存储
  type: "key-value database"
  
  # 2. 强一致性（Raft算法）
  consistency: "strong consistency"
  
  # 3. 高可用
  replication: true  # 数据复制到多个节点
  
  # 4. 存储内容
  stores:
    - 集群节点信息
    - Pod信息
    - Service信息
    - 配置信息
    - 认证信息
    - 调度决策
```

### 访问etcd（了解即可）

```bash
# etcdctl 是 etcd 的命令行客户端（一般不会直接使用）
# 备份数据
ETCDCTL_API=3 etcdctl snapshot save backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# 查看数据
ETCDCTL_API=3 etcdctl get / --prefix \
  --endpoints=https://127.0.0.1:2379
```

**⚠️ 小白易懵点**

> **etcd 不是用来存数据的！**
> 
> 很多小白以为 etcd 是用来存储应用数据的（如用户信息、订单数据）。实际上：
> - etcd **只存储K8s集群的元数据**（配置、状态、调度信息）
> - 应用数据应该存在数据库（MySQL/PostgreSQL）或存储服务（NFS/云存储）中

### 2.3.3 Scheduler - 任务调度

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

### 一句话人话
**Scheduler是K8s的"人事部"**，决定每个Pod应该放到哪个Node上。

### 生活比喻 🔥

Scheduler就像**派单系统**：
- 有一批新订单（新建Pod）
- 系统查看各分店的忙碌程度（Node资源）
- 系统查看订单的特殊需求（Pod的资源请求）
- 分配到最合适的分店（调度决策）

### 调度流程

```
创建新Pod
    │
    ▼
Pod处于 Pending 状态
    │
    ▼
Scheduler 监听到新Pod
    │
    ▼
┌─────────────────────────────────────┐
│           调度决策过程                │
├─────────────────────────────────────┤
│                                     │
│  1. 预选（Filtering）               │
│     ├─ 资源不足的Node → 排除         │
│     ├─ 标签不匹配的Node → 排除        │
│     └─ 存在污点的Node → 排除          │
│                                     │
│  2. 优选（Scoring）                  │
│     ├─ 计算每个Node的得分            │
│     │  ├─ 资源使用率越低得分越高      │
│     │  ├─ 亲和性规则匹配度           │
│     │  └─ 负载分布均衡度             │
│     │                                  │
│     └─ 选择得分最高的Node            │
│                                     │
│  3. 选定（Selection）                │
│     └─ 绑定Pod到选中的Node           │
│                                     │
└─────────────────────────────────────┘
    │
    ▼
Pod绑定到目标Node
    │
    ▼
Node上的kubelet创建Pod
```

### 影响调度的因素

| 因素 | 说明 |
|------|------|
| **资源请求** | Pod需要多少CPU/内存 |
| **资源限制** | Pod最多能用多少 |
| **节点选择器** | 必须/不能部署在哪些节点 |
| **亲和性/反亲和性** | 与其他Pod的关系 |
| **污点和容忍** | 节点是否愿意接收Pod |
| **优先级** | 高优先级Pod优先调度 |

```yaml
# 示例：带有调度策略的Pod
apiVersion: v1
kind: Pod
metadata:
  name: my-app-pod
spec:
  # 资源请求和限制
  containers:
  - name: my-app
    image: my-app:1.0
    resources:
      requests:           # 需要的资源
        memory: "256Mi"
        cpu: "500m"
      limits:             # 限制的资源
        memory: "512Mi"
        cpu: "1000m"
  
  # 节点选择器（必须部署在有SSD磁盘的节点）
  nodeSelector:
    disk-type: ssd
  
  # 亲和性（希望与redis Pod在同一节点）
  affinity:
    podAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app: redis
          topologyKey: kubernetes.io/hostname
  
  # 容忍（可以容忍有NoSchedule污点的节点）
  tolerations:
  - key: "node-role"
    operator: "Equal"
    value: "gpu"
    effect: "NoSchedule"
```

### 2.3.4 Controller Manager - 控制器管理

### 一句话人话
**Controller Manager是K8s的"监工"**，确保实际状态与期望状态一致。

### 生活比喻 🔥

Controller Manager就像**物业管理系统**：
- 电梯坏了 → 自动派维修工（自愈）
- 灯不亮了 → 自动换灯泡（自愈）
- 垃圾满了 → 自动清理（垃圾收集）
- 人少了 → 招人（扩容）

### 内置控制器

| 控制器 | 作用 |
|--------|------|
| **Deployment Controller** | 管理Deployment，确保Pod数量符合预期 |
| **ReplicaSet Controller** | 管理ReplicaSet，确保Pod副本数 |
| **StatefulSet Controller** | 管理StatefulSet，确保有状态应用 |
| **DaemonSet Controller** | 管理DaemonSet，确保每节点一个Pod |
| **Job Controller** | 管理Job任务，确保一次性任务完成 |
| **CronJob Controller** | 管理定时任务 |
| **Service Controller** | 管理Service，配置负载均衡 |
| **Node Controller** | 管理节点，监控节点状态 |
| **Endpoint Controller** | 管理Endpoints，追踪Pod变化 |
| **Namespace Controller** | 管理Namespace |

### 控制循环原理

```
┌─────────────────────────────────────────────────────────┐
│                    控制循环 (Control Loop)                │
│                                                         │
│   ┌───────────┐      ┌───────────┐      ┌───────────┐ │
│   │  期望状态   │ ──▶ │  观察现状   │ ──▶ │  采取行动   │ │
│   │ (Spec)     │      │ (Status)   │      │ (Action)   │ │
│   └───────────┘      └─────┬─────┘      └───────────┘ │
│                            │                            │
│                      持续监控                            │
│                            ▼                            │
│                    ┌───────────────┐                    │
│                    │   发现差异    │                    │
│                    │ (Reconcile)   │                    │
│                    └───────────────┘                    │
│                                                         │
└─────────────────────────────────────────────────────────┘

# 示例：Deployment控制器
期望状态：3个Pod副本
当前状态：只有2个Pod在运行
采取行动：创建1个新Pod
```

**💡 一句话总结**

> Master节点的四大组件：
> - **API Server**：入口（接待）
> - **etcd**：存储（档案室）
> - **Scheduler**：调度（人事部）
> - **Controller Manager**：控制（监工）

---

## 2.4 工作节点组件（Node）

### 2.4.1 kubelet - 节点代理

### 一句话人话
**kubelet是Node上的"现场经理"**，负责在节点上创建和管理容器。

### 生活比喻 🔥

kubelet就像**分店店长**：
- 接收总部指令（从API Server获取任务）
- 分配工作任务（创建Pod/容器）
- 监督工作质量（健康检查）
- 汇报工作进度（状态上报）
- 处理紧急情况（自动重启）

### kubelet的核心职责

```
┌─────────────────────────────────────────────────────────┐
│                      kubelet                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Pod管理                                            │
│     ├─ 从API Server获取Pod规格                          │
│     ├─ 创建/启动/停止Pod内的容器                        │
│     └─ 挂载存储卷                                       │
│                                                         │
│  2. 健康检查                                            │
│     ├─ LivenessProbe（存活探针）→ 容器是否活着？         │
│     ├─ ReadinessProbe（就绪探针）→ 容器是否就绪？       │
│     └─ StartupProbe（启动探针）→ 容器是否启动完成？     │
│                                                         │
│  3. 资源报告                                            │
│     ├─ 节点CPU/内存使用情况                             │
│     ├─ Pod资源使用情况                                  │
│     └─ 定期上报给Master                                  │
│                                                         │
│  4. 容器运行时接口                                       │
│     └─ 与CRI通信，管理容器                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.4.2 kube-proxy - 网络代理

### 一句话人话
**kube-proxy是Node上的"网络交警"**，负责Pod的网络通信和负载均衡。

### 生活比喻 🔥

kube-proxy就像**大楼的门禁系统**：
- 记录每个住户的信息（Service到Pod的映射）
- 转发访客到正确的人（流量路由）
- 负载均衡多个住户的访客（均衡分发）

### kube-proxy的工作模式

| 模式 | 说明 | 性能 |
|------|------|------|
| **userspace** | 用户态代理，性能差 | 最低 |
| **iptables** | 使用iptables规则转发（默认） | 中等 |
| **ipvs** | 使用IPVS内核模块转发 | 最高 |

```bash
# 查看kube-proxy的工作模式
kubectl get configmap kube-proxy -n kube-system -o yaml

# ipvs模式的特点
ipvs:
  # 基于哈希表的负载均衡
  # 支持多种均衡算法：rr, wrr, lc, wlc, ip hash...
  # 性能比iptables高50%以上
```

### kube-proxy网络规则

```
Service: my-app (10.96.0.100:80)
    │
    ├──▶ Pod: my-app-1 (10.244.1.10:8080)
    ├──▶ Pod: my-app-2 (10.244.1.11:8080)
    └──▶ Pod: my-app-3 (10.244.1.12:8080)

# kube-proxy生成的iptables规则示例
-A KUBE-SERVICES -d 10.96.0.100/32 -p tcp --dport 80 -j KUBE-SVC-XXXX
-A KUBE-SVC-XXXX -m statistic --mode random --probability 0.33 -j KUBE-SEP-YYYY1
-A KUBE-SVC-XXXX -m statistic --mode random --probability 0.50 -j KUBE-SEP-YYYY2
-A KUBE-SVC-XXXX -j KUBE-SEP-YYYY3
```

### 2.4.3 CRI - 容器运行时接口

### 一句话人话
**CRI是K8s和容器运行时之间的"翻译官"**，让K8s可以支持不同的容器技术。

### 生活比喻 🔥

CRI就像**手机充电口**：
- 无论你用苹果还是安卓，充电头只要符合接口标准就能充电
- 无论你用Docker还是Containerd，只要符合CRI标准，K8s就能管理它们

### CRI架构

```
┌─────────────────────────────────────────────────────────┐
│                    kubelet                              │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              CRI (Container Runtime Interface) │   │
│  │                                                  │   │
│  │   ┌─────────────┐    ┌─────────────────────┐   │   │
│  │   │ Docker      │    │ Containerd          │   │   │
│  │   │ (via shim)  │    │ (原生CRI支持)        │   │   │
│  │   │             │    │                     │   │   │
│  │   │  Docker     │    │  containerd          │   │   │
│  │   │ -shim      │    │   └─ ctr            │   │   │
│  │   └─────────────┘    └─────────────────────┘   │   │
│  │                                                  │   │
│  │   ┌─────────────┐    ┌─────────────────────┐   │   │
│  │   │ cri-dockerd │    │ cri-o (OCI)         │   │   │
│  │   │ (Dockershim)│    │                     │   │   │
│  │   └─────────────┘    └─────────────────────┘   │   │
│  │                                                  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 常见的容器运行时

| 运行时 | 说明 | 备注 |
|--------|------|------|
| **containerd** | Docker的容器引擎，独立使用 | K8s推荐 |
| **cri-o** | 纯CRI实现，只支持OCI镜像 | 轻量 |
| **Docker** | 早期K8s使用，需要shim桥接 | 逐渐被containerd取代 |
| **Podman** | 无守护进程容器引擎 | 兼容CRI |

### 2.4.4 Pod与容器的关系

### 一句话人话
**Pod是K8s调度的最小单位**，一个Pod里可以运行一个或多个容器。

### 生活比喻 🔥

**Pod = 胶囊旅馆的房间**

```
┌─────────────────────────────────────────────────────────┐
│                     Pod                                  │
│  ┌─────────────────────────────────────────────────┐    │
│  │              胶囊旅馆房间                         │    │
│  │                                                  │    │
│  │   ┌─────────────┐     ┌─────────────┐          │    │
│  │   │   容器1      │     │   容器2      │          │    │
│  │   │   (主应用)   │     │   (辅助)    │          │    │
│  │   │              │     │              │          │    │
│  │   │  nginx       │     │  日志收集    │          │    │
│  │   │  :80         │     │  (sidecar)   │          │    │
│  │   └─────────────┘     └─────────────┘          │    │
│  │                                                  │    │
│  │   ┌─────────────┐                              │    │
│  │   │ Init容器     │   (先启动，执行完就退出)       │    │
│  │   └─────────────┘                              │    │
│  │                                                  │    │
│  │   ┌─────────────────────────────────────────┐   │    │
│  │   │           共享存储 (Volume)              │   │    │
│  │   │   /shared-data (两个容器共享)            │   │    │
│  │   └─────────────────────────────────────────┘   │    │
│  │                                                  │    │
│  │   ┌─────────────────────────────────────────┐   │    │
│  │   │           共享网络命名空间               │   │    │
│  │   │   localhost (两个容器可以互相访问)       │   │    │
│  │   └─────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Pod的网络特点

```bash
# 同一个Pod内的容器共享：
# 1. 网络命名空间（可以localhost互相访问）
# 2. IPC命名空间（可以用信号量通信）
# 3. 存储卷（共享文件）

# 示例：nginx + 日志收集器在一个Pod
# nginx容器监听 :80
# log-collector容器可以通过 localhost:80 访问nginx
```

**⚠️ 小白易懵点**

> **容器 vs Pod 的区别**
> - **容器（Container）**：一个独立的运行实例
> - **Pod**：一个或多个容器的"壳"，共享网络和存储
> 
> 一般情况下，1个Pod运行1个容器。但有些场景需要"主容器+辅助容器"模式（如日志收集、代理等），这时1个Pod运行多个容器。

---

## 2.5 kubectl安装与配置

### 一句话人话
**kubectl是操作K8s集群的命令行工具**，就像docker命令操作Docker一样。

### 安装kubectl

**macOS安装：**
```bash
# 方法1：使用brew安装
brew install kubectl

# 方法2：下载二进制
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"

# 方法3：安装kubectl插件管理器
brew install krew
```

**Linux安装：**
```bash
# 下载最新版本
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# 添加执行权限
chmod +x kubectl

# 移动到PATH
sudo mv kubectl /usr/local/bin/

# 或者放到用户目录
mkdir -p ~/.local/bin
mv kubectl ~/.local/bin/
export PATH="$HOME/.local/bin:$PATH"
```

**Windows安装：**
```powershell
# 使用 Chocolatey
choco install kubernetes-cli

# 或手动下载kubectl.exe并添加到PATH
```

**验证安装：**
```bash
kubectl version --client
# 输出：Client Version: version.Info{Major:"1", Minor:"28", GitVersion:"v1.28.0", ...}
```

### 配置kubectl

kubectl需要配置文件来连接K8s集群，默认位置：`~/.kube/config`

```bash
# 查看当前kubectl配置
kubectl config view

# 查看当前上下文
kubectl config current-context

# 查看所有上下文
kubectl config get-contexts
```

**配置文件结构：**
```yaml
# ~/.kube/config
apiVersion: v1
kind: Config

clusters:                      # 集群配置
- name: my-cluster
  cluster:
    server: https://192.168.1.100:6443
    certificate-authority-data: <base64编码的CA证书>

contexts:                      # 上下文配置（用户+集群+命名空间）
- name: my-context
  context:
    cluster: my-cluster
    user: admin-user
    namespace: default

current-context: my-context    # 当前使用的上下文

users:                         # 用户配置
- name: admin-user
  user:
    token: <base64编码的token>
    # 或使用证书认证
    client-certificate-data: <base64编码的客户端证书>
    client-key-data: <base64编码的客户端私钥>
```

### 常用kubectl配置

```bash
# 1. 手动指定kubeconfig文件
kubectl get pods --kubeconfig=/path/to/config

# 2. 设置默认命名空间
kubectl config set-context --current --namespace=my-namespace

# 3. 添加新集群
kubectl config set-cluster my-cluster \
  --server=https://192.168.1.100:6443 \
  --certificate-authority=/path/to/ca.crt

# 4. 添加用户
kubectl config set-credentials admin \
  --token=<your-token>

# 5. 创建上下文
kubectl config set-context my-context \
  --cluster=my-cluster \
  --user=admin \
  --namespace=default

# 6. 切换上下文
kubectl config use-context my-context
```

### kubectl命令自动补全

```bash
# macOS
source <(kubectl completion bash)
echo 'source <(kubectl completion bash)' >> ~/.bash_profile

# Linux
source <(kubectl completion bash)
echo 'source <(kubectl completion bash)' >> ~/.bashrc

# zsh
echo 'source <(kubectl completion zsh)' >> ~/.zshrc
```

### kubectl常用命令速查

```bash
# ============================================
# kubectl 命令速查
# ============================================

# 集群信息
kubectl cluster-info              # 查看集群信息
kubectl version                   # 查看版本
kubectl api-resources             # 查看所有资源类型
kubectl explain <resource>        # 查看资源定义

# 节点操作
kubectl get nodes                 # 列出所有节点
kubectl describe node <name>      # 查看节点详情
kubectl top node <name>           # 查看节点资源使用

# 命名空间
kubectl get namespaces            # 列出命名空间
kubectl create namespace <name>   # 创建命名空间
kubectl delete namespace <name>  # 删除命名空间

# Pod操作
kubectl get pods                   # 列出Pod
kubectl get pods -o wide          # 详细信息
kubectl get pods -w                # 实时监控
kubectl describe pod <name>        # 查看Pod详情
kubectl logs <pod>                 # 查看日志
kubectl logs -f <pod>             # 实时日志
kubectl exec -it <pod> -- /bin/sh # 进入容器
kubectl delete pod <name>         # 删除Pod
kubectl apply -f <file.yaml>      # 应用配置
kubectl replace -f <file.yaml>    # 替换配置

# Deployment操作
kubectl get deployments           # 列出Deployment
kubectl create deployment <name> --image=<image>  # 创建Deployment
kubectl scale deployment <name> --replicas=3     # 扩缩容
kubectl rollout status deployment/<name>         # 查看滚动更新状态
kubectl rollout undo deployment/<name>            # 回滚

# Service操作
kubectl get services              # 列出Service
kubectl expose deployment <name> --port=80 --target-port=8080  # 创建Service
kubectl delete service <name>     # 删除Service

# 标签操作
kubectl label pods <name> env=prod    # 添加标签
kubectl label pods <name> env-        # 删除标签
kubectl get pods -l env=prod          # 按标签筛选

# 格式化输出
kubectl get pods -o yaml             # YAML格式
kubectl get pods -o json             # JSON格式
kubectl get pods -o wide             # 宽表格
kubectl get pods -o name             # 只输出名称

# 其他
kubectl apply -f <file.yaml>         # 应用配置（创建或更新）
kubectl delete -f <file.yaml>        # 删除资源配置
kubectl edit <resource> <name>       # 编辑资源配置
kubectl diff -f <file.yaml>          # 预览更改
kubectl port-forward <pod> 8080:80   # 端口转发
kubectl cp <pod>:/path/to/file ./local-file  # 复制文件
```

### kubectl context使用示例

```bash
# 场景：管理多个集群（开发、测试、生产）

# 1. 配置三个集群
kubectl config set-cluster dev --server=https://dev.k8s.example.com
kubectl config set-cluster test --server=https://test.k8s.example.com
kubectl config set-cluster prod --server=https://prod.k8s.example.com

# 2. 配置用户
kubectl config set-credentials dev-admin --token=<dev-token>
kubectl config set-credentials test-admin --token=<test-token>
kubectl config set-credentials prod-admin --token=<prod-token>

# 3. 创建上下文
kubectl config set-context dev --cluster=dev --user=dev-admin --namespace=default
kubectl config set-context test --cluster=test --user=test-admin --namespace=default
kubectl config set-context prod --cluster=prod --user=prod-admin --namespace=default

# 4. 切换上下文
kubectl config use-context dev      # 切换到开发环境
kubectl config use-context test     # 切换到测试环境
kubectl config use-context prod     # 切换到生产环境

# 5. 查看当前上下文
kubectl config current-context
```

**⚠️ 小白易懵点**

> **kubectl apply vs kubectl create 的区别**
> - `kubectl create`：创建资源，**如果已存在会报错**
> - `kubectl apply`：创建或**更新**资源，幂等操作
> 
> **推荐使用 `kubectl apply`**，因为它可以重复执行。

**💡 一句话总结**

> kubectl是K8s的"遥控器"，学会它就能掌控整个集群。核心命令：`get`（查看）、`describe`（详情）、`logs`（日志）、`exec`（进入）、`apply`（应用）、`delete`（删除）。

---

## 2.6 Minikube - 本地K8s体验

### 一句话人话
**Minikube是在本地电脑运行K8s的最简单方式**，适合学习和测试。

### 安装Minikube

**macOS：**
```bash
# 使用brew安装
brew install minikube

# 或下载二进制
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-amd64
sudo mv minikube-darwin-amd64 /usr/local/bin/minikube
sudo chmod +x /usr/local/bin/minikube
```

**Linux：**
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo mv minikube-linux-amd64 /usr/local/bin/minikube
sudo chmod +x /usr/local/bin/minikube
```

**Windows：**
```powershell
# 使用Chocolatey
choco install minikube

# 或下载.exe安装
```

### 安装Kubernetes Driver

Minikube需要在虚拟机中运行K8s，需要安装驱动：

| 操作系统 | 推荐驱动 | 安装命令 |
|----------|----------|----------|
| macOS | Docker Desktop | 内置 |
| macOS | HyperKit | `brew install hyperkit` |
| Linux | Docker | `minikube config set driver docker` |
| Windows | Docker Desktop | 内置 |
| Windows | Hyper-V | 启用Windows功能 |

### Minikube基本操作

```bash
# 1. 启动集群（第一次会下载镜像）
minikube start

# 指定版本
minikube start --kubernetes-version=v1.28.0

# 指定驱动
minikube start --driver=docker

# 指定资源配置
minikube start --cpus=4 --memory=8192

# 2. 查看状态
minikube status

# 3. 打开Dashboard
minikube dashboard

# 4. SSH进入Minikube节点
minikube ssh

# 5. 停止集群
minikube stop

# 6. 删除集群
minikube delete

# 7. 查看集群IP
minikube ip

# 8. 加载镜像（从Docker拉取的镜像需要在Minikube中重新加载）
minikube image load my-image:tag

# 9. 常用命令别名
alias kubectl="minikube kubectl --"
```

### Minikube体验完整流程

```bash
# 1. 启动Minikube
minikube start

# 2. 等待启动完成（约5分钟）
# 看到 "Done! kubectl is now configured to use 'minikube' cluster"

# 3. 创建第一个Deployment
kubectl create deployment hello-minikube --image=kicbase/echo-server:1.0

# 4. 查看Deployment
kubectl get deployments

# 5. 暴露服务
kubectl expose deployment hello-minikube --type=NodePort --port=8080

# 6. 获取服务URL
minikube service hello-minikube --url

# 7. 访问服务
curl $(minikube service hello-minikube --url)

# 8. 清理
kubectl delete deployment hello-minikube
kubectl delete service hello-minikube
```

### 启用插件

```bash
# 查看可用插件
minikube addons list

# 启用插件
minikube addons enable metrics-server
minikube addons enable dashboard
minikube addons enable ingress

# 禁用插件
minikube addons disable dashboard

# 打开插件的Dashboard（如Ingress）
minikube addons open ingress
```

### Minikube与kubectl的对比

| 特性 | Minikube | kubectl |
|------|----------|---------|
| **作用** | 创建本地K8s集群 | 操作K8s集群 |
| **关系** | 提供集群 | 使用集群 |
| **使用场景** | 学习、开发、测试 | 管理任何K8s集群 |
| **复杂度** | 一次性设置 | 日常使用 |

---

## 2.7 本章实战：部署第一个K8s应用

### 目标
使用kubectl在本地Minikube上部署一个简单的Web应用。

### 步骤1：启动Minikube

```bash
# 启动Minikube
minikube start --cpus=2 --memory=4g --disk-size=20g

# 验证状态
minikube status
# 输出：
# minikube
# type: Control Plane
# host: Running
# kubelet: Running
# apiserver: Running
# kubeconfig: Configured
```

### 步骤2：创建Deployment

```bash
# 方式1：使用kubectl创建
kubectl create deployment nginx-web --image=nginx:alpine --port=80

# 方式2：使用YAML创建
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-web
  labels:
    app: nginx-web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx-web
  template:
    metadata:
      labels:
        app: nginx-web
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
EOF
```

### 步骤3：查看Deployment状态

```bash
# 查看Deployment
kubectl get deployments

# 查看ReplicaSet
kubectl get rs

# 查看Pod
kubectl get pods -o wide

# 查看Pod日志
kubectl logs nginx-web-xxxxx-yyyyy
```

### 步骤4：创建Service

```bash
# 方式1：kubectl expose
kubectl expose deployment nginx-web --type=NodePort --port=80

# 方式2：YAML
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: nginx-web
  labels:
    app: nginx-web
spec:
  type: NodePort
  selector:
    app: nginx-web
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
    name: http
EOF
```

### 步骤5：访问应用

```bash
# 查看Service
kubectl get svc

# 获取访问URL（Minikube特有）
minikube service nginx-web --url

# 浏览器打开
minikube service nginx-web
```

### 步骤6：扩容

```bash
# 扩容到3个副本
kubectl scale deployment nginx-web --replicas=3

# 查看扩容结果
kubectl get pods

# 查看Service会负载均衡到3个Pod
kubectl describe service nginx-web
```

### 步骤7：滚动更新

```bash
# 修改镜像版本
kubectl set image deployment/nginx-web nginx=nginx:1.25

# 查看滚动更新状态
kubectl rollout status deployment/nginx-web

# 查看历史版本
kubectl rollout history deployment/nginx-web

# 回滚到上一版本
kubectl rollout undo deployment/nginx-web
```

### 步骤8：清理

```bash
# 删除资源
kubectl delete deployment nginx-web
kubectl delete service nginx-web

# 或者一条命令删除所有相关资源
kubectl delete all -l app=nginx-web

# 停止Minikube
minikube stop
```

**💡 一句话总结**

> K8s部署流程：创建Deployment → 创建Service → 访问应用 → 扩容/更新 → 清理。

---

## 第二篇总结

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### 关键知识点回顾

| 组件 | 一句话解释 |
|------|------------|
| API Server | K8s集群的入口 |
| etcd | K8s的数据存储 |
| Scheduler | Pod的调度器 |
| Controller Manager | 集群的自动控制器 |
| kubelet | Node节点的代理 |
| kube-proxy | 网络代理和负载均衡 |
| CRI | 容器运行时接口 |

### 架构简图

```
┌─────────────────────────────────────────────────────┐
│                   K8s集群                           │
│                                                     │
│   Master节点（控制平面）                              │
│   ├── API Server（入口）                            │
│   ├── etcd（数据库）                                 │
│   ├── Scheduler（调度器）                           │
│   └── Controller Manager（控制器）                   │
│                                                     │
│   Node节点1 ─ Pod, Pod, Pod                         │
│   Node节点2 ─ Pod, Pod                              │
│   Node节点3 ─ Pod, Pod, Pod, Pod                    │
│                                                     │
│   kubectl ← 用户命令                                 │
└─────────────────────────────────────────────────────┘
```

### 下一章预告

在下一章《核心资源对象》中，我们将学习：
- Pod的生命周期和管理
- Deployment的滚动更新和回滚
- StatefulSet管理有状态应用
- DaemonSet的节点守护
- Job和CronJob的批处理任务

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

**💡 一句话总结**

> K8s的核心是Master-Node架构：Master负责任务调度和控制，Node负责运行容器。kubectl是管理K8s集群的主要工具。

---

*感谢学习第二篇！有问题欢迎随时提问。*

# 第三篇：核心资源对象

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

## 前言：K8s的"积木"

想象一下玩乐高积木：

- 每个积木块都是一个**资源对象**
- 你可以组合不同的积木块来搭建不同的东西
- 积木块之间可以有关系（比如一个积木放在另一个上面）

**K8s就像一个积木盒，提供了各种"积木块"来构建你的应用。**

---

## 3.1 Pod - 最小调度单位

### 一句话人话
**Pod是K8s中最小的调度单位**，就像一个"胶囊房间"，里面住着一个或多个容器。

### 生活比喻 🔥

**Pod = 鸟巢里的鸟蛋**

```
┌─────────────────────────────────────────────────────────┐
│                        Pod                              │
│                                                         │
│   就像一个鸟巢：                                         │
│                                                         │
│   ┌─────────────────────────────────────────┐           │
│   │  🪺 鸟巢 (Pod)                          │           │
│   │                                          │           │
│   │    🥚 鸟蛋1 (容器1 - 主应用)              │           │
│   │    🥚 鸟蛋2 (容器2 - 日志收集)           │           │
│   │    🥚 鸟蛋3 (容器3 - 监控代理)           │           │
│   │                                          │           │
│   │    它们共享同一个巢穴的环境                │           │
│   │    一起孵化、一起成长                      │           │
│   │                                          │           │
│   └─────────────────────────────────────────┘           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**特点：**
- 一个Pod里的容器共享**网络命名空间**（可以用localhost互相访问）
- 一个Pod里的容器共享**存储卷**（可以读写同一份文件）
- 一个Pod里的容器总是调度到**同一个Node**

### Pod的YAML结构

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1              # API版本
kind: Pod                   # 资源类型
metadata:                   # 元数据
  name: my-app-pod          # Pod名称
  namespace: default         # 所属命名空间
  labels:                   # 标签（用于选择）
    app: my-app
    version: v1
  annotations:              # 注解（附加信息）
    description: "This is my application"
spec:                       # 规格（期望状态）
  containers:                # 容器列表
  - name: my-app             # 容器名称
    image: my-app:1.0        # 镜像
    imagePullPolicy: IfNotPresent  # 镜像拉取策略
    ports:                   # 端口列表
    - name: http
      containerPort: 8080   # 容器端口
      protocol: TCP
    env:                    # 环境变量
    - name: APP_ENV
      value: production
    - name: DB_HOST
      valueFrom:             # 从ConfigMap引用
        configMapKeyRef:
          name: my-config
          key: database.host
    resources:              # 资源请求和限制
      requests:             # 需要的资源（调度依据）
        memory: "256Mi"
        cpu: "250m"
      limits:               # 限制的资源（不能超过）
        memory: "512Mi"
        cpu: "500m"
    livenessProbe:           # 存活探针
      httpGet:
        path: /health
        port: 8080
      initialDelaySeconds: 15
      periodSeconds: 10
    readinessProbe:          # 就绪探针
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5
    startupProbe:            # 启动探针（慢启动应用）
      httpGet:
        path: /health
        port: 8080
      failureThreshold: 30
      periodSeconds: 10
    volumeMounts:           # 挂载存储卷
    - name: app-data
      mountPath: /data
  volumes:                  # 定义存储卷
  - name: app-data
    emptyDir: {}            # 临时存储卷
```

### Pod的生命周期

```
                    ┌────────────────────────────────────────┐
                    │              Pod 生命周期              │
                    └────────────────────────────────────────┘

    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────────┐
    │ Pending │───▶│ Running │───▶│ Succeeded │   │ Failed     │
    └─────────┘    └─────────┘    └─────────┘    └─────────────┘
         │              │              │
         │              │              └──────▶ 正常退出（一次性任务）
         │              │
         │              │
         │         ┌─────┴─────┐
         │         │           │
         │    ┌────┴───┐   ┌───┴────┐
         │    │ Running │   │ Unknown│
         │    └─────────┘   └────────┘
         │
         │
    ┌────┴────┐
    │ Pending │
    └─────────┘
         │
         └── 等待调度，或正在下载镜像
```

| 状态 | 说明 |
|------|------|
| **Pending** | Pod已被K8s接受，但容器镜像未创建。可能原因：调度中、下载镜像中 |
| **Running** | Pod已绑定到Node，所有容器已创建，至少有一个在运行 |
| **Succeeded** | Pod中所有容器已成功终止，不会重启 |
| **Failed** | Pod中所有容器已终止，且至少有一个非正常退出（exit code != 0） |
| **Unknown** | 无法获取Pod状态（通常是与Node通信问题） |

### 健康检查（探针）

**为什么需要探针？**

```
┌─────────────────────────────────────────────────────────┐
│                  为什么要健康检查？                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  场景：应用进程还在，但已经"假死"了                       │
│                                                         │
│  ❌ 没有探针：                                           │
│     K8s 认为容器还活着，继续往里面发请求                  │
│     → 用户请求失败                                       │
│                                                         │
│  ✅ 有探针：                                            │
│     K8s 探测到容器不健康，停止发送请求                   │
│     → 用户请求被转发到其他健康容器                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**三种探针对比：**

| 探针 | 作用 | 适用场景 |
|------|------|----------|
| **LivenessProbe** | 容器是否存活 | 检测死锁、OOM等 |
| **ReadinessProbe** | 容器是否就绪 | 检测启动中、依赖未就绪 |
| **StartupProbe** | 容器是否启动完成 | 慢启动应用 |

**探针检测方式：**

| 方式 | 说明 | 示例 |
|------|------|------|
| **exec** | 执行命令 | `kubectl exec ... curl localhost:8080/health` |
| **httpGet** | HTTP GET请求 | `curl http://localhost:8080/health` |
| **tcpSocket** | TCP端口检测 | `telnet localhost:8080` |
| **grpc** | gRPC健康检查 | gRPC健康检查协议 |

**完整示例：**

```yaml
spec:
  containers:
  - name: my-app
    image: my-app:1.0
    
    # 启动探针：容器启动时用，检测启动是否成功
    # 如果失败，K8s会杀掉容器重启
    startupProbe:
      httpGet:
        path: /healthz/startup
        port: 8080
      failureThreshold: 30      # 最多失败30次
      periodSeconds: 10        # 每10秒检查一次
      # 也就是说，最长给30*10=300秒启动时间
    
    # 存活探针：容器启动完成后持续检测
    # 如果失败，K8s会杀掉容器重启
    livenessProbe:
      httpGet:
        path: /healthz/live
        port: 8080
      initialDelaySeconds: 15   # 容器启动15秒后再检测
      periodSeconds: 10          # 每10秒检测一次
      failureThreshold: 3        # 连续失败3次才重启
    
    # 就绪探针：检测容器是否准备好接收流量
    # 如果失败，K8s会从Service中移除该Pod
    readinessProbe:
      httpGet:
        path: /healthz/ready
        port: 8080
      initialDelaySeconds: 5     # 容器启动5秒后开始检测
      periodSeconds: 5           # 每5秒检测一次
      failureThreshold: 3       # 连续失败3次才认为不健康
```

**⚠️ 小白易懵点**

> **LivenessProbe vs ReadinessProbe 的区别**
> - **LivenessProbe**：容器"死了"吗？死了就杀掉重启
> - **ReadinessProbe**：容器"准备好了"吗？没准备好就从Service移除
> 
> 典型场景：
> - 应用启动需要预热 → 用ReadinessProbe
> - 应用可能死锁 → 用LivenessProbe
> - 两者可以同时使用

### Init Container（初始化容器）

### 一句话人话
**Init Container在主容器启动前运行**，适合做初始化工作。

### 生活比喻 🔥

Init Container就像**登机前的安检**：
- 所有乘客（Init Container）必须通过安检
- 通过后才能登机（主容器启动）

### 使用场景

```yaml
# 场景1：等待数据库就绪
initContainers:
- name: wait-for-db
  image: busybox:1.36
  command:
  - sh
  - -c
  - |
    echo "Waiting for database to be ready..."
    until nc -z db-service 3306; do
      echo "Database not ready, waiting..."
      sleep 2
    done
    echo "Database is ready!"

# 场景2：从Git仓库克隆代码
initContainers:
- name: git-clone
  image: alpine/git
  args:
  - clone
  - https://github.com/myapp/config
  - /config
  volumeMounts:
  - name: config
    mountPath: /config

# 场景3：设置权限
initContainers:
- name: setup-permissions
  image: busybox:1.36
  command:
  - sh
  - -c
  - |
    chmod 777 /data
    chown -R 1000:1000 /data
  volumeMounts:
  - name: data
    mountPath: /data
```

### Sidecar模式

### 一句话人话
**Sidecar是附加在主容器旁的辅助容器**，为方便理解，你可以理解为"小跟班"。

### 生活比喻 🔥

Sidecar就像**豪华轿车旁边的服务员**：
- 主容器是豪华轿车（提供主要服务）
- Sidecar是旁边的服务员（提供辅助服务：擦车、递水）
- 两者一起提供完整的用户体验

### 常见Sidecar应用

```yaml
# Sidecar示例：日志收集
spec:
  containers:
  # 主容器：业务应用
  - name: my-app
    image: my-app:1.0
    volumeMounts:
    - name: logs
      mountPath: /var/log/myapp
  
  # Sidecar：日志收集器
  - name: log-collector
    image: fluent/fluent-bit:latest
    volumeMounts:
    - name: logs
      mountPath: /var/log/myapp
    - name: config
      mountPath: /fluent-bit/etc
    # 读取主容器的日志，发送到Elasticsearch

---

# Sidecar示例：代理容器
spec:
  containers:
  # 主容器：业务应用（不需要关心网络）
  - name: my-app
    image: my-app:1.0
    ports:
    - containerPort: 8080
  
  # Sidecar：Envoy代理（处理网络、安全、可观测性）
  - name: envoy-proxy
    image: envoyproxy/envoy:v1.25
    ports:
    - containerPort: 9901
    - containerPort: 15000
    # 代理所有进出主容器的流量

---

# Sidecar示例：健康检查
spec:
  containers:
  # 主容器
  - name: my-app
    image: my-app:1.0
  
  # Sidecar：健康检查代理
  - name: health-checker
    image: my-health-checker:1.0
    # 定期检查主容器健康状态
```

**💡 一句话总结**

> Pod是K8s的最小调度单位，一个Pod包含一个或多个容器，它们共享网络和存储。Init Container用于初始化，Sidecar用于辅助功能。

---

## 3.2 Deployment - 无状态应用的流水线

### 一句话人话
**Deployment是管理无状态应用的"流水线主管"**，负责创建、更新、扩缩容Pod。

### 生活比喻 🔥

**Deployment = 工厂流水线**

```
┌─────────────────────────────────────────────────────────┐
│                    Deployment                           │
│                                                         │
│   就像一个自动化流水线：                                  │
│                                                         │
│   ┌─────────────────────────────────────────┐           │
│   │  📋 流水线主管 (Deployment)              │           │
│   │                                          │           │
│   │   负责：                                   │           │
│   │   • 招聘工人（创建Pod）                    │           │
│   │   • 解雇不合格的工人（删除Pod）            │           │
│   │   • 培训新技能（更新版本）                 │           │
│   │   • 调整工人数量（扩缩容）                 │           │
│   │                                          │           │
│   └─────────────────────────────────────────┘           │
│                                                         │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│   │ 工人Pod1 │  │ 工人Pod2 │  │ 工人Pod3 │           │
│   │ (ReplicaSet) │  │ (ReplicaSet) │  │ (ReplicaSet) │           │
│   └──────────┘  └──────────┘  └──────────┘           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Deployment的YAML

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-deployment
  namespace: default
  labels:
    app: my-app
    environment: production
spec:
  # 副本数（同时运行的Pod数量）
  replicas: 3
  
  # 选择器（确定管理哪些Pod）
  selector:
    matchLabels:
      app: my-app
  
  # 滚动更新策略
  strategy:
    type: RollingUpdate          # 滚动更新
    rollingUpdate:
      maxSurge: 1                # 最多超出期望值的Pod数
      maxUnavailable: 0          # 滚动过程中始终保持的可用Pod数
  
  # Pod模板（定义Pod的样子）
  template:
    metadata:
      labels:
        app: my-app              # 必须包含selector中定义的标签
        version: v1
    spec:
      # 亲和性：不要把同一个应用的Pod调度到一起
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: my-app
              topologyKey: kubernetes.io/hostname
      
      containers:
      - name: my-app
        image: my-app:1.0
        ports:
        - name: http
          containerPort: 8080
        
        # 资源设置
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        
        # 健康检查
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 15
          periodSeconds: 10
        
        readinessProbe:
          httpGet:
            path: /ready
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
        
        # 环境变量
        env:
        - name: APP_ENV
          value: production
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        
        # 生命周期钩子
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 10"]
```

### 滚动更新机制

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      滚动更新流程                                        │
│                                                                         │
│  初始状态：v1版本，3个Pod                                                │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                                 │
│  │ my-app  │  │ my-app  │  │ my-app  │                                 │
│  │  v1.0   │  │  v1.0   │  │  v1.0   │                                 │
│  └─────────┘  └─────────┘  └─────────┘                                 │
│                                                                         │
│  开始更新：maxSurge=1, maxUnavailable=0                                │
│  创建1个新Pod（v2.0）                                                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                   │
│  │ my-app  │  │ my-app  │  │ my-app  │  │ my-app  │                   │
│  │  v1.0   │  │  v1.0   │  │  v1.0   │  │  v2.0 🆕 │                   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘                   │
│                                                                         │
│  继续更新：逐个替换旧Pod                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                   │
│  │ my-app  │  │ my-app  │  │ my-app  │  │ my-app  │                   │
│  │  v2.0 🆕 │  │  v1.0   │  │  v1.0   │  │  v2.0 🆕 │                   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘                   │
│                        ↓                                                │
│  旧Pod被删除                                                           │
│                        ↓                                                │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                   │
│  │ my-app  │  │ my-app  │  │ my-app  │  │         │                   │
│  │  v2.0 🆕 │  │  v2.0 🆕 │  │  v1.0   │  │ (删除)   │                   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘                   │
│                        ↓                                                │
│  完成更新：v2版本，3个Pod                                               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                                 │
│  │ my-app  │  │ my-app  │  │ my-app  │                                 │
│  │  v2.0   │  │  v2.0   │  │  v2.0   │                                 │
│  └─────────┘  └─────────┘  └─────────┘                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 滚动更新命令

```bash
# ============================================
# Deployment 滚动更新命令
# ============================================

# 1. 更新镜像版本
kubectl set image deployment/my-app my-app=my-app:2.0.0

# 2. 查看滚动更新状态
kubectl rollout status deployment/my-app

# 3. 查看更新历史
kubectl rollout history deployment/my-app

# 4. 查看特定版本的详情
kubectl rollout history deployment/my-app --revision=2

# 5. 回滚到上一版本
kubectl rollout undo deployment/my-app

# 6. 回滚到指定版本
kubectl rollout undo deployment/my-app --to-revision=2

# 7. 暂停滚动更新
kubectl rollout pause deployment/my-app

# 8. 恢复滚动更新
kubectl rollout resume deployment/my-app

# 9. 完全替代（不使用滚动更新）
kubectl replace --force -f new-deployment.yaml
```

### 扩缩容

```bash
# 扩容（增加副本）
kubectl scale deployment my-app --replicas=5

# 缩容（减少副本）
kubectl scale deployment my-app --replicas=2

# 基于CPU使用率自动扩缩容（需要metrics-server）
kubectl autoscale deployment my-app \
  --min=2 \
  --max=10 \
  --cpu-percent=80

# 查看HPA（HorizontalPodAutoscaler）
kubectl get hpa

# 删除HPA
kubectl delete hpa my-app
```

### Deployment、ReplicaSet、Pod的关系

```
┌─────────────────────────────────────────────────────────┐
│                    层级关系                               │
│                                                         │
│   Deployment（管理层）                                   │
│   │                                                       │
│   ├── 管理 ───▶ ReplicaSet v1（版本1的管理者）             │
│   │               │                                     │
│   │               ├── 创建 ───▶ Pod my-app-abc123
│   │               ├── 创建 ───▶ Pod my-app-def456
│   │               └── 创建 ───▶ Pod my-app-ghi789
│   │                                                       │
│   └── 管理 ───▶ ReplicaSet v2（版本2的管理者）             │
│                   │                                     │
│                   ├── 创建 ───▶ Pod my-app-jkl012
│                   ├── 创建 ───▶ Pod my-app-mno345
│                   └── 创建 ───▶ Pod my-app-pqr678
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**⚠️ 小白易懵点**

> **不要直接管理ReplicaSet！**
> 
> ReplicaSet是由Deployment自动创建的：
> - 你创建Deployment → Deployment创建ReplicaSet → ReplicaSet创建Pod
> - 你更新Deployment → Deployment创建新的ReplicaSet → 滚动更新
> 
> 直接操作ReplicaSet可能会被Deployment覆盖。

**💡 一句话总结**

> Deployment是管理无状态应用的最佳方式，支持滚动更新、回滚、扩缩容。核心操作：`kubectl apply`、`kubectl set image`、`kubectl rollout`。

---

## 3.3 StatefulSet - 有状态应用的管理者

### 一句话人话
**StatefulSet用于管理有状态应用**，每个实例都有稳定的身份和存储。

### 生活比喻 🔥

**StatefulSet = 银行柜员**

```
┌─────────────────────────────────────────────────────────┐
│                    StatefulSet                          │
│                                                         │
│   就像银行系统：                                         │
│                                                         │
│   每个柜员都有：                                         │
│   • 固定的工号（稳定网络标识）                           │
│   • 自己的抽屉（独立存储）                               │
│   • 有序的上班顺序（有序部署）                           │
│   • 交接班记录（数据同步）                               │
│                                                         │
│   ┌──────────────────────────────────────────┐          │
│   │ 柜员-0 (bank-0)           抽屉-0 (PV-0)    │          │
│   │  ├── IP: 10.244.1.10                    │          │
│   │  ├── DNS: bank-0.bank.default.svc     │          │
│   │  └── 存储: /data                         │          │
│   └──────────────────────────────────────────┘          │
│   ┌──────────────────────────────────────────┐          │
│   │ 柜员-1 (bank-1)           抽屉-1 (PV-1)    │          │
│   │  ├── IP: 10.244.2.10                    │          │
│   │  ├── DNS: bank-1.bank.default.svc     │          │
│   │  └── 存储: /data                         │          │
│   └──────────────────────────────────────────┘          │
│   ┌──────────────────────────────────────────┐          │
│   │ 柜员-2 (bank-2)           抽屉-2 (PV-2)    │          │
│   │  ├── IP: 10.244.1.15                    │          │
│   │  ├── DNS: bank-2.bank.default.svc     │          │
│   │  └── 存储: /data                         │          │
│   └──────────────────────────────────────────┘          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### StatefulSet vs Deployment

| 特性 | Deployment | StatefulSet |
|------|------------|-------------|
| **Pod标识** | 随机的（如my-app-abc123） | 稳定的序号（如my-app-0） |
| **网络标识** | 每次重启IP可能变化 | 稳定的DNS名称 |
| **存储** | 共享存储或无持久化 | 独立持久存储 |
| **部署顺序** | 并行 | 顺序（0→1→2→3） |
| **删除顺序** | 并行 | 逆序（3→2→1→0） |
| **适用场景** | 无状态Web应用 | 数据库、消息队列 |

### StatefulSet的YAML

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql                         # StatefulSet名称
  namespace: default
spec:
  serviceName: mysql-headless         # Headless Service名称（重要！）
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  
  # Pod模板
  template:
    metadata:
      labels:
        app: mysql
    spec:
      # 初始化容器：等待主节点就绪
      initContainers:
      - name: init-mysql
        image: mysql:8.0
        command:
        - bash
        - "-c"
        - |
          # 等待主节点创建完成
          until host mysql-0.mysql-headless; do
            echo "Waiting for mysql-0 to be ready..."
            sleep 5
          done
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
      
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - name: mysql
          containerPort: 3306
        
        # 环境变量
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: password
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        
        # 健康检查
        livenessProbe:
          exec:
            command: ["mysqladmin", "ping", "-h", "localhost"]
          initialDelaySeconds: 30
          periodSeconds: 10
        
        readinessProbe:
          exec:
            command:
            - mysqladmin
            - ping
            - "-h"
            - localhost
          initialDelaySeconds: 20
          periodSeconds: 5
        
        # 资源限制
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1000m
            memory: 2Gi
        
        # 存储卷挂载
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
  
  # 存储卷模板（每个Pod独立的PVC）
  volumeClaimTemplates:
  - metadata:
      name: mysql-data                 # PVC模板名称
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "fast-ssd"    # 存储类
      resources:
        requests:
          storage: 50Gi               # 每个Pod请求50Gi存储
```

### StatefulSet的核心特性

**1. 稳定的网络标识**

```bash
# Pod名称格式：StatefulSet名称-序号
# 例如：mysql-0, mysql-1, mysql-2

# DNS名称格式：Pod名称.Service名称.命名空间.svc.cluster.local
# 例如：mysql-0.mysql-headless.default.svc.cluster.local
```

**2. 有序的部署和扩展**

```bash
# 部署顺序：0 → 1 → 2 → ...
# 删除顺序：... → 2 → 1 → 0

# 每个Pod必须 Ready 且 Running 后，才能创建下一个Pod
```

**3. 独立的持久存储**

```yaml
# 每个Pod有独立的PVC
# mysql-0 → mysql-data-mysql-0 (PVC)
# mysql-1 → mysql-data-mysql-1 (PVC)
# mysql-2 → mysql-data-mysql-2 (PVC)

# PVC会随着Pod一起删除（如果设置了）
```

### 有状态应用示例：MySQL主从集群

```yaml
# 1. ConfigMap：MySQL配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-config
  namespace: default
data:
  master.cnf: |
    [mysqld]
    server-id=1
    log-bin=mysql-bin
    binlog-format=ROW
  
  slave.cnf: |
    [mysqld]
    log_bin=mysql-bin
    binlog-format=ROW

---
# 2. Secret：MySQL密码
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
type: Opaque
stringData:
  password: "MySecurePassword123!"

---
# 3. Headless Service（必需！）
apiVersion: v1
kind: Service
metadata:
  name: mysql-headless
  labels:
    app: mysql
spec:
  ports:
  - name: mysql
    port: 3306
  clusterIP: None          # 关键！clusterIP=None 表示Headless Service
  selector:
    app: mysql

---
# 4. StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql-headless
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  
  template:
    metadata:
      labels:
        app: mysql
    spec:
      initContainers:
      # 主节点不需要等待，从节点需要等待主节点
      - name: wait-for-master
        image: busybox:1.36
        command:
        - sh
        - -c
        - |
          # 如果不是第一个Pod，等待主节点
          if [ ${HOSTNAME##*-} != "0" ]; then
            until nslookup mysql-0.mysql-headless; do
              echo "Waiting for master to be ready..."
              sleep 5
            done
          fi
      
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - name: mysql
          containerPort: 3306
        
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: password
        
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
        
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
  
  volumeClaimTemplates:
  - metadata:
      name: mysql-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "standard"
      resources:
        requests:
          storage: 10Gi
```

**⚠️ 小白易懵点**

> **StatefulSet必须配合Headless Service使用！**
> 
> Headless Service的`clusterIP: None`让每个Pod都有自己的DNS记录，这样Pod之间才能通过DNS名称互相访问。

**💡 一句话总结**

> StatefulSet用于有状态应用，提供稳定的网络标识、独立的持久存储、有序的部署/删除。典型应用：数据库、消息队列、分布式存储。

---

## 3.4 DaemonSet - 每节点守护者

### 一句话人话
**DaemonSet确保每个（或者符合某些条件的）节点上都运行一个Pod副本**。

### 生活比喻 🔥

**DaemonSet = 物业保安**

```
┌─────────────────────────────────────────────────────────┐
│                    DaemonSet                            │
│                                                         │
│   就像每个楼层都有保安：                                   │
│                                                         │
│   ┌─────────────────────────────────────────┐           │
│   │ 楼层1 (Node1)           👮 保安-1 (Pod)   │           │
│   │    └── 监控电梯、大堂                     │           │
│   └─────────────────────────────────────────┘           │
│   ┌─────────────────────────────────────────┐           │
│   │ 楼层2 (Node2)           👮 保安-2 (Pod)   │           │
│   │    └── 监控电梯、大堂                     │           │
│   └─────────────────────────────────────────┘           │
│   ┌─────────────────────────────────────────┐           │
│   │ 楼层3 (Node3)           👮 保安-3 (Pod)   │           │
│   │    └── 监控电梯、大堂                     │           │
│   └─────────────────────────────────────────┘           │
│                                                         │
│   新建楼层 → 自动派保安                                  │
│   删除楼层 → 自动撤保安                                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### DaemonSet的应用场景

| 场景 | 示例 |
|------|------|
| **日志收集** | Fluentd、Filebeat |
| **监控代理** | Prometheus Node Exporter |
| **网络插件** | Calico、Flannel |
| **存储插件** | Ceph、GlusterFS |
| **系统工具** | node-problem-detector |

### DaemonSet的YAML

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd-elasticsearch
  namespace: kube-system
  labels:
    app: fluentd
spec:
  # 选择器
  selector:
    matchLabels:
      app: fluentd
  
  # 更新策略
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
  
  # Pod模板
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      # 容忍所有污点（确保能在所有节点运行）
      tolerations:
      - operator: Exists  # 容忍所有污点
      
      # 亲和性
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              # 不在Master节点运行
              - key: node-role.kubernetes.io/master
                operator: DoesNotExist
      
      containers:
      - name: fluentd
        image: quay.io/fluentd_elasticsearch/fluentd:v2.5.2
        
        resources:
          limits:
            cpu: 500m
            memory: 512Mi
          requests:
            cpu: 100m
            memory: 200Mi
        
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
        
        # 允许Daemonset获取宿主机网络
        securityContext:
          privileged: true
      
      # 使用宿主机的文件系统
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

### DaemonSet vs Deployment

| 特性 | DaemonSet | Deployment |
|------|-----------|------------|
| **调度方式** | 每个节点运行一个 | 由Scheduler决定 |
| **副本数** | 固定等于符合条件的节点数 | 可以自定义 |
| **缩容** | 不支持手动缩容 | 支持 |
| **用途** | 系统级服务 | 应用级服务 |

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

**💡 一句话总结**

> DaemonSet用于每个节点都需要运行的服务，如日志收集、监控代理、网络插件等。

---

## 3.5 Job与CronJob - 任务执行器

### 一句话人话
**Job用于执行一次性任务，CronJob用于执行定时任务**。

### 生活比喻 🔥

**Job = 一次性外卖订单**

```
┌─────────────────────────────────────────────────────────┐
│                       Job                               │
│                                                         │
│   就像点一次外卖：                                        │
│                                                         │
│   1. 下单（创建Job）                                     │
│   2. 商家做菜（执行任务）                                 │
│   3. 送达确认（任务完成）                                 │
│   4. 订单结束（Pod可能保留或删除）                        │
│                                                         │
│   可能的情况：                                           │
│   ✅ 成功：订单完成                                      │
│   ❌ 失败：重试或放弃                                    │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                     CronJob                             │
│                                                         │
│   就像每天定时闹钟：                                      │
│                                                         │
│   🕐 09:00 上班打卡 → Job执行                           │
│   🕐 18:00 下班打卡 → Job执行                           │
│   🕐 每天凌晨备份 → Job执行                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Job的YAML

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: data-migration
  namespace: default
spec:
  # 手动设置并行度（可选）
  parallelism: 2
  
  # 失败重试次数
  backoffLimit: 4
  
  # 超时时间
  activeDeadlineSeconds: 600
  
  # 成功完成的Pod数
  completions: 5
  
  ttlSecondsAfterFinished: 3600  # 完成后自动删除（K8s 1.27+）
  
  template:
    metadata:
      labels:
        app: data-migration
    spec:
      # 重启策略
      restartPolicy: OnFailure
      
      containers:
      - name: migrator
        image: my-migration-tool:1.0
        command: ["/bin/sh", "-c"]
        args:
        - |
          echo "Starting data migration..."
          # 迁移数据的脚本
          /app/migrate.sh --batch-size=1000
          echo "Migration completed!"
        
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
      
      # 容忍
      tolerations:
      - key: "node-role"
        operator: "Exists"
```

### CronJob的YAML

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-job
  namespace: default
spec:
  # Cron表达式：分 时 日 月 周
  # 每天凌晨2点执行
  schedule: "0 2 * * *"
  
  # 时区（K8s 1.27+）
  timeZone: "Asia/Shanghai"
  
  # 并发策略
  concurrencyPolicy: Forbid  # Forbid | Allow | Replace
  
  # 是否挂起（暂停执行）
  suspend: false
  
  # 成功Job保留数
  successfulJobsHistoryLimit: 3
  
  # 失败Job保留数
  failedJobsHistoryLimit: 1
  
  # Job的超时时间
  jobTemplate:
    spec:
      # 任务超时
      activeDeadlineSeconds: 3600
      
      # 重试次数
      backoffLimit: 3
      
      template:
        metadata:
          labels:
            app: backup-job
        spec:
          restartPolicy: OnFailure
          
          containers:
          - name: backup
            image: my-backup-tool:1.0
            command: ["/bin/sh", "-c"]
            args:
            - |
              echo "Starting backup at $(date)"
              
              # 备份数据库
              mysqldump -h mysql -u root -p$MYSQL_ROOT_PASSWORD mydb > /backup/mydb-$(date +%Y%m%d).sql
              
              # 备份到对象存储
              rclone copy /backup/myapp-$(date +%Y%m%d).sql s3:my-bucket/backups/
              
              echo "Backup completed!"
            
            env:
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-secret
                  key: password
            
            volumeMounts:
            - name: backup-data
              mountPath: /backup
            
            resources:
              requests:
                cpu: 100m
                memory: 128Mi
              limits:
                cpu: 1000m
                memory: 1Gi
          
          volumes:
          - name: backup-data
            persistentVolumeClaim:
              claimName: backup-pvc
          
          # 容忍
          tolerations:
          - key: "backup"
            operator: "Exists"
            effect: "NoSchedule"
```

### Cron表达式详解

```bash
# Cron表达式格式：分 时 日 月 周

# 常用示例：
"0 * * * *"        # 每小时整点
"0 0 * * *"        # 每天午夜
"0 2 * * *"        # 每天凌晨2点
"0 9 * * 1-5"      # 工作日早上9点
"*/15 * * * *"     # 每15分钟
"0 */2 * * *"      # 每2小时
"0 0 1 * *"        # 每月1号
"0 0 * * 0"        # 每周日

# 特殊字符：
# * - 任意值
# , - 列表，如 1,3,5
# - - 范围，如 1-5
# / - 步长，如 */15 表示每15个单位
```

### 常见的Job使用场景

```yaml
# 场景1：数据库迁移
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration
spec:
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: migrator
        image: myapp-migration:1.0
        env:
        - name: MIGRATION_MODE
          value: "up"

---
# 场景2：批量数据处理
apiVersion: batch/v1
kind: Job
metadata:
  name: batch-processor
spec:
  parallelism: 5  # 5个Pod并行处理
  completions: 50 # 总共处理50个批次
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: processor
        image: myapp-processor:1.0
        args:
        - "--batch-id=$(BATCH_ID)"
        env:
        - name: BATCH_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name

---
# 场景3：一次性计算任务
apiVersion: batch/v1
kind: Job
metadata:
  name: one-time-computation
spec:
  ttlSecondsAfterFinished: 300  # 5分钟后自动清理
  template:
    spec:
      restartPolicy: Never  # 任务完成后不重启
      containers:
      - name: calculator
        image: myapp-calculator:1.0
        command: ["/app/compute.sh"]
```

**⚠️ 小白易懵点**

> **Job的restartPolicy**
> 
> Job只支持两种restartPolicy：
> - `OnFailure`：容器失败时重启容器
> - `Never`：容器失败时不重启，等待Job控制器创建新Pod
> 
> **不支持** `restartPolicy: Always`！

**💡 一句话总结**

> Job用于一次性任务，CronJob用于定时任务。Job的关键参数：completions（成功次数）、parallelism（并行度）、backoffLimit（重试次数）。

---

## 3.6 本章实战：完整应用部署

### 项目需求

部署一个微服务应用，包含：
- Web前端（Deployment，3个副本）
- API后端（StatefulSet，3个副本，有数据库）
- Redis缓存（StatefulSet，3个副本）
- 定时备份任务（CronJob）

### 完整YAML

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# ============================================
# 微服务应用完整部署清单
# ============================================

# ============ Namespace ============
apiVersion: v1
kind: Namespace
metadata:
  name: myapp
  labels:
    environment: production

---
# ============ ConfigMap ============
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-frontend-config
  namespace: myapp
data:
  NGINX_CONF: |
    server {
        listen 80;
        server_name localhost;
        location / {
            proxy_pass http://api-backend:8080;
        }
    }
  APP_ENV: "production"
  LOG_LEVEL: "info"

---
# ============ Secret ============
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: myapp
type: Opaque
stringData:
  API_SECRET_KEY: "super-secret-key-12345"
  DB_PASSWORD: "SecurePassword123!"

---
# ============ Service Account ============
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp-sa
  namespace: myapp

---
# ============ RBAC ============
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: myapp-role
  namespace: myapp
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: myapp-rolebinding
  namespace: myapp
subjects:
- kind: ServiceAccount
  name: myapp-sa
  namespace: myapp
roleRef:
  kind: Role
  name: myapp-role
  apiGroup: rbac.authorization.k8s.io

---
# ============ Web Frontend Deployment ============
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-frontend
  namespace: myapp
  labels:
    app: web-frontend
    component: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-frontend
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: web-frontend
        component: frontend
        version: v1
    spec:
      serviceAccountName: myapp-sa
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - name: http
          containerPort: 80
        
        volumeMounts:
        - name: nginx-config
          mountPath: /etc/nginx/conf.d
          readOnly: true
        
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 250m
            memory: 256Mi
        
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
        
        env:
        - name: UPSTREAM_SERVER
          value: "api-backend:8080"
      
      volumes:
      - name: nginx-config
        configMap:
          name: web-frontend-config
          items:
          - key: NGINX_CONF
            path: default.conf

---
# ============ API Backend Deployment ============
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-backend
  namespace: myapp
  labels:
    app: api-backend
    component: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-backend
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: api-backend
        component: backend
        version: v1
    spec:
      serviceAccountName: myapp-sa
      containers:
      - name: api
        image: myapp/api:v1.0.0
        ports:
        - name: http
          containerPort: 8080
        
        env:
        - name: NODE_ENV
          value: production
        - name: DB_HOST
          value: "mysql-readwrite"
        - name: DB_PORT
          value: "3306"
        - name: DB_NAME
          value: "myapp"
        - name: DB_USER
          value: "appuser"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DB_PASSWORD
        - name: REDIS_HOST
          value: "redis"
        - name: REDIS_PORT
          value: "6379"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: API_SECRET_KEY
        
        resources:
          requests:
            cpu: 200m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 15
          periodSeconds: 10
        
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5

---
# ============ MySQL StatefulSet ============
apiVersion: v1
kind: Service
metadata:
  name: mysql-headless
  namespace: myapp
spec:
  ports:
  - name: mysql
    port: 3306
  clusterIP: None
  selector:
    app: mysql

---
apiVersion: apps/v1
kind: Service
metadata:
  name: mysql-readwrite
  namespace: myapp
spec:
  ports:
  - name: mysql
    port: 3306
  selector:
    app: mysql
  sessionAffinity: ClientIP

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
  namespace: myapp
spec:
  serviceName: mysql-headless
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - name: mysql
          containerPort: 3306
        
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DB_PASSWORD
        - name: MYSQL_DATABASE
          value: "myapp"
        - name: MYSQL_USER
          value: "appuser"
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DB_PASSWORD
        
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1000m
            memory: 2Gi
        
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
        
        livenessProbe:
          exec:
            command: ["mysqladmin", "ping", "-h", "localhost"]
          initialDelaySeconds: 30
          periodSeconds: 10
        
        readinessProbe:
          exec:
            command: ["mysqladmin", "ping", "-h", "localhost"]
          initialDelaySeconds: 20
          periodSeconds: 5
      
  volumeClaimTemplates:
  - metadata:
      name: mysql-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "standard"
      resources:
        requests:
          storage: 10Gi

---
# ============ Redis StatefulSet ============
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: myapp
spec:
  ports:
  - name: redis
    port: 6379
  clusterIP: None
  selector:
    app: redis

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis
  namespace: myapp
spec:
  serviceName: redis
  replicas: 3
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - name: redis
          containerPort: 6379
        
        args:
        - "--requirepass"
        - "$(REDIS_PASSWORD)"
        - "--appendonly"
        - "yes"
        
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DB_PASSWORD
        
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        
        volumeMounts:
        - name: redis-data
          mountPath: /data
      
  volumeClaimTemplates:
  - metadata:
      name: redis-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "standard"
      resources:
        requests:
          storage: 1Gi

---
# ============ CronJob 备份任务 ============
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup
  namespace: myapp
spec:
  schedule: "0 2 * * *"
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      backoffLimit: 3
      activeDeadlineSeconds: 3600
      template:
        metadata:
          labels:
            app: db-backup
        spec:
          restartPolicy: OnFailure
          containers:
          - name: backup
            image: mysql:8.0
            command:
            - /bin/sh
            - -c
            args:
            - |
              echo "Starting backup at $(date)"
              mysqldump -h mysql-readwrite -u appuser -p$DB_PASSWORD myapp > /backup/myapp-$(date +%Y%m%d-%H%M%S).sql
              echo "Backup completed at $(date)"
            
            env:
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: DB_PASSWORD
            
            volumeMounts:
            - name: backup-data
              mountPath: /backup
            
            resources:
              requests:
                cpu: 100m
                memory: 128Mi
              limits:
                cpu: 500m
                memory: 512Mi
          
          volumes:
          - name: backup-data
            persistentVolumeClaim:
              claimName: backup-pvc
          
          tolerations:
          - key: "backup"
            operator: "Exists"
            effect: "NoSchedule"

---
# ============ Services ============
apiVersion: v1
kind: Service
metadata:
  name: web-frontend
  namespace: myapp
spec:
  type: NodePort
  selector:
    app: web-frontend
  ports:
  - name: http
    port: 80
    targetPort: 80
    nodePort: 30080

---
apiVersion: v1
kind: Service
metadata:
  name: api-backend
  namespace: myapp
spec:
  type: ClusterIP
  selector:
    app: api-backend
  ports:
  - name: http
    port: 8080
    targetPort: 8080
```

### 部署步骤

```bash
# 1. 创建所有资源
kubectl apply -f deployment.yaml

# 2. 查看部署状态
kubectl get all -n myapp

# 3. 查看Pod详情
kubectl describe pods -n myapp

# 4. 查看日志
kubectl logs -n myapp deployment/api-backend

# 5. 查看CronJob
kubectl get cronjob -n myapp

# 6. 手动触发备份Job
kubectl create job backup-manual --from=cronjob/db-backup -n myapp

# 7. 扩容
kubectl scale deployment web-frontend -n myapp --replicas=5

# 8. 更新镜像
kubectl set image deployment/api-backend api=myapp/api:v1.1.0 -n myapp

# 9. 回滚
kubectl rollout undo deployment/api-backend -n myapp

# 10. 清理
kubectl delete namespace myapp
```

---

## 第三篇总结

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### 核心资源对象速查

| 资源对象 | 用途 | 关键词 |
|----------|------|--------|
| **Pod** | 最小调度单位 | 容器、探针、Init |
| **Deployment** | 无状态应用 | 滚动更新、回滚、扩缩容 |
| **StatefulSet** | 有状态应用 | 稳定标识、独立存储 |
| **DaemonSet** | 节点守护 | 每节点一个 |
| **Job** | 一次性任务 | 批处理 |
| **CronJob** | 定时任务 | 调度 |

### 下一章预告

在下一章《服务发现与网络》中，我们将学习：
- Service的四种类型
- Ingress七层路由
- NetworkPolicy网络策略
- CoreDNS服务名解析

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

**💡 一句话总结**

> K8s的核心资源对象：Pod是最小单位，Deployment管理无状态应用，StatefulSet管理有状态应用，DaemonSet每节点一个，Job/CronJob处理任务。

---

*感谢学习第三篇！有问题欢迎随时提问。*

# 第四篇：服务发现与网络

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

## 前言：K8s的网络迷宫

想象一下你住在一个巨大的写字楼里：

- **每个房间（Pod）** 都有不同的住户
- **房间号（IP地址）** 经常变化（因为有人退房、有人入住）
- **部门（Service）** 需要一个固定的联系电话
- **公司域名（DNS）** 需要一个固定的对外名称

如果没有服务发现，你怎么找到你要找的人？

**K8s的服务发现与网络，就是解决这个问题的！**

---

## 4.1 Service - 服务发现

### 一句话人话
**Service是一组Pod的统一入口**，提供稳定的IP地址和DNS名称，自动负载均衡到后端Pod。

### 生活比喻 🔥

**Service = 电话总机**

```
┌─────────────────────────────────────────────────────────┐
│                    Service                              │
│                                                         │
│   就像公司电话总机：                                      │
│                                                         │
│   ┌─────────────────────────────────────────┐           │
│   │  📞 总机：400-123-4567                 │           │
│   │      ↓                                  │           │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐ │           │
│   │  │  客服1   │  │  客服2   │  │  客服3   │ │           │
│   │  │ 分机101 │  │ 分机102 │  │ 分机103 │ │           │
│   │  └─────────┘  └─────────┘  └─────────┘ │           │
│   │      ↓              ↓              ↓    │           │
│   │   有人接听      有人接听      有人接听    │           │
│   └─────────────────────────────────────────┘           │
│                                                         │
│   客户拨打总机 → 自动分配到空闲的客服                     │
│   客服换人了？ → 总机号码不变，客户无感知                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Service的工作原理

```
┌─────────────────────────────────────────────────────────────────┐
│                       Service 原理                              │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                                                         │   │
│   │   Service: my-app (10.96.0.100:80)                     │   │
│   │                                                         │   │
│   │   Selector: app=my-app                                │   │
│   │                                                         │   │
│   │   ┌──────────────────────────────────────────────┐     │   │
│   │   │                    Pod                       │     │   │
│   │   │   app: my-app                               │     │   │
│   │   │                                              │     │   │
│   │   │   ┌─────────┐                               │     │   │
│   │   │   │ Pod-1   │ ← 10.244.1.10:8080           │     │   │
│   │   │   │ (Ready) │                             │     │   │
│   │   │   └─────────┘                               │     │   │
│   │   │   ┌─────────┐                               │     │   │
│   │   │   │ Pod-2   │ ← 10.244.2.15:8080           │     │   │
│   │   │   │ (Ready) │                             │     │   │
│   │   │   └─────────┘                               │     │   │
│   │   │   ┌─────────┐                               │     │   │
│   │   │   │ Pod-3   │ ← 10.244.1.20:8080           │     │   │
│   │   │   │ (NotReady)│                           │     │   │
│   │   │   └─────────┘                               │     │   │
│   │   │          ↑                                  │     │   │
│   │   │    kube-proxy                             │     │   │
│   │   │    只转发到Ready的Pod！                    │     │   │
│   │   └──────────────────────────────────────────────┘     │   │
│   │                                                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Service的四种类型

| 类型 | 说明 | 比喻 | 使用场景 |
|------|------|------|----------|
| **ClusterIP** | 集群内部访问 | 内部分机 | 默认，内部服务调用 |
| **NodePort** | 通过节点端口访问 | 开门店 | 开发测试、小型服务 |
| **LoadBalancer** | 云厂商负载均衡 | 外部热线 | 生产环境 |
| **ExternalName** | CNAME映射 | 呼叫转接 | 外部服务别名 |

### 4.1.1 ClusterIP - 内部总机

### 一句话人话
**ClusterIP是默认的Service类型**，只在集群内部访问，提供一个固定的虚拟IP。

### 生活比喻 🔥

ClusterIP就像**酒店内部电话**：
- 只能在酒店内拨打
- 每个房间有一个内部号码
- 拨打内部号码可以转接到对应房间

### ClusterIP的YAML

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
  namespace: default
  labels:
    app: my-app
spec:
  # Service类型
  type: ClusterIP
  
  # 选择器：确定哪些Pod属于这个Service
  selector:
    app: my-app
  
  # 端口配置
  ports:
  # Service端口（ClusterIP监听的端口）
  - name: http
    port: 80
    # Pod端口（targetPort可以是端口号或端口名称）
    targetPort: 8080
    protocol: TCP
  
  # 多个端口
  - name: https
    port: 443
    targetPort: 8443
    protocol: TCP
  
  # Session亲和性（可选）
  sessionAffinity: None  # None | ClientIP
  
  # 健康检查端口（可选）
  healthCheckNodePort: 0
```

### ClusterIP使用场景

```yaml
# 场景：前端服务访问后端API
# 前端Pod中配置环境变量
env:
- name: API_SERVICE_HOST
  value: "my-api-service"    # 直接使用Service名称
- name: API_SERVICE_PORT
  value: "80"

# 访问方式
# 1. DNS方式（推荐）
# curl http://my-api-service/endpoint

# 2. 完整DNS名称
# curl http://my-api-service.default.svc.cluster.local/endpoint

# 3. ClusterIP方式
# curl http://10.96.0.100/endpoint
```

### 4.1.2 NodePort - 开门店

### 一句话人话
**NodePort在每个Node上开放一个端口**，通过`NodeIP:NodePort`可以从集群外部访问。

### 生活比喻 🔥

NodePort就像**路边开设服务窗口**：
- 在大楼每个入口（Node）都开一个窗口
- 客户可以从任意入口的窗口办事
- 窗口号码固定（30000-32767）

### NodePort的YAML

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-nodeport
  namespace: default
spec:
  type: NodePort
  
  selector:
    app: my-app
  
  ports:
  - name: http
    port: 80          # Service端口
    targetPort: 8080  # Pod端口
    nodePort: 30080  # NodePort（可选，不指定会随机分配）
    # nodePort范围：30000-32767
  
  # 多个端口
  - name: https
    port: 443
    targetPort: 8443
    nodePort: 30443
```

### NodePort访问方式

```bash
# 访问方式
# http://<NodeIP>:30080/

# NodeIP 可以是任意节点的IP
# K8s会自动将流量路由到有Pod运行的节点

# Minikube环境
minikube ip
# 例如返回 192.168.49.2
# 访问 http://192.168.49.2:30080/
```

### NodePort的网络流向

```
外部请求
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   Node1 (192.168.1.10)                                  │
│   ┌─────────────────────────────────────┐               │
│   │  NodePort: 30080                    │               │
│   │         ↓                           │               │
│   │  kube-proxy                         │               │
│   │         ↓                           │               │
│   │  ClusterIP: 10.96.0.100             │               │
│   │         ↓                           │               │
│   │  负载均衡到后端Pod                   │               │
│   └─────────────────────────────────────┘               │
│                                                         │
│   Node2 (192.168.1.11)                                  │
│   ┌─────────────────────────────────────┐               │
│   │  NodePort: 30080                    │               │
│   │         ↓                           │               │
│   │  kube-proxy                         │               │
│   └─────────────────────────────────────┘               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 4.1.3 LoadBalancer - 外部总机

### 一句话人话
**LoadBalancer在云环境创建外部负载均衡器**，提供公网IP或ELB访问。

### 生活比喻 🔥

LoadBalancer就像**公司对外热线**：
- 电信运营商提供专线号码
- 自动分配到空闲的客服
- 自动扩展客服数量
- 故障自动转移

### LoadBalancer的YAML

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-lb
  namespace: default
  labels:
    app: my-app
  annotations:
    # 云厂商特定的注解（以阿里云为例）
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-id: "lb-xxx"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-backend-label: "zone=hangzhou"
spec:
  type: LoadBalancer
  
  selector:
    app: my-app
  
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP
  
  - name: https
    port: 443
    targetPort: 8443
    protocol: TCP
  
  # 负载均衡配置
  externalTrafficPolicy: Cluster  # Cluster | Local
  # Cluster: 流量可能经过多个节点
  # Local: 流量只经过有Pod的节点，保留源IP
  
  # 分配静态IP
  loadBalancerIP: "1.2.3.4"
  
  # 负载均衡器类型
  # external:
  #   loadBalancerSourceRanges:
  #   - "10.0.0.0/8"
```

### LoadBalancer类型对比

| 环境 | 支持情况 | 额外配置 |
|------|----------|----------|
| **云厂商（AWS/GCP/Azure/阿里云）** | 原生支持 | 需要云厂商注解 |
| **裸金属服务器** | MetalLB | 需要安装配置 |
| **本地环境** | 无 | 使用NodePort或Ingress |

### 4.1.4 ExternalName - 呼叫转接

### 一句话人话
**ExternalName将Service映射到外部域名**，就像呼叫转接。

### 生活比喻 🔥

ExternalName就像**呼叫转接服务**：
- 你拨打公司总机
- 总机把你的电话转接到外部合作伙伴
- 对你来说，好像还是打给公司的

### ExternalName的YAML

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-external-service
  namespace: default
spec:
  type: ExternalName
  # 外部域名
  externalName: api.external.com
```

### ExternalName使用场景

```yaml
# 场景1：访问外部数据库（开发环境用本地，生产环境用云数据库）
# 开发环境：外部MySQL
apiVersion: v1
kind: Service
metadata:
  name: mysql
spec:
  type: ExternalName
  externalName: mysql-dev.local

# 生产环境：云RDS
apiVersion: v1
kind: Service
metadata:
  name: mysql
spec:
  type: ExternalName
  externalName: rm-xxx.mysql.rds.aliyuncs.com

# 场景2：内部服务别名
apiVersion: v1
kind: Service
metadata:
  name: legacy-api
spec:
  type: ExternalName
  externalName: api-backend.default.svc.cluster.local

# 访问方式
# curl http://mysql/default.svc.cluster.local
# curl http://legacy-api/default.svc.cluster.local
```

**⚠️ 小白易懵点**

> **ExternalName vs Endpoint**
> - ExternalName：返回CNAME记录，DNS解析在客户端完成
> - ClusterIP/NodePort/LoadBalancer：返回A记录，kube-proxy做负载均衡
> 
> ExternalName不能设置selector和ports，它只是一个"别名"。

**💡 一句话总结**

> Service四种类型：
> - ClusterIP：集群内部访问
> - NodePort：开发测试访问
> - LoadBalancer：生产环境访问
> - ExternalName：外部服务别名

---

## 4.2 Ingress - 七层路由

### 一句话人话
**Ingress是K8s的"大楼大堂"**，统一管理外部HTTP/HTTPS访问，提供基于域名和路径的路由。

### 生活比喻 🔥

**Ingress = 大楼大堂**

```
┌─────────────────────────────────────────────────────────┐
│                      Ingress                            │
│                                                         │
│   就像写字楼大堂：                                        │
│                                                         │
│   ┌─────────────────────────────────────────┐           │
│   │  🏢 大楼入口 (Ingress)                   │           │
│   │                                          │           │
│   │   客户A → api.example.com    → 7层       │           │
│   │   客户B → web.example.com    → 8层       │           │
│   │   客户C → admin.example.com  → 12层      │           │
│   │   客户D → /api/*            → API服务    │           │
│   │   客户E → /static/*         → 静态资源   │           │
│   │                                          │           │
│   └─────────────────────────────────────────┘           │
│                                                         │
│   大堂管理员（Ingress Controller）                      │
│   • 识别访客身份（域名）                                 │
│   • 指引到正确楼层（路由规则）                           │
│   • 登记访客（TLS证书）                                  │
│   • 安检（认证、限流）                                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Ingress vs Service

| 特性 | Service | Ingress |
|------|---------|---------|
| **层级** | 四层（TCP/UDP） | 七层（HTTP/HTTPS） |
| **路由依据** | 端口 | 域名+路径 |
| **SSL/TLS** | 需要LB支持 | 原生支持 |
| **基于Cookie的会话保持** | 不支持 | 支持 |
| **重写路径** | 不支持 | 支持 |
| **限流** | 不支持 | 支持 |

### Ingress Controller

Ingress需要配合Ingress Controller使用，常用的有：

| Controller | 说明 |
|------------|------|
| **Nginx Ingress Controller** | 最流行，功能全面 |
| **Traefik** | 轻量，配置简单 |
| **Kong** | API网关功能强 |
| **云厂商ALB/CLB** | 云原生集成好 |

### Nginx Ingress Controller安装

```bash
# 使用Helm安装
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer
```

### Ingress的YAML

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  namespace: default
  labels:
    app: my-app
  annotations:
    # Nginx Ingress特定注解
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    
    # SSL重定向
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    
    # 代理超时
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "30"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    
    # 限流
    nginx.ingress.kubernetes.io/limit-rps: "100"
    
    # CORS
    nginx.ingress.kubernetes.io/enable-cors: "true"

spec:
  ingressClassName: nginx  # 指定Ingress Class
  
  # TLS配置
  tls:
  - hosts:
    - api.example.com
    - web.example.com
    secretName: my-tls-secret  # 保存证书的Secret
  
  # 路由规则
  rules:
  # 基于主机名的路由
  - host: api.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
      
      - path: /docs
        pathType: Prefix
        backend:
          service:
            name: docs-service
            port:
              number: 80
  
  # 默认主机（没有匹配host时使用）
  - host: ""
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: default-service
            port:
              number: 80
```

### 完整的TLS配置示例

```yaml
# 1. 创建自签名证书（仅测试用）
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -out tls.crt \
  -keyout tls.key \
  -subj "/CN=example.com/O=example"

# 2. 创建Secret保存证书
kubectl create secret tls my-tls-secret \
  --cert=tls.crt \
  --key=tls.key

# 3. 或使用cert-manager自动管理证书
# 参考下一节的cert-manager配置
```

### 基于路径的路由

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: path-based-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  ingressClassName: nginx
  rules:
  - host: myapp.example.com
    http:
      paths:
      # 前端应用
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
      
      # API服务
      - path: /api/v1
        pathType: Prefix
        backend:
          service:
            name: api-v1-service
            port:
              number: 8080
      
      # 管理后台
      - path: /admin
        pathType: Prefix
        backend:
          service:
            name: admin-service
            port:
              number: 80
      
      # 静态资源
      - path: /static
        pathType: Prefix
        backend:
          service:
            name: static-service
            port:
              number: 80
```

### 基于主机名的路由（虚拟主机）

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-host-ingress
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - www.example.com
    secretName: www-tls
  - hosts:
    - api.example.com
    secretName: api-tls
  - hosts:
    - admin.example.com
    secretName: admin-tls
  
  rules:
  # www.example.com
  - host: www.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
  
  # api.example.com
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
  
  # admin.example.com
  - host: admin.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: admin-service
            port:
              number: 80
```

### 使用cert-manager自动管理证书

```yaml
# 1. 安装cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# 2. 创建ClusterIssuer
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx

# 3. 修改Ingress添加证书注解
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - myapp.example.com
    secretName: myapp-tls  # cert-manager会自动创建和管理这个Secret
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp-service
            port:
              number: 80
```

**💡 一句话总结**

> Ingress是HTTP/HTTPS的入口，提供基于域名和路径的路由。配合Ingress Controller使用，支持TLS、路径重写、限流等功能。

---

## 4.3 NetworkPolicy - 网络策略

### 一句话人话
**NetworkPolicy是K8s的"门禁卡"**，控制Pod之间以及Pod与外部之间的网络通信。

### 生活比喻 🔥

**NetworkPolicy = 门禁系统**

```
┌─────────────────────────────────────────────────────────┐
│                   NetworkPolicy                         │
│                                                         │
│   就像写字楼的门禁：                                      │
│                                                         │
│   🏢 大楼                                              │
│   ┌─────────────────────────────────────────┐           │
│   │                                         │           │
│   │  📦 前台区域 (公网可访问)                 │           │
│   │      ↓ 允许外部访问                       │           │
│   │                                         │           │
│   │  📦 工作区域 (需要门禁卡)                  │           │
│   │      ↓ 只有前台才能进入                    │           │
│   │                                         │           │
│   │  📦 核心区域 (需要高级权限)                │           │
│   │      ↓ 只有工作区特定人员才能进入           │           │
│   │                                         │           │
│   └─────────────────────────────────────────┘           │
│                                                         │
│   门禁规则（NetworkPolicy）：                            │
│   • 只有授权的人才能进入                                    │
│   • 每个区域有不同的权限要求                               │
│   • 可以设置黑白名单                                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### NetworkPolicy的基本概念

```yaml
# NetworkPolicy的工作方式
networkPolicy:
  # 1. 选择要控制的Pod（podSelector）
  podSelector:
    matchLabels:
      app: backend
  
  # 2. 设置入站规则（ingress）- 谁可以访问这些Pod
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    - namespaceSelector:
        matchLabels:
          name: production
    ports:
    - protocol: TCP
      port: 8080
  
  # 3. 设置出站规则（egress）- 这些Pod可以访问谁
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 3306
```

### 常见的网络隔离策略

```yaml
# 场景1：只允许前端访问后端
# 后端NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
  namespace: default
spec:
  # 目标Pod
  podSelector:
    matchLabels:
      app: backend
      tier: backend
  
  # 入站规则
  ingress:
  # 允许来自前端Pod的流量
  - from:
    - podSelector:
        matchLabels:
          app: frontend
          tier: frontend
    ports:
    - protocol: TCP
      port: 8080
  
  # 出站规则
  egress:
  # 允许访问数据库
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 3306

---
# 场景2：禁止所有入站流量（完全隔离）
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-policy
  namespace: production
spec:
  podSelector: {}  # 空选择器表示所有Pod
  policyTypes:
  - Ingress
  ingress: []  # 空数组表示禁止所有入站流量

---
# 场景3：只允许同命名空间的Pod访问
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-same-namespace
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: internal-service
  ingress:
  # 只允许同一命名空间的Pod
  - from:
    - podSelector: {}  # 空选择器表示同一命名空间的所有Pod
    ports:
    - protocol: TCP
      port: 8080

---
# 场景4：允许特定IP范围访问
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-external-access
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: public-service
  ingress:
  # 允许特定IP段
  - from:
    - ipBlock:
        cidr: 10.0.0.0/8
        except:
        - 10.0.0.0/24
    ports:
    - protocol: TCP
      port: 80
```

### NetworkPolicy与Ingress Controller的关系

```bash
# NetworkPolicy需要网络插件支持
# 支持NetworkPolicy的CNI插件：
# - Calico（推荐）
# - Cilium
# - Weave Net
# - OVN-Kubernetes

# 不支持NetworkPolicy的CNI插件：
# - Flannel（默认不支持）
# - Canal（项目已停止）

# 检查网络插件是否支持NetworkPolicy
kubectl get pods -n kube-system
# 查看CNI插件的Pod日志
kubectl logs -n kube-system <cni-pod-name>
```

**⚠️ 小白易懵点**

> **NetworkPolicy是"白名单"策略**
> 
> 如果为一个Pod创建了NetworkPolicy，那么**只有**明确允许的流量才能通过。
> 
> 如果Pod没有任何NetworkPolicy，则**允许所有流量**。
> 
> 建议：为所有Pod创建默认拒绝策略，然后只允许必要的流量。

**💡 一句话总结**

> NetworkPolicy是K8s的网络防火墙，控制Pod的入站和出站流量。配合支持NetworkPolicy的CNI插件（如Calico）使用。

---

## 4.4 CoreDNS - 服务名解析

### 一句话人话
**CoreDNS是K8s集群的"电话本"**，负责将Service名称解析为IP地址。

### 生活比喻 🔥

**CoreDNS = 114查号台**

```
┌─────────────────────────────────────────────────────────┐
│                     CoreDNS                             │
│                                                         │
│   就像114电话查号台：                                    │
│                                                         │
│   用户："帮我查一下'我的应用'公司的电话"                  │
│       ↓                                                 │
│   CoreDNS查表                                           │
│       ↓                                                 │
│   返回：10.96.0.100（Service的ClusterIP）               │
│       ↓                                                 │
│   用户："好的，帮我转接"                                  │
│                                                         │
│   DNS查询格式：                                          │
│   my-app                # 短名称                        │
│   my-app.default        # 带命名空间                    │
│   my-app.default.svc    # 带服务类型                   │
│   my-app.default.svc.cluster.local  # 完整名称        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### CoreDNS的工作原理

```
┌─────────────────────────────────────────────────────────────────┐
│                       DNS查询流程                                │
│                                                                 │
│   Pod内部                                                         │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                                                         │   │
│   │   应用发起DNS查询                                         │   │
│   │   curl http://my-app.default.svc.cluster.local/api      │   │
│   │          ↓                                               │   │
│   │   读取 /etc/resolv.conf                                  │   │
│   │   nameserver 10.96.0.2                                   │   │
│   │   search default.svc.cluster.local svc.cluster.local ... │   │
│   │          ↓                                               │   │
│   │   查询 CoreDNS (10.96.0.2)                               │   │
│   │          ↓                                               │   │
│   │   CoreDNS查找                                            │   │
│   │   my-app.default.svc.cluster.local → 10.96.0.100       │   │
│   │          ↓                                               │   │
│   │   返回 IP 地址                                            │   │
│   │                                                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### DNS配置

```bash
# Pod内部的DNS配置
kubectl exec -it my-app-pod -- cat /etc/resolv.conf

# 输出示例：
# nameserver 10.96.0.2        # CoreDNS Service IP
# search default.svc.cluster.local svc.cluster.local cluster.local
# options ndots:5

# ndots配置说明：
# ndots:5 表示如果查询的域名少于5个点，会自动添加搜索后缀
# 例如：查询 "mysql" 会变成 "mysql.default.svc.cluster.local"
```

### DNS查询示例

```bash
# 在Pod内执行DNS查询
kubectl exec -it my-app-pod -- nslookup kubernetes

# 输出：
# Name:      kubernetes
# Address:   10.96.0.1    # Kubernetes Service IP

kubectl exec -it my-app-pod -- nslookup my-app.default.svc.cluster.local

# 输出：
# Name:      my-app.default.svc.cluster.local
# Address:   10.96.0.100  # my-app Service IP
```

### Headless Service的DNS

```yaml
# Headless Service返回Pod的真实IP（不是ClusterIP）
apiVersion: v1
kind: Service
metadata:
  name: mysql-headless
spec:
  clusterIP: None  # 关键！
  selector:
    app: mysql
  ports:
  - port: 3306

# DNS查询会返回Pod的IP列表
# mysql-headless.default.svc.cluster.local
#   → 10.244.1.10 (mysql-0)
#   → 10.244.2.15 (mysql-1)
#   → 10.244.1.20 (mysql-2)

# StatefulSet的每个Pod都有固定DNS
# mysql-0.mysql-headless.default.svc.cluster.local → 10.244.1.10
# mysql-1.mysql-headless.default.svc.cluster.local → 10.244.2.15
# mysql-2.mysql-headless.default.svc.cluster.local → 10.244.1.20
```

### DNS优化：减少不必要的DNS查询

```yaml
# 问题：应用频繁发起短连接，产生大量DNS查询
# 解决：使用连接池或HTTP/2

# 配置Pod使用更高效的DNS设置
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  dnsPolicy: ClusterFirst
  dnsConfig:
    nameservers:
    - 10.96.0.2
    searches:
    - default.svc.cluster.local
    - svc.cluster.local
    - cluster.local
    options:
    - name: ndots
      value: "2"  # 减少到2，减少搜索后缀尝试
    - name: timeout
      value: "2"
    - name: attempts
      value: "2"
```

**💡 一句话总结**

> CoreDNS是K8s内置的DNS服务器，将Service名称解析为ClusterIP。理解DNS查询格式和Headless Service的DNS特性对于服务间通信很重要。

---

## 4.5 本章实战：完整的微服务网络架构

### 架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         微服务网络架构                                  │
│                                                                         │
│  外部用户                                                                 │
│      │                                                                    │
│      ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                    Ingress (Nginx Controller)                      │ │
│  │  api.example.com  → /api/*  → api-service                         │ │
│  │  web.example.com  → /*     → web-service                          │ │
│  │  TLS终止                                                             │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                    │                                      │
│              ┌─────────────────────┼─────────────────────┐               │
│              ▼                     ▼                     ▼               │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐       │
│  │   Web Service   │   │   API Service   │   │  Admin Service  │       │
│  │   (ClusterIP)   │   │   (ClusterIP)   │   │   (ClusterIP)   │       │
│  └────────┬────────┘   └────────┬────────┘   └────────┬────────┘       │
│           │                     │                     │                 │
│           │    ┌────────────────┘                     │                 │
│           │    │                                      │                 │
│           ▼    ▼                                      ▼                 │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐       │
│  │  Redis Service  │   │  MySQL Service  │   │  Auth Service  │       │
│  │   (ClusterIP)   │   │   (Headless)    │   │   (ClusterIP)   │       │
│  └────────┬────────┘   └────────┬────────┘   └─────────────────┘       │
│           │                     │                                       │
│           ▼                     ▼                                       │
│  ┌─────────────────┐   ┌─────────────────┐                             │
│  │ Redis StatefulSet│   │ MySQL StatefulSet│                            │
│  │  redis-0,1,2    │   │  mysql-0,1,2     │                            │
│  └─────────────────┘   └─────────────────┘                             │
│                                                                         │
│  NetworkPolicy:                                                          │
│  • Web → API (允许)                                                     │
│  • API → MySQL (允许)                                                   │
│  • API → Redis (允许)                                                   │
│  • 其他流量 (禁止)                                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 完整YAML配置

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# ============================================
# 微服务网络架构完整配置
# ============================================

# ============ Namespace ============
apiVersion: v1
kind: Namespace
metadata:
  name: microservices
  labels:
    environment: production

---
# ============ Services ============
# Web前端Service
apiVersion: v1
kind: Service
metadata:
  name: web-service
  namespace: microservices
spec:
  type: ClusterIP
  selector:
    app: web
  ports:
  - name: http
    port: 80
    targetPort: 80

---
# API后端Service
apiVersion: v1
kind: Service
metadata:
  name: api-service
  namespace: microservices
spec:
  type: ClusterIP
  selector:
    app: api
  ports:
  - name: http
    port: 8080
    targetPort: 8080

---
# Redis Headless Service
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: microservices
spec:
  type: ClusterIP
  selector:
    app: redis
  ports:
  - name: redis
    port: 6379

---
# MySQL Headless Service (StatefulSet需要)
apiVersion: v1
kind: Service
metadata:
  name: mysql-service
  namespace: microservices
spec:
  type: ClusterIP
  clusterIP: None  # Headless
  selector:
    app: mysql
  ports:
  - name: mysql
    port: 3306

---
# MySQL读写Service
apiVersion: v1
kind: Service
metadata:
  name: mysql-readwrite
  namespace: microservices
spec:
  type: ClusterIP
  selector:
    app: mysql
  ports:
  - name: mysql
    port: 3306

---
# Admin后台Service
apiVersion: v1
kind: Service
metadata:
  name: admin-service
  namespace: microservices
spec:
  type: ClusterIP
  selector:
    app: admin
  ports:
  - name: http
    port: 80
    targetPort: 80

---
# ============ Ingress ============
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: microservices-ingress
  namespace: microservices
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.example.com
    - web.example.com
    - admin.example.com
    secretName: microservices-tls
  rules:
  # Web前端
  - host: web.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
  
  # API后端
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
  
  # Admin后台
  - host: admin.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: admin-service
            port:
              number: 80

---
# ============ Deployments ============
# Web前端
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
  namespace: microservices
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi
        env:
        - name: API_ENDPOINT
          value: "http://api-service:8080"

---
# API后端
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-deployment
  namespace: microservices
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: myapp/api:v1.0.0
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 200m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        env:
        - name: DB_HOST
          value: "mysql-service"
        - name: DB_PORT
          value: "3306"
        - name: REDIS_HOST
          value: "redis-service"
        - name: REDIS_PORT
          value: "6379"

---
# Admin后台
apiVersion: apps/v1
kind: Deployment
metadata:
  name: admin-deployment
  namespace: microservices
spec:
  replicas: 2
  selector:
    matchLabels:
      app: admin
  template:
    metadata:
      labels:
        app: admin
    spec:
      containers:
      - name: admin
        image: myapp/admin:v1.0.0
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi

---
# ============ Redis StatefulSet ============
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis
  namespace: microservices
spec:
  serviceName: redis-service
  replicas: 3
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
  volumeClaimTemplates:
  - metadata:
      name: redis-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 5Gi

---
# ============ MySQL StatefulSet ============
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
  namespace: microservices
spec:
  serviceName: mysql-service
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1000m
            memory: 2Gi
  volumeClaimTemplates:
  - metadata:
      name: mysql-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 20Gi

---
# ============ NetworkPolicies ============
# 默认拒绝所有入站流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: microservices
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress

---
# 允许Ingress Controller访问
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress
  namespace: microservices
spec:
  podSelector:
    matchLabels:
      app: web
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: ingress-nginx
    ports:
    - protocol: TCP
      port: 80
  policyTypes:
  - Ingress

---
# 允许Web访问API
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-web-to-api
  namespace: microservices
spec:
  podSelector:
    matchLabels:
      app: api
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: web
    ports:
    - protocol: TCP
      port: 8080
  policyTypes:
  - Ingress

---
# 允许API访问MySQL和Redis
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-to-db
  namespace: microservices
spec:
  podSelector:
    matchLabels:
      app: mysql
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api
    ports:
    - protocol: TCP
      port: 3306
  policyTypes:
  - Ingress

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-to-redis
  namespace: microservices
spec:
  podSelector:
    matchLabels:
      app: redis
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api
    ports:
    - protocol: TCP
      port: 6379
  policyTypes:
  - Ingress

---
# 允许DNS查询
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: microservices
spec:
  podSelector: {}
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
  policyTypes:
  - Egress
```

### 测试网络连通性

```bash
# 1. 部署所有资源
kubectl apply -f microservices.yaml

# 2. 检查服务状态
kubectl get svc -n microservices

# 3. 测试DNS解析
kubectl run -it --rm dns-test --image=busybox:1.36 --restart=Never -- nslookup api-service

# 4. 测试服务间通信
kubectl run -it --rm curl-test --image=curlimages/curl --restart=Never -- \
  curl -v http://api-service:8080/health

# 5. 测试Ingress
curl -v https://api.example.com/health

# 6. 检查NetworkPolicy效果
# 创建临时Pod测试被拒绝的流量
kubectl run -it --rm blocked-test --image=busybox:1.36 --restart=Never -- \
  sh -c "wget -O- http://web-service:80"
# 应该会失败，因为没有允许访问web-service的规则
```

---

## 第四篇总结

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### 网络核心概念速查

| 概念 | 一句话解释 | 关键词 |
|------|------------|--------|
| **Service** | Pod的统一入口 | ClusterIP、NodePort、LoadBalancer |
| **Ingress** | HTTP/HTTPS路由 | 域名、路径、TLS |
| **NetworkPolicy** | 网络防火墙 | 入口、出口、隔离 |
| **CoreDNS** | 服务名解析 | DNS查询、Headless |

### 访问链路

```
外部访问（用户）
    ↓
Ingress（域名+路径路由）
    ↓
Service（负载均衡）
    ↓
Pod（最终处理）
```

### 下一章预告

在下一章《配置与存储》中，我们将学习：
- ConfigMap非敏感配置
- Secret敏感配置
- Volume存储卷
- PV/PVC持久存储
- StorageClass动态供给

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

**💡 一句话总结**

> K8s网络核心：Service提供负载均衡，Ingress提供七层路由，NetworkPolicy控制网络访问，CoreDNS提供名称解析。

---

*感谢学习第四篇！有问题欢迎随时提问。*

# 第五篇：配置与存储

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

## 前言：让应用配置和存储更灵活

想象一下你搬家到新房子：

- **配置（ConfigMap）**：墙上的公告栏贴着的公告（欢迎语、物业通知等）
- **敏感配置（Secret）**：保险柜里存放的贵重物品（房产证、存折等）
- **存储（Volume）**：你的衣柜、书架等收纳空间

**K8s的配置与存储机制，让你的应用可以灵活配置、安全存储。**

---

## 5.1 ConfigMap - 非敏感配置

### 一句话人话
**ConfigMap是K8s的"公告栏"**，用来存储非敏感的配置信息，如配置文件、环境变量、命令行参数等。

### 生活比喻 🔥

**ConfigMap = 办公室公告栏**

```
┌─────────────────────────────────────────────────────────┐
│                     ConfigMap                            │
│                                                         │
│   就像办公室的公告栏：                                    │
│                                                         │
│   ┌─────────────────────────────────────────┐           │
│   │  📋 公告栏 (ConfigMap)                  │           │
│   │                                          │           │
│   │  📄 欢迎语：欢迎新同事                   │           │
│   │  📄 工作时间：9:00-18:00                │           │
│   │  📄 WiFi密码：Welcome123（开玩笑）       │           │
│   │  📄 会议室规则：请保持安静               │           │
│   │                                          │           │
│   └─────────────────────────────────────────┘           │
│                                                         │
│   特点：                                                 │
│   • 公开透明，任何人都能看到                               │
│   • 公告内容可以更新                                      │
│   • 需要保密的不要放这里！                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### ConfigMap的创建方式

```bash
# 方式1：从字面量创建
kubectl create configmap app-config \
  --from-literal=APP_ENV=production \
  --from-literal=LOG_LEVEL=info

# 方式2：从文件创建
kubectl create configmap nginx-config \
  --from-file=nginx.conf

# 方式3：从目录创建（目录下所有文件都会变成ConfigMap条目）
kubectl create configmap app-config \
  --from-file=./config/

# 方式4：从env文件创建
kubectl create configmap app-config \
  --from-env-file=./config/.env
```

### ConfigMap的YAML

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# 方式1：键值对形式
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: default
data:
  # 键值对（值必须是字符串）
  APP_ENV: "production"
  LOG_LEVEL: "info"
  API_URL: "https://api.example.com"
  DATABASE_NAME: "myapp"
  
---
# 方式2：配置文件形式（使用dataLiteral或binaryData）
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
  namespace: default
data:
  nginx.conf: |
    server {
        listen 80;
        server_name localhost;
        
        location / {
            root /usr/share/nginx/html;
            index index.html;
        }
        
        location /api {
            proxy_pass http://api-service:8080;
        }
    }
  
  default.conf: |
    server {
        listen 80 default_server;
        server_name _;
        return 404;
    }
```

### 在Pod中使用ConfigMap

**1. 作为环境变量**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
  - name: my-app
    image: my-app:1.0
    env:
    # 方式1：直接引用ConfigMap中的键
    - name: APP_ENV
      valueFrom:
        configMapKeyRef:
          name: app-config      # ConfigMap名称
          key: APP_ENV         # ConfigMap中的键
          optional: false      # 可选：true表示ConfigMap不存在时不报错
    
    - name: LOG_LEVEL
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: LOG_LEVEL
```

**2. 引用所有键值对为环境变量**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
  - name: my-app
    image: my-app:1.0
    envFrom:
    # 所有ConfigMap中的键值对都会变成环境变量
    - configMapRef:
        name: app-config
        optional: false
```

**3. 作为命令行参数**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
  - name: my-app
    image: my-app:1.0
    env:
    - name: API_URL
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: API_URL
    
    command: ["/app/start.sh"]
    args:
    - "--config-path=/config/config.yaml"
    - "--log-level=$(LOG_LEVEL)"  # 引用上面定义的环境变量
```

**4. 挂载为文件**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
  - name: my-app
    image: my-app:1.0
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
      readOnly: true
  
  volumes:
  - name: config-volume
    configMap:
      name: app-config
      # 可选：只挂载指定的键
      items:
      - key: nginx.conf
        path: nginx.conf
      - key: default.conf
        path: default.conf
```

**5. 挂载为文件（完整配置）**

```yaml
# 创建ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: spring-config
data:
  application.yml: |
    spring:
      application:
        name: my-app
      datasource:
        url: jdbc:mysql://mysql:3306/myapp
        username: appuser
        password: ${DB_PASSWORD}
      redis:
        host: redis
        port: 6379
    
    server:
      port: 8080
    
    logging:
      level: ${LOG_LEVEL:info}

---
# Pod使用
apiVersion: v1
kind: Pod
metadata:
  name: spring-app
spec:
  containers:
  - name: spring-app
    image: myapp/springboot:1.0
    volumeMounts:
    - name: spring-config
      mountPath: /app/config
      readOnly: true
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
  volumes:
  - name: spring-config
    configMap:
      name: spring-config
```

### ConfigMap的更新

```bash
# 更新ConfigMap
kubectl create configmap app-config --from-literal=APP_ENV=production -o yaml --dry-run=client | kubectl apply -f -

# 或者直接编辑
kubectl edit configmap app-config

# 查看ConfigMap
kubectl get configmap app-config -o yaml

# 验证更新（Pod内的配置会自动更新，挂载的文件会热更新）
# 注意：通过环境变量引用的不会自动更新，需要重启Pod
kubectl exec my-app-pod -- cat /etc/config/APP_ENV
```

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

**⚠️ 小白易懵点**

> **ConfigMap更新的两种方式**
> 
> 1. **文件挂载**：挂载的文件会自动更新（K8s 1.19+），但有短暂延迟
> 2. **环境变量**：环境变量在Pod创建时固定，ConfigMap更新后需要重启Pod才能生效
> 
> 如果需要配置热更新，使用文件挂载方式；如果配置不经常变化，使用环境变量更简单。

**💡 一句话总结**

> ConfigMap用于存储非敏感配置，可以作为环境变量或挂载为文件。适合配置文件、环境变量等场景。

---

## 5.2 Secret - 敏感配置

### 一句话人话
**Secret是K8s的"保险柜"**，用于存储敏感信息，如密码、密钥、证书等。

### 生活比喻 🔥

**Secret = 保险柜**

```
┌─────────────────────────────────────────────────────────┐
│                      Secret                             │
│                                                         │
│   就像公司的保险柜：                                     │
│                                                         │
│   ┌─────────────────────────────────────────┐           │
│   │  🔐 保险柜 (Secret)                     │           │
│   │                                          │           │
│   │  🔑 房门钥匙                             │           │
│   │  💳 银行卡                               │           │
│   │  📄 重要合同                             │           │
│   │  🔑 API密钥                             │           │
│   │  📄 TLS证书                             │           │
│   │                                          │           │
│   └─────────────────────────────────────────┘           │
│                                                         │
│   特点：                                                 │
│   • 需要钥匙才能打开                                     │
│   • 内容经过Base64编码（但不是加密！）                    │
│   • 可以配合加密插件实现真正加密                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Secret的类型

| 类型 | 说明 | 使用场景 |
|------|------|----------|
| **Opaque** | 通用类型，默认 | 密码、密钥 |
| **kubernetes.io/dockerconfigjson** | Docker仓库认证 | 私有镜像拉取 |
| **kubernetes.io/tls** | TLS证书 | HTTPS |
| **kubernetes.io/service-account-token** | ServiceAccount令牌 | Pod认证 |

### Secret的YAML

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# 方式1：Opaque类型（通用）
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
  namespace: default
type: Opaque
data:
  # Base64编码的值（不是加密！）
  # echo -n "password123" | base64
  username: YXBwdXNlcg==          # base64编码后的appuser
  password: cGFzc3dvcmQxMjM=      # base64编码后的password123
  # 或者使用stringData（K8s会自动转成Base64）
stringData:
  API_KEY: "sk-xxxxx-xxxxx"
  TLS_CERT: |
    -----BEGIN CERTIFICATE-----
    MIIDXTCCAkWgAwIBAgIJ...
    -----END CERTIFICATE-----
  TLS_KEY: |
    -----BEGIN PRIVATE KEY-----
    MIIEvwIBADANBgkqhkiG9w0B...
    -----END PRIVATE KEY-----

---
# 方式2：TLS类型
apiVersion: v1
kind: Secret
metadata:
  name: tls-secret
  namespace: default
type: kubernetes.io/tls
data:
  # Base64编码的证书和私钥
  tls.crt: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0t...
  tls.key: LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0t...

---
# 方式3：Docker仓库认证
apiVersion: v1
kind: Secret
metadata:
  name: dockerhub-secret
type: kubernetes.io/dockerconfigjson
data:
  # echo -n '{"auths":{"https://index.docker.io/v1/":{"username":"xxx","password":"xxx"}}}' | base64
  .dockerconfigjson: eyJhdXRocyI6eyJodHRwczovL2luZGV4LmRvY2tlci5pby92MS8iOnsidXNlcm5hbWUiOiJ4eHgiLCJwYXNzd29yZCI6Inh4eCJ9fX0=
```

### Base64编解码

```bash
# 编码
echo -n "password123" | base64
# 输出：cGFzc3dvcmQxMjM=

# 解码
echo -n "cGFzc3dvcmQxMjM=" | base64 -d
# 输出：password123

# 注意：Windows PowerShell使用不同命令
# 编码：[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("password123"))
# 解码：[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String("cGFzc3dvcmQxMjM="))
```

### 在Pod中使用Secret

**1. 作为环境变量**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
  - name: my-app
    image: my-app:1.0
    env:
    - name: DB_USERNAME
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: username
    
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
```

**2. 引用所有Secret为环境变量**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
  - name: my-app
    image: my-app:1.0
    envFrom:
    - secretRef:
        name: db-secret
```

**3. 挂载为文件**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
  - name: my-app
    image: my-app:1.0
    volumeMounts:
    - name: tls-certs
      mountPath: /etc/tls
      readOnly: true
    
    - name: api-keys
      mountPath: /etc/keys
      readOnly: true
  
  volumes:
  - name: tls-certs
    secret:
      secretName: tls-secret
      items:
      - key: tls.crt
        path: cert.pem
      - key: tls.key
        path: key.pem
  
  - name: api-keys
    secret:
      secretName: api-keys
```

### 私有镜像仓库认证

```yaml
# 1. 创建Secret
kubectl create secret docker-registry dockerhub-secret \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=your-username \
  --docker-password=your-password \
  --docker-email=your-email@example.com

# 2. 在Pod中使用
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  # 引用镜像拉取Secret
  imagePullSecrets:
  - name: dockerhub-secret
  
  containers:
  - name: my-app
    image: your-registry.com/your-image:tag
```

### Secret的安全建议

```bash
# ⚠️ Secret的注意事项

# 1. Secret的Base64不是加密！
# 任何能访问API Server的人都能看到Secret内容
kubectl get secret db-secret -o yaml

# 2. 启用加密来保护Secret
# 在API Server配置中启用EncryptionConfiguration

# 3. 启用RBAC控制Secret访问
kubectl auth can-i get secrets --namespace=default

# 4. 定期轮换Secret
kubectl create secret generic db-secret --from-literal=password=newpassword -o yaml --dry-run=client | kubectl replace -f -

# 5. 不要把Secret写入代码或配置文件
# 错误：secret: password123
# 正确：使用kubectl create secret生成
```

**⚠️ 小白易懵点**

> **Secret的Base64编码 vs 加密**
> 
> Secret的data字段只是Base64编码，**不是加密**！
> 
> ```bash
> # 任何人可以轻松解码
> kubectl get secret my-secret -o jsonpath='{.data.password}' | base64 -d
> ```
> 
> 要真正保护Secret，需要：
> 1. 启用K8s的加密配置（EncryptionConfiguration）
> 2. 使用Vault等专门的密钥管理工具
> 3. 启用RBAC限制访问

**💡 一句话总结**

> Secret用于存储敏感配置，支持Base64编码和环境变量/文件挂载方式使用。建议启用加密配置和RBAC保护Secret。

---

## 5.3 Volume - 存储卷

### 一句话人话
**Volume是Pod的"附加存储空间"**，可以让容器持久化数据或在不同容器间共享数据。

### 生活比喻 🔥

**Volume = 随身行李箱**

```
┌─────────────────────────────────────────────────────────┐
│                      Volume                             │
│                                                         │
│   就像登机箱：                                           │
│                                                         │
│   ┌─────────────────────────────────────────┐           │
│   │  🧳 登机箱 (Volume)                     │           │
│   │                                          │           │
│   │  🏠 临时物品（emptyDir）                  │           │
│   │     每次登机箱清空                        │           │
│   │                                          │           │
│   │  🏠 固定物品（hostPath）                  │           │
│   │     固定放在某个位置                      │           │
│   │                                          │           │
│   │  🏠 共享仓库（NFS/云存储）                │           │
│   │     多个机场共用一个仓库                   │           │
│   │                                          │           │
│   └─────────────────────────────────────────┘           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Volume的类型

| 类型 | 说明 | 生命周期 | 使用场景 |
|------|------|----------|----------|
| **emptyDir** | 临时空目录 | 与Pod同生命周期 | 临时存储、缓存 |
| **hostPath** | 宿主机目录 | 独立于Pod | 节点级存储 |
| **nfs** | NFS网络文件系统 | 独立于Pod | 共享存储 |
| **configMap/secret** | ConfigMap/Secret | 独立于Pod | 配置注入 |
| **persistentVolumeClaim** | PVC持久卷 | 独立于Pod | 持久化存储 |

### emptyDir - 临时存储

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app-with-cache
spec:
  containers:
  - name: my-app
    image: my-app:1.0
    volumeMounts:
    - name: cache-volume
      mountPath: /tmp/cache
  
  - name: log-collector
    image: fluent/fluent-bit:latest
    volumeMounts:
    - name: cache-volume
      mountPath: /var/log
  
  volumes:
  - name: cache-volume
    emptyDir:
      sizeLimit: "100Mi"           # 可选：限制大小
      medium: "Memory"              # 可选：存储到内存（tmpfs）
```

### hostPath - 节点存储

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app-with-hostpath
spec:
  containers:
  - name: my-app
    image: my-app:1.0
    volumeMounts:
    - name: data
      mountPath: /data
  
  volumes:
  - name: data
    hostPath:
      path: /var/local/data        # 宿主机上的目录
      type: DirectoryOrCreate      # 目录不存在时创建
```

### NFS - 网络共享存储

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app-with-nfs
spec:
  containers:
  - name: my-app
    image: my-app:1.0
    volumeMounts:
    - name: nfs-storage
      mountPath: /shared-data
  
  volumes:
  - name: nfs-storage
    nfs:
      server: 192.168.1.100        # NFS服务器IP
      path: /exports/shared-data   # 共享路径
      readOnly: false
```

### Volume在多容器间共享

```yaml
# 示例：Nginx + 日志收集器共享Volume
apiVersion: v1
kind: Pod
metadata:
  name: shared-volume-pod
spec:
  containers:
  # 主容器：Nginx
  - name: nginx
    image: nginx:alpine
    ports:
    - containerPort: 80
    volumeMounts:
    - name: html-volume
      mountPath: /usr/share/nginx/html
    - name: log-volume
      mountPath: /var/log/nginx
  
  # Sidecar：日志收集器
  - name: log-collector
    image: busybox:latest
    command:
    - /bin/sh
    - -c
    - |
      while true; do
        tail -f /var/log/nginx/access.log
        sleep 1
      done
    volumeMounts:
    - name: log-volume
      mountPath: /var/log/nginx
    - name: shared-log
      mountPath: /collected-logs
  
  volumes:
  # Nginx的HTML文件
  - name: html-volume
    configMap:
      name: nginx-html
  
  # Nginx的日志
  - name: log-volume
    emptyDir: {}
  
  # 收集的日志（两个容器共享）
  - name: shared-log
    emptyDir: {}
```

**💡 一句话总结**

> Volume是Pod的存储空间，emptyDir用于临时存储，hostPath用于节点级存储，NFS用于共享存储。

---

## 5.4 PV与PVC - 持久存储

### 一句话人话
**PV是仓库的"车位"，PVC是"停车证"**，PVC向PV申请存储空间。

### 生活比喻 🔥

**PV/PVC = 停车场系统**

```
┌─────────────────────────────────────────────────────────┐
│                  PV (PersistentVolume)                  │
│                                                         │
│   就像停车场的车位：                                      │
│                                                         │
│   ┌─────────────────────────────────────────┐           │
│   │  🅿️ 停车场 (PV)                         │           │
│   │                                          │           │
│   │   车位A ────── 大车位 (20平米)            │           │
│   │   车位B ────── 中车位 (15平米)            │           │
│   │   车位C ────── 小车位 (10平米)            │           │
│   │                                          │           │
│   │   特点：                                   │           │
│   │   • 车位是固定的                           │           │
│   │   • 可以被不同的车（Pod）使用               │           │
│   │   • 可以设置访问权限                        │           │
│   └─────────────────────────────────────────┘           │
│                                                         │
│                  PVC (PersistentVolumeClaim)             │
│                                                         │
│   就像停车证申请：                                       │
│                                                         │
│   司机A：我要一个中车位           ────▶  分配车位B      │
│   司机B：我要一个大车位           ────▶  分配车位A      │
│   司机C：我要一个车位（随便）     ────▶  分配车位C      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### PV的YAML

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-mysql
  labels:
    type: local
spec:
  # 存储容量
  capacity:
    storage: 50Gi
  
  # 访问模式
  accessModes:
  - ReadWriteOnce      # 只允许单节点读写
  # - ReadOnlyMany     # 允许多节点只读
  # - ReadWriteMany    # 允许多节点读写
  
  # 回收策略
  # Retain：保留数据，需要手动清理
  # Delete：删除卷和底层存储
  # Recycle：删除数据但保留卷（已废弃）
  persistentVolumeReclaimPolicy: Retain
  
  # 存储类型
  storageClassName: standard
  
  # 本地存储配置
  local:
    path: /mnt/disks/ssd1
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - node-1
          - node-2

---
# NFS存储的PV
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-nfs
spec:
  capacity:
    storage: 100Gi
  
  accessModes:
  - ReadWriteMany
  
  storageClassName: nfs
  
  persistentVolumeReclaimPolicy: Retain
  
  nfs:
    server: 192.168.1.100
    path: /exports/data
```

### PVC的YAML

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-mysql
spec:
  # 请求的访问模式
  accessModes:
  - ReadWriteOnce
  
  # 请求的存储容量
  resources:
    requests:
      storage: 20Gi
  
  # 指定存储类（可选，不指定会使用默认存储类）
  storageClassName: standard
  
  # 选择器（可选，精确匹配PV）
  selector:
    matchLabels:
      type: local

---
# StatefulSet使用PVC模板
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
  
  # PVC模板
  volumeClaimTemplates:
  - metadata:
      name: mysql-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "standard"
      resources:
        requests:
          storage: 10Gi
```

### PV与PVC的生命周期

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PV/PVC 生命周期                                      │
│                                                                         │
│  ┌─────────────┐                                                      │
│  │  Available  │ ← PV创建后可用                                         │
│  └──────┬──────┘                                                      │
│         │                                                               │
│         │ PVC申请                                                       │
│         ▼                                                               │
│  ┌─────────────┐                                                      │
│  │   Pending   │ ← PVC等待绑定                                          │
│  └──────┬──────┘                                                      │
│         │                                                               │
│         │ 找到匹配的PV                                                  │
│         ▼                                                               │
│  ┌─────────────┐                                                      │
│  │   Bound     │ ← PVC绑定到PV                                          │
│  └──────┬──────┘                                                      │
│         │                                                               │
│         │ Pod使用PVC                                                    │
│         ▼                                                               │
│  ┌─────────────┐                                                      │
│  │   In Use    │ ← Pod正在使用                                          │
│  └──────┬──────┘                                                      │
│         │                                                               │
│         │ Pod删除                                                       │
│         ▼                                                               │
│  ┌─────────────────────────────────────────┐                            │
│  │           回收策略                        │                            │
│  │                                          │                            │
│  │   Retain → 保持数据，手动清理            │                            │
│  │   Delete → 删除存储资源                  │                            │
│  │   Recycle → 删除数据（已废弃）           │                            │
│  │                                          │                            │
│  └─────────────────────────────────────────┘                            │
│         │                                                               │
│         ▼                                                               │
│  ┌─────────────┐                                                      │
│  │  Available  │ ← 再次可用                                             │
│  └─────────────┘                                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 查看PV和PVC状态

```bash
# 查看所有PV
kubectl get pv

# 查看所有PVC
kubectl get pvc

# 查看PVC详情
kubectl describe pvc pvc-mysql

# 查看PV详情
kubectl describe pv pv-mysql

# 示例输出：
# NAME      CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM
# pv-mysql   50Gi       RWO            Retain           Bound    default/pvc-mysql
```

**💡 一句话总结**

> PV是集群级别的存储资源，PVC是Pod对存储的请求。PV/PVC分离了存储的供应和使用，让存储管理更灵活。

---

## 5.5 StorageClass - 动态供给

### 一句话人话
**StorageClass是"自助仓储系统"**，根据PVC的请求自动创建PV，不需要手动预先创建。

### 生活比喻 🔥

**StorageClass = 自助仓储系统**

```
┌─────────────────────────────────────────────────────────┐
│                  StorageClass                            │
│                                                         │
│   就像自助仓储服务：                                      │
│                                                         │
│   客户A：我需要一个10平米的小仓库         ────▶ 自动分配小仓库 │
│   客户B：我需要一个20平米的中仓库         ────▶ 自动分配中仓库 │
│   客户C：我需要一个30平米的大仓库         ────▶ 自动分配大仓库 │
│                                                         │
│   特点：                                                 │
│   • 不用提前预约车位                                      │
│   • 按需分配                                              │
│   • 可以指定存储类型（SSD、普通盘）                        │
│   • 自动清理过期存储                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### StorageClass的YAML

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# 默认StorageClass（没有指定storageClassName时使用）
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: kubernetes.io/gce-pd  # GCP的PD存储
parameters:
  type: pd-standard
  replication-type: regional-pd
reclaimPolicy: Delete
allowVolumeExpansion: true
mountOptions:
- debug
volumeBindingMode: WaitForFirstConsumer

---
# 云厂商示例：阿里云云盘
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: alicloud-disk-efficiency
provisioner: diskplugin.csi.alibabacloud.com
parameters:
  type: cloud_essd
  regionId: cn-hangzhou
  zoneId: cn-hangzhou-b
reclaimPolicy: Retain
allowVolumeExpansion: true

---
# 云厂商示例：AWS EBS
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: aws-ebs-gp3
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  fsType: ext4
  encrypted: "true"
reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer

---
# NFS存储类
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-storage
provisioner: nfs.csi.k8s.io
parameters:
  server: 192.168.1.100
  share: /exports/default
reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: Immediate

---
# Local Storage Class
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-storage
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
# WaitForFirstConsumer：延迟绑定，直到Pod调度到节点
```

### 使用StorageClass动态供给

```yaml
# 创建PVC时指定StorageClass
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dynamic-pvc
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: standard  # 指定存储类
  resources:
    requests:
      storage: 20Gi

---
# StatefulSet使用动态存储
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "standard"
      resources:
        requests:
          storage: 10Gi
```

### Volume扩展

```bash
# 1. 启用存储扩展（StorageClass需设置allowVolumeExpansion: true）
kubectl patch storageclass standard -p '{"allowVolumeExpansion": true}'

# 2. 修改PVC大小
kubectl patch pvc data-pvc-mysql-0 -p '{"spec":{"resources":{"requests":{"storage":"30Gi"}}}}'

# 3. 查看扩展状态
kubectl describe pvc data-pvc-mysql-0
```

### 常见的Provisioner

| Provisioner | 存储类型 | 云厂商 |
|-------------|----------|--------|
| kubernetes.io/gce-pd | GCP PD | GCP |
| kubernetes.io/aws-ebs | AWS EBS | AWS |
| kubernetes.io/azure-disk | Azure Disk | Azure |
| diskplugin.csi.alibabacloud.com | 阿里云云盘 | 阿里云 |
| nfs.csi.k8s.io | NFS | 通用 |
| hostpath.csi.k8s.io | HostPath | 本地 |

**⚠️ 小白易懵点**

> **volumeBindingMode 的区别**
> 
> - **Immediate**：PVC创建时立即绑定PV，可能导致Pod调度到没有对应存储的节点
> - **WaitForFirstConsumer**：延迟绑定，等Pod调度到节点后再绑定合适的PV（推荐）
> 
> 推荐使用 `WaitForFirstConsumer`，避免存储和Pod不在同一节点导致的网络延迟。

**💡 一句话总结**

> StorageClass实现了存储的动态供给，根据PVC请求自动创建PV。设置 `volumeBindingMode: WaitForFirstConsumer` 可以优化存储调度。

---

## 5.6 本章实战：完整的配置与存储方案

### 项目需求

部署一个MySQL数据库应用，包含：
- ConfigMap存储配置文件
- Secret存储敏感信息
- PVC使用动态存储
- 完整的挂载和配置

### 完整YAML

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# ============================================
# MySQL数据库完整配置与存储方案
# ============================================

# ============ Namespace ============
apiVersion: v1
kind: Namespace
metadata:
  name: database
  labels:
    environment: production

---
# ============ ConfigMap ============
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-config
  namespace: database
data:
  # MySQL主配置文件
  my.cnf: |
    [mysqld]
    # 基本设置
    user = mysql
    port = 3306
    socket = /var/run/mysqld/mysqld.sock
    pid-file = /var/run/mysqld/mysqld.pid
    
    # 字符集
    character-set-server = utf8mb4
    collation-server = utf8mb4_unicode_ci
    
    # 日志
    log_error = /var/log/mysql/error.log
    slow_query_log = 1
    slow_query_log_file = /var/log/mysql/slow.log
    long_query_time = 2
    
    # 连接数
    max_connections = 500
    max_connect_errors = 100
    
    # 缓冲区
    innodb_buffer_pool_size = 256M
    innodb_log_file_size = 64M
    innodb_flush_log_at_trx_commit = 1
    innodb_flush_method = O_DIRECT
    
    # 性能
    innodb_file_per_table = 1
    innodb_stats_on_metadata = 0
    query_cache_type = 0
    query_cache_size = 0
  
  # 初始化SQL脚本
  init.sql: |
    CREATE DATABASE IF NOT EXISTS myapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    CREATE USER IF NOT EXISTS 'appuser'@'%' IDENTIFIED BY 'placeholder_password';
    GRANT ALL PRIVILEGES ON myapp.* TO 'appuser'@'%';
    FLUSH PRIVILEGES;

---
# ============ Secret ============
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
  namespace: database
type: Opaque
stringData:
  # MySQL root密码
  MYSQL_ROOT_PASSWORD: "RootPassword123!"
  
  # 应用用户密码（会被Kubernetes base64编码）
  MYSQL_PASSWORD: "AppPassword456!"

---
# ============ StorageClass ============
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: mysql-storage
  annotations:
    storageclass.kubernetes.io/is-default-class: "false"
provisioner: kubernetes.io/gce-pd  # 根据实际环境修改
parameters:
  type: pd-ssd
  replication-type: regional-pd
reclaimPolicy: Retain
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer

---
# ============ StatefulSet ============
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
  namespace: database
spec:
  serviceName: mysql-headless
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  
  # Pod模板
  template:
    metadata:
      labels:
        app: mysql
        environment: production
    spec:
      # 初始化容器
      initContainers:
      # 等待其他MySQL节点就绪（如果集群模式）
      - name: init-mysql
        image: mysql:8.0
        command:
        - bash
        - "-c"
        - |
          set -ex
          # 等待数据目录准备就绪
          [[ -d /var/lib/mysql ]] || mkdir -p /var/lib/mysql
          # 检查权限
          chown -R mysql:mysql /var/lib/mysql /var/log/mysql /etc/mysql
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
        - name: mysql-log
          mountPath: /var/log/mysql
      
      # 主容器
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - name: mysql
          containerPort: 3306
        
        # 环境变量
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: MYSQL_ROOT_PASSWORD
        
        - name: MYSQL_DATABASE
          value: "myapp"
        
        - name: MYSQL_USER
          value: "appuser"
        
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: MYSQL_PASSWORD
        
        # 健康检查
        livenessProbe:
          exec:
            command:
            - mysqladmin
            - ping
            - "-h"
            - localhost
            - "-uroot"
            - "-p$MYSQL_ROOT_PASSWORD"
          initialDelaySeconds: 60
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 6
        
        readinessProbe:
          exec:
            command:
            - mysqladmin
            - ping
            - "-h"
            - localhost
            - "-uroot"
            - "-p$MYSQL_ROOT_PASSWORD"
          initialDelaySeconds: 30
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        
        # 启动探针（MySQL启动较慢）
        startupProbe:
          exec:
            command:
            - mysqladmin
            - ping
            - "-h"
            - localhost
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 30
        
        # 资源限制
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        
        # 存储卷挂载
        volumeMounts:
        # 数据目录
        - name: mysql-data
          mountPath: /var/lib/mysql
        # 日志目录
        - name: mysql-log
          mountPath: /var/log/mysql
        # 配置文件
        - name: mysql-config
          mountPath: /etc/mysql/conf.d
          readOnly: true
        # 初始化脚本
        - name: mysql-init
          mountPath: /docker-entrypoint-initdb.d
          readOnly: true
        
        # 生命周期钩子
        lifecycle:
          preStop:
            exec:
              command:
              - bash
              - "-c"
              - |
                echo "Waiting for MySQL to flush buffers..."
                mysqladmin -uroot -p$MYSQL_ROOT_PASSWORD flush-logs
                sleep 5
        
        # 安全上下文
        securityContext:
          runAsUser: 999
          runAsGroup: 999
          fsGroup: 999
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: false
      
      # 容忍（可选，允许在特定节点运行）
      tolerations:
      - key: "database"
        operator: "Exists"
        effect: "NoSchedule"
      
      # 亲和性（可选，优先调度到数据库节点）
      affinity:
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            preference:
              matchExpressions:
              - key: node-role
                operator: In
                values:
                - database
      
      # DNS配置
      dnsPolicy: ClusterFirst
      dnsConfig:
        options:
        - name: ndots
          value: "2"
  
  # PVC模板（动态供给存储）
  volumeClaimTemplates:
  # 数据存储
  - metadata:
      name: mysql-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "mysql-storage"
      resources:
        requests:
          storage: 50Gi
  
  # 日志存储（可选，独立于数据）
  - metadata:
      name: mysql-log
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "mysql-storage"
      resources:
        requests:
          storage: 10Gi

---
# ============ Services ============
# Headless Service（StatefulSet必需）
apiVersion: v1
kind: Service
metadata:
  name: mysql-headless
  namespace: database
  labels:
    app: mysql
spec:
  type: ClusterIP
  clusterIP: None  # 关键！Headless Service
  ports:
  - name: mysql
    port: 3306
    targetPort: 3306
  selector:
    app: mysql

---
# 普通Service（用于应用访问）
apiVersion: v1
kind: Service
metadata:
  name: mysql
  namespace: database
  labels:
    app: mysql
spec:
  type: ClusterIP
  ports:
  - name: mysql
    port: 3306
    targetPort: 3306
    protocol: TCP
  selector:
    app: mysql

---
# ============ Volume（配置文件） ============
# 配置存储卷
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-config
  namespace: database
binaryData:
  my.cnf: |
    W215bXlzcWxd...
data:
  init.sql: |
    CREATE DATABASE IF NOT EXISTS myapp;
---
# 或者直接在StatefulSet中使用
```

### 部署和验证

```bash
# 1. 创建所有资源
kubectl apply -f mysql-complete.yaml

# 2. 查看资源状态
kubectl get all -n database
kubectl get pvc -n database
kubectl get pv

# 3. 查看Pod日志
kubectl logs -n database mysql-0 -f

# 4. 进入MySQL容器
kubectl exec -it -n database mysql-0 -- mysql -uroot -p

# 5. 验证数据持久化
kubectl exec -it -n database mysql-0 -- mysql -uroot -p$MYSQL_ROOT_PASSWORD \
  -e "CREATE TABLE test (id INT PRIMARY KEY, name VARCHAR(50)); INSERT INTO test VALUES (1, 'Hello K8s!');"
kubectl exec -it -n database mysql-0 -- mysql -uroot -p$MYSQL_ROOT_PASSWORD \
  -e "SELECT * FROM myapp.test;"

# 6. 删除Pod测试自愈
kubectl delete pod -n database mysql-0

# 7. 验证数据恢复（Pod会自动重建，数据应该还在）
kubectl exec -it -n database mysql-0 -- mysql -uroot -p$MYSQL_ROOT_PASSWORD \
  -e "SELECT * FROM myapp.test;"

# 8. 查看存储使用
kubectl exec -it -n database mysql-0 -- df -h /var/lib/mysql
```

---

## 第五篇总结

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### 配置与存储核心概念速查

| 概念 | 一句话解释 | 关键词 |
|------|------------|--------|
| **ConfigMap** | 非敏感配置存储 | 环境变量、文件挂载 |
| **Secret** | 敏感配置存储 | Base64编码、加密 |
| **Volume** | Pod临时存储 | emptyDir、hostPath、NFS |
| **PV** | 持久卷 | 存储资源 |
| **PVC** | 持久卷请求 | 存储申请 |
| **StorageClass** | 动态存储供给 | 自动创建PV |

### 配置管理最佳实践

```
敏感信息
    │
    └──▶ Secret（启用加密！）
    │
非敏感配置
    │
    └──▶ ConfigMap
    │
存储需求
    │
    ├── 临时存储 ──▶ emptyDir
    │
    ├── 持久存储 ──▶ PVC + StorageClass
    │
    └── 共享存储 ──▶ NFS + PV/PVC
```

### 下一章预告

恭喜你完成上半部分学习！下半部分（第6-10篇）将涵盖：
- 第六篇：安全机制（RBAC、SecurityContext、NetworkPolicy）
- 第七篇：资源管理（ResourceQuota、LimitRange、HPA）
- 第八篇：日志与监控（EFK、Prometheus、Grafana）
- 第九篇：Helm包管理器
- 第十篇：实战项目

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

**💡 一句话总结**

> K8s配置与存储：ConfigMap存配置，Secret存敏感信息，Volume提供临时存储，PV/PVC提供持久存储，StorageClass实现存储动态供给。

---

## 教程上半部分总结

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### 五篇内容回顾

| 篇目 | 主题 | 核心知识点 |
|------|------|------------|
| **第一篇** | 容器基础 | Docker命令、Dockerfile、Docker Compose、镜像优化 |
| **第二篇** | K8s架构 | Master/Node架构、API Server、Scheduler、Controller Manager |
| **第三篇** | 核心资源对象 | Pod、Deployment、StatefulSet、DaemonSet、Job/CronJob |
| **第四篇** | 服务发现与网络 | Service、Ingress、NetworkPolicy、CoreDNS |
| **第五篇** | 配置与存储 | ConfigMap、Secret、Volume、PV/PVC、StorageClass |

### 学习路线图

```
容器基础 ──▶ K8s架构 ──▶ 核心资源对象 ──▶ 服务发现与网络 ──▶ 配置与存储
    │           │              │                │              │
  Docker     Master/Node    Pod/Dep         Service/Ingress  ConfigMap/PV
  Dockerfile   kubectl      StatefulSet      NetworkPolicy   StorageClass
```

### 下一步学习建议

1. **实践**：在Minikube或Docker Desktop上部署自己的应用
2. **阅读**：K8s官方文档
3. **进阶**：学习下半部分内容（安全、资源管理、监控、Helm）

---

*恭喜你完成了K8s零基础小白教程上半部分的学习！*
*建议收藏本文，经常回顾和实践。*
*有疑问欢迎随时交流！*
# K8s零基础小白教程（下）

![K8s](https://www.coze.cn/s/JqVhDq6lmkg/)

## 教程概述

本教程专为Kubernetes（K8s）零基础小白设计，通过生动的比喻和实际案例，让你从零开始掌握K8s的核心知识。整个教程分为上、下两部分：

- **上半部分（第1-5篇）**：容器基础、K8s架构、核心资源对象、服务发现与网络、配置与存储
- **下半部分（第6-11篇）**：调度与伸缩、安全与权限、Helm包管理、监控与日志、运维排错、实战项目

### 学习路径图

```
容器基础 → K8s架构 → 核心资源对象 → 服务发现与网络 → 配置与存储
    ↓           ↓            ↓              ↓              ↓
 Docker命令  Master/Node   Pod/Deployment  Service/Ingress  ConfigMap/Secret
   Dockerfile   kubectl     StatefulSet     NetworkPolicy    PV/PVC
   Docker Compose             DaemonSet      CoreDNS         StorageClass
    ↓
 调度与伸缩 → 安全与权限 → Helm → 监控与日志 → 运维排错 → 实战
 NodeSelector   RBAC        Chart      Prometheus/Grafana  kubectl    项目
 Affinity       Service     自定义      EFK                常见故障    CI/CD
 HPA/VPA        NetworkPolicy           告警               升级备份    SpringBoot
 Taint/Toleration PodSecurity
```

---

## 目录

6. [第六篇：调度与伸缩](#第六篇调度与伸缩)
7. [第七篇：安全与权限](#第七篇安全与权限)
8. [第八篇：Helm](#第八篇helm)
9. [第九篇：监控与日志](#第九篇监控与日志)
10. [第十篇：运维排错](#第十篇运维排错)
11. [第十一篇：实战](#第十一篇实战)

---

# 第六篇：调度与伸缩

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

## 前言：智能调度的魔法

想象你是一家大型餐厅的老板，有10位服务员（节点）和成百上千的顾客请求（Pod）。谁来负责决定哪位服务员去服务哪张桌子呢？这就是K8s的调度器。

不仅如此，餐厅的高峰期和低谷期差别巨大。午餐时间人满为患，需要增加人手；下午三点门可罗雀，可以安排休息。这就是K8s的自动伸缩。

本篇我们将深入探索K8s如何智能分配Pod到节点，以及如何根据负载自动调整资源。

---

## 6.1 调度策略：Pod该去哪？

### 6.1.1 NodeSelector：硬性要求

### 一句话人话
**NodeSelector**是给Pod加的标签筛选器，强制Pod只能调度到符合标签要求的节点上。

### 生活比喻 🔥
就像**VIP客户的专属服务**：
- 某些高端客户（特殊的Pod）必须由金牌服务员（有特定标签的节点）服务
- 不是金牌服务员就不能接这个单
- 简单粗暴，要么满足，要么就挂起

### 核心概念
NodeSelector是Pod Spec中的一个字段，用于指定Pod必须调度到带有特定标签的节点上。这是最简单、最直接的调度策略。

### 实操步骤

**步骤1：给节点打标签**

```bash
# 查看当前节点
kubectl get nodes

# 给节点打标签
kubectl label nodes node-1 disktype=ssd
kubectl label nodes node-2 disktype=hdd

# 验证标签
kubectl get nodes --show-labels
```

**步骤2：创建使用NodeSelector的Pod**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ssd-pod
  labels:
    app: storage-app
spec:
  # 只能调度到带有disktype=ssd标签的节点
  nodeSelector:
    disktype: ssd
  containers:
  - name: nginx
    image: nginx:1.21
    resources:
      requests:
        memory: "256Mi"
        cpu: "250m"
      limits:
        memory: "512Mi"
        cpu: "500m"
```

**步骤3：应用并验证**

```bash
# 创建Pod
kubectl apply -f ssd-pod.yaml

# 查看Pod调度到哪个节点
kubectl get pods -o wide

# 查看详细信息
kubectl describe pod ssd-pod
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **NodeSelector的局限性**：
> - NodeSelector不支持复杂的逻辑（比如"或"关系）
> - 如果没有节点满足条件，Pod会一直处于Pending状态
> - NodeSelector只做硬性限制，不做软性偏好
>
> **解决方法**：如果需要更复杂的调度策略，应该使用NodeAffinity（节点亲和性）

---

### 6.1.2 NodeAffinity：软硬兼施

### 一句话人话
**NodeAffinity**是更强大的节点选择器，支持复杂的匹配规则和软硬两种要求。

### 生活比喻 🔥
就像**相亲软件的高级筛选**：
- **硬性要求（Required）**：必须在北京，必须工作稳定，如果不满足就直接pass
- **软性偏好（Preferred）**：最好有车，最好会做饭，如果没有也行，但优先匹配有的
- 可以组合多个条件，甚至设置优先级

### 核心概念
NodeAffinity分为两种类型：
1. **requiredDuringSchedulingIgnoredDuringExecution**：硬性要求，必须满足
2. **preferredDuringSchedulingIgnoredDuringExecution**：软性偏好，优先满足

操作符包括：
- `In`：在列表中
- `NotIn`：不在列表中
- `Exists`：标签存在
- `DoesNotExist`：标签不存在
- `Gt`：大于
- `Lt`：小于

### 实操步骤

**场景：希望Pod优先调度到SSD节点，如果没有SSD节点也可以调度到HDD节点**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: affinity-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: affinity-app
  template:
    metadata:
      labels:
        app: affinity-app
    spec:
      affinity:
        # 硬性要求：必须有zone标签
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: zone
                operator: In
                values:
                - east-1
                - east-2
          # 软性偏好：优先选择SSD节点
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            preference:
              matchExpressions:
              - key: disktype
                operator: In
                values:
                - ssd
          - weight: 50
            preference:
              matchExpressions:
              - key: cpu-type
                operator: In
                values:
                - high-performance
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **为什么叫IgnoredDuringExecution？**
> - 这意味着在Pod运行期间，即使节点的标签发生了变化，Pod也不会被驱逐
> - 比如：Pod调度到SSD节点后，节点的disktype标签被改成hdd，Pod不会自动迁移
> - 如果希望标签变化时Pod重新调度，需要结合其他机制（如Descheduler）
>
> **Weight的作用**：preferred规则的权重，范围1-100，权重越高优先级越高

---

### 6.1.3 PodAffinity与PodAntiAffinity：亲疏有别

### 一句话人话
**PodAffinity**让Pod和某些特定的Pod在一起（亲和），**PodAntiAffinity**让Pod远离某些Pod（反亲和）。

### 生活比喻 🔥

**PodAffinity = 志同道合的朋友**
- 爱打篮球的人喜欢住在一起（互相依赖，需要低延迟通信）
- 靠近点方便交流，效率更高

**PodAntiAffinity = 独来独往的孤狼**
- 容易吵架的人不能住同一层楼（避免单点故障）
- 硬盘密集型的应用不要和CPU密集型的应用争资源
- 同一个应用的不同实例最好分散到不同节点（高可用）

### 核心概念

| 类型 | 用途 | 典型场景 |
|------|------|----------|
| **PodAffinity** | 让Pod调度到特定Pod所在的节点 | 数据库应用和缓存放在一起 |
| **PodAntiAffinity** | 让Pod避开特定Pod所在的节点 | 多副本分散部署、资源隔离 |
| **NodeAffinity** | 基于节点标签调度 | 硬件资源选择、区域划分 |

### 实操步骤

**场景1：PodAffinity - Web应用和Redis必须部署在同一节点**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      affinity:
        podAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - redis
            topologyKey: kubernetes.io/hostname
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
```

**场景2：PodAntiAffinity - 多副本强制分散到不同节点**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: high-availability-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ha-app
  template:
    metadata:
      labels:
        app: ha-app
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - ha-app
            topologyKey: kubernetes.io/hostname
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

**场景3：软性反亲和 - 尽量分散，但也可以集中**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: soft-anti-affinity-app
spec:
  replicas: 5
  selector:
    matchLabels:
      app: soft-ha-app
  template:
    metadata:
      labels:
        app: soft-ha-app
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - soft-ha-app
              topologyKey: kubernetes.io/hostname
      containers:
      - name: nginx
        image: nginx:1.21
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **TopologyKey是什么？**
> - TopologyKey定义了"亲疏关系的作用范围"
> - `kubernetes.io/hostname`：同一台服务器
> - `topology.kubernetes.io/zone`：同一个可用区
> - `topology.kubernetes.io/region`：同一个区域
>
> **PodAntiAffinity的问题**：
> - 如果副本数超过节点数，多余的Pod会无法调度
> - 例如：3个副本，2个节点 → 第3个副本永远Pending
>
> **解决方法**：使用软性反亲和，或者增加节点数

---

## 6.2 污点与容忍度：VIP专属通道

### 6.2.1 污点（Taint）：节点说"不"

### 一句话人话
**污点**是节点上的标记，给节点加限制条件，拒绝不符合条件的Pod调度上来。

### 生活比喻 🔥
就像**餐厅的VIP包间**：
- 普通顾客（普通Pod）不能进入VIP包间（有污点的节点）
- 只有VIP客户（有容忍度的Pod）才能进入
- 包间可能有特殊设备（GPU、专用硬件），只服务于特定需求

### 核心概念

污点由三个部分组成：
```
key=value:effect
```

| Effect | 效果 | 说明 |
|--------|------|------|
| **NoSchedule** | 不可调度 | 新Pod不能调度，已运行的Pod不受影响 |
| **PreferNoSchedule** | 尽量不调度 | 尽量不调度，但如果资源紧张也可以 |
| **NoExecute** | 驱逐 | 新Pod不能调度，已运行的Pod如果不匹配会被驱逐 |

### 实操步骤

**步骤1：给节点打污点**

```bash
# 查看节点当前污点
kubectl describe node node-1 | grep Taint

# 添加NoSchedule污点（普通Pod无法调度）
kubectl taint nodes node-1 dedicated=database:NoSchedule

# 添加NoExecute污点（会驱逐不匹配的Pod）
kubectl taint nodes node-2 special=gpu:NoExecute

# 添加PreferNoSchedule污点（软限制）
kubectl taint nodes node-3 preferred=true:PreferNoSchedule

# 删除污点（注意：key后面的-表示删除）
kubectl taint nodes node-1 dedicated:NoSchedule-

# 查看所有节点及其污点
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints
```

**步骤2：创建普通Pod（无法调度到有污点的节点）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: normal-pod
spec:
  containers:
  - name: nginx
    image: nginx:1.21
```

**验证**：如果只有一个节点且有NoSchedule污点，这个Pod会一直Pending。

**步骤3：创建有容忍度的Pod（可以调度到有污点的节点）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: database-pod
spec:
  # 匹配节点的dedicated=database:NoSchedule污点
  tolerations:
  - key: dedicated
    operator: Equal
    value: database
    effect: NoSchedule
  containers:
  - name: mysql
    image: mysql:8.0
    env:
    - name: MYSQL_ROOT_PASSWORD
      value: "password123"
    resources:
      requests:
        memory: "512Mi"
        cpu: "250m"
      limits:
        memory: "1Gi"
        cpu: "500m"
```

**步骤4：更复杂的容忍度配置**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-toleration-pod
spec:
  tolerations:
  # 精确匹配污点
  - key: dedicated
    operator: Equal
    value: database
    effect: NoSchedule
  # 匹配所有key为special的污点，effect为NoExecute
  - key: special
    operator: Exists
    effect: NoExecute
  # 匹配所有key为gpu的污点，任何effect
  - key: gpu
    operator: Exists
  # 匹配所有污点（慎用！）
  - operator: Exists
  containers:
  - name: nginx
    image: nginx:1.21
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **Taint vs NodeSelector的区别？**
> - **NodeSelector**：Pod说"我要去A节点"（主动选择）
> - **Taint**：节点说"我不接收某些Pod"（被动拒绝）
> - 两者的配合：节点打Taint拒绝普通Pod，Pod加Toleration请求进入
>
> **常见的系统污点**：
> - `node.kubernetes.io/not-ready`：节点NotReady
> - `node.kubernetes.io/unreachable`：节点不可达
> - `node.kubernetes.io/memory-pressure`：内存压力
> - `node.kubernetes.io/disk-pressure`：磁盘压力
> - `node.kubernetes.io/pid-pressure`：PID压力
>
> 这些污点会让不匹配的Pod被驱逐，以保护集群稳定性

---

### 6.2.2 实战：GPU节点专用

### 一句话人话
**GPU节点配置污点**，只让AI/机器学习等需要GPU的应用调度到该节点。

### 生活比喻 🔥
就像**专业实验室**：
- 只有上过相关课程（有特定标签）的学生才能进入
- 实验室里昂贵的设备（GPU）不会被普通项目占用
- 资源利用率最大化，避免浪费

### 实操步骤

**步骤1：给GPU节点打污点**

```bash
# 假设node-gpu是GPU节点
kubectl taint nodes node-gpu gpu=true:NoSchedule
kubectl label nodes node-gpu hardware=gpu

# 验证
kubectl describe node node-gpu | grep -A 10 "Taints"
```

**步骤2：创建需要GPU的Pod**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: tensorflow-pod
spec:
  # 1. 通过Toleration允许调度到GPU节点
  tolerations:
  - key: gpu
    operator: Equal
    value: "true"
    effect: NoSchedule
  
  # 2. 通过NodeSelector确保调度到GPU节点
  nodeSelector:
    hardware: gpu
  
  containers:
  - name: tensorflow
    image: tensorflow/tensorflow:latest-gpu
    command: ["python"]
    args: ["-c", "import tensorflow as tf; print('GPU:', tf.test.is_gpu_available())"]
    resources:
      requests:
        nvidia.com/gpu: 1
      limits:
        nvidia.com/gpu: 1
```

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

### 💡 一句话总结
调度是K8s的核心能力，NodeSelector简单粗暴，Affinity灵活强大，Taint/Toleration实现资源隔离。就像餐厅安排座位，有硬性要求、软性偏好，还有VIP包间。

---

## 6.3 资源限制：别让Pod吃撑了

### 6.3.1 Requests和Limits

### 一句话人话
**Requests**是Pod承诺需要的最少资源，**Limits**是Pod最多能使用的资源上限。

### 生活比喻 🔥

**Requests = 预订座位**
- 告诉餐厅（K8s）："我需要4个人位"
- 餐厅会预留这4个位子（资源预留）
- 其他Pod不能占用这部分资源

**Limits = 消费上限**
- 告诉餐厅："我们最多吃5个人"
- 超过了就不再给吃的（CPU会被限速，内存OOM会被杀）
- 防止某个Pod吃撑了影响其他Pod

### 核心概念

| 资源 | Requests | Limits | 说明 |
|------|----------|--------|------|
| **CPU** | 保证的最小CPU | 使用的最大CPU | 超过限速 |
| **Memory** | 保证的最小内存 | 使用的最大内存 | 超过被杀（OOM） |
| **Storage** | 保证的最小存储 | 无 | PVC申请时使用 |

**CPU单位**：
- `1` = 1个CPU核心（1000m）
- `100m` = 0.1个CPU核心（10%）
- `500m` = 0.5个CPU核心（50%）
- `2` = 2个CPU核心（200%）

**内存单位**：
- `128Mi` = 128兆字节
- `1Gi` = 1吉字节
- `1G` = 1000000000字节
- `1Gi` = 1073741824字节（推荐用Gi/Mi）

### 实操步骤

**场景1：设置Requests和Limits**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-demo
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    resources:
      requests:
        cpu: "250m"      # 保证250毫核CPU
        memory: "256Mi"  # 保证256MB内存
      limits:
        cpu: "500m"      # 最多使用500毫核CPU
        memory: "512Mi"  # 最多使用512MB内存
  
  - name: redis
    image: redis:7
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
      limits:
        cpu: "200m"
        memory: "256Mi"
```

**场景2：不设置Limit的风险**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# ❌ 危险配置：不设置Limits
apiVersion: v1
kind: Pod
metadata:
  name: dangerous-pod
spec:
  containers:
  - name: memory-hog
    image: ubuntu
    command: ["bash", "-c", "while true; do dd if=/dev/zero of=/dev/shm/fill bs=1M count=100; done"]
    resources:
      requests:
        memory: "128Mi"
      # 没有设置limits，可能会占用所有内存！
```

**场景3：CPU限速测试**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: cpu-limit-demo
spec:
  containers:
  - name: stress
    image: polinux/stress
    command: ["stress"]
    args: ["--cpu", "2", "--timeout", "300s"]  # 请求2个CPU
    resources:
      requests:
        cpu: "100m"
      limits:
        cpu: "200m"  # 但限制只能用200m
```

验证：进入Pod查看CPU使用率，会发现CPU被限制在200m（20%）左右。

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **CPU vs Memory的超限处理**：
> - **CPU超限**：Pod不会被杀，只是CPU使用被限速（throttled），变慢
> - **Memory超限**：Pod会立即被OOM Killer杀死，重启
>
> **不设置Limit的后果**：
> - Pod可能占用节点所有资源
> - 影响同一节点的其他Pod
> - 甚至导致节点崩溃
>
> **Limit Range（资源配额）**：
> - 可以在Namespace级别设置默认的Requests和Limits
> - 强制所有Pod遵守资源约束

---

### 6.3.2 LimitRange：统一规范

### 一句话人话
**LimitRange**是命名空间级别的资源限制规则，为所有Pod设定默认和最大值。

### 生活比喻 🔥
就像**小区的装修规定**：
- 所有业主必须遵守（统一规范）
- 新装修的业主按标准执行（默认值）
- 不能超出限制（最大值）
- 避免某个业主过度装修影响整栋楼

### 实操步骤

**创建LimitRange**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: cpu-mem-limit-range
  namespace: default
spec:
  limits:
  - type: Container
    default:          # 默认的Limits
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:   # 默认的Requests
      cpu: "250m"
      memory: "256Mi"
    max:              # 最大的Limits
      cpu: "2"
      memory: "2Gi"
    min:              # 最小的Requests
      cpu: "50m"
      memory: "64Mi"
    maxLimitRequestRatio:  # Limit/Request的最大比率
      cpu: "2"
      memory: "1.5"
```

**验证LimitRange**

```bash
# 查看LimitRange
kubectl get limitrange

kubectl describe limitrange cpu-mem-limit-range

# 创建不设置资源的Pod（自动使用默认值）
kubectl run nginx-default --image=nginx:1.21 --restart=Never

# 查看Pod的资源（自动加上了Limits）
kubectl describe pod nginx-default | grep -A 5 "Limits"
```

**LimitRange的类型**

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: all-limits
spec:
  limits:
  - type: Container      # 限制容器
    max:
      cpu: "800m"
      memory: "1Gi"
  - type: Pod           # 限制Pod（所有容器总和）
    max:
      cpu: "2"
      memory: "4Gi"
  - type: PersistentVolumeClaim  # 限制PVC
    max:
      storage: "10Gi"
    min:
      storage: "1Gi"
```

---

### 6.3.3 ResourceQuota：总量控制

### 一句话人话
**ResourceQuota**限制命名空间可以使用的总资源量，防止过度消耗集群资源。

### 生活比喻 🔥
就像**家庭的月度预算**：
- 全家人这个月只能花5000元（总量限制）
- 买衣服最多2000元（特定资源限制）
- 每个人都有自己的额度（Pod级别）
- 总预算超了就不能再消费了

### 实操步骤

**创建ResourceQuota**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-resources
  namespace: default
spec:
  hard:
    requests.cpu: "4"      # 该命名空间总共只能申请4核CPU
    requests.memory: "8Gi"  # 总共只能申请8GB内存
    limits.cpu: "8"         # 总共最多使用8核CPU
    limits.memory: "16Gi"   # 总共最多使用16GB内存
    pods: "10"              # 最多创建10个Pod
    requests.nvidia.com/gpu: "2"  # 最多申请2个GPU
```

**创建对象数量配额**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: object-counts
  namespace: default
spec:
  hard:
    configmaps: "10"        # 最多10个ConfigMap
    persistentvolumeclaims: "5"  # 最多5个PVC
    replicationcontrollers: "20" # 最多20个RC
    secrets: "10"            # 最多10个Secret
    services: "5"            # 最多5个Service
    services.loadbalancers: "1"  # 最多1个LoadBalancer类型的Service
```

**验证配额**

```bash
# 查看配额
kubectl get resourcequota

kubectl describe resourcequota compute-resources

# 尝试创建超过配额的Pod（会失败）
kubectl run test-pod --image=nginx:1.21 --requests=cpu=5 --restart=Never

# 错误信息：exceeded quota: compute-resources, requested: requests.cpu=5, used: requests.cpu=0, limited: requests.cpu=4
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **LimitRange vs ResourceQuota的区别？**
> - **LimitRange**：限制单个Pod/容器的资源
> - **ResourceQuota**：限制整个命名空间的总资源
>
> **配额的作用范围**：
> - 默认对整个命名空间生效
> - 可以通过`ScopeSelector`限定特定Pod（比如BestEffort的Pod不计入配额）
>
> **生产环境最佳实践**：
> 1. 每个Namespace设置ResourceQuota
> 2. 设置LimitRange提供默认值
> 3. 所有Pod显式设置资源请求和限制
> 4. 定期监控资源使用情况

---

## 6.4 自动伸缩：动态调整规模

### 6.4.1 HPA：水平自动伸缩

### 一句话人话
**HPA（Horizontal Pod Autoscaler）**根据Pod的CPU/内存使用率，自动增加或减少Pod的副本数。

### 生活比喻 🔥
就像**餐厅的动态排班**：
- 高峰期顾客多了，服务员不够，临时叫人手（扩容）
- 低谷期顾客少了，太多服务员闲着，安排休息（缩容）
- 根据当前排队人数（CPU使用率）决定增减多少人手
- 避免顾客等太久，也避免服务员闲置浪费

### 核心概念

HPA的工作流程：
```
1. Metrics Server采集Pod的CPU/内存使用率
2. HPA定期检查指标（默认15秒一次）
3. 计算需要的副本数 = 当前副本数 × (当前使用率 / 目标使用率)
4. 调用Deployment/StatefulSet的Scale接口调整副本数
5. 循环执行，持续监控和调整
```

**HPA关键参数**：
- `minReplicas`：最小副本数
- `maxReplicas`：最大副本数
- `targetCPUUtilizationPercentage`：目标CPU使用率
- `targetMemoryUtilizationPercentage`：目标内存使用率

### 实操步骤

**前提：安装Metrics Server**

```bash
# 检查Metrics Server是否已安装
kubectl get pods -n kube-system | grep metrics-server

# 如果没有，安装Metrics Server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# 验证
kubectl top nodes
kubectl top pods
```

**步骤1：创建目标Deployment**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: php-apache
spec:
  selector:
    matchLabels:
      run: php-apache
  replicas: 1
  template:
    metadata:
      labels:
        run: php-apache
    spec:
      containers:
      - name: php-apache
        image: registry.k8s.io/hpa-example
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: "200m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
```

```bash
kubectl apply -f php-apache-deployment.yaml
kubectl expose deployment php-apache --port=80
```

**步骤2：创建HPA**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: php-apache-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: php-apache
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50  # 目标CPU使用率50%
```

```bash
kubectl apply -f hpa.yaml

# 查看HPA
kubectl get hpa

kubectl describe hpa php-apache-hpa
```

**步骤3：压力测试**

```bash
# 开一个终端，持续请求
kubectl run -i --tty load-generator --rm --image=busybox:1.28 --restart=Never -- /bin/sh -c "while sleep 0.01; do wget -q -O- http://php-apache; done"

# 另一个终端，观察HPA
watch kubectl get hpa php-apache-hpa

# 查看Pod数量变化
kubectl get pods -l run=php-apache -w
```

**停止压力后观察缩容**

```bash
# Ctrl+C停止压力请求后，等待几分钟
# Pod数量会自动缩回minReplicas（1个）
kubectl get pods -l run=php-apache
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **为什么HPA不工作？**
> - Pod没有设置resources.requests（HPA需要计算百分比）
> - Metrics Server未安装或异常
> - 当前使用率低于目标值，不会扩容
>
> **HPA的稳定窗口**：
> - 默认：扩容立即生效，缩容等待5分钟
> - 可通过`stabilizationWindowSeconds`调整
> - 避免频繁扩缩容（抖动）
>
> **HPA vs VPA的选择**：
> - **HPA**：增加Pod数量（横向），适合无状态应用
> - **VPA**：调整Pod资源（纵向），适合资源需求变化大的应用
> - **两者不能同时使用**：VPA调整requests，HPA基于requests计算，会冲突

---

### 6.4.2 VPA：垂直自动伸缩

### 一句话人话
**VPA（Vertical Pod Autoscaler）**根据Pod的历史资源使用情况，自动调整Pod的CPU和内存requests/limits。

### 生活比喻 🔥
就像**办公室的工位调整**：
- 观察员工（Pod）的工作量（资源使用）
- 发现经常加班（CPU/内存不足），升级配置（增加资源）
- 发现长期闲置，降级配置（减少资源）
- 同一个工位（Pod）调整大小，不是增加工位数量

### 核心概念

VPA由三个组件组成：
1. **Recommender**：监控资源使用，推荐合适的资源值
2. **Updater**：更新Pod的requests/limits（需要重启Pod）
3. **Admission Controller**：拦截Pod创建请求，应用推荐值

**VPA的四种模式**：
- `Off`：VPA仅计算推荐值，不应用
- `Initial`：只在Pod创建时应用推荐值
- `Recreate`：Pod重启时应用推荐值
- `Auto`：自动更新Pod（默认）

### 实操步骤

**前提：安装VPA**

```bash
# 克隆VPA仓库
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler

# 安装VPA
./hack/vpa-up.sh

# 验证
kubectl get pods -n kube-system | grep vpa
kubectl api-versions | grep autoscaling
```

**创建VPA**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: nginx-vpa
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind:       Deployment
    name:       nginx-deployment
  updatePolicy:
    updateMode: "Auto"  # Off, Initial, Recreate, Auto
  resourcePolicy:
    containerPolicies:
    - containerName: "*"
      minAllowed:
        cpu: "100m"
        memory: "256Mi"
      maxAllowed:
        cpu: "1"
        memory: "1Gi"
      controlledResources: ["cpu", "memory"]
```

```bash
kubectl apply -f vpa.yaml

# 查看VPA
kubectl get vpa

kubectl describe vpa nginx-vpa

# 查看推荐值
kubectl describe vpa nginx-vpa | grep -A 20 "Container Resource"
```

**查看VPA推荐**

```bash
# VPA会给出推荐的requests
kubectl describe vpa nginx-vpa

输出示例：
  Container Resource Usage:
    Lower Bound:
      cpu:    100m
      memory: 262144k
    Target:
      cpu:    587m
      memory: 262144k
    Uncapped Target:
      cpu:    587m
      memory: 262144k
    Upper Bound:
      cpu:    2
      memory: 2Gi
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **VPA会重启Pod吗？**
> - `Auto`模式下，会自动更新Pod的requests/limits，导致Pod重启
> - 生产环境建议用`Off`模式先观察推荐值
> - 手动调整后，再决定是否启用自动更新
>
> **VPA vs 手动调整资源**：
> - **优点**：自动监控、精准调整、避免资源浪费
> - **缺点**：Pod会重启、可能和HPA冲突
>
> **生产环境建议**：
> - 用VPA的`Off`模式观察推荐值
> - 根据推荐值手动调整requests/limits
> - 对于无状态应用，优先使用HPA
> - 对于有状态应用或资源需求变化大的应用，考虑VPA

---

### 6.4.3 Cluster Autoscaler：集群自动伸缩

### 一句话人话
**Cluster Autoscaler**根据集群的资源不足情况，自动增加或减少节点。

### 生活比喻 🔥
就像**连锁餐厅的门店管理**：
- 某个分店（节点）顾客多了，临时开新分店（增加节点）
- 分店生意冷清，关闭一些分店（减少节点）
- 根据整体需求调整分店数量
- 比只在一个分店增加服务员（HPA）更灵活

### 核心概念

Cluster Autoscaler的工作原理：
```
1. 检测到Pod处于Pending状态（资源不足）
2. 尝试调度失败，确认需要更多节点
3. 调用云厂商API创建新节点
4. 等待节点Ready
5. 重新调度Pending的Pod到新节点
6. 定期检查节点利用率，低利用率节点自动缩容
```

**适用场景**：
- 云厂商托管集群（GKE, EKS, AKS, ACK）
- 基于虚拟机节点的集群
- 节点池配置

### 实操步骤

**前提条件**：
1. 集群运行在云平台上
2. 有足够的配额创建新节点
3. 节点有正确的标签和污点

**配置Cluster Autoscaler（以GKE为例）**

```bash
# GKE上创建集群时启用autoscaler
gcloud container clusters create my-cluster \
  --num-nodes=1 \
  --min-nodes=1 \
  --max-nodes=5 \
  --enable-autoscaling
```

**配置YAML（适用于Kubeadm集群）**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-autoscaler
  namespace: kube-system
data:
  cluster-autoscaler.yaml: |
    scaleDownEnabled: true
    scaleDownDelayAfterAdd: 10m
    scaleDownUnneededTime: 10m
    skipNodesWithLocalStorage: true
    maxNodeProvisionTime: 15m
    podsPerCore: 10
    maxPodsPerNode: 110
    balanceSimilarNodeGroups: true
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cluster-autoscaler
  template:
    metadata:
      labels:
        app: cluster-autoscaler
    spec:
      serviceAccountName: cluster-autoscaler
      containers:
      - image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.27.0
        name: cluster-autoscaler
        resources:
          limits:
            cpu: 100m
            memory: 300Mi
          requests:
            cpu: 100m
            memory: 300Mi
        command:
        - ./cluster-autoscaler
        - --v=4
        - --stderrthreshold=info
        - --cloud-provider=aws  # 根据云厂商修改：aws, gce, azure
        - --skip-nodes-with-local-storage=false
        - --expander=priority
        - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/my-cluster
        env:
        - name: AWS_REGION
          value: us-west-2  # AWS区域
```

**测试自动扩容**

```bash
# 创建大量Pod，超过当前节点容量
kubectl create deployment stress-test --image=nginx:1.21 --replicas=20 --dry-run=client -o yaml | kubectl apply -f -

# 观察Pod状态
kubectl get pods -w

# 观察节点数量变化（等待几分钟）
kubectl get nodes -w

# 查看Cluster Autoscaler日志
kubectl logs -n kube-system deployment/cluster-autoscaler -f
```

**测试自动缩容**

```bash
# 删除大量Pod
kubectl delete deployment stress-test

# 等待10-15分钟，观察节点是否自动缩容
kubectl get nodes -w
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **Cluster Autoscaler不会缩容的情况**：
> - 节点上有系统Pod（kube-system namespace）
> - 节点上有使用本地存储的Pod
> - Pod有反亲和性要求，无法调度到其他节点
> - 节点刚加入集群不到10分钟
>
> **HPA vs Cluster Autoscaler的配合**：
> - **HPA**：调整Pod数量（微观）
> - **Cluster Autoscaler**：调整节点数量（宏观）
> - 两级联动：HPA先扩容Pod → 资源不足 → Cluster Autoscaler扩容节点
>
> **生产环境建议**：
> 1. 设置合理的min和max节点数
> 2. 配置节点池，区分不同规格的节点
> 3. 使用PodDisruptionBudget保护重要应用
> 4. 监控扩缩容事件，及时调整配置

---

## 本章小结

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

### 💡 一句话总结
K8s的调度与伸缩就像智能餐厅管理系统：NodeSelector和Affinity安排座位，Taint/Toleration实现VIP专区，资源限制防止浪费，HPA/VPA/Cluster Autoscaler实现动态调整。合理配置才能既保证服务质量，又提高资源利用率。

---

# 第七篇：安全与权限

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

## 前言：安全第一，权限分明

想象你是一家大公司的IT管理员，需要管理成百上千的员工和应用。如何确保：
- 每个人只能访问他们需要的资源？（最小权限原则）
- 敏感数据不被泄露？（数据安全）
- 恶意代码被隔离？（网络安全）

K8s提供了完善的安全机制：RBAC控制权限，ServiceAccount管理身份，NetworkPolicy实现网络隔离，Pod Security保护容器安全。

本篇我们将深入了解K8s的安全体系。

---

## 7.1 RBAC：基于角色的访问控制

### 7.1.1 RBAC的核心概念

### 一句话人话
**RBAC（Role-Based Access Control）**通过角色来管理权限，给用户或服务账号分配角色，从而控制它们能做什么。

### 生活比喻 🔥
就像**公司的门禁卡系统**：
- **角色（Role）**：定义了一组权限（比如"工程师"可以进入机房和办公室）
- **用户（User）**：具体的人（张三、李四）
- **绑定（RoleBinding）**：把用户和角色绑定（张三是工程师）
- **权限（Permission）**：具体能做什么（开门、读文件）

**RBAC的好处**：
- 张三离职了，删除用户即可，不需要修改角色
- 李四升职了，换个角色绑定，不需要重复授权
- 权限和角色分离，管理清晰

### 核心概念

RBAC的四个核心对象：

| 对象 | 作用 | 作用范围 |
|------|------|----------|
| **Role** | 定义角色和权限 | 单个命名空间 |
| **ClusterRole** | 定义角色和权限 | 整个集群 |
| **RoleBinding** | 绑定角色和主体 | 单个命名空间 |
| **ClusterRoleBinding** | 绑定ClusterRole和主体 | 整个集群 |

**主体（Subject）类型**：
- `User`：用户（外部管理，K8s不存储）
- `Group`：用户组（外部管理，K8s不存储）
- `ServiceAccount`：服务账号（K8s管理，Pod使用）

**API资源**和**动词（Verbs）**：

| 资源类型 | 说明 |
|----------|------|
| `pods`, `deployments`, `services` | 具体的K8s资源 |
| `configmaps`, `secrets` | 配置和密钥 |
| `persistentvolumeclaims` | 持久化存储 |
| `namespaces`, `nodes` | 集群级资源 |

| 动词 | 说明 |
|------|------|
| `get`, `list`, `watch` | 读取 |
| `create`, `update`, `patch` | 修改 |
| `delete` | 删除 |
| `*` | 所有权限 |

### 实操步骤

**场景1：创建开发人员的Role（只能管理Pod）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-manager
rules:
- apiGroups: [""]  # "" 表示核心API组（Pod, Service等）
  resources: ["pods", "pods/log", "pods/exec"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: [""]
  resources: ["pods/status"]
  verbs: ["get"]
```

**场景2：创建只读Role**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get"]
```

**场景3：绑定Role到用户**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: bind-pod-manager
  namespace: default
subjects:
- kind: User
  name: "alice@example.com"  # 用户名
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-manager
  apiGroup: rbac.authorization.k8s.io
```

**场景4：绑定Role到ServiceAccount**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: bind-sa-to-pod-reader
  namespace: default
subjects:
- kind: ServiceAccount
  name: my-app-sa
  namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

**验证权限**

```bash
# 创建测试用户（使用kubectl的模拟功能）
kubectl auth can-i get pods --as=alice@example.com

# 模拟ServiceAccount
kubectl auth can-i create pods --as=system:serviceaccount:default:my-app-sa

# 查看所有Role
kubectl get roles -n default

kubectl describe role pod-manager

# 查看所有RoleBinding
kubectl get rolebindings -n default

kubectl describe rolebinding bind-pod-manager
```

---

### 7.1.2 ClusterRole和ClusterRoleBinding

### 一句话人话
**ClusterRole**和**ClusterRoleBinding**用于集群级别的权限控制，不受命名空间限制。

### 生活比喻 🔥
就像**公司的全局管理员**：
- 可以访问所有部门（所有命名空间）
- 可以创建新部门（创建命名空间）
- 可以管理服务器和基础设施（集群级资源）
- 比部门经理（Role）权限更大

### 实操步骤

**场景1：创建管理员ClusterRole**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-admin  # 内置的超级管理员角色（谨慎使用！）
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

**注意**：`cluster-admin`是K8s内置的超级管理员角色，拥有所有权限，谨慎分配！

**场景2：自定义ClusterRole - 集群级别的Pod查看权限**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-pod-viewer
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["namespaces"]
  verbs: ["get", "list"]
- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets", "daemonsets"]
  verbs: ["get", "list", "watch"]
```

**场景3：绑定ClusterRole到用户**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: bind-cluster-admin
subjects:
- kind: User
  name: "admin@example.com"
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
```

**场景4：跨命名空间使用Role**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# ClusterRole定义在cluster级别
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: namespace-admin
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
---
# 在特定命名空间绑定
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: namespace-admin-binding
  namespace: development
subjects:
- kind: User
  name: "dev-lead@example.com"
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: namespace-admin
  apiGroup: rbac.authorization.k8s.io
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **Role vs ClusterRole的区别？**
> - **Role**：只在单个命名空间生效
> - **ClusterRole**：在整个集群生效
>
> **RoleBinding vs ClusterRoleBinding的区别？**
> - **RoleBinding**：绑定Role或ClusterRole到主体，作用范围是命名空间
> - **ClusterRoleBinding**：绑定ClusterRole到主体，作用范围是整个集群
>
> **常见的内置ClusterRole**：
> - `cluster-admin`：超级管理员（所有权限）
> - `admin`：命名空间管理员（命名空间内所有权限）
> - `edit`：编辑者（可以修改资源，但不能修改Role/Binding）
> - `view`：查看者（只读权限）
>
> **查看内置Role**：
> ```bash
> kubectl get clusterrole
> kubectl describe clusterrole cluster-admin
> kubectl describe clusterrole admin
> kubectl describe clusterrole edit
> kubectl describe clusterrole view
> ```

---

### 7.1.3 RBAC实战：CI/CD流水线权限

### 一句话人话
为CI/CD工具（如Jenkins、GitLab CI）创建最小权限的ServiceAccount，只让它能部署和更新应用。

### 生活比喻 🔥
就像**建筑公司的项目经理**：
- 可以在现场部署材料（部署应用）
- 可以查看施工进度（查看Pod状态）
- 但不能动公司的财务数据（不能访问Secret）
- 权限够用，但不多给

### 实操步骤

**步骤1：创建CI/CD专用的ServiceAccount**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ci-cd-sa
  namespace: production
```

**步骤2：创建CI/CD专用的Role**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ci-cd-role
  namespace: production
rules:
# Deployment管理
- apiGroups: ["apps"]
  resources: ["deployments", "deployments/scale", "deployments/status"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]

# Service管理
- apiGroups: [""]
  resources: ["services", "endpoints"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]

# ConfigMap管理
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]

# Secret管理（只允许创建，不允许读取其他Secret）
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["create"]
- apiGroups: [""]
  resourceNames: ["ci-cd-secret"]
  resources: ["secrets"]
  verbs: ["get", "update", "delete"]

# Pod管理（读取日志和状态）
- apiGroups: [""]
  resources: ["pods", "pods/log", "pods/status"]
  verbs: ["get", "list", "watch"]

# Ingress管理
- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

**步骤3：绑定Role到ServiceAccount**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: bind-ci-cd
  namespace: production
subjects:
- kind: ServiceAccount
  name: ci-cd-sa
  namespace: production
roleRef:
  kind: Role
  name: ci-cd-role
  apiGroup: rbac.authorization.k8s.io
```

**步骤4：使用ServiceAccount的token**

```bash
# 获取ServiceAccount的token
kubectl get secret -n production | grep ci-cd-sa

TOKEN_NAME=$(kubectl get secret -n production | grep ci-cd-sa | awk '{print $1}')
TOKEN=$(kubectl get secret $TOKEN_NAME -n production -o jsonpath='{.data.token}' | base64 -d)

echo $TOKEN

# 使用token连接集群（模拟CI/CD工具）
kubectl config set-credentials ci-cd --token=$TOKEN
kubectl config set-context ci-cd-context --cluster=your-cluster --user=ci-cd
kubectl config use-context ci-cd-context

# 测试权限
kubectl get pods -n production  # 应该成功
kubectl delete pod -n production -l app=xxx  # 应该失败（没有删除Pod的权限）
```

---

## 7.2 ServiceAccount：Pod的身份凭证

### 7.2.1 ServiceAccount基础

### 一句话人话
**ServiceAccount**是Pod在K8s API中的身份，用于Pod与API Server通信。

### 生活比喻 🔥
就像**员工的工牌**：
- 每个员工（Pod）都有工牌（ServiceAccount）
- 进门刷卡（访问API Server）
- 不同级别的工牌权限不同（不同的ServiceAccount有不同的RBAC权限）
- 没工牌就不能进门（Pod没有ServiceAccount无法访问API）

### 核心概念

**默认ServiceAccount**：
- 每个命名空间自动创建一个`default` ServiceAccount
- 不指定ServiceAccount的Pod使用`default`
- `default`通常只有最低权限

**ServiceAccount和Pod的关系**：
```yaml
spec:
  serviceAccountName: my-custom-sa  # 指定ServiceAccount
```

**ServiceAccount的Secret**：
- 自动生成包含token的Secret
- 挂载到Pod的`/var/run/secrets/kubernetes.io/serviceaccount/`
- Pod自动使用这个token访问API Server

### 实操步骤

**场景1：创建自定义ServiceAccount**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: default
  labels:
    app: my-application
```

```bash
# 创建ServiceAccount
kubectl apply -f sa.yaml

# 查看ServiceAccount
kubectl get sa

kubectl describe sa my-app-sa

# 查看自动生成的Secret
kubectl get secrets | grep my-app-sa
```

**场景2：Pod使用自定义ServiceAccount**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-custom-sa
spec:
  serviceAccountName: my-app-sa  # 使用自定义ServiceAccount
  containers:
  - name: nginx
    image: nginx:1.21
    command:
    - /bin/sh
    - -c
    - |
      echo "ServiceAccount Token:"
      cat /var/run/secrets/kubernetes.io/serviceaccount/token
      sleep 3600
```

```bash
# 创建Pod
kubectl apply -f pod-with-sa.yaml

# 查看Pod的挂载（应该有serviceaccount token）
kubectl describe pod pod-with-custom-sa | grep -A 10 "Mounts"

# 进入Pod验证
kubectl exec -it pod-with-custom-sa -- sh

# 在Pod内
ls /var/run/secrets/kubernetes.io/serviceaccount/
# 输出：ca.crt  namespace  token

cat /var/run/secrets/kubernetes.io/serviceaccount/namespace
cat /var/run/secrets/kubernetes.io/serviceaccount/token
```

**场景3：禁用自动挂载token（安全实践）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-no-token
spec:
  serviceAccountName: default
  automountServiceAccountToken: false  # 不自动挂载token
  containers:
  - name: nginx
    image: nginx:1.21
```

**场景4：ServiceAccount级别的RBAC**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# 创建ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: list-pods-sa
---
# 创建Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-list-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
# 绑定Role到ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: bind-list-pods
subjects:
- kind: ServiceAccount
  name: list-pods-sa
roleRef:
  kind: Role
  name: pod-list-role
  apiGroup: rbac.authorization.k8s.io
---
# Pod使用ServiceAccount
apiVersion: v1
kind: Pod
metadata:
  name: test-list-pods
spec:
  serviceAccountName: list-pods-sa
  containers:
  - name: kubectl
    image: bitnami/kubectl:latest
    command: ["kubectl", "get", "pods"]
```

---

### 7.2.2 IAM角色绑定（云厂商集成）

### 一句话人话
**IAM角色绑定**让Pod可以使用云厂商的IAM权限，访问S3、RDS等云资源。

### 生活比喻 🔥
就像**公司的跨部门协作**：
- 你的工牌（ServiceAccount）不仅能进公司门（K8s API）
- 还能访问财务部（S3）、人事部（RDS）等
- 通过统一的身份系统，管理跨部门权限
- 不用每个部门单独发工牌

### 实操步骤（以AWS EKS为例）

**步骤1：创建IAM OIDC Provider**

```bash
# 获取集群的OIDC issuer
CLUSTER_NAME=your-cluster
AWS_REGION=us-west-2

OIDC_ISSUER=$(aws eks describe-cluster \
  --name $CLUSTER_NAME \
  --region $AWS_REGION \
  --query "cluster.identity.oidc.issuer" \
  --output text)

echo $OIDC_ISSUER
# 输出：https://oidc.eks.us-west-2.amazonaws.com/id/EXAMPLE...

# 提取provider URL
OIDC_PROVIDER=$(echo $OIDC_ISSUER | cut -f 3 -d'/')
echo $OIDC_PROVIDER
```

**步骤2：创建IAM策略（S3读写权限）**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ]
    }
  ]
}
```

保存为`s3-policy.json`，创建策略：

```bash
aws iam create-policy \
  --policy-name k8s-s3-policy \
  --policy-document file://s3-policy.json

POLICY_ARN=$(aws iam list-policies --query 'Policies[?PolicyName==`k8s-s3-policy`].Arn' --output text)
```

**步骤3：创建IAM Role并信任OIDC**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/OIDC_PROVIDER"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "OIDC_PROVIDER:sub": "system:serviceaccount:default:my-app-sa",
          "OIDC_PROVIDER:aud": "sts.amazonaws.com"
        }
      }
    }
  ]
}
```

创建IAM Role：

```bash
aws iam create-role \
  --role-name k8s-s3-role \
  --assume-role-policy-document file://trust-policy.json

aws iam attach-role-policy \
  --role-name k8s-s3-role \
  --policy-arn $POLICY_ARN
```

**步骤4：添加IAM Role注解到ServiceAccount**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: default
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT_ID:role/k8s-s3-role
```

**步骤5：验证IAM权限**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-s3-access
spec:
  serviceAccountName: my-app-sa
  containers:
  - name: aws-cli
    image: amazon/aws-cli:latest
    command:
    - /bin/sh
    - -c
    - |
      echo "Testing S3 access..."
      aws s3 ls s3://my-bucket
      aws s3 cp /etc/hostname s3://my-bucket/test-$(date +%s)
      sleep 3600
```

```bash
# 创建Pod
kubectl apply -f test-s3.yaml

# 查看日志（应该能看到S3 bucket内容）
kubectl logs test-s3-access
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **ServiceAccount vs User的区别？**
> - **ServiceAccount**：K8s管理的，用于Pod访问API
> - **User**：外部管理的（如LDAP、OAuth），用于人类用户
>
> **什么时候需要创建自定义ServiceAccount？**
> - Pod需要访问K8s API（如Operator）
> - 需要不同的权限隔离
> - 需要访问云厂商资源（绑定IAM角色）
>
> **安全最佳实践**：
> 1. 不需要访问API的Pod，禁用token挂载
> 2. 为每个应用创建专用ServiceAccount
> 3. 遵循最小权限原则，只给必要的RBAC权限
> 4. 定期审查ServiceAccount和权限

---

## 7.3 NetworkPolicy：网络隔离

### 7.3.1 NetworkPolicy基础

### 一句话人话
**NetworkPolicy**定义Pod之间的网络访问规则，实现网络隔离。

### 生活比喻 🔥
就像**公司的防火墙**：
- 研发部（Namespace）不能访问财务部（Namespace）
- 只有特定员工（标签选择器）可以进入特定房间（Pod）
- 只允许特定端口（端口）通信
- 防止网络攻击和横向渗透

### 核心概念

**NetworkPolicy的工作方式**：
- 默认：所有Pod可以互相通信（非隔离状态）
- 应用NetworkPolicy后：只允许白名单中的通信
- 每条NetworkPolicy包含：
  - `podSelector`：选择要应用规则的Pod
  - `policyTypes`：`Ingress`（入站）和/或`Egress`（出站）
  - `ingress`：允许哪些来源访问
  - `egress`：允许访问哪些目标

**支持NetworkPolicy的CNI插件**：
- Calico（推荐，功能丰富）
- Cilium（eBPF，性能高）
- Weave Net
- Canal（Flannel + Calico）

### 实操步骤

**前提：安装支持NetworkPolicy的CNI插件（以Calico为例）**

```bash
# 安装Calico
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml

# 验证
kubectl get pods -n kube-system | grep calico
```

**场景1：默认拒绝所有入站流量（白名单模式）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
  namespace: default
spec:
  podSelector: {}  # 空选择器 = 所有Pod
  policyTypes:
  - Ingress
  # 没有ingress规则 = 拒绝所有入站流量
```

**场景2：允许特定Pod访问（允许Web访问Backend）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-web-to-backend
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: backend  # 应用到backend Pod
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: web  # 允许web Pod访问
    ports:
    - protocol: TCP
      port: 8080  # 只允许访问8080端口
```

**场景3：多命名空间隔离（默认拒绝跨命名空间）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# 在命名空间dev上：拒绝所有跨命名空间的入站
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-cross-namespace
  namespace: dev
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector: {}  # 允许同一命名空间内的Pod访问
```

**场景4：允许访问特定命名空间**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# 允许dev命名空间访问prod命名服务的特定Pod
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dev-to-prod-api
  namespace: prod
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: dev  # 允许dev命名空间的Pod访问
    ports:
    - protocol: TCP
      port: 80
```

**场景5：出站流量控制（限制Pod只能访问特定服务）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: restrict-egress
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: restricted-pod
  policyTypes:
  - Egress
  egress:
  # 允许访问DNS（53端口UDP）
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: UDP
      port: 53
  # 允许访问特定的backend服务
  - to:
    - podSelector:
        matchLabels:
          app: backend
    ports:
    - protocol: TCP
      port: 8080
```

**场景6：完整的双向规则（入站+出站）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-policy
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: frontend
  policyTypes:
  - Ingress
  - Egress
  # 入站：允许来自ingress-nginx的流量
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 80
  # 出站：允许访问backend和DNS
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: backend
    ports:
    - protocol: TCP
      port: 8080
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: UDP
      port: 53
```

**验证NetworkPolicy**

```bash
# 创建测试Pod
kubectl run test-web --image=nginx:1.21 --labels=app=web --restart=Never
kubectl run test-backend --image=nginx:1.21 --labels=app=backend --port=8080 --restart=Never

# 测试连接
kubectl exec -it test-web -- curl http://test-backend:8080

# 查看NetworkPolicy
kubectl get networkpolicy

kubectl describe networkpolicy allow-web-to-backend
```

---

### 7.3.2 NetworkPolicy实战：多层应用隔离

### 一句话人话
为三层架构（Web → App → DB）应用创建网络隔离，防止横向攻击。

### 生活比喻 🔥
就像**银行的分区管理**：
- 大厅（Web层）：客户可以进来，但不能进入柜台
- 柜台（App层）：只处理业务，不能直接进入金库
- 金库（DB层）：只有特定的柜员可以进入
- 每层都有门禁（NetworkPolicy），防止越级访问

### 实操步骤

**步骤1：部署三层应用**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# Web层
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 2
  selector:
    matchLabels:
      tier: web
  template:
    metadata:
      labels:
        tier: web
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    tier: web
  ports:
  - port: 80
    targetPort: 80
---
# App层
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 2
  selector:
    matchLabels:
      tier: app
  template:
    metadata:
      labels:
        tier: app
    spec:
      containers:
      - name: app
        image: nginx:1.21
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: app
spec:
  selector:
    tier: app
  ports:
  - port: 8080
    targetPort: 8080
---
# DB层
apiVersion: apps/v1
kind: Deployment
metadata:
  name: db
spec:
  replicas: 1
  selector:
    matchLabels:
      tier: db
  template:
    metadata:
      labels:
        tier: db
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        env:
        - name: MYSQL_ROOT_PASSWORD
          value: "password123"
        ports:
        - containerPort: 3306
---
apiVersion: v1
kind: Service
metadata:
  name: db
spec:
  selector:
    tier: db
  ports:
  - port: 3306
    targetPort: 3306
```

**步骤2：应用网络隔离策略**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# DB层：只允许App层访问
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-policy
spec:
  podSelector:
    matchLabels:
      tier: db
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: app
    ports:
    - protocol: TCP
      port: 3306
---
# App层：只允许Web层访问，允许出站到DB
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-policy
spec:
  podSelector:
    matchLabels:
      tier: app
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: web
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          tier: db
    ports:
    - protocol: TCP
      port: 3306
---
# Web层：允许所有入站，只允许出站到App
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-policy
spec:
  podSelector:
    matchLabels:
      tier: web
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          tier: app
    ports:
    - protocol: TCP
      port: 8080
```

**步骤3：验证隔离效果**

```bash
# 创建测试Pod，尝试从各层访问
kubectl run test-pod --image=busybox:1.28 --rm -it --restart=Never -- sh

# 在Pod内测试
# 尝试直接访问DB（应该失败）
nslookup db
telnet db 3306

# 尝试从Web访问App（应该成功）
telnet app 8080

# 尝试从App访问DB（应该成功）
telnet db 3306
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **NetworkPolicy不生效？**
> - 确保CNI插件支持NetworkPolicy（如Calico、Cilium）
> - NetworkPolicy只适用于同一CNI网络内的Pod
> - NodePort/LoadBalancer的外部流量不受NetworkPolicy限制
>
> **白名单 vs 黑名单**：
> - **白名单（推荐）**：默认拒绝，明确允许（更安全）
> - **黑名单**：默认允许，明确拒绝（容易遗漏）
>
> **调试NetworkPolicy**：
> ```bash
> # 查看所有NetworkPolicy
> kubectl get networkpolicy -A
>
> # 查看Pod关联的NetworkPolicy
> kubectl describe pod <pod-name> | grep -A 10 "Network"
>
> # 使用工具测试连接（如curl、telnet、nc）
> ```

---

## 7.4 Pod安全策略

### 7.4.1 Pod Security Admission

### 一句话人话
**Pod Security Admission（PSA）**是K8s 1.25+的新安全标准，控制Pod的安全配置。

### 生活比喻 🔥
就像**机场的安检规则**：
- 所有人都要过安检（强制检查）
- 分三个等级：宽松（Privileged）、基准（Baseline）、受限（Restricted）
- 限制携带危险物品（特权容器、root用户等）
- 不同等级有不同限制

### 核心概念

**PSA的三种模式**：

| 模式 | 说明 | 适合场景 |
|------|------|----------|
| **Privileged** | 无限制 | 测试环境、系统级Pod |
| **Baseline** | 基础限制 | 生产环境（默认推荐） |
| **Restricted** | 严格限制 | 高安全要求环境 |

**PSA配置级别**：
- `cluster`：集群级别
- `namespace`：命名空间级别

**限制的内容**：
- 特权容器
- 宿主机路径挂载
- hostNetwork、hostPID、hostIPC
- root用户运行
- 容器Capabilities

### 实操步骤

**步骤1：给命名空间设置PSA级别**

```bash
# 设置为restricted模式（最严格）
kubectl label --overwrite ns production pod-security.kubernetes.io/enforce=restricted

# 设置为baseline模式
kubectl label --overwrite ns staging pod-security.kubernetes.io/enforce=baseline

# 设置warn模式（只警告，不拒绝）
kubectl label --overwrite ns development pod-security.kubernetes.io/warn=restricted

# 设置audit模式（审计，不拒绝）
kubectl label --overwrite ns development pod-security.kubernetes.io/audit=baseline
```

**步骤2：测试Pod Security Admission**

**特权Pod（会被拒绝）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: privileged-pod
  namespace: production
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    securityContext:
      privileged: true  # 特权模式
```

```bash
# 尝试创建（会被拒绝）
kubectl apply -f privileged-pod.yaml

# 错误信息：Pod violates PodSecurity "restricted:latest": privileged (container "nginx" must not set securityContext.privileged=true)
```

**安全的Pod（会被接受）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
  namespace: production
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
  containers:
  - name: nginx
    image: nginx:1.21
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

**查看命名空间的PSA设置**

```bash
kubectl get namespace production -o jsonpath='{.metadata.labels}' | jq .

# 输出示例：
{
  "kubernetes.io/metadata.name": "production",
  "pod-security.kubernetes.io/enforce": "restricted",
  "pod-security.kubernetes.io/warn": "baseline"
}
```

---

### 7.4.2 SecurityContext：容器安全配置

### 一句话人话
**SecurityContext**在Pod或容器级别设置安全参数，限制容器的权限。

### 生活比喻 🔥
就像**员工的工作权限配置**：
- 某些操作需要管理员权限（privileged）
- 某些人只能读不能写（readOnlyRootFilesystem）
- 禁止越权（allowPrivilegeEscalation）
- 剥离多余权限（drop capabilities）

### 实操步骤

**场景1：Pod级别的SecurityContext**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: security-context-demo
spec:
  securityContext:
    runAsUser: 1000          # 所有容器以1000用户运行
    runAsGroup: 3000         # 组ID
    fsGroup: 2000            # 文件系统组ID
  containers:
  - name: nginx
    image: nginx:1.21
    securityContext:
      allowPrivilegeEscalation: false  # 禁止提权
  - name: redis
    image: redis:7
```

**场景2：容器级别的SecurityContext（覆盖Pod级别）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: override-security
spec:
  securityContext:
    runAsUser: 1000
  containers:
  - name: nginx
    image: nginx:1.21
    securityContext:
      runAsUser: 2000  # 覆盖Pod级别的设置
  - name: redis
    image: redis:7
    # 使用Pod级别的runAsUser: 1000
```

**场景3：Capabilities管理**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: capabilities-demo
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    securityContext:
      capabilities:
        drop:
        - ALL        # 删除所有capabilities
        add:
        - NET_BIND_SERVICE  # 只添加绑定的权限
```

**场景4：只读根文件系统**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: readonly-root
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    securityContext:
      readOnlyRootFilesystem: true  # 只读根文件系统
    volumeMounts:
    - name: tmp
      mountPath: /tmp  # 需要挂载可写目录
    - name: cache
      mountPath: /var/cache/nginx
  volumes:
  - name: tmp
    emptyDir: {}
  - name: cache
    emptyDir: {}
```

**场景5：禁止特权容器**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: no-privilege
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    securityContext:
      privileged: false  # 禁止特权模式
      allowPrivilegeEscalation: false  # 禁止提权
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **Pod Security vs SecurityContext的区别？**
> - **Pod Security Admission**：命名空间级别的强制规则（K8s 1.25+）
> - **SecurityContext**：Pod或容器级别的安全配置（所有版本）
>
> **为什么需要只读根文件系统？**
> - 防止恶意代码修改系统文件
> - 防止被入侵后植入后门
> - 增强安全性
>
> **常见的SecurityContext配置**：
> ```yaml
> securityContext:
>   runAsNonRoot: true              # 非root用户
>   allowPrivilegeEscalation: false  # 禁止提权
>   readOnlyRootFilesystem: true    # 只读根文件系统
>   capabilities:
>     drop:
>     - ALL                         # 删除所有capabilities
> ```

---

## 本章小结

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

### 💡 一句话总结
K8s的安全体系层层设防：RBAC控制谁能做什么，ServiceAccount给Pod发身份卡，NetworkPolicy像防火墙隔离网络，Pod Security限制容器权限。遵循最小权限原则，才能既灵活又安全。

---
