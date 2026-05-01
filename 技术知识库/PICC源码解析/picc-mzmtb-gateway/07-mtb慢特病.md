# picchealth/module/mtb - 慢特病管理模块

## 🎯 模块一句话说明
**慢特病管理业务** - 37个文件，处理慢特病的申报、审核、体检、专家分配等全流程

---

## 📁 模块结构

```
mtb/
├── api/            ← 接口控制器 (18个)
├── constant/       ← 常量定义
├── enums/          ← 枚举定义
├── po/             ← 持久化对象
├── utils/          ← 工具类
└── vo/             ← 视图对象
```

---

## 🔑 核心API接口 (18个)

### 1. DocDeclareApi.java

> 🎯 医生端申报接口

### 这是啥？（小白版）
像"医生工作站"，医生在这里帮患者提交慢特病申报。

```java
@Api(tags = "医生申报")
@RestController
@RequestMapping("/docDeclare")
public class DocDeclareApi {
    // 提交申报
    @PostMapping("/declare")
    ApiResponse declare(@RequestBody DeclareVo vo);
    
    // 查询申报列表
    @PostMapping("/list")
    ApiResponse list(@RequestBody QueryVo vo);
    
    // 取消申报
    @PostMapping("/cancel")
    ApiResponse cancel(@RequestBody CancelVo vo);
}
```

---

### 2. MtbDeclareListApi.java

> 🎯 慢特病申报列表

```java
@Api(tags = "慢特病申报列表")
@RestController
@RequestMapping("/mtbDeclareList")
public class MtbDeclareListApi {
    // 查询申报列表
    @PostMapping("/query")
    ApiResponse query(@RequestBody QueryDeclareVO vo);
    
    // 查询详情
    @PostMapping("/detail")
    ApiResponse detail(@RequestBody IdVo vo);
}
```

---

### 3. MtbDeclareExpertAssignApi.java

> 🎯 专家分配

```java
@Api(tags = "专家分配")
@RestController
@RequestMapping("/mtbDeclareExpertAssign")
public class MtbDeclareExpertAssignApi {
    // 自动分配
    @PostMapping("/autoAssign")
    ApiResponse autoAssign(@RequestBody AutoAssignVo vo);
    
    // 手动分配
    @PostMapping("/manualAssign")
    ApiResponse manualAssign(@RequestBody ManualAssignVo vo);
    
    // 撤回分配
    @PostMapping("/withdraw")
    ApiResponse withdraw(@RequestBody WithdrawVo vo);
}
```

---

### 4. MtbdeclarePhysicalApi.java

> 🎯 体检管理

### 这是啥？（小白版）
像"体检中心"，管理患者的体检安排和结果。

```java
@Api(tags = "体检管理")
@RestController
@RequestMapping("/mtbdeclarePhysical")
public class MtbdeclarePhysicalApi {
    // 安排体检
    @PostMapping("/schedule")
    ApiResponse schedule(@RequestBody PhysicalScheduleVo vo);
    
    // 体检结果录入
    @PostMapping("/result")
    ApiResponse result(@RequestBody PhysicalResultVo vo);
    
    // 体检完成确认
    @PostMapping("/complete")
    ApiResponse complete(@RequestBody IdVo vo);
}
```

---

### 5. ProfDeclareApi.java

> 🎯 专家审核

### 这是啥？（小白版）
像"专家评审会"，专家在这里审核患者的申报材料。

```java
@Api(tags = "专家审核")
@RestController
@RequestMapping("/profDeclare")
public class ProfDeclareApi {
    // 初审
    @PostMapping("/firstTrial")
    ApiResponse firstTrial(@RequestBody FirstTrialVo vo);
    
    // 复审
    @PostMapping("/review")
    ApiResponse review(@RequestBody ReviewVo vo);
    
    // 审批通过
    @PostMapping("/approve")
    ApiResponse approve(@RequestBody ApproveVo vo);
    
    // 审批拒绝
    @PostMapping("/reject")
    ApiResponse reject(@RequestBody RejectVo vo);
}
```

---

### 6. MtbDataStatisticsApi.java

> 🎯 数据统计

```java
@Api(tags = "数据统计")
@RestController
@RequestMapping("/mtbDataStatistics")
public class MtbDataStatisticsApi {
    // 申报统计
    @PostMapping("/declare")
    ApiResponse declare(@RequestBody StatVo vo);
    
    // 审核统计
    @PostMapping("/review")
    ApiResponse review(@RequestBody StatVo vo);
    
    // 导出报表
    @PostMapping("/export")
    ApiResponse export(@RequestBody ExportVo vo);
}
```

---

### 7. MtbImportApi.java

> 🎯 数据导入

```java
@Api(tags = "数据导入")
@RestController
@RequestMapping("/mtbImport")
public class MtbImportApi {
    // Excel导入用户
    @PostMapping("/user")
    ApiResponse importUser(@RequestBody MultipartFile file);
    
    // Excel导入申报
    @PostMapping("/declare")
    ApiResponse importDeclare(@RequestBody MultipartFile file);
}
```

---

### 8. MtbUpdateApi.java

> 🎯 数据更新

```java
@Api(tags = "数据更新")
@RestController
@RequestMapping("/mtbUpdate")
public class MtbUpdateApi {
    // 更新申报信息
    @PostMapping("/declare")
    ApiResponse updateDeclare(@RequestBody UpdateDeclareVo vo);
}
```

---

### 9. MtbDrugApi.java

> 🎯 药品管理

```java
@Api(tags = "药品管理")
@RestController
@RequestMapping("/mtbDrug")
public class MtbDrugApi {
    // 查询药品目录
    @PostMapping("/list")
    ApiResponse list(@RequestBody DrugQueryVo vo);
    
    // 查询药品详情
    @PostMapping("/detail")
    ApiResponse detail(@RequestBody IdVo vo);
}
```

---

### 10. MtbDeclareCancelApi.java

> 🎯 申报取消

```java
@Api(tags = "申报取消")
@RestController
@RequestMapping("/mtbDeclareCancel")
public class MtbDeclareCancelApi {
    // 取消申报
    @PostMapping("/cancel")
    ApiResponse cancel(@RequestBody CancelVo vo);
}
```

---

### 11. MtbDeclareSwitchApi.java

> 🎯 申报切换

```java
@Api(tags = "申报切换")
@RestController
@RequestMapping("/mtbDeclareSwitch")
public class MtbDeclareSwitchApi {
    // 切换申报类型
    @PostMapping("/switch")
    ApiResponse switchDeclare(@RequestBody SwitchVo vo);
}
```

---

### 12. MtbMbDeclareApi.java

> 🎯 慢特病申报关联

```java
@Api(tags = "慢特病申报关联")
@RestController
@RequestMapping("/mtbMbDeclare")
public class MtbMbDeclareApi {
    // 关联查询
    @PostMapping("/query")
    ApiResponse query(@RequestBody QueryVo vo);
}
```

---

### 13. MtbPrescriptionManagementApi.java

> 🎯 处方管理

```java
@Api(tags = "处方管理")
@RestController
@RequestMapping("/mtbPrescription")
public class MtbPrescriptionManagementApi {
    // 查询处方
    @PostMapping("/list")
    ApiResponse list(@RequestBody PrescriptionQueryVo vo);
    
    // 处方详情
    @PostMapping("/detail")
    ApiResponse detail(@RequestBody IdVo vo);
}
```

---

### 14. MtbFileApi.java

> 🎯 文件管理

```java
@Api(tags = "文件管理")
@RestController
@RequestMapping("/mtbFile")
public class MtbFileApi {
    // 上传文件
    @PostMapping("/upload")
    ApiResponse upload(@RequestBody MultipartFile file);
    
    // 下载文件
    @GetMapping("/download/{id}")
    ApiResponse download(@PathVariable String id);
}
```

---

### 15-18. 其他API

| API类 | 说明 |
|-------|------|
| MtbExtLoginApi | 专家端登录 |
| MtbInfoMosaicApi | 信息整合 |
| MtbVipMbDeclareFirstTrialApi | VIP申报初审 |
| TFilingManApi | 填报人管理 |
| XcxDeclareApi | 小程序申报 |
| XcxIndexApi | 小程序首页 |
| XcxLoginApi | 小程序登录 |
| XjsApi | 新疆接口 |
| ZipDownloadApi | 批量下载 |

---

## 📋 枚举定义

### FlowStatusEnum - 流程状态

```java
public enum FlowStatusEnum {
    DRAFT("草稿"),
    SUBMITTED("已提交"),
    EXPERT_FIRST("专家初审"),
    EXPERT_SECOND("专家复审"),
    PHYSICAL("体检中"),
    PHYSICAL_PASS("体检通过"),
    APPROVED("已通过"),
    REJECTED("已拒绝"),
    CANCELLED("已取消");
}
```

### ApplyStatusEnum - 申请状态

```java
public enum ApplyStatusEnum {
    PENDING("待审核"),
    APPROVED("已通过"),
    REJECTED("已拒绝"),
    WITHDRAWN("已撤回");
}
```

---

## 🔧 工具类

### FlagUtils.java / FlagLocal.java

> 🎯 Flag本地线程存储

```java
// FlagLocal - 存储当前请求的flag(地区标识)
public class FlagLocal {
    private String flag;  // 地区标识
}

// FlagUtils - ThreadLocal操作工具
public class FlagUtils {
    private static ThreadLocal<FlagLocal> flagThreadLocal = new ThreadLocal<>();
    
    public static void setFlagLocal(FlagLocal flagLocal);
    public static FlagLocal getFlagLocal();
    public static void remove();
}
```

---

## 🔄 与mb模块的区别

| 方面 | mb模块 | mtb模块 |
|------|--------|---------|
| 全称 | 慢病管理 | 慢特病管理 |
| 定位 | 门诊慢病 | 慢病+特殊病种 |
| 文件数 | 523个 | 37个 |
| 复杂度 | 更高 | 相对简化 |
| API数 | 60+ | 18 |

### 业务流程对比

**慢病(mb)流程:**
```
申报 → 初审 → 复审 → 体检 → 待遇享受
```

**慢特病(mtb)流程:**
```
申报 → 专家分配 → 初审 → 复审 → 体检 → 审批 → 待遇享受
```

---

## 📁 文件清单

### API (18个)
```
DocDeclareApi              - 医生申报
MtbDataStatisticsApi       - 数据统计
MtbDeclareCancelApi        - 申报取消
MtbDeclareExpertAssignApi  - 专家分配
MtbDeclareListApi          - 申报列表
MtbdeclarePhysicalApi      - 体检管理
MtbDeclareSwitchApi        - 申报切换
MtbDrugApi                 - 药品管理
MtbExtLoginApi             - 专家登录
MtbFileApi                 - 文件管理
MtbImportApi               - 数据导入
MtbInfoMosaicApi           - 信息整合
MtbMbDeclareApi            - 慢特病关联
MtbPrescriptionManagementApi - 处方管理
MtbUpdateApi               - 数据更新
MtbVipMbDeclareFirstTrialApi - VIP初审
ProfDeclareApi             - 专家审核
TFilingManApi              - 填报人管理
XcxDeclareApi              - 小程序申报
XcxIndexApi                - 小程序首页
XcxLoginApi                - 小程序登录
XjsApi                     - 新疆接口
ZipDownloadApi             - 批量下载
```

---

## 🎯 小白理解要点

1. **mtb是mb的简化版** - 慢特病流程更直接
2. **医生和专家分开** - 不同角色不同入口
3. **体检是必经环节** - 需要体检结果才能审批
4. **Flag标识地区** - 通过ThreadLocal在请求间传递

---

**相关文档**:
- `00-项目概览.md` - 整体架构
- `02-mb慢病管理.md` - 慢病模块详解
