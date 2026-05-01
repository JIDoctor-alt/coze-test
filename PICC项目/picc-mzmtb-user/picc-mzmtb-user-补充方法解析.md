---

## 📝 补充：遗漏方法解析

> 📅 补充日期：2024年
> ⚠️ 本章节补全了 UserInfoServiceImpl、OrgInfoServiceImpl、RoleInfoServiceImpl、MenuInfoServiceImpl、PrivilegeMenuInfoServiceImpl、PrivilegeMenuServiceServiceImpl 中遗漏的47个方法，以及5个工具类。

---

### 1️⃣ UserInfoServiceImpl 补充方法（5个）

---

#### `setAuths(PrivilegeUserInfoDto, String)` - 设置用户权限归属

> 🎯 **一句话人话**：给用户分配具体的权限归属（比如哪个地区的权限）

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `privilegeUserInfoDto` | 用户信息+要分配的权限ID数组 | `{account:"zhangsan", roleIds:["role001"], authIds:["auth001","auth002"]}` |
| `userId` | 用户ID | `"user-uuid-123"` |

**📤 返回什么？**
无返回值，但会：
- 清空用户历史权限归属
- 往 `privilege_user_auth` 表插入新记录
- 往 `person_division` 和 `up_org_user` 表写入归属信息

**🔗 谁会用这个方法？**
- **直接调用**：`create()` 方法创建用户时自动调用（第1步）
- **触发场景**：创建用户时传了 `authIds` 参数

**📖 方法内部一步一步在做什么？**
```java
// 第1行（约）：deleteHistroyUserAuth() - 先把用户之前的权限归属清掉
// 第2步：校验参数 - account和roleIds必须有
// 第3步：queryUserInfo() - 确认用户存在
// 第4步：queryAuthListByRoleIdAndAuthId() - 查询这些角色有哪些权限
// 第5步：循环authList，逐个插入 privilege_user_auth 记录
// 第6步：给每个权限归属标记 flag（0=个人，1=机构）
// 第7步：同步更新 person_division 表（个人归属）和 up_org_user 表（机构归属）
```

**⚠️ 出错了怎么办？**
- 抛 `CustomException("参数错误！账户不能为空！")`
- 抛 `CustomException("该人员信息不存在！")`
- 事务自动回滚，数据不会混乱

**💡 小白容易懵的地方**
1. `authIds` 是权限归属ID，不是角色ID，可以理解为"归哪个地区/部门管"
2. 方法内部会同时操作3张表（user_auth、person_division、up_org_user），是批量操作

---

#### `deleteUsersByIds(String[])` - 批量删除用户

> 🎯 **一句话人话**：把一批用户标记为"已删除"（逻辑删除）

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `userIds` | 用户ID数组 | `["user001", "user002", "user003"]` |

**📤 返回什么？**
无返回值，每个用户会被打上 `delete_at` 时间戳

**🔗 谁会用这个方法？**
- **直接调用**：`UserInfoApi` 的批量删除接口
- **触发场景**：管理员勾选多个用户，点击"批量删除"

**📖 方法内部一步一步在做什么？**
```java
// 第1步：校验userIds不能为空
// 第2步：循环每个userId
// 第3步：selectByPrimaryKey() - 查用户是否存在
// 第4步：如果不存在就跳过（continue）
// 第5步：设置 deleteAt = 当前时间
// 第6步：设置 modifier = 当前操作用户
// 第7步：updateByPrimaryKey() - 更新记录
```

**⚠️ 出错了怎么办？**
- 抛 `CustomException("参数错误！用户ID不能为空！")`
- 单个用户不存在不影响其他用户的删除

**💡 小白容易懵的地方**
1. 这是逻辑删除，不是真的从数据库抹掉，数据还在 `delete_at` 字段有记录
2. 删除用户后，用户的角色关联关系还在，只是这个用户登录不了了

---

#### `queryUsersByOrgIds(PrivilegeOrgUserInfoDto)` - 按机构ID列表查询用户

> 🎯 **一句话人话**：输入多个机构ID，查询这些机构下的所有用户（带分页）

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `privilegeOrgUserInfoDto.orgIds` | 机构ID列表 | `["org001", "org002", "org003"]` |
| `privilegeOrgUserInfoDto.pageIndex` | 页码 | `1` |
| `privilegeOrgUserInfoDto.pageSize` | 每页条数 | `10` |

**📤 返回什么？**
`ResultPage<UserInfoVo>` - 分页的用户列表，每个用户包含姓名、账号、所属机构名称等

**🔗 谁会用这个方法？**
- **直接调用**：`UserInfoApi` 的按机构查询接口
- **触发场景**：在机构管理页面，点击"查看该机构用户"

**📖 方法内部一步一步在做什么？**
```java
// 第1步：PageHelper.startPage() - 开启分页
// 第2步：selectUsersByOrgIds() - 一次性查出所有机构下的用户（数据库IN查询）
// 第3步：包装成 PageInfo 获取总数
// 第4步：循环每个用户，BeanUtils.copyProperties复制字段
// 第5步：查询用户的机构信息，拼上机构名称
// 第6步：LocalTimeUtils.parseLocalDateTime() - 转换时间格式
// 第7步：返回分页结果
```

**⚠️ 出错了怎么办？**
- orgIds为空时查全部用户
- 某个机构不存在，对应的用户机构信息会显示空字符串

**💡 小白容易懵的地方**
1. 数据库用的是 `IN` 查询，比如 `WHERE org_id IN ('org001','org002')`
2. 返回的用户列表里会拼上机构名称，方便前端展示

---

#### `deleteRolesByIds(String[])` - 删除用户角色关联

> 🎯 **一句话人话**：解除用户和角色的绑定关系

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `userRoleIds` | 用户-角色关联表的ID数组 | `["ur001", "ur002"]`（不是角色ID！是关联表ID） |

**📤 返回什么？**
无返回值，关联记录会被打上 `delete_at`

**🔗 谁会用这个方法？**
- **直接调用**：`setRoles()` 方法（第8步）重新设置角色时先清空旧的
- **触发场景**：给用户换角色时，先删后加

**📖 方法内部一步一步在做什么？**
```java
// 第1步：校验userRoleIds不能为空
// 第2步：获取当前时间now
// 第3步：循环每个userRoleId
// 第4步：selectUserRoleInfoById() - 查关联记录
// 第5步：如果不存在就跳过
// 第6步：设置 deleteAt = now（软删除）
// 第7步：设置 modifier = 当前操作用户
// 第8步：updateByPrimaryKey() - 更新
```

**⚠️ 出错了怎么办？**
- 抛 `CustomException("参数错误！人员角色表id不能为空！")`
- 关联记录不存在不影响其他删除操作

**💡 小白容易懵的地方**
1. 传的参数是 **用户-角色关联表的ID**，不是角色ID！要通过 `privilege_user_role_info` 表的ID来删除
2. 注意和 `deleteRolesByIds`（角色自己的删除）区分开

---

#### `queryRolesByUserId(PrivilegeUserRoleInfoDto)` - 查询用户的角色列表

> 🎯 **一句话人话**：查看某个用户被分配了哪些角色

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `privilegeUserRoleInfoDto.userId` | 用户ID | `"user-uuid-123"` |
| `privilegeUserRoleInfoDto.pageIndex` | 页码 | `1` |
| `privilegeUserRoleInfoDto.pageSize` | 每页条数 | `10` |

**📤 返回什么？**
`ResultPage<UserRoleInfoVo>` - 分页的角色列表

**🔗 谁会用这个方法？**
- **直接调用**：`UserInfoApi` 的"查看用户角色"接口
- **触发场景**：编辑用户时，查看该用户已有角色

**📖 方法内部一步一步在做什么？**
```java
// 第1步：校验userId不能为空
// 第2步：PageHelper.startPage() - 开启分页
// 第3步：selectByUserIdAndRoleId(userId, null) - 查询该用户的所有角色关联
// 第4步：包装成 PageInfo
// 第5步：循环每个关联记录
// 第6步：BeanUtils.copyProperties() - 复制字段到VO
// 第7步：查用户表获取 enable 状态
// 第8步：LocalTimeUtils.parseLocalDateTime() - 转换时间格式
// 第9步：返回分页结果
```

**⚠️ 出错了怎么办？**
- 抛 `CustomException("参数错误！人员ID不能为空！")`

**💡 小白容易懵的地方**
1. 返回的 `UserRoleInfoVo` 里有用户的 `enable` 状态（这个用户是否被禁用）
2. 注意和角色模块的 `queryAuthTreeByRoleId` 区分，那个是查角色有什么权限

---

### 2️⃣ OrgInfoServiceImpl 补充方法（14个）

---

#### `update(OrgInfoVo)` - 更新机构信息

> 🎯 **一句话人话**：修改机构的基本信息

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `orgInfoVo.id` | 机构ID | `"org-uuid-123"` |
| `orgInfoVo.code` | 机构编码 | `"866103001"` |
| `orgInfoVo.name` | 机构名称 | `"北京分公司"` |
| `orgInfoVo.enable` | 启用状态 | `0`（禁用）或 `1`（启用） |

**📤 返回什么？**
`Integer` - 受影响的行数（通常为1）

**🔗 谁会用这个方法？**
- **直接调用**：`OrgInfoApi` 的更新机构接口
- **触发场景**：编辑机构信息后保存

**📖 方法内部一步一步在做什么？**
```java
// 第1步：校验4个必填字段（id、code、name、enable）
// 第2步：selectOrg() - 查询原机构记录
// 第3步：BeanUtils.copyProperties() - 把新值复制到实体（但id不变）
// 第4步：设置 modifytime = 当前时间
// 第5步：设置 modifier = 当前操作用户
// 第6步：updateByPrimaryKey() - 更新数据库
```

**⚠️ 出错了怎么办？**
- 抛 `CustomException("缺少参数,机构id、机构编码、机构名称、机构状态不可为空")`

**💡 小白容易懵的地方**
1. 这里用的是 `BeanUtils.copyProperties`，会把 `vo` 里的空值也覆盖过去吗？不会，因为用的是 `copyProperties`（全量复制）
2. 机构编码 `code` 不允许重复，如果改成已存在的编码会报错

---

#### `queryOrgs(GetOrgInfoListDto)` - 分页查询机构

> 🎯 **一句话人话**：带条件筛选的分页查询机构列表

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `getOrgInfoListDto.pageVo` | 分页信息 | `{pageIndex:1, pageSize:10}` |
| `getOrgInfoListDto.code` | 机构编码（可选） | `"866"` |
| `getOrgInfoListDto.name` | 机构名称（可选） | `"北京"` |
| `getOrgInfoListDto.parentId` | 父机构ID（可选） | `"org-parent-123"` |

**📤 返回什么？**
`ResultPage<PrivilegeOrgInfo>` - 分页的机构列表

**🔗 谁会用这个方法？**
- **直接调用**：`OrgInfoApi` 的机构列表接口
- **触发场景**：打开机构管理页面，默认显示全部机构

**📖 方法内部一步一步在做什么？**
```java
// 第1步：从dto取出pageVo分页信息
// 第2步：新建PrivilegeOrgInfo对象
// 第3步：BeanUtils.copyProperties() - 把dto的可选参数复制到查询对象
// 第4步：PageHelper.startPage() - 开启分页
// 第5步：privilegeOrgInfoDao.select() - 执行动态查询（有多少填多少条件）
// 第6步：包装PageInfo返回
```

**⚠️ 出错了怎么办？**
- 参数全为空时查询全部机构
- 没有符合条件的机构时返回空分页列表

**💡 小白容易懵的地方**
1. 这个方法用的是 MyBatis 的动态 SQL，根据传了哪些参数自动拼接 WHERE 条件
2. 返回的是原始的 `PrivilegeOrgInfo` 实体，不是 VO

---

#### `queryOrgsById(String)` - 按ID查询单个机构

> 🎯 **一句话人话**：根据机构ID查询详情

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `id` | 机构ID | `"org-uuid-123"` |

**📤 返回什么？**
`PrivilegeOrgInfo` - 机构实体对象

**🔗 谁会用这个方法？**
- **直接调用**：`OrgInfoApi` 的机构详情接口
- **触发场景**：点击某个机构查看详情

**📖 方法内部一步一步在做什么？**
```java
// 第1步：privilegeOrgInfoDao.selectOrg() - 调用Mapper查询
// 第2步：返回单条机构记录
```

**⚠️ 出错了怎么办？**
- 如果机构不存在，返回 null
- 如果机构已被删除（deleteAt不为空），返回带删除标记的对象

**💡 小白容易懵的地方**
1. 这个方法没有校验机构是否已删除，如果需要校验要用 `getDetail()` 方法

---

#### `setSystemResources(OrgSysResourceDto)` - 设置机构系统资源

> 🎯 **一句话人话**：给机构分配系统（把某个系统"分配"给这个机构用）

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `orgSysResourceDto.orgId` | 机构ID | `"org-uuid-123"` |
| `orgSysResourceDto.systemId` | 系统ID | `"sys-uuid-456"` |
| `orgSysResourceDto.menuIds` | 菜单ID数组 | `["menu001", "menu002"]` |

**📤 返回什么？**
无返回值

**🔗 谁会用这个方法？**
- **直接调用**：`OrgInfoApi` 的分配系统接口
- **触发场景**：把某个系统（比如"体检系统"）分配给某个机构

**📖 方法内部一步一步在做什么？**
```java
// 第1步：校验机构ID和系统ID必填
// 第2步：selectByPrimaryKey() - 查机构是否存在
// 第3步：如果机构不存在则抛异常
// 第4步：privilegeOrgSystemDao.selectOrgSysInfo() - 查该机构已有的系统关联
// 第5步：循环menuIds，逐个插入 privilege_org_system 记录
// 第6步：每条记录设置 orgId、systemId、menuId、creator等
```

**⚠️ 出错了怎么办？**
- 抛 `CustomException("缺少参数")`
- 机构不存在时抛异常

**💡 小白容易懵的地方**
1. 一个机构可以关联多个系统，一个系统可以分配给多个机构（多对多关系）
2. menuIds 是该系统下的哪些菜单分配给这个机构

---

#### `querySystemsByOrgId(GetOrgSysInfoListDto)` - 查询机构下的系统列表

> 🎯 **一句话人话**：查看某个机构被分配了哪些系统

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `getOrgSysInfoListDto.orgId` | 机构ID | `"org-uuid-123"` |
| `getOrgSysInfoListDto.pageIndex` | 页码 | `1` |
| `getOrgSysInfoListDto.pageSize` | 每页条数 | `10` |

**📤 返回什么？**
`ResultPage<PrivilegeOrgSystem>` - 分页的机构-系统关联列表

**🔗 谁会用这个方法？**
- **直接调用**：`OrgInfoApi` 的查看机构系统列表接口
- **触发场景**：在机构详情页查看"已分配的系统"

**📖 方法内部一步一步在做什么？**
```java
// 第1步：PageHelper.startPage() - 开启分页
// 第2步：privilegeOrgSystemDao.selectOrgSysInfo() - 查询该机构的系统关联
// 第3步：包装PageInfo返回
```

**⚠️ 出错了怎么办？**
- orgId为空时可能查不到数据或报错

**💡 小白容易懵的地方**
1. 返回的是 `PrivilegeOrgSystem` 实体，里面有 orgId、systemId、menuId 三个ID

---

#### `deleteSystemsByIds(List<String>)` - 删除机构系统关联

> 🎯 **一句话人话**：取消机构对某些系统的分配

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `ids` | 机构-系统关联ID列表 | `["org-sys-001", "org-sys-002"]` |

**📤 返回什么？**
无返回值

**🔗 谁会用这个方法？**
- **直接调用**：`OrgInfoApi` 的删除机构系统接口
- **触发场景**：从某个机构移除某个系统的分配

**📖 方法内部一步一步在做什么？**
```java
// 第1步：校验ids不为空
// 第2步：循环每个id
// 第3步：selectByPrimaryKey() - 查关联记录
// 第4步：设置 deleteAt = 当前时间（软删除）
// 第5步：updateByPrimaryKey() - 更新
```

**⚠️ 出错了怎么办？**
- 抛 `CustomException("缺少参数")`
- 关联记录不存在不影响其他删除

**💡 小白容易懵的地方**
1. 这里删的是机构-系统关联关系，不是删除系统本身

---

#### `query(OrgQueryVo)` - 复杂组合查询机构

> 🎯 **一句话人话**：多条件组合查询机构，支持精确匹配、模糊搜索、树形结构返回

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `orgQueryVo.parentId` | 父机构ID | `"org-parent-123"` |
| `orgQueryVo.name` | 机构名称 | `"北京"` |
| `orgQueryVo.code` | 机构编码 | `"866"` |
| `orgQueryVo.enable` | 启用状态 | `1` |
| `orgQueryVo.queryType` | 查询类型 | `"tree"`（树形）或 `"list"`（列表） |

**📤 返回什么？**
根据 `queryType` 返回：
- `"tree"`：返回树形结构 `List<OrgTreeVo>`
- `"list"` 或其他：返回分页列表 `ResultPage<OrgTreeVo>`

**🔗 谁会用这个方法？**
- **直接调用**：`OrgInfoApi` 的高级查询接口
- **触发场景**：机构管理页的搜索功能

**📖 方法内部一步一步在做什么？**
```java
// 第1步：校验pageVo分页参数
// 第2步：如果parentId不为空，调用getidList()递归获取所有子机构ID
// 第3步：构建查询条件（多条件AND组合）
// 第4步：PageHelper.startPage() - 开启分页
// 第5步：privilegeOrgInfoDao.selectOrgInfoByQuery() - 执行复杂查询
// 第6步：循环结果，BeanUtils.copyProperties()复制到OrgTreeVo
// 第7步：如果queryType是tree，递归构建树形结构
// 第8步：返回树形或列表
```

**⚠️ 出错了怎么办？**
- 参数都为空时查全部
- parentId对应的机构不存在时返回空

**💡 小白容易懵的地方**
1. `getidList()` 是个递归方法，会把传入ID的所有子子孙孙都查出来
2. 这个方法约200行，是系统中比较复杂的查询方法

---

#### `getPartOrgTree(String)` - 获取部分机构树

> 🎯 **一句话人话**：从指定机构开始，向下构建子树

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `id` | 起始机构ID | `"org-uuid-123"` |

**📤 返回什么？**
`List<OrgTreeVo>` - 从该机构开始的子树

**🔗 谁会用这个方法？**
- **直接调用**：机构树展示组件
- **触发场景**：只显示某个大机构下的子机构树

**📖 方法内部一步一步在做什么？**
```java
// 第1步：selectOrg() - 查起始机构
// 第2步：BeanUtils.copyProperties() - 复制到OrgTreeVo
// 第3步：创建队列，用BFS（广度优先）遍历子机构
// 第4步：循环查子机构，BeanUtils.copyProperties复制
// 第5步：子机构加入父节点的children列表
// 第6步：返回树形结构
```

**⚠️ 出错了怎么办？**
- 机构不存在时返回空列表
- 有子机构就继续构建，没有就停止

**💡 小白容易懵的地方**
1. 和 `getOrgTree()`（全量树）不同，这个只返回从某个节点开始的子树
2. 用的是 BFS 队列遍历，不是递归

---

#### `updateOrgsByIds(String)` - 按ID更新机构

> 🎯 **一句话人话**：根据ID批量更新机构信息

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `id` | 机构ID | `"org-uuid-123"` |

**📤 返回什么？**
`Integer` - 受影响行数

**🔗 谁会用这个方法？**
- **直接调用**：`OrgInfoApi` 的更新接口
- **触发场景**：编辑机构信息保存

**📖 方法内部一步一步在做什么？**
```java
// 第1步：selectOrg() - 查原机构
// 第2步：设置修改人和修改时间
// 第3步：updateByPrimaryKey() - 更新
```

**⚠️ 出错了怎么办？**
- 机构不存在时可能报错

**💡 小白容易懵的地方**
1. 这个方法和 `update(OrgInfoVo)` 类似，但是根据ID直接更新

---

#### `deleteAtByIds(String[])` - 批量逻辑删除机构

> 🎯 **一句话人话**：一次性删除多个机构

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `id` | 机构ID数组 | `["org001", "org002", "org003"]` |

**📤 返回什么？**
无返回值

**🔗 谁会用这个方法？**
- **直接调用**：`OrgInfoApi` 的批量删除接口
- **触发场景**：勾选多个机构，点击"批量删除"

**📖 方法内部一步一步在做什么？**
```java
// 第1步：Arrays.asList() - 转成List
// 第2步：校验list不为空
// 第3步：循环每个id
// 第4步：selectByPrimaryKey() - 查机构
// 第5步：校验机构存在、未被删除、没有子机构
// 第6步：设置 deleteAt = 当前时间
// 第7步：updateByPrimaryKey() - 更新
```

**⚠️ 出错了怎么办？**
- 抛 `CustomException("缺少参数")`
- 抛 `CustomException("批量删除存在部分机构不存在")`
- 抛 `CustomException("批量删除存在部分机构存在子机构，不允许批量删除")`

**💡 小白容易懵的地方**
1. 有子机构的机构不允许删除，必须先删子机构
2. 如果10个机构里有1个有问题，整个批量操作会失败回滚

---

#### `setOrgSystemResources(OrgSystemInfoVo)` - 创建机构并设置系统资源

> 🎯 **一句话人话**：新建机构时同时分配系统资源（一步到位）

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `orgSystemInfoVo.orgName` | 机构名称 | `"新公司"` |
| `orgSystemInfoVo.parentId` | 父机构ID | `"org-parent-123"` |
| `orgSystemInfoVo.systemId` | 系统ID | `"sys-uuid-456"` |
| `orgSystemInfoVo.menuIds` | 菜单ID数组 | `["menu001", "menu002"]` |
| `orgSystemInfoVo.enable` | 启用状态 | `1` |
| `orgSystemInfoVo.orderIndex` | 排序号 | `1` |

**📤 返回什么？**
无返回值

**🔗 谁会用这个方法？**
- **直接调用**：`OrgInfoApi` 的新建机构接口
- **触发场景**：创建新机构并分配系统

**📖 方法内部一步一步在做什么？**
```java
// 第1步：校验必填参数（orgName、enable、parentId、orderIndex、systemId、menuIds）
// 第2步：selectOrgInfoByName() - 检查机构名是否重复
// 第3步：如果机构名已存在则抛异常
// 第4步：BeanUtils.copyProperties() - 复制属性
// 第5步：UUIDUtil.getUUID() - 生成新ID
// 第6步：设置创建人、创建时间
// 第7步：privilegeOrgInfoDao.insert() - 插入机构
// 第8步：循环menuIds，插入 privilege_org_system 记录
```

**⚠️ 出错了怎么办？**
- 抛 `CustomException("缺少必填参数")`
- 抛 `CustomException("该机构已被创建")`

**💡 小白容易懵的地方**
1. 这个方法同时操作机构表和机构-系统关联表
2. 如果只创建机构但不想分配系统，用 `create()` 方法

---

#### `updateOrgSystemResources(OrgSystemInfoVo)` - 更新机构及系统资源

> 🎯 **一句话人话**：修改机构信息，同时更新系统资源分配

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `orgSystemInfoVo.id` | 机构ID | `"org-uuid-123"` |
| `orgSystemInfoVo.orgName` | 机构名称 | `"新名字"` |
| `orgSystemInfoVo.systemId` | 系统ID | `"sys-uuid-456"` |
| `orgSystemInfoVo.menuIds` | 菜单ID数组 | `["menu001", "menu003"]` |

**📤 返回什么？**
无返回值

**🔗 谁会用这个方法？**
- **直接调用**：`OrgInfoApi` 的编辑机构接口
- **触发场景**：修改机构并重新分配系统资源

**📖 方法内部一步一步在做什么？**
```java
// 第1步：校验必填参数
// 第2步：selectOrg() - 查原机构
// 第3步：selectOrgInfoByName() - 检查新名称是否和其他机构重名
// 第4步：如果重名且不是自己，抛异常
// 第5步：BeanUtils.copyProperties() - 更新机构属性
// 第6步：privilegeOrgInfoDao.updateByPrimaryKey() - 更新机构
// 第7步：查该机构旧的系统关联
// 第8步：循环旧关联，设置 deleteAt（软删除旧的）
// 第9步：循环新的menuIds，插入新的 privilege_org_system 记录
```

**⚠️ 出错了怎么办？**
- 抛 `CustomException("缺少必填参数")`
- 抛 `CustomException("已有该机构名称")`

**💡 小白容易懵的地方**
1. 更新时会先删旧的系统关联，再插入新的（相当于替换）
2. 机构名称可以改，但不能改成已存在的名称

---

#### `getSystemList(String)` - 获取机构分配的系统列表（带菜单树）

> 🎯 **一句话人话**：查看某个机构分配了哪些系统，每个系统下有哪些菜单

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `id` | 机构ID | `"org-uuid-123"` |

**📤 返回什么？**
`ApiResponse<List<SystemMenuTreeVo>>` - 系统列表，每个系统下带菜单树

**🔗 谁会用这个方法？**
- **直接调用**：`OrgInfoApi` 的系统列表接口
- **触发场景**：机构详情页查看"系统及菜单"

**📖 方法内部一步一步在做什么？**
```java
// 第1步：如果id是"1"，自动替换为中国（根节点）
// 第2步：selectOrgSysInfo() - 查该机构的系统关联
// 第3步：用Stream去重，按systemId分组
// 第4步：循环每个系统
// 第5步：查系统信息，拼systemName
// 第6步：queryMenusBySystemIdAndOrgId() - 查该机构该系统下的菜单
// 第7步：筛选顶级菜单（parentId为空的）
// 第8步：调用buildTree()递归构建菜单树
// 第9步：返回系统列表（每个系统带菜单树）
```

**⚠️ 出错了怎么办？**
- id为"1"时自动映射到"中国"节点
- 某个系统下没有菜单则菜单树为空

**💡 小白容易懵的地方**
1. 返回结构是：`[{systemId, systemName, treeData: [菜单树]}, ...]`
2. 菜单树是从机构-系统关联表查的，不是从菜单表直接查

---

#### `buildTree(List<PrivilegeMenuInfoDto>, List<PrivilegeMenuInfoDto>)` - 构建菜单树

> 🎯 **一句话人话**：把平铺的菜单列表变成树形结构

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `collect` | 顶级菜单列表（父节点） | `[根菜单1, 根菜单2]` |
| `allItems` | 所有菜单列表 | `[根1, 子1-1, 子1-2, 根2, ...]` |

**📤 返回什么？**
`List<PrivilegeMenuInfoDto>` - 带 children 的树形结构

**🔗 谁会用这个方法？**
- **直接调用**：`getSystemList()`、`getMenuTree()`
- **触发场景**：前端需要树形菜单展示

**📖 方法内部一步一步在做什么？**
```java
// 第1步：循环每个顶级菜单（collect）
// 第2步：新建dtoList收集子节点
// 第3步：循环所有菜单（allItems）
// 第4步：如果某菜单的parentId等于当前父节点ID
// 第5步：递归调用buildTree，查找这个子节点的子节点
// 第6步：把递归结果加入dtoList
// 第7步：parent.setChildren(dtoList) - 设置子节点列表
// 第8步：返回带children的父节点列表
```

**⚠️ 出错了怎么办？**
- 如果allItems为空，直接返回collect
- 递归深度由数据决定，不会无限递归（有数据就有叶子节点）

**💡 小白容易懵的地方**
1. 这是个递归方法，自己调用自己
2. 每个节点有 `children` 字段存子节点，叶子节点的 `children` 是空列表

---

### 3️⃣ RoleInfoServiceImpl 补充方法（7个）

---

#### `getDetail(RoleDetailVo)` - 查询角色详情

> 🎯 **一句话人话**：查看某个角色的详细信息

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `roleDetailVo.id` | 角色ID | `"role-uuid-123"` |

**📤 返回什么？**
`ApiResponse<RoleDetailVo>` - 角色详情，包含基本信息+角色资源列表

**🔗 谁会用这个方法？**
- **直接调用**：`RoleInfoApi` 的角色详情接口
- **触发场景**：点击角色查看详情

**📖 方法内部一步一步在做什么？**
```java
// 第1步：校验id不为空
// 第2步：selectByPrimaryKey() - 查角色基本信息
// 第3步：如果角色为空或已删除，抛异常
// 第4步：BeanUtils.copyProperties() - 复制到RoleDetailVo
// 第5步：queryResourcesByRoleId() - 查该角色的资源列表
// 第6步：循环资源，查菜单名称
// 第7步：返回完整详情
```

**⚠️ 出错了怎么办？**
- 抛 `CustomException("缺少参数")`
- 角色不存在或已删除时抛异常

**💡 小白容易懵的地方**
1. 返回的详情里包含 `menuInfoList`（菜单信息列表）

---

#### `queryRoleTreeByOrgId(RolesQueryVo)` - 按机构查询角色树

> 🎯 **一句话人话**：查看某个机构下的所有角色（带分页）

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `rolesQueryVo.orgId` | 机构ID | `"org-uuid-123"` |
| `rolesQueryVo.pageIndex` | 页码 | `1` |
| `rolesQueryVo.pageSize` | 每页条数 | `10` |

**📤 返回什么？**
`ResultPage<RoleQueryDto>` - 分页的角色列表

**🔗 谁会用这个方法？**
- **直接调用**：`RoleInfoApi` 的角色列表接口
- **触发场景**：打开角色管理页面

**📖 方法内部一步一步在做什么？**
```java
// 第1步：校验orgId不为空
// 第2步：PageHelper.startPage() - 开启分页
// 第3步：如果有parentId，调用getidList()获取所有子机构ID
// 第4步：privilegeRoleInfoDao.queryRolesByOrgIds() - 查询角色列表
// 第5步：包装PageInfo返回
```

**⚠️ 出错了怎么办？**
- 抛 `CustomException("缺少机构ID")`

**💡 小白容易懵的地方**
1. 如果传了parentId，会查出该机构及所有子机构的角色

---

#### `deleteResourcesByIds(ResourceDelVo)` - 删除角色资源关联

> 🎯 **一句话人话**：从角色上移除某些菜单权限

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `resourceDelVo.ids` | 角色-资源关联ID列表 | `["rr001", "rr002"]` |

**📤 返回什么？**
`CommonReqVo` - 操作结果

**🔗 谁会用这个方法？**
- **直接调用**：`RoleInfoApi` 的删除资源接口
- **触发场景**：编辑角色时移除某些菜单权限

**📖 方法内部一步一步在做什么？**
```java
// 第1步：校验ids不为空
// 第2步：queryResourcesByIds() - 查这些关联记录
// 第3步：循环每个记录
// 第4步：设置 deleteAt = 当前时间
// 第5步：设置 modifier = 当前用户
// 第6步：updateByPrimaryKey() - 更新
```

**⚠️ 出错了怎么办？**
- ids为空时返回失败
- 单个不存在不影响其他删除

**💡 小白容易懵的地方**
1. 删除的是角色-资源关联关系，不是删除角色本身

---

#### `updateEnable(UpdateEnableVo)` - 启用/禁用角色

> 🎯 **一句话人话**：切换角色的启用状态

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `updateEnableVo.id` | 角色ID | `"role-uuid-123"` |

**📤 返回什么？**
`String` - null表示成功，非空表示错误信息

**🔗 谁会用这个方法？**
- **直接调用**：`RoleInfoApi` 的启用禁用接口
- **触发场景**：点击角色的启用/禁用按钮

**📖 方法内部一步一步在做什么？**
```java
// 第1步：selectByPrimaryKey() - 查角色
// 第2步：如果不存在，返回"未查找到该角色"
// 第3步：如果已删除，返回"该角色已删除"
// 第4步：如果enable=1，改为0；如果是0或null，改为1
// 第5步：设置 modifier 和 modifytime
// 第6步：updateByPrimaryKey() - 更新
```

**⚠️ 出错了怎么办？**
- 返回字符串表示错误信息
- 正常情况返回null表示成功

**💡 小白容易懵的地方**
1. 禁用角色后，所有拥有这个角色的用户都会失去相应权限
2. 如果用户正在使用系统，禁用可能不会立即生效（取决于缓存策略）

---

#### `deleteRolesByIds(RoleListDeleteVo)` - 批量删除角色

> 🎯 **一句话人话**：一次性删除多个角色

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `roleListDeleteVo.ids` | 角色ID列表 | `["role001", "role002"]` |

**📤 返回什么？**
`CommonReqVo` - 包含被删除角色名称列表的JSON

**🔗 谁会用这个方法？**
- **直接调用**：`RoleInfoApi` 的批量删除角色接口
- **触发场景**：勾选多个角色，点击"批量删除"

**📖 方法内部一步一步在做什么？**
```java
// 第1步：queryRoleByIds() - 批量查角色
// 第2步：过滤掉已删除的角色（deleteAt != null）
// 第3步：循环每个角色
// 第4步：设置 deleteAt = 当前时间
// 第5步：设置 modifier 和 modifytime
// 第6步：updateByPrimaryKey() - 更新
// 第7步：收集被删除的角色名称到roleDeleteList
// 第8步：返回成功状态和角色名称列表
```

**⚠️ 出错了怎么办？**
- 如果某个角色不存在，会被过滤掉继续执行
- 已删除的角色也会被过滤

**💡 小白容易懵的地方**
1. 只会删除未删除的角色，已删除的会被忽略
2. 返回的JSON里是被删除角色的名称，前端用来显示"删除成功：xxx, xxx"

---

#### `queryAuthTreeByRoleId(AuthQueryDto)` - 查询角色拥有的权限树

> 🎯 **一句话人话**：查看某个角色有哪些权限

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `authQueryDto.roleList` | 角色ID列表 | `["role001", "role002"]` |
| `authQueryDto.pageIndex` | 页码 | `1` |
| `authQueryDto.pageSize` | 每页条数 | `10` |

**📤 返回什么？**
`CommonReqVo` - 包含分页权限列表的JSON

**🔗 谁会用这个方法？**
- **直接调用**：`RoleInfoApi` 的权限树查询接口
- **触发场景**：给用户分配权限时，查看该角色已有权限

**📖 方法内部一步一步在做什么？**
```java
// 第1步：如果有分页参数，开启PageHelper
// 第2步：queryParentMenuIdByRoleId() - 根据角色ID查对应的父级菜单
// 第3步：queryAuthListByMenuId() - 根据菜单ID列表查权限
// 第4步：包装PageInfo返回
```

**⚠️ 出错了怎么办？**
- roleList为空时直接返回空结果
- 数据库没有对应权限时返回空分页

**💡 小白容易懵的地方**
1. 查的是权限（PrivilegeAuthInfo），不是菜单
2. 先查角色的菜单，再根据菜单查权限

---

### 4️⃣ MenuInfoServiceImpl 补充方法（10个）

---

#### `getDetail(PrivilegeMenuInfoVo)` - 查询菜单详情

> 🎯 **一句话人话**：查看某个菜单的详细信息

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `privilegeMenuInfoVo.id` | 菜单ID | `"menu-uuid-123"` |

**📤 返回什么？**
`ApiResponse<PrivilegeMenuInfo>` - 菜单详情

**🔗 谁会用这个方法？**
- **直接调用**：`MenuInfoApi` 的菜单详情接口
- **触发场景**：点击菜单查看详情

**📖 方法内部一步一步在做什么？**
```java
// 第1步：校验id不为空
// 第2步：privilegeMenuInfoDao.selectByPrimaryKey() - 查菜单
// 第3步：如果菜单不存在或已删除，抛异常
// 第4步：查关联的机构系统信息
// 第5步：返回菜单详情
```

**⚠️ 出错了怎么办？**
- 抛 `CustomException("菜单不存在")`

**💡 小白容易懵的地方**
1. 如果菜单已删除，也查不到

---

#### `queryMenusBySystemId(PrivilegeMenuInfoVo)` - 按系统ID查询菜单

> 🎯 **一句话人话**：查看某个系统下有哪些菜单

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `privilegeMenuInfoVo.systemId` | 系统ID | `"sys-uuid-456"` |
| `privilegeMenuInfoVo.pageIndex` | 页码 | `1` |
| `privilegeMenuInfoVo.pageSize` | 每页条数 | `10` |

**📤 返回什么？**
`ApiResponse<ResultPage<PrivilegeMenuInfoDto>>` - 分页菜单列表

**🔗 谁会用这个方法？**
- **直接调用**：`MenuInfoApi` 的菜单列表接口
- **触发场景**：打开菜单管理页面

**📖 方法内部一步一步在做什么？**
```java
// 第1步：校验systemId不为空
// 第2步：PageHelper.startPage() - 开启分页
// 第3步：privilegeMenuInfoDao.queryMenusBySystemId() - 查菜单列表
// 第4步：循环查父菜单名称
// 第5步：包装PageInfo返回
```

**⚠️ 出错了怎么办？**
- 抛 `CustomException("系统id不能为空")`

**💡 小白容易懵的地方**
1. 返回的菜单列表里，每个菜单会拼上父菜单名称

---

#### `buildTree(List<PrivilegeMenuInfoDto>, List<PrivilegeMenuInfoDto>)` - 构建菜单树

> 🎯 **一句话人话**：把平铺菜单变成树形结构

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `collect` | 顶级菜单列表 | `[根菜单1, 根菜单2]` |
| `allItems` | 所有菜单列表 | `[根1, 子1-1, 子1-2, 根2, ...]` |

**📤 返回什么？**
`List<PrivilegeMenuInfoDto>` - 带 children 的树

**🔗 谁会用这个方法？**
- **直接调用**：`getMenuTree()`
- **触发场景**：前端需要树形菜单

**📖 方法内部一步一步在做什么？**
```java
// 第1步：循环每个顶级菜单
// 第2步：新建dtoList
// 第3步：循环所有菜单，找parentId匹配的
// 第4步：递归调用自己找子子节点
// 第5步：parent.setChildren(dtoList)
// 第6步：返回树
```

**⚠️ 出错了怎么办？**
- 数据为空时直接返回空列表

**💡 小白容易懵的地方**
1. 和 OrgInfoServiceImpl 的 buildTree 是同一个逻辑

---

#### `enable(PrivilegeMenuInfoVo)` - 启用/禁用菜单

> 🎯 **一句话人话**：切换菜单的启用状态

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `privilegeMenuInfoVo.id` | 菜单ID | `"menu-uuid-123"` |
| `privilegeMenuInfoVo.enable` | 启用状态 | `0`（禁用）或 `1`（启用） |

**📤 返回什么？**
`ApiResponse` - 操作结果

**🔗 谁会用这个方法？**
- **直接调用**：`MenuInfoApi` 的启用禁用接口
- **触发场景**：点击菜单的启用/禁用按钮

**📖 方法内部一步一步在做什么？**
```java
// 第1步：新建菜单对象
// 第2步：设置id和enable
// 第3步：privilegeMenuInfoService.save() - 保存更新
// 第4步：返回成功
```

**⚠️ 出错了怎么办？**
- save方法本身会处理异常

**💡 小白容易懵的地方**
1. 禁用的菜单不会显示给用户，但角色关联还在
2. 如果角色配置了禁用菜单，权限验证时可能有问题

---

#### `checkRepeat(PrivilegeMenuServiceVo)` - 检查服务接口URL是否重复

> 🎯 **一句话人话**：新增/修改/删除服务接口时，检查是否有重复的URL

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `vo.addservicesList` | 新增的接口列表 | `[{serviceUrl:"/api/test"}]` |
| `vo.updateservicesList` | 修改的接口列表 | `[{serviceUrl:"/api/update"}]` |
| `vo.deleteservicesList` | 删除的接口列表 | `[{serviceUrl:"/api/del"}]` |

**📤 返回什么？**
`boolean` - true表示有重复，false表示没有

**🔗 谁会用这个方法？**
- **直接调用**：`reviseServices()` 方法
- **触发场景**：批量保存服务接口前校验

**📖 方法内部一步一步在做什么？**
```java
// 第1步：新建url列表
// 第2步：循环新增列表，把serviceUrl加入url列表
// 第3步：循环修改列表，把serviceUrl加入url列表
// 第4步：循环删除列表，把serviceUrl加入url列表
// 第5步：hasDuplicates(url) - 判断是否有重复
// 第6步：返回true/false
```

**⚠️ 出错了怎么办？**
- 返回true时，reviseServices会返回失败

**💡 小白容易懵的地方**
1. 这个方法检查的是"新增+修改+删除列表内部"是否有重复，不是和数据库比

---

#### `hasDuplicates(List<String>)` - 判断列表是否有重复元素

> 🎯 **一句话人话**：用Collections.frequency检查是否有重复

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `list` | 字符串列表 | `["a", "b", "a", "c"]` |

**📤 返回什么？**
`boolean` - true有重复，false没有

**🔗 谁会用这个方法？**
- **直接调用**：`checkRepeat()` 方法
- **触发场景**：URL重复校验

**📖 方法内部一步一步在做什么？**
```java
// 第1步：循环每个元素
// 第2步：Collections.frequency(list, element) - 统计出现次数
// 第3步：如果>1，说明有重复，返回true
// 第4步：都没重复返回false
```

**⚠️ 出错了怎么办？**
- 空列表返回false（没有重复）

**💡 小白容易懵的地方**
1. `Collections.frequency` 是JDK自带方法，统计元素出现次数

---

#### `queryServicesTree(PrivilegeMenuServiceVo)` - 查询服务树

> 🎯 **一句话人话**：查看菜单的服务接口树

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `vo.menuId` | 菜单ID | `"menu-uuid-123"` |
| `vo.menuChrilrenId` | 子菜单ID（可选） | `"menu-child-456"` |

**📤 返回什么？**
`ApiResponse<List<PrivilegeMenuInfoDto>>` - 服务树

**🔗 谁会用这个方法？**
- **直接调用**：`MenuInfoApi` 的服务树接口
- **触发场景**：查看菜单的服务接口

**📖 方法内部一步一步在做什么？**
```java
// 第1步：获取orgId
// 第2步：如果有menuChrilrenId，查父菜单和子菜单，拼成树
// 第3步：如果只有menuId，判断是父ID还是子ID
// 第4步：如果menuId是子ID，查父节点，把子节点加入父的children
// 第5步：如果menuId是父ID，查子节点列表
// 第6步：如果都没有，查全部服务树
// 第7步：buildTree()递归构建树
// 第8步：返回
```

**⚠️ 出错了怎么办？**
- menuId为空时查全部

**💡 小白容易懵的地方**
1. menuId可能传的是父ID也可能是子ID，方法内部会自动判断

---

#### `queryChildrenMenus(PrivilegeMenuServiceVo)` - 查询子菜单

> 🎯 **一句话人话**：查看某个菜单的所有直接子菜单

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `vo.menuId` | 父菜单ID | `"menu-uuid-123"` |

**📤 返回什么？**
`ApiResponse<List<PrivilegeMenuInfoDto>>` - 子菜单列表

**🔗 谁会用这个方法？**
- **直接调用**：`MenuInfoApi` 的子菜单查询接口
- **触发场景**：点击菜单节点查看子菜单

**📖 方法内部一步一步在做什么？**
```java
// 第1步：获取orgId
// 第2步：新建dto，设置parentId为menuId
// 第3步：privilegeMenuInfoService.getChildrenMenus() - 查询
// 第4步：返回结果
```

**⚠️ 出错了怎么办？**
- menuId为空时查全部（parentId为空会查出顶级）

**💡 小白容易懵的地方**
1. 只查直接子菜单，不查孙子辈

---

#### `queryChildrenServicesMenus(PrivilegeMenuServiceVo)` - 查询子服务菜单

> 🎯 **一句话人话**：查看菜单的服务接口列表

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `vo.menuId` | 菜单ID | `"menu-uuid-123"` |

**📤 返回什么？**
`ApiResponse<List<PrivilegeMenuService>>` - 服务接口列表

**🔗 谁会用这个方法？**
- **直接调用**：`MenuInfoApi` 的服务列表接口
- **触发场景**：查看菜单下有哪些接口

**📖 方法内部一步一步在做什么？**
```java
// 第1步：BeanUtils.copyProperties() - 复制到dto
// 第2步：privilegeMenuServiceService.queryChildrenServicesMenus() - 查询
// 第3步：返回服务列表
```

**⚠️ 出错了怎么办？**
- menuId为空可能查不到

**💡 小白容易懵的地方**
1. 这里查的是 PrivilegeMenuService（服务接口），不是 PrivilegeMenuInfo（菜单）

---

#### `queryDataStatistics(PrivilegeMenuServiceVo)` - 查询菜单数据统计

> 🎯 **一句话人话**：统计系统的菜单和服务接口数量

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| 无特殊参数 | 使用当前用户的orgId | - |

**📤 返回什么？**
`ApiResponse<PrivilegeMenuServiceDto>` - 包含三个数量：
- `systemMenuNum`：系统菜单数量
- `authMenuNum`：配置了接口的菜单数量
- `authInterfaceNum`：配置接口数量

**🔗 谁会用这个方法？**
- **直接调用**：`MenuInfoApi` 的统计接口
- **触发场景**：菜单管理页面的统计卡片

**📖 方法内部一步一步在做什么？**
```java
// 第1步：获取orgId
// 第2步：querySystemMenuNum() - 查菜单总数
// 第3步：queryauthMenuNum() - 查配置了接口的菜单数
// 第4步：queryAuthInterfaceNum() - 查接口总数
// 第5步：组装dto返回
```

**⚠️ 出错了怎么办？**
- 数字为0时正常返回

**💡 小白容易懵的地方**
1. authMenuNum是"有多少个菜单配置了接口"，authInterfaceNum是"总共有多少个接口"

---

### 5️⃣ PrivilegeMenuInfoServiceImpl 补充方法（9个）

> 🎯 这个类所有方法都是PrivilegeMenuInfoService接口的实现，是对DAO层的封装代理。

---

#### `getMenuOrgTree(PrivilegeMenuInfoDto)` - 获取菜单机构树

> 🎯 **一句话人话**：查询菜单的机构树（用于按机构筛选菜单）

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `dto.systemId` | 系统ID | `"sys-uuid-456"` |
| `dto.orgId` | 机构ID | `"org-uuid-123"` |

**📤 返回什么？**
`List<PrivilegeMenuInfoDto>` - 菜单列表

**🔗 谁会用这个方法？**
- **直接调用**：`MenuInfoServiceImpl.getMenuTree()`
- **触发场景**：构建菜单树时先查所有菜单

**📖 方法内部一步一步在做什么？**
```java
// 第1步：privilegeMenuInfoDao.getMenuOrgTree(dto) - 调用Mapper
// 第2步：返回结果列表
```

**💡 小白容易懵的地方**
1. 这个方法就是调用DAO层，没有额外逻辑

---

#### `queryInfo(PrivilegeMenuInfo)` - 查询菜单信息

> 🎯 **一句话人话**：按条件查询菜单列表

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `info.url` | 菜单URL | `"/api/user"` |
| `info.name` | 菜单名称 | `"用户管理"` |

**📤 返回什么？**
`List<PrivilegeMenuInfo>` - 菜单列表

**🔗 谁会用这个方法？**
- **直接调用**：`MenuInfoServiceImpl.createMenu()` 重复校验
- **触发场景**：创建菜单时检查URL或名称是否重复

**📖 方法内部一步一步在做什么？**
```java
// 第1步：privilegeMenuInfoDao.queryInfo(info) - 调用Mapper
// 第2步：返回结果
```

**💡 小白容易懵的地方**
1. MyBatis会根据info里非空的字段自动拼接WHERE条件

---

#### `getChildrenMenus(PrivilegeMenuInfoDto)` - 获取子菜单

> 🎯 **一句话人话**：根据父菜单ID查询子菜单

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `dto.parentId` | 父菜单ID | `"parent-menu-id"` |
| `dto.orgId` | 机构ID | `"org-uuid-123"` |

**📤 返回什么？**
`List<PrivilegeMenuInfoDto>` - 子菜单列表

**🔗 谁会用这个方法？**
- **直接调用**：`MenuInfoServiceImpl.queryChildrenMenus()`、`queryServicesTree()`

**📖 方法内部一步一步在做什么？**
```java
// 第1步：privilegeMenuInfoDao.getChildrenMenus(dto) - 调用Mapper
// 第2步：返回结果
```

---

#### `queryServicesTree(PrivilegeMenuInfoDto)` - 查询服务树

> 🎯 **一句话人话**：查询菜单的服务树（带机构筛选）

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `dto.orgId` | 机构ID | `"org-uuid-123"` |

**📤 返回什么？**
`List<PrivilegeMenuInfoDto>` - 菜单列表

**🔗 谁会用这个方法？**
- **直接调用**：`MenuInfoServiceImpl.queryServicesTree()`

**📖 方法内部一步一步在做什么？**
```java
// 第1步：privilegeMenuInfoDao.queryServicesTree(dto) - 调用Mapper
// 第2步：返回结果
```

---

#### `selectMenuInfoById(String)` - 按ID查询菜单

> 🎯 **一句话人话**：根据菜单ID查询详情

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `id` | 菜单ID | `"menu-uuid-123"` |

**📤 返回什么？**
`PrivilegeMenuInfoDto` - 菜单详情

**🔗 谁会用这个方法？**
- **直接调用**：`MenuInfoServiceImpl.queryServicesTree()`

**📖 方法内部一步一步在做什么？**
```java
// 第1步：privilegeMenuInfoDao.selectMenuInfoById(id) - 调用Mapper
// 第2步：返回单条记录
```

---

#### `querySystemMenuNum(PrivilegeMenuInfoDto)` - 查询系统菜单数量

> 🎯 **一句话人话**：统计某个机构的菜单总数

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `dto.orgId` | 机构ID | `"org-uuid-123"` |

**📤 返回什么？**
`Integer` - 菜单数量

**🔗 谁会用这个方法？**
- **直接调用**：`MenuInfoServiceImpl.queryDataStatistics()`

**📖 方法内部一步一步在做什么？**
```java
// 第1步：privilegeMenuInfoDao.querySystemMenuNum(dto) - 调用Mapper统计
// 第2步：返回数量
```

---

#### `queryauthMenuNum(PrivilegeMenuInfoDto)` - 查询授权菜单数量

> 🎯 **一句话人话**：统计配置了接口的菜单数量

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `dto.orgId` | 机构ID | `"org-uuid-123"` |

**📤 返回什么？**
`Integer` - 有接口的菜单数量

**🔗 谁会用这个方法？**
- **直接调用**：`MenuInfoServiceImpl.queryDataStatistics()`

**📖 方法内部一步一步在做什么？**
```java
// 第1步：privilegeMenuInfoDao.queryauthMenuNum(dto) - 调用Mapper统计
// 第2步：返回数量
```

---

#### `queryMenuOrder(PrivilegeMenuInfoDto)` - 查询菜单排序

> 🎯 **一句话人话**：查询某父菜单下的所有子菜单（用于排序）

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `dto.parentId` | 父菜单ID | `"parent-menu-id"` |
| `dto.orgId` | 机构ID | `"org-uuid-123"` |

**📤 返回什么？**
`List<PrivilegeMenuInfo>` - 按orderIndex排序的子菜单列表

**🔗 谁会用这个方法？**
- **直接调用**：`modifyOrder()` 方法

**📖 方法内部一步一步在做什么？**
```java
// 第1步：privilegeMenuInfoDao.queryMenuOrder(dto) - 调用Mapper
// 第2步：返回列表（已按orderIndex排序）
```

---

#### `modifyOrder(PrivilegeMenuInfoVo, PrivilegeMenuInfo)` - 修改菜单排序

> 🎯 **一句话人话**：调整菜单的顺序

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `vo.id` | 要移动的菜单ID | `"menu-uuid-123"` |
| `vo.parentId` | 父菜单ID | `"parent-menu-id"` |
| `vo.orderIndex` | 目标位置 | `2`（移到第2位） |
| `info` | 如果是新建则为null，编辑则为菜单对象 | null 或 PrivilegeMenuInfo |

**📤 返回什么？**
`String` - null成功，"排序错误"表示失败

**🔗 谁会用这个方法？**
- **直接调用**：`MenuInfoServiceImpl.createMenu()`、`updateMenu()`
- **触发场景**：拖拽菜单排序或设置orderIndex

**📖 方法内部一步一步在做什么？**
```java
// 第1步：获取orgId
// 第2步：如果有parentId
// 第3步：queryMenuOrder() - 查该父菜单下所有子菜单
// 第4步：如果要移动的是新菜单，先查出来
// 第5步：从列表中移除当前菜单（如果有）
// 第6步：把菜单插入到目标位置
// 第7步：循环更新所有菜单的orderIndex
// 第8步：返回null或"排序错误"
```

**⚠️ 出错了怎么办？**
- 返回"排序错误"时，前端会提示排序失败

**💡 小白容易懵的地方**
1. orderIndex从1开始，不是从0开始
2. 如果目标位置超出范围，会自动调整到末尾

---

### 6️⃣ PrivilegeMenuServiceServiceImpl 补充方法（2个）

> 🎯 这个类所有方法都是PrivilegeMenuServiceService接口的实现。

---

#### `queryChildrenServicesMenus(PrivilegeMenuServiceDto)` - 查询子服务菜单

> 🎯 **一句话人话**：查询某个菜单下的服务接口列表

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `dto.menuId` | 菜单ID | `"menu-uuid-123"` |

**📤 返回什么？**
`List<PrivilegeMenuService>` - 服务接口列表

**🔗 谁会用这个方法？**
- **直接调用**：`MenuInfoServiceImpl.queryChildrenServicesMenus()`、`reviseServices()`

**📖 方法内部一步一步在做什么？**
```java
// 第1步：privilegeMenuServiceDao.queryChildrenServicesMenus(dto) - 调用Mapper
// 第2步：返回服务列表
```

---

#### `queryAuthInterfaceNum(PrivilegeMenuInfoDto)` - 查询授权接口数量

> 🎯 **一句话人话**：统计配置的总接口数量

**📥 需要什么？**

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| `dto.orgId` | 机构ID | `"org-uuid-123"` |

**📤 返回什么？**
`Integer` - 接口数量

**🔗 谁会用这个方法？**
- **直接调用**：`MenuInfoServiceImpl.queryDataStatistics()`

**📖 方法内部一步一步在做什么？**
```java
// 第1步：privilegeMenuServiceDao.queryAuthInterfaceNum(dto) - 调用Mapper统计
// 第2步：返回数量
```

---

### 7️⃣ 工具类补充

---

#### 📦 NotBlankFieldCopy - 非空字段拷贝工具

> 🎯 **一句话人话**：只拷贝源对象中非空（not null）的字段到目标对象

**🏠 生活比喻**：就像填表格时，只填写有内容的格子，空的格子保持原样

**📝 核心代码解析**

```java
// 第1步：fieldPropertiesCopy(T origin, T target)
// 遍历源对象的所有字段
for (Field sourceField : sourceFields) {
    sourceField.setAccessible(true); // 设置可访问私有字段
    oriValue = sourceField.get(origin); // 获取源字段值
    if (oriValue == null) {
        continue; // 如果是null就跳过，不拷贝
    }
    // 在目标对象上找同名字段，设置值
    Field targetField = targetClazz.getDeclaredField(sourceField.getName());
    targetField.setAccessible(true);
    targetField.set(target, oriValue);
}
```

**💡 什么时候用？**
- 更新用户信息时，只更新传了值的字段，其他字段保持原样
- RoleInfoServiceImpl.updateRole() 里用了这个方法

**⚠️ 注意事项**
1. 字段名必须完全一致才能拷贝
2. 空字符串""不会被认为是非空，会被跳过

---

#### 📦 UserUtils - 用户上下文工具类

> 🎯 **一句话人话**：获取当前登录用户的信息（线程级别存储）

**🏠 生活比喻**：就像在一个请求的"流水线"上放一个对讲机，任何工位都能拿到当前是谁在操作

**📝 核心代码解析**

```java
// ThreadLocal：每个线程独立的存储空间
public static ThreadLocal<User> threadLocal = new ThreadLocal<>();

// 获取当前用户
public static User getUser() {
    User localUser = threadLocal.get();
    if (localUser == null) {
        // 如果没设置，返回默认的"人保健康"用户
        localUser = new User();
        localUser.setUserId("000000");
        localUser.setUserName("人保健康");
        // ...设置默认值
    }
    return localUser;
}

// 设置当前用户（登录时调用）
public static void setUser(User user) {
    threadLocal.set(user);
}

// 清理（请求结束时调用，防止内存泄漏）
public static void remove() {
    threadLocal.remove();
}
```

**💡 什么场景用？**
- 任何Service方法里想知道"当前是谁在操作"，就调用 `UserUtils.getUser()`
- 创建人/修改人字段、获取用户的orgId等

**⚠️ 注意事项**
1. ThreadLocal 是线程隔离的，不同请求不会串数据
2. 一定要在请求结束时调用 `remove()`，否则可能内存泄漏

---

#### 📦 User - 用户上下文对象

> 🎯 **一句话人话**：存储当前登录用户的信息

**📝 主要字段**

| 字段 | 含义 |
|------|------|
| `userId` | 用户ID |
| `userName` | 用户姓名 |
| `userAccount` | 用户账号 |
| `orgId` | 机构ID |
| `orgCode` | 机构编码 |
| `orgName` | 机构名称 |
| `roleList` | 角色列表 |
| `isProperty` | 是否财险人员 |
| `isInsurance` | 是否医保人员 |
| `loginDate` | 登录时间 |
| `endLoginDate` | 登录失效时间 |

**💡 什么时候用？**
- 需要获取当前用户信息时，通过 `UserUtils.getUser()` 获取

---

#### 📦 UniqueIDGenerator - 唯一ID生成器

> 🎯 **一句话人话**：生成不带横杠的UUID

**📝 核心代码**

```java
public static String generateUniqueID() {
    return UUID.randomUUID().toString().replaceAll("-", "");
}
```

**💡 什么场景用？**
- 生成数据库主键ID
- RoleInfoServiceImpl 里创建角色和资源时用这个生成ID

**⚠️ 注意事项**
1. UUID是几乎不可能重复的
2. 去掉横杠后是32位字符串

**📖 UUID打比方**
- 就像给每个数据发一张**独一无二的身份证号**
- 全世界同时生成的UUID也不会重复

---

#### 📦 AesUtil - AES加密解密工具

> 🎯 **一句话人话**：AES对称加密解密工具类

**🏠 生活比喻**：就像一把钥匙能锁能开，加密用钥匙锁上，解密用同一把钥匙打开

**📝 核心方法**

| 方法 | 作用 | 例子 |
|------|------|------|
| `aesEncrypt(content)` | 加密内容 | `"密码"` → `"abc123xxx=="` |
| `aesDecrypt(encrypt)` | 解密内容 | `"abc123xxx=="` → `"密码"` |
| `isEncrypted(data)` | 判断是否已加密 | 检查字符串是否是Base64格式 |

**📝 配置项**

| 配置 | 默认值 | 含义 |
|------|--------|------|
| `utils.aes.KEY` | `abcdefgabcdefg12` | 密钥（16位） |
| `utils.aes.ALGORITHMSTR` | `AES/ECB/PKCS5Padding` | 算法模式 |

**⚠️ 注意事项**
1. 加密和解密用的必须是**同一把钥匙**
2. ECB模式适合小数据量，大数据量建议用CBC模式
3. 密钥长度必须是16字节（128位）

**💡 AES加密打比方**
- 想象一个**保险箱**：
  - 你有一把钥匙（KEY）
  - 把文件锁进保险箱（AES加密）
  - 别人没有钥匙打不开
  - 你用同一把钥匙可以打开（AES解密）

---

## 📝 附录：补充方法速查表

### UserInfoServiceImpl 补充方法

| 方法名 | 一句话说明 | 关联表 |
|--------|------------|--------|
| `setAuths` | 给用户分配权限归属 | privilege_user_auth, person_division, up_org_user |
| `deleteUsersByIds` | 批量删除用户 | privilege_user_info |
| `queryUsersByOrgIds` | 按机构ID列表查询用户 | privilege_user_info |
| `deleteRolesByIds` | 删除用户角色关联 | privilege_user_role_info |
| `queryRolesByUserId` | 查询用户的角色列表 | privilege_user_role_info |

### OrgInfoServiceImpl 补充方法

| 方法名 | 一句话说明 | 关联表 |
|--------|------------|--------|
| `update` | 更新机构信息 | privilege_org_info |
| `queryOrgs` | 分页查询机构 | privilege_org_info |
| `queryOrgsById` | 按ID查询机构 | privilege_org_info |
| `setSystemResources` | 设置机构系统资源 | privilege_org_system |
| `querySystemsByOrgId` | 查询机构下的系统 | privilege_org_system |
| `deleteSystemsByIds` | 删除机构系统 | privilege_org_system |
| `query` | 复杂组合查询机构 | privilege_org_info |
| `getPartOrgTree` | 获取部分机构树 | privilege_org_info |
| `updateOrgsByIds` | 按ID更新机构 | privilege_org_info |
| `deleteAtByIds` | 批量删除机构 | privilege_org_info |
| `setOrgSystemResources` | 创建机构并设置系统 | privilege_org_info, privilege_org_system |
| `updateOrgSystemResources` | 更新机构及系统 | privilege_org_info, privilege_org_system |
| `getSystemList` | 获取系统列表（带菜单树） | privilege_org_system |
| `buildTree` | 构建菜单树 | - |

### RoleInfoServiceImpl 补充方法

| 方法名 | 一句话说明 | 关联表 |
|--------|------------|--------|
| `getDetail` | 查询角色详情 | privilege_role_info |
| `queryRoleTreeByOrgId` | 按机构查询角色树 | privilege_role_info |
| `deleteResourcesByIds` | 删除角色资源关联 | privilege_role_resource |
| `updateEnable` | 启用/禁用角色 | privilege_role_info |
| `deleteRolesByIds` | 批量删除角色 | privilege_role_info |
| `queryAuthTreeByRoleId` | 查询角色权限树 | privilege_auth_info |

### MenuInfoServiceImpl 补充方法

| 方法名 | 一句话说明 | 关联表 |
|--------|------------|--------|
| `getDetail` | 查询菜单详情 | privilege_menu_info |
| `queryMenusBySystemId` | 按系统查询菜单 | privilege_menu_info |
| `buildTree` | 构建菜单树 | - |
| `enable` | 启用/禁用菜单 | privilege_menu_info |
| `checkRepeat` | 检查接口URL重复 | - |
| `hasDuplicates` | 判断列表重复 | - |
| `queryServicesTree` | 查询服务树 | privilege_menu_info |
| `queryChildrenMenus` | 查询子菜单 | privilege_menu_info |
| `queryChildrenServicesMenus` | 查询子服务菜单 | privilege_menu_service |
| `queryDataStatistics` | 查询数据统计 | privilege_menu_info, privilege_menu_service |

### PrivilegeMenuInfoServiceImpl 补充方法（9个全部缺失）

| 方法名 | 一句话说明 | DAO层调用 |
|--------|------------|-----------|
| `getMenuOrgTree` | 获取菜单机构树 | `privilegeMenuInfoDao.getMenuOrgTree()` |
| `queryInfo` | 查询菜单信息 | `privilegeMenuInfoDao.queryInfo()` |
| `getChildrenMenus` | 获取子菜单 | `privilegeMenuInfoDao.getChildrenMenus()` |
| `queryServicesTree` | 查询服务树 | `privilegeMenuInfoDao.queryServicesTree()` |
| `selectMenuInfoById` | 按ID查询菜单 | `privilegeMenuInfoDao.selectMenuInfoById()` |
| `querySystemMenuNum` | 查询系统菜单数量 | `privilegeMenuInfoDao.querySystemMenuNum()` |
| `queryauthMenuNum` | 查询授权菜单数量 | `privilegeMenuInfoDao.queryauthMenuNum()` |
| `queryMenuOrder` | 查询菜单排序 | `privilegeMenuInfoDao.queryMenuOrder()` |
| `modifyOrder` | 修改菜单排序 | 调用自身方法 |

### PrivilegeMenuServiceServiceImpl 补充方法（2个全部缺失）

| 方法名 | 一句话说明 | DAO层调用 |
|--------|------------|-----------|
| `queryChildrenServicesMenus` | 查询子服务菜单 | `privilegeMenuServiceDao.queryChildrenServicesMenus()` |
| `queryAuthInterfaceNum` | 查询授权接口数量 | `privilegeMenuServiceDao.queryAuthInterfaceNum()` |

### 工具类速查

| 工具类 | 一句话说明 | 核心用途 |
|--------|------------|----------|
| `NotBlankFieldCopy` | 非空字段拷贝 | 只拷贝有值的字段 |
| `UserUtils` | 用户上下文工具 | 获取当前登录用户 |
| `User` | 用户对象 | 存储用户信息 |
| `UniqueIDGenerator` | UUID生成器 | 生成唯一ID |
| `AesUtil` | AES加解密 | 内容加密解密 |

---

> 📄 补充文档版本：1.1
> 👨‍💻 整理人：AI助手
> 📅 补充日期：2024年

---

📎 **延伸阅读**：
- [深度解析-角色管理](picc-mzmtb-user-深度解析第三章-角色管理.md) - 角色管理的完整流程和核心方法详解
- [深度解析-菜单与系统管理](picc-mzmtb-user-深度解析第四章-菜单与系统管理.md) - 菜单树的递归构建原理
- [API-Mapper-数据模型](picc-mzmtb-user-API-Mapper-数据模型.md) - API接口层和Mapper层的详细说明

