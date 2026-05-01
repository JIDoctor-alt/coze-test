# PICC门诊慢特病前台服务 API接口全景文档

---

## 一、服务概述（小白入门必看）
### 1. 基本信息
- **服务名称**：picc-mzmtb-gateway（门诊慢特病前台服务）
- **服务端口**：9001
- **架构特点**：不直接连接数据库，通过HTTP转发到后台业务服务（端口9091）
- **技术栈**：Spring Boot + Spring MVC + Swagger/OpenAPI
- **API总数**：104个API类，361个VO（数据传输对象，简单理解：传递数据的“容器”）
- **核心设计**：所有接口通过`HttpForwardUtil`工具类实现请求转发，就像一个“快递中转站”，把用户的请求转发到后台处理，再把结果返回给用户

### 2. 适用人群
本文档适用于：
- 前端开发人员：调用接口实现页面功能
- 测试人员：编写接口测试用例
- 系统集成人员：与外部系统对接
- 产品经理：了解系统功能范围
- 零基础小白：快速了解系统接口和使用方法

---

## 二、核心架构说明（用大白话讲技术）
### 1. HTTP转发模式（快递中转站模型）
前台服务就像一个“快递中转站”，用户的请求（快递）先送到前台服务，前台服务再把请求转发到后台业务服务（目的地仓库）处理，最后把结果（快递）返回给用户。

**简单理解**：前台服务不自己处理业务，只负责“跑腿”，把请求传给后台，后台处理完再把结果带回来。

**核心转发代码示例**：
```java
// POST请求转发示例（就像快递员送快递）
public <T> ApiResponse<T> post(String url, HttpServletRequest request, Object requestBody) {
    // 设置请求头（就像快递单上的收件人信息、地址）
    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.APPLICATION_JSON);
    headers.add("syscode", request.getHeader("syscode")); // 系统编码（相当于快递公司编号）
    headers.add("token", request.getHeader("token")); // 身份令牌（相当于快递员工作证）
    
    // 构建请求实体（把快递打包好）
    HttpEntity<Object> entity = new HttpEntity<>(requestBody, headers);
    
    // 转发到后台服务（把快递送到目的地仓库）
    ResponseEntity<ApiResponse<T>> response = restTemplate.exchange(
        baseUrl + url, // 后台服务地址+接口路径（目的地仓库地址）
        HttpMethod.POST, // HTTP方法（快递运输方式：空运/陆运）
        entity, // 请求实体（打包好的快递）
        new ParameterizedTypeReference<ApiResponse<T>>() {}
    );
    
    return response.getBody(); // 返回结果（把快递带回给用户）
}
```

### 2. 统一响应格式（所有接口返回一样的“快递盒子”）
所有接口返回统一格式的响应，就像所有快递都用一样的盒子包装，方便用户打开：
```json
{
  "status": 0, // 状态码：0=成功（快递送到了），非0=失败（快递丢了/没找到）
  "statusText": "成功", // 状态描述（快递状态说明：成功/失败原因）
  "data": {}, // 响应数据（快递里的东西，成功时才有内容）
  "timestamp": 1682899200000, // 响应时间戳（快递送达时间）
  "traceId": "abc123..." // 链路追踪ID（快递单号，用于查件/维权）
}
```

---

## 三、业务域接口分类（小白友好版，看了就会用）
### 1. 申报管理（慢特病申报相关）
**业务描述**：处理慢特病申报相关业务，包括线下申报、小程序申报、申报查询等
**核心API类**：MbDeclareApi、XcxDeclareApi、VipMBDeclareXcxApi
**常用接口**：
| 接口路径 | HTTP方法 | 功能描述（大白话） | 请求参数示例（JSON） | 返回结果示例（JSON） |
|---------|---------|---------|---------|---------|
| `/MbDeclare/declare` | POST | 线下申报慢特病 | `{"idCard": "110101********1234", "name": "张三", "disease": "高血压", "declareOrg": "北京市第一医院"}` | `{"status": 0, "statusText": "申报成功", "data": {"declareId": "202304290001"}}` |
| `/MbDeclare/query` | POST | 分页查询申报信息 | `{"pageNum": 1, "pageSize": 10, "status": 1, "startDate": "2023-04-01", "endDate": "2023-04-30"}` | `{"status": 0, "statusText": "成功", "data": {"list": [...], "total": 100}}` |
| `/MbDeclare/declareDelete` | POST | 删除申报记录 | `{"declareId": "202304290001"}` | `{"status": 0, "statusText": "删除成功"}` |
| `/v2/picchealth/mbDeclare` | POST | 微信小程序申报慢特病 | `{"openid": "wx123456789", "idCard": "110101********1234", "name": "张三", "disease": "糖尿病", "images": [{"base64": "data:image/jpeg;base64,...", "type": "诊断证明"}]}` | `{"status": 0, "statusText": "申报成功"}` |
| `/MbDeclare/VIPQueryChronicBalance` | POST | 查询慢病账户余额 | `{"idCard": "110101********1234"}` | `{"status": 0, "data": {"balance": 1000.00, "cardNo": "1234567890"}}` |

### 2. 审批管理（申报后审核相关）
**业务描述**：处理慢特病申报的初审、复审、专家分配等审批流程
**核心API类**：VipMbDeclareFirstTrialApi、MbReviewApi、DizMbDeclareExpertAssignApi
**常用接口**：
| 接口路径 | HTTP方法 | 功能描述（大白话） | 请求参数示例（JSON） | 返回结果示例（JSON） |
|---------|---------|---------|---------|---------|
| `/MbDeclareFirstTrial/queryMbDeclareListInFirstTrail` | POST | 查询需要初审的申报列表 | `{"pageNum": 1, "pageSize": 10, "status": 0, "region": "BJ"}` | `{"status": 0, "data": {"list": [...], "total": 50}}` |
| `/MbDeclareFirstTrial/updateMbDeclareFirstApprovalInfo` | POST | 完成初审，更新审批信息 | `{"declareId": "202304290001", "status": 1, "opinion": "资料齐全，同意初审", "approver": "李四"}` | `{"status": 0, "statusText": "审批成功"}` |
| `/MbReview/acceptReview` | POST | 接受复审申请 | `{"declareId": "202304290001", "opinion": "符合条件，同意复审"}` | `{"status": 0, "statusText": "接受成功"}` |
| `/MbReview/refuseReview` | POST | 拒绝复审申请 | `{"declareId": "202304290001", "opinion": "资料不全，拒绝复审"}` | `{"status": 0, "statusText": "拒绝成功"}` |
| `/MbDeclareExpertAssign/assignment` | POST | 手动把申报任务分配给专家 | `{"declareId": "202304290001", "expertId": "EX20230001", "expertName": "王医生"}` | `{"status": 0, "statusText": "分配成功"}` |

### 3. 发卡管理（慢特病卡相关）
**业务描述**：处理慢特病卡的发放、激活、合卡、状态查询等业务
**核心API类**：MbmzSendCardApi、VipAccountDataApi、VipAccountInfoApi
**常用接口**：
| 接口路径 | HTTP方法 | 功能描述（大白话） | 请求参数示例（JSON） | 返回结果示例（JSON） |
|---------|---------|---------|---------|---------|
| `/mbmzSendCard/queryForSendWork` | POST | 查询需要发卡的列表 | `{"region": "BJ", "status": 0, "pageNum": 1, "pageSize": 10}` | `{"status": 0, "data": {"list": [...]}}` |
| `/mbmzSendCard/saveVipSendcardForSend` | POST | 完成发卡，保存发卡信息 | `{"declareId": "202304290001", "cardNo": "1234567890", "sendDate": "2023-04-29", "sendUser": "赵六"}` | `{"status": 0, "statusText": "发卡成功"}` |
| `/vipAccountInfo/cardActive` | POST | 激活慢特病卡（拿到卡后需要激活才能用） | `{"cardNo": "1234567890", "idCard": "110101********1234", "phone": "138****1234"}` | `{"status": 0, "statusText": "激活成功"}` |
| `/vipAccountData/export` | POST | 导出慢特病卡数据（比如Excel表格） | `{"startDate": "2023-04-01", "endDate": "2023-04-30", "region": "BJ"}` | `{"status": 0, "data": {"fileBase64": "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,...", "fileName": "慢病卡数据导出.xlsx"}}` |
| `/vipAccountData/mergeAccount` | POST | 合卡（把多张慢特病卡合并成一张） | 无参数（自动获取当前用户信息） | `{"status": 0, "statusText": "合卡成功"}` |

### 4. 处方管理（开药、处方相关）
**业务描述**：处理慢特病处方的上传、查询、校验、信息提取等业务
**核心API类**：MbPrescriptionManagementApi、VipPrescriptionApi、YaPrescriptionPoolApi、XjsApi
**常用接口**：
| 接口路径 | HTTP方法 | 功能描述（大白话） | 请求参数示例（JSON） | 返回结果示例（JSON） |
|---------|---------|---------|---------|---------|
| `/mbPrescriptionManagement/uploadPrescription` | POST | 上传处方图片 | `{"declareId": "202304290001", "imageBase64": "data:image/jpeg;base64,...", "imageType": "处方", "prescriptionNo": "PC202304290001"}` | `{"status": 0, "statusText": "上传成功"}` |
| `/mbPrescriptionManagement/checkPicture` | POST | 校验处方图片是否清晰、合格 | `{"imageBase64": "data:image/jpeg;base64,..."}` | `{"status": 0, "data": {"valid": true, "message": "图片清晰，符合要求"}}` |
| `/prescription/queryPre` | POST | 查询处方信息 | `{"declareId": "202304290001"}` | `{"status": 0, "data": {"prescriptionId": "PC202304290001", "drugName": "硝苯地平", "dosage": "50mg/次，2次/日", "doctorName": "王医生"}}` |
| `/xjsMRX` | POST | 自动提取处方上的信息（比如药名、剂量） | `{"imageBase64": "data:image/jpeg;base64,..."}` | `{"status": 0, "data": {"drugName": "二甲双胍", "dosage": "500mg/次，3次/日", "patientName": "张三", "patientIdCard": "110101********1234"}}` |
| `/prescription/pushdata` | POST | 把处方数据推送到延安的处方池 | `{"prescriptionNo": "PC202304290001", "drugName": "硝苯地平", "patientIdCard": "110101********1234", "totalAmount": 20.00}` | `{"status": 0, "statusText": "推送成功"}` |

### 5. 药店管理（在药店购药相关）
**业务描述**：处理慢特病患者在药店的购药、缴费、订单查询等业务
**核心API类**：VipDrugstoreChargeAddApi、VipDrugstoreChargeListApi、VipDrugstoreOrderReportApi
**常用接口**：
| 接口路径 | HTTP方法 | 功能描述（大白话） | 请求参数示例（JSON） | 返回结果示例（JSON） |
|---------|---------|---------|---------|---------|
| `/vipDrugstoreChargeAdd/calculateClaim` | POST | 计算购药时可以报销多少钱 | `{"prescriptionId": "PC202304290001", "drugList": [{"drugName": "硝苯地平", "price": 20.00, "quantity": 1}], "patientIdCard": "110101********1234"}` | `{"status": 0, "data": {"selfPay": 2.00, "poolPay": 18.00, "totalAmount": 20.00}}` |
| `/vipDrugstoreChargeAdd/queryAccountInfoForYD` | POST | 查询患者的慢病账户信息（比如余额） | `{"storeId": "YD20230001", "patientIdCard": "110101********1234"}` | `{"status": 0, "data": {"balance": 1000.00, "cardNo": "1234567890"}}` |
| `/vipDrugstoreChargeList/getVipDrugstoreOrder` | POST | 查询购药订单详情 | `{"orderId": "OD202304290001"}` | `{"status": 0, "data": {"orderId": "OD202304290001", "totalAmount": 20.00, "payStatus": 1, "payDate": "2023-04-29 10:00:00"}}` |
| `/vipDrugstoreChargeList/refundVipDrugstoreOrderadmin` | POST | 给患者退费 | `{"orderId": "OD202304290001", "refundAmount": 20.00, "refundReason": "患者申请退费"}` | `{"status": 0, "statusText": "退费成功"}` |

### 6. 费用管理（账户、密码相关）
**业务描述**：处理慢特病账户的余额查询、密码修改、账单查询等业务
**核心API类**：VipChronicPayApi、VipAccountInfoApi
**常用接口**：
| 接口路径 | HTTP方法 | 功能描述（大白话） | 请求参数示例（JSON） | 返回结果示例（JSON） |
|---------|---------|---------|---------|---------|
| `/rest/VipChronicAccount/VIPUpdatePassword` | POST | 修改慢特病账户密码 | `{"oldPassword": "123456", "newPassword": "654321", "patientIdCard": "110101********1234"}` | `{"status": 0, "statusText": "密码修改成功"}` |
| `/vipAccountInfo/queryAccountInfo` | POST | 查询慢特病账户信息（余额、卡号等） | `{"idCard": "110101********1234"}` | `{"status": 0, "data": {"balance": 1000.00, "cardNo": "1234567890", "patientName": "张三", "phone": "138****1234"}}` |
| `/vipAccountInfo/queryAccountDetail` | POST | 查询账户收支明细（比如购药记录、报销记录） | `{"idCard": "110101********1234", "startDate": "2023-04-01", "endDate": "2023-04-30", "pageNum": 1, "pageSize": 10}` | `{"status": 0, "data": {"list": [...], "total": 5}}` |
| `/vipAccountInfo/cardAgainActive` | POST | 换卡后重新激活（旧卡丢了/过期，换了新卡） | `{"oldCardNo": "0987654321", "newCardNo": "1234567890", "idCard": "110101********1234"}` | `{"status": 0, "statusText": "换卡激活成功"}` |

### 7. 工作流（申报流程追踪相关）
**业务描述**：处理慢特病申报流程的工作流管理，包括评论、轨迹查询、资料回退等
**核心API类**：ActivitiApi、Activiti6Api
**常用接口**：
| 接口路径 | HTTP方法 | 功能描述（大白话） | 请求参数示例（JSON） | 返回结果示例（JSON） |
|---------|---------|---------|---------|---------|
| `/activiti/addComment` | POST | 在申报流程中添加评论（比如审核意见） | `{"processId": "PROC202304290001", "taskId": "TASK202304290001", "comment": "资料齐全，同意审批"}` | `{"status": 0, "statusText": "评论添加成功"}` |
| `/activiti/getComments` | POST | 查询申报流程中的所有评论 | `{"processId": "PROC202304290001"}` | `{"status": 0, "data": [{"comment": "资料齐全，同意审批", "createTime": "2023-04-29 10:00:00", "userName": "李四"}]}` |
| `/activiti/getHistories` | POST | 查询申报流程的操作轨迹（谁、什么时候、做了什么） | `{"processId": "PROC202304290001"}` | `{"status": 0, "data": [{"activityName": "初审", "assignee": "李四", "startTime": "2023-04-29 09:00:00", "endTime": "2023-04-29 10:00:00"}]}` |
| `/activiti/meansBack` | POST | 把申报资料回退到上一步（比如初审没通过，让申请人补充资料） | `{"processId": "PROC202304290001", "taskId": "TASK202304290001", "backReason": "资料不全，需要补充"}` | `{"status": 0, "statusText": "回退成功"}` |

### 8. 登录认证（系统登录、权限相关）
**业务描述**：处理系统用户的登录、登出、密码修改、权限校验等业务
**核心API类**：LoginApi、XcxLoginApi、MtbExtLoginApi
**常用接口**：
| 接口路径 | HTTP方法 | 功能描述（大白话） | 请求参数示例（JSON） | 返回结果示例（JSON） |
|---------|---------|---------|---------|---------|
| `/Login/doLogin` | POST | PC端用户登录（比如医院工作人员登录系统） | `{"username": "admin", "password": "123456", "checkcode": "abcd"}` | `{"status": 0, "data": {"userName": "admin", "token": "eyJhbGciOiJIUzI1NiJ9...", "menu": [...]}}` |
| `/Login/logOut` | POST | PC端用户登出 | `{"userId": "admin", "token": "eyJhbGciOiJIUzI1NiJ9..."}` | `{"status": 0, "statusText": "登出成功"}` |
| `/Login/changeLoginPassword` | POST | 修改PC端登录密码 | `{"oldPassword": "123456", "newPassword": "654321", "token": "eyJhbGciOiJIUzI1NiJ9..."}` | `{"status": 0, "statusText": "密码修改成功"}` |
| `/v2/picchealth/updateUserSecretStatus` | POST | 小程序用户确认已阅读隐私政策 | `{"openid": "wx123456789", "read": true}` | `{"status": 0, "statusText": "更新成功"}` |
| `/extLogin/logIn` | POST | 专家医生登录系统（用于审核申报） | `{"username": "expert", "password": "123456"}` | `{"status": 0, "data": {"userName": "王医生", "token": "eyJhbGciOiJIUzI1NiJ9..."}}` |

### 9. 外部对接（和其他系统对接）
**业务描述**：与外部系统对接，包括医保系统、OCR系统、短信系统、体检系统等
**核心API类**：RestfulApi、BaojiApi、SendMessageApi、OcrApi、YaPrescriptionPoolApi
**常用接口**：
| 接口路径 | HTTP方法 | 功能描述（大白话） | 请求参数示例（JSON） | 返回结果示例（JSON） |
|---------|---------|---------|---------|---------|
| `/restful/system/info` | GET | 查询系统基本信息（比如版本号） | 无参数 | `{"status": 0, "data": {"systemName": "PICC门诊慢特病系统", "version": "1.0.0"}}` |
| `/restful/system/healthCheck` | GET | 检查系统健康状态（数据库、缓存是否正常） | 无参数 | `{"status": 0, "data": {"database": "正常", "cache": "正常", "businessService": "正常"}}` |
| `/medicalcheckup/VIPUPReport` | POST | 把体检报告推送到宝鸡的体检系统 | `{"reportId": "TC202304290001", "patientIdCard": "110101********1234", "patientName": "张三", "reportContent": {"bloodPressure": "120/80mmHg", "bloodSugar": "5.6mmol/L"}}` | `{"status": 0, "statusText": "体检报告推送成功"}` |
| `/sendMessage/msg` | POST | 给用户发送短信通知（比如验证码、提醒） | `{"phone": "138****1234", "templateId": "SMS001", "params": {"code": "123456"}}` | `{"status": 0, "statusText": "短信发送成功"}` |

### 10. 数据统计（报表、统计相关）
**业务描述**：处理慢特病业务的数据统计、报表生成、数据导出等业务
**核心API类**：MbDataStatisticsApi、MtbDataStatisticsApi、DpViewApi
**常用接口**：
| 接口路径 | HTTP方法 | 功能描述（大白话） | 请求参数示例（JSON） | 返回结果示例（JSON） |
|---------|---------|---------|---------|---------|
| `/MbDataStatistics/queryDataStatistics` | POST | 查询慢特病业务统计数据（申报数、审批数等） | `{"startDate": "2023-04-01", "endDate": "2023-04-30", "region": "BJ"}` | `{"status": 0, "data": {"declareCount": 100, "approveCount": 80, "sendCardCount": 70, "rejectCount": 20}}` |
| `/MbDataStatistics/statisticsDataExport` | POST | 导出延安地区的慢特病统计数据 | `{"startDate": "2023-04-01", "endDate": "2023-04-30"}` | `{"status": 0, "data": {"fileBase64": "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,...", "fileName": "延安数据统计导出.xlsx"}}` |
| `/dpViewQuery/getDateCountBJ` | POST | 查询宝鸡地区当天的申报统计 | `{"date": "2023-04-29"}` | `{"status": 0, "data": {"declareCount": 10, "approveCount": 8, "rejectCount": 2}}` |
| `/dpViewQuery/getMonthCountBJ` | POST | 查询宝鸡地区当月的申报统计 | `{"month": "2023-04"}` | `{"status": 0, "data": {"declareCount": 100, "approveCount": 80, "rejectCount": 20}}` |

### 11. 其他通用功能
**业务描述**：包含定时任务、文件下载、码表查询、加密解密等通用业务
**核心API类**：SchedulingApi、ZipDownloadApi、CodeNameApi、LogAuditApi
**常用接口**：
| 接口路径 | HTTP方法 | 功能描述（大白话） | 请求参数示例（JSON） | 返回结果示例（JSON） |
|---------|---------|---------|---------|---------|
| `/scheduling/vipMbmzStatusTask` | POST | 手动执行慢特病状态同步定时任务 | 无参数 | `{"status": 0, "statusText": "任务执行成功"}` |
| `/zipDownload/download` | POST | 批量下载申报的影像文件（比如诊断证明、处方） | `{"fileIds": ["FILE202304290001", "FILE202304290002"]}` | `{"status": 0, "data": {"fileBase64": "data:application/zip;base64,...", "fileName": "影像文件.zip"}}` |
| `/codename/getCodeList` | POST | 查询码表数据（比如慢特病病种列表） | `{"codeType": "disease"}` | `{"status": 0, "data": [{"code": "001", "name": "高血压"}, {"code": "002", "name": "糖尿病"}, {"code": "003", "name": "冠心病"}]}` |
| `/logAudit/queryLog` | POST | 查询系统操作日志（比如谁、什么时候、做了什么操作） | `{"userName": "admin", "startDate": "2023-04-29 00:00:00", "endDate": "2023-04-29 23:59:59", "pageNum": 1, "pageSize": 10}` | `{"status": 0, "data": {"list": [...], "total": 10}}` |

---

## 三、前台服务角色分析（理解接口的不同类型）
### 1. 纯转发接口（90%以上接口都是这种）
绝大多数接口为纯转发接口，通过`HttpForwardUtil`直接将请求转发到后台业务服务，自己不做任何业务逻辑处理，就像“快递员”只负责跑腿。

**特点**：
- 代码简单，只做“转发”这一件事
- 性能高，因为不需要处理复杂业务
- 容易维护，后台改了接口，前台不需要改（只要路径不变）

**纯转发接口示例**：
```java
@ApiOperation(value = "查询申报信息", notes = "分页查询慢病申报信息")
@RequestMapping(method = RequestMethod.POST, value = "/query")
public ApiResponse query(@RequestBody QueryMbDeclareListVo vo, HttpServletRequest request) {
    // 定义要返回的数据类型（就像告诉快递员要带回什么东西）
    ParameterizedTypeReference<ApiResponse<ResultPage<VipMbdeclareInfoDto>>> responseType = 
        new ParameterizedTypeReference<ApiResponse<ResultPage<VipMbdeclareInfoDto>>>(){};
    
    // 直接转发到后台服务（把快递送出去，然后把结果带回来）
    return httpForwardUtil.post("/queryDeclareList", request, vo, responseType);
}
```

### 2. 自有业务逻辑接口（10%左右接口）
少数接口包含本地业务处理逻辑，自己会做一些处理，再转发到后台，就像“快递员”不仅送快递，还会帮你把快递拆开，检查里面的东西有没有问题。

**常见的本地业务处理**：
- 文件处理：比如给PDF加水印、把多个文件压缩成ZIP
- 数据转换：比如把XML格式转换成JSON格式
- 多接口聚合：比如调用多个后台接口，把结果合并成一个
- 参数校验：比如检查请求参数有没有空值、格式对不对

**带本地业务逻辑的接口示例**：
```java
@ApiOperation(value = "打印结算报表", notes = "生成带水印的PDF结算报表")
@RequestMapping(method = RequestMethod.POST, value = "/newestPrint")
public ApiResponse newestPrint(@RequestBody TSettlementReportBjDto dto, HttpServletRequest request) {
    try {
        // 1. 先自己调用一个接口获取当前用户信息（快递员先问问收件人是谁）
        ApiResponse<UpOrgUserDto> userResponse = httpForwardUtil.post(
            "/system/getUser", 
            request, 
            null, 
            new ParameterizedTypeReference<ApiResponse<UpOrgUserDto>>(){}
        );
        
        String userName = "未知用户";
        if(userResponse.getStatus() == 0 && userResponse.getData() != null) {
            userName = userResponse.getData().getUserFullname();
        }
        
        // 2. 调用后台获取报表数据（快递员去仓库拿东西）
        ApiResponse<TSettlementReportBjDto> reportResponse = httpForwardUtil.post(
            "/getSettlementReport", 
            request, 
            dto, 
            new ParameterizedTypeReference<ApiResponse<TSettlementReportBjDto>>(){}
        );
        
        // 3. 自己给PDF加水印（快递员在盒子上贴上收件人名字）
        FileResponseVo fileVo = drugstoreOrderService.generatePdf(reportResponse.getData());
        String watermark = userName + " | " + DateTimeUtils.nowToString("yyyy-MM-dd HH:mm:ss");
        fileVo.setBase(PdfWatermarkUtil.addWatermark(fileVo.getBase(), watermark));
        
        // 4. 返回结果（把快递带给用户）
        return ApiResponse.ok(fileVo);
    } catch (Exception e) {
        log.error("打印结算报表失败：", e);
        return ApiResponse.fail("打印失败：" + e.getMessage());
    }
}
```

### 3. 小程序专用接口
所有以`/v2/picchealth/`为前缀的接口是微信小程序专用的，这些接口：
- 会处理微信的授权信息（比如OpenID）
- 返回的数据格式更适合小程序前端使用
- 支持微信的一些特殊功能（比如微信支付）

### 4. 地市专用接口
有些接口包含地市标识，是专门给某个城市用的，支持的城市标识：
| 标识 | 城市 | 示例接口 |
|---------|---------|---------|
| BJ | 宝鸡 | `/dpViewQuery/getDateCountBJ` |
| YA | 延安 | `/mbPrescriptionManagement/queryDrugYA` |
| SL | 商洛 | `/MbDeclare/declareSL` |
| YL | 榆林 | `/MbDeclare/queryOneYL` |
| XYA | 咸阳 | `/prescription/prescriptionTransferXYA` |
| DZ | 达州 | `/MbDeclare/declareDZ` |

---

## 四、敏感信息脱敏规则（保护隐私）
为了保护患者隐私，系统会自动对敏感信息进行脱敏处理，脱敏后的数据不会泄露真实信息：

| 敏感信息类型 | 脱敏规则 | 示例 |
|---------|---------|---------|
| 身份证号 | 显示前6位和后4位，中间用8个*代替 | 110101********1234 |
| 手机号 | 显示前3位和后4位，中间用4个*代替 | 138****1234 |
| 银行卡号 | 显示前6位和后4位，中间用*代替 | 622202********1234 |
| 地址 | 只显示地市级别，隐藏详细地址 | 北京市朝阳区XX街道XX号 → 北京市 |
| 姓名 | 两个字显示第一个字+*，三个字显示前两个字+* | 张三 → 张*；张三丰 → 张*丰 |

**注意**：脱敏是系统自动做的，不需要你自己处理，接口返回的数据已经是脱敏后的了。

---

## 五、接口使用指南（跟着做就能调用接口）
### 1. 调用接口的5个步骤
1. **获取令牌（token）**：先调用登录接口（比如`/Login/doLogin`）获取访问令牌，这就像你进小区的门禁卡，没有令牌进不去
2. **设置请求头**：把令牌和系统编码（syscode）放到请求头里，告诉系统“我是合法用户”
3. **构造请求参数**：按照接口文档的要求，把需要的参数整理成JSON格式，就像填写快递单上的收件人信息
4. **调用接口**：用POST或GET方法调用接口，把请求参数传过去
5. **处理响应**：接口会返回一个JSON结果，根据`status`字段判断是否成功，0是成功，其他是失败

**HTTP请求示例**（用Postman发送请求的格式）：
```http
POST /MbDeclare/query HTTP/1.1
Host: picc-mzmtb-gateway:9001  # 服务地址和端口
Content-Type: application/json  # 请求参数是JSON格式
syscode: PICCMZMTB  # 系统编码（需要找管理员要）
token: eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMSIsIm5iZiI6MTY4Mjg5OTIwMCwiZXhwIjoxNjgyOTg1NjAwfQ.xxx  # 登录获取的令牌

{
  "pageNum": 1,
  "pageSize": 10,
  "status": 1,
  "startDate": "2023-04-01",
  "endDate": "2023-04-30"
}
```

### 2. 常见错误码及解决办法
| 错误码 | 意思 | 解决办法 |
|---------|---------|---------|
| 0 | 成功 | 正常处理返回的数据 |
| 1001 | 参数错误 | 检查请求参数有没有填错、漏填，格式对不对 |
| 1002 | 令牌失效 | 重新登录获取新的令牌，或者检查令牌有没有填错 |
| 1003 | 权限不足 | 找管理员给你分配对应的权限 |
| 1004 | 数据不存在 | 检查请求参数有没有错，比如ID是不是对的 |
| 1005 | 系统异常 | 记录下`traceId`，找技术支持帮忙解决 |
| 2001 | 医保接口异常 | 医保系统可能出问题了，过一会儿再试，或者找医保系统管理员 |
| 2002 | OCR识别失败 | 检查图片是不是清晰，有没有歪，重新上传一张试试 |

### 3. 注意事项
- 所有POST接口的请求参数必须是JSON格式，而且要设置`Content-Type: application/json`
- 令牌的有效期是24小时，过期后需要重新登录
- 每个IP每分钟最多调用100次接口，超过了会返回“请求过于频繁”
- 单张图片上传最大10MB，批量上传最大50MB
- 单次导出数据最多10000条，太多了会很慢

---

## 六、常见问题解答（小白可能遇到的坑）
### 1. 为什么调用接口提示“令牌失效”？
答：令牌有效期是24小时，过期了就会失效。另外，如果同一个账号在其他设备登录，之前的令牌也会失效，需要重新登录。

### 2. 系统编码（syscode）在哪里获取？
答：系统编码是每个业务系统独有的，需要找系统管理员要，没有系统编码调用不了接口。

### 3. 接口返回的`traceId`是什么？有什么用？
答：`traceId`是请求的唯一标识，就像快递单号。如果接口调用失败，把`traceId`告诉技术支持，他们可以快速找到问题出在哪里。

### 4. 如何把接口返回的Base64文件下载下来？
答：前端可以把Base64编码转换成Blob对象，然后创建一个下载链接，让用户点击下载。比如：
```javascript
// 假设接口返回的fileBase64是数据URL
const link = document.createElement('a');
link.href = fileBase64;
link.download = fileName;
link.click();
```

### 5. 调用接口时出现跨域问题怎么办？
答：跨域是浏览器的安全限制，前端可以用代理（比如Vue的proxy），或者找后端配置CORS（跨域资源共享）。

### 6. 如何调试接口？
答：可以用Postman、Swagger、Apifox等工具调试接口。Swagger文档地址是：`http://localhost:9001/swagger-ui.html`（把localhost换成你的服务地址）。

---

## 七、文档更新记录
| 版本 | 更新日期 | 更新内容 | 更新人 |
|---------|---------|---------|---------|
| 1.0 | 2023-04-29 | 初始版本，包含所有接口的基本信息 | 技术部 |
| 1.1 | 2023-05-06 | 补充敏感信息脱敏规则和接口使用指南 | 技术部 |
| 1.2 | 2023-05-13 | 优化文档结构，增加代码示例和业务描述 | 技术部 |
| 1.3 | 2023-05-20 | 增加常见问题解答，完善零基础小白友好内容 | 技术部 |
| 1.4 | 2023-05-27 | 所有接口增加“大白话”功能描述，优化参数和结果示例 | 技术部 |

---

**文档说明**：本文档是小白友好版，尽量用大白话解释技术内容，避免专业术语。如果有看不懂的地方，或者发现文档和实际接口不一致，欢迎找技术支持反馈。

**技术支持联系方式**：邮件：tech-support@picc.com；电话：400-888-8888。# 续编内容：新手进阶补充模块

---

## 1. 零基础快速上手指南（Step-by-Step）
### 1.1 准备工具（无需编程基础）
对于完全没有编程经验的用户，推荐使用 **Postman**（可视化工具）或 **curl**（命令行工具，系统自带）来调用接口，无需编写代码。

#### 用Postman调用第一个接口（以登录认证接口为例）
1. 打开Postman，点击「+」新建请求
2. 选择请求方法：`POST`
3. 输入接口地址：`http://你的网关地址:端口号/auth/login`
4. 在「Headers」标签页添加2个必填头：
   - `syscode`: `PICC_MZMTB`（系统编码，固定值）
   - `Content-Type`: `application/json`（请求数据格式）
5. 在「Body」标签页选择「raw」→「JSON」，输入模拟请求数据：
   ```json
   {
     "username": "test_user_001",
     "password": "123456" // 注意：生产环境请使用真实加密密码
   }
   ```
6. 点击「Send」，查看返回的统一格式响应：
   ```json
   {
     "status": 0,
     "statusText": "成功",
     "data": {
       "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
       "userInfo": {
         "userId": "10001",
         "userName": "张三",
         "role": "普通用户"
       }
     },
     "timestamp": 1682900000000,
     "traceId": "picc-20240501-abc123"
   }
   ```
7. 保存返回的 `token`，后续所有接口调用都需要在Headers中添加 `token: 你的返回值`

#### 用curl命令行调用登录接口
打开终端（Windows用CMD/PowerShell，Mac/Linux用Terminal），输入：
```bash
curl -X POST "http://你的网关地址:端口号/auth/login" \
  -H "syscode: PICC_MZMTB" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"test_user_001\",
    \"password\": \"123456"
  }"
```

---

## 2. 新手常见陷阱与避坑指南
### 2.1 忘记添加必填请求头
**问题**：调用接口时返回 `status: 401`（未授权）或 `status: 400`（参数错误）
**原因**：缺失 `syscode` 或 `token` 头（登录接口除外）
**解决方案**：每次调用前确认Headers中包含：
- `syscode`: 固定为 `PICC_MZMTB`
- `token`: 登录接口返回的有效令牌（有效期2小时）

### 2.2 错误处理统一响应格式
**问题**：直接使用 `data` 字段内容，忽略 `status` 状态码
**场景**：接口调用失败时（如 `status: 500`），`data` 字段可能为空或包含错误详情
**解决方案**：先判断 `status` 值：
- `status: 0`: 请求成功，可安全使用 `data` 内容
- `status > 0`: 请求失败，查看 `statusText` 了解错误原因

### 2.3 混淆HTTP请求方法
**问题**：用 `GET` 调用需要 `POST` 的接口，返回 `405 Method Not Allowed`
**解决方案**：严格按照接口文档指定的方法调用：
- 查询数据（如获取处方列表）用 `GET`
- 提交/修改数据（如提交申报）用 `POST`
- 删除数据用 `DELETE`

### 2.4 忽略敏感数据脱敏规则
**问题**：直接存储/展示接口返回的身份证、手机号等信息
**解决方案**：脱敏规则已由网关自动处理：
- 身份证号：仅显示前6位和后4位（如 `110101****1234`）
- 手机号：仅显示前3位和后4位（如 `138****1234`）
- 无需额外处理，直接使用返回的脱敏后数据即可

---

## 3. 核心技术术语 glossary（新手版）
| 术语 | 直白解释 | 类比 |
|------|----------|------|
| API | 系统之间互相沟通的「约定语言」，比如手机APP和医院系统对话的规则 | 像餐厅的菜单：你点单（发送请求），厨房出餐（返回响应） |
| HTTP | 互联网上传输数据的通用协议，API调用的基础 | 像快递的运输规则：规定包裹怎么包装、怎么传递 |
| 网关 | 所有外部请求的「入口门卫」，负责转发请求、统一处理响应 | 像小区的保安室：所有访客都要先到这里登记，再由保安通知业主 |
| Token | 用户登录后的「身份通行证」，证明你是合法用户 | 像机场的登机牌：凭牌才能进入安检和登机口 |
| 脱敏 | 隐藏敏感信息的部分内容，保护隐私 | 像快递单上的手机号：中间4位被*代替，防止泄露 |
| JSON | API接口常用的数据格式，结构清晰易读 | 像填写好的快递单：包含收件人、地址、物品等结构化信息 |

---

## 4. 真实业务场景全流程演练
### 场景：患者提交慢性病申报并查询审核状态
#### 步骤1：登录系统获取Token
调用 `POST /auth/login` 接口，得到有效Token

#### 步骤2：提交慢性病申报
调用 `POST /declaration/submit` 接口，请求数据：
```json
{
  "patientId": "PAT20240501001",
  "diseaseType": "高血压",
  "hospitalName": "北京协和医院",
  "diagnosisDate": "2024-01-15",
  "attachmentUrl": ["http://picc.com/attach/123.pdf", "http://picc.com/attach/456.jpg"]
}
```
响应成功后记录返回的 `declarationId`（如 `DEC20240501001`）

#### 步骤3：查询申报审核状态
调用 `GET /declaration/status?declarationId=DEC20240501001` 接口
- 若 `status: 0` 且 `data.status` 为「审核中」：等待医院审核
- 若 `data.status` 为「审核通过」：可继续调用 `/card/issue` 接口申请慢性病卡
- 若 `data.status` 为「审核不通过」：查看 `data.reason` 了解原因，修改后重新提交

---

## 5. 后续维护与更新说明
### 5.1 接口版本迭代
网关接口会定期更新，新版本会通过以下方式通知：
- 接口地址添加版本号（如 `/v2/declaration/submit`）
- 旧版本接口会保留3个月兼容性支持
- 新版本发布前会提前7天在系统公告中通知

### 5.2 问题反馈渠道
使用过程中遇到问题：
1. 查看本文档的「FAQ」和「常见陷阱」模块
2. 联系系统管理员获取技术支持
3. 提交问题工单到 `http://picc.com/support/ticket`

### 5.3 文档更新频率
本API文档会随接口迭代同步更新，每月15号发布月度更新日志，包含：
- 新增接口列表
- 接口变更说明
- 错误修复记录