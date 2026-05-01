# PICC门诊慢特病前台服务 - 新成员Onboarding手册

> **项目全称**：门诊慢特病业务管理信息系统-前台服务  
> **服务端口**：9001  
> **源码位置**：`/tmp/picc-mzmtb-gateway/`  
> **预计上手时间**：2小时

---

## 📌 快速认知（5分钟）

### 这是什么服务？

```
┌─────────┐     ┌──────────────────┐     ┌─────────────────┐
│  前端   │ ──► │  前台服务(9001)  │ ──► │  业务服务(9091) │
│         │     │   (你在这里)      │     │                 │
└─────────┘     └──────────────────┘     └─────────────────┘
                                                 │
                                                 ▼
                                         ┌─────────────────┐
                                         │  权限服务(9092) │
                                         └─────────────────┘
```

**核心职责**：前台服务是**网关层**，不连数据库，负责：
- 接收前端请求
- 权限校验（Token、flag等）
- HTTP转发给业务服务
- 返回统一响应格式

### 技术栈速查

| 组件 | 版本/名称 | 用途 |
|------|----------|------|
| 基础框架 | Spring Boot | 应用框架 |
| 父POM | pdfc-parent 4.2.6.0 | 内部微服务框架 |
| 应用服务器 | BES宝蓝德 | 信创环境（非Tomcat） |
| 配置中心 | Apollo | 环境配置管理 |
| 缓存 | Redis | 权限/会话缓存 |
| 定时任务 | XXL-Job | 定时任务调度 |
| API文档 | Knife4j (Swagger) | 接口文档 |

### 项目规模

- **809** 个Java文件
- **102** 个API类
- **361** 个VO文件

---

## 第一部分：环境准备（30分钟）

### 1.1 JDK 8 安装 ⚠️重要

**本项目使用JDK 8，不是JDK 17！**

```bash
# 检查当前JDK版本
java -version

# 如果不是1.8，需要安装
# Windows: 下载JDK 8uXXX安装包 https://www.oracle.com/java/technologies/javase/javase8-archive-downloads.html

# macOS使用Homebrew
brew install openjdk@8
echo 'export JAVA_HOME=$(/usr/libexec/java_home -v 1.8)' >> ~/.zshrc
source ~/.zshrc

# Linux (CentOS/RHEL)
sudo yum install java-1.8.0-openjdk java-1.8.0-openjdk-devel -y
```

**IDEA中配置JDK 8**：
1. `File` → `Project Structure` → `Project`
2. Project SDK选择 `1.8`
3. `Modules` → `Dependencies` → `Module SDK` 也要选 `1.8`

### 1.2 IntelliJ IDEA 安装和配置

**推荐版本**：IntelliJ IDEA 2022.2+（社区版足够）

**必装插件**：
1. `Lombok` - 自动生成getter/setter
2. `Maven Helper` - Maven依赖分析
3. `Rainbow Brackets` - 括号高亮
4. `Alibaba Java Coding Guidelines` - 编码规范检查

**IDEA配置**：
```properties
# Settings → Build → Compiler → Java Compiler
Project bytecode version: 1.8

# Settings → Build → Build Tools → Maven
Maven home path: 选择你的Maven目录

# Settings → Editor → File Encodings
Project Encoding: UTF-8
```

### 1.3 Maven 配置

**settings.xml配置**（关键！PICC私服）：

```xml
<!-- ~/.m2/settings.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">

  <mirrors>
    <!-- PICC内部Maven私服 -->
    <mirror>
      <id>picc-maven-public</id>
      <mirrorOf>*</mirrorOf>
      <name>PICC Maven Public</name>
      <url>http://south.repo.devops.piccnet/maven/picc/maven-public/</url>
    </mirror>
  </mirrors>
  
  <profiles>
    <profile>
      <id>picc</id>
      <activation>
        <activeByDefault>true</activeByDefault>
      </activation>
      <repositories>
        <repository>
          <id>picc-maven-public</id>
          <url>http://south.repo.devops.piccnet/maven/picc/maven-public/</url>
          <releases>
            <enabled>true</enabled>
          </releases>
          <snapshots>
            <enabled>false</enabled>
          </snapshots>
        </repository>
        <repository>
          <id>f1dd82-picc-mzmtb</id>
          <url>http://bkrepo.itservice.piccnet/maven/f1dd82/picc-mzmtb/</url>
        </repository>
      </repositories>
    </profile>
  </profiles>
</settings>
```

**验证Maven配置**：
```bash
mvn -version
# 应该显示：
# Apache Maven 3.x.x
# Maven home: /path/to/maven
# Java version: 1.8.0_xxx
```

### 1.4 BES宝蓝德应用服务器 ⚠️信创环境

**背景**：项目使用BES宝蓝德中间件，不是传统Tomcat（信创要求）

**本地开发配置**：

1. **下载BES服务器**（联系运维获取安装包）
2. **配置IDEA**：
   ```
   Run → Edit Configurations → 
   点击"+" → JBoss Server → Local
   Application server: 选择BES安装路径
   JRE: 1.8
   ```

3. **或者使用传统方式启动**：
   ```bash
   # 打包后用java命令运行
   java -jar picc-mzmtb-gateway.jar
   ```

**注意**：如果BES本地环境配置困难，可以先用`java -jar`方式本地调试。

### 1.5 Apollo配置中心连接

**ApolloMeta地址**（从application-dev.yml获取）：
```
http://10.57.16.41:8080
```

**本地配置**：
```properties
# VM Options中添加
-Dapollo.meta=http://10.57.16.41:8080
-Dapp.id=picc-mzmtb-gateway
-Dapollo.cacheDir=/tmp/apollo-cache
```

**本地Apollo配置目录**：
```bash
# Windows: C:\opt\data\apolloconfig
# Linux/Mac: /opt/data/apolloconfig
```

### 1.6 Redis本地安装

**macOS**：
```bash
brew install redis
redis-server
```

**Linux (CentOS)**：
```bash
sudo yum install redis -y
sudo systemctl start redis
```

**Windows**：建议使用 [Memurai](https://www.memurai.com/) 或 Docker：
```bash
docker run -d -p 6379:6379 redis:6.2
```

**测试连接**：
```bash
redis-cli ping
# 返回 PONG 表示成功
```

---

## 第二部分：项目拉取和启动（30分钟）

### 2.1 Git克隆

```bash
# 方式1：使用Access Token
git clone https://gitlab.picchealth.com/picc-mzmtb/picc-mzmtb-gateway.git
cd picc-mzmtb-gateway

# 方式2：SSH（需要先配置SSH Key）
git clone git@gitlab.picchealth.com:picc-mzmtb/picc-mzmtb-gateway.git
```

**如果没有仓库权限**：联系项目负责人添加GitLab权限

### 2.2 Maven编译

⚠️ **注意**：项目lib目录有私有jar包！

```bash
# 先确认lib目录结构
ls lib/com/
# 应该看到: bes/, rsaSDK/, shie/, 91jkys/

# 编译（跳过测试加快速度）
cd picc-mzmtb-gateway
mvn clean compile -DskipTests

# 首次编译可能需要5-10分钟，耐心等待...
```

**常见编译问题**：

| 问题 | 解决方案 |
|------|----------|
| 找不到pdfc-parent | 检查Maven settings.xml私服配置 |
| 找不到lib下的jar | 确保在项目根目录执行mvn命令 |
| 内存溢出 | `mvn clean compile -DskipTests -Xmx1024m` |

### 2.3 配置文件修改

**关键配置文件位置**：`src/main/resources/`

```yaml
# bootstrap.yml - 启动配置（一般不改）
spring:
  application:
    name: picc-mzmtb-gateway
server:
  port: 9001  # 服务端口

# application-dev.yml - 开发环境配置
app:
  id: picc-mzmtb-gateway
apollo:
  bootstrap:
    enabled: true
    namespaces: application-local.properties
  meta: http://10.57.16.41:8080  # Apollo地址
```

**本地需要关注的配置**：

```yaml
# 在application-dev.yml或通过Apollo配置
forwardUrl: http://localhost:9091  # 业务服务地址
redis:
  host: localhost
  port: 6379
```

### 2.4 本地启动步骤

**方式1：IDEA直接启动**

1. 打开项目
2. 找到入口类：`LinkSpringBootApplication.java`
3. 右键 → Run 'LinkSpringBootApplication'
4. 或点击绿色三角按钮

**方式2：命令行启动**

```bash
# 打包
mvn clean package -DskipTests

# 运行
java -jar target/picc-mzmtb-gateway.jar --spring.profiles.active=dev

# 带Apollo参数
java -jar target/picc-mzmtb-gateway.jar \
  --spring.profiles.active=dev \
  -Dapollo.meta=http://10.57.16.41:8080 \
  -Dapp.id=picc-mzmtb-gateway
```

**启动成功标志**：
```
--------启动成功！--------
```

**Swagger文档地址**：
```
http://localhost:9001/doc.html
```

### 2.5 常见启动报错和解决方案

| 错误信息 | 原因 | 解决方案 |
|---------|------|----------|
| `Apollo配置加载失败` | ApolloMeta地址不通 | 检查网络或使用离线配置 |
| `Redis连接失败` | Redis未启动 | 启动Redis或修改配置 |
| `端口被占用` | 9001端口被占用 | `lsof -i:9001` 查进程并杀掉 |
| `BES初始化失败` | 缺少BES依赖 | 确保lib目录完整 |
| `ClassNotFoundException` | Maven依赖未下载 | `mvn dependency:resolve` |
| `flag信息不能为空` | 缺少header | 前端请求需带flag头 |

---

## 第三部分：代码导航（30分钟）

### 3.1 项目目录结构速览

```
picc-mzmtb-gateway/
├── src/main/java/com/picchealth/
│   ├── LinkSpringBootApplication.java    ← 启动入口
│   ├── config/                           ← 配置类
│   │   ├── interceptor/                  ← 拦截器
│   │   ├── jackson/                      ← JSON处理
│   │   ├── cors/                         ← 跨域配置
│   │   └── xssfilter/                    ← XSS过滤
│   ├── utils/                            ← 工具类
│   │   ├── HttpForwardUtil.java          ← ★HTTP转发核心
│   │   ├── RedisUtil.java                ← Redis操作
│   │   └── AesUtil.java                  ← 加密工具
│   └── module/                           ← 业务模块
│       ├── mb/                           ← ★慢特病主业务（最大模块）
│       ├── drugstore/                    ← 药店模块
│       ├── logaudit/                     ← 日志审计
│       └── ...
├── src/main/resources/
│   ├── application.yml                   ← 主配置
│   ├── bootstrap.yml                     ← 启动配置
│   └── logback-spring.xml                ← 日志配置
├── lib/                                  ← 私有jar包
└── pom.xml                               ← Maven配置
```

### 3.2 业务模块速查

| 模块名 | 路径 | 业务说明 |
|--------|------|----------|
| **mb** | `module/mb/` | 慢特病主业务（申报、审核、备案等） |
| **drugstore** | `module/drugstore/` | 药店管理、结算 |
| **logaudit** | `module/logaudit/` | 日志审计 |
| **call** | `module/call/` | 呼叫中心 |
| **schedualing** | `module/schedualing/` | 排班管理 |
| **diz** | `module/diz/` | 目录管理 |
| **outservice** | `module/outservice/` | 外部服务调用 |
| **restful** | `module/restful/` | REST接口 |
| **mtb** | `module/mtb/` | 核心业务逻辑 |
| **dpview** | `module/dpview/` | 数据展示视图 |

### 3.3 "我想看..." → 文件定位

#### 📌 "我想看申报接口"

```bash
# 路径
src/main/java/com/picchealth/module/mb/api/MbDeclareApi.java
src/main/java/com/picchealth/module/mb/api/VipMbDeclareListApi.java

# 关键接口
MbDeclareApi.java - 线下申报（/MbDeclare/*）
VipMbDeclareListApi.java - 申报列表（/vipMbDeclareList/*）
```

#### 📌 "我想看VO定义"

```bash
# 361个VO文件，按模块分布
src/main/java/com/picchealth/module/mb/vo/         # 慢特病相关VO
src/main/java/com/picchealth/module/drugstore/vo/   # 药店相关VO

# 常见VO命名规律
*Vo.java          # 请求/响应对象
*RequestVo.java   # 请求对象
*ResponseVo.java  # 响应对象
*Form.java        # 表单对象
```

#### 📌 "我想看HTTP转发逻辑"

```bash
# 核心工具类
src/main/java/com/picchealth/utils/HttpForwardUtil.java

# 使用示例（在API中）
@Autowired
private HttpForwardUtil httpForwardUtil;

// POST转发
ParameterizedTypeReference<ApiResponse> typeRef = new ParameterizedTypeReference<ApiResponse>(){};
return httpForwardUtil.post("/MbDeclare/query", request, queryVo, typeRef);
```

**HttpForwardUtil核心方法**：
```java
// JSON转发（最常用）
<T> T post(String url, HttpServletRequest request, Object requestVo, 
           ParameterizedTypeReference<T> typeRef);

// 表单+文件转发
<T> T post(String url, HttpServletRequest request, 
           ParameterizedTypeReference<T> typeRef, Map<String,Object> requestVo);

// GET转发
<T> T get(String url, Class<T> tClass);
```

#### 📌 "我想看拦截器"

```bash
# 拦截器目录
src/main/java/com/picchealth/config/interceptor/

# 文件说明
FlagInterceptorConfig.java     # flag拦截器（必带header）
APIAuthorityFilter.java        # 权限过滤器（Token、xcxUser）
MvcInterceptorConfig.java      # 拦截器注册
ServletConfig.java            # Servlet配置
```

#### 📌 "我想看权限校验"

```bash
# 权限过滤器
src/main/java/com/picchealth/config/interceptor/APIAuthorityFilter.java

# 关键逻辑
- Token验证
- xcxUser小程序用户验证
- URL权限验证（Redis中存储）
```

### 3.4 关键文件速查表

| 功能 | 文件路径 |
|------|----------|
| **启动入口** | `LinkSpringBootApplication.java` |
| **HTTP转发** | `utils/HttpForwardUtil.java` |
| **权限校验** | `config/interceptor/APIAuthorityFilter.java` |
| **Flag传递** | `config/interceptor/FlagInterceptorConfig.java` |
| **跨域配置** | `config/cors/GlobalCorsConfig.java` |
| **XSS过滤** | `config/xssfilter/XssRequestFilter.java` |
| **Redis工具** | `utils/redis/RedisUtil.java` |
| **统一响应** | `pdfc.framework.web.ApiResponse` |
| **API常量** | `module/mtb/constant/UrlApiConstant.java` |
| **XXL-Job配置** | `config/XxlJobConfig.java` |
| **Swagger配置** | （使用Knife4j自动配置） |

### 3.5 API路径约定

**前缀**：`/v2/`（UrlApiConstant.VERSION）

**常见API路径**：
```java
// MbDeclareApi
POST /v2/MbDeclare/query       // 查询申报
POST /v2/MbDeclare/declare     // 提交申报

// VipMbDeclareListApi
POST /v2/vipMbDeclareList/query // 申报列表

// LoginApi
POST /v2/Login/checkLogin       // 登录验证
```

---

## 第四部分：调试技巧（30分钟）

### 4.1 本地调试配置

**IDEA调试配置**：

1. `Run` → `Edit Configurations` → `+` → `Spring Boot`
2. 配置：
   ```
   Name: picc-mzmtb-gateway-dev
   Main class: com.picchealth.LinkSpringBootApplication
   Active profiles: dev
   VM options: 
     -Dapollo.meta=http://10.57.16.41:8080
     -Dapp.id=picc-mzmtb-gateway
   ```
3. 点击Debug按钮启动

### 4.2 同时调试前台服务和业务服务

**场景**：需要同时修改前后台代码进行调试

```
┌─────────────────────────────────────────────┐
│  IDEA窗口1: 前台服务 (9001)                  │
│  - picc-mzmtb-gateway                        │
│  - 打断点: HttpForwardUtil.post()            │
└─────────────────────────────────────────────┘
                    ↓ 转发
┌─────────────────────────────────────────────┐
│  IDEA窗口2: 业务服务 (9091)                  │
│  - picc-mzmtb-server（另一个项目）           │
│  - 打断点: Controller层                      │
└─────────────────────────────────────────────┘
```

**配置**：
1. 业务服务端口配置为9091
2. 前台服务配置 `forwardUrl=http://localhost:9091`
3. 分别启动两个服务
4. 前台服务打断点，业务服务也打断点

### 4.3 HTTP转发调试技巧

**在HttpForwardUtil中打断点**：

```java
// HttpForwardUtil.java 第30行附近
public <T> T post(String url, HttpServletRequest request, Object requestVo,
        ParameterizedTypeReference<T> parameterizedTypeReference) {
    // 在这里打断点可以看到：
    // url: 目标路径
    // requestVo: 请求参数
    // headers: 请求头（包含token、flag等）
    HttpHeaders headers = getHttpHeaders(request);
    HttpEntity requestEntity = new HttpEntity(requestVo, headers);
    ResponseEntity<T> responseEntity = restTemplate.exchange(prefix + url, HttpMethod.POST, requestEntity,
            parameterizedTypeReference);
    return responseEntity.getBody();
}
```

**关键变量**：
- `prefix` = `http://localhost:9091`（可配置）
- `url` = `/MbDeclare/query`（目标路径）
- `requestVo` = 请求参数对象

### 4.4 日志级别调整

**方式1：通过Apollo配置**
```
logging.level.root=INFO
logging.level.com.picchealth=DEBUG
```

**方式2：本地logback-spring.xml**

```xml
<!-- 临时改为DEBUG -->
<logger name="com.picchealth" level="DEBUG"/>
<logger name="org.springframework.web" level="DEBUG"/>
```

**关键日志类**：
```java
// 在代码中添加日志
@Slf4j
public class XxxService {
    public void method() {
        log.debug("请求参数: {}", request);
        log.info("处理中...");
        log.error("异常: ", e);
    }
}
```

**日志输出格式**（从logback-spring.xml）：
```
[时间] [线程] [级别] [tid] [主机/IP] [服务名] [日志器] [全局ID] [父ID] [本地ID] [消息]
```

### 4.5 接口调试

**Swagger文档**：
```
开发环境: http://localhost:9001/doc.html
生产环境: http://gateway.picchealth.com/doc.html
```

**Postman调试示例**：

```http
POST http://localhost:9001/v2/MbDeclare/query
Content-Type: application/json
flag: test-flag-123
token: xxx

{
  "pageNum": 1,
  "pageSize": 10
}
```

**必须的头信息**：
| Header | 说明 | 示例 |
|--------|------|------|
| flag | 标识（必填） | test-flag |
| token | 认证令牌 | xxx |
| Content-Type | application/json | application/json |

**常见调试问题**：

| 问题 | 检查项 |
|------|--------|
| 401 Unauthorized | 检查token是否正确 |
| 403 Forbidden | 检查权限配置 |
| flag信息不能为空 | 添加flag请求头 |
| 转发超时 | 检查业务服务是否启动 |
| 500 Internal Error | 查看前台服务日志 |

---

## 第五部分：避坑指南

### 5.1 🔴 前台服务不连数据库

**🔍 当前实现分析**：
```java
// 不要在前台服务找Mapper/DAO！
@Autowired
private MbDeclareMapper mbDeclareMapper;  // ❌ 不存在！

// 不要找MyBatis的XML！
find /src -name "MbDeclareMapper.xml"  // ❌ 找不到！
```

**📖 规范写法参考（仅供学习对比）**：
```java
// 前台服务通过HTTP转发给业务服务
@Autowired
private HttpForwardUtil httpForwardUtil;

@PostMapping("/query")
public ApiResponse query(@RequestBody QueryVo vo, HttpServletRequest request) {
    // 转发到业务服务(9091)
    return httpForwardUtil.post("/MbDeclare/query", request, vo, typeRef);
}
```

**数据库操作在哪里？**
- 在**业务服务**（picc-mzmtb-server）中
- 前台服务只做转发和权限校验

### 5.2 VO和PO的区别

| 类型 | 用途 | 位置 |
|------|------|------|
| **VO** | View Object，前台与前端交互 | 前台服务 `module/*/vo/` |
| **PO** | Persist Object，数据库实体 | 业务服务（你看不到） |
| **DTO** | Data Transfer Object，数据传输 | 业务服务 |

**前台服务只用VO**：
```java
// 前台服务的VO
src/main/java/com/picchealth/module/mb/vo/QueryDeclareVO.java

// 业务服务的PO（前台服务不可见）
// 应该在 picc-mzmtb-server 项目中
```

### 5.3 HTTP转发超时问题

**问题**：请求经常超时或响应慢

**原因**：
1. 业务服务处理时间长
2. 网络延迟
3. 超时配置太短

**解决方案**：

```yaml
# application.yml
resttemplate:
  connect-timeout: 30000  # 连接超时30秒
  read-timeout: 60000     # 读取超时60秒
```

**代码层面优化**：
```java
// HttpForwardUtil.java 默认超时设置
httpClient.getParams().setParameter(CoreConnectionPNames.CONNECTION_TIMEOUT, 2000000);
```

### 5.4 Token传递问题

**问题**：前端请求带Token，但转发后丢失

**原因**：Token在Header中，需要手动传递

**📖 规范写法参考（仅供学习对比）**：
```java
// HttpForwardUtil已自动处理Header传递
HttpHeaders getHttpHeaders(HttpServletRequest request) {
    HttpHeaders headers = new HttpHeaders();
    Enumeration<String> names = request.getHeaderNames();
    while (names.hasMoreElements()) {
        String name = names.nextElement();
        headers.add(name, request.getHeader(name));  // 包含token
    }
    return headers;
}
```

**⚠️ 注意事项**：
- Token在Header中传递，不是Body
- 部分接口可能需要额外处理（如解密）

### 5.5 BES和Tomcat的差异

| 差异点 | BES宝蓝德 | Tomcat |
|--------|----------|--------|
| **启动速度** | 较慢 | 快 |
| **内存占用** | 较大 | 较小 |
| **配置文件** | domain.xml | server.xml |
| **日志位置** | logs/ | logs/ |
| **部署方式** | 相似 | 相似 |
| **JVM参数** | 通过domain.xml配置 | 通过catalina.sh |

**本地开发建议**：
```bash
# 如果BES配置困难，可以用java -jar方式启动
java -jar picc-mzmtb-gateway.jar --spring.profiles.active=dev

# 注意：这种方式不经过BES，部分BES特性可能不可用
```

### 5.6 Apollo配置优先级

**加载顺序**（后面的覆盖前面的）：
1. `bootstrap.yml`（固定加载）
2. `application-{profile}.yml`
3. Apollo `application-local.properties`
4. Apollo `application.properties`
5. 命令行参数 `-D`

**本地开发建议**：
- 使用 `application-local.properties` 覆盖Apollo配置
- 避免污染Apollo测试/生产配置

---

## 附录

### A. 服务依赖关系

```
前端 (Vue/React)
    ↓ HTTP
前台服务 (9001) ←→ Redis (权限缓存)
    ↓ HTTP转发
业务服务 (9091) ←→ MySQL/Oracle
权限服务 (9092) ←→ 用户数据
```

### B. 常用Git命令

```bash
# 克隆项目
git clone git@gitlab.picchealth.com:picc-mzmtb/picc-mzmtb-gateway.git

# 创建分支
git checkout -b feature/your-feature-name

# 提交代码
git add .
git commit -m "feat: 新增xxx功能"

# 拉取代码
git pull origin develop

# 推送代码
git push origin feature/your-feature-name
```

### C. 联系人和资源

| 类型 | 联系方式 |
|------|----------|
| 项目负责人 | 联系TL获取 |
| GitLab | gitlab.picchealth.com |
| Apollo | apollo.picchealth.com |
| Redis运维 | 联系运维获取 |

### D. 快速检查清单

- [ ] JDK 8已安装并配置
- [ ] Maven settings.xml已配置PICC私服
- [ ] Redis已启动
- [ ] Apollo可连接
- [ ] 项目可编译通过
- [ ] 服务可启动（端口9001）
- [ ] Swagger文档可访问

---

**手册版本**：v1.0  
**最后更新**：2024年  
**维护者**：PICC慢特病项目组
