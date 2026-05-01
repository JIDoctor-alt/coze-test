# PICC慢病管理项目全景导航文档

> **版本**: v5.0 (五轮深度扫描汇总)  
> **更新日期**: 2024年  
> **文件总数**: 64个  
> **总行数**: 69,952行  
> **覆盖范围**: 4个项目 + 跨项目文档

---

## 一、四服务架构概览

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           PICC慢病管理系统架构                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│    ┌─────────────────┐                                                         │
│    │  picc-mzmtb-agent │  (前端门户, 端口 80/443)                              │
│    │   Vue.js + Vuex   │◄────────────┐                                         │
│    │   15+通用组件     │             │                                         │
│    └────────┬─────────┘             │                                         │
│             │ HTTP/REST             │                                         │
│             ▼                       │                                         │
│    ┌─────────────────┐             │                                         │
│    │ picc-mzmtb-gateway│ (网关服务, 端口 9001)                                 │
│    │  统一入口/路由    │─────────────┼──────────────────┐                      │
│    │  安全防护/限流    │             │                  │                      │
│    └────────┬─────────┘             │                  │                      │
│             │                       │                  │                      │
│    ┌────────┴────────┐             │                  │                      │
│    │ Feign/HTTP       │             │                  │                      │
│    ▼                  ▼             │                  │                      │
│ ┌─────────────────┐  ┌─────────────────┐              │                      │
│ │ picc-mzmtb-server│  │picc-mzmtb-user │              │                      │
│ │ (业务服务,9091)   │  │ (权限服务,9092) │              │                      │
│ │                  │  │                 │              │                      │
│ │ • 申报管理       │  │ • 用户管理      │              │                      │
│ │ • 处方管理       │  │ • 角色权限      │◄─────────────┘                      │
│ │ • BPMN工作流     │  │ • 菜单系统      │                                      │
│ │ • 26定时任务     │  │ • Spring Security│                                     │
│ │ • 地市差异化     │  │                 │                                      │
│ └─────────────────┘  └─────────────────┘                                      │
│                                                                                 │
│    ┌─────────────────────────────────────────┐                                │
│    │              共享基础设施                │                                │
│    │  • Redis (40+缓存Key)  • MySQL          │                                │
│    │  • 消息队列           • 文件存储        │                                │
│    └─────────────────────────────────────────┘                                │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 二、项目总览

| 项目名称 | 技术栈 | 端口 | 核心职责 | 文档数 |
|---------|--------|------|---------|--------|
| picc-mzmtb-agent | Vue.js + Vuex | 80/443 | 前端门户/用户交互 | 12 |
| picc-mzmtb-gateway | Spring Cloud Gateway | 9001 | 统一入口/路由/安全 | 10 |
| picc-mzmtb-server | Spring Boot + BPMN | 9091 | 业务逻辑/申报流程/工作流 | 19 |
| picc-mzmtb-user | Spring Security | 9092 | 权限管理/用户认证 | 16 |
| **跨项目文档** | - | - | 架构/安全/部署/测试 | 7 |

---

## 三、按项目分类文档清单

### 3.1 项目1：权限服务 (picc-mzmtb-user)

**服务端口**: 9092 | **核心框架**: Spring Security + MyBatis Plus

| 轮次 | 文档名称 | 核心内容 | 行数 |
|-----|---------|---------|-----|
| 1 | picc-mzmtb-user-教程文档.md | 总纲索引，文档导航入口 | - |
| 1 | picc-mzmtb-user-架构设计文档.md | 整体架构设计与模块划分 | - |
| 1 | picc-mzmtb-user-深度解析.md | 核心模块深度分析 | - |
| 1 | picc-mzmtb-user-深度解析第二章.md | 第二章内容 | - |
| 1 | picc-mzmtb-user-深度解析第三章-角色管理.md | 角色管理全流程 | - |
| 1 | picc-mzmtb-user-深度解析第四章-菜单与系统管理.md | 菜单系统与系统配置 | - |
| 1 | picc-mzmtb-user-补充方法解析.md | 补充方法说明 | - |
| 1 | picc-mzmtb-user-深度解析补充-辅助模块.md | 辅助功能模块解析 | - |
| 1 | picc-mzmtb-user-API-Mapper-数据模型.md | API与Mapper层分析 | - |
| 1 | picc-mzmtb-user-数据库ER图与表结构.md | 数据库设计与ER图 | - |
| 1 | picc-mzmtb-user-配置部署依赖.md | 配置文件与部署指南 | - |
| 2 | picc-mzmtb-user-安全问题分析.md | 安全问题问题分析 | - |
| 2 | picc-mzmtb-user-安全修复工单.md | 安全修复工单详情 | - |
| 2 | picc-mzmtb-user-安全问题原理学习文档.md | 问题原理实现 | - |
| 1 | picc-mzmtb-user-Onboarding手册.md | 新人入门指南 | - |
| 4 | picc-mzmtb-user-方法级深度解析II.md | **17个核心方法+Spring Security逻辑** | - |

**项目亮点**:
- 完善的Spring Security权限体系
- 角色-菜单-权限三级管理
- 细粒度的数据权限控制

---

### 3.2 项目2：业务服务 (picc-mzmtb-server)

**服务端口**: 9091 | **核心框架**: Spring Boot + Activiti BPMN

| 轮次 | 文档名称 | 核心内容 | 行数 |
|-----|---------|---------|-----|
| 1 | picc-mzmtb-server-教程文档.md | 总纲索引 | - |
| 1 | picc-mzmtb-server-项目全貌.md | 项目整体介绍 | - |
| 1 | picc-mzmtb-server-架构解析.md | 架构设计与模块划分 | - |
| 1 | picc-mzmtb-server-API接口全景.md | 全量API接口列表 | - |
| 1 | picc-mzmtb-server-申报流程解析.md | 申报业务流程详解 | - |
| 1 | picc-mzmtb-server-数据模型解析.md | 核心数据模型分析 | - |
| 1 | picc-mzmtb-server-安全与代码质量审计.md | 安全问题与代码质量报告 | - |
| 1 | picc-mzmtb-server-地市差异化机制.md | 地市差异化配置实现 | - |
| 1 | picc-mzmtb-server-处方与药店管理解析.md | 处方药店模块分析 | - |
| 1 | picc-mzmtb-server-Onboarding手册.md | 新人入门指南 | - |
| 2 | picc-mzmtb-server-安全修复工单.md | 安全修复工单 | - |
| 2 | picc-mzmtb-server-安全问题原理学习文档.md | 安全问题原理 | - |
| 2 | picc-mzmtb-server-核心Service方法级解析.md | **10个Service/35+方法** | - |
| 2 | picc-mzmtb-server-工作流与外部对接解析.md | **13个BPMN+4外部系统+26定时任务** | - |
| 3 | picc-mzmtb-server-定时任务详解.md | 定时任务全面解析 | 1540 |
| 3 | picc-mzmtb-server-核心Service方法级解析II.md | **12个Service深度解析** | - |
| 4 | picc-mzmtb-server-数据字典与状态码.md | **60+枚举/100+状态码** | - |
| 5 | picc-mzmtb-server-缓存策略详解.md | **40+Redis Key设计** | - |
| 5 | picc-mzmtb-server-核心接口文档.md | **50+接口完整文档** | - |

**项目亮点**:
- 完整的BPMN工作流引擎集成
- 26个定时任务的精细调度
- 地市差异化配置支持
- 40+Redis缓存Key设计

---

### 3.3 项目3：前台服务 (picc-mzmtb-gateway)

**服务端口**: 9001 | **核心框架**: Spring Cloud Gateway

| 轮次 | 文档名称 | 核心内容 | 行数 |
|-----|---------|---------|-----|
| 1 | picc-mzmtb-gateway-教程文档.md | 总纲索引 | - |
| 1 | picc-mzmtb-gateway-项目全貌与架构解析.md | 架构设计与全貌 | - |
| 1 | picc-mzmtb-gateway-API接口全景.md | API接口全景 | - |
| 1 | picc-mzmtb-gateway-安全与代码质量审计.md | 安全审计报告 | - |
| 1 | picc-mzmtb-gateway-Service与VO层解析.md | Service与VO层分析 | - |
| 1 | picc-mzmtb-gateway-通信机制与三服务联动.md | 服务间通信机制 | - |
| 1 | picc-mzmtb-gateway-Onboarding手册.md | 新人入门指南 | - |
| 2 | picc-mzmtb-gateway-安全修复工单.md | **11个工单/4个P0问题** | - |
| 2 | picc-mzmtb-gateway-安全问题原理学习文档.md | **4个P0问题原理** | - |
| 5 | picc-mzmtb-gateway-核心Service方法级解析.md | **12个Service逐方法拆解** | - |

**项目亮点**:
- 三服务统一入口
- 4个P0级安全问题的彻底修复
- 完善的服务间通信机制

---

### 3.4 项目4：前端门户 (picc-mzmtb-agent)

**服务端口**: 80/443 | **核心框架**: Vue.js + Vuex

| 轮次 | 文档名称 | 核心内容 | 行数 |
|-----|---------|---------|-----|
| 1 | picc-mzmtb-agent-教程文档.md | 总纲索引 | - |
| 1 | picc-mzmtb-agent-项目全貌与架构解析.md | 前端架构全解析 | - |
| 1 | picc-mzmtb-agent-API层与路由解析.md | API调用与路由设计 | - |
| 1 | picc-mzmtb-agent-地市差异化与组件解析.md | 地市差异化实现 | - |
| 1 | picc-mzmtb-agent-Onboarding手册.md | 前端新人指南 | - |
| 2 | picc-mzmtb-agent-安全与性能审计.md | **8安全+5性能问题** | - |
| 2 | picc-mzmtb-agent-核心页面深度解析.md | **10个核心页面** | - |
| 3 | picc-mzmtb-agent-安全修复工单.md | **9个安全问题修复工单** | - |
| 3 | picc-mzmtb-agent-安全问题原理学习文档.md | 安全问题原理 | - |
| 3 | picc-mzmtb-agent-前端性能优化.md | **8大优化方向** | - |
| 4 | picc-mzmtb-agent-组件封装与复用指南.md | **15+通用组件** | - |
| 5 | picc-mzmtb-agent-Vuex状态管理深度解析.md | **架构评分2/5** | - |

**项目亮点**:
- 15+可复用通用组件
- 8大前端性能优化方向
- 完善的地市差异化配置

---

### 3.5 跨项目文档

| 轮次 | 文档名称 | 核心内容 | 行数 |
|-----|---------|---------|-----|
| 1 | PICC双服务关联关系.md | 用户-业务服务关联 | - |
| 1 | PICC三服务关联关系.md | 网关+双服务关联 | - |
| 2 | PICC四服务全景架构.md | **30+架构图/1901行** | 1901 |
| 3 | PICC四项目安全审计总报告.md | **等保2.0评估/3月路线图/1290行** | 1290 |
| 4 | PICC四项目API错误码与异常处理.md | **1508行** | 1508 |
| 4 | PICC四项目CI-CD与部署指南.md | **2243行** | 2243 |
| 5 | PICC四项目测试体系分析.md | **1986行** | 1986 |

---

## 四、新手推荐阅读路径

### 🚀 入门三步曲（建议按顺序阅读）

```
第一步：了解全局架构
├── PICC四服务全景架构.md          ⭐ 必读 - 30+架构图建立全局视野
└── PICC四服务关联关系.md            参考 - 服务间调用关系

第二步：选定项目深入
├── 前端方向：
│   ├── picc-mzmtb-agent-项目全貌与架构解析.md
│   ├── picc-mzmtb-agent-Onboarding手册.md
│   └── picc-mzmtb-agent-组件封装与复用指南.md
│
├── 后端方向（业务服务）：
│   ├── picc-mzmtb-server-项目全貌.md
│   ├── picc-mzmtb-server-Onboarding手册.md
│   └── picc-mzmtb-server-申报流程解析.md
│
├── 后端方向（权限服务）：
│   ├── picc-mzmtb-user-架构设计文档.md
│   ├── picc-mzmtb-user-Onboarding手册.md
│   └── picc-mzmtb-user-数据库ER图与表结构.md
│
└── 网关方向：
    ├── picc-mzmtb-gateway-项目全貌与架构解析.md
    ├── picc-mzmtb-gateway-通信机制与三服务联动.md
    └── picc-mzmtb-gateway-Onboarding手册.md

第三步：掌握核心功能
├── picc-mzmtb-server-工作流与外部对接解析.md    (BPMN工作流)
├── picc-mzmtb-server-定时任务详解.md            (26个定时任务)
├── picc-mzmtb-server-数据字典与状态码.md         (枚举/状态码)
└── picc-mzmtb-server-缓存策略详解.md            (Redis缓存)
```

---

## 五、按角色推荐阅读路径

### 👨‍💻 开发工程师

| 优先级 | 文档名称 | 理由 |
|-------|---------|-----|
| **P0** | picc-mzmtb-server-核心Service方法级解析.md | 35+核心方法实现 |
| **P0** | picc-mzmtb-server-核心Service方法级解析II.md | 12个Service深度解析 |
| **P0** | picc-mzmtb-user-方法级深度解析II.md | 17个核心方法+Security |
| **P0** | picc-mzmtb-gateway-核心Service方法级解析.md | 12个Service拆解 |
| P1 | picc-mzmtb-server-申报流程解析.md | 业务流程理解 |
| P1 | picc-mzmtb-server-工作流与外部对接解析.md | BPMN+外部系统 |
| P1 | picc-mzmtb-server-定时任务详解.md | 定时任务调度 |
| P1 | picc-mzmtb-agent-核心页面深度解析.md | 前端核心页面 |
| P2 | picc-mzmtb-server-地市差异化机制.md | 差异化配置 |
| P2 | picc-mzmtb-agent-地市差异化与组件解析.md | 前端差异化 |
| P2 | picc-mzmtb-server-数据模型解析.md | 数据模型设计 |

---

### 🛡️ 安全工程师

| 优先级 | 文档名称 | 理由 |
|-------|---------|-----|
| **P0** | PICC四项目安全审计总报告.md | **等保2.0评估/3月路线图** |
| **P0** | picc-mzmtb-gateway-安全修复工单.md | 4个P0+11工单 |
| **P0** | picc-mzmtb-gateway-安全问题原理学习文档.md | P0问题原理 |
| P1 | picc-mzmtb-server-安全与代码质量审计.md | 业务服务安全 |
| P1 | picc-mzmtb-gateway-安全与代码质量审计.md | 网关安全 |
| P1 | picc-mzmtb-agent-安全与性能审计.md | 前端安全8问题 |
| P1 | picc-mzmtb-agent-安全修复工单.md | 9个安全问题 |
| P2 | picc-mzmtb-user-安全问题分析.md | 权限服务安全 |
| P2 | picc-mzmtb-server-安全修复工单.md | 业务服务安全修复 |

---

### 🚀 运维工程师

| 优先级 | 文档名称 | 理由 |
|-------|---------|-----|
| **P0** | PICC四项目CI-CD与部署指南.md | **2243行完整部署文档** |
| **P0** | picc-mzmtb-server-缓存策略详解.md | 40+Redis Key设计 |
| P1 | picc-mzmtb-server-定时任务详解.md | 26个定时任务 |
| P1 | picc-mzmtb-user-配置部署依赖.md | 权限服务配置 |
| P1 | PICC四服务关联关系.md | 服务依赖关系 |
| P2 | picc-mzmtb-server-工作流与外部对接解析.md | 外部系统对接 |
| P2 | picc-mzmtb-agent-前端性能优化.md | 前端性能调优 |

---

### 🧪 测试工程师

| 优先级 | 文档名称 | 理由 |
|-------|---------|-----|
| **P0** | PICC四项目测试体系分析.md | **1986行测试体系** |
| **P0** | picc-mzmtb-server-核心接口文档.md | 50+接口完整文档 |
| P1 | PICC四项目API错误码与异常处理.md | **1508行错误码** |
| P1 | picc-mzmtb-server-API接口全景.md | 全量接口列表 |
| P1 | picc-mzmtb-gateway-API接口全景.md | 网关接口 |
| P2 | picc-mzmtb-agent-API层与路由解析.md | 前端API调用 |
| P2 | picc-mzmtb-server-数据字典与状态码.md | 60+枚举/100+状态码 |

---

### 📊 项目经理/架构师

| 优先级 | 文档名称 | 理由 |
|-------|---------|-----|
| **P0** | PICC四服务全景架构.md | **30+架构图/1901行** |
| **P0** | PICC四项目安全审计总报告.md | **等保2.0评估** |
| P1 | PICC四项目CI-CD与部署指南.md | 部署与运维 |
| P1 | PICC四项目测试体系分析.md | 测试策略 |
| P1 | picc-mzmtb-server-架构解析.md | 业务服务架构 |
| P2 | picc-mzmtb-gateway-项目全貌与架构解析.md | 网关架构 |

---

## 六、文档统计总览

### 6.1 按轮次分布

| 轮次 | 项目文档数 | 跨项目文档数 | 合计 |
|-----|----------|------------|-----|
| 第一轮 | 24 | 3 | 27 |
| 第二轮 | 12 | 1 | 13 |
| 第三轮 | 9 | 1 | 10 |
| 第四轮 | 5 | 2 | 7 |
| 第五轮 | 5 | 1 | 6 |
| **总计** | **55** | **8** | **64** |

### 6.2 按项目分布

| 项目 | 文档数 | 占比 |
|-----|-------|-----|
| picc-mzmtb-server (业务服务) | 19 | 29.7% |
| picc-mzmtb-user (权限服务) | 16 | 25.0% |
| picc-mzmtb-gateway (网关服务) | 10 | 15.6% |
| picc-mzmtb-agent (前端门户) | 12 | 18.8% |
| 跨项目文档 | 7 | 10.9% |
| **合计** | **64** | **100%** |

### 6.3 核心亮点文档

| 类别 | 文档名称 | 亮点 |
|-----|---------|-----|
| 🔥 最详细 | picc-mzmtb-server-定时任务详解.md | 1540行，26个定时任务 |
| 🔥 最大全貌 | PICC四服务全景架构.md | 1901行，30+架构图 |
| 🔥 最安全 | PICC四项目安全审计总报告.md | 等保2.0评估，1290行 |
| 🔥 最部署 | PICC四项目CI-CD与部署指南.md | 2243行，完整CI/CD |
| 🔥 最测试 | PICC四项目测试体系分析.md | 1986行，测试策略 |
| 🔥 最API | PICC四项目API错误码与异常处理.md | 1508行，100+状态码 |
| 🔥 最接口 | picc-mzmtb-server-核心接口文档.md | 50+接口完整文档 |
| 🔥 最缓存 | picc-mzmtb-server-缓存策略详解.md | 40+Redis Key |

---

## 七、快速索引

### 按关键字快速查找

| 关键字 | 相关文档 |
|-------|---------|
| **Spring Security** | picc-mzmtb-user-方法级深度解析II.md |
| **BPMN/工作流** | picc-mzmtb-server-工作流与外部对接解析.md |
| **定时任务** | picc-mzmtb-server-定时任务详解.md |
| **Redis缓存** | picc-mzmtb-server-缓存策略详解.md |
| **枚举/状态码** | picc-mzmtb-server-数据字典与状态码.md |
| **等保2.0** | PICC四项目安全审计总报告.md |
| **CI/CD** | PICC四项目CI-CD与部署指南.md |
| **Vuex** | picc-mzmtb-agent-Vuex状态管理深度解析.md |
| **地市差异化** | picc-mzmtb-server-地市差异化机制.md |
| **P0安全修复** | picc-mzmtb-gateway-安全问题原理学习文档.md |

---

## 八、文档更新记录

| 版本 | 日期 | 更新内容 |
|-----|------|---------|
| v1.0 | - | 第一轮扫描完成，基础文档框架 |
| v2.0 | - | 第二轮扫描，安全修复文档+全景架构 |
| v3.0 | - | 第三轮扫描，等保报告+定时任务详解 |
| v4.0 | - | 第四轮扫描，CI/CD+错误码+数据字典 |
| v5.0 | - | 第五轮扫描，测试体系+缓存策略+核心接口 |

---

> 📌 **提示**: 本文档为PICC慢病管理项目的全景导航，所有详细文档请查阅对应文件。
> 
> 🔗 **相关链接**: [返回顶部](#picc慢病管理项目全景导航文档)
