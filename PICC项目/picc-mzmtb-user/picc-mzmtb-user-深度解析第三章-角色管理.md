# PICC人保健康权限管理系统 - 深度解析第三章：角色管理

> 📅 更新时间：2024年7月  
> 🎯 适合人群：零基础开发人员、刚接手项目的同学  
> 📖 学习方式：跟着"🏠比喻"理解业务流程

---

## 一、角色管理业务概述

### 1.1 角色在权限系统中的地位

```
┌─────────────────────────────────────────────────────────────────┐
│                        PICC权限系统架构                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────┐      ┌─────────┐      ┌─────────┐                │
│   │ 用户    │ ───▶ │ 角色    │ ───▶ │ 权限    │                │
│   │ User   │ 属于  │ Role   │ 包含  │ Auth   │                │
│   └─────────┘      └─────────┘      └─────────┘                │
│        │                │                │                      │
│        │                │                │                      │
│        ▼                ▼                ▼                      │
│   ┌─────────┐      ┌─────────┐      ┌─────────┐                │
│   │ 人员表  │      │ 角色表  │      │ 权限表  │                │
│   │         │      │         │      │         │                │
│   │ 一人    │      │ 一人    │      │ 多个    │                │
│   │ 多角色  │      │ 多权限  │      │         │                │
│   └─────────┘      └─────────┘      └─────────┘                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**简单理解：**
- 👤 **用户** = 实际使用系统的人（张三、李四）
- 🎭 **角色** = 一堆权限的"打包"（比如"医生"角色包含开处方权限、查看病历权限）
- 🔐 **权限** = 具体的操作许可（能不能看、能不能改、能不能删）

### 1.2 角色管理功能清单

| 功能 | 方法名 | 一句话说明 |
|------|--------|------------|
| 创建角色 | `createRole()` | 新建一个角色，配置它属于哪个系统、能访问哪些菜单 |
| 编辑角色 | `updateRole()` | 修改角色的名字、备注、启用状态、菜单配置 |
| 删除角色 | `deleteRole()` | 软删除一个角色（只是标记删除，数据还在） |
| 批量删除 | `deleteRolesByIds()` | 一次性删除多个角色 |
| 角色详情 | `getDetail()` | 查看某个角色的所有信息 |
| 查询角色列表 | `queryRolesByOrgId()` | 按机构查询角色（支持分页） |
| 查询角色树 | `queryRoleTreeByOrgId()` | 查询某机构及其所有子机构的角色 |
| 查询权限树 | `queryAuthTreeByRoleId()` | 查看某角色能看到哪些权限 |
| 配置菜单 | `setResource()` | 给角色分配/修改能访问的菜单 |
| 查询菜单 | `queryResourcesByRoleId()` | 查看某角色能访问哪些菜单 |
| 删除菜单 | `deleteResourcesByIds()` | 移除角色的某个菜单权限 |
| 启用/禁用 | `updateEnable()` | 开关角色（禁用后该角色无法使用） |

---

## 二、核心数据模型

### 2.1 角色表 (privilege_role_info)

```sql
┌──────────────────────────────────────────────────────────────┐
│                    privilege_role_info 表                    │
├──────────────┬───────────────────────────────────────────────┤
│ 字段         │ 含义                                           │
├──────────────┼───────────────────────────────────────────────┤
│ id           │ 主键，角色的唯一标识（系统生成UUID）           │
│ org_id       │ 归属的机构ID（角色属于哪个机构）               │
│ code         │ 角色编码（可选）                               │
│ name         │ 角色名称（如"管理员"、"医生"、"护士"）        │
│ remark       │ 角色描述                                       │
│ enable       │ 是否启用：1=启用，0=禁用                       │
│ delete_at    │ 删除时间（软删除标记，非空表示已删除）         │
│ creator      │ 创建人账号                                     │
│ createtime   │ 创建时间                                       │
│ modifier     │ 修改人账号                                     │
│ modifytime   │ 修改时间                                       │
└──────────────┴───────────────────────────────────────────────┘
```

### 2.2 角色资源表 (privilege_role_resource)

```sql
┌──────────────────────────────────────────────────────────────┐
│                privilege_role_resource 表                    │
├──────────────┬───────────────────────────────────────────────┤
│ 字段         │ 含义                                           │
├──────────────┼───────────────────────────────────────────────┤
│ id           │ 主键                                           │
│ role_id      │ 角色ID（关联privilege_role_info）             │
│ system_id    │ 系统ID（这个菜单属于哪个系统）                 │
│ menu_id      │ 菜单ID（这个角色能访问哪些菜单）               │
│ delete_at    │ 删除时间（软删除）                             │
│ creator      │ 创建人                                         │
│ createtime   │ 创建时间                                       │
│ modifier     │ 修改人                                         │
│ modifytime   │ 修改时间                                       │
└──────────────┴───────────────────────────────────────────────┘
```

> 🏠 **比喻**：这张表就像"角色-菜单"的**通行证申请表**
> - 一个角色可以申请多张通行证（一个角色可以配多个菜单）
> - 一张通行证对应一个菜单权限

### 2.3 菜单表 (privilege_menu_info)

```sql
┌──────────────────────────────────────────────────────────────┐
│                   privilege_menu_info 表                      │
├──────────────┬───────────────────────────────────────────────┤
│ 字段         │ 含义                                           │
├──────────────┼───────────────────────────────────────────────┤
│ id           │ 菜单ID                                         │
│ system_id    │ 所属系统ID                                     │
│ parent_id    │ 父级菜单ID（构建菜单树）                       │
│ code         │ 菜单编码                                       │
│ name         │ 菜单名称                                       │
│ menu_level   │ 菜单层级                                       │
│ url          │ 菜单对应的页面地址                             │
│ enable       │ 是否启用                                       │
│ order_index  │ 排序号                                         │
└──────────────┴───────────────────────────────────────────────┘
```

### 2.4 权限表 (privilege_auth_info)

```sql
┌──────────────────────────────────────────────────────────────┐
│                    privilege_auth_info 表                    │
├──────────────┬───────────────────────────────────────────────┤
│ 字段         │ 含义                                           │
├──────────────┼───────────────────────────────────────────────┤
│ id           │ 权限ID                                         │
│ name         │ 权限名称（如"查看"、"编辑"、"删除"）         │
│ code         │ 权限编码                                       │
│ enable       │ 是否启用                                       │
│ shared       │ 是否共享（跨系统使用）                         │
│ order_index  │ 排序号                                         │
└──────────────┴───────────────────────────────────────────────┘
```

---

## 三、方法详解

---

### 方法1：createRole（创建角色）

> 🎯 **一句话人话**：新建一个角色，并给它分配能访问的菜单

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| orgId | 角色属于哪个机构 | `org_001`（北京分公司） |
| name | 角色叫什么名字 | `"门诊医生"` |
| enable | 是否启用 | `1`（启用） |
| systemId | 属于哪个系统 | `sys_001`（HIS系统） |
| menuIds | 能访问哪些菜单 | `["menu_001", "menu_002"]` |
| remark | 备注说明 | `"负责日常门诊工作"` |

#### 📤 返回什么？（返回值）

```json
{
  "code": "SUCCESS",
  "jsonResult": "{\"id\":\"role_xxx123\"}",  // 返回新创建的角色ID
  "msg": null
}
```

#### 🔗 谁会用这个方法？（调用方）

- **直接调用**：`POST /privilege/role/create`
- **触发场景**：
  - 管理员在后台新增一个角色
  - 给新部门配置专属角色

#### 📖 方法内部一步一步在做什么？

```java
// 第1步（约第48行）：创建一个"角色信息"对象
//    把前端传来的数据（名字、机构等）复制到角色对象里
PrivilegeRoleInfo privilegeRoleInfo = new PrivilegeRoleInfo();
BeanUtils.copyProperties(roleCreateVo, privilegeRoleInfo);

// 第2步（约第50行）：生成唯一ID
//    就像给每个角色发一个身份证号
String roleId = UniqueIDGenerator.generateUniqueID();

// 第3步（约第52-55行）：记录创建人信息
//    谁创建了这个角色，什么时间创建的
privilegeRoleInfo.setCreatetime(LocalDateTime.now());
privilegeRoleInfo.setCreator(UserUtils.getUser().getUserAccount());

// 第4步（约第57行）：数据校验
//    检查：1）这个ID是否已被占用  2）同机构下是否有同名角色
String checkRes = roleDataVerifi(privilegeRoleInfo);

// 第5步（约第65行）：🏠 事务开始！
//    🏠 银行转账：要么角色信息+资源信息一起存成功，要么一起失败回滚
@Transactional(rollbackForClassName = {"Exception"})
// 把角色信息存入数据库
privilegeRoleInfoDao.insertSelective(privilegeRoleInfo);

// 第6步（约第68-98行）：配置角色能访问的菜单
//    如果传了 systemId 或 menuIds，说明要给这个角色分配菜单
if (StringUtils.isNotBlank(roleCreateVo.getSystemId()) || 
    CollectionUtils.isNotEmpty(roleCreateVo.getMenuIds())) {
    
    // 遍历每个菜单ID，一张一张地创建"通行证"
    for(String menuId : roleCreateVo.getMenuIds()) {
        // 创建角色-菜单关联记录
        PrivilegeRoleResource privilegeRoleResource = new PrivilegeRoleResource();
        privilegeRoleResource.setMenuId(menuId);
        privilegeRoleResource.setRoleId(roleId);
        // 校验这个角色是否已经配置过这个菜单
        String resoureCheckRes = resourceDataVerifi(privilegeRoleResource);
        // 存入数据库
        privilegeRoleResourceDao.insert(privilegeRoleResource);
    }
}
```

#### ⚠️ 异常处理

| 情况 | 结果 |
|------|------|
| 同机构下有同名角色 | 返回 `"该机构下已存在同名角色"` |
| 这个菜单已经配给这个角色了 | 跳过（不报错，但也不插入） |
| 数据库插入失败 | 事务回滚，整个创建操作取消 |

#### 🐛 小白易懵点

1. **menuIds 为空时**：只创建角色，不配置菜单
2. **@Transactional 是什么**：
   > 🏠 银行转账比喻：你给朋友转1000块
   > - 你扣1000 + 朋友到账 = 必须同时成功
   > - 如果朋友账户有问题，你这边也应该回滚
   > - `@Transactional` 就是保证"角色信息"和"菜单配置"要么一起成功，要么一起失败

---

### 方法2：updateRole（编辑角色）

> 🎯 **一句话人话**：修改角色的基本信息或菜单配置

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| id | 要修改哪个角色 | `role_xxx123` |
| orgId | 角色归属的机构 | `org_001` |
| name | 新的角色名 | `"高级医生"` |
| remark | 新的备注 | `"具有处方权"` |
| enable | 启用/禁用状态 | `1`（启用） |
| systemId | 所属系统 | `sys_001` |
| menuIds | 新的菜单列表 | `["menu_001", "menu_003"]` |

#### 📤 返回什么？（返回值）

```json
{
  "code": "SUCCESS",
  "jsonResult": null,
  "msg": null
}
```

#### 🔗 谁会用这个方法？（调用方）

- **直接调用**：`POST /privilege/role/update`
- **触发场景**：
  - 管理员修改角色名称
  - 给角色添加/移除菜单权限

#### 📖 方法内部一步一步在做什么？

```java
// 第1步（约第110行）：查出这个角色原来的信息
PrivilegeRoleInfo roleQueryPo = privilegeRoleInfoDao.selectByPrimaryKey(roleUpdateVo.getId());

// 第2步（约第112-113行）：记录修改人
roleQueryPo.setModifier(UserUtils.getUser().getUserAccount());
roleQueryPo.setModifytime(LocalDateTime.now());

// 第3步（约第116-124行）：检查哪些字段被修改了
//    如果名字、机构、备注、启用状态有变化，就更新
if (fieldDiff(roleUpdateVo.getName(), roleQueryPo.getName()) || 
    fieldDiff(roleUpdateVo.getOrgId(), roleQueryPo.getOrgId()) ||
    // ... 其他字段) {
    // 更新角色基本信息
    NotBlankFieldCopy.fieldPropertiesCopy(privilegeRoleInfo, roleQueryPo);
    // 校验修改后是否会有同名角色
    String checkRes = roleDataUpdateVerifi(roleQueryPo);
}

// 第4步（约第130行）：保存角色信息
privilegeRoleInfoDao.updateByPrimaryKey(roleQueryPo);

// 第5步（约第137-153行）：更新菜单配置（如果有的话）
//    ⚠️ 注意：这里有TODO，逻辑不完整！
if (StringUtils.isNotBlank(roleUpdateVo.getSystemId())) {
    // tod 更新角色菜单集合...
    // 这里应该先删旧的，再插入新的，但代码被截断了
}
```

#### ⚠️ 异常处理

| 情况 | 结果 |
|------|------|
| 角色不存在 | 返回 `"未查找到该角色"` |
| 同机构下有同名角色 | 返回 `"该机构下已存在同名角色"` |
| 更新失败 | 记录日志，返回 `"角色信息更新失败"` |

#### 🐛 小白易懵点

1. **fieldDiff() 方法**：比较两个值是否有变化
   - 如果值1=值2，返回 false（没变化）
   - 如果值1≠值2，返回 true（有变化，需要更新）

2. **为什么不直接覆盖？**
   - 因为有些字段可能没传，不能把原来的值覆盖成 null
   - `NotBlankFieldCopy.fieldPropertiesCopy` 只复制非空字段

---

### 方法3：deleteRole（删除单个角色）

> 🎯 **一句话人话**：软删除一个角色（只是标记删除，数据还在数据库里）

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| id | 要删除哪个角色 | `role_xxx123` |

#### 📤 返回什么？（返回值）

```json
{
  "code": "SUCCESS",
  "jsonResult": "role_xxx123",  // 返回被删除的角色ID
  "msg": null
}
```

#### 🔗 谁会用这个方法？（调用方）

- **直接调用**：`POST /privilege/role/delete`
- **触发场景**：
  - 管理员删除某个不再需要的角色

#### 📖 方法内部一步一步在做什么？

```java
// 第1步（约第177行）：校验参数
if (StringUtils.isBlank(roleDeleteVo.getId())) {
    return "id不能为空";
}

// 第2步（约第179行）：根据ID查角色
PrivilegeRoleInfo privilegeRoleInfo = privilegeRoleInfoDao.selectByPrimaryKey(roleDeleteVo.getId());

// 第3步（约第180-183行）：检查角色状态
if (privilegeRoleInfo == null) {
    return "未查找到该角色";
}
if (privilegeRoleInfo.getDeleteAt() != null) {
    return "该角色已删除";
}

// 第4步（约第185-187行）：🏠 事务开始！
@Transactional(rollbackForClassName = {"Exception"})
// 软删除：设置删除时间（而不是真的从数据库删掉）
privilegeRoleInfo.setDeleteAt(LocalDateTime.now());
privilegeRoleInfo.setModifier(UserUtils.getUser().getUserAccount());
privilegeRoleInfo.setModifytime(LocalDateTime.now());

// 第5步（约第189行）：保存
privilegeRoleInfoDao.updateByPrimaryKey(privilegeRoleInfo);
```

#### ⚠️ 异常处理

| 情况 | 结果 |
|------|------|
| id为空 | 返回 `"id不能为空"` |
| 角色不存在 | 返回 `"未查找到该角色"` |
| 角色已删除 | 返回 `"该角色已删除"` |

#### 🐛 小白易懵点

1. **什么是软删除？**
   > 🏠 比喻：把文件扔进"回收站"而不是直接Delete
   > - 数据还在，但标记为"已删除"
   > - 以后可以恢复
   > - 代码里用 `deleteAt != null` 判断是否已删除

---

### 方法4：deleteRolesByIds（批量删除角色）

> 🎯 **一句话人话**：一次性删除多个角色

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| ids | 要删除的角色ID列表 | `["role_001", "role_002", "role_003"]` |

#### 📤 返回什么？（返回值）

```json
{
  "code": "SUCCESS",
  "jsonResult": "[\"角色A\",\"角色B\"]",  // 返回被删除的角色名称列表
  "msg": null
}
```

#### 🔗 谁会用这个方法？（调用方）

- **直接调用**：`POST /privilege/role/deleteRolesByIds`
- **触发场景**：
  - 批量清理过期/无用角色

#### 📖 方法内部一步一步在做什么？

```java
// 第1步（约第275行）：根据ID列表查出所有要删除的角色
List<PrivilegeRoleInfo> roleInfoList = privilegeRoleInfoDao.queryRoleByIds(roleListDeleteVo.getIds());

// 第2步（约第277-279行）：🏠 事务开始！批量软删除
@Transactional(rollbackForClassName = {"Exception"})
// 只保留还没被删除的（过滤掉已删除的）
roleInfoList.stream()
    .filter(role -> role.getDeleteAt() == null)
    .forEach(role -> role.setDeleteAt(LocalDateTime.now()));

// 第3步（约第283-289行）：逐个更新，标记修改人
for (PrivilegeRoleInfo privilegeRoleInfo : roleInfoList) {
    privilegeRoleInfo.setModifier(user);
    privilegeRoleInfo.setModifytime(currentTime);
    privilegeRoleInfoDao.updateByPrimaryKey(privilegeRoleInfo);
    roleDeleteList.add(privilegeRoleInfo.getName());  // 记录被删的名字
}
```

#### ⚠️ 异常处理

- 只会删除还没被删除的角色，已删除的会被跳过

---

### 方法5：getDetail（查看角色详情）

> 🎯 **一句话人话**：查看某个角色的所有信息

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| id | 要查看哪个角色 | `role_xxx123` |

#### 📤 返回什么？（返回值）

```json
{
  "code": "SUCCESS",
  "jsonResult": "{\"id\":\"role_xxx123\",\"name\":\"门诊医生\",\"orgId\":\"org_001\",...}",
  "msg": null
}
```

#### 🔗 谁会用这个方法？（调用方）

- **直接调用**：`POST /privilege/role/getDetail`
- **触发场景**：
  - 管理员点击角色列表中的"详情"按钮

#### 📖 方法内部一步一步在做什么？

```java
// 第1步（约第201行）：校验ID
if (StringUtils.isBlank(roleDetailVo.getId())) {
    return "id不能为空";
}

// 第2步（约第203行）：查询角色基本信息
PrivilegeRoleInfo privilegeRoleInfo = privilegeRoleInfoDao.selectByPrimaryKey(roleDetailVo.getId());

// 第3步（约第206-212行）：查询角色关联的菜单
List<PrivilegeRoleResource> roleResources = privilegeRoleResourceDao.queryResourcesByRoleId(roleDetailVo.getId());

// 第4步（约第214-220行）：把菜单信息组装进返回对象
List<MenuInfo> menuInfoList = new ArrayList<>();
roleResources.forEach(resource -> {
    // 查询每个菜单的详细信息
    PrivilegeMenuInfo menuInfo = privilegeMenuInfoDao.selectByPrimaryKey(resource.getMenuId());
    if (menuInfo != null && menuInfo.getDeleteAt() == null && menuInfo.getEnable() == 1) {
        menuInfoList.add(new MenuInfo().setResourceId(menuInfo.getId()).setResourceName(menuInfo.getName()));
    }
});
```

---

### 方法6：queryRolesByOrgId（查询角色列表）

> 🎯 **一句话人话**：按机构查询角色列表（支持分页）

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| orgId | 查询哪个机构的角色 | `org_001` |
| roleName | 按角色名模糊搜索（可选） | `"医生"` |
| pageIndex | 第几页 | `1` |
| pageSize | 每页几条 | `10` |

#### 📤 返回什么？（返回值）

```json
{
  "code": "SUCCESS",
  "jsonResult": "{\"total\":50,\"list\":[{\"id\":\"role_001\",\"name\":\"医生\"},...]}",
  "msg": null
}
```

#### 🔗 谁会用这个方法？（调用方）

- **直接调用**：`POST /privilege/role/queryRolesByOrgId`
- **触发场景**：
  - 管理员打开角色管理页面
  - 用户筛选某个机构下的角色

#### 📖 方法内部一步一步在做什么？

```java
// 第1步（约第236-239行）：启动分页
//    🏠 仓库管理员分页比喻：
//    "我要第1页，每页10条" = 管理员只给你10条，不是一次性全部给你
if (rolesQueryVo.getPageIndex() > 0 && rolesQueryVo.getPageSize() > 0) {
    PageHelper.startPage(rolesQueryVo.getPageIndex(), rolesQueryVo.getPageSize());
}

// 第2步（约第241行）：查询数据库
List<PrivilegeRoleInfo> privilegeRoleInfoList = privilegeRoleInfoDao.queryRolesByOrgidAndRolename(...);

// 第3步（约第243-254行）：把角色信息转成VO格式
List<RoleQueryDto> roleQueryDtos = new ArrayList<>();
privilegeRoleInfoList.forEach(roleInfo -> {
    RoleQueryDto dto = new RoleQueryDto();
    BeanUtils.copyProperties(roleInfo, dto);
    // 补充机构名称
    if (StringUtils.isNotBlank(roleInfo.getOrgId())) {
        String orgName = privilegeOrgInfoDao.queryOrgName(roleInfo.getOrgId());
        dto.setOrgName(orgName);
    }
    roleQueryDtos.add(dto);
});

// 第4步（约第256行）：返回分页结果
ResultPage<RoleQueryDto> resPage = this.createResultPage(new PageInfo<>(roleQueryDtos));
```

---

### 方法7：queryRoleTreeByOrgId（查询角色树）

> 🎯 **一句话人话**：查询某个机构及其所有子机构的角色

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| orgId | 顶级机构ID | `org_root` |
| roleName | 按角色名模糊搜索（可选） | `"管理员"` |
| pageIndex | 第几页 | `1` |
| pageSize | 每页几条 | `10` |

#### 📤 返回什么？（返回值）

```json
{
  "code": "SUCCESS",
  "jsonResult": "{包含org_root + 所有子机构的角色列表}",
  "msg": null
}
```

#### 🔗 谁会用这个方法？（调用方）

- **直接调用**：`POST /privilege/role/queryRoleTreeByOrgId`
- **触发场景**：
  - 查看集团下所有子公司的角色

#### 📖 方法内部一步一步在做什么？

```java
// 第1步（约第269行）：查询该机构及其所有子机构ID
//    🏠 找所有子部门的比喻：
//    先找到所有直接下属，然后找每个下属的下属，一直找下去...
List<String> idList = getidList(rolesQueryVo.getOrgId());
// 结果：[org_root, org_001, org_002, org_001_01, org_001_02, ...]

// 第2步（约第271行）：用这些ID去查询角色
privilegeRoleInfoDao.queryRolesByOrgidListAndRolename(idList, rolesQueryVo.getRoleName());
```

#### 🐛 小白易懵点

1. **getidList() 方法是递归获取所有子机构**：
```java
// 这个方法使用"广度优先搜索"获取整个机构树
private List<String> getidList(String id) {
    Queue<String> queue = new LinkedList<>();
    List<String> idList = new ArrayList<>();
    queue.offer(id);
    
    while (!queue.isEmpty()) {
        // 取出队列中的一个机构
        String current = queue.poll();
        // 查找它的所有直接子机构
        List<PrivilegeOrgInfo> children = privilegeOrgInfoDao.selectAllOrgByParentId(current);
        // 把子机构加入队列和结果集
        for (PrivilegeOrgInfo child : children) {
            queue.offer(child.getId());
            idList.add(child.getId());
        }
    }
    return idList;
}
```

---

### 方法8：queryAuthTreeByRoleId（查询角色的权限树）

> 🎯 **一句话人话**：查看某角色能看到哪些权限

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| roleList | 角色ID列表 | `["role_001", "role_002"]` |
| pageIndex | 第几页 | `1` |
| pageSize | 每页几条 | `10` |

#### 📤 返回什么？（返回值）

```json
{
  "code": "SUCCESS",
  "jsonResult": "{包含该角色关联的父级菜单所对应的所有权限列表}",
  "msg": null
}
```

#### 🔗 谁会用这个方法？（调用方）

- **直接调用**：`POST /privilege/role/queryAuthTreeByRoleId`
- **触发场景**：
  - 查看某角色有哪些权限
  - 角色配置时选择权限

#### 📖 方法内部一步一步在做什么？

```java
// 第1步（约第309-313行）：启动分页
if (pageIndex > 0 && pageSize > 0) {
    PageHelper.startPage(pageIndex, pageSize);
}

// 第2步（约第318行）：根据角色ID查询对应的父级菜单ID
//    关系链：角色 -> 角色资源 -> 菜单 -> 菜单的父级 -> 权限
List<String> menuParentIdList = privilegeMenuInfoDao.queryParentMenuIdByRoleId(roleList);

// 第3步（约第320行）：根据菜单查询对应的权限
List<PrivilegeAuthInfo> authList = privilegeAuthInfoDao.queryAuthListByMenuId(menuParentIdList);
```

#### ⚠️ 小白易懵点

1. **为什么要查"父级菜单"的权限？**
   > 因为菜单和权限是多对多关系，一个菜单可能关联多个权限
   > 通过查询父级菜单，可以拿到所有子菜单关联的权限

2. **SQL 逻辑（PrivilegeAuthInfoDao.xml）**：
```sql
SELECT DISTINCT pai.id, pai.name, ...
FROM privilege_auth_info pai
LEFT JOIN privilege_auth_menu pam ON pai.id = pam.auth_id
WHERE pam.parent_menu_id IN (所有父级菜单ID)
```

---

### 方法9：setResource（配置角色菜单）

> 🎯 **一句话人话**：给角色分配能访问的菜单

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| roleId | 要配置哪个角色 | `role_xxx123` |
| systemId | 属于哪个系统 | `sys_001` |
| menuIds | 分配哪些菜单 | `["menu_001", "menu_002", "menu_003"]` |

#### 📤 返回什么？（返回值）

```json
{
  "code": "SUCCESS",
  "jsonResult": null,
  "msg": null
}
```

#### 🔗 谁会用这个方法？（调用方）

- **直接调用**：`POST /privilege/role/setResources`
- **触发场景**：
  - 给角色分配菜单权限

#### 📖 方法内部一步一步在做什么？

```java
// 第1步（约第168行）：🏠 事务开始！
@Transactional(rollbackForClassName = {"Exception"})

// 第2步（约第170行）：查询这个角色已有的菜单资源
List<PrivilegeRoleResource> existResources = privilegeRoleResourceDao.queryResourcesByRoleId(resourceVo.getRoleId());

// 第3步（约第172-181行）：删除已存在且不在新列表中的资源
existResources.forEach(exist -> {
    if (!resourceVo.getMenuIds().contains(exist.getMenuId())) {
        // 这个菜单不在新列表里，删掉
        exist.setDeleteAt(LocalDateTime.now());
        privilegeRoleResourceDao.updateByPrimaryKey(exist);
    }
});

// 第4步（约第183-197行）：添加新菜单
for (String menuId : resourceVo.getMenuIds()) {
    // 检查这个菜单是否已经配置过
    boolean exists = existResources.stream()
        .anyMatch(r -> r.getMenuId().equals(menuId) && r.getDeleteAt() == null);
    
    if (!exists) {
        // 没有配置过，新增
        PrivilegeRoleResource newResource = new PrivilegeRoleResource();
        newResource.setMenuId(menuId);
        newResource.setRoleId(resourceVo.getRoleId());
        newResource.setSystemId(resourceVo.getSystemId());
        privilegeRoleResourceDao.insert(newResource);
    }
}
```

---

### 方法10：queryResourcesByRoleId（查询角色菜单）

> 🎯 **一句话人话**：查看某角色能访问哪些菜单

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| roleIds | 要查询哪些角色 | `["role_001", "role_002"]` |
| pageIndex | 第几页 | `1` |
| pageSize | 每页几条 | `10` |

#### 📤 返回什么？（返回值）

```json
{
  "code": "SUCCESS",
  "jsonResult": "{
    \"total\": 5,
    \"list\": [
      {
        \"roleId\": \"role_001\",
        \"systemId\": \"sys_001\",
        \"menuInfo\": [
          {\"resourceId\": \"menu_001\", \"resourceName\": \"门诊挂号\"},
          {\"resourceId\": \"menu_002\", \"resourceName\": \"病历管理\"}
        ]
      }
    ]
  }",
  "msg": null
}
```

#### 🔗 谁会用这个方法？（调用方）

- **直接调用**：`POST /privilege/role/queryResourcesByRoleId`
- **触发场景**：
  - 查看某角色的菜单权限

#### 📖 方法内部一步一步在做什么？

```java
// 第1步（约第220行）：查询所有角色-菜单关联
List<PrivilegeRoleResource> privilegeRoleResourceList = 
    privilegeRoleResourceDao.queryResourcesByRoleIds(resourcesQueryVo.getRoleIds());

// 第2步（约第222-223行）：按角色ID分组
//    🏠 分组比喻：把一堆文件按部门分类放好
Map<String, List<PrivilegeRoleResource>> roleMap = privilegeRoleResourceList.stream()
    .collect(Collectors.groupingBy(PrivilegeRoleResource::getRoleId, Collectors.toList()));

// 第3步（约第225-240行）：每个角色单独处理
roleMap.entrySet().forEach((entry) -> {
    List<MenuInfo> menuInfoList = new ArrayList<>();
    // 遍历这个角色的每个菜单
    entry.getValue().forEach(resource -> {
        // 查询菜单详细信息
        PrivilegeMenuInfo menuInfo = privilegeMenuInfoDao.selectByPrimaryKey(resource.getMenuId());
        if (menuInfo != null && menuInfo.getDeleteAt() == null && menuInfo.getEnable() == 1) {
            menuInfoList.add(new MenuInfo()
                .setResourceId(menuInfo.getId())
                .setResourceName(menuInfo.getName()));
        }
    });
});
```

---

### 方法11：deleteResourcesByIds（删除角色菜单）

> 🎯 **一句话人话**：移除角色的某个菜单权限

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| ids | 要删除的角色-菜单关联ID列表 | `["res_001", "res_002"]` |

#### 📤 返回什么？（返回值）

```json
{
  "code": "SUCCESS",
  "jsonResult": null,
  "msg": null
}
```

#### 🔗 谁会用这个方法？（调用方）

- **直接调用**：`POST /privilege/role/deleteResourcesByIds`
- **触发场景**：
  - 移除角色的某个菜单权限

#### 📖 方法内部一步一步在做什么？

```java
// 第1步（约第259行）：校验参数
if (CollectionUtils.isEmpty(resourceDelVo.getIds())) {
    return "id列表为空";
}

// 第2步（约第261行）：根据ID查询要删除的记录
List<PrivilegeRoleResource> privilegeRoleResourceList = 
    privilegeRoleResourceDao.queryResourcesByIds(resourceDelVo.getIds());

// 第3步（约第263-268行）：🏠 事务开始！批量软删除
@Transactional(rollbackForClassName = {"Exception"})
privilegeRoleResourceList.forEach(resourceInfo -> {
    resourceInfo.setModifier(UserUtils.getUser().getUserAccount());
    resourceInfo.setModifytime(LocalDateTime.now());
    resourceInfo.setDeleteAt(LocalDateTime.now());  // 标记删除
    privilegeRoleResourceDao.updateByPrimaryKey(resourceInfo);
});
```

---

### 方法12：updateEnable（启用/禁用角色）

> 🎯 **一句话人话**：开关角色（禁用后该角色无法使用）

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| id | 要操作哪个角色 | `role_xxx123` |

#### 📤 返回什么？（返回值）

| 结果 | 说明 |
|------|------|
| `null` | 操作成功 |
| `"未查找到该角色"` | 角色不存在 |
| `"该角色已删除"` | 角色已被删除 |
| `"更新失败"` | 数据库更新失败 |

#### 🔗 谁会用这个方法？（调用方）

- **直接调用**：`POST /privilege/role/updateEnable`
- **触发场景**：
  - 临时禁用某个角色（保留数据，以后可能恢复）

#### 📖 方法内部一步一步在做什么？

```java
// 第1步（约第300行）：查询角色
PrivilegeRoleInfo privilegeRoleInfo = privilegeRoleInfoDao.selectByPrimaryKey(id);

// 第2步（约第301-308行）：校验
if (privilegeRoleInfo == null) {
    return "未查找到该角色";
}
if (privilegeRoleInfo.getDeleteAt() != null) {
    return "该角色已删除";
}

// 第3步（约第310-316行）：切换启用状态
//    🏠 开关比喻：当前是"开(1)"就变成"关(0)"，反之亦然
Integer enable = privilegeRoleInfo.getEnable();
if (enable != null && enable.equals(1)) {
    enable = 0;  // 关
} else {
    enable = 1;  // 开
}

// 第4步（约第318-321行）：保存
privilegeRoleInfo.setEnable(enable);
privilegeRoleInfo.setModifier(UserUtils.getUser().getUserAccount());
privilegeRoleInfo.setModifytime(LocalDateTime.now());
privilegeRoleInfoDao.updateByPrimaryKey(privilegeRoleInfo);
```

---

## 四、私有方法解析（工具方法）

### 4.1 roleDataVerifi（角色数据校验 - 创建时）

> **什么时候用**：创建角色前，检查数据是否合法

```java
private String roleDataVerifi(PrivilegeRoleInfo privilegeRoleInfo) {
    // 第1步：检查ID是否已被占用
    if (StringUtils.isNotBlank(id)) {
        PrivilegeRoleInfo queryPo = new PrivilegeRoleInfo();
        queryPo.setId(id);
        List<PrivilegeRoleInfo> checkPo = privilegeRoleInfoDao.select(queryPo);
        if (CollectionUtils.isNotEmpty(checkPo)) {
            return "id已存在";
        }
    }
    
    // 第2步：检查同机构下是否有同名角色
    if (StringUtils.isNotBlank(orgId) && StringUtils.isNotBlank(name)) {
        PrivilegeRoleInfo queryPo = new PrivilegeRoleInfo().setOrgId(orgId).setName(name);
        List<PrivilegeRoleInfo> checkPo = privilegeRoleInfoDao.select(queryPo);
        // 过滤掉已删除的
        checkPo = checkPo.stream()
            .filter(po -> po.getDeleteAt() == null)
            .collect(Collectors.toList());
        if (CollectionUtils.isNotEmpty(checkPo)) {
            return "该机构下已存在同名角色";
        }
    }
    return null;  // 校验通过
}
```

### 4.2 resourceDataVerifi（资源数据校验）

> **什么时候用**：给角色分配菜单前，检查是否已分配

```java
private String resourceDataVerifi(PrivilegeRoleResource privilegeRoleResource) {
    // 检查这个角色是否已经配置过这个菜单
    if (StringUtils.isNotBlank(menuId)) {
        PrivilegeRoleResource queryPo = new PrivilegeRoleResource();
        queryPo.setMenuId(menuId);
        queryPo.setRoleId(roleId);
        
        List<PrivilegeRoleResource> checkPos = privilegeRoleResourceDao.select(queryPo);
        // 过滤掉已删除的
        checkPos = checkPos.stream()
            .filter(checkPo -> checkPo.getDeleteAt() == null)
            .collect(Collectors.toList());
        
        if(CollectionUtils.isNotEmpty(checkPos)) {
            return "该角色已配置菜单" + menuId;
        }
    }
    return null;
}
```

### 4.3 fieldDiff（字段差异比较）

> **什么时候用**：判断两个值是否不同

```java
private boolean fieldDiff(String field1, String field2) {
    if (field2 == null && field2 == null) {
        return false;  // 两个都是null，没变化
    }
    if ((field1 == null && field2 != null) || (field1 != null && field2 == null)) {
        return true;   // 一个是null一个不是，有变化
    }
    return !field1.equals(field2);  // 都不为null，比较值
}
```

---

## 五、角色权限树构建逻辑

### 5.1 什么是权限树？

```
权限树 = 角色能看到的所有权限的树形结构

                    权限树（按菜单分组）
                         
    ┌─────────────────────────────────────────────────────────┐
    │                                                          │
    │  📁 系统管理                                              │
    │     ├── 🔐 用户管理 ────── [查看✓] [新增✓] [编辑✓] [删除✗] │
    │     ├── 🔐 角色管理 ────── [查看✓] [新增✓] [编辑✓] [删除✗] │
    │     └── 🔐 机构管理 ────── [查看✓] [新增✗] [编辑✗] [删除✗] │
    │                                                          │
    │  📁 门诊管理                                              │
    │     ├── 🔐 挂号管理 ────── [查看✓] [新增✓] [编辑✓] [删除✓] │
    │     └── 🔐 病历管理 ────── [查看✓] [新增✓] [编辑✓] [删除✓] │
    │                                                          │
    └─────────────────────────────────────────────────────────┘
```

### 5.2 权限树构建流程

```
┌────────────────────────────────────────────────────────────────────┐
│                    权限树构建流程                                    │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1️⃣ 根据角色ID查询角色资源表                                         │
│      SQL: SELECT * FROM privilege_role_resource WHERE role_id = ?   │
│      │                                                               │
│      ▼                                                               │
│  2️⃣ 根据角色拥有的菜单，查询父级菜单ID                                 │
│      SQL: SELECT DISTINCT parent_id FROM privilege_menu_info ...   │
│      │                                                               │
│      ▼                                                               │
│  3️⃣ 根据父级菜单查询关联的权限                                       │
│      SQL: SELECT * FROM privilege_auth_info WHERE ...              │
│      │                                                               │
│      ▼                                                               │
│  4️⃣ 组装成树形结构返回                                               │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### 5.3 核心SQL解析

**查询角色关联的父级菜单**（PrivilegeMenuInfoDao.xml）：
```sql
SELECT DISTINCT pmi.parent_id
FROM privilege_menu_info pmi
LEFT JOIN privilege_role_resource prr
    ON pmi.id = prr.menu_id
    AND prr.delete_at IS NULL
WHERE pmi.delete_at IS NULL
AND prr.role_id IN (角色ID列表)
```

**查询父级菜单对应的权限**（PrivilegeAuthInfoDao.xml）：
```sql
SELECT DISTINCT pai.id, pai.name, pai.code, pai.enable
FROM privilege_auth_info pai
LEFT JOIN privilege_auth_menu pam
    ON pai.id = pam.auth_id
    AND pam.delete_at IS NULL
WHERE pai.delete_at IS NULL
AND pam.parent_menu_id IN (父级菜单ID列表)
```

---

## 六、角色资源管理完整流程

### 6.1 创建角色 + 分配菜单

```
用户操作                          系统处理
   │                                 │
   │  POST /role/create              │
   │  {                              │
   │    "orgId": "org_001",           │
   │    "name": "门诊医生",           │
   │    "systemId": "sys_001",       │
   │    "menuIds": ["m1","m2"]        │
   │  }                               │
   ├────────────────────────────────>│
   │                                 │
   │                      ┌──────────┴──────────┐
   │                      │ 1. 生成角色ID        │
   │                      │ 2. 校验数据          │
   │                      │ 3. 插入角色表        │
   │                      │ 4. 插入角色资源表     │
   │                      │ (事务保证一致性)     │
   │                      └──────────┬──────────┘
   │                                 │
   │  返回: {"id": "role_xxx"}       │
   │<────────────────────────────────┤
```

### 6.2 修改角色菜单

```
用户操作                          系统处理
   │                                 │
   │  POST /role/setResources        │
   │  {                              │
   │    "roleId": "role_001",        │
   │    "systemId": "sys_001",       │
   │    "menuIds": ["m1","m2","m3"]  │
   │  }                               │
   ├────────────────────────────────>│
   │                                 │
   │                      ┌──────────┴──────────┐
   │                      │ 1. 查询已有菜单      │
   │                      │ 2. 删除不在新列表的  │
   │                      │ 3. 新增新菜单       │
   │                      └──────────┬──────────┘
   │                                 │
   │  返回: 成功                      │
   │<────────────────────────────────┤
```

---

## 七、第二章补充：UserInfoServiceImpl.setAuths() 权限归属配置

> 📌 这是第二章标记的"待深入内容"

### 7.1 什么是"权限归属"？

```
┌─────────────────────────────────────────────────────────────────┐
│                       权限归属概念                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  当给用户分配角色时，有些特殊权限需要"归属"到具体的业务单元        │
│                                                                  │
│  例子：                                                          │
│  ├── 用户"张三"被分配了"门诊医生"角色                            │
│  ├── "门诊医生"角色包含"开处方"权限                              │
│  ├── 但"开处方"权限需要归属到具体的"科室"                         │
│  │                                                               │
│  │   张三 ──属于──> 门诊科                                        │
│  │     │                                                         │
│  │     └── 拥有角色 ──> 门诊医生                                  │
│  │                    │                                         │
│  │                    └── 拥有权限 ──> 开处方（归属到：门诊科）     │
│  │                                                               │
│  └── 这样做的好处：系统能知道张三只能在门诊科开处方                 │
│                   不能在儿科、急诊科开处方                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 setAuths() 方法解析

> 🎯 **一句话人话**：给用户配置权限的"归属地"

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| account | 用户账号 | `"zhangsan"` |
| userId | 用户ID | `"user_001"` |
| authIds | 要分配的权限ID数组 | `["auth_001", "auth_002"]` |
| roleIds | 用户拥有的角色ID数组 | `["role_001"]` |

#### 📤 返回什么？（返回值）

| 结果 | 说明 |
|------|------|
| void（无返回值） | 操作成功 |
| 抛出异常 | 参数错误或用户不存在 |

#### 🔗 谁会用这个方法？（调用方）

- **直接调用**：在 `UserInfoServiceImpl.create()` 创建用户时自动调用
- **触发场景**：
  - 创建新用户时指定权限归属
  - 修改用户权限时重新配置归属

#### 📖 方法内部一步一步在做什么？

```java
public void setAuths(PrivilegeUserInfoDto privilegeUserInfoDto, String userId) {
    String account = privilegeUserInfoDto.getAccount();
    
    // 第1步（约第108行）：删除用户之前配置的历史权限归属
    //    🏠 比喻：装修前先清场，把旧的家具搬走
    deleteHistroyUserAuth(account, userId);
    
    // 第2步（约第113行）：校验参数
    if (StringUtils.isBlank(privilegeUserInfoDto.getAccount())) {
        throw new CustomException("参数错误！账户不能为空！");
    }
    if (privilegeUserInfoDto.getRoleIds() == null || privilegeUserInfoDto.getRoleIds().length == 0) {
        throw new CustomException("参数错误！角色ID不能为空！");
    }
    
    // 第3步（约第120行）：查询用户信息，确认用户存在
    List<PrivilegeUserInfo> userInfo = privilegeUserInfoDao.queryUserInfo(
        privilegeUserInfoDto.getAccount(), null, null, null, null);
    if (userInfo.isEmpty()) {
        throw new CustomException("该人员信息不存在！");
    }
    
    // 第4步（约第125行）：🏠 事务开始！
    try {
        // 查询该角色ID和权限ID对应的权限信息（包含归属标识）
        List<PrivilegeMenuAuthDto> authList = 
            privilegeAuthInfoDao.queryAuthListByRoleIdAndAuthId(
                privilegeUserInfoDto.getRoleIds(),
                privilegeUserInfoDto.getAuthIds());
        
        // 第5步（约第127-140行）：为每个权限创建归属记录
        for (PrivilegeMenuAuthDto authId : authList) {
            // 5.1 创建用户-权限归属记录
            PrivilegeUserAuth userAuth = new PrivilegeUserAuth();
            userAuth.setId(UUIDUtil.getUUID());
            userAuth.setUserId(userId);
            userAuth.setAuthId(authId.getId());           // 权限ID
            userAuth.setFlag(authId.getFlag().toString()); // 归属标识
            userAuth.setCreator(UserUtils.getUser().getUserAccount());
            userAuth.setCreatetime(LocalDateTime.now());
            userAuth.setModifier(UserUtils.getUser().getUserAccount());
            userAuth.setModifytime(LocalDateTime.now());
            privilegeUserAuthDao.insertSelective(userAuth);  // 存入用户权限表
            
            // 5.2 配置权限：person_division + up_org_user
            //    🏠 比喻：在两个地方登记，方便以后查询
            PersonDivision pd1 = new PersonDivision();
            pd1.setAccount(account);
            pd1.setFlag(authId.getFlag().toString());  // 归属标识
            List<PersonDivision> pdInfo = personDivisionDao.queryPersonDivisonList(pd1);
            
            // ... 后续逻辑（查询并更新业务归属表）
        }
    }
}
```

### 7.3 权限归属数据流

```
┌────────────────────────────────────────────────────────────────────┐
│                     权限归属配置完整流程                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  输入：                                                             │
│  ├── account = "zhangsan"                                          │
│  ├── userId = "user_001"                                           │
│  ├── authIds = ["auth_001", "auth_002"]  // 要分配的权限            │
│  └── roleIds = ["role_001"]              // 用户拥有的角色          │
│                                                                     │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Step 1: deleteHistroyUserAuth(account, userId)              │   │
│  │  删除用户历史权限归属记录                                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Step 2: queryAuthListByRoleIdAndAuthId(roleIds, authIds)   │   │
│  │  SQL查询：SELECT auth_id, flag FROM privilege_auth_menu ... │   │
│  │  返回：authId + flag（归属标识）                              │   │
│  │  例如：[{authId: "auth_001", flag: "dept_001"},             │   │
│  │         {authId: "auth_002", flag: "dept_002"}]             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Step 3: 循环处理每个权限                                    │   │
│  │                                                             │   │
│  │  3.1 插入用户权限表（privilege_user_auth）                  │   │
│  │      INSERT INTO privilege_user_auth                        │   │
│  │      (id, user_id, auth_id, flag, ...)                      │   │
│  │      VALUES ("uuid", "user_001", "auth_001", "dept_001",...)│   │
│  │                                                             │   │
│  │  3.2 配置业务归属表（person_division）                       │   │
│  │      在业务系统中登记这个权限的归属                           │   │
│  │                                                             │   │
│  │  3.3 配置组织用户表（up_org_user）                          │   │
│  │      把用户和归属组织关联起来                                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  结果：用户拥有了这些权限，并且每个权限都归属到具体的业务单元          │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### 7.4 核心表结构

**privilege_user_auth（用户权限表）**：
```sql
┌──────────────────────────────────────────────────────────────┐
│                 privilege_user_auth 表                      │
├──────────────┬───────────────────────────────────────────────┤
│ 字段         │ 含义                                           │
├──────────────┼───────────────────────────────────────────────┤
│ id           │ 主键                                           │
│ user_id      │ 用户ID                                         │
│ auth_id      │ 权限ID                                         │
│ flag         │ 归属标识（表示这个权限归属到哪个业务单元）       │
│ creator      │ 创建人                                         │
│ createtime   │ 创建时间                                       │
└──────────────┴───────────────────────────────────────────────┘
```

### 7.5 deleteHistroyUserAuth（删除历史权限归属）

```java
private void deleteHistroyUserAuth(String account, String userId) {
    // 1. 查询用户当前所有的权限归属记录
    List<PrivilegeUserAuth> userAuthList = 
        privilegeUserAuthDao.queryUserAuthList(userId, null, null);
    
    // 2. 批量软删除
    LocalDateTime now = LocalDateTime.now();
    for (PrivilegeUserAuth auth : userAuthList) {
        auth.setDeleteAt(now);
        auth.setModifier(UserUtils.getUser().getUserAccount());
        auth.setModifytime(now);
        privilegeUserAuthDao.updateByPrimaryKey(auth);
    }
}
```

---

## 八、常见问题与排查

### 8.1 创建角色失败

| 可能原因 | 排查方法 |
|----------|----------|
| 同机构下有同名角色 | 检查数据库中是否已有同名角色 |
| ID已被占用 | 检查传入的ID是否在表中已存在 |
| 数据库连接失败 | 检查数据库服务是否正常 |

### 8.2 查询不到角色

| 可能原因 | 排查方法 |
|----------|----------|
| 角色已被删除 | 检查 `delete_at` 字段是否有值 |
| 角色不属于该机构 | 确认 `org_id` 是否匹配 |
| 角色未启用 | 检查 `enable` 字段是否为1 |

### 8.3 角色权限树为空

| 可能原因 | 排查方法 |
|----------|----------|
| 角色没有配置菜单 | 检查 `privilege_role_resource` 表 |
| 菜单已被删除 | 检查菜单的 `delete_at` 是否为空 |
| 菜单未启用 | 检查菜单的 `enable` 是否为1 |

---

## 九、API 接口速查表

| 接口地址 | 方法 | 功能 | 关键参数 |
|----------|------|------|----------|
| `/privilege/role/create` | POST | 创建角色 | orgId, name, enable |
| `/privilege/role/update` | POST | 编辑角色 | id, name, menuIds |
| `/privilege/role/delete` | POST | 删除角色 | id |
| `/privilege/role/getDetail` | POST | 角色详情 | id |
| `/privilege/role/queryRolesByOrgId` | POST | 查询角色列表 | orgId |
| `/privilege/role/queryRoleTreeByOrgId` | POST | 查询角色树 | orgId |
| `/privilege/role/queryAuthTreeByRoleId` | POST | 查询权限树 | roleList |
| `/privilege/role/setResources` | POST | 配置菜单 | roleId, systemId, menuIds |
| `/privilege/role/queryResourcesByRoleId` | POST | 查询菜单 | roleIds |
| `/privilege/role/deleteResourcesByIds` | POST | 删除菜单 | ids |
| `/privilege/role/updateEnable` | POST | 启用/禁用 | id |
| `/privilege/role/deleteRolesByIds` | POST | 批量删除 | ids |

---

## 十、学习建议

### 10.1 从简单到复杂

1. **先学查询**：`queryRolesByOrgId()` - 最简单，不会改变数据
2. **再学创建**：`createRole()` - 理解事务和数据校验
3. **最后学删除**：`deleteRole()` - 理解软删除概念

### 10.2 理解核心概念

- 🏠 **事务**：要么都成功，要么都失败
- 🏠 **仓库管理员**：MyBatis Mapper 就是仓库管理员，你说要什么，它去拿
- 🏠 **软删除**：扔进回收站，不是真的删掉

### 10.3 调试技巧

```java
// 在关键位置加日志
log.info("角色创建成功, roleId:{}, orgId:{}", roleId, orgId);
log.error("角色资源配置失败, roleId:{}", roleId, e);

// 查看返回结果
System.out.println(JSON.toJSONString(commonReqVo));
```

---

> 📝 **文档版本**：v1.0  
> 🔄 **最后更新**：2024年7月

---

📎 **延伸阅读**：
- [深度解析-菜单与系统管理](picc-mzmtb-user-深度解析第四章-菜单与系统管理.md) - 菜单与系统的管理，和角色管理配合使用
- [补充方法解析](picc-mzmtb-user-补充方法解析.md) - RoleInfoServiceImpl中的setResource()等方法的补充说明
- [数据库ER图与表结构](picc-mzmtb-user-数据库ER图与表结构.md) - privilege_role_info、privilege_role_resource表字段详解
  
> ✍️ **作者**：基于源码分析自动生成
