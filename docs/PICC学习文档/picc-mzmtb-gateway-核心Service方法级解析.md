# PICC门诊慢特病前台服务（picc-mzmtb-gateway）- 核心Service方法级深度解析

> 📖 **阅读指南**：本文档专为"零基础小白"设计，用最通俗的语言+生动的比喻，带你彻底搞懂这个项目的核心Service。即使你刚学Java三天，也能看懂！
> 
> ⚠️ **敏感信息已脱敏**：所有真实的机构编码、IP地址、密钥等已用占位符替代

---

# Part 1：前置知识 —— 小白也能懂的"行话翻译"

## 🎯 一句话总结

**前台服务 = 高级中介**，它不自己做饭（没有数据库），而是帮你点餐后跑去后厨催单，然后把菜摆盘好看再端给你。

---

## 🍽️ 餐饮类比：前台服务的角色

| 专业术语 | 餐饮比喻 | 大白话解释 |
|---------|--------|-----------|
| **Service** | 前台经理 | 处理客人特殊需求，简单的直接传给后厨 |
| **VO (Value Object)** | 外卖包装盒 | 把后厨做好的菜换一种方式包好给客人 |
| **Request VO** | 点餐单 | 客人填的需求单（要什么、几份、地址） |
| **Response VO** | 摆盘后的菜 | 服务员端上来的成品 |
| **HttpForwardUtil** | 服务员 | 拿着点餐单跑到后厨喊"3号桌要一份宫保鸡丁！" |
| **Controller/API** | 收银台 | 接收客人订单，给号牌的地方 |

---

## 🏠 为什么前台服务没有DAO层？

**业务服务（后厨）**：有自己的厨房（数据库），可以自己做菜
```java
// 业务服务 - 有自己的数据库
@Service
public class UserService {
    @Autowired
    private UserMapper userMapper; // 直接操作数据库
}
```

**前台服务（前台）：没有厨房，只能转单**
```java
// 前台服务 - 没有自己的数据库
@Service
public class AccountService {
    @Autowired
    private HttpForwardUtil httpForwardUtil; // 只能远程调用业务服务
    
    // 用户问："我的慢病账户余额是多少？"
    // 前台经理回答："我去问问后厨"
    public AccountInfo queryBalance(...) {
        // 跑去后厨问
        return httpForwardUtil.post("/queryBalance", request, vo, ApiResponse.class);
    }
}
```

---

# Part 2：核心Service全景图

## 📊 Service文件大盘点

项目共有 **14个Service实现类**，分布在以下位置：

```
src/main/java/com/picchealth/module/
├── mb/service/impl/           # 慢病管理核心Service
│   ├── VipMbdeclareInfoServiceImpl.java       ⭐ 申报信息+图片处理+医保校验
│   ├── VipMbDeclareServiceImpl.java           ⭐ 申报审核表下载（Excel/PDF）
│   ├── VipMbdeclareFileServiceImpl.java       ⭐ 申报文件+FTP读取+PDF生成
│   ├── VipAccountmbmzServiceImpl.java         ⭐ 账户管理+Excel导出
│   ├── VipDrugstoreOrderServiceImpl.java      ⭐ 药店订单+报表打印
│   ├── ChronicManageServiceImpl.java          ⭐ 慢病管理+Banner图+验证码
│   ├── ZipDownloadServiceImpl.java            ⭐ 批量打包下载（ZIP）
│   ├── SLExcelServiceImpl.java                ⭐ 商洛Excel导出
│   ├── YaExcelServiceImpl.java                ⭐ 延安Excel导出
│   ├── BJMedicalInsuranceServiceImpl.java      ⭐ 北京医保资格校验
│   └── CallJkscServiceImpl.java               ⭐ 小程序认证+SM2加密
├── ws/service/impl/             # WebService接口
│   └── VipMbsbserviceImpl.java               ⭐ 慢病备案信息同步
└── thirdfee/service/impl/       # 第三方费用
    └── OffLineDetailReportServiceImpl.java   （空实现）
```

---

# Part 3：核心Service方法级深度拆解

---

## 🏆 1️⃣ VipMbdeclareInfoServiceImpl —— 申报信息处理全能选手

**一句话解释**：这个Service是申报信息的"瑞士军刀"，处理图片上传、医保资格校验、各种城市的审批表PDF生成。

**核心能力**：
- 📤 图片上传到FTP服务器
- 🏥 医保系统资格校验
- 📄 多城市审批表PDF生成（商洛/北京/云南/贵州）
- 🔐 RSA加密解密

---

### 方法：editImage

**一句话人话**：用户上传了图片，前台帮你存到FTP服务器，然后通知后厨更新数据库

**参数说明**：
| 参数 | 类型 | 作用 | 打个比方 |
|-----|------|-----|---------|
| `editImagesVo` | EditImagesVo | 包含多张图片和申报ID | 客人的多张照片 |
| `request` | HttpServletRequest | HTTP请求对象（用来传Token） | 客人的工牌 |
| `url` | String | 后厨的接口地址 | 通知哪个部门 |

**返回值**：`ApiResponse`（后厨处理结果）

**逐步拆解**：
```java
// 1. 生成日期文件夹路径
String dateName = new SimpleDateFormat("yyyy-MM-dd").format(new Date());
// 格式：/mbdeclare/mbedit/2024-01-15/

// 2. 遍历每张图片
for (EditImageVo image : editImagesVo.getImages()) {
    // 3. Base64解码（前端传的是Base64格式）
    byte[] imageByte = new BASE64Decoder().decodeBuffer(image.getContent());
    
    // 4. 生成唯一文件名（UUID）
    String fileName = UUID.randomUUID() + ".jpg";
    // 例如：f47ac10b-58cc-4372-a567-0e02b2c3d479.jpg
    
    // 5. 上传到SFTP服务器
    SFTPUtils ftpFileUtil = new SFTPUtils();
    String urlpath = filePath + dateName + "/";
    ftpFileUtil.createFile(urlpath, inputStream, fileName);
    
    // 6. 把FTP路径更新到图片对象
    image.setContent(urlpath + fileName);
}

// 7. 转发给后厨更新数据库
return httpForwardUtil.post(url, request, editImagesVo, ApiResponse.class);
```

**调用链**：
```
用户上传图片 → 前台Service处理图片 → 上传SFTP → 
转发给后厨(/mb/editImage) → 后厨更新数据库
```

**调用的远程服务**：`/mb/editImage`（后厨的申报管理服务）

**异常处理**：
- FTP上传失败 → 抛出 `CustomException("上传失败")`
- Base64解析失败 → 抛出 `CustomException("文件解析失败")`

**小白易懵点**：
- ⚠️ 为什么用SFTP而不是FTP？因为SFTP更安全，像SSH一样加密传输
- ⚠️ 为什么路径要带日期？方便按日期管理文件，不至于所有文件堆在一起

---

### 方法：VIPQueryChronicBalance

**一句话人话**：去医保系统查查这个人还有多少慢病额度可以用

**参数说明**：
| 参数 | 类型 | 作用 |
|-----|------|-----|
| `vo` | CheckBalanceVo | 包含身份证号和就诊类型 |

**返回值**：`ApiResponse<YBMessageVo>`（医保信息：职工/居民、医院名称等）

**逐步拆解**：
```java
// 1. 构造医保查询请求
JSONObject inJson = new JSONObject();
inJson.put("AKB020", code);              // 医疗机构编码
inJson.put("AAC002", vo.getIdcard());    // 身份证号（脱敏后）
inJson.put("AKA130", vo.getVisitkind()); // 就诊类型（慢病/两病）

// 2. 调用医保接口（调用北京接口1001）
LinkRuturnEntity responseJson = callBJ1001(inJson);

// 3. 解析返回结果
if (responseJson.getSuccess()) {
    YBMessageVo messageVo = new YBMessageVo();
    // AAE140=3 表示职工，其他表示居民
    messageVo.setPlanttype("3".equals(row.getString("AAE140")) ? "职工" : "居民");
    messageVo.setOrganization(row.getString("AAB004")); // 参保单位
}

// 4. 返回给用户
return ApiResponse.ok(messageVo);
```

**调用的远程服务**：北京医保接口（`callBJ1001` → `baseCallService.callService("CH001", reqJson)`）

**小白易懵点**：
- ⚠️ 这是真正的外部系统调用，不是走后厨HTTP
- ⚠️ `callBJ1001()` 封装了医保系统的XML报文格式，非常专业
- ⚠️ AKB020、AAC002这些是医保系统的标准字段编码

---

### 方法：credentialsSL / credentialsBJ / credentialsYH / credentialsJZ / credentialsGZ

**一句话人话**：生成不同城市的审批表PDF（商洛/北京/云南/贵州/广州）

**参数说明**：
| 参数 | 类型 | 作用 |
|-----|------|-----|
| `map` | Map<String, String> | 审批表数据（姓名、身份证、病种等） |
| `vo` | IdVo | 用户ID |

**返回值**：`ImageFileVo`（包含PDF的Base64编码）

**逐步拆解（以credentialsSL为例）**：
```java
// 1. 根据数据量判断用哪个模板
// 5个字段 → 职工模板(sl_zg.ftl)
// 其他 → 居民模板(sl_jm.ftl)
String paths = map.size() == 5 ? "sl_zg.ftl" : "sl_jm.ftl";

// 2. 复制模板文件到容器（如果不存在）
String toReportPath = reportPath + paths;
File reportFile = new File(toReportPath);
if (!reportFile.exists()) {
    FileUtils.fileChannelCopy(resourceReportPath, toReportPath);
}

// 3. FreeMarker模板引擎填充数据
Configuration cfg = new Configuration(Configuration.VERSION_2_3_23);
Template t = cfg.getTemplate(ftlPath);
t.process(hashMap, writer);  // 把数据塞进模板

// 4. HTML转PDF
ITextRenderer renderer = new ITextRenderer();
renderer.setDocumentFromString(writer.toString());
renderer.createPDF(os);

// 5. PDF转Base64返回
String fileBase64 = FileUtils.getBase64FromInputStream(in);
fileVo.setBase(fileBase64);
```

**模板选择逻辑**：
```
商洛(SL)：sl_zg.ftl（职工）/ sl_jm.ftl（居民）
北京(BJ)：BJ_SHB.ftl
云南(YH)：YH_SHB.ftl
贵州(JZ)：JZ_SHB.ftl
广州(GZ)：GZ.ftl
```

**小白易懵点**：
- ⚠️ 为什么需要复制模板文件？因为容器内路径和宿主机路径不同
- ⚠️ 为什么PDF转Base64？因为前端需要以JSON形式接收二进制文件
- ⚠️ `processMap()` 方法会把FTP上的签名图片下载并转Base64

---

### 方法：editImageJJ / editImageJC

**一句话人话**：上传体检报告图片（JJ=体检）或检查报告图片（JC=检查）

**与editImage的区别**：
| 方法 | 路径 | 用途 |
|-----|------|-----|
| `editImage` | `/mbdeclare/mbedit/` | 普通申报资料图片 |
| `editImageJJ` | `/mbdeclare/mbedit/JJ/` | 体检报告图片 |
| `editImageJC` | `/mbdeclare/mbedit/JC/` | 检查报告图片 |

**小白易懵点**：
- ⚠️ 不同的文件类型存在不同的FTP目录，方便分类管理

---

## 🏆 2️⃣ VipMbDeclareServiceImpl —— 申报审核表下载专家

**一句话解释**：这个Service专门负责把慢病审核表做成Excel和PDF格式下载。

---

### 方法：downLoad

**一句话人话**：帮用户下载一份"慢性病门诊医疗审批表"Excel文件

**参数说明**：
| 参数 | 类型 | 作用 | 打个比方 |
|-----|------|-----|---------|
| `vipMbdeclareInfo` | VipMbdeclareInfo | 申报信息（姓名、身份证、病种等） | 客人的基本信息 |
| `request` | HttpServletRequest | HTTP请求对象 | 客人的请求 |
| `response` | HttpServletResponse | HTTP响应对象 | 端菜的盘子 |

**返回值**：`void`（直接往response里写文件流）

**逐步拆解**：
```java
// 1. 加载Excel模板（mbAuditForm.xls）
resourceAsStream = getClass().getClassLoader()
    .getResourceAsStream("temp/mbAuditForm.xls");

// 2. 打开Excel的第一个sheet
HSSFSheet sheet = wb.getSheetAt(0);

// 3. 找到特定单元格，填入数据
HSSFRow row1 = sheet.getRow(2);
HSSFCell cell11 = row1.getCell(1);
cell11.setCellValue(vipMbdeclareInfo.getName());  // 填姓名

HSSFCell cell13 = row1.getCell(3);
cell13.setCellValue("0".equals(vipMbdeclareInfo.getSex()) ? "男" : "女"); // 填性别

HSSFRow row4 = sheet.getRow(4);
HSSFCell cell42 = row4.getCell(2);
cell42.setCellValue(vipMbdeclareInfo.getIcdname()); // 填病种名称

// 4. 设置响应头，告诉浏览器这是Excel文件
response.setContentType("application/msexcel");
response.setHeader("Content-Disposition", "attachment; filename=慢性病门诊医疗审批表.xls");

// 5. 写入输出流
wb.write(outputStream);
```

**易懵点**：
- ⚠️ 模板文件放在 `resources/temp/` 目录下
- ⚠️ 只有审核通过的申报才能下载（`applystatus == PASS`）
- ⚠️ Excel的行列索引从0开始，但模板通常预留了表头行

---

### 方法：exportPdfData

**一句话人话**：根据人员身份（职工/居民）和病种类型（慢病/两病）生成不同的PDF审批表

**参数说明**：
| 参数 | 类型 | 作用 |
|-----|------|-----|
| `treatmentVo` | TreatmentVo | 治疗信息（人员类型、病种等） |

**返回值**：`ApiResponse<List<FileResponseVo>>`（可能返回多个PDF）

**模板选择逻辑**：
```
                    ┌─ 职工 ──→ "zg.ftl"模板
人员身份 ───────────┤
                    └─ 居民 ──┬─ 两病(icdkind=3 && icdtype=3) ──→ "lb.ftl"
                              └─ 慢特病 ──→ "mtb.ftl"
```

**逐步拆解**：
```java
// 1. 处理签名图片（FTP下载转Base64）
processMap(treatmentVo);

// 2. 根据人员身份选模板
if ("3".equals(treatmentVo.getPersontype())) {
    ftlPath = "templates/zg.ftl";      // 职工模板
} else {
    // 居民还要细分病种
    if ("3".equals(icdkind) && "3".equals(icdtype)) {
        ftlPath = "templates/lb.ftl";    // 两病模板
    } else {
        ftlPath = "templates/mtb.ftl";   // 慢特病模板
    }
}

// 3. FreeMarker模板引擎填充数据
Configuration cfg = new Configuration(Configuration.VERSION_2_3_23);
Template t = cfg.getTemplate(ftlPath);
t.process(hashMap, writer);

// 4. 用iTextRenderer把HTML转PDF
ITextRenderer renderer = new ITextRenderer();
renderer.setDocumentFromString(writer.toString());
renderer.createPDF(os);

// 5. 把PDF转Base64返回
String fileBase64 = FileUtils.getBase64FromInputStream(in);
```

**易懵点**：
- 🔥 FTP上的签名图片URL需要下载转Base64再塞进模板
- 🔥 `processMap()` 方法专门处理签名图片

---

## 🏆 3️⃣ VipMbdeclareFileServiceImpl —— 申报文件处理专家

**一句话解释**：处理申报相关的文件（图片、PDF），负责从FTP读取、转换格式、生成审批表。

---

### 方法：getPicPath

**一句话人话**：从FTP下载申报相关的图片（证件照、病历等）

**参数说明**：
| 参数 | 类型 | 作用 |
|-----|------|-----|
| `vo` | SelectPicPathVo | 文件ID |
| `request` | HttpServletRequest | HTTP请求对象（传Token） |
| `url` | String | 后厨接口地址 |

**返回值**：`ApiResponse<byte[]>`（图片二进制数据）

**逐步拆解**：
```java
// 1. 先问后厨拿文件元数据
ApiResponse<VipMbdeclareFile> response = 
    httpForwardUtil.post(url, request, vo, parameterizedTypeReference);

VipMbdeclareFile vipMbdeclareFile = response.getData();

// 2. 根据文件类型选择不同的FTP配置
if (filetype == FileTypeEnum.FILETYPE_PHYSICALREPORT) {
    // 体检报告 → 用SFTPUtils下载
    SFTPUtils ftpFileUtil = new SFTPUtils();
    InputStream inputStream = ftpFileUtil.downLoadto(filepath, filename);
} else if (filetype == FileTypeEnum.FILETYPE_PRESCRIPTION) {
    // 理赔资料 → 用SFTPUtils_xcx下载（小程序专用）
    SFTPUtils_xcx ftpFileUtil_xcx = new SFTPUtils_xcx();
    InputStream inputStream = ftpFileUtil_xcx.downLoadto(filepath, filename);
} else {
    // 普通申报资料 → 用SFTPUtils下载
    SFTPUtils ftpFileUtil = new SFTPUtils();
    InputStream inputStream = ftpFileUtil.downLoadto(filepath, filename);
}

// 3. 从FTP下载图片并转Base64
String imageStr = FTPFileUtil.getBase64FromInputStream(inputStream);

// 4. Base64转byte[]返回
imageByte = new BASE64Decoder().decodeBuffer(imageStr);
```

**调用的远程服务**：`/vipMbDeclareList/getPicture`（后厨的申报文件查询接口）

**易懵点**：
- ⚠️ 不同文件类型用不同的SFTP客户端（小程序的和普通的分开）
- ⚠️ 为什么分三个FTP？因为不同业务线的文件存储在不同的服务器

---

### 方法：makePdf

**一句话人话**：生成审批表PDF，支持多个城市模板

**参数说明**：
| 参数 | 类型 | 作用 |
|-----|------|-----|
| `map` | Map<String, String> | 审批表数据 |
| `vo` | IdVo | 用户ID |

**返回值**：`ImageFileVo`（PDF的Base64编码）

**支持的模板**：
| 城市 | 模板文件 |
|-----|---------|
| 商洛 | sl_zg.ftl / sl_jm.ftl |
| 北京 | BJ_SHB.ftl |
| 云南 | YH_SHB.ftl |
| 贵州 | JZ_SHB.ftl |
| 杨凌 | yanglinglb.ftl / yanglingmtb.ftl |

**小白易懵点**：
- ⚠️ `processMap()` 会把签名图片从FTP下载并转Base64

---

### 方法：getPictureByExtId

**一句话人话**：获取专家签名图片（和普通图片不同，用的是另一个FTP配置）

**与getPicPath的区别**：
| 对比项 | getPicPath | getPictureByExtId |
|-------|------------|-------------------|
| 用途 | 普通申报图片 | 专家签名图片 |
| FTP客户端 | SFTPUtils | FTPFileUtil（普通FTP） |

---

## 🏆 4️⃣ VipAccountmbmzServiceImpl —— 账户管理专家

**一句话解释**：管理慢病账户，包括余额查询、账户状态管理、Excel导出。

---

### 方法：export

**一句话人话**：把一堆账户信息导出成Excel表格，方便管理员查看

**参数说明**：
| 参数 | 类型 | 作用 |
|-----|------|-----|
| `list` | List<VipAccountmbmzListForViewResultDto> | 账户数据列表 |

**返回值**：`ApiResponse<FileResponseVo>`（Excel的Base64编码）

**逐步拆解**：
```java
// 1. 加载Excel模板
resourceAsStream = getClass().getClassLoader()
    .getResourceAsStream("temp/mbmz_cardstatus_report.xls");
HSSFWorkbook workBook = new HSSFWorkbook(resourceAsStream);

// 2. 遍历数据，填入Excel
for (int i = 0; i < list.size(); i++) {
    VipAccountmbmzListForViewResultDto item = list.get(i);
    HSSFRow row = sheet.createRow(i + 1);
    
    // 填姓名
    cell.setCellValue(item.getName());
    
    // 填卡号
    cell.setCellValue(item.getCardno());
    
    // 人员身份转换（代码→中文）
    if (PersonTypeEnum.RESIDENT.getValue().equals(item.getPersontype())) {
        cell.setCellValue("居民");
    } else if (PersonTypeEnum.WORKER.getValue().equals(item.getPersontype())) {
        cell.setCellValue("职工");
    }
    
    // 账户状态转换
    if (AccountStatusEnum.ACTIVE.getValue() == item.getCardstatus()) {
        cell.setCellValue("激活");
    } else if (AccountStatusEnum.FORZEN.getValue() == item.getCardstatus()) {
        cell.setCellValue("冻结");
    }
}

// 3. 转Base64返回
responseVo.setFile(FileUtils.getBase64FromInputStream(excelStream));
responseVo.setName("慢病卡状态数据导出.xls");
```

**易懵点**：
- ⚠️ `DecimalFormat` 格式化金额（保留两位小数）
- ⚠️ 枚举值转中文是在Service层做的，不是数据库

---

### 方法：exportMbmzSettlement

**一句话人话**：导出慢病结算明细，包含统筹支付、自付、大额救助等详细信息

**Excel列数**：高达35列！覆盖了完整的结算数据

**字段列表**：
- 基础信息：姓名、身份证、人员类别、性别
- 医院信息：医院编码+名称
- 就诊信息：就诊类别、账单号码、账单日期、入出院日期
- 费用明细：费用总额、起付线、统筹支付、统筹自付、大额救助支付/自付、部分自付、全自费
- 银行信息：银行编码+名称、账户名、账号
- 其他：疾病诊断、发生日期、联系电话等

---

## 🏆 5️⃣ VipDrugstoreOrderServiceImpl —— 药店订单专家

**一句话解释**：处理药店购药订单，包括订单查询、导出、打印结算单。

---

### 方法：exportDrugstoreOrderReportList

**一句话人话**：把用户在药店的购药记录导出来

**参数说明**：
| 参数 | 类型 | 作用 |
|-----|------|-----|
| `vipDrugstoreOrderResultDtoList` | List<VipDrugstoreOrderResultDto> | 订单数据列表 |

**返回值**：`ApiResponse<ExportMbdeclareInfoDto>`（Excel的Base64编码）

**逐步拆解**：
```java
// 1. 加载模板
resourceAsStream = getClass().getClassLoader()
    .getResourceAsStream("temp/onecard_drugstore_order.xls");

// 2. 遍历订单数据
for (VipDrugstoreOrderResultDto order : orderList) {
    // 订单号
    cell.setCellValue(order.getOrderno());
    // 卡号
    cell.setCellValue(order.getCardno());
    // 费用信息
    cell.setCellValue(dfMoney.format(order.getTotalmoney()));   // 费用总额
    cell.setCellValue(dfMoney.format(order.getReimbursementmoney())); // 报销金额
    cell.setCellValue(dfMoney.format(order.getReadymoney()));    // 自费金额
    // 药店
    cell.setCellValue(order.getMerchantname());
    // 退费状态
    cell.setCellValue(order.getStatus());
}
```

**易懵点**：
- ⚠️ 退费时间列只在已退款状态下才显示

---

### 方法：print / newestPrint

**一句话人话**：把结算信息生成PDF，还带水印（谁打印的、什么时候打印的）

**逐步拆解**：
```java
// 1. 获取当前打印人
ApiResponse<UpOrgUserDto> apiResponse = 
    httpForwardUtil.post("/getUser", request, null, parameterizedTypeReference);
String userName = apiResponse.getData().getUserFullname();

// 2. 用FreeMarker填充模板
Configuration cfg = new Configuration(...);
Template t = cfg.getTemplate("report.ftl");
t.process(hashMap, writer);

// 3. HTML转PDF
ITextRenderer renderer = new ITextRenderer();
renderer.createPDF(os);

// 4. 加水印（谁打印的）
String fileBase64 = PdfWatermarkUtil.pdfWatemark(in, userName);

// 5. 返回带水印的PDF
fileResponseVo.setFile(fileBase64);
```

**易懵点**：
- 🔥 水印包含打印人的名字，防止赖账
- 🔥 不同医疗类别（慢病/门诊统筹）用不同模板

---

## 🏆 6️⃣ ChronicManageServiceImpl —— 慢病管理专家

**一句话解释**：管理慢病首页的Banner图、申报指南HTML、验证码等通用功能。

---

### 方法：getBanner

**一句话人话**：从FTP下载首页轮播图

**参数说明**：
| 参数 | 类型 | 作用 |
|-----|------|-----|
| `vo` | GetBannerVo | 包含文件名 |

**返回值**：`CommonVo`（图片的Base64编码）

**逐步拆解**：
```java
// 1. 创建SFTP客户端
SFTPUtils ftpFileUtil = new SFTPUtils();

// 2. 从FTP下载图片
InputStream inputStream = ftpFileUtil.downLoadto("/mbBanner/", vo.getFileName());

// 3. 转Base64返回
String base64 = FileUtils.getBase64FromInputStream(inputStream);
commonVo.setJsonResult(base64);
```

**易懵点**：
- ⚠️ FTP路径是 `/mbBanner/`，不是其他业务用的路径

---

### 方法：getHtml

**一句话人话**：从FTP下载申报指南HTML文件

**与getBanner的区别**：
| 对比项 | getBanner | getHtml |
|-------|----------|---------|
| 文件类型 | 图片 | HTML |
| 转换方式 | Base64 | 直接读取文本 |
| 字符编码 | 二进制 | UTF-8 |

---

### 方法：jsonMobileCaptcha

**一句话人话**：生成手机验证码图片，防止机器人攻击

**参数说明**：
| 参数 | 类型 | 作用 |
|-----|------|-----|
| `vo` | JsonMobileActionVo | 包含手机号 |
| `request` | HttpServletRequest | HTTP请求（存session） |

**返回值**：`ApiResponse<CommonVo>`（验证码图片Base64）

**逐步拆解**：
```java
// 1. 创建内存图像对象
BufferedImage image = new BufferedImage(120, 40, BufferedImage.TYPE_INT_RGB);
Graphics g = image.getGraphics();

// 2. 设置背景色和字体
g.setColor(Color.WHITE);
g.fillRect(0, 0, 120, 40);
g.setFont(new Font("Times New Roman", Font.PLAIN, 24));

// 3. 生成5位随机验证码（字母+数字）
SecureRandom random = SecureRandom.getInstance("SHA1PRNG");
String characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
for (int i = 0; i < 5; i++) {
    char c = characters.charAt(random.nextInt(characters.length()));
    sb.append(c);
}
captcha = sb.toString();

// 4. 绘制验证码到图片
g.setColor(Color.BLACK);
g.drawString(captcha, 10, 30);

// 5. 绘制干扰线
for (int i = 0; i < 5; i++) {
    g.drawLine(random.nextInt(120), random.nextInt(40), 
               random.nextInt(120), random.nextInt(40));
}

// 6. 保存到Redis（1分钟过期）
redisUtil.set("Captcha:" + vo.getReceiver(), captcha, 1);

// 7. 图片转Base64
ByteArrayOutputStream bos = new ByteArrayOutputStream();
ImageIO.write(image, "JPEG", bos);
base64Image = Base64.getEncoder().encodeToString(bos.toByteArray());
```

**易懵点**：
- 🔥 验证码存在Redis而不是Session，因为前台服务是集群部署
- 🔥 验证码1分钟后自动过期

---

### 方法：JsonMobileCaptchaVerify

**一句话人话**：验证用户输入的验证码是否正确

**逐步拆解**：
```java
// 1. 从Redis获取验证码
String Captcha = (String) redisUtil.get("Captcha:" + vo.getReceiver());

// 2. 比较（忽略大小写）
String converted = vo.getCaptcha().toUpperCase();
if (!Captcha.equals(converted)) {
    return ApiResponse.fail("验证码错误");
}

// 3. 验证成功
return ApiResponse.ok("验证成功");
```

---

## 🏆 7️⃣ ZipDownloadServiceImpl —— 批量下载打包专家

**一句话解释**：把多个文件打包成ZIP下载，包括PDF审批表和图片资料。

---

### 方法：makeDir

**一句话人话**：为用户创建个人文件夹，并下载所有申报材料

**参数说明**：
| 参数 | 类型 | 作用 |
|-----|------|-----|
| `infoVo` | InfoVo | 申报ID、姓名、身份证 |
| `totalpath` | String | 总目录路径 |
| `request` | HttpServletRequest | HTTP请求 |

**逐步拆解**：
```java
// 1. 创建总目录和个人目录
String FilePath = totalpath;           // 例如：/data/export/
String path = FilePath + "/" + name + idcard;  // 例如：/data/export/张三610101199001011234

// 2. 下载PDF审批表
ApiResponse post = httpForwardUtil.post("/vipMbDeclareList/downloadBook", request, vo);
if (post成功) {
    // 调用Service生成PDF
    fileVo = vipMbdeclareFileService.makePdf(map, vo);
    // 保存到个人目录
    FileOutputStream outputStream = new FileOutputStream(path + "/门诊慢特病病种待遇认定申请表.pdf");
    outputStream.write(Base64Util.decode(fileVo.getBase()));
}

// 3. 下载图片资料
downloadDeclarePic(path, vo, request);

// 4. 合并PDF
mergePDFs(path);
```

**易懵点**：
- 🔥 先下载PDF审批表，再下载图片资料，最后合并成一个PDF
- 🔥 图片资料根据类型（证件/病历）分类存放

---

### 方法：packFilesToZip

**一句话人话**：把多个文件打包成ZIP

**逐步拆解**：
```java
try (FileOutputStream fos = new FileOutputStream(zipFile);
     ZipOutputStream zipOutputStream = new ZipOutputStream(fos)) {
    for (File file : files) {
        if (file.isDirectory()) {
            addFolderToZip(file, file.getName(), zipOutputStream);
        } else {
            addFileToZip(file, zipOutputStream);
        }
    }
}
```

---

## 🏆 8️⃣ SLExcelServiceImpl —— 商洛Excel导出专家

**一句话解释**：专门处理商洛地区的Excel导出，支持多Sheet和压缩数据。

---

### 方法：export

**一句话人话**：导出商洛慢病申报列表Excel

**参数说明**：
| 参数 | 类型 | 作用 |
|-----|------|-----|
| `queryMbDeclareListVo` | QueryMbDeclareListVo | 查询条件（包含列配置） |
| `slExcelDataByte` | byte[] | GZIP压缩的数据 |
| `response` | HttpServletResponse | HTTP响应（直接写流） |
| `request` | HttpServletRequest | HTTP请求 |

**逐步拆解**：
```java
// 1. 获取当前用户（加水印用）
ApiResponse<UpOrgUserDto> apiResponse = httpForwardUtil.post("/getUser", ...);
String userName = apiResponse.getData().getUserFullname();

// 2. 解压数据（GZIP压缩的List）
List<List<SLExcelData>> slExcelDataList = uncompressList(slExcelDataByte);

// 3. 加载模板
resourceAsStream = getClass().getClassLoader()
    .getResourceAsStream("temp/mbmz_declareInfo_sl.xlsx");
workBook = new XSSFWorkbook(resourceAsStream);

// 4. 根据数据量创建多个Sheet
for (int s = 0; s < slExcelDataListSize - 1; s++) {
    workBook.cloneSheet(0);  // 复制第一个Sheet
}

// 5. 使用EasyExcel写入数据（支持模板填充）
ExcelWriter excelWriter = EasyExcel.write(response.getOutputStream())
    .includeColumnFieldNames(includeColumns)  // 只包含指定的列
    .withTemplate(fileNameTemp)              // 使用模板
    .registerWriteHandler(new CustomWaterMarkHandler(watermark))  // 加水印
    .inMemory(true)
    .build();
```

**易懵点**：
- 🔥 数据是GZIP压缩传输的，因为数据量大
- 🔥 支持自定义导出列（`includeColumns`）
- 🔥 多Sheet模板，每个Sheet放一部分数据

---

## 🏆 9️⃣ YaExcelServiceImpl —— 延安Excel导出专家

**一句话解释**：专门处理延安地区的Excel导出，支持数据脱敏。

---

### 方法：drugExport

**一句话人话**：导出延安用药目录Excel

**逐步拆解**：
```java
// 1. 数据脱敏（AES加密的字段解密）
for (VipDrugDirectoryYaDto datum : data) {
    datum.setIdcard(AesUtil.getDecryptedValue(datum.getIdcard()));
    datum.setName(AesUtil.getDecryptedValue(datum.getName()));
}

// 2. DTO转换
List<YaDrugExportDto> drugExports = data.stream().map(dto -> {
    YaDrugExportDto exportDto = new YaDrugExportDto();
    BeanUtil.copyProperties(dto, exportDto, true);
    return exportDto;
}).collect(Collectors.toList());

// 3. 导出Excel
ExcelUtil excelUtil = new ExcelUtil();
return ApiResponse.ok(excelUtil.exportExcel("用药目录列表.xlsx", "temp/ya_drug.xlsx", drugExports));
```

**易懵点**：
- 🔥 身份证和姓名是AES加密存储的，导出时需要解密
- 🔥 使用 `BeanUtil.copyProperties` 进行DTO转换

---

## 🏆 🔟 BJMedicalInsuranceServiceImpl —— 北京医保资格校验专家

**一句话解释**：调用北京医保系统验证用户资格。

---

### 方法：VIPQueryChronicBalance

**一句话人话**：去北京医保系统查查这个人有没有参保资格

**参数说明**：
| 参数 | 类型 | 作用 |
|-----|------|-----|
| `vo` | CheckBalanceVo | 身份证号和就诊类型 |

**返回值**：`CommonVo`（包含人员类型：职工/居民，参保单位）

**逐步拆解**：
```java
// 1. 构造医保查询请求
JSONObject inJson = new JSONObject();
inJson.put("AKB020", code);              // 医疗机构编码
inJson.put("AAC002", vo.getIdcard());    // 身份证号
inJson.put("AKA130", vo.getVisitkind()); // 就诊类型

// 2. 调用医保接口（1001接口）
LinkRuturnEntity responseJson = callBJ1001(inJson);

// 3. 解析返回结果
JSONObject transferinfo = (JSONObject) responseJson.getData();
JSONObject head = transferinfo.getJSONObject("headinfo");

if ("1".equals(head.getString("ERRCODE"))) {
    // 查询成功
    JSONObject row = data1.getJSONObject("row");
    String name = row.getString("AAC003");  // 姓名
    
    // 姓名匹配验证
    if (vo.getName().equals(name)) {
        messageVo.setPlanttype("3".equals(row.getString("AAE140")) ? "职工" : "居民");
        messageVo.setOrganization(row.getString("AAB004")); // 参保单位
    }
}
```

**医保字段说明**：
| 字段 | 含义 |
|-----|------|
| AKB020 | 医疗机构编码 |
| AAC002 | 身份证号 |
| AAC003 | 姓名 |
| AAE140 | 险种类型（3=职工，其他=居民） |
| AAB004 | 参保单位名称 |
| AKA130 | 就诊类型 |

---

## 🏆 1️⃣1️⃣ CallJkscServiceImpl —— 小程序认证加密专家

**一句话解释**：处理健康商城小程序的认证请求，使用SM2国密加密。

---

### 方法：getJkscListing

**一句话人话**：给健康商城的请求数据加密，防止泄露用户隐私

**参数说明**：
| 参数 | 类型 | 作用 |
|-----|------|-----|
| `vo` | CallJkscVo | 包含手机号、OpenId |

**返回值**：`CallJkscVo`（加密后的请求数据）

**逐步拆解**：
```java
// 1. 如果有手机号，先加密手机号
if (StringUtils.isNotBlank(phone)) {
    String encryptedPhone = this.encryptData(phone, phonekey);
    // 例如：手机号 13800138000 加密后变成一串乱码
}

// 2. 构造请求JSON
JSONObject jsonObject = new JSONObject();
jsonObject.put("openId", vo.getOpenId());
jsonObject.put("userSource", userSource);      // 固定值：135
jsonObject.put("channelCode", channelCode);    // 固定值：1016
jsonObject.put("phone", encryptedPhone);       // 加密后的手机号

// 3. 再次加密整个请求
String info = this.encryptData(jsonObject.toString(), infokey);

// 4. 设置到返回对象
vo.setInfo(info);
```

**加密流程图**：
```
原始数据：
{
    "openId": "xxx",
    "phone": "13800138000"
}

↓ 第一步：用手机号密钥加密phone
{
    "openId": "xxx",
    "phone": "encrypted_13800138000"
}

↓ 第二步：用信息密钥加密整个JSON
info = "encrypted_{...整个JSON...}"
```

---

### 方法：encryptData

**一句话人话**：使用SM2国密算法加密数据

**逐步拆解**：
```java
public String encryptData(String data, String publicKey) {
    // 1. 创建SM2加密器
    SM2 sm2 = SmUtil.sm2(
        ECKeyUtil.toSm2PrivateParams(HexUtil.decodeHex(PRIVATE_KEY)),  // 私钥
        ECKeyUtil.toSm2PublicParams(HexUtil.decodeHex(publicKey))      // 公钥
    );
    
    // 2. 用公钥加密
    return sm2.encryptBcd(data, KeyType.PublicKey);
}
```

**小白易懵点**：
- 🔥 SM2是中国国家密码管理局发布的国密算法
- 🔥 使用椭圆曲线密码体系，比RSA更安全
- 🔥 私钥存在配置中，公钥由对方提供

---

## 🏆 1️⃣2️⃣ VipMbsbserviceImpl —— 慢病备案信息同步专家

**一句话解释**：通过WebService接口同步慢病人员备案信息到医保系统。

---

### 方法：MBinfo

**一句话人话**：接收医保系统的XML报文，处理后转发给后厨

**参数说明**：
| 参数 | 类型 | 作用 |
|-----|------|-----|
| `xmlData` | String | XML格式的备案请求 |

**返回值**：`String`（XML格式的响应）

**逐步拆解**：
```java
@Override
public String MBinfo(String xmlData) {
    try {
        // 转发到后厨的REST接口
        String url = "/rest/vipMbsb/mbinfo";
        return HmLinkWebserviceBL.runComWebsToRef(xmlData, url);
    } catch (Exception e) {
        log.error("MBinfo", e);
    }
    return null;
}
```

**小白易懵点**：
- ⚠️ 这是WebService接口，用XML格式通信，不是JSON
- ⚠️ `HmLinkWebserviceBL` 是webservice工具类

---

# Part 4：HTTP转发机制深度解析

## 🔄 HttpForwardUtil —— 前台服务的"电话总机"

**一句话解释**：HttpForwardUtil是前台服务连接业务服务的核心工具，相当于酒店的总机小姐。

### 核心方法解析

---

### post方法（最常用）

**使用场景**：POST请求转发，带Token认证

```java
public <T> T post(String url, HttpServletRequest request, Object requestVo, Class<T> clazz) {
    // 1. 从原请求中提取所有Header（重点是Token）
    HttpHeaders headers = getHttpHeaders(request);
    
    // 2. 构造HTTP请求
    HttpEntity requestEntity = new HttpEntity(requestVo, headers);
    
    // 3. 发送到业务服务
    ResponseEntity<T> responseEntity = restTemplate.exchange(
        prefix + url,           // 例如：http://业务服务:9091/mb/queryBalance
        HttpMethod.POST, 
        requestEntity, 
        clazz
    );
    
    // 4. 返回响应
    return responseEntity.getBody();
}
```

**Token传递机制**：
```
用户请求（带Token）
    ↓
前台Controller收到请求
    ↓
调用 httpForwardUtil.post("/mb/query", request, vo)
    ↓
HttpForwardUtil.getHttpHeaders(request) 提取原请求的Header
    ↓（包括：Authorization: Bearer xxx_token）
HTTP POST 到业务服务（Header原封不动传递）
    ↓
业务服务校验Token并处理
    ↓
返回结果给前台
    ↓
前台返回给用户
```

---

### post方法（支持自定义Header）

**使用场景**：专家端访问链接中没有Token，需要手动添加

```java
public <T> T post(String url, HttpServletRequest request, Object requestVo,
                  ParameterizedTypeReference<T> parameterizedTypeReference,
                  MultiValueMap<String,String> header) {
    // 1. 用传入的header替代原请求的header
    HttpEntity requestEntity = new HttpEntity(requestVo, header);
    
    // 2. 发送到业务服务
    ResponseEntity<T> responseEntity = restTemplate.exchange(
        prefix + url, 
        HttpMethod.POST, 
        requestEntity, 
        parameterizedTypeReference
    );
    
    return responseEntity.getBody();
}
```

**应用场景**：
```java
// 专家端URL中的Token是加密的，需要解密后添加Header
MultiValueMap<String, String> header = new LinkedMultiValueMap<>();
String token = request.getParameter("token");
token = decrypt(token).replaceAll(" ", "+");  // RSA解密
header.add("token", token);

// 调用
httpForwardUtil.post(url, request, vo, parameterizedTypeReference, header);
```

---

### post方法（文件上传）

**使用场景**：form-data格式的文件上传

```java
public <T> T post(String url, HttpServletRequest request,
                  ParameterizedTypeReference<T> parameterizedTypeReference, 
                  Map<String, Object> requestVo) {
    // 1. 提取文件
    Map<String, MultipartFile> fileMap = req.getFileMap();
    
    // 2. 构造form-data
    MultiValueMap<String, Object> map = new LinkedMultiValueMap<>();
    for (String key : fileMap.keySet()) {
        MultipartFile file = fileMap.get(key);
        // 转成临时文件
        File tempFile = new File(tempFilePath);
        file.transferTo(tempFile);
        // 添加到表单
        map.add(key, new FileSystemResource(tempFile));
    }
    
    // 3. 发送
    HttpEntity<MultiValueMap<String, Object>> requestEntity = 
        new HttpEntity<>(map, headers);
    ResponseEntity<T> responseEntity = restTemplate.exchange(...);
    
    // 4. 删除临时文件
    tempFile.delete();
}
```

---

### getHttpHeaders方法（Header提取）

**一句话解释**：把原请求的所有Header原封不动复制到新请求

```java
private HttpHeaders getHttpHeaders(HttpServletRequest request) {
    HttpHeaders headers = new HttpHeaders();
    Enumeration<String> names = request.getHeaderNames();
    while (names.hasMoreElements()) {
        String name = names.nextElement();
        headers.add(name, request.getHeader(name));
    }
    return headers;
}
```

**重点提取的Header**：
| Header | 作用 |
|--------|------|
| `Authorization` | 用户Token认证 |
| `Content-Type` | 请求内容类型 |
| `User-Agent` | 用户代理信息 |

---

# Part 5：FTP文件操作机制

## 📁 SFTPUtils —— 安全文件传输工具

**一句话解释**：SFTPUtils是前台服务操作FTP/SFTP服务器的"文件管理员"。

### 核心方法

---

### createFile（上传）

```java
public boolean createFile(String path, InputStream inputStream, String fileName) {
    // 1. 连接SFTP服务器
    connect();
    
    // 2. 确保目录存在
    String[] dirs = path.split("/");
    String currentPath = "";
    for (String dir : dirs) {
        if (!dir.isEmpty()) {
            currentPath += "/" + dir;
            try {
                sftp.cd(currentPath);
            } catch (SftpException e) {
                sftp.mkdir(currentPath);  // 不存在则创建
            }
        }
    }
    
    // 3. 上传文件
    sftp.put(inputStream, fileName);
    
    return true;
}
```

---

### downLoadto（下载）

```java
public InputStream downLoadto(String path, String fileName) {
    // 1. 连接SFTP服务器
    connect();
    
    // 2. 进入目录
    sftp.cd(path);
    
    // 3. 下载文件到输入流
    InputStream inputStream = sftp.get(fileName);
    
    return inputStream;
}
```

---

### 两种FTP客户端的区别

| 客户端 | 用途 | 服务器 |
|--------|------|--------|
| `SFTPUtils` | 普通业务文件 | SFTP服务器A |
| `SFTPUtils_xcx` | 小程序相关文件 | SFTP服务器B（小程序专用） |

---

# Part 6：PDF生成机制

## 📄 FreeMarker + iText 组合拳

**一句话解释**：用FreeMarker模板引擎填充数据，然后用iText把HTML转成PDF。

### 流程图

```
数据对象（Java）
    ↓ JSON序列化
JSON字符串
    ↓ JsonUtil.parseJSON2Map
Map<String, Object>
    ↓ FreeMarker模板引擎
HTML字符串（含占位符替换后的数据）
    ↓ iText渲染器
PDF二进制
    ↓ Base64编码
Base64字符串 → 返回前端
```

### 模板文件位置

```
resources/
├── templates/          # FreeMarker模板
│   ├── zg.ftl         # 职工审批表
│   ├── lb.ftl         # 两病审批表
│   ├── mtb.ftl        # 慢特病审批表
│   ├── sl_zg.ftl      # 商洛职工
│   ├── sl_jm.ftl      # 商洛居民
│   ├── BJ_SHB.ftl     # 北京审批表
│   ├── YH_SHB.ftl     # 云南审批表
│   ├── JZ_SHB.ftl     # 贵州审批表
│   └── report.ftl     # 结算单
├── temp/              # Excel模板
│   ├── mbAuditForm.xls
│   └── mbmz_cardstatus_report.xls
└── config/            # 字体文件
    └── simsun.ttc    # 宋体（PDF中文字体）
```

### 模板语法示例

```freemarker
<!-- sl_zg.ftl (商洛职工审批表) -->
<html>
<body>
    <h1>商洛市慢性病门诊医疗待遇审批表</h1>
    <table>
        <tr>
            <td>姓名：${name}</td>
            <td>性别：${sex}</td>
        </tr>
        <tr>
            <td>身份证号：${idcard}</td>
            <td>单位：${workunit}</td>
        </tr>
        <tr>
            <td>申报病种：${icdname}</td>
        </tr>
    </table>
    <!-- 签名图片 -->
    <img src="${expertSignature}" />
</body>
</html>
```

---

# Part 7：Redis缓存机制

## 🚀 验证码存储

**一句话解释**：用Redis存储验证码，实现分布式Session。

### 存储结构

```
Key: Captcha:13800138000
Value: A7K9M
TTL: 60秒
```

### 操作流程

```java
// 1. 生成验证码
String captcha = generateCaptcha();
redisUtil.set("Captcha:" + phone, captcha, 1);  // 1分钟过期

// 2. 验证验证码
String storedCaptcha = (String) redisUtil.get("Captcha:" + phone);
if (storedCaptcha.equals(inputCaptcha)) {
    // 验证通过
}
```

---

# Part 8：加密解密机制

## 🔐 AES加密（数据脱敏）

**使用场景**：数据库中存储的敏感字段（身份证、姓名）用AES加密

```java
// 加密
String encrypted = AesUtil.getEncryptedValue("610101199001011234");

// 解密
String decrypted = AesUtil.getDecryptedValue(encrypted);
```

## 🔐 SM2国密（接口加密）

**使用场景**：与健康商城小程序的通信加密

```java
// 加密
SM2 sm2 = SmUtil.sm2(privateKey, publicKey);
String encrypted = sm2.encryptBcd(data, KeyType.PublicKey);

// 解密
String decrypted = sm2.decryptStr(encrypted, KeyType.PrivateKey);
```

## 🔐 RSA加密（专家Token）

**使用场景**：专家端URL中的Token用RSA加密

```java
// 解密
String decrypted = decrypt(encryptedToken);
```

---

# Part 9：常见问题速查

## ❓ Q1: 为什么前台服务不用MyBatis？

**A**: 前台服务是"中介"，只负责转发请求，不直接操作数据库。真正的数据操作在业务服务（后厨）中完成。

## ❓ Q2: Token是怎么传递的？

**A**: 通过`HttpForwardUtil.getHttpHeaders(request)`提取原请求的所有Header，包括`Authorization: Bearer xxx`，然后原封不动地传递到业务服务。

## ❓ Q3: 文件上传为什么要存FTP而不是数据库？

**A**: 
1. 数据库不适合存储大量二进制文件
2. FTP可以跨服务器共享
3. 方便CDN加速访问

## ❓ Q4: 为什么要用GZIP压缩数据传输？

**A**: 商洛地区的申报数据量很大，GZIP压缩可以减少网络传输时间。

## ❓ Q5: 为什么用Redis存验证码而不是Session？

**A**: 前台服务是集群部署，多台服务器共享Session需要额外配置。Redis是天然的分布式缓存，所有服务器都能访问。

---

# Part 10：附录

## 📊 枚举值速查表

### 人员身份 (PersonTypeEnum)
| 值 | 含义 |
|----|------|
| `3` | 职工 |
| 其他 | 居民 |

### 账户状态 (AccountStatusEnum)
| 值 | 含义 |
|----|------|
| `0` | 新建 |
| `1` | 待激活 |
| `2` | 激活 |
| `3` | 冻结 |
| `4` | 作废 |

### 文件类型 (FileTypeEnum)
| 值 | 含义 |
|----|------|
| `1` | 证件照 |
| `2` | 体检报告 |
| `3` | 专家签名 |
| `4` | 理赔资料 |

### 病种类型 (IcdTypeEnum)
| 值 | 含义 |
|----|------|
| `1` | 七种病 |
| `2` | 十种病 |
| `3` | 两病（高血压/糖尿病） |

---

**文档版本**：1.0  
**生成日期**：2024年  
**维护者**：PICC技术团队
