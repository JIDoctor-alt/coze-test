> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC门诊慢特病业务管理系统 - 安全问题原理学习文档

> 📅 文档生成日期：2024年  
> 📁 项目：`picc-mzmtb-server`  
> 🔧 技术栈：Spring Boot + MyBatis + Activiti6 + GaussDB + Redis + Apollo  
> 👥 目标读者：开发人员（需要完整问题原理）  

---

## 📖 文档说明

本文档为P0级别问题提供**完整可用的问题原理学习代码**，包含：
- 修改的文件路径
- 修改前的原始代码
- 修改后的安全代码
- 详细的修改说明

---

# 🔴 P0-001：集成Spring Security框架

## 修改文件清单

| 文件路径 | 操作 | 说明 |
|---------|------|------|
| `pom.xml` | 修改 | 添加Spring Security依赖 |
| `picchealth-server/src/main/java/com/picchealth/config/SecurityConfig.java` | 新建 | 安全配置类 |
| `picchealth-server/src/main/java/com/picchealth/config/security/JwtAuthenticationFilter.java` | 新建 | JWT认证过滤器 |
| `picchealth-server/src/main/java/com/picchealth/config/WebMvcConfig.java` | 新建 | Web配置 |
| `picchealth-server/src/main/java/com/picchealth/exception/GlobalExceptionHandler.java` | 新建 | 全局异常处理 |

---

## 1.1 修改 pom.xml

### 修改前
```xml
<!-- 无Spring Security依赖 -->
<dependencies>
    <!-- 只有业务相关的依赖 -->
</dependencies>
```

### 修改后

```xml
<dependencies>
    <!-- ========== 新增：Spring Security依赖 ========== -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-security</artifactId>
    </dependency>
    
    <!-- JWT相关依赖 -->
    <dependency>
        <groupId>io.jsonwebtoken</groupId>
        <artifactId>jjwt-api</artifactId>
        <version>0.11.5</version>
    </dependency>
    <dependency>
        <groupId>io.jsonwebtoken</groupId>
        <artifactId>jjwt-impl</artifactId>
        <version>0.11.5</version>
        <scope>runtime</scope>
    </dependency>
    <dependency>
        <groupId>io.jsonwebtoken</groupId>
        <artifactId>jjwt-jackson</artifactId>
        <version>0.11.5</version>
        <scope>runtime</scope>
    </dependency>
    
    <!-- 原有依赖保持不变 -->
</dependencies>
```

### 修改说明
> 添加Spring Security和JWT依赖，这是安全框架的基础依赖。

---

## 1.2 新建 SecurityConfig.java

**文件路径**：`picchealth-server/src/main/java/com/picchealth/config/SecurityConfig.java`

```java
package com.picchealth.config;

import com.picchealth.config.security.JwtAuthenticationFilter;
import com.picchealth.config.security.JwtAuthenticationEntryPoint;
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
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.Arrays;

/**
 * Spring Security 安全配置类
 * 
 * 功能说明：
 * 1. 配置URL权限规则
 * 2. 配置JWT认证过滤器
 * 3. 配置密码加密器
 * 4. 配置CORS跨域
 * 
 * @author Security Team
 * @date 2024
 */
@Configuration
@EnableWebSecurity
@EnableGlobalMethodSecurity(prePostEnabled = true) // 启用@PreAuthorize注解
public class SecurityConfig {

    /**
     * JWT认证过滤器
     * 负责从请求中提取Token并验证
     */
    private final JwtAuthenticationFilter jwtAuthenticationFilter;
    
    /**
     * JWT认证失败时的处理
     */
    private final JwtAuthenticationEntryPoint jwtAuthenticationEntryPoint;

    public SecurityConfig(JwtAuthenticationFilter jwtAuthenticationFilter,
                         JwtAuthenticationEntryPoint jwtAuthenticationEntryPoint) {
        this.jwtAuthenticationFilter = jwtAuthenticationFilter;
        this.jwtAuthenticationEntryPoint = jwtAuthenticationEntryPoint;
    }

    /**
     * 配置安全过滤器链
     * 
     * 配置说明：
     * - CSRF：禁用（因为使用JWT无状态认证）
     * - Session：不使用（STATELESS无状态）
     * - 权限规则：按URL路径匹配
     */
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // ===== CORS配置 =====
            .cors().and()
            
            // ===== CSRF配置 =====
            // JWT是无状态认证，不需要CSRF Token
            // 注意：如果是Cookie-based认证，需要启用CSRF
            .csrf().disable()
            
            // ===== 异常处理配置 =====
            .exceptionHandling()
                .authenticationEntryPoint(jwtAuthenticationEntryPoint)
                .and()
            
            // ===== Session管理 =====
            // 不使用session，因为使用JWT无状态认证
            .sessionManagement()
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
                .and()
            
            // ===== 权限规则配置 =====
            .authorizeHttpRequests(auth -> auth
                // ===== 公共路径（无需认证）=====
                // 健康检查
                .antMatchers("/health", "/actuator/**").permitAll()
                // 公共API（登录、注册等）
                .antMatchers("/api/public/**").permitAll()
                // 静态资源
                .antMatchers("/static/**", "/public/**", "/*.html", "/*.js", "/*.css").permitAll()
                // Swagger文档
                .antMatchers("/swagger-ui/**", "/v3/api-docs/**").permitAll()
                
                // ===== 管理后台（需要ADMIN角色）=====
                .antMatchers("/api/admin/**").hasRole("ADMIN")
                
                // ===== 其他所有请求都需要认证 =====
                .anyRequest().authenticated()
            )
            
            // ===== 添加JWT过滤器 =====
            // 在UsernamePasswordAuthenticationFilter之前执行
            .addFilterBefore(jwtAuthenticationFilter, 
                UsernamePasswordAuthenticationFilter.class);
        
        return http.build();
    }

    /**
     * 密码加密器配置
     * 
     * 使用BCrypt算法：
     * - 自动生成随机盐
     * - 迭代哈希（默认10轮，可配置）
     * - 防彩虹表攻击
     */
    @Bean
    public PasswordEncoder passwordEncoder() {
        // 强度因子12，安全性和性能的平衡
        return new BCryptPasswordEncoder(12);
    }

    /**
     * CORS跨域配置
     */
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOriginPatterns(Arrays.asList("*"));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setAllowCredentials(true);
        configuration.setMaxAge(3600L);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
```

### 修改说明
> 这是整个安全框架的核心配置类，定义了：
> 1. 哪些URL需要认证，哪些不需要
> 2. 如何验证用户身份（JWT过滤器）
> 3. 如何加密密码（BCrypt）
> 4. 如何处理跨域请求

---

## 1.3 新建 JwtAuthenticationFilter.java

**文件路径**：`picchealth-server/src/main/java/com/picchealth/config/security/JwtAuthenticationFilter.java`

```java
package com.picchealth.config.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.picchealth.utils.User;
import com.picchealth.utils.UserUtils;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.*;
import java.util.stream.Collectors;

/**
 * JWT认证过滤器
 * 
 * 功能说明：
 * 1. 从请求Header中提取Token
 * 2. 验证Token有效性
 * 3. 从Token中解析用户信息
 * 4. 设置Spring Security上下文
 * 
 * 执行时机：每个请求都会执行，在Controller之前
 */
@Component
@Slf4j
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private static final String TOKEN_HEADER = "Authorization";
    private static final String TOKEN_PREFIX = "Bearer ";
    private static final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * 核心过滤方法
     */
    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        try {
            // 1. 从请求中提取Token
            String jwt = extractJwtFromRequest(request);
            
            if (StringUtils.hasText(jwt)) {
                // 2. 验证Token并获取用户信息
                Claims claims = JwtUtil.parseToken(jwt);
                String userId = claims.getSubject();
                String userName = claims.get("userName", String.class);
                List<String> roles = claims.get("roles", List.class);
                
                // 3. 构建用户对象
                User user = new User();
                user.setUserId(userId);
                user.setUserName(userName);
                
                // 4. 转换为Spring Security权限对象
                List<SimpleGrantedAuthority> authorities = roles != null 
                    ? roles.stream()
                        .map(role -> new SimpleGrantedAuthority("ROLE_" + role))
                        .collect(Collectors.toList())
                    : Collections.emptyList();
                
                // 5. 创建认证对象
                UsernamePasswordAuthenticationToken authentication = 
                    new UsernamePasswordAuthenticationToken(user, null, authorities);
                
                // 6. 设置到Security上下文
                SecurityContextHolder.getContext().setAuthentication(authentication);
                
                // 7. 同时设置到ThreadLocal（兼容原有代码）
                UserUtils.setUser(user);
                
                log.debug("用户认证成功: userId={}, roles={}", userId, roles);
            }
        } catch (Exception e) {
            log.warn("JWT认证失败: {}", e.getMessage());
            // 认证失败不清除上下文，让后续判断处理
        }
        
        // 8. 继续执行过滤器链
        filterChain.doFilter(request, response);
    }

    /**
     * 从请求中提取JWT Token
     * 
     * 支持两种方式：
     * 1. Header: Authorization: Bearer <token>
     * 2. Query参数: ?token=<token>
     */
    private String extractJwtFromRequest(HttpServletRequest request) {
        // 优先从Header获取
        String bearerToken = request.getHeader(TOKEN_HEADER);
        if (StringUtils.hasText(bearerToken) && bearerToken.startsWith(TOKEN_PREFIX)) {
            return bearerToken.substring(TOKEN_PREFIX.length());
        }
        
        // 其次从Query参数获取
        String token = request.getParameter("token");
        if (StringUtils.hasText(token)) {
            return token;
        }
        
        return null;
    }

    /**
     * 白名单路径，这些路径不需要认证
     */
    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        String path = request.getServletPath();
        return path.startsWith("/health") 
            || path.startsWith("/api/public/")
            || path.startsWith("/swagger-ui")
            || path.startsWith("/v3/api-docs");
    }
}
```

### 修改说明
> 这是JWT认证的核心过滤器，负责：
> 1. 提取请求中的Token
> 2. 解析Token获取用户信息
> 3. 设置Spring Security的认证上下文
> 4. 同时兼容原有UserUtils的使用方式

---

## 1.4 新建 JwtUtil.java

**文件路径**：`picchealth-server/src/main/java/com/picchealth/utils/security/JwtUtil.java`

```java
package com.picchealth.utils.security;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import lombok.extern.slf4j.Slf4j;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * JWT工具类
 * 
 * 功能说明：
 * 1. 生成JWT Token
 * 2. 解析验证Token
 * 3. 获取Token中的用户信息
 */
@Slf4j
public class JwtUtil {

    // ===== 配置常量 =====
    // 生产环境应从配置中心读取，不要硬编码！
    private static final String SECRET_KEY = "your-256-bit-secret-key-here-change-in-production-min-32-chars";
    private static final long EXPIRATION_TIME = 2 * 60 * 60 * 1000; // 2小时
    private static final String ALGORITHM = "HS256";

    /**
     * 生成JWT Token
     * 
     * @param userId 用户ID
     * @param userName 用户名
     * @param roles 用户角色列表
     * @return JWT Token字符串
     */
    public static String generateToken(String userId, String userName, List<String> roles) {
        // 1. 创建签名Key
        SecretKey key = Keys.hmacShaKeyFor(SECRET_KEY.getBytes(StandardCharsets.UTF_8));
        
        // 2. 创建Claims（Payload）
        Map<String, Object> claims = new HashMap<>();
        claims.put("userName", userName);
        claims.put("roles", roles);
        
        // 3. 创建Token
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + EXPIRATION_TIME);
        
        String token = Jwts.builder()
            .setSubject(userId)  // 用户ID作为主题
            .setClaims(claims)   // 自定义claims
            .setIssuedAt(now)    // 签发时间
            .setExpiration(expiryDate)  // 过期时间
            .signWith(key, SignatureAlgorithm.valueOf(ALGORITHM))  // 签名
            .compact();
        
        log.debug("生成Token: userId={}, expiry={}", userId, expiryDate);
        return token;
    }

    /**
     * 解析Token，获取Claims
     * 
     * @param token JWT Token
     * @return Claims对象
     */
    public static Claims parseToken(String token) {
        try {
            SecretKey key = Keys.hmacShaKeyFor(SECRET_KEY.getBytes(StandardCharsets.UTF_8));
            
            Claims claims = Jwts.parserBuilder()
                .setSigningKey(key)
                .build()
                .parseClaimsJws(token)
                .getBody();
            
            return claims;
        } catch (ExpiredJwtException e) {
            log.warn("Token已过期: {}", e.getMessage());
            throw e;
        } catch (JwtException e) {
            log.warn("Token解析失败: {}", e.getMessage());
            throw e;
        }
    }

    /**
     * 验证Token是否有效
     * 
     * @param token JWT Token
     * @return true=有效, false=无效
     */
    public static boolean validateToken(String token) {
        try {
            parseToken(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * 获取Token中的用户ID
     */
    public static String getUserId(String token) {
        return parseToken(token).getSubject();
    }

    /**
     * 获取Token过期时间
     */
    public static Date getExpiration(String token) {
        return parseToken(token).getExpiration();
    }
}
```

### 修改说明
> 这是JWT工具类，负责Token的生成和解析。
> **重要**：SECRET_KEY在生产环境必须从配置中心或密钥管理系统读取！

---

## 1.5 新建 JwtAuthenticationEntryPoint.java

**文件路径**：`picchealth-server/src/main/java/com/picchealth/config/security/JwtAuthenticationEntryPoint.java`

```java
package com.picchealth.config.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 * JWT认证失败处理器
 * 
 * 当用户未认证或认证失败时，返回统一的JSON错误响应
 */
@Component
@Slf4j
public class JwtAuthenticationEntryPoint implements AuthenticationEntryPoint {

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public void commence(HttpServletRequest request,
                        HttpServletResponse response,
                        AuthenticationException authException) throws IOException, ServletException {
        
        log.warn("认证失败: path={}, error={}", 
            request.getRequestURI(), authException.getMessage());
        
        // 设置响应类型为JSON
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.setCharacterEncoding("UTF-8");
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        
        // 返回统一错误格式
        Map<String, Object> result = new HashMap<>();
        result.put("code", 401);
        result.put("message", "认证失败，请登录后重试");
        result.put("path", request.getRequestURI());
        
        objectMapper.writeValue(response.getOutputStream(), result);
    }
}
```

### 修改说明
> 当用户未登录或Token无效时，返回友好的JSON错误信息，而不是Spring Security默认的错误页面。

---

# 🔴 P0-002：移除FTP硬编码密码

## 修改文件清单

| 文件路径 | 操作 | 说明 |
|---------|------|------|
| `picchealth-server/src/main/java/com/picchealth/utils/FTPFileUtil_xcx.java` | 修改 | 移除默认密码 |
| `picchealth-server/src/main/java/com/picchealth/utils/CommonUtils.java` | 修改 | 移除默认密码 |
| `picchealth-server/src/main/java/com/picchealth/utils/MbXcxValueUtil.java` | 修改 | 移除默认密码 |
| `application-prod.yml` | 新建 | 生产环境配置 |

---

## 2.1 修改 FTPFileUtil_xcx.java

### 修改前
```java
@Value("${xcxftp.password:hmlink@123}")  // ❌ 有默认密码
public void setPass(String passWord){
    pass = passWord;
}
```

### 修改后

```java
package com.picchealth.utils;

import lombok.extern.slf4j.Slf4j;
import org.apache.commons.codec.binary.Base64;
import org.apache.commons.lang.StringUtils;
import org.apache.commons.net.ftp.FTPClient;
import org.apache.commons.net.ftp.FTPReply;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;

/**
 * FTP文件上传工具类
 * 
 * 功能说明：
 * 1. 连接FTP服务器
 * 2. 上传文件
 * 3. 下载文件
 * 4. 删除文件
 */
@Slf4j
@Component
public class FTPFileUtil_xcx {

    // ===== FTP配置（从配置中心读取，无默认值）=====
    
    private static String userName;
    private static String pass;
    private static String port;
    private static String ip;

    public static FTPClient ftpClient = null;

    // 字符编码配置
    static String LOCAL_CHARSET = "GBK";
    static String SERVER_CHARSET = "ISO-8859-1";

    /**
     * 设置FTP用户名
     * 
     * ⚠️ 注意：生产环境必须配置，无默认值
     */
    @Value("${xcxftp.username}")
    public void setUserName(String Name) {
        userName = Name;
    }

    /**
     * 设置FTP密码
     * 
     * ⚠️ 注意：生产环境必须配置，无默认值
     * 配置缺失时应用启动失败，防止密码泄露
     */
    @Value("${xcxftp.password}")
    public void setPass(String passWord) {
        pass = passWord;
    }

    /**
     * 设置FTP端口
     * 
     * 默认值：21
     */
    @Value("${xcxftp.port:21}")
    public void setPort(String ftpPort) {
        port = ftpPort;
    }

    /**
     * 设置FTP服务器地址
     * 
     * ⚠️ 注意：生产环境必须配置，无默认值
     */
    @Value("${xcxftp.ip}")
    public void setIp(String ftpIp) {
        ip = ftpIp;
    }

    /**
     * 初始化FTP连接
     */
    public void initFtpClient() {
        ftpClient = new FTPClient();
        try {
            log.info("连接FTP服务器: {}:{}", ip, port);
            
            // 连接FTP服务器
            ftpClient.connect(ip, Integer.parseInt(port));
            
            // 登录
            ftpClient.login(userName, pass);
            
            // 检查登录状态
            int replyCode = ftpClient.getReplyCode();
            if (!FTPReply.isPositiveCompletion(replyCode)) {
                log.error("FTP连接失败: {}", replyCode);
                throw new RuntimeException("FTP连接失败");
            }
            
            log.info("FTP连接成功");
            
            // 设置UTF-8编码
            if (FTPReply.isPositiveCompletion(ftpClient.sendCommand("OPTS UTF8", "ON"))) {
                LOCAL_CHARSET = "UTF-8";
            }
            ftpClient.setControlEncoding(LOCAL_CHARSET);
            
        } catch (IOException e) {
            log.error("FTP连接异常", e);
            throw new RuntimeException("FTP连接异常", e);
        }
    }

    // ... 其他方法保持不变
}
```

### 修改说明
> **关键变更**：
> 1. `@Value` 注解不再有默认值
> 2. 密码、用户名、IP地址缺失时，应用启动失败
> 3. 防止敏感信息泄露到代码仓库

---

## 2.2 修改 CommonUtils.java

### 修改前
```java
@Value("${ftp.ip:192.168.8.120}")           // ❌ 有默认IP
@Value("${ftp.password:hellolevy}")         // ❌ 有默认密码
private static String passWord;
```

### 修改后

```java
package com.picchealth.utils;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * 公共工具类
 * 
 * ⚠️ 已移除所有硬编码配置
 * 所有配置必须从配置中心读取
 */
@Slf4j
@Component
public class CommonUtils {

    // ===== 配置项（无默认值，必须配置）=====
    
    private static String ip;
    private static int port;
    private static String userName;
    private static String passWord;

    /**
     * FTP服务器地址
     */
    @Value("${ftp.ip}")
    public void setIp(String ftpIp) {
        ip = ftpIp;
    }

    /**
     * FTP服务器端口
     */
    @Value("${ftp.port:21}")
    public void setPort(int ftpPort) {
        port = ftpPort;
    }

    /**
     * FTP用户名
     */
    @Value("${ftp.username}")
    public void setUserName(String name) {
        userName = name;
    }

    /**
     * FTP密码
     * 
     * ⚠️ 无默认值，配置缺失则启动失败
     */
    @Value("${ftp.password}")
    public void setPassWord(String password) {
        passWord = password;
    }

    // ... 其他方法保持不变
}
```

### 修改说明
> 移除所有硬编码的IP地址和密码。

---

## 2.3 创建生产环境配置模板

**文件路径**：`config/application-prod-template.yml`

```yaml
# PICC门诊慢特病管理系统 - 生产环境配置模板
# 
# 使用说明：
# 1. 复制此文件为 application-prod.yml
# 2. 填写实际的值（不要提交到git！）
# 3. 或使用环境变量替换
# 
# ⚠️ 警告：此文件包含敏感信息，严禁提交到代码仓库！

spring:
  profiles:
    active: prod

# ===== FTP配置 =====
# 生产环境FTP配置（从环境变量读取）
ftp:
  ip: ${FTP_SERVER_IP}           # 例：10.0.0.100
  port: ${FTP_PORT:21}           # FTP端口，默认21
  username: ${FTP_USERNAME}       # FTP用户名
  password: ${FTP_PASSWORD}      # FTP密码（从密钥管理系统获取）

xcxftp:
  ip: ${XCX_FTP_SERVER_IP}       # 小程序FTP地址
  port: ${XCX_FTP_PORT:21}
  username: ${XCX_FTP_USERNAME}
  password: ${XCX_FTP_PASSWORD}

# ===== JWT配置 =====
jwt:
  secret: ${JWT_SECRET_KEY}      # JWT签名密钥（至少32字符）
  expiration: ${JWT_EXPIRATION:7200000}  # Token有效期，毫秒

# ===== 数据库配置 =====
datasource:
  url: ${DB_URL}
  username: ${DB_USERNAME}
  password: ${DB_PASSWORD}
  driver-class-name: com.mysql.cj.jdbc.Driver

# ===== Redis配置 =====
redis:
  host: ${REDIS_HOST}
  port: ${REDIS_PORT:6379}
  password: ${REDIS_PASSWORD:}
  database: ${REDIS_DB:0}
```

### 修改说明
> 生产环境配置使用环境变量，不在代码中明文存储敏感信息。

---

# 🔴 P0-003：移除API密钥硬编码

## 修改文件清单

| 文件路径 | 操作 | 说明 |
|---------|------|------|
| `picchealth-server/src/main/java/com/picchealth/utils/ImageQualityAssessmentUtil.java` | 修改 | 移除硬编码密钥 |
| `application.yml` | 修改 | 添加密钥配置 |

---

## 3.1 修改 ImageQualityAssessmentUtil.java

### 修改前（危险代码）
```java
// 图片分类 - 硬编码密钥！
String appId = "7da2f83e";
String secretId = "7839c25a";  // ❌ 硬编码
String secretKey = "7c16d7d5"; // ❌ 硬编码
String abilityId = "35b0c3ec";
```

### 修改后

```java
package com.picchealth.utils;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

/**
 * 图片质量评估工具类
 * 
 * ⚠️ 已移除所有硬编码密钥
 * 密钥配置从配置中心读取
 */
@Component
public class ImageQualityAssessmentUtil {

    // ===== API密钥配置（从配置中心读取，无默认值）=====
    
    private static String appId;
    private static String secretId;
    private static String secretKey;
    private static String abilityId;
    private static String sceneId;

    /**
     * 设置App ID
     */
    @Value("${image.qa.appId}")
    public void setAppId(String id) {
        appId = id;
    }

    /**
     * 设置Secret ID
     */
    @Value("${image.qa.secretId}")
    public void setSecretId(String id) {
        secretId = id;
    }

    /**
     * 设置Secret Key
     */
    @Value("${image.qa.secretKey}")
    public void setSecretKey(String key) {
        secretKey = key;
    }

    /**
     * 设置Ability ID
     */
    @Value("${image.qa.abilityId}")
    public void setAbilityId(String id) {
        abilityId = id;
    }

    /**
     * 设置场景ID
     */
    @Value("${image.qa.sceneId:default}")
    public void setSceneId(String scene) {
        sceneId = scene;
    }

    /**
     * 生成授权头
     * 
     * @param method HTTP方法
     * @param nonce 随机数
     * @param timestamp 时间戳
     * @return 授权头字符串
     */
    public static String getAuthorizationHeader(String method, String nonce, String timestamp) throws Exception {
        // 使用类的静态方法时需要确保已初始化
        // 建议改用实例方法调用
        
        String normalizedHeaders = 
            "ability=" + abilityId + "\n" +
            "action=test\n" +
            "appId=" + appId + "\n" +
            "nonce=" + nonce + "\n" +
            "sceneId=" + sceneId + "\n" +
            "timestamp=" + timestamp + "\n";
        
        String normalizedResource = "/";
        String stringToSign = method + "\n" + normalizedHeaders + normalizedResource;
        
        return "HmacSHA256:" + secretId + ":" + signature(stringToSign, secretKey);
    }

    /**
     * HMAC签名
     */
    private static String signature(String stringToSign, String key) throws Exception {
        byte[] secretBytes = key.getBytes(StandardCharsets.UTF_8);
        SecretKeySpec secretKeyObj = new SecretKeySpec(secretBytes, "HmacSHA256");
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(secretKeyObj);
        byte[] stringToSignBytes = stringToSign.getBytes(StandardCharsets.UTF_8);
        byte[] signatureBytes = mac.doFinal(stringToSignBytes);
        return Base64.getEncoder().encodeToString(signatureBytes);
    }

    /**
     * 实例方法版本的授权头生成（推荐使用）
     */
    public String generateAuthorization(String method, String nonce, String timestamp) throws Exception {
        String normalizedHeaders = 
            "ability=" + abilityId + "\n" +
            "action=test\n" +
            "appId=" + appId + "\n" +
            "nonce=" + nonce + "\n" +
            "sceneId=" + sceneId + "\n" +
            "timestamp=" + timestamp + "\n";
        
        String normalizedResource = "/";
        String stringToSign = method + "\n" + normalizedHeaders + normalizedResource;
        
        return "HmacSHA256:" + secretId + ":" + signature(stringToSign, secretKey);
    }
}
```

### 修改说明
> **关键变更**：
> 1. 移除所有硬编码的API密钥
> 2. 使用@Value从配置中心读取
> 3. 建议更换已泄露的API密钥

---

# 🔴 P0-004：实现CSRF防护

## 修改文件清单

| 文件路径 | 操作 | 说明 |
|---------|------|------|
| `picchealth-server/src/main/java/com/picchealth/utils/security/CsrfTokenUtil.java` | 新建 | CSRF Token工具类 |
| `picchealth-server/src/main/java/com/picchealth/config/security/CsrfInterceptor.java` | 新建 | CSRF验证拦截器 |
| `picchealth-server/src/main/java/com/picchealth/config/WebMvcConfig.java` | 新建 | Web配置 |

---

## 4.1 新建 CsrfTokenUtil.java

**文件路径**：`picchealth-server/src/main/java/com/picchealth/utils/security/CsrfTokenUtil.java`

```java
package com.picchealth.utils.security;

import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.security.SecureRandom;
import java.util.Base64;

/**
 * CSRF Token工具类
 * 
 * 功能说明：
 * 1. 生成安全的随机Token
 * 2. 将Token写入Cookie
 * 3. 验证请求中的Token
 * 
 * CSRF攻击原理：
 * - 用户登录后访问恶意网站
 * - 恶意网站自动发起请求到你的系统
 * - 浏览器会自动带上同源Cookie
 * - 系统无法区分是用户操作还是恶意请求
 * 
 * 防护原理：
 * - 登录时生成随机Token
 * - Token存在Cookie中，同时需要前端获取
 * - 前端发送请求时，必须从Cookie读取Token放入Header
 * - 后端验证Header和Cookie中的Token是否一致
 */
@Component
@Slf4j
public class CsrfTokenUtil {

    // ===== 常量定义 =====
    
    /** Cookie中Token的名称 */
    private static final String CSRF_TOKEN_NAME = "XSRF-TOKEN";
    
    /** 请求Header中Token的名称 */
    private static final String CSRF_HEADER_NAME = "X-XSRF-TOKEN";
    
    /** 安全的随机数生成器 */
    private static final SecureRandom SECURE_RANDOM = new SecureRandom();
    
    /** Token长度（字节） */
    private static final int TOKEN_LENGTH = 32;
    
    /** Token有效期：2小时 */
    private static final long TOKEN_VALIDITY = 2 * 60 * 60 * 1000;

    /**
     * 生成CSRF Token并写入Cookie
     * 
     * 调用时机：用户登录成功后
     * 
     * @param request HTTP请求（用于判断是否HTTPS）
     * @param response HTTP响应（用于写入Cookie）
     * @return 生成的Token值（前端可能需要用到）
     */
    public String generateToken(HttpServletRequest request, HttpServletResponse response) {
        // 1. 生成安全的随机Token
        String token = generateSecureToken();
        
        // 2. 创建Cookie
        Cookie cookie = new Cookie(CSRF_TOKEN_NAME, token);
        cookie.setHttpOnly(false); // 前端需要通过JS读取，所以不能设为true
        cookie.setPath("/");        // 全路径有效
        cookie.setMaxAge((int) (TOKEN_VALIDITY / 1000)); // 2小时
        cookie.setSecure(request.isSecure()); // HTTPS时设置为true
        
        // 3. 防止XSS读取Cookie（HttpOnly配合CSP）
        // 注意：如果前端框架支持，可以通过response header传递Token
        
        // 4. 添加到响应
        response.addCookie(cookie);
        
        // 5. 同时通过Header返回（更安全的方式）
        response.setHeader("X-XSRF-TOKEN", token);
        
        log.debug("生成CSRF Token: {}", maskToken(token));
        return token;
    }

    /**
     * 验证请求中的Token
     * 
     * 验证规则：
     * 1. Header中必须有Token
     * 2. Cookie中必须有Token
     * 3. 两者必须完全一致
     * 
     * @param request HTTP请求
     * @return true=验证通过, false=验证失败
     */
    public boolean validateToken(HttpServletRequest request) {
        // 1. 从请求Header获取Token
        String headerToken = request.getHeader(CSRF_HEADER_NAME);
        
        // 2. 从Cookie获取Token
        String cookieToken = extractCookieValue(request, CSRF_TOKEN_NAME);
        
        // 3. 验证两者都存在
        if (headerToken == null || headerToken.isEmpty()) {
            log.warn("CSRF验证失败：Header中缺少Token");
            return false;
        }
        
        if (cookieToken == null || cookieToken.isEmpty()) {
            log.warn("CSRF验证失败：Cookie中缺少Token");
            return false;
        }
        
        // 4. 验证两者一致
        if (!headerToken.equals(cookieToken)) {
            log.warn("CSRF验证失败：Token不匹配");
            return false;
        }
        
        log.debug("CSRF Token验证通过");
        return true;
    }

    /**
     * 验证Token并抛出异常（验证失败时）
     */
    public void validateTokenOrThrow(HttpServletRequest request) {
        if (!validateToken(request)) {
            throw new SecurityException("CSRF验证失败");
        }
    }

    /**
     * 生成安全的随机Token
     * 
     * 使用SecureRandom生成密码学安全的随机数
     */
    private String generateSecureToken() {
        byte[] bytes = new byte[TOKEN_LENGTH];
        SECURE_RANDOM.nextBytes(bytes);
        return Base64.getUrlEncoder()
            .withoutPadding() // 不添加=padding
            .encodeToString(bytes);
    }

    /**
     * 从Cookie中提取指定名称的值
     */
    private String extractCookieValue(HttpServletRequest request, String name) {
        Cookie[] cookies = request.getCookies();
        if (cookies != null) {
            for (Cookie cookie : cookies) {
                if (name.equals(cookie.getName())) {
                    return cookie.getValue();
                }
            }
        }
        return null;
    }

    /**
     * 遮蔽Token用于日志（只显示首尾字符）
     */
    private String maskToken(String token) {
        if (token == null || token.length() < 8) {
            return "***";
        }
        return token.substring(0, 4) + "..." + token.substring(token.length() - 4);
    }
}
```

### 修改说明
> CSRF Token的工作流程：
> 1. 用户登录时，后端生成随机Token
> 2. Token同时写入Cookie和Header返回
> 3. 前端发起修改请求时，从Cookie读取Token放入Header
> 4. 后端验证Header和Cookie中的Token是否一致
> 5. 攻击者无法获取Cookie中的Token（受同源策略限制），所以验证会失败

---

## 4.2 新建 CsrfInterceptor.java

**文件路径**：`picchealth-server/src/main/java/com/picchealth/config/security/CsrfInterceptor.java`

```java
package com.picchealth.config.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import java.util.HashMap;
import java.util.Map;

/**
 * CSRF拦截器
 * 
 * 功能说明：
 * 1. 拦截所有POST/PUT/DELETE请求
 * 2. 验证CSRF Token
 * 3. 验证失败返回403错误
 * 
 * 配置说明：
 * - GET请求不验证（GET请求不应有副作用）
 * - OPTIONS请求不验证（预检请求）
 * - 公共接口不验证（通过配置路径排除）
 */
@Component
@Slf4j
public class CsrfInterceptor implements HandlerInterceptor {

    private final CsrfTokenUtil csrfTokenUtil;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public CsrfInterceptor(CsrfTokenUtil csrfTokenUtil) {
        this.csrfTokenUtil = csrfTokenUtil;
    }

    /**
     * 请求前置处理
     * 
     * 在Controller方法执行前验证CSRF Token
     */
    @Override
    public boolean preHandle(HttpServletRequest request, 
                            HttpServletResponse response, 
                            Object handler) throws Exception {
        
        // 1. 只验证修改性请求
        String method = request.getMethod();
        if ("GET".equalsIgnoreCase(method) || "OPTIONS".equalsIgnoreCase(method)) {
            // GET和OPTIONS请求不需要验证
            return true;
        }
        
        // 2. 验证Token
        if (!csrfTokenUtil.validateToken(request)) {
            log.warn("CSRF验证失败: IP={}, URI={}, Method={}", 
                request.getRemoteAddr(), 
                request.getRequestURI(), 
                method);
            
            // 3. 返回403错误
            response.setStatus(HttpServletResponse.SC_FORBIDDEN);
            response.setContentType("application/json");
            response.setCharacterEncoding("UTF-8");
            
            Map<String, Object> result = new HashMap<>();
            result.put("code", 403);
            result.put("message", "CSRF验证失败，请刷新页面后重试");
            result.put("path", request.getRequestURI());
            
            response.getWriter().write(objectMapper.writeValueAsString(result));
            return false;
        }
        
        return true;
    }
}
```

### 修改说明
> 拦截器会对所有POST/PUT/DELETE请求进行CSRF验证。

---

## 4.3 新建 WebMvcConfig.java

**文件路径**：`picchealth-server/src/main/java/com/picchealth/config/WebMvcConfig.java`

```java
package com.picchealth.config;

import com.picchealth.config.security.CsrfInterceptor;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * Web MVC配置
 * 
 * 配置说明：
 * 1. 注册CSRF拦截器
 * 2. 配置拦截路径
 * 3. 配置排除路径
 */
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

    private final CsrfInterceptor csrfInterceptor;

    public WebMvcConfig(CsrfInterceptor csrfInterceptor) {
        this.csrfInterceptor = csrfInterceptor;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(csrfInterceptor)
            // 拦截/api/**下的所有请求
            .addPathPatterns("/api/**")
            
            // 排除公共接口（这些接口不需要CSRF验证）
            .excludePathPatterns(
                "/api/public/**",     // 公共接口
                "/api/health",        // 健康检查
                "/api/auth/login"     // 登录接口
            );
    }
}
```

### 修改说明
> 配置CSRF拦截器的作用范围，排除不需要验证的公共接口。

---

# 🔴 P0-005：实现XSS防护

## 修改文件清单

| 文件路径 | 操作 | 说明 |
|---------|------|------|
| `picchealth-server/src/main/java/com/picchealth/utils/security/XssUtil.java` | 新建 | XSS过滤工具类 |
| `picchealth-server/src/main/java/com/picchealth/config/filter/XssFilter.java` | 新建 | 全局XSS过滤器 |
| `picchealth-server/src/main/java/com/picchealth/config/filter/XssRequestWrapper.java` | 新建 | 请求包装器 |
| `picchealth-server/src/main/java/com/picchealth/config/FilterConfig.java` | 新建 | 过滤器配置 |

---

## 5.1 新建 XssUtil.java

**文件路径**：`picchealth-server/src/main/java/com/picchealth/utils/security/XssUtil.java`

```java
package com.picchealth.utils.security;

import cn.hutool.core.util.StrUtil;
import cn.hutool.http.html.XssUtil;
import org.springframework.stereotype.Component;

import java.util.regex.Pattern;

/**
 * XSS防护工具类
 * 
 * 功能说明：
 * 1. 过滤HTML标签和脚本
 * 2. 检测XSS攻击
 * 3. 转义危险字符
 * 
 * XSS攻击类型：
 * 1. 存储型XSS：恶意代码存入数据库
 * 2. 反射型XSS：恶意代码通过URL参数反射
 * 3. DOM型XSS：通过JavaScript操作DOM注入
 */
@Component
public class XssUtil {

    // ===== 危险标签和属性 =====
    
    /** 危险标签正则 */
    private static final Pattern SCRIPT_PATTERN = 
        Pattern.compile("<script[^>]*?>[\\s\\S]*?</script>", Pattern.CASE_INSENSITIVE);
    
    private static final Pattern IFRAME_PATTERN = 
        Pattern.compile("<iframe[^>]*?>[\\s\\S]*?</iframe>", Pattern.CASE_INSENSITIVE);
    
    private static final Pattern OBJECT_PATTERN = 
        Pattern.compile("<object[^>]*?>[\\s\\S]*?</object>", Pattern.CASE_INSENSITIVE);
    
    private static final Pattern EMBED_PATTERN = 
        Pattern.compile("<embed[^>]*?>", Pattern.CASE_INSENSITIVE);
    
    private static final Pattern FORM_PATTERN = 
        Pattern.compile("<form[^>]*?>[\\s\\S]*?</form>", Pattern.CASE_INSENSITIVE);
    
    /** 危险属性正则 */
    private static final Pattern JAVASCRIPT_PROTOCOL = 
        Pattern.compile("javascript\\s*:", Pattern.CASE_INSENSITIVE);
    
    private static final Pattern EVENT_HANDLER = 
        Pattern.compile("on\\w+\\s*=", Pattern.CASE_INSENSITIVE);

    /**
     * 过滤HTML危险标签和脚本
     * 
     * 使用Hutool的XSS过滤，会：
     * - 移除 <script>、<iframe> 等危险标签
     * - 转义 < > 等HTML特殊字符
     * 
     * @param text 原始文本
     * @return 过滤后的安全文本
     */
    public static String filter(String text) {
        if (StrUtil.isEmpty(text)) {
            return text;
        }
        
        // 使用Hutool的XSS过滤
        String filtered = XssUtil.filterHtml(text);
        
        // 额外的安全处理
        filtered = filtered
            .replaceAll("<[^>]*>", "") // 移除所有HTML标签
            .replaceAll("&lt;", "<")   // 转义回来
            .replaceAll("&gt;", ">")
            .replaceAll("&amp;", "&")
            .replaceAll("&quot;", "\"");
        
        return filtered;
    }

    /**
     * 过滤但保留部分HTML（用于文章内容等富文本）
     * 
     * @param text 原始HTML文本
     * @return 清理后的HTML
     */
    public static String filterHtmlSafe(String text) {
        if (StrUtil.isEmpty(text)) {
            return text;
        }
        
        // 使用Hutool的XSS过滤
        return XssUtil.filterHtml(text);
    }

    /**
     * 过滤JSON中的XSS
     * 
     * @param json 原始JSON字符串
     * @return 过滤后的JSON
     */
    public static String filterForJson(String json) {
        if (StrUtil.isEmpty(json)) {
            return json;
        }
        
        String filtered = json;
        
        // 移除script标签
        filtered = SCRIPT_PATTERN.matcher(filtered).replaceAll("");
        
        // 移除iframe标签
        filtered = IFRAME_PATTERN.matcher(filtered).replaceAll("");
        
        // 移除object标签
        filtered = OBJECT_PATTERN.matcher(filtered).replaceAll("");
        
        // 移除embed标签
        filtered = EMBED_PATTERN.matcher(filtered).replaceAll("");
        
        // 移除javascript:协议
        filtered = JAVASCRIPT_PROTOCOL.matcher(filtered).replaceAll("");
        
        // 移除事件处理器
        filtered = EVENT_HANDLER.matcher(filtered).replaceAll("");
        
        return filtered;
    }

    /**
     * 检查是否包含XSS风险
     * 
     * @param text 待检查的文本
     * @return true=包含XSS风险, false=安全
     */
    public static boolean containsXss(String text) {
        if (StrUtil.isEmpty(text)) {
            return false;
        }
        
        String lowerText = text.toLowerCase();
        
        return lowerText.contains("<script") 
            || lowerText.contains("javascript:")
            || lowerText.contains("onerror")
            || lowerText.contains("onload")
            || lowerText.contains("<iframe")
            || EVENT_HANDLER.matcher(text).find();
    }

    /**
     * HTML转义（用于在HTML页面中显示用户输入）
     * 
     * 示例：
     * - 用户输入: <script>alert('XSS')</script>
     * - 转义后: &lt;script&gt;alert(&#39;XSS&#39;)&lt;/script&gt;
     * 
     * @param text 原始文本
     * @return 转义后的文本
     */
    public static String escapeHtml(String text) {
        if (StrUtil.isEmpty(text)) {
            return text;
        }
        
        return text
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll("\"", "&quot;")
            .replaceAll("'", "&#39;");
    }

    /**
     * HTML反转义
     * 
     * @param text 转义后的文本
     * @return 原始文本
     */
    public static String unescapeHtml(String text) {
        if (StrUtil.isEmpty(text)) {
            return text;
        }
        
        return text
            .replaceAll("&amp;", "&")
            .replaceAll("&lt;", "<")
            .replaceAll("&gt;", ">")
            .replaceAll("&quot;", "\"")
            .replaceAll("&#39;", "'");
    }
}
```

### 修改说明
> XSS防护的核心是过滤和转义：
> 1. 过滤：移除危险的HTML标签
> 2. 转义：将特殊字符转为HTML实体

---

## 5.2 新建 XssFilter.java

**文件路径**：`picchealth-server/src/main/java/com/picchealth/config/filter/XssFilter.java`

```java
package com.picchealth.config.filter;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.picchealth.utils.security.XssUtil;
import jakarta.servlet.*;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 * 全局XSS过滤器
 * 
 * 功能说明：
 * 1. 过滤所有请求参数中的XSS攻击
 * 2. 阻止明显的XSS攻击请求
 * 3. 对参数值进行安全处理
 * 
 * 注意：
 * - 此过滤器会处理所有请求参数
 * - 对于需要保留HTML的富文本，需要单独处理
 */
@Component
@Slf4j
public class XssFilter implements Filter {

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public void init(FilterConfig filterConfig) throws ServletException {
        log.info("XSS过滤器初始化");
    }

    @Override
    public void doFilter(ServletRequest servletRequest, 
                         ServletResponse servletResponse,
                         FilterChain chain) throws IOException, ServletException {
        
        HttpServletRequest request = (HttpServletRequest) servletRequest;
        HttpServletResponse response = (HttpServletResponse) servletResponse;
        
        // 1. 检查是否包含XSS攻击
        if (containsXssAttack(request)) {
            log.warn("检测到XSS攻击: IP={}, URI={}, Params={}", 
                request.getRemoteAddr(), 
                request.getRequestURI(),
                getParameterNames(request));
            
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            response.setContentType("application/json");
            response.setCharacterEncoding("UTF-8");
            
            Map<String, Object> result = new HashMap<>();
            result.put("code", 400);
            result.put("message", "请求参数包含非法字符，已被拦截");
            
            response.getWriter().write(objectMapper.writeValueAsString(result));
            return;
        }
        
        // 2. 使用XSS过滤包装器处理请求
        XssRequestWrapper xssRequest = new XssRequestWrapper(request);
        chain.doFilter(xssRequest, response);
    }

    @Override
    public void destroy() {
        log.info("XSS过滤器销毁");
    }

    /**
     * 检查请求是否包含XSS攻击
     */
    private boolean containsXssAttack(HttpServletRequest request) {
        // 检查所有参数
        Map<String, String[]> params = request.getParameterMap();
        for (String key : params.keySet()) {
            String[] values = params.get(key);
            if (values != null) {
                for (String value : values) {
                    // 明显的XSS攻击模式直接拦截
                    if (isObviousXssAttack(value)) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    /**
     * 判断是否是明显的XSS攻击
     */
    private boolean isObviousXssAttack(String value) {
        if (value == null || value.isEmpty()) {
            return false;
        }
        
        String lowerValue = value.toLowerCase();
        
        // 检查明显的XSS模式
        return lowerValue.contains("<script")
            || lowerValue.contains("javascript:")
            || lowerValue.contains("onerror=")
            || lowerValue.contains("onload=")
            || lowerValue.matches(".*<[^>]*\\s+on\\w+\\s*=.*");
    }

    /**
     * 获取参数名称（脱敏）
     */
    private String getParameterNames(HttpServletRequest request) {
        return request.getParameterMap().keySet().toString();
    }
}
```

### 修改说明
> 全局过滤器会在请求进入Controller之前过滤XSS攻击。

---

## 5.3 新建 XssRequestWrapper.java

**文件路径**：`picchealth-server/src/main/java/com/picchealth/config/filter/XssRequestWrapper.java`

```java
package com.picchealth.config.filter;

import com.picchealth.utils.security.XssUtil;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletRequestWrapper;

/**
 * XSS过滤请求包装器
 * 
 * 功能说明：
 * 1. 包装HttpServletRequest
 * 2. 重写getParameter方法
 * 3. 对参数值进行XSS过滤
 * 
 * 使用方式：
 * - 将此包装器传入FilterChain
 * - Controller中通过request.getParameter()获取的值会自动过滤
 */
public class XssRequestWrapper extends HttpServletRequestWrapper {

    public XssRequestWrapper(HttpServletRequest request) {
        super(request);
    }

    /**
     * 获取参数（过滤XSS）
     */
    @Override
    public String getParameter(String name) {
        String value = super.getParameter(name);
        return XssUtil.filter(value);
    }

    /**
     * 获取参数数组（过滤XSS）
     */
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

    /**
     * 获取所有参数名
     */
    @Override
    public java.util.Enumeration<String> getParameterNames() {
        return super.getParameterNames();
    }

    /**
     * 获取参数Map（过滤XSS）
     */
    @Override
    public java.util.Map<String, String[]> getParameterMap() {
        java.util.Map<String, String[]> map = super.getParameterMap();
        java.util.Map<String, String[]> result = new java.util.HashMap<>();
        
        for (String key : map.keySet()) {
            String[] values = map.get(key);
            String[] filteredValues = new String[values.length];
            for (int i = 0; i < values.length; i++) {
                filteredValues[i] = XssUtil.filter(values[i]);
            }
            result.put(key, filteredValues);
        }
        
        return result;
    }

    /**
     * 获取Header（过滤XSS）
     */
    @Override
    public String getHeader(String name) {
        String value = super.getHeader(name);
        return XssUtil.filter(value);
    }
}
```

### 修改说明
> 请求包装器确保所有传入Controller的参数都经过XSS过滤。

---

# 🔴 P0-007：配置Redis缓存

## 修改文件清单

| 文件路径 | 操作 | 说明 |
|---------|------|------|
| `picchealth-server/src/main/java/com/picchealth/config/CacheConfig.java` | 新建 | 缓存配置 |
| `picchealth-server/src/main/java/com/picchealth/module/basedoc/service/DictionaryService.java` | 新建 | 字典服务（示例） |

---

## 7.1 新建 CacheConfig.java

**文件路径**：`picchealth-server/src/main/java/com/picchealth/config/CacheConfig.java`

```java
package com.picchealth.config;

import com.fasterxml.jackson.annotation.JsonAutoDetect;
import com.fasterxml.jackson.annotation.PropertyAccessor;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.jsontype.impl.LaissezFaireSubTypeValidator;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.cache.RedisCacheConfiguration;
import org.springframework.data.redis.cache.RedisCacheManager;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.RedisSerializationContext;
import org.springframework.data.redis.serializer.StringRedisSerializer;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

/**
 * Redis缓存配置
 * 
 * 功能说明：
 * 1. 配置Redis连接
 * 2. 配置序列化方式
 * 3. 配置不同缓存的过期时间
 * 
 * 缓存策略：
 * - dict: 字典数据，更新频率低，缓存24小时
 * - user: 用户数据，更新频率中等，缓存10分钟
 * - config: 配置数据，缓存5分钟
 * - default: 默认缓存，缓存30分钟
 */
@Configuration
@EnableCaching  // 启用Spring Cache注解支持
public class CacheConfig {

    /**
     * Redis缓存管理器配置
     * 
     * 配置说明：
     * - 默认过期时间：30分钟
     * - 序列化方式：JSON
     * - 不缓存null值
     */
    @Bean
    public RedisCacheManager cacheManager(RedisConnectionFactory factory) {
        // 默认缓存配置
        RedisCacheConfiguration defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(30))  // 默认过期时间
            .serializeKeysWith(
                // Key使用String序列化
                RedisSerializationContext.SerializationPair
                    .fromSerializer(new StringRedisSerializer()))
            .serializeValuesWith(
                // Value使用JSON序列化
                RedisSerializationContext.SerializationPair
                    .fromSerializer(new GenericJackson2JsonRedisSerializer()))
            .disableCachingNullValues();  // 不缓存null值

        // 不同缓存的配置
        Map<String, RedisCacheConfiguration> cacheConfigurations = new HashMap<>();
        
        // ===== 字典缓存 =====
        // 字典数据很少变化，设置为24小时
        cacheConfigurations.put("dict", defaultConfig
            .entryTtl(Duration.ofHours(24))
            .prefixCacheNameWith("picc:cache:"));
        
        // ===== 用户缓存 =====
        // 用户数据可能更新，设置为10分钟
        cacheConfigurations.put("user", defaultConfig
            .entryTtl(Duration.ofMinutes(10))
            .prefixCacheNameWith("picc:cache:"));
        
        // ===== 配置缓存 =====
        // 配置数据可能动态修改，设置为5分钟
        cacheConfigurations.put("config", defaultConfig
            .entryTtl(Duration.ofMinutes(5))
            .prefixCacheNameWith("picc:cache:"));
        
        // ===== 权限缓存 =====
        // 权限数据更新频率中等，设置为30分钟
        cacheConfigurations.put("permission", defaultConfig
            .entryTtl(Duration.ofMinutes(30))
            .prefixCacheNameWith("picc:cache:"));

        // 构建缓存管理器
        return RedisCacheManager.builder(factory)
            .cacheDefaults(defaultConfig.prefixCacheNameWith("picc:cache:default"))
            .withInitialCacheConfigurations(cacheConfigurations)
            .transactionAware()  // 支持事务
            .build();
    }

    /**
     * RedisTemplate配置
     * 
     * 用于更灵活的Redis操作
     */
    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(factory);
        
        // ObjectMapper配置
        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.setVisibility(PropertyAccessor.ALL, JsonAutoDetect.Visibility.ANY);
        objectMapper.activateDefaultTyping(
            LaissezFaireSubTypeValidator.instance,
            ObjectMapper.DefaultTyping.NON_FINAL);
        
        // Key序列化
        template.setKeySerializer(new StringRedisSerializer());
        template.setHashKeySerializer(new StringRedisSerializer());
        
        // Value序列化
        GenericJackson2JsonRedisSerializer jsonSerializer = 
            new GenericJackson2JsonRedisSerializer(objectMapper);
        template.setValueSerializer(jsonSerializer);
        template.setHashValueSerializer(jsonSerializer);
        
        template.afterPropertiesSet();
        return template;
    }
}
```

### 修改说明
> 缓存配置定义了：
> 1. 不同类型数据的缓存时间
> 2. 序列化和反序列化方式
> 3. 缓存key的前缀

---

## 7.2 新建 DictionaryService.java（缓存使用示例）

**文件路径**：`picchealth-server/src/main/java/com/picchealth/module/basedoc/service/DictionaryService.java`

```java
package com.picchealth.module.basedoc.service;

import com.picchealth.module.basedoc.dao.DictionaryDao;
import com.picchealth.module.basedoc.po.Dictionary;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 字典服务
 * 
 * 缓存使用说明：
 * - @Cacheable: 读取缓存，缓存不存在时查询数据库
 * - @CacheEvict: 清除缓存，新增/修改/删除数据时调用
 * 
 * 缓存key格式：
 * - dict:type:SEX  → 获取单个字典项
 * - dict:list:SEX  → 获取字典列表
 */
@Service
@Slf4j
public class DictionaryService {

    @Autowired
    private DictionaryDao dictionaryDao;

    /**
     * 获取字典项文本
     * 
     * 缓存策略：
     * - Key: dict:type:{type}:{code}
     * - TTL: 24小时
     * 
     * @param type 字典类型
     * @param code 字典编码
     * @return 字典显示文本
     */
    @Cacheable(value = "dict", key = "#type + ':' + #code")
    public String getDictText(String type, String code) {
        log.info("查询字典（数据库）: type={}, code={}", type, code);
        Dictionary dict = dictionaryDao.selectByTypeAndCode(type, code);
        return dict != null ? dict.getText() : "";
    }

    /**
     * 获取字典列表
     * 
     * 缓存策略：
     * - Key: dict:list:{type}
     * - TTL: 24小时
     * 
     * @param type 字典类型
     * @return 字典列表
     */
    @Cacheable(value = "dict", key = "'list:' + #type")
    public List<Dictionary> getDictList(String type) {
        log.info("查询字典列表（数据库）: type={}", type);
        return dictionaryDao.selectListByType(type);
    }

    /**
     * 新增字典
     * 
     * 注意：
     * - 使用@CacheEvict清除缓存
     * - allEntries=true 表示清除该缓存分区下的所有key
     * 
     * @param dict 字典对象
     */
    @CacheEvict(value = "dict", allEntries = true)
    public void insert(Dictionary dict) {
        log.info("新增字典，缓存已清除: type={}", dict.getType());
        dictionaryDao.insert(dict);
    }

    /**
     * 更新字典
     * 
     * @param dict 字典对象
     */
    @CacheEvict(value = "dict", allEntries = true)
    public void update(Dictionary dict) {
        log.info("更新字典，缓存已清除: type={}", dict.getType());
        dictionaryDao.update(dict);
    }

    /**
     * 删除字典
     * 
     * @param id 字典ID
     */
    @CacheEvict(value = "dict", allEntries = true)
    public void delete(Long id) {
        log.info("删除字典，缓存已清除: id={}", id);
        dictionaryDao.deleteById(id);
    }

    /**
     * 刷新字典缓存（手动触发）
     * 
     * 场景：
     * - 管理员在后台修改字典后
     * - 调用此方法强制刷新缓存
     */
    @CacheEvict(value = "dict", allEntries = true)
    public void refreshCache() {
        log.info("手动刷新字典缓存");
    }
}
```

### 修改说明
> 缓存使用示例：
> 1. `@Cacheable`：读取缓存，命中则跳过方法执行
> 2. `@CacheEvict`：修改数据时清除缓存
> 3. 合理设置缓存时间

---

# 📋 附录：配置检查清单

## 敏感信息检查

完成修复后，请执行以下检查：

```bash
# 1. 检查是否还有硬编码密码
grep -rn "password:" --include="*.java" --include="*.yml" | grep -v "redis\|spring\|datasource"

# 2. 检查是否还有默认密码
grep -rn "hmlink@123\|hellolevy" --include="*.java" --include="*.yml"

# 3. 检查是否还有硬编码API密钥
grep -rn "7839c25a\|7c16d7d5" --include="*.java"

# 4. 检查是否还有硬编码IP地址
grep -rn "192.168\." --include="*.java" --include="*.yml" | grep -v "example\|comment"

# 5. 检查System.out
grep -rn "System.out.println" --include="*.java" | wc -l
```

## 修复验收

| 问题编号 | 修复内容 | 验收状态 |
|----------|----------|----------|
| P0-001 | Spring Security集成 | [ ] |
| P0-002 | FTP密码移除 | [ ] |
| P0-003 | API密钥移除 | [ ] |
| P0-004 | CSRF防护 | [ ] |
| P0-005 | XSS防护 | [ ] |
| P0-006 | 代码重构（进行中） | [ ] |
| P0-007 | Redis缓存 | [ ] |

---

**文档版本**：1.0  
**更新日期**：2024年  
**审核状态**：待审核
