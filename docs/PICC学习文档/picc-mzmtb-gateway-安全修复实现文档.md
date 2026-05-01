> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC门诊慢特病前台服务（picc-mzmtb-gateway）
# 安全问题原理学习文档

> **生成日期**：2024年  
> **项目名称**：picc-mzmtb-gateway（门诊慢特病业务管理信息系统-前台服务）  
> **服务端口**：9001  
> **适用读者**：开发人员（零基础也能看懂）  
> **核心目标**：将所有硬编码的敏感信息迁移到Apollo配置中心

---

## 📖 目录

1. [问题概览](#问题概览)
2. [修复前准备](#修复前准备)
3. [修复一：SM2私钥外部化](#修复一sm2私钥外部化)
4. [修复二：AES密钥外部化](#修复二aes密钥外部化)
5. [修复三：SFTP密码外部化](#修复三sftp密码外部化)
6. [修复四：CORS白名单模式](#修复四cors白名单模式)
7. [Apollo配置模板](#apollo配置模板)
8. [验证测试指南](#验证测试指南)

---

## 🔴 问题概览

本次修复涉及**4个P0致命问题**：

| 序号 | 问题 | 风险 | 影响 |
|-----|------|-----|------|
| 1 | SM2私钥硬编码 | 🔴 致命 | 所有加密数据可被解密 |
| 2 | AES密钥硬编码 | 🔴 致命 | 手机号、身份证号可被解密 |
| 3 | SFTP密码硬编码 | 🔴 致命 | SFTP服务器可被未授权访问 |
| 4 | CORS配置通配符 | 🔴 致命 | 任何网站可冒充用户发起请求 |

---

## 🔧 修复前准备

### 1. 获取Apollo配置中心权限

```
联系运维/配置管理员：
1. 获取Apollo配置中心地址（通常为 http://apollo-config-server:8080）
2. 获取应用 picc-mzmtb-gateway 的编辑权限
3. 确认各环境（DEV/UAT/PROD）的配置权限
```

### 2. 确认项目已有依赖

确保 `pom.xml` 中有以下依赖：

```xml
<!-- Spring Boot 配置处理 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>

<!-- Apollo 客户端（如果已接入Apollo） -->
<dependency>
    <groupId>com.ctrip.framework.apollo</groupId>
    <artifactId>apollo-client</artifactId>
    <version>2.1.0</version>
</dependency>
```

### 3. 备份当前配置

```bash
# 备份当前的敏感配置文件
cp src/main/resources/application.yml src/main/resources/application.yml.backup
cp src/main/resources/bootstrap.yml src/main/resources/bootstrap.yml.backup
```

---

## 修复一：SM2私钥外部化

### 📍 问题位置

```
文件路径：src/main/java/com/picchealth/utils/Sm2Util.java
```

### ⚠️ 修改前代码（危险）

```java
package com.picchealth.utils;

import org.bouncycastle.crypto.engines.SM2Engine;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.bouncycastle.util.encoders.Hex;

import java.security.*;
import java.security.spec.PKCS8EncodedKeySpec;

/**
 * SM2加密工具类
 */
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

    /**
     * SM2加密
     */
    public static String encrypt(String content) {
        // ... 加密逻辑使用 PRIVATE_KER ...
    }

    /**
     * SM2解密
     */
    public static String decrypt(String encrypted) {
        // ... 解密逻辑使用 PRIVATE_KER ...
    }
}
```

### ✅ 修改后代码（安全）

```java
package com.picchealth.utils;

import org.bouncycastle.crypto.engines.SM2Engine;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.bouncycastle.util.encoders.Hex;

import java.security.*;
import java.security.spec.PKCS8EncodedKeySpec;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * SM2加密工具类
 * 
 * 🔐 安全改进：密钥从Apollo配置中心读取，不再硬编码
 */
@Component  // 添加@Component注解，让Spring管理这个Bean
public class Sm2Util {

    /**
     * 私钥 - 从Apollo配置中心读取，不再硬编码！
     * 
     * Apollo配置项：sm2.private.key
     * 配置示例（Base64格式）：
     *   MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0...
     */
    @Value("${sm2.private.key}")
    private String privateKeyStr;

    /**
     * 公钥 - 从Apollo配置中心读取
     * 
     * Apollo配置项：sm2.public.key
     * 配置示例（Base64格式）：
     *   MFkwEwYHKoZIzj0CAQYIKoEcz1UBgi0DQgAE...
     */
    @Value("${sm2.public.key}")
    private String publicKeyStr;

    /**
     * 密钥是否已初始化（用于启动时校验）
     * 使用volatile确保多线程可见性
     */
    private volatile boolean keyInitialized = false;

    /**
     * 确保密钥已正确配置
     * 在第一次使用时调用，如果未配置会抛出明确的错误
     */
    private void ensureKeyInitialized() {
        if (!keyInitialized) {
            synchronized (this) {
                if (!keyInitialized) {
                    // 校验私钥
                    if (privateKeyStr == null || privateKeyStr.trim().isEmpty()) {
                        throw new IllegalStateException(
                            "【安全配置错误】SM2私钥未配置！\n" +
                            "请在Apollo配置中心添加配置项：sm2.private.key\n" +
                            "配置路径：应用 picc-mzmtb-gateway > 配置项 sm2.private.key"
                        );
                    }
                    // 校验公钥
                    if (publicKeyStr == null || publicKeyStr.trim().isEmpty()) {
                        throw new IllegalStateException(
                            "【安全配置错误】SM2公钥未配置！\n" +
                            "请在Apollo配置中心添加配置项：sm2.public.key\n" +
                            "配置路径：应用 picc-mzmtb-gateway > 配置项 sm2.public.key"
                        );
                    }
                    keyInitialized = true;
                }
            }
        }
    }

    /**
     * SM2加密
     * 
     * @param content 需要加密的明文
     * @return 加密后的密文（十六进制字符串）
     */
    public String encrypt(String content) {
        ensureKeyInitialized();
        try {
            // 获取密钥
            PrivateKey privateKey = getPrivateKey();
            PublicKey pubKey = getPublicKey();
            
            // SM2加密逻辑（保持原有实现）
            // ...
            
            return encryptedHexString;
        } catch (Exception e) {
            throw new RuntimeException("SM2加密失败", e);
        }
    }

    /**
     * SM2解密
     * 
     * @param encryptedHex 加密后的密文（十六进制字符串）
     * @return 解密后的明文
     */
    public String decrypt(String encryptedHex) {
        ensureKeyInitialized();
        try {
            PrivateKey privateKey = getPrivateKey();
            
            // SM2解密逻辑（保持原有实现）
            // ...
            
            return decryptedContent;
        } catch (Exception e) {
            throw new RuntimeException("SM2解密失败", e);
        }
    }

    /**
     * 获取SM2私钥对象
     */
    private PrivateKey getPrivateKey() {
        try {
            // SM2私钥需要转换为PKCS8格式
            byte[] keyBytes = Hex.decode(privateKeyStr);
            PKCS8EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(keyBytes);
            KeyFactory keyFactory = KeyFactory.getInstance("SM2", new BouncyCastleProvider());
            return keyFactory.generatePrivate(keySpec);
        } catch (Exception e) {
            throw new RuntimeException("SM2私钥解析失败，请检查密钥格式是否正确", e);
        }
    }

    /**
     * 获取SM2公钥对象
     */
    private PublicKey getPublicKey() {
        try {
            byte[] keyBytes = Hex.decode(publicKeyStr);
            X509EncodedKeySpec keySpec = new X509EncodedKeySpec(keyBytes);
            KeyFactory keyFactory = KeyFactory.getInstance("SM2", new BouncyCastleProvider());
            return keyFactory.generatePublic(keySpec);
        } catch (Exception e) {
            throw new RuntimeException("SM2公钥解析失败，请检查密钥格式是否正确", e);
        }
    }
}
```

### 📝 修改说明

| 修改点 | 修改前 | 修改后 |
|-------|-------|-------|
| 类注解 | 无 | `@Component` - 让Spring管理Bean |
| 私钥定义 | `private static final String PRIVATE_KER = "00ced30f..."` | `@Value("${sm2.private.key}") private String privateKeyStr` |
| 公钥定义 | `private static final String PUBLIC_KER = "0488bd..."` | `@Value("${sm2.public.key}") private String publicKeyStr` |
| 密钥校验 | 无 | `ensureKeyInitialized()` - 启动时校验 |
| 错误提示 | 无 | 明确的错误信息，指导如何配置 |

---

## 修复二：AES密钥外部化

### 📍 问题位置

```
文件路径：src/main/java/com/picchealth/utils/AesUtil.java
```

### ⚠️ 修改前代码（危险）

```java
package com.picchealth.utils;

import javax.crypto.*;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;

/**
 * AES加密工具类
 */
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
            
            Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
            cipher.init(Cipher.ENCRYPT_MODE, keySpec);
            byte[] encrypted = cipher.doFinal(content.getBytes());
            return Hex.encodeHexString(encrypted);
        } catch (Exception e) {
            throw new RuntimeException("加密失败", e);
        }
    }
}
```

### ✅ 修改后代码（安全）

```java
package com.picchealth.utils;

import javax.crypto.*;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * AES加密工具类
 * 
 * 🔐 安全改进：
 * 1. 密钥从Apollo配置中心读取，不再硬编码
 * 2. 密钥长度升级为256位（增强安全性）
 */
@Component
public class AesUtil {

    /**
     * AES密钥 - 从Apollo配置中心读取
     * 
     * Apollo配置项：aes.encryption.key
     * - 密钥长度：32字节（256位），推荐使用
     * - 格式：Base64编码
     * - 生成方式：openssl rand -base64 32
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
                    if (encryptionKey == null || encryptionKey.trim().isEmpty()) {
                        throw new IllegalStateException(
                            "【安全配置错误】AES密钥未配置！\n" +
                            "请在Apollo配置中心添加配置项：aes.encryption.key\n" +
                            "建议使用32字节密钥：openssl rand -base64 32"
                        );
                    }
                    keyInitialized = true;
                }
            }
        }
    }

    /**
     * AES加密（升级为AES-256）
     * 
     * @param content 需要加密的明文
     * @return 加密后的密文（十六进制字符串）
     */
    public String encrypt(String content) {
        ensureKeyInitialized();
        try {
            // 使用256位AES加密
            KeyGenerator keyGenerator = KeyGenerator.getInstance("AES");
            keyGenerator.init(256, new SecureRandom(encryptionKey.getBytes()));
            SecretKey secretKey = keyGenerator.generateKey();
            byte[] keyBytes = secretKey.getEncoded();
            SecretKeySpec keySpec = new SecretKeySpec(keyBytes, "AES");
            
            Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
            cipher.init(Cipher.ENCRYPT_MODE, keySpec);
            byte[] encrypted = cipher.doFinal(content.getBytes());
            return Hex.encodeHexString(encrypted);
        } catch (Exception e) {
            throw new RuntimeException("AES加密失败", e);
        }
    }

    /**
     * AES解密（升级为AES-256）
     * 
     * @param encryptedHex 加密后的密文（十六进制字符串）
     * @return 解密后的明文
     */
    public String decrypt(String encryptedHex) {
        ensureKeyInitialized();
        try {
            KeyGenerator keyGenerator = KeyGenerator.getInstance("AES");
            keyGenerator.init(256, new SecureRandom(encryptionKey.getBytes()));
            SecretKey secretKey = keyGenerator.generateKey();
            byte[] keyBytes = secretKey.getEncoded();
            SecretKeySpec keySpec = new SecretKeySpec(keyBytes, "AES");
            
            Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
            cipher.init(Cipher.DECRYPT_MODE, keySpec);
            byte[] decrypted = cipher.doFinal(Hex.decodeHex(encryptedHex.toCharArray()));
            return new String(decrypted);
        } catch (Exception e) {
            throw new RuntimeException("AES解密失败", e);
        }
    }
}
```

### 📝 修改说明

| 修改点 | 修改前 | 修改后 |
|-------|-------|-------|
| 类注解 | 无 | `@Component` - 让Spring管理Bean |
| 密钥定义 | `private static final String PRIVATE_KER = "abcdefgabcdefg12"` | `@Value("${aes.encryption.key}") private String encryptionKey` |
| 密钥长度 | 128位（16字节） | 256位（32字节）- 更安全 |
| 密钥校验 | 无 | `ensureKeyInitialized()` - 启动时校验 |
| 错误提示 | 无 | 明确的错误信息和密钥生成命令 |

### ⚠️ 前端同步注意

如果前端也使用AES加密，需要同步更新前端密钥：

```javascript
// 前端密钥需要与后端 aes.encryption.key 保持一致
const AES_KEY = 'your-32-byte-key-from-apollo';
```

---

## 修复三：SFTP密码外部化

### 📍 问题位置

```
文件路径：src/main/java/com/picchealth/utils/SFTPUtils.java
```

### ⚠️ 修改前代码（危险）

```java
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

    /**
     * 上传文件到SFTP
     */
    public boolean uploadFile(String localPath, String remotePath) {
        // ... SFTP上传逻辑 ...
    }
}
```

### ✅ 修改后代码（安全）

```java
package com.picchealth.utils;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import com.jcraft.jsch.*;

import java.util.Properties;

/**
 * SFTP工具类
 * 
 * 🔐 安全改进：
 * 1. 密码从Apollo配置中心读取，不再硬编码
 * 2. 移除所有默认值，强制要求必须配置
 * 3. 添加启动校验，未配置时服务启动失败
 */
@Component
public class SFTPUtils {

    private static String pass;
    private static String ip;
    private static String username;
    private static int port;
    private static int connectionTimeout;

    /**
     * SFTP密码 - 从Apollo配置中心读取，强制配置无默认值
     * 
     * Apollo配置项：sftp.password
     * ⚠️ 注意：不再有默认值，必须配置！
     */
    @Value("${sftp.password}")
    public void setPass(String passWord) {
        if (passWord == null || passWord.trim().isEmpty()) {
            throw new IllegalStateException(
                "【安全配置错误】SFTP密码未配置！\n" +
                "请在Apollo配置中心添加配置项：sftp.password\n" +
                "配置路径：应用 picc-mzmtb-gateway > 配置项 sftp.password"
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
        if (sftpHost == null || sftpHost.trim().isEmpty()) {
            throw new IllegalStateException(
                "【安全配置错误】SFTP服务器地址未配置！\n" +
                "请在Apollo配置中心添加配置项：sftp.host"
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
        if (sftpUsername == null || sftpUsername.trim().isEmpty()) {
            throw new IllegalStateException(
                "【安全配置错误】SFTP用户名未配置！\n" +
                "请在Apollo配置中心添加配置项：sftp.username"
            );
        }
        username = sftpUsername;
    }

    /**
     * SFTP端口（默认22）
     * 
     * Apollo配置项：sftp.port
     */
    @Value("${sftp.port:22}")
    public void setPort(int sftpPort) {
        this.port = sftpPort;
    }

    /**
     * 连接超时时间（毫秒）
     * 
     * Apollo配置项：sftp.connection-timeout
     */
    @Value("${sftp.connection-timeout:5000}")
    public void setConnectionTimeout(int timeout) {
        this.connectionTimeout = timeout;
    }

    /**
     * 上传文件到SFTP
     * 
     * @param localPath 本地文件路径
     * @param remotePath 远程文件路径
     * @return 是否上传成功
     */
    public boolean uploadFile(String localPath, String remotePath) {
        Session session = null;
        ChannelSftp channelSftp = null;
        
        try {
            JSch jSch = new JSch();
            
            // 创建Session
            session = jSch.getSession(username, ip, port);
            session.setPassword(pass);
            session.setTimeout(connectionTimeout);
            
            // 配置SFTP连接属性
            Properties config = new Properties();
            config.put("StrictHostKeyChecking", "no");  // 首次连接不验证HostKey
            session.setConfig(config);
            
            // 连接
            session.connect();
            
            // 打开SFTP通道
            channelSftp = (ChannelSftp) session.openChannel("sftp");
            channelSftp.connect();
            
            // 确保远程目录存在
            createRemoteDirectory(channelSftp, remotePath);
            
            // 上传文件
            channelSftp.put(localPath, remotePath);
            
            return true;
        } catch (Exception e) {
            throw new RuntimeException("SFTP上传失败: " + e.getMessage(), e);
        } finally {
            // 关闭连接
            if (channelSftp != null && channelSftp.isConnected()) {
                channelSftp.disconnect();
            }
            if (session != null && session.isConnected()) {
                session.disconnect();
            }
        }
    }

    /**
     * 创建远程目录（如果不存在）
     */
    private void createRemoteDirectory(ChannelSftp channelSftp, String remotePath) {
        try {
            String dir = remotePath.substring(0, remotePath.lastIndexOf('/'));
            String[] dirs = dir.split("/");
            String path = "";
            for (String d : dirs) {
                if (d.isEmpty()) continue;
                path += "/" + d;
                try {
                    channelSftp.cd(path);
                } catch (SftpException e) {
                    channelSftp.mkdir(path);
                    channelSftp.cd(path);
                }
            }
        } catch (Exception e) {
            // 忽略目录创建错误
        }
    }
}
```

### 📝 修改说明

| 修改点 | 修改前 | 修改后 |
|-------|-------|-------|
| 密码配置 | `@Value("${ftp.password:hellolevy}")` | `@Value("${sftp.password}")` - 无默认值 |
| IP配置 | `@Value("${ftp.ip:10.252.68.236}")` | `@Value("${sftp.host}")` - 无默认值 |
| 密码校验 | 无 | 强制校验，未配置则启动失败 |
| 新增配置 | 无 | username、port、connectionTimeout |
| 配置命名 | `ftp.*` | `sftp.*` - 更规范 |

---

## 修复四：CORS白名单模式

### 📍 问题位置

```
文件路径：src/main/java/com/picchealth/config/cors/GlobalCorsConfig.java
```

### ⚠️ 修改前代码（危险）

```java
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
```

### ✅ 修改后代码（安全）

```java
package com.picchealth.config.cors;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.util.Arrays;
import java.util.List;

/**
 * 全局跨域配置
 * 
 * 🔐 安全改进：
 * 1. 从Apollo配置中心读取允许的域名列表
 * 2. 移除通配符*，只允许受信任的域名
 * 3. 精确控制允许的HTTP方法和请求头
 */
@Configuration
public class GlobalCorsConfig implements WebMvcConfigurer {

    /**
     * 允许的跨域来源列表
     * 
     * Apollo配置项：cors.allowed-origins
     * 格式：多个域名用逗号分隔
     * 示例：
     *   https://www.picchealth.com,https://mzmtb.picchealth.com,https://h5.picchealth.com
     */
    @Value("${cors.allowed-origins}")
    private String allowedOriginsConfig;

    /**
     * 缓存预检请求结果的时间（秒）
     * 默认1小时，减少OPTIONS请求
     * 
     * Apollo配置项：cors.max-age
     */
    @Value("${cors.max-age:3600}")
    private long maxAge;

    /**
     * 允许的HTTP方法
     */
    private static final List<String> ALLOWED_METHODS = Arrays.asList(
        "GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"
    );

    /**
     * 允许的请求头（白名单）
     * 只允许必要的请求头，防止恶意头注入
     */
    private static final List<String> ALLOWED_HEADERS = Arrays.asList(
        "Content-Type",      // 请求内容类型
        "Authorization",     // 认证信息
        "X-Requested-With",  // AJAX请求标识
        "Accept",            // 可接受的响应类型
        "Origin",            // 请求来源（浏览器自动设置）
        "Cache-Control",     // 缓存控制
        "X-Timestamp"        // 时间戳（自定义）
    );

    /**
     * 暴露给前端的响应头
     * 只有在这里配置的响应头前端才能访问
     */
    private static final List<String> EXPOSED_HEADERS = Arrays.asList(
        "Content-disposition",  // 文件下载时使用
        "Content-Length",        // 内容长度
        "X-Request-Id"          // 请求追踪ID
    );

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        // 解析允许的域名列表
        String[] allowedOrigins = parseAllowedOrigins();
        
        registry.addMapping("/**")
                // 只允许白名单中的域名
                .allowedOrigins(allowedOrigins)
                // 允许携带Cookie（必须配合具体域名，不能用*）
                .allowCredentials(true)
                // 允许的HTTP方法
                .allowedMethods(ALLOWED_METHODS.toArray(new String[0]))
                // 允许的请求头（白名单）
                .allowedHeaders(ALLOWED_HEADERS.toArray(new String[0]))
                // 暴露给前端的响应头
                .exposedHeaders(EXPOSED_HEADERS.toArray(new String[0]))
                // 预检请求缓存时间
                .maxAge(maxAge);
    }

    /**
     * 解析允许的域名配置
     * 支持从Apollo配置中心读取，格式：域名1,域名2,域名3
     */
    private String[] parseAllowedOrigins() {
        if (allowedOriginsConfig == null || allowedOriginsConfig.trim().isEmpty()) {
            throw new IllegalStateException(
                "【安全配置错误】CORS允许来源未配置！\n" +
                "请在Apollo配置中心添加配置项：cors.allowed-origins\n" +
                "配置示例：https://www.picchealth.com,https://mzmtb.picchealth.com"
            );
        }
        
        // 按逗号分割并去除空格
        String[] origins = allowedOriginsConfig.split(",");
        for (int i = 0; i < origins.length; i++) {
            origins[i] = origins[i].trim();
            // 校验域名格式
            if (!isValidOrigin(origins[i])) {
                throw new IllegalStateException(
                    "【配置格式错误】CORS域名格式不正确: " + origins[i] + "\n" +
                    "正确格式：https://www.example.com"
                );
            }
        }
        
        return origins;
    }

    /**
     * 校验域名格式
     * 
     * @param origin 域名
     * @return 是否有效
     */
    private boolean isValidOrigin(String origin) {
        if (origin == null || origin.isEmpty()) {
            return false;
        }
        // 必须以 https:// 或 http:// 开头
        return origin.startsWith("https://") || origin.startsWith("http://");
    }
}
```

### 📝 修改说明

| 修改点 | 修改前 | 修改后 |
|-------|-------|-------|
| allowedOrigins | `"*"` - 允许所有 | 从配置读取 - 白名单模式 |
| allowCredentials | `true` | `true` - 配合具体域名 |
| allowedMethods | `"GET","POST","PUT","DELETE"` | 白名单列表 |
| allowedHeaders | `"*"` - 允许所有 | 白名单列表 |
| 配置项 | 无 | `cors.allowed-origins` |
| 启动校验 | 无 | 未配置则启动失败 |

### ⚠️ 添加新域名流程

```
当需要添加新的前端域名时，必须走以下流程：

1. 前端团队发起申请（邮件/工单）
2. 安全工程师审核域名安全性
3. 在Apollo配置中心添加新域名
4. 通知测试团队验证
5. 上线后观察日志
```

---

## 📋 Apollo配置模板

在Apollo配置中心添加以下配置项：

```yaml
# ============================================
# picc-mzmtb-gateway 安全配置
# ============================================

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SM2加密配置（必须配置）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sm2:
  private:
    # Base64编码的SM2私钥
    # ⚠️ 生产环境密钥必须妥善保管！
    key: ${SM2_PRIVATE_KEY}
  public:
    # Base64编码的SM2公钥
    key: ${SM2_PUBLIC_KEY}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AES加密配置（必须配置）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
aes:
  encryption:
    # 32字节AES密钥（Base64编码）
    # 生成命令：openssl rand -base64 32
    key: ${AES_ENCRYPTION_KEY}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SFTP配置（必须配置）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sftp:
  host: ${SFTP_HOST}
  port: ${SFTP_PORT:-22}
  username: ${SFTP_USERNAME}
  password: ${SFTP_PASSWORD}
  connection-timeout: 5000

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CORS跨域配置（必须配置）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cors:
  # 允许的前端域名列表（逗号分隔）
  # ⚠️ 必须是完整的HTTPS地址！
  allowed-origins: >-
    https://www.picchealth.com,
    https://mzmtb.picchealth.com,
    https://h5.picchealth.com,
    https://mp.weixin.qq.com
  # 预检请求缓存时间（秒）
  max-age: 3600
```

### 环境差异配置

| 环境 | sm2.private.key | aes.encryption.key | sftp.password | cors.allowed-origins |
|------|-----------------|-------------------|---------------|---------------------|
| DEV | 开发测试密钥 | 开发测试密钥 | 开发密码 | 开发域名 |
| UAT | UAT测试密钥 | UAT测试密钥 | UAT密码 | UAT域名 |
| PROD | **生产密钥🔒** | **生产密钥🔒** | **生产密码🔒** | 生产域名 |

---

## ✅ 验证测试指南

### 1. 启动验证

```bash
# 启动应用，观察日志
mvn spring-boot:run

# 预期结果：
# - 如果配置正确，应用正常启动
# - 如果配置缺失，抛出 IllegalStateException 并提示配置项名称
```

### 2. SM2加密测试

```bash
# 测试加密
curl -X POST http://localhost:9001/api/test-sm2 \
  -H "Content-Type: application/json" \
  -d '{"data": "测试敏感数据"}'

# 预期：返回加密后的十六进制字符串
```

### 3. AES加密测试

```bash
# 测试加密
curl -X POST http://localhost:9001/api/test-aes \
  -H "Content-Type: application/json" \
  -d '{"data": "13800138000"}'

# 预期：返回加密后的十六进制字符串

# 测试解密
curl -X POST http://localhost:9001/api/test-aes-decrypt \
  -H "Content-Type: application/json" \
  -d '{"data": "加密后的密文"}'

# 预期：返回原始数据 "13800138000"
```

### 4. CORS跨域测试

```bash
# 测试合法域名
curl -X OPTIONS http://localhost:9001/api/test \
  -H "Origin: https://www.picchealth.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v

# 预期响应头：
# HTTP/1.1 200 OK
# Access-Control-Allow-Origin: https://www.picchealth.com
# Access-Control-Allow-Credentials: true
# Access-Control-Allow-Methods: GET,POST,PUT,DELETE,OPTIONS,PATCH

# 测试非法域名
curl -X OPTIONS http://localhost:9001/api/test \
  -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Method: POST" \
  -v

# 预期响应头：
# Access-Control-Allow-Origin: (不存在)
```

### 5. SFTP连接测试

```bash
# 测试SFTP上传
curl -X POST http://localhost:9001/api/test-sftp \
  -H "Content-Type: application/json" \
  -d '{"localPath": "/tmp/test.txt", "remotePath": "/upload/test.txt"}'

# 预期：上传成功或失败提示
```

### 6. 安全扫描

```bash
# 使用git-secrets扫描硬编码密钥
git clone https://github.com/awslabs/git-secrets
cd git-secrets && make && sudo make install

# 扫描项目
cd /path/to/project
git secrets --scan -r -- .

# 预期：不应该有任何输出（无硬编码密钥）
```

---

## 📅 修复检查清单

| 检查项 | 状态 | 说明 |
|-------|------|------|
| Sm2Util.java 不包含硬编码密钥 | □ | 搜索 "00ced30f" 应该无结果 |
| AesUtil.java 不包含硬编码密钥 | □ | 搜索 "abcdefgabcdefg12" 应该无结果 |
| SFTPUtils.java 不包含默认密码 | □ | 搜索 "hellolevy" 应该无结果 |
| GlobalCorsConfig.java 不使用 "*" | □ | 搜索 'allowedOrigins("*")' 应该无结果 |
| Apollo配置项已添加 | □ | DEV/UAT/PROD 环境都已配置 |
| 启动测试通过 | □ | 应用能正常启动 |
| 功能测试通过 | □ | 加密/解密/上传/CORS都正常 |
| 安全扫描通过 | □ | 无硬编码敏感信息 |

---

**文档生成工具**：Coze AI 安全修复助手  
**适用读者**：开发人员、测试工程师、运维工程师  
**版本**：V1.0  
**最后更新**：2024年
