> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC人保健康权限管理系统 - 安全修复实施方案

> 🎯 目标：针对已发现的6个严重安全问题和2个中等问题，给出可落地的修复步骤、代码示例和迁移方案。

---

## 一、安全问题总览与优先级

| 优先级 | 问题 | 影响范围 | 修复难度 |
|--------|------|---------|---------|
| P0 | SM4密钥硬编码 | 所有用户密码 | 中 |
| P0 | AES密钥硬编码 | 敏感数据加密 | 中 |
| P0 | RSA密钥硬编码 | 数据迁移 | 低 |
| P0 | URL权限contains模糊匹配 | 全部接口权限 | 中 |
| P1 | APIAuthorityFilter只拦截部分路径 | 用户管理接口外全部 | 低 |
| P1 | 权限编码"88"硬编码 | 用户查询逻辑 | 低 |
| P2 | 默认密码可预测 | 新建用户 | 中 |
| P2 | passwordBackMD5明文存储 | 数据迁移 | 高 |

---

## 二、P0修复：密钥外部化

### 步骤1：Apollo配置中心添加密钥配置

```yaml
# 在Apollo的application命名空间中添加：
encryption:
  sm4:
    key: ${SM4_SECRET_KEY}        # 16位随机密钥
  aes:
    key: ${AES_SECRET_KEY}        # 16位随机密钥
rsa:
  public-encrypt-key: ${RSA_PUBLIC_KEY}
  private-decrypt-key: ${RSA_PRIVATE_KEY}
privilege:
  admin-auth-code: ${ADMIN_AUTH_CODE}  # 替代硬编码的"88"
```

### 步骤2：修改SM4Util.java

```java
// 修改前（硬编码）
public class SM4Util {
    private static final String KEY = "1234567812345678";
    
    public static String sm4Encrypt(String data) {
        return sm4Encrypt(data, KEY);
    }
}

// 修改后（从Spring注入）
@Component
public class SM4Util {
    @Value("${encryption.sm4.key}")
    private String sm4Key;
    
    public String encrypt(String data) {
        return sm4Encrypt(data, sm4Key);
    }
    
    // 保留静态方法兼容旧代码，但标记@Deprecated
    @Deprecated
    private static final String OLD_KEY = "1234567812345678";
    public static String sm4Encrypt(String data) {
        return sm4Encrypt(data, OLD_KEY);
    }
}
```

### 步骤3：密码数据迁移

```sql
-- 密码迁移方案（在应用层执行，不要在数据库直接操作）
-- 1. 查出所有用户密码
-- 2. 用旧密钥SM4解密
-- 3. 用新密钥SM4加密
-- 4. 更新回数据库

-- 临时迁移脚本（Java代码）：
// @Service
// public class PasswordMigrationService {
//     @Value("${encryption.sm4.new-key}")
//     private String newKey;
//     
//     public void migrateAllPasswords() {
//         List<PrivilegeUserInfo> users = privilegeUserInfoDao.selectAll();
//         for (PrivilegeUserInfo user : users) {
//             String oldEncrypted = user.getPassword();
//             try {
//                 String plainText = SM4Util.sm4Decrypt(oldEncrypted);  // 旧密钥解密
//                 String newEncrypted = SM4Util.sm4Encrypt(plainText, newKey);  // 新密钥加密
//                 user.setPassword(newEncrypted);
//                 privilegeUserInfoDao.updateByPrimaryKey(user);
//             } catch (Exception e) {
//                 log.error("密码迁移失败: userId={}", user.getId());
//             }
//         }
//     }
// }
```

---

## 三、P0修复：URL权限精确匹配

### 步骤1：修改ApiInterceptor

```java
// 修改前
String url = request.getRequestURI();
List<String> authUrls = (List<String>) redisUtil.get(RedisKeyConf.API_AUTH_URL + userRole);
if (!authUrls.contains(url)) {  // ⚠️ contains模糊匹配
    throw new CustomException("无权限访问");
}

// 修改后
@Autowired
private AntPathMatcher pathMatcher;  // Spring自带的Ant路径匹配器

String url = request.getRequestURI();
List<String> authUrls = (List<String>) redisUtil.get(RedisKeyConf.API_AUTH_URL + userRole);

boolean hasPermission = authUrls.stream()
    .anyMatch(pattern -> pathMatcher.match(pattern, url));

if (!hasPermission) {
    log.warn("权限拒绝: user={}, url={}, authUrls={}", 
             userInfo.getUserAccount(), url, authUrls);
    throw new CustomException("无权限访问");
}
```

### 步骤2：更新数据库中的URL权限配置

```sql
-- 将精确URL改为Ant模式（如果需要通配）
-- 修改前: /privilege/user/create
-- 修改后: /privilege/user/create  (精确匹配，无需改)

-- 如果需要通配：
-- 修改前: /privilege/user/*
-- 修改后: /privilege/user/**  (Ant模式匹配子路径)
```

---

## 四、P1修复：扩展APIAuthorityFilter拦截范围

```java
// 修改前
if (url.contains("/privilege/user/")) {
    // 只校验用户管理接口
}

// 修改后
if (url.startsWith("/privilege/")) {
    // 校验所有权限管理接口
    // 排除公开接口（如登录接口）
    List<String> publicUrls = Arrays.asList(
        "/privilege/login",
        "/privilege/logout"
    );
    if (publicUrls.contains(url)) {
        chain.doFilter(request, response);
        return;
    }
    // ... 原有Token校验逻辑
}
```

---

## 五、P1修复：权限编码配置化

```java
// 修改前
if (UserUtils.getUser().getAuthCode().contains("88")) {
    // 管理员逻辑
}

// 修改后
@Value("${privilege.admin-auth-code:ADMIN}")
private String adminAuthCode;

// 在AuthConfigEnum中定义
public enum AuthConfigEnum {
    // ...
    ADMIN_AUTH_CODE("ADMIN", "管理员权限编码");
}

if (UserUtils.getUser().getAuthCode().contains(adminAuthCode)) {
    // 管理员逻辑
}
```

---

## 六、P2修复：默认密码安全增强

### 步骤1：添加首次登录强制修改密码

```java
// 在UserInfoServiceImpl.create()中
privilegeUserInfo.setMustChangePassword(true);  // 新增字段

// 在登录逻辑中检查
if (user.getMustChangePassword()) {
    return ApiResponse.ok(Map.of(
        "mustChangePassword", true,
        "message", "首次登录请修改密码"
    ));
}
```

### 步骤2：添加密码复杂度校验

```java
public class PasswordValidator {
    private static final int MIN_LENGTH = 8;
    private static final Pattern UPPER = Pattern.compile("[A-Z]");
    private static final Pattern LOWER = Pattern.compile("[a-z]");
    private static final Pattern DIGIT = Pattern.compile("[0-9]");
    private static final Pattern SPECIAL = Pattern.compile("[!@#$%^&*()_+\\-=\\[\\]{};':\"\\\\|,.<>/?]");
    
    public static void validate(String password) {
        if (password.length() < MIN_LENGTH) {
            throw new CustomException("密码长度不能少于8位");
        }
        int typeCount = 0;
        if (UPPER.matcher(password).find()) typeCount++;
        if (LOWER.matcher(password).find()) typeCount++;
        if (DIGIT.matcher(password).find()) typeCount++;
        if (SPECIAL.matcher(password).find()) typeCount++;
        if (typeCount < 3) {
            throw new CustomException("密码必须包含大写字母、小写字母、数字、特殊字符中的至少3种");
        }
    }
}
```

### 步骤3：密码过期策略

```java
// 在登录逻辑中添加
LocalDateTime passwordChanged = user.getPasswordChanged();
if (passwordChanged != null) {
    long daysSinceChange = ChronoUnit.DAYS.between(
        passwordChanged.toLocalDate(), 
        LocalDate.now()
    );
    if (daysSinceChange > 90) {
        throw new CustomException("密码已超过90天未修改，请先修改密码");
    }
}
```

---

## 七、P2修复：废弃passwordBackMD5方法

### 问题分析

```java
// 方案1：直接废弃该方法（推荐）
@Deprecated
@Override
@Transactional(rollbackForClassName = {"Exception"})
public void passwordBackMD5() {
    throw new CustomException("该方法已废弃，不允许将密码回退为明文");
}

// 方案2：如果确实需要，解密后用SM4重新加密
@Deprecated
@Override
@Transactional(rollbackForClassName = {"Exception"})
public void passwordBackMD5() {
    List<PrivilegeUserInfo> users = privilegeUserInfoDao.selectAll();
    for (PrivilegeUserInfo user : users) {
        String password = user.getPassword();
        if (StringUtils.isBlank(password)) continue;
        try {
            String decrypted = RSAUtils.privateDecrypt(privateKey, password);
            // 关键改动：解密后用SM4重新加密，不再存储明文
            String reEncrypted = SM4Util.sm4Encrypt(decrypted);
            user.setPassword(reEncrypted);
            privilegeUserInfoDao.updateByPrimaryKey(user);
        } catch (Exception e) {
            log.warn("用户{}RSA解密失败，跳过", user.getId());
        }
    }
}
```

### 已执行过passwordBackMD5的修复脚本

```java
// 如果数据库中已有明文密码，需要重新加密
public void fixPlaintextPasswords() {
    List<PrivilegeUserInfo> users = privilegeUserInfoDao.selectAll();
    for (PrivilegeUserInfo user : users) {
        String password = user.getPassword();
        if (StringUtils.isBlank(password)) continue;
        
        // 判断是否是明文（尝试SM4解密，失败则认为是明文）
        try {
            SM4Util.sm4Decrypt(password);
            // 解密成功，说明已经是加密的了，跳过
            continue;
        } catch (Exception e) {
            // 解密失败，可能是明文密码，需要加密
            String encrypted = SM4Util.sm4Encrypt(password);
            user.setPassword(encrypted);
            privilegeUserInfoDao.updateByPrimaryKey(user);
            log.info("修复明文密码: userId={}", user.getId());
        }
    }
}
```

---

## 八、修复时间线建议

```
第1周（紧急）:
├── Day1-2: Apollo添加密钥配置 + 修改SM4Util/AesUtil读取配置
├── Day3-4: 修改ApiInterceptor使用AntPathMatcher
├── Day5: 扩展APIAuthorityFilter拦截范围
└── Day5: 权限编码"88"配置化

第2周（重要）:
├── Day1-2: 密码数据迁移（旧密钥→新密钥）
├── Day3-4: 默认密码安全增强（首次修改+复杂度校验）
└── Day5: 废弃passwordBackMD5 + 修复已存在的明文密码

第3周（优化）:
├── Day1-2: 添加密码过期策略
├── Day3-4: 添加操作审计日志
└── Day5: 安全测试 + 渗透测试
```

---

## 九、修复验证清单

- [ ] SM4密钥不再出现在源码中
- [ ] AES密钥不再出现在源码中
- [ ] RSA密钥不再出现在源码中
- [ ] URL权限使用AntPathMatcher精确匹配
- [ ] 所有/privilege/*路径都经过Token校验
- [ ] 权限编码从配置读取
- [ ] 新建用户首次登录强制修改密码
- [ ] 密码复杂度校验生效
- [ ] 数据库中无明文密码
- [ ] passwordBackMD5方法已废弃
- [ ] 所有修改通过安全测试

---

📎 **延伸阅读**：
- [安全问题原理学习文档](picc-mzmtb-user-安全问题原理学习文档.md) - 具体代码实现，包括SM4Util、AesUtil、ApiInterceptor修改
- [安全修复工单](picc-mzmtb-user-安全修复工单.md) - 每个P0/P1/P2问题的详细工单卡片
- [深度解析](picc-mzmtb-user-深度解析.md) - 安全机制详解，理解三道认证关卡

