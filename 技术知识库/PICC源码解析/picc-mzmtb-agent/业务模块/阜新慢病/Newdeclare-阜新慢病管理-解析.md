# 业务模块 - 阜新慢病管理 (Newdeclare)

> 🎯 一句话说明：阜新地区的慢病管理模块，与宝鸡模块类似但有独立的流程和接口

---

## 这是啥？（小白版）

想象 **阜新慢病管理是另一个城市的"慢病管理系统"**：
- 独立的机构编码（flag=1）
- 独立的业务流程
- 共享部分代码，按需定制

---

## 模块组成

### 1. newDeclareInport.vue - 慢病申报导入
**位置**: `pages/Newdeclare/newDeclareInport.vue`

**功能**: 批量导入阜新地区的慢病申报数据

```html
<template>
    <div class="main-box">
        <a-card class="card-top">
            <div slot="title">
                <img src="@/assets/images/person_icon.png">慢病申报导入
            </div>
            
            <!-- 导入说明 -->
            <a-alert
                message="导入说明"
                description="请下载模板，按要求填写后上传。上传的Excel文件大小不能超过5MB。"
                type="info"
                show-icon
                style="margin-bottom: 20px"
            />
            
            <!-- 下载模板 -->
            <a-button @click="downloadTemplate">
                <a-icon type="download" /> 下载导入模板
            </a-button>
            
            <!-- 上传 -->
            <a-upload
                :before-upload="beforeUpload"
                :custom-request="handleUpload"
                accept=".xls,.xlsx"
                style="margin: 20px 0"
            >
                <a-button>
                    <a-icon type="upload" /> 选择文件
                </a-button>
            </a-upload>
            
            <!-- 导入结果 -->
            <a-table
                v-if="importResults.length"
                :columns="resultColumns"
                :data-source="importResults"
            >
                <div slot="status" slot-scope="status">
                    <a-tag :color="status === '成功' ? 'green' : 'red'">
                        {{ status }}
                    </a-tag>
                </div>
            </a-table>
        </a-card>
    </div>
</template>

<script>
import api from "@/api/apiNewDeclare";

export default {
    data() {
        return {
            importResults: [],
            resultColumns: [
                { title: '行号', dataIndex: 'rowNum' },
                { title: '姓名', dataIndex: 'name' },
                { title: '身份证', dataIndex: 'idcard' },
                { title: '状态', dataIndex: 'status', scopedSlots: { customRender: 'status' } },
                { title: '原因', dataIndex: 'reason' }
            ]
        }
    },
    methods: {
        // 下载模板
        downloadTemplate() {
            api.downloadTemplate().then(res => {
                this.$downloadFileByBase64(res, '阜新慢病申报导入模板.xls');
            });
        },
        
        // 上传前验证
        beforeUpload(file) {
            const isExcel = file.type === 'application/vnd.ms-excel' ||
                           file.name.endsWith('.xlsx');
            if (!isExcel) {
                this.$message.error('只能上传 Excel 文件！');
            }
            
            const isLt5M = file.size / 1024 / 1024 < 5;
            if (!isLt5M) {
                this.$message.error('文件大小不能超过 5MB！');
            }
            
            return isExcel && isLt5M;
        },
        
        // 上传
        handleUpload(param) {
            const formData = new FormData();
            formData.append('file', param.file);
            
            api.importDeclare(formData).then(res => {
                if (res.status === 0) {
                    this.importResults = res.data.results || [];
                    this.$message.success(`导入完成，成功 ${res.data.successCount} 条，失败 ${res.data.failCount} 条`);
                }
            });
        }
    }
}
</script>
```

---

## 阜新业务流程

阜新地区的慢病业务流程与宝鸡类似，但有以下区别：

```
┌─────────────────────────────────────────────────────────────┐
│                   阜新慢病申报流程                           │
└─────────────────────────────────────────────────────────────┘

    申报导入（批量）
         ↓
    ┌────┴────┐
    ↓         ↓
  自动审核   人工审核
    ↓         ↓
    └────┬────┘
         ↓
    初审管理
         ↓
    体检分配
         ↓
    专家分配
         ↓
    复审管理
         ↓
     备案通过
```

---

## 阜新与宝鸡对比

| 对比项 | 宝鸡 (flag=0) | 阜新 (flag=1) |
|--------|---------------|---------------|
| 入口方式 | 小程序申报 + 线下 | 批量导入为主 |
| 初审 | 人工审核为主 | 可结合AI |
| 体检 | 必须体检 | 可选 |
| 专家分配 | 手动+自动 | 手动 |
| 复审 | 有 | 有 |

---

## 关键参数

### 接口调用时传递 flag 参数

```javascript
// 查询列表时
api.queryList({
    flag: "1",  // 0=宝鸡 1=阜新
    name: "张三"
})

// 提交审核时
api.submitAudit({
    flag: "1",
    id: "申报ID"
})
```

---

## 阜新专有页面

| 页面 | 功能 | 路由 |
|------|------|------|
| newDeclareInport | 申报导入 | /newDeclareInport |
| newDeclareManage | 申报管理 | /newDeclareManage |
| newAuditManage | 初审管理 | /newAuditManage |
| newPhysicalAssignment | 体检分配 | /newPhysicalAssignment |
| newExpertAssignment | 专家分配 | /newExpertAssignment |
| newDoctorManage | 医生管理 | /newDoctorManage |
| newPhysicalManage | 体检站点 | /newPhysicalManage |
| newReexamine | 复审管理 | /newReexamine |
