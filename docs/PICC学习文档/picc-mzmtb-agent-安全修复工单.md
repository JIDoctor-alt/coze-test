> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC门诊慢特病前端项目（picc-mzmtb-agent）
# 安全修复工单

> 工单生成日期：2024年
> 项目规模：652个Vue文件、74个API文件
> 技术栈：Vue 2.6 + Vuex 3 + Axios + Ant Design Vue
> 紧急程度：高

---

## 📋 工单概览表

| 编号 | 问题名称 | 风险等级 | 涉及文件数 | 负责人 | 预计工时 | 修复时间 |
|------|---------|---------|-----------|--------|---------|---------|
| **SEC-001** | Token通过URL参数明文传递 | 🔴 高危 | 2 | 前端开发 | 8h | Week 1 |
| **SEC-002** | 使用不安全的MD5密码哈希 | 🔴 高危 | 4 | 前端开发 | 6h | Week 1 |
| **SEC-003** | 敏感数据存储在sessionStorage | 🟠 中危 | 1 | 前端开发 | 4h | Week 2 |
| **SEC-004** | Token从URL重复解析 | 🟠 中危 | 1 | 前端开发 | 3h | Week 2 |
| **SEC-005** | 硬编码RSA公钥 | 🟠 中危 | 1 | 前端开发 | 4h | Week 2 |
| **SEC-006** | CORS配置过于宽松 | 🟠 中危 | 1 | 前后端联动 | 2h | Week 2 |
| **SEC-007** | 99处console.log调试代码残留 | 🟡 中危 | 50+ | 前端开发 | 6h | Week 2 |
| **SEC-008** | 打印功能使用innerHTML | 🔵 低危 | 4 | 前端开发 | 3h | Week 3 |
| **SEC-009** | 硬编码的AccountNum | 🔵 低危 | 1 | 前端开发 | 1h | Week 3 |

---

## 📅 修复时间线

```
Week 1 (紧急修复)
├── SEC-001: Token通过URL参数明文传递 ⭐⭐⭐
└── SEC-002: 使用不安全的MD5密码哈希 ⭐⭐⭐

Week 2 (重点修复)
├── SEC-003: 敏感数据存储在sessionStorage ⭐⭐
├── SEC-004: Token从URL重复解析 ⭐⭐
├── SEC-005: 硬编码RSA公钥 ⭐⭐
├── SEC-006: CORS配置过于宽松 ⭐⭐
└── SEC-007: 99处console.log调试代码残留 ⭐⭐

Week 3 (收尾清理)
├── SEC-008: 打印功能使用innerHTML ⭐
└── SEC-009: 硬编码的AccountNum ⭐
```

---

## 🔴 高危工单详情

---

### SEC-001：Token通过URL参数明文传递

#### 问题描述

系统登录后，用户Token（相当于"电子通行证"）通过URL的query参数明文传递。

**🔍 小白解释**：就像把家门钥匙写在信封外面寄信一样危险！别人只要看一眼浏览器地址栏，就能知道你的"通行证"是什么。

#### 影响分析

| 风险项 | 说明 |
|-------|------|
| 浏览器历史记录 | URL会被浏览器记住，任何能用你电脑的人都能看到 |
| 服务器日志 | 访问日志会完整记录URL，Token泄露 |
| Referer头泄露 | 页面跳转到其他网站时，Token会随Referer头发送出去 |
| 书签泄露 | 用户收藏带Token的URL，等于把钥匙贴在门上 |

#### 涉及文件

```
/src/mtbnewcomponents/menuList/menuindex.vue:87
/src/mtbnewcomponents/menuList/menudeclare.vue:86
```

#### 问题分析

- **短期**：移除URL中的Token参数，改为从sessionStorage读取
- **长期**：后端配合改用HttpOnly Cookie

#### 预计工时：8小时

---

### SEC-002：使用不安全的MD5密码哈希

#### 问题描述

项目使用MD5算法对用户密码进行哈希处理，但MD5已被密码学界认定不安全。

**🔍 小白解释**：MD5就像用一把已经很旧的锁，虽然能锁上，但小偷有现成的工具可以秒开。

#### 影响分析

| 风险项 | 说明 |
|-------|------|
| 彩虹表攻击 | MD5彩虹表可以在秒级破解常见密码（如123456） |
| 数据库泄露风险 | 如果数据库泄露，用户密码可被还原 |
| 合规风险 | 不符合等保三级要求的密码存储标准 |

#### 涉及文件

```
/src/mtbnewcomponents/loginMb/settingModal.vue:114
/src/pages/DZChronicDis/serveStatusMod.vue:418
/src/pages/YLChronicDis/serveStatusMod.vue:418
```

#### 问题分析

- **前端**：使用SHA-256替代MD5（Web Crypto API）
- **后端**：使用bcrypt/Argon2做密码哈希

#### 预计工时：6小时

---

## 🟠 中危工单详情

---

### SEC-003：敏感数据存储在sessionStorage

#### 问题描述

用户登录信息和Token存储在sessionStorage中，存在XSS攻击窃取风险。

**🔍 小白解释**：sessionStorage就像贴在电脑屏幕上的便利贴，关了浏览器就没了。但如果网站有漏洞，"有人在便利贴上偷看你的信息"。

#### 影响分析

| 风险项 | 说明 |
|-------|------|
| XSS攻击 | 如果页面存在XSS漏洞，恶意脚本可以读取sessionStorage |
| 跨站攻击 | 攻击者可以获取用户登录凭证 |
| 数据暴露 | 用户名、手机号等敏感信息可被窃取 |

#### 涉及文件

```
/src/mtbnewcomponents/loginMb/index.vue:177
```

#### 问题分析

将敏感数据从sessionStorage迁移到Vuex内存存储，页面刷新时重新从接口获取。

#### 预计工时：4小时

---

### SEC-004：Token从URL重复解析

#### 问题描述

在axiosCenter.js的请求拦截器中，每次发起请求都从URL解析Token。

**🔍 小白解释**：就像每次买东西都要重新去银行查余额，而不是用之前取好的钱，效率低且增加Token泄露风险。

#### 影响分析

| 风险项 | 说明 |
|-------|------|
| 性能损耗 | 每次请求都重复解析URL |
| 安全风险 | URL中Token暴露时间延长 |
| 代码复杂 | 多种获取Token的路径难以维护 |

#### 涉及文件

```
/src/api/axiosCenter.js:45-52
```

#### 问题分析

统一从Vuex store或sessionStorage缓存读取Token，不重复解析URL。

#### 预计工时：3小时

---

### SEC-005：硬编码RSA公钥

#### 问题描述

在util.js中硬编码了RSA公钥，不利于密钥轮换。

**🔍 小白解释**：公钥虽然可以公开，但每次换锁都要重新发布代码，太麻烦了。

#### 影响分析

| 风险项 | 说明 |
|-------|------|
| 密钥轮换困难 | 需要重新发布前端代码 |
| 版本管理复杂 | 不同环境的密钥管理混乱 |

#### 涉及文件

```
/src/utils/util.js:290-298
```

#### 问题分析

从后端接口动态获取公钥，缓存24小时。

#### 预计工时：4小时

---

### SEC-006：CORS配置过于宽松

#### 问题描述

Axios请求配置中允许所有来源的跨域请求。

**🔍 小白解释**：CORS就像门卫，只认识的人才能进。现在门卫谁都不认识，任何人都能进。

#### 影响分析

| 风险项 | 说明 |
|-------|------|
| 恶意调用 | 恶意网站可以调用后端接口 |
| CSRF攻击 | 增加跨站请求伪造风险 |

#### 涉及文件

```
/src/api/axiosCenter.js:106
```

#### 问题分析

后端配置具体的允许来源列表，不使用通配符`*`。

#### 预计工时：2小时（需要后端配合）

---

### SEC-007：99处console.log调试代码残留

#### 问题描述

代码中存在99处console.log、console.warn、console.error调试代码未清理。

**🔍 小白解释**：console.log就像"大声说出自己的银行卡密码"，在生产环境中很危险。

#### 影响分析

| 风险项 | 说明 |
|-------|------|
| 信息泄露 | 可能打印敏感业务数据 |
| 性能损耗 | console操作影响性能 |
| 可读性差 | 控制台充满无用信息 |

#### 涉及文件

50+个文件

#### 问题分析

1. 批量搜索并删除console语句
2. 或在webpack配置中确认drop_console生效

#### 预计工时：6小时

---

## 🔵 低危工单详情

---

### SEC-008：打印功能使用innerHTML

#### 问题描述

多处使用innerHTML进行打印内容处理，存在潜在的XSS风险。

#### 涉及文件

```
/src/components/comPrintTable/comPrintTable.vue:183
/src/mtbcomponents/comPrintTable/comPrintTable.vue:183
/src/mtbslcomponents/comPrintTable/comPrintTable.vue:183
/src/mtbnewcomponents/comPrintTable/comPrintTable.vue:183
```

#### 问题分析

使用textContent替代innerHTML，或进行HTML转义。

#### 预计工时：3小时

---

### SEC-009：硬编码的AccountNum

#### 问题描述

在请求头中硬编码了accountNum账号标识。

#### 涉及文件

```
/src/api/axiosCenter.js:60-64
```

#### 问题分析

将这些标识符移到环境变量配置文件中。

#### 预计工时：1小时

---

## ✅ 修复完成检查清单

### Week 1 完成后检查

- [ ] SEC-001：Token不再出现在URL参数中
- [ ] SEC-001：菜单跳转功能正常
- [ ] SEC-001：用户登出后Token正确清除
- [ ] SEC-002：登录接口使用SHA-256哈希
- [ ] SEC-002：修改密码功能正常
- [ ] SEC-002：测试常见密码（如123456）不再能用彩虹表秒破

### Week 2 完成后检查

- [ ] SEC-003：敏感数据存储在Vuex内存中
- [ ] SEC-003：页面刷新后用户状态正确恢复
- [ ] SEC-004：Token从单一来源读取
- [ ] SEC-004：网络请求中Token正确携带
- [ ] SEC-005：公钥从后端接口获取
- [ ] SEC-005：公钥缓存机制正常
- [ ] SEC-006：后端配置了具体的CORS来源白名单
- [ ] SEC-007：所有console.log已清理
- [ ] SEC-007：生产环境控制台无调试信息

### Week 3 完成后检查

- [ ] SEC-008：打印功能使用textContent或转义
- [ ] SEC-008：打印预览正常显示
- [ ] SEC-009：AccountNum移至环境变量
- [ ] SEC-009：多环境构建正常

---

## 📎 附录

### 关键文件清单

| 文件路径 | 涉及工单 |
|---------|---------|
| `/src/api/axiosCenter.js` | SEC-001, SEC-004, SEC-006, SEC-009 |
| `/src/mtbnewcomponents/loginMb/index.vue` | SEC-003 |
| `/src/mtbnewcomponents/menuList/menuindex.vue` | SEC-001 |
| `/src/mtbnewcomponents/menuList/menudeclare.vue` | SEC-001 |
| `/src/utils/util.js` | SEC-005 |
| `/src/mtbnewcomponents/loginMb/settingModal.vue` | SEC-002 |
| `/src/mtbnewcomponents/comPrintTable/comPrintTable.vue` | SEC-008 |

### 后端配合需求

| 工单 | 配合事项 |
|------|---------|
| SEC-001 | 改为通过HttpOnly Cookie返回Token |
| SEC-002 | 后端改用bcrypt/Argon2哈希 |
| SEC-005 | 提供公钥查询接口 |
| SEC-006 | 配置CORS白名单 |

---

**工单生成完毕**
