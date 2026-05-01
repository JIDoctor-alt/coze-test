# picchealth/module/ws - WebService实现模块

## 🎯 模块一句话说明
**WebService服务实现** - CXF发布的WebService接口的具体业务实现，18个文件

---

## 📁 模块结构

```
ws/
├── adapter/         ← 适配器 (8个)
├── common/         ← 公共工具 (8个)
├── service/        ← 服务接口与实现
│   └── impl/       ← 服务实现 (3个)
```

---

## 🔑 核心服务接口与实现

### 1. VipMbsbservice.java

> 🎯 慢病信息服务接口

```java
@WebService
public interface VipMbsbservice {
    // 慢病信息同步
    String MBinfo(String xmlData);
}
```

---

### 2. VipMbsbserviceImpl.java

> 🎯 慢病信息服务实现

### 这是啥？（小白版）
像"翻译员"，把外部XML请求转成内部能处理的格式。

```java
@Component
@Slf4j
@WebService(
    endpointInterface = "com.picchealth.module.ws.service.VipMbsbservice",
    serviceName = "mbsbservice",
    targetNamespace = "http://service.ws.module.picchealth.com/"
)
public class VipMbsbserviceImpl implements VipMbsbservice {
    
    @Override
    public String MBinfo(String xmlData) {
        try {
            String url = "/rest/vipMbsb/mbinfo";
            // 调用业务逻辑处理
            return HmLinkWebserviceBL.runComWebsToRef(xmlData, url);
        } catch (Exception e) {
            log.error("MBinfo", e);
        }
        return null;
    }
}
```

---

### 3. VipMedicalserviceImpl.java

> 🎯 医疗服务实现

```java
@Component
@WebService(
    endpointInterface = "com.picchealth.module.ws.service.VipMedicalservice",
    serviceName = "medicalservice"
)
public class VipMedicalserviceImpl implements VipMedicalservice {
    
    @Override
    public String medicalservice(String xmlData) {
        // 业务处理
        return HmLinkWebserviceBL.runComWebsToRef(xmlData, "/rest/medical/service");
    }
}
```

---

### 4. VipOutServiceImpl.java

> 🎯 外部服务实现

```java
@Component
@WebService(
    endpointInterface = "com.picchealth.module.ws.service.VipOutService",
    serviceName = "outservice"
)
public class VipOutServiceImpl implements VipOutService {
    
    @Override
    public String outservice(String xmlData) {
        // 业务处理
        return HmLinkWebserviceBL.runComWebsToRef(xmlData, "/rest/out/service");
    }
}
```

---

## 🔧 适配器模式

### Adapter.java

> 🎯 适配器基类

```java
public interface Adapter {
    // 适配方法
    Object adapt(Object input);
}
```

---

### BaseAdapter.java

> 🎯 适配器基类实现

```java
public abstract class BaseAdapter implements Adapter {
    
    @Override
    public Object adapt(Object input) {
        // 通用适配逻辑
        return doAdapt(input);
    }
    
    // 子类实现具体适配逻辑
    protected abstract Object doAdapt(Object input);
}
```

---

### 具体适配器 (7个)

| 适配器 | 用途 |
|--------|------|
| JG005Adapter | JG005接口适配 |
| JG007Adapter | JG007接口适配 |
| R0010Adapter | R0010接口适配 |
| R0012Adapter | R0012接口适配 |
| SC001Adapter | SC001接口适配 |

#### 示例：R0010Adapter.java

```java
@Component
public class R0010Adapter extends BaseAdapter {
    
    @Override
    protected Object doAdapt(Object input) {
        // R0010特定处理逻辑
        // 转换请求格式
        // 调用服务
        // 转换响应格式
        return result;
    }
}
```

---

## 🛠️ 公共工具类 (8个)

### 1. CxfConfig.java

> 🎯 CXF服务配置

### 这是啥？（小白版）
像"服务发布台"，把WebService发布到网络上供外部调用。

```java
@Configuration
public class CxfConfig {
    
    @Autowired
    private Bus bus;
    
    @Autowired
    private VipMbsbservice vipMbsbservice;
    
    @Autowired
    private VipMedicalservice vipMedicalservice;
    
    @Autowired
    private VipOutService vipOutService;
    
    // 发布慢病服务
    @Bean
    public Endpoint vipMbsbservice() {
        EndpointImpl endpoint = new EndpointImpl(bus, vipMbsbservice);
        // 添加入站拦截器
        endpoint.getInInterceptors().add(new NameSpaceChecker());
        endpoint.getInInterceptors().add(new ReadSoapHeader());
        endpoint.publish("/mbsbservice");
        return endpoint;
    }
    
    // 发布医疗服务
    @Bean
    public Endpoint medicalservice() {
        EndpointImpl endpoint = new EndpointImpl(bus, vipMedicalservice);
        endpoint.publish("/medicalservice");
        return endpoint;
    }
    
    // 发布外部服务
    @Bean
    public Endpoint outservice() {
        EndpointImpl endpoint = new EndpointImpl(bus, vipOutService);
        endpoint.publish("/outservice");
        return endpoint;
    }
}
```

---

### 2. NameSpaceChecker.java

> 🎯 SOAP命名空间检查

```java
public class NameSpaceChecker extends AbstractPhaseInterceptor<SoapMessage> {
    
    public NameSpaceChecker() {
        super(Phase.PRE_INVOKE);  // 在调用前执行
    }
    
    @Override
    public void handleMessage(SoapMessage message) {
        // 检查SOAP消息的命名空间
        // 验证是否匹配预期格式
    }
}
```

### 为什么需要检查命名空间？
- 防止恶意请求
- 确保消息格式正确
- 避免版本不兼容

---

### 3. ReadSoapHeader.java

> 🎯 SOAP头信息读取

```java
public class ReadSoapHeader extends AbstractPhaseInterceptor<SoapMessage> {
    
    public ReadSoapHeader() {
        super(Phase.PRE_INVOKE);
    }
    
    @Override
    public void handleMessage(SoapMessage message) {
        // 从SOAP Header中提取认证信息
        SoapHeader header = message.getHeader(new QName("SYSCODE"));
        String syscode = header.getStringContent();
        
        SoapHeader headerPwd = message.getHeader(new QName("PASSWORD"));
        String password = headerPwd.getStringContent();
        
        // 验证认证信息
        validateAuth(syscode, password);
    }
}
```

### SOAP Header格式
```xml
<soap:Header>
    <SYSCODE>VIP_SYSTEM</SYSCODE>
    <PASSWORD>password123</PASSWORD>
</soap:Header>
```

---

### 4. WSSoapHeader.java

> 🎯 SOAP头信息结构

```java
public class WSSoapHeader {
    private String syscode;    // 系统编码
    private String password;   // 密码
    private String timestamp;  // 时间戳
    private String signature;  // 签名
}
```

---

### 5. WSSoapHeaderUtil.java

> 🎯 SOAP头工具

```java
public class WSSoapHeaderUtil {
    
    // 构建SOAP头
    public static WSSoapHeader buildHeader(String syscode, String password);
    
    // 验证SOAP头
    public static boolean validateHeader(WSSoapHeader header);
    
    // 签名验证
    public static boolean verifySignature(String data, String signature);
}
```

---

### 6. RestfulForwardUtil.java

> 🎯 REST转发工具

```java
public class RestfulForwardUtil {
    
    // 转发REST请求
    public JSONObject postByJson(String url, String jsonData) {
        // 发送HTTP POST请求
        // 返回JSON响应
    }
    
    // GET请求
    public JSONObject get(String url) {
        // 发送HTTP GET请求
    }
}
```

---

### 7. Xml2JsonVisitor.java

> 🎯 XML转JSON访问器

```java
public class Xml2JsonVisitor {
    
    // XML字符串转JSON对象
    public static JSONObject convert(String xmlString) {
        // 解析XML
        // 构建JSON
    }
    
    // 带命名空间的XML转换
    public static JSONObject convertWithNS(String xmlString, String namespace);
}
```

---

## 🔄 服务调用流程

```
外部系统 (医保局/保险公司)
        ↓ SOAP请求(XML)
┌───────────────────────────────────────┐
│            CXF网关层                  │
│  ┌─────────────────────────────┐      │
│  │   NameSpaceChecker          │      │  ← 验证命名空间
│  │   ReadSoapHeader           │      │  ← 读取认证信息
│  └─────────────────────────────┘      │
└───────────────────┬───────────────────┘
                    ↓
┌───────────────────────────────────────┐
│           服务实现层                   │
│  ┌─────────────────────────────┐      │
│  │   VipMbsbserviceImpl        │      │
│  │   VipMedicalserviceImpl     │      │
│  │   VipOutServiceImpl         │      │
│  └─────────────────────────────┘      │
└───────────────────┬───────────────────┘
                    ↓
┌───────────────────────────────────────┐
│           业务逻辑层                   │
│  ┌─────────────────────────────┐      │
│  │   HmLinkWebserviceBL        │      │
│  └─────────────────────────────┘      │
└───────────────────┬───────────────────┘
                    ↓ REST/内部调用
        ┌───────────┴───────────┐
        ↓                       ↓
┌───────────────┐      ┌───────────────┐
│   后端服务    │      │   数据库      │
└───────────────┘      └───────────────┘
```

---

## 📝 知识点

### 1. CXF拦截器链
```
1. IN - 入站拦截器
   ├─ LogicalHandler (逻辑处理)
   └─ SoapHandler (SOAP处理)
       ├─ NameSpaceChecker (命名空间检查)
       └─ ReadSoapHeader (读取认证)
   
2. INVOKE - 服务调用
   
3. OUT - 出站拦截器
   └─ 处理响应
```

### 2. 适配器模式
- 把不兼容的接口适配成统一的接口
- 便于扩展新的接口类型
- 解耦请求处理逻辑

### 3. SOAP vs HTTP
- SOAP是基于HTTP的应用协议
- SOAP消息必须符合XML格式
- SOAP有标准的信封结构

---

## 📁 文件清单

### Service接口 (3个)
```
VipMbsbservice     - 慢病服务接口
VipMedicalservice  - 医疗服务接口
VipOutService      - 外部服务接口
```

### Service实现 (3个)
```
VipMbsbserviceImpl
VipMedicalserviceImpl
VipOutServiceImpl
```

### Adapter (8个)
```
Adapter           - 适配器基类接口
BaseAdapter       - 适配器基类
JG005Adapter
JG007Adapter
R0010Adapter
R0012Adapter
SC001Adapter
(其他适配器)
```

### Common (8个)
```
CxfConfig
NameSpaceChecker
ReadSoapHeader
WSSoapHeader
WSSoapHeaderUtil
RestfulForwardUtil
Xml2JsonVisitor
(其他工具)
```

---

## 🎯 小白理解要点

1. **WebService是XML接口** - 外部系统通过XML调用
2. **CXF是发布平台** - 把Java服务发布成WebService
3. **拦截器做安全检查** - 验证命名空间和认证信息
4. **适配器做格式转换** - 把不同格式转成统一格式

---

**相关文档**:
- `00-项目概览.md` - 整体架构
- `03-webservice接口.md` - WebService接口定义
