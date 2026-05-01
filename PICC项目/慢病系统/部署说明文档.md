# PICC人保健康门诊慢特病业务管理信息系统
## 安全升级功能 - 部署说明文档

---

## 一、项目概述

### 1.1 项目背景
为落实信息安全升级要求，完善慢病系统的安全功能，计划实施以下安全升级：

1. **禁用高危默认账号**：禁用 admin、system、root 等高危默认账号
2. **隐藏敏感信息**：在所有查询页面实施用户五要素动态加密
3. **操作流程审批**：针对批量下载及导出功能，增设"申请-审批-执行"流程

### 1.2 涉及地市
宝鸡、张家口、定州、延安、商洛、满洲里、榆林、杨凌、九江、晋城、咸阳

---

## 二、数据库部署

### 2.1 环境要求
- MySQL 5.7+ 或 PostgreSQL 12+
- 支持 UTF8MB4 字符集

### 2.2 数据库初始化

```bash
# 1. 创建数据库
mysql -u root -p < scripts/01_账号安全.sql
mysql -u root -p < scripts/02_敏感信息脱敏.sql
mysql -u root -p < scripts/03_审批流程.sql

# 或者使用 psql（PostgreSQL）
psql -U postgres -d picc_chronic_disease -f scripts/01_账号安全.sql
psql -U postgres -d picc_chronic_disease -f scripts/02_敏感信息脱敏.sql
psql -U postgres -d picc_chronic_disease -f scripts/03_审批流程.sql
```

### 2.3 数据库脚本说明

| 脚本文件 | 说明 | 主要表结构 |
|---------|------|-----------|
| `01_账号安全.sql` | 账号安全相关表 | 高危账号黑名单、审计日志、账号规则配置 |
| `02_敏感信息脱敏.sql` | 敏感数据脱敏配置表 | 脱敏规则、菜单字段映射、查看权限配置 |
| `03_审批流程.sql` | 下载审批流程表 | 下载申请、审批记录、审批配置 |

---

## 三、后端服务部署

### 3.1 环境要求
- Python 3.9+
- JDK 11+ (如果使用Java后端)

### 3.2 Python后端部署

```bash
# 1. 创建虚拟环境
cd PICC慢病系统/src
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
export DATABASE_URL="mysql+pymysql://user:password@host:3306/picc_chronic_disease"
export SECRET_KEY="your-secret-key-here"
export ENCRYPTION_KEY="your-encryption-key"

# 4. 运行服务
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3.3 服务模块说明

| 模块文件 | 说明 | 主要功能 |
|---------|------|---------|
| `account_security_service.py` | 账号安全服务 | 高危账号检测、密码强度验证、审计日志 |
| `sensitive_data_service.py` | 敏感数据服务 | 数据脱敏、加密存储、权限控制 |
| `approval_service.py` | 审批流程服务 | 下载申请、审批流程、权限验证 |
| `api/v1/endpoints/api_endpoints.py` | API端点定义 | RESTful接口规范 |

---

## 四、前端部署

### 4.1 环境要求
- Node.js 16+
- npm 8+ 或 yarn 1.22+

### 4.2 前端部署步骤

```bash
# 1. 进入前端目录
cd PICC慢病系统/web

# 2. 安装依赖
npm install

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置 API 地址等

# 4. 开发环境运行
npm run dev

# 5. 生产环境构建
npm run build

# 6. 部署到服务器
# 将 dist 目录下的文件部署到 Nginx 或其他 Web 服务器
```

### 4.3 前端组件说明

| 组件路径 | 说明 | 用途 |
|---------|------|------|
| `components/SensitiveField.vue` | 敏感字段组件 | 小眼睛交互，显示/隐藏明文 |
| `views/Approval/ApprovalManagement.vue` | 审批管理页面 | 下载申请、审批、查询 |
| `views/Approval/components/DownloadApplyModal.vue` | 下载申请弹窗 | 提交下载申请表单 |
| `types/index.ts` | TypeScript类型定义 | 统一类型管理 |

---

## 五、Nginx配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /var/www/picc-frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # API代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # 上传文件大小限制
    client_max_body_size 100m;
}
```

---

## 六、安全配置

### 6.1 密钥管理

```bash
# 生成加密密钥（用于敏感数据加密）
openssl rand -hex 32

# 配置到环境变量
export ENCRYPTION_KEY="your-generated-key"
```

### 6.2 高危账号关键词配置

通过管理后台配置高危关键词黑名单：
- 默认关键词：admin, system, root, administrator, supervisor
- 支持添加、修改、删除关键词
- 支持精确匹配或模糊匹配

### 6.3 敏感字段脱敏规则

| 字段类型 | 脱敏规则 | 示例 |
|---------|---------|------|
| 姓名 | 保留姓氏+** | 张三 → 张** |
| 身份证号 | 前6后4 | 610310********5721 |
| 手机号 | 前3后4 | 154****0918 |
| 银行卡号 | 前6后4 | 622202****1234 |
| 地址 | 保留省市区+** | 北京市丰台区****** |

---

## 七、权限配置

### 7.1 审批权限配置

在权限管理系统中配置审批下载权限：

```
权限归属选项：
- 审批(宝鸡下载)
- 审批(张家口下载)
- 审批(定州下载)
- 审批(延安下载)
- 审批(商洛下载)
- 审批(满洲里下载)
- 审批(榆林下载)
- 审批(杨凌下载)
- 审批(九江下载)
- 审批(晋城下载)
- 审批(咸阳下载)
```

### 7.2 敏感信息查看权限

| 角色 | 权限级别 | 可查看字段 |
|------|---------|-----------|
| 系统管理员 | 3级 | 全部字段 |
| 审计员 | 3级 | 全部字段 |
| 经办人 | 2级 | 姓名、身份证号、手机号 |
| 医生 | 1级 | 姓名、身份证号、手机号 |
| 专家 | 2级 | 姓名、身份证号、手机号 |

---

## 八、API接口文档

### 8.1 账号安全接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/account/validate` | POST | 验证账号名称 |
| `/api/v1/account/create` | POST | 创建账号 |
| `/api/v1/account/generate` | POST | 生成账号名称 |
| `/api/v1/audit/logs` | GET | 查询审计日志 |

### 8.2 敏感数据接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/sensitive/mask` | POST | 脱敏数据 |
| `/api/v1/sensitive/config` | GET | 获取脱敏配置 |
| `/api/v1/sensitive/permission/check` | POST | 检查查看权限 |
| `/api/v1/sensitive/log` | POST | 记录查看操作 |

### 8.3 下载审批接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/approval/download/apply` | POST | 提交下载申请 |
| `/api/v1/approval/download/approve` | POST | 审批下载申请 |
| `/api/v1/approval/download/list` | GET | 查询申请列表 |
| `/api/v1/approval/download/detail` | GET | 获取申请详情 |
| `/api/v1/approval/permission/cities` | GET | 获取可审批地市 |
| `/api/v1/download/validate` | POST | 验证下载权限 |

详细API文档请参考：`src/api/v1/endpoints/api_endpoints.py`

---

## 九、运维监控

### 9.1 日志配置

```yaml
# logging.yaml
version: 1
formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    formatter: default
  file:
    class: logging.handlers.RotatingFileHandler
    filename: logs/app.log
    maxBytes: 10485760
    backupCount: 5
root:
  level: INFO
  handlers: [console, file]
```

### 9.2 监控指标

- API响应时间
- 错误率
- 审批流程处理时间
- 敏感数据访问次数

---

## 十、常见问题

### 10.1 部署后功能不可用
1. 检查数据库连接配置
2. 检查API服务是否正常运行
3. 检查前端API地址配置

### 10.2 脱敏显示异常
1. 检查字段编码是否正确
2. 确认浏览器控制台是否有报错

### 10.3 审批流程异常
1. 检查审批权限配置
2. 验证数据库记录状态
3. 查看日志排查问题

---

## 十一、联系方式

技术支持：PICC信息技术部
