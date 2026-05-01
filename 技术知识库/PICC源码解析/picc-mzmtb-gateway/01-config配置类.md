# picchealth/config - 配置类模块解析

## 🎯 模块一句话说明
**系统配置中心** - 管理跨域、加密、Excel、初始化、拦截器、JSON序列化、XSS过滤、定时任务等配置

---

## 1. LinkSpringBootApplication.java

> 🎯 启动入口，配置组件扫描

### 这是啥？（小白版）
就像饭店的开业准备，这个类是整个系统的"开业仪式"。它告诉Spring：有哪些区域（包）需要管理，开业前要做什么准备。

### 核心代码解析
```java
@ComponentScan(value = { 
    "pdfc.framework",           // PDFC框架组件
    "com.picchealth.module",    // 业务模块
    "com.picchealth.utils",     // 工具类
    "com.picchealth.config"     // 配置类
})
// 排除一些不需要自动装配的类
excludeFilters = @ComponentScan.Filter(...)
```

### 关键注解
| 注解 | 作用 |
|------|------|
| `@SpringBootApplication` | 启动Spring Boot应用 |
| `@EnableApolloConfig` | 启用Apollo配置中心 |
| `@EnableAsync` | 启用异步任务 |
| `@ServletComponentScan` | 扫描Servlet组件(Filter) |

---

## 2. cors/GlobalCorsConfig.java

> 🎯 跨域配置，让前端能访问后端

### 这是啥？（小白版）
就像机场的"国际中转许可"。没有这个配置，前端网页无法请求后端API（浏览器安全策略阻止）。

### 核心代码解析
```java
@Configuration
public class GlobalCorsConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")              // 所有路径都允许跨域
                .allowedOrigins("*")             // 允许所有域名访问
                .allowCredentials(true)         // 允许携带Cookie
                .allowedMethods("GET", "POST", "DELETE", "PUT", "PATCH") // 允许的方法
                .maxAge(3600);                  // 预检请求缓存1小时
    }
}
```

### 生活比喻
就像酒店前台说："所有客人都可以办理入住"，不用每次都检查身份证。

---

## 3. Encrypt/EncryptDecryptAop.java

> 🎯 自动解密小程序传过来的加密字段

### 这是啥？（小白版）
像快递的"拆箱员"。小程序用SM2加密身份证号传过来，网关自动帮忙解密，业务代码不用管加密解密。

### 核心代码解析
```java
@Aspect        // 切面
@Component
@Slf4j
public class EncryptDecryptAop {
    // 拦截mb模块的所有方法
    @Around("execution(* com.picchealth.module.mb.api.*.*(..))")
    public Object doProcess(ProceedingJoinPoint proceedingJoinPoint) {
        // 1. 获取方法参数
        List<Object> methodArgs = this.getMethodArgs(proceedingJoinPoint);
        // 2. 遍历所有参数
        for (Object item : methodArgs) {
            Field[] fields = item.getClass().getDeclaredFields();
            // 3. 找标记了@EncryptField的字段
            for (Field field : fields) {
                if (null != AnnotationUtils.findAnnotation(field, EncryptField.class)) {
                    // 4. SM2解密
                    field.set(item, Sm2Util.decryptData((String) field.get(item)));
                }
            }
        }
        return proceedingJoinPoint.proceed();
    }
}
```

### 知识点
| 概念 | 解释 |
|------|------|
| AOP | 面向切面编程，在方法前后添加额外逻辑 |
| @Around | 环绕通知，方法前后都执行 |
| 反射 | 运行时动态读取/修改类的字段 |

---

## 4. Encrypt/EncryptField.java

> 🎯 标记需要解密的字段

### 这是啥？（小白版）
像"易碎品"标签，贴在字段上表示"这个要解密"。

### 核心代码
```java
@Documented
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)  // 只能用在字段上
public @interface EncryptField {
}
```

### 使用示例
```java
public class LoginVo {
    @EncryptField  // 标记这个字段需要解密
    private String idCard;  // 身份证号
}
```

---

## 5. excel/DateConverter.java & DateTimeConverter.java

> 🎯 Excel导出时的日期格式化

### 这是啥？（小白版）
就像打印机的"格式刷"。导出Excel时，日期默认是数字，用这个转换器让它显示成"2024-01-01"格式。

### 核心代码
```java
public class DateConverter implements Converter<Date> {
    private static final String PATTERN_YYYY_MM_DD = "yyyy-MM-dd";
    
    @Override
    public WriteCellData<?> convertToExcelData(Date value, ...) {
        SimpleDateFormat sdf = new SimpleDateFormat(PATTERN_YYYY_MM_DD);
        String dateValue = sdf.format(value);
        return new WriteCellData<>(dateValue);
    }
}
```

### 两个转换器的区别
| 转换器 | 格式 | 示例 |
|--------|------|------|
| DateConverter | yyyy-MM-dd | 2024-01-01 |
| DateTimeConverter | yyyy-MM-dd HH:mm:ss | 2024-01-01 15:30:00 |

---

## 6. init/CommandLineRunnerImpl.java

> 🎯 启动时初始化缓存

### 这是啥？（小白版）
像餐厅开门前的"准备工作"。系统启动时加载常用数据到内存，不用每次查数据库。

### 核心代码
```java
@Component("CommandLineRunner")
public class CommandLineRunnerImpl implements CommandLineRunner {
    @Autowired
    MethodArgumentCache methodArgumentCache;  // 方法参数缓存
    
    @Autowired
    CustomFontCache customFontCache;           // 字体缓存
    
    @Override
    public void run(String... args) {
        methodArgumentCache.initExtCLass();    // 初始化方法参数
        customFontCache.initFont();            // 加载字体文件
    }
}
```

---

## 7. interceptor/APIAuthorityFilter.java

> 🎯 接口权限验证过滤器

### 这是啥？（小白版）
像小区门口的"门禁系统"。检查来访者是否有权进入，验证Token、用户ID、地区权限。

### 核心流程
```
请求进入 → 检查路径是否排除 → 验证Token → 检查用户权限 → 放行或拒绝
```

### 关键代码逻辑
```java
// 1. 排除路径不用验证
boolean isExcluded = excludePaths.stream()
    .anyMatch(excludePath -> requestPath.startsWith(excludePath));

// 2. 小程序用户验证
String xcxUser = request.getHeader("xcxUser");
xcxString = Sm2Util.decryptData(xcxUser).toUpperCase(); // 解密手机号

// 3. 检查Redis中的Token
if (!redisUtil.exists(XCXUsers + xcxString)){
    throw new CustomException("Token无效!");
}

// 4. 经办端Token验证
String token = request.getHeader(HEAD_TOKEN);
String userid = request.getHeader(HEAD_USERID2);
```

### 拦截的路径
- `/ppop/*` - 药品相关
- `/drugstore/*` - 药店相关
- `/MbDeclare/*` - 慢病申报
- `/MbReview/*` - 审核相关
- `/Login/*` - 登录相关

---

## 8. interceptor/FlagInterceptorConfig.java

> 🎯 拦截器，提取请求中的flag

### 这是啥？（小白版）
像快递的"签收单"，记录这个请求归属哪个地区/机构。

### 核心代码
```java
@Configuration
public class FlagInterceptorConfig implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest request, ...) {
        String flag = request.getHeader(RequestConstant.HEAD_FLAG);
        FlagLocal flagLocal = new FlagLocal();
        flagLocal.setFlag(flag);
        FlagUtils.setFlagLocal(flagLocal);  // 存入ThreadLocal
        return true;
    }
    
    @Override
    public void afterCompletion(...) {
        FlagUtils.remove();  // 请求结束后清理
    }
}
```

### ThreadLocal 是什么？
就像每个线程的"专属口袋"，存的数据只有当前线程能访问，互不干扰。

---

## 9. interceptor/MvcInterceptorConfig.java

> 🎯 MVC拦截器配置

### 这是啥？（小白版）
像"安检传送带"，把请求传送到指定拦截器检查。

### 核心代码
```java
@Configuration
public class MvcInterceptorConfig extends WebMvcConfigurationSupport {
    @Override
    protected void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(flagInterceptorConfig)
                .addPathPatterns(UrlApiConstant.VERSION + "/**")  // 拦截所有v2开头的请求
                .excludePathPatterns(
                    "/swagger-resources/**",  // 排除Swagger文档
                    "/v2/MbDeclareFileView/getPicPath/**"  // 排除某个接口
                );
    }
}
```

---

## 10. interceptor/ServletConfig.java

> 🎯 Tomcat服务器特殊配置

### 这是啥？（小白版）
像"机场的特殊通道设置"，允许某些特殊字符通过（URL中的大括号等）。

### 核心代码
```java
@Configuration
public class ServletConfig {
    @Bean
    public ConfigurableServletWebServerFactory webServerFactory() {
        BesServletWebServerFactory tomcatFactory = new BesServletWebServerFactory();
        tomcatFactory.addConnectorCustomizers(connector -> {
            connector.setProperty("relaxedQueryChars","|{}[](),/:;<=>?@[\\]{}");
            connector.setProperty("relaxedPathChars","|{}[](),/:;<=>?@[\\]{}");
        });
        return tomcatFactory;
    }
}
```

---

## 11. jackson/BigDecimalSerialize.java

> 🎯 金额字段保留两位小数

### 这是啥？（小白版）
像"收银机的四舍五入"，金额数字自动保留2位小数。

### 核心代码
```java
public class BigDecimalSerialize extends JsonSerializer<BigDecimal> {
    @Override
    public void serialize(BigDecimal value, JsonGenerator gen, ...) {
        if (value != null && !"".equals(value)) {
            // 保留两位小数，四舍五入
            gen.writeString(value.setScale(2, RoundingMode.HALF_DOWN) + "");
        }
    }
}
```

### 使用方式
```java
@JsonSerialize(using = BigDecimalSerialize.class)
private BigDecimal amount;  // 自动保留两位小数
```

---

## 12. xssfilter/XssRequestFilter.java

> 🎯 XSS攻击防护过滤器

### 这是啥？（小白版）
像"安检X光机"，检测并过滤恶意脚本，防止跨站脚本攻击。

### 核心代码
```java
@WebFilter(filterName = "xssFilter", urlPatterns = {"/*"})
public class XssRequestFilter implements Filter {
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) {
        // 包装请求，过滤XSS字符
        request = new XssHttpServletRequestWrapper((HttpServletRequest) request);
        
        // 设置Cookie的HttpOnly属性，防止JS读取
        ((HttpServletResponse) response).setHeader("Set-Cookie", "...; HttpOnly");
        
        chain.doFilter(request, response);
    }
}
```

### 防护原理
把 `<script>alert('xss')</script>` 转换成 `&lt;script&gt;` 避免执行。

---

## 13. XxlJobConfig.java

> 🎯 定时任务配置

### 这是啥？（小白版）
像"闹钟"，定时执行某些任务，比如每天凌晨同步数据。

### 核心代码
```java
@Configuration
public class XxlJobConfig {
    @Value("${xxl.job.admin.addresses}")
    private String adminAddresses;  // 调度中心地址
    
    @Value("${xxl.job.executor.appname}")
    private String appname;  // 执行器名称
    
    @Bean
    public XxlJobSpringExecutor xxlJobExecutor() {
        XxlJobSpringExecutor executor = new XxlJobSpringExecutor();
        executor.setAdminAddresses(adminAddresses);
        executor.setAppname(appname);
        executor.setPort(port);
        // ...
        return executor;
    }
}
```

### XXL-JOB 是什么？
分布式任务调度平台，可以管理定时任务的执行、监控、失败重试。

---

## 📚 知识点汇总

| 配置类 | 核心功能 | 技术点 |
|--------|----------|--------|
| GlobalCorsConfig | 跨域配置 | CORS |
| EncryptDecryptAop | 自动解密 | AOP、反射、SM2 |
| APIAuthorityFilter | 权限验证 | Filter、Token、Redis |
| FlagInterceptorConfig | Flag提取 | Interceptor、ThreadLocal |
| XssRequestFilter | XSS防护 | Filter |
| XxlJobConfig | 定时任务 | XXL-JOB |

## 🔗 调用关系图

```
请求进入
    ↓
XssRequestFilter (XSS过滤)
    ↓
APIAuthorityFilter (Token验证)
    ↓
FlagInterceptorConfig (提取flag)
    ↓
Controller (业务处理)
    ↓
EncryptDecryptAop (解密参数)
```
