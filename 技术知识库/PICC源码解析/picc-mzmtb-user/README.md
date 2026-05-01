# PICC-MZMTB-USER 源码解析索引

> 📚 人保健康微服务 - 用户权限管理系统

## 项目概述

本项目是PICC人保健康的**用户权限管理微服务**，负责：
- 👤 用户管理（CRUD、角色分配、密码重置）
- 🔐 RBAC权限控制（角色、菜单、资源、数据权限）
- 🏢 机构管理（树形结构、父子关系）
- 🔑 敏感数据加密（SM4/AES加密）
- 🗄️ PersonDivision分区权限管理
- 📋 权限归属(Auth)配置

---

## 模块索引

### 1️⃣ 敏感数据加密模块 (`SensitiveEncrypt`)
**文件**: 4个 | **说明**: 用户五要素加密脱敏

| 文件名 | 一句话说明 |
|--------|-----------|
| `AesUtil.java` | AES对称加密工具类 |
| `SensitiveEncrypt.java` | 敏感字段加密注解 |
| `SensitiveEncryptSerializer.java` | JSON序列化加密器 |
| `SensitiveEncryptDeserializer.java` | JSON反序列化解密器 |

📖 [查看详细解析](./01-敏感数据加密模块.md)

---

### 2️⃣ 角色管理模块 (`role`)
**文件**: 10个 | **说明**: 角色的增删改查和资源绑定

| 文件名 | 一句话说明 |
|--------|-----------|
| `RoleInfoApi.java` | 角色管理API接口 |
| `RoleInfoService.java` | 角色服务接口定义 |
| `RoleInfoServiceImpl.java` | 角色服务实现（含资源管理） |
| `PrivilegeRoleInfo.java` | 角色实体类 |
| `PrivilegeRoleResource.java` | 角色-资源关联实体 |
| `RoleCreateVo.java` | 创建角色请求参数 |
| `RoleUpdateVo.java` | 更新角色请求参数 |
| `RoleDeleteVo.java` | 删除角色请求参数 |
| `RoleDetailVo.java` | 角色详情查询参数 |
| `ResourceVo.java` | 资源配置参数 |

📖 [查看详细解析](./02-角色管理模块.md)

---

### 3️⃣ 菜单管理模块 (`menu`)
**文件**: 8个 | **说明**: 系统菜单树形管理

| 文件名 | 一句话说明 |
|--------|-----------|
| `MenuInfoApi.java` | 菜单管理API接口 |
| `MenuInfoService.java` | 菜单服务接口定义 |
| `MenuInfoServiceImpl.java` | 菜单服务实现 |
| `PrivilegeMenuInfoServiceImpl.java` | 菜单业务服务实现 |
| `PrivilegeMenuServiceServiceImpl.java` | 菜单-服务关联实现 |
| `PrivilegeMenuInfoVo.java` | 菜单视图对象 |
| `PrivilegeMenuServiceVo.java` | 菜单服务视图对象 |
| `PrivilegeMenuInfo.java` | 菜单实体类 |

📖 [查看详细解析](./03-菜单管理模块.md)

---

### 4️⃣ 系统管理模块 (`sys`)
**文件**: 最多 | **说明**: 用户、机构、系统、权限归属管理

#### 4.1 用户管理
| 文件名 | 一句话说明 |
|--------|-----------|
| `UserInfoApi.java` | 用户管理API接口 |
| `UserInfoService.java` | 用户服务接口定义 |
| `UserInfoServiceImpl.java` | 用户服务实现（含分区权限配置） |
| `PrivilegeUserInfo.java` | 用户实体类 |
| `PrivilegeUserRoleInfo.java` | 用户-角色关联实体 |
| `PrivilegeUserAuth.java` | 用户-权限归属关联实体 |

#### 4.2 机构管理
| 文件名 | 一句话说明 |
|--------|-----------|
| `OrgInfoApi.java` | 机构管理API接口 |
| `OrgInfoService.java` | 机构服务接口定义 |
| `OrgInfoServiceImpl.java` | 机构服务实现 |
| `PrivilegeOrgInfo.java` | 机构实体类 |
| `PrivilegeOrgSystem.java` | 机构-系统订阅实体 |

#### 4.3 系统管理
| 文件名 | 一句话说明 |
|--------|-----------|
| `SysInfoApi.java` | 系统管理API接口 |
| `SysInfoService.java` | 系统服务接口定义 |
| `SysInfoServiceImpl.java` | 系统服务实现 |
| `PrivilegeSystemInfo.java` | 系统实体类 |

#### 4.4 数据迁移
| 文件名 | 一句话说明 |
|--------|-----------|
| `MoveApi.java` | 数据迁移API接口 |
| `MoveService.java` | 数据迁移服务接口 |
| `MoveServiceImpl.java` | 数据迁移实现 |

📖 [查看详细解析](./04-系统管理模块.md)

---

### 5️⃣ 分区权限模块 (`PersonDivision`)
**文件**: 4个 | **说明**: 各地区医保分区权限配置

| 文件名 | 一句话说明 |
|--------|-----------|
| `PersonDivision.java` | 分区权限实体类 |
| `PersonDivisionDao.java` | 分区权限数据访问 |
| `PersonDivisionVo.java` | 分区权限视图对象 |
| `PersonDivisionDao.java` | 分区权限DAO |

📖 [查看详细解析](./05-分区权限模块.md)

---

### 6️⃣ 配置模块 (`config`)
**文件**: 4个 | **说明**: 拦截器、过滤器配置

| 文件名 | 一句话说明 |
|--------|-----------|
| `APIAuthorityFilter.java` | API权限过滤器（Token校验） |
| `ApiInterceptor.java` | API拦截器注解 |
| `MvcInterceptorConfig.java` | MVC拦截器配置 |
| `TokenInterceptorConfig.java` | Token拦截器配置 |

📖 [查看详细解析](./06-配置模块.md)

---

### 7️⃣ 工具类模块 (`utils`)
**文件**: 10个 | **说明**: 通用工具类

| 文件名 | 一句话说明 |
|--------|-----------|
| `UserUtils.java` | 当前登录用户上下文获取 |
| `SM4Util.java` | 国密SM4加密工具 |
| `AESUtil.java` | AES加密工具 |
| `EncryptionUtil.java` | MD5/SHA加密工具 |
| `AuthConfigEnum.java` | 权限归属配置枚举 |
| `UnitConfigEnum.java` | 地区单位配置枚举 |
| `ReturnStatusEnum.java` | 返回状态枚举 |
| `UniqueIDGenerator.java` | UUID生成器 |
| `LocalTimeUtils.java` | 时间处理工具 |
| `NotBlankFieldCopy.java` | 非空字段拷贝工具 |
| `User.java` | 用户信息实体 |

📖 [查看详细解析](./07-工具类模块.md)

---

### 8️⃣ 数据访问层 (`dao`)
**文件**: 22个 | **说明**: MyBatis数据库操作

| DAO文件 | 对应PO | 说明 |
|---------|--------|------|
| `PrivilegeUserInfoDao.java` | PrivilegeUserInfo | 用户DAO |
| `PrivilegeOrgInfoDao.java` | PrivilegeOrgInfo | 机构DAO |
| `PrivilegeRoleInfoDao.java` | PrivilegeRoleInfo | 角色DAO |
| `PrivilegeMenuInfoDao.java` | PrivilegeMenuInfo | 菜单DAO |
| `PrivilegeSystemInfoDao.java` | PrivilegeSystemInfo | 系统DAO |
| `PrivilegeAuthInfoDao.java` | PrivilegeAuthInfo | 权限归属DAO |
| `PrivilegeUserRoleInfoDao.java` | PrivilegeUserRoleInfo | 用户角色DAO |
| `PrivilegeUserAuthDao.java` | PrivilegeUserAuth | 用户权限归属DAO |
| `PrivilegeRoleResourceDao.java` | PrivilegeRoleResource | 角色资源DAO |
| `PrivilegeOrgSystemDao.java` | PrivilegeOrgSystem | 机构系统DAO |
| `PersonDivisionDao.java` | PersonDivision | 分区权限DAO |
| `SensitiveWordsDao.java` | SensitiveWords | 敏感词DAO |
| `AccountRecordDao.java` | AccountRecord | 账户记录DAO |
| `UpOrgUserDao.java` | UpOrgUser | 机构用户DAO |

📖 [查看详细解析](./08-数据访问层.md)

---

### 9️⃣ 实体类模块 (`po`)
**文件**: 14个 | **说明**: 数据库表对应实体

| 文件名 | 对应表 | 核心字段 |
|--------|--------|----------|
| `PrivilegeUserInfo.java` | privilege_user_info | 用户信息 |
| `PrivilegeOrgInfo.java` | privilege_org_info | 机构信息 |
| `PrivilegeRoleInfo.java` | privilege_role_info | 角色信息 |
| `PrivilegeMenuInfo.java` | privilege_menu_info | 菜单信息 |
| `PrivilegeSystemInfo.java` | privilege_system_info | 系统信息 |
| `PrivilegeAuthInfo.java` | privilege_auth_info | 权限归属信息 |
| `PrivilegeUserRoleInfo.java` | privilege_user_role_info | 用户角色关联 |
| `PrivilegeUserAuth.java` | privilege_user_auth | 用户权限归属关联 |
| `PrivilegeRoleResource.java` | privilege_role_resource | 角色资源关联 |
| `PrivilegeOrgSystem.java` | privilege_org_system | 机构系统订阅 |
| `PersonDivision.java` | person_division | 分区权限 |
| `SensitiveWords.java` | sensitive_words | 敏感词 |
| `AccountRecord.java` | account_record | 账户记录 |
| `UpOrgUser.java` | up_org_user | 机构用户 |

📖 [查看详细解析](./09-实体类模块.md)

---

## 核心知识点

### 🔐 加密体系
```
用户五要素加密:
├── @SensitiveEncrypt 注解
│   ├── 序列化时: AES加密
│   └── 反序列化时: AES解密
└── 密码加密: SM4国密算法
```

### 🏢 权限架构(RBAC)
```
用户(User) 
    ├── 归属机构(Org)
    ├── 拥有角色(Role) ───→ 绑定菜单(Menu)
    └── 配置权限归属(Auth) ───→ 设置分区(PersonDivision)

机构(Org)
    ├── 树形结构(父子关系)
    ├── 订阅系统(System)
    └── 分配菜单(Menu)
```

### 🗄️ PersonDivision分区权限
```java
// 各地区医保系统权限配置
PersonDivision {
    account: 账号
    flag: 地市标识(0-宝鸡, 4-延安, 7-榆林...)
    unitcode/unitname: 服务窗口
    persontype: 人员身份(职工/居民)
    isupdate: 修改权限(1-支公司, 2-分公司)
    isdownload: 下载权限(九江批量下载)
    isfilingback: 备案撤销权限
    isyb: 医保账号标识
    ismanual: 手动分配权限(榆林)
}
```

---

## 快速导航

- [总目录](./README.md)
- [01-敏感数据加密模块](./01-敏感数据加密模块.md)
- [02-角色管理模块](./02-角色管理模块.md)
- [03-菜单管理模块](./03-菜单管理模块.md)
- [04-系统管理模块](./04-系统管理模块.md)
- [05-分区权限模块](./05-分区权限模块.md)
- [06-配置模块](./06-配置模块.md)
- [07-工具类模块](./07-工具类模块.md)
- [08-数据访问层](./08-数据访问层.md)
- [09-实体类模块](./09-实体类模块.md)
