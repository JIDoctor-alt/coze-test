# PICC人保健康权限管理系统 - 深度解析补充篇：辅助模块与BaseServiceImpl

> 🎯 本章补充解析项目中的辅助模块（AccountRecord、SensitiveWords、SystemInfo）以及BaseServiceImpl通用CRUD能力。

---

## 一、BaseServiceImpl —— 所有Service的"万能基类"

### 🎯 一句话人话
> 🏠 就像超市的自助收银机——提供一套标准操作（增删改查），每个柜台不用自己造收银机，直接用就行。

### BaseServiceImpl提供的通用方法

| 方法 | 干什么 | 对应SQL |
|------|--------|---------|
| insert(T entity) | 插入一条记录 | INSERT INTO ... |
| insertSelective(T entity) | 选择性插入（只插非空字段） | INSERT INTO ... (非空字段) |
| selectByPrimaryKey(id) | 按主键查询 | SELECT * WHERE id = ? |
| select(T entity) | 按条件查询 | SELECT * WHERE ... |
| selectAll() | 查询所有 | SELECT * |
| updateByPrimaryKey(T entity) | 按主键更新 | UPDATE ... WHERE id = ? |
| deleteByPrimaryKey(id) | 按主键删除 | DELETE WHERE id = ? |

### 🏠 打比方
BaseServiceImpl就像一个**万能遥控器**——不管你管的是电视、空调还是音响，开机、关机、调音量这些基础操作都是一样的。每个具体的Service只需要实现自己特有的"高级功能"。

---

## 二、AccountRecordServiceImpl —— 账号操作记录服务

### 🎯 一句话人话
> 🏠 就像银行的监控摄像头——记录谁在什么时候对哪个账号做了什么操作（启用/禁用）。

### 没有自定义方法？
是的！AccountRecordServiceImpl是一个空壳类，只继承了BaseServiceImpl<AccountRecord>。所有操作都走通用CRUD。

### 实际使用场景
在UserInfoServiceImpl.enableUser()中被调用：
```java
// 禁用/启用用户时，自动记录操作日志
AccountRecord accountRecord = new AccountRecord();
accountRecord.setAccount(privilegeUserInfo.getAccount());    // 被操作的账号
accountRecord.setAccountid(privilegeUserInfo.getId());       // 被操作的用户ID
accountRecord.setReason("经办人修改");                        // 操作原因
accountRecord.setUpdateaccount("经办人");                     // 操作人
accountRecord.setType("1");                                  // 操作类型
accountRecord.setEnable(privilegeUserInfo.getEnable()==0 ? "T":"F");  // T=禁用, F=启用
accountRecordService.save(accountRecord);
```

### 数据流向
```
管理员点击"禁用用户"
  → UserInfoApi.enableUser()
  → UserInfoServiceImpl.enableUser()
  → AccountRecordService.save()  ← 记录操作日志
  → 数据库 privilege_account_record 表
```

### ⚠️ 发现的问题
- **操作人固定写死为"经办人"**，应该从UserUtils获取当前操作人的真实账号
- **操作类型固定为"1"**，缺少类型枚举定义
- **没有查询接口**，记录了日志但没有API可以查看

---

## 三、SensitiveWordsServiceImpl —— 敏感词服务

### 🎯 一句话人话
> 🏠 就像论坛的违禁词过滤器——创建账号时不允许包含admin、root、system等敏感词。

### 同样没有自定义方法
SensitiveWordsServiceImpl也是空壳类，继承BaseServiceImpl<SensitiveWords>。

### 实际使用场景
在UserInfoServiceImpl.create()中被调用：
```java
// 创建用户时校验账号是否包含敏感词
String userAccount = privilegeUserInfo.getAccount();
List<SensitiveWords> sensitiveWordsList = sensitiveWordsDao.selectWords();
if (CollectionUtils.isNotEmpty(sensitiveWordsList)){
    for (SensitiveWords words : sensitiveWordsList) {
        if (userAccount.contains(words.getWord())) {
            throw new CustomException("账号包含敏感词");
        }
    }
}
```

### 敏感词列表（从代码推断）
- admin、user、system、manager、supervisor、root、postgres等系统保留词

### ⚠️ 发现的问题
- **没有管理接口**：敏感词的增删改查没有暴露API，只能通过数据库直接操作
- **匹配方式为contains**：如果敏感词是"admin"，那"badminton"也会被拦截（误杀）
- **缺少模糊匹配**：应该支持精确匹配和正则匹配两种模式

---

## 四、PrivilegeSystemInfoServiceImpl —— 系统信息服务

### 🎯 一句话人话
> 🏠 就像应用商店的分类列表——记录有哪些系统可供机构订阅。

### 没有自定义方法
同样是空壳类。自定义查询在SysInfoServiceImpl中实现。

### 数据流向
```
系统信息（门诊慢特病系统、综合查询系统...）
  → 被机构订阅（privilege_org_system）
  → 被菜单关联（privilege_menu_info.system_id）
  → 被角色资源关联（privilege_role_resource.system_id）
```

---

## 五、SysInfoServiceImpl —— 系统信息查询服务

### 源码位置
`/tmp/picc-mzmtb-user/picchealth-privilege-server/src/main/java/com/picchealth/module/sys/service/impl/SysInfoServiceImpl.java`

### 方法：querySysInfo(PrivilegeSystemInfoVo vo)

> 🎯 **一句话人话**：查询系统列表，支持按系统名称模糊搜索。

#### 📥 参数
| 参数 | 说明 | 举例 |
|------|------|------|
| sysName | 系统名称（模糊查询） | "门诊" |
| pageIndex | 页码 | 1 |
| pageSize | 每页条数 | 10 |

#### 📤 返回
`ResultPage<PrivilegeSystemInfoDto>` —— 分页的系统列表

#### 📖 内部步骤
1. 创建查询条件对象
2. 如果sysName不为空，设置模糊查询条件
3. 调用Mapper查询
4. 将PO转为DTO返回

---

## 六、辅助模块学习思考

| 模块 | 问题 | 建议 |
|------|------|------|
| AccountRecord | 操作人写死"经办人" | 改为UserUtils.getUser().getUserAccount() |
| AccountRecord | 没有查询API | 添加查询接口供审计使用 |
| AccountRecord | 操作类型无枚举 | 定义AccountRecordTypeEnum |
| SensitiveWords | 没有管理API | 添加CRUD接口 |
| SensitiveWords | contains误杀 | 改为精确匹配或正则匹配 |
| SystemInfo | 只有一个查询方法 | 可添加系统的新增/编辑/删除 |

---

## 七、项目Service层完整清单

| Service | 有自定义方法？ | 方法数 | 复杂度 |
|---------|-------------|-------|--------|
| OrgInfoServiceImpl | ✅ | 12 | 🔴 高（query()200行） |
| UserInfoServiceImpl | ✅ | 15 | 🔴 高（setAuths复杂） |
| RoleInfoServiceImpl | ✅ | 12 | 🟡 中 |
| MenuInfoServiceImpl | ✅ | 10+ | 🟡 中 |
| PrivilegeMenuInfoServiceImpl | ✅ | 若干 | 🟢 低 |
| PrivilegeMenuServiceServiceImpl | ✅ | 若干 | 🟢 低 |
| SysInfoServiceImpl | ✅ | 1 | 🟢 低 |
| MoveServiceImpl | ✅ | 3 | 🟡 中（迁移逻辑） |
| AccountRecordServiceImpl | ❌ | 0（继承BaseService） | 🟢 最低 |
| SensitiveWordsServiceImpl | ❌ | 0（继承BaseService） | 🟢 最低 |
| PrivilegeSystemInfoServiceImpl | ❌ | 0（继承BaseService） | 🟢 最低 |
| PrivilegeOrgSystemServiceImpl | ❌ | 0（继承BaseService） | 🟢 最低 |

**统计**：12个Service类，其中8个有自定义方法，4个为空壳（纯CRUD走BaseService）。

---

📎 **延伸阅读**：
- [深度解析-菜单与系统管理](picc-mzmtb-user-深度解析第四章-菜单与系统管理.md) - MenuInfoServiceImpl、PrivilegeMenuServiceServiceImpl的完整方法详解
- [深度解析](picc-mzmtb-user-深度解析.md) - BaseServiceImpl通用CRUD能力和安全机制说明
- [数据库ER图与表结构](picc-mzmtb-user-数据库ER图与表结构.md) - 辅助模块涉及的数据库表结构



---

## 八、BaseServiceImpl方法逐行解析

> 🏠 BaseServiceImpl就像超市的自助收银机——不管你买什么，扫码、付款、打印小票的流程都是一样的

### 1. insert(T entity) —— 插入一条记录

**🏠 一句话解释**：往数据库的表格里新增一行数据，就像往Excel表格里新加一行。

**📥 参数说明**：
| 参数 | 类型 | 说明 | 举例 |
|------|------|------|------|
| entity | T | 要插入的数据对象 | new PrivilegeUserInfo() |

**📤 返回值**：无（void）

**📖 逐步拆解**：
```java
public String insert(T entity) {
    // 步骤1：检查数据是否有效
    // if (entity == null) throw new Exception("数据不能为空");
    
    // 步骤2：设置创建时间
    // entity.setCreateTime(LocalDateTime.now());
    
    // 步骤3：设置主键ID（如果是自增或UUID）
    // entity.setId(UUID.randomUUID().toString());
    
    // 步骤4：执行SQL插入
    // INSERT INTO table_name (col1, col2, ...) VALUES (?, ?, ...)
    
    // 步骤5：返回插入结果
}
```

**🏪 生活比喻**：你去奶茶店点单，店员在收银系统里新开一笔订单，记录你要什么奶茶。

**⚠️ 易懵点**：
- 这个方法会插入所有字段，包括null值
- 如果某个字段不想插入，用`insertSelective()`

---

### 2. insertSelective(T entity) —— 选择性插入

**🏠 一句话解释**：只插入非空字段，就像填表格时只填必填项，空白的可以不填。

**📥 参数说明**：
| 参数 | 类型 | 说明 |
|------|------|------|
| entity | T | 要插入的数据对象 |

**📤 返回值**：无（void）

**📖 逐步拆解**：
```java
public String insertSelective(T entity) {
    // 步骤1：只取出有值的字段
    // List<String> nonNullFields = entity.getNonNullFields();
    
    // 步骤2：只拼接有值的列名
    // SQL: INSERT INTO table_name (col1, col3, col5) VALUES (?, ?, ?)
    //      不插入 col2, col4 这些空字段
    
    // 步骤3：执行SQL
    // 好处：数据库会用默认值填充空字段
}
```

**🏪 生活比喻**：填入职登记表时，标了星号的必填项必须填，没标星号的可选项可以空着。

**⚠️ 易懵点**：
- `insert()` vs `insertSelective()`：前者插入所有字段（空字段存NULL），后者只插入非空字段
- 通常用`insertSelective()`更安全，避免覆盖数据库默认值

---

### 3. selectByPrimaryKey(id) —— 按主键查询

**🏠 一句话解释**：根据ID找唯一的一条记录，就像用身份证号找人。

**📥 参数说明**：
| 参数 | 类型 | 说明 | 举例 |
|------|------|------|------|
| id | String | 数据的主键ID | "123456789012345678" |

**📤 返回值**：`T` 找到的数据对象，没找到返回null

**📖 逐步拆解**：
```java
public T selectByPrimaryKey(String id) {
    // 步骤1：参数校验
    // if (id == null) return null;
    
    // 步骤2：构建查询条件
    // WHERE id = '123456789012345678'
    
    // 步骤3：执行SQL
    // SELECT * FROM table_name WHERE id = ?
    
    // 步骤4：返回结果（最多1条，因为ID唯一）
}
```

**🏪 生活比喻**：用快递单号查快递，身份证号查户籍信息。

**⚠️ 易懵点**：
- ID是String类型，不是Long
- 如果没找到，返回null，不会抛异常

---

### 4. select(T entity) —— 按条件查询

**🏠 一句话解释**：根据条件找记录，就像Excel的筛选功能。

**📥 参数说明**：
| 参数 | 类型 | 说明 | 举例 |
|------|------|------|------|
| entity | T | 查询条件对象 | new UserInfo(account="张三") |

**📤 返回值**：`List<T>` 符合条件的记录列表

**📖 逐步拆解**：
```java
public List<T> select(T entity) {
    // 步骤1：取出entity中非空字段作为查询条件
    // 例如 entity.account = "张三", entity.enable = 1
    
    // 步骤2：拼接WHERE条件
    // WHERE account = '张三' AND enable = 1
    
    // 步骤3：执行SQL
    // SELECT * FROM table_name WHERE account = '张三' AND enable = 1
    
    // 步骤4：返回结果列表（0到多条）
}
```

**🏪 生活比喻**：在通讯录里筛选"北京"+"开发部"+"30岁以下"的同事。

**⚠️ 易懵点**：
- 返回的是列表，不是单个对象
- 如果想查单个对象，用`selectOne()`

---

### 5. selectAll() —— 查询所有

**🏠 一句话解释**：把整张表的数据都查出来（软删除的除外）。

**📥 参数说明**：无

**📤 返回值**：`List<T>` 所有记录列表

**📖 逐步拆解**：
```java
public List<T> selectAll() {
    // 步骤1：默认拼接软删除条件
    // WHERE delete_at IS NULL
    
    // 步骤2：执行SQL
    // SELECT * FROM table_name WHERE delete_at IS NULL
    
    // 步骤3：返回所有记录
}
```

**🏪 生活比喻**：打开一个Excel文件，看到所有没被删除的行。

**⚠️ 易懵点**：
- 已经被软删除的记录查不到
- 数据量大时慎用，会内存溢出

---

### 6. updateByPrimaryKey(T entity) —— 按主键更新

**🏠 一句话解释**：根据ID更新整条记录，就像修改快递单上的信息。

**📥 参数说明**：
| 参数 | 类型 | 说明 |
|------|------|------|
| entity | T | 要更新的数据（必须包含ID） |

**📤 返回值**：受影响行数（通常1）

**📖 逐步拆解**：
```java
public int updateByPrimaryKey(T entity) {
    // 步骤1：从entity取出ID作为条件
    // WHERE id = entity.id
    
    // 步骤2：取出entity中所有字段作为更新值
    // UPDATE table_name SET col1 = ?, col2 = ?, ... WHERE id = ?
    
    // 步骤3：执行SQL
    // 注意：即使某个字段没变，也会更新为同样的值
    
    // 步骤4：返回更新行数
}
```

**🏪 生活比喻**：修改快递单，收件人地址变了，整张单子都要重新打印。

**⚠️ 易懵点**：
- entity必须包含ID，否则无法定位要更新哪条
- 会更新所有字段，包括null（可能把数据覆盖成null）

---

### 7. deleteByPrimaryKey(id) —— 按主键删除

**🏠 一句话解释**：根据ID删除记录（实际上是软删除）。

**📥 参数说明**：
| 参数 | 类型 | 说明 |
|------|------|------|
| id | String | 要删除记录的主键ID |

**📤 返回值**：受影响行数（通常1）

**📖 逐步拆解**：
```java
public int deleteByPrimaryKey(String id) {
    // 步骤1：校验ID不为空
    
    // 步骤2：拼接UPDATE语句（软删除）
    // UPDATE table_name SET delete_at = NOW() WHERE id = ?
    // 注意：不是DELETE FROM，而是UPDATE
    
    // 步骤3：执行SQL
    
    // 步骤4：返回更新行数
}
```

**🏪 生活比喻**：把Excel里的某一行的delete_at列打上勾，表示"这一行不要了但我还留着"。

**⚠️ 易懵点**：
- 这不是真正的物理删除，只是标记删除
- 数据还在，可以通过数据库直接查询看到

---

## 九、MoveServiceImpl方法逐行解析

> 🏠 MoveServiceImpl就像数据迁移公司的搬运工——把旧仓库的货物搬到新仓库

### 源码位置
`/tmp/picc-mzmtb-user/picchealth-privilege-server/src/main/java/com/picchealth/module/sys/service/impl/MoveServiceImpl.java`

---

### 方法1：move() —— 角色数据迁移

**🏠 一句话解释**：把旧系统的角色和菜单关系，迁移到新系统的角色表里。

**📥 参数说明**：无

**📤 返回值**：无（void）

**🏪 生活比喻**：旧公司有100个员工岗位描述，新公司需要重建这些岗位，但每个岗位要给一个新的工牌号。

**📖 逐步拆解**：

```java
@Transactional(rollbackForClassName = {"Exception"})
public void move() {
    // ===== 步骤1：从旧表读取所有角色和资源关系 =====
    // SQL: SELECT * FROM sys_role_module_rel
    List<PrivilegeRoleInfo> privilegeRoleInfos = sysRoleModuleRelDao.moveRoleResources();
    
    // ===== 步骤2：遍历每个角色，处理拆分逻辑 =====
    int index = 1;      // 序号计数器
    String groupId = null;  // 上一个角色的ID
    
    for (int i = 0; i < privilegeRoleInfos.size(); i++) {
        PrivilegeRoleInfo privilegeRoleInfo = privilegeRoleInfos.get(i);
        
        // ===== 步骤3：判断是否是新角色（和上一个不同） =====
        if (i == 0 || !privilegeRoleInfos.get(i).getCode().equals(
                privilegeRoleInfos.get(i-1).getCode())) {
            // 【情况A】新角色，给它一个新的唯一ID
            // 新ID = 旧ID（保持关联性）
            
            // 步骤3.1：查询这个角色的所有菜单
            List<SysRoleModuleRel> sysRoleModuleRels = 
                sysRoleModuleRelDao.queryResourcesByRoleIds(privilegeRoleInfo.getId());
            
            // 步骤3.2：给每个菜单关系分配新的ID
            for (SysRoleModuleRel rel : sysRoleModuleRels) {
                PrivilegeRoleResource privilegeRoleResource = new PrivilegeRoleResource();
                String roleId = UniqueIDGenerator.generateUniqueID();
                privilegeRoleResource.setId(roleId);
                privilegeRoleResource.setSystemId("459694197360955392");
                privilegeRoleResource.setRoleId(rel.getRoleId());
                privilegeRoleResource.setMenuId(rel.getModuleId());
                privilegeRoleResourceDao.insert(privilegeRoleResource);
            }
            
            // 步骤3.3：插入新角色
            privilegeRoleInfo.setModifytime(privilegeRoleInfo.getCreatetime());
            privilegeRoleInfoDao.insert(privilegeRoleInfo);
            log.info("新角色: " + privilegeRoleInfo.getId() + " " + 
                    privilegeRoleInfo.getCode());
            
            index = 1;  // 重置序号
            groupId = privilegeRoleInfos.get(i).getId();  // 记住这个ID
        } else {
            // 【情况B】同角色不同机构，需要拆分
            // 比如"经办员"角色，西安有，宝鸡也有，新系统要分别建两条
            
            // 步骤3.4：生成新的拆分ID = 原ID + 序号
            String id = groupId + String.valueOf(index);
            index++;
            
            // 步骤3.5：复制菜单关系到新角色
            List<SysRoleModuleRel> sysRoleModuleRels = 
                sysRoleModuleRelDao.queryResourcesByRoleIds(groupId);
            for (SysRoleModuleRel rel : sysRoleModuleRels) {
                // ... 同样的插入逻辑 ...
            }
            
            // 步骤3.6：插入拆分后的角色（用新ID）
            privilegeRoleInfo.setId(id);
            privilegeRoleInfoDao.insert(privilegeRoleInfo);
        }
    }
}
```

**⚠️ 易懵点**：
- 同一个角色code（如"经办员"），在不同机构是不同记录
- 新ID的生成规则：第一个用原ID，后面的用"原ID+序号"（如001, 002）
- 迁移时按机构拆分，避免角色冲突

**🔑 关键变量说明**：
| 变量 | 含义 |
|------|------|
| `groupId` | 同code角色的第一个ID |
| `index` | 拆分序号 |
| `code` | 角色编码（决定是否要拆分） |

---

### 方法2：moveUserRole() —— 用户角色关系迁移

**🏠 一句话解释**：把旧系统的用户-角色对应关系，迁移到新系统。

**📥 参数说明**：无

**📤 返回值**：无（void）

**🏪 生活比喻**：旧公司张三和李四是"经办员"，新公司要给张和李分配新的"经办员"工牌。

**📖 逐步拆解**：

```java
@Transactional(rollbackForClassName = {"Exception"})
public void moveUserRole() {
    // ===== 前提：必须先执行 move() =====
    // 因为角色ID变了，需要找新的角色ID
    
    // ===== 步骤1：从旧表读取所有用户角色关系 =====
    // SQL: SELECT * FROM sys_user_role_rel
    List<SysUserRoleRel> sysUserRoleRelList = sysUserRoleRelDao.queryAllSysUserRoleRel();
    
    // ===== 步骤2：遍历每个用户角色关系 =====
    for (SysUserRoleRel sysUserRoleRel : sysUserRoleRelList) {
        
        // 步骤2.1：找到用户所属的机构
        // SQL: SELECT org_id FROM privilege_user_info WHERE id = ?
        String orgId = sysUserRoleRelDao.selectOrgIdByUserId(sysUserRoleRel.getUserId());
        
        // 步骤2.2：根据旧角色ID找到旧角色信息
        // SQL: SELECT * FROM privilege_role_info WHERE id = ?
        PrivilegeRoleInfo roleInfo = privilegeRoleInfoDao.queryRoleByID(
            sysUserRoleRel.getRoleId());
        if (roleInfo == null) continue;  // 找不到就跳过
        
        // 步骤2.3：获取角色编码
        String code = roleInfo.getCode();
        
        // 步骤2.4：在新表中查找对应机构下的同编码角色
        // SQL: SELECT * FROM privilege_role_info 
        //      WHERE org_id = ? AND code = ?
        PrivilegeRoleInfo newRoleInfo = privilegeRoleInfoDao.queryRoleByOrgIdAndCode(
            orgId, code);
        if (newRoleInfo == null) continue;  // 找不到就跳过
        
        // 步骤2.5：创建用户角色关联记录
        PrivilegeUserRoleInfo privilegeUserRoleInfo = new PrivilegeUserRoleInfo();
        privilegeUserRoleInfo.setId(UUIDUtil.getUUID());  // 新ID
        privilegeUserRoleInfo.setUserId(sysUserRoleRel.getUserId());  // 同一用户
        privilegeUserRoleInfo.setRoleId(newRoleInfo.getId());  // 新角色ID！
        privilegeUserRoleDao.insert(privilegeUserRoleInfo);
    }
}
```

**⚠️ 易懵点**：
- 必须先执行`move()`再执行这个方法
- 关联逻辑：用"机构ID + 角色编码"找新角色
- 旧角色ID和新角色ID完全不同，不能直接用

---

### 方法3：passwordBackMD5() —— 密码解密回退

**🏠 一句话解释**：把RSA加密的密码解密后存回数据库（实际是MD5值）。

**📥 参数说明**：无

**📤 返回值**：无（void）

**🏪 生活比喻**：旧系统把密码用锁锁在箱子里，这个方法是开锁，把密码取出来换成明文MD5。

**📖 逐步拆解**：

```java
public void passwordBackMD5() {
    // ===== 步骤1：读取所有用户密码 =====
    List<PrivilegeUserInfo> users = privilegeUserInfoDao.selectAll();
    
    for (PrivilegeUserInfo user : users) {
        String rsaPassword = user.getPassword();  // RSA加密的密码
        
        try {
            // ===== 步骤2：用RSA私钥解密 =====
            // RSA解密：加密后的密码 → 明文（实际是MD5）
            String md5Password = RSAUtils.decryptByPrivateKey(
                rsaPassword, privateKey);
            
            // ===== 步骤3：把解密后的MD5密码存回 =====
            // 注意：这里是MD5，不是明文
            user.setPassword(md5Password);
            privilegeUserInfoDao.updateByPrimaryKey(user);
            
        } catch (Exception e) {
            // 解密失败的跳过（比如密码本来就是明文的）
            log.warn("密码解密失败，用户ID: " + user.getId());
        }
    }
}
```

**⚠️ 易懵点**：
- 解密后的密码是MD5格式，不是明文
- 解密失败的可能原因：密码本身就是明文/MD5（未加密）
- 这是一个一次性迁移脚本，跑完就可以删掉

---

## 十、PrivilegeOrgSystemServiceImpl方法逐行解析

> 🏠 PrivilegeOrgSystemServiceImpl就像订阅管理——管理每个机构订阅了哪些系统

### 源码位置
`/tmp/picc-mzmtb-user/picchealth-privilege-server/src/main/java/com/picchealth/module/sys/service/impl/PrivilegeOrgSystemServiceImpl.java`

### 类的真相

```java
@Service
@Slf4j
public class PrivilegeOrgSystemServiceImpl 
    extends BaseServiceImpl<PrivilegeOrgSystem> 
    implements PrivilegeOrgSystemService {
    // 空壳类！所有方法都来自父类BaseServiceImpl
}
```

**🏠 一句话解释**：这是一个空壳类，没有自己写任何方法，所有操作都继承自BaseServiceImpl。

**🏪 生活比喻**：公司前台只提供标准服务（接电话、收快递），没有定制服务。

**📖 为什么没有自定义方法？**

| 功能 | 来自 | 原因 |
|------|------|------|
| 查询机构订阅 | BaseServiceImpl.select() | 标准的按条件查询 |
| 添加订阅 | BaseServiceImpl.insertSelective() | 标准的插入 |
| 删除订阅 | BaseServiceImpl.deleteByPrimaryKey() | 标准的软删除 |
| 修改订阅 | BaseServiceImpl.updateByPrimaryKey() | 标准的更新 |

**⚠️ 这个类的实际使用场景**：

```java
// 在OrgInfoServiceImpl中被调用
@Resource
private PrivilegeOrgSystemService privilegeOrgSystemService;

// 添加机构订阅
public void addOrgSystem(String orgId, String systemId) {
    PrivilegeOrgSystem orgSystem = new PrivilegeOrgSystem();
    orgSystem.setOrgId(orgId);
    orgSystem.setSystemId(systemId);
    privilegeOrgSystemService.insertSelective(orgSystem);  // 调用的父类方法
}

// 查询机构订阅
public List<PrivilegeOrgSystem> getOrgSystems(String orgId) {
    PrivilegeOrgSystem query = new PrivilegeOrgSystem();
    query.setOrgId(orgId);
    return privilegeOrgSystemService.select(query);  // 调用的父类方法
}
```

**⚠️ 易懵点**：
- 空壳类不是没用的类，它定义了业务边界
- 将来如果需要特殊逻辑，可以在这里添加

---

## 十一、Service方法调用关系图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Controller层（入口）                          │
│  UserInfoApi  OrgInfoApi  RoleInfoApi  MenuInfoApi  MoveApi          │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Service层（业务逻辑）                          │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
│  │UserInfoSvc  │  │ OrgInfoSvc  │  │ RoleInfoSvc │                  │
│  │  15个方法   │  │  12个方法   │  │  12个方法   │                  │
│  └─────────────┘  └─────────────┘  └─────────────┘                  │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │MenuInfoSvc  │  │  SysInfoSvc │  │  MoveSvc    │  │ BaseSvc   │ │
│  │  10+方法    │  │  1个方法    │  │  3个方法    │  │ 7个通用方法│ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘ │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │AccountRecord│  │SensitiveWrd │  │PrivilegeOrg │                 │
│  │   空壳类    │  │   空壳类    │  │   空壳类    │                 │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DAO层（数据库操作）                            │
│  UserInfoDao  OrgInfoDao  RoleInfoDao  MenuInfoDao  PrivilegeOrgDao  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         数据库（GaussDB）                             │
│  privilege_user_info  privilege_org_info  privilege_role_info        │
│  privilege_menu_info  privilege_org_system  privilege_account_record │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 十二、Service方法完整清单

| Service类 | 自定义方法数 | 复杂度 | 主要功能 |
|-----------|-------------|--------|---------|
| UserInfoServiceImpl | 15 | 🔴 高 | 用户CRUD、权限分配 |
| OrgInfoServiceImpl | 12 | 🔴 高 | 机构CRUD、机构树 |
| RoleInfoServiceImpl | 12 | 🟡 中 | 角色CRUD、权限分配 |
| MenuInfoServiceImpl | 10+ | 🟡 中 | 菜单CRUD、菜单树 |
| SysInfoServiceImpl | 1 | 🟢 低 | 系统列表查询 |
| MoveServiceImpl | 3 | 🟡 中 | 数据迁移（一次性） |
| PrivilegeMenuInfoServiceImpl | 若干 | 🟢 低 | 菜单信息CRUD |
| PrivilegeMenuServiceServiceImpl | 若干 | 🟢 低 | 菜单服务CRUD |
| AccountRecordServiceImpl | 0 | 🟢 最低 | 继承BaseService |
| SensitiveWordsServiceImpl | 0 | 🟢 最低 | 继承BaseService |
| PrivilegeSystemInfoServiceImpl | 0 | 🟢 最低 | 继承BaseService |
| PrivilegeOrgSystemServiceImpl | 0 | 🟢 最低 | 继承BaseService |

**统计**：12个Service类
- 有自定义方法：8个
- 空壳类（纯CRUD）：4个
- 总方法数：73+个

---

## 十三、核心Service方法详解（带生活比喻）

### UserInfoServiceImpl.create() —— 创建用户

```java
/**
 * 🏠 创建新用户
 * 
 * 生活比喻：奶茶店开业，登记新员工信息
 * 
 * 步骤：
 * 1. 检查账号是否包含敏感词（admin/root/...)
 * 2. 检查账号是否已存在
 * 3. 生成UUID作为用户ID
 * 4. SM4加密密码
 * 5. 设置创建时间和默认状态
 * 6. 插入数据库
 * 7. 返回用户ID
 */
public String create(PrivilegeUserInfoDto privilegeUserInfoDto) {...}
```

### OrgInfoServiceImpl.query() —— 机构查询

```java
/**
 * 🏠 机构权限范围查询（最复杂的查询）
 * 
 * 生活比喻：查找"你能看到哪些机构的数据"
 * 
 * 权限三维度：
 * 维度1：你所在的机构（orgId）
 * 维度2：你的管辖范围（authCode）
 * 维度3：你订阅的系统（systemIds）
 * 
 * 步骤：
 * 1. 获取当前用户信息
 * 2. 根据orgId判断是查本机构还是下级机构
 * 3. 根据authCode判断管辖范围（88=管全部，1=管自己）
 * 4. 根据systemIds过滤系统
 * 5. 拼接WHERE条件查询
 * 6. 构建树形结构返回
 */
public ResultPage<OrgSystemVo> query(OrgQueryVo orgQueryVo) {...}
```

### RoleInfoServiceImpl.setResource() —— 角色权限分配

```java
/**
 * 🏠 给角色分配菜单权限
 * 
 * 生活比喻：给员工分配工牌能开的门禁
 * 
 * 步骤：
 * 1. 先删除角色原有权限（清空）
 * 2. 遍历新分配的菜单ID列表
 * 3. 为每个菜单创建角色-资源关联记录
 * 4. 插入数据库
 */
public CommonReqVo setResource(ResourceVo resourceVo) {...}
```

### MenuInfoServiceImpl.getMenuTree() —— 菜单树查询

```java
/**
 * 🏠 获取菜单树（前端菜单展示用）
 * 
 * 生活比喻：公司组织架构图
 * 
 * 步骤：
 * 1. 根据系统ID查询所有菜单
 * 2. 调用buildTree()递归构建树
 * 3. 返回树形结构
 * 
 * buildTree递归逻辑：
 * 1. 找到根节点（parentId = null 或 "0"）
 * 2. 递归构建子节点
 * 3. 子节点找到自己的子节点
 * 4. 直到没有子节点
 */
public ApiResponse getMenuTree(PrivilegeMenuInfoVo vo) {...}
```

---

## 十四、辅助模块学习思考详解

### 1. AccountRecordServiceImpl —— 操作记录服务

**当前问题**：
```java
// 问题1：操作人写死了
accountRecord.setUpdateaccount("经办人");  // 应该用UserUtils.getUser()

// 问题2：操作类型是固定值
accountRecord.setType("1");  // 应该有枚举定义

// 问题3：没有查询接口
// 记录了日志但查不出来
```

**学习思考**：
```java
// 改进1：使用UserUtils获取真实操作人
UserInfoVo currentUser = UserUtils.getUser();
accountRecord.setUpdateaccount(currentUser.getUserAccount());

// 改进2：定义操作类型枚举
public enum AccountRecordTypeEnum {
    ENABLE("1", "启用用户"),
    DISABLE("2", "禁用用户"),
    RESET_PASSWORD("3", "重置密码"),
    UPDATE_INFO("4", "修改信息");
}

// 改进3：添加查询接口
public ResultPage<AccountRecordVo> queryRecords(AccountRecordQueryVo vo) {
    // 支持按时间、用户账号、操作类型等条件查询
}
```

### 2. SensitiveWordsServiceImpl —— 敏感词服务

**当前问题**：
```java
// 问题1：没有管理接口
// 只能在数据库手动添加敏感词

// 问题2：contains方式匹配会误杀
if (userAccount.contains(words.getWord())) {  // "badminton"包含"admin"
// 如果敏感词是"admin"，会误杀"badminton"用户

// 问题3：匹配方式单一
// 只有contains，应该支持精确匹配、正则匹配等
```

**学习思考**：
```java
// 改进1：添加CRUD接口
public void addSensitiveWord(String word, String type) {...}
public void deleteSensitiveWord(String id) {...}

// 改进2：改进匹配逻辑
public boolean isValidAccount(String account) {
    List<SensitiveWords> words = sensitiveWordsDao.selectAll();
    for (SensitiveWords sw : words) {
        if ("EXACT".equals(sw.getMatchType())) {
            // 精确匹配：账号 == 敏感词
            if (account.equals(sw.getWord())) return false;
        } else if ("REGEX".equals(sw.getMatchType())) {
            // 正则匹配：支持正则表达式
            if (account.matches(sw.getWord())) return false;
        } else {
            // 前后缀匹配：敏感词在开头或结尾
            if (account.startsWith(sw.getWord()) || 
                account.endsWith(sw.getWord())) return false;
        }
    }
    return true;
}
```

### 3. PrivilegeOrgSystemServiceImpl —— 机构订阅服务

**当前问题**：
```java
// 空壳类，缺少业务方法
// 比如：批量订阅、订阅检查等
```

**学习思考**：
```java
// 改进1：批量订阅
public void batchSubscribe(String orgId, List<String> systemIds) {
    for (String systemId : systemIds) {
        // 检查是否已订阅
        if (!hasSubscribed(orgId, systemId)) {
            PrivilegeOrgSystem pos = new PrivilegeOrgSystem();
            pos.setOrgId(orgId);
            pos.setSystemId(systemId);
            this.insertSelective(pos);
        }
    }
}

// 改进2：检查订阅状态
public boolean hasSubscribed(String orgId, String systemId) {
    PrivilegeOrgSystem query = new PrivilegeOrgSystem();
    query.setOrgId(orgId);
    query.setSystemId(systemId);
    return !CollectionUtils.isEmpty(this.select(query));
}

// 改进3：获取已订阅的系统列表
public List<PrivilegeSystemInfo> getSubscribedSystems(String orgId) {
    // ...查询逻辑
}
```
