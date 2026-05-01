# PICC四项目日志体系与监控可观测性分析报告

> 📖 **文档版本**: v1.0  
> 📅 **生成日期**: 2025年1月  
> 👤 **目标读者**: 零基础运维/开发人员  
> 🔒 **敏感信息已脱敏处理**

---

## 📚 目录导航

1. [什么是日志和监控？——小白入门第一课](#什么是日志和监控)
2. [Part 1：Java日志框架分析](#part-1java日志框架分析)
3. [Part 2：业务日志审计](#part-2业务日志审计)
4. [Part 3：前端日志](#part-3前端日志)
5. [Part 4：监控体系评估](#part-4监控体系评估)
6. [Part 5：监控体系学习思考](#part-5监控体系学习思考)
7. [附录：快速查询手册](#附录快速查询手册)

---

# 🎓 什么是日志和监控？——小白入门第一课

## 1.1 日志基础概念（用生活比喻理解）

### 日志 = 系统的"行车记录仪"

想象一下，如果你的系统是一辆汽车，那日志就是这辆车的**行车记录仪**：

| 生活场景 | 对应日志概念 |
|---------|-------------|
| 行车记录仪24小时录像 | 系统运行时持续记录的日志 |
| 出了事故调取录像 | 问题排查时查看日志 |
| 录像能看清车牌、时间、地点 | 日志能看清时间、用户、操作 |
| 录像保存7天（或更长） | 日志滚动保留策略 |

### 日志级别 = 记事本的重要性标签

就像我们给笔记贴不同颜色的标签一样，日志也有"重要性等级"：

```
┌─────────────────────────────────────────────────────────────────────┐
│                          日志级别金字塔                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                         🔴 ERROR (最高)                             │
│                    "系统挂了！快来处理！"                            │
│                    例：数据库连接失败、OOM内存溢出                     │
│                                                                     │
│                        🟠 WARN (注意)                               │
│                  "有点不对劲，但还能跑"                              │
│                  例：配置文件缺失用默认值、连接池即将耗尽               │
│                                                                     │
│                         🟢 INFO (记录)                              │
│                    "日常运行情况，记录一下"                          │
│                    例：用户登录、方法调用开始/结束                     │
│                                                                     │
│                        🔵 DEBUG (调试)                              │
│                    "开发调试用，线上别开"                            │
│                    例：SQL语句、变量值、详细流程                      │
│                                                                     │
│                       ⚫ TRACE (最细)                               │
│                    "详细到不能再详细"                                │
│                    例：框架内部运行细节                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 滚动策略 = 记事本写满了换一本

就像我们的工作日志本：

```
📓 第一本日志（当前）
   ├── 1月1日-1月7日的记录
   └── 写到第100MB时 → 换新本

📚 归档日志架（历史）
   ├── 📕 1月第一周.log
   ├── 📗 12月第四周.log  
   ├── 📘 12月第三周.log
   └── ... (最多保留7本/7天)
   
🗑️ 定期清理
   └── 超过7天的旧日志 → 自动删除
```

## 1.2 监控基础概念

### 监控 = 医院的"体检中心"

| 医院体检 | 系统监控 |
|---------|---------|
| 体温计测体温 | 探测端点检查服务是否存活 |
| 心电图监控心跳 | Metrics指标监控性能 |
| 验血报告 | 日志分析 |
| 异常指标触发警报 | 告警通知 |
| 病历本记录历史 | 趋势图、大盘展示 |

### 关键监控指标

```
🫀 健康检查（心跳）
   └── /health → 返回 "I'm alive!"

📊 性能指标（体检数据）
   ├── QPS: 每秒处理多少请求
   ├── 响应时间: 请求从发起到返回要多久
   ├── 错误率: 100个请求有几个失败
   └── JVM内存: Java程序占用的内存

🔗 链路追踪（快递追踪）
   └── 用户请求 → 网关 → 权限服务 → 业务服务 → 数据库
       每个环节都有"快递单号"串联

🚨 告警（医院急诊）
   └── 体温>38.5℃ → 自动打电话给家属
       系统指标异常 → 自动发短信/邮件/钉钉通知
```

## 1.3 常用术语对照表

| 术语 | 小白解释 | 生活中的例子 |
|-----|---------|-------------|
| **ELK** | 超级档案室，收集+索引+查询 | 图书馆的自动借还系统 |
| **SkyWalking/Zipkin** | 快递追踪号，一个号查到底 | 快递100追踪 |
| **Apollo** | 配置中心，配置修改不用重启 | 电视遥控器调音量 |
| **XXL-Job** | 定时任务管理器 | 闹钟叫醒服务 |
| **Prometheus** | 指标收集器，专收集数字 | 银行ATM机的交易计数器 |
| **Actuator** | Spring Boot的健康体检医生 | 汽车的OBD诊断接口 |

---

# Part 1：Java日志框架分析

## 2.1 四个项目日志框架总览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PICC四项目日志框架架构图                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│   │  权限服务    │  │  业务服务    │  │  前台服务    │  │   前端      │      │
│   │  (User)     │  │  (Server)   │  │  (Gateway)  │  │  (Agent)    │      │
│   │  端口:9092  │  │  端口:9091  │  │  端口:9001  │  │  Vue 2      │      │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘      │
│          │                 │                 │                 │            │
│          ▼                 ▼                 ▼                 ▼            │
│   ┌─────────────────────────────────────────────────────────────┐           │
│   │                    统一日志框架: Logback + SLF4J           │           │
│   │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐ │           │
│   │  │ Logback   │  │ SLF4J API │  │ Logstash  │  │SkyWalking │ │           │
│   │  │ 核心实现  │  │   接口    │  │ JSON输出  │  │ 链路追踪  │ │           │
│   │  └───────────┘  └───────────┘  └───────────┘  └───────────┘ │           │
│   └─────────────────────────────────────────────────────────────┘           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 框架依赖分析

| 项目 | 日志框架 | 版本 | 说明 |
|-----|---------|-----|------|
| 权限服务 | Logback + SLF4J | 1.x | 标准Spring Boot日志方案 |
| 业务服务 | Logback + SLF4J | 1.x | 与权限服务一致 |
| 前台服务 | Logback + SLF4J | 1.x | 与权限服务一致 |
| 前端 | Console API | - | 原生JS日志 |

### 依赖库详情

```xml
<!-- Logback 日志框架 -->
<dependency>
    <groupId>ch.qos.logback</groupId>
    <artifactId>logback-classic</artifactId>
    <version>1.x</version>
</dependency>

<!-- SLF4J 日志接口 -->
<dependency>
    <groupId>org.slf4j</groupId>
    <artifactId>slf4j-api</artifactId>
    <version>1.x</version>
</dependency>

<!-- Logstash JSON格式输出（用于ELK） -->
<dependency>
    <groupId>net.logstash.logback</groupId>
    <artifactId>logstash-logback-encoder</artifactId>
    <version>5.3</version>
</dependency>

<!-- Log4j2 API（桥接到SLF4J） -->
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-to-slf4j</artifactId>
    <version>2.15.0</version>
</dependency>
```

## 2.2 配置文件详细分析

### 2.2.1 日志配置文件位置

```
项目根目录
├── picchealth-privilege-server/     # 权限服务
│   └── src/main/resources/
│       └── logback-spring.xml       # 日志配置
├── picchealth-server/              # 业务服务
│   └── src/main/resources/
│       ├── logback-spring.xml      # 主配置
│       └── dev/
│           ├── logback-dev.xml      # 开发环境
│           ├── logback-prd.xml     # 生产环境
│           └── logback-sit.xml      # 测试环境
├── picchealth-gateway/             # 前台服务
│   └── src/main/resources/
│       └── logback-spring.xml      # 日志配置
```

### 2.2.2 核心配置项解读

#### 🔧 配置基础参数

```xml
<!-- 配置文件监控：开启后修改配置不用重启 -->
<configuration scan="true" scanPeriod="60 seconds" debug="false">
    
    <!-- 自定义转换规则：获取主机名/IP -->
    <conversionRule conversionWord="hostname_ip" 
                    converterClass="pdfc.framework.aop.log.util.LogIP"/>
    
    <!-- 自定义转换规则：获取端口 -->
    <conversionRule conversionWord="port" 
                    converterClass="pdfc.framework.aop.log.util.LogPort"/>
```

**小白解读**：
- `scan="true"`: 日志配置文件修改后，60秒内自动重新加载
- `hostname_ip`: 自动获取部署服务器的主机名和IP地址
- `port`: 自动获取服务监听的端口号

#### 📁 日志路径配置

```xml
<!-- PaaS平台日志路径 -->
<property name="LOG_HOME" value="/data/log/app"/>
<!-- 日志文件名格式：服务名-主机名-端口 -->
<property name="LOG_FILENAME" value="${springAppName}-${HOSTNAME}-${springAppPort}"/>

<!-- NAS存储日志路径（长期归档） -->
<property name="LOG_FILE" value="/data/logs/path"/>
<property name="LOG_PREFIX" value="${springAppName}"/>
```

**小白解读**：
```
实际生成的日志文件示例：
/data/log/app/sys_log-picc-mzmtb-server-webserver-9091.log
                │        │         │         │
                │        │         │         └── 端口号
                │        │         └── 主机名
                │        └── 服务名
                └── 日志类型(syslog/aoplog/interface/error)
```

#### 📜 滚动策略配置

```xml
<!-- 滚动文件名格式：带日期和序号 -->
<property name="FILE_NAME_PATTERN_SUFFIX" 
          value="${LOG_FILENAME}-%d{yyyyMMdd}.log.%i"/>

<!-- 单文件最大100MB -->
<property name="MAX_FILE_SIZE" value="100MB"/>

<!-- PaaS本地保留7天 -->
<property name="MAX_HISTORY" value="7"/>

<!-- 总大小上限500MB，超出则删除旧日志 -->
<property name="TOTAL_SIZE_CAP" value="500MB"/>
```

**滚动流程图解**：

```
时间轴 ──────────────────────────────────────────────────────►

第1天: sys_log-xxx.log ──────► (写满100MB) ──► sys_log-xxx.log.1
                                      │
第2天: sys_log-xxx.log ──────► (写满100MB) ──► sys_log-xxx.log.2
                                      │
第3天: sys_log-xxx.log ──────► (写满100MB) ──► sys_log-xxx.log.3
                                      │
                                     ...
                                      │
第7天: sys_log-xxx.log ──────► (写满100MB) ──► sys_log-xxx.log.7
                                      │
第8天: sys_log-xxx.log ──────►  sys_log-xxx.log.1 被删除
                                      │
第9天: sys_log-xxx.log ──────►  sys_log-xxx.log.2 被删除
```

## 2.3 四种日志输出详解

### 📋 SYSLOG - 系统日志（综合日志）

**用途**：记录所有系统级日志，包括框架运行信息

**输出格式**：
```
[%d{yyyy-MM-dd HH:mm:ss.SSS}]  时间戳
[%thread]                       线程名
[%-5level]                       日志级别
[%tid]                           线程ID
[%hostname_ip]                   主机IP
[%property{springAppName}]       服务名
[%logger{50}]                    类名(截取50字符)
[%X{pGlobalTraceId}]             全局追踪ID
[%X{pParentTraceId}]             父追踪ID
[%X{pLocalTraceId}]              本地追踪ID
[%msg]                           消息内容
```

**实际输出示例**：
```log
[2025-01-15 10:30:25.123] [http-nio-9091-exec-5] [INFO ] [TID-12345] [192.168.1.100] [picc-mzmtb-server] [c.p.c.UserService] [GID-abc123] [PID-xyz789] [LID-def456] 用户登录成功: userId=10001
```

### 🎯 AOPLOG - AOP切面日志（业务操作日志）

**用途**：记录方法级别的业务操作，用于审计

**输出格式**：
```
[%d{yyyy-MM-dd HH:mm:ss.SSS}]  时间戳
[%thread]                       线程名
[%level]                         日志级别
[%tid]                           线程ID
[%hostname_ip]                   主机IP
%msg                             业务消息
```

**记录内容**：
```java
// 包含的字段信息
msg格式: [微服务IP:端口] [微服务名称] [操作用户] [方法URL] 
         [业务含义] [方法耗时] [处理开始时间] [客户端IP] 
         [全局ID] [父ID] [本地ID]
```

**实际输出示例**：
```log
[2025-01-15 10:30:25.123] [http-nio-9091-exec-5] [INFO] [TID-12345] [192.168.1.100] 
    [微服务:192.168.1.100:9091] 
    [服务名:picc-mzmtb-server] 
    [操作用户:张三] 
    [方法:/mb/api/queryUserInfo] 
    [业务:查询用户信息] 
    [耗时:25ms] 
    [开始时间:2025-01-15 10:30:25] 
    [客户端IP:10.0.0.50]
```

### 🔌 INTERFACE - 接口日志（服务间调用）

**用途**：记录微服务之间的HTTP调用

**输出格式**：
```
[%d{yyyy-MM-dd HH:mm:ss.SSS}]  时间戳
[%X{pGlobalTraceId}]             全局追踪ID
[%X{pParentTraceId}]             父追踪ID
[%X{pLocalTraceId}]              本地追踪ID
[%thread]                       线程名
[%level]                         日志级别
[%tid]                           线程ID
[%hostname_ip]                   主机IP
%msg                             调用详情
```

**记录内容**：
```java
msg格式: [微服务IP:端口] [提供方服务] [请求方服务] [客户端IP] 
         [终端类型] [终端信息] [操作用户] [方法URL] 
         [开始时间] [耗时] [执行状态] [请求报文] [响应报文]
```

### ⚠️ ERROR - 错误日志

**用途**：专门记录ERROR级别的异常信息

**输出格式**：
```
[%d{yyyy-MM-dd HH:mm:ss.SSS}]  时间戳
[%thread]                       线程名
[%level]                         日志级别(固定ERROR)
[%tid]                           线程ID
[%hostname_ip]                   主机IP
%msg                             错误详情
```

**注意**：只捕获**未捕获的运行时异常**，如果代码用try-catch处理了，错误日志可能不会输出

## 2.4 日志级别配置

### 🏷️ Logger配置详情

```xml
<!-- tk.mybatis框架：降低日志级别，避免刷屏 -->
<logger name="tk.mybatis.mapper" level="warn"/>

<!-- 业务代码：INFO级别 -->
<logger name="com.picchealth.module" level="info"/>

<!-- 配置类：DEBUG级别（开发调试用） -->
<logger name="com.picchealth.config" level="debug"/>

<!-- Apollo配置中心：WARN级别 -->
<logger name="com.ctrip.framework.apollo" level="warn" additivity="false"/>

<!-- Netflix服务发现：WARN级别 -->
<logger name="com.netflix.discovery" level="warn" additivity="false"/>

<!-- 分片框架：WARN级别 -->
<logger name="pdfc.framework.sharding" level="warn" additivity="false"/>

<!-- 根日志：INFO级别 -->
<root level="INFO">
    <appender-ref ref="STDOUT"/>           <!-- 控制台输出 -->
    <appender-ref ref="ASYNC-SYSLOG"/>     <!-- 异步系统日志 -->
    <appender-ref ref="ASYNC-SYSLOG-NAS"/> <!-- 异步NAS日志 -->
</root>
```

### 📊 级别继承关系

```
root (INFO)
  │
  ├── com.picchealth.module (INFO) ────► 继承root，输出INFO及以上
  │     ├── com.picchealth.module.mb (INFO) ────► 继承module
  │     └── com.picchealth.module.mtb (INFO) ────► 继承module
  │
  ├── com.picchealth.config (DEBUG) ────► 自定义，输出DEBUG及以上
  │     └── 任何子包都继承DEBUG
  │
  ├── tk.mybatis.mapper (WARN) ────► 自定义，输出WARN及以上
  │
  └── com.ctrip.framework.apollo (WARN, additivity=false)
                                      ────► 独立，不向上传递
```

## 2.5 异步日志配置

### ⚡ 异步Appender配置

```xml
<!-- 异步系统日志 -->
<appender name="ASYNC-SYSLOG" class="ch.qos.logback.classic.AsyncAppender">
    <!-- 队列满了直接丢弃（0=不丢弃任何日志） -->
    <discardingThreshold>0</discardingThreshold>
    <!-- 队列大小256条 -->
    <queueSize>256</queueSize>
    <!-- 引用同步Appender -->
    <appender-ref ref="SYSLOG"/>
</appender>
```

### 🔄 异步工作原理

```
同步模式:
  日志输出 ──► 写入文件 ──► 返回
  (阻塞等待)

异步模式:
  日志输出 ──► 放入队列 ──► 立即返回
                │
                ▼
            后台线程
                │
                ▼
            写入文件
```

### 📈 异步配置对比

| 配置项 | PaaS本地 | NAS存储 |
|-------|---------|--------|
| discardingThreshold | 0（不丢弃） | 0（不丢弃） |
| queueSize | 256 | 256 |
| maxHistory | 7天 | 180天 |
| totalSizeCap | 500MB | 500MB |
| cleanHistoryOnStart | true | false |

## 2.6 四个项目配置差异分析

### 项目间对比表

| 配置项 | 权限服务 | 业务服务 | 前台服务 |
|-------|---------|---------|---------|
| 配置文件 | logback-spring.xml | logback-spring.xml + dev/*.xml | logback-spring.xml |
| 服务名 | picc-mzmtb-user | picc-mzmtb-server | picc-mzmtb-server |
| 端口 | 9092 | 9091 | 9001 |
| 日志路径 | /data/log/app | /data/log/app | /data/log/app |
| 模块日志级别 | com.picchealth.module=info | com.picchealth.module=info | com.picchealth.module=info |
| 配置日志级别 | com.picchealth.config=debug | com.picchealth.config=debug | com.picchealth.config=debug |
| Apollo日志级别 | warn | warn | warn |

### ✅ 配置一致性评价

| 评估维度 | 评分 | 说明 |
|---------|-----|------|
| 框架统一性 | ⭐⭐⭐⭐⭐ | 三个Java项目完全一致 |
| 滚动策略统一 | ⭐⭐⭐⭐⭐ | 统一使用100MB/7天 |
| 异步配置统一 | ⭐⭐⭐⭐⭐ | 队列大小一致 |
| 格式统一性 | ⭐⭐⭐⭐⭐ | 日志格式完全一致 |

---

# Part 2：业务日志审计

## 3.1 审计日志概述

### 🎯 什么是业务审计日志？

**审计日志 = 重要操作的"记账本"**

就像财务记账一样，审计日志记录了"谁在什么时间做了什么操作"：

```
┌─────────────────────────────────────────────────────────────────┐
│                     审计日志记账本                               │
├─────────────────────────────────────────────────────────────────┤
│ 日期: 2025-01-15                                                │
│ ════════════════════════════════════════════════════════════    │
│ 10:30:25  张三  登录系统                                        │
│ 10:31:00  张三  查询用户列表                                     │
│ 10:35:10  张三  新增用户"李四"                                  │
│ 10:40:00  张三  修改用户权限                                     │
│ 10:45:00  王五  删除用户"赵六"                                  │
│ 11:00:00  张三  登出系统                                        │
└─────────────────────────────────────────────────────────────────┘
```

## 3.2 审计日志实现机制

### 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                    AOP审计日志架构                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   用户请求                                                       │
│      │                                                          │
│      ▼                                                          │
│   ┌─────────────────────┐                                       │
│   │   LogAudit 切面     │ ◄── Spring AOP 拦截                   │
│   │  @Aspect @Component │                                       │
│   └──────────┬──────────┘                                       │
│              │                                                  │
│              ▼                                                  │
│   ┌─────────────────────┐                                       │
│   │  MethodNameKeyWords │ ◄── 关键字匹配引擎                    │
│   │  关键词列表配置      │                                       │
│   └──────────┬──────────┘                                       │
│              │                                                  │
│              ▼                                                  │
│   ┌─────────────────────┐                                       │
│   │   LogRecordInfoDao  │ ◄── MyBatis DAO                       │
│   │   插入日志到数据库    │                                       │
│   └──────────┬──────────┘                                       │
│              │                                                  │
│              ▼                                                  │
│   ┌─────────────────────┐                                       │
│   │   log_record_info   │ ◄── MySQL数据库表                      │
│   │   日志记录表         │                                       │
│   └─────────────────────┘                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📝 审计切面代码解析

```java
@Aspect
@Component
@Slf4j
public class LogAudit {
    
    // 拦截规则：com.picchealth.module.mb.api 和 mtb.api 下的所有方法
    @Pointcut("execution(* com.picchealth.module.mb.api.*.*(..)) || " +
              "execution(* com.picchealth.module.mtb.api.*.*(..))")
    public void pointCut() {}
    
    @Around("pointCut()")
    public Object printLog(ProceedingJoinPoint joinPoint) throws Throwable {
        // 1. 获取方法信息
        MethodSignature signature = (MethodSignature) joinPoint.getSignature();
        Method method = signature.getMethod();
        
        // 2. 获取当前登录用户
        User user = UserUtils.getUser();
        
        // 3. 关键字匹配判断操作类型
        List<String> mathchRes = pathMatch(method.getName());
        
        // 4. 记录审计日志
        if (CollectionUtils.isNotEmpty(mathchRes)) {
            LogRecordInfo logRecordInfo = new LogRecordInfo();
            logRecordInfo.setUrl(method.getDeclaringClass().getName() + "/" + method.getName());
            logRecordInfo.setUserName(user.getUserName());
            logRecordInfo.setOperateType(operateType);
            logRecordInfo.setCreatetime(LocalDateTime.now());
            logRecordInfoDao.insert(logRecordInfo);
        }
        
        // 5. 执行目标方法
        Object result = joinPoint.proceed();
        return result;
    }
}
```

## 3.3 操作类型识别

### 🔍 关键字匹配表

| 操作类型 | 关键字列表 | 示例方法 |
|---------|----------|---------|
| **新增/INSERT** | add, save, insert, import, edit, declare, accept, reject, regist, merge, allocat, rollback, book, determine, trad, sync | saveUser(), addOrder(), importData() |
| **删除/DELETE** | delete, stop, filingback | deleteUser(), stopService() |
| **修改/UPDATE** | update, reset, assign, giveup, withdraw, revert | updatePassword(), resetStatus() |
| **登录/LOGIN** | login | webLogin(), appLogin() |
| **登出/LOGOUT** | loginout | logout(), exitSystem() |
| **上传/UPLOAD** | upload, importmbfile | uploadFile(), importExcel() |
| **下载/DOWNLOAD** | download, imagefile | downloadReport(), exportImage() |

### 🔄 匹配流程图

```
方法名: queryUserById
    │
    ▼
转小写: queryuserbyid
    │
    ▼
遍历关键字列表:
    │
    ├─► add      ──► 不匹配
    ├─► delete   ──► 不匹配
    ├─► update   ──► 不匹配
    ├─► login    ──► 不匹配
    ├─► query    ──► ✅ 匹配!
    │                操作类型 = "query"
    │
    └─► 其他...   ──► 不匹配
```

## 3.4 审计日志数据库表设计

### 📊 LogRecordInfo表结构

```sql
CREATE TABLE log_record_info (
    id VARCHAR(32) PRIMARY KEY,           -- UUID主键
    host VARCHAR(50),                     -- 服务器IP
    url VARCHAR(200),                     -- 请求URL/方法路径
    user_name VARCHAR(100),               -- 用户名
    user_info VARCHAR(500),               -- 用户详细信息（可包含多个字段拼接）
    operate_type VARCHAR(50),              -- 操作类型（login/logout/insert/update/delete/query等）
    method_name VARCHAR(100),             -- 方法名
    creator VARCHAR(50),                   -- 创建者
    create_time DATETIME,                 -- 创建时间
    update_time DATETIME,                 -- 更新时间
    update_person VARCHAR(50)             -- 更新人
);

-- 索引设计
CREATE INDEX idx_url ON log_record_info(url);
CREATE INDEX idx_user_name ON log_record_info(user_name);
CREATE INDEX idx_operate_type ON log_record_info(operate_type);
CREATE INDEX idx_create_time ON log_record_info(create_time);
```

### 📊 LogBury表结构（用户行为埋点）

```sql
CREATE TABLE t_log_bury (
    id VARCHAR(32) PRIMARY KEY,
    is_login VARCHAR(10),                 -- 是否登录（0:匿名 1:已登录）
    flag VARCHAR(50),                     -- 地区标识
    mobile VARCHAR(20),                   -- 手机号
    id_card VARCHAR(20),                  -- 身份证号
    bury_type VARCHAR(50),                -- 大模块类型
    bury_code VARCHAR(50),               -- 小模块编码
    bury_time INT,                        -- 点击次数
    open_id VARCHAR(100),                 -- 微信OpenId
    create_time DATETIME,
    update_time DATETIME
);
```

## 3.5 登录日志特殊处理

### 🔑 登录日志记录

```java
@Override
public void addLog() {
    User user = UserUtils.getUser();
    LogRecordInfo logRecordInfo = new LogRecordInfo();
    logRecordInfo.setUserInfo(integrateParam(user.getUserId(), user.getUserName(), 
                                              user.getUserName(), user.getOrgName(), 
                                              user.getOrgId(), user.getOrgCode()));
    logRecordInfo.setUserName(user.getUserName());
    logRecordInfo.setUrl("auth_server_web_login");
    logRecordInfo.setMethodName("web_login");
    logRecordInfo.setCreatetime(LocalDateTime.now());
    logRecordInfo.setCreator("server");
    logRecordInfo.setId(generateUUID());
    logRecordInfo.setOperateType("login");
    logRecordInfo.setHost(getHostAddr());
    logRecordInfoDao.insert(logRecordInfo);
}
```

## 3.6 审计日志查询

### 🔍 查询条件支持

| 查询条件 | 说明 | SQL片段 |
|---------|------|--------|
| url | 方法路径精确匹配 | `url = #{url}` |
| userName | 用户名精确匹配 | `user_name = #{userName}` |
| operateType | 操作类型列表 | `operate_type IN (...)` |
| host | 服务器IP | `host = #{host}` |
| methodName | 方法名模糊匹配 | `method_name LIKE #{methodName}` |
| beginDateTime | 开始时间 | `create_time >= #{beginDateTime}` |
| endDateTime | 结束时间 | `create_time <= #{endDateTime}` |

### 📋 日志查询示例

```java
// 按时间范围查询
LogQueryVo queryVo = new LogQueryVo();
queryVo.setCountStartTime("2025-01-01 00:00:00");
queryVo.setCountEndTime("2025-01-15 23:59:59");

// 按操作类型查询
queryVo.setOperateType(Arrays.asList("login", "logout", "insert", "update", "delete"));

// 按用户名查询
queryVo.setUserName("张三");

// 分页查询
PageHelper.startPage(1, 20);
List<LogRecordInfo> logs = logRecordInfoDao.logQuery(logAuditInfoDto);
```

## 3.7 审计日志覆盖评估

### ✅ 已覆盖场景

| 场景 | 覆盖状态 | 说明 |
|-----|---------|------|
| 用户登录 | ✅ 已覆盖 | 通过login关键字匹配 |
| 用户登出 | ✅ 已覆盖 | 通过loginout关键字匹配 |
| 数据新增 | ✅ 已覆盖 | 通过add/save/insert等关键字匹配 |
| 数据修改 | ✅ 已覆盖 | 通过update关键字匹配 |
| 数据删除 | ✅ 已覆盖 | 通过delete关键字匹配 |
| 文件上传 | ✅ 已覆盖 | 通过upload关键字匹配 |
| 文件下载 | ✅ 已覆盖 | 通过download关键字匹配 |
| 审批操作 | ✅ 已覆盖 | 通过accept/reject/refuse关键字匹配 |

### ⚠️ 待改进场景

| 场景 | 风险等级 | 建议 |
|-----|---------|------|
| 敏感数据查询 | 中 | 查询操作目前未记录详细内容 |
| 导出操作 | 低 | 只记录方法调用，未记录导出数据量 |
| 定时任务执行 | 低 | 批处理任务缺少执行记录 |
| 外部接口调用 | 中 | 未记录第三方调用详情 |

---

# Part 3：前端日志

## 4.1 前端日志现状分析

### 📊 console.log 残留统计

```
┌─────────────────────────────────────────────────────────────────┐
│                    前端console.log统计                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   📁 统计范围: /src目录下所有.vue和.js文件                       │
│   📝 匹配规则: console.log/console.error/console.warn/console.info│
│   🔢 统计结果: 99处残留                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📋 残留分布统计

| 类型 | 数量 | 占比 | 示例 |
|-----|-----|-----|------|
| console.log | ~85 | 86% | `console.log('弹窗已关闭')` |
| console.error | ~8 | 8% | `console.error('删除用户失败:', error)` |
| console.warn | ~4 | 4% | `console.warn('姓名解密失败:', item.name)` |
| console.info | ~2 | 2% | 其他调试信息 |

### 📁 残留文件分布

```
前端源码目录 (/src)
├── pages/
│   ├── YLChronicDis/         # 约10处
│   ├── XYaChronicDis/        # 约25处
│   ├── ChronicDis/           # 约15处
│   ├── YAChronicDis/         # 约12处
│   ├── YaLChronicDis/        # 约8处
│   └── SLChronicDis/         # 约7处
├── mtbnewcomponents/
│   └── recordImport/          # 约5处
└── 其他目录                   # 约17处
```

### 🔍 典型问题代码示例

```javascript
// ❌ 问题1: 生产环境不应存在的调试代码
presentry(val,num,ids){
    console.log('弹窗已关闭');  // 无实际意义
}

// ❌ 问题2: 捕获错误后只打印未处理
.catch(error => {
    console.error('删除用户失败:', error);
    // 缺少用户友好的错误提示
});

// ❌ 问题3: 敏感信息输出
.catch(error => {
    console.warn('姓名解密失败:', item.name);
    // item.name可能是身份证号等敏感信息
});

// ❌ 问题4: 调试后未清理
params => {
    console.log("params",params);  // 生产环境应删除
}
```

## 4.2 前端错误处理现状

### 📝 main.js配置

```javascript
// main.js 第X行
Vue.config.productionTip = false;  // 生产环境禁用提示
// Vue.config.devtools = false;     // 开发工具（已注释）
```

### ⚠️ 存在的问题

| 问题 | 严重程度 | 影响 |
|-----|---------|------|
| 无全局错误处理 | 中 | 未捕获的Promise错误无法感知 |
| 无错误上报机制 | 高 | 浏览器控制台错误无法收集 |
| 无前端监控SDK | 高 | 缺少Sentry等错误监控 |
| console.log残留99处 | 低 | 生产环境日志泄露信息 |

### 🚫 缺少的前端监控能力

```
┌─────────────────────────────────────────────────────────────────┐
│                    前端可观测性能力矩阵                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   能力项                    现状          建议方案               │
│   ─────────────────────────────────────────────────────────   │
│   ✅ JavaScript错误监控      未实现        Sentry               │
│   ❌ Promise异常监控         未实现        Sentry               │
│   ❌ 资源加载失败监控        未实现        Sentry               │
│   ❌ 页面性能指标监控        未实现        Performance API      │
│   ❌ 用户行为回放           未实现        rrweb                │
│   ❌ PV/UV统计              未实现        自研或百度统计         │
│   ❌ 自定义事件埋点         部分实现      LogBury表            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 4.3 用户行为埋点分析

### 📍 埋点数据模型

```java
public class LogBury extends BaseEntity {
    String isLogin;      // 是否匿名登录（0:是 1:否）
    String flag;         // 地区标识
    String mobile;       // 手机号
    String idCard;       // 身份证号
    String buryType;     // 大模块类型
    String buryCode;     // 小模块编码
    Integer buryTime;    // 点击次数
    String openId;       // 微信OpenId
}
```

### 📊 埋点维度说明

| 字段 | 说明 | 取值示例 |
|-----|------|---------|
| isLogin | 登录状态 | "0"=匿名, "1"=已登录 |
| flag | 地区标识 | "YL"=伊犁, "YA"=阿克苏等 |
| buryType | 功能模块 | "declare"=申报, "audit"=审核 |
| buryCode | 具体功能 | "prescription"=处方, "physical"=体检 |
| buryTime | 操作次数 | 1, 2, 3... |

---

# Part 4：监控体系评估

## 5.1 健康检查端点

### 🔍 现有健康检查实现

```java
// 业务服务健康检查
@RequestMapping(method = RequestMethod.GET, value = "/healthCheck")
public Result<String> healthCheck() {
    return Result.success("服务正常");
}

// 前台服务健康检查
@RequestMapping(method = RequestMethod.GET, value = "/healthCheck")
public ApiResponse healthCheck() {
    return httpForwardUtil.get(baseUrl + "/healthCheck");
}
```

### 📋 健康检查配置

| 服务 | 端点路径 | 方法 | 说明 |
|-----|---------|------|------|
| 业务服务 | `/picchealth/health/check/hello` | GET | 上线通知 |
| 业务服务 | `/picchealth/health/check/offline` | - | 下线通知 |
| 业务服务 | `/healthCheck` | GET | 自检 |
| 前台服务 | `/healthCheck` | GET | 自检 |

### ⚠️ 缺失的标准健康检查

| 检查项 | 现状 | 建议 |
|-------|-----|------|
| Spring Boot Actuator | ❌ 未集成 | 集成并暴露端点 |
| /actuator/health | ❌ 无 | 启用并自定义健康检查 |
| /actuator/info | ❌ 无 | 暴露应用信息 |
| /actuator/metrics | ❌ 无 | 暴露JVM/应用指标 |
| 数据库连接检查 | ⚠️ 简单 | 加入详细检查 |
| Redis连接检查 | ⚠️ 简单 | 加入详细检查 |

## 5.2 Prometheus指标暴露

### 📊 现状评估

```
┌─────────────────────────────────────────────────────────────────┐
│                    指标监控能力评估                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ❌ Prometheus依赖未添加                                        │
│   ❌ Micrometer依赖未添加                                        │
│   ❌ /actuator/prometheus端点未暴露                              │
│   ❌ 自定义业务指标未定义                                        │
│   ❌ JVM指标未暴露                                               │
│   ❌ 自定义Metrics未集成                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📦 需要添加的依赖

```xml
<!-- Spring Boot Actuator -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>

<!-- Micrometer Prometheus Registry -->
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

### ⚙️ 配置文件

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: always
  metrics:
    tags:
      application: ${spring.application.name}
```

## 5.3 XXL-Job任务执行监控

### 📦 依赖引入

```xml
<!-- XXL-Job 核心包 -->
<dependency>
    <groupId>com.xuxueli</groupId>
    <artifactId>xxl-job-core</artifactId>
    <version>2.3.1</version>
</dependency>
```

### 📋 定时任务清单

| 任务类名 | 功能描述 | 触发方式 |
|---------|---------|---------|
| AccountEnableTask | 账号失效批处理 | XXL-Job |
| VipMbAutoMaskTask | 自动脱敏批处理 | XXL-Job |
| MBCSZNHTask | 慢病初审智能化 | XXL-Job |
| DrugSynchronizedTask | 药品数据同步 | XXL-Job |
| Approval2EndYlTask | 审批流程任务 | XXL-Job |
| SlYearCheckTask | 年度审核任务 | XXL-Job |
| VipMbdeclareGetPhysicalTask | 体检申报任务 | XXL-Job |
| BJGXTTask/BJAutoFilingTask | 北京自动归档 | XXL-Job |
| BJDelFilingTask | 北京删除归档 | XXL-Job |
| ReviewWaringTask | 审核预警任务 | XXL-Job |

### ⚠️ 监控现状问题

| 问题 | 影响 | 建议 |
|-----|------|------|
| XXL-Job Admin未集成 | 无法可视化任务管理 | 部署XXL-Job管理后台 |
| 任务执行无日志记录 | 问题难排查 | 在任务中添加详细日志 |
| 任务失败无告警 | 问题延迟发现 | 配置任务失败告警 |
| 任务耗时未统计 | 性能问题难发现 | 添加任务耗时指标 |

## 5.4 Apollo配置变更监控

### 📦 依赖和配置

```xml
<!-- Apollo Client -->
<!-- 通过Spring Boot自动配置，已在bootstrap.yml中配置 -->
```

### 📋 Apollo配置位置

```yaml
# application-prod.yml
apollo:
  meta: http://10.34.80.145:8080    # Apollo配置中心地址（已脱敏）
  app:
    id: picc-mzmtb-server            # 应用ID
  bootstrap:
    enabled: true                     # 启用bootstrap加载
    eagerLoad:
      enabled: true
    namespaces: application.properties
```

### 📁 各环境配置

| 环境 | Apollo Meta地址 | namespaces |
|-----|---------------|-----------|
| dev | http://10.57.16.41:8080 | application-local.properties |
| test | 未提供 | - |
| uat | 未提供 | - |
| prod | http://10.34.80.145:8080 | application.properties |

### ⚠️ 监控现状问题

| 问题 | 影响 | 建议 |
|-----|------|------|
| 配置变更无审计 | 安全风险 | Apollo支持审计功能，需开启 |
| 配置变更无通知 | 变更影响未知 | 配置WebHook通知 |
| 配置回滚不便利 | 紧急恢复慢 | Apollo支持版本回滚 |

## 5.5 链路追踪集成现状

### 🔗 SkyWalking集成情况

```xml
<!-- logback-spring.xml 已集成SkyWalking布局 -->
<layout class="org.apache.skywalking.apm.toolkit.log.logback.v1.x.TraceIdPatternLogbackLayout">
    <pattern>${CONSOLE_LOG_PATTERN}</pattern>
</layout>
```

### 📊 链路追踪能力

| 能力 | 现状 | 说明 |
|-----|------|------|
| TraceId生成 | ✅ 已实现 | 通过SkyWalking布局 |
| 全局追踪ID (pGlobalTraceId) | ✅ 已配置 | MDC中存储 |
| 父追踪ID (pParentTraceId) | ✅ 已配置 | 调用链传递 |
| 本地追踪ID (pLocalTraceId) | ✅ 已配置 | 本地唯一标识 |
| SkyWalking Agent | ❓ 需确认 | 需要在PaaS平台配置 |

### ⚠️ 链路追踪问题

| 问题 | 严重程度 | 说明 |
|-----|---------|------|
| SkyWalking Agent需单独部署 | 中 | Java Agent需要手动挂载 |
| 未验证Agent是否生效 | 高 | 需要测试验证 |
| 缺少链路可视化大盘 | 中 | 建议对接SkyWalking UI |

---

# Part 5：监控体系学习思考

## 6.1 统一日志规范

### 📋 建议制定的标准

```yaml
日志规范 v1.0:
  文件命名: "{服务名}-{主机名}-{端口}-{日期}.log"
  滚动策略: 
    单文件大小: 100MB
    保留天数: 30天
    总大小上限: 10GB
  格式标准:
    时间戳: "yyyy-MM-dd HH:mm:ss.SSS"
    必含字段: [时间, 线程, 级别, 服务名, 类名, TraceId]
    敏感信息: 脱敏处理
  级别规范:
    ERROR: 系统故障、不可恢复错误
    WARN: 潜在问题、性能警告
    INFO: 业务操作、流程节点
    DEBUG: 开发调试、详细流程
```

### 🔧 具体改进措施

| 改进项 | 当前状态 | 目标状态 | 优先级 |
|-------|---------|---------|-------|
| 日志保留天数 | PaaS:7天, NAS:180天 | 统一30天 | 高 |
| 日志格式标准化 | 已有标准 | 持续完善 | 中 |
| 敏感信息脱敏 | 部分实现 | 全面覆盖 | 高 |
| 日志关键字规范 | 无 | 制定规范 | 中 |

## 6.2 链路追踪方案

### 🛠️ 推荐方案：SkyWalking

```
┌─────────────────────────────────────────────────────────────────┐
│                 SkyWalking链路追踪架构                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│  │ 权限服务 │    │ 业务服务 │    │ 前台服务 │    │ 数据库  │     │
│  │  :9092  │    │  :9091  │    │  :9001  │    │  :3306  │     │
│  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘     │
│       │              │              │              │          │
│       └──────────────┴──────────────┴──────────────┘          │
│                            │                                  │
│                     ┌──────▼──────┐                           │
│                     │ SkyWalking  │                           │
│                     │   Agent     │                           │
│                     │ (Java Agent)│                           │
│                     └──────┬──────┘                           │
│                            │                                  │
│                            ▼                                  │
│                     ┌─────────────┐                          │
│                     │   OAP Server │                          │
│                     │  (收集存储)  │                          │
│                     └──────┬──────┘                          │
│                            │                                  │
│                            ▼                                  │
│                     ┌─────────────┐                          │
│                     │   UI 界面   │                          │
│                     │  (可视化)   │                          │
│                     └─────────────┘                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📦 部署步骤

**Step 1: 下载Agent**
```bash
wget https://archive.apache.org/dist/skywalking/{version}/apache-skywalking-apm-{version}.tar.gz
tar -xzf apache-skywalking-apm-{version}.tar.gz
```

**Step 2: 配置JVM参数**
```bash
java -javaagent:/path/to/skywalking-agent/skywalking-agent.jar \
     -Dskywalking.agent.service_name=picc-mzmtb-server \
     -Dskywalking.collector.backend_service=oap-server:11800 \
     -jar your-app.jar
```

**Step 3: Kubernetes部署配置**
```yaml
# deployment.yaml
spec:
  template:
    spec:
      containers:
      - name: app
        env:
        - name: SW_AGENT_NAME
          value: "picc-mzmtb-server"
        - name: SW_COLLECTOR_BACKEND_SERVICE
          value: "skywalking-oap:11800"
        args:
        - -javaagent:/agent/skywalking-agent.jar
```

### 🔄 替代方案：Zipkin

如果已有Zipkin基础设施：

```xml
<!-- Zipkin依赖 -->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-sleuth-zipkin</artifactId>
</dependency>
```

## 6.3 告警规则设计

### 🚨 推荐告警规则

```yaml
# Prometheus告警规则示例
groups:
- name: picc-mzmtb-alerts
  rules:
  
  # 服务存活告警
  - alert: ServiceDown
    expr: up{job="picc-services"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "服务 {{ $labels.instance }} 已宕机"
      description: "服务已停止响应超过1分钟"
  
  # ERROR日志激增告警
  - alert: ErrorLogSpike
    expr: rate(logback_events_total{level="error"}[5m]) > 10
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "ERROR日志激增"
      description: "ERROR日志每分钟超过10条"
  
  # 响应时间过长告警
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, http_server_requests_seconds_bucket) > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "响应时间过长"
      description: "95分位响应时间超过2秒"
  
  # JVM内存告警
  - alert: JVMMemoryHigh
    expr: jvm_memory_used_bytes{area="heap"} / jvm_memory_max_bytes{area="heap"} > 0.9
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "JVM堆内存使用率过高"
      description: "当前使用率 {{ $value | humanizePercentage }}"
  
  # 任务执行失败告警
  - alert: XXLJobFailed
    expr: xxl_job_failed_count > 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "定时任务执行失败"
      description: "任务 {{ $labels.task_name }} 执行失败"
```

### 📊 告警渠道配置

```yaml
# AlertManager配置
route:
  group_by: ['alertname', 'severity']
  receiver: 'default-receiver'
  
receivers:
- name: 'default-receiver'
  email_configs:
  - to: ops-team@company.com
  webhook_configs:
  - url: http://dingtalk-webhook/api/alerts
```

## 6.4 日志聚合方案（ELK）

### 🏗️ ELK架构

```
┌─────────────────────────────────────────────────────────────────┐
│                       ELK日志聚合架构                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │ 权限服务 │  │ 业务服务 │  │ 前台服务 │  │  其他   │            │
│  │ :9092   │  │ :9091   │  │ :9001   │  │  服务   │            │
│  └────┬────┘  └────┬────┘  └────┬────┘  └───┬───┘            │
│       │             │             │           │                 │
│       └─────────────┴─────────────┴───────────┘                │
│                         │                                      │
│                    Filebeat                                   │
│                    (日志收集)                                  │
│                         │                                      │
│                         ▼                                      │
│              ┌──────────────────┐                             │
│              │   Logstash       │                             │
│              │ (日志解析过滤)    │                             │
│              └────────┬─────────┘                             │
│                       │                                        │
│                       ▼                                        │
│              ┌──────────────────┐                             │
│              │   Elasticsearch  │                             │
│              │   (日志存储索引)  │                             │
│              └────────┬─────────┘                             │
│                       │                                        │
│                       ▼                                        │
│              ┌──────────────────┐                             │
│              │     Kibana       │                             │
│              │   (可视化查询)    │                             │
│              └──────────────────┘                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📦 Filebeat配置

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /data/log/app/*-picc-mzmtb-*.log
  fields:
    service: picc-mzmtb
    environment: production
  multiline:
    pattern: '^\['
    negate: true
    match: after

output.logstash:
  hosts: ["logstash:5044"]
```

### 📝 Logstash管道配置

```ruby
# pipeline.conf
input {
  beats {
    port => 5044
  }
}

filter {
  # JSON解析
  json {
    source => "message"
  }
  
  # 时间处理
  date {
    match => ["timestamp", "ISO8601"]
    target => "@timestamp"
  }
  
  # 敏感信息脱敏
  mutate {
    gsub => [
      "password", ".*", "***",
      "idCard", "\d{17}\d", "***"
    ]
  }
  
  # 字段类型转换
  mutate {
    convert => {
      "responseTime" => "integer"
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "picc-logs-%{+YYYY.MM.dd}"
  }
}
```

### 📊 Kibana大盘设计

| 大盘名称 | 内容 | 刷新频率 |
|---------|-----|---------|
| 系统总览 | 服务状态、错误率、QPS | 30秒 |
| 日志查询 | 实时日志搜索 | 手动 |
| 性能分析 | 响应时间分布 | 1分钟 |
| 用户行为 | 热点页面、操作统计 | 5分钟 |
| 告警中心 | 活跃告警、历史告警 | 30秒 |

## 6.5 监控大盘设计

### 📊 推荐大盘布局

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PICC系统监控总览大盘                            │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐     │
│  │     服务状态概览            │  │      QPS监控                │     │
│  │  ┌─────┬─────┬─────┐       │  │                             │     │
│  │  │用户 │业务 │前台 │       │  │    ████▓▓▓▓▓▓░░░░ 250/s    │     │
│  │  │  ✅ │  ✅ │  ✅ │       │  │                             │     │
│  │  │9092 │9091 │9001 │       │  │    目标: 200/s              │     │
│  │  └─────┴─────┴─────┘       │  │                             │     │
│  └─────────────────────────────┘  └─────────────────────────────┘     │
│                                                                        │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐     │
│  │      响应时间分布            │  │      错误率监控              │     │
│  │                             │  │                             │     │
│  │  P50: 45ms   P90: 120ms    │  │  █░░░░░░░░░░░░░░░ 0.5%      │     │
│  │  P95: 250ms  P99: 500ms    │  │                             │     │
│  │                             │  │  目标: <1%                  │     │
│  └─────────────────────────────┘  └─────────────────────────────┘     │
│                                                                        │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐     │
│  │      JVM内存使用            │  │      活跃告警                │     │
│  │                             │  │                             │     │
│  │  Heap: ████████░░ 80%      │  │  🔴 服务宕机 x0             │     │
│  │  Old:  ██████░░░░ 60%       │  │  🟠 响应慢    x2             │     │
│  │                             │  │  🟡 错误率高  x1             │     │
│  └─────────────────────────────┘  └─────────────────────────────┘     │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                      实时日志流                                  │  │
│  │  [10:30:25] [INFO] [User:张三] [操作:登录] [耗时:25ms]         │  │
│  │  [10:30:30] [WARN] [数据库连接池使用率:80%]                      │  │
│  │  [10:30:35] [ERROR] [用户:李四] [操作:查询] [原因:超时]          │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 🔧 监控指标清单

| 类别 | 指标名称 | 说明 | 采集方式 |
|-----|---------|-----|---------|
| **存活** | 服务UP/DOWN | 服务是否响应 | 探测 |
| **流量** | QPS | 每秒请求数 | Metrics |
| **延迟** | P50/P90/P99响应时间 | 响应速度分布 | Metrics |
| **错误** | 错误率 | 失败请求占比 | Metrics |
| **JVM** | 堆内存使用率 | 内存健康状态 | JMX |
| **JVM** | GC频率/耗时 | 垃圾回收状态 | JMX |
| **线程** | 活跃线程数 | 并发处理能力 | JMX |
| **连接池** | 数据库连接使用率 | 连接池健康 | Metrics |
| **任务** | XXL-Job执行状态 | 定时任务监控 | XXL-Job API |
| **业务** | 登录次数 | 业务指标 | 日志统计 |

## 6.6 实施路线图

### 🗺️ 阶段一：基础监控（1-2周）

| 任务 | 工期 | 负责人 | 产出物 |
|-----|-----|-------|-------|
| 集成Spring Boot Actuator | 1天 | 后端 | 健康检查端点 |
| 集成Micrometer | 1天 | 后端 | 基础指标 |
| 配置Prometheus抓取 | 1天 | 运维 | 指标采集 |
| 配置AlertManager | 1天 | 运维 | 告警通道 |
| 部署Grafana大盘 | 2天 | 运维 | 监控界面 |

### 🗺️ 阶段二：链路追踪（2-3周）

| 任务 | 工期 | 负责人 | 产出物 |
|-----|-----|-------|-------|
| 部署SkyWalking OAP | 2天 | 运维 | 追踪后端 |
| 配置Java Agent | 1天 | 运维 | Agent部署 |
| 服务接入测试 | 2天 | 后端 | 链路数据 |
| 验证TraceId传递 | 1天 | 后端 | 端到端追踪 |

### 🗺️ 阶段三：日志聚合（2-3周）

| 任务 | 工期 | 负责人 | 产出物 |
|-----|-----|-------|-------|
| 部署Elasticsearch | 1天 | 运维 | 存储后端 |
| 部署Logstash | 1天 | 运维 | 管道服务 |
| 部署Kibana | 1天 | 运维 | 查询界面 |
| 配置Filebeat | 1天 | 运维 | 日志收集 |
| 编写日志解析规则 | 3天 | 后端 | 解析模板 |

### 🗺️ 阶段四：前端监控（2周）

| 任务 | 工期 | 负责人 | 产出物 |
|-----|-----|-------|-------|
| 集成Sentry SDK | 1天 | 前端 | 错误收集 |
| 清理console.log | 3天 | 前端 | 99处清理 |
| 配置错误告警 | 1天 | 前端 | 告警规则 |
| 接入性能监控 | 2天 | 前端 | 性能指标 |

---

# 附录：快速查询手册

## A1. 日志文件快速定位

```bash
# 查看某服务最新日志
tail -f /data/log/app/sys_log-picc-mzmtb-*-9091.log

# 搜索ERROR日志
grep "ERROR" /data/log/app/error-*.log

# 按时间范围查询
grep "2025-01-15 10:3" /data/log/app/aoplog-*.log

# 按用户查询操作
grep "userName:张三" /data/log/app/aoplog-*.log
```

## A2. 常用运维命令

```bash
# 查看Java进程
jps -l | grep picc

# 查看JVM内存
jstat -gc <pid>

# 查看线程堆栈
jstack <pid>

# 查看端口占用
netstat -tlnp | grep 9091

# 查看日志文件大小
du -sh /data/log/app/*
```

## A3. 健康检查命令

```bash
# 检查服务存活
curl http://localhost:9091/healthCheck

# 检查端口连通性
telnet localhost 9091

# 检查数据库连接
mysql -h localhost -u root -p -e "SELECT 1"
```

## A4. 告警阈值参考

| 告警项 | 阈值 | 持续时间 | 级别 |
|-------|-----|---------|------|
| 服务宕机 | - | 1分钟 | P0 |
| ERROR日志 | >10条/分钟 | 2分钟 | P1 |
| 响应时间P99 | >3秒 | 5分钟 | P1 |
| 错误率 | >1% | 5分钟 | P1 |
| JVM堆使用率 | >90% | 5分钟 | P2 |
| 磁盘使用率 | >80% | 10分钟 | P2 |

## A5. 术语表

| 术语 | 英文 | 解释 |
|-----|-----|-----|
| 日志 | Log | 系统运行时产生的记录 |
| 追踪 | Trace | 一次请求的完整调用链 |
| 指标 | Metrics | 可量化的数值统计 |
| 告警 | Alert | 异常情况的通知 |
| 滚动 | Rolling | 日志文件按策略切换 |
| 脱敏 | Desensitization | 隐藏敏感信息 |

---

## 📝 文档维护

| 版本 | 日期 | 作者 | 变更内容 |
|-----|-----|-----|---------|
| v1.0 | 2025-01 | - | 初始版本 |

---

> 💡 **提示**: 本文档基于PICC四个项目的源码分析生成，部分信息（如IP、密码等敏感数据）已脱敏处理。如有疑问，请联系技术团队。
