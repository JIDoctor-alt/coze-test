# PICC四个项目API错误码与异常处理机制跨项目整合解析报告

> 📅 文档生成时间：2024年
> 
> 📌 零基础小白化规则说明：
> - **异常** = "出了差错要怎么善后"
> - **全局异常处理器** = "急诊室，不管什么病先送到这里"
> - **BusinessException** = "业务上的规矩，比如金额不能为负"
> - **错误码** = "病历编号，一看就知道是什么问题"
> - **HTTP状态码** = "医院的分诊信号灯"
> - **Axios拦截器** = "快递分拣站，检查包裹有没有问题"

---

## 目录

1. [项目概览](#1-项目概览)
2. [Part 1：每个Java项目的异常处理机制](#2-part-1每个java项目的异常处理机制)
   - [1.1 权限服务 (user)](#11-权限服务-user)
   - [1.2 业务服务 (server)](#12-业务服务-server)
   - [1.3 前台服务 (gateway)](#13-前台服务-gateway)
3. [Part 2：前端错误处理机制](#3-part-2前端错误处理机制)
4. [Part 3：跨项目错误传播链路](#4-part-3跨项目错误传播链路)
5. [Part 4：统一错误码规范建议](#5-part-4统一错误码规范建议)
6. [总结与建议](#6-总结与建议)

---

## 1. 项目概览

### 1.1 四个项目基本信息

| 项目名称 | 角色定位 | 端口 | 技术栈 |
|---------|---------|------|--------|
| **picc-mzmtb-user** | 权限服务 | 9092 | Spring Boot + MyBatis |
| **picc-mzmtb-server** | 业务服务 | 9091 | Spring Boot + MyBatis + Redis |
| **picc-mzmtb-gateway** | 前台服务 | 9001 | Spring Boot + Web |
| **picc-mzmtb-agent** | 前端 | - | Vue 2 + Axios + Ant Design Vue |

### 1.2 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端 (agent)                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Axios 拦截器                                             │   │
│  │  - 请求拦截器 (加密、Token注入)                            │   │
│  │  - 响应拦截器 (解密、错误处理、状态判断)                   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP Request
┌─────────────────────────────────────────────────────────────────┐
│                       前台服务 (gateway)                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  APIAuthorityFilter (权限过滤器)                          │   │
│  │  - Token 验证                                            │   │
│  │  - 权限校验                                              │   │
│  │  - 地区标记(flag)验证                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  FlagInterceptorConfig (地区拦截器)                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  XssRequestFilter (XSS防护)                              │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP/RPC 调用
┌─────────────────────────────────────────────────────────────────┐
│                       业务服务 (server)                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  RequestFilter (参数过滤器)                               │   │
│  │  - 业务参数处理                                           │   │
│  │  - 地区路由分发                                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  TokenInterceptorConfig (Token拦截器)                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  XcxInterceptorConfig (小程序签名拦截器)                  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP/RPC 调用
┌─────────────────────────────────────────────────────────────────┐
│                       权限服务 (user)                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  APIAuthorityFilter (权限过滤器)                          │   │
│  │  - Token 验证                                            │   │
│  │  - URL权限校验                                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  TokenInterceptorConfig (Token拦截器)                     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Part 1：每个Java项目的异常处理机制

### 2.1 权限服务 (user) - 端口9092

#### 2.1.1 异常处理概述

**权限服务未使用全局异常处理器**，而是采用 **Filter + Interceptor** 的组合方式进行异常处理。

```
🏥 异常处理模式：Filter/Interceptor 模式（无全局异常处理器）
```

#### 2.1.2 核心异常处理组件

##### (1) APIAuthorityFilter - API权限过滤器

**文件位置**：`/picchealth-privilege-server/src/main/java/com/picchealth/config/APIAuthorityFilter.java`

**工作原理**：
- 使用 `@WebFilter` 注解注册为 Servlet 过滤器
- 拦截路径：`/privilege/user/*`
- 在 `doFilter` 方法中直接抛出异常

**异常处理流程**：
```java
// 1. Token为空校验
if (StringUtils.isBlank(token)) {
    throw CustomException.createByMassage(999, "登录Token无效!请重新登录");
}

// 2. 用户信息校验
if(re==null || StringUtils.isBlank(re.getUserId())){
    throw new CustomException("用户信息错误,请重新登录");
}

// 3. 权限缓存校验
if (!redisUtil.exists(UrlPermission + userid)){
    throw new BusinessException("请重新登录");
}

// 4. URL权限校验
long count1 = list.stream().filter(s -> s.contains(requestPath)).count();
if (count1 == 0){
    throw new CustomException("接口权限未通过!");
}
```

##### (2) TokenInterceptorConfig - Token拦截器

**文件位置**：`/picchealth-privilege-server/src/main/java/com/picchealth/config/TokenInterceptorConfig.java`

**工作原理**：
- 实现 `HandlerInterceptor` 接口
- 在 `preHandle` 方法中进行Token校验
- 通过配置可控制是否启用拦截

**关键配置**：
```java
@Value("${tokenInterceptFlag:false}")
private boolean tokenInterceptFlag;
```

**异常场景**：
| 错误码 | 错误消息 | 触发条件 |
|-------|---------|---------|
| 999 | 登录token无效!请重新登录 | Token为空 |
| 999 | 请不要非法使用token！ | userId与Token不匹配 |
| - | 账号无权限访问该菜单 | 用户无权限 |

##### (3) CustomException - 自定义异常类

**导入路径**：`com.picchealth.exception.CustomException`

**核心方法**：
```java
// 方式1：只设置错误消息
throw new CustomException("用户信息错误,请重新登录");

// 方式2：设置错误码和消息
throw CustomException.createByMassage(999, "登录Token无效!请重新登录");
```

##### (4) BusinessException - 业务异常

**导入路径**：`pdfc.framework.exception.BusinessException`

**使用场景**：
```java
// 权限服务中的使用
throw new BusinessException("请重新登录");
```

#### 2.1.3 统一响应格式

**权限服务使用 `ApiResponse` 作为统一响应格式**

**导入路径**：`pdfc.framework.web.ApiResponse`

**API返回示例**：
```java
// 成功响应
return ApiResponse.ok(userInfoService.queryUsers(privilegeUserInfoDto));

// 失败响应
return ApiResponse.fail(commonReqVo.getMsg());
```

**ApiResponse 响应结构**：
```json
{
  "status": 0,           // 状态码：0=成功，非0=失败
  "message": "处理成功",  // 消息
  "data": { }           // 数据
}
```

#### 2.1.4 错误码定义

| 错误码 | 错误消息 | 触发场景 |
|-------|---------|---------|
| 999 | 登录Token无效!请重新登录 | Token为空或无效 |
| 999 | 请不要非法使用token！ | Token与用户ID不匹配 |
| 999 | 登录token无效!请重新登录 | Redis中Token不存在 |
| - | 用户信息错误,请重新登录 | Redis中用户信息为空 |
| - | 接口权限未通过! | URL权限校验失败 |
| - | 请重新登录 | 权限缓存不存在 |
| - | 账号无权限访问该菜单 | 用户无菜单权限 |

#### 2.1.5 权限服务异常处理类图

```
┌─────────────────────────────────────────────────────────────────┐
│                     CustomException (自定义异常)                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ + createByMassage(code: int, message: String): CustomException│
│  │ + CustomException(message: String)                      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ 继承
┌─────────────────────────────────────────────────────────────────┐
│                     BusinessException (框架异常)                  │
│  来源: pdfc.framework.exception.BusinessException                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     ApiResponse (统一响应)                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ + ok(data: Object): ApiResponse                         │   │
│  │ + fail(message: String): ApiResponse                   │   │
│  │ + status: int                                          │   │
│  │ + message: String                                      │   │
│  │ + data: Object                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

### 2.2 业务服务 (server) - 端口9091

#### 2.2.1 异常处理概述

**业务服务同样采用 Filter + Interceptor 模式**，未使用全局异常处理器。异常处理更加细致，分为多个层级和场景。

```
🏥 异常处理模式：多层 Filter/Interceptor + 业务异常码
```

#### 2.2.2 核心异常处理组件

##### (1) RequestFilter - 请求参数过滤器

**文件位置**：`/picchealth-server/src/main/java/com/picchealth/config/interceptor/RequestFilter.java`

**工作原理**：
- 拦截特定业务接口
- 根据 `flag` 参数进行业务路由
- 对 `visoncode` 进行转换处理

**异常场景**：
```java
// 异常码: 999
if(StringUtils.isBlank(personDivision)){
    throw CustomException.createByMassage(999, "该账户暂时无权限");
}
```

**支持的地市标记**：
| Flag值 | 地市 | 路由逻辑 |
|-------|-----|---------|
| YL | 榆林 | 调用 `getPersonDivision()` |
| YA | 延安 | 调用 `getPersonDivisionYa()` |
| SL | 商洛 | 调用 `getPersonDivisionSl()` |
| XYA | 西安 | 调用 `getPersonDivisionXya()` |

##### (2) TokenInterceptorConfig - Token拦截器

**文件位置**：`/picchealth-server/src/main/java/com/picchealth/config/TokenInterceptorConfig.java`

**特点**：业务服务的Token拦截器与权限服务类似，但可能处于被注释状态（开发环境）。

##### (3) XcxInterceptorConfig - 小程序签名拦截器

**文件位置**：`/picchealth-server/src/main/java/com/picchealth/config/XcxInterceptorConfig.java`

**工作原理**：
- 验证请求头中的签名信息
- 解密签名并检查过期时间

**异常场景**：
| 错误码 | 错误消息 | 触发条件 |
|-------|---------|---------|
| 401 | 小程序签名过期! | 签名已过期 |
| 999 | 小程序签名无效! | 签名为空或解密失败 |

```java
// 签名过期
throw CustomException.createByMassage(401, CommonConstant.XCX_SIGN_EXPIRE);

// 签名无效
throw CustomException.createByMassage(999, CommonConstant.XCX_SIGN_ERROR);
```

##### (4) FlagInterceptorConfig - 地区标记拦截器

**文件位置**：`/picchealth-server/src/main/java/com/picchealth/config/FlagInterceptorConfig.java`

**工作原理**：
- 从请求头获取 `flag` 参数
- 存入 ThreadLocal 供后续使用

**异常场景**：
```java
if (StringUtils.isBlank(flag)) {
    throw CustomException.createByMassage(888, "flag信息不能为空！");
}
```

##### (5) CheckFlagUtil - 地区标记工具类

**文件位置**：`/picchealth-server/src/main/java/com/picchealth/utils/CheckFlagUtil.java`

**异常场景**：
```java
// 错误码: -1
throw CustomException.createByMassage(-1, "地区标记不存在！");
```

#### 2.2.3 业务异常码体系

##### ResCodeEnum - 错误码枚举

**文件位置**：`/picchealth-server/src/main/java/com/picchealth/module/mb/enums/ResCodeEnum.java`

```java
public enum ResCodeEnum {
    // 成功
    RES_SUCCESS("000000"),              // 处理成功
    RES_SUCCESS_DOING("000010"),        // 处理中
    
    // 通用错误 (100xxx)
    RES_FAIL("100100"),                 // 错误异常
    RES_PARAM_ERROR_FAIL("100110"),      // 参数错误
    RES_AUTH_ERROR_FAIL("100120"),       // 安全验证失败
    RES_DATA_STYLE_FAIL("100160"),       // 数据格式错误
    RES_MONEY_ERROR_FAIL("100230"),      // 金额参数错误
    RES_QUERY_ERROR_FAIL("100300"),      // 查询无数据
    
    // 会员卡相关 (200xxx)
    RES_CARDNO_FAIL("200100"),           // 会员卡认证失败
    RES_CARD_PASSWORD_FAIL("200120"),    // 支付密码错误
    RES_CARD_NOPASSWORD_FAIL("200121"),   // 未设置支付密码
    RES_CARD_PASSWORD_CH("200122"),       // 附属卡密码验证
    RES_CARD_NO_TOKEN("200123"),         // 未授权免密支付
    RES_CARD_LOCK_FAIL("200130"),        // 会员卡已锁定
    RES_CARD_NOAUTHLOCK_FAIL("200140"),  // 附属卡未授权
    
    // 业务特定 (500xxx, 600xxx)
    RES_REPEAT("500120"),               // 订单重复提交
    RES_MONEY_OVER_BALANCE("500560"),    // 支付额度超余额
    RES_EXPORT_OVER_MAXIMUM("600100");   // 导出数据超限
}
```

##### ResMsgEnum - 错误消息枚举

**文件位置**：`/picchealth-server/src/main/java/com/picchealth/module/mb/enums/ResMsgEnum.java`

```java
public enum ResMsgEnum {
    RES_SUCCESS_MSG("处理成功"),
    RES_SUCCESS_MSG_DOING("处理中"),
    RES_FAIL_MSG("错误异常"),
    RES_PARAM_ERROR_FAIL_MSG("参数错误"),
    RES_AUTH_ERROR_FAIL_MSG("安全验证,MD5验证,接口验证失败"),
    RES_DATA_STYLE_FAIL_MSG("错误的数据格式,不能解析"),
    RES_MONEY_ERROR_FAIL_MSG("参数错误,非法金额参数"),
    RES_QUERY_ERROR_FAIL_MSG("未查询到相应数据"),
    RES_CARDNO_FAIL_MSG("会员卡认证失败"),
    RES_CARD_PASSWORD_FAIL_MSG("支付密码认证失败，支付取消"),
    RES_CARD_NOPASSWORD_FAIL_MSG("附属人支付密码未设置，请设置支付密码。"),
    RES_CARD_PASSWORD_CH_MSG("您已被持卡人授权使用为您发放的附属卡消费此账户，请输入您个人一卡通支付密码。"),
    RES_CARD_NO_TOKEN_MSG("该卡号还未授权免密支付，请先进行授权。"),
    RES_CARD_LOCK_FAIL_MSG("该卡已经锁定，支付取消"),
    RES_CARD_NOAUTHLOCK_FAIL_MSG("该附属卡还未授权，支付取消"),
    RES_REPEAT_MSG("该订单已经提交成功,请勿重复提交"),
    RES_MONEY_OVER_BALANCE_MSG("支付额度超过账号余额");
}
```

##### ResCodeConstant - 错误码常量

**文件位置**：`/picchealth-server/src/main/java/com/picchealth/module/thirdfee/ResCodeConstant.java`

```java
public interface ResCodeConstant {
    // 成功
    String RES_SUCCESS = "000000";
    String RES_SUCCESS_MSG = "处理成功";
    
    // 通用错误
    String RES_FAIL = "100100";
    String RES_FAIL_MSG = "错误异常";
    String RES_PARAM_ERROR_FAIL = "100110";
    String RES_PARAM_ERROR_FAIL_MSG = "参数错误";
    String RES_AUTH_ERROR_FAIL = "100120";
    String RES_AUTH_ERROR_FAIL_MSG = "安全验证,MD5验证,接口验证失败";
    String RES_DATA_STYLE_FAIL = "4100160";  // 注意：与枚举中不一致
    String RES_DATA_STYLE_FAIL_MSG = "错误的数据格式,不能解析";
    String RES_MONEY_ERROR_FAIL = "100230";
    String RES_MONEY_ERROR_FAIL_MSG = "参数错误,非法金额参数";
    String RES_QUERY_ERROR_FAIL = "100300";
    String RES_QUERY_ERROR_FAIL_MSG = "未查询到相应数据";
    
    // 会员卡相关
    String RES_CARDNO_FAIL = "200100";
    String RES_CARD_PICC_FAIL = "200120";
    String RES_CARD_PICC_FAIL_MSG = "支付密码认证失败，支付取消";
    String RES_CARD_NOPICC_FAIL = "200121";
    String RES_CARD_PICC_CH = "200122";
    String RES_CARD_NO_TOKEN = "200123";
    String RES_CARD_LOCK_FAIL = "200130";
    String RES_CARD_LOCK_FAIL_MSG = "该卡已经锁定，支付取消";
    String RES_CARD_NOAUTHLOCK_FAIL = "200140";
    String RES_CARD_NOAUTHLOCK_FAIL_MSG = "该附属卡还未授权，支付取消";
    
    // 业务特定
    String RES_REPEAT = "500120";
    String RES_REPEAT_MSG = "该订单已经提交成功,请勿重复提交";
    String RES_MONEY_OVER_BALANCE = "500560";
    String RES_MONEY_OVER_BALANCE_MSG = "支付额度超过账号余额";
    
    // 导出限制
    String RES_EXPORT_OVER_MAXIMUM = "600100";
}
```

##### CommonConstant - 通用常量

**文件位置**：`/picchealth-server/mtb-yh/mtb-base/src/main/java/com/picchealth/module/mtb/constant/CommonConstant.java`

```java
public class CommonConstant {
    // 小程序签名相关
    public static final String XCX_SIGN_ERROR = "小程序签名无效!";
    public static final String XCX_SIGN_EXPIRE = "小程序签名过期!";
    
    // 申报相关
    public static final String NO_MATCHING_NAME_MOBILE = "姓名与身份证号不匹配，请重新填写。";
    public static final String NO_MATCHING_MOBILE_NAME = "该手机号下已有绑定身份证号，请更换手机号进行申报。";
    public static final String UNIT_ERROR = "机构信息有误";
    public static final String RECORD_BACK = "此申报数据因操作失误已被撤回，请刷新后查看。";
    public static final String CANCEL_BACK_ERROR = "撤回失败！当前申报状态不是待专家审核状态";
    public static final String RE_ENTRY = "您的{}已有审核通过记录，不支持重复申报。";
}
```

#### 2.2.4 业务服务错误码完整映射表

| 错误码 | 错误消息 | 业务场景 | 使用位置 |
|-------|---------|---------|---------|
| 000000 | 处理成功 | 接口正常返回 | 所有接口 |
| 000010 | 处理中 | 异步处理中 | 支付回调等 |
| 100100 | 错误异常 | 通用错误 | 未知异常 |
| 100110 | 参数错误 | 入参校验失败 | 各类校验 |
| 100120 | 安全验证失败 | MD5/签名校验失败 | 支付相关 |
| 100160 | 数据格式错误 | JSON/XML解析失败 | 数据转换 |
| 100230 | 金额参数错误 | 金额为负或非法 | 支付相关 |
| 100300 | 未查询到相应数据 | 数据库无记录 | 查询接口 |
| 200100 | 会员卡认证失败 | 卡号不存在 | 会员卡操作 |
| 200120 | 支付密码错误 | 密码不匹配 | 支付验证 |
| 200121 | 未设置支付密码 | 首次支付 | 支付设置 |
| 200122 | 附属卡密码验证 | 附属卡消费 | 附属卡操作 |
| 200123 | 未授权免密支付 | 未开通免密 | 免密设置 |
| 200130 | 会员卡已锁定 | 卡被锁定 | 会员卡状态 |
| 200140 | 附属卡未授权 | 未授权附属人 | 附属卡权限 |
| 500120 | 订单重复提交 | 幂等性校验 | 支付接口 |
| 500560 | 支付额度超余额 | 余额不足 | 支付扣款 |
| 600100 | 导出数据超限 | 导出数据量过大 | 导出功能 |
| 888 | flag信息不能为空 | 地区标记缺失 | 路由分发 |
| 999 | 登录Token无效 | 认证失败 | 全局认证 |
| -1 | 业务自定义错误 | 业务规则校验 | 各业务模块 |

#### 2.2.5 业务服务异常使用示例

```java
// 使用 BusinessException + ResCodeEnum
throw new BusinessException(ResCodeEnum.RES_CARDNO_FAIL.getValue(), "卡号或者账号不能同时为空。");

// 使用 CustomException + 错误码
throw CustomException.createByMassage(999, "登录token无效!请重新登录");

// 使用 CustomException + 业务错误码
throw CustomException.createByMassage(ApiResponse.FAIL, "入参类型错误！");

// 使用 CustomException + 负数错误码
throw CustomException.createByMassage(-1, "疾病信息为空！");
```

---

### 2.3 前台服务 (gateway) - 端口9001

#### 2.3.1 异常处理概述

**前台服务是整个系统的网关层**，负责请求的路由、权限校验和安全防护。异常处理机制与业务服务类似，但增加了更多的安全相关处理。

```
🏥 异常处理模式：Filter/Interceptor + 安全防护
```

#### 2.3.2 核心异常处理组件

##### (1) APIAuthorityFilter - API权限过滤器（增强版）

**文件位置**：`/gateway/src/main/java/com/picchealth/config/interceptor/APIAuthorityFilter.java`

**工作原理**：
- 拦截路径覆盖更广：`/ppop/*`, `/offline/*`, `/drugstore/*`, `/vip*`, `/Mb*` 等
- 支持多种认证方式：Token认证、小程序认证
- 支持排除路径配置

**支持的认证方式**：

| 认证类型 | 识别方式 | 错误响应方式 |
|---------|---------|-------------|
| 小程序认证 | 请求路径包含 `picchealth` | `sendErrorResponse` |
| Token认证 | POST请求头、GET参数 | `throw CustomException` |
| 经办端认证 | Redis中的USERID | `customRequest` |

**异常响应示例**：
```java
// 小程序Token无效
sendErrorResponse(response, 1001, "小程序Token无效! 请重新登录");

// 登录Token无效
throw CustomException.createByMassage(999, "登录Token无效!请重新登录");

// 接口权限未通过
throw new CustomException("接口权限未通过!");
```

##### (2) FlagInterceptorConfig - 地区标记拦截器

与业务服务相同：
```java
if (StringUtils.isBlank(flag)) {
    throw CustomException.createByMassage(888, "flag信息不能为空！");
}
```

##### (3) XssRequestFilter - XSS防护过滤器

**文件位置**：`/gateway/src/main/java/com/picchealth/config/xssfilter/XssRequestFilter.java`

**工作原理**：
- 过滤请求中的XSS恶意脚本
- 防止跨站脚本攻击

#### 2.3.3 统一响应格式

**前台服务使用 `ApiResponse`**（与权限服务相同）

```java
// 直接返回错误响应
ApiResponse result = new ApiResponse(code, message, null);
```

**响应格式**：
```json
{
  "status": 1001,           // 业务状态码
  "message": "小程序Token无效! 请重新登录",
  "data": null
}
```

#### 2.3.4 前台服务错误码定义

| 错误码 | 错误消息 | 触发场景 |
|-------|---------|---------|
| 1001 | 小程序Token无效! 请重新登录 | 小程序Token验证失败 |
| 1002 | 手机号与Token不匹配 | 手机号校验失败 |
| 888 | flag信息不能为空！ | 地区标记缺失 |
| 999 | 登录Token无效!请重新登录 | Token认证失败 |
| 999 | 登录账号信息不一致。请重新登录 | Token与Flag不匹配 |
| - | 接口权限未通过! | URL权限校验失败 |
| - | 请重新登录 | 权限缓存不存在 |

#### 2.3.5 前台服务安全响应头

```java
private void addSecurityHeaders(HttpServletResponse response) {
    // 防止点击劫持
    response.setHeader("X-Frame-Options", "SAMEORIGIN");
}
```

---

## 3. Part 2：前端错误处理机制

### 3.1 Axios 拦截器架构

#### 3.1.1 核心配置文件

**文件位置**：`/agent/src/api/axios.js`

```
🔧 核心功能：
- 请求参数 AES 加密
- 响应数据 AES 解密
- Token/UserId 自动注入
- 统一错误处理
```

#### 3.1.2 请求拦截器

```javascript
// 请求拦截器核心逻辑
instance.interceptors.request.use(
    config => {
        // 1. AES字段加密（敏感数据）
        if (config.data) {
            config.data = this.encryptRequestFieldsWithAES(config.data, apiUrl);
        }

        // 2. Token注入
        let query = location.href.split('?')[1];
        token = qs.parse(query, { ignoreQueryPrefix: true })["token"];
        
        // 3. 从本地存储获取用户信息
        if (util.getUserInfo()) {
            let logInfoMB = util.getUserInfo();
            userId = logInfoMB.userId;
            token = logInfoMB.token;
        }

        // 4. 设置请求头
        config.headers.common['Authorization'] = token;
        config.headers['token'] = token;
        config.headers['tokenFlag'] = sessionStorage.getItem('tokenFlag');
        config.headers['userId'] = userId || null;
        config.headers['flag'] = flag || 0;

        return config;
    },
    error => {
        return Promise.reject(error);
    }
);
```

#### 3.1.3 响应拦截器（核心错误处理）

```javascript
// 响应拦截器核心逻辑
instance.interceptors.response.use(
    res => {
        let data = url.includes('/zipdownload/downloadListPdfZip') ? res : res.data;

        // 1. 销毁请求队列
        const is = this.destroy(url);
        if (!is) {
            setTimeout(() => { /* 关闭loading */ }, 500);
        }

        // 2. AES字段解密
        if (data && data.status === 0) {
            data = this.decryptSpecificFieldsWithAES(data);
        }

        // 3. 错误状态判断
        if (data.status !== undefined && data.status !== 0 && data.status !== 200) {
            let errorMsg = data.statusText || data.error;
            
            // 特殊接口处理（弹窗提示而非消息提示）
            if (apiUrl == '/MbDeclareFirstTrial/updateMbDeclareFirstApprovalInfo' ||
                apiUrl == '/vipMbDeclareList/saveVipMbdeclareInfo' /* ... */) {
                if ((!queryFlag) && data.status == -1) {
                    return Promise.reject(data);
                }
            }

            // 显示错误消息
            if (errorMsg) message.error(errorMsg);

            // 999错误码 -> 跳转登录页
            if (data.status == 999) {
                window.sessionStorage.clear();
                Router.replace("/loginMb");
            }

            return Promise.reject(data);
        }

        return data;
    },
    error => {
        // 网络错误处理
        if (error.message.includes('timeout')) {
            message.error("服务请求超时，稍后重试");
            return;
        }
        return Promise.reject(error);
    }
);
```

### 3.2 统一响应格式解析

#### 3.2.1 前端响应状态判断

```javascript
// 成功状态
data.status === 0 || data.status === 200

// 失败状态
data.status !== 0 && data.status !== 200
```

#### 3.2.2 响应数据结构

```typescript
// 成功响应
{
    status: 0,                    // 状态码：0=成功
    message: "处理成功",          // 消息
    data: {                       // 数据
        // 业务数据
    }
}

// 失败响应
{
    status: -1,                   // 业务错误码（非0即失败）
    statusText: "申报数据不存在！", // 错误消息（与error字段二选一）
    error: "申报数据不存在！"      // 错误消息
}
```

### 3.3 HTTP状态码与业务状态码对照

#### 3.3.1 前端HTTP状态码处理

| HTTP状态码 | 场景 | 前端处理 |
|-----------|-----|---------|
| 200 | 正常响应 | 检查业务status |
| 401 | 会话超时 | 跳转登录页 |
| 403 | 无权限 | 显示错误消息 |
| 404 | 接口不存在 | 显示错误消息 |
| 500 | 服务器错误 | 显示错误消息 |
| timeout | 请求超时 | 显示"服务请求超时" |

#### 3.3.2 业务状态码处理

| 业务status | 含义 | 前端处理 |
|-----------|-----|---------|
| 0 | 成功 | 正常返回data |
| -1 | 业务错误 | 显示错误消息，部分接口特殊处理 |
| 999 | 认证失败 | 清除session，跳转登录页 |
| 200 | 成功（兼容） | 正常返回data |
| 其他 | 业务错误 | 显示错误消息 |

### 3.4 错误提示机制

#### 3.4.1 使用 Ant Design Vue 消息组件

```javascript
import { message } from 'ant-design-vue';

// 错误提示
message.error(errorMsg);

// 超时提示
message.error("服务请求超时，稍后重试");
```

#### 3.4.2 特殊错误处理场景

```javascript
// 场景1：手机号被占用（特殊弹窗提示）
if (apiUrl == '/picchealth/checkICDDeclareRepeat2') {
    if ((!queryFlag) && data.status == -1) {
        return Promise.reject(data);  // 不显示消息，交给调用方处理
    }
}

// 场景2：延安手机号被占用
if (apiUrl == '/vipMbDeclareList/updateMobileYa') {
    if ((queryFlag == '4') && data.status == -1) {
        return Promise.reject(data);
    }
}

// 场景3：认证失败跳转登录
if (data.status == 999) {
    window.sessionStorage.clear();
    Router.replace("/loginMb");
}
```

### 3.5 通用中心 Axios 配置

**文件位置**：`/agent/src/api/axiosCenter.js`

```javascript
// 响应拦截器
instance.interceptors.response.use(
    res => {
        let { data } = res;

        // 错误状态判断
        if (data.status !== undefined && data.status != 0) {
            let errorMsg = data.statusText || data.error;
            if (errorMsg) message.error(errorMsg);
            
            // 401 会话超时
            if (data.status == 401) {
                window.sessionStorage.clear();
                Router.replace({path: '/loginMb'});
            }
            return Promise.reject(data);
        }
        return data;
    },
    error => {
        message.error(error.toString());
        if (error.message.includes('timeout')) {
            message.error("服务请求超时，稍后重试");
        }
        return Promise.reject(error);
    }
);
```

---

## 4. Part 3：跨项目错误传播链路

### 4.1 错误传播链路总览

```
┌────────────────────────────────────────────────────────────────────┐
│                         前端 (agent)                               │
│  axios.js 响应拦截器                                                │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  if (data.status !== 0) {                                  │   │
│  │      message.error(data.error);  // 显示错误               │   │
│  │      if (data.status == 999) {                             │   │
│  │          Router.replace("/loginMb"); // 跳转登录            │   │
│  │      }                                                     │   │
│  │  }                                                         │   │
│  └────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
                                  ▲
                                  │ HTTP Response
                                  │ {
                                  │   status: -1,
                                  │   error: "申报数据不存在！"
                                  │ }
                                  │
┌────────────────────────────────────────────────────────────────────┐
│                      前台服务 (gateway)                            │
│  APIAuthorityFilter                                               │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  try {                                                     │   │
│  │      filterChain.doFilter(request, response);               │   │
│  │  } catch (Throwable e) {                                   │   │
│  │      // 异常被框架处理，可能返回HTTP 500                    │   │
│  │  }                                                         │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  业务服务调用 (Feign/HTTP)                                          │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  // 调用业务服务，可能抛出 CustomException                  │   │
│  │  throw CustomException.createByMassage(-1, "申报数据不存在！");│   │
│  └────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
                                  ▲
                                  │ HTTP/RPC
                                  │
┌────────────────────────────────────────────────────────────────────┐
│                      业务服务 (server)                             │
│  业务逻辑层                                                        │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  public MbDeclareInfo getMbDeclareInfo(Long declareId) {   │   │
│  │      MbDeclareInfo info = mbDeclareInfoDao.selectById(declareId);│
│  │      if (info == null) {                                    │   │
│  │          throw CustomException.createByMassage(-1, "申报数据不存在！");│
│  │      }                                                      │   │
│  │      return info;                                           │   │
│  │  }                                                          │   │
│  └────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
```

### 4.2 典型错误传播场景

#### 场景1：Token无效错误

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. 业务服务 (server)                                                │
│    TokenInterceptorConfig.preHandle()                                │
│    ┌───────────────────────────────────────────────────────────┐   │
│    │ if (StringUtils.isBlank(token)) {                         │   │
│    │     throw CustomException.createByMassage(999, "登录token │   │
│    │         无效!请重新登录");                                │   │
│    │ }                                                         │   │
│    └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ 异常被抛出
┌─────────────────────────────────────────────────────────────────────┐
│ 2. 前台服务 (gateway) - APIAuthorityFilter                         │
│    ┌───────────────────────────────────────────────────────────┐   │
│    │ // 异常可能在此被捕获或直接透传                           │   │
│    │ // 取决于异常类型和框架配置                               │   │
│    └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP Response
┌─────────────────────────────────────────────────────────────────────┐
│ 3. 前端 (agent) - axios.js 响应拦截器                               │
│    ┌───────────────────────────────────────────────────────────┐   │
│    │ if (data.status == 999) {                                 │   │
│    │     window.sessionStorage.clear();                       │   │
│    │     Router.replace("/loginMb"); // 跳转登录页             │   │
│    │ }                                                         │   │
│    └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

#### 场景2：业务数据校验错误

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. 业务服务 (server) - 业务层                                        │
│    VipMbdeclareInfoServiceImpl                                      │
│    ┌───────────────────────────────────────────────────────────┐   │
│    │ public MbDeclareInfo getMbDeclareInfo(Long declareId) {   │   │
│    │     MbDeclareInfo info = dao.selectById(declareId);       │   │
│    │     if (info == null) {                                   │   │
│    │         throw CustomException.createByMassage(             │   │
│    │             -1, "申报数据不存在！");                       │   │
│    │     }                                                     │   │
│    │     return info;                                           │   │
│    │ }                                                         │   │
│    └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ ApiResponse 包装
┌─────────────────────────────────────────────────────────────────────┐
│ 2. 业务服务 (server) - Controller层                                │
│    MbDeclareApi                                                    │
│    ┌───────────────────────────────────────────────────────────┐   │
│    │ @RequestMapping("/getMbDeclareInfo")                       │   │
│    │ public ApiResponse getMbDeclareInfo(Long declareId) {      │   │
│    │     try {                                                 │   │
│    │         return ApiResponse.ok(service.getMbDeclareInfo(declareId));│
│    │     } catch (CustomException e) {                         │   │
│    │         return ApiResponse.fail(e.getMessage());          │   │
│    │     }                                                     │   │
│    │ }                                                         │   │
│    └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP Response
┌─────────────────────────────────────────────────────────────────────┐
│ 3. 前端 (agent)                                                    │
│    ┌───────────────────────────────────────────────────────────┐   │
│    │ // axios 响应拦截器                                        │   │
│    │ if (data.status !== 0 && data.status !== 200) {           │   │
│    │     let errorMsg = data.statusText || data.error;         │   │
│    │     message.error(errorMsg); // 显示"申报数据不存在！"     │   │
│    │     return Promise.reject(data);                          │   │
│    │ }                                                         │   │
│    └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

#### 场景3：小程序Token错误

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. 前台服务 (gateway) - APIAuthorityFilter                          │
│    ┌───────────────────────────────────────────────────────────┐   │
│    │ // 小程序认证                                              │   │
│    │ String xcxUser = request.getHeader("xcxUser");           │   │
│    │ try {                                                     │   │
│    │     xcxString = Sm2Util.decryptData(xcxUser).toUpperCase();│   │
│    │ } catch (Exception e) {                                  │   │
│    │     sendErrorResponse(response, 1002, "手机号与Token不匹配");│
│    │     return;                                                │   │
│    │ }                                                         │   │
│    │                                                           │   │
│    │ if (!redisUtil.exists(XCXUsers + xcxString)) {            │   │
│    │     sendErrorResponse(response, 1001,                     │   │
│    │         "小程序Token无效! 请重新登录");                   │   │
│    │     return;                                                │   │
│    │ }                                                         │   │
│    └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP Response (直接写入)
                              │ {
                              │   "status": 1001,
                              │   "message": "小程序Token无效! 请重新登录",
                              │   "data": null
                              │ }
                              │
┌─────────────────────────────────────────────────────────────────────┐
│ 2. 前端 (agent)                                                    │
│    ┌───────────────────────────────────────────────────────────┐   │
│    │ // axios 响应拦截器                                        │   │
│    │ if (data.status !== 0 && data.status !== 200) {           │   │
│    │     let errorMsg = data.error || data.statusText;         │   │
│    │     message.error(errorMsg); // 显示错误消息              │   │
│    │ }                                                         │   │
│    └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.3 错误传播中的数据转换

```
┌─────────────────────────────────────────────────────────────────────┐
│                        错误码转换流程                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  │  Java Exception │ ──▶ │   ApiResponse   │ ──▶ │  JSON Response  │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘
│                                                                     │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  │ CustomException │     │  status: -1    │     │  status: -1     │
│  │ code=-1, msg=  │ ──▶ │  error: "消息"  │ ──▶ │  error: "消息"  │
│  │ "申报不存在"    │     │                 │     │                 │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.4 跨项目接口调用关系

```
┌─────────────────────────────────────────────────────────────────────┐
│                           调用关系图                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│    ┌──────────┐                                                    │
│    │  前端    │ ◀──── HTTP ────────────────────────────────────┐  │
│    │ (agent)  │                                                    │  │
│    └────┬─────┘                                                    │  │
│         │                                                          │  │
│         │ HTTP                                                     │  │
│         ▼                                                          │  │
│    ┌──────────┐                                                    │  │
│    │ 前台服务 │ ◀──── HTTP/Feign ────────────────────────────────┤  │
│    │(gateway) │                                                    │  │
│    └────┬─────┘                                                    │  │
│         │                                                          │  │
│         │ HTTP/Feign                                               │  │
│         ▼                                                          │  │
│    ┌──────────┐                                                    │  │
│    │ 业务服务 │ ◀──── HTTP ───────────────────────────────┐       │  │
│    │ (server) │                                         │       │  │
│    └────┬─────┘                                         │       │  │
│         │                                               │       │  │
│         │ HTTP/内部调用                                  │       │  │
│         ▼                                               │       │  │
│    ┌──────────┐                                        │       │  │
│    │ 权限服务 │ ───────────────────────────────────────┘       │  │
│    │  (user)  │                                                │  │
│    └──────────┘                                                │  │
│                                                                  │  │
│    ┌──────────┐                                                │  │
│    │  Redis   │ ◀──── 缓存Token/权限/会话 ─────────────────────┘  │
│    └──────────┘                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Part 4：统一错误码规范建议

### 5.1 当前问题分析

#### 5.1.1 错误码体系不一致

| 项目 | 错误码来源 | 状态码含义 |
|-----|-----------|-----------|
| user | CustomException | 999=认证失败 |
| server | ResCodeEnum | 000000=成功，100xxx=错误 |
| server | CustomException | -1/999/888 等 |
| gateway | CustomException | 999/888/1001/1002 |
| agent | data.status | 0=成功，非0=失败 |

#### 5.1.2 错误码命名不规范

```
问题1: ResCodeConstant 和 ResCodeEnum 中的错误码不一致
  - ResCodeEnum.RES_DATA_STYLE_FAIL = "100160"
  - ResCodeConstant.RES_DATA_STYLE_FAIL = "4100160"  // 多了一个"4"

问题2: CustomException 使用负数错误码
  - -1: 业务自定义错误
  - 与正数错误码体系不一致

问题3: 前端状态码判断混乱
  - data.status === 0  // 成功
  - data.status === 200  // 兼容
  - data.status !== 0 && data.status !== 200  // 失败
```

### 5.2 统一错误码规范建议

#### 5.2.1 错误码分段设计

```
┌────────────────────────────────────────────────────────────────────┐
│                        错误码结构设计                               │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│   ┌────────┬────────┬────────┬────────┐                           │
│   │ XX     │  XX    │   XX   │   XX   │  共6位数字                │
│   └────────┴────────┴────────┴────────┘                           │
│    ▲         ▲        ▲       ▲                                   │
│    │         │        │       │                                   │
│    │         │        │       │                                   │
│  系统标识   模块标识   错误类型   错误序号                          │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**分段说明**：

| 段位 | 长度 | 说明 | 示例 |
|-----|-----|-----|-----|
| 系统标识 | 2位 | 区分不同微服务 | 10=权限服务, 20=业务服务, 30=网关 |
| 模块标识 | 2位 | 区分业务模块 | 01=用户模块, 02=订单模块 |
| 错误类型 | 1位 | 错误大类 | 1=参数错误, 2=认证错误, 5=业务错误 |
| 错误序号 | 2位 | 具体错误 | 01, 02, 03... |

#### 5.2.2 推荐错误码体系

##### 成功码

| 错误码 | 含义 | 说明 |
|-------|-----|-----|
| 000000 | 成功 | 处理成功 |
| 000010 | 处理中 | 异步处理 |
| 000099 | 部分成功 | 部分操作成功 |

##### 系统级错误 (1xxx)

| 错误码 | 含义 | 说明 |
|-------|-----|-----|
| 10xx00 | 系统错误 | 系统内部错误 |
| 10xx01 | 系统繁忙 | 服务暂不可用 |
| 10xx02 | 服务超时 | 调用超时 |

##### 参数错误 (11xx)

| 错误码 | 含义 | 说明 |
|-------|-----|-----|
| 11xx00 | 参数错误 | 通用参数错误 |
| 11xx01 | 参数为空 | 必填参数缺失 |
| 11xx02 | 参数格式错误 | 格式不正确 |
| 11xx03 | 参数超出范围 | 值超出允许范围 |

##### 认证授权错误 (12xx)

| 错误码 | 含义 | 说明 |
|-------|-----|-----|
| 12xx00 | 认证失败 | 通用认证失败 |
| 12xx01 | Token无效 | Token为空或无效 |
| 12xx02 | Token过期 | Token已过期 |
| 12xx03 | 签名无效 | 签名校验失败 |
| 12xx04 | 签名过期 | 签名已过期 |
| 12xx05 | 权限不足 | 无访问权限 |
| 12xx06 | 用户被禁用 | 账户已被禁用 |

##### 数据错误 (13xx)

| 错误码 | 含义 | 说明 |
|-------|-----|-----|
| 13xx00 | 数据错误 | 通用数据错误 |
| 13xx01 | 数据不存在 | 记录不存在 |
| 13xx02 | 数据重复 | 违反唯一约束 |
| 13xx03 | 数据格式错误 | 无法解析 |

##### 业务错误 (2xxx)

| 错误码 | 含义 | 说明 |
|-------|-----|-----|
| 20xx00 | 业务错误 | 通用业务错误 |
| 21xx01 | 余额不足 | 账户余额不足 |
| 21xx02 | 库存不足 | 库存不足 |
| 21xx03 | 订单已存在 | 重复下单 |
| 21xx04 | 状态不允许 | 当前状态不允许操作 |
| 21xx05 | 超过限制 | 超出业务限制 |

##### 第三方服务错误 (5xxx)

| 错误码 | 含义 | 说明 |
|-------|-----|-----|
| 50xx00 | 第三方服务错误 | 通用第三方错误 |
| 50xx01 | 支付服务不可用 | 支付渠道异常 |
| 50xx02 | 短信服务不可用 | 短信发送失败 |
| 50xx03 | 医保接口异常 | 医保系统异常 |

#### 5.2.3 响应格式统一

```json
// 成功响应
{
    "status": 0,
    "message": "处理成功",
    "data": {
        // 业务数据
    },
    "timestamp": 1700000000000,
    "traceId": "abc123def456"
}

// 失败响应
{
    "status": 120001,
    "message": "Token无效，请重新登录",
    "error": {
        "code": "AUTH_TOKEN_INVALID",
        "detail": "Token已失效或不存在"
    },
    "timestamp": 1700000000000,
    "traceId": "abc123def456"
}
```

### 5.3 学习思考

#### 5.3.1 后端改进

**建议1：统一异常处理**

```java
// 使用 @ControllerAdvice 统一处理异常
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(CustomException.class)
    public ApiResponse handleCustomException(CustomException e) {
        return ApiResponse.fail(e.getCode(), e.getMessage());
    }
    
    @ExceptionHandler(BusinessException.class)
    public ApiResponse handleBusinessException(BusinessException e) {
        return ApiResponse.fail(e.getCode(), e.getMessage());
    }
    
    @ExceptionHandler(Exception.class)
    public ApiResponse handleException(Exception e) {
        log.error("系统异常", e);
        return ApiResponse.fail(100001, "系统繁忙，请稍后重试");
    }
}
```

**建议2：统一错误码枚举**

```java
public enum ErrorCode {
    // 成功
    SUCCESS("000000", "处理成功"),
    
    // 认证授权 (12xx)
    AUTH_TOKEN_INVALID("120001", "Token无效，请重新登录"),
    AUTH_TOKEN_EXPIRED("120002", "Token已过期，请重新登录"),
    AUTH_SIGN_INVALID("120003", "签名无效"),
    AUTH_PERMISSION_DENIED("120005", "权限不足"),
    
    // 参数错误 (11xx)
    PARAM_ERROR("110000", "参数错误"),
    PARAM_REQUIRED("110001", "参数不能为空"),
    PARAM_FORMAT_ERROR("110002", "参数格式错误"),
    
    // 业务错误 (2xxx)
    BIZ_ERROR("200000", "业务处理失败"),
    ORDER_DUPLICATE("210003", "订单已存在，请勿重复提交"),
    BALANCE_INSUFFICIENT("210001", "余额不足"),
    
    // 系统错误 (10xx)
    SYS_ERROR("100000", "系统繁忙，请稍后重试"),
    SYS_TIMEOUT("100002", "服务超时，请稍后重试");
    
    private final String code;
    private final String message;
    
    ErrorCode(String code, String message) {
        this.code = code;
        this.message = message;
    }
}
```

**建议3：异常类改进**

```java
public class BusinessException extends RuntimeException {
    private final String code;
    private final String message;
    
    public BusinessException(ErrorCode errorCode) {
        this.code = errorCode.getCode();
        this.message = errorCode.getMessage();
    }
    
    public BusinessException(ErrorCode errorCode, String detail) {
        this.code = errorCode.getCode();
        this.message = detail;
    }
}
```

#### 5.3.2 前端改进

**建议1：统一错误处理**

```javascript
// 错误码到消息的映射
const ERROR_MESSAGE_MAP = {
    '000000': '处理成功',
    '120001': '登录已过期，请重新登录',
    '120002': '登录已过期，请重新登录',
    '120005': '您没有权限访问该功能',
    '110000': '参数错误',
    '110001': '请填写必填项',
    '200000': '业务处理失败',
    '210001': '余额不足',
    '210003': '订单已存在，请勿重复提交',
    '100000': '系统繁忙，请稍后重试',
    '100002': '请求超时，请稍后重试',
};

// axios 响应拦截器改进
instance.interceptors.response.use(
    res => {
        let data = res.data;
        
        // 成功判断
        if (data.status === 0 || data.status === '000000') {
            return data;
        }
        
        // 失败处理
        const errorCode = data.status;
        const errorMsg = ERROR_MESSAGE_MAP[errorCode] || data.error || '操作失败';
        
        // 认证错误 - 跳转登录
        if (errorCode === '120001' || errorCode === '120002') {
            window.sessionStorage.clear();
            Router.replace('/login');
            return Promise.reject(data);
        }
        
        // 显示错误消息
        message.error(errorMsg);
        return Promise.reject(data);
    },
    error => {
        if (error.code === 'ECONNABORTED') {
            message.error('请求超时，请稍后重试');
        } else {
            message.error('网络异常，请检查网络连接');
        }
        return Promise.reject(error);
    }
);
```

**建议2：统一错误组件**

```vue
<template>
    <a-modal v-model="visible" title="错误提示">
        <p>{{ errorMessage }}</p>
        <template slot="footer">
            <a-button @click="handleRetry" v-if="retryable">重试</a-button>
            <a-button type="primary" @click="handleLogin" v-if="needLogin">重新登录</a-button>
            <a-button @click="handleClose">关闭</a-button>
        </template>
    </a-modal>
</template>
```

---

## 6. 总结与建议

### 6.1 当前架构优点

1. **多层防护**：Filter + Interceptor 双重验证
2. **统一响应格式**：ApiResponse 统一封装
3. **错误码分类**：按业务模块划分错误码
4. **前端友好**：错误消息直接展示给用户
5. **Token管理**：Redis 集中管理会话

### 6.2 当前架构问题

1. **缺少全局异常处理器**：异常处理分散在各个 Filter/Interceptor
2. **错误码体系不一致**：枚举、常量定义重复且不一致
3. **错误码不连续**：100110, 100120, 100160, 100230, 100300 跳跃
4. **负数错误码**：部分使用 -1，与正数体系不一致
5. **前端状态码判断复杂**：需要同时判断 0 和 200
6. **错误消息分散**：部分在后端返回，部分在前端配置

### 6.3 改进优先级

| 优先级 | 改进项 | 工作量 | 收益 |
|-------|-------|-------|-----|
| P0 | 统一错误码体系 | 中 | 高 |
| P0 | 添加全局异常处理器 | 中 | 高 |
| P1 | 前端错误码映射表 | 低 | 高 |
| P1 | 统一响应格式 | 低 | 中 |
| P2 | 错误追踪ID | 低 | 中 |
| P2 | 错误日志规范 | 中 | 中 |

### 6.4 后续工作建议

1. **建立错误码文档**：统一维护所有错误码
2. **增加错误追踪**：traceId 贯穿整个调用链路
3. **监控告警**：对特定错误码设置告警
4. **错误统计**：按错误码统计分析问题
5. **用户引导**：针对高频错误提供解决方案

---

## 附录

### A. 完整错误码对照表

| 错误码 | 错误消息 | 来源 | 触发场景 |
|-------|---------|-----|---------|
| 000000 | 处理成功 | 全局 | 成功响应 |
| 000010 | 处理中 | 全局 | 异步处理 |
| 100100 | 错误异常 | server | 未知异常 |
| 100110 | 参数错误 | server | 入参校验失败 |
| 100120 | 安全验证失败 | server | MD5/签名校验失败 |
| 100160 | 数据格式错误 | server | JSON/XML解析失败 |
| 100230 | 金额参数错误 | server | 金额为负或非法 |
| 100300 | 未查询到相应数据 | server | 数据库无记录 |
| 200100 | 会员卡认证失败 | server | 卡号不存在 |
| 200120 | 支付密码错误 | server | 密码不匹配 |
| 200121 | 未设置支付密码 | server | 首次支付 |
| 200122 | 附属卡密码验证 | server | 附属卡消费 |
| 200123 | 未授权免密支付 | server | 未开通免密 |
| 200130 | 会员卡已锁定 | server | 卡被锁定 |
| 200140 | 附属卡未授权 | server | 未授权附属人 |
| 500120 | 订单重复提交 | server | 幂等性校验 |
| 500560 | 支付额度超余额 | server | 余额不足 |
| 600100 | 导出数据超限 | server | 导出数据量过大 |
| 888 | flag信息不能为空 | server/gateway | 地区标记缺失 |
| 999 | 登录Token无效 | user/server/gateway | 认证失败 |
| 1001 | 小程序Token无效 | gateway | 小程序认证失败 |
| 1002 | 手机号与Token不匹配 | gateway | 手机号校验失败 |
| -1 | 业务自定义错误 | server | 业务规则校验 |

### B. 关键文件清单

| 文件路径 | 说明 |
|---------|-----|
| user/config/APIAuthorityFilter.java | 权限过滤器 |
| user/config/TokenInterceptorConfig.java | Token拦截器 |
| server/config/interceptor/RequestFilter.java | 请求参数过滤器 |
| server/config/XcxInterceptorConfig.java | 小程序签名拦截器 |
| server/config/FlagInterceptorConfig.java | 地区标记拦截器 |
| server/module/mb/enums/ResCodeEnum.java | 错误码枚举 |
| server/module/mb/enums/ResMsgEnum.java | 错误消息枚举 |
| gateway/config/interceptor/APIAuthorityFilter.java | 网关权限过滤器 |
| agent/src/api/axios.js | Axios核心配置 |
| agent/src/api/axiosCenter.js | 通用中心Axios配置 |

---

*文档结束*
