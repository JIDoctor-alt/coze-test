# 业务模块 - 慢病用户管理 (userManage.vue)

> 🎯 一句话说明：这是管理"慢病患者信息"的页面，包括查询、修改、导入等操作

---

## 这是啥？（小白版）

想象 **用户管理是医院的"患者档案室"**：
- 档案袋 = 患者信息
- 添加患者 = 新增记录
- 修改信息 = 纠错更正
- 批量建档 = Excel导入

---

## 核心代码解析

### template 部分

```html
<template>
    <div class="main-box">
        <!-- 搜索条件 -->
        <searchCard
            :formObj="formObj"
            :bjUnitList="unitList"
            :bjPersontypeList="persontypeList"
            @search="search"
            @resetFields="resetFields"
        />
        
        <!-- 患者列表 -->
        <a-card class="card-top card-table">
            <div slot="title">
                <img src="@/assets/images/person_icon.png">慢病患者列表
            </div>
            <div slot="extra">
                <a-button @click="exportData">导出</a-button>
                <a-button @click="importData">导入</a-button>
            </div>
            
            <a-table
                :columns="columns"
                :data-source="data"
                :pagination="pagination"
                :loading="loading"
                :rowKey="record => record.id"
            >
                <!-- 患者类型 -->
                <div slot="persontype" slot-scope="persontype, record">
                    {{ record.persontype | filterType("persontype") }}
                </div>
                
                <!-- 服务状态 -->
                <div slot="servicestatus" slot-scope="servicestatus, record">
                    <a-tag :color="getStatusColor(servicestatus)">
                        {{ getStatusText(servicestatus) }}
                    </a-tag>
                </div>
                
                <!-- 手机号脱敏 -->
                <div slot="mobile" slot-scope="mobile, record">
                    {{ record.mobile | filterMobile }}
                </div>
                
                <!-- 操作列 -->
                <span slot="action" slot-scope="record">
                    <a @click="viewDetail(record)">详情</a>
                    <a @click="editInfo(record)">编辑</a>
                </span>
            </a-table>
        </a-card>
        
        <!-- 编辑弹窗 -->
        <el-container :visible="editVisible" title="编辑患者信息" @ok="submitEdit">
            <a-form :form="form">
                <a-row>
                    <a-col :span="12">
                        <a-form-item label="姓名">
                            <a-input v-model="form.name" />
                        </a-form-item>
                    </a-col>
                    <a-col :span="12">
                        <a-form-item label="身份证">
                            <a-input v-model="form.idcard" />
                        </a-form-item>
                    </a-col>
                </a-row>
                <a-row>
                    <a-col :span="12">
                        <a-form-item label="手机号">
                            <a-input v-model="form.mobile" />
                        </a-form-item>
                    </a-col>
                    <a-col :span="12">
                        <a-form-item label="服务状态">
                            <a-select v-model="form.servicestatus">
                                <a-select-option value="1">正常</a-select-option>
                                <a-select-option value="0">暂停</a-select-option>
                            </a-select>
                        </a-form-item>
                    </a-col>
                </a-row>
            </a-form>
        </el-container>
    </div>
</template>
```

### script 部分

```javascript
import searchCard from "@/components/searchCard/index";
import api from "@/api/apiUserManage";
import tableMinxins from "@/utils/tableMixins";

export default {
    components: {
        searchCard
    },
    mixins: [tableMinxins],
    data() {
        return {
            // 搜索条件
            formObj: {
                name: "",
                idcard: "",
                mobile: "",
                persontype: "",
                servicestatus: "",
                ybArea: ""
            },
            
            // 表格
            columns: [
                { title: '姓名', dataIndex: 'name', width: 100 },
                { title: '身份证', dataIndex: 'idcard', width: 180 },
                { title: '手机号', dataIndex: 'mobile', scopedSlots: { customRender: 'mobile' } },
                { title: '人员类型', dataIndex: 'persontype', scopedSlots: { customRender: 'persontype' } },
                { title: '服务状态', dataIndex: 'servicestatus', scopedSlots: { customRender: 'servicestatus' } },
                { title: '有效期起', dataIndex: 'validFrom', width: 120 },
                { title: '有效期止', dataIndex: 'validTo', width: 120 },
                { title: '操作', key: 'action', width: 150, scopedSlots: { customRender: 'action' } }
            ],
            data: [],
            loading: false,
            
            // 分页
            pagination: {
                current: 1,
                pageSize: 10,
                total: 0
            },
            
            // 弹窗
            editVisible: false,
            form: {},
            
            // 其他
            unitList: [],
            persontypeList: [],
            searchParams: {}
        }
    },
    created() {
        this.initPage();
        this.getUnitList();
    },
    methods: {
        // 1. 加载患者列表
        initPage() {
            this.loading = true;
            api.getUserList({
                ...this.searchParams,
                pageNum: this.pagination.current,
                pageSize: this.pagination.pageSize
            }).then(res => {
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
        
        // 3. 查看详情
        viewDetail(row) {
            this.$router.push({
                path: '/userDetail',
                query: { id: row.id }
            });
        },
        
        // 4. 编辑
        editInfo(row) {
            this.form = { ...row };
            this.editVisible = true;
        },
        
        // 5. 提交编辑
        submitEdit() {
            api.updateUserInfo(this.form).then(res => {
                if (res.status === 0) {
                    this.$message.success('修改成功');
                    this.editVisible = false;
                    this.initPage();
                }
            });
        },
        
        // 6. 导入
        importData() {
            this.$refs.upload.click();
        },
        
        // 7. 导出
        exportData() {
            api.exportUserList(this.searchParams).then(res => {
                this.$downloadFileByBase64(res, '患者信息导出.xls');
            });
        },
        
        // 8. 获取状态颜色
        getStatusColor(status) {
            return status === '1' ? 'green' : 'red';
        },
        
        // 9. 获取状态文字
        getStatusText(status) {
            return status === '1' ? '正常' : '暂停';
        }
    }
}
```

---

## 患者数据结构

```javascript
{
    id: "患者ID",
    name: "张三",
    idcard: "610302199001011234",
    mobile: "13800000000",
    sex: "1",
    birthdate: "1990-01-01",
    persontype: "1",           // 1职工 2居民
    servicestatus: "1",        // 1正常 0暂停
    icdcode: "I10",           // 疾病编码
    icdname: "高血压",         // 疾病名称
    validFrom: "2024-01-01",  // 有效期起
    validTo: "2026-01-01",    // 有效期止
    bjUnitName: "宝鸡市人民医院",
    cardNo: "MB123456789",    // 慢病卡号
    createTime: "2024-01-01",
    updateTime: "2024-01-15"
}
```

---

## 服务状态说明

| 状态 | 说明 | 可用服务 |
|------|------|----------|
| 1 | 正常 | 购药、报销 |
| 0 | 暂停 | 冻结服务 |

---

## 知识点

### 🔹 服务状态变更
```javascript
// 暂停服务
api.updateUserInfo({
    id: userId,
    servicestatus: '0'
});

// 恢复服务
api.updateUserInfo({
    id: userId,
    servicestatus: '1'
});
```

### 🔹 批量导入
```javascript
// 导入接口接收 FormData
const formData = new FormData();
formData.append('file', file);
api.importUserList(formData);
```
