# PICC门诊慢特病业务服务(picc-mzmtb-server)工作流与外部对接深度解析

> **作者**：Claude Code  
> **版本**：1.0  
> **解析目标**：Activiti 6.0.0 工作流引擎 + 14个BPMN流程 + 四大外部系统对接 + 26个定时任务

---

## 📖 目录

1. [技术架构概览](#1-技术架构概览)
2. [Part 1：BPMN工作流深度解析](#2-part-1bpmn工作流深度解析)
3. [Part 2：外部系统对接深度解析](#3-part-2外部系统对接深度解析)
4. [Part 3：定时任务详解](#4-part-3定时任务详解)
5. [业务术语对照表](#5-业务术语对照表)

---

## 1. 技术架构概览

### 1.1 核心技术栈

```
┌─────────────────────────────────────────────────────────────┐
│                        整体架构                               │
├─────────────────────────────────────────────────────────────┤
│  前端接入层    │ 微信小程序 │ 移动端H5 │ 第三方系统API        │
├─────────────────────────────────────────────────────────────┤
│  网关拦截层    │ XcxInterceptorConfig(小程序签名拦截)         │
├─────────────────────────────────────────────────────────────┤
│  业务服务层    │ Activiti 6.0.0 工作流 │ Spring Boot        │
├─────────────────────────────────────────────────────────────┤
│  数据访问层    │ MyBatis │ Redis缓存 │ MySQL                 │
├─────────────────────────────────────────────────────────────┤
│  外部对接层    │ HIS系统 │ 医保核心 │ 短信平台 │ 微信小程序    │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 项目结构

```
picc-mzmtb-server/
├── picchealth-server/          # 主服务模块
│   └── src/main/
│       ├── java/com/picchealth/
│       │   ├── module/
│       │   │   ├── mb/           # 慢病业务模块
│       │   │   ├── scheduling/    # 定时任务模块
│       │   │   ├── basedoc/      # 基础文档模块
│       │   │   └── drugstore/    # 药店模块
│       │   └── config/           # 配置类
│       └── resources/
│           └── processes/        # BPMN流程文件 (13个)
├── picchealth-db/              # 数据库访问模块
└── mtb-yh/                     # 智能任务处理模块
```

### 1.3 Activiti核心服务类

| Service类 | 用途 | 核心方法 |
|-----------|------|---------|
| `TaskService` | 任务管理 | claim(), complete(), addComment() |
| `RuntimeService` | 流程运行 | startProcessInstanceByKey() |
| `HistoryService` | 历史记录 | createHistoricTaskInstanceQuery() |
| `RepositoryService` | 流程定义 | getBpmnModel() |

---

## 2. Part 1：BPMN工作流深度解析

> **小白化理解**：BPMN流程就像工厂的流水线图纸，规定了每一步该做什么、谁来负责、满足什么条件往下走。

### 2.1 13个BPMN流程文件清单

| 流程ID | 流程名称 | 所属地区 | 用途说明 |
|--------|----------|----------|----------|
| `bjmbfs` | 宝鸡慢病复审流程 | 陕西宝鸡 | 慢病患者定期复审的审批流程 |
| `bjmbsb` | 宝鸡慢病申报流程 | 陕西宝鸡 | 新患者慢病资格申请 |
| `dizmbsb` | 第三人慢病申报 | 通用 | 代他人申报慢病资格 |
| `jcmbsb` | 进程慢病申报 | 通用 | 进度查询相关流程 |
| `jjmbsb` | 静静慢病申报 | 通用 | 静静地区慢病申报 |
| `jzmbsb` | 精准慢病申报 | 通用 | 精准扶贫慢病申报 |
| `mzlmbsb` | 慢病种类慢病申报 | 通用 | 按病种分类申报 |
| `slmbsb` | 商洛慢病申报 | 陕西商洛 | 商洛地区特有的慢病申报 |
| `xyambsb` | 咸阳慢病申报 | 陕西咸阳 | 咸阳地区慢病申报 |
| `yambsb` | 延安慢病申报 | 陕西延安 | 延安地区慢病申报 |
| `ylimbsb` | 榆林慢病申报 | 陕西榆林 | 榆林地区慢病申报 |
| `ylmbsb` | 医疗慢病申报 | 通用 | 医疗相关慢病申报 |
| `zjkmbsb` | 专家看病慢病申报 | 通用 | 专家会诊类申报 |

### 2.2 核心流程详解

#### 2.2.1 宝鸡慢病复审流程(bjmbfs) - ASCII流程图

```
                    ┌─────────────────────────────────────────┐
                    │           开始 (startevent1)             │
                    └───────────────────┬─────────────────────┘
                                        │
                                        ▼
                    ┌─────────────────────────────────────────┐
                    │    岔路口网关 (exclusivegateway5)        │
                    │    根据 startType 判断流程走向            │
                    └───────────────────┬─────────────────────┘
                       │                                    │
           ┌───────────┴───────────┐          ┌──────────────┴──────────────┐
           │ startType == 1        │          │ startType == 2               │
           ▼                       ▼          ▼                              ▼
    ┌──────────────┐       ┌──────────────┐  ┌──────────────┐       ┌──────────────┐
    │  W2002 复审预警 │       │  W2003 复审管理 │  └──────┬───────┘       │   结束流程    │
    └──────┬───────┘       └──────┬───────┘         │              └──────────────┘
           │                      │                 │
           └──────────────────────┴─────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────────────────┐
                    │    岔路口网关 (exclusivegateway1)         │
                    │    根据 reviewStatus 判断处理结果          │
                    └───────────────────┬─────────────────────┘
                      │       │       │       │       │
          ┌───────────┴───┐   │   ┌───┴───────┐   │
          │ reviewStatus==2│   │   │reviewStatus│   │
          ▼                │   │   │  ==3      │   │
    ┌──────────────┐        │   │   ▼           │   │
    │ W3001 慢病体检 │        │   │ ┌──────────┐ │   │
    └──────┬───────┘        │   │ │结束(拒绝) │ │   │
           │                │   │ └──────────┘ │   │
           ▼                │   │              │   │
    ┌──────────────┐        │   │              │   │
    │岔路口(exclusivegateway2)│  │              │   │
    │体检状态判断      │        │   │              │   │
    └──────┬───────┘        │   │              │   │
     │      │      │        │   │              │   │
     ▼      ▼      ▼        │   │              │   │
  ┌────┐ ┌────┐ ┌────┐      │   │              │   │
  │完成│ │未到│ │放弃│      │   │              │   │
  │    │ │    │ │    │      │   │              │   │
  ▼    ▼ ▼    ▼ └────┘      │   │              │   │
 ┌──────────┐                │   │              │   │
 │W4001专家审核│              │   │              │   │
 └────┬─────┘                │   │              │   │
      │                      │   │              │   │
      └──────────────────────┴───┴──────────────┘
                              │
                              ▼
                      ┌──────────────┐
                      │    结束       │
                      └──────────────┘
```

**流程变量说明**：

| 变量名 | 类型 | 含义 |
|--------|------|------|
| `startType` | Integer | 启动类型：1=复审预警, 2=再次复审 |
| `reviewStatus` | Integer | 复审状态：2=接受复审, 3=拒绝复审, 4=复审失效, -1=无效复审 |
| `physicalStatus` | Integer | 体检状态：1=完成, 2=未到, 3=放弃 |
| `physicalCount` | Integer | 未到次数统计 |

#### 2.2.2 流程节点角色配置

| 节点ID | 节点名称 | 角色类型 | 说明 |
|--------|----------|----------|------|
| W2002 | 复审预警 | 用户任务 | 发送给相关人员进行复审提醒 |
| W2003 | 复审管理 | 用户任务 | 复审管理人员处理 |
| W3001 | 慢病体检 | 用户任务 | 安排患者进行体检 |
| W4001 | 专家审核 | 用户任务 | 专家对体检结果进行审核 |

### 2.3 业务代码与工作流交互

#### 2.3.1 启动流程

```java
// 代码位置: VipMbdeclareInfoServiceImpl.java
ProcessInstance instance = runtimeService.startProcessInstanceByKey(
    processKey,           // 流程定义Key，如 "bjmbsb"
    businessKey,          // 业务主键(申报单ID)
    variables            // 流程变量
);
```

#### 2.3.2 完成任务

```java
// 认领任务
taskService.claim(taskId, userId);
// 设置流程变量
Map<String, Object> variables = new HashMap<>();
variables.put("reviewStatus", 2);
// 完成任务
taskService.complete(taskId, variables);
```

#### 2.3.3 查询待办任务

```java
// 按业务Key查询当前任务
List<Task> tasks = taskService.createTaskQuery()
    .processInstanceBusinessKey(businessKey)
    .list();

// 按用户查询待办
List<Task> tasks = taskService.createTaskQuery()
    .taskAssignee(userId)
    .list();
```

#### 2.3.4 流程回退功能

```java
// ActivitiServiceImpl.java 实现了流程回退
// 1. 获取当前任务和前一个任务
// 2. 动态修改流程图节点指向
// 3. 完成当前任务，流程自动流向目标节点
taskService.complete(task.getId());
```

---

## 3. Part 2：外部系统对接深度解析

> **小白化理解**：
> - HIS系统 = 医院的"大管家系统"，管挂号、开药、收费
> - 医保核心 = "保险公司结算中心"，决定能不能报销、报多少
> - WebService = 两个公司之间的"标准化公文"，按固定格式交换信息

### 3.1 HIS医院信息系统对接

#### 3.1.1 对接方式

| 项目 | 说明 |
|------|------|
| **协议** | WebService (SOAP) |
| **接口服务** | `BaseCallService.callService()` |
| **配置文件** | `InterfaceGrantHandler.java` |

#### 3.1.2 核心对接代码

```java
// JcSendMessageUtil.java - 短信发送工具类
public boolean sendMessage(String mobile, String content, String taskVa) {
    Map<String, Object> json = new HashMap<>();
    json.put("mobile", mobile);
    json.put("content", content);
    json.put("taskVa", taskVa);
    
    // 调用webservice接口
    LinkRuturnEntity result = callService.callService(
        InterfacewsEnum.LTMS001.toString(), 
        param
    );
    return result.getSuccess();
}
```

#### 3.1.3 HIS主要功能

| 功能 | 说明 |
|------|------|
| 患者信息查询 | 获取患者基本信息、病历信息 |
| 处方获取 | 从HIS系统获取医生开具的处方 |
| 费用结算 | 获取诊疗费用明细 |
| 体检报告 | 获取患者体检结果 |

### 3.2 医保核心系统对接

#### 3.2.1 对接架构

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   慢特病系统      │────▶│   医保核心系统    │────▶│   医保局数据库    │
│                  │     │   (WebService)   │     │                  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
         │                        │                        │
         │  备案申请(5302)         │  备案确认              │
         │────────────────────────▶│                        │
         │  备案查询(5301)         │                        │
         │────────────────────────▶│                        │
         │  资质查询(1101)         │                        │
         │────────────────────────▶│                        │
```

#### 3.2.2 核心接口列表

| 接口代码 | 接口名称 | 用途 |
|----------|----------|------|
| `1101` | 医保资质查询 | 查询患者是否有医保资格 |
| `5301` | 备案查询 | 查询已备案的慢病信息 |
| `5302` | 备案申请 | 向医保系统提交慢病备案 |
| `CXCF` | 共享库接口 | 处方共享数据交换 |

#### 3.2.3 医保备案流程代码

```java
// MedicareResearchTask.java
// 1. 调用1101接口查询资质
Sx1101Vo sx1101Vo = new Sx1101Vo();
sx1101Vo.setMdtrt_cert_type("jmsfz");  // 居民身份证
sx1101Vo.setMdtrt_cert_no(idCard);
LinkRuturnEntity call1101 = sxMedicareService.call1101(sx1101Vo);

// 2. 调用5301接口查询备案
Sx5301Vo sx5301Vo = new Sx5301Vo();
sx5301Vo.setPsn_no(psn_no);  // 医保个人编号
LinkRuturnEntity call5301 = sxMedicareServiceImpl.call5301(sx5301Vo);

// 3. 处理备案结果
JSONObject data5301 = (JSONObject)call5301Result.getData();
List<Map> feedetail = data5301.getList("feedetail");
```

#### 3.2.4 医保接口入参示例

```java
// 1101资质查询入参
{
  "mdtrt_cert_type": "jmsfz",  // 就医凭证类型：居民身份证
  "mdtrt_cert_no": "61030219...",  // 身份证号
  "certno": "61030219...",        // 证件号码
  "flag": "BJ"                     // 地区标识
}

// 5301备案查询入参
{
  "psn_no": "P10001...",          // 医保个人编号
  "flag": "BJ"                     // 地区标识
}
```

### 3.3 短信平台对接

#### 3.3.1 对接配置

| 配置项 | 说明 |
|--------|------|
| **服务地址** | `10.57.128.98:9503` (内网) |
| **接口代码** | `LTMS001` |
| **发送时间限制** | 08:00 - 22:00 |

#### 3.3.2 短信发送代码

```java
// VipSendMessageService - 短信发送服务
public void saveSendMessage(String name, String mobile, String message, 
                            VipMessage vipMessage, String vipid) {
    // 1. 创建短信记录
    VipSendMessage sms = new VipSendMessage();
    sms.setMobile(mobile);
    sms.setMessage(message);
    sms.setSendflag("2");  // 待发送状态
    sms.setType("1");      // 普通短信
    vipSendMessageService.save(sms);
}

// 定时任务实际发送
// VipSendMessageTask.java
public void run() {
    if (!isSendTime()) return;  // 检查是否在允许发送时间
    
    List<VipSendMessage> list = vipSendMessageService.getVipSendMessageList(filter);
    for (VipSendMessage sms : list) {
        boolean success = sendVerificationCodeUtil.sendSMS(
            sms.getMobile(), 
            sms.getMessage(), 
            sms.getUnitid()
        );
        // 更新发送状态
        sms.setSendflag(success ? "2" : "3");  // 2=成功, 3=失败
    }
}
```

#### 3.3.3 短信模板示例

```text
【中国人民健康保险】尊敬的{姓名}（身份证号：{身份证号}），您好！
你申请的{城市}医保慢病治疗有效期即将结束，请于{日期}前通过微信小程序
"慢病保险服务平台"进行年审，确保正常享受待遇。
咨询电话：{电话号码}
```

### 3.4 微信小程序对接

#### 3.4.1 小程序配置

```java
// MbXcxValueUtil.java
@Value("${call.hosts.wxxcx.host:http://10.34.92.150:9502/sns/jscode2session}")
private String wxXcxHost;  // 微信登录验证地址

// FTP配置 (小程序图片存储)
@Value("${xcxftp.ip:10.252.68.155}")
@Value("${xcxftp.port:21}")
@Value("${xcxftp.username:****}")  // 已脱敏
@Value("${xcxftp.password:****}")  // 已脱敏
```

#### 3.4.2 小程序签名拦截

```java
// XcxInterceptorConfig.java
@Value("${xcxInterceptFlag:false}")
private boolean xcxInterceptFlag;

@Override
public boolean preHandle(HttpServletRequest request, ...) {
    if (!xcxInterceptFlag) return true;
    // 验证小程序签名
    String signature = request.getHeader("X-Signature");
    // ... 签名验证逻辑
}
```

#### 3.4.3 小程序FTP文件操作

```java
// FTPFileUtil_xcx.java - 小程序文件工具类
public InputStream downLoadto(String path, String fileName) {
    // 从小程序SFTP服务器下载文件
}

public String getBase64FromInputStream(InputStream is) {
    // 转换为Base64
}
```

---

## 4. Part 3：定时任务详解

> **小白化理解**：定时任务就像闹钟，每天固定时间自动执行某些操作。

### 4.1 定时任务清单 (共26个)

| 序号 | 任务类名 | 任务功能 | 触发规则 | 执行频率 |
|------|----------|----------|----------|----------|
| 1 | `AccountEnableTask` | 账号失效处理 | 每日凌晨 | 每日1次 |
| 2 | `Approval2EndYlTask` | 审批流自动结束 | 定时扫描 | 每日多次 |
| 3 | `BJAutoFilingTask` | 宝鸡自动备案 | 待遇到期前一个月 | 每日1次 |
| 4 | `BJDelFilingTask` | 宝鸡备案删除 | 备案到期后 | 每日1次 |
| 5 | `BJGXTTask` | 宝鸡共享库推送 | 定时扫描 | 每日多次 |
| 6 | `DrugSynchronizedTask` | 药品信息同步 | 定时扫描 | 每日多次 |
| 7 | `File2ImageTask` | 文件转图片 | 定时扫描 | - |
| 8 | `GhiInsureDetailInitTask` | 宝鸡慢病初始化 | 定时扫描 | 每日多次 |
| 9 | `IcdExpiresTask` | 病种过期处理 | 每日凌晨 | 每日1次 |
| 10 | `MBCSZNHTask` | 慢病智能初审 | 定时扫描 | 每日多次 |
| 11 | `MedicarePutOnRecordTask` | 医保备案 | 申报通过后 | 实时 |
| 12 | `MedicareResearchTask` | 医保资质查询 | 定时扫描 | 每日多次 |
| 13 | `ReviewWaringTask` | 复审预警 | 每日凌晨 | 每日1次 |
| 14 | `SlYearCheckTask` | 商洛年审 | 定时扫描 | 每日多次 |
| 15 | `SlYearPostponeTask` | 商洛年审延期 | 定时扫描 | 每日多次 |
| 16 | `SxMedicarePORResearchTask` | 陕西医保备案查询 | 定时扫描 | 每日多次 |
| 17 | `VipAccountMoneyResetTask` | 账户金额重置 | 每日凌晨 | 每日1次 |
| 18 | `VipMbAutoMaskTask` | 慢病自动掩码 | 定时扫描 | - |
| 19 | `VipMbReviewGetPhysicalTask` | 复审获取体检报告 | 定时扫描 | 每日多次 |
| 20 | `VipMbdeclareGetPhysicalTask` | 申报获取体检报告 | 定时扫描 | 每日多次 |
| 21 | `VipMbmzStatusTask` | 慢病状态更新 | 定时扫描 | 每日多次 |
| 22 | `VipMbmzUpdateTask` | 慢病信息更新 | 定时扫描 | 每日多次 |
| 23 | `VipSendMessageJCTask` | JC短信发送 | 每分钟检查 | 08:00-22:00 |
| 24 | `VipSendMessageTask` | 短信发送 | 每分钟检查 | 08:00-22:00 |
| 25 | `WqxOutInterfaceTask` | 文曲星接口推送 | 定时扫描 | 每日多次 |
| 26 | `xjsMRXOutInterfaceTask` | 新技术处接口 | 智能审核调用 | 实时 |

### 4.2 重点任务详解

#### 4.2.1 商洛年审定时任务 (SlYearCheckTask)

**功能**：处理商洛地区慢病患者的年度审核

**核心逻辑**：
```
1. 修改数据状态为资质生效
2. 重置待遇享受开始和结束时间
3. 发送年审预警短信
4. 超出待遇享受期的置成资质失效
```

**触发条件**：
- 居民：每年12月1日发送预警，1月1日自动通过
- 职工：待遇到期当月发送预警，到期后30天内未年审则失效

**短信模板**：
```text
【中国人民健康保险】尊敬的{姓名}（身份证号：{身份证}），您好！
你申请的商洛市医保慢病治疗有效期即将结束，请于{日期}日前通过微信小程序
"慢病保险服务平台"进行年审。咨询电话：0914-2030198
```

#### 4.2.2 宝鸡慢病初始化任务 (GhiInsureDetailInitTask)

**功能**：处理宝鸡地区慢病新用户的绑卡和产品绑定

**处理阶段**：
```
阶段1: 绑卡处理 (status=0, flowstatus=2)
  ├── 七种病 (icdtype=QZB)
  ├── 两病 (icdtype=LB)
  └── 十种病 (icdtype=SZB)

阶段2: 绑定产品 (status=1, flowstatus=3)
  └── 调用 ghiInsureDetailInitService.bindingProduct()
```

#### 4.2.3 医保备案任务 (MedicareResearchTask)

**功能**：从医保系统同步患者备案信息

**接口调用链**：
```
1. call1101() - 查询医保资质
   └── 输入: 身份证号
   └── 输出: 医保个人编号(psn_no)

2. call5301() - 查询备案信息
   └── 输入: psn_no
   └── 输出: 备案病种列表
       ├── 糖尿病 (M03900)
       ├── 高血压 (M01600)
       └── ...
```

#### 4.2.4 智能初审任务 (MBCSZNHTask)

**功能**：利用AI技术自动初审申报资料

**处理流程**：
```
1. 图片质检 (IQI)
   └── 调用 xjsIQI() 接口
   └── 检测: 清晰度、倾斜度

2. 医疗影像分类 (MIC)
   └── 调用 xjsMIC() 接口
   └── 分类: 病案首页、处方、检验报告等

3. 身份证OCR (IDCard)
   └── 调用 xjsIDCard() 接口
   └── 提取: 姓名、身份证号、地址

4. 印章识别 (Seal)
   └── 调用 xjsSeal() 接口
   └── 检测: 医院印章、骑缝章

5. 病案首页信息抽取 (MIE)
   └── 调用 xjsMIE() 接口
   └── 提取: 诊断、住院日期、诊疗信息
```

#### 4.2.5 短信发送任务 (VipSendMessageTask / VipSendMessageJCTask)

**功能**：批量发送短信通知

**发送时间控制**：
```java
private boolean isSendTime() {
    String sendstartTime = "08:00:00";
    String sendEndTime = "22:00:00";
    // 只在 08:00 - 22:00 之间发送
}
```

**发送流程**：
```
1. 查询待发送短信 (sendflag=2, type=1)
2. 循环调用发送接口
3. 间隔300ms避免频率限制
4. 更新发送状态 (成功=2, 失败=3)
```

#### 4.2.6 账号失效处理任务 (AccountEnableTask)

**功能**：定期清理长期未登录的账号

**处理逻辑**：
```java
public void updateEnable() {
    // 1. 查询慢病会员中到期的账号
    List<PrivilegeUserInfo> vipList = privilegeUserInfoService.getEndLoginAccount();
    for (PrivilegeUserInfo vip : vipList) {
        vip.setEnable(0);  // 设置为失效
        // 记录操作日志
    }
    
    // 2. 查询机构用户中到期的账号
    List<UpOrgUser> userList = upOrgUserDao.getEndLoginAccount();
    for (UpOrgUser user : userList) {
        user.setUserAccountLocked("T");  // 锁定账号
    }
}
```

### 4.3 定时任务配置说明

#### 4.3.1 Spring @Scheduled 注解

```java
// 注: 代码中部分任务注解被注释，实际由XXL-JOB调度平台触发

// 每分钟执行
@Scheduled(cron = "0 0/1 * * * ?")

// 每10分钟执行
@Scheduled(cron = "0 0/10 * * * ?")

// 每小时执行
@Scheduled(cron = "0 0 0/9999 * * ?")
```

#### 4.3.2 任务执行模式

```
┌─────────────────────────────────────────────────────────────┐
│                    XXL-JOB 调度平台                          │
├─────────────────────────────────────────────────────────────┤
│  定时触发                                                      │
│      │                                                        │
│      ▼                                                        │
│  ┌─────────────┐    分布式锁    ┌─────────────┐             │
│  │   Server 1   │◀─────────────▶│   Server 2   │             │
│  └──────┬──────┘               └──────┬──────┘             │
│         │                              │                     │
│         ▼                              ▼                     │
│  ┌─────────────────────────────────────────────┐            │
│  │           定时任务执行节点                     │            │
│  └─────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. 业务术语对照表

### 5.1 慢病业务术语

| 术语 | 全称 | 解释 |
|------|------|------|
| 慢特病 | 门诊慢性特殊疾病 | 需要长期门诊治疗的疾病，如糖尿病、高血压 |
| 备案 | 慢病备案 | 向医保系统登记慢病资格的过程 |
| 复审 | 复审 | 慢病资格到期前的再次审核 |
| 年审 | 年度审核 | 每年一次的资格审核 |
| 体检 | 体检 | 部分慢病需要体检报告作为申报材料 |

### 5.2 流程状态术语

| 术语 | 解释 |
|------|------|
| `reviewStatus` | 复审状态：2=接受, 3=拒绝, 4=失效, -1=无效 |
| `physicalStatus` | 体检状态：1=完成, 2=未到, 3=放弃 |
| `flowStatus` | 流程状态：2=已绑卡, 3=已绑定产品 |
| `status` | 处理状态：0=未处理, 1=已处理 |

### 5.3 地区代码

| 地区 | 代码 | 说明 |
|------|------|------|
| 宝鸡 | BJ | 陕西省宝鸡市 |
| 商洛 | SL | 陕西省商洛市 |
| 延安 | YA | 陕西省延安市 |
| 咸阳 | XY | 陕西省咸阳市 |
| 榆林 | YL | 陕西省榆林市 |

### 5.4 接口代码

| 代码 | 名称 | 系统 |
|------|------|------|
| LTMS001 | 短信发送接口 | 短信平台 |
| 1101 | 医保资质查询 | 医保核心 |
| 5301 | 备案查询 | 医保核心 |
| 5302 | 备案申请 | 医保核心 |
| CXCF | 处方共享接口 | 医保共享库 |
| IQI | 图片质检接口 | 新技术处AI |
| MIC | 医疗影像分类 | 新技术处AI |
| MIE | 病案首页抽取 | 新技术处AI |

---

## 附录

### A. 文件路径速查

| 文件 | 路径 |
|------|------|
| BPMN文件 | `picchealth-server/src/main/resources/processes/*.bpmn` |
| Activiti服务 | `picchealth-server/src/main/java/com/picchealth/module/mb/service/impl/ActivitiServiceImpl.java` |
| 定时任务 | `picchealth-server/src/main/java/com/picchealth/module/scheduling/*.java` |
| 短信工具 | `picchealth-server/src/main/java/com/picchealth/utils/JcSendMessageUtil.java` |
| 医保服务 | `picchealth-server/src/main/java/com/picchealth/module/mb/service/impl/SxMedicareServiceImpl.java` |

### B. 敏感信息脱敏说明

| 信息类型 | 脱敏方式 |
|----------|----------|
| 身份证号 | 显示前3后4位，如 `610***19****221` |
| 手机号 | 显示前3后4位，如 `138****1234` |
| 银行卡号 | 显示前4后4位，如 `6228****1234` |
| 密码 | 使用 `****` 替代 |
| FTP密码 | 使用 `****` 替代 |

---

*文档结束*
