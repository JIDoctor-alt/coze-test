# Java零基础小白教程 - 下半部分

---

## 第五篇：企业级框架

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### Maven/Gradle：你的外卖菜单

**一句话人话解释**：Maven/Gradle是帮你自动下载、管理项目所需工具包的工具。

**生活比喻**：
就像点外卖一样，你不需要自己去买菜做饭，只需要看菜单选择你想要的菜（依赖包），外卖员（Maven/Gradle）就会帮你配送所有原材料，连碗筷都给你准备好了。

**核心概念**：
- **pom.xml**：Maven的核心配置文件，就像外卖菜单，列出你需要什么菜（依赖）
- **build.gradle**：Gradle的配置文件，功能类似但语法更灵活
- **依赖管理**：自动下载jar包，解决版本冲突
- **生命周期**：clean（清理）、compile（编译）、test（测试）、package（打包）、install（安装）

**代码示例 - pom.xml**：
```xml
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.java</groupId>
    <artifactId>java-tutorial</artifactId>
    <version>1.0.0</version>
    
    <properties>
        <java.version>17</java.version>
    </properties>
    
    <!-- 依赖列表，就像菜单上的菜品 -->
    <dependencies>
        <!-- Spring Boot Starter -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <version>3.1.0</version>
        </dependency>
        
        <!-- MySQL驱动 -->
        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <version>8.0.33</version>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

**代码示例 - build.gradle**：
```gradle
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.1.0'
}

group = 'com.java'
version = '1.0.0'

repositories {
    mavenCentral() // 从Maven中央仓库下载依赖
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'mysql:mysql-connector-java:8.0.33'
    
    // 测试依赖
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}
```

**常见坑点**：
1. ❌ 依赖版本冲突，导致类找不到
2. ❌ 网络问题导致依赖下载失败（配置国内镜像源）
3. ❌ 忘记刷新IDE的Maven配置

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

**⚠️ 小白易懵点**：
为什么我的项目报红？→ 依赖没下载成功，点击IDE右侧的Maven面板，点击刷新按钮（⚡️图标）即可。

---

### Spring核心：IoC容器（中介所）

**一句话人话解释**：Spring帮你管理和创建对象，你不需要自己new对象。

**生活比喻**：
IoC（Inversion of Control，控制反转）就像房屋中介所。以前你自己找房子、自己签合同（自己new对象），现在告诉中介你要什么房子，中介帮你找好、签好合同，你直接住进去（使用对象）就行。

**核心概念**：
- **IoC容器**：Spring的核心容器，管理所有Bean对象的生命周期
- **Bean**：Spring管理的对象
- **ApplicationContext**：容器的主要接口

**代码示例**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
// 定义一个服务类
@Service // 告诉Spring：这是一个Bean，请帮我管理
public class UserService {
    public void login(String username, String password) {
        System.out.println("用户登录：" + username);
    }
}

// 定义控制器类
@RestController
public class LoginController {
    
    // 不需要 new UserService()，让Spring帮你注入
    private final UserService userService;
    
    // 构造器注入（推荐方式）
    @Autowired
    public LoginController(UserService userService) {
        this.userService = userService;
    }
    
    @GetMapping("/login")
    public String login() {
        userService.login("xiaoming", "123456");
        return "登录成功";
    }
}
```

**常见坑点**：
1. ❌ 忘记加@Component、@Service等注解，Bean创建失败
2. ❌ 两个Bean类型相同，Spring不知道注入哪个
3. ❌ 构造器注入时，没有@Autowired（Spring 4.3+可省略）

---

### DI依赖注入：@Autowired

**一句话人话解释**：DI（Dependency Injection）是Spring把你需要对象自动送给你，不用自己找。

**生活比喻**：
DI就像快递员送货上门。你下单（声明需要某个对象），快递员（Spring）把包裹（依赖对象）送到你家门口（注入到你的类中），你签收就能用了。

**核心概念**：
- **@Autowired**：自动装配注解，告诉Spring"帮我注入这个对象"
- **三种注入方式**：构造器注入（推荐）、Setter注入、字段注入（不推荐）

**代码示例 - 三种注入方式对比**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@Service
public class OrderService {
    
    private final ProductService productService;
    private final PaymentService paymentService;
    
    // ✅ 方式1：构造器注入（推荐）
    // 优点：确保对象创建时依赖就准备好，不可变，便于测试
    @Autowired
    public OrderService(ProductService productService, PaymentService paymentService) {
        this.productService = productService;
        this.paymentService = paymentService;
    }
    
    // ✅ 方式2：Setter注入
    // 优点：灵活，可随时修改
    private final InventoryService inventoryService;
    
    @Autowired
    public void setInventoryService(InventoryService inventoryService) {
        this.inventoryService = inventoryService;
    }
    
    // ⚠️ 方式3：字段注入（不推荐）
    // 缺点：无法设置final，测试困难，依赖外部容器
    @Autowired
    private ShippingService shippingService;
    
    public void createOrder(String productId) {
        // 直接使用，不需要new
        productService.getProduct(productId);
        paymentService.pay();
        inventoryService.reduceStock();
        shippingService.ship();
    }
}
```

**常见坑点**：
1. ❌ 字段注入导致无法单元测试
2. ❌ 循环依赖（A依赖B，B又依赖A）
3. ❌ 接口有多个实现类，注入失败（用@Qualifier指定）

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

**⚠️ 小白易懵点**：
@Autowired报错"NoUniqueBeanDefinitionException" → 接口有多个实现类，用@Qualifier("bean名称")指定要注入哪个。

---

### AOP切面：安检员

**一句话人话解释**：AOP（面向切面编程）在不修改原有代码的情况下，给程序添加额外功能（如日志、权限检查）。

**生活比喻**：
AOP就像小区的安检员或机场安检。无论你走哪个小区门、坐哪班飞机，安检员都会统一检查你的证件、行李（横切关注点），而不需要进入每家每户去加装摄像头。

**核心概念**：
- **切面（Aspect）**：包含横切逻辑的类
- **切点（Pointcut）**：定义在哪些方法上执行切面逻辑
- **通知（Advice）**：具体要执行的逻辑（前置、后置、环绕等）
- **连接点（Join Point）**：程序执行的某个位置（方法执行时）

**代码示例 - 日志切面**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
import org.aspectj.lang.annotation.*;
import org.aspectj.lang.ProceedingJoinPoint;
import org.springframework.stereotype.Component;

// 定义一个切面类
@Aspect
@Component
public class LoggingAspect {
    
    // 定义切点：拦截所有Service层的方法
    @Pointcut("execution(* com.java.service.*.*(..))")
    public void serviceMethods() {}
    
    // 前置通知：方法执行前
    @Before("serviceMethods()")
    public void beforeMethod() {
        System.out.println("🚀 方法准备执行...");
    }
    
    // 后置通知：方法执行后（无论成功失败）
    @After("serviceMethods()")
    public void afterMethod() {
        System.out.println("✅ 方法执行完毕");
    }
    
    // 返回通知：方法成功返回后
    @AfterReturning(pointcut = "serviceMethods()", returning = "result")
    public void afterReturning(Object result) {
        System.out.println("📦 方法返回值：" + result);
    }
    
    // 异常通知：方法抛出异常时
    @AfterThrowing(pointcut = "serviceMethods()", throwing = "exception")
    public void afterThrowing(Exception exception) {
        System.out.println("❌ 方法抛出异常：" + exception.getMessage());
    }
    
    // 环绕通知：可以完全控制方法的执行
    @Around("serviceMethods()")
    public Object aroundMethod(ProceedingJoinPoint joinPoint) throws Throwable {
        long startTime = System.currentTimeMillis();
        
        System.out.println("🔍 开始执行：" + joinPoint.getSignature().getName());
        
        // 执行目标方法
        Object result = joinPoint.proceed();
        
        long endTime = System.currentTimeMillis();
        System.out.println("⏱️ 执行耗时：" + (endTime - startTime) + "ms");
        
        return result;
    }
}
```

**代码示例 - 权限检查切面**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@Aspect
@Component
public class AuthAspect {
    
    // 拦截所有Controller的方法
    @Before("@within(org.springframework.web.bind.annotation.RestController)")
    public void checkAuth() {
        // 模拟获取当前用户
        String currentUser = getCurrentUser();
        
        if (currentUser == null) {
            throw new RuntimeException("未登录，请先登录");
        }
        
        System.out.println("✅ 用户：" + currentUser + " 通过权限检查");
    }
    
    private String getCurrentUser() {
        // 实际项目中从Session或JWT Token中获取
        return "xiaoming";
    }
}
```

**常见坑点**：
1. ❌ 切点表达式写错，拦截不到方法
2. ❌ 环绕通知忘记调用joinPoint.proceed()，导致目标方法不执行
3. ❌ private方法无法被AOP拦截（因为是通过代理实现的）

---

### SpringBoot自动配置：智能装修

**一句话人话解释**：SpringBoot根据你引入的依赖包，自动帮你配置好项目。

**生活比喻**：
SpringBoot自动配置就像智能装修公司。你告诉它"我要3室2厅"（引入依赖包），它自动帮你规划好水电、地板、墙壁、家具，你拎包就能住（启动即用）。

**核心概念**：
- **@SpringBootApplication**：启动类注解，包含自动配置
- **条件注解**：根据条件决定是否加载某个配置
- **Starter依赖**：简化依赖引入的一站式依赖包

**代码示例 - 启动类**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@SpringBootApplication // 核心注解，开启自动配置
public class JavaTutorialApplication {
    
    public static void main(String[] args) {
        // 启动SpringBoot应用
        SpringApplication.run(JavaTutorialApplication.class, args);
        System.out.println("🎉 SpringBoot应用启动成功！");
    }
}
```

**@SpringBootApplication包含的三个注解**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@SpringBootConfiguration // 标识这是配置类
@EnableAutoConfiguration // 开启自动配置（核心）
@ComponentScan // 自动扫描Bean
public @interface SpringBootApplication {
    // ...
}
```

**代码示例 - 自定义条件配置**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
// 自定义一个邮件服务
public interface EmailService {
    void sendEmail(String to, String subject, String content);
}

// 企业邮箱服务
@Service
@ConditionalOnProperty(name = "email.type", havingValue = "enterprise") // 当配置文件中email.type=enterprise时创建
public class EnterpriseEmailService implements EmailService {
    @Override
    public void sendEmail(String to, String subject, String content) {
        System.out.println("🏢 使用企业邮箱发送邮件到：" + to);
    }
}

// 免费邮箱服务
@Service
@ConditionalOnProperty(name = "email.type", havingValue = "free") // 当配置文件中email.type=free时创建
public class FreeEmailService implements EmailService {
    @Override
    public void sendEmail(String to, String subject, String content) {
        System.out.println("📧 使用免费邮箱发送邮件到：" + to);
    }
}

// 配置文件 application.yml
// email:
//   type: free
```

**常见坑点**：
1. ❌ 引入了多个Starter，自动配置冲突
2. ❌ 忘记在启动类所在的包下创建其他Bean，导致扫描不到
3. ❌ 条件注解的配置值写错

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

**⚠️ 小白易懵点**：
如何查看SpringBoot自动配置了什么？→ 启动时加 `--debug` 参数，或查看 `spring-boot-autoconfigure` 源码。

---

### MyBatis：翻译官

**一句话人话解释**：MyBatis帮你把Java对象转换成SQL语句，执行SQL后再把结果转回Java对象。

**生活比喻**：
MyBatis就像一位翻译官。你用中文（Java对象）跟他说话，他翻译成英文（SQL）跟数据库交流，拿到英文结果后再翻译成中文（Java对象）给你。

**核心概念**：
- **Mapper接口**：定义数据库操作的方法
- **映射文件**：写SQL语句的地方
- **注解方式**：直接在接口方法上写SQL（简单查询推荐）
- **参数映射**：#{}（预编译）和${}（字符串拼接，有SQL注入风险）

**代码示例 - 注解方式（推荐简单场景）**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
import org.apache.ibatis.annotations.*;

// Mapper接口
@Mapper // 告诉MyBatis这是一个数据库操作接口
public interface UserMapper {
    
    // 查询单个用户（使用#{}，防SQL注入）
    @Select("SELECT id, username, email FROM users WHERE id = #{id}")
    User findById(Long id);
    
    // 查询所有用户
    @Select("SELECT * FROM users")
    List<User> findAll();
    
    // 插入用户
    @Insert("INSERT INTO users(username, password, email) " +
            "VALUES(#{username}, #{password}, #{email})")
    @Options(useGeneratedKeys = true, keyProperty = "id") // 返回自增ID
    int insert(User user);
    
    // 更新用户
    @Update("UPDATE users SET email = #{email} WHERE id = #{id}")
    int updateEmail(@Param("id") Long id, @Param("email") String email);
    
    // 删除用户
    @Delete("DELETE FROM users WHERE id = #{id}")
    int deleteById(Long id);
}
```

**代码示例 - 映射文件方式（复杂查询推荐）**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
// Mapper接口
@Mapper
public interface OrderMapper {
    
    // 复杂查询：动态SQL
    List<Order> findOrders(OrderQuery query);
    
    // 批量插入
    int batchInsert(@Param("orders") List<Order> orders);
}
```

```xml
<!-- OrderMapper.xml -->
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" 
    "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.java.mapper.OrderMapper">
    
    <!-- 复杂查询：动态SQL -->
    <select id="findOrders" resultType="com.java.entity.Order">
        SELECT * FROM orders
        <where>
            <if test="userId != null">
                AND user_id = #{userId}
            </if>
            <if test="status != null">
                AND status = #{status}
            </if>
            <if test="startTime != null and endTime != null">
                AND create_time BETWEEN #{startTime} AND #{endTime}
            </if>
        </where>
        ORDER BY create_time DESC
    </select>
    
    <!-- 批量插入 -->
    <insert id="batchInsert">
        INSERT INTO orders(user_id, product_id, amount, total_price)
        VALUES
        <foreach collection="orders" item="order" separator=",">
            (#{order.userId}, #{order.productId}, #{order.amount}, #{order.totalPrice})
        </foreach>
    </insert>
</mapper>
```

**实体类**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@Data // Lombok自动生成getter/setter
public class User {
    private Long id;
    private String username;
    private String password;
    private String email;
    private LocalDateTime createTime;
}

@Data
public class Order {
    private Long id;
    private Long userId;
    private Long productId;
    private Integer amount;
    private BigDecimal totalPrice;
    private String status;
    private LocalDateTime createTime;
}

@Data
public class OrderQuery {
    private Long userId;
    private String status;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
}
```

**常见坑点**：
1. ❌ 使用${}导致SQL注入风险
2. ❌ Mapper.xml路径配置错误，找不到映射文件
3. ❌ 数据库字段名和Java属性名不一致（用@ResultMap或@Results处理）

---

### RESTful API设计：标准沟通协议

**一句话人话解释**：RESTful API是一种设计Web服务的标准方式，让前后端沟通更规范。

**生活比喻**：
RESTful API就像餐厅的点餐协议。每种菜品操作都有固定的指令格式：看菜单（GET）、点菜（POST）、改菜（PUT）、退菜（DELETE），大家都按这个协议来，不会乱套。

**核心概念**：
- **HTTP动词**：GET（查询）、POST（新增）、PUT（更新）、DELETE（删除）
- **资源**：URL表示的实体（如 /users、/orders）
- **状态码**：200成功、201创建、400请求错误、404未找到、500服务器错误
- **无状态**：每个请求包含所有信息，不依赖前一个请求

**代码示例 - RESTful Controller**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@RestController // 声明这是RESTful控制器，所有方法自动返回JSON
@RequestMapping("/api/users") // 基础路径
public class UserController {
    
    @Autowired
    private UserService userService;
    
    // GET /api/users/{id} - 查询单个用户
    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        User user = userService.findById(id);
        if (user == null) {
            return ResponseEntity.notFound().build(); // 404
        }
        return ResponseEntity.ok(user); // 200
    }
    
    // GET /api/users - 查询所有用户（支持分页）
    @GetMapping
    public ResponseEntity<Page<User>> getUsers(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        Page<User> users = userService.findAll(page, size);
        return ResponseEntity.ok(users);
    }
    
    // POST /api/users - 新增用户
    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody @Valid UserDTO userDTO) {
        User user = userService.create(userDTO);
        return ResponseEntity.status(201).body(user); // 201 Created
    }
    
    // PUT /api/users/{id} - 更新用户
    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(
            @PathVariable Long id,
            @RequestBody @Valid UserDTO userDTO) {
        User user = userService.update(id, userDTO);
        return ResponseEntity.ok(user);
    }
    
    // DELETE /api/users/{id} - 删除用户
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.delete(id);
        return ResponseEntity.noContent().build(); // 204 No Content
    }
}
```

**DTO（数据传输对象）**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@Data
public class UserDTO {
    @NotBlank(message = "用户名不能为空")
    private String username;
    
    @NotBlank(message = "密码不能为空")
    @Size(min = 6, max = 20, message = "密码长度6-20位")
    private String password;
    
    @Email(message = "邮箱格式不正确")
    private String email;
}
```

**统一返回结果封装**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@Data
@AllArgsConstructor
public class Result<T> {
    private int code;        // 状态码
    private String message;  // 提示信息
    private T data;          // 返回数据
    
    public static <T> Result<T> success(T data) {
        return new Result<>(200, "success", data);
    }
    
    public static <T> Result<T> error(String message) {
        return new Result<>(500, message, null);
    }
}
```

**常见坑点**：
1. ❌ HTTP动词使用不规范（用GET做修改操作）
2. ❌ 返回状态码错误（成功返回200，失败还返回200）
3. ❌ URL设计不规范（应该用资源名词，不要用动词）

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

**⚠️ 小白易懵点**：
什么时候用@PathVariable，什么时候用@RequestParam？→ URL路径中的一部分（如 /users/{id}）用@PathVariable；查询参数（如 /users?page=1）用@RequestParam。

---

### Spring Security权限框架入门

**一句话人话解释**：Spring Security帮你搞定登录认证和权限控制，保护你的接口。

**生活比喻**：
Spring Security就像小区门卫系统。业主（登录用户）有门禁卡，可以进小区大门；访客（普通用户）需要登记；陌生人（未登录）直接拦在门外。不同门禁卡（权限）能进不同的楼栋（接口）。

**核心概念**：
- **认证（Authentication）**：确认你是谁（登录）
- **授权（Authorization）**：确认你能做什么（权限）
- **SecurityContextHolder**：存放当前登录用户信息
- **@PreAuthorize**：方法级别的权限控制

**代码示例 - Security配置**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // 开启跨域支持
            .cors(cors -> cors.disable())
            // 禁用CSRF（前后端分离项目常用）
            .csrf(csrf -> csrf.disable())
            
            // 配置请求授权
            .authorizeHttpRequests(auth -> auth
                // 公开接口（不需要登录）
                .requestMatchers("/api/public/**", "/login").permitAll()
                // 管理员接口
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                // 普通用户接口
                .requestMatchers("/api/user/**").hasRole("USER")
                // 其他请求需要登录
                .anyRequest().authenticated()
            )
            
            // 自定义登录页面
            .formLogin(form -> form
                .loginPage("/login")
                .defaultSuccessUrl("/home")
                .permitAll()
            )
            
            // 自定义登出
            .logout(logout -> logout
                .logoutUrl("/logout")
                .logoutSuccessUrl("/login?logout")
                .permitAll()
            );
        
        return http.build();
    }
    
    // 密码编码器（必须配置）
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

**代码示例 - 用户登录服务**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@Service
public class AuthService {
    
    @Autowired
    private AuthenticationManager authenticationManager;
    
    @Autowired
    private PasswordEncoder passwordEncoder;
    
    // 用户登录
    public String login(String username, String password) {
        // 构造认证信息
        UsernamePasswordAuthenticationToken token = 
            new UsernamePasswordAuthenticationToken(username, password);
        
        // 执行认证（Spring Security会自动调用UserDetailsService）
        Authentication authentication = authenticationManager.authenticate(token);
        
        // 认证成功，存入SecurityContext
        SecurityContextHolder.getContext().setAuthentication(authentication);
        
        // 生成Token（实际项目用JWT）
        return "生成的Token";
    }
    
    // 用户注册
    public void register(User user) {
        // 密码加密
        String encodedPassword = passwordEncoder.encode(user.getPassword());
        user.setPassword(encodedPassword);
        
        // 保存到数据库...
    }
}
```

**代码示例 - UserDetailsService（从数据库加载用户）**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@Service
public class CustomUserDetailsService implements UserDetailsService {
    
    @Autowired
    private UserMapper userMapper;
    
    @Override
    public UserDetails loadUserByUsername(String username) 
            throws UsernameNotFoundException {
        
        // 从数据库查询用户
        User user = userMapper.findByUsername(username);
        
        if (user == null) {
            throw new UsernameNotFoundException("用户不存在：" + username);
        }
        
        // 构造Spring Security的User对象
        return org.springframework.security.core.userdetails.User
                .builder()
                .username(user.getUsername())
                .password(user.getPassword())
                .roles("USER") // 角色列表
                .build();
    }
}
```

**代码示例 - 方法级权限控制**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@RestController
@RequestMapping("/api/admin")
public class AdminController {
    
    // 只有管理员角色能访问
    @PreAuthorize("hasRole('ADMIN')")
    @GetMapping("/users")
    public List<User> getAllUsers() {
        return userService.findAll();
    }
    
    // 需要ADMIN或MANAGER角色
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER')")
    @PostMapping("/users")
    public User createUser(@RequestBody UserDTO userDTO) {
        return userService.create(userDTO);
    }
    
    // 需要ADMIN权限 AND 拥有deleteUser权限
    @PreAuthorize("hasRole('ADMIN') and hasAuthority('deleteUser')")
    @DeleteMapping("/users/{id}")
    public void deleteUser(@PathVariable Long id) {
        userService.delete(id);
    }
}
```

**常见坑点**：
1. ❌ 忘记配置PasswordEncoder，登录失败
2. ❌ 权限注解不生效（需要在配置类上加@EnableMethodSecurity）
3. ❌ 角色名要有"ROLE_"前缀，Spring Security会自动处理

---

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

**💡 一句话总结**：
企业级框架让你的开发效率起飞——Maven/Gradle管理依赖、Spring管理对象、MyBatis处理数据库、Security保护安全，你只需要写业务逻辑。

---

## 第六篇：数据库与中间件

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### JDBC基础连接流程：6步打通数据库

**一句话人话解释**：JDBC是Java连接数据库的标准方式，虽然繁琐但必须掌握原理。

**生活比喻**：
JDBC就像打电话的6个步骤：1.找到电话（加载驱动）→ 2.拨号（建立连接）→ 3.拿起话筒（创建语句）→ 4.说话（执行SQL）→ 5.听到回应（处理结果）→ 6.挂断（关闭资源）。

**核心概念**：
- **Driver**：数据库驱动程序
- **Connection**：数据库连接
- **Statement**：执行SQL语句的对象
- **ResultSet**：查询结果集
- **PreparedStatement**：预编译语句（推荐，防SQL注入）

**代码示例 - JDBC基础操作**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
import java.sql.*;

public class JDBCDemo {
    
    // 数据库配置
    private static final String URL = "jdbc:mysql://localhost:3306/java_tutorial?useSSL=false&serverTimezone=UTC";
    private static final String USERNAME = "root";
    private static final String PASSWORD = "123456";
    
    public static void main(String[] args) {
        Connection connection = null;
        PreparedStatement statement = null;
        ResultSet resultSet = null;
        
        try {
            // 步骤1：加载驱动（新版本JDBC可省略）
            Class.forName("com.mysql.cj.jdbc.Driver");
            System.out.println("✅ 驱动加载成功");
            
            // 步骤2：建立连接
            connection = DriverManager.getConnection(URL, USERNAME, PASSWORD);
            System.out.println("✅ 数据库连接成功");
            
            // 步骤3：创建PreparedStatement（推荐使用）
            String sql = "SELECT id, username, email FROM users WHERE id = ?";
            statement = connection.prepareStatement(sql);
            statement.setInt(1, 1); // 设置参数，防止SQL注入
            
            // 步骤4：执行查询
            resultSet = statement.executeQuery();
            
            // 步骤5：处理结果
            while (resultSet.next()) {
                Long id = resultSet.getLong("id");
                String username = resultSet.getString("username");
                String email = resultSet.getString("email");
                
                System.out.println("用户ID：" + id);
                System.out.println("用户名：" + username);
                System.out.println("邮箱：" + email);
            }
            
            // 步骤6：关闭资源（在finally中统一关闭）
            
        } catch (ClassNotFoundException e) {
            System.out.println("❌ 驱动加载失败：" + e.getMessage());
        } catch (SQLException e) {
            System.out.println("❌ 数据库操作失败：" + e.getMessage());
        } finally {
            // 步骤6：按创建的逆序关闭资源
            try {
                if (resultSet != null) resultSet.close();
                if (statement != null) statement.close();
                if (connection != null) connection.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }
}
```

**代码示例 - 插入数据**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
public void insertUser(String username, String password, String email) {
    String sql = "INSERT INTO users(username, password, email) VALUES(?, ?, ?)";
    
    try (Connection conn = DriverManager.getConnection(URL, USERNAME, PASSWORD);
         PreparedStatement stmt = conn.prepareStatement(sql)) {
        
        // 设置参数
        stmt.setString(1, username);
        stmt.setString(2, password);
        stmt.setString(3, email);
        
        // 执行插入（返回影响行数）
        int rows = stmt.executeUpdate();
        System.out.println("✅ 插入成功，影响行数：" + rows);
        
    } catch (SQLException e) {
        System.out.println("❌ 插入失败：" + e.getMessage());
    }
}
```

**代码示例 - 批量操作**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
public void batchInsert(List<User> users) {
    String sql = "INSERT INTO users(username, password, email) VALUES(?, ?, ?)";
    
    try (Connection conn = DriverManager.getConnection(URL, USERNAME, PASSWORD);
         PreparedStatement stmt = conn.prepareStatement(sql)) {
        
        // 关闭自动提交，开启事务
        conn.setAutoCommit(false);
        
        // 批量添加参数
        for (User user : users) {
            stmt.setString(1, user.getUsername());
            stmt.setString(2, user.getPassword());
            stmt.setString(3, user.getEmail());
            stmt.addBatch(); // 添加到批处理
        }
        
        // 执行批处理
        int[] results = stmt.executeBatch();
        System.out.println("✅ 批量插入成功，影响行数：" + results.length);
        
        // 提交事务
        conn.commit();
        
    } catch (SQLException e) {
        System.out.println("❌ 批量插入失败：" + e.getMessage());
    }
}
```

**常见坑点**：
1. ❌ 忘记关闭连接，导致连接池耗尽
2. ❌ 使用Statement导致SQL注入风险
3. ❌ 忘记设置serverTimezone导致连接失败

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

**⚠️ 小白易懵点**：
Statement和PreparedStatement有什么区别？→ Statement直接拼接SQL字符串，有注入风险；PreparedStatement预编译SQL，用？占位符，安全高效。

---

### 事务ACID：银行转账的保障

**一句话人话解释**：事务保证一组数据库操作要么全部成功，要么全部失败，不会出现中间状态。

**生活比喻**：
事务就像银行转账。A转100元给B，必须保证：A扣100元成功 AND B加100元成功。如果A扣了钱但B没加上，这个操作要全部回滚（取消），不能出现"钱凭空消失"的情况。

**核心概念 - ACID**：
- **原子性（Atomicity）**：操作要么全部成功，要么全部失败
- **一致性（Consistency）**：事务前后数据保持一致
- **隔离性（Isolation）**：并发事务互不干扰
- **持久性（Durability）**：事务提交后永久生效

**代码示例 - 手动事务控制**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
public void transfer(Long fromId, Long toId, BigDecimal amount) {
    Connection conn = null;
    
    try {
        // 获取连接
        conn = dataSource.getConnection();
        
        // 关闭自动提交（开启事务）
        conn.setAutoCommit(false);
        
        // 步骤1：检查转账人余额
        BigDecimal balance = getBalance(conn, fromId);
        if (balance.compareTo(amount) < 0) {
            throw new RuntimeException("余额不足");
        }
        
        // 步骤2：扣款
        updateBalance(conn, fromId, balance.subtract(amount));
        
        // 步骤3：收款
        BigDecimal toBalance = getBalance(conn, toId);
        updateBalance(conn, toId, toBalance.add(amount));
        
        // 全部成功，提交事务
        conn.commit();
        System.out.println("✅ 转账成功");
        
    } catch (Exception e) {
        // 出现异常，回滚事务
        try {
            if (conn != null) {
                conn.rollback();
                System.out.println("❌ 转账失败，已回滚：" + e.getMessage());
            }
        } catch (SQLException ex) {
            ex.printStackTrace();
        }
    } finally {
        // 恢复自动提交
        if (conn != null) {
            try {
                conn.setAutoCommit(true);
                conn.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }
}

private void updateBalance(Connection conn, Long userId, BigDecimal newBalance) 
        throws SQLException {
    String sql = "UPDATE accounts SET balance = ? WHERE user_id = ?";
    PreparedStatement stmt = conn.prepareStatement(sql);
    stmt.setBigDecimal(1, newBalance);
    stmt.setLong(2, userId);
    stmt.executeUpdate();
}

private BigDecimal getBalance(Connection conn, Long userId) throws SQLException {
    String sql = "SELECT balance FROM accounts WHERE user_id = ?";
    PreparedStatement stmt = conn.prepareStatement(sql);
    stmt.setLong(1, userId);
    ResultSet rs = stmt.executeQuery();
    
    if (rs.next()) {
        return rs.getBigDecimal("balance");
    }
    return BigDecimal.ZERO;
}
```

**代码示例 - Spring事务注解**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@Service
@Transactional // 类级别事务，所有方法都受事务控制
public class TransferService {
    
    @Autowired
    private AccountMapper accountMapper;
    
    // 转账方法（默认使用REQUIRED传播级别）
    @Transactional(rollbackFor = Exception.class) // 遇到异常就回滚
    public void transfer(Long fromId, Long toId, BigDecimal amount) {
        // 查询余额
        BigDecimal fromBalance = accountMapper.getBalance(fromId);
        if (fromBalance.compareTo(amount) < 0) {
            throw new RuntimeException("余额不足");
        }
        
        // 扣款
        accountMapper.updateBalance(fromId, fromBalance.subtract(amount));
        
        // 收款
        BigDecimal toBalance = accountMapper.getBalance(toId);
        accountMapper.updateBalance(toId, toBalance.add(amount));
        
        System.out.println("✅ 转账成功");
    }
    
    // 只读事务，不进行写操作（优化性能）
    @Transactional(readOnly = true)
    public BigDecimal queryBalance(Long userId) {
        return accountMapper.getBalance(userId);
    }
    
    // 设置事务隔离级别
    @Transactional(isolation = Isolation.READ_COMMITTED)
    public void saveOrder(Order order) {
        // ...
    }
}
```

**事务隔离级别**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
public enum Isolation {
    READ_UNCOMMITTED,    // 读未提交：可能读到脏数据
    READ_COMMITTED,      // 读已提交：解决脏读问题（MySQL默认）
    REPEATABLE_READ,     // 可重复读：解决不可重复读（InnoDB默认）
    SERIALIZABLE         // 串行化：最高隔离级别，性能最差
}
```

**常见坑点**：
1. ❌ 忘记设置rollbackFor，运行时异常不回滚
2. ❌ 同一类中调用事务方法，事务失效（因为通过代理调用）
3. ❌ 隔离级别设置过高，导致性能下降

---

### 连接池：高效的数据库快递站

**一句话人话解释**：连接池预先创建好一批数据库连接，需要时直接取用，用完归还，避免频繁创建销毁连接。

**生活比喻**：
连接池就像共享单车或共享充电宝。提前把车/充电宝准备好（创建连接），你需要时扫码取用，用完还回去，其他人可以继续用。不用每次都买新车/充电宝（新建连接）。

**核心概念**：
- **连接池**：管理数据库连接的容器
- **初始连接数**：连接池启动时创建的连接数量
- **最大连接数**：连接池最多持有的连接数
- **空闲连接数**：空闲时保留的连接数
- **等待时间**：获取连接时的最长等待时间

**代码示例 - HikariCP配置**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import javax.sql.DataSource;

@Configuration
public class DataSourceConfig {
    
    @Bean
    public DataSource dataSource() {
        HikariConfig config = new HikariConfig();
        
        // 基本配置
        config.setJdbcUrl("jdbc:mysql://localhost:3306/java_tutorial");
        config.setUsername("root");
        config.setPassword("123456");
        config.setDriverClassName("com.mysql.cj.jdbc.Driver");
        
        // 连接池配置
        config.setMinimumIdle(5);           // 最小空闲连接数
        config.setMaximumPoolSize(20);       // 最大连接数
        config.setConnectionTimeout(30000);  // 连接超时时间（毫秒）
        config.setIdleTimeout(600000);       // 空闲超时时间（10分钟）
        config.setMaxLifetime(1800000);      // 连接最大生命周期（30分钟）
        
        // 性能优化
        config.setConnectionTestQuery("SELECT 1"); // 测试连接是否有效
        config.setPoolName("HikariPool-JavaTutorial");
        
        return new HikariDataSource(config);
    }
}
```

**application.yml配置方式**：
```yaml
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/java_tutorial?useSSL=false&serverTimezone=UTC
    username: root
    password: 123456
    driver-class-name: com.mysql.cj.jdbc.Driver
    
    # HikariCP连接池配置
    hikari:
      minimum-idle: 5              # 最小空闲连接
      maximum-pool-size: 20        # 最大连接数
      connection-timeout: 30000    # 连接超时（毫秒）
      idle-timeout: 600000         # 空闲超时（毫秒）
      max-lifetime: 1800000        # 连接最大生命周期（毫秒）
      pool-name: HikariPool-Dev    # 连接池名称
      connection-test-query: SELECT 1  # 测试查询
```

**代码示例 - Druid配置**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
import com.alibaba.druid.pool.DruidDataSource;

@Configuration
public class DruidConfig {
    
    @Bean
    public DataSource dataSource() {
        DruidDataSource dataSource = new DruidDataSource();
        
        // 基本配置
        dataSource.setUrl("jdbc:mysql://localhost:3306/java_tutorial");
        dataSource.setUsername("root");
        dataSource.setPassword("123456");
        dataSource.setDriverClassName("com.mysql.cj.jdbc.Driver");
        
        // 连接池配置
        dataSource.setInitialSize(5);        // 初始连接数
        dataSource.setMinIdle(5);            // 最小空闲连接数
        dataSource.setMaxActive(20);         // 最大活跃连接数
        dataSource.setMaxWait(60000);       // 获取连接最大等待时间
        
        // 连接有效性检查
        dataSource.setValidationQuery("SELECT 1");
        dataSource.setTestWhileIdle(true);
        dataSource.setTestOnBorrow(false);
        dataSource.setTestOnReturn(false);
        
        // 监控统计配置
        dataSource.setFilters("stat,wall"); // 开启统计和防火墙
        
        return dataSource;
    }
    
    // 配置Druid监控页面
    @Bean
    public ServletRegistrationBean<StatViewServlet> druidStatViewServlet() {
        ServletRegistrationBean<StatViewServlet> registrationBean = 
            new ServletRegistrationBean<>(new StatViewServlet(), "/druid/*");
        
        // 配置监控页面访问账号密码
        registrationBean.addInitParameter("loginUsername", "admin");
        registrationBean.addInitParameter("loginPassword", "admin");
        
        return registrationBean;
    }
}
```

**常见坑点**：
1. ❌ 连接池大小设置不合理（太小导致等待，太大浪费资源）
2. ❌ 忘记关闭连接，导致连接泄漏
3. ❌ 连接长时间未使用，被数据库关闭

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

**⚠️ 小白易懵点**：
连接池的连接用完不用close吗？→ 要close，但这不是真的关闭，而是归还到连接池，供其他人使用。

---

### Redis缓存入门：超级快的内存数据库

**一句话人话解释**：Redis是存内存里的数据库，速度比硬盘数据库快几十倍，常用来做缓存。

**生活比喻**：
Redis就像你的背包（内存），东西一伸手就能拿到；而MySQL像家里的仓库（硬盘），东西多但拿起来慢。常用的东西放背包（缓存），不常用的放仓库（数据库）。

**核心概念**：
- **String**：字符串类型（最常用）
- **Hash**：哈希表（类似Java Map）
- **List**：列表（类似Java List）
- **Set**：集合（无序不重复）
- **ZSet**：有序集合（带分数的集合）

**代码示例 - Redis配置与使用**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.StringRedisTemplate;

@Configuration
public class RedisConfig {
    
    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(factory);
        
        // 设置key的序列化方式
        template.setKeySerializer(new StringRedisSerializer());
        template.setHashKeySerializer(new StringRedisSerializer());
        
        // 设置value的序列化方式
        template.setValueSerializer(new GenericJackson2JsonRedisSerializer());
        template.setHashValueSerializer(new GenericJackson2JsonRedisSerializer());
        
        return template;
    }
}
```

**代码示例 - String操作**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@Service
public class UserService {
    
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;
    
    @Autowired
    private UserMapper userMapper;
    
    public User getUser(Long userId) {
        String key = "user:" + userId;
        
        // 先从缓存获取
        User user = (User) redisTemplate.opsForValue().get(key);
        
        if (user != null) {
            System.out.println("✅ 从缓存获取用户：" + userId);
            return user;
        }
        
        // 缓存没有，查询数据库
        System.out.println("🔍 查询数据库...");
        user = userMapper.findById(userId);
        
        if (user != null) {
            // 存入缓存，设置30分钟过期
            redisTemplate.opsForValue().set(key, user, 30, TimeUnit.MINUTES);
            System.out.println("✅ 已存入缓存");
        }
        
        return user;
    }
    
    public void updateUser(User user) {
        // 更新数据库
        userMapper.update(user);
        
        // 删除缓存
        String key = "user:" + user.getId();
        redisTemplate.delete(key);
        System.out.println("✅ 已更新数据库并删除缓存");
    }
}
```

**代码示例 - Hash操作**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@Service
public class CartService {
    
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;
    
    // 添加商品到购物车
    public void addToCart(Long userId, Long productId, Integer quantity) {
        String cartKey = "cart:" + userId;
        
        redisTemplate.opsForHash().put(cartKey, String.valueOf(productId), quantity);
        System.out.println("✅ 已添加到购物车");
    }
    
    // 获取购物车所有商品
    public Map<Object, Object> getCart(Long userId) {
        String cartKey = "cart:" + userId;
        return redisTemplate.opsForHash().entries(cartKey);
    }
    
    // 删除购物车商品
    public void removeFromCart(Long userId, Long productId) {
        String cartKey = "cart:" + userId;
        redisTemplate.opsForHash().delete(cartKey, String.valueOf(productId));
        System.out.println("✅ 已从购物车移除");
    }
}
```

**代码示例 - List操作（消息队列）**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@Service
public class MessageQueueService {
    
    @Autowired
    private StringRedisTemplate stringRedisTemplate;
    
    private static final String QUEUE_KEY = "message:queue";
    
    // 生产者：发送消息
    public void sendMessage(String message) {
        // 左推（LPUSH）
        stringRedisTemplate.opsForList().leftPush(QUEUE_KEY, message);
        System.out.println("✅ 消息已发送：" + message);
    }
    
    // 消费者：接收消息
    public String receiveMessage() {
        // 右弹（BRPOP），阻塞等待
        return stringRedisTemplate.opsForList().rightPop(QUEUE_KEY);
    }
}
```

**代码示例 - Set操作（标签系统）**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@Service
public class TagService {
    
    @Autowired
    private StringRedisTemplate stringRedisTemplate;
    
    // 添加标签
    public void addTags(Long userId, String... tags) {
        String key = "user:tags:" + userId;
        stringRedisTemplate.opsForSet().add(key, tags);
    }
    
    // 获取所有标签
    public Set<String> getTags(Long userId) {
        String key = "user:tags:" + userId;
        return stringRedisTemplate.opsForSet().members(key);
    }
    
    // 查找共同标签
    public Set<String> findCommonTags(Long userId1, Long userId2) {
        String key1 = "user:tags:" + userId1;
        String key2 = "user:tags:" + userId2;
        return stringRedisTemplate.opsForSet().intersect(key1, key2);
    }
}
```

**代码示例 - ZSet操作（排行榜）**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@Service
public class RankingService {
    
    @Autowired
    private StringRedisTemplate stringRedisTemplate;
    
    private static final String RANKING_KEY = "game:ranking";
    
    // 增加分数
    public void addScore(Long userId, int score) {
        stringRedisTemplate.opsForZSet().add(RANKING_KEY, String.valueOf(userId), score);
    }
    
    // 获取排名
    public Long getRank(Long userId) {
        return stringRedisTemplate.opsForZSet().reverseRank(RANKING_KEY, String.valueOf(userId));
    }
    
    // 获取前10名
    public Set<String> getTop10() {
        return stringRedisTemplate.opsForZSet().reverseRange(RANKING_KEY, 0, 9);
    }
    
    // 获取用户分数
    public Double getScore(Long userId) {
        return stringRedisTemplate.opsForZSet().score(RANKING_KEY, String.valueOf(userId));
    }
}
```

**Redis常用命令**：
```
# String操作
SET key value            # 设置键值
GET key                  # 获取值
INCR key                 # 自增
EXPIRE key seconds       # 设置过期时间

# Hash操作
HSET key field value     # 设置哈希字段
HGET key field           # 获取哈希字段
HGETALL key              # 获取所有字段
HDEL key field           # 删除字段

# List操作
LPUSH key value          # 左推
RPUSH key value          # 右推
LPOP key                 # 左弹
RPOP key                 # 右弹

# Set操作
SADD key member          # 添加成员
SMEMBERS key             # 获取所有成员
SINTER key1 key2         # 求交集

# ZSet操作
ZADD key score member    # 添加成员和分数
ZREVRANGE key start stop # 反向获取排名
ZSCORE key member        # 获取分数
```

**常见坑点**：
1. ❌ 忘记设置过期时间，导致内存泄漏
2. ❌ 缓存和数据库数据不一致
3. ❌ 大key导致Redis阻塞

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

**⚠️ 小白易懵点**：
StringRedisTemplate和RedisTemplate有什么区别？→ StringRedisTemplate的key和value都是String，序列化简单；RedisTemplate支持任意对象，需要配置序列化方式。

---

### 消息队列：快递站解耦系统

**一句话人话解释**：消息队列是一个中间件，让发送方和接收方解耦，提高系统可靠性。

**生活比喻**：
消息队列就像快递站。寄件人（生产者）把包裹放到快递站就完事了，不用等收件人（消费者）立即取件。快递站帮你存包裹，收件人自己来取。就算收件人不在家，快递站也会帮他保管，不会丢。

**核心概念**：
- **生产者（Producer）**：发送消息的一方
- **消费者（Consumer）**：接收消息的一方
- **队列（Queue）**：存放消息的地方
- **交换机（Exchange）**：消息路由器（RabbitMQ）
- **发布订阅模式**：一个消息，多个消费者都能收到

**代码示例 - RabbitMQ配置**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
import org.springframework.amqp.core.*;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfig {
    
    public static final String QUEUE_NAME = "order.queue";
    public static final String EXCHANGE_NAME = "order.exchange";
    public static final String ROUTING_KEY = "order.created";
    
    // 声明队列
    @Bean
    public Queue orderQueue() {
        return QueueBuilder.durable(QUEUE_NAME).build();
    }
    
    // 声明交换机
    @Bean
    public TopicExchange orderExchange() {
        return new TopicExchange(EXCHANGE_NAME);
    }
    
    // 绑定队列和交换机
    @Bean
    public Binding binding(Queue orderQueue, TopicExchange orderExchange) {
        return BindingBuilder.bind(orderQueue)
                .to(orderExchange)
                .with(ROUTING_KEY);
    }
}
```

**代码示例 - 生产者**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class OrderProducer {
    
    @Autowired
    private RabbitTemplate rabbitTemplate;
    
    // 发送订单消息
    public void sendOrderMessage(Order order) {
        // 转换为JSON发送
        rabbitTemplate.convertAndSend(
            RabbitMQConfig.EXCHANGE_NAME, 
            RabbitMQConfig.ROUTING_KEY, 
            order
        );
        
        System.out.println("✅ 订单消息已发送：" + order.getId());
    }
}
```

**代码示例 - 消费者**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Service;

@Service
public class OrderConsumer {
    
    @Autowired
    private NotificationService notificationService;
    
    // 监听队列，自动消费消息
    @RabbitListener(queues = RabbitMQConfig.QUEUE_NAME)
    public void handleOrderMessage(Order order) {
        System.out.println("📦 收到订单消息：" + order.getId());
        
        try {
            // 处理订单：发送通知
            notificationService.sendOrderNotification(order);
            
            System.out.println("✅ 订单处理成功");
            
        } catch (Exception e) {
            System.out.println("❌ 订单处理失败：" + e.getMessage());
            // 可以选择重试或进入死信队列
        }
    }
}
```

**代码示例 - 发布订阅模式（广播）**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@Configuration
public class FanoutExchangeConfig {
    
    public static final String FANOUT_QUEUE_1 = "fanout.queue.1";
    public static final String FANOUT_QUEUE_2 = "fanout.queue.2";
    public static final String FANOUT_EXCHANGE = "fanout.exchange";
    
    // 队列1
    @Bean
    public Queue fanoutQueue1() {
        return new Queue(FANOUT_QUEUE_1);
    }
    
    // 队列2
    @Bean
    public Queue fanoutQueue2() {
        return new Queue(FANOUT_QUEUE_2);
    }
    
    // 广播交换机
    @Bean
    public FanoutExchange fanoutExchange() {
        return new FanoutExchange(FANOUT_EXCHANGE);
    }
    
    // 绑定队列1
    @Bean
    public Binding binding1(Queue fanoutQueue1, FanoutExchange fanoutExchange) {
        return BindingBuilder.bind(fanoutQueue1).to(fanoutExchange);
    }
    
    // 绑定队列2
    @Bean
    public Binding binding2(Queue fanoutQueue2, FanoutExchange fanoutExchange) {
        return BindingBuilder.bind(fanoutQueue2).to(fanoutExchange);
    }
}
```

**消费者监听两个队列**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@Service
public class NotificationConsumer {
    
    // 消费者1：接收短信通知
    @RabbitListener(queues = FanoutExchangeConfig.FANOUT_QUEUE_1)
    public void handleSmsNotification(String message) {
        System.out.println("📱 发送短信：" + message);
    }
    
    // 消费者2：接收邮件通知
    @RabbitListener(queues = FanoutExchangeConfig.FANOUT_QUEUE_2)
    public void handleEmailNotification(String message) {
        System.out.println("📧 发送邮件：" + message);
    }
}
```

**常见坑点**：
1. ❌ 消息重复消费（幂等性设计）
2. ❌ 消息丢失（持久化配置）
3. ❌ 消费速度跟不上生产速度（队列积压）

---

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

**💡 一句话总结**：
数据库与中间件让你的系统更强大——JDBC连接数据库、事务保证数据一致性、连接池提高性能、Redis加速查询、消息队列解耦系统。

---

## 第七篇：开发工具链

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### Git版本控制：游戏存档管理

**一句话人话解释**：Git帮你记录代码的所有历史版本，随时可以回退到任意版本。

**生活比喻**：
Git就像游戏的存档系统。你玩到某个关卡，存个档（commit），万一后面玩崩了，可以读档回到之前的状态（checkout）。还能存多个档（branch），从不同路线探索游戏。

**核心概念**：
- **仓库（Repository）**：存放代码的地方
- **工作区（Working Directory）**：你正在编辑的文件
- **暂存区（Staging Area）**：准备提交的文件
- **版本库（Repository）**：已提交的历史记录
- **分支（Branch）**：并行的开发线
- **合并（Merge）**：把两个分支合并

**常用Git命令**：
```bash
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
# 初始化仓库
git init

# 克隆远程仓库
git clone https://github.com/username/repository.git

# 查看状态
git status

# 添加文件到暂存区
git add .                    # 添加所有文件
git add file.java           # 添加单个文件

# 提交到本地仓库
git commit -m "feat: 添加用户登录功能"

# 查看提交历史
git log
git log --oneline           # 简洁显示
git log --graph             # 图形化显示

# 查看差异
git diff                    # 工作区vs暂存区
git diff --staged           # 暂存区vs版本库

# 分支操作
git branch                  # 查看分支
git branch feature-login    # 创建分支
git checkout feature-login  # 切换分支
git checkout -b dev         # 创建并切换到新分支
git branch -d feature-login # 删除分支

# 合并分支
git merge feature-login      # 合并feature-login到当前分支

# 推送到远程仓库
git remote add origin https://github.com/username/repo.git
git push -u origin master
git push origin feature-login  # 推送分支

# 拉取远程更新
git pull                    # 拉取并合并
git fetch                  # 只拉取不合并

# 回退版本
git reset --hard HEAD~1     # 回退到上一个版本
git reset --hard abc123     # 回退到指定版本
```

**代码示例 - Git工作流**：
```bash
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
# 1. 克隆项目
git clone https://github.com/username/java-tutorial.git
cd java-tutorial

# 2. 创建功能分支
git checkout -b feature/user-login

# 3. 修改代码
echo "// 登录功能代码" > UserService.java

# 4. 查看状态
git status

# 5. 添加到暂存区
git add UserService.java

# 6. 提交
git commit -m "feat: 添加用户登录功能"

# 7. 推送到远程
git push -u origin feature/user-login

# 8. 在GitHub上创建Pull Request

# 9. 合并后拉取最新代码
git checkout master
git pull origin master

# 10. 删除已合并的分支
git branch -d feature/user-login
```

**Git工作流图解**：
```
工作区 ──git add──> 暂存区 ──git commit──> 版本库
   ↓                                               ↓
编辑文件                                      git push
                                                   ↓
                                              远程仓库
```

**常见坑点**：
1. ❌ 忘记add就commit，提交内容不对
2. ❌ 冲突解决错误，代码丢失
3. ❌ 强制推送（git push -f），覆盖他人代码

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

**⚠️ 小白易懵点**：
git add和git commit的区别？→ git add把文件放到暂存区（准备提交），git commit把暂存区的文件保存为版本（正式提交）。就像打草稿和正式发文。

---

### IDEA常用快捷键与调试

**一句话人话解释**：熟练使用IDEA快捷键和调试功能，让你的开发效率提升数倍。

**生活比喻**：
IDEA快捷键就像开车用的方向盘、油门、刹车，熟练了就不用看路标（鼠标点菜单）。调试就像开车时看仪表盘，发现异常及时处理，避免抛锚。

**核心概念**：
- **断点**：让程序暂停的位置
- **单步执行**：一行一行执行代码
- **变量监视**：实时查看变量值
- **表达式求值**：执行自定义代码片段

**常用快捷键（Windows/Linux）**：
```
Ctrl + Space            代码补全
Ctrl + Shift + Enter    自动补全分号和括号
Ctrl + Alt + L          格式化代码
Ctrl + D                复制当前行
Ctrl + Y                删除当前行
Ctrl + /                注释/取消注释
Ctrl + F                查找
Ctrl + R                替换
Ctrl + Shift + F        全局查找
Ctrl + Shift + R        全局替换
Alt + Enter             快速修复
Alt + Insert            生成代码（getter/setter等）
Ctrl + O                重写方法
Ctrl + I                实现接口方法
Ctrl + N                查找类
Ctrl + Shift + N        查找文件
Ctrl + Shift + A        查找动作
F2                      下一个高亮错误
Ctrl + Alt + Left       返回上一个位置
Ctrl + Alt + Right      前进到下一个位置
Ctrl + Shift + F12      隐藏/显示所有面板
```

**调试快捷键**：
```
F8                      Step Over（单步跳过）
F7                      Step Into（单步进入）
Shift + F7              Smart Step Into（智能进入）
Shift + F8              Step Out（跳出）
F9                      Resume（继续运行）
Ctrl + F8               添加/删除断点
Ctrl + Shift + F8       查看所有断点
```

**代码示例 - 调试演示**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
public class DebugDemo {
    
    public static void main(String[] args) {
        DebugDemo demo = new DebugDemo();
        int result = demo.calculate(5, 3);
        System.out.println("结果：" + result);
    }
    
    public int calculate(int a, int b) {
        int sum = a + b;          // 设置断点1
        int product = a * b;      // 设置断点2
        int result = sum + product; // 设置断点3
        return result;
    }
}
```

**调试步骤**：
1. 在行号右侧点击，设置断点（出现红点）
2. 点击Debug按钮（绿色虫子图标）
3. 程序在断点处暂停
4. 使用快捷键控制执行：
   - F8：执行当前行，进入下一行
   - F7：进入方法内部
   - Shift + F8：跳出当前方法
5. 查看变量窗口，实时监控变量值
6. 使用条件断点：右键断点 → Condition，输入条件（如 `a > 5`）
7. 使用表达式求值：点击计算器图标，输入代码片段

**条件断点示例**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
for (int i = 0; i < 100; i++) {
    // 只在 i = 50 时暂停
    System.out.println(i); // 设置条件断点：i == 50
}
```

**常见坑点**：
1. ❌ 断点过多，程序频繁暂停
2. ❌ 忘记删除断点，影响性能
3. ❌ 调试时修改代码，导致调试状态失效

---

### 单元测试：JUnit5 + Mockito

**一句话人话解释**：单元测试是自动测试你的代码是否正确，避免手动测试的麻烦。

**生活比喻**：
单元测试就像做作业时的检查工具。你写完作业，老师帮你检查一遍，发现错误及时修改。而不是等考试时（上线）才发现错误。

**核心概念**：
- **JUnit**：测试框架
- **Mockito**：模拟对象，隔离依赖
- **@Test**：标记测试方法
- **Assert**：断言，验证结果

**代码示例 - JUnit5基础测试**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

public class CalculatorTest {
    
    private Calculator calculator;
    
    // 每个测试方法执行前执行
    @BeforeEach
    public void setUp() {
        calculator = new Calculator();
    }
    
    // 测试加法
    @Test
    @DisplayName("测试加法")
    public void testAdd() {
        int result = calculator.add(2, 3);
        assertEquals(5, result, "2 + 3 应该等于 5");
    }
    
    // 测试除法
    @Test
    @DisplayName("测试除法")
    public void testDivide() {
        double result = calculator.divide(10, 2);
        assertEquals(5.0, result, 0.0001, "10 / 2 应该等于 5");
    }
    
    // 测试异常
    @Test
    @DisplayName("测试除零异常")
    public void testDivideByZero() {
        assertThrows(ArithmeticException.class, () -> {
            calculator.divide(10, 0);
        }, "除零应该抛出 ArithmeticException");
    }
    
    // 测试忽略
    @Test
    @Disabled("还没实现")
    public void testMultiply() {
        // ...
    }
    
    // 每个测试方法执行后执行
    @AfterEach
    public void tearDown() {
        calculator = null;
    }
}
```

**代码示例 - Mockito模拟依赖**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
import org.junit.jupiter.api.*;
import org.mockito.*;
import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

public class UserServiceTest {
    
    @Mock  // 模拟依赖对象
    private UserMapper userMapper;
    
    @InjectMocks  // 自动注入Mock对象
    private UserService userService;
    
    @BeforeEach
    public void setUp() {
        MockitoAnnotations.openMocks(this);
    }
    
    @Test
    @DisplayName("测试查询用户")
    public void testGetUser() {
        // 准备测试数据
        User expectedUser = new User();
        expectedUser.setId(1L);
        expectedUser.setUsername("xiaoming");
        
        // 模拟userMapper行为
        when(userMapper.findById(1L)).thenReturn(expectedUser);
        
        // 执行测试
        User actualUser = userService.getUser(1L);
        
        // 验证结果
        assertNotNull(actualUser);
        assertEquals("xiaoming", actualUser.getUsername());
        
        // 验证userMapper.findById(1L)被调用了一次
        verify(userMapper, times(1)).findById(1L);
    }
    
    @Test
    @DisplayName("测试用户不存在")
    public void testUserNotFound() {
        // 模拟返回null
        when(userMapper.findById(999L)).thenReturn(null);
        
        // 执行测试
        User user = userService.getUser(999L);
        
        // 验证结果
        assertNull(user);
    }
}
```

**代码示例 - 参数化测试**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.*;

public class ParameterizedTestDemo {
    
    @ParameterizedTest
    @ValueSource(strings = {"hello", "world", "java"})
    void testWithStrings(String word) {
        assertNotNull(word);
        assertTrue(word.length() > 0);
    }
    
    @ParameterizedTest
    @CsvSource({
        "2, 3, 5",
        "5, 10, 15",
        "-1, 1, 0"
    })
    void testAdd(int a, int b, int expected) {
        Calculator calculator = new Calculator();
        assertEquals(expected, calculator.add(a, b));
    }
    
    @ParameterizedTest
    @MethodSource("provideTestData")
    void testWithMethodSource(String input, boolean expected) {
        assertEquals(expected, input.isEmpty());
    }
    
    static Stream<Arguments> provideTestData() {
        return Stream.of(
            arguments("", true),
            arguments("hello", false),
            arguments("java", false)
        );
    }
}
```

**常见断言**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
assertEquals(expected, actual)          // 相等
assertNotEquals(expected, actual)       // 不相等
assertTrue(condition)                   // 为真
assertFalse(condition)                  // 为假
assertNull(object)                      // 为null
assertNotNull(object)                   // 不为null
assertThrows(Exception.class, () -> {...})  // 抛出异常
assertTimeout(Duration.ofSeconds(1), () -> {...})  // 超时
```

**常见坑点**：
1. ❌ 测试依赖数据库，测试不稳定
2. ❌ 测试之间有依赖关系，顺序影响结果
3. ❌ 不使用Mock，测试速度慢

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

**⚠️ 小白易懵点**：
什么时候用Mock？→ 当要测试的方法依赖其他对象（如数据库、外部API），用Mock模拟这些对象，只测试当前方法的逻辑。

---

### 日志框架：SLF4J + Logback

**一句话人话解释**：日志框架帮你记录程序运行时的重要信息，方便排查问题。

**生活比喻**：
日志就像行车记录仪。车子运行时自动记录路线、速度、事件（加油、维修）。出问题时可以回放日志，找到问题原因。

**核心概念**：
- **SLF4J**：日志门面（接口）
- **Logback**：日志实现
- **日志级别**：TRACE < DEBUG < INFO < WARN < ERROR
- **日志格式**：时间、级别、类名、消息

**代码示例 - 配置logback.xml**：
```xml
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    
    <!-- 定义变量 -->
    <property name="LOG_HOME" value="logs"/>
    
    <!-- 控制台输出 -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>
    
    <!-- 文件输出 -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_HOME}/app.log</file>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
        
        <!-- 滚动策略 -->
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>${LOG_HOME}/app.%d{yyyy-MM-dd}.log</fileNamePattern>
            <maxHistory>30</maxHistory> <!-- 保留30天 -->
        </rollingPolicy>
    </appender>
    
    <!-- 错误日志单独输出 -->
    <appender name="ERROR_FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_HOME}/error.log</file>
        <filter class="ch.qos.logback.classic.filter.LevelFilter">
            <level>ERROR</level>
            <onMatch>ACCEPT</onMatch>
            <onMismatch>DENY</onMismatch>
        </filter>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>${LOG_HOME}/error.%d{yyyy-MM-dd}.log</fileNamePattern>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
    </appender>
    
    <!-- 根日志级别 -->
    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="FILE"/>
        <appender-ref ref="ERROR_FILE"/>
    </root>
    
    <!-- 特定包的日志级别 -->
    <logger name="com.java.mapper" level="DEBUG"/>
    <logger name="org.springframework" level="WARN"/>
    
</configuration>
```

**代码示例 - 使用日志**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Service
public class UserService {
    
    private static final Logger logger = LoggerFactory.getLogger(UserService.class);
    
    public User getUser(Long userId) {
        logger.info("开始查询用户，userId={}", userId);
        
        try {
            User user = userMapper.findById(userId);
            
            if (user == null) {
                logger.warn("用户不存在，userId={}", userId);
                return null;
            }
            
            logger.debug("查询成功，用户名={}", user.getUsername());
            return user;
            
        } catch (Exception e) {
            logger.error("查询用户失败，userId={}", userId, e);
            throw new RuntimeException("查询失败", e);
        }
    }
}
```

**日志级别说明**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
logger.trace("最详细的日志，一般不开启");
logger.debug("调试信息，开发时使用");
logger.info("重要信息，程序正常运行");
logger.warn("警告信息，不影响运行但需要注意");
logger.error("错误信息，需要立即处理");
```

**使用占位符（不要用字符串拼接）**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
// ✅ 推荐：使用占位符
logger.info("用户登录成功，userId={}, username={}", userId, username);

// ❌ 不推荐：字符串拼接
logger.info("用户登录成功，userId=" + userId + ", username=" + username);
```

**常见坑点**：
1. ❌ 生产环境使用DEBUG级别，日志量太大
2. ❌ 用System.out.println打印日志，无法管理
3. ❌ 日志中输出敏感信息（密码、身份证号）

---

### 代码规范：阿里巴巴Java开发手册要点

**一句话人话解释**：代码规范是让所有人的代码风格统一，便于阅读和维护。

**生活比喻**：
代码规范就像交通规则。大家遵守同一套规则（红灯停绿灯行），交通才能有序，不会乱套。不遵守规范的代码就像乱开车，容易出事故。

**核心规范要点**：
- **命名规范**：见名知意
- **代码格式**：统一缩进、空行
- **注释规范**：必要的注释
- **异常处理**：不要吞掉异常
- **集合使用**：注意空指针

**代码示例 - 命名规范**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
// ✅ 类名：大驼峰（帕斯卡命名法）
public class UserService {}
public class OrderManager {}
public class HttpClientUtil {}

// ❌ 错误：类名不用小驼峰
public class userService {}

// ✅ 方法名：小驼峰
public void getUser() {}
public void calculateTotal() {}
public String toString() {}

// ❌ 错误：方法名不用大驼峰或下划线
public void GetUser() {}
public void calculate_total() {}

// ✅ 常量：全大写，下划线分隔
public static final String MAX_SIZE = "100";
public static final int DEFAULT_PAGE_SIZE = 10;

// ❌ 错误：常量不用小驼峰
public static final String maxSize = "100";

// ✅ 变量：小驼峰
private String userName;
private Integer userId;
private boolean isValid;

// ❌ 错误：变量用拼音
private String yonghuMing;
```

**代码示例 - 代码格式**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
// ✅ 正确：if/else加大括号
if (user != null) {
    user.login();
} else {
    System.out.println("用户为空");
}

// ❌ 错误：不加大括号
if (user != null)
    user.login();

// ✅ 正确：运算符两边加空格
int sum = a + b;
if (a > b && b > c) {

// ❌ 错误：空格不统一
int sum=a+b;
if(a>b&&b>c){

// ✅ 正确：方法参数间加空格
public void login(String username, String password) {

// ❌ 错误：参数间不加空格
public void login(String username,String password) {
```

**代码示例 - 异常处理**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
// ✅ 正确：捕获具体异常，打印堆栈
try {
    int result = 10 / 0;
} catch (ArithmeticException e) {
    logger.error("除零异常", e);
    throw new RuntimeException("计算失败", e);
}

// ❌ 错误：捕获Exception太宽泛
try {
    int result = 10 / 0;
} catch (Exception e) {
    // 吞掉异常
}

// ❌ 错误：不打印堆栈
try {
    int result = 10 / 0;
} catch (ArithmeticException e) {
    logger.error("出错了");  // 没有打印e，无法定位问题
}
```

**代码示例 - 集合使用**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
// ✅ 正确：初始化集合
List<String> list = new ArrayList<>();
Map<String, Integer> map = new HashMap<>();

// ❌ 错误：使用原始类型
List list = new ArrayList();

// ✅ 正确：判断集合是否为空
if (list != null && !list.isEmpty()) {
    for (String item : list) {
        System.out.println(item);
    }
}

// ❌ 错误：直接使用，可能空指针
for (String item : list) {
    System.out.println(item);
}

// ✅ 正确：使用containsKey判断
Map<String, String> map = new HashMap<>();
if (map.containsKey("key")) {
    String value = map.get("key");
}

// ✅ 正确：使用getOrDefault
String value = map.getOrDefault("key", "默认值");
```

**代码示例 - 对象比较**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
// ✅ 正确：使用equals比较字符串
if ("hello".equals(username)) {

// ❌ 错误：可能空指针
if (username.equals("hello")) {

// ✅ 正确：使用Objects.equals比较对象
if (Objects.equals(user1, user2)) {

// ✅ 正确：使用StringUtils（Apache Commons）
if (StringUtils.isNotBlank(username)) {

// ❌ 错误：直接判断字符串
if (username != null && username.length() > 0) {
```

**代码示例 - 注释规范**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
/**
 * 用户服务类
 * 
 * @author xiaoming
 * @since 1.0.0
 */
public class UserService {
    
    /**
     * 根据用户ID查询用户信息
     * 
     * @param userId 用户ID
     * @return 用户信息，如果不存在返回null
     * @throws IllegalArgumentException 如果userId为null
     */
    public User getUserById(Long userId) {
        if (userId == null) {
            throw new IllegalArgumentException("userId不能为null");
        }
        return userMapper.findById(userId);
    }
    
    /**
     * 更新用户邮箱
     * 
     * @param userId 用户ID
     * @param newEmail 新邮箱地址
     */
    public void updateEmail(Long userId, String newEmail) {
        // TODO: 需要验证邮箱格式
        userMapper.updateEmail(userId, newEmail);
    }
}
```

**常见坑点**：
1. ❌ 命名不规范，看不懂代码含义
2. ❌ 没有注释，后人无法维护
3. ❌ 异常吞掉，问题无法定位

---

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

**💡 一句话总结**：
开发工具链让你如虎添翼——Git管理版本、IDEA提高效率、JUnit保证质量、日志记录运行、规范统一风格。

---

## 第八篇：部署与运维

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### JAR/WAR打包区别

**一句话人话解释**：JAR和WAR是Java应用的打包格式，用于部署到服务器。

**生活比喻**：
JAR就像随身包，自己就完整，走到哪都能用；WAR像快递箱，需要专门的接收站（Tomcat服务器）才能打开使用。

**核心概念**：
- **JAR**：Java Archive，包含所有依赖，独立运行
- **WAR**：Web Application Archive，需要Web容器（Tomcat）
- **打包命令**：mvn clean package

**JAR vs WAR对比**：
```
JAR包：
  ├─ 独立运行（java -jar app.jar）
  ├─ 内置Tomcat（SpringBoot）
  ├─ 所有依赖打包在一起
  └─ 适合微服务、云原生应用

WAR包：
  ├─ 需要部署到Tomcat
  ├─ 外部Tomcat管理
  ├─ 依赖Tomcat提供的服务
  └─ 适合传统Web应用
```

**代码示例 - pom.xml打包配置**：
```xml
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
<project>
    <!-- 打包类型：jar 或 war -->
    <packaging>jar</packaging>
    
    <build>
        <plugins>
            <!-- SpringBoot打包插件（JAR打包） -->
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
            
            <!-- WAR打包插件 -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-war-plugin</artifactId>
                <version>3.3.2</version>
            </plugin>
        </plugins>
    </build>
</project>
```

**代码示例 - SpringBoot打包为WAR**：
```java
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
@SpringBootApplication
public class Application extends SpringBootServletInitializer {
    
    // 重写configure方法
    @Override
    protected SpringApplicationBuilder configure(SpringApplicationBuilder builder) {
        return builder.sources(Application.class);
    }
    
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

**打包命令**：
```bash
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
# 清理并打包
mvn clean package

# 跳过测试打包（更快）
mvn clean package -DskipTests

# 指定环境打包
mvn clean package -Pprod

# 打包并安装到本地仓库
mvn clean install
```

**运行JAR包**：
```bash
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
# 运行JAR包（默认使用内置端口8080）
java -jar app.jar

# 指定端口运行
java -jar app.jar --server.port=8081

# 指定配置文件
java -jar app.jar --spring.profiles.active=prod

# 指定JVM参数（最大内存2GB）
java -Xmx2G -jar app.jar

# 后台运行（Linux）
nohup java -jar app.jar > app.log 2>&1 &

# 停止应用
ps -ef | grep app.jar
kill <pid>
```

**部署WAR包到Tomcat**：
```bash
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
# 1. 复制WAR包到Tomcat webapps目录
cp app.war /opt/tomcat/webapps/

# 2. 重启Tomcat
/opt/tomcat/bin/shutdown.sh
/opt/tomcat/bin/startup.sh

# 3. 查看日志
tail -f /opt/tomcat/logs/catalina.out

# 4. 访问应用（Tomcat默认端口8080）
http://localhost:8080/app/
```

**常见坑点**：
1. ❌ JAR包打包失败，依赖冲突
2. ❌ WAR包部署后404，访问路径错误
3. ❌ 端口被占用，应用启动失败

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

**⚠️ 小白易懵点**：
什么时候用JAR，什么时候用WAR？→ 新项目、微服务用JAR（SpringBoot）；传统项目、需要依赖Tomcat高级功能用WAR。

---

### Docker化Java应用

**一句话人话解释**：Docker把应用和依赖打包成容器，在任何服务器上都能运行。

**生活比喻**：
Docker就像集装箱。货物（应用）装进集装箱，无论用什么船（服务器）运输，集装箱里的货物都不会变，到哪都能用。

**核心概念**：
- **Dockerfile**：构建镜像的脚本
- **镜像（Image）**：应用的静态模板
- **容器（Container）**：运行中的镜像实例
- **Docker Compose**：多容器编排

**代码示例 - Dockerfile（OpenJDK）**：
```dockerfile
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
# 使用OpenJDK 17作为基础镜像
FROM openjdk:17-jdk-slim

# 设置工作目录
WORKDIR /app

# 复制JAR包到容器
COPY target/app.jar app.jar

# 暴露端口
EXPOSE 8080

# 设置JVM参数
ENV JAVA_OPTS="-Xms512m -Xmx1024m"

# 启动应用
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

**代码示例 - Dockerfile（多阶段构建）**：
```dockerfile
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
# 第一阶段：构建
FROM maven:3.8-openjdk-17 AS builder
WORKDIR /build
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

# 第二阶段：运行
FROM openjdk:17-jre-slim
WORKDIR /app
COPY --from=builder /build/target/app.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

**构建和运行镜像**：
```bash
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
# 1. 构建镜像
docker build -t java-app:1.0 .

# 2. 运行容器
docker run -d -p 8080:8080 --name myapp java-app:1.0

# 3. 查看日志
docker logs -f myapp

# 4. 进入容器
docker exec -it myapp /bin/bash

# 5. 停止容器
docker stop myapp

# 6. 删除容器
docker rm myapp

# 7. 删除镜像
docker rmi java-app:1.0
```

**代码示例 - docker-compose.yml**：
```yaml
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
version: '3.8'

services:
  # Java应用
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=prod
      - DB_HOST=mysql
    depends_on:
      - mysql
      - redis
    networks:
      - app-network
  
  # MySQL数据库
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: 123456
      MYSQL_DATABASE: java_tutorial
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql
    networks:
      - app-network
  
  # Redis缓存
  redis:
    image: redis:7
    ports:
      - "6379:6379"
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  mysql-data:
```

**使用Docker Compose**：
```bash
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f app

# 重启服务
docker-compose restart app

# 停止所有服务
docker-compose down

# 停止并删除数据
docker-compose down -v
```

**常见坑点**：
1. ❌ Dockerfile路径错误，找不到JAR包
2. ❌ 端口冲突，容器无法启动
3. ❌ 容器内无法访问宿主机服务（用host.docker.internal）

---

### JVM调优参数

**一句话人话解释**：JVM调优是通过调整参数让Java应用跑得更快、更稳。

**生活比喻**：
JVM调优就像调汽车。调整发动机参数（JVM参数），让车跑得更快、更省油、更稳定。参数调好了，驾驶体验大幅提升。

**核心参数**：
- **-Xms**：初始堆内存大小
- **-Xmx**：最大堆内存大小
- **-XX:+UseG1GC**：使用G1垃圾回收器
- **-XX:MetaspaceSize**：元空间大小

**代码示例 - JVM参数配置**：
```bash
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
# 基础配置（4GB服务器）
java -Xms2g -Xmx2g -XX:+UseG1GC -jar app.jar

# 详细配置
java \
  -Xms2g \                    # 初始堆内存2GB
  -Xmx2g \                    # 最大堆内存2GB
  -XX:+UseG1GC \              # 使用G1垃圾回收器
  -XX:MetaspaceSize=256m \    # 元空间256MB
  -XX:MaxMetaspaceSize=512m \  # 最大元空间512MB
  -XX:MaxGCPauseMillis=200 \  # GC停顿时间目标200ms
  -XX:+HeapDumpOnOutOfMemory \  # OOM时自动Dump
  -XX:HeapDumpPath=/logs/heapdump.hprof \  # Dump文件路径
  -XX:+PrintGCDetails \        # 打印GC详情
  -XX:+PrintGCDateStamps \    # 打印GC时间戳
  -Xloggc:/logs/gc.log \      # GC日志路径
  -jar app.jar
```

**垃圾回收器选择**：
```
Serial GC：单线程，适合单核CPU
Parallel GC：多线程，吞吐量优先（JDK8默认）
G1 GC：低延迟，适合大堆内存（推荐）
ZGC：超低延迟，JDK11+
```

**堆内存配置建议**：
```
小型应用（<2GB堆）：
  -Xms512m -Xmx512m

中型应用（2-8GB堆）：
  -Xms2g -Xmx4g

大型应用（>8GB堆）：
  -Xms4g -Xmx8g
```

**代码示例 - 生产环境JVM参数**：
```bash
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
#!/bin/bash

APP_NAME="app.jar"
LOG_DIR="/logs"

# JVM参数
JVM_OPTS="-Xms4g \
  -Xmx4g \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=200 \
  -XX:InitiatingHeapOccupancyPercent=45 \
  -XX:MetaspaceSize=256m \
  -XX:MaxMetaspaceSize=512m \
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=$LOG_DIR/heapdump.hprof \
  -XX:+PrintGCDetails \
  -XX:+PrintGCDateStamps \
  -Xloggc:$LOG_DIR/gc.log \
  -XX:+UseGCLogFileRotation \
  -XX:NumberOfGCLogFiles=10 \
  -XX:GCLogFileSize=100M"

# 启动应用
nohup java $JVM_OPTS -jar $APP_NAME > $LOG_DIR/application.log 2>&1 &

echo "应用已启动，PID: $!"
```

**常见坑点**：
1. ❌ 堆内存设置过小，频繁FullGC
2. ❌ 堆内存设置过大，超过物理内存
3. ❌ 垃圾回收器选择错误，性能下降

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

**⚠️ 小白易懵点**：
-Xms和-Xmx应该设置一样大吗？→ 建议一样大，避免运行时动态调整内存导致性能抖动。

---

### 常见问题排查

**一句话人话解释**：通过工具分析日志、线程、内存，找到Java应用的性能瓶颈和故障原因。

**生活比喻**：
排查问题就像医生看病。通过听诊器（jstat）、CT（jmap）、验血（日志）等工具，找到病因（问题所在），对症下药（解决问题）。

**核心概念**：
- **jstack**：查看线程堆栈，找死锁
- **jmap**：查看内存使用，导出堆快照
- **jstat**：查看GC统计
- **Arthas**：线上诊断工具

**代码示例 - OOM分析**：
```bash
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
# 1. 查找Java进程
jps -l

# 2. 导出堆快照（Heap Dump）
jmap -dump:format=b,file=heapdump.hprof <pid>

# 3. 分析堆快照（使用MAT、JProfiler等工具）
# 下载MAT：https://www.eclipse.org/mat/

# 4. 查看堆内存概览
jmap -heap <pid>

# 5. 查看堆内存中的对象统计
jmap -histo:live <pid> | head -20
```

**代码示例 - CPU飙高排查**：
```bash
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
# 1. 查看CPU占用高的Java进程
top -c
# 找到CPU占用高的Java进程PID

# 2. 查看该进程的线程占用
top -Hp <pid>
# 找到CPU占用高的线程PID（十进制）

# 3. 将线程PID转为16进制
printf "%x\n" <线程PID>
# 例如：12345 -> 3039

# 4. 查看线程堆栈
jstack <pid> | grep <十六进制PID>

# 5. 找到占用CPU的代码位置
# 定位到具体代码行号
```

**代码示例 - 线程死锁检测**：
```bash
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
# 导出线程堆栈
jstack <pid> > thread.dump

# 查找死锁
jstack -l <pid>

# 输出示例：
# Found one Java-level deadlock:
# =============================
# "Thread-1":
#   waiting to lock monitor 0x0000000787c4e818 (object 0x0000000789f3d2d0),
#   which is held by "Thread-0"
# "Thread-0":
#   waiting to lock monitor 0x0000000787c4f5d8 (object 0x0000000789f3d2e8),
#   which is held by "Thread-1"
```

**代码示例 - 使用jstat查看GC**：
```bash
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
# 查看GC统计（每1秒输出一次，共10次）
jstat -gcutil <pid> 1s 10

# 输出说明：
# S0C  S1C  S0U  S1U      EC       EU       OC       OU       MC       MU    CCSC  CCSU   YGC     YGCT     FGC    FGCT     GCT
# 512.0 512.0  0.0  0.0   2048.0   512.0  40960.0  20480.0  51200.0 50000.0  6144.0 5800.0    512    12.345     10    20.678   33.023

# 字段说明：
# S0C/S1C: Survivor区容量
# S0U/S1U: Survivor区使用量
# EC: Eden区容量
# EU: Eden区使用量
# OC: 老年代容量
# OU: 老年代使用量
# YGC: Young GC次数
# YGCT: Young GC耗时
# FGC: Full GC次数
# FGCT: Full GC耗时
# GCT: 总GC耗时
```

**代码示例 - 使用Arthas（推荐）**：
```bash
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
# 1. 下载Arthas
wget https://arthas.aliyun.com/arthas-boot.jar

# 2. 启动Arthas
java -jar arthas-boot.jar

# 3. 选择要诊断的Java进程

# 4. 查看线程情况
thread
thread -n 5           # 查看CPU占用最高的5个线程
thread -b             # 查找阻塞的线程

# 5. 查看类加载情况
sc -d *UserService    # 查看UserService类信息

# 6. 查看方法调用
monitor -c 5 com.java.UserService getUser  # 每5秒统计一次方法调用

# 7. 查看堆内存
dashboard             # 查看系统概览
vmtool --action getInstances --className java.lang.String --limit 10  # 查看String实例

# 8. 反编译类
jad com.java.UserService  # 查看UserService反编译代码

# 9. 退出Arthas
quit                   # 退出当前会话
stop                    # 停止所有Arthas会话
```

**代码示例 - 日志分析**：
```bash
![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
# 1. 查看错误日志
grep ERROR application.log | tail -20

# 2. 查看特定时间的日志
sed -n '/2024-01-01 10:00:00/,/2024-01-01 11:00:00/p' application.log

# 3. 统计错误数量
grep ERROR application.log | wc -l

# 4. 查看异常堆栈
grep -A 10 "Exception" application.log

# 5. 实时查看日志
tail -f application.log

# 6. 查看特定关键词
grep "NullPointerException" application.log
```

**常见问题排查清单**：
```
1. 应用启动失败
   └─ 检查日志，看具体错误信息
   └─ 检查端口是否被占用
   └─ 检查配置文件是否正确

2. CPU飙高
   └─ top找到Java进程
   └─ top -Hp找到线程
   └─ jstack查看堆栈
   └─ 定位到代码

3. 内存泄漏
   └─ jmap导出堆快照
   └─ MAT分析
   └─ 找到占用内存的对象
   └─ 定位代码并修复

4. 应用响应慢
   └─ 查看GC日志
   └─ 看是否有FullGC
   └─ 检查慢查询日志
   └─ Arthas查看方法调用

5. 线程死锁
   └─ jstack -l <pid>
   └─ 查看死锁信息
   └─ 修复死锁代码
```

**常见坑点**：
1. ❌ 生产环境频繁Dump，导致卡顿
2. ❌ 只看日志不看堆栈，定位问题慢
3. ❌ 乱用Arthas命令，影响生产环境

---

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

**💡 一句话总结**：
部署与运维让你的应用稳定运行——JAR/WAR打包、Docker容器化、JVM调优参数、问题排查工具，让你的应用跑得更稳更快。

---

## 结语

恭喜你完成了Java零基础小白教程下半部分的学习！🎉

**你已经掌握了**：
- ✅ 企业级框架：Maven、Spring、MyBatis、Security
- ✅ 数据库与中间件：JDBC、Redis、消息队列
- ✅ 开发工具链：Git、IDEA、JUnit、日志
- ✅ 部署与运维：打包、Docker、JVM调优、问题排查

**下一步建议**：
1. 🚀 动手实践，做个完整的小项目
2. 📚 深入学习某个方向（如后端、微服务、大数据）
3. 💼 准备面试，刷LeetCode算法题
4. 👥 参与开源项目，提升实战经验

**记住**：
- 编程是实践出来的，多写代码
- 遇到问题不要怕，善用搜索和工具
- 保持好奇心，持续学习

**祝你编程之路越走越宽！加油！💪**

---

*本教程由蜡笔小新友情插画支持* 🖍️
