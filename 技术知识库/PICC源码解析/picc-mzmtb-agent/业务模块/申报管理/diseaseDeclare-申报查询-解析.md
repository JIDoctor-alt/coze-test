# 业务模块 - 慢病申报查询 (diseaseDeclare.vue)

> 🎯 一句话说明：这是患者提交慢病申报后，管理人员查询和审核的"入口页面"

---

## 这是啥？（小白版）

想象 **申报查询是医院的"病历档案室"**：
- 档案柜 = 数据库
- 档案袋 = 每条申报记录
- 档案管理员 = 查询系统
- 可以按姓名、身份证、日期等条件查找档案

---

## 核心代码解析

### template 部分

```html
<template>
    <div class="main-box">
        <!-- 1. 搜索条件区域 -->
        <searchCard
            :formObj="formObj"
            :bjUnitList="unitList"              <!-- 宝鸡定点单位 -->
            :bjPersontypeList="persontypeList"  <!-- 人员类型 -->
            @search="search"
            @resetFields="resetFields"
        />
        
        <!-- 2. 数据表格区域 -->
        <a-card class="card-top card-table">
            <div slot="title">
                <img src="@/assets/images/person_icon.png">申报列表
            </div>
            <div slot="extra">
                <a-button @click="changeMobile">修改手机号</a-button>
                <a-button @click="exportFun">导出EXCEL</a-button>
            </div>
            
            <!-- 表格主体 -->
            <a-table
                :columns="columns"           <!-- 表头配置 -->
                :data-source="data"           <!-- 数据源 -->
                :pagination="pagination"      <!-- 分页配置 -->
                :loading="loading"             <!-- 加载状态 -->
                :row-selection="rowSelection"  <!-- 行选择 -->
                :rowKey="record => record.id"  <!-- 行唯一标识 -->
            >
                <!-- 自定义列显示 -->
                <div slot="icdkind" slot-scope="icdkind, record">
                    {{ record.icdkind | filterIcdkind }}
                </div>
                <div slot="specialflag1" slot-scope="specialflag1, record">
                    {{ record.specialflag1 | filterSpecialflag1 }}
                </div>
                <div slot="mobile" slot-scope="mobile, record">
                    {{ record.mobile | filterMobile }}  <!-- 手机号脱敏 -->
                </div>
                
                <!-- 操作列 -->
                <span slot="modifier" slot-scope="modifier, record">
                    <a @click="showMaterial(record)">资料</a>
                    <a-divider v-if="record.physicalstatus == '1'" />
                    <a @click="showReport(record)">体检报告</a>
                </span>
            </a-table>
        </a-card>
        
        <!-- 3. 弹窗区域 -->
        <!-- 体检报告弹窗 -->
        <el-container :visible="visible" title="体检报告" width="85%">
            <img v-for="item in reportList" :src="item" />
        </el-container>
        
        <!-- 申请资料弹窗 -->
        <el-container :visible="visibleMaterial" title="申请资料" width="60%">
            <applyMaterial :row="selectObj" />
        </el-container>
        
        <!-- 修改手机号弹窗 -->
        <changeMoblie :row="selectedRows" @refreshFnUpdate="refreshFn" />
    </div>
</template>
```

### script 部分

```javascript
import searchCard from "@/components/searchCard/index";
import api from "@/api/apiDiseaseDeclare";
import tableCon from "./config/config";      // 表格列配置
import applyMaterial from "./components/applyMaterial";  // 申请资料组件
import changeMoblie from './components/changeMoblie';    // 修改手机号组件
import tableMixins from "@/utils/tableMixins";

export default {
    components: {
        searchCard,
        applyMaterial,
        changeMoblie
    },
    mixins: [tableMixins],
    data() {
        return {
            // 查询表单
            formObj: {
                name: "",              // 姓名
                idcard: "",            // 身份证
                mobile: "",            // 手机号
                declareStatusQueryBJ: "",  // 申报状态
                declareBeginFrom: "",  // 申报时间起
                declareBeginTo: "",    // 申报时间止
                persontype: "",        // 人员类型
                ybArea: ""            // 医保区划
            },
            
            // 表格相关
            columns: [],              // 表头配置
            data: [],                 // 数据列表
            loading: false,          // 加载状态
            
            // 分页
            pagination: {
                current: 1,
                pageSize: 10,
                total: 0,
                showTotal: total => `共 ${total} 条`
            },
            
            // 弹窗控制
            visible: false,           // 体检报告弹窗
            visibleMaterial: false,  // 申请资料弹窗
            
            // 选中的行
            selectedRows: null,
            selectObj: null,
            reportList: [],           // 体检报告图片列表
            
            // 其他
            unitList: [],             // 单位列表
            persontypeList: [],       // 人员类型列表
            exportLoading: false,     // 导出loading
        }
    },
    created() {
        this.initPage();      // 初始化加载
        this.getUnitList();   // 获取单位列表
        this.getPersontypeList();  // 获取人员类型列表
    },
    methods: {
        // 1. 初始化页面数据
        initPage() {
            this.loading = true;
            api.queryDeclareList({
                ...this.searchParams,  // 合并查询参数
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
        
        // 3. 重置
        resetFields() {
            this.searchParams = {};
            this.pagination.current = 1;
            this.initPage();
        },
        
        // 4. 查看申请资料
        showMaterial(row) {
            this.selectObj = row;
            this.visibleMaterial = true;
        },
        
        // 5. 查看体检报告
        showReport(row) {
            this.selectObj = row;
            api.getReportPicture({ declareId: row.id }).then(res => {
                if (res.status === 0) {
                    this.reportList = res.data || [];
                    this.visible = true;
                }
            });
        },
        
        // 6. 修改手机号
        changeMobile() {
            if (!this.selectedRows) {
                this.$message.warning('请选择一条记录');
                return;
            }
            this.$refs.moblieVisable.open();
        },
        
        // 7. 导出Excel
        exportFun() {
            this.exportLoading = true;
            api.exportDeclare(this.searchParams).then(res => {
                // 文件下载处理
                this.$downloadFileByBase64(res, '申报列表.xls');
            }).finally(() => {
                this.exportLoading = false;
            });
        },
        
        // 8. 获取单位列表
        getUnitList() {
            api.getCityList().then(res => {
                if (res.status === 0) {
                    this.unitList = res.data || [];
                }
            });
        }
    },
    // 过滤器：人员类型
    filters: {
        filterType(value, type) {
            // 根据类型转换显示值
        }
    }
}
```

---

## 数据结构

### 申报列表数据 (data)
```javascript
{
    id: "申报ID",
    name: "张三",                    // 姓名
    idcard: "610302199001011234",   // 身份证号
    mobile: "13800000000",          // 手机号
    sex: "1",                       // 性别 1男 2女
    persontype: "1",               // 人员类型 1职工 2居民
    icdkind: "M",                  // 疾病大类
    icdcode: "I10",                // 疾病编码
    icdname: "高血压",              // 疾病名称
    declareStatus: "1",            // 申报状态
    physicalstatus: "1",          // 体检状态 0未分配 1已分配
    expertstatus: "0",            // 专家分配状态
    declaredate: "2024-01-15",    // 申报日期
    bjUnitName: "宝鸡市人民医院",   // 定点单位
    approvalnote: "符合申报条件"    // 审批备注
}
```

---

## 知识点

### 🔹 表格列配置 (tableCon)
```javascript
const columns = [
    { title: '姓名', dataIndex: 'name', width: 100 },
    { title: '身份证', dataIndex: 'idcard', width: 180 },
    { title: '疾病名称', dataIndex: 'icdname', width: 150 },
    { title: '申报日期', dataIndex: 'declaredate', width: 120 },
    { title: '操作', key: 'modifier', width: 150 }
];
```

### 🔹 手机号脱敏过滤器
```javascript
filterMobile(phone) {
    return phone ? phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : '';
    // 13800001234 → 138****1234
}
```

### 🔹 申报状态枚举
| 值 | 说明 |
|----|------|
| 0 | 待提交 |
| 1 | 初审中 |
| 2 | 体检中 |
| 3 | 专家审核中 |
| 4 | 复审中 |
| 5 | 通过 |
| 6 | 不通过 |

### 🔹 分页参数
```javascript
{
    pageNum: 1,    // 当前页码
    pageSize: 10,  // 每页条数
    total: 100    // 总条数
}
```
