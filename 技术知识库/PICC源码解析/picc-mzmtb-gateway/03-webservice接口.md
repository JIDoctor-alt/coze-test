# picchealth/module/webservice - WebService接口模块

## 🎯 模块一句话说明
**对外XML接口** - 提供基于SOAP协议的WebService服务，供医保局、第三方系统调用

---

## 📁 模块结构

```
webservice/
├── enums/          ← 枚举定义
├── vo/            ← XML数据结构
│   ├── mb/        ← 慢病相关VO
│   ├── message/   ← 消息VO
│   ├── rexml/     ← 响应XML结构
│   ├── third/     ← 第三方对接VO
│   └── vipjghx/   ← 健管华夏VO
└── (顶层VO)
```

---

## 🔑 核心接口 (通过CXF发布)

### VipMbsbservice - 慢病信息同步

```java
@WebService
public interface VipMbsbservice {
    // 慢病信息同步
    String MBinfo(String xmlData);
}
```

### VipMedicalservice - 医疗信息服务

```java
@WebService
public interface VipMedicalservice {
    // 医疗信息服务
    String medicalservice(String xmlData);
}
```

---

## 📋 核心VO对象

### 1. XMLCom.java

> 🎯 SOAP通用头信息

### 这是啥？（小白版）
像"快递单头"，每个XML请求都带的基本信息。

### 结构
```xml
<XMLCom>
    <SYSCODE>系统编码</SYSCODE>
    <PASSWORD>密码</PASSWORD>
    <RESULTFLAG>结果标志</RESULTFLAG>
    <RESULTMSG>结果消息</RESULTMSG>
</XMLCom>
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| SYSCODE | String | 系统编码(用于验证) |
| PASSWORD | String | 密码 |
| RESULTFLAG | String | 结果标志(100100=成功) |
| RESULTMSG | String | 结果消息 |

---

### 2. XMLTable.java / XMLRecs.java

> 🎯 XML表格数据结构

### XMLTable - 表格容器
```xml
<XMLTable>
    <XMLCom>...</XMLCom>      <!-- 头信息 -->
    <XMLRecs>                  <!-- 数据记录 -->
        <XMLRec>...</XMLRec>
        <XMLRec>...</XMLRec>
    </XMLRecs>
</XMLTable>
```

### XMLRec - 单条记录
```xml
<XMLRec>
    <字段1>值1</字段1>
    <字段2>值2</字段2>
    ...
</XMLRec>
```

---

## 📦 mb子包 - 慢病相关VO

### MbinfoVo.java

> 🎯 慢病人员信息

```java
public class MbinfoVo {
    private String idCard;           // 身份证号
    private String name;             // 姓名
    private String chronicDisease;   // 慢性病名称
    private String cardNo;           // 卡号
    private String status;           // 状态
    private String startDate;        // 生效日期
    private String endDate;          // 失效日期
    // ... 更多字段
}
```

### MbinfoResVo.java

> 🎯 慢病查询响应

```java
public class MbinfoResVo {
    private String RESULTFLAG;      // 结果标志
    private String RESULTMSG;        // 结果消息
    private List<MbinfoVo> data;    // 慢病信息列表
}
```

### VipMBDeclareResVo.java

> 🎯 申报响应

```java
public class VipMBDeclareResVo {
    private String declareId;       // 申报ID
    private String status;          // 状态
    private String message;         // 消息
}
```

### 更多mb VO

| VO类 | 用途 |
|------|------|
| DiseaseInfoVo | 疾病信息 |
| HosInfoVo | 医院信息 |
| MBConsumeFlowResVo | 消费流水响应 |
| MbdeclareWorkunitResVo | 服务窗口响应 |
| PresInfoVo | 处方信息 |
| QueryDeclareComVo | 申报查询 |
| VipAccountVo | 账户信息 |
| VipCheckAuditFormResVo | 审核表单响应 |
| VipDrugstoreItemVo | 药店项目 |
| VipMbFileInfoVo | 附件信息 |
| VipQueryAuditFormListResVo | 审核表单列表 |
| VipQueryIcdListVo | ICD列表 |
| VipQueryMBDeclareVo | 申报查询 |
| WorkunitForPageVo | 服务窗口 |

---

## 📦 third子包 - 第三方对接VO

### R0001-R0013 请求/响应

> 🎯 第三方接口报文

| 请求类 | 响应类 | 说明 |
|--------|--------|------|
| R0001RequestVo | R0001ResponseVo | 查询客户基本信息 |
| R0002RequestVo | R0002ResponsetVo | 查询客户银行信息 |
| R0003RequestVo | R0003ResponseVo | 查询保单信息 |
| R0004RequestVo | R0004ResponseVo | 查询计划信息 |
| R0005RequestVo | R0005ResponseVo | 查询计划明细 |
| R0006RequestVo | R0006ResponseVo | 查询发票信息 |
| R0007RequestVo | (内嵌) | 保全申请 |
| R0008RequestVo | (内嵌) | 保全确认 |
| R0009RequestVo | R0009ResponseVo | 查询保全信息 |
| R0010RequestVo | R0010ResponseVo | 查询理赔信息 |
| R0011RequestVo | R0011ResponseVo | 查询理赔明细 |
| R0012RequestVo | R0012ResponseVo | 查询理赔结论 |
| R0013RequestVo | R0013ResponseVo | 查询理赔清单 |

### 示例：R0001ResponseVo

```java
public class R0001ResponseVo {
    private String RESULTFLAG;      // 结果标志
    private String RESULTMSG;        // 结果消息
    private MEMBERVo member;        // 客户信息
    private List<ProductsVo> products;  // 产品列表
}
```

### 内部结构类

| 类名 | 说明 |
|------|------|
| MEMBERVo | 客户会员信息 |
| ProductsVo | 产品信息 |
| ProductVo | 单个产品 |
| ClinicDetailsResponseVo | 门诊明细响应 |
| ClinicDetailsVo | 门诊明细 |
| ClinicFeesResponseVo | 门诊费用响应 |
| ClinicFeesVo | 门诊费用 |
| PatientinfoVo | 患者信息 |
| PayInfosVo | 支付信息列表 |
| PayinfoVo | 支付信息 |
| DataPartVo | 数据部分 |
| PagePartVo | 分页部分 |
| P0005RequestVo | P0005请求 |

---

## 📦 message子包 - 消息推送VO

### MessageVo.java

> 🎯 消息推送数据

```java
public class MessageVo {
    private String phone;           // 手机号
    private String messageType;     // 消息类型
    private String content;         // 内容
    private String sendTime;        // 发送时间
    private String templateId;      // 模板ID
}
```

### 消息类型

| 类型 | 说明 |
|------|------|
| SMS | 短信 |
| WECHAT | 微信模板消息 |
| PUSH | App推送 |

---

## 📦 vipjghx子包 - 健管华夏VO

### VipFindServcieTimeVo.java

> 🎯 服务时间查询

### VipFindServcieVo.java

> 🎯 服务查询

---

## 🔧 WebService发布配置

### CxfConfig.java

> 🎯 CXF服务发布配置

```java
@Configuration
public class CxfConfig {
    @Autowired
    private Bus bus;
    
    @Autowired
    private VipMbsbservice vipMbsbservice;
    
    @Bean
    public Endpoint vipMbsbservice() {
        EndpointImpl endpoint = new EndpointImpl(bus, vipMbsbservice);
        // 添加拦截器
        endpoint.getInInterceptors().add(new NameSpaceChecker());  // 命名空间检查
        endpoint.getInInterceptors().add(new ReadSoapHeader());   // 读取SOAP头
        endpoint.publish("/mbsbservice");  // 发布路径
        return endpoint;
    }
}
```

### 发布的服务

| 服务名 | 发布路径 | 说明 |
|--------|----------|------|
| mbsbservice | /mbsbservice | 慢病信息服务 |
| medicalservice | /medicalservice | 医疗信息服务 |
| outservice | /outservice | 外部服务 |

---

## 🔐 SOAP安全机制

### NameSpaceChecker.java

> 🎯 SOAP命名空间检查

### ReadSoapHeader.java

> 🎯 SOAP头信息读取

### WSSoapHeaderUtil.java

> 🎯 SOAP头工具

---

## 📝 WebService调用示例

### 请求示例
```xml
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Header>
        <SYSCODE>VIP_SYSTEM</SYSCODE>
        <PASSWORD>password123</PASSWORD>
    </soap:Header>
    <soap:Body>
        <MBinfo>
            <idCard>110101199001011234</idCard>
        </MBinfo>
    </soap:Body>
</soap:Envelope>
```

### 响应示例
```xml
<MBinfoResponse>
    <RESULTFLAG>100100</RESULTFLAG>
    <RESULTMSG>成功</RESULTMSG>
    <Data>
        <idCard>110101199001011234</idCard>
        <name>张三</name>
        <chronicDisease>高血压</chronicDisease>
        <cardNo>MB20240001</cardNo>
    </Data>
</MBinfoResponse>
```

---

## 📚 知识点

### SOAP vs REST

| 方面 | SOAP | REST |
|------|------|------|
| 协议 | W3C标准 | HTTP约定 |
| 格式 | XML固定格式 | JSON/XML都行 |
| 复杂度 | 较高 | 较简单 |
| 适用场景 | 老系统、大企业 | 新项目、互联网 |

### SOAP拦截器
```java
// 入站拦截器处理流程
1. NameSpaceChecker - 检查命名空间是否正确
2. ReadSoapHeader - 读取并验证认证信息
3. 业务方法执行
```

### XML与JSON转换
- 使用 Xml2JsonVisitor 转换XML为JSON
- 使用 Json2XmlVistor 转换JSON为XML

---

## 🔗 调用关系

```
外部系统 (医保局/保险公司)
        ↓ SOAP请求
    CXF网关 (/mbsbservice)
        ↓
VipMbsbserviceImpl 
        ↓
HmLinkWebserviceBL.runComWebsToRef()
        ↓
REST转发到后端服务
        ↓
业务处理 → 数据库
```

---

## 🎯 小白理解要点

1. **WebService是XML接口** - 老系统不支持JSON只能用XML
2. **每个请求都有头信息** - 包含认证信息(SYSCODE/PASSWORD)
3. **响应有固定格式** - RESULTFLAG标识成功/失败
4. **需要CXF发布** - 才能被外部调用
5. **第三方对接复杂** - 有几十种报文类型

---

**相关文档**:
- `00-项目概览.md` - 整体架构
- `01-config配置类.md` - CXF配置
