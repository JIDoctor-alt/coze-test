# 入口文件解析 - main.js

> 🎯 一句话说明：main.js 是程序的家门，所有配置都从这里开始

---

## 这是啥？（小白版）

想象 **main.js 是餐厅的"前台接待处"**：
- 迎接客人（初始化 Vue）
- 登记会员信息（加载各种插件）
- 分配座位（配置路由、状态管理）
- 介绍今天有什么菜（导入全局组件）

---

## 核心代码解析

### 1. 导入必要的"装备"

```javascript
import Vue from 'vue';              // 🧒 主角Vue框架
import App from './App';            // 🏠 根组件（所有页面的容器）
import router from './router';     // 🧭 路由配置（导航系统）
import store from './store';       // 💾 状态管理（记忆系统）
import Antd from 'ant-design-vue'; // 🎨 Ant Design UI组件库
```

### 2. 加载样式文件

```javascript
import './assets/ant-theme-file.less'; // 🎨 定制主题色（把界面染成PICC蓝）
import './assets/css/base.less';       // 📄 基础样式
import './assets/css/reiview.less';    // 📄 审核相关样式
```

### 3. 全局组件注册

```javascript
// 打印功能
import Print from "@/components/comPrintTable/print.js";
Vue.use(Print)

// 图片预览功能
import Viewer from 'v-viewer';
import 'viewerjs/dist/viewer.css';
Vue.use(Viewer);

// 懒加载图片插件
import lazyload from "vue-lazyload"
Vue.use(lazyload, {
    loading: require('@/assets/images/loading.png'),  // 加载中显示的图片
    error: require('@/assets/images/error.png')       // 加载失败显示的图片
});
```

### 4. 全局方法挂载

```javascript
// 弹窗提示（类似于 alert()，但更好看）
Vue.prototype.$layer = layer(Vue);

// MD5加密
Vue.prototype.$md5 = md5;

// 文件下载方法
Vue.prototype.$downloadFileByBase64 = downloadFileByBase64;
Vue.prototype.$downloadFileByBase64sl = downloadFileByBase64sl;
Vue.prototype.$downloadFileByBlobJiJ = downloadFileByBlobJiJ;

// 工具方法集合
Vue.prototype.$util = util
```

### 5. axios 配置（重要！）

```javascript
// 创建axios实例
const axios = originalAxios.create({
    baseURL: baseUrl,  // API基础地址
    headers: {
        common: {
            Authorization: getQueryString('token') || "",  // 登录令牌
            userId: getQueryString('userId') || null,      // 用户ID
            token: getQueryString('token') || "",          // 令牌
            tokenFlag: sessionStorage.getItem('tokenFlag') || 1,  // 令牌标志
        }
    }
});

// 注册为全局变量
Vue.use({
    install(vue, options) {
        vue.prototype.$axios = axios;         // HTTP请求工具
        vue.prototype.$apiList = apiList;    // API接口列表
    }
});
```

### 6. 全局组件注册

```javascript
// 头部组件
import commonHeader from './components/header.vue'
Vue.component('common-header', commonHeader);

// 拖拽模态框组件
import elContainer from "@/mtbnewcomponents/Modal/dragModal"
Vue.component('el-container', elContainer);
```

### 7. 创建Vue实例（最后一步！）

```javascript
new Vue({
    el: '#app',       // 挂载点（HTML中的<div id="app">）
    router,          // 路由
    store,           // 状态管理
    axios,           // HTTP工具
    components: { App },  // 注册根组件
    template: '<App/>'    // 使用App组件作为模板
});
```

---

## 知识点

### 🔹 import 和 require 的区别
- `import` 是 ES6 模块导入（静态分析，加载更快）
- `require` 是 CommonJS 导入（动态执行）
- 图片懒加载用 `require()` 是为了动态拼接路径

### 🔹 Vue.use() 的作用
注册插件，使其在所有组件中可用。类似于"办理会员卡"，办了之后所有门店都认识你。

### 🔹 Vue.prototype.xxx 的作用
把某个方法/变量挂载到 Vue 实例上，之后在任何组件中都可以用 `this.$xxx` 访问。

### 🔹 getQueryString() 函数
从 URL 中获取参数，比如从 `?token=abc123&userId=456` 中提取 token 值。

---

## 生命周期流程

```
页面加载
    ↓
main.js 执行
    ↓
    ├─→ 导入 Vue、插件、组件
    ├─→ 配置 axios（请求拦截器、响应拦截器）
    ├─→ 注册全局组件和方法
    ├─→ 创建 Vue 实例
    ↓
App.vue 渲染
    ↓
router-view 显示页面
```
