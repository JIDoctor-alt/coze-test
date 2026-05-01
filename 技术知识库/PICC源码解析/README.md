# PICC源码解析文档

> 📌 本目录包含人保健康医疗通项目两个核心模块的源码解析

---

## 📚 文档清单

### picc-mzmtb-auth 认证服务模块

| 文档 | 说明 |
|------|------|
| [`picc-mzmtb-auth解析.md`](./picc-mzmtb-auth解析.md) | **核心解析文档**（登录流程、验证码、Token机制等） |
| [`picc-mzmtb-auth文件清单.md`](./picc-mzmtb-auth文件清单.md) | 文件清单索引（快速定位文件） |

### picc-mzmtb-common 公共模块

| 文档 | 说明 |
|------|------|
| [`picc-mzmtb-common解析.md`](./picc-mzmtb-common解析.md) | **核心解析文档**（数据库操作、Redis、加密、接口调用等） |
| [`picc-mzmtb-common文件清单.md`](./picc-mzmtb-common文件清单.md) | 文件清单索引（快速定位文件） |

---

## 🎯 推荐阅读顺序

### 1. 如果你是Java新手
建议阅读顺序：
1. `picc-mzmtb-common解析.md` → 了解基础工具
2. `picc-mzmtb-auth解析.md` → 了解业务流程

### 2. 如果你想了解登录流程
→ 直接阅读 `picc-mzmtb-auth解析.md` 的"登录流程"部分

### 3. 如果你想找某个文件
→ 打开对应的 `文件清单.md`，按Ctrl+F搜索

### 4. 如果你想了解某个类
→ 搜索对应的 `### xxx` 标题

---

## 📖 核心概念速查

### Auth服务（认证）
| 概念 | 解释 | 相关文件 |
|------|------|----------|
| Token | 登录凭证，120分钟有效 | SM4Util.java, RedisKeyConf.java |
| 验证码 | 短信/拼图验证码 | CaptchaUtil.java, VipSecurityCodeServiceImpl |
| 用户实体 | 账号/密码/角色 | PrivilegeUserInfo.java |
| 菜单权限 | 用户能访问的页面 | PrivilegeMenuInfo.java |

### Common服务（公共）
| 概念 | 解释 | 相关文件 |
|------|------|----------|
| BaseEntity | 所有实体的老祖宗 | BaseEntity.java |
| BaseServiceImpl | 增删改查模板 | BaseServiceImpl.java |
| Redis | 缓存/会话存储 | RedisUtil.java |
| 雪花算法 | 生成唯一ID | IdWorker.java, PrimaryKeyUtil.java |

---

## 🔧 技术栈速查

| 技术 | 用途 | 位置 |
|------|------|------|
| Spring Boot | 框架 | 启动类 |
| MyBatis/TkMyBatis | 数据库 | MyMapper.java |
| Redis | 缓存 | RedisConfig.java |
| SM4 | 国密加密 | SM4Util.java |
| MD5/SHA | 哈希加密 | MD5Util.java |
| Jackson/FastJSON | JSON | JsonUtil.java |
| 雪花算法 | ID生成 | IdWorker.java |
| Swagger | 接口文档 | SwaggerConfiguration.java |

---

## 📊 源码统计

| 模块 | Java文件数 |
|------|-----------|
| picc-mzmtb-auth | 89个 |
| picc-mzmtb-common | 139个 |
| **合计** | **228个** |

---

## 📝 文档更新说明

- **更新时间**：2024年
- **解析深度**：核心文件详细解析，普通文件列表索引
- **小白友好**：使用生活比喻解释技术概念
