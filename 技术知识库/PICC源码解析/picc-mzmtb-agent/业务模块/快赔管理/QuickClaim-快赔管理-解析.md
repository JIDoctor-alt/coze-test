# 业务模块 - 快赔管理 (QuickClaim)

> 🎯 一句话说明：快赔管理是患者申请"快速理赔"的入口，包括申请、确认、授权等全流程

---

## 这是啥？（小白版）

想象 **快赔管理是医院的"快速报销通道"**：
- 传统报销 = 排队等待
- 快速理赔 = 绿色通道
- 系统审核 = AI自动判断
- 授权确认 = 领导签字

---

## 模块组成

### 1. quickClaimApply.vue - 快速理赔申请确认
**位置**: `pages/QuickClaim/quickClaimApply.vue`

**功能**: 审核人员确认患者提交的快速理赔申请

```html
<template>
    <div class="main-box">
        <!-- 搜索条件 -->
        <searchCard :formObj="formObj" @search="search" />
        
        <!-- 申请列表 -->
        <a-table :columns="columns" :data-source="data">
            <!-- 申请金额 -->
            <div slot="claimAmount" slot-scope="amount">
                ¥ {{ amount | qianfenwei }}
            </div>
            
            <!-- 申请状态 -->
            <div slot="status" slot-scope="status, record">
                {{ status | filterClaimStatus }}
            </div>
            
            <!-- 操作 -->
            <span slot="action" slot-scope="record">
                <a @click="approve(record)">确认</a>
                <a @click="reject(record)">拒绝</a>
            </span>
        </a-table>
    </div>
</template>

<script>
import api from "@/api/apiQuickClaimApply";

export default {
    data() {
        return {
            formObj: {
                name: "",
                idcard: "",
                claimBeginFrom: "",
                claimBeginTo: "",
                status: ""
            },
            data: [],
            columns: [
                { title: '申请人', dataIndex: 'name' },
                { title: '身份证', dataIndex: 'idcard' },
                { title: '理赔金额', dataIndex: 'claimAmount', scopedSlots: { customRender: 'claimAmount' } },
                { title: '申请时间', dataIndex: 'claimDate' },
                { title: '状态', dataIndex: 'status', scopedSlots: { customRender: 'status' } },
                { title: '操作', key: 'action', scopedSlots: { customRender: 'action' } }
            ]
        }
    },
    methods: {
        // 确认理赔
        approve(row) {
            api.confirmClaim({ id: row.id, status: 'pass' }).then(res => {
                if (res.status === 0) {
                    this.$message.success('确认成功');
                    this.initPage();
                }
            });
        },
        
        // 拒绝理赔
        reject(row) {
            api.rejectClaim({ id: row.id, status: 'reject', reason: '' });
        }
    }
}
</script>
```

---

### 2. quickClaimAuthorize.vue - 快速理赔授权
**位置**: `pages/QuickClaim/quickClaimAuthorize.vue`

**功能**: 授权人员对已确认的理赔进行二次授权

```html
<template>
    <div class="main-box">
        <searchCard :formObj="formObj" @search="search" />
        
        <a-table :columns="columns" :data-source="data">
            <!-- 大额提示 -->
            <div slot="amount" slot-scope="amount, record">
                <span v-if="amount > 5000" style="color: red;">⚠️</span>
                {{ amount | qianfenwei }}
            </div>
            
            <!-- 操作 -->
            <span slot="action" slot-scope="record">
                <a @click="authorize(record)">授权</a>
                <a @click="viewDetail(record)">详情</a>
            </span>
        </a-table>
    </div>
</template>

<script>
import api from "@/api/apiQuickClaimAuthorize";

export default {
    methods: {
        // 授权
        authorize(row) {
            // 大于5000需要主管授权
            if (row.claimAmount > 5000) {
                this.$confirm({
                    title: '大额理赔授权',
                    content: `该理赔金额为 ¥${row.claimAmount}，是否确认授权？`,
                    onOk() {
                        return api.authorize({ id: row.id, authorized: true });
                    }
                });
            } else {
                api.authorize({ id: row.id, authorized: true }).then(res => {
                    if (res.status === 0) {
                        this.$message.success('授权成功');
                        this.initPage();
                    }
                });
            }
        }
    }
}
</script>
```

---

### 3. Claims.vue - 理赔申请管理
**位置**: `pages/QuickClaim/Claims.vue`

**功能**: 管理和查看所有理赔申请记录

---

### 4. QuickClaim.vue - 快速理赔申请
**位置**: `pages/QuickClaim/QuickClaim.vue`

**功能**: 患者端发起理赔申请

---

## 快赔流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                       快赔管理流程                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────┐
│  提交申请    │ ← 患者发起
└──────┬──────┘
       ↓
┌─────────────────┐
│  申请确认      │ ← 审核人员审核
│ quickClaimApply │   确认材料真实性
└──────┬──────────┘
       ↓
       ├─────────────┐
       ↓             ↓
  材料无误       材料有问题
       ↓             ↓
┌──────┴──────────┐
│  授权确认       │ ← 大额需主管授权
│ quickClaimAuthorize │
└──────┬──────────┘
       ↓
┌──────┴──────────┐
│   理赔完成      │ ← 财务打款
└─────────────────┘
```

---

## 理赔状态

| 状态码 | 说明 | 操作 |
|--------|------|------|
| 0 | 待确认 | 确认/拒绝 |
| 1 | 已确认 | 授权 |
| 2 | 已授权 | 等待打款 |
| 3 | 已打款 | 完成 |
| 4 | 已拒绝 | 查看原因 |
| 5 | 已取消 | - |

---

## 知识点

### 🔹 大额理赔阈值
```javascript
// 金额大于5000需要额外授权
if (row.claimAmount > 5000) {
    // 显示警告
    // 需要二次确认
}
```

### 🔹 金额格式化
```javascript
// 显示带千分符的金额
{{ amount | qianfenwei }}
// 10000 → 10,000.00
```
