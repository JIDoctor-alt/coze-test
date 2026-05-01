## picc-mzmtb-gateway 项目 - 已完成
- ✅ 通信机制与三服务联动、安全审计、API全景、Onboarding手册、三服务关联关系
- ✅ 总纲索引文档（160行，含导航表、数字速查、阅读路径、核心发现摘要）
- ✅ API接口全景文档从291行扩充到484行，新增完整API类清单（104类）和核心发现总结
- ✅ 文档：通信机制(808行)、安全审计(734行,20问题/4致命)、API全景(484行,11业务域+完整API清单)、Onboarding(1015行)、三服务关联关系(新增，替代双服务版本，文档路径：./PICC三服务关联关系.md)、总纲索引(160行，路径：./picc-mzmtb-gateway-教程文档.md)

## picc-mzmtb-server 项目 - 已完成
- ✅ 项目全貌、架构解析(782行)、API全景(1016行,894接口)、申报流程(1164行)、数据模型(1159行,213Mapper)、安全审计(1348行,33问题)、地市差异化(771行)、处方药店(1124行)、总纲索引、Onboarding(760行)、三服务关联(新增，替代双服务版本，文档路径：./PICC三服务关联关系.md)
- ✅ 安全修复工单(1322行)+实现文档(2127行)、25个文档交叉引用优化、3个薄弱文档充实v2

## 关键任务
1. 榆林慢病管理模块敏感信息导出权限控制（进行中 - 需要确认具体需求）
2. RAGFLOW PLUS项目Logo设计（已完成）
3. 专家分配后短信发送接口实现（已完成）
4. RAGFLOW PLUS集成wiki功能（进行中 - 已完成对比分析）
5. 企业级知识库平台项目（开发阶段 - 基础框架已完成，待MinerU集成、RAG增强、前端开发）
   - ✅ 调研报告、系统设计方案、RAGFlow学习文档
   - ✅ 阿里云部署方案调研、RAGFlow-Plus源码分析
   - ✅ 权限体系与数据隔离设计
   - 🔄 后端核心服务开发中
   - 🔄 前端管理系统开发中
   - 🔄 数据库初始化脚本开发中
6. PICC人保健康权限管理系统文档充实（待重启）
   - 任务内容：充实三个薄弱文档，达到与其他文档相同的深度和质量
   - 待充实文档：
     1. Onboarding手册：补充IDE配置、启动报错解决方案、代码导航速查表、调试技巧、踩坑FAQ
     2. 配置部署依赖：补充application.yml、bootstrap.yml、logback-spring.xml解析，Apollo配置中心说明，K8s部署配置，CI/CD流程
     3. 深度解析补充-辅助模块：补充AccountRecordServiceImpl、SensitiveWordsServiceImpl、SystemInfoServiceImpl、BaseServiceImpl的逐方法解析
   - 优化原则：在原有结构上补充，保持小白友好风格，每个方法用生活化比喻，敏感信息脱敏
   - 状态：待重启（会话上下文中断，需要重新开始）
7. 企业知识库平台权限体系与数据隔离设计（已完成）
   - 任务内容：设计RBAC+ABAC混合权限模型、多租户数据隔离、RAG行级权限
   - 产出路径：./企业知识库平台/06-权限体系与数据隔离设计.md
   - 完成内容：
     1. 权限模型设计：五级权限层级（系统级→租户级→知识库级→文档级→行级）、标准化权限标识、内置角色设计
     2. 数据隔离设计：混合隔离模式（Schema/数据库隔离）、租户上下文传递机制、知识库/文档/向量库/对话历史隔离
     3. RAG行级权限：元数据标签设计、权限过滤查询构造、性能优化策略
     4. 数据库表结构：10+核心表（租户/用户/角色/权限/知识库/文档/文档权限/审计日志等）、完整ER图
     5. 核心代码示例：TenantContextHolder、TenantContextFilter、UserPermissionService、RagPermissionFilterService、TenantInterceptor
     6. 实施步骤：四阶段计划（基础权限→数据隔离→RAG权限→高级特性）

## 关键概念/话题理解

### 行级权限（Row-Level）
**定义**：数据库按行控制访问权限的机制，常见于数据库权限控制领域。

**常见术语**：
| 英文 | 中文 | 说明 |
|------|------|------|
| Row-Level Security | 行级安全 | 数据库按行控制访问权限 |
| Row-Level Permission | 行级权限 | 用户只能看到自己有权限的数据行 |
| Row-Level Locking | 行级锁 | 锁定单行数据，提高并发性能 |

**示例**：慢病系统中，宝鸡经办员只能查看本地区的申报数据，西安经办员只能查看西安地区的数据。

### 鲁棒性（Robustness）
**定义**：系统在遇到异常情况时，依然能正常工作的能力，即健壮性、抗干扰能力。

**在AI/RAG领域的体现**：
1. **输入鲁棒性**：用户说错话、打错字、口语化表达，系统还能正确理解
2. **数据鲁棒性**：文档有乱码、格式混乱，依然能正确解析
3. **模型鲁棒性**：面对对抗样本或异常输入，不会产生离谱输出

**一句话总结**：鲁棒性 = 系统的"抗压能力"和"容错能力"

## 注意事项与规范

### PICC文档合规化任务（2026-05-01 完成）
- **任务内容**：修复12个违规PICC文档，将"修改建议"改为"学习理解"定位
- **核心原则**：PICC项目仅限学习理解，不允许修改
- **完成状态**：✅ 全部完成
- **修复文档列表**：
  1. ✅ picc-mzmtb-agent-前端性能优化.md → 前端性能问题分析文档
  2. ✅ picc-mzmtb-server-SQL与数据库优化.md → SQL与数据库问题分析文档
  3. ✅ PICC四项目代码规范与重构建议.md → 代码风格与规范学习
  4. ✅ picc-mzmtb-agent-安全修复实现文档.md → 安全问题原理学习文档
  5. ✅ picc-mzmtb-gateway-安全修复实现文档.md → 安全问题原理学习文档
  6. ✅ picc-mzmtb-server-安全修复实现文档.md → 安全问题原理学习文档
  7. ✅ picc-mzmtb-user-安全修复实现文档.md → 安全问题原理学习文档
  8. ✅ picc-mzmtb-agent-安全修复工单.md → 安全风险学习笔记
  9. ✅ picc-mzmtb-gateway-安全修复工单.md → 安全风险学习笔记
  10. ✅ picc-mzmtb-server-安全修复工单.md → 安全风险学习笔记
  11. ✅ picc-mzmtb-user-安全修复工单.md → 安全风险学习笔记
  12. ✅ picc-mzmtb-user-安全修复方案.md → 安全问题学习理解方案
- **修改要点**：
  - 所有文档开头添加声明：`> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议`
  - "优化方案/建议" → "问题分析/学习要点"
  - "重构建议" → "代码风格对比学习"
  - "修复实现/方案/步骤" → "安全问题原理学习"
  - 删除具体修改代码，改为学习理解说明
  - "修复工单/方案" → "安全风险学习笔记"


## 需求2分析结果（榆林申报综合查询新增初审驳回意见展示）

**结论**：代码已基本实现，后端正确获取initialnote字段，前端列表页有条件显示。⚠️ 多次驳回场景下前端只显示单个initialnote，可能丢失历史驳回信息。
- 方案A(最小改动)：确认initialnote为最新驳回原因即可
- 方案B(完整展示)：前端遍历flag="YL_FIRST_TRIAL"记录，展示完整驳回历史


## picc-mzmtb-server 配置信息

### 服务端口
- Server 服务端口：9091
- User 服务端口：9092

### 数据库配置
- 数据库类型：OpenGauss（华为）
- 主库地址：jdbc:opengauss://10.57.18.123:8000,10.57.18.6:8000,10.57.18.169:8000/paas_dev_cdm
- Schema：cdm_dev_user
- 用户名：cdm_dev_user

### Redis配置
- 地址：10.57.17.188:8000
- 密码：PICCmbgl@2024

### Consul配置
- 地址：127.0.0.1:8500
- ACL Token：17373549-c4b5-9d33-778d-d769382d5a7b

### Feign配置
- isUseFeign = N（当前关闭）

### 榆林医保配置
- fixmedinsCode.YL = R61080000001
- fixmedinsName.YL = 人保健康(榆林)

### 文件存储路径
- 申报材料：/mbdeclare/mbfile/
- 体检报告：/mbdeclare/tjbg/
- FTP地址：10.252.68.236:21

### 完整配置文件
已保存至 `./picc-mzmtb-server-config.properties`


## picc-mzmtb-auth 配置信息

### 服务端口
- Auth 服务端口：9093

### 数据库配置
- 数据库类型：OpenGauss（华为）
- 主库地址：jdbc:opengauss://10.57.18.123:8000,10.57.18.6:8000,10.57.18.169:8000/paas_dev_cdm
- Schema：cdm_dev_user
- 用户名：cdm_dev_user

### Redis配置
- 地址：10.57.17.188:8000
- 密码：PICCmbgl@2024

### Consul配置
- 地址：127.0.0.1:8500
- ACL Token：f0447373-e45c-65f7-2c5a-7839ab27de24

### 转发地址
- forwardUrl = http://10.57.17.188:10101/zt/mbgl-uat-ns-btc-hw-k8s/picc-mzmtb-server/

### 完整配置文件
已保存至 `./picc-mzmtb-auth-config.properties`

## picc-mzmtb-user 配置信息

### 服务端口
- User 服务端口：9092

### 数据库配置
- 数据库类型：OpenGauss（华为）
- 主库地址：jdbc:opengauss://10.57.18.123:8000,10.57.18.6:8000,10.57.18.169:8000/paas_dev_cdm
- Schema：cdm_dev_user
- 用户名：cdm_dev_user

### Redis配置
- 地址：10.57.17.190:8000
- 密码：PICCmbgl@2024

### Consul配置
- 地址：127.0.0.1:8500
- ACL Token：d29a875a-4d0c-51e2-aac0-0fe4bea71332

### Feign配置
- isUseFeign = N（当前关闭）

### 完整配置文件
已保存至 `./picc-mzmtb-user-config.properties`


## picc-mzmtb-gateway 配置信息

### 服务端口
- Gateway 服务端口：9001

### 数据库配置
- 使用与其他服务相同的数据库

### Redis配置
- 地址：10.57.17.188:8000
- 密码：PICCmbgl@2024

### Consul配置
- 地址：127.0.0.1:8500
- ACL Token：f0447373-e45c-65f7-2c5a-7839ab27de24

### 转发地址
- forwardUrl = http://10.57.17.188:10101/zt/mbgl-uat-ns-btc-hw-k8s/picc-mzmtb-server/
- zuul.inside.url = http://10.57.17.188:10101

### XXL-Job 配置
- Admin 地址：http://10.57.17.188:8070
- Executor 端口：9999

### 完整配置文件
已保存至 `./picc-mzmtb-gateway-config.properties`


## 专家分配后短信发送接口实现（已完成）
- 短信服务地址：http://10.30.131.12:8000/WSSMSIF/services
- 实现方式：SOAP WebService调用（支持原生Java或Spring RestTemplate）
- 核心业务类：`VipMbDeclareExpertAssignServiceImpl.java`，关键方法：`assignExpert()`
- 调用流程：专家分配成功 → 异步发送短信通知
- 注意事项：异步发送（不阻塞主流程）、异常处理（失败仅记录日志）、内容规范（需含【人保健康】签名）
## RAGFLOW PLUS Logo设计（已完成）
- 需求：将现有logo修改为jiusheng风格，采用草绿色（#7CB342）和藏蓝色（#1A237E）配色，生成横版和图标版PNG格式文件
- 结果：已交付用户，文件路径：`imgs/260423_09_生图/` 下的三个PNG文件
## RAGFLOW PLUS集成wiki功能需求

已完成PandaWiki与Ragflow-Plus的对比分析，推荐先用PandaWiki快速搭建知识库，后续可引入Ragflow-Plus作为底层RAG引擎。

## RuoYi-SpringBoot3-Pro集成AI能力方案（已完成）
### 核心方案
1. **集成RAGFlow知识库**：支持同步/异步/流式调用，提供数据集管理、文档解析、块管理、AI对话能力
2. **集成Dify应用平台**：利用现成Java Client SDK实现对话应用、知识库管理、工作流编排
3. **架构**：RuoYi前端 → RuoYi后端 → RAGFlow/Dify服务
### 方案对比
| 方案 | 优势 | 适用场景 |
|------|------|----------|
| RAGFlow | 精细化文档管理、块控制、知识图谱 | 企业知识库、专业文档问答 |
| Dify | 低代码、工作流编排、快速上线 | AI应用快速开发 |
| PandaWiki | Wiki编辑+AI问答一体化 | 产品文档、FAQ、博客 |

---

## 知识库RAG方案对比
- 传统RAG：切片→向量化→相似度检索（简单但碎片化）
- LongRAG：大块切片+长上下文模型（保留语境，延迟高）
- GraphRAG：实体关系→知识图谱→图遍历（多跳推理，构建成本高）
- Self-RAG：检索决策Token+自我反思（智能但需额外训练）
- Hybrid RAG：BM25+向量+RRF融合（精确+语义双保险，复杂度高）
- Long Context：全文塞入大模型（无丢失，成本高）

## exportYL接口完整流程

### 一、接口定义
**URL**: `POST /mtbapi/mtb/gateway/vipMbDeclareList/exportYL`
**请求参数**：`QueryMbDeclareListVo`（查询条件）

### 二、处理流程
1. **医保账号审批检查**：查询person_division表，如果是医保账号则返回"数据导出需审批"
2. **查询申报数据**：调用queryVipMbdeclareInfoYlListNew()获取榆林申报列表
3. **权限判断**：调用User服务判断是否有"榆林导出权限"
4. **敏感信息脱敏处理**：有权限返回原始数据，无权限则脱敏
5. **生成Excel文件**：根据idList是否为空选择导出全部或选中数据
6. **返回导出结果**：返回包含base64文件的ExportMbdeclareInfoDto

### 三、脱敏规则

| 字段 | 脱敏后 |
|------|--------|
| 参保人姓名 | 张** |
| 手机号码 | 154****7181 |
| 身份证号 | 130180********0918 |
| 专家姓名 | 李** |

---

## 门诊慢特病业务管理信息系统智能化设计方案总结

### 核心目标
- 审核时间从5天缩短到3天
- 初审实现智能化自动处理
- 专家审核实现智能辅助+人工复核

### 智能场景
1. **资料质检**（P0）：图片模糊度、角度检测
2. **慢病初审**（P0）：图片分类→完整性判断→公章识别
3. **资料脱敏**（P1）：自动打码敏感信息
4. **专家鉴定**（P2）：结构化数据+规则校验+大模型审核
5. **处方上传**（P1）：通用模板处方识别

### 关键数据
- 日均申报量：500-2000人
- 日均图片上传：13415张（峰值84813张）
- 高频病种TOP3：高血压、糖尿病、冠心病

---

## 代码解释
- **exportMbdeclareInfoYL**：榆林慢病申报导出（医保校验→查询→权限判断→脱敏→Excel）
- **DrEnum**：VALID(0)/INVALID(1)，逻辑删除标识


## 企业级知识库平台项目（2026-04-24 启动，已完成基础框架搭建）

### 项目背景
- 客户已通过知识库汇报，需要交付企业知识库平台
- 技术选型：RAGFlow 开源版本进行二开
- 参考：RAGFlow-Plus（已做企业级改造，文档处理升级为 MinerU，效果提升但需要GPU资源）

### 核心需求
1. **部署方案**：阿里云服务部署知识库/RAGFlow 可行性调研
2. **系统设计**：企业级知识库系统架构 + RAG 集成方案
3. **权限体系**：用户权限 + 数据隔离设计
4. **行级权限**：RAG 的行级权限控制
5. **增强策略**：企业级知识库增强方案
6. **参考项目**：RAGFlow-Plus 系统架构

### 项目完成情况
已完成基础框架搭建，包含：
- ✅ RBAC+ABAC混合权限模型
- ✅ 行级权限过滤器（支持用户属性过滤）
- ✅ 多租户隔离机制
- ✅ 核心API接口框架
- ✅ 数据库初始化脚本
- ✅ RAGFlow API与权限模型分析及文档更新（输出v2.0版本学习文档）

**项目路径**：./企业知识库平台/
**源码目录**：./企业知识库平台/src/
**默认账号**：admin / admin123

### 待完成
- MinerU文档解析集成
- RAG检索增强策略
- 前端页面开发

### 已完成任务
10. RAGFlow项目深度学习与知识库文档生成（已完成）
   - 任务内容：访问GitHub仓库、分析核心功能和技术架构、理解RAGFlow核心概念、生成详细知识库文档
   - 项目地址：https://github.com/infiniflow/ragflow.git
   - 产出路径：./企业知识库平台/03-RAGFlow项目学习.md
   - 完成内容：
     1. 完整的RAGFlow学习文档（9大章节）
     2. 项目概述、技术架构、核心功能、目录结构、快速开始
     3. 核心概念（RAG原理、DeepDoc解析、知识库概念、分块策略、混合检索）
     4. API接口（Python SDK完整API、OpenAI兼容API、记忆管理）
     5. 配置说明（环境变量、服务配置、支持的LLM厂商列表）
     6. 与RAGFlow-Plus对比分析
   - 关键发现：
     - RAGFlow v0.25.0 是最新稳定版本
     - 技术栈：Python 46% + TypeScript 33% + Go 10% + C++ 9%
     - 支持12种分块方法（naive/manual/qa/table/paper/book/laws/presentation/picture/one/email/knowledge-graph）
     - 支持 Agentic Workflow、MCP协议、Agent Memory
     - 支持从 Confluence、S3、Notion、Discord、Google Drive 同步数据
     - 文档引擎可切换：Elasticsearch ↔ Infinity

### 已完成任务
8. 阿里云部署方案调研（已完成）
   - 任务内容：调研阿里云PAI、百炼、向量检索服务,分析在阿里云上自建RAGFlow的可行性和成本
   - 产出路径：./企业知识库平台/04-阿里云部署方案调研.md
   - 完成内容：
     1. 阿里云RAG产品矩阵分析（百炼、PAI-EAS、Milvus）
     2. 自建RAGFlow vs 阿里云RAG服务成本对比
     3. 三种部署方案详解（计算巢、ECS自建、混合架构）
     4. 阿里云托管服务配置要点（RDS、OSS、Redis）
     5. 场景化部署建议

9. RAGFlow-Plus源码分析（已完成）
   - 任务内容：分析RAGFlow-Plus企业级改造的核心内容（用户权限体系、数据隔离机制、MinerU文档解析集成、与原版RAGFlow的差异）
   - 产出路径：./企业知识库平台/05-RAGFlow-Plus源码分析.md
   - 完成内容：
     1. RAGFlow-Plus项目概览（GitHub: zstar1003/ragflow-plus）
     2. 系统架构分析（9个Docker容器）
     3. 用户权限体系实现（RBAC三层架构）
     4. 数据隔离机制（多租户隔离策略）
     5. MinerU解析引擎集成细节
     6. 与原版RAGFlow的核心差异
     7. API设计和部署配置
     8. AGPLv3许可证使用注意事项

### 关键发现与建议
#### 阿里云部署方面：
- 阿里云百炼提供开箱即用RAG服务（标准版0.03元/知识库/小时）
- PAI-EAS支持一键部署RAG系统，对接多种向量库
- 自建RAGFlow推荐使用混合架构（ECS+RDS+OSS+Milvus）

#### RAGFlow-Plus方面：
- 企业级改进核心：后台管理系统 + MinerU解析 + 权限体系
- AGPLv3许可证：衍生作品需开源，网络服务需提供源码
- 最低内存要求12GB（含6GB的MinerU后端）

#### 部署策略建议：
采用"短期用百炼快速验证，中期基于RAGFlow-Plus二开"的渐进策略

#### 风险提示：
- 许可证风险：若需闭源商用，RAGFlow-Plus存在AGPLv3合规风险，需提前规划
- 硬件要求：RAGFlow-Plus完整部署需要较大内存（≥12GB），GPU可选


## 接口调用日志问题（已解决）
- varchar字段截断/加密超限 → 改为TEXT类型；缺少必填字段校验

## CxPrescriptionPoolServiceImpl 代码问题（已解决）
- 参数缺失+varchar长度不足 → 添加校验+改TEXT类型

## PICC PaaS云平台日志查询
- 地址：http://portal.paas.cspiccnet:9000/paasPortal/log/logQuery/
- 查不到日志常见原因：时间范围太短、没输入关键字、服务选择不全

## Tavily API Key 信息
- 搜索API服务，专为LLM优化。Free: 1,000次/月，Pro: $29/月
- 注册：https://tavily.com

## DeepSeek模型配置
- deepseek-v3.2-exp / deepseek-v3.1（ksyun金山云部署），V3.1推荐生产环境

## LongCat-Flash-Lite API
- 地址：https://api.longcat.chat/openai

## 罗技键盘电池型号参考（2026-04-25）
- 罗技K380：2节AAA电池（7号）
- 罗技MK950：2节AAA电池（7号）
- 罗技MK360/K360：2节AA电池（5号）
- 罗技MK650：2节AA电池（5号）
- 罗技G613：2节AA电池（5号）
- 罗技SlimFolio系列：2枚CR2032纽扣电池

6. RAGFlow API与权限模型分析（已完成）
   - 任务背景：企业知识库平台需要基于RAGFlow进行二开，需深入理解其API设计和权限模型
   - 分析目标：
     1. API结构分析：核心API端点和功能、认证机制、会话管理机制
     2. 权限模型分析：数据集(Dataset)权限控制、知识库(Knowledgebase)访问控制、Agent权限隔离、租户/多租户支持情况
     3. 向量检索权限：检索时权限过滤机制、行级权限实现可能性
   - 产出要求：将分析结果追加到./企业知识库平台/03-RAGFlow项目学习.md，新增章节：API权限设计分析、多租户可行性分析、行级权限实现建议
   - 参考路径：RAGFlow项目（https://github.com/infiniflow/ragflow.git），重点关注api/目录和rag/目录中的代码
   - 完成内容：
     1. 新增4个章节到文档中：
        - 第10章：API权限设计分析（认证机制、核心数据模型、权限控制机制、API端点结构）
        - 第11章：多租户可行性分析（现有租户模型、数据隔离机制、多租户支持评估）
        - 第12章：行级权限实现建议（现状分析、数据库层/服务层/检索层改造、前端改造）
        - 第13章：企业级扩展建议（SSO单点登录、审计日志、资源配额管理）
     2. 关键发现：
        - 认证机制：双层安全模型（Session Token + API Token）
        - 多租户架构：基于tenant_id的物理隔离（MySQL、ES索引、MinIO、Redis）
        - 权限控制：开源版仅支持me/team两种知识库权限，需扩展实现行级权限
     3. 文档更新：将文档版本从v1.0升级到v2.0
   - 文档路径：./企业知识库平台/03-RAGFlow项目学习.md
## PICC人保健康权限管理系统项目学习
- **仓库**: https://codeup.aliyun.com/69708490f7b43e00d4204914/picc-mzmtb-user.git
- **项目全称**: 门诊慢特病业务管理信息系统-权限管理服务
- **技术栈**: Spring Boot + MyBatis + GaussDB + Redis + Apollo + K8s + BES宝兰德
- **已部署地市**: 16个（宝鸡、榆林、延安、商洛、杨凌等）
- **教程文档**: ./picc-mzmtb-user-教程文档.md（5929行，完整覆盖）
- **关键发现**: 
  - SM4/AES密钥硬编码（安全隐患）
  - URL权限模糊匹配（可绕过）
  - 权限编码"88"硬编码
  - APIAuthorityFilter只拦截/privilege/user/*路径
  - 默认密码PICChealth@2020
- **完成时间**: 2026-04-30

## PICC人保健康权限项目 - 深度解析进度

### 已完成
- [x] Service层73个public方法全覆盖
- [x] API层6个Api类、47个HTTP接口
- [x] Mapper层核心XML逐行拆解
- [x] 数据模型PO/DTO/VO、表关系图
- [x] 配置文件+项目依赖+部署+测试
- [x] 安全机制三道关卡+密码加密体系
- [x] 代码质量6严重8中等6改进
- [x] **深度解析第二章**：query()200行逐行拆解、BFS机构树、菜单树递归、完整数据流时序图、前端页面→接口映射(47个)、数据迁移逻辑(MoveServiceImpl)、6个安全修复方案、权限数据流转全景

- [x] **深度解析第三章**：RoleInfoServiceImpl完整方法解析（12个public方法+3个私有方法）→ `./picc-mzmtb-user-深度解析第三章-角色管理.md`（1430行，60KB），含角色管理业务概述、核心数据模型、12方法详解、权限树构建逻辑、角色资源管理流程、setAuths()权限归属配置补充

### 待深入
（当前无待深入项）

### 本轮新增
- [x] 数据库ER图与17张表结构详解
- [x] 新成员Onboarding手册
- [x] 安全修复实施方案（P0/P1/P2分级+代码示例+时间线）
- [x] **深度解析第四章**：菜单与系统管理模块完整解析（MenuInfoServiceImpl、PrivilegeMenuInfoServiceImpl、PrivilegeMenuServiceServiceImpl、SysInfoServiceImpl共21个public方法）→ `./picc-mzmtb-user-深度解析第四章-菜单与系统管理.md`（1517行，49KB），含业务概述、核心数据模型、菜单树构建原理、服务架构全图、方法详解、业务场景解析、API速查表
- [x] 辅助模块解析（BaseServiceImpl+辅助服务）
- [x] 教程总纲文档重建（主文档被子任务覆盖后重建为结构化索引）
- [x] 架构设计文档（10章节，含技术/安全/数据/部署/扩展性架构）
- [x] 安全修复工单（8个工单，9.5人天，含完整修复代码）
- [x] API层+Mapper层+数据模型专项文档 → `./picc-mzmtb-user-API-Mapper-数据模型.md`（6个Api类32接口+17个Mapper XML+PO/DTO/VO解析+数据流转图+表关系图）

### 关键发现
- query()方法有N+1查询和重复查询问题，pageNum=0导致不分页
- getidList() BFS方式性能差，应改为一次性查询+内存构建
- MoveServiceImpl.passwordBackMD5()会将密码明文存储
- OrgQueryVo.orgName字段名误导，实际传的是机构ID
- 前端页面与接口完全映射表已建立（47个接口）
- 菜单树采用递归构建算法，需注意递归深度限制
- @Transactional事务注解确保删除操作的原子性（要么全删，要么全不删）
- 所有删除操作均为软删除（设置deleteAt字段而非物理删除）
- PageHelper分页插件通过ThreadLocal传递分页参数，实现无侵入分页
- reviseServices方法支持批量增删改菜单服务，减少前后端交互次数

### 零基础小白教程文档
- **文档路径**: `./picc-mzmtb-user-教程文档.md`
- **文件规模**: 2024行，约80KB
- **内容覆盖**:
  - sys模块（UserInfoServiceImpl、OrgInfoServiceImpl等8个类）
  - role模块（RoleInfoServiceImpl）
  - menu模块（MenuInfoServiceImpl等3个类）
  - config配置类（APIAuthorityFilter、TokenInterceptorConfig等）
  - utils工具类（EncryptionUtil、SM4Util）
- **文档特色**:
  - 生活比喻贯穿全文，专业概念小白友好
  - 每个方法标准解析（参数、返回值、调用关系、步骤拆解）
  - 异常处理说明与小白易懵点提示
  - 附赠数据库表结构、业务流程图、FAQ等内容

## PICC门诊慢特病业务服务（picc-mzmtb-server）- 解析进度

### 项目概况
- 仓库地址: https://codeup.aliyun.com/69708490f7b43e00d4204914/picc-mzmtb-server.git
- 规模: 2647个Java文件, 213个Mapper XML, 11+13个业务模块
- 核心模块: mb(833文件), mtb-yh(749文件,13地市差异化)
- 服务端口: 9091
- 技术栈: Spring Boot + MyBatis + Activiti6 + GaussDB + Redis + Apollo

### 已完成
- [x] 项目全貌扫描（规模、模块结构、与权限服务对比）
- [x] API接口全景（子任务 session_id=7634447726138278187）
  - ✅ 文档：`./picc-mzmtb-server-API接口全景.md`（1016行，894个接口）
  - ✅ 核心内容：10个业务域分类（申报管理、审核管理、慢病卡管理、处方管理、药店管理、费用管理、数据统计、系统管理、外部对接、工作流）、每个域包含类名、HTTP方法、完整路径、说明
  - ✅ 统计数据：105个API类，894个接口，申报管理占比最高（48.7%）
  - ✅ 关键处理：路径解析优化（避免把RequestMethod.POST当成路径）、敏感信息脱敏、多业务域分类

## picc-mzmtb-agent 前端项目解析进度
- ✅ 项目克隆到 `/tmp/picc-mzmtb-agent/`（652个Vue文件，74个API，21个地市模块，Vue 2项目）
- ✅ Onboarding手册 → `./picc-mzmtb-agent-Onboarding手册.md`（1206行）
- ✅ 项目全貌与架构解析 → `./picc-mzmtb-agent-项目全貌与架构解析.md`（1459行，Vue2全家桶+21地市+74API+5环境构建）
- ✅ API层与路由解析 → `./picc-mzmtb-agent-API层与路由解析.md`（966行，4个Axios实例+340接口+13地市flag）
- ✅ API层与路由深度解析文档 → `/home/user/picc-docs/API层与路由深度解析文档.md`（966行，29948字节，包含项目概览、Axios封装、多实例架构、API层详解、路由系统、Vuex、安全机制、多城市flag、接口总览、路由菜单等10大章节）
- ✅ 总纲索引 → `./picc-mzmtb-agent-教程文档.md`（166行，包含项目一句话定位、文档导航表、3类阅读路径<小白/前端/全栈>、核心发现摘要<架构亮点/业务特色/技术债务>、技术栈速查、9个关键文件索引、ASCII服务调用链路图、5个快速问答）
- ✅ 地市差异化与组件解析 → `./picc-mzmtb-agent-地市差异化与组件解析.md`（884行，21地市对比+3套组件库+Vuex）
- 📌 核心技术与架构细节：
  - 4个Axios实例分工明确：axios.js(慢病业务核心请求)、axiosCenter.js(通用中心请求)、axiosPower.js(权限管理请求)、axiosjkgl.js(鉴权请求)
  - 环境硬性要求：Node.js必须为14.x或16.x版本（Vue 2项目不支持17及以上版本）
  - 完整服务调用链路：用户浏览器(HTTPS 443) → Nginx反向代理 → 网关服务(9001) → 业务服务(9091)/权限服务(9092) → GaussDB数据库