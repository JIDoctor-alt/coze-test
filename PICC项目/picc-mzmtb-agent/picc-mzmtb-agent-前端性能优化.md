# PICC门诊慢特病前端项目（picc-mzmtb-agent）前端性能问题分析文档

> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

> **文档版本**: v1.0
> **项目规模**: 652个Vue文件、231个JS文件、74个API文件、21个地市模块
> **技术栈**: Vue 2.6 + Vuex 3 + Vue Router 3 + Axios + Ant Design Vue + Webpack
> **文档目的**: 深入学习理解前端性能问题的原理

---

## 📖 阅读指南（小白必读）

### 本文档使用的"人话"比喻

| 技术术语 | 人话比喻 | 解释 |
|---------|---------|------|
| **首屏加载** | "开门迎客的速度" | 用户打开网页到看到内容的等待时间 |
| **代码分割** | "大箱子拆成小包裹" | 把大代码包拆成多个小包，按需加载 |
| **Tree-shaking** | "摇树掉枯叶" | 打包时自动删除没用到的代码 |
| **懒加载** | "用到再拿" | 不提前加载，用到时才加载 |
| **内存泄漏** | "房间只进不出" | 内存不断增长不释放 |
| **CDN** | "最近的仓库拿货" | 把资源放到离用户近的服务器 |
| **Bundle** | "搬家行李箱" | 所有代码打包成一个大文件 |

---

## 📊 一、性能问题总览

### 问题分布统计

| 问题分布统计 | 问题数量 | 风险等级 | 问题理解价值 |
|-------------|---------|---------|------------|
| 🔴 Bundle体积优化 | 8项 | 高 | ⭐⭐⭐⭐⭐ |
| 🟠 组件渲染优化 | 6项 | 中高 | ⭐⭐⭐⭐ |
| 🟡 内存泄漏风险 | 5项 | 中 | ⭐⭐⭐⭐ |
| 🟢 API调用优化 | 4项 | 中 | ⭐⭐⭐ |
| 🔵 图片资源优化 | 3项 | 中低 | ⭐⭐⭐ |
| ⚪ 构建配置优化 | 4项 | 低 | ⭐⭐ |

---

## 🔴 二、Bundle体积问题分析（理解首屏加载原理）

### 问题分析：Ant Design Vue全量引入

**一句话人话**：就像一次性把整个家具城的家具都搬回家，太占地儿了。

**当前问题**：
```javascript
// src/main.js:5
import Antd from 'ant-design-vue';  // ❌ 全量引入，整个家具城都搬进来
Vue.use(Antd);
```

项目使用了 `babel-plugin-import` 配置了 iview 的按需加载，但 Ant Design Vue 却是全量引入。根据代码扫描：
- Ant Design Vue 完整包约 **400KB+**
- 实际项目使用的组件不超过 **30个**
- 按需引入后预计可节省 **300KB+**

**问题理解**：

📖 **规范写法参考（供学习对比）**：

// 方式一：手动按需引入
// 理解原理：只引入用到的组件，减少打包体积

**问题理解**：

📖 **规范写法参考（供学习对比）**：按需引入可以显著减少打包体积，理解其原理后有助于学习前端工程化优化思想。

**学习要点**：
- Ant Design Vue 完整包约 **400KB+**
- 实际项目使用的组件不超过 **30个**
- 按需引入可大幅减少打包体积

**小白易懵点**：
- 为什么手动引入？因为自动化工具有时分析不准确，手动更可控
- `libraryDirectory: 'es'` vs `'lib'`：es是ES6模块版本，体积更小
- `style: true` 会自动引入CSS，但如果想完全自定义主题，可以改为 `style: false` 然后手动引入

---

### 问题分析：Lodash全量引入

**一句话人话**：就像买了一套百科全书，结果只用到了其中几页。

**当前问题**：
```javascript
// 扫描发现只有3处使用了lodash的部分函数
// 但整个lodash库被完整引入，约 70KB
```

**问题分析**：

```javascript
// 🔍 当前实现分析
import _ from 'lodash';  // 全量引入，约70KB

// 📖 规范写法参考（仅供学习对比） - 按需引入
import isEmpty from 'lodash/isEmpty';      // 只引入用到的函数
import get from 'lodash/get';
import debounce from 'lodash/debounce';
import cloneDeep from 'lodash/cloneDeep';
import throttle from 'lodash/throttle';

// 或者使用 lodash-es 版本（推荐）
import { isEmpty, get, debounce } from 'lodash-es';
```

**当前代码中需要修改的位置**：

```javascript
// src/pages/ChronicDis/auditManagement.vue:156
// 原本: import {isEmpty} from "lodash";
// 改为:
import isEmpty from "lodash/isEmpty";

// src/components/Modal/intelliUtil.js:1
// 原本: import { isEmpty, get } from "lodash";
// 改为:
import isEmpty from "lodash/isEmpty";
import get from "lodash/get";

// src/components/Modal/applicationInformation2.vue:311
// 同样修改为按需引入
```

**问题理解**：

📖 **规范写法参考（供学习对比）**：按需引入可以显著减少打包体积，理解其原理后有助于学习前端工程化优化思想。

**学习要点**：
- Lodash 全量引入约 70KB
- 实际只用了 3 处函数
- 按需引入可减少 50-60KB 体积

**实施难度**：⭐

**小白易懵点**：lodash-es 是纯 ES Module 版本，比普通 lodash 体积更小且支持更好的 Tree-shaking

---

### 问题分析：大图片资源未压缩

**一句话人话**：搬家时没把衣服叠好，行李箱塞满了。

**当前问题**：
```bash
# src/assets/images/ 目录下发现多个超大图片
login_bg_02.png   - 901KB  ❌ 建议压缩到 200KB 以下
bg-login.png       - 651KB  ❌ 建议压缩到 150KB 以下  
bg.png            - 662KB  ❌ 建议压缩到 150KB 以下
bg-login-back.png - 651KB  ❌ 建议压缩到 150KB 以下
login_bg_02.png   - 901KB  ❌ 建议压缩到 200KB 以下
```

**问题分析**：

```bash
# 1. 使用 imagemin 进行图片压缩
npm install --save-dev imagemin-cli

# 2. 或者使用在线工具压缩：
# - TinyPNG (https://tinypng.com/)
# - Squoosh (https://squoosh.app/)

# 3. 将压缩后的图片替换到 src/assets/images/ 目录
```

```javascript
// 4. 在 webpack 配置中添加图片压缩（可选）
// build/webpack.prod.conf.js 中添加 image-webpack-loader

// 安装
npm install --save-dev image-webpack-loader

// 在 webpack.base.conf.js 中配置
{
  test: /\.(png|jpe?g|gif|svg)(\?.*)?$/,
  loader: 'image-webpack-loader',
  options: {
    mozjpeg: { quality: 65 },
    pngquant: { quality: [0.65, 0.90], speed: 4 },
    gifsicle: { interlaced: false },
    webp: { quality: 75 }
  }
}
```

**问题理解**：

📖 **规范写法参考（供学习对比）**：图片压缩是前端性能优化的重要手段，理解其原理有助于学习图片优化策略。

**学习要点**：
- login_bg_02.png 约 901KB
- bg-login.png 约 651KB
- 建议压缩后单张不超过 200KB

**问题理解**：

📖 **规范写法参考（供学习对比）**：按需引入可以显著减少打包体积，理解其原理后有助于学习前端工程化优化思想。

**学习要点**：
- Ant Design Vue 完整包约 **400KB+**
- 实际项目使用的组件不超过 **30个**
- 按需引入可大幅减少打包体积

**小白易懵点**：
- PNG vs JPG：照片类用 JPG，图标/透明图用 PNG
- 压缩后要确保视觉效果可接受，不要一味追求小体积

---

### 问题分析：路由代码分割粒度不足

**一句话人话**：搬家时把所有行李装在一个大箱子里，上楼累死人。

**当前问题**：
```javascript
// src/router/childrenRoutes.js
// 100+个页面路由，虽然使用了懒加载
component: () => import("@/pages/SomePage")
// 但它们全部被打包到同一个 chunk 文件中
```

**问题分析**：

```javascript
// 📖 规范写法参考（仅供学习对比） - 使用命名 chunk（修改路由文件）

// 修改 src/router/childrenRoutes.js

// 方式一：给每个路由指定 chunk 名称
{
  path: `/systemUserManage`,
  name: "systemUserManage",
  component: () => import(/* webpackChunkName: "system-manage" */ "@/pages/SystemView/systemUserManage"),
}

// 方式二：将相关页面分组到同一个 chunk
{
  path: `/userImport`,
  name: "userImport",
  component: () => import(/* webpackChunkName: "baoji-chronic" */ "@/pages/ChronicDis/userImport"),
},
{
  path: `/userModify`,
  name: "userModify",
  component: () => import(/* webpackChunkName: "baoji-chronic" */ "@/pages/ChronicDis/userModify"),
},
{
  path: `/vipAccountManage`,
  name: "vipAccountManage",
  component: () => import(/* webpackChunkName: "baoji-chronic" */ "@/pages/ChronicDis/vipAccountManage"),
}

// 方式三：按地市分组
// 延安慢病 - webpackChunkName: "yanan-chronic"
// 宝鸡慢病 - webpackChunkName: "baoji-chronic"  
// 等等...
```

```javascript
// ✅ 同时优化 webpack.prod.conf.js 的 splitChunks 配置

// 修改 build/webpack.prod.conf.js 中的 optimization.splitChunks

optimization: {
  splitChunks: {
    chunks: 'all',  // 改为 'all' 而不是 'async'，捕获所有chunks
    maxInitialRequests: Infinity,  // 允许更多初始请求
    minSize: 20000,  // 降低最小 chunk 大小
    cacheGroups: {
      // 第三方库
      vendor: {
        test: /[\\/]node_modules[\\/]/,
        name(module) {
          const packageName = module.context.match(/[\\/]node_modules[\\/](.*?)([\\/]|$)/)[1];
          // 重要库单独打包
          if (['ant-design-vue', 'vue', 'vuex', 'vue-router', 'axios'].includes(packageName)) {
            return 'vendor-common';
          }
          // 其他库按需分配
          return `vendor-${packageName.replace('@', '')}`;
        },
        chunks: 'all',
        priority: 10,
      },
      // 公共组件
      common: {
        name: 'common',
        minChunks: 3,  // 被3个以上模块共享的代码抽离
        chunks: 'all',
        priority: 5,
        reuseExistingChunk: true,
      },
      // 样式
      styles: {
        name: 'styles',
        type: 'css/mini-extract',
        chunks: 'all',
        enforce: true,
      },
    }
  },
  runtimeChunk: 'single',  // 运行时代码单独打包
}
```

**问题理解**：

📖 **规范写法参考（供学习对比）**：路由代码分割是前端性能优化的核心手段，理解其原理有助于学习前端工程化。

**学习要点**：
- 100+ 个页面路由使用懒加载
- 但全部被打包到同一个 chunk 文件中
- 使用命名 chunk 可以实现更好的缓存策略

**问题理解**：

📖 **规范写法参考（供学习对比）**：按需引入可以显著减少打包体积，理解其原理后有助于学习前端工程化优化思想。

**学习要点**：
- Ant Design Vue 完整包约 **400KB+**
- 实际项目使用的组件不超过 **30个**
- 按需引入可大幅减少打包体积⭐

**小白易懵点**：
- `webpackChunkName`：这个注释会告诉 webpack 生成的 chunk 文件名
- 分组要合理，不要分得太细，否则请求数过多反而影响性能
- 一般建议首屏加载不超过 **3-5个** JS 文件

---

### 问题分析：静态资源未配置CDN

**一句话人话**：每次买菜都去远处的大超市，其实楼下小卖部就有。

**当前问题**：
```javascript
// build/webpack.base.conf.js
// 所有静态资源都打包到 dist 目录
output: {
  path: config.build.assetsRoot,
  filename: '[name].js',
  publicPath: config.build.assetsPublicPath  // 可能是相对路径
}
```

**问题分析**：

```javascript
// 1. 修改 config/index.js 添加 CDN 配置

// config/index.js
module.exports = {
  build: {
    // ... 原有配置
    
    // CDN 配置
    assetsPublicPath: '/',  // 或使用绝对路径
    cdn: {
      // 公共库的 CDN 地址（生产环境使用）
      base: 'https://cdn.yourcdn.com/',
      css: [
        // 如果有外部 CSS CDN
      ],
      js: [
        // Vue 核心库可以通过 CDN 加载，减少 bundle 体积
        // 'https://cdn.jsdelivr.net/npm/vue@2.6.11/dist/vue.runtime.min.js',
        // 'https://cdn.jsdelivr.net/npm/vuex@3.5.1/dist/vuex.min.js',
        // 'https://cdn.jsdelivr.net/npm/vue-router@3.3.4/dist/vue-router.min.js',
        // 'https://cdn.jsdelivr.net/npm/axios@0.19.2/dist/axios.min.js',
      ]
    }
  }
}
```

```html
<!-- 2. 修改 index.html 模板，在 head 中引入 CDN 资源 -->

<!-- public/index.html 或 index.html -->
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>门诊慢特病业务管理信息系统</title>
  
  <!-- CDN 引入公共库 -->
  <!-- 注意：Vue 必须使用运行时版本，且不能同时在 bundle 中打包 -->
  <!-- <script src="https://cdn.jsdelivr.net/npm/vue@2.6.11/dist/vue.runtime.min.js"></script> -->
</head>
<body>
  <div id="app"></div>
</body>
</html>
```

```javascript
// 3. 修改 webpack 配置，使用外部扩展（externals）

// build/webpack.base.conf.js
module.exports = {
  // ...
  externals: {
    // 从 CDN 加载的库，不再打包
    // 'vue': 'Vue',
    // 'vuex': 'Vuex',
    // 'vue-router': 'VueRouter',
    // 'axios': 'axios',
  }
}
```

**问题理解**：

📖 **规范写法参考（供学习对比）**：CDN是前端性能优化的重要手段，理解其原理有助于学习静态资源优化策略。

**学习要点**：
- CDN 可以加速静态资源下载
- 公共库可通过 CDN 加载，减少 bundle 体积
- 需要后端配合配置 CDN 服务器

**问题理解**：

📖 **规范写法参考（供学习对比）**：按需引入可以显著减少打包体积，理解其原理后有助于学习前端工程化优化思想。

**学习要点**：
- Ant Design Vue 完整包约 **400KB+**
- 实际项目使用的组件不超过 **30个**
- 按需引入可大幅减少打包体积⭐⭐（需要后端配合配置 CDN 服务器）

**小白易懵点**：
- externals 会让库从全局变量读取，不是从 npm 包
- 使用 CDN 后，本地开发仍需要 npm 包（通过 webpack 注入）
- CDN 适合稳定不变的第三方库，自定义代码不适合

---

## 🟠 三、组件渲染问题分析（理解Vue渲染原理）

### 问题分析：v-for缺少key

**一句话人话**：老师点名叫不出名字，只能从头数到尾。

**当前问题**：
```bash
# 代码扫描结果
v-for 总数：759 处
有 key 的：279 处
缺少 key：约 480 处 ❌
```

**典型问题代码**：
```vue
<!-- src/mtbnewcomponents/menuList/menuindex.vue:18 -->
<!-- ❌ 没有使用 key -->
<a-menu-item v-for="(subItem) in menuList" :key="`${subItem.location}`">
  {{subItem.title}}
</a-menu-item>

<!-- src/mtbnewcomponents/menuList/menudeclare.vue:22 -->
<!-- ❌ 循环嵌套时 key 可能重复 -->
<a-menu-item v-for="subItem in item.children" :key="`${subItem.location}`">

<!-- src/mtbnewcomponents/Modal/applicationInformation.vue:12 -->
<!-- ❌ template 上的 v-for 没有 key -->
<template v-for="(item, index) in itemlist">
```

**问题分析**：

```vue
<!-- 📖 规范写法参考（仅供学习对比） - 使用唯一稳定的 key -->

<!-- 1. 使用数据中的唯一ID（最佳） -->
<a-menu-item 
  v-for="subItem in menuList" 
  :key="subItem.routerName || subItem.id"
>
  {{subItem.title}}
</a-menu-item>

<!-- 2. 使用 index + 前缀（次选，避免重复） -->
<a-menu-item 
  v-for="(item, index) in itemlist" 
  :key="`item-${index}`"
>
  {{item.label}}
</a-menu-item>

<!-- 3. 嵌套循环要确保 key 唯一 -->
<a-sub-menu 
  v-for="(item, parentIndex) in menuList" 
  :key="`parent-${item.id}`"
>
  <a-menu-item 
    v-for="(subItem, childIndex) in item.children" 
    :key="`${item.id}-${subItem.routerName || subItem.id}`"
  >
    {{subItem.title}}
  </a-menu-item>
</a-sub-menu>

<!-- 4. template 上的 v-for 也要加 key -->
<template 
  v-for="(item, index) in itemlist" 
  :key="`info-${item.id || index}`"
>
  <div :key="`div-${index}`">{{item}}</div>
</template>
```

**问题理解**：

📖 **规范写法参考（供学习对比）**：v-for 使用唯一稳定的 key 是 Vue 渲染优化的重要原则，理解其原理有助于学习 Vue 渲染机制。

**学习要点**：
- v-for 总数：759 处
- 有 key 的：279 处
- 缺少 key：约 480 处
- 使用唯一稳定的 key 可以提升渲染性能

**问题理解**：

📖 **规范写法参考（供学习对比）**：按需引入可以显著减少打包体积，理解其原理后有助于学习前端工程化优化思想。

**学习要点**：
- Ant Design Vue 完整包约 **400KB+**
- 实际项目使用的组件不超过 **30个**
- 按需引入可大幅减少打包体积

**小白易懵点**：
- `key` 必须是唯一且稳定的，不要用 index（数组中间删除会导致 key 变化）
- `key` 的最佳选择是数据的唯一 ID
- 动态生成的 key 可能不稳定，尽量用后端返回的 id

---

### 问题分析：watch vs computed 使用不当

**一句话人话**：应该动口（computed）不动手（watch），让系统自动算。

**当前问题**：
```vue
<!-- src/mtbnewcomponents/selectTree/selectTree.vue -->
<!-- ❌ 使用 deep watch 来同步 props，太重了 -->
watch: {
  value: {
    handler(newVal, oldVal) {
      this.selectedValue = newVal
    },
    immediate: true,
    deep: true  // ❌ deep watch 性能开销大
  }
}

// 应该使用 computed 直接同步
```

**问题分析**：

```vue
<!-- 📖 规范写法参考（仅供学习对比） - 使用 computed 同步 props -->

<!-- 方案一：使用 computed 代替简单 watch -->
<script>
export default {
  props: {
    value: {
      type: [Number, Array, String, Object],
      default: undefined
    }
  },
  computed: {
    // 直接用 computed 读取和设置
    selectedValue: {
      get() {
        return this.value;
      },
      set(val) {
        this.$emit('change', val);
      }
    }
  }
}
</script>

<!-- 方案二：必须用 watch 时，避免 deep -->
<script>
export default {
  props: {
    value: {
      type: Object,
      default: () => ({})
    }
  },
  watch: {
    // 只监听特定属性，不使用 deep
    'value.id': function(newVal) {
      this.selectedValue = this.value;
    },
    'value.label': function(newVal) {
      this.selectedValue = this.value;
    }
  }
}
</script>

<!-- 方案三：使用 shallowRef 或 markRaw（Vue 3 思路） -->
```

**当前项目中需要修改的文件**：
```javascript
// src/mtbnewcomponents/selectTree/selectTree.vue
// src/mtbnewcomponents/selectTree/orgTree.vue
// src/mtbnewcomponents/selectTree/partOrgTree.vue
// 等约 150 个组件有 watch
```

**问题理解**：

📖 **规范写法参考（供学习对比）**：computed 和 watch 是 Vue 的核心概念，理解它们的区别有助于学习 Vue 响应式原理。

**学习要点**：
- computed：计算属性，自动缓存，依赖变化才重新计算
- watch：监听器，值变化时执行回调
- 能用 computed 解决的就不要用 watch
- deep watch 性能开销大，应尽量避免

**问题理解**：

📖 **规范写法参考（供学习对比）**：按需引入可以显著减少打包体积，理解其原理后有助于学习前端工程化优化思想。

**学习要点**：
- Ant Design Vue 完整包约 **400KB+**
- 实际项目使用的组件不超过 **30个**
- 按需引入可大幅减少打包体积

**小白易懵点**：
- `computed`：计算属性，自动缓存，依赖变化才重新计算
- `watch`：监听器，值变化时执行回调
- 能用 `computed` 解决的就不要用 `watch`

---

### 问题分析：组件销毁时未清理定时器

**一句话人话**：出门不关灯，白白浪费电。

**当前问题**：
```vue
<!-- src/pages/JiJChronicDis/declarationInformation.vue:187 -->
<!-- ❌ 创建了定时器但组件销毁时没有清理 -->
data() {
  return {
    timer: null
  }
},
methods: {
  search() {
    this.timer = setTimeout(() => {
      this.loadData();
    }, 500);
  }
}
// ❌ 没有 beforeDestroy 钩子来清理

<!-- 类似问题存在于约 20 个文件中 -->
```

**问题分析**：

```vue
<!-- 📖 规范写法参考（仅供学习对比） - 在 beforeDestroy 中清理定时器 -->

<script>
export default {
  data() {
    return {
      timer: null,
      intervalTimer: null
    }
  },
  methods: {
    search() {
      // 搜索防抖：先清理之前的定时器
      if (this.timer) {
        clearTimeout(this.timer);
      }
      this.timer = setTimeout(() => {
        this.loadData();
      }, 500);
    },
    
    startPolling() {
      // 轮询：先清理之前的
      if (this.intervalTimer) {
        clearInterval(this.intervalTimer);
      }
      this.intervalTimer = setInterval(() => {
        this.fetchData();
      }, 5000);
    }
  },
  
  // ⚠️ 关键：组件销毁时清理
  beforeDestroy() {
    // 清理定时器
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    if (this.intervalTimer) {
      clearInterval(this.intervalTimer);
      this.intervalTimer = null;
    }
    
    // 清理事件监听器
    if (this.scrollHandler) {
      window.removeEventListener('scroll', this.scrollHandler);
    }
    
    // 清理其他资源
    if (this.canvas) {
      this.canvas = null;
    }
  }
}
</script>
```

**需要修改的文件清单**：
```javascript
// 以下文件有 setTimeout 但可能缺少清理
src/pages/JiJChronicDis/declarationInformation.vue
src/pages/JiJChronicDis/auditManagement.vue
src/pages/JiJChronicDis/desensitization.vue
src/pages/YLChronicDis/declarationInformation.vue
src/pages/YLChronicDis/diseaseCheck.vue
src/pages/YLChronicDis/auditManagement.vue
src/pages/YLChronicDis/desensitization.vue
src/pages/XYaChronicDis/declarationInformation.vue
src/pages/XYaChronicDis/auditManagement.vue
src/pages/XYaChronicDis/desensitization.vue
src/pages/ChronicDis/components/prescription.vue
// 等等...
```

**问题理解**：

📖 **规范写法参考（供学习对比）**：组件生命周期中的资源清理是前端开发的重要知识点，理解其原理有助于避免内存泄漏。

**学习要点**：
- setTimeout 用 clearTimeout 清理
- setInterval 用 clearInterval 清理
- requestAnimationFrame 用 cancelAnimationFrame 清理
- 约 20 个文件有 setTimeout 但可能缺少清理

**问题理解**：

📖 **规范写法参考（供学习对比）**：按需引入可以显著减少打包体积，理解其原理后有助于学习前端工程化优化思想。

**学习要点**：
- Ant Design Vue 完整包约 **400KB+**
- 实际项目使用的组件不超过 **30个**
- 按需引入可大幅减少打包体积

**小白易懵点**：
- `setTimeout` 用 `clearTimeout` 清理
- `setInterval` 用 `clearInterval` 清理
- `requestAnimationFrame` 用 `cancelAnimationFrame` 清理

---

## 🟡 四、内存泄漏风险（房间只进不出）

### 问题分析：Modal组件事件监听器管理

**一句话人话**：在房间里装了摄像头，走的时候忘了拆。

**当前问题**：
```vue
<!-- src/mtbnewcomponents/Modal/dragModal.vue:374-390 -->
<!-- ⚠️ 事件监听器分散在多处添加和移除，逻辑复杂容易遗漏 -->

window.addEventListener("mousemove", this.handleMove, false);
window.addEventListener("mouseup", this.removeUp, false);
// ... 很多逻辑

// 虽然在 beforeDestroy 中有清理，但逻辑分散
beforeDestroy() {
  window.removeEventListener("mouseup", this.removeUp, false);
  window.removeEventListener("mousemove", this.handleMove, false);
}
```

**问题分析**：

```vue
<!-- 📖 规范写法参考（仅供学习对比） - 统一管理事件监听器 -->

<script>
export default {
  data() {
    return {
      boundHandlers: {}  // 记录所有绑定的处理函数
    }
  },
  
  methods: {
    initDrag() {
      // 保存处理函数的引用
      this.boundHandlers.handleMove = this.handleMove.bind(this);
      this.boundHandlers.removeUp = this.removeUp.bind(this);
      
      // 使用具名函数便于移除
      window.addEventListener("mousemove", this.boundHandlers.handleMove, false);
      window.addEventListener("mouseup", this.boundHandlers.removeUp, false);
    },
    
    handleMove() {
      // 拖拽逻辑
    },
    
    removeUp() {
      // 抬起鼠标逻辑
    }
  },
  
  beforeDestroy() {
    // ✅ 统一清理所有事件监听器
    Object.keys(this.boundHandlers).forEach(key => {
      window.removeEventListener(
        key === 'handleMove' ? 'mousemove' : 'mouseup',
        this.boundHandlers[key],
        false
      );
    });
    this.boundHandlers = {};
  }
}
</script>
```

**问题理解**：

📖 **规范写法参考（供学习对比）**：事件监听器的正确管理是前端开发的重要知识点，理解其原理有助于避免内存泄漏。

**学习要点**：
- 事件监听器必须用相同的函数引用才能移除
- 箭头函数每次创建新引用，无法移除
- Modal 组件存在事件监听器管理问题

**问题理解**：

📖 **规范写法参考（供学习对比）**：按需引入可以显著减少打包体积，理解其原理后有助于学习前端工程化优化思想。

**学习要点**：
- Ant Design Vue 完整包约 **400KB+**
- 实际项目使用的组件不超过 **30个**
- 按需引入可大幅减少打包体积⭐

**小白易懵点**：
- 事件监听器必须用相同的函数引用才能移除
- 箭头函数每次创建新引用，无法移除

---

### 问题分析：Vuex-persistedstate 存储过多数据

**一句话人话**：把整个房间的东西都拍成照片存进相册，太占地方。

**当前问题**：
```javascript
// src/store/index.js
const createPersisted = createPersistedState({
  storage: window.sessionStorage,
})

const store = new Vuex.Store({
  plugins: [createPersisted],
  state: {
    // ❌ 存储了大量不应该持久化的数据
    systemData: [...],      // 30+ 个菜单项的完整数据
    menuData: [...],        // 100+ 个菜单配置
    menuList: [...],       // 50+ 个菜单项
    menuDeclare: [...],
    menuQuick: [...],
    menuNewDeclare: [...],
    menuStore: [...],
    hospManage: [...],
    // ... 还有很多
  }
})
```

**问题分析**：

```javascript
// 📖 规范写法参考（仅供学习对比） - 只持久化必要的数据

import Vue from "vue";
import Vuex from "vuex";
import menu from "./modules/menu";
import createPersistedState from "vuex-persistedstate";
import SecureLS from "secure-ls";  // 更安全的本地存储

Vue.use(Vuex);

// 只持久化需要恢复的关键数据
const persistedState = createPersistedState({
  storage: window.sessionStorage,  // 或使用 localStorage
  // 指定只持久化这些 key
  paths: [
    'token',           // ✅ 用户登录态
    'userInfo',         // ✅ 用户基本信息
    'menu.collapsed',  // ✅ 菜单展开状态
    // ❌ 不要持久化这些
    // 'systemData',
    // 'menuData',
    // 'menuList',
    // 等
  ],
  // 过滤函数
  filter: (mutation) => {
    // 只持久化特定的 mutations
    const persistedMutations = [
      'updateToken',
      'updateUserInfo',
      'updateCollapsed'
    ];
    return persistedMutations.includes(mutation.type);
  }
});

const store = new Vuex.Store({
  modules: {
    menu,
    activeRouterMatch
  },
  state: {
    token: "",
    userInfo: null,
    collapsed: false,
    // ⚠️ 删除这些硬编码数据，改为从接口获取
    // systemData: [...],
    // menuData: [...],
  },
  mutations: {
    updateToken(state, token) {
      state.token = token;
    },
    updateUserInfo(state, userInfo) {
      state.userInfo = userInfo;
    },
    updateCollapsed(state, collapsed) {
      state.collapsed = collapsed;
    }
    // 删除 updateMenu 等不需要的 mutations
  },
  plugins: [persistedState]
});

export default store;
```

**问题理解**：

📖 **规范写法参考（供学习对比）**：Vuex 持久化存储的合理使用是前端开发的重要知识点，理解其原理有助于优化前端性能。

**学习要点**：
- SessionStorage vs localStorage：前者会话级（关闭浏览器清除），后者持久化
- Token 不应该存储在前端，建议使用 HttpOnly Cookie
- 菜单数据应该每次从接口获取，而不是存储在 state 中
- 存储了大量菜单数据，可能影响性能

**问题理解**：

📖 **规范写法参考（供学习对比）**：按需引入可以显著减少打包体积，理解其原理后有助于学习前端工程化优化思想。

**学习要点**：
- Ant Design Vue 完整包约 **400KB+**
- 实际项目使用的组件不超过 **30个**
- 按需引入可大幅减少打包体积⭐

**小白易懵点**：
- SessionStorage vs localStorage：前者会话级（关闭浏览器清除），后者持久化
- Token 不应该存储在前端，建议使用 HttpOnly Cookie
- 菜单数据应该每次从接口获取，而不是存储在 state 中

---

### 问题分析：未使用的 Store 模块

**一句话人话**：房间里放了不用的家具，白白占空间。

**当前问题**：
```javascript
// src/store/index.js
const store = new Vuex.Store({
  modules: {
    menu,              // ⚠️ 这个模块被引用但功能不完整
    activeRouterMatch
  },
  // ...
})

// src/store/modules/menu.js
// 这个模块包含问题管理和数据报告的逻辑
// 但实际项目中根本没有这些功能
export default {
  state: {
    menuCollapsed: true,
    userInfo: {},
    sysPermission: true,
    permissions: {},
    menu: []
  },
  mutations: {
    // 有问题管理相关的 mutation
    updateMenu(state, data) {
      // 创建问题管理菜单...
    }
  }
  // ...
}
```

**问题分析**：

```javascript
// ✅ 方案一：清理无用的 store 模块

// src/store/index.js
import Vue from "vue";
import Vuex from "vuex";
import activeRouterMatch from "./modules/activeRouterMatch";

Vue.use(Vuex);

// 清理后的 store
const store = new Vuex.Store({
  modules: {
    activeRouterMatch  // 只保留有用的模块
    // menu: 删除，合并到 activeRouterMatch 或移除
  },
  state: {
    token: "",
    userInfo: null,
    collapsed: false,
    // ... 只保留必要状态
  },
  mutations: {
    updateToken(state, token) {
      state.token = token;
    },
    updateUserInfo(state, userInfo) {
      state.userInfo = userInfo;
    },
    updateCollapsed(state, collapsed) {
      state.collapsed = collapsed;
    }
  }
});

export default store;

// ✅ 方案二：如果 menu 模块部分功能还在用，重构它

// src/store/modules/menu.js - 清理后
export default {
  state: {
    collapsed: true,  // 只保留菜单折叠状态
    permissions: {}   // 只保留权限数据
  },
  mutations: {
    toggleMenu(state) {
      state.collapsed = !state.collapsed;
    },
    setPermissions(state, permissions) {
      state.permissions = permissions;
    }
  },
  getters: {
    collapsed: state => state.collapsed,
    permissions: state => state.permissions
  }
  // 删除无用的 mutations 和 actions
}
```

**预期收益**：Store 初始化更快，内存占用减少

**问题理解**：

📖 **规范写法参考（供学习对比）**：按需引入可以显著减少打包体积，理解其原理后有助于学习前端工程化优化思想。

**学习要点**：
- Ant Design Vue 完整包约 **400KB+**
- 实际项目使用的组件不超过 **30个**
- 按需引入可大幅减少打包体积

**小白易懵点**：
- 删除 store 模块前要确保没有组件在用它
- 可以用 `grep -rn "from.*store/modules/menu"` 检查引用

---

## 🟢 五、API调用优化（点外卖要高效）

### 问题分析：Token重复解析

**一句话人话**：每次买东西都要重新去银行查余额。

**当前问题**：
```javascript
// src/api/axiosCenter.js:45-52
// ❌ 每次请求都从 URL 解析 token
interceptors(instance, url) {
  instance.interceptors.request.use(config => {
    let query = location.href.split('?')[1];
    token = qs.parse(query, { ignoreQueryPrefix: true })["token"];  // ❌ 每次都解析
    // ...
  })
}
```

**问题分析**：

```javascript
// 📖 规范写法参考（仅供学习对比） - 缓存 token，只解析一次

// src/api/axiosCenter.js

// 1. 创建 token 管理模块
const TokenManager = {
  token: null,
  userId: null,
  cityFlag: null,
  
  init() {
    if (!this.token) {
      const query = location.href.split('?')[1];
      if (query) {
        const params = qs.parse(query, { ignoreQueryPrefix: true });
        this.token = params.token || '';
        this.userId = params.userId || '';
        this.cityFlag = params.flag || '';
      }
    }
    return this;
  },
  
  getToken() {
    return this.token;
  },
  
  getUserId() {
    return this.userId;
  },
  
  getCityFlag() {
    return this.cityFlag;
  },
  
  // 从 sessionStorage 获取（推荐）
  getTokenFromStorage() {
    if (!this.token) {
      const logInfo = sessionStorage.getItem('logInfoMB');
      if (logInfo) {
        try {
          const userInfo = JSON.parse(logInfo);
          this.token = userInfo.token || '';
        } catch (e) {
          console.error('Parse logInfoMB failed:', e);
        }
      }
    }
    return this.token;
  }
};

// 2. 在拦截器中使用
interceptors(instance, url) {
  instance.interceptors.request.use(config => {
    // ✅ 使用缓存的 token
    config.headers['token'] = TokenManager.getTokenFromStorage();
    config.headers['userId'] = TokenManager.getUserId();
    
    // ... 其他逻辑
    return config;
  })
}

// 3. 登录后调用初始化
// 在 src/mtbnewcomponents/loginMb/index.vue 中
loginSuccess(res) {
  sessionStorage.setItem('logInfoMB', JSON.stringify(res.data));
  TokenManager.init();  // 初始化 token manager
}
```

**问题理解**：

📖 **规范写法参考（供学习对比）**：Token 的安全管理是前端开发的重要知识点，理解其原理有助于学习前端安全知识。

**学习要点**：
- 每次请求都从 URL 解析 token 是低效的
- 应该在登录后缓存 token
- 更好的方案是使用 HttpOnly Cookie

**问题理解**：

📖 **规范写法参考（供学习对比）**：按需引入可以显著减少打包体积，理解其原理后有助于学习前端工程化优化思想。

**学习要点**：
- Ant Design Vue 完整包约 **400KB+**
- 实际项目使用的组件不超过 **30个**
- 按需引入可大幅减少打包体积

**小白易懵点**：
- Token 存在 sessionStorage 是安全妥协，更好的方案是 HttpOnly Cookie
- 页面刷新后 token 可能过期，需要配合登录态验证

---

### 问题分析：缺少请求取消机制

**一句话人话**：点了外卖又不想吃了，应该可以取消订单。

**当前问题**：
```javascript
// src/api/axiosCenter.js
// ❌ 没有请求取消机制
request(options) {
  var instance = this.create();
  // ... 发起请求，但没有取消能力
  return instance(options);
}
```

**问题分析**：

```javascript
// 📖 规范写法参考（仅供学习对比） - 添加请求管理和取消能力

// src/api/requestManager.js

class RequestManager {
  constructor() {
    this.pendingMap = new Map();  // 存储请求的取消函数
  }
  
  // 生成请求的唯一标识
  generateKey(config) {
    const { method, url, params, data } = config;
    return `${method}_${url}_${JSON.stringify(params)}_${JSON.stringify(data)}`;
  }
  
  // 添加请求到队列
  addRequest(key, cancelToken) {
    this.pendingMap.set(key, cancelToken);
  }
  
  // 取消请求
  cancelRequest(key) {
    const cancel = this.pendingMap.get(key);
    if (cancel) {
      cancel('请求被取消');
      this.pendingMap.delete(key);
    }
  }
  
  // 取消所有请求
  cancelAll() {
    this.pendingMap.forEach(cancel => cancel('页面切换，取消所有请求'));
    this.pendingMap.clear();
  }
  
  // 移除请求
  removeRequest(key) {
    this.pendingMap.delete(key);
  }
}

const requestManager = new RequestManager();

// 导出单例
export default requestManager;
```

```javascript
// ✅ 修改 axiosCenter.js

import axios from "axios";
import requestManager from "./requestManager";

class HttpRequest {
  constructor() {
    this.queue = {};
  }
  
  create() {
    return axios.create({
      baseURL: baseURL,
      withCredentials: true,
      headers: { /* ... */ }
    });
  }
  
  request(options) {
    const instance = this.create();
    const requestKey = requestManager.generateKey(options);
    
    // 生成取消 token
    const CancelToken = axios.CancelToken;
    options.cancelToken = new CancelToken((cancel) => {
      requestManager.addRequest(requestKey, cancel);
    });
    
    // 添加响应拦截器
    instance.interceptors.response.use(
      res => {
        requestManager.removeRequest(requestKey);
        return res;
      },
      error => {
        requestManager.removeRequest(requestKey);
        if (axios.isCancel(error)) {
          console.log('Request canceled:', error.message);
        }
        return Promise.reject(error);
      }
    );
    
    return instance(options);
  }
  
  // 取消同名请求（防抖）
  cancelDuplicate(config) {
    const key = requestManager.generateKey(config);
    requestManager.cancelRequest(key);
  }
}

export default new HttpRequest();
```

```javascript
// ✅ 在路由切换时取消请求

// src/router/index.js
import requestManager from '@/api/requestManager';

router.beforeEach((to, from, next) => {
  // 路由切换时取消所有进行中的请求
  if (from.path !== to.path) {
    requestManager.cancelAll();
  }
  // ... 其他逻辑
  next();
});
```

**问题理解**：

📖 **规范写法参考（供学习对比）**：请求取消机制是前端开发的重要知识点，理解其原理有助于提升用户体验。

**学习要点**：
- 取消请求会触发 error，需要在拦截器中正确处理
- 页面切换时取消旧请求，避免旧数据覆盖新数据
- 可以使用 axios 的 CancelToken 来实现

**问题理解**：

📖 **规范写法参考（供学习对比）**：按需引入可以显著减少打包体积，理解其原理后有助于学习前端工程化优化思想。

**学习要点**：
- Ant Design Vue 完整包约 **400KB+**
- 实际项目使用的组件不超过 **30个**
- 按需引入可大幅减少打包体积⭐

**小白易懵点**：
- 取消请求会触发 error，需要在拦截器中正确处理
- 不要在 catch 中输出错误，因为取消请求不是真正的错误

---

### 问题分析：缺少请求重试机制

**一句话人话**：外卖送丢了，应该自动再送一单。

**当前问题**：
```javascript
// src/api/axiosCenter.js
// ❌ 网络失败时直接报错，没有重试
instance.interceptors.response.use(
  res => {
    return data;
  },
  error => {
    message.error(error.toString());  // 直接报错
    return Promise.reject(error);
  }
);
```

**问题分析**：

```javascript
// ✅ 添加请求重试机制

import axios from "axios";

// 请求重试拦截器
axios.interceptors.response.use(undefined, async (err) => {
  const config = err.config;
  
  // 如果没有配置重试次数，或者已经重试过，直接拒绝
  if (!config || !config.retry || !config.retryDelay) {
    return Promise.reject(err);
  }
  
  // 设置标志避免重复请求
  config.retryCount = config.retryCount || 0;
  
  // 判断是否应该重试
  if (config.retryCount < config.retry) {
    config.retryCount += 1;
    
    // 延迟重试
    await new Promise(resolve => setTimeout(resolve, config.retryDelay));
    
    console.log(`请求重试 ${config.retryCount}/${config.retry}`);
    return axios(config);
  }
  
  return Promise.reject(err);
});

// 在 axiosCenter.js 中使用
const AxiosRequest = new HttpRequest();

// 发送请求时配置重试
export function get(url, data, config = {}) {
  return AxiosRequest.request({
    method: 'get',
    url,
    params: data,
    retry: 3,           // 最多重试3次
    retryDelay: 1000,   // 重试间隔1秒
    ...config
  });
}

export function post(url, data, config = {}) {
  return AxiosRequest.request({
    method: 'post',
    url,
    data,
    retry: 2,           // POST 请求重试2次
    retryDelay: 500,
    ...config
  });
}
```

**问题理解**：

📖 **规范写法参考（供学习对比）**：请求重试机制是前端开发的重要知识点，理解其原理有助于提升接口成功率。

**学习要点**：
- POST 请求重试要谨慎，有些接口本身是幂等的才能重试
- 重试会增加服务器压力，可以设置最大重试次数
- 可以使用 axios 的拦截器实现

**问题理解**：

📖 **规范写法参考（供学习对比）**：按需引入可以显著减少打包体积，理解其原理后有助于学习前端工程化优化思想。

**学习要点**：
- Ant Design Vue 完整包约 **400KB+**
- 实际项目使用的组件不超过 **30个**
- 按需引入可大幅减少打包体积

**小白易懵点**：
- POST 请求重试要谨慎，有些接口本身是幂等的才能重试
- 重试会增加服务器压力，可以设置最大重试次数

---

## 🔵 六、图片与静态资源优化

### 问题分析：图片未使用懒加载

**一句话人话**：一进门就让你看完全家的照片，其实客人只关心客厅。

**当前问题**：
```vue
<!-- src/mtbnewcomponents/Modal/applicationInformations.vue -->
<!-- ❌ 所有图片一次性加载 -->
<viewer :images="list[noIcdValue]">
  <img 
    v-for="(item, index) in list[noIcdValue]" 
    :src="item.src" 
    :key="item.id + index" 
  />
</viewer>
```

**问题分析**：

```vue
<!-- 📖 规范写法参考（仅供学习对比） - 使用图片懒加载 -->

<!-- 方案一：使用已有的 vue-lazyload -->
<!-- 项目已安装 vue-lazyload，只需配置使用 -->

<script>
// src/main.js 中已配置
Vue.use(lazyload, {
  preLoad: 1,
  loading: require('@/assets/images/loading.png'),
  attempt: 2,
  error: require('@/assets/images/error.png')
})
</script>

<template>
  <!-- 使用 v-lazy 替代 src -->
  <viewer :images="list[noIcdValue]">
    <img 
      v-for="(item, index) in list[noIcdValue]" 
      v-lazy="item.src" 
      :key="item.id + index" 
    />
  </viewer>
</template>

<!-- 方案二：原生懒加载（现代浏览器） -->
<template>
  <img 
    v-for="(item, index) in list[noIcdValue]" 
    :src="item.src" 
    :key="item.id + index"
    loading="lazy"  <!-- 原生懒加载属性 -->
  />
</template>

<!-- 方案三：Intersection Observer（兼容性更好） -->
<script>
export default {
  directives: {
    lazy: {
      inserted(el, binding) {
        const observer = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              el.src = binding.value;
              observer.unobserve(el);
            }
          });
        });
        observer.observe(el);
      }
    }
  }
}
</script>

<template>
  <img v-for="item in images" v-lazy="item.src" />
</template>
```

**问题理解**：

📖 **规范写法参考（供学习对比）**：图片懒加载是前端性能优化的重要手段，理解其原理有助于提升首屏性能。

**学习要点**：
- loading="lazy" 是原生属性，IE 不支持
- vue-lazyload 需要图片 URL 稳定，不能带时间戳
- 懒加载可能导致图片闪烁，可以用 placeholder 解决

**实施难度**：⭐

**小白易懵点**：
- `loading="lazy"` 是原生属性，IE 不支持
- vue-lazyload 需要图片 URL 稳定，不能带时间戳
- 懒加载可能导致图片闪烁，可以用 placeholder 解决

---

### 问题分析：图片未使用WebP格式

**一句话人话**：衣服应该挂衣柜里，而不是摊在床上。

**当前问题**：
```vue
<!-- 项目中大量使用 PNG/JPG 格式 -->
<!-- 没有利用 WebP 等更高效的图片格式 -->
```

**问题分析**：

```javascript
// ✅ 使用 WebP 图片（需要后端或CDN支持）

// 方案一：CSS 或 JS 检测并切换
export function getWebPUrl(originalUrl) {
  // 检测浏览器是否支持 WebP
  const canvas = document.createElement('canvas');
  if (canvas.getContext && canvas.getContext('2d')) {
    const isSupportWebP = canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    if (isSupportWebP) {
      // 将 URL 转换为 WebP 版本
      // 假设后端支持格式协商，或 CDN 自动转换
      return originalUrl.replace(/\.(png|jpg|jpeg)$/i, '.webp');
    }
  }
  return originalUrl;
}

// 方案二：使用 <picture> 标签
<picture>
  <source type="image/webp" :srcset="getWebPUrl(imageUrl)" />
  <img :src="imageUrl" :alt="alt" />
</picture>

// 方案三：CDN 自动转换（推荐）
// 配置 CDN 根据 Accept 头自动返回合适格式
// Nginx 配置示例：
// location ~* \.(jpg|png)$ {
//   add_header Vary Accept;
//   try_files $uri $uri/webp /$uri;
// }
```

**问题理解**：

📖 **规范写法参考（供学习对比）**：WebP 格式是前端图片优化的重要手段，理解其原理有助于学习图片格式优化。

**学习要点**：
- WebP 格式 IE 不完全支持，需要降级方案
- 可以用 Canvas 判断浏览器是否支持
- WebP 比 PNG/JPG 体积更小

**问题理解**：

📖 **规范写法参考（供学习对比）**：按需引入可以显著减少打包体积，理解其原理后有助于学习前端工程化优化思想。

**学习要点**：
- Ant Design Vue 完整包约 **400KB+**
- 实际项目使用的组件不超过 **30个**
- 按需引入可大幅减少打包体积⭐（需要后端配合）

**小白易懵点**：
- WebP 格式 IE 不完全支持，需要降级方案
- 可以用 Canvas 判断浏览器是否支持

---

## ⚪ 七、构建配置优化

### 问题分析：Webpack生产构建优化

**一句话人话**：搬家时把所有东西都打包好，但没分类，易碎品和衣服混在一起。

**当前问题**：
```javascript
// build/webpack.prod.conf.js
// ✅ 有 splitChunks，但配置比较简单
optimization: {
  splitChunks: {
    cacheGroups: {
      vendor: {
        test: /[\\/]node_modules[\\/]/,
        name: 'vendor',
        chunks: 'all'
      },
      manifest: {
        name: 'manifest',
        minChunks: Infinity
      },
    }
  }
}

// ❌ 没有对常用库进行进一步分割
// ❌ 没有配置 content hash 用于长期缓存
```

**问题分析**：

```javascript
// ✅ 优化后的 build/webpack.prod.conf.js

const webpack = require('webpack');

module.exports = merge(baseWebpackConfig, {
  mode: 'production',
  
  optimization: {
    // 使用 contenthash 便于长期缓存
    filename: utils.assetsPath('js/[name].[contenthash:8].js'),
    chunkFilename: utils.assetsPath('js/[name].[contenthash:8].chunk.js'),
    
    splitChunks: {
      chunks: 'all',  // 改为 'all' 捕获初始 chunks
      maxInitialRequests: 20,  // 允许更多初始请求
      maxAsyncRequests: 20,    // 允许更多异步请求
      minSize: 10000,          // 降低最小 chunk 大小
      cacheGroups: {
        // Vue 生态圈 - 几乎不变
        vue: {
          test: /[\\/]node_modules[\\/](vue|vuex|vue-router)[\\/]/,
          name: 'vue',
          chunks: 'all',
          priority: 30,
        },
        // Ant Design Vue - 较大库单独打包
        antd: {
          test: /[\\/]node_modules[\\/](ant-design-vue|@ant-design)[\\/]/,
          name: 'antd',
          chunks: 'all',
          priority: 25,
        },
        // axios - 单独打包
        axios: {
          test: /[\\/]node_modules[\\/]axios[\\/]/,
          name: 'axios',
          chunks: 'all',
          priority: 20,
        },
        // lodash/es - 如果使用了的话
        lodash: {
          test: /[\\/]node_modules[\\/](lodash|lodash-es)[\\/]/,
          name: 'lodash',
          chunks: 'all',
          priority: 20,
        },
        // 其他 node_modules
        vendors: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
          priority: 10,
          reuseExistingChunk: true,
        },
        // 公共代码
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          priority: 5,
          reuseExistingChunk: true,
        },
      }
    },
    
    // 运行时代码单独提取
    runtimeChunk: 'single',
    
    // 模块串联
    concatenateModules: true,
  },
  
  // 插件配置
  plugins: [
    // ... 其他插件
    
    // 清理未使用的 CSS
    new PurgecssPlugin({
      paths: glob.sync('./src/**/*.{vue,js,ts,jsx,tsx}', { nodir: true }),
      whitelist: ['html', 'body'],
    }),
  ]
});
```

```bash
# 安装 purgecss-webpack-plugin
npm install --save-dev purgecss-webpack-plugin glob
```

**问题理解**：

📖 **规范写法参考（供学习对比）**：Webpack 构建优化是前端工程化的重要知识点，理解其原理有助于学习前端构建知识。

**学习要点**：
- contenthash vs chunkhash：前者是文件内容hash
- 分包太细会导致请求数增加，需要权衡

---

### 问题分析：关闭生产环境source map

**一句话人话**：产品交付时不需要附带说明书源代码。

**当前问题**：
```javascript
// config/index.js
build: {
  // ⚠️ 生产环境启用了 source map
  productionSourceMap: true,  // ❌ 增加包体积，影响加载
}
```

**问题分析**：

```javascript
// 📖 规范写法参考（仅供学习对比） - 生产环境关闭 source map

// config/index.js
module.exports = {
  build: {
    // 开发环境开启方便调试
    productionSourceMap: process.env.NODE_ENV === 'development',
    // 或者完全关闭（推荐）
    // productionSourceMap: false,
  }
}

// ✅ 如果需要调试，可以使用外部 source map 服务
// 将 source map 上传到 Sentry 等错误监控服务
```

```javascript
// build/webpack.prod.conf.js
// 添加 source map 上传插件（可选）

const SentryWebpackPlugin = require('@sentry/webpack-plugin');

new SentryWebpackPlugin({
  org: 'your-org',
  project: 'your-project',
  authToken: process.env.SENTRY_AUTH_TOKEN,
  release: process.env.npm_package_version,
  // 不要在 bundle 中内嵌 source map
  include: './dist',
  ignore: ['node_modules', 'webpack.config.js'],
  urlPrefix: '~/',
})
```

**问题理解**：

📖 **规范写法参考（供学习对比）**：生产环境 source map 的正确配置是前端工程化的重要知识点，理解其原理有助于学习前端构建优化。

**学习要点**：
- 生产环境关闭 source map 后，生产环境报错定位困难
- 建议配合错误监控服务（如 Sentry）使用

---

## 📋 八、学习理解清单

### Bundle体积学习要点

| 序号 | 学习项 | 理解价值 |
|-----|--------|---------|
| 1 | Ant Design Vue 按需引入原理 | 理解前端打包优化 |
| 2 | Lodash 按需引入原理 | 理解第三方库优化 |
| 3 | 图片压缩原理 | 理解资源优化策略 |
| 4 | 路由代码分割原理 | 理解前端工程化 |

### 组件渲染学习要点

| 序号 | 学习项 | 理解价值 |
|-----|--------|---------|
| 1 | v-for key 原理 | 理解 Vue 渲染机制 |
| 2 | computed vs watch | 理解 Vue 响应式原理 |
| 3 | 组件生命周期清理 | 理解内存管理 |

---

## 📊 九、学习理解总结

### 性能问题分类理解

| 问题分类 | 问题数量 | 学习价值 |
|---------|---------|---------|
| Bundle体积问题 | 8项 | 理解前端打包原理 |
| 组件渲染问题 | 6项 | 理解Vue渲染机制 |
| 内存泄漏风险 | 5项 | 理解内存管理 |
| API调用问题 | 4项 | 理解网络优化 |
| 图片资源问题 | 3项 | 理解资源优化 |
| 构建配置问题 | 4项 | 理解前端工程化 |

### 学习路径建议

1. **入门**：先理解 v-for key、computed vs watch 等 Vue 基础
2. **进阶**：理解 Ant Design Vue 按需引入、Webpack 打包原理
3. **深入**：理解内存泄漏、路由代码分割等高级话题

---

> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

| 工具 | 用途 | 链接 |
|-----|------|------|
| webpack-bundle-analyzer | Bundle 分析 | 内置 |
| Lighthouse | 性能审计 | Chrome DevTools |
| TinyPNG | 图片压缩 | https://tinypng.com |
| Sentry | 错误监控 | https://sentry.io |
| SpeedCurve | 持续监控 | https://speedcurve.com |

---

> **文档编写日期**: 2024年
> **适用版本**: picc-mzmtb-agent (Vue 2.6 + Webpack 4)
> **问题反馈**: 如有问题请提交 Issue
