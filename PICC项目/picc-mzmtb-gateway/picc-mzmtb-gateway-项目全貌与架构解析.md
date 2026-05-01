# PICC门诊慢特病前台服务（picc-mzmtb-gateway）
## 项目全貌与架构深度解析

> 📌 **文档定位**：面向零基础读者，采用"餐厅比喻"进行技术概念普及，但技术细节不缩水
> 
> 📌 **版本信息**：基于源码分析生成，请以实际项目为准

---

# Part 1：项目全貌

## 1.1 三服务架构总览

### 1.1.1 项目定位：你是谁？

**前台服务 = 餐厅的服务员** 🧑‍🍳

想象你去一家高档餐厅吃饭：
- **你**（顾客）→ 就像用户通过前端访问系统
- **服务员**（前台服务）→ 接待你、记下你要点的菜（接收请求）、把菜单传给后厨（转发请求）、把做好的菜端给你（返回结果）
- **后厨**（业务服务）→ 真正做菜的地方，涉及各种复杂操作
- **仓库管理员**（权限服务）→ 决定谁能进餐厅、谁能点什么菜

**前台服务的核心职责**：
> 接收前端请求 → 验证权限 → 转发给后端业务服务 → 把处理结果返回给前端

### 1.1.2 三服务对比表

| 对比维度 | 权限服务 | 业务服务 | 前台服务（本案） |
|---------|---------|---------|----------------|
| **服务端口** | 9092 | 9091 | **9001** |
| **Java文件数** | 136 | 2647 | **809** |
| **代码总量** | ~2万行 | ~30万行 | **5.6万行** |
| **数据库** | 直连GaussDB | 直连GaussDB | **❌ 不直连** |
| **Mapper文件** | 有 | 有 | **❌ 0个** |
| **核心职责** | 身份验证+权限管理 | 业务逻辑处理+数据CRUD | **请求转发+格式转换** |
| **API数量** | ~30个 | ~500个 | **104个** |
| **VO文件** | ~50个 | ~400个 | **361个** |

### 1.1.3 三服务调用链路图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              用户请求发起                                     │
│                                   ↓                                          │
│  ┌─────────────┐                                                              │
│  │   前端应用   │  ←  小程序 / PC端 / 移动端                                   │
│  └──────┬──────┘                                                              │
│         ↓                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                        防火墙 / 网关 / 负载均衡                           │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│         ↓                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                     【前台服务】端口:9001                                  │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │ │
│  │  │  拦截器链（4层防护）                                                │    │ │
│  │  │  ① Token验证 → ② Flag提取 → ③ 接口授权 → ④ 小程序签名               │    │ │
│  │  └─────────────────────────────────────────────────────────────────┘    │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │ │
│  │  │  XSS过滤 → 请求参数清洗                                            │    │ │
│  │  └─────────────────────────────────────────────────────────────────┘    │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │ │
│  │  │  字段解密 → SM2/AES加密字段自动解密                                 │    │ │
│  │  └─────────────────────────────────────────────────────────────────┘    │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │ │
│  │  │  HTTP转发 → RestTemplate调用业务服务                               │    │ │
│  │  └─────────────────────────────────────────────────────────────────┘    │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │ │
│  │  │  响应包装 → ApiResponse统一格式                                    │    │ │
│  │  └─────────────────────────────────────────────────────────────────┘    │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│         ↓                          ↓                                         │
│    ┌─────────┐              ┌─────────────┐                                  │
│    │ 业务服务 │              │  权限服务    │                                  │
│    │ 9091    │              │  9092       │                                  │
│    └────┬────┘              └──────┬──────┘                                  │
│         ↓                         ↓                                         │
│  ┌───────────────┐          ┌───────────────┐                                │
│  │   GaussDB    │          │   GaussDB     │                                │
│  │  业务数据库   │          │   权限数据库   │                                │
│  └───────────────┘          └───────────────┘                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.1.4 前台服务的"无Mapper"设计哲学

**为什么前台服务不需要Mapper？**

因为前台服务**不直接操作数据库**！它只做"传话筒"：

```
┌─────────────────────────────────────────────────────────┐
│  传统分层架构：                                          │
│  Controller → Service → Mapper → 数据库                   │
│              （直接操作数据库）                           │
├─────────────────────────────────────────────────────────┤
│  前台服务架构：                                          │
│  Controller → Service → 【HttpForwardUtil】→ 业务服务     │
│              （通过HTTP调用别人）                        │
└─────────────────────────────────────────────────────────┘
```

**这种设计的优势**：
1. **解耦**：前台服务不知道数据库长什么样
2. **安全**：数据库不暴露在外网
3. **灵活**：业务逻辑变更不需要动前台服务
4. **复用**：一个业务服务可以被多个前台服务调用

---

## 1.2 模块结构详解

### 1.2.1 模块目录概览

```
src/main/java/com/picchealth/module/
├── base/           # 1个文件    → 基础父类
├── cache/          # 1个文件    → 缓存相关
├── call/           # 1个文件    → 外部调用
├── claim/          # 1个文件    → 理赔相关
├── config/         # 2个文件    → 配置类
├── consumer/       # 2个文件    → 消费者/订阅
├── diz/            # 2个文件    → 目录相关
├── dpview/         # 11个文件   → 数据展示
├── drugstore/      # 13个文件   → 药店管理（主力模块之一）
├── logaudit/       # 3个文件    → 日志审计
├── mb/             # 523个文件  → ⭐慢病申报（绝对主力，占65%）
├── mtb/            # 37个文件   → 慢特病核心
├── outservice/     # 1个文件    → 外部服务
├── publics/        # 1个文件    → 公共接口
├── restful/        # 56个文件   → REST接口
├── schedualing/    # 2个文件    → 定时任务
├── test/           # 1个文件    → 测试类
├── thirdfee/       # 1个文件    → 第三方费用
├── webservice/     # 93个文件   → WebService服务
└── ws/             # 18个文件   → WebService工具
─────────────────────────────────────────────────────────
总计: 770个Java文件
```

### 1.2.2 模块职责说明

| 模块 | 文件数 | 占比 | 核心功能 | 比喻 |
|-----|-------|------|---------|------|
| **mb** | 523 | 65% | 慢病申报、备案、审核 | 餐厅的"招牌菜" |
| **webservice** | 93 | 12% | 医保/第三方系统对接 | 餐厅的"外卖平台对接" |
| **restful** | 56 | 7% | REST风格接口 | 餐厅的"扫码点餐" |
| **drugstore** | 13 | 2% | 药店管理、处方审核 | 餐厅的"酒水区" |
| **dpview** | 11 | 1% | 数据统计展示 | 餐厅的"销售报表" |
| **ws** | 18 | 2% | WebService工具 | 餐厅的"电话订餐系统" |
| 其他 | 56 | 7% | 辅助功能 | 餐厅的"后勤部门" |

### 1.2.3 mb模块（慢病申报）内部结构

```
mb/
├── api/           # 62个API类    → 对外接口层
├── constant/     # 常量定义
├── dto/          # 数据传输对象
├── enums/        # 枚举类
├── po/           # 持久化对象
├── service/      # 服务层
│   ├── impl/     # 59个实现类
│   └── *.java    # 多个接口定义
└── vo/           # 视图对象（请求/响应包装）
```

---

## 1.3 关键数字速览

| 指标 | 数值 | 说明 |
|-----|------|------|
| **Java文件总数** | 809个 | 包括API、Service、VO、工具类等 |
| **代码总行数** | 55,949行 | 纯Java代码 |
| **API类数量** | 104个 | Controller层接口类 |
| **API方法数量** | ~400+个 | 实际暴露的接口 |
| **VO文件数量** | 361个 | 请求/响应对象 |
| **Mapper XML** | 0个 | **不直连数据库** |
| **Service层** | ~60个 | 业务逻辑类 |
| **定时任务** | 22个 | XXL-Job定时任务 |
| **业务模块** | 20个 | 按功能划分 |
| **配置文件** | 7个 | yml/properties |

---

# Part 2：架构深度解析

## 2.1 技术栈全景

### 2.1.1 技术栈地图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            【应用层】                                        │
│  Spring Boot 2.x                    快速启动 + 自动配置                       │
│  pdfc-parent 4.2.6.0               PICC统一开发框架（内部封装）                │
│  Swagger/Knife4j 2.0.0              API文档 + 接口调试                        │
│  EasyExcel 3.2.1                    Excel导入导出                             │
│  iTextPDF 5.5.13                    PDF生成                                  │
│  Apache CXF 3.2.5                   WebService服务                           │
│  XXL-Job 2.3.1                     分布式任务调度                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                            【通信层】                                        │
│  RestTemplate                       HTTP同步调用（主要）                        │
│  HttpClient 4.1                    Apache HTTP客户端                        │
│  Feign                             服务间调用（未使用）                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                            【中间件层】                                       │
│  Apollo 1.8.0                      配置中心                                 │
│  Redis                             缓存 + Session存储                         │
│  BES (宝蓝德) 9.5.5.007            应用服务器中间件                           │
│  SFTP/FTP                          文件传输                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                            【安全层】                                        │
│  SM2 (国密算法)                    国产加密                                 │
│  AES                               对称加密                                 │
│  JSoup 1.15.3                     XSS防护                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                            【基础设施】                                       │
│  MySQL/PostgreSQL兼容              通过业务服务访问                           │
│  Tomcat内嵌                        应用服务器                                │
│  Logback                           日志框架                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.1.2 技术栈小白化翻译

| 技术名词 | 小白翻译 | 实际作用 |
|---------|---------|---------|
| **Spring Boot** | 预制菜设备 | 帮你把做菜（开发）的流程标准化、自动化 |
| **Apollo** | 中央厨房调料柜 | 所有项目的配置（数据库地址、开关等）都从这里拿 |
| **Redis** | 餐厅取餐叫号屏 | 临时存储用户登录状态，不用每次都查"会员系统" |
| **RestTemplate** | 对讲机 | 前台服务"呼叫"业务服务的工具 |
| **SM2** | 保险柜密码 | 国家认可的加密方式，保护敏感数据 |
| **XXL-Job** | 自动炒菜机定时器 | 定时执行任务，如每天凌晨自动对账 |
| **Knife4j** | 餐厅电子菜单 | 方便前端工程师查看有哪些"菜"可以点 |
| **EasyExcel** | 批量点餐表格 | 导入导出Excel文件 |
| **iTextPDF** | 打印小票机 | 生成PDF文件，如电子发票 |

---

## 2.2 Maven依赖分析

### 2.2.1 pom.xml核心依赖解读

```xml
<!-- ============ 1. 基础框架 ============ -->
<!-- PICC内部封装框架 -->
<parent>
    <groupId>pdfc</groupId>
    <artifactId>pdfc-parent</artifactId>
    <version>4.2.6.0</version>
</parent>

<!-- Spring Boot 2.x 基础包 -->
<dependency>
    <groupId>pdfc</groupId>
    <artifactId>pdfc-web</artifactId>  <!-- Web支持 -->
</dependency>
<dependency>
    <groupId>pdfc</groupId>
    <artifactId>pdfc-cloud</artifactId>  <!-- 微服务支持 -->
</dependency>
<dependency>
    <groupId>pdfc</groupId>
    <artifactId>pdfc-config</artifactId>  <!-- 配置支持 -->
</dependency>
<dependency>
    <groupId>pdfc</groupId>
    <artifactId>pdfc-cache</artifactId>  <!-- 缓存支持 -->
</dependency>

<!-- ============ 2. 中间件 ============ -->
<!-- 宝蓝德应用服务器 -->
<dependency>
    <groupId>com.bes.appserver</groupId>
    <artifactId>bes-lite-spring-boot-2.x-starter</artifactId>
    <version>9.5.5.007</version>
</dependency>

<!-- Apollo配置中心 -->
<!-- 已在启动类通过 @EnableApolloConfig 启用 -->

<!-- ============ 3. 工具库 ============ -->
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>fastjson</artifactId>  <!-- JSON处理 -->
    <version>1.2.83</version>
</dependency>
<dependency>
    <groupId>org.bouncycastle</groupId>
    <artifactId>bcprov-jdk15to18</artifactId>  <!-- 国密算法支持 -->
    <version>1.78.1</version>
</dependency>
<dependency>
    <groupId>com.github.xiaoymin</groupId>
    <artifactId>knife4j-spring-boot-starter</artifactId>  <!-- Swagger增强 -->
    <version>2.0.0</version>
</dependency>
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>easyexcel</artifactId>  <!-- Excel处理 -->
    <version>3.2.1</version>
</dependency>
<dependency>
    <groupId>com.itextpdf</groupId>
    <artifactId>itextpdf</artifactId>  <!-- PDF生成 -->
    <version>5.5.13</version>
</dependency>

<!-- ============ 4. 安全相关 ============ -->
<dependency>
    <groupId>org.jsoup</groupId>
    <artifactId>jsoup</artifactId>  <!-- XSS防护 -->
    <version>1.15.3</version>
</dependency>

<!-- ============ 5. 定时任务 ============ -->
<dependency>
    <groupId>com.xuxueli</groupId>
    <artifactId>xxl-job-core</artifactId>
    <version>2.3.1</version>
</dependency>

<!-- ============ 6. WebService ============ -->
<dependency>
    <groupId>org.apache.cxf</groupId>
    <artifactId>cxf-spring-boot-starter-jaxws</artifactId>
    <version>3.2.5</version>
</dependency>

<!-- ============ 7. 文件处理 ============ -->
<dependency>
    <groupId>org.apache.poi</groupId>
    <artifactId>poi</artifactId>  <!-- Office文档 -->
    <version>4.1.2</version>
</dependency>
<dependency>
    <groupId>org.apache.pdfbox</groupId>
    <artifactId>pdfbox</artifactId>  <!-- PDF解析 -->
    <version>2.0.24</version>
</dependency>
<dependency>
    <groupId>org.xhtmlrenderer</groupId>
    <artifactId>flying-saucer-pdf-itext5</artifactId>  <!-- HTML转PDF -->
    <version>9.1.20</version>
</dependency>
<dependency>
    <groupId>com.jcraft</groupId>
    <artifactId>jsch</artifactId>  <!-- SFTP传输 -->
    <version>0.1.55</version>
</dependency>
```

### 2.2.2 依赖排除策略

项目主动排除了以下依赖，避免冲突：

```xml
<!-- 排除Swagger重复依赖 -->
<exclusions>
    <exclusion>
        <groupId>io.springfox</groupId>
        <artifactId>springfox-swagger-ui</artifactId>
    </exclusion>
</exclusions>

<!-- 排除pdfc-mybatis（前台不需要直连数据库） -->
<exclusions>
    <exclusion>
        <groupId>pdfc</groupId>
        <artifactId>pdfc-mybatis</artifactId>
    </exclusion>
    <exclusion>
        <groupId>tk.mybatis</groupId>
        <artifactId>mapper-spring-boot-starter</artifactId>
    </exclusion>
</exclusions>
```

---

## 2.3 配置文件解析

### 2.3.1 bootstrap.yml（启动引导配置）

```yaml
spring:
  application:
    name: picc-mzmtb-gateway   # 应用名称
server:
  port: 9001                   # 服务端口
```

**解读**：
- 这是Spring Cloud应用的"出生证明"
- 在所有配置加载之前先读取这个文件
- 告诉系统"我是谁"（应用名）、"我在哪"（端口）

### 2.3.2 application.yml（主配置文件）

```yaml
server:
  port: 9001
spring:
  profiles:
    active: dev          # 激活dev环境配置
  application:
    name: picc-mzmtb-server
apollo:
  bootstrap:
    enabled: true       # 启用Apollo配置拉取
    eagerLoad:
      enabled: true
```

**解读**：
- `profiles.active: dev` 表示使用dev环境的配置
- Apollo配置中心会覆盖本地配置

### 2.3.3 多环境配置

```
src/main/resources/
├── application.yml              # 主配置
├── application-dev.yml          # 开发环境
├── application-test.yml         # 测试环境
└── application-uat.yml         # UAT环境
```

**dev环境配置（application-dev.yml）**：
```yaml
app:
  id: picc-mzmtb-gateway              # Apollo中的应用ID
apollo:
  bootstrap:
    enabled: true
    namespaces: application-local.properties  # 私有配置命名空间
  meta: http://10.57.16.41:8080       # Apollo配置中心地址
```

### 2.3.4 Apollo配置中心

Apollo是配置中心，存储敏感配置和公共配置：

```properties
# Apollo中的典型配置项（示例，非实际值）
forward.url=http://业务服务地址:9091    # 业务服务地址
redis.host=Redis服务器地址               # Redis服务器
redis.port=6379                          # Redis端口
xxl.job.admin.addresses=XXL-Job地址     # 定时任务管理后台
```

---

## 2.4 安全机制（4层拦截器）

### 2.4.1 安全架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                      请求进入前台服务                             │
├─────────────────────────────────────────────────────────────────┤
│  【第1层】APIAuthorityFilter                                     │
│  ├── Token验证：检查登录凭证                                     │
│  ├── Flag验证：检查地市标识                                      │
│  └── 接口授权：检查URL访问权限                                   │
├─────────────────────────────────────────────────────────────────┤
│  【第2层】FlagInterceptorConfig                                  │
│  └── 提取Flag并存入ThreadLocal，供后续使用                       │
├─────────────────────────────────────────────────────────────────┤
│  【第3层】XssRequestFilter                                       │
│  └── XSS攻击防护，清理恶意脚本                                   │
├─────────────────────────────────────────────────────────────────┤
│  【第4层】EncryptDecryptAop                                      │
│  └── 字段解密，自动解密SM2加密的字段                             │
├─────────────────────────────────────────────────────────────────┤
│                      到达Controller                              │
└─────────────────────────────────────────────────────────────────┘
```

### 2.4.2 第1层：APIAuthorityFilter（API权限过滤器）

**源码位置**：`com.picchealth.config.interceptor.APIAuthorityFilter`

```java
@WebFilter(urlPatterns = {
    "/ppop/*", "/offline/*", "/drugstore/*", 
    "/MbDeclare/*", "/MbReview/*", "/v2/*",
    "/picchealth/*", "/filingMan/*"
}, filterName = "APIAuthorityFilter")
public class APIAuthorityFilter implements Filter {
    
    // Token前缀
    private String USERID = "userid:";
    private String FLAG = "flag:";
    private String XCXUsers = "XCXUsers:";  // 小程序用户
    
    @Override
    public void doFilter(ServletRequest servletRequest, 
                        ServletResponse servletResponse, 
                        FilterChain filterChain) {
        HttpServletRequest request = (HttpServletRequest) servletRequest;
        
        // 1. 提取Token和UserID
        String token = request.getHeader("token");
        String userid = request.getHeader("userid");
        
        // 2. 验证Token有效性
        if (StringUtils.isBlank(token)) {
            throw CustomException.createByMassage(999, "登录Token无效!请重新登录");
        }
        
        // 3. 检查Redis中是否存在
        if (!redisUtil.exists(USERID + userid)) {
            throw new BusinessException("请重新登录");
        }
        
        // 4. 验证Token一致性
        String storedToken = (String) redisUtil.get(USERID + userid);
        if (!storedToken.equals(token)) {
            throw CustomException.createByMassage(999, "登录Token无效!请重新登录");
        }
        
        // 5. 检查URL权限
        List<String> permissions = (ArrayList<String>) redisUtil.get(UrlPermission + userid);
        long count = permissions.stream()
            .filter(s -> requestPath.startsWith(s))
            .count();
        if (count == 0) {
            throw new CustomException("接口权限未通过!");
        }
        
        filterChain.doFilter(servletRequest, servletResponse);
    }
}
```

**核心逻辑**：
1. 从请求头获取Token和UserID
2. 从Redis查询Token是否有效
3. 验证Token一致性（防止伪造）
4. 检查用户是否有访问该URL的权限

### 2.4.3 第2层：FlagInterceptorConfig（Flag拦截器）

**源码位置**：`com.picchealth.config.interceptor.FlagInterceptorConfig`

```java
@Configuration
public class FlagInterceptorConfig implements HandlerInterceptor {
    
    @Override
    public boolean preHandle(HttpServletRequest request, 
                             HttpServletResponse response, 
                             Object handler) {
        // 从请求头获取Flag（地市标识）
        String flag = request.getHeader("flag");
        if (StringUtils.isBlank(flag)) {
            throw CustomException.createByMassage(888, "flag信息不能为空！");
        }
        
        // 存入ThreadLocal，供后续使用
        FlagLocal flagLocal = new FlagLocal();
        flagLocal.setFlag(flag);
        FlagUtils.setFlagLocal(flagLocal);
        
        return true;
    }
    
    @Override
    public void afterCompletion(HttpServletRequest request, 
                               HttpServletResponse response, 
                               Object handler, Exception ex) {
        // 清理ThreadLocal，防止内存泄漏
        FlagUtils.remove();
    }
}
```

**Flag的作用**：
- Flag是地市标识，如"6103"代表某个城市
- 用于数据隔离，不同地市只能看自己的数据
- 存入ThreadLocal保证线程安全

### 2.4.4 第3层：XssRequestFilter（XSS防护）

**源码位置**：`com.picchealth.config.xssfilter.XssRequestFilter`

```java
@WebFilter(filterName = "xssFilter", urlPatterns = {"/*"})
public class XssRequestFilter implements Filter {
    
    @Override
    public void doFilter(ServletRequest request, 
                        ServletResponse response, 
                        FilterChain filterChain) {
        if (request instanceof HttpServletRequest) {
            // 包装请求，对输入进行XSS过滤
            request = new XssHttpServletRequestWrapper((HttpServletRequest) request);
            
            // 设置HttpOnly，防止Cookie劫持
            ((HttpServletResponse) response).setHeader(
                "Set-Cookie", 
                "cookiename=cookievalue; path=/; HttpOnly"
            );
        }
        filterChain.doFilter(request, response);
    }
}
```

**XSS防护原理**：
- 过滤`<script>`、`javascript:`等危险字符
- 防止跨站脚本攻击
- 设置HttpOnly防止JS读取Cookie

### 2.4.5 第4层：EncryptDecryptAop（字段解密）

**源码位置**：`com.picchealth.config.Encrypt.EncryptDecryptAop`

```java
@Component
@Aspect
public class EncryptDecryptAop {
    
    // 切面：拦截mb模块的API
    @Around("execution(* com.picchealth.module.mb.api.*.*(..))")
    public Object doProcess(ProceedingJoinPoint proceedingJoinPoint) throws Throwable {
        
        // 1. 获取方法参数
        List<Object> methodArgs = this.getMethodArgs(proceedingJoinPoint);
        
        // 2. 遍历参数，查找被@EncryptField注解的字段
        for (Object item : methodArgs) {
            Field[] fields = item.getClass().getDeclaredFields();
            for (Field field : fields) {
                if (null != AnnotationUtils.findAnnotation(field, EncryptField.class)) {
                    // 允许访问private字段
                    ReflectionUtils.makeAccessible(field);
                    
                    // 解密字段值
                    String encryptedValue = (String) field.get(item);
                    String decryptedValue = Sm2Util.decryptData(encryptedValue);
                    field.set(item, decryptedValue);
                }
            }
        }
        
        // 3. 执行原方法
        return proceedingJoinPoint.proceed();
    }
}
```

**解密注解使用示例**：

```java
public class SomeRequestVo {
    
    @EncryptField  // 这个字段会自动解密
    private String mobile;  // 手机号
    
    private String name;  // 这个字段不解密
}
```

---

## 2.5 XSS过滤、字段加密、跨域配置

### 2.5.1 XSS过滤配置

```java
// XssRequestFilter.java
@WebFilter(filterName = "xssFilter", urlPatterns = {"/*"})
public class XssRequestFilter implements Filter {
    // 底层使用 pdfc.framework.web.filter.support.XssHttpServletRequestWrapper
    // 实现XSS字符过滤
}
```

### 2.5.2 字段加密配置

```java
// EncryptField.java - 注解定义
@Documented
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)  // 作用于字段
public @interface EncryptField {
}

// 使用方式
public class MbDeclareRequestVo {
    @EncryptField
    private String mobile;  // 手机号自动解密
}
```

### 2.5.3 跨域配置

**源码位置**：`com.picchealth.config.cors.GlobalCorsConfig`

```java
@Configuration
public class GlobalCorsConfig implements WebMvcConfigurer {

    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/**")           // 所有路径
                        .allowedOrigins("*")          // 允许所有来源
                        .allowCredentials(true)       // 允许携带Cookie
                        .allowedMethods("GET", "POST", "PUT", "DELETE")  // 允许的方法
                        .allowedHeaders("*");         // 允许的头部
            }
        };
    }
}
```

**解读**：
- `allowedOrigins("*")` 允许所有域名访问（生产环境应限制）
- `allowCredentials(true)` 允许前端携带Cookie
- `allowedHeaders("*")` 允许所有请求头

---

## 2.6 定时任务（XXL-Job）

### 2.6.1 XXL-Job配置

**源码位置**：`com.picchealth.config.XxlJobConfig`

```java
@Configuration
public class XxlJobConfig {
    
    @Value("${xxl.job.admin.addresses}")
    private String adminAddresses;      // 调度中心地址
    
    @Value("${xxl.job.executor.appname}")
    private String appname;             // 执行器名称
    
    @Value("${xxl.job.executor.port}")
    private int port;                   // 执行器端口
    
    @Bean
    public XxlJobSpringExecutor xxlJobExecutor() {
        XxlJobSpringExecutor executor = new XxlJobSpringExecutor();
        executor.setAdminAddresses(adminAddresses);
        executor.setAppname(appname);
        executor.setPort(port);
        executor.setAccessToken(accessToken);  // 调度安全token
        executor.setLogPath(logPath);           // 日志路径
        executor.setLogRetentionDays(30);       // 日志保留30天
        return executor;
    }
}
```

### 2.6.2 定时任务实现

**源码位置**：`com.picchealth.module.schedualing.api.SchedulingXxlJob`

```java
@Component
public class SchedulingXxlJob {
    
    @Resource
    private HttpForwardUtil httpForwardUtil;
    
    private String baseUrl = "/scheduling";
    
    // 任务1：发卡相关
    @XxlJob("ghiInsureDetailInitTask")
    public void executeGhiInsureDetailInitTask() {
        XxlJobHelper.log("XXL-JOB, ghiInsureDetailInitTask Begin");
        try {
            JSONObject jsonString = httpForwardUtil.post(
                baseUrl + "/ghiInsureDetailInitTask", 
                new JSONObject()
            );
            if (jsonString.getInteger("status").equals(-1)) {
                XxlJobHelper.handleFail();  // 标记任务失败
            }
        } catch (Exception e) {
            XxlJobHelper.log(e);
            XxlJobHelper.handleFail();
        }
    }
    
    // 任务2：门诊状态更新
    @XxlJob("vipMbmzStatusTask")
    public void executeVipMbmzStatusTask() {
        // 定时更新门诊状态
    }
    
    // ... 共22个定时任务
}
```

### 2.6.3 定时任务清单

| 任务名称 | 功能描述 | 执行频率 |
|---------|---------|---------|
| `ghiInsureDetailInitTask` | 宝鸡慢病发卡 | 定时 |
| `BJRecordTask` | 宝鸡备案信息查询 | 定时 |
| `BJDelFilingTask` | 宝鸡病种删除同步 | 定时 |
| `vipMbmzStatusTask` | 门诊状态更新 | 定时 |
| `vipMbmzUpdateTask` | 门诊信息更新 | 定时 |
| `vipSendMessageTask` | 短信发送 | 定时 |
| `imageQualityInspectionTaskBJ` | 图片质检(宝鸡) | 定时 |
| `medicalImageClassificationTaskBJ` | 医疗影像分类(宝鸡) | 定时 |
| `idCardOcrTaskBJ` | 身份证OCR识别(宝鸡) | 定时 |
| `sealRecognitionTaskBJ` | 印章识别(宝鸡) | 定时 |
| ... | ... | ... |

---

## 2.7 与业务服务的通信方式

### 2.7.1 HttpForwardUtil（HTTP转发工具）

**源码位置**：`com.picchealth.utils.HttpForwardUtil`

这是前台服务的**核心通信组件**，所有对业务服务的调用都通过它：

```java
@Component
@Slf4j
public class HttpForwardUtil {
    
    // 业务服务地址，默认本地9091
    @Value("${forwardUrl:http://localhost:9091}")
    private String prefix;
    
    @Autowired
    private RestTemplate restTemplate;
    
    // ============ 核心方法1：POST请求 ============
    public <T> T post(String url, HttpServletRequest request, 
                     Object requestVo, Class<T> clazz) {
        // 1. 复制请求头
        HttpHeaders headers = getHttpHeaders(request);
        
        // 2. 封装请求实体
        HttpEntity requestEntity = new HttpEntity(requestVo, headers);
        
        // 3. 发送POST请求
        ResponseEntity<T> responseEntity = restTemplate.exchange(
            prefix + url,           // 目标地址
            HttpMethod.POST,        // 请求方法
            requestEntity,          // 请求体
            clazz                   // 返回类型
        );
        
        // 4. 返回响应体
        return responseEntity.getBody();
    }
    
    // ============ 核心方法2：带参数化类型返回 ============
    public <T> T post(String url, HttpServletRequest request, 
                     Object requestVo,
                     ParameterizedTypeReference<T> parameterizedTypeReference) {
        HttpHeaders headers = getHttpHeaders(request);
        HttpEntity requestEntity = new HttpEntity(requestVo, headers);
        ResponseEntity<T> responseEntity = restTemplate.exchange(
            prefix + url, HttpMethod.POST, requestEntity,
            parameterizedTypeReference
        );
        return responseEntity.getBody();
    }
    
    // ============ 核心方法3：表单文件上传 ============
    public <T> T post(String url, HttpServletRequest request,
                     ParameterizedTypeReference<T> parameterizedTypeReference, 
                     Map<String, Object> requestVo) {
        HttpHeaders headers = getHttpHeaders(request);
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);
        
        // 处理文件上传
        MultiValueMap<String, Object> map = new LinkedMultiValueMap<>();
        // ... 文件处理逻辑
        
        HttpEntity<MultiValueMap<String, Object>> requestEntity = 
            new HttpEntity<>(map, headers);
        
        return restTemplate.exchange(
            prefix + url, HttpMethod.POST, requestEntity,
            parameterizedTypeReference
        ).getBody();
    }
    
    // ============ 核心方法4：直接POST（不带请求头） ============
    public JSONObject post(String url, JSONObject all) {
        DefaultHttpClient httpClient = new DefaultHttpClient();
        HttpPost httpPost = new HttpPost(prefix + url);
        
        // 设置请求体
        StringEntity entity = new StringEntity(
            JSONObject.toJSONString(all), "utf-8"
        );
        entity.setContentType("application/json");
        httpPost.setEntity(entity);
        
        // 执行请求
        HttpResponse response = httpClient.execute(httpPost);
        String result = EntityUtils.toString(response.getEntity(), "utf-8");
        
        return JSONObject.parseObject(result);
    }
}
```

### 2.7.2 调用示例

**以MbDeclareApi为例**：

```java
@RestController
@Api(value = "线下申报", tags = "线下申报")
@RequestMapping(value = "/MbDeclare")
public class MbDeclareApi {
    
    @Autowired
    private HttpForwardUtil httpForwardUtil;
    
    private String baseUrl = "/MbDeclare";  // 业务服务的接口前缀
    
    @ApiOperation(value = "查询线下申报记录")
    @RequestMapping(method = {RequestMethod.POST}, value = "/query")
    public ApiResponse query(@RequestBody QueryDeclareVO queryDeclareVO, 
                            HttpServletRequest request) {
        // 定义返回类型
        ParameterizedTypeReference<ApiResponse> typeRef = 
            new ParameterizedTypeReference<ApiResponse>(){};
        
        // 调用HttpForwardUtil转发请求
        return httpForwardUtil.post(
            baseUrl + "/query",     // 业务服务接口路径
            request,                 // 传递请求（用于复制header）
            queryDeclareVO,          // 请求参数
            typeRef                  // 返回类型
        );
    }
}
```

### 2.7.3 调用链路图

```
┌─────────────────────────────────────────────────────────────────┐
│                     【前台服务】Controller                        │
│                                                                 │
│  MbDeclareApi.query()                                           │
│       ↓                                                         │
│  return httpForwardUtil.post(                                   │
│      baseUrl + "/query",  // "http://localhost:9091/MbDeclare/query" │
│      request,                                                   │
│      queryDeclareVO,                                            │
│      typeRef                                                    │
│  );                                                             │
└─────────────────────────────────────────────────────────────────┘
                         ↓ HTTP POST
┌─────────────────────────────────────────────────────────────────┐
│                     【业务服务】Controller                        │
│                                                                 │
│  @RequestMapping("/MbDeclare")                                  │
│  public class MbDeclareController {                             │
│                                                                 │
│      @RequestMapping("/query")                                  │
│      public ApiResponse query(@RequestBody QueryDeclareVO vo) {│
│          // 执行业务逻辑                                         │
│          return mbDeclareService.query(vo);                    │
│      }                                                          │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2.8 特殊组件详解

### 2.8.1 Swagger/Knife4j（API文档）

**依赖引入**：
```xml
<dependency>
    <groupId>com.github.xiaoymin</groupId>
    <artifactId>knife4j-spring-boot-starter</artifactId>
    <version>2.0.0</version>
</dependency>
```

**使用示例**：
```java
@RestController
@Api(value = "线下申报", tags = "线下申报")
@RequestMapping(value = "/MbDeclare")
public class MbDeclareApi {
    
    @ApiOperation(value = "查询线下申报记录",
                  notes = "根据条件查询线下申报记录列表")
    @RequestMapping(method = {RequestMethod.POST}, value = "/query")
    public ApiResponse query(@RequestBody QueryDeclareVO queryDeclareVO) {
        // ...
    }
}
```

**访问地址**：
- Knife4j文档：`http://IP:9001/doc.html`
- Swagger文档：`http://IP:9001/swagger-ui.html`

### 2.8.2 EasyExcel（Excel处理）

**依赖**：
```xml
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>easyexcel</artifactId>
    <version>3.2.1</version>
</dependency>
```

**典型用法**：
```java
// 导出Excel
EasyExcel.write(fileName, DemoData.class)
    .sheet("模板")
    .doWrite(data());

// 导入Excel
EasyExcel.read(fileName, DemoData.class, new DemoDataListener())
    .sheet()
    .headRowNumber(1)
    .doRead();
```

### 2.8.3 iTextPDF（PDF生成）

**依赖**：
```xml
<dependency>
    <groupId>com.itextpdf</groupId>
    <artifactId>itextpdf</artifactId>
    <version>5.5.13</version>
</dependency>
<dependency>
    <groupId>com.itextpdf</groupId>
    <artifactId>itext-asian</artifactId>
    <version>5.2.0</version>
</dependency>
```

**典型用法**：
```java
// 创建PDF文档
Document document = new Document();
PdfWriter.getInstance(document, new FileOutputStream("test.pdf"));
document.open();

// 添加中文字体
BaseFont bfChinese = BaseFont.createFont(
    "STSong-Light", "UniGB-UCS2-H", BaseFont.NOT_EMBEDDED
);
Font font = new Font(bfChinese, 12, Font.NORMAL);

// 添加内容
document.add(new Paragraph("门诊慢特病备案证明", font));
```

### 2.8.4 CXF WebService

**依赖**：
```xml
<dependency>
    <groupId>org.apache.cxf</groupId>
    <artifactId>cxf-spring-boot-starter-jaxws</artifactId>
    <version>3.2.5</version>
</dependency>
```

**典型配置**：
```java
@Configuration
public class CxfConfig {
    
    @Bean
    public ServletRegistrationBean<CXFServlet> dispatchServlet() {
        return new ServletRegistrationBean<>(
            new CXFServlet(), "/webservice/*"
        );
    }
    
    @Bean
    public Endpoint endpoint() {
        EndpointImpl endpoint = new EndpointImpl(bus, yourService);
        endpoint.publish("/yourService");
        return endpoint;
    }
}
```

### 2.8.5 FreeMarker + Flying Saucer（HTML转PDF）

**依赖**：
```xml
<dependency>
    <groupId>org.freemarker</groupId>
    <artifactId>freemarker</artifactId>
    <version>2.3.31</version>
</dependency>
<dependency>
    <groupId>org.xhtmlrenderer</groupId>
    <artifactId>flying-saucer-pdf-itext5</artifactId>
    <version>9.1.20</version>
</dependency>
```

**典型用法**：
```java
// 1. 渲染HTML模板
Configuration cfg = new Configuration(Configuration.VERSION_2_3_31);
Template template = cfg.getTemplate("template.ftl");
String htmlContent = FreeMarkerTemplateUtils.processTemplateIntoString(
    template, dataModel
);

// 2. HTML转PDF
ITextRenderer renderer = new ITextRenderer();
renderer.setDocumentFromString(htmlContent);
renderer.layout();
renderer.createPDF(outputStream);
```

---

# 附录：源码阅读指南

## A.1 关键文件位置速查

| 功能 | 文件路径 |
|-----|---------|
| **启动类** | `com.picchealth.LinkSpringBootApplication` |
| **配置文件** | `src/main/resources/application.yml` |
| **HTTP转发** | `com.picchealth.utils.HttpForwardUtil` |
| **权限拦截器** | `com.picchealth.config.interceptor.APIAuthorityFilter` |
| **Flag拦截器** | `com.picchealth.config.interceptor.FlagInterceptorConfig` |
| **XSS过滤器** | `com.picchealth.config.xssfilter.XssRequestFilter` |
| **加密AOP** | `com.picchealth.config.Encrypt.EncryptDecryptAop` |
| **跨域配置** | `com.picchealth.config.cors.GlobalCorsConfig` |
| **XXL-Job配置** | `com.picchealth.config.XxlJobConfig` |
| **定时任务** | `com.picchealth.module.schedualing.api.SchedulingXxlJob` |
| **登录API** | `com.picchealth.module.mb.api.LoginApi` |
| **慢病申报API** | `com.picchealth.module.mb.api.MbDeclareApi` |

## A.2 快速定位业务代码

```bash
# 查看所有API类
find src/main/java/com/picchealth/module -name "*Api.java" | head -20

# 查看某个模块的API
ls src/main/java/com/picchealth/module/mb/api/

# 查看配置文件
cat src/main/resources/application.yml

# 查看pom.xml
cat pom.xml

# 统计各模块代码量
find src/main/java/com/picchealth/module -name "*.java" | xargs wc -l | sort -rn | head -10
```

## A.3 关键配置项说明

```yaml
# Apollo配置中心（通过Apollo管理）
forward.url: http://业务服务地址:9091  # 业务服务地址
xxl.job.admin.addresses: http://xxl-job地址:8080  # 定时任务管理后台
redis.host: Redis服务器地址
redis.port: 6379

# 本地配置
spring.application.name: picc-mzmtb-gateway
server.port: 9001
```

---

# 总结

## 项目核心特点

1. **"前台接待"定位**：不直连数据库，通过HTTP转发处理请求
2. **四层安全防护**：Token验证 + Flag提取 + 接口授权 + XSS过滤
3. **国密算法支持**：SM2/AES字段加密，保护敏感数据
4. **丰富的工具链**：Excel/PDF/文件传输/定时任务
5. **统一配置管理**：Apollo配置中心集中管理配置
6. **微服务架构**：与业务服务、权限服务协同工作

## 技术亮点

| 亮点 | 说明 |
|-----|------|
| 无Mapper设计 | 解耦数据库访问，提高安全性 |
| ThreadLocal传递 | Flag等信息通过ThreadLocal在线程间传递 |
| AOP自动解密 | 通过注解自动解密加密字段 |
| XXL-Job定时任务 | 22个定时任务覆盖各类后台处理 |
| Knife4j文档 | 完善的API文档和调试界面 |

---

*文档生成时间：基于源码静态分析*
*如有疑问，请查阅源码注释或联系项目负责人*
