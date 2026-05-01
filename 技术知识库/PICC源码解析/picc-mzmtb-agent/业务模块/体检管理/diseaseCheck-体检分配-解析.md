# 业务模块 - 慢病体检分配 (diseaseCheck.vue)

> 🎯 一句话说明：这是将需要体检的患者分配到"体检机构"的页面

---

## 这是啥？（小白版）

想象 **体检分配是医院的"体检中心预约"**：
- 患者 = 体检申请人
- 体检机构 = 体检中心/医院
- 预约单 = 分配记录
- 体检报告 = 完成证明

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
            :colSpan="6"
            :gutter="30"
            @resetFields="resetFields"
        />
        
        <!-- 体检分配列表 -->
        <a-card class="card-top card-table">
            <div slot="title">
                <img src="@/assets/images/person_icon.png">体检分配列表
            </div>
            <div slot="extra">
                <a-button @click="actionsTable('manual')">手动分配</a-button>
                <a-button @click="actionsTable('recall')">撤回分配</a-button>
            </div>
            
            <a-table
                :columns="columns"
                :data-source="data"
                :pagination="pagination"
                :row-selection="rowSelection"
                :loading="loading"
                :rowKey="record => record.id"
            >
                <!-- 体检状态 -->
                <div slot="physicalstatus" slot-scope="physicalstatus, record">
                    {{ record.physicalstatus | filterBjPhysicalstatus }}
                </div>
                
                <!-- 体检来源 -->
                <div slot="physicalsource" slot-scope="physicalsource, record">
                    {{ record.physicalsource == 1 ? "初审体检" : "复审体检" }}
                </div>
                
                <!-- 操作 -->
                <a slot="modifier" @click="showDetail(record)">详情</a>
            </a-table>
        </a-card>
        
        <!-- 体检分配详情弹窗 -->
        <el-container :visible="visible" title="体检分配详情" width="60%">
            <a-table
                :columns="columnsDet"
                :data-source="dataDetail"
                :pagination="false"
            >
                <div slot="booktime" slot-scope="booktime, record">
                    {{ record.booktime | filterDate }}
                </div>
                <div slot="status" slot-scope="status, record">
                    {{ record.status | filterTypeBjPhysicalstatus("physicalstatus") }}
                </div>
            </a-table>
        </el-container>
        
        <!-- 手动分配弹窗 -->
        <el-container :visible="visibleManual" title="体检机构分配" width="75%">
            <physicalOrg
                ref="physicalOrg"
                :assign="manualFun"
                :orgList="orgObj.data"
                :paginationOrg="paginationOrg"
            />
        </el-container>
    </div>
</template>
```

### script 部分

```javascript
import searchCard from "@/components/searchCard/index";
import physicalOrg from "./components/physicalOrg";  // 体检机构选择组件
import api from "@/api/apiMbPhysicalAssign";
import tableCon from "./config/config";
import tableMinxins from "@/utils/tableMixins";

export default {
    components: {
        searchCard,
        physicalOrg
    },
    mixins: [tableMinxins],
    data() {
        return {
            // 表格
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
            
            // 弹窗
            visible: false,           // 详情弹窗
            visibleManual: false,     // 手动分配弹窗
            
            // 详情数据
            dataDetail: [],
            columnsDet: [],
            
            // 体检机构
            orgObj: {},
            paginationOrg: {
                pageSize: 10,
                current: 1,
                total: 0
            },
            
            // ID列表
            ids: "",
            reviewId: "",
            taskIds: "",
            
            // 其他
            searchParams: {},
            selectedRows: [],
            recallLoading: false
        }
    },
    created() {
        this.initPage();
    },
    methods: {
        // 1. 加载体检分配列表
        initPage(searchObj) {
            this.loading = true;
            let params = {
                ...this.searchParams,
                flag: "0",  // 0=宝鸡 1=阜新
                pageNum: this.pagination.current,
                pageSize: this.pagination.pageSize
            };
            
            api.getAssignList(params).then(res => {
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
        
        // 3. 批量操作
        actionsTable(type) {
            if (this.selectedRows.length === 0) {
                this.$message.warning('请选择要操作的数据');
                return;
            }
            
            // 准备ID列表
            this.prepareIds();
            
            if (type === 'manual') {
                // 手动分配
                this.visibleManual = true;
            } else if (type === 'recall') {
                // 撤回分配
                this.recallAssign();
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
            this.reviewId = reviewIds.join(',');
            this.taskIds = taskIds.join(',');
        },
        
        // 5. 查看详情
        showDetail(row) {
            let params = {
                flag: "0",
                declareid: row.id
            };
            
            api.getAssignDetail(params).then(res => {
                if (res.status === 0) {
                    this.visible = true;
                    this.dataDetail = res.data;
                }
            });
        },
        
        // 6. 手动分配机构
        manualFun(orgId) {
            api.manualAssignOrg({
                ids: this.ids,
                reviewId: this.reviewId,
                taskIds: this.taskIds,
                orgId: orgId
            }).then(res => {
                if (res.status === 0) {
                    this.$message.success('分配成功');
                    this.visibleManual = false;
                    this.rowSelection.selectedRowKeys = [];
                    this.selectedRows = [];
                    this.initPage();
                }
            });
        },
        
        // 7. 撤回分配
        recallAssign() {
            this.recallLoading = true;
            
            api.recallAssign({
                ids: this.ids,
                reviewId: this.reviewId,
                taskIds: this.taskIds
            }).then(res => {
                if (res.status === 0) {
                    this.$message.success('撤回成功');
                    this.rowSelection.selectedRowKeys = [];
                    this.selectedRows = [];
                    this.initPage();
                }
            }).finally(() => {
                this.recallLoading = false;
            });
        }
    }
}
```

---

## 体检状态流转

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ 未分配  │ →→ │ 已分配  │ →→ │ 体检中  │ →→ │ 已完成  │
│ (0)    │    │ (1)    │    │ (2)    │    │ (7)    │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
     ↓
  撤回 → 返回未分配状态
```

---

## 体检机构分配流程

```
┌─────────────────────────────────────────────────────────┐
│                   体检机构分配                            │
└─────────────────────────────────────────────────────────┘

选择患者记录
    ↓
点击"手动分配"
    ↓
弹出机构选择列表
    ↓
选择体检机构
    ↓
填写预约信息
    ├─ 预约时间
    ├─ 预约时段
    └─ 注意事项
    ↓
确认分配
    ↓
发送短信通知患者
    ↓
分配完成，状态变为"已分配"
```
