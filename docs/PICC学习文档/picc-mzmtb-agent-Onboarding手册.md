# PICC门诊慢特病前端项目 Onboarding 手册

> **项目全称**：门诊慢特病业务管理信息系统-前端  
> **项目代号**：picc-mzmtb-agent  
> **版本**：V1.0  
> **更新日期**：2024年

---

## 📋 目录

1. [环境准备（30分钟）](#第一部分环境准备30分钟)
2. [项目拉取和启动（30分钟）](#第二部分项目拉取和启动30分钟)
3. [代码导航（30分钟）](#第三部分代码导航30分钟)
4. [开发技巧（30分钟）](#第四部分开发技巧30分钟)
5. [避坑指南](#第五部分避坑指南)

---

# 第一部分：环境准备（30分钟）

## 1.1 Node.js 安装

### 🎯 推荐版本
本项目是 **Vue 2.6** 项目，**必须使用 Node.js 14.x 或 16.x**

> ⚠️ **重要提示**：Vue 2 不支持 Node.js 17及以上版本！推荐使用 Node.js 14.21.3 或 16.20.2

### 📥 Windows 用户

1. 访问 [Node.js 官网](https://nodejs.org/)
2. 下载 **LTS 版本**（推荐 14.21.3 或 16.20.2）
3. 安装时一路 Next，注意勾选 **"Add to PATH"**
4. 打开命令行验证：

```bash
node -v
# 应显示: v14.21.3 或 v16.20.2

npm -v
# 应显示: 6.14.17 或 8.x.x
```

### 📥 Mac/Linux 用户

```bash
# 使用 nvm 管理多版本（推荐）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 安装指定版本
nvm install 14
nvm use 14

# 验证
node -v
```

### 🔧 nvm 安装后快速切换

```bash
nvm install 14
nvm use 14
node -v
```

---

## 1.2 npm/yarn 安装

项目同时支持 npm 和 yarn，推荐使用 **npm**（项目原生支持）

### 检查是否已安装

```bash
npm -v
yarn -v
```

### 配置 npm 镜像（国内加速）

```bash
# 设置淘宝镜像
npm config set registry https://registry.npmmirror.com

# 查看配置
npm config get registry
# 应显示: https://registry.npmmirror.com
```

---

## 1.3 VS Code 安装与配置

### 📥 安装 VS Code

访问 [https://code.visualstudio.com/](https://code.visualstudio.com/) 下载安装

### 🔌 必装插件列表

打开 VS Code，按 `Ctrl+Shift+X`（Mac: `Cmd+Shift+X`）打开扩展面板，搜索安装：

| 插件名称 | 功能 | 搜索关键词 |
|---------|------|----------|
| Vetur | Vue 2 语法高亮和提示 | vetur |
| ESLint | 代码规范检查 | eslint |
| Vue VSCode Snippets | Vue 代码片段 | vue-vscode-snippets |
| Prettier | 代码格式化 | prettier |
| Path Intellisense | 路径自动补全 | path-intellisense |
| Auto Close Tag | 自动闭合标签 | auto-close-tag |
| Auto Rename Tag | 自动重命名标签 | auto-rename-tag |

### ⚙️ VS Code 设置

按 `Ctrl+,`（Mac: `Cmd+,`）打开设置，点击右上角打开 `settings.json`：

```json
{
  // 保存时自动格式化
  "editor.formatOnSave": true,
  
  // 默认格式化工具选择 Prettier
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  
  // Tab 大小
  "editor.tabSize": 2,
  
  // 开启 ESLint
  "eslint.enable": true,
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "vue"
  ],
  
  // 忽略 Vue 文件的警告（项目使用 tabs 缩进）
  "vetur.validation.template": false,
  
  // 文件排除
  "files.exclude": {
    "**/.git": true,
    "**/.svn": true,
    "**/.hg": true,
    "**/CVS": true,
    "**/.DS_Store": true,
    "**/node_modules": true
  }
}
```

---

## 1.4 Git 安装

### Windows 用户

1. 访问 [https://git-scm.com/download/win](https://git-scm.com/download/win)
2. 下载安装，一路 Next
3. 安装完成，打开 Git Bash 验证：

```bash
git --version
# 应显示: git version 2.x.x
```

### Mac 用户

```bash
# 如果已安装 Homebrew
brew install git

# 或使用 Xcode Command Line Tools
xcode-select --install
```

### 基础配置

```bash
# 设置用户名和邮箱
git config --global user.name "你的名字"
git config --global user.email "your.email@example.com"

# 查看配置
git config --list
```

---

## ✅ 环境检查清单

```bash
# 执行以下命令，确保全部通过
node -v      # v14.x 或 v16.x
npm -v       # 6.x 或 8.x
git --version # 2.x.x
```

---

# 第二部分：项目拉取和启动（30分钟）

## 2.1 克隆项目

### 📁 克隆命令

```bash
# 进入工作目录
cd ~/workspace

# 克隆项目（请替换为实际仓库地址）
git clone [项目仓库地址] picc-mzmtb-agent

# 进入项目目录
cd picc-mzmtb-agent
```

### 📂 查看项目结构

```bash
ls -la
# 应该看到以下主要文件和目录：
# package.json  README.md  src/  config/  build/  static/
```

---

## 2.2 安装依赖

### 📦 使用 npm 安装

```bash
npm install
```

> ⚠️ **注意**：如果安装失败，尝试清理缓存后重试：
> ```bash
> npm cache clean --force
> rm -rf node_modules
> npm install
> ```

### ⏱️ 等待时间
- 首次安装约需 **5-10分钟**（取决于网络）
- 安装完成会看到 `added xxx packages` 提示

---

## 2.3 本地开发启动

### 🚀 启动开发服务器

```bash
npm run s_dev
```

### 🌐 访问项目

启动后会自动打开浏览器，访问：

```
http://localhost:80
```

> 💡 如果端口 80 被占用，会自动切换到其他端口，注意看终端输出的实际地址

---

## 2.4 多环境启动说明

项目支持多个环境，通过不同命令启动：

| 命令 | 环境 | 用途 |
|------|------|------|
| `npm run s_dev` | 开发环境 dev | 本地开发调试 |
| `npm run s_test` | 测试环境 test | 连接测试服务器 |
| `npm run s_uat` | UAT环境 uat | 用户验收测试 |
| `npm run s_production` | 生产环境 | 模拟生产环境 |

### 🔧 环境配置位置

```
config/
├── dev.env.js      # 开发环境配置
├── test.env.js     # 测试环境配置
├── uat.env.js      # UAT环境配置
├── prod.env.js     # 生产环境配置
├── index.js        # 主配置文件
└── proxyConfig.js  # 代理配置
```

### 📡 后端服务地址配置

在 `config/dev.env.js` 中配置：

```javascript
module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  EVN_CONFIG: '"dev"',
  
  // 慢病业务逻辑服务 - 测试环境
  domainName: '"http://10.57.17.188:9001/"',
  
  // 慢病鉴权服务
  domainNameCenter: '"http://10.57.17.188:9093/"',
  
  // 慢病权限系统服务
  domainNamePower: '"http://10.57.17.188:9092/"',
})
```

---

## 2.5 常见启动报错和解决方案

### ❌ 报错1: "node-gyp" 安装失败

**错误信息**：
```
gyp ERR! stack Error: not found: make
```

**解决方案**：
```bash
# Windows: 安装 Visual Studio Build Tools
# Mac: 安装 Xcode Command Line Tools
xcode-select --install
```

---

### ❌ 报错2: "sass-loader" 编译失败

**错误信息**：
```
Module build failed: Error: Node Sass does not yet support your current node version
```

**解决方案**：
```bash
# 卸载后重新安装
npm uninstall node-sass
npm install node-sass@7.0.0
```

---

### ❌ 报错3: 端口被占用

**错误信息**：
```
Error: listen EADDRINUSE :::80
```

**解决方案**：
```bash
# 方法1: 查找占用端口的进程并结束
# Windows
netstat -ano | findstr :80
taskkill /PID <进程ID> /F

# Mac/Linux
lsof -i :80
kill -9 <进程ID>

# 方法2: 修改端口（在 config/index.js 中修改 port）
```

---

### ❌ 报错4: Webpack 内存溢出

**错误信息**：
```
FATAL ERROR: CALL_AND_RETRY_LAST Allocation failed - JavaScript heap out of memory
```

**解决方案**：
```bash
# Windows: 设置环境变量后启动
set NODE_OPTIONS=--max_old_space_size=4096
npm run s_dev

# Mac/Linux: 
export NODE_OPTIONS=--max_old_space_size=4096
npm run s_dev
```

---

### ❌ 报错5: npm install 一直卡住

**解决方案**：
```bash
# 1. 清理缓存
npm cache clean --force

# 2. 删除 node_modules
rm -rf node_modules

# 3. 使用淘宝镜像重新安装
npm install --registry=https://registry.npmmirror.com
```

---

# 第三部分：代码导航（30分钟）

## 3.1 项目目录结构速览

```
picc-mzmtb-agent/
├── src/                          # 源代码目录
│   ├── api/                      # API 接口定义（74个文件）
│   │   ├── axios.js              # Axios 封装核心
│   │   ├── axiosCenter.js        # 通用中心接口
│   │   ├── axiosPower.js         # 权限系统接口
│   │   ├── apiLoginMb.js         # 登录相关接口
│   │   └── api*.js               # 各业务模块接口
│   │
│   ├── components/               # 通用组件
│   │   ├── index.js              # 组件全局注册
│   │   ├── loginMb/              # 登录组件
│   │   ├── comAlert/             # 通用弹窗
│   │   ├── comSelect/            # 通用下拉
│   │   ├── myTable/              # 通用表格
│   │   └── ...
│   │
│   ├── pages/                    # 页面组件（652个Vue文件）
│   │   ├── Home.vue              # 首页框架
│   │   ├── ChronicDis/           # 宝鸡慢病管理
│   │   ├── DZChronicDis/          # 达州慢病管理
│   │   ├── DIZChronicDis/         # 定制模块
│   │   ├── JCChronicDis/          # 吉林长春
│   │   ├── JiJChronicDis/         # 吉林吉林
│   │   ├── JZChronicDis/          # 锦州慢病管理
│   │   ├── MZLChronicDis/         # 某地市慢病管理
│   │   ├── SLChronicDis/         # 某地市慢病管理
│   │   ├── XYaChronicDis/         # 西安某区
│   │   ├── YAChronicDis/          # 延安慢病管理
│   │   ├── YaLChronicDis/         # 榆林慢病管理
│   │   ├── YLChronicDis/         # 营口慢病管理
│   │   ├── ZJKChronicDis/         # 张家口慢病管理
│   │   ├── Declare/              # 申报管理
│   │   ├── Payment/              # 支付管理
│   │   ├── QuickClaim/           # 快速理赔
│   │   ├── SystemView/           # 系统管理
│   │   └── NewChronicDis/        # 新慢病模块
│   │
│   ├── router/                   # 路由配置
│   │   ├── index.js              # 路由主入口
│   │   └── childrenRoutes.js     # 子路由配置（21个地市模块路由）
│   │
│   ├── store/                    # Vuex 状态管理
│   │   ├── index.js              # store 主入口
│   │   └── modules/             # 模块化 store
│   │       ├── menu.js           # 菜单状态
│   │       └── activeRouterMatch.js  # 路由匹配
│   │
│   ├── utils/                    # 工具函数
│   │   ├── util.js               # 通用工具
│   │   ├── fileDownload.js       # 文件下载
│   │   ├── sm4.js                # SM4 加密
│   │   └── tableMixins.js        # 表格混入
│   │
│   ├── mtbcomponents/            # 慢病组件库（第一版）
│   ├── mtbnewcomponents/         # 慢病组件库（新版本）
│   │   ├── comSelect/            # 通用选择组件
│   │   ├── myTable/              # 表格组件
│   │   ├── searchCard/           # 搜索卡片
│   │   ├── declareModal/         # 申报弹窗
│   │   └── ...
│   │
│   ├── mtbslcomponents/         # 某地市专用组件
│   │
│   ├── mock/                     # Mock 数据
│   │
│   ├── assets/                   # 静态资源
│   │   ├── css/                  # 样式文件
│   │   └── images/               # 图片资源
│   │
│   ├── main.js                   # 项目入口
│   └── App.vue                   # 根组件
│
├── config/                       # 配置文件
│   ├── index.js                  # 主配置
│   ├── dev.env.js                # 开发环境
│   ├── test.env.js               # 测试环境
│   └── proxyConfig.js            # 代理配置
│
├── build/                        # Webpack 构建配置
│   ├── webpack.base.conf.js      # 基础配置
│   ├── webpack.dev.conf.js       # 开发配置
│   └── webpack.prod.conf.js     # 生产配置
│
├── static/                       # 静态资源（不经过构建）
│
├── package.json                  # 项目配置
├── .eslintrc.js                  # ESLint 配置
├── jsconfig.json                 # JS 配置（路径别名）
└── README.md                     # 项目说明
```

---

## 3.2 快速定位指南

### 🔍 "我想看登录页面"

**路径**：`src/components/loginMb/index.vue`

**说明**：通用中心登录页面，包含用户名密码登录、手机验证码登录等功能

```javascript
// 登录接口位置
src/api/apiLoginMb.js
src/api/apiLogin.js
```

---

### 🔍 "我想看申报页面"

**路径**：`src/pages/Declare/`

```javascript
// 申报相关组件
src/pages/Declare/diseaseDeclare.vue      // 慢病申报主页面
src/pages/Declare/diseaseDeclareInfo.vue  // 申报详情
src/pages/Declare/diseaseDeclarePrint.vue // 申报打印
src/pages/Declare/declarationModification.vue // 申报修改

// 申报相关 API
src/api/apiDeclare.js
src/api/apiDiseaseDeclare.js
```

---

### 🔍 "我想看某个地市的页面"

**21个地市模块目录**：

| 地市 | 目录路径 |
|------|----------|
| 宝鸡 | `src/pages/ChronicDis/` |
| 达州 | `src/pages/DZChronicDis/` |
| 达州(定制) | `src/pages/DIZChronicDis/` |
| 吉林长春 | `src/pages/JCChronicDis/` |
| 吉林吉林 | `src/pages/JiJChronicDis/` |
| 锦州 | `src/pages/JZChronicDis/` |
| 梅州/某地 | `src/pages/MZLChronicDis/` |
| 某地市 | `src/pages/NewChronicDis/` |
| 陕西某地 | `src/pages/SLChronicDis/` |
| 西安某区 | `src/pages/XYaChronicDis/` |
| 延安 | `src/pages/YAChronicDis/` |
| 榆林 | `src/pages/YaLChronicDis/` |
| 营口 | `src/pages/YLChronicDis/` |
| 张家口 | `src/pages/ZJKChronicDis/` |

> 💡 每个地市目录结构类似：`diseaseDeclare.vue`（申报）、`auditManagement.vue`（审核）等

---

### 🔍 "我想看 API 调用"

**API 文件目录**：`src/api/`

| API 文件 | 用途 |
|---------|------|
| `axios.js` | Axios 核心封装（请求拦截、响应拦截） |
| `axiosCenter.js` | 通用中心接口封装 |
| `axiosPower.js` | 权限系统接口封装 |
| `apiLoginMb.js` | 登录相关接口 |
| `apiDeclare.js` | 申报管理接口 |
| `apiAuditManagement.js` | 审核管理接口 |
| `apiUserManage.js` | 用户管理接口 |

---

### 🔍 "我想看路由配置"

**路由文件**：
```
src/router/
├── index.js           # 路由主入口（定义静态路由）
└── childrenRoutes.js  # 动态子路由（21个地市模块路由，共65KB）
```

**关键路由**：
```javascript
// 登录页路由
{ path: "/loginMb", name: "loginMb" }

// 首页路由（包含所有子路由）
{ path: "/home", name: "home", children: [...childrenRoutes] }
```

---

### 🔍 "我想看全局状态（Vuex）"

**Store 文件**：`src/store/`

```javascript
// 主入口
src/store/index.js

// 模块
src/store/modules/menu.js              // 菜单状态
src/store/modules/activeRouterMatch.js  // 路由匹配状态
```

---

## 3.3 关键文件速查表

| 功能 | 文件路径 |
|------|----------|
| 项目入口 | `src/main.js` |
| 根组件 | `src/App.vue` |
| 首页框架 | `src/pages/Home.vue` |
| 登录页面 | `src/components/loginMb/index.vue` |
| 路由入口 | `src/router/index.js` |
| 路由子配置 | `src/router/childrenRoutes.js` |
| Axios封装 | `src/api/axios.js` |
| Vuex入口 | `src/store/index.js` |
| 工具函数 | `src/utils/util.js` |
| 环境配置 | `config/dev.env.js` |
| 代理配置 | `config/proxyConfig.js` |
| ESLint配置 | `.eslintrc.js` |
| Webpack配置 | `build/webpack.base.conf.js` |

---

# 第四部分：开发技巧（30分钟）

## 4.1 新增一个页面

### 步骤1: 创建页面组件

在 `src/pages/ChronicDis/`（或对应地市目录）下新建文件：

```vue
<!-- src/pages/ChronicDis/myNewPage.vue -->
<template>
  <div class="my-new-page">
    <div class="search-card">
      <!-- 搜索区域 -->
    </div>
    <div class="table-content">
      <!-- 表格区域 -->
    </div>
  </div>
</template>

<script>
export default {
  name: 'MyNewPage',
  data() {
    return {
      // 数据
    }
  },
  methods: {
    // 方法
  }
}
</script>

<style lang="less" scoped>
.my-new-page {
  padding: 20px;
}
</style>
```

### 步骤2: 注册路由

在 `src/router/childrenRoutes.js` 中添加路由：

```javascript
{
  path: `/myNewPage`,
  name: "myNewPage",
  meta: {
    ptitle: "慢病管理",      // 父级菜单名称
    title: "新页面",         // 菜单显示名称
    pathName: "/myNewPage",  // 路由路径
  },
  component: () => import("@/pages/ChronicDis/myNewPage"),
}
```

### 步骤3: 添加菜单权限（可选）

在菜单配置中添加对应的菜单项，关联权限编码

---

## 4.2 新增一个 API 接口

### 步骤1: 创建 API 文件

```javascript
// src/api/apiMyModule.js
import axios from "./axios";

export default {
  // 查询列表
  queryList: (params) => {
    return axios.request({
      url: '/myModule/queryList',
      method: 'POST',
      data: params
    })
  },
  
  // 获取详情
  getDetail: (id) => {
    return axios.request({
      url: `/myModule/detail/${id}`,
      method: 'GET'
    })
  },
  
  // 保存数据
  save: (params) => {
    return axios.request({
      url: '/myModule/save',
      method: 'POST',
      data: params
    })
  },
  
  // 删除数据
  delete: (id) => {
    return axios.request({
      url: `/myModule/delete/${id}`,
      method: 'DELETE'
    })
  }
}
```

### 步骤2: 在组件中使用

```javascript
import apiMyModule from '@/api/apiMyModule'

export default {
  methods: {
    async loadData() {
      try {
        const res = await apiMyModule.queryList({ page: 1, size: 10 })
        if (res.status === '0') {
          this.tableData = res.data.list
        }
      } catch (error) {
        console.error('加载数据失败', error)
      }
    }
  }
}
```

### 步骤3: 统一导出（可选）

在 `src/api/apiList.js` 中导出，方便全局使用

---

## 4.3 新增一个地市模块

### 步骤1: 创建目录结构

```bash
# 在 src/pages/ 下创建新地市目录
mkdir -p src/pages/XZChronicDis/components
mkdir -p src/pages/XZChronicDis/config
mkdir -p src/pages/XZChronicDis/css
```

### 步骤2: 复制基础模板

从已有地市模块（如 `ChronicDis/`）复制 `diseaseDeclare.vue` 作为模板

### 步骤3: 添加路由

在 `src/router/childrenRoutes.js` 中添加：

```javascript
{
  path: `/xzDiseaseDeclare`,
  name: "xzDiseaseDeclare",
  meta: {
    ptitle: "XZ慢病管理",
    title: "慢病申报",
    pathName: "/xzDiseaseDeclare",
  },
  component: () => import("@/pages/XZChronicDis/diseaseDeclare"),
},
```

### 步骤4: 配置代理（开发环境）

在 `config/dev.env.js` 中确认后端地址

### 步骤5: 创建 API 文件

在 `src/api/` 下创建 `apiXZChronicDis.js`

---

## 4.4 Vue DevTools 调试

### 安装

Chrome 扩展商店搜索 "Vue Devtools" 安装

### 使用技巧

1. **查看组件状态**：打开 DevTools → Vue 面板 → 选择组件
2. **查看 Vuex 状态**：Vue 面板 → Vuex 标签
3. **追踪 mutations**：在 Vuex 面板开启 "Record mutations"
4. **查看路由**：Vue 面板 → Router 标签

### 常见操作

```javascript
// 在控制台手动触发 Vuex mutation
$store.commit('menu/UPDATE_MENU', newMenuData)

// 查看当前路由
$store.state.route.path

// 查看用户信息
$store.getters.getUserInfo
```

---

## 4.5 网络请求调试

### Chrome DevTools Network 面板

1. **筛选请求**：使用 Filter 输入 `domainName` 中的路径关键词
2. **查看请求详情**：点击请求 → Headers/Payload/Response
3. **复制请求**：右键请求 → Copy → Copy as cURL

### 请求参数格式

```javascript
// POST 请求（表单格式）
Content-Type: application/x-www-form-urlencoded
data: { key: 'value' }

// POST 请求（JSON格式）
Content-Type: application/json
data: { key: 'value' }
```

### 响应格式

```javascript
// 成功响应
{
  "status": "0",
  "message": "success",
  "data": { ... }
}

// 失败响应
{
  "status": "1",
  "message": "错误信息",
  "data": null
}
```

---

## 4.6 组件调试技巧

### 打印组件实例

```javascript
// 在组件方法中
console.log(this.$refs.myTable)
console.log(this.$attrs)
console.log(this.$listeners)
```

### 查看组件 props

```javascript
// 父组件传递的 props
console.log(this.$props)

// 所有属性（包括 props、attrs）
console.log(this.$options.props)
```

### 触发组件方法

```javascript
// 通过 ref 调用子组件方法
this.$refs.myTable.refresh()
this.$refs.myForm.validate()
```

---

# 第五部分：避坑指南

## 5.1 Vue 2 和 Vue 3 的区别 ⚠️

**本项目是 Vue 2.6 项目，严禁使用 Vue 3 语法！**

### ❌ 禁止使用的 Vue 3 特性

| Vue 3 特性 | Vue 2 对应写法 |
|-----------|---------------|
| `<script setup>` | `export default {}` |
| `reactive()` | `data() { return {} }` |
| `ref()` | `data() { return { value: '' } }` |
| `computed()` (函数式) | `computed: { ... }` |
| `watch()` (新语法) | `watch: { ... }` |
| `defineProps()` | `props: { ... }` |
| `v-model` 新语法 | `v-model` / `:value` + `@input` |

### ✅ 正确写法示例

```javascript
// ❌ Vue 3 错误写法
<script setup>
import { ref, computed } from 'vue'
const count = ref(0)
const doubled = computed(() => count.value * 2)
</script>

// ✅ Vue 2 正确写法
<script>
export default {
  name: 'MyComponent',
  data() {
    return {
      count: 0
    }
  },
  computed: {
    doubled() {
      return this.count * 2
    }
  }
}
</script>
```

### Vue 2 生命周期

```
beforeCreate → created → beforeMount → mounted → 
beforeUpdate → updated → beforeDestroy → destroyed
```

---

## 5.2 Axios 拦截器注意点

### 请求拦截器

在 `src/api/axios.js` 中配置：

```javascript
// 已在 axios.js 中配置
instance.interceptors.request.use(config => {
  // ✅ Token 已在拦截器中自动添加
  // ✅ userId 已在拦截器中自动添加
  
  // ⚠️ 不要在这里手动设置 Content-Type
  // 因为部分接口使用 form-data 格式
  
  return config
})
```

### 响应拦截器

```javascript
instance.interceptors.response.use(
  res => {
    // ✅ 状态码 '0' 表示成功
    // ⚠️ 不要使用 res.data.status === 200
    if (res.data.status === '0') {
      return res.data
    }
    // 其他状态码处理...
  },
  error => {
    // ❌ 不要在这里统一弹窗提示
    // 让具体业务组件处理错误提示
    return Promise.reject(error)
  }
)
```

### ⚠️ 常见坑点

1. **请求体加密**：部分接口需要 AES/SM4 加密，封装在 `axios.js` 中
2. **FormData 格式**：文件上传等接口使用 `FormData`，不要设置 `Content-Type`
3. **Token 失效**：Token 过期会自动跳转登录页（已封装）

---

## 5.3 地市模块路由注意点

### 路由参数传递

```javascript
// ❌ 错误：通过 query 传递
this.$router.push('/page?id=1&name=test')

// ✅ 正确：通过 params 传递
this.$router.push({ 
  path: '/page', 
  params: { id: '1', name: 'test' } 
})

// ✅ 或使用 name
this.$router.push({ 
  name: 'pageName', 
  params: { id: '1' } 
})
```

### 获取路由参数

```javascript
// 获取 params 参数
this.$route.params.id

// 获取 query 参数
this.$route.query.id
```

### ⚠️ 地市标识 flag

部分地市通过 URL 参数 `flag` 区分：

```
http://localhost:80/#/home?token=xxx&flag=0
```

在组件中获取：
```javascript
let flag = this.$route.query.flag || 0
```

---

## 5.4 Webpack 构建内存溢出

### 原因

项目较大（652个Vue文件），构建时内存不足

### 解决方案

#### 方案1: 增加 Node.js 内存

```bash
# Mac/Linux
export NODE_OPTIONS=--max_old_space_size=4096
npm run build

# Windows PowerShell
$env:NODE_OPTIONS="--max_old_space_size=4096"
npm run build

# Windows CMD
set NODE_OPTIONS=--max_old_space_size=4096
npm run build
```

#### 方案2: 修改 package.json

```json
{
  "scripts": {
    "build": "node --max_old_space_size=4096 build/build.js"
  }
}
```

#### 方案3: 分模块构建

如果只需要某个地市模块，可以在 `webpack.prod.conf.js` 中配置 `entry` 为指定目录

---

## 5.5 跨域问题

### 开发环境

通过 `config/proxyConfig.js` 配置代理解决：

```javascript
module.exports = {
  proxy: {
    '/apis': {
      target: 'http://10.57.17.188:9001/',
      changeOrigin: true,
      pathRewrite: { '^/apis': '' }
    }
  }
}
```

### 生产环境

通过 Nginx 反向代理解决：

```nginx
# nginx-dev.conf 参考配置
server {
    listen 80;
    server_name localhost;
    
    location / {
        root /path/to/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    location /apis {
        proxy_pass http://10.57.17.188:9001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api2 {
        proxy_pass http://10.57.17.188:9093/;
        proxy_set_header Host $host;
    }
    
    location /api3 {
        proxy_pass http://10.57.17.188:9092/;
        proxy_set_header Host $host;
    }
}
```

---

## 5.6 常用命令速查

```bash
# 安装依赖
npm install

# 开发环境启动
npm run s_dev

# 测试环境启动
npm run s_test

# 构建（需先设置 NODE_OPTIONS）
npm run build

# 指定环境构建
npm run build:dev    # 开发环境
npm run build:test    # 测试环境
npm run build:uat     # UAT环境
npm run build:prod    # 生产环境

# 代码检查
npm run lint

# 问题原理格式
npm run lint -- --fix
```

---

## 5.7 后端服务端口说明

| 服务 | 端口 | 用途 |
|------|------|------|
| 慢病业务服务 | 9001 | 主要业务接口 |
| 业务服务 | 9091 | 备用业务接口 |
| 权限服务 | 9092 | 权限校验接口 |
| 通用中心 | 9093 | 登录鉴权接口 |

---

## 📞 常见问题求助

1. **查看 README.md**：项目根目录有基本说明
2. **查看历史 commit**：通过 `git log` 查看开发记录
3. **请教同事**：项目有 21 个地市模块，不同模块找对应的负责人
4. **查看接口文档**：联系后端获取 Swagger 文档

---

**手册版本**：V1.0  
**最后更新**：2024年  
**维护者**：前端团队
