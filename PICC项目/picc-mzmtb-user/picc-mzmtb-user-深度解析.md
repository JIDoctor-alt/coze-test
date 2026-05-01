> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC 权限管理系统 - 深度解析

> 🎯 安全机制 / 调用链路 / 代码质量 / 业务全景

---

## 🔐 安全机制深度解析

> 🏠 安全机制就像大厦的**门禁系统**：从大门口到每个房间，层层把关

### 一、请求认证全链路

每个请求从前端到后端，要过**三道关卡**：

```
前端发送请求
    │
    ▼
┌─────────────────────────────────────────────────┐
│  第1关：TokenInterceptorConfig（门卫）             │
│  检查：你有门禁卡吗？卡还有效吗？                   │
│  通过 → 放行                                     │
│  不通过 → "登录Token无效!请重新登录"（999）         │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│  第2关：APIAuthorityFilter（楼层保安）             │
│  仅拦截 /privilege/user/* 路径                    │
│  检查：你有权限进这个房间吗？                       │
│  通过 → 放行                                     │
│  不通过 → "接口权限未通过!"                        │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│  第3关：Service层业务校验（部门经理审核）           │
│  检查：参数完整吗？账号重复吗？有敏感词吗？          │
│  通过 → 执行业务                                  │
│  不通过 → 抛 CustomException                      │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
                  数据库操作
```

### 二、Token机制详解

> 🏠 Token就像你的**临时工牌**，有效期1天（1440分钟）

**Token存储位置**：Redis
```
Key: API_TOKEN + token值     →  Value: User对象（含userId、userName、orgId等）
Key: UrlPermission + userId   →  Value: 该用户有权限的URL列表
Key: flag: + userId           →  Value: 该用户的权限编码（逗号分隔）
```

**Token验证流程**：
```java
// 第1步：从请求头取Token
token = request.getHeader("token");
userId = request.getHeader("userId");  // 可选

// 第2步：从Redis查Token对应的用户
User user = redis.get("API_TOKEN:" + token);
if (user == null) → "登录Token无效"

// 第3步：检查用户权限编码
String permission = redis.get("flag:" + user.getUserId());
if (!permission.contains("88")) → "账号无权限访问该菜单"
// ⚠️ 权限编码 "88" 是硬编码的！

// 第4步：续期Token（每次有效请求续期1440分钟）
redis.set("API_TOKEN:" + token, user, 1440);
```

**关键发现**：
- Token有效期1天，每次请求自动续期
- 权限编码 `88` 是硬编码的"权限管理菜单"标识
- `tokenInterceptFlag` 配置可关闭Token校验（开发环境方便调试）
- 请求结束后 `UserUtils.remove()` 清除ThreadLocal，防止内存泄漏

### 三、URL权限校验（APIAuthorityFilter）

> 🏠 就像楼层保安查"你能进哪个房间"

**只拦截**：`/privilege/user/*` 路径（注意：角色/菜单/机构接口不拦截！）

**校验逻辑**：
```java
// 从Redis取用户的URL权限列表
List<String> urlList = redis.get("UrlPermission:" + userId);
// 检查当前请求路径是否在权限列表中
long count = urlList.stream().filter(s -> s.contains(requestPath)).count();
if (count == 0) → "接口权限未通过!"
```

**⚠️ 安全隐患**：URL匹配用的是 `s.contains(requestPath)`，不是精确匹配！
- 比如 `requestPath = "/privilege/user/create"`
- 如果权限列表里有 `/privilege/user/`，也会匹配通过
- 攻击者可能利用这个模糊匹配绕过权限

### 四、密码加密体系

系统用了**三层加密**保护密码：

```
明文密码
    │
    ▼ SM4加密（国密，存储时使用）
密文（Base64格式，存入数据库）
    │
    ▼ 前端传输时用RSA加密（防传输窃听）
RSA密文
    │
    ▼ 重置密码时用MD5+盐（旧系统兼容）
MD5值
```

| 加密方式 | 用途 | 算法 | 密钥管理 |
|----------|------|------|----------|
| SM4 | 密码存储加密 | SM4/ECB/PKCS5Padding | ⚠️ 硬编码 `1234567812345678` |
| RSA | 密码传输加密 | RSA 1024位 | 在测试类中硬编码了公私钥 |
| MD5+盐 | 旧系统密码回退 | MD5 | 盐值是"PICC" |
| AES | 敏感字段加密 | AES/ECB/PKCS5Padding | ⚠️ 默认 `abcdefgabcdefg12` |
| SHA-256 | 客户端哈希 | SHA-256 | 无盐 |

**⚠️ 严重安全问题**：
1. SM4密钥硬编码在源码中（`1234567812345678`）
2. AES密钥硬编码（`abcdefgabcdefg12`）
3. RSA公私钥硬编码在测试类中
4. MD5加密已有两个方法，一个标注"有问题"但没删
5. `encodeMD5` 和 `encodeMD52` 和 `encodeMD5Small` 三个方法功能几乎一样，代码冗余

### 五、敏感词过滤

```java
// 创建/修改用户时检查账号是否包含敏感词
List<SensitiveWords> sensitiveWordsList = sensitiveWordsDao.selectWords();
for (SensitiveWords words : sensitiveWordsList) {
    if (userAccount.contains(words.getWord())) {
        throw new CustomException("账号包含敏感词");
    }
}
```

> 💡 敏感词存在数据库 `sensitive_words` 表中，动态管理。但检查的是"包含"关系，不是"等于"，所以 "administrator" 会被 "admin" 匹配到。

### 六、@SensitiveEncrypt 注解

> 🏠 就像给信封上的敏感信息贴**遮盖贴**，只有收件人能看

```java
@SensitiveEncrypt  // 标注在字段上
private String tel;  // 手机号传输时自动AES加密
```

**工作原理**：
- 序列化时（返回给前端）→ 自动AES加密
- 反序列化时（前端传过来）→ 自动AES解密
- 使用Jackson的Serializer/Deserializer机制

---

## 🔗 核心业务调用链路图

### 链路1：用户创建

```
前端POST /privilege/user/create
  Body: {account, name, tel, email, orgId, roleIds[], authIds[]}
    │
    ▼ TokenInterceptorConfig.preHandle()
    │  验证Token有效性 → 续期1440分钟 → 存入ThreadLocal
    │
    ▼ UserInfoApi.create(PrivilegeUserInfoDto)
    │
    ▼ UserInfoServiceImpl.create()
    │  ├─ 校验：账号/姓名/电话/机构不能为空
    │  ├─ 校验：手机号/邮箱不能重复
    │  ├─ 校验：账号不能重复
    │  ├─ 校验：机构必须存在
    │  ├─ 校验：账号不能包含敏感词
    │  ├─ 生成UUID作为userId
    │  ├─ 密码SM4加密（默认PICChealth@2020）
    │  ├─ 设置创建人/时间/修改人/时间
    │  ├─ insertSelective → privilege_user_info表
    │  ├─ setRoles() → privilege_user_role_info表
    │  └─ setAuths() → privilege_user_auth + person_division表
    │
    ▼ 返回 userId
```

### 链路2：用户登录后权限验证

```
用户在登录服务完成登录
  → 登录服务把Token+用户信息+权限URL列表写入Redis
  → 返回Token给前端
    │
前端后续请求携带Token
    │
    ▼ TokenInterceptorConfig
    │  ├─ 从请求头取Token
    │  ├─ Redis查Token → 得到User对象
    │  ├─ Redis查flag:userId → 检查权限编码是否包含"88"
    │  ├─ 续期Token
    │  └─ 存入ThreadLocal → UserUtils.setUser(user)
    │
    ▼ APIAuthorityFilter（仅/privilege/user/*路径）
    │  ├─ 从Redis查UrlPermission:userId → 得到URL列表
    │  └─ 检查当前路径是否在列表中
    │
    ▼ 业务处理...
    │
    ▼ afterCompletion()
    └─ UserUtils.remove() → 清除ThreadLocal
```

### 链路3：给角色分配菜单权限

```
前端POST /privilege/role/setResources
  Body: {roleId, systemId, menuIds[]}
    │
    ▼ RoleInfoServiceImpl.setResource()
    │  ├─ 查角色是否存在
    │  ├─ 查系统是否存在
    │  ├─ 删除该角色在当前系统下的旧权限（逻辑删除）
    │  └─ 逐个插入新权限 → privilege_role_resource表
    │
    ▼ 权限生效（需要用户重新登录，Redis缓存更新）
```

### 链路4：机构查询（最复杂的query方法）

```
前端POST /privilege/org/query
  Body: {systemId, orgId, orgName, enable, pageIndex, pageSize}
    │
    ▼ OrgInfoServiceImpl.query()
    │  ├─ 根据systemId查关联的机构ID列表
    │  │  → privilege_org_system表 + privilege_org_info表
    │  ├─ 根据条件筛选（名称模糊/状态/机构ID列表）
    │  ├─ 分页处理
    │  ├─ 对每个机构查：
    │  │  ├─ 父机构名称
    │  │  ├─ 关联的系统列表
    │  │  ├─ 系统下的菜单数量
    │  │  └─ 已授权菜单数量
    │  └─ 组装返回
    │
    ▼ 返回分页结果 + 每条记录带详细关联信息
```

---

## 🐛 代码质量分析

### 🔴 严重问题（必须修复）

| # | 问题 | 位置 | 风险 | 修复建议 |
|---|------|------|------|----------|
| 1 | **SM4密钥硬编码** | SM4Util.java:20 | 攻击者拿到源码就能解密所有密码 | 密钥放Apollo配置中心，加密存储 |
| 2 | **AES密钥硬编码** | AesUtil.java:18 | 敏感字段加密形同虚设 | 同上 |
| 3 | **RSA公私钥硬编码** | PrivilegeMoveTest.java | 可解密所有用户密码 | 移除测试类中的密钥，使用密钥管理服务 |
| 4 | **URL权限模糊匹配** | APIAuthorityFilter.java:58 | 可绕过权限校验 | 改用精确匹配或AntPathMatcher |
| 5 | **权限编码"88"硬编码** | TokenInterceptorConfig.java | 权限逻辑不灵活 | 改为配置项或枚举 |
| 6 | **APIAuthorityFilter只拦截user路径** | APIAuthorityFilter.java:28 | 角色/菜单/机构接口无URL权限校验 | 扩大拦截范围或统一权限框架 |

### 🟡 中等问题（建议修复）

| # | 问题 | 位置 | 说明 |
|---|------|------|------|
| 7 | **MD5方法重复3个** | EncryptionUtil.java | encryptMD5（有问题）、encodeMD5、encodeMD52、encodeMD5Small 功能几乎相同 |
| 8 | **默认密码太简单** | UserInfoServiceImpl.java | 默认密码 PICChealth@2020，且SM4加密后固定，可被彩虹表攻击 |
| 9 | **Token续期无条件** | TokenInterceptorConfig.java | 每次请求都续期，活跃用户Token永不过期 |
| 10 | **UserUtils默认值泄露** | UserUtils.java | getUser()返回默认用户"人保健康/中科软"，可能导致权限泄露 |
| 11 | **synchronized性能问题** | APIAuthorityFilter.java:53 | synchronized(this) 在高并发下阻塞所有请求 |
| 12 | **System.out.println未清理** | TokenInterceptorConfig.java:66 | 打印了所有请求头信息，可能泄露敏感数据 |
| 13 | **变量名拼写错误** | RoleInfoApi.java | `resouceVo` 应为 `resourceVo` |
| 14 | **中文异常信息硬编码** | 多处 | 不利于国际化，i18n配置形同虚设 |

### 🟢 学习思考

| # | 建议 | 说明 |
|---|------|------|
| 15 | **统一异常处理** | 目前CustomException和BusinessException混用，建议统一 |
| 16 | **引入参数校验框架** | 目前手动if判断，建议用 @Valid + Hibernate Validator |
| 17 | **BeanUtils.copyProperties问题** | 浅拷贝，嵌套对象可能出问题；建议用MapStruct |
| 18 | **逻辑删除不彻底** | 只做了delete_at标记，没有定期归档机制，数据量会越来越大 |
| 19 | **分页参数默认值** | 没看到对pageIndex/pageSize的上下限校验，可能被恶意传大值 |
| 20 | **日志脱敏** | TokenInterceptorConfig直接打印Token值，应脱敏 |

---

## 📊 业务全景图

### 系统部署的各地市

从 `UnitConfigEnum` 可以看出，这个慢病系统已部署在 **16个地市**：

| 编号 | 地市 | 编号 | 地市 | 编号 | 地市 |
|------|------|------|------|------|------|
| 0 | 宝鸡 | 6 | 晋中 | 12 | 新余 |
| 1 | 阜新 | 7 | 榆林 | 13 | 杨凌 |
| 2 | 商洛 | 8 | 满洲里 | 14 | 德州 |
| 3 | 张家口 | 10 | 定州 | 15 | 九江 |
| 4 | 延安 | 11 | 淮南 | 16 | 晋城 |
| 5 | 达州 | | | | |

### 各地市差异化权限配置

从 `AuthConfigEnum` 可以看出，不同地市有不同的权限开关：

| 地市 | 特殊权限 | 说明 |
|------|----------|------|
| 宝鸡 | 药品库、备案操作、病种映射编辑/删除、是否医保账号 | 功能最多 |
| 榆林 | 备案操作、是否医保账号、手动分配、敏感信息导出 | 你之前做的敏感导出权限 |
| 延安 | 数据范围控制、县区授权、备案操作 | 数据隔离要求高 |
| 商洛 | 备案操作、是否医保账号 | |
| 杨凌 | 备案操作、是否医保账号、是否修改待遇享受期 | |
| 九江 | 批量下载 | |
| 咸阳 | 备案操作 | |

> 💡 这种"按地市开关功能"的设计，就是典型的**Feature Flag（特性开关）**模式。好处是不用为每个地市单独部署，坏处是开关越来越多，代码里if-else越来越长。

---

## 🏗️ 架构优缺点总结

### ✅ 做得好的

1. **逻辑删除** - 所有表都通过 delete_at 标记删除，数据可恢复
2. **事务控制** - 增删改操作都加了 @Transactional
3. **多环境配置** - dev/test/uat/prod 四套环境隔离
4. **Apollo配置中心** - 运维友好，不用重启改配置
5. **国密算法** - 使用SM4加密，符合信创要求
6. **敏感词过滤** - 防止创建管理员类账号
7. **数据隔离** - 不同地市通过权限编码控制数据访问范围

### ❌ 需要改进的

1. **密钥管理** - 多处硬编码，安全隐患最大
2. **权限校验** - URL模糊匹配 + 只拦截user路径，安全覆盖不完整
3. **代码冗余** - 3个MD5方法、重复的权限检查代码
4. **缺乏接口文档规范** - @ApiOperation描述太简单，缺少参数示例
5. **测试覆盖不足** - 只有迁移测试，无单元测试
6. **日志安全** - 打印了Token和请求头敏感信息

---

📎 **延伸阅读**：
- [安全问题分析](picc-mzmtb-user-安全问题分析.md) - P0/P1/P2安全问题分级修复策略和代码示例
- [安全问题原理学习文档](picc-mzmtb-user-安全问题原理学习文档.md) - 具体的代码问题原理学习（SM4/AES/RSA密钥外部化等）
- [架构设计文档](picc-mzmtb-user-架构设计文档.md) - 安全架构详解、三道认证关卡流程图

