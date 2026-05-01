# PICC 权限管理系统 - API层、Mapper层、数据模型详解

> 🎓 **学习目标**：深入理解系统的前后端接口契约、数据库操作细节、以及数据如何在各层之间流转

---

## 🌐 API层 - 前后端对接接口

> 🏠 就像公司前台接待处，所有来找公司的访客都要先在前台登记
> - `@RestController` = 前台接待窗口，专门接电话/收表格的
> - `@RequestMapping/@PostMapping` = 窗口门牌号，告诉别人去哪办事
> - `@RequestBody` = 访客填的业务申请表

---

### 📋 MenuInfoApi - 菜单信息接口 (`/privilege/menu`)

> 🎯 **一句话**：管理系统的"导航菜单"，让用户知道能从系统里做什么

#### 接口清单

| 接口 | 方法 | 路径 | 一句话 |
|------|------|------|--------|
| 创建菜单 | POST | `/create` | 添加新菜单项 |
| 编辑菜单 | POST | `/update` | 修改菜单内容 |
| 删除菜单 | POST | `/deleteById` | 移除菜单项 |
| 查询菜单详情 | POST | `/getDetail` | 查看单个菜单信息 |
| 查询菜单列表 | POST | `/queryMenusBySystemId` | 获取某系统下的所有菜单 |
| 获取菜单树 | POST | `/getMenuTree` | 获取树形结构的菜单 |
| 启用/禁用菜单 | POST | `/enable` | 开关菜单功能 |
| 修改菜单服务 | POST | `/reviseServices` | 增删改菜单关联的服务接口 |
| 查询服务树 | POST | `queryServicesTree` | 获取服务接口的树形结构 |
| 查询子级菜单 | POST | `queryChildrenMenus` | 获取某个菜单的子菜单 |
| 模糊查询服务 | POST | `queryChildrenServicesMenus` | 搜索菜单下的服务 |
| 数据统计 | POST | `queryDataStatistics` | 统计菜单和服务数量 |

#### 重点接口详解

##### 🔹 POST /create - 创建菜单
```java
// 第30行
public ApiResponse createMenu(@RequestBody PrivilegeMenuInfoVo vo)
```
- **请求体**：PrivilegeMenuInfoVo（包含parentId、systemId、name、menuType等）
- **谁来调用**：管理员在菜单管理页面点击"新增菜单"按钮
- **返回值**：创建成功返回菜单ID

##### 🔹 POST /queryMenusBySystemId - 查询菜单列表
```java
// 第62行
public ApiResponse queryMenusBySystemId(@RequestBody PrivilegeMenuInfoVo vo)
```
- **请求体**：需要传入 systemId（系统ID）
- **谁来调用**：前端加载菜单管理列表时
- **返回值**：该系统下的所有菜单列表
- **权限**：需要管理员权限

---

### 👥 RoleInfoApi - 角色信息接口 (`/privilege/role`)

> 🎯 **一句话**：管理系统里的"工作岗位"，决定每个人能干什么

#### 接口清单

| 接口 | 方法 | 路径 | 一句话 |
|------|------|------|--------|
| 创建角色 | POST | `/create` | 新增工作岗位 |
| 更新角色 | POST | `/update` | 修改岗位信息 |
| 删除角色 | POST | `/delete` | 移除岗位 |
| 角色详情 | POST | `/getDetail` | 查看岗位详情 |
| 按机构查角色 | POST | `/queryRolesByOrgId` | 查看某机构的所有岗位 |
| 角色树 | POST | `/queryRoleTreeByOrgId` | 获取岗位的树形结构 |
| 权限树 | POST | `/queryAuthTreeByRoleId` | 查看某岗位能访问什么 |
| 设置资源 | POST | `/setResources` | 给岗位分配能访问的菜单 |
| 查询资源 | POST | `/queryResourcesByRoleId` | 查看岗位已分配的资源 |
| 删除资源 | POST | `/deleteResourcesByIds` | 移除岗位的某些资源 |
| 启用/禁用 | POST | `/updateEnable` | 开关岗位功能 |
| 批量删除 | POST | `/deleteRolesByIds` | 一次删除多个岗位 |

#### 重点接口详解

##### 🔹 POST /create - 创建角色
```java
// 第31行
public ApiResponse<String> createRole(@RequestBody @Validated RoleCreateVo roleCreateVo)
```
- **请求体**：RoleCreateVo
  - `orgId`（必填）- 所属机构ID
  - `name`（必填）- 角色名称
  - `enable`（必填）- 启用状态
  - `code` - 角色编码
  - `remark` - 角色描述
  - `menuIds` - 关联的菜单ID列表
- **谁来调用**：管理员在"角色管理"页面点击"新增角色"
- **返回值**：成功返回角色ID，失败返回错误信息

##### 🔹 POST /setResources - 设置角色资源
```java
// 第98行
public ApiResponse<String> setResources(@RequestBody @Validated ResourceVo resouceVo)
```
- **请求体**：ResourceVo
  - `roleId`（必填）- 角色ID
  - `systemId`（必填）- 系统ID
  - `menuIds` - 要分配的菜单ID列表
- **谁来调用**：管理员在角色详情页勾选菜单权限后点击"保存"
- **核心逻辑**：清空旧资源 → 添加新资源

---

### 🏢 OrgInfoApi - 机构信息接口 (`/privilege/org`)

> 🎯 **一句话**：管理系统的"部门/子公司"，组织架构的树形结构

#### 接口清单

| 接口 | 方法 | 路径 | 一句话 |
|------|------|------|--------|
| 创建机构 | POST | `/create` | 新增部门 |
| 更新机构 | POST | `/update` | 修改部门信息 |
| 删除机构 | POST | `/deleteById` | 移除部门 |
| 批量删除 | POST | `/deleteOrgsByIds` | 一次删除多个部门 |
| 机构详情 | POST | `/getDetail` | 查看部门详情 |
| 查询机构列表 | POST | `/queryOrgs` | 分页查询所有机构 |
| 按ID查机构 | GET | `/queryOrgsById` | 获取某机构及其子机构 |
| 配置系统订阅 | POST | `/setSystemResources` | 给机构分配系统 |
| 查询系统订阅 | POST | `/querySystemsByOrgId` | 查看机构订阅了哪些系统 |
| 删除系统订阅 | POST | `/deleteSystemsByIds` | 取消机构订阅的系统 |
| 机构树 | POST | `/getOrgTree` | 获取机构树形图 |
| 部分机构树 | POST | `/getPartOrgTree` | 获取部分机构树（用户归属） |
| 更改机构状态 | POST | `/updateOrgsByIds` | 启用/禁用机构 |
| 创建机构+系统 | POST | `/setOrgSystemResources` | 创建机构并分配系统 |
| 更新机构+系统 | POST | `/updateOrgSystemResources` | 更新机构并更新系统 |
| 获取系统列表 | POST | `/getSystemList` | 获取某机构的系统列表 |

#### 重点接口详解

##### 🔹 POST /create - 创建机构
```java
// 第36行
public ApiResponse create(@RequestBody OrgInfoVo orgInfoVo)
```
- **请求体**：OrgInfoVo
  - `code` - 机构编码
  - `name`（必填）- 机构名称
  - `parentId` - 父级机构ID（构成树形）
  - `address` - 地址
  - `contacts` - 联系人
  - `contactNumber` - 联系电话
  - `enable` - 启用状态
- **谁来调用**：管理员在"机构管理"页面新增部门

##### 🔹 POST /setSystemResources - 配置机构系统订阅
```java
// 第95行
public ApiResponse setSystemResources(@RequestBody OrgSysResourceDto orgSysResourceDto)
```
- **请求体**：OrgSysResourceDto
  - `orgId` - 机构ID
  - `sysResourcesVo` - 系统资源信息
- **谁来调用**：管理员给机构分配可用的子系统

---

### 🖥️ SysInfoApi - 系统信息接口 (`/privilege/sys`)

> 🎯 **一句话**：管理系统里的"子系统列表"，比如慢病系统、处方系统等

#### 接口清单

| 接口 | 方法 | 路径 | 一句话 |
|------|------|------|--------|
| 查询系统列表 | POST | `/list` | 获取所有子系统 |

```java
// 第31行
public ApiResponse<ResultPage<PrivilegeSystemInfoDto>> querySysInfo(@RequestBody PrivilegeSystemInfoVo vo)
```
- **请求体**：PrivilegeSystemInfoVo（包含分页信息）
- **谁来调用**：前端加载系统选择下拉框
- **返回值**：分页的系统列表（sysCode、sysName、enable等）

---

### 👤 UserInfoApi - 人员信息接口 (`/privilege/user`)

> 🎯 **一句话**：管理系统里的"员工账号"，决定谁能登录系统

#### 接口清单

| 接口 | 方法 | 路径 | 一句话 |
|------|------|------|--------|
| 创建人员 | POST | `/create` | 新增员工账号 |
| 更新人员 | POST | `/update` | 修改员工信息 |
| 删除人员 | POST | `/deleteById` | 删除单个员工 |
| 批量删除 | POST | `/deleteUsersByIds` | 一次删除多个员工 |
| 人员详情 | POST | `/getDetail` | 查看员工详情 |
| 查询人员列表 | POST | `/queryUsers` | 分页查询系统人员 |
| 按机构查人员 | POST | `/queryUsersByOrgIds` | 查看某机构的所有员工 |
| 配置人员角色 | POST | `/setRoles` | 给员工分配工作岗位 |
| 删除人员角色 | GET | `/deleteRolesByIds` | 移除员工的工作岗位 |
| 查询人员角色 | POST | `/queryRolesByUserId` | 查看某员工有哪些岗位 |
| 启用/禁用人员 | POST | `/enableUser` | 开关员工账号 |
| 重置密码 | POST | `/resetPassword` | 把密码改回默认 |

#### 重点接口详解

##### 🔹 POST /create - 创建人员
```java
// 第34行
ApiResponse create(@RequestBody PrivilegeUserInfoDto privilegeUserInfoDto)
```
- **请求体**：PrivilegeUserInfoDto
  - `account`（必填）- 登录账号
  - `name`（必填）- 员工姓名
  - `orgId`（必填）- 所属机构
  - `tel` - 手机号
  - `email` - 邮箱
  - `idNum` - 身份证号
  - `roleIds` - 关联的角色ID数组
- **谁来调用**：管理员在"用户管理"页面新增员工
- **返回值**：创建成功返回用户ID

##### 🔹 POST /setRoles - 配置人员角色
```java
// 第93行
ApiResponse setRoles(@RequestBody PrivilegeUserRoleInfoDto privilegeUserRoleInfoDto)
```
- **请求体**：PrivilegeUserRoleInfoDto
  - `userId` - 员工ID
  - `roleIds` - 角色ID数组
- **谁来调用**：管理员给员工分配工作岗位

---

### 🔄 MoveApi - 数据迁移接口 (`/privilege/move`)

> 🎯 **一句话**：老系统数据迁移到新系统时用的临时接口

| 接口 | 方法 | 路径 | 一句话 |
|------|------|------|--------|
| 迁移角色和资源 | POST | `/moveRoleAndResource` | 从旧系统搬角色数据 |
| 迁移用户角色 | POST | `/moveUserRole` | 从旧系统搬用户角色关系 |
| 密码MD5回退 | POST | `/passwordBackMD5` | 密码加密方式转换 |

---

## 🗄️ Mapper层 - 数据库操作详解

> 🏠 就像仓库管理员的操作手册，告诉系统怎么从数据库（仓库）里存取货物
> - `Mapper XML` = 仓库管理员的操作手册
> - `<select>` = 从仓库拿东西出来
> - `<insert>` = 把新东西放进仓库
> - `<update>` = 改变仓库里东西的属性
> - `<delete>` = 把东西从仓库移除

---

### Mapper: PrivilegeMenuInfoDao.xml → 表: privilege_menu_info

> 🏠 就像仓库里的**菜单货架**，每层货架放什么菜单都有标签

#### SQL查询清单

| SQL ID | 做什么 | 复杂度 |
|--------|--------|--------|
| getMenuOrgTree | 获取菜单和机构树 | ⭐ |
| queryMenusBySystemId | 按系统ID查菜单列表 | ⭐⭐ |
| queryMenusBySystemIdAndOrgId | 按系统和机构查菜单 | ⭐⭐⭐ |
| queryInfo | 精确查询菜单信息 | ⭐ |
| getChildrenMenus | 获取子级菜单 | ⭐⭐ |
| queryServicesTree | 查询服务树 | ⭐⭐ |
| selectMenuInfoById | 按ID查菜单详情 | ⭐ |
| querySystemMenuNum | 统计某机构菜单数量 | ⭐⭐ |
| queryauthMenuNum | 统计有权限的菜单数 | ⭐⭐ |
| queryParentMenuIdByRoleId | 按角色查父级菜单ID | ⭐⭐ |

#### 重点SQL拆解

**queryMenusBySystemId - 按系统查菜单（行58-79）**
```sql
SELECT id, system_id, parent_id, code, name, ...
FROM privilege_menu_info
WHERE id IN (
    -- 先找出这些菜单的ID
    SELECT m.id 
    FROM privilege_menu_info m
    LEFT JOIN privilege_org_system o ON m.id = o.menu_id
    WHERE m.system_id = #{systemId}
    AND m.name = #{name}        -- 可选：按名称过滤
    AND o.org_id = #{orgId}     -- 可选：按机构过滤
)
AND delete_at IS NULL
ORDER BY parent_id, order_index  -- 按层级和排序号排列
```

**大白话**：先从菜单表里挑出符合条件的菜单ID（可能还要关联机构表），然后把这些菜单按"爸爸在前、排序号小的在前"的顺序列出来。

#### 动态SQL说明
- `<if test="systemId != null">` = 如果传了系统ID就用上这个条件
- `<if test="name != null">` = 如果传了名称就过滤
- `ORDER BY parent_id, order_index` = 按层级和排序号排列成树

---

### Mapper: PrivilegeUserInfoDao.xml → 表: privilege_user_info

> 🏠 就像仓库里的**员工档案柜**，每个人的信息都存这里

#### SQL查询清单

| SQL ID | 做什么 | 复杂度 |
|--------|--------|--------|
| selectUserInfoById | 按ID查员工档案 | ⭐ |
| queryUserInfo | 条件查询员工 | ⭐⭐ |
| selectByAccount | 按账号查员工 | ⭐ |
| selectUsersByOrgIds | 按机构ID列表查员工 | ⭐⭐ |

#### 重点SQL拆解

**queryUserInfo - 条件查询员工（行55-80）**
```sql
SELECT id, account, name, password, sex, tel, email, org_id, ...
FROM privilege_user_info
WHERE delete_at IS NULL
-- 如果传了账号，就按账号查
AND account = #{account}
-- 如果传了姓名，就模糊匹配
AND name LIKE '%' || #{name} || '%'
-- 如果传了机构ID列表，就查这些机构的员工
AND org_id IN (#{id1}, #{id2}, #{id3})
ORDER BY createtime DESC  -- 最新创建的在最前面
```

**大白话**：从员工档案柜里，按条件找出员工名单。账号要精确匹配，姓名可以模糊搜索。

#### 动态SQL说明
- `<if test="account != null">` = 账号不为空才加这个条件
- `LIKE '%' || #{name} || '%'` = 姓名模糊匹配
- `<foreach>` = 遍历机构ID列表，构建 IN 查询

---

### Mapper: PrivilegeOrgInfoDao.xml → 表: privilege_org_info

> 🏠 就像仓库里的**部门架构图**，显示谁是谁的下属

#### SQL查询清单

| SQL ID | 做什么 | 复杂度 |
|--------|--------|--------|
| selectOrgInfo | 条件查询机构 | ⭐⭐ |
| selectOrgInfoById | 按ID查机构（含子机构） | ⭐ |
| selectOrgInfoByName | 按名称查机构 | ⭐ |
| selectOrgInfoByParentId | 按父ID查子机构 | ⭐ |
| selectOrg | 按ID查单个机构 | ⭐ |
| selectByOrgIds | 按机构ID列表查 | ⭐⭐ |
| selectOrgByCode | 按编码查机构 | ⭐ |
| selectEnableOrgInfoByParentId | 查询启用的子机构 | ⭐ |

#### 重点SQL拆解

**selectOrgInfo - 条件查询机构（行23-36）**
```sql
SELECT id, code, name, parent_id, address, contacts, ...
FROM privilege_org_info
WHERE 1=1 AND delete_at IS NULL
-- 如果传了编码，就按编码过滤
AND code = #{code}
-- 如果传了名称，就按名称过滤
AND name = #{name}
-- 如果传了状态，就按状态过滤
AND enable = #{enable}
```

**大白话**：从部门图里按条件找部门。可以用编码、名称或状态来筛选。

---

### Mapper: PrivilegeSystemInfoDao.xml → 表: privilege_system_info

> 🏠 就像仓库里的**系统货架**，放着各种子系统

#### SQL查询清单

| SQL ID | 做什么 | 复杂度 |
|--------|--------|--------|
| selectByName | 按名称查系统 | ⭐ |
| selectById | 按ID查系统 | ⭐ |

#### 动态SQL说明
- 都很简单，没有复杂的动态SQL
- `delete_at IS NULL` = 只查没被删除的记录

---

### Mapper: PrivilegeMenuServiceDao.xml → 表: privilege_menu_service

> 🏠 就像仓库里的**菜单服务清单**，列出一个菜单能干哪些事

#### SQL查询清单

| SQL ID | 做什么 | 复杂度 |
|--------|--------|--------|
| queryChildrenServicesMenus | 查询子服务 | ⭐⭐ |
| queryAuthInterfaceNum | 统计授权接口数量 | ⭐⭐⭐ |

#### 重点SQL拆解

**queryChildrenServicesMenus - 模糊查询子服务（行32-47）**
```sql
SELECT id, menu_id, service_url, service_name, enable, ...
FROM privilege_menu_service
WHERE delete_at IS NULL
AND menu_id = #{menuId}                    -- 属于哪个菜单
AND (
    service_url LIKE '%' || #{serviceKey} || '%'  -- URL模糊匹配
    OR service_name LIKE '%' || #{serviceKey} || '%'  -- 名称模糊匹配
)
```

**大白话**：从服务清单里，找出属于某个菜单的服务，支持按URL或名称搜索。

---

### Mapper: PrivilegeRoleInfoDao.xml → 表: privilege_role_info

> 🏠 就像仓库里的**岗位手册架**，每本手册规定一个岗位的职责

#### SQL查询清单

| SQL ID | 做什么 | 复杂度 |
|--------|--------|--------|
| queryRolesByOrgidAndRolename | 按机构和名称查岗位 | ⭐⭐ |
| queryRoleByID | 按ID查岗位 | ⭐ |
| queryRoleByIds | 按ID列表查岗位 | ⭐⭐ |
| queryOrgName | 查询机构名称 | ⭐ |
| queryRolesByOrgidListAndRolename | 按机构列表和名称查 | ⭐⭐ |
| queryRoleByOrgIdAndCode | 按机构和编码查岗位 | ⭐⭐ |

#### 重点SQL拆解

**queryRolesByOrgidListAndRolename - 按机构列表和名称查询（行44-58）**
```sql
SELECT * FROM privilege_role_info
WHERE delete_at IS NULL
AND org_id IN ( #{orgId1}, #{orgId2}, ... )  -- 在这些机构里
AND name LIKE '%' || #{roleName} || '%'     -- 名称模糊匹配
ORDER BY createtime DESC
```

**大白话**：找出属于某些机构、名称包含某关键词的所有岗位。

---

### Mapper: PrivilegeUserRoleInfoDao.xml → 表: privilege_user_role

> 🏠 就像仓库里的**员工-岗位对应表**，记录谁在什么岗位上

#### SQL查询清单

| SQL ID | 做什么 | 复杂度 |
|--------|--------|--------|
| selectUserRoleInfoById | 按ID查用户角色关系 | ⭐ |
| selectByUserIdAndRoleId | 按用户ID和角色ID查 | ⭐ |

---

### Mapper: PrivilegeAuthInfoDao.xml → 表: privilege_auth_info

> 🏠 就像仓库里的**权限清单本**，记录有哪些权限

#### SQL查询清单

| SQL ID | 做什么 | 复杂度 |
|--------|--------|--------|
| queryAuthById | 按ID查权限 | ⭐ |
| queryAuthInfo | 条件查权限 | ⭐⭐ |
| queryAuthListByMenuId | 按菜单ID查权限列表 | ⭐⭐ |
| queryAuthListByRoleIdAndAuthId | 按角色和权限ID查 | ⭐⭐⭐ |
| queryAuthListByUserId | 按用户查权限列表 | ⭐⭐ |

#### 重点SQL拆解

**queryAuthListByRoleIdAndAuthId - 按角色和权限查询（行89-124）**
```sql
WITH menuList AS (
    -- 先找出这个角色能访问的菜单的父级ID
    SELECT DISTINCT pmi.parent_id
    FROM privilege_menu_info pmi
    LEFT JOIN privilege_role_resource prr ON pmi.id = prr.menu_id
    WHERE prr.role_id IN ( #{roleId1}, #{roleId2}, ... )
)
SELECT pai.id, pai.name, pai.code, pai.shared, pam.flag
FROM privilege_auth_info pai
LEFT JOIN privilege_auth_menu pam ON pai.id = pam.auth_id
WHERE pai.id IN ( #{authId1}, #{authId2}, ... )
ORDER BY pai.id
```

**大白话**：
1. 先找出指定角色们能访问的所有菜单的父级
2. 然后查出这些父级对应的权限
3. 再从权限清单里挑出指定的权限

---

### Mapper: PrivilegeRoleResourceDao.xml → 表: privilege_role_resource

> 🏠 就像仓库里的**岗位-资源分配表**，规定每个岗位能访问哪些菜单

#### SQL查询清单

| SQL ID | 做什么 | 复杂度 |
|--------|--------|--------|
| queryResourcesByRoleIds | 按角色ID列表查资源 | ⭐⭐ |
| queryResourcesByRoleId | 按单个角色查资源 | ⭐ |
| queryResourcesByIds | 按资源ID列表查 | ⭐⭐ |
| querySystemId | 查询角色关联的系统ID | ⭐ |

---

### Mapper: PrivilegeOrgSystemDao.xml → 表: privilege_org_system

> 🏠 就像仓库里的**机构-系统订阅表**，记录哪个机构订阅了哪些系统

#### SQL查询清单

| SQL ID | 做什么 | 复杂度 |
|--------|--------|--------|
| selectOrgSysInfo | 按机构查订阅的系统 | ⭐ |
| selectByIds | 按ID列表查订阅 | ⭐⭐ |
| selectOrgSysInfoBySysId | 按系统查订阅的机构 | ⭐ |
| selectOrgSysInfoByOrgSysId | 按机构和系统查 | ⭐ |
| queryOrgSysInfo | 查询已关联的系统 | ⭐ |

---

### Mapper: PrivilegeUserAuthDao.xml → 表: privilege_user_auth

> 🏠 就像仓库里的**用户-权限对应表**，记录每个用户有哪些权限

#### SQL查询清单

| SQL ID | 做什么 | 复杂度 |
|--------|--------|--------|
| queryUserAuthList | 查询用户权限列表 | ⭐⭐ |

---

### Mapper: SysUserRoleRelDao.xml → 表: sys_user_role_rel

> 🏠 就像仓库里的**旧版用户-角色对应表**（用于数据迁移）

#### SQL查询清单

| SQL ID | 做什么 | 复杂度 |
|--------|--------|--------|
| queryAllSysUserRoleRel | 查询所有旧版关系 | ⭐ |
| selectOrgIdByUserId | 根据用户查机构ID | ⭐⭐ |

---

### Mapper: SysRoleModuleRelDao.xml → 表: sys_role_module_rel

> 🏠 就像仓库里的**旧版岗位-模块对应表**（用于数据迁移）

#### SQL查询清单

| SQL ID | 做什么 | 复杂度 |
|--------|--------|--------|
| queryResourcesByRoleIds | 按角色查模块资源 | ⭐ |
| moveRoleResources | 迁移旧版岗位数据 | ⭐⭐⭐ |

#### 重点SQL拆解

**moveRoleResources - 迁移旧版岗位（行22-35）**
```sql
SELECT DISTINCT sr.id, sr.role_name AS name, sr.role_code AS code,
       sr.role_description AS remark,
       (CASE sr.status WHEN 1 THEN 0 WHEN 0 THEN 1 END) AS enable,  -- 状态反转
       tu.user_name AS creator,
       dept.dept_id AS org_id
FROM sys_role sr
LEFT JOIN sys_user_role_rel surr ON sr.id = surr.role_id
LEFT JOIN t_user tu ON tu.user_id = sr.create_author
LEFT JOIN t_user_dept ud ON ud.user_id = surr.user_id
LEFT JOIN t_dept dept ON dept.dept_code = ud.dept_code
WHERE org_id IS NOT NULL
ORDER BY id
```

**大白话**：从旧系统的好几个表里联合查出岗位信息，还要把状态值反转（1变0、0变1），然后关联出创建人信息和所属机构。

---

## 📋 数据模型 - 数据怎么流转

> 🏠 就像货物在仓库里的流转过程
> - `PO(Persistent Object)` = 仓库里的**原装货物**，原封不动从数据库拿出来
> - `DTO(Data Transfer Object)` = **运输途中打包好的货物**，精简后适合传输
> - `VO(View Object)` = **摆在货架上的展示品**，给前端看的样子

---

### 🔷 PO层 - 持久化对象（数据库原样）

#### PrivilegeUserInfo - 人员信息表
> 🏠 就像公司的**员工档案卡**

| 字段 | 类型 | 含义 | 生活比喻 |
|------|------|------|----------|
| id | String | 主键 | 档案编号 |
| account | String | 登录账号 | 工号 |
| name | String | 姓名 | 姓名 |
| password | String | 密码（加密） | 锁的密码 |
| sex | Integer | 性别(1男0女) | 性别 |
| tel | String | 电话 | 手机号 |
| email | String | 邮箱 | 邮箱地址 |
| idNum | String | 身份证号 | 身份证 |
| orgId | String | 所属机构ID | 所属部门 |
| isAdmin | Integer | 是否管理员 | 是不是领导 |
| enable | Integer | 启用状态 | 在职/离职 |
| remark | String | 备注 | 备注信息 |
| deleteAt | LocalDateTime | 删除时间 | 归档时间 |

**数据流转**：数据库 → Service层 → 可能转换为DTO → 返回前端

---

#### PrivilegeOrgInfo - 机构信息表
> 🏠 就像公司的**组织架构图**

| 字段 | 类型 | 含义 | 生活比喻 |
|------|------|------|----------|
| id | String | 主键 | 部门编号 |
| code | String | 机构编码 | 部门代码 |
| name | String | 机构名称 | 部门名称 |
| parentId | String | 父级ID | 上级部门 |
| address | String | 地址 | 办公地址 |
| contacts | String | 联系人 | 负责人 |
| contactNumber | String | 联系电话 | 联系方式 |
| contactEmail | String | 联系邮箱 | 邮箱 |
| enable | Integer | 启用状态 | 部门状态 |
| categoryCode | String | 分类代码 | 部门类型 |
| orderIndex | Integer | 排序号 | 显示顺序 |
| remark | String | 备注 | 说明 |

**数据流转**：前端提交 → VO → Service处理 → PO存储 → 数据库

---

#### PrivilegeMenuInfo - 菜单信息表
> 🏠 就像公司的**导航菜单栏**

| 字段 | 类型 | 含义 | 生活比喻 |
|------|------|------|----------|
| id | String | 主键 | 菜单编号 |
| parentId | String | 父级ID | 上级菜单 |
| systemId | String | 所属系统ID | 属于哪个子系统 |
| code | String | 菜单编码 | 菜单代码 |
| name | String | 菜单名称 | 显示名称 |
| menuLevel | Integer | 菜单层级 | 第几级菜单 |
| menuType | String | 菜单类型 | 按钮/链接/目录 |
| isSysMenu | Integer | 是否系统菜单 | 系统内置/自定义 |
| url | String | 请求地址 | 跳转链接 |
| enable | Integer | 启用状态 | 显示/隐藏 |
| orderIndex | Integer | 排序号 | 显示顺序 |

**数据流转**：管理员配置 → VO → Service → PO → 数据库

---

#### PrivilegeMenuService - 菜单服务表
> 🏠 就像菜单项的**操作手册**

| 字段 | 类型 | 含义 | 生活比喻 |
|------|------|------|----------|
| id | String | 主键 | 操作编号 |
| menuId | String | 所属菜单ID | 属于哪个菜单 |
| serviceUrl | String | 接口URL | 操作入口 |
| serviceName | String | 接口名称 | 操作名称 |
| enable | Integer | 启用状态 | 可用/不可用 |

---

#### PrivilegeRoleInfo - 角色信息表
> 🏠 就像公司的**岗位说明书**

| 字段 | 类型 | 含义 | 生活比喻 |
|------|------|------|----------|
| id | String | 主键 | 岗位编号 |
| code | String | 角色编码 | 岗位代码 |
| orgId | String | 所属机构ID | 属于哪个部门 |
| name | String | 角色名称 | 岗位名称 |
| enable | Integer | 启用状态 | 在用/停用 |
| remark | String | 描述 | 岗位职责 |

---

#### PrivilegeSystemInfo - 系统信息表
> 🏠 就像公司的**子系统清单**

| 字段 | 类型 | 含义 | 生活比喻 |
|------|------|------|----------|
| id | String | 主键 | 系统编号 |
| sysCode | String | 系统编码 | 系统代码 |
| sysName | String | 系统名称 | 系统名称 |
| enable | Integer | 启用状态 | 运行/维护 |

---

#### PrivilegeUserRoleInfo - 用户角色关联表
> 🏠 就像公司的**员工岗位分配表**

| 字段 | 类型 | 含义 | 生活比喻 |
|------|------|------|----------|
| id | String | 主键 | 分配编号 |
| userId | String | 用户ID | 员工编号 |
| roleId | String | 角色ID | 岗位编号 |

---

#### PrivilegeOrgSystem - 机构系统订阅表
> 🏠 就像公司的**部门订阅清单**

| 字段 | 类型 | 含义 | 生活比喻 |
|------|------|------|----------|
| id | String | 主键 | 订阅编号 |
| systemId | String | 系统ID | 订阅的系统 |
| orgId | String | 机构ID | 哪个部门订阅 |
| menuId | String | 菜单ID | 具体菜单 |
| isRelates | String | 是否关联(1/0) | 有没有权限 |

---

#### PrivilegeAuthInfo - 权限信息表
> 🏠 就像公司的**权限清单本**

| 字段 | 类型 | 含义 | 生活比喻 |
|------|------|------|----------|
| id | String | 主键 | 权限编号 |
| name | String | 权限名称 | 权限名 |
| code | String | 权限编码 | 代码 |
| enable | Integer | 启用状态 | 可用/禁用 |
| shared | Integer | 是否共享(0独有1共享) | 独享/共享 |
| orderIndex | Integer | 排序号 | 显示顺序 |

---

#### PrivilegeRoleResource - 角色资源关联表
> 🏠 就像岗位的**资源权限卡**

| 字段 | 类型 | 含义 | 生活比喻 |
|------|------|------|----------|
| id | String | 主键 | 分配编号 |
| roleId | String | 角色ID | 岗位编号 |
| systemId | String | 系统ID | 哪个系统 |
| menuId | String | 菜单ID | 能访问什么 |

---

### 🔶 DTO层 - 数据传输对象

#### PrivilegeUserInfoDto - 用户信息传输对象
> 🏠 就像发给前端的**员工名片**

```java
// 字段包括：
id, account, name, tel, email, idNum, orgId, remark, enable, 
roleIds[], pageIndex, pageSize, authIds[]
```

**特点**：
- 敏感字段加了`@SensitiveEncrypt`注解，会加密传输
- 增加了`roleIds[]`方便传多个角色
- 增加了分页字段

**数据流转**：PO → DTO转换 → 前端展示

---

#### PrivilegeMenuInfoDto - 菜单信息传输对象
> 🏠 就像发给前端的**菜单导航卡**

```java
// 继承自 PrivilegeMenuInfo
// 增加字段：
List<PrivilegeMenuInfoDto> children  // 子菜单列表（构成树）
String userId                          // 用户ID
String systemName                      // 系统名称
String orgId                           // 机构ID
```

**数据流转**：PO列表 → 递归构建树形 → DTO返回前端

---

#### PrivilegeUserRoleInfoDto - 用户角色传输对象
> 🏠 就像发给前端的**员工岗位表**

```java
userId      // 用户ID
roleIds[]   // 角色ID数组（可以分配多个）
pageIndex   // 页码
pageSize    // 每页条数
```

---

### 🔶 VO层 - 视图对象（前端提交）

#### RoleCreateVo - 角色创建视图对象
> 🏠 就像新建岗位时填的**申请表**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| orgId | String | ✅ | 所属机构 |
| name | String | ✅ | 角色名称 |
| enable | Integer | ✅ | 启用状态 |
| code | String | ❌ | 角色编码 |
| remark | String | ❌ | 描述 |
| systemId | String | ❌ | 系统ID |
| menuIds | List | ❌ | 菜单ID列表 |

**数据流转**：前端表单 → VO → @Validated验证 → Service处理

---

#### OrgInfoVo - 机构信息视图对象
> 🏠 就像新增部门时填的**登记表**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String | 主键（编辑时用） |
| code | String | 机构编码 |
| name | String | 机构名称 |
| parentId | String | 父级ID（构成树） |
| address | String | 地址 |
| contacts | String | 联系人 |
| contactNumber | String | 联系电话 |
| contactEmail | String | 邮箱 |
| enable | Integer | 启用状态 |
| remark | String | 备注 |
| orderIndex | Integer | 排序号 |

---

#### PrivilegeMenuInfoVo - 菜单信息视图对象
> 🏠 就像配置菜单时填的**菜单卡**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String | 主键 |
| parentId | String | 父级菜单 |
| systemId | String | 所属系统 |
| name | String | 菜单名称 |
| menuLevel | Integer | 菜单层级 |
| menuType | String | 菜单类型 |
| url | String | 请求地址 |
| enable | Integer | 启用状态 |
| orderIndex | Integer | 排序号 |
| ids | List<String> | 批量操作的ID列表 |

---

#### PrivilegeMenuServiceVo - 菜单服务视图对象
> 🏠 就像配置服务接口时填的**服务卡**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String | 主键 |
| menuId | String | 所属菜单 |
| serviceUrl | String | 接口URL |
| serviceName | String | 接口名称 |
| serviceKey | String | 搜索关键词 |
| addservicesList | List | 新增的服务列表 |
| updateservicesList | List | 更新的服务列表 |
| deleteservicesList | List | 删除的服务列表 |

---

#### OrgSystemInfoVo - 机构系统视图对象
> 🏠 就像给部门分配系统时填的**分配单**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String | 主键 |
| systemId | String | 系统ID |
| orgId | String | 机构ID |
| menuIds | String[] | 菜单ID数组 |
| menuName | String | 菜单名称 |
| orgName | String | 机构名称 |
| systemName | String | 系统名称 |
| enable | Integer | 启用状态 |

---

### 📊 数据流转总图

```
┌─────────────────────────────────────────────────────────────────────┐
│                           前端 (Vue/React)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ 用户表单  │  │ 角色表单  │  │ 菜单表单  │  │ 机构表单  │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
└───────┼────────────┼────────────┼────────────┼───────────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        API层 (Controller)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │UserInfoApi│ │RoleInfoApi│ │MenuInfoApi│ │OrgInfoApi│           │
│  │  /create │  │  /create │  │  /create │  │  /create │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
└───────┼────────────┼────────────┼────────────┼───────────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Service层 (业务逻辑)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │UserInfo  │  │ RoleInfo │  │ MenuInfo │  │ OrgInfo  │           │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
└───────┼────────────┼────────────┼────────────┼───────────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Mapper层 (SQL操作)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │UserInfoDao   │  │ RoleInfoDao  │  │ MenuInfoDao  │             │
│  │ Privilege    │  │  Privilege   │  │  Privilege   │             │
│  │UserInfoDao   │  │ RoleInfoDao  │  │ MenuInfoDao  │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
└─────────┼────────────────┼────────────────┼───────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         数据库 (MySQL/Oracle)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │privilege     │  │privilege     │  │privilege     │             │
│  │_user_info    │  │_role_info    │  │_menu_info    │             │
│  │   人员表      │  │   角色表      │  │   菜单表      │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │privilege     │  │privilege     │  │privilege     │             │
│  │_org_info     │  │_org_system    │  │_user_role    │             │
│  │   机构表      │  │   机构系统表   │  │   用户角色表  │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 🔄 数据转换示例

**用户创建流程**：

```
1. 前端填写用户表单 (PrivilegeUserInfoVo/Dto)
   ↓
2. API接口接收 @RequestBody
   ↓
3. Service层处理
   - 创建PO对象 (PrivilegeUserInfo)
   - 设置密码（加密）
   - 调用Mapper保存
   ↓
4. Mapper执行INSERT SQL
   ↓
5. 数据库插入记录
```

**用户查询流程**：

```
1. 前端请求用户列表
   ↓
2. API接口接收查询条件
   ↓
3. Mapper执行SELECT SQL
   ↓
4. 数据库返回PO列表 (PrivilegeUserInfo[])
   ↓
5. Service层转换为DTO
   - 密码字段不返回（置空）
   - 敏感字段加密
   ↓
6. API层返回ApiResponse
   ↓
7. 前端展示用户列表
```

---

## 📝 附录：表关系图

```
┌─────────────────┐       ┌─────────────────┐
│privilege_user   │       │privilege_org    │
│_info            │       │_info            │
│(用户表)          │       │(机构表)          │
├─────────────────┤       ├─────────────────┤
│id               │◄─────►│id               │
│org_id           │       │parent_id        │
└────────┬────────┘       └─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐       ┌─────────────────┐
│privilege_user   │       │privilege_role   │
│_role            │       │_info            │
│(用户角色表)      │       │(角色表)          │
├─────────────────┤       ├─────────────────┤
│id               │◄─────►│id               │
│user_id          │       │org_id           │
│role_id          │       │enable           │
└─────────────────┘       └────────┬────────┘
                                  │
                                  │ 1:N
                                  ▼
                         ┌─────────────────┐
                         │privilege_role   │
                         │_resource        │
                         │(角色资源表)      │
                         ├─────────────────┤
                         │id               │
                         │role_id          │
                         │menu_id          │
                         │system_id        │
                         └────────┬────────┘
                                  │
                                  │ N:1
                                  ▼
                         ┌─────────────────┐
                         │privilege_menu   │
                         │_info            │
                         │(菜单表)          │
                         ├─────────────────┤
                         │id               │
                         │system_id        │
                         │parent_id        │
                         └─────────────────┘
```

---

📎 **延伸阅读**：
- [数据库ER图与表结构](picc-mzmtb-user-数据库ER图与表结构.md) - 17张数据库表的完整ER图和字段说明
- [深度解析-菜单与系统管理](picc-mzmtb-user-深度解析第四章-菜单与系统管理.md) - 菜单树递归构建、服务接口管理
- [配置部署依赖](picc-mzmtb-user-配置部署依赖.md) - MyBatis配置、分页插件、Mapper XML加载

*文档生成时间：基于 PICC 权限管理系统源码解析*
