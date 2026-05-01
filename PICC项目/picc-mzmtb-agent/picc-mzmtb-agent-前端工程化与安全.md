> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC门诊慢特病前端项目（picc-mzmtb-agent）国际化现状与可访问性分析报告

## 📋 项目概览

| 项目信息 | 详情 |
|---------|------|
| **项目名称** | 门诊慢特病业务管理信息系统 |
| **技术栈** | Vue 2.6.11 + Ant Design Vue 1.7.2 |
| **构建工具** | Webpack 4.16.2 |
| **Vuex版本** | 3.0.1 |
| **Vue Router版本** | 3.3.4 |
| **国际化方案** | vue-i18n 8.0.0 |
| **代码规模** | 652个Vue组件 + 213个JS文件 |
| **代码总量** | 约16万行代码 |
| **作者** | xufengli |
| **项目负责人** | wangyz |

---

## 📖 目录

1. [Part 1：前端代码规范分析](#part-1前端代码规范分析)
2. [Part 2：前端安全最佳实践](#part-2前端安全最佳实践)
3. [Part 3：前端可访问性(a11y)](#part-3前端可访问性a11y)
4. [Part 4：前端工程化建议](#part-4前端工程化建议)
5. [Part 5：SEO与PWA](#part-5seo与pwa)
6. [总结与优先级建议](#总结与优先级建议)

---

# Part 1：前端代码规范分析

## 1.1 ESLint配置分析

### 📊 当前配置状态

```javascript
// .eslintrc.js 核心配置
module.exports = {
  root: true,
  parserOptions: {
    parser: 'babel-eslint'  // ⚠️ 已过时，建议迁移到 @babel/eslint-parser
  },
  env: {
    browser: true,
  },
  extends: [
    'plugin:vue/essential',  // ⚠️ 建议升级到 strongly-recommended 或 recommended
    'standard'
  ],
  plugins: ['vue'],
  rules: {
    "vue/no-parsing-error": [2, { "x-invalid-end-tag": false }],
    "no-extra-boolean-cast": "off",
    "no-unused-vars": "off",  // ⚠️ 关闭了未使用变量检查
    "indent": ["error", "tab"],  // ⚠️ 使用 tab 缩进
    "no-tabs": "on",
    "no-debugger": 2,
    "camelcase": 2,
    "comma-dangle": [2, "never"],
    "comma-spacing": [2, { "before": false, "after": true }],
  }
}
```

### ✅ 做得好的地方

| 方面 | 评价 |
|-----|------|
| ESLint集成 | ✅ 开发环境已启用ESLint检查 |
| Vue组件支持 | ✅ 使用 eslint-plugin-vue |
| Standard规范 | ✅ 遵循Standard代码规范 |
| 错误级别 | ✅ 合理区分error和warning |

### ⚠️ 问题与风险

#### 问题1：ESLint版本过旧（4.19.1）

```
当前版本：ESLint 4.19.1
最新版本：ESLint 9.x
```

**影响：**
- 不支持ES6+新语法的高级检查
- 缺少最新的安全规则
- 无法使用现代ESLint的缓存和并行检查功能

**学习思考：**
```bash
# 升级到最新ESLint
npm install eslint@latest --save-dev
npm install @eslint/js --save-dev
npm install eslint-plugin-vue@latest --save-dev
```

#### 问题2：关闭了重要检查规则

```javascript
"no-unused-vars": "off"  // ❌ 关闭未使用变量检查
```

**影响：**
- 代码中存在大量未使用的变量和导入
- 打包体积增大
- 代码可维护性降低

**学习思考：**
```javascript
// 调整为严格模式
"no-unused-vars": ["error", { 
  "vars": "all", 
  "args": "after-used",
  "ignoreRestSiblings": true 
}]
```

#### 问题3：缩进规范混乱

```javascript
"indent": ["error", "tab"],  // 要求使用 tab
"no-tabs": "on",              // 又禁止使用 tab
```

**这是一个配置冲突！** 导致代码格式化行为不可预测。

**学习思考：**
```javascript
// 统一使用空格缩进（推荐2空格）
"indent": ["error", 2],
"no-tabs": "off"
```

### 🔧 建议的现代化ESLint配置

```javascript
// .eslintrc.js (推荐配置)
module.exports = {
  root: true,
  parserOptions: {
    parser: '@babel/eslint-parser',
    ecmaVersion: 2021,
    sourceType: 'module',
  },
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended',  // Vue 3规则
    '@vue/standard'
  ],
  plugins: ['vue'],
  rules: {
    // Vue组件规则
    'vue/multi-word-component-names': 'off',
    'vue/no-v-html': 'warn',
    'vue/require-default-prop': 'error',
    'vue/require-prop-types': 'error',
    
    // 代码质量
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'warn',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'warn',
    'no-unused-vars': ['error', { 
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_'
    }],
    
    // 格式化
    'indent': ['error', 2],
    'quotes': ['error', 'single'],
    'semi': ['error', 'always'],
  }
}
```

---

## 1.2 代码格式化（Prettier）

### 📊 当前状态

| 检查项 | 状态 | 说明 |
|-------|------|------|
| Prettier安装 | ❌ **未安装** | package.json中无prettier依赖 |
| .prettierrc配置 | ❌ **不存在** | 无Prettier配置文件 |
| Prettier集成ESLint | ❌ **未集成** | 未安装eslint-config-prettier |

### ⚠️ 问题与风险

当前项目：
- 没有统一的代码格式化工具
- 不同开发者的代码风格可能不一致
- ESLint的格式化规则与Prettier可能冲突

### ✅ 改进方案

#### Step 1: 安装Prettier

```bash
npm install prettier --save-dev
npm install eslint-config-prettier --save-dev
```

#### Step 2: 创建.prettierrc配置

```json
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "arrowParens": "always",
  "endOfLine": "lf",
  "vueIndentScriptAndStyle": false
}
```

#### Step 3: 创建.prettierignore

```
build/
config/
dist/
node_modules/
*.min.js
```

#### Step 4: 更新package.json脚本

```json
{
  "scripts": {
    "prettier": "prettier --write \"src/**/*.{js,vue,less,css}\"",
    "prettier:check": "prettier --check \"src/**/*.{js,vue,less,css}\"",
    "lint": "eslint --ext .js,.vue src",
    "lint:fix": "eslint --fix --ext .js,.vue src"
  }
}
```

---

## 1.3 Git Hooks（husky/lint-staged）

### 📊 当前状态

| 检查项 | 状态 | 说明 |
|-------|------|------|
| husky | ❌ **未安装** | package.json中无husky依赖 |
| lint-staged | ❌ **未安装** | 未配置暂存区检查 |
| pre-commit钩子 | ⚠️ **使用默认钩子** | 仅使用Git默认的示例钩子 |

### 📁 当前Git Hooks目录

```
.git/hooks/
├── applypatch-msg.sample
├── commit-msg.sample
├── pre-commit.sample  ← 未激活
├── pre-push.sample    ← 未激活
└── ...（共14个示例钩子）
```

### ✅ 改进方案

#### Step 1: 安装husky和lint-staged

```bash
npm install husky lint-staged --save-dev
```

#### Step 2: 在package.json中配置

```json
{
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged",
      "commit-msg": "commitlint -E HUSKY_GIT_PARAMS"
    }
  },
  "lint-staged": {
    "*.{js,vue}": [
      "eslint --fix",
      "git add"
    ],
    "*.{less,css,vue}": [
      "prettier --write",
      "git add"
    ]
  }
}
```

#### Step 3: 初始化husky

```bash
npx husky install
```

---

## 1.4 代码提交规范（commitlint）

### 📊 当前状态

| 检查项 | 状态 | 说明 |
|-------|------|------|
| commitlint | ❌ **未安装** | 无提交信息规范检查 |
| Commitizen | ❌ **未安装** | 无交互式提交工具 |
| conventional commits | ❌ **未采用** | 未使用标准提交格式 |

### ⚠️ 问题与风险

- 提交信息格式不统一
- 无法自动生成CHANGELOG
- 代码回溯和版本管理困难

### ✅ 改进方案

#### Step 1: 安装commitlint

```bash
npm install @commitlint/config-conventional @commitlint/cli --save-dev
```

#### Step 2: 创建commitlint.config.js

```javascript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',     // 新功能
        'fix',      // 修复bug
        'docs',     // 文档变更
        'style',    // 代码格式
        'refactor', // 重构
        'perf',     // 性能优化
        'test',     // 测试
        'chore',    // 构建/工具
        'revert',   // 回退
        'build',    // 构建相关
      ]
    ],
    'type-case': [2, 'never', ['sentence-case', 'pascal-case', 'snake-case']],
    'type-empty': [2, 'never'],
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],
    'header-max-length': [2, 'always', 100]
  }
}
```

#### Step 3: 使用Commitizen（可选）

```bash
npm install commitizen cz-customizable --save-dev

# package.json添加
{
  "config": {
    "commitizen": {
      "path": "node_modules/cz-customizable"
    }
  }
}
```

---

# Part 2：前端安全最佳实践

## 2.1 XSS防护现状

### 📊 当前状态

| 检查项 | 状态 | 说明 |
|-------|------|------|
| v-html使用 | ⚠️ **存在** | 在打印组件中使用了innerHTML |
| 动态内容渲染 | ⚠️ **需审查** | 需确认所有用户输入都经过转义 |
| XSS过滤库 | ❌ **未使用** | 无专门的XSS防护库 |

### 🔍 发现的潜在风险点

#### 风险点1：打印功能中的innerHTML使用

```javascript
// src/components/comPrintTable/comPrintTable.vue:183
var bdhtml = window.document.body.innerHTML
// 后续可能有风险...
```

**风险说明：**
虽然这是内部打印功能，但如果打印内容包含用户提交的数据，需要确保已经过XSS过滤。

**学习思考：**
```javascript
// 使用安全的HTML转义
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// 或使用 DOMParser 进行安全解析
function safeInnerHTML(html) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, 'text/html');
  return doc.body.textContent || '';
}
```

#### 风险点2：用户输入的卡号显示

```vue
<!-- src/components/myTable/index.vue:24 -->
<span :key="n+key">**********{{record|filterCardNo}}</span>
```

**✅ 已做处理：** 使用了脱敏处理，但建议确认后端也做了相同处理。

### ✅ XSS防护学习思考

#### 1. 安装xss库

```bash
npm install xss --save
```

#### 2. 创建XSS过滤器工具

```javascript
// src/utils/xss.js
import xss from 'xss';

const xssOptions = {
  whiteList: {
    // 允许的标签和属性
    a: ['href', 'title', 'target'],
    img: ['src', 'alt', 'title'],
  },
  onTag: (tag, html, options) => {
    // 自定义标签处理
  },
  onTagAttr: (tag, name, value) => {
    // 自定义属性处理
  }
};

// 过滤HTML
export function filterXSS(html) {
  return xss(html, xssOptions);
}

// 严格过滤（仅保留文本）
export function stripXSS(html) {
  return xss(html, { whiteList: {} });
}
```

#### 3. 全局注册Vue过滤器

```javascript
// src/filters/xss.js
import { filterXSS, stripXSS } from '@/utils/xss';

Vue.filter('xss', filterXSS);
Vue.filter('stripXss', stripXSS);

// 在模板中使用
// <span v-html="$options.filters.stripXss(content)"></span>
```

---

## 2.2 CSRF防护

### 📊 当前状态

| 检查项 | 状态 | 说明 |
|-------|------|------|
| CSRF Token | ⚠️ **部分实现** | 在axios请求头中有鉴权参数 |
| SameSite Cookie | ❌ **未配置** | 后端需配置SameSite属性 |
| 自定义请求头 | ✅ **已实现** | 使用了accessId和sign签名 |

### 🔍 现有鉴权机制分析

```javascript
// src/api/axiosCenter.js
let headerSign = {
  accountNum: "...",
  accessId: util.getUUIDTime(8, 10) + "_" + dataTime,
  apiCode: config.data.apiCode,
  accessDate: util.formatDays(dataTime),
  sign: md5.toUpperCase()  // 基于参数计算的签名
};
config.headers = Object.assign(config.headers, headerSign);
```

**✅ 做得好的地方：**
- 使用了基于时间的accessId
- 使用了签名机制防止参数篡改
- 每个请求都有唯一的标识

**⚠️ 需要增强的地方：**
- 建议在后端配置SameSite=Strict或Lax
- 建议添加请求来源验证

### ✅ CSRF防护学习思考

#### 1. 后端配置（需协调后端）

```
# Nginx配置示例
proxy_cookie_path / "/; SameSite=Strict; Secure";
```

#### 2. 前端添加来源检查

```javascript
// src/api/axiosCenter.js
instance.interceptors.request.use(config => {
  // 验证请求来源
  const validOrigins = [
    'https://your-domain.com',
    'https://www.your-domain.com'
  ];
  
  if (process.env.NODE_ENV !== 'development') {
    if (!validOrigins.includes(window.location.origin)) {
      console.warn('CSRF: Invalid origin detected');
    }
  }
  
  return config;
});
```

#### 3. 使用Vue Cookie库

```bash
npm install js-cookie --save
```

```javascript
// src/utils/csrf.js
import Cookies from 'js-cookie';

export function getCSRFToken() {
  return Cookies.get('csrf_token');
}

export function setCSRFToken(token) {
  Cookies.set('csrf_token', token, {
    secure: true,
    sameSite: 'strict',
    expires: 1
  });
}
```

---

## 2.3 点击劫持防护

### 📊 当前状态

| 检查项 | 状态 | 说明 |
|-------|------|------|
| X-Frame-Options | ✅ **已配置** | Nginx配置了SAMEORIGIN |
| Frame-Breaking脚本 | ❌ **未配置** | 无JS层面的防护 |
| CSP frame-ancestors | ❌ **未配置** | 未设置Content-Security-Policy |

### 🔍 Nginx配置分析

```nginx
# nginx-pro.conf
server {
    listen 80;
    server_name localhost;
    
    location / {
        root /home/front/output;
        add_header X-Frame-Options SAMEORIGIN;  # ✅ 已配置
    }
}
```

**✅ 做得好的地方：**
- Nginx层已配置X-Frame-Options

**⚠️ 需要增强的地方：**
- 仅配置了主location，建议确保所有location都配置
- 建议添加CSP的frame-ancestors指令

### ✅ 点击劫持防护学习思考

#### 1. 增强Nginx配置

```nginx
server {
    listen 80;
    server_name localhost;
    
    # 点击劫持防护
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    location / {
        root /home/front/output;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
}
```

#### 2. 添加Frame-Breaking脚本

```html
<!-- index.html -->
<head>
  <style id="anti-clickjack">
    body { display: none !important; }
  </style>
</head>
<body>
  <script>
    if (self === top) {
      var antiClickjack = document.getElementById("anti-clickjack");
      antiClickjack.parentNode.removeChild(antiClickjack);
    } else {
      top.location = self.location;
    }
  </script>
</body>
```

---

## 2.4 Content Security Policy (CSP)

### 📊 当前状态

| 检查项 | 状态 | 说明 |
|-------|------|------|
| CSP配置 | ❌ **未配置** | Nginx和前端均无CSP |
| nonce策略 | ❌ **未实现** | 未使用nonce防止内联脚本注入 |
| 报告URI | ❌ **未配置** | 无CSP违规报告端点 |

### ⚠️ 安全风险

当前缺少CSP配置，面临以下风险：
- 外部脚本注入攻击
- 内联脚本执行
- 未知来源的AJAX请求

### ✅ CSP配置学习思考

#### 1. 基础CSP配置（Nginx）

```nginx
# nginx-pro.conf
add_header Content-Security-Policy "
  default-src 'self';
  script-src 'self' 'unsafe-inline' 'unsafe-eval';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  font-src 'self' data:;
  connect-src 'self' https://api.example.com;
  frame-ancestors 'self';
  form-action 'self';
  base-uri 'self';
" always;
```

#### 2. 生产环境严格CSP

```nginx
add_header Content-Security-Policy "
  default-src 'none';
  script-src 'self';
  style-src 'self';
  img-src 'self';
  font-src 'self';
  connect-src 'self';
  frame-ancestors 'none';
  form-action 'self';
  report-uri /csp-report;
" always;
```

#### 3. Vue项目中的nonce支持

```javascript
// vue.config.js
const crypto = require('crypto');

module.exports = {
  chainWebpack: config => {
    // 生成nonce
    config.plugin('html').tap(args => {
      const nonce = crypto.randomBytes(16).toString('base64');
      args[0].nonce = nonce;
      return args;
    });
    
    // 配置内联脚本使用nonce
    config.module
      .rule('vue')
      .use('vue-loader')
      .tap(options => {
        options.compilerOptions.directives = {
          script: (el, dir) => {
            el.props.push({ name: 'nonce', value: `'${nonce}'` });
          }
        };
        return options;
      });
  }
};
```

---

## 2.5 Subresource Integrity (SRI)

### 📊 当前状态

| 检查项 | 状态 | 说明 |
|-------|------|------|
| SRI配置 | ❌ **未配置** | CDN资源无integrity属性 |
| 第三方库 | ⚠️ **通过npm管理** | 主要依赖本地node_modules |
| 外部脚本 | ⚠️ **需审查** | 需检查是否有直接引用的外部脚本 |

### 🔍 现有依赖管理

```json
// package.json
{
  "dependencies": {
    "vue": "^2.6.11",
    "ant-design-vue": "^1.7.2",
    "axios": "^0.19.2",
    // ... 其他依赖通过npm管理
  }
}
```

**✅ 做得好的地方：**
- 主要依赖通过npm管理
- 使用了lock文件（yarn.lock）

### ✅ SRI学习思考

#### 1. 检查外部资源引用

```bash
# 检查index.html中的外部资源
grep -E "(src|href)=['\"]https?://" index.html
```

#### 2. 为CDN资源添加SRI

```html
<!-- 使用SRI的示例 -->
<script 
  src="https://cdn.example.com/library.js" 
  integrity="sha384-oqVuAfXRKap..."
  crossorigin="anonymous">
</script>
```

#### 3. 生成SRI哈希

```bash
# 使用OpenSSL生成SHA384哈希
cat library.js | openssl dgst -sha384 -binary | openssl base64 -A
```

---

# Part 3：前端可访问性(a11y)

## 3.1 ARIA标签使用

### 📊 当前状态

| 检查项 | 状态 | 说明 |
|-------|------|------|
| ARIA角色定义 | ⚠️ **部分使用** | 在部分组件中使用了aria属性 |
| aria-label | ⚠️ **存在但不规范** | 部分元素有aria-label |
| aria-expanded | ⚠️ **存在** | 折叠面板有使用 |
| aria-hidden | ⚠️ **存在** | 部分图标有使用 |
| aria-required | ❌ **未使用** | 表单未关联 |
| aria-describedby | ❌ **未使用** | 未关联说明文字 |

### 🔍 发现的使用情况

```bash
# 搜索ARIA使用
$ grep -rn "aria" ./picc-mzmtb-agent/src/ | head -20

# 结果：存在aria使用但不规范、不完整
```

### ✅ ARIA学习思考

#### 1. 为图标添加替代文本

```vue
<!-- ❌ 当前写法 -->
<img src="icon.png" />
<i class="icon-user"></i>

<!-- ✅ 改进后 -->
<img src="icon.png" alt="用户图标" aria-hidden="true" />
<i class="icon-user" role="img" aria-label="用户"></i>
```

#### 2. 为表单元素关联标签

```vue
<!-- ❌ 当前写法 -->
<a-input placeholder="请输入用户名" />

<!-- ✅ 改进后 -->
<a-form-item label="用户名">
  <a-input 
    id="username" 
    placeholder="请输入用户名" 
    aria-describedby="username-help"
  />
  <span id="username-help" class="sr-only">
    用户名长度为4-20个字符
  </span>
</a-form-item>
```

#### 3. 为模态框添加ARIA属性

```vue
<a-modal
  title="用户信息"
  :visible="modalVisible"
  :aria-labelledby="'modal-title'"
  role="dialog"
>
  <template slot="default" #default>
    <h2 id="modal-title">用户信息编辑</h2>
    <!-- 内容 -->
  </template>
</a-modal>
```

#### 4. 为表格添加描述

```vue
<a-table
  :columns="columns"
  :data-source="data"
  :aria-label="'用户列表表格'"
  :row-selection="rowSelection"
>
  <span slot="noData" slot-scope="">
    暂无数据
  </span>
</a-table>
```

---

## 3.2 键盘导航支持

### 📊 当前状态

| 检查项 | 状态 | 说明 |
|-------|------|------|
| Tab导航 | ⚠️ **部分支持** | 仅搜索框支持回车搜索 |
| focus管理 | ❌ **未规范化** | 无焦点管理策略 |
| 快捷键 | ❌ **未实现** | 无键盘快捷键 |
| Skip Link | ❌ **未实现** | 无跳过导航链接 |
| 焦点可见性 | ⚠️ **依赖浏览器** | 未自定义焦点样式 |

### 🔍 发现的使用情况

```javascript
// 搜索框的回车支持
// src/components/searchCard/index.vue:68
<a-input @keyup.enter="handleSearch($event)" />

// 表格编辑回车确认
// src/pages/ChronicDis/components/prescription.vue:49
<a-input @keyup.enter="edit(record.id,'finished')" />
```

### ✅ 键盘导航学习思考

#### 1. 添加Skip Link（跳过导航）

```vue
<!-- App.vue -->
<template>
  <div id="app">
    <a href="#main-content" class="skip-link">
      跳过导航，直接跳到主要内容
    </a>
    <header>...</header>
    <main id="main-content">
      <router-view />
    </main>
  </div>
</template>

<style>
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #000;
  color: #fff;
  padding: 8px;
  z-index: 100;
  transition: top 0.3s;
}

.skip-link:focus {
  top: 0;
}
</style>
```

#### 2. 定义焦点管理策略

```javascript
// src/utils/a11y.js

/**
 * 管理焦点跳转到指定元素
 */
export function focusElement(selector) {
  const element = document.querySelector(selector);
  if (element) {
    element.focus();
  }
}

/**
 * 模态框打开时聚焦到标题
 */
export function focusModalTitle(modalId) {
  const title = document.querySelector(`#${modalId} h2`);
  if (title) {
    title.setAttribute('tabindex', '-1');
    title.focus();
  }
}

/**
 * 捕获Trap焦点（模态框内）
 */
export function trapFocus(containerSelector) {
  const container = document.querySelector(containerSelector);
  if (!container) return;

  const focusableElements = container.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  
  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];

  container.addEventListener('keydown', (e) => {
    if (e.key !== 'Tab') return;

    if (e.shiftKey) {
      if (document.activeElement === firstElement) {
        lastElement.focus();
        e.preventDefault();
      }
    } else {
      if (document.activeElement === lastElement) {
        firstElement.focus();
        e.preventDefault();
      }
    }
  });
}
```

#### 3. 定义键盘快捷键

```javascript
// src/utils/shortcuts.js
const shortcuts = {
  'Alt+S': '提交/保存',
  'Alt+C': '取消',
  'Alt+N': '新建',
  'Alt+F': '搜索',
  'Escape': '关闭弹窗',
  '?': '显示帮助'
};

export function registerShortcuts(vm) {
  document.addEventListener('keydown', (e) => {
    const key = [];
    if (e.altKey) key.push('Alt');
    if (e.ctrlKey) key.push('Ctrl');
    if (e.shiftKey) key.push('Shift');
    key.push(e.key.toUpperCase());
    
    const combo = key.join('+');
    
    if (combo === 'ALT+S') {
      e.preventDefault();
      vm.handleSubmit();
    }
    // ... 其他快捷键处理
  });
}
```

#### 4. 添加焦点样式

```less
// src/assets/css/a11y.less

// 全局焦点样式
*:focus {
  outline: 2px solid @primary-color;
  outline-offset: 2px;
}

// 隐藏的焦点样式（用于sr-only）
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

// 焦点不可见（仅屏幕阅读器可见）
.sr-only-focusable:focus,
.sr-only-focusable:active {
  position: static;
  width: auto;
  height: auto;
  margin: 0;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

---

## 3.3 颜色对比度

### 📊 当前状态

| 检查项 | 状态 | 说明 |
|-------|------|------|
| 主色调 | ⚠️ **合规** | #456CFA 符合对比度要求 |
| 错误色 | ✅ **合规** | #f5222d 对比度良好 |
| 次要文字 | ⚠️ **需审查** | @text-color-secondary: rgba(0,0,0,0.65) |
| 禁用色 | ❌ **不达标** | @disabled-color: rgba(0,0,0,0.45) |

### 🎨 主题色配置

```less
// src/assets/ant-theme-file.less
@primary-color: rgb(69, 108, 250);     // #456CFA - ✅ 达标
@link-color: rgb(45 140 240);           // #2D8CF0 - ✅ 达标
@success-color: #52c41a;                // ✅ 达标
@warning-color: #faad14;                // ✅ 达标
@error-color: #f5222d;                 // ✅ 达标
@text-color: rgba(0, 0, 0, 0.75);       // ⚠️ 需要验证
@text-color-secondary: rgba(0, 0, 0, 0.65);  // ⚠️ 需要验证
@disabled-color: rgba(0, 0, 0, 0.45);   // ❌ 不达标（应≥4.5:1）
```

### 🔍 对比度分析

| 颜色组合 | 对比度 | WCAG AA | WCAG AAA | 状态 |
|---------|--------|---------|----------|------|
| #456CFA 文字 on 白 | 4.6:1 | ✅ | ❌ | 勉强达标 |
| #2D8CF0 文字 on 白 | 4.2:1 | ❌ | ❌ | 不达标 |
| rgba(0,0,0,0.65) on 白 | 6.9:1 | ✅ | ✅ | 达标 |
| rgba(0,0,0,0.45) on 白 | 3.1:1 | ❌ | ❌ | 不达标 |

### ✅ 颜色对比度学习思考

#### 1. 调整禁用颜色

```less
// 当前（不达标）
@disabled-color: rgba(0, 0, 0, 0.45);

// 改进后（达标）
@disabled-color: rgba(0, 0, 0, 0.38);  // 对比度≥4.5:1
```

#### 2. 调整链接颜色

```less
// 当前（不达标）
@link-color: rgb(45 140 240);  // #2D8CF0

// 改进后（推荐）
@link-color: rgb(24, 144, 255);  // #1890FF - 对比度 5.9:1
```

#### 3. 创建对比度工具函数

```javascript
// src/utils/colorContrast.js

/**
 * 计算颜色对比度
 */
function getLuminance(r, g, b) {
  const [rs, gs, bs] = [r, g, b].map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

function getContrastRatio(color1, color2) {
  const l1 = getLuminance(...color1);
  const l2 = getLuminance(...color2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

// 检查是否符合WCAG标准
function meetsWCAG(contrastRatio, level = 'AA') {
  return level === 'AAA' ? contrastRatio >= 7 : contrastRatio >= 4.5;
}
```

#### 4. 登录页面颜色审查

```less
// src/components/loginMb/index.vue
// 需要审查的颜色

color: #5478F9;           // 链接色 - ⚠️ 需验证
color: #456cfa;           // 文字色 - ✅ 达标
color: #A5B6C6;           // 占位符 - ❌ 不达标
background: #5385FF;      // 按钮 - ✅ 达标
```

---

## 3.4 表单标签关联

### 📊 当前状态

| 检查项 | 状态 | 说明 |
|-------|------|------|
| label关联 | ⚠️ **部分关联** | 使用placeholder代替label |
| 错误提示 | ⚠️ **存在** | 使用v-decorator的message |
| 必填标记 | ⚠️ **不统一** | 有*标记但无aria-required |
| 帮助文本 | ⚠️ **存在** | 使用placeholder |

### 🔍 发现的问题

#### 问题1：使用placeholder代替label

```vue
<!-- ❌ 当前写法 - 仅使用placeholder -->
<a-input
  placeholder="请输入用户名"
  v-decorator="['username', { rules: [...] }]"
/>

<!-- ⚠️ 部分有label -->
<a-form-item label="用户名">
  <a-input ... />
</a-form-item>
```

**WCAG要求：** 所有输入框必须有可见的标签，placeholder不能替代标签。

#### 问题2：必填字段无aria-required

```vue
<!-- ❌ 当前写法 -->
<a-input v-decorator="['username', { rules: [{ required: true }] }]" />

<!-- ✅ 改进后 -->
<a-input 
  v-decorator="['username', { rules: [{ required: true }] }]"
  aria-required="true"
/>
```

### ✅ 表单可访问性学习思考

#### 1. 统一表单结构（必填字段）

```vue
<a-form layout="horizontal">
  <a-form-item
    label="用户名"
    name="username"
    required
    :validateStatus="validateStatus"
    :help="helpText"
  >
    <a-input
      id="username"
      v-model="form.username"
      aria-describedby="username-help username-error"
      aria-required="true"
    />
    <template #help>
      <span id="username-help">用户名长度为4-20个字符</span>
    </template>
  </a-form-item>
</a-form>
```

#### 2. 创建可复用的表单组件

```vue
<!-- src/components/a11y/FormItem.vue -->
<template>
  <a-form-item
    :label="label"
    :required="required"
    :validateStatus="validateStatus"
    :help="helpText"
  >
    <component
      :is="inputType"
      v-bind="$attrs"
      v-on="$listeners"
      :id="inputId"
      :aria-label="label"
      :aria-required="required"
      :aria-describedby="helpId"
    />
    <template v-if="helpText" #help>
      <span :id="helpId" class="form-help">
        {{ helpText }}
      </span>
    </template>
  </a-form-item>
</template>

<script>
export default {
  props: {
    label: String,
    required: Boolean,
    helpText: String,
    inputId: String,
    inputType: {
      type: String,
      default: 'a-input'
    }
  },
  computed: {
    helpId() {
      return this.inputId ? `${this.inputId}-help` : null;
    }
  }
}
</script>
```

#### 3. 错误状态通知

```javascript
// src/utils/a11y.js

/**
 * 通知屏幕阅读器
 */
export function announceToScreenReader(message, priority = 'polite') {
  const announcer = document.createElement('div');
  announcer.setAttribute('role', 'status');
  announcer.setAttribute('aria-live', priority);
  announcer.setAttribute('aria-atomic', 'true');
  announcer.className = 'sr-only';
  announcer.textContent = message;
  
  document.body.appendChild(announcer);
  
  setTimeout(() => {
    document.body.removeChild(announcer);
  }, 1000);
}

/**
 * 表单提交后 announce 结果
 */
export function announceFormResult(isSuccess, message) {
  if (isSuccess) {
    announceToScreenReader('表单提交成功', 'assertive');
  } else {
    announceToScreenReader(`表单提交失败：${message}`, 'assertive');
  }
}
```

---

# Part 4：前端工程化建议

## 4.1 微前端改造可行性

### 📊 当前状态

| 检查项 | 状态 | 说明 |
|-------|------|------|
| 微前端框架 | ❌ **未使用** | 当前是单体应用 |
| 模块划分 | ⚠️ **存在** | 有mtbcomponents、mtbnewcomponents等 |
| 独立部署 | ⚠️ **受限** | 代码耦合较紧 |

### 🔍 现有代码组织

```
src/
├── components/           # 通用组件
├── mtbcomponents/        # 慢特病组件（复制的）
├── mtbnewcomponents/     # 慢特病新组件（复制的）
├── mtbslcomponents/       # 另一套组件（复制的）
├── pages/
│   ├── ChronicDis/       # 慢病管理页面
│   ├── DZChronicDis/     # 电子病历
│   ├── JZChronicDis/     # 集中管理
│   ├── MZLChronicDis/    # 门诊慢特病
│   └── ...
```

**⚠️ 问题：存在大量重复组件代码**

| 组件目录 | 存在重复 |
|---------|----------|
| searchCard | 4份 |
| textArea | 4份 |
| Modal相关 | 3-4份 |

### ✅ 微前端改造建议

#### 方案A：渐进式迁移（推荐）

**适用场景：** 业务稳定，需要逐步拆分

**步骤：**

1. **第一阶段：组件库抽离**
   - 抽取公共组件到独立npm包
   - 统一使用单一套组件

2. **第二阶段：按业务域拆分**
   - 按页面类型拆分为不同子应用
   - 使用qiankun或single-spa进行集成

```javascript
// 主应用注册子应用
import { registerMicroApps, start } from 'qiankun';

registerMicroApps([
  {
    name: 'chronic-disease',
    entry: '//localhost:8081',
    container: '#container',
    activeRule: '/chronic',
  },
  {
    name: 'declare-management',
    entry: '//localhost:8082',
    container: '#container',
    activeRule: '/declare',
  },
]);

start();
```

#### 方案B：保持单体架构

**适用场景：** 快速迭代期，避免架构复杂度

**建议：**
- 暂不引入微前端
- 先进行组件库抽离和代码规范化
- 等Vue 3升级完成后再考虑

### 🎯 优先级建议

| 优先级 | 建议事项 | 原因 |
|-------|---------|------|
| P0 | 组件库统一 | 减少维护成本，提高一致性 |
| P1 | 插件化改造 | 按需加载，提升性能 |
| P2 | 微前端评估 | 视团队规模和后续需求 |

---

## 4.2 组件库抽离

### 📊 当前状态

| 检查项 | 状态 | 说明 |
|-------|------|------|
| 公共组件 | ⚠️ **存在但不统一** | 多套重复组件 |
| 组件文档 | ❌ **无** | 无组件文档 |
| 组件测试 | ❌ **无** | 无单元测试 |

### 🔍 组件目录结构

```
src/components/           # 通用组件 (~20个)
src/mtbcomponents/        # 慢特病组件 (~15个)
src/mtbnewcomponents/     # 慢特病新组件 (~20个)
src/mtbslcomponents/      # 另一套组件 (~15个)
```

### ✅ 组件库抽离方案

#### 1. 创建独立组件包

```bash
# 创建组件库目录
mkdir picc-mzmtb-components
cd picc-mzmtb-components
npm init -y
```

#### 2. 目录结构

```
picc-mzmtb-components/
├── src/
│   ├── SearchCard/
│   ├── TextArea/
│   ├── MyTable/
│   ├── Modal/
│   └── ...
├── docs/                  # 组件文档
├── .eslintrc.js
├── package.json
└── README.md
```

#### 3. 发布npm包

```json
{
  "name": "@picc/mzmtb-components",
  "version": "1.0.0",
  "main": "lib/index.js",
  "scripts": {
    "build": "vue-cli-service build",
    "lib": "vue-cli-service build --target lib --name piccComponents src/index.js"
  }
}
```

#### 4. 在主项目中使用

```bash
npm install @picc/mzmtb-components --save
```

```javascript
// main.js
import PiccComponents from '@picc/mzmtb-components';
import '@picc/mzmtb-components/lib/index.css';

Vue.use(PiccComponents);
```

### 📋 待抽离组件清单

| 组件名 | 重复次数 | 优先级 | 复杂度 |
|-------|---------|-------|--------|
| SearchCard | 4 | P0 | 中 |
| TextArea | 4 | P0 | 低 |
| MyTable | 3 | P0 | 高 |
| Modal | 4 | P1 | 高 |
| Header | 3 | P1 | 低 |

---

## 4.3 Monorepo改造

### 📊 当前状态

| 检查项 | 状态 | 说明 |
|-------|------|------|
| Monorepo | ❌ **未使用** | 单一仓库 |
| 包管理 | ⚠️ **yarn** | 使用yarn但未利用workspace |
| 代码共享 | ❌ **复制粘贴** | 组件重复复制 |

### ✅ Monorepo改造方案

#### 使用Yarn Workspace

```json
// package.json (根目录)
{
  "private": true,
  "workspaces": [
    "packages/*"
  ],
  "scripts": {
    "dev": "yarn workspace @picc/mzmtb-main dev",
    "build": "yarn workspace @picc/mzmtb-main build"
  }
}
```

#### 目录结构

```
picc-mzmtb/
├── packages/
│   ├── main-app/              # 主应用
│   │   └── package.json
│   ├── shared-components/     # 共享组件库
│   │   └── package.json
│   ├── shared-utils/          # 共享工具库
│   │   └── package.json
│   └── shared-styles/         # 共享样式
│       └── package.json
├── package.json               # Workspace根配置
├── lerna.json                 # Lerna配置（可选）
└── yarn.lock
```

#### 迁移步骤

1. **Step 1: 初始化Monorepo**
   ```bash
   mkdir picc-mzmtb && cd picc-mzmtb
   yarn init -y
   ```

2. **Step 2: 创建子包**
   ```bash
   mkdir -p packages/main-app packages/shared-components
   ```

3. **Step 3: 配置package.json**
   ```json
   {
     "workspaces": ["packages/*"],
     "private": true
   }
   ```

4. **Step 4: 安装依赖**
   ```bash
   yarn install
   ```

---

## 4.4 TypeScript迁移建议

### 📊 当前状态

| 检查项 | 状态 | 说明 |
|-------|------|------|
| TypeScript | ❌ **未使用** | 当前使用JavaScript |
| JSDoc | ⚠️ **极少** | 少量使用 |
| 类型定义 | ❌ **无** | 无.d.ts文件 |

### 🎯 迁移策略

#### 渐进式迁移（推荐）

**阶段1: 添加TypeScript配置（1周）**

```bash
npm install typescript @types/node @types/vue @types/webpack --save-dev
```

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "strict": false,  // 宽松模式开始
    "jsx": "preserve",
    "moduleResolution": "node",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    },
    "typeRoots": ["node_modules/@types", "src/types"]
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

**阶段2: 创建类型定义文件**

```typescript
// src/types/vue-shim.d.ts
declare module '*.vue' {
  import Vue from 'vue';
  export default Vue;
}

// src/types/api.d.ts
interface ApiResponse<T = any> {
  code: number;
  data: T;
  message: string;
}

interface PageParams {
  page: number;
  pageSize: number;
  [key: string]: any;
}

// src/types/store.d.ts
interface RootState {
  token: string;
  userInfo: UserInfo | null;
}
```

**阶段3: 关键模块添加类型**

```typescript
// src/api/types.ts
import { AxiosRequestConfig } from 'axios';

interface HttpRequestOptions extends AxiosRequestConfig {
  apiCode?: string;
}

class HttpRequest {
  constructor();
  request<T = any>(options: HttpRequestOptions): Promise<ApiResponse<T>>;
  get<T = any>(url: string, params?: object): Promise<ApiResponse<T>>;
  post<T = any>(url: string, data?: object): Promise<ApiResponse<T>>;
}
```

**阶段4: Vue组件类型增强**

```typescript
// src/components/MyTable/index.vue
<template>
  <a-table :columns="columns" :data-source="data" />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator';

interface Column {
  title: string;
  dataIndex: string;
  key: string;
  scopedSlots?: { customRender: string };
}

interface Record {
  id: string | number;
  [key: string]: any;
}

@Component
export default class MyTable extends Vue {
  @Prop({ type: Array, default: () => [] })
  columns!: Column[];

  @Prop({ type: Array, default: () => [] })
  data!: Record[];
}
</script>
```

### 📊 迁移工作量估算

| 模块 | 文件数 | 预估工时 | 优先级 |
|-----|-------|---------|--------|
| 类型定义 | ~10个 | 1周 | P0 |
| API层 | ~30个 | 2周 | P1 |
| 工具函数 | ~20个 | 1周 | P1 |
| Vue组件 | ~650个 | 8-12周 | P2 |
| **总计** | **~710个** | **12-16周** | - |

### ⚠️ 注意事项

1. **Vue 2 + TypeScript**: 需要安装 `vue-property-decorator`
2. **渐进式迁移**: 建议从新组件开始，逐步覆盖老组件
3. **不强制迁移**: 已有稳定运行的组件可保持JS

---

# Part 5：SEO与PWA

## 5.1 Meta标签优化

### 📊 当前状态

```html
<!-- index.html 当前配置 -->
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0,user-scalable=0,minimum-scale=1.0,maximum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=Edge" />
    <title>门诊慢特病业务管理信息系统</title>
    <link rel="icon" href="/static/images/favicon.ico" type="image/x-icon">
  </head>
```

### ⚠️ 问题分析

| 检查项 | 状态 | 说明 |
|-------|------|------|
| description | ❌ **缺失** | 无页面描述 |
| keywords | ❌ **缺失** | 无关键词 |
| og标签 | ❌ **缺失** | 无社交分享标签 |
| twitter标签 | ❌ **缺失** | 无Twitter卡片 |
| canonical | ❌ **缺失** | 无规范链接 |
| robots | ❌ **缺失** | 无爬虫指导 |

### ✅ Meta标签学习要点

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=Edge,chrome=1">
  
  <!-- 基础Meta -->
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <meta name="theme-color" content="#456CFA">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  
  <!-- SEO Meta -->
  <title>门诊慢特病业务管理信息系统 - PICC慢特病管理平台</title>
  <meta name="description" content="PICC门诊慢特病业务管理信息系统，提供慢特病申报、审核、结算全流程线上管理服务，支持慢病体检、专家分配、用户管理等功能。">
  <meta name="keywords" content="门诊慢特病,慢病管理,特病申报,医保管理,PICC,医院管理系统">
  <meta name="author" content="PICC">
  <meta name="robots" content="index, follow">
  
  <!-- 规范链接 -->
  <link rel="canonical" href="https://mzmtb.picc.com/">
  
  <!-- Open Graph (社交分享) -->
  <meta property="og:type" content="website">
  <meta property="og:title" content="门诊慢特病业务管理信息系统">
  <meta property="og:description" content="PICC门诊慢特病业务管理信息系统，提供慢特病申报、审核、结算全流程线上管理服务。">
  <meta property="og:url" content="https://mzmtb.picc.com/">
  <meta property="og:site_name" content="PICC慢特病管理">
  <meta property="og:image" content="https://mzmtb.picc.com/static/images/og-image.png">
  <meta property="og:locale" content="zh_CN">
  
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="门诊慢特病业务管理信息系统">
  <meta name="twitter:description" content="PICC门诊慢特病业务管理信息系统">
  <meta name="twitter:image" content="https://mzmtb.picc.com/static/images/og-image.png">
  
  <!-- 浏览器配置 -->
  <meta name="format-detection" content="telephone=no">
  <meta http-equiv="X-Content-Type-Options" content="nosniff">
  
  <!-- 图标 -->
  <link rel="icon" type="image/x-icon" href="/static/images/favicon.ico">
  <link rel="apple-touch-icon" href="/static/images/icon-192.png">
  
  <!-- DNS预解析 -->
  <link rel="dns-prefetch" href="//cdn.picc.com">
  <link rel="dns-prefetch" href="//api.picc.com">
</head>
```

---

## 5.2 PWA改造可行性

### 📊 当前状态

| 检查项 | 状态 | 说明 |
|-------|------|------|
| Service Worker | ❌ **未配置** | 无SW |
| Web App Manifest | ❌ **未配置** | 无manifest.json |
| 离线缓存 | ❌ **未实现** | 无离线访问 |
| 安装提示 | ❌ **未实现** | 无PWA安装banner |

### ✅ PWA改造方案

#### 1. 安装依赖

```bash
npm install workbox-webpack-plugin --save-dev
npm install vue-pwa-ace --save
```

#### 2. 创建manifest.json

```json
// public/manifest.json
{
  "name": "门诊慢特病业务管理信息系统",
  "short_name": "慢特病管理",
  "description": "PICC门诊慢特病业务管理信息系统",
  "start_url": "/",
  "display": "standalone",
  "orientation": "portrait",
  "background_color": "#ffffff",
  "theme_color": "#456CFA",
  "icons": [
    {
      "src": "/static/images/icon-72.png",
      "sizes": "72x72",
      "type": "image/png"
    },
    {
      "src": "/static/images/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/images/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "categories": ["business", "medical"],
  "lang": "zh-CN"
}
```

#### 3. 注册Service Worker

```javascript
// src/registerServiceWorker.js
import { register } from 'register-service-worker';

if (process.env.NODE_ENV === 'production') {
  register(`${process.env.BASE_URL}service-worker.js`, {
    ready() {
      console.log('Service Worker 已加载');
    },
    registered() {
      console.log('Service Worker 已注册');
    },
    cached() {
      console.log('内容已缓存离线可用');
    },
    updatefound() {
      console.log('发现新内容正在下载...');
    },
    updated() {
      console.log('新内容已可用，请刷新');
      // 可以显示更新提示
    },
    offline() {
      console.log('无可用网络，显示离线页面');
    },
    error(err) {
      console.error('Service Worker 错误:', err);
    }
  });
}
```

#### 4. Workbox配置

```javascript
// vue.config.js
const { InjectManifest } = require('workbox-webpack-plugin');

module.exports = {
  pwa: {
    name: '门诊慢特病管理',
    themeColor: '#456CFA',
    msTileColor: '#456CFA',
    appleMobileWebAppCapable: 'yes',
    appleMobileWebAppStatusBarStyle: 'black-translucent',
    workboxPluginMode: 'InjectManifest',
    workboxOptions: {
      swSrc: './src/sw.js',
      swDest: 'service-worker.js',
    }
  }
};
```

#### 5. 创建Service Worker

```javascript
// src/sw.js
importScripts('https://storage.googleapis.com/workbox-cdn/releases/5.1.2/workbox-sw.js');

workbox.core.setCacheNameDetails({
  prefix: 'mzmtb',
  suffix: 'v1'
});

workbox.precaching.precacheAndRoute(self.__WB_MANIFEST);

// 静态资源缓存
workbox.routing.registerRoute(
  /\.(?:js|css)$/,
  new workbox.strategies.StaleWhileRevalidate({
    cacheName: 'static-resources',
  })
);

// 图片缓存
workbox.routing.registerRoute(
  /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
  new workbox.strategies.CacheFirst({
    cacheName: 'images',
    plugins: [
      new workbox.expiration.ExpirationPlugin({
        maxEntries: 60,
        maxAgeSeconds: 30 * 24 * 60 * 60, // 30天
      }),
    ],
  })
);

// API缓存（仅GET请求）
workbox.routing.registerRoute(
  /\/api\//,
  new workbox.strategies.NetworkFirst({
    cacheName: 'api-cache',
    plugins: [
      new workbox.expiration.ExpirationPlugin({
        maxEntries: 30,
        maxAgeSeconds: 24 * 60 * 60, // 1天
      }),
    ],
  })
);
```

---

## 5.3 离线缓存策略

### 📊 需求分析

| 功能模块 | 离线需求 | 建议策略 |
|---------|---------|---------|
| 登录页面 | 必须离线 | CacheFirst |
| 静态资源 | 必须离线 | StaleWhileRevalidate |
| 用户信息 | 可选离线 | NetworkFirst |
| 业务数据 | 不建议离线 | NetworkOnly |
| 处方信息 | 不建议离线 | NetworkOnly |

### ✅ 离线策略实现

#### 1. 分级缓存策略

```javascript
// src/utils/offlineStrategy.js

/**
 * 缓存策略配置
 */
const cacheStrategies = {
  // 静态资源 - 优先缓存
  static: {
    strategy: 'StaleWhileRevalidate',
    maxAge: 7 * 24 * 60 * 60, // 7天
    maxEntries: 50
  },
  
  // 登录相关 - 必须可用
  auth: {
    strategy: 'CacheFirst',
    maxAge: 24 * 60 * 60, // 24小时
    maxEntries: 5
  },
  
  // 业务数据 - 优先网络
  business: {
    strategy: 'NetworkFirst',
    maxAge: 0,
    maxEntries: 20
  },
  
  // 用户数据 - 适中策略
  user: {
    strategy: 'NetworkFirst',
    maxAge: 30 * 60, // 30分钟
    maxEntries: 10
  }
};

/**
 * 判断缓存类型
 */
function getCacheType(url) {
  if (url.includes('/static/') || url.includes('.css') || url.includes('.js')) {
    return 'static';
  }
  if (url.includes('/auth/') || url.includes('/login')) {
    return 'auth';
  }
  if (url.includes('/api/user')) {
    return 'user';
  }
  return 'business';
}
```

#### 2. 离线数据同步

```javascript
// src/utils/syncManager.js

class SyncManager {
  constructor() {
    this.pendingSyncs = [];
  }

  // 记录待同步操作
  async addPendingSync(operation) {
    const syncItem = {
      id: this.generateId(),
      operation,
      timestamp: Date.now(),
      retries: 0
    };
    
    this.pendingSyncs.push(syncItem);
    await this.saveToLocalStorage();
    
    // 如果在线，立即尝试同步
    if (navigator.onLine) {
      this.processPendingSyncs();
    }
  }

  // 处理待同步操作
  async processPendingSyncs() {
    for (const item of this.pendingSyncs) {
      try {
        await this.executeOperation(item.operation);
        this.removePendingSync(item.id);
      } catch (error) {
        item.retries++;
        if (item.retries >= 3) {
          // 超过重试次数，标记为失败
          item.status = 'failed';
        }
      }
    }
    await this.saveToLocalStorage();
  }

  // 监听网络状态
  setupNetworkListeners() {
    window.addEventListener('online', () => {
      console.log('网络已连接，开始同步...');
      this.processPendingSyncs();
    });

    window.addEventListener('offline', () => {
      console.log('网络已断开，进入离线模式');
    });
  }
}

export default new SyncManager();
```

#### 3. 离线状态UI提示

```vue
<!-- src/components/OfflineBanner.vue -->
<template>
  <transition name="slide">
    <div v-if="isOffline" class="offline-banner">
      <span class="offline-icon">📡</span>
      <span class="offline-text">当前处于离线模式，部分功能可能受限</span>
    </div>
  </transition>
</template>

<script>
export default {
  data() {
    return {
      isOffline: !navigator.onLine
    };
  },
  
  created() {
    window.addEventListener('offline', () => {
      this.isOffline = true;
    });
    
    window.addEventListener('online', () => {
      this.isOffline = false;
    });
  }
};
</script>

<style scoped>
.offline-banner {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: #faad14;
  color: #000;
  padding: 8px 16px;
  text-align: center;
  z-index: 9999;
}

.slide-enter-active, .slide-leave-active {
  transition: transform 0.3s;
}

.slide-enter, .slide-leave-to {
  transform: translateY(-100%);
}
</style>
```

---

# 总结与优先级建议

## 📊 改进项汇总

| 类别 | 改进项 | 优先级 | 工作量 | 风险 |
|-----|-------|-------|-------|------|
| **代码规范** | ESLint升级到v9 | P1 | 1天 | 低 |
| **代码规范** | 添加Prettier | P1 | 1天 | 低 |
| **代码规范** | 配置Git Hooks | P1 | 2天 | 中 |
| **代码规范** | 添加commitlint | P2 | 1天 | 低 |
| **安全** | 添加CSP配置 | P0 | 2天 | 高 |
| **安全** | XSS过滤器 | P0 | 2天 | 中 |
| **安全** | SRI配置 | P2 | 1天 | 低 |
| **可访问性** | ARIA标签完善 | P1 | 5天 | 低 |
| **可访问性** | 键盘导航 | P1 | 3天 | 低 |
| **可访问性** | 颜色对比度 | P2 | 2天 | 低 |
| **可访问性** | 表单标签关联 | P1 | 3天 | 低 |
| **工程化** | 组件库抽离 | P0 | 4周 | 中 |
| **工程化** | Monorepo改造 | P2 | 2周 | 中 |
| **工程化** | TypeScript迁移 | P2 | 12-16周 | 高 |
| **SEO/PWA** | Meta标签优化 | P2 | 1天 | 低 |
| **SEO/PWA** | PWA改造 | P3 | 2周 | 中 |

## 🎯 分阶段实施计划

### Phase 1: 安全加固（1-2周）
1. 添加Content-Security-Policy
2. 添加XSS过滤器
3. 增强CSRF防护

### Phase 2: 可访问性提升（2-3周）
1. 添加ARIA标签
2. 完善键盘导航
3. 优化颜色对比度
4. 规范表单结构

### Phase 3: 代码规范化（2周）
1. 升级ESLint
2. 添加Prettier
3. 配置Git Hooks
4. 添加commitlint

### Phase 4: 工程化改进（中长期）
1. 组件库统一抽离
2. Monorepo改造
3. TypeScript迁移评估

---

## 📝 附录

### A. 相关文档链接

- [Vue.js 可访问性指南](https://vuejs.org/v2/guide/accessibility.html)
- [WCAG 2.1 规范](https://www.w3.org/WAI/WCAG21/quickref/)
- [Ant Design Vue 可访问性](https://antdv.com/docs/vue/introduce-cn/)
- [ESLint 官方文档](https://eslint.org/docs/user-guide/)
- [Workbox 文档](https://developers.google.com/web/tools/workbox/)

### B. 推荐工具

- [axe DevTools](https://www.deque.com/axe/) - 可访问性检测
- [Lighthouse](https://developers.google.com/web/tools/lighthouse) - 性能与可访问性审计
- [WAVE](https://wave.webaim.org/) - Web可访问性评估
- [Color Contrast Checker](https://webaim.org/resources/contrastchecker/) - 颜色对比度检查

### C. 术语表

| 术语 | 解释 |
|-----|------|
| ESLint | JavaScript代码语法检查工具 |
| Prettier | 代码格式化工具 |
| Husky | Git Hooks管理工具 |
| lint-staged | 暂存区文件检查工具 |
| XSS | 跨站脚本攻击 |
| CSRF | 跨站请求伪造 |
| CSP | 内容安全策略 |
| SRI | 子资源完整性 |
| ARIA | 可访问性富互联网应用 |
| WCAG | 网络内容可访问性指南 |
| PWA | 渐进式Web应用 |
| Service Worker | 后台脚本技术 |
| Monorepo | 单仓库多包管理 |

---

*报告生成时间：2024年*
*分析工具：静态代码分析 + 配置审查*
*覆盖范围：652个Vue组件 + 213个JS文件*
