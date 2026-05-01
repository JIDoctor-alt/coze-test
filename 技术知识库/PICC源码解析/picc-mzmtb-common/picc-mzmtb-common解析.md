# picc-mzmtb-common 公共模块解析

> 📌 **一句话概括**：公共模块是整个系统的"工具箱"，提供所有服务都需要的通用功能，如数据库操作、Redis缓存、加密工具、外部接口调用等。

---

## 项目结构概览

```
picc-mzmtb-common/
├── common-core/     # 核心基础（实体、服务基类、配置）
├── common-call/     # 外部服务调用（HTTP/WebService）
└── common-utils/    # 工具类集合（加密、文件、日期等）
```

---

## 一、common-core 核心基础模块

### 1.1 基础实体（BaseEntity）

#### BaseEntity.java
> 🎯 所有数据库实体类的"老祖宗"

### 这是啥？（小白版）
就像所有的"表格"都有一个共同的表头（编号、创建时间、修改时间），这个类是所有数据表的"公共表头"。

### 核心代码解析
```java
public class BaseEntity implements Serializable {
    @Id
    public String id;              // 主键ID
    
    @Column
    private LocalDateTime createtime;  // 创建时间
    
    @Column
    private String creator;         // 创建人
    
    @Column
    private LocalDateTime modifytime;  // 修改时间
    
    @Column
    private String modifier;        // 修改人
}
```

### 知识点
- **@Id**：主键标识
- **@Column**：数据库字段映射
- **Serializable**：序列化，用于网络传输和缓存

---

### 1.2 基础服务（BaseService）

#### BaseServiceImpl.java
> 🎯 所有业务服务的"祖宗类"

### 这是啥？（小白版）
就像所有的"服务员"都需要会的基本功（登记、查询、删除），这个类定义了所有服务都要有的基本操作。

### 核心代码解析

| 方法 | 大白话解释 |
|------|----------|
| `save()` | 保存或更新 - 插入新数据或修改旧数据 |
| `selectOne()` | 查询一条 - 根据条件找一条 |
| `selectAll()` | 查询所有 - 符合条件都找出来 |
| `getById()` | 按ID查询 - 根据编号找记录 |
| `deleteById()` | 按ID删除 - 删除单条 |
| `selectPage()` | 分页查询 - 返回一页数据 |
| `createPrimaryKey()` | 生成ID - 调用雪花算法 |

### 保存逻辑（重点！）
```java
public T save(T entity) {
    LocalDateTime now = LocalDateTime.now();
    
    if (StringUtils.isNotBlank(entity.getId())) {
        // 有ID = 更新
        entity.setModifytime(now);
        mapper.updateByPrimaryKeySelective(entity);
    } else {
        // 无ID = 新增
        entity.setModifytime(now);
        entity.setCreatetime(now);
        entity.setId(createPrimaryKey());  // 生成雪花ID
        mapper.insertSelective(entity);
    }
    return entity;
}
```

### 知识点
- **泛型T**：通用类型，什么实体都能操作
- **MyBatis**：数据库操作框架
- **雪花算法**：分布式ID生成器

---

#### BaseServiceDrImpl.java
> 🎯 支持逻辑删除的服务基类

### 这是啥？（小白版）
在"删除"时不是真的删除，而是在记录上打个"已删除"标记，方便以后查账。

---

### 1.3 数据库配置

#### MyMapper.java
> 🎯 数据库操作的"通用工具箱"

### 这是啥？（小白版）
定义了所有数据库操作的基本能力，增删改查都从这里继承。

### 知识点
- **TkMyBatis**：简化MyBatis操作的工具
- **批量插入**：支持一次性插入多条数据

---

#### BatisPlusConfig.java
> 🎯 MyBatis性能监控配置

### 这是啥？（小白版）
给数据库操作装上"计时器"，记录每个SQL执行了多久，方便排查慢SQL。

---

#### PerformanceInterceptor.java
> 🎯 SQL执行性能拦截器

### 这是啥？（小白版）
记录每个SQL语句执行花了多少毫秒，超过阈值就报警。

---

### 1.4 分页支持

#### PageVo.java
> 🎯 分页参数封装

### 这是啥？（小白版）
查询数据时告诉系统"我要第几页，每页几条"。

```java
pageNum=1     // 第1页
pageSize=10   // 每页10条
```

---

#### PageUtil.java
> 🎯 分页工具类

### 这是啥？（小白版）
把查询结果"切成片"，返回指定的那一片。

---

### 1.5 异常处理

#### CustomException.java
> 🎯 自定义业务异常

### 这是啥？（小白版）
程序运行出错时，告诉用户"哪里出问题了"。比如"余额不足"、"权限不足"等。

### 核心代码解析
```java
public class CustomException extends RuntimeException {
    public static CustomException createByMassage(Long errorCode, String message) {
        return new CustomException(errorCode, message, null, null, null);
    }
}
```

**使用示例：**
```java
throw CustomException.createByMassage(500L, "密码错误");
throw CustomException.createByMassage(401L, "您没有权限");
```

---

#### RuntimeExceptionAdvice.java
> 🎯 全局异常处理器

### 这是啥？（小白版）
系统的"客服中心"，所有程序报错都会汇总到这里，统一给用户返回友好的错误信息。

### 处理逻辑
1. 参数校验异常 → 提示参数错误
2. 业务异常 → 返回业务错误信息
3. 系统异常 → 记录日志，返回"系统繁忙"

---

### 1.6 Redis配置

#### RedisConfig.java
> 🎯 Redis缓存配置

### 这是啥？（小白版）
配置Redis怎么存储和读取数据，用JSON格式序列化。

### 核心代码解析
```java
template.setValueSerializer(serializer);  // JSON方式存储值
template.setKeySerializer(new StringRedisSerializer());  // key用字符串
```

---

#### RedisUtil.java
> 🎯 Redis操作工具（在common-utils）

### 这是啥？（小白版）
操作Redis缓存的"遥控器"。

### 核心代码解析

| 方法 | 大白话解释 |
|------|----------|
| `set(key, value)` | 存入缓存 |
| `get(key)` | 取出缓存 |
| `exists(key)` | 检查存在 |
| `remove(key)` | 删除缓存 |
| `set(key, value, 30*60L)` | 带过期时间存（秒） |
| `getExpire(key)` | 获取剩余时间 |

---

### 1.7 ID生成

#### PrimaryKeyUtil.java
> 🎯 分布式ID生成器

### 这是啥？（小白版）
在分布式系统中，每个服务都能生成唯一ID，不会重复。就像给每条记录发一个"身份证号"。

### 核心代码解析
```java
// 雪花算法ID = 时间戳 + 数据中心ID + 机器ID + 序列号
public String snowFlakeKeyStr() {
    String id = partition + snowFlake.nextId();
    // 处理超长ID（确保不超过19位）
    return id;
}
```

**ID组成：**
```
| 符号位 | 时间戳(41位) | 数据中心(5位) | 机器ID(5位) | 序列号(12位) |
1位        41位          5位            5位           12位
```

### 知识点
- **雪花算法**：Twitter开源的ID生成算法
- **趋势递增**：ID有序，对数据库索引友好

---

#### SnowFlake.java
> 🎯 雪花算法实现

### 这是啥？（小白版）
雪花算法的具体代码实现。

---

### 1.8 响应封装

#### ApiResponse.java
> 🎯 统一响应格式

### 这是啥？（小白版）
所有接口返回的数据都长一个样，方便前端处理。

### 核心代码解析
```java
@Data
public class ApiResponse<T> {
    public static final int SUCCESS = 0;   // 成功
    public static final int FAIL = -1;    // 失败
    public static final int BUSY = -100;   // 繁忙
    
    private long status;      // 状态码
    private String statusText; // 状态说明
    private T data;           // 数据
}
```

**返回格式：**
```json
{
    "status": 0,
    "statusText": "Success",
    "data": { ... }
}
```

---

#### Result.java
> 🎯 通用响应包装

### 这是啥？（小白版）
另一个版本的响应封装，用Result.success()和Result.fail()更方便。

---

### 1.9 枚举定义

#### StatusCode.java
> 🎯 HTTP状态码枚举

### 这是啥？（小白版）
标准的状态码定义，就像HTTP状态码一样。

```java
SUCCESS(200, "操作成功")
FAILURE(201, "操作失败")
UNAUTHORIZED(401, "无权限访问")
SERVER_ERROR(500, "服务器错误")
```

---

#### DelFlagEnum.java
> 🎯 删除标志枚举

### 这是啥？（小白版）
记录是"活着"还是"删除了"。

```java
YES(1, "已删除")
NO(0, "未删除")
```

---

#### YesOrNoEnum.java
> 🎯 是否枚举

### 这是啥？（小白版）
"是"或"否"的选择。

```java
YES("1", "是")
NO("0", "否")
```

---

### 1.10 参数解析

#### MyHandlerMethodArgumentResolver.java
> 🎯 自定义参数解析器

### 这是啥？（小白版）
让Controller方法可以直接接收JSON对象，自动转换。

```java
@PostMapping("/save")
public ApiResponse save(@MyRequestBody User user) {
    // user已经自动从JSON转成对象了
}
```

---

### 1.11 配置类

#### RestTemplateConfig.java
> 🎯 HTTP客户端配置

### 这是啥？（小白版）
配置发送HTTP请求的工具，可以调用其他服务。

---

#### SwaggerConfiguration.java
> 🎯 API文档配置

### 这是啥？（小白版）
自动生成接口文档，方便测试和对接。

---

---

## 二、common-call 外部服务调用模块

### 2.1 服务调用核心

#### BaseCallService.java
> 🎯 服务调用的抽象接口

### 这是啥？（小白版）
定义怎么调用外部服务（不同类型的调用方式）。

---

#### BaseCallServiceImpl.java
> 🎯 服务调用实现

### 这是啥？（小白版）
根据配置决定用哪种方式调用外部服务。

### 核心代码解析
```java
public LinkRuturnEntity callService(String serviceCode, JSON param) {
    // 1. 根据服务编码获取配置
    LinkCallConfig callConfig = callCache.getLinkCallConfig(serviceCode);
    
    // 2. 根据配置选择调用方式
    CallService call = getCallService(callConfig);
    
    // 3. 执行调用
    return call.callService(callConfig, param);
}
```

**调用方式选择：**
- AXIS → WebService调用
- REST → HTTP REST调用
- SOAP → 传统WebService

---

### 2.2 服务配置

#### LinkCallConfig.java
> 🎯 服务调用配置模型

### 这是啥？（小白版）
记录每个外部服务的"使用说明"：地址、调用方式、参数等。

### 字段说明
| 字段 | 含义 |
|------|------|
| servicecode | 服务编码 |
| requesttype | 调用方式（AXIS/REST/SOAP） |
| url | 服务地址 |
| methodname | 方法名 |
| namespace | 命名空间 |
| timeout | 超时时间 |

---

#### CallCacheUtils.java
> 🎯 调用配置缓存工具

### 这是啥？（小白版）
从缓存中获取服务配置，不用每次都查数据库。

---

### 2.3 HTTP调用

#### HttpClientUtil.java
> 🎯 HTTP请求工具

### 这是啥？（小白版）
发送HTTP请求的工具，可以带header、带参数。

### 核心代码解析
```java
// 带认证头的POST请求
String result = HttpClientUtil.doPostWithHeader(
    url,                    // 地址
    paramMap,               // 参数
    headerMap,              // 请求头(token等)
    methodName              // 方法名
);
```

---

#### RestCallUtils.java
> 🎯 REST调用工具

### 这是啥？（小白版）
用Spring的RestTemplate发送REST请求。

---

### 2.4 SOAP调用

#### SOAPUtil.java
> 🎯 SOAP协议调用工具

### 这是啥？（小白版）
发送SOAP协议（XML格式）的请求，老式WebService常用这种方式。

---

### 2.5 具体服务实现

#### WxCallServiceImpl.java
> 🎯 微信服务调用

#### WxxcxCallServiceImpl.java
> 🎯 微信小程序服务调用

#### JkdaCallServiceImpl.java
> 🎯 健康档案服务调用

#### OcrWqxCallServiceImpl.java
> 🎯 OCR识别服务调用（文鼎无忌）

### 这是啥？（小白版）
封装好的外部服务调用，用法统一：

```java
callService.callService("OCR_WQX", param);
```

---

---

## 三、common-utils 工具类模块

### 3.1 加密工具

#### MD5Util.java
> 🎯 MD5加密工具

### 这是啥？（小白版）
把任意字符串变成一串"乱码"，常用于密码存储。

```java
String hash = MD5Util.encodeMD5("123456");
// 结果：E10ADC3949BA59ABBE56E057F20F883E
```

**特点：**
- 不可逆（不能从结果反推原内容）
- 相同输入→相同输出
- 速度快

---

#### Sha256.java
> 🎯 SHA-256加密工具

### 这是啥？（小白版）
比MD5更安全的加密算法。

```java
String hash = Sha256.getSha256Str("密码");
```

---

#### AESUtil.java / AESCrypt.java
> 🎯 AES对称加密

### 这是啥？（小白版）
可以加密也能解密，需要密钥。

```java
String secret = AESCrypt.encrypt("原文", "密钥");
String plain = AESCrypt.decrypt(secret, "密钥");
```

---

### 3.2 字符串工具

#### StringUtils.java
> 🎯 字符串处理工具

### 这是啥？（小白版）
处理字符串的各种"小工具"。

### 核心代码解析

| 方法 | 大白话解释 |
|------|----------|
| `isEmpty()` | 判断是否为空 |
| `isNotBlank()` | 判断是否非空（排除空格） |
| `gb2312ToUtf8()` | 中文编码转换 |
| `UnicodeToString()` | Unicode转中文 |

---

### 3.3 日期工具

#### DateUtil.java
> 🎯 日期处理工具

### 这是啥？（小白版）
日期操作的"瑞士军刀"。

### 核心代码解析

| 方法 | 大白话解释 |
|------|----------|
| `dateTrans()` | 字符串转日期（自动识别格式） |
| `transDateEnd()` | 转成当天结束时间（23:59:59） |
| `transDateStart()` | 转成当天开始时间（00:00:00） |
| `addDateDay()` | 日期加减天数 |
| `addDateMonth()` | 日期加减月份 |

---

#### DateTimeUtils.java
> 🎯 日期时间工具

### 这是啥？（小白版）
更详细的日期时间处理。

---

#### TimeUtil.java
> 🎯 时间工具

### 这是啥？（小白版）
获取当前时间、格式化时间等。

---

### 3.4 文件工具

#### FileUtils.java
> 🎯 文件操作工具

### 这是啥？（小白版）
读写文件、上传下载文件。

### 核心代码解析

| 方法 | 大白话解释 |
|------|----------|
| `readFile()` | 读取文件内容 |
| `fileWriteStr()` | 写入文件 |
| `base64ToFile()` | Base64转文件 |
| `fileToBase64()` | 文件转Base64 |
| `getFileSize()` | 获取文件大小 |

---

#### Base64Util.java
> 🎯 Base64编解码

### 这是啥？（小白版）
把图片/文件转成字符串传输，或反过来。

---

### 3.5 JSON工具

#### JsonUtil.java
> 🎯 JSON处理工具

### 这是啥？（小白版）
JSON和Java对象互转。

```java
// 对象转JSON
String json = JsonUtil.toJsonString(user);

// JSON转对象
User user = JsonUtil.parseObject(json, User.class);
```

---

#### JacksonUtils.java
> 🎯 Jackson工具

### 这是啥？（小白版）
另一个JSON处理库，功能更强大。

---

### 3.6 唯一ID工具

#### UUIDUtil.java
> 🎯 UUID生成工具

### 这是啥？（小白版）
生成全球唯一的ID。

```java
String uuid = UUIDUtil.getUUID();
// 结果：550e8400-e29b-41d4-a716-446655440000
```

---

#### IdWorker.java
> 🎯 雪花算法实现

### 这是啥？（小白版）
分布式环境下生成不重复ID。

---

### 3.7 Redis工具

#### RedisKeyConf.java
> 🎯 Redis Key命名规范

### 这是啥？（小白版）
统一Redis的key命名，避免混乱。

```java
public static String API_TOKEN = "token:";
public static String USER_KEY = "user:";
```

---

#### RedisUtil.java
> 🎯 Redis操作封装

### 这是啥？（小白版）
更易用的Redis操作接口。

```java
redisUtil.set(key, value, 3600);  // 存1小时
redisUtil.get(key);              // 取
redisUtil.remove(key);          // 删
```

---

### 3.8 网络请求

#### HttpRequest.java
> 🎯 HTTP请求封装

### 这是啥？（小白版）
简化HTTP请求的发送。

```java
String result = HttpRequest.post(url)
    .header("token", "xxx")
    .body(json)
    .execute();
```

---

### 3.9 财务工具

#### FinanceUtils.java
> 🎯 财务计算工具

### 这是啥？（小白版）
计算等额本息、等额本金等贷款相关。

| 方法 | 大白话解释 |
|------|----------|
| `getAverageCapital()` | 等额本金计算 |
| `getAverageCapitalPlusInterest()` | 等额本息计算 |
| `getPMT()` | 等额Payment计算 |

---

### 3.10 日志工具

#### LogUtils.java
> 🎯 日志工具

### 这是啥？（小白版）
收集异常堆栈信息。

```java
String trace = LogUtils.getMessage(exception);
```

---

#### LogAspect.java
> 🎯 日志切面

### 这是啥？（小白版）
自动记录方法调用的入参、出参、耗时。

---

### 3.11 FTP工具

#### FtpUtil.java
> 🎯 FTP文件传输

### 这是啥？（小白版）
上传下载文件到FTP服务器。

---

### 3.12 序列化工具

#### SerializeUtils.java
> 🎯 对象序列化

### 这是啥？（小白版）
把对象转成字节数组，用于Redis存储。

```java
byte[] bytes = SerializeUtils.serialize(object);
Object obj = SerializeUtils.deserialize(bytes);
```

---

### 3.13 Bean工具

#### BeanUtils.java
> 🎯 Bean属性拷贝

### 这是啥？（小白版）
复制对象属性，相同名字的自动复制。

```java
UserDTO dto = new UserDTO();
BeanUtils.copyProperties(user, dto);  // user的属性复制到dto
```

---

---

## 四、模块间关系

### 架构图
```
┌─────────────────────────────────────────────────────────┐
│                    业务服务层                            │
│              (picc-mzmtb-auth 等)                       │
└─────────────────────┬───────────────────────────────────┘
                      │ 依赖
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  common-call                            │
│            外部服务调用（HTTP/WS/SOAP）                   │
└─────────────────────┬───────────────────────────────────┘
                      │ 依赖
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  common-utils                           │
│            工具类（加密/文件/日期/ID等）                   │
└─────────────────────────────────────────────────────────┘
                      ▲ 依赖
                      │
┌─────────────────────────────────────────────────────────┐
│                  common-core                            │
│            核心基础（实体/服务基类/配置）                   │
└─────────────────────────────────────────────────────────┘
```

### 依赖关系
```
common-core ← common-utils ← common-call
         ←───────────业务服务──────────→
```

---

## 五、核心知识点总结

### 5.1 设计模式
| 模式 | 应用场景 |
|------|----------|
| 模板方法 | BaseServiceImpl定义增删改查模板 |
| 单例模式 | RedisUtil、IdWorker |
| 工厂模式 | CallService根据配置创建不同实现 |
| 策略模式 | 不同加密算法的选择 |

### 5.2 技术栈
| 技术 | 用途 |
|------|------|
| Spring Boot | 快速开发框架 |
| MyBatis/TkMyBatis | 数据库操作 |
| Redis | 缓存、会话存储 |
| JWT/SM4 | 认证加密 |
| Jackson/FastJSON | JSON处理 |
| 雪花算法 | 分布式ID |

### 5.3 安全措施
| 措施 | 说明 |
|------|------|
| SM4加密 | Token、数据加密 |
| MD5/SHA256 | 密码哈希 |
| 参数校验 | 防止注入攻击 |
| 异常隔离 | 不暴露内部错误 |

---

## 六、常见使用示例

### 6.1 新增一条数据
```java
@Autowired
private UserService userService;

public void addUser(User user) {
    userService.save(user);
}
```

### 6.2 分页查询
```java
PageVo page = new PageVo();
page.setPageNum(1);
page.setPageSize(10);

ResultPage<User> result = userService.selectPage(query, page);
List<User> users = result.getData();
```

### 6.3 调用外部服务
```java
JSONObject params = new JSONObject();
params.put("idCard", "110101199001011234");

LinkRuturnEntity result = baseCallService.callService("OCR_WQX", params);
if (result.getSuccess()) {
    JSONObject data = (JSONObject) result.getData();
}
```

### 6.4 生成唯一ID
```java
String id = primaryKeyUtil.snowFlakeKeyStr();
```

### 6.5 Redis缓存
```java
// 缓存用户信息
redisUtil.set("user:" + userId, user, 30*60L);

// 取缓存
User cached = (User) redisUtil.get("user:" + userId);
```
