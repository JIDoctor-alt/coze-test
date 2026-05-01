# 业务模块 - 慢病初审管理 (auditManagement.vue)

> 🎯 一句话说明：这是对患者提交的申报资料进行"初步审核"的页面，判断材料是否齐全、是否符合申报条件

---

## 这是啥？（小白版）

想象 **初审管理是医院的"分诊台"**：
- 分诊护士 = 初审员
- 查看患者资料 = 检查材料
- 判断：
  - 材料齐全 → 安排体检 或 直接鉴定
  - 材料不全 → 退回补充
  - 不符合条件 → 驳回申报

---

## 核心代码解析

### template 部分

```html
<template>
    <div class="rootDiv main-box">
        <!-- 搜索条件 -->
        <searchCard
            :bjUnitList="unitList"
            :bjPersontypeList="persontypeList"
            :formObj="formObj"
            @search="search"
            @resetFields="resetFields"
        />
        
        <!-- 申报列表表格 -->
        <a-card class="card-top card-table">
            <a-table
                :columns="columns"
                :data-source="datas"
                :pagination="pagination"
                :loading="loading"
                :rowKey="record => record.id"
            >
                <!-- 人员类型 -->
                <div slot="persontype" slot-scope="persontype, record">
                    {{ record.persontype | filterType("persontype") }}
                </div>
                
                <!-- 疾病大类 -->
                <div slot="icdkind" slot-scope="icdkind, record">
                    {{ record.icdkind | filterIcdkind }}
                </div>
                
                <!-- 特殊标志 -->
                <div slot="specialflag1" slot-scope="specialflag1, record">
                    {{ record.specialflag1 | filterSpecialflag1 }}
                </div>
                
                <!-- 操作列 -->
                <span slot="operation" slot-scope="text, record">
                    <a @click="showStaffInfo(record)">资料</a>
                    <a @click="editStaffInfo(record)">编辑资料</a>
                </span>
            </a-table>
        </a-card>
        
        <!-- 初审不通过弹窗 -->
        <auditOpinion
            ref="auditOpinion"
            :keys="selectObj.id"
            :taskId="selectObj.taskId"
            :declareStatusName="selectObj.declareStatusName"
            @getData="initPage(searchParam)"
        />
        
        <!-- 初审结论不一致原因记录弹窗 -->
        <auditOpinionAI
            ref="auditOpinionAI"
            :keys="selectObj.id"
            :taskId="selectObj.taskId"
            @getData="deal(searchParam)"
        />
        
        <!-- 选择直接鉴定/去体检弹窗 -->
        <el-container
            :visible="firstTrialTypevisible"
            title="选择"
            @ok="handleSelectTrialType"
        >
            <a-radio-group v-model="firstTrialType">
                <a-radio value="N">直接鉴定</a-radio>
                <a-radio value="Y">去体检</a-radio>
            </a-radio-group>
        </el-container>
        
        <!-- 资料弹窗 -->
        <el-container :visible="visibleMaterial" title="申请资料" width="80%">
            <applicationInformation2 ref="editPicAI" :row="selectObj" />
        </el-container>
        
        <!-- 编辑资料弹窗 -->
        <el-container :visible="visibleEditMaterial" title="编辑资料" width="80%" @ok="submitFn">
            <applicationInformation2 
                ref="editPic" 
                :row="selectObj" 
                :showIcd="showIcd" 
                :visibleEditMaterial="visibleEditMaterial"
            />
        </el-container>
    </div>
</template>
```

### script 部分

```javascript
import searchCard from "@/components/searchCard/index";
import applicationInformation2 from "@/components/Modal/applicationInformation2";
import auditOpinion from "@/components/Modal/auditOpinion";
import auditOpinionAI from "@/components/Modal/auditOpinionAI";
import tableMinxins from "@/utils/tableMixins.js";
import {
    queryMbDeclareListInFirstTrail,      // 查询初审列表
    updateMbDeclareFirstApprovalInfo,    // 提交初审结论
} from "@/api/apiAuditManagement";
import { firstTrailPassAutoMask } from "@/api/apiIntelligent";  // AI审核

export default {
    components: {
        searchCard,
        applicationInformation2,
        auditOpinion,
        auditOpinionAI
    },
    mixins: [tableMinxins],
    data() {
        return {
            // 初审决策相关
            firstTrialTypevisible: false,  // 选择弹窗
            firstTrialType: 'N',           // 默认直接鉴定 N=直接 Y=去体检
            firstTrialLoading: false,      // 提交loading
            
            // 弹窗控制
            visibleMaterial: false,        // 查看资料弹窗
            visibleEditMaterial: false,    // 编辑资料弹窗
            
            // 数据
            selectObj: {},
            showIcd: true,                // 是否显示身份证
            
            // 表单
            formObj: {
                name: "",
                idcard: "",
                mobile: "",
                declareBeginFrom: "",
                declareBeginTo: "",
                persontype: "",
                ybArea: ""
            },
            
            // 表格
            columns: [],
            datas: [],
            loading: false,
            
            // 搜索参数
            searchParam: {},
            pagination: {
                current: 1,
                pageSize: 10,
                total: 0
            }
        }
    },
    created() {
        this.initPage();
    },
    methods: {
        // 1. 加载初审列表
        initPage(searchObj) {
            this.loading = true;
            let params = {
                ...this.searchParam,
                pageNum: this.pagination.current,
                pageSize: this.pagination.pageSize
            };
            
            queryMbDeclareListInFirstTrail(params).then(res => {
                if (res.status === 0) {
                    this.datas = res.data.list || [];
                    this.pagination.total = res.data.total || 0;
                }
            }).finally(() => {
                this.loading = false;
            });
        },
        
        // 2. 查询
        search(values) {
            this.searchParam = values;
            this.pagination.current = 1;
            this.initPage();
        },
        
        // 3. 查看资料
        showStaffInfo(row) {
            this.selectObj = row;
            this.visibleMaterial = true;
        },
        
        // 4. 编辑资料
        editStaffInfo(row) {
            this.selectObj = row;
            this.showIcd = false;  // 编辑时不显示身份证图片
            this.visibleEditMaterial = true;
        },
        
        // 5. 初审通过 - 弹出选择框
        passFirstTrial(row) {
            this.selectObj = row;
            this.firstTrialTypevisible = true;
        },
        
        // 6. 选择直接鉴定/去体检
        handleSelectTrialType() {
            this.firstTrialTypevisible = false;
            // 根据选择调用不同接口
            this.confirmTrialType();
        },
        
        // 7. 确认初审类型
        confrimSelectTrialType() {
            this.firstTrialLoading = true;
            let params = {
                id: this.selectObj.id,
                taskId: this.selectObj.taskId,
                // 审核结论
                firstTrialResult: 'pass',
                // 是否需要体检
                physicalFlag: this.firstTrialType,
                // 初审意见
                firstTrialOpinion: this.firstTrialOpinion
            };
            
            updateMbDeclareFirstApprovalInfo(params).then(res => {
                if (res.status === 0) {
                    this.$message.success('初审通过');
                    this.initPage(this.searchParam);
                }
            }).finally(() => {
                this.firstTrialLoading = false;
            });
        },
        
        // 8. 初审不通过
        rejectFirstTrial(row) {
            this.selectObj = row;
            this.$refs.auditOpinion.open();  // 打开不通过弹窗
        },
        
        // 9. AI辅助审核
        async autoAuditByAI(row) {
            const res = await firstTrailPassAutoMask({ declareId: row.id });
            if (res.status === 0) {
                const aiResult = res.data;
                // AI判断与初审员判断是否一致
                if (aiResult.isConsistent) {
                    // 一致 → 快速通过
                    this.passFirstTrial(row);
                } else {
                    // 不一致 → 记录差异原因
                    this.selectObj = row;
                    this.$refs.auditOpinionAI.open();
                }
            }
        },
        
        // 10. 提交编辑后的资料
        submitFn() {
            // 获取编辑后的资料
            const editedData = this.$refs.editPic.getData();
            
            api.updateDeclareInfo(editedData).then(res => {
                if (res.status === 0) {
                    this.$message.success('资料更新成功');
                    this.visibleEditMaterial = false;
                    this.initPage();
                }
            });
        }
    }
}
```

---

## 初审流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                        初审管理流程                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────┐
│  收到新申报   │
└──────┬──────┘
       ↓
┌─────────────────┐
│ 查看申请资料    │ ←─── 查看身份证、病历、诊断证明等
│ showStaffInfo() │
└──────┬──────────┘
       ↓
┌─────────────────────────────────────────┐
│                                         │
│  ┌───────────┐  ┌───────────┐          │
│  │ 材料齐全  │  │ 材料不全  │          │
│  └─────┬─────┘  └─────┬─────┘          │
│        ↓              ↓                  │
│  ┌─────┴─────┐  ┌────┴────┐            │
│  │ 决定方式  │  │ 退回补充 │            │
│  │ 1.直接鉴定 │  │         │            │
│  │ 2.去体检   │  │         │            │
│  └─────┬─────┘  └─────────┘            │
│        ↓                                │
│  ┌─────┴────────┐                      │
│  │  提交初审结论 │                      │
│  └─────┬────────┘                      │
│        ↓                                │
│  ┌─────┴─────┐                         │
│  │ 初审完成   │ →→→ 进入下一流程         │
│  │ 体检分配/专家分配                   │
│  └───────────┘                         │
│                                         │
└─────────────────────────────────────────┘
```

---

## 初审状态流转

```
待初审 → 初审通过(需体检) → 体检中 → 体检完成
   ↓
   ├→ 初审通过(直接鉴定) → 专家分配
   │
   └→ 初审不通过 → 退回修改 → 重新提交
```

---

## 知识点

### 🔹 firstTrialType 决策类型
| 值 | 说明 | 后续流程 |
|----|------|----------|
| N | 直接鉴定 | 跳过体检，进入专家分配 |
| Y | 去体检 | 进入体检分配环节 |

### 🔹 AI辅助审核
```javascript
firstTrailPassAutoMask({ declareId })
```
- 调用智能审核接口
- 自动检查材料完整性
- 辅助初审员判断

### 🔹 taskId 任务ID
每个申报在流程中都会有一个 taskId，用于追踪整个审批流程。

### 🔹 审核意见记录
```javascript
{
    id: "申报ID",
    taskId: "任务ID",
    firstTrialResult: "pass|reject",
    physicalFlag: "Y|N",
    firstTrialOpinion: "审核意见内容"
}
```
