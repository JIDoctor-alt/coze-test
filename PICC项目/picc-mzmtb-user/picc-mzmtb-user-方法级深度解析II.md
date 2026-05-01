> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC权限管理系统 - 方法级深度解析II（补充）

> 📅 补充日期：2024年
> 🎯 本章节补充解析了权限管理系统中**尚未深度解析的重要方法**，重点涵盖用户角色分配、启用禁用、密码重置、角色CRUD核心逻辑、Spring Security拦截器等关键方法。

---

## 一、用户管理核心方法

---

### 方法：UserInfoServiceImpl.setRoles()

**一句话人话**：给用户分配角色，就像给员工发放工牌——一个员工可以有多张工牌（多角色）

**🏠 生活比喻**
想象你是酒店人事部员工，给新员工分配工牌：
- 张三入职了，他要进入"客房部"和"安保部"工作
- 你需要给他发两张工牌（两个角色）
- 如果他之前有其他部门的工牌，要先收回来
- 每张工牌上写着：张三的工号 + 部门名称

**📥 参数说明**

| 参数 | 人话解释 | 举个例子 |
|------|----------|----------|
| `privilegeUserRoleInfoDto.userId` | 要分配角色的用户ID | `"user-uuid-001"` |
| `privilegeUserRoleInfoDto.roleIds` | 要分配的角色ID数组 | `["role-001", "role-002"]` |

**📤 返回值**：无返回值，但会操作数据库

**🔗 谁在调用**：
- `UserInfoApi.create()` - 创建用户时自动调用
- `UserInfoApi.update()` - 修改用户时自动调用
- Controller层直接调用 - 给用户换角色

**📖 逐步拆解**

```java
// 第1步：校验参数 - userId必须有
if (StringUtils.isBlank(privilegeUserRoleInfoDto.getUserId())) {
    throw new CustomException("参数错误！人员ID不能为空！");
}

// 第2步：校验参数 - roleIds必须有且不能为空数组
if (privilegeUserRoleInfoDto.getRoleIds() == null || 
    privilegeUserRoleInfoDto.getRoleIds().length == 0) {
    throw new CustomException("参数错误！角色ID不能为空！");
}

// 第3步：获取当前时间，用于记录创建/修改时间
LocalDateTime now = LocalDateTime.now();

// 第4步：确认用户存在
PrivilegeUserInfo userInfo = privilegeUserInfoDao.selectUserInfoById(
    privilegeUserRoleInfoDto.getUserId());
if (userInfo == null) {
    throw new CustomException("该人员信息不存在！");
}

// 第5步：查询用户已有的角色关联
List<PrivilegeUserRoleInfo> infoList = 
    privilegeUserRoleInfoDao.selectByUserIdAndRoleId(
        privilegeUserRoleInfoDto.getUserId(), null);

// 第6步：如果用户已有角色，先全部删除（清空旧工牌）
if (!infoList.isEmpty()) {
    List<String> userRoleIdList = infoList.stream()
        .map(privilegeUserRoleInfo -> privilegeUserRoleInfo.getId())
        .collect(Collectors.toList());
    String[] userRoleIds = userRoleIdList.toArray(new String[0]);
    deleteRolesByIds(userRoleIds);  // 调用删除方法
}

// 第7步：循环新角色，逐个插入（发放新工牌）
for (String roleId : privilegeUserRoleInfoDto.getRoleIds()) {
    
    // 7a: 确认角色存在
    PrivilegeRoleInfo roleInfo = privilegeRoleInfoDao.queryRoleByID(roleId);
    if (roleInfo == null) {
        continue;  // 角色不存在就跳过，不报错
    }
    
    // 7b: 检查是否已经分配过这个角色
    List<PrivilegeUserRoleInfo> userRoleInfoList =
        privilegeUserRoleInfoDao.selectByUserIdAndRoleId(
            privilegeUserRoleInfoDto.getUserId(), roleId);
    if (userRoleInfoList.size() > 0) {
        continue;  // 已经分配过了，跳过
    }
    
    // 7c: 创建新的用户-角色关联记录
    PrivilegeUserRoleInfo privilegeUserRoleInfo = new PrivilegeUserRoleInfo();
    privilegeUserRoleInfo.setId(UUIDUtil.getUUID());
    privilegeUserRoleInfo.setRoleId(roleId);
    privilegeUserRoleInfo.setUserId(privilegeUserRoleInfoDto.getUserId());
    privilegeUserRoleInfo.setModifier(UserUtils.getUser().getUserAccount());
    privilegeUserRoleInfo.setModifytime(now);
    privilegeUserRoleInfo.setCreatetime(now);
    privilegeUserRoleInfo.setCreator(UserUtils.getUser().getUserAccount());
    
    // 7d: 插入数据库
    privilegeUserRoleInfoDao.insertSelective(privilegeUserRoleInfo);
}
```

**⚠️ 异常处理**

| 异常情况 | 后果 |
|----------|------|
| `userId`为空 | 抛 `CustomException("参数错误！人员ID不能为空！")` |
| `roleIds`为空或空数组 | 抛 `CustomException("参数错误！角色ID不能为空！")` |
| 用户不存在 | 抛 `CustomException("该人员信息不存在！")` |
| 角色不存在 | 静默跳过，继续处理其他角色 |
| 数据库插入失败 | 事务自动回滚 |

**🔒 安全注意**

1. **先删后加策略**：修改角色时会先删除旧关联，再插入新关联，确保不会有重复关联
2. **操作员记录**：每次操作都会记录 `creator`/`modifier`，可追溯谁给用户分配了角色
3. **事务保证**：整个方法有 `@Transactional` 注解，要么全成功，要么全回滚

**🐛 小白易懵点**

1. **角色不存在不会报错**：第7a步如果角色不存在，会 `continue` 跳过。这意味着传一个不存在的角色ID，系统会静默忽略它
2. **删除的是关联记录**：不是删除角色本身，只是解除用户和角色的绑定关系
3. **一个用户可以有多角色**：roleIds是数组，支持同时分配多个角色

---

### 方法：UserInfoServiceImpl.enableUser()

**一句话人话**：启用或禁用用户账号，禁用时会强制踢用户下线

**🏠 生活比喻**
想象你是酒店前台经理：
- 某个员工行为不端，你要封停他的工卡
- 封停后，他的所有登录状态都要被清除——就像把他从酒店大门直接赶出去
- 启用时只是恢复正常状态

**📥 参数说明**

| 参数 | 人话解释 | 举个例子 |
|------|----------|----------|
| `privilegeUserInfoDto.id` | 要操作的用户的ID | `"user-uuid-001"` |
| `privilegeUserInfoDto.enable` | 启用状态：0=禁用，1=启用 | `0` 或 `1` |

**📤 返回值**：无返回值

**🔗 谁在调用**：
- `UserInfoApi.enableUser()` - 启用/禁用用户接口

**📖 逐步拆解**

```java
// 第1步：校验用户ID不能为空
if (StringUtils.isBlank(privilegeUserInfoDto.getId())) {
    throw new CustomException("参数错误！人员的ID不能为空！");
}

// 第2步：查询用户是否存在
PrivilegeUserInfo privilegeUserInfo = 
    privilegeUserInfoDao.selectUserInfoById(privilegeUserInfoDto.getId());
if (privilegeUserInfo == null) {
    throw new CustomException("该人员已经被删除，不能启用/禁用！");
}

// 第3步：更新启用状态
privilegeUserInfo.setEnable(privilegeUserInfoDto.getEnable());
LocalDateTime now = LocalDateTime.now();
privilegeUserInfo.setModifier(UserUtils.getUser().getUserAccount());
privilegeUserInfo.setModifytime(now);
privilegeUserInfoDao.updateByPrimaryKey(privilegeUserInfo);

// 第4步：记录操作日志（账号变更记录）
AccountRecord accountRecord = new AccountRecord();
accountRecord.setAccount(privilegeUserInfo.getAccount());
accountRecord.setAccountid(privilegeUserInfo.getId());
accountRecord.setReason("经办人修改");
accountRecord.setUpdateaccount("经办人");
accountRecord.setType("1");
accountRecord.setEnable(privilegeUserInfo.getEnable() == 0 ? "T" : "F");
accountRecord.setCreatetime(LocalDateTime.now());
accountRecord.setCreator(UserUtils.getUser().getUserId());
accountRecord.setModifytime(LocalDateTime.now());
accountRecord.setModifier(UserUtils.getUser().getUserId());
accountRecordService.save(accountRecord);

// 第5步：如果要禁用（enable=0），清除Redis中的登录状态
if (privilegeUserInfo.getEnable() == 0) {
    // 5a: 检查用户是否有Token
    if (redisUtil.exists(userId + privilegeUserInfo.getId())) {
        // 5b: 获取用户的Token
        String oldtoken = (String) redisUtil.get(
            userId + privilegeUserInfo.getId());
        
        // 5c: 删除Token对应的用户信息
        if (redisUtil.exists(RedisKeyConf.API_TOKEN + oldtoken)) {
            redisUtil.remove(RedisKeyConf.API_TOKEN + oldtoken);
        }
        
        // 5d: 删除用户的权限标识
        if (redisUtil.exists(flag + privilegeUserInfo.getId())) {
            redisUtil.remove(flag + privilegeUserInfo.getId());
        }
        
        // 5e: 删除Token映射
        redisUtil.remove(userId + privilegeUserInfo.getId());
    }
    
    // 5f: 删除用户的USERKEY
    if (redisUtil.exists(RedisKeyConf.API_USERKEY + privilegeUserInfo.getId())) {
        redisUtil.remove(RedisKeyConf.API_USERKEY + privilegeUserInfo.getId());
    }
}
```

**🔌 Redis清理详解**

禁用用户时，会清理以下Redis Key：

| Redis Key | 含义 | 清理原因 |
|-----------|------|----------|
| `API_TOKEN:{token}` | Token对应的用户信息 | 清除登录态 |
| `flag:{userId}` | 用户的权限编码 | 清除权限缓存 |
| `userid:{userId}` | Token映射 | 清除Token关联 |
| `API_USERKEY:{userId}` | 用户Key | 清除用户会话 |

**⚠️ 异常处理**

| 异常情况 | 后果 |
|----------|------|
| 用户ID为空 | 抛异常 |
| 用户已被删除 | 抛 `CustomException("该人员已经被删除，不能启用/禁用！")` |
| Redis操作失败 | 可能导致用户无法被踢下线 |

**🔒 安全注意**

1. **强制下线机制**：禁用用户时会清除Redis中的所有登录状态，被禁用的用户立即无法访问系统
2. **操作审计**：每次启用/禁用都会记录到 `account_record` 表
3. **双向记录**：记录 `creator`/`modifier` 和 `T`/`F` 状态标识

**🐛 小白易懵点**

1. **enable=0 是禁用**：不是 `true`/`false`，而是 `0`/`1`
2. **禁用才会清理Redis**：启用用户不会操作Redis
3. **删除的用户不能操作**：被软删除的用户不能再启用/禁用

---

### 方法：UserInfoServiceImpl.resetPassword()

**一句话人话**：把用户密码重置为默认密码

**🏠 生活比喻**
就像酒店前台接到电话："我忘记密码了，帮我重置"
- 前台核实身份后，把密码重置为统一的默认密码
- 用户拿到新密码后应该立即修改

**📥 参数说明**

| 参数 | 人话解释 | 举个例子 |
|------|----------|----------|
| `privilegeUserInfoDto.id` | 要重置密码的用户ID | `"user-uuid-001"` |

**📤 返回值**：无返回值

**🔗 谁在调用**：
- `UserInfoApi.resetPassword()` - 重置密码接口

**📖 逐步拆解**

```java
// 第1步：校验用户ID不能为空
if (StringUtils.isBlank(privilegeUserInfoDto.getId())) {
    throw new CustomException("参数错误！人员的ID不能为空！");
}

// 第2步：查询用户是否存在
PrivilegeUserInfo privilegeUserInfo = 
    privilegeUserInfoDao.selectUserInfoById(privilegeUserInfoDto.getId());
if (privilegeUserInfo == null) {
    throw new CustomException("该用户不存在，不能重置密码！");
}

// 第3步：使用默认密码 + SM4加密
// 默认密码在配置文件中定义：loginUser.defaultPassWord=PICChealth@2020
String password = SM4Util.sm4Encrypt(defaultPassWord);
privilegeUserInfo.setPassword(password);

// 第4步：记录重置操作
LocalDateTime now = LocalDateTime.now();
privilegeUserInfo.setModifier(UserUtils.getUser().getUserAccount());
privilegeUserInfo.setModifytime(now);

// 第5步：记录密码修改时间（用于判断密码是否过期）
privilegeUserInfo.setPasswordChanged(new Date());

// 第6步：更新数据库
privilegeUserInfoDao.updateByPrimaryKey(privilegeUserInfo);
```

**🔒 安全注意**

1. **默认密码固定**：所有重置的密码都一样（`PICChealth@2020`），建议用户首次登录必须修改
2. **SM4加密存储**：密码不会明文存储
3. **记录修改时间**：可判断密码是否过期

**🐛 小白易懵点**

1. **重置不是生成随机密码**：是设置为固定的默认密码
2. **需要操作员权限**：会记录谁重置的密码
3. **不会踢用户下线**：和 `enableUser()` 不同，重置密码不会清除登录态

---

### 方法：UserInfoServiceImpl.deleteById()

**一句话人话**：软删除用户（不是真的从数据库抹掉）

**🏠 生活比喻**
就像酒店开除员工：
- 不是把员工信息从档案里撕掉
- 而是在档案上盖个"已离职"的章
- 以后查档案还能看到历史记录

**📥 参数说明**

| 参数 | 人话解释 | 举个例子 |
|------|----------|----------|
| `id` | 要删除的用户ID | `"user-uuid-001"` |

**📤 返回值**：`Integer` - 受影响的行数

**🔗 谁在调用**：
- `UserInfoApi.delete()` - 删除用户接口

**📖 逐步拆解**

```java
// 第1步：校验用户ID不能为空
if (StringUtils.isBlank(id)) {
    throw new CustomException("参数错误！人员ID不能为空！");
}

// 第2步：查询用户是否存在
PrivilegeUserInfo privilegeUserInfo = 
    privilegeUserInfoDao.selectByPrimaryKey(id);
if (privilegeUserInfo == null) {
    throw new CustomException("该人员不存在，不能删除！");
}

// 第3步：检查是否已经被删除
if (privilegeUserInfo.getDeleteAt() != null) {
    throw new CustomException("该人员已经被删除，不能重复删除！");
}

LocalDateTime now = LocalDateTime.now();

// 第4步：删除 up_org_user 表中的关联数据
upOrgUserDao.deleteByPrimaryKey(privilegeUserInfo.getId());

// 第5步：删除 privilege_user_auth 表中的权限归属数据
PrivilegeUserAuth userAuth = new PrivilegeUserAuth();
userAuth.setUserId(privilegeUserInfo.getId());
List<PrivilegeUserAuth> authList = privilegeUserAuthDao.queryUserAuthList(userAuth);
if (!authList.isEmpty()) {
    for (PrivilegeUserAuth ua : authList) {
        ua.setDeleteAt(now);
        ua.setModifier(UserUtils.getUser().getUserAccount());
        ua.setModifytime(now);
        privilegeUserAuthDao.updateByPrimaryKey(ua);
    }
}

// 第6步：设置用户的 deleteAt 时间戳（软删除标记）
privilegeUserInfo.setDeleteAt(now);
privilegeUserInfo.setModifier(UserUtils.getUser().getUserAccount());
privilegeUserInfo.setModifytime(now);

// 第7步：更新用户记录
privilegeUserInfoDao.updateByPrimaryKey(privilegeUserInfo);
```

**⚠️ 异常处理**

| 异常情况 | 后果 |
|----------|------|
| 用户ID为空 | 抛异常 |
| 用户不存在 | 抛异常 |
| 用户已删除 | 抛 `CustomException("该人员已经被删除，不能重复删除！")` |

**🐛 小白易懵点**

1. **软删除不是真删除**：数据还在数据库里，只是 `deleteAt` 字段有值
2. **关联数据也软删除**：用户角色关联、权限归属都会标记删除
3. **删除后不能登录**：虽然数据还在，但登录时会被过滤掉

---

### 方法：UserInfoServiceImpl.queryUsers()

**一句话人话**：分页查询用户列表，支持多种条件筛选

**📥 参数说明**

| 参数 | 人话解释 | 举个例子 |
|------|----------|----------|
| `privilegeUserInfoDto.account` | 用户账号（模糊查询） | `"zhang"` |
| `privilegeUserInfoDto.name` | 用户姓名（模糊查询） | `"张"` |
| `privilegeUserInfoDto.tel` | 手机号（模糊查询） | `"138"` |
| `privilegeUserInfoDto.orgId` | 机构ID（树形范围） | `"org-001"` |
| `privilegeUserInfoDto.pageVo` | 分页参数 | `{pageNum:1, pageSize:10}` |

**📤 返回值**：`ResultPage<UserInfoVo>` - 分页的用户列表

**📖 逐步拆解**

```java
// 第1步：从dto取出分页参数
PageVo pageVo = privilegeUserInfoDto.getPageVo();

// 第2步：开启分页
PageHelper.startPage(pageVo.getPageNum(), pageVo.getPageSize());

// 第3步：获取当前用户的机构ID范围
String orgId = UserUtils.getUser().getOrgId();

// 第4步：调用私有方法获取所有子机构ID（BFS遍历）
List<String> idList = getidList(orgId);

// 第5步：执行分页查询
List<PrivilegeUserInfo> privilegeUserInfoList = 
    privilegeUserInfoDao.selectUsers(privilegeUserInfoDto, idList);

// 第6步：包装分页信息
PageInfo<PrivilegeUserInfo> pageInfo = new PageInfo<>(privilegeUserInfoList);

// 第7步：组装返回VO
List<UserInfoVo> userInfoVoList = new ArrayList<>();
privilegeUserInfoList.forEach(user -> {
    UserInfoVo vo = new UserInfoVo();
    BeanUtils.copyProperties(user, vo);
    vo.setUserId(user.getId());
    
    // 查机构名称
    if (StringUtils.isNotBlank(user.getOrgId())) {
        PrivilegeOrgInfo org = privilegeOrgInfoDao.selectByPrimaryKey(user.getOrgId());
        if (org != null) {
            vo.setOrgName(org.getName());
        }
    }
    
    userInfoVoList.add(vo);
});

// 第8步：转换时间格式
userInfoVoList.forEach(vo -> {
    vo.setCreateTime(LocalTimeUtils.parseLocalDateTime(vo.getCreatetime()));
    vo.setModifyTime(LocalTimeUtils.parseLocalDateTime(vo.getModifytime()));
});

// 第9步：返回分页结果
PageInfo<UserInfoVo> page = new PageInfo<>();
BeanUtils.copyProperties(pageInfo, page);
page.setList(userInfoVoList);
return this.createResultPage(page);
```

**🔒 安全注意**

1. **数据权限过滤**：只返回当前用户所在机构及子机构的用户
2. **不能跨机构查询**：即使是管理员也只能看到自己机构下的用户

---

## 二、角色管理核心方法

---

### 方法：RoleInfoServiceImpl.createRole()

**一句话人话**：创建新角色并可同时分配菜单资源

**🏠 生活比喻**
就像酒店设立新部门：
1. 先确定部门名称和职责
2. 给这个部门分配工作区域和工具（菜单资源）
3. 部门创建后，就可以给员工发这个部门的工牌了

**📥 参数说明**

| 参数 | 人话解释 | 举个例子 |
|------|----------|----------|
| `roleCreateVo.name` | 角色名称 | `"门诊管理员"` |
| `roleCreateVo.orgId` | 所属机构ID | `"org-001"` |
| `roleCreateVo.systemId` | 关联系统ID | `"sys-001"` |
| `roleCreateVo.menuIds` | 分配的菜单ID列表 | `["menu-001", "menu-002"]` |
| `roleCreateVo.remark` | 备注说明 | `"负责门诊系统管理"` |

**📤 返回值**：`CommonReqVo` - 包含新创建的角色ID

**🔗 谁在调用**：
- `RoleInfoApi.createRole()` - 创建角色接口

**📖 逐步拆解**

```java
// 第1步：初始化返回对象
CommonReqVo commonReqVo = new CommonReqVo();
commonReqVo.setCode(ReturnStatusEnum.FAIL.getCode());

// 第2步：复制属性到实体
PrivilegeRoleInfo privilegeRoleInfo = new PrivilegeRoleInfo();
BeanUtils.copyProperties(roleCreateVo, privilegeRoleInfo);

// 第3步：生成唯一ID
String roleId = UniqueIDGenerator.generateUniqueID();

// 第4步：设置审计字段
privilegeRoleInfo.setCreatetime(LocalDateTime.now());
privilegeRoleInfo.setCreator(UserUtils.getUser().getUserAccount());
privilegeRoleInfo.setModifytime(LocalDateTime.now());
privilegeRoleInfo.setModifier(UserUtils.getUser().getUserAccount());

// 第5步：如果没有传入ID，使用生成的ID
if (StringUtils.isBlank(privilegeRoleInfo.getId())) {
    privilegeRoleInfo.setId(roleId);
}

// 第6步：数据校验（角色名是否重复等）
String checkRes = roleDataVerifi(privilegeRoleInfo);
if (StringUtils.isNotBlank(checkRes)) {
    commonReqVo.setMsg(checkRes);
    return commonReqVo;
}

// 第7步：插入角色记录
int insertCount = privilegeRoleInfoDao.insertSelective(privilegeRoleInfo);

// 第8步：配置角色资源（如果传了系统ID或菜单ID）
if (StringUtils.isNotBlank(roleCreateVo.getSystemId()) || 
    CollectionUtils.isNotEmpty(roleCreateVo.getMenuIds())) {
    
    // 8a: 循环每个菜单ID，插入角色-资源关联
    for (int i = 0; i < roleCreateVo.getMenuIds().size(); i++) {
        String menuId = roleCreateVo.getMenuIds().get(i);
        
        PrivilegeRoleResource privilegeRoleResource = new PrivilegeRoleResource();
        privilegeRoleResource.setSystemId(roleCreateVo.getSystemId());
        privilegeRoleResource.setRoleId(privilegeRoleInfo.getId());
        privilegeRoleResource.setMenuId(menuId);
        privilegeRoleResource.setCreator(UserUtils.getUser().getUserAccount());
        privilegeRoleResource.setModifier(UserUtils.getUser().getUserAccount());
        privilegeRoleResource.setCreatetime(LocalDateTime.now());
        privilegeRoleResource.setModifytime(LocalDateTime.now());
        privilegeRoleResource.setId(UniqueIDGenerator.generateUniqueID());
        
        // 8b: 资源数据校验
        String resoureCheckRes = resourceDataVerifi(privilegeRoleResource);
        if (StringUtils.isNotBlank(resoureCheckRes)) {
            continue;  // 校验不通过就跳过
        }
        
        // 8c: 插入角色-资源关联
        int resouceInsertCount = privilegeRoleResourceDao.insert(privilegeRoleResource);
    }
}

// 第9步：返回成功结果
RoleCreateDto roleCreateDto = new RoleCreateDto().setId(privilegeRoleInfo.getId());
commonReqVo.setCode(ReturnStatusEnum.SUCCECESS.getCode());
commonReqVo.setJsonResult(JSONObject.toJSONString(roleCreateDto));
return commonReqVo;
```

**🔒 安全注意**

1. **事务保证**：整个操作在一个事务中，角色创建失败会回滚
2. **审计追踪**：记录创建人和修改人
3. **校验机制**：创建前会校验数据合法性

---

### 方法：RoleInfoServiceImpl.updateRole()

**一句话人话**：更新角色信息，同时可更新菜单资源配置

**🏠 生活比喻**
就像酒店调整部门：
1. 可能只改部门名称
2. 可能调整工作区域（菜单）
3. 可能名称和区域都改

**📥 参数说明**

| 参数 | 人话解释 | 举个例子 |
|------|----------|----------|
| `roleUpdateVo.id` | 角色ID | `"role-001"` |
| `roleUpdateVo.name` | 新角色名称 | `"新门诊管理员"` |
| `roleUpdateVo.systemId` | 关联系统ID | `"sys-001"` |
| `roleUpdateVo.menuIds` | 新分配的菜单ID列表 | `["menu-003", "menu-004"]` |

**📖 逐步拆解**

```java
// 第1步：初始化返回对象
CommonReqVo commonReqVo = new CommonReqVo();
commonReqVo.setCode(ReturnStatusEnum.FAIL.getCode());

// 第2步：复制属性
PrivilegeRoleInfo privilegeRoleInfo = new PrivilegeRoleInfo();
BeanUtils.copyProperties(roleUpdateVo, privilegeRoleInfo);

// 第3步：查询原角色信息
PrivilegeRoleInfo roleQueryPo = 
    privilegeRoleInfoDao.selectByPrimaryKey(roleUpdateVo.getId());
roleQueryPo.setModifier(UserUtils.getUser().getUserAccount());
roleQueryPo.setModifytime(LocalDateTime.now());

// 第4步：检查哪些字段有变化
boolean nameChanged = fieldDiff(roleUpdateVo.getName(), roleQueryPo.getName());
boolean orgIdChanged = fieldDiff(roleUpdateVo.getOrgId(), roleQueryPo.getOrgId());
boolean remarkChanged = fieldDiff(roleUpdateVo.getRemark(), roleQueryPo.getRemark());
boolean enableChanged = !roleQueryPo.getEnable().equals(roleUpdateVo.getEnable());

// 第5步：如果有变化，更新角色基本信息
if (nameChanged || orgIdChanged || remarkChanged || enableChanged) {
    NotBlankFieldCopy.fieldPropertiesCopy(privilegeRoleInfo, roleQueryPo);
    String checkRes = roleDataUpdateVerifi(roleQueryPo);
    if (StringUtils.isNotBlank(checkRes)) {
        commonReqVo.setMsg(checkRes);
        return commonReqVo;
    }
}

// 第6步：无论如何都更新时间戳
int updateCount = privilegeRoleInfoDao.updateByPrimaryKey(roleQueryPo);

// 第7步：如果传了systemId，更新角色资源
if (StringUtils.isNotBlank(roleUpdateVo.getSystemId())) {
    
    // 7a: 查询该角色现有的资源
    List<PrivilegeRoleResource> oldRoleResources = 
        privilegeRoleResourceDao.queryResourcesByRoleId(roleUpdateVo.getId());
    
    // 7b: 找出需要删除的资源（旧菜单但不在新菜单列表中）
    List<PrivilegeRoleResource> toDelete = oldRoleResources.stream()
        .filter(r -> !roleUpdateVo.getMenuIds().contains(r.getMenuId()))
        .collect(Collectors.toList());
    
    // 7c: 软删除要删除的资源
    for (PrivilegeRoleResource del : toDelete) {
        del.setModifier(UserUtils.getUser().getUserAccount());
        del.setModifytime(LocalDateTime.now());
        del.setDeleteAt(LocalDateTime.now());
        privilegeRoleResourceDao.updateByPrimaryKey(del);
    }
    
    // 7d: 找出已经配置过的菜单
    List<String> configured = oldRoleResources.stream()
        .filter(r -> roleUpdateVo.getMenuIds().contains(r.getMenuId()))
        .map(r -> r.getMenuId())
        .collect(Collectors.toList());
    
    // 7e: 过滤掉已配置的，插入新菜单
    List<String> toAdd = roleUpdateVo.getMenuIds().stream()
        .filter(menuId -> !configured.contains(menuId))
        .collect(Collectors.toList());
    
    // 7f: 逐个插入新资源
    toAdd.forEach(menuId -> {
        PrivilegeRoleResource resource = new PrivilegeRoleResource();
        resource.setId(UniqueIDGenerator.generateUniqueID());
        resource.setRoleId(roleUpdateVo.getId());
        resource.setSystemId(roleUpdateVo.getSystemId());
        resource.setMenuId(menuId);
        resource.setCreator(UserUtils.getUser().getUserAccount());
        resource.setModifier(UserUtils.getUser().getUserAccount());
        resource.setCreatetime(LocalDateTime.now());
        resource.setModifytime(LocalDateTime.now());
        
        privilegeRoleResourceDao.insert(resource);
    });
}

// 第8步：返回结果
commonReqVo.setCode(ReturnStatusEnum.SUCCECESS.getCode());
return commonReqVo;
```

**🔒 安全注意**

1. **差异更新**：只更新有变化的字段
2. **资源增量更新**：删除不再需要的资源，添加新资源，保留已有的
3. **软删除资源**：被移除的资源不会真删除，只打上时间戳

---

### 方法：RoleInfoServiceImpl.deleteRole()

**一句话人话**：软删除角色

**📥 参数说明**

| 参数 | 人话解释 | 举个例子 |
|------|----------|----------|
| `roleDeleteVo.id` | 要删除的角色ID | `"role-001"` |

**📖 逐步拆解**

```java
// 第1步：查询角色是否存在
PrivilegeRoleInfo privilegeRoleInfo = 
    privilegeRoleInfoDao.selectByPrimaryKey(roleDeleteVo.getId());
if (privilegeRoleInfo == null) {
    commonReqVo.setMsg("未查到对应角色,请重新校验输入");
    return commonReqVo;
}

// 第2步：检查是否已删除
if (privilegeRoleInfo.getDeleteAt() != null) {
    commonReqVo.setMsg("该ID已删除,请不要重复删除");
    return commonReqVo;
}

// 第3步：设置删除标记
privilegeRoleInfo.setModifier(UserUtils.getUser().getUserAccount());
privilegeRoleInfo.setModifytime(LocalDateTime.now());
privilegeRoleInfo.setDeleteAt(LocalDateTime.now());

// 第4步：更新数据库
int updateCount = privilegeRoleInfoDao.updateByPrimaryKey(privilegeRoleInfo);

commonReqVo.setCode(ReturnStatusEnum.SUCCECESS.getCode());
return commonReqVo;
```

**⚠️ 安全注意**

1. **不删除关联资源**：注释写了 `//tod 暂不删除角色所属资源`，被删除角色的菜单权限关联仍然保留
2. **需要重新登录**：删除角色后，拥有该角色的用户需要重新登录才能使变更生效

---

### 方法：RoleInfoServiceImpl.setResource()

**一句话人话**：给角色批量分配菜单资源

**🏠 生活比喻**
就像给部门分配会议室：
- 指定部门（角色）
- 指定系统（会议室区域）
- 指定多个会议室（菜单）

**📥 参数说明**

| 参数 | 人话解释 | 举个例子 |
|------|----------|----------|
| `resouceVo.roleId` | 角色ID | `"role-001"` |
| `resouceVo.systemId` | 系统ID | `"sys-001"` |
| `resouceVo.menuIds` | 菜单ID数组 | `["menu-001", "menu-002"]` |

**📖 逐步拆解**

```java
// 第1步：校验菜单ID不能为空
if (CollectionUtils.isEmpty(resouceVo.getMenuIds())) {
    commonReqVo.setMsg("请选择该角色要配置的菜单列表");
    return commonReqVo;
}

// 第2步：循环每个菜单ID，插入角色-资源关联
for (String menuId : resouceVo.getMenuIds()) {
    
    // 2a: 创建角色-资源关联对象
    PrivilegeRoleResource privilegeRoleResource = new PrivilegeRoleResource()
        .setMenuId(menuId)
        .setSystemId(resouceVo.getSystemId())
        .setRoleId(resouceVo.getRoleId());
    
    // 2b: 生成唯一ID
    String resourceId = UniqueIDGenerator.generateUniqueID();
    privilegeRoleResource.setId(resourceId);
    
    // 2c: 设置审计字段
    privilegeRoleResource.setCreatetime(LocalDateTime.now());
    privilegeRoleResource.setCreator(UserUtils.getUser().getUserAccount());
    privilegeRoleResource.setModifier(UserUtils.getUser().getUserAccount());
    privilegeRoleResource.setModifytime(LocalDateTime.now());
    
    // 2d: 数据校验
    String checkRes = resourceDataVerifi(privilegeRoleResource);
    if (StringUtils.isNotBlank(checkRes)) {
        commonReqVo.setMsg(commonReqVo.getMsg() + checkRes);
        continue;  // 校验不通过就跳过
    }
    
    // 2e: 插入数据库
    int insertCount = privilegeRoleResourceDao.insertSelective(privilegeRoleResource);
    
    if (insertCount == 0) {
        log.error("配置角色资源信息失败");
        commonReqVo.setMsg(commonReqVo.getMsg() + "新增配置失败");
    }
}

// 第3步：返回结果
if (StringUtils.isBlank(commonReqVo.getMsg())) {
    commonReqVo.setCode(ReturnStatusEnum.SUCCECESS.getCode());
}
return commonReqVo;
```

**🐛 小白易懵点**

1. **不清空旧资源**：这个方法只是追加新资源，不会删除已有的资源
2. **校验失败继续处理**：某个菜单校验失败不会中断整个流程

---

### 方法：RoleInfoServiceImpl.queryResourcesByRoleId()

**一句话人话**：查询一个或多个角色拥有的菜单资源

**📥 参数说明**

| 参数 | 人话解释 | 举个例子 |
|------|----------|----------|
| `resourcesQueryVo.roleIds` | 角色ID列表 | `["role-001", "role-002"]` |
| `resourcesQueryVo.pageIndex` | 页码 | `1` |
| `resourcesQueryVo.pageSize` | 每页条数 | `10` |

**📤 返回值**：按角色分组的资源列表

**📖 返回数据结构**

```json
{
  "code": "SUCCESS",
  "jsonResult": {
    "list": [
      {
        "roleId": "role-001",
        "systemId": "sys-001",
        "menuInfo": [
          {"resourceId": "menu-001", "resourceName": "用户管理"},
          {"resourceId": "menu-002", "resourceName": "角色管理"}
        ]
      }
    ]
  }
}
```

**📖 逐步拆解**

```java
// 第1步：校验角色ID列表不能为空
if (CollectionUtils.isEmpty(resourcesQueryVo.getRoleIds())) {
    commonReqVo.setMsg("未选择角色,请选择要查询的角色集合");
    return commonReqVo;
}

// 第2步：开启分页
if (resourcesQueryVo.getPageIndex() > 0 && resourcesQueryVo.getPageSize() > 0) {
    PageHelper.startPage(resourcesQueryVo.getPageIndex(), 
                         resourcesQueryVo.getPageSize());
}

// 第3步：查询所有角色的资源
List<PrivilegeRoleResource> privilegeRoleResourceList = 
    privilegeRoleResourceDao.queryResourcesByRoleIds(resourcesQueryVo.getRoleIds());

// 第4步：按角色ID分组
Map<String, List<PrivilegeRoleResource>> roleMap = 
    privilegeRoleResourceList.stream()
        .collect(Collectors.groupingBy(PrivilegeRoleResource::getRoleId));

// 第5步：组装返回数据
List<ResourceQueryDto> resourceQueryDtos = new ArrayList<>();
roleMap.entrySet().forEach(entry -> {
    List<MenuInfo> menuInfoList = new ArrayList<>();
    
    // 5a: 遍历每个资源，查菜单名称
    entry.getValue().forEach(resource -> {
        PrivilegeMenuInfo menuInfo = 
            privilegeMenuInfoDao.selectByPrimaryKey(resource.getMenuId());
        
        if (menuInfo != null && menuInfo.getDeleteAt() == null 
            && menuInfo.getEnable() == 1) {
            MenuInfo mi = new MenuInfo()
                .setResourceId(resource.getMenuId())
                .setResourceName(menuInfo.getName());
            menuInfoList.add(mi);
        }
    });
    
    // 5b: 构建角色资源DTO
    ResourceQueryDto dto = new ResourceQueryDto();
    if (CollectionUtils.isNotEmpty(entry.getValue())) {
        BeanUtils.copyProperties(entry.getValue().get(0), dto);
        dto.setMenuInfo(menuInfoList);
        resourceQueryDtos.add(dto);
    }
});

// 第6步：返回分页结果
ResultPage<ResourceQueryDto> resPage = 
    createResultPage(new PageInfo<>(resourceQueryDtos));
commonReqVo.setJsonResult(JSONObject.toJSONString(resPage));
```

---

## 三、Spring Security 核心组件

---

### 组件：TokenInterceptorConfig

**一句话人话**：请求拦截器，验证Token有效性和用户权限

**🏠 生活比喻**
就像酒店大堂的门禁系统：
1. 检查你是否有房卡（Token）
2. 检查房卡是否有效（Redis中是否存在）
3. 检查你是否有权限进入权限管理区域（是否包含"88"权限码）
4. 自动续期（每次有效请求，房间有效期延长）

**🔗 拦截路径**：所有请求都会经过此拦截器

**📖 工作流程**

```java
// preHandle() 方法流程：

// 第1步：检查是否开启Token校验（可配置关闭）
if (!tokenInterceptFlag) {
    return true;  // 关闭时直接放行
}

// 第2步：从请求头获取Token和UserId
String token = request.getHeader("token");
String userId = request.getHeader("userId");

// 第3步：Token不能为空
if (StringUtils.isBlank(token)) {
    throw CustomException("登录token无效!请重新登录");
}

// 第4步：从Redis查询Token对应的用户
User urUser = (User) redisUtil.get(RedisKeyConf.API_TOKEN + token);
if (urUser == null) {
    throw CustomException("登录token无效!请重新登录");
}

// 第5步：检查用户是否有权限管理权限
String permissionKey = "flag:" + urUser.getUserId();
if (!redisUtil.exists(permissionKey)) {
    throw CustomException("账号无权限访问该菜单");
}

String permissionStr = (String) redisUtil.get(permissionKey);
String[] permissions = permissionStr.split(",");
boolean hasPermission = Arrays.asList(permissions).contains("88");
if (!hasPermission) {
    throw CustomException("账号无权限访问该菜单");
}

// 第6步：续期Token（24小时 = 1440分钟）
redisUtil.set(RedisKeyConf.API_TOKEN + token, urUser, 1440);

// 第7步：存入ThreadLocal供后续使用
UserUtils.setUser(urUser);

return true;  // 放行
```

**⚠️ 安全注意点**

| 问题 | 说明 | 风险等级 |
|------|------|----------|
| 权限码"88"硬编码 | 权限管理菜单的权限码直接写在代码里 | 🟡 中 |
| 每次请求无条件续期 | 活跃用户Token永不过期 | 🟡 中 |
| 打印请求头信息 | `System.out.println`可能泄露敏感数据 | 🟡 中 |
| UserUtils默认值 | 获取不到用户时返回默认用户 | 🔴 高 |

**🐛 小白易懵点**

1. **只拦截部分路径**：配置可开关 `tokenInterceptFlag`，开发环境常关闭
2. **ThreadLocal清理**：在 `afterCompletion()` 中清理，防止内存泄漏
3. **userId双来源**：优先取 Header1，没有则取 Header2

---

### 组件：APIAuthorityFilter

**一句话人话**：API权限过滤器，检查用户是否有权限访问特定接口

**🏠 生活比喻**
就像楼层保安检查你的房卡：
- 大堂检查你能不能进入酒店（TokenInterceptor）
- 楼层保安检查你能不能进这个楼层（APIAuthorityFilter）
- 保安手里有一份授权名单（Redis中的UrlPermission）

**🔗 拦截路径**：仅拦截 `/privilege/user/*` 路径

**📖 工作流程**

```java
// doFilter() 方法流程：

// 第1步：获取请求路径
String requestPath = request.getServletPath();

// 第2步：从请求获取Token（POST从Header，GET从参数）
String token = "";
if ("POST".equalsIgnoreCase(request.getMethod())) {
    token = request.getHeader("token");
} else if ("GET".equalsIgnoreCase(request.getMethod())) {
    token = request.getParameter("token");
}

// 第3步：Token校验
if (StringUtils.isBlank(token)) {
    throw CustomException("登录Token无效!请重新登录");
}

// 第4步：从Redis获取用户信息
User re = (User) redisUtil.get(RedisKeyConf.API_TOKEN + token);
if (re == null || StringUtils.isBlank(re.getUserId())) {
    throw CustomException("用户信息错误,请重新登录");
}

String userid = re.getUserId();

// 第5步：检查用户是否有URL权限缓存
if (!redisUtil.exists("UrlPermission:" + userid)) {
    // 双重检查，防止并发问题
    synchronized (this) {
        if (!redisUtil.exists("UrlPermission:" + userid)) {
            throw new BusinessException("请重新登录");
        }
    }
}

// 第6步：获取用户的URL权限列表
List<String> list = (ArrayList<String>) redisUtil.get("UrlPermission:" + userid);

// 第7步：检查当前路径是否在权限列表中
// ⚠️ 使用 contains() 进行模糊匹配
long count = list.stream()
    .filter(s -> s.contains(requestPath))
    .count();

if (count == 0) {
    throw CustomException("接口权限未通过!");
}

// 第8步：放行
filterChain.doFilter(servletRequest, servletResponse);
```

**🔒 安全注意**

| 问题 | 说明 | 风险等级 |
|------|------|----------|
| `contains()`模糊匹配 | `/privilege/user/`会匹配`/privilege/user/create` | 🔴 高 |
| synchronized同步 | 高并发下可能阻塞所有请求 | 🟡 中 |
| 只拦截user路径 | 角色/菜单/机构接口无URL权限校验 | 🔴 高 |

**🐛 小白易懵点**

1. **Redis缓存预热**：用户登录时会把URL权限列表存入Redis
2. **URL匹配问题**：`/privilege/user/`包含了 `/privilege/user/create`
3. **修改权限需重新登录**：权限变更后需要重新登录才能刷新Redis缓存

---

## 四、数据迁移方法

---

### 方法：MoveServiceImpl.move()

**一句话人话**：将旧系统角色数据迁移到新系统

**🏠 生活比喻**
就像公司搬迁时，把旧档案室的文件夹搬到新档案室：
- 每个旧文件夹（角色）对应新档案室的一个或多个文件夹
- 如果同一个编码的角色有多个（不同机构），要生成不同的新ID

**📖 逐步拆解**

```java
// 第1步：从旧表查询所有角色资源
List<PrivilegeRoleInfo> privilegeRoleInfos = sysRoleModuleRelDao.moveRoleResources();

int index = 1;
String groupId = null;

// 第2步：遍历每个角色
for (int i = 0; i < privilegeRoleInfos.size(); i++) {
    
    // 第3步：判断是否是新角色（编码和前一个不同）
    if (i == 0 || !privilegeRoleInfos.get(i).getCode()
            .equals(privilegeRoleInfos.get(i - 1).getCode())) {
        
        // 3a: 新角色，生成新ID
        PrivilegeRoleInfo privilegeRoleInfo = privilegeRoleInfos.get(i);
        
        // 3b: 查询该角色的所有旧资源
        List<SysRoleModuleRel> sysRoleModuleRels = 
            sysRoleModuleRelDao.queryResourcesByRoleIds(privilegeRoleInfo.getId());
        
        // 3c: 逐个迁移资源到新表
        for (SysRoleModuleRel rel : sysRoleModuleRels) {
            PrivilegeRoleResource privilegeRoleResource = new PrivilegeRoleResource();
            String roleId = UniqueIDGenerator.generateUniqueID();
            privilegeRoleResource.setId(roleId);
            privilegeRoleResource.setSystemId("459694197360955392");  // 固定系统ID
            privilegeRoleResource.setRoleId(rel.getRoleId());
            privilegeRoleResource.setMenuId(rel.getModuleId());
            privilegeRoleResource.setModifytime(LocalDateTime.now());
            privilegeRoleResource.setCreatetime(LocalDateTime.now());
            privilegeRoleResourceDao.insert(privilegeRoleResource);
        }
        
        // 3d: 插入新角色记录
        privilegeRoleInfo.setModifytime(privilegeRoleInfo.getCreatetime());
        privilegeRoleInfoDao.insert(privilegeRoleInfo);
        
        index = 1;
        groupId = privilegeRoleInfos.get(i).getId();
        
    } else {
        // 第4步：同编码的重复角色（不同机构）
        // 生成带序号的ID：原ID + 序号
        String id = groupId + String.valueOf(index);
        index++;
        
        // 4a: 复用第一个角色的资源
        List<SysRoleModuleRel> sysRoleModuleRels = 
            sysRoleModuleRelDao.queryResourcesByRoleIds(groupId);
        
        // 4b: 迁移资源到新表（新ID）
        for (SysRoleModuleRel rel : sysRoleModuleRels) {
            PrivilegeRoleResource privilegeRoleResource = new PrivilegeRoleResource();
            String roleId = UniqueIDGenerator.generateUniqueID();
            privilegeRoleResource.setId(roleId);
            privilegeRoleResource.setSystemId("459694197360955392");
            privilegeRoleResource.setRoleId(id);  // 使用新ID
            privilegeRoleResource.setMenuId(rel.getModuleId());
            privilegeRoleResource.setModifytime(LocalDateTime.now());
            privilegeRoleResource.setCreatetime(LocalDateTime.now());
            privilegeRoleResourceDao.insert(privilegeRoleResource);
        }
        
        // 4c: 插入新角色记录
        PrivilegeRoleInfo privilegeRoleInfo = privilegeRoleInfos.get(i);
        privilegeRoleInfo.setModifytime(privilegeRoleInfo.getCreatetime());
        privilegeRoleInfo.setId(id);  // 使用新ID
        privilegeRoleInfoDao.insert(privilegeRoleInfo);
    }
}
```

**🐛 小白易懵点**

1. **同编码不同机构**：如果旧系统有两个"管理员"角色（不同机构），新系统会生成两个不同的ID
2. **固定系统ID**：`"459694197360955392"` 是硬编码的目标系统ID
3. **事务保证**：有 `@Transactional` 注解，迁移失败会回滚

---

### 方法：MoveServiceImpl.passwordBackMD5()

**一句话人话**：将用户密码从RSA加密还原为明文MD5（旧系统兼容）

**🔒 安全注意**

1. **只用于迁移**：迁移完成后应删除此方法
2. **密钥硬编码**：公私钥写在代码里是严重安全问题
3. **明文存储**：密码会被还原为MD5格式存储

**📖 逐步拆解**

```java
// 第1步：查询所有用户
List<PrivilegeUserInfo> privilegeUserInfos = privilegeUserInfoDao.selectAll();

for (PrivilegeUserInfo privilegeUserInfo : privilegeUserInfos) {
    String password = privilegeUserInfo.getPassword();
    
    if (StringUtils.isBlank(password)) {
        continue;  // 跳过空密码
    }
    
    try {
        // 第2步：RSA解密
        password = RSAUtils.privateDecrypt(privateKey, password);
    } catch (Exception e) {
        log.info("用户{}RSA解密失败！", privilegeUserInfo.getId());
        continue;  // 解密失败跳过
    }
    
    // 第3步：更新为解密后的密码
    privilegeUserInfo.setPassword(password);
    privilegeUserInfoDao.updateByPrimaryKey(privilegeUserInfo);
}
```

---

## 五、菜单管理方法

---

### 方法：MenuInfoServiceImpl.createMenu()

**一句话人话**：创建菜单并关联到机构系统

**🏠 生活比喻**
就像酒店装修时添加新房间：
1. 先确定房间名称和位置（菜单名称和父级）
2. 检查房间是否重复
3. 把房间分配给对应楼层（关联系统）
4. 调整房间顺序

**📥 参数说明**

| 参数 | 人话解释 | 举个例子 |
|------|----------|----------|
| `vo.name` | 菜单名称 | `"用户管理"` |
| `vo.url` | 菜单URL | `"/privilege/user"` |
| `vo.systemId` | 所属系统ID | `"sys-001"` |
| `vo.parentId` | 父级菜单ID | `"menu-parent"` |
| `vo.orderIndex` | 排序号 | `1` |
| `vo.enable` | 启用状态 | `1` |

**📖 逐步拆解**

```java
// 第1步：获取当前用户机构ID
String orgId = UserUtils.getUser().getOrgId();

// 第2步：复制属性
PrivilegeMenuInfo privilegeMenuInfo = new PrivilegeMenuInfo();
BeanUtils.copyProperties(vo, privilegeMenuInfo);

// 第3步：校验URL唯一性
if (StringUtils.isNotBlank(vo.getUrl())) {
    PrivilegeMenuInfo info = new PrivilegeMenuInfo();
    info.setUrl(vo.getUrl());
    List<PrivilegeMenuInfo> list = privilegeMenuInfoService.queryInfo(info);
    if (CollUtil.isNotEmpty(list)) {
        return ApiResponse.fail("模块链接重复，请修改后重新创建。");
    }
}

// 第4步：校验菜单名唯一性
PrivilegeMenuInfo menuInfo = new PrivilegeMenuInfo();
menuInfo.setUrl(vo.getUrl());
menuInfo.setName(vo.getName());
List<PrivilegeMenuInfo> privilegeMenuInfoList = 
    privilegeMenuInfoService.queryInfo(menuInfo);
if (CollUtil.isNotEmpty(privilegeMenuInfoList)) {
    return ApiResponse.fail("模块重复，请修改后重新创建。");
}

// 第5步：设置审计字段并保存
privilegeMenuInfo.setCreator(UserUtils.getUser().getUserAccount());
privilegeMenuInfo.setModifier(UserUtils.getUser().getUserAccount());
privilegeMenuInfo.setCreatetime(LocalDateTime.now());
privilegeMenuInfo.setModifytime(LocalDateTime.now());
privilegeMenuInfoService.save(privilegeMenuInfo);

// 第6步：自动关联到机构系统
boolean result = false;
List<PrivilegeOrgSystem> privilegeOrgSystems = 
    privilegeOrgSystemDao.selectOrgSysInfoByOrgSysId(orgId, vo.getSystemId());

if (CollUtil.isNotEmpty(privilegeOrgSystems)) {
    for (PrivilegeOrgSystem system : privilegeOrgSystems) {
        if (privilegeMenuInfo.getId().equals(system.getMenuId())) {
            result = true;  // 已存在关联
        }
    }
}

if (!result) {
    // 不存在则新建关联
    PrivilegeOrgSystem privilegeOrgSystem = new PrivilegeOrgSystem();
    privilegeOrgSystem.setOrgId(orgId);
    privilegeOrgSystem.setSystemId(vo.getSystemId());
    privilegeOrgSystem.setMenuId(privilegeMenuInfo.getId());
    privilegeOrgSystem.setIsRelates("0");
    privilegeOrgSystem.setCreatetime(LocalDateTime.now());
    privilegeOrgSystem.setModifier(UserUtils.getUser().getUserAccount());
    privilegeOrgSystem.setModifytime(LocalDateTime.now());
    privilegeOrgSystemService.save(privilegeOrgSystem);
}

// 第7步：调整排序
if (StringUtils.isNotBlank(vo.getParentId())) {
    String resultOrder = privilegeMenuInfoService.modifyOrder(vo, privilegeMenuInfo);
    if (StringUtils.isNotEmpty(resultOrder)) {
        return ApiResponse.fail(resultOrder);
    }
}

return ApiResponse.ok(privilegeMenuInfo.getId());
```

**🐛 小白易懵点**

1. **自动关联机构**：创建菜单时会自动关联到当前用户的机构
2. **URL和名称都校验唯一性**：两个维度都检查
3. **排序自动调整**：插入后兄弟节点的排序会重新编号

---

### 方法：MenuInfoServiceImpl.modifyOrder()

**一句话人话**：调整菜单的排序位置

**🏠 生活比喻**
就像酒店楼层重新排房号：
- 你要把101房间挪到103的位置
- 原来的102、103要往后挪一位
- 最后所有房间号连续

**📥 参数说明**

| 参数 | 人话解释 | 举个例子 |
|------|----------|----------|
| `vo.id` | 要移动的菜单ID | `"menu-001"` |
| `vo.parentId` | 父级菜单ID | `"menu-parent"` |
| `vo.orderIndex` | 新的排序位置 | `3` |
| `info` | 菜单对象（新建时传入） | `PrivilegeMenuInfo对象` |

**📖 逐步拆解**

```java
// 第1步：计算实际插入位置
Integer addIndex = vo.getOrderIndex() - 1;  // 转成0-based索引

// 第2步：获取同级所有子菜单
String orgId = UserUtils.getUser().getOrgId();
PrivilegeMenuInfoDto dto = new PrivilegeMenuInfoDto();
dto.setParentId(vo.getParentId());
dto.setOrgId(orgId);
List<PrivilegeMenuInfo> childrenMenuList = 
    privilegeMenuInfoService.queryMenuOrder(dto);

// 第3步：获取菜单对象（如果是新建的）
PrivilegeMenuInfo menuInfo = new PrivilegeMenuInfo();
menuInfo.setId(vo.getId());
menuInfo = privilegeMenuInfoService.selectOne(menuInfo);

// 第4步：从列表中移除当前菜单（如果是已存在的）
childrenMenuList.removeIf(pinfo -> vo.getId().equals(pinfo.getId()));

// 第5步：计算最终插入位置
Integer finalAddIndex = addIndex - 1;
if (addIndex >= 0 && addIndex <= childrenMenuList.size()) {
    childrenMenuList.add(addIndex, menuInfo);
} else if (finalAddIndex >= 0 && finalAddIndex <= childrenMenuList.size()) {
    childrenMenuList.add(finalAddIndex, menuInfo);
} else {
    return "排序错误";  // 超出范围
}

// 第6步：重新编号所有菜单
int orderIndex = 1;
for (PrivilegeMenuInfo pinfo : childrenMenuList) {
    pinfo.setOrderIndex(orderIndex);
    privilegeMenuInfoService.save(pinfo);
    orderIndex++;
}

return null;  // 成功返回null
```

**🐛 小白易懵点**

1. **0-based vs 1-based**：`orderIndex`前端传1，但代码里转成0
2. **双重边界检查**：`addIndex` 和 `finalAddIndex` 两个都检查
3. **不传menuId**：新建菜单时传入`info`参数，修改时传null

---

## 六、安全机制总结

### 🔐 三层安全防护体系

```
┌─────────────────────────────────────────────────────────────┐
│  第1层：TokenInterceptorConfig（门卫）                        │
│  ├─ 验证Token存在且有效                                      │
│  ├─ 检查权限码包含"88"                                       │
│  ├─ 自动续期Token                                           │
│  └─ 存入ThreadLocal                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  第2层：APIAuthorityFilter（楼层保安）                       │
│  ├─ 拦截 /privilege/user/* 路径                             │
│  ├─ 验证URL在权限列表中                                      │
│  └─ 模糊匹配机制（contains）                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  第3层：Service层业务校验（部门经理）                         │
│  ├─ 参数完整性校验                                           │
│  ├─ 业务规则校验（重复、空值等）                              │
│  └─ 敏感词过滤                                               │
└─────────────────────────────────────────────────────────────┘
```

### 🔑 Redis安全缓存

| Key | 存储内容 | 生命周期 |
|-----|---------|----------|
| `API_TOKEN:{token}` | 用户登录信息 | 1440分钟（24小时） |
| `flag:{userId}` | 用户权限编码 | 永久（手动清理） |
| `UrlPermission:{userId}` | 用户可访问URL列表 | 永久（手动清理） |
| `userid:{userId}` | Token映射 | 与Token同步 |

### ⚠️ 安全风险等级

| 风险 | 位置 | 建议 |
|------|------|------|
| 🔴 高 | APIAuthorityFilter URL模糊匹配 | 改为精确匹配 |
| 🔴 高 | 权限码"88"硬编码 | 改为配置项 |
| 🔴 高 | 硬编码加密密钥 | 使用密钥管理服务 |
| 🟡 中 | Token无条件续期 | 增加活跃度检测 |
| 🟡 中 | UserUtils默认值泄露 | 严格校验返回值 |
| 🟡 中 | 打印请求头信息 | 使用日志框架 |

---

## 📝 附录：方法统计

| Service | 已解析方法数 | 核心方法 |
|---------|------------|---------|
| UserInfoServiceImpl | 13 | create, setRoles, enableUser, resetPassword, deleteById |
| OrgInfoServiceImpl | 14 | query, setOrgSystemResources, buildTree |
| RoleInfoServiceImpl | 10 | createRole, updateRole, setResource |
| MenuInfoServiceImpl | 8 | createMenu, modifyOrder |
| TokenInterceptorConfig | 1 | preHandle |
| APIAuthorityFilter | 1 | doFilter |
| MoveServiceImpl | 3 | move, moveUserRole, passwordBackMD5 |

> 📌 **累计已解析方法**: 50+ 个核心方法
