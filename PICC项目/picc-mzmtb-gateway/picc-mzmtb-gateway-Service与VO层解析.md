# PICC门诊慢特病前台服务（picc-mzmtb-gateway）

## Service层与VO层深度解析

> 📖 **阅读指南**：本文档专为"零基础小白"设计，用最通俗的语言+生动的比喻，带你彻底搞懂这个项目的数据层架构。即使你刚学Java三天，也能看懂！

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

# Part 2：Service层全解析

## 📊 Service文件大盘点

项目共有 **32个Service文件**，分布在以下位置：

```
src/main/java/com/picchealth/module/mb/service/
├── impl/                    # Service实现类
│   ├── VipMbDeclareServiceImpl.java      ⭐ 申报相关（PDF导出）
│   ├── VipMbdeclareInfoServiceImpl.java   ⭐ 申报信息（图片处理）
│   ├── VipMbdeclareFileServiceImpl.java   ⭐ 申报文件（FTP操作）
│   ├── VipAccountmbmzServiceImpl.java    ⭐ 账户管理（Excel导出）
│   ├── VipDrugstoreOrderServiceImpl.java ⭐ 药店订单（报表打印）
│   ├── ChronicManageServiceImpl.java      ⭐ 慢病管理（Banner图、验证码）
│   ├── ZipDownloadServiceImpl.java        ⭐ 批量下载（打包ZIP）
│   └── ...其他Service
└── 接口文件（xxxService.java）
```

---

## 🏆 核心Service深度拆解

### 1️⃣ VipMbDeclareServiceImpl —— 申报审核表下载专家

**一句话解释**：这个Service专门负责把慢病审核表做成Excel和PDF格式下载。

#### 核心方法解析

---

##### 📥 `downLoad()` —— 下载慢病审核表Excel

```
人话版：帮用户下载一份"慢性病门诊医疗审批表"Excel文件
```

**参数**：
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
HSSFCell cell11 = row1.getCell(1);
cell11.setCellValue(vipMbdeclareInfo.getName());  // 填姓名
cell13.setCellValue("0".equals(vipMbdeclareInfo.getSex()) ? "男" : "女"); // 填性别
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

##### 📄 `exportPdfData()` —— 导出审批表PDF

```
人话版：根据人员身份（职工/居民）和病种类型（慢病/两病）生成不同的PDF
```

**判断逻辑**：
```
                    ┌─ 职工 ──→ "zg.ftl"模板
人员身份 ───────────┤
                    └─ 居民 ──┬─ 两病(icdkind=3 && icdtype=3) ──→ "lb.ftl"
                              └─ 慢特病 ──→ "mtb.ftl"
```

**逐步拆解**：
```java
// 1. 根据人员身份选模板
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

// 2. 把数据塞进FreeMarker模板
Configuration cfg = new Configuration(Configuration.VERSION_2_3_23);
cfg.setDirectoryForTemplateLoading(new File(path));
Template t = cfg.getTemplate(ftlPath);
t.process(hashMap, writer);

// 3. 用iTextRenderer把HTML转PDF
ITextRenderer renderer = new ITextRenderer();
renderer.setDocumentFromString(writer.toString());
renderer.createPDF(os);

// 4. 把PDF转Base64返回
String fileBase64 = FileUtils.getBase64FromInputStream(in);
```

**易懵点**：
- 🔥 FTP上的签名图片URL需要下载转Base64再塞进模板
- 🔥 `processMap()` 方法专门处理签名图片

---

### 2️⃣ VipMbdeclareInfoServiceImpl —— 申报信息处理专家

**一句话解释**：处理申报信息的图片上传、编辑，以及医保资格校验。

#### 核心方法解析

---

##### 🖼️ `editImage()` —— 编辑申报图片

```
人话版：用户上传了图片，前台帮你存到FTP服务器，然后通知后厨更新数据库
```

**参数**：
```java
EditImagesVo editImagesVo  // 包含图片列表和申报ID
HttpServletRequest request
String url                // 后厨的接口地址
```

**逐步拆解**：
```java
// 1. 遍历每张图片
for (EditImageVo image : editImagesVo.getImages()) {
    // 2. Base64解码
    byte[] imageByte = new BASE64Decoder().decodeBuffer(image.getContent());
    
    // 3. 生成唯一文件名（UUID）
    String fileName = UUID.randomUUID() + ".jpg";
    
    // 4. 上传到FTP
    SFTPUtils ftpFileUtil = new SFTPUtils();
    ftpFileUtil.createFile(urlpath, inputStream, fileName);
    
    // 5. 把FTP路径更新到图片对象
    image.setContent(urlpath + fileName);
}

// 6. 转发给后厨更新数据库
return httpForwardUtil.post(url, request, editImagesVo, ApiResponse.class);
```

**调用链**：
```
用户上传图片 → 前台Service处理图片 → 上传FTP → 
转发给后厨(/mb/editImage) → 后厨更新数据库
```

---

##### 💰 `VIPQueryChronicBalance()` —— 查询医保慢病余额

```
人话版：去医保系统查查这个人还有多少慢病额度可以用
```

**逐步拆解**：
```java
// 1. 构造医保查询请求
JSONObject inJson = new JSONObject();
inJson.put("AKB020", code);              // 医疗机构编码
inJson.put("AAC002", vo.getIdcard());    // 身份证号
inJson.put("AKA130", vo.getVisitkind()); // 就诊类型

// 2. 调用医保接口（调用北京接口1001）
LinkRuturnEntity responseJson = callBJ1001(inJson);

// 3. 解析返回结果
if (responseJson.getSuccess()) {
    YBMessageVo messageVo = new YBMessageVo();
    messageVo.setPlanttype("职工");  // 或"居民"
    messageVo.setOrganization("xxx医院");
}

// 4. 返回给用户
return ApiResponse.ok(messageVo);
```

**易懵点**：
- ⚠️ 这里是真正的外部系统调用，不是走后厨HTTP
- ⚠️ `callBJ1001()` 封装了医保系统的XML报文格式

---

##### 📄 `credentialsSL()` / `credentialsBJ()` / `credentialsYH()` —— 生成审批表PDF

```
人话版：生成不同城市的审批表（商洛/北京/云南）
```

**区别**：
| 方法 | 城市 | 模板文件 |
|-----|------|---------|
| `credentialsSL()` | 商洛 | sl_zg.ftl（职工）/ sl_jm.ftl（居民） |
| `credentialsBJ()` | 北京 | BJ_SHB.ftl |
| `credentialsYH()` | 云南 | YH_SHB.ftl |

---

### 3️⃣ VipMbdeclareFileServiceImpl —— 申报文件处理专家

**一句话解释**：处理申报相关的文件（图片、PDF），负责从FTP读取、转换格式、生成审批表。

#### 核心方法解析

---

##### 🖼️ `getPicPath()` —— 获取申报图片

```
人话版：从FTP下载申报相关的图片（证件照、病历等）
```

**逐步拆解**：
```java
// 1. 先问后厨拿文件元数据
ApiResponse<VipMbdeclareFile> response = 
    httpForwardUtil.post(url, request, vo, parameterizedTypeReference);

VipMbdeclareFile vipMbdeclareFile = response.getData();

// 2. 根据文件类型选择不同的FTP配置
if (filetype == FileTypeEnum.FILETYPE_PHYSICALREPORT) {
    // 体检报告 → 用SFTPUtils下载
} else if (filetype == FileTypeEnum.FILETYPE_PRESCRIPTION) {
    // 理赔资料 → 用SFTPUtils_xcx下载
} else {
    // 普通申报资料 → 用SFTPUtils下载
}

// 3. 从FTP下载图片并转Base64
SFTPUtils ftpFileUtil = new SFTPUtils();
InputStream inputStream = ftpFileUtil.downLoadto(filepath, filename);
String imageStr = FTPFileUtil.getBase64FromInputStream(inputStream);

// 4. 返回给前端
return ApiResponse.ok(imageByte);
```

---

##### 📦 `getPictureByExtId()` —— 获取专家签名图片

```
人话版：专门下载专家签名图片（和普通图片不同，用的是另一个FTP配置）
```

**调用链**：
```
Controller → Service → HTTP转发给后厨 → 后厨查DB返回文件信息 → 
Service从FTP下载 → 转Base64 → 返回前端
```

---

### 4️⃣ VipAccountmbmzServiceImpl —— 账户管理专家

**一句话解释**：管理慢病账户，包括余额查询、账户状态管理、Excel导出。

#### 核心方法解析

---

##### 📊 `export()` —— 导出慢病卡状态报表

```
人话版：把一堆账户信息导出成Excel表格，方便管理员查看
```

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

##### 💰 `exportMbmzSettlement()` —— 导出结算明细

```
人话版：导出慢病结算明细，包含统筹支付、自付、大额救助等详细信息
```

**Excel列数**：高达35列！覆盖了完整的结算数据：
- 姓名、身份证、人员类别
- 医院信息（编码+名称）
- 费用明细（总额、起付线、统筹、大额救助等）
- 银行信息（账号、开户行）

---

### 5️⃣ VipDrugstoreOrderServiceImpl —— 药店订单专家

**一句话解释**：处理药店购药订单，包括订单查询、导出、打印结算单。

#### 核心方法解析

---

##### 📥 `exportDrugstoreOrderReportList()` —— 导出药店订单Excel

```
人话版：把用户在药店的购药记录导出来
```

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

---

##### 🖨️ `print()` / `newestPrint()` —— 打印结算单

```
人话版：把结算信息生成PDF，还带水印（谁打印的、什么时候打印的）
```

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

### 6️⃣ ChronicManageServiceImpl —— 慢病管理专家

**一句话解释**：管理慢病首页的Banner图、申报指南HTML、验证码等通用功能。

#### 核心方法解析

---

##### 🖼️ `getBanner()` —— 获取Banner图

```
人话版：从FTP下载首页轮播图
```

```java
// 1. 从FTP下载图片
SFTPUtils ftpFileUtil = new SFTPUtils();
InputStream inputStream = ftpFileUtil.downLoadto("/mbBanner/", vo.getFileName());

// 2. 转Base64返回
String base64 = FileUtils.getBase64FromInputStream(inputStream);
commonVo.setJsonResult(base64);
```

---

##### 📝 `getHtml()` —— 获取申报指南HTML

```
人话版：下载申报指南的HTML内容（不是图片哦！）
```

```java
// 用BufferedReader一行行读HTML
BufferedReader br = new BufferedReader(new InputStreamReader(inputStream, "UTF-8"));
StringBuilder sb = new StringBuilder();
while ((line = br.readLine()) != null) {
    sb.append(line);
}
commonVo.setJsonResult(sb.toString());
```

---

##### 🔐 `jsonMobileCaptcha()` / `JsonMobileCaptchaVerify()` —— 短信验证码

```
人话版：生成图片验证码 + 发送短信验证码 + 验证
```

**流程**：
```
1. 生成随机验证码（5位字母数字）
2. 画到图片上（加干扰线防机器识别）
3. 图片转Base64返回给前端
4. 验证码存Redis，过期时间1分钟
5. 用户提交短信验证码时，从Redis比对
```

```java
// 生成验证码
SecureRandom random = SecureRandom.getInstance("SHA1PRNG");
for (int i = 0; i < 5; i++) {
    captcha += characters.charAt(random.nextInt(characters.length()));
}

// 存Redis，1分钟过期
redisUtil.set("Captcha:" + phone, captcha, 1);

// 画图
BufferedImage image = new BufferedImage(120, 40, BufferedImage.TYPE_INT_RGB);
g.drawString(captcha, 10, 30);
for (int i = 0; i < 5; i++) {
    g.drawLine(random.nextInt(120), random.nextInt(40), ...); // 干扰线
}
```

---

### 7️⃣ ZipDownloadServiceImpl —— 批量下载打包专家

**一句话解释**：把申报材料（申请表PDF + 证件照 + 病历图）打包成ZIP下载。

#### 核心方法解析

---

##### 📦 `makeDir()` + `packFilesToZip()` —— 打包下载

```
人话版：把一个人的所有申报材料打包成ZIP
```

**打包内容**：
```
张三申报材料.zip
├── 门诊慢特病病种待遇认定申请表.pdf   ← 生成的审批表
├── 影像资料.pdf                       ← 证件照+病历合并的PDF
└── [如果有]体检报告.pdf
```

**逐步拆解**：
```java
// 1. 创建目录
File personalDir = new File(totalPath + "/" + name + idcard);
personalDir.mkdirs();

// 2. 生成审批表PDF
ApiResponse post = httpForwardUtil.post("/downloadBook", request, vo, ...);
fileVo = vipMbdeclareFileService.makePdf(map, vo);

// 3. 下载证件照+病历图，转PDF合并
downloadDeclarePic(path, vo, request, ...);

// 4. 合并多个PDF成一个
mergePDFs(path);

// 5. 打包ZIP
packFilesToZip(files, zipFile);
```

---

##### 🔗 `mergePDFs()` —— 合并PDF

```java
// 用PDFBox合并两个PDF
PDFMergerUtility merger = new PDFMergerUtility();
merger.setDestinationFileName(output);
merger.addSource(new File(input2));  // 申请表
merger.addSource(new File(input1));  // 影像资料
merger.mergeDocuments();
```

---

# Part 3：VO层全解析

## 📊 VO大盘点

项目共有 **361个VO文件**，按模块分类：

```
src/main/java/com/picchealth/module/mb/vo/         ← 核心业务VO (21个)
src/main/java/com/picchealth/module/mb/third/vo/   ← 第三方接口VO (53个)
src/main/java/com/picchealth/module/restful/vo/   ← 外部接口VO (29个)
```

---

## 🎯 VO是什么？

**VO = Value Object（值对象）**

```
大白话：VO就是一个"数据包装盒"

┌─────────────────────────────────────┐
│           MbDeclareVo               │
│  ┌─────────────────────────────┐   │
│  │ userId: "用户ID"            │   │
│  │ vipMbdeclareInfo: {...}     │   │
│  │ hoscode: "医院编码"          │   │
│  │ files: ["图片1", "图片2"]    │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## 📁 VO分类详解

### 1️⃣ 申报相关VO

| VO类名 | 用途 | 关键字段 |
|-------|------|---------|
| `MbDeclareVo` | 申报主VO | userId, vipMbdeclareInfo, hoscode, files |
| `VipMbDeclareInfoVo` | 申报信息 | declareid, physicalid, taskId |
| `UpdateVipMbdeclareInfoVo` | 更新申报 | 所有可修改的申报字段 |
| `SelectVipMbdeclareInfoVo` | 查询申报 | ids, reviewId, taskIds |
| `QueryMbInfoVo` | 查询申报列表 | mobile, idcard, name, declareStatus等 |

**MbDeclareVo 详解**：
```java
@Data
public class MbDeclareVo {
    private String userId;                    // 用户ID
    private VipMbdeclareInfo vipMbdeclareInfo; // 申报核心信息（姓名、身份证、病种）
    private String hoscode;                  // 定点医院编码
    private String hosname;                  // 定点医院名称
    private List<String> files;              // 处方图片列表
    private String mdtrtareaAdmvs;           // 就医地医保区划
    private String insuplcAdmdvs;             // 参保地医保区划
    private String psnNo;                     // 医保平台的人员编号
}
```

---

### 2️⃣ 账户相关VO

| VO类名 | 用途 | 关键字段 |
|-------|------|---------|
| `QueryAccountInfoVo` | 查询账户 | name, idCard, mobile, cardNo, flag |
| `VipInfoAccountVo` | 账户信息 | balance, cardStatus, icdType |
| `UpdateVipAccountMbmzVo` | 更新账户 | 可修改的账户字段 |

---

### 3️⃣ 结算相关VO

| VO类名 | 用途 | 关键字段 |
|-------|------|---------|
| `MbmzSettlementVo` | 结算明细 | 35个字段（费用、支付、银行信息等） |
| `QueryMbSettlementVo` | 查询结算 | startDate, endDate |

**MbmzSettlementVo 字段分类**：
```
基本信息：name, idcard, sex, mobile
地点信息：province, city, county
医院信息：hoscode, hosname
病种信息：icdcode, icdname
费用信息：totalmoney, startmoney, tcmoney, realmoney
银行信息：bankcode, bankname, bankaccount
```

---

### 4️⃣ 文件相关VO

| VO类名 | 用途 | 关键字段 |
|-------|------|---------|
| `ImageFileVo` | 图片文件 | base(Base64), userId, name, filetype |
| `EditImagesVo` | 编辑图片 | declareid, images, filetype |
| `EditImageVo` | 单张图片 | content(Base64) |
| `FileResponseVo` | 文件响应 | file(Base64), name |
| `QueryFilePathVo` | 查询文件路径 | fileId |

**ImageFileVo 详解**：
```java
@Data
public class ImageFileVo {
    private String base;           // Base64编码的图片内容
    private String userId;        // 用户ID
    private int filetype;          // 图片类型（101等）
    private String name;          // 文件名
    private String icdkind;       // 病种类型
    private Date generationtime;   // 生成时间
    private String JPGbase;       // JPG格式的Base64
    private String credentialsid;  // 凭证表ID
}
```

---

### 5️⃣ 外部接口VO（causacloud）

这是与"因数云"平台对接的VO：

```java
// CausacloudApplyServiceVo.java
@Data
public class CausacloudApplyServiceVo {
    private String userid;    // 用户ID
    private String planid;    // 计划名称
    private String batchno;   // 流水号
    private String partner;   // 渠道名称
}

// CausacloudUserInfoVo.java
@Data
public class CausacloudUserInfoVo {
    private String name;
    private String idCard;
    private String mobile;
    private String city;
    // ... 其他用户信息
}
```

---

## 🏗️ Request VO vs Response VO

### 命名规则

```
Request VO：通常以 "Query" / "Update" / "Save" / "Add" 开头
Response VO：通常以 "Vo" / "Result" / "Info" 结尾
```

### 举例

| 场景 | Request VO | Response VO |
|-----|-----------|-------------|
| 查询申报 | `QueryMbInfoVo` | 直接返回 `List<VipMbdeclareInfo>` |
| 查询账户 | `QueryAccountInfoVo` | `VipInfoAccountVo` |
| 上传图片 | `EditImagesVo` | `ApiResponse` |
| 导出Excel | 无（直接用List） | `FileResponseVo` |

---

## 🤔 为什么不叫DTO？

**DTO（Data Transfer Object）** 和 **VO** 经常被混用，但有细微区别：

```
DTO：数据传输对象，更偏向"传输"
VO：值对象，更偏向"展示"

在这个项目里：
- VO = 前后端交互的数据格式
- DTO = Service内部流转的数据格式
```

---

# Part 4：API→Service→HTTP转发调用链

## 🔗 典型调用链路图

### 场景1：下载慢病审核表

```
用户点击"下载审核表"
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  Controller: VipMbDeclareServiceApi                             │
│  @GetMapping("/download/{id}")                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 1. 构造IdVo {id: "123456"}                                  ││
│  │ 2. 调用 httpForwardUtil.post("/mb/auditform/query", ...)    ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
        │
        │  HTTP POST → 业务服务 (9091端口)
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  业务服务 /mb/auditform/query                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 查数据库: SELECT * FROM vip_mbdeclare_info WHERE id=?      ││
│  │ 返回: VipMbdeclareInfo对象                                  ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
        │
        │  返回 VipMbdeclareInfo
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  Service: VipMbDeclareServiceImpl.downLoad()                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 1. 加载Excel模板 mbAuditForm.xls                             ││
│  │ 2. 填入姓名、性别、身份证、病种                               ││
│  │ 3. 设置响应头 (application/msexcel)                         ││
│  │ 4. 写入response输出流                                        ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
浏览器弹出下载框 → 用户下载Excel文件
```

---

### 场景2：上传申报图片

```
用户上传身份证照片
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  Controller: VipMbdeclareInfoServiceApi (假设)                 │
│  @PostMapping("/editImage")                                     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 1. 接收 EditImagesVo {declareid, images: [Base64...]}       ││
│  │ 2. 调用 vipMbdeclareInfoService.editImage()                 ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  Service: VipMbdeclareInfoServiceImpl.editImage()              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 1. 遍历images列表                                            ││
│  │ 2. Base64解码 → byte[]                                       ││
│  │ 3. 生成UUID文件名                                            ││
│  │ 4. 上传到FTP服务器 /mbdeclare/mbedit/2024-01-15/            ││
│  │ 5. 更新image.content为FTP路径                               ││
│  │ 6. 转发给后厨更新数据库                                      ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
        │
        │  HTTP POST → 业务服务 (9091端口)
        │  Body: {declareid, images: [{content: "/mbdeclare/..."}]}
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  业务服务 /mb/editImage                                         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ UPDATE vip_mbdeclare_file SET filepath=? WHERE declareid=?  ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
返回成功 → 用户看到"上传成功"
```

---

### 场景3：查询医保慢病余额

```
用户在APP查询慢病余额
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  Controller: VipMbdeclareInfoServiceApi                        │
│  @PostMapping("/queryChronicBalance")                           │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 1. 接收 CheckBalanceVo {idcard, visitkind}                   ││
│  │ 2. 调用 vipMbdeclareInfoService.VIPQueryChronicBalance()    ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  Service: VipMbdeclareInfoServiceImpl.VIPQueryChronicBalance() │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 1. 构造医保查询报文                                          ││
│  │   {AKB020: "医疗机构编码", AAC002: "身份证", AKA130: "就诊类型"}││
│  │ 2. 调用 callBJ1001() → 发送XML到医保系统                    ││
│  │ 3. 解析返回报文                                              ││
│  │ 4. 封装YBMessageVo返回                                      ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
        │
        │  HTTP → 医保系统（外部系统，不是业务服务）
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  医保系统                                                       │
│  返回: {AAC003: "姓名", AAE140: "险种类型", AAB004: "参保单位"}  │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
返回给用户 → 显示"职工医保 | 余额：5000元"
```

---

### 场景4：打印药店结算单

```
用户点击"打印结算单"
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  Controller: DrugstoreOrderServiceApi                          │
│  @PostMapping("/newestPrint")                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 1. 接收 TSettlementReportBjDto {ids, medical_category}      ││
│  │ 2. 调用 drugstoreOrderService.newestPrint()                 ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  Service: VipDrugstoreOrderServiceImpl.newestPrint()           │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 1. 校验medical_category（必须是"慢病"或"门诊统筹"）            ││
│  │ 2. 调用 /drugstoreOrderPrint/newestQuery 获取结算明细        ││
│  │ 3. 加载report.ftl模板                                        ││
│  │ 4. 用FreeMarker填充数据                                      ││
│  │ 5. HTML转PDF                                                ││
│  │ 6. 加水印（打印人名字）                                       ││
│  │ 7. 转Base64返回                                              ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  水印效果                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         门诊慢特病结算单                                   │   │
│  │  ─────────────────────────────────────────────────────   │   │
│  │  姓名：张三    身份证：230***111                          │   │
│  │  ...                                                       │   │
│  │  ─────────────────────────────────────────────────────   │   │
│  │                    李主任 打印于 2024-01-15 10:30         │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
返回给用户 → 浏览器展示PDF → 用户下载或打印
```

---

### 场景5：批量打包下载申报材料

```
用户点击"下载全部材料"
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  Controller: ZipDownloadController                              │
│  @GetMapping("/downloadZip/{declareId}")                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 1. 构造InfoVo {declareid, name, idcard}                     ││
│  │ 2. 调用 zipDownloadService.makeDir()                       ││
│  │ 3. 调用 zipDownloadService.packFilesToZip()                 ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  Service: ZipDownloadServiceImpl                               │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 1. 创建目录: /tmp/zip/张三_230***111/                        ││
│  │ 2. 调用业务服务生成审批表PDF                                 ││
│  │ 3. 下载证件照+病历图，转PDF                                  ││
│  │ 4. 合并成"影像资料.pdf"                                      ││
│  │ 5. 用PDFBox合并：申请表.pdf + 影像资料.pdf                    ││
│  │ 6. 用ZipOutputStream打包成ZIP                               ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  最终ZIP内容                                                    │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  📁 张三_230***111_申报材料.zip                            │ │
│  │    ├── 📄 门诊慢特病病种待遇认定申请表.pdf                  │ │
│  │    └── 📄 影像资料.pdf                                     │ │
│  │         ├── 第1页：身份证                                   │ │
│  │         ├── 第2页：病历                                     │ │
│  │         └── 第3页：处方                                     │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
浏览器下载ZIP → 用户解压查看
```

---

## 📊 调用链路总结表

| 场景 | Controller | Service | 转发目标 | 特殊处理 |
|-----|------------|---------|---------|---------|
| 下载审核表Excel | VipMbDeclareServiceApi | VipMbDeclareServiceImpl | 业务服务 | 填充Excel模板 |
| 上传图片 | VipMbdeclareInfoServiceApi | VipMbdeclareInfoServiceImpl | 业务服务 | 上传FTP |
| 查询医保余额 | VipMbdeclareInfoServiceApi | VipMbdeclareInfoServiceImpl | 医保系统 | XML报文 |
| 打印结算单 | DrugstoreOrderServiceApi | VipDrugstoreOrderServiceImpl | 业务服务 | PDF+水印 |
| 批量打包 | ZipDownloadController | ZipDownloadServiceImpl | 业务服务+FTP | ZIP打包 |

---

# Part 5：附录

## 📁 项目目录结构

```
picc-mzmtb-gateway/
├── src/main/java/com/picchealth/module/
│   ├── mb/                           # 慢病核心模块
│   │   ├── api/                      # Controller层
│   │   │   ├── VipMbDeclareServiceApi.java
│   │   │   └── YihuServiceApi.java
│   │   ├── service/                   # Service接口
│   │   │   ├── VipMbDeclareService.java
│   │   │   └── impl/                 # Service实现
│   │   │       ├── VipMbDeclareServiceImpl.java
│   │   │       └── ...
│   │   ├── vo/                       # VO对象 (21个)
│   │   │   ├── MbDeclareVo.java
│   │   │   └── ...
│   │   ├── po/                       # PO对象 (很少)
│   │   │   ├── VipMbdeclareInfo.java
│   │   │   └── ...
│   │   ├── dto/                      # DTO对象
│   │   ├── enums/                    # 枚举
│   │   └── constant/                 # 常量
│   └── restful/                      # 外部接口模块
│       └── vo/causacloud/           # 因数云VO
└── src/main/resources/
    ├── temp/                         # Excel模板
    │   ├── mbAuditForm.xls
    │   ├── mbmz_cardstatus_report.xls
    │   └── onecard_drugstore_order.xls
    └── templates/                    # PDF模板 (FreeMarker)
        ├── zg.ftl                    # 职工审批表
        ├── mtb.ftl                   # 慢特病审批表
        └── lb.ftl                    # 两病审批表
```

---

## 🔧 常用工具类

| 工具类 | 用途 |
|-------|------|
| `HttpForwardUtil` | HTTP转发（核心！） |
| `SFTPUtils` / `SFTPUtils_xcx` | SFTP文件上传下载 |
| `FTPFileUtil` | FTP文件操作 |
| `FileUtils` | 文件工具（Base64转InputStream等） |
| `JsonUtil` | JSON工具 |
| `PdfWatermarkUtil` | PDF水印 |
| `RedisUtil` | Redis缓存 |

---

## ⚠️ 开发注意事项

1. **前台服务没有数据库**：所有数据操作都要通过`HttpForwardUtil`转发给业务服务

2. **FTP文件上传路径**：
   - 申报图片：`/mbdeclare/mbedit/{日期}/`
   - 体检报告：`/mbdeclare/JJ/{日期}/`
   - 病历资料：`/mbdeclare/JC/{日期}/`
   - Banner图：`/mbBanner/`

3. **模板文件位置**：
   - Excel模板：`resources/temp/`
   - PDF模板：`resources/templates/`

4. **医保接口是外部调用**：不走`HttpForwardUtil`，直接发HTTP请求到医保系统

5. **Base64编解码**：
   - 前端传图片用Base64
   - Service层要解码成byte[]再存FTP
   - 返回给前端时再转Base64

---

## 📚 参考文档

- [PICC门诊慢特病前台服务架构解析](./picc-mzmtb-gateway架构解析.md)
- [HttpForwardUtil使用指南](./picc-mzmtb-gateway-HttpForwardUtil使用指南.md)

---

> 🎉 **恭喜你！** 到这里，你已经对picc-mzmtb-gateway的Service层和VO层有了深入的理解。继续加油！