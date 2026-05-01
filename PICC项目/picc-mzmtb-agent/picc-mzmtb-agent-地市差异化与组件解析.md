# PICC门诊慢特病前端项目（PICC-MZMTB-Agent）
## 地市差异化与组件层深度解析

> 📌 **阅读说明**：本文档采用"小白也能看懂"的风格编写，通过大量生活化比喻帮助非技术人员理解技术架构。文档已对敏感信息进行脱敏处理。

---

## 📋 目录

1. [项目整体概览](#1-项目整体概览)
2. [Part 1：地市差异化分析](#2-part-1地市差异化分析)
3. [Part 2：组件层解析](#3-part-2组件层解析)
4. [Part 3：Store状态管理解析](#4-part-3store状态管理解析)
5. [技术架构总结](#5-技术架构总结)
6. [附录：常见问题FAQ](#6-附录常见问题faq)

---

## 1. 项目整体概览

### 1.1 项目定位

**🏠 打个比方**：
想象这是一个**大型连锁快餐店（麦/肯/当式）**的全国点餐系统：

| 现实场景 | 技术对应 |
|---------|---------|
| 全国各地连锁店 | 21个地市页面模块 |
| 汉堡/薯条基础菜单 | 通用组件库 |
| 各地特色菜品（如北京的炸酱面） | 地市专属业务逻辑 |
| 中央厨房配送系统 | 后端API接口 |
| 各门店收银系统 | Vuex状态管理 |

### 1.2 项目目录结构

```
picc-mzmtb-agent/
├── src/
│   ├── pages/          📁 21个地市页面模块（相当于各地分店）
│   │   ├── ChronicDis/     通用模块（全国统一菜单）
│   │   ├── YAChronicDis/   延安模块（62个Vue文件，最大分店）
│   │   ├── SLChronicDis/   商洛模块（58个Vue文件）
│   │   ├── YLChronicDis/   榆林模块（55个Vue文件）
│   │   └── ...（其他17个地市模块）
│   │
│   ├── mtbcomponents/     📁 基础款组件库（通用模具）
│   ├── mtbnewcomponents/   📁 新版组件库（升级款模具）
│   ├── mtbslcomponents/    📁 商洛定制组件库（定制款模具）
│   │
│   ├── store/           📁 Vuex状态管理（中央仓库）
│   ├── router/          📁 路由配置（导航系统）
│   ├── api/             📁 API接口（点餐呼叫系统）
│   ├── utils/           📁 工具函数（厨房小工具）
│   └── components/      📁 通用组件
```

---

## 2. Part 1：地市差异化分析

### 2.1 21个地市模块大盘点

| 地市模块 | Vue文件数 | 定位说明 |
|---------|----------|---------|
| **YAChronicDis** | 62个 | 🔥 延安——功能最全的旗舰店 |
| **SLChronicDis** | 58个 | 商洛——第二大分店 |
| **YLChronicDis** | 55个 | 榆林——第三大分店 |
| **ChronicDis** | 53个 | 通用模板——可复制的标准店 |
| **DZChronicDis** | 47个 | 定制版 |
| **JZChronicDis** | 40个 | 定制版 |
| **XYaChronicDis** | 32个 | 小延安版 |
| **YaLChronicDis** | 31个 | 雅安版 |
| **其他** | ... | 各有特色的小分店 |

**🏪 比喻理解**：
- 62个Vue文件 ≈ 大型超市的62个商品区
- 53个Vue文件 ≈ 中型超市的53个商品区
- 文件越多 = 功能越丰富 = 当地业务越复杂

### 2.2 各地市页面对比分析

#### 2.2.1 延安（YAChronicDis）独有功能 🚀

```
延安专属页面：
├── approveFirstTrial.vue      ✨ 初审审批（延安特色）
├── autoControlDeclare.vue     ✨ 自动申报控制
├── declarePower.vue           ✨ 申报权限管理
├── expertSecondaryJudgment.vue ✨ 专家二审判断
└── prescriptionPool.vue       ✨ 处方池管理
```

**🎯 延安的业务特点**：
- 业务闭环完整：有初审→二审的完整流程
- 自动化程度高：支持自动申报控制
- 权限管理精细：申报权限单独管理
- 处方管理独立：有专门的处方池

#### 2.2.2 商洛（SLChronicDis）独有功能

```
商洛专属页面：
├── AnnualAuditManagement.vue   ✨ 年度审核管理（商洛特色）
├── declarationInformation.vue   ✨ 申报信息管理
├── desensitization.vue         ✨ 数据脱敏处理
├── diseaseChange.vue           ✨ 病种变更
├── integratedQuery.vue         ✨ 综合查询
├── taskTable.vue               ✨ 任务表格
└── webUserManage.vue           ✨ 网站用户管理
```

**🎯 商洛的业务特点**：
- 年度审核严格：独立的年度审核管理
- 数据安全意识强：有专门的数据脱敏功能
- 查询功能丰富：综合查询能力突出

#### 2.2.3 榆林（YLChronicDis）独有功能

```
榆林专属页面：
├── declarationInformation.vue   ✨ 申报信息
├── declareModifyApply.vue       ✨ 申报修改申请
├── desensitization.vue          ✨ 数据脱敏
├── integratedQuery.vue          ✨ 综合查询
├── recordAnnual.vue              ✨ 年度记录
├── taskTable.vue                 ✨ 任务表格
└── webUserManage.vue            ✨ 网站用户管理
```

**🎯 榆林的业务特点**：
- 申报流程完整：支持申报修改申请
- 数据保护：数据脱敏功能
- 任务管理：独立的任务表格系统

#### 2.2.4 三城对比总结

| 功能维度 | 延安 | 商洛 | 榆林 | 通用 |
|---------|------|------|------|------|
| **初审审批** | ✅ 完整流程 | ✅ 有 | ✅ 有 | ✅ 有 |
| **二审判断** | ✅ 专家二审 | ❌ 无 | ❌ 无 | ❌ 无 |
| **自动申报** | ✅ 支持 | ❌ 无 | ❌ 无 | ❌ 无 |
| **年度审核** | ❌ 无 | ✅ 专属管理 | ✅ 专属管理 | ❌ 无 |
| **数据脱敏** | ❌ 无 | ✅ 有 | ✅ 有 | ❌ 无 |
| **处方池** | ✅ 独立管理 | ❌ 无 | ❌ 无 | ❌ 无 |
| **综合查询** | ❌ 无 | ✅ 有 | ✅ 有 | ❌ 无 |

### 2.3 地市差异化机制详解

#### 2.3.1 路由层：如何决定显示哪个地市页面？

**🔍 核心原理**：路由配置中的 `path` + 动态组件导入

```javascript
// src/router/childrenRoutes.js 示例

// 延安的用户导入
{
  path: `/userImport`,
  name: "userImport", 
  component: () => import("@/pages/YAChronicDis/userImport"), // 👈 指向延安模块
}

// 商洛的用户导入
{
  path: `/slUserImport`,  // 👈 不同的路径
  name: "slUserImport",
  component: () => import("@/pages/SLChronicDis/userImport"), // 👈 指向商洛模块
}
```

**🏪 通俗理解**：
```
用户点击"用户导入"菜单
    ↓
路由系统根据当前登录用户的"身份标识"（如cityFlag）
    ↓
跳转到对应的路由路径（如 /userImportYA 或 /slUserImport）
    ↓
加载对应地市的Vue页面组件
```

#### 2.3.2 登录时的地市识别

**🔐 核心流程**：

```
用户输入账号密码 → 登录接口返回用户信息 
    ↓
用户信息中包含 cityFlag（地市标识）字段
    ↓
前端Store存储cityFlag
    ↓
路由守卫根据cityFlag动态决定可访问的菜单和页面
```

**📝 示例**：
```javascript
// 登录返回的用户信息结构（简化版）
{
  userId: "U12345",
  userName: "张三",
  cityFlag: "YA",        // 👈 延安标识
  cityName: "延安市",
  permissions: ["userImport", "userModify", ...],
  menuData: [            // 👈 该用户可见的菜单
    { title: "慢病初审管理", routerName: "diseaseFirstTrial" },
    { title: "用户导入", routerName: "userImport" }
  ]
}
```

#### 2.3.3 地市模块与通用模块的关系

**🤝 继承关系图**：

```
                    ┌─────────────────┐
                    │  ChronicDis     │  👈 通用模板（基类）
                    │  (53个Vue文件)  │
                    └────────┬────────┘
                             │ 继承/复用
            ┌────────────────┼────────────────┐
            ↓                ↓                ↓
    ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
    │ YAChronicDis  │ │ SLChronicDis  │ │ YLChronicDis  │
    │   (62个)      │ │   (58个)      │ │   (55个)      │
    ├───────────────┤ ├───────────────┤ ├───────────────┤
    │ 通用页面: 50个 │ │ 通用页面: 48个 │ │ 通用页面: 47个 │
    │ 独有页面: 12个 │ │ 独有页面: 10个 │ │ 独有页面: 8个  │
    └───────────────┘ └───────────────┘ └───────────────┘
```

**📖 通俗解释**：
- **通用模块（ChronicDis）**：就像全国连锁店的"标准装修方案"
- **地市模块**：在标准方案基础上，根据当地法规和业务需求做的"本地化装修"
- **复用方式**：
  1. 直接复制通用页面 + 微调业务逻辑
  2. 继承通用页面 + Override特定方法
  3. 完全新建独有页面

#### 2.3.4 新增一个地市的前端接入步骤

**🚀 七步走战略**：

```
Step 1️⃣：创建地市文件夹
    在 src/pages/ 下创建，如 XXChronicDis/

Step 2️⃣：复制通用模块作为基础
    复制 src/pages/ChronicDis/ 下的文件到 XXChronicDis/

Step 3️⃣：调整业务逻辑
    根据新地市的需求，修改或新增页面组件

Step 4️⃣：配置路由
    在 src/router/childrenRoutes.js 中添加路由映射

Step 5️⃣：配置菜单权限
    在后端配置该cityFlag对应的菜单权限

Step 6️⃣：按需选择组件库
    如需定制UI，创建或修改组件库

Step 7️⃣：测试验证
    使用新地市账号登录，验证功能和界面
```

**📝 详细示例**：

```javascript
// Step 4：路由配置示例
// src/router/childrenRoutes.js

{
  // 新增地市的用户管理页面
  path: `/xxUserManage`,
  name: "xxUserManage",
  meta: {
    ptitle: "西安慢病管理",      // 👈 菜单父标题
    title: "慢病用户管理",       // 👈 菜单标题
    pathName: "/xxUserManage",
  },
  component: () => import("@/pages/XXChronicDis/userManage"),
}
```

---

## 3. Part 2：组件层解析

### 3.1 三套组件库概述

**🏭 打个比方**：三套模具工厂

| 组件库 | 文件数 | 定位 | 比喻 |
|--------|--------|------|------|
| **mtbcomponents** | 31个 | 基础款模具 | 普通塑料积木 |
| **mtbnewcomponents** | 50个 | 升级款模具 | 升级版塑料积木 |
| **mtbslcomponents** | 32个 | 商洛定制模具 | 商洛专属积木 |

### 3.2 组件库结构对比

```
mtbcomponents/                    mtbnewcomponents/                 mtbslcomponents/
├── comAddressSelect/             ├── comAddressSelect/              ├── comAddressSelect/
├── comAlert/                     ├── comAlert/                      ├── comAlert/
├── comPrintTable/                ├── comPrintTable/                 ├── comPrintTable/
├── comSelect/                    ├── comSelect/                     ├── comSelect/
├── datePicker/                   ├── declareModal/                  ├── datePicker/      ✨ 独有
├── declareModal/                 ├── header.vue                     ├── declareModal/
├── header.vue                    ├── loginMb/                       ├── header.vue
├── loginMb/                      ├── menuList/                      ├── loginMb/
├── menuList/                      ├── Modal/                         ├── menuList/
├── Modal/                        ├── modalTable/                    ├── Modal/
├── modalTable/                   ├── myAntAlert/       ✨ 独有      ├── modalTable/
├── myTable/                      ├── myTable/                      ├── myTable/
├── searchCard/                   ├── recordImport/     ✨ 独有      ├── searchCard/
├── selectTree/        ✨ 独有    ├── searchCard/                   ├── textArea/
├── textArea/                      ├── selectTree/
└── index.js                       ├── textArea/
                                    └── index.js
```

### 3.3 核心组件逐个解析

#### 3.3.1 通用组件（所有地市都在用）

**📦 myTable —— 万能表格组件**

```vue
<!-- 使用示例 -->
<myTable
  :columns="columns"           <!-- 表格列配置 -->
  :data="tableData"            <!-- 表格数据 -->
  :typeObj="['status']"         <!-- 需要转换的字段 -->
  :timeObj="['createTime']"     <!-- 需要格式化的时间 -->
  :moneyObj="['amount']"        <!-- 需要格式化的金额 -->
  :isSelect="true"             <!-- 是否可多选 -->
  :isPage="true"               <!-- 是否分页 -->
  @row-click="handleRowClick"  <!-- 行点击事件 -->
/>
```

**🔧 功能特性**：
| 功能 | 说明 |
|------|------|
| 自动类型转换 | status字段自动转中文（0→待审核，1→已通过） |
| 时间格式化 | createTime自动格式化为"2024-01-15 10:30" |
| 金额格式化 | amount自动加千分位和小数点 |
| 卡号脱敏 | 身份证号自动显示为 `********1234` |
| 分页支持 | 内置分页器 |
| 行选中 | 支持单选/多选 |

**🏪 通俗理解**：
> myTable就像一个"智能包装机"，你把数据扔进去，它自动帮你：
> - 贴上中文标签（类型转换）
> - 装上精美包装（格式化）
> - 盖上生产日期（时间处理）
> - 贴上保密条（数据脱敏）

---

**📦 searchCard —— 搜索卡片组件**

```vue
<!-- 使用示例 -->
<searchCard
  :fieldList="searchFields"     <!-- 搜索字段配置 -->
  :formObj="searchForm"         <!-- 表单初始值 -->
  @search="handleSearch"        <!-- 搜索事件 -->
  @reset="handleReset"          <!-- 重置事件 -->
/>
```

**🔧 支持的字段类型**：
| 类型 | 说明 | 示例 |
|------|------|------|
| `input` | 文本输入框 | 姓名、身份证号 |
| `input-long` | 长文本输入框 | 详细地址 |
| `select` | 下拉选择框 | 状态、类型 |
| `date-picker` | 日期选择器 | 申报日期 |
| `date-picker-array` | 日期范围选择器 | 开始~结束日期 |
| `radio` | 单选按钮 | 性别、是否报销 |
| `cascader` | 级联选择器 | 省市县三级联动 |

---

**📦 declareModal —— 申报弹窗组件**

```vue
<!-- 使用示例 -->
<declareModal
  :visible.sync="showModal"
  :type="'create'"              <!-- create/edit/view -->
  :recordId="currentRecordId"
  @success="handleSuccess"
/>
```

**🏪 通俗理解**：
> declareModal就像一个"标准申报表格"，有固定的格式：
> - 新建时：空白表格让你填
> - 编辑时：已有数据让你改
> - 查看时：只读模式给你看

---

#### 3.3.2 登录组件

**📦 loginMb —— 移动端登录组件**

```
src/mtbcomponents/loginMb/
├── index.vue          主登录页面
└── settingModal.vue  设置弹窗（修改密码等）
```

**🔐 登录流程**：

```
┌─────────────┐
│  输入账号   │ ──→ ┌──────────────┐
└─────────────┘     │  前端验证    │
┌─────────────┐     │  (非空/格式) │
│  输入密码   │ ──→ └──────┬───────┘
└─────────────┘            ↓
                    ┌──────────────┐
                    │  SM4加密     │ ← 密码加密传输
                    └──────┬───────┘
                            ↓
                    ┌──────────────┐
                    │  后端验证    │
                    │  返回Token   │
                    └──────┬───────┘
                            ↓
                    ┌──────────────┐
                    │  存储用户    │
                    │  信息和Token │
                    └──────────────┘
```

---

#### 3.3.3 其他重要组件

| 组件名 | 功能 | 使用场景 |
|--------|------|---------|
| **comSelect** | 通用下拉选择 | 所有下拉选择场景 |
| **comAddressSelect** | 地址三级联动 | 选择省/市/区 |
| **comAlert** | 通用提示框 | 操作成功/失败提示 |
| **comPrintTable** | 打印表格 | 打印申报表等 |
| **Modal** | 基础弹窗 | 确认框、详情弹窗 |
| **modalTable** | 弹窗表格 | 弹窗中展示数据列表 |
| **textArea** | 多行文本 | 备注、原因等 |
| **menuList** | 菜单列表 | 侧边栏菜单 |
| **header** | 面包屑头部 | 页面导航 |

### 3.4 组件复用模式

#### 3.4.1 全局共享组件

```
✅ 这些组件被所有地市共享使用：

myTable        ── 几乎所有列表页面都在用
searchCard     ── 几乎所有查询页面都在用
declareModal   ── 所有申报相关页面
comSelect      ── 所有下拉选择场景
comAlert       ── 全局提示
```

#### 3.4.2 地市专属组件

```
🔧 mtbnewcomponents 独有：
├── myAntAlert.vue     ── 新版提示组件
└── recordImport.vue   ── 记录导入组件

🔧 mtbslcomponents 独有：
└── datePicker.vue    ── 商洛专属日期选择器
```

#### 3.4.3 组件注册机制

**📝 自动注册原理**：

```javascript
// src/mtbcomponents/index.js

import Vue from 'vue'

// 自动扫描当前目录下所有.vue文件
const requireCom = require.context('./', true, /\.vue$/)

// 依次注册到Vue全局
requireCom.keys().forEach(key => {
  // 获取组件名（如 "./myTable/index.vue" → "MyTable"）
  const componentName = key
    .split('/')[1]           // 取中间部分
    .replace(/\.\w+$/, '')    // 去掉扩展名
    .charAt(0).toUpperCase() + // 首字母大写
    .slice(1)
  
  // 注册到Vue
  Vue.component(componentName, requireCom(key).default)
})
```

**🏪 通俗理解**：
> 这就像一个"自动注册机"：
> - 扫描文件夹里所有的.vue文件
> - 自动提取组件名
> - 自动注册到系统
> - 之后在任何页面都能直接使用 `<myTable>` 标签

---

## 4. Part 3：Store状态管理解析

### 4.1 Vuex Store 是什么？

**🏪 打个比方**：中央仓库

```
┌──────────────────────────────────────────────────────┐
│                     Vuex Store                       │
│                      (中央仓库)                       │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │   token    │  │  userInfo  │  │  menuData   │    │
│  │  (钥匙)    │  │  (员工卡)  │  │  (菜单)     │    │
│  └────────────┘  └────────────┘  └────────────┘    │
│                                                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │  cityFlag  │  │  tabList   │  │ collapsed  │    │
│  │  (城市证)  │  │  (标签页)  │  │  (菜单状态) │    │
│  └────────────┘  └────────────┘  └────────────┘    │
│                                                      │
└──────────────────────────────────────────────────────┘
            ↑ 读取              ↓ 修改
            │                   │
    ┌───────┴───────┐     ┌──────┴──────┐
    │  任何组件都能  │     │  通过commit │
    │  通过getters  │     │  修改状态   │
    │  读取数据     │     │             │
    └───────────────┘     └─────────────┘
```

### 4.2 Store模块结构

```
src/store/
├── index.js              主入口
└── modules/
    ├── menu.js           菜单模块
    └── activeRouterMatch.js  路由匹配模块
```

### 4.3 核心状态详解

#### 4.3.1 主状态（src/store/index.js）

```javascript
export default new Vuex.Store({
  state: {
    // 🔐 认证相关
    token: "",                    // 登录令牌（相当于钥匙）
    
    // 👤 用户信息
    pageUrl: "http://www.baidu.com",
    ActionStr: [],                // 操作权限列表
    DefaultOrgunitid: null,       // 默认机构ID
    
    // 🏙️ 地市标识（核心！）
    cityFlagSplit: "",            // 👈 用于区分地市
    
    // 📋 菜单数据
    menuData: [                   // 所有菜单配置
      {
        module_name: "慢病管理",
        children: [
          { title: "慢病初审管理", routerName: "diseaseFirstTrial" },
          { title: "慢病体检分配", routerName: "diseaseCheck" },
          // ...
        ]
      }
    ],
    
    menuList: [],                 // 快捷菜单
    menuDeclare: [],              // 申报菜单
    menuNewDeclare: [],           // 新版申报菜单
    menuQuick: [],                // 快赔菜单
    menuStore: [],                // 药店菜单
    
    // 🏠 系统管理
    systemData: [                 // 系统配置菜单
      { module_name: "模块管理", toUrl: "/module" },
      { module_name: "角色管理", toUrl: "/role" },
      // ...
    ],
    
    // 📑 UI状态
    tabList: [],                  // 标签页列表
    collapsed: false,             // 菜单是否折叠
    
    // 📊 其他
    selectData: [],               // 选择数据缓存
  },
  
  mutations: {
    // 更新Token
    updateToken(state, token) {
      state.token = token
    },
    
    // 更新用户菜单
    updateMenu(state, newMenu) {
      state.menuData = newMenu
    },
    
    // 更新城市标识
    saveAfterRouter(state, router) {
      state.afterRouter = router
    },
    
    // 设置机构ID
    setOrgunitid(state, data) {
      state.DefaultOrgunitid = data
    },
    
    // 标签页操作
    updateTabList(state, tab) {
      state.tabList = tab
    },
    
    // 菜单折叠
    updateCollapsed(state, collapsed) {
      state.collapsed = collapsed
    }
  }
})
```

#### 4.3.2 menu模块（菜单管理）

```javascript
// src/store/modules/menu.js

export default {
  state: {
    menuCollapsed: true,      // 菜单是否折叠
    userInfo: {},             // 用户详细信息
    sysPermission: true,      // 系统权限开关
    permissions: {},          // 权限详情 {menuCode: menuItem}
    menu: []                  // 菜单树
  },
  
  mutations: {
    // 切换菜单折叠状态
    toggleMenu(state) {
      state.menuCollapsed = !state.menuCollapsed
    },
    
    // 更新用户信息
    updateUserInfo(state, data) {
      state.userInfo = {
        deptId: data.deptId,
        roles: data.roles,
        roleNames: data.roleNames,
        userName: data.userName,
        email: data.email
      }
      // 构建权限映射
      let permissions = {}
      ;(data.menus || []).forEach(x => {
        x.menuCode && (permissions[x.menuCode] = x)
      })
      state.permissions = permissions
    },
    
    // 更新菜单
    updateMenu(state, data) {
      // 处理特殊菜单（问题管理、数据报告等）
      // ...
      state.menu = menus
    }
  }
}
```

### 4.4 状态管理流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户登录流程                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────────────┐
                    │   登录成功       │
                    └────────┬────────┘
                             ↓
              ┌──────────────────────────────┐
              │  后端返回用户信息：            │
              │  - token                    │
              │  - menuData (菜单)           │
              │  - cityFlag (地市标识)       │
              │  - permissions (权限)       │
              └──────────────────────────────┘
                             ↓
         ┌────────────────────┴────────────────────┐
         ↓                                         ↓
┌─────────────────┐                      ┌─────────────────┐
│  存入Vuex Store │                      │  存储Session    │
│                 │                      │  (浏览器会话)   │
│  state.token    │                      │                 │
│  state.menuData │                      │  刷新页面时     │
│  state.cityFlag │                      │  可恢复登录状态 │
│  ...            │                      │                 │
└─────────────────┘                      └─────────────────┘
         ↓
┌─────────────────────────────────────────┐
│           前端根据状态渲染               │
│                                         │
│  if (cityFlag === 'YA') {               │
│    // 渲染延安专属菜单                    │
│  } else if (cityFlag === 'SL') {       │
│    // 渲染商洛专属菜单                    │
│  }                                      │
│                                         │
│  if (permissions['userImport']) {      │
│    // 显示用户导入菜单                    │
│  }                                      │
└─────────────────────────────────────────┘
```

### 4.5 持久化机制

```javascript
// Store配置
import createPersistedState from 'vuex-persistedstate'

const store = new Vuex.Store({
  // ...
  plugins: [
    // 👇 关键：数据持久化到 sessionStorage
    createPersistedState({
      storage: window.sessionStorage,  // 页面关闭即清除
    })
  ]
})
```

**🔐 安全说明**：
- 使用 `sessionStorage` 而非 `localStorage`
- 页面关闭/浏览器关闭后自动清除登录状态
- 防止多人共用电脑时的信息泄露

---

## 5. 技术架构总结

### 5.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户浏览器                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐        ┌──────────────┐                     │
│   │   登录页     │   →    │  主页/菜单   │                     │
│   │  (loginMb)   │        │              │                     │
│   └──────────────┘        └──────┬───────┘                     │
│                                 ↓                                │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                     Vue Router 路由系统                   │  │
│   │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │  │
│   │  │延安路由  │ │商洛路由  │ │榆林路由  │ │通用路由  │       │  │
│   │  │(YA*)    │ │(SL*)    │ │(YL*)    │ │(Chronic)│       │  │
│   │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                 ↓                                │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                     Vuex Store 状态管理                  │  │
│   │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐            │  │
│   │  │ Token  │ │MenuData│ │CityFlag│ │UserInfo│            │  │
│   │  └────────┘ └────────┘ └────────┘ └────────┘            │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                     页面组件层                            │  │
│   │  ┌──────────────────────────────────────────────────┐   │  │
│   │  │              地市专属页面                          │   │  │
│   │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐            │   │  │
│   │  │  │ YA页面  │ │ SL页面  │ │ YL页面  │            │   │  │
│   │  │  └────┬────┘ └────┬────┘ └────┬────┘            │   │  │
│   │  └────────┼──────────┼──────────┼─────────────────┘   │  │
│   │           ↓          ↓          ↓                       │  │
│   │  ┌──────────────────────────────────────────────────┐   │  │
│   │  │              组件库（乐高积木）                    │   │  │
│   │  │  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐        │   │  │
│   │  │  │myTable│ │search │ │declare │ │comSel │        │   │  │
│   │  │  │       │ │Card   │ │Modal   │ │ect    │        │   │  │
│   │  │  └───────┘ └───────┘ └───────┘ └───────┘        │   │  │
│   │  └──────────────────────────────────────────────────┘   │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP请求
┌─────────────────────────────────────────────────────────────────┐
│                        后端API服务                              │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 核心技术栈

| 技术 | 用途 | 说明 |
|------|------|------|
| **Vue 2.x** | 前端框架 | 核心UI框架 |
| **Vue Router** | 路由管理 | 页面导航 |
| **Vuex** | 状态管理 | 数据存储 |
| **Ant Design Vue** | UI组件库 | 企业级UI组件 |
| **Axios** | HTTP请求 | API调用 |
| **Less** | CSS预处理器 | 样式编写 |

### 5.3 地市差异化的三种实现方式

| 方式 | 说明 | 示例 |
|------|------|------|
| **路由分离** | 不同地市使用不同路由路径 | `/ya/userImport` vs `/sl/userImport` |
| **组件复用** | 复用通用组件，不同地市调用不同API | 同一页面，不同数据源 |
| **配置驱动** | 通过配置文件控制功能开关 | `config.js` 中的开关 |

---

## 6. 附录：常见问题FAQ

### Q1：如何添加一个新的地市模块？

**A**：七步走
1. 在 `src/pages/` 下创建地市文件夹（如 `XXChronicDis/`）
2. 复制通用模块作为基础
3. 按需修改业务逻辑
4. 在路由中配置新路由
5. 配置后端菜单权限
6. 测试验证

### Q2：为什么延安有62个文件，其他地市少很多？

**A**：延安是功能最全的旗舰店，很多功能（如二审、自动申报等）只在延安上线，其他地市逐步跟进。

### Q3：三套组件库有什么区别？用哪个？

**A**：
- **mtbcomponents**：基础版，稳定
- **mtbnewcomponents**：新版，功能更多
- **mtbslcomponents**：商洛定制版，有专属组件

一般按项目要求选择，或直接用 `mtbnewcomponents`。

### Q4：cityFlag 是怎么传递的？

**A**：登录后由后端返回，存储在 Vuex 的 `state.cityFlag` 中，所有需要区分地市的组件都会读取这个值。

### Q5：如何调试某个地市的页面？

**A**：
1. 使用该地市的测试账号登录
2. 在浏览器开发者工具中查看 Vue Devtools
3. 检查 `Vuex Store` 中的 `cityFlag` 值
4. 确认是否加载了正确的路由

---

## 📝 文档信息

- **生成时间**：2024年
- **项目版本**：PICC-MZMTB-Agent
- **文档作者**：AI文档助手
- **适用对象**：前端开发人员、产品经理、零基础新人

---

> 💡 **温馨提示**：本文档已对敏感信息进行脱敏处理。如需更详细的代码实现，请查阅项目源码。
