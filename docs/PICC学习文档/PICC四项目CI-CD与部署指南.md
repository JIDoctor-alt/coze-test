# PICC门诊慢特病业务管理信息系统 CI/CD与部署指南

> **文档版本**: v1.0  
> **更新日期**: 2024年  
> **适用项目**: PICC门诊慢特病业务管理信息系统（四项目）

---

## 📋 目录

1. [系统概述](#系统概述)
2. [Part 1：构建流程](#part-1构建流程)
3. [Part 2：配置管理](#part-2配置管理)
4. [Part 3：部署架构](#part-3部署架构)
5. [Part 4：CI/CD流水线设计](#part-4cicd流水线设计)
6. [Part 5：运维手册](#part-5运维手册)
7. [附录：快速参考](#附录快速参考)

---

## 🏥 系统概述

### 1.1 项目架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              用户访问层                                       │
│                         (浏览器 / 移动端)                                     │
│                              :80 / :443                                      │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Nginx 反向代理层                                  │
│                      (Vue前端静态资源 + API路由分发)                          │
│                                                                             │
│   • /          → 前端静态资源                                                │
│   • /mtbapi/*  → 业务服务 (picc-mzmtb-gateway:9001)                        │
│   • /mbapi/*   → 鉴权服务                                                   │
│   • /mbjkglapi/* → 权限服务 (picc-mzmtb-user:9092)                         │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           前台服务层 (Gateway)                               │
│                     picc-mzmtb-gateway (端口:9001)                          │
│                         Spring Boot 微服务网关                               │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
┌───────────────────────────┐   ┌───────────────────────────┐
│      业务服务层             │   │      权限服务层             │
│ picc-mzmtb-server         │   │ picc-mzmtb-user           │
│ (端口:9091)               │   │ (端口:9092)               │
│                           │   │                           │
│ • Spring Boot多模块        │   │ • Spring Boot             │
│ • Maven构建                │   │ • 权限管理                 │
│ • Activiti工作流           │   │ • 用户认证                 │
└───────────────────────────┘   └───────────────────────────┘
```

### 1.2 服务清单

| 服务名称 | 项目路径 | 端口 | 技术栈 | 描述 |
|---------|---------|------|--------|------|
| **前端** | picc-mzmtb-agent | 80/443 | Vue 2 + Webpack + Nginx | 用户操作界面 |
| **前台服务** | picc-mzmtb-gateway | 9001 | Spring Boot | API网关/聚合服务 |
| **业务服务** | picc-mzmtb-server | 9091 | Spring Boot + Maven | 核心业务逻辑 |
| **权限服务** | picc-mzmtb-user | 9092 | Spring Boot | 权限认证服务 |

### 1.3 技术栈一览

| 类别 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **后端框架** | Spring Boot | 2.x | Java应用框架 |
| **微服务** | Spring Cloud | 2020.x | 微服务架构组件 |
| **构建工具** | Apache Maven | 3.6+ | Java项目构建管理 |
| **数据库** | PostgreSQL / GaussDB | - | 关系型数据库 |
| **配置中心** | Apollo | - | 分布式配置管理 |
| **缓存** | Redis + J2Cache | - | 分布式缓存 |
| **前端框架** | Vue.js | 2.6 | 前端渐进式框架 |
| **构建工具** | Webpack | 4.x | 前端资源打包 |
| **Web服务器** | Nginx | - | 反向代理服务器 |
| **容器化** | Docker | - | 应用容器化 |
| **编排** | Kubernetes | - | 容器编排平台 |

---

## ⭐ 零基础概念速查（小白化）

在开始之前，让我们用简单的比喻理解这些专业术语：

| 术语 | 小白化解释 | 比喻 |
|------|-----------|------|
| **CI/CD** | 自动流水线，代码提交后自动打包上货架 | 工厂流水线，工人提交零件，自动组装检测包装 |
| **Maven** | 自动化采购员，帮你下载jar包 | 餐厅采购员，自动采购所需食材 |
| **Docker** | 集装箱，把程序和所有依赖打包在一起 | 集装箱运输，无论什么货物都能统一运输 |
| **K8s (Kubernetes)** | 集装箱调度员，决定哪个集装箱放哪里 | 码头调度员，决定集装箱放在哪个位置 |
| **Nginx** | 前台接待，把客人引到正确的窗口 | 商场前台，引导顾客到对应柜台 |
| **Profile** | 换装间，开发穿便装，生产穿工装 | 演员更衣室，根据场景换不同服装 |
| **Apollo** | 中央广播站，所有服务听它指挥 | 广播台，统一播放通知给所有人 |
| **Build** | 打包/编译，把代码变成可运行的程序 | 烹饪，把食材做成成品菜 |
| **Deploy** | 部署/发布，把程序放到服务器上运行 | 上菜，把做好的菜端到客人面前 |
| **Pipeline** | 流水线，一系列自动化步骤 | 生产线，多个工位依次完成不同操作 |

---

## Part 1：构建流程

### 1.1 权限服务 (picc-mzmtb-user)

#### 1.1.1 项目结构

```
picc-mzmtb-user/
├── pom.xml                              # 父POM，包含公共依赖
├── picchealth-privilege-server/         # 服务模块
│   ├── pom.xml                          # 子模块POM
│   └── src/main/
│       ├── java/                         # Java源代码
│       └── resources/                    # 配置文件
│           ├── application.yml          # 主配置
│           ├── application-dev.yml      # 开发环境
│           ├── application-test.yml     # 测试环境
│           ├── application-uat.yml     # UAT环境
│           └── application-prod.yml     # 生产环境
├── picchealth-privilege-db/             # 数据库模块
│   └── pom.xml
└── config/
    └── docker/                           # Docker配置
        ├── dev/Dockerfile
        ├── sit/Dockerfile
        └── prd/Dockerfile
```

#### 1.1.2 pom.xml 关键配置分析

```xml
<!-- 父POM关键信息 -->
<groupId>com.picchealth</groupId>
<artifactId>picc-mzmtb-user</artifactId>
<packaging>pom</packaging>           <!-- pom类型，支持多模块 -->
<version>1.0-SNAPSHOT</version>

<modules>
    <module>picchealth-privilege-db</module>
    <module>picchealth-privilege-server</module>
</modules>

<!-- 关键属性 -->
<java.version>8</java.version>        <!-- Java 8 -->
<skipTests>true</skipTests>           <!-- 默认跳过测试 -->

<!-- 关键依赖 -->
<!-- PDFC微服务框架 -->
<dependency>
    <groupId>pdfc</groupId>
    <artifactId>pdfc-cloud</artifactId>
</dependency>

<!-- 宝蓝德中间件 -->
<dependency>
    <groupId>com.bes.appserver</groupId>
    <artifactId>bes-lite-spring-boot-2.x-starter</artifactId>
    <version>9.5.5.007</version>
</dependency>

<!-- Apollo配置中心客户端 -->
<dependency>
    <groupId>com.ctrip.framework.apollo</groupId>
    <artifactId>apollo-client</artifactId>
</dependency>
```

#### 1.1.3 构建命令

```bash
# 进入项目目录
cd /path/to/picc-mzmtb-user

# 完整构建（跳过测试）
mvn clean package -U -Dmaven.test.skip=true

# 安装到本地仓库（供其他模块依赖）
mvn clean install -U -Dmaven.test.skip=true

# 仅编译
mvn clean compile

# 指定环境打包
mvn clean package -Ppro -Dmaven.test.skip=true

# 带验证的构建
mvn clean verify -Dmaven.test.skip=true
```

#### 1.1.4 构建产物

```
权限服务模块输出：
picchealth-privilege-server/target/
└── picchealth-privilege-server-1.0-SNAPSHOT.jar
```

---

### 1.2 业务服务 (picc-mzmtb-server)

#### 1.2.1 项目结构 - Maven多模块

```
picc-mzmtb-server/
├── pom.xml                              # 父POM
├── picchealth-server/                   # 主服务模块 ★
│   ├── pom.xml
│   └── src/main/
│       └── resources/
│           ├── application.yml
│           ├── application-dev.yml
│           ├── application-test.yml
│           ├── application-uat.yml
│           ├── application-prod.yml
│           └── dev/
│               ├── application-dev.yml
│               └── application-sit.yml
├── picchealth-db/                       # 数据库实体模块
│   └── pom.xml
└── mtb-yh/                              # 业务子模块集合
    ├── pom.xml                          # 父POM
    ├── mtb-base/                        # 基础模块
    ├── mtb-bj/                          # 便捷模块
    ├── mtb-dz/                          # 定点模块
    ├── mtb-jc/                          # 基层模块
    ├── mtb-jj/                          # 就医模块
    ├── mtb-mzl/                         # 门诊总量模块
    ├── mtb-sl/                          # 申领模块
    ├── mtb-sya/                         # 适用药模块
    ├── mtb-ya/                          # 药典模块
    ├── mtb-yl/                          # 医疗模块
    └── mtb-yli/                         # 医疗保障模块
```

#### 1.2.2 pom.xml 关键配置分析

```xml
<!-- 父POM信息 -->
<groupId>com.picchealth</groupId>
<artifactId>picc-mzmtb-server</artifactId>
<packaging>pom</packaging>
<version>1.0</version>

<modules>
    <module>picchealth-db</module>
    <module>picchealth-server</module>
    <module>mtb-yh</module>
</modules>

<!-- 关键依赖 -->
<!-- Activiti工作流 -->
<dependency>
    <groupId>org.activiti</groupId>
    <artifactId>activiti-engine-picc</artifactId>
    <version>6.0.0</version>
</dependency>

<!-- POIOffice文档处理 -->
<dependency>
    <groupId>org.apache.poi</groupId>
    <artifactId>poi-ooxml</artifactId>
    <version>4.1.2</version>
</dependency>

<!-- 华为云OBS存储 -->
<dependency>
    <groupId>com.huaweicloud</groupId>
    <artifactId>esdk-obs-java</artifactId>
    <version>3.23.9</version>
</dependency>

<!-- XXL-Job分布式任务调度 -->
<dependency>
    <groupId>com.xuxueli</groupId>
    <artifactId>xxl-job-core</artifactId>
    <version>2.3.1</version>
</dependency>
```

#### 1.2.3 构建命令

```bash
# 进入项目目录
cd /path/to/picc-mzmtb-server

# 方式一：使用构建脚本
chmod +x mvnPackage.sh mvnInstall.sh mvnVerify.sh
./mvnPackage.sh    # 打包（带-Ppro）

# 方式二：直接Maven命令
# 完整构建
mvn clean install -U -Dmaven.test.skip=true

# 打包生产版本
mvn clean package -U -Dmaven.test.skip=true -Ppro

# 构建验证
mvn clean verify -Dmaven.test.skip=true

# 指定模块构建
mvn clean package -pl picchealth-server -am -Dmaven.test.skip=true
```

#### 1.2.4 构建产物

```
业务服务模块输出：
picchealth-server/target/
└── picchealth-server-1.0.jar
```

---

### 1.3 前台服务 (picc-mzmtb-gateway)

#### 1.3.1 项目结构

```
picc-mzmtb-gateway/
├── pom.xml
├── src/main/
│   ├── java/
│   │   └── (Java源码)
│   └── resources/
│       ├── application.yml
│       ├── application-dev.yml
│       ├── application-test.yml
│       ├── application-uat.yml
│       └── application-prod.yml
├── docker/
│   └── Dockerfile
└── lib/                      # 本地依赖库
```

#### 1.3.2 pom.xml 关键配置分析

```xml
<!-- 前台服务信息 -->
<groupId>com.picchealth</groupId>
<artifactId>picc-mzmtb-gateway</artifactId>
<version>1.0</version>

<!-- 关键插件：Spring Boot打包 -->
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
</plugin>

<!-- 关键依赖 -->
<!-- CXF WebService -->
<dependency>
    <groupId>org.apache.cxf</groupId>
    <artifactId>cxf-spring-boot-starter-jaxws</artifactId>
    <version>3.2.5</version>
</dependency>

<!-- PDF渲染 -->
<dependency>
    <groupId>org.xhtmlrenderer</groupId>
    <artifactId>flying-saucer-pdf-itext5</artifactId>
    <version>9.1.20</version>
</dependency>

<!-- FreeMarker模板引擎 -->
<dependency>
    <groupId>org.freemarker</groupId>
    <artifactId>freemarker</artifactId>
    <version>2.3.31</version>
</dependency>

<!-- SFTP文件传输 -->
<dependency>
    <groupId>com.jcraft</groupId>
    <artifactId>jsch</artifactId>
    <version>0.1.55</version>
</dependency>
```

#### 1.3.3 构建命令

```bash
cd /path/to/picc-mzmtb-gateway

# Maven打包
mvn clean package -Dmaven.test.skip=true

# 或使用完整命令
mvn clean package -U -Dmaven.test.skip=true
```

#### 1.3.4 构建产物

```
前台服务模块输出：
target/
└── picc-mzmtb-gateway-1.0.jar
```

---

### 1.4 前端 (picc-mzmtb-agent)

#### 1.4.1 项目结构

```
picc-mzmtb-agent/
├── package.json                 # npm依赖配置
├── .babelrc                     # ES6转码配置
├── .eslintrc.js                 # ESLint配置
├── build/                       # 构建脚本
│   ├── build.js                 # 生产构建入口
│   ├── webpack.base.conf.js      # 基础配置
│   ├── webpack.prod.conf.js      # 生产配置
│   └── webpack.dev.conf.js       # 开发配置
├── config/                      # 环境配置
│   ├── index.js                 # 主配置
│   ├── dev.env.js               # 开发环境变量
│   ├── test.env.js              # 测试环境变量
│   ├── uatMbReform.env.js       # UAT环境变量
│   ├── proMbReform.env.js       # 生产环境变量
│   └── proxyConfig.js           # 代理配置
├── src/                        # 源代码
│   ├── api/                     # API接口
│   ├── components/              # 组件
│   ├── router/                  # 路由
│   ├── store/                   # 状态管理
│   ├── views/                   # 页面
│   └── App.vue                  # 根组件
├── dist/                       # 构建输出（构建后生成）
├── docker/
│   └── Dockerfile
└── nginx-dev.conf              # 开发环境Nginx配置
└── nginx-pro.conf              # 生产环境Nginx配置
```

#### 1.4.2 package.json 关键配置分析

```json
{
  "name": "approve",
  "version": "1.0.0",
  "scripts": {
    // 生产构建（按环境）
    "dev": "node build/build.js dev",
    "test": "node build/build.js test",
    "uat": "node build/build.js uat",
    "sit": "node build/build.js sit",
    "production": "node build/build.js production",
    
    // 带版本号的生产构建
    "build:prod": "node resetVersion.js && cross-env NODE_ENV=proMbReform env_config=proMbReform node build/build.js",
    "build:uat": "cross-env NODE_ENV=uatMbReform env_config=uatMbReform node build/build.js",
    "build:test": "node resetVersion.js && cross-env NODE_ENV=testing env_config=test node build/build.js",
    
    // 本地开发服务器
    "s_dev": "webpack-dev-server --inline --progress --config build/webpack.dev.conf.js --dev",
    "s_test": "webpack-dev-server --inline --progress --config build/webpack.dev.conf.js --test",
    
    // 代码检查
    "lint": "eslint --ext .js,.vue src"
  },
  "dependencies": {
    "vue": "^2.6.11",
    "vue-router": "^3.3.4",
    "vuex": "^3.0.1",
    "axios": "^0.19.2",
    "element-ui": "...",
    "ant-design-vue": "^1.7.2"
  },
  "devDependencies": {
    "webpack": "^4.16.2",
    "webpack-cli": "^3.1.0",
    "webpack-dev-server": "^3.1.5",
    "vue-loader": "^15.2.6",
    "babel-core": "^6.22.1"
  }
}
```

#### 1.4.3 构建命令

```bash
cd /path/to/picc-mzmtb-agent

# 安装依赖
npm install
# 或使用yarn
yarn install

# 开发环境构建
npm run dev

# 测试环境构建
npm run test

# UAT环境构建
npm run uat

# 生产环境构建
npm run production

# 或使用npm scripts
npm run build:prod    # 生产
npm run build:uat     # UAT
npm run build:test    # 测试
```

#### 1.4.4 构建产物

```
前端构建输出：
output/                        # 输出目录
├── index.html
├── static/
│   ├── js/
│   │   ├── app.[hash].js     # 主应用JS
│   │   ├── vendor.[hash].js   # 第三方库JS
│   │   └── manifest.[hash].js # 缓存清单
│   ├── css/
│   │   └── [name].[hash].css  # 样式文件
│   └── img/                   # 静态图片

# Docker构建需要的压缩包
output/dist.tar.gz             # 打包后的tar.gz文件
```

---

## Part 2：配置管理

### 2.1 配置文件体系

#### 2.1.1 Spring Boot Profile 架构

```
application.yml                    # 主配置（通用配置）
    │
    ├── application-dev.yml       # 开发环境 (DEV)
    ├── application-test.yml      # 测试环境 (TEST)
    ├── application-uat.yml       # 用户验收测试环境 (UAT)
    ├── application-prod.yml      # 生产环境 (PROD)
    │
    └── dev/                      # 本地开发额外配置
        ├── application-dev.yml
        └── application-sit.yml
```

#### 2.1.2 application.yml 主配置示例

```yaml
# 权限服务配置
server:
  port: 9092

spring:
  profiles:
    active: dev                   # 默认激活dev环境
  application:
    name: picc-mzmtb-user         # 应用名称

apollo:
  bootstrap:
    enabled: true                 # 启用Apollo引导
    eagerLoad:
      enabled: true               # 提前加载配置
```

#### 2.1.3 环境差异化配置

| 环境 | Profile名称 | Apollo Namespace | 配置特点 |
|------|------------|-----------------|----------|
| **开发环境** | dev | application-local.properties | 本地开发，连接开发数据库 |
| **测试环境** | test | application.properties | 测试数据库，Mock数据 |
| **UAT环境** | uat | application.properties | 模拟生产环境 |
| **生产环境** | prod | application.properties | 真实生产环境 |

##### 各环境Apollo配置差异

**开发环境 (dev)**
```yaml
app:
  id: picc-mzmtb-user
apollo:
  bootstrap:
    enabled: true
    eagerLoad:
      enabled: true
    namespaces: application-local.properties  # 本地开发
  meta: http://10.57.16.41:8080              # 开发Apollo地址
```

**生产环境 (prod)**
```yaml
app:
  id: picc-mzmtb-user
apollo:
  bootstrap:
    enabled: true
    eagerLoad:
      enabled: true
    namespaces: application.properties        # 生产配置
  meta: http://10.34.80.145:8080             # 生产Apollo地址
```

### 2.2 Apollo配置中心使用

#### 2.2.1 Apollo核心概念

```
┌──────────────────────────────────────────────────────────────┐
│                        Apollo配置中心                         │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                    应用：picc-mzmtb-user               │  │
│  │  ┌──────────────────────────────────────────────────┐ │  │
│  │  │              Namespace: application               │ │  │
│  │  │  ┌────────────────────────────────────────────┐  │ │  │
│  │  │  │  配置项 Key=Value                           │  │ │  │
│  │  │  │  ┌─────────────────┬─────────────────┐     │  │ │  │
│  │  │  │  │ spring.datasource│ url: jdbc:...  │     │  │ │  │
│  │  │  │  │                 │ username: ***  │     │  │ │  │
│  │  │  │  │                 │ password: ***  │     │  │ │  │
│  │  │  │  └─────────────────┴─────────────────┘     │  │ │  │
│  │  │  └────────────────────────────────────────────┘  │ │  │
│  │  └──────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  环境: DEV | TEST | UAT | PROD                              │
└──────────────────────────────────────────────────────────────┘
```

#### 2.2.2 Apollo配置读取流程

```
应用启动
    │
    ▼
Bootstrap阶段 ──→ 读取本地application.yml
    │                    │
    │                    ▼
    │              读取Apollo Meta地址
    │                    │
    ▼                    ▼
连接Apollo ─────────→ 获取Namespace配置
    │
    ▼
合并配置到Spring Environment
    │
    ▼
应用启动完成
```

#### 2.2.3 Apollo配置示例

```properties
# 数据库配置
spring.datasource.url=jdbc:postgresql://${DB_HOST}:5432/picc_mzmtb
spring.datasource.username=${DB_USERNAME}
spring.datasource.password=${DB_PASSWORD}

# Redis配置
spring.redis.host=${REDIS_HOST}
spring.redis.port=6379
spring.redis.password=${REDIS_PASSWORD}

# 日志级别
logging.level.com.picchealth=INFO
logging.level.org.springframework=DEBUG
```

### 2.3 敏感配置安全建议

#### 2.3.1 敏感配置清单

| 配置类型 | 示例 | 安全级别 | 处理方式 |
|---------|------|---------|---------|
| 数据库密码 | `password: ***` | 🔴 极高 | Apollo加密或密钥管理 |
| API密钥 | `secret-key: ***` | 🔴 极高 | 密钥管理服务 |
| 证书密钥 | `.p12, .jks` | 🔴 极高 | K8s Secret |
| Redis密码 | `password: ***` | 🟠 高 | Apollo加密 |
| 文件存储密钥 | `oss.secret: ***` | 🟠 高 | Apollo加密 |
| 第三方密钥 | `openapi-key: ***` | 🟠 高 | 密钥管理服务 |

#### 2.3.2 安全配置建议

```yaml
# ❌ 不推荐：明文密码
spring:
  datasource:
    password: admin123

# ✅ 推荐：使用环境变量或密钥管理
spring:
  datasource:
    password: ${DB_PASSWORD}           # 环境变量
    # 或使用Apollo加密配置
```

#### 2.3.3 多环境配置分离策略

```
┌─────────────────────────────────────────────────────────────┐
│                      配置管理策略                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  DEV环境     │  TEST环境    │  UAT环境     │  PROD环境    │
│  ──────────  │  ──────────  │  ──────────  │  ──────────  │
│  本地配置    │  测试数据库   │  模拟生产    │  生产数据库   │
│  Mock数据    │  测试数据    │  真实数据    │  真实数据     │
│  详细日志    │  调试日志    │  适量日志    │  最小日志     │
│  任意访问    │  受限访问    │  受限访问    │  严格访问     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Part 3：部署架构

### 3.1 Kubernetes部署方案

#### 3.1.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Kubernetes Cluster                             │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                          Ingress / Gateway                          │    │
│  │                  (HTTPS入口，域名路由，SSL终止)                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        Service Layer (K8s Service)                   │    │
│  │                                                                       │    │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │    │
│  │   │picc-mzmtb-   │  │picc-mzmtb-   │  │picc-mzmtb-   │           │    │
│  │   │user-svc      │  │server-svc    │  │gateway-svc   │           │    │
│  │   │:9092         │  │:9091         │  │:9001         │           │    │
│  │   └──────────────┘  └──────────────┘  └──────────────┘           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        Pod Layer (应用容器)                          │    │
│  │                                                                       │    │
│  │   ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │    │
│  │   │  User Pod  │  │ Server Pod │  │Gateway Pod │  │ Agent Pod  │  │    │
│  │   │  (×2)      │  │   (×3)     │  │   (×2)     │  │  (×2)      │  │    │
│  │   │  权限服务   │  │  业务服务   │  │  前台服务   │  │  前端Nginx │  │    │
│  │   └────────────┘  └────────────┘  └────────────┘  └────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      Storage & Middleware                           │    │
│  │                                                                       │    │
│  │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │    │
│  │   │PostgreSQL│  │  Redis   │  │ Apollo   │  │   OBS    │          │    │
│  │   │ (主从)   │  │ (集群)   │  │ (配置中心)│  │ (对象存储)│          │    │
│  │   └──────────┘  └──────────┘  └──────────┘  └──────────┘          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 3.1.2 K8s Deployment YAML示例

**权限服务 Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: picc-mzmtb-user
  namespace: mzmtb-prod
  labels:
    app: picc-mzmtb-user
    version: v1.0
spec:
  replicas: 2
  selector:
    matchLabels:
      app: picc-mzmtb-user
  template:
    metadata:
      labels:
        app: picc-mzmtb-user
        version: v1.0
    spec:
      containers:
      - name: picc-mzmtb-user
        image: harbor.picchealth.com/picc-mzmtb/user:1.0.0
        ports:
        - containerPort: 9092
          name: http
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "prod"
        - name: APOLLO_META
          value: "http://apollo-meta:8080"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /actuator/health
            port: 9092
          initialDelaySeconds: 60
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /actuator/health
            port: 9092
          initialDelaySeconds: 30
          periodSeconds: 5
```

**业务服务 Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: picc-mzmtb-server
  namespace: mzmtb-prod
  labels:
    app: picc-mzmtb-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: picc-mzmtb-server
  template:
    metadata:
      labels:
        app: picc-mzmtb-server
    spec:
      containers:
      - name: picc-mzmtb-server
        image: harbor.picchealth.com/picc-mzmtb/server:1.0.0
        ports:
        - containerPort: 9091
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "prod"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

**前台服务 Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: picc-mzmtb-gateway
  namespace: mzmtb-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: picc-mzmtb-gateway
  template:
    metadata:
      labels:
        app: picc-mzmtb-gateway
    spec:
      containers:
      - name: picc-mzmtb-gateway
        image: harbor.picchealth.com/picc-mzmtb/gateway:1.0.0
        ports:
        - containerPort: 9001
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "prod"
```

#### 3.1.3 K8s Service YAML示例

```yaml
apiVersion: v1
kind: Service
metadata:
  name: picc-mzmtb-user-svc
  namespace: mzmtb-prod
spec:
  type: ClusterIP
  ports:
  - port: 9092
    targetPort: 9092
    protocol: TCP
  selector:
    app: picc-mzmtb-user
---
apiVersion: v1
kind: Service
metadata:
  name: picc-mzmtb-server-svc
  namespace: mzmtb-prod
spec:
  type: ClusterIP
  ports:
  - port: 9091
    targetPort: 9091
    protocol: TCP
  selector:
    app: picc-mzmtb-server
---
apiVersion: v1
kind: Service
metadata:
  name: picc-mzmtb-gateway-svc
  namespace: mzmtb-prod
spec:
  type: ClusterIP
  ports:
  - port: 9001
    targetPort: 9001
    protocol: TCP
  selector:
    app: picc-mzmtb-gateway
```

### 3.2 Docker镜像构建

#### 3.2.1 权限服务 Dockerfile

**开发环境**
```dockerfile
FROM harbortest.picchealth.com/hb-jczx-tyfwzt-dev/java:1.8

VOLUME /tmp

# 复制JAR包
ADD link-server-1.0.0.jar /link-server.jar

# 创建JAR包时间戳（防止Docker缓存问题）
RUN bash -c 'touch /link-server.jar'

# 设置时区
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone

EXPOSE 9092

ENTRYPOINT ["java","-Dsun.net.inetaddr.ttl=60","-Dsun.net.inetaddr.negative.ttl=60","-jar","/link-server.jar"]
```

**生产环境**
```dockerfile
FROM 10.35.201.106/hb-p-jczx-tyfwzt-al/java:1.8

VOLUME /tmp

ADD link-server-application.jar /link-server-application.jar

# 设置时区
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone
RUN bash -c 'touch /link-server-application.jar'

EXPOSE 9092

# JVM参数配置
ENV JAVA_OPTS="-Xmx2048M -Xms2048M -Xmn448M -XX:MaxMetaspaceSize=192M -XX:MetaspaceSize=192M"

# 使用shell方式执行，支持变量替换
ENTRYPOINT java ${JAVA_OPTS} -Dsun.net.inetaddr.ttl=60 -Dsun.net.inetaddr.negative.ttl=60 -jar /link-server-application.jar
```

#### 3.2.2 业务服务 Dockerfile

**生产环境**
```dockerfile
# 基础镜像
FROM 10.35.201.106/hb-p-jczx-tyfwzt-zt/hmlink-server:1.0.0

VOLUME /tmp

ADD link-server.jar /link-server.jar

# 时区配置
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone
RUN bash -c 'touch /link-server.jar'

EXPOSE 9091

# 优化后的JVM参数（4C8G机器）
ENV JAVA_OPTS="-Xmx4096M -Xms4096M -Xmn1536M -XX:MaxMetaspaceSize=1024M -XX:MetaspaceSize=819M"

ENTRYPOINT java ${JAVA_OPTS} -Dsun.net.inetaddr.ttl=60 -Dsun.net.inetaddr.negative.ttl=60 -jar /link-server.jar
```

#### 3.2.3 前端 Dockerfile

```dockerfile
# 基于Nginx基础镜像
FROM harbor.picchealth.com/hb-p-mzmtbyw/mb-base:0.0.4

# 复制构建产物
COPY dist.tar.gz /usr/local/nginx/

# 时区配置
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone

# 解压前端构建产物
RUN rm -rf /usr/local/nginx/dist
RUN tar zxvf /usr/local/nginx/dist.tar.gz -C /usr/local/nginx/

EXPOSE 443

# 启动Nginx（前台运行）
ENTRYPOINT ["/usr/local/nginx/sbin/nginx", "-g", "daemon off;"]
```

#### 3.2.4 镜像构建命令

```bash
# Java服务镜像构建
docker build -t harbor.picchealth.com/picc-mzmtb/user:1.0.0 -f config/docker/prd/Dockerfile .

# 前端镜像构建
cd picc-mzmtb-agent
npm run build:prod
tar -czvf dist.tar.gz -C output .
docker build -t harbor.picchealth.com/picc-mzmtb/agent:1.0.0 -f docker/Dockerfile .

# 推送镜像
docker push harbor.picchealth.com/picc-mzmtb/user:1.0.0
docker push harbor.picchealth.com/picc-mzmtb/server:1.0.0
docker push harbor.picchealth.com/picc-mzmtb/gateway:1.0.0
docker push harbor.picchealth.com/picc-mzmtb/agent:1.0.0
```

### 3.3 Nginx配置

#### 3.3.1 生产环境Nginx配置

```nginx
worker_processes 4;
events {
    worker_connections 1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] '
                    'request="$request" status=$status '
                    'bytes_sent=$bytes_sent body_bytes_sent=$body_bytes_sent '
                    'referer="$http_referer" user_agent="$http_user_agent" '
                    'upstream_addr=$upstream_addr upstream_status=$upstream_status';

    sendfile on;
    server_tokens off;
    keepalive_timeout 65;

    # 上游服务超时配置
    fastcgi_connect_timeout 300;
    fastcgi_send_timeout 300;
    fastcgi_read_timeout 300;

    # HTTP Server
    server {
        listen 80;
        server_name localhost;
        add_header X-Frame-Options SAMEORIGIN;

        # 前端静态资源
        location / {
            root /home/front/output;
            index index.html index.htm;
            try_files $uri $uri/ /index.html;
        }

        # 业务服务API
        location /mtbapi/mtb/gateway/ {
            proxy_pass http://picc-mzmtb-gateway-svc:9001/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            client_max_body_size 200m;
            add_header 'Access-Control-Allow-Origin' *;
        }

        # 鉴权服务
        location /mbapi/ {
            proxy_pass http://picc-mzmtb-auth-svc:8080/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            add_header 'Access-Control-Allow-Origin' *;
        }

        # 权限服务
        location /mbjkglapi/ {
            proxy_pass http://picc-mzmtb-user-svc:9092/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            add_header 'Access-Control-Allow-Origin' *;
        }

        # 图片服务
        location /mtbapi/appimg/ {
            proxy_pass http://image-service:9966/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }

    # HTTPS Server
    server {
        listen 443 ssl;
        server_name mtb.health.piccnet,mzmtb.picchealth.com,localhost;
        server_tokens off;
        add_header X-Frame-Options SAMEORIGIN;

        # SSL证书配置
        ssl_certificate /home/front/ssl/_.picchealth.com_bundle.crt;
        ssl_certificate_key /home/front/ssl/picchealth.com.key;
        ssl_session_cache shared:SSL:1m;
        ssl_session_timeout 5m;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        client_max_body_size 100m;

        # 静态资源配置同上...
        # API代理配置同上...
    }
}
```

#### 3.3.2 Nginx路由规则汇总

| URL路径 | 目标服务 | 端口 | 说明 |
|---------|---------|------|------|
| `/` | 前端静态资源 | 80 | Vue SPA应用 |
| `/mtbapi/*` | Gateway | 9001 | 业务接口 |
| `/mbapi/*` | 鉴权服务 | 8080 | 登录认证 |
| `/mbjkglapi/*` | 权限服务 | 9092 | 权限管理 |
| `/mtbapi/appimg/*` | 图片服务 | 9966 | 文件预览 |

### 3.4 数据库初始化与迁移

#### 3.4.1 数据库架构

```
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL / GaussDB                      │
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │  picc-mzmtb-user │  │ picc-mzmtb-server│                  │
│  │  (权限服务数据库) │  │   (业务数据库)    │                  │
│  │                  │  │                  │                  │
│  │  • 用户表        │  │  • 业务表         │                  │
│  │  • 角色表        │  │  • 工作流表       │                  │
│  │  • 权限表        │  │  • 流程定义表     │                  │
│  │  • 组织机构表    │  │  • 历史记录表     │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

#### 3.4.2 数据库初始化脚本

```sql
-- 创建数据库
CREATE DATABASE picc_mzmtb_user;
CREATE DATABASE picc_mzmtb_server;

-- 创建用户（生产环境应使用强密码）
CREATE USER mzmtb_user WITH PASSWORD '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON DATABASE picc_mzmtb_user TO mzmtb_user;
GRANT ALL PRIVILEGES ON DATABASE picc_mzmtb_server TO mzmtb_user;
```

#### 3.4.3 Flyway数据库迁移

```properties
# application-prod.yml
spring:
  flyway:
    enabled: true
    baseline-on-migrate: true
    locations: classpath:db/migration
    sql-migration-prefix: V
    sql-migration-separator: __
    sql-migration-suffixes: .sql
```

```
src/main/resources/db/migration/
├── V1.0.0__init_schema.sql
├── V1.0.1__init_data.sql
├── V1.1.0__add_workflow_table.sql
└── V1.1.1__add_new_column.sql
```

---

## Part 4：CI/CD流水线设计

### 4.1 流水线概述

#### 4.1.1 CI/CD是什么？

```
传统部署流程：
┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
│ 编写代码 │ → │ 本地测试 │ → │ 手动打包 │ → │ 上传服务器│ → │ 手动部署 │
└────────┘    └────────┘    └────────┘    └────────┘    └────────┘
     ↑                                                      ↑
     └──────────── 繁琐、耗时、容易出错 ────────────────────┘

CI/CD自动化流程：
┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
│ 代码提交 │ → │ 自动构建 │ → │ 自动测试 │ → │ 自动部署 │ → │ 自动验证 │
└────────┘    └────────┘    └────────┘    └────────┘    └────────┘
     │                           │                      │
     └────────── 一切自动化 ──────┴──────────────────────┘
```

#### 4.1.2 流水线阶段设计

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CI/CD 完整流水线                                     │
│                                                                             │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐     │
│  │ 代码检查 │ → │ 编译构建 │ → │ 单元测试 │ → │ 打包发布 │ → │ 部署测试 │     │
│  │ (Lint)  │   │(Maven) │   │ (Test)  │   │(Package)│   │(Deploy) │     │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘     │
│                                                                    │       │
│                                                                    ▼       │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐     │
│  │ 镜像构建 │ ← │ 代码扫描 │ ← │ 集成测试 │   │ 部署UAT │   │ 部署验证 │     │
│  │(Docker) │   │(SonarQ) │   │         │   │         │   │         │     │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘     │
│                                                                    │       │
│                                                                    ▼       │
│                                    ┌─────────┐   ┌─────────┐   ┌─────────┐ │
│                               ←─── │ 部署生产 │ ← │ 代码审批 │   │ 部署预审 │ │
│                                    │         │   │         │   │         │ │
│                                    └─────────┘   └─────────┘   └─────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 GitLab CI Pipeline

#### 4.2.1 Java后端 .gitlab-ci.yml

```yaml
# .gitlab-ci.yml - Java后端服务CI/CD配置
stages:
  - checkout
  - build
  - test
  - package
  - scan
  - build-image
  - deploy-dev
  - deploy-test
  - deploy-uat
  - deploy-prod

variables:
  MAVEN_OPTS: "-Dmaven.repo.local=.m2/repository"
  DOCKER_REGISTRY: "harbor.picchealth.com"
  DOCKER_IMAGE_PREFIX: "picc-mzmtb"

# Maven缓存
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .m2/repository/

# 代码检出
checkout-code:
  stage: checkout
  script:
    - echo "Checking out code..."
    - git checkout -b ${CI_COMMIT_REF_NAME}
  only:
    - develop
    - master
    - develop-*

# 代码编译
maven-build:
  stage: build
  image: maven:3.8-openjdk-8
  script:
    - mvn clean compile -Dmaven.test.skip=true
  artifacts:
    paths:
      - "**/target/**/*.class"
    expire_in: 1 day
  only:
    - develop
    - master
    - develop-*

# 单元测试
maven-test:
  stage: test
  image: maven:3.8-openjdk-8
  script:
    - mvn test -Dtest=*Test
  coverage: '/Total:[^\d]*(\d+)%/'
  artifacts:
    reports:
      junit: "**/target/surefire-reports/TEST-*.xml"
    paths:
      - "**/target/surefire-reports/"
    expire_in: 7 days
  allow_failure: false
  only:
    - develop
    - master
    - develop-*
    - merge_requests

# 代码质量扫描
sonarqube-check:
  stage: scan
  image: maven:3.8-openjdk-8
  script:
    - mvn sonar:sonar -Dsonar.projectKey=${CI_PROJECT_NAME} 
      -Dsonar.host.url=${SONAR_HOST_URL}
      -Dsonar.login=${SONAR_TOKEN}
      -Dsonar.branch.name=${CI_COMMIT_REF_NAME}
  allow_failure: true
  only:
    - develop
    - master
    - develop-*
    - merge_requests

# Maven打包
maven-package:
  stage: package
  image: maven:3.8-openjdk-8
  script:
    - mvn clean package -U -Dmaven.test.skip=true -P${BUILD_PROFILE}
  artifacts:
    paths:
      - "**/target/*.jar"
    expire_in: 7 days
  only:
    - develop
    - master
    - develop-*
  when: manual

# Docker镜像构建 - 权限服务
build-user-image:
  stage: build-image
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker login -u ${DOCKER_USER} -p ${DOCKER_PASSWORD} ${DOCKER_REGISTRY}
    - docker build -t ${DOCKER_REGISTRY}/${DOCKER_IMAGE_PREFIX}/user:${CI_COMMIT_SHA} 
      -f config/docker/prd/Dockerfile .
    - docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE_PREFIX}/user:${CI_COMMIT_SHA}
    - docker tag ${DOCKER_REGISTRY}/${DOCKER_IMAGE_PREFIX}/user:${CI_COMMIT_SHA}
      ${DOCKER_REGISTRY}/${DOCKER_IMAGE_PREFIX}/user:latest
    - docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE_PREFIX}/user:latest
    - docker rmi ${DOCKER_REGISTRY}/${DOCKER_IMAGE_PREFIX}/user:${CI_COMMIT_SHA}
  only:
    - master
  when: manual

# 部署到开发环境
deploy-dev:
  stage: deploy-dev
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context dev-k8s
    - sed -i 's|image:.*|image: ${DOCKER_REGISTRY}/${DOCKER_IMAGE_PREFIX}/user:${CI_COMMIT_SHA}|' 
      k8s/dev/user-deployment.yaml
    - kubectl apply -f k8s/dev/user-deployment.yaml
    - kubectl rollout status deployment/picc-mzmtb-user -n mzmtb-dev
    - kubectl get pods -n mzmtb-dev -l app=picc-mzmtb-user
  only:
    - develop
  when: manual

# 部署到测试环境
deploy-test:
  stage: deploy-test
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context test-k8s
    - kubectl set image deployment/picc-mzmtb-user 
      picc-mzmtb-user=${DOCKER_REGISTRY}/${DOCKER_IMAGE_PREFIX}/user:${CI_COMMIT_SHA}
      -n mzmtb-test
    - kubectl rollout status deployment/picc-mzmtb-user -n mzmtb-test
  only:
    - develop-*
  when: manual

# 部署到UAT环境
deploy-uat:
  stage: deploy-uat
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context uat-k8s
    - kubectl set image deployment/picc-mzmtb-user 
      picc-mzmtb-user=${DOCKER_REGISTRY}/${DOCKER_IMAGE_PREFIX}/user:${CI_COMMIT_SHA}
      -n mzmtb-uat
    - kubectl rollout status deployment/picc-mzmtb-user -n mzmtb-uat
  only:
    - master
  when: manual

# 部署到生产环境
deploy-prod:
  stage: deploy-prod
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context prod-k8s
    - echo "Production deployment requires approval"
    - kubectl set image deployment/picc-mzmtb-user 
      picc-mzmtb-user=${DOCKER_REGISTRY}/${DOCKER_IMAGE_PREFIX}/user:${CI_COMMIT_SHA}
      -n mzmtb-prod
    - kubectl rollout status deployment/picc-mzmtb-user -n mzmtb-prod
    - kubectl annotate deployment/picc-mzmtb-user kubernetes.io/change-cause="Deployed by CI: ${CI_COMMIT_MESSAGE}"
  only:
    - master
  when: manual
  environment:
    name: production
    url: https://mzmtb.picchealth.com
  retry:
    max: 2
    when: runner_system_failure
```

#### 4.2.2 前端 .gitlab-ci.yml

```yaml
# .gitlab-ci.yml - Vue前端CI/CD配置
stages:
  - build
  - test
  - scan
  - build-image
  - deploy-dev
  - deploy-test
  - deploy-uat
  - deploy-prod

variables:
  DOCKER_REGISTRY: "harbor.picchealth.com"
  DOCKER_IMAGE_PREFIX: "picc-mzmtb"

# Node缓存
cache:
  key: ${CI_COMMIT_REF_SLUG}-node
  paths:
    - node_modules/

# 安装依赖
install-dependencies:
  stage: build
  image: node:16-alpine
  script:
    - npm install --registry=https://registry.npmmirror.com
    - npm list --depth=0
  artifacts:
    paths:
      - node_modules/
    expire_in: 1 day
  only:
    - develop
    - master
    - develop-*

# 代码检查
eslint-check:
  stage: test
  image: node:16-alpine
  script:
    - npm run lint
  allow_failure: true
  only:
    - develop
    - master
    - develop-*
    - merge_requests

# 构建测试环境
build-test:
  stage: build
  image: node:16-alpine
  script:
    - npm install --registry=https://registry.npmmirror.com
    - npm run build:test
    - tar -czvf dist-test.tar.gz output/
  artifacts:
    paths:
      - dist-test.tar.gz
    expire_in: 7 days
  only:
    - develop-*
  when: manual

# 构建UAT环境
build-uat:
  stage: build
  image: node:16-alpine
  script:
    - npm install --registry=https://registry.npmmirror.com
    - npm run build:uat
    - tar -czvf dist-uat.tar.gz output/
  artifacts:
    paths:
      - dist-uat.tar.gz
    expire_in: 7 days
  only:
    - master
  when: manual

# 构建生产环境
build-prod:
  stage: build
  image: node:16-alpine
  script:
    - npm install --registry=https://registry.npmmirror.com
    - npm run build:prod
    - tar -czvf dist-prod.tar.gz output/
  artifacts:
    paths:
      - dist-prod.tar.gz
    expire_in: 7 days
  only:
    - master
  when: manual

# 构建Docker镜像
build-frontend-image:
  stage: build-image
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker login -u ${DOCKER_USER} -p ${DOCKER_PASSWORD} ${DOCKER_REGISTRY}
    - docker build -t ${DOCKER_REGISTRY}/${DOCKER_IMAGE_PREFIX}/agent:${CI_COMMIT_SHA}
      -f docker/Dockerfile .
    - docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE_PREFIX}/agent:${CI_COMMIT_SHA}
    - docker tag ${DOCKER_REGISTRY}/${DOCKER_IMAGE_PREFIX}/agent:${CI_COMMIT_SHA}
      ${DOCKER_REGISTRY}/${DOCKER_IMAGE_PREFIX}/agent:latest
    - docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE_PREFIX}/agent:latest
  only:
    - master
  when: manual

# 部署到开发环境
deploy-frontend-dev:
  stage: deploy-dev
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context dev-k8s
    - kubectl set image deployment/picc-mzmtb-agent 
      picc-mzmtb-agent=${DOCKER_REGISTRY}/${DOCKER_IMAGE_PREFIX}/agent:${CI_COMMIT_SHA}
      -n mzmtb-dev
    - kubectl rollout status deployment/picc-mzmtb-agent -n mzmtb-dev
  only:
    - develop
  when: manual

# 部署到测试环境
deploy-frontend-test:
  stage: deploy-test
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context test-k8s
    - kubectl set image deployment/picc-mzmtb-agent 
      picc-mzmtb-agent=${DOCKER_REGISTRY}/${DOCKER_IMAGE_PREFIX}/agent:${CI_COMMIT_SHA}
      -n mzmtb-test
    - kubectl rollout status deployment/picc-mzmtb-agent -n mzmtb-test
  only:
    - develop-*
  when: manual

# 部署到UAT环境
deploy-frontend-uat:
  stage: deploy-uat
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context uat-k8s
    - kubectl set image deployment/picc-mzmtb-agent 
      picc-mzmtb-agent=${DOCKER_REGISTRY}/${DOCKER_IMAGE_PREFIX}/agent:${CI_COMMIT_SHA}
      -n mzmtb-uat
    - kubectl rollout status deployment/picc-mzmtb-agent -n mzmtb-uat
  only:
    - master
  when: manual

# 部署到生产环境
deploy-frontend-prod:
  stage: deploy-prod
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context prod-k8s
    - kubectl set image deployment/picc-mzmtb-agent 
      picc-mzmtb-agent=${DOCKER_REGISTRY}/${DOCKER_IMAGE_PREFIX}/agent:${CI_COMMIT_SHA}
      -n mzmtb-prod
    - kubectl rollout status deployment/picc-mzmtb-agent -n mzmtb-prod
  only:
    - master
  when: manual
  environment:
    name: production
  retry:
    max: 2
```

### 4.3 多环境流水线

#### 4.3.1 环境流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          多环境部署流程                                       │
│                                                                             │
│    开发分支                    主分支                                         │
│   (develop)                  (master)                                        │
│       │                          │                                          │
│       ▼                          ▼                                          │
│  ┌─────────┐               ┌─────────┐                                      │
│  │ DEV环境  │               │ UAT环境  │                                      │
│  │ 自动部署 │               │ 手动部署 │                                      │
│  └────┬────┘               └────┬────┘                                      │
│       │                          │                                          │
│       ▼                          ▼                                          │
│  ┌─────────┐               ┌─────────┐                                      │
│  │ TEST环境  │               │ PROD环境 │                                      │
│  │ 手动部署 │               │ 审批部署 │                                      │
│  └────┬────┘               └────┬────┘                                      │
│       │                          │                                          │
│       └──────────┬──────────────┘                                          │
│                  │                                                          │
│                  ▼                                                          │
│           ┌─────────────┐                                                   │
│           │   回滚机制   │                                                   │
│           └─────────────┘                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 4.3.2 环境差异配置

| 环境 | 代码分支 | 部署方式 | 数据库 | Apollo |
|------|---------|---------|--------|--------|
| **DEV** | develop | 自动 | 开发库 | dev |
| **TEST** | develop-* | 手动 | 测试库 | test |
| **UAT** | master | 手动审批 | UAT库 | uat |
| **PROD** | master | 审批+确认 | 生产库 | prod |

### 4.4 回滚策略

#### 4.4.1 回滚方案

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           回滚策略设计                                        │
│                                                                             │
│  ┌────────────────┐     ┌────────────────┐     ┌────────────────┐          │
│  │   策略一：镜像回滚 │     │  策略二：版本回滚  │     │ 策略三：代码回滚   │          │
│  │                │     │                │     │                │          │
│  │ kubectl set    │     │ helm rollback │     │ git revert     │          │
│  │ image ...       │     │ <release> 1   │     │ <commit>       │          │
│  │ user:previous   │     │                │     │                │          │
│  │                │     │                │     │ → 重新CI/CD     │          │
│  └────────────────┘     └────────────────┘     └────────────────┘          │
│                                                                             │
│  推荐优先级：镜像回滚 > 版本回滚 > 代码回滚                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 4.4.2 快速回滚脚本

```bash
#!/bin/bash
# rollback.sh - 快速回滚脚本

set -e

NAMESPACE=${1:-mzmtb-prod}
SERVICE=${2:-picc-mzmtb-user}
REVISION=${3:-1}

echo "=========================================="
echo "  PICC MZMTB 回滚工具"
echo "  Namespace: $NAMESPACE"
echo "  Service: $SERVICE"
echo "  Revision: $REVISION"
echo "=========================================="

# 回滚Deployment
kubectl rollout undo deployment/${SERVICE} -n ${NAMESPACE} --to-revision=${REVISION}

# 等待回滚完成
echo "等待Pod回滚..."
kubectl rollout status deployment/${SERVICE} -n ${NAMESPACE}

# 验证状态
echo "检查Pod状态..."
kubectl get pods -n ${NAMESPACE} -l app=${SERVICE}

# 健康检查
echo "执行健康检查..."
SERVICE_PORT=$(kubectl get svc ${SERVICE} -n ${NAMESPACE} -o jsonpath='{.spec.ports[0].port}')
POD_IP=$(kubectl get pods -n ${NAMESPACE} -l app=${SERVICE} -o jsonpath='{.items[0].status.podIP}')
curl -f http://${POD_IP}:${SERVICE_PORT}/actuator/health || exit 1

echo ""
echo "=========================================="
echo "  回滚完成！"
echo "=========================================="
```

#### 4.4.3 回滚触发条件

| 场景 | 触发条件 | 自动/手动 |
|------|---------|----------|
| 部署后Pod启动失败 | `kubectl get pods` 显示CrashLoopBackOff | 手动 |
| 健康检查失败 | 连续3次探针检查失败 | 手动 |
| 服务响应超时 | 95%响应时间>30s | 手动 |
| 错误率飙升 | 5xx错误率>5% | 自动 |
| 内存泄漏 | 内存使用率>90%持续5分钟 | 手动 |

---

## Part 5：运维手册

### 5.1 服务启停管理

#### 5.1.1 Java服务管理脚本

```bash
#!/bin/bash
# service-manager.sh - Java服务管理脚本

APP_NAME="picc-mzmtb-user"
JAR_FILE="picchealth-privilege-server-1.0-SNAPSHOT.jar"
APP_PORT="9092"
LOG_FILE="/var/log/${APP_NAME}.log"
PID_FILE="/var/run/${APP_NAME}.pid"

# JVM参数
JAVA_OPTS="-Xmx2048M -Xms2048M -Xmn512M -XX:MaxMetaspaceSize=256M"
JAVA_OPTS="${JAVA_OPTS} -Dsun.net.inetaddr.ttl=60 -Dsun.net.inetaddr.negative.ttl=60"

start() {
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        if kill -0 $PID 2>/dev/null; then
            echo "$APP_NAME is already running (PID: $PID)"
            return 1
        fi
    fi
    
    echo "Starting $APP_NAME..."
    nohup java $JAVA_OPTS -jar $JAR_FILE --spring.profiles.active=prod >> $LOG_FILE 2>&1 &
    echo $! > $PID_FILE
    echo "$APP_NAME started (PID: $(cat $PID_FILE))"
}

stop() {
    if [ ! -f $PID_FILE ]; then
        echo "$APP_NAME is not running"
        return 1
    fi
    
    PID=$(cat $PID_FILE)
    echo "Stopping $APP_NAME (PID: $PID)..."
    
    kill $PID
    sleep 5
    
    if kill -0 $PID 2>/dev/null; then
        echo "Force killing $APP_NAME..."
        kill -9 $PID
    fi
    
    rm -f $PID_FILE
    echo "$APP_NAME stopped"
}

restart() {
    echo "Restarting $APP_NAME..."
    stop
    sleep 3
    start
}

status() {
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        if kill -0 $PID 2>/dev/null; then
            echo "$APP_NAME is running (PID: $PID)"
            return 0
        fi
    fi
    echo "$APP_NAME is not running"
    return 1
}

health_check() {
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${APP_PORT}/actuator/health 2>/dev/null)
    if [ "$RESPONSE" = "200" ]; then
        echo "Health check OK"
        return 0
    else
        echo "Health check FAILED (HTTP: $RESPONSE)"
        return 1
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    health)
        health_check
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|health}"
        exit 1
        ;;
esac
```

#### 5.1.2 使用systemd管理服务

```ini
# /etc/systemd/system/picc-mzmtb-user.service

[Unit]
Description=PICC MZMTB User Service
After=network.target

[Service]
Type=simple
User=app
Group=app
WorkingDirectory=/opt/picc-mzmtb-user
ExecStart=/usr/bin/java -Xmx2048M -Xms2048M -jar picchealth-privilege-server-1.0-SNAPSHOT.jar --spring.profiles.active=prod
ExecStop=/bin/kill -TERM $MAINPID
StandardOutput=append:/var/log/picc-mzmtb-user/output.log
StandardError=append:/var/log/picc-mzmtb-user/error.log
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 使用systemd管理服务
systemctl enable picc-mzmtb-user    # 开机自启
systemctl start picc-mzmtb-user     # 启动
systemctl stop picc-mzmtb-user      # 停止
systemctl restart picc-mzmtb-user    # 重启
systemctl status picc-mzmtb-user     # 状态
journalctl -u picc-mzmtb-user -f    # 日志
```

### 5.2 日志查看与排查

#### 5.2.1 日志文件位置

| 服务 | 日志路径 | 说明 |
|------|---------|------|
| 权限服务 | `/var/log/picc-mzmtb-user/` | 权限服务日志 |
| 业务服务 | `/var/log/picc-mzmtb-server/` | 业务服务日志 |
| 前台服务 | `/var/log/picc-mzmtb-gateway/` | 网关日志 |
| Nginx | `/var/log/nginx/` | 前端访问日志 |
| K8s Pod | `kubectl logs` | 容器内日志 |

#### 5.2.2 日志查看命令

```bash
# 查看实时日志
tail -f /var/log/picc-mzmtb-user/app.log

# 查看最近100行
tail -100 /var/log/picc-mzmtb-user/app.log

# 搜索错误日志
grep -i "ERROR" /var/log/picc-mzmtb-user/app.log | tail -50

# 搜索异常堆栈
grep -A 10 "Exception" /var/log/picc-mzmtb-user/app.log

# 按时间范围查看
sed -n '/2024-01-15 10:00:00/,/2024-01-15 11:00:00/p' /var/log/picc-mzmtb-user/app.log

# K8s日志查看
kubectl logs -f deployment/picc-mzmtb-user -n mzmtb-prod
kubectl logs --previous deployment/picc-mzmtb-user -n mzmtb-prod  # 上一个容器
kubectl logs -l app=picc-mzmtb-user -n mzmtb-prod --tail=100
```

#### 5.2.3 日志分析常用命令

```bash
# 统计错误数量
grep -c "ERROR" /var/log/picc-mzmtb-user/app.log

# 统计访问量
cat access.log | awk '{print $7}' | sort | uniq -c | sort -rn | head -20

# 分析响应时间
grep " completed in " app.log | awk -F'completed in ' '{print $2}' | awk '{sum+=$1; count++} END {print "平均响应时间: " sum/count "ms"}'

# 查看慢查询
grep -i "slow query\|executing\|cost" app.log | head -50

# 分析线程状态
grep "Thread" app.log | grep -i "waiting\|blocked\|runnable" | sort | uniq -c
```

### 5.3 健康检查端点

#### 5.3.1 各服务健康检查URL

| 服务 | 端口 | 健康检查URL | 说明 |
|------|------|------------|------|
| 权限服务 | 9092 | `http://localhost:9092/actuator/health` | 包含DB和Redis健康检查 |
| 业务服务 | 9091 | `http://localhost:9091/actuator/health` | 包含DB和Redis健康检查 |
| 前台服务 | 9001 | `http://localhost:9001/actuator/health` | 网关健康状态 |
| 前端Nginx | 80/443 | `http://localhost/` | 检查首页访问 |

#### 5.3.2 健康检查脚本

```bash
#!/bin/bash
# health-check.sh - 服务健康检查脚本

check_service() {
    local name=$1
    local url=$2
    local timeout=${3:-5}
    
    echo -n "检查 $name ... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time $timeout "$url" 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo "✓ OK"
        return 0
    else
        echo "✗ FAILED (HTTP: $response)"
        return 1
    fi
}

echo "========================================"
echo "  PICC MZMTB 健康检查"
echo "========================================"
echo ""

failed=0

check_service "权限服务" "http://localhost:9092/actuator/health" || ((failed++))
check_service "业务服务" "http://localhost:9091/actuator/health" || ((failed++))
check_service "前台服务" "http://localhost:9001/actuator/health" || ((failed++))
check_service "前端Nginx" "http://localhost/" || ((failed++))

echo ""
echo "========================================"
if [ $failed -eq 0 ]; then
    echo "  全部服务正常"
    exit 0
else
    echo "  $failed 个服务异常"
    exit 1
fi
```

### 5.4 常见部署问题排查

#### 5.4.1 问题排查流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           问题排查流程                                        │
│                                                                             │
│  部署失败/服务异常                                                            │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────┐  是   ┌─────────────┐  是   ┌─────────────┐                │
│  │ Pod运行中？ │ ──→ │ 健康检查通过？│ ──→ │ 端口可访问？ │                │
│  └─────────────┘      └─────────────┘      └─────────────┘                │
│       │ 否                   │ 否                   │ 否                   │
│       ▼                      ▼                      ▼                       │
│  查看Pod事件            检查日志                  检查防火墙                  │
│  kubectl describe      查看应用日志              检查Service配置            │
│       │                      │                      │                       │
│       │                      │                      │                       │
│       ▼                      ▼                      ▼                       │
│  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐               │
│  │ OOMKilled   │       │ 数据库连接失败│       │ 网络策略阻塞 │               │
│  │ → 增加内存  │       │ → 检查配置  │       │ → 调整策略  │               │
│  └─────────────┘       └─────────────┘       └─────────────┘               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 5.4.2 常见问题与解决方案

##### 问题1：Pod启动失败 - CrashLoopBackOff

```bash
# 查看Pod状态
kubectl get pods -n mzmtb-prod | grep picc-mzmtb-user

# 查看详细事件
kubectl describe pod picc-mzmtb-user-xxxx -n mzmtb-prod

# 查看容器日志
kubectl logs picc-mzmtb-user-xxxx -n mzmtb-prod --previous

# 可能原因：
# 1. JVM内存不足 → 调整JVM参数
# 2. 数据库连接失败 → 检查数据库配置
# 3. Apollo配置获取失败 → 检查网络和白名单
# 4. 端口冲突 → 检查端口配置
```

##### 问题2：数据库连接失败

```bash
# 检查数据库连接配置
kubectl exec -it picc-mzmtb-user-xxxx -n mzmtb-prod -- env | grep -i db

# 测试数据库连接
kubectl exec -it picc-mzmtb-user-xxxx -n mzmtb-prod -- nc -zv db-host 5432

# 检查数据库连接池配置
# application-prod.yml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
```

##### 问题3：Apollo配置获取失败

```bash
# 检查Apollo连接
kubectl exec -it picc-mzmtb-user-xxxx -n mzmtb-prod -- curl -v http://apollo-meta:8080

# 检查Apollo配置
kubectl exec -it picc-mzmtb-user-xxxx -n mzmtb-prod -- \
  java -cp app.jar org.springframework.boot.loader.PropertiesLauncher \
  --spring.cloud.config.uri=http://apollo-meta:8080

# 常见原因：
# 1. Apollo地址配置错误
# 2. 网络不通（检查安全组）
# 3. 应用ID未在Apollo注册
# 4. Namespace配置不存在
```

##### 问题4：Nginx 502 Bad Gateway

```bash
# 检查上游服务是否运行
kubectl get pods -n mzmtb-prod -l app=picc-mzmtb-gateway

# 检查Nginx错误日志
kubectl exec -it picc-mzmtb-agent-xxxx -n mzmtb-prod -- \
  tail -50 /var/log/nginx/error.log

# 检查Nginx upstream配置
kubectl exec -it picc-mzmtb-agent-xxxx -n mzmtb-prod -- \
  cat /etc/nginx/conf.d/default.conf

# 测试上游连接
kubectl exec -it picc-mzmtb-agent-xxxx -n mzmtb-prod -- \
  curl -v http://picc-mzmtb-gateway-svc:9001/actuator/health
```

##### 问题5：前端静态资源加载失败

```bash
# 检查Nginx配置中的root路径
# 确认output目录存在且有内容
kubectl exec -it picc-mzmtb-agent-xxxx -n mzmtb-prod -- \
  ls -la /home/front/output/

# 检查index.html是否存在
kubectl exec -it picc-mzmtb-agent-xxxx -n mzmtb-prod -- \
  cat /home/front/output/index.html

# 检查静态文件路径映射
# nginx配置中 location / 指向 /home/front/output
```

##### 问题6：JWT Token验证失败

```bash
# 检查JWT配置
kubectl exec -it picc-mzmtb-user-xxxx -n mzmtb-prod -- \
  grep -r "jwt\|token" /app/config/

# 检查密钥配置（敏感信息已在Apollo加密）
# 检查Token过期时间
# 检查签名算法
```

#### 5.4.3 性能问题排查

```bash
# 查看CPU和内存使用
kubectl top pods -n mzmtb-prod

# 查看JVM内存使用
kubectl exec -it picc-mzmtb-server-xxxx -n mzmtb-prod -- \
  jstat -gc $(jps | grep jar | awk '{print $1}')

# 查看线程信息
kubectl exec -it picc-mzmtb-server-xxxx -n mzmtb-prod -- \
  jstack $(jps | grep jar | awk '{print $1}') | head -100

# 查看GC日志
kubectl exec -it picc-mzmtb-server-xxxx -n mzmtb-prod -- \
  cat /app/logs/gc.log
```

---

## 附录：快速参考

### A.1 快速部署命令

```bash
# 1. 拉取代码
git clone https://gitlab.picchealth.com/picc-mzmtb/picc-mzmtb-user.git
git clone https://gitlab.picchealth.com/picc-mzmtb/picc-mzmtb-server.git
git clone https://gitlab.picchealth.com/picc-mzmtb/picc-mzmtb-gateway.git
git clone https://gitlab.picchealth.com/picc-mzmtb/picc-mzmtb-agent.git

# 2. Maven构建
cd picc-mzmtb-server
mvn clean package -Dmaven.test.skip=true

# 3. 前端构建
cd picc-mzmtb-agent
npm install
npm run build:prod

# 4. Docker镜像构建
docker build -t harbor.picchealth.com/picc-mzmtb/server:1.0.0 .

# 5. 推送镜像
docker push harbor.picchealth.com/picc-mzmtb/server:1.0.0

# 6. K8s部署
kubectl apply -f k8s/prod/
```

### A.2 常用端口汇总

| 服务 | 内部端口 | 外部端口 | 协议 | 用途 |
|------|---------|---------|------|------|
| 前端Nginx | 80/443 | 80/443 | HTTP/HTTPS | Web访问 |
| 前台服务 | 9001 | 9001 | HTTP | API网关 |
| 业务服务 | 9091 | 9091 | HTTP | 业务API |
| 权限服务 | 9092 | 9092 | HTTP | 权限API |
| Apollo | 8080 | - | HTTP | 配置中心 |
| 数据库 | 5432 | - | PostgreSQL | 数据存储 |
| Redis | 6379 | - | TCP | 缓存 |

### A.3 环境变量快速参考

| 变量名 | 说明 | 示例值 |
|-------|------|-------|
| `SPRING_PROFILES_ACTIVE` | 激活的环境 | `prod` |
| `APOLLO_META` | Apollo元服务器地址 | `http://apollo-meta:8080` |
| `DB_HOST` | 数据库主机 | `postgres-db` |
| `DB_PASSWORD` | 数据库密码 | `***` |
| `REDIS_HOST` | Redis主机 | `redis-cluster` |
| `JAVA_OPTS` | JVM参数 | `-Xmx2048M -Xms2048M` |

### A.4 紧急联系人

| 角色 | 职责 | 联系方式 |
|------|------|---------|
| 运维负责人 | 基础设施问题 | [待填写] |
| 开发负责人 | 应用问题 | [待填写] |
| DBA | 数据库问题 | [待填写] |
| 安全负责人 | 安全事件 | [待填写] |

---

## 📝 文档维护

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|---------|
| 1.0 | 2024 | PICC DevOps Team | 初始版本 |

---

**注意**: 本文档中的敏感信息（如IP地址、密码、密钥等）已进行脱敏处理，请勿在生产环境中使用示例值。如有问题，请联系运维团队。
