# 业务模块 - 支付管理 (Payment)

> 🎯 一句话说明：支付管理是患者线下购药后"报销结算"的入口，包括支付、退款、对账等功能

---

## 这是啥？（小白版）

想象 **支付管理是医院的"收费窗口"**：
- 缴费 = 线下支付确认
- 退费 = 退款处理
- 对账 = 账目核对
- 查询 = 交易记录查看

---

## 模块组成

### 1. paymentManagement.vue - 支付管理
**位置**: `pages/Payment/paymentManagement.vue`

**功能**: 查询和管理患者的支付记录

```html
<template>
    <div class="main-box">
        <!-- 搜索条件 -->
        <searchCard :formObj="formObj" @search="search" />
        
        <!-- 支付列表 -->
        <a-card class="card-top card-table">
            <div slot="extra">
                <a-button @click="exportData">导出对账</a-button>
            </div>
            
            <a-table
                :columns="columns"
                :data-source="data"
                :pagination="pagination"
                :loading="loading"
            >
                <!-- 支付金额 -->
                <div slot="payAmount" slot-scope="payAmount">
                    ¥ {{ payAmount | qianfenwei }}
                </div>
                
                <!-- 支付状态 -->
                <div slot="payStatus" slot-scope="payStatus, record">
                    <a-tag :color="getStatusColor(payStatus)">
                        {{ getStatusText(payStatus) }}
                    </a-tag>
                </div>
                
                <!-- 操作 -->
                <span slot="action" slot-scope="record">
                    <a @click="viewDetail(record)">详情</a>
                    <a-divider type="vertical" />
                    <a @click="refund(record)" v-if="record.payStatus === '1'">
                        退款
                    </a>
                </span>
            </a-table>
        </a-card>
        
        <!-- 详情弹窗 -->
        <el-container :visible="detailVisible" title="支付详情" width="60%">
            <paymentDetails :paymentId="paymentId" />
        </el-container>
        
        <!-- 退款弹窗 -->
        <el-container :visible="refundVisible" title="退款" @ok="confirmRefund">
            <a-form>
                <a-form-item label="退款金额">
                    <a-input-number 
                        v-model="refundAmount" 
                        :min="0" 
                        :max="maxRefundAmount"
                        style="width: 100%"
                    />
                </a-form-item>
                <a-form-item label="退款原因">
                    <a-textarea v-model="refundReason" :rows="4" />
                </a-form-item>
            </a-form>
        </el-container>
    </div>
</template>

<script>
import api from "@/api/apiPaymentManagement";
import paymentDetails from "./paymentDetails.vue";

export default {
    components: {
        paymentDetails
    },
    data() {
        return {
            formObj: {
                name: "",
                idcard: "",
                payBeginFrom: "",
                payBeginTo: "",
                payStatus: ""
            },
            columns: [
                { title: '订单号', dataIndex: 'orderNo', width: 150 },
                { title: '患者姓名', dataIndex: 'patientName' },
                { title: '身份证', dataIndex: 'idcard' },
                { title: '药品名称', dataIndex: 'drugName' },
                { title: '支付金额', dataIndex: 'payAmount', scopedSlots: { customRender: 'payAmount' } },
                { title: '支付时间', dataIndex: 'payTime' },
                { title: '状态', dataIndex: 'payStatus', scopedSlots: { customRender: 'payStatus' } },
                { title: '操作', key: 'action', scopedSlots: { customRender: 'action' } }
            ],
            data: [],
            pagination: { current: 1, pageSize: 10, total: 0 },
            loading: false,
            
            // 弹窗
            detailVisible: false,
            refundVisible: false,
            paymentId: "",
            refundAmount: 0,
            refundReason: "",
            maxRefundAmount: 0
        }
    },
    methods: {
        // 加载支付列表
        initPage() {
            this.loading = true;
            api.getPaymentList({
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
        
        // 查看详情
        viewDetail(record) {
            this.paymentId = record.id;
            this.detailVisible = true;
        },
        
        // 申请退款
        refund(record) {
            this.paymentId = record.id;
            this.refundAmount = record.payAmount;
            this.maxRefundAmount = record.payAmount;
            this.refundReason = "";
            this.refundVisible = true;
        },
        
        // 确认退款
        confirmRefund() {
            api.refund({
                id: this.paymentId,
                amount: this.refundAmount,
                reason: this.refundReason
            }).then(res => {
                if (res.status === 0) {
                    this.$message.success('退款申请已提交');
                    this.refundVisible = false;
                    this.initPage();
                }
            });
        },
        
        // 获取状态颜色
        getStatusColor(status) {
            const colorMap = {
                '0': 'orange',  // 待支付
                '1': 'green',   // 已支付
                '2': 'blue',    // 已退款
                '3': 'red'      // 退款失败
            };
            return colorMap[status] || 'default';
        },
        
        // 获取状态文字
        getStatusText(status) {
            const textMap = {
                '0': '待支付',
                '1': '已支付',
                '2': '已退款',
                '3': '退款失败'
            };
            return textMap[status] || '未知';
        }
    }
}
</script>
```

---

### 2. Offlinepayment.vue - 线下支付
**位置**: `pages/Payment/Offlinepayment.vue`

**功能**: 录入和管理线下购药支付记录

---

### 3. dataSummary.vue - 数据汇总
**位置**: `pages/Payment/dataSummary.vue`

**功能**: 查看支付数据的统计汇总

```javascript
// 数据汇总典型结构
{
    totalOrders: 1000,         // 总订单数
    totalAmount: 500000,       // 总金额
    successOrders: 980,        // 成功订单
    successAmount: 490000,    // 成功金额
    refundOrders: 20,         // 退款订单
    refundAmount: 10000,      // 退款金额
    dateRange: ['2024-01-01', '2024-01-31']
}
```

---

## 支付状态流转

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ 待支付  │ →→ │ 已支付  │ ←← │ 退款中  │ ←← │ 已退款  │
│ (0)    │    │ (1)    │    │ (2)    │    │ (3)    │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
     ↓
  超时取消
```

---

## 退款规则

| 条件 | 说明 |
|------|------|
| 全额退款 | 支付后未取药，可全额退款 |
| 部分退款 | 已取部分药品，按实际金额退款 |
| 不可退款 | 超过退款期限（30天） |

---

## 知识点

### 🔹 金额精度处理
```javascript
// 金额以"分"存储，转换时除以100
const displayAmount = record.amount / 100;

// 输入时乘以100
const saveAmount = inputAmount * 100;
```

### 🔹 对账导出
```javascript
// 导出指定时间范围内的所有交易记录
api.exportPaymentData({
    beginDate: '2024-01-01',
    endDate: '2024-01-31'
}).then(res => {
    this.$downloadFileByBase64(res, '支付对账_2024年1月.xlsx');
});
```
