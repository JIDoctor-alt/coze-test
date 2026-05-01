# PICC门诊慢特病前端项目路由与权限深度解析

> 文档版本：1.0  
> 解析范围：picc-mzmtb-agent（Vue 2.6 + Vue Router 3 + Vuex 3）  
> 源码位置：/tmp/picc-mzmtb-agent/

---

## 📋 目录

1. [路由配置深度解析](#part-1-路由配置深度解析)
2. [路由守卫完整解析](#part-2-路由守卫完整解析)
3. [菜单与权限的联动](#part-3-菜单与权限的联动)
4. [地市差异化路由](#part-4-地市差异化路由)
5. [权限体系全景](#part-5-权限体系全景)
6. [总结与架构图](#总结与架构图)

---

## Part 1：路由配置深度解析

### 1.1 路由架构总览

```
📦 路由文件结构
├── index.js          # 主路由配置文件（入口+守卫）
└── childrenRoutes.js # 子路由配置（2389行，核心路由表）
```

#### 1.1.1 主路由配置 (index.js)

```javascript
// src/router/index.js 核心结构
export const staticRoutes = [
    {
      path: "/",
      name: "_index",
      redirect: "/loginMb"  // 根路径重定向到登录页
    },
    {
      path: "/home",
      name: "home",
      meta: { title: "首页", pathName: "/home" },
      component: () => import("@/pages/Home"),
      children: [...childrenRoutes]  // 注入所有子路由
    },
    {
      path: "/loginMb",
      name: "loginMb",
      meta: { title: "门诊慢特病业务管理信息系统" },
      component: () => import("@/components/loginMb/index"),
    }
]

export const activeRouter = [
    // 精简版静态路由（不含children，用于初始化）
    { path: "/", redirect: "/loginMb" },
    { path: "/home", name: "home", component: () => import("@/pages/Home") },
    { path: "/loginMb", name: "loginMb", component: () => import("@/components/loginMb/index") },
    { path: "/resetConfirm", name: "resetConfirm", component: () => import("@/pages/SystemView/resetConfirm") }
]

export const createRouter = () => new Router({
    mode: "hash",  // Hash模式路由
    routes: [...activeRouter]  // 初始只加载基础路由
})
```

**关键设计点**：
- 采用**双路由数组**策略：`staticRoutes`（完整版）和 `activeRouter`（精简版）
- 路由模式使用 `hash` 模式，便于部署和跨域
- 初始加载只包含登录页和首页，**动态路由在登录后按需注入**

---

### 1.2 完整路由表分析 (childrenRoutes.js)

#### 1.2.1 路由条目结构

```javascript
// 标准路由条目格式
{
    path: `/systemUserManage`,
    name: "systemUserManage",
    meta: {
        ptitle: "系统管理",      // 父级菜单标题
        title: "用户管理",       // 当前菜单标题
        pathName: "/systemUserManage"  // 路由标识
    },
    component: () => import("@/pages/SystemView/systemUserManage"),
}
```

#### 1.2.2 路由元信息 (meta) 字段说明

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `ptitle` | String | 父级菜单名称 | "系统管理" |
| `title` | String | 当前页面标题 | "用户管理" |
| `pathName` | String | 路由路径标识 | "/systemUserManage" |
| `isLogin` | Boolean | 是否需要登录验证(已注释) | true |

#### 1.2.3 路由分类统计

| 分类 | 数量 | 说明 |
|------|------|------|
| 系统管理 | 6 | 用户管理、角色管理、模块管理等 |
| 宝鸡慢病 | 35+ | 慢病申报、体检、专家分配等 |
| 延安慢病 | 35+ | 延安专属业务流程 |
| 晋中慢病 | 35+ | 晋中专属业务流程 |
| 商洛慢病 | 35+ | 商洛专属业务流程 |
| 满洲里慢病 | 10+ | 满洲里专属业务流程 |
| 榆林慢病 | 15+ | 榆林专属业务流程 |
| 张家口慢病 | 7+ | 张家口专属业务流程 |
| 阜新慢病 | 8+ | 阜新专属业务流程 |
| 医院管理 | 4 | 医院建卡、挂号等 |
| 药店管理 | 6 | 药店缴费、药品维护等 |
| 快赔管理 | 6 | 理赔申请、授权等 |
| 其他地市 | - | 定州、杨凌、九江、晋城、咸阳等 |

---

### 1.3 路由懒加载实现

#### 1.3.1 懒加载语法

```javascript
// 标准箭头函数懒加载
component: () => import("@/pages/SystemView/systemUserManage")

// 示例：路由懒加载原理
{
    path: "/systemUserManage",
    component: () => {
        return import("@/pages/SystemView/systemUserManage")
    }
}
```

**优势**：
- 首屏加载只加载登录页，减小初始 bundle 体积
- 路由跳转时才加载对应组件代码
- Webpack 会为每个懒加载路由生成独立的 chunk 文件

#### 1.3.2 懒加载与预加载对比

```javascript
// 懒加载（当前使用）- 访问时才加载
component: () => import("@/pages/xxx")

// 预加载（注释状态）
// component: () => import("@/pages/xxx").then(module => module.default)
```

---

### 1.4 404错误页面路由

```javascript
// src/store/modules/activeRouterMatch.js
router.addRoute({
    path: "*",  // 匹配所有未定义路由
    name: "404",
    component: () => import("@/pages/404")
})
```

**特点**：
- 使用通配符 `*` 匹配所有未定义路由
- 在动态路由添加完成后注入，确保404页面可用
- 不需要在 childrenRoutes.js 中预定义

---

### 1.5 重定向规则

| 源路径 | 目标路径 | 触发条件 |
|--------|----------|----------|
| `/` | `/loginMb` | 根路径访问 |
| 无效路由 | `/loginMb` | 未登录状态 |
| 无效路由 | 404 | 已登录状态 |

---

## Part 2：路由守卫完整解析

### 2.1 守卫架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户访问URL                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     beforeEach 全局前置守卫                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 1. 修改页面标题 (document.title)                           │ │
│  │ 2. 获取用户信息 (util.getUserInfo())                       │ │
│  │ 3. Token验证流程                                           │ │
│  │ 4. 未登录/无权限重定向                                      │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
            ┌───────────────┐       ┌───────────────┐
            │   已登录       │       │   未登录       │
            │   next()      │       │   重定向       │
            └───────────────┘       └───────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     afterEach 全局后置守卫                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 1. 滚动位置重置 (window.scrollTo(0,0))                    │ │
│  │ 2. 路由变化检测                                           │ │
│  │ 3. 版本更新检查 (updatePages)                             │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 全局前置守卫代码解析

```javascript
// src/router/index.js

router.beforeEach((to, from, next) => {
    // ========== 第一步：修改页面标题 ==========
    if (to.meta.title) {
        document.title = to.meta.title;
    }
    
    // ========== 第二步：获取用户信息 ==========
    let logInfoMB = util.getUserInfo();
    
    // ========== 第三步：Token验证与权限校验 ==========
    if (!logInfoMB) {
        // 未登录状态处理
        if (to.path == '/loginMb') {
            // 访问登录页，直接放行
            next();
            sessionStorage.clear();
            store.commit("updateTabList", []);
        } else if (to.path == '/resetConfirm') {
            // 访问重置密码页，直接放行
            next();
        } else {
            // 其他页面，重定向到登录页
            next('/loginMb');
            sessionStorage.clear();
            store.commit("updateTabList", []);
        }
    } else {
        // 已登录状态，直接放行
        next();
    }
    
    // ========== 第四步：版本更新检查 ==========
    if (from.path !== to.path) {
        updatePages();
    }
});
```

### 2.3 Token验证流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      Token验证流程                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  util.getUserInfo()                                              │
│  ├── 检查 sessionStorage.getItem("logInfoMB")                   │
│  ├── 使用 AES 解密数据 (util.decrypt)                           │
│  ├── JSON.parse 解析用户信息                                    │
│  └── 返回用户对象或null                                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
            ┌───────────────┐       ┌───────────────┐
            │ 返回用户对象   │       │ 返回 null     │
            │ logInfoMB     │       │ 未登录/过期   │
            └───────────────┘       └───────────────┘
                    │                       │
                    ▼                       ▼
            ┌───────────────┐       ┌───────────────┐
            │ next()放行    │       │ 重定向登录页  │
            └───────────────┘       └───────────────┘
```

### 2.4 权限校验逻辑

```javascript
// 权限校验伪代码
function checkPermission(to, from, next) {
    // 1. 获取用户信息
    const userInfo = util.getUserInfo();
    
    // 2. 检查登录状态
    if (!userInfo) {
        // 白名单路由检查
        const whiteList = ['/loginMb', '/resetConfirm'];
        if (whiteList.includes(to.path)) {
            next();
        } else {
            next('/loginMb');
        }
        return;
    }
    
    // 3. 登录状态直接放行
    // 注：本项目权限校验主要在动态路由生成阶段
    next();
}
```

### 2.5 未登录/无权限处理方式

| 场景 | 处理方式 | 后续操作 |
|------|----------|----------|
| 访问登录页 | `next()` 直接放行 | 允许访问 |
| 访问重置密码页 | `next()` 直接放行 | 允许访问 |
| 未登录访问其他页面 | `next('/loginMb')` | 强制跳转登录 |
| 无权限访问某路由 | 无显式处理 | 由动态路由控制（未配置则404） |

### 2.6 全局后置守卫

```javascript
router.afterEach((to, from, next) => {
    // 页面滚动位置重置
    window.scrollTo(0, 0);
});
```

---

## Part 3：菜单与权限的联动

### 3.1 菜单数据来源分析

#### 3.1.1 双重数据源

```
┌─────────────────────────────────────────────────────────────────┐
│                      菜单数据来源                                 │
├─────────────────────────────┬───────────────────────────────────┤
│        后端API              │           本地配置                 │
├─────────────────────────────┼───────────────────────────────────┤
│ logInfoMB.menus             │ store/index.js                    │
│ 登录后从服务器获取           │ menuData/menuList等               │
│ 包含用户真实权限菜单         │ 备用/默认菜单配置                  │
└─────────────────────────────┴───────────────────────────────────┘
```

#### 3.1.2 后端菜单数据结构

```javascript
// 登录成功后从API获取的菜单数据结构
{
    menus: [
        {
            module_name: "慢病管理",      // 一级菜单名称
            id: "asacdfdtg",
            children: [
                {
                    moduleName: "慢病初审管理",  // 二级菜单名称
                    url: "/diseaseFirstTrial",   // 路由路径
                    menuKey: "diseaseFirstTrial" // 菜单Key
                },
                // ... 更多子菜单
            ]
        },
        // ... 更多一级菜单
    ]
}
```

#### 3.1.3 本地默认菜单配置

```javascript
// src/store/index.js
menuData: [
    {
        module_name: "慢病管理",
        icon: "diff",
        children: [
            { title: "慢病初审管理", routerName: "diseaseFirstTrial" },
            { title: "慢病体检分配", routerName: "diseaseCheck" },
            // ...
        ]
    },
    {
        module_name: "阜新慢病",
        children: [
            { title: "慢病申报导入", routerName: "newDeclareInport" },
            // ...
        ]
    }
]
```

### 3.2 动态路由生成机制

#### 3.2.1 核心流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                    动态路由生成流程                               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. 用户登录成功                                                  │
│    loginFn() → 获取用户信息 → 加密存储到sessionStorage           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. 调用 getRoleMenusAsync()                                      │
│    this.$store.dispatch('getRoleMenusAsync')                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. 从sessionStorage解密获取用户菜单权限                          │
│    logInfoMB = util.getUserInfo()                               │
│    menusData = logInfoMB.menus                                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. 匹配静态路由                                                  │
│    for each menu item:                                          │
│        urlArr = menu.url.split('/')                             │
│        menuKey = urlArr[last]                                    │
│        matchedRoute = staticMenus.find(route.name == menuKey)   │
│        addRoutes.push(matchedRoute)                              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. 重置路由匹配器                                                │
│    router.matcher = createRouter().matcher                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. 动态添加路由                                                  │
│    addRoutes.forEach(route => {                                 │
│        router.addRoute('home', route)                           │
│    })                                                           │
│    router.addRoute('*', { name: '404', ... })                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. 路由添加完成                                                  │
│    router.push('/home') → 显示首页和菜单                         │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.2.2 核心代码解析

```javascript
// src/store/modules/activeRouterMatch.js

actions: {
    getRoleMenusAsync(store) {
        return new Promise(resolve => {
            let logInfoMB = util.getUserInfo();
            if (logInfoMB) {
                var menusData = logInfoMB.menus;
                var addRoutes = [];
                var staticMenus = [...staticRoutes[1].children];  // 获取静态子路由
                
                store.commit('setMenus', menusData);  // 存储菜单数据
                
                // ========== 开发环境 vs 生产环境 ==========
                if (process.env.NODE_ENV != 'development') {
                    // 生产/测试环境：严格按权限匹配路由
                    for (let i = 0; i < menusData.length; i++) {
                        for (let j = 0; j < menusData[i].children.length; j++) {
                            let urlArr = menusData[i].children[j].url.split('/');
                            menusData[i].children[j].menuKey = urlArr[urlArr.length - 1];
                            let oneRouter = staticMenus.find(item => 
                                item.name == urlArr[urlArr.length - 1]
                            );
                            oneRouter !== undefined ? addRoutes.push(oneRouter) : "";
                        }
                    }
                } else {
                    // 开发环境：加载全部静态路由（绕过权限控制）
                    for (let i = 0; i < menusData.length; i++) {
                        for (let j = 0; j < menusData[i].children.length; j++) {
                            let urlArr = menusData[i].children[j].url.split('/');
                            menusData[i].children[j].menuKey = urlArr[urlArr.length - 1];
                        }
                    }
                    addRoutes = [...staticMenus];
                }
                
                // ========== 关键：重置路由匹配器 ==========
                router.matcher = createRouter().matcher;
                
                // ========== 动态添加路由 ==========
                addRoutes.forEach(val => {
                    router.addRoute('home', val);  // 添加到home父路由下
                });
                
                // ========== 添加404路由 ==========
                router.addRoute({
                    path: "*",
                    name: "404",
                    component: () => import("@/pages/404")
                });
                
                resolve();
            }
        });
    }
}
```

### 3.3 菜单渲染与路由对应关系

#### 3.3.1 菜单组件结构

```vue
<!-- src/components/menuList/index.vue -->

<template>
    <a-menu mode="inline" :openKeys="openKeys" :selectedKeys="itemSelect">
        <a-sub-menu v-for="item in menuList" :key="item.id">
            <span slot="title">
                <img src="..." class="icon">
                <span class="title">{{item.moduleName}}</span>
            </span>
            <a-menu-item v-for="subItem in item.children" 
                         :key="`${subItem.menuKey}`">
                {{subItem.moduleName}}
            </a-menu-item>
        </a-sub-menu>
    </a-menu>
</template>

<script>
export default {
    created() {
        // 菜单数据从Vuex store获取
        this.menuList = this.$store.state.activeRouterMatch.homeMenus;
    },
    methods: {
        menuClickEvent({ item, key, keyPath }) {
            if (!isNaN(key)) {
                // 根据路由name导航
                this.$router.push({ name: key });
            }
        }
    }
}
</script>
```

#### 3.3.2 路由与菜单的映射关系

```
┌─────────────────────────────────────────────────────────────────┐
│                     路由 → 菜单 映射关系                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  后端菜单数据 (menus)          静态路由 (childrenRoutes.js)     │
│  ┌──────────────────────┐       ┌──────────────────────────┐   │
│  │ url: "/diseaseFirst" │  ←→   │ name: "diseaseFirst"     │   │
│  │ moduleName: "慢病初审" │       │ meta.title: "慢病初审管理"  │   │
│  │ menuKey: "diseaseFirst"│      │ component: import(...)  │   │
│  └──────────────────────┘       └──────────────────────────┘   │
│                                                                 │
│  匹配逻辑：menuKey === route.name                               │
└─────────────────────────────────────────────────────────────────┘
```

### 3.4 按钮级权限控制

> ⚠️ **注意**：本项目未发现 `v-permission` 自定义指令，权限控制主要依赖动态路由。若需要按钮级权限控制，需自行扩展。

#### 3.4.1 权限数据存储

```javascript
// src/store/modules/menu.js
state: {
    permissions: {}  // 权限对象存储
},
mutations: {
    updateUserInfo(state, data) {
        state.userInfo = {
            deptId: data.deptId,
            roles: data.roles,
            roleNames: data.roleNames,
            userName: data.userName,
            email: data.email
        };
        // 构建权限映射
        let permissions = {};
        (data.menus || []).forEach((x) => {
            x.menuCode && (permissions[x.menuCode] = x);
        });
        state.permissions = permissions;
    }
},
getters: {
    permissions: state => state.permissions
}
```

#### 3.4.2 权限检查方式（手动实现）

```javascript
// 在组件中手动检查权限
methods: {
    hasPermission(permissionCode) {
        const permissions = this.$store.getters.permissions;
        return !!permissions[permissionCode];
    }
}

// 模板中使用
<template>
    <div>
        <button v-if="hasPermission('user:add')">新增用户</button>
        <button v-if="hasPermission('user:delete')">删除用户</button>
    </div>
</template>
```

---

## Part 4：地市差异化路由

### 4.1 地市Flag字段说明

```
┌─────────────────────────────────────────────────────────────────┐
│                    地市Flag字段控制机制                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  路由路径格式：/diseaseFirstTrial&flag=3                        │
│                      │                  │                      │
│                      │                  └── Flag值（地市标识）   │
│                      └── 基础路由名称                            │
│                                                                 │
│  Flag值对照表：                                                 │
│  ┌───────┬──────────────────────┐                              │
│  │ Flag  │       地市名称       │                              │
│  ├───────┼──────────────────────┤                              │
│  │ 0     │ 通用/默认             │                              │
│  │ 2     │ 商洛                  │                              │
│  │ 3     │ 张家口                │                              │
│  │ 4     │ 延安                  │                              │
│  │ 6     │ 晋中                  │                              │
│  │ 7     │ 榆林                  │                              │
│  │ 8     │ 满洲里                │                              │
│  │ 10    │ 定州                  │                              │
│  │ 13    │ 杨凌                  │                              │
│  │ 15    │ 九江                  │                              │
│  │ 16    │ 晋城                  │                              │
│  │ 17    │ 咸阳                  │                              │
│  └───────┴──────────────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 路由差异化实现

#### 4.2.1 独立路由配置

```javascript
// childrenRoutes.js 中的地市专属路由
{
    // 延安慢病初审
    path: "/diseaseFirstTrial&flag=4",
    name: "diseaseFirstTrial&flag=4",
    meta: {
        ptitle: "延安慢病管理",
        title: "慢病初审管理",
        pathName: "/diseaseFirstTrial",
    },
    component: () => import("@/pages/YAChronicDis/auditManagement"),
},
{
    // 晋中慢病初审
    path: "/diseaseFirstTrial&flag=6",
    name: "diseaseFirstTrial&flag=6",
    meta: {
        ptitle: "晋中慢病管理",
        title: "慢病初审管理",
        pathName: "/diseaseFirstTrial",
    },
    component: () => import("@/pages/JZChronicDis/auditManagement"),
}
```

#### 4.2.2 组件目录差异化

```
📦 pages/
├── ChronicDis/          # 通用组件
├── YAChronicDis/         # 延安专属组件
├── JZChronicDis/         # 晋中专属组件
├── SLChronicDis/         # 商洛专属组件
├── MZLChronicDis/        # 满洲里专属组件
├── YLChronicDis/        # 榆林专属组件
├── ZJKChronicDis/        # 张家口专属组件
├── DIZChronicDis/        # 定州专属组件
├── YaLChronicDis/        # 杨凌专属组件
├── JiJChronicDis/        # 九江专属组件
├── JCChronicDis/         # 晋城专属组件
├── XYaChronicDis/        # 咸阳专属组件
└── Newdeclare/           # 阜新专属组件
```

### 4.3 地市功能差异对比

| 功能模块 | 商洛(flag=2) | 延安(flag=4) | 榆林(flag=7) | 晋中(flag=6) |
|----------|--------------|--------------|--------------|--------------|
| 慢病初审管理 | ✅ | ✅ | ✅ | ✅ |
| 慢病体检分配 | ✅ | ✅ | ✅ | ✅ |
| 慢病专家分配 | ✅ | ✅ | ✅ | ✅ |
| 慢病用户管理 | ✅ | ✅ | ❌ | ✅ |
| 体检站点管理 | ✅ | ✅ | ❌ | ✅ |
| 人员批量导入 | ✅ | ✅ | ✅ | ✅ |
| 服务状态修改 | ✅ | ✅ | ❌ | ✅ |
| 消费记录查询 | ❌ | ✅ | ❌ | ✅ |
| 对账导出报表 | ✅ | ✅ | ❌ | ✅ |
| 专家二次判定 | ❌ | ✅ | ❌ | ❌ |
| 处方管理 | ✅ | ✅ | ✅ | ❌ |
| 年审管理 | ✅ | ❌ | ✅ | ❌ |
| 申报综合查询 | ✅ | ❌ | ✅ | ❌ |
| 外部用户管理 | ✅ | ❌ | ✅ | ❌ |

---

## Part 5：权限体系全景

### 5.1 完整权限链路

```
┌─────────────────────────────────────────────────────────────────┐
│                  权限体系全景图                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         后端权限数据                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ userId, userName, token, menus[], roles[]                │   │
│  │ menus = [{ module_name, url, menuCode, children[] }]     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ JSON加密传输
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      前端登录接口                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ api.loginByCaptchaMb(params)                             │   │
│  │  → 获取用户信息 → 加密存储到 sessionStorage              │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     用户信息存储                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ sessionStorage:                                          │   │
│  │ {                                                       │   │
│  │   logInfoMB: "AES加密的用户JSON字符串"                   │   │
│  │ }                                                        │   │
│  │                                                           │   │
│  │ 解密后结构:                                               │   │
│  │ { token, menus, roles, userId, userName, ... }           │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    动态路由生成                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ getRoleMenusAsync()                                      │   │
│  │ 1. 解密获取 menus                                        │   │
│  │ 2. 遍历菜单，匹配静态路由                                 │   │
│  │ 3. 重置 router.matcher                                   │   │
│  │ 4. 动态添加用户有权限的路由                               │   │
│  │ 5. 添加 404 路由                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      菜单渲染                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ menuList组件                                             │   │
│  │  - 从 store 获取 homeMenus                                │   │
│  │  - 根据 menus 数据渲染菜单树                              │   │
│  │  - 点击菜单通过路由name导航                               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     路由守卫校验                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ beforeEach                                               │   │
│  │  - 检查 sessionStorage 中的用户信息                       │   │
│  │  - 未登录重定向到登录页                                  │   │
│  │  - 已登录放行                                           │   │
│  │  - 动态路由已过滤无权路由                                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      页面访问控制                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 已登录用户访问 /diseaseFirstTrial                        │   │
│  │                                                           │   │
│  │ 情况1: 用户有此路由权限                                  │   │
│  │   → 路由存在 → 渲染对应组件                              │   │
│  │                                                           │   │
│  │ 情况2: 用户无此路由权限                                  │   │
│  │   → 路由不存在 → 匹配 * → 渲染 404                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 角色权限 → 菜单权限 → 按钮权限映射

#### 5.2.1 三级权限模型

```
┌─────────────────────────────────────────────────────────────────┐
│                      三级权限模型                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  第一级：角色权限 (roles[])                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ { roleId: "admin", roleName: "系统管理员" }              │   │
│  │ { roleId: "doctor", roleName: "医生" }                  │   │
│  │ { roleId: "expert", roleName: "专家" }                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  第二级：菜单权限 (menus[]) - 控制页面级访问                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ module_name: "慢病管理"                                │   │
│  │ ├── children[                                         │   │
│  │ │   { url: "/diseaseFirstTrial", title: "慢病初审" },  │   │
│  │ │   { url: "/diseaseCheck", title: "体检分配" },      │   │
│  │ │   ...                                                │   │
│  │ ]                                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  第三级：按钮权限 (menuCode) - 控制操作级访问                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ { menuCode: "user:add", title: "新增用户" }            │   │
│  │ { menuCode: "user:edit", title: "编辑用户" }           │   │
│  │ { menuCode: "user:delete", title: "删除用户" }        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.2.2 权限检查流程

```javascript
// 权限检查示例代码

// 1. 页面级权限检查（路由守卫自动处理）
function checkPagePermission(userMenus, targetPath) {
    for (let module of userMenus) {
        for (let menu of module.children) {
            if (menu.url === targetPath) {
                return true;  // 有权限
            }
        }
    }
    return false;  // 无权限 → 404
}

// 2. 按钮级权限检查（需手动实现）
function checkButtonPermission(permissions, buttonCode) {
    return !!permissions[buttonCode];
}

// 使用
if (checkButtonPermission(store.state.menu.permissions, 'user:delete')) {
    // 渲染删除按钮
}
```

### 5.3 权限缓存策略

#### 5.3.1 存储介质

```
┌─────────────────────────────────────────────────────────────────┐
│                      权限数据存储策略                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  sessionStorage (推荐)                                           │
│  ├── 存储内容: 加密的用户信息 (logInfoMB)                        │
│  ├── 生命周期: 浏览器会话期间有效                                │
│  ├── 适用场景: 用户信息、Token、菜单数据                          │
│  └── 优势: 页面刷新不丢失，关闭标签页自动清除                      │
│                                                                 │
│  localStorage (当前未使用)                                       │
│  ├── 存储内容: -                                                │
│  ├── 生命周期: 永久有效                                          │
│  └── 适用场景: 长期配置、记住登录状态                             │
│                                                                 │
│  Vuex + vuex-persistedstate                                     │
│  ├── 存储内容: 菜单折叠状态、Tab列表等                            │
│  ├── 持久化: 配置为 sessionStorage                               │
│  └── 自动同步: 刷新后自动恢复状态                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.3.2 加密存储实现

```javascript
// src/utils/util.js

// AES加密存储
let encrypt = (word) => {
    let aseNum = process.env.ASE_Num;
    var key = CryptoJS.enc.Utf8.parse(aseNum);
    var srcs = CryptoJS.enc.Utf8.parse(word);
    var encrypted = CryptoJS.AES.encrypt(srcs, key, {
        mode: CryptoJS.mode.ECB,
        padding: CryptoJS.pad.Pkcs7
    });
    return encrypted.toString();
}

// AES解密读取
let decrypt = (word) => {
    try {
        let aseNum = process.env.ASE_Num;
        var key = CryptoJS.enc.Utf8.parse(aseNum);
        var decrypt = CryptoJS.decrypt(word, key, {
            mode: CryptoJS.mode.ECB,
            padding: CryptoJS.pad.Pkcs7
        });
        return CryptoJS.enc.Utf8.stringify(decrypt).toString();
    } catch (error) {
        return null;
    }
}

// 存储
sessionStorage.setItem("logInfoMB", encrypt(JSON.stringify(userData)));

// 读取
let logInfoMB = null;
if (sessionStorage.getItem("logInfoMB")) {
    logInfoMB = JSON.parse(decrypt(sessionStorage.getItem("logInfoMB")));
}
```

### 5.4 权限变更的实时性

#### 5.4.1 权限变更场景

| 场景 | 处理方式 | 实时性 |
|------|----------|--------|
| 用户登录 | 调用 `getRoleMenusAsync` 生成路由 | 即时 |
| 刷新页面 | 从 sessionStorage 读取并重新生成 | 即时 |
| 管理员修改用户权限 | 需要用户重新登录 | 下次登录生效 |
| Token过期 | 后端返回 999，前端跳转登录页 | 即时 |

#### 5.4.2 Token过期处理

```javascript
// src/api/axiosPower.js

instance.interceptors.response.use(
    res => {
        let data = res.data;
        // ...
        return data;
    },
    error => {
        return Promise.reject(error);
    }
);

// 状态码 999 处理（在具体接口中）
if (data.status == 999) {
    window.sessionStorage.clear();
    Router.replace("/loginMb");  // 强制跳转登录
}
```

---

## 总结与架构图

### 整体架构总结

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                     Vue Router 3                         │   │
│   │  ┌────────────────┐  ┌────────────────┐               │   │
│   │  │   Hash 模式     │  │  动态路由       │               │   │
│   │  │   #/loginMb    │  │  按需加载       │               │   │
│   │  └────────────────┘  └────────────────┘               │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                     Vuex 3                              │   │
│   │  ┌────────────────┐  ┌────────────────┐               │   │
│   │  │ menu模块       │  │ activeRouterMatch│              │   │
│   │  │ 菜单状态      │  │  动态路由匹配   │               │   │
│   │  └────────────────┘  └────────────────┘               │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    权限体系                              │   │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │   │
│   │  │后端菜单  │→│加密存储 │→│路由生成 │→│菜单渲染 │    │   │
│   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 关键设计亮点

| 设计点 | 说明 | 优势 |
|--------|------|------|
| Hash路由模式 | 使用 `#` 路由 | 便于部署，无需服务端配置 |
| 动态路由 | 登录后按权限生成路由 | 减小首屏体积，提高安全性 |
| 双路由数组 | staticRoutes + activeRouter | 开发/生产环境灵活切换 |
| Flag字段 | 路径参数标识地市 | 一套代码支持多地市差异化 |
| AES加密 | 用户信息加密存储 | 防止信息泄露 |
| 开发环境全权限 | 自动加载全部路由 | 提高开发效率 |
| 404兜底 | 未匹配路由显示404 | 优雅降级 |

### 路由守卫执行顺序

```
1. 用户点击菜单/输入URL
       │
       ▼
2. beforeEach 全局前置守卫
   ├── 修改页面标题
   ├── 检查登录状态
   ├── 未登录重定向
   └── 调用 next()
       │
       ▼
3. 路由匹配 (matcher.match)
   ├── 有权限 → 找到路由 → 渲染组件
   └── 无权限 → 404路由 → 渲染404
       │
       ▼
4. afterEach 全局后置守卫
   ├── 滚动位置重置
   └── 版本检查
```

---

## 附录

### A. 文件索引

| 文件路径 | 说明 | 行数 |
|----------|------|------|
| `/src/router/index.js` | 主路由配置、守卫 | ~120行 |
| `/src/router/childrenRoutes.js` | 子路由配置 | ~2400行 |
| `/src/store/index.js` | Vuex主模块、菜单配置 | ~400行 |
| `/src/store/modules/menu.js` | 菜单状态管理 | ~120行 |
| `/src/store/modules/activeRouterMatch.js` | 动态路由匹配 | ~60行 |
| `/src/utils/util.js` | 工具函数（含加密解密） | ~600行 |
| `/src/components/menuList/index.vue` | 菜单组件 | ~150行 |
| `/src/api/axiosPower.js` | 权限相关API封装 | ~500行 |

### B. 环境变量说明

| 变量 | 说明 | 示例 |
|------|------|------|
| `NODE_ENV` | 运行环境 | development / production |
| `ASE_Num` | AES加密密钥 | 从环境配置获取 |
| `domainNamePower` | 权限服务域名 | 生产环境API地址 |

### C. 常见问题排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 刷新页面后菜单消失 | sessionStorage数据丢失 | 检查加密/解密逻辑 |
| 404页面频繁出现 | 路由未正确添加 | 检查动态路由生成逻辑 |
| 权限不生效 | 开发环境默认加载全路由 | 确认NODE_ENV配置 |
| Token过期频繁 | 后端Token有效期短 | 协调后端延长有效期 |

---

> 📝 文档生成时间：2024年  
> 🔍 解析版本：picc-mzmtb-agent 最新版本  
> ✍️ 解析深度：架构设计 + 核心流程 + 关键代码
