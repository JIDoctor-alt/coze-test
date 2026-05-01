> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC门诊慢特病业务服务 - 架构深度解析

> 📖 **相关文档**：[项目全貌](picc-mzmtb-server-项目全貌.md) · [安全与代码质量审计](picc-mzmtb-server-安全与代码质量审计.md) · [数据模型解析](picc-mzmtb-server-数据模型解析.md) · [API接口全景](picc-mzmtb-server-API接口全景.md) 📌(权限服务)

> 文档版本：1.0  
> 生成时间：2025年  
> 项目名称：门诊慢特病业务管理信息系统-中台服务  
> 项目版本：1.0

---

## 一、技术栈全景

### 1.1 核心技术框架

| 技术组件 | 版本 | 说明 |
|---------|------|------|
| **Spring Boot** | 父级4.2.6.0 | 统一开发平台(pdfc)封装，企业级应用基础框架 |
| **Java** | 8 | JDK 8，成熟稳定的企业级运行时 |
| **MyBatis** | pdfc-mybatis | 通过pdfc封装的MyBatis，简化数据库操作 |
| **Activiti** | 6.0.0 | 工作流引擎，处理慢特病申报审批流程 |
| **Apollo** | 配置中心 | 分布式配置管理，支持多环境配置切换 |
| **Redis** | Redisson 3.13.4 | 分布式缓存+Session管理，支持哨兵模式 |
| **Druid** | 1.0.11 | 阿里数据库连接池，性能监控 |
| **PageHelper** | 5.3.1 | MyBatis分页插件 |

### 1.2 信创适配

| 中间件 | 版本 | 用途 |
|-------|------|------|
| **BES(宝蓝德应用服务器)** | 9.5.5.007 | 信创环境应用服务器 |
| **GaussDB** | - | 华为高斯数据库(通过activiti-engine-picc适配) |

> 💡 **小白理解**：信创就是用国产软硬件替代国外产品。BES就像Tomcat的国产版，GaussDB是Oracle/DB2的国产替代。

### 1.3 文档处理套件

| 组件 | 版本 | 用途 |
|-----|------|------|
| Apache POI | 4.1.2 | Excel/Word文档生成与解析 |
| PDFBox | 2.0.21 | PDF文档处理 |
| JodConverter | 4.3.0 | 文档格式转换(Office↔PDF) |
| iTextPDF | 5.5.10 | PDF生成与处理 |

---

## 二、Maven依赖分析

### 2.1 父级依赖 (pdfc-parent 4.2.6.0)

```
【大白话】pdfc就像一个"企业开发模板包"，里面定义了：
- 统一的项目结构
- 标准的依赖版本
- 通用的插件配置
所有子公司项目都基于这个模板开发，保证技术栈统一。
```

### 2.2 核心业务依赖

| 依赖坐标 | 版本 | 小白化解释 |
|---------|------|-----------|
| `com.picchealth:common-core` | 2.0 | 公共工具核心包，封装了通用工具类 |
| `com.picchealth:common-call` | 2.0 | 服务调用包，用于微服务间通信 |
| `com.picchealth:common-utils` | 2.0 | 工具类集合(String/Date/加密等) |
| `com.picchealth:picchealth-db` | 1.0 | 数据库层(DAO+PO+Mapper XML) |
| `com.picchealth:picchealth-server` | 1.0 | 主服务(API+Service+VO) |

### 2.3 地市差异化模块

```xml
【地市模块依赖清单】
mtb-base      - 基础包(674个文件，所有地市的公共代码)
mtb-bj        - 宝鸡特化实现
mtb-dz        - 德州特化实现  
mtb-jc        - 晋城特化实现
mtb-jj        - 九江特化实现
mtb-mzl       - 眉县/陇县特化实现
mtb-ya        - 延安特化实现
mtb-yl        - 榆林特化实现
mtb-yli       - 榆林(独立)特化实现
mtb-sl        - 省略...
mtb-xya       - 省略...
```

> 💡 **小白理解**：就像一套"标准化模板+地方补丁"，基础包是全国统一的，地市模块是根据各地方政策/流程特化的部分。

### 2.4 工作流依赖

| 依赖 | 版本 | 作用 |
|-----|------|------|
| `activiti-spring-boot-starter-basic` | 6.0.0 | Activiti标准starter |
| `activiti-engine-picc` | 6.0.0 | PICC定制版，解决GaussDB字段不匹配 |

```java
【配置示例 - ActivitiDatasourceConfig.java】
@Configuration
public class ActivitiDatasourceConfig extends AbstractProcessEngineAutoConfiguration {
    @Bean
    public SpringProcessEngineConfiguration springProcessEngineConfiguration(
            SpringAsyncExecutor springAsyncExecutor) {
        // 使用PICC定制版引擎，兼容GaussDB
        SpringProcessEngineConfiguration spc = baseSpringProcessEngineConfiguration(...);
        spc.setIdGenerator(activitiIdGenerator); // 自定义ID生成器
        return spc;
    }
}
```

### 2.5 缓存与数据库

```xml
【Redis配置】
org.redisson:redisson:3.13.4
├── 单机模式：redis://host:port
└── 哨兵模式：支持主从自动切换

【数据库连接池】
com.alibaba:druid:1.0.11
├── 监控统计
├── SQL防火墙  
└── 连接池管理
```

---

## 三、Spring Boot配置解析

### 3.1 bootstrap.yml - 启动配置

```yaml
server:
  port: 9091  # 服务端口

spring:
  application:
    name: picc-mzmtb-server  # 应用名称

apollo:
  bootstrap:
    enabled: true           # 启用Apollo配置
    eagerLoad:
      enabled: true         # 启动阶段加载配置
```

> 💡 **小白理解**：bootstrap.yml是"提前加载"的配置，在Spring容器启动前就准备好，就像"程序还没开门，先把钥匙和服务台准备好"。

### 3.2 application.yml - 主配置

```yaml
server:
  port: 9091

spring:
  profiles:
    active: dev  # 激活dev环境配置

apollo:
  bootstrap:
    enabled: true
    eagerLoad:
      enabled: true
```

### 3.3 多环境配置

| 环境 | namespace | Apollo Meta Server | 用途 |
|-----|-----------|-------------------|------|
| **dev** | application-local.properties | 10.57.16.41:8080 | 本地开发 |
| **sit** | application-local.properties | (本地) | 集成测试 |
| **test** | application.properties | 测试环境 | 测试环境 |
| **uat** | application.properties | UAT环境 | 用户验收 |
| **prod** | application.properties | 10.34.80.145:8080 | 生产环境 |

```yaml
# dev环境配置示例
apollo:
  meta: http://10.57.16.41:8080
  namespaces: application-local.properties

# prod环境配置示例  
apollo:
  meta: http://10.34.80.145:8080  # 生产环境-北中心
  namespaces: application.properties
```

### 3.4 数据源配置(Apollo管理)

```
【Apollo配置的典型项】
├── spring.datasource.*     # 数据库连接配置
├── spring.redis.*          # Redis连接配置
├── logging.level.*         # 日志级别
└── 自定义业务参数
```

> ⚠️ **脱敏说明**：实际数据库密码、Redis密码等敏感信息存储在Apollo配置中心，本文档不展示。

---

## 四、Activiti工作流集成

### 4.1 工作流引擎架构

```
┌─────────────────────────────────────────────────────────┐
│                    Activiti 6.0.0                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ 流程设计器   │  │  运行时引擎  │  │  历史数据    │   │
│  │ (BPMN文件)  │──▶│ (ProcessEngine)│──▶│ (HistoryService)│ │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
    流程定义文件          流程实例              审批记录
   (bpmn文件)           (RUNNING)            (COMPLETED)
```

### 4.2 流程定义文件清单

| BPMN文件 | 流程名称 | 适用地市 |
|---------|---------|---------|
| bjmbsb.bpmn | 宝鸡慢病申报流程 | 宝鸡 |
| jcmbsb.bpmn | 晋城慢病申报流程 | 晋城 |
| ylmbsb.bpmn | 榆林慢病申报流程 | 榆林 |
| yambsb.bpmn | 延安慢病申报流程 | 延安 |
| jjmbsb.bpmn | 九江慢病申报流程 | 九江 |
| slmbsb.bpmn | 省略... | 省略 |
| dizmbsb.bpmn | 省略... | 省略 |
| mzlmbsb.bpmn | 省略... | 省略 |
| xyambsb.bpmn | 省略... | 省略 |
| zjkmbsb.bpmn | 省略... | 省略 |
| bjmbfs.bpmn | 宝鸡慢病发票流程 | 宝鸡 |

### 4.3 典型流程示例 - 宝鸡慢病申报

```xml
<!-- bjmbsb.bpmn 核心节点 -->
<process id="bjmbsb" name="宝鸡慢病申报流程">
    <startEvent id="startevent1" name="Start"/>
    
    <!-- 申报入口分支 -->
    <exclusiveGateway id="exclusivegateway1"/>  <!-- 线上/线下/导入 -->
    <userTask id="W1001" name="线上申报"/>
    <userTask id="W1002" name="线下申报"/>
    <userTask id="W6001" name="线下人员导入"/>
    
    <!-- 审批流程 -->
    <userTask id="W2001" name="初审管理"/>
    <userTask id="W3001" name="慢病体检"/>
    <userTask id="W4001" name="专家审核"/>
    
    <!-- 发卡流程 -->
    <userTask id="W6002" name="发卡确认"/>
    <userTask id="W6003" name="慢病发卡"/>
    <userTask id="W6004" name="慢病卡激活"/>
    
    <endEvent id="endevent1" name="End"/>
</process>

<!-- 流程分支条件示例 -->
<sequenceFlow>
    <conditionExpression xsi:type="tFormalExpression">
        ${firstApproveFlag==0}  <!-- 初审通过 -->
    </conditionExpression>
</sequenceFlow>
```

### 4.4 工作流与业务交互

```java
【Activiti服务调用示例】
// 通过Spring注入Activiti服务
@Autowired
private RuntimeService runtimeService;
@Autowired
private TaskService taskService;
@Autowired
private HistoryService historyService;

// 启动流程实例
ProcessInstance processInstance = runtimeService
    .startProcessInstanceByKey("bjmbsb", variables);

// 完成任务
taskService.complete(taskId, variables);

// 查询流程历史
HistoricActivityInstanceQuery query = historyService
    .createHistoricActivityInstanceQuery();
```

> 💡 **小白理解**：工作流就像医院的"挂号→分诊→就诊→检查→取药→出院"流程，每个节点有不同的人负责。

---

## 五、地市差异化机制（mtb-yh）

### 5.1 模块架构

```
mtb-yh (慢病优化父模块)
├── mtb-base (基础包 - 674个文件)
│   ├── 公共Service
│   ├── 公共Mapper
│   ├── 公共常量
│   └── 公共工具类
│
├── mtb-bj (宝鸡特化)
├── mtb-dz (德州特化)
├── mtb-jc (晋城特化)
├── mtb-jj (九江特化)
├── mtb-mzl (眉县/陇县特化)
├── mtb-ya (延安特化)
├── mtb-yl (榆林特化)
├── mtb-yli (榆林独立特化)
├── mtb-sl (省略)
├── mtb-xya (省略)
└── mtb-dez (省略)
```

### 5.2 地市识别机制

```java
【FlagInterceptorConfig - 地市Flag拦截器】
@Configuration
public class FlagInterceptorConfig implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response) {
        // 从请求头获取flag，识别地市
        String flag = request.getHeader(RequestConstant.HEAD_FLAG);
        
        // 存入ThreadLocal，供后续代码使用
        FlagLocal flagLocal = new FlagLocal();
        flagLocal.setFlag(flag);
        flagLocal.setUnitCode(UnitConfigEnum.fromFlag(flag).getTopUnitCode());
        FlagUtils.setFlagLocal(flagLocal);
        
        return true;
    }
}
```

### 5.3 地市特化实现方式

```java
【方式一：继承+重写】
public class BjDeclareServiceImpl extends BaseDeclareServiceImpl {
    @Override
    public void specialLogic() {
        // 宝鸡特有的业务逻辑
    }
}

【方式二：@ConditionalOnProperty】
@ConditionalOnProperty(name = "city.code", havingValue = "BJ")
public class BjSpecificService implements CityService {
    // 只有宝鸡环境才会加载
}

【方式三：SPI机制】
// META-INF/services 配置
com.picchealth.CityService=com.picchealth.bj.BjServiceImpl
```

### 5.4 新地市接入流程

```
【新地市接入步骤】
1. 在mtb-yh/pom.xml新增模块
   <module>mtb-xx</module>  <!-- xx为新地市代码 -->

2. 创建模块目录
   mtb-yh/mtb-xx/
   ├── pom.xml
   └── src/main/java/...

3. 继承或引用mtb-base
   <parent>mtb-yh</parent>
   <dependency>
       <groupId>com.picchealth</groupId>
       <artifactId>mtb-base</artifactId>
   </dependency>

4. 在picchealth-server/pom.xml添加依赖
   <dependency>
       <groupId>com.picchealth</groupId>
       <artifactId>mtb-xx</artifactId>
   </dependency>

5. 实现地市特有流程
   - 继承公共Service，重写差异化方法
   - 或新增BPMN流程文件

6. 配置地市Flag识别规则
```

---

## 六、安全配置

### 6.1 拦截器链

```
【请求拦截链 - MvcInterceptorConfig】
┌─────────────────────────────────────────────────────────────┐
│                    请求入口                                  │
└─────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│TokenInterceptor│  │FlagInterceptor │  │XcxInterceptor │
│  (Token验证)  │  │  (地市识别)   │  │(小程序签名)   │
└───────────────┘  └───────────────┘  └───────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               InterfaceGrantHandler                          │
│                   (接口授权认证)                              │
│         校验 syscode + password                              │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                    Controller处理
```

### 6.2 Token拦截器

```java
【TokenInterceptorConfig - 身份验证】
@Component
@CrossOrigin(origins = "*")
public class TokenInterceptorConfig implements HandlerInterceptor {
    
    @Value("${tokenInterceptFlag:false}")
    private boolean tokenInterceptFlag;  // 开发环境可关闭
    
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response) {
        // 1. 获取请求头中的Token
        String token = request.getHeader(RequestConstant.HEAD_TOKEN);
        String userId = request.getHeader(RequestConstant.HEAD_USERID);
        
        // 2. 从Redis查询用户信息
        User user = (User) redisUtil.get(RedisKeyConf.API_TOKEN + token);
        
        // 3. 验证通过，续期120分钟
        redisUtil.set(RedisKeyConf.API_TOKEN + token, user, 120);
        
        // 4. 存入上下文供后续使用
        UserUtils.setUser(user);
        
        return true;
    }
}
```

### 6.3 接口授权认证

```java
【InterfaceGrantHandler - 外部系统认证】
@Component
public class InterfaceGrantHandler extends HandlerInterceptorAdapter {
    
    // 外部系统接入需提供：系统编码 + 密码
    private static final String HEAD_SYSCODE = "syscode";
    private static final String HEAD_PICC = "password";
    
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response) {
        String syscode = request.getHeader(HEAD_SYSCODE);
        String password = request.getHeader(HEAD_PICC);
        
        // 校验系统授权
        VipOutsystem vipOutsystem = new VipOutsystem();
        vipOutsystem.setSyscode(syscode);
        vipOutsystem.setPassword(password);
        
        if (!outSystemCache.checkSystemAuthority(vipOutsystem)) {
            throw new BusinessException("100120", "非法认证系统！");
        }
        
        return true;
    }
}
```

### 6.4 跨域配置

```java
【CorsFilter配置 - MvcInterceptorConfig】
@Bean
public CorsFilter corsFilter() {
    CorsConfiguration config = new CorsConfiguration();
    config.addAllowedOrigin("*");        // 允许所有来源
    config.addAllowedMethod("*");        // 允许所有方法
    config.addAllowedHeader("*");        // 允许所有请求头
    // 注：生产环境应限制具体域名
    return new CorsFilter(configSource);
}
```

### 6.5 Redis会话管理

```java
【RedissonConfig - 分布式缓存配置】
@Configuration
public class RedissonConfig {
    
    @Bean
    public RedissonClient redissonClient() {
        Config config = new Config();
        
        // 模式一：单机模式
        if (StringUtils.isNotBlank(redisProperties.getHost())) {
            config.useSingleServer()
                .setAddress("redis://" + host + ":" + port)
                .setPassword(password)
                .setDatabase(database);
        } 
        // 模式二：哨兵模式(自动故障转移)
        else {
            config.useSentinelServers()
                .addSentinelAddress(nodes)
                .setMasterName(masterName)
                .setPassword(password);
        }
        
        return Redisson.create(config);
    }
}
```

---

## 七、定时任务

### 7.1 任务调度架构

```
┌─────────────────────────────────────────────────────────────┐
│                   SchedulingApi (REST接口)                   │
│                      /scheduling/*                          │
└─────────────────────────────────────────────────────────────┘
                           │ HTTP调用
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    定时任务组件 (@Component)                  │
├─────────────────────────────────────────────────────────────┤
│ 定时触发机制由外部调度系统(如XXL-JOB/Quartz)控制              │
│ 本服务提供任务执行入口，具体触发由运维平台配置                  │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 任务清单

| 任务类 | 任务名称 | 触发方式 |
|-------|---------|---------|
| **AccountEnableTask** | 账号失效自动处理 | 日间批处理 |
| **Approval2EndYlTask** | 审批结束YL任务 | 定时 |
| **BJAutoFilingTask** | 宝鸡自动归档任务 | 定时 |
| **BJDelFilingTask** | 宝鸡删除归档任务 | 定时 |
| **BJGXTTask** | 宝鸡国心通接口 | 定时 |
| **DrugSynchronizedTask** | 药品同步任务 | 定时 |
| **File2ImageTask** | 文件转图片任务 | 定时 |
| **GhiInsureDetailInitTask** | 医保明细初始化 | 定时 |
| **IcdExpiresTask** | ICD有效期检查 | 定时 |
| **MBCSZNHTask** | 慢病初审智能化任务 | 定时 |
| **MedicareResearchTask** | 医保查询任务 | 定时 |
| **ReviewWaringTask** | 复审预警任务 | 日执行 |
| **SlYearCheckTask** | 年度审核任务 | 定时 |
| **SlYearPostponeTask** | 年度延期任务 | 定时 |
| **SxMedicarePORResearchTask** | 陕西医保备案查询 | 定时 |
| **SxMedicarePutOnRecordTask** | 陕西医保备案任务 | 定时 |
| **VipAccountMoneyResetTask** | 账户金额重置 | 定时 |
| **VipMbAutoMaskTask** | 图片自动马赛克 | 按需 |
| **VipMbReviewGetPhysicalTask** | 复审体检获取 | 定时 |
| **VipMbmzStatusTask** | 慢病状态更新 | 定时 |
| **VipMbmzUpdateTask** | 慢病信息更新 | 定时 |
| **VipSendMessageTask** | 发送短信通知 | 定时 |
| **VipSendMessageJCTask** | 发送短信(JC) | 定时 |
| **WqxOutInterfaceTask** | 外区系统接口 | 定时 |

### 7.3 典型任务示例

```java
【复审预警任务 - ReviewWaringTask】
@Component("reviewWaringTask")
public class ReviewWaringTask {
    
    @Resource
    private VipReviewInfoService vipReviewInfoService;
    
    /**
     * 提取复审预警信息 - 每日执行一次
     * 由外部调度系统触发 /scheduling/reviewWaring
     */
    public void run() {
        try {
            // 获取即将到期需要复审的患者
            vipReviewInfoService.getReviews();
        } catch (Exception e) {
            log.error("提取复审预警信息时异常", e);
        }
    }
}

/* 调用方式：
 * POST /scheduling/reviewWaring
 * 触发频率：每日一次（建议凌晨2-4点执行）
 */
```

```java
【账号失效自动处理 - AccountEnableTask】
@Component("AccountEnableTask")
public class AccountEnableTask {
    
    public void updateEnable() {
        // 1. 查询长期未登录的特权账号
        List<PrivilegeUserInfo> list = privilegeUserInfoService.getEndLoginAccount();
        
        for (PrivilegeUserInfo info : list) {
            // 2. 设置账号失效
            info.setEnable(0);
            privilegeUserInfoService.save(info);
            
            // 3. 记录操作日志
            AccountRecord record = new AccountRecord();
            record.setReason("系统账号失效批处理");
            accountRecordService.save(record);
        }
        
        // 4. 处理UP_ORG_USER表中的账号
        List<UpOrgUser> userList = upOrgUserDao.getEndLoginAccount();
        // ...
    }
}
```

### 7.4 智能化初审任务(宝鸡)

```java
【MBCSZNHTask - 慢病初审智能化任务】
// 提供多种AI能力：
public void imageQualityRuleValidationTask(String orgCode);     // 图片质检规则校验
public void medicalImageClassificationTask(String orgCode);      // 医疗影像分类
public void micRuleValidationTask(String orgCode);              // 影像分类规则校验
public void idCardOcrTask(String orgCode);                       // 身份证OCR识别
public void sealRecognitionTask(String orgCode);                 // 印章识别
public void medicalInfoExtractionTask(String orgCode);           // 病案首页信息抽取

// 带分布式锁版本(推荐生产使用)
public void imageQualityRuleValidationTaskLock(String orgCode);
// ... 其他任务Lock版本
```

---

## 八、项目结构总览

```
picc-mzmtb-server/
├── pom.xml                          # 父POM
│
├── picchealth-db/                   # 数据库层模块
│   ├── src/main/java/
│   │   └── com/picchealth/
│   │       ├── module/
│   │       │   ├── basedoc/         # 基础文档
│   │       │   ├── mb/              # 慢病管理
│   │       │   ├── mtb/             # 慢特病
│   │       │   ├── publics/         # 公共
│   │       │   └── drugstore/        # 药店
│   │       └── dao/                 # 数据访问
│   └── src/main/resources/
│       └── mapper/                  # MyBatis XML (213个)
│
├── picchealth-server/               # 主服务模块
│   ├── pom.xml
│   └── src/main/
│       ├── java/com/picchealth/
│       │   ├── config/              # 配置类(17个)
│       │   ├── module/
│       │   │   ├── basedoc/         # 基础文档模块
│       │   │   ├── call/            # 服务调用模块
│       │   │   ├── dpview/          # 数据展示模块
│       │   │   ├── drugstore/       # 药店模块
│       │   │   ├── logaudit/        # 日志审计模块
│       │   │   ├── mb/              # 慢病申报模块(含Activiti)
│       │   │   ├── mtb/             # 慢特病核心模块
│       │   │   ├── restful/        # REST接口
│       │   │   ├── scheduling/      # 定时任务(26个任务)
│       │   │   ├── thirdfee/        # 第三方费用模块
│       │   │   └── webservice/      # WebService模块
│       │   └── Application.java    # 启动类
│       └── resources/
│           ├── application*.yml     # 多环境配置
│           ├── bootstrap.yml        # 启动配置
│           └── processes/           # BPMN流程文件(14个)
│
└── mtb-yh/                          # 地市差异化模块
    ├── pom.xml
    ├── mtb-base/                    # 基础包(674文件)
    ├── mtb-bj/                      # 宝鸡
    ├── mtb-dz/                      # 德州
    ├── mtb-jc/                      # 晋城
    ├── mtb-jj/                      # 九江
    ├── mtb-mzl/                     # 眉县/陇县
    ├── mtb-ya/                      # 延安
    ├── mtb-yl/                      # 榆林
    ├── mtb-yli/                     # 榆林(独立)
    ├── mtb-sl/                      # 省略
    ├── mtb-xya/                     # 省略
    ├── mtb-dez/                     # 省略
    └── mtb-hn/                      # 省略
```

---

## 九、关键配置类清单

| 配置类 | 职责 |
|-------|------|
| `ActivitiDatasourceConfig` | Activiti工作流数据源配置 |
| `ActivitiIdGenerator` | 工作流ID生成器 |
| `CommandLineRunnerImpl` | 启动时初始化缓存 |
| `InterfaceGrantHandler` | 外部系统接口授权 |
| `MvcInterceptorConfig` | 拦截器链+跨域配置 |
| `TokenInterceptorConfig` | Token身份验证 |
| `FlagInterceptorConfig` | 地市Flag拦截 |
| `XcxInterceptorConfig` | 小程序签名验证 |
| `RedissonConfig` | Redis连接配置 |
| `H5CorsRegistration` | H5跨域注册 |
| `ComCodeShardingConverter` | 机构代码分片转换 |
| `RediesCode` | Redis工具类 |
| `MyRequestWrapper` | 请求包装器 |

---

## 十、运维注意事项

### 10.1 部署前置条件

```bash
【依赖检查清单】
□ Java 8 已安装
□ Apollo配置中心已启动
□ Redis已启动(单机或哨兵)
□ GaussDB/MySQL已启动
□ BES应用服务器已配置(信创环境)
```

### 10.2 启动顺序

```
1. Apollo Config Service → 2. Apollo Portal → 
3. Redis → 4. GaussDB/MySQL → 5. picc-mzmtb-server
```

### 10.3 健康检查

```bash
# 端口检查
curl http://localhost:9091/actuator/health

# 接口测试
curl -H "flag:BJ" http://localhost:9091/picchealth/health
```

### 10.4 常见问题

| 问题 | 原因 | 解决方案 |
|-----|------|---------|
| 启动失败 | Apollo连接超时 | 检查网络和Meta Server |
| Token验证失败 | Redis未启动 | 启动Redis服务 |
| 流程启动失败 | GaussDB字段不匹配 | 使用activiti-engine-picc |
| 地市识别异常 | Flag未传或错误 | 检查请求头FLAG参数 |

---

📎 **延伸阅读**：
- [安全与代码质量审计](picc-mzmtb-server-安全与代码质量审计.md) - 33个问题详细分析，含8个P0紧急问题的问题分析
- [数据模型解析](picc-mzmtb-server-数据模型解析.md) - 213个Mapper XML对应的核心表和SQL分析
- [picc-mzmtb-user-教程文档.md](picc-mzmtb-user-教程文档.md) 📌(权限服务) - 权限管理服务的完整教程

**文档完**
