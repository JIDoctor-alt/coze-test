# 业务模块 - 体检站点管理 (physicalManage.vue)

> 🎯 一句话说明：这是管理"体检机构"信息的页面，包括新增、编辑、启用/停用等操作

---

## 这是啥？（小白版）

想象 **体检站点管理是医院的"体检中心名单"**：
- 名单列表 = 机构信息表
- 添加新中心 = 新增记录
- 更换负责人 = 编辑信息
- 暂停营业 = 停用机构

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
            :colSpan="8"
            @resetFields="resetFields"
        />
        
        <!-- 体检站点列表 -->
        <a-card class="card-top card-table">
            <div slot="title">
                <img src="@/assets/images/person_icon.png">体检站点列表
            </div>
            <div slot="extra">
                <a-button @click="addUsers('体检站点管理')">新增</a-button>
                <a-button @click="showModal('check')">启用</a-button>
                <a-button @click="showModal('stop')">停用</a-button>
            </div>
            
            <a-table
                :columns="physicalManageColumns"
                :data-source="physicalManageData"
                :pagination="pagination"
                :loading="loading"
                :rowSelection="rowSelection"
                :rowKey="record => record.id"
            >
                <!-- 状态 -->
                <div slot="status" slot-scope="status, record">
                    {{ record.status | filterPhysicalaccountlocked }}
                </div>
            </a-table>
            
            <!-- 编辑/新增弹窗 -->
            <editUserInformation
                ref="editUserInformation"
                :modalTitle="modalTitle"
                :userFormObj="userFormObj"
                :phoneRequire="phoneRequire"
                @change="initPage(searchParam)"
                checkSite="checkSite"
            />
        </a-card>
        
        <!-- 启用/停用确认弹窗 -->
        <el-container
            :visible="visible"
            title="确认框"
            :loading="checkLoading"
            width="520px"
            @ok="handleOk"
        >
            <p style="text-align:center;font-size:18px">
                确定{{ this.changeState }}此机构吗
            </p>
        </el-container>
    </div>
</template>
```

### script 部分

```javascript
import searchCard from "@/components/searchCard/index";
import editUserInformation from "@/components/Modal/editUserInformation";
import ChronicDis from "./ChronicDis.js";       // 表格配置
import tableMinxins from "@/utils/tableMixins.js";
import {
    getPhysicalOrgList,      // 获取站点列表
    updateStatus,            // 更新启用/停用状态
} from "@/api/apiPhysicalManage.js";

export default {
    components: {
        searchCard,
        editUserInformation
    },
    mixins: [tableMinxins],
    data() {
        return {
            // 表格
            physicalManageColumns: [],
            physicalManageData: [],
            loading: false,
            
            // 分页
            pagination: {
                pageSize: 10,
                current: 1,
                total: 0,
                showTotal: (total) => `共 ${total} 条`,
                showSizeChanger: true,
                pageSizeOptions: ["10", "20", "35", "50"]
            },
            
            // 搜索条件
            formObj: {
                orgname: "",                    // 机构名称
                newPhysicalManageStatus: ""      // 状态
            },
            
            // 表单数据
            userFormObj: {
                orgname: "",        // 机构名称
                orgcode: "",        // 机构编码
                managername: "",    // 负责人
                mobile: "",         // 联系电话
                address: "",        // 地址
                province: "",       // 省
                city: "",           // 市
                district: ""       // 区
            },
            
            // 弹窗
            modalTitle: "",
            visible: false,
            checkLoading: false,
            changeState: "",       // "启用" 或 "停用"
            
            // 选中行
            selectedRows: [],
            rowSelection: {
                type: "radio",
                selectedRowKeys: [],
                onChange: (selectedRowKeys, selectedRows) => {
                    this.selectedRows = selectedRows[0];
                    this.rowSelection.selectedRowKeys = selectedRowKeys;
                }
            },
            
            // 搜索参数
            searchParam: {}
        }
    },
    mounted() {
        this.initPage();
    },
    methods: {
        // 1. 加载体检站点列表
        initPage(searchObj) {
            this.loading = true;
            this.physicalManageColumns = ChronicDis.physicalManageColumns;
            
            let params = {
                flag: "0",  // 0=宝鸡 1=阜新
                orgname: "",
                pageVo: {
                    pageNum: this.pagination.current,
                    pageSize: this.pagination.pageSize
                },
                status: ""
            };
            
            if (searchObj) {
                params.orgname = searchObj.orgname;
                params.status = searchObj.newPhysicalManageStatus;
            }
            
            getPhysicalOrgList(params).then(res => {
                if (res.status === 0) {
                    this.loading = false;
                    this.physicalManageData = res.data.data || [];
                    this.pagination.total = res.data.total || 0;
                }
            });
        },
        
        // 2. 查询
        search(values) {
            this.searchParam = values;
            this.pagination.current = 1;
            this.initPage(values);
        },
        
        // 3. 新增/编辑
        addUsers(title) {
            this.modalTitle = title;
            this.userFormObj = {
                orgname: "",
                orgcode: "",
                managername: "",
                mobile: "",
                address: "",
                province: "",
                city: "",
                district: ""
            };
            this.$refs.editUserInformation.open();
        },
        
        // 4. 启用/停用
        showModal(values) {
            if (this.selectedRows.length === 0) {
                this.$message.warning('请选择一条记录');
                return;
            }
            
            this.visible = true;
            if (values === "check") {
                this.changeState = "启用";
            } else {
                this.changeState = "停用";
            }
        },
        
        // 5. 确认启用/停用
        handleOk() {
            let params = {
                flag: "0",
                id: this.selectedRows.id,
                status: this.changeState === "启用" ? "0" : "1"  // 0启用 1停用
            };
            
            this.checkLoading = true;
            updateStatus(params).then(res => {
                if (res.status === 0) {
                    this.visible = false;
                    this.$message.success('修改成功');
                    this.initPage(this.searchParam);
                }
            }).finally(() => {
                this.checkLoading = false;
            });
        }
    }
}
```

---

## 体检机构数据结构

```javascript
{
    id: "机构ID",
    orgname: "宝鸡市中心医院体检中心",
    orgcode: "61030001",
    managername: "张院长",
    mobile: "0917-1234567",
    status: "0",          // 0启用 1停用
    province: "陕西省",
    city: "宝鸡市",
    district: "渭滨区",
    address: "宝鸡市渭滨区经二路108号",
    createTime: "2024-01-01",
    updateTime: "2024-01-15"
}
```

---

## 操作流程

### 新增机构
```
点击"新增"按钮
    ↓
弹出编辑弹窗
    ↓
填写机构信息
    ├─ 机构名称 *
    ├─ 机构编码 *
    ├─ 负责人
    ├─ 联系电话
    ├─ 所在地区
    └─ 详细地址
    ↓
点击"提交"
    ↓
保存到数据库
```

### 启用/停用机构
```
选中一条记录
    ↓
点击"启用"或"停用"
    ↓
弹出确认框
    ↓
确认操作
    ↓
更新状态
    ↓
列表刷新
```
