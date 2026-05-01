# 状态管理系统解析 - Vuex Store

> 🎯 一句话说明：Vuex 是系统的"记忆中心"，保存用户信息、权限、菜单等全局共享数据

---

## 这是啥？（小白版）

想象 **Vuex 是医院的"病历本管理系统"**：
- 每个病人（用户）的信息统一存储在护士站
- 医生（组件）需要查看病人信息时，从护士站获取
- 病人信息更新时，也需要通知护士站更新

---

## 核心代码解析

### store/index.js 主文件

```javascript
import Vue from "vue";
import Vuex from "vuex";
import menu from "./modules/menu";           // 菜单模块
import createPersistedState from "vuex-persistedstate";
import activeRouterMatch from "./modules/activeRouterMatch"

Vue.use(Vuex);

// 持久化配置：将状态保存到 sessionStorage
const createPersisted = createPersistedState({
    storage: window.sessionStorage,
})

const store = new Vuex.Store({
    modules: {
        menu,              // 菜单模块
        activeRouterMatch   // 动态路由匹配模块
    },
    state: {
        pageUrl: "http://www.baidu.com",
        showType: "router",
        ActionStr: [],
        token: "",
        afterRouter: "",
        cityFlagSplit: "",
        DefaultOrgunitid: null,
        // 系统模块列表
        systemData: [
            { module_name: "模块管理", toUrl: "/module" },
            { module_name: "角色管理", toUrl: "/role" },
            { module_name: "机构管理", toUrl: "/organManage" },
            { module_name: "用户管理", toUrl: "/userManage" },
        ],
        // 默认菜单数据
        menuData: [
            {
                module_name: "慢病管理",
                icon: "diff",
                children: [
                    { title: "慢病初审管理", routerName: "diseaseFirstTrial" },
                    { title: "慢病体检分配", routerName: "diseaseCheck" },
                    { title: "慢病专家分配", routerName: "proficientManage" },
                    // ... 更多菜单项
                ]
            }
        ]
    }
});

export default store;
```

### modules/menu.js 菜单模块

```javascript
export default {
    state: {
        menuCollapsed: true,      // 菜单是否折叠
        userInfo: {},             // 用户信息
        sysPermission: true,     // 系统权限
        permissions: {},          // 权限对象
        menu: []                  // 菜单列表
    },
    mutations: {
        // 切换菜单折叠状态
        toggleMenu(state) {
            state.menuCollapsed = !state.menuCollapsed;
        },
        // 更新用户信息
        updateUserInfo(state, data) {
            state.userInfo = {
                deptId: data.deptId,           // 部门ID
                roles: data.roles,             // 角色列表
                roleNames: data.roleNames,     // 角色名称
                userName: data.userName,       // 用户名
                email: data.email             // 邮箱
            };
            // 将菜单权限转换为对象，方便快速查找
            let permissions = {};
            (data.menus || []).forEach((x) => {
                x.menuCode && (permissions[x.menuCode] = x);
            });
            state.permissions = permissions;
        },
        // 更新菜单数据
        updateMenu(state, data) {
            let menus = [];
            data.forEach((ele) => {
                // 根据 menuCode 分类整理菜单
                // ...
            });
            state.menu = menus;
        }
    },
    actions: {
        // 切换菜单（提交 mutation）
        toggleMenu({ commit }) {
            commit('toggleMenu');
        }
    },
    getters: {
        // 类似计算属性，获取 state 的派生值
        menuCollapsed: state => state.menuCollapsed,
        userInfo: state => state.userInfo,
        permissions: state => state.permissions,
        menu: state => state.menu
    }
};
```

---

## 数据流（小白版）

```
┌─────────────┐      dispatch      ┌─────────────┐      commit       ┌─────────────┐
│   组件      │ ───────────────→ │    Actions   │ ───────────────→ │  Mutations   │
│             │                  │   (异步操作)  │                  │  (同步修改)   │
└─────────────┘                  └─────────────┘                  └─────────────┘
       ↑                                                                  ↓
       │                                                                  ↓
       └──────────────────── getters ────────────────────────────────────┘
```

---

## 登录流程中的状态管理

### 1. 登录成功后保存用户信息

```javascript
// 登录成功后
api.loginMb.login(params).then(res => {
    // 1. 保存登录信息
    sessionStorage.setItem("logInfoMB", encrypt(JSON.stringify(res.data)));
    
    // 2. 更新 Vuex 状态
    this.$store.commit('updateUserInfo', res.data);
    
    // 3. 加载菜单权限
    this.$store.dispatch('getRoleMenusAsync');
    
    // 4. 跳转到首页
    this.$router.push('/home');
});
```

### 2. 页面加载时恢复用户信息

```javascript
// App.vue mounted 钩子
if (!location.href.includes('loginMb')) {
    // 非登录页面，加载用户菜单
    this.$store.dispatch('getRoleMenusAsync')
}
```

---

## 常用操作示例

### 在组件中使用 state
```javascript
export default {
    computed: {
        // 获取用户信息
        userInfo() {
            return this.$store.state.menu.userInfo;
        },
        // 获取用户信息（通过 getter）
        userName() {
            return this.$store.getters.userInfo.userName;
        }
    },
    methods: {
        // 修改状态
        updateUserInfo() {
            this.$store.commit('updateUserInfo', { userName: '张三' });
        }
    }
}
```

### 在组件中调用 actions
```javascript
// 加载菜单
this.$store.dispatch('getRoleMenusAsync');

// 切换菜单折叠
this.$store.dispatch('toggleMenu');
```

---

## 持久化说明

```javascript
const createPersisted = createPersistedState({
    storage: window.sessionStorage,  // 存储在 sessionStorage
})
```

- **sessionStorage**：浏览器会话关闭后清除
- **localStorage**：永久保存，直到手动清除
- 本项目使用 sessionStorage，关闭浏览器后需要重新登录

---

## 知识点

### 🔹 Vuex 的 5 个核心概念

| 概念 | 说明 | 类比 |
|------|------|------|
| **state** | 存储状态（数据） | 仓库里的货物 |
| **getters** | 计算属性（派生的状态） | 货物的标签/分类 |
| **mutations** | 同步修改状态 | 仓库管理员（只能一个个操作） |
| **actions** | 异步操作 + 提交 mutations | 物流公司（可以批量操作） |
| **modules** | 模块化拆分 | 分仓库 |

### 🔹 为什么 mutations 要同步？

是为了方便调试：
- 同步修改 → DevTools 能准确记录每次状态变化
- 异步修改 → 不知道是哪个操作导致的状态变化

### 🔹 模块化

```javascript
modules: {
    menu,              // 菜单子模块
    activeRouterMatch  // 路由匹配子模块
}
```
- 每个模块有独立的 state、mutations、actions、getters
- 访问时：`this.$store.state.menu.userInfo`
