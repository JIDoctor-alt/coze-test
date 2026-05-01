> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC门诊慢特病业务 - SQL与数据库问题分析文档

> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

> 📖 本文档为零基础小白打造，用最通俗易懂的语言，带你彻底搞懂这套系统的SQL和数据库使用
> 
> 🎯 目标：看完这篇，你也能像个老司机一样，跟别人讲清楚这个系统的SQL是怎么写的、数据库是怎么用的

---

## 📚 目录导航

1. [MyBatis Mapper XML深度分析](#一mybatis-mapper-xml深度分析) - 213个Mapper是怎么写SQL的
2. [慢SQL风险识别](#二慢sql风险识别) - 找出那些拖后腿的查询
3. [核心表关系与查询模式](#三核心表关系与查询模式) - 8大金刚都是怎么被查的
4. [事务管理分析](#四事务管理分析) - 原子弹是怎么确保不爆炸的
5. [数据库问题分析](#五数据库问题分析) - 让系统跑得更快更稳
6. [GaussDB特有优化](#六gaussdb特有优化) - 华为数据库的独门秘籍

---

## 一、MyBatis Mapper XML深度分析

### 1.1 基础统计速览

先来看看这套系统有多少SQL"菜谱"：

| 指标 | 数量 | 说明 |
|------|------|------|
| **Mapper XML文件** | 213个 | 存放SQL语句的"菜谱本" |
| **总代码行数** | 65,069行 | 所有Mapper XML加起来 |
| **最大Mapper** | 18,182行 | ActivitiDao.xml (工作流相关) |
| **使用动态SQL(if)** | 154个Mapper | 72%的Mapper用了条件判断 |
| **使用foreach** | 41个Mapper | 批量操作的"神器" |
| **使用JOIN** | 42个Mapper | 表与表的"拼图游戏" |
| **使用分页** | 30个Mapper | "减肥"查询结果 |

**🀄 小白解读**：
> 想象一下，你有213本菜谱，每本平均300多行字，这厨房够大吧？

---

### 1.2 动态SQL使用分析

#### 📌 什么是动态SQL？

> **动态SQL = 会"看情况办事"的SQL**
> 
> 比如：用户输入了姓名就按姓名查，输入了手机号就按手机号查，都输入了就两个都用

#### 1.2.1 if标签 - 最常见的条件判断

**使用统计**：154个Mapper使用，占比72%

**典型例子** - 申报列表查询：

```xml
<!-- VipMbdeclareInfoDao.xml -->
<select id="getVipMbdeclareInfoList" resultType="VipMbdeclareInfo">
    SELECT ID, NAME, IDCARD, ICDNAME, ... 
    FROM VIP_MBDECLARE_INFO
    <where>
        dr = 0  <!-- 逻辑删除标记 -->
        <if test="name != null and name != ''">
            AND NAME = #{name}
        </if>
        <if test="idcard != null and idcard != ''">
            AND IDCARD = #{idcard}
        </if>
        <if test="icdtype != null and icdtype != ''">
            AND ICDTYPE = #{icdtype}
        </if>
    </where>
    ORDER BY CREATETIME DESC
</select>
```

**🀄 小白解读**：
> 想象你在填表格搜索框：
> - 只填了姓名？→ 只按姓名查
> - 只填了身份证？→ 只按身份证查
> - 都填了？→ 两个条件一起用
> 
> 这就是 `if` 标签在做的事！

---

#### 1.2.2 choose/when标签 - 多选一

**使用统计**：15个Mapper使用

**典型例子** - 手机号或用户ID二选一：

```xml
<choose>
    <when test="userid != null and mobile != null">
        AND ( MOBILE = #{mobile} OR USERID = #{userid} )
    </when>
    <when test="mobile != null">
        AND MOBILE = #{mobile}
    </when>
</choose>
```

**🀄 小白解读**：
> 这就像点外卖选配菜：
> 1. 如果有用户ID和手机号 → 用OR查
> 2. 如果只有手机号 → 只用手机号查
> 3. 都不填 → 那就不加这个条件
> 
> `choose` 只会选**第一个满足**的条件！

---

#### 1.2.3 where标签 - 自动处理WHERE

**使用统计**：124个Mapper使用

**好处**：不用手动写 `WHERE 1=1`

```xml
<!-- 不用where标签，需要这样写 -->
<select id="query1">
    SELECT * FROM TABLE_NAME WHERE 1=1
    <if test="name != null">AND NAME = #{name}</if>
</select>

<!-- 用where标签，可以这样写 -->
<select id="query2">
    SELECT * FROM TABLE_NAME
    <where>
        <if test="name != null">AND NAME = #{name}</if>
    </where>
</select>
```

**🀄 小白解读**：
> `where` 标签就像个"智能WHERE助手"：
> - 如果第一个条件是 `AND`，它会自动帮你去掉
> - 如果没有任何条件，它不会生成 WHERE
> 
> 省心又安全！

---

#### 1.2.4 set标签 - 智能UPDATE

**使用统计**：22个Mapper使用

**典型例子** - 动态更新申报信息：

```xml
<update id="updateInfo" parameterType="VipMbdeclareInfoDto">
    UPDATE VIP_MBDECLARE_INFO
    <set>
        <if test="name != null">NAME = #{name},</if>
        <if test="mobile != null">MOBILE = #{mobile},</if>
        <if test="icdcode != null">ICDCODE = #{icdcode},</if>
        MODIFYTIME = NOW()
    </set>
    WHERE ID = #{id}
</update>
```

**🀄 小白解读**：
> `set` 标签会帮你处理讨厌的"最后一个逗号"问题：
> - 如果只更新NAME，SQL变成 `SET NAME = xxx, MODIFYTIME = NOW()`
> - 如果两个都更新，SQL变成 `SET NAME = xxx, MOBILE = xxx, MODIFYTIME = NOW()`

---

### 1.3 复杂联表查询分析

#### 1.3.1 JOIN使用统计

| JOIN类型 | 使用数量 | 说明 |
|---------|---------|------|
| INNER JOIN | 28个 | 两边都有的数据 |
| LEFT JOIN | 35个 | 左边全保留 |
| 隐式JOIN(逗号) | 多个 | 老的写法 |

**典型例子** - 账户多表联合查询：

```xml
<!-- VipAccountmbmzDao.xml -->
<select id="getVipAccountmbmzListForView" resultType="VipAccountmbmzListForViewResultDto">
    SELECT 
        b.id, b.icdcode, b.icdname, b.monthlimit, b.yearlimit,
        vi.name, vi.sex, vi.idcard, vi.mobile,
        va.cardno, va.vipid,
        mon.money
    FROM vip_accountmbmz b
    INNER JOIN vip_account va ON b.accountid = va.id AND va.dr = 0
    INNER JOIN vip_info vi ON va.vipid = vi.id AND vi.dr = 0
    INNER JOIN vip_accountmoney mon ON b.accountid = mon.id AND mon.dr = 0
    WHERE b.dr = 0
</select>
```

**🀄 小白解读**：
> 这就像玩"连连看"：
> 
> ```
> vip_accountmbmz ──accountid──► vip_account ──vipid──► vip_info
>       │
>       └──accountid──► vip_accountmoney
> ```
> 
> INNER JOIN = 必须在两边都有数据才显示
> LEFT JOIN = 左边全保留，右边没有就显示NULL

---

#### 1.3.2 窗口函数(ROW_NUMBER) - 分组排序神器

**使用统计**：20个Mapper使用

**典型例子** - 处方列表取最新：

```xml
<!-- PrescriptionMainDao.xml -->
<select id="selectPrescription" resultType="PrescriptionMainDto">
    SELECT * FROM (
        SELECT
            t.*,
            ROW_NUMBER() OVER(
                PARTITION BY t.accountid 
                ORDER BY todo ASC, createtime DESC
            ) as rowNum
        FROM (
            SELECT * FROM t_mb_prescription_main
            WHERE dr = '0'
        ) t
    ) tt
    WHERE tt.rowNum = '1'  <!-- 取每组的第一条 -->
</select>
```

**🀄 小白解读**：
> 想象你有3张处方，时间分别是1号、2号、3号：
> 
> | 处方 | 时间 | ROW_NUMBER |
> |------|------|------------|
> | 1号 | 2024-01-01 | 3 |
> | 2号 | 2024-01-02 | 2 |
> | 3号 | 2024-01-03 | 1 |
> 
> `WHERE rowNum = 1` 就是取最新的那张处方！

---

### 1.4 批量操作(Foreach)

**使用统计**：41个Mapper使用

#### 1.4.1 foreach批量插入

**典型例子** - 批量保存附件：

```xml
<insert id="batchSaveDeclareFile" parameterType="java.util.List">
    INSERT INTO VIP_MBDECLARE_FILE (
        ID, DECLAREID, FILETYPE, FILEPATH, FILENAME, DR
    ) VALUES
    <foreach collection="list" item="item" separator=",">
        (
            #{item.id}, #{item.declareid}, #{item.filetype},
            #{item.filepath}, #{item.filename}, 0
        )
    </foreach>
</insert>
```

**生成的实际SQL**：
```sql
INSERT INTO VIP_MBDECLARE_FILE (ID, DECLAREID, FILETYPE, ...) VALUES
('id1', 'decl1', '1', ...),
('id2', 'decl1', '2', ...),
('id3', 'decl1', '3', ...)
```

**🀄 小白解读**：
> 以前：插入3条数据要写3次INSERT
> 现在：1次INSERT搞定3条数据
> 
> 效率提升：3倍！

---

#### 1.4.2 foreach批量IN查询

**典型例子** - 批量查询申报信息：

```xml
<select id="queryByIds" resultType="VipMbdeclareInfo">
    SELECT * FROM VIP_MBDECLARE_INFO
    WHERE DR = 0
    AND ID IN
    <foreach collection="ids" item="id" open="(" separator="," close=")">
        #{id}
    </foreach>
</select>
```

---

### 1.5 分页实现方式

**使用统计**：30个Mapper使用分页

#### 1.5.1 MySQL风格LIMIT

```xml
<select id="selectLasttimeone" resultType="PrescriptionMain">
    SELECT * FROM t_mb_prescription_main
    WHERE accountid = #{accountid}
    ORDER BY createtime DESC 
    LIMIT 1
</select>
```

#### 1.5.2 应用层分页(PageInfo)

```java
// VipMbdeclareInfoServiceImpl.java
public ResultPage<VipMbdeclareInfoDto> queryMbdeclarePhysicalCompleteList(...) {
    List<VipMbdeclareInfoDto> infoList = dao.selectList(queryParam);
    return this.createResultPage(new PageInfo<>(infoList));
}
```

**🀄 小白解读**：
> 应用层分页 = 把所有数据查出来，然后在内存里"切蛋糕"
> 数据库分页 = 让数据库只返回需要的"那块蛋糕"
> 
> 建议：数据量大时用数据库分页，小数据量时用应用层分页

---

## 二、慢SQL风险识别

> ⚠️ **慢SQL = 堵车，后面的车全排队等着**

### 2.1 缺少WHERE条件的全表扫描 🔴

**风险等级**：🔴 高危

**发现问题**：部分Mapper中存在潜在的全表扫描风险

```xml
<!-- 风险示例：没有主键/索引条件 -->
<select id="queryVIPMbdeclareFile" resultType="VipMbdeclareFile">
    select * from VIP_MBDECLARE_FILE 
    where filetype = '4' and dr = 0 
    and char_length(filecontent) = 0  
    limit 10
</select>
```

**学习要点**：

📖 **规范写法参考（供学习对比）**：

---

### 2.2 SELECT * 的使用 🟡

**风险等级**：🟡 中危

**发现问题**：11个Mapper使用了 `SELECT *`

```xml
<!-- 风险示例 -->
<select id="getByAccountid" resultType="VipAccountmbmz">
    SELECT * FROM VIP_ACCOUNTMBMZ WHERE ACCOUNTID = #{accountid}
</select>

<!-- VipInfoDao.xml 中多处使用 -->
<select id="getVipInfoForupdate" resultType="VipInfo">
    SELECT * FROM VIP_INFO WHERE ID = #{id} AND DR = 0 FOR UPDATE
</select>
```

**学习要点**：

📖 **规范写法参考（供学习对比）**：SELECT * 会增加网络传输量，理解其影响有助于学习 SQL 优化原理。

**问题分析**：
1. 增加网络传输量
2. 无法利用覆盖索引优化
3. 表结构变更时可能出问题

---

### 2.3 模糊查询前置百分号 🔴

**风险等级**：🔴 高危

**发现问题**：大量使用 `LIKE '%xxx%'`

**典型案例** - 申报列表查询(60+处)：

```xml
<!-- VipMbdeclareInfoDao.xml -->
<if test="unitcode != null and unitcode != ''">
    AND UNITCODE like '%' || #{unitcode} || '%'
</if>
```

**ActivitiDao.xml中的统计**：
```
UNITCODE like '%...%' 出现次数：100+次
ICDCODE like '%...%' 出现次数：20+次
ICDNAME like '%...%' 出现次数：10+次
```

**🀄 小白解读**：
> ```
> LIKE '%keyword%' = 读书时把书翻到最后一页，
>                     然后从后往前找"keyword"
>                     必须看完整个书架！
> 
> LIKE 'keyword%'  = 读书时从书架左边开始找，
>                     可以直接跳到对应位置！
> ```

**学习要点**：

📖 **规范写法参考（供学习对比）**：LIKE '%keyword%' 无法使用索引，理解其影响有助于学习数据库索引原理。

---

### 2.4 N+1查询问题 🔴

**风险等级**：🔴 高危

**发现问题**：循环中执行SQL

**典型案例** - 批量撤回申报：

```java
// VipMbdeclareInfoServiceImpl.java
for (String id : idArr) {
    // 每个ID都单独查一次数据库！
    VipDivideInfoBj vipDivideInfoBj = vipDivideInfoBjService.selectOne(
        new VipDivideInfoBj() {{ setId(id); }}
    );
    
    if(vipDivideInfoBj1!=null && vipDivideInfoBj1.getStatus()!=0){
        throw new CustomException("选择的记录申报状态不在撤回范围之内！");
    }
    // 每个ID都单独更新一次！
    vipDivideInfoBjService.update(...);
}
```

**🀄 小白解读**：
> 假设你有100个申报要撤回：
> 
> **N+1问题**：
> - 查100次 + 更新100次 = 200次数据库操作
> 
> **优化后**：
> - 1次批量查询 + 1次批量更新 = 2次数据库操作
> 
> 效率提升：**100倍**！

**学习要点**：

📖 **规范写法参考（供学习对比）**：N+1 查询问题会显著降低查询性能，理解其原理有助于学习数据库查询优化。

**问题分析**：
- 假设有100个申报要撤回：
- N+1问题：查100次 + 更新100次 = 200次数据库操作
- 理解循环中执行 SQL 的性能影响

---

### 2.5 缺少LIMIT的大量返回 🟡

**风险等级**：🟡 中危

**发现问题**：部分查询没有限制返回数量

```xml
<!-- 风险示例 -->
<select id="getVipInfoForupdate" resultType="VipInfo">
    SELECT * FROM VIP_INFO
    WHERE DR = 0 AND IDCARD = #{idcard} AND NAME = #{name}
    <!-- 没有LIMIT -->
</select>
```

**学习要点**：

📖 **规范写法参考（供学习对比）**：缺少 LIMIT 可能导致返回大量数据，理解其影响有助于学习 SQL 查询安全。

**问题分析**：部分查询没有限制返回数量，可能导致内存问题。

---

### 2.6 慢SQL风险汇总表

| 问题类型 | 发现数量 | 风险等级 | 学习理解 |
|---------|---------|---------|---------|
| 模糊查询前置% | 100+处 | 🔴 高 | 理解索引原理 |
| SELECT * | 11处 | 🟡 中 | 理解网络传输 |
| 缺少LIMIT | 多处 | 🟡 中 | 理解查询安全 |
| N+1查询 | 发现2处 | 🔴 高 | 理解批量操作 |
| 无WHERE条件 | 潜在风险 | 🟡 中 | 理解SQL安全 |

---

## 三、核心表关系与查询模式

> 💡 本章节分析8大核心表的查询模式，基于数据模型文档

### 3.1 核心表概览

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           门诊慢特病系统 - 核心表关系                          │
└──────────────────────────────────────────────────────────────────────────────┘

         ┌───────────────┐
         │  VIP_INFO     │
         │  会员信息表    │
         └───────┬───────┘
                 │ 1:N
                 │ vipid
         ┌──────▼───────────┐
         │  VIP_ACCOUNT     │
         │  账户表           │
         └───────┬───────────┘
                 │
         ┌───────┼───────────────┐
         │1:1    │               │1:N
    ┌────▼───┐   │         ┌────▼────────┐
    │VIP_CARD│   │         │VIP_ACCOUNTMBMZ│
    │会员卡表│   │         │慢特病账户表    │
    └────────┘   │         └──────┬────────┘
                 │                │
         ┌───────▼─────────┐     │ 1:N
         │VIP_ACCOUNTMONEY │     ▼
         │账户余额表        │ ┌───────────────┐
         └─────────────────┘ │T_MB_PRESCRIPTION│
                              │处方主表        │
                              └───────────────┘

         ┌───────────────────────────────────────────┐
         │           VIP_MBDECLARE_INFO              │
         │              申报信息主表                   │
         └───────────┬───────────┬───────────┬───────┘
                     │           │           │
               1:N   │      1:N  │      1:1  │
         ┌───────────▼┐  ┌───────▼┐  ┌──────▼──────┐
         │FILE附件表 │  │APPROVAL│  │PHYSICAL体检表│
         └───────────┘  │审批记录 │  └─────────────┘
                        └─────────┘

         ┌───────────────────────────────────────────┐
         │           GHI_INSURE_DETAIL              │
         │              参保信息表                    │
         └───────────────────────────────────────────┘
```

---

### 3.2 核心表查询频率分析

#### 📋 VIP_MBDECLARE_INFO - 申报信息表

**查询频率**：⭐⭐⭐⭐⭐ 最高

**主要查询场景**：

| 查询类型 | Mapper | 条件 | 说明 |
|---------|--------|------|------|
| 列表查询 | VipMbdeclareInfoDao | 姓名/手机/身份证/状态/机构 | 后台管理 |
| 详情查询 | VipMbdeclareInfoDao | ID | 查看申报详情 |
| 状态更新 | VipMbdeclareInfoDao | ID | 审批流程 |
| 附件查询 | VipMbdeclareFileDao | declareid | 申报材料 |

**典型SQL模式**：

```xml
<!-- 申报列表查询 -->
<select id="getVipMbdeclareInfoList">
    SELECT ID, NAME, IDCARD, ICDNAME, 
           CASE WHEN APPLYSTATUS = 0 THEN 0 ... END AS APPLYSTATUS,
           PHYSICALSTATUS, UNITCODE, ...
    FROM VIP_MBDECLARE_INFO
    <where>
        DR = 0
        <if test="name != null">AND NAME = #{name}</if>
        <if test="applystatus != null">AND APPLYSTATUS = #{applystatus}</if>
        <if test="unitcode != null">AND UNITCODE like '%' || #{unitcode} || '%'</if>
    </where>
    ORDER BY CREATETIME DESC
</select>
```

**索引学习要点**：

📖 **规范写法参考（供学习对比）**：理解索引的作用和创建方法有助于学习数据库性能优化。

**学习理解**：
- 创建合适的索引可以显著提升查询性能
- 复合索引需要考虑字段顺序

---

#### 👤 VIP_INFO - 会员信息表

**查询频率**：⭐⭐⭐⭐ 高

**主要查询场景**：

| 查询类型 | Mapper | 条件 | 说明 |
|---------|--------|------|------|
| 身份验证 | VipInfoDao | 身份证+姓名 | 唯一性检查 |
| 会员查询 | VipInfoDao | ID/手机号 | 登录/查询 |
| 排他锁查询 | VipInfoDao | ID | 资金操作 |

**典型SQL模式**：

```xml
<!-- 身份证姓名验证 -->
<select id="getByIdcardAndName" resultType="VipInfo">
    SELECT * FROM VIP_INFO
    WHERE DR = 0 AND IDCARD = #{idcard} AND NAME = #{name}
</select>

<!-- 行锁查询(资金操作时) -->
<select id="getVipInfoForupdate" resultType="VipInfo">
    SELECT * FROM VIP_INFO
    WHERE ID = #{id} AND DR = 0
    FOR UPDATE  <!-- 悲观锁，防止并发问题 -->
</select>
```

**索引学习要点**：

📖 **规范写法参考（供学习对比）**：理解索引的作用和创建方法有助于学习数据库性能优化。

**学习理解**：
- 身份证号和姓名的唯一约束索引设计
- 手机号索引的创建

---

#### 💰 VIP_ACCOUNTMBMZ - 慢特病账户表

**查询频率**：⭐⭐⭐⭐ 高

**主要查询场景**：

| 查询类型 | Mapper | 条件 | 说明 |
|---------|--------|------|------|
| 账户列表 | VipAccountmbmzDao | accountid/icdtype | 查看账户 |
| 多表联查 | VipAccountmbmzDao | accountid | 联查会员+余额 |
| 额度查询 | VipAccountmbmzDao | accountid | 报销计算 |

**典型SQL模式**：

```xml
<!-- 慢特病账户多表联查 -->
<select id="getVipAccountmbmzListForView">
    SELECT 
        b.id, b.icdcode, b.icdname, b.monthlimit, b.yearlimit,
        vi.name, vi.sex, vi.idcard, vi.mobile,
        va.cardno, va.vipid,
        mon.money
    FROM vip_accountmbmz b
    INNER JOIN vip_account va ON b.accountid = va.id AND va.dr = 0
    INNER JOIN vip_info vi ON va.vipid = vi.id AND vi.dr = 0
    INNER JOIN vip_accountmoney mon ON b.accountid = mon.id AND mon.dr = 0
    WHERE b.dr = 0
    <if test="accountid != null">AND b.accountid = #{accountid}</if>
    <if test="icdtype != null">AND b.icdtype = #{icdtype}</if>
</select>
```

**索引学习要点**：

📖 **规范写法参考（供学习对比）**：理解复合索引的设计原理有助于学习数据库性能优化。

**学习理解**：
- accountid 是最常用的查询条件
- 复合索引设计需要考虑查询频率

---

#### 💊 T_MB_PRESCRIPTION_MAIN - 处方主表

**查询频率**：⭐⭐⭐ 中高

**主要查询场景**：

| 查询类型 | Mapper | 条件 | 说明 |
|---------|--------|------|------|
| 最新处方 | PrescriptionMainDao | accountid | 处方列表 |
| 处方统计 | PrescriptionMainDao | idcard | 购药统计 |
| 窗口函数 | PrescriptionMainDao | accountid | 分组取最新 |

**典型SQL模式**：

```xml
<!-- 取最新处方(使用窗口函数) -->
<select id="selectPrescription" resultType="PrescriptionMainDto">
    SELECT * FROM (
        SELECT t.*,
            ROW_NUMBER() OVER(PARTITION BY t.accountid ORDER BY todo, createtime DESC) as rowNum
        FROM t_mb_prescription_main t
        WHERE t.dr = '0'
    ) tt
    WHERE tt.rowNum = '1'
</select>
```

**索引学习要点**：

📖 **规范写法参考（供学习对比）**：理解处方表查询特点有助于学习数据库性能优化。

**学习理解**：
- 窗口函数用于分组取最新记录
- createtime 字段用于排序

---

### 3.3 核心表查询模式总结

| 核心表 | 日查询量 | 主要联表 | 索引完整性 | 学习理解 |
|-------|---------|---------|----------|----------|
| VIP_MBDECLARE_INFO | 最高 | 4-5张 | ⚠️需关注 | 理解申报查询 |
| VIP_INFO | 高 | 2-3张 | ✅良好 | 理解会员查询 |
| VIP_ACCOUNTMBMZ | 高 | 3-4张 | ✅良好 | 理解账户查询 |
| VIP_ACCOUNT | 中 | 3-4张 | ⚠️需关注 | 理解关联查询 |
| VIP_ACCOUNTMONEY | 中 | 1-2张 | ⚠️需关注 | 理解余额查询 |
| T_MB_PRESCRIPTION | 中高 | 2-3张 | ⚠️需关注 | 理解处方查询 |
| VIP_MBDECLARE_FILE | 中 | 1-2张 | ⚠️需关注 | 理解文件查询 |
| GHI_INSURE_DETAIL | 中 | 2-3张 | ⚠️需关注 | 理解参保查询 |

---

## 四、事务管理分析

> 💡 事务 = 原子弹，要么全炸要么不炸

### 4.1 @Transactional使用统计

| 统计项 | 数量 |
|-------|------|
| 使用事务的服务类 | 15+个 |
| 传播行为 REQUIRED | 10+处 |
| 传播行为 REQUIRES_NEW | 1处 |
| 事务回滚配置 | rollbackForClassName = "Exception" |

---

### 4.2 典型事务使用场景

#### 场景1：申报提交事务 🔴

```java
@Transactional
public ApiResponse declare(DeclareVo declareVo) {
    ApiResponse apiResponse = ApiResponse.ok();
    
    // 1. 校验参数
    if (!checkParam(declareVo)) {
        throw new CustomException("参数校验失败！");
    }
    
    // 2. 保存申报主表
    VipMbdeclareInfo declareInfo = new VipMbdeclareInfo();
    vipMbdeclareInfoDao.insert(declareInfo);
    
    // 3. 保存申报附件
    for (DeclareFile file : declareVo.getFiles()) {
        VipMbdeclareFile declareFile = new VipMbdeclareFile();
        declareFile.setDeclareid(declareInfo.getId());
        vipMbdeclareFileDao.insert(declareFile);
    }
    
    // 4. 更新体检分配(如果需要)
    if (needPhysical) {
        vipMbdeclarePhysicalDao.update(...);
    }
    
    return apiResponse;
}
```

**🀄 小白解读**：
> 申报提交就像"开户口"：
> - 要创建申报记录 ✓
> - 要保存身份证照片 ✓
> - 要保存病历材料 ✓
> 
> 如果中途任何一个失败，整个"户口申请"就取消，不会留下半成品！

---

#### 场景2：Excel批量导入事务 🟡

```java
@Transactional(propagation = Propagation.REQUIRED)
private void importOne(GhiInsureDetail ghi, GhiInsureHos ghihos, UnitConfig unitConfig) {
    String mobile = ghi.getInsuredmobile();
    // 查询会员
    List<VipInfo> vipInfos = vipInfoService.getByIdcardAndName(
        ghi.getInsuredidno(), ghi.getInsurednname()
    );
    // 保存关联关系
    if (vipInfos.size() > 0) {
        // 保存到数据库
    }
}
```

**问题分析**：
- 如果Excel有10000条数据，这个事务会很大
- 可能导致数据库连接长时间被占用
- 网络异常时回滚成本高

**学习要点**：

📖 **规范写法参考（供学习对比）**：大事务会长时间占用数据库连接，理解其影响有助于学习事务管理。

**问题分析**：
- 如果Excel有10000条数据，这个事务会很大
- 可能导致数据库连接长时间被占用
- 网络异常时回滚成本高

---

#### 场景3：排他锁查询(悲观锁) 🟢

```xml
<!-- VipInfoDao.xml -->
<select id="getVipInfoForupdate" resultType="VipInfo">
    SELECT * FROM VIP_INFO
    WHERE ID = #{id} AND DR = 0
    FOR UPDATE  <!-- 悲观锁 -->
</select>
```

**使用场景**：资金扣减、账户余额更新

```java
@Transactional
public void deductMoney(String accountId, BigDecimal amount) {
    // 1. 加锁查询账户
    VipAccountmoney account = vipAccountmoneyDao.getForUpdate(accountId);
    
    // 2. 校验余额
    if (account.getMoney().compareTo(amount) < 0) {
        throw new CustomException("余额不足！");
    }
    
    // 3. 扣减余额
    account.setMoney(account.getMoney().subtract(amount));
    vipAccountmoneyDao.update(account);
    
    // 4. 记录流水
    VipAccountChange change = new VipAccountChange();
    change.setAccountid(accountId);
    change.setAmount(amount.negate());
    vipAccountmoneyChangeDao.insert(change);
}
```

**🀄 小白解读**：
> `FOR UPDATE` = 告诉数据库："这笔账我先锁着，别人别动！"
> 
> 就像你去银行取钱，要先锁住账户，防止别人同时取钱导致余额变成负数！

---

### 4.3 事务传播行为分析

| 传播行为 | 使用次数 | 说明 |
|---------|---------|------|
| REQUIRED | 10+ | 默认值，加入已有事务 |
| REQUIRES_NEW | 1 | 挂起当前事务，创建新事务 |
| 未指定 | 5+ | 默认REQUIRED |

**典型REQUIRES_NEW场景**：

```java
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void logError(String errorInfo) {
    // 即使外面的事务失败了，这条日志也要记录
    errorLogDao.insert(new ErrorLog(errorInfo));
}
```

---

### 4.4 事务学习要点

#### ⚠️ 大事务识别

以下情况属于"大事务"风险：

```java
@Transactional
public void batchImport(List<ExcelData> dataList) {
    for (ExcelData data : dataList) {  // 循环1000次
        // 每个循环都有数据库操作
        saveMain(data);      // INSERT
        saveDetail(data);    // INSERT
        saveFile(data);      // INSERT
        updateStatus(data);   // UPDATE
    }
}
```

**问题**：
- 1000条数据 = 可能1000+次数据库操作
- 任何一条失败，全部回滚
- 数据库连接长时间占用

#### 📖 学习理解

📖 **规范写法参考（供学习对比）**：大事务会影响系统性能，理解其原理有助于学习事务管理。

**学习要点**：
- 分段提交可以减少单次事务的规模
- 批量SQL可以减少数据库交互次数
- 理解事务边界的重要性

---

### 4.5 只读事务优化

**当前使用情况**：未发现显式使用 `readOnly = true`

**学习要点**：

📖 **规范写法参考（供学习对比）**：readOnly 事务可以让数据库进行优化，理解其作用有助于学习事务管理。

**学习理解**：
1. 数据库可以对只读查询进行优化
2. 不会获取写锁
3. 明确代码意图

---

## 五、数据库问题分析

### 5.1 索引问题分析

#### 🔴 高优先级索引

**VIP_MBDECLARE_INFO表**

📖 **索引学习要点**：
- 理解 DR + APPLYSTATUS 复合索引的作用
- 理解 DR + UNITCODE 复合索引的作用
- 理解 DR + CREATETIME 复合索引的作用
- 理解 IDCARD 和 MOBILE 索引的作用

---

#### 🟡 中优先级索引

**VIP_MBDECLARE_FILE表**

📖 **索引学习要点**：
- 理解 DECLAREID 索引的作用（关联申报主表）
- 理解 FILETYPE 索引的作用（按类型查询）

**GHI_INSURE_DETAIL表**

📖 **索引学习要点**：
- 理解 INSUREDIDNO 索引的作用（按身份证查询）
- 理解 ACCOUNTID 索引的作用（按账户查询）

---

### 5.2 分页查询分析

#### 当前问题

```xml
<!-- 应用层分页：先查全部，再内存分页 -->
<select id="getVipMbdeclareInfoList" resultType="VipMbdeclareInfo">
    SELECT * FROM VIP_MBDECLARE_INFO WHERE DR = 0
    <if test="name != null">AND NAME = #{name}</if>
    ORDER BY CREATETIME DESC
    <!-- 没有LIMIT！ -->
</select>
```

#### 问题分析

#### 学习理解

📖 **规范写法参考（供学习对比）**：理解数据库层分页和内存分页的区别，有助于学习分页优化原理。

**学习要点**：
- 数据库层分页只返回需要的记录
- 内存分页会加载所有数据再切分
- 游标分页适合深度分页场景

---

### 5.3 模糊查询优化

#### 当前问题

```xml
<!-- 前置%导致无法使用索引 -->
<if test="unitcode != null">
    AND UNITCODE like '%' || #{unitcode} || '%'
</if>
```

#### 学习理解

📖 **规范写法参考（供学习对比）**：LIKE '%keyword%' 无法使用索引，理解其影响有助于学习索引原理。

**学习要点**：
- 前置 % 会导致全表扫描
- ES 适合全文检索场景
- 游标分页适合深度分页场景

---

### 5.4 N+1问题分析

#### 当前问题代码

```java
// 批量操作变成N+1
for (String id : idArr) {
    VipDivideInfoBj info = service.selectOne(new VipDivideInfoBj(){{ setId(id); }});
    // 处理
    service.update(info);
}
```

#### 问题分析

```java
// 1. 批量查询
List<VipDivideInfoBj> infoList = service.selectBatchIds(Arrays.asList(idArr));

// 2. 批量处理
List<VipDivideInfoBj> toUpdate = new ArrayList<>();
for (VipDivideInfoBj info : infoList) {
    if (info.getStatus() == 0) {
        info.setSeconduserid("");
        toUpdate.add(info);
    }
}

// 3. 批量更新
if (!toUpdate.isEmpty()) {
    service.updateBatchById(toUpdate);
}
```

---

### 5.5 读写分离建议

#### 架构设计

```
                    ┌─────────────────┐
                    │   应用服务       │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ 主库(写)  │   │ 从库1(读) │   │ 从库2(读) │
        │ GaussDB  │   │ GaussDB  │   │ GaussDB  │
        └──────────┘   └──────────┘   └──────────┘
```

#### 实现方式

**方案1：注解方式(推荐)**

```java
public class ReadOnlyConnectionInterceptor {
    @Around("@annotation(ReadOnly)")
    public Object routeToRead(ProceedingJoinPoint point) throws Throwable {
        // 切换到从库
        DataSourceContextHolder.setReadOnly(true);
        try {
            return point.proceed();
        } finally {
            DataSourceContextHolder.clearDataSource();
        }
    }
}

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface ReadOnly {}

@Service
public class VipMbdeclareInfoService {
    @ReadOnly
    public List<VipMbdeclareInfo> getList(QueryVo query) {
        return vipMbdeclareInfoDao.selectList(query);
    }
    
    @Transactional
    public void save(VipMbdeclareInfo info) {
        vipMbdeclareInfoDao.insert(info);
    }
}
```

**方案2：MyBatis路由**

📖 **规范写法参考（供学习对比）**：理解读写分离的原理，有助于学习数据库架构设计。

**学习要点**：
- 读库和写库分离可以提升性能
- 需要配置数据源路由

---

### 5.6 数据归档策略

#### 归档时机

| 数据类型 | 保留策略 | 归档时机 |
|---------|---------|---------|
| 历史申报(已结案2年+) | 归档到历史库 | 每年12月 |
| 处方数据(1年前) | 归档到历史库 | 每月1号 |
| 操作日志(6个月前) | 删除或归档 | 每日 |
| 附件文件(已结案1年+) | 迁移到OSS | 每周 |

#### 归档学习理解

📖 **规范写法参考（供学习对比）**：理解数据归档的原理和策略，有助于学习数据库维护。

**学习要点**：
- 历史数据归档可以减少主库压力
- 需要定期执行归档任务
- 归档后需要验证数据完整性

---

## 六、GaussDB学习理解

### 6.1 GaussDB vs MySQL对比

| 特性 | MySQL | GaussDB |
|------|-------|---------|
| 分页 | LIMIT offset,size | LIMIT size OFFSET offset |
| 窗口函数 | 支持 | 支持(完全兼容) |
| 并行查询 | 有限 | 支持 |
| Hash Join | 支持 | 支持 |
| 向量化引擎 | 无 | 支持 |
| AI优化器 | 无 | 支持 |

---

### 6.2 推荐的GaussDB优化

#### 向量化执行

```sql
-- 启用向量化引擎
SET enable_vector_engine = on;

-- 查看执行计划
EXPLAIN PERFORMANCE SELECT * FROM VIP_MBDECLARE_INFO WHERE DR = 0;
```

#### 并行查询

```sql
-- 启用并行查询
SET enable_parallel_query = on;

-- 设置并行度(根据CPU核数)
SET query_parallelism = 4;

-- 大表分析使用并行
ANALYZE PARALLEL VIP_MBDECLARE_INFO;
```

#### 分区表优化

```sql
-- 按月份分区申报表
CREATE TABLE VIP_MBDECLARE_INFO_PART (
    ID VARCHAR(32) NOT NULL,
    NAME VARCHAR(100),
    ...
    CREATETIME TIMESTAMP,
    PRIMARY KEY (ID, CREATETIME)
) PARTITION BY RANGE (CREATETIME) (
    PARTITION p202401 VALUES LESS THAN ('2024-02-01'),
    PARTITION p202402 VALUES LESS THAN ('2024-03-01'),
    PARTITION p202403 VALUES LESS THAN ('2024-04-01'),
    PARTITION p_future VALUES LESS THAN (MAXVALUE)
);

-- 查询自动只扫描相关分区
SELECT * FROM VIP_MBDECLARE_INFO_PART 
WHERE CREATETIME BETWEEN '2024-01-01' AND '2024-01-31';
```

---

### 6.3 SQL兼容性注意事项

#### GaussDB特有的语法

```xml
<!-- 时间函数差异 -->
<!-- MySQL -->
<if test="startdate != null">
    AND createtime >= #{startdate}
</if>

<!-- GaussDB(兼容写法) -->
<if test="startdate != null">
    AND createtime >= to_timestamp(#{startdate}, 'YYYY-MM-DD')
</if>

<!-- GaussDB特有的to_timestamp用法 -->
<if test="startdate != null">
    <![CDATA[
    AND to_timestamp(to_char(va.activatetime,'YYYY-MM-DD HH24:MI:SS'),'YYYY-MM-DD HH24:MI:SS') 
    >= to_timestamp(to_char(CAST(#{startdate} as DATE),'YYYY-MM-DD')||' 00:00:00','YYYY-MM-DD HH24:MI:SS')
    ]]>
</if>
```

#### 字符串聚合函数

```sql
-- MySQL
SELECT GROUP_CONCAT(name) FROM users;

-- GaussDB(兼容写法)
SELECT STRING_AGG(name, ',') FROM users;
```

---

## 七、总结与行动计划

### 7.1 问题优先级排序

| 优先级 | 问题 | 影响 | 预计工时 |
|-------|------|------|---------|
| 🔴 P0 | 模糊查询前置%无法走索引 | 查询缓慢 | 2天 |
| 🔴 P0 | N+1查询问题 | 批量操作极慢 | 3天 |
| 🟡 P1 | SELECT * 滥用 | 网络开销大 | 1天 |
| 🟡 P1 | 缺少分页LIMIT | 可能OOM | 1天 |
| 🟡 P1 | 索引缺失 | 查询慢 | 2天 |
| 🟢 P2 | 读写分离 | 提升并发 | 5天 |
| 🟢 P2 | 数据归档 | 提升性能 | 3天 |

---

### 7.2 快速优化清单

```markdown
## 紧急优化项(1周内完成)

### 1. 添加缺失索引
- [ ] VIP_MBDECLARE_INFO: DR+APPLYSTATUS, DR+UNITCODE, DR+CREATETIME
- [ ] T_MB_PRESCRIPTION_MAIN: DR+ACCOUNTID, DR+CREATETIME
- [ ] VIP_MBDECLARE_FILE: DECLAREID

### 2. 修复N+1问题
- [ ] VipMbdeclareInfoServiceImpl: 批量撤回优化
- [ ] VipDivideInfoBjService: 批量操作优化

### 3. 添加分页限制
- [ ] 所有列表查询添加LIMIT
- [ ] 添加COUNT(*)统计总数

## 中期优化项(2-4周)

### 4. 模糊查询优化
- [ ] 评估ES全文检索可行性
- [ ] 优化为前缀匹配或后缀匹配

### 5. 事务优化
- [ ] 大事务拆分
- [ ] 添加只读事务注解

## 长期优化项(1-2月)

### 6. 架构优化
- [ ] 读写分离
- [ ] 分区表设计
- [ ] 数据归档策略
```

---

### 7.3 监控指标

建议监控以下SQL性能指标：

```yaml
# Prometheus监控指标
sql_query_duration_seconds:
  - VIP_MBDECLARE_INFO列表查询
  - VIP_ACCOUNTMBMZ联表查询
  - T_MB_PRESCRIPTION窗口函数查询

sql_slow_query_count:
  threshold: 1s
  alert: true

sql_active_connection_count:
  warning: 80%
  critical: 90%
```

---

## 附录：术语表

| 术语 | 小白解释 |
|------|---------|
| SQL | 给数据库下订单的指令 |
| 索引 | 书的目录，不用翻遍全书就能找到 |
| 全表扫描 | 没有目录，从第一页翻到最后一页 |
| JOIN | 把两张表像拼图一样拼起来 |
| 事务 | 原子弹，要么全炸要么不炸 |
| N+1问题 | 买100本书，不是一次下单，而是打了100次电话 |
| 慢SQL | 堵车，后面的车全排队等着 |
| SELECT * | 把整本书都搬回家(其实只需要一页) |
| 乐观锁 | 相信你不会乱改，改了再说 |
| 悲观锁 | 先把门锁上，谁也别想改 |
| 读写分离 | 有人专门负责读，有人专门负责写 |
| 数据归档 | 把旧书搬到仓库，新书架放新书 |

---

> 📝 文档版本：v1.0
> 
> 📅 更新日期：2024年
> 
> 👤 作者：AI助手
