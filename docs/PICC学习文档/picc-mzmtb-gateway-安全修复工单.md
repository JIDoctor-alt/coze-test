> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC门诊慢特病前台服务（picc-mzmtb-gateway）
# 安全修复工单

> **生成日期**：2024年  
> **项目名称**：picc-mzmtb-gateway（门诊慢特病业务管理信息系统-前台服务）  
> **服务端口**：9001  
> **涉及文件**：809个Java文件，102个API接口  
> **修复周期**：3周（建议）

---

## 📋 工单概览

| 工单编号 | 问题 | 风险等级 | 预估工时 | 负责人 | 状态 |
|---------|------|---------|---------|-------|------|
| SEC-GW-001 | SM2私钥硬编码 | 🔴 P0 | 4人天 | 待分配 | 待修复 |
| SEC-GW-002 | AES密钥硬编码 | 🔴 P0 | 2人天 | 待分配 | 待修复 |
| SEC-GW-003 | SFTP密码硬编码 | 🔴 P0 | 2人天 | 待分配 | 待修复 |
| SEC-GW-004 | CORS配置漏洞 | 🔴 P0 | 1人天 | 待分配 | 待修复 |
| SEC-GW-005 | 敏感Header全转发 | 🟠 P1 | 4人天 | 待分配 | 待修复 |
| SEC-GW-006 | XSS过滤器Cookie错误 | 🟠 P1 | 1人天 | 待分配 | 待修复 |
| SEC-GW-007 | RestTemplate无超时 | 🟠 P1 | 2人天 | 待分配 | 待修复 |
| SEC-GW-008 | SSRF后端地址风险 | 🟡 P2 | 2人天 | 待分配 | 待修复 |
| SEC-GW-009 | 异常信息泄露手机号 | 🟡 P2 | 1人天 | 待分配 | 待修复 |
| SEC-GW-010 | ThreadLocal未清理 | 🟡 P2 | 1人天 | 待分配 | 待修复 |
| SEC-GW-011 | SecurityHeaders不完整 | 🟡 P2 | 2人天 | 待分配 | 待修复 |

**🔴 P0工单合计**：9人天  
**🟠 P1工单合计**：7人天  
**🟡 P2工单合计**：6人天  
**总工时**：约22人天

---

## 🔴 P0级工单（必须立即修复）

---

## 工单编号：SEC-GW-001
### SM2加密私钥硬编码

**风险等级**：🔴 P0（致命）  
**预估工时**：4人天  
**影响范围**：所有加密通信、用户敏感数据  
**协作部门**：前端团队（需同步修改）、配置中心管理员

---

### 问题描述（小白化解释）

**想象一下这个场景**：
> 你把保险柜的密码用马克笔写在保险柜门上，还拍了照片发朋友圈告诉大家你家的保险柜有多安全！

**实际情况**：
- SM2私钥 `00ced30f88fc9187c1777957e2613df69b28284cd7689e300f4db27f62a616b3d3` 直接写在代码里
- 任何能访问源代码的人都能解密所有加密数据
- 如果代码泄露（如GitHub），所有加密数据立即失效
- 密钥泄漏后无法轮换，必须修改代码重新部署

**为什么是P0？**
- 🚨 直接暴露核心加密密钥
- 🚨 用户身份证号、登录凭证可被解密
- 🚨 无法通过常规手段修复（必须改代码+重新部署）
- 🚨 影响整个系统的安全基础

---

### 问题分析

#### 方案选择：Apollo配置中心（推荐）

```
┌─────────────────────────────────────────────────────────────┐
│                      修改前：硬编码                          │
├─────────────────────────────────────────────────────────────┤
│  代码仓库                                                    │
│  ┌─────────────────┐                                        │
│  │ Sm2Util.java    │ ← 私钥明文在这里！                     │
│  │ PRIVATE_KER =   │                                        │
│  │ "00ced30f..."   │                                        │
│  └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘

                              ↓ 修改后

┌─────────────────────────────────────────────────────────────┐
│                      修改后：配置中心                        │
├─────────────────────────────────────────────────────────────┤
│  Apollo配置中心         代码仓库                            │
│  ┌─────────────────┐    ┌─────────────────┐                 │
│  │ sm2.private.key │ →  │ Sm2Util.java   │                 │
│  │ = "真实密钥"    │    │ @Value读取     │                 │
│  └─────────────────┘    └─────────────────┘                 │
│           ↓                                                  │
│  不同环境不同密钥                                              │
│  - DEV: 测试密钥                                             │
│  - UAT: 测试密钥                                             │
│  - PROD: 生产密钥 🔒                                         │
└─────────────────────────────────────────────────────────────┘
```

#### 学习路径

1. **Step 1**：在Apollo配置中心创建命名空间 `encryption-keys`
2. **Step 2**：为每个环境配置SM2私钥
3. **Step 3**：修改 `Sm2Util.java` 使用 `@Value` 读取配置
4. **Step 4**：前端同步更新（如果前端也用到SM2）
5. **Step 5**：测试验证加解密正常
6. **Step 6**：生产环境上线后，旧密钥作废

---

### 问题原理

**文件位置**：`com.picchealth.utils.Sm2Util.java`

```java
// ═══════════════════════════════════════════════════════════════
//                      🔴 修改前（危险）
// ═══════════════════════════════════════════════════════════════
package com.picchealth.utils;

import org.bouncycastle.crypto.engines.SM2Engine;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.bouncycastle.util.encoders.Hex;

import java.security.*;
import java.security.spec.PKCS8EncodedKeySpec;

public class Sm2Util {
    
    /**
     * 私钥 - 这应该是绝密信息！
     * ⚠️ 危险：硬编码在代码中，任何能看到代码的人都能拿到密钥！
     */
    private static final String PRIVATE_KER = "00ced30f88fc9187c1777957e2613df69b28284cd7689e300f4db27f62a616b3d3";

    /**
     * 公钥
     */
    private static final String PUBLIC_KER = "0488bd65709c64c5c2262a2777ef0b1a2b0af0492b124f44e282ca9a0e34a935bfda26daf70df691b28a130c283918edcdaf573da95909176baa01ffaa9bb7380d";

    // ... 其他代码 ...
}


// ═══════════════════════════════════════════════════════════════
//                      ✅ 修改后（安全）
// ═══════════════════════════════════════════════════════════════
package com.picchealth.utils;

import org.bouncycastle.crypto.engines.SM2Engine;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.bouncycastle.util.encoders.Hex;

import java.security.*;
import java.security.spec.PKCS8EncodedKeySpec;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component  // 添加@Component注解，让Spring管理这个类
public class Sm2Util {

    /**
     * 私钥 - 从Apollo配置中心读取，不再硬编码！
     * 
     * Apollo配置项：sm2.private.key
     * 不同环境的值不同：
     * - DEV: <开发环境测试密钥>
     * - UAT: <UAT环境测试密钥>
     * - PROD: <生产环境真实密钥>
     */
    @Value("${sm2.private.key}")
    private String privateKeyStr;

    /**
     * 公钥 - 从Apollo配置中心读取
     * 
     * Apollo配置项：sm2.public.key
     */
    @Value("${sm2.public.key}")
    private String publicKeyStr;

    /**
     * 密钥是否已初始化（用于启动时校验）
     */
    private volatile boolean keyInitialized = false;

    /**
     * 初始化密钥
     * 在第一次使用时确保密钥已配置
     */
    private void ensureKeyInitialized() {
        if (!keyInitialized) {
            synchronized (this) {
                if (!keyInitialized) {
                    if (privateKeyStr == null || privateKeyStr.isEmpty()) {
                        throw new IllegalStateException(
                            "SM2私钥未配置！请在Apollo配置中心设置 sm2.private.key"
                        );
                    }
                    if (publicKeyStr == null || publicKeyStr.isEmpty()) {
                        throw new IllegalStateException(
                            "SM2公钥未配置！请在Apollo配置中心设置 sm2.public.key"
                        );
                    }
                    keyInitialized = true;
                }
            }
        }
    }

    // 获取私钥
    private PrivateKey getPrivateKey() {
        ensureKeyInitialized();
        try {
            // SM2私钥需要转换为PKCS8格式
            byte[] keyBytes = Hex.decode(privateKeyStr);
            PKCS8EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(keyBytes);
            KeyFactory keyFactory = KeyFactory.getInstance("SM2", new BouncyCastleProvider());
            return keyFactory.generatePrivate(keySpec);
        } catch (Exception e) {
            throw new RuntimeException("SM2私钥解析失败", e);
        }
    }

    // ... 其他代码保持不变 ...
}
```

**Apollo配置示例**（在Apollo配置中心添加）：

```yaml
# application.yml 或专门的加密配置
sm2:
  private:
    key: ${SM2_PRIVATE_KEY}  # 生产环境真实密钥
  public:
    key: ${SM2_PUBLIC_KEY}
```

---

### 验证方式

```bash
# 1. 代码审查验证
# - 确认 Sm2Util.java 中不存在 PRIVATE_KER 硬编码
# - 确认使用了 @Value("${sm2.private.key}")

# 2. 功能测试
curl -X POST http://localhost:9001/api/test-sm2-encrypt \
  -d '{"data": "测试敏感数据123"}'

# 预期：返回加密后的数据

# 3. 配置验证
# - 登录Apollo配置中心
# - 确认各环境都有 sm2.private.key 配置
# - 确认密钥格式正确（64位十六进制字符串）

# 4. 安全扫描
# 运行安全扫描工具，确认无硬编码密钥
```

---

## 工单编号：SEC-GW-002
### AES加密密钥硬编码

**风险等级**：🔴 P0（致命）  
**预估工时**：2人天  
**影响范围**：请求参数加密（手机号、身份证号）  
**协作部门**：前端团队（需同步修改）

---

### 问题描述（小白化解释）

**想象一下这个场景**：
> 你和朋友约定了一个暗号"天王盖地虎"，结果：
> 1. 写在明信片上寄出去（代码里）
> 2. 全世界都能看到（开源或泄露）
> 3. 一旦知道就无法更换（硬编码）

**实际情况**：
- AES密钥 `abcdefgabcdefg12` 直接写在代码里
- 请求参数中加密的手机号、身份证号可被解密
- 密钥长度仅16字节，安全性不足

---

### 问题分析

#### 学习路径

1. **Step 1**：在Apollo配置中心添加AES密钥配置
2. **Step 2**：修改 `AesUtil.java` 使用 `@Value` 读取
3. **Step 3**：使用更强的密钥（推荐32字节AES-256）
4. **Step 4**：前端同步更新
5. **Step 5**：验证加解密正常

---

### 问题原理

**文件位置**：`com.picchealth.utils.AesUtil.java`

```java
// ═══════════════════════════════════════════════════════════════
//                      🔴 修改前（危险）
// ═══════════════════════════════════════════════════════════════
package com.picchealth.utils;

import javax.crypto.*;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;

public class AesUtil {

    //密钥 (需要前端和后端保持一致) - 这是什么鬼注释？！
    //⚠️ 危险：密钥直接写在代码里，全世界都能看到！
    private static final String PRIVATE_KER = "abcdefgabcdefg12";

    /**
     * AES加密
     */
    public static String encrypt(String content) {
        try {
            KeyGenerator keyGenerator = KeyGenerator.getInstance("AES");
            keyGenerator.init(128, new SecureRandom(PRIVATE_KER.getBytes()));
            SecretKey secretKey = keyGenerator.generateKey();
            byte[] keyBytes = secretKey.getEncoded();
            SecretKeySpec keySpec = new SecretKeySpec(keyBytes, "AES");
            // ... 加密逻辑 ...
        } catch (Exception e) {
            throw new RuntimeException("加密失败", e);
        }
    }

    // ... 其他代码 ...
}


// ═══════════════════════════════════════════════════════════════
//                      ✅ 修改后（安全）
// ═══════════════════════════════════════════════════════════════
package com.picchealth.utils;

import javax.crypto.*;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class AesUtil {

    /**
     * AES密钥 - 从Apollo配置中心读取
     * 
     * Apollo配置项：aes.encryption.key
     * - 密钥长度：32字节（256位），推荐使用
     * - 格式：Base64编码或十六进制字符串
     */
    @Value("${aes.encryption.key}")
    private String encryptionKey;

    /**
     * 密钥是否已初始化
     */
    private volatile boolean keyInitialized = false;

    /**
     * 确保密钥已配置
     */
    private void ensureKeyInitialized() {
        if (!keyInitialized) {
            synchronized (this) {
                if (!keyInitialized) {
                    if (encryptionKey == null || encryptionKey.isEmpty()) {
                        throw new IllegalStateException(
                            "AES密钥未配置！请在Apollo配置中心设置 aes.encryption.key"
                        );
                    }
                    keyInitialized = true;
                }
            }
        }
    }

    /**
     * AES加密
     */
    public String encrypt(String content) {
        ensureKeyInitialized();
        try {
            KeyGenerator keyGenerator = KeyGenerator.getInstance("AES");
            keyGenerator.init(256, new SecureRandom(encryptionKey.getBytes()));
            SecretKey secretKey = keyGenerator.generateKey();
            byte[] keyBytes = secretKey.getEncoded();
            SecretKeySpec keySpec = new SecretKeySpec(keyBytes, "AES");
            // ... 加密逻辑 ...
        } catch (Exception e) {
            throw new RuntimeException("加密失败", e);
        }
    }

    // ... 其他代码保持不变 ...
}
```

**Apollo配置示例**：

```yaml
# 生产环境AES密钥（32字节，推荐使用）
aes:
  encryption:
    key: ${AES_ENCRYPTION_KEY}
```

---

### 验证方式

```bash
# 1. 代码审查验证
# - 确认 AesUtil.java 中不存在 PRIVATE_KER 硬编码

# 2. 功能测试
curl -X POST http://localhost:9001/api/test-aes-encrypt \
  -d '{"data": "13800138000"}'

# 预期：返回加密后的数据

# 3. 前后端联调测试
# 确保前端和后端使用相同的密钥能正常加解密
```

---

## 工单编号：SEC-GW-003
### SFTP密码硬编码

**风险等级**：🔴 P0（致命）  
**预估工时**：2人天  
**影响范围**：SFTP服务器（IP: 10.252.68.236）  
**协作部门**：运维团队（需配置服务器密码）

---

### 问题描述（小白化解释）

**想象一下这个场景**：
> 把服务器的门禁密码写在便利贴上贴在电脑上。万一这个代码：
> - 被新员工看到
> - 上传到GitHub
> - 被黑客扫描到
> 
> 服务器就直接门户大开！

**实际情况**：
- SFTP密码 `hellolevy` 作为默认值硬编码在代码里
- SFTP服务器IP `10.252.68.236` 也硬编码了
- 默认值让配置变成了可选，而不是必须

---

### 问题分析

#### 学习路径

1. **Step 1**：在Apollo配置中心添加SFTP配置
2. **Step 2**：移除默认值，强制要求必须配置
3. **Step 3**：添加启动校验，未配置时服务启动失败
4. **Step 4**：更新服务器密码（如果旧密码已泄露）
5. **Step 5**：测试SFTP连接正常

---

### 问题原理

**文件位置**：`com.picchealth.utils.SFTPUtils.java`

```java
// ═══════════════════════════════════════════════════════════════
//                      🔴 修改前（危险）
// ═══════════════════════════════════════════════════════════════
package com.picchealth.utils;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import com.jcraft.jsch.*;

@Component
public class SFTPUtils {

    private static String pass;
    private static String ip;

    /**
     * ⚠️ 危险：密码有默认值 hellolevy！
     * 这意味着即使不配置密码，也能运行！
     */
    @Value("${ftp.password:hellolevy}")
    public void setPass(String passWord){
        pass = passWord;
    }

    /**
     * ⚠️ 危险：IP地址硬编码！
     */
    @Value("${ftp.ip:10.252.68.236}")
    public void setIp(String ftpIp){
        ip = ftpIp;
    }

    // ... 其他代码 ...
}


// ═══════════════════════════════════════════════════════════════
//                      ✅ 修改后（安全）
// ═══════════════════════════════════════════════════════════════
package com.picchealth.utils;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import com.jcraft.jsch.*;

@Component
public class SFTPUtils {

    private static String pass;
    private static String ip;
    private static String username;

    /**
     * SFTP密码 - 从Apollo配置中心读取，强制配置无默认值
     * 
     * Apollo配置项：sftp.password
     * ⚠️ 注意：不再有默认值，必须配置！
     */
    @Value("${sftp.password}")
    public void setPass(String passWord) {
        if (passWord == null || passWord.isEmpty()) {
            throw new IllegalStateException(
                "SFTP密码未配置！请在Apollo配置中心设置 sftp.password"
            );
        }
        pass = passWord;
    }

    /**
     * SFTP服务器地址
     * 
     * Apollo配置项：sftp.host
     */
    @Value("${sftp.host}")
    public void setHost(String sftpHost) {
        if (sftpHost == null || sftpHost.isEmpty()) {
            throw new IllegalStateException(
                "SFTP服务器地址未配置！请在Apollo配置中心设置 sftp.host"
            );
        }
        ip = sftpHost;
    }

    /**
     * SFTP用户名
     * 
     * Apollo配置项：sftp.username
     */
    @Value("${sftp.username}")
    public void setUsername(String sftpUsername) {
        if (sftpUsername == null || sftpUsername.isEmpty()) {
            throw new IllegalStateException(
                "SFTP用户名未配置！请在Apollo配置中心设置 sftp.username"
            );
        }
        username = sftpUsername;
    }

    /**
     * SFTP端口（可选，默认22）
     */
    @Value("${sftp.port:22}")
    private int port;

    /**
     * 连接超时时间（毫秒）
     */
    @Value("${sftp.connection-timeout:5000}")
    private int connectionTimeout;

    // ... 其他代码保持不变 ...
}
```

**Apollo配置示例**：

```yaml
# SFTP配置 - 必须配置，无默认值
sftp:
  host: ${SFTP_HOST}        # 如：10.252.68.236
  port: ${SFTP_PORT}        # 如：22
  username: ${SFTP_USERNAME}
  password: ${SFTP_PASSWORD}
  connection-timeout: 5000
```

---

### 验证方式

```bash
# 1. 配置验证
# - 登录Apollo配置中心
# - 确认 sftp.password, sftp.host, sftp.username 都有配置

# 2. 启动测试
# - 注释掉某个配置项
# - 启动服务，应该抛出 IllegalStateException

# 3. 功能测试
curl -X POST http://localhost:9001/api/test-sftp-upload \
  -d '{"filename": "test.txt"}'

# 预期：SFTP上传成功

# 4. 错误日志检查
# 确认密码错误时有明确的错误提示
```

---

## 工单编号：SEC-GW-004
### CORS跨域配置严重漏洞

**风险等级**：🔴 P0（致命）  
**预估工时**：1人天  
**影响范围**：所有前端页面（可能被恶意网站冒充）  
**协作部门**：前端团队（确认合法域名）

---

### 问题描述（小白化解释）

**想象一下这个场景**：
> 你家的门：
> - 地址公开（/**）
> - 任何人都能进（*）
> - 还能复制你的钥匙带走（credentials=true）
> - 不用登记身份证（* headers）
> 
> 这意味着**任何网站**都可以假装成用户发起请求！

**实际情况**：
- CORS配置 `allowedOrigins("*")` 允许所有来源
- `allowCredentials(true)` 配合 `origins=*` 在浏览器中会失败
- 攻击者可以搭建钓鱼网站，窃取用户Session

---

### 问题分析

#### 学习路径

1. **Step 1**：收集所有合法的前端域名
2. **Step 2**：修改CORS配置为白名单模式
3. **Step 3**：测试各域名跨域请求正常
4. **Step 4**：添加新的域名需要走审批流程

---

### 问题原理

**文件位置**：`com.picchealth.config.cors.GlobalCorsConfig.java`

```java
// ═══════════════════════════════════════════════════════════════
//                      🔴 修改前（危险）
// ═══════════════════════════════════════════════════════════════
package com.picchealth.config.cors;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class GlobalCorsConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowedOrigins("*")  // ⚠️ 危险：允许所有来源！
                .allowCredentials(true)  // 允许携带Cookie
                .allowedMethods("GET", "POST", "PUT", "DELETE")
                .allowedHeaders("*");  // 允许所有请求头
    }
}


// ═══════════════════════════════════════════════════════════════
//                      ✅ 修改后（安全）
// ═══════════════════════════════════════════════════════════════
package com.picchealth.config.cors;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.util.Arrays;
import java.util.List;

@Configuration
public class GlobalCorsConfig implements WebMvcConfigurer {

    /**
     * 允许的跨域来源列表
     * 
     * Apollo配置项：cors.allowed-origins
     * 格式：多个域名用逗号分隔
     * 示例：https://www.picchealth.com,https://mzmtb.picchealth.com
     */
    @Value("${cors.allowed-origins}")
    private String allowedOriginsConfig;

    /**
     * 缓存预检请求结果的时间（秒）
     */
    @Value("${cors.max-age:3600}")
    private long maxAge;

    /**
     * 允许的HTTP方法
     */
    private static final List<String> ALLOWED_METHODS = Arrays.asList(
        "GET", "POST", "PUT", "DELETE", "OPTIONS"
    );

    /**
     * 允许的请求头
     */
    private static final List<String> ALLOWED_HEADERS = Arrays.asList(
        "Content-Type", "Authorization", "X-Requested-With",
        "Accept", "Origin", "Cache-Control"
    );

    /**
     * 暴露给前端的响应头
     */
    private static final List<String> EXPOSED_HEADERS = Arrays.asList(
        "Content-disposition", "Content-Length"
    );

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        // 解析允许的域名列表
        String[] allowedOrigins = parseAllowedOrigins();
        
        registry.addMapping("/**")
                .allowedOrigins(allowedOrigins)  // 只允许白名单域名
                .allowCredentials(true)  // 允许携带Cookie（配合具体域名）
                .allowedMethods(ALLOWED_METHODS.toArray(new String[0]))
                .allowedHeaders(ALLOWED_HEADERS.toArray(new String[0]))
                .exposedHeaders(EXPOSED_HEADERS.toArray(new String[0]))
                .maxAge(maxAge);  // 预检请求缓存1小时
    }

    /**
     * 解析允许的域名配置
     * 支持从Apollo配置中心读取
     */
    private String[] parseAllowedOrigins() {
        if (allowedOriginsConfig == null || allowedOriginsConfig.trim().isEmpty()) {
            throw new IllegalStateException(
                "CORS允许来源未配置！请在Apollo配置中心设置 cors.allowed-origins"
            );
        }
        
        String[] origins = allowedOriginsConfig.split(",");
        for (int i = 0; i < origins.length; i++) {
            origins[i] = origins[i].trim();
        }
        
        return origins;
    }
}
```

**Apollo配置示例**：

```yaml
# CORS跨域配置 - 只允许受信任的域名
cors:
  allowed-origins: >-
    https://www.picchealth.com,
    https://mzmtb.picchealth.com,
    https://h5.picchealth.com,
    https://mp.weixin.qq.com
  max-age: 3600
```

---

### 验证方式

```bash
# 1. 合法域名测试
curl -X OPTIONS http://localhost:9001/ppic/p/xxx \
  -H "Origin: https://www.picchealth.com" \
  -H "Access-Control-Request-Method: POST"

# 预期响应头包含：
# Access-Control-Allow-Origin: https://www.picchealth.com
# Access-Control-Allow-Credentials: true

# 2. 非法域名测试
curl -X OPTIONS http://localhost:9001/ppic/p/xxx \
  -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Method: POST"

# 预期响应头：
# Access-Control-Allow-Origin: (不存在或为null)

# 3. 浏览器控制台检查
# 打开浏览器开发者工具，访问各页面
# 查看 Network 标签，检查跨域请求的响应头
```

---

## 🟠 P1级工单（高优先级）

---

## 工单编号：SEC-GW-005
### 敏感Header全局转发漏洞

**风险等级**：🟠 P1（高危）  
**预估工时**：4人天  
**影响范围**：所有HTTP转发请求（102个API接口）  
**修复文件**：`com.picchealth.utils.HttpForwardUtil.java`

**完整代码和验证方式详见实现文档。**

---

## 工单编号：SEC-GW-006
### XSS过滤器Cookie配置错误

**风险等级**：🟠 P1（高危）  
**预估工时**：1人天  
**影响范围**：Cookie相关功能  
**修复文件**：`com.picchealth.config.xssfilter.XssRequestFilter.java`

**完整代码和验证方式详见实现文档。**

---

## 工单编号：SEC-GW-007
### RestTemplate无超时配置

**风险等级**：🟠 P1（高危）  
**预估工时**：2人天  
**影响范围**：所有HTTP转发请求  
**修复文件**：新增 `RestTemplateConfig.java`

**完整代码和验证方式详见实现文档。**

---

## 🟡 P2级工单（中优先级）

---

## 工单编号：SEC-GW-008
### SSRF风险 - 后端地址可配置

**风险等级**：🟡 P2（中危）  
**预估工时**：2人天  
**修复文件**：`com.picchealth.utils.HttpForwardUtil.java`

---

## 工单编号：SEC-GW-009
### 异常信息泄露手机号

**风险等级**：🟡 P2（中危）  
**预估工时**：1人天  
**修复文件**：`com.picchealth.config.interceptor.APIAuthorityFilter.java`

---

## 工单编号：SEC-GW-010
### ThreadLocal未清理

**风险等级**：🟡 P2（中危）  
**预估工时**：1人天  
**修复文件**：`com.picchealth.config.interceptor.FlagInterceptorConfig.java`

---

## 工单编号：SEC-GW-011
### SecurityHeaders不完整

**风险等级**：🟡 P2（中危）  
**预估工时**：2人天  
**修复文件**：`com.picchealth.config.interceptor.APIAuthorityFilter.java`

---

## 📅 3周修复时间线

```
Week 1 (Day 1-5)
├── Day 1-2: SEC-GW-001 SM2密钥外部化
│   └── 协作：前端团队同步更新
├── Day 3: SEC-GW-002 AES密钥外部化
├── Day 4: SEC-GW-003 SFTP密码外部化
└── Day 5: SEC-GW-004 CORS白名单配置

Week 2 (Day 6-10)
├── Day 6-7: SEC-GW-005 Header白名单
├── Day 8: SEC-GW-006 Cookie配置修复
├── Day 9: SEC-GW-007 RestTemplate超时
└── Day 10: 集成测试 & 回归测试

Week 3 (Day 11-15)
├── Day 11-12: SEC-GW-008~011 P2问题修复
├── Day 13-14: UAT测试
└── Day 15: 生产环境部署 & 验证
```

---

## 📋 修复完成清单

| 工单编号 | 问题 | 修复日期 | 修复人 | 测试人 | 验证结果 |
|---------|------|---------|-------|-------|---------|
| SEC-GW-001 | SM2私钥硬编码 | _________ | _________ | _________ | □ 通过 □ 失败 |
| SEC-GW-002 | AES密钥硬编码 | _________ | _________ | _________ | □ 通过 □ 失败 |
| SEC-GW-003 | SFTP密码硬编码 | _________ | _________ | _________ | □ 通过 □ 失败 |
| SEC-GW-004 | CORS配置漏洞 | _________ | _________ | _________ | □ 通过 □ 失败 |
| SEC-GW-005 | Header全转发 | _________ | _________ | _________ | □ 通过 □ 失败 |
| SEC-GW-006 | Cookie配置错误 | _________ | _________ | _________ | □ 通过 □ 失败 |
| SEC-GW-007 | RestTemplate超时 | _________ | _________ | _________ | □ 通过 □ 失败 |
| SEC-GW-008 | SSRF后端地址 | _________ | _________ | _________ | □ 通过 □ 失败 |
| SEC-GW-009 | 异常信息泄露 | _________ | _________ | _________ | □ 通过 □ 失败 |
| SEC-GW-010 | ThreadLocal未清理 | _________ | _________ | _________ | □ 通过 □ 失败 |
| SEC-GW-011 | SecurityHeaders不完整 | _________ | _________ | _________ | □ 通过 □ 失败 |

---

**文档生成工具**：Coze AI 安全修复助手  
**适用读者**：开发人员、项目经理、测试工程师、运维工程师
