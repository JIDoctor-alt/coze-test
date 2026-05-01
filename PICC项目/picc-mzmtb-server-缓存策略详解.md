> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC门诊慢特病业务服务 Redis缓存策略完整解析

> 📅 文档生成时间：2025年
> 🎯 适用对象：零基础开发人员、运维人员、业务分析人员
> 🔐 敏感信息已脱敏处理

---

## 目录

1. [零基础概念入门](#一零基础概念入门)
2. [Part 1：Redis配置与连接](#二part-1redis配置与连接)
3. [Part 2：缓存使用清单](#三part-2缓存使用清单)
4. [Part 3：缓存分类整理](#四part-3缓存分类整理)
5. [Part 4：缓存问题分析](#五part-4缓存问题分析)
6. [Part 5：缓存学习要点](#六part-5缓存学习要点)
7. [总结与建议](#七总结与建议)

---

## 一、零基础概念入门

### 1.1 什么是Redis？

**🌡️ 想象一下这个场景：**

你去超市买菜，每次都要从超市门口走到蔬菜区挑选，然后结账再走回来。如果超市就在你家楼下，而且你把常吃的菜提前买好放在冰箱里，是不是就快多了？

**Redis 就是那个"冰箱"！**

| 概念 | 通俗解释 | 技术本质 |
|------|----------|----------|
| Redis | 一个超级快的记事本 | 内存数据库 |
| 传统数据库 | 超市仓库 | 磁盘存储 |
| 缓存 | 冰箱 | 常用数据放内存 |

**为什么Redis这么快？**
- 数据存在**内存**里（就像你从冰箱拿东西 vs 去超市买菜）
- 比数据库快 **100-1000倍**
- 但内存有限，不能什么都放进去

### 1.2 核心概念解释

#### 📦 缓存（Cache）

```
冰箱 = 缓存
- 常用的东西放冰箱（热点数据缓存）
- 不常用的偶尔去买（查询数据库）
- 冰箱满了要清理过期食物（TTL过期策略）
```

#### ⏰ TTL（Time To Live）

```
TTL = 保鲜期

冰箱里的牛奶：
- 过期了（TTL到了）→ 扔掉，重新买
- 没过期 → 继续喝

Redis中的TTL：
- 设置30分钟 → 30分钟后自动删除
- 设置24小时 → 一天后自动删除
```

#### 🔐 缓存穿透

```
坏人故意问你："你家冰箱有外星人的食物吗？"
你回答："没有"，然后去超市找，超市也没有
坏人一直问 → 你一直去超市 → 累死了

解决方案：
1. 布隆过滤器（门口安检，直接拦截）
2. 空值缓存（记住"真的没有"）
```

#### ❄️ 缓存雪崩

```
突然停电了！
冰箱里所有东西同时坏掉
所有人都涌向超市 → 超市挤爆了

解决方案：
1. 随机TTL（让过期时间分散开）
2. 多级缓存（冰箱+冰柜）
3. 熔断限流（排队入场）
```

#### 🔒 分布式锁

```
洗手间只有1个坑位
门锁 = 分布式锁
- 锁住 → 里面的人用完 → 解锁 → 下一个人用
- 保证一次只有1个人能用

场景：
- 抢优惠券
- 防止重复下单
- 定时任务重复执行
```

#### 📝 @Cacheable 注解（Spring缓存）

```
@Cacheable = "先看冰箱有没有，没有再去超市买回来放冰箱"

@Cacheable(value = "user", key = "#id")
public User getUser(Long id) {
    // 第一次：冰箱没有，去数据库查，放冰箱
    // 第二次：冰箱有，直接返回
}
```

---

## 二、Part 1：Redis配置与连接

### 2.1 项目配置概览

根据 `application.yml` 和 `application-sit.yml` 配置分析：

```yaml
# application-sit.yml 配置
spring:
  redis:
    host: 10.252.68.157      # Redis服务器地址（脱敏显示）
    port: 6379               # Redis默认端口
    database: 0              # 使用的数据库编号
    timeout: 30000           # 连接超时时间（毫秒）
    enable: true             # Redis启用开关
    lettuce:                 # 连接池类型
      pool:
        max-active: 8        # 最大连接数
        max-wait: -1         # 最大等待时间（-1表示无限）
        max-idle: 8          # 最大空闲连接数
        min-idle: 0          # 最小空闲连接数
```

### 2.2 Redis连接池配置分析

```
┌─────────────────────────────────────────────────────────────┐
│                    连接池参数建议值                          │
├──────────────────┬──────────────────────────────────────────┤
│     参数名称      │              说明                         │
├──────────────────┼──────────────────────────────────────────┤
│ max-active: 8    │ ⚠️ 偏小！建议根据QPS调整到50-200         │
│ max-idle: 8      │ 空闲时可保留的连接数                       │
│ min-idle: 0     │ ⚠️ 可能导致连接频繁创建销毁                │
│ max-wait: -1    │ 无限制等待，可能导致请求堆积               │
└──────────────────┴──────────────────────────────────────────┘
```

**问题发现：**
1. `max-active: 8` 对于高并发系统来说太小
2. `min-idle: 0` 空闲连接为0，没有预热
3. 缺少 `password` 配置（生产环境必须配置）

### 2.3 Redisson配置（分布式锁）

```java
// RedissonConfig.java
@Configuration
public class RedissonConfig {
    @Bean
    public RedissonClient redissonClient() {
        Config config = new Config();
        
        // 单机模式
        if (StringUtils.isNotBlank(redisProperties.getHost())) {
            config.useSingleServer()
                .setAddress("redis://" + host + ":" + port)
                .setPassword(password)
                .setDatabase(database);
        } 
        // 哨兵模式（高可用）
        else {
            config.useSentinelServers()
                .addSentinelAddress(adds)
                .setMasterName(masterName)
                .setPassword(password)
                .setDatabase(database);
        }
        return Redisson.create(config);
    }
}
```

**支持的部署模式：**
| 模式 | 适用场景 | 配置方式 |
|------|----------|----------|
| 单机模式 | 开发/测试 | `useSingleServer()` |
| 哨兵模式 | 生产高可用 | `useSentinelServers()` |
| 集群模式 | 超大规模 | `useClusterServers()` |
| 主从模式 | 读写分离 | `useMasterSlaveServers()` |

### 2.4 Redis Key前缀定义（RediesCode）

```java
// RediesCode.java - 统一管理Redis Key前缀
public class RediesCode {
    // 手机验证码
    public static final String PHONE_VERIFYCODE = "verifyCode:";
    
    // 微信相关
    public static final String WX_ACCESSTOKEN = "wx:accesstoken";
    public static final String WX_ACCESSTOKEN_H5 = "wx:accesstokenh5";
    public static final String WX_JSAPITICKET_H5 = "wx:jsapitickeh5";
    
    // 地理位置
    public static final String WX_FUJINYAODIAN = "wx:fujinyaodian";    // 附近药店
    public static final String WX_FUJINMEMBER = "wx:fujinmember";      // 附近会员
    
    // 业务数据
    public static final String WX_VIPDRUGFORMKEY = "wx:vipdrugformkey";  // 药品来源
    
    // TTL常量
    public static final int WX_FUJINTIMEOUT = 11;           // 附近药店缓存11分钟
    public static final int WX_VIPDRUGFORMKEYTIMEOUT = 1440; // 药品数据缓存24小时
}
```

---

## 三、Part 2：缓存使用清单

> 🔍 以下是项目中所有Redis缓存使用场景的完整清单

### 3.1 用户认证与Token管理

#### ✅ 场景1：API Token管理

```java
// 位置：TokenInterceptorConfig.java
// 用途：用户登录凭证校验与自动续期

Key格式：
- API_TOKEN + token → User对象
- API_USERKEY + userId → User对象
- userid: + userId → token字符串

示例：
- "api:token:abc123xyz" → User对象（用户信息）
- "api:userkey:10001" → User对象
- "userid:10001" → "abc123xyz"（token）

TTL：120分钟（自动续期）

为什么需要缓存？
👤 人话：登录后把用户信息存"临时工作证"，每次请求验证一下，不用每次都去人事部查

缓存策略：
1. 登录时设置 → 有效期120分钟
2. 每次请求 → 自动刷新延期
3. 登出时删除
```

#### ✅ 场景2：用户权限标识

```java
// 位置：TokenInterceptorConfig.java

Key格式：
- "flag:" + userId → 权限标识字符串
- "UrlPermission:" + userId → List<String>权限列表

示例：
- "flag:10001" → "admin"
- "UrlPermission:10001" → ["/api/user/list", "/api/order/*"]

TTL：120分钟（与Token同步）

为什么需要缓存？
👤 人话：员工进公司要刷卡，显示他能进哪些房间。刷卡记录缓存起来，不用每次都查数据库

缓存策略：
1. 用户登录 → 加载权限到Redis
2. 请求验证 → 查Redis权限列表
3. 权限变更 → 清除缓存重新加载
```

### 3.2 登录验证码与限流

#### ✅ 场景3：图形验证码缓存

```java
// 位置：LoginApi.java

Key格式：
- "x" → 拼图滑块x坐标值

TTL：30分钟

为什么需要缓存？
👤 人话：注册时滑动拼图验证，滑块位置要记住，30分钟内不用重新生成

代码示例：
redisUtil.set(CaptchaConstant.X, captchaDTO.getX(), 30*60L);
```

#### ✅ 场景4：短信验证码防刷

```java
// 位置：LoginApi.java

Key格式：
- "verifyCode:" + 手机号 + 验证码类型 → 验证码值

示例：
- "verifyCode:13800138000login" → "123456"

TTL：
- 首次设置：60秒
- 计数重置：300秒（5分钟）

为什么需要缓存？
👤 人话：防止恶意刷短信，每5分钟最多发5次，像电话亭的投币计时器

缓存策略：
1. 首次发送 → 记录并计数=1，TTL=60秒
2. 再次发送 → 计数+1，TTL重置=300秒
3. 超过5次 → 阻止发送

代码示例：
String receiver = RediesCode.PHONE_VERIFYCODE + phone + verificationFlag;
if (!redisUtil.exists(receiver)) {
    redisUtil.set(receiver, "1", 60L);  // 首次
} else {
    count = Integer.parseInt(redisUtil.get(receiver));
    if (limit >= count) {
        redisUtil.set(receiver, (count + 1) + "", 300L);  // 重置TTL
    }
}
```

### 3.3 外部系统配置缓存

#### ✅ 场景5：对外系统信息缓存（OutSystemCache）

```java
// 位置：OutSystemCache.java

Key格式：
- REDIS_CALL_CONFIG + syscode → VipOutsystem对象
- REDIS_CALL_GRANT + syscode + ":" + interfacecode → VipInterfaceGrant对象
- REDIS_CALL_FLAG → 初始化状态标识

常量定义：
public static final String REDIS_CALL_CONFIG = "outSystem:info:";
public static final String REDIS_CALL_GRANT = "outSystem:grant:";
public static final String REDIS_CALL_FLAG = "outSystem:1";

示例：
- "outSystem:info:jghx" → 第三方系统配置对象
- "outSystem:grant:jghx:orderquery" → 接口授权对象

TTL：无明确过期时间（程序控制刷新）

为什么需要缓存？
👤 人话：合作公司的账号密码和接口权限，像通讯录一样存在手机里，不用每次翻档案柜

缓存策略：
1. 应用启动 → 检查FLAG是否存在
2. 不存在 → 从数据库加载所有系统配置
3. 变更时 → 清除FLAG强制重载
```

#### ✅ 场景6：机构配置缓存（UnitConfigCache）

```java
// 位置：UnitConfigCache.java

Key格式：
- UNIT_CONFIG_FLAG + flag → 机构名称

常量定义：
public static final String UNIT_CONFIG_FLAG = "flag:config:";

示例：
- "flag:config:99" → "WX"（微信）
- "flag:config:YL" → "养老"

TTL：无明确过期时间

为什么需要缓存？
👤 人话：不同地区的医保政策不同，机构配置像城市区号本，常查常驻

初始化：
List<UnitConfig> unitConfigs = unitConfigService.selectAll();
for (UnitConfig unitConfig : unitConfigs) {
    redisUtil.set(UNIT_CONFIG_FLAG + unitConfig.getFlag(), unitConfig.getName());
}
```

### 3.4 定时任务调度控制

#### ✅ 场景7：定时任务防并发执行

```java
// 位置：SchedulingApi.java

Key格式：
- "ghiInsureDetailInitTask" → 任务状态（0/1）
- "vipMbmzStatusTask" → 任务状态
- "vipSendMessageTask" → 任务状态
- "wqxOutInterfaceTask" → 任务状态
- "xjsMRXOutInterfaceTask" → 任务状态
- "file2ImageTask" → 任务状态

TTL：无（程序控制）

值说明：
- "0" → 空闲状态，可执行
- "1" → 执行中，禁止重复执行

为什么需要缓存？
👤 人话：定时任务像自动扫地机器人，设置为"打扫中"后，防止它还没扫完又启动另一个

代码示例：
public ApiResponse excuteGhiInsureDetailInitTask() {
    String tFlag = redisUtil.get("ghiInsureDetailInitTask");
    if ("1".equals(tFlag)) {
        return ApiResponse.fail("任务执行中，不重复执行");
    }
    redisUtil.set("ghiInsureDetailInitTask", "1");
    try {
        ghiInsureDetailInitTask.run();
    } finally {
        redisUtil.set("ghiInsureDetailInitTask", "0");
    }
}
```

#### ✅ 场景8：第三方接口状态检测

```java
// 位置：BJGXTTask.java

Key格式：
- "baoji:Switch" → 宝鸡共享库接口状态（boolean）

示例：
- "baoji:Switch" → true（接口正常）
- "baoji:Switch" → false（接口故障）

TTL：无（故障检测后自动更新）

为什么需要缓存？
👤 人话：定期检查合作的快递公司电话能不能打通，打不通就换一家

代码示例：
public void detectionSwitchTask() {
    if (redisUtil.exists(BJGXK)) {
        boolean b = (boolean) redisUtil.get(BJGXK);
        if (!b) {
            // 尝试调用接口检测
            JSONObject data = callCxcfService.ybQueryPreBj(vo);
            if ("200".equals(data.getString("code"))) {
                redisUtil.set(BJGXK, true);  // 恢复
            }
        }
    }
}
```

### 3.5 业务数据缓存

#### ✅ 场景9：功能开关配置（FunctionSwitch）

```java
// 位置：FunctionSwitchServiceImpl.java

Key格式：
- "mb:switch:" + flag → TFunctionSwitch对象

示例：
- "mb:switch:declare_open" → 申报开关配置
- "mb:switch:notice_daily" → 每日通知开关

TTL：无明确过期时间（启动时加载）

为什么需要缓存？
👤 人话：App功能的"开关按钮"，像电灯开关一样频繁操作，缓存起来不用查数据库

缓存策略：
1. @PostConstruct启动加载 → 全量加载到Redis
2. 查询时 → 直接从Redis取
3. 变更时 → 更新Redis

代码示例：
@PostConstruct
public void init() {
    List<TFunctionSwitch> switches = tFunctionSwitchDao.selectAll();
    for (TFunctionSwitch tfs : switches) {
        redisUtil.set(mbswitch + tfs.getFlag(), tfs);
    }
}
```

#### ✅ 场景10：病种限额配置缓存（多地区）

```java
// 位置：TDiseaseMzlServiceImpl.java

Key格式：
- "mzl:disease" → Map<String, DiseaseMzl>全量病种
- "mzl:limit" → List<LimitConfig>限额配置
- "mzl:allKey:" + icdcode → 单个病种对象

示例：
- "mzl:disease" → 整个绵阳病种Map
- "mzl:limit" → 限额配置列表
- "mzl:allKey:E11.301" → 具体病种对象

TTL：无明确过期时间

为什么需要缓存？
👤 人话：医保报销的病种目录和报销限额，像字典一样常用，提前背下来查得快

缓存策略：
1. @PostConstruct启动加载
2. 查询按ICD编码缓存
3. 变更需手动刷新缓存
```

```java
// 其他地区病种缓存（类似结构）
// 位置：TDiseaseDizServiceImpl.java
Key: "diz:disease", "diz:allKey:", "diz:limit"

// 位置：TDiseaseJcServiceImpl.java  
Key: "JC:disease", "JC:allKey:", "JC:limit"

// 位置：TDiseaseJjServiceImpl.java
Key: "JJ:disease", "JJ:allKey:", "JJ:limit"
```

#### ✅ 场景11：病种信息查询（西宁地区）

```java
// 位置：DiseaseXYaServiceImpl.java

Key格式：
- "XYa:allKey:" + icdcode → DiseaseXya病种对象

示例：
- "XYa:allKey:E11.301" → 青海西宁某病种信息

TTL：无明确过期时间

为什么需要缓存？
👤 人话：每个地区的医保报销政策不同，按ICD编码缓存常用病种，查得快

代码示例：
public DiseaseXya getDiseaseByCode(String icdcode) {
    return (DiseaseXya) redisUtil.get(allKey + icdcode);
}
```

#### ✅ 场景12：专家信息缓存

```java
// 位置：VipMbuserExtServiceImpl.java

Key格式：
- "CatalogJson-Lock" → 分布式锁

用途：专家目录JSON操作的并发控制

为什么需要缓存？
👤 人话：专家信息表像通讯录，查和改不能同时进行，加锁防止乱序

代码示例：
RLock lock = redissonClient.getLock("CatalogJson-Lock");
lock.lock();
try {
    // 专家目录操作
} finally {
    lock.unlock();
}
```

#### ✅ 场景13：机构信息缓存

```java
// 位置：MtbUserExtApiAndOrgServiceImpl.java

Key格式：
- 机构编码 → VipPhysicalOrg对象

示例：
- "ORG001" → 体检机构配置

TTL：无明确过期时间

为什么需要缓存？
👤 人话：定点医院信息像名片夹，频繁查询，缓存减少数据库压力
```

### 3.6 用户操作锁

#### ✅ 场景14：用户账户锁定

```java
// 位置：MtbUserExtApiAndOrgServiceImpl.java

Key格式：
- USERLOCK + userAccount + "lock" → 锁定标识
- USERLOCK + userAccount → 用户信息
- USERLOCK + userAccount + "lockFlag" → 锁定原因

常量定义：
private final String USERLOCK = "userLock :";

示例：
- "userLock :admin001lock" → "locked"
- "userLock :admin001" → 用户信息
- "userLock :admin001lockFlag" → "密码错误5次"

TTL：定时任务自动解锁

为什么需要缓存？
👤 人话：账户输错5次密码就锁住，像ATM机一样，记在机器里比查数据库快

代码示例：
// 锁定
redisUtil.set(USERLOCK + userAccount + "lock", "locked");
redisUtil.set(USERLOCK + userAccount + "lockFlag", "密码错误次数过多");

// 解锁
redisUtil.remove(USERLOCK + userAccount + "lock");
redisUtil.remove(USERLOCK + userAccount);
redisUtil.remove(USERLOCK + userAccount + "lockFlag");
```

### 3.7 智能审核分布式锁

#### ✅ 场景15：AI智能审核并发控制

```java
// 位置：MtbVipIntelligentAuditLockServiceImpl.java

Key格式：
- "global:audit:query" → 读锁
- "declare:" + declareId + ":audit" → 申报记录写锁
- "status:" + declareId + ":lock" → 状态变更锁

锁配置：
- READ_LOCK_WAIT_TIME = 3L（秒）
- WRITE_LOCK_WAIT_TIME = 5L（秒）
- LOCK_LEASE_TIME = 30L（秒）

为什么需要缓存？
👤 人话：AI审核像流水线作业，多个人同时处理同一申报会乱，需要按申报单号排队

代码示例：
// 读锁 - 查询时使用
RReadWriteLock globalReadLock = redissonClient.getReadWriteLock("global:audit:query");
RLock readLock = globalReadLock.readLock();
readLock.lock(3, TimeUnit.SECONDS);

// 写锁 - 处理时使用
RReadWriteLock writeLock = redissonClient.getReadWriteLock("declare:" + declareId);
RLock lock = writeLock.writeLock();
lock.lock(30, TimeUnit.SECONDS);
```

---

## 四、Part 3：缓存分类整理

### 4.1 分类总览

```
┌─────────────────────────────────────────────────────────────────┐
│                     PICC慢特病系统 Redis缓存分类                  │
├─────────────────┬───────────────────────────────────────────────┤
│   缓存类型       │              数量/占比                        │
├─────────────────┼───────────────────────────────────────────────┤
│ 1.Token/会话缓存  │ 约6个Key类型，覆盖登录、权限                │
│ 2.业务数据缓存    │ 最多，约20+个Key类型，病种、配置、机构等    │
│ 3.分布式锁       │ 10+个锁Key，用于并发控制                    │
│ 4.计数器/限流    │ 约5个，用于防刷、任务调度                   │
│ 5.定时任务控制    │ 6+个，用于任务状态标记                     │
└─────────────────┴───────────────────────────────────────────────┘
```

### 4.2 详细分类表

#### 📋 类型一：Token/会话缓存

| Key格式 | Value类型 | TTL | 用途 |
|---------|-----------|-----|------|
| `api:token:{token}` | User对象 | 120分钟 | 用户登录凭证 |
| `api:userkey:{userId}` | User对象 | 120分钟 | 用户信息缓存 |
| `userid:{userId}` | String(token) | 120分钟 | 用户Token映射 |
| `flag:{userId}` | String | 120分钟 | 用户权限标识 |
| `UrlPermission:{userId}` | List<String> | 120分钟 | 接口权限列表 |
| `x` | Integer | 30分钟 | 图形验证码坐标 |

#### 📋 类型二：业务数据缓存

| Key格式 | Value类型 | TTL | 用途 |
|---------|-----------|-----|------|
| `outSystem:info:{syscode}` | VipOutsystem | 无 | 外部系统配置 |
| `outSystem:grant:{syscode}:{interface}` | VipInterfaceGrant | 无 | 接口授权信息 |
| `flag:config:{flag}` | String | 无 | 机构配置 |
| `mb:switch:{flag}` | TFunctionSwitch | 无 | 功能开关 |
| `mzl:disease` | Map | 无 | 绵阳病种全量 |
| `mzl:limit` | List | 无 | 绵阳限额配置 |
| `mzl:allKey:{icdcode}` | DiseaseMzl | 无 | 单个病种 |
| `diz:disease` | Map | 无 | 迪庆病种全量 |
| `JC:disease` | Map | 无 | 金昌病种全量 |
| `JJ:disease` | Map | 无 | 晋江病种全量 |
| `XYa:allKey:{icdcode}` | DiseaseXya | 无 | 西宁病种 |
| `baoji:Switch` | Boolean | 无 | 宝鸡接口状态 |
| `verifyCode:{phone}{type}` | String | 60-300秒 | 短信验证码 |

#### 📋 类型三：分布式锁

| Key格式 | 锁类型 | 用途 |
|---------|--------|------|
| `CatalogJson-Lock` | 互斥锁 | 专家目录操作 |
| `global:audit:query` | 读锁 | AI审核查询 |
| `declare:{id}:audit` | 写锁 | 申报记录处理 |
| `status:{id}:lock` | 互斥锁 | 状态变更控制 |
| `userLock :{account}lock` | 互斥锁 | 账户锁定 |

#### 📋 类型四：计数器/限流

| Key格式 | 用途 | TTL |
|---------|------|-----|
| `verifyCode:{phone}{type}` | 短信发送计数 | 300秒 |
| `call:1` | 外部调用计数 | - |

#### 📋 类型五：定时任务控制

| Key格式 | 值 | 用途 |
|---------|-----|------|
| `ghiInsureDetailInitTask` | 0/1 | 宝鸡发卡任务 |
| `vipMbmzStatusTask` | 0/1 | 慢病状态更新 |
| `vipSendMessageTask` | 0/1 | 短信发送任务 |
| `wqxOutInterfaceTask` | 0/1 | 外部接口任务 |
| `xjsMRXOutInterfaceTask` | 0/1 | MRX接口任务 |
| `file2ImageTask` | 0/1 | 文件转换任务 |

---

## 五、Part 4：缓存问题分析

### 5.1 问题总览

```
⚠️ 已发现的缓存问题

┌────────────────────────────────────────────────────────────┐
│ 问题类型              │ 严重程度  │ 影响范围               │
├─────────────────────┼──────────┼────────────────────────┤
│ 1. 缓存穿透风险       │   高     │ 短信验证码、病种查询    │
│ 2. 缓存雪崩风险       │   中     │ 大量无TTL缓存          │
│ 3. 缓存一致性问题     │   高     │ 业务数据变更不同步      │
│ 4. 热点Key问题        │   中     │ 高频访问配置项          │
│ 5. Key过期策略缺失    │   中     │ 大部分业务缓存无TTL     │
│ 6. 连接池配置过小     │   高     │ 并发能力受限           │
│ 7. 零缓存问题         │   高     │ 大部分查询无缓存        │
└─────────────────────┴──────────┴────────────────────────┘
```

### 5.2 问题详细分析

#### 🔴 问题1：缓存穿透风险

**问题描述：**
```java
// 位置：DiseaseXYaServiceImpl.java
private List<DiseaseXya> getDiseaseXYAByIcdCodes(String icdcodes) {
    String[] icdcodeArr = icdcodes.split(",");
    List<DiseaseXya> diseaseXya = new ArrayList<>();
    for (String icdcode : icdcodeArr) {
        // ⚠️ 直接get，key不存在返回null，可能抛NPE
        DiseaseXya diseaseXyaOne = (DiseaseXya) redisUtil.get(allKey + icdcode);
        diseaseXya.add(diseaseXyaOne);  // 可能加入null
    }
    return diseaseXya;
}
```

**风险：**
- 查询不存在的ICD编码 → Redis无 → 查数据库 → 数据库也无 → 返回null
- 恶意请求不存在的数据 → 每次都打到数据库

**影响范围：**
- 所有病种查询接口
- 机构信息查询

**解决方案：**
```java
// 改进方案：增加空值缓存
private static final String NULL_MARK = "NULL";  // 空值标记

public DiseaseXya getDisease(String icdcode) {
    String key = allKey + icdcode;
    Object value = redisUtil.get(key);
    
    if (value == null) {
        // 查数据库
        DiseaseXya disease = diseaseDao.selectByCode(icdcode);
        if (disease != null) {
            redisUtil.set(key, disease);
        } else {
            // 空值缓存，防止穿透
            redisUtil.set(key, NULL_MARK, 5 * 60);  // 5分钟过期
        }
        return disease;
    }
    
    if (NULL_MARK.equals(value)) {
        return null;  // 已知的不存在数据
    }
    
    return (DiseaseXya) value;
}
```

#### 🔴 问题2：缓存一致性问题

**问题描述：**
```java
// 位置：OutSystemCache.java
// 外部系统配置变更后，需要手动调用API清除缓存
public void removeSystemCache() {
    redisUtil.remove(REDIS_CALL_FLAG);  // 强制重载
}
```

**风险：**
- 数据库数据变更 → Redis不同步
- 需要手动调用清除接口
- 多实例部署时清除不彻底

**影响范围：**
- 外部系统配置
- 功能开关
- 机构配置

**解决方案：**
```
方案A：定时同步（适合变更不频繁）
┌──────────────────────────────────────────┐
│ 定时任务：每5分钟检查配置表变更            │
│ 变更记录表：记录配置ID和更新时间           │
└──────────────────────────────────────────┘

方案B：订阅数据库变更（推荐）
┌──────────────────────────────────────────┐
│ 使用Canal等工具监听数据库变更              │
│ 变更时主动更新/删除Redis                  │
└──────────────────────────────────────────┘

方案C：程序控制（适合实时性要求高）
┌──────────────────────────────────────────┐
│ 变更配置时，同时更新Redis                  │
│ 使用事务保证一致性                         │
└──────────────────────────────────────────┘
```

#### 🔴 问题3：Key过期策略缺失

**问题描述：**
```java
// 大部分缓存没有设置TTL
redisUtil.set("mzl:disease", diseaseMap);        // ❌ 无TTL
redisUtil.set("mb:switch:" + flag, tfs);         // ❌ 无TTL
redisUtil.set(REDIS_CALL_CONFIG + syscode, row); // ❌ 无TTL
```

**风险：**
- 数据变更后旧缓存长期存在
- 内存持续增长（如果Redis内存满会自动淘汰）
- 无法保证数据新鲜度

**影响范围：**
- 所有业务数据缓存
- 外部系统配置
- 功能开关

#### 🟡 问题4：连接池配置过小

**当前配置：**
```yaml
spring:
  redis:
    lettuce:
      pool:
        max-active: 8      # ⚠️ 太小
        max-idle: 8
        min-idle: 0        # ⚠️ 无预热
        max-wait: -1       # ⚠️ 无限等待
```

**风险：**
- 并发请求超过8个时排队等待
- 高峰期可能超时
- 冷启动时无连接可用

**建议配置：**
```yaml
spring:
  redis:
    lettuce:
      pool:
        max-active: 50     # 根据QPS调整
        max-idle: 20
        min-idle: 10       # 预热连接
        max-wait: 3000     # 3秒超时
```

#### 🟡 问题5：零缓存问题

**审计发现的"零缓存"问题：**

```java
// 典型场景：每次都查数据库
public VipMbdeclareInfo getDeclareInfo(String declareId) {
    // ⚠️ 直接查数据库，没有缓存
    return vipMbdeclareInfoDao.selectById(declareId);
}
```

**应该缓存但没缓存的热点查询：**
| 查询场景 | 建议缓存 | 原因 |
|----------|----------|------|
| 申报单详情 | 5-15分钟 | 高频访问，变更不频繁 |
| 体检机构列表 | 30-60分钟 | 相对稳定 |
| 用户信息 | 15-30分钟 | 可能变更，需平衡 |
| 医保政策配置 | 24小时 | 很少变更 |
| 药品目录 | 24小时 | 数据量大但稳定 |

---

## 六、Part 5：缓存学习要点

### 6.1 缓存Key命名规范建议

**当前问题：**
```
❌ 混乱的命名
- "baoji:Switch"
- "mzl:disease"
- "mb:switch:"
- "flag:config:"
- "userLock :xxx"  (注意空格!)
```

**建议规范：**
```
✅ 统一格式：模块:业务:标识

推荐格式：
{system}:{module}:{entity}:{id}

示例：
- picc:mb:disease:mzl:{icdcode}    绵阳病种
- picc:mb:disease:diz:{icdcode}    迪庆病种
- picc:auth:token:{token}          登录Token
- picc:auth:user:{userId}          用户信息
- picc:config:switch:{flag}        功能开关
- picc:external:system:{syscode}   外部系统
- picc:lock:user:{account}         用户锁
- picc:task:{taskName}             任务状态
```

**命名原则：**
1. 前缀统一（项目标识）
2. 模块清晰（auth/mb/config等）
3. 语义明确（user/token/switch）
4. 避免特殊字符（空格、冒号过多）
5. 长度控制（建议不超过100字符）

### 6.2 TTL设置建议

```
┌─────────────────────────────────────────────────────────────────┐
│                        TTL设置建议表                             │
├───────────────────────┬──────────────┬──────────────────────────┤
│       缓存类型         │   建议TTL    │          说明             │
├───────────────────────┼──────────────┼──────────────────────────┤
│ Token/会话            │ 120-1440分钟 │ 登录有效期与活跃度相关   │
│ 验证码                │ 5-30分钟     │ 一次性，短时效           │
│ 用户权限              │ 30-120分钟   │ 权限变更需及时生效       │
│ 业务配置（稳定）       │ 24小时起     │ 配置很少变更             │
│ 业务配置（易变）       │ 5-30分钟     │ 需要及时同步             │
│ 病种/药品目录         │ 24小时       │ 数据量大，更新不频繁      │
│ 机构信息              │ 1-24小时     │ 相对稳定                 │
│ 排行榜/统计           │ 5-60分钟     │ 需要实时性               │
│ 防刷限流              │ 秒级到分钟级  │ 短期计数                 │
│ 分布式锁              │ 30秒-5分钟   │ 防止死锁                 │
│ 任务状态标记          │ 无（程序控制）│ 需要持久化               │
└───────────────────────┴──────────────┴──────────────────────────┘
```

### 6.3 应该加缓存但没加的场景

#### 📌 场景1：申报单查询（高频）

```java
// 当前：每次查数据库
public VipMbdeclareInfo getDeclareInfo(String declareId) {
    return vipMbdeclareInfoDao.selectById(declareId);
}

// 建议：增加缓存
@Cacheable(value = "declare", key = "#declareId", ttl = 900)
public VipMbdeclareInfo getDeclareInfoCached(String declareId) {
    return vipMbdeclareInfoDao.selectById(declareId);
}

// 更新时清除缓存
@CacheEvict(value = "declare", key = "#declareId")
public void updateDeclare(VipMbdeclareInfo info) {
    // ...
}
```

#### 📌 场景2：体检机构列表（相对稳定）

```java
// 当前：无缓存
public List<VipPhysicalOrg> getPhysicalOrgList() {
    return physicalOrgDao.selectAll();
}

// 建议：缓存1小时
public List<VipPhysicalOrg> getPhysicalOrgList() {
    String key = "picc:mb:org:physical:all";
    List<VipPhysicalOrg> list = redisUtil.get(key);
    if (list == null) {
        list = physicalOrgDao.selectAll();
        redisUtil.set(key, list, 3600);
    }
    return list;
}
```

#### 📌 场景3：医保目录查询（大数据量）

```java
// 建议：按条件缓存
public List<DrugCatalog> searchDrugs(String keyword, String region) {
    String key = "picc:mb:drug:search:" + MD5(keyword + region);
    List<DrugCatalog> result = redisUtil.get(key);
    if (result == null) {
        result = drugDao.search(keyword, region);
        // 缓存5分钟
        redisUtil.set(key, result, 300);
    }
    return result;
}
```

### 6.4 缓存预热方案

**问题：** 服务重启后Redis缓存为空，首次请求全部打库

**解决方案：**

```java
// 方案1：启动时预热
@Component
public class CacheWarmupRunner implements CommandLineRunner {
    
    @Override
    public void run(String... args) {
        log.info("开始缓存预热...");
        
        // 1. 预热病种数据
        diseaseCacheService.init();
        
        // 2. 预热功能开关
        functionSwitchService.init();
        
        // 3. 预热外部系统配置
        outSystemCache.initMethod();
        
        // 4. 预热机构配置
        unitConfigCache.initMethod();
        
        log.info("缓存预热完成");
    }
}

// 方案2：懒加载+热点驻留
@Component
public class HotDataKeeper {
    
    // 最近访问的热点数据
    private final Map<String, Long> hotKeys = new ConcurrentHashMap<>();
    
    @PostConstruct
    public void init() {
        // 启动定时任务，统计热点Key
        scheduleAtFixedRate(() -> {
            // 记录访问频率
            // 将高频访问的Key延长TTL
        }, 5, 5, TimeUnit.MINUTES);
    }
}

// 方案3：预加载关键数据到JVM缓存
@Bean
public LoadingCache<String, Object> localCache = Caffeine.newBuilder()
    .maximumSize(10000)
    .expireAfterWrite(5, TimeUnit.MINUTES)
    .build(key -> {
        // 二级Redis查询
        Object value = redisUtil.get(key);
        if (value == null) {
            value = databaseService.getByKey(key);
        }
        return value;
    });
```

### 6.5 缓存架构学习要点

```
                    ┌─────────────────────────────────────┐
                    │            应用层                   │
                    │  ┌─────────────────────────────┐   │
                    │  │     本地缓存 (Caffeine)      │   │
                    │  │   热点数据，极低延迟         │   │
                    │  └──────────────┬──────────────┘   │
                    │                 │                  │
                    │  ┌──────────────▼──────────────┐   │
                    │  │     Redis缓存               │   │
                    │  │   共享缓存，一级存储        │   │
                    │  └──────────────┬──────────────┘   │
                    │                 │                  │
                    │  ┌──────────────▼──────────────┐   │
                    │  │     MySQL数据库             │   │
                    │  │   最终数据源                │   │
                    │  └─────────────────────────────┘   │
                    └─────────────────────────────────────┘

架构说明：
1. 本地缓存：热点数据（如配置、字典），延迟<1ms
2. Redis缓存：共享缓存，支持分布式，延迟<5ms
3. 数据库：持久化存储，延迟10-50ms
```

---

## 七、总结与建议

### 7.1 现状总结

```
┌─────────────────────────────────────────────────────────────────┐
│                   PICC慢特病系统 Redis现状                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ 已实现的能力：                                                │
│  ├─ Token/会话管理（登录认证）                                    │
│  ├─ 基础业务缓存（病种、配置、机构）                               │
│  ├─ 分布式锁（智能审核、定时任务）                                 │
│  ├─ 限流防刷（短信验证码）                                        │
│  └─ 定时任务状态控制                                              │
│                                                                 │
│  ⚠️ 待改进的问题：                                                │
│  ├─ 缓存穿透防护不足                                              │
│  ├─ 部分缓存无TTL策略                                             │
│  ├─ 连接池配置偏小                                                │
│  ├─ 缺少热点数据自动识别                                          │
│  ├─ 缓存一致性保障机制                                            │
│  └─ 零缓存场景仍较多                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 优先级建议

```
阶段一（紧急-1周内）：
1. 🔴 修复缓存穿透风险（空值缓存）
2. 🔴 增加短信防刷限流
3. 🔴 调整Redis连接池配置

阶段二（重要-2周内）：
4. 🟡 为所有缓存添加TTL
5. 🟡 实现缓存预热机制
6. 🟡 增加热点数据统计

阶段三（优化-1月内）：
7. 🟢 统一Key命名规范
8. 🟢 引入本地缓存（Caffeine）
9. 🟢 实现配置变更主动推送
```

### 7.3 监控指标建议

```yaml
# 需要监控的Redis指标
redis:
  # 连接指标
  - connected_clients: 连接数
  - blocked_clients: 阻塞客户端数
  
  # 内存指标
  - used_memory: 已用内存
  - used_memory_rss: 物理内存
  - maxmemory: 最大内存
  
  # 性能指标
  - ops_per_sec: 每秒操作数
  - hit_rate: 缓存命中率
  - evicted_keys: 驱逐键数
  
  # 业务指标（自定义）
  - cache:mb:disease:size: 病种缓存大小
  - cache:token:count: Token数量
  - lock:wait:time: 锁等待时间
```

### 7.4 最佳实践清单

```
✅ 缓存使用 Checklist

【Key设计】
□ Key命名符合规范（项目:模块:实体:ID）
□ 避免使用特殊字符和空格
□ 控制Key长度不超过100字符

【TTL设置】
□ 所有缓存必须设置TTL
□ Token类：120-1440分钟
□ 验证码类：5-30分钟
□ 业务配置：24小时起
□ 热点数据：5-60分钟

【一致性】
□ 数据变更时同步更新/删除缓存
□ 关键操作使用事务或Lua脚本
□ 考虑双写一致性 vs 最终一致性

【防护】
□ 防止缓存穿透（空值缓存/布隆过滤器）
□ 防止缓存雪崩（随机TTL/多级缓存）
□ 防止热点Key集中（分散/本地缓存）

【监控】
□ 监控缓存命中率
□ 监控内存使用
□ 监控慢查询
□ 设置告警阈值
```

---

## 附录：术语表

| 术语 | 英文 | 解释 |
|------|------|------|
| 缓存 | Cache | 临时存储数据的组件，比数据库快 |
| TTL | Time To Live | 缓存过期时间 |
| 穿透 | Penetration | 请求穿过缓存直达数据库 |
| 雪崩 | Avalanche | 大量缓存同时过期或故障 |
| 击穿 | Breakdown | 热点Key过期瞬间大量请求 |
| 分布式锁 | Distributed Lock | 多机器协调访问的互斥机制 |
| 本地缓存 | Local Cache | 进程内缓存，最快 |
| Redis | Remote Dictionary Server | 远程字典服务，开源缓存中间件 |
| Redisson | - | Redis的Java客户端，封装了分布式锁等 |

---

**文档结束**

> 📝 本文档基于对 `picc-mzmtb-server` 项目源码的静态分析生成
> ⚠️ 实际运行行为请以生产环境为准
> 🔐 所有敏感信息（IP、密码等）已做脱敏处理
