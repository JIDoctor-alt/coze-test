# PICC门诊慢特病业务管理系统 - 地市差异化机制深度解析

> 📖 本文档为零基础开发者编写，用最通俗易懂的方式解释复杂的技术架构
> 
> 🎯 读完本文档，你将理解：一个系统如何用"一套代码"服务全国13个地市，每个地市却能拥有自己的"特色菜单"

---

## 一、先打个比方：理解地市差异化就像理解"外卖平台"

想象你要开发一个**全国连锁外卖平台**，会遇到这样的问题：

### 🏪 问题：如何让每个城市有不同的"口味"？

| 方案 | 做法 | 缺点 |
|------|------|------|
| 方案A | 每个城市复制一套代码 | 代码重复，维护噩梦，改一处要改13份 |
| 方案B | 所有城市完全一样 | 无法满足各地特色需求 |

### 💡 最终方案：采用"中央厨房 + 本地厨师"模式

```
┌─────────────────────────────────────────────────────────┐
│                      中央厨房（mtb-base）                │
│         提供：基础设施、公共接口、通用业务逻辑            │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┬───────────────┐
         ▼               ▼               ▼               ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │ 西安分店 │    │ 延安分店 │    │ 宝鸡分店 │    │ 商洛分店 │
    │(mtb-xya)│    │ (mtb-ya) │    │ (mtb-bj) │    │ (mtb-sl) │
    │ 凉皮肉夹馍│    │ 炖羊肉   │    │ 擀面皮   │    │ 商芝面   │
    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

> **PICC慢特病系统就是这样设计的**：
> - `mtb-base`：中央厨房，所有地市公用的基础代码
> - `mtb-xya`、`mtb-ya` 等：各地市的"特色厨师"，只做差异化的部分

---

## 二、系统架构总览

### 2.1 项目模块结构

```
picc-mzmtb-server/
├── mtb-yh/                          # 慢特病优化模块（核心差异区域）
│   ├── mtb-base/                    # 🏠 基础模块（674个Java文件）
│   │   ├── src/main/java/
│   │   │   └── com/picchealth/
│   │   │       ├── module/
│   │   │       │   ├── mb/         # 地市配置、Flag机制核心
│   │   │       │   └── mtb/        # 核心业务服务
│   │   │       └── utils/          # 工具类（Flag工具链）
│   │   └── resources/
│   │       └── temp/               # Excel模板
│   ├── mtb-bj/                      # 北京/宝鸡分店（2个文件）
│   ├── mtb-sl/                      # 商洛分店（4个文件）
│   ├── mtb-ya/                      # 延安分店（4个文件）
│   ├── mtb-xya/                     # 西安分店（13个文件）⭐ 差异最丰富
│   ├── mtb-yl/                      # 榆林分店（4个文件）
│   ├── mtb-yli/                     # 杨凌分店（10个文件）
│   ├── mtb-dz/                      # 达州分店（8个文件）
│   ├── mtb-jc/                      # 晋城分店（11个文件）
│   ├── mtb-jj/                      # 九江分店（9个文件）
│   ├── mtb-mzl/                     # 满洲里分店（6个文件）
│   └── mtb-dez/                     # 定州分店（2个文件）
├── picchealth-server/              # 服务启动模块
└── picchealth-db/                  # 数据库层模块
```

### 2.2 13个地市模块一览

| 模块名 | 地市 | Java文件数 | 主要差异点 |
|--------|------|------------|------------|
| mtb-xya | 西安 | 13 | 申报流程、专家分配、体检报告 |
| mtb-bj | 宝鸡 | 2 | 申报列表查询优化 |
| mtb-sl | 商洛 | 4 | 处方管理、小程序申报 |
| mtb-ya | 延安 | 4 | 申报列表、审批文件 |
| mtb-yl | 榆林 | 4 | 申报列表 |
| mtb-yli | 杨凌 | 10 | 申报信息更新、专家列表 |
| mtb-dz | 达州 | 8 | 处方主服务 |
| mtb-jc | 晋城 | 11 | Excel导出服务 |
| mtb-jj | 九江 | 9 | 专家分配 |
| mtb-mzl | 满洲里 | 6 | Excel导出服务 |
| mtb-dez | 定州 | 2 | Excel导出服务 |

---

## 三、Flag识别机制：系统如何知道"你是哪个地市的"？

### 3.1 核心概念：Flag = 地市身份证号

```
Flag 就像是每个地市的"身份证号"，系统看到这个号码就知道：
- 你是谁（哪个地市）
- 你有什么权限
- 你的特色配置是什么
```

### 3.2 Flag的流转过程（请求的一生）

```
┌─────────────┐     ┌─────────────────┐     ┌──────────────┐
│   用户端     │     │   FlagInterceptor│     │  ThreadLocal  │
│  HTTP请求   │────▶│     拦截器       │────▶│   线程存储    │
│  Header中   │     │  提取flag       │     │  保存上下文   │
│  flag: xya  │     │                 │     │               │
└─────────────┘     └─────────────────┘     └──────────────┘
                                                 │
                                                 ▼
┌─────────────┐     ┌─────────────────┐     ┌──────────────┐
│   Service   │◀────│  MtbBeanFactory │◀────│  FlagUtils   │
│   具体实现   │     │    工厂类       │     │  获取flag    │
│  XYA专用    │     │  根据flag拿Bean │     │               │
└─────────────┘     └─────────────────┘     └──────────────┘
```

### 3.3 三行代码理解Flag机制

#### 📍 第一站：FlagInterceptorConfig（拦截器）
```java
// 位置: picchealth-server/.../config/FlagInterceptorConfig.java
// 功能: 从HTTP请求头中提取flag，存入ThreadLocal

String flag = request.getHeader("flag");  // 1. 从请求头拿到flag
FlagLocal flagLocal = new FlagLocal();
flagLocal.setFlag(flag);
flagLocal.setUnitCode(UnitConfigEnum.fromFlag(flag).getTopUnitCode());
FlagUtils.setFlagLocal(flagLocal);         // 2. 存入线程存储
```

#### 📍 第二站：FlagLocal（载体）
```java
// 位置: mtb-yh/mtb-base/.../utils/FlagLocal.java
// 功能: 存储请求上下文信息

@Data
public class FlagLocal {
    private String flag;        // 地市标识，如"xya"
    private String unitCode;    // 机构编码，如"610100"
}
```

#### 📍 第三站：FlagUtils（工具）
```java
// 位置: mtb-yh/mtb-base/.../utils/FlagUtils.java
// 功能: 线程安全地获取/设置flag

public static FlagLocal getFlagLocal() {
    FlagLocal flagLocal = threadLocal.get();
    if (flagLocal == null) {
        flagLocal = new FlagLocal();
        flagLocal.setFlag("9");  // 默认值
    }
    return flagLocal;
}
```

#### 📍 第四站：MtbBeanFactory（工厂）
```java
// 位置: mtb-yh/mtb-base/.../utils/MtbBeanFactory.java
// 功能: 根据flag获取对应的Service实现

public static <T> T getService(Class<T> tClass) {
    return getService(FlagUtils.getFlagLocal().getFlag(), tClass);
}

public static <T> T getService(String flag, Class<T> tClass) {
    UnitConfig unitConfig = UnitConfigEnum.fromFlag(flag);
    String serverName = unitConfig.getName();  // 如"XYA"
    String name = tClass.getSimpleName() + serverName;  // 如"MtbDeclareServiceXYA"
    return SpringContext.getBean(name, tClass);  // 返回西安专用的Service
}
```

### 3.4 Flag到地市配置的映射

```java
// 位置: mtb-yh/mtb-base/.../enums/UnitConfigEnum.java
// 功能: 枚举定义，支持多种匹配方式

public class UnitConfigEnum {
    public final static UnitConfig BJ = new UnitConfig();   // 宝鸡
    public final static UnitConfig SL = new UnitConfig();   // 商洛
    public final static UnitConfig YA = new UnitConfig();   // 延安
    public final static UnitConfig XYA = new UnitConfig();  // 西安
    // ... 其他地市

    // 初始化：将配置注册到映射表
    public static void init(UnitConfig unitConfig) {
        mappings.put("FLAG:" + unitConfig.getFlag(), unitConfig);
        mappings.put("SOURCE:" + unitConfig.getSource(), unitConfig);
        mappings.put("TOP_UNIT_CODE:" + unitConfig.getTopUnitCode(), unitConfig);
    }

    // 根据flag查找配置
    public static UnitConfig fromFlag(String flag) {
        if (StringUtils.isEmpty(flag) || "99".equals(flag)) {
            return BJ;  // 默认返回宝鸡
        }
        return mappings.get("FLAG:" + flag);
    }
}
```

### 3.5 配置表：t_mb_unit_config

> Flag的真正来源是数据库配置表 `t_mb_unit_config`

| 字段 | 说明 | 示例值 |
|------|------|--------|
| name | 地市名称（对应枚举） | XYA |
| flag | 地市标识（请求中传递） | xya |
| source | 来源标识 | xya_source |
| top_unit_code | 顶层机构编码 | 610100 |
| service1 | 地区业务实例ID | xya_service |
| service2 | 文件导入实例ID | xyaExcelService |
| workflow_flag | 工作流标志 | 1 |

---

## 四、Service差异化：如何实现"同名不同菜"？

### 4.1 策略：继承 + Override

每个地市的Service都遵循这个模式：
```
mtb-base（父类）：提供通用实现
地市模块（子类）：只Override需要差异化的方法
```

### 4.2 实战示例：MtbDeclareListService

#### 父类：通用申报列表服务
```java
// mtb-base/.../service/impl/MtbDeclareListServiceImpl.java
@Service
public class MtbDeclareListServiceImpl {
    
    public ApiResponse<ResultPage<VipMbdeclareInfoDto>> queryVipMbdeclareInfoList(...) {
        // 通用查询逻辑
    }
}
```

#### 西安定制版
```java
// mtb-xya/.../service/impl/MtbDeclareListXYAServiceImpl.java
@Service("MtbDeclareListServiceXYA")  // ⭐ 注意bean名称！
public class MtbDeclareListXYAServiceImpl extends MtbDeclareListServiceImpl {
    
    @Override
    public ApiResponse<ResultPage<VipMbdeclareInfoDto>> queryVipMbdeclareInfoList(...) {
        // 西安特有的查询逻辑
        // 比如：额外的筛选条件、特殊字段处理
    }
}
```

#### 延安定制版
```java
// mtb-ya/.../service/impl/MtbDeclareListYAServiceImpl.java
@Service("MtbDeclareListServiceYA")  // ⭐ 注意bean名称！
public class MtbDeclareListYAServiceImpl extends MtbDeclareListServiceImpl {
    
    @Override
    public ApiResponse<ResultPage<VipMbdeclareInfoDto>> queryVipMbdeclareInfoList(...) {
        // 延安特有的查询逻辑
    }
}
```

### 4.3 调用方透明切换

```java
// 无论哪个地市，调用方式完全一样！
// 系统自动根据flag找到对应的Service

// 在Controller或Service中
MtbDeclareListService service = MtbBeanFactory.getService(MtbDeclareListService.class);
service.queryVipMbdeclareInfoList(queryVo);

// 西安用户调用 → MtbDeclareListServiceXYA
// 延安用户调用 → MtbDeclareListServiceYA
// 宝鸡用户调用 → MtbDeclareListServiceImpl（父类）
```

---

## 五、各地市差异场景深度解析

### 5.1 场景一：申报流程差异

#### 西安（mtb-xya）：最复杂的申报流程
```java
// XcxIndexXYAServiceImpl - 咸阳小程序端
@Service("XcxIndexServiceXYA")
public class XcxIndexXYAServiceImpl extends XcxIndexServiceImpl {
    
    // 西安特有的申报文件上传
    @Override
    public ApiResponse imageFiles(List<VipMbFileVo> vipMbFileVos) {
        // 1. 图片上传到FTP
        // 2. 特殊处理西安的文件路径格式
        String filePath = valueUtil.getFtpFilePath() + "XYa/" + dateName + "/";
        // 3. 返回文件信息
    }
    
    // 西安特有的待遇认定表生成
    public ApiResponse notificationListing(TMbYLiPrescriptionVo vo) {
        // 调用专门的Service获取数据
        MtbDeclareListService service = MtbBeanFactory.getService(..., MtbDeclareListService.class);
        map = service.credentialsMake(declareid);
    }
}
```

#### 商洛（mtb-sl）：处方管理为主
```java
// XcxIndexSLServiceImpl - 商洛小程序端
@Service("XcxIndexServiceSL")
public class XcxIndexSLServiceImpl extends XcxIndexServiceImpl {
    
    // 商洛特有的处方上传逻辑
    @Override
    public ApiResponse<CommonVo> getUploadPrescriptionList(CheckPrescriptionImgVo vo) {
        // 1. 先通过手机号或身份证查询
        // 2. 调用陕西医保1101接口验证资格
        // 3. 从Redis缓存获取处方列表
        // 4. 返回可上传处方的申报数据
    }
}
```

### 5.2 场景二：审批规则差异

#### 宝鸡（mtb-bj）：复审页面特殊处理
```java
// MtbDeclareListBJServiceImpl
@Service("MtbDeclareListServiceBJ")
public class MtbDeclareListBJServiceImpl extends MtbDeclareListServiceImpl {
    
    @Override
    public ApiResponse<ResultPage<VipMbdeclareInfoDto>> queryVipMbdeclareInfoList(...) {
        // 复审页面标识处理
        String reviewFlag = queryMbDeclareListVo.getReviewFlag();
        if ("review".equals(reviewFlag)) {
            // 复审相关的三个状态
            vipMbdeclareInfoDto.setDeclareStatus("367");
        }
        // ... 其他宝鸡特有逻辑
    }
}
```

#### 延安（mtb-ya）：医保账号特殊处理
```java
// MtbDeclareListYAServiceImpl
@Service("MtbDeclareListServiceYA")
public class MtbDeclareListYAServiceImpl extends MtbDeclareListServiceImpl {
    
    @Override
    public ApiResponse<ResultPage<VipMbdeclareInfoDto>> queryVipMbdeclareInfoList(...) {
        // 延安特有的账号权限查询
        String[] codes = vipMbdeclareInfoDto.getUnitcode().split(",");
        List<String> unitCodes = new ArrayList<>(Arrays.asList(codes));
        vipMbdeclareInfoDto.setUnitcodes(unitCodes);
        
        // 医保账号特殊处理
        if(UserUtils.getUser().getIsInsurance()) {
            Calendar calendar = Calendar.getInstance();
            calendar.set(2022, 11, 15);  // 延安特有日期判断
            vipMbdeclareInfoDto.setIdentificationFrom(date);
            vipMbDeclareInfoList = vipMbdeclareInfoDao.queryVipMbdeclareInfoYbList1(...);
        }
    }
}
```

### 5.3 场景三：Excel导出差异

> 每个地市的Excel模板和导出格式都不同

#### 典型差异点

| 地市 | Excel模板 | 特殊字段 |
|------|-----------|----------|
| 西安 | mbmz_declareInfo_xya.xls | XYA特有列 |
| 宝鸡 | mbmz_declareInfo_bj.xls | BJ特有列 |
| 延安 | mbmz_declareInfo_ya.xls | YA特有列 |
| 榆林 | mbmz_declareInfo_yl.xls | YL特有列 |

#### ExcelService接口
```java
// mtb-base/.../service/ExcelService.java
public interface ExcelService {
    VipFilepath ExcelFile(VipFilepath vipFilepath, String flag);
    VipFilepath ExcelUpdateFile(VipFilepath vipFilepath, String flag);
    ExportMbdeclareInfoDto exportMbdeclareInfo(List<VipMbdeclareInfoDto> list);
}
```

#### 西安Excel导出实现
```java
// mtb-xya/.../service/impl/XYAExcelServiceImpl.java
@Service("xyaExcelService")
public class XYAExcelServiceImpl implements ExcelService {
    
    @Override
    public ExportMbdeclareInfoDto exportMbdeclareInfo(List<VipMbdeclareInfoDto> list) {
        // 使用西安专用模板
        HSSFWorkbook workBook = new HSSFWorkbook(
            getClass().getClassLoader().getResourceAsStream("temp/mbmz_declareInfo_xya.xls")
        );
        // 填充西安特有的字段
    }
}
```

### 5.4 场景四：外部接口对接差异

#### 陕西医保接口（TSxMedicareService）

> 各地市调用统一的陕西医保平台，但传参和解析逻辑不同

```java
// 接口定义（统一）
public interface TSxMedicareService {
    LinkRuturnEntity call1101(Sx1101Vo vo);  // 资格校验
    LinkRuturnEntity call2102(Sx2101Vo vo);  // 购药结算
    LinkRuturnEntity call2503(Sx2503Vo vo);  // 备案同步
    // ... 更多接口
}
```

#### 调用示例：商洛vs西安
```java
// 商洛小程序 - SL
Sx1101Vo sx1101Vo = new Sx1101Vo();
sx1101Vo.setFlag(flag);  // 传入flag
sx1101Vo.setMdtrt_cert_type(Mdtrt_cert_typeEnum.jmsfz.getValue());
sx1101Vo.setMdtrt_cert_no(IDNO);
sx1101Vo.setCertno(IDNO);
sx1101Vo.setPsn_name(name);
call1101 = sxMedicareService.call1101(sx1101Vo);

// 西安小程序 - XYA
// 类似调用，但参数处理可能不同
```

---

## 六、代码调用链路：一次申报请求的完整旅程

```
用户在小程序提交申报（flag=xya）
          │
          ▼
┌─────────────────────────────────────┐
│ 1. FlagInterceptorConfig            │
│    提取请求头中的"flag=xya"         │
│    存入ThreadLocal                  │
└─────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ 2. Controller层                     │
│    @RequestHeader("flag") String flag │
│    调用Service时传递flag            │
└─────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ 3. MtbBeanFactory                   │
│    根据flag找到: MtbDeclareServiceXYA│
└─────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ 4. XYA专用Service                   │
│    MtbDeclareXYAServiceImpl         │
│    - 特殊文件上传路径               │
│    - XYA专用FTP配置                 │
│    - 西安特有的业务逻辑             │
└─────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ 5. 公共Service（可选）             │
│    如需通用逻辑，调用父类方法       │
│    super.commonMethod()             │
└─────────────────────────────────────┘
          │
          ▼
      返回结果
```

---

## 七、新增地市接入指南（CheckList）

> 🎯 假设我们要接入一个新地市"安康"（简称AK）

### 第一步：数据库配置

```sql
-- 在 t_mb_unit_config 表中新增记录
INSERT INTO t_mb_unit_config (
    name,           -- AK (与枚举名对应)
    flag,           -- ak (请求中传递)
    source,         -- ak_source
    top_unit_code,  -- 610900 (安康市医保编码)
    unit_code,      -- 610900
    unit_name,      -- 安康市
    service1,       -- ak_service
    service2,       -- akExcelService
    -- ... 其他配置
) VALUES (...);
```

### 第二步：创建枚举常量

```java
// 在 UnitConfigEnum.java 中新增
public final static UnitConfig AK = new UnitConfig();
```

### 第三步：创建Maven子模块

```
mtb-yh/
└── mtb-ak/                    # 新建目录
    ├── pom.xml
    └── src/main/java/
        └── com/picchealth/
            └── module/
                └── mtb/
                    └── service/
                        └── impl/
                            ├── MtbDeclareListAKServiceImpl.java
                            ├── XcxIndexAKServiceImpl.java
                            └── AKExcelServiceImpl.java
```

#### pom.xml 配置
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project>
    <parent>
        <groupId>com.picchealth</groupId>
        <artifactId>mtb-yh</artifactId>
    </parent>
    <artifactId>mtb-ak</artifactId>
    
    <dependencies>
        <!-- 依赖基础模块 -->
        <dependency>
            <groupId>com.picchealth</groupId>
            <artifactId>mtb-base</artifactId>
        </dependency>
    </dependencies>
</project>
```

#### 父模块 pom.xml 中注册
```xml
<!-- mtb-yh/pom.xml -->
<modules>
    <module>mtb-base</module>
    <module>mtb-ak</module>  <!-- 新增 -->
    <!-- 其他模块 -->
</modules>
```

### 第四步：实现差异化Service

#### 基础Service示例
```java
package com.picchealth.module.mtb.service.impl;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service("MtbDeclareListServiceAK")  // ⭐ 关键：bean名称格式
public class MtbDeclareListAKServiceImpl extends MtbDeclareListServiceImpl {

    @Override
    public ApiResponse<ResultPage<VipMbdeclareInfoDto>> queryVipMbdeclareInfoList(
            QueryMbDeclareListVo queryMbDeclareListVo) {
        
        // 1. 安康特有的数据处理
        log.info("安康申报列表查询");
        
        // 2. 设置安康特有的查询条件
        UnitConfig unitConfig = UnitConfigEnum.AK;
        // ...
        
        // 3. 调用父类通用逻辑（如果需要）
        // return super.queryVipMbdeclareInfoList(queryMbDeclareListVo);
        
        // 4. 或者完全自己实现
        // return customImplement();
        
        return null; // 根据实际情况返回
    }
    
    // 可以Override其他需要差异化的方法
}
```

#### 小程序端Service示例
```java
@Slf4j
@Service("XcxIndexServiceAK")
public class XcxIndexAKServiceImpl extends XcxIndexServiceImpl {

    // 安康特有的资格校验
    @Override
    public ApiResponse<CommonVo> getUploadPrescriptionList(CheckPrescriptionImgVo vo) {
        // 安康特有逻辑
    }
}
```

### 第五步：实现Excel导出Service（如需要）

```java
@Slf4j
@Service("akExcelService")
public class AKExcelServiceImpl implements ExcelService {

    @Override
    public ExportMbdeclareInfoDto exportMbdeclareInfo(List<VipMbdeclareInfoDto> list) {
        // 使用安康模板
        HSSFWorkbook workBook = new HSSFWorkbook(
            getClass().getClassLoader()
                .getResourceAsStream("temp/mbmz_declareInfo_ak.xls")
        );
        // 填充数据
        return null;
    }
}
```

### 第六步：准备Excel模板

```
src/main/resources/
└── temp/
    ├── mbmz_declareInfo_xya.xls  # 西安模板
    ├── mbmz_declareInfo_ak.xls   # ⭐ 新增安康模板
    └── ...
```

### 第七步：测试验证

#### 测试清单

| 测试项 | 验证点 |
|--------|--------|
| Flag传递 | 请求头正确传递flag=ak |
| ThreadLocal | FlagInterceptor正确存储 |
| Bean注入 | AK专用Service被正确加载 |
| 申报流程 | AK申报列表查询正常 |
| Excel导出 | 导出文件格式正确 |
| 权限控制 | AK数据隔离正确 |

#### 测试命令示例
```bash
# 模拟带flag的请求
curl -H "flag:ak" http://localhost:8080/api/mtb/declare/list
```

---

## 八、架构设计模式总结

### 8.1 使用的设计模式

| 模式 | 应用场景 | 示例 |
|------|----------|------|
| **模板方法模式** | 父类定义算法骨架，子类实现差异步骤 | MtbDeclareListServiceImpl |
| **工厂模式** | 根据flag创建不同的Service | MtbBeanFactory |
| **策略模式** | 不同地市使用不同算法 | Excel导出、申报流程 |
| **单例模式** | UnitConfigEnum常量 | 每个地市一个实例 |

### 8.2 优势与局限

#### ✅ 优势

1. **代码复用**：通用逻辑在mtb-base中维护
2. **快速扩展**：新增地市只需关注差异点
3. **独立演进**：各地市可独立迭代
4. **配置灵活**：通过数据库动态配置

#### ⚠️ 局限

1. **父类变更风险**：修改mtb-base可能影响所有地市
2. **复杂度**：需要理解整个调用链
3. **测试挑战**：需要覆盖所有地市场景

---

## 九、常见问题FAQ

### Q1: flag为空会怎样？
```java
// FlagInterceptorConfig中的处理
if (StringUtils.isBlank(flag)) {
    throw CustomException.createByMassage(888, "flag信息不能为空！");
}
```
**答案**：直接抛出异常，请求被拒绝。

### Q2: flag不存在会怎样？
```java
// UnitConfigEnum.fromFlag
if (StringUtils.isEmpty(flag) || "99".equals(flag)) {
    return BJ;  // 默认返回宝鸡
}
return mappings.get("FLAG:" + flag);  // 找不到返回null
```
**答案**：找不到时返回null，可能导致NPE。

### Q3: 能否同时支持多个地市？
**答案**：可以通过修改ThreadLocal存储多个flag，或在请求参数中显式传递。

### Q4: 如何查看当前请求属于哪个地市？
```java
// 在任意代码中
FlagLocal flagLocal = FlagUtils.getFlagLocal();
String flag = flagLocal.getFlag();
String unitCode = flagLocal.getUnitCode();
```

---

## 十、附录

### A. 文件清单

| 文件路径 | 作用 |
|----------|------|
| `FlagInterceptorConfig.java` | Flag拦截器 |
| `FlagLocal.java` | Flag上下文载体 |
| `FlagUtils.java` | Flag工具类 |
| `UnitConfigEnum.java` | 地市枚举配置 |
| `UnitConfig.java` | 地市配置实体 |
| `MtbBeanFactory.java` | Service工厂 |
| `CheckFlagUtil.java` | Flag校验工具 |

### B. 命名规范

| 类型 | 命名格式 | 示例 |
|------|----------|------|
| 地市模块 | mtb-{缩写} | mtb-xya |
| Bean名称 | {原始名}{地市缩写} | MtbDeclareServiceXYA |
| Excel模板 | {原始名}_{地市缩写} | mbmz_declareInfo_xya |
| Service2 | {地市缩写}ExcelService | xyaExcelService |

---

> 📝 文档版本：v1.0
> 
> 📅 更新日期：2024年
> 
> 👨‍💻 编写目的：帮助开发者快速理解地市差异化机制，降低新地市接入门槛

---

📎 **延伸阅读**：
- [项目全貌](picc-mzmtb-server-项目全貌.md) - 了解13个地市模块的整体结构和文件分布
- [API接口全景](picc-mzmtb-server-API接口全景.md) - 查看各地市特有的API接口(如商洛/延安/榆林)
- [处方与药店管理解析](picc-mzmtb-server-处方与药店管理解析.md) - 各地市处方管理、药店缴费的差异化实现

