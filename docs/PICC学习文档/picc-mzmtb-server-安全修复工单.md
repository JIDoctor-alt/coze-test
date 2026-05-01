> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC门诊慢特病业务管理系统 - 安全修复工单

> 📅 工单生成日期：2024年  
> 📁 项目：`picc-mzmtb-server`  
> 🔧 技术栈：Spring Boot + MyBatis + Activiti6 + GaussDB + Redis + Apollo  
> 👥 目标读者：零基础开发人员  

---

## 📊 工单概览

| 优先级 | 问题数量 | 涉及安全 | 涉及代码质量 |
|--------|----------|----------|--------------|
| **P0 - 立即处理** | 7个 | 5个 | 2个 |
| **P1 - 本周处理** | 15个 | 8个 | 7个 |
| **P2 - 本月处理** | 10个 | 5个 | 5个 |
| **总计** | **33个** | **18个** | **15个** |

---

# 🚨 第一批：P0问题工单（必须立即处理）

---

## 工单编号：SEC-SERVER-P0-001
### 问题标题：未使用Spring Security标准化安全框架
**风险等级**：🔴 P0 - 极高危  
**影响范围**：全系统107个API接口  
**预估工时**：3-5人天  

### 问题描述（小白化解释）

> 🏠 **危险程度**：就像一个高档小区没有安装正规的门禁系统，而是让保安自己用纸笔记录谁可以进门。没有统一的管理标准，权限管理混乱。

**具体表现**：
- 系统用自己写的Interceptor来做权限判断
- 权限代码散落在各个地方，难以统一管理
- 如果要修改权限规则，需要改代码而不是改配置

### 问题分析（步骤化）

```
第一步：添加Spring Security依赖到pom.xml
第二步：创建SecurityConfig配置类
第三步：配置JWT认证过滤器
第四步：迁移现有Token逻辑到新框架
第五步：在Controller方法上添加权限注解
```

### 问题原理骨架

```java
// ===== 第一步：pom.xml添加依赖 =====
// 在pom.xml的dependencies节点中添加：
/*
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
*/

// ===== 第二步：创建SecurityConfig.java =====
// 文件位置：src/main/java/com/picchealth/config/SecurityConfig.java

package com.picchealth.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableGlobalMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
@EnableGlobalMethodSecurity(prePostEnabled = true) // 启用@PreAuthorize注解
public class SecurityConfig {

    // JWT认证过滤器（需要自己创建，后面有详细代码）
    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    public SecurityConfig(JwtAuthenticationFilter jwtAuthenticationFilter) {
        this.jwtAuthenticationFilter = jwtAuthenticationFilter;
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // 关闭CSRF（如果使用JWT token，可以关闭；后续会修复CSRF问题）
            .csrf().disable()
            
            // 不需要session（无状态API）
            .sessionManagement()
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
                .and()
            
            // 配置权限规则
            .authorizeRequests()
                // 公共接口放行
                .antMatchers("/api/public/**", "/health").permitAll()
                // 管理后台需要ADMIN角色
                .antMatchers("/api/admin/**").hasRole("ADMIN")
                // 其他接口需要登录
                .anyRequest().authenticated()
                .and()
            
            // 添加JWT过滤器
            .addFilterBefore(jwtAuthenticationFilter, 
                UsernamePasswordAuthenticationFilter.class);
        
        return http.build();
    }

    // 使用BCrypt加密（后续密码迁移会用到）
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);
    }
}
```

### 验证方式

1. ✅ 启动应用后，未登录访问 `/api/**` 应返回 401 Unauthorized
2. ✅ 使用正确Token访问应返回200
3. ✅ 登录接口 `/api/public/**` 无需认证即可访问
4. ✅ 没有权限的用户访问受限接口应返回 403 Forbidden

---

## 工单编号：SEC-SERVER-P0-002
### 问题标题：硬编码FTP默认密码（敏感信息泄露）
**风险等级**：🔴 P0 - 极高危  
**影响范围**：文件上传功能  
**预估工时**：1人天  

### 问题描述（小白化解释）

> 🔑 **危险程度**：就像把家门钥匙粘在门口的脚垫下面，谁都能找到。虽然你告诉别人"应该没人会用这把钥匙"，但小偷只要翻脚垫就能进门。

**发现的危险代码**：
```java
// FTPFileUtil_xcx.java 第44行
@Value("${xcxftp.password:hmlink@123}")  // 默认密码：hmlink@123

// CommonUtils.java 第37行  
@Value("${ftp.password:hellolevy}")     // 默认密码：hellolevy

// MbXcxValueUtil.java
@Value("${ftp.password:hellolevy}")     // 默认密码：hellolevy
```

### 问题分析（步骤化）

```
第一步：在Apollo配置中心创建敏感配置项
第二步：修改代码，移除所有默认密码
第三步：修改启动脚本，从环境变量读取密码
第四步：验证FTP连接正常
```

### 问题原理

```java
// ===== 修改前（危险代码）=====
@Value("${xcxftp.password:hmlink@123}")  // ❌ 有默认值
private String ftpPassword;

// ===== 修改后（安全代码）=====
@Value("${xcxftp.password}")  // ✅ 无默认值，配置缺失则启动失败
private String ftpPassword;
```

```yaml
# ===== Apollo配置中心 application-prod.yml =====

# 生产环境FTP配置（不要提交到git！）
ftp:
  host: ${FTP_SERVER_IP}
  port: 21
  username: ${FTP_USERNAME}
  password: ${FTP_PASSWORD}  # 从环境变量读取

xcxftp:
  host: ${XCX_FTP_SERVER_IP}
  port: 21
  username: ${XCX_FTP_USERNAME}
  password: ${XCX_FTP_PASSWORD}  # 从环境变量读取
```

```bash
# ===== 启动脚本 start.sh =====
#!/bin/bash

# 从密钥管理系统获取密码（示例）
# export FTP_PASSWORD=$(vault read -field=password secret/picc/ftp)
export FTP_PASSWORD="你的强密码(至少16位，包含大小写字母数字特殊字符)"
export XCX_FTP_PASSWORD="另一个强密码"

java -jar app.jar --spring.profiles.active=prod
```

### 验证方式

1. ✅ 代码中搜索 `hmlink@123`、`hellolevy` 无结果
2. ✅ 搜索 `password:hmlink`、`password:hellolevy` 无结果
3. ✅ 配置文件中无明文密码
4. ✅ 应用能正常启动并连接FTP服务器

---

## 工单编号：SEC-SERVER-P0-003
### 问题标题：硬编码第三方API密钥
**风险等级**：🔴 P0 - 极高危  
**影响范围**：图片质检、OCR等第三方服务  
**预估工时**：1人天  

### 问题描述（小白化解释）

> 💳 **危险程度**：就像把银行卡密码写在卡背面，被人捡到就能直接取钱。这些API密钥一旦泄露，攻击者可以免费使用你的云服务资源。

**发现的危险代码**：
```java
// ImageQualityAssessmentUtil.java 第89-90行
String secretId = "7839c25a";    // ❌ 硬编码密钥
String secretKey = "7c16d7d5";   // ❌ 硬编码密钥

// application-sit.yml 第102-122行
lexus: {key: Ezk6ZM1MaUYq16xqxYP8cE==, secret: +E06YaZlF05o16CPj6/0Fw==}
causacloud: {key: 0123456, secret: 0123456789ABCDEF}
oasi: {appkey: dc8730151eb546ce8085d255e2b3d736, secret: b835002645204a0595bc9d3a9598e731}
```

### 问题分析（步骤化）

```
第一步：禁用或更换已泄露的API密钥
第二步：将密钥迁移到Apollo配置中心
第三步：修改代码，从配置读取
第四步：配置CI/CD，确保密钥不进入代码仓库
```

### 问题原理

```java
// ===== 修改前（危险代码）=====
// ImageQualityAssessmentUtil.java
String secretId = "7839c25a";
String secretKey = "7c16d7d5";

// ===== 修改后（安全代码）=====
// 在类中添加配置注入
@Value("${image.qa.secretId}")
private String secretId;

@Value("${image.qa.secretKey}")  
private String secretKey;

// 或者使用更安全的方式 - 加密配置
@EncryptedValue("${image.qa.secretKey}")
private String secretKey;
```

```yaml
# ===== Apollo配置中心 =====

# SIT环境
image-qa:
  secretId: ${IMAGE_QA_SECRET_ID}
  secretKey: ${IMAGE_QA_SECRET_KEY}

# 第三方服务配置（生产环境）
lexus:
  key: ${LEXUS_API_KEY}
  secret: ${LEXUS_API_SECRET}
  
causacloud:
  key: ${CAUSACLOUD_API_KEY}
  secret: ${CAUSACLOUD_API_SECRET}
```

### 验证方式

1. ✅ 代码中无硬编码的密钥字符串
2. ✅ 第三方服务调用正常
3. ✅ 新密钥已生效，旧密钥已禁用
4. ✅ 密钥不在git历史记录中

---

## 工单编号：SEC-SERVER-P0-004
### 问题标题：缺失CSRF防护
**风险等级**：🔴 P0 - 极高危  
**影响范围**：所有表单提交接口  
**预估工时**：2人天  

### 问题描述（小白化解释）

> 🎣 **危险程度**：就像你登录网银后，攻击者诱骗你点击一个链接，这个链接会自动向你账户转账。没有CSRF防护，银行无法区分是你本人操作还是钓鱼攻击。

**具体场景**：
- 用户登录后访问恶意网站
- 恶意网站自动发起请求到你的系统
- 系统会认为是用户本人操作
- 可能导致用户数据被篡改

### 问题分析（步骤化）

```
第一步：创建CSRF Token生成和验证工具类
第二步：修改登录接口，返回CSRF Token到Cookie
第三步：前端获取Cookie中的Token，每次请求携带
第四步：后端验证Token有效性
第五步：测试验证
```

### 问题原理

```java
// ===== 第一步：创建CsrfTokenUtil.java =====

package com.picchealth.utils.security;

import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.stereotype.Component;

import java.security.SecureRandom;
import java.util.Base64;

@Component
public class CsrfTokenUtil {

    private static final String CSRF_TOKEN_NAME = "XSRF-TOKEN";
    private static final String CSRF_HEADER_NAME = "X-XSRF-TOKEN";
    private static final SecureRandom SECURE_RANDOM = new SecureRandom();
    
    // Token有效期：2小时
    private static final long TOKEN_VALIDITY = 2 * 60 * 60 * 1000;

    /**
     * 生成CSRF Token并写入Cookie
     */
    public String generateToken(HttpServletRequest request, HttpServletResponse response) {
        String token = generateSecureToken();
        
        // 写入HttpOnly Cookie
        Cookie cookie = new Cookie(CSRF_TOKEN_NAME, token);
        cookie.setHttpOnly(false); // 前端需要读取，设为false（配合XSS防护）
        cookie.setPath("/");
        cookie.setMaxAge((int) (TOKEN_VALIDITY / 1000));
        cookie.setSecure(request.isSecure());
        response.addCookie(cookie);
        
        return token;
    }

    /**
     * 验证请求中的Token
     */
    public boolean validateToken(HttpServletRequest request) {
        // 从请求头获取Token
        String requestToken = request.getHeader(CSRF_HEADER_NAME);
        
        // 从Cookie获取Token
        String cookieToken = null;
        Cookie[] cookies = request.getCookies();
        if (cookies != null) {
            for (Cookie cookie : cookies) {
                if (CSRF_TOKEN_NAME.equals(cookie.getName())) {
                    cookieToken = cookie.getValue();
                    break;
                }
            }
        }
        
        // 两者必须匹配
        return requestToken != null 
            && requestToken.equals(cookieToken)
            && !requestToken.isEmpty();
    }

    /**
     * 生成安全的随机Token
     */
    private String generateSecureToken() {
        byte[] bytes = new byte[32];
        SECURE_RANDOM.nextBytes(bytes);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
    }
}
```

```java
// ===== 第二步：创建CSRF拦截器 =====

package com.picchealth.config.security;

import com.picchealth.utils.security.CsrfTokenUtil;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

@Component
@Slf4j
public class CsrfInterceptor implements HandlerInterceptor {

    private final CsrfTokenUtil csrfTokenUtil;

    public CsrfInterceptor(CsrfTokenUtil csrfTokenUtil) {
        this.csrfTokenUtil = csrfTokenUtil;
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        // 只验证非GET请求
        if (!"GET".equalsIgnoreCase(request.getMethod())) {
            if (!csrfTokenUtil.validateToken(request)) {
                log.warn("CSRF验证失败，IP: {}, URI: {}", 
                    request.getRemoteAddr(), request.getRequestURI());
                response.setStatus(HttpServletResponse.SC_FORBIDDEN);
                response.getWriter().write("{\"code\":403,\"message\":\"CSRF验证失败\"}");
                return false;
            }
        }
        return true;
    }
}
```

```java
// ===== 第三步：修改SecurityConfig，集成CSRF =====

@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {

    @Autowired
    private CsrfInterceptor csrfInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(csrfInterceptor)
            .addPathPatterns("/api/**")  // 只对API生效
            .excludePathPatterns("/api/public/**");  // 排除公共接口
    }
    
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
            // 启用CSRF（使用自定义Token验证）
            .csrf()
                .disable()  // 禁用Spring Security的CSRF，使用自定义实现
                .and()
            // ... 其他配置
    }
}
```

### 验证方式

1. ✅ 登录后，Cookie中有 `XSRF-TOKEN`
2. ✅ GET请求不验证Token
3. ✅ POST请求带正确Token可以成功
4. ✅ POST请求不带Token返回403
5. ✅ 跨站POST请求（不带Token）被拦截

---

## 工单编号：SEC-SERVER-P0-005
### 问题标题：缺失XSS防护
**风险等级**：🔴 P0 - 极高危  
**影响范围**：所有用户输入的数据展示  
**预估工时**：2人天  

### 问题描述（小白化解释）

> 🖥️ **危险程度**：就像论坛允许用户发"代码"，而不做任何过滤。其他用户打开这个帖子时，攻击者的JavaScript代码就会在受害者浏览器执行，偷走Cookie。

**具体场景**：
- 用户提交：`<script>alert('XSS')</script>`
- 没有防护时，这段代码会在所有查看者浏览器执行
- 攻击者可以窃取用户Cookie，劫持账户

### 问题分析（步骤化）

```
第一步：添加XSS防护依赖（hutool或owasp）
第二步：创建XSS过滤工具类
第三步：创建全局请求参数过滤
第四步：在数据输出时统一转义
第五步：添加单元测试验证
```

### 问题原理

```java
// ===== pom.xml添加依赖 =====

<!-- Hutool工具类（包含XSS防护） -->
<dependency>
    <groupId>cn.hutool</groupId>
    <artifactId>hutool-all</artifactId>
    <version>5.8.22</version>
</dependency>

<!-- 或使用OWASP HTML Sanitizer -->
<dependency>
    <groupId>com.googlecode.owasp-java-html-sanitizer</groupId>
    <artifactId>owasp-java-html-sanitizer</artifactId>
    <version>20220608.1</version>
</dependency>
```

```java
// ===== XssUtil.java 工具类 =====

package com.picchealth.utils.security;

import cn.hutool.core.util.StrUtil;
import cn.hutool.http.html.XssUtil;
import org.springframework.stereotype.Component;

@Component
public class XssUtil {

    /**
     * 过滤HTML危险标签和脚本
     * 
     * @param text 原始文本
     * @return 过滤后的安全文本
     */
    public static String filter(String text) {
        if (StrUtil.isEmpty(text)) {
            return text;
        }
        
        // 使用Hutool的XSS过滤
        // 会移除 <script>、<iframe> 等危险标签
        // 会将 < 转义为 &lt;
        return XssUtil.filterHtml(text);
    }

    /**
     * 过滤JSON中的XSS
     */
    public static String filterForJson(String json) {
        if (StrUtil.isEmpty(json)) {
            return json;
        }
        // 移除script标签和事件属性
        String filtered = json;
        filtered = filtered.replaceAll("<script[^>]*?>.*?</script>", "");
        filtered = filtered.replaceAll("javascript:", "");
        filtered = filtered.replaceAll("on\\w+\\s*=", "");
        return filtered;
    }

    /**
     * 检查是否包含XSS风险
     */
    public static boolean containsXss(String text) {
        if (StrUtil.isEmpty(text)) {
            return false;
        }
        String lowerText = text.toLowerCase();
        return lowerText.contains("<script") 
            || lowerText.contains("javascript:")
            || lowerText.matches(".*on\\w+\\s*=.*");
    }
}
```

```java
// ===== GlobalXssFilter.java 全局过滤器 =====

package com.picchealth.config.filter;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.picchealth.utils.security.XssUtil;
import jakarta.servlet.*;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

@Component
@Slf4j
public class GlobalXssFilter implements Filter {

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public void doFilter(ServletRequest request, Response response, FilterChain chain) 
            throws IOException, ServletException {
        
        HttpServletRequest httpRequest = (HttpServletRequest) request;
        
        // 检测到XSS攻击时阻止请求
        Map<String, String[]> params = httpRequest.getParameterMap();
        for (String key : params.keySet()) {
            String[] values = params.get(key);
            for (String value : values) {
                if (XssUtil.containsXss(value)) {
                    log.warn("检测到XSS攻击, 参数: {}, IP: {}", 
                        key, httpRequest.getRemoteAddr());
                    
                    Map<String, Object> result = new HashMap<>();
                    result.put("code", 400);
                    result.put("message", "请求参数包含非法字符");
                    
                    response.setContentType("application/json");
                    response.getWriter().write(objectMapper.writeValueAsString(result));
                    return;
                }
            }
        }
        
        // 继续处理请求（使用XSS过滤后的包装器）
        chain.doFilter(new XssRequestWrapper(httpRequest), response);
    }
}
```

```java
// ===== XssRequestWrapper.java 请求包装器 =====

package com.picchealth.config.filter;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletRequestWrapper;
import com.picchealth.utils.security.XssUtil;

public class XssRequestWrapper extends HttpServletRequestWrapper {

    public XssRequestWrapper(HttpServletRequest request) {
        super(request);
    }

    @Override
    public String getParameter(String name) {
        String value = super.getParameter(name);
        return XssUtil.filter(value);
    }

    @Override
    public String[] getParameterValues(String name) {
        String[] values = super.getParameterValues(name);
        if (values != null) {
            for (int i = 0; i < values.length; i++) {
                values[i] = XssUtil.filter(values[i]);
            }
        }
        return values;
    }
}
```

### 验证方式

1. ✅ 提交 `<script>alert(1)</script>` 被自动过滤
2. ✅ 在页面上显示 `<script>` 时不会执行
3. ✅ 各种XSS攻击向量都被拦截
4. ✅ 正常HTML内容（如文章内容）可以正确显示

---

## 工单编号：SEC-SERVER-P0-006
### 问题标题：超级上帝类（代码行数过长）
**风险等级**：🔴 P0 - 极高危  
**影响范围**：代码可维护性  
**预估工时**：持续重构（3-4周）  

### 问题描述（小白化解释）

> 🏗️ **危险程度**：就像一个人要负责盖一整栋摩天大楼的所有工作：打地基、砌墙、布线、装修、通风...一个人根本无法有效管理，出了问题也不知道找谁。

**问题文件清单**：
| 文件 | 行数 | 方法数 | 危险等级 |
|------|------|--------|----------|
| `ChronicManageServiceImpl.java` | **12,507** | 109个 | 🔴 致命 |
| `VipMbdeclareInfoServiceImpl.java` | **12,225** | 172个 | 🔴 致命 |
| `VipMbdeclareApprovalServiceImpl.java` | 6,297 | 100+ | 🔴 严重 |
| `SLExcelServiceImpl.java` | 4,531 | 80+ | 🟠 高危 |
| `VipMbuserExtServiceImpl.java` | 3,707 | 60+ | 🟠 高危 |

### 问题分析（步骤化）

```
第一步：识别类的职责边界（按业务领域拆分）
第二步：创建新的Service类
第三步：使用组合模式调用拆分后的Service
第四步：逐步迁移方法
第五步：删除原类中的已迁移方法
第六步：更新所有调用方
```

### 问题原理示例

```java
// ===== 重构前：12507行的ChronicManageServiceImpl =====

@Service
public class ChronicManageServiceImpl {
    // 109个方法，全部混在一起
    // ❌ 申报方法、审批方法、统计方法、导出方法...
    
    public void createChronic() { ... }
    public void approveChronic() { ... }
    public void exportChronic() { ... }
    public void statisticsChronic() { ... }
    // ... 100多个方法
}
```

```java
// ===== 重构后：按职责拆分 =====

// 1. 核心服务类（负责编排）
@Service
@Slf4j
public class ChronicManageService {
    
    // 注入拆分后的服务
    @Autowired private ChronicDeclareService declareService;
    @Autowired private ChronicApprovalService approvalService;
    @Autowired private ChronicStatisticsService statisticsService;
    @Autowired private ChronicExportService exportService;
    
    // 核心业务编排方法
    public void processChronic(Long id) {
        log.info("开始处理慢特病申报: id={}", id);
        
        // 调用各个子服务
        declareService.validate(id);
        approvalService.review(id);
        statisticsService.record(id);
    }
}

// 2. 申报服务（只负责申报相关）
@Service
@Slf4j
public class ChronicDeclareService {
    
    // 申报相关方法（约30个）
    
    public void validate(Long id) { ... }
    public void create(ChronicDeclareDTO dto) { ... }
    public void update(ChronicDeclareDTO dto) { ... }
    public void cancel(Long id) { ... }
}

// 3. 审批服务（只负责审批相关）
@Service
@Slf4j
public class ChronicApprovalService {
    
    // 审批相关方法（约30个）
    
    public void review(Long id) { ... }
    public void approve(Long id, ApprovalDTO dto) { ... }
    public void reject(Long id, String reason) { ... }
}

// 4. 统计服务（只负责统计相关）
@Service
@Slf4j
public class ChronicStatisticsService {
    
    // 统计相关方法（约25个）
    
    public void record(Long id) { ... }
    public MonthlyStatDTO getMonthlyStat() { ... }
}

// 5. 导出服务（只负责导出相关）
@Service
@Slf4j
public class ChronicExportService {
    
    // 导出相关方法（约20个）
    
    public byte[] exportToExcel(ExportQuery query) { ... }
    public byte[] exportToPdf(Long id) { ... }
}
```

### 验证方式

1. ✅ 每个Service类不超过1000行
2. ✅ 每个类的方法不超过20个
3. ✅ 每个类有明确的单一职责
4. ✅ 所有单元测试通过
5. ✅ 功能测试全部通过

---

## 工单编号：SEC-SERVER-P0-007
### 问题标题：零缓存使用（性能问题）
**风险等级**：🔴 P0 - 极高危  
**影响范围**：系统性能和数据库压力  
**预估工时**：3-5人天  

### 问题描述（小白化解释）

> 🍳 **危险程度**：就像每次做饭都要重新去菜市场买菜，而不是把常用的菜放在冰箱里。每次查询数据库都要重新执行SQL，效率很低。

**具体表现**：
- 字典数据每次请求都查数据库
- 用户信息每次都重新加载
- 热点数据没有缓存
- 数据库压力巨大

### 问题分析（步骤化）

```
第一步：添加Spring Cache和Redis依赖
第二步：配置Redis缓存
第三步：在高频访问的Service方法上添加缓存注解
第四步：配置缓存策略（过期时间、容量等）
第五步：监控缓存命中率
```

### 问题原理

```java
// ===== pom.xml添加依赖 =====

<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-cache</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

```java
// ===== CacheConfig.java 缓存配置 =====

package com.picchealth.config;

import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.cache.RedisCacheConfiguration;
import org.springframework.data.redis.cache.RedisCacheManager;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.RedisSerializationContext;
import org.springframework.data.redis.serializer.StringRedisSerializer;

import java.time.Duration;

@Configuration
@EnableCaching
public class CacheConfig {

    @Bean
    public RedisCacheManager cacheManager(RedisConnectionFactory factory) {
        // 默认配置
        RedisCacheConfiguration defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(30))  // 默认30分钟过期
            .serializeKeysWith(
                RedisSerializationContext.SerializationPair
                    .fromSerializer(new StringRedisSerializer()))
            .serializeValuesWith(
                RedisSerializationContext.SerializationPair
                    .fromSerializer(new GenericJackson2JsonRedisSerializer()))
            .disableCachingNullValues();  // 不缓存null值

        // 不同缓存的配置
        return RedisCacheManager.builder(factory)
            .cacheDefaults(defaultConfig)
            
            // 字典缓存：数据很少变化，缓存24小时
            .withCacheConfiguration("dict", 
                defaultConfig.entryTtl(Duration.ofHours(24)))
            
            // 用户缓存：设置短一些，10分钟
            .withCacheConfiguration("user", 
                defaultConfig.entryTtl(Duration.ofMinutes(10)))
            
            // 配置缓存：缓存5分钟
            .withCacheConfiguration("config", 
                defaultConfig.entryTtl(Duration.ofMinutes(5)))
            
            .build();
    }
}
```

```java
// ===== DictionaryService.java 使用缓存 =====

package com.picchealth.module.basedoc.service;

@Service
@Slf4j
public class DictionaryService {

    @Autowired
    private DictionaryDao dictionaryDao;

    /**
     * 查询字典项（带缓存）
     * 缓存key格式：dict:type:SEX
     * 缓存时间：24小时
     */
    @Cacheable(value = "dict", key = "#type + ':' + #code")
    public String getDictText(String type, String code) {
        log.info("查询字典（数据库）: type={}, code={}", type, code);
        return dictionaryDao.selectText(type, code);
    }

    /**
     * 获取字典列表（带缓存）
     */
    @Cacheable(value = "dict", key = "'list:' + #type")
    public List<Dictionary> getDictList(String type) {
        log.info("查询字典列表（数据库）: type={}", type);
        return dictionaryDao.selectList(type);
    }

    /**
     * 新增/修改字典时清除缓存
     */
    @CacheEvict(value = "dict", allEntries = true)
    public void saveOrUpdate(Dictionary dict) {
        dictionaryDao.saveOrUpdate(dict);
        log.info("字典已更新，缓存已清除: type={}", dict.getType());
    }
}
```

```java
// ===== UserService.java 使用缓存 =====

@Service
@Slf4j
public class UserService {

    @Autowired
    private UserDao userDao;

    /**
     * 查询用户（带缓存）
     * 先查缓存，缓存不存在再查数据库
     */
    @Cacheable(value = "user", key = "#userId")
    public User getUserById(Long userId) {
        log.info("查询用户（数据库）: userId={}", userId);
        return userDao.selectById(userId);
    }

    /**
     * 更新用户（同时更新缓存）
     */
    @CachePut(value = "user", key = "#user.id")
    public User updateUser(User user) {
        log.info("更新用户: userId={}", user.getId());
        return userDao.update(user);
    }

    /**
     * 删除用户（清除缓存）
     */
    @CacheEvict(value = "user", key = "#userId")
    public void deleteUser(Long userId) {
        log.info("删除用户: userId={}", userId);
        userDao.deleteById(userId);
    }
}
```

### 验证方式

1. ✅ 第一次查询会打印日志 "查询字典（数据库）"
2. ✅ 第二次查询不会打印 "查询字典（数据库）"（从缓存取）
3. ✅ 更新字典后，查询会重新从数据库获取
4. ✅ Redis中有对应的缓存key
5. ✅ 缓存命中率 > 80%

---

# 🟠 第二批：P1问题工单（本周处理）

---

## 工单编号：SEC-SERVER-P1-001
### 问题标题：Token校验逻辑可被绕过
**风险等级**：🟠 P1 - 高危  
**影响范围**：认证机制  
**预估工时**：1人天  

### 问题描述

> 🔌 **危险程度**：就像家里的电路总开关可以随时关闭，让所有防盗报警器失效。如果配置错误或忘记打开，生产环境将完全裸奔。

**原始代码**：
```java
// TokenInterceptorConfig.java
private boolean tokenInterceptFlag = false;  // ❌ 默认关闭

if (!tokenInterceptFlag) {
    return true;  // 直接放行，跳过Token校验
}
```

### 问题分析

```java
// 方案1：使用@Profile限制仅开发环境可用
@Profile("dev")
@Component
public class DevTokenInterceptorConfig {
    // 开发环境专用配置
}

// 方案2：移除开关，强制开启校验
// 删除tokenInterceptFlag变量及相关逻辑
```

### 验证方式
1. ✅ 生产环境必须进行Token校验
2. ✅ 未登录用户无法访问受保护接口

---

## 工单编号：SEC-SERVER-P1-002
### 问题标题：接口授权机制过于简单
**风险等级**：🟠 P1 - 高危  
**影响范围**：系统间接口调用  
**预估工时**：2人天  

### 问题描述

> 🏪 **危险程度**：就像一家店只检查顾客说"我是好人"就放行，没有核实身份证明。黑客可以轻易伪造请求头。

**原始代码**：
```java
// InterfaceGrantHandler.java
String password = request.getHeader("password");  // ❌ 直接比对密码
if (!outSystemCache.checkSystemAuthority(vipOutsystem)) {
    throw new BusinessException("非法认证系统");
}
```

### 问题分析

```java
// 使用HMAC签名验证
public boolean validateRequest(HttpServletRequest request) {
    String timestamp = request.getHeader("timestamp");
    String signature = request.getHeader("signature");
    String syscode = request.getHeader("syscode");
    
    // 1. 时间戳校验（5分钟有效）
    long requestTime = Long.parseLong(timestamp);
    if (Math.abs(System.currentTimeMillis() - requestTime) > 300000) {
        throw new BusinessException("100120", "请求已过期");
    }
    
    // 2. 签名验证
    String secret = outSystemCache.getSecret(syscode);
    String data = syscode + timestamp + request.getRequestURI();
    String expectedSign = HMACUtil.sign(data, secret);
    
    if (!signature.equals(expectedSign)) {
        throw new BusinessException("100120", "签名验证失败");
    }
    
    return true;
}
```

### 验证方式
1. ✅ 使用正确签名可以调用接口
2. ✅ 使用旧密码无法调用接口
3. ✅ 超时请求被拒绝

---

## 工单编号：SEC-SERVER-P1-003
### 问题标题：密码使用不安全的MD5加密
**风险等级**：🟠 P1 - 高危  
**影响范围**：用户账户安全  
**预估工时**：2人天  

### 问题描述

> 🍳 **危险程度**：就像把所有用户的密码都做成同一道菜（MD5后的固定值），攻击者只需破解一次，就能用这个固定值尝试登录所有用户账户。

**原始代码**：
```java
// EncryptionUtil.java
public static String encryptMD5(String password) throws Exception {
    return new String(MD5Util.encodeMD5(password));
}
```

### 问题分析

```java
// 使用BCryptPasswordEncoder（Spring Security提供）
@Configuration
public class PasswordConfig {
    @Bean
    public PasswordEncoder passwordEncoder() {
        // 使用BCrypt，强度因子12，自动随机盐
        return new BCryptPasswordEncoder(12);
    }
}

// 密码加密
@Autowired
private PasswordEncoder passwordEncoder;

public void register(User user) {
    // 新用户注册
    user.setPassword(passwordEncoder.encode(user.getPassword()));
}

public boolean login(String rawPassword, String encodedPassword) {
    // 登录验证
    return passwordEncoder.matches(rawPassword, encodedPassword);
}
```

### 验证方式
1. ✅ 新注册用户密码使用BCrypt加密
2. ✅ 登录验证使用BCrypt校验
3. ✅ 相同密码每次加密结果不同（因为有随机盐）

---

## 工单编号：SEC-SERVER-P1-004
### 问题标题：硬编码服务器IP地址
**风险等级**：🟠 P1 - 高危  
**影响范围**：配置管理  
**预估工时**：1人天  

### 问题描述

内部服务器IP硬编码在代码中，不利于环境迁移。

### 问题分析

```yaml
# 统一使用环境变量
ftp:
  ip: ${FTP_SERVER_IP}
ocr:
  callbackurl: ${OCR_CALLBACK_URL}
```

---

## 工单编号：SEC-SERVER-P1-005
### 问题标题：缺失API限流防护
**风险等级**：🟠 P1 - 高危  
**影响范围**：防DDoS攻击  
**预估工时**：2人天  

### 问题描述

> 🛒 **危险程度**：就像双11时，商场没有限制每个人购买数量。一个用户可以在1秒内下单10000次，导致服务器过载。

### 问题分析

```java
// 使用Guava RateLimiter
@Service
public class RateLimitService {
    
    private Map<String, RateLimiter> limiters = new ConcurrentHashMap<>();
    
    public boolean tryAcquire(String key, double permitsPerSecond) {
        limiters.putIfAbsent(key, RateLimiter.create(permitsPerSecond));
        return limiters.get(key).tryAcquire();
    }
}

// 在Controller中使用
@RestController
public class MbDeclareApi {
    
    @Autowired
    private RateLimitService rateLimitService;
    
    @PostMapping("/api/declare")
    public Result createDeclare(HttpServletRequest request) {
        String userId = getUserId(request);
        
        // 每用户每秒最多10次
        if (!rateLimitService.tryAcquire("user:" + userId, 10)) {
            return Result.error("操作太频繁，请稍后再试");
        }
        
        // 业务逻辑...
    }
}
```

### 验证方式
1. ✅ 正常频率请求不受影响
2. ✅ 超频率请求被限流并返回友好提示

---

## 工单编号：SEC-SERVER-P1-006 ~ SEC-SERVER-P1-015
### 问题标题：其他P1问题汇总

| 工单编号 | 问题 | 预估工时 | 简要方案 |
|----------|------|----------|----------|
| SEC-SERVER-P1-006 | 敏感信息返回未脱敏 | 2人天 | 添加VO字段脱敏注解 |
| SEC-SERVER-P1-007 | 179处System.out残留 | 1人天 | 全局替换为log.info |
| SEC-SERVER-P1-008 | SimpleDateFormat线程安全 | 1人天 | 使用ThreadLocal或Java8 DateTimeFormatter |
| SEC-SERVER-P1-009 | 大事务风险 | 持续优化 | 缩小事务范围，添加超时配置 |
| SEC-SERVER-P1-010 | 循环内查询数据库 | 持续优化 | 改为批量查询 |
| SEC-SERVER-P1-011 | 配置硬编码 | 持续优化 | 迁移到配置中心 |
| SEC-SERVER-P1-012 | 日志记录不足 | 持续优化 | 补充关键操作日志 |
| SEC-SERVER-P1-013 | 日志打印敏感信息 | 1人天 | 移除或脱敏 |
| SEC-SERVER-P1-014 | 缺少全局异常处理 | 1人天 | 添加@ControllerAdvice |
| SEC-SERVER-P1-015 | MyBatis SQL注入风险 | 0.5人天 | 确认全部使用#{} |

---

# 🟡 第三批：P2问题工单（本月处理）

---

## 工单编号：SEC-SERVER-P2-001 ~ SEC-SERVER-P2-010
### 问题标题：P2中危问题汇总

| 工单编号 | 问题 | 预估工时 | 简要方案 |
|----------|------|----------|----------|
| SEC-SERVER-P2-001 | MyBatis SQL注入风险 | 0.5人天 | 审计确认#{}使用 |
| SEC-SERVER-P2-002 | 日志打印敏感信息 | 1人天 | 代码审查脱敏 |
| SEC-SERVER-P2-003 | 缺少全局异常处理 | 1人天 | 添加@ControllerAdvice |
| SEC-SERVER-P2-004 | 配置硬编码 | 持续优化 | 迁移到Apollo |
| SEC-SERVER-P2-005 | 日志记录不足 | 持续优化 | 补充关键操作日志 |
| SEC-SERVER-P2-006 | 空catch块风险 | 0.5人天 | 添加日志记录 |
| SEC-SERVER-P2-007 | 单元测试覆盖不足 | 持续补充 | 逐步增加测试用例 |
| SEC-SERVER-P2-008 | 代码注释不足 | 持续优化 | 补充关键方法注释 |
| SEC-SERVER-P2-009 | 魔法数字未定义常量 | 1人天 | 提取为常量 |
| SEC-SERVER-P2-010 | 代码重复 | 持续优化 | 抽取公共方法 |

---

# 📅 修复时间线

## 第1周：紧急修复（P0问题）

| 日期 | 任务 | 负责人 | 完成标准 |
|------|------|--------|----------|
| 周一 | P0-001 添加Spring Security依赖和基础配置 | 待定 | 依赖引入成功 |
| 周二 | P0-001 完成JWT认证过滤器 | 待定 | Token验证通过 |
| 周三 | P0-002 移除FTP硬编码密码 | 待定 | 代码中无明文密码 |
| 周四 | P0-003 移除API密钥硬编码 | 待定 | 代码中无明文密钥 |
| 周五 | P0-004 实现CSRF防护 | 待定 | CSRF验证生效 |
| 周六-周日 | 缓冲区/Code Review | 全员 | - |

## 第2周：核心安全修复

| 日期 | 任务 | 负责人 | 完成标准 |
|------|------|--------|----------|
| 周一 | P0-005 实现XSS防护 | 待定 | XSS过滤生效 |
| 周二 | P1-001 修复Token绕过漏洞 | 待定 | Token强制校验 |
| 周三 | P1-002 增强接口授权 | 待定 | 签名验证通过 |
| 周四 | P1-003 升级密码加密 | 待定 | BCrypt加密生效 |
| 周五 | P0-007 配置Redis缓存 | 待定 | 缓存功能正常 |
| 周六-周日 | 缓冲区/测试 | 全员 | - |

## 第3周：代码质量提升

| 日期 | 任务 | 负责人 | 完成标准 |
|------|------|--------|----------|
| 周一 | P0-006 开始重构超级上帝类 | 待定 | 完成一个类的拆分 |
| 周二 | P1-004 移除IP硬编码 | 待定 | 配置使用环境变量 |
| 周三 | P1-005 实现API限流 | 待定 | 限流功能正常 |
| 周四 | P1-006 敏感信息脱敏 | 待定 | 脱敏注解添加 |
| 周五 | P1-007 清除System.out | 待定 | 无System.out残留 |
| 周六-周日 | 缓冲区/P2问题处理 | 全员 | - |

---

# ✅ 验收标准

## 安全验收
- [ ] 所有敏感配置移至配置中心
- [ ] Spring Security集成完成并生效
- [ ] CSRF Token机制启用
- [ ] XSS过滤中间件启用
- [ ] API限流规则配置完成
- [ ] 密码加密升级为BCrypt

## 代码质量验收
- [ ] 最大Service类行数 < 1000行（持续减少）
- [ ] System.out/err完全清除
- [ ] 核心业务添加缓存注解
- [ ] 事务超时配置 < 30秒
- [ ] 日志覆盖所有关键操作
- [ ] 单元测试覆盖率 > 60%

---

**文档版本**：1.0  
**生成日期**：2024年  
**审核状态**：待审核
