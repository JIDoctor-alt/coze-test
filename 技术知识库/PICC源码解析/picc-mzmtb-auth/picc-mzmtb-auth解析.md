# picc-mzmtb-auth 认证服务模块解析

> 📌 **一句话概括**：认证服务是整个系统的"门卫"，负责验证用户身份、发放通行证、管理登录状态。

---

## 项目结构概览

```
picc-mzmtb-auth/
├── picchealth-authentication-server/    # 核心服务（API接口、业务逻辑、工具类）
├── picchealth-authentication-db/        # 数据库层（实体类、数据访问层）
└── picchealth-authentication-starter/   # 启动配置
```

---

## 核心模块解析

### 一、启动入口

#### AuthenticationSpringBootApplication.java
> 🎯 Spring Boot应用启动类

### 这是啥？（小白版）
就像你家的"总开关"，按下开关，家里所有电器就开始工作了。这个类启动后，整个认证服务就开始运行了。

### 核心代码解析
```java
@SpringBootApplication(...)  // 声明这是一个Spring Boot应用
@EnableDiscoveryClient       // 允许服务被发现（微服务注册）
@EnableApolloConfig          // 集成Apollo配置中心
@EnableScheduling            // 开启定时任务
public static void main(String[] args) {
    // 启动应用
}
```

### 知识点
- **Spring Boot**：Java项目快速开发框架
- **Apollo**：配置中心，动态管理配置
- **@EnableScheduling**：支持定时任务（如清理过期数据）

---

### 二、登录API（用户入口）

#### LoginApi.java
> 🎯 登录接口控制器，处理所有登录相关请求

### 这是啥？（小白版）
就像酒店的"前台接待处"，你来住宿（使用系统），首先要到前台登记验证身份。前台会根据你的情况告诉你能不能住、给你房卡。

### 核心代码解析

| 方法 | 大白话解释 |
|------|----------|
| `logOut()` | 退房 - 注销当前登录 |
| `update()` | 修改密码 - 换个新密码 |
| `getUser()` | 出示房卡 - 用Token获取用户信息 |
| `resetting()` | 忘记密码重置 - 申诉重置 |
| `register()` | 拼图验证注册 - 生成滑动验证码图片 |
| `check()` | 验证并登录 - 检查拼图+验证码后发放Token |

### 登录流程（重点！）
```
1. 用户输入账号密码/手机号验证码
2. 系统检查敏感词（不能叫admin、root等）
3. 验证账号是否存在、是否被禁用
4. 校验验证码（手机短信验证码）
5. 检查用户权限角色
6. 生成Token（通行证）
7. 返回用户信息和菜单权限
```

### 知识点
- **API接口**：对外提供服务的入口
- **Swagger注解**：自动生成接口文档
- **敏感词过滤**：防止用户注册危险账号名

---

### 三、验证码生成

#### CaptchaUtil.java
> 🎯 滑动拼图验证码生成工具

### 这是啥？（小白版）
就像网站登录时的"滑动验证"，你需要在图片上滑动拼图到正确位置。这是用代码"画"出来的验证码。

### 核心代码解析

| 方法 | 大白话解释 |
|------|----------|
| `createCaptcha()` | 画验证码 - 从背景图切出拼图块 |
| `createSmallShape()` | 画形状 - 拼图块的凸起和凹槽 |
| `dealLightAndShadow()` | 加特效 - 给拼图加高光和阴影 |

### 生成过程（图片处理）
1. 读取背景图
2. 随机确定拼图位置
3. 切出带形状的小图
4. 给小图加阴影效果
5. 在大图上"挖"出凹槽
6. 转为Base64格式返回

### 知识点
- **BufferedImage**：Java图片处理
- **Graphics2D**：画图工具
- **Base64**：图片转字符串传输

---

#### TokenUtil.java
> 🎯 生成随机Token

### 这是啥？（小白版）
就像给你发一张"会员卡号"，这个号码是随机生成的，用来标识你这次登录。

### 核心代码解析
```java
// 生成过程：随机数1 + 随机数2 → MD5加密 → 拼接
String md5Str1 = Md5Util.md5(rnd1 + "");
String md5Str2 = Md5Util.md5(rnd2 + "");
return md5Str1 + md5Str2.substring(0, 2);  // 30位随机字符串
```

---

### 四、用户服务

#### UserInfoServiceImpl.java
> 🎯 用户登录核心业务逻辑

### 这是啥？（小白版）
这是整个登录流程的"大脑"，指挥各个环节配合工作，最终决定让不让你登录。

### 核心代码解析

**登录方法 `login()` 的完整流程：**
```
1️⃣ 检查账号是否被锁定
   ↓
2️⃣ 查询用户信息
   ↓
3️⃣ 验证账号是否被禁用
   ↓
4️⃣ 验证密码是否正确
   ↓
5️⃣ 检查用户是否有权限（角色检查）
   ↓
6️⃣ 保存机构用户关联
   ↓
7️⃣ 生成Token（双重SM4加密）
   ↓
8️⃣ 存储到Redis（120分钟有效期）
   ↓
9️⃣ 查询用户菜单权限
   ↓
🔟 返回登录成功信息和Token
```

**Token生成细节：**
```java
// 用户ID + 随机字符串 → SM4加密 → 再加密
String randomStr = UUID.randomUUID().toString();
String enUserId = SM4Util.sm4Encrypt(用户ID + randomStr);
String token = SM4Util.sm4Encrypt(enUserId + tokenKey);
```

**登录锁定机制：**
- 密码错误5次 → 锁定30分钟
- 锁定后每次错误增加30分钟
- 最大锁定时间：24小时

### 知识点
- **Redis**：内存数据库，存储登录状态
- **Token**：登录凭证，有时效性
- **SM4加密**：国密算法，安全性高
- **线程变量**：保存当前登录用户信息

---

#### VipSecurityCodeServiceImpl.java
> 🎯 短信验证码服务

### 这是啥？（小白版）
就像银行发给你的"动态密码"，手机号验证码登录时，系统会给你手机发一条短信，里面有6位数字验证码。

### 核心代码解析

| 方法 | 大白话解释 |
|------|----------|
| `sendVerificationCode()` | 发验证码 - 发送短信 |
| `verifyCode()` | 验验证码 - 核对用户输入 |
| `checkCode()` | 核心比对 - 数据库查询验证 |
| `sendCode()` | 发短信 - 调用短信网关 |

**验证码发送限制：**
- 每设备每小时 ≤ 20条
- 每设备每天 ≤ 100条
- 有效期：10分钟
- 校验错误5次 → 5分钟内禁止

### 知识点
- **OTP**：一次性密码（One-Time Password）
- **Redis计数**：限制发送频率
- **SM4加密**：验证码也加密存储

---

### 五、菜单权限

#### MenuInfoServiceImpl.java
> 🎯 菜单查询服务

### 这是啥？（小白版）
登录成功后，系统会返回你能看到哪些菜单。就像酒店给你房卡后，你只能进入你房间和公共区域，其他房间进不去。

### 核心代码解析
```java
// 查询用户可用的菜单树
List<PrivilegeMenuInfoDto> getMenuOrgTree(dto);
```

---

### 六、加密工具

#### SM4Util.java
> 🎯 国密SM4加密解密

### 这是啥？（小白版）
就像给你的秘密文件上锁，只有用正确的钥匙（密钥）才能打开。这是中国国家标准的加密算法。

### 核心代码解析
```java
sm4Encrypt(明文)  → 加密  → 密文
sm4Decrypt(密文)  → 解密  → 明文
```

**为什么用SM4？**
- 国家标准算法，安全可靠
- 比普通加密更安全
- 用于Token、密码等敏感数据

---

#### EncryptionUtil.java
> 🎯 通用加密工具

### 这是啥？（小白版）
提供各种"打码"方式，把普通文字变成乱码，保护信息安全。

### 核心代码解析

| 方法 | 大白话解释 |
|------|----------|
| `encodeMD5()` | MD5单向加密（不可逆） |
| `getPassword()` | SHA-256加密密码 |

### 知识点
- **MD5**：信息摘要，不可逆，常用于密码
- **SHA-256**：更安全的哈希算法

---

### 七、Redis配置

#### RedisKeyConf.java
> 🎯 Redis缓存的"柜子编号"

### 这是啥？（小白版）
Redis就像一个有很多格子的储物柜，每个格子存不同的东西。这个文件告诉系统每个格子放什么。

### 核心代码解析
```java
public static String API_TOKEN = "token:";      // Token存放
public static String API_USERKEY = "userkey:";  // 用户信息存放
public static String PERMISSIONS = "permissions:"; // 权限存放
public static Long PERMISSIONS_TIME = 30*60L;   // 30分钟过期
```

---

#### RedisUtil.java
> 🎯 Redis操作工具（在common模块）

### 这是啥？（小白版）
操作Redis的"遥控器"，可以往储物柜里放东西、取东西、设置过期时间。

### 核心代码解析
```java
redisUtil.set(key, value)      // 存东西
redisUtil.get(key)             // 取东西
redisUtil.exists(key)         // 检查是否存在
redisUtil.remove(key)         // 删除
redisUtil.set(key, value, 30*60L)  // 带过期时间存
```

---

### 八、用户信息存储

#### UserUtils.java
> 🎯 当前用户信息存储

### 这是啥？（小白版）
就像"黑板"，记录当前正在操作的用户是谁，方便任何地方查看。

### 核心代码解析
```java
ThreadLocal<User> threadLocal = new ThreadLocal<>();

// 存
UserUtils.setUser(user);

// 取
UserUtils.getUser();

// 清理（登出时）
UserUtils.remove();
```

### 知识点
- **ThreadLocal**：线程本地变量，每个线程独立
- **用户上下文**：在请求生命周期内保存用户信息

---

### 九、发送短信

#### SendVerificationCodeUtil.java
> 🎯 短信发送工具

### 这是啥？（小白版）
调用第三方短信平台API，发送验证码到用户手机。

### 核心代码解析
```java
sendSMS(手机号, 短信内容, 模板参数);
```

---

## 数据库实体层（PO）

### PrivilegeUserInfo.java
> 🎯 用户信息表

### 这是啥？（小白版）
系统的"花名册"，记录每个用户的详细信息。

### 字段说明
| 字段 | 含义 |
|------|------|
| account | 登录账号 |
| name | 姓名 |
| password | 密码 |
| tel | 手机号 |
| email | 邮箱 |
| enable | 是否启用（1启用，0禁用） |
| is_admin | 是否管理员 |
| org_id | 所属机构ID |
| password_changed | 密码最后修改时间 |
| end_login | 最后登录时间 |

---

### PrivilegeMenuInfo.java
> 🎯 菜单信息表

### 这是啥？（小白版）
系统的"导航地图"，告诉系统有哪些功能页面。

### 字段说明
| 字段 | 含义 |
|------|------|
| name | 菜单名称 |
| parent_id | 上级菜单ID |
| url | 页面地址 |
| icon | 图标 |
| sort | 排序 |

---

### PrivilegeRoleInfo.java
> 🎯 角色表

### 这是啥？（小白版）
"岗位说明书"，比如"医生"、"护士"、"管理员"，每个岗位有不同的权限。

---

### PrivilegeUserRoleInfo.java
> 🎯 用户角色关联表

### 这是啥？（小白版）
"人员分配表"，谁是什么岗位。

---

### PrivilegeRoleResource.java
> 🎯 角色资源关联表

### 这是啥？（小白版）
"权限清单"，每个岗位能访问哪些资源。

---

## 常量与枚举

### CaptchaConstant.java
> 🎯 验证码常量

### 这是啥？（小白版）
验证码相关的"默认值设置"。

```java
X = "coordinates:"           // 拼图坐标Redis key前缀
SLICE_DIFF_LIMIT = 5         // 允许的滑动误差
```

---

### CaptchaEnum.java
> 🎯 验证码状态枚举

### 这是啥？（小白版）
验证码各种状态的"标准答案"。

---

### ReturnStatusEnum.java
> 🎯 返回状态枚举

### 这是啥？（小白版）
接口返回结果的"状态码字典"。

---

## VO（视图对象）

### LoginVo.java
> 🎯 登录请求参数

### 这是啥？（小白版）
用户登录时填写的"表单"。

```java
userAccount      // 账号
passWord         // 密码
loginType        // 登录方式
loginMeans       // 登录手段（1密码，2验证码）
receiver         // 手机号
verificationCode // 验证码
```

---

### LoginSuccVo.java
> 🎯 登录成功返回

### 这是啥？（小白版）
登录成功后返回给用户的"欢迎礼包"。

```java
token            // 通行证（最重要）
userName         // 用户名
menus            // 能访问的菜单
orgId/orgCode    // 机构信息
```

---

## 配置类

### MvcInterceptorConfig.java
> 🎯 MVC拦截器配置

### 这是啥？（小白版）
配置哪些请求需要"安检"，比如登录验证。

---

### LogAudit.java
> 🎯 日志审计注解

### 这是啥？（小白版）
记录谁在什么时候做了什么操作。

---

## 工具类汇总

| 文件 | 用途 |
|------|------|
| MailSender | 发送邮件 |
| MathUtil | 数学计算（生成验证码） |
| HttpForwardUtil | HTTP请求转发 |
| UniqueIDGenerator | 生成唯一ID |

---

## 总结

### 认证服务核心流程
```
用户登录 → 验证账号密码 → 验证权限 → 生成Token → 返回菜单
    ↓
后续请求带着Token → 验证Token → 执行业务 → 返回结果
    ↓
登出 → 清除Token → 结束会话
```

### 安全措施
1. **登录锁定**：密码错误5次锁定30分钟
2. **敏感词过滤**：禁止危险账号名
3. **验证码校验**：防机器人登录
4. **Token机制**：无状态认证
5. **SM4加密**：数据传输加密
6. **短信验证码**：手机号登录验证
