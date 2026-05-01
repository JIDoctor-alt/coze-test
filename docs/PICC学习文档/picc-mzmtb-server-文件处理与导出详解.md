# PICC门诊慢特病业务服务（picc-mzmtb-server）文件处理与导出功能深度解析

## 一、系统概述

### 1.1 项目简介

PICC门诊慢特病业务服务（picc-mzmtb-server）是基于 **Spring Boot + MyBatis** 技术栈构建的慢特病管理系统，服务于陕西省12个地市的医疗保险业务。项目涉及大量文件处理需求，包括Excel数据导入导出、PDF文档生成、文件上传存储、图片处理等核心功能。

### 1.2 技术栈概览

| 技术领域 | 框架/工具 | 版本 |
|---------|----------|------|
| **Excel处理** | Apache POI | 4.1.2 |
| **PDF生成** | Apache PDFBox | 2.0.21 |
| **PDF生成** | iText (部分模块) | - |
| **文件上传** | Apache Commons FileUpload | - |
| **文件传输** | Apache Commons Net (FTP) | - |
| **安全传输** | JSch (SFTP) | - |
| **Office转换** | JodConverter | - |
| **图片处理** | Java ImageIO / BufferedImage | 内置 |
| **JSON处理** | FastJSON / Hutool | - |

---

## 二、Excel导出功能（把数据库的表格印成Excel文件）

### 2.1 核心架构设计

#### 2.1.1 Excel服务接口设计

```java
// ExcelService.java - 统一的Excel处理接口
public interface ExcelService {
    VipFilepath ExcelFile(VipFilepath vipFilepath);              // 解析导入Excel
    VipFilepath ExcelUpdateFile(VipFilepath vipFilepath);        // 解析修改导入Excel
    ExportMbdeclareInfoDto exportMbdeclareInfo(List<VipMbdeclareInfoDto> list);
    String uploadExcel(InputStream fis, String fileName, String uploadFlag);
    String doErrDownload(String fileName);                        // 下载错误文件
    String doUpErrDownload(String fileName);                      // 下载修改错误文件
    ExportMbdeclareInfoDto exportMbdeclareInfoWithId(List<VipMbdeclareInfoDto> list, List<String> idList);
    ExportMbdeclareInfoDto exportProInfo(List<VipMbdeclareInfoDto> list);
    ExportMbdeclareInfoDto exportProInfoWithId(List<VipMbdeclareInfoDto> list, List<String> idList);
}
```

#### 2.1.2 地市差异化实现策略

系统为12个地市实现了不同的Excel处理服务，通过 **策略模式 + 工厂模式** 实现：

```java
// 地市配置枚举
public enum UnitConfigEnum {
    YA("延安", "yaExcelService", "0002"),
    SL("商洛", "slExcelService", "0003"),
    BJ("宝鸡", "bjExcelService", "0004"),
    FX("阜新", "fxExcelService", "0005"),
    // ... 其他地市
    ;
}
```

### 2.2 POI使用详解

#### 2.2.1 两种Excel格式支持

```java
// 判断文件格式（兼容2003和2007+版本）
String hz = fileName.substring(fileName.lastIndexOf("."));
Workbook workbook;
if (hz.equals(ExcelTypeEnum.XLS.getValue())) {
    workbook = new HSSFWorkbook(inputStream);  // 2003版本 (.xls)
} else if (hz.equals(ExcelTypeEnum.XLSX.getValue())) {
    workbook = new XSSFWorkbook(inputStream);  // 2007+版本 (.xlsx)
}
```

#### 2.2.2 工作表遍历与数据读取

```java
// 读取Excel数据
Sheet sheet = workbook.getSheetAt(0);
int rows = sheet.getPhysicalNumberOfRows();

for (int i = 1; i < rows; i++) {
    Row row = sheet.getRow(i);
    if (row == null) continue;
    
    // 强制转换为字符串类型读取
    row.getCell(j).setCellType(CellType.STRING);
    String cellValue = row.getCell(j).getStringCellValue();
    
    // 数据校验
    String errorMsg = checkData(j, cellValue, dataObject);
}
```

### 2.3 大数据量导出策略（流水线作业）

#### 2.3.1 流式导出机制

项目采用 **SXSSFWorkbook**（POI的流式API）处理大数据量导出：

```java
// ExcelWaterMarkUtil.java - 流式导出带水印的Excel
public static String SXSSFWorkbookForXlsx(SXSSFWorkbook workBook, String text) {
    File tempFile = null;
    FileOutputStream fos = null;
    OPCPackage pkg = null;
    XSSFWorkbook wb = null;
    
    try {
        // 1. 先将SXSSFWorkbook写入临时文件
        String l = System.nanoTime() + "1" + text;
        tempFile = File.createTempFile(l, ".xlsx");
        fos = new FileOutputStream(tempFile);
        workBook.write(fos);  // 流水线边造边写
        
        // 2. 转换为XSSFWorkbook以便添加水印
        pkg = OPCPackage.open(tempFile);
        wb = new XSSFWorkbook(pkg);
        
        // 3. 添加水印
        String s = excelWaterMarkForXlsx(wb, text);
        return s;
    } finally {
        // 资源关闭（注意顺序）
        if (wb != null) wb.close();
        if (pkg != null) pkg.close();
        if (fos != null) fos.close();
        if (workBook != null) workBook.close();
    }
}
```

#### 2.3.2 导出数据处理流程

```java
// SLExcelServiceImpl.java - 商洛导出实现
public ExportMbdeclareInfoDto exportMbdeclareInfo(List<VipMbdeclareInfoDto> list) {
    HSSFWorkbook workBook = null;
    ByteArrayOutputStream output = null;
    InputStream in = null;
    
    try {
        // 1. 加载模板
        workBook = new HSSFWorkbook(
            getClass().getClassLoader().getResourceAsStream("temp/mbmz_declare_info.xls")
        );
        
        // 2. 创建样式（复用，减少内存开销）
        CellStyle style = workBook.createCellStyle();
        style.setBorderBottom(BorderStyle.THIN);
        style.setAlignment(HorizontalAlignment.CENTER);
        
        // 3. 填充数据（逐行写入）
        for (VipMbdeclareInfoDto dto : list) {
            Row dataRow = sheet.createRow(rowNum++);
            // ... 填充单元格
        }
        
        // 4. 添加水印
        String userName = UserUtils.getUser().getUserName();
        String fileBase64 = ExcelWaterMarkUtil.excelWaterMarkForXls(workBook, userName);
        
        exportMbdeclareInfoDto.setFileBase64(fileBase64);
    } finally {
        // 关闭资源
    }
    return exportMbdeclareInfoDto;
}
```

### 2.4 导出模板机制

#### 2.4.1 模板文件管理

```java
// VipFilePathServiceImpl.java - 模板下载
public ApiResponse<FileResponseVo> downloadTemplateSL() {
    // 从classpath加载模板
    InputStream resourceAsStream = getClass().getClassLoader()
        .getResourceAsStream("temp/mbrydrmbsl.xlsx");
    
    XSSFWorkbook workBook = new XSSFWorkbook(resourceAsStream);
    String fileName = "人员批量导入模板.xlsx";
    
    // 转换为Base64返回
    ByteArrayOutputStream output = new ByteArrayOutputStream();
    workBook.write(output);
    String fileBase64 = FileUtils.getBase64FromInputStream(
        new ByteArrayInputStream(output.toByteArray())
    );
    
    FileResponseVo responseVo = new FileResponseVo();
    responseVo.setFile(fileBase64);
    responseVo.setName(fileName);
    return ApiResponse.ok(responseVo);
}
```

#### 2.4.2 地市模板差异

| 地市 | 模板文件 | 字段数量 | 特点 |
|------|---------|---------|------|
| 延安 | `mbrydrmb.xlsx` | 25列 | 包含七种病/十种病/两病区分 |
| 商洛 | `mbrydrmbsl.xlsx` | 26列 | 包含复审信息 |
| 宝鸡 | `mbrydrmbyl.xlsx` | 24列 | 职工/居民区分 |
| 榆林 | `mbrydrmbyh.xlsx` | 24列 | 简化字段 |
| 达州 | `mbrydrmb.xlsx` | 20列 | 基础字段 |

### 2.5 Excel水印添加机制（在文件上盖章）

#### 2.5.1 水印生成核心逻辑

```java
// FontImageUtil.java - 水印图片生成
public static BufferedImage createWatermarkImage(Watermark watermark) {
    // 1. 配置水印参数
    if (watermark == null) {
        watermark = new Watermark();
        watermark.setEnable(true);
        watermark.setText("内部资料");
        watermark.setColor("#C5CBCF");
        watermark.setDateFormat("yyyyMMdd");
    }
    
    // 2. 加载字体（支持中文）
    GraphicsEnvironment ge = GraphicsEnvironment.getLocalGraphicsEnvironment();
    if (!Arrays.stream(ge.getAllFonts()).anyMatch(f -> f.getName().equals("Microsoft YaHei UI"))) {
        PathMatchingResourcePatternResolver resolver = new PathMatchingResourcePatternResolver();
        Resource[] resources = resolver.getResources("classpath*:/**/config/MicrosoftYaHeiUI-Bold.ttf");
        Font font = Font.createFont(Font.TRUETYPE_FONT, resources[0].getInputStream());
        ge.registerFont(font);
    }
    
    // 3. 创建水印图片
    BufferedImage image = new BufferedImage(400, 200, BufferedImage.TYPE_INT_RGB);
    Graphics2D g = image.createGraphics();
    g.setColor(Color.white);
    g.fillRect(0, 0, width, height);
    g.setColor(new Color(Integer.parseInt(watermark.getColor().substring(1), 16)));
    g.setFont(new Font("Microsoft YaHei UI", Font.PLAIN, 15));
    g.shear(0.1, -0.26);  // 倾斜效果
    
    // 4. 绘制文字
    for (String s : textArray) {
        g.drawString(s, 0, y);
        y = y + g.getFontMetrics(g.getFont()).getHeight();
    }
    
    return image;
}
```

#### 2.5.2 XLSX格式水印（新版）

```java
// ExcelWaterMarkUtil.java - XLSX水印添加
public static String excelWaterMarkForXlsx(XSSFWorkbook workBook, String text) {
    // 1. 生成水印图片并转为字节流
    BufferedImage image = FontImageUtil.createWatermarkImage(
        new FontImageUtil.Watermark(true, text, null, null)
    );
    ByteArrayOutputStream os = new ByteArrayOutputStream();
    ImageIO.write(image, "png", os);
    
    // 2. 将图片添加到工作簿
    int pictureIdx = workBook.addPicture(os.toByteArray(), Workbook.PICTURE_TYPE_PNG);
    POIXMLDocumentPart poixmlDocumentPart = workBook.getAllPictures().get(pictureIdx);
    
    // 3. 为每个Sheet添加水印
    for (int i = 0; i < workbook.getNumberOfSheets(); i++) {
        XSSFSheet sheet = workbook.getSheetAt(i);
        PackagePartName ppn = poixmlDocumentPart.getPackagePart().getPartName();
        String relType = XSSFRelation.IMAGES.getRelation();
        PackageRelationship pr = sheet.getPackagePart()
            .addRelationship(ppn, TargetMode.INTERNAL, relType, null);
        sheet.getCTWorksheet().addNewPicture().setId(pr.getId());
    }
    
    // 4. 返回Base64编码
    ByteArrayOutputStream output = new ByteArrayOutputStream();
    workbook.write(output);
    return FileUtils.getBase64FromInputStream(
        new ByteArrayInputStream(output.toByteArray())
    );
}
```

#### 2.5.3 XLS格式水印（旧版）

```java
// ExcelWaterMarkUtil.java - XLS水印添加（复杂，需要操作底层Record）
public static String excelWaterMarkForXls(HSSFWorkbook workBook, String text) {
    // 1. 生成水印图片
    BufferedImage image = FontImageUtil.createWatermarkImage(
        new FontImageUtil.Watermark(true, text, null, null)
    );
    
    // 2. 转换为BMP格式（XLS水印必须是BMP）
    byte[] data = getBackgroundBitmapData(imagePath);
    
    // 3. 为每个Sheet添加BitmapRecord
    for (int k = 0; k < workbook.getNumberOfSheets(); k++) {
        HSSFSheet sheet = workbook.getSheetAt(k);
        InternalSheet internalsheet = sheet.getSheet();
        List<RecordBase> records = internalsheet.getRecords();
        
        // 创建BitmapRecord和ContinueRecord
        BitmapRecord bitmapRecord;
        List<ContinueRecord> continueRecords = new ArrayList<>();
        
        if (data.length > 8220) {
            // 大图片需要分块
            bitmapRecord = new BitmapRecord(Arrays.copyOfRange(data, 0, 8220));
            int bytes = 8220;
            while (bytes < data.length) {
                continueRecords.add(new ContinueRecord(
                    Arrays.copyOfRange(data, bytes, Math.min(bytes + 8220, data.length))
                ));
                bytes += 8220;
            }
        } else {
            bitmapRecord = new BitmapRecord(data);
        }
        
        // 插入到PageSettingsBlock之前
        int i = 0;
        for (RecordBase r : records) {
            if (r instanceof PageSettingsBlock) break;
            i++;
        }
        records.add(++i, bitmapRecord);
        for (ContinueRecord cr : continueRecords) {
            records.add(++i, cr);
        }
    }
    
    // 4. 返回Base64编码
    ByteArrayOutputStream output = new ByteArrayOutputStream();
    workbook.write(output);
    return FileUtils.getBase64FromInputStream(
        new ByteArrayInputStream(output.toByteArray())
    );
}
```

### 2.6 地市差异化导出实现

#### 2.6.1 延安导出（YAExcelServiceImpl）

```java
// 延安导出特点：支持七种病/十种病/两病分类导出
public ExportMbdeclareInfoDto exportMbdeclareInfo(List<VipMbdeclareInfoDto> list) {
    HSSFWorkbook workBook = new HSSFWorkbook();
    HSSFSheet sheet = workBook.createSheet("延安慢病申报列表");
    
    // 延安特有字段处理
    for (VipMbdeclareInfoDto dto : list) {
        // 七种病/十种病/两病分类
        if ("七种病".equals(dto.getIcdKindName())) {
            // 特殊处理
        } else if ("十种病".equals(dto.getIcdKindName())) {
            // 特殊处理
        }
        // ... 填充数据
    }
    
    return exportMbdeclareInfoDto;
}
```

#### 2.6.2 商洛导出（SLExcelServiceImpl）

```java
// 商洛导出特点：包含复审信息和专家审核结论
public ExportMbdeclareInfoDto exportMbdeclareInfo(List<VipMbdeclareInfoDto> list) {
    HSSFWorkbook workBook = new HSSFWorkbook();
    HSSFSheet sheet = workBook.createSheet("商洛慢病申报列表");
    
    // 商洛特有字段
    List<String> exportFields = Arrays.asList(
        "expertConclusionName",  // 专家审核结论
        "firstoperdate",         // 资料审核时间
        "initialnote",           // 资料审核意见
        "enjoyStartTime",       // 待遇享受开始时间
        "enjoyEndTime"          // 待遇享受结束时间
    );
    
    // ... 动态列导出
}
```

#### 2.6.3 宝鸡导出（BJExcelServiceImpl）

```java
// 宝鸡导出特点：与医保系统对接，需校验医保资格
public ExportMbdeclareInfoDto exportMbdeclareInfo(List<VipMbdeclareInfoDto> list) {
    // 宝鸡导出需要校验医保资格状态
    for (VipMbdeclareInfoDto dto : list) {
        // 调用医保系统校验
        CXRecordBVo vo = new CXRecordBVo();
        vo.setIdcard(dto.getIdcard());
        vo.setPsn_no(dto.getPsnNo());
        
        // 查询备案状态
        String result = CallCxcfService.recordInquire(vo);
        
        // 根据状态设置导出内容
        if (StringUtils.isNotEmpty(result)) {
            dto.setMedicalStatus("已备案");
        }
    }
}
```

#### 2.6.4 阜新导出（FXExcelServiceImpl）

```java
// 阜新导出特点：支持定点医疗机构信息
public ExportMbdeclareInfoDto exportMbdeclareInfo(List<VipMbdeclareInfoDto> list) {
    HSSFWorkbook workBook = new HSSFWorkbook();
    
    // 阜新特有字段
    // - 定点医疗机构编码
    // - 定点医疗机构名称
    // - 定点医院等级
    // - 审批编号
    
    // ... 填充数据
}
```

---

## 三、PDF生成功能（用模板填空，生成正式文件）

### 3.1 PDFBox水印机制

#### 3.1.1 核心水印工具

```java
// PdfWatermarkUtil.java - PDF水印添加
public static String pdfWatemark(InputStream inputStream, String text) {
    PDDocument document = null;
    InputStream fontStream = null;
    
    try {
        // 1. 加载PDF文档
        document = PDDocument.load(inputStream);
        
        // 2. 加载中文字体
        fontStream = PdfWatermarkUtil.class.getClassLoader()
            .getResourceAsStream("config/simsun.ttf");
        
        // 3. 构造水印内容（用户名+日期）
        LocalDateTime date = LocalDateTime.now();
        String watermarkText = text + "#" + dtf.format(date);
        
        // 4. 遍历每一页添加水印
        for (int i = 0; i < document.getNumberOfPages(); i++) {
            PDPage page = document.getPage(i);
            PDRectangle pageSize = page.getMediaBox();
            float pageWidth = pageSize.getUpperRightX();
            float pageHeight = pageSize.getUpperRightY();
            
            // 5. 创建内容流
            PDPageContentStream contentStream = new PDPageContentStream(
                document, page, APPEND, true, true
            );
            
            // 6. 设置字体和透明度
            PDFont pdFont = PDType0Font.load(document, fontStream);
            contentStream.setFont(pdFont, 10);
            contentStream.setNonStrokingColor(Color.GRAY);
            
            PDExtendedGraphicsState graphicsState = new PDExtendedGraphicsState();
            graphicsState.setNonStrokingAlphaConstant(0.3f);  // 30%透明度
            contentStream.setGraphicsStateParameters(graphicsState);
            
            // 7. 45度倾斜水印
            float rotationAngleRad = (float) Math.toRadians(45);
            contentStream.concatenate2CTM(
                Math.cos(rotationAngleRad), Math.sin(rotationAngleRad),
                -Math.sin(rotationAngleRad), Math.cos(rotationAngleRad),
                centerX * (1 - Math.cos(rotationAngleRad)) + centerY * Math.sin(rotationAngleRad),
                centerY * (1 - Math.cos(rotationAngleRad)) - centerX * Math.sin(rotationAngleRad)
            );
            
            // 8. 网格状绘制水印
            for (float x = 0; x < pageWidth; x += textWidth + horizontalSpacing) {
                for (float y = 0; y < pageHeight; y += textHeight + verticalSpacing + 20) {
                    contentStream.beginText();
                    contentStream.setTextMatrix(Matrix.getTranslateInstance(x, y));
                    contentStream.showText(watermarkText);
                    contentStream.endText();
                }
            }
            
            contentStream.close();
        }
        
        // 9. 保存并返回Base64
        ByteArrayOutputStream output = new ByteArrayOutputStream();
        document.save(output);
        return FileUtils.getBase64FromInputStream(
            new ByteArrayInputStream(output.toByteArray())
        );
    } finally {
        // 关闭资源
    }
}
```

#### 3.1.2 Base64输入支持

```java
// 支持Base64编码的PDF水印
public static String basePdfWatemark(String base64, String text) {
    BASE64Decoder decoder = new BASE64Decoder();
    byte[] bt = decoder.decodeBuffer(base64);
    ByteArrayInputStream stream = new ByteArrayInputStream(bt);
    return pdfWatemark(stream, text);
}
```

### 3.2 Office文档转PDF

#### 3.2.1 JodConverter转换引擎

```java
// File2ImageServiceImpl.java - Office转PDF
@Autowired(required = false)
private DocumentConverter documentConverter;

public void file2image(VipMbdeclareFile vipMbdeclareFile) {
    String fileName = vipMbdeclareFile.getFilename();
    String suffix = fileName.substring(fileName.lastIndexOf(".") + 1);
    
    if ("xls".equalsIgnoreCase(suffix) || "xlsx".equalsIgnoreCase(suffix)) {
        // Excel转PDF
        File srcFile = org.apache.commons.io.FileUtils.getFile(tempPath + fileName);
        File pdfFile = org.apache.commons.io.FileUtils.getFile(tempPath + pdfName);
        
        documentConverter.convert(srcFile).to(pdfFile).execute();
        
        // PDF再转图片
        inputStreamPng = OfficeConverterUtils.pdf2image(pdfFile);
    } else if ("doc".equalsIgnoreCase(suffix) || "docx".equalsIgnoreCase(suffix)) {
        // Word转PDF
        File srcFile = org.apache.commons.io.FileUtils.getFile(tempPath + fileName);
        File pdfFile = org.apache.commons.io.FileUtils.getFile(tempPath + pdfName);
        
        documentConverter.convert(srcFile).to(pdfFile).execute();
    }
}
```

### 3.3 PDF转图片

```java
// OfficeConverterUtils.java - PDF转图片
public static InputStream pdf2image(File pdfFile) throws Exception {
    List<BufferedImage> images = new ArrayList<>();
    String path = pdfFile.getParent() + File.separator;
    String fileName = pdfFile.getName().replace(".pdf", "");
    
    PDDocument document = PDDocument.load(pdfFile);
    PDPageTree list = document.getDocumentCatalog().getPages();
    
    int w = 0;
    int h = 0;
    int pageCounter = 0;
    
    // 1. 逐页渲染
    for (PDPage page : list) {
        PDFRenderer pdfRenderer = new PDFRenderer(document);
        BufferedImage image = pdfRenderer.renderImageWithDPI(pageCounter, 100, ImageType.RGB);
        
        String target = path + fileName + "-" + (pageCounter++) + ".png";
        ImageIOUtil.writeImage(image, target, 100);
        
        w = image.getWidth();
        h += image.getHeight();
        images.add(image);
        
        new File(target).delete();  // 删除临时页
    }
    
    document.close();
    
    // 2. 垂直拼接所有页面
    BufferedImage combined = new BufferedImage(w, h, BufferedImage.TYPE_INT_ARGB);
    Graphics g = combined.getGraphics();
    int y = 0;
    for (BufferedImage image : images) {
        g.drawImage(image, 0, y, null);
        y += image.getHeight();
    }
    
    // 3. 保存合并后的图片
    File imageFile = new File(path, fileName + ".png");
    ImageIO.write(combined, "PNG", imageFile);
    
    return new FileInputStream(imageFile);
}
```

---

## 四、文件上传与存储（快递寄件，把东西放到仓库）

### 4.1 文件上传接口分析

#### 4.1.1 上传流程概览

```
用户上传 → 文件类型校验 → Base64解码 → 临时存储 → SFTP上传 → 数据库记录 → 清理临时文件
```

#### 4.1.2 上传服务实现

```java
// VipMbdeclareFileServiceImpl.java - 申报材料上传
@Transactional(propagation = Propagation.REQUIRED)
public void uploadPhysicalFile(UploadPhyFileVo uploadFileVo) {
    String fileBase = uploadFileVo.getFileBase();
    byte[] bytes = Base64.getDecoder().decode(fileBase);
    InputStream inputStream = new ByteArrayInputStream(bytes);
    
    // 生成唯一文件名
    String tFilename = uploadFileVo.getFileName();
    int index = tFilename.lastIndexOf(".");
    SimpleDateFormat df = new SimpleDateFormat("yyyyMMddHHmmss");
    String fileName = tFilename.substring(0, index) + "-" + df.format(new Date()) 
                      + tFilename.substring(index);
    
    // 上传到SFTP
    SFTPUtils ftpFileUtil = new SFTPUtils();
    String filePath = "/mbdeclare/tjbg/" + declareId + "/";
    ftpFileUtil.createFile(filePath, inputStream, fileName);
    
    // 保存到数据库
    VipMbdeclareFile vipMbdeclareFile = new VipMbdeclareFile();
    vipMbdeclareFile.setDeclareid(declareId);
    vipMbdeclareFile.setFilepath(filePath);
    vipMbdeclareFile.setFilename(fileName);
    vipMbdeclareFile.setFiletype((short) FileTypeEnum.FILETYPE_PHYSICALREPORT.getIntValue());
    this.save(vipMbdeclareFile);
}
```

### 4.2 SFTP存储机制（专用快递通道）

#### 4.2.1 SFTP工具类

```java
// SFTPUtils.java - SFTP文件传输
@Component
public class SFTPUtils {
    private ChannelSftp sftpChannel;
    private Session session;
    
    @Value("${ftp.username:app}")
    public void setUserName(String Name) { userName = Name; }
    
    @Value("${sftp.port:22}")
    public void setPort(int ftpPort) { port = ftpPort; }
    
    @Value("${ftp.ip:10.252.68.236}")
    public void setIp(String ftpIp) { ip = ftpIp; }
    
    @Value("${ftp.privatekey:sftpkey/scprivatekey.bem}")
    public void setprivatekey(String key) { privatekey = key; }
    
    // 初始化连接
    public void initSFTPClient() {
        JSch jsch = new JSch();
        // 使用私钥认证
        InputStream privateKeyStream = Thread.currentThread()
            .getContextClassLoader().getResourceAsStream(privatekey);
        jsch.addIdentity("private_key_alias", IOUtils.toByteArray(privateKeyStream), null, null);
        
        session = jsch.getSession(userName, ip, port);
        session.setConfig("StrictHostKeyChecking", "no");
        session.connect();
        
        ChannelSftp channelSftp = (ChannelSftp) session.openChannel("sftp");
        channelSftp.connect();
        this.sftpChannel = channelSftp;
    }
    
    // 上传文件
    public boolean createFile(String pathname, InputStream fis, String filename) {
        try {
            if (sftpChannel == null || !sftpChannel.isConnected()) {
                initSFTPClient();
            }
            
            // 切换到目标目录（自动创建不存在的目录）
            String[] split = pathname.split("/");
            sftpChannel.cd("/");  // 从根目录开始
            for (String str : split) {
                if (!str.isEmpty()) {
                    try {
                        sftpChannel.cd(str);
                    } catch (Exception e) {
                        sftpChannel.mkdir(str);  // 目录不存在则创建
                        sftpChannel.cd(str);
                    }
                }
            }
            
            // 上传文件
            sftpChannel.put(fis, filename);
            return true;
        } finally {
            closeSFTPChannel();
        }
    }
    
    // 下载文件
    public InputStream downLoadto(String path, String filename) {
        if (sftpChannel == null || !sftpChannel.isConnected()) {
            initSFTPClient();
        }
        sftpChannel.cd("/" + path);
        return sftpChannel.get(filename);
    }
    
    // 删除文件
    public boolean deleteFile(String pathname, String filename) {
        sftpChannel.cd("/" + pathname);
        sftpChannel.rm(filename);
        return true;
    }
    
    // 关闭连接
    public void closeSFTPChannel() {
        if (sftpChannel != null && sftpChannel.isConnected()) {
            sftpChannel.disconnect();
        }
        if (session != null && session.isConnected()) {
            session.disconnect();
        }
    }
}
```

#### 4.2.2 FTP工具类（传统FTP协议）

```java
// FTPFileUtil_xcx.java - 传统FTP传输
@Component
public class FTPFileUtil_xcx {
    private FTPClient ftpClient = null;
    
    // 初始化FTP连接
    public void initFtpClient() {
        ftpClient = new FTPClient();
        ftpClient.connect(ip, Integer.parseInt(port));
        ftpClient.login(userName, pass);
        
        // 开启UTF-8支持
        if (FTPReply.isPositiveCompletion(ftpClient.sendCommand("OPTS UTF8", "ON"))) {
            LOCAL_CHARSET = "UTF-8";
        }
        ftpClient.setControlEncoding(LOCAL_CHARSET);
    }
    
    // 上传文件
    public boolean createFile(String pathname, InputStream fis, String filename) {
        try {
            // 自动创建目录
            String[] split = pathname.split("/");
            for (String str : split) {
                if (!StringUtils.isBlank(str)) {
                    if (!ftpClient.changeWorkingDirectory(str)) {
                        ftpClient.makeDirectory(str);
                    }
                    ftpClient.changeWorkingDirectory(str);
                }
            }
            
            ftpClient.enterLocalPassiveMode();
            ftpClient.setFileType(FTPClient.BINARY_FILE_TYPE);
            
            // 处理中文文件名
            return ftpClient.storeFile(
                new String(filename.getBytes(LOCAL_CHARSET), "ISO-8859-1"), 
                fis
            );
        } finally {
            // 关闭连接
        }
    }
    
    // 下载文件
    public InputStream downLoad(String path, String filename) {
        String[] split = path.split("/");
        for (String str : split) {
            if (!StringUtils.isBlank(str)) {
                ftpClient.changeWorkingDirectory(str);
            }
        }
        ftpClient.enterLocalPassiveMode();
        ftpClient.setFileType(FTPClient.BINARY_FILE_TYPE);
        return ftpClient.retrieveFileStream(
            new String(filename.getBytes(LOCAL_CHARSET), "ISO-8859-1")
        );
    }
}
```

### 4.3 文件类型校验与安全

#### 4.3.1 文件类型白名单

```java
// 支持的文件类型
public enum FileTypeEnum {
    FILETYPE_IDCARD_FRONT(1, "身份证正面"),
    FILETYPE_IDCARD_BACK(2, "身份证背面"),
    FILETYPE_MEDICAL_CARD(3, "医保卡"),
    FILETYPE_PRESCRIPTION(4, "处方"),
    FILETYPE_PHYSICALREPORT(5, "体检报告"),
    FILETYPE_APPLY_FORM(6, "申请表"),
    FILETYPE_UPLOAD(100, "上传文件");
    
    // ... 其他类型
}
```

#### 4.3.2 上传安全校验

```java
// 文件名校验
private boolean validateFileName(String fileName) {
    // 1. 检查文件扩展名
    String suffix = fileName.substring(fileName.lastIndexOf(".") + 1).toLowerCase();
    Set<String> allowedSuffix = new HashSet<>(Arrays.asList(
        "jpg", "jpeg", "png", "bmp", "pdf", "doc", "docx", "xls", "xlsx"
    ));
    if (!allowedSuffix.contains(suffix)) {
        return false;
    }
    
    // 2. 检查文件名长度
    if (fileName.length() > 200) {
        return false;
    }
    
    // 3. 检查危险字符
    if (fileName.contains("..") || fileName.contains("/") || fileName.contains("\\")) {
        return false;
    }
    
    return true;
}

// 文件大小校验
private boolean validateFileSize(InputStream inputStream, long maxSize) {
    byte[] buffer = new byte[8192];
    long count = 0;
    while (true) {
        int read = inputStream.read(buffer);
        if (read == -1) break;
        count += read;
        if (count > maxSize) {
            return false;
        }
    }
    return true;
}
```

---

## 五、图片处理（图片压缩/OCR/水印）

### 5.1 图片压缩

```java
// ImageQualityAssessmentUtil.java - 图片压缩
public static BufferedImage resizeImage(BufferedImage originalImage, double scale) {
    int width = (int) (originalImage.getWidth() * scale);
    int height = (int) (originalImage.getHeight() * scale);
    
    BufferedImage resizedImage = new BufferedImage(
        width, height, BufferedImage.TYPE_INT_RGB
    );
    Graphics2D g2d = resizedImage.createGraphics();
    
    // 平滑缩放
    g2d.drawImage(
        originalImage.getScaledInstance(width, height, Image.SCALE_SMOOTH),
        0, 0, null
    );
    g2d.dispose();
    
    return resizedImage;
}

// Base64编码
public static String encodeImageToBase64(BufferedImage image) throws IOException {
    try (ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
        ImageIO.write(image, "jpg", baos);
        baos.flush();
        byte[] imageBytes = baos.toByteArray();
        return Base64.getEncoder().encodeToString(imageBytes);
    }
}
```

### 5.2 OCR识别

```java
// 图片脱敏处理流程
public void imageMasking(String declareId, List<VipMbdeclareFile> mbfiles) {
    // 1. 创建临时目录
    String zipPath1 = "/mbdeclare/ocr/zipPath1/" + declareId + "/";
    
    // 2. 压缩原图
    ZipUtil.zip(zipPath1 + declareId, zipPath1 + declareId + ".zip", true);
    
    // 3. 调用OCR脱敏接口
    OkHttpClient client = new OkHttpClient.Builder()
        .connectTimeout(60, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .build();
    
    RequestBody requestBody = new MultipartBody.Builder()
        .setType(MultipartBody.FORM)
        .addFormDataPart("file", uploadFile.getName(),
            RequestBody.create(MediaType.parse("application/zip"), uploadFile))
        .addFormDataPart("pos", params.toJSONString())  // OCR识别位置
        .build();
    
    Request request = new Request.Builder()
        .url(URL5002)
        .post(requestBody)
        .build();
    
    Response response = client.newCall(request).execute();
    String resultBase64Data = JSON.parseObject(response.body().string())
        .getString("data");
    
    // 4. 解压脱敏后的图片
    ZipUtil.unzip(zipPath2 + declareId + ".zip", zipPath2 + declareId);
    
    // 5. 上传脱敏图片替换原图
    // ...
}
```

### 5.3 图片水印

```java
// 在已有图片上添加水印
public BufferedImage addWatermark(BufferedImage originalImage, String watermarkText) {
    Graphics2D g2d = originalImage.createGraphics();
    
    // 设置水印属性
    g2d.setComposite(AlphaComposite.getInstance(AlphaComposite.SRC_OVER, 0.3f));
    g2d.setColor(Color.GRAY);
    g2d.setFont(new Font("Arial", Font.PLAIN, 12));
    
    // 计算水印位置（右下角）
    int x = originalImage.getWidth() - g2d.getFontMetrics().stringWidth(watermarkText) - 10;
    int y = originalImage.getHeight() - 10;
    
    // 绘制水印
    g2d.drawString(watermarkText, x, y);
    g2d.dispose();
    
    return originalImage;
}
```

### 5.4 图片质检

```java
// 图片质量评估
public static String getAuthorizationHeader(String appId, String abilityId, 
        String secretId, String secretKey, String sceneId, String method, 
        String nonce, String timestamp) throws Exception {
    
    // 构建签名
    String normalizedHeaders = "ability=" + abilityId + "\n" +
                               "app_id=" + appId + "\n" +
                               "nonce=" + nonce + "\n" +
                               "scene_id=" + sceneId + "\n" +
                               "timestamp=" + timestamp + "\n";
    
    String stringToSign = method + "\n" + normalizedHeaders + "/";
    
    // HMAC-SHA256签名
    Mac mac = Mac.getInstance("HmacSHA256");
    SecretKeySpec secretKeySpec = new SecretKeySpec(
        secretKey.getBytes(StandardCharsets.UTF_8), "HmacSHA256"
    );
    mac.init(secretKeySpec);
    
    byte[] signatureBytes = mac.doFinal(stringToSign.getBytes(StandardCharsets.UTF_8));
    String signature = Base64.getEncoder().encodeToString(signatureBytes);
    
    return "HmacSHA256:" + secretId + ":" + signature;
}
```

---

## 六、ZIP打包下载（批量打包）

### 6.1 ZIP压缩工具

```java
// FileHelper.java - ZIP打包
public static void zipCompress(String src, String des) {
    File file = new File(src);
    File zipFile = new File(des);
    
    ZipOutputStream zipOut = null;
    FileInputStream input = null;
    
    try {
        zipOut = new ZipOutputStream(new FileOutputStream(zipFile));
        
        if (file.isDirectory()) {
            File[] lists = file.listFiles();
            for (File list : lists) {
                input = new FileInputStream(list);
                ZipEntry zipEntry = new ZipEntry(
                    file.getName() + File.separator + list.getName()
                );
                zipOut.putNextEntry(zipEntry);
                
                // 边读边写（流式）
                int temp;
                while ((temp = input.read()) != -1) {
                    zipOut.write(temp);
                }
                input.close();
            }
        }
    } finally {
        // 关闭资源
    }
}
```

### 6.2 ZIP解压工具

```java
// FileHelper.java - ZIP解压（支持GBK和UTF-8编码）
public static String DeCompress(String zipPath, String descDir) throws Exception {
    ZipFile zip = null;
    
    try {
        // 尝试GBK编码（Windows默认）
        zip = new ZipFile(new File(zipPath), Charset.forName("GBK"));
        
        for (Enumeration entries = zip.entries(); entries.hasMoreElements();) {
            ZipEntry entry = (ZipEntry) entries.nextElement();
            String zipEntryName = entry.getName();
            InputStream in = zip.getInputStream(entry);
            
            // 验证路径安全性（防止路径穿越攻击）
            String outPath = validateFileDir(descDir + File.separator + zipEntryName, descDir);
            
            // 创建目录
            File file = new File(outPath.substring(0, outPath.lastIndexOf('/')));
            if (!file.exists()) {
                file.mkdirs();
            }
            
            // 写入文件
            try (FileOutputStream out = new FileOutputStream(outPath)) {
                byte[] buf = new byte[1024];
                int len;
                while ((len = in.read(buf)) > 0) {
                    out.write(buf, 0, len);
                }
            }
        }
    } catch (Exception e) {
        // 尝试UTF-8编码（Mac/Linux）
        return DeCompressUTF8(zipPath, descDir);
    } finally {
        if (zip != null) zip.close();
    }
    
    return "SUCCESS";
}

// UTF-8编码解压
private static String DeCompressUTF8(String zipPath, String descDir) throws Exception {
    ZipFile zip = new ZipFile(new File(zipPath), StandardCharsets.UTF_8);
    // ... 类似处理
}
```

### 6.3 批量打包下载

```java
// VipMbdeclareFileServiceImpl.java - 批量附件打包
public FileResponseVo batchDownloadFiles(QueryMbInfoVo vo) {
    List<VipMbdeclareInfoDto> infoList = page.getData();
    String tempDir = "/tmp/batch_" + UUID.randomUUID().toString();
    
    // 1. 创建临时目录
    new File(tempDir).mkdirs();
    
    // 2. 下载所有附件到临时目录
    for (VipMbdeclareInfoDto info : infoList) {
        List<VipMbdeclareFile> files = getFilesByDeclareId(info.getId());
        for (VipMbdeclareFile file : files) {
            SFTPUtils ftp = new SFTPUtils();
            InputStream is = ftp.downLoadto(file.getFilePath(), file.getFileName());
            
            String localPath = tempDir + "/" + info.getName() + "_" + file.getFileName();
            FileUtils.saveFileByInputStream(is, localPath);
        }
    }
    
    // 3. 打包
    String zipPath = tempDir + ".zip";
    ZipUtil.zip(tempDir, zipPath, true);
    
    // 4. 读取并转为Base64
    File zipFile = new File(zipPath);
    byte[] zipBytes = Files.readAllBytes(zipFile.toPath());
    String base64 = Base64.getEncoder().encodeToString(zipBytes);
    
    // 5. 清理临时文件
    FileHelper.delDir(tempDir);
    
    return new FileResponseVo(base64, "batch_export.zip");
}
```

---

## 七、核心工具类速查表

| 工具类 | 职责 | 关键方法 |
|--------|------|---------|
| `ExcelWaterMarkUtil` | Excel水印添加 | `excelWaterMarkForXlsx()`, `excelWaterMarkForXls()` |
| `PdfWatermarkUtil` | PDF水印添加 | `pdfWatemark()`, `basePdfWatemark()` |
| `FontImageUtil` | 水印图片生成 | `createWatermarkImage()` |
| `SFTPUtils` | SFTP文件传输 | `createFile()`, `downLoad()`, `deleteFile()` |
| `FTPFileUtil_xcx` | FTP文件传输 | `createFile()`, `downLoad()` |
| `FileUtils` | 文件基础操作 | `getBase64FromInputStream()`, `saveFileByInputStream()` |
| `FileHelper` | 文件压缩解压 | `zipCompress()`, `DeCompress()` |
| `UploadUtil` | 文件上传解析 | `parseParam()` |
| `OfficeConverterUtils` | Office转图片 | `pdf2image()` |
| `ImageQualityAssessmentUtil` | 图片压缩质检 | `resizeImage()`, `encodeImageToBase64()` |
| `CommonUtils` | 通用工具 | `checkIdentityCardValue()`, `getBase64FromInputStream()` |

---

## 八、最佳实践总结

### 8.1 内存管理

1. **流式处理**：大数据量导出使用 `SXSSFWorkbook`，避免OOM
2. **及时关闭**：所有流操作必须在 finally 块中关闭
3. **临时文件清理**：操作完成后立即删除临时文件

### 8.2 安全建议

1. **文件类型校验**：仅允许白名单内的文件类型
2. **路径穿越防护**：解压时验证目标路径在允许范围内
3. **文件名清理**：去除文件名中的特殊字符和路径分隔符
4. **私钥安全**：SFTP私钥文件妥善保管，不提交到代码仓库

### 8.3 性能优化

1. **连接池复用**：SFTP/FTP连接使用单例或连接池
2. **异步处理**：OCR识别、图片脱敏等耗时操作使用异步任务
3. **分批处理**：大量文件操作时分批进行，避免长时间占用

### 8.4 地市差异化策略

1. **配置驱动**：通过枚举类管理地市配置，便于扩展
2. **策略模式**：不同地市使用不同的服务实现
3. **模板分离**：各地市使用独立的Excel模板文件

---

## 九、配置参考

### 9.1 FTP/SFTP配置

```yaml
# application.yml
ftp:
  ip: 10.252.68.236
  port: 22
  username: app
  password: hellolevy
  path: /picc/ftpuser/
  privatekey: sftpkey/scprivatekey.bem

xcxftp:
  ip: 10.252.68.155
  port: 21
  username: hmlink
  password: hmlink@123
```

### 9.2 文件路径配置

```yaml
ftp:
  mbmz: /mbmz/                    # 慢病导入文件
  mbmzError: /mbmz/error/        # 导入错误文件
  mbmzUpdate: /mbmzupdate/       # 修改导入文件
  appexl: /dev/ya/appexl/        # APP导入Excel

tmp:
  uploadpath: /tmp/upload         # 上传临时目录
  zippath: ~/test/zip/            # ZIP打包目录
  file2img: D:/temp/              # 文件转图片目录
```

---

**文档版本**: v1.0  
**分析日期**: 2024年  
**源码位置**: `/tmp/picc-mzmtb-server/`
