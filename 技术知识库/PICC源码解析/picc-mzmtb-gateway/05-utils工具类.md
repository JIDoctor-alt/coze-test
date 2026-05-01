# picchealth/utils - 工具类模块

## 🎯 模块一句话说明
**通用工具集** - 提供加密解密、HTTP调用、文件处理、FTP上传、PDF水印等工具方法

---

## 📁 工具类清单 (23个)

| 工具类 | 用途 | 小白理解 |
|--------|------|----------|
| AesUtil | AES加密 | 密码箱 |
| Sm2Util | SM2国密加密 | 保险柜 |
| HttpForwardUtil | HTTP请求转发 | 快递员 |
| HttpClient | HTTP客户端 | 浏览器 |
| FileUtils | 文件操作 | 文件管家 |
| ExcelUtil | Excel处理 | Excel助手 |
| FTPFileUtil | FTP上传 | 文件上传器 |
| SFTPUtils | SFTP安全上传 | 安全文件上传器 |
| PdfWatermarkUtil | PDF水印 | 水印印章 |
| ExcelWaterMarkUtil | Excel水印 | Excel水印 |
| CustomWaterMarkHandler | 水印处理器 | 水印工厂 |
| FontImageUtil | 字体图片生成 | 艺术字 |
| PropertiesUtil | 配置文件读取 | 配置读取器 |
| Json2XmlVistor | JSON转XML | 格式转换器 |
| Xml2JsonVisitor | XML转JSON | 格式转换器 |
| JsonAndXmlTools | JSON/XML互转 | 格式转换器 |
| OneCardwsXmlUtil | 一卡通XML工具 | 旧系统对接 |
| KeyHelper | 密钥帮助 | 密钥助手 |
| KeyPairGeneratorExample | 密钥对生成 | 钥匙工厂 |
| TransformUtil | 数据转换 | 变形金刚 |
| HmLinkRestfulBL | REST业务逻辑 | REST处理器 |
| HmLinkWebserviceBL | WebService业务逻辑 | SOAP处理器 |
| SFTPUtils_xcx | 小程序SFTP | 小程序上传 |

---

## 🔐 加密解密类

### 1. AesUtil.java

> 🎯 AES对称加密解密

### 这是啥？（小白版）
像"密码箱"，用同一个密码加密和解密数据。

### 核心方法
```java
public class AesUtil {
    // AES加密
    public static String aesEncrypt(String content) {
        // 用固定密钥加密
        return aesEncrypt(content, PRIVATE_KER);
    }
    
    // AES解密
    public static String aesDecrypt(String encrypt) {
        // 用固定密钥解密
        return aesDecrypt(encrypt, PRIVATE_KER);
    }
    
    // base64编码
    public static String base64Encode(byte[] bytes);
    
    // base64解码
    public static byte[] base64Decode(String base64Code);
}
```

### 使用示例
```java
String original = "Hello World";
String encrypted = AesUtil.aesEncrypt(original);  // 加密
String decrypted = AesUtil.aesDecrypt(encrypted); // 解密
```

---

### 2. Sm2Util.java

> 🎯 SM2国密算法加密解密

### 这是啥？（小白版）
像"高级保险柜"，用公钥加密、私钥解密，是国家标准的加密算法。

### 核心方法
```java
public class Sm2Util {
    // SM2加密
    public static String encryptData(String data) {
        SM2 sm2 = SmUtil.sm2(privateKey, publicKey);
        String encryptBcd = sm2.encryptBcd(data, KeyType.PublicKey);
        // 去掉04前缀，转小写
        return encryptBcd.substring(2).toLowerCase();
    }
    
    // SM2解密
    public static String decryptData(String encryptData) {
        SM2 sm2 = SmUtil.sm2(privateKey, publicKey);
        // 补齐04前缀
        if (!encryptData.startsWith("04")) {
            encryptData = "04".concat(encryptData);
        }
        byte[] decryptFromBcd = sm2.decryptFromBcd(encryptData, KeyType.PrivateKey);
        return StrUtil.utf8Str(decryptFromBcd);
    }
    
    // 生成密钥对
    public static void generateSm2KeyPair();
}
```

### 小程序加密流程
```
1. 前端用公钥加密身份证号
2. 传到网关 → EncryptDecryptAop拦截
3. 用私钥解密 → 业务代码直接拿到明文
```

---

## 🌐 HTTP请求类

### 3. HttpForwardUtil.java

> 🎯 HTTP请求转发核心工具

### 这是啥？（小白版）
像"快递中转站"，把请求转发到后端服务。

### 核心方法
```java
@Component
public class HttpForwardUtil {
    @Value("${forwardUrl:http://localhost:9091}")
    private String prefix;  // 后端服务地址
    
    // POST转发(泛型)
    public <T> T post(String url, HttpServletRequest request, 
                      Object requestVo, ParameterizedTypeReference<T> parameterizedTypeReference) {
        HttpHeaders headers = getHttpHeaders(request);  // 获取原请求头
        HttpEntity requestEntity = new HttpEntity(requestVo, headers);
        ResponseEntity<T> responseEntity = restTemplate.exchange(
            prefix + url, HttpMethod.POST, requestEntity, parameterizedTypeReference);
        return responseEntity.getBody();
    }
    
    // GET请求
    public <T> T get(String url, Class<T> tClass);
    
    // multipart/form-data转发(文件上传)
    public <T> T post(String url, HttpServletRequest request,
                      ParameterizedTypeReference<T> parameterizedTypeReference, 
                      Map<String,Object> requestVo);
}
```

### 请求头传递
```java
private HttpHeaders getHttpHeaders(HttpServletRequest request) {
    HttpHeaders headers = new HttpHeaders();
    Enumeration<String> names = request.getHeaderNames();
    while (names.hasMoreElements()) {
        String name = names.nextElement();
        headers.add(name, request.getHeader(name));  // 原样传递所有header
    }
    return headers;
}
```

---

### 4. HttpClient.java

> 🎯 传统HTTP客户端

### 这是啥？（小白版）
像"老式浏览器"，用Apache HttpClient发送请求。

### 使用场景
- 需要更精细控制的HTTP请求
- 连接池配置
- 超时设置

---

### 5. HttpForwardUtil.post (JSON方式)

```java
public JSONObject post(String url, JSONObject all) {
    DefaultHttpClient httpClient = new DefaultHttpClient();
    HttpPost httpPost = new HttpPost(prefix + url);
    httpPost.setHeader("Accept", "application/json; charset=utf-8");
    StringEntity entity = new StringEntity(jsonParams, "utf-8");
    entity.setContentType("application/json");
    httpPost.setEntity(entity);
    HttpResponse response = httpClient.execute(httpPost);
    // 返回JSONObject
}
```

---

## 📁 文件处理类

### 6. FileUtils.java

> 🎯 文件操作工具

### 核心方法
```java
public class FileUtils {
    // 复制文件
    public static void copyFile(File src, File dest);
    
    // 删除文件
    public static boolean deleteFile(String filePath);
    
    // 获取文件扩展名
    public static String getExtension(String fileName);
    
    // 判断文件是否存在
    public static boolean exists(String filePath);
}
```

---

### 7. FTPFileUtil.java / SFTPUtils.java

> 🎯 FTP/SFTP文件上传

### 这是啥？（小白版）
像"文件搬运工"，把文件上传到远程服务器。

### FTP上传示例
```java
FTPFileUtil ftp = new FTPFileUtil();
ftp.connect(host, port, username, password);
ftp.uploadFile(localFile, remotePath);
ftp.disconnect();
```

### SFTP上传示例
```java
SFTPUtils sftp = new SFTPUtils(host, port, username, password);
sftp.login();
sftp.upload(localPath, remotePath);
sftp.logout();
```

---

### 8. ExcelUtil.java

> 🎯 Excel导入导出

### 核心方法
```java
public class ExcelUtil {
    // 导出Excel
    public static void exportExcel(HttpServletResponse response, 
                                   List<?> data, Class<?> clazz);
    
    // 导入Excel
    public static List<?> importExcel(InputStream is, Class<?> clazz);
}
```

---

## 🖼️ 水印图片类

### 9. PdfWatermarkUtil.java

> 🎯 PDF水印添加

### 这是啥？（小白版）
像"PDF印章机"，给PDF文件加水印。

### 使用示例
```java
PdfWatermarkUtil.addWatermark(
    sourcePdfPath,    // 源文件
    targetPdfPath,   // 输出文件
    "CONFIDENTIAL",  // 水印文字
    FontImageUtil.getChineseFont()  // 字体
);
```

---

### 10. ExcelWaterMarkUtil.java

> 🎯 Excel水印添加

### 使用示例
```java
ExcelWaterMarkUtil.addWaterMark(
    sourceExcelPath,
    targetExcelPath,
    "内部资料"
);
```

---

### 11. CustomWaterMarkHandler.java

> 🎯 水印处理器

### 使用示例
```java
// 支持多种水印类型
CustomWaterMarkHandler handler = new CustomWaterMarkHandler();
handler.setTextWaterMark("机密");     // 文字水印
handler.setImageWaterMark(imagePath); // 图片水印
handler.process(inputFile, outputFile);
```

---

### 12. FontImageUtil.java

> 🎯 字体图片生成

### 这是啥？（小白版）
像"艺术字生成器"，把文字转成图片。

### 核心方法
```java
public class FontImageUtil {
    // 创建字体图片
    public static BufferedImage createFontImage(String text, Font font, Color color);
    
    // 获取中文字体
    public static Font getChineseFont();
}
```

---

## 🔧 配置转换类

### 13. PropertiesUtil.java

> 🎯 配置文件读取

### 使用示例
```java
public class PropertiesUtil {
    // 读取配置
    public static String getProperty(String key);
    
    public static String getProperty(String key, String defaultValue);
}
```

---

### 14-16. JSON/XML转换工具

> 🎯 格式转换器

```java
// JSON转XML
String xml = Json2XmlVistor.json2Xml(jsonString);

// XML转JSON  
String json = Xml2JsonVisitor.xml2Json(xmlString);

// 互转
String xml = JsonAndXmlTools.json2Xml(jsonString);
String json = JsonAndXmlTools.xml2Json(xmlString);
```

---

## 🔗 业务处理类

### 17. HmLinkRestfulBL.java

> 🎯 REST业务逻辑处理

```java
public class HmLinkRestfulBL {
    // 处理REST请求并转发
    public static JSONObject runComRestful(String xmlData, String url);
}
```

---

### 18. HmLinkWebserviceBL.java

> 🎯 WebService业务逻辑处理

```java
public class HmLinkWebserviceBL {
    // 处理WebService请求并转发
    public static String runComWebsToRef(String xmlData, String url);
}
```

---

## 📝 知识点

### 1. 对称加密 vs 非对称加密

| 类型 | 算法 | 特点 | 场景 |
|------|------|------|------|
| 对称 | AES | 加密解密用同一密钥 | 数据传输 |
| 非对称 | SM2 | 公钥加密、私钥解密 | 敏感信息(身份证号) |

### 2. base64编码
把二进制数据转成ASCII字符，用于URL参数传递。

### 3. RestTemplate vs HttpClient
- RestTemplate: Spring提供的简洁HTTP客户端
- HttpClient: Apache提供的功能更全面的HTTP客户端

### 4. FTP vs SFTP
- FTP: 明文传输，不安全
- SFTP: SSH加密传输，安全

---

## 🎯 小白理解要点

1. **AesUtil是密码箱** - 同一密码加密解密
2. **Sm2Util是保险柜** - 公钥加密、私钥解密，用于小程序
3. **HttpForwardUtil是快递** - 转发请求到后端
4. **FTP/SFTP是上传** - 把文件传到服务器
5. **水印工具是印章** - 给文档加水印防伪

---

**相关文档**:
- `00-项目概览.md` - 整体架构
- `01-config配置类.md` - 加密配置
