# picchealth/module/restful - REST接口模块

## 🎯 模块一句话说明
**第三方REST对接** - 与外部系统(医保局、医院HIS系统)的JSON接口对接

---

## 📁 模块结构

```
restful/
├── api/            ← 接口控制器 (6个)
├── enums/          ← 枚举定义
├── service/         ← 服务层
│   └── impl/       ← 服务实现
├── utils/          ← 工具类
└── vo/             ← 数据对象
    ├── causacloud/ ← causacloud对接
    ├── ocr/        ← OCR识别
    └── test/       ← 测试用
```

---

## 🔑 核心API接口

### 1. RestfulApi.java

> 🎯 REST通用接口

### 这是啥？（小白版）
像"万能转接头"，把外部系统的请求转换成内部能处理的格式。

### 核心方法
```java
@RestController
@RequestMapping("/rest")
public class RestfulApi {
    // 系统授权接口
    @PostMapping("/sys/interfaceGrant")
    
    // 转发外部请求到内部
    @PostMapping("/**")
    public ApiResponse forward(@RequestBody String requestJson, HttpServletRequest request) {
        // 1. 读取请求头
        // 2. 转发到对应服务
        // 3. 返回结果
    }
}
```

---

### 2. BaojiApi.java

> 🎯 宝鸡医保对接

### 这是啥？（小白版）
专门对接陕西宝鸡市医保系统的接口。

### 核心接口
```java
@Api(tags = "宝鸡医保接口")
@RestController
@RequestMapping("/baoji")
public class BaojiApi {
    // 宝鸡医保查询
    // 宝鸡医保申报
    // 宝鸡医保审核
}
```

---

### 3. OcrApi.java

> 🎯 OCR文字识别接口

### 这是啥？（小白版）
像"拍照识字"，上传图片自动识别文字。

### 核心接口
```java
@Api(tags = "OCR识别")
@RestController
@RequestMapping("/ocr")
public class OcrApi {
    // 身份证识别
    @PostMapping("/idCard")
    ApiResponse idCard(@RequestBody OcrRequestVo vo);
    
    // 发票识别
    @PostMapping("/invoice")
    ApiResponse invoice(@RequestBody OcrRequestVo vo);
    
    // 银行卡识别
    @PostMapping("/bankCard")
    ApiResponse bankCard(@RequestBody OcrRequestVo vo);
}
```

### OCR使用场景
- 参保人上传身份证自动提取信息
- 发票OCR识别自动录入
- 病历文字提取

---

### 4. SendMessageApi.java

> 🎯 消息推送接口

### 这是啥？（小白版）
像"短信发送器"，给用户发短信/微信模板消息。

### 核心接口
```java
@Api(tags = "消息推送")
@RestController
@RequestMapping("/sendMessage")
public class SendMessageApi {
    // 发送短信
    @PostMapping("/sms")
    ApiResponse sendSms(@RequestBody SmsRequestVo vo);
    
    // 发送微信模板消息
    @PostMapping("/wechat")
    ApiResponse sendWechat(@RequestBody WechatRequestVo vo);
}
```

---

### 5. WqxStructuredDataApi.java

> 🎯 卫企信结构化数据

### 核心接口
```java
@Api(tags = "卫企信接口")
@RestController
@RequestMapping("/wqx")
public class WqxStructuredDataApi {
    // 提交结构化数据
    // 查询结构化数据
}
```

---

### 6. YaPrescriptionPoolApi.java

> 🎯 雅安处方池接口

### 这是啥？（小白版）
四川雅安地区的处方查询接口。

---

## 🔧 Service层

### RestfulService.java

> 🎯 REST服务接口

```java
public interface RestfulService {
    // 处理外部请求
    ApiResponse processRequest(String xmlData);
    
    // 查询数据
    ApiResponse queryData(QueryRequest request);
}
```

### RestfulServiceImpl.java

> 🎯 REST服务实现

```java
@Service
@Slf4j
public class RestfulServiceImpl implements RestfulService {
    @Override
    public ApiResponse processRequest(String xmlData) {
        // 1. 解析XML
        // 2. 调用业务服务
        // 3. 返回结果
    }
}
```

---

## 📋 VO对象说明

### causacloud子包

| VO类 | 用途 |
|------|------|
| CausaCloudRequestVo | 请求参数 |
| CausaCloudResponseVo | 响应参数 |

### ocr子包

| VO类 | 用途 |
|------|------|
| OcrRequestVo | OCR请求(图片Base64) |
| OcrResponseVo | OCR响应(识别的文字) |

### test子包

| VO类 | 用途 |
|------|------|
| TestRequestVo | 测试请求 |
| TestResponseVo | 测试响应 |

---

## 🔧 工具类

### RestfulForwardUtil.java

> 🎯 REST转发工具

```java
@Component
public class RestfulForwardUtil {
    // 转发JSON请求
    public JSONObject postByJson(String url, String jsonData, HttpServletRequest request) {
        // 添加认证头
        // 发送HTTP POST请求
        // 返回JSON响应
    }
    
    // 转发XML请求
    public JSONObject postByXml(String url, String xmlData, HttpServletRequest request) {
        // 转换XML
        // 添加认证头
        // 发送请求
    }
}
```

### JsonAndXmlTools.java

> 🎯 JSON与XML互转

```java
public class JsonAndXmlTools {
    // JSON转XML
    public static String json2Xml(String json);
    
    // XML转JSON
    public static String xml2Json(String xml);
}
```

---

## 📝 知识点

### 1. REST接口特点
- 使用JSON格式
- HTTP标准方法(GET/POST)
- 无状态通信
- 轻量级

### 2. 第三方对接流程
```
外部系统 → REST请求(JSON) → RestfulApi 
        ↓
   解析请求 → 业务处理
        ↓
   返回JSON响应
```

### 3. OCR识别应用
```
用户上传身份证照片
        ↓
Base64编码 → OCR接口
        ↓
返回身份证信息(姓名/身份证号/地址)
        ↓
自动填充表单
```

---

## 🔗 与WebService的区别

| 方面 | REST | WebService |
|------|------|------------|
| 协议 | HTTP | SOAP |
| 格式 | JSON | XML |
| 复杂度 | 简单 | 复杂 |
| 适用 | 新系统 | 老系统 |
| 性能 | 较高 | 较低 |

---

## 📁 文件清单

### API (6个)
```
BaojiApi          - 宝鸡医保对接
OcrApi            - OCR识别
RestfulApi        - REST通用接口
SendMessageApi    - 消息推送
WqxStructuredDataApi - 卫企信接口
YaPrescriptionPoolApi - 雅安处方池
```

### Service (2个)
```
RestfulService    - 服务接口
RestfulServiceImpl - 服务实现
```

### Utils (1个)
```
RestfulForwardUtil - REST转发工具
```

---

## 🎯 小白理解要点

1. **REST是JSON接口** - 比XML更轻量
2. **OCR是拍照识字** - 自动提取图片中的文字
3. **消息推送是发短信** - 通知用户审核结果等
4. **第三方对接需要转换** - 把外部格式转成内部格式

---

**相关文档**:
- `00-项目概览.md` - 整体架构
- `03-webservice接口.md` - WebService接口
