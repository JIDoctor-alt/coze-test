# PICC门诊慢特病业务管理系统 - 申报全流程深度解析

> 📅 文档版本：V1.0  
> 🎯 适用对象：零基础开发人员、需求分析师、技术小白  
> 🔧 技术栈：Spring Boot + MyBatis + Activiti6 + GaussDB + Redis

---

## 一、业务背景（小白必读）

### 1.1 什么是门诊慢特病？

**通俗比喻**：想象你有一种慢性病（比如高血压、糖尿病），需要长期吃药和治疗。这种病就叫"慢特病"（门诊慢性特殊疾病的简称）。

**医保政策**：国家为了减轻这类患者的负担，规定可以申请"慢特病待遇"——简单说就是以后买药可以报销一大部分钱！

### 1.2 这个系统解决什么问题？

```
患者痛点                    系统解决
   │                          │
   ▼                          ▼
"我要怎么申请？"         ──→  线上/线下提交申报材料
"要准备什么材料？"       ──→  材料清单+上传功能  
"审批要多久？"           ──→  流程透明、实时查询
"批下来了怎么用？"       ──→  慢特病卡+买药报销
```

### 1.3 参与角色有哪些？

| 角色 | 通俗解释 | 类比 |
|------|----------|------|
| 🧑‍💼 患者 | 申请慢特病待遇的人 | 顾客 |
| 👨‍⚕️ 初审工作人员 | 窗口人员，接收材料并初审核 | 银行柜员 |
| 🩺 体检中心 | 部分病种需要体检证明 | 体检机构 |
| 👨‍⚕️ 专家医生 | 专家评审，判断是否达标 | 评审委员会 |
| 💳 发卡人员 | 制卡、发卡、激活卡片 | 营业厅工作人员 |
| 🔧 运维人员 | 系统维护、问题处理 | IT支持 |

---

## 二、流程总览（全景图）

### 2.1 完整生命周期流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        🏥 慢特病申报全流程（像个流水线！）                    │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ┌─────────────────┐
                                    │  📋 开始申报     │
                                    │  (患者端申请)    │
                                    └────────┬────────┘
                                             │
                                    ┌────────▼────────┐
                                    │  📥 材料提交     │
                                    │  (身份+病历+...) │
                                    └────────┬────────┘
                                             │
                        ┌────────────────────┼────────────────────┐
                        │                    │                    │
               ┌────────▼────────┐   ┌────────▼────────┐   ┌────────▼────────┐
               │  📱 线上申报    │   │  🏢 线下窗口申报  │   │  📁 数据导入    │
               │  (小程序/H5)   │   │  (服务窗口)       │   │  (批量处理)     │
               └────────┬────────┘   └────────┬────────┘   └────────┬────────┘
                        │                    │                    │
                        └────────────────────┼────────────────────┘
                                             │
                                    ┌────────▼────────┐
                              ╔═════╡  🔍 初审环节    ╞═════╗
                              ║     └────────┬────────┘     ║
                              ║              │              ║
                    ┌─────────▼─────────┐    │    ┌─────────▼─────────┐
                    │   ✅ 初审通过     │    │    │   ❌ 初审驳回      │
                    │   (进入下一环节)  │    │    │   (流程结束/申诉)  │
                    └─────────┬─────────┘    │    └───────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  🤔 需要体检吗？  │
                    └─────────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
     ┌────────▼────────┐ ┌────▼────┐ ┌────────▼────────┐
     │  🏥 需要体检     │ │ ✅ 不需要 │ │  ❌ 放弃体检     │
     │  (进入体检流程)  │ │ (跳过)   │ │  (流程结束)     │
     └────────┬────────┘ └───┬────┘ └───────────────────┘
              │              │
     ┌────────▼────────┐     │
     │  📋 体检完成    │     │
     │  (等待结果)    │     │
     └────────┬────────┘     │
              │              │
     ┌────────▼────────┐     │
     │  ⚠️ 未到/未通过  │     │
     │  (可重试≤3次)   │     │
     └────────┬────────┘     │
              │              │
              └──────┬───────┘
                     │
            ┌────────▼────────┐
      ╔═════╡  👨‍⚕️ 专家审核    ╞═════╗
      ║     └────────┬────────┘     ║
      ║              │              ║
┌─────▼─────┐ ┌──────▼──────┐ ┌────▼────┐
│ ✅ 通过   │ │ ❌ 驳回      │ │ 📝 补充  │
│ (进入发卡) │ │ (流程结束)   │ │ (退回)   │
└─────┬─────┘ └─────────────┘ └─────────┘
      │
     ┌▼─────────────────────────────────────────┐
     │         💳 发卡环节                        │
     │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
     │  │ 新发卡    │  │ 无变化    │  │ 信息变更  │ │
     │  │ (新制卡)  │  │ (沿用旧卡) │  │ (更新信息) │ │
     │  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
     └───────┼─────────────┼─────────────┼───────┘
             │             │             │
    ┌────────▼────────┐    │    ┌────────▼────────┐
    │  📮 待邮寄/自取  │    │    │  ✅ 继续使用旧卡  │
    └────────┬────────┘    │    └─────────────────┘
             │             │
    ┌────────▼────────┐    │
    │  🔓 卡激活       │    │
    │  (患者自助激活)  │    │
    └────────┬────────┘    │
             │             │
    ┌────────▼────────┐    │
    │  🎉 待遇享受     │────┘
    │  (买药可报销)    │
    └─────────────────┘
```

### 2.2 流程中的状态流转（状态机）

**核心状态枚举** `ApplyStatusEnum`：

| 状态值 | 枚举名 | 通俗解释 | 状态图位置 |
|--------|--------|----------|------------|
| 0 | PASSING | ⏳ 审核中 | 🔴 黄灯-等待处理 |
| 1 | PASSFIRST | ✅ 初审通过 | 🟢 绿灯-第一关过 |
| 2 | NOPASSFIRST | ❌ 初审驳回 | 🔴 红灯-结束 |
| 3 | PASS | ✅ 审核通过(专家) | 🟢 绿灯-第二关过 |
| 4 | NOPASS | ❌ 审核驳回(专家) | 🔴 红灯-结束 |
| 5 | SOMEPASS | ⚠️ 部分通过 | 🟡 黄灯-部分成功 |
| 6 | PASSSECOND | ✅ 复审通过 | 🟢 绿灯-复审过 |
| 7 | NOPASSSECOND | ❌ 复审驳回 | 🔴 红灯-结束 |
| 8 | BCZL | 📝 补充资料 | 🟡 黄灯-需补材料 |
| 9 | WX | ❌ 无效/作废 | 🔴 红灯-结束 |
| 10 | Second | 🔄 二次审核 | 🟡 黄灯-再审一次 |
| 99 | NOSUBMIT | 📋 待提交 | ⚪ 灰灯-未开始 |

---

## 三、核心API入口解析

### 3.1 申报入口 - MbDeclareApi

**文件位置**：`picchealth-server/src/main/java/com/picchealth/module/mb/api/MbDeclareApi.java`

**一句话解释**：这是患者或窗口工作人员提交申报材料的入口，就像医院的挂号窗口。

```java
@RestController
@RequestMapping(value = "/MbDeclare")
public class MbDeclareApi {
    @Resource
    private VipMbdeclareInfoService vipMbdeclareInfoService;
    
    // 线下申报
    @RequestMapping(method = {RequestMethod.POST}, value = "/declare")
    public ApiResponse declare(@RequestBody JSONObject jsonObject) {
        // 把患者填的信息和上传的材料打包，交给Service处理
        DeclareVo declareVo = jsonObject.toBean(DeclareVo.class);
        return vipMbdeclareInfoService.declare(declareVo);
    }
    
    // 批量上传图片
    @RequestMapping(method = {RequestMethod.POST}, value = "/imageFiles")
    public ApiResponse imageFiles(@RequestBody JSONObject jsonObject) {
        // 处理患者上传的证件照片、病历照片等
        return vipMbdeclareInfoService.picture(vipMbFileVos);
    }
}
```

**小白理解**：
```
用户操作: 打开申报页面 → 填写信息 → 上传材料 → 点击提交
系统后台: Api接收 → Vo转换 → Service处理 → 存入数据库 → 返回结果
```

---

### 3.2 初审入口 - VipMbDeclareFirstTrialApi

**文件位置**：`picchealth-server/src/main/java/com/picchealth/module/mb/api/VipMbDeclareFirstTrialApi.java`

**一句话解释**：这是初审工作人员查看和审批申报材料的入口，像银行贷款的初审批。

```java
@RestController
@RequestMapping(value = "/MbDeclareFirstTrial")
public class VipMbDeclareFirstTrialApi {
    
    // 查询待初审列表（像银行柜员看排队名单）
    @RequestMapping(method = {RequestMethod.POST}, value = "/queryMbDeclareListInFirstTrail")
    public ApiResponse<ResultPage<VipMbdeclareInfoDto>> queryMbDeclareListInFirstTrail(...) {
        return ApiResponse.ok(vipMbdeclareInfoService.selectPage(vo));
    }
    
    // 初审审批通过
    @RequestMapping(method = {RequestMethod.POST}, value = "/updateMbDeclareFirstApprovalInfo")
    public ApiResponse updateMbDeclareFirstApprovalInfo(InsertVipMbdeclareInfoVo vo) {
        // 调用审批服务，设置审批类型为"0"（通过）
        vipMbdeclareApprovalService.updateInfo(vo, "0");
        return ApiResponse.ok("审批成功");
    }
    
    // 初审不予通过
    @RequestMapping(method = {RequestMethod.POST}, value = "/updateMbDeclareReviewApprovalInfo")
    public ApiResponse updateMbDeclareReviewApprovalInfo(InsertVipMbdeclareInfoVo vo) {
        // 调用审批服务，设置审批类型为"1"（驳回）
        vipMbdeclareApprovalService.updateInfo(vo, "1");
        return ApiResponse.ok("不予通过成功");
    }
}
```

**审批决策树**：

```
                    初审工作人员看到申报材料
                              │
                              ▼
                    ┌─────────────────┐
                    │  材料是否齐全？  │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
         ┌────▼────┐                    ┌───▼────┐
         │  YES    │                    │  NO    │
         └────┬────┘                    └───┬────┘
              │                             │
              ▼                             ▼
    ┌─────────────────┐           ┌─────────────────┐
    │ 病种是否需要体检？│           │  📝 补充资料      │
    └────────┬────────┘           │  (打回让患者补)  │
             │                    └─────────────────┘
      ┌──────┴──────┐
      │             │
 ┌────▼───┐    ┌────▼───┐
 │ 需要    │    │ 不需要  │
 └────┬───┘    └────┬───┘
      │             │
      ▼             ▼
┌──────────┐  ┌──────────┐
│ 安排体检  │  │ 专家审核  │
│ (下一环节)│  │ (下一环节)│
└──────────┘  └──────────┘
```

---

### 3.3 复审入口 - VipMbDeclareReviewApi & MbReviewApi

**文件位置**：
- `picchealth-server/src/main/java/com/picchealth/module/mb/api/VipMbDeclareReviewApi.java`
- `picchealth-server/src/main/java/com/picchealth/module/mb/api/MbReviewApi.java`

**一句话解释**：复审是对即将到期的慢特病资格进行重新验证，像驾照到期换证。

```java
// 复审结果提交
@RequestMapping(method = {RequestMethod.POST}, value = "/updateMbdeclareReviewApprovalInfo")
public ApiResponse updateMbdeclareReviewApprovalInfo(UpdateMbdeclareReviewApprovalInfoVo vo) {
    // 保存复审结果和专家意见
    ApiResponse result = vipMbdeclareApprovalService.updateMbdeclareReviewApprovalInfo(vo);
    return ApiResponse.ok();
}

// 复审查询
@RequestMapping(method = {RequestMethod.POST}, value = "/query")
public ApiResponse<ResultPage<MbReviewDto>> query(QureyMbReviewDto vo) {
    return ApiResponse.ok(vipReviewService.queryReview(vo));
}

// 接受复审
@RequestMapping(method = {RequestMethod.POST}, value = "/acceptReview")
public ApiResponse acceptReview(MbReviewDto mbReviewDto) {
    return vipReviewService.acceptReview(mbReviewDto);
}

// 拒绝复审
@RequestMapping(method = {RequestMethod.POST}, value = "/refuseReview")
public ApiResponse refuseReview(MbReviewDto mbReviewDto) {
    return vipReviewService.refuseReview(mbReviewDto);
}
```

---

### 3.4 发卡入口 - MbmzSendCardApi

**文件位置**：`picchealth-server/src/main/java/com/picchealth/module/mb/api/MbmzSendCardApi.java`

**一句话解释**：这是给通过审核的患者发慢特病卡的环节，像银行给用户制卡。

```java
@RestController
@RequestMapping(value = "/mbmzSendCard")
public class MbmzSendCardApi {
    @Resource
    private VipSendcardService vipSendcardService;
    
    // 查询待发卡列表
    @RequestMapping(method = {RequestMethod.POST}, value = "/queryForSendWork")
    public ApiResponse<ResultPage<VipSendcardResultDto>> queryForSendWork(...) {
        return ApiResponse.ok(vipSendcardService.queryForSendWork(queryForSendWorkVo));
    }
    
    // 确认发卡
    @RequestMapping(method = {RequestMethod.POST}, value = "/saveVipSendcardForSend")
    public ApiResponse saveVipSendcardForSend(SaveVipSendcardForSendVo vo) {
        return vipSendcardService.saveVipSendcardForSend(vo);
    }
}
```

---

## 四、核心Service逐行解析

### 4.1 VipMbdeclareInfoService - 申报信息服务

**文件位置**：`picchealth-server/src/main/java/com/picchealth/module/mb/service/impl/VipMbdeclareInfoServiceImpl.java`

#### 4.1.1 declare() - 线下申报方法

**一句话人话**：接收患者的申报材料，给材料拍照存档，然后找个"流水线"来推进审批流程。

```java
@Override
public ApiResponse declare(DeclareVo declareVo) {
    // 📸 比喻：医院接收患者的病历本，开始建档
    
    // 1️⃣ 第一步：医保资格校验 - 看看这个患者有没有参保
    // （就像银行先查你有没有账户）
    if (StringUtils.isNotBlank(declareVo.getIdCard())) {
        SxCheckVo sxCheckVo = new SxCheckVo();
        sxCheckVo.setIdCard(declareVo.getIdCard());
        // ... 调用医保系统校验
    }
    
    // 2️⃣ 第二步：判断是初审还是复审 - 老病人复查还是新病人首次申请
    if (isFirstApply) {
        // 首次申报 - 走初审流程
        // 状态设为"审核中"(PASSING=0)
        vipMbdeclareInfo.setApplystatus(ApplyStatusEnum.PASSING.getIntValue());
    } else {
        // 复审申报 - 直接复审流程
        // 状态设为"复审通过"(PASSSECOND=6)
        vipMbdeclareInfo.setApplystatus(ApplyStatusEnum.PASSSECOND.getIntValue());
    }
    
    // 3️⃣ 第三步：保存申报主表信息
    // （像把患者信息录入医院信息系统）
    String primaryKey = this.createPrimaryKey();  // 生成唯一ID
    vipMbdeclareInfo.setId(primaryKey);
    vipMbdeclareInfo.setDeclareno(UUID.randomUUID().toString()); // 申报编号
    vipMbdeclareInfoService.save(vipMbdeclareInfo);
    
    // 4️⃣ 第四步：保存上传的文件（证件照片、病历等）
    // （把患者的病历本拍照存档）
    for (VipMbFileVo mbFile : declareVo.getMbFiles()) {
        VipMbdeclareFile file = new VipMbdeclareFile();
        file.setId(mbFile.getFileContent());  // 文件ID
        file.setDeclareid(primaryKey);        // 关联申报ID
        vipMbdeclareFileService.save(file);
    }
    
    // 5️⃣ 第五步：启动工作流 - 把这个申报扔到流水线
    // （就像医院挂号后，病历本被传到相应科室）
    if (unitConfig.getWorkflowFlag() != null) {
        String processKey = unitConfig.getWorkflowFlag() + "mbsb";
        Map<String, Object> variables = new HashMap<>();
        variables.put("startType", StartTypeEnum.XXSB.getIntValue()); // 线下申报
        
        // 启动流程实例
        ProcessInstance instance = runtimeService.startProcessInstanceByKey(
            processKey,           // 流程定义Key（如"bjmbsb"）
            vipMbdeclareInfo.getId(),  // 业务键（申报ID）
            variables             // 流程变量
        );
        
        // 获取第一个任务并完成（自动流转到初审）
        Task task = taskService.createTaskQuery()
            .processInstanceId(instance.getId())
            .singleResult();
        taskService.complete(task.getId());
    }
    
    return ApiResponse.ok();  // 返回成功
}
```

**参数解析**：
| 参数 | 类型 | 含义 |
|------|------|------|
| declareVo | DeclareVo | 申报信息封装对象（患者信息+病种+材料） |
| 返回值 | ApiResponse | 操作结果（成功/失败/错误信息） |
| 调用方 | MbDeclareApi | 患者端或窗口工作人员调用 |

**小白易懵点**：
- ❓ `startType`是什么？→ 区分线上申报(1)、线下申报(2)、导入(3)
- ❓ `processKey`为什么加"mbsb"？→ 区分不同地区流程，如"bjmbsb"(宝鸡)
- ❓ 为什么要先完成第一个任务？→ 自动跳转到初审环节

---

#### 4.1.2 saveVipmbdeclareInfoBJ() - 宝鸡申报方法

**一句话人话**：给宝鸡地区量身定制的申报方法，多了一些"特殊照顾"。

```java
private void saveVipmbdeclareInfoBJ(DeclareVo declareVo, 
                                     VipMbdeclareInfo vipMbdeclareInfo, 
                                     DiseaseBjVo diseaseBjVo) {
    
    // 1️⃣ 基础信息保存（和其他地区一样）
    String primaryKey = this.createPrimaryKey();
    vipMbdeclareInfo.setId(primaryKey);
    vipMbdeclareInfo.setApplystatus(ApplyStatusEnum.PASSING.getIntValue()); // 审核中
    
    // 2️⃣ 特殊逻辑：根据疾病类型判断是否需要体检
    // 🩺 某些病种必须先体检才能进入专家审核
    if (needPhysical) {
        vipMbdeclareInfo.setPhysicalstatus(PhysicalStatusEnum.NEED.getIntValue());
    } else {
        vipMbdeclareInfo.setPhysicalstatus(PhysicalStatusEnum.NONEED.getIntValue());
    }
    
    // 3️⃣ 保存申报主表
    saveVipmbdeclareInfo(vipMbdeclareInfo);
    
    // 4️⃣ 创建备案记录 - 告诉医保系统"这个人要享受慢特病待遇"
    // （就像去社保局登记，社保局要给你建档）
    TMbPutOnRecDetl detl = createPutOnRecDetl(vipMbdeclareInfo, diseaseBjVo);
    detl.setOpspDiseCode(diseaseBjVo.getYbcode());  // 医保病种编码
    tMbPutOnRecDetlService.save(detl);
    
    // 5️⃣ 如果需要体检，安排体检
    if (needPhysical) {
        // 分配体检中心
        assignPhysicalCenter(vipMbdeclareInfo, diseaseBjVo);
    }
}
```

---

### 4.2 VipMbdeclareApprovalService - 审批服务

**文件位置**：`picchealth-server/src/main/java/com/picchealth/module/mb/service/impl/VipMbdeclareApprovalServiceImpl.java`

#### 4.2.1 updateInfo() - 初审审批方法

**一句话人话**：把初审结果（通过/驳回/补充材料）记录下来，然后通知流水线继续走。

```java
@Override
@Transactional(propagation = Propagation.REQUIRED)
public void updateInfo(InsertVipMbdeclareInfoVo insertVipMbdeclareInfoVo, String flag) {
    // 🔐 @Transactional：像银行转账，要么全成功要么全回滚
    
    String userId = UserUtils.getUser().getUserId();  // 获取当前登录用户
    
    // 1️⃣ 获取申报信息
    VipMbdeclareInfo vipMbdeclareInfo = vipMbdeclareInfoService.getVipMbdeclareInfoById(
        insertVipMbdeclareInfoVo.getId()
    );
    
    // 2️⃣ 创建审批记录
    VipMbdeclareApproval approval = new VipMbdeclareApproval();
    approval.setDeclareid(vipMbdeclareInfo.getId());
    approval.setApprovaltype(ApprovalTypeEnum.APPROVALTYPE_FIRST.getValue()); // 初审
    approval.setApprovaluserid(userId);  // 审批人
    approval.setFirstuseraccount(UserUtils.getUser().getUserAccount());
    approval.setFirstusername(UserUtils.getUser().getUserName());
    
    // 3️⃣ 根据审批结果决定状态
    if ("0".equals(flag)) {
        // ✅ 通过 - 设置为初审通过状态
        vipMbdeclareInfo.setApplystatus(ApplyStatusEnum.PASSFIRST.getIntValue()); // 1
        approval.setApprovalstatus(ApprovalStatusEnum.PASS.getIntValue()); // 0
        
        // 判断是否需要体检
        if (needPhysical) {
            vipMbdeclareInfo.setPhysicalstatus(PhysicalStatusEnum.NEED.getIntValue());
        } else {
            vipMbdeclareInfo.setPhysicalstatus(PhysicalStatusEnum.NONEED.getIntValue());
        }
    } else if ("1".equals(flag)) {
        // ❌ 驳回 - 流程结束
        vipMbdeclareInfo.setApplystatus(ApplyStatusEnum.NOPASSFIRST.getIntValue()); // 2
        approval.setApprovalstatus(ApprovalStatusEnum.NOPASS.getIntValue()); // 1
    }
    
    // 4️⃣ 保存审批意见
    if (StringUtils.isNotBlank(insertVipMbdeclareInfoVo.getApprovalOpinion())) {
        approval.setApprovalopinion(insertVipMbdeclareInfoVo.getApprovalOpinion());
    }
    
    // 5️⃣ 保存审批记录
    vipMbdeclareApprovalService.save(approval);
    
    // 6️⃣ 更新申报主表状态
    vipMbdeclareInfoService.save(vipMbdeclareInfo);
    
    // 7️⃣ 完成工作流任务 - 推动流程到下一环节
    Task task = taskService.createTaskQuery()
        .processInstanceBusinessKey(vipMbdeclareInfo.getId())
        .singleResult();
    
    if (task != null) {
        // 设置流程变量，控制流转方向
        Map<String, Object> variables = new HashMap<>();
        variables.put("firstApproveFlag", Integer.parseInt(flag));  // 审批结果
        variables.put("needPhysical", needPhysical ? 6 : 7);        // 是否需要体检
        
        // 完成任务，流程自动流向下一个节点
        taskService.complete(task.getId(), variables);
    }
}
```

**流程变量控制条件分支**：

| 变量名 | 值 | 含义 | 流转方向 |
|--------|-----|------|----------|
| firstApproveFlag | 0 | 初审通过 | →体检/专家审核 |
| firstApproveFlag | 1 | 初审驳回 | →流程结束 |
| firstApproveFlag | 2 | 资料不全 | →补充资料 |
| needPhysical | 6 | 需要体检 | →体检环节 |
| needPhysical | 7 | 不需要体检 | →专家审核 |

---

#### 4.2.2 reviewPass() - 专家审核通过方法

**一句话人话**：专家看完材料说"这个患者符合条件"，然后系统开始算他能享受多久的待遇。

```java
@Override
@Transactional
public ApiResponse reviewPass(VipMbdeclareInfoDto dto) {
    String declareId = dto.getId();
    
    // 1️⃣ 查询申报信息
    VipMbdeclareInfo vipMbdeclareInfo = vipMbdeclareInfoService.getVipMbdeclareInfoById(declareId);
    
    // 2️⃣ 判断是多病种还是单病种
    if (multipleDisease) {
        // 多病种：逐个审核，每个病种都要过一遍专家
        for (String icdCode : diseaseCodeList) {
            reviewSingleDisease(vipMbdeclareInfo, icdCode);
        }
    } else {
        // 单病种：直接审核
        reviewSingleDisease(vipMbdeclareInfo, vipMbdeclareInfo.getIcdcode());
    }
    
    // 3️⃣ 计算待遇享受时间
    // 📅 规则：审核通过后次月1日生效，截止日期根据病种复审年限计算
    LocalDateTime startDateTime = getStartDateTime(icdCode);  // 生效时间
    LocalDateTime endDateTime = getEndDateTime(icdCode);     // 失效时间
    
    // 4️⃣ 创建备案记录（告诉医保系统这个人可以享受待遇了）
    TMbPutOnRecDetl detl = new TMbPutOnRecDetl();
    detl.setDeclareid(declareId);
    detl.setBegndate(Date.from(startDateTime.atZone(ZoneId.systemDefault()).toInstant()));
    detl.setEnddate(Date.from(endDateTime.atZone(ZoneId.systemDefault()).toInstant()));
    detl.setTrtDclaPutOnRecStas(FilingStatusEnum.YES.getValue()); // 已备案
    detl.setOpspDiseCode(ybCode);  // 医保病种编码
    tMbPutOnRecDetlService.save(detl);
    
    // 5️⃣ 发送短信通知患者
    vipSendMessageService.sendNoticeMessage(vipMbdeclareInfo, "审核通过");
    
    return ApiResponse.ok();
}
```

**待遇享受期计算规则**：

```
特殊病种（恶性肿瘤、器官移植、血透）：
  审核通过当日立即生效

普通病种：
  审核通过次月1日生效
  截止日期 = 生效年份 + 复审年限 - 1年 的12月31日

例如：2024年6月审核通过，2年复审年限
  生效：2024-07-01
  截止：2025-12-31（第一年）+ 2026-12-31（第二年）
```

---

### 4.3 VipSendcardService - 发卡服务

**文件位置**：`picchealth-server/src/main/java/com/picchealth/module/mb/service/impl/VipSendcardServiceImpl.java`

#### 4.3.1 saveVipSendcardForSend() - 确认发卡方法

**一句话人话**：把慢特病卡绑定给患者，就像银行给客户激活银行卡。

```java
@Override
@Transactional(rollbackForClassName={"Exception"})
public ApiResponse saveVipSendcardForSend(SaveVipSendcardForSendVo vo) {
    VipSendcard vipSendcard = vo.getVipSendcard();
    String cardNo = vipSendcard.getCardno();  // 卡号
    
    // 1️⃣ 校验卡号是否存在
    // （刷身份证查账户）
    VipCard cardParam = new VipCard();
    cardParam.setCardno(cardNo);
    cardParam.setType(VipCardTypeEnum.PHYSICAL.getValue());  // 实体卡
    cardParam.setDr(DrEnum.VALID.getValue());
    List<VipCard> lstVipCard = vipCardService.selectAll(cardParam);
    
    if (lstVipCard.isEmpty()) {
        throw new CustomException("该卡号在系统不存在!");
    }
    
    VipCard cardNoOne = lstVipCard.get(0);
    
    // 2️⃣ 校验卡是否被使用
    // （银行卡不能重复激活）
    if (cardNoOne.getStatus() != 1) {  // 1=未使用
        throw new CustomException("该卡号已经被使用!");
    }
    
    // 3️⃣ 更新卡状态为"已使用"
    cardNoOne.setStatus(VipCardStatusEnum.USED.getValue());  // 已用
    cardNoOne.setAccountid(vipSendcard.getAccountid());     // 绑定账户
    vipCardService.save(cardNoOne);
    
    // 4️⃣ 更新发卡记录
    vipSendcard.setCardno(cardNo);
    vipSendcard.setSendflag(VipSendCardStatusEnum.NOSEND.getValue()); // 待邮寄
    vipSendcard.setSendcardtime(new Date());  // 发卡时间
    this.save(vipSendcard);
    
    // 5️⃣ 更新账户信息
    VipAccount vipAccount = vipAccountService.getVipAccountById(vipSendcard.getAccountid());
    if (vipAccount.getStatus() == 1) {  // 新建状态
        vipAccount.setStatus(AccountStatusEnum.NOT_ACTIVE.getValue()); // 待激活
    }
    vipAccount.setChangecardno(cardNo);  // 更新卡号
    vipAccountService.save(vipAccount);
    
    // 6️⃣ 发送短信通知
    vipSendMessageService.saveVipSendMessage(vipSendcard, MessageTypeEnum.A02.getValue());
    
    return ApiResponse.ok();
}
```

**发卡状态机**：

```
卡状态(VipCardStatusEnum):
  1 = 新建/未使用    → 发卡后变成"已使用"
  2 = 待激活         → 激活后变成"激活"
  3 = 激活           → 可正常使用
  4 = 冻结           → 冻结后无法使用

发卡标识(VipSendCardStatusEnum):
  0 = 待发卡
  1 = 已发卡
  2 = 待邮寄
  3 = 已邮寄
```

---

### 4.4 ActivitiService - 工作流服务

**文件位置**：`picchealth-server/src/main/java/com/picchealth/module/mb/service/impl/ActivitiServiceImpl.java`

#### 4.4.1 getHistories() - 获取审批历史

**一句话人话**：查看一个申报单在整个流水线上的"旅行记录"。

```java
@Override
public List<HistoryTaskVo> getHistories(GetHistoriesVo getHistoriesVo) {
    String businessKey = getHistoriesVo.getBusinessKey();  // 申报ID
    
    // 1️⃣ 查询历史任务（像查快递物流）
    List<HistoricTaskInstance> list = historyService
        .createHistoricTaskInstanceQuery()
        .processInstanceBusinessKey(businessKey)
        .list();
    
    List<HistoryTaskVo> historyTasks = new ArrayList<>();
    
    // 2️⃣ 转换为前端需要的格式
    for (HistoricTaskInstance task : list) {
        HistoryTaskVo vo = new HistoryTaskVo();
        vo.setId(task.getId());
        vo.setTaskDefinitionKey(task.getTaskDefinitionKey());
        vo.setName(TaskEnum.forValue(task.getTaskDefinitionKey()).getName()); // 环节名称
        vo.setStartTime(task.getStartTime());    // 开始时间
        vo.setEndTime(task.getEndTime());        // 结束时间
        vo.setDurationInMillis(task.getDurationInMillis()); // 处理时长
        
        // 3️⃣ 获取处理人信息
        if (StringUtils.isNotEmpty(task.getAssignee())) {
            UpOrgUser user = upOrgUserDao.selectByPrimaryKey(task.getAssignee());
            vo.setAssigneeName(user.getUserFullname());
        }
        
        historyTasks.add(vo);
    }
    
    return historyTasks;
}
```

**返回的审批历史示例**：

```json
[
  {
    "taskDefinitionKey": "W2001",
    "name": "初审管理",
    "startTime": "2024-01-15 09:00:00",
    "endTime": "2024-01-15 10:30:00",
    "assigneeName": "张三",
    "durationInMillis": 5400000
  },
  {
    "taskDefinitionKey": "W3001",
    "name": "慢病体检",
    "startTime": "2024-01-15 14:00:00",
    "endTime": "2024-01-17 16:00:00",
    "assigneeName": "第一体检中心",
    "durationInMillis": 180000000
  },
  {
    "taskDefinitionKey": "W4001",
    "name": "专家审核",
    "startTime": "2024-01-18 09:00:00",
    "endTime": "2024-01-18 11:00:00",
    "assigneeName": "李四(专家)",
    "durationInMillis": 7200000
  }
]
```

---

## 五、Activiti工作流与业务代码配合方式

### 5.1 工作流文件结构（宝鸡慢病申报流程）

**文件位置**：`picchealth-server/src/main/resources/processes/bjmbsb.bpmn`

```
宝鸡慢病申报流程 (bjmbsb.bpmn)
│
├── 开始事件 (startevent1)
│   │
│   ▼
├── 排他网关 (exclusivegateway1) ←─┐
│   │ 判断申报类型                │
│   ├── startType=1 → 线上申报(W1001)
│   ├── startType=2 → 线下申报(W1002)
│   ├── startType=3 → 线下导入(W6001)
│   └── startType=4 → 信息修改(W6005)
│   │
│   ▼
├── 初审管理 (W2001) ←─ userTask（需要人工处理）
│   │
│   ▼
├── 排他网关 (exclusivegateway2)
│   │ 判断初审结果
│   ├── firstApproveFlag=1 → 初审驳回(end)
│   ├── firstApproveFlag=2 → 补充资料(W1003) → 返回初审
│   └── firstApproveFlag=0 → 初审通过
│   │
│   ▼
├── 排他网关 (exclusivegateway10)
│   │ 判断是否需要体检
│   ├── needPhysical=6 → 慢病体检(W3001)
│   └── needPhysical=7 → 专家审核(W4001)
│   │
│   ▼
├── 慢病体检 (W3001) ←─ userTask
│   │
│   ▼
├── 排他网关 (exclusivegateway3)
│   │ 判断体检状态
│   ├── physicalStatus=1 → 体检完成 → 专家审核
│   ├── physicalStatus=2 → 未到 → 重新体检
│   └── physicalStatus=3 → 放弃体检(end)
│   │
│   ▼
├── 专家审核 (W4001) ←─ userTask
│   │
│   ▼
├── 排他网关 (exclusivegateway4)
│   │ 判断审核结果
│   ├── secondApproveFlag=0 → 审核通过 → 发卡环节
│   ├── secondApproveFlag=1 → 审核驳回(end)
│   └── secondApproveFlag=2 → 补充资料(W1004) → 返回专家审核
│   │
│   ▼
├── 发卡确认 (W6002) ←─ userTask
│   │
│   ▼
├── 慢病发卡 (W6003) ←─ userTask
│   │
│   ▼
├── 慢病卡激活 (W6004) ←─ userTask
│   │
│   ▼
└── 结束事件 (endevent)
```

### 5.2 工作流与业务的配合机制

```
┌─────────────────────────────────────────────────────────────────┐
│                      业务系统（Java代码）                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Controller    │  │ Service      │  │ DAO          │         │
│  │ (接收请求)    │  │ (业务逻辑)   │  │ (数据库)      │         │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘         │
│         │                 │                                    │
│         │  1.启动流程     │                                    │
│  ───────┼────────────────┼────────────────────────────────>    │
│         │  runtimeService.startProcessInstanceByKey()         │
│         │                                                     │
│         │  2.完成任务     │                                    │
│  ───────┼────────────────┼────────────────────────────────>    │
│         │  taskService.complete(taskId, variables)            │
│         │                                                     │
│         │  3.查询任务     │                                    │
│  ───────┼────────────────┼────────────────────────────────>    │
│         │  taskService.createTaskQuery()                      │
└─────────┼────────────────┼───────────────────────────────────────┘
          │                 │
          │                 ▼
┌─────────┼───────────────────────────────────────────────────────┐
│         │            Activiti工作流引擎                          │
│         │  ┌─────────────────────────────────────────────┐       │
│         │  │            流程定义 (BPMN)                   │       │
│         │  │  ┌───┐  ┌───┐  ┌───┐  ┌───┐  ┌───┐       │       │
│         │  │  │ A │─▶│ B │─▶│ C │─▶│ D │─▶│ E │       │       │
│         │  │  └───┘  └───┘  └───┘  └───┘  └───┘       │       │
│         │  └─────────────────────────────────────────────┘       │
│         │                                                      │
│         │  ┌─────────────────────────────────────────────┐       │
│         │  │            任务表 (ACT_RU_TASK)              │       │
│         │  │  taskId | key | assignee | businessKey      │       │
│         │  │  1001   | W2001 | user1  | MB202401001     │       │
│         │  └─────────────────────────────────────────────┘       │
│         │                                                      │
│         │  ┌─────────────────────────────────────────────┐       │
│         │  │            变量表 (ACT_RU_VARIABLE)          │       │
│         │  │  name             | value                    │       │
│         │  │  firstApproveFlag | 0                        │       │
│         │  │  needPhysical     | 6                        │       │
│         │  └─────────────────────────────────────────────┘       │
└─────────┼────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      数据库（GaussDB/MySQL）                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 申报主表      │  │ 审批记录表    │  │ 备案记录表    │          │
│  │ vip_mbdeclare │  │ vip_mb_approval│ │ t_mb_put_on_rec│         │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 代码中的工作流操作

```java
// 1️⃣ 启动工作流（在申报时调用）
ProcessInstance instance = runtimeService.startProcessInstanceByKey(
    "bjmbsb",                    // 流程定义Key
    vipMbdeclareInfo.getId(),   // 业务键（申报ID）
    variables                    // 初始变量
);

// 2️⃣ 完成任务，推动流程（在审批时调用）
Task task = taskService.createTaskQuery()
    .processInstanceBusinessKey(declareId)  // 通过申报ID查任务
    .singleResult();

Map<String, Object> variables = new HashMap<>();
variables.put("firstApproveFlag", 0);   // 通过
variables.put("needPhysical", 7);       // 不需要体检
taskService.complete(task.getId(), variables);  // 完成任务

// 3️⃣ 查询当前环节
Task currentTask = taskService.createTaskQuery()
    .processInstanceBusinessKey(declareId)
    .singleResult();
String currentStep = currentTask.getTaskDefinitionKey(); // 如 "W4001"

// 4️⃣ 获取流程历史
List<HistoricTaskInstance> history = historyService
    .createHistoricTaskInstanceQuery()
    .processInstanceBusinessKey(declareId)
    .list();
```

---

## 六、数据库表关系

### 6.1 核心表结构

```sql
-- 申报主表：存申报的基本信息
CREATE TABLE vip_mbdeclare_info (
    id VARCHAR(32) PRIMARY KEY,        -- 主键
    name VARCHAR(50),                   -- 姓名
    idcard VARCHAR(18),                 -- 身份证号
    mobile VARCHAR(20),                  -- 手机号
    icdtype VARCHAR(10),                -- 疾病类型
    icdname VARCHAR(100),               -- 疾病名称
    icdcode VARCHAR(50),                -- 疾病编码
    unitcode VARCHAR(50),               -- 医保区划编码
    applystatus INT,                    -- 申报状态
    physicalstatus INT,                 -- 体检状态
    sendcardflag INT,                   -- 发卡标识
    declarationtype INT,                -- 申报类型(1线上2线下)
    declareno VARCHAR(50),              -- 申报编号
    firstuserid VARCHAR(32),            -- 初审人ID
    seconduserid VARCHAR(32),           -- 复审人ID
    creator VARCHAR(32),                  -- 创建人
    createtime DATETIME,                -- 创建时间
    modifier VARCHAR(32),               -- 修改人
    modifytime DATETIME,                -- 修改时间
    dr INT DEFAULT 0                    -- 删除标志
);

-- 审批记录表：存每次审批的信息
CREATE TABLE vip_mbdeclare_approval (
    id VARCHAR(32) PRIMARY KEY,
    declareid VARCHAR(32),              -- 关联申报ID
    approvaltype VARCHAR(10),            -- 审批类型(1初审2专家3复审)
    approvalstatus INT,                  -- 审批状态(0通过1驳回)
    approvaluserid VARCHAR(32),          -- 审批人ID
    approvalusername VARCHAR(50),        -- 审批人姓名
    approvalopinion VARCHAR(500),        -- 审批意见
    approvaltime DATETIME,              -- 审批时间
    createtime DATETIME
);

-- 备案记录表：存医保局备案信息
CREATE TABLE t_mb_put_on_rec_detl (
    id VARCHAR(32) PRIMARY KEY,
    declareid VARCHAR(32),              -- 关联申报ID
    idcard VARCHAR(18),                 -- 身份证号
    opsp_dise_code VARCHAR(50),         -- 医保病种编码
    insutype VARCHAR(10),               -- 险种类型
    hosp_ide_date DATE,                -- 医院诊断日期
    begndate DATE,                     -- 待遇开始日期
    enddate DATE,                      -- 待遇结束日期
    trt_dcla_put_on_rec_stas VARCHAR(10), -- 备案状态
    createtime DATETIME
);

-- 发卡记录表：存发卡信息
CREATE TABLE vip_sendcard (
    id VARCHAR(32) PRIMARY KEY,
    accountid VARCHAR(32),              -- 账户ID
    vipid VARCHAR(32),                  -- 会员ID
    cardno VARCHAR(30),                 -- 卡号
    sendflag INT,                       -- 发卡标识
    sendcardtime DATETIME,             -- 发卡时间
    modifier VARCHAR(32),
    modifytime DATETIME
);
```

### 6.2 表关系图

```
┌─────────────────┐         ┌─────────────────┐
│ vip_mbdeclare   │         │ vip_mbdeclare   │
│     _info       │◄────────│   _approval     │
│   (申报主表)     │ 1:N    │   (审批记录)     │
└────────┬────────┘         └─────────────────┘
         │ 1:1
         ▼
┌─────────────────┐         ┌─────────────────┐
│ t_mb_put_on_rec │         │ vip_mbdeclare   │
│     _detl       │         │   _file         │
│   (备案记录)     │         │   (申报材料)     │
└────────┬────────┘         └─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐         ┌─────────────────┐
│  vip_account    │◄────────│ vip_sendcard    │
│   (账户表)       │ 1:1    │   (发卡记录)     │
└────────┬────────┘         └─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│  vip_card       │
│   (卡表)         │
└─────────────────┘
```

---

## 七、易踩坑点汇总

### 7.1 申报环节

| 坑点 | 描述 | 解决方案 |
|------|------|----------|
| ❌ 重复申报 | 同一患者同一病种重复提交 | 申报前校验：`SELECT * FROM vip_mbdeclare_info WHERE idcard=? AND icdcode=? AND dr=0 AND applystatus NOT IN (2,4,9)` |
| ❌ 图片上传失败 | Base64过长或格式错误 | 前端压缩图片，限制5MB以内 |
| ❓ 医保资格校验失败 | 患者未参保或参保信息不一致 | 先调用医保接口校验，校验通过再保存 |
| ❓ 病种编码不匹配 | 地方病种编码与国家编码映射错误 | 使用 `disease_mapping` 表做映射转换 |

### 7.2 初审环节

| 坑点 | 描述 | 解决方案 |
|------|------|----------|
| ❌ 并发审批 | 两人同时审批同一单 | 使用Redis分布式锁：`SETNX lock:declare:{id} {userId} EX 300` |
| ❌ 状态不一致 | 数据库状态更新了但工作流没推动 | 使用 `@Transactional` 确保原子性 |
| ❓ 体检状态判断 | `physicalStatus` 值含义混淆 | 定义枚举注释清晰：`1=需要体检 2=不需要体检 3=已体检` |

### 7.3 专家审核环节

| 坑点 | 描述 | 解决方案 |
|------|------|----------|
| ❌ 多病种漏审 | 患者申报多个病种，专家漏审某一个 | 系统自动拆单，每个病种单独生成审批任务 |
| ❌ 待遇期计算错误 | 恶性肿瘤和普通病种生效时间不同 | 按病种类型分别调用 `getStartDateTime()` |
| ❓ 撤回规则 | 审核后30分钟内才能撤回 | 记录审批时间，校验时间差 |

### 7.4 发卡环节

| 坑点 | 描述 | 解决方案 |
|------|------|----------|
| ❌ 卡号重复使用 | 同一张卡绑定多个账户 | 发卡前查 `vip_card.status`，必须为"未使用"状态 |
| ❌ 激活失败 | 备案记录不存在导致激活失败 | 激活前校验 `t_mb_put_on_rec_detl` 是否存在且状态正确 |
| ❓ 邮寄状态丢失 | 发卡后患者没收到卡 | 使用 `sendflag` 追踪状态，短信+物流双重通知 |

---

## 八、常见问题FAQ

### Q1: 申报状态"审核中"但工作流已结束怎么办？

**原因**：工作流异常结束但数据库状态未同步

```java
// 修复脚本
UPDATE vip_mbdeclare_info 
SET applystatus = 9, modifytime = NOW() 
WHERE id = '申报ID' 
AND NOT EXISTS (
    SELECT 1 FROM ACT_RU_TASK 
    WHERE BUSINESS_KEY_ = '申报ID'
);
```

### Q2: 如何查看某个申报的完整审批链路？

```java
// 调用工作流服务获取历史
ActivitiService activitiService;
List<HistoryTaskVo> histories = activitiService.getHistories(
    new GetHistoriesVo(businessKey)
);
// histories 包含每个环节的开始/结束时间、处理人、处理时长
```

### Q3: 申报材料能批量上传吗？

**可以**，但限制：
- 单次最多3张图片
- 每张图片最大5MB
- 支持格式：JPG、PNG、PDF

### Q4: 不同地区的流程差异在哪里？

| 地区 | 流程差异 |
|------|----------|
| 宝鸡(bj) | 需要体检、初审→体检→专家→发卡 |
| 延安(ya) | 不需要体检，初审→专家→发卡 |
| 商洛(sl) | 复审机制，审核通过即生效 |
| 张家口(zjk) | 支持线上申报，流程略有不同 |

---

## 九、附录：关键枚举速查

### 申报状态 (ApplyStatusEnum)

| 值 | 枚举名 | 中文 |
|----|--------|------|
| 0 | PASSING | 审核中 |
| 1 | PASSFIRST | 初审通过 |
| 2 | NOPASSFIRST | 初审驳回 |
| 3 | PASS | 审核通过 |
| 4 | NOPASS | 审核驳回 |
| 5 | SOMEPASS | 部分通过 |
| 6 | PASSSECOND | 复审通过 |
| 7 | NOPASSSECOND | 复审驳回 |
| 8 | BCZL | 补充资料 |
| 9 | WX | 无效 |
| 10 | Second | 二次审核 |
| 99 | NOSUBMIT | 待提交 |

### 审批类型 (ApprovalTypeEnum)

| 值 | 枚举名 | 中文 |
|----|--------|------|
| 1 | APPROVALTYPE_FIRST | 初审 |
| 2 | APPROVALTYPE_EXPERT | 专家审批 |
| 3 | APPROVALTYPE_REVIEW | 复审 |
| 4 | APPROVALTYPE_SECOND | 二次审核 |

### 审批状态 (ApprovalStatusEnum)

| 值 | 枚举名 | 中文 |
|----|--------|------|
| 0 | PASS | 通过 |
| 1 | NOPASS | 未通过 |
| 2 | ZLBQ | 资料不全 |
| 9 | PRE | 尚未审核 |

### 体检状态 (PhysicalStatusEnum)

| 值 | 枚举名 | 中文 |
|----|--------|------|
| 99 | NOFP | 未分配体检中心 |
| 0 | NEED | 需要体检 |
| 1 | NONEED | 不需要体检 |
| 2 | NOARRIVE | 未到 |
| 3 | GIVEUP | 放弃体检 |

---

📎 **延伸阅读**：
- [项目全貌](picc-mzmtb-server-项目全貌.md) - 快速了解系统整体架构和模块划分
- [API接口全景](picc-mzmtb-server-API接口全景.md) - 申报管理435个接口的详细清单
- [处方与药店管理解析](picc-mzmtb-server-处方与药店管理解析.md) - 申报通过后的处方管理和药店买药流程

**文档结束** ✅

> 如有问题，请联系系统负责人或查阅各模块的单元测试用例。
