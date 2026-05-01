# PICC门诊慢特病业务服务 - 核心API接口文档

> 📅 文档版本：V2.0  
> 🎯 适用对象：零基础开发人员、需求分析师、技术小白  
> 🔧 技术栈：Spring Boot + MyBatis + Activiti6 + GaussDB + Redis  
> 📊 统计口径：10个核心业务域，50+核心接口详细解析

---

## 📋 文档目录

1. [业务域一：慢病申报管理](#一慢病申报管理)
2. [业务域二：申报审批管理](#二申报审批管理)
3. [业务域三：支付/费用管理](#三支付费用管理)
4. [业务域四：药店管理](#四药店管理)
5. [业务域五：处方管理](#五处方管理)
6. [业务域六：复审管理](#六复审管理)
7. [业务域七：备案管理](#七备案管理)
8. [业务域八：数据统计](#八数据统计)
9. [业务域九：系统管理](#九系统管理)
10. [业务域十：用户认证](#十用户认证)

---

## 一、慢病申报管理

慢病申报是整个系统的核心入口，患者通过此模块提交慢特病待遇申请材料。

### 1.1 POST /MbDeclare/query — 查询线下申报记录

**用途**：查询已提交的线下申报记录，支持分页和条件筛选。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| pageNum | Integer | 否 | 页码，默认1 | 第几页？ |
| pageSize | Integer | 否 | 每页条数，默认10 | 每页显示几条？ |
| name | String | 否 | 姓名 | 搜索谁的申报？ |
| idcard | String | 否 | 身份证号 | 按身份证精确查找 |
| icdname | String | 否 | 疾病名称 | 查某种病的申报 |
| applyStatus | Integer | 否 | 申报状态 | 按状态筛选 |
| startDate | String | 否 | 申报开始日期 | 查哪段时间的？ |
| endDate | String | 否 | 申报结束日期 | 查哪段时间的？ |
| unitCode | String | 否 | 机构编码 | 查哪个网点的申报？ |

**请求示例**
```json
{
  "pageNum": 1,
  "pageSize": 10,
  "name": "张三",
  "applyStatus": 0,
  "startDate": "2024-01-01",
  "endDate": "2024-12-31"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码，0=成功 | 请求有没有成功？ |
| msg | String | 返回消息 | 成功或失败原因 |
| data | Object | 数据对象 | 查到的数据在这 |
| data.list | Array | 申报记录列表 | 符合条件的申报 |
| data.list[].id | String | 申报ID | 唯一标识这个申报 |
| data.list[].name | String | 姓名 | 患者叫什么 |
| data.list[].idcard | String | 身份证号(脱敏) | 如：610***********1234 |
| data.list[].icdname | String | 疾病名称 | 申请的什么病 |
| data.list[].applyStatus | Integer | 申报状态 | 0=审核中,1=通过,2=驳回 |
| data.list[].declaredate | String | 申报日期 | 什么时候提交的 |
| data.total | Integer | 总记录数 | 一共有多少条 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": {
    "pageNum": 1,
    "pageSize": 10,
    "total": 158,
    "list": [
      {
        "id": "20240115000001",
        "name": "张三",
        "idcard": "610***********1234",
        "icdname": "2型糖尿病",
        "applyStatus": 0,
        "declaredate": "2024-01-15 09:30:22"
      }
    ]
  }
}
```

**谁在调用**：窗口工作人员申报查询页面 `/MbDeclare/query`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 查询正常返回 |
| 1001 | 参数错误 | pageSize超过限制，请检查分页参数 |
| 2001 | 数据不存在 | 没有符合条件的申报记录 |
| 5000 | 系统异常 | 数据库连接超时，请稍后重试 |

**小白易懵点**：
- `applyStatus`状态值含义：0=审核中(黄灯)，1=初审通过(绿灯)，2=初审驳回(红灯)，3=审核通过(绿灯)，4=审核驳回(红灯)
- 身份证号在返回时会自动脱敏，中间部分用`*`代替
- 日期格式统一为`yyyy-MM-dd HH:mm:ss`

---

### 1.2 POST /MbDeclare/declare — 线下提交慢病申报

**用途**：窗口工作人员帮患者提交慢特病申报，将患者信息和申报材料打包入库。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| name | String | ✅ | 姓名 | 患者叫什么 |
| idcard | String | ✅ | 身份证号 | 患者身份证 |
| mobile | String | ✅ | 手机号 | 联系方式 |
| sex | String | ✅ | 性别 | M=男，F=女 |
| birthday | String | ✅ | 出生日期 | yyyy-MM-dd格式 |
| persontype | String | ✅ | 人员类型 | 3=职工医保，390=居民医保 |
| icdkind | String | ✅ | 疾病种类 | 大类，如：内分泌 |
| icdtype | String | ✅ | 疾病类型 | 小类，如：糖尿病 |
| icdcode | String | ✅ | 疾病编码 | 医保疾病编码 |
| icdname | String | ✅ | 疾病名称 | 完整病名 |
| medicalno | String | ✅ | 医保编号 | 患者的医保卡号 |
| fixedhoscode | String | ✅ | 定点医院编码 | 选哪家医院就医 |
| unitcode | String | ✅ | 申报机构编码 | 哪个窗口受理的 |
| remark | String | 否 | 备注 | 补充说明 |

**请求示例**
```json
{
  "name": "李四",
  "idcard": "610102199001011234",
  "mobile": "13800138000",
  "sex": "M",
  "birthday": "1990-01-01",
  "persontype": "3",
  "icdkind": "内分泌",
  "icdtype": "糖尿病",
  "icdcode": "E11",
  "icdname": "2型糖尿病",
  "medicalno": "P61010219900101123456",
  "fixedhoscode": "H61010001",
  "unitcode": "U610100"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功，其他=失败 |
| msg | String | 返回消息 | 成功或失败原因 |
| data | Object | 申报结果 | 返回申报信息 |
| data.declareid | String | 申报ID | 后续查询用这个ID |
| data.declareno | String | 申报编号 | 形式：DC+日期+序号 |

**返回示例**
```json
{
  "code": 0,
  "msg": "申报提交成功",
  "data": {
    "declareid": "20240115000000001",
    "declareno": "DC2024011500001"
  }
}
```

**谁在调用**：窗口工作人员申报填写页面 `/MbDeclare/declare`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 申报已提交 |
| 1002 | 身份证格式错误 | 检查身份证号是否18位 |
| 1003 | 手机号格式错误 | 检查手机号是否11位 |
| 1004 | 疾病编码不存在 | 请核实医保疾病编码 |
| 1005 | 该患者已有进行中的申报 | 避免重复申报 |
| 1006 | 定点医院不存在 | 检查医院编码 |

**小白易懵点**：
- `persontype`必须与医保系统一致，填错会导致后续报销失败
- `icdcode`是医保标准编码，不是医院内部编码
- 申报提交后会自动生成申报编号，后续查询都用这个编号

---

### 1.3 POST /MbDeclare/imageFiles — 批量上传申报图片材料

**用途**：上传患者的证件照片、病历照片等申报材料附件，支持批量上传。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| declareid | String | ✅ | 申报ID | 关联到哪个申报 |
| files | Array | ✅ | 文件列表 | 上传的图片数组 |
| files[].fileType | String | ✅ | 文件类型 | 1=身份证,2=病历,3=体检报告,4=其他 |
| files[].fileName | String | ✅ | 文件名 | 原始文件名 |
| files[].filePath | String | ✅ | 文件路径 | FTP服务器存储路径 |
| files[].fileSize | Long | 否 | 文件大小 | 字节数 |

**请求示例**
```json
{
  "declareid": "20240115000000001",
  "files": [
    {
      "fileType": "1",
      "fileName": "idcard_front.jpg",
      "filePath": "/upload/2024/01/15/idcard_001.jpg",
      "fileSize": 256000
    },
    {
      "fileType": "1",
      "fileName": "idcard_back.jpg",
      "filePath": "/upload/2024/01/15/idcard_002.jpg",
      "fileSize": 248000
    },
    {
      "fileType": "2",
      "fileName": "medical_report.pdf",
      "filePath": "/upload/2024/01/15/medical_001.pdf",
      "fileSize": 1024000
    }
  ]
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| msg | String | 返回消息 | 上传结果 |
| data | Array | 上传结果列表 | 每个文件的处理结果 |
| data[].fileId | String | 文件ID | 唯一标识文件 |
| data[].fileName | String | 文件名 | 文件名 |
| data[].fileType | String | 文件类型 | 类型代码 |
| data[].uploadStatus | String | 上传状态 | success=成功 |

**返回示例**
```json
{
  "code": 0,
  "msg": "文件上传成功",
  "data": [
    {
      "fileId": "F20240115000001",
      "fileName": "idcard_front.jpg",
      "fileType": "1",
      "uploadStatus": "success"
    },
    {
      "fileId": "F20240115000002",
      "fileName": "idcard_back.jpg",
      "fileType": "1",
      "uploadStatus": "success"
    },
    {
      "fileId": "F20240115000003",
      "fileName": "medical_report.pdf",
      "fileType": "2",
      "uploadStatus": "success"
    }
  ]
}
```

**谁在调用**：申报材料上传页面 `/MbDeclare/imageFiles`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 文件上传成功 |
| 2001 | 申报不存在 | declareid错误或申报已删除 |
| 3001 | 文件类型不支持 | 仅支持jpg/png/pdf格式 |
| 3002 | 文件大小超限 | 单文件不超过5MB |
| 3003 | FTP上传失败 | 服务器存储异常，请重试 |

**小白易懵点**：
- `fileType`类型代码：1=身份证正反面，2=病历资料，3=体检报告，4=其他证明材料
- 图片上传前需先调用FTP上传接口获取filePath
- 建议一次性把所有材料传完，避免遗漏

---

### 1.4 POST /MbDeclare/YiBaoCheck — 医保资格校验

**用途**：在提交申报前，先调用医保系统校验患者是否有参保资格，防止无效申报。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| idcard | String | ✅ | 身份证号 | 患者身份证 |
| name | String | ✅ | 姓名 | 患者姓名 |
| medicalno | String | ✅ | 医保编号 | 医保卡号 |
| icdcode | String | ✅ | 疾病编码 | 要申请的病种编码 |
| persontype | String | ✅ | 人员类型 | 3=职工，390=居民 |

**请求示例**
```json
{
  "idcard": "610102199001011234",
  "name": "李四",
  "medicalno": "P61010219900101123456",
  "icdcode": "E11",
  "persontype": "3"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | String | 结果码 | 1101=校验通过，其他=失败 |
| msg | String | 返回消息 | 校验结果描述 |
| data | Object | 医保信息 | 医保系统返回的信息 |
| data.insuredStatus | String | 参保状态 | 1=正常参保 |
| data.insureType | String | 险种类型 | 职工/居民 |
| data.balance | Decimal | 账户余额 | 医保卡余额 |
| data.validFlag | String | 有效标志 | Y=有效 |

**返回示例**
```json
{
  "code": "1101",
  "msg": "医保资格校验通过",
  "data": {
    "insuredStatus": "1",
    "insureType": "职工基本医疗保险",
    "balance": 1523.50,
    "validFlag": "Y"
  }
}
```

**谁在调用**：申报前置校验环节 `/MbDeclare/YiBaoCheck`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 1101 | 校验通过 | 可以继续申报 |
| 1102 | 人员未参保 | 该身份证未参加医保 |
| 1103 | 暂停参保 | 医保处于暂停状态 |
| 1104 | 病种不在目录 | 该病种不在慢特病目录 |
| 1105 | 年度报销额度已满 | 需等到下个年度 |

**小白易懵点**：
- 这是调用外部医保系统的接口，返回码1101代表校验成功
- 1101是固定的"成功码"，不是随便定的
- 校验失败时会有具体的医保返回码，可以反馈给患者

---

### 1.5 POST /MbImport/query — 慢病信息导入查询

**用途**：查询批量导入的慢病信息记录，支持分页查看导入历史和结果。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| pageNum | Integer | 否 | 页码 | 第几页？ |
| pageSize | Integer | 否 | 每页条数 | 每页几条？ |
| batchNo | String | 否 | 批次号 | 按批次查询 |
| importStatus | Integer | 否 | 导入状态 | 0=导入中,1=成功,2=失败 |
| startDate | String | 否 | 导入开始日期 | 查哪天的 |
| endDate | String | 否 | 导入结束日期 | 查哪天的 |

**请求示例**
```json
{
  "pageNum": 1,
  "pageSize": 20,
  "importStatus": 1,
  "startDate": "2024-01-01",
  "endDate": "2024-01-31"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data.list | Array | 导入记录列表 | 符合条件的结果 |
| data.list[].batchNo | String | 批次号 | 唯一标识这个批次 |
| data.list[].fileName | String | 文件名 | 导入的Excel文件名 |
| data.list[].totalCount | Integer | 总条数 | 导入文件总行数 |
| data.list[].successCount | Integer | 成功条数 | 成功导入的行数 |
| data.list[].failCount | Integer | 失败条数 | 导入失败的行数 |
| data.list[].importStatus | Integer | 导入状态 | 0=进行中,1=完成,2=失败 |
| data.list[].importDate | String | 导入时间 | 什么时候导入的 |
| data.list[].importUser | String | 导入人 | 谁导入的 |
| data.total | Integer | 总记录数 | 一共有多少批次 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": {
    "pageNum": 1,
    "pageSize": 20,
    "total": 5,
    "list": [
      {
        "batchNo": "IMP202401150001",
        "fileName": "慢病申报_20240115.xlsx",
        "totalCount": 100,
        "successCount": 95,
        "failCount": 5,
        "importStatus": 1,
        "importDate": "2024-01-15 14:30:00",
        "importUser": "admin"
      }
    ]
  }
}
```

**谁在调用**：批量导入管理页面 `/MbImport/query`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 查询正常返回 |
| 1001 | 参数错误 | 日期格式错误，应为yyyy-MM-dd |

**小白易懵点**：
- 批量导入适合医院或社区批量提交申报的场景
- 失败的数据可以在错误文件中查看失败原因

---

### 1.6 POST /MbDeclare/queryWorkUnit — 查询服务窗口

**用途**：获取系统中配置的所有服务窗口（申报受理点）信息，方便患者选择就近办理。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| districtCode | String | 否 | 区县编码 | 筛选特定区县 |
| windowType | String | 否 | 窗口类型 | 1=线上,2=线下 |

**请求示例**
```json
{
  "districtCode": "610102",
  "windowType": "2"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data | Array | 窗口列表 | 所有窗口信息 |
| data[].unitCode | String | 窗口编码 | 唯一标识 |
| data[].unitName | String | 窗口名称 | 如：XX区医保服务中心 |
| data[].address | String | 地址 | 详细地址 |
| data[].mobile | String | 联系电话 | 电话号码 |
| data[].workTime | String | 工作时间 | 如：周一至周五 9:00-17:00 |
| data[].latitude | Decimal | 纬度 | 用于地图显示 |
| data[].longitude | Decimal | 经度 | 用于地图显示 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": [
    {
      "unitCode": "U610102001",
      "unitName": "西安市雁塔区医保服务中心",
      "address": "西安市雁塔区雁塔西路178号",
      "mobile": "029-88888888",
      "workTime": "周一至周五 9:00-17:00",
      "latitude": 34.223,
      "longitude": 108.953
    },
    {
      "unitCode": "U610102002",
      "unitName": "西安市雁塔区街道服务站",
      "address": "西安市雁塔区小寨路100号",
      "mobile": "029-88888889",
      "workTime": "周一至周五 8:30-17:30",
      "latitude": 34.225,
      "longitude": 108.956
    }
  ]
}
```

**谁在调用**：申报页面下拉选择 / 小程序地图页面

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 返回窗口列表 |
| 1001 | 区域编码错误 | 检查districtCode是否正确 |

**小白易懵点**：
- 经纬度用于小程序地图展示"离我最近"的功能
- 窗口类型：1=线上（小程序/H5），2=线下（实体窗口）

---

## 二、申报审批管理

申报审批是对已提交的申报材料进行审核，包括初审和专家审批两个环节。

### 2.1 POST /MbDeclareFirstTrial/queryMbDeclareListInFirstTrail — 查询待初审申报列表

**用途**：初审工作人员查询需要自己审核的申报列表，按分页返回。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| pageNum | Integer | 否 | 页码 | 默认1 |
| pageSize | Integer | 否 | 每页条数 | 默认10 |
| name | String | 否 | 姓名 | 按姓名搜索 |
| idcard | String | 否 | 身份证号 | 按身份证搜索 |
| icdname | String | 否 | 疾病名称 | 按病种筛选 |
| applyStatus | Integer | 否 | 申报状态 | 见状态说明 |
| declareStartDate | String | 否 | 申报开始日期 | 时间范围 |
| declareEndDate | String | 否 | 申报结束日期 | 时间范围 |
| unitCode | String | 否 | 受理机构 | 哪个窗口报的 |
| sortField | String | 否 | 排序字段 | declaredate=申报时间 |
| sortOrder | String | 否 | 排序方向 | asc=升序,desc=降序 |

**请求示例**
```json
{
  "pageNum": 1,
  "pageSize": 10,
  "applyStatus": 0,
  "sortField": "declaredate",
  "sortOrder": "asc"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data.list | Array | 申报列表 | 待审核的申报 |
| data.list[].declareId | String | 申报ID | 唯一标识 |
| data.list[].declareno | String | 申报编号 | 如：DC202401150001 |
| data.list[].name | String | 姓名 | 患者姓名 |
| data.list[].idcard | String | 身份证号 | 脱敏显示 |
| data.list[].sex | String | 性别 | M/F |
| data.list[].age | Integer | 年龄 | 计算得出 |
| data.list[].mobile | String | 手机号 | 联系方式 |
| data.list[].icdkind | String | 疾病种类 | 大类 |
| data.list[].icdname | String | 疾病名称 | 具体病名 |
| data.list[].persontypeName | String | 人员类型名称 | 职工医保/居民医保 |
| data.list[].applyStatus | Integer | 申报状态 | 0=审核中 |
| data.list[].applyStatusName | String | 状态名称 | 待初审 |
| data.list[].declaredate | String | 申报日期 | 什么时候报的 |
| data.list[].fileCount | Integer | 材料数量 | 已上传几张材料 |
| data.list[].isneedPhysical | Integer | 是否需要体检 | 0=否,1=是 |
| data.total | Integer | 总记录数 | 一共多少条 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": {
    "pageNum": 1,
    "pageSize": 10,
    "total": 45,
    "list": [
      {
        "declareId": "20240115000001",
        "declareno": "DC202401150001",
        "name": "王五",
        "idcard": "610***********5678",
        "sex": "F",
        "age": 55,
        "mobile": "139****8901",
        "icdkind": "内分泌",
        "icdname": "2型糖尿病",
        "persontypeName": "职工医保",
        "applyStatus": 0,
        "applyStatusName": "待初审",
        "declaredate": "2024-01-15 10:00:00",
        "fileCount": 5,
        "isneedPhysical": 1
      }
    ]
  }
}
```

**谁在调用**：初审工作人员审核页面 `/MbDeclareFirstTrial/queryMbDeclareListInFirstTrail`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 查询正常 |
| 1001 | 参数错误 | 检查分页参数是否合理 |

**小白易懵点**：
- 初审只能看到`applyStatus=0`的申报
- `isneedPhysical=1`表示该病种需要体检才能通过

---

### 2.2 POST /MbDeclareFirstTrial/updateMbDeclareFirstApprovalInfo — 初审审批通过

**用途**：初审工作人员审核通过某条申报，自动判断是否需要体检或直接进入专家审批。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| declareId | String | ✅ | 申报ID | 要审核哪个 |
| approvalType | String | ✅ | 审批类型 | 固定值"0"表示通过 |
| approvalNote | String | 否 | 审批意见 | 补充说明 |
| isneedPhysical | Integer | 否 | 是否需要体检 | 0=不需要,1=需要(系统自动判断) |
| nextAssignType | String | 否 | 下一环节分配类型 | auto=自动,manual=手动 |

**请求示例**
```json
{
  "declareId": "20240115000001",
  "approvalType": "0",
  "approvalNote": "材料齐全，符合申报条件",
  "nextAssignType": "auto"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| msg | String | 返回消息 | 审批结果 |
| data | Object | 审批结果详情 | 详细信息 |
| data.declareId | String | 申报ID | 已审核的申报 |
| data.applyStatus | Integer | 新状态 | 1=初审通过 |
| data.isneedPhysical | Integer | 是否需体检 | 1=需要,0=不需要 |

**返回示例**
```json
{
  "code": 0,
  "msg": "初审通过，申报已进入下一环节",
  "data": {
    "declareId": "20240115000001",
    "applyStatus": 1,
    "isneedPhysical": 0,
    "nextStep": "专家审批"
  }
}
```

**谁在调用**：初审审核操作按钮 `/MbDeclareFirstTrial/updateMbDeclareFirstApprovalInfo`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 初审通过 |
| 2001 | 申报不存在 | declareId错误 |
| 2002 | 状态已变更 | 已被其他人员审核 |
| 2003 | 材料不完整 | 上传材料不足，请先驳回补充 |

**小白易懵点**：
- `approvalType`固定为"0"表示通过，"1"表示驳回
- 系统会自动判断该病种是否需要体检
- 审核通过后申报状态变为1，系统自动流转到下一环节

---

### 2.3 POST /MbDeclareFirstTrial/updateMbDeclareReviewApprovalInfo — 初审不予通过

**用途**：初审工作人员驳回申报，填写驳回原因，要求患者补充材料。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| declareId | String | ✅ | 申报ID | 要驳回哪个 |
| approvalType | String | ✅ | 审批类型 | 固定值"1"表示驳回 |
| approvalNote | String | ✅ | 驳回原因 | 必须填写！ |
| rejectType | String | 否 | 驳回类型 | 1=材料不全,2=信息错误,3=不符合条件 |

**请求示例**
```json
{
  "declareId": "20240115000001",
  "approvalType": "1",
  "rejectType": "1",
  "approvalNote": "缺少近三个月内的血糖检查报告，请补充后重新提交"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| msg | String | 返回消息 | 驳回结果 |
| data | Object | 驳回结果详情 | 详细信息 |
| data.declareId | String | 申报ID | 已驳回的申报 |
| data.applyStatus | Integer | 新状态 | 2=初审驳回 |

**返回示例**
```json
{
  "code": 0,
  "msg": "申报已驳回，已短信通知患者",
  "data": {
    "declareId": "20240115000001",
    "applyStatus": 2,
    "notifyMobile": "138****8000",
    "rejectTime": "2024-01-15 15:30:00"
  }
}
```

**谁在调用**：初审驳回操作 `/MbDeclareFirstTrial/updateMbDeclareReviewApprovalInfo`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 驳回成功 |
| 1004 | 驳回原因必填 | approvalNote不能为空 |
| 2001 | 申报不存在 | declareId错误 |

**小白易懵点**：
- 驳回原因必填，且会通过短信通知患者
- 患者可以在小程序查看驳回原因并重新上传材料

---

### 2.4 POST /MbDeclareFirstTrial/getVipMbDeclareFileTypesByDeclareId — 查看申报附件分类信息

**用途**：获取某条申报的所有上传材料，按类型分类展示。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| declareId | String | ✅ | 申报ID | 查看哪个申报的材料 |

**请求示例**
```json
{
  "declareId": "20240115000001"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data | Array | 分类材料列表 | 按类型分组 |
| data[].fileType | String | 材料类型 | 1=身份证,2=病历等 |
| data[].fileTypeName | String | 类型名称 | 身份证正反面 |
| data[].files | Array | 文件列表 | 该类型的所有文件 |
| data[].files[].fileId | String | 文件ID | 唯一标识 |
| data[].files[].fileName | String | 文件名 | 显示文件名 |
| data[].files[].filePath | String | 预览URL | 点击可预览 |
| data[].files[].uploadTime | String | 上传时间 | 什么时候上传的 |
| data[].files[].isComplete | Integer | 是否完整 | 1=完整,0=缺失 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": [
    {
      "fileType": "1",
      "fileTypeName": "身份证",
      "files": [
        {
          "fileId": "F20240115000001",
          "fileName": "身份证正面.jpg",
          "filePath": "https://xxx.com/preview/F20240115000001",
          "uploadTime": "2024-01-15 10:05:00",
          "isComplete": 1
        },
        {
          "fileId": "F20240115000002",
          "fileName": "身份证背面.jpg",
          "filePath": "https://xxx.com/preview/F20240115000002",
          "uploadTime": "2024-01-15 10:05:00",
          "isComplete": 1
        }
      ]
    },
    {
      "fileType": "2",
      "fileTypeName": "病历资料",
      "files": [
        {
          "fileId": "F20240115000003",
          "fileName": "门诊病历.pdf",
          "filePath": "https://xxx.com/preview/F20240115000003",
          "uploadTime": "2024-01-15 10:06:00",
          "isComplete": 1
        }
      ]
    }
  ]
}
```

**谁在调用**：初审审核详情页查看材料

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 材料查询正常 |
| 2001 | 申报不存在 | declareId错误 |

**小白易懵点**：
- 材料按类型分组显示，方便审核人员逐项检查
- 支持点击文件查看大图或下载

---

### 2.5 POST /MbExpertList/queryMbExpertList — 查询专家列表

**用途**：获取可分配的专家医生列表，用于手动分配专家审批任务。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| icdcode | String | 否 | 疾病编码 | 筛选擅长该病种的专家 |
| districtCode | String | 否 | 区县编码 | 筛选该区域专家 |
| expertType | String | 否 | 专家类型 | 1=内分泌,2=心血管等 |
| status | Integer | 否 | 状态 | 1=在用,0=停用 |

**请求示例**
```json
{
  "icdcode": "E11",
  "status": 1
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data | Array | 专家列表 | 可分配的专家 |
| data[].expertId | String | 专家ID | 唯一标识 |
| data[].expertName | String | 专家姓名 | 医生姓名 |
| data[].hospitalName | String | 医院名称 | 所属医院 |
| data[].department | String | 科室 | 所属科室 |
| data[].title | String | 职称 | 主任医师/副主任医师等 |
| data[].specialties | String | 擅长领域 | 擅长哪些病种 |
| data[].workload | Integer | 当前待审数 | 还有多少待审核 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": [
    {
      "expertId": "EXP20240001",
      "expertName": "张主任",
      "hospitalName": "西安市第一医院",
      "department": "内分泌科",
      "title": "主任医师",
      "specialties": "糖尿病,甲状腺疾病",
      "workload": 5
    },
    {
      "expertId": "EXP20240002",
      "expertName": "李副主任",
      "hospitalName": "西安市第二医院",
      "department": "内分泌科",
      "title": "副主任医师",
      "specialties": "糖尿病,高血压",
      "workload": 3
    }
  ]
}
```

**谁在调用**：专家分配页面

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 返回专家列表 |
| 1001 | 参数错误 | 疾病编码不存在 |

**小白易懵点**：
- `workload`显示专家当前待审核数量，方便合理分配
- 专家按擅长领域划分，确保专业对口

---

## 三、支付/费用管理

费用管理模块处理患者的账户余额、消费、退费等业务。

### 3.1 POST /VipChronicPay/VIPQueryChronicBalance — 查询慢病账户余额

**用途**：查询患者的慢特病账户余额，用于确认可用额度。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| accountId | String | ✅ | 账户ID | 要查哪个账户 |

**请求示例**
```json
{
  "accountId": "ACC202401150001"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| msg | String | 返回消息 | 查询结果 |
| data | Object | 账户信息 | 余额详情 |
| data.accountId | String | 账户ID | 账户唯一标识 |
| data.accountName | String | 账户姓名 | 患者姓名 |
| data.totalQuota | Decimal | 年度总额度 | 今年一共多少额度 |
| data.usedQuota | Decimal | 已用额度 | 已经报销了多少 |
| data.balanceQuota | Decimal | 剩余额度 | 还能报销多少 |
| data.validStartDate | String | 有效期开始 | 额度从哪天开始 |
| data.validEndDate | String | 有效期结束 | 额度到哪天结束 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": {
    "accountId": "ACC202401150001",
    "accountName": "李四",
    "totalQuota": 5000.00,
    "usedQuota": 1234.56,
    "balanceQuota": 3765.44,
    "validStartDate": "2024-01-01",
    "validEndDate": "2024-12-31"
  }
}
```

**谁在调用**：患者端余额查询页面 `/VipChronicPay/VIPQueryChronicBalance`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 返回账户信息 |
| 2001 | 账户不存在 | accountId错误或账户已注销 |

**小白易懵点**：
- 额度每年清零重新计算，注意`validEndDate`
- 剩余额度`balanceQuota`是患者最关心的数字

---

### 3.2 POST /VipChronicPay/VIPChronicPay — 会员消费扣款

**用途**：药店销售药品后，调用此接口进行医保账户扣款结算。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| accountId | String | ✅ | 账户ID | 哪个患者的账户 |
| orderNo | String | ✅ | 订单号 | 唯一订单标识 |
| drugStoreCode | String | ✅ | 药店编码 | 哪家药店 |
| totalAmount | Decimal | ✅ | 消费总金额 | 药品总价 |
| selfPayAmount | Decimal | ✅ | 自付金额 | 患者自己掏的钱 |
| accountPayAmount | Decimal | ✅ | 账户扣款 | 从医保账户扣的钱 |
| drugList | Array | ✅ | 药品清单 | 买了哪些药 |
| drugList[].drugCode | String | ✅ | 药品编码 | 药品唯一编码 |
| drugList[].drugName | String | ✅ | 药品名称 | 药品名字 |
| drugList[].quantity | Integer | ✅ | 数量 | 买了几盒 |
| drugList[].price | Decimal | ✅ | 单价 | 每盒多少钱 |
| drugList[].reimburseRatio | Decimal | ✅ | 报销比例 | 如：0.8表示80%报销 |

**请求示例**
```json
{
  "accountId": "ACC202401150001",
  "orderNo": "ORD20240115100001",
  "drugStoreCode": "DS61010001",
  "totalAmount": 150.00,
  "selfPayAmount": 30.00,
  "accountPayAmount": 120.00,
  "drugList": [
    {
      "drugCode": "D20240001",
      "drugName": "二甲双胍缓释片",
      "quantity": 2,
      "price": 25.00,
      "reimburseRatio": 0.8
    },
    {
      "drugCode": "D20240002",
      "drugName": "阿卡波糖片",
      "quantity": 1,
      "price": 100.00,
      "reimburseRatio": 0.8
    }
  ]
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| msg | String | 返回消息 | 结算结果 |
| data | Object | 结算详情 | 详细结果 |
| data.orderNo | String | 订单号 | 订单唯一标识 |
| data.accountId | String | 账户ID | 扣款账户 |
| data.totalAmount | Decimal | 消费总额 | 多少钱 |
| data.selfPayAmount | Decimal | 自付金额 | 患者掏了 |
| data.accountPayAmount | Decimal | 账户扣款 | 医保扣了 |
| data.balanceBefore | Decimal | 扣款前余额 | 原来有多少 |
| data.balanceAfter | Decimal | 扣款后余额 | 还剩多少 |
| data.payTime | String | 扣款时间 | 什么时候扣的 |

**返回示例**
```json
{
  "code": 0,
  "msg": "结算成功",
  "data": {
    "orderNo": "ORD20240115100001",
    "accountId": "ACC202401150001",
    "totalAmount": 150.00,
    "selfPayAmount": 30.00,
    "accountPayAmount": 120.00,
    "balanceBefore": 3765.44,
    "balanceAfter": 3645.44,
    "payTime": "2024-01-15 16:30:00"
  }
}
```

**谁在调用**：药店收银系统 `/VipChronicPay/VIPChronicPay`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 结算成功 |
| 3001 | 余额不足 | balanceQuota不够扣 |
| 3002 | 账户已冻结 | 联系医保局解冻 |
| 3003 | 额度已用完 | 年度额度用完了 |
| 3004 | 订单已结算 | 防止重复扣款 |
| 3005 | 药品不在目录 | 药品未纳入慢病报销 |

**小白易懵点**：
- `reimburseRatio`是报销比例，如0.8表示80%报销，患者只需付20%
- 余额不足时，优先扣自付部分，不足则交易失败
- `orderNo`必须唯一，重复提交会被拒绝

---

### 3.3 POST /VipChronicPay/VIPChronicRefund — 会员账户退款

**用途**：药店需要对已结算的订单进行退款时调用此接口。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| orderNo | String | ✅ | 原订单号 | 要退哪个订单 |
| refundAmount | Decimal | ✅ | 退款金额 | 退多少钱 |
| refundReason | String | ✅ | 退款原因 | 为什么要退 |
| refundType | String | 否 | 退款类型 | full=全额,partial=部分 |

**请求示例**
```json
{
  "orderNo": "ORD20240115100001",
  "refundAmount": 120.00,
  "refundReason": "药品数量有误，已重新结算",
  "refundType": "full"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| msg | String | 返回消息 | 退款结果 |
| data | Object | 退款详情 | 详细结果 |
| data.orderNo | String | 原订单号 | 退的哪个订单 |
| data.refundNo | String | 退款单号 | 退款唯一标识 |
| data.refundAmount | Decimal | 退款金额 | 退了多少钱 |
| data.balanceAfter | Decimal | 退款后余额 | 账户新余额 |

**返回示例**
```json
{
  "code": 0,
  "msg": "退款成功",
  "data": {
    "orderNo": "ORD20240115100001",
    "refundNo": "REF20240115100001",
    "refundAmount": 120.00,
    "balanceAfter": 3765.44,
    "refundTime": "2024-01-15 17:00:00"
  }
}
```

**谁在调用**：药店收银退款操作 `/VipChronicPay/VIPChronicRefund`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 退款成功 |
| 4001 | 订单不存在 | 订单号错误 |
| 4002 | 订单已退款 | 不要重复退款 |
| 4003 | 退款金额超限 | 不能超过原订单金额 |

**小白易懵点**：
- 退款金额不能超过原订单的账户扣款部分
- 退款后额度返还到账户余额

---

### 3.4 POST /VipAccount/qureyFLowDetailList — 查询会员消费流水

**用途**：查询患者的账户消费明细记录，了解资金流向。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| accountId | String | ✅ | 账户ID | 查哪个账户 |
| pageNum | Integer | 否 | 页码 | 默认1 |
| pageSize | Integer | 否 | 每页条数 | 默认10 |
| flowType | String | 否 | 流水类型 | 1=消费,2=退款,3=返还 |
| startDate | String | 否 | 开始日期 | 时间范围 |
| endDate | String | 否 | 结束日期 | 时间范围 |

**请求示例**
```json
{
  "accountId": "ACC202401150001",
  "pageNum": 1,
  "pageSize": 20,
  "flowType": "1",
  "startDate": "2024-01-01",
  "endDate": "2024-01-31"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data.list | Array | 流水列表 | 消费记录 |
| data.list[].flowNo | String | 流水号 | 唯一标识 |
| data.list[].orderNo | String | 订单号 | 关联订单 |
| data.list[].flowType | String | 流水类型 | 1=消费,2=退款 |
| data.list[].flowTypeName | String | 类型名称 | 消费/退款 |
| data.list[].amount | Decimal | 金额 | 多少钱 |
| data.list[].balanceBefore | Decimal | 变动前余额 | 原来多少 |
| data.list[].balanceAfter | Decimal | 变动后余额 | 现在多少 |
| data.list[].merchantName | String | 商家名称 | 哪家药店 |
| data.list[].drugSummary | String | 药品摘要 | 买了什么药 |
| data.list[].createTime | String | 发生时间 | 什么时候 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": {
    "pageNum": 1,
    "pageSize": 20,
    "total": 35,
    "list": [
      {
        "flowNo": "FLOW20240115100001",
        "orderNo": "ORD20240115100001",
        "flowType": "1",
        "flowTypeName": "消费",
        "amount": -120.00,
        "balanceBefore": 3765.44,
        "balanceAfter": 3645.44,
        "merchantName": "XX大药房(科技路店)",
        "drugSummary": "二甲双胍缓释片等2种药品",
        "createTime": "2024-01-15 16:30:00"
      },
      {
        "flowNo": "FLOW20240110000001",
        "orderNo": "ORD20240110100001",
        "flowType": "2",
        "flowTypeName": "退款",
        "amount": 50.00,
        "balanceBefore": 3595.44,
        "balanceAfter": 3645.44,
        "merchantName": "XX大药房(科技路店)",
        "drugSummary": "阿卡波糖片(退款)",
        "createTime": "2024-01-10 14:20:00"
      }
    ]
  }
}
```

**谁在调用**：患者端账单明细页面 `/VipAccount/qureyFLowDetailList`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 查询正常 |
| 2001 | 账户不存在 | accountId错误 |

**小白易懵点**：
- 消费金额为负数，退款金额为正数
- `drugSummary`只显示摘要，详情可点击查看

---

## 四、药店管理

药店管理模块处理医保定点药店的信息维护、订单管理和药品管理。

### 4.1 POST /drugstore/enter — 药店缴费/退费查询

**用途**：查询药店的缴费订单或退费订单列表。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| pageNum | Integer | 否 | 页码 | 默认1 |
| pageSize | Integer | 否 | 每页条数 | 默认10 |
| queryType | String | ✅ | 查询类型 | pay=缴费,refund=退费 |
| orderNo | String | 否 | 订单号 | 精确查询 |
| patientName | String | 否 | 患者姓名 | 模糊查询 |
| startDate | String | 否 | 开始日期 | 时间范围 |
| endDate | String | 否 | 结束日期 | 时间范围 |

**请求示例**
```json
{
  "pageNum": 1,
  "pageSize": 10,
  "queryType": "pay",
  "startDate": "2024-01-01",
  "endDate": "2024-01-31"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data.list | Array | 订单列表 | 查询结果 |
| data.list[].orderNo | String | 订单号 | 唯一标识 |
| data.list[].patientName | String | 患者姓名 | 谁买的 |
| data.list[].idcard | String | 身份证号 | 脱敏显示 |
| data.list[].totalAmount | Decimal | 消费总额 | 多少钱 |
| data.list[].accountPay | Decimal | 账户支付 | 医保扣了多少 |
| data.list[].selfPay | Decimal | 自付金额 | 患者掏了多少 |
| data.list[].orderStatus | String | 订单状态 | 已结算/已退款等 |
| data.list[].drugCount | Integer | 药品数量 | 买了几个品种 |
| data.list[].createTime | String | 下单时间 | 什么时候买的 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": {
    "pageNum": 1,
    "pageSize": 10,
    "total": 128,
    "list": [
      {
        "orderNo": "ORD20240115100001",
        "patientName": "李四",
        "idcard": "610***********1234",
        "totalAmount": 150.00,
        "accountPay": 120.00,
        "selfPay": 30.00,
        "orderStatus": "已结算",
        "drugCount": 2,
        "createTime": "2024-01-15 16:30:00"
      }
    ]
  }
}
```

**谁在调用**：药店后台订单管理页面 `/drugstore/enter`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 查询正常 |
| 1001 | queryType必填 | 必须指定pay或refund |

**小白易懵点**：
- `queryType`区分查询缴费订单还是退费订单
- 订单号格式：`ORD`开头

---

### 4.2 POST /drugstore/detail — 缴费/退费详情查询

**用途**：查询某条订单的详细信息，包括药品明细。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| orderNo | String | ✅ | 订单号 | 要查哪个订单 |

**请求示例**
```json
{
  "orderNo": "ORD20240115100001"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data | Object | 订单详情 | 完整信息 |
| data.orderNo | String | 订单号 | 唯一标识 |
| data.orderType | String | 订单类型 | pay=消费,refund=退款 |
| data.patientName | String | 患者姓名 | 谁买的 |
| data.idcard | String | 身份证号 | 患者身份证 |
| data.mobile | String | 手机号 | 联系方式 |
| data.totalAmount | Decimal | 消费总额 | 订单总金额 |
| data.accountPay | Decimal | 账户支付 | 医保扣款 |
| data.selfPay | Decimal | 自付金额 | 患者自付 |
| data.drugList | Array | 药品明细 | 买的药列表 |
| data.drugList[].drugName | String | 药品名称 | 药品名 |
| data.drugList[].specs | String | 规格 | 包装规格 |
| data.drugList[].quantity | Integer | 数量 | 几盒 |
| data.drugList[].price | Decimal | 单价 | 每盒价格 |
| data.drugList[].reimburseRatio | Decimal | 报销比例 | 报销多少 |
| data.drugList[].amount | Decimal | 小计 | 这项多少钱 |
| data.createTime | String | 下单时间 | 什么时候 |
| data.payTime | String | 支付时间 | 什么时候付的 |
| data.pharmacyName | String | 药店名称 | 哪家店 |
| data.pharmacyAddress | String | 药店地址 | 药店地址 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": {
    "orderNo": "ORD20240115100001",
    "orderType": "pay",
    "patientName": "李四",
    "idcard": "610***********1234",
    "mobile": "138****8000",
    "totalAmount": 150.00,
    "accountPay": 120.00,
    "selfPay": 30.00,
    "drugList": [
      {
        "drugName": "二甲双胍缓释片",
        "specs": "0.5g*30片",
        "quantity": 2,
        "price": 25.00,
        "reimburseRatio": 0.8,
        "amount": 50.00
      },
      {
        "drugName": "阿卡波糖片",
        "specs": "50mg*30片",
        "quantity": 1,
        "price": 100.00,
        "reimburseRatio": 0.8,
        "amount": 100.00
      }
    ],
    "createTime": "2024-01-15 16:25:00",
    "payTime": "2024-01-15 16:30:00",
    "pharmacyName": "XX大药房(科技路店)",
    "pharmacyAddress": "西安市雁塔区科技路100号"
  }
}
```

**谁在调用**：订单详情页面 `/drugstore/detail`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 查询成功 |
| 2001 | 订单不存在 | orderNo错误 |

**小白易懵点**：
- 药品明细中，`reimburseRatio=0.8`表示80%报销
- `amount` = 单价 × 数量

---

### 4.3 POST /vipDrugstoreProductList/queryProductList — 查询药店药品列表

**用途**：查询药店可销售的慢特病药品目录。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| pageNum | Integer | 否 | 页码 | 默认1 |
| pageSize | Integer | 否 | 每页条数 | 默认20 |
| keyword | String | 否 | 关键词 | 搜索药品名/编码 |
| drugType | String | 否 | 药品分类 | 口服/注射等 |
| icdcode | String | 否 | 关联病种 | 哪些病能用 |

**请求示例**
```json
{
  "pageNum": 1,
  "pageSize": 20,
  "keyword": "二甲双胍",
  "icdcode": "E11"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data.list | Array | 药品列表 | 搜索结果 |
| data.list[].drugCode | String | 药品编码 | 唯一标识 |
| data.list[].drugName | String | 药品名称 | 通用名 |
| data.list[].tradeName | String | 商品名称 | 品牌名 |
| data.list[].specs | String | 规格 | 包装规格 |
| data.list[].manufacturer | String | 生产企业 | 哪家药厂 |
| data.list[].unit | String | 单位 | 盒/瓶 |
| data.list[].price | Decimal | 零售价 | 售价 |
| data.list[].reimbursePrice | Decimal | 报销价 | 医保认定的价格 |
| data.list[].reimburseRatio | Decimal | 报销比例 | 80%=0.8 |
| data.list[].stock | Integer | 库存 | 还剩多少 |
| data.total | Integer | 总记录数 | 一共多少药品 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": {
    "pageNum": 1,
    "pageSize": 20,
    "total": 5,
    "list": [
      {
        "drugCode": "D20240001",
        "drugName": "二甲双胍缓释片",
        "tradeName": "格华止",
        "specs": "0.5g*30片",
        "manufacturer": "中美上海施贵宝制药",
        "unit": "盒",
        "price": 25.00,
        "reimbursePrice": 25.00,
        "reimburseRatio": 0.8,
        "stock": 500
      }
    ]
  }
}
```

**谁在调用**：药店进销存系统 / 患者端搜索药品

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 查询正常 |
| 1001 | 参数错误 | 分页参数超限 |

**小白易懵点**：
- `reimburseRatio`决定报销比例，患者实际支付 = price × (1-reimburseRatio)
- 库存为0时无法销售

---

### 4.4 POST /vipDrugstoreOrderReport/exportDrugstoreOrderReportList — 药店订单数据导出

**用途**：导出药店的订单数据为Excel，用于对账和统计。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| startDate | String | ✅ | 开始日期 | 导出范围开始 |
| endDate | String | ✅ | 结束日期 | 导出范围结束 |
| orderStatus | String | 否 | 订单状态 | 筛选状态 |
| exportFormat | String | 否 | 导出格式 | 默认xlsx |

**请求示例**
```json
{
  "startDate": "2024-01-01",
  "endDate": "2024-01-31",
  "orderStatus": "paid",
  "exportFormat": "xlsx"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| msg | String | 返回消息 | 处理结果 |
| data | Object | 导出信息 | 文件信息 |
| data.fileName | String | 文件名 | 导出的文件名 |
| data.fileUrl | String | 下载地址 | 文件下载地址 |

**返回示例**
```json
{
  "code": 0,
  "msg": "导出成功",
  "data": {
    "fileName": "药店订单报表_20240101_20240131.xlsx",
    "fileUrl": "https://xxx.com/download/DR20240115001.xlsx"
  }
}
```

**谁在调用**：药店对账导出功能 `/vipDrugstoreOrderReport/exportDrugstoreOrderReportList`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 导出成功 |
| 5001 | 数据量过大 | 导出条数超过10000条，请缩小范围 |
| 5002 | 导出失败 | 服务器异常，请重试 |

**小白易懵点**：
- 导出数据量过大会导致超时，建议按月导出
- 下载链接有效期24小时

---

## 五、处方管理

处方管理模块处理医生开具的处方笺，包括上传、审核、录入药品等操作。

### 5.1 POST /getPrescription/getPrescription — 查询处方信息

**用途**：查询某个患者的处方列表，支持查看处方详情和药品信息。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| accountId | String | ✅ | 账户ID | 查哪个患者的处方 |
| pageNum | Integer | 否 | 页码 | 默认1 |
| pageSize | Integer | 否 | 每页条数 | 默认10 |
| icdType | String | 否 | 疾病类型 | 筛选病种 |
| prescriptionStatus | Integer | 否 | 处方状态 | 0=待审核,1=已录入 |

**请求示例**
```json
{
  "accountId": "ACC202401150001",
  "pageNum": 1,
  "pageSize": 10,
  "prescriptionStatus": 0
}
```

**返回参数**
| 字段 |类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data.list | Array | 处方列表 | 查询结果 |
| data.list[].prescriptionId | String | 处方ID | 唯一标识 |
| data.list[].prescriptionNo | String | 处方号 | 医院处方编号 |
| data.list[].hospitalName | String | 医院名称 | 哪家医院开的 |
| data.list[].department | String | 科室 | 哪个科室 |
| data.list[].doctorName | String | 医生姓名 | 谁开的 |
| data.list[].diagnoseDate | String | 开方日期 | 什么时候开的 |
| data.list[].prescriptionStatus | Integer | 处方状态 | 0=待录入,1=已录入 |
| data.list[].drugCount | Integer | 药品数量 | 有几种药 |
| data.list[].uploadTime | String | 上传时间 | 什么时候上传的 |
| data.total | Integer | 总记录数 | 一共多少处方 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": {
    "pageNum": 1,
    "pageSize": 10,
    "total": 15,
    "list": [
      {
        "prescriptionId": "PR202401150001",
        "prescriptionNo": "CF202401150001",
        "hospitalName": "西安市第一医院",
        "department": "内分泌科",
        "doctorName": "王医生",
        "diagnoseDate": "2024-01-10",
        "prescriptionStatus": 0,
        "drugCount": 3,
        "uploadTime": "2024-01-15 10:00:00"
      }
    ]
  }
}
```

**谁在调用**：处方管理列表页 `/getPrescription/getPrescription`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 查询正常 |
| 2001 | 账户不存在 | accountId错误 |

**小白易懵点**：
- 处方号`prescriptionNo`是医院系统的编号，不是我们系统的
- `prescriptionStatus=0`表示待录入药品，需要工作人员处理

---

### 5.2 POST /getPrescription/getOCRPrescription — OCR处方图片识别结果回显

**用途**：上传处方图片后，调用OCR识别自动提取文字，返回识别结果供人工核对。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| accountId | String | ✅ | 账户ID | 关联哪个患者 |
| prescriptionId | String | 否 | 处方ID | 编辑时传入 |
| fileId | String | ✅ | 文件ID | 上传后的图片ID |

**请求示例**
```json
{
  "accountId": "ACC202401150001",
  "fileId": "F20240115000001"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data | Object | 识别结果 | OCR提取的信息 |
| data.fileId | String | 文件ID | 图片ID |
| data.originalImage | String | 原图地址 | 原始图片URL |
| data.ocrResult | String | OCR文本 | 识别出的文字 |
| data.drugList | Array | 识别出的药品 | 自动提取的药品 |
| data.drugList[].drugName | String | 药品名称 | 识别结果 |
| data.drugList[].quantity | String | 数量 | 识别结果 |
| data.drugList[].specs | String | 规格 | 识别结果 |
| data.confidence | Decimal | 识别置信度 | 0-1之间 |

**返回示例**
```json
{
  "code": 0,
  "msg": "识别成功",
  "data": {
    "fileId": "F20240115000001",
    "originalImage": "https://xxx.com/images/prescription/001.jpg",
    "ocrResult": "处方笺\n西安市第一医院\n科室内分泌科\n诊断：2型糖尿病\n\n二甲双胍缓释片 0.5g*30片 2盒\n阿卡波糖片 50mg*30片 1盒",
    "drugList": [
      {
        "drugName": "二甲双胍缓释片",
        "quantity": "2盒",
        "specs": "0.5g*30片",
        "confidence": 0.95
      },
      {
        "drugName": "阿卡波糖片",
        "quantity": "1盒",
        "specs": "50mg*30片",
        "confidence": 0.92
      }
    ]
  }
}
```

**谁在调用**：处方上传识别页面 `/getPrescription/getOCRPrescription`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 识别成功 |
| 6001 | OCR识别失败 | 图片不清晰，请重新上传 |
| 6002 | 未识别到药品 | 处方格式不规范 |

**小白易懵点**：
- OCR识别结果仅供参考，需要人工核对确认
- `confidence`越接近1表示识别越准确

---

### 5.3 POST /getPrescription/insertDrug — 存储处方药品信息

**用途**：将医生开具的药品录入系统，与处方关联存储。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| prescriptionId | String | ✅ | 处方ID | 关联哪个处方 |
| accountId | String | ✅ | 账户ID | 哪个患者 |
| drugList | Array | ✅ | 药品列表 | 要录入的药品 |
| drugList[].drugCode | String | ✅ | 药品编码 | 来自药品目录 |
| drugList[].drugName | String | ✅ | 药品名称 | 药品名 |
| drugList[].specs | String | 否 | 规格 | 包装规格 |
| drugList[].quantity | Integer | ✅ | 数量 | 几盒/几瓶 |
| drugList[].price | Decimal | ✅ | 单价 | 每盒价格 |
| drugList[].doseonce | String | 否 | 单次剂量 | 每次吃多少 |
| drugList[].frequency | String | 否 | 用药频率 | 一天几次 |
| drugList[].administration | String | 否 | 给药途径 | 口服/注射 |

**请求示例**
```json
{
  "prescriptionId": "PR202401150001",
  "accountId": "ACC202401150001",
  "drugList": [
    {
      "drugCode": "D20240001",
      "drugName": "二甲双胍缓释片",
      "specs": "0.5g*30片",
      "quantity": 2,
      "price": 25.00,
      "doseonce": "1片",
      "frequency": "每日1次",
      "administration": "口服"
    },
    {
      "drugCode": "D20240002",
      "drugName": "阿卡波糖片",
      "specs": "50mg*30片",
      "quantity": 1,
      "price": 100.00,
      "doseonce": "1片",
      "frequency": "每日3次",
      "administration": "口服"
    }
  ]
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| msg | String | 返回消息 | 处理结果 |
| data | Object | 录入结果 | 详情 |
| data.prescriptionId | String | 处方ID | 已录入的处方 |
| data.drugCount | Integer | 录入数量 | 成功录入几种 |

**返回示例**
```json
{
  "code": 0,
  "msg": "药品录入成功",
  "data": {
    "prescriptionId": "PR202401150001",
    "drugCount": 2,
    "录入时间": "2024-01-15 10:30:00"
  }
}
```

**谁在调用**：处方药品录入页面 `/getPrescription/insertDrug`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 录入成功 |
| 7001 | 药品编码不存在 | drugCode错误 |
| 7002 | 药品不在目录 | 该药品未纳入报销范围 |

**小白易懵点**：
- `drugCode`必须来自系统药品目录，不能随意填写
- 录入后需要点击"完成"按钮才算正式提交

---

### 5.4 POST /getPrescription/rejectSingleImg — 单张处方图片驳回

**用途**：审核人员发现某张处方图片有问题，单独驳回让患者重新上传。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| prescriptionId | String | ✅ | 处方ID | 驳回哪个处方 |
| fileId | String | ✅ | 文件ID | 驳回哪张图片 |
| rejectReason | String | ✅ | 驳回原因 | 必须填写！ |

**请求示例**
```json
{
  "prescriptionId": "PR202401150001",
  "fileId": "F20240115000001",
  "rejectReason": "处方图片不清晰，请重新上传清晰的处方照片"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| msg | String | 返回消息 | 驳回结果 |
| data | Object | 处理结果 | 详情 |
| data.prescriptionId | String | 处方ID | 已驳回的处方 |
| data.fileId | String | 文件ID | 已驳回的文件 |
| data.notifyPatient | Boolean | 是否通知患者 | true=已发短信 |

**返回示例**
```json
{
  "code": 0,
  "msg": "处方已驳回，患者已收到通知",
  "data": {
    "prescriptionId": "PR202401150001",
    "fileId": "F20240115000001",
    "notifyPatient": true,
    "rejectTime": "2024-01-15 11:00:00"
  }
}
```

**谁在调用**：处方审核驳回操作 `/getPrescription/rejectSingleImg`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 驳回成功 |
| 8001 | 驳回原因必填 | 必须填写rejectReason |
| 2001 | 处方不存在 | prescriptionId错误 |

**小白易懵点**：
- 驳回后系统会自动发短信通知患者
- 患者可以在小程序重新上传清晰的图片

---

## 六、复审管理

复审管理是对已享受慢特病待遇的患者进行年度审核，确认是否仍需继续享受待遇。

### 6.1 POST /MbReview/query — 查询慢病复审记录

**用途**：查询需要进行复审的慢特病患者列表。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| pageNum | Integer | 否 | 页码 | 默认1 |
| pageSize | Integer | 否 | 每页条数 | 默认10 |
| name | String | 否 | 姓名 | 按姓名搜索 |
| idcard | String | 否 | 身份证号 | 按身份证搜索 |
| reviewStatus | Integer | 否 | 复审状态 | 0=待复审,1=已复审,2=拒绝 |
| icdname | String | 否 | 疾病名称 | 按病种筛选 |

**请求示例**
```json
{
  "pageNum": 1,
  "pageSize": 10,
  "reviewStatus": 0,
  "startDate": "2024-01-01"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data.list | Array | 复审列表 | 待复审记录 |
| data.list[].reviewId | String | 复审ID | 唯一标识 |
| data.list[].accountId | String | 账户ID | 患者账户 |
| data.list[].name | String | 姓名 | 患者姓名 |
| data.list[].idcard | String | 身份证号 | 脱敏显示 |
| data.list[].icdname | String | 疾病名称 | 复审的病种 |
| data.list[].reviewStatus | Integer | 复审状态 | 0=待复审 |
| data.list[].reviewStatusName | String | 状态名称 | 待复审 |
| data.list[].validEndDate | String | 待遇到期日 | 什么时候到期 |
| data.list[].createTime | String | 创建时间 | 什么时候发起的 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": {
    "pageNum": 1,
    "pageSize": 10,
    "total": 25,
    "list": [
      {
        "reviewId": "RV202401150001",
        "accountId": "ACC202401150001",
        "name": "李四",
        "idcard": "610***********1234",
        "icdname": "2型糖尿病",
        "reviewStatus": 0,
        "reviewStatusName": "待复审",
        "validEndDate": "2024-12-31",
        "createTime": "2024-01-10 09:00:00"
      }
    ]
  }
}
```

**谁在调用**：复审管理列表页 `/MbReview/query`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 查询正常 |

**小白易懵点**：
- 复审通常在待遇到期前一个月发起
- 复审不通过会取消患者的慢特病待遇

---

### 6.2 POST /MbReview/acceptReview — 接受复审

**用途**：复审通过，继续保持患者的慢特病待遇。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| reviewId | String | ✅ | 复审ID | 要通过哪个 |
| approvalNote | String | 否 | 审批意见 | 补充说明 |
| newValidEndDate | String | 否 | 新有效期 | 延续到什么时候 |

**请求示例**
```json
{
  "reviewId": "RV202401150001",
  "approvalNote": "患者持续服药，病情稳定，同意续期",
  "newValidEndDate": "2025-12-31"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| msg | String | 返回消息 | 审批结果 |
| data | Object | 详情 | 处理结果 |
| data.reviewId | String | 复审ID | 已通过的复审 |
| data.reviewStatus | Integer | 新状态 | 1=已复审 |
| data.newValidEndDate | String | 新到期日 | 延续到哪天 |

**返回示例**
```json
{
  "code": 0,
  "msg": "复审通过，待遇已延续",
  "data": {
    "reviewId": "RV202401150001",
    "reviewStatus": 1,
    "newValidEndDate": "2025-12-31"
  }
}
```

**谁在调用**：复审审批操作 `/MbReview/acceptReview`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 复审通过 |
| 2001 | 复审不存在 | reviewId错误 |
| 2002 | 状态已变更 | 已被其他人员处理 |

---

### 6.3 POST /MbReview/refuseReview — 拒绝复审

**用途**：复审不通过，取消患者的慢特病待遇。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| reviewId | String | ✅ | 复审ID | 要拒绝哪个 |
| refuseReason | String | ✅ | 拒绝原因 | 必须填写！ |
| refuseType | String | 否 | 拒绝类型 | 1=不符合条件,2=材料不全 |

**请求示例**
```json
{
  "reviewId": "RV202401150001",
  "refuseReason": "经复查，患者已不符合糖尿病慢特病标准，取消其待遇资格",
  "refuseType": "1"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| msg | String | 返回消息 | 处理结果 |
| data | Object | 详情 | 处理结果 |
| data.reviewId | String | 复审ID | 已拒绝的复审 |
| data.reviewStatus | Integer | 新状态 | 2=已拒绝 |

**返回示例**
```json
{
  "code": 0,
  "msg": "复审已拒绝，患者待遇将取消",
  "data": {
    "reviewId": "RV202401150001",
    "reviewStatus": 2,
    "effectiveDate": "2024-02-01"
  }
}
```

**谁在调用**：复审拒绝操作 `/MbReview/refuseReview`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 拒绝成功 |
| 9001 | 拒绝原因必填 | 必须填写refuseReason |
| 2001 | 复审不存在 | reviewId错误 |

---

## 七、备案管理

备案管理处理医保系统的备案信息同步。

### 7.1 POST /MbUpdate/query — 慢病备案信息查询

**用途**：查询医保系统中的慢特病备案信息。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| pageNum | Integer | 否 | 页码 | 默认1 |
| pageSize | Integer | 否 | 每页条数 | 默认10 |
| name | String | 否 | 姓名 | 按姓名搜索 |
| idcard | String | 否 | 身份证号 | 按身份证搜索 |
| filingStatus | Integer | 否 | 备案状态 | 1=已备案,0=未备案 |

**请求示例**
```json
{
  "pageNum": 1,
  "pageSize": 10,
  "idcard": "610102199001011234",
  "filingStatus": 1
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data.list | Array | 备案列表 | 查询结果 |
| data.list[].filingId | String | 备案ID | 医保系统备案号 |
| data.list[].name | String | 姓名 | 患者姓名 |
| data.list[].idcard | String | 身份证号 | 脱敏显示 |
| data.list[].icdcode | String | 疾病编码 | 医保病种编码 |
| data.list[].icdname | String | 疾病名称 | 病种名称 |
| data.list[].filingStatus | Integer | 备案状态 | 1=已备案 |
| data.list[].filingDate | String | 备案日期 | 什么时候备案的 |
| data.list[].validStartDate | String | 待遇开始 | 什么时候开始享受 |
| data.list[].validEndDate | String | 待遇结束 | 什么时候结束 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": {
    "pageNum": 1,
    "pageSize": 10,
    "total": 1,
    "list": [
      {
        "filingId": "BA2024000001",
        "name": "李四",
        "idcard": "610***********1234",
        "icdcode": "E11",
        "icdname": "2型糖尿病",
        "filingStatus": 1,
        "filingDate": "2024-01-15",
        "validStartDate": "2024-02-01",
        "validEndDate": "2024-12-31"
      }
    ]
  }
}
```

**谁在调用**：备案信息查询页面 `/MbUpdate/query`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 查询正常 |

---

### 7.2 POST /MbUpdate/update — 备案信息修改

**用途**：修改备案信息，如变更定点医院、有效期等。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| filingId | String | ✅ | 备案ID | 要修改哪个 |
| fixedhoscode | String | 否 | 定点医院编码 | 改到哪家医院 |
| validEndDate | String | 否 | 有效期结束 | 调整结束日期 |
| remark | String | 否 | 备注 | 修改原因 |

**请求示例**
```json
{
  "filingId": "BA2024000001",
  "fixedhoscode": "H61010002",
  "remark": "患者申请变更定点医院"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| msg | String | 返回消息 | 修改结果 |
| data | Object | 详情 | 修改后的信息 |

**返回示例**
```json
{
  "code": 0,
  "msg": "备案信息修改成功",
  "data": {
    "filingId": "BA2024000001",
    "fixedhoscode": "H61010002",
    "updateTime": "2024-01-15 14:00:00"
  }
}
```

**谁在调用**：备案信息维护页面 `/MbUpdate/update`

---

## 八、数据统计

数据统计模块提供各类业务数据的汇总和分析。

### 8.1 POST /MbDataStatistics/queryDataStatistics — 数据统计查询

**用途**：按日期、机构等维度统计慢特病申报、审批、发卡等业务数据。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| startDate | String | ✅ | 开始日期 | 统计范围 |
| endDate | String | ✅ | 结束日期 | 统计范围 |
| unitCode | String | 否 | 机构编码 | 按机构筛选 |
| groupBy | String | 否 | 分组维度 | date=按日,unit=按机构 |

**请求示例**
```json
{
  "startDate": "2024-01-01",
  "endDate": "2024-01-31",
  "unitCode": "U610100",
  "groupBy": "date"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data | Array | 统计结果 | 汇总数据 |
| data[].date | String | 统计日期 | 哪一天 |
| data[].declareCount | Integer | 申报数量 | 当日申报数 |
| data[].approveCount | Integer | 审批通过数 | 当日通过数 |
| data[].rejectCount | Integer | 审批驳回数 | 当日驳回数 |
| data[].sendCardCount | Integer | 发卡数量 | 当日发卡数 |
| data[].consumeAmount | Decimal | 消费金额 | 当日消费总额 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": [
    {
      "date": "2024-01-15",
      "declareCount": 45,
      "approveCount": 38,
      "rejectCount": 5,
      "sendCardCount": 30,
      "consumeAmount": 15800.00
    },
    {
      "date": "2024-01-16",
      "declareCount": 52,
      "approveCount": 42,
      "rejectCount": 3,
      "sendCardCount": 35,
      "consumeAmount": 18600.00
    }
  ]
}
```

**谁在调用**：数据统计报表页面 `/MbDataStatistics/queryDataStatistics`

---

### 8.2 POST /MbDataStatistics/StatisticsDataExport — 统计数据导出

**用途**：将统计数据导出为Excel文件。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| startDate | String | ✅ | 开始日期 | 导出范围 |
| endDate | String | ✅ | 结束日期 | 导出范围 |
| exportType | String | 否 | 导出类型 | all=全部,detail=明细 |

**请求示例**
```json
{
  "startDate": "2024-01-01",
  "endDate": "2024-01-31",
  "exportType": "all"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| msg | String | 返回消息 | 导出结果 |
| data | Object | 文件信息 | 下载链接 |
| data.fileName | String | 文件名 | 导出的文件名 |
| data.fileUrl | String | 下载地址 | 文件URL |

**返回示例**
```json
{
  "code": 0,
  "msg": "导出成功",
  "data": {
    "fileName": "数据统计报表_2024年1月.xlsx",
    "fileUrl": "https://xxx.com/download/ST20240131001.xlsx"
  }
}
```

**谁在调用**：统计导出功能 `/MbDataStatistics/StatisticsDataExport`

---

## 九、系统管理

系统管理模块处理用户、角色、权限等系统级配置。

### 9.1 POST /Login/doLogin — 用户登录

**用途**：验证用户名密码，登录系统。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| username | String | ✅ | 用户名 | 账号 |
| password | String | ✅ | 密码 | 密码(已加密) |
| captcha | String | 否 | 验证码 | 图形验证码 |

**请求示例**
```json
{
  "username": "admin",
  "password": "e10adc3949ba59abbe56e057f20f883e",
  "captcha": "1234"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| msg | String | 返回消息 | 登录结果 |
| data | Object | 用户信息 | 登录成功信息 |
| data.userId | String | 用户ID | 唯一标识 |
| data.username | String | 用户名 | 登录名 |
| data.realName | String | 真实姓名 | 显示名 |
| data.token | String | 登录令牌 | 后续请求凭证 |
| data.expireTime | Long | 过期时间 | token失效时间戳 |
| data.roles | Array | 角色列表 | 用户角色 |
| data.permissions | Array | 权限列表 | 用户权限 |

**返回示例**
```json
{
  "code": 0,
  "msg": "登录成功",
  "data": {
    "userId": "U20240001",
    "username": "admin",
    "realName": "系统管理员",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expireTime": 1705401600000,
    "roles": ["admin", "auditor"],
    "permissions": ["declare:query", "declare:approve"]
  }
}
```

**谁在调用**：登录页面 `/Login/doLogin`

**常见错误码**
| 错误码 | 含义 | 原因与解决 |
|--------|------|-----------|
| 0 | 成功 | 登录成功 |
| 1001 | 用户名错误 | 账号不存在 |
| 1002 | 密码错误 | 密码不正确 |
| 1003 | 账号已冻结 | 联系管理员解冻 |
| 1004 | 验证码错误 | 检查验证码 |

---

### 9.2 POST /MbUser/query — 查询系统用户

**用途**：查询系统中的用户列表，支持分页和条件筛选。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| pageNum | Integer | 否 | 页码 | 默认1 |
| pageSize | Integer | 否 | 每页条数 | 默认10 |
| username | String | 否 | 用户名 | 模糊查询 |
| realName | String | 否 | 真实姓名 | 模糊查询 |
| roleId | String | 否 | 角色ID | 按角色筛选 |
| status | Integer | 否 | 状态 | 1=启用,0=停用 |

**请求示例**
```json
{
  "pageNum": 1,
  "pageSize": 20,
  "roleId": "R20240001",
  "status": 1
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data.list | Array | 用户列表 | 查询结果 |
| data.list[].userId | String | 用户ID | 唯一标识 |
| data.list[].username | String | 用户名 | 登录账号 |
| data.list[].realName | String | 真实姓名 | 显示名 |
| data.list[].mobile | String | 手机号 | 联系方式 |
| data.list[].email | String | 邮箱 | 邮箱地址 |
| data.list[].roleName | String | 角色名称 | 岗位 |
| data.list[].status | Integer | 状态 | 1=启用,0=停用 |
| data.list[].createTime | String | 创建时间 | 什么时候创建 |
| data.list[].lastLoginTime | String | 最后登录 | 上次登录时间 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": {
    "pageNum": 1,
    "pageSize": 20,
    "total": 50,
    "list": [
      {
        "userId": "U20240001",
        "username": "admin",
        "realName": "系统管理员",
        "mobile": "138****8000",
        "email": "admin@picc.com",
        "roleName": "超级管理员",
        "status": 1,
        "createTime": "2023-01-01 00:00:00",
        "lastLoginTime": "2024-01-15 09:30:00"
      }
    ]
  }
}
```

**谁在调用**：用户管理列表页 `/MbUser/query`

---

### 9.3 POST /MbUser/UserManageEdit — 新增/编辑用户

**用途**：创建新用户或编辑现有用户信息。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| userId | String | 否 | 用户ID | 编辑时传入，新增不传 |
| username | String | ✅ | 用户名 | 登录账号 |
| password | String | ✅(新增) | 密码 | 新增时必填 |
| realName | String | ✅ | 真实姓名 | 显示名 |
| mobile | String | ✅ | 手机号 | 联系方式 |
| email | String | 否 | 邮箱 | 邮箱地址 |
| roleId | String | ✅ | 角色ID | 分配角色 |
| districtCode | String | 否 | 管辖区域 | 区县编码 |
| status | Integer | 否 | 状态 | 1=启用,0=停用 |

**请求示例**
```json
{
  "username": "zhangsan",
  "password": "e10adc3949ba59abbe56e057f20f883e",
  "realName": "张三",
  "mobile": "13800138000",
  "email": "zhangsan@picc.com",
  "roleId": "R20240003",
  "districtCode": "610102",
  "status": 1
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| msg | String | 返回消息 | 操作结果 |
| data | Object | 用户信息 | 创建/更新的用户 |

**返回示例**
```json
{
  "code": 0,
  "msg": "用户创建成功",
  "data": {
    "userId": "U20240050",
    "username": "zhangsan",
    "realName": "张三"
  }
}
```

**谁在调用**：用户新增/编辑页面 `/MbUser/UserManageEdit`

---

### 9.4 POST /MbUser/resetPassword — 重置用户密码

**用途**：管理员重置用户密码，默认密码会通过短信发送给用户。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| userId | String | ✅ | 用户ID | 要重置哪个 |
| resetType | String | 否 | 重置方式 | sms=短信,email=邮件 |

**请求示例**
```json
{
  "userId": "U20240050",
  "resetType": "sms"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| msg | String | 返回消息 | 重置结果 |
| data | Object | 详情 | 发送信息 |
| data.userId | String | 用户ID | 已重置的用户 |
| data.notifyTarget | String | 通知目标 | 138****8000 |
| data.notifyStatus | String | 通知状态 | success |

**返回示例**
```json
{
  "code": 0,
  "msg": "密码已重置，新密码已发送至手机",
  "data": {
    "userId": "U20240050",
    "notifyTarget": "138****8000",
    "notifyStatus": "success"
  }
}
```

**谁在调用**：用户管理-重置密码操作 `/MbUser/resetPassword`

---

### 9.5 POST /PhysicalOrg/getPhysicalOrgList — 查询体检机构列表

**用途**：获取系统配置的体检中心/医院列表。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| districtCode | String | 否 | 区县编码 | 筛选区域 |
| orgType | String | 否 | 机构类型 | hospital=医院,clinic=诊所 |
| status | Integer | 否 | 状态 | 1=启用,0=停用 |

**请求示例**
```json
{
  "districtCode": "610102",
  "status": 1
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data | Array | 机构列表 | 体检机构 |
| data[].orgId | String | 机构ID | 唯一标识 |
| data[].orgName | String | 机构名称 | 名称 |
| data[].orgType | String | 机构类型 | 医院/诊所 |
| data[].address | String | 地址 | 详细地址 |
| data[].mobile | String | 联系电话 | 电话 |
| data[].longitude | Decimal | 经度 | 地图坐标 |
| data[].latitude | Decimal | 纬度 | 地图坐标 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": [
    {
      "orgId": "ORG20240001",
      "orgName": "西安市第一医院体检中心",
      "orgType": "hospital",
      "address": "西安市碑林区南大街100号",
      "mobile": "029-88888888",
      "longitude": 108.953,
      "latitude": 34.223
    }
  ]
}
```

**谁在调用**：体检机构配置页面 / 分配体检时选择

---

## 十、用户认证

用户认证模块处理小程序端的登录、注册、身份验证等。

### 10.1 POST /picchealth/getWeiXinUserStatus — 获取微信用户状态

**用途**：检查用户在微信小程序的登录状态，判断是否已注册。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| openId | String | ✅ | 微信OpenID | 用户唯一标识 |
| unionId | String | 否 | 微信UnionID | 用户唯一标识 |

**请求示例**
```json
{
  "openId": "oXXXXXXXXXXXXXX",
  "unionId": "uXXXXXXXXXXXXXX"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data | Object | 用户状态 | 状态详情 |
| data.isRegistered | Boolean | 是否已注册 | true/false |
| data.userId | String | 用户ID | 已注册才有 |
| data.isRealnameVerified | Boolean | 是否已实名 | true/false |
| data.hasDeclare | Boolean | 是否有申报 | 是否有申报记录 |
| data.bindMobile | String | 绑定手机 | 脱敏显示 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": {
    "isRegistered": true,
    "userId": "WXU20240001",
    "isRealnameVerified": true,
    "hasDeclare": true,
    "bindMobile": "138****8000"
  }
}
```

**谁在调用**：小程序启动时检查登录态 `/picchealth/getWeiXinUserStatus`

---

### 10.2 POST /picchealth/mbDeclare — 小程序慢病申报

**用途**：用户在微信小程序端提交慢特病申报材料。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| userId | String | ✅ | 用户ID | 哪个用户 |
| name | String | ✅ | 姓名 | 患者姓名 |
| idcard | String | ✅ | 身份证号 | 患者身份证 |
| mobile | String | ✅ | 手机号 | 联系方式 |
| sex | String | ✅ | 性别 | M/F |
| persontype | String | ✅ | 人员类型 | 3=职工,390=居民 |
| medicalno | String | ✅ | 医保编号 | 医保卡号 |
| icdcode | String | ✅ | 疾病编码 | 要申请的病种 |
| icdname | String | ✅ | 疾病名称 | 病种名称 |
| fixedhoscode | String | ✅ | 定点医院 | 选哪家医院 |
| fileIds | Array | ✅ | 材料文件ID | 上传的图片ID列表 |

**请求示例**
```json
{
  "userId": "WXU20240001",
  "name": "张三",
  "idcard": "610102199001011234",
  "mobile": "13800138000",
  "sex": "M",
  "persontype": "3",
  "medicalno": "P61010219900101123456",
  "icdcode": "E11",
  "icdname": "2型糖尿病",
  "fixedhoscode": "H61010001",
  "fileIds": ["F202401150001", "F202401150002", "F202401150003"]
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| msg | String | 返回消息 | 申报结果 |
| data | Object | 申报详情 | 申报信息 |
| data.declareId | String | 申报ID | 唯一标识 |
| data.declareno | String | 申报编号 | 申报单号 |

**返回示例**
```json
{
  "code": 0,
  "msg": "申报提交成功，请等待审核",
  "data": {
    "declareId": "20240115000001",
    "declareno": "DC2024011500001",
    "submitTime": "2024-01-15 10:00:00",
    "estimatedDays": 15
  }
}
```

**谁在调用**：小程序申报页面 `/picchealth/mbDeclare`

---

### 10.3 POST /picchealth/queryMBDeclare — 小程序查询申报记录

**用途**：用户在微信小程序查看自己的申报记录和状态。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| userId | String | ✅ | 用户ID | 哪个用户 |
| pageNum | Integer | 否 | 页码 | 默认1 |
| pageSize | Integer | 否 | 每页条数 | 默认10 |
| declareStatus | Integer | 否 | 申报状态 | 筛选状态 |

**请求示例**
```json
{
  "userId": "WXU20240001",
  "pageNum": 1,
  "pageSize": 10
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data.list | Array | 申报列表 | 申报记录 |
| data.list[].declareId | String | 申报ID | 唯一标识 |
| data.list[].declareno | String | 申报编号 | 申报单号 |
| data.list[].icdname | String | 疾病名称 | 申请的病种 |
| data.list[].applyStatus | Integer | 申报状态 | 见状态说明 |
| data.list[].applyStatusName | String | 状态名称 | 审核中/已通过等 |
| data.list[].progress | Integer | 进度百分比 | 0-100 |
| data.list[].declaredate | String | 申报日期 | 什么时候提交 |
| data.list[].approvalDate | String | 审批日期 | 什么时候审批 |
| data.list[].rejectReason | String | 驳回原因 | 如果被驳回 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": {
    "pageNum": 1,
    "pageSize": 10,
    "total": 3,
    "list": [
      {
        "declareId": "20240115000001",
        "declareno": "DC2024011500001",
        "icdname": "2型糖尿病",
        "applyStatus": 1,
        "applyStatusName": "初审通过",
        "progress": 60,
        "declaredate": "2024-01-15 10:00:00",
        "approvalDate": "2024-01-16 14:00:00",
        "rejectReason": null
      },
      {
        "declareId": "20240110000001",
        "declareno": "DC2024011000001",
        "icdname": "高血压",
        "applyStatus": 2,
        "applyStatusName": "初审驳回",
        "progress": 30,
        "declaredate": "2024-01-10 09:00:00",
        "approvalDate": "2024-01-12 10:00:00",
        "rejectReason": "缺少近三个月的血压监测记录"
      }
    ]
  }
}
```

**谁在调用**：小程序-我的申报页面 `/picchealth/queryMBDeclare`

---

### 10.4 POST /picchealth/queryNearbyDrugstores — 查询附近药店

**用途**：查询用户附近的医保定点药店。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| userId | String | ✅ | 用户ID | 哪个用户 |
| latitude | Decimal | ✅ | 纬度 | 用户位置 |
| longitude | Decimal | ✅ | 经度 | 用户位置 |
| radius | Integer | 否 | 范围(米) | 搜索半径，默认2000 |
| keyword | String | 否 | 关键词 | 搜索药店名 |

**请求示例**
```json
{
  "userId": "WXU20240001",
  "latitude": 34.223,
  "longitude": 108.953,
  "radius": 3000,
  "keyword": "大药房"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data | Array | 药店列表 | 附近的药店 |
| data[].storeId | String | 药店ID | 唯一标识 |
| data[].storeName | String | 药店名称 | 店名 |
| data[].address | String | 地址 | 详细地址 |
| data[].distance | Integer | 距离(米) | 离用户多远 |
| data[].mobile | String | 联系电话 | 电话 |
| data[].businessHours | String | 营业时间 | 几点开门 |
| data[].hasStock | Boolean | 是否有货 | 常用药品是否有货 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": [
    {
      "storeId": "DS20240001",
      "storeName": "XX大药房(科技路店)",
      "address": "西安市雁塔区科技路100号",
      "distance": 520,
      "mobile": "029-88888888",
      "businessHours": "08:00-22:00",
      "hasStock": true
    },
    {
      "storeId": "DS20240002",
      "storeName": "XX药店(小寨店)",
      "address": "西安市雁塔区小寨路50号",
      "distance": 1200,
      "mobile": "029-88888889",
      "businessHours": "07:30-21:30",
      "hasStock": true
    }
  ]
}
```

**谁在调用**：小程序-找药店页面 `/picchealth/queryNearbyDrugstores`

---

### 10.5 POST /picchealth/queryReviewDate — 查询复审提醒

**用途**：获取用户的慢特病待遇复审提醒信息。

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 小白解释 |
|--------|------|------|------|---------|
| userId | String | ✅ | 用户ID | 哪个用户 |

**请求示例**
```json
{
  "userId": "WXU20240001"
}
```

**返回参数**
| 字段 | 类型 | 说明 | 小白解释 |
|------|------|------|---------|
| code | Integer | 状态码 | 0=成功 |
| data | Array | 复审列表 | 待复审记录 |
| data[].reviewId | String | 复审ID | 唯一标识 |
| data[].icdname | String | 疾病名称 | 要复审的病种 |
| data[].validEndDate | String | 到期日期 | 什么时候到期 |
| data[].daysRemaining | Integer | 剩余天数 | 还有多久到期 |
| data[].isUrgent | Boolean | 是否紧急 | true=7天内到期 |

**返回示例**
```json
{
  "code": 0,
  "msg": "查询成功",
  "data": [
    {
      "reviewId": "RV202401150001",
      "icdname": "2型糖尿病",
      "validEndDate": "2024-03-31",
      "daysRemaining": 75,
      "isUrgent": false
    },
    {
      "reviewId": "RV202401150002",
      "icdname": "高血压",
      "validEndDate": "2024-01-20",
      "daysRemaining": 5,
      "isUrgent": true
    }
  ]
}
```

**谁在调用**：小程序首页复审提醒 `/picchealth/queryReviewDate`

---

## 附录

### A. 通用响应格式

所有接口统一使用以下响应格式：

```json
{
  "code": 0,        // 状态码：0=成功，其他=失败
  "msg": "成功",    // 消息：成功或失败原因
  "data": {}        // 数据：具体返回内容，可能为null
}
```

### B. 状态码参考表

| 状态码范围 | 含义 |
|-----------|------|
| 0 | 成功 |
| 1001-1999 | 参数校验错误 |
| 2001-2999 | 业务数据错误 |
| 3001-3999 | 支付/费用相关错误 |
| 4001-4999 | 退款相关错误 |
| 5001-5999 | 系统/导出相关错误 |
| 6001-6999 | OCR识别相关错误 |
| 7001-7999 | 药品相关错误 |
| 8001-8999 | 处方相关错误 |
| 9001-9999 | 复审相关错误 |

### C. 申报状态说明

| 状态值 | 状态名称 | 说明 |
|--------|---------|------|
| 0 | 审核中 | 待初审 |
| 1 | 初审通过 | 初审已通过，待专家审批 |
| 2 | 初审驳回 | 材料不全或不符合 |
| 3 | 审核通过 | 专家审批通过 |
| 4 | 审核驳回 | 不符合慢特病标准 |
| 5 | 部分通过 | 多病种申报，部分通过 |
| 6 | 复审通过 | 年度复审通过 |
| 7 | 复审驳回 | 年度复审未通过 |
| 8 | 补充资料 | 需要补充材料 |
| 9 | 无效/作废 | 申报已作废 |
| 10 | 二次审核 | 需要再次审核 |

### D. 文件类型说明

| 类型代码 | 类型名称 | 说明 |
|---------|---------|------|
| 1 | 身份证 | 身份证正反面 |
| 2 | 病历资料 | 门诊/住院病历 |
| 3 | 体检报告 | 体检中心报告 |
| 4 | 诊断证明 | 医生开具的诊断证明 |
| 5 | 其他材料 | 其他证明材料 |

---

> 📝 **文档说明**
> - 本文档基于 `picc-mzmtb-server` 项目源码生成
> - 脱敏处理：身份证号、手机号等敏感信息已做脱敏处理
> - 接口路径：基于全景扫描结果整理，实际路径以代码为准
> - 示例数据：请求/响应示例为示意数据，非真实用户数据

---

*文档生成时间：2024年1月*
