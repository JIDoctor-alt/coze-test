# PICC门诊慢特病前端项目(picc-mzmtb-agent)全貌与架构深度解析

> 📌 **文档目标**：让零基础小白也能看懂这个Vue前端项目是怎么工作的  
> 📌 **项目定位**：门诊慢特病业务管理信息系统的前端Agent端（柜面业务系统）

---

## 目录导航
1. [项目全貌](#part1)
2. [架构深度解析](#part2)
3. [源码阅读指引](#part3)

---

# Part 1：项目全貌 🗺️

## 1.1 四服务对比表：前端Vue + 三个Java后端

想象一下，这个系统就像一家**大型医院的完整运作体系**：

| 角色 | 项目中的位置 | 比喻说明 | 核心技术 |
|------|-------------|---------|---------|
| **前台接待** | 前端Vue应用 (80/443端口) | 医院的导医台和各个科室窗口 | Vue 2.6 + Vuex + Vue Router + Ant Design Vue |
| **前台服务** | picc-mzmtb-gateway (9001端口) | 挂号收费处，统一登记患者信息 | Java微服务 + 网关路由 |
| **业务服务** | picc-mzmtb-auth (9091端口) | 各科室医生，处理具体业务 | Java业务逻辑 + GaussDB数据库 |
| **权限服务** | picc-mzmtb-user (9092端口) | 医院的人事部和保安，管理谁可以进哪个门 | Java权限管理 + 用户鉴权 |

### 服务调用流程图（比喻版）

```
🏥 患者（浏览器）
    ↓ 挂号
前台接待（前端Vue，端口80/443）
    ↓ 分诊
前台服务（网关，端口9001）- "您好，请到对应窗口"
    ↓ 医生接诊
业务服务（业务Java，端口9091）- "我去查查您的病历"
    ↓ 查询病历
数据库（GaussDB）- 病历档案室
    ↓
权限服务（权限Java，端口9092）- "让我确认下您的挂号单"
```

### 四服务详细职责

| 服务 | 服务名 | 端口 | 前缀路径 | 主要职责 |
|------|--------|------|----------|---------|
| 前端Vue | picc-mzmtb-agent | 80/443 | `/` | 页面展示、用户交互、表单处理 |
| 前台服务 | gateway | 9001 | `/mtbapi/mtb/gateway/` | 统一入口、路由分发、负载均衡 |
| 业务服务 | auth | 9091 | `/mbapi/` | 慢病申报、审核、体检、备案等核心业务 |
| 权限服务 | user | 9092 | `/mbjkglapi/` | 用户登录、菜单权限、角色管理 |

---

## 1.2 技术栈详解：Vue 2全家桶 + 工具库大礼包

### 核心技术三件套（Vue全家桶）

```
🍎 Vue 2.6：整个项目的"骨架"和"大脑"
   ├── 核心：响应式数据绑定 + 组件化开发
   ├── 模板语法：{{ }} 双括号插值，v-if/v-for指令
   └── 生命周期：created/mounted/updated/destroyed

🍎 Vuex 3：项目的"中央数据仓库"
   ├── 作用：所有组件共享的数据都存在这里
   ├── 核心概念：state(数据) + mutations(同步改数据) + actions(异步改数据)
   └── 持久化：vuex-persistedstate 插件让刷新不丢数据

🍎 Vue Router 3：项目的"导航系统"
   ├── 作用：决定用户访问哪个页面
   ├── 路由守卫：beforeEach 全局拦截，登录验证
   └── 懒加载：component: () => import() 按需加载页面
```

### UI框架：Ant Design Vue

> 💡 **Ant Design Vue** 就是一套现成的"装修材料"，别人已经设计好了按钮、表单、表格、弹窗长什么样，我们直接拿来用。

```javascript
// 引入方式（在 main.js 中）
import Antd from 'ant-design-vue';
Vue.use(Antd);

// 使用示例：表格组件
<a-table :dataSource="dataSource" :columns="columns" :pagination="false" />

// 使用示例：表单组件
<a-form :form="form" @submit="handleSubmit">
  <a-form-item label="用户名">
    <a-input v-model="username" />
  </a-form-item>
</a-form>
```

### 工具库全家福

| 工具库 | 用途 | 生活化比喻 |
|--------|------|-----------|
| **Axios** | HTTP请求库，发送API请求 | 就像"外卖小哥"，帮你把订单送到后厨，把饭菜带回来 |
| **Webpack** | 打包工具，编译Vue代码 | 像"厨师长"，把各种食材(JS/CSS/图片)加工成能上桌的菜(浏览器可执行文件) |
| **vue-i18n** | 国际化 | 像"同声传译"，中英文切换 |
| **vue-lazyload** | 图片懒加载 | 像"按需打印"，图片进入视野才加载 |
| **v-viewer** | 图片预览 | 像"放大镜"，点击图片可以放大查看 |
| **vue-layer** | 弹窗提示 | 像"服务员叫号"，各种提示弹窗 |
| **tinymce-vue** | 富文本编辑器 | 像"Word编辑器"，可以编辑带格式的文字 |
| **file-saver** | 文件下载 | 像"下载按钮"，保存文件到本地 |

### 加密与安全相关

| 工具库 | 用途 |
|--------|------|
| **crypto-js** | AES对称加密 |
| **jsencrypt** | RSA非对称加密 |
| **gm-crypt** | SM4国密加密（国产密码算法） |
| **md5** | MD5哈希，用于密码加密 |
| **js-base64** | Base64编码解码 |

### 数据处理相关

| 工具库 | 用途 |
|--------|------|
| **lodash** | JS工具库，数组/对象处理 |
| **accounting** | 金融数字格式化（如货币、百分比） |
| **decimal.js** | 精确数学运算（解决0.1+0.2≠0.3的问题） |

---

## 1.3 21个页面模块分析：按地市分类

> 💡 **"地市"是什么？**  
> 这个系统是为PICC（中国人保）在不同城市的分公司使用的。"地市"就是不同的城市，比如陕西的宝鸡、延安、榆林，山西的晋城，江西的九江等。

### 地市模块总览表

| 序号 | 地市代码 | 地市名称 | 主要模块 | 特殊功能 |
|------|---------|---------|---------|---------|
| 1 | 0 (默认) | 宝鸡 | 慢病管理、申报、体检、专家分配 | 最早建设的模块，基础功能最全 |
| 2 | 1 | 阜新 | 慢病申报导入、申报管理、初审、体检分配、专家分配、医生管理 | 独立的申报流程 |
| 3 | 2 | 商洛 | 慢病申报、备案、处方管理 | 处方管理是亮点 |
| 4 | 3 | 张家口 | 慢病管理、申报、备案、处方管理 | 河北地区 |
| 5 | 4 | 延安 | 慢病申报导入、申报管理、初审、体检、专家分配 | 陕北地区中心 |
| 6 | 5 | 汉中 | 慢病申报导入、申报管理、初审、体检、专家分配 | 陕南地区中心 |
| 7 | 6 | 定制地市 | 独立的业务模块 | 可配置化 |
| 8 | 7 | 榆林 | 申报录入、资料审核、专家分配、人员导入、处方管理、备案年审 | 功能最完善的地市之一 |
| 9 | 8 | 咸阳 | 申报录入、资料审核、专家分配、数据统计、处方管理 | 包含数据统计 |
| 10 | 10 | 咸阳 | 申报录入、专家分配 | 简化版咸阳 |
| 11 | 13 | 杨凌 | 申报录入、资料审核、专家分配、人员导入、处方管理、数据统计 | 农业示范区 |
| 12 | 15 | 九江 | 申报录入、资料审核、专家分配、资料脱敏、二次判定 | 包含资料脱敏 |
| 13 | 16 | 晋城 | 申报录入、资料审核、体检分配、专家分配、二次判定、资料脱敏 | 山西地区中心 |
| 14 | 17 | 咸阳(新) | 申报录入、资料审核、专家分配、数据统计、资料脱敏、处方管理 | 最新版本 |

### 核心业务模块功能详解

#### 📋 慢病申报管理（最核心的模块）
- **申报录入**：录入患者的基本信息、疾病类型、诊断证明等
- **资料审核**：初审医生审核提交的资料是否完整、真实
- **体检分配**：需要体检的患者，分配到哪个体检站点
- **专家分配**：资料审核通过后，分配给专家进行最终评审
- **专家二次判定**：对有争议的案例进行二次评审

#### 👤 人员管理模块
- **人员导入**：批量导入患者信息（Excel格式）
- **人员修改**：修改已有患者的信息
- **待发卡管理**：已经审核通过但还没发卡的患者
- **人卡绑定**：将慢病卡绑定到具体的人

#### 💊 处方管理
- **处方录入**：医生开具药品处方
- **处方查询**：查看历史处方
- **处方打印**：打印处方用于取药

#### 📊 查询与报表
- **申报综合查询**：查询各种申报记录
- **消费记录查询**：查询患者的消费明细
- **账户信息查询**：查询患者的账户余额、状态等
- **数据统计**：对业务数据进行统计分析

---

## 1.4 74个API文件按业务域分类

> 💡 **API文件是什么？**  
> 就像餐厅的"菜单"，每个API文件定义了能"点"哪些"菜"（接口），以及"菜"长什么样（参数和返回值）。

### API文件分类表

| 业务域 | 文件数量 | 主要功能 |
|--------|---------|---------|
| **申报管理** | 15个 | 慢病申报、修改申报、线下申报、申报查询 |
| **审核管理** | 5个 | 初审管理、复审管理、二次判定 |
| **体检专家** | 4个 | 体检分配、专家分配 |
| **人员管理** | 8个 | 用户管理、人员导入、人员修改、发卡管理 |
| **账户管理** | 6个 | 账户查询、消费记录、服务状态 |
| **处方管理** | 6个 | 处方录入、处方查询、处方导入 |
| **登录权限** | 4个 | 登录、登出、权限验证 |
| **快赔业务** | 5个 | 理赔申请、理赔授权 |
| **系统管理** | 6个 | 模块管理、角色管理、机构管理 |
| **医院药店** | 8个 | 医院建卡、挂号、缴费；药店缴费 |
| **其他业务** | 7个 | 备案管理、处方管理等 |

### 核心API文件说明

```javascript
// src/api/apiDeclare.js - 申报相关API
// 包含：申报列表查询、申报详情、新增申报、修改申报等

// src/api/apiAuditManagement.js - 审核管理API
// 包含：初审列表、审核通过/驳回、审核详情等

// src/api/apiLoginMb.js - 登录API
// 包含：用户名密码登录、手机验证码登录、获取用户信息等

// src/api/apiChronicDis.js - 慢病管理API
// 包含：慢病备案、备案查询、备案变更等

// src/api/apiUserManage.js - 用户管理API
// 包含：用户列表、用户新增、用户编辑、角色分配等
```

---

## 1.5 与后端三个服务的调用关系

### 调用关系全景图

```
┌─────────────────────────────────────────────────────────────────┐
│                         浏览器 (Browser)                         │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     前端Vue应用 (port 80/443)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Vuex Store │  │ Vue Router  │  │     Axios HTTP Client   │ │
│  │  (状态仓库)  │  │  (路由导航)  │  │      (网络请求)          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
            ┌───────────┐   ┌───────────┐   ┌───────────┐
            │ /mtbapi/  │   │  /mbapi/  │   │/mbjkglapi/│
            │ (网关)    │   │ (业务)    │   │ (权限)    │
            │  9001     │   │  9091     │   │  9092     │
            └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
                  │               │               │
                  ▼               ▼               ▼
          ┌───────────┐   ┌───────────┐   ┌───────────┐
          │ picc-      │   │ picc-      │   │ picc-      │
          │ mzmtb-     │   │ mzmtb-     │   │ mzmtb-     │
          │ gateway    │   │ auth       │   │ user       │
          │ (网关服务)  │   │ (业务服务)  │   │ (权限服务)  │
          └─────┬─────┘   └─────┬─────┘   └───────────┘
                │               │
                │               ▼
                │       ┌───────────┐
                │       │ GaussDB   │
                │       │ (数据库)   │
                │       └───────────┘
                │
                ▼
    ┌───────────────────┐
    │  /v2/ 路径切换逻辑 │
    │  根据flag参数判断  │
    │  走哪个版本接口    │
    └───────────────────┘
```

### Nginx代理配置详解

```nginx
# nginx-pro.conf 生产环境配置

# 1. 前端静态资源 - 根路径 "/" 
location / {
    root   /home/front/output;        # 前端构建产物目录
    index  index.html index.htm;
    try_files $uri $uri/ /index.html;  # SPA路由支持：找不到文件就返回index.html
}

# 2. 业务网关 - 所有业务请求走这里
location /mtbapi/mtb/gateway/ {
    proxy_pass http://10.34.124.201:10100/zt/mzmtb-ns-bzx-hw-k8s/picc-mzmtb-gateway/;
    # 转发真实IP，便于后端记录日志
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

# 3. 业务服务 - 核心业务逻辑
location /mbapi/ {
    proxy_pass http://10.34.124.201:10100/zt/mzmtb-ns-bzx-hw-k8s/picc-mzmtb-auth/;
}

# 4. 权限服务 - 登录和权限验证
location /mbjkglapi/ {
    proxy_pass http://10.34.124.201:10100/zt/mzmtb-ns-bzx-hw-k8s/picc-mzmtb-user/;
}

# 5. 图片服务 - 处方图片等
location /mtbapi/appimg/mtb/prd/bj/mbpres/ {
    proxy_pass http://10.34.92.150:9966/appimg/mtb/prd/bj/mbpres/;
}
```

---

# Part 2：架构深度解析 🔬

## 2.1 项目构建配置：Webpack + 多环境构建

### Webpack配置结构

```
build/
├── build.js              # 构建入口脚本
├── check-versions.js     # Node/npm版本检查
├── utils.js              # 工具函数（CSS处理、资源路径等）
├── vue-loader.conf.js    # Vue单文件组件加载器配置
├── webpack.base.conf.js  # 基础配置（所有环境共享）
├── webpack.dev.conf.js   # 开发环境配置
└── webpack.prod.conf.js  # 生产环境配置
```

### Webpack基础配置（webpack.base.conf.js）

```javascript
// 入口文件 - 从 main.js 开始构建
entry: {
  app: ['babel-polyfill', './src/main.js']  // babel-polyfill 兼容旧浏览器
},

// 输出配置
output: {
  path: config.build.assetsRoot,  // 输出到 output/ 目录
  filename: '[name].js',          // 入口文件名字不变
  chunkFilename: '[name].js',     // 异步加载的chunk名字
  publicPath: './'                 // 相对路径（支持多地市部署）
},

// 路径别名 - 方便 import 引用
resolve: {
  alias: {
    '@': resolve('src')            // @ 代表 src/ 目录
  }
}
```

### 五种环境构建命令

| 环境 | 构建命令 | NODE_ENV | env_config | 用途 |
|------|---------|----------|------------|------|
| 开发环境 | `npm run dev` | development | dev | 本地开发调试 |
| 测试环境 | `npm run test` | testing | test | 测试环境部署 |
| UAT环境 | `npm run uat` | uatMbReform | uatMbReform | 用户验收测试 |
| 生产环境 | `npm run production` | production | production | 正式环境 |
| 定制生产 | `npm run build:prod` | proMbReform | proMbReform | 定制版生产 |

### 生产构建优化（webpack.prod.conf.js）

```javascript
// 代码分割策略
optimization: {
  splitChunks: {
    cacheGroups: {
      vendor: {
        test: /[\\/]node_modules[\\/]/,  // 第三方库单独打包
        name: 'vendor',
        chunks: 'all'
      }
    }
  }
}

// UglifyJs压缩配置
new UglifyJsPlugin({
  uglifyOptions: {
    compress: {
      drop_debugger: true,           // 生产环境移除debugger
      drop_console: true,           // 生产环境移除console
    }
  }
})

// CSS提取和压缩
new MiniCssExtractPlugin({
  filename: 'css/[name].[contenthash:12].css'  // 带hash便于缓存
})
```

---

## 2.2 路由设计：Vue Router + 动态路由 + 权限路由

### 路由配置文件结构

```
src/router/
├── index.js           # 路由主入口（包含守卫）
└── childrenRoutes.js  # 子路由配置（所有页面路由）
```

### 路由模式：Hash模式

```javascript
// src/router/index.js
export const createRouter = () => new Router({
  mode: "hash",  // 使用hash模式，URL带 # 号
  // 例如：http://xxx.com/#/home/patientManage
  routes: [...]
})
```

> 💡 **为什么用Hash模式？**  
> 因为这个系统可能部署在不同的路径下，hash模式不需要服务器配置，直接在前端跳转即可。

### 静态路由（无需权限）

```javascript
export const staticRoutes = [
  {
    path: "/",
    redirect: "/loginMb"  // 根路径重定向到登录页
  },
  {
    path: "/loginMb",
    name: "loginMb",
    component: () => import("@/components/loginMb/index"),  // 登录页
    meta: { title: "门诊慢特病业务管理信息系统" }
  },
  {
    path: "/home",
    name: "home",
    component: () => import("@/pages/Home"),  // 主页框架
    children: [...childrenRoutes]              // 动态子路由
  }
]
```

### 路由守卫：登录验证

```javascript
// src/router/index.js
router.beforeEach((to, from, next) => {
  // 1. 修改页面标题
  if (to.meta.title) {
    document.title = to.meta.title;
  }
  
  // 2. 获取用户信息
  let logInfoMB = util.getUserInfo();
  
  // 3. 判断是否已登录
  if (!logInfoMB) {
    if (to.path == '/loginMb') {
      // 未登录但访问登录页，允许
      next();
    } else {
      // 未登录访问其他页面，跳转登录
      next('/loginMb');
    }
  } else {
    // 已登录，允许访问
    next();
  }
})
```

### 子路由配置（childrenRoutes.js）

```javascript
// 每个路由都是懒加载的（按需加载）
let childrenRoutes = [
  // 系统管理模块
  {
    path: `/systemUserManage`,
    name: "systemUserManage",
    meta: { ptitle: "系统管理", title: "用户管理" },
    component: () => import("@/pages/SystemView/systemUserManage"),
  },
  
  // 慢病管理模块（宝鸡默认）
  {
    path: "/diseaseDeclare",
    name: "diseaseDeclare",
    meta: { ptitle: "宝鸡慢病管理", title: "慢病申报查询" },
    component: () => import("@/pages/ChronicDis/diseaseDeclare"),
  },
  
  // 延安地市模块（带flag参数）
  {
    path: "/diseaseDeclare&flag=4",
    name: "diseaseDeclare&flag=4",
    meta: { ptitle: "延安慢病管理", title: "慢病申报查询" },
    component: () => import("@/pages/YAChronicDis/diseaseDeclare"),
  },
  
  // 更多地市...
]

export default childrenRoutes;
```

### 路由参数：flag地市标识

```javascript
// flag参数对照表
flag = 0 或不传 → 宝鸡（默认）
flag = 1         → 阜新
flag = 2         → 商洛
flag = 4         → 延安
flag = 7         → 榆林
flag = 8/10      → 咸阳
flag = 13        → 杨凌
flag = 15        → 九江
flag = 16        → 晋城
flag = 17        → 咸阳(新)
```

---

## 2.3 状态管理：Vuex Store设计

### Vuex模块结构

```
src/store/
├── index.js           # 主store入口
└── modules/
    ├── menu.js        # 菜单模块
    └── activeRouterMatch.js  # 路由匹配模块
```

### 主Store配置（src/store/index.js）

```javascript
import Vue from "vue";
import Vuex from "vuex";
import menu from "./modules/menu";
import createPersistedState from "vuex-persistedstate";

Vue.use(Vuex);

// 持久化配置：数据存储到sessionStorage
const createPersisted = createPersistedState({
  storage: window.sessionStorage,  // 刷新不丢数据
})

const store = new Vuex.Store({
  modules: {
    menu,
    activeRouterMatch
  },
  
  state: {
    // 标签页列表
    tabList: [],
    
    // 菜单是否折叠
    collapsed: false,
    
    // 用户Token
    token: "",
    
    // 地市标识
    cityFlagSplit: "",
    
    // 登录用户信息（需要解密后使用）
    userInfo: {},
    
    // 菜单数据（多套菜单）
    menuData: [...],      // 慢病管理菜单
    menuList: [...],      // 线下缴费菜单
    menuQuick: [...],     // 快赔菜单
    menuNewDeclare: [...], // 新申报菜单
    menuStore: [...],     // 药店菜单
    hospManage: [...],    // 医院管理菜单
  },
  
  mutations: {
    // 更新标签页
    updateTabList(state, tab) {
      state.tabList = tab;
    },
    
    // 切换菜单折叠状态
    updateCollapsed(state, collapsed) {
      state.collapsed = collapsed
    },
    
    // 更新Token
    updateToken(state, token) {
      state.token = token;
    },
    
    // 设置地市标识
    setOrgunitid(state, data) {
      state.DefaultOrgunitid = data
    }
  },
  
  plugins: [createPersisted]  // 启用持久化
})

export default store;
```

### 菜单模块（menu.js）

```javascript
export default {
  state: {
    menuCollapsed: true,      // 菜单是否折叠
    userInfo: {},             // 用户信息
    permissions: {},          // 用户权限
    menu: []                  // 用户菜单
  },
  
  mutations: {
    updateUserInfo(state, data) {
      // 更新用户信息和权限
      state.userInfo = {
        userName: data.userName,
        roleNames: data.roleNames,
      };
      // 将权限转成对象，便于快速查询
      let permissions = {};
      (data.menus || []).forEach((x) => {
        if (x.menuCode) {
          permissions[x.menuCode] = x;
        }
      });
      state.permissions = permissions;
    }
  }
}
```

---

## 2.4 网络请求层：Axios封装 + 拦截器 + Token刷新

### Axios封装文件

```
src/api/
├── axios.js          # 主Axios封装（业务请求）
├── axiosAuther.js    # 认证相关请求
├── axiosCenter.js    # 通用中心请求
├── axiosjkgl.js      # 权限管理请求
├── axiosPower.js     # 权限验证请求
└── apiList.js        # API接口列表
```

### 核心请求封装（axios.js）

```javascript
class HttpRequest {
  constructor() {
    this.queue = {};  // 请求队列，用于并发控制
  }
  
  // 创建Axios实例
  create() {
    return Axios.create({
      baseURL: process.env.domainName || '',
      withCredentials: true,  // 允许携带cookie
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "token": token
      }
    });
  }
  
  // 发送请求
  request(options) {
    let url = options.url;
    
    // 根据cityFlag决定是否使用v2接口
    if (cityFlag == '8' || cityFlag == '10' || ...) {
      url = '/v2' + url;  // 使用新版接口
    } else {
      url = url;  // 使用旧版接口
    }
    
    // 添加时间戳防止缓存
    options.url = url + "?_t=" + Math.random();
    
    return instance(options);
  }
}

export default new HttpRequest();
```

### 请求拦截器

```javascript
// 请求发送前
instance.interceptors.request.use(
  config => {
    // 1. AES加密敏感字段（姓名、身份证、手机号）
    config.data = this.encryptRequestFieldsWithAES(config.data, apiUrl);
    
    // 2. 从URL参数获取Token
    let query = location.href.split('?')[1];
    let token = qs.parse(query, { ignoreQueryPrefix: true })["token"];
    
    // 3. 设置请求头
    config.headers['Authorization'] = token;
    config.headers['userId'] = userId;
    config.headers['flag'] = flag;  // 地市标识
    
    return config;
  },
  error => Promise.reject(error)
);
```

### 响应拦截器

```javascript
// 响应返回后
instance.interceptors.response.use(
  res => {
    let data = res.data;
    
    // 1. AES解密敏感字段
    if (data.status === 0) {
      data = this.decryptSpecificFieldsWithAES(data);
    }
    
    // 2. 处理业务错误
    if (data.status !== 0 && data.status !== 200) {
      if (data.status === 999) {
        // Token过期，跳转登录
        window.sessionStorage.clear();
        Router.replace("/loginMb");
      }
      message.error(data.error || data.statusText);
      return Promise.reject(data);
    }
    
    return data;
  },
  error => {
    if (error.message.includes('timeout')) {
      message.error("服务请求超时，稍后重试");
    }
    return Promise.reject(error);
  }
);
```

### AES加密解密逻辑

> 💡 **为什么要加密？**  
> 敏感信息（姓名、身份证号、手机号）在网络上传输时需要加密，防止被窃取。

```javascript
// 加密白名单 - 只有这些接口的请求参数需要加密
const encryptRequestWhiteList = [
  '/vipMbDeclareList/queryList',
  '/MbDeclareFirstTrial/queryMbDeclareListInFirstTrail',
  '/vipMbDeclareList/saveVipMbdeclareInfo',
  // ... 更多接口
];

// 加密逻辑：对name、idcard、mobile字段进行AES加密
encryptRequestFieldsWithAES(data, apiUrl) {
  // 白名单检查
  if (!encryptRequestWhiteList.includes(apiUrl)) {
    return data;
  }
  
  // 对数据中的敏感字段加密
  if (data.name) {
    data.name = util.encrypt(data.name);
  }
  if (data.idcard) {
    data.idcard = util.encrypt(data.idcard);
  }
  
  return data;
}
```

---

## 2.5 国际化：vue-i18n配置

### i18n配置方式

项目使用 `vue-i18n` 8.x 版本，支持中英文切换：

```javascript
// 在 main.js 中引入
import Vue from 'vue';
import VueI18n from 'vue-i18n';

Vue.use(VueI18n);

// 创建i18n实例
const i18n = new VueI18n({
  locale: 'zh-CN',     // 默认语言
  fallbackLocale: 'zh-CN',
  messages: {
    'zh-CN': require('./i18n/zh-CN'),
    'en-US': require('./i18n/en-US')
  }
});

// 挂载到Vue
new Vue({
  i18n,
  router,
  store,
  render: h => h(App)
}).$mount('#app')
```

### 模板中使用

```vue
<!-- 在Vue组件中 -->
<template>
  <div>
    <span>{{ $t('menu.diseaseDeclare') }}</span>
    <a-button>{{ $t('button.submit') }}</a-button>
  </div>
</template>
```

---

## 2.6 登录与权限：登录流程 + 菜单权限 + 按钮权限

### 登录流程详解

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户输入账号密码                          │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      调用登录API (/mbjkglapi/Login/signIn)       │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    后端返回用户信息 + Token                       │
│     {                                                           │
│       userId: "1526095669060960256",                            │
│       token: "eyJhbGciOiJIUzI1NiJ9...",                          │
│       menus: [...],  // 用户菜单                                │
│       permissions: [...]  // 用户权限                           │
│     }                                                           │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              前端存储用户信息（加密后存sessionStorage）           │
│                                                                 │
│   sessionStorage.setItem('logInfoMB', encrypt(JSON.stringify({  │
│     userId, token, userName, menus...                            │
│   })))                                                          │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    跳转到主页 /home                              │
└─────────────────────────────────────────────────────────────────┘
```

### 登录页面（loginMb）

```vue
<!-- src/components/loginMb/index.vue -->
<template>
  <div class="loginForm">
    <a-form @submit="handleSubmit">
      <!-- 用户名 -->
      <a-form-item>
        <a-input v-decorator="['username', {rules: [{required: true}]}]" 
                 placeholder="请输入用户名" />
      </a-form-item>
      
      <!-- 密码 -->
      <a-form-item>
        <a-input type="password" v-decorator="['password']" 
                 placeholder="请输入密码" />
      </a-form-item>
      
      <!-- 手机号（自动获取） -->
      <a-form-item>
        <a-input :value="userMobile" disabled />
        <a-button @click="sendCode" :disabled="codeLoading">
          {{ codeButtonText }}
        </a-button>
      </a-form-item>
      
      <!-- 验证码 -->
      <a-form-item>
        <a-input v-decorator="['vcode']" placeholder="请输入验证码" />
      </a-form-item>
      
      <!-- 登录按钮 -->
      <a-button type="primary" html-type="submit" :loading="loading">
        登录
      </a-button>
    </a-form>
  </div>
</template>

<script>
export default {
  methods: {
    async handleSubmit() {
      // 1. 验证表单
      // 2. 调用登录API
      // 3. 存储Token和用户信息
      // 4. 跳转主页
    }
  }
}
</script>
```

### 权限控制

```javascript
// 按钮级别权限控制
export default {
  // 判断用户是否有某个权限
  hasPermission(permission) {
    let permissions = this.$store.state.menu.permissions;
    return !!permissions[permission];
  }
}

// 在组件中使用
<template>
  <div>
    <a-button v-if="hasPermission('disease:declare:add')">
      新增申报
    </a-button>
    <a-button v-if="hasPermission('disease:declare:edit')">
      编辑
    </a-button>
  </div>
</template>
```

---

## 2.7 地市差异化：21个地市页面如何复用和差异化

### 差异化策略：三级架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    第一级：基础通用组件                          │
│    src/components/                                              │
│    ├── commonHeader.vue      # 通用头部                         │
│    ├── comPrintTable/        # 打印组件                         │
│    └── comTable/             # 通用表格                         │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    第二级：业务通用模块                           │
│    src/pages/ChronicDis/                                        │
│    ├── diseaseDeclare.vue    # 慢病申报查询（宝鸡默认）          │
│    ├── auditManagement.vue   # 审核管理                         │
│    └── ...                                                     │
│                                                                 │
│    ※ 这些是"原型"，其他地市可以基于此修改                        │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    第三级：地市专用模块                           │
│    src/pages/YAChronicDis/    # 延安专用                        │
│    ├── diseaseDeclare.vue    # 继承+修改                        │
│    └── auditManagement.vue   # 继承+修改                        │
│                                                                 │
│    src/pages/JiJChronicDis/   # 九江专用                        │
│    ├── diseaseOfflineDeclare.vue  # 特有功能                    │
│    └── desensitization.vue   # 资料脱敏（九江特有）             │
└─────────────────────────────────────────────────────────────────┘
```

### 差异化实现方式

#### 方式1：路由级差异化（flag参数）

```javascript
// src/router/childrenRoutes.js

// 宝鸡默认
{
  path: "/diseaseDeclare",
  component: () => import("@/pages/ChronicDis/diseaseDeclare"),
}

// 延安专用
{
  path: "/diseaseDeclare&flag=4",
  component: () => import("@/pages/YAChronicDis/diseaseDeclare"),
}

// 九江专用
{
  path: "/diseaseDeclare&flag=15",
  component: () => import("@/pages/JiJChronicDis/diseaseOfflineDeclare"),
}
```

#### 方式2：组件内差异化（flag判断）

```javascript
export default {
  created() {
    // 从URL获取flag参数
    let query = location.href.split('?')[1];
    this.cityFlag = qs.parse(query, { ignoreQueryPrefix: true })["flag"];
    
    // 根据地市加载不同配置
    this.initConfig();
  },
  
  methods: {
    initConfig() {
      const configs = {
        '0': { title: '慢病申报', api: '/vipMbDeclareList/queryList' },
        '4': { title: '延安慢病申报', api: '/vipSxMbDeclare/SlMbCheck' },
        '7': { title: '榆林慢病申报', api: '/vipSxMbDeclare/YlMbCheck' },
        '15': { title: '九江慢病申报', api: '/vipSxMbDeclare/JjMbCheck' },
      };
      
      this.currentConfig = configs[this.cityFlag] || configs['0'];
    }
  }
}
```

#### 方式3：API级差异化

```javascript
// src/api/axios.js 中的逻辑
let v2List = ["/vipMbDeclareList/queryList"];
let nov2List = ["/MbUser/EditYh", ...];

if (cityFlag == '8' || cityFlag == '10' || ...) {
  // 这些地市用v2接口
  url = '/v2' + url;
} else if ((!cityFlag || cityFlag == '4') && v2List.includes(url)) {
  // 延安和默认用v2接口
  url = '/v2' + url;
}
```

### 各大地市特色功能

| 地市 | 特色功能 | 说明 |
|------|---------|------|
| 宝鸡(0) | 全功能 | 最早的版本，功能最全 |
| 延安(4) | 处方管理 | 处方录入、查询、打印 |
| 榆林(7) | 备案年审、处方管理 | 完整的备案+处方体系 |
| 九江(15) | 资料脱敏 | 专家审核时可以脱敏查看 |
| 晋城(16) | 体检分配 | 完整的体检流程 |
| 咸阳(17) | 数据统计 | 包含业务数据分析报表 |

---

## 2.8 Nginx部署配置：dev开发 + pro生产

### 开发环境配置（nginx-dev.conf）

```nginx
worker_processes  4;

events {
    worker_connections  1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;
    
    sendfile        on;
    keepalive_timeout  65;
    
    server {
        listen      80;
        server_name  localhost;
        
        # 前端静态资源
        location / {
            root   /home/front/output;
            index  index.html index.htm;
            try_files $uri $uri/ /index.html;
        }
        
        # UAT环境网关
        location /mtbapi/mtb/gateway/ {
            proxy_pass http://10.57.17.188:10100/zt/mbgl-uat-ns-btc-hw-k8s/picc-mzmtb-gateway/;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # UAT环境业务服务
        location /mbapi/ {
            proxy_pass http://10.57.17.188:10100/zt/mbgl-uat-ns-btc-hw-k8s/picc-mzmtb-auth/;
        }
        
        # UAT环境权限服务
        location /mbjkglapi/ {
            proxy_pass http://10.57.17.188:10100/zt/mbgl-uat-ns-btc-hw-k8s/picc-mzmtb-user/;
        }
        
        # 图片服务
        location /mtbapi/appimg/ {
            proxy_pass http://10.57.128.98:9966/appimg/;
        }
        
        # 文曲星处方识别（AI服务）
        location /policy/extractData {
            proxy_pass https://service.deltanlp.cspiccnet;
            client_max_body_size 50m;
        }
    }
}
```

### 生产环境配置（nginx-pro.conf）

```nginx
worker_processes  4;

events {
    worker_connections  1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;
    
    # 日志格式
    log_format  main  '$remote_addr - $remote_user [$time_local] '
                      'request="$request" status=$status bytes_sent=$bytes_sent '
                      'upstream_addr=$upstream_addr upstream_status=$upstream_status';
    
    sendfile        on;
    server_tokens off;  # 隐藏Nginx版本号
    keepalive_timeout  65;
    
    # ==================== HTTP服务 ====================
    server {
        listen      80;
        server_name  localhost;
        
        location / {
            root   /home/front/output;
            index  index.html index.htm;
            try_files $uri $uri/ /index.html;
        }
        
        # 生产网关
        location /mtbapi/mtb/gateway/ {
            proxy_pass http://10.34.124.201:10100/zt/mzmtb-ns-bzx-hw-k8s/picc-mzmtb-gateway/;
        }
        
        # 生产业务服务
        location /mbapi/ {
            proxy_pass http://10.34.124.201:10100/zt/mzmtb-ns-bzx-hw-k8s/picc-mzmtb-auth/;
        }
        
        # 生产权限服务
        location /mbjkglapi/ {
            proxy_pass http://10.34.124.201:10100/zt/mzmtb-ns-bzx-hw-k8s/picc-mzmtb-user/;
        }
    }
    
    # ==================== HTTPS服务 ====================
    server {
        listen       443 ssl;
        server_name  mtb.health.piccnet,mzmtb.picchealth.com,localhost;
        
        # SSL证书配置
        ssl_certificate      /home/front/ssl/_.picchealth.com_bundle.crt;
        ssl_certificate_key  /home/front/ssl/picchealth.com.key;
        ssl_session_cache    shared:SSL:1m;
        ssl_session_timeout  5m;
        ssl_ciphers  HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers  on;
        
        # 防止点击劫持
        add_header X-Frame-Options SAMEORIGIN;
        
        location / {
            root   /home/front/output;
            index  index.html index.htm;
            try_files $uri $uri/ /index.html;
        }
        
        # 与HTTP相同的代理配置...
    }
}
```

### 配置差异对比

| 配置项 | 开发环境 | 生产环境 |
|--------|---------|---------|
| 监听端口 | 80 | 80 + 443(HTTPS) |
| 后端地址 | 10.57.17.188 (UAT) | 10.34.124.201 (生产) |
| SSL证书 | 无 | 有 |
| 日志 | 注释掉 | 启用 |
| server_tokens | 默认 | off（隐藏版本） |
| 请求体大小 | 默认 | 50m（大文件上传） |

---

# Part 3：源码阅读指引 📖

## 3.1 核心文件速查表

| 文件路径 | 作用 | 关键代码量 | 阅读优先级 |
|---------|------|----------|----------|
| `src/main.js` | Vue应用入口 | 150行 | ⭐⭐⭐⭐⭐ |
| `src/router/index.js` | 路由配置和守卫 | 100行 | ⭐⭐⭐⭐⭐ |
| `src/router/childrenRoutes.js` | 所有页面路由 | 3000+行 | ⭐⭐⭐ |
| `src/store/index.js` | Vuex主配置 | 200行 | ⭐⭐⭐⭐ |
| `src/api/axios.js` | 网络请求封装 | 700+行 | ⭐⭐⭐⭐⭐ |
| `src/utils/util.js` | 工具函数 | 600+行 | ⭐⭐⭐ |
| `src/pages/Home.vue` | 主页框架 | 300行 | ⭐⭐⭐ |
| `src/components/loginMb/index.vue` | 登录页面 | 200行 | ⭐⭐⭐⭐ |

## 3.2 阅读顺序建议

### 入门路线（适合新加入项目的同学）

```
第1步：main.js
    ↓ 了解整个应用是怎么启动的

第2步：App.vue + Home.vue
    ↓ 了解页面整体布局结构

第3步：router/index.js
    ↓ 了解路由守卫（登录验证逻辑）

第4步：store/index.js
    ↓ 了解全局状态管理

第5步：找一个具体页面开始深入
    如：src/pages/ChronicDis/diseaseDeclare.vue
    ↓ 
    找到对应的API文件：src/api/apiDiseaseDeclare.js
```

### 进阶路线（适合想深入了解架构的同学）

```
第1步：api/axios.js
    ↓ 理解网络请求的封装逻辑

第2步：router/childrenRoutes.js
    ↓ 理解路由设计和地市差异化

第3步：utils/util.js
    ↓ 理解工具函数（加密解密、格式化等）

第4步：nginx-dev.conf / nginx-pro.conf
    ↓ 理解部署架构

第5步：package.json
    ↓ 理解项目依赖和构建命令
```

## 3.3 常用命令速查

```bash
# 进入项目目录
cd /tmp/picc-mzmtb-agent/

# 安装依赖
npm install

# 开发环境启动
npm run dev

# 测试环境构建
npm run test

# UAT环境构建
npm run uat

# 生产环境构建
npm run production

# ESLint代码检查
npm run lint

# 分析打包体积
npm run build --report
```

## 3.4 目录结构速览

```
picc-mzmtb-agent/
├── build/                    # Webpack构建配置
│   ├── webpack.base.conf.js # 基础配置
│   ├── webpack.dev.conf.js  # 开发配置
│   └── webpack.prod.conf.js # 生产配置
├── config/                   # 项目配置
│   ├── index.js             # 主配置（代理、路径等）
│   └── proxyConfig.js       # 代理配置
├── src/
│   ├── main.js             # Vue应用入口
│   ├── App.vue             # 根组件
│   ├── api/                # API请求封装（74个文件）
│   ├── assets/             # 静态资源（图片、样式）
│   ├── components/         # 公共组件
│   │   ├── loginMb/       # 登录组件
│   │   ├── header.vue     # 头部组件
│   │   └── index.js       # 组件全局注册
│   ├── mock/              # Mock数据
│   ├── pages/             # 页面组件（21个地市模块）
│   │   ├── Home.vue       # 主页
│   │   ├── ChronicDis/    # 宝鸡慢病（默认）
│   │   ├── YAChronicDis/  # 延安慢病
│   │   ├── YLChronicDis/  # 榆林慢病
│   │   ├── SLChronicDis/  # 商洛慢病
│   │   ├── JiJChronicDis/ # 九江慢病
│   │   ├── JCChronicDis/  # 晋城慢病
│   │   └── ...            # 更多地市
│   ├── router/             # 路由配置
│   │   ├── index.js       # 路由主入口+守卫
│   │   └── childrenRoutes.js # 子路由
│   ├── store/             # Vuex状态管理
│   │   ├── index.js       # 主Store
│   │   └── modules/       # Store模块
│   └── utils/             # 工具函数
│       ├── util.js        # 通用工具
│       ├── fileDownload.js # 文件下载
│       ├── enum.js        # 枚举定义
│       └── tableMixins.js  # 表格混入
├── nginx-dev.conf         # 开发Nginx配置
├── nginx-pro.conf         # 生产Nginx配置
├── package.json           # 项目依赖
└── README.md              # 项目说明
```

---

## 3.5 快速定位技巧

### 查找某个页面组件

```bash
# 方法1：通过路由名称查找
grep -r "diseaseDeclare" src/router/

# 方法2：通过页面标题查找
grep -r "慢病申报查询" src/router/

# 方法3：直接查看pages目录
ls src/pages/
```

### 查找某个API接口

```bash
# 在API文件中搜索
grep -r "queryList" src/api/

# 查看具体的API文件
cat src/api/apiDiseaseDeclare.js
```

### 查找某个工具函数

```bash
# 在util.js中搜索
grep -r "encrypt" src/utils/util.js

# 查看完整的util.js
cat src/utils/util.js
```

---

## 3.6 常见问题排查

### 问题1：页面空白或404
```
排查步骤：
1. 检查浏览器控制台是否有报错
2. 检查Nginx配置是否正确
3. 检查路由是否正确注册
4. 检查API请求是否正常
```

### 问题2：登录后跳转回登录页
```
排查步骤：
1. 检查Token是否正确获取
2. 检查sessionStorage是否正常存储
3. 检查路由守卫逻辑
4. 检查util.getUserInfo()方法
```

### 问题3：接口请求失败
```
排查步骤：
1. 检查接口路径是否正确
2. 检查flag参数是否正确
3. 检查Nginx代理配置
4. 查看浏览器Network面板的请求详情
```

### 问题4：数据加密解密异常
```
排查步骤：
1. 检查AES密钥是否一致
2. 检查加密白名单配置
3. 查看控制台warn日志
4. 对比前后端加密逻辑
```

---

# 附录：术语对照表 📚

| 术语 | 全称 | 通俗解释 |
|------|------|---------|
| Vue | Vue.js | 一个用于构建用户界面的渐进式JavaScript框架 |
| Vuex | Vuex | Vue的状态管理模式，集中管理组件共享状态 |
| Vue Router | Vue Router | Vue官方路由管理器 |
| Axios | Axios | 基于Promise的HTTP客户端，用于浏览器发送请求 |
| Webpack | Webpack | 模块打包器，把各种资源打包成浏览器能识别的文件 |
| Ant Design Vue | Ant Design Vue | 蚂蚁金服开源的Vue UI组件库 |
| SPA | Single Page Application | 单页应用，整个应用只有一个HTML页面 |
| Token | Token | 用户身份凭证，类似于"入场券" |
| flag | Flag | 标识参数，用于区分不同地市/业务 |
| API | Application Programming Interface | 应用程序编程接口，后端暴露给前端调用的接口 |

---

> 📝 **文档版本**：v1.0  
> 📅 **最后更新**：2024年  
> 👤 **维护者**：PICC前端团队  
> 
> 💡 **温馨提示**：本项目涉及多个地市定制开发，修改前请务必确认影响范围！
