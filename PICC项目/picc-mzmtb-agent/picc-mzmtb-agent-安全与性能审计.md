> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC门诊慢特病前端项目（picc-mzmtb-agent）
# 安全与代码质量+性能审计报告

> 审计日期：2024年
> 项目规模：652个Vue文件、74个API文件、21个地市模块
> 技术栈：Vue 2.6 + Vuex + Vue Router + Axios + Ant Design Vue

---

## 📋 审计结果总览

| 审计维度 | 问题数量 | 风险等级 |
|---------|---------|---------|
| 🔴 安全问题 | 8项 | 2高危、4中危、2低危 |
| 🟡 代码质量问题 | 6项 | 中等 |
| 🟠 性能问题 | 5项 | 中等 |
| 🟢 优点 | 4项 | - |

**综合评价**：项目整体架构清晰，但存在部分安全风险和代码质量问题需要关注，建议按优先级修复。

---

## 🔴 一、安全审计（8项问题）

### 【高危-1】Token通过URL参数传递

**问题描述**  
系统登录后，用户Token（相当于"身份证"）通过URL的query参数明文传递，这是一个严重的安全漏洞。

**问题位置**
```
/src/mtbnewcomponents/menuList/menuindex.vue:87
/src/mtbnewcomponents/menuList/menudeclare.vue:86
```
代码示例：
```javascript
path: `/${key}`,query:{token:list.token}
```

**🔍 小白解释**  
就像把家门钥匙写在信封外面寄信一样，URL参数会被浏览器历史记录、服务器日志、Referer头等地方记录，容易被窃取。

**风险影响**  
- 攻击者可以通过浏览器历史记录获取用户Token
- 服务器日志会记录完整的URL，Token泄露
- Token可能出现在 Referer 头中泄露给第三方

**学习要点**
```javascript
// 🔍 当前实现分析 - URL传递Token
path: `/${key}`,query:{token:list.token}

// 📖 规范写法参考（仅供学习对比） - 使用Cookie或SessionStorage
// 1. 使用 HttpOnly Cookie（后端配合）
// 2. 或使用 SessionStorage + 内存状态
path: `/${key}`
// 然后在路由守卫或请求拦截器中从sessionStorage读取Token
```

**学习要点**  
需要后端将Token改为通过 `Set-Cookie` 的 `HttpOnly` 方式返回，前端通过Cookie自动携带。

---

### 【高危-2】MD5密码哈希不安全

**问题描述**  
项目使用 MD5 算法对用户密码进行哈希处理，但MD5已被证明不安全。

**问题位置**
```
/src/mtbnewcomponents/loginMb/settingModal.vue:114
/src/pages/DZChronicDis/serveStatusMod.vue:418
/src/pages/YLChronicDis/serveStatusMod.vue:418
```

代码示例：
```javascript
password: md5(values.password)  // MD5不安全
```

**🔍 小白解释**  
MD5就像用一把简单的锁来保护保险箱，虽然能上锁，但小偷可以用现成的工具快速破解开锁。目前MD5已被密码学界认定不安全。

**风险影响**  
- MD5彩虹表攻击可以在秒级破解常见密码
- 如果数据库泄露，用户密码可被还原
- 不符合等保三级要求的密码存储标准

**学习要点**
```javascript
// 🔍 当前实现分析
password: md5(values.password)

// 📖 规范写法参考（仅供学习对比） - 使用bcrypt或Argon2
// 前端：使用Web Crypto API或crypto-js的SHA-256
import sha256 from 'crypto-js/sha256';

// 或在后端使用bcrypt
password: sha256(values.password + salt)  // 加盐哈希
```

**最佳实践**  
1. 前端传输密码使用HTTPS加密
2. 后端使用 bcrypt/Argon2 做密码哈希
3. 添加随机盐值防止彩虹表攻击

---

### 【中危-1】Token从URL重复解析

**问题描述**  
在axiosCenter.js的请求拦截器中，每次发起请求都会从URL解析Token，而不是从store或sessionStorage缓存读取。

**问题位置**
```
/src/api/axiosCenter.js:45-52
```

代码示例：
```javascript
// 每次请求都重新解析URL
let query = location.href.split('?')[1];
token = qs.parse(query, { ignoreQueryPrefix: true })["token"];
```

**🔍 小白解释**  
就像每次买东西都要重新去银行查余额，而不是用之前取好的钱，效率低且增加Token泄露风险。

**问题分析**
```javascript
// 📖 规范写法参考（仅供学习对比） - 从sessionStorage读取并缓存
const getToken = (() => {
  let cachedToken = null;
  return () => {
    if (!cachedToken) {
      let logInfo = sessionStorage.getItem("logInfoMB");
      if (logInfo) {
        cachedToken = JSON.parse(logInfo).token;
      }
    }
    return cachedToken;
  };
})();

// 在拦截器中使用
token = getToken();
```

---

### 【中危-2】敏感数据存储在sessionStorage

**问题描述**  
用户登录信息和Token存储在sessionStorage中，存在XSS攻击窃取风险。

**问题位置**
```
/src/mtbnewcomponents/loginMb/index.vue:177
// 存储用户信息
window.sessionStorage.setItem("logInfoMB", logInfoMB);
```

**🔍 小白解释**  
SessionStorage就像放在桌上的便签，如果网站存在XSS漏洞，恶意脚本可以读取并发送给攻击者。

**问题分析**
```javascript
// ✅ 敏感数据应存储在内存中，而非持久化存储
// Vuex store中存储，组件销毁后自动清除

// ❌ 不推荐 - sessionStorage存储
window.sessionStorage.setItem("logInfoMB", logInfoMB);

// ✅ 推荐 - 仅在内存中存储
// Vuex store state
state: {
  userInfo: null,
  token: null
}

// 刷新页面通过接口重新获取
```

---

### 【中危-3】硬编码的RSA公钥

**问题描述**  
在util.js中硬编码了RSA公钥，如果公钥泄露可能影响加密安全。

**问题位置**
```
/src/utils/util.js:290-298
```

代码示例：
```javascript
const publicKey=`-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAqwWX6nHe7fj8...
-----END PUBLIC KEY-----`
```

**🔍 小白解释**  
公钥虽然叫"公"钥，但硬编码在前端代码中仍然不够安全。更好的做法是从后端接口动态获取。

**风险等级**  
中危 - 公钥本身可公开使用，但如果需要轮换密钥，硬编码会导致更新困难。

**问题分析**
```javascript
// ✅ 从后端接口获取公钥
async function getPublicKey() {
  const res = await api.getPublicKey(); // 后端接口
  return res.data.publicKey;
}

// 缓存公钥，最多缓存24小时
let cachedPublicKey = null;
let keyExpireTime = 0;

async function getRsaEncryptor() {
  const now = Date.now();
  if (!cachedPublicKey || now > keyExpireTime) {
    cachedPublicKey = await getPublicKey();
    keyExpireTime = now + 24 * 60 * 60 * 1000; // 24小时后过期
  }
  const encryptor = new JSEncrypt();
  encryptor.setPublicKey(cachedPublicKey);
  return encryptor;
}
```

---

### 【中危-4】CORS配置过于宽松

**问题描述**  
Axios请求配置中允许所有来源的跨域请求。

**问题位置**
```
/src/api/axiosCenter.js:106
```

代码示例：
```javascript
headers: {
  'Access-Control-Allow-Origin': '*',  // 允许所有来源
}
```

**🔍 小白解释**  
这就像餐厅不检查身份证就让任何人进入，可能导致恶意网站调用你的接口。

**说明**  
这个配置主要是后端生效，前端设置仅供参考。不过前后端都需要注意CORS安全。

**学习要点**
后端应配置具体的允许来源列表，不使用通配符 `*`。

---

### 【低危-1】打印功能使用innerHTML

**问题描述**  
多处使用innerHTML进行打印内容处理，存在潜在的XSS风险。

**问题位置**
```
/src/components/comPrintTable/comPrintTable.vue:183
/src/mtbcomponents/comPrintTable/comPrintTable.vue:183
/src/mtbslcomponents/comPrintTable/comPrintTable.vue:183
/src/mtbnewcomponents/comPrintTable/comPrintTable.vue:183
```

代码示例：
```javascript
var bdhtml = window.document.body.innerHTML
```

**🔍 小白解释**  
innerHTML会将HTML字符串直接插入页面，如果内容来自用户输入且未过滤，可能执行恶意脚本。

**风险评估**  
低危 - 打印内容通常来自系统生成，不太可能是用户可控的恶意代码。但仍建议使用更安全的方式。

**问题分析**
```javascript
// ✅ 使用textContent替代innerHTML
var bdhtml = window.document.body.textContent;

// 或使用更安全的DOM操作
const printContent = document.createElement('div');
printContent.textContent = originalContent;
```

---

### 【低危-2】硬编码的AccountNum

**问题描述**  
在请求头中硬编码了accountNum账号标识。

**问题位置**
```
/src/api/axiosCenter.js:60-64
```

代码示例：
```javascript
if (process.env.NODE_ENV === "proMbReform" || ...) {
  headerSign.accountNum = "1561166093318619136";
} else {
  headerSign.accountNum = "1546784022366257152";
}
```

**🔍 小白解释**  
硬编码的账号ID虽然不直接泄露密钥，但可能帮助攻击者识别系统版本和配置。

**学习要点**
建议将这些标识符移到环境变量配置文件中，不直接写在代码里。

---

## 🟡 二、代码质量审计（6项问题）

### 【中等-1】99处console.log残留

**问题描述**  
代码中存在99处console.log、console.warn、console.error调试代码未清理。

**示例位置**
```
/src/mtbnewcomponents/recordImport/recordImport.vue:200
/src/pages/YLChronicDis/webUserManage.vue:354
/src/pages/YLChronicDis/proficientManage.vue:214
```

**🔍 小白解释**  
就像装修完房子还留着施工梯，虽然不影响使用，但既不专业也可能泄露调试信息。

**影响**
- 生产环境暴露调试信息
- 可能打印敏感业务数据
- 影响控制台可读性

**问题分析**
```bash
# 使用正则批量搜索并清理
grep -rn "console.log\|console.warn\|console.error" src --include="*.vue" --include="*.js"
```

或在生产构建时自动移除（webpack已配置，但需确认生效）：
```javascript
// webpack.prod.conf.js
new UglifyJsPlugin({
  uglifyOptions: {
    compress: {
      drop_console: true,  // 确认生产环境生效
    }
  }
})
```

---

### 【中等-2】21个超大组件（500行以上）

**问题描述**  
项目存在21个超过500行的Vue组件，其中最大的超过2400行。

**TOP10大组件**
| 文件 | 行数 | 建议 |
|-----|------|------|
| searchCard/index.vue | 2448 | 拆分为多个小组件 |
| diseaseOfflineDeclare.vue | 1945 | 按功能拆分 |
| editUserInformationBJ.vue | 1680 | 拆分为表单、列表、详情等 |
| editUserInformationYL.vue | 1547 | 拆分为多个模块 |
| comSelect/comSelect.vue | 1287 | 抽取通用逻辑 |

**🔍 小白解释**  
就像一本没有目录的字典，查一个字要看完全本书。大组件难维护、难测试、易出错。

**问题分析**
```
# 建议的组件拆分策略

# 1. 按功能拆分
LargeComponent.vue (1500行)
├── form/
│   ├── BasicForm.vue      (表单基础)
│   ├── AddressForm.vue    (地址表单)
│   └── FileUploadForm.vue (文件上传)
├── table/
│   ├── DataTable.vue      (数据表格)
│   └── Pagination.vue     (分页器)
└── modals/
    ├── EditModal.vue      (编辑弹窗)
    └── ConfirmModal.vue   (确认弹窗)

# 2. 使用Vue Mixins复用逻辑
# 3. 使用Vue 3 Composition API (可选升级)
```

---

### 【中等-3】14个地市模块大量重复代码

**问题描述**  
项目有14个 `*ChronicDis` 目录（地市模块），存在大量重复的组件和代码。

**重复模块列表**
```
DZChronicDis  (定州)
JiJChronicDis (冀州)
YLChronicDis  (玉林)
XYaChronicDis (信阳)
ChronicDis     (通用)
ZJKChronicDis (张家口)
DIZChronicDis (定州另一个版本)
YAChronicDis  (延安)
JCChronicDis  (晋城)
MZLChronicDis (梅州)
YaLChronicDis (牙克石)
NewChronicDis (新版)
JZChronicDis  (锦州)
SLChronicDis  (商洛)
```

**🔍 小白解释**  
就像14个城市都建了相同的医院，每个医院都要单独维护，浪费资源且容易出错。

**问题分析**
```javascript
// 1. 建立统一的组件库
/src/components/common/  // 通用组件
/src/components/mtbnewcomponents/  // 新版通用组件

// 2. 地市差异化通过配置实现
// 配置文件
city-config/
├── base-config.js      // 基础配置
├── dzh-config.js       // 定州配置
├── yl-config.js        // 玉林配置
└── ...

// 3. 使用Vue Router的meta配置地市差异化
{
  path: '/diseaseDeclare',
  component: DiseaseDeclare,
  meta: {
    cityCode: 'DZH',
    features: ['import', 'export', 'audit']
  }
}
```

---

### 【中等-4】Props类型校验不完善

**问题描述**  
部分组件使用了props但缺乏完整的类型校验和默认值设置。

**示例**
```javascript
// 大部分组件的props格式
props: {
  tableTitle: {
    type: String,
    default: ""
  },
  // 但很多复杂类型的props没有校验
  dataSource: Array,  // 缺少default
  onChange: Function,  // 缺少required标记
}
```

**🔍 小白解释**  
Props就像函数的参数说明，没有类型校验就像参数表写"某种东西"，调用者可能传错类型导致bug。

**问题分析**
```javascript
// ✅ 完整的props定义
props: {
  // 必填的简单类型
  recordId: {
    type: [String, Number],
    required: true
  },
  
  // 可选的有默认值
  tableData: {
    type: Array,
    default: () => []  // 数组默认值必须用函数返回
  },
  
  // 带验证器
  status: {
    type: String,
    default: 'pending',
    validator: (value) => ['pending', 'approved', 'rejected'].includes(value)
  },
  
  // 对象类型
  config: {
    type: Object,
    default: () => ({})
  }
}
```

---

### 【中等-5】定时器清理不一致

**问题描述**  
部分组件使用了setTimeout但未在beforeDestroy中清理，可能导致内存泄漏。

**问题组件**
```
/src/pages/JiJChronicDis/declarationInformation.vue (部分清理)
/src/pages/JiJChronicDis/auditManagement.vue (部分清理)
/src/pages/YLChronicDis/auditManagement.vue (部分清理)
/src/pages/XYaChronicDis/declarationInformation.vue (部分清理)
```

**示例代码**
```javascript
// 有些组件有清理
beforeDestroy() {
  clearTimeout(this.timer);
}

// 但很多组件没有
```

**🔍 小白解释**  
定时器就像闹钟，如果页面关闭时不关掉，闹钟还会响（占用内存），而且可能执行页面已经销毁的逻辑导致报错。

**问题分析**
```javascript
export default {
  data() {
    return {
      timer: null,
      intervalId: null
    }
  },
  
  methods: {
    startPolling() {
      // 使用class属性存储定时器ID
      this.timer = setTimeout(() => {
        this.fetchData();
        this.startPolling(); // 递归实现轮询
      }, 5000);
    }
  },
  
  beforeDestroy() {
    // ✅ 清理定时器
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }
}
```

---

### 【中等-6】未发现虚拟滚动实现

**问题描述**  
项目未使用虚拟滚动技术来处理大数据列表，当数据量大时可能造成性能问题。

**🔍 小白解释**  
虚拟滚动就像只渲染可见的书页，而不是把整本书都印出来。不使用虚拟滚动，长列表会卡顿。

**影响范围**  
- 申报查询列表（可能数千条数据）
- 历史记录列表
- 用户列表

**问题分析**
```javascript
// 方案1: 使用 vue-virtual-scroller
import RecycleScroller from 'vue-virtual-scroller';
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css';

<RecycleScroller
  class="scroller"
  :items="dataList"
  :item-size="50"
  key-field="id"
>
  <template v-slot="{ item }">
    <ListItem :item="item" />
  </template>
</RecycleScroller>

// 方案2: 使用 ant-design-vue 的 a-table
// 配置虚拟滚动
<a-table
  :data-source="dataList"
  :scroll="{ y: 500 }"
  :pagination="false"
/>
```

---

## 🟠 三、性能审计（5项问题）

### 【中等-1】未配置图片资源优化

**问题描述**  
未发现图片压缩、WebP转换、懒加载等优化配置。

**学习要点**
```javascript
// vue.config.js
module.exports = {
  chainWebpack: config => {
    // 图片压缩
    config.module
      .rule('images')
      .set('parser', {
        dataUrlCondition: {
          maxSize: 10 * 1024 // 小于10KB转base64
        }
      })
    
    // 开启WebP转换
    config.module
      .rule('images')
      .oneOf('webp')
      . ResourceQuery('?format=webp')
      ....
  }
}
```

---

### 【中等-2】未配置组件预加载

**问题描述**  
虽然使用了路由懒加载，但未配置预加载策略。

**当前代码**
```javascript
component: () => import("@/pages/Home")
```

**问题分析**
```javascript
// 方案1: 预加载下一个页面
// router/index.js
const router = createRouter();

// 预加载逻辑
const preloadRoute = () => {
  const currentPath = router.currentRoute.path;
  const routes = router.getRoutes();
  // 预加载相邻或热门页面
};

// 空闲时预加载
if ('requestIdleCallback' in window) {
  requestIdleCallback(preloadRoute);
} else {
  setTimeout(preloadRoute, 1000);
}

// 方案2: Webpack magic comments
component: () => import(/* webpackChunkName: "home" */ "@/pages/Home")

// 方案3: 预加载指定组件
const { ComponentA } = require('./components');
// 业务需要时提前加载
```

---

### 【中等-3】lodash未按需引入

**问题描述**  
使用了完整版lodash，增加包体积。

**当前引入**
```javascript
import _ from 'lodash';  // 完整包 ~70KB
_.debounce()
```

**问题分析**
```javascript
// ✅ 按需引入
import debounce from 'lodash/debounce';  // ~2KB
import cloneDeep from 'lodash/cloneDeep'; // ~5KB

// 或使用原生实现简单功能
const debounce = (fn, delay) => {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
};
```

---

### 【中等-4】Vue 2未升级到最新补丁版本

**问题描述**  
项目使用Vue 2.6.11，可能存在已修复的安全问题和性能优化。

**当前版本**
```json
"vue": "^2.6.11"
```

**建议升级**
```json
// package.json
"vue": "^2.6.14"  // Vue 2最新稳定版

// 同时更新相关依赖
"vue-template-compiler": "^2.6.14",
"vue-router": "^3.5.3",
"vuex": "^3.6.2"
```

---

### 【中等-5】axios版本较旧

**问题描述**  
使用axios 0.19.2，存在已知的安全漏洞和功能限制。

**当前版本**
```json
"axios": "^0.19.2"
```

**建议升级**
```json
// 升级到1.x版本或至少1.6.x
"axios": "^1.6.0"

// 新版本改进：
// - 更好的TypeScript支持
// - 拦截器优化
// - 安全性修复
```

---

## 🟢 四、项目亮点（4项）

### ✅ 亮点1：路由守卫完善

项目在路由守卫中实现了基本的登录验证：
```javascript
router.beforeEach((to, from, next) => {
  let logInfoMB = util.getUserInfo();
  if (!logInfoMB) {
    if (to.path == '/loginMb' || to.path == '/resetConfirm') {
      next();
    } else {
      next('/loginMb');  // 未登录重定向
    }
  } else {
    next();
  }
});
```

---

### ✅ 亮点2：支持多环境构建

项目配置了dev、test、uat、production等多个环境：
```json
"scripts": {
  "dev": "node build/build.js dev",
  "test": "node build/build.js test",
  "uat": "node build/build.js uat",
  "production": "node build/build.js production"
}
```

---

### ✅ 亮点3：Webpack生产构建配置完善

```javascript
// webpack.prod.conf.js
new UglifyJsPlugin({
  uglifyOptions: {
    compress: {
      drop_debugger: true,
      drop_console: true  // 自动移除console
    }
  }
})

// 代码分割配置
splitChunks: {
  cacheGroups: {
    vendor: {
      test: /[\\/]node_modules[\\/]/,
      name: 'vendor',
      chunks: 'all'
    }
  }
}
```

---

### ✅ 亮点4：使用Vuex持久化状态

```javascript
// vuex-persistedstate
const createPersisted = createPersistedState({
  storage: window.sessionStorage,
})
```

---

## 📊 五、与后端项目对比分析

根据后端三项目的67个安全问题，前端可能存在的**同类问题**：

| 后端问题类型 | 前端是否存在 | 说明 |
|------------|-------------|------|
| SQL注入 | ❌ | 前端无直接SQL操作 |
| XSS跨站脚本 | ⚠️ | 存在innerHTML使用，需注意 |
| CSRF攻击 | ⚠️ | Token管理方式需改进 |
| 敏感信息泄露 | ⚠️ | URL传参问题需修复 |
| 密码存储 | ⚠️ | MD5问题需升级 |
| 权限控制 | ✅ | 路由守卫已实现 |
| API安全 | ⚠️ | 签名机制需加强 |

---

## 📋 六、修复优先级建议

### 🔥 P0 - 立即修复（高危）
1. **Token URL传递问题** - 必须修复，改为Cookie或安全存储
2. **MD5密码哈希** - 升级为bcrypt或SHA-256+盐

### ⚡ P1 - 本周修复（中危）
3. **sessionStorage敏感数据** - 改为内存存储
4. **RSA公钥硬编码** - 改为后端接口获取
5. **console.log残留** - 批量清理

### 📅 P2 - 下月规划（中等）
6. **大组件拆分** - 优先拆分超过1000行的组件
7. **地市模块重构** - 抽取公共组件
8. **定时器清理** - 统一清理规范
9. **依赖升级** - Vue、axios升级

---

## 📝 七、附录

### A. 文件清单（需重点关注的文件）

| 文件路径 | 问题类型 |
|---------|---------|
| `/src/api/axiosCenter.js` | Token管理、CORS配置 |
| `/src/mtbnewcomponents/loginMb/index.vue` | 登录Token处理 |
| `/src/mtbnewcomponents/menuList/menuindex.vue` | URL传参Token |
| `/src/utils/util.js` | RSA公钥、加密函数 |
| `/src/router/index.js` | 路由守卫 |
| `/src/store/index.js` | 状态持久化 |

### B. 快速检查命令

```bash
# 检查敏感信息
grep -rn "password\|token\|secret" src --include="*.js" --include="*.vue" | grep -v "node_modules"

# 检查console残留
grep -rn "console.log" src --include="*.js" --include="*.vue" | wc -l

# 检查大文件
find src -name "*.vue" -exec wc -l {} \; | sort -rn | head -10

# 检查定时器清理
grep -rn "beforeDestroy" src/pages --include="*.vue" | wc -l
```

---

**报告生成时间**：2024年
**审计工具**：grep、find、静态代码分析
**审计覆盖范围**：652个Vue文件、74个API文件、关键配置文件
