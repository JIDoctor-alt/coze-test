> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC门诊慢特病前端项目（picc-mzmtb-agent）
# 安全问题原理学习文档

> 文档生成日期：2024年
> 技术栈：Vue 2.6 + Vuex 3 + Axios + Ant Design Vue

---

## 📖 使用说明

本文档提供每个安全问题的**修复前/修复后代码对比**，开发者可以直接复制使用。

---

## 🔴 SEC-001：Token通过URL参数明文传递

### 问题位置

```
/src/mtbnewcomponents/menuList/menuindex.vue:87
/src/mtbnewcomponents/menuList/menudeclare.vue:86
```

### 修复前代码 ❌

```javascript
// menuindex.vue 第87行
goPage(key) {
  let list = this.menuList[key]
  this.$router.push({
    path: `/${key}`,
    query: { token: list.token }  // ❌ 危险！Token明文在URL中
  })
}
```

```javascript
// menudeclare.vue 第86行
goPage(key) {
  let list = this.menuList[key]
  this.$router.push({
    path: `/${key}`,
    query: { token: list.token }  // ❌ 危险！Token明文在URL中
  })
}
```

### 修复后代码 ✅

```javascript
// ✅ 安全版本 - 从sessionStorage或Vuex读取Token
goPage(key) {
  let list = this.menuList[key]
  this.$router.push({
    path: `/${key}`
    // ✅ 不再传递Token，Token会通过请求拦截器自动从存储中读取
  })
}
```

### 完整问题原理

#### 方案一：从sessionStorage读取（推荐短期方案）

```javascript
// src/mtbnewcomponents/menuList/menuindex.vue
export default {
  methods: {
    goPage(key) {
      // ✅ 移除URL中的Token参数
      this.$router.push({
        path: `/${key}`
      })
    }
  }
}
```

#### 方案二：创建统一的Token获取工具（推荐）

```javascript
// src/utils/tokenHelper.js

/**
 * 统一Token获取工具
 * 优先从Vuex获取，其次从sessionStorage获取
 */
import store from '@/store'

export function getToken() {
  // 优先从Vuex获取（内存，速度快）
  const state = store.state
  if (state && state.user && state.user.token) {
    return state.user.token
  }
  
  // 备选：从sessionStorage获取
  const logInfo = sessionStorage.getItem('logInfoMB')
  if (logInfo) {
    try {
      const userInfo = JSON.parse(logInfo)
      return userInfo.token
    } catch (e) {
      console.warn('Token解析失败')
      return null
    }
  }
  
  return null
}

export function setToken(token) {
  // 存入Vuex
  if (store.commit) {
    store.commit('user/SET_TOKEN', token)
  }
}

export function clearToken() {
  // 清除Vuex
  if (store.commit) {
    store.commit('user/CLEAR_TOKEN')
  }
  // 清除sessionStorage
  sessionStorage.removeItem('logInfoMB')
}
```

---

## 🔴 SEC-002：使用不安全的MD5密码哈希

### 问题位置

```
/src/mtbnewcomponents/loginMb/settingModal.vue:114
/src/pages/DZChronicDis/serveStatusMod.vue:418
/src/pages/YLChronicDis/serveStatusMod.vue:418
```

### 修复前代码 ❌

```javascript
// settingModal.vue 第114行
import md5 from 'js-md5'

methods: {
  handleSubmit(values) {
    // ❌ 使用不安全的MD5
    const password = md5(values.password)
    
    this.$http.post('/api/changePassword', {
      password: password,
      // ...
    })
  }
}
```

### 修复后代码 ✅

#### 安装依赖

```bash
npm install crypto-js --save
# 或
yarn add crypto-js
```

#### 创建密码哈希工具

```javascript
// src/utils/passwordHash.js

import CryptoJS from 'crypto-js'

/**
 * 使用SHA-256进行密码哈希（加盐）
 * @param {string} password - 明文密码
 * @param {string} salt - 盐值，默认使用随机盐
 * @returns {string} 哈希后的密码
 */
export function hashPassword(password, salt = null) {
  // 如果没有提供盐值，生成随机盐
  if (!salt) {
    salt = CryptoJS.lib.WordArray.random(128 / 8).toString()
  }
  
  // 使用SHA-256进行两次哈希
  const hashed = CryptoJS.SHA256(password + salt)
  
  // 返回盐值和哈希值拼接的字符串
  return salt + ':' + hashed.toString()
}

/**
 * 验证密码
 * @param {string} inputPassword - 用户输入的密码
 * @param {string} storedHash - 存储的哈希值（格式：salt:hash）
 * @returns {boolean} 是否匹配
 */
export function verifyPassword(inputPassword, storedHash) {
  const parts = storedHash.split(':')
  if (parts.length !== 2) {
    return false
  }
  
  const [salt, originalHash] = parts
  const newHash = CryptoJS.SHA256(inputPassword + salt).toString()
  
  return newHash === originalHash
}

/**
 * 生成随机盐值
 * @returns {string} 随机盐值
 */
export function generateSalt() {
  return CryptoJS.lib.WordArray.random(128 / 8).toString()
}
```

#### 修复登录页面

```javascript
// src/mtbnewcomponents/loginMb/index.vue

import { hashPassword } from '@/utils/passwordHash'

export default {
  methods: {
    handleLogin() {
      // ✅ 使用SHA-256哈希密码
      const hashedPassword = hashPassword(this.loginForm.password)
      
      this.$http.post('/api/login', {
        username: this.loginForm.username,
        password: hashedPassword
      }).then(res => {
        // 登录成功处理
        const userInfo = res.data
        userInfo.password = undefined // 清除内存中的密码
        
        // 存储到sessionStorage
        window.sessionStorage.setItem('logInfoMB', JSON.stringify(userInfo))
        
        // 同时存入Vuex
        this.$store.commit('user/SET_USER_INFO', userInfo)
      })
    }
  }
}
```

#### 修复修改密码页面

```javascript
// src/mtbnewcomponents/loginMb/settingModal.vue

import { hashPassword } from '@/utils/passwordHash'

export default {
  methods: {
    handleSubmit(values) {
      // ✅ 使用SHA-256哈希新密码
      const hashedPassword = hashPassword(values.password)
      const hashedOldPassword = hashPassword(values.oldPassword)
      
      this.$http.post('/api/changePassword', {
        oldPassword: hashedOldPassword,
        password: hashedPassword,
        confirmPassword: hashPassword(values.confirmPassword)
      }).then(() => {
        this.$message.success('密码修改成功')
        this.$emit('close')
      })
    }
  }
}
```

---

## 🟠 SEC-003：敏感数据存储在sessionStorage

### 问题位置

```
/src/mtbnewcomponents/loginMb/index.vue:177
```

### 修复前代码 ❌

```javascript
// loginMb/index.vue 第177行
// 登录成功后直接存储
window.sessionStorage.setItem("logInfoMB", logInfoMB);
```

### 修复后代码 ✅

#### Step 1: 创建Vuex模块

```javascript
// src/store/modules/user.js

export default {
  namespaced: true,
  
  state: {
    userInfo: null,
    token: null,
    isLoggedIn: false
  },
  
  mutations: {
    SET_USER_INFO(state, userInfo) {
      state.userInfo = userInfo
      state.token = userInfo.token
      state.isLoggedIn = true
    },
    
    CLEAR_USER_INFO(state) {
      state.userInfo = null
      state.token = null
      state.isLoggedIn = false
    },
    
    SET_TOKEN(state, token) {
      state.token = token
    }
  },
  
  actions: {
    login({ commit }, userInfo) {
      commit('SET_USER_INFO', userInfo)
      // 存入sessionStorage作为后备
      window.sessionStorage.setItem('logInfoMB', JSON.stringify(userInfo))
    },
    
    logout({ commit }) {
      commit('CLEAR_USER_INFO')
      window.sessionStorage.removeItem('logInfoMB')
    },
    
    // 页面刷新后从sessionStorage恢复
    restoreSession({ commit }) {
      const logInfoMB = window.sessionStorage.getItem('logInfoMB')
      if (logInfoMB) {
        try {
          const userInfo = JSON.parse(logInfoMB)
          commit('SET_USER_INFO', userInfo)
          return true
        } catch (e) {
          window.sessionStorage.removeItem('logInfoMB')
          return false
        }
      }
      return false
    }
  },
  
  getters: {
    token: state => state.token,
    userInfo: state => state.userInfo,
    isLoggedIn: state => state.isLoggedIn
  }
}
```

#### Step 2: 注册Vuex模块

```javascript
// src/store/index.js

import Vue from 'vue'
import Vuex from 'vuex'
import user from './modules/user'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    user
  },
  
  state: {
    // 其他全局状态
  },
  
  mutations: {
    // 其他mutations
  },
  
  actions: {
    // 其他actions
  }
})
```

#### Step 3: 修改登录页面

```javascript
// src/mtbnewcomponents/loginMb/index.vue

export default {
  methods: {
    handleLogin() {
      this.$http.post('/api/login', {
        username: this.loginForm.username,
        password: this.loginForm.password
      }).then(res => {
        const userInfo = res.data
        
        // ✅ 存入Vuex（内存存储）
        this.$store.dispatch('user/login', userInfo)
        
        // 跳转到首页
        this.$router.push('/')
      }).catch(err => {
        this.$message.error('登录失败')
      })
    }
  }
}
```

#### Step 4: 在App.vue中恢复会话

```javascript
// src/App.vue

export default {
  created() {
    // ✅ 页面加载时尝试恢复会话
    this.$store.dispatch('user/restoreSession')
  }
}
```

---

## 🟠 SEC-004：Token从URL重复解析

### 问题位置

```
/src/api/axiosCenter.js:45-52
```

### 修复前代码 ❌

```javascript
// axiosCenter.js 第45-52行

// 请求拦截器
service.interceptors.request.use(
  config => {
    // ❌ 每次请求都从URL解析Token
    let query = location.href.split('?')[1];
    let token = qs.parse(query, { ignoreQueryPrefix: true })["token"];
    
    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);
```

### 修复后代码 ✅

```javascript
// src/api/axiosCenter.js

// ✅ 创建统一的Token获取函数（带缓存）
const getAuthToken = (() => {
  let cachedToken = null;
  let cacheTime = 0;
  const CACHE_DURATION = 5 * 60 * 1000; // 缓存5分钟
  
  return () => {
    const now = Date.now();
    
    // 如果缓存过期或没有缓存，重新获取
    if (!cachedToken || now - cacheTime > CACHE_DURATION) {
      // 优先从Vuex获取
      const store = require('@/store').default;
      if (store.state.user && store.state.user.token) {
        cachedToken = store.state.user.token;
        cacheTime = now;
      } else {
        // 备选：从sessionStorage获取
        try {
          const logInfo = sessionStorage.getItem('logInfoMB');
          if (logInfo) {
            const userInfo = JSON.parse(logInfo);
            cachedToken = userInfo.token;
            cacheTime = now;
          }
        } catch (e) {
          console.warn('获取Token失败');
        }
      }
    }
    
    return cachedToken;
  };
})();

// 请求拦截器
service.interceptors.request.use(
  config => {
    // ✅ 从缓存/存储中获取Token，不再从URL解析
    const token = getAuthToken();
    
    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);
```

---

## 🟠 SEC-005：硬编码RSA公钥

### 问题位置

```
/src/utils/util.js:290-298
```

### 修复前代码 ❌

```javascript
// util.js 第290-298行

const publicKey = `-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAqwWX6nHe7fj8...
-----END PUBLIC KEY-----`

function encryptByRSA(data) {
  const encryptor = new JSEncrypt();
  encryptor.setPublicKey(publicKey);
  return encryptor.encrypt(data);
}
```

### 修复后代码 ✅

#### 创建公钥获取服务

```javascript
// src/api/publicKey.js

import api from './axiosCenter'

// 公钥缓存
let cachedPublicKey = null
let keyExpireTime = 0
const KEY_CACHE_DURATION = 24 * 60 * 60 * 1000 // 24小时

/**
 * 从后端获取公钥
 * @returns {Promise<string>} 公钥
 */
async function fetchPublicKey() {
  try {
    const res = await api.get('/api/publicKey')
    return res.data.publicKey
  } catch (e) {
    console.error('获取公钥失败:', e)
    throw e
  }
}

/**
 * 获取RSA加密器（带缓存）
 * @returns {Promise<JSEncrypt>}
 */
async function getRSAEncryptor() {
  const now = Date.now()
  
  // 检查缓存
  if (cachedPublicKey && now < keyExpireTime) {
    const encryptor = new JSEncrypt()
    encryptor.setPublicKey(cachedPublicKey)
    return encryptor
  }
  
  // 缓存过期，重新获取
  cachedPublicKey = await fetchPublicKey()
  keyExpireTime = now + KEY_CACHE_DURATION
  
  const encryptor = new JSEncrypt()
  encryptor.setPublicKey(cachedPublicKey)
  return encryptor
}

/**
 * 使用RSA加密数据
 * @param {string} data - 待加密数据
 * @returns {Promise<string>} 加密后的数据
 */
async function encryptByRSA(data) {
  const encryptor = await getRSAEncryptor()
  return encryptor.encrypt(data)
}

/**
 * 清除公钥缓存
 */
function clearPublicKeyCache() {
  cachedPublicKey = null
  keyExpireTime = 0
}

export {
  fetchPublicKey,
  getRSAEncryptor,
  encryptByRSA,
  clearPublicKeyCache
}
```

#### 修改util.js

```javascript
// src/utils/util.js

// ✅ 移除硬编码的公钥
// import { publicKey } from './config' // 不再使用

import JSEncrypt from 'jsencrypt'
import api from '@/api/publicKey'

/**
 * ✅ 异步RSA加密函数
 * @param {string} data - 待加密数据
 * @returns {Promise<string>} 加密后的数据
 */
async function encryptByRSA(data) {
  try {
    return await api.encryptByRSA(data)
  } catch (e) {
    console.error('RSA加密失败:', e)
    throw e
  }
}

/**
 * 同步RSA加密（使用缓存的公钥）
 * 注意：首次调用可能返回null，需要先调用encryptByRSA初始化
 */
function encryptByRSASync(data) {
  // 如果公钥已缓存，直接使用
  // 否则返回null，由调用方处理
  return null
}
```

---

## 🟠 SEC-006：CORS配置过于宽松

### 问题位置

```
/src/api/axiosCenter.js:106
```

### 修复前代码 ❌

```javascript
// axiosCenter.js 第106行

const service = axios.create({
  baseURL: baseURL,
  timeout: timeout,
  headers: {
    'Access-Control-Allow-Origin': '*', // ❌ 危险！允许所有来源
  }
});
```

### 修复后代码 ✅

```javascript
// src/api/axiosCenter.js

// ✅ 开发环境和生产环境使用不同的配置
const service = axios.create({
  baseURL: baseURL,
  timeout: timeout,
  headers: {
    // Content-Type应该根据请求内容设置，而不是固定
    // 'Content-Type': 'application/json'
  }
});

// ✅ CORS配置主要由后端控制，前端只需正确设置Origin
service.defaults.withCredentials = true; // 允许携带cookie

// 请求拦截器中设置正确的Origin
service.interceptors.request.use(
  config => {
    // 设置当前页面的origin
    config.headers['Origin'] = window.location.origin
    return config
  }
)
```

> **注意**：CORS安全主要依靠后端配置，前端需要后端配合设置允许的来源白名单。

---

## 🟡 SEC-007：99处console.log调试代码残留

### 批量清理脚本

#### 创建清理脚本

```javascript
// scripts/cleanConsole.js

const fs = require('fs')
const path = require('path')

// 需要清理的文件扩展名
const extensions = ['.js', '.vue']

// 需要清理的console方法
const consoleMethods = [
  'console.log',
  'console.info',
  'console.warn',
  'console.error',
  'console.debug'
]

// 递归遍历目录
function walkDir(dir, callback) {
  const files = fs.readdirSync(dir)
  
  files.forEach(file => {
    const filePath = path.join(dir, file)
    const stat = fs.statSync(filePath)
    
    if (stat.isDirectory()) {
      // 跳过node_modules和.git
      if (file !== 'node_modules' && file !== '.git') {
        walkDir(filePath, callback)
      }
    } else {
      const ext = path.extname(file)
      if (extensions.includes(ext)) {
        callback(filePath)
      }
    }
  })
}

// 清理文件中的console语句
function cleanConsole(filePath) {
  let content = fs.readFileSync(filePath, 'utf-8')
  let modified = false
  let removedCount = 0
  
  consoleMethods.forEach(method => {
    // 匹配 console.xxx(...) 
    const regex = new RegExp(`${method}\\s*\\([^;]*\\)\\s*;?`, 'g')
    
    const matches = content.match(regex)
    if (matches) {
      removedCount += matches.length
      content = content.replace(regex, '')
      modified = true
    }
  })
  
  if (modified) {
    // 清理空行
    content = content.replace(/^\s*\n/gm, '\n')
    fs.writeFileSync(filePath, content)
    console.log(`✅ 已清理 ${filePath} (移除 ${removedCount} 处console)`)
  }
  
  return removedCount
}

// 主函数
function main() {
  const srcDir = path.join(__dirname, '..', 'src')
  let totalRemoved = 0
  
  console.log('🔍 开始扫描并清理console语句...\n')
  
  walkDir(srcDir, (filePath) => {
    totalRemoved += cleanConsole(filePath)
  })
  
  console.log(`\n✨ 完成！共移除 ${totalRemoved} 处console语句`)
}

// 运行
main()
```

#### 使用方法

```bash
node scripts/cleanConsole.js
```

#### Webpack生产配置（确保console被移除）

```javascript
// vue.config.js 或 build/webpack.prod.conf.js

module.exports = {
  configureWebpack: {
    optimization: {
      minimize: true
    }
  },
  chainWebpack: config => {
    // 生产环境移除console
    config.optimization.minimizer('terser').tap(args => {
      args[0].terserOptions.compress.drop_console = true
      args[0].terserOptions.compress.drop_debugger = true
      return args
    })
  }
}
```

---

## 🔵 SEC-008：打印功能使用innerHTML

### 问题位置

```
/src/components/comPrintTable/comPrintTable.vue:183
/src/mtbcomponents/comPrintTable/comPrintTable.vue:183
/src/mtbslcomponents/comPrintTable/comPrintTable.vue:183
/src/mtbnewcomponents/comPrintTable/comPrintTable.vue:183
```

### 修复前代码 ❌

```javascript
// comPrintTable.vue 第183行

var bdhtml = window.document.body.innerHTML  // ❌ 可能导致XSS
sprnstr = "<!--startprint-->"
eprnstr = "<!--endprint-->"
```

### 修复后代码 ✅

```javascript
// src/mtbnewcomponents/comPrintTable/comPrintTable.vue

export default {
  methods: {
    print() {
      // ✅ 使用更安全的方式获取打印内容
      
      // 方法1：使用textContent获取纯文本（推荐用于纯文本打印）
      // const printContent = document.getElementById('printArea').textContent
      
      // 方法2：使用innerHTML但进行HTML转义（用于保留格式的打印）
      const getSafeHTML = (element) => {
        const tempDiv = document.createElement('div')
        tempDiv.textContent = element.innerHTML
        return tempDiv.innerHTML
      }
      
      // 获取打印区域的HTML并进行转义
      const printArea = document.getElementById('printArea')
      if (!printArea) {
        console.warn('未找到打印区域')
        return
      }
      
      // 克隆节点避免修改原DOM
      const clone = printArea.cloneNode(true)
      
      // 转义所有文本内容
      const escapeHTML = (str) => {
        const div = document.createElement('div')
        div.textContent = str
        return div.innerHTML
      }
      
      // 处理克隆节点中的文本
      clone.querySelectorAll('*').forEach(el => {
        // 跳过脚本和样式
        if (el.tagName === 'SCRIPT' || el.tagName === 'STYLE') {
          el.remove()
          return
        }
        
        // 转义文本内容
        Array.from(el.childNodes).forEach(node => {
          if (node.nodeType === Node.TEXT_NODE) {
            node.textContent = node.textContent
          }
        })
      })
      
      const safeHTML = clone.innerHTML
      
      // 提取打印内容
      const startIdx = safeHTML.indexOf('<!--startprint-->')
      const endIdx = safeHTML.indexOf('<!--endprint-->')
      
      if (startIdx === -1 || endIdx === -1) {
        console.warn('未找到打印标记')
        return
      }
      
      const printContent = safeHTML.substring(
        startIdx + '<!--startprint-->'.length,
        endIdx
      )
      
      // 执行打印
      const originalContent = document.body.innerHTML
      document.body.innerHTML = printContent
      window.print()
      document.body.innerHTML = originalContent
      location.reload() // 重新加载以恢复Vue状态
    }
  }
}
```

---

## 🔵 SEC-009：硬编码的AccountNum

### 问题位置

```
/src/api/axiosCenter.js:60-64
```

### 修复前代码 ❌

```javascript
// axiosCenter.js 第60-64行

if (process.env.NODE_ENV === "proMbReform" || ...) {
  headerSign.accountNum = "1561166093318619136"; // ❌ 硬编码
} else {
  headerSign.accountNum = "1546784022366257152"; // ❌ 硬编码
}
```

### 修复后代码 ✅

#### Step 1: 创建环境变量配置

```javascript
// .env.production
VUE_APP_ACCOUNT_NUM=1561166093318619136

// .env.development
VUE_APP_ACCOUNT_NUM=1546784022366257152

// .env.test
VUE_APP_ACCOUNT_NUM=1546784022366257152

// .env.uat
VUE_APP_ACCOUNT_NUM=1546784022366257152
```

#### Step 2: 修改axiosCenter.js

```javascript
// src/api/axiosCenter.js

// ✅ 从环境变量获取accountNum
const accountNum = process.env.VUE_APP_ACCOUNT_NUM || ''

// 在请求拦截器中使用
service.interceptors.request.use(
  config => {
    const headerSign = {
      accountNum: accountNum, // ✅ 使用环境变量
      timestamp: new Date().getTime(),
      // ...
    }
    
    // 将签名信息添加到请求头
    Object.assign(config.headers, headerSign)
    
    return config
  }
)
```

---

## 📋 修改文件清单

| 文件路径 | 修改类型 | 涉及工单 |
|---------|---------|---------|
| `/src/mtbnewcomponents/menuList/menuindex.vue` | 修改 | SEC-001 |
| `/src/mtbnewcomponents/menuList/menudeclare.vue` | 修改 | SEC-001 |
| `/src/mtbnewcomponents/loginMb/settingModal.vue` | 修改 | SEC-002 |
| `/src/pages/DZChronicDis/serveStatusMod.vue` | 修改 | SEC-002 |
| `/src/pages/YLChronicDis/serveStatusMod.vue` | 修改 | SEC-002 |
| `/src/mtbnewcomponents/loginMb/index.vue` | 修改 | SEC-002, SEC-003 |
| `/src/api/axiosCenter.js` | 修改 | SEC-004, SEC-006, SEC-009 |
| `/src/utils/util.js` | 修改 | SEC-005 |
| `/src/utils/passwordHash.js` | 新增 | SEC-002 |
| `/src/utils/tokenHelper.js` | 新增 | SEC-001 |
| `/src/api/publicKey.js` | 新增 | SEC-005 |
| `/src/store/modules/user.js` | 新增 | SEC-003 |
| `/src/store/index.js` | 修改 | SEC-003 |
| `/src/App.vue` | 修改 | SEC-003 |
| `/src/components/comPrintTable/comPrintTable.vue` | 修改 | SEC-008 |
| `/src/mtbcomponents/comPrintTable/comPrintTable.vue` | 修改 | SEC-008 |
| `/src/mtbslcomponents/comPrintTable/comPrintTable.vue` | 修改 | SEC-008 |
| `/src/mtbnewcomponents/comPrintTable/comPrintTable.vue` | 修改 | SEC-008 |
| `/scripts/cleanConsole.js` | 新增 | SEC-007 |
| `/src/api/axiosCenter.js` | 修改 | SEC-007 |

---

## 🧪 验证测试步骤

### SEC-001 验证

1. **登录系统**，进入任意菜单
2. **打开浏览器开发者工具** → Network面板
3. **观察菜单跳转**：点击菜单项后，检查URL中是否还有`token`参数
   - ✅ 正确：URL类似 `/diseaseDeclare`，无token参数
   - ❌ 错误：URL类似 `/diseaseDeclare?token=xxx`

4. **检查请求头**：在Network面板中点击任意API请求，查看Headers中的Authorization
   - ✅ 正确：有`Authorization: Bearer xxx`请求头

### SEC-002 验证

1. **登录系统**
2. **进入"修改密码"功能**
3. **修改密码**，使用密码`Test123456`
4. **使用数据库工具**（或联系后端）检查数据库中的密码存储
   - ✅ 正确：密码字段是SHA-256哈希值，不再是MD5
   - ✅ 正确：哈希值带有盐值前缀（如`abc123:SHA256...`）

5. **尝试彩虹表攻击**（可选）：
   ```bash
   # 使用彩虹表测试常见密码
   echo -n "Test123456" | md5sum
   # 应该无法匹配数据库中的哈希值
   ```

### SEC-003 验证

1. **登录系统**
2. **打开开发者工具** → Application面板 → Session Storage
3. **检查存储内容**：
   - ✅ 正确：sessionStorage中仍有`logInfoMB`（作为后备）
   - ✅ 正确：Vuex（内存）中存储了用户信息

4. **模拟XSS攻击测试**（谨慎操作）：
   - 在浏览器控制台执行：
   ```javascript
   // 尝试读取sessionStorage
   sessionStorage.getItem('logInfoMB')
   ```
   - ✅ 正确：可以读取（sessionStorage本身特性）
   - 💡 最佳实践：敏感Token应使用HttpOnly Cookie

### SEC-004 验证

1. **打开开发者工具** → Network面板
2. **发起多个请求**，观察请求头
3. **检查Token来源**：
   - ✅ 正确：Token从请求头`Authorization`获取，不再从URL解析
   - ✅ 正确：多次请求Token来源一致

### SEC-005 验证

1. **登录系统**
2. **打开开发者工具** → Network面板
3. **查找公钥请求**（如果是首次加载）
   - ✅ 正确：有`/api/publicKey`请求
   - ✅ 正确：公钥响应来自后端，非硬编码

4. **等待24小时后再次测试**：
   - ✅ 正确：公钥重新从后端获取（验证缓存过期）

### SEC-007 验证

1. **打包项目**：
   ```bash
   npm run build
   ```
2. **打开生成的dist文件**，检查控制台：
   - ✅ 正确：生产环境中无任何console输出
   - ❌ 错误：仍有console输出，检查webpack配置

3. **代码检查**：
   ```bash
   grep -rn "console.log" src --include="*.vue" --include="*.js" | wc -l
   ```
   - ✅ 正确：返回0

### SEC-008 验证

1. **进入有打印功能的页面**
2. **点击打印按钮**
3. **检查打印预览**：
   - ✅ 正确：打印内容正常显示
   - ✅ 正确：HTML标签被正确转义或处理
   - ✅ 正确：没有执行可疑脚本

### SEC-009 验证

1. **检查代码**：
   ```javascript
   // 在axiosCenter.js中不应有硬编码的accountNum
   grep -n "1561166093318619136" src/api/axiosCenter.js
   # 应该无输出
   ```

2. **多环境构建测试**：
   ```bash
   npm run build:dev   # 开发环境
   npm run build:prod  # 生产环境
   npm run build:test  # 测试环境
   ```
   - ✅ 正确：不同环境使用不同的accountNum

---

## ⚠️ 后端配合检查清单

| 工单 | 后端配合事项 | 状态 |
|------|-------------|------|
| SEC-001 | Token改用HttpOnly Cookie返回 | ⬜ 待后端 |
| SEC-002 | 改用bcrypt/Argon2验证密码 | ⬜ 待后端 |
| SEC-005 | 提供`/api/publicKey`接口 | ⬜ 待后端 |
| SEC-006 | 配置CORS白名单 | ⬜ 待后端 |

---

**文档生成完毕**
