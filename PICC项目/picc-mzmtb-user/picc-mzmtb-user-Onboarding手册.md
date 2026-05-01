# PICC人保健康权限管理系统 - 新成员Onboarding手册

> 🎯 目标：让一个新加入项目组的开发人员，在2小时内理解项目全貌，能独立开始开发。

---

## 一、项目速览卡

| 项目 | 信息 |
|------|------|
| 项目名称 | 门诊慢特病业务管理信息系统-权限管理服务 |
| 仓库地址 | 阿里云Codeup（私有仓库） |
| 技术栈 | Spring Boot 2.x + MyBatis + GaussDB + Redis + Apollo |
| 服务端口 | 9092 |
| 部署方式 | K8s容器化部署 |
| 应用服务器 | BES宝兰德（信创要求） |
| 数据库 | GaussDB（信创要求，兼容PostgreSQL） |
| 代码规范 | Lombok + PageHelper分页 + 软删除(delete_at) |

---

## 二、5分钟跑起来

### 环境准备
```bash
# 1. JDK 1.8（必须）
java -version  # 确认1.8.x

# 2. Maven 3.6+
mvn -version

# 3. 本地需要有GaussDB或PostgreSQL实例
# 4. 本地需要有Redis
```

### 克隆与启动
```bash
# 克隆仓库
git clone https://codeup.aliyun.com/69708490f7b43e00d4204914/picc-mzmtb-user.git

# 编译打包
cd picc-mzmtb-user
mvn clean package -DskipTests

# 启动（需要先配置数据库和Redis连接）
# 配置文件: picchealth-privilege-server/src/main/resources/application.yml
# Apollo配置中心: 10.57.16.41:8080 (dev环境)

java -jar picchealth-privilege-server/target/picchealth-privilege-server.jar
```

### 常见启动问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 连不上Apollo | VPN未连接 | 先连VPN，Apollo在内网 |
| GaussDB连接失败 | 数据库未配置 | 修改bootstrap.yml指向本地PG |
| Redis连接失败 | Redis未启动 | 启动本地Redis |
| Bean创建失败 | Apollo配置缺失 | 本地开发可临时关闭Apollo |

---

## 三、项目结构速查

```
picc-mzmtb-user/
├── picchealth-privilege-server/     ← 主服务模块（启动类在这里）
│   ├── src/main/java/
│   │   └── com/picchealth/
│   │       ├── config/              ← 配置类（拦截器、过滤器）
│   │       ├── module/
│   │       │   ├── sys/             ← 系统模块（机构、用户、系统）
│   │       │   │   ├── api/         ← Controller层
│   │       │   │   ├── service/     ← Service接口
│   │       │   │   │   └── impl/    ← Service实现
│   │       │   │   ├── vo/          ← 视图对象（给前端看的）
│   │       │   │   └── dto/         ← 数据传输对象
│   │       │   ├── role/            ← 角色模块
│   │       │   └── menu/            ← 菜单模块
│   │       └── utils/               ← 工具类
│   └── src/main/resources/
│       ├── application.yml          ← 主配置
│       └── bootstrap.yml            ← Apollo配置
│
├── picchealth-privilege-db/         ← 数据库模块
│   └── src/main/resources/mapper/   ← MyBatis XML文件
│       └── module/
│           ├── system/              ← 系统模块Mapper
│           └── role/                ← 角色模块Mapper
│
└── pom.xml                          ← Maven父POM
```

---

## 四、核心业务速懂

### 权限模型：三维度交叉

```
维度1: 用户→角色→菜单（你能用哪些功能？）
维度2: 机构→系统→菜单（你所在部门开通了哪些功能？）
维度3: 用户→权限归属→菜单（你的管辖范围能看到哪些数据？）

最终可见 = 维度1 ∩ 维度2 ∩ 维度3
```

### 六大业务模块

| 模块 | 干什么的 | API前缀 | 核心表 |
|------|---------|---------|-------|
| 机构管理 | 管理省/市/县公司层级 | /privilege/org | privilege_org_info |
| 用户管理 | 管理系统用户CRUD | /privilege/user | privilege_user_info |
| 角色管理 | 管理角色及角色权限 | /privilege/role | privilege_role_info |
| 菜单管理 | 管理系统菜单树 | /privilege/menu | privilege_menu_info |
| 系统管理 | 管理业务系统 | /privilege/sys | privilege_system_info |
| 数据迁移 | 旧系统数据迁移工具 | /privilege/move | sys_role_module_rel |

---

## 五、开发规范速记

### 编码约定

| 规范 | 说明 |
|------|------|
| 删除 = 软删除 | 设置delete_at字段，不物理删除 |
| 主键 = UUID | UUIDUtil.getUUID()生成 |
| 分页 = PageHelper | PageHelper.startPage() |
| 密码 = SM4加密 | SM4Util.sm4Encrypt() |
| 用户信息 = UserUtils | UserUtils.getUser()获取当前用户 |
| 异常 = CustomException | 统一抛CustomException |
| 返回 = ApiResponse | 统一用ApiResponse.ok()/fail() |

### 新增接口标准流程

```
1. 在vo/下创建请求VO
2. 在dto/下创建DTO（如需）
3. 在service/下创建Service接口
4. 在service/impl/下实现Service
5. 在api/下创建Controller
6. 在dao/下添加Mapper方法
7. 在mapper XML中添加SQL
8. 测试！
```

### 请求走完一遭的路径

```
前端请求
  → ApiAuthorityFilter（Token校验，只拦截/privilege/user/*）
  → ApiInterceptor（URL权限校验）
  → Controller（参数校验，调用Service）
  → Service（业务逻辑，调用Mapper）
  → Mapper（SQL执行）
  → 数据库（GaussDB）
  → 返回ApiResponse
```

---

## 六、踩坑指南

### 已知坑点

| 坑 | 在哪 | 怎么避 |
|----|------|-------|
| orgName字段传的是ID | OrgQueryVo.orgName | 看注释！传机构ID不是名称 |
| pageNum从0开始=不分页 | PageHelper | pageNum最小传1 |
| 密码默认值在配置里 | defaultPassWord | 默认PICChealth@2020，SM4加密 |
| 机构树默认根ID="1" | defaultId = "1" | parentId="1"代表上级是人保集团 |
| 权限编码88=管理员 | UserInfoServiceImpl | authCode.contains("88")是管理员 |
| Apollo必须连通 | bootstrap.yml | 本地开发可配本地profile |

---

## 七、调试技巧

### 1. Swagger文档
启动后访问：`http://localhost:9092/swagger-ui.html`

### 2. 日志配置
logback-spring.xml控制日志级别，开发环境建议设为DEBUG

### 3. Redis调试
```bash
# 查看当前Token
redis-cli keys "api_token:*"

# 查看用户信息缓存
redis-cli keys "userid:*"

# 清除某个用户的Token（强制重新登录）
redis-cli del "userid:xxx"
```

### 4. 数据库调试
```sql
-- 查看软删除的数据（正常查询看不到）
SELECT * FROM privilege_user_info WHERE delete_at IS NOT NULL;

-- 查看某个用户的所有权限
SELECT u.name, r.name as role_name, m.name as menu_name
FROM privilege_user_info u
JOIN privilege_user_role ur ON u.id = ur.user_id AND ur.delete_at IS NULL
JOIN privilege_role_info r ON ur.role_id = r.id AND r.delete_at IS NULL
JOIN privilege_role_resource rr ON r.id = rr.role_id AND rr.delete_at IS NULL
JOIN privilege_menu_info m ON rr.menu_id = m.id AND m.delete_at IS NULL
WHERE u.account = '要查的账号';
```

---

## 八、关键人物与联系方式

> ⚠️ 请根据实际情况补充

| 角色 | 姓名 | 职责 |
|------|------|------|
| 项目负责人 | ? | 项目整体管理 |
| 后端开发 | jiezhenchi | 用户、机构、迁移模块 |
| 后端开发 | LiuChunlin | 角色、权限模块 |
| DBA | ? | GaussDB维护 |
| 运维 | ? | K8s部署、Apollo配置 |

---

## 九、下一步学习路径

1. 📖 通读 `picc-mzmtb-user-教程文档.md`（主教程，7000+行）
2. 🔧 本地启动项目，用Swagger调通一个接口
3. 📝 阅读OrgInfoServiceImpl.java（最复杂的Service，731行）
4. 🔐 理解权限三维度模型
5. 🗄️ 熟悉17张数据库表的结构和关系
6. 🛡️ 了解安全机制（三道认证关卡）
7. ✏️ 尝试新增一个简单接口（如机构备注修改）

---

## 十、常见问题FAQ

**Q: 为什么用GaussDB不用MySQL？**
A: 信创要求。政府/国企项目必须使用国产数据库，GaussDB是华为的，兼容PostgreSQL语法。

**Q: 为什么用BES宝兰德不用Tomcat？**
A: 同样是信创要求。BES是国产应用服务器，API和Tomcat基本兼容。

**Q: Apollo是什么？为什么要用它？**
A: Apollo是配置中心，把所有环境（dev/test/uat/prod）的配置集中管理，修改配置不需要重启服务。项目里数据库连接、Redis地址等都在Apollo里。

**Q: 为什么所有表都用软删除？**
A: 权限数据是敏感数据，删除后可能需要审计追溯，所以用delete_at标记删除而不是物理删除。

**Q: 同一个角色名在不同机构是不同记录？**
A: 是的。比如"经办员"这个角色在西安和宝鸡是两条不同记录（不同ID），因为每个机构可以自定义角色的权限范围。

---

📎 **延伸阅读**：
- [教程总纲索引](picc-mzmtb-user-教程文档.md) - 快速导航到所有权限服务文档
- [架构设计文档](picc-mzmtb-user-架构设计文档.md) - 完整的技术架构、安全架构说明
- [数据库ER图与表结构](picc-mzmtb-user-数据库ER图与表结构.md) - 17张数据库表的完整说明



---

## 十一、IDE配置详解（IntelliJ IDEA）

> 🏠 开发工具配置就像新员工配电脑——把该装的软件都装好，才能高效工作

### 必备插件清单

| 插件名称 | 干嘛的 | 重要程度 | 安装建议 |
|---------|-------|---------|---------|
| **Lombok** | 自动生成getter/setter/constructor | ⭐⭐⭐⭐⭐ 必须装 | 代码量减少50% |
| **MyBatisX** | MyBatis XML和接口互相跳转 | ⭐⭐⭐⭐⭐ 必须装 | Mapper开发神器 |
| **Spring Boot Assistant** | application.yml智能提示 | ⭐⭐⭐⭐ 建议装 | 配置写错能及时发现 |
| **Alibaba Java Coding Guidelines** | 阿里Java编码规范检查 | ⭐⭐⭐ 建议装 | 避免写出不规范代码 |
| **Maven Helper** | Maven依赖冲突分析 | ⭐⭐⭐ 建议装 | 依赖问题排查必备 |
| **GitToolBox** | Git提交历史显示 | ⭐⭐ 可选 | 看代码改动原因很方便 |

### 插件安装步骤

```
1. 打开 IDEA → File → Settings → Plugins
2. 点击 "Browse repositories..."
3. 搜索插件名称
4. 点击 "Install" 安装
5. 重启 IDEA
```

### Lombok配置检查

```bash
# 确认pom.xml中有lombok依赖
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <version>1.18.30</version>
    <scope>provided</scope>
</dependency>

# IDEA需要安装Lombok插件才能识别@Data等注解
# Settings → Build → Compiler → Annotation Processors → Enable annotation processing ✓
```

### 编码设置

```bash
# IDEA设置（必须改成UTF-8）
File → Settings → Editor → File Encodings
  → Project Encoding: UTF-8
  → Default encoding for properties files: UTF-8
  → ✓ Save as UTF-8 for files

# JDK配置
File → Project Structure → Project
  → Project SDK: 1.8
  → Project language level: 8 - Lambdas, type annotations etc.
```

### Maven配置

```bash
# IDEA中配置Maven
File → Settings → Build → Build Tools → Maven
  → Maven home directory: 选择本机Maven路径
  → User settings file: ${MAVEN_HOME}/conf/settings.xml
  → Local repository: C:/Users/你的用户名/.m2/repository

# Maven导入优化（让IDEA不要傻傻地一直indexing）
Settings → Build → Build Tools → Maven → Importing
  → ✓ Import Maven projects automatically
  → JDK for importer: 1.8
```

---

## 十二、常见启动报错及解决方案

> 🏠 报错信息就像汽车仪表盘的故障灯——看懂了就知道哪里出了问题

### 报错1：Apollo连接失败

```
***************************
APPLICATION FAILED TO START
***************************

Description:

Failed to configure a DataSource: 'url' attribute is not specified and 
no embedded datasource could be configured.

Reason: Failed to determine a suitable driver class
```

**原因分析**：Apollo没连上 → 配置没加载 → 数据库连接信息没有 → DataSource创建失败

**解决方案**：
```bash
# 方案1：连VPN（最常见）
先确保连接了人保内网VPN

# 方案2：本地临时配置
在bootstrap.yml中临时指定本地数据库：
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/picc_health
    username: postgres
    password: 123456

# 方案3：跳过Apollo（不推荐，仅测试用）
# 删除bootstrap.yml中的apollo配置
# 在application.yml中直接写数据库配置
```

### 报错2：Redis连接失败

```
redis.clients.jedis.exceptions.JedisConnectionException: 
Could not get a resource from the pool
```

**原因分析**：Redis没启动或地址不对

**解决方案**：
```bash
# 检查Redis是否启动
redis-cli ping
# 如果返回 PONG，说明启动了

# 如果没启动，启动Redis
# Windows: redis-server
# Mac/Linux: brew services start redis 或 systemctl start redis

# 检查Redis地址配置（Apollo中）
redis.host=localhost
redis.port=6379
redis.password=（如果有密码）
```

### 报错3：端口被占用

```
java.net.BindException: Address already in use: bind
```

**原因分析**：9092端口被其他程序占用了

**解决方案**：
```bash
# Windows：查找占用端口的进程
netstat -ano | findstr 9092
taskkill /PID <进程ID> /F

# Mac/Linux：
lsof -i :9092
kill -9 <进程ID>

# 或者修改本机端口
# 在application.yml中临时修改：
server:
  port: 9093
```

### 报错4：Bean创建失败

```
org.springframework.beans.factory.UnsatisfiedDependencyException: 
Error creating bean with name 'xxxService': 
Unsatisfied dependency expressed through field 'xxxDao'
```

**原因分析**：Mapper接口没找到，可能是XML位置不对

**解决方案**：
```bash
# 检查Mapper XML位置是否正确
# 应该在：picchealth-privilege-db/src/main/resources/mapper/

# 检查pom.xml中是否配置了mapper-locations
mybatis:
  mapper-locations: classpath:mapper/**/*.xml

# 检查XML的namespace是否对应Mapper接口
<!-- XML中 -->
<mapper namespace="com.picchealth.module.system.dao.PrivilegeUserInfoDao">

// 接口中
package com.picchealth.module.system.dao;
public interface PrivilegeUserInfoDao {...}
```

### 报错5：GaussDB驱动找不到

```
java.lang.ClassNotFoundException: org.postgresql.Driver
```

**原因分析**：缺少PostgreSQL驱动

**解决方案**：
```bash
# 确认pom.xml中有这个依赖（pdfc-parent应该已经包含了）
# 如果没有，手动添加：
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <version>42.2.5</version>
</dependency>

# 如果用的是GaussDB，需要华为专有驱动
<dependency>
    <groupId>com.huawei.gauss</groupId>
    <artifactId>gaussdb</artifactId>
    <version>xxx</version>
</dependency>
```

### 报错6：Swagger页面打不开

```
Whitelabel Error Page
This application has no explicit mapping for /error
```

**原因分析**：服务没启动成功，或者路径写错了

**解决方案**：
```bash
# 确认服务完全启动（日志显示Started）
# 2024-xx-xx 10:30:00.123  INFO 12345 --- [main] com.picchealth.PiccHealthPrivilegeApplication  : Started PiccHealthPrivilegeApplication

# 确认端口
# 日志中会显示 Tomcat started on port(s): 9092

# 正确访问地址：
http://localhost:9092/swagger-ui.html
http://localhost:9092/doc.html  ( Knife4j文档)
http://localhost:9092/swagger-resources  ( API列表)
```

---

## 十三、代码导航速查表

> 🏠 就像公司的组织架构图——知道找谁办事最快捷

### 场景化导航

| 你想做的事 | 去哪个文件 | 关键代码位置 |
|-----------|----------|------------|
| **登录逻辑** | `UserInfoServiceImpl.java` | 第89行 `create()`方法 |
| **修改密码** | `UserInfoServiceImpl.java` | 第507行 `update()`方法 |
| **禁用/启用用户** | `UserInfoServiceImpl.java` | 第1042行 `enableUser()`方法 |
| **重置密码** | `UserInfoServiceImpl.java` | 第1094行 `resetPassword()`方法 |
| **权限校验** | `ApiAuthorityFilter.java` | Filter过滤器层 |
| **URL权限校验** | `ApiInterceptor.java` | Interceptor拦截器层 |
| **机构管理（增删改查）** | `OrgInfoServiceImpl.java` | 第70-154行 |
| **机构树查询** | `OrgInfoServiceImpl.java` | 第462行 `getOrgTree()`方法 |
| **角色管理** | `RoleInfoServiceImpl.java` | 第63-541行 |
| **角色权限分配** | `RoleInfoServiceImpl.java` | 第387行 `setResource()`方法 |
| **菜单管理** | `MenuInfoServiceImpl.java` | 第56-575行 |
| **菜单树** | `MenuInfoServiceImpl.java` | 第309行 `getMenuTree()`方法 |
| **系统管理** | `SysInfoServiceImpl.java` | 第38行 `querySysInfo()`方法 |
| **数据迁移** | `MoveServiceImpl.java` | 第76-166行 |

### 模块→文件对应表

#### 系统模块（module/sys）

| 你要找... | 去这里 | 路径 |
|---------|-------|------|
| 用户Service | UserInfoServiceImpl | `module/sys/service/impl/UserInfoServiceImpl.java` |
| 用户Dao | UserInfoDao | `module/system/dao/UserInfoDao.java` |
| 用户PO | PrivilegeUserInfo | `module/system/po/PrivilegeUserInfo.java` |
| 用户VO | UserInfoVo | `module/sys/vo/UserInfoVo.java` |
| 用户DTO | PrivilegeUserInfoDto | `module/sys/dto/PrivilegeUserInfoDto.java` |
| 机构Service | OrgInfoServiceImpl | `module/sys/service/impl/OrgInfoServiceImpl.java` |
| 机构Dao | OrgInfoDao | `module/system/dao/OrgInfoDao.java` |
| 机构PO | PrivilegeOrgInfo | `module/system/po/PrivilegeOrgInfo.java` |
| 账号记录Service | AccountRecordServiceImpl | `module/sys/service/impl/AccountRecordServiceImpl.java` |
| 敏感词Service | SensitiveWordsServiceImpl | `module/sys/service/impl/SensitiveWordsServiceImpl.java` |
| 系统信息Service | SysInfoServiceImpl | `module/sys/service/impl/SysInfoServiceImpl.java` |
| 迁移Service | MoveServiceImpl | `module/sys/service/impl/MoveServiceImpl.java` |

#### 角色模块（module/role）

| 你要找... | 去这里 | 路径 |
|---------|-------|------|
| 角色Service | RoleInfoServiceImpl | `module/role/service/impl/RoleInfoServiceImpl.java` |
| 角色Dao | RoleInfoDao | `module/role/dao/RoleInfoDao.java` |
| 角色PO | PrivilegeRoleInfo | `module/role/po/PrivilegeRoleInfo.java` |
| 角色资源关联PO | PrivilegeRoleResource | `module/role/po/PrivilegeRoleResource.java` |

#### 菜单模块（module/menu）

| 你要找... | 去这里 | 路径 |
|---------|-------|------|
| 菜单Service | MenuInfoServiceImpl | `module/menu/service/impl/MenuInfoServiceImpl.java` |
| 菜单Dao | MenuInfoDao | `module/menu/dao/MenuInfoDao.java` |
| 菜单PO | PrivilegeMenuInfo | `module/menu/po/PrivilegeMenuInfo.java` |

#### 配置层（config）

| 你要找... | 去这里 | 路径 |
|---------|-------|------|
| Token校验过滤器 | ApiAuthorityFilter | `config/ApiAuthorityFilter.java` |
| 权限校验拦截器 | ApiInterceptor | `config/ApiInterceptor.java` |
| Web配置 | WebMvcConfig | `config/WebMvcConfig.java` |
| Swagger配置 | SwaggerConfig | `config/SwaggerConfig.java` |

### API层→Controller对应表

| 你想调哪个接口 | Controller | 方法 | 路径 |
|-------------|-----------|------|------|
| 用户CRUD | UserInfoApi | create/update/deleteById... | `module/sys/api/UserInfoApi.java` |
| 机构管理 | OrgInfoApi | create/update/deleteAtById... | `module/sys/api/OrgInfoApi.java` |
| 角色管理 | RoleInfoApi | createRole/updateRole... | `module/role/api/RoleInfoApi.java` |
| 菜单管理 | MenuInfoApi | createMenu/updateMenu... | `module/menu/api/MenuInfoApi.java` |
| 数据迁移 | MoveApi | move/moveUserRole... | `module/sys/api/MoveApi.java` |

---

## 十四、调试技巧详解

> 🏠 调试就像侦探破案——通过各种线索找到问题的根源

### 1. 断点调试位置推荐

**场景1：调试用户登录**
```
位置：UserInfoServiceImpl.java 第89行 create()
断点条件：account.equals("要调试的账号")
```

**场景2：调试权限校验**
```
位置1：ApiAuthorityFilter.java doFilter() - 看Token是否有效
位置2：ApiInterceptor.java preHandle() - 看URL权限
位置3：UserInfoServiceImpl.java 第144行 setAuths() - 看权限组装
```

**场景3：调试机构树查询**
```
位置1：OrgInfoServiceImpl.java 第462行 getOrgTree()
位置2：OrgInfoServiceImpl.java 第690行 buildTree() - 树构建递归
```

**场景4：调试角色权限分配**
```
位置1：RoleInfoServiceImpl.java 第387行 setResource()
位置2：PrivilegeRoleResourceDao insert() - 看SQL执行
```

### 2. 日志级别调整

```bash
# 当前日志级别（从logback-spring.xml读取）
com.picchealth.module = INFO
com.picchealth.config = DEBUG

# 临时调整为DEBUG（在Apollo配置中心修改）
logging.level.com.picchealth.module = DEBUG
logging.level.com.picchealth.config = DEBUG

# 查看更详细的SQL日志
logging.level.org.mybatis = DEBUG
logging.level.com.picchealth.module.system.dao = TRACE

# 生产环境不建议开DEBUG，会产生大量日志影响性能
```

### 3. Postman接口调试示例

#### 示例1：创建用户

```http
POST http://localhost:9092/privilege/user/create
Content-Type: application/json
token: your-token-here

{
    "account": "test001",
    "userName": "测试用户",
    "orgId": "123456789",
    "password": "PICChealth@2020",
    "mobile": "13800138000"
}
```

#### 示例2：查询用户列表

```http
POST http://localhost:9092/privilege/user/queryUsers
Content-Type: application/json
token: your-token-here

{
    "pageNum": 1,
    "pageSize": 10,
    "account": "test",
    "userName": ""
}
```

#### 示例3：给用户分配角色

```http
POST http://localhost:9092/privilege/user/setRoles
Content-Type: application/json
token: your-token-here

{
    "userId": "用户ID",
    "roleIds": ["角色ID1", "角色ID2"]
}
```

#### 示例4：查询机构树

```http
POST http://localhost:9092/privilege/org/getOrgTree
Content-Type: application/json
token: your-token-here

{
    "id": "1"
}
```

### 4. Redis调试命令

```bash
# 连接Redis
redis-cli -h localhost -p 6379

# 查看所有Token（key格式：api_token:用户ID）
KEYS api_token:*

# 查看Token详情
GET api_token:用户ID

# 查看用户信息缓存
KEYS userid:*
GET userid:用户ID

# 清除指定用户的Token（强制重新登录）
DEL api_token:用户ID
DEL userid:用户ID

# 清除所有Token（所有用户重新登录）
FLUSHDB

# 查看Redis内存使用
INFO memory
```

### 5. 数据库调试技巧

```sql
-- 查看当前连接情况（GaussDB特有）
SELECT * FROM pg_stat_activity;

-- 开启SQL日志（临时）
ALTER DATABASE picc_health SET log_statement = 'all';

-- 查看慢查询
SELECT * FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

-- 查看表结构
\d privilege_user_info
\d privilege_role_info
\d privilege_menu_info

-- 查看索引
SELECT * FROM pg_indexes 
WHERE tablename = 'privilege_user_info';

-- 强制使用索引（调试用）
SELECT * FROM privilege_user_info 
WHERE id = 'xxx'
OPTION (INDEX (idx_user_id));
```

---

## 十五、踩坑FAQ（常见问题汇总）

> 🏠 别人踩过的坑，你可以绕过去

### Q1：为什么前端传了用户名，后端却查不到用户？

**A**：很可能你传的是`userName`但代码里查的是`account`。

```java
// 错误示例：前端传的是userName，但代码查的是account
@PostMapping("/queryUsers")
public ApiResponse queryUsers(@RequestBody PrivilegeUserInfoDto dto) {
    // 这里的account字段其实是前端传的用户名
    List<PrivilegeUserInfo> list = userInfoDao.selectByAccount(dto.getAccount());
}
```

**排查步骤**：
1. 看Swagger文档确认参数名
2. 打断点看DTO里哪个字段有值
3. 看VO/DTO的注释，字段可能有误导性命名

---

### Q2：为什么角色创建成功了，但没权限？

**A**：创建角色后，还需要调用`setResource`接口分配菜单权限！

```java
// 创建角色的两个步骤：
// 步骤1：创建角色基本信息
roleInfoApi.createRole(roleCreateVo);  // 返回角色ID

// 步骤2：给角色分配菜单权限（很多人忘记这一步！）
ResourceVo resourceVo = new ResourceVo();
resourceVo.setRoleId(刚才返回的角色ID);
resourceVo.setMenuIds(new String[]{"菜单1ID", "菜单2ID"});
roleInfoApi.setResource(resourceVo);
```

---

### Q3：为什么机构树只返回了两层？

**A**：`getOrgTree`默认只查直接子节点，要查完整树需要递归调用。

```java
// 查看OrgInfoServiceImpl第462行 getOrgTree()
// 这个方法只查一层：parentId = 参数id 的机构

// 要查完整树，需要：
// 1. 调用getOrgTree("1") 获取根节点下的直接子机构
// 2. 对每个子机构，递归调用getOrgTree(子机构ID)
// 3. 循环直到没有子机构

// 建议直接调用 getPartOrgTree("1") - 这个方法会递归查完整树
```

---

### Q4：为什么用户的权限总是没生效？

**A**：可能是缓存问题，用户权限会缓存到Redis。

```bash
# 清除用户权限缓存
redis-cli DEL userid:用户ID

# 或者清除所有缓存
redis-cli FLUSHDB

# 然后重新登录，让系统重新计算权限
```

---

### Q5：为什么修改了机构信息，查询还是旧数据？

**A**：机构信息有缓存，更新后需要清理缓存。

```java
// 查看OrgInfoServiceImpl中是否有缓存注解
// 如果有@CacheEvict，更新后会自动清理
// 如果没有，需要手动清理：

// 方案1：清除所有机构缓存
redis-cli KEYS "org*"
redis-cli DEL `redis-cli KEYS "org*" | tr '\n' ' '`

// 方案2：等待缓存过期（默认TTL）
// 查看缓存配置的过期时间
```

---

### Q6：为什么分页查询pageNum=0没数据？

**A**：PageHelper的pageNum从1开始，不是从0开始。

```java
// 错误：
PageHelper.startPage(0, 10);  // pageNum=0 会被当成"不分页"
// 结果：返回所有数据

// 正确：
PageHelper.startPage(1, 10);  // pageNum=1，第一页
PageHelper.startPage(2, 10);  // pageNum=2，第二页

// 前端注意：
// - pageNum最小传1
// - pageSize建议传10/20/50，不要传太大
// - 总页数 = total / pageSize
```

---

### Q7：为什么密码总是验证失败？

**A**：密码是SM4加密存储的，验证时也需要加密后比对。

```java
// 用户注册/修改密码时
String encryptedPassword = SM4Util.sm4Encrypt(明文密码);
user.setPassword(encryptedPassword);

// 用户登录时
String encryptedInput = SM4Util.sm4Encrypt(用户输入的密码);
if (!encryptedInput.equals(storedPassword)) {
    throw new CustomException("密码错误");
}

// 如果你直接存明文或MD5，登录永远成功不了
```

---

### Q8：为什么删除用户后，用户还能登录？

**A**：这是软删除，只是标记了delete_at字段，用户记录还在。

```java
// 错误的理解：
// deleteById() 只是设置了 delete_at 字段
// 用户记录没有物理删除
// 用户还能用原账号密码登录（如果Token还有效的话）

// 正确的做法：
// 1. 删除用户
userInfoService.deleteById(userId);

// 2. 清除用户Token缓存（重要！）
redis-cli DEL api_token:用户ID
redis-cli DEL userid:用户ID

// 3. 确保下次登录会失败
// （因为软删除的用户可能在某些查询中被过滤掉）
```

---

### Q9：为什么接口返回401未授权？

**A**：常见原因有三个，按顺序排查：

```bash
# 原因1：Token过期
# 解决：重新登录获取新Token

# 原因2：Token格式不对
# 检查请求头：token: xxx（不是Authorization: Bearer xxx）

# 原因3：接口被Token校验拦截了
# ApiAuthorityFilter只拦截 /privilege/user/* 路径
# 其他路径不需要token也能访问
```

---

### Q10：为什么Apollo配置改了不生效？

**A**：Apollo配置需要发布才能生效，且服务需要重启或等待拉取。

```bash
# Apollo配置生效流程：
# 1. 在Apollo界面修改配置
# 2. 点击"发布"按钮（不点发布，配置不会生效！）
# 3. Apollo通知服务拉取新配置
# 4. 服务端收到通知，更新配置

# 如果改了配置不生效，检查：
# 1. 确认点过"发布"按钮
# 2. 确认发布的环境是对的（dev/test/prod）
# 3. 重启服务强制拉取配置

# 本地开发时Apollo配置路径：
# Apollo地址：10.57.16.41:8080
# AppId：picc-mzmtb-user
# 环境：DEV
```

---

### Q11：为什么新增的字段数据库里没有？

**A**：本地数据库和Apollo配置不同步，需要手动同步DDL。

```bash
# 检查pom.xml中flyway或mybatis版本
# 如果有数据库版本管理工具，可能需要执行迁移脚本

# 手动同步：
# 1. 找DBA导出生产DDL
# 2. 在本地执行DDL
# 3. 或者让DBA在测试环境执行，你连接测试环境

# 注意：
# 千万不能在生产环境手动执行DDL！
# 所有DDL变更必须走审批流程
```

---

### Q12：为什么启动时总是报"MyBatis Mapper XML not found"？

**A**：Mapper XML的位置和pom.xml中配置的不一致。

```bash
# 标准Mapper XML位置：
# picchealth-privilege-db/src/main/resources/mapper/**/*.xml

# 检查pom.xml中mybatis mapper-locations配置：
mybatis:
  mapper-locations: classpath:mapper/**/*.xml

# 如果你的XML放到了其他地方，需要修改这个配置

# 常见错误位置：
# ❌ src/main/resources/mapper/UserInfoMapper.xml (对)
# ❌ src/main/java/mapper/UserInfoMapper.xml (错)
# ❌ src/main/resources/com/picchealth/.../UserInfoMapper.xml (错)
```

---

### 附加提示：遇到问题时的排查顺序

```
1. 看日志：从日志中找到ERROR/EXCEPTION信息
         日志路径：/data/log/app/picc-mzmtb-user-*.log

2. 看配置：确认Apollo配置是否正确
         特别检查：数据库连接、Redis地址、端口号

3. 看网络：确认VPN是否连接、端口是否通
         telnet 10.57.16.41 8080 (Apollo)
         telnet 数据库地址 5432

4. 问同事：问下其他人是否遇到同样问题
         可能是共性问题，已经有人解决了

5. 提工单：如果确认是基础设施问题
         提给人保IT运维处理
```
