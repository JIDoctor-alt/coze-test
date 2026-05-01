# PICC门诊慢特病前端项目（picc-mzmtb-agent）
# 安全问题原理学习文档

> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

> 文档生成日期：2024年
> 技术栈：Vue 2.6 + Vuex 3 + Axios + Ant Design Vue

---

## 📖 使用说明

本文档提供每个安全问题的**原理分析**，帮助理解安全问题的成因和影响。

---

## 🔴 SEC-001：Token通过URL参数明文传递

### 问题位置

```
/src/mtbnewcomponents/menuList/menuindex.vue:87
/src/mtbnewcomponents/menuList/menudeclare.vue:86
```

### 🔍 问题原理分析

📖 **学习理解**：Token 是用户的身份凭证，相当于"家门钥匙"。

**当前实现分析**：

```javascript
// menuindex.vue 第87行 - 当前实现
goPage(key) {
  let list = this.menuList[key]
  this.$router.push({
    path: `/${key}`,
    query: { token: list.token }  // ❌ Token明文在URL中
  })
}
```

**安全问题原理**：

1. **URL会被记录**：浏览器历史记录、服务器日志、代理日志都会记录URL
2. **URL会被泄露**：用户分享链接时，Token也跟着泄露了
3. **Token应该保密**：就像钥匙不能随便给人看一样

**安全影响**：
- 攻击者可以从浏览器历史记录获取Token
- 攻击者可以从服务器日志获取Token
- 用户分享链接时无意中泄露Token

---

## 🔴 SEC-002：使用不安全的MD5密码哈希

### 问题位置

```
/src/utils/util.js:45
```

### 🔍 问题原理分析

📖 **学习理解**：MD5是一种哈希算法，但已经不安全了。

**当前实现分析**：

```javascript
// util.js - 当前实现
import md5 from 'md5';

export function encryptPassword(password) {
  return md5(password);  // ❌ MD5已经不安全
}
```

**安全问题原理**：

1. **彩虹表攻击**：攻击者有预计算的MD5对照表，秒破解
2. **碰撞攻击**：不同密码可能产生相同的MD5值
3. **计算速度太快**：现代GPU每秒可以计算数十亿次MD5，暴力破解太容易

**安全影响**：
- 密码容易被破解
- 不符合现代安全标准
- 违反密码存储最佳实践

---

## 🟠 SEC-003：敏感数据存储在sessionStorage

### 问题位置

```
/src/mtbnewcomponents/loginMb/index.vue
```

### 🔍 问题原理分析

📖 **学习理解**：sessionStorage 是浏览器的临时存储，但并不安全。

**当前实现分析**：

```javascript
// loginMb/index.vue - 当前实现
// 登录成功后将用户信息存入sessionStorage
sessionStorage.setItem('logInfoMB', JSON.stringify(userInfo));
```

**安全问题原理**：

1. **XSS攻击**：如果网站存在XSS漏洞，攻击者可以读取sessionStorage
2. **浏览器存储不加密**：任何能访问页面的脚本都能读取
3. **开发者工具可见**：任何人打开开发者工具都能看到存储的内容

**安全影响**：
- 敏感数据可能被XSS攻击窃取
- 用户隐私信息泄露风险

---

## 🟠 SEC-004：Token从URL重复解析

### 问题位置

```
/src/api/axiosCenter.js
```

### 🔍 问题原理分析

📖 **学习理解**：每次请求都从URL解析Token是低效且不安全的做法。

**当前实现分析**：

```javascript
// axiosCenter.js - 当前实现
request.interceptors.request.use(config => {
  // 每次请求都从URL解析token
  const token = getTokenFromUrl();  // 低效操作
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});
```

**安全问题原理**：

1. **性能问题**：每次请求都要解析URL，浪费资源
2. **安全隐患**：URL中的Token容易被泄露
3. **代码复杂度**：需要在多个地方处理Token解析

**学习理解**：
- Token应该在登录后缓存，而不是每次都解析
- 更好的方案是使用 HttpOnly Cookie

---

## 🟠 SEC-005：硬编码RSA公钥

### 问题位置

```
/src/utils/util.js
```

### 🔍 问题原理分析

📖 **学习理解**：RSA公钥硬编码在代码中，难以维护和更换。

**当前实现分析**：

```javascript
// util.js - 当前实现
const RSA_PUBLIC_KEY = `-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----`;

export function encryptWithRSA(data) {
  // 使用硬编码的公钥加密
}
```

**安全问题原理**：

1. **难以更换**：如果要更换密钥，需要重新部署前端代码
2. **代码泄露风险**：公钥会随前端代码一起发布
3. **维护困难**：不同环境可能需要不同的密钥

**学习理解**：
- 密钥应该从配置中心或接口动态获取
- 这样可以实现密钥的统一管理和更换

---

## 🟠 SEC-006：CORS配置过于宽松

### 问题位置

```
/src/api/axiosCenter.js
```

### 🔍 问题原理分析

📖 **学习理解**：CORS（跨域资源共享）配置过于宽松会导致安全风险。

**安全问题原理**：

1. **跨域风险**：允许所有来源的跨域请求
2. **CSRF风险**：攻击者可以从其他网站发起恶意请求
3. **数据泄露**：敏感数据可能被恶意网站获取

**学习理解**：
- CORS应该配置白名单
- 只允许可信来源的跨域请求

---

## 🟡 SEC-007：缺少请求超时配置

### 问题位置

```
/src/api/axiosCenter.js
```

### 🔍 问题原理分析

📖 **学习理解**：请求没有超时限制，可能导致用户长时间等待。

**安全问题原理**：

1. **资源占用**：请求可能无限期挂起
2. **用户体验差**：用户不知道请求是否成功
3. **可能的DoS**：恶意请求可能占用服务器资源

**学习理解**：
- 应该设置合理的请求超时时间
- 超时后应该给用户友好的提示

---

## 🟡 SEC-008：缺少错误处理

### 问题位置

```
/src/mtbnewcomponents/comPrintTable/comPrintTable.vue
```

### 🔍 问题原理分析

📖 **学习理解**：错误处理不完善可能导致信息泄露或程序崩溃。

**安全问题原理**：

1. **信息泄露**：错误信息可能包含敏感信息
2. **程序崩溃**：未捕获的错误可能导致程序异常
3. **调试困难**：缺少错误日志难以排查问题

**学习理解**：
- 应该有统一的错误处理机制
- 错误信息不应该直接展示给用户

---

## 📋 安全问题学习总结

| 问题编号 | 问题名称 | 风险等级 | 学习要点 |
|---------|---------|---------|---------|
| SEC-001 | Token通过URL明文传递 | 🔴 高危 | 理解Token安全传输原理 |
| SEC-002 | 使用不安全的MD5密码哈希 | 🔴 高危 | 理解密码哈希算法安全性 |
| SEC-003 | 敏感数据存储在sessionStorage | 🟠 中危 | 理解前端存储安全 |
| SEC-004 | Token从URL重复解析 | 🟠 中危 | 理解Token管理最佳实践 |
| SEC-005 | 硬编码RSA公钥 | 🟠 中危 | 理解密钥管理安全 |
| SEC-006 | CORS配置过于宽松 | 🟠 中危 | 理解跨域安全策略 |
| SEC-007 | 缺少请求超时配置 | 🟡 低危 | 理解请求超时机制 |
| SEC-008 | 缺少错误处理 | 🟡 低危 | 理解错误处理安全 |

---

## 🔗 延伸阅读

- [安全修复工单](picc-mzmtb-agent-安全修复工单.md) - 每个问题的详细工单卡片
- [前端工程化与安全](picc-mzmtb-agent-前端工程化与安全.md) - 前端安全最佳实践

---

> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议
