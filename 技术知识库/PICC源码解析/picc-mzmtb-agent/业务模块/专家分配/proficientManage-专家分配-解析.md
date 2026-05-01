# 业务模块 - 慢病专家分配 (proficientManage.vue)

> 🎯 一句话说明：这是将体检完成的患者分配给"专家医生"进行最终鉴定的页面

---

## 这是啥？（小白版）

想象 **专家分配是医院的"专家门诊挂号"**：
- 患者体检报告 = 体检结果
- 专家库 = 各科室医生名单
- 分配过程 = 挂号分诊
- 专家给出结论 = 最终诊断

---

## 核心代码解析

### template 部分

```html
<template>
    <div class="main-box">
        <!-- 搜索条件 -->
        <searchCard
            :formObj="formObj"
            @search="search"
            @resetFields="resetFields"
        />
        
        <!-- 体检完成的申报列表 -->
        <a-card class="card-top card-table">
            <div slot="title">
                <img src="@/assets/images/person_icon.png">体检完成的申报列表
            </div>
            <div slot="extra">
                <a-button @click="actionsTable('auto')">自动分配</a-button>
                <a-button @click="actionsTable('manual')">手动分配</a-button>
                <a-button @click="actionsTable('recall')">撤回分配</a-button>
            </div>
            
            <!-- 表格 -->
            <a-table
                :columns="columns"
                :data-source="data"
                :pagination="pagination"
                :row-selection="rowSelection"
                :loading="loading"
                :rowKey="record => record.id"
            >
                <!-- 性别 -->
                <div slot="sex" slot-scope="sex, record">
                    {{ record.sex | filterSex }}
                </div>
                
                <!-- 体检来源 -->
                <div slot="physicalsource" slot-scope="physicalsource, record">
                    {{ record.physicalsource == 1 ? "初审体检" : "复审体检" }}
                </div>
                
                <!-- 操作列 -->
                <span slot="modifier" slot-scope="modifier, record">
                    <a @click="showReport(record, false)">体检报告</a>
                    <a @click="showReport(record, true)">编辑体检报告</a>
                </span>
            </a-table>
        </a-card>
        
        <!-- 查看体检报告弹窗 -->
        <el-container :visible="visible" title="体检报告" width="80%">
            <img v-for="item in reportList" :src="item.src" />
        </el-container>
        
        <!-- 编辑体检报告弹窗 -->
        <el-container :visible="editVisible" title="编辑体检报告" @ok="submitFn">
            <canvas id="canvas"></canvas>
        </el-container>
        
        <!-- 手动分配弹窗 -->
        <el-container :visible="visibleManual" title="专家分配" width="75%">
            <proficientView
                :ids="ids"
                :reviewIds="reviewIds"
                :taskIds="taskIds"
                @updateList="updateList"
            />
        </el-container>
        
        <!-- 自动分配确认弹窗 -->
        <el-container
            :visible="visibletext"
            confirmText="确定进行批量自动分配吗?"
            @ok="updateExpertAutoFn"
            :loading="autoLoading"
        />
    </div>
</template>
```

### script 部分

```javascript
import searchCard from "@/components/searchCard/index";
import proficientView from "./components/proficientView";  // 专家选择组件
import api from "@/api/apiMbExpertAssign";
import tableCon from "./config/config";
import tableMinxins from "@/utils/tableMixins";

export default {
    components: {
        searchCard,
        proficientView
    },
    mixins: [tableMinxins],
    data() {
        return {
            // 表格数据
            data: [],
            columns: [],
            loading: false,
            
            // 分页
            pagination: {
                current: 1,
                pageSize: 10,
                total: 0
            },
            
            // 搜索条件
            formObj: {
                name: "",
                idcard: "",
                mobile: "",
                physicalstatus: "",
                declareBeginFrom: "",
                declareBeginTo: "",
                ybArea: ""
            },
            
            // 选中行
            rowSelection: {
                type: "checkbox",
                selectedRowKeys: [],
                onChange: (selectedRowKeys, selectedRows) => {
                    this.selectedRows = [...selectedRows];
                    this.rowSelection.selectedRowKeys = [...selectedRowKeys];
                }
            },
            
            // 弹窗控制
            visible: false,              // 查看报告
            editVisible: false,          // 编辑报告
            visibleManual: false,        // 手动分配
            visibletext: false,          // 自动分配确认
            autoLoading: false,
            
            // 数据
            reportList: [],              // 体检报告图片
            ids: "",                     // 申报ID列表
            reviewIds: "",              // 复审ID列表
            taskIds: "",                 // 任务ID列表
            
            // 其他
            selectedRows: [],
            searchParams: {}
        }
    },
    created() {
        this.initPage();
    },
    methods: {
        // 1. 加载数据
        initPage(searchObj) {
            this.loading = true;
            let params = {
                ...this.searchParams,
                flag: "0",  // 0=宝鸡 1=阜新
                pageNum: this.pagination.current,
                pageSize: this.pagination.pageSize
            };
            
            api.getExpertAssignList(params).then(res => {
                if (res.status === 0) {
                    this.data = res.data.list || [];
                    this.pagination.total = res.data.total || 0;
                }
            }).finally(() => {
                this.loading = false;
            });
        },
        
        // 2. 查询
        search(values) {
            this.searchParams = values;
            this.pagination.current = 1;
            this.initPage();
        },
        
        // 3. 批量操作（自动/手动/撤回）
        actionsTable(type) {
            switch (type) {
                case 'auto':
                    // 自动分配
                    if (this.selectedRows.length === 0) {
                        this.$message.warning('请选择要分配的数据');
                        return;
                    }
                    this.visibletext = true;
                    break;
                    
                case 'manual':
                    // 手动分配
                    if (this.selectedRows.length === 0) {
                        this.$message.warning('请选择要分配的数据');
                        return;
                    }
                    this.prepareIds();
                    this.visibleManual = true;
                    break;
                    
                case 'recall':
                    // 撤回分配
                    if (this.selectedRows.length === 0) {
                        this.$message.warning('请选择要撤回的数据');
                        return;
                    }
                    this.recallAssign();
                    break;
            }
        },
        
        // 4. 准备IDs
        prepareIds() {
            let ids = [];
            let reviewIds = [];
            let taskIds = [];
            
            this.selectedRows.forEach(row => {
                ids.push(row.id);
                reviewIds.push(row.reviewId);
                taskIds.push(row.taskId);
            });
            
            this.ids = ids.join(',');
            this.reviewIds = reviewIds.join(',');
            this.taskIds = taskIds.join(',');
        },
        
        // 5. 自动分配
        updateExpertAutoFn() {
            this.autoLoading = true;
            this.prepareIds();
            
            api.autoAssignExpert({
                ids: this.ids,
                reviewIds: this.reviewIds,
                taskIds: this.taskIds
            }).then(res => {
                if (res.status === 0) {
                    this.$message.success('自动分配成功');
                    this.visibletext = false;
                    this.rowSelection.selectedRowKeys = [];
                    this.selectedRows = [];
                    this.initPage();
                }
            }).finally(() => {
                this.autoLoading = false;
            });
        },
        
        // 6. 撤回分配
        recallAssign() {
            this.prepareIds();
            
            api.recallExpertAssign({
                ids: this.ids,
                reviewIds: this.reviewIds,
                taskIds: this.taskIds
            }).then(res => {
                if (res.status === 0) {
                    this.$message.success('撤回成功');
                    this.rowSelection.selectedRowKeys = [];
                    this.selectedRows = [];
                    this.initPage();
                }
            });
        },
        
        // 7. 查看体检报告
        showReport(row, isEdit) {
            api.getReportPicture({ declareId: row.id }).then(res => {
                if (res.status === 0) {
                    this.reportList = res.data || [];
                    if (isEdit) {
                        this.editVisible = true;
                    } else {
                        this.visible = true;
                    }
                }
            });
        },
        
        // 8. 提交编辑后的报告
        submitFn() {
            // 获取canvas中编辑后的图片
            const canvas = document.getElementById('canvas');
            const imageData = canvas.toDataURL('image/jpeg');
            
            api.updateReportPicture({
                declareId: this.selectObj.id,
                imageData: imageData
            }).then(res => {
                if (res.status === 0) {
                    this.$message.success('保存成功');
                    this.editVisible = false;
                }
            });
        },
        
        // 9. 分配完成刷新列表
        updateList() {
            this.visibleManual = false;
            this.rowSelection.selectedRowKeys = [];
            this.selectedRows = [];
            this.initPage();
        }
    }
}
```

---

## 专家分配流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                     专家分配流程                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────┐
│ 体检完成    │
└──────┬──────┘
       ↓
┌─────────────────┐
│ 进入专家分配列表 │
└──────┬──────────┘
       ↓
       ├─────────────┐
       ↓             ↓
  ┌────┴────┐   ┌────┴────┐
  │ 自动分配 │   │ 手动分配 │
  │ (AI)   │   │ (人工)  │
  └───┬────┘   └───┬────┘
      ↓            ↓
  系统按规则       人工选择
  智能分配         专家
      ↓            ↓
      └─────┬───────┘
            ↓
    ┌───────┴───────┐
    │   分配成功    │
    │ 通知专家审核  │
    └───────┬───────┘
            ↓
    ┌───────┴───────┐
    │   撤回分配    │ (如需修改)
    └───────────────┘
```

---

## 数据结构

### 专家信息
```javascript
{
    id: "专家ID",
    name: "王主任",
    hospital: "宝鸡市中心医院",
    title: "主任医师",           // 职称
    specialty: "心血管内科",     // 专业
    mobile: "13800000001",
    status: "0",                // 0可用 1停用
    assignCount: 15            // 当前已分配数
}
```

### 分配参数
```javascript
{
    ids: "id1,id2,id3",         // 申报ID列表(逗号分隔)
    reviewIds: "rid1,rid2",    // 复审ID列表
    taskIds: "tid1,tid2",      // 任务ID列表
    expertId: "专家ID"          // 手动分配时使用
}
```

---

## 知识点

### 🔹 自动分配规则
系统会根据以下维度自动匹配专家：
- 专家的专业领域与疾病类型匹配
- 专家当前工作量（分配数量）
- 专家状态（是否可用）

### 🔹 批量操作
```javascript
// 逗号分隔的ID字符串
ids: "123,456,789"
```
- 支持多选 checkbox
- 一次性分配/撤回多个

### 🔹 体检报告编辑
使用 Canvas 画布进行图片标注和编辑，编辑后以 Base64 格式提交。
