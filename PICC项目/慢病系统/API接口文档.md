# PICC慢特病系统安全功能 API 接口文档

## 一、接口概览

### 1.1 账号安全相关

#### POST /api/v1/account/validate
**功能**: 验证账号名称是否包含高危关键词

**请求参数**:
```json
{
  "account_name": "admin001",
  "city_code": "610300"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "验证通过",
  "success": true
}
```
或
```json
{
  "code": 400,
  "message": "账号信息不可包含admin、system、root，请修改",
  "success": false
}
```

---

#### POST /api/v1/account/create
**功能**: 创建新账号，包含高危账号检测和密码强度验证

**请求参数**:
```json
{
  "account_name": "bjzs1234",
  "real_name": "张三",
  "password": "SecurePass123!",
  "city_code": "610300",
  "account_source": "jingban",
  "phone": "13812345678",
  "id_card": "610310199001011234"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "账号创建成功",
  "data": {
    "account_id": "ACC202603190001"
  },
  "success": true
}
```

---

#### POST /api/v1/account/generate
**功能**: 根据姓名和地市生成符合规范的账号名称

**请求参数**:
```json
{
  "real_name": "李四",
  "city_code": "610300",
  "account_source": "jingban"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "account_name": "bjls5678"
  },
  "success": true
}
```

---

#### GET /api/v1/audit/logs
**功能**: 分页查询账号安全审计日志

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| account_name | string | 否 | 账号名称 |
| log_type | int | 否 | 日志类型 |
| city_code | string | 否 | 地市编码 |
| start_time | datetime | 否 | 开始时间 |
| end_time | datetime | 否 | 结束时间 |
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "list": [
      {
        "id": 1,
        "log_type": 1,
        "account_id": "ACC001",
        "account_name": "bjzs1234",
        "real_name": "张三",
        "city_name": "宝鸡",
        "operation_content": "创建账号成功",
        "operation_result": 1,
        "ip_address": "192.168.1.100",
        "created_time": "2026-03-19 10:30:00"
      }
    ]
  },
  "success": true
}
```

---

### 1.2 敏感数据相关

#### POST /api/v1/sensitive/mask
**功能**: 对敏感字段进行脱敏处理

**请求参数**:
```json
{
  "data": {
    "name": "张三",
    "id_card": "610310199001011234",
    "phone": "13812345678"
  },
  "city_code": "610300",
  "menu_code": "MENU_BJ_001"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "masked_data": {
      "name": "张**",
      "id_card": "610310********1234",
      "phone": "138****5678"
    }
  },
  "success": true
}
```

---

#### GET /api/v1/sensitive/config
**功能**: 获取敏感字段脱敏配置列表

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": [
    {
      "field_code": "NAME",
      "field_name": "姓名",
      "field_type": "name",
      "masking_rule": "first-last",
      "preserve_chars": 1,
      "example": {
        "original": "张三",
        "masked": "张**"
      }
    },
    {
      "field_code": "IDCARD",
      "field_name": "身份证号",
      "field_type": "idcard",
      "masking_rule": "front-back",
      "preserve_chars": 6,
      "example": {
        "original": "610310199001011234",
        "masked": "610310********1234"
      }
    },
    {
      "field_code": "PHONE",
      "field_name": "手机号码",
      "field_type": "phone",
      "masking_rule": "front-back",
      "preserve_chars": 3,
      "example": {
        "original": "13812345678",
        "masked": "138****5678"
      }
    }
  ],
  "success": true
}
```

---

#### POST /api/v1/sensitive/permission/check
**功能**: 检查用户查看敏感字段的权限

**请求参数**:
```json
{
  "user_id": "user001",
  "role_code": "ROLE_JINGBAN",
  "field_codes": ["NAME", "IDCARD", "PHONE", "BANKCARD"],
  "city_code": "610300"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "NAME": true,
    "IDCARD": true,
    "PHONE": true,
    "BANKCARD": false
  },
  "success": true
}
```

---

### 1.3 下载审批相关

#### POST /api/v1/approval/download/apply
**功能**: 提交数据下载/导出审批申请

**请求参数**:
```json
{
  "city_code": "610300",
  "city_name": "宝鸡",
  "menu_code": "MENU_BJ_006",
  "menu_name": "慢病申报查询",
  "download_type": "export_excel",
  "download_purpose": "导出数据给医保局",
  "download_conditions": "时间范围：2026-3-1~2026-3-20; 表头字段：姓名、身份证号、手机号码、疾病类型、疾病名称",
  "query_params": "{\"startDate\":\"2026-03-01\",\"endDate\":\"2026-03-20\"}"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "下载申请已提交，请等待审批",
  "data": {
    "application_no": "DA61030020260319123456123"
  },
  "success": true
}
```

---

#### POST /api/v1/approval/download/approve
**功能**: 审批下载申请

**请求参数**:
```json
{
  "application_no": "DA61030020260319123456123",
  "approval_result": 1,
  "approval_comment": "数据用途合理，同意导出"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "已审核通过",
  "success": true
}
```

---

#### GET /api/v1/approval/download/list
**功能**: 分页查询下载申请列表

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| city_code | string | 否 | 地市编码 |
| menu_name | string | 否 | 菜单名称（模糊搜索） |
| applicant_account | string | 否 | 下载申请人 |
| approver_account | string | 否 | 审批人 |
| approval_status | int | 否 | 审批状态：0-未审核，1-审核通过，2-审核不通过 |
| start_date | datetime | 否 | 申请日期起 |
| end_date | datetime | 否 | 申请日期止 |
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "list": [
      {
        "id": 1,
        "application_no": "DA61030020260319123456123",
        "city_code": "610300",
        "city_name": "宝鸡",
        "menu_code": "MENU_BJ_006",
        "menu_name": "慢病申报查询",
        "applicant_id": "user001",
        "applicant_name": "张三",
        "applicant_account": "zhangsan",
        "created_time": "2026-03-19 10:30:00",
        "download_purpose": "导出数据给医保局",
        "download_conditions": "时间范围：2026-3-1~2026-3-20",
        "approval_status": 0,
        "approval_status_text": "未审核"
      }
    ]
  },
  "success": true
}
```

---

#### GET /api/v1/approval/download/detail
**功能**: 根据申请单号获取申请详情

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| application_no | string | 是 | 申请单号 |

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": 1,
    "application_no": "DA61030020260319123456123",
    "city_code": "610300",
    "city_name": "宝鸡",
    "menu_code": "MENU_BJ_006",
    "menu_name": "慢病申报查询",
    "download_type": "export_excel",
    "download_purpose": "导出数据给医保局",
    "download_conditions": "时间范围：2026-3-1~2026-3-20; 表头字段：姓名、身份证号、手机号码、疾病类型、疾病名称",
    "applicant_id": "user001",
    "applicant_name": "张三",
    "applicant_account": "zhangsan",
    "created_time": "2026-03-19 10:30:00",
    "approval_status": 0,
    "approval_status_text": "未审核"
  },
  "success": true
}
```

---

#### GET /api/v1/approval/permission/cities
**功能**: 获取当前用户可审批的地市列表

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": [
    {"city_code": "610300", "city_name": "宝鸡"},
    {"city_code": "610600", "city_name": "延安"},
    {"city_code": "611000", "city_name": "商洛"}
  ],
  "success": true
}
```

---

#### POST /api/v1/download/validate
**功能**: 验证用户是否有权下载指定申请

**请求参数**:
```json
{
  "application_no": "DA61030020260319123456123"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "允许下载",
  "data": {
    "can_download": true,
    "file_path": "/downloads/DA61030020260319123456123.xlsx"
  },
  "success": true
}
```

---

## 二、错误码说明

| 错误码 | 说明 |
|-------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未登录或登录已过期 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 三、通用响应格式

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {},
  "success": true,
  "timestamp": "2026-03-19 10:30:00"
}
```
