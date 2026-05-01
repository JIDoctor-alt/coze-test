# PICC门诊慢特病业务管理系统 - 项目全貌扫描

> 📖 **相关文档**：[教程总纲索引](picc-mzmtb-server-教程文档.md) · [架构解析](picc-mzmtb-server-架构解析.md) · [申报流程解析](picc-mzmtb-server-申报流程解析.md) · [API接口全景](picc-mzmtb-server-API接口全景.md)

> 🎯 项目全称：门诊慢特病业务管理信息系统-业务服务（picc-mzmtb-server）
> 📅 扫描日期：2026年4月30日
> 🔧 技术栈：Spring Boot + MyBatis + Activiti6 + GaussDB + Redis + Apollo + K8s

---

## 一、项目规模对比

| 指标 | picc-mzmtb-user（权限服务） | picc-mzmtb-server（业务服务） | 对比 |
|------|---------------------------|-----------------------------|------|
| Java文件数 | 136 | **2647** | **19倍** |
| Mapper XML | 17 | **213** | 12倍 |
| Service接口 | 12 | **187+385** | 48倍 |
| API类 | 6 | **59+** | 10倍 |
| 业务模块 | 1（权限管理） | **11+13子模块** | - |
| 服务端口 | 9092 | **9091** | - |

---

## 二、Maven模块结构

```
picc-mzmtb-server/
├── picchealth-db/          ← 数据库模块（DAO + PO + Mapper XML）
├── picchealth-server/      ← 主服务模块（API + Service + VO）
│   └── module/
│       ├── mb/             ← 慢病核心业务（833个Java文件，绝对主力）
│       ├── webservice/     ← 外部接口对接（94个Java文件）
│       ├── restful/        ← RESTful接口（77个Java文件）
│       ├── scheduling/     ← 定时任务（27个Java文件）
│       ├── thirdfee/       ← 第三方费用（25个Java文件）
│       ├── drugstore/      ← 药店管理（20个Java文件）
│       ├── basedoc/        ← 基础文档（10个Java文件）
│       ├── mtb/            ← 慢病通用（8个Java文件）
│       ├── dpview/         ← 数据展示（4个Java文件）
│       ├── logaudit/       ← 日志审计（4个Java文件）
│       └── call/           ← 外部调用（2个Java文件）
└── mtb-yh/                 ← 地市差异化模块（13个子模块！）
    ├── mtb-base/           ← 地市通用基类（674个Java文件）
    ├── mtb-xya/            ← 咸阳地市（13个Java文件）
    ├── mtb-jc/             ← 晋城地市（11个Java文件）
    ├── mtb-yli/            ← 玉林地市（10个Java文件）
    ├── mtb-jj/             ← 九江地市（9个Java文件）
    ├── mtb-dz/             ← 达州地市（8个Java文件）
    ├── mtb-mzl/            ← 毛嘴林地市（6个Java文件）
    ├── mtb-ya/             ← 延安地市（4个Java文件）
    ├── mtb-yl/             ← 榆林地市（4个Java文件）
    ├── mtb-sl/             ← 商洛地市（4个Java文件）
    ├── mtb-bj/             ← 宝鸡地市（2个Java文件）
    ├── mtb-dez/            ← 德州地市（2个Java文件）
    └── mtb-hn/             ← 海南地市（2个Java文件）
```

---

## 三、核心业务模块（mb）概览

### mb模块是整个系统的心脏，包含：

| 子领域 | Service数 | 功能 |
|--------|----------|------|
| 申报管理 | ~20 | VipMbdeclareInfo、FirstTrial、Review... |
| 慢病卡管理 | ~15 | VipAccount、MbmzStatus、SendCard... |
| 处方管理 | ~10 | Prescription、DrugCollect、DrugForm... |
| 费用管理 | ~10 | VipMoneyflow、ChronicPay、Pay... |
| 智能审核 | ~8 | VipIntelligent、Audit、Mapping、Model... |
| 医保对接 | ~8 | MedicalInsurance、SxMedicare、YABusiness... |
| 工作流 | ~5 | ActivitiService、BusinessService... |
| 药店管理 | ~5 | VipDrugstore、Order、Product... |
| 数据统计 | ~5 | MbDataStatistics、ExcelService... |
| 专家管理 | ~5 | VipMbdeclareInfoExpert... |
| 外部对接 | ~10 | CallCxcf、CallFace、CallJksc、CallLxbx... |

---

## 四、与权限服务的关联

```
picc-mzmtb-server (9091) ←→ picc-mzmtb-user (9092)
       业务服务                    权限服务
       
调用关系：
- 业务服务通过Feign调用权限服务的用户/角色/菜单接口
- ApiInterceptor从权限服务获取URL权限列表
- Token校验可能走同一个Redis
```

---

## 五、解析策略

由于项目规模巨大（2647个Java文件），不可能像权限服务那样逐方法拆解。
采用**分层递进**策略：

1. **第一层：项目架构** — 技术栈、模块划分、外部依赖、部署架构
2. **第二层：核心业务流** — 申报全流程、审核流程（Activiti）、处方流程
3. **第三层：关键模块解析** — mb模块Top20核心Service、地市差异化机制
4. **第四层：接口层** — 59个API类分类解析
5. **第五层：数据模型** — 213个Mapper XML对应的核心表
6. **第六层：安全与质量** — 安全审计、代码质量、性能问题

---

📎 **延伸阅读**：
- [架构解析](picc-mzmtb-server-架构解析.md) - 技术栈、Spring Boot配置、Activiti工作流集成的详细说明
- [申报流程解析](picc-mzmtb-server-申报流程解析.md) - 慢特病申报全生命周期、状态机流转的完整流程
- [API接口全景](picc-mzmtb-server-API接口全景.md) - 894个接口按业务域分类的完整清单
