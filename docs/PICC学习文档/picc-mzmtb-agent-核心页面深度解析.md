# PICC门诊慢特病前端项目（picc-mzmtb-agent）核心页面深度解析

> **文档版本**: v1.0  
> **解析对象**: picc-mzmtb-agent  
> **Vue文件数量**: 542个  
> **地市页面模块**: 23个

---

## 📖 阅读指南（小白必读）

### 本文档使用的"人话"比喻

| 技术术语 | 人话比喻 | 解释 |
|---------|---------|------|
| **页面 (Page)** | "房间" | 用户进入后看到的完整屏幕 |
| **组件 (Component)** | "家具" | 房间里的各种物件，如桌子、椅子 |
| **数据绑定** | "遥控器和电视" | 改遥控器，电视画面自动变 |
| **事件处理** | "按钮传感器" | 按下按钮，触发对应动作 |
| **生命周期** | "人的一生" | 组件也有创建→成长→销毁的过程 |
| **API调用** | "外卖下单" | 页面"点餐"，后端"做菜送餐" |
| **Vuex/Store** | "中控室" | 全局数据中心，所有房间共享 |
| **路由 (Router)** | "走廊指引" | 告诉你该去哪个房间 |

---

## 📊 第一章：项目整体架构

### 1.1 项目结构速览

```
picc-mzmtb-agent/
├── src/
│   ├── pages/                    # 📦 所有"房间"（页面）
│   │   ├── Home.vue              # 🏠 主框架（带菜单和标签栏）
│   │   ├── index.vue             # 🔝 顶部导航栏
│   │   ├── ChronicDis/           # 🏥 慢病管理通用模块
│   │   ├── YAChronicDis/         # 🏥 延安慢病管理（最大模块，39个文件）
│   │   ├── Newdeclare/           # 📝 新申报管理
│   │   ├── Declare/              # 📝 申报管理
│   │   ├── Drugstore/            # 💊 药店管理
│   │   ├── Payment/              # 💰 支付管理
│   │   ├── QuickClaim/           # ⚡ 快赔管理
│   │   ├── SystemView/           # ⚙️ 系统管理
│   │   ├── Hospital/             # 🏩 医院管理
│   │   └── [其他地市模块]...     # 各地市定制模块
│   │
│   ├── components/               # 🪑 公共"家具"（组件）
│   │   ├── loginMb/              # 🔐 登录相关组件
│   │   ├── menuList/             # 📋 菜单组件
│   │   └── ...
│   │
│   ├── api/                      # 🍔 外卖菜单（API接口）
│   │   ├── apiLoginMb.js         # 登录接口
│   │   ├── apiDiseaseDeclare.js  # 慢病申报接口
│   │   ├── apiPaymentMange.js    # 支付管理接口
│   │   └── ...（74个接口文件）
│   │
│   ├── router/                   # 🗺️ 走廊地图（路由配置）
│   │   ├── index.js              # 路由总览
│   │   └── childrenRoutes.js    # 子路由（100+个页面）
│   │
│   └── store/                    # 🏢 中控室（Vuex状态管理）
│       ├── index.js              # 状态中心
│       └── modules/              # 分区管理
│
└── ...
```

### 1.2 23个地市模块一览

| 模块名 | 说明 | 文件数 |
|--------|------|--------|
| ChronicDis | 慢病管理通用（宝鸡） | 较多 |
| YAChronicDis | 延安慢病管理 | **39个（最大）** |
| NewChronicDis | 新慢病管理 | 中等 |
| DZChronicDis | DZ慢病管理 | 中等 |
| JZChronicDis | JZ慢病管理 | 中等 |
| 其他模块 | 各地市定制 | 若干 |

---

## 🔐 第二章：登录页面（loginMb）

**文件位置**: `src/components/loginMb/index.vue`

### 2.1 功能说明（人话版）

> 这就是系统"大门"，用户必须先刷脸（输账号密码+验证码）才能进入系统。

### 2.2 页面布局结构

```
┌────────────────────────────────────────────────────┐
│                    [背景图]                          │
│  ┌──────────────────────────────────────────────┐  │
│  │                   登录                         │  │
│  │  ┌────────────────────────────────────────┐   │  │
│  │  │ [👤] 用户名输入框                       │   │  │
│  │  └────────────────────────────────────────┘   │  │
│  │  ┌────────────────────────────────────────┐   │  │
│  │  │ [🔒] 密码输入框                         │   │  │
│  │  └────────────────────────────────────────┘   │  │
│  │  ┌────────────────┐  ┌──────────────────┐   │  │
│  │  │ 手机号(自动填充)│  │ [📱获取验证码]   │   │  │
│  │  └────────────────┘  └──────────────────┘   │  │
│  │  ┌────────────────────────────────────────┐   │  │
│  │  │ 验证码输入框                            │   │  │
│  │  └────────────────────────────────────────┘   │  │
│  │              [🔓 登录按钮]                    │  │
│  │                                               │  │
│  │  ┌─ 重置密码 ────────────────────────────┐   │  │
│  └──────────────────────────────────────────────┘  │
│                                                    │
│  ⚠️ 严禁处理、传输国家秘密                          │
│  中国人民健康保险股份有限公司  版权所有               │
└────────────────────────────────────────────────────┘
```

### 2.3 核心组件拆解

| 组件 | 类型 | 说明 |
|------|------|------|
| a-form | Ant Design 表单 | 登录表单容器 |
| a-input | 输入框 | 用户名、密码、手机号、验证码 |
| a-button | 按钮 | 登录、获取验证码 |
| a-modal | 弹窗 | 重置密码弹窗 |

### 2.4 数据流分析

```
用户输入账号密码
       ↓
前端验证（非空检查）
       ↓
blur事件 → 调用API获取用户手机号（自动填充）
       ↓
点击"获取验证码" → 调用 sendUserVerifCodeMb API
       ↓
用户输入验证码
       ↓
点击"登录" → 调用 loginByCaptchaMb API
       ↓
后端验证通过 → 返回 token + 用户信息
       ↓
存储到 sessionStorage
       ↓
跳转到 /home 首页
```

### 2.5 核心交互逻辑

```javascript
// 登录流程伪代码
handleSubmit() {
  // 1. 表单验证
  this.form.validateFields((err, values) => {
    if (!err) {
      // 2. 调用登录API
      api.loginByCaptchaMb({
        username: values.username,
        password: values.password,
        vcode: values.vcode,      // 验证码
        mobile: this.mobile       // 手机号
      }).then(res => {
        // 3. 登录成功，存储用户信息
        sessionStorage.setItem('logInfo', JSON.stringify(res.data));
        // 4. 跳转到首页
        this.$router.push('/home');
      })
    }
  })
}

sendCode() {
  // 1. 倒计时60秒防抖
  // 2. 调用发送验证码API
  api.sendUserVerifCodeMb({ mobile: this.mobile })
}
```

### 2.6 权限控制

- **公开访问**：无需登录即可访问
- **登录后自动跳转**：有token则直接进入首页

### 2.7 小白易懵点

| 困惑点 | 解释 |
|--------|------|
| 为什么需要验证码？ | 安全验证，防止机器登录 |
| 手机号为什么自动填充？ | 输入用户名后自动从后端获取绑定手机号 |
| sessionStorage vs localStorage？ | 前者会话级（关闭浏览器清除），后者持久化 |

---

## 🏠 第三章：首页（Home.vue）

**文件位置**: `src/pages/Home.vue`

### 3.1 功能说明（人话版）

> 这是系统的"大厅"，有导航菜单（左边的侧边栏）和多标签页展示区。用户点击菜单会在这里打开对应的"房间"。

### 3.2 页面布局结构

```
┌────────────────────────────────────────────────────────────┐
│ [系统图标]  门诊慢特病业务管理信息系统         🔔 [⚙️设置]  │
│ ──────────────────────────────────────────────────────────│
│                                                            │
│ ┌────────────┐  ┌────────────────────────────────────────┐│
│ │  [侧边菜单] │  │  [标签栏1] [标签栏2] [标签栏3] ×       ││
│ │            │  ├────────────────────────────────────────┤│
│ │ 📋 慢病管理 │  │                                        ││
│ │   └ 申报查询│  │           内容区域                       ││
│ │   └ 初审管理│  │         (router-view)                   ││
│ │            │  │                                        ││
│ │ 💊 药店管理 │  │                                        ││
│ │            │  │                                        ││
│ │ 💰 支付管理 │  │                                        ││
│ │            │  │                                        ││
│ │ ⚙️ 系统管理 │  │                                        ││
│ └────────────┘  └────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────┘
```

### 3.3 核心组件拆解

| 组件名 | 来源 | 功能说明 |
|--------|------|----------|
| Indexheader | `./index.vue` | 顶部导航栏组件 |
| MenuList | `@/components/menuList` | 左侧菜单导航 |
| Watermark | `@/components/Watermark` | 水印组件（防截图） |
| settingModal | `@/components/loginMb/settingModal` | 修改密码弹窗 |
| a-layout | Ant Design | 经典后台布局框架 |
| a-tabs | Ant Design | 标签页组件 |
| keep-alive | Vue内置 | 缓存已访问页面 |

### 3.4 数据流分析

```
┌──────────────────────────────────────────────────────────────────┐
│                         Vuex Store (中控室)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐   │
│  │ menuData    │  │ tabList     │  │ collapsed               │   │
│  │ [菜单数据]   │  │ [已开标签]   │  │ [菜单是否折叠]           │   │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
         ↓                  ↑                    ↑
    MenuList组件       a-tabs组件          点击折叠按钮
         ↓                  ↑                    ↑
    渲染菜单项      渲染标签栏             触发mutation
                                                             
路由变化 → router-view 渲染对应页面
```

### 3.5 核心交互逻辑

```javascript
// 1. 标签页切换
onChange(activeKey) {
  this.activeKey = activeKey;
  this.$router.push({ path: activeKey });
}

// 2. 关闭标签页
remove(targetKey) {
  // 从tabList中移除
  // 切换到邻近标签页
  // 如果没有标签则跳转到/home
}

// 3. 菜单折叠
collapsedChange() {
  this.$store.commit('updateCollapsed', !collapsed);
}

// 4. 退出登录
cancel() {
  api.loginOutMb({}).then(res => {
    window.sessionStorage.clear();
    this.$router.replace("/loginMb");
  })
}

// 5. 初次登录检查密码强度
created() {
  let { pdMBBj, passwordStatus: status } = this.$util.getUserInfo();
  // 弱密码或初始密码 → 强制弹出修改密码
  if (pdMBBj == 'PICChealth@2020' || status == 3) {
    this.visiblePerson = true;
  }
}
```

### 3.6 水印功能

```javascript
canShowWatermark() {
  let date = moment(new Date()).format('YYYYMMDD');
  let account = this.$util.getUserInfo().chnName;
  this.watermarkText = `${account}\n${date}`
  // 水印内容：用户名 + 日期
  // 防止用户截图泄露信息
}
```

### 3.7 权限控制

- **必须登录**：未登录用户访问直接跳转/loginMb
- **菜单权限**：后端返回的menuData决定能看到哪些菜单
- **标签页管理**：动态生成，基于路由

### 3.8 小白易懵点

| 困惑点 | 解释 |
|--------|------|
| 为什么用keep-alive？ | 避免每次切换标签都重新加载页面，提升体验 |
| tabList存在哪里？ | Vuex Store，可跨页面共享 |
| 菜单数据从哪来？ | 登录时后端返回，存到sessionStorage |
| 水印有什么用？ | 防止截屏泄露敏感信息 |

---

## 📝 第四章：慢病申报管理

**文件位置**: 
- 通用版：`src/pages/ChronicDis/diseaseDeclare.vue`
- 新版：`src/pages/Newdeclare/newDeclareManage.vue`
- 延安版：`src/pages/YAChronicDis/diseaseDeclare.vue`

### 4.1 功能说明（人话版）

> 这是"慢病患者申报记录"的查询窗口。工作人员可以查看谁申报了慢病、审核到哪一步了、需要补充什么材料。

### 4.2 页面布局结构

```
┌──────────────────────────────────────────────────────────────────┐
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ [🔍] 姓名:[____] 身份证:[____] 手机:[____] 状态:[下拉▼]      │ │
│ │        申报日期:[____] 至 [____]         [搜索] [重置]       │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ 申报列表                              [申报修改] [导出EXCEL] │   │
│ ├──────────────────────────────────────────────────────────┤   │
│ │ ○ | 姓名 | 身份证 | 手机号 | 疾病名称 | 申报状态 | 操作   │   │
│ │ ────────────────────────────────────────────────────────│   │
│ │ ● | 张三 | 6103..  | 138..  | 糖尿病    | 初审通过   |... │   │
│ │ ○ | 李四 | 6104..  | 139..  | 高血压    | 待体检     |... │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│                        共 XX 条数据  [< 1 2 3 ... >]            │
└──────────────────────────────────────────────────────────────────┘
```

### 4.3 核心组件拆解

| 组件 | 来源 | 功能 |
|------|------|------|
| searchCard | `@/components/searchCard/index` | 搜索表单卡片 |
| a-table | Ant Design | 数据表格 |
| a-modal | Ant Design | 弹窗容器 |
| applyMaterial | `./components/applyMaterial` | 申请材料展示 |
| editUserInformation | `@/components/Modal/editUserInformation` | 编辑用户信息 |
| el-container | 自定义 | 弹窗容器 |

### 4.4 数据流分析

```
┌────────────────────────────────────────────────────────────┐
│                        搜索表单                              │
│  nameOne: ""                                                │
│  idcard: ""                                                 │
│  mobile: ""                                                  │
│  declareStatusQueryOne: ""  ←─── 申报状态下拉               │
│  declareBeginFrom: ""                                       │
│  declareBeginTo: ""                                         │
└──────────────────────┬─────────────────────────────────────┘
                       ↓ 搜索
┌────────────────────────────────────────────────────────────┐
│                   API调用: queryList                         │
│  api/apiDiseaseDeclare.js → /vipMbDeclareList/queryList    │
└──────────────────────┬─────────────────────────────────────┘
                       ↓ 返回数据
┌────────────────────────────────────────────────────────────┐
│                        表格数据                              │
│  {                                                          │
│    id: "xxx",                                               │
│    name: "张三",                                            │
│    idcard: "6103...",                                       │
│    mobile: "138...",                                        │
│    declareStatus: "11",  ←─── 数字代码需翻译               │
│    icdname: "糖尿病",                                       │
│    ...                                                      │
│  }[]                                                        │
└────────────────────────────────────────────────────────────┘
```

### 4.5 核心交互逻辑

```javascript
// 1. 搜索查询
search(params) {
  this.pagination.current = 1;
  this.searchParam = params;
  this.initPage(params);
}

// 2. 初始化数据
initPage(searchObj) {
  let params = {
    name: searchObj?.nameOne,
    idcard: searchObj?.idcard,
    declareStatus: searchObj?.declareStatusQueryOne,
    pageVo: {
      pageNum: this.pagination.current,
      pageSize: this.pagination.pageSize,
    }
  };
  api.queryList(params).then(res => {
    this.data = res.data.list;
    this.pagination.total = res.data.total;
  })
}

// 3. 查看申请材料
showMaterial(record) {
  this.selectObj = record;
  this.visibleMaterial = true; // 打开弹窗
}

// 4. 分页切换
onPageChange(page, pageSize) {
  this.pagination.current = page;
  this.initPage(this.searchParam);
}
```

### 4.6 申报状态流转

```
[新建申报] → [待初审] → [初审通过/不通过]
                    ↓
              [待体检] → [体检中] → [体检完成]
                    ↓
              [待专家鉴定] → [鉴定通过/不通过]
                    ↓
              [已完成] / [已拒绝]
```

### 4.7 权限控制

| 角色 | 权限 |
|------|------|
| 普通用户 | 仅查看自己申报记录 |
| 审核人员 | 查看所有，可操作审核 |
| 管理员 | 全权限 |

### 4.8 小白易懵点

| 困惑点 | 解释 |
|--------|------|
| declareStatus为什么是数字？ | 11=初审通过，3=待体检...需要字典翻译 |
| 为什么用applyMaterial组件？ | 展示多张材料图片，用轮播或网格 |
| 体检报告怎么查？ | record.physicalstatus=='1' 时显示"体检报告"链接 |

---

## 💊 第五章：药店管理

**文件位置**: `src/pages/Drugstore/`

### 5.1 功能说明（人话版）

> 药店工作人员用来管理慢病患者买药、缴费、退费的系统。

### 5.2 核心页面

| 页面 | 功能 |
|------|------|
| drugstoreChargeList.vue | 缴费列表（查订单、退费） |
| drugstoreChargeAdd.vue | 新增缴费 |
| productList.vue | 产品列表 |

### 5.3 页面布局

```
┌──────────────────────────────────────────────────────────────────┐
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ 卡号:[____] 订单号:[____] 状态:[下拉▼]  日期:[____至____]    │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ 缴费列表                                  [退费] [查看详情] │   │
│ ├──────────────────────────────────────────────────────────┤   │
│ │ ○ | 订单日期 | 订单号 | 总金额 | 卡号       | 状态 | ... │   │
│ │ ● | 2024-01 | OD123| ¥150.00| *********1234| 已支付| ... │   │
│ └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### 5.4 核心API调用

```javascript
// src/api/apiPaymentMange.js
import {
  getVipDrugstoreOrder,      // 获取订单详情
  queryAccountInfoForYD,     // 分页查询订单列表
  refundVipDrugstoreOrder,   // 退费操作
} from "@/api/apiPaymentMange.js";

// 查询订单列表
queryAccountInfoForYD({
  pageNum: 1,
  pageSize: 10,
  eCardNo: "xxx",        // 电子卡号
  orderno: "xxx",         // 订单号
  status: "1"             // 支付状态
})

// 退费
refundVipDrugstoreOrder({
  id: "orderId",          // 订单ID
  reason: "xxx"           // 退费原因
})
```

### 5.5 核心交互

```javascript
// 查看详情
payInfo() {
  if (this.selectedRows.length == 0) {
    this.selectConfirm(); // 提示选择记录
  } else {
    this.$refs.paymentDetails.show(this.selectedRows);
  }
}

// 退费
refund() {
  if (this.selectedRows.length == 0) {
    this.selectConfirm();
  } else if (this.selectedRows.status !== '1') {
    this.$warning({ title: "只有已支付的订单才能退费！" });
  } else {
    // 确认退费 → 调用 refundVipDrugstoreOrder API
  }
}
```

---

## 💰 第六章：支付管理

**文件位置**: `src/pages/Payment/`

### 6.1 功能说明（人话版）

> 管理"一卡通"患者的门诊缴费、支付、退费。

### 6.2 核心页面

| 页面 | 功能 |
|------|------|
| paymentManagement.vue | 缴费管理主页面 |
| paymentDetails.vue | 缴费详情弹窗 |
| Refundmanagement.vue | 退费管理 |
| dataSummary.vue | 数据汇总 |
| detailsInquiry.vue | 明细查询 |

### 6.3 页面布局

```
┌──────────────────────────────────────────────────────────────────┐
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ 一卡通:[____] 订单号:[____] 第三方:[____] 状态:[下拉▼]      │ │
│ │ 订单日期:[____至____]                           [搜索][重置] │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ 缴费列表                                               [查看详情] │
│ ├──────────────────────────────────────────────────────────┤   │
│ │ ○ | 订单日期 | 订单号 | 支付金额 | 一卡通卡号 | 第三方订单 | 状态 | │
│ └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### 6.4 API调用关系

```javascript
// 缴费查询
import { detail, enter } from "@/api/apiPaymentManagement.js";

// 分页查询
enter({
  pageNum: 1,
  pageSize: 10,
  onecard: "卡号",
  ordernumber: "订单号",
  thirdparty: "第三方订单号",
  status: "支付状态",
  orderstart: "开始日期",
  endoforder: "结束日期"
})

// 查询详情
detail({ id: "订单ID" })
```

---

## ⚡ 第七章：快赔管理

**文件位置**: `src/pages/QuickClaim/`

### 7.1 功能说明（人话版）

> 快速理赔通道，患者授权后，系统自动查询就医数据并快速完成理赔。

### 7.2 核心页面

| 页面 | 功能 |
|------|------|
| QuickClaim.vue | 快赔申请主页面 |
| quickClaimApply.vue | 快赔申请 |
| quickClaimAuthorize.vue | 授权管理 |
| quickclaimResult.vue | 理赔结果 |

### 7.3 页面布局

```
┌──────────────────────────────────────────────────────────────────┐
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ 姓名:[____] 身份证:[____] 手机:[____] 授权状态:[下拉▼]       │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ 会员账户列表                              [取消授权]       │   │
│ ├──────────────────────────────────────────────────────────┤   │
│ │ ○ | 姓名 | 性别 | 证件类型 | 证件号 | 医院 | 状态 | ...  │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ 查询信息                              [就医数据查询]       │   │
│ │ 科室:[____]  就诊开始:[____]  就诊结束:[____]           │   │
│ └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### 7.4 API调用

```javascript
// src/api/apiquickam.js
import { 
  cancelEmpower,       // 取消授权
  insertStlQueryinfo,  // 就医数据查询
  query               // 授权列表查询
} from "@/api/apiquickam.js";

// 查询授权列表
query({
  name: "姓名",
  idcard: "身份证",
  authorizationstatus: "授权状态"
})

// 取消授权
cancelEmpower({
  id: "记录ID",
  birthday: "生日",
  certyficatecode: "证件号"
})
```

### 7.5 核心交互

```javascript
// 就医数据查询
searchHosp() {
  if (this.selectedRows.length == "0") {
    this.$warning({ title: "请选择一条记录!" });
  } else if (this.selectedRows.certyficatetype !== "0") {
    this.$warning({ title: "证件类型错误，快赔只支持身份证!" });
  } else if (this.selectedRows.status !== "1") {
    this.$warning({ title: "会员还未授权，请先授权!" });
  } else {
    this.$refs.hospSearch.handleSearch();
  }
}
```

---

## ⚙️ 第八章：系统管理

**文件位置**: `src/pages/SystemView/`

### 8.1 功能说明（人话版）

> 管理员用的"后台管理"，管理用户、角色、权限、机构等。

### 8.2 核心页面

| 页面 | 功能 |
|------|------|
| systemUserManage.vue | 用户管理 |
| roleManage.vue | 角色管理 |
| moduleManage.vue | 模块管理 |
| orgManage.vue | 机构管理 |
| logAudit.vue | 日志审计 |
| interfaceAuth.vue | 接口鉴权 |

### 8.3 角色管理页面布局

```
┌──────────────────────────────────────────────────────────────────┐
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ [🔍] 角色名称:[____] 状态:[下拉▼]    [搜索] [重置]           │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌────────────────────────────────────────────────────────────┐   │
│ │ 系统角色列表                    [新增] [批量导入] [批量删除] │   │
│ ├────────────────────────────────────────────────────────────┤   │
│ │ ○ | 角色名称 | 角色编码 | 系统 | 状态 | 操作               │   │
│ │ ● | 管理员   | admin   | 慢病系统 | 启用 | [编辑][禁用][删除]│   │
│ └────────────────────────────────────────────────────────────┘   │
│                                                                  │
│ ┌─ 编辑弹窗 ──────────────────────────────────────────────────┐  │
│ │ 角色信息：                                                  │  │
│ │   角色名称：[__________]  角色编码：[__________]            │  │
│ │   所属系统：[下拉▼____]   状态：[下拉▼____]                │  │
│ │                                                           │  │
│ │ 菜单权限：                                                  │  │
│ │   ☑ 慢病管理                                                │  │
│ │     ☑ 申报查询  ☑ 初审管理  ☑ 体检分配                    │  │
│ │   ☑ 药店管理                                                │  │
│ │     ☑ 缴费管理  ☑ 产品管理                                 │  │
│ │                                        [提交] [取消]       │  │
│ └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### 8.4 核心API调用

```javascript
// 角色管理相关API
import { 
  getRoleList,      // 获取角色列表
  saveRole,         // 保存角色
  deleteRole,       // 删除角色
  updateRoleStatus  // 更新角色状态
} from "@/api/apiRole.js";
```

---

## 🏩 第九章：医院管理

**文件位置**: `src/pages/Hospital/`

### 9.1 功能说明（人话版）

> 管理医院的会员信息、预约挂号、门诊费用等。

### 9.2 核心页面

| 页面 | 功能 |
|------|------|
| hisRegister.vue | 预约挂号 |
| hisRegisterList.vue | 挂号记录列表 |
| hisClinicFeeList.vue | 门诊费用列表 |
| hisCreateCard.vue | 建卡管理 |

### 9.3 预约挂号布局

```
┌──────────────────────────────────────────────────────────────────┐
│ ┌─ 会员信息查询 ───────────────────────────────────────────────┐ │
│ │ 姓名:[____] 身份证:[____] 手机:[____] 卡号:[____] [搜索]    │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─ 会员信息列表 ───────────────────────────────────────────────┐ │
│ │ 姓名 | 性别 | 证件类型 | 证件号 | 卡号 | 余额 | 状态 | ...  │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─ 挂号信息 ───────────────────────────────────────────────────┐ │
│ │ 科室:[下拉▼]  日期:[____]  [搜索]                          │ │
│ │                                                           │ │
│ │ 开放预约科室：                                              │ │
│ │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │ │
│ │ │ 内科    │ │ 外科    │ │ 儿科    │ │ 妇科    │          │ │
│ │ └─────────┘ └─────────┘ └─────────┘ └─────────┘          │ │
│ └───────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🗺️ 第十章：核心页面跳转关系图

### 10.1 整体架构图

```
                              ┌─────────────────┐
                              │   用户浏览器     │
                              └────────┬────────┘
                                       │
                                       ▼
                    ┌─────────────────────────────────────┐
                    │         /loginMb  (登录页)           │
                    │   ┌─────────────────────────┐       │
                    │   │  账号 + 密码 + 验证码    │       │
                    │   │         [登录]          │       │
                    │   └───────────┬─────────────┘       │
                    └───────────────┼─────────────────────┘
                                    │ 登录成功，获取token
                                    ▼
                    ┌─────────────────────────────────────┐
                    │         /home  (系统首页)            │
                    │  ┌────────────────────────────────┐   │
                    │  │  🔝 顶部导航栏 (用户名/日期)   │   │
                    │  ├────────────┬───────────────────┤   │
                    │  │ 📋 侧边菜单 │ 🏷️ 标签栏区域     │   │
                    │  │            │ ┌───────────────┐ │   │
                    │  │ • 慢病管理  │ │ router-view   │ │   │
                    │  │ • 药店管理  │ │  (动态页面)   │ │   │
                    │  │ • 支付管理  │ │               │ │   │
                    │  │ • 快赔管理  │ │               │ │   │
                    │  │ • 医院管理  │ └───────────────┘ │   │
                    │  │ • 系统管理  │                   │   │
                    │  └────────────┴───────────────────┘   │
                    └─────────────────────────────────────┘
```

### 10.2 主要功能模块跳转

```
┌─────────────────────────────────────────────────────────────────┐
│                        首页 (Home.vue)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐        │
│  │ 慢病管理 │   │ 药店管理 │   │ 支付管理 │   │ 快赔管理 │        │
│  └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘        │
│       │             │             │             │              │
│       ▼             ▼             ▼             ▼              │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐        │
│  │申报查询  │   │缴费列表  │   │缴费管理  │   │会员账户 │        │
│  │初审管理  │   │新增缴费  │   │退费管理  │   │理赔申请 │        │
│  │体检分配  │   │产品列表  │   │数据汇总  │   │理赔结果 │        │
│  │专家分配  │   └─────────┘   └─────────┘   └─────────┘        │
│  │用户管理  │                                                  │
│  │历史查询  │                                                  │
│  └─────────┘                                                  │
│                                                                 │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐                      │
│  │ 系统管理 │   │ 医院管理 │   │ 申报管理 │                      │
│  └────┬────┘   └────┬────┘   └────┬────┘                      │
│       │             │             │                            │
│       ▼             ▼             ▼                            │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐                       │
│  │用户管理  │   │预约挂号  │   │申报管理  │                       │
│  │角色管理  │   │挂号记录  │   │审核管理  │                       │
│  │模块管理  │   │门诊费用  │   │专家分配  │                       │
│  │机构管理  │   │建卡管理  │   │体检分配  │                       │
│  │日志审计  │   └─────────┘   └─────────┘                       │
│  └─────────┘                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 10.3 慢病申报流程跳转

```
┌─────────────────────────────────────────────────────────────────┐
│                     慢病申报全流程                                │
└─────────────────────────────────────────────────────────────────┘

[患者端/医院端]
      │
      ▼
┌─────────────────┐
│   线下/线上申报  │
│ diseaseDeclare  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   申报列表查询   │
│ newDeclareManage│
└────────┬────────┘
         │
         ├────────────────────────────────┐
         ▼                                ▼
┌─────────────────┐              ┌─────────────────┐
│   初审管理      │              │   申报修改      │
│ approveFirstTrial│              │ declarationMod │
└────────┬────────┘              └─────────────────┘
         │
         ▼
┌─────────────────┐
│   体检分配      │
│ diseaseCheck   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   专家分配      │
│ proficientManag│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   复审管理      │
│ auditManagement │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   完成/拒绝     │
│ 历史可查       │
└─────────────────┘
```

---

## 📡 第十一章：API调用关系总览

### 11.1 核心API文件映射

| 页面模块 | API文件 | 主要接口 |
|---------|---------|----------|
| 登录 | apiLoginMb.js | loginByCaptchaMb, sendUserVerifCodeMb, loginOutMb |
| 慢病申报 | apiDiseaseDeclare.js | queryList, getPictue, getVipMbDeclareFileTypesByDeclareId |
| 药店管理 | apiPaymentMange.js | getVipDrugstoreOrder, queryAccountInfoForYD, refundVipDrugstoreOrder |
| 支付管理 | apiPaymentManagement.js | detail, enter |
| 快赔管理 | apiquickam.js | query, cancelEmpower, insertStlQueryinfo |
| 系统管理 | apiUserManage.js, apiRole.js | getUserList, saveUser, getRoleList, saveRole |
| 医院管理 | apiHisRegister.js | getRegisterList, getAppointmentList |

### 11.2 API调用规范示例

```javascript
// 每个API文件遵循统一格式
import axios from "./axios";

const api = {
  // 方法名: (参数) => axios请求
  queryList: (obj) => {
    return axios.request({
      url: `/vipMbDeclareList/queryList`,  // 后端接口路径
      data: obj,                            // 请求参数
      method: 'POST'                        // 请求方法
    });
  },
  
  // 带分页的查询
  queryWithPage: (params) => {
    return axios.request({
      url: `/some/api`,
      data: {
        pageNum: params.pageNum || 1,
        pageSize: params.pageSize || 10,
        ...params                          // 展开其他参数
      },
      method: 'POST'
    });
  }
};

export default api;
```

### 11.3 Vue组件调用API流程

```javascript
// Step 1: 引入API
import api from "@/api/apiDiseaseDeclare";

// Step 2: 在methods中调用
methods: {
  initPage() {
    // Step 3: 组装参数
    const params = {
      name: this.formObj.nameOne,
      idcard: this.formObj.idcard,
      pageVo: {
        pageNum: this.pagination.current,
        pageSize: this.pagination.pageSize
      }
    };
    
    // Step 4: 调用API
    api.queryList(params).then(res => {
      // Step 5: 处理响应
      if (res.status == 0) {
        this.data = res.data.list;
        this.pagination.total = res.data.total;
      }
    }).catch(err => {
      // Step 6: 错误处理
      this.$message.error("查询失败");
    });
  }
}
```

---

## 🔧 第十二章：通用组件说明

### 12.1 searchCard 搜索卡片

**位置**: `@/components/searchCard/index.vue`

```vue
<!-- 使用方式 -->
<searchCard
  :formObj="formObj"       <!-- 绑定的表单对象 -->
  @search="search"         <!-- 搜索事件 -->
  @resetFields="resetFields"<!-- 重置事件 -->
  :colSpan="6"             <!-- 每行放几个表单项 -->
  formLayout="horizontal"  <!-- 表单布局方向 -->
/>
```

### 12.2 tableMixins 表格混入

**位置**: `@/utils/tableMixins.js`

提供通用的表格操作方法：
- `onPageChange` - 分页切换
- `onPageSizeChange` - 每页条数切换
- `selectConfirm` - 提示选择记录
- `resetFields` - 重置表单

### 12.3 el-container 自定义弹窗

**位置**: 项目内部封装

```vue
<el-container
  :visible="dialogVisible"     <!-- 显示/隐藏 -->
  title="弹窗标题"              <!-- 标题 -->
  width="60%"                   <!-- 宽度 -->
  :footer="false"              <!-- 是否显示底部 -->
  :dragstate="false"           <!-- 是否可拖拽 -->
  @cancel="closeDialog"        <!-- 关闭回调 -->
>
  <!-- 弹窗内容 -->
</el-container>
```

---

## 📋 第十三章：权限控制机制

### 13.1 路由守卫

```javascript
// src/router/index.js
router.beforeEach((to, from, next) => {
  // 检查登录状态
  let logInfoMB = util.getUserInfo();
  
  if (!logInfoMB) {
    if (to.path == '/loginMb') {
      next();
    } else {
      next('/loginMb');  // 未登录跳转登录页
    }
  } else {
    next();
  }
});
```

### 13.2 菜单权限

- 登录时后端返回 `menus` 菜单数据
- 存入 sessionStorage
- 渲染左侧菜单时只显示有权限的项

### 13.3 按钮级权限

```javascript
// 通过 v-if 控制按钮显示
<a-button v-if="hasPermission('declare:edit')">编辑</a-button>
<a-button v-if="hasPermission('declare:delete')">删除</a-button>
```

---

## ⚠️ 第十四章：小白常见问题

### Q1: 为什么同一个功能有多个版本？

**A**: 这是多地市定制的结果。延安、宝鸡、DZ等地区业务流程略有不同，所以各自有独立模块。

### Q2: declareStatus数字代码是什么意思？

**A**: 需要查字典/过滤器翻译：
- 11 = 初审通过
- 3 = 待体检
- 4 = 体检完成
- 21 = 专家鉴定通过
- 等...

### Q3: keep-alive是什么？

**A**: Vue内置组件，缓存已访问的页面。比如从申报查询跳到详情再返回，申报列表不需要重新加载。

### Q4: 为什么用sessionStorage不用localStorage？

**A**: 敏感信息会话级管理，关闭浏览器自动清除，更安全。

### Q5: API返回的status是什么含义？

**A**: 
- `status == 0` = 成功
- `status != 0` = 失败，需看errorMsg

### Q6: 什么是"一卡通"？

**A**: 慢病患者持有的IC卡/电子卡，绑定身份和账户信息。

---

## 📁 附录：文件索引

| 文件路径 | 说明 |
|---------|------|
| `src/pages/Home.vue` | 系统首页 |
| `src/pages/index.vue` | 顶部导航 |
| `src/components/loginMb/index.vue` | 登录页 |
| `src/pages/ChronicDis/diseaseDeclare.vue` | 慢病申报查询 |
| `src/pages/Newdeclare/newDeclareManage.vue` | 新申报管理 |
| `src/pages/Drugstore/drugstoreChargeList.vue` | 药店缴费列表 |
| `src/pages/Payment/paymentManagement.vue` | 支付管理 |
| `src/pages/QuickClaim/QuickClaim.vue` | 快赔申请 |
| `src/pages/SystemView/roleManage.vue` | 角色管理 |
| `src/pages/Hospital/hisRegister.vue` | 预约挂号 |
| `src/api/apiLoginMb.js` | 登录API |
| `src/api/apiDiseaseDeclare.js` | 慢病申报API |
| `src/api/apiPaymentMange.js` | 药店支付API |
| `src/router/index.js` | 路由配置 |
| `src/store/index.js` | Vuex配置 |

---

*文档结束*
