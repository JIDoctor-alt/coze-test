# PICC门诊慢特病前台服务（picc-mzmtb-gateway）
# 安全问题原理学习文档

> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

> **生成日期**：2024年  
> **项目名称**：picc-mzmtb-gateway（门诊慢特病业务管理信息系统-前台服务）  
> **服务端口**：9001  
> **适用读者**：开发人员（零基础也能看懂）  
> **核心目标**：理解硬编码敏感信息的安全风险原理

---

## 📖 目录

1. [问题概览](#问题概览)
2. [问题一：SM2私钥硬编码原理](#问题一sm2私钥硬编码原理)
3. [问题二：AES密钥硬编码原理](#问题二aes密钥硬编码原理)
4. [问题三：SFTP密码硬编码原理](#问题三sftp密码硬编码原理)
5. [问题四：CORS配置风险原理](#问题四cors配置风险原理)
6. [学习理解总结](#学习理解总结)

---

## 问题概览

| 问题编号 | 问题名称 | 风险等级 | 学习要点 |
|---------|---------|---------|---------|
| SEC-GW-001 | SM2私钥硬编码 | 🔴 P0 | 理解非对称加密密钥管理 |
| SEC-GW-002 | AES密钥硬编码 | 🔴 P0 | 理解对称加密密钥管理 |
| SEC-GW-003 | SFTP密码硬编码 | 🔴 P0 | 理解凭证安全管理 |
| SEC-GW-004 | CORS配置漏洞 | 🔴 P0 | 理解跨域安全策略 |

---

## 问题一：SM2私钥硬编码原理

### 📍 问题位置

```
文件路径：src/main/java/com/picchealth/utils/SM2Util.java
```

### 🔍 问题原理分析

📖 **学习理解**：SM2是中国国密非对称加密算法，私钥相当于"家门钥匙"，必须保密。

**当前实现分析**：

```java
// SM2Util.java - 当前实现
public class SM2Util {
    // ❌ 私钥硬编码在代码中
    private static final String PRIVATE_KEY = "this_is_a_private_key_32_bytes_long";
    
    public static String decrypt(String encryptedData) {
        // 使用硬编码的私钥解密
    }
}
```

**安全问题原理**：

1. **代码泄露风险**：代码库被访问时，密钥也泄露了
2. **无法更换**：更换密钥需要重新编译部署
3. **多环境问题**：测试环境和生产环境应该用不同密钥
4. **合规问题**：违反密钥安全管理规范

**安全影响**：
- 攻击者获取代码后可以直接解密所有数据
- 无法实现密钥轮换
- 不符合金融行业安全规范

---

## 问题二：AES密钥硬编码原理

### 📍 问题位置

```
文件路径：src/main/java/com/picchealth/utils/AESUtil.java
```

### 🔍 问题原理分析

📖 **学习理解**：AES是对称加密算法，加密和解密用同一把密钥。

**当前实现分析**：

```java
// AESUtil.java - 当前实现
public class AESUtil {
    // ❌ AES密钥硬编码
    private static final String AES_KEY = "1234567890123456";
    
    public static String encrypt(String plainText) {
        // 使用硬编码的密钥加密
    }
}
```

**安全问题原理**：

1. **对称加密特性**：知道密钥就能解密所有数据
2. **硬编码风险**：密钥随代码发布，任何人都能看到
3. **密钥管理缺失**：没有密钥轮换机制

**学习理解**：
- AES密钥应该从安全的配置中心获取
- 应该定期更换密钥
- 不同环境使用不同密钥

---

## 问题三：SFTP密码硬编码原理

### 📍 问题位置

```
文件路径：src/main/java/com/picchealth/utils/SFTPUtils.java
```

### 🔍 问题原理分析

📖 **学习理解**：SFTP密码是服务器登录凭证，相当于"服务器大门钥匙"。

**当前实现分析**：

```java
// SFTPUtils.java - 当前实现
@Component
public class SFTPUtils {
    // ❌ 密码有默认值
    @Value("${ftp.password:hellolevy}")
    public void setPass(String passWord){
        pass = passWord;
    }
}
```

**安全问题原理**：

1. **默认密码风险**：即使不配置密码，也能用默认密码连接
2. **配置文件风险**：密码明文存储在配置文件中
3. **权限过大**：SFTP账号可能有过高的文件操作权限

**安全影响**：
- 攻击者可以用默认密码连接SFTP服务器
- 可能上传恶意文件或下载敏感数据

---

## 问题四：CORS配置风险原理

### 📍 问题位置

```
文件路径：src/main/java/com/picchealth/config/CorsConfig.java
```

### 🔍 问题原理分析

📖 **学习理解**：CORS（跨域资源共享）控制哪些网站可以访问你的API。

**当前实现分析**：

```java
// CorsConfig.java - 当前实现
@Configuration
public class CorsConfig {
    @Bean
    public CorsFilter corsFilter() {
        CorsConfiguration config = new CorsConfiguration();
        // ❌ 允许所有来源
        config.addAllowedOrigin("*");
        // ❌ 允许所有方法
        config.addAllowedMethod("*");
        // ❌ 允许所有头
        config.addAllowedHeader("*");
        return new CorsFilter(source);
    }
}
```

**安全问题原理**：

1. **允许所有来源**：任何网站都可以发起跨域请求
2. **CSRF风险**：攻击者可以从恶意网站发起请求
3. **数据泄露**：敏感数据可能被恶意网站获取

**学习理解**：
- 应该配置允许的来源白名单
- 只允许可信域名访问API

---

## 学习理解总结

### 硬编码敏感信息的危害

| 危害 | 说明 |
|-----|------|
| 代码泄露 | 代码被访问时，敏感信息也泄露 |
| 无法更换 | 更换密钥需要重新编译部署 |
| 环境混淆 | 测试和生产环境使用相同密钥 |
| 合规问题 | 违反金融行业安全规范 |

### 密钥安全管理的最佳实践

📖 **学习理解**：

1. **配置中心管理**：密钥应该存储在Apollo等配置中心
2. **环境隔离**：不同环境使用不同密钥
3. **定期轮换**：定期更换密钥降低泄露风险
4. **权限控制**：限制密钥的访问权限
5. **加密存储**：密钥本身也应该加密存储

---

## 🔗 延伸阅读

- [安全修复工单](picc-mzmtb-gateway-安全修复工单.md) - 每个问题的详细工单卡片

---

> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议
