# 📚 PICC慢病管理网关源码解析 - 文档索引

## 🎯 项目概述

**picc-mzmtb-gateway** 是PICC(中国人保)慢病管理系统的**API网关**，负责：
- 请求拦截与安全过滤
- Token验证与权限控制
- 请求转发到后端服务
- 对外提供HTTP REST和SOAP WebService接口

---

## 📖 文档导航

### 🔰 新手入门
| 文档 | 说明 | 推荐阅读顺序 |
|------|------|--------------|
| `00-项目概览.md` | 项目整体架构、技术栈、业务流程 | ⭐ 必读 |
| `10-完整文件清单.md` | 809个文件的索引目录 | 按需查阅 |

### 📦 模块详解
| 文档 | 内容 | 重要程度 |
|------|------|----------|
| `01-config配置类.md` | 跨域、加密、拦截器、XSS、定时任务 | ⭐⭐⭐ |
| `02-mb慢病管理.md` | 523个文件，核心业务模块 | ⭐⭐⭐⭐⭐ |
| `03-webservice接口.md` | SOAP XML接口，第三方对接 | ⭐⭐⭐ |
| `04-restful接口.md` | REST JSON接口，OCR、消息推送 | ⭐⭐⭐ |
| `05-utils工具类.md` | 23个工具类详解 | ⭐⭐⭐ |
| `06-其他业务模块.md` | 药店、大屏、日志、定州等 | ⭐⭐ |
| `07-mtb慢特病.md` | 慢特病管理模块 | ⭐⭐⭐ |
| `08-ws-WebService实现.md` | CXF WebService实现 | ⭐⭐⭐ |
| `09-剩余小模块.md` | BaseApi、Cache、Call等 | ⭐ |

---

## 🎓 学习路径

### 路径1: 从整体到局部
```
1. 项目概览 → 了解系统全貌
2. config配置 → 理解安全机制
3. mb慢病管理 → 掌握核心业务
4. webservice/restful → 理解外部对接
```

### 路径2: 从入口到核心
```
1. 拦截器链(APIAuthorityFilter) → 请求如何进来
2. BaseApi → API如何组织
3. MbDeclareApi → 核心业务如何处理
4. HttpForwardUtil → 如何转发请求
```

---

## 📁 快速定位

### 想找某个API？
- 登录接口 → `02-mb慢病管理.md` → LoginApi
- 申报接口 → `02-mb慢病管理.md` → MbDeclareApi
- 药店接口 → `06-其他业务模块.md` → drugstore

### 想找某个工具类？
- 加密解密 → `05-utils工具类.md` → AesUtil/Sm2Util
- HTTP转发 → `05-utils工具类.md` → HttpForwardUtil
- 文件上传 → `05-utils工具类.md` → FTP/SFTP

### 想找某个配置？
- 跨域配置 → `01-config配置类.md` → GlobalCorsConfig
- Token验证 → `01-config配置类.md` → APIAuthorityFilter
- XSS防护 → `01-config配置类.md` → XssRequestFilter

---

## 🔑 核心概念速查

| 概念 | 说明 | 文档位置 |
|------|------|----------|
| Gateway | 网关层，不执行业务，只转发 | 00-项目概览 |
| Token | 用户身份凭证，存Redis | 01-config |
| SM2加密 | 国密算法，解密小程序数据 | 05-utils |
| SOAP/XML | WebService通信格式 | 03-webservice |
| REST/JSON | HTTP接口通信格式 | 04-restful |
| flag | 地区标识，ThreadLocal存储 | 07-mtb |
| AOP切面 | 自动解密@EncryptField字段 | 01-config |

---

## 🛠️ 常用开发场景

### 场景1: 新增一个API
1. 在对应模块创建Api类，继承BaseApi
2. 使用HttpForwardUtil转发请求
3. 定义VO接收参数和返回结果

### 场景2: 新增WebService接口
1. 在webservice/vo定义请求/响应VO
2. 在ws/service定义接口和实现
3. 在CxfConfig发布服务

### 场景3: 新增第三方对接
1. 在restful/api创建接口
2. 在webservice/vo/third添加报文VO
3. 在ws/adapter添加适配器

---

## 📞 问题排查

| 问题 | 可能原因 | 排查位置 |
|------|----------|----------|
| Token无效 | Redis中Token过期 | APIAuthorityFilter |
| 接口无权限 | 小程序Token验证失败 | APIAuthorityFilter |
| 请求转发失败 | 后端服务未启动 | HttpForwardUtil |
| SM2解密失败 | 前后端密钥不一致 | Sm2Util |
| CORS跨域错误 | 未配置跨域或路径错误 | GlobalCorsConfig |

---

## 📊 文件统计

| 类型 | 数量 |
|------|------|
| 总文件数 | 809 |
| API接口 | 100+ |
| Service服务 | 20+ |
| VO对象 | 500+ |
| 枚举常量 | 100+ |
| 工具类 | 23 |
| 配置类 | 13 |

---

## 🔗 相关文档

- **项目源码**: `/app/data/所有对话/主对话/picc-mzmtb-gateway/`
- **后端服务**: `picchealth-api-paas` (业务逻辑在此)
- **配置中心**: Apollo配置中心

---

*最后更新: 2024*
