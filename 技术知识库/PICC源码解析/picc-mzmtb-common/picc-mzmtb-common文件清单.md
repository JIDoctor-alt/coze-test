# picc-mzmtb-common 文件清单索引

> 📌 common公共模块完整文件列表，便于快速定位

---

## common-core 核心基础模块

### 公共基础 (comm)

#### 实体基类 (comm/entity)
| 文件 | 一句话说明 |
|------|-----------|
| `BaseEntity.java` | **所有实体的老祖宗**（id/createtime/modifytime） |

#### 条件封装 (comm/condition)
| 文件 | 一句话说明 |
|------|-----------|
| `BaseCondition.java` | 查询条件基类 |
| `PageVo.java` | 分页参数（pageNum/pageSize） |

#### 服务基类 (comm/service)
| 文件 | 一句话说明 |
|------|-----------|
| `BaseService.java` | 服务接口定义 |
| `BaseServiceImpl.java` | **核心服务实现**（增删改查模板） |
| `BaseServiceDrImpl.java` | 支持逻辑删除的服务基类 |

#### 控制器基类 (comm/controller)
| 文件 | 一句话说明 |
|------|-----------|
| `CommonRestController.java` | 通用REST控制器基类 |

#### 工具类 (comm/util)
| 文件 | 一句话说明 |
|------|-----------|
| `PageUtil.java` | 分页工具类 |

---

### 配置类 (config)

#### 数据库配置 (config/jdbc)
| 文件 | 一句话说明 |
|------|-----------|
| `MyMapper.java` | **通用Mapper接口**（继承TkMyBatis） |
| `MyInsertListMapper.java` | 批量插入Mapper |
| `MyInsertListProvider.java` | 批量插入SQL提供者 |
| `BatisPlusConfig.java` | MyBatis Plus配置 |
| `TKMabatisConfig.java` | TkMyBatis配置 |
| `TransactionAdviceConfig.java` | 事务配置 |
| `PerformanceInterceptor.java` | SQL性能拦截器 |

#### Redis配置 (config/redis)
| 文件 | 一句话说明 |
|------|-----------|
| `RedisConfig.java` | **Redis配置**（序列化方式） |
| `FastJsonRedisSerializer.java` | FastJSON序列化器 |

#### HTTP配置 (config/call, config)
| 文件 | 一句话说明 |
|------|-----------|
| `RestTemplateConfig.java` | RestTemplate HTTP客户端配置 |
| `HttpClientProperties.java` | HTTP客户端属性配置 |

#### 参数解析 (config/resolver)
| 文件 | 一句话说明 |
|------|-----------|
| `MyHandlerMethodArgumentResolver.java` | **自定义参数解析**（@MyRequestBody） |
| `MethodArgumentCache.java` | 参数类型缓存 |
| `JackJsonConfig.java` | Jackson配置 |
| `annotation/MyRequestBody.java` | 自定义请求体注解 |
| `annotation/ExtCLass.java` | 扩展类型注解 |

#### 异常处理 (config/exception)
| 文件 | 一句话说明 |
|------|-----------|
| `RuntimeExceptionAdvice.java` | **全局异常处理器** |

#### 其他配置 (config)
| 文件 | 一句话说明 |
|------|-----------|
| `RequestConstant.java` | 请求常量 |
| `MessageSourceConfig.java` | 国际化配置 |
| `SwaggerConfiguration.java` | Swagger文档配置 |
| `SwaggerProperties.java` | Swagger属性 |
| `SecureFilter.java` | 安全过滤器 |
| `InterceptorConfig.java` | 拦截器配置 |
| `AutoConfigListener.java` | 自动配置监听器 |
| `ArrayJsonHandler.java` | 数组JSON处理器 |
| `JsonTypeHandler.java` | JSON类型处理器 |

#### 雪花ID (config/snowflake)
| 文件 | 一句话说明 |
|------|-----------|
| `PrimaryKeyUtil.java` | **分布式ID生成工具** |
| `SnowFlake.java` | 雪花算法实现 |

---

### 异常类 (exception)
| 文件 | 一句话说明 |
|------|-----------|
| `CustomException.java` | **自定义业务异常** |

### 枚举 (enums)
| 文件 | 一句话说明 |
|------|-----------|
| `StatusCode.java` | HTTP状态码枚举 |
| `DelFlagEnum.java` | 删除标志枚举 |
| `YesOrNoEnum.java` | 是否枚举 |
| `HqEnum.java` | 总部枚举 |
| `QuyiEnum.java` | 区域枚举 |

### 响应封装 (vo/http)
| 文件 | 一句话说明 |
|------|-----------|
| `ApiResponse.java` | **统一响应格式** |
| `Result.java` | 通用响应工具 |

---

## common-call 外部服务调用模块

### 核心服务 (module/call)
| 文件 | 一句话说明 |
|------|-----------|
| `SpringContext.java` | Spring上下文获取Bean |
| `BaseCallService.java` | 服务调用接口 |
| `BaseCallServiceImpl.java` | **服务调用实现**（路由到具体实现） |

#### 缓存 (module/call/cache)
| 文件 | 一句话说明 |
|------|-----------|
| `CallCacheUtils.java` | 调用配置缓存工具 |
| `ICallCache.java` | 缓存接口 |
| `CallCache.java` | 缓存实现 |
| `ApplicationCallCache.java` | 应用级缓存 |

#### 数据传输 (module/call/dto)
| 文件 | 一句话说明 |
|------|-----------|
| `InvokenBean.java` | 调用方法信息 |
| `JcSendMessageDto.java` | 消息发送DTO |

#### 模型 (module/call/model)
| 文件 | 一句话说明 |
|------|-----------|
| `LinkCallConfig.java` | **服务调用配置**（URL/方式/超时等） |

#### 配置 (config/call)
| 文件 | 一句话说明 |
|------|-----------|
| `CallProperties.java` | 调用属性配置 |
| `InvokeConfig.java` | 调用配置 |

#### 工具 (module/call/util)
| 文件 | 一句话说明 |
|------|-----------|
| `HttpClientUtil.java` | **HTTP客户端工具** |
| `RestCallUtils.java` | REST调用工具 |
| `DateUtil.java` | 日期工具 |
| `DataTransferUtil.java` | 数据转换工具 |
| `ReflectionUtil.java` | 反射工具 |
| `AuthorizationUtils.java` | 认证工具 |
| `ApiHeaderEnum.java` | API头信息枚举 |
| `SSLClient.java` | SSL客户端（普通） |
| `SSLClientqy.java` | SSL客户端（企业版） |
| `XyHosUtil.java` | 协议工具 |

### 一卡通 (module/onecard)
| 文件 | 一句话说明 |
|------|-----------|
| `ParamTransferUtil.java` | 参数转换工具 |
| `ResCodeConstant.java` | 响应码常量 |

### 服务实现 (module/call/service/impl)
| 文件 | 一句话说明 |
|------|-----------|
| `BaseCallApplictionServiceImpl.java` | 应用层调用基类 |
| `AXISCallServiceImpl.java` | AXIS WebService调用 |
| `FaceTokenCallServiceImpl.java` | 人脸Token服务 |
| `ImageMaskingCallServiceImpl.java` | 图片遮罩服务 |
| `ImageQualityCallServiceImpl.java` | 图片质量服务 |
| `JkdaCallServiceImpl.java` | 健康档案服务 |
| `JkscCallServiceImpl.java` | 健康生成服务 |
| `LTMessageCallServiceImpl.java` | 联通消息服务 |
| `MedicalImgClassifierCallServiceImpl.java` | 医学图像分类 |
| `MedicalInfoExtractionCallServiceImpl.java` | 医学信息提取 |
| `OcrWqxCallServiceImpl.java` | **OCR识别服务（文鼎无忌）** |
| `OcrWqxHukouProofCallServiceImpl.java` | OCR户口本识别 |
| `PrescriptionExtractionServiceImpl.java` | 处方提取服务 |
| `SealRecognitionCallServiceImpl.java` | 印章识别服务 |
| `SxMedicareCallServiceImpl.java` | 山西医保服务 |
| `VipChronicCallServiceImpl.java` | VIP慢病服务 |
| `WqxOutInterfaceCallServiceImpl.java` | 外接接口服务 |
| `WxCallServiceImpl.java` | 微信服务 |
| `WxxcxCallServiceImpl.java` | 微信小程序服务 |
| `cxcfInterfaceCallServiceImpl.java` | 创新服务 |

---

## common-utils 工具类模块

### 通用工具 (utils)
| 文件 | 一句话说明 |
|------|-----------|
| `JsonUtil.java` | **JSON处理工具** |
| `XmlUtil.java` | XML处理工具 |
| `XmlConstant.java` | XML常量 |
| `StringFileUtil.java` | 字符串文件互转 |
| `AESCrypt.java` | AES加密 |
| `LinkRuturnEntity.java` | 调用返回实体 |

### ID生成 (utils/ID)
| 文件 | 一句话说明 |
|------|-----------|
| `IdWorker.java` | **雪花算法ID** |
| `UUIDUtil.java` | UUID生成 |

### 字符串 (utils/string, utils)
| 文件 | 一句话说明 |
|------|-----------|
| `StringUtils.java` | **字符串工具**（判断/转换/编码） |
| `PassWordUtil.java` | 密码工具 |
| `SerializeUtils.java` | 序列化工具 |
| `UUIDUtil.java` | UUID工具 |

### 日期时间 (utils/date)
| 文件 | 一句话说明 |
|------|-----------|
| `DateUtil.java` | **日期工具**（转换/加减） |
| `DateTimeUtils.java` | 日期时间工具 |
| `DateUtils.java` | 日期工具 |
| `TimeUtil.java` | 时间工具 |

### 加密 (utils/encrypt)
| 文件 | 一句话说明 |
|------|-----------|
| `MD5Util.java` | **MD5加密** |
| `SHA1.java` | SHA1加密 |
| `Sha256.java` | SHA256加密 |

### 文件 (utils/file)
| 文件 | 一句话说明 |
|------|-----------|
| `FileUtils.java` | **文件操作**（读写/上传） |
| `Base64FileUtil.java` | Base64文件互转 |

### 财务 (utils/finance)
| 文件 | 一句话说明 |
|------|-----------|
| `FinanceUtils.java` | 财务计算基类 |
| `AverageCapitalUtils.java` | 等额本金计算 |
| `AverageCapitalPlusInterestUtils.java` | 等额本息计算 |
| `PMTUtil.java` | 等额Payment计算 |
| `Rate.java` | 利率计算 |

### Redis (utils/redis)
| 文件 | 一句话说明 |
|------|-----------|
| `RedisUtil.java` | **Redis操作工具** |
| `RedisKeyConf.java` | Key命名规范 |

### 请求 (utils/request)
| 文件 | 一句话说明 |
|------|-----------|
| `HttpRequest.java` | HTTP请求封装 |
| `SOAPUtil1.java` | SOAP请求 |

### SOAP (utils)
| 文件 | 一句话说明 |
|------|-----------|
| `SOAPUtil.java` | SOAP协议工具 |

### 日志 (utils/logback, utils/json)
| 文件 | 一句话说明 |
|------|-----------|
| `LogAspect.java` | 日志切面 |
| `AopLog.java` | 日志注解 |
| `LogUtils.java` | 日志工具 |

### 路径 (utils/path)
| 文件 | 一句话说明 |
|------|-----------|
| `Environment.java` | 环境变量 |
| `GetServerPort.java` | 获取服务端口 |

### Bean (utils/classzz)
| 文件 | 一句话说明 |
|------|-----------|
| `BeanUtils.java` | Bean属性拷贝 |
| `ClassUtil.java` | 类工具 |

### 集合 (utils/collection)
| 文件 | 一句话说明 |
|------|-----------|
| `CollectionUtils.java` | 集合工具 |

### IO (utils/io)
| 文件 | 一句话说明 |
|------|-----------|
| `IOUtils.java` | IO流工具 |

### FTP (utils/ftp)
| 文件 | 一句话说明 |
|------|-----------|
| `FtpUtil.java` | FTP上传下载 |

### XML (utils/xml)
| 文件 | 一句话说明 |
|------|-----------|
| `XmlUtil.java` | XML工具 |

### 通用实体 (entity)
| 文件 | 一句话说明 |
|------|-----------|
| `LinkRuturnEntity.java` | 服务调用返回实体 |

### 工具入口 (utils)
| 文件 | 一句话说明 |
|------|-----------|
| `Base64Util.java` | Base64工具 |
| `DesUtil.java` | DES加密 |
| `GenEntityUtil.java` | 实体生成工具 |
| `JacksonUtils.java` | Jackson工具 |
| `DateTimeUtils.java` | 日期时间工具 |

---

## 快速查询

### 想改数据库操作？
→ `comm/service/impl/BaseServiceImpl.java`

### 想加新的Redis操作？
→ `utils/redis/RedisUtil.java`

### 想改JSON处理？
→ `utils/JsonUtil.java` 或 `utils/JacksonUtils.java`

### 想加新的加密算法？
→ `utils/encrypt/` 目录

### 想调用外部服务？
```java
// 1. 配置 LinkCallConfig
// 2. 调用
LinkRuturnEntity result = baseCallService.callService("服务编码", params);
```

### 想生成唯一ID？
```java
@Autowired
private PrimaryKeyUtil primaryKeyUtil;

String id = primaryKeyUtil.snowFlakeKeyStr();
```

### 想统一响应格式？
→ `vo/http/ApiResponse.java`

### 想处理异常？
→ `config/exception/RuntimeExceptionAdvice.java`

### 想分页查询？
```java
PageVo page = new PageVo();
page.setPageNum(1);
page.setPageSize(10);
ResultPage<T> result = service.selectPage(entity, page);
```

---

## 核心依赖关系

```
BaseEntity
    ↑
PrivilegeUserInfo (业务实体)
    ↑
BaseServiceImpl<T extends BaseEntity>
    ↑
UserInfoServiceImpl (业务服务)
    ↑
LoginApi (控制器)
```

```
MyMapper (TkMyBatis)
    ↑
PrivilegeUserInfoDao (业务Dao)
    ↑
BaseServiceImpl (服务基类)
```

```
RedisConfig (配置)
    ↑
RedisUtil (工具类)
    ↑
业务服务 (注入使用)
```
