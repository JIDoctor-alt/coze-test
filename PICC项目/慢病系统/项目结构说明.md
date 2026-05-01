# PICC慢特病系统安全升级功能 - 项目结构说明

```
PICC慢病系统/
├── scripts/                          # 数据库脚本目录
│   ├── 01_账号安全.sql              # 账号安全相关表结构
│   ├── 02_敏感信息脱敏.sql           # 脱敏配置相关表结构
│   └── 03_审批流程.sql              # 下载审批流程相关表结构
│
├── src/                              # 后端服务目录
│   ├── account_security_service.py   # 账号安全服务
│   ├── sensitive_data_service.py     # 敏感数据处理服务
│   ├── approval_service.py          # 审批流程服务
│   ├── api/                          # API定义目录
│   │   └── v1/
│   │       └── endpoints/
│   │           └── api_endpoints.py  # RESTful API端点定义
│   ├── models/                       # 数据模型目录（扩展）
│   ├── services/                     # 服务层目录（扩展）
│   └── core/                         # 核心配置目录（扩展）
│
├── web/                              # 前端目录
│   ├── src/
│   │   ├── components/               # 通用组件
│   │   │   └── SensitiveField.vue    # 敏感字段组件（带小眼睛交互）
│   │   ├── views/                    # 页面视图
│   │   │   └── Approval/
│   │   │       ├── ApprovalManagement.vue  # 审批管理页面
│   │   │       └── components/
│   │   │           └── DownloadApplyModal.vue  # 下载申请弹窗
│   │   ├── types/                    # TypeScript类型定义
│   │   │   └── index.ts
│   │   ├── utils/                    # 工具函数
│   │   │   └── sensitive.ts          # 敏感数据处理工具
│   │   ├── router/                   # 路由配置（扩展）
│   │   ├── stores/                   # 状态管理（扩展）
│   │   └── public/                   # 静态资源
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .env.example
│
├── 部署说明文档.md                    # 部署说明文档
├── API接口文档.md                    # API接口文档
└── 项目结构说明.md                   # 本文档
```

---

## 目录详细说明

### 1. 数据库脚本 (`scripts/`)

| 文件 | 说明 | 包含表 |
|------|------|--------|
| `01_账号安全.sql` | 账号安全相关表结构 | sec_high_risk_account_blacklist (高危账号黑名单)<br>sec_account_audit_log (审计日志)<br>sec_account_extension (账号扩展)<br>sec_account_creation_rule (账号创建规则)<br>sys_city_info (地市信息) |
| `02_敏感信息脱敏.sql` | 敏感数据脱敏配置表 | sec_sensitive_field_config (字段脱敏配置)<br>sec_menu_field_mapping (菜单字段映射)<br>sec_sensitive_view_permission (查看权限)<br>sec_sensitive_operation_log (操作日志)<br>sec_encryption_key (密钥管理) |
| `03_审批流程.sql` | 下载审批流程表 | sec_download_application (下载申请)<br>sec_approval_record (审批记录)<br>sec_approval_flow_config (流程配置)<br>sec_approval_permission (审批权限)<br>sec_download_menu_permission (菜单下载权限)<br>sec_approval_flow_node (流程节点)<br>sec_system_operation_log (系统日志) |

### 2. 后端服务 (`src/`)

| 文件 | 说明 | 主要功能 |
|------|------|---------|
| `account_security_service.py` | 账号安全服务 | 高危账号验证、密码强度检查、账号创建、审计日志 |
| `sensitive_data_service.py` | 敏感数据服务 | 数据脱敏、加密存储、权限控制、脱敏配置管理 |
| `approval_service.py` | 审批流程服务 | 下载申请、审批处理、权限验证、下载管理 |
| `api_endpoints.py` | API端点定义 | RESTful接口规范、请求/响应格式定义 |

### 3. 前端组件 (`web/src/`)

| 文件 | 说明 | 功能描述 |
|------|------|---------|
| `SensitiveField.vue` | 敏感字段组件 | 小眼睛图标交互，点击显示/隐藏明文，支持权限控制 |
| `ApprovalManagement.vue` | 审批管理页面 | 查询申请、审批操作、申请详情查看 |
| `DownloadApplyModal.vue` | 下载申请弹窗 | 填写下载用途、提交下载申请 |
| `index.ts` | 类型定义 | 统一管理TypeScript接口类型 |
| `sensitive.ts` | 工具函数 | 脱敏算法、验证函数、格式化工具 |

---

## 功能模块对应关系

### 功能一：禁用高危默认账号

| 层级 | 文件 | 说明 |
|------|------|------|
| 数据库 | `01_账号安全.sql` | sec_high_risk_account_blacklist, sec_account_audit_log |
| 后端 | `account_security_service.py` | HighRiskAccountValidator, AccountSecurityService |
| 前端 | 各地市用户管理页面 | 新增用户时调用validate接口 |

### 功能二：隐藏敏感信息

| 层级 | 文件 | 说明 |
|------|------|------|
| 数据库 | `02_敏感信息脱敏.sql` | sec_sensitive_field_config, sec_menu_field_mapping |
| 后端 | `sensitive_data_service.py` | SensitiveDataMasker, SensitiveDataService |
| 前端 | `SensitiveField.vue` | 通用敏感字段组件 |
| 前端 | 各地市查询页面 | 集成SensitiveField组件 |

### 功能三：操作流程审批

| 层级 | 文件 | 说明 |
|------|------|------|
| 数据库 | `03_审批流程.sql` | sec_download_application, sec_approval_record, sec_approval_permission |
| 后端 | `approval_service.py` | ApprovalService, DownloadApplicationHelper |
| 前端 | `ApprovalManagement.vue` | 审批管理主页面 |
| 前端 | `DownloadApplyModal.vue` | 下载申请弹窗 |

---

## 地市配置

| 地市编码 | 地市名称 | 简码 |
|---------|---------|------|
| 610300 | 宝鸡 | BJ |
| 130700 | 张家口 | ZJK |
| 139000 | 定州 | DZ |
| 610600 | 延安 | YA |
| 611000 | 商洛 | SL |
| 150700 | 满洲里 | MZL |
| 610800 | 榆林 | YL |
| 610400 | 杨凌 | YLing |
| 360400 | 九江 | JJ |
| 140500 | 晋城 | JC |
| 610400 | 咸阳 | XY |

---

## 开发建议

### 数据库开发
1. 先执行 `01_账号安全.sql` 初始化基础表
2. 再执行 `02_敏感信息脱敏.sql` 初始化脱敏配置
3. 最后执行 `03_审批流程.sql` 初始化审批流程

### 后端开发
1. 安装Python依赖
2. 配置数据库连接
3. 启动API服务
4. 验证接口功能

### 前端开发
1. 安装Node.js依赖
2. 配置API地址
3. 启动开发服务器
4. 集成组件到现有页面

---

## 版本信息

- 文档版本：1.0
- 创建日期：2026-03-19
- 适用系统：PICC人保健康门诊慢特病业务管理信息系统
