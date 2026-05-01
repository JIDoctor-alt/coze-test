> ⚠️ 本文档仅供学习理解PICC项目，不做任何修改建议

# PICC人保健康权限管理系统 - 安全修复工单

> 生成日期：2024年
> 审核方式：代码审计
> 工单总数：8个（P0×4, P1×2, P2×2）

---

## 工单 #1: SM4加密密钥硬编码

### 基本信息
- **优先级**：P0
- **影响范围**：所有使用SM4加密的业务模块、用户敏感数据传输
- **发现位置**：`com.picc.common.utils.sm4.SM4Util`
- **风险等级**：高

### 问题描述
SM4Util类中将加密密钥硬编码为`1234567812345678`，该密钥被用于敏感数据加密（如医保卡号、联系方式等）。攻击者通过反编译或源码泄露可直接获取密钥，进而解密所有加密数据。

**攻击场景**：攻击者获取密钥后，可批量解密数据库中存储的用户敏感信息，导致大规模数据泄露。

### 复现步骤
1. 获取SM4Util.java源码或反编译class文件
2. 定位密钥常量`1234567812345678`
3. 使用相同密钥解密任意加密字段

### 当前代码
```java
public class SM4Util {
    // 硬编码密钥，违反密钥管理安全规范
    private static final String SECRET_KEY = "1234567812345678";
    
    public static String encryptDataEcb(String plainText) {
        // 使用固定密钥加密
        return sm4.encrypt_Ecb_Padding(s plainText, SECRET_KEY);
    }
    
    public static String decryptDataEcb(String cipherText) {
        return sm4.decrypt_Ecb_Padding(cipherText, SECRET_KEY);
    }
}
```

### 问题分析
```java
public class SM4Util {
    private static volatile String SECRET_KEY;
    
    /**
     * 从安全配置中心（如Nacos Config、Apollo）动态获取密钥
     * 或通过环境变量/密钥管理服务(KMS)注入
     */
    public static void initSecretKey(String key) {
        if (StringUtils.isBlank(key)) {
            throw new IllegalArgumentException("SM4密钥不能为空");
        }
        if (key.length() != 16) {
            throw new IllegalArgumentException("SM4密钥长度必须为16字节");
        }
        SECRET_KEY = key;
    }
    
    private static String getSecretKey() {
        if (SECRET_KEY == null) {
            synchronized (SM4Util.class) {
                if (SECRET_KEY == null) {
                    // 从环境变量或配置中心获取
                    String envKey = System.getenv("SM4_SECRET_KEY");
                    if (StringUtils.isBlank(envKey)) {
                        throw new IllegalStateException("SM4密钥未初始化，请检查配置");
                    }
                    initSecretKey(envKey);
                }
            }
        }
        return SECRET_KEY;
    }
    
    public static String encryptDataEcb(String plainText) {
        if (StringUtils.isBlank(plainText)) {
            return null;
        }
        return sm4.encrypt_Ecb_Padding(plainText, getSecretKey());
    }
    
    public static String decryptDataEcb(String cipherText) {
        if (StringUtils.isBlank(cipherText)) {
            return null;
        }
        return sm4.decrypt_Ecb_Padding(cipherText, getSecretKey());
    }
}
```

### 测试验证
- [ ] 验证密钥为空时抛出明确异常
- [ ] 验证密钥长度不为16时抛出异常
- [ ] 验证正常加解密流程
- [ ] 验证不同密钥加密后无法互相解密
- [ ] 验证密钥通过环境变量注入成功

### 回归影响
- 调用SM4Util的敏感数据加解密模块
- 需同步更新相关单元测试

### 预计工时
1人天

---

## 工单 #2: AES加密密钥硬编码

### 基本信息
- **优先级**：P0
- **影响范围**：所有使用AES加密的业务模块、HTTP请求参数加密
- **发现位置**：`com.picc.common.utils.aes.AesUtil`
- **风险等级**：高

### 问题描述
AesUtil类中将AES加密密钥硬编码为`abcdefgabcdefg12`，攻击者可直接使用该密钥解密所有AES加密的通信数据，包括HTTP请求中的敏感参数。

**攻击场景**：中间人攻击获取加密流量后，使用已知密钥解密会话token、认证凭据等敏感数据。

### 复现步骤
1. 定位AesUtil中的硬编码密钥
2. 使用BurpSuite拦截加密请求
3. 使用硬编码密钥解密 intercepted 流量

### 当前代码
```java
public class AesUtil {
    // 硬编码AES-128密钥
    private static final String DEFAULT_KEY = "abcdefgabcdefg12";
    
    public static String encrypt(String data) {
        return encrypt(data, DEFAULT_KEY);
    }
    
    public static String decrypt(String data) {
        return decrypt(data, DEFAULT_KEY);
    }
    
    public static String encrypt(String data, String key) {
        // 如果未传key则使用默认硬编码密钥
        if (key == null || key.length() == 0) {
            key = DEFAULT_KEY;
        }
        // ... 加密逻辑
    }
}
```

### 问题分析
```java
public class AesUtil {
    private static volatile String DEFAULT_KEY;
    private static final String KEY_ENV_NAME = "AES_SECRET_KEY";
    
    /**
     * 初始化AES密钥，优先从环境变量获取
     */
    public static void initKey(String key) {
        if (StringUtils.isBlank(key)) {
            throw new IllegalArgumentException("AES密钥不能为空");
        }
        if (key.length() != 16 && key.length() != 24 && key.length() != 32) {
            throw new IllegalArgumentException("AES密钥长度必须为16/24/32字节");
        }
        DEFAULT_KEY = key;
    }
    
    /**
     * 静态块：从环境变量或配置中心初始化密钥
     */
    static {
        String envKey = System.getenv(KEY_ENV_NAME);
        if (StringUtils.isNotBlank(envKey)) {
            initKey(envKey);
        }
    }
    
    private static String getKey() {
        if (DEFAULT_KEY == null) {
            throw new IllegalStateException("AES密钥未初始化，请设置环境变量" + KEY_ENV_NAME);
        }
        return DEFAULT_KEY;
    }
    
    public static String encrypt(String data) {
        return encrypt(data, getKey());
    }
    
    public static String decrypt(String data) {
        return decrypt(data, getKey());
    }
    
    public static String encrypt(String data, String key) {
        if (data == null || data.length() == 0) {
            return null;
        }
        if (key == null || key.length() == 0) {
            throw new IllegalArgumentException("AES密钥不能为空");
        }
        // ... 加密逻辑保持不变
    }
    
    public static String decrypt(String data, String key) {
        if (data == null || data.length() == 0) {
            return null;
        }
        if (key == null || key.length() == 0) {
            throw new IllegalArgumentException("AES密钥不能为空");
        }
        // ... 解密逻辑保持不变
    }
}
```

### 测试验证
- [ ] 验证环境变量未设置时系统启动失败并抛出明确错误
- [ ] 验证密钥长度校验
- [ ] 验证加解密功能正常
- [ ] 验证硬编码密钥已被移除

### 回归影响
- HTTP加解密请求处理模块
- 第三方接口调用加解密模块

### 预计工时
1人天

---

## 工单 #3: RSA密钥硬编码

### 基本信息
- **优先级**：P0
- **影响范围**：数字签名、敏感信息RSA加密传输
- **发现位置**：`com.picc.mzmtb.user.service.impl.MoveServiceImpl`
- **风险等级**：高

### 问题描述
MoveServiceImpl中RSA私钥通过@Value注解的默认值硬编码，攻击者获取源码后可伪造签名，导致身份冒充和数据篡改风险。

**攻击场景**：攻击者使用泄露的RSA私钥伪造服务端签名，冒充系统向其他服务发起合法请求。

### 复现步骤
1. 反编译MoveServiceImpl.class或获取源码
2. 提取@Value默认值中的RSA私钥
3. 使用私钥伪造签名请求

### 当前代码
```java
@Service
public class MoveServiceImpl implements MoveService {
    
    @Value("${rsa.private.key:<此处为实际硬编码私钥内容>}")
    private String privateKey;
    
    @Value("${rsa.public.key:<此处为实际硬编码公钥内容>}")
    private String publicKey;
    
    public String sign(String data) {
        // 使用硬编码密钥签名
        return RSAUtils.sign(data, privateKey);
    }
}
```

### 问题分析
```java
@Service
@ConfigurationProperties(prefix = "rsa")
public class MoveServiceImpl implements MoveService {
    
    /**
     * RSA私钥 - 必须通过配置文件或环境变量注入，禁止硬编码
     * 建议从密钥管理服务（如AWS KMS、阿里云KMS、HashiCorp Vault）动态获取
     */
    @Value("${rsa.private.key}")
    private String privateKey;
    
    @Value("${rsa.public.key}")
    private String publicKey;
    
    @PostConstruct
    public void validateKeys() {
        if (StringUtils.isBlank(privateKey)) {
            throw new IllegalStateException("RSA私钥未配置，请检查rsa.private.key配置项");
        }
        if (StringUtils.isBlank(publicKey)) {
            throw new IllegalStateException("RSA公钥未配置，请检查rsa.public.key配置项");
        }
        log.info("RSA密钥初始化完成，私钥指纹: {}", calculateKeyFingerprint(privateKey));
    }
    
    public String sign(String data) {
        if (StringUtils.isBlank(data)) {
            throw new IllegalArgumentException("签名数据不能为空");
        }
        return RSAUtils.sign(data, privateKey);
    }
    
    public boolean verify(String data, String signature) {
        if (StringUtils.isBlank(data) || StringUtils.isBlank(signature)) {
            return false;
        }
        return RSAUtils.verify(data, signature, publicKey);
    }
    
    private String calculateKeyFingerprint(String key) {
        // 计算密钥指纹用于日志记录（不暴露密钥内容）
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] hash = md.digest(key.getBytes(StandardCharsets.UTF_8));
            return DatatypeConverter.printHexBinary(hash).substring(0, 16);
        } catch (NoSuchAlgorithmException e) {
            return "UNAVAILABLE";
        }
    }
}
```

### 测试验证
- [ ] 验证私钥为空时应用启动失败
- [ ] 验证签名和验签功能正常
- [ ] 验证不同密钥对签名无法通过验签
- [ ] 验证日志中仅记录密钥指纹而非密钥内容

### 回归影响
- 涉及RSA签名验证的业务接口
- 第三方系统对接模块

### 预计工时
1人天

---

## 工单 #4: URL权限模糊匹配导致越权访问

### 基本信息
- **优先级**：P0
- **影响范围**：所有受保护的API接口、权限控制模块
- **发现位置**：`com.picc.mzmtb.user.interceptor.ApiInterceptor`
- **风险等级**：高

### 问题描述
ApiInterceptor使用`contains()`方法进行URL权限匹配，存在严重的越权漏洞。例如配置`/admin/user/delete`权限时，可被`/admin/user/deleteAll`错误匹配，导致未授权用户可访问敏感接口。

**攻击场景**：
1. 普通用户被授权访问`/report/export`导出报表
2. 攻击者请求`/report/exportAdminPasswords`时可绕过权限校验
3. 实际访问了未授权的敏感接口

### 复现步骤
1. 使用普通权限账号登录系统
2. 查看已授权URL列表（如`/privilege/user/list`）
3. 构造恶意请求`/privilege/user/listAll`或`/privilege/user/listxxx`
4. 验证是否成功访问（若权限配置中包含`/privilege/user`）

### 当前代码
```java
@Component
public class ApiInterceptor extends HandlerInterceptorAdapter {
    
    @Autowired
    private PrivilegeService privilegeService;
    
    @Override
    public boolean preHandle(HttpServletRequest request, 
                            HttpServletResponse response, Object handler) {
        String requestUri = request.getRequestURI();
        String contextPath = request.getContextPath();
        String path = requestUri.substring(contextPath.length());
        
        // 获取用户权限列表
        List<String> userPrivileges = getUserPrivileges();
        
        // 使用contains模糊匹配 - 存在严重越权风险
        boolean hasPermission = userPrivileges.stream()
            .anyMatch(privilege -> path.contains(privilege));
        
        if (!hasPermission) {
            response.setStatus(403);
            response.getWriter().write("{\"code\":403,\"msg\":\"无权限访问\"}");
            return false;
        }
        return true;
    }
}
```

### 问题分析
```java
@Component
public class ApiInterceptor extends HandlerInterceptorAdapter {
    
    @Autowired
    private PrivilegeService privilegeService;
    
    @Override
    public boolean preHandle(HttpServletRequest request, 
                            HttpServletResponse response, Object handler) {
        String requestUri = request.getRequestURI();
        String contextPath = request.getContextPath();
        String path = requestUri.substring(contextPath.length());
        
        // 获取用户权限列表
        List<String> userPrivileges = getUserPrivileges();
        
        // 使用精确前缀匹配，路径必须以授权路径开头
        // 确保/privilege/user能匹配/privilege/user/list
        // 但/privilege/user不能匹配/privilege/users/delete
        boolean hasPermission = userPrivileges.stream()
            .anyMatch(privilege -> {
                // 规范化路径：去除末尾斜杠，统一处理
                String normalizedPath = normalizePath(path);
                String normalizedPrivilege = normalizePath(privilege);
                
                // 精确前缀匹配：请求路径必须以授权路径开头
                // 且要么长度相等，要么后面紧跟斜杠（防止越权）
                return normalizedPath.startsWith(normalizedPrivilege) 
                    && (normalizedPath.length() == normalizedPrivilege.length() 
                        || normalizedPath.charAt(normalizedPrivilege.length()) == '/');
            });
        
        if (!hasPermission) {
            // 记录未授权访问日志
            log.warn("未授权访问尝试: URI={}, User={}, IP={}", 
                    path, getCurrentUserId(), getClientIP(request));
            response.setStatus(403);
            response.setContentType("application/json;charset=UTF-8");
            response.getWriter().write("{\"code\":403,\"msg\":\"无权限访问\"}");
            return false;
        }
        return true;
    }
    
    /**
     * 规范化路径：去除末尾斜杠（保留根路径"/"）
     */
    private String normalizePath(String path) {
        if (path == null) {
            return "";
        }
        // 统一使用正斜杠
        path = path.replace("\\", "/");
        // 去除末尾斜杠（根路径除外）
        while (path.length() > 1 && path.endsWith("/")) {
            path = path.substring(0, path.length() - 1);
        }
        return path;
    }
}
```

### 测试验证
- [ ] `/privilege/user`能匹配`/privilege/user/list`（授权）
- [ ] `/privilege/user`不能匹配`/privilege/users/delete`（拒绝）
- [ ] `/privilege/user/list`不能匹配`/privilege/user/delete`（拒绝）
- [ ] `/admin`能匹配`/admin/user`（授权）
- [ ] 验证边界情况：根路径、特殊字符、路径遍历符

### 回归影响
- 所有API权限校验逻辑
- 需回归测试所有接口权限控制

### 预计工时
1.5人天

---

## 工单 #5: API过滤器拦截范围不足

### 基本信息
- **优先级**：P1
- **影响范围**：除`/privilege/user/*`外的所有接口
- **发现位置**：`com.picc.mzmtb.user.filter.APIAuthorityFilter`
- **风险等级**：高

### 问题描述
APIAuthorityFilter仅拦截`/privilege/user/*`路径，导致其他路径（如`/admin/*`、`/system/*`等）的敏感接口完全绕过了权限校验过滤器，存在未授权访问风险。

**攻击场景**：攻击者可直接访问`/admin/config/update`、`/system/user/export`等敏感接口，完全绕过权限校验。

### 复现步骤
1. 获取系统接口文档或抓包分析接口路径
2. 定位不在`/privilege/user/*`范围内的敏感接口
3. 直接发送未授权请求，验证是否返回业务数据

### 当前代码
```java
@WebFilter(urlPatterns = "/privilege/user/*")
public class APIAuthorityFilter implements Filter {
    
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, 
                         FilterChain chain) throws IOException, ServletException {
        HttpServletRequest req = (HttpServletRequest) request;
        HttpServletRequestWrapper wrapper = new HttpServletRequestWrapper(req);
        
        // 权限校验逻辑...
        if (!checkAuthority(wrapper)) {
            response.getWriter().write("{\"code\":401,\"msg\":\"未登录\"}");
            return;
        }
        
        chain.doFilter(wrapper, response);
    }
}
```

### 问题分析
```java
@WebFilter(urlPatterns = "/*")
public class APIAuthorityFilter implements Filter {
    
    /**
     * 需要放行的路径模式（无需登录即可访问）
     */
    private static final Set<String> EXCLUDE_PATTERNS = new HashSet<>(Arrays.asList(
        "/login",
        "/logout", 
        "/public/",
        "/static/",
        "/error",
        "/health",
        "/actuator/health"
    ));
    
    /**
     * 需要放行的接口路径（使用正则匹配）
     */
    private static final List<Pattern> EXCLUDE_REGEX_PATTERNS = Arrays.asList(
        Pattern.compile("^/api/v\\d+/public/.*$"),      // 公开API
        Pattern.compile("^/swagger-ui/.*$"),            // Swagger文档
        Pattern.compile("^/v3/api-docs.*$")
    );
    
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, 
                         FilterChain chain) throws IOException, ServletException {
        HttpServletRequest req = (HttpServletRequest) request;
        
        String path = getRequestPath(req);
        
        // 检查是否在放行列表中
        if (isExcludedPath(path)) {
            chain.doFilter(request, response);
            return;
        }
        
        // 执行权限校验
        HttpServletRequestWrapper wrapper = new HttpServletRequestWrapper(req);
        if (!checkAuthority(wrapper)) {
            HttpServletResponse resp = (HttpServletResponse) response;
            resp.setStatus(401);
            resp.setContentType("application/json;charset=UTF-8");
            resp.getWriter().write("{\"code\":401,\"msg\":\"未登录或登录已过期\"}");
            return;
        }
        
        chain.doFilter(wrapper, response);
    }
    
    /**
     * 检查路径是否在放行列表中
     */
    private boolean isExcludedPath(String path) {
        if (path == null) {
            return false;
        }
        
        // 精确匹配检查
        for (String pattern : EXCLUDE_PATTERNS) {
            if (path.equals(pattern) || path.startsWith(pattern)) {
                return true;
            }
        }
        
        // 正则匹配检查
        for (Pattern pattern : EXCLUDE_REGEX_PATTERNS) {
            if (pattern.matcher(path).matches()) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * 获取标准化请求路径
     */
    private String getRequestPath(HttpServletRequest request) {
        String contextPath = request.getContextPath();
        String uri = request.getRequestURI();
        if (contextPath == null || contextPath.equals("/")) {
            return uri;
        }
        return uri.substring(contextPath.length());
    }
}
```

### 测试验证
- [ ] 验证放行路径（如`/login`）无需认证即可访问
- [ ] 验证`/privilege/user/*`路径需要认证
- [ ] 验证`/admin/*`、`/system/*`等路径现在被正确拦截
- [ ] 验证Swagger文档等开发相关路径被正确放行
- [ ] 验证Filter执行顺序正确

### 回归影响
- 登录/登出接口（需确保在放行列表中）
- 静态资源访问
- 健康检查接口

### 预计工时
1人天

---

## 工单 #6: 权限编码硬编码导致权限控制失效

### 基本信息
- **优先级**：P1
- **影响范围**：用户权限分配、角色管理
- **发现位置**：`com.picc.mzmtb.user.service.impl.UserInfoServiceImpl`
- **风险等级**：中

### 问题描述
UserInfoServiceImpl中权限编码`88`被硬编码用于特定业务逻辑判断，当权限编码规则变更时代码需同步修改，且难以动态配置。同时存在业务逻辑耦合问题。

**攻击场景**：攻击者通过分析代码逻辑，可能利用固定权限编码绕过业务校验。

### 复现步骤
1. 搜索代码中`88`的使用位置
2. 分析该权限编码对应的业务功能
3. 尝试在权限配置中修改或绕过该逻辑

### 当前代码
```java
@Service
public class UserInfoServiceImpl implements UserInfoService {
    
    @Autowired
    private PrivilegeMapper privilegeMapper;
    
    public boolean hasSpecialPrivilege(Long userId) {
        // 硬编码权限编码"88"，难以维护
        List<Privilege> privileges = privilegeMapper.selectByUserId(userId);
        return privileges.stream()
            .anyMatch(p -> "88".equals(p.getPrivilegeCode()));
    }
    
    public void assignSpecialPrivilege(Long userId) {
        // 硬编码权限编码"88"
        Privilege privilege = new Privilege();
        privilege.setUserId(userId);
        privilege.setPrivilegeCode("88");
        privilege.setPrivilegeName("特殊权限");
        privilegeMapper.insert(privilege);
    }
    
    public List<User> queryUsersWithSpecialPrivilege() {
        // SQL中硬编码权限编码
        return userMapper.selectList(
            new QueryWrapper<User>().like("privilege_codes", "88")
        );
    }
}
```

### 问题分析
```java
@Service
public class UserInfoServiceImpl implements UserInfoService {
    
    private static final String PRIVILEGE_CODE_CONFIG_KEY = "system.special.privilege.code";
    
    @Autowired
    private PrivilegeMapper privilegeMapper;
    
    @Autowired
    private ConfigService configService;  // 统一配置服务
    
    /**
     * 获取特殊权限编码，从配置中心动态获取
     */
    private String getSpecialPrivilegeCode() {
        String code = configService.getString(PRIVILEGE_CODE_CONFIG_KEY);
        if (StringUtils.isBlank(code)) {
            throw new IllegalStateException(
                "特殊权限编码未配置，请检查配置项: " + PRIVILEGE_CODE_CONFIG_KEY);
        }
        return code;
    }
    
    public boolean hasSpecialPrivilege(Long userId) {
        List<Privilege> privileges = privilegeMapper.selectByUserId(userId);
        String specialCode = getSpecialPrivilegeCode();
        return privileges.stream()
            .anyMatch(p -> specialCode.equals(p.getPrivilegeCode()));
    }
    
    public void assignSpecialPrivilege(Long userId) {
        Privilege privilege = new Privilege();
        privilege.setUserId(userId);
        privilege.setPrivilegeCode(getSpecialPrivilegeCode());
        privilege.setPrivilegeName("特殊权限");
        privilegeMapper.insert(privilege);
    }
    
    public List<User> queryUsersWithSpecialPrivilege() {
        String specialCode = getSpecialPrivilegeCode();
        return userMapper.selectList(
            new QueryWrapper<User>().like("privilege_codes", specialCode)
        );
    }
    
    /**
     * 获取所有特殊权限配置（可枚举）
     */
    public Map<String, String> getAllSpecialPrivilegeCodes() {
        return configService.getMap("system.special.privilege");
    }
}
```

**配置文件 (application.yml)**:
```yaml
system:
  special:
    privilege:
      code: "88"  # 可通过配置中心动态修改
      name: "特殊权限"
```

### 测试验证
- [ ] 验证权限编码可从配置中心动态获取
- [ ] 验证配置为空时抛出明确异常
- [ ] 验证修改配置后权限逻辑生效
- [ ] 验证权限编码变更后的兼容性

### 回归影响
- 权限管理模块
- 用户管理模块
- 涉及特殊权限的业务功能

### 预计工时
1人天

---

## 工单 #7: 默认密码可预测

### 基本信息
- **优先级**：P2
- **影响范围**：新用户创建、密码重置功能
- **发现位置**：`com.picc.mzmtb.user.service.impl.UserServiceImpl`
- **风险等级**：中

### 问题描述
系统使用可预测的默认密码`PICChealth@2020`，攻击者可通过社工猜测、代码泄露等方式获取该密码，进而登录未修改默认密码的账号。

**攻击场景**：
1. 新员工账号创建后未强制修改密码
2. 攻击者尝试使用常见默认密码登录
3. 成功登录后获取敏感业务数据

### 复现步骤
1. 获取系统默认密码规则（代码注释、文档等）
2. 使用默认密码尝试登录常见用户名
3. 验证是否存在未修改默认密码的账号

### 当前代码
```java
@Service
public class UserServiceImpl implements UserService {
    
    private static final String DEFAULT_PASSWORD = "PICChealth@2020";
    
    public Long createUser(UserDTO userDTO) {
        User user = new User();
        user.setUsername(userDTO.getUsername());
        // 使用固定默认密码
        user.setPassword(passwordEncoder.encode(DEFAULT_PASSWORD));
        // ...
        return userMapper.insert(user);
    }
    
    public void resetPassword(Long userId) {
        User user = userMapper.selectById(userId);
        // 重置为默认密码
        user.setPassword(passwordEncoder.encode(DEFAULT_PASSWORD));
        userMapper.updateById(user);
        // ...
    }
}
```

### 问题分析
```java
@Service
public class UserServiceImpl implements UserService {
    
    private static final int MIN_PASSWORD_LENGTH = 10;
    
    /**
     * 生成随机默认密码
     * 格式：大写字母 + 小写字母 + 数字 + 特殊字符，长度12位
     */
    private String generateRandomDefaultPassword() {
        String upperCase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        String lowerCase = "abcdefghijklmnopqrstuvwxyz";
        String numbers = "0123456789";
        String specialChars = "!@#$%^&*";
        String allChars = upperCase + lowerCase + numbers + specialChars;
        
        SecureRandom random = new SecureRandom();
        StringBuilder password = new StringBuilder();
        
        // 确保包含各类字符
        password.append(upperCase.charAt(random.nextInt(upperCase.length())));
        password.append(lowerCase.charAt(random.nextInt(lowerCase.length())));
        password.append(numbers.charAt(random.nextInt(numbers.length())));
        password.append(specialChars.charAt(random.nextInt(specialChars.length())));
        
        // 填充剩余字符
        for (int i = 4; i < 12; i++) {
            password.append(allChars.charAt(random.nextInt(allChars.length())));
        }
        
        // 打乱顺序
        char[] chars = password.toString().toCharArray();
        for (int i = chars.length - 1; i > 0; i--) {
            int j = random.nextInt(i + 1);
            char temp = chars[i];
            chars[i] = chars[j];
            chars[j] = temp;
        }
        
        return new String(chars);
    }
    
    public Long createUser(UserDTO userDTO) {
        User user = new User();
        user.setUsername(userDTO.getUsername());
        
        // 生成随机默认密码
        String defaultPassword = generateRandomDefaultPassword();
        user.setPassword(passwordEncoder.encode(defaultPassword));
        
        // 标记首次登录必须修改密码
        user.setMustChangePassword(true);
        user.setCreateTime(new Date());
        
        Long userId = userMapper.insert(user);
        
        // 通过安全渠道发送密码（如短信、加密邮件）
        sendPasswordNotification(user.getUsername(), defaultPassword, user.getMobile());
        
        return userId;
    }
    
    public void resetPassword(Long userId) {
        User user = userMapper.selectById(userId);
        
        // 生成一次性随机密码
        String tempPassword = generateRandomDefaultPassword();
        user.setPassword(passwordEncoder.encode(tempPassword));
        user.setMustChangePassword(true);
        user.setPasswordUpdateTime(new Date());
        
        userMapper.updateById(user);
        
        // 通过安全渠道发送临时密码
        sendPasswordNotification(user.getUsername(), tempPassword, user.getMobile());
        
        // 记录密码重置日志（不记录密码本身）
        log.info("密码已重置: userId={}, expireTime={}", userId, LocalDateTime.now().plusHours(24));
    }
    
    /**
     * 发送密码通知（示例，具体实现需对接实际通知渠道）
     */
    private void sendPasswordNotification(String username, String password, String mobile) {
        if (mobile != null && mobile.matches("^1\\d{10}$")) {
            // 通过短信发送
            smsService.send(mobile, String.format(
                "【PICC人保健康】您的临时密码：%s，请于24小时内登录并修改密码。", password));
        }
    }
}
```

### 测试验证
- [ ] 验证新用户创建时生成随机密码
- [ ] 验证密码包含大写、小写、数字、特殊字符
- [ ] 验证密码长度为12位
- [ ] 验证密码重置生成新随机密码
- [ ] 验证首次登录强制要求修改密码
- [ ] 验证密码不记录到日志

### 回归影响
- 用户创建流程
- 密码重置流程
- 通知系统集成

### 预计工时
1人天

---

## 工单 #8: 密码明文存储

### 基本信息
- **优先级**：P2
- **影响范围**：用户认证、密码存储
- **发现位置**：`com.picc.mzmtb.user.service.impl.MoveServiceImpl.passwordBackMD5()`
- **风险等级**：高

### 问题描述
`passwordBackMD5()`方法将用户密码以MD5形式存储（可逆），而非使用bcrypt/argon2等专业密码哈希算法。MD5已被证实可被彩虹表快速破解，且无盐值存储易遭受暴力破解。

**攻击场景**：
1. 数据库泄露后，攻击者使用彩虹表快速匹配大量用户密码
2. 相同密码的用户会生成相同的MD5值，易被识别

### 复现步骤
1. 找到`passwordBackMD5()`方法调用位置
2. 分析密码存储逻辑
3. 使用在线MD5破解工具验证密码强度

### 当前代码
```java
@Service
public class MoveServiceImpl implements MoveService {
    
    /**
     * 密码备份 - 使用MD5存储（不安全）
     */
    public void passwordBackMD5(String userId, String password) {
        // 直接使用MD5，无盐值
        String md5Password = MD5Util.encode(password);
        
        // 存储到备份表
        PasswordBackup backup = new PasswordBackup();
        backup.setUserId(userId);
        backup.setPasswordHash(md5Password);
        backup.setCreateTime(new Date());
        passwordBackupMapper.insert(backup);
    }
    
    /**
     * 验证密码
     */
    public boolean verifyPassword(String userId, String password) {
        String storedHash = passwordBackupMapper.selectByUserId(userId);
        String inputHash = MD5Util.encode(password);
        return storedHash.equals(inputHash);
    }
}

// MD5Util - 不安全的实现
public class MD5Util {
    public static String encode(String input) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(input.getBytes());
            return Hex.encodeHexString(digest);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }
}
```

### 问题分析
```java
@Service
public class MoveServiceImpl implements MoveService {
    
    @Autowired
    private PasswordEncoder passwordEncoder;
    
    /**
     * 密码备份 - 使用BCrypt专业密码哈希算法
     * BCrypt特性：
     * 1. 内置盐值，每条密码哈希使用不同盐
     * 2. 计算成本可调节，适应硬件发展
     * 3. 专为密码设计，经过安全社区验证
     */
    public void passwordBack(String userId, String rawPassword) {
        // 使用Spring Security的BCryptPasswordEncoder
        // 默认强度10，自动生成随机盐
        String bcryptHash = passwordEncoder.encode(rawPassword);
        
        PasswordBackup backup = new PasswordBackup();
        backup.setUserId(userId);
        backup.setPasswordHash(bcryptHash);
        backup.setHashAlgorithm("BCrypt");  // 记录使用的算法，便于后续迁移
        backup.setCreateTime(new Date());
        passwordBackupMapper.insert(backup);
        
        // 记录操作日志（不记录密码明文或哈希）
        log.info("密码备份完成: userId={}, algorithm=BCrypt", userId);
    }
    
    /**
     * 验证密码
     * BCrypt的matches方法会自动处理盐值对比
     */
    public boolean verifyPassword(String userId, String rawPassword) {
        PasswordBackup backup = passwordBackupMapper.selectByUserId(userId);
        if (backup == null) {
            log.warn("密码验证失败，用户不存在: userId={}", userId);
            return false;
        }
        
        String storedHash = backup.getPasswordHash();
        boolean matches = passwordEncoder.matches(rawPassword, storedHash);
        
        if (!matches) {
            log.warn("密码验证失败: userId={}", userId);
        }
        
        return matches;
    }
    
    /**
     * 检查密码强度（可选集成）
     * 使用zxcvbn库评估密码强度
     */
    public PasswordStrengthResult checkPasswordStrength(String password) {
        // 集成zxcvbn密码强度评估
        Strength strength = Strength.calculate(password);
        return new PasswordStrengthResult(
            strength.getScore(),           // 0-4分
            strength.getFeedback(),       // 学习思考
            strength.estimateCrackTime()  // 预计破解时间
        );
    }
}
```

**Spring Security 配置**:
```java
@Configuration
public class SecurityConfig {
    
    @Bean
    public PasswordEncoder passwordEncoder() {
        // BCryptPasswordEncoder - 推荐用于密码存储
        // strength参数范围4-31，数值越高计算越慢，安全性越高
        // 生产环境建议设置15-20
        return new BCryptPasswordEncoder(12);
    }
}
```

**数据表结构更新**:
```sql
ALTER TABLE password_backup 
ADD COLUMN hash_algorithm VARCHAR(20) DEFAULT 'BCrypt' COMMENT '哈希算法标识',
ADD COLUMN salt VARCHAR(60) DEFAULT NULL COMMENT '盐值（BCrypt内置，此字段冗余）',
MODIFY COLUMN password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希值';
```

### 测试验证
- [ ] 验证相同密码生成不同的哈希值（BCrypt特性）
- [ ] 验证密码验证功能正常
- [ ] 验证哈希值长度符合BCrypt格式（约60字符）
- [ ] 验证密码存储算法标识正确记录
- [ ] 验证历史MD5密码可被正确识别（支持渐进式迁移）

### 回归影响
- 密码备份功能
- 密码验证功能
- 历史数据迁移脚本

### 预计工时
2人天（含数据迁移）

---

## 工单汇总

| 工单 | 问题 | 优先级 | 风险等级 | 预计工时 |
|------|------|--------|----------|----------|
| #1 | SM4密钥硬编码 | P0 | 高 | 1人天 |
| #2 | AES密钥硬编码 | P0 | 高 | 1人天 |
| #3 | RSA密钥硬编码 | P0 | 高 | 1人天 |
| #4 | URL权限模糊匹配 | P0 | 高 | 1.5人天 |
| #5 | 过滤器拦截范围不足 | P1 | 高 | 1人天 |
| #6 | 权限编码硬编码 | P1 | 中 | 1人天 |
| #7 | 默认密码可预测 | P2 | 中 | 1人天 |
| #8 | 密码明文存储 | P2 | 高 | 2人天 |

**总计：9.5人天**

---

## 修复优先级建议

### 立即修复（P0）
1. **工单 #4**：越权漏洞可被立即利用，影响所有接口
2. **工单 #5**：权限过滤器遗漏导致大量接口裸奔
3. **工单 #1-3**：密钥硬编码泄露后无法修复影响

### 尽快修复（P1）
4. **工单 #6**：权限编码耦合影响系统扩展性
5. **工单 #8**：密码存储风险在数据泄露时放大

### 计划修复（P2）
6. **工单 #7**：默认密码风险相对可控

---

## 附录：密钥管理建议

建议引入密钥管理服务（KMS），统一管理所有密钥：

```yaml
# application.yml
encryption:
  sm4:
    key: ${SM4_SECRET_KEY}  # 从环境变量或KMS获取
  aes:
    key: ${AES_SECRET_KEY}
  rsa:
    private-key: ${RSA_PRIVATE_KEY}
    public-key: ${RSA_PUBLIC_KEY}
```

密钥轮换机制：
- SM4/AES密钥：每90天轮换
- RSA密钥对：每180天轮换，保留旧公钥用于验证历史签名

---

📎 **延伸阅读**：
- [安全问题分析](picc-mzmtb-user-安全问题分析.md) - 完整的修复策略和3周修复时间线
- [安全问题原理学习文档](picc-mzmtb-user-安全问题原理学习文档.md) - 具体代码实现和部署注意事项
- [深度解析](picc-mzmtb-user-深度解析.md) - 安全机制详解、三道认证关卡流程图

