# PICC导入导出功能代码解析——小白版

> 📅 更新日期：2024年5月
> 🎯 适用版本：picc-mzmtb-server 全模块
> 👶 阅读前提：懂一点Java，不懂Excel也没关系

---

## 零、先搞懂几个概念（5分钟入门）

### 0.1 什么是导入？什么是导出？

**导入（Import）** = 把Excel表格里的数据"复制粘贴"到数据库里

> 打个比方：老师让你把Excel里的学生成绩表发到班级群里，你上传Excel文件，系统自动把每个人的成绩录入数据库——这就是导入。

**导出（Export）** = 从数据库里查出数据，生成一个Excel文件让你下载

> 打个比方：学期末老师要从系统里导出所有学生的成绩单，打印出来发给家长——这就是导出。

### 0.2 Apache POI是什么？

**Apache POI** 是一个Java库，专门用来操作Microsoft Office文件（包括Excel）。

这个项目用到了POI的三种Excel处理方式：

| 类 | 适用场景 | 特点 | 项目里的名字 |
|---|---|---|---|
| **HSSF** | `.xls`格式（2003版） | 经典格式，最大行数65536 | HSSFWorkbook |
| **XSSF** | `.xlsx`格式（2007+版） | 新格式，容量大 | XSSFWorkbook |
| **SXSSF** | 大数据量导出 | 流式处理，不占内存 | SXSSFWorkbook |

> 💡 小白理解：
> - HSSF = 老式大巴车，座位少（6万行），但稳稳当当
> - XSSF = 新式高铁，座位多（100万行），但比较占地方（内存）
> - SXSSF = 流水线式的旅游大巴，一批一批上车，不用所有人都站在车里等

### 0.3 为什么要分地市？

陕西医保系统需要在多个地市上线，每个地市的政策、流程、表格格式都不一样：

| 地市 | 代码中的标识 | 说明 |
|---|---|---|
| 宝鸡 | BJ | 最早一批上线 |
| 延安 | YA | 典型代表 |
| 商洛 | SL | 有年审功能 |
| 榆林 | YH | 多版本模板 |
| 其他 | DZ/JZ/FX等 | 陆续上线 |

每个地市就像一个"方言区"，虽然基本流程差不多，但具体细节（字段校验规则、模板格式、业务流程）各不相同。

---

## 一、导入功能：从Excel到数据库

### 1.1 导入的整体流程

```
用户上传Excel文件
       ↓
  文件保存到服务器（FTP/SFTP）
       ↓
  系统读取Excel内容
       ↓
  数据逐行校验（必填项、格式、重复等）
       ↓
   ┌────┴────┐
   ↓         ↓
有错误      全部通过
   ↓         ↓
生成带错误标记的Excel  写入数据库
（错误文件下载）       ↓
                 导入完成
```

### 1.2 入口在哪？（API层代码解析）

**文件位置**：`mtb-base/src/main/java/com/picchealth/module/mtb/api/MtbImportApi.java`

```java
@RestController
@Api(value = "慢病人员导入", tags = "慢病人员导入")
@RequestMapping(value = "/v1/MbImport")
public class MtbImportApi {
    
    // ① 文件上传接口
    @RequestMapping(method = {RequestMethod.POST}, value = "/uploadMBFile")
    public ApiResponse<String> uploadMBFileYH(HttpServletRequest request) {
        // 获取文件路径服务
        MtbFilePathService mtbFilePathService = MtbBeanFactory.getService(MtbFilePathService.class);
        // 执行上传
        mtbFilePathService.uploadMBFileYH(TypeEnum.IMPORT.getValue(), request);
        return ApiResponse.ok();
    }
    
    // ② 导入执行接口
    @RequestMapping(method = {RequestMethod.POST}, value = "/importMBfile")
    public ApiResponse<String> importMBfileYH(T vo) {
        MtbFilePathService mtbFilePathService = MtbBeanFactory.getService(MtbFilePathService.class);
        // 执行导入
        mtbFilePathService.importMBfileYH(vo, TypeEnum.IMPORT.getValue());
        return ApiResponse.ok();
    }
    
    // ③ 错误文件下载接口
    @RequestMapping(method = {RequestMethod.POST}, value = "/doErrDownload")
    public ApiResponse<String> doErrDownloadYH(T vo) {
        MtbFilePathService mtbFilePathService = MtbBeanFactory.getService(MtbFilePathService.class);
        return mtbFilePathService.doErrDownloadYH(vo);
    }
}
```

> 📝 小白注释：
> - `@RestController` = 告诉Spring这是处理请求的"服务员"
> - `HttpServletRequest` = 用户的请求，里面包含上传的文件
> - `MtbBeanFactory.getService()` = 工厂模式，根据地市获取对应的服务

### 1.3 Excel文件怎么读进来的？（POI读取逻辑）

**文件位置**：`picchealth-server/src/main/java/com/picchealth/module/mb/service/impl/YAExcelServiceImpl.java`

```java
@Override
public VipFilepath ExcelFile(VipFilepath vipFilepath) {
    InputStream inputStream = null;
    Workbook workbook = null;
    SFTPUtils ftpFileUtil = new SFTPUtils();  // SFTP工具，用于从服务器下载文件
    
    try {
        // ① 从FTP服务器下载Excel文件到内存
        String tFilePath = vipFilepath.getFilePath();
        inputStream = ftpFileUtil.downLoadto(tFilePath, vipFilepath.getFileName());
        
        // ② 根据文件后缀判断Excel版本
        String fileName = vipFilepath.getFileName();
        String hz = fileName.substring(fileName.lastIndexOf("."));  // 取".xls"或".xlsx"
        
        // ③ 创建Workbook对象（这一步"打开"Excel）
        if (hz.equals(ExcelTypeEnum.XLS.getValue())) {
            workbook = new HSSFWorkbook(inputStream);  // 2003版格式
        } else if (hz.equals(ExcelTypeEnum.XLSX.getValue())) {
            workbook = new XSSFWorkbook(inputStream);  // 2007+版格式
        } else {
            // 不支持的格式，直接返回错误
            vipFilepath.setImportMessage("导入失败，只支持xls、xlsx类型文件！");
            return vipFilepath;
        }
        
        // ④ 获取第一个Sheet（工作表）
        Sheet sheet = workbook.getSheetAt(0);
        
        // ⑤ 遍历每一行数据
        int rows = sheet.getPhysicalNumberOfRows();  // 获取总行数
        for (int i = 2; i < rows; i++) {  // 从第3行开始（跳过表头）
            Row row = sheet.getRow(i);  // 获取当前行
            if (row == null) continue;  // 空行跳过
            
            // ⑥ 遍历每一列，读取单元格的值
            int cellNum = row.getPhysicalNumberOfCells();
            for (int j = 0; j < cellNum; j++) {
                // 设置单元格类型为字符串，避免数字/日期格式问题
                row.getCell(j).setCellType(CellType.STRING);
                String cellValue = row.getCell(j).getStringCellValue();
                
                // 这里开始你的业务逻辑...
            }
        }
    } catch (Exception e) {
        log.error("导入失败:", e);
        vipFilepath.setImportMessage("导入失败，未知异常！");
    } finally {
        // ⑦ 关闭流，释放资源
        if (inputStream != null) inputStream.close();
        if (workbook != null) workbook.close();
        ftpFileUtil.closeSFTPChannel();
    }
    
    return vipFilepath;
}
```

> 📝 小白注释：
> - `Workbook` = 相当于Excel软件打开的一个文件
> - `Sheet` = Excel里的"工作表"（底部标签页）
> - `Row` = 一行数据
> - `Cell` = 一个单元格
> - `SFTPUtils` = 用SFTP协议从远程服务器下载文件

### 1.4 数据校验怎么做的？

**核心代码位置**：YAExcelServiceImpl第173行 `checkData()`方法

```java
// 校验逻辑的核心片段
String errorMsg = "";

// 【校验点1】第一个单元格（机构编码）不能为空
if (j == 0 && StringUtils.isEmpty(cellValue)) {
    errorMsg += "机构编码不能为空;";
    break;  // 跳出当前列的循环，处理下一行
}

// 【校验点2】诊断信息必填
if (j > 18) {  // 诊断相关的列
    if (j == 19 && StringUtils.isEmpty(cellValue)) {
        errorMsg += "请选择诊断信息;";
    }
}

// 【校验点3】定点医院必填
if (j == 9) {
    if (StringUtils.isEmpty(cellValue)) {
        errorMsg += "请输入定点医院信息；";
    } else {
        ghihos.setHosname(cellValue);  // 保存医院信息
    }
}

// 【校验点4】身份证号格式校验
if ("0".equals(ghi.getAppntidtype()) && !CommonUtils.checkIdentityCardValue(ghi.getAppntidno())) {
    errorMsg += "证件号码错误；";
}

// 【校验点5】诊断名称有效性校验
try {
    String[] icdCodes = yaBusinessService.getIcdCodes(...);
    ghi.setIcdcode(icdCodes[0]);
} catch (CustomException e) {
    errorMsg += e.getMessage() + ";";
}
```

### 1.5 校验失败怎么办？（错误文件机制）

当某一行数据校验失败时，系统会把错误信息**写在同一行的最后一列**，方便用户修改：

```java
// 如果有错误信息
if (!StringUtils.isEmpty(errorMsg)) {
    // 在第26列（COLNUM_CNT = 25）写入错误原因
    row.createCell(COLNUM_CNT).setCellValue(errorMsg);
    errorNumber++;  // 错误计数+1
    errorMsg = "";  // 清空错误信息，准备处理下一行
    continue;  // 跳过这行，继续处理下一行
}
```

**导入完成后的状态统计**：

```java
// 延安代码第342-356行
importInfo = "导入完成！";
if (successNum > 0) {
    importInfo += "成功导入" + successNum + "条慢病人员信息；";
}
vipFilepath.setImportStatus(VipMbmzImportStatusEnum.DONE.getValue());

if (existNum > 0) {
    importInfo += "有" + existNum + "条慢病人员信息已经存在，不能重复导入;";
    vipFilepath.setImportStatus(VipMbmzImportStatusEnum.FAIL.getValue());
}
if (errorNumber > 0) {
    importInfo += "有" + errorNumber + "条慢病人员信息校验不通过，请下载并修改后再进行导入;";
    vipFilepath.setImportStatus(VipMbmzImportStatusEnum.FAIL.getValue());
}
```

**导入状态枚举**（VipMbmzImportStatusEnum）：

| 状态码 | 含义 | 触发场景 |
|---|---|---|
| `0` | 未处理 | 刚上传，还没开始导入 |
| `1` | 已处理 | 全部成功导入 |
| `2` | 处理失败 | 有错误或重复 |
| `3` | 与模板不符 | 表头格式不对 |

### 1.6 数据怎么入库的？

**延安实现**：单条数据入库（`importOne`方法）

```java
@Transactional(propagation = Propagation.REQUIRED)  // 加事务，保证数据一致性
private void importOne(GhiInsureDetail ghi, GhiInsureHos ghihos, UnitConfig unitConfig) {
    String userId = UserUtils.getUser().getUserId();  // 获取当前操作用户
    
    // ① 先查VIP用户表，看是否已存在
    List<VipInfo> vipInfos = vipInfoService.getByIdcardAndName(
        ghi.getInsuredidno(), ghi.getInsurednname());
    
    if (!vipInfos.isEmpty()) {
        // 用户已存在，更新手机号
        VipInfo vipInfo = vipInfos.get(0);
        ghi.setVipid(vipInfo.getId());
        if (!mobile.equals(vipInfo.getMobile())) {
            vipInfo.setMobile(mobile);
            vipInfoService.save(vipInfo);
        }
    } else {
        // 用户不存在，新建
        VipInfo vipInfo = getVipInfo(ghi);  // 把Excel数据转成VipInfo对象
        vipInfoService.save(vipInfo);
        ghi.setVipid(vipInfo.getId());
    }
    
    // ② 保存慢病主表数据
    ghiInsureDetailService.save(ghi);
    
    // ③ 保存医院关联表数据
    ghihos.setGhiid(ghi.getId());
    ghihos.setCreator(userId);
    ghiInsureHosService.save(ghihos);
    
    // ④ 启动审批流程（如果配置了工作流）
    if (unitConfig.getWorkflowFlag() != null) {
        String process = unitConfig.getWorkflowFlag() + "mbsb";
        Map<String, Object> variables = new HashMap<>();
        variables.put("startType", StartTypeEnum.RYDR.getIntValue());
        // 启动Activiti工作流
        ProcessInstance instance = runtimeService.startProcessInstanceByKey(
            process, ghi.getContno(), variables);
        Task task = taskService.createTaskQuery()
            .processInstanceId(instance.getId()).singleResult();
        taskService.complete(task.getId());
    }
}
```

> 📝 小白注释：
> - `@Transactional` = 保证这一系列操作要么全部成功，要么全部失败，不会出现"一半数据入库"的情况
> - `VipInfo` = 会员/用户信息表
> - `GhiInsureDetail` = 慢病保险详细信息表
> - `GhiInsureHos` = 慢病和医院的关联表
> - Activiti = 工作流引擎，用于审批流程

### 1.7 不同地市的差异在哪？

| 地市 | Service Bean名 | 主要差异 |
|---|---|---|
| 延安 | `yaExcelService` | 业务逻辑最完整，有单独的计算限额方法 |
| 商洛 | `slExcelService` | 多了表头校验、年审功能 |
| 宝鸡 | `bjExcelService` | 最早实现，流程最简洁 |
| 榆林 | `yhExcelService` | 支持多版本模板下载 |

**工厂模式获取服务**（UnitInfoUtils）：

```java
// 根据flag获取对应的Excel服务
public static ExcelService getService(String flag) {
    UnitConfig unitConfig = UnitConfigEnum.fromFlag(flag);
    String key = unitConfig.getService2();  // 如"yaExcelService"
    return SpringContext.getApplicationContext().getBean(key, ExcelService.class);
}

// 使用示例
ExcelService service = UnitInfoUtils.getService("YA");  // 获取延安服务
service.ExcelFile(vipFilepath);  // 执行导入
```

---

## 二、导出功能：从数据库到Excel

### 2.1 导出的整体流程

```
用户点击"导出"按钮
       ↓
  查询数据库，筛选条件
       ↓
  加载Excel模板文件
       ↓
  把数据一行行写入Excel
       ↓
  （可选）给Excel加水印
       ↓
  生成Base64编码的文件
       ↓
  返回给前端下载
```

### 2.2 入口在哪？

导出功能通常在**申报信息查询页面**，通过 `MbDeclareInfoApi` 或类似的API触发。

### 2.3 模板加载机制

**文件位置**：`picchealth-server/src/main/java/com/picchealth/module/mb/service/impl/VipFilePathServiceImpl.java`

```java
@Override
public ApiResponse<FileResponseVo> downloadTemplate() {
    XSSFWorkbook workBook = null;
    ByteArrayOutputStream output = null;
    
    try {
        // ① 从resources/temp目录下加载模板
        InputStream resourceAsStream = getClass()
            .getClassLoader()
            .getResourceAsStream("temp/mbrydrmbbj.xlsx");
        
        // ② 打开模板
        workBook = new XSSFWorkbook(resourceAsStream);
        
        // ③ 转成字节流
        output = new ByteArrayOutputStream();
        workBook.write(output);
        
        // ④ 转成Base64（方便网络传输）
        InputStream in = new ByteArrayInputStream(output.toByteArray());
        String fileBase64 = FileUtils.getBase64FromInputStream(in);
        
        // ⑤ 返回文件信息
        FileResponseVo responseVo = new FileResponseVo();
        responseVo.setFile(fileBase64);
        responseVo.setName("人员批量导入模板.xlsx");
        return ApiResponse.ok(responseVo);
    } catch (IOException e) {
        return null;
    }
}
```

**模板文件存放位置**：`src/main/resources/temp/`

| 模板文件名 | 用途 |
|---|---|
| `mbrydrmbbj.xlsx` | 宝鸡人员导入模板 |
| `mbrydrmbsl.xlsx` | 商洛人员导入模板 |
| `mbrydrmbyl.xlsx` | 榆林人员导入模板 |
| `mbmz_declareInfo_ya.xls` | 延安导出申报信息模板 |

### 2.4 数据填充逻辑

**延安导出实现**（YAExcelServiceImpl第644行）：

```java
@Override
public ExportMbdeclareInfoDto exportMbdeclareInfo(List<VipMbdeclareInfoDto> vipMbdeclareInfoList) {
    HSSFWorkbook workBook = null;
    
    try {
        // ① 加载模板
        InputStream resourceAsStream = getClass()
            .getClassLoader()
            .getResourceAsStream("temp/mbmz_declareInfo_ya.xls");
        workBook = new HSSFWorkbook(resourceAsStream);
        HSSFSheet sheet = workBook.getSheetAt(0);
        
        // ② 设置日期格式
        SimpleDateFormat sf = new SimpleDateFormat("yyyy年MM月dd日");
        DecimalFormat dfMoney = new DecimalFormat("###,###,##0.00");
        
        // ③ 设置单元格样式
        HSSFCellStyle ztStyle = workBook.createCellStyle();
        ztStyle.setBorderBottom(BorderStyle.valueOf((short) 1));  // 下边框
        ztStyle.setBorderLeft(BorderStyle.valueOf((short) 1));    // 左边框
        ztStyle.setAlignment(HorizontalAlignment.CENTER);          // 水平居中
        ztStyle.setVerticalAlignment(VerticalAlignment.CENTER);   // 垂直居中
        
        // ④ 遍历数据，写入Excel
        if (CollectionUtils.isNotEmpty(vipMbdeclareInfoList)) {
            for (int i = 0; i < vipMbdeclareInfoList.size(); i++) {
                VipMbdeclareInfoDto vipMbdeclareInfo = vipMbdeclareInfoList.get(i);
                
                // 从第4行开始写入（跳过标题行和表头）
                HSSFRow row = sheet.createRow((int) (i + 3));
                row.setHeightInPoints((float) 22.5);  // 行高22.5磅
                
                int k = 0;  // 列索引
                
                // 档案编号
                HSSFCell cell = row.createCell(k++);
                cell.setCellStyle(ztStyle);
                cell.setCellValue(vipMbdeclareInfo.getRecordno() != null 
                    ? vipMbdeclareInfo.getRecordno() : "-");
                
                // 姓名
                cell = row.createCell(k++);
                cell.setCellStyle(ztStyle);
                cell.setCellValue(vipMbdeclareInfo.getName() != null 
                    ? vipMbdeclareInfo.getName() : "-");
                
                // 性别（枚举转文字）
                String sex = "";
                if (SexEnum.MAN.getIntValue() == Integer.parseInt(vipMbdeclareInfo.getSex())) {
                    sex = "男性";
                } else if (SexEnum.WOMAN.getIntValue() == Integer.parseInt(vipMbdeclareInfo.getSex())) {
                    sex = "女性";
                }
                cell = row.createCell(k++);
                cell.setCellStyle(ztStyle);
                cell.setCellValue(sex);
                
                // ... 更多字段，类似处理
            }
        }
        
        // ⑤ 返回导出结果
        return null;  // 实际项目中有更复杂的返回逻辑
    } finally {
        if (workBook != null) workBook.close();
    }
}
```

### 2.5 水印怎么加的？

**文件位置**：`picchealth-server/src/main/java/com/picchealth/utils/ExcelWaterMarkUtil.java`

**XLSX格式水印**（新版本Excel）：

```java
public static String excelWaterMarkForXlsx(XSSFWorkbook workBook, String text) {
    try {
        // ① 生成水印图片
        BufferedImage image = FontImageUtil.createWatermarkImage(
            new FontImageUtil.Watermark(true, text, null, null));
        
        // ② 把图片转成字节流
        ByteArrayOutputStream os = new ByteArrayOutputStream();
        ImageIO.write(image, "png", os);
        
        // ③ 把水印图片嵌入Excel
        int pictureIdx = workBook.addPicture(os.toByteArray(), Workbook.PICTURE_TYPE_PNG);
        POIXMLDocumentPart poixmlDocumentPart = workBook.getAllPictures().get(pictureIdx);
        
        // ④ 给每个Sheet添加水印
        for (int i = 0; i < workBook.getNumberOfSheets(); i++) {
            XSSFSheet sheet1 = workBook.getSheetAt(i);
            PackagePartName ppn = poixmlDocumentPart.getPackagePart().getPartName();
            String relType = XSSFRelation.IMAGES.getRelation();
            PackageRelationship pr = sheet1.getPackagePart()
                .addRelationship(ppn, TargetMode.INTERNAL, relType, null);
            sheet1.getCTWorksheet().addNewPicture().setId(pr.getId());
        }
        
        // ⑤ 返回Base64编码
        try (ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            workBook.write(output);
            return Base64.getEncoder().encodeToString(output.toByteArray());
        }
    } catch (Exception e) {
        log.info("excel文件添加水印异常", e);
    }
    return "";
}
```

**水印效果**：给导出的Excel文件添加带用户名的斜向水印，防止截图泄密。

### 2.6 大数据量导出怎么处理的？（SXSSF流式导出）

**文件位置**：`picchealth-server/src/main/java/com/picchealth/module/mb/service/impl/VipDrugstoreOrderServiceImpl.java`

```java
@Override
public ApiResponse<ExportMbdeclareInfoDto> exportDrugstoreOrderReportList(...) {
    SXSSFWorkbook workBook = null;
    XSSFWorkbook wb = null;
    
    try {
        // ① 先用XSSF加载模板
        InputStream resourceAsStream = getClass()
            .getClassLoader()
            .getResourceAsStream("temp/onecard_drugstore_order.xlsx");
        wb = new XSSFWorkbook(resourceAsStream);
        
        // ② 转换成SXSSF（关键步骤！）
        // SXSSF会"抛弃"已经写入磁盘的行，节省内存
        workBook = new SXSSFWorkbook(wb);
        workBook.setCompressTempFiles(true);  // 启用临时文件压缩
        
        // ③ 获取Sheet
        SXSSFSheet sheet = workBook.getSheetAt(0);
        
        // ④ 正常写入数据...
        for (int i = 0; i < dataList.size(); i++) {
            SXSSFRow row = sheet.createRow(i + 1);
            // 写入单元格...
        }
        
        // ⑤ 加水印（如果是SXSSF，需要特殊处理）
        String fileBase64 = ExcelWaterMarkUtil.SXSSFWorkbookForXlsx(workBook, userName);
        
        return ApiResponse.ok(fileBase64);
        
    } finally {
        // ⑥ 清理临时文件
        if (workBook != null) {
            workBook.dispose();  // 删除临时文件
            workBook.close();
        }
    }
}
```

> 📝 小白注释：
> - 普通XSSF：所有数据都在内存里，10万行就可能内存溢出
> - SXSSF：写一行丢一行，用磁盘临时文件存储"过期的行"，内存占用稳定

### 2.7 导出权限控制

**文件位置**：`mtb-base/src/main/java/com/picchealth/module/mb/dto/ExportPermissionDto.java`

```java
/**
 * 导出权限DTO
 */
@Data
public class ExportPermissionDto {
    /**
     * 账号
     */
    private String account;
    
    /**
     * 地市标识（如：15 榆林）
     */
    private String flag;
    
    /**
     * 是否有导出权限 1：有权限
     */
    private String isexport;
}
```

导出前会检查用户是否有权限，没有权限的用户不能导出数据。

---

## 三、文件上传与存储

### 3.1 上传流程

**文件位置**：`picchealth-server/src/main/java/com/picchealth/module/mb/service/impl/VipFilePathServiceImpl.java`

```java
@Override
public void uploadMBFile(String flag, HttpServletRequest request) {
    // ① 解析请求参数
    ParamDto paramDto = UploadUtil.parseParam(request);
    String uploadFlag = paramDto.getParamMap().get("flag");
    List<FileItem> fileList = paramDto.getFileMap().get("fileList");
    
    if (!fileList.isEmpty()) {
        // ② 生成新文件名（加时间戳，防止重名覆盖）
        String tFileName = fileList.get(0).getName();
        int index = tFileName.lastIndexOf(".");
        SimpleDateFormat df = new SimpleDateFormat("yyyyMMddHHmmss");
        String time = df.format(new Date());
        String fileName = tFileName.substring(0, index) + "-" + time 
            + tFileName.substring(index);
        
        // ③ 上传到FTP/SFTP服务器
        try (InputStream inputStream = fileList.get(0).getInputStream()) {
            path = UnitInfoUtils.getService(uploadFlag)
                .uploadExcel(inputStream, fileName, flag);
        }
    }
    
    // ④ 保存文件记录到数据库
    VipFilepath vipFilepath = new VipFilepath();
    vipFilepath.setFilePath(path);           // 文件服务器路径
    vipFilepath.setFileName(fileName);       // 文件名
    vipFilepath.setUploadTime(new Date());    // 上传时间
    vipFilepath.setImportStatus("0");        // 未处理状态
    vipFilepath.setUnitId(unitConfig.getUnitCode());  // 所属机构
    vipFilepath.setCreator(userId);           // 上传人
    vipFilepathDao.save(vipFilepath);
}
```

### 3.2 FTP/SFTP存储

项目使用SFTP协议将文件存储到远程服务器：

```java
// SFTPUtils的使用
SFTPUtils ftpFileUtil = new SFTPUtils();

// 下载文件
InputStream inputStream = ftpFileUtil.downLoadto(filePath, fileName);

// 上传文件
ftpFileUtil.uploadFile(inputStream, fileName, remotePath);

// 关闭连接
ftpFileUtil.closeSFTPChannel();
```

### 3.3 文件路径管理

**导入路径配置**（YAExcelServiceImpl）：

```java
@Value("${ftp.mbmz:/mbmz/}")
private String mbmzPath;              // 正常文件存放路径

@Value("${ftp.mbmzError:/mbmz/error/}")
private String mbmzErrorPath;        // 错误文件存放路径

@Value("${ftp.mbmzUpdate:/mbmzupdate/}")
private String uploadUpdatePath;      // 修改导入文件路径

@Value("${ftp.mbmzUpdateError:/mbmzupdate/error/}")
private String errorUpdatePath;       // 修改导入错误文件路径
```

---

## 四、设计模式与架构亮点

### 4.1 策略模式+工厂模式（地市分发）

```
                    ┌─────────────────┐
                    │   ExcelService  │
                    │    (接口)        │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ↓                    ↓                    ↓
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ YAExcelService│   │ SLExcelService│   │ BJExcelService│
│   (延安)       │   │   (商洛)       │   │   (宝鸡)       │
└───────────────┘   └───────────────┘   └───────────────┘
```

**工厂获取服务**：

```java
// 根据flag获取对应的Service
public static ExcelService getService(String flag) {
    UnitConfig unitConfig = UnitConfigEnum.fromFlag(flag);
    String key = unitConfig.getService2();
    return SpringContext.getApplicationContext().getBean(key, ExcelService.class);
}

// 使用示例
ExcelService service = UnitInfoUtils.getService("YA");  // 延安
service.ExcelFile(vipFilepath);  // 执行导入
```

### 4.2 模板方法模式（导入流程）

每个地市的导入Service都实现`ExcelService`接口，保证流程一致：

```java
public interface ExcelService {
    // 解析导入excel
    VipFilepath ExcelFile(VipFilepath vipFilepath);
    
    // 解析修改导入excel
    VipFilepath ExcelUpdateFile(VipFilepath vipFilepath);
    
    // 导出申报信息
    ExportMbdeclareInfoDto exportMbdeclareInfo(List<VipMbdeclareInfoDto> list);
    
    // 上传excel
    String uploadExcel(InputStream fis, String fileName, String uploadFlag);
    
    // 下载错误文件
    String doErrDownload(String fileName);
}
```

### 4.3 代码复用与差异化的平衡

| 层面 | 复用内容 | 差异化内容 |
|---|---|---|
| **接口层** | 统一API入口 | 不同地市调不同Service |
| **工具层** | SFTP工具、水印工具 | - |
| **枚举层** | 状态枚举、类型枚举 | - |
| **Service层** | 基本结构相同 | 业务逻辑、表头校验规则 |

---

## 五、关键代码速查表

### 5.1 导入核心代码位置

| 功能 | 文件位置 | 关键方法 |
|---|---|---|
| API入口 | `MtbImportApi.java` | `uploadMBFile()`, `importMBfile()` |
| 文件上传 | `VipFilePathServiceImpl.java` | `uploadMBFile()` |
| Excel解析 | `YAExcelServiceImpl.java` | `ExcelFile()` |
| 数据校验 | `YAExcelServiceImpl.java` | `checkData()` |
| 数据入库 | `YAExcelServiceImpl.java` | `importOne()` |

### 5.2 导出核心代码位置

| 功能 | 文件位置 | 关键方法 |
|---|---|---|
| 模板下载 | `VipFilePathServiceImpl.java` | `downloadTemplate()` |
| 数据导出 | `YAExcelServiceImpl.java` | `exportMbdeclareInfo()` |
| 水印添加 | `ExcelWaterMarkUtil.java` | `excelWaterMarkForXlsx()` |
| 大数据导出 | `VipDrugstoreOrderServiceImpl.java` | SXSSF流式导出 |

### 5.3 工具类速查

| 工具 | 位置 | 用途 |
|---|---|---|
| `UploadUtil` | `mtb-base/.../mtb/utils/` | 解析HTTP上传请求 |
| `FileUtils` | `picchealth-server/.../utils/` | Base64编码/解码 |
| `SFTPUtils` | 全局 | SFTP文件传输 |
| `ExcelWaterMarkUtil` | `picchealth-server/.../utils/` | Excel添加水印 |
| `UnitInfoUtils` | `mtb-base/.../mb/enums/` | 地市服务工厂 |

### 5.4 枚举类速查

| 枚举 | 位置 | 用途 |
|---|---|---|
| `ExcelTypeEnum` | `picchealth-server/.../mb/enums/` | Excel格式（.xls/.xlsx） |
| `UnitConfigEnum` | `mtb-base/.../mb/enums/` | 地市配置映射 |
| `VipMbmzImportStatusEnum` | `picchealth-server/.../mb/enums/` | 导入状态 |
| `TypeEnum` | `mtb-base/.../mb/enums/` | 操作类型（导入/修改导入） |

---

## 六、常见问题排查

### Q1：导入时报"不支持的文件格式"

**原因**：上传了`.xls`或`.xlsx`以外的文件

**解决**：检查`ExcelTypeEnum`是否包含该后缀

### Q2：导入时报"表头与模板不匹配"

**原因**：商洛等地区有表头校验逻辑

**解决**：下载最新模板，确保表头完全一致

### Q3：大数据量导出内存溢出

**原因**：使用了`XSSFWorkbook`，所有数据在内存中

**解决**：改用`SXSSFWorkbook`流式导出

### Q4：水印没有生效

**原因**：
1. XLS格式水印和XLSX格式水印实现不同
2. 临时文件没有清理

**解决**：
1. XLS用`excelWaterMarkForXls()`
2. XLSX用`SXSSFWorkbookForXlsx()`
3. 调用`workbook.dispose()`清理临时文件

---

## 七、参考文档

- 之前的文档：`./picc-mzmtb-server-文件处理与导出详解.md`
- POI官方文档：https://poi.apache.org/
- SXSSF流式导出：适合10万行以上数据导出

---

> 📝 **文档维护建议**：
> - 新增地市时，在地市列表中添加记录
> - 修改模板路径时，同步更新表格
> - 发现文档与代码不符时，以代码为准并更新文档
