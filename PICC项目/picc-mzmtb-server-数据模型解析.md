> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC门诊慢特病业务管理系统 - 数据模型层深度解析

> 📖 本文档为零基础小白打造，用最通俗易懂的语言，带你彻底搞懂这套系统的数据库设计
> 
> 🎯 目标：看完这篇，你也能像个老司机一样，跟别人讲清楚这个系统是怎么"存数据"的

---

## 📚 目录导航

1. [数据库整体概览](#一数据库整体概览) - 先看看这个"大仓库"长什么样
2. [核心业务表详解](#二核心业务表详解) - 8大金刚都是干嘛的
3. [ER图 - 表与表的关系](#三er图表与表的关系) - 像拼图一样理解表之间的联系
4. [Mapper XML深度解析](#四mapper-xml深度解析) - SQL菜谱的详细解读
5. [SQL性能分析](#五sql性能分析) - 找出那些拖后腿的慢查询
6. [设计建议与优化](#六设计建议与优化) - 让系统跑得更快更稳

---

## 一、数据库整体概览

### 1.1 系统规模速览

先来张"全家福"，看看这个系统有多少东西：

| 指标 | 数量 | 说明 |
|------|------|------|
| **Mapper XML文件** | 213个 | 存放SQL语句的"菜谱本" |
| **Java PO类** | 260+个 | 跟数据库表一一对应的"代言人" |
| **核心模块** | 6个 | mb(慢特病)、vip(会员)、drugstore(药店)等 |
| **地市子模块** | 13个 | 全国各地市的定制化实现 |

### 1.2 模块分布图

```
picc-mzmtb-server/
├── picchealth-db/                    # 数据库层（重点！）
│   └── src/main/resources/mapper/
│       ├── module/
│       │   ├── mb/              ← 核心业务模块 (157个Mapper)
│       │   │   ├── 申报管理 (declare)
│       │   │   ├── 审批管理 (review/approval)
│       │   │   ├── 疾病管理 (disease)
│       │   │   ├── 处方管理 (prescription)
│       │   │   ├── 账户管理 (account)
│       │   │   └── 发卡管理 (card)
│       │   ├── vip/              ← 会员模块 (26个Mapper)
│       │   ├── publics/          ← 公共模块 (16个Mapper)
│       │   ├── basedoc/         ← 基础文档 (7个Mapper)
│       │   ├── drugstore/       ← 药店模块 (2个Mapper)
│       │   └── dpview/          ← 数据视图 (4个Mapper)
│       └── java/.../po/          ← PO实体类
├── picchealth-server/               # 服务层
└── mtb-yh/                          # 地市定制模块
    ├── mtb-bj/  (北京)
    ├── mtb-ya/  (延安)
    ├── mtb-sl/  (商洛)
    ├── mtb-yl/  (榆林)
    └── ... (其他地市)
```

### 1.3 数据库命名规范

从Mapper文件名就能猜出表名，比如：

| Mapper文件 | 对应表名 |
|-----------|---------|
| `VipMbdeclareInfoDao.xml` | `VIP_MBDECLARE_INFO` |
| `PersonDao.xml` | `PERSON` (或 `MB_PERSON`) |
| `VipCardDao.xml` | `VIP_CARD` |

**规律解读**：
- `VIP_` 前缀 = 会员相关表
- `MB_` 前缀 = 慢特病(Màn Bìng)相关表
- `GHI_` 前缀 = 社保/医保相关表
- 大驼峰命名转下划线：`MbdeclareInfo` → `MB_DECLARE_INFO`

---

## 二、核心业务表详解

### 2.1 表的"八大金刚" 🦸‍♂️

系统里最重要的8类表，用生活中的比喻来理解：

```
┌─────────────────────────────────────────────────────────────────────┐
│                        门诊慢特病管理系统核心表                      │
├─────────────┬──────────────────────────────────────────────────────┤
│  申报管理    │  像"入学申请"，患者提交资料申请慢特病待遇            │
│  审批管理    │  像"老师批作业"，审核人员决定通过还是驳回            │
│  疾病管理    │  像"病历本目录"，记录所有慢特病的种类和编码          │
│  处方管理    │  像"药方"，记录医生开的药品清单                      │
│  账户管理    │  像"钱包+病历本"，存储患者身份和报销额度             │
│  药店管理    │  像"药房地图"，哪些药店可以买药报销                  │
│  发卡管理    │  像"发身份证"，给审核通过的人发慢特病卡               │
│  参保管理    │  像"医保卡信息"，对接医保局的参保数据                │
└─────────────┴──────────────────────────────────────────────────────┘
```

---

### 2.2 申报相关表 (Declare/Apply)

#### 📋 VIP_MBDECLARE_INFO - 申报信息主表

**一句话理解**：这是整个系统的"申请表"，患者要享受慢特病待遇，先在这里报名。

**核心字段解读**：

```java
// 申报人基本信息
String name;           // 姓名 (敏感信息，已加密)
String idcard;         // 证件号 (敏感信息，已加密)
String mobile;         // 手机号 (敏感信息，已加密)
String sex;            // 性别
Date birthday;         // 生日
String persontype;     // 人员类型："3"=职工，"390"=居民

// 疾病信息
String icdkind;        // 疾病种类
String icdtype;        // 疾病类型 (决定慢病卡是否合并)
String icdcode;        // 病种编码 (比如 "E11" 代表2型糖尿病)
String icdname;        // 病种名称

// 申报状态 - 这是最复杂的字段！
Integer applystatus;   // 申报状态：0=审核中, 1=初审通过, 2=初审驳回...
Integer physicalstatus;// 体检状态：0=体检中, 1=已体检, 2=未到一次...
Short orgstatus;       // 体检中心分配：0=未分配, 1=已分配
Short endstatus;        // 结案状态：0=未结案, 1=已结案

// 审核人员信息
String firstuserid;     // 初审人ID
String firstusername;  // 初审人姓名
Date firstoperdate;    // 初审时间
String seconduserid;   // 专家审批人ID
String secondusername; // 专家审批人姓名
Date secondoperdate;   // 专家审批时间

// 其他重要信息
String unitcode;       // 机构编码 (申报地点)
String fixedhoscode;   // 定点医院编码
String medicalno;      // 医保编号
String declareno;      // 申报编号
Date declaredate;      // 申报时间
```

**状态机流转图**：

```
用户提交申报
     │
     ▼
[applystatus=0 审核中] ──→ 初审通过
     │                         │
     │                    [applystatus=1]
     │                         │
     │                         ▼
     │               ┌─────────────────────┐
     │               │  需要体检?          │
     │               └─────────────────────┘
     │                    │          │
     │                   是          否
     │                    │          │
     │     [physicalstatus=1 已体检]   │
     │                    │          │
     │                    ▼          ▼
     │              专家审批     直接复审
     │                    │          │
     │    ┌────────────────┴──────────┘
     │    ▼
     │ [applystatus=6 复审通过] ──→ 发卡！
     │    │
     │    ▼
     │ 结案 [endstatus=1]
```

**典型SQL解读**：

```sql
-- 查询申报列表 (带状态计算)
SELECT 
    ID, NAME, IDCARD, ICDNAME,
    -- 这里是状态计算的核心逻辑！
    CASE
        WHEN APPLYSTATUS = 0 THEN 0                           -- 审核中
        WHEN APPLYSTATUS = 1 AND ORGSTATUS = 0 THEN 1        -- 初审通过待分配
        WHEN APPLYSTATUS = 2 THEN 2                           -- 初审驳回
        WHEN APPLYSTATUS = 3 THEN 3                           -- 审核通过
        WHEN APPLYSTATUS = 4 THEN 4                           -- 审核驳回
        WHEN APPLYSTATUS = 5 THEN 11                          -- (特殊状态)
        WHEN APPLYSTATUS = 1 AND PHYSICALSTATUS = 0 THEN 5    -- 待体检
        WHEN APPLYSTATUS = 1 AND PHYSICALSTATUS = 1 THEN 6    -- 已体检待审批
        WHEN APPLYSTATUS = 1 AND PHYSICALSTATUS = 2 THEN 7   -- 一次未到
        WHEN APPLYSTATUS = 1 AND PHYSICALSTATUS = 3 THEN 8   -- 两次未到
        WHEN APPLYSTATUS = 1 AND PHYSICALSTATUS = 4 THEN 9   -- 三次未到
        WHEN APPLYSTATUS = 1 AND PHYSICALSTATUS = 5 THEN 10  -- 放弃体检
        ELSE 0
    END AS APPLYSTATUS
FROM VIP_MBDECLARE_INFO
WHERE DR = 0  -- 逻辑删除标记，0=有效
```

---

#### 📎 VIP_MBDECLARE_FILE - 申报附件表

**一句话理解**：患者提交的"证明材料"，身份证照片、病历等。

```java
String declareid;      // 关联申报ID
String filetype;       // 文件类型：1=证件照, 2=病历, 3=体检报告...
String filepath;       // 文件存储路径
String filename;       // 原始文件名
Date uploadtime;       // 上传时间
String todo;           // 处理状态：0=待处理, 1=已处理
```

---

#### 🏥 VIP_MBDECLARE_PHYSICAL - 体检分配表

**一句话理解**：哪些人去哪个体检中心体检。

```java
String declareid;      // 申报ID
String hosid;          // 体检中心ID
String hosname;        // 体检中心名称
Short status;          // 状态：0=待体检, 1=已完成
String reportid;       // 体检报告ID
```

---

### 2.3 审批相关表 (Audit/Review)

#### ✅ VIP_MBDECLARE_APPROVAL - 审批记录表

**一句话理解**：每次审批的"批条"，谁在什么时间同意了/驳回了。

```java
String declareid;          // 申报ID
String approvaluserid;     // 审批人ID
String approvalusername;   // 审批人姓名
Date approvaldate;         // 审批时间
Integer approvalstatus;    // 审批状态：0=通过, 1=不通过
String approvalnote;       // 审批意见/驳回原因
String approvaltype;       // 审批类型：1=初审, 2=专家审批, 3=复审
String icdcode;            // 病种编码
String icdname;            // 病种名称
```

**审批类型说明**：
- `approvaltype=1` : 初审（窗口工作人员审核资料是否齐全）
- `approvaltype=2` : 专家审批（医生专家判断是否符合慢特病标准）
- `approvaltype=3` : 复审（年度复审，检查是否还需继续享受待遇）

#### 🎯 VIP_REVIEW_YA - 复审信息表

**一句话理解**：专家复审的"复议单"。

```java
String declareid;          // 申报ID
String name;               // 患者姓名
String idcard;             // 身份证号
String isreview;           // 复审状态：0=未复审, 1=已复审
String recordstatus;       // 病历相符：0=不相符, 1=相符
String diseasesstatus;     // 疾病相符
String indicatorsstatus;   // 指标相符
```

---

### 2.4 疾病相关表 (Disease)

系统支持多个地市，每个地市的疾病目录可能不同，所以有多个疾病表。

#### 📖 T_MB_DISEASE_XX - 各地市疾病目录表

| 表名 | 所属地市 | 说明 |
|------|---------|------|
| T_MB_DISEASE_YA | 延安 | 延安慢特病病种目录 |
| T_MB_DISEASE_YL | 榆林 | 榆林慢特病病种目录 |
| T_MB_DISEASE_SL | 商洛 | 商洛慢特病病种目录 |
| T_MB_DISEASE_BJ | 北京 | 北京慢特病病种目录 |
| ... | ... | ... |

**核心字段**：

```java
String icdcode;        // ICD疾病编码 (国际标准)
String icdkind;        // 疾病种类
String icdtype;        // 疾病类型
String icdname;        // 疾病名称
String persontype;     // 适用人员类型
String ybcode;         // 医保系统编码
String jycode;         // 精灵系统编码
```

#### 🔗 DISEASE_MAPPING - 疾病编码映射表

**一句话理解**：不同系统之间的"翻译官"，把A系统的编码翻译成B系统的编码。

```java
String sourcecode;     // 来源编码
String targetcode;     // 目标编码
String source;         // 来源系统
String target;         // 目标系统
```

---

### 2.5 处方相关表 (Prescription)

#### 💊 T_MB_PRESCRIPTION_MAIN - 处方主表

**一句话理解**：医生开的"药方单"。

```java
String id;                 // 处方ID
String accountid;          // 患者账户ID
String name;               // 患者姓名
String idcard;             // 身份证号
String icdtype;            // 疾病类型
String icdcode;            // 病种编码
String doctor;             // 开方医生
String pharmacist;         // 审核药师
Date issue_date;           // 开方日期
String prescriptionnumber;  // 处方编号
String hospital;           // 医院名称
Integer buy_count;         // 已购药次数
String todo;               // 处理状态：0=待审核, 1=已审核
```

#### 💉 T_MB_XX_PRESCRIPTION - 各地市处方表

| 表名 | 所属地市 |
|------|---------|
| T_MB_YA_PRESCRIPTION | 延安 |
| T_MB_SL_PRESCRIPTION | 商洛 |
| T_MB_YL_PRESCRIPTION | 榆林 |
| T_MB_XYA_PRESCRIPTION | 西安 |
| T_MB_YLI_PRESCRIPTION | 宜宾 |
| ... | ... |

---

### 2.6 账户相关表 (Account)

#### 👤 VIP_ACCOUNT - 会员账户表

**一句话理解**：患者的"身份证+钱包"，存储身份信息和报销额度。

```java
String id;                 // 账户ID
String vipid;              // 会员ID (关联VIP_INFO)
String cardno;             // 会员卡号
Short status;              // 账户状态：1=新建, 2=待激活, 3=激活, 4=冻结
Short type;                // 卡类型：1=实体卡, 2=电子卡
String cardtypename;       // 卡类型名称
String gradetypename;      // 会员等级

// 慢特病相关
String icdtype;            // 病种类型
String icdcode;            // 病种编码
BigDecimal monthlimit;     // 月报销限额
BigDecimal yearlimit;      // 年报销限额

// 激活信息
String activatecode;      // 激活码
String activatename;      // 激活人
Date activatetime;        // 激活时间
```

#### 💰 VIP_ACCOUNTMBMZ - 慢特病账户表

**一句话理解**：专门记录慢特病患者的"报销账户"。

```java
String id;                 // 账户ID
String accountid;          // 关联VIP_ACCOUNT的ID
String icdkind;           // 疾病种类
String icdtype;           // 疾病类型 (1=七种病, 2=十种病)
String icdcode;           // 病种编码
String icdname;           // 病种名称
BigDecimal monthlimit;    // 月额度
BigDecimal yearlimit;     // 年额度
BigDecimal cureper;       // 治疗支付比例 (国产)
BigDecimal importcureper; // 治疗支付比例 (进口)
BigDecimal materialper;   // 材料支付比例
String cvalidate;         // 生效日期
Short status;            // 状态：1=启用, 2=停止
Short moneytype;         // 额度类型：1=月限额, 2=年限额, 3=季度限额
```

**账户余额关系图**：

```
┌─────────────────────────────────────────────┐
│              VIP_ACCOUNTMBMZ                │
│              慢特病账户                       │
├─────────────────────────────────────────────┤
│  monthlimit: 500元     ← 月额度             │
│  yearlimit: 6000元     ← 年额度             │
│  cureper: 70%          ← 报销比例(国产)     │
│  importcureper: 50%    ← 报销比例(进口)     │
└─────────────────────────────────────────────┘
              │
              │ 通过 accountid 关联
              ▼
┌─────────────────────────────────────────────┐
│              VIP_ACCOUNTMONEY               │
│              账户余额表                       │
├─────────────────────────────────────────────┤
│  money: 350.50元        ← 当前余额          │
│  monthstart: 100元      ← 月起付线          │
└─────────────────────────────────────────────┘
```

#### 💵 VIP_ACCOUNTMONEY - 账户余额表

```java
String id;             // 关联账户ID
BigDecimal money;      // 当前余额
BigDecimal points;     // 积分
String monthstart;     // 月起付线
```

---

### 2.7 药店相关表 (Drugstore)

#### 🏪 VIP_DRUGSTORE - 药店信息表

**一句话理解**：跟系统对接的"定点药房"名单。

```java
String id;             // 药店ID
String code;           // 药店编码
String name;           // 药店名称
String address;        // 详细地址
BigDecimal latitude;   // 纬度 (用于附近药店搜索)
BigDecimal longitude;  // 经度
String contact;        // 联系电话
Short status;          // 状态：0=停用, 1=启用
```

**典型SQL - 查找附近药店**：

```sql
-- 用了地球距离公式，计算两点之间的直线距离
SELECT 
    name, code, address,
    round(6378.138 * 2 * asin(
        sqrt(
            pow(sin((#{lat}*pi()/180 - lat*pi()/180)/2), 2) +
            cos(#{lat}*pi()/180) * cos(lat*pi()/180) *
            pow(sin((#{lon}*pi()/180 - lon*pi()/180)/2), 2)
        )
    ), 3) as distance
FROM vip_drugstore
WHERE dr = 0
ORDER BY distance ASC  -- 按距离排序，近的排前面
```

---

### 2.8 发卡相关表 (Card)

#### 🎴 VIP_CARD - 会员卡表

**一句话理解**：慢特病的"电子身份证"。

```java
String id;             // 卡ID
String cardno;         // 卡号
String accountid;      // 关联账户ID
Short type;            // 卡类型：1=实体卡, 2=电子卡
Short status;          // 卡状态：1=未使用, 2=已使用, 3=作废
String cardtypecode;   // 卡种编码
String cardtypename;   // 卡种名称
Short useflag;         // 使用标识
String cardpassword;   // 卡密 (实体卡)
Integer cardseq;       // 卡序列号
```

#### 📤 VIP_SENDCARD - 发卡记录表

```java
String id;             // 记录ID
String declareid;      // 申报ID
String cardid;         // 卡ID
Short status;          // 发送状态
String sendtype;       // 发送方式：1=自取, 2=邮寄
```

---

### 2.9 参保相关表 (Insurance)

#### 🏛️ GHI_INSURE_DETAIL - 参保信息表

**一句话理解**：从医保局同步过来的"参保数据"。

```java
String id;             // 主键ID
String vipid;          // 会员ID
String appntname;      // 投保人姓名
String insuredidno;    // 被保险人证件号
String insuredmobile;  // 被保险人电话
String persontype;     // 人员类型
String icdtype;        // 疾病类型
String icdcode;        // 疾病编码
String icdname;        // 疾病名称
String unitcode;       // 机构编码
String accountid;      // 账户ID
String comname;        // 保险公司名称
```

#### 📁 GHI_INSURE_FILING - 备案信息表

```java
String idcard;         // 身份证号
String icdcode;        // 病种编码
String icdname;        // 病种名称
Date startdate;        // 备案开始日期
Date enddate;          // 备案结束日期
Short status;          // 状态：0=有效, 1=无效
```

---

## 三、ER图 - 表与表的关系

### 3.1 核心ER图（文字版）

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           门诊慢特病系统 - 表关系图                           │
└──────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │   VIP_INFO      │
                              │   会员信息表     │
                              └────────┬────────┘
                                       │ 1:N (一个会员多个账户)
                                       │ vipid
                                       ▼
┌─────────────────┐             ┌─────────────────┐             ┌─────────────────┐
│  VIP_CARD       │◄────────────│  VIP_ACCOUNT    │────────────►│ VIP_ACCOUNTMBMZ │
│  会员卡表        │  cardno    │  会员账户表       │  accountid  │  慢特病账户表    │
└─────────────────┘             └────────┬────────┘             └────────┬────────┘
                                        │                               │
                                        │ 1:1                            │ 1:N
                                        │ cardno                        │ accountid
                                        ▼                               ▼
                              ┌─────────────────┐             ┌─────────────────┐
                              │ VIP_ACCOUNTMONEY│             │ T_MB_PRESCRIPTION│
                              │ 账户余额表       │             │ 处方主表         │
                              └─────────────────┘             └─────────────────┘
                                        
                                       
┌─────────────────┐      declareid      ┌─────────────────┐      accountid
│VIP_MBDECLARE_FILE│◄────────────────►│VIP_MBDECLARE_INFO│                │
│申报附件表        │                   │ 申报信息主表      │                │
└─────────────────┘                   └────────┬────────┘                │
                                               │                         │
                                               │ 1:N                     │
                                               ▼                         │
                              ┌─────────────────────────┐                  │
                              │VIP_MBDECLARE_APPROVAL  │                  │
                              │审批记录表               │                  │
                              └─────────────────────────┘                  │
                                               │                         │
                                               │ 1:1 (体检关联)          │
                                               ▼                         │
                              ┌─────────────────────────┐                  │
                              │VIP_MBDECLARE_PHYSICAL  │                  │
                              │体检分配表               │                  │
                              └─────────────────────────┘                  │
                                                                          
                                       ┌─────────────────────────┐
                                       │   GHI_INSURE_DETAIL    │
                                       │   参保信息表            │
                                       └─────────────────────────┘
                                               │
                                               │ N:1 (icdcode关联)
                                               ▼
                              ┌─────────────────────────┐
                              │   T_MB_DISEASE_XX      │
                              │   疾病目录表            │
                              └─────────────────────────┘
```

### 3.2 表关系详解

| 关系 | 主表 | 从表 | 关联字段 | 说明 |
|------|------|------|---------|------|
| 1:N | VIP_INFO | VIP_ACCOUNT | vipid | 一个会员可以有多个账户 |
| 1:1 | VIP_ACCOUNT | VIP_CARD | accountid | 一张卡绑定一个账户 |
| 1:1 | VIP_ACCOUNT | VIP_ACCOUNTMBMZ | accountid | 一个账户一种慢特病 |
| 1:N | VIP_MBDECLARE_INFO | VIP_MBDECLARE_APPROVAL | declareid | 一个申报多次审批 |
| 1:N | VIP_MBDECLARE_INFO | VIP_MBDECLARE_FILE | declareid | 一个申报多个附件 |
| 1:1 | VIP_MBDECLARE_INFO | VIP_MBDECLARE_PHYSICAL | declareid | 一个申报一次体检 |

### 3.3 主键设计

系统使用**字符串UUID**作为主键，不是自增ID：

```java
// 例如
String id;  // 值类似: "8a8a8a8a8a8a8a8a8a8a8a8a8a8a8a8"
```

**为什么用UUID而不是自增ID？**
- ✅ 分布式环境下不会冲突
- ✅ 无法从ID猜测数据量
- ❌ 查询效率略低（字符串比对 vs 整数比对）
- ❌ 主键索引占用空间大

### 3.4 逻辑删除设计

系统采用**逻辑删除**而不是物理删除：

```sql
WHERE DR = 0  -- 0=有效, 1=已删除
```

**好处**：
- 数据可以恢复
- 保留操作日志
- 符合审计要求

**坏处**：
- 查询时要记得加 `DR=0` 条件
- 容易遗漏导致查出"假数据"

---

## 四、Mapper XML深度解析

### 4.1 MyBatis是什么？

> **MyBatis = 帮你写SQL的工具**
> 
> Mapper XML就是存放SQL的"菜谱本"，告诉MyBatis："我想查什么数据，按这个格式给我。"

```
┌─────────────────────────────────────────────────────────┐
│                     Mapper XML 结构                      │
├─────────────────────────────────────────────────────────┤
│  <mapper namespace="com.xxx.dao.XXXDao">                 │
│                                                          │
│    <!-- 查询 -->                                         │
│    <select id="方法名" resultType="返回类型">            │
│        SELECT * FROM 表名 WHERE 条件                     │
│    </select>                                             │
│                                                          │
│    <!-- 新增 -->                                         │
│    <insert id="方法名">                                  │
│        INSERT INTO 表名 (字段) VALUES (值)               │
│    </insert>                                             │
│                                                          │
│    <!-- 更新 -->                                         │
│    <update id="方法名">                                  │
│        UPDATE 表名 SET 字段=值 WHERE 条件                │
│    </update>                                             │
│                                                          │
│    <!-- 删除 -->                                         │
│    <delete id="方法名">                                  │
│        DELETE FROM 表名 WHERE 条件                       │
│    </delete>                                             │
│                                                          │
│  </mapper>                                               │
└─────────────────────────────────────────────────────────┘
```

---

### 4.2 复杂查询SQL逐个拆解

#### 📝 SQL 1: 申报列表查询 (getVipMbdeclareInfoList)

**场景**：管理员查询所有申报记录

```sql
<!-- Mapper XML写法 -->
<select id="getVipMbdeclareInfoList" 
        parameterType="VipMbdeclareInfo" 
        resultType="VipMbdeclareInfo">
    SELECT
        ID, NAME, IDCARDTYPE, IDCARD, BIRTHDAY, SEX, MOBILE,
        ICDTYPE, ICDCODE, ICDNAME, PERSONTYPE,
        CASE
            WHEN APPLYSTATUS = 0 THEN 0
            WHEN APPLYSTATUS = 1 AND ORGSTATUS = 0 THEN 1
            WHEN APPLYSTATUS = 1 AND PHYSICALSTATUS = 1 THEN 6
            -- ... 更多状态判断
        END AS APPLYSTATUS,
        PHYSICALSTATUS, UNITCODE, ...
    FROM VIP_MBDECLARE_INFO
    WHERE DR = 0
        AND APPLYSTATUS <> 99
        <if test="name != null and name != ''">
            AND NAME = #{name}
        </if>
        <choose>
            <when test="userid != null and mobile != null">
                AND (MOBILE = #{mobile} OR USERID = #{userid})
            </when>
            <when test="mobile != null">
                AND MOBILE = #{mobile}
            </when>
        </choose>
        <if test="idcard != null">
            AND IDCARD = #{idcard}
        </if>
    ORDER BY CREATETIME DESC
</select>
```

**🀄 小白解读**：

> 想象你要在一堆申请表里找东西
> 
> **SELECT** = 我要"拿"这些列
> **FROM** = 从哪堆文件里找 (VIP_MBDECLARE_INFO申报表)
> **WHERE** = 筛选条件
> **CASE WHEN** = 如果...那么...的判断 (计算最终状态)
> **ORDER BY** = 按时间倒序排列 (最新的放前面)

---

#### 📝 SQL 2: 处方查询带窗口函数 (selectPrescription)

**场景**：查询患者的处方列表，并按最新处方排序

```sql
<select id="selectPrescription" resultType="PrescriptionMainDto">
    SELECT * FROM (
        SELECT
            gid.id as ghiId,
            t.id, t.accountid, t.version,
            t.doctor, t.department,
            CASE
                WHEN t.remark = 'pc' THEN '经办端'
                ELSE '小程序'
            END AS remark,
            -- 窗口函数：按accountid分组，按todo升序、createtime降序排序
            ROW_NUMBER() OVER(
                PARTITION BY t.accountid 
                ORDER BY todo ASC, createtime DESC
            ) as ghiaccountid,
            ...
        FROM (
            SELECT *,
                ROW_NUMBER() OVER(
                    PARTITION BY accountid
                    ORDER BY todo ASC, createtime DESC
                ) as aa
            FROM t_mb_prescription_main
            WHERE dr = '0'
        ) t
        LEFT JOIN vip_accountmbmz vmz ON t.accountid = vmz.accountid
        LEFT JOIN ghi_insure_detail gid ON t.accountid = gid.accountid
    ) tt
    WHERE tt.aa = '1'
</select>
```

**🀄 小白解读**：

> 这个SQL有点复杂，像是在做"分组取最新"
> 
> **ROW_NUMBER() OVER()** = 给每一行编个号
> **PARTITION BY** = 按什么分组 (每个患者一组)
> **ORDER BY** = 组内按什么排序
> 
> **简单理解**：
> - 假设你有3张处方，时间分别是1号、2号、3号
> - 加上行号后：3号=1号，2号=2号，1号=3号
> - 外层 WHERE aa = '1' 就是取每组的第一条，也就是最新的

---

#### 📝 SQL 3: 账户多表联合查询 (queryAccountForClaim)

**场景**：查询账户信息，同时展示会员资料和余额

```sql
<select id="queryAccountForClaim" resultType="VipAccountDto">
    SELECT
        vip.name, vip.sex, vip.idcard, vip.mobile,
        acc.id, acc.vipid, acc.cardno, acc.cardtypename,
        mon.money
    FROM 
        VIP_ACCOUNT acc,      -- 账户表
        VIP_INFO vip,         -- 会员表
        VIP_ACCOUNTMONEY mon   -- 余额表
    WHERE 
        acc.vipid = vip.id     -- 账户关联会员
        AND acc.id = mon.id    -- 账户关联余额
        AND acc.dr = 0         -- 账户未删除
        AND vip.dr = 0         -- 会员未删除
        AND mon.dr = 0         -- 余额未删除
        <if test="name != ''">
            AND vip.name = #{name}
        </if>
        <if test="idcard != ''">
            AND vip.idcard = #{idcard}
        </if>
</select>
```

**🀄 小白解读**：

> 这就是"表连接"，把三张表拼成一张大表
> 
> **INNER JOIN** (这里用的是老式逗号连接) = 把两张表按条件拼起来
> 
> ```
> VIP_ACCOUNT          VIP_INFO           VIP_ACCOUNTMONEY
> ┌────────────┐      ┌────────────┐     ┌────────────┐
> │ vipid=001  │──────│ id=001    │     │ id=xxx    │
> │ cardno=123 │      │ name=张三 │     │ money=500 │
> └────────────┘      └────────────┘     └────────────┘
> ```

---

#### 📝 SQL 4: 药店附近搜索 (queryNearbyDrugstores)

**场景**：根据用户GPS坐标，查找附近的定点药店

```sql
<select id="queryNearbyDrugstores" resultType="VipDrugstoreDto">
    SELECT * FROM (
        SELECT 
            name, code, address, latitude, longitude,
            -- 地球距离公式(Haversine)
            round(6378.138 * 2 * asin(sqrt(
                pow(sin((#{latitude}*pi()/180 - latitude*pi()/180)/2), 2) +
                cos(#{latitude}*pi()/180) * cos(latitude*pi()/180) *
                pow(sin((#{longitude}*pi()/180 - longitude*pi()/180)/2), 2)
            ))::numeric, 3) as distance
        FROM vip_drugstore 
        WHERE dr = 0
            <if test="name != null">
                AND name LIKE '%' || #{name} || '%'
            </if>
    ) ds
    WHERE distance < 50  -- 50公里内
    ORDER BY distance ASC
</select>
```

**🀄 小白解读**：

> 这个SQL在计算"地球表面两点间的距离"
> 
> 公式里那些sin、cos、pow就是数学里算球面距离的公式
> 
> **6378.138** = 地球半径（公里）
> 
> **结果** = 两点之间隔了多少公里
> 
> **ORDER BY distance ASC** = 最近的放前面

---

#### 📝 SQL 5: 智能审核任务分配 (selectVipIntelligentAuditErrorData)

**场景**：AI自动审核系统，分配待处理的图片识别任务

```sql
<select id="selectVipIntelligentAuditErrorData" resultType="VipIntelligentAuditFileDto">
    SELECT
        vmf.id as fileId,
        vmf.declareid,
        vmf.filepath,
        vif.iqi, vif.mic, vif.idcard
    FROM (
        SELECT *
        FROM vip_intelligent_audit via
        WHERE via.state = '0'  -- 待处理状态
            <if test="vipIntelligentAudit.iqi != null">
                AND via.iqi = #{vipIntelligentAudit.iqi}
            </if>
            <if test="vipIntelligentAudit.idcard != null">
                AND via.idcard = #{vipIntelligentAudit.idcard}
            </if>
        ORDER BY via.createtime DESC
        LIMIT #{limit}  -- 限制条数
    ) vif
    LEFT JOIN vip_mbdeclare_file vmf ON vmf.declareid = vif.declareid
    WHERE vmf.dr = '0'
</select>
```

**🀄 小白解读**：

> 这是在为AI审核系统准备"待处理任务清单"
> 
> 1. 先从智能审核表找出状态=待处理(state=0)的记录
> 2. 再关联附件表，获取需要识别的图片
> 3. 限制返回条数，避免一次处理太多
> 
> **state=0** 可能是指 IQI图片质量检测未通过，需要人工复核

---

### 4.3 动态SQL语法

MyBatis支持"动态拼接SQL"，根据条件决定加不加某些字段。

```xml
<!-- if标签：条件成立才加这段 -->
<if test="name != null and name != ''">
    AND NAME = #{name}
</if>

<!-- choose/when/otherwise：类似switch-case -->
<choose>
    <when test="type == 'A'">
        AND type = 'A'
    </when>
    <when test="type == 'B'">
        AND type = 'B'
    </when>
    <otherwise>
        AND type IN ('A', 'B')
    </otherwise>
</choose>

<!-- foreach：循环拼接 -->
<foreach collection="ids" open="(" close=")" separator=",">
    #{item}
</foreach>
<!-- 结果：('1','2','3','4') -->
```

---

## 五、SQL性能分析

### 5.1 常见性能问题一览

| 问题类型 | 表现 | 影响 | 解决思路 |
|---------|------|------|---------|
| **全表扫描** | WHERE条件没索引 | 查全量数据，慢 | 加索引 |
| **N+1查询** | 循环查关联数据 | 查询次数暴增 | 改成JOIN |
| **缺少LIMIT** | 查出太多数据 | 内存溢出 | 加分页 |
| **SELECT *** | 取了不需要的字段 | 网络传输慢 | 只查需要的字段 |
| **函数运算** | WHERE里用函数 | 索引失效 | 改写成区间查询 |
| **子查询** | 嵌套太深 | 优化器难优化 | 改成JOIN |

### 5.2 问题SQL详解

#### ⚠️ 问题1: 模糊查询导致全表扫描

```sql
-- 低效写法：LIKE开头，导致索引失效
WHERE unitcode LIKE '%' || #{unitcode} || '%'

-- 优化写法：只追后缀，能用索引
WHERE unitcode LIKE #{unitcode} || '%'
```

#### ⚠️ 问题2: 子查询代替JOIN

```sql
-- 低效写法：子查询在WHERE里，每行都要执行一次
SELECT * FROM VIP_ACCOUNT
WHERE VIPID IN (
    SELECT VIPID FROM VIP_ACCOUNT 
    WHERE CARDNO = #{cardno}
)

-- 优化写法：改成JOIN
SELECT a.* FROM VIP_ACCOUNT a
INNER JOIN VIP_ACCOUNT b ON a.VIPID = b.VIPID
WHERE b.CARDNO = #{cardno}
```

#### ⚠️ 问题3: 没有分页限制

```sql
-- 低效写法：没LIMIT，可能查出上百万条
SELECT * FROM t_mb_prescription_main

-- 优化写法：加分页
SELECT * FROM t_mb_prescription_main
LIMIT 20 OFFSET 0
```

### 5.3 性能学习要点清单

```
┌─────────────────────────────────────────────────────────────────┐
│                     SQL性能优化检查清单                          │
├─────────────────────────────────────────────────────────────────┤
│ □ WHERE条件字段是否有索引？                                      │
│ □ 是否需要加LIMIT分页？                                         │
│ □ 是否用SELECT * 了？（改成只查需要的字段）                       │
│ □ WHERE条件里是否用了函数？（改区间查询）                         │
│ □ 是否有多表JOIN？（确保ON条件有索引）                           │
│ □ 模糊查询是否用了前置通配符 '%xxx'？（改后置）                   │
│ □ 排序字段是否有索引？                                           │
│ □ 关联查询数据量是否太大？（考虑分批处理）                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 六、设计建议与优化

### 6.1 架构学习要点

#### 1. 分库分表策略

当前213个Mapper，数据都存在一个大库里，建议考虑：

```
当前架构：
┌─────────────────────────────┐
│        VIP_MBDECLARE_INFO   │
│        (所有地市数据)         │
└─────────────────────────────┘

优化后：
┌─────────────────┬─────────────────┬─────────────────┐
│  VIP_MBDECLARE_ │  VIP_MBDECLARE_ │  VIP_MBDECLARE_ │
│  INFO_BJ        │  INFO_YA        │  INFO_SL        │
│  (北京)          │  (延安)          │  (商洛)          │
└─────────────────┴─────────────────┴─────────────────┘
```

#### 2. 冷热数据分离

```sql
-- 常用数据放热库，历史数据归档到冷库
-- 最近1年的申报数据 = 热数据
-- 超过1年的 = 冷数据，可归档
```

#### 3. 索引优化

必须加索引的字段：

```sql
-- 申报表：按申报状态查询
CREATE INDEX idx_declare_applystatus ON VIP_MBDECLARE_INFO(APPLYSTATUS) WHERE DR = 0;

-- 申报表：按机构查询
CREATE INDEX idx_declare_unitcode ON VIP_MBDECLARE_INFO(UNITCODE);

-- 申报表：按申报时间排序
CREATE INDEX idx_declare_createtime ON VIP_MBDECLARE_INFO(CREATETIME);

-- 账户表：按卡号查询
CREATE INDEX idx_account_cardno ON VIP_ACCOUNT(CARDNO) WHERE DR = 0;

-- 账户表：按会员ID查询
CREATE INDEX idx_account_vipid ON VIP_ACCOUNT(VIPID) WHERE DR = 0;
```

### 6.2 安全加固建议

#### 1. 敏感字段加密

系统已对敏感字段加密，但建议定期更换密钥：

```java
@SensitiveEncrypt  // 已加注解标记
private String idcard;  // 身份证号

@SensitiveEncrypt
private String mobile;  // 手机号

@SensitiveEncrypt
private String name;    // 姓名
```

#### 2. SQL注入防护

MyBatis使用 `#{}` 参数化查询，可以防止SQL注入：

```sql
-- 安全写法 ✅
WHERE name = #{name}

-- 危险写法 ❌ (绝对不要用)
WHERE name = '${name}'  -- 字符串拼接，可能被注入
```

### 6.3 总结

```
┌─────────────────────────────────────────────────────────────────┐
│                      PICC慢特病系统 - 数据层总结                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📊 数据规模                                                     │
│     • 213个Mapper，260+个PO类                                    │
│     • 覆盖13个地市的慢特病业务                                    │
│                                                                  │
│  🎯 核心业务                                                     │
│     • 申报→审批→发卡 全流程                                      │
│     • 账户→额度→处方→购药 资金流                                 │
│     • 参保→备案→审核 医保对接                                   │
│                                                                  │
│  ⚠️ 优化方向                                                     │
│     • 索引优化：高频查询字段加索引                                │
│     • 分库分表：按地市拆分数据                                    │
│     • 冷热分离：历史数据归档                                      │
│     • 监控告警：慢查询监控                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📖 附录：字段速查表

### 状态字段含义速查

| 字段 | 表 | 可能的值 | 含义 |
|------|-----|---------|------|
| DR | 所有表 | 0, 1 | 逻辑删除：0=有效, 1=删除 |
| APPLYSTATUS | VIP_MBDECLARE_INFO | 0-11 | 申报状态 |
| PHYSICALSTATUS | VIP_MBDECLARE_INFO | 0-5 | 体检状态 |
| ORGSTATUS | VIP_MBDECLARE_INFO | 0, 1 | 机构分配状态 |
| ENDSTATUS | VIP_MBDECLARE_INFO | 0, 1 | 结案状态 |
| APPROVALSTATUS | VIP_MBDECLARE_APPROVAL | 0, 1 | 审批状态：通过/驳回 |
| STATUS | VIP_ACCOUNT | 1, 2, 3, 4 | 账户状态 |
| STATUS | VIP_CARD | 1, 2, 3 | 卡状态 |
| TYPE | VIP_CARD | 1, 2 | 卡类型：实体卡/电子卡 |

### 常用时间字段

| 字段 | 说明 |
|------|------|
| CREATETIME | 创建时间 |
| MODIFYTIME | 最后修改时间 |
| DECLAREDATE | 申报时间 |
| APPROVALDATE | 审批时间 |
| FIRSTOPERDATE | 初审时间 |
| SECONDOPERDATE | 专家审批时间 |
| ACTIVATETIME | 激活时间 |
| ISSUE_DATE | 处方开具时间 |
| INPUTTIME | 录入时间 |

---

> 📝 **文档信息**
> - 版本：v1.0
> - 生成时间：2024年
> - 适用版本：picc-mzmtb-server
> - 技术栈：Spring Boot + MyBatis + GaussDB

---

📎 **延伸阅读**：
- [API接口全景](picc-mzmtb-server-API接口全景.md) - 213个Mapper对应的API接口层调用关系
- [架构解析](picc-mzmtb-server-架构解析.md) - 数据库连接池配置、Druid监控等运维相关内容
- [picc-mzmtb-user-数据库ER图与表结构.md](picc-mzmtb-user-数据库ER图与表结构.md) 📌(权限服务) - 权限服务的17张数据库表详解

