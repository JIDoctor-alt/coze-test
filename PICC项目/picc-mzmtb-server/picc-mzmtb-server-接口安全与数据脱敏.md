> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC门诊慢特病业务管理系统 - 接口安全与数据脱敏现状分析

> 📅 分析日期：2024年
> 
> 📁 源码位置：`/tmp/picc-mzmtb-server/`
> 
> 🛠 技术栈：Spring Boot + MyBatis + Activiti6 + GaussDB + Redis + Apollo
> 
> 📊 项目规模：**2,647个Java文件**
> 
> ⚠️ **声明**：本文档仅供学习理解项目现状，不涉及任何代码修改

---

## 📋 文档摘要

| 分析类别 | 现状描述 | 学习要点 |
|---------|---------|---------|
| **接口认证与授权** | 自定义Interceptor实现，Token+Redis方案 | 🏠 小区门禁系统 |
| **数据脱敏** | 部分VO使用@SensitiveEncrypt注解 | 🎭 给敏感信息戴面具 |
| **输入校验** | 散落的@Valid/@Pattern，缺乏统一校验 | 🚧 高速公路安检站 |
| **传输加密** | SM4国密+AES混合，配置中部分明文 | 🔐 给数据加锁 |
| **接口签名** | 简单的Header参数校验，无签名机制 | 📦 快递防伪标签 |

---

# 🎓 第一部分：接口认证与授权现状分析

## 1.1 零基础概念：什么是接口安全？

### 🏠 生活化比喻：接口就像大楼的门禁

想象一个高档写字楼：

```
未授权用户 → ❌ 无法进入大楼（接口需要登录）
普通员工   → ✅ 只能进自己楼层（数据权限隔离）
管理员     → ✅ 可以进所有楼层（后台管理接口）
访客       → ✅ 只能在大厅活动（公开接口）
```

### 💻 技术解释

接口安全主要解决三个问题：

| 问题 | 含义 | 类比 |
|------|------|------|
| **认证（Authentication）** | 你是谁？ | 出示身份证 |
| **授权（Authorization）** | 你能做什么？ | 员工卡只能开自己的门 |
| **数据权限** | 你能看到什么数据？ | 经理只能看自己部门的数据 |

---

## 1.2 Token验证机制详解

### 📍 核心代码位置
```
TokenInterceptorConfig.java
```

### 🔍 机制原理解析（图文版）

```
┌─────────────────────────────────────────────────────────────────┐
│                        Token验证流程图                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   用户登录                                                      │
│      │                                                         │
│      ▼                                                         │
│   ┌─────────────────┐                                          │
│   │  生成Token       │  ← UUID或其他唯一字符串                    │
│   │  存入Redis      │  ← 设置过期时间（如120分钟）                 │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   返回给前端                                                    │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐     ┌─────────────────┐                 │
│   │  前端请求时      │────▶│  Header携带Token │                 │
│   │  Authorization  │     │  或 token字段    │                 │
│   └─────────────────┘     └────────┬────────┘                 │
│                                    │                            │
│                                    ▼                            │
│                          ┌─────────────────┐                   │
│                          │  TokenInterceptor │                  │
│                          │  检查Redis       │                   │
│                          └────────┬────────┘                   │
│                                   │                             │
│              ┌────────────────────┼────────────────────┐       │
│              ▼                    ▼                    ▼       │
│         Token存在              Token过期            Token无效   │
│              │                    │                    │       │
│              ▼                    ▼                    ▼       │
│         验证通过，继续         续期或重新          返回登录页面   │
│         业务处理              登录                  ❌        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📄 关键代码解读

```java
// TokenInterceptorConfig.java 核心逻辑
public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
    
    // 1. 获取请求头中的Token
    String token = request.getHeader(RequestConstant.HEAD_TOKEN);
    
    // 2. 从Redis中查询Token对应的用户信息
    User urUser = (User) redisUtil.get(RedisKeyConf.API_TOKEN + token);
    
    if (urUser == null) {
        // Token不存在或已过期
        throw CustomException.createByMassage(999, "登录token无效!请重新登录");
    }
    
    // 3. 验证通过，续期（延长Token有效期）
    redisUtil.set(RedisKeyConf.API_TOKEN + token, urUser, 120);
    
    // 4. 将用户信息存入ThreadLocal，供后续使用
    UserUtils.setUser(urUser);
    
    return true;  // 放行
}
```

### 🎯 学习要点

```
┌────────────────────────────────────────────────────────────────┐
│                      Token机制学习要点                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ✅ 优点：                                                      │
│     • 无状态设计，适合分布式系统                                │
│     • Redis存储支持集群共享                                    │
│     • 续期机制提升用户体验                                      │
│                                                                │
│  ⚠️  注意点：                                                   │
│     • Token默认校验开关可能关闭（tokenInterceptFlag=false）      │
│     • 需要配合HTTPS使用，防止Token被窃取                        │
│     • Redis过期时间要合理设置                                  │
│                                                                │
│  💡 改进方向：                                                  │
│     • 使用JWT替代Redis存储，减少对Redis的依赖                   │
│     • 添加Token刷新机制                                        │
│     • 实现更细粒度的权限控制                                    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 1.3 接口权限控制分析

### 🗺️ 项目接口分类

通过代码扫描，项目接口主要分为以下几类：

| 接口类型 | 前缀 | 认证要求 | 示例 |
|---------|------|---------|------|
| **公开接口** | /public/, /common/ | ❌ 不需要 | 获取验证码、基础配置 |
| **用户接口** | /mb/, /vip/ | ✅ 需要Token | 申报查询、用户信息 |
| **管理接口** | /admin/, /opt/ | ✅ 需要Token+角色 | 用户管理、系统配置 |
| **外部接口** | /rest/, /interface/ | ✅ 需要syscode+password | 第三方系统对接 |
| **小程序接口** | /xcx/ | ✅ 需要签名 | 微信小程序调用 |

### 🔐 权限校验流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                      接口权限校验流程                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   请求进来                                                      │
│      │                                                         │
│      ▼                                                         │
│   ┌─────────────────┐                                          │
│   │  获取用户ID     │  ← 从Header或Token中                       │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                          │
│   │  查询Redis权限   │  ← flag:userId → 权限字符串                 │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                          │
│   │  URL权限匹配    │  ← UrlPermission:userId → URL列表           │
│   └────────┬────────┘                                          │
│            │                                                    │
│     ┌─────┴─────┐                                              │
│     ▼           ▼                                              │
│   匹配成功    匹配失败                                          │
│     │           │                                              │
│     ▼           ▼                                              │
│   业务处理    返回：无权限 ❌                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📄 权限校验核心代码

```java
// 从Redis获取用户的接口权限列表
List<String> list = (ArrayList<String>) redisUtil.get(UrlPermission + userId);

// 检查当前请求的URL是否在权限列表中
long count = list.stream()
    .filter(s -> s.contains(requestPath))  // 简单字符串包含匹配
    .count();

if (count == 0) {
    throw new CustomException("账号无权限访问该接口");
}
```

---

## 1.4 数据权限（地市/角色隔离）

### 🏛️ 数据隔离架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    多地市数据权限隔离示意                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│    ┌─────────────────────────────────────────┐                   │
│    │           用户登录请求                   │                   │
│    └─────────────────┬───────────────────────┘                   │
│                      │                                            │
│                      ▼                                            │
│    ┌─────────────────────────────────────────┐                   │
│    │        解析用户所属地市码(visonCode)      │                   │
│    └─────────────────┬───────────────────────┘                   │
│                      │                                            │
│         ┌────────────┼────────────┐                               │
│         ▼            ▼            ▼                               │
│    ┌─────────┐  ┌─────────┐  ┌─────────┐                          │
│    │  榆林   │  │  延安   │  │  商洛   │                          │
│    │YL地市码 │  │YA地市码 │  │SL地市码 │                          │
│    └────┬────┘  └────┬────┘  └────┬────┘                          │
│         │            │            │                               │
│         ▼            ▼            ▼                               │
│    ┌─────────┐  ┌─────────┐  ┌─────────┐                          │
│    │ 只能看  │  │ 只能看  │  │ 只能看  │                          │
│    │榆林数据 │  │延安数据 │  │商洛数据 │                          │
│    └─────────┘  └─────────┘  └─────────┘                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📄 地市隔离实现代码

```java
// RequestFilter.java 中的地市码转换逻辑
private void handleBizParams(RequestWrapper wrapper, HttpServletRequest req) {
    String flag = req.getHeader("flag");
    
    if (UnitConfigEnum.YL.getFlag().equals(flag)) {
        // 榆林地市
        JSONObject bodyJsonObject = new JSONObject(wrapper.getBody());
        String viSonCode = bodyJsonObject.getStr("visoncode");
        // 查询用户实际归属的地市码
        String personDivision = vipMbdeclareInfoService.getPersonDivisionYa(viSonCode);
        // 替换为实际地市码
        bodyJsonObject.set("visoncode", personDivision);
        wrapper.setBody(bodyJsonObject.toString());
    }
    // 其他地市类似处理...
}
```

---

## 1.5 接口签名机制

### 📦 生活化比喻：快递包裹上的防伪标签

```
┌─────────────────────────────────────────────────────────────────┐
│                    接口签名 = 快递防伪标签                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🏪 寄件过程：                                                  │
│     商家把商品打包 → 贴上防伪标签 → 填写快递单                    │
│                          │                                      │
│                          ▼                                      │
│  🔍 收件验证：                                                  │
│     拆开包裹 → 扫描防伪标签 → 验证真伪 → 确认签收                │
│                                                                 │
│  如果没有防伪标签：                                             │
│     ❌ 不知道是谁寄的                                            │
│     ❌ 不知道寄的东西有没有被掉包                                │
│     ❌ 无法追溯责任                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 🔐 小程序签名机制分析

```java
// XcxInterceptorConfig.java - 小程序签名拦截器
public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
    
    // 1. 获取签名（经过AES加密）
    String sign = request.getHeader(RequestConstant.HEAD_XCXSIGN);
    
    // 2. AES解密
    String aesDecrypt = AesUtil.decrypt(sign);
    
    // 3. 解析过期时间
    // 格式示例: "dataPICC2022-10-14 20:15:36"
    String exDate = aesDecrypt.split("PICC")[1];
    DateTime parse = DateUtil.parse(exDate);
    
    // 4. 验证是否过期
    if (new DateTime().before(parse)) {
        return true;  // 未过期，验证通过
    } else {
        throw CustomException.createByMassage(401, "签名已过期");
    }
}
```

### ⚠️ 当前签名机制的不足

| 问题 | 说明 | 风险等级 |
|------|------|---------|
| 无时间戳 | 无法防止重放攻击 | 🔴 高 |
| 无随机数 | 相同请求可被重放 | 🔴 高 |
| 简单加密 | AES密钥可能硬编码 | 🟠 中 |
| 无签名验证 | 只验证过期时间，不验证内容 | 🟠 中 |

### 💡 学习思考：标准的接口签名方案

```java
// 改进后的签名验证逻辑
public boolean validateSignature(HttpServletRequest request) {
    
    // 1. 获取签名参数
    String timestamp = request.getHeader("timestamp");    // 时间戳
    String nonce = request.getHeader("nonce");            // 随机数
    String signature = request.getHeader("signature");    // 签名
    String syscode = request.getHeader("syscode");        // 系统编码
    
    // 2. 时间戳校验（5分钟有效期，防止重放）
    long requestTime = Long.parseLong(timestamp);
    if (Math.abs(System.currentTimeMillis() - requestTime) > 300000) {
        throw new CustomException("请求已过期");
    }
    
    // 3. 查询系统密钥
    String secret = outSystemCache.getSecret(syscode);
    
    // 4. 生成签名
    // 签名规则：MD5(syscode + timestamp + nonce + requestBody + secret)
    String data = syscode + timestamp + nonce + getRequestBody(request) + secret;
    String expectedSign = MD5(data);
    
    // 5. 验证签名
    if (!signature.equals(expectedSign)) {
        throw new CustomException("签名验证失败");
    }
    
    return true;
}
```

---

# 🎭 第二部分：数据脱敏现状

## 2.1 零基础概念：什么是数据脱敏？

### 🎭 生活化比喻：明星的"马赛克"脸

```
┌─────────────────────────────────────────────────────────────────┐
│                    什么是数据脱敏？                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  原始数据                    脱敏后                              │
│  ┌─────────────┐           ┌─────────────┐                       │
│  │ 身份证号    │           │ 身份证号    │                       │
│  │11010119900101│  ────▶  │110101****1234│                      │
│  │1234         │           │****         │                       │
│  └─────────────┘           └─────────────┘                       │
│                                                                 │
│  ┌─────────────┐           ┌─────────────┐                       │
│  │ 手机号      │           │ 手机号      │                       │
│  │13812345678 │  ────▶    │138****5678  │                       │
│  └─────────────┘           └─────────────┘                       │
│                                                                 │
│  ┌─────────────┐           ┌─────────────┐                       │
│  │ 姓名        │           │ 姓名        │                       │
│  │ 张三丰      │  ────▶    │ 张*丰       │                       │
│  └─────────────┘           └─────────────┘                       │
│                                                                 │
│  脱敏目的：展示必要信息的同时，保护隐私                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📊 常见脱敏规则

| 数据类型 | 原始值 | 脱敏后 | 规则说明 |
|---------|-------|-------|---------|
| 手机号 | 13812345678 | 138****5678 | 显示前3后4位 |
| 身份证 | 110101199001011234 | 110101\*\*\*\*\*\*1234 | 显示前6后4位 |
| 姓名 | 张三丰 | 张\*丰 | 保留姓氏，隐藏中间字 |
| 银行卡 | 6222021234567890123 | \*\*\*\*1234 | 只显示后4位 |
| 邮箱 | zhangsan@example.com | z\*\*\*\*@example.com | 隐藏用户名 |

---

## 2.2 项目脱敏机制详解

### 📍 脱敏核心文件

```
┌─────────────────────────────────────────────────────────────────┐
│                      脱敏相关文件清单                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  注解定义：                                                      │
│  📄 SensitiveEncrypt.java          - 脱敏注解定义                   │
│                                                                 │
│  序列化器/反序列化器：                                           │
│  📄 SensitiveEncryptSerializer.java   - 序列化时加密              │
│  📄 SensitiveEncryptDeserializer.java - 反序列化时解密            │
│                                                                 │
│  加密工具：                                                      │
│  📄 AesUtil.java                 - AES加密工具                   │
│  📄 SM4Util.java                 - 国密SM4加密                   │
│                                                                 │
│  定时任务：                                                      │
│  📄 VipMbAutoMaskTask.java      - 自动脱敏批处理任务              │
│                                                                 │
│  业务类VO：                                                      │
│  📄 ForeignUserInfoVo.java       - 境外用户信息（已脱敏）          │
│  📄 QueryMbDeclareListVo.java   - 申报列表（已脱敏）             │
│  📄 QueryFLowDetailVo.java       - 流程详情（已脱敏）             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 🎨 脱敏注解机制图解

```
┌─────────────────────────────────────────────────────────────────┐
│                   @SensitiveEncrypt 注解工作流程                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────┐                                           │
│   │  定义注解        │                                           │
│   │ @SensitiveEncrypt│                                          │
│   │ (serialize=true) │                                          │
│   └────────┬────────┘                                           │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                           │
│   │ Jackson拦截      │                                           │
│   │ 字段序列化       │                                           │
│   └────────┬────────┘                                           │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐    ┌─────────────────┐                   │
│   │ SensitiveEncrypt │───▶│  AesUtil        │                   │
│   │ Serializer       │    │  .aesEncrypt() │                   │
│   └─────────────────┘    └─────────────────┘                   │
│                                                                 │
│   输入: "张三丰" ──────▶ 输出: "a3b4c5d6..." (加密字符串)        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📄 脱敏注解定义

```java
// SensitiveEncrypt.java - 注解定义
@Target(ElementType.FIELD)              // 作用于字段
@Retention(RetentionPolicy.RUNTIME)      // 运行时保留
@JacksonAnnotationsInside                 // 组合注解
@JsonSerialize(using = SensitiveEncryptSerializer.class)  // 序列化器
@JsonDeserialize(using = SensitiveEncryptDeserializer.class) // 反序列化器
public @interface SensitiveEncrypt {
    
    /**
     * 是否在序列化时加密（返回给前端时）
     */
    boolean serialize() default true;
    
    /**
     * 是否在反序列化时解密（前端传入时）
     */
    boolean deserialize() default true;
}
```

### 📄 序列化器实现

```java
// SensitiveEncryptSerializer.java - 序列化时执行加密
public class SensitiveEncryptSerializer extends JsonSerializer<Object> 
        implements ContextualSerializer {

    @Override
    public void serialize(Object value, JsonGenerator gen, SerializerProvider serializers)
            throws IOException {
        if (value == null) {
            gen.writeNull();
            return;
        }
        
        String stringValue = value.toString();
        // 关键：调用AES加密
        String encryptedValue = AesUtil.aesEncrypt(stringValue);
        gen.writeString(encryptedValue);
    }
}
```

### 📄 反序列化器实现

```java
// SensitiveEncryptDeserializer.java - 反序列化时执行解密
public class SensitiveEncryptDeserializer extends JsonDeserializer<Object> 
        implements ContextualDeserializer {

    @Override
    public Object deserialize(JsonParser p, DeserializationContext ctxt)
            throws IOException {
        String value = p.getValueAsString();
        if (value == null) {
            return null;
        }
        
        try {
            // 关键：调用AES解密
            return AesUtil.aesDecrypt(value);
        } catch (Exception e) {
            // 如果解密失败，返回原始值（可能是未加密的数据）
            return value;
        }
    }
}
```

---

## 2.3 已使用脱敏注解的字段统计

### 📊 脱敏字段分布表

| VO类名 | 脱敏字段 | 数量 |
|-------|---------|-----|
| ForeignUserInfoVo | name, tel, receiver, idcard | 4个 |
| QueryMbDeclareListVo | idcard, tel | 2个 |
| QureyFLowDetailVo | idcard, tel | 2个 |
| CallJkscVo | tel | 1个 |
| FrozenCardVo | bankcard, bankaccount | 2个 |
| QueryMbInfoVoSL | idcard, tel, bankaccount | 3个 |
| ICDDeclareVo | idcard, tel, bankaccount | 3个 |
| QueryDeclareVO | idcard, tel, bankaccount | 3个 |
| UpdateVipAccountMbmzVo | idcard, tel, bankaccount | 3个 |
| QueryAccountInfoVo | bankaccount | 1个 |

### 📄 脱敏字段使用示例

```java
// ForeignUserInfoVo.java - 境外用户信息VO
@Data
public class ForeignUserInfoVo {
    
    @ApiModelProperty(value = "第三方用户id")
    private String foreignUserId;
    
    @ApiModelProperty(value = "用户来源，WX：微信")
    private String source;

    @SensitiveEncrypt  // 姓名加密
    private String name;

    private String sex;

    private String birthday;

    private String cardType;

    private String cardNo;

    @ApiModelProperty(value = "手机号")
    @SensitiveEncrypt  // 手机号加密
    private String tel;
    
    // ... 其他字段
    
    @ApiModelProperty(value = "证件号")
    @SensitiveEncrypt  // 身份证号加密
    private String idcard;
}
```

---

## 2.4 自动脱敏批处理任务

### 🔄 定时脱敏流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                   自动脱敏批处理流程                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   定时触发（每小时）                                             │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────────┐                                          │
│   │  查询待脱敏申报   │  ← 从数据库查询过去1小时的新申报           │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                          │
│   │  开启多线程处理   │  ← 配置线程池大小（默认10）                │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                          │
│   │  下载申报图片    │  ← 从SFTP服务器下载                        │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                          │
│   │  AI智能脱敏处理  │  ← 调用图像识别，自动遮盖敏感信息           │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                          │
│   │  上传脱敏后图片  │  ← 覆盖原文件或保存到新路径                │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                          │
│   │  更新申报状态    │  ← IntelligentAuditStateEnum.Masking      │
│   └─────────────────┘                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📄 批处理任务核心代码

```java
// VipMbAutoMaskTask.java
public void run(String declareIDs, String filetype) {
    
    // 1. 创建线程池
    ExecutorService executorService = Executors.newFixedThreadPool(threadCount);
    
    // 2. 查询需要脱敏的申报ID列表
    List<String> declareidList;
    if (declareIDs != null && !declareIDs.isEmpty()) {
        // 指定了申报ID
        declareidList = Arrays.asList(declareIDs.split(","));
    } else {
        // 查询过去1小时内需要脱敏的申报
        Calendar calendar = Calendar.getInstance();
        calendar.add(Calendar.HOUR_OF_DAY, -1);
        Date oneHourAgo = calendar.getTime();
        declareidList = callMaskDao.queryNeedAutoMaskDeclareIDList(startTime);
    }
    
    // 3. 逐个处理
    for (String declareId : declareidList) {
        executorService.execute(new AutoMaskThread(fileVoList, declareId));
    }
    
    // 4. 关闭线程池
    executorService.shutdown();
}
```

---

## 2.5 脱敏现状分析与建议

### ⚠️ 当前脱敏机制的不足

| 问题 | 描述 | 影响 |
|------|------|------|
| 覆盖不全面 | 仅部分VO使用脱敏注解 | 敏感信息可能泄露 |
| 注解式脱敏 | 字段级别，无法批量处理 | 维护成本高 |
| 无脱敏类型 | 统一AES加密，无差异化 | 无法实现"显示部分" |
| 缺少监控 | 无脱敏使用统计 | 难以评估覆盖度 |

### 💡 学习思考：完善的数据脱敏体系

```java
// 建议1：定义更细粒度的脱敏类型
public enum SensitiveType {
    PHONE,      // 手机号: 138****5678
    ID_CARD,    // 身份证: 110101****1234
    BANK_CARD,  // 银行卡: ****1234
    NAME,       // 姓名: 张*
    ADDRESS,    // 地址: 北京市****
}

// 建议2：使用Jackson统一脱敏
@Configuration
public class JacksonConfig {
    
    @Bean
    public ObjectMapper objectMapper() {
        ObjectMapper mapper = new ObjectMapper();
        
        // 注册敏感字段序列化器
        SimpleModule sensitiveModule = new SimpleModule();
        sensitiveModule.addSerializer(new SensitiveFieldSerializer());
        mapper.registerModule(sensitiveModule);
        
        return mapper;
    }
}

// 建议3：全局脱敏工具类
public class SensitiveUtil {
    
    public static String maskPhone(String phone) {
        if (phone == null || phone.length() < 11) return phone;
        return phone.substring(0, 3) + "****" + phone.substring(7);
    }
    
    public static String maskIdCard(String idCard) {
        if (idCard == null || idCard.length() < 18) return idCard;
        return idCard.substring(0, 6) + "********" + idCard.substring(14);
    }
    
    public static String maskName(String name) {
        if (name == null || name.length() < 2) return name;
        return name.charAt(0) + "*".repeat(name.length() - 1);
    }
}
```

---

# 🛡️ 第三部分：输入校验现状

## 3.1 零基础概念：为什么要输入校验？

### 🚧 生活化比喻：机场安检

```
┌─────────────────────────────────────────────────────────────────┐
│                   为什么要做输入校验？                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🏢 想象一个没有安检的机场：                                     │
│                                                                 │
│  ❌ 有人携带炸弹上飞机                                           │
│  ❌ 有人用假护照过海关                                           │
│  ❌ 有人携带毒品闯关                                            │
│  ❌ 有人冒充他人登机                                            │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  🛡️ 有安检的机场：                                              │
│                                                                 │
│  ✅ 金属探测器扫描危险物品                                       │
│  ✅ X光机检查行李内容                                           │
│  ✅ 证件比对确认身份                                            │
│  ✅ 体温检测防控疫情                                            │
│                                                                 │
│  输入校验 = 代码的"安检系统"，防止恶意数据进入系统                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📊 常见输入校验类型

| 校验类型 | 目的 | 示例 |
|---------|------|------|
| **非空校验** | 确保必填字段有值 | @NotNull, @NotBlank |
| **格式校验** | 验证数据格式 | @Pattern(regexp="手机号") |
| **长度校验** | 限制数据长度 | @Size(min=11, max=11) |
| **范围校验** | 限制数值范围 | @Min, @Max |
| **类型校验** | 确保数据类型正确 | @Email, @URL |
| **业务校验** | 符合业务规则 | 自定义Validator |

---

## 3.2 @Valid / @Validated 使用现状

### 📊 校验注解使用统计

| 注解类型 | 使用数量 | 示例 |
|---------|---------|------|
| @NotBlank | 20+ | 用户名、身份证号必填 |
| @NotNull | 15+ | ID、主键必填 |
| @Pattern | 10+ | 手机号、身份证号格式 |
| @Size | 5+ | 字符串长度限制 |

### 📄 校验注解使用示例

```java
// RegisterVo.java - 注册表单
@Data
public class RegisterVo {
    
    @NotBlank(message = "请输入身份证号！")
    @Pattern(regexp = "(^[1-9]\\d{5}\\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\\d{3}$)|" +
                      "(^[1-9]\\d{5}(18|19|([23]\\d))\\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\\d{3}[0-9Xx]$)",
             message = "身份证号不正确，请重新输入")
    private String idcard;
    
    @NotBlank(message = "请输入密码！")
    @Pattern(regexp = "^[A-Za-z0-9~!@#$%^&*()_+|<>,.?/:;'\\[\\]{}\\\"]+$",
             message = "请输入数字、字母和特殊字符密码")
    private String password;
    
    @NotBlank(message = "请重复输入密码！")
    private String confirmPassword;
}

// MobileVo.java - 手机号校验
public class MobileVo {
    
    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "请输入正确的手机号码")
    private String mobile;
}

// UpdateMobileVo.java - 手机号更新
public class UpdateMobileVo {
    
    @NotBlank(message = "旧联系方式不能为空！")
    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "请输入正确的手机号码")
    private String oldMobile;
    
    @NotBlank(message = "新联系方式不能为空！")
    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "请输入正确的手机号码")
    private String newMobile;
}
```

### ⚠️ 校验注解使用问题

| 问题 | 描述 | 建议 |
|------|------|------|
| 分散使用 | 注解分散在各个VO中，缺乏统一规范 | 制定校验规范文档 |
| 不完整 | 部分必填字段缺少@NotBlank | 全面排查补充 |
| 正则复杂 | 身份证正则表达式过长 | 抽取为常量或工具类 |
| 校验不统一 | 各模块校验规则可能不一致 | 建立统一的校验框架 |

---

## 3.3 SQL注入防护现状

### 💉 生活化比喻：餐厅点餐系统

```
┌─────────────────────────────────────────────────────────────────┐
│                    什么是SQL注入？                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🍽️ 正常点餐：                                                  │
│     顾客："我要一份宫保鸡丁"                                      │
│     服务员：记下 → 厨房做菜                                      │
│                                                                 │
│  💉 SQL注入攻击：                                               │
│     顾客："我要一份宫保鸡丁; DROP TABLE orders; --"             │
│     服务员：全部执行 → 厨房做菜 + 删除所有订单                   │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  🛡️ 正确做法（参数化查询）：                                     │
│     顾客："我要一份宫保鸡丁"                                      │
│     服务员：只接受菜品名称，不执行其他命令                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### ✅ 项目SQL注入防护措施

```xml
<!-- MyBatis Mapper XML 使用 #{} 参数化查询 -->
<select id="selectById" parameterType="java.lang.String" resultType="User">
    SELECT * FROM users WHERE id = #{id}
</select>

<!-- 📖 规范写法参考（仅供学习对比）：使用 #{} -->
<select id="searchUsers" resultType="User">
    SELECT * FROM users 
    WHERE name LIKE '%' || #{name} || '%'
    AND status = #{status}
</select>

<!-- ❌ 危险：使用 ${} 直接拼接（项目中未发现） -->
<!-- <select id="searchUsers" resultType="User"> -->
<!--     SELECT * FROM users WHERE name LIKE '%${name}%' -->
<!-- </select> -->
```

### 📊 审计结果

```
┌────────────────────────────────────────────────────────────────┐
│                    SQL注入防护审计结果                           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│   检查项                          结果                          │
│   ──────────────────────────────────────────────────────────   │
│   ${} 直接拼接                    ✅ 未发现                      │
│   #{} 参数化查询                 ✅ 大量使用                     │
│   MyBatis动态SQL                 ✅ 使用 <if> 标签              │
│   存储过程                        ⚠️  需进一步确认               │
│                                                                │
│   结论：项目中MyBatis使用规范，SQL注入风险较低                   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 3.4 XSS过滤现状

### 🖥️ 生活化比喻：论坛发帖

```
┌─────────────────────────────────────────────────────────────────┐
│                    什么是XSS攻击？                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📝 正常发帖：                                                  │
│     用户输入：<script>alert('你好')</script>                      │
│     论坛显示：alert('你好')  （纯文本）                          │
│                                                                 │
│  💉 XSS攻击：                                                   │
│     用户输入：<script>document.location='黑客网站'</script>       │
│     论坛显示：（执行脚本）→ 跳转到黑客网站                        │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  攻击后果：                                                      │
│     🔴 窃取用户Cookie（冒充用户登录）                            │
│     🔴 篡改页面内容                                             │
│     🔴 植入恶意软件                                             │
│     🔴 进行钓鱼诈骗                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### ⚠️ 审计结果

```bash
$ grep -r "XSS\|escape\|sanitize\|HtmlUtils" --include="*.java"
# 无任何XSS防护代码
```

### 🛡️ XSS防护建议

```java
// 方案1：Spring Boot HTML转义
@Configuration
public class XssConfig implements WebMvcConfigurer {
    
    @Override
    public void addFormatters(FormatterRegistry registry) {
        registry.addConverter(new StringTrimmerEditor(true) {
            @Override
            public void setAsText(String text) {
                // 移除HTML标签
                super.setValue(text == null ? null : 
                    text.replaceAll("<[^>]*>", ""));
            }
        });
    }
}

// 方案2：使用Hutool的XssUtil
import cn.hutool.http.html.XssUtil;

// 过滤用户输入
public String sanitizeInput(String input) {
    return XssUtil.filter(input);
}

// 方案3：使用OWASP Java HTML Sanitizer
import org.owasp.html.PolicyFactory;
import org.owasp.html.Sanitizers;

public static final PolicyFactory POLICY = Sanitizers.FORMATTING
    .and(Sanitizers.BLOCKS)
    .and(Sanitizers.LINKS);

public String sanitize(String input) {
    return POLICY.sanitize(input);
}
```

---

## 3.5 文件上传校验现状

### 📎 生活化比喻：快递公司收件

```
┌─────────────────────────────────────────────────────────────────┐
│                    文件上传的安全风险                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📦 正常包裹：                                                   │
│     重量：2kg, 尺寸：30x20x10cm, 内容：衣物                       │
│     → 正常收件、运输、送达                                        │
│                                                                 │
│  💣 恶意文件：                                                   │
│     文件名：document.pdf.exe                                     │
│     内容：可执行病毒                                             │
│     → 上传 → 服务器执行 → 系统被入侵                             │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  需要校验的内容：                                                 │
│     ✅ 文件类型（扩展名、MIME类型）                                │
│     ✅ 文件大小                                                  │
│     ✅ 文件内容（真实格式）                                       │
│     ✅ 存储路径                                                  │
│     ✅ 存储文件名（防覆盖、防目录遍历）                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📄 项目文件处理代码

```java
// FileUtils.java - 文件工具类
public class FileUtils {
    
    /**
     * 保存文件
     */
    public static void saveFileByInputStream(InputStream is, String fileName) {
        BufferedInputStream in = null;
        BufferedOutputStream out = null;
        
        try {
            in = new BufferedInputStream(is);
            File file = new File(fileName);
            
            // 创建父目录
            File fileParent = file.getParentFile();
            if (!fileParent.exists()) {
                fileParent.mkdirs();
            }
            
            // 创建文件
            file.createNewFile();
            out = new BufferedOutputStream(new FileOutputStream(file));
            
            // 写入内容
            byte[] b = new byte[1024];
            while ((len = in.read(b)) != -1) {
                out.write(b, 0, len);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

### ⚠️ 当前文件上传安全问题

| 问题 | 描述 | 风险 |
|------|------|------|
| 无类型校验 | 未检查文件扩展名和MIME类型 | 🔴 高 |
| 无大小限制 | 未限制上传文件大小 | 🟠 中 |
| 无病毒扫描 | 上传文件未经过安全检测 | 🔴 高 |
| 存储路径固定 | 可能存在路径遍历风险 | 🟠 中 |

### 💡 文件上传安全建议

```java
// 安全文件上传示例
@Service
public class FileUploadService {
    
    // 允许的文件类型
    private static final Set<String> ALLOWED_EXTENSIONS = 
        Set.of("jpg", "jpeg", "png", "gif", "pdf");
    
    // 最大文件大小：10MB
    private static final long MAX_FILE_SIZE = 10 * 1024 * 1024;
    
    public String uploadFile(MultipartFile file) {
        // 1. 校验文件是否为空
        if (file.isEmpty()) {
            throw new CustomException("上传文件不能为空");
        }
        
        // 2. 校验文件大小
        if (file.getSize() > MAX_FILE_SIZE) {
            throw new CustomException("文件大小不能超过10MB");
        }
        
        // 3. 校验文件类型
        String originalFilename = file.getOriginalFilename();
        String extension = getExtension(originalFilename).toLowerCase();
        if (!ALLOWED_EXTENSIONS.contains(extension)) {
            throw new CustomException("不支持的文件类型");
        }
        
        // 4. 生成安全的新文件名
        String newFilename = UUID.randomUUID().toString() + "." + extension;
        
        // 5. 安全存储路径（使用日期分目录）
        String datePath = LocalDate.now().format(DateTimeFormatter.BASIC_ISO_DATE);
        String savePath = uploadDir + "/" + datePath + "/" + newFilename;
        
        // 6. 保存文件
        file.transferTo(new File(savePath));
        
        return savePath;
    }
    
    private String getExtension(String filename) {
        int lastIndexOf = filename.lastIndexOf(".");
        if (lastIndexOf == -1) {
            return "";
        }
        return filename.substring(lastIndexOf + 1);
    }
}
```

---

# 🔐 第四部分：数据传输加密现状

## 4.1 零基础概念：为什么要加密传输？

### 📦 生活化比喻：寄送机密文件

```
┌─────────────────────────────────────────────────────────────────┐
│                 为什么要加密传输数据？                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📬 普通邮寄（HTTP）：                                           │
│     把信放进信封 → 邮局运输 → 送达                               │
│     ❌ 任何人都能在运输途中拆开信封                               │
│     ❌ 快递员能看到信的内容                                       │
│     ❌ 可能被偷看、篡改                                           │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  🔐 挂号信邮寄（HTTPS）：                                        │
│     信放进保险箱 → 上锁 → 邮局运输 → 送达 → 用钥匙打开            │
│     ✅ 只有收发双方有钥匙                                         │
│     ✅ 运输途中无法打开                                           │
│     ✅ 能检测到是否被篡改                                         │
│                                                                 │
│  HTTPS = HTTP + TLS/SSL 加密层                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4.2 HTTPS使用情况

### 📊 配置分析

```yaml
# application-sit.yml 配置
# 大部分内部服务调用使用HTTP
spring:
  redis:
    host: 10.252.68.157
    port: 6379

# 外部第三方服务调用
call:
  hosts:
    # HTTPS服务
    lexus: {host: https://api.irisapp.cn/...}
    causacloud: {host: https://uat-health.insbrain.cn/...}
    vippay: {host: https://hmapp01.picchealth.com/PICC}
    
    # HTTP服务（开发/测试环境）
    ocr: {host: http://test.renhuantech.com:8041/...}
    oasi: {host: http://3test.oasisapp.cn/...}
```

### ✅ HTTPS使用建议

| 场景 | 建议 | 说明 |
|------|------|------|
| 面向用户 | ✅ 必须HTTPS | 浏览器到服务器 |
| 内部服务调用 | ⚠️  建议HTTPS | 微服务间通信 |
| 第三方接口 | ✅ 必须HTTPS | 敏感数据传输 |
| 开发测试 | ⚠️  可用HTTP | 但不要带入生产 |

---

## 4.3 SM4国密算法使用场景

### 🇨🇳 什么是国密算法？

```
┌─────────────────────────────────────────────────────────────────┐
│                      SM4国密算法介绍                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📜 SM4 = 商密4 = 中国国家密码管理局发布的分组密码标准            │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    国密算法家族                          │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │                                                         │    │
│  │   SM1  │ 对称加密  │ 硬件实现，不公开                    │    │
│  │   SM2  │ 非对称加密│ 椭圆曲线算法，类似RSA                │    │
│  │   SM3  │ 哈希算法  │ 类似SHA-256                         │    │
│  │   SM4  │ 对称加密  │ 类似AES，128位分组                  │    │
│  │   SM9  │ 身份认证  │ 标识密码算法                        │    │
│  │                                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  💡 为什么使用SM4？                                              │
│     • 政策要求：金融、政府等敏感行业必须使用国密                  │
│     • 自主可控：避免使用国外加密算法的风险                       │
│     • 合规要求：通过密码评测需要支持国密                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📄 SM4工具类代码解析

```java
// SM4Util.java
public class SM4Util {
    
    // 国密密钥（应为配置项，不应硬编码）
    private static String testKey = "1234567812345678";

    static {
        // 添加BouncyCastle加密提供者
        // BouncyCastle支持SM2、SM3、SM4等国密算法
        Security.addProvider(new BouncyCastleProvider());
    }

    /**
     * SM4加密
     * @param plainString 明文
     * @return 密文（Base64编码）
     */
    public static String sm4Encrypt(String plainString) {
        try {
            // 1. 指定加密算法：SM4
            String algorithm = "SM4";
            
            // 2. 创建密钥（16字节 = 128位）
            SecretKeySpec secretKeySpec = new SecretKeySpec(
                testKey.getBytes(StandardCharsets.UTF_8), 
                algorithm
            );
            
            // 3. 创建密码器（ECB模式 + PKCS5Padding填充）
            Cipher cipher = Cipher.getInstance(algorithm + "/ECB/PKCS5Padding");
            
            // 4. 初始化为加密模式
            cipher.init(Cipher.ENCRYPT_MODE, secretKeySpec);
            
            // 5. 执行加密
            byte[] cipherBytes = cipher.doFinal(plainString.getBytes(StandardCharsets.UTF_8));
            
            // 6. 返回Base64编码的密文
            return Base64.getEncoder().encodeToString(cipherBytes);
            
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    /**
     * SM4解密
     * @param cipherString 密文（Base64编码）
     * @return 明文
     */
    public static String sm4Decrypt(String cipherString) {
        try {
            // 解密过程与加密相反
            String algorithm = "SM4";
            SecretKeySpec secretKeySpec = new SecretKeySpec(
                testKey.getBytes(StandardCharsets.UTF_8), 
                algorithm
            );
            Cipher cipher = Cipher.getInstance(algorithm + "/ECB/PKCS5Padding");
            cipher.init(Cipher.DECRYPT_MODE, secretKeySpec);
            
            // Base64解码后执行解密
            byte[] cipherBytes = cipher.doFinal(Base64.getDecoder().decode(cipherString));
            return new String(cipherBytes);
            
        } catch (Exception e) {
            e.printStackTrace();
            return cipherString; // 失败返回原值
        }
    }
}
```

### 🔍 SM4使用场景分析

| 场景 | 代码位置 | 用途 |
|------|---------|------|
| 短信验证码 | MathUtil.java | 生成4位数字验证码 |
| 敏感字段 | VO类 | 配合@SensitiveEncrypt使用 |
| 数据传输 | 待确认 | 敏感数据加密传输 |

### ⚠️ SM4使用注意问题

| 问题 | 描述 | 风险等级 |
|------|------|---------|
| 密钥硬编码 | "1234567812345678"直接写在代码中 | 🔴 高 |
| ECB模式 | 电子密码本模式，相同明文产生相同密文 | 🟠 中 |
| 无IV向量 | 未使用CBC/CFB等更安全的模式 | 🟠 中 |

### 💡 SM4安全使用建议

```java
// 建议的SM4使用方式
@Configuration
public class SM4Config {
    
    // 从配置中心读取密钥
    @Value("${sm4.secret.key}")
    private String sm4Key;
    
    // 使用CBC模式（需要IV向量）
    public static String sm4EncryptCBC(String plainString, String key) {
        try {
            // 1. 生成随机IV
            byte[] iv = new byte[16];
            new SecureRandom().nextBytes(iv);
            
            // 2. 创建密钥和IV
            SecretKeySpec keySpec = new SecretKeySpec(key.getBytes(), "SM4");
            IvParameterSpec ivSpec = new IvParameterSpec(iv);
            
            // 3. 使用CBC模式
            Cipher cipher = Cipher.getInstance("SM4/CBC/PKCS5Padding");
            cipher.init(Cipher.ENCRYPT_MODE, keySpec, ivSpec);
            
            // 4. 加密
            byte[] cipherBytes = cipher.doFinal(plainString.getBytes());
            
            // 5. 拼接IV和密文（或使用特殊分隔符）
            byte[] combined = new byte[iv.length + cipherBytes.length];
            System.arraycopy(iv, 0, combined, 0, iv.length);
            System.arraycopy(cipherBytes, 0, combined, iv.length, cipherBytes.length);
            
            return Base64.getEncoder().encodeToString(combined);
        } catch (Exception e) {
            throw new RuntimeException("加密失败", e);
        }
    }
}
```

---

## 4.4 AES加密场景分析

### 📦 AES加密流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                       AES加密流程                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   明文: "13812345678"                                           │
│        │                                                       │
│        ▼                                                       │
│   ┌─────────────────┐                                          │
│   │  AES加密        │                                          │
│   │  key: PICChealth│                                          │
│   │  模式: ECB     │                                          │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   密文: "ojJz74k_Wb_HP-d37uopf81B9I0UPICC..."                  │
│        │                                                       │
│        ▼                                                       │
│   ┌─────────────────┐                                          │
│   │  Base64编码      │                                          │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   最终传输: "aW5wdXQxMjM0NTY3ODkwMA=="                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📄 小程序签名加密实现

```java
// AesUtil.java - 小程序签名相关
public class AesUtil {
    
    private final static String picc = "PICChealth";
    
    /**
     * AES加密（用于小程序签名）
     */
    public static String encryptAES(String content) {
        // 1. AES加密
        byte[] encryptResult = encrypt(content);
        
        // 2. 转换为十六进制字符串
        String encryptResultStr = parseByte2HexStr(encryptResult);
        
        // 3. Base64编码
        encryptResultStr = ebotongEncrypto(encryptResultStr);
        
        return encryptResultStr;
    }
    
    /**
     * AES解密
     */
    public static String decrypt(String encryptResultStr) {
        // 1. Base64解码
        String decrpt = ebotongDecrypto(encryptResultStr);
        
        // 2. 十六进制转字节数组
        byte[] decryptFrom = parseHexStr2Byte(decrpt);
        
        // 3. AES解密
        byte[] decryptResult = decrypt(decryptFrom);
        
        return new String(decryptResult);
    }
    
    /**
     * AES加密核心实现
     */
    private static byte[] encrypt(String content) {
        try {
            KeyGenerator kgen = KeyGenerator.getInstance("AES");
            
            // 使用SHA1PRNG生成安全随机数
            SecureRandom secureRandom = SecureRandom.getInstance("SHA1PRNG");
            secureRandom.setSeed(picc.getBytes());
            kgen.init(128, secureRandom);
            
            SecretKey secretKey = kgen.generateKey();
            byte[] enCodeFormat = secretKey.getEncoded();
            SecretKeySpec key = new SecretKeySpec(enCodeFormat, "AES");
            
            Cipher cipher = Cipher.getInstance("AES");
            cipher.init(Cipher.ENCRYPT_MODE, key);
            
            return cipher.doFinal(content.getBytes(StandardCharsets.UTF_8));
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
}
```

### ⚠️ AES使用安全问题

| 问题 | 描述 | 风险等级 | 建议 |
|------|------|---------|------|
| 密钥硬编码 | "PICChealth"写在代码中 | 🔴 高 | 移到配置中心 |
| ECB模式 | 相同块产生相同密文 | 🟠 中 | 使用CBC模式 |
| SHA1PRNG | 密钥依赖种子值 | 🟠 中 | 使用SecureRandom |
| 密钥重复 | 不同地方可能使用不同密钥 | 🟡 低 | 统一密钥管理 |

---

## 4.5 其他加密相关

### 📄 密码加密（MD5）

```java
// EncryptionUtil.java - 密码加密
public class EncryptionUtil {
    
    /**
     * MD5加密
     * ⚠️ 注意：MD5已不安全，仅用于演示
     */
    public static String encodeMD5(String inStr) {
        MessageDigest md5 = null;
        try {
            md5 = MessageDigest.getInstance("MD5");
            byte[] byteArray = inStr.getBytes(StandardCharsets.UTF_8);
            byte[] md5Bytes = md5.digest(byteArray);
            
            StringBuffer hexValue = new StringBuffer();
            for (byte md5Byte : md5Bytes) {
                int val = ((int) md5Byte) & 0xff;
                if (val < 16) {
                    hexValue.append("0");
                }
                hexValue.append(Integer.toHexString(val));
            }
            return hexValue.toString().toUpperCase();
        } catch (Exception e) {
            return null;
        }
    }
    
    /**
     * SHA-256加密
     */
    public static String getClientHash(String str) {
        String rawData = str + "PICC";  // 加盐
        byte[] hashData = getMessageDigest("SHA-256", rawData.getBytes());
        return binaryToHexString(hashData);
    }
}
```

### ⚠️ 密码加密问题

| 问题 | 描述 | 建议 |
|------|------|------|
| MD5不安全 | MD5已被破解，可被彩虹表攻击 | 使用BCrypt |
| 无盐值 | 相同密码产生相同哈希 | 使用随机盐 |
| 简单哈希 | 未使用多次迭代 | 使用PBKDF2/BCrypt |

### 💡 推荐：使用BCrypt

```java
// Spring Security的BCryptPasswordEncoder
@Configuration
public class PasswordConfig {
    
    @Bean
    public PasswordEncoder passwordEncoder() {
        // 强度因子12，自动随机盐
        return new BCryptPasswordEncoder(12);
    }
}

// 使用
@Service
public class UserService {
    
    @Autowired
    private PasswordEncoder passwordEncoder;
    
    // 注册时加密密码
    public void register(User user) {
        user.setPassword(passwordEncoder.encode(user.getPassword()));
    }
    
    // 登录时验证
    public boolean login(String rawPassword, String encodedPassword) {
        return passwordEncoder.matches(rawPassword, encodedPassword);
    }
}
```

---

# 📚 第五部分：安全知识学习要点

## 5.1 从本项目学到的企业级安全实践

### 🏢 企业安全建设框架

```
┌─────────────────────────────────────────────────────────────────┐
│                    企业级安全建设体系                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                      身份与访问管理                       │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │   │
│   │  │ 认证机制  │  │ 授权机制  │  │ 会话管理  │               │   │
│   │  │ Token   │  │ RBAC    │  │ Redis   │               │   │
│   │  └──────────┘  └──────────┘  └──────────┘               │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                      数据安全                             │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │   │
│   │  │ 数据脱敏  │  │ 传输加密  │  │ 存储加密  │               │   │
│   │  │ @Sensit │  │ SM4/AES  │  │ 数据库   │               │   │
│   │  └──────────┘  └──────────┘  └──────────┘               │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                      应用安全                             │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │   │
│   │  │ 输入校验  │  │ SQL防护  │  │ XSS防护  │               │   │
│   │  │ @Valid  │  │ MyBatis  │  │ HTML转义 │               │   │
│   │  └──────────┘  └──────────┘  └──────────┘               │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### ✅ 项目中做得好的方面

| 方面 | 做法 | 评价 |
|------|------|------|
| Token机制 | Redis存储+自动续期 | ✅ 成熟方案 |
| 接口权限 | URL级别权限控制 | ✅ 基本完善 |
| 数据脱敏 | 注解+序列化器 | ✅ 设计良好 |
| 加密算法 | SM4国密+AES | ✅ 符合规范 |
| 配置分离 | Apollo配置中心 | ✅ 敏感配置外置 |

### ⚠️ 需要改进的方面

| 方面 | 问题 | 学习思考 |
|------|------|---------|
| 权限框架 | 自定义Interceptor | 建议使用Spring Security |
| Token开关 | 可关闭校验 | 生产必须强制开启 |
| 密钥管理 | 硬编码密钥 | 使用配置中心+KMS |
| XSS防护 | 无过滤机制 | 添加全局过滤器 |
| CSRF防护 | 无Token验证 | 添加CSRF Token |
| API限流 | 无频率限制 | 添加RateLimiter |

---

## 5.2 常见安全漏洞模式识别

### 🔍 OWASP Top 10 漏洞对照

| 排名 | 漏洞类型 | 本项目是否存在 | 检测方法 |
|------|---------|--------------|---------|
| 1 | 注入(SQL/命令) | ⚠️  低风险（MyBatis参数化） | 代码审计 |
| 2 | 认证失效 | ⚠️  可关闭Token校验 | 配置检查 |
| 3 | 敏感信息泄露 | ⚠️  部分VO已脱敏 | 全面扫描 |
| 4 | XML外部实体(XXE) | ⚠️  需确认 | 代码审计 |
| 5 | 访问控制失效 | ⚠️  URL级别控制 | 权限测试 |
| 6 | 安全配置错误 | ⚠️  可能存在 | 配置审计 |
| 7 | XSS跨站脚本 | ⚠️  无防护 | 渗透测试 |
| 8 | 不安全反序列化 | ⚠️  需确认 | 代码审计 |
| 9 | 使用有漏洞组件 | ⚠️  需检查 | 依赖扫描 |
| 10 | 日志不足 | ⚠️  缺少审计 | 日志审查 |

### 📋 漏洞识别清单

```markdown
## SQL注入识别
- [ ] 是否使用 ${} 直接拼接SQL
- [ ] 是否有ORM框架的预编译
- [ ] 是否有WAF防护

## XSS识别
- [ ] 是否对用户输入进行HTML转义
- [ ] 是否设置Content-Security-Policy
- [ ] 是否使用模板引擎的自动转义

## CSRF识别
- [ ] 是否有CSRF Token
- [ ] 是否验证Referer/Origin
- [ ] 是否使用SameSite Cookie

## 敏感信息泄露识别
- [ ] 是否使用HTTPS
- [ ] 敏感数据是否加密存储
- [ ] API响应是否脱敏
- [ ] 日志是否打印敏感信息

## 认证失效识别
- [ ] Token是否可以预测
- [ ] Token是否可以无限使用
- [ ] 是否有强密码策略
- [ ] 是否有账号锁定机制
```

---

## 5.3 零基础安全意识培养

### 📚 安全学习路径

```
┌─────────────────────────────────────────────────────────────────┐
│                    安全知识学习路径                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   第一阶段：基础概念（1-2周）                                     │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  📖 了解常见安全术语                                      │   │
│   │  📖 理解HTTP/HTTPS原理                                    │   │
│   │  📖 认识常见攻击类型（SQL注入、XSS、CSRF）                 │   │
│   │  📖 学习密码学基础（对称/非对称加密、哈希）                 │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│   第二阶段：实践体验（2-4周）                                     │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  🔧 使用Burp Suite抓包分析                                │   │
│   │  🔧 在靶场环境练习常见漏洞利用                             │   │
│   │  🔧 审计开源项目安全代码                                   │   │
│   │  🔧 使用安全扫描工具（OWASP ZAP等）                       │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│   第三阶段：深度提升（持续）                                      │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  📚 学习安全框架（Spring Security、Shiro）                 │   │
│   │  📚 了解合规要求（等保、GDPR、PCI-DSS）                    │   │
│   │  📚 关注安全漏洞公告（CVE、CNVD）                         │   │
│   │  📚 参与安全社区讨论                                       │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📖 安全术语速查表

| 术语 | 英文 | 解释 | 类比 |
|------|------|------|------|
| 认证 | Authentication | 验证用户身份 | 出示身份证 |
| 授权 | Authorization | 验证用户权限 | 检查门禁卡 |
| 加密 | Encryption | 将明文转为密文 | 给信加锁 |
| 解密 | Decryption | 将密文转为明文 | 给信开锁 |
| 哈希 | Hash | 单向不可逆转换 | 指纹识别 |
| 签名 | Signature | 验证信息来源和完整性 | 手写签名 |
| Token | Token | 身份凭证 | 游乐场通行证 |
| Salt | Salt | 随机添加的字符串 | 密码的调料 |

### 🛡️ 日常安全实践清单

```markdown
## 开发人员安全检查清单

### 代码层面
- [ ] 用户输入是否做了校验？
- [ ] SQL是否使用了参数化查询？
- [ ] 输出是否做了转义？
- [ ] 敏感信息是否加密存储？
- [ ] API是否做了权限校验？
- [ ] 异常信息是否泄露敏感数据？

### 配置层面
- [ ] 生产环境是否关闭调试模式？
- [ ] 敏感配置是否外置？
- [ ] 是否使用了HTTPS？
- [ ] 密钥是否安全存储？
- [ ] 日志是否包含敏感信息？

### 测试层面
- [ ] 是否进行了安全测试？
- [ ] 是否使用了自动化扫描工具？
- [ ] 是否进行了代码审计？
- [ ] 第三方依赖是否检查漏洞？
```

---

## 5.4 安全加固建议汇总

### 🚀 快速加固路线图

```
┌─────────────────────────────────────────────────────────────────┐
│                    安全加固优先级建议                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔴 P0 - 立即修复（紧急）                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. 移除所有硬编码密钥                                     │   │
│  │ 2. 生产环境强制开启Token校验                              │   │
│  │ 3. 启用HTTPS                                              │   │
│  │ 4. 添加CSRF Token验证                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  🟠 P1 - 近期修复（高优先级）                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. 添加XSS过滤机制                                        │   │
│  │ 2. 完善数据脱敏覆盖                                       │   │
│  │ 3. 替换MD5为BCrypt                                       │   │
│  │ 4. 添加API限流机制                                        │   │
│  │ 5. 优化SM4/AES实现（使用CBC+IV）                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  🟡 P2 - 计划修复（中优先级）                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. 引入Spring Security框架                               │   │
│  │ 2. 添加统一异常处理                                       │   │
│  │ 3. 完善日志审计                                          │   │
│  │ 4. 添加安全监控告警                                       │   │
│  │ 5. 定期安全培训和代码审计                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📋 分步骤实施方案

#### 第一步：密钥管理（1天）

```yaml
# 配置中心统一管理密钥
# application-prod.yml
security:
  sm4:
    key: ${SM4_SECRET_KEY}  # 从环境变量读取
  aes:
    key: ${AES_SECRET_KEY}
  jwt:
    secret: ${JWT_SECRET_KEY}
```

#### 第二步：Token校验加固（1天）

```java
// 移除tokenInterceptFlag，生产强制开启
@Value("${token.intercept.mode:force}")  // force | optional
private String tokenInterceptMode;

public boolean preHandle(...) {
    // 生产环境force模式，无视其他配置
    if ("force".equals(tokenInterceptMode)) {
        validateToken(token);
        return true;
    }
    // 其他逻辑...
}
```

#### 第三步：XSS防护（2天）

```java
// 添加XSS过滤器
@Component
@Order(1)
public class XssFilter extends OncePerRequestFilter {
    
    @Override
    protected void doFilterInternal(HttpServletRequest request, 
            HttpServletResponse response, FilterChain chain) {
        chain.doFilter(new XssRequestWrapper(request), response);
    }
}

// 统一异常处理
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(Exception.class)
    public Result handleException(Exception e) {
        // 不返回具体错误信息给前端
        log.error("系统异常", e);
        return Result.error("系统异常，请联系管理员");
    }
}
```

#### 第四步：数据脱敏完善（3天）

```java
// 完善脱敏注解
@SensitiveEncrypt
private String idcard;  // 身份证

@SensitiveMask(type = MaskType.PHONE)
private String tel;  // 手机号：138****5678

@SensitiveMask(type = MaskType.NAME)
private String name;  // 姓名：张*

@SensitiveMask(type = MaskType.BANK_CARD)
private String bankcard;  // 银行卡：****1234
```

#### 第五步：引入安全框架（1周）

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
<dependency>
    <groupId>com.github.thestyleofme</groupId>
    <artifactId>security-starter</artifactId>
</dependency>
```

---

## 附录：学习资源推荐

### 📚 推荐书籍

| 书籍名称 | 难度 | 适合人群 |
|---------|------|---------|
| 《Web应用安全权威指南》 | ⭐⭐ | 入门 |
| 《白帽子讲Web安全》 | ⭐⭐⭐ | 进阶 |
| 《代码整洁之道》 | ⭐⭐ | 代码质量 |
| 《深入理解计算机系统》 | ⭐⭐⭐⭐ | 底层原理 |

### 🔧 推荐工具

| 工具 | 用途 | 难度 |
|------|------|------|
| Burp Suite | Web渗透测试 | ⭐⭐⭐ |
| OWASP ZAP | 安全扫描 | ⭐⭐ |
| SonarQube | 代码安全扫描 | ⭐⭐ |
| Nmap | 端口扫描 | ⭐⭐ |

### 🌐 推荐网站

| 网站 | 用途 |
|------|------|
| OWASP | Web安全标准 |
| FreeBuf | 安全资讯 |
| 先知社区 | 技术分享 |
| NVD | 漏洞数据库 |

---

> 📝 **文档说明**
> 
> 本文档通过对 PICC 门诊慢特病业务管理系统源码的安全审计，分析了项目在接口认证、数据脱敏、输入校验、传输加密等方面的现状。文档采用通俗易懂的语言和丰富的图表，帮助学习者理解企业级安全实践。
> 
> ⚠️ **免责声明**：本文档仅供学习研究使用，不涉及任何实际系统的攻击或漏洞利用。
