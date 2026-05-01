> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC门诊慢特病前台服务（picc-mzmtb-gateway）
# 安全与代码质量审计报告

> **审计日期**：2024年
> **项目名称**：picc-mzmtb-gateway（门诊慢特病业务管理信息系统-前台服务）
> **服务端口**：9001
> **项目规模**：809个Java文件，102个API接口
> **服务角色**：前台服务，不直连数据库，通过HTTP转发到后端业务服务

---

## 📋 执行摘要

| 审计维度 | 发现问题数 | 严重(P0) | 高危(P1) | 中危(P2) | 低危(P3) |
|---------|-----------|---------|---------|---------|---------|
| 安全审计 | 12 | 3 | 4 | 4 | 1 |
| 代码质量 | 8 | 1 | 2 | 3 | 2 |
| **合计** | **20** | **4** | **6** | **7** | **3** |

### 🔴 严重问题概览
1. **SM2加密密钥硬编码** - 私钥明文写在代码中
2. **AES加密密钥硬编码** - 密钥直接暴露
3. **SFTP默认密码硬编码** - `hellolevy`明文存储
4. **CORS配置严重漏洞** - 允许任意来源跨域访问

---

## 📖 第一部分：安全审计（面向小白的解释）

### 🔐 认证与授权机制分析

#### 1. APIAuthorityFilter 认证过滤器分析

**文件位置**：`com.picchealth.config.interceptor.APIAuthorityFilter.java`

**认证机制说明**（小白版）：
> 想象一个高级小区的门禁系统：每个住户都有两张卡——一张是"通行证Token"（证明你是这个小区的住户），另一张是"身份证ID"（证明你是谁）。
> 
> 这套系统会检查：
> - 你的通行证是不是真的（Token验证）
> - 你有没有权限进入这栋楼（URL权限检查）
> - 你是不是这栋楼的住户（用户ID和Token匹配）

**代码流程图**：
```
请求进入 → 路径是否排除？ → Token获取 → Token验证 → 权限检查 → 请求放行
                        ↓               ↓           ↓
                       放行          失败=拦截    失败=拦截
```

**保护范围**：
```java
@WebFilter(urlPatterns = {
    "/ppop/*", "/offline/*", "/drugstore/*", 
    "/MbDeclare/*", "/MbReview/*", "/v2/*",
    "/picchealth/*", "/filingMan/*"  // 共40+路径
})
```

**排除路径（无需认证）**：
- `/v2/Login/` - 登录接口
- `/v2/Doctor/` - 医生相关
- `/v2/vipMbDeclareForProf/` - 专家相关

**✅ 做得好的地方**：
1. 使用Redis存储Token，支持会话过期刷新（180秒）
2. URL权限精确匹配（支持动态参数）
3. 手机号与Token绑定校验（防止A用户用B的Token）
4. 添加了X-Frame-Options安全响应头

**⚠️ 存在的问题**：

---

### 🚨 P0-1：SM2加密密钥硬编码【严重】

**问题位置**：`com.picchealth.utils.Sm2Util.java`

**问题代码**：
```java
/**
 * 私钥 - 这应该是绝密信息！
 */
private static final String PRIVATE_KER = "00ced30f88fc9187c1777957e2613df69b28284cd7689e300f4db27f62a616b3d3";

/**
 * 公钥
 */
private static final String PUBLIC_KER = "0488bd65709c64c5c2262a2777ef0b1a2b0af0492b124f44e282ca9a0e34a935bfda26daf70df691b28a130c283918edcdaf573da95909176baa01ffaa9bb7380d";
```

**小白解释**：
> 就像把保险柜的密码直接写在门上！这意味着：
> 1. 任何能访问源代码的人都能解密所有加密数据
> 2. 密钥泄漏后无法轮换（必须修改代码重新部署）
> 3. 如果代码意外公开（如GitHub），所有加密数据立即失效

**风险等级**：🔴 严重

**影响范围**：
- 所有小程序用户的身份证号、登录凭证
- Token加密/解密机制完全失效

**学习要点**：
```java
// 方案1：使用配置文件
@Value("${sm2.private.key}")
private static String PRIVATE_KER;

// 方案2：使用密钥管理服务（如AWS KMS、阿里云KMS）
private static final String PRIVATE_KER = KeyManagementService.getPrivateKey("sm2-key-id");
```

---

### 🚨 P0-2：AES加密密钥硬编码【严重】

**问题位置**：`com.picchealth.utils.AesUtil.java`

**问题代码**：
```java
//密钥 (需要前端和后端保持一致) - 这是什么鬼注释？！
private static final String PRIVATE_KER = "abcdefgabcdefg12";
```

**小白解释**：
> 想象你和朋友约定了一个暗号"天王盖地虎"，但这个暗号：
> 1. 写在明信片上（代码里）
> 2. 全世界都能看到（开源或泄露）
> 3. 一旦知道就无法更换（硬编码）

**风险等级**：🔴 严重

**影响范围**：请求参数中加密的手机号、身份证号可被解密

**学习要点**：
```java
@Value("${aes.encryption.key}")
private static String PRIVATE_KER;

// 或使用密钥长度更强的密钥
private static final String PRIVATE_KER = System.getenv("AES_KEY");
```

---

### 🚨 P0-3：SFTP默认密码硬编码【严重】

**问题位置**：`com.picchealth.utils.SFTPUtils.java`

**问题代码**：
```java
@Value("${ftp.password:hellolevy}")  // 默认密码是 hellolevy
public void setPass(String passWord){
    pass = passWord;
}

@Value("${ftp.ip:10.252.68.236}")  // 硬编码IP地址
public void setIp(String ftpIp){
    ip = ftpIp;
}
```

**小白解释**：
> 这就像把服务器的门禁密码写在便利贴上贴在电脑上。万一这个代码：
> - 被新员工看到
> - 上传到GitHub
> - 被黑客扫描到
> 
> 服务器就直接门户大开！

**风险等级**：🔴 严重

**影响范围**：SFTP服务器（IP: 10.252.68.236）可能被未授权访问

**学习要点**：
```java
// 强制要求必须从环境变量或密钥管理服务获取
@Value("${ftp.password}")
public void setPass(String passWord) {
    if (passWord == null || passWord.isEmpty()) {
        throw new IllegalStateException("SFTP密码必须配置！");
    }
    pass = passWord;
}
```

---

### 🚨 P1-1：CORS跨域配置严重漏洞【高危】

**问题位置**：`com.picchealth.config.cors.GlobalCorsConfig.java`

**问题代码**：
```java
registry.addMapping("/**")    // 对所有路径开放
        .allowedOrigins("*")  // 允许所有来源访问！
        .allowCredentials(true)  // 允许携带Cookie
        .allowedMethods("GET","POST", "PUT", "DELETE")
        .allowedHeaders("*");   // 允许所有请求头
```

**小白解释**：
> 这就像你家的门：
> - 地址公开（/**）
> - 任何人都能进（*）
> - 还能复制你的钥匙带走（credentials=true）
> - 不用登记身份证（* headers）
> 
> 这意味着**任何网站**都可以假装成用户发起请求！

**⚠️ 特别危险的点**：
```java
.allowCredentials(true)  // 允许携带Cookie
.allowedOrigins("*")    // 但同时允许所有来源！
```
**这是一个矛盾的配置**：`credentials=true` 配合 `origins=*` 在浏览器中会失败，但逻辑上是严重漏洞。

**风险等级**：🟠 高危

**学习要点**：
```java
@Override
public void addCorsMappings(CorsRegistry registry) {
    registry.addMapping("/**")
            .allowedOrigins(
                "https://www.picchealth.com",
                "https://mzmtb.picchealth.com"
            )  // 只允许受信任的域名
            .allowCredentials(true)
            .allowedMethods("GET", "POST", "PUT", "DELETE")
            .allowedHeaders("*")
            .exposedHeaders("Content-disposition")  // 暴露需要的响应头
            .maxAge(3600);
}
```

---

### 🚨 P1-2：敏感Header全局转发【高危】

**问题位置**：`com.picchealth.utils.HttpForwardUtil.java`

**问题代码**：
```java
private HttpHeaders getHttpHeaders(HttpServletRequest request) {
    HttpHeaders headers = new HttpHeaders();
    Enumeration<String> names = request.getHeaderNames();
    while (names.hasMoreElements()) {
        String name = names.nextElement();
        headers.add(name, request.getHeader(name));  // 原样转发所有Header！
    }
    return headers;
}
```

**小白解释**：
> 这相当于：快递员把所有收到的包裹（包括写着你家地址的标签）原封不动地转送给下一家。
> 
> 如果攻击者发送这样的请求：
> ```
> Header: X-Forwarded-For: 127.0.0.1 (伪造IP)
> Header: Host: evil.com (伪造域名)
> Header: Authorization: Bearer xxx (窃取Token)
> ```
> 这些都会被转发到后端！

**风险等级**：🟠 高危

**影响范围**：所有HTTP转发请求（102个API接口）

**学习要点**：
```java
private HttpHeaders getHttpHeaders(HttpServletRequest request) {
    HttpHeaders headers = new HttpHeaders();
    // 只转发必要的、经过验证的Header
    headers.add("Content-Type", request.getContentType());
    headers.add("Accept", request.getHeader("Accept"));
    
    // Token单独处理，不从请求中直接获取
    String token = validateAndExtractToken(request);
    if (token != null) {
        headers.add(RequestConstant.HEAD_TOKEN, token);
    }
    
    return headers;
}
```

---

### 🚨 P1-3：XSS过滤器Cookie配置错误【高危】

**问题位置**：`com.picchealth.config.xssfilter.XssRequestFilter.java`

**问题代码**：
```java
((HttpServletResponse) response).setHeader("Set-Cookie",
    "cookiename=cookievalue; path=/; Domain=domainvaule;Max-age=seconds; HttpOnly");
//                                                                    ^^^^^^^^^^^^^
//                                                                 硬编码的错误Cookie
```

**小白解释**：
> 你的Cookie被设置成了 `cookiename=cookievalue`，这：
> 1. 是一个固定的假Cookie名
> 2. Domain写成"domainvaule"（字面意思就是"域名值"）
> 3. Max-age写成"seconds"（字面意思"秒数"）

**风险等级**：🟠 高危

**学习要点**：
```java
// 如果需要设置HttpOnly Cookie，应该：
Cookie sessionCookie = new Cookie("SESSION_ID", sessionId);
sessionCookie.setHttpOnly(true);
sessionCookie.setPath("/");
sessionCookie.setMaxAge(1800);  // 30分钟
response.addCookie(sessionCookie);

// 或者使用Spring Session
```

---

### 🚨 P1-4：RestTemplate无超时配置【高危】

**问题位置**：`com.picchealth.utils.HttpForwardUtil.java`

**问题代码**：
```java
@Autowired
private RestTemplate restTemplate;  // 没有配置超时

// 使用
ResponseEntity<T> responseEntity = restTemplate.exchange(prefix + url, ...);
```

**小白解释**：
> 想象你派快递员去送信，但没告诉他"等多久就放弃回家"。
> 
> 如果后端服务：
> - 卡住了（死锁）
> - 宕机了
> - 网络断了
> 
> 你的服务会**无限等待**，最终耗尽所有线程资源！

**风险等级**：🟠 高危

**影响范围**：所有HTTP转发请求

**学习要点**：
```java
@Bean
public RestTemplate restTemplate() {
    SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
    factory.setConnectTimeout(5000);      // 连接超时：5秒
    factory.setReadTimeout(10000);       // 读取超时：10秒
    factory.setBufferRequestBody(false);  // 大文件流式处理
    
    return new RestTemplate(factory);
}
```

---

### 🟡 P2-1：SSRF风险 - 后端地址可配置【中危】

**问题位置**：
- `com.picchealth.utils.HttpForwardUtil.java`
- `com.picchealth.module.ws.common.RestfulForwardUtil.java`

**问题代码**：
```java
@Value("${forwardUrl:http://localhost:9091}")  // 默认本地地址
private String prefix;

@Value("${forwardUrl:http://10.252.68.238:9091}")  // 硬编码内网IP
private String prefix;
```

**小白解释**：
> 虽然这里配置的是内网地址，但如果没有严格校验，理论上可以：
> 1. 攻击者通过某种方式改变配置
> 2. 让请求转发到恶意服务器
> 3. 窃取转发过程中的敏感数据

**风险等级**：🟡 中危

**学习要点**：
```java
@Value("${forwardUrl}")
private String prefix;

// 校验URL必须来自白名单
private static final List<String> ALLOWED_HOSTS = Arrays.asList(
    "10.252.68.238",
    "internal-backend.picchealth.com"
);

if (!isHostAllowed(prefix)) {
    throw new IllegalStateException("后端地址不在白名单中");
}
```

---

### 🟡 P2-2：异常信息泄露【中危】

**问题位置**：`com.picchealth.config.interceptor/APIAuthorityFilter.java`

**问题代码**：
```java
} catch (Exception e) {
    sendErrorResponse(response, 1002, "手机号与Token不匹配");
    log.info("手机号与Token不匹配", xcxString);  // 泄露了手机号
    return;
}
```

**小白解释**：
> 在日志中记录手机号可能导致：
> 1. 日志文件泄露用户手机号
> 2. 不符合《个人信息保护法》要求
> 3. 日志搜索可能暴露用户身份

**风险等级**：🟡 中危

**学习要点**：
```java
} catch (Exception e) {
    log.warn("Token validation failed for masked user");
    sendErrorResponse(response, 1002, "认证失败");
    return;
}
```

---

### 🟡 P2-3：ThreadLocal未清理【中危】

**问题位置**：`com.picchealth.config.interceptor/FlagInterceptorConfig.java`

**问题代码**：
```java
public boolean preHandle(...) {
    FlagLocal flagLocal = new FlagLocal();  // 每次请求创建新对象
    flagLocal.setFlag(flag);
    FlagUtils.setFlagLocal(flagLocal);
    return true;
}

public void afterCompletion(...) {
    FlagUtils.remove();  // 有清理
}
```

**小白解释**：
> 看起来有清理，但问题是每次请求都 `new FlagLocal()`，可能导致内存积累。
> 如果有异常导致 `afterCompletion` 没被调用，就会有内存泄漏。

**风险等级**：🟡 中危

---

### 🟡 P2-4：SecurityHeaders不完整【中危】

**问题位置**：`com.picchealth.config/interceptor/APIAuthorityFilter.java`

**问题代码**：
```java
private void addSecurityHeaders(HttpServletResponse response) {
    response.setHeader("X-Frame-Options", "SAMEORIGIN");
    // 缺少其他重要安全头！
}
```

**应该添加的安全头**：
| Header | 作用 | 当前状态 |
|--------|------|---------|
| X-Content-Type-Options | 防止MIME类型嗅探 | ❌ 缺失 |
| X-XSS-Protection | XSS过滤器（旧浏览器） | ❌ 缺失 |
| Content-Security-Policy | 内容安全策略 | ❌ 缺失 |
| Strict-Transport-Security | 强制HTTPS | ❌ 缺失 |
| X-Frame-Options | 点击劫持防护 | ✅ 已有 |

**学习要点**：
```java
private void addSecurityHeaders(HttpServletResponse response) {
    response.setHeader("X-Frame-Options", "SAMEORIGIN");
    response.setHeader("X-Content-Type-Options", "nosniff");
    response.setHeader("X-XSS-Protection", "1; mode=block");
    response.setHeader("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
    // CSP需要根据实际情况配置
}
```

---

## 📖 第二部分：代码质量审计

### 📊 统计数据

| 指标 | 数值 | 评价 |
|------|------|------|
| Java文件总数 | 809 | - |
| API接口数 | 102 | 较多 |
| VO类数量 | 339 | ⚠️ 过多 |
| 最大文件行数 | 1212 | ⚠️ 过大 |
| System.out.println | 60处 | ❌ 应该用日志 |
| 空catch块 | 0 | ✅ 好 |

---

### 🔴 P1-5：超长方法【高危】

**问题文件**：`com.picchealth.module.mb.api/VipMBDeclareXcxApi.java`

**文件大小**：1212行

**小白解释**：
> 想象一本1212页的说明书！这意味着：
> 1. 没有人能完全理解这个文件
> 2. 修改一处可能影响另一处
> 3. 调试困难，测试覆盖不全
> 4. 违背"单一职责原则"

**建议拆分**：
```
VipMBDeclareXcxApi.java (1212行)
├── VipMBDeclareXcxApi.java (主入口，~200行)
├── VipMBDeclareXcxService.java (业务逻辑，~500行)
├── VipMBDeclareXcxValidator.java (参数校验)
└── VipMBDeclareXcxMapper.java (数据映射)
```

---

### 🟠 P2-5：VO类爆炸【中危】

**问题统计**：
- VO类数量：339个
- 总Java文件：809个
- VO占比：42%

**问题分析**：
```java
// 典型的VO膨胀
/module/mb/vo/VipInfoAccountVo.java - 602行
/module/mb/dto/VipAccountInfoDto.java - 528行
/module/mb/vo/VipDrugXYa.java - 大量字段重复
```

**小白解释**：
> 339个VO就像339个文件夹，但它们很多内容重复。
> 比如"用户信息"可能有5个版本：
> - `VipUserVo` - 给前端展示
> - `VipUserDto` - 内部传输
> - `VipUserRequest` - 请求参数
> - `VipUserResponse` - 响应参数
> - `VipUserDetail` - 详情页用

**修复建议**：
```java
// 统一使用DTO进行内部传输
// 只在API层做VO转换
// 使用继承减少重复字段
public class VipUserVo {
    private Long id;
    private String name;
    // 通用字段...
}

public class VipUserDetailVo extends VipUserVo {
    private String extraInfo;
    // 详情特有的字段...
}
```

---

### 🟠 P2-6：System.out.println残留【中危】

**问题统计**：60处System.out.println

**问题代码示例**：
```java
System.out.println("excludePaths: " + excludePaths);  // APIAuthorityFilter
System.out.println("url: " + url);  // HttpClient
System.out.println("response: " + response);  // HttpClient
```

**小白解释**：
> System.out.println的问题：
> 1. 无法控制日志级别（开发/生产都要输出）
> 2. 无法输出到文件（只在控制台显示）
> 3. 无法异步处理（影响性能）
> 4. 无法追溯问题（没有时间戳、线程信息）

**学习要点**：
```java
// 替换为
log.info("API Authority Filter initialized with excludePaths: {}", excludePaths);
log.debug("Request URL: {}", url);
log.debug("Response: {}", response);
```

---

### 🟡 P3-1：代码重复 - 加密工具类

**问题位置**：
- `Sm2Util.java` - SM2加密
- `AesUtil.java` - AES加密

**问题**：
- 两个工具类各自独立
- 没有统一的加密服务接口
- 密钥分散管理

**建议**：
```java
public interface EncryptionService {
    String encrypt(String data);
    String decrypt(String data);
}

@Service
public class EncryptionServiceImpl implements EncryptionService {
    @Value("${encryption.sm2.private}")
    private String sm2PrivateKey;
    
    @Value("${encryption.aes.key}")
    private String aesKey;
    
    // 根据数据类型选择加密方式
}
```

---

### 🟡 P3-2：HTTP客户端重复

**问题位置**：
- `HttpForwardUtil.java` - 使用RestTemplate
- `HttpClient.java` - 使用Apache HttpClient
- `RestfulForwardUtil.java` - 又一个RestTemplate封装

**问题**：同一个项目使用3种HTTP客户端

---

## 📖 第三部分：三服务安全对比

### 对比表格

| 审计项 | 权限服务 | 业务服务 | 前台服务(本项目) |
|--------|---------|---------|----------------|
| 硬编码密码 | 无 | 有 | **有（SM2/AES/SFTP）** |
| Spring Security | 有 | **无** | 无（自定义Filter） |
| XSS防护 | 有 | 无 | **有（jsoup）** |
| SQL注入防护 | 有 | 无 | N/A（不直连DB） |
| CORS配置 | - | - | **危险（*）** |
| 敏感Header处理 | - | - | **全转发** |
| 日志脱敏 | - | - | **部分泄露** |
| 安全Header | - | - | **不完整** |
| 加密方式 | - | - | SM2+AES混用 |

### 结论

**前台服务 vs 业务服务**：
- 前台服务：认证机制更完善，但存在**密钥硬编码**致命问题
- 业务服务：缺乏安全防护，但无密钥泄露风险

**最需要修复的问题**：
1. 🚨 SM2/AES私钥硬编码（最高优先级）
2. 🚨 CORS配置漏洞
3. 🚨 SFTP密码硬编码

---

## 📖 第四部分：修复优先级与时间估算

### 修复计划

| 优先级 | 问题 | 修复工时 | 风险 |
|-------|------|---------|------|
| P0-1 | SM2密钥硬编码 | 4h | 高（需同步前端） |
| P0-2 | AES密钥硬编码 | 2h | 中 |
| P0-3 | SFTP密码硬编码 | 2h | 低 |
| P1-1 | CORS配置 | 1h | 低 |
| P1-2 | Header转发 | 4h | 中 |
| P1-3 | Cookie配置 | 1h | 低 |
| P1-4 | RestTemplate超时 | 2h | 低 |
| P2-1~4 | 中危问题 | 8h | 低 |
| P3-1~2 | 代码质量问题 | 16h | 低 |

**总修复工时**：约40小时

---

## 📎 附录：快速修复清单

### ✅ 可立即修复（无需测试）

```bash
# 1. 移除代码中的System.out.println
grep -rn "System.out.println" src/ | sed 's/System.out.println/log.info/g'

# 2. 完善安全响应头
# 在APIAuthorityFilter.java中添加

# 3. CORS白名单配置
# 替换 allowedOrigins("*")
```

### ⚠️ 需要测试后上线

```bash
# 1. 密钥外部化
# 移动到配置中心或环境变量

# 2. Header白名单
# 修改getHttpHeaders方法

# 3. RestTemplate超时
# 添加RestTemplate Bean配置
```

---

**报告生成工具**：Coze AI 代码审计助手
**适用读者**：开发人员、项目经理、安全工程师
