# PICC人保健康权限管理系统 - 深度解析第四章
## 菜单与系统管理模块（Menu & System Management）

> 📅 文档版本：v1.0  
> 🎯 适用对象：零基础开发人员  
> 📂 对应源码：`picc-mzmtb-user/picchealth-privilege-server`

---

## 📖 目录导航

1. [业务概述：菜单系统是权限管理的"骨架"](#1-业务概述菜单系统是权限管理的骨架)
2. [核心数据模型](#2-核心数据模型)
3. [菜单树构建原理](#3-菜单树构建原理)
4. [服务架构全图](#4-服务架构全图)
5. [MenuInfoServiceImpl 方法详解](#5-menuinfoserviceimpl-方法详解)
6. [PrivilegeMenuInfoServiceImpl 方法详解](#6-privilegemenuinfoserviceimpl-方法详解)
7. [PrivilegeMenuServiceServiceImpl 方法详解](#7-privilegemenuserviceserviceimpl-方法详解)
8. [SysInfoServiceImpl 方法详解](#8-sysinfoserviceimpl-方法详解)
9. [常见业务场景解析](#9-常见业务场景解析)

---

## 1. 业务概述：菜单系统是权限管理的"骨架"

### 🏠 打个比方

想象一个**大型商场**：
- **系统(System)** = 商场里的不同楼层（如：体检楼层、慢病管理楼层、药品楼层）
- **菜单(Menu)** = 每个楼层的店铺导航图
- **菜单服务(MenuService)** = 每个店铺提供的具体服务项目

```
商场（系统集合）
├── 1楼-体检中心（系统A）
│   ├── 体检预约（菜单）
│   │   ├── 创建预约（服务）
│   │   ├── 取消预约（服务）
│   │   └── 查询预约（服务）
│   └── 体检报告（菜单）
│       ├── 下载报告（服务）
│       └── 查看报告（服务）
├── 2楼-慢病管理（系统B）
│   └── ...
└── 3楼-药品管理（系统C）
    └── ...
```

### 🎯 本模块解决的问题

| 业务问题 | 系统答案 |
|---------|---------|
| 如何管理多个子系统？ | 通过 `PrivilegeSystemInfo` 系统表 |
| 如何组织复杂的菜单结构？ | 通过 `PrivilegeMenuInfo` 菜单表（树形结构） |
| 如何给菜单配置具体接口权限？ | 通过 `PrivilegeMenuService` 菜单服务表 |
| 机构能看到哪些菜单？ | 通过 `PrivilegeOrgSystem` 机构-系统关联表 |

---

## 2. 核心数据模型

### 2.1 系统表 (PrivilegeSystemInfo) - "楼层定义"

```
privilege_system_info 表
├── id              主键ID（UUID）
├── sys_code        系统编码（如：MZMTB_HEALTH）
├── sys_name        系统名称（如：慢病管理系统）
├── enable          是否启用（1=启用，0=禁用）
├── creator         创建人
├── createtime      创建时间
├── modifier        修改人
├── modifytime      修改时间
└── delete_at       删除时间（null=未删除）
```

### 2.2 菜单表 (PrivilegeMenuInfo) - "楼层导航图"

```
privilege_menu_info 表
├── id              主键ID（UUID）
├── system_id       所属系统ID（关联 privilege_system_info）
├── parent_id       父级菜单ID（null=顶级菜单）
├── code            菜单编码
├── name            菜单名称
├── menu_level      菜单层级（1=一级，2=二级...）
├── menu_type       菜单类型（目录/菜单/按钮）
├── is_sys_menu     是否系统菜单（1=是，0=否）
├── url             请求地址
├── enable          是否启用
├── order_index     排序序号
├── remark          备注说明
└── delete_at       删除时间
```

### 2.3 菜单服务表 (PrivilegeMenuService) - "店铺服务清单"

```
privilege_menu_service 表
├── id              主键ID
├── menu_id         所属菜单ID
├── service_url     接口URL（如：/api/appointment/create）
├── service_name    接口名称
├── enable          是否启用
└── delete_at       删除时间
```

### 2.4 机构系统关联表 (PrivilegeOrgSystem) - "哪些机构能进哪些楼层"

```
privilege_org_system 表
├── id              主键ID
├── system_id       系统ID
├── org_id          机构ID
├── menu_id         菜单ID
├── is_relates      是否关联（1=关联，0=未关联）
└── delete_at       删除时间
```

---

## 3. 菜单树构建原理

### 🌳 树形结构的本质

菜单系统是多级树形结构，支持无限层级：

```
                    根菜单 (parent_id = null)
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
    菜单A            菜单B            菜单C
        │               │
        ▼               ▼
    子菜单A1        子菜单B1
        │
        ▼
    子菜单A1-1
```

### 🔄 递归构建算法（Java代码解读）

```java
// MenuInfoServiceImpl.java 中的 buildTree 方法
public List<PrivilegeMenuInfoDto> buildTree(
    List<PrivilegeMenuInfoDto> collect,   // 父级菜单列表
    List<PrivilegeMenuInfoDto> allItems  // 所有菜单列表
) {
    for (PrivilegeMenuInfoDto parent : collect) {
        List<PrivilegeMenuInfoDto> dtoList = new ArrayList<>();
        
        // 遍历所有菜单，找出入参父菜单的"孩子"
        for (PrivilegeMenuInfoDto dto : allItems) {
            if (parent.getId().equals(dto.getParentId())) {
                // 递归：继续找"孩子"的"孩子"
                List<PrivilegeMenuInfoDto> menu = new ArrayList<>();
                menu.add(dto);
                List<PrivilegeMenuInfoDto> dtos = buildTree(menu, allItems);
                dtoList.addAll(dtos);
            }
        }
        // 设置当前父菜单的"孩子们"
        parent.setChildren(dtoList);
    }
    return collect;
}
```

### 🐣 小白易懵点：递归到底怎么走的？

假设有菜单：
- 菜单1（id=1, parent_id=null） → 顶级
- 菜单2（id=2, parent_id=1） → 菜单1的孩子
- 菜单3（id=3, parent_id=1） → 菜单1的孩子
- 菜单4（id=4, parent_id=2） → 菜单2的孩子

调用 `buildTree([菜单1], [菜单1,菜单2,菜单3,菜单4])` 的执行流程：

```
第1层循环：parent = 菜单1
    → 遍历所有菜单，发现 菜单2.parent_id = 菜单1.id ✓
    → 递归调用 buildTree([菜单2], [全部菜单])
    
    第2层循环：parent = 菜单2
        → 遍历所有菜单，发现 菜单4.parent_id = 菜单2.id ✓
        → 递归调用 buildTree([菜单4], [全部菜单])
        
        第3层循环：parent = 菜单4
            → 遍历所有菜单，没有菜单的 parent_id = 菜单4.id
            → 菜单4.setChildren([]) ← 空数组
            → 返回 [菜单4]
        
        → 菜单2.setChildren([菜单4])
        → 继续遍历，发现 菜单3 不是 菜单2 的孩子
    
    → 返回 [菜单2(含孩子菜单4)]

→ 菜单1.setChildren([菜单2(含孩子菜单4), 菜单3])

最终返回：菜单1（含完整树结构）
```

---

## 4. 服务架构全图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Controller 层 (API)                          │
│  ┌─────────────────────┐          ┌─────────────────────┐          │
│  │   MenuInfoApi        │          │   SysInfoApi         │          │
│  │  /privilege/menu/*  │          │  /privilege/sys/*    │          │
│  └──────────┬──────────┘          └──────────┬──────────┘          │
└─────────────┼─────────────────────────────────┼───────────────────┘
              │                                 │
              ▼                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Service 层 (业务逻辑)                          │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    MenuInfoServiceImpl                       │    │
│  │  ├── createMenu()     创建菜单                               │    │
│  │  ├── updateMenu()     更新菜单                               │    │
│  │  ├── deleteMenu()     删除菜单                               │    │
│  │  ├── getMenuTree()    获取菜单树                             │    │
│  │  ├── reviseServices() 批量增删改菜单服务                     │    │
│  │  └── queryDataStatistics() 数据统计                          │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │                                        │
│        ┌─────────────────────┼─────────────────────┐                │
│        ▼                     ▼                     ▼                │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐       │
│  │PrivilegeMenu    │ │PrivilegeMenu    │ │PrivilegeOrg      │       │
│  │InfoServiceImpl  │ │ServiceService   │ │SystemService     │       │
│  │                 │ │Impl             │ │                  │       │
│  │(复杂查询逻辑)     │ │(服务统计查询)    │ │(继承BaseService) │       │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘       │
└───────────┼──────────────────┼──────────────────┼─────────────────┘
            │                  │                  │
            ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Mapper 层 (数据库)                           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐      │
│  │PrivilegeMenu    │ │PrivilegeMenu    │ │PrivilegeOrg      │      │
│  │InfoDao.xml      │ │ServiceDao.xml  │ │SystemDao.xml    │      │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘      │
└───────────┼──────────────────┼──────────────────┼─────────────────┘
            │                  │                  │
            ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Database (MySQL)                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│  │privilege_    │ │privilege_    │ │privilege_    │ │privilege_ │ │
│  │menu_info     │ │menu_service  │ │org_system    │ │system_info│ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. MenuInfoServiceImpl 方法详解

> 🏠 这个类是最重要的业务类，负责菜单的增删改查核心逻辑

### 5.1 createMenu - 创建菜单

---

### 方法名：createMenu(菜单信息VO)

> 🎯 **一句话人话**：新增一个菜单，并且自动把它绑定到当前用户的机构下

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| name | 菜单名称 | "体检预约管理" |
| systemId | 所属系统ID | "system-uuid-xxx" |
| parentId | 父级菜单ID（可选） | "parent-menu-uuid" 或 null |
| url | 访问路径（可选） | "/api/health/appointment" |
| enable | 是否启用 | 1（启用）或 0（禁用） |
| orderIndex | 排序序号 | 1, 2, 3... |

#### 📤 返回什么？（返回值）
- `ApiResponse` - 包含创建成功的菜单ID

#### 🔗 谁会用这个方法？
- 前端菜单管理页面 → MenuInfoApi → createMenu()
- POST `/privilege/menu/create`

#### 📖 方法内部一步一步在做什么？

```
步骤1️⃣：获取当前用户信息
         ↓
         拿到当前登录用户的 orgId（机构ID）

步骤2️⃣：复制数据（VO → PO）
         ↓
         BeanUtils.copyProperties(vo, privilegeMenuInfo)
         把前端传来的数据拷贝到数据库实体

步骤3️⃣：检查URL是否重复
         ↓
         如果传了url，就去数据库查是否有相同url的菜单
         有 → 返回失败："模块链接重复"
         无 → 继续

步骤4️⃣：检查菜单名是否重复
         ↓
         在同一系统下查是否有相同名称的菜单
         有 → 返回失败："模块重复"
         无 → 继续

步骤5️⃣：保存菜单基本信息
         ↓
         设置创建人、创建时间
         privilegeMenuInfoService.save(privilegeMenuInfo)

步骤6️⃣：建立机构和菜单的关联
         ↓
         查 privilege_org_system 表
         看这个机构+系统+菜单 是否已经有关联
         没有 → 新增一条关联记录
         有 → 跳过

步骤7️⃣：调整菜单排序
         ↓
         如果传了 parentId
         调用 modifyOrder() 重新排这个父菜单下的所有子菜单

步骤8️⃣：返回成功
         ↓
         返回创建的菜单ID
```

#### ⚠️ 异常处理

| 异常情况 | 处理方式 |
|---------|---------|
| URL重复 | 返回失败："模块链接重复，请修改后重新创建" |
| 名称重复 | 返回失败："模块重复，请修改后重新创建" |
| 系统ID为空 | 校验失败，无法创建 |

#### 🐛 小白易懵点

1. **为什么要设置机构和菜单的关联？**
   - 答：不同的机构可能看到不同的菜单。比如总公司的管理员能看到所有菜单，但分公司的管理员只能看到部分菜单。

2. **modifyOrder() 是干什么的？**
   - 答：如果菜单是某个父菜单的子菜单，需要重新排顺序。比如原来顺序是 [1,2,3]，现在要在位置2插入新菜单，那顺序就变成 [1,新菜单,2,3]。

---

### 5.2 updateMenu - 更新菜单

---

### 方法名：updateMenu(菜单信息VO)

> 🎯 **一句话人话**：修改菜单的基本信息（名称、URL、启用状态等）

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| id | 要修改的菜单ID | "menu-uuid-xxx" |
| name | 新菜单名称 | "体检预约管理(新版)" |
| systemId | 所属系统ID | "system-uuid-xxx" |
| enable | 是否启用 | 1 或 0 |
| orderIndex | 排序序号 | 2 |

#### 📤 返回什么？（返回值）
- `ApiResponse` - 包含修改后的菜单ID

#### 🔗 谁会用这个方法？
- 前端菜单编辑页面 → MenuInfoApi → updateMenu()
- POST `/privilege/menu/update`

#### 📖 方法内部一步一步在做什么？

```
步骤1️⃣：校验必填参数
         ↓
         checkVo() 检查：
         - id 不能为空
         - name 不能为空
         - systemId 不能为空
         - enable 不能为空
         - orderIndex 不能为空

步骤2️⃣：复制数据 + 更新修改人/时间
         ↓
         BeanUtils.copyProperties(vo, privilegeMenuInfo)
         privilegeMenuInfo.setModifier(当前用户)
         privilegeMenuInfo.setModifytime(当前时间)

步骤3️⃣：保存更新
         ↓
         privilegeMenuInfoService.save(privilegeMenuInfo)
         注意：MyBatis-Plus会根据id自动判断是更新而非插入

步骤4️⃣：调整菜单排序
         ↓
         如果有父级菜单，调用 modifyOrder() 调整顺序

步骤5️⃣：返回成功
```

#### ⚠️ 异常处理

| 异常情况 | 处理方式 |
|---------|---------|
| 缺少id | 返回："缺少入参" |
| 缺少name | 返回："缺少入参" |
| 缺少systemId | 返回："缺少入参" |
| 缺少enable | 返回："缺少入参" |
| 缺少orderIndex | 返回："缺少入参" |

#### 🐛 小白易懵点

1. **createMenu 和 updateMenu 有什么区别？**
   - createMenu 多了"重复性校验"（URL重复、名称重复）
   - updateMenu 少了这些校验，因为通常只改名称而不改URL

2. **为什么要校验这些字段？**
   - 答：这些是菜单的核心属性，缺了任何一个都可能导致系统异常。

---

### 5.3 deleteMenu - 删除菜单

---

### 方法名：deleteMenu(菜单信息VO)

> 🎯 **一句话人话**：删除一个或多个菜单，如果是父菜单还会把子菜单一起删掉

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| ids | 要删除的菜单ID列表 | ["menu-1", "menu-2", "menu-3"] |

#### 📤 返回什么？（返回值）
- `ApiResponse` - 成功/失败信息

#### 🔗 谁会用这个方法？
- 前端菜单列表 → 勾选菜单 → 点击删除 → MenuInfoApi → deleteMenu()
- POST `/privilege/menu/deleteById`

#### 📖 方法内部一步一步在做什么？

```
步骤1️⃣：校验参数
         ↓
         ids 不能为空，否则返回失败

步骤2️⃣：遍历每个要删除的菜单
         ↓
         for (menuId : ids) {
             // 对每个菜单执行删除前检查
         }

步骤3️⃣：检查菜单是否已被删除
         ↓
         如果 deleteAt != null，说明已经删过了
         返回失败："该菜单已经被删除"

步骤4️⃣：查找并删除子菜单（递归）
         ↓
         调用 getChildrenMenus() 查所有子菜单
         对每个子菜单：
         - 设置 deleteAt = 当前时间（软删除）
         - 保存更新

步骤5️⃣：删除当前菜单本身
         ↓
         设置 deleteAt = 当前时间
         保存更新

步骤6️⃣：批量更新同父菜单下的排序
         ↓
         把剩余的同级菜单重新编号
         如：[1,2,3] 删除2后变成 [1,2]
```

#### 🏠 银行转账比喻（@Transactional）

```java
@Override
@Transactional
public ApiResponse deleteMenu(PrivilegeMenuInfoVo vo) {
    // 删除操作要么全部成功，要么全部回滚
    // 如果删除父菜单时子菜单删除失败，整个事务都会回滚
    // 不会出现"父菜单删了但子菜单还在"的情况
}
```

#### ⚠️ 异常处理

| 异常情况 | 处理方式 |
|---------|---------|
| ids为空 | 返回："入参不能为空" |
| 菜单已删除 | 返回："该菜单已经被删除" |
| 数据库异常 | @Transactional自动回滚 |

#### 🐛 小白易懵点

1. **什么是"软删除"？**
   - 答：不是真的从数据库删掉，而是设置 `deleteAt` 字段 = 当前时间。查询时排除 `deleteAt != null` 的记录，就相当于"删了"。

2. **为什么要删除子菜单？**
   - 答：如果删除了父菜单"体检中心"，但保留子菜单"预约挂号"，那"预约挂号"就没有父级了，会变成孤儿数据。所以删父必须删子。

3. **为什么要重新排序？**
   - 答：假设同级菜单顺序是 1,2,3,4。删掉第2个后，如果不做处理，剩下的顺序还是1,2,3，但实际上是1,3,4。重新排序后变成1,2,3，保持连续。

---

### 5.4 getMenuTree - 获取菜单树

---

### 方法名：getMenuTree(菜单查询VO)

> 🎯 **一句话人话**：根据系统ID，查询该系统下的所有菜单，并以树形结构返回

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| systemId | 系统ID（必填） | "system-uuid-xxx" |

#### 📤 返回什么？（返回值）
- `ApiResponse` - 包含树形结构的菜单列表

```json
{
  "status": "SUCCESS",
  "data": [
    {
      "id": "menu-1",
      "name": "体检中心",
      "parentId": null,
      "children": [
        {
          "id": "menu-2",
          "name": "体检预约",
          "parentId": "menu-1",
          "children": []
        }
      ]
    }
  ]
}
```

#### 🔗 谁会用这个方法？
- 前端菜单树组件渲染
- 前端下拉选择父菜单
- POST `/privilege/menu/getMenuTree`

#### 📖 方法内部一步一步在做什么？

```
步骤1️⃣：校验系统ID
         ↓
         systemId 不能为空
         为空 → 返回失败："系统id不能为空"

步骤2️⃣：复制数据（VO → DTO）
         ↓
         BeanUtils.copyProperties(vo, dto)

步骤3️⃣：查询该系统下所有菜单（扁平结构）
         ↓
         getMenuOrgTree(dto)
         返回：List<PrivilegeMenuInfoDto>（所有菜单，不分层级）

步骤4️⃣：筛选出顶级菜单
         ↓
         menus.stream()
              .filter(menu -> parentId == null)
              .collect(Collectors.toList())
         即：parentId 为空的那些菜单

步骤5️⃣：递归构建树形结构
         ↓
         buildTree(顶级菜单列表, 全部菜单列表)
         详细过程见第三章"菜单树构建原理"

步骤6️⃣：返回树形结构
```

#### ⚠️ 异常处理

| 异常情况 | 处理方式 |
|---------|---------|
| systemId为空 | 返回失败："系统id不能为空" |

#### 🐛 小白易懵点

1. **为什么要分两步：先查扁平，再构建树？**
   - 答：数据库查询是扁平的（一行一个菜单），没有天生的树结构。我们需要把所有菜单查出来，然后在Java代码里手动组装成树。

2. **children 为空数组和 children 为 null 有什么区别？**
   - 答：children 为空数组 `[]` 表示"我确认没有子菜单"。children 为 null 表示"还没查子菜单"。前端需要区分这两种情况。

---

### 5.5 queryMenusBySystemId - 查询菜单列表

---

### 方法名：queryMenusBySystemId(菜单查询VO)

> 🎯 **一句话人话**：根据系统ID和机构ID，查询该机构在此系统下能访问的菜单列表

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| systemId | 系统ID（可选） | "system-uuid-xxx" |
| name | 菜单名称（可选，模糊查询） | "体检" |
| pageVo | 分页信息 | {pageNum: 1, pageSize: 10} |

#### 📤 返回什么？（返回值）
- `ApiResponse` - 包含分页的菜单列表（扁平结构）

#### 🔗 谁会用这个方法？
- 前端菜单管理列表页面
- POST `/privilege/menu/queryMenusBySystemId`

#### 📖 方法内部一步一步在做什么？

```
步骤1️⃣：分页处理
         ↓
         PageHelper.startPage(pageNum, pageSize)
         告诉MyBatis后续查询需要分页

步骤2️⃣：查询菜单列表
         ↓
         getMenuOrgTree(dto) 或 getMenuOrgTree(dto)
         返回当前用户机构下该系统的菜单

步骤3️⃣：补充父级菜单名称
         ↓
         对每个菜单：
         - 如果有 parentId
         - 去查父级菜单的信息
         - 把父级菜单名称 setParentName()

步骤4️⃣：补充系统名称
         ↓
         对每个菜单：
         - 根据 systemId 查系统表
         - 把系统名称 setSystemName()

步骤5️⃣：返回分页结果
```

#### 🐛 小白易懵点

1. **为什么要在返回结果里补充 parentName 和 systemName？**
   - 答：数据库存的是ID（如 parent_id="xxx"），前端展示需要显示名称。一次性查出来比前端多次查询更高效。

---

### 5.6 enable - 启用/禁用菜单

---

### 方法名：enable(菜单VO)

> 🎯 **一句话人话**：把某个菜单开启或关闭

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| id | 菜单ID | "menu-uuid-xxx" |
| enable | 是否启用 | 1（启用）或 0（禁用） |

#### 📤 返回什么？（返回值）
- `ApiResponse` - 成功/失败

#### 🔗 谁会用这个方法？
- 前端菜单列表 → 开关按钮 → MenuInfoApi → enable()
- POST `/privilege/menu/enable`

#### 📖 方法内部一步一步在做什么？

```
步骤1️⃣：构建更新对象
         ↓
         PrivilegeMenuInfo menu = new PrivilegeMenuInfo()
         menu.setId(vo.getId())
         menu.setEnable(vo.getEnable())

步骤2️⃣：保存更新
         ↓
         privilegeMenuInfoService.save(menu)
         只更新 id 和 enable 两个字段

步骤3️⃣：返回成功
```

#### 🐛 小白易懵点

1. **为什么不传其他字段？**
   - 答：这是"快速操作"，只改启用状态，不影响其他信息。

2. **禁用菜单后，角色权限还在吗？**
   - 答：角色权限关联的是菜单ID，不会自动删除。但用户访问被禁用的菜单时，后台接口应该会返回"无权限"或"菜单已停用"。

---

### 5.7 reviseServices - 批量增删改菜单服务

---

### 方法名：reviseServices(菜单服务VO)

> 🎯 **一句话人话**：一次性完成菜单的服务接口的增、删、改操作

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| menuId | 菜单ID | "menu-uuid-xxx" |
| addservicesList | 要新增的服务列表 | [{serviceUrl: "/api/xxx", serviceName: "新增接口"}] |
| updateservicesList | 要修改的服务列表 | [{id: "service-1", serviceUrl: "/api/yyy"}] |
| deleteservicesList | 要删除的服务列表 | [{id: "service-2"}] |

#### 📤 返回什么？（返回值）
- `ApiResponse` - 成功/失败信息

#### 🔗 谁会用这个方法？
- 前端菜单服务配置页面
- POST `/privilege/menu/reviseServices`

#### 📖 方法内部一步一步在做什么？

```
步骤1️⃣：校验菜单ID
         ↓
         menuId 不能为空

步骤2️⃣：检查URL是否重复
         ↓
         checkRepeat() 合并新增+修改+删除的所有URL
         检查是否有重复URL
         有 → 返回失败

步骤3️⃣：处理删除
         ↓
         for (service : deleteservicesList) {
             service.setDeleteAt(当前时间)  // 软删除
             privilegeMenuServiceService.save(service)
         }

步骤4️⃣：查询现有服务（用于后续去重）
         ↓
         queryChildrenServicesMenus(dto)
         查该菜单下已有的服务

步骤5️⃣：处理新增
         ↓
         for (service : addservicesList) {
             // 检查是否和已有服务URL重复
             if (service.getUrl() 已在 existingServices 中) {
                 return 失败："接口路径重复"
             }
             // 创建新服务
             setMenuId(menuId)
             setCreator/modifier
             setEnable(1)
             save(service)
         }

步骤6️⃣：处理修改
         ↓
         for (service : updateservicesList) {
             // 检查是否和其他服务URL重复（排除自己）
             if (service.getUrl() 已在 existingServices 中 && id不同) {
                 return 失败："接口路径重复"
             }
             // 更新服务
             service.setModifier/modifytime
             save(service)
         }

步骤7️⃣：返回成功
```

#### ⚠️ 异常处理

| 异常情况 | 处理方式 |
|---------|---------|
| menuId为空 | 返回失败："菜单id不能为空" |
| URL重复 | 返回失败："提交的信息中存在接口路径重复" |
| 新增URL已存在 | 返回失败："接口路径重复" |
| 修改时URL冲突 | 返回失败："接口路径重复" |

#### 🐛 小白易懵点

1. **为什么要传入三个List（增、删、改）？**
   - 答：减少前后端交互次数。比如管理员一次性勾选了"新增3个、修改2个、删除1个"，一次请求全部搞定，而不是发3次请求。

2. **checkRepeat() 怎么判断重复？**
   - 答：把所有URL（新增的、修改的、删除的）放到一个List里，然后检查是否有重复元素。

3. **新增时为什么要和已有服务比较？**
   - 答：一个菜单下不能有两个URL相同的服务，否则权限判断会出问题。

---

### 5.8 queryServicesTree - 查询菜单服务树

---

### 方法名：queryServicesTree(菜单服务VO)

> 🎯 **一句话人话**：查询某个菜单下的服务列表，支持查看父子菜单结构

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| menuId | 菜单ID | "menu-uuid-xxx" |
| menuChrilrenId | 子级菜单ID（可选） | "child-menu-uuid" |

#### 📤 返回什么？（返回值）
- `ApiResponse` - 菜单树结构（带服务信息）

#### 🔗 谁会用这个方法？
- 前端查看菜单服务配置
- POST `/privilege/menu/queryServicesTree`

#### 📖 方法内部一步一步在做什么？

```
情况A：传了 menuChrilrenId（子菜单ID）
┌─────────────────────────────────────┐
步骤1️⃣：查询指定菜单
         ↓
         selectMenuInfoById(menuId)

步骤2️⃣：查询子级菜单
         ↓
         selectMenuInfoById(menuChrilrenId)

步骤3️⃣：组装父子关系
         ↓
         menuInfo.setChildren([menuChrilrenInfo])

步骤4️⃣：返回
         ↓
         return [menuInfo(含子菜单)]
└─────────────────────────────────────┘

情况B：只传了 menuId
┌─────────────────────────────────────┐
步骤1️⃣：查询指定菜单
         ↓
         selectMenuInfoById(menuId)

步骤2️⃣：判断 menuId 是父级还是子级
         ↓
         如果 parentId != null → 是子级菜单
         如果 parentId == null → 是父级菜单

情况B1：是子级菜单（menuId是子级）
         ↓
         查父级菜单
         查当前菜单（作为子级）
         组装：父菜单.setChildren([当前菜单])
         返回：[父菜单]

情况B2：是父级菜单（menuId是父级）
         ↓
         查所有子级菜单
         查父菜单
         父菜单.setChildren([子级们])
         返回：[父菜单]
└─────────────────────────────────────┘

情况C：什么都没传
┌─────────────────────────────────────┐
步骤1️⃣：查询该机构下所有菜单
         ↓
         queryServicesTree(dto)

步骤2️⃣：筛选顶级菜单
         ↓
         parentId == null 的菜单

步骤3️⃣：递归构建树
         ↓
         buildTree()

步骤4️⃣：返回完整菜单树
└─────────────────────────────────────┘
```

#### 🐛 小白易懵点

1. **menuId 和 menuChrilrenId 同时传是什么意思？**
   - 答：表示"我要看 menuId 这个父菜单，但特别关注它的某个子菜单 menuChrilrenId"。返回结果会把这个子菜单放到父菜单的 children 里。

---

### 5.9 queryChildrenMenus - 查询子级菜单

---

### 方法名：queryChildrenMenus(菜单服务VO)

> 🎯 **一句话人话**：查询某个菜单的所有直接子菜单

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| menuId | 父级菜单ID | "parent-menu-uuid" |

#### 📤 返回什么？（返回值）
- `ApiResponse` - 子级菜单列表

#### 🔗 谁会用这个方法？
- 前端展开菜单树
- POST `/privilege/menu/queryChildrenMenus`

#### 📖 方法内部一步一步在做什么？

```
步骤1️⃣：获取机构ID
         ↓
         orgId = UserUtils.getUser().getOrgId()

步骤2️⃣：构建查询条件
         ↓
         dto.setOrgId(orgId)
         dto.setParentId(menuId)

步骤3️⃣：查询子级菜单
         ↓
         getChildrenMenus(dto)
         只返回 parentId == menuId 的菜单

步骤4️⃣：返回
```

#### 🐛 小白易懵点

1. **为什么不返回 grandchildren（孙子菜单）？**
   - 答：这是"懒加载"。先查一层，如果前端需要，再继续查下一层。避免一次查询返回过多数据。

---

### 5.10 queryChildrenServicesMenus - 模糊查询菜单服务

---

### 方法名：queryChildrenServicesMenus(菜单服务VO)

> 🎯 **一句话人话**：根据菜单ID或关键字，模糊查询该菜单关联的服务接口

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| menuId | 菜单ID | "menu-uuid-xxx" |
| serviceKey | 关键字（URL或名称） | "appointment" |

#### 📤 返回什么？（返回值）
- `ApiResponse` - 服务列表

#### 📖 方法内部一步一步在做什么？

```
步骤1️⃣：复制数据
         ↓
         BeanUtils.copyProperties(vo, dto)

步骤2️⃣：查询服务
         ↓
         queryChildrenServicesMenus(dto)
         
         SQL条件：
         - delete_at is null
         - menu_id = menuId (如果传了)
         - (service_url like '%serviceKey%' OR service_name like '%serviceKey%') (如果传了serviceKey)

步骤3️⃣：返回
```

---

### 5.11 queryDataStatistics - 查询数据统计

---

### 方法名：queryDataStatistics(菜单服务VO)

> 🎯 **一句话人话**：统计当前机构下配置了多少菜单、多少接口

#### 📥 需要什么？（参数）
- 无需传参，从当前用户Session获取 orgId

#### 📤 返回什么？（返回值）

```json
{
  "systemMenuNum": 50,     // 系统菜单总数
  "authMenuNum": 30,        // 配置了接口的菜单数
  "authInterfaceNum": 150   // 接口总数
}
```

#### 🔗 谁会用这个方法？
- 前端数据看板
- POST `/privilege/menu/queryDataStatistics`

#### 📖 方法内部一步一步在做什么？

```
步骤1️⃣：获取机构ID
         ↓
         orgId = UserUtils.getUser().getOrgId()

步骤2️⃣：查询系统菜单总数
         ↓
         querySystemMenuNum(dto)
         统计：机构关联的菜单总数

步骤3️⃣：查询已配置接口的菜单数
         ↓
         queryauthMenuNum(dto)
         统计：机构关联的菜单中，有服务接口的菜单数

步骤4️⃣：查询接口总数
         ↓
         queryAuthInterfaceNum(dto)
         统计：机构关联菜单下的服务接口总数

步骤5️⃣：返回统计数据
```

#### 🐛 小白易懵点

1. **为什么要区分"菜单总数"和"已配置接口的菜单数"？**
   - 答：有些菜单只是目录（如"体检管理"），下面有子菜单但自己不带接口。只有带接口的菜单才能做权限控制。

---

## 6. PrivilegeMenuInfoServiceImpl 方法详解

> 🏠 这个类主要封装了菜单相关的数据库查询操作，是MenuInfoServiceImpl的"左膀右臂"

### 6.1 getMenuOrgTree - 查询机构菜单树

---

### 方法名：getMenuOrgTree(菜单DTO)

> 🎯 **一句话人话**：查询指定机构在指定系统下的所有菜单

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| systemId | 系统ID（可选） | "system-uuid-xxx" |

#### 📤 返回什么？（返回值）
- `List<PrivilegeMenuInfoDto>` - 菜单列表（扁平结构）

#### 📖 SQL 解读

```sql
SELECT * FROM privilege_menu_info
WHERE delete_at IS NULL
  AND system_id = #{systemId}
ORDER BY parent_id, order_index
```

---

### 6.2 queryInfo - 菜单重复性查询

---

### 方法名：queryInfo(菜单PO)

> 🎯 **一句话人话**：根据URL或名称，查询是否有重复菜单

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| url | 菜单URL（可选） | "/api/health" |
| name | 菜单名称（可选） | "体检预约" |

#### 📤 返回什么？（返回值）
- `List<PrivilegeMenuInfo>` - 匹配到的菜单列表

#### 📖 SQL 解读

```sql
SELECT * FROM privilege_menu_info
WHERE delete_at IS NULL
  AND (url = #{url} OR name = #{name})
ORDER BY parent_id, order_index
```

---

### 6.3 getChildrenMenus - 查询子级菜单

---

### 方法名：getChildrenMenus(菜单DTO)

> 🎯 **一句话人话**：查询指定父菜单ID下的所有直接子菜单

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| parentId | 父级菜单ID | "parent-menu-uuid" |
| orgId | 机构ID | "org-uuid-xxx" |

#### 📤 返回什么？（返回值）
- `List<PrivilegeMenuInfoDto>` - 子级菜单列表

#### 📖 SQL 解读

```sql
SELECT * FROM privilege_menu_info
WHERE id IN (
    SELECT m.id FROM privilege_menu_info m
    LEFT JOIN privilege_org_system o ON m.id = o.menu_id
    WHERE m.parent_id = #{parentId}
      AND o.org_id = #{orgId}
)
AND delete_at IS NULL
ORDER BY order_index
```

---

### 6.4 selectMenuInfoById - 根据ID查询菜单

---

### 方法名：selectMenuInfoById(id)

> 🎯 **一句话人话**：根据菜单ID获取菜单详情

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| id | 菜单ID | "menu-uuid-xxx" |

#### 📤 返回什么？（返回值）
- `PrivilegeMenuInfoDto` - 菜单详情（无则返回null）

---

### 6.5 querySystemMenuNum - 统计菜单总数

---

### 方法名：querySystemMenuNum(菜单DTO)

> 🎯 **一句话人话**：统计机构关联的菜单总数

#### 📤 返回什么？（返回值）
- `Integer` - 菜单数量

---

### 6.6 queryauthMenuNum - 统计已配置接口的菜单数

---

### 方法名：queryauthMenuNum(菜单DTO)

> 🎯 **一句话人话**：统计机构关联的菜单中，已配置接口权限的菜单数量

#### 📖 SQL 解读

```sql
SELECT count(1) FROM privilege_menu_info i
WHERE id IN (
    SELECT m.id FROM privilege_menu_info m
    LEFT JOIN privilege_org_system o ON m.id = o.menu_id
    WHERE o.org_id = #{orgId}
      AND m.delete_at IS NULL
      AND o.delete_at IS NULL
)
AND EXISTS (SELECT * FROM privilege_menu_service s WHERE i.id = s.menu_id)
```

---

### 6.7 modifyOrder - 调整菜单排序

---

### 方法名：modifyOrder(菜单VO, 菜单PO)

> 🎯 **一句话人话**：把菜单移动到指定位置，重新编排同级菜单的顺序

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| vo.orderIndex | 新位置（从1开始） | 2（移动到第2位） |
| vo.parentId | 父级菜单ID | "parent-menu-uuid" |
| vo.id | 要移动的菜单ID | "menu-to-move-uuid" |

#### 📖 方法内部一步一步在做什么？

```
步骤1️⃣：计算实际插入位置
         ↓
         addIndex = orderIndex - 1
         比如传 orderIndex=2，实际是第1位（从0开始）

步骤2️⃣：查询同级所有菜单
         ↓
         queryMenuOrder(dto)
         查 parentId 相同的所有菜单，按 orderIndex 排序

步骤3️⃣：从列表中移除要移动的菜单
         ↓
         childrenMenuList.removeIf(pinfo -> vo.getId().equals(pinfo.getId()))

步骤4️⃣：把菜单插入到新位置
         ↓
         childrenMenuList.add(addIndex, menuInfo)

步骤5️⃣：重新编号所有同级菜单
         ↓
         for (int i = 0; i < childrenMenuList.size(); i++) {
             childrenMenuList.get(i).setOrderIndex(i + 1);
             save(childrenMenuList.get(i));
         }

步骤6️⃣：返回
         ↓
         如果全部成功，返回 null
         如果失败，返回错误信息
```

#### 🐛 小白易懵点

1. **orderIndex 为什么减1？**
   - 答：用户看到的顺序是从1开始的，但Java List的索引是从0开始的。传2表示"插到第2位"，实际是 index=1。

2. **为什么要先把菜单从列表移除再插入？**
   - 答：如果是原地移动（比如从第3位移到第5位），不先移除的话会导致数据错位。

---

## 7. PrivilegeMenuServiceServiceImpl 方法详解

> 🏠 这个类主要封装了菜单服务（接口权限）的数据库查询操作

### 7.1 queryChildrenServicesMenus - 查询菜单的服务列表

---

### 方法名：queryChildrenServicesMenus(服务DTO)

> 🎯 **一句话人话**：查询指定菜单关联的所有服务接口

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| menuId | 菜单ID | "menu-uuid-xxx" |
| serviceKey | 搜索关键字（可选） | "appointment" |

#### 📤 返回什么？（返回值）
- `List<PrivilegeMenuService>` - 服务列表

#### 📖 SQL 解读

```sql
SELECT * FROM privilege_menu_service
WHERE delete_at IS NULL
  AND menu_id = #{menuId}
  AND (
      service_url LIKE '%' || #{serviceKey} || '%'
      OR service_name LIKE '%' || #{serviceKey} || '%'
  )
```

---

### 7.2 queryAuthInterfaceNum - 统计接口总数

---

### 方法名：queryAuthInterfaceNum(菜单DTO)

> 🎯 **一句话人话**：统计机构下所有菜单配置的接口总数

#### 📖 SQL 解读

```sql
SELECT count(DISTINCT s.id)
FROM privilege_menu_service s
LEFT JOIN privilege_menu_info i ON s.menu_id = i.id
LEFT JOIN privilege_org_system o ON i.id = o.menu_id
WHERE o.org_id = #{orgId}
  AND s.delete_at IS NULL
  AND i.delete_at IS NULL
  AND o.delete_at IS NULL
```

---

## 8. SysInfoServiceImpl 方法详解

> 🏠 这个类负责系统信息的管理，目前只有一个核心方法

### 8.1 querySysInfo - 查询系统列表

---

### 方法名：querySysInfo(系统VO)

> 🎯 **一句话人话**：分页查询所有系统信息

#### 📥 需要什么？（参数）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| pageVo.pageNum | 页码 | 1 |
| pageVo.pageSize | 每页条数 | 10 |

#### 📤 返回什么？（返回值）
- `ResultPage<PrivilegeSystemInfoDto>` - 分页后的系统列表

#### 🔗 谁会用这个方法？
- 前端系统管理页面
- POST `/privilege/sys/list`

#### 📖 方法内部一步一步在做什么？

```
步骤1️⃣：获取分页参数
         ↓
         pageVo = vo.getPageVo()
         pageNum = pageVo.getPageNum()
         pageSize = pageVo.getPageSize()

步骤2️⃣：启动分页
         ↓
         PageHelper.startPage(pageNum, pageSize)
         告诉PageHelper插件拦截后续SQL，添加LIMIT

步骤3️⃣：查询所有系统
         ↓
         privilegeSystemInfoService.selectAll()
         SELECT * FROM privilege_system_info WHERE delete_at IS NULL

步骤4️⃣：包装分页结果
         ↓
         PageInfo<PrivilegeSystemInfo> page = new PageInfo<>(list)
         ResultPage resultPage = this.createResultPage(page)

步骤5️⃣：返回
```

#### 🐛 小白易懵点

1. **PageHelper 是什么？**
   - 答：一个MyBatis分页插件。只要在查询前调用 `PageHelper.startPage()`，后续的查询就会自动加上分页。

2. **selectAll() 不是查全部吗？**
   - 答：在BaseServiceImpl里，selectAll()会被PageHelper拦截，实际只会查当前页的数据。PageHelper通过ThreadLocal传递分页参数。

---

## 9. 常见业务场景解析

### 场景1：管理员新建一个"体检预约"菜单

```
操作流程：
1. 管理员进入菜单管理页面
2. 点击"新增菜单"
3. 填写信息：
   - 菜单名称：体检预约管理
   - 所属系统：慢病管理系统
   - 父级菜单：体检中心（选择已有的父菜单）
   - URL：/api/health/appointment
   - 排序：2
4. 点击保存

后端执行：
createMenu() 
→ 检查URL不重复 ✓
→ 检查名称不重复 ✓
→ 保存菜单到 privilege_menu_info ✓
→ 建立机构-菜单关联 ✓
→ 调整同级菜单排序 ✓
→ 返回菜单ID

前端刷新页面 → 调用 getMenuTree() → 显示新菜单
```

### 场景2：给"体检预约"菜单配置接口权限

```
操作流程：
1. 管理员点击"体检预约"菜单
2. 进入服务配置页面
3. 添加服务：
   - 接口名称：创建预约
   - 接口URL：/api/health/appointment/create
4. 再添加服务：
   - 接口名称：取消预约
   - 接口URL：/api/health/appointment/cancel
5. 点击保存

后端执行：
reviseServices()
→ checkRepeat() 检查URL不重复 ✓
→ 遍历 addservicesList
  → 保存第一个服务 ✓
  → 保存第二个服务 ✓
→ 返回成功

这样配置后，只有角色分配了"体检预约"菜单权限，才能访问这两个接口
```

### 场景3：删除一个父菜单

```
操作流程：
1. 管理员勾选"体检中心"菜单
2. 点击"删除"
3. 系统提示"该菜单下有子菜单，确认删除？"
4. 管理员确认

后端执行：
deleteMenu()
→ 查询"体检中心"的子菜单：["体检预约", "体检报告"]
→ 删除"体检预约"（软删除）
→ 删除"体检报告"（软删除）
→ 删除"体检中心"（软删除）
→ 重新排序同级菜单
→ 提交事务（@Transactional保证原子性）

如果任何一步失败，整个事务回滚，不会出现"父删了子还在"的情况
```

### 场景4：查看数据统计

```
操作流程：
1. 管理员进入数据看板
2. 系统自动调用 queryDataStatistics()

后端返回：
{
  "systemMenuNum": 50,     // 共50个菜单
  "authMenuNum": 30,       // 其中30个配置了接口
  "authInterfaceNum": 150  // 共150个接口
}

用途：
- 系统管理员了解菜单配置情况
- 排查"为什么有些菜单没有权限控制"（可能是没配置接口）
```

---

## 📚 附录：API 接口速查表

| 接口 | 方法 | 说明 |
|------|------|------|
| POST `/privilege/menu/create` | createMenu | 创建菜单 |
| POST `/privilege/menu/update` | updateMenu | 更新菜单 |
| POST `/privilege/menu/deleteById` | deleteMenu | 删除菜单 |
| POST `/privilege/menu/getDetail` | getDetail | 获取菜单详情 |
| POST `/privilege/menu/queryMenusBySystemId` | queryMenusBySystemId | 查询菜单列表 |
| POST `/privilege/menu/getMenuTree` | getMenuTree | 获取菜单树 |
| POST `/privilege/menu/enable` | enable | 启用/禁用菜单 |
| POST `/privilege/menu/reviseServices` | reviseServices | 批量增删改服务 |
| POST `/privilege/menu/queryServicesTree` | queryServicesTree | 查询服务树 |
| POST `/privilege/menu/queryChildrenMenus` | queryChildrenMenus | 查询子级菜单 |
| POST `/privilege/menu/queryChildrenServicesMenus` | queryChildrenServicesMenus | 模糊查询服务 |
| POST `/privilege/menu/queryDataStatistics` | queryDataStatistics | 数据统计 |
| POST `/privilege/sys/list` | querySysInfo | 查询系统列表 |

---

## 🔗 相关文档链接

- [PICC人保健康权限管理系统 - 教程文档](./picc-mzmtb-user-教程文档.md)

---

📎 **延伸阅读**：
- [深度解析-角色管理](picc-mzmtb-user-深度解析第三章-角色管理.md) - 角色管理和菜单管理的配合使用
- [深度解析补充-辅助模块](picc-mzmtb-user-深度解析补充-辅助模块.md) - PrivilegeMenuInfoServiceImpl、PrivilegeMenuServiceServiceImpl辅助模块说明
- [API-Mapper-数据模型](picc-mzmtb-user-API-Mapper-数据模型.md) - 菜单相关API的详细接口说明

- [深度解析第二章](./picc-mzmtb-user-深度解析第二章.md)
- [深度解析第三章-角色管理](./picc-mzmtb-user-深度解析第三章-角色管理.md)
- [数据库ER图与表结构](./picc-mzmtb-user-数据库ER图与表结构.md)

---

> 📝 文档更新记录
> - v1.0 (2024-04-30): 初版完成，包含 MenuInfoServiceImpl、PrivilegeMenuInfoServiceImpl、PrivilegeMenuServiceServiceImpl、SysInfoServiceImpl 的完整解析
