# PICC门诊慢特病业务管理系统 - 新成员Onboarding手册

> 📅 预计完成时间：**2小时**  
> 👤 目标读者：零基础新人  
> 🔧 服务端口：`9091`

---

## 第一部分：环境准备（30分钟）

### 1.1 JDK安装

**版本要求**：JDK 8（Java 8）

```bash
# 检查是否已安装
java -version

# 如需安装，推荐使用OpenJDK 8（Linux/Mac）
# Ubuntu/Debian
sudo apt update && sudo apt install openjdk-8-jdk

# Mac (使用Homebrew)
brew install openjdk@8

# Windows: 下载地址 https://adoptium.net/temurin/releases/?version=8
```

**环境变量配置**：
```bash
# 在 ~/.bashrc 或 ~/.zshrc 中添加
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# 使配置生效
source ~/.bashrc
```

### 1.2 Maven配置

**版本要求**：Maven 3.6+

```bash
# 检查版本
mvn -version
```

**settings.xml配置**（关键！必须配置私服）：

```xml
<!-- ~/.m2/settings.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<settings>
  <mirrors>
    <!-- 阿里云公共仓库（兜底） -->
    <mirror>
      <id>aliyun</id>
      <mirrorOf>*</mirrorOf>
      <url>http://maven.aliyun.com/nexus/content/groups/public/</url>
    </mirror>
  </mirrors>
  
  <profiles>
    <profile>
      <id>picc-repo</id>
      <repositories>
        <!-- PICC项目私服 -->
        <repository>
          <id>f1dd82-picc-mzmtb</id>
          <name>PICC-MZMTB私服</name>
          <url>http://bkrepo.itservice.piccnet/maven/f1dd82/picc-mzmtb/</url>
          <releases><enabled>true</enabled></releases>
          <snapshots><enabled>false</enabled></snapshots>
        </repository>
        <!-- 南方开发平台仓库 -->
        <repository>
          <id>picc-maven-public</id>
          <url>http://south.repo.devops.piccnet/maven/picc/maven-public/</url>
        </repository>
      </repositories>
    </profile>
  </profiles>
  
  <activeProfiles>
    <activeProfile>picc-repo</activeProfile>
  </activeProfiles>
</settings>
```

### 1.3 IDE配置（IntelliJ IDEA）

**推荐插件安装**：
1. **Lombok** - 自动生成getter/setter
2. **MyBatisX** - Mapper XML与接口跳转
3. **Maven Helper** - Maven依赖分析
4. **RestfulToolkit** - REST接口快速定位
5. **Translation** - 中英文翻译

**IDEA配置**：
```properties
# File → Settings → Build → Compiler → Java Compiler
Project bytecode version: 8

# File → Settings → Build → Build Tools → Maven
Maven home: 选择你的Maven目录
User settings file: ~/.m2/settings.xml

# 开启注解处理器（支持Lombok）
File → Settings → Build → Compiler → Annotation Processors
☑ Enable annotation processing
```

### 1.4 数据库客户端

**GaussDB兼容PostgreSQL协议**，推荐使用以下客户端：

| 客户端 | 特点 | 下载地址 |
|--------|------|----------|
| DataGrip | 功能强大，支持多数据库 | jetbrains.com/datagrip |
| DBeaver | 免费开源 | dbeaver.io |
| pgAdmin | PostgreSQL官方 | pgadmin.org |
| Navicat | 界面友好 | navicat.com |

**连接参数**（从配置文件获取）：
```yaml
# 开发环境数据库连接
URL: jdbc:postgresql://{host}:{port}/link
用户名: postgres
密码: {联系管理员获取}
```

### 1.5 Apollo配置中心

**本地开发配置**：

```properties
# Windows: C:\opt\settings\server.properties
# Linux/Mac: /opt/settings/server.properties

# 创建配置目录
sudo mkdir -p /opt/settings

# 添加配置（外网访问）
apollo.configService=http://nps.08600.pw:31162

# 或内网访问（需要VPN）
apollo.configService=http://192.168.8.120:8080/
```

**Apollo管理后台**：
- 地址：http://nps.08600.pw:41117/
- 账号：联系项目管理员获取

### 1.6 Redis安装/连接

**方式一：使用远程Redis（推荐本地开发）**
```yaml
# 已配置远程Redis
host: nps.08600.pw
port: 41114
database: 0
```

**方式二：本地安装**
```bash
# Ubuntu/Debian
sudo apt install redis-server

# Mac
brew install redis

# 启动
redis-server

# 测试连接
redis-cli ping
```

---

## 第二部分：项目拉取和启动（30分钟）

### 2.1 Git克隆

```bash
# 克隆项目
git clone <项目仓库地址> picc-mzmtb-server

# 进入项目目录
cd picc-mzmtb-server

# 查看项目结构
ls -la
```

### 2.2 Maven编译

```bash
# 首次编译（跳过测试以加快速度）
mvn clean install -DskipTests

# 或分模块编译
cd picchealth-db && mvn clean install -DskipTests && cd ..
cd picchealth-server && mvn clean install -DskipTests && cd ..
cd mtb-yh && mvn clean install -DskipTests && cd ..
```

**编译常见问题**：

| 问题 | 解决方案 |
|------|----------|
| 依赖下载超时 | 配置阿里云镜像，切换网络 |
| 找不到parent pom | 确保settings.xml配置正确 |
| 编译内存不足 | `export MAVEN_OPTS="-Xmx2g"` |

### 2.3 配置文件修改

**关键配置文件位置**：
```
picchealth-server/src/main/resources/
├── application.yml          # 主配置
├── application-dev.yml      # 开发环境配置
├── bootstrap.yml            # 启动配置
└── dev/
    └── applic.properties    # 本地开发配置
```

**本地开发配置修改**：

```yaml
# application-dev.yml 或 applic.properties

# 1. Apollo配置（确保能连接）
apollo:
  meta: http://nps.08600.pw:31162

# 2. 数据库连接
spring:
  datasource:
    url: jdbc:postgresql://{host}:{port}/link
    username: postgres
    # password: {联系管理员获取}

# 3. Redis连接
spring.redis.host: nps.08600.pw
spring.redis.port: 41114

# 4. Token拦截配置（开发环境建议关闭）
tokenInterceptFlag: false
```

### 2.4 本地启动

**方式一：IDEA启动**

1. 打开 `picchealth-server/src/main/java/com/picchealth/LinkSpringBootApplication.java`
2. 右键 → Run 'LinkSpringBootApplication'
3. 添加VM参数（如需要）：
   ```
   -Dapollo.configService=http://nps.08600.pw:31162
   -Dserver.port=9091
   ```

**方式二：命令行启动**

```bash
cd picchealth-server
mvn spring-boot:run -DskipTests
```

**启动成功标志**：
```
--------启动成功！--------
```

### 2.5 常见启动报错和解决方案

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `Apollo配置中心连接失败` | 网络或配置问题 | 检查server.properties配置 |
| `Redis连接超时` | Redis服务未启动或网络 | 检查Redis配置或启动本地Redis |
| `数据库连接失败` | GaussDB未启动或参数错误 | 检查数据库连接参数 |
| `端口9091被占用` | 其他服务占用端口 | `lsof -i:9091` 查看并关闭 |
| `Bean注入失败` | 循环依赖 | 检查@Service命名是否正确 |
| `Activiti表不存在` | 数据库初始化问题 | 执行Activiti建表SQL |

---

## 第三部分：代码导航（30分钟）

### 3.1 项目目录结构

```
picc-mzmtb-server/
├── pom.xml                          # 父POM
├── picchealth-db/                   # 数据库层（DAO + PO）
│   ├── src/main/java/com.picchealth.module/
│   │   ├── basedoc/                 # 基础文档模块
│   │   ├── mb/                      # 慢病核心模块
│   │   ├── drugstore/               # 药店模块
│   │   ├── thirdfee/                # 第三方费用模块
│   │   └── publics/                 # 公共模块
│   └── src/main/resources/mapper/   # MyBatis XML
│       └── module/
│           ├── mb/                  # 慢病相关Mapper
│           ├── basedoc/
│           └── ...
│
├── picchealth-server/               # 业务服务层（主工程）
│   ├── src/main/java/com.picchealth/
│   │   ├── module/
│   │   │   ├── mb/                  # 核心业务模块
│   │   │   │   ├── api/             # API层（对外接口）
│   │   │   │   ├── service/         # 业务层
│   │   │   │   ├── vo/              # 入参VO
│   │   │   │   ├── dto/             # 数据传输对象
│   │   │   │   ├── enums/           # 枚举类
│   │   │   │   └── constant/        # 常量
│   │   │   ├── mtb/                 # PC端业务
│   │   │   ├── scheduling/          # 定时任务
│   │   │   └── ...
│   │   ├── config/                  # 配置类
│   │   └── utils/                   # 工具类
│   └── src/main/resources/
│       ├── processes/               # BPMN流程文件（13个）
│       ├── i18n/                    # 国际化配置
│       └── applic.properties        # 本地配置
│
└── mtb-yh/                          # 地市差异模块
    ├── mtb-base/                    # 基础配置
    ├── mtb-bj/                      # 宝鸡
    ├── mtb-sl/                      # 商洛
    ├── mtb-ya/                      # 延安
    ├── mtb-yl/                      # 榆林
    ├── mtb-dz/                      # 达州
    ├── mtb-jz/                      # 晋中
    ├── mtb-jc/                      # 晋城
    ├── mtb-jj/                      # 九江
    ├── mtb-mzl/                     # 满洲里
    ├── mtb-yli/                     # 杨凌
    ├── mtb-xya/                     # 咸阳
    ├── mtb-dez/                     # 定州
    └── mtb-hn/                      # 河南（信创适配）
```

### 3.2 代码导航速查表

#### 🔍 "我想看申报逻辑"

| 需求 | 文件路径 |
|------|----------|
| 申报API接口 | `picchealth-server/src/main/java/com/picchealth/module/mb/api/MbDeclareApi.java` |
| 申报Service | `picchealth-server/src/main/java/com/picchealth/module/mb/service/VipMbdeclareInfoService.java` |
| 申报流程Service | `picchealth-server/src/main/java/com/picchealth/module/mb/service/ActivitiService.java` |
| 申报相关Mapper | `picchealth-db/src/main/resources/mapper/module/mb/VipMbdeclareInfoDao.xml` |

#### 🔍 "我想看某个地市的差异"

| 地市 | 目录路径 |
|------|----------|
| 宝鸡 | `mtb-yh/mtb-bj/` |
| 商洛 | `mtb-yh/mtb-sl/` |
| 延安 | `mtb-yh/mtb-ya/` |
| 榆林 | `mtb-yh/mtb-yl/` |
| 达州 | `mtb-yh/mtb-dz/` |
| 晋中 | `mtb-yh/mtb-jz/` |

**地市Flag对应关系**（在 `SxMedicareConstant.java`）：
```java
// 陕西地区Flag
REGION_CODE_SX_BJ = "0"   // 宝鸡
REGION_CODE_SX_SL = "2"   // 商洛
REGION_CODE_SX_YA = "4"   // 延安
REGION_CODE_SX_YL = "7"   // 榆林
```

#### 🔍 "我想看数据库表结构"

| 用途 | Mapper XML位置 |
|------|---------------|
| 申报主表 | `picchealth-db/src/main/resources/mapper/module/mb/VipMbdeclareInfoDao.xml` |
| 申报材料表 | `picchealth-db/src/main/resources/mapper/module/mb/VipMbdeclareFileDao.xml` |
| 用户扩展表 | `picchealth-db/src/main/resources/mapper/module/mb/VipMbuserExtDao.xml` |
| 体检机构表 | `picchealth-db/src/main/resources/mapper/module/mb/VipPhysicalOrgDao.xml` |
| 单位配置表 | `picchealth-db/src/main/resources/mapper/module/mb/UnitConfigDao.xml` |

**Mapper接口位置**：
```
picchealth-db/src/main/java/com/picchealth/module/mb/dao/
```

#### 🔍 "我想看API接口"

**API列表**（共81个核心API类）：

| 模块 | 文件 |
|------|------|
| 申报 | `MbDeclareApi.java` |
| 审批 | `MbReviewApi.java` |
| Activiti流程 | `ActivitiApi.java`, `Activiti6Api.java` |
| 体检 | `MbImportApi.java` |
| 登录 | `LoginApi.java` |
| 用户 | `MbUserExtApi.java` |

**接口文档访问地址**：
```
http://localhost:9091/swagger-ui.html
http://localhost:9091/doc.html
```

### 3.3 关键文件速查表

| 功能 | 文件路径 |
|------|----------|
| **启动类** | `picchealth-server/.../LinkSpringBootApplication.java` |
| **Token拦截器** | `picchealth-server/.../config/TokenInterceptorConfig.java` |
| **Flag拦截器** | `picchealth-server/.../config/FlagInterceptorConfig.java` |
| **接口授权拦截** | `picchealth-server/.../config/InterfaceGrantHandler.java` |
| **小程序签名拦截** | `picchealth-server/.../config/XcxInterceptorConfig.java` |
| **动态参数解析** | `picchealth-server/.../config/resolver/MyHandlerMethodArgumentResolver.java` |
| **Redis配置** | `picchealth-server/.../config/RedissonConfig.java` |
| **Activiti配置** | `picchealth-server/.../config/ActivitiDatasourceConfig.java` |
| **国际化消息** | `picchealth-server/src/main/resources/i18n/messages_zh_CN.properties` |
| **地市枚举** | `mtb-yh/mtb-base/.../enums/UnitConfigEnum.java` |

### 3.4 BPMN流程文件（13个）

| 文件名 | 说明 | 地市 |
|--------|------|------|
| `bjmbsb.bpmn` | 宝鸡慢病申报流程 | 宝鸡 |
| `bjmbfs.bpmn` | 宝鸡慢病放石流程 | 宝鸡 |
| `slmbsb.bpmn` | 商洛慢病申报流程 | 商洛 |
| `yambsb.bpmn` | 延安慢病申报流程 | 延安 |
| `ylimbsb.bpmn` | 榆林慢病申报流程 | 榆林 |
| `dizmbsb.bpmn` | 定州慢病申报流程 | 定州 |
| `jcmbsb.bpmn` | 晋城慢病申报流程 | 晋城 |
| `jjmbsb.bpmn` | 九江慢病申报流程 | 九江 |
| `jzmbsb.bpmn` | 晋中慢病申报流程 | 晋中 |
| `ylmbsb.bpmn` | 养老慢病申报流程 | - |
| `mzlmbsb.bpmn` | 满洲里慢病申报流程 | 满洲里 |
| `xyambsb.bpmn` | 咸阳慢病申报流程 | 咸阳 |
| `zjkmbsb.bpmn` | 张家口慢病申报流程 | 张家口 |

---

## 第四部分：调试技巧（30分钟）

### 4.1 本地调试配置

**IDEA配置**：

1. **创建运行配置**
   - Run → Edit Configurations → + → Spring Boot
   - Main class: `com.picchealth.LinkSpringBootApplication`
   - VM options:
     ```
     -Dapollo.configService=http://nps.08600.pw:31162
     -Dserver.port=9091
     -Xms512m -Xmx1024m
     ```

2. **启用热部署（可选）**
   ```xml
   <!-- pom.xml中取消注释 -->
   <dependency>
       <groupId>org.springframework.boot</groupId>
       <artifactId>spring-boot-devtools</artifactId>
       <scope>runtime</scope>
       <optional>true</optional>
   </dependency>
   ```

### 4.2 日志级别调整

```yaml
# applic.properties
logging.level.root = INFO
logging.level.com.picchealth = DEBUG
logging.level.org.activiti = DEBUG
logging.level.org.springframework = INFO
```

**动态调整（通过Apollo）**：
```
apollo.bootstrap.namespaces = application
```

**代码中使用**：
```java
@Slf4j
public class XxxService {
    public void method() {
        log.debug("调试信息");
        log.info("普通信息");
        log.warn("警告信息");
        log.error("错误信息");
    }
}
```

### 4.3 接口调试

**Swagger文档**：
```
http://localhost:9091/swagger-ui.html
http://localhost:9091/doc.html
```

**Postman调试示例**：

```json
// 通用请求头
{
  "Content-Type": "application/json",
  "flag": "0",           // 地市Flag（必填！）
  "token": "xxx",        // Token（开发环境可为空）
  "userid": "xxx"        // 用户ID
}

// 申报查询接口示例
POST http://localhost:9091/MbDeclare/query
{
  "pageNum": 1,
  "pageSize": 10,
  "name": "张三"
}
```

### 4.4 Activiti流程调试

**查看流程定义**：
```java
// ActivitiApi.java 提供了流程查询接口
POST /Activiti/queryProcessDefinitions
```

**关键流程操作**：
| 操作 | 说明 |
|------|------|
| 启动流程 | `ActivitiApi.startProcess()` |
| 查询任务 | `ActivitiApi.queryTasks()` |
| 完成任务 | `ActivitiApi.completeTask()` |
| 查看历史 | `ActivitiApi.getHistories()` |
| 添加批注 | `ActivitiApi.addComment()` |

**调试技巧**：
```java
// 在流程关键节点添加日志
log.info("=== 流程ID: {}, 任务ID: {}, 当前节点: {} ===", 
    processInstanceId, taskId, taskName);

// 查看当前节点
@Autowired
private RuntimeService runtimeService;

ProcessInstance instance = runtimeService.createProcessInstanceQuery()
    .processInstanceId(processInstanceId)
    .singleResult();
```

### 4.5 常见问题和排查思路

| 问题 | 排查思路 |
|------|----------|
| 接口返回401 | 检查Token拦截器，确认flag是否传递 |
| 接口返回无权限 | 检查InterfaceGrantHandler配置 |
| 流程节点不流转 | 检查BPMN配置和变量传递 |
| 数据库操作失败 | 检查Mapper XML和事务配置 |
| Redis操作超时 | 检查Redis连接和网络 |
| 文件上传失败 | 检查文件大小限制和存储路径 |

**调试命令**：

```bash
# 查看端口占用
netstat -tlnp | grep 9091

# 查看日志
tail -f logs/*.log

# 清理Maven缓存
mvn dependency:purge-local-repository
```

---

## 第五部分：避坑指南

### 5.1 安全/代码质量问题清单

> ⚠️ **以下问题已在安全审计中发现，开发时务必注意！**

#### P0级问题（必须立即修复）

| 序号 | 问题类型 | 问题描述 | 修复建议 |
|------|----------|----------|----------|
| 1 | SQL注入 | 动态SQL未使用参数化查询 | 使用 `#{}` 而非 `${}` |
| 2 | XSS | 未对用户输入进行过滤 | 添加输入校验和输出编码 |
| 3 | 敏感信息泄露 | 日志中打印敏感数据 | 使用脱敏工具类 |
| 4 | 接口越权 | 缺少权限校验 | 添加接口授权验证 |
| 5 | 文件上传 | 未限制文件类型 | 白名单校验文件类型 |
| 6 | 密码明文 | 密码未加密存储 | 使用BCrypt加密 |
| 7 | Token失效 | Token永不过期 | 设置合理过期时间 |
| 8 | 异常泄露 | 未捕获异常直接抛出 | 全局异常处理 |

#### P1-P2级问题（尽快修复）

| 序号 | 问题类型 | 修复建议 |
|------|----------|----------|
| 1 | 日志级别 | 生产环境使用INFO/WARN |
| 2 | 事务边界 | 确保事务注解位置正确 |
| 3 | 空指针风险 | 使用Optional或Objects.nonNull() |
| 4 | 并发问题 | 使用线程安全集合 |

### 5.2 代码中的常见陷阱

#### 1. Flag路由陷阱

```java
// ❌ 错误：直接在Service中硬编码Flag判断
if ("0".equals(flag)) {
    // 宝鸡逻辑
} else if ("2".equals(flag)) {
    // 商洛逻辑
}

// ✅ 正确：使用接口多态 + @Service("接口名+Flag") 注解
@Service("IHealthServiceSL")  // SL = 商洛
public class HealthServiceSL implements IHealthService {
    // 商洛实现
}
```

#### 2. 动态参数解析陷阱

```java
// ❌ 错误：直接使用具体类型
public ApiResponse test(@RequestBody BJDeclareVo vo) {}

// ✅ 正确：使用泛型 + @MyRequestBody
public <T extends BaseDeclareVo> ApiResponse test(@MyRequestBody T vo) {}
```

#### 3. 事务陷阱

```java
// ❌ 错误：事务注解在接口层
@ApiInterceptor
@RestController
@Transactional  // ❌ 不要在Controller加事务！
public class XxxApi {
    @RequestMapping("/save")
    public void save() { }
}

// ✅ 正确：事务在Service实现层
@Service
@Transactional
public class XxxServiceImpl implements XxxService {
    @Override
    public void save() { }
}
```

#### 4. 日志打印陷阱

```java
// ❌ 错误：打印敏感信息
log.info("用户密码: {}", password);

// ✅ 正确：脱敏处理
log.info("用户信息: {}", UserUtils.desensitize(user));
```

### 5.3 与权限服务交互注意事项

**依赖服务**：`picc-mzmtb-user`（用户权限服务）

**注意事项**：

1. **Token校验**
   - 开发环境可通过配置 `tokenInterceptFlag=false` 跳过
   - 生产环境必须校验

2. **用户信息获取**
   ```java
   // 通过ThreadLocal获取当前用户
   User user = UserUtils.getUser();
   String userId = user.getUserId();
   ```

3. **权限缓存**
   - 权限信息存储在Redis
   - Key格式：`UrlPermission:{userId}`
   - 超时时间：120分钟

4. **常见错误码**
   ```java
   // 999: Token无效
   // 888: Flag信息为空
   // 其他: 查看国际化配置
   ```

### 5.4 申报全流程节点说明

```
申报 → 初审 → 体检 → 专家审核 → 发卡 → 激活 → 待遇享受
```

| 节点 | 说明 | 关键文件 |
|------|------|----------|
| 申报 | 患者提交申请材料 | `MbDeclareApi.java` |
| 初审 | 工作人员初步审核 | `MbReviewApi.java` |
| 体检 | 安排体检/不需要体检 | `MbImportApi.java` |
| 专家审核 | 专家评审 | `ActivitiService.java` |
| 发卡 | 制作并发放慢特病卡 | `MbmzSendCardApi.java` |
| 激活 | 患者激活卡片 | `MbmzInfoUpdateApi.java` |
| 待遇享受 | 开始享受慢特病待遇 | `ThirdfeeService.java` |

---

## 附录

### A. 快捷命令汇总

```bash
# Maven编译
mvn clean install -DskipTests

# 启动服务
cd picchealth-server && mvn spring-boot:run

# 查看API文档
open http://localhost:9091/swagger-ui.html

# 编译特定模块
mvn clean install -pl picchealth-db -am -DskipTests
```

### B. 联系方式

| 角色 | 联系方式 |
|------|----------|
| 项目负责人 | 联系管理员 |
| 技术支持 | 联系管理员 |
| Apollo配置 | http://nps.08600.pw:41117/ |
| Git仓库 | 联系管理员获取 |

### C. 相关文档

- [项目README](./README.md) - 项目基础说明
- [数据库设计文档] - 联系DBA获取
- [接口设计文档] - Swagger在线文档
- [BPMN流程图] - resources/processes/目录下

---

> 📝 **手册版本**：v1.0  
> 🕐 **最后更新**：2024年  
> ✨ **祝您开发愉快！**

---

📎 **延伸阅读**：
- [教程总纲索引](picc-mzmtb-server-教程文档.md) - 快速导航到所有业务服务文档
- [架构解析](picc-mzmtb-server-架构解析.md) - 深入理解技术栈、中间件配置、Activiti工作流
- [picc-mzmtb-user-Onboarding手册.md](picc-mzmtb-user-Onboarding手册.md) 📌(权限服务) - 权限服务的快速上手指南

