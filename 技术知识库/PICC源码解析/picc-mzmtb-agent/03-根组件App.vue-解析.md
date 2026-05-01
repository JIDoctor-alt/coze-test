# 根组件解析 - App.vue

> 🎯 一句话说明：App.vue 是所有页面的"外壳"，负责包裹内容和处理整体刷新

---

## 这是啥？（小白版）

想象 **App.vue 是一栋大楼的"外墙和大门"**：
- 大楼外墙 = 整体布局框架
- 大门 = 判断用户是否登录
- 进入大楼后，才能看到各个房间（页面）

---

## 核心代码解析

### template 部分

```html
<template>
    <div id="app">
        <!-- Ant Design 的国际化配置 -->
        <a-config-provider :locale="zhCN">
            <!-- 路由视图：显示当前路由对应的页面 -->
            <router-view v-if="isRouterAlive"/>
        </a-config-provider>
    </div>
</template>
```

**解释**：
- `router-view` = 路由器控制的"显示屏"，根据 URL 显示不同页面
- `isRouterAlive` = 控制页面是否显示（用于解决IE浏览器路由不跳转问题）
- `a-config-provider` = Ant Design 国际化配置

### script 部分

```javascript
export default {
    name: 'App',
    // 提供给子组件的方法
    provide() {
        return {
            reload: this.reload  // 刷新页面的方法
        }
    },
    data() {
        return {
            zhCN,  // 中文语言包
            isRouterAlive: true  // 控制页面渲染
        }
    },
    // 监听路由变化
    watch: {
        $route: {
            handler(val, oldval) {
                // 在特定环境下，路由变化时整体刷新页面
                if (process.env.NODE_ENV == 'uatMb' || process.env.NODE_ENV == 'proMb') {
                    this.reload()
                }
            },
            deep: true,
            immediate: true
        }
    },
    mounted() {
        // 如果不是登录页面，加载用户菜单权限
        if (!location.href.includes('loginMb')) {
            this.$store.dispatch('getRoleMenusAsync')
        }
        
        // 处理IE浏览器路由问题
        if (this.checkIE()) {
            window.addEventListener('hashchange', () => {
                var currentPath = window.location.hash.slice(1);
                if (this.$route.path !== currentPath) {
                    this.$router.push(currentPath)
                }
            }, false)
        }
    },
    methods: {
        // 刷新页面的方法
        reload() {
            this.isRouterAlive = false;     // 先隐藏页面
            this.$nextTick(() => {
                this.isRouterAlive = true;  // 再显示页面（实现刷新效果）
            })
        },
        // 判断是否是IE浏览器
        checkIE() {
            return '-ms-scroll-limit' in document.documentElement.style && 
                   '-ms-ime-align' in document.documentElement.style
        }
    }
}
```

---

## 知识点

### 🔹 provide / inject（依赖注入）

这是 Vue 的高级特性，类似于"广播"：
- `provide` = 祖先组件"广播"方法和数据
- `inject` = 后代组件"收听"获取

```javascript
// App.vue（祖先）提供
provide() {
    return {
        reload: this.reload
    }
}

// 子组件使用
export default {
    inject: ['reload'],  // 注入祖先提供的方法
    methods: {
        handleClick() {
            this.reload()  // 可以直接调用
        }
    }
}
```

### 🔹 hashchange 事件

监听 URL 中 `#` 后面的部分变化（Vue Router hash 模式）

### 🔹 $nextTick

等 DOM 更新完成后执行回调，用于解决"改了数据但 DOM 还没更新"的问题

---

## 组件关系图

```
┌─────────────────────────────────────────┐
│            App.vue (根组件)              │
│  ┌─────────────────────────────────┐    │
│  │  <a-config-provider>            │    │
│  │    ┌─────────────────────────┐  │    │
│  │    │  <router-view>          │  │    │
│  │    │  ┌───────────────────┐  │  │    │
│  │    │  │ 当前显示的页面     │  │  │    │
│  │    │  │ (如diseaseDeclare)│  │  │    │
│  │    │  └───────────────────┘  │  │    │
│  │    └─────────────────────────┘  │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

---

## 生命周期钩子

```
App.vue 加载
    ↓
created()      创建阶段（可以访问 data 和 methods）
    ↓
mounted()      挂载阶段（DOM 已渲染）
    ↓
    ├─→ 如果不是登录页 → 调用 getRoleMenusAsync 加载菜单
    ├─→ 如果是IE浏览器 → 监听 hashchange 事件
    ↓
路由变化时
    ↓
    ├─→ 在 uatMb 或 proMb 环境 → 执行 reload() 刷新
    ↓
用户离开或关闭页面
```
