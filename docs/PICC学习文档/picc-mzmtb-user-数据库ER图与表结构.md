# PICC人保健康权限管理系统 - 数据库ER图与表结构详解

> 🎯 本章目标：用小白能看懂的方式，画出项目15+张数据库表之间的关系图，解释每张表的作用、关键字段、表与表之间的"谁认识谁"。

---

## 一、数据库全景图（ASCII版ER图）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          数据库ER关系图                                      │
│                                                                             │
│   ┌──────────────┐        ┌──────────────────┐        ┌─────────────────┐  │
│   │privilege_org  │1──────*│privilege_org_    │*──────1│privilege_system │  │
│   │    _info      │        │   system         │        │    _info        │  │
│   │ (机构信息)    │        │(机构-系统关联)    │        │ (系统信息)      │  │
│   └──────┬───────┘        └────────┬─────────┘        └────────┬────────┘  │
│          │1                        │1                           │1           │
│          │                         │                            │            │
│          *                         *                            *            │
│   ┌──────┴───────┐        ┌───────┴──────────┐        ┌───────┴────────┐  │
│   │privilege_user │        │privilege_menu_   │*──────1│privilege_menu  │  │
│   │    _info      │        │   info           │        │    _service    │  │
│   │ (用户信息)    │        │ (菜单信息)        │        │(菜单服务信息)  │  │
│   └──────┬───────┘        └──────────────────┘        └────────────────┘  │
│          │1                                                                  │
│          │                                                                   │
│          *                                                                   │
│   ┌──────┴──────────┐        ┌──────────────────┐                           │
│   │privilege_user_  │*──────1│privilege_role_   │                           │
│   │   role          │        │    info          │                           │
│   │(用户-角色关联)  │        │ (角色信息)        │                           │
│   └─────────────────┘        └──────┬───────────┘                           │
│                                      │1                                      │
│                                      *                                       │
│                              ┌───────┴──────────┐                           │
│                              │privilege_role_   │                           │
│                              │   resource       │                           │
│                              │(角色-资源关联)    │                           │
│                              └──────────────────┘                           │
│                                                                             │
│   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────────┐  │
│   │privilege_auth_   │1─*│privilege_auth_   │   │privilege_user_auth   │  │
│   │   info           │   │   menu           │   │(用户-权限归属关联)    │  │
│   │(权限归属信息)    │   │(权限-菜单映射)    │   └──────────────────────┘  │
│   └──────────────────┘   └──────────────────┘                              │
│                                                                             │
│   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────────┐  │
│   │person_division   │   │up_org_user       │   │account_record        │  │
│   │(人员地市归属)    │   │(上级机构用户)    │   │(账号操作记录)        │  │
│   └──────────────────┘   └──────────────────┘   └──────────────────────┘  │
│                                                                             │
│   ┌──────────────────┐   ┌──────────────────┐                              │
│   │sensitive_words   │   │sys_role_module_  │                              │
│   │(敏感词表)        │   │   rel(旧系统)    │                              │
│   └──────────────────┘   └──────────────────┘                              │
└─────────────────────────────────────────────────────────────────────────────┘

图例：1 = 一端  * = 多端  1────* = 一对多关系
```

---

## 二、核心表关系解读（小白版）

### 🏠 打比方：把数据库想象成一家大公司

| 数据库表 | 公司里的角色 | 干什么的 |
|---------|------------|---------|
| privilege_org_info | 公司部门 | 记录陕西省分公司、西安市分公司、宝鸡市分公司... |
| privilege_system_info | 业务系统 | 记录有哪些系统：门诊慢特病系统、综合查询系统... |
| privilege_menu_info | 功能菜单 | 记录系统里有哪些页面/按钮：申报管理、审核管理... |
| privilege_user_info | 员工档案 | 记录每个员工的基本信息：张三、李四... |
| privilege_role_info | 岗位 | 记录有哪些岗位：经办员、审核员、管理员... |
| privilege_org_system | 部门-系统订阅 | 记录哪个部门开通了哪个系统 |
| privilege_user_role | 员工-岗位分配 | 记录哪个员工担任了哪个岗位 |
| privilege_role_resource | 岗位-功能权限 | 记录哪个岗位能用哪些菜单 |
| privilege_user_auth | 员工-权限归属 | 记录员工的地市级权限范围 |

---

## 三、每张表详细字段说明

### 1. privilege_org_info（机构信息表）🏢

> 🏠 公司的"部门花名册"——每个分公司/支公司一条记录

| 字段 | 类型 | 说明 | 举例 |
|------|------|------|------|
| id | NVARCHAR | 机构唯一标识（主键，UUID） | "a1b2c3d4..." |
| code | NVARCHAR | 机构编码 | "86"=陕西省, "8601"=西安市 |
| name | NVARCHAR | 机构名称 | "陕西省分公司" |
| parent_id | NVARCHAR | 上级机构ID | 西安的parent_id指向陕西的id |
| address | NVARCHAR | 机构地址 | "西安市雁塔区..." |
| contacts | NVARCHAR | 联系人 | "王经理" |
| contact_number | NVARCHAR | 联系电话 | "029-88888888" |
| contact_email | NVARCHAR | 联系邮箱 | "xxx@picc.com.cn" |
| enable | INTEGER | 启用状态 | 1=启用, 0=禁用 |
| category_code | NVARCHAR | 分类代码 | 区分公司/支公司/营销部 |
| order_index | INTEGER | 排序序号 | 显示顺序 |
| remark | NVARCHAR | 备注信息 | |
| delete_at | TIMESTAMP | 软删除时间 | NULL=有效, 有值=已删除 |
| creator | NVARCHAR | 创建人 | "admin" |
| createtime | TIMESTAMP | 创建时间 | |
| modifier | NVARCHAR | 修改人 | |
| modifytime | TIMESTAMP | 修改时间 | |

**关键关系**：
- `parent_id` → `id`（自引用，形成机构树）
- 一条机构记录 → 对应多条 `privilege_org_system`（开通了多个系统）

---

### 2. privilege_system_info（系统信息表）💻

> 🏠 公司的"业务系统清单"——有哪些软件系统可供使用

| 字段 | 类型 | 说明 | 举例 |
|------|------|------|------|
| id | NVARCHAR | 系统唯一标识 | "459694197360955392" |
| sys_code | NVARCHAR | 系统编码 | "MZMTB" |
| sys_name | NVARCHAR | 系统名称 | "门诊慢特病业务管理系统" |
| enable | INTEGER | 启用状态 | 1=启用, 0=禁用 |
| delete_at | TIMESTAMP | 软删除时间 | |

**关键关系**：
- 一个系统 → 对应多条 `privilege_menu_info`（包含多个菜单）
- 一个系统 → 对应多条 `privilege_org_system`（被多个机构订阅）

---

### 3. privilege_menu_info（菜单信息表）📋

> 🏠 公司的"功能菜单清单"——系统里有哪些页面和按钮

| 字段 | 类型 | 说明 | 举例 |
|------|------|------|------|
| id | NVARCHAR | 菜单唯一标识 | |
| parent_id | NVARCHAR | 父菜单ID | 形成菜单树 |
| system_id | NVARCHAR | 所属系统ID | 指向system_info |
| code | NVARCHAR | 菜单编码 | |
| name | NVARCHAR | 菜单名称 | "申报管理" |
| menu_level | INTEGER | 菜单层级 | 1=一级, 2=二级... |
| menu_type | NVARCHAR | 菜单类型 | 目录/菜单/按钮 |
| is_sys_menu | INTEGER | 是否系统菜单 | |
| url | NVARCHAR | 请求地址 | "/apply/list" |
| enable | INTEGER | 启用状态 | |
| order_index | INTEGER | 排序序号 | |
| delete_at | TIMESTAMP | 软删除时间 | |

**关键关系**：
- `parent_id` → `id`（自引用，形成菜单树）
- `system_id` → `privilege_system_info.id`（属于哪个系统）
- 一条菜单 → 对应多条 `privilege_menu_service`（有多个接口服务）

---

### 4. privilege_org_system（机构-系统关联表）🔗

> 🏠 "哪个部门开通了哪个系统的哪些功能"的登记表

| 字段 | 类型 | 说明 | 举例 |
|------|------|------|------|
| id | NVARCHAR | 关联记录唯一标识 | |
| org_id | NVARCHAR | 机构ID | 指向org_info |
| system_id | NVARCHAR | 系统ID | 指向system_info |
| menu_id | NVARCHAR | 菜单ID | 指向menu_info |
| is_relates | NVARCHAR | 是否关联 | "1"=已关联, "0"=未关联 |
| delete_at | TIMESTAMP | 软删除时间 | |

**🏠 打比方**：
```
一条记录的意思是：
西安市分公司（org_id）+ 门诊慢特病系统（system_id）+ 申报管理菜单（menu_id）= 已开通 ✓

这就像一张"业务开通确认单"：
某个部门 + 某个系统 + 某个功能 = 是否开通
```

---

### 5. privilege_user_info（用户信息表）👤

> 🏠 "员工档案"——记录每个使用系统的员工信息

| 字段 | 类型 | 说明 | 举例 |
|------|------|------|------|
| id | NVARCHAR | 用户唯一标识 | |
| account | NVARCHAR | 登录账号 | "zhangsan" |
| name | NVARCHAR | 真实姓名 | "张三" |
| password | NVARCHAR | 密码（SM4加密） | 加密后的字符串 |
| sex | INTEGER | 性别 | 1=男, 0=女 |
| tel | NVARCHAR | 联系电话 | "13800138000" |
| email | NVARCHAR | 邮箱 | "zhangsan@picc.com" |
| id_num | NVARCHAR | 身份证号 | |
| org_id | NVARCHAR | 所属机构ID | 指向org_info |
| is_admin | INTEGER | 是否管理员 | 1=管理员, 0=普通用户 |
| enable | INTEGER | 启用状态 | 1=启用, 0=禁用 |
| password_changed | DATE | 密码最后修改时间 | |
| end_login | DATE | 最后登录时间 | |
| delete_at | TIMESTAMP | 软删除时间 | |

**关键关系**：
- `org_id` → `privilege_org_info.id`（员工属于哪个机构）
- 一个用户 → 对应多条 `privilege_user_role`（可以担任多个岗位）
- 一个用户 → 对应多条 `privilege_user_auth`（可以有多个权限归属）

---

### 6. privilege_role_info（角色信息表）🎭

> 🏠 "岗位清单"——经办员、审核员、管理员等岗位定义

| 字段 | 类型 | 说明 | 举例 |
|------|------|------|------|
| id | NVARCHAR | 角色唯一标识 | |
| code | NVARCHAR | 角色编码 | "OPERATOR" |
| name | NVARCHAR | 角色名称 | "经办员" |
| org_id | NVARCHAR | 所属机构ID | 同一角色名在不同机构是不同记录 |
| enable | INTEGER | 启用状态 | |
| remark | NVARCHAR | 描述信息 | |
| delete_at | TIMESTAMP | 软删除时间 | |

**🏠 关键理解**：同一个角色编码（如"经办员"）在不同机构是**不同的记录**（不同ID），因为每个机构可以自定义角色权限。

---

### 7. privilege_user_role（用户-角色关联表）👤🎭

> 🏠 "员工岗位任命书"——张三担任了经办员岗位

| 字段 | 类型 | 说明 |
|------|------|------|
| id | NVARCHAR | 关联记录唯一标识 |
| user_id | NVARCHAR | 用户ID |
| role_id | NVARCHAR | 角色ID |
| delete_at | TIMESTAMP | 软删除时间 |

---

### 8. privilege_role_resource（角色-资源关联表）🎭📋

> 🏠 "岗位职能说明书"——经办员岗位能使用哪些菜单

| 字段 | 类型 | 说明 |
|------|------|------|
| id | NVARCHAR | 关联记录唯一标识 |
| role_id | NVARCHAR | 角色ID |
| system_id | NVARCHAR | 系统ID |
| menu_id | NVARCHAR | 菜单ID |
| delete_at | TIMESTAMP | 软删除时间 |

---

### 9. privilege_auth_info（权限归属信息表）🔐

> 🏠 "权限类别清单"——定义不同的权限归属类型

| 字段 | 类型 | 说明 | 举例 |
|------|------|------|------|
| id | NVARCHAR | 权限归属唯一标识 | |
| name | NVARCHAR | 权限名称 | "西安经办权限" |
| code | NVARCHAR | 权限编码 | 医保编码或排序号 |
| enable | INTEGER | 启用状态 | 0=启用, 1=禁用 |
| shared | INTEGER | 是否共享 | 0=独有, 1=共享 |
| order_index | INTEGER | 排序 | |
| delete_at | TIMESTAMP | 软删除时间 | |

**🏠 打比方**：权限归属就像"你能管哪个片区"——西安市的经办员只能看西安的数据，宝鸡的只能看宝鸡的。

---

### 10. privilege_user_auth（用户-权限归属关联表）👤🔐

> 🏠 "员工管辖范围分配"——张三被分配了西安市的经办权限

| 字段 | 类型 | 说明 |
|------|------|------|
| id | NVARCHAR | 关联记录唯一标识 |
| user_id | NVARCHAR | 用户ID |
| auth_id | NVARCHAR | 权限归属ID |
| flag | NVARCHAR | 地市标识 |
| delete_at | TIMESTAMP | 软删除时间 |

---

### 11. privilege_auth_menu（权限-菜单映射表）🔐📋

> 🏠 "权限类别能看到哪些菜单"——西安经办权限能看到哪些一级菜单

| 字段 | 类型 | 说明 |
|------|------|------|
| id | NVARCHAR | 映射记录唯一标识 |
| auth_id | NVARCHAR | 权限归属ID |
| parent_menu_id | NVARCHAR | 父级菜单ID |
| flag | INTEGER | 归属地市 |
| enable | INTEGER | 启用状态 |
| delete_at | TIMESTAMP | 软删除时间 |

---

### 12. privilege_menu_service（菜单服务信息表）📋🔌

> 🏠 "菜单对应的接口清单"——申报管理这个菜单调用了哪些后端接口

| 字段 | 类型 | 说明 |
|------|------|------|
| id | NVARCHAR | 记录唯一标识 |
| menu_id | NVARCHAR | 菜单ID |
| service_url | NVARCHAR | 接口URL |
| service_name | NVARCHAR | 接口名称 |
| enable | INTEGER | 启用状态 |
| delete_at | TIMESTAMP | 软删除时间 |

---

### 13. person_division（人员地市归属表）🗺️

> 🏠 "员工在哪个窗口办公"——记录员工的实际办公地点和服务窗口

| 字段 | 类型 | 说明 |
|------|------|------|
| id | NVARCHAR | 记录唯一标识 |
| account | NVARCHAR | 账号 |
| flag | NVARCHAR | 地市标识 |
| unitcode | NVARCHAR | 服务窗口编码 |
| unitname | NVARCHAR | 服务窗口名称 |
| persontype | NVARCHAR | 人员身份编码 |
| persontypename | NVARCHAR | 人员身份名称 |
| identity | NVARCHAR | 身份类型：1=支公司, 2=分公司 |
| isdownload | NVARCHAR | 是否有下载权限 |
| isfilingback | NVARCHAR | 是否有备案撤销权限 |
| isyb | NVARCHAR | 是否医保账号 |
| ismanual | NVARCHAR | 是否手动分配权限（榆林） |
| dr | SMALLINT | 逻辑删除：0=有效, 1=删除 |

---

### 14. up_org_user（上级机构用户表）🏢👤

> 🏠 "上级部门员工信息"——存储从上级系统同步过来的用户信息

| 字段 | 类型 | 说明 |
|------|------|------|
| id | NVARCHAR | 记录唯一标识 |
| userAccount | NVARCHAR | 用户账号 |
| userFullname | NVARCHAR | 用户全名 |
| userPassword | NVARCHAR | 用户密码 |
| userAccountEnabled | NVARCHAR | 账号是否启用 |
| userAccountLocked | NVARCHAR | 账号是否锁定 |
| hosLevel | NVARCHAR | 所属医院级别 |
| admdvs | NVARCHAR | 医保区划 |
| accountversion | INTEGER | 延安复审版本号 |
| isreview | INTEGER | 延安复审是否开启 |

---

### 15. account_record（账号操作记录表）📝

> 🏠 "账号操作日志"——记录谁在什么时候启用/禁用了哪个账号

| 字段 | 类型 | 说明 |
|------|------|------|
| id | NVARCHAR | 记录唯一标识 |
| account | NVARCHAR | 被操作的账号 |
| accountid | NVARCHAR | 被操作的用户ID |
| reason | NVARCHAR | 操作原因 |
| updateaccount | NVARCHAR | 操作人 |
| type | NVARCHAR | 操作类型 |
| enable | NVARCHAR | 状态：T=启用, F=禁用 |

---

### 16. sensitive_words（敏感词表）🚫

> 🏠 "账号命名黑名单"——创建账号时不能包含的词汇

| 字段 | 类型 | 说明 |
|------|------|------|
| id | NVARCHAR | 记录唯一标识 |
| word | NVARCHAR | 敏感词（如admin、root、system） |
| enable | INTEGER | 启用状态 |
| dr | SMALLINT | 逻辑删除 |

---

### 17. sys_role_module_rel（旧系统角色-模块关系表）📦

> 🏠 "旧办公楼的文件柜索引"——数据迁移用的旧表，记录旧系统中角色和模块的对应关系

| 字段 | 类型 | 说明 |
|------|------|------|
| role_id | NVARCHAR | 旧角色ID |
| module_id | NVARCHAR | 旧模块ID |

---

## 四、核心查询路径

### 🔍 用户能做什么？—— 五表关联查询

```sql
-- 查询某用户能看到的所有菜单（核心权限查询）
SELECT DISTINCT m.*
FROM privilege_user_info u
  JOIN privilege_user_role ur ON u.id = ur.user_id
  JOIN privilege_role_resource rr ON ur.role_id = rr.role_id
  JOIN privilege_menu_info m ON rr.menu_id = m.id
WHERE u.id = '用户ID'
  AND ur.delete_at IS NULL
  AND rr.delete_at IS NULL
  AND m.delete_at IS NULL
  AND m.enable = 1;

-- 但实际还要加上机构维度：
-- 机构开通了哪些菜单（privilege_org_system）
-- 用户的权限归属（privilege_user_auth）
-- 最终可见菜单 = 角色菜单 ∩ 机构菜单 ∩ 权限归属菜单
```

### 🏠 查询路径图解

```
用户（张三）
  │
  ├─→ 用户-角色表 ──→ 角色（经办员）
  │                      │
  │                      └─→ 角色-资源表 ──→ 菜单A、菜单B、菜单C
  │
  ├─→ 用户所属机构 ──→ 机构-系统表 ──→ 菜单A、菜单B、菜单D
  │
  └─→ 用户-权限归属表 ──→ 权限-菜单表 ──→ 菜单A
  │
  └─→ 最终可见：菜单A（三者交集）
```

---

## 五、表设计问题与建议

| 问题 | 严重程度 | 说明 | 建议 |
|------|---------|------|------|
| 所有表用UUID做主键 | 🟡 中等 | UUID作为主键影响索引性能，尤其在大数据量时 | 考虑雪花算法生成有序ID |
| 软删除无统一规范 | 🟡 中等 | 有的表用delete_at，有的用dr，不统一 | 统一为delete_at |
| person_division字段过多 | 🟠 改进 | isdownload/isfilingback/isyb/ismanual等都是地市个性化字段 | 抽取为JSON或独立配置表 |
| up_org_user包含密码字段 | 🔴 严重 | 上级系统同步的用户密码明文存储 | 不应同步密码，只做身份映射 |
| org_system缺少唯一约束 | 🟡 中等 | 同一机构+系统+菜单可以重复插入 | 添加联合唯一约束(org_id, system_id, menu_id) |
| 缺少创建/修改时间索引 | 🟡 中等 | 大量按时间排序的查询没有索引 | 为createtime/modifytime添加索引 |

---

## 六、本章总结

- 项目共有**17张数据库表**，其中15张为业务表、2张为旧系统迁移表
- 核心权限模型为**用户→角色→菜单** + **机构→系统→菜单** + **用户→权限归属→菜单**三维度交叉
- 所有业务表使用**软删除**（delete_at字段），不物理删除数据
- 表命名规范为`privilege_`前缀，但person_division和up_org_user例外（历史遗留）
- BaseEntity提供公共字段：id, creator, createtime, modifier, modifytime

---

📎 **延伸阅读**：
- [API-Mapper-数据模型](picc-mzmtb-user-API-Mapper-数据模型.md) - 数据库表对应的Mapper XML和API接口层说明
- [深度解析-菜单与系统管理](picc-mzmtb-user-深度解析第四章-菜单与系统管理.md) - 菜单树的递归构建原理
- [picc-mzmtb-server-数据模型解析.md](picc-mzmtb-server-数据模型解析.md) 📌(业务服务) - 业务服务的213个Mapper和核心表详解

