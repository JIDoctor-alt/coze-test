> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC门诊慢特病前端项目 (picc-mzmtb-agent) Vuex状态管理深度解析

> 项目技术栈：Vue 2.6 + Vuex 3 + Vue Router 3  
> 文档生成时间：2024年  
> 解析版本：完整版

---

## 📖 前言：Vuex零基础小白化解读

在开始深入分析之前，让我们用"超市仓库"的比喻来理解Vuex的核心概念：

| 概念 | 超市比喻 | 人话解释 |
|------|---------|---------|
| **Vuex** | 超市的共享仓库 | 所有柜台（组件）都能存取货（数据）的地方 |
| **State** | 仓库里的货架 | 存放数据的地方，如商品库存、会员信息 |
| **Getter** | 仓库管理员 | 帮你找货的人，比如"帮我查下某商品还剩多少" |
| **Mutation** | 入库/出库登记簿 | 每次操作都要登记，这是同步的操作记录 |
| **Action** | 采购员 | 去外面（API接口）进货后交给仓库管理员登记，可以做异步操作 |
| **Module** | 仓库分区 | 把仓库分成食品区/日用品区/家电区，方便管理 |
| **持久化** | 仓库装了监控 | 断电（刷新页面）也不丢记录，数据会保存到sessionStorage/localStorage |

---

## Part 1：Vuex Store结构分析

### 1.1 目录结构

```
src/store/
├── index.js                 # 主入口文件 (575行)
└── modules/
    ├── activeRouterMatch.js # 动态路由匹配模块 (65行)
    └── menu.js             # 菜单与权限模块 (124行)
```

### 1.2 Store架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        Vuex Store (根Store)                      │
├─────────────────────────────────────────────────────────────────┤
│  plugins: [createPersistedState] ← 使用sessionStorage持久化      │
├─────────────────────────────────────────────────────────────────┤
│  modules:                                                        │
│  ┌─────────────────────┐  ┌─────────────────────────────┐      │
│  │   menu 模块          │  │   activeRouterMatch 模块     │      │
│  │   (命名空间: menu)   │  │   (命名空间: activeRouterMatch)│      │
│  ├─────────────────────┤  ├─────────────────────────────┤      │
│  │ - state             │  │ - state                     │      │
│  │   · menuCollapsed   │  │   · homeMenus              │      │
│  │   · userInfo        │  ├─────────────────────────────┤      │
│  │   · sysPermission   │  │ - mutations                 │      │
│  │   · permissions     │  │   · setMenus               │      │
│  │   · menu            │  ├─────────────────────────────┤      │
│  ├─────────────────────┤  │ - actions                  │      │
│  │ - mutations         │  │   · getRoleMenusAsync      │      │
│  │   · toggleMenu      │  └─────────────────────────────┘      │
│  │   · updateMenu      │                                        │
│  │   · updateUserInfo  │                                        │
│  ├─────────────────────┤                                        │
│  │ - actions           │                                        │
│  │   · toggleMenu      │                                        │
│  ├─────────────────────┤                                        │
│  │ - getters           │                                        │
│  │   · menuCollapsed   │                                        │
│  │   · userInfo        │                                        │
│  │   · permissions     │                                        │
│  │   · menu            │                                        │
│  └─────────────────────┘                                        │
├─────────────────────────────────────────────────────────────────┤
│  根State (直接挂在根Store上):                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ pageUrl, showType, ActionStr, token, afterRouter        │    │
│  │ cityFlagSplit, DefaultOrgunitid, systemData             │    │
│  │ menuData, menuList, menuDeclare, menuQuick              │    │
│  │ menuNewDeclare, menuStore, hospManage                   │    │
│  │ selectData, systemClassB, tabList, collapsed           │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│  根Mutations:                                                    │
│  updateCollapsed, updateTabList, updateState, updateShowType      │
│  updateMenu, updateToken, updateActionStr, updateSelectData       │
│  updateSystemClassB, saveAfterRouter, setOrgunitid               │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 持久化配置分析

```javascript
// 使用vuex-persistedstate插件
import createPersistedState from "vuex-persistedstate";

const createPersisted = createPersistedState({
  storage: window.sessionStorage,  // ⚠️ 使用sessionStorage，不是localStorage
});

// ⚠️ 重要问题：这里createPersisted被创建但没有传入任何参数！
// 这意味着默认会持久化所有state到sessionStorage
```

**⚠️ 潜在问题**：未指定paths，意味着所有state都会被持久化，包括可能不需要持久化的大对象。

---

## Part 2：每个Vuex Module详解

### 2.1 根Store (index.js)

#### 2.1.1 State字段表

| 字段名 | 类型 | 默认值 | 人话解释 |
|--------|------|--------|----------|
| `pageUrl` | String | `"http://www.baidu.com"` | 页面URL配置（硬编码，应动态化） |
| `showType` | String | `"router"` | 展示类型，控制页面渲染方式 |
| `ActionStr` | Array | `[]` | 操作权限字符串数组 |
| `token` | String | `""` | 用户认证令牌 |
| `afterRouter` | String | `""` | 路由切换后的路径记录 |
| `cityFlagSplit` | String | `""` | 地市标识分割标记 |
| `DefaultOrgunitid` | Any | `null` | 默认机构单元ID（用于地市切换） |
| `systemData` | Array | 见代码 | 系统管理菜单数据（硬编码） |
| `menuData` | Array | 见代码 | 慢病管理完整菜单树（硬编码，⚠️很大） |
| `menuList` | Array | 见代码 | 一卡通菜单列表 |
| `menuDeclare` | Array | 见代码 | 申报查询菜单（医生/专家） |
| `menuQuick` | Array | 见代码 | 快赔相关菜单 |
| `menuNewDeclare` | Array | 见代码 | 阜新慢病新申报菜单 |
| `menuStore` | Array | 见代码 | 药店菜单 |
| `hospManage` | Array | 见代码 | 医院管理菜单 |
| `selectData` | Array | `[]` | 下拉选择框数据缓存 |
| `systemClassB` | Object | `{module_name, toUrl}` | 系统分类B |
| `tabList` | Array | `[]` | 标签页列表（多标签页功能） |
| `collapsed` | Boolean | `false` | 菜单是否折叠 |

#### 2.1.2 根Mutations表

| Mutation名称 | 参数 | 作用 | 调用位置 |
|-------------|------|------|----------|
| `updateCollapsed` | `collapsed` (Boolean) | 更新菜单折叠状态 | Home.vue - collapsedChange() |
| `updateTabList` | `tab` (Array) | 更新标签页列表 | Home.vue - remove() |
| `updateState` | `pageUrl` (String) | 更新页面URL | Home.vue - pageChange() |
| `updateShowType` | `showType` (String) | 更新展示类型 | Home.vue - showTypeChange() |
| `updateMenu` | `newMenu` (Array) | 更新menuData | 待查 |
| `updateToken` | `token` (String) | 更新Token | 登录逻辑 |
| `updateActionStr` | `ActionStr` (Array) | 更新操作权限字符串 | - |
| `updateSelectData` | `selectData` (Array) | 更新下拉选择数据 | - |
| `updateSystemClassB` | `systemClassB` (Object) | 更新系统分类B | - |
| `saveAfterRouter` | `router` (String) | 保存路由后的路径 | - |
| `setOrgunitid` | `data` (Any) | 设置默认机构ID | 地市切换逻辑 |

#### 2.1.3 根Getters（无显式定义）

根Store没有定义getters，所有state都是直接访问。

#### 2.1.4 根Actions（无显式定义）

根Store没有定义actions，所有操作都通过mutations直接提交。

---

### 2.2 menu模块详解

**模块路径**: `src/store/modules/menu.js`  
**命名空间**: `menu`（默认开启）

#### 2.2.1 模块名与人话解释

```
模块名: menu
人话解释: "这个模块负责管理侧边栏菜单的展示状态、用户登录信息、权限数据"
```

#### 2.2.2 State字段表

| 字段名 | 类型 | 默认值 | 人话解释 |
|--------|------|--------|----------|
| `menuCollapsed` | Boolean | `true` | 菜单是否折叠状态 |
| `userInfo` | Object | `{}` | 用户信息（部门、角色、用户名等） |
| `sysPermission` | Boolean | `true` | 系统权限总开关 |
| `permissions` | Object | `{}` | 权限映射表（menuCode → 权限对象） |
| `menu` | Array | `[]` | 动态构建的菜单列表 |

#### 2.2.3 Getters表

| Getter名称 | 返回值 | 用途 |
|-----------|--------|------|
| `menuCollapsed` | `state.menuCollapsed` | 获取菜单折叠状态 |
| `userInfo` | `state.userInfo` | 获取用户信息 |
| `sysPermission` | `state.sysPermission` | 获取系统权限状态 |
| `permissions` | `state.permissions` | 获取权限映射表 |
| `menu` | `state.menu` | 获取动态菜单列表 |

#### 2.2.4 Mutations表

| Mutation名称 | 参数 | 作用 | 调用位置 |
|-------------|------|------|----------|
| `toggleMenu` | 无 | 切换菜单折叠状态 | actions.toggleMenu |
| `updateMenu` | `data` (Array) | 根据权限码动态构建菜单 | 登录后初始化 |
| `updateUserInfo` | `data` (Object) | 更新用户信息和权限映射 | 登录后初始化 |

#### 2.2.5 Actions表

| Action名称 | 异步操作 | 调用的API | commit的mutations |
|-----------|---------|----------|-------------------|
| `toggleMenu` | 否 | 无 | `toggleMenu` |

#### 2.2.6 updateMenu mutation 逻辑详解

```javascript
// 这个mutation做了复杂的菜单过滤和重组
updateMenu(state, data) {
    let hasProblem = false;  // 是否有问题管理权限
    let hasStatics = false;  // 是否有数据报告权限
    let menus = [];
    
    // 第一遍遍历：检测是否有人问题管理和数据报告的权限
    data.forEach((ele) => {
        if (ele.menuCode == 'problems_all' || ...) {
            hasProblem = true;
        }
        if (ele.menuCode == 'problems_deptCount' || ...) {
            hasStatics = true;
        }
    });
    
    // 第二遍遍历：根据权限码重组菜单结构
    data.forEach((ele) => {
        // 根据不同的menuCode构建不同的菜单项
    });
    
    state.menu = menus;
}
```

---

### 2.3 activeRouterMatch模块详解

**模块路径**: `src/store/modules/activeRouterMatch.js`  
**命名空间**: `activeRouterMatch`（默认开启）

#### 2.3.1 模块名与人话解释

```
模块名: activeRouterMatch
人话解释: "这个模块负责根据用户权限动态生成和匹配路由，实现权限控制"
```

#### 2.3.2 State字段表

| 字段名 | 类型 | 默认值 | 人话解释 |
|--------|------|--------|----------|
| `homeMenus` | Array | `[]` | 用户的菜单权限数据（来自登录返回） |

#### 2.3.3 Mutations表

| Mutation名称 | 参数 | 作用 |
|-------------|------|------|
| `setMenus` | `data` (Array) | 设置用户菜单权限数据 |

#### 2.3.4 Actions表

| Action名称 | 异步操作 | 调用的API | commit的mutations |
|-----------|---------|----------|-------------------|
| `getRoleMenusAsync` | 是 | 无（从sessionStorage获取） | `setMenus` |

#### 2.3.5 getRoleMenusAsync 逻辑详解

```javascript
getRoleMenusAsync(store) {
    return new Promise(resolve => {
        // 1. 从sessionStorage获取用户信息
        let logInfoMB = util.getUserInfo();
        
        if(logInfoMB) {
            // 2. 获取用户权限菜单
            var menusData = logInfoMB.menus;
            var addRoutes = [];
            var staticMenus = [...staticRoutes[1].children];
            
            // 3. 保存菜单到state
            store.commit('setMenus', menusData);
            
            // 4. 根据环境决定是否需要动态路由
            if (process.env.NODE_ENV != 'development') {
                // 生产/测试环境：遍历权限菜单，匹配静态路由
                for(let i = 0; i < menusData.length; i++) {
                    for(let j = 0; j < menusData[i].children.length; j++) {
                        let urlArr = menusData[i].children[j].url.split('/');
                        menusData[i].children[j].menuKey = urlArr[urlArr.length - 1];
                        let oneRouter = staticMenus.find(item => item.name == urlArr[urlArr.length - 1]);
                        oneRouter !== undefined ? addRoutes.push(oneRouter) : "";
                    }
                }
            } else {
                // 开发环境：绕过权限控制，使用全部静态路由
                addRoutes = [...staticMenus];
            }
            
            // 5. 重置路由matcher（清除现有路由）
            router.matcher = createRouter().matcher;
            
            // 6. 动态添加路由
            addRoutes.forEach(val => {
                router.addRoute('home', val);
            });
            
            // 7. 添加404路由
            router.addRoute({
                path: "*",
                name: "404",
                component: () => import("@/pages/404")
            });
            
            resolve();
        }
    });
}
```

---

## Part 3：状态流转分析

### 3.1 用户登录→Token存储→权限加载→菜单生成的完整数据流

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           登录流程数据流                                      │
└─────────────────────────────────────────────────────────────────────────────┘

[用户输入账号密码]
        │
        ▼
┌─────────────────┐
│  登录接口调用     │
│  (apiLoginMb)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  登录成功后返回的数据结构:                                                    │
│  {                                                                           │
│    status: 0,                                                               │
│    data: {                                                                   │
│      userId: "xxx",                                                         │
│      userName: "张三",                                                      │
│      token: "eyJhbGciOiJIUzI1NiIs...",                                      │
│      menus: [                                                               │
│        { menuCode: "problems_all", menuName: "问题池", ... },               │
│        { menuCode: "problems_todo", menuName: "待我处理", ... },            │
│        ...                                                                   │
│      ],                                                                     │
│      roles: [...],                                                          │
│      roleNames: "管理员",                                                   │
│      deptId: "xxx",                                                         │
│      email: "xxx@xxx.com"                                                   │
│    }                                                                         │
│  }                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  util.js - getUserInfo() 实现:                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ let getUserInfo = () => {                                           │    │
│  │   let logInfoMB = null;                                             │    │
│  │   // 1. 从sessionStorage获取加密的用户信息                           │    │
│  │   if (sessionStorage.getItem("logInfoMB")) {                        │    │
│  │     // 2. AES解密后JSON.parse                                        │    │
│  │     logInfoMB = JSON.parse(decrypt(sessionStorage.getItem("logInfoMB")));│  │
│  │   }                                                                  │    │
│  │   return logInfoMB                                                   │    │
│  │ }                                                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  数据存储位置1: sessionStorage (⚠️非Vuex)                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Key: "logInfoMB"                                                     │    │
│  │ Value: AES(JSON.stringify(userData))                                 │    │
│  │ 持久化到sessionStorage，刷新页面不丢失，但关闭浏览器会清除              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                            │
│  数据存储位置2: Vuex Store (通过vuex-persistedstate)                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ state.token = "eyJhbGciOiJIUzI1NiIs..."                              │    │
│  │ state.ActionStr = [...]                                             │    │
│  │ (其他state根据默认配置也会被持久化)                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  axios请求拦截器中的Token读取 (axios.js):                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ instance.interceptors.request.use(config => {                       │    │
│  │   // 从URL参数或sessionStorage获取token                              │    │
│  │   let logInfoMB = util.getUserInfo();                                │    │
│  │   if(logInfoMB){                                                     │    │
│  │     token = logInfoMB.token                                         │    │
│  │   }                                                                  │    │
│  │   config.headers.common['Authorization'] = token                    │    │
│  │   config.headers['token'] = token                                   │    │
│  │   return config;                                                    │    │
│  │ })                                                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  动态路由生成 (activeRouterMatch.js):                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ 1. 获取用户菜单权限: logInfoMB.menus                                 │    │
│  │ 2. 遍历权限菜单，匹配静态路由                                         │    │
│  │ 3. 调用 router.addRoute() 动态添加路由                               │    │
│  │ 4. 重置 router.matcher 清除旧路由                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                            │
│  菜单数据更新 (menu.js):                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ 1. commit('updateUserInfo', userData) - 更新用户信息               │    │
│  │ 2. commit('updateMenu', menus) - 根据权限码构建菜单                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Home.vue组件消费状态:                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ computed: {                                                          │    │
│  │   ...mapState({                                                      │    │
│  │     showType: state => state.showType,                               │    │
│  │     menuData: state => state.menuData,                               │    │
│  │     tabList: state => state.tabList,                                 │    │
│  │     collapsed: state => state.collapsed                              │    │
│  │   })                                                                  │    │
│  │ }                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 地市切换的状态管理

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           地市切换状态管理                                    │
└─────────────────────────────────────────────────────────────────────────────┘

【问题背景】
项目支持多地市（宝鸡、阜新、商洛、延安等），不同地市有不同的业务逻辑和菜单。

【状态字段】
┌─────────────────────────────────────────────────────────────────────────────┐
│ state.cityFlagSplit     - 地市标识分割标记                                  │
│ state.DefaultOrgunitid  - 默认机构单元ID                                    │
│ state.menuData          - 当前地市的菜单数据（硬编码了大量地市菜单）         │
│ state.menuNewDeclare    - 阜新慢病新申报菜单                                │
│ state.hospManage        - 医院管理菜单                                      │
└─────────────────────────────────────────────────────────────────────────────┘

【切换逻辑】
┌─────────────────────────────────────────────────────────────────────────────┐
│ axios.js 请求拦截器:                                                         │
│ ┌───────────────────────────────────────────────────────────────────────┐  │
│ │ let cityFlag = qs.parse(query, { ignoreQueryPrefix: true })["flag"]; │  │
│ │ // flag: 0=宝鸡, 1=阜新, 2=商洛, 4=延安                               │  │
│ │ config.headers['flag'] = flag || 0;                                   │  │
│ └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│ index.js mutation:                                                           │
│ ┌───────────────────────────────────────────────────────────────────────┐  │
│ │ setOrgunitid(state, data) {                                           │  │
│ │   state.DefaultOrgunitid = data;  // 保存地市机构ID                    │  │
│ │ }                                                                     │  │
│ └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘

【⚠️ 问题】
1. 地市标识通过URL参数传递，存在安全风险
2. menuData硬编码了所有地市的菜单，应该动态从后端获取
3. 地市切换没有完整的退出登录→重新登录→重新加载数据流程
```

### 3.3 表单数据在Vuex中的流转

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           表单数据流转分析                                    │
└─────────────────────────────────────────────────────────────────────────────┘

【当前项目表单数据管理模式】

┌─────────────────────────────────────────────────────────────────────────────┐
│ 模式1: 组件本地状态 (推荐，大多数页面使用)                                    │
│ ┌───────────────────────────────────────────────────────────────────────┐  │
│ │ export default {                                                      │  │
│ │   data() {                                                            │  │
│ │     return {                                                           │  │
│ │       form: { name: '', idCard: '', ... }  // 表单数据在组件内管理     │  │
│ │     }                                                                 │  │
│ │   }                                                                   │  │
│ │ }                                                                     │  │
│ └───────────────────────────────────────────────────────────────────────┘  │
│ ✅ 优点: 数据流清晰，组件自治                                               │
│ ✅ 优点: 避免Vuex膨胀                                                      │
│ ✅ 适合: 大部分业务表单                                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 模式2: Vuex状态管理 (少数场景)                                               │
│ ┌───────────────────────────────────────────────────────────────────────┐  │
│ │ state.selectData = []  // 下拉选择框数据缓存                          │  │
│ │ state.tabList = []     // 标签页数据                                  │  │
│ └───────────────────────────────────────────────────────────────────────┘  │
│ ⚠️ 问题: selectData被持久化，可能造成数据过期                                │
└─────────────────────────────────────────────────────────────────────────────┘

【tableMixins.js - 表格混入】
┌─────────────────────────────────────────────────────────────────────────────┐
│ 路径: src/utils/tableMixins.js (约1400行)                                   │
│ 功能: 提供表格的通用逻辑混入                                                │
│ 内容: 分页、搜索、筛选、导出等通用功能                                       │
│ ⚠️ 注意: 表单数据不在Vuex中管理，通过mixin共享                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 4：性能问题分析

### 4.1 哪些State过大？

| State字段 | 估计大小 | 问题描述 |
|-----------|---------|----------|
| `menuData` | ~50KB | 硬编码了大量菜单结构，包含完整的菜单树 |
| `systemData` | ~2KB | 硬编码的系统管理菜单 |
| `menuList` | ~5KB | 一卡通菜单列表 |
| `menuNewDeclare` | ~8KB | 阜新慢病菜单 |
| `hospManage` | ~3KB | 医院管理菜单 |
| `permissions` | 动态 | 根据用户权限动态构建，可能是空对象或包含大量权限 |

**⚠️ 严重问题**: `menuData`等菜单数据是硬编码的，每次都会持久化到sessionStorage，即使这些数据不需要根据用户变化也应被持久化。

### 4.2 是否有不需要持久化的数据被持久化了？

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              持久化问题分析                                   │
└─────────────────────────────────────────────────────────────────────────────┘

【应该持久化的数据】✅
├── token                          - 用户认证令牌，刷新页面需要保持
├── userInfo (在menu模块)          - 用户基本信息
├── menuCollapsed                  - 菜单折叠状态（用户体验）
└── permissions                    - 权限映射

【不应该持久化的数据】❌
├── pageUrl                        - 页面URL，每次访问可能不同
├── showType                       - 展示类型，会话级状态
├── ActionStr                      - 操作权限字符串，应每次从服务器获取
├── afterRouter                    - 路由记录，临时状态
├── cityFlagSplit                  - 地市标记，应从URL/服务器获取
├── DefaultOrgunitid               - 机构ID，应从登录响应获取
├── systemData                     - 系统菜单，硬编码数据不应持久化
├── menuData                       - 菜单数据，应从后端API获取或静态定义
├── menuList/menuDeclare/menuQuick  - 菜单数据，应动态加载
├── selectData                     - 下拉数据，可能过期
├── systemClassB                   - 系统分类，硬编码数据
├── tabList                        - ⚠️ 争议：标签页数据是否需要保持？
└── collapsed                      - 菜单折叠状态，可选

【当前配置问题】
createPersistedState({
  storage: window.sessionStorage,
  // ⚠️ 没有指定paths，默认持久化所有state
})

【应该的配置】
createPersistedState({
  storage: window.sessionStorage,
  paths: ['token', 'menu.menuCollapsed', 'menu.userInfo', 'menu.permissions', 'tabList', 'collapsed']
})
```

### 4.3 哪些Getter计算过重？

| Getter | 问题描述 | 学习要点 |
|--------|----------|----------|
| 无显式getters | 根Store直接访问state，没有缓存计算 | 建议添加getters用于派生数据 |
| `menu.updateMenu` | mutation中双重遍历权限数组构建菜单 | 可移到getter中惰性计算 |
| `menu.updateUserInfo` | 每次调用都重新构建permissions映射 | 可优化为增量更新 |

### 4.4 模块是否需要懒加载？

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              模块懒加载分析                                   │
└─────────────────────────────────────────────────────────────────────────────┘

【当前模块加载方式】
┌─────────────────────────────────────────────────────────────────────────────┐
│ store/index.js:                                                             │
│ ┌───────────────────────────────────────────────────────────────────────┐  │
│ │ const store = new Vuex.Store({                                        │  │
│ │   modules: {                                                          │  │
│ │     menu,                      // 同步加载                            │  │
│ │     activeRouterMatch          // 同步加载                            │  │
│ │   },                                                                   │  │
│ │   ...                                                                 │  │
│ │ });                                                                   │  │
│ └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘

【分析】
├── menu模块                  - 小型模块，可同步加载 ✅
├── activeRouterMatch模块    - 小型模块，可同步加载 ✅
└── 根state                  - 大量硬编码数据，可考虑拆分 ⚠️

【建议】
1. 将硬编码的菜单数据移到单独的配置文件，按需加载
2. 考虑将activeRouterMatch的action改为动态导入
```

### 4.5 其他性能问题

| 问题 | 描述 | 影响 |
|------|------|------|
| 硬编码菜单数据 | menuData等包含大量硬编码菜单结构 | 增加bundle大小，每次都需解析 |
| AES加密存储 | 使用AES加密logInfoMB再存sessionStorage | 增加CPU开销，每次读取都要解密 |
| 无模块化拆分 | 所有状态都在根Store和少数几个模块中 | 难以维护，状态逻辑混杂 |
| 无命名空间规范 | 部分模块混用命名空间和非命名空间 | 调用方式不一致 |

---

## Part 5：学习要点

### 5.1 状态拆分建议

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              推荐状态拆分方案                                │
└─────────────────────────────────────────────────────────────────────────────┘

【当前结构】
src/store/
├── index.js              # 575行，所有状态混在一起
└── modules/
    ├── activeRouterMatch.js
    └── menu.js

【推荐结构】
src/store/
├── index.js              # 入口，仅配置
├── modules/
│   ├── auth/             # 🔵 新增：认证模块
│   │   ├── index.js
│   │   ├── state.js
│   │   ├── mutations.js
│   │   ├── actions.js
│   │   └── getters.js
│   │
│   ├── menu/             # 现有menu模块重构
│   │   ├── index.js
│   │   └── ...
│   │
│   ├── router/           # 🔵 新增：动态路由模块
│   │   ├── index.js
│   │   └── ...
│   │
│   ├── tabs/             # 🔵 新增：标签页模块
│   │   ├── index.js
│   │   └── ...
│   │
│   ├── city/             # 🔵 新增：地市/机构模块
│   │   ├── index.js
│   │   └── ...
│   │
│   └── cache/            # 🔵 新增：缓存数据模块
│       ├── index.js
│       └── ...
│
├── plugins/
│   └── persist.js        # 🔵 新增：持久化插件配置
│
└── config/
    └── menus.js          # 🔵 新增：菜单配置文件
```

### 5.2 持久化策略优化

```javascript
// src/store/plugins/persist.js
import createPersistedState from "vuex-persistedstate";
import sessionStorage from "sessionstorage"; // 或使用原生sessionStorage

// 需要持久化的state白名单
const WHITELIST = [
  // 认证相关
  'auth.token',
  'auth.refreshToken',
  
  // 用户偏好
  'menu.menuCollapsed',
  'ui.collapsed',
  
  // 会话状态（可选）
  // 'tabs.tabList',  // 注释：标签页状态可选是否持久化
];

// 不需要持久化的state黑名单
const BLACKLIST = [
  'loading',
  'error',
  'modal',
  'tempData',    // 临时数据
];

export default createPersistedState({
  storage: window.sessionStorage,
  paths: WHITELIST,
  // 或者使用filter函数
  filter: (mutation) => {
    // 只持久化指定模块的变化
    return WHITELIST.some(path => mutation.type.startsWith(path.split('.')[0]));
  }
});
```

### 5.3 大对象优化

```javascript
// 1. 菜单数据优化 - 移到配置文件
// src/store/config/menus.js
export const SYSTEM_MENUS = [
  {
    module_name: "慢病管理",
    icon: "diff",
    id: "disease-manage",
    children: [/* ... */]
  },
  // ...其他菜单
];

// 2. 按地市/模块动态导入
// src/store/config/city-menus/
export const BAOJI_MENUS = () => import('./baoji.js');
export const FUXIN_MENUS = () => import('./fuxin.js');
export const SHANGLUO_MENUS = () => import('./shangluo.js');

// 3. 菜单数据不在Vuex中存储，改为直接import
// src/store/modules/menu.js
import { SYSTEM_MENUS } from '../config/menus';

// state
const state = {
  // menuData不再存储在state中
  // menuCollapsed: true,  // 只保留需要动态变化的状态
};

// getters
const getters = {
  // 菜单数据通过getter动态获取
  systemMenus: () => SYSTEM_MENUS,
  
  // 根据权限过滤后的菜单
  filteredMenus: (state, getters, rootState) => {
    const permissions = state.permissions;
    return SYSTEM_MENUS.map(module => ({
      ...module,
      children: module.children.filter(child => {
        // 根据权限过滤
        return permissions[child.routerName];
      })
    }));
  }
};
```

### 5.4 模块化改造方案

```javascript
// src/store/modules/auth/index.js
// 认证模块 - 负责Token、登录状态、用户信息

const state = {
  token: '',
  tokenType: 'Bearer',
  refreshToken: '',
  expiresAt: null,
  isAuthenticated: false,
};

const getters = {
  isLoggedIn: state => !!state.token,
  authHeaders: state => ({
    'Authorization': `${state.tokenType} ${state.token}`
  }),
};

const mutations = {
  SET_TOKEN(state, { token, refreshToken, expiresIn }) {
    state.token = token;
    state.refreshToken = refreshToken;
    state.expiresAt = Date.now() + expiresIn * 1000;
    state.isAuthenticated = true;
  },
  CLEAR_AUTH(state) {
    state.token = '';
    state.refreshToken = '';
    state.expiresAt = null;
    state.isAuthenticated = false;
  },
};

const actions = {
  async login({ commit }, credentials) {
    const response = await api.login(credentials);
    commit('SET_TOKEN', response.data);
    return response;
  },
  
  async logout({ commit }) {
    await api.logout();
    commit('CLEAR_AUTH');
    sessionStorage.clear();
  },
  
  async refreshToken({ state, commit }) {
    if (Date.now() >= state.expiresAt - 60000) { // 提前1分钟刷新
      const response = await api.refreshToken(state.refreshToken);
      commit('SET_TOKEN', response.data);
    }
  },
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions,
};
```

### 5.5 完整优化后的Store结构

```javascript
// src/store/index.js (优化后)
import Vue from 'vue';
import Vuex from 'vuex';

// 导入模块
import auth from './modules/auth';
import menu from './modules/menu';
import router from './modules/router';
import tabs from './modules/tabs';
import city from './modules/city';
import cache from './modules/cache';

// 导入插件
import persist from './plugins/persist';

Vue.use(Vuex);

const store = new Vuex.Store({
  // 严格模式 - 生产环境关闭
  strict: process.env.NODE_ENV !== 'production',
  
  // 根state - 仅包含全局共享的简单状态
  state: {
    version: '1.0.0',
    env: process.env.NODE_ENV,
  },
  
  // 根getters
  getters: {
    isDev: state => state.env === 'development',
    version: state => state.version,
  },
  
  // 根mutations - 仅处理简单的同步操作
  mutations: {
    // 全局loading状态
    SET_LOADING(state, { key, value }) {
      state.loading = state.loading || {};
      Vue.set(state.loading, key, value);
    },
  },
  
  // 根actions
  actions: {
    async initApp({ dispatch }) {
      // 初始化应用
      await dispatch('auth/checkAuth', null, { root: true });
    },
  },
  
  // 模块
  modules: {
    auth,      // 认证模块
    menu,      // 菜单模块
    router,    // 路由模块
    tabs,      // 标签页模块
    city,      // 地市模块
    cache,     // 缓存模块
  },
  
  // 插件
  plugins: [persist],
});

export default store;
```

---

## 📊 总结与评分

### 当前架构评分

| 维度 | 评分 | 说明 |
|------|------|------|
| **代码组织** | ⭐⭐ | 所有状态混在index.js中，缺乏模块化 |
| **持久化策略** | ⭐⭐ | 未配置paths，全量持久化，⚠️性能问题 |
| **类型安全** | ⭐ | 全部使用JS，无TypeScript |
| **可维护性** | ⭐⭐⭐ | 代码量不大，但结构混乱 |
| **性能** | ⭐⭐ | 大量硬编码数据被持久化 |
| **扩展性** | ⭐⭐ | 模块间耦合严重，难以扩展 |

**综合评分: 2/5**

### 核心问题总结

1. **持久化过度**: 所有state都被持久化，应该只持久化必要数据
2. **硬编码数据**: menuData等数据应从后端获取或使用配置文件
3. **模块化不足**: 只有2个模块，状态逻辑混杂
4. **缺乏getters**: 根Store直接访问state，无计算缓存
5. **安全风险**: 地市标识通过URL参数传递

### 优先优化项

1. 🔴 **紧急**: 配置持久化paths，只持久化token和用户偏好
2. 🔴 **紧急**: 将硬编码菜单移到配置文件
3. 🟡 **重要**: 重构模块化结构，拆分auth、tabs等独立模块
4. 🟡 **重要**: 添加根getters用于派生数据
5. 🟢 **建议**: 考虑TypeScript重构

---

*文档结束*

---

## 附录A：Vuex核心概念速查表

### A.1 Mutation vs Action 区别

| 特性 | Mutation | Action |
|------|----------|--------|
| 同步/异步 | 同步 | 异步 |
| 状态修改 | 直接修改state | 通过commit调用mutation |
| 调试 | devtools记录每一步 | devtools记录异步流程 |
| 适用场景 | 简单的状态赋值 | API调用、多步骤操作 |

### A.2 项目中主要Mutations调用关系

```
updateTabList ← Home.vue.remove()
           ← router/index.js (路由守卫)
updateCollapsed ← Home.vue.collapsedChange()
setMenus ← activeRouterMatch.getRoleMenusAsync()
updateMenu ← 登录后初始化
updateUserInfo ← 登录后初始化
updateToken ← 登录成功时
updateSelectData ← 下拉数据加载
```

---

## 附录B：技术债务清单

### B.1 安全性问题

| 问题 | 严重程度 | 描述 | 建议 |
|------|---------|------|------|
| Token明文存储 | 高 | token在sessionStorage中明文存储 | 使用HttpOnly Cookie或加密存储 |
| AES加密的日志泄露 | 中 | 加密密钥可能出现在日志中 | 使用环境变量管理密钥 |
| URL参数传递敏感信息 | 中 | cityFlag等通过URL传递 | 改用请求头或Cookie |
| 硬编码密钥 | 高 | util.js中存在硬编码的ASE密钥 | 移除或使用环境变量 |

### B.2 性能问题

| 问题 | 影响 | 描述 | 建议 |
|------|------|------|------|
| 全量持久化 | 性能 | 所有state都被持久化 | 配置paths白名单 |
| 硬编码菜单 | 体积 | menuData等数据约60KB | 移到配置文件或后端 |
| 无缓存策略 | 重复请求 | selectData无过期机制 | 添加TTL或手动刷新 |
| 重复解析 | 性能 | 每次读取用户信息都解密 | 缓存解密结果 |

### B.3 可维护性问题

| 问题 | 影响 | 描述 |
|------|------|------|
| 模块化不足 | 中 | 所有状态在根Store和2个模块中 |
| 硬编码值 | 中 | 大量magic number和字符串 |
| 注释缺失 | 低 | 部分代码无注释说明 |
| 无单元测试 | 低 | 无Vuex相关测试 |

---

## 附录C：代码示例

### C.1 完整的登录→路由加载流程代码

```javascript
// 1. 登录组件调用
async handleLogin() {
  try {
    // 调用登录API
    const res = await api.loginByCaptchaMb({
      account: this.form.getFieldValue('username'),
      password: this.$util.encrypt(this.form.getFieldValue('password')),
      captcha: this.form.getFieldValue('captcha')
    });
    
    if (res.status === 0) {
      // 2. 保存到sessionStorage（加密）
      const encryptedData = this.$util.encrypt(JSON.stringify(res.data));
      sessionStorage.setItem('logInfoMB', encryptedData);
      
      // 3. 跳转到首页
      this.$router.push('/home');
      
      // 4. 触发动态路由加载
      this.$store.dispatch('activeRouterMatch/getRoleMenusAsync');
      
      // 5. 更新用户信息到menu模块
      this.$store.commit('menu/updateUserInfo', res.data);
      this.$store.commit('menu/updateMenu', res.data.menus || []);
    }
  } catch (error) {
    console.error('登录失败:', error);
  }
}

// 5. 路由守卫检查
router.beforeEach((to, from, next) => {
  // 检查登录状态
  const logInfoMB = util.getUserInfo();
  
  if (!logInfoMB) {
    // 未登录，跳转到登录页
    if (to.path !== '/loginMb') {
      next('/loginMb');
      sessionStorage.clear();
      store.commit("updateTabList", []);
    } else {
      next();
    }
  } else {
    // 已登录，允许访问
    next();
  }
});
```

### C.2 标签页状态管理示例

```javascript
// Home.vue 中的标签页操作
export default {
  data() {
    return {
      activeKey: this.$route.path
    };
  },
  computed: {
    ...mapState({
      tabList: state => state.tabList
    })
  },
  methods: {
    // 切换标签
    onChange(activeKey) {
      this.activeKey = activeKey;
      this.$router.push({ path: activeKey });
    },
    
    // 关闭标签
    remove(targetKey) {
      let activeKey = this.activeKey;
      let lastIndex;
      this.tabList.forEach((tab, i) => {
        if (tab.path === targetKey) {
          lastIndex = i - 1;
        }
      });
      
      const tabList = this.tabList.filter(tab => tab.path !== targetKey);
      
      if (tabList.length && activeKey === targetKey) {
        activeKey = lastIndex >= 0 
          ? tabList[lastIndex].path 
          : tabList[0].path;
        this.$router.push({ path: activeKey });
      }
      
      // 更新store
      this.$store.commit('updateTabList', tabList);
    },
    
    // 添加新标签（通常在router.beforeEach中调用）
    addTab(tab) {
      const tabList = [...this.tabList];
      const exists = tabList.find(t => t.path === tab.path);
      
      if (!exists) {
        tabList.push(tab);
        this.$store.commit('updateTabList', tabList);
      }
      
      this.activeKey = tab.path;
    }
  },
  
  // 监听路由变化，自动添加标签
  watch: {
    '$route.path': {
      handler(newPath) {
        this.addTab({
          path: newPath,
          moduleName: this.$route.meta.title || '未命名'
        });
      },
      immediate: true
    }
  }
};
```

### C.3 权限验证工具函数

```javascript
// src/utils/permission.js

/**
 * 检查用户是否有指定权限
 * @param {string} permissionCode - 权限码
 * @returns {boolean} - 是否有权限
 */
export function hasPermission(permissionCode) {
  const store = require('@/store').default;
  const permissions = store.state.menu.permissions;
  return !!permissions[permissionCode];
}

/**
 * 检查用户是否有所有指定权限
 * @param {string[]} permissionCodes - 权限码数组
 * @returns {boolean} - 是否有所有权限
 */
export function hasAllPermissions(permissionCodes) {
  return permissionCodes.every(code => hasPermission(code));
}

/**
 * 检查用户是否有任一指定权限
 * @param {string[]} permissionCodes - 权限码数组
 * @returns {boolean} - 是否有任一权限
 */
export function hasAnyPermission(permissionCodes) {
  return permissionCodes.some(code => hasPermission(code));
}

/**
 * 权限指令（用于Vue组件）
 * 使用方式: v-permission="'problem:create'"
 */
export const permissionDirective = {
  inserted(el, binding, vnode) {
    const { value } = binding;
    if (value && !hasPermission(value)) {
      el.parentNode && el.parentNode.removeChild(el);
    }
  }
};
```

### C.4 模块化改造后的store配置

```javascript
// src/store/index.js (模块化改造版本)

import Vue from 'vue';
import Vuex from 'vuex';

// 动态导入所有模块
const modulesFiles = require.context('./modules', true, /index\.js$/);
const modules = modulesFiles.keys().reduce((modules, modulePath) => {
  const moduleName = modulePath.replace(/^\.\/(.*)\/index\.js$/, '$1');
  const value = modulesFiles(modulePath);
  modules[moduleName] = value.default;
  return modules;
}, {});

// 持久化配置
import createPersistedState from 'vuex-persistedstate';

const persistedState = createPersistedState({
  storage: window.sessionStorage,
  key: 'picc-mzmtb-store',
  paths: [
    'auth.token',
    'ui.collapsed',
    'tabs.tabList',
    'city.currentCityId'
  ],
  filter: (mutation) => {
    const persistedMutations = [
      'auth/SET_TOKEN',
      'auth/SET_USER_INFO',
      'ui/SET_COLLAPSED',
      'tabs/ADD_TAB',
      'tabs/REMOVE_TAB',
      'tabs/CLEAR_TABS'
    ];
    return persistedMutations.includes(mutation.type);
  }
});

Vue.use(Vuex);

const store = new Vuex.Store({
  strict: process.env.NODE_ENV !== 'production',
  
  modules,
  
  plugins: [persistedState]
});

export default store;
```

---

## 附录D：环境变量配置参考

### D.1 .env.development

```bash
# 开发环境配置
NODE_ENV=development
domainName=http://localhost:8080
ASE_Num=your_dev_encryption_key_here
```

### D.2 .env.production

```bash
# 生产环境配置
NODE_ENV=production
domainName=https://api.picc.com
ASE_Num=your_prod_encryption_key_here
```

---

## 附录E：快速参考卡片

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PICC Vuex架构快速参考                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  📦 Store结构                                                                │
│  ├── 根State (index.js)                                                     │
│  │   ├── token - 用户令牌                                                   │
│  │   ├── menuData - 菜单数据                                                │
│  │   └── tabList - 标签页列表                                               │
│  │                                                                            │
│  └── 模块                                                                   │
│      ├── menu - 菜单/用户/权限                                               │
│      └── activeRouterMatch - 动态路由                                        │
│                                                                             │
│  🔄 数据流                                                                   │
│  登录 → sessionStorage(logInfoMB) → token → 菜单 → 路由                      │
│                                                                             │
│  ⚠️ 注意事项                                                                │
│  ├── 持久化配置paths避免全量持久化                                           │
│  ├── menuData应移到配置文件                                                 │
│  └── 考虑TypeScript重构                                                     │
│                                                                             │
│  🔧 调试命令                                                                 │
│  └── this.$store.state.menu.menuCollapsed                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

*文档结束 - PICC门诊慢特病前端Vuex状态管理深度解析报告*

