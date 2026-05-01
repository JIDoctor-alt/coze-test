# PICC 权限管理系统 - 配置文件 / 部署 / 依赖 小白解析

---

## ⚙️ 配置文件 - 系统怎么启动

> 🏠 配置文件就像公司的**规章制度手册**：告诉系统用什么端口、连什么数据库、开什么功能。

### application.yml - 主配置（总规章制度）

| 配置项 | 值 | 含义 | 生活比喻 |
|--------|-----|------|----------|
| server.port | 9092 | 服务端口号 | 公司的门牌号 |
| spring.profiles.active | dev | 当前使用哪套环境配置 | 用哪个分公司的制度 |
| spring.application.name | picc-mzmtb-user | 服务名称 | 公司注册名 |
| apollo.bootstrap.enabled | true | 启用Apollo配置中心 | 用集团统一制度管理平台 |
| apollo.bootstrap.eagerLoad.enabled | true | 启动阶段就加载配置 | 开门前先把制度贴好 |

> 💡 **Apollo配置中心**：人保的统一配置管理平台。就像集团的制度发布平台，不用改代码就能调整配置。本地yml只写基础信息，详细配置都在Apollo上。

### 各环境配置对比

| 环境 | 文件 | Apollo命名空间 | Apollo地址 | 说明 |
|------|------|----------------|------------|------|
| dev（开发） | application-dev.yml | application-local.properties | 10.57.16.41:8080 | 程序员本地开发用 |
| test（测试） | application-test.yml | application-test.properties | 10.57.16.41:8080 | 测试团队验证用 |
| uat（验收） | application-uat.yml | application-uat.properties | 10.57.16.41:8080 | 业务人员验收用 |
| prod（生产） | application-prod.yml | application.properties | 10.34.80.145:8080 | 真正对外服务的环境 |

> 💡 注意：生产环境的Apollo地址不同（北中心），说明是独立的配置中心实例，和生产环境物理隔离。

### bootstrap.yml - 启动引导配置

> 🏠 就像开业前要先办**营业执照**，bootstrap.yml在Spring Boot正式启动前就加载

```yaml
spring:
  application:
    name: picc-mzmtb-user
server:
  port: 9092
```

> 💡 bootstrap.yml 比 application.yml 更早加载，主要用来配置Apollo等需要在启动阶段就准备好的东西。

### logback-spring.xml - 日志配置

> 🏠 就像公司装的**监控摄像头**，记录谁什么时候干了什么

| 配置项 | 值 | 含义 |
|--------|-----|------|
| LOG_HOME | /data/log/app | 日志存放目录 |
| MAX_FILE_SIZE | 100MB | 单个日志文件最大100MB |
| MAX_HISTORY | 7 | 保留7天日志 |
| TOTAL_SIZE_CAP | 500MB | 日志总共最多占500MB |
| 日志格式 | [时间][线程][级别][traceId][主机][服务名][类名][消息] | 包含全链路追踪信息 |

> 💡 日志里带了 `pGlobalTraceId`、`pParentTraceId`、`pLocalTraceId`，这是微服务全链路追踪三件套：就像快递的"始发站→中转站→终点站"追踪码。

### app.properties - Apollo应用标识

```properties
app.id=@app.id@
apollo.meta=@meta@
```
> 这里的 `@xxx@` 是Maven编译时替换的占位符，构建时自动填入实际值。

---

## 📦 项目依赖 - 用了什么库

> 🏠 pom.xml就像公司的**采购清单**，列出了项目需要引入的所有工具和组件

### 技术栈总览

| 技术 | 版本 | 干嘛的 | 生活比喻 |
|------|------|--------|----------|
| Java | 8 | 编程语言 | 工作语言 |
| pdfc-parent | 4.2.6.0 | 人保统一开发框架 | 公司标准工装 |
| Spring Cloud | (由pdfc管理) | 微服务框架 | 集团办公系统 |
| MyBatis | (由pdfc-mybatis管理) | 数据库操作框架 | 仓库管理员 |
| Apollo | (由pdfc-config管理) | 配置中心 | 集团制度发布平台 |
| Redis/Redisson | 3.13.4 | 缓存+分布式锁 | 冰箱+门锁 |
| Druid | 1.0.11 | 数据库连接池 | 银行窗口排队系统 |
| GaussDB | 3.0.0-spc1000 | 华为高斯数据库 | 仓库（华为牌） |
| FastJSON | 1.2.72 | JSON处理 | 翻译官（中英互译） |
| Knife4j | 2.0.0 | API文档工具 | 接口说明书 |
| Lombok | 1.18.30 | 代码简化工具 | 自动填表机 |
| j2cache | 2.7.7 | 两级缓存框架 | 冰箱+冷冻库 |
| BES（宝兰德） | 9.5.5.007 | 国产中间件服务器 | 国产办公大楼 |
| Log4j | 1.2.13 | 日志框架 | 监控录像机 |

### 关键依赖解释

**1. pdfc-parent（统一开发框架）**
> 🏠 就像集团统一采购的办公套件：办公桌、电脑、电话都标准化了，所有分公司用同一套。

**2. GaussDB（华为高斯数据库）**
> 🏠 就像华为牌仓库：不是常见的MySQL/Oracle，而是国产数据库。人保作为国企，用国产数据库是信创要求。

**3. Redisson（分布式锁+缓存）**
> 🏠 Redisson = Redis的加强版：除了当冰箱存东西，还能当"公共厕所锁"（分布式锁），保证同一时间只有一个操作在执行。

**4. BES（宝兰德应用服务器）**
> 🏠 就像国产办公大楼：替代Tomcat的国产中间件，同样是信创要求。注意pom里排除了Tomcat依赖。

**5. j2cache（两级缓存）**
> 🏠 就像冰箱+冷冻库：第一级是本地缓存（冰箱，快但容量小），第二级是Redis（冷冻库，稍慢但容量大），配合使用性能最优。

**6. Knife4j（API文档）**
> 🏠 就像接口说明书：自动生成所有API的在线文档，前端同事可以在线查看和调试，不用每次问后端。

---

## 🐳 部署配置 - 怎么上线

> 🏠 部署就像开连锁店：需要统一装修方案、分配合适的场地、办各种手续

### K8s部署概述

项目在 `config/kubeconfig/` 下有3个K8s配置文件：

| 文件 | 用途 |
|------|------|
| ns-jczx-tyfwzt-dev.yaml | 开发环境K8s配置 |
| ns-jczx-tyfwzt.yaml | 标准环境K8s配置 |
| p-ns-jczx-tyfwzt.yaml | 生产环境K8s配置 |

> `jczx-tyfwzt` = 基础中心-统一服务中台（拼音缩写）

### 部署流程（小白版）

```
1. 程序员写好代码，推送到阿里云Codeup
         ↓
2. CI/CD流水线自动构建（mvn package打jar包）
         ↓
3. 制作Docker镜像（把jar包塞进容器）
         ↓
4. 推送到人保私有镜像仓库
         ↓
5. 通过K8s配置部署到对应环境（dev/test/uat/prod）
         ↓
6. 服务启动，连接Apollo拉取配置，注册到注册中心
         ↓
7. 对外提供服务（端口9092）
```

---

## 🧪 测试 - 怎么验证

> 🏠 测试就像出厂前的**质量检验**，确保迁移功能不会出问题

### 测试类：PrivilegeMoveTest

这是唯一的测试类，专门测试数据迁移功能。

#### 测试方法列表

| 方法 | 测试什么 | 是否危险 |
|------|----------|----------|
| move() | 角色数据迁移 | ⚠️ 会往数据库写数据 |
| moveUserRole() | 用户角色关系迁移 | ⚠️ 会往数据库写数据 |
| passwordBackMD5() | 密码RSA解密→MD5回退 | ⚠️ 会修改用户密码 |

#### 测试详解

**1. move() - 角色迁移测试**
- 从旧表 `sys_role_module_rel` 读取角色和资源数据
- 按角色编码去重（同一角色在不同机构下需要拆分）
- 写入新表 `privilege_role_info` 和 `privilege_role_resource`
- 关键逻辑：相同code的角色会被赋予不同的ID，按序号递增

**2. moveUserRole() - 用户角色迁移测试**
- 必须在 `move()` 之后执行（因为角色ID已经变了）
- 从旧表 `sys_user_role_rel` 读取用户角色关系
- 通过"用户→机构ID"和"旧角色→新角色code"找到新的角色ID
- 写入新表 `privilege_user_role_info`

**3. passwordBackMD5() - 密码回退测试**
- 读取所有用户的RSA加密密码
- 用RSA私钥解密
- 把解密后的明文密码直接存回数据库（实际是MD5值）
- 解密失败的跳过

> ⚠️ **警告**：这些测试不是单元测试，是数据迁移工具！执行时会直接修改数据库，千万不要在测试/生产环境随便跑！

---

## 🔗 完整项目架构总结

```
┌─────────────────────────────────────────────────────┐
│  前端页面 (Vue/React)                                │
│  用户管理 | 机构管理 | 角色管理 | 菜单管理 | 系统管理   │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP POST (所有接口都是POST)
┌──────────────────────▼──────────────────────────────┐
│  API层 (@RestController)                             │
│  UserInfoApi | OrgInfoApi | RoleInfoApi | MenuInfoApi │
│  + @ApiInterceptor (Token验证 + 权限检查)             │
└──────────────────────┬──────────────────────────────┘
┌──────────────────────▼──────────────────────────────┐
│  Service层 (业务逻辑)                                │
│  UserInfoServiceImpl | OrgInfoServiceImpl | ...       │
│  + @Transactional (事务控制)                          │
│  + BeanUtils.copyProperties (对象转换)                 │
└──────────────────────┬──────────────────────────────┘
┌──────────────────────▼──────────────────────────────┐
│  DAO层 (MyBatis Mapper)                              │
│  XML定义SQL → 操作GaussDB数据库                       │
│  + 动态SQL (<if>/<foreach>)                          │
│  + 逻辑删除 (delete_at IS NULL)                       │
└──────────────────────┬──────────────────────────────┘
┌──────────────────────▼──────────────────────────────┐
│  GaussDB数据库 (华为高斯DB)                           │
│  privilege_user_info / org_info / role_info / menu    │
│  org_system / role_resource / menu_service / ...      │
└─────────────────────────────────────────────────────┘

外部依赖：
  Apollo配置中心 → 统一管理所有环境配置
  Redis/Redisson → 缓存 + 分布式锁
  K8s → 容器化部署
  BES宝兰德 → 国产应用服务器
```

---

📎 **延伸阅读**：
- [架构设计文档](picc-mzmtb-user-架构设计文档.md) - 完整的技术架构、信创适配、Maven依赖版本
- [Onboarding手册](picc-mzmtb-user-Onboarding手册.md) - 本地开发环境搭建、Git克隆、K8s部署配置
- [深度解析](picc-mzmtb-user-深度解析.md) - 安全机制、Token校验、三道认证关卡的详细说明



---

## 十一、application.yml配置项详解（逐项小白化解释）

> 🏠 application.yml就像公司的详细规章制度——每个配置项都规定了一件事该怎么办

### 完整配置项及解释

```yaml
# ==================== 服务基础配置 ====================

server:
  port: 9092                    # 🏠 公司的门牌号：服务监听哪个端口
  
spring:
  profiles:
    active: dev                # 🏠 用哪个分公司的制度：dev/test/uat/prod
    
  application:
    name: picc-mzmtb-user      # 🏠 公司注册名：服务的唯一标识

# ==================== Apollo配置中心 ====================
apollo:
  bootstrap:
    enabled: true               # 🏠 是否启用Apollo：true=用集团制度管理平台，false=用本地制度
    eagerLoad:
      enabled: true             # 🏠 是否提前加载：true=开门前先把制度贴好
    
# ==================== 数据源配置（Apollo中） ====================
# 以下配置通常在Apollo的application.properties中

spring:
  datasource:
    url: jdbc:postgresql://host:port/database
    # 🏠 仓库地址：GaussDB数据库的连接地址
    # 格式：jdbc:postgresql://服务器IP:5432/数据库名
    # 生产环境：10.34.80.145:5432/picc_health_prod
    
    username: postgres
    # 🏠 仓库管理员账号：数据库用户名
    
    password: xxxxxx
    # 🏠 仓库管理员密码：数据库密码（SM4加密存储）
    
    driver-class-name: org.postgresql.Driver
    # 🏠 钥匙型号：连接PostgreSQL/GaussDB的驱动类
    
    type: com.alibaba.druid.pool.DruidDataSource
    # 🏠 排队方式：Druid连接池，不是银行叫号机而是窗口排队
    
    druid:
      initial-size: 5           # 🏠 开业窗口数：初始连接数
      min-idle: 5               # 🏠 最少窗口数：最小保持连接数
      max-active: 20            # 🏠 最多窗口数：最大连接数
      max-wait: 60000           # 🏠 最长等待时间：60秒等不到窗口就放弃

# ==================== Redis配置（Apollo中） ====================
redis:
  host: 127.0.0.1               # 🏠 冰箱地址：Redis服务器IP
  port: 6379                    # 🏠 冰箱门号：Redis端口
  
  password:                     # 🏠 冰箱密码：如果Redis设置了密码就填这里
  
  timeout: 3000                 # 🏠 送取东西的超时时间：3秒
  
  database: 0                    # 🏠 冰箱第几层：Redis第几个数据库（0-15）
  
  lettuce:
    pool:
      max-active: 8             # 🏠 最多8个人同时开冰箱门
      max-idle: 8               # 🏠 冰箱里最多放8样东西
      min-idle: 0               # 🏠 冰箱里最少放0样东西
      max-wait: -1              # 🏠 等不到冰箱就死等（-1表示无限等待）

# ==================== MyBatis配置（Apollo中） ====================
mybatis:
  mapper-locations: classpath:mapper/**/*.xml
  # 🏠 找SQL的路径：在哪些目录下找MyBatis的XML映射文件
  
  type-aliases-package: com.picchealth.module.**.po
  # 🏠 PO类的简写：在哪些包下可以用简写的类名
  
  configuration:
    map-underscore-to-camel-case: true
    # 🏠 命名转换：true=数据库的下划线转Java的驼峰（create_time→createTime）
    
    log-impl: org.apache.ibatis.logging.slf4j.Slf4jImpl
    # 🏠 SQL日志用哪种：Sl4j日志框架

# ==================== 分页插件 ====================
pagehelper:
  helper-dialect: postgresql     # 🏠 分页语法用哪种：PostgreSQL语法
  reasonable: true              # 🏠 页码纠错：pageNum<=0时变成1
  support-methods-arguments: true
  # 🏠 支持方法参数分页：可以用Controller参数直接分页

# ==================== 日志配置 ====================
logging:
  level:
    root: INFO                  # 🏠 基础日志级别：INFO以上才显示
    com.picchealth: DEBUG       # 🏠 我们项目日志级别：DEBUG以上都显示
    com.ctrip.framework.apollo: WARN
    # 🏠 Apollo的日志：只显示警告以上（减少噪音）
```

---

## 十二、bootstrap.yml配置项详解

> 🏠 bootstrap.yml就像"开业前准备"——在Spring Boot正式启动之前就要加载

### 完整配置项及解释

```yaml
# bootstrap.yml - 在application.yml之前加载，用于配置Apollo等早期组件

server:
  port: 9092
  # 🏠 门牌号：这个必须写在bootstrap里，因为启动阶段就需要知道端口

spring:
  application:
    name: picc-mzmtb-user
    # 🏠 公司注册名：告诉Apollo这是哪个应用
  
  profiles:
    active: dev
    # 🏠 当前环境：dev/test/uat/prod
    # 注意：这个配置有优先级问题
    # - 如果写在bootstrap.yml：所有环境共用
    # - 如果写在application.yml：可以按环境拆分

# Apollo配置（如果没写在application.yml里的话）
apollo:
  meta: http://apollo-meta:8080
  # 🏠 Apollo配置中心地址（K8s内部用服务名）
  # 本地开发：http://10.57.16.41:8080
  # 生产：http://10.34.80.145:8080
  
  bootstrap:
    enabled: true
    # 🏠 启动时加载Apollo：必须在bootstrap阶段加载，不然拿不到数据库配置
```

### bootstrap和application的区别

| 场景 | 用bootstrap.yml | 用application.yml |
|------|----------------|-------------------|
| Apollo配置 | ✅ 必须 | ❌ 太晚了 |
| 服务端口 | ✅ 需要提前知道 | ✅ 也可以 |
| 日志配置 | ❌ 没必要 | ✅ 可以 |
| 自定义业务配置 | ❌ 没必要 | ✅ 可以 |

```java
// 加载顺序（Spring Boot启动流程）
// 1. SpringApplication.run() 开始
// 2. bootstrap.yml 加载 ← Apollo配置在这里
// 3. application.yml 加载 ← 业务配置在这里
// 4. 应用主类初始化
// 5. Bean创建
```

---

## 十三、logback-spring.xml日志配置详解

> 🏠 logback-spring.xml就像公司的监控摄像头系统——记录每个人什么时候干了什么

### 日志文件分类

| 日志文件 | 记录什么 | 文件名示例 |
|---------|---------|-----------|
| **syslog** | 系统日志（所有日志） | sys_log-picc-mzmtb-user-*.log |
| **aoplog** | AOP切面日志（方法调用） | aoplog-picc-mzmtb-user-*.log |
| **interface** | 接口调用日志（前后端交互） | interface-picc-mzmtb-user-*.log |
| **error** | 错误日志（只记录ERROR） | error-picc-mzmtb-user-*.log |

### 日志存储策略

```xml
<!-- PaaS平台日志存储（K8s临时存储） -->
<property name="LOG_HOME" value="/data/log/app"/>
<!-- 特点：重启后可能丢失，仅用于临时调试 -->

<!-- NAS存储（持久化存储） -->
<property name="LOG_FILE" value="/data/logs/path"/>
<!-- 特点：持久化，不会丢失，适合长期保存 -->
```

### 日志滚动策略

```xml
<!-- 单个文件最大100MB -->
<property name="MAX_FILE_SIZE" value="100MB"/>

<!-- 保留7天（PaaS存储）/ 180天（NAS存储） -->
<property name="MAX_HISTORY" value="7"/>  <!-- PaaS -->
<maxHistory>180</maxHistory>            <!-- NAS -->

<!-- 日志总大小上限500MB -->
<property name="TOTAL_SIZE_CAP" value="500MB"/>
```

### 日志格式解读

```
# syslog格式示例
[2024-03-15 10:30:45.123] [http-nio-9092-exec-1] [INFO] [001] 
[DESKTOP-DV52DQ8/169.254.123.105] [picc-mzmtb-user] 
[com.picchealth.module.sys.service.impl.UserInfoServiceImpl] 
[g-abc123] [p-parent456] [p-local789] [用户张三登录成功]
```

| 部分 | 含义 |
|------|------|
| `[2024-03-15 10:30:45.123]` | 时间戳 |
| `[http-nio-9092-exec-1]` | 线程名 |
| `[INFO]` | 日志级别 |
| `[DESKTOP-DV52DQ8/169.254.123.105]` | 主机名/IP |
| `[picc-mzmtb-user]` | 服务名 |
| `[com.picchealth...]` | 类名 |
| `[g-abc123]` | 全局追踪ID |
| `[p-parent456]` | 父追踪ID |
| `[p-local789]` | 本地追踪ID |
| `[用户张三登录成功]` | 日志内容 |

### 日志级别说明

| 级别 | 含义 | 使用场景 |
|------|------|---------|
| **TRACE** | 追踪，最详细 | 调试时用，会产生大量日志 |
| **DEBUG** | 调试信息 | 开发时用，生产不建议开 |
| **INFO** | 一般信息 | 生产默认，记录正常流程 |
| **WARN** | 警告 | 有问题但不影响功能 |
| **ERROR** | 错误 | 需要处理的异常 |

### 如何调整日志级别

```bash
# 方式1：在Apollo配置中心修改（推荐，无需重启）
logging.level.root = INFO
logging.level.com.picchealth = DEBUG
logging.level.com.picchealth.module.sys.service.impl = TRACE  # 某个类的详细日志

# 方式2：临时通过URL调整（需要 actuator）
curl -X "POST" "http://localhost:9092/actuator/loggers/com.picchealth" \
  -H "Content-Type: application/json" \
  -d "{\"configuredLevel\": \"DEBUG\"}"

# 方式3：修改logback-spring.xml（需要重启）
```

---

## 十四、Apollo配置中心详解

> 🏠 Apollo就像集团的制度发布平台——所有配置集中管理，改完发布就生效

### Apollo地址和环境

| 环境 | Apollo地址 | AppId | 用途 |
|------|----------|-------|------|
| dev | http://10.57.16.41:8080 | picc-mzmtb-user | 开发环境 |
| test | http://10.57.16.41:8080 | picc-mzmtb-user | 测试环境 |
| uat | http://10.57.16.41:8080 | picc-mzmtb-user | 验收环境 |
| prod | http://10.34.80.145:8080 | picc-mzmtb-user | 生产环境 |

> 💡 注意：生产环境的Apollo是独立的（北中心），和开发/测试的物理隔离

### Apollo配置命名空间

| 命名空间 | 存储内容 |
|---------|---------|
| application | 主配置（数据库、Redis、MyBatis等） |
| application-dev.properties | 开发环境专用配置 |
| application-test.properties | 测试环境专用配置 |
| application-uat.properties | 验收环境专用配置 |
| application-prod.properties | 生产环境专用配置 |

### Apollo配置项清单

```properties
# ==================== 数据源 ====================
spring.datasource.url=jdbc:postgresql://10.34.80.145:5432/picc_health
spring.datasource.username=postgres
spring.datasource.password=SM4加密的密码

# ==================== Redis ====================
redis.host=10.34.80.146
redis.port=6379
redis.password=redis密码

# ==================== RSA密钥（数据迁移用） ====================
rsa.publicEncryptKey=MIGfMA0GCSq...（公钥）
rsa.privateDecryptKey=MIICdQIBAD...（私钥）

# ==================== 日志级别 ====================
logging.level.com.picchealth=INFO
logging.level.org.mybatis=DEBUG

# ==================== 其他配置 ====================
# 密码策略
defaultPassWord=PICChealth@2020
# 用户默认密码，新用户创建时使用
```

### Apollo配置发布流程

```
1. 登录Apollo（需要内网VPN）
   地址：http://10.57.16.41:8080
   
2. 选择应用和环境
   应用：picc-mzmtb-user
   环境：DEV（开发）/ TEST（测试）
   
3. 修改配置
   在application或对应的properties中修改
   
4. 提交 + 发布（重要！）
   - 填写发布说明
   - 点击"发布"按钮
   - 不点发布，配置不会生效！
   
5. 服务自动拉取新配置
   Apollo会通知服务有新配置
   如果没生效，重启服务
```

### Apollo常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 连接超时 | VPN未连接 | 先连VPN |
| 配置不生效 | 没点发布 | 点击发布按钮 |
| 配置不生效 | 服务没拉取 | 重启服务 |
| 读取不到配置 | namespace写错了 | 检查namespace名称 |
| 配置覆盖 | 多处配置了同一个key | 优先级：私有配置 > 公共配置 |

---

## 十五、K8s部署配置详解

> 🏠 K8s就像连锁店管理系统——标准化复制、快速部署、自动扩缩容

### K8s核心概念速解

| 概念 | 生活比喻 | 作用 |
|------|---------|------|
| **Deployment** | 开店计划书 | 定义有多少个副本、如何更新 |
| **Pod** | 具体的店 | K8s运行的最小单元 |
| **Service** | 招商部门 | 对外提供稳定服务 |
| **Ingress** | 大楼前台 | 外部访问入口 |
| **Namespace** | 商场楼层 | 资源隔离 |

### 本项目K8s配置文件

```
config/kubeconfig/
├── ns-jczx-tyfwzt-dev.yaml    # 开发环境（1个副本）
├── ns-jczx-tyfwzt.yaml        # 标准环境（多副本）
└── p-ns-jczx-tyfwzt.yaml      # 生产环境（高可用）
```

### Deployment配置解读

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hmlink-server           # 部署名称
  namespace: ns-jczx-tyfwzt-dev # 所属命名空间
spec:
  replicas: 1                   # 🏠 几家分店：Pod副本数量
  selector:
    matchLabels:
      app: hmlink-server        # 标签选择器
  strategy:
    type: RollingUpdate         # 🏠 更新策略：滚动更新
    rollingUpdate:
      maxSurge: 2              # 最多超出几个新Pod
      maxUnavailable: 2        # 最多不可用几个Pod
  minReadySeconds: 5            # 🏠 开业前检查：就绪后等5秒
  template:
    metadata:
      labels:
        app: hmlink-server     # Pod标签
    spec:
      containers:
        - name: hmlink-server
          image: harbortest.picchealth.com/hb-jczx-tyfwzt-dev/hmlink-server
          # 🏠 容器镜像地址
          ports:
            - containerPort: 9060  # 🏠 店内门牌号
          resources:
            limits:                # 🏠 最高配置
              cpu: "4"             # 最多4核CPU
              memory: 4096Mi       # 最多4GB内存
            requests:              # 🏠 最低配置
              cpu: "2"             # 至少2核CPU
              memory: 2048Mi       # 至少2GB内存
          volumeMounts:            # 🏠 挂载存储
            - mountPath: /logs
              name: xxx-logs
            - mountPath: /upload
              name: xxx-upload
```

### Service配置解读

```yaml
apiVersion: v1
kind: Service
metadata:
  name: hmlink-server
  namespace: ns-jczx-tyfwzt-dev
spec:
  type: NodePort               # 🏠 访问方式：NodePort
  selector:
    app: hmlink-server         # 关联哪个Pod
  ports:
    - name: http
      port: 9060               # 🏠 对外端口（Service端口）
      targetPort: 9060         # 🏠 Pod端口（容器端口）
      protocol: TCP
      nodePort: 32060          # 🏠 外部访问端口（NodePort）
```

### 资源限制说明

```bash
# resources.limits = 最高配置，Pod不能超过这个值
# - 超过会被限流或杀掉
# - 生产环境应该设置，避免一个服务拖垮整个集群

# resources.requests = 最低配置，调度时会看这个
# - K8s调度Pod时会根据这个分配节点
# - 设置太低可能导致Pod分配到资源不足的节点

# 建议配置：
# requests: 实际需要的1.5倍
# limits: requests的2倍
```

### 存储挂载说明

```yaml
volumes:
  - name: xxx-logs
    nfs:
      server: 10.252.68.161    # NFS服务器IP
      path: /nfs/logs          # 共享目录路径
```

| 挂载点 | 用途 | 说明 |
|-------|------|------|
| /logs | 日志输出 | 需要持久化存储 |
| /upload | 文件上传 | 上传的文件需要持久化 |

### 常用K8s命令

```bash
# 查看Pod状态
kubectl get pods -n ns-jczx-tyfwzt-dev

# 查看Pod日志
kubectl logs -f hmlink-server-xxx -n ns-jczx-tyfwzt-dev

# 进入Pod内部
kubectl exec -it hmlink-server-xxx -n ns-jczx-tyfwzt-dev -- /bin/bash

# 扩容Pod
kubectl scale deployment hmlink-server -n ns-jczx-tyfwzt-dev --replicas=3

# 重启Pod
kubectl rollout restart deployment hmlink-server -n ns-jczx-tyfwzt-dev

# 查看Service
kubectl get svc -n ns-jczx-tyfwzt-dev
```

---

## 十六、Dockerfile详解

> 🏠 Dockerfile就像奶茶店的配方——告诉Docker怎么制作这个应用的容器

### 开发环境Dockerfile

```dockerfile
# 基础镜像：Java 1.8运行环境
FROM harbortest.picchealth.com/hb-jczx-tyfwzt-dev/java:1.8

# 临时目录
VOLUME /tmp

# 添加jar包到容器
ADD link-server-1.0.0.jar /link-server.jar

# 保持jar文件更新时间（避免有些框架基于时间判断启动）
RUN bash -c 'touch /link-server.jar'

# 设置时区
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' > /etc/timezone

# 暴露端口
EXPOSE 9081

# 启动命令
ENTRYPOINT ["java","-Dsun.net.inetaddr.ttl=60","-Dsun.net.inetaddr.negative.ttl=60","-jar","/link-server.jar"]
```

### Dockerfile指令解释

| 指令 | 作用 | 注意事项 |
|------|------|---------|
| FROM | 基础镜像 | 不要改，用人保镜像仓库的 |
| VOLUME | 声明挂载点 | 让K8s知道哪些目录要持久化 |
| ADD | 复制文件 | 源文件相对于构建目录 |
| RUN | 执行命令 | 尽量合并，减少层数 |
| EXPOSE | 声明端口 | 只是声明，实际用K8s的端口 |
| ENTRYPOINT | 启动命令 | jar包路径要和ADD的一致 |

### 构建Docker镜像

```bash
# 1. 编译打包
mvn clean package -DskipTests

# 2. 构建镜像
docker build -t picchealth/picc-mzmtb-user:1.0.0 .

# 3. 推送镜像仓库
docker push picchealth/picc-mzmtb-user:1.0.0

# 4. 在K8s中更新镜像版本
kubectl set image deployment/hmlink-server hmlink-server=picchealth/picc-mzmtb-user:1.0.0 -n ns-jczx-tyfwzt-dev
```

---

## 十七、CI/CD流程详解

> 🏠 CI/CD就像流水线生产——代码提交后自动完成构建、测试、部署

### 完整流程图

```
┌─────────────────────────────────────────────────────────────────────┐
│                           CI/CD流水线                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  代码提交 ──► 单元测试 ──► 构建jar ──► 构建镜像 ──► 推送镜像 ──► 部署  │
│    │          │          │          │          │          │        │
│    ▼          ▼          ▼          ▼          ▼          ▼        │
│  Git提交    Mvn Test   Mvn Package  Docker Build  Harbor   K8s部署   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 各环节详解

#### 1. 代码提交

```bash
# 开发者提交代码到阿里云Codeup
git add .
git commit -m "feat: 新增xxx功能"
git push origin feature/xxx
```

#### 2. 单元测试（Maven Test）

```bash
# CI服务器自动执行
mvn test

# 测试内容：
# - 单元测试类 PrivilegeMoveTest
# - 代码质量检查（可选）
# - 覆盖率检查（可选）
```

#### 3. 构建jar包（Maven Package）

```bash
# 跳过测试打包
mvn clean package -DskipTests

# 产出：
# picchealth-privilege-server/target/picchealth-privilege-server.jar
```

#### 4. 构建Docker镜像

```bash
# 使用流水线工具（Jenkins/GitLab CI等）
docker build -t picchealth/picc-mzmtb-user:1.0.0 .

# 多阶段构建示例（如果需要）
# FROM maven:3.8 AS builder
# RUN mvn clean package
# FROM openjdk:8-jre
# COPY --from=builder target/*.jar app.jar
```

#### 5. 推送镜像仓库

```bash
# 推送到人保私有镜像仓库Harbor
docker push harbortest.picchealth.com/hb-jczx-tyfwzt-dev/picc-mzmtb-user:1.0.0

# 镜像标签格式：
# harbortest.picchealth.com = 人保镜像仓库
# hb-jczx-tyfwzt-dev = 项目/环境目录
# picc-mzmtb-user = 镜像名
# 1.0.0 = 版本号
```

#### 6. K8s部署

```bash
# 方式1：手动部署（测试用）
kubectl apply -f ns-jczx-tyfwzt-dev.yaml -n ns-jczx-tyfwzt-dev

# 方式2：自动部署（流水线触发）
# 流水线执行 kubectl set image 命令更新镜像版本

# 方式3：滚动更新（不中断服务）
kubectl rollout restart deployment/hmlink-server -n ns-jczx-tyfwzt-dev
```

### 环境对应关系

| 环境 | K8s Namespace | 镜像仓库 | Apollo |
|------|--------------|---------|--------|
| dev | ns-jczx-tyfwzt-dev | harbortest.xxx/dev/ | DEV |
| sit | ns-jczx-tyfwzt | harbortest.xxx/sit/ | TEST |
| uat | ns-jczx-tyfwzt | harbortest.xxx/uat/ | UAT |
| prod | p-ns-jczx-tyfwzt | harbor.xxx/prod/ | PROD |

### 常用运维命令

```bash
# 查看部署状态
kubectl get deployment -n ns-jczx-tyfwzt-dev

# 查看Pod状态
kubectl get pods -n ns-jczx-tyfwzt-dev

# 查看Pod详细状态
kubectl describe pod hmlink-server-xxx -n ns-jczx-tyfwzt-dev

# 查看Pod日志
kubectl logs -f hmlink-server-xxx -n ns-jczx-tyfwzt-dev

# 进入Pod
kubectl exec -it hmlink-server-xxx -n ns-jczx-tyfwzt-dev -- /bin/bash

# 重启Pod
kubectl rollout restart deployment/hmlink-server -n ns-jczx-tyfwzt-dev

# 回滚到上一版本
kubectl rollout undo deployment/hmlink-server -n ns-jczx-tyfwzt-dev

# 查看历史版本
kubectl rollout history deployment/hmlink-server -n ns-jczx-tyfwzt-dev

# 扩容
kubectl scale deployment hmlink-server -n ns-jczx-tyfwzt-dev --replicas=5
```

---

## 十八、生产环境配置建议值

> 🏠 生产环境就像正式营业的店铺——需要更严格的配置

### 资源配置建议

```yaml
# 生产环境K8s资源配置
resources:
  limits:
    cpu: "4"           # CPU上限4核
    memory: 4096Mi     # 内存上限4GB
  requests:
    cpu: "2"           # 初始CPU 2核
    memory: 2048Mi     # 初始内存 2GB

# 副本数建议
replicas: 2           # 至少2个副本，保证高可用
```

### 数据库连接池建议

```yaml
# 生产环境Druid配置
druid:
  initial-size: 10      # 初始连接数10
  min-idle: 10          # 最小空闲连接10
  max-active: 50        # 最大连接数50（根据QPS调整）
  max-wait: 30000       # 获取连接超时30秒
  validation-query: SELECT 1  # 验证连接是否有效
  test-while-idle: true     # 空闲时验证连接
  test-on-borrow: true      # 借出时验证连接
  time-between-eviction-runs-millis: 60000  # 每60秒检查一次空闲连接
```

### Redis连接建议

```yaml
# 生产环境Redis配置
redis:
  timeout: 5000           # 超时时间5秒
  lettuce:
    pool:
      max-active: 50      # 最大连接数
      max-idle: 20        # 最大空闲连接
      min-idle: 5         # 最小空闲连接
      max-wait: 3000      # 获取连接超时3秒
```

### 日志级别建议

```yaml
# 生产环境日志级别
logging:
  level:
    root: WARN            # 只显示警告和错误
    com.picchealth: INFO   # 项目日志INFO级别
    com.ctrip.framework.apollo: WARN  # Apollo日志降级
    org.mybatis: WARN      # MyBatis日志降级
    com.alibaba.druid: WARN  # Druid日志降级
```

### JVM参数建议

```bash
# 生产环境JVM参数
java -jar app.jar \
  -Xms2g \                 # 初始堆大小2GB
  -Xmx4g \                 # 最大堆大小4GB
  -XX:+UseG1GC \           # 使用G1垃圾收集器
  -XX:MaxGCPauseMillis=200 \  # 最大GC停顿时间200ms
  -XX:+HeapDumpOnOutOfMemoryError \  # OOM时生成堆转储
  -XX:HeapDumpPath=/logs/heapdump.hprof \  # 堆转储文件路径
```

---

## 十九、配置文件速查表

| 配置文件 | 位置 | 作用 | 优先级 |
|---------|------|------|-------|
| bootstrap.yml | src/main/resources | Apollo连接配置 | 最高（最先加载） |
| application.yml | src/main/resources | 本地基础配置 | 中等 |
| Apollo配置 | Apollo服务端 | 详细配置（数据库、Redis等） | 最高（运行时覆盖） |
| logback-spring.xml | src/main/resources | 日志配置 | 运行时可改 |
| Dockerfile | config/docker/ | 容器化配置 | 构建时 |
| K8s YAML | config/kubeconfig/ | 部署配置 | 部署时 |

### 配置加载顺序

```
1. bootstrap.yml（最先加载，读取Apollo地址）
      ↓
2. Apollo配置中心（获取application.properties）
      ↓
3. application-{profile}.properties（环境专用配置）
      ↓
4. application.yml（本地默认配置，Apollo没有的配置用这里的）
      ↓
5. 命令行参数（-Dxxx=yyy，最高优先级）
```

### 配置覆盖规则

```bash
# 后面的会覆盖前面的配置

# 示例：
# application.yml: server.port=9092
# Apollo: server.port=9093
# 命令行: -Dserver.port=9094

# 最终生效：9094（命令行最高）
# 如果没有命令行：9093（Apollo覆盖application）
```
