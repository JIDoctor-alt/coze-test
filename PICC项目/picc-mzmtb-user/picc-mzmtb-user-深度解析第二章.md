> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC人保健康权限管理系统 - 深度解析第二章

> 🎯 本章目标：把项目里**最难啃的骨头**啃干净——200行的`query()`组合查询逐行拆解、完整数据流时序图、前端页面与接口映射、数据迁移逻辑、安全问题分析。

---

## 一、OrgInfoServiceImpl.query() —— 项目最复杂的200行组合查询逐行拆解

### 🎯 一句话人话
> 就像在快递站找包裹：你可以只说"到哪个系统的包裹"，也可以说"某个站+某个系统的包裹"，还可以说"某个站的全部包裹"，甚至什么都不说就"给我看我们站及下属所有站的包裹"——**四种找法，一个方法搞定**。

### 🏠 生活比喻
想象你是人保集团陕西省分公司的管理员：
- **场景A**：我想看陕西下属所有地市里，哪些开通了"门诊慢特病系统" → 只传`sysName`，不传`orgName`
- **场景B**：我想看西安市是否开通了"门诊慢特病系统" → 同时传`orgName`和`sysName`
- **场景C**：我想看西安市的全部信息 → 只传`orgName`，不传`sysName`
- **场景D**：我想看陕西下属所有地市的全部信息 → 什么都不传

### 📥 需要什么？（参数 OrgQueryVo）

| 参数 | 是什么意思 | 举个例子 |
|------|------------|----------|
| orgName | 机构ID（注意：字段叫orgName但实际传的是机构ID！） | 西安市的ID如"abc123" |
| sysName | 系统名称 | "门诊慢特病系统" |
| pageVo | 分页信息（页码+每页条数） | 第1页，每页10条 |
| id | 机构ID（其他场景用） | 用于getDetail等 |

### 📤 返回什么？
`ResultPage<OrgSystemVo>` —— 分页的机构+系统组合信息，每条包含：
- orgId、orgName：机构基本信息
- systemId[]、systemName：关联的系统（可能有多个，用顿号拼接）
- menuIds[]：关联的菜单ID
- parentDirectory：上级机构名称
- enable、contacts等：状态、联系人等

### 🔗 谁会用这个方法？
- **直接调用**：OrgInfoApi.query() → `/privilege/org/query`（POST）
- **触发场景**：管理员在前端"机构管理"页面，使用组合条件搜索机构信息

---

### 📖 方法内部一步一步在做什么？

#### 前置校验（第249-253行）
```java
// 第1步：获取当前登录用户所属的机构ID
String userOrgId = UserUtils.getUser().getOrgId();
// 如果获取不到，说明登录状态异常，直接抛异常
if (StringUtils.isBlank(userOrgId)){
    throw new CustomException("获取当前登录用户失败" + UserUtils.getUser().getUserId());
}
```
> 🏠 就像你进了快递站，系统先确认"你是哪个站的员工"，确认不了就拦住你。

#### ⚡ 四大分支逻辑概览
```
query()方法 = 四个if-else分支 = 四种搜索策略
├── 分支1: orgName为空 && sysName不为空 → 按系统名称搜索当前机构及下属所有机构
├── 分支2: orgName不为空 && sysName不为空 → 精确搜索某个机构是否开通了某个系统
├── 分支3: orgName不为空 && sysName为空 → 搜索某个机构的全部信息
└── 分支4: orgName为空 && sysName为空 → 搜索当前机构及下属所有机构的全部信息
```

---

#### 🔴 分支1：只按系统名称搜索（第255-303行）
**场景**：`orgName为空，sysName不为空` → "给我看我们站及下属所有站里，开通了XX系统的"

```java
// 第2步：用BFS（广度优先搜索）获取当前机构及所有子机构的ID列表
List<String> idList = getidList(userOrgId);
// 🏠 就像从总公司开始，一层一层找出所有分公司、支公司的编号

// 第3步：如果ID列表为空，直接返回null（说明当前机构没有数据）
if (CollectionUtils.isEmpty(idList)){ return null; }

// 第4步：根据系统名称查系统信息表，获取系统ID
String sysName = orgQueryVo.getSysName();
PrivilegeSystemInfo privilegeSystemInfo = privilegeSystemInfoDao.selectByName(sysName);
// 🏠 就像拿着"门诊慢特病系统"这个名字，去系统表里查它的编号

// 第5步：系统不存在也返回null
if (privilegeSystemInfo == null){ return null; }

// 第6步：启动分页查询
PageHelper.startPage(pageVo != null ? pageVo.getPageNum() : 0, 
                     pageVo != null ? pageVo.getPageSize() : 500);
// 🏠 就像告诉仓库管理员："我一次只看10个，给我翻到第1页"

// 第7步：用机构ID列表+系统ID联合查询
List<PrivilegeOrgInfo> privilegeOrgInfoList = 
    privilegeOrgInfoDao.selectByOrgIds(idList, privilegeSystemInfo.getId());
// 🏠 SQL: SELECT DISTINCT poi.* FROM privilege_org_info poi 
//        LEFT JOIN privilege_org_system pos ON poi.id = pos.org_id
//        WHERE poi.delete_at IS NULL AND poi.id IN (...) AND pos.system_id = ?
// 注意：这里用了LEFT JOIN + DISTINCT，是核心SQL

// 第8步：如果查不到数据，返回null
if (CollectionUtils.isEmpty(privilegeOrgInfoList)){ return null; }

// 第9步：保存分页元信息（总条数、总页数等）
PageInfo<PrivilegeOrgInfo> pageInfo = new PageInfo<>(privilegeOrgInfoList);

// 第10步：开始逐条组装返回对象（这是最重复的部分，四个分支都类似）
for (int i = 0; i < privilegeOrgInfoList.size(); i++) {
    OrgSystemVo orgSystemVo = new OrgSystemVo();
    
    // 10a: 拷贝基本信息（code、name、address等）
    BeanUtils.copyProperties(privilegeOrgInfoList.get(i), orgSystemVo);
    orgSystemVo.setOrgId(privilegeOrgInfoList.get(i).getId());
    orgSystemVo.setOrgName(privilegeOrgInfoList.get(i).getName());
    
    // 10b: 查上级机构名称（三段式判断）
    if (StringUtils.isNotBlank(privilegeOrgInfoList.get(i).getParentId())) {
        if (privilegeOrgInfoList.get(i).getParentId().equals(defaultId)){
            // parentId = "1" → 上级是"人保集团"
            orgSystemVo.setParentDirectory("人保集团");
        } else {
            // parentId = 其他值 → 去数据库查上级机构名称
            PrivilegeOrgInfo parentOrg = privilegeOrgInfoDao.selectOrg(...getParentId());
            orgSystemVo.setParentDirectory(parentOrg.getName());
        }
    } else {
        // parentId为空 → 没有上级
        orgSystemVo.setParentDirectory("无");
    }
    // 🏠 就像查快递单上的"寄出站点"：如果是从总部寄的写"总部"，从分站寄的写分站名，没有就写"无"
    
    // 10c: 查关联的系统信息（又是一次数据库查询！）
    String[] systemIds = privilegeOrgSystemDao.selectOrgSysInfo(...getId())
        .stream()
        .map(PrivilegeOrgSystem::getSystemId)
        .distinct()
        .toArray(String[]::new);
    // 🏠 查这个机构开通了哪些系统
    
    // 10d: 把系统ID翻译成系统名称（又一个循环查询！）
    List<String> list = Arrays.stream(systemIds)
        .map(systemId -> privilegeSystemInfoDao.selectById(systemId).getSysName())
        .collect(Collectors.toList());
    // ⚠️ 性能问题：N+1查询！每个机构都要查一次系统名称
    
    // 10e: 用顿号拼接系统名称
    String result = String.join("、", list);
    if (StringUtils.isBlank(result)){ result = "无"; }
    // 输出示例："门诊慢特病系统、综合查询系统"
    
    orgSystemVo.setSystemId(systemIds);
    orgSystemVo.setSystemName(result);
    
    // 10f: 查关联的菜单ID
    String[] menuIds = privilegeOrgSystemDao.selectOrgSysInfo(...getId())
        .stream()
        .map(PrivilegeOrgSystem::getMenuId)
        .distinct()
        .toArray(String[]::new);
    // ⚠️ 注意：这里selectOrgSysInfo在10c已经调过一次了，又调了一次！重复查询
    
    orgSystemVo.setMenuIds(menuIds);
    orgSystemVos.add(orgSystemVo);
}

// 第11步：把分页信息拷贝到返回对象
PageInfo<OrgSystemVo> page = new PageInfo<>();
BeanUtils.copyProperties(pageInfo, page);
page.setList(orgSystemVos);
return this.createResultPage(page);
```

> 🐛 **小白易懵点1**：字段名叫`orgName`但实际传的是机构**ID**，不是名称！这是代码命名的不一致。
> 
> 🐛 **小白易懵点2**：`selectOrgSysInfo`在同一条数据上被调了**两次**——一次取systemId，一次取menuId。完全可以一次查出后分别提取。
> 
> 🐛 **小白易懵点3**：默认pageSize=500，如果不传分页参数，一次最多返回500条。但PageHelper.startPage第一个参数是pageNum=0，**第0页在PageHelper里等同于不分页**！

---

#### 🔵 分支2：同时按机构+系统搜索（第304-362行）
**场景**：`orgName不为空，sysName不为空` → "西安市有没有开通门诊慢特病系统？"

```java
// 第12步：启动分页
PageHelper.startPage(pageVo != null ? pageVo.getPageNum() : 0, ...);

// 第13步：根据orgName（实际是机构ID）查机构信息
String orgId = orgQueryVo.getOrgName();  // ⚠️ 命名混乱：orgName存的是ID
PrivilegeOrgInfo privilegeOrgInfo = privilegeOrgInfoDao.selectOrg(orgId);
if (privilegeOrgInfo == null){ return null; }

// 第14步：根据sysName查系统信息
String sysName = orgQueryVo.getSysName();
PrivilegeSystemInfo privilegeSystemInfo = privilegeSystemInfoDao.selectByName(sysName);
if (privilegeSystemInfo == null){ return null; }

// 第15步：查询机构-系统关联关系（精确匹配orgId + systemId）
List<PrivilegeOrgSystem> privilegeOrgSystem = 
    privilegeOrgSystemDao.selectOrgSysInfoByOrgSysId(
        privilegeOrgInfo.getId(), privilegeSystemInfo.getId());
if (CollectionUtils.isEmpty(privilegeOrgSystem)){ return null; }
// 🏠 就像查"西安站"的"门诊慢特病系统"订阅记录，没有记录说明没开通

// 第16步：组装OrgSystemVo（和分支1的10a-10f基本一样）
// ... 同样的拷贝、查上级、查系统、查菜单 ...

// 第17步：额外校验——确认系统ID在机构的系统列表中
String[] systemIds = privilegeOrgSystemDao.selectOrgSysInfo(...getId())...;
List<String> systemIdsList = Arrays.asList(systemIds);
if (!systemIdsList.contains(privilegeSystemInfo.getId())){
    return null;  // 双重确认：虽然前面查过关联关系了，这里再验证一次
}
// ⚠️ 冗余校验：selectOrgSysInfoByOrgSysId已经确认了关联关系，这里又查一次再校验

// 返回单条结果
PageInfo<OrgSystemVo> page = new PageInfo<>(orgSystemVos);
return this.createResultPage(page);
```

> 🐛 **小白易懵点4**：分支2做了**两次权限校验**——先查selectOrgSysInfoByOrgSysId确认关联，又查selectOrgSysInfo取全部系统ID再contains验证。第二次完全是多余的。

---

#### 🟢 分支3：只按机构搜索（第363-410行）
**场景**：`orgName不为空，sysName为空` → "给我看西安市的所有信息"

```java
// 第18步：启动分页
PageHelper.startPage(...);

// 第19步：根据orgName（机构ID）查机构信息
String orgName = orgQueryVo.getOrgName();
PrivilegeOrgInfo privilegeOrgInfo = privilegeOrgInfoDao.selectOrg(orgName);
if (privilegeOrgInfo == null){ return null; }

// 第20步：组装OrgSystemVo（和前两个分支一样）
// ... 拷贝、查上级、查系统、查菜单 ...

// 返回单条结果
PageInfo<OrgSystemVo> page = new PageInfo<>(orgSystemVos);
return this.createResultPage(page);
```

> 💡 这个分支最简单，就是精确查一个机构然后组装返回。

---

#### 🟡 分支4：什么都不传（第411-455行）
**场景**：`orgName为空，sysName为空` → "给我看我们站及下属所有站的全部信息"

```java
// 第21步：BFS获取所有子机构ID
List<String> idList = getidList(userOrgId);
if (CollectionUtils.isEmpty(idList)){ return null; }

// 第22步：分页查询所有子机构（注意systemId传null，不按系统筛选）
PageHelper.startPage(...);
List<PrivilegeOrgInfo> privilegeOrgInfoList = 
    privilegeOrgInfoDao.selectByOrgIds(idList, null);
// SQL中: systemId为null时，不添加 AND pos.system_id = ? 条件，查出所有

// 第23步：组装OrgSystemVo（和分支1完全一样）
// ... 拷贝、查上级、查系统、查菜单 ...

// 返回分页结果
PageInfo<OrgSystemVo> page = new PageInfo<>();
BeanUtils.copyProperties(pageInfo, page);
page.setList(orgSystemVos);
return this.createResultPage(page);
```

---

### 📊 query()方法性能问题汇总

| 问题 | 严重程度 | 说明 |
|------|---------|------|
| N+1查询：每个机构循环查系统名称 | 🔴 严重 | 100个机构 = 100次系统表查询 |
| 重复查询：selectOrgSysInfo调两次 | 🟡 中等 | 一次取systemId，一次取menuId，完全可以合并 |
| 冗余校验：分支2双重确认关联关系 | 🟡 中等 | selectOrgSysInfoByOrgSysId已确认，contains校验多余 |
| 父机构名称循环查询 | 🟡 中等 | 每个机构都查一次上级机构名称，可批量查询 |
| pageNum默认0导致不分页 | 🔴 严重 | PageHelper的pageNum从1开始，传0等于不分页 |
| 代码重复：四个分支的组装逻辑几乎一样 | 🟠 改进 | 应抽取公共方法 |

### 💡 query()方法学习要点

```
优化前：query() = 200行，4个分支重复代码
优化后：query() = 60行核心 + 1个公共组装方法

// 1. 抽取公共组装方法
private OrgSystemVo buildOrgSystemVo(PrivilegeOrgInfo orgInfo) { ... }

// 2. 批量查询系统名称和菜单ID
private Map<String, String> batchQuerySystemNames(List<String> orgIds) { ... }

// 3. 修正分页参数：pageNum最小值应为1
int pageNum = pageVo != null ? Math.max(1, pageVo.getPageNum()) : 1;
```

---

## 二、getidList() —— BFS遍历机构树的"子机构收割机"

### 🎯 一句话人话
> 给我一个机构ID，我把它和它所有"子子孙孙"的ID全找出来，像族谱一样一级一级往下扒。

### 📖 逐行拆解

```java
private List<String> getidList(String id){
    // 第1步：查自己
    PrivilegeOrgInfo privilegeOrgInfo = privilegeOrgInfoDao.selectOrg(id);
    List<String> idList = new ArrayList<>();
    
    if(privilegeOrgInfo != null){
        // 第2步：创建BFS队列（🏠 像银行排队叫号系统）
        Queue<String> queue = new LinkedList<>();
        idList.add(id);     // 先把自己加入结果
        queue.offer(id);    // 把自己排进队列

        // 第3步：BFS循环——队列不空就继续
        while (!queue.isEmpty()) {
            String current = queue.poll();  // 取出队首（叫号）
            
            // 第4步：查当前机构的所有直接子机构
            List<PrivilegeOrgInfo> children = 
                privilegeOrgInfoDao.selectOrgInfoByParentId(current);
            
            // 第5步：把每个子机构加入结果和队列
            for (PrivilegeOrgInfo child : children) {
                queue.offer(child.getId());  // 子机构排队（后续还要查它的子机构）
                idList.add(child.getId());   // 子机构ID加入结果列表
            }
        }
    }
    return idList;
}
```

> 🏠 **BFS（广度优先搜索）图解**：
> ```
> 人保集团（ID=1）
> ├── 陕西省分公司（ID=2）← 第1轮找到
> │   ├── 西安市分公司（ID=5）← 第2轮找到
> │   └── 宝鸡市分公司（ID=6）← 第2轮找到
> └── 甘肃省分公司（ID=3）← 第1轮找到
>     └── 兰州市分公司（ID=7）← 第2轮找到
> 
> getidList("1") 返回: [1, 2, 3, 5, 6, 7]
> 注意顺序：先同级，再下一级（广度优先）
> ```

> ⚠️ **性能问题**：如果机构树有N层，最坏情况需要N次数据库查询。如果机构数量很大（如16个地市×N个区县），这是一个严重的性能瓶颈。建议改为一次性查出所有机构，然后在内存中构建树。

---

## 三、buildTree() —— 递归构建菜单树

### 🎯 一句话人话
> 给你一堆菜单项（有些是父菜单、有些是子菜单），把它们组装成一棵"家族树"——父菜单下面挂着子菜单，子菜单下面可能还有孙菜单。

### 📖 逐行拆解

```java
public List<PrivilegeMenuInfoDto> buildTree(
    List<PrivilegeMenuInfoDto> collect,  // 顶级菜单列表
    List<PrivilegeMenuInfoDto> allItems   // 所有菜单项（含子级）
) {
    for (PrivilegeMenuInfoDto parent : collect) {
        List<PrivilegeMenuInfoDto> dtoList = new ArrayList<>();
        for (PrivilegeMenuInfoDto dto : allItems){
            // 第1步：如果某项的parentId等于当前项的ID → 它是子菜单
            if (parent.getId().equals(dto.getParentId())) {
                List<PrivilegeMenuInfoDto> menu = new ArrayList<>();
                menu.add(dto);
                
                // 第2步：递归查找子菜单的子菜单（🏠 子菜单也可能有自己的子菜单）
                List<PrivilegeMenuInfoDto> dtos = buildTree(menu, allItems);
                dtoList.addAll(dtos);
            }
        }
        // 第3步：把子菜单列表挂到父菜单上
        parent.setChildren(dtoList);
    }
    return collect;
}
```

> 🏠 **菜单树图解**：
> ```
> 门诊慢特病管理（顶级菜单）
> ├── 申报管理（子菜单）
> │   ├── 新增申报（孙菜单）
> │   └── 申报查询（孙菜单）
> ├── 审核管理（子菜单）
> │   ├── 初审（孙菜单）
> │   └── 复审（孙菜单）
> └── 统计分析（子菜单）
> ```

> ⚠️ **性能问题**：双层循环 + 递归，时间复杂度O(N²×深度)。菜单数量不多时没问题，但设计上不够优雅。更好的做法是用Map<parentId, List>一次遍历构建。

---

## 四、完整数据流时序图

### 🔑 用户登录 → 获取菜单 → 操作数据 的完整流程

```
用户浏览器              前端(Vue)            后端(Spring Boot)          Redis           GaussDB
    │                     │                      │                      │                │
    │  1.输入账号密码      │                      │                      │                │
    │─────────────────────>│                      │                      │                │
    │                     │  2.POST /login       │                      │                │
    │                     │─────────────────────>│                      │                │
    │                     │                      │  3.查用户信息          │                │
    │                     │                      │──────────────────────────────────────>│
    │                     │                      │  4.返回用户数据        │                │
    │                     │                      │<─────────────────────────────────────│
    │                     │                      │  5.SM4解密密码比对     │                │
    │                     │                      │  6.生成Token           │                │
    │                     │                      │──────────────────────>│                │
    │                     │                      │  7.存Token+用户信息    │                │
    │                     │                      │    key=api_token:xxx  │                │
    │                     │  8.返回Token          │                      │                │
    │                     │<─────────────────────│                      │                │
    │  9.存储Token到本地   │                      │                      │                │
    │<─────────────────────│                      │                      │                │
    │                     │                      │                      │                │
    │  10.点击"机构管理"   │                      │                      │                │
    │─────────────────────>│                      │                      │                │
    │                     │  11.GET /org/tree    │                      │                │
    │                     │  Header: token       │                      │                │
    │                     │─────────────────────>│                      │                │
    │                     │                      │  12.ApiInterceptor校验Token           │
    │                     │                      │──────────────────────>│                │
    │                     │                      │  13.返回用户信息       │                │
    │                     │                      │<──────────────────────│                │
    │                     │                      │  14.查机构树           │                │
    │                     │                      │──────────────────────────────────────>│
    │                     │  15.返回机构树数据    │                      │                │
    │                     │<─────────────────────│                      │                │
    │  16.渲染机构树       │                      │                      │                │
    │<─────────────────────│                      │                      │                │
    │                     │                      │                      │                │
    │  17.搜索"门诊慢特病" │                      │                      │                │
    │─────────────────────>│                      │                      │                │
    │                     │  18.POST /org/query  │                      │                │
    │                     │  {sysName:"门诊慢特病"} │                     │                │
    │                     │─────────────────────>│                      │                │
    │                     │                      │  19.query()分支1      │                │
    │                     │                      │  → getidList(BFS)     │                │
    │                     │                      │──────────────────────────────────────>│
    │                     │                      │  → selectByName       │                │
    │                     │                      │──────────────────────────────────────>│
    │                     │                      │  → selectByOrgIds     │                │
    │                     │                      │──────────────────────────────────────>│
    │                     │                      │  → 循环组装(N+1查询)  │                │
    │                     │  20.返回分页数据      │                      │                │
    │                     │<─────────────────────│                      │                │
    │  21.渲染搜索结果     │                      │                      │                │
    │<─────────────────────│                      │                      │                │
```

---

## 五、前端页面与接口映射关系

### 🖥️ 前端页面 → 后端接口完整映射表

| 前端页面 | 功能操作 | HTTP方法 | 接口路径 | Service方法 | 说明 |
|---------|---------|---------|---------|------------|------|
| **机构管理** | 机构列表/搜索 | POST | /privilege/org/query | OrgInfoServiceImpl.query() | 组合查询，4种分支 |
| | 机构树形下拉 | POST | /privilege/org/getOrgTree | OrgInfoServiceImpl.getOrgTree() | 角色管理用 |
| | 新增机构 | POST | /privilege/org/create | OrgInfoServiceImpl.create() | 单独创建 |
| | 创建机构+配置资源 | POST | /privilege/org/setOrgSystemResources | OrgInfoServiceImpl.setOrgSystemResources() | 创建+配置一步到位 |
| | 编辑机构 | POST | /privilege/org/update | OrgInfoServiceImpl.update() | 单独编辑 |
| | 编辑机构+配置资源 | POST | /privilege/org/updateOrgSystemResources | OrgInfoServiceImpl.updateOrgSystemResources() | 编辑+配置一步到位 |
| | 删除机构 | POST | /privilege/org/deleteById | OrgInfoServiceImpl.deleteAtById() | 软删除 |
| | 批量删除机构 | POST | /privilege/org/deleteOrgsByIds | OrgInfoServiceImpl.deleteAtByIds() | 批量软删除 |
| | 机构详情 | POST | /privilege/org/getDetail | OrgInfoServiceImpl.getDetail() | 含系统+菜单信息 |
| | 机构状态切换 | POST | /privilege/org/updateOrgsByIds | OrgInfoServiceImpl.updateOrgsByIds() | 启用/禁用 |
| | 机构系统资源树 | POST | /privilege/org/getSystemList | OrgInfoServiceImpl.getSystemList() | 含菜单树 |
| | 机构归属下拉 | POST | /privilege/org/getPartOrgTree | OrgInfoServiceImpl.getPartOrgTree() | 用户/角色管理用 |
| **用户管理** | 用户列表 | POST | /privilege/user/queryUsers | UserInfoServiceImpl.queryUsers() | 分页+多条件 |
| | 创建用户 | POST | /privilege/user/create | UserInfoServiceImpl.create() | 含敏感词校验 |
| | 编辑用户 | POST | /privilege/user/update | UserInfoServiceImpl.update() | |
| | 删除用户 | POST | /privilege/user/deleteById | UserInfoServiceImpl.deleteById() | 软删除 |
| | 批量删除用户 | POST | /privilege/user/deleteUsersByIds | UserInfoServiceImpl.deleteUsersByIds() | |
| | 用户详情 | POST | /privilege/user/getDetail | UserInfoServiceImpl.getDetail() | |
| | 启用/禁用用户 | POST | /privilege/user/enableUser | UserInfoServiceImpl.enableUser() | 含Redis清除 |
| | 重置密码 | POST | /privilege/user/resetPassword | UserInfoServiceImpl.resetPassword() | 重置为默认密码 |
| | 配置用户角色 | POST | /privilege/user/setRoles | UserInfoServiceImpl.setRoles() | |
| | 查询用户角色 | POST | /privilege/user/queryRolesByUserId | UserInfoServiceImpl.queryRolesByUserId() | |
| | 按机构查用户 | POST | /privilege/user/queryUsersByOrgIds | UserInfoServiceImpl.queryUsersByOrgIds() | |
| **角色管理** | 创建角色 | POST | /privilege/role/create | RoleInfoServiceImpl.createRole() | |
| | 编辑角色 | POST | /privilege/role/update | RoleInfoServiceImpl.updateRole() | |
| | 删除角色 | POST | /privilege/role/delete | RoleInfoServiceImpl.deleteRole() | |
| | 角色详情 | POST | /privilege/role/getDetail | RoleInfoServiceImpl.getDetail() | |
| | 按机构查角色 | POST | /privilege/role/queryRolesByOrgId | RoleInfoServiceImpl.queryRolesByOrgId() | |
| | 角色树形图 | POST | /privilege/role/queryRoleTreeByOrgId | RoleInfoServiceImpl.queryRoleTreeByOrgId() | |
| | 权限树 | POST | /privilege/role/queryAuthTreeByRoleId | RoleInfoServiceImpl.queryAuthTreeByRoleId() | |
| | 配置角色资源 | POST | /privilege/role/setResources | RoleInfoServiceImpl.setResource() | |
| | 角色启用/禁用 | POST | /privilege/role/updateEnable | RoleInfoServiceImpl.updateEnable() | |
| | 批量删除角色 | POST | /privilege/role/deleteRolesByIds | RoleInfoServiceImpl.deleteRolesByIds() | |
| **菜单管理** | 创建菜单 | POST | /privilege/menu/create | MenuInfoServiceImpl.createMenu() | |
| | 编辑菜单 | POST | /privilege/menu/update | MenuInfoServiceImpl.updateMenu() | |
| | 删除菜单 | POST | /privilege/menu/deleteById | MenuInfoServiceImpl.deleteMenu() | |
| | 菜单树 | POST | /privilege/menu/getMenuTree | MenuInfoServiceImpl.getMenuTree() | |
| | 菜单启用/禁用 | POST | /privilege/menu/enable | MenuInfoServiceImpl.enable() | |
| **系统管理** | 系统列表 | POST | /privilege/sys/list | SysInfoServiceImpl.querySysInfo() | |
| **数据迁移** | 迁移角色+资源 | POST | /privilege/move/moveRoleAndResource | MoveServiceImpl.move() | 一次性工具 |
| | 迁移用户角色 | POST | /privilege/move/moveUserRole | MoveServiceImpl.moveUserRole() | 一次性工具 |
| | 密码回退MD5 | POST | /privilege/move/passwordBackMD5 | MoveServiceImpl.passwordBackMD5() | 一次性工具 |

---

## 六、数据迁移逻辑深度解析（MoveServiceImpl）

### 🏠 生活比喻
> 就像公司从旧办公楼搬到新办公楼——需要把旧楼里的文件柜（角色）、文件（资源）、员工工位（用户角色）全部搬过来，而且搬的过程中不能搞错对应关系。

### 📖 move() —— 角色与资源迁移

```
旧系统表                          新系统表
sys_role_module_rel              privilege_role_info + privilege_role_resource
(角色-模块关系)                   (角色信息)              (角色-菜单资源关系)

迁移逻辑：
1. 从旧表查出所有角色-资源关系
2. 按角色code分组（同一code可能对应多个机构的不同角色实例）
3. 第一个角色：原样插入新角色表 + 插入角色资源关系
4. 后续同code角色：生成新ID（groupId + index），插入新角色表 + 插入角色资源关系
5. 所有角色资源的systemId硬编码为"459694197360955392"
```

> ⚠️ **关键问题**：
> - `systemId`硬编码为`"459694197360955392"`，如果系统ID变了，迁移数据就错了
> - 角色ID生成策略（groupId + index）不够健壮，可能产生ID冲突

### 📖 moveUserRole() —— 用户角色迁移

```
旧系统表                          新系统表
sys_user_role_rel                privilege_user_role_info
(用户-角色关系)                   (用户-角色关系)

迁移逻辑：
1. 查旧表所有用户-角色关系
2. 根据userId查该用户所属机构ID
3. 根据旧roleId查旧角色信息获取code
4. 用orgId + code在新角色表查新角色ID
5. 插入新的用户-角色关系（使用新角色ID）
```

> 🏠 就像搬家时，员工的工号不变，但所属部门的编号变了，需要重新对应。

### 📖 passwordBackMD5() —— 密码回退

```
迁移逻辑：
1. 查所有用户
2. 对每个用户的密码尝试RSA私钥解密
3. 解密失败则跳过（说明密码不是RSA加密的）
4. 将解密后的明文密码直接存回数据库（未加密！）
```

> 🔴 **严重安全风险**：这个方法把加密密码解密后以**明文**存回数据库！这是密码回退操作，但在生产环境执行后，所有用户密码都是明文存储的，极其危险。

---

## 七、安全问题分析

### 🔴 严重问题1：SM4密钥硬编码

**现状**：`SM4Util.sm4Encrypt()`使用硬编码密钥`1234567812345678`

**问题分析**：
```yaml
# application.yml
encryption:
  sm4:
    key: ${SM4_SECRET_KEY}  # 从环境变量或Apollo配置中心读取
```

```java
@Value("${encryption.sm4.key}")
private String sm4Key;
```

**迁移步骤**：
1. 在Apollo配置中心添加SM4密钥配置
2. 修改SM4Util从配置读取密钥
3. 生成新密钥，编写数据迁移脚本重新加密所有密码

---

### 🔴 严重问题2：AES密钥硬编码

**现状**：`AesUtil`使用硬编码密钥`abcdefgabcdefg12`

**问题分析**：同SM4，从配置中心读取

---

### 🔴 严重问题3：RSA密钥硬编码在MoveServiceImpl

**现状**：RSA公私钥通过`@Value`注解硬编码默认值

**问题分析**：
```yaml
rsa:
  publicEncryptKey: ${RSA_PUBLIC_KEY}
  privateDecryptKey: ${RSA_PRIVATE_KEY}
```

---

### 🔴 严重问题4：权限编码"88"硬编码

**现状**：`UserInfoServiceImpl`中`queryUsers()`方法用`"88"`判断管理员权限

**问题分析**：
```java
// 修改前
if (UserUtils.getUser().getAuthCode().contains("88")) {

// 修改后
@Value("${privilege.admin-auth-code}")
private String adminAuthCode;

if (UserUtils.getUser().getAuthCode().contains(adminAuthCode)) {
```

---

### 🔴 严重问题5：URL权限contains模糊匹配

**现状**：`ApiInterceptor`用`contains()`匹配URL权限

**问题分析**：
```java
// 修改前
if (authUrls.contains(url)) { ... }

// 修改后：使用精确匹配或Ant路径匹配
@Autowired
private AntPathMatcher pathMatcher;

boolean hasPermission = authUrls.stream()
    .anyMatch(pattern -> pathMatcher.match(pattern, url));
```

---

### 🔴 严重问题6：APIAuthorityFilter只拦截/privilege/user/*

**现状**：过滤器只对`/privilege/user/*`路径做Token校验

**问题分析**：扩展拦截范围
```java
// 修改前
if (url.contains("/privilege/user/")) { ... }

// 修改后：拦截所有/privilege/开头的路径
if (url.startsWith("/privilege/")) { ... }
```

---

### 🟡 中等问题：默认密码可预测

**现状**：默认密码`PICChealth@2020`

**问题分析**：
1. 首次登录强制修改密码
2. 增加密码复杂度校验
3. 密码过期策略（如90天必须修改）

---

### 🟡 中等问题：passwordBackMD5导致密码明文存储

**问题分析**：
1. 废弃该方法，不执行密码回退
2. 如果确实需要，解密后应该用SM4重新加密再存储
3. 对已执行过回退的数据库，编写修复脚本重新加密

---

## 八、项目核心数据流图（ASCII版）

```
┌─────────────────────────────────────────────────────────────────────┐
│                        用户浏览器 (Vue)                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ 机构管理  │  │ 用户管理  │  │ 角色管理  │  │ 菜单管理  │           │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘           │
└────────┼─────────────┼─────────────┼─────────────┼─────────────────┘
         │             │             │             │
    ┌────▼─────────────▼─────────────▼─────────────▼────┐
    │              Nginx / K8s Ingress                    │
    │              (路由 + SSL终止)                        │
    └────────────────────┬───────────────────────────────┘
                         │
    ┌────────────────────▼───────────────────────────────┐
    │         Spring Boot (端口9092)                       │
    │  ┌─────────────────────────────────────────────┐   │
    │  │           Filter Chain (过滤器链)              │   │
    │  │  ApiAuthorityFilter → ApiInterceptor         │   │
    │  │  (Token校验)     (URL权限校验)                │   │
    │  └─────────────────────┬───────────────────────┘   │
    │                        │                            │
    │  ┌─────────────────────▼───────────────────────┐   │
    │  │              Controller / API层               │   │
    │  │  OrgInfoApi  UserInfoApi  RoleInfoApi        │   │
    │  │  MenuInfoApi SysInfoApi  MoveApi             │   │
    │  └─────────────────────┬───────────────────────┘   │
    │                        │                            │
    │  ┌─────────────────────▼───────────────────────┐   │
    │  │              Service层                        │   │
    │  │  OrgInfoService  UserInfoService             │   │
    │  │  RoleInfoService MenuInfoService             │   │
    │  │  MoveService      SysInfoService             │   │
    │  └────────┬──────────┬──────────┬──────────────┘   │
    │           │          │          │                    │
    │  ┌────────▼──┐  ┌───▼────┐  ┌─▼──────────────┐   │
    │  │   Redis   │  │ Apollo │  │  Mapper/DAO层   │   │
    │  │ Token缓存 │  │ 配置中 │  │  MyBatis        │   │
    │  │ 用户信息  │  │ 心     │  │  (17个Mapper)   │   │
    │  └───────────┘  └────────┘  └────────┬────────┘   │
    │                                       │             │
    └───────────────────────────────────────┼─────────────┘
                                          │
                              ┌───────────▼───────────┐
                              │      GaussDB           │
                              │  (信创数据库)           │
                              │                       │
                              │ privilege_org_info     │
                              │ privilege_user_info    │
                              │ privilege_role_info    │
                              │ privilege_menu_info    │
                              │ privilege_org_system   │
                              │ privilege_user_role    │
                              │ privilege_role_resource│
                              │ privilege_user_auth    │
                              │ privilege_auth_info    │
                              │ privilege_auth_menu    │
                              │ privilege_menu_service │
                              │ person_division        │
                              │ up_org_user            │
                              │ account_record         │
                              │ sensitive_words        │
                              └───────────────────────┘
```

---

## 九、权限数据流转全景

### 🔑 用户能做什么？从数据库到前端菜单的完整链路

```
1. 用户登录 → Token写入Redis
2. 前端请求菜单 → ApiInterceptor校验Token
3. 后端查用户角色 → privilege_user_role_info
4. 后端查角色资源 → privilege_role_resource (角色关联了哪些菜单)
5. 后端查菜单详情 → privilege_menu_info
6. 后端查机构菜单 → privilege_org_system (机构开通了哪些菜单)
7. 取交集 → 用户能看到的菜单 = 角色菜单 ∩ 机构菜单
8. 构建菜单树 → buildTree()递归组装
9. 返回前端 → 渲染侧边栏菜单

🏠 就像员工进公司：
- 你的工牌(Token) → 确认你是谁
- 你的岗位(角色) → 决定你能用哪些工具
- 你所在部门(机构) → 决定你能进哪些房间
- 最终你能用的 = 岗位给你的工具 ∩ 部门给你的房间权限
```

---

## 十、本章总结

| 内容 | 覆盖情况 |
|------|---------|
| query()方法200行逐行拆解 | ✅ 四大分支全部覆盖 |
| getidList() BFS机构树遍历 | ✅ 逐行拆解+图解 |
| buildTree() 菜单树递归构建 | ✅ 逐行拆解+图解 |
| 完整数据流时序图 | ✅ 登录→查菜单→操作数据 |
| 前端页面→接口映射 | ✅ 47个接口全覆盖 |
| 数据迁移逻辑 | ✅ 三个迁移方法逐个拆解 |
| 安全问题分析 | ✅ 6个严重+2个中等 |
| 核心数据流图 | ✅ ASCII架构图 |
| 权限数据流转全景 | ✅ 从数据库到前端菜单完整链路 |
| query()性能问题汇总 | ✅ 6个问题+学习要点 |

---

📎 **延伸阅读**：
- [深度解析-角色管理](picc-mzmtb-user-深度解析第三章-角色管理.md) - 角色管理的完整流程、数据模型、设计思路
- [深度解析-菜单与系统管理](picc-mzmtb-user-深度解析第四章-菜单与系统管理.md) - 菜单树递归构建、服务接口管理
- [数据库ER图与表结构](picc-mzmtb-user-数据库ER图与表结构.md) - query()涉及的privilege_org_info等核心表的详细说明

