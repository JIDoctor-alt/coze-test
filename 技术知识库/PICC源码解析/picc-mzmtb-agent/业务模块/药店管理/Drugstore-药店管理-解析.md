# 业务模块 - 药店管理 (Drugstore)

> 🎯 一句话说明：药店管理是患者在药店购药后"缴费结算"的入口，包括缴费、退费、订单查询等

---

## 这是啥？（小白版）

想象 **药店管理是药店的"收银系统"**：
- 收银台 = 缴费列表
- 小票 = 订单详情
- 退款 = 退费处理
- 库存 = 药品管理

---

## 模块组成

### 1. drugstoreChargeList.vue - 药店缴费列表
**位置**: `pages/Drugstore/drugstoreChargeList.vue`

**功能**: 查看和管理患者的药店购药缴费记录

```html
<template>
    <div class="main-box">
        <!-- 搜索条件 -->
        <searchCard
            :formObj="formObj"
            @search="search"
            @resetFields="resetFields"
            :colSpan="colSpan"
        />
        
        <!-- 缴费列表 -->
        <a-card title="缴费列表" class="card-top card-table">
            <div slot="extra">
                <a-button @click="refund">退费</a-button>
                <a-button @click="payInfo">查看详情</a-button>
            </div>
            
            <a-table
                :columns="columns.chargeList"
                :data-source="list"
                :pagination="pagination"
                :loading="loading"
                :row-selection="rowSelection"
            >
                <!-- 缴费金额 -->
                <div slot="totalmoney" slot-scope="totalmoney, record">
                    ￥{{ record.totalmoney }}
                </div>
                
                <!-- 社保卡号脱敏 -->
                <div slot="cardno" slot-scope="cardno, record">
                    ************{{ editmoney(record.cardno) }}
                </div>
                
                <!-- 订单类型 -->
                <div slot="ordertype" slot-scope="ordertype, record">
                    {{ record.ordertype | filterType("ordertype") }}
                </div>
                
                <!-- 状态 -->
                <div slot="status" slot-scope="status, record">
                    {{ record.status | filterBindCardStatus("paymentStatus") }}
                </div>
            </a-table>
        </a-card>
        
        <!-- 详情弹窗 -->
        <paymentDetails
            ref="paymentDetails"
            :userFormObj="userFormObj"
            pharmacy="pharmacy"
        />
    </div>
</template>

<script>
import searchCard from "@/components/searchCard/index";
import paymentDetails from "../Payment/paymentDetails";
import tableMixins from "@/utils/tableMixins";
import {
    getVipDrugstoreOrder,      // 获取缴费订单
    refundVipDrugstoreOrder,   // 退费
} from "@/api/apiPaymentMange.js";

export default {
    components: {
        searchCard,
        paymentDetails
    },
    mixins: [tableMixins],
    data() {
        return {
            // 搜索条件
            formObj: {
                eCardNo: "",           // 社保卡号
                orderno: "",           // 订单号
                paymentStatus: "",     // 缴费状态
                orderstart: "",        // 订单开始时间
                endoforder: ""         // 订单结束时间
            },
            
            // 表格
            columns: [],
            list: [],
            loading: false,
            
            // 分页
            pagination: {
                pageSize: 10,
                current: 1,
                total: 0
            },
            
            // 选中行
            selectedRows: [],
            rowSelection: {
                type: "radio",
                selectedRowKeys: []
            },
            
            // 详情数据
            userFormObj: {}
        }
    },
    created() {
        this.initPage();
    },
    methods: {
        // 1. 加载缴费列表
        initPage(extraparams) {
            this.loading = true;
            let params = {
                ...this.searchParam,
                pageNum: this.pagination.current,
                pageSize: this.pagination.pageSize
            };
            
            getVipDrugstoreOrder(params).then(res => {
                if (res.status === 0) {
                    this.list = res.data.list || [];
                    this.pagination.total = res.data.total || 0;
                }
            }).finally(() => {
                this.loading = false;
            });
        },
        
        // 2. 查询
        search(params) {
            this.searchParam = params;
            this.pagination.current = 1;
            this.initPage(params);
        },
        
        // 3. 查看详情
        payInfo() {
            if (!this.selectedRows || this.selectedRows.length === 0) {
                this.$message.warning('请选择一条记录');
                return;
            }
            this.$refs.paymentDetails.show(this.selectedRows);
        },
        
        // 4. 退费
        refund() {
            if (!this.selectedRows || this.selectedRows.length === 0) {
                this.$message.warning('请选择一条记录');
                return;
            }
            
            this.$confirm({
                title: '确认退费',
                content: `确定对订单 ${this.selectedRows.orderno} 进行退费吗？`,
                onOk() {
                    return refundVipDrugstoreOrder({
                        orderId: this.selectedRows.id
                    }).then(res => {
                        if (res.status === 0) {
                            this.$message.success('退费成功');
                            this.initPage();
                        }
                    });
                }
            });
        },
        
        // 5. 社保卡号脱敏
        editmoney(cardno) {
            return cardno ? cardno.slice(12) : '';  // 只显示后4位
        }
    }
}
</script>
```

---

### 2. drugstoreChargeAdd.vue - 药店缴费新增
**位置**: `pages/Drugstore/drugstoreChargeAdd.vue`

**功能**: 新增药店购药缴费记录

---

### 3. drugstoreChargeAddNew.vue - 药店缴费新增(新版)
**位置**: `pages/Drugstore/drugstoreChargeAddNew.vue`

**功能**: 新版缴费新增界面

---

### 4. productList.vue - 药品列表
**位置**: `pages/Drugstore/productList.vue`

**功能**: 管理药店药品目录

---

## 订单状态说明

| 状态码 | 说明 | 可操作 |
|--------|------|--------|
| 0 | 待支付 | 支付 |
| 1 | 已支付 | 退费 |
| 2 | 已退费 | - |
| 3 | 退费失败 | 重试 |

---

## 缴费流程图

```
┌─────────────────────────────────────────────────────────────┐
│                      药店缴费流程                              │
└─────────────────────────────────────────────────────────────┘

    患者到药店购药
         ↓
    店员扫描社保卡
         ↓
    查询患者信息
         ↓
    选择药品
         ↓
    计算费用
         ↓
    ┌─────────┴─────────┐
    ↓                   ↓
  医保支付            自费支付
    ↓                   ↓
    └─────────┬─────────┘
              ↓
         打印小票
              ↓
         缴费完成
```

---

## 知识点

### 🔹 社保卡号脱敏
```javascript
// 只显示后4位
editmoney(cardno) {
    return cardno ? cardno.slice(12) : '';
    // 6103001234567890123 → 90123
}
```

### 🔹 退费规则
- 已缴费未取药 → 可全额退费
- 已取部分药品 → 按实际未取数量退费
- 已打印发票 → 需要先作废发票
