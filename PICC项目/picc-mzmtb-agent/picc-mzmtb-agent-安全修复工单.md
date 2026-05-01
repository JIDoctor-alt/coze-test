# PICC门诊慢特病前端项目（picc-mzmtb-agent）
# 安全风险学习笔记

> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

> 工单生成日期：2024年
> 项目规模：652个Vue文件、74个API文件
> 技术栈：Vue 2.6 + Vuex 3 + Axios + Ant Design Vue
> 紧急程度：高

---

## 📋 风险概览表

| 编号 | 问题名称 | 风险等级 | 涉及文件数 | 学习要点 |
|------|---------|---------|-----------|---------|
| **SEC-001** | Token通过URL参数明文传递 | 🔴 高危 | 2 | 理解Token安全传输 |
| **SEC-002** | 使用不安全的MD5密码哈希 | 🔴 高危 | 4 | 理解密码哈希安全 |
| **SEC-003** | 敏感数据存储在sessionStorage | 🟠 中危 | 1 | 理解前端存储安全 |
| **SEC-004** | Token从URL重复解析 | 🟠 中危 | 1 | 理解Token管理 |
| **SEC-005** | 硬编码RSA公钥 | 🟠 中危 | 1 | 理解密钥管理 |
| **SEC-006** | CORS配置过于宽松 | 🟠 中危 | 1 | 理解跨域安全 |
| **SEC-007** | 缺少请求超时配置 | 🟡 低危 | 1 | 理解请求超时 |
| **SEC-008** | 缺少错误处理 | 🟡 低危 | 1 | 理解错误处理 |

---

## 🔴 SEC-001：Token通过URL参数明文传递

### 问题位置

```
/src/mtbnewcomponents/menuList/menuindex.vue:87
/src/mtbnewcomponents/menuList/menudeclare.vue:86
```

### 📖 学习理解

**问题原理**：Token 是用户的身份凭证，相当于"家门钥匙"。通过URL传递Token会带来以下风险：

1. **浏览器历史记录**：URL会被记录在浏览器历史中
2. **服务器日志**：URL会被记录在服务器访问日志中
3. **链接分享**：用户分享链接时会无意中泄露Token

**学习要点**：
- Token应该通过安全的HTTP头传输
- 推荐使用HttpOnly Cookie存储Token
- URL中不应该包含敏感信息

---

## 🔴 SEC-002：使用不安全的MD5密码哈希

### 问题位置

```
/src/utils/util.js:45
/src/mtbnewcomponents/loginMb/settingModal.vue
```

### 📖 学习理解

**问题原理**：MD5已经被证明是不安全的哈希算法。

**学习要点**：
- MD5存在碰撞攻击：不同输入可能产生相同输出
- MD5计算速度太快：现代GPU可以每秒计算数十亿次，暴力破解太容易
- 推荐使用bcrypt、Argon2或PBKDF2等安全哈希算法

---

## 🟠 SEC-003：敏感数据存储在sessionStorage

### 问题位置

```
/src/mtbnewcomponents/loginMb/index.vue
```

### 📖 学习理解

**问题原理**：sessionStorage 虽然是会话级存储，但并不安全。

**学习要点**：
- XSS攻击可以读取sessionStorage
- 开发者工具可以直接查看存储内容
- 敏感数据应该只存储在服务端
- 推荐使用HttpOnly Cookie存储认证信息

---

## 🟠 SEC-004：Token从URL重复解析

### 问题位置

```
/src/api/axiosCenter.js
```

### 📖 学习理解

**问题原理**：每次请求都从URL解析Token是低效且不安全的做法。

**学习要点**：
- Token应该在登录后缓存，而不是每次解析
- URL中的Token容易被泄露
- 推荐使用安全的Token存储方式

---

## 🟠 SEC-005：硬编码RSA公钥

### 问题位置

```
/src/utils/util.js
```

### 📖 学习理解

**问题原理**：RSA公钥硬编码在代码中，难以维护和更换。

**学习要点**：
- 密钥应该从配置中心或接口动态获取
- 硬编码密钥难以更换
- 不同环境应该使用不同密钥

---

## 🟠 SEC-006：CORS配置过于宽松

### 问题位置

```
/src/api/axiosCenter.js
```

### 📖 学习理解

**问题原理**：CORS配置过于宽松会导致跨域安全风险。

**学习要点**：
- 应该配置允许的来源白名单
- 只允许可信来源的跨域请求
- 避免使用`*`允许所有来源

---

## 🟡 SEC-007：缺少请求超时配置

### 问题位置

```
/src/api/axiosCenter.js
```

### 📖 学习理解

**问题原理**：请求没有超时限制可能导致用户体验问题。

**学习要点**：
- 应该设置合理的请求超时时间
- 超时后应该给用户友好提示
- 避免请求无限期挂起

---

## 🟡 SEC-008：缺少错误处理

### 问题位置

```
/src/mtbnewcomponents/comPrintTable/comPrintTable.vue
```

### 📖 学习理解

**问题原理**：错误处理不完善可能导致程序异常。

**学习要点**：
- 应该有统一的错误处理机制
- 错误信息不应该直接暴露给用户
- 应该记录错误日志便于排查

---

## 📎 附录

### 关键文件清单

| 文件路径 | 涉及问题 |
|---------|---------|
| `/src/api/axiosCenter.js` | SEC-001, SEC-004, SEC-006, SEC-007 |
| `/src/mtbnewcomponents/loginMb/index.vue` | SEC-003 |
| `/src/mtbnewcomponents/menuList/menuindex.vue` | SEC-001 |
| `/src/mtbnewcomponents/menuList/menudeclare.vue` | SEC-001 |
| `/src/utils/util.js` | SEC-002, SEC-005 |
| `/src/mtbnewcomponents/loginMb/settingModal.vue` | SEC-002 |
| `/src/mtbnewcomponents/comPrintTable/comPrintTable.vue` | SEC-008 |

---

> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议
