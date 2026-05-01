# PICC门诊慢特病前端项目 API层与路由深度解析文档

> 📅 更新时间：2024年  
> 📂 项目位置：/tmp/picc-mzmtb-agent/  
> 🔧 技术栈：Vue 2 + Vuex + Vue Router + Axios  
> 📊 项目规模：74个API文件，652个Vue文件，2389行路由配置

---

## 📋 目录

1. [项目概览](#1-项目概览)
2. [Axios封装层深度解析](#2-axios封装层深度解析)
3. [多实例Axios架构](#3-多实例axios架构)
4. [API层架构详解](#4-api层架构详解)
5. [路由系统深度解析](#5-路由系统深度解析)
6. [Vuex状态管理](#6-vuex状态管理)
7. [安全机制详解](#7-安全机制详解)
8. [多城市flag标识系统](#8-多城市flag标识系统)
9. [API接口总览](#9-api接口总览)
10. [路由菜单总览](#10-路由菜单总览)

---

## 1. 项目概览

### 1.1 技术架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端应用层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Vue组件    │  │   Vue组件    │  │   Vue组件    │  ...652个  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
└─────────┼────────────────┼────────────────┼────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API调用层 (74个文件)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ apiLogin │ │apiUserMg │ │apiDisease│ │apiDeclare│  ...340+个│
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │
└───────┼────────────┼────────────┼────────────┼──────────────────┘
        │            │            │            │
        └────────────┴────────────┼────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Axios封装层 (4个实例)                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────┐ │
│  │  axios.js    │ │axiosCenter.js│ │axiosPower.js │ │axiosjkgl│ │
│  │  (慢病业务)   │ │  (通用中心)   │ │  (权限管理)   │ │(接口鉴权)│ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └─────────┘ │
└─────────────────────────────────────────────────────────────────┐
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                        后端API服务                               │
│     慢病业务API  │  通用中心API  │  权限管理API  │  接口鉴权API    │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 目录结构

```
picc-mzmtb-agent/src/
├── api/                          # API层 (74个文件)
│   ├── axios.js                  # 主Axios实例 - 慢病业务
│   ├── axiosCenter.js            # 通用中心请求配置
│   ├── axiosPower.js             # 权限管理请求配置
│   ├── axiosjkgl.js              # 接口鉴权请求配置
│   ├── axiosAuther.js            # 信创鉴权配置
│   ├── apiLogin.js               # 登录相关API
│   ├── apiUserManage.js          # 用户管理API
│   ├── apiDiseaseDeclare.js      # 慢病申报API
│   ├── apiChronicDis.js          # 慢病管理API
│   ├── apiSystem.js              # 系统管理API
│   ├── apiOrganization.js        # 机构管理API
│   └── ...                       # 其他业务API (65+个)
│
├── router/                        # 路由配置
│   ├── index.js                  # 路由主入口
│   └── childrenRoutes.js         # 子路由配置 (2389行)
│
├── store/                         # Vuex状态管理
│   ├── index.js                  # 主Store
│   └── modules/                  # Store模块
│       ├── menu.js
│       └── activeRouterMatch.js
│
├── pages/                        # 页面组件 (按业务模块组织)
│   ├── Home.vue                 # 首页
│   ├── SystemView/             # 系统管理页面
│   ├── ChronicDis/             # 慢病管理页面
│   └── ...
│
└── utils/                        # 工具函数
    └── util.js                  # 通用工具 (含AES加解密)
```

---

## 2. Axios封装层深度解析

### 2.1 主Axios实例 (axios.js) - 慢病业务核心

这是项目中最核心的Axios封装，包含**请求加密**和**响应解密**功能。

#### 2.1.1 基础配置

```javascript
// 环境判断
if (process.env.NODE_ENV === 'development') {
    baseURL = '';                    // 开发环境：使用相对路径
    urlPrefix = 'apis';              // 开发环境API前缀
} else {
    baseURL = process.env.domainName; // 生产环境：使用配置域名
}

// 请求实例配置
let conf = {
    baseURL: baseURL,
    withCredentials: true,          // 允许携带Cookie
    headers: {
        "Content-Type": "application/json; charset=utf-8",
        "X-URL-PATH": location.pathname,  // 当前路径
        "token": token              // 认证Token
    }
};
```

#### 2.1.2 请求拦截器 (Request Interceptor)

```javascript
// 请求拦截器处理的6个关键步骤：
// 1️⃣ 参数加密
config.data = this.encryptRequestFieldsWithAES(config.data, apiUrl);

// 2️⃣ Token提取 (从URL参数获取)
token = qs.parse(query, { ignoreQueryPrefix: true })["token"];

// 3️⃣ 用户ID提取
userId = logInfoMB.userId;

// 4️⃣ 城市标识提取
cityFlag = qs.parse(query, { ignoreQueryPrefix: true })["flag"];

// 5️⃣ 设置请求头
config.headers['Authorization'] = token;
config.headers['token'] = token;
config.headers['tokenFlag'] = sessionStorage.getItem('tokenFlag');
config.headers['userId'] = userId;
config.headers['flag'] = flag || 0;
```

#### 2.1.3 响应拦截器 (Response Interceptor)

```javascript
// 响应拦截器处理流程：
// 1️⃣ AES字段解密
if (data && data.status === 0) {
    data = this.decryptSpecificFieldsWithAES(data);
}

// 2️⃣ 错误处理
if (data.status !== undefined && data.status !== 0 && data.status !== 200) {
    // 显示错误消息
    message.error(errorMsg);
    
    // 登录超时处理 (status=999)
    if (data.status == 999) {
        window.sessionStorage.clear();
        Router.replace("/loginMb");
    }
    return Promise.reject(data);
}

// 3️⃣ 超时处理
if(error.message.includes('timeout')) {
    message.error("服务请求超时，稍后重试");
}
```

### 2.2 通用中心Axios实例 (axiosCenter.js)

用于接入**通用中心**系统的请求配置。

```javascript
// 基础配置差异
if (process.env.NODE_ENV === 'development') {
    urlPrefix = 'api2';  // 开发环境使用api2前缀
} else {
    baseURL = process.env.domainNameCenter;  // 使用通用中心域名
}

// 特殊鉴权机制 - MD5签名
let headerSign = {
    accountNum: "1546784022366257152",  // 账户编号
    accessId: util.getUUIDTime(8, 10) + "_" + dataTime,  // 随机ID
    apiCode: config.data.apiCode,      // API代码
    accessDate: util.formatDays(dataTime)  // 访问日期
};

// 生成MD5签名
let md5 = cryptoJs.MD5(`${headerSign.accountNum}${headerSign.accessId}${headerSign.apiCode}${headerSign.accessDate}`) + ''
headerSign.sign = md5.toUpperCase();
```

### 2.3 权限管理Axios实例 (axiosPower.js)

用于**权限管理系统**的请求配置，支持AES加密/解密。

```javascript
// 继承主Axios的加密机制
if (config.data) {
    config.data = this.encryptRequestFieldsWithAES(config.data, apiUrl);
}

// 响应解密
if (data && data.status === 0) {
    data = this.decryptSpecificFieldsWithAES(data, apiUrl);
}

// 请求头配置
config.headers['token'] = token;
config.headers['userId'] = userId;
```

### 2.4 接口鉴权Axios实例 (axiosjkgl.js)

用于**接口鉴权**系统的请求配置。

---

## 3. 多实例Axios架构

### 3.1 四大实例对比

| 实例名称 | 文件 | 用途 | 域名配置 | 特殊功能 |
|---------|------|------|---------|---------|
| axios.js | 慢病业务 | 核心业务请求 | domainName | AES加解密 |
| axiosCenter.js | 通用中心 | 接入通用中心 | domainNameCenter | MD5签名 |
| axiosPower.js | 权限管理 | 权限系统 | domainNamePower | AES加解密 |
| axiosjkgl.js | 接口鉴权 | 接口权限管理 | - | 基础配置 |

### 3.2 实例选择流程图

```
发起API请求
     │
     ▼
┌─────────────┐
│ 请求URL分析 │
└─────────────┘
     │
     ├─── 包含 "/privilege/" ───→ axiosPower.js (权限管理)
     │
     ├─── 包含 "/codename/" ───→ axios.js (通用请求)
     │
     ├─── 通用中心接口 ────────→ axiosCenter.js (通用中心)
     │
     └─── 其他业务接口 ────────→ axios.js (默认)
```

### 3.3 URL路径前缀规则

```javascript
// 根据cityFlag决定API版本
if (cityFlag == '8' || cityFlag == '10' || cityFlag == '16' || 
    (cityFlag == '2' && SLV2List.includes(url))) {
    // 使用v2版本API
    url = urlPrefix + '/v2' + url;
} else {
    // 使用普通API
    url = urlPrefix + url;
}

// 添加时间戳防止缓存
if (url.indexOf("?") > 0) {
    url += "&_t=" + Math.random();
} else {
    url += "?_t=" + Math.random();
}
```

---

## 4. API层架构详解

### 4.1 API文件组织结构

```
API文件命名规范：api + 业务模块名.js

示例：
├── apiLogin.js              # 登录模块
├── apiUserManage.js         # 用户管理
├── apiDiseaseDeclare.js      # 慢病申报
├── apiChronicDis.js         # 慢病管理
├── apiDeclarationexpert.js  # 专家审核
├── apiAuditManagement.js    # 审核管理
├── apiPrescriptionManage.js # 处方管理
└── ...
```

### 4.2 API调用模式

```javascript
// 标准API文件结构
import axios from "./axios";  // 导入Axios实例

// 方式1：具名导出
export const queryList = (param) => {
    return axios.request({
        url: `/MbDeclare/queryList`,
        data: param,
        method: "post"
    });
};

// 方式2：对象导出
const api = {
    getDetail: (obj) => {
        return axios.request({
            url: `/MbUser/getDetail`,
            data: obj,
            method: 'POST'
        })
    }
};
export default api;

// 方式3：混合导出
export const login = (param) => {...};
export const logout = (param) => {...};
export default { login, logout };
```

### 4.3 API模块分类 (共74个文件)

#### 🏥 系统管理模块 (6个文件)

| 文件名 | 功能 | 核心接口 |
|--------|------|---------|
| apiUserManage.js | 用户管理 | MbUser/edit, query, resetPassword |
| apiOrganization.js | 机构管理 | /privilege/org/* |
| apiSystem.js | 系统配置 | 权限相关接口 |
| apiModule.js | 模块管理 | 模块CRUD |
| apiRoleManage.js | 角色管理 | 角色权限配置 |
| apiLogRecordQuery.js | 日志审计 | 操作日志查询 |

#### 👤 登录认证模块 (4个文件)

| 文件名 | 功能 | 核心接口 |
|--------|------|---------|
| apiLogin.js | 登录 | /Login/doLogin, /Login/getUser |
| apiLoginMb.js | 移动端登录 | 移动端专用登录 |
| apiloginOut.js | 登出 | /Login/signOut |
| apiauthorization.js | 授权 | 授权相关 |

#### 🏥 慢病申报模块 (15个文件)

| 文件名 | 功能 | 核心接口 |
|--------|------|---------|
| apiDiseaseDeclare.js | 申报查询 | /vipMbDeclareList/queryList |
| apiDeclare.js | 申报管理 | /MbDeclare/* |
| apiDeclarationexpert.js | 专家审核 | 专家审核相关 |
| apiDeclarationInquiry.js | 申报录入 | 申报信息录入 |
| apiDiseaseRecheck.js | 复审管理 | 复审流程 |
| apiDiseaseOfflineDecalre.js | 线下申报 | 线下申报处理 |
| apiDeclareQueryInfo.js | 申报查询信息 | 申报详情 |

#### 📋 慢病管理模块 (10个文件)

| 文件名 | 功能 | 核心接口 |
|--------|------|---------|
| apiChronicDis.js | 慢病主管理 | ICD编码、病种管理 |
| apiDiseaseRecord.js | 备案管理 | /filingMan/* |
| apiDiseaseChange.js | 病种变更 | 变更申请 |
| apiUserModify.js | 用户修改 | 人员信息修改 |
| apiUserImport.js | 批量导入 | Excel导入 |

#### 💊 处方管理模块 (8个文件)

| 文件名 | 功能 | 核心接口 |
|--------|------|---------|
| apiEnterPrescription.js | 处方录入 | 处方信息录入 |
| apiPrescriptionImport.js | 处方导入 | 批量导入处方 |
| apiDrug.js | 药品管理 | 药品库管理 |
| apiDrugMaintain.js | 药品维护 | 药品信息维护 |

#### 💳 支付管理模块 (6个文件)

| 文件名 | 功能 | 核心接口 |
|--------|------|---------|
| apiPaymentMange.js | 支付管理 | 支付相关 |
| apiPaymentManagement.js | 支付处理 | 支付流程 |
| apiHistoryPayment.js | 历史支付 | 支付记录 |
| apiOfflinepayment.js | 线下支付 | 线下支付处理 |

#### 🏦 会员管理模块 (5个文件)

| 文件名 | 功能 | 核心接口 |
|--------|------|---------|
| apiVipAccountManage.js | 会员账户 | 账户信息管理 |
| apiWaitCardManage.js | 待发卡 | 发卡管理 |
| apiBindCardManage.js | 人卡绑定 | 绑定管理 |
| apivipRecordQuery.js | 消费记录 | 消费流水查询 |

#### 🏨 医院管理模块 (5个文件)

| 文件名 | 功能 | 核心接口 |
|--------|------|---------|
| apiHisRegister.js | 挂号管理 | 挂号预约 |
| apiHisClinicFeeList.js | 门诊费用 | 费用清单 |
| apiHisCreateCard.js | 建卡管理 | 医院建卡 |

#### ⚡ 快速理赔模块 (4个文件)

| 文件名 | 功能 | 核心接口 |
|--------|------|---------|
| apiQuickClaimApply.js | 快速理赔申请 | 快赔申请 |
| apiQuickClaimAuthorize.js | 快赔授权 | 授权确认 |
| apiQuickClaim.js | 快赔处理 | 快赔主流程 |

#### 🔒 其他业务模块 (10+个文件)

- apiApplyforcheck.js - 申请审核
- apiApplyforQuery.js - 申请查询
- apiAuditManagement.js - 审核管理
- apiIntelligent.js - 智能审核
- apiCommon.js - 通用接口
- apiAddressSelect.js - 地址选择
- apiDoctor.js - 医生管理
- apiList.js - 列表查询
- apiHistory.js - 历史记录
- apiExportReport.js - 报表导出
- apiDrgReconciliation.js - DRG对账
- apiYlRecordAnnual.js - 年度记录
- apiZjkChronicDis.js - 张家口慢病
- apiMbExpertAssign.js - 专家分配
- apiMbPhysicalAssign.js - 体检分配
- apiServiceStatus.js - 服务状态
- apiDataView.js - 数据查看
- apiInquiry.js - 查询接口
- apiTaskTable.js - 任务表格
- apiInterface.js - 接口管理

---

## 5. 路由系统深度解析

### 5.1 路由架构

```
静态路由 (index.js)
├── /                 # 根路径 → 重定向
├── /home             # 首页容器
│   └── children      # 动态子路由
└── /loginMb          # 登录页

动态路由 (childrenRoutes.js)
└── 2389行路由配置
    ├── 系统管理 (6个)
    ├── 宝鸡慢病管理 (35个)
    ├── 延安慢病管理 (35个)
    ├── 商洛慢病管理 (36个)
    ├── 晋中慢病管理 (29个)
    ├── 榆林慢病管理 (12个)
    ├── 杨凌慢病管理 (11个)
    ├── 咸阳慢病管理 (9个)
    ├── 阜新慢病管理 (8个)
    ├── 晋城慢病管理 (8个)
    ├── 张家口慢病管理 (7个)
    ├── 九江慢病管理 (7个)
    ├── 定州慢病管理 (4个)
    ├── 满洲里慢病管理 (8个)
    ├── 药店管理 (6个)
    ├── 快赔管理 (6个)
    ├── 慢病管理 (6个)
    ├── 医院管理 (4个)
    └── 系统管理 (6个)
```

### 5.2 路由配置详解

```javascript
// 标准路由配置模板
{
    path: `/diseaseDeclare`,                    // 路由路径
    name: "diseaseDeclare",                    // 路由名称
    meta: {
        ptitle: "宝鸡慢病管理",                 // 父级菜单标题
        title: "慢病申报查询",                  // 菜单标题
        pathName: "/diseaseDeclare"            // 路径标识
    },
    component: () => import("@/pages/...")     // 懒加载组件
}

// 带flag参数的路由 (多城市)
{
    path: "/diseaseDeclare&flag=2",            // flag=2 商洛
    name: "diseaseDeclare_sl",
    meta: {
        ptitle: "商洛慢病管理",
        title: "慢病申报查询"
    },
    component: () => import("@/pages/...")
}
```

### 5.3 路由守卫 (Navigation Guards)

```javascript
// 全局前置守卫
router.beforeEach((to, from, next) => {
    // 1️⃣ 修改页面标题
    if (to.meta.title) {
        document.title = to.meta.title;
    }
    
    // 2️⃣ 检查登录状态
    let logInfoMB = util.getUserInfo();
    
    if (!logInfoMB) {
        // 未登录 - 跳转登录页
        if (to.path == '/loginMb') {
            next();
            sessionStorage.clear();
            store.commit("updateTabList", []);
        } else if (to.path == '/resetConfirm') {
            // 密码重置页面
            next();
        } else {
            next('/loginMb');
            sessionStorage.clear();
            store.commit("updateTabList", []);
        }
    } else {
        next();
    }
    
    // 3️⃣ 版本更新检测
    if (from.path !== to.path) {
        updatePages();
    }
});

// 全局后置守卫 - 滚动复位
router.afterEach((to, from, next) => {
    window.scrollTo(0, 0);
});
```

### 5.4 懒加载策略

```javascript
// 所有页面组件使用懒加载
component: () => import("@/pages/SystemView/systemUserManage")

// 优势：
// 1. 首屏加载更快
// 2. 按需加载减少内存占用
// 3. 利于缓存和更新
```

### 5.5 路由重试机制

```javascript
// 解决路由跳转报错问题
const originalPush = Router.prototype.push;
Router.prototype.push = function push(location) {
    return originalPush.call(this, location).catch(err => err);
};

const originalReplace = Router.prototype.replace;
Router.prototype.replace = function replace(location) {
    return originalReplace.call(this, location).catch(err => err);
};
```

---

## 6. Vuex状态管理

### 6.1 Store结构

```javascript
// 主Store (index.js)
const store = new Vuex.Store({
    modules: {
        menu,                   // 菜单模块
        activeRouterMatch       // 路由匹配模块
    },
    state: {
        pageUrl: "...",         // 页面URL
        showType: "router",     // 显示类型
        ActionStr: [],          // 操作列表
        token: "",              // 认证Token
        afterRouter: "",        // 路由信息
        cityFlagSplit: "",      // 城市标识 (关键)
        DefaultOrgunitid: null, // 默认机构ID
        systemData: [...],      // 系统数据
        menuData: [...]         // 菜单数据
    },
    plugins: [createPersisted]  // 持久化插件
});
```

### 6.2 持久化配置

```javascript
// 使用vuex-persistedstate
// 数据存储到sessionStorage
const createPersisted = createPersistedState({
    storage: window.sessionStorage,
});
```

### 6.3 核心状态说明

| 状态名 | 类型 | 说明 | 持久化 |
|--------|------|------|--------|
| token | String | 认证令牌 | ✓ |
| cityFlagSplit | String | 城市标识 | ✓ |
| afterRouter | String | 路由信息 | ✓ |
| menuData | Array | 菜单数据 | ✓ |
| systemData | Array | 系统数据 | ✓ |

---

## 7. 安全机制详解

### 7.1 AES字段加密/解密

#### 7.1.1 加密的必要性

敏感字段（姓名、身份证、手机号）需要加密传输，防止中间人攻击。

#### 7.1.2 加密字段清单

```javascript
// 需要加密的字段列表
const fieldsToEncrypt = [
    'name', 'idcard', 'mobile', 'tel',
    'appntname', 'appntmobile', 'appntidno',      // 投保人信息
    'insurednname', 'insuredidno', 'insuredmobile', // 被保人信息
    'oldname', 'oldidcard', 'oldmobile'            // 旧信息
];
```

#### 7.1.3 加密白名单

```javascript
// 只有以下接口的请求参数才加密
const encryptRequestWhiteList = [
    '/vipMbDeclareList/queryList',
    '/MbDeclareFirstTrial/queryMbDeclareListInFirstTrail',
    '/MbDeclareFirstTrial/getMbDeclareInfo',
    '/filingMan/queryFiling',
    '/MbYearCheck/querySl',
    '/MbDeclare/query',
    '/MbPrescription/getDrugPrescriptionYa',
    '/MbPrescriptionManagement/getPrescription',
    // ... 更多接口
];
```

### 7.2 Token认证机制

```javascript
// Token获取方式
// 1. 从URL参数获取
let query = location.href.split('?')[1];
token = qs.parse(query, { ignoreQueryPrefix: true })["token"];

// 2. 从本地存储获取
if (util.getUserInfo()) {
    let logInfoMB = util.getUserInfo();
    token = logInfoMB.token;
}

// 3. 设置到请求头
config.headers['Authorization'] = token;
config.headers['token'] = token;
```

### 7.3 登录超时处理

```javascript
// 响应拦截器中检测
if (data.status == 999) {
    window.sessionStorage.clear();    // 清除存储
    Router.replace("/loginMb");       // 跳转登录页
}
```

---

## 8. 多城市flag标识系统

### 8.1 城市标识对照表

| flag值 | 城市/地区 | 说明 |
|--------|----------|------|
| 0 | 宝鸡 | 陕西宝鸡市 |
| 1 | 阜新 | 辽宁阜新市 |
| 2 | 商洛 | 陕西商洛市 |
| 3 | 张家口 | 河北张家口市 |
| 4 | 延安 | 陕西延安市 |
| 6 | 杨凌 | 陕西杨凌示范区 |
| 7 | 咸阳 | 陕西咸阳市 |
| 8 | 晋中 | 山西晋中市 |
| 10 | 榆林 | 陕西榆林市 |
| 13 | 九江 | 江西九江 |
| 15 | 定州 | 河北定州 |
| 16 | 满洲里 | 内蒙古满洲里 |
| 17 | 晋城 | 山西晋城 |

### 8.2 flag使用场景

```javascript
// 1. API版本选择
if (cityFlag == '8' || cityFlag == '10' || cityFlag == '16') {
    url = urlPrefix + '/v2' + url;  // 使用v2版本API
}

// 2. 路由参数传递
if (cityFlag) {
    options.data.flag = cityFlag;
} else if (!options.data.flag) {
    options.data.flag = 0;  // 默认宝鸡
}

// 3. 动态路由匹配
path: "/diseaseDeclare&flag=2"  // 商洛专用路由
```

---

## 9. API接口总览

### 9.1 接口数量统计

| 分类 | 文件数 | 预估接口数 |
|------|--------|-----------|
| 系统管理 | 6 | ~40 |
| 登录认证 | 4 | ~15 |
| 慢病申报 | 15 | ~80 |
| 慢病管理 | 10 | ~60 |
| 处方管理 | 8 | ~40 |
| 支付管理 | 6 | ~30 |
| 会员管理 | 5 | ~25 |
| 医院管理 | 5 | ~20 |
| 快速理赔 | 4 | ~20 |
| 其他业务 | 10+ | ~30 |
| **总计** | **74** | **~340+** |

### 9.2 核心业务接口速查

#### 登录认证

| 接口路径 | 方法 | 说明 |
|---------|------|------|
| /Login/doLogin | POST | 用户登录 |
| /Login/getUser | POST | 获取用户信息 |
| /Login/logOut | POST | 登出 |
| /Login/signOut | POST | 注销 |
| /Login/update | POST | 修改用户信息 |

#### 慢病申报

| 接口路径 | 方法 | 说明 |
|---------|------|------|
| /vipMbDeclareList/queryList | POST | 申报列表查询 |
| /vipMbDeclareList/saveVipMbdeclareInfo | POST | 保存申报信息 |
| /MbDeclare/query | POST | 申报查询 |
| /MbDeclareFirstTrial/queryMbDeclareListInFirstTrail | POST | 初审列表 |
| /MbDeclareExpertAssign/* | POST | 专家分配相关 |

#### 慢病备案

| 接口路径 | 方法 | 说明 |
|---------|------|------|
| /filingMan/queryFiling | POST | 备案查询 |
| /filingMan/filingBack | POST | 备案退回 |
| /MbYearCheck/querySl | POST | 年审查询 |

#### 处方管理

| 接口路径 | 方法 | 说明 |
|---------|------|------|
| /MbPrescription/* | POST | 处方相关操作 |
| /MbPrescriptionManagement/* | POST | 处方管理 |

#### 用户管理

| 接口路径 | 方法 | 说明 |
|---------|------|------|
| /MbUser/edit | POST | 用户编辑 |
| /MbUser/query | POST | 用户查询 |
| /MbUser/resetPassword | POST | 重置密码 |
| /MbUser/getRole | POST | 获取角色 |

#### 权限管理

| 接口路径 | 方法 | 说明 |
|---------|------|------|
| /privilege/user/* | POST | 用户权限 |
| /privilege/role/* | POST | 角色权限 |
| /privilege/org/* | POST | 机构权限 |
| /privilege/menu/* | POST | 菜单权限 |

---

## 10. 路由菜单总览

### 10.1 一级菜单分类

```
├── 系统管理 (6个页面)
│   ├── 用户管理
│   ├── 角色管理
│   ├── 模块管理
│   ├── 机构管理
│   ├── 日志审计
│   └── 接口鉴权管理
│
├── 慢病管理 (通用)
│   ├── 慢病备案
│   ├── 慢病初审管理
│   ├── 慢病体检分配
│   ├── 慢病专家分配
│   ├── 慢病申报查询
│   └── ...
│
├── 宝鸡慢病管理 (35个页面)
├── 延安慢病管理 (35个页面)
├── 商洛慢病管理 (36个页面)  ← 页面最多
├── 晋中慢病管理 (29个页面)
├── 榆林慢病管理 (12个页面)
├── 杨凌慢病管理 (11个页面)
├── 咸阳慢病管理 (9个页面)
├── 阜新慢病管理 (8个页面)
├── 晋城慢病管理 (8个页面)
├── 张家口慢病管理 (7个页面)
├── 九江慢病管理 (7个页面)
├── 定州慢病管理 (4个页面)
├── 满洲里慢病管理 (8个页面)
│
├── 快赔管理 (6个页面)
│   ├── 快速理赔申请
│   ├── 快速理赔授权
│   ├── 快速理赔结果查询
│   └── ...
│
├── 药店管理 (6个页面)
│   ├── 药店缴费
│   ├── 药店对账报表
│   └── ...
│
└── 医院管理 (4个页面)
    ├── 医院建卡
    ├── 挂号管理
    ├── 门诊缴费
    └── ...
```

### 10.2 常见业务流程页面

```
1️⃣ 申报流程
   慢病申报查询 → 申报录入 → 资料上传 → 提交申报

2️⃣ 审核流程
   初审列表 → 体检分配 → 专家分配 → 审核意见

3️⃣ 备案流程
   备案查询 → 备案信息 → 备案确认 → 完成备案

4️⃣ 年审流程
   年审管理 → 年审申请 → 年审审核

5️⃣ 支付流程
   消费记录 → 支付申请 → 支付确认
```

---

## 附录：开发指南

### A1. 如何新增API接口

```javascript
// 1. 在api目录下新建或编辑文件
// 2. 导入Axios实例
import axios from "./axios";

// 3. 编写接口方法
export const newApiMethod = (param) => {
    return axios.request({
        url: `/模块名/接口名`,
        data: param,
        method: "post"
    });
};

// 4. 在组件中使用
import { newApiMethod } from "@/api/apiXxx";
newApiMethod({ id: 1 }).then(res => {
    console.log(res);
});
```

### A2. 如何新增路由页面

```javascript
// 在 src/router/childrenRoutes.js 中添加
{
    path: `/newPage`,
    name: "newPage",
    meta: {
        ptitle: "所属菜单",
        title: "页面标题",
        pathName: "/newPage"
    },
    component: () => import("@/pages/xxx/NewPage")
}
```

### A3. 如何使用城市flag

```javascript
// 方式1：在API调用时传递
import axios from "./axios";

export const queryList = (param) => {
    return axios.request({
        url: `/vipMbDeclareList/queryList`,
        data: { ...param, flag: 2 },  // flag=2 商洛
        method: "post"
    });
};

// 方式2：从Vuex获取
let cityFlag = store.state.cityFlagSplit;
```

### A4. 环境配置

```javascript
// .env.development
NODE_ENV = development
domainName = ''              # 慢病业务域名
domainNameCenter = ''        # 通用中心域名
domainNamePower = ''         # 权限管理域名

// .env.production / .env.proMbReform
NODE_ENV = production
domainName = https://xxx.com
domainNameCenter = https://xxx.com
domainNamePower = https://xxx.com
```

---

*本文档由代码自动解析生成，如有疑问请联系项目维护团队。*
