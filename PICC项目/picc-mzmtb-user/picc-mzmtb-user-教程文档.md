> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC人保健康权限管理系统 - 项目完整教程总纲

> 📖 **相关文档**：[Onboarding手册](picc-mzmtb-user-Onboarding手册.md) · [架构设计文档](picc-mzmtb-user-架构设计文档.md) · [数据库ER图](picc-mzmtb-user-数据库ER图与表结构.md) · [安全问题分析](picc-mzmtb-user-安全问题分析.md)

> 📅 生成日期：2026年4月30日
> 🎯 目标：零基础小白也能看懂的方法级教程文档
> 📖 项目全称：门诊慢特病业务管理信息系统-权限管理服务
> 🔧 技术栈：Spring Boot + MyBatis + GaussDB + Redis + Apollo + K8s + BES宝兰德

---

## 📚 文档导航

| 序号 | 章节 | 文件 | 内容 | 行数 |
|------|------|------|------|------|
| 0 | **总纲（本文档）** | picc-mzmtb-user-教程文档.md | 项目概览、阅读指南、完整索引 | 本文档 |
| 1 | Service层方法解析 | picc-mzmtb-user-补充方法解析.md | 73个public方法的全覆盖教程 | 1906 |
| 2 | API+Mapper+数据模型 | picc-mzmtb-user-API-Mapper-数据模型.md | 6个Api类、47个接口、Mapper XML、PO/DTO/VO | 1049 |
| 3 | 配置+部署+依赖 | picc-mzmtb-user-配置部署依赖.md | application.yml、Apollo、K8s、14个依赖、信创说明 | 227 |
| 4 | 安全机制深度解析 | picc-mzmtb-user-深度解析.md | 三道认证关卡、Token机制、密码加密体系、代码质量 | 350 |
| 5 | 核心查询拆解 | picc-mzmtb-user-深度解析第二章.md | query()200行逐行拆解、BFS机构树、数据流时序图、前端映射、安全问题分析 | 796 |
| 6 | 角色管理深度解析 | picc-mzmtb-user-深度解析第三章-角色管理.md | 12个角色方法、权限树、setAuths()权限归属 | 1430 |
| 7 | 菜单与系统管理 | picc-mzmtb-user-深度解析第四章-菜单与系统管理.md | 21个方法、菜单树递归、服务管理 | 1517 |
| 8 | 辅助模块 | picc-mzmtb-user-深度解析补充-辅助模块.md | BaseServiceImpl、AccountRecord、SensitiveWords | 175 |
| 9 | 数据库ER图 | picc-mzmtb-user-数据库ER图与表结构.md | 17张表ER图、字段详解、查询路径 | 21434→* |
| 10 | 新成员手册 | picc-mzmtb-user-Onboarding手册.md | 2小时上手指南、踩坑指南、FAQ | 8695→* |
| 11 | 安全问题分析 | picc-mzmtb-user-安全问题分析.md | P0/P1/P2分级问题分析、代码示例、学习路径 | 10547→* |
| 12 | 安全问题原理学习 | picc-mzmtb-user-安全问题原理学习文档.md | 安全原理学习与代码分析 | 10237→* |
| 13 | 方法级深度解析II | picc-mzmtb-user-方法级深度解析II.md | 17个核心方法含Spring Security逻辑 | 1458 |

*注：部分文件包含重复内容或被追加过，实际有效内容以各章节独立文件为准。

**总计覆盖**：~10000+行专业教程文档

---

## 🏗️ 项目架构速览

```
┌─────────────────────────────────────────────────────┐
│                  用户浏览器 (Vue)                     │
│    机构管理 | 用户管理 | 角色管理 | 菜单管理           │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│            Nginx / K8s Ingress (SSL终止)             │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│         Spring Boot 服务 (端口9092)                   │
│  ┌────────────────────────────────────────────┐     │
│  │  Filter Chain                               │     │
│  │  ApiAuthorityFilter → ApiInterceptor        │     │
│  └────────────────────┬───────────────────────┘     │
│  ┌────────────────────▼───────────────────────┐     │
│  │  API层 (6个Api类, 47个接口)                  │     │
│  │  OrgInfoApi | UserInfoApi | RoleInfoApi     │     │
│  │  MenuInfoApi | SysInfoApi | MoveApi         │     │
│  └────────────────────┬───────────────────────┘     │
│  ┌────────────────────▼───────────────────────┐     │
│  │  Service层 (8个有自定义方法 + 4个空壳)        │     │
│  │  73个public方法全覆盖                         │     │
│  └──────┬──────────┬──────────┬───────────────┘     │
│  │ Redis │  Apollo  │  Mapper/DAO (17个XML)   │     │
│  └──────┘──────────┘──────────┬───────────────┘     │
└───────────────────────────────┼─────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │    GaussDB (信创)      │
                    │    17张业务表           │
                    └───────────────────────┘
```

---

## 🔐 安全机制速览

```
请求进来
  │
  ├─ 第1关: ApiAuthorityFilter（Token校验，只拦截/privilege/user/）
  │         从Redis取Token验证
  │
  ├─ 第2关: ApiInterceptor（URL权限校验）
  │         检查用户角色是否有权访问该URL
  │
  └─ 第3关: Service层（业务权限校验）
            如authCode.contains("88")管理员判断
```

---

## 🗄️ 数据库表速览（17张）

| 分类 | 表名 | 说明 |
|------|------|------|
| 机构 | privilege_org_info | 机构信息（省/市/县树形结构） |
| | privilege_org_system | 机构-系统-菜单关联 |
| 用户 | privilege_user_info | 用户信息（账号、密码、所属机构） |
| | privilege_user_role | 用户-角色关联 |
| | privilege_user_auth | 用户-权限归属关联 |
| 角色 | privilege_role_info | 角色信息 |
| | privilege_role_resource | 角色-菜单资源关联 |
| 菜单 | privilege_menu_info | 菜单信息（树形结构） |
| | privilege_menu_service | 菜单服务（接口URL） |
| 系统 | privilege_system_info | 系统信息 |
| 权限 | privilege_auth_info | 权限归属信息 |
| | privilege_auth_menu | 权限-菜单映射 |
| 辅助 | person_division | 人员地市归属 |
| | up_org_user | 上级机构用户 |
| | account_record | 账号操作记录 |
| | sensitive_words | 敏感词表 |
| 旧系统 | sys_role_module_rel | 旧角色-模块关系（迁移用） |
| | sys_user_role_rel | 旧用户-角色关系（迁移用） |

---

## 🐛 已发现的关键问题

### 严重安全风险（P0）
1. SM4密钥硬编码 `1234****5678`
2. AES密钥硬编码 `abcdefg******12`
3. RSA密钥在@Value默认值中硬编码
4. URL权限用contains()模糊匹配

### 性能问题
5. query()方法N+1查询（每个机构循环查系统名称）
6. selectOrgSysInfo在同一数据上调两次（取systemId和menuId）
7. getidList() BFS逐层查数据库（N层=N次查询）
8. PageHelper pageNum=0等于不分页

### 设计问题
9. OrgQueryVo.orgName字段名误导（实际传的是机构ID）
10. passwordBackMD5()将密码明文存回数据库
11. AccountRecord操作人写死为"经办人"
12. SensitiveWords使用contains()匹配（会误杀）

---

## 📖 推荐阅读路径

### 路径A：新人入职（2小时快速上手）
1. → [新成员手册](picc-mzmtb-user-Onboarding手册.md) （30分钟）
2. → [数据库ER图](picc-mzmtb-user-数据库ER图与表结构.md) （30分钟）
3. → [API+Mapper+数据模型](picc-mzmtb-user-API-Mapper-数据模型.md) （30分钟）
4. → [配置+部署](picc-mzmtb-user-配置部署依赖.md) （30分钟）

### 路径B：深入理解业务（1天）
1. → [Service层方法解析](picc-mzmtb-user-补充方法解析.md) （2小时）
2. → [核心查询拆解](picc-mzmtb-user-深度解析第二章.md) （1小时）
3. → [角色管理](picc-mzmtb-user-深度解析第三章-角色管理.md) （1小时）
4. → [菜单与系统管理](picc-mzmtb-user-深度解析第四章-菜单与系统管理.md) （1小时）
5. → [安全机制](picc-mzmtb-user-深度解析.md) （1小时）

### 路径C：安全修复（3天）
1. → [安全机制深度解析](picc-mzmtb-user-深度解析.md) （了解问题）
2. → [安全问题分析](picc-mzmtb-user-安全问题分析.md) （问题分析）
3. → [安全问题原理学习](picc-mzmtb-user-安全问题原理学习文档.md) （具体代码）

---

## 📊 覆盖统计

| 维度 | 覆盖内容 | 状态 |
|------|---------|------|
| Service层 | 73个public方法 | ✅ 100% |
| API层 | 6个Api类、47个HTTP接口 | ✅ 100% |
| Mapper层 | 17个Mapper XML | ✅ 核心覆盖 |
| 数据模型 | 17张表ER图+字段说明 | ✅ 100% |
| 配置文件 | application.yml、bootstrap.yml、Apollo | ✅ 覆盖 |
| 部署 | K8s、CI/CD | ✅ 覆盖 |
| 安全机制 | 三道关卡+密码体系 | ✅ 深度解析 |
| 代码质量 | 6严重+8中等+6改进 | ✅ 审计完成 |
| 数据迁移 | 3个迁移方法 | ✅ 深度解析 |
| 新人上手 | Onboarding手册 | ✅ 2小时指南 |
| 安全修复 | P0/P1/P2方案+工单 | ✅ 可执行 |
