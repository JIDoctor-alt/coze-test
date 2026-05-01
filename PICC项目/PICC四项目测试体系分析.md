# PICC四项目测试体系全面分析报告

## 📋 文档概述

| 项目 | 技术栈 | 测试现状 | 测试评分 |
|------|--------|----------|----------|
| 权限服务 (picc-mzmtb-user) | Spring Boot | ⚠️ 基础测试 | ⭐⭐ 2/10 |
| 业务服务 (picc-mzmtb-server) | Spring Boot + Maven多模块 | ⚠️ 少量测试 | ⭐⭐ 2/10 |
| 前台服务 (picc-mzmtb-gateway) | Spring Boot | ❌ 无测试 | ⭐ 1/10 |
| 前端 (picc-mzmtb-agent) | Vue 2 | ❌ 无测试 | ⭐ 1/10 |

---

## 🎯 Part 1：现有测试代码扫描

### 1.1 权限服务 (picc-mzmtb-user)

#### 📁 项目结构
```
picc-mzmtb-user/
├── picchealth-privilege-server/
│   ├── src/main/java/com/picchealth/
│   │   ├── module/
│   │   │   ├── menu/      # 菜单模块
│   │   │   ├── role/      # 角色模块
│   │   │   └── sys/        # 系统模块
│   │   └── utils/         # 工具类
│   └── src/test/          # ⚠️ 测试目录
└── picchealth-privilege-db/  # 数据库模块
```

#### 🔍 测试代码扫描结果

| 测试文件 | 类型 | 说明 |
|----------|------|------|
| `PrivilegeMoveTest.java` | 数据迁移测试 | 使用 `@SpringBootTest` + `@RunWith(SpringRunner.class)` |

#### 📝 权限服务测试代码详情

```java
// 文件位置: src/test/java/com/picchealth/module/PrivilegeMoveTest.java
package com.picchealth.module;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit4.SpringRunner;

@RunWith(SpringRunner.class)
@SpringBootTest(classes = PrivilegeSpringBootApplication.class)
public class PrivilegeMoveTest {
    
    @Resource
    private SysRoleModuleRelDao sysRoleModuleRelDao;
    
    @Test
    public void move() {
        // 数据迁移逻辑测试
    }
    
    @Test
    public void moveUserRole() {
        // 用户角色迁移测试
    }
    
    @Test
    public void passwordBackMD5() {
        // 密码解密测试
    }
}
```

#### 📊 权限服务统计

| 指标 | 数量 |
|------|------|
| Service 类 | 25 |
| Controller 类 | 0 |
| 测试类 | 1 |
| 测试方法 | 3 |
| 测试覆盖率 | **约 4%** |

---

### 1.2 业务服务 (picc-mzmtb-server)

#### 📁 项目结构（多模块架构）
```
picc-mzmtb-server/
├── mtb-yh/                    # 业务子模块
│   ├── mtb-base/             # 基础模块
│   ├── mtb-bj/               # 北京分模块
│   ├── mtb-dez/              # 德宏分模块
│   ├── mtb-dz/               # 大理分模块
│   ├── mtb-hn/               # 河南分模块
│   ├── mtb-jc/               # 基层分模块
│   ├── mtb-jj/               # 竞价分模块
│   ├── mtb-mzl/              # 门诊量分模块
│   ├── mtb-sl/               # 生理分模块
│   ├── mtb-xya/              # 协议分模块
│   ├── mtb-ya/               # 延安分模块
│   ├── mtb-yl/               # 养老分模块
│   └── mtb-yli/              # 义马分模块
├── picchealth-server/         # 主服务
│   ├── src/main/java/
│   │   └── com/picchealth/module/
│   │       ├── basedoc/      # 基础文档
│   │       ├── call/         # 外部调用
│   │       ├── dpview/       # 数据展示
│   │       ├── drugstore/    # 药店模块
│   │       ├── logaudit/     # 日志审计
│   │       ├── mb/           # 慢病模块
│   │       ├── mtb/          # 核心业务模块
│   │       ├── restful/      # REST API
│   │       ├── scheduling/   # 调度任务
│   │       ├── thirdfee/     # 第三方费用
│   │       └── webservice/   # Web服务
│   └── src/test/             # ⚠️ 测试目录
└── picchealth-db/            # 数据库模块
```

#### 🔍 测试代码扫描结果

| 测试文件 | 类型 | 说明 |
|----------|------|------|
| `MtbVipIntelligentAuditLockTest.java` | 并发锁测试 | 测试读写锁并发 |
| `QuerySyBalanceTest.java` | 外部服务测试 | 测试查询余额 |
| `LexusCallServiceTest.java` | 服务调用测试 | 测试服务间调用 |
| `DrugOrderTest.java` | 订单测试 | 测试药品订单 |
| `RedisUtilTest.java` | 工具类测试 | Redis工具测试 |
| `test1.java` | 示例测试 | 占位测试 |

#### 📝 业务服务测试代码详情

**示例1: 并发锁测试 (MtbVipIntelligentAuditLockTest.java)**

```java
@SpringBootTest(classes = LinkSpringBootApplication.class)
@RunWith(SpringRunner.class)
@Slf4j
public class MtbVipIntelligentAuditLockTest {

    @Resource
    private MtbVipIntelligentAuditLockServiceImpl auditLockService;

    @Resource
    private RedissonClient redissonClient;

    @Test
    @DisplayName("测试多个查询可以并发执行（读锁共享）")
    public void testReadLockConcurrency() throws InterruptedException {
        int threadCount = 5;
        CountDownLatch startLatch = new CountDownLatch(1);
        // ... 并发测试逻辑
        assertTrue("读锁应该支持并发", maxConcurrency.get() > 1);
    }

    @Test
    @DisplayName("测试读写锁互斥：写锁会阻塞读锁")
    public void testReadWriteLockMutualExclusion() {
        // ... 读写锁互斥测试
        assertFalse(readLockAcquired.get(), "写锁持有期间，读锁应该无法获取");
    }
}
```

**特点分析：**
- ✅ 使用 `@DisplayName` 描述性测试名称
- ✅ 测试并发场景（CountDownLatch）
- ✅ 使用 JUnit 5 断言 `assertTrue/assertFalse`
- ✅ 测试分布式锁（Redisson）

#### 📊 业务服务统计

| 指标 | 数量 |
|------|------|
| Service 类 | 445 |
| Controller 类 | 0 |
| 测试类 | 6 |
| 测试方法 | 约 10+ |
| 测试覆盖率 | **< 1%** |

---

### 1.3 前台服务 (picc-mzmtb-gateway)

#### 📁 项目结构
```
picc-mzmtb-gateway/
├── src/main/java/com/picchealth/
│   ├── module/
│   │   ├── base/             # 基础模块
│   │   ├── call/            # 调用服务
│   │   ├── claim/           # 理赔模块
│   │   ├── drugstore/       # 药店模块
│   │   ├── mb/              # 慢病模块
│   │   ├── mtb/             # 核心业务
│   │   ├── restful/         # REST API
│   │   └── ...（共19个模块）
│   └── LinkSpringBootApplication.java
└── pom.xml                  # ⚠️ skipTests=true
```

#### 🔍 测试扫描结果

| 扫描项 | 结果 |
|--------|------|
| 测试类 | ❌ **0个** |
| 测试目录 | ❌ 不存在 |
| 测试配置 | ⚠️ `skipTests=true` |

#### 📊 前台服务统计

| 指标 | 数量 |
|------|------|
| Service 类 | 32 |
| Controller 类 | 0 |
| 测试类 | 0 |
| 测试覆盖率 | **0%** |

---

### 1.4 前端 (picc-mzmtb-agent)

#### 📁 项目结构
```
picc-mzmtb-agent/
├── src/
│   ├── api/                 # 65+ API接口文件
│   ├── assets/              # 静态资源
│   ├── components/          # 通用组件
│   ├── pages/               # 页面组件
│   │   ├── Declare/         # 申报模块
│   │   ├── ChronicDis/      # 慢病模块
│   │   ├── Drugstore/       # 药店模块
│   │   ├── Hospital/        # 医院模块
│   │   └── Payment/         # 支付模块
│   ├── router/              # 路由配置
│   ├── store/               # Vuex状态管理
│   └── utils/               # 工具函数
├── package.json             # ⚠️ 无测试依赖
└── build/                   # 构建配置
```

#### 🔍 测试扫描结果

| 扫描项 | 结果 | 说明 |
|--------|------|------|
| Jest 配置 | ❌ | 无 jest.config.js |
| Mocha 配置 | ❌ | 无 mocha 配置 |
| 测试文件 | ❌ | 无 .spec.js/.test.js |
| 测试依赖 | ❌ | package.json 无测试库 |
| E2E测试 | ❌ | 无 Cypress/Nightwatch |

#### 📊 前端统计

| 指标 | 数量 |
|------|------|
| Vue 组件 | 652 |
| JS 文件 | 213 |
| API 文件 | 65+ |
| 测试文件 | 0 |
| 测试覆盖率 | **0%** |

#### 📝 package.json 分析

```json
{
  "scripts": {
    "test": "node build/build.js test",    // ⚠️ 只是构建命令
    "dev": "node build/build.js dev",
    "build": "node --max_old_space_size=4096 build/build.js"
  },
  "dependencies": {
    "vue": "^2.6.11",
    "vue-router": "^3.3.4",
    "vuex": "^3.0.1",
    "axios": "^0.19.2"
  },
  "devDependencies": {
    // ❌ 无 jest、mocha、chai 等测试依赖
  }
}
```

---

## 🎯 Part 2：测试覆盖率评估

### 2.1 覆盖率评分标准

| 评分 | 覆盖率范围 | 说明 |
|------|------------|------|
| ⭐⭐⭐⭐⭐ | 80%+ | 优秀，覆盖充分 |
| ⭐⭐⭐⭐ | 60-79% | 良好，需要补充 |
| ⭐⭐⭐ | 40-59% | 一般，亟需改进 |
| ⭐⭐ | 20-39% | 较差，危险 |
| ⭐ | < 20% | 极差，高风险 |

### 2.2 各项目测试覆盖率评估

#### 权限服务 (picc-mzmtb-user)

| 模块 | Service数量 | 测试覆盖 | 覆盖率 |
|------|------------|----------|--------|
| role (角色) | 2 | 0 | 0% |
| sys (系统) | 8 | 1 (数据迁移) | 12.5% |
| menu (菜单) | 3 | 0 | 0% |
| **总计** | **25** | **1** | **~4%** |

**评分：⭐⭐ (20-39%)**

#### 业务服务 (picc-mzmtb-server)

| 模块 | Service数量 | 测试覆盖 | 覆盖率 |
|------|------------|----------|--------|
| mtb (核心业务) | 100+ | 1 | <1% |
| restful (API) | 20+ | 0 | 0% |
| call (外部调用) | 15+ | 3 | ~20% |
| 其他模块 | 300+ | 0 | 0% |
| **总计** | **445** | **6** | **<1%** |

**评分：⭐ (极差)**

#### 前台服务 (picc-mzmtb-gateway)

| 模块 | Service数量 | 测试覆盖 | 覆盖率 |
|------|------------|----------|--------|
| 所有模块 | 32 | 0 | 0% |

**评分：⭐ (极差)**

#### 前端 (picc-mzmtb-agent)

| 类型 | 数量 | 测试覆盖 | 覆盖率 |
|------|------|----------|--------|
| Vue组件 | 652 | 0 | 0% |
| API模块 | 65+ | 0 | 0% |
| 工具函数 | 50+ | 0 | 0% |

**评分：⭐ (极差)**

### 2.3 综合评估

```
┌─────────────────────────────────────────────────────────────┐
│                    PICC测试覆盖率综合评估                    │
├─────────────────────────────────────────────────────────────┤
│  权限服务     ████░░░░░░░░░░░░░░░░░░░░  4%     ⭐⭐          │
│  业务服务     ██░░░░░░░░░░░░░░░░░░░░░░░  <1%    ⭐           │
│  前台服务     ░░░░░░░░░░░░░░░░░░░░░░░░░  0%     ⭐           │
│  前端        ░░░░░░░░░░░░░░░░░░░░░░░░░  0%     ⭐           │
├─────────────────────────────────────────────────────────────┤
│  行业基准     ████████████████░░░░░░░░  70%    ⭐⭐⭐⭐       │
└─────────────────────────────────────────────────────────────┘
```

**行业对比：**
- 金融保险行业测试覆盖率基准：**≥60%**
- PICC当前综合覆盖率：**<2%**
- **差距：98%以上**

---

## 🎯 Part 3：关键业务测试建议

### 3.1 申报流程的完整状态流转测试

#### 🔍 业务背景
申报流程是PICC系统的核心业务，涉及：
- 慢病申报
- 大病申报
- 离线申报
- 专家申报
- 快速申报

#### 📋 建议测试场景

| 测试场景 | 输入 | 预期结果 | 测试目的 |
|----------|------|----------|----------|
| 草稿→暂存 | 空表单 | 保存成功 | 验证草稿保存 |
| 暂存→待提交 | 完整信息 | 状态变更 | 验证状态流转 |
| 待提交→审核中 | 点击提交 | 审核队列 | 验证提交流程 |
| 审核中→审核通过 | 审核通过 | 状态更新 | 验证审核通过 |
| 审核中→审核拒绝 | 审核拒绝+原因 | 驳回通知 | 验证审核拒绝 |
| 审核通过→支付中 | 发起支付 | 支付状态 | 验证支付触发 |
| 支付中→已支付 | 支付成功 | 完成状态 | 验证支付完成 |
| 超时自动取消 | 24小时无操作 | 自动作废 | 验证超时机制 |

#### 🧪 测试用例设计（不写代码）

**测试用例TC001：申报状态完整正向流转**
```
前置条件：
- 用户已登录
- 医保账户余额充足
- 网络连接正常

测试步骤：
1. 进入"新建申报"页面
2. 填写申报信息（姓名、身份证、疾病类型）
3. 上传必要的证件照片
4. 点击"保存草稿"
5. 验证页面显示"草稿"状态
6. 点击"提交申报"
7. 验证页面显示"待审核"状态
8. 使用审核账号登录
9. 进入审核列表
10. 点击"通过"按钮
11. 验证页面显示"审核通过"状态
12. 触发支付流程
13. 完成支付
14. 验证页面显示"已完成"状态

预期结果：
- 每个状态变更都有明确的提示
- 状态历史可追溯
- 时间戳准确记录
```

**测试用例TC002：申报状态异常流转**
```
测试场景：重复提交审核
前置条件：存在一条"待审核"状态的申报

测试步骤：
1. 进入待审核申报详情页
2. 连续点击"提交"按钮3次
3. 观察系统响应

预期结果：
- 系统应阻止重复提交
- 仅生成一条申报记录
- 提示"该申报已在审核中"
```

**测试用例TC003：超时取消状态流转**
```
测试场景：申报超时未处理
前置条件：存在一条"待审核"超过24小时的申报

测试步骤：
1. 等待系统自动处理（或模拟时间）
2. 查询该申报的状态

预期结果：
- 系统自动将状态变更为"已取消"
- 发送超时通知
- 记录取消原因
```

---

### 3.2 支付流程的并发测试

#### 🔍 业务背景
支付涉及资金安全，需要测试：
- 多用户同时支付
- 幂等性验证
- 库存锁定
- 超时处理

#### 📋 建议测试场景

| 测试场景 | 并发数 | 测试重点 |
|----------|--------|----------|
| 同一订单多次支付 | 10 | 防重复支付 |
| 余额不足并发 | 100 | 准确扣款 |
| 超时未支付 | 1 | 库存释放 |
| 网络异常中断 | 5 | 事务回滚 |
| 第三方回调失败 | 3 | 重试机制 |

#### 🧪 测试用例设计（不写代码）

**测试用例TC004：防重复支付测试**
```
测试目标：验证同一订单不能被支付两次

前置条件：
- 存在一条待支付订单，订单号：ORDER_20240101_001
- 账户余额：1000元
- 订单金额：500元

测试步骤：
1. 启动10个并发线程
2. 同时调用支付接口
3. 记录每个请求的响应
4. 查询最终订单状态
5. 查询账户余额变化

预期结果：
- 只有1个请求返回"支付成功"
- 其他9个请求返回"订单已支付"或"订单不存在"
- 账户只扣款500元
- 订单状态为"已支付"
```

**测试用例TC005：并发扣款准确性**
```
测试目标：验证高并发下余额扣减准确

前置条件：
- 账户A余额：10000元
- 100个并发请求，每个扣款100元

测试步骤：
1. 启动100个并发线程
2. 同时发起扣款请求
3. 记录每个请求的执行时间
4. 查询最终账户余额

预期结果：
- 所有请求执行完成
- 账户余额：10000 - 100*100 = 0元
- 不出现负数余额
- 不出现超扣现象
```

---

### 3.3 Token认证的边界测试

#### 🔍 业务背景
系统使用Token进行认证，涉及：
- 用户登录Token
- API访问Token
- Token刷新机制
- Token失效处理

#### 📋 建议测试场景

| 测试场景 | 输入 | 预期结果 |
|----------|------|----------|
| 正常登录 | 正确用户名密码 | 返回有效Token |
| 错误密码 | 错误密码 | 拒绝登录 |
| Token过期 | 过期Token | 返回401 |
| Token刷新 | 即将过期Token | 返回新Token |
| 伪造Token | 随机字符串 | 拒绝访问 |
| 重复使用Token | 同一Token两次 | 第二次拒绝 |
| Token部分篡改 | 修改Token尾部 | 拒绝访问 |

#### 🧪 测试用例设计（不写代码）

**测试用例TC006：Token有效期内正常访问**
```
测试目标：验证有效Token可正常访问

前置条件：
- 用户已登录，获取Token：eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
- Token有效期：2小时

测试步骤：
1. 使用Token调用用户信息接口
2. 使用Token调用申报列表接口
3. 使用Token调用支付接口

预期结果：
- 所有接口返回200
- 响应数据正确
- 请求头中Token被正确解析
```

**测试用例TC007：Token过期处理**
```
测试目标：验证Token过期后的正确处理

前置条件：
- 存在一个已过期的Token
- Token过期时间：2024-01-01 00:00:00

测试步骤：
1. 使用过期Token调用任意接口
2. 观察系统响应

预期结果：
- 返回401 Unauthorized
- 响应体包含错误码：AUTH_TOKEN_EXPIRED
- 提示信息："Token已过期，请重新登录"
```

**测试用例TC008：Token刷新机制**
```
测试目标：验证Token即将过期时的自动刷新

前置条件：
- Token过期时间：当前时间 + 5分钟

测试步骤：
1. 调用任意业务接口
2. 观察响应头

预期结果：
- 返回新的Refresh-Token
- 业务接口正常返回
- 新Token有效期延长2小时
```

---

### 3.4 前端表单校验测试

#### 🔍 业务背景
前端使用Vue 2 + Ant Design Vue，涉及：
- 申报表单
- 用户信息表单
- 支付信息表单

#### 📋 建议测试场景

| 测试场景 | 输入 | 预期结果 |
|----------|------|----------|
| 身份证格式 | 15位/18位正确格式 | 校验通过 |
| 身份证错误 | 字母开头/位数不足 | 提示格式错误 |
| 手机号格式 | 11位正确格式 | 校验通过 |
| 手机号错误 | 10位/字母 | 提示格式错误 |
| 必填项为空 | 姓名为空 | 提示必填 |
| 金额格式 | 正数/两位小数 | 校验通过 |
| 金额错误 | 负数/多位小数 | 提示格式错误 |
| 特殊字符 | <script>alert(1)</script> | 过滤或拒绝 |

#### 🧪 测试用例设计（不写代码）

**测试用例TC009：身份证号格式校验**
```
测试目标：验证身份证号格式校验

测试数据：
- 正确格式：110101199001011234（18位）
- 错误格式1：123（位数不足）
- 错误格式2：123456789012345678（纯数字18位，校验位错误）
- 错误格式3：ABCD123456789012（字母）

测试步骤：
1. 进入申报表单页面
2. 输入正确的身份证号
3. 点击下一步
4. 清空，输入错误格式1
5. 点击下一步
6. 观察错误提示
7. 重复步骤2-6，测试其他错误格式

预期结果：
- 正确格式：通过
- 错误格式：显示"身份证号格式不正确"
- 不提交表单
```

**测试用例TC010：XSS注入防护**
```
测试目标：验证前端对XSS攻击的防护

测试数据：
- <script>alert('xss')</script>
- <img src=x onerror=alert(1)>
- <svg onload=alert('xss')>
- ' OR '1'='1

测试步骤：
1. 在任意文本输入框输入XSS payload
2. 提交表单
3. 查看数据库存储的内容
4. 在列表页面查看显示效果

预期结果：
- 特殊字符被转义或过滤
- 不执行JavaScript代码
- 页面正常显示文本内容
```

---

### 3.5 API接口异常场景测试

#### 🔍 业务背景
系统有65+个API接口，需要测试异常场景

#### 📋 建议测试场景

| 测试场景 | 测试方法 |
|----------|----------|
| 参数为空 | 各必填参数传空值 |
| 参数类型错误 | 期望String传Number |
| 参数超长 | 输入超长字符串 |
| 特殊字符 | SQL注入/XSS |
| 并发请求 | 多线程同时调用 |
| 服务不可用 | 模拟下游服务故障 |
| 超时处理 | 设置短超时 |
| 限流测试 | 超过QPS限制 |

#### 🧪 测试用例设计（不写代码）

**测试用例TC011：参数为空场景**
```
接口：POST /api/declare/submit
Content-Type: application/json

测试数据：
- 参数：name (String, 必填)
- 参数：idCard (String, 必填)
- 参数：amount (Number, 必填)

测试步骤：
1. 发送请求，name=""，其他正常
2. 发送请求，idCard=null，其他正常
3. 发送请求，amount=""，其他正常

预期结果：
- 返回400 Bad Request
- 响应体包含错误详情
- 提示哪个参数缺失
```

**测试用例TC012：SQL注入测试**
```
测试数据：
- ' OR '1'='1
- '; DROP TABLE users;--
- 1' AND '1'='1

测试步骤：
1. 在搜索接口输入SQL注入语句
2. 在查询参数输入SQL注入语句
3. 观察响应

预期结果：
- 不执行SQL语句
- 返回正常结果或空结果
- 不暴露数据库错误信息
```

---

## 🎯 Part 4：测试策略建议

### 4.1 单元测试规范

#### 📖 什么是单元测试？（小白解释）

```
🏭 想象一下汽车工厂...

单元测试 = "出厂前每个零件单独检查"

比如检查：
- 螺丝能不能拧紧
- 轮胎会不会漏气
- 方向盘能不能转动
- 发动机能不能启动

每个零件单独测试，不依赖其他零件！
```

#### 📋 Java单元测试规范

**1. 测试框架选择**
```xml
<!-- 推荐：JUnit 5 + Mockito -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

**2. 测试代码位置**
```
src/main/java/
└── com/picchealth/module/
    └── role/
        ├── service/
        │   └── RoleInfoService.java      ← 业务代码
        └── service/
            └── RoleInfoServiceTest.java  ← 测试代码（同级目录）
```

**3. 测试命名规范**
```java
// ✅ 正确：方法名_场景_预期结果
@Test
void saveRole_WithValidData_ShouldReturnSuccess() {}

@Test
void saveRole_WithDuplicateName_ShouldThrowException() {}

// ❌ 错误：模糊不清
@Test
void test1() {}
@Test
void save() {}
```

**4. 测试结构（Given-When-Then）**
```java
@Test
void saveRole_WithValidData_ShouldReturnSuccess() {
    // ========== Given（准备测试数据）==========
    RoleInfo role = new RoleInfo();
    role.setName("测试角色");
    role.setCode("TEST001");
    
    // ========== When（执行被测试的方法）==========
    RoleInfo result = roleInfoService.saveRole(role);
    
    // ========== Then（验证结果）==========
    assertNotNull(result.getId());
    assertEquals("测试角色", result.getName());
    assertEquals("TEST001", result.getCode());
}
```

**5. Mock使用规范**
```java
@ExtendWith(MockitoExtension.class)
class RoleInfoServiceTest {
    
    @Mock
    private RoleInfoDao roleInfoDao;  // 模拟DAO层
    
    @InjectMocks
    private RoleInfoService roleInfoService;
    
    @Test
    void findRole_WithValidId_ShouldReturnRole() {
        // Given
        RoleInfo expectedRole = new RoleInfo();
        expectedRole.setId("123");
        expectedRole.setName("管理员");
        
        when(roleInfoDao.findById("123")).thenReturn(expectedRole);
        
        // When
        RoleInfo result = roleInfoService.findRole("123");
        
        // Then
        assertEquals("管理员", result.getName());
        verify(roleInfoDao, times(1)).findById("123");
    }
}
```

#### 📋 前端单元测试规范（Vue 2）

**1. 测试框架选择**
```bash
# 推荐：Jest + Vue Test Utils
npm install --save-dev jest @vue/test-utils babel-jest jest-transform-stub
```

**2. Jest配置（jest.config.js）**
```javascript
module.exports = {
  preset: '@vue/cli-plugin-unit-jest',
  testMatch: [
    '**/src/**/*.spec.js',
    '**/src/**/*.test.js'
  ],
  collectCoverage: true,
  collectCoverageFrom: [
    'src/**/*.{js,vue}',
    '!src/main.js'
  ]
}
```

**3. Vue组件测试示例**
```javascript
// src/components/DeclareForm.spec.js
import { mount } from '@vue/test-utils'
import DeclareForm from './DeclareForm.vue'

describe('DeclareForm.vue', () => {
  it('表单验证 - 身份证号格式', () => {
    const wrapper = mount(DeclareForm)
    
    // 找到身份证输入框
    const input = wrapper.find('input[id="idCard"]')
    
    // 输入错误格式
    input.setValue('123')
    
    // 点击提交
    wrapper.find('button[type="submit"]').trigger('click')
    
    // 验证错误提示
    expect(wrapper.text()).toContain('身份证号格式不正确')
  })
  
  it('表单提交 - 正确数据', async () => {
    const wrapper = mount(DeclareForm, {
      mocks: {
        $api: {
          submitDeclare: jest.fn().mockResolvedValue({ success: true })
        }
      }
    })
    
    // 填写表单
    wrapper.find('input[id="name"]').setValue('张三')
    wrapper.find('input[id="idCard"]').setValue('110101199001011234')
    
    // 提交
    await wrapper.find('button[type="submit"]').trigger('click')
    
    // 验证
    expect(wrapper.emitted('submit')).toBeTruthy()
  })
})
```

---

### 4.2 集成测试规范

#### 📖 什么是集成测试？（小白解释）

```
🏭 继续汽车工厂的故事...

集成测试 = "把零件组装起来看能不能跑"

比如：
- 发动机 + 变速箱 能不能配合工作
- 方向盘 + 轮胎 能不能让车转弯
- 刹车 + 车轮 能不能让车停下

把多个零件组合起来测试，看整体能不能工作！
```

#### 📋 Spring Boot集成测试规范

**1. 集成测试配置**
```java
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = LinkSpringBootApplication.class
)
@AutoConfigureMockMvc
class DeclareIntegrationTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Autowired
    private DeclareService declareService;
    
    @Test
    void testDeclareFlow_FromCreateToSubmit() {
        // 1. 创建申报
        Declare declare = new Declare();
        declare.setName("测试申报");
        Declare saved = declareService.save(declare);
        
        // 2. 提交申报
        declareService.submit(saved.getId());
        
        // 3. 验证状态
        Declare updated = declareService.findById(saved.getId());
        assertEquals("待审核", updated.getStatus());
    }
}
```

**2. 数据库测试配置**
```properties
# src/test/resources/application-test.yml
spring:
  datasource:
    url: jdbc:h2:mem:testdb
    driver-class-name: org.h2.Driver
  jpa:
    hibernate:
      ddl-auto: create-drop
  redis:
    host: localhost
    port: 6379
```

**3. 事务管理（测试后回滚）**
```java
@SpringBootTest
@Transactional  // 测试结束后自动回滚
class DeclareIntegrationTest {
    
    @Test
    void testDeclareCreation() {
        // 所有操作都会在测试后回滚
        // 不会污染数据库
    }
}
```

---

### 4.3 API自动化测试方案

#### 📖 什么是API测试？（小白解释）

```
📡 API测试 = "用工具模拟客户端调用服务器"

就像：
- 你用Postman点按钮测试接口
- 或者写代码自动调用接口
- 不用打开浏览器，也不用打开App

自动跑一堆接口，检查返回对不对！
```

#### 📋 工具推荐

| 工具 | 适用场景 | 难度 | 推荐指数 |
|------|----------|------|----------|
| **Apifox** | 团队协作、API管理 | ⭐ | ⭐⭐⭐⭐⭐ |
| **Postman** | 个人调试 | ⭐⭐ | ⭐⭐⭐⭐ |
| **JMeter** | 性能测试 | ⭐⭐⭐ | ⭐⭐⭐ |
| **RestAssured** | Java代码API测试 | ⭐⭐ | ⭐⭐⭐⭐ |

#### 📋 Apifox使用建议

**1. 项目结构**
```
PICC-API-Project/
├── 环境配置/
│   ├── 开发环境
│   ├── 测试环境
│   └── 生产环境
├── 接口分组/
│   ├── 申报模块 (Declare)
│   │   ├── 创建申报 POST /api/declare
│   │   ├── 查询申报 GET /api/declare/{id}
│   │   ├── 提交申报 POST /api/declare/{id}/submit
│   │   └── 取消申报 POST /api/declare/{id}/cancel
│   ├── 支付模块 (Payment)
│   ├── 用户模块 (User)
│   └── 系统模块 (System)
└── 测试套件/
    ├── 冒烟测试
    ├── 回归测试
    └── 性能测试
```

**2. 常用接口示例**

```bash
# 创建申报
POST {{baseUrl}}/api/declare
Content-Type: application/json
Authorization: {{token}}

{
    "name": "张三",
    "idCard": "110101199001011234",
    "diseaseType": "hypertension",
    "hospitalId": "H001",
    "amount": 5000.00
}

# 预期响应：
# {
#     "code": 200,
#     "message": "success",
#     "data": {
#         "id": "DEC2024010100001",
#         "status": "草稿"
#     }
# }
```

**3. 自动化测试脚本（Apifox）**
```javascript
// 后置脚本：提取Token
const response = pm.response.json();
if (response.data && response.data.token) {
    pm.collectionVariables.set("token", response.data.token);
}

// 断言脚本
pm.test("响应状态码为200", function() {
    pm.response.to.have.status(200);
});

pm.test("返回成功", function() {
    var jsonData = pm.response.json();
    pm.expect(jsonData.code).to.eql(200);
});

pm.test("申报ID存在", function() {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.id).to.be.a('string');
});
```

---

### 4.4 前端E2E测试方案

#### 📖 什么是E2E测试？（小白解释）

```
🎮 E2E测试 = "模拟真实用户从头到尾走一遍"

就像：
- 有人帮你玩一遍游戏
- 看你点击后页面会不会动
- 看填表单后数据对不对

完全模拟真实用户操作，测试整个系统！
```

#### 📋 E2E测试工具选择

| 工具 | 框架 | 难度 | 适用场景 |
|------|------|------|----------|
| **Cypress** | JS | ⭐⭐ | Vue/React应用 |
| **Playwright** | 多语言 | ⭐⭐⭐ | 复杂场景 |
| **Nightwatch** | JS | ⭐⭐ | Vue2 |

#### 📋 Cypress测试方案

**1. 安装Cypress**
```bash
cd picc-mzmtb-agent
npm install --save-dev cypress
npx cypress open
```

**2. Cypress配置（cypress.json）**
```json
{
  "baseUrl": "http://localhost:8080",
  "viewportWidth": 1920,
  "viewportHeight": 1080,
  "video": false,
  "screenshotOnRunFailure": true,
  "e2e": {
    "specPattern": "cypress/integration/**/*.spec.js"
  }
}
```

**3. 申报流程E2E测试示例**
```javascript
// cypress/integration/declare-flow.spec.js
describe('申报完整流程E2E测试', () => {
    
    beforeEach(() => {
        // 登录
        cy.visit('/login')
        cy.get('input[name="username"]').type('testuser')
        cy.get('input[name="password"]').type('password123')
        cy.get('button[type="submit"]').click()
        cy.url().should('include', '/home')
    })
    
    it('完整的申报流程', () => {
        // 1. 进入申报页面
        cy.clickMenu('申报管理', '新建申报')
        
        // 2. 填写申报表单
        cy.get('input[name="name"]').type('张三')
        cy.get('input[name="idCard"]').type('110101199001011234')
        cy.get('select[name="diseaseType"]').select('高血压')
        cy.get('input[name="hospital"]').type('北京协和医院')
        
        // 3. 上传证件照片
        cy.get('input[type="file"]').attachFile('id-card.jpg')
        
        // 4. 保存草稿
        cy.contains('保存草稿').click()
        cy.contains('保存成功').should('be.visible')
        
        // 5. 提交申报
        cy.contains('提交申报').click()
        cy.contains('确认提交').click()
        
        // 6. 验证状态
        cy.contains('待审核').should('be.visible')
        
        // 7. 验证列表显示
        cy.visit('/declare/list')
        cy.contains('张三').should('be.visible')
        cy.contains('待审核').should('be.visible')
    })
    
    it('申报表单校验', () => {
        cy.visit('/declare/new')
        
        // 不填任何内容直接提交
        cy.contains('提交申报').click()
        
        // 验证错误提示
        cy.contains('姓名为必填项').should('be.visible')
        cy.contains('身份证号为必填项').should('be.visible')
        
        // 输入错误格式
        cy.get('input[name="idCard"]').type('123')
        cy.contains('提交申报').click()
        cy.contains('身份证号格式不正确').should('be.visible')
    })
})
```

---

### 4.5 性能测试方案

#### 📖 什么是性能测试？（小白解释）

```
🚀 性能测试 = "看看系统能扛多少人同时用"

就像：
- 双十一服务器能扛多少人下单
- 页面加载要等多长时间
- 系统会不会在高并发下崩溃

测出系统的极限在哪里！
```

#### 📋 性能测试指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 响应时间 | < 2秒 | 用户可接受范围 |
| TPS | > 100 | 每秒处理交易数 |
| 成功率 | > 99.9% | 请求成功比例 |
| 并发数 | > 500 | 同时在线用户 |

#### 📋 JMeter性能测试方案

**1. 测试场景**
```
场景1：申报提交并发测试
- 并发用户：100
- 持续时间：5分钟
- 目标：TPS > 50

场景2：申报列表查询测试
- 并发用户：200
- 持续时间：10分钟
- 目标：响应时间 < 1秒

场景3：支付流程压力测试
- 并发用户：50
- 持续时间：5分钟
- 目标：无资金差错
```

**2. JMeter脚本示例**
```xml
<!-- 申报提交线程组 -->
<ThreadGroup>
    <name>申报提交压力测试</name>
    <numThreads>100</numThreads>
    <rampTime>60</rampTime>
    <duration>300</duration>
    <elementProp name="HTTPsampler">
        <stringProp name="HTTPSampler.domain">api.picc.com</stringProp>
        <stringProp name="HTTPSampler.path">/api/declare/submit</stringProp>
        <stringProp name="HTTPSampler.method">POST</stringProp>
    </elementProp>
</ThreadGroup>
```

---

### 4.6 测试环境管理

#### 📖 测试环境类型

```
🏢 环境分级：

┌─────────────────────────────────────────────────┐
│  生产环境 (Production)                          │
│  - 真实数据                                     │
│  - 用户实际使用                                 │
│  - 最高权限控制                                 │
├─────────────────────────────────────────────────┤
│  预发布环境 (Pre-Production)                    │
│  - 生产数据副本                                 │
│  - 上线前最后验证                               │
├─────────────────────────────────────────────────┤
│  UAT环境 (User Acceptance Test)                │
│  - 用户验收测试                                 │
│  - 模拟真实业务场景                             │
├─────────────────────────────────────────────────┤
│  测试环境 (Test/SIT)                           │
│  - 开发人员自测                                 │
│  - 独立数据库                                   │
├─────────────────────────────────────────────────┤
│  开发环境 (Dev)                                │
│  - 开发人员本地                                 │
│  - 快速迭代                                     │
└─────────────────────────────────────────────────┘
```

#### 📋 环境配置建议

**1. 数据库隔离**
```yaml
# 开发环境
dev:
  database:
    url: jdbc:mysql://dev-db.picc.com:3306/picc_dev
    username: dev_user
    password: dev_pass

# 测试环境
test:
  database:
    url: jdbc:mysql://test-db.picc.com:3306/picc_test
    username: test_user
    password: test_pass
```

**2. 测试数据管理**
```
test-data/
├── 申报数据/
│   ├── normal_declare.json      # 正常申报
│   ├── special_declare.json     # 特殊申报
│   └── error_declare.json       # 错误申报
├── 用户数据/
│   ├── admin_user.json          # 管理员
│   ├── normal_user.json         # 普通用户
│   └── doctor_user.json         # 医生用户
└── 支付数据/
    └── mock_payments.json        # 模拟支付数据
```

---

## 🎯 Part 5：快速上手指南

### 5.1 如何为现有Service写第一个单元测试

#### 📖 前置知识（小白解释）

```
🔧 单元测试 = "给每个方法出考题"

就像：
- 给厨师一个任务，看他做得好不好
- 给计算器一个算式，看结果对不对
- 给登录方法一个账号密码，看能不能登录

单元测试就是给代码方法"出题"，看它能不能答对！
```

#### 📝 步骤一：创建测试类

**场景：为 RoleInfoService 的 saveRole 方法写测试**

**1. 创建测试文件**
```
原文件位置：
src/main/java/com/picchealth/module/role/service/RoleInfoService.java

创建测试文件：
src/test/java/com/picchealth/module/role/service/RoleInfoServiceTest.java
```

**2. 编写测试代码**
```java
package com.picchealth.module.role.service;

import com.picchealth.module.role.po.PrivilegeRoleInfo;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class RoleInfoServiceTest {

    @Mock
    private RoleInfoDao roleInfoDao;
    
    @InjectMocks
    private RoleInfoService roleInfoService;

    @Test
    void saveRole_WithValidData_ShouldReturnSavedRole() {
        // ========== 准备测试数据 (Given) ==========
        PrivilegeRoleInfo inputRole = new PrivilegeRoleInfo();
        inputRole.setName("测试角色");
        inputRole.setCode("TEST001");
        inputRole.setOrgId("ORG001");
        
        PrivilegeRoleInfo savedRole = new PrivilegeRoleInfo();
        savedRole.setId("ROLE123");
        savedRole.setName("测试角色");
        savedRole.setCode("TEST001");
        savedRole.setOrgId("ORG001");
        
        // 设置DAO的mock行为
        when(roleInfoDao.insert(any(PrivilegeRoleInfo.class))).thenReturn(1);
        when(roleInfoDao.findById("ROLE123")).thenReturn(savedRole);
        
        // ========== 执行被测试的方法 (When) ==========
        PrivilegeRoleInfo result = roleInfoService.saveRole(inputRole);
        
        // ========== 验证结果 (Then) ==========
        assertNotNull(result);
        assertEquals("测试角色", result.getName());
        assertEquals("TEST001", result.getCode());
        
        // 验证方法被调用了一次
        verify(roleInfoDao, times(1)).insert(any(PrivilegeRoleInfo.class));
    }

    @Test
    void saveRole_WithDuplicateCode_ShouldThrowException() {
        // ========== 准备测试数据 (Given) ==========
        PrivilegeRoleInfo inputRole = new PrivilegeRoleInfo();
        inputRole.setName("测试角色");
        inputRole.setCode("EXIST001"); // 已存在的编码
        
        // 模拟数据库查询返回已存在的角色
        PrivilegeRoleInfo existingRole = new PrivilegeRoleInfo();
        existingRole.setCode("EXIST001");
        when(roleInfoDao.findByCode("EXIST001")).thenReturn(existingRole);
        
        // ========== 执行并验证异常 (When & Then) ==========
        assertThrows(RoleAlreadyExistsException.class, () -> {
            roleInfoService.saveRole(inputRole);
        });
    }
}
```

#### 📝 步骤二：运行测试

**使用Maven运行：**
```bash
# 运行单个测试类
mvn test -Dtest=RoleInfoServiceTest

# 运行单个测试方法
mvn test -Dtest=RoleInfoServiceTest#saveRole_WithValidData_ShouldReturnSavedRole

# 运行所有测试
mvn test

# 生成覆盖率报告
mvn test jacoco:report
```

**使用IDE运行（IDEA）：**
1. 右键点击测试类
2. 选择 "Run 'RoleInfoServiceTest'"
3. 查看测试结果

#### 📝 步骤三：解读测试结果

```
✅ 测试通过显示（绿色）：
RoleInfoServiceTest
  ✅ saveRole_WithValidData_ShouldReturnSavedRole (45ms)
  ✅ saveRole_WithDuplicateCode_ShouldThrowException (12ms)

Tests run: 2, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

```
❌ 测试失败显示（红色）：
RoleInfoServiceTest
  ❌ saveRole_WithValidData_ShouldReturnSavedRole (45ms)
    Expected: "测试角色"
    Actual: null
    
AssertionFailedError: expected: "测试角色" but was: null

Tests run: 1, Failures: 1, Errors: 0, Skipped: 0
BUILD FAILURE
```

---

### 5.2 如何使用Apifox做接口测试

#### 📖 前置知识（小白解释）

```
🔍 API测试 = "用工具给接口出题"

就像：
- 用Postman点按钮测试登录接口
- 看看返回的用户信息对不对
- 不用打开浏览器也能测试后端接口

Apifox就是升级版的Postman，功能更强大！
```

#### 📝 步骤一：创建项目

1. 访问 Apifox 官网注册账号
2. 创建新项目：`PICC接口管理`
3. 设置环境变量：
   ```
   baseUrl: https://api.test.picc.com
   token: (登录后获取)
   ```

#### 📝 步骤二：创建接口

**1. 新建接口：查询申报列表**

```
接口信息：
- 名称：查询申报列表
- 请求方式：GET
- URL：{{baseUrl}}/api/declare/list
- Headers：
  - Authorization: Bearer {{token}}
  - Content-Type: application/json
- Query参数：
  - pageNum: 1
  - pageSize: 10
  - status: 待审核
```

**2. 新建接口：创建申报**

```
接口信息：
- 名称：创建申报
- 请求方式：POST
- URL：{{baseUrl}}/api/declare
- Headers：
  - Authorization: Bearer {{token}}
  - Content-Type: application/json
- Body（JSON）：
{
    "name": "张三",
    "idCard": "110101199001011234",
    "diseaseType": "hypertension",
    "hospitalName": "北京协和医院",
    "amount": 5000.00
}
```

#### 📝 步骤三：编写测试脚本

**添加前置脚本（自动登录获取Token）：**
```javascript
// 环境：开发环境
// 前置操作：自动登录获取Token

pm.test("登录获取Token", function() {
    const response = pm.sendRequest({
        url: pm.environment.get("baseUrl") + "/api/login",
        method: "POST",
        header: {
            "Content-Type": "application/json"
        },
        body: {
            mode: "raw",
            raw: JSON.stringify({
                username: "testuser",
                password: "password123"
            })
        }
    }, function(err, res) {
        if (err) {
            console.log(err);
        }
        const jsonData = res.json();
        if (jsonData.code === 200) {
            pm.environment.set("token", jsonData.data.token);
        }
    });
});
```

**添加断言脚本：**
```javascript
// 后置操作：验证响应

// 验证状态码
pm.test("状态码为200", function() {
    pm.response.to.have.status(200);
});

// 验证返回结构
pm.test("返回数据存在", function() {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('code');
    pm.expect(jsonData).to.have.property('data');
});

// 验证申报列表不为空
pm.test("申报列表有数据", function() {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.list).to.have.length.above(0);
});

// 验证申报状态
pm.test("申报状态正确", function() {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.list[0].status).to.be.oneOf(['待审核', '审核中', '已完成']);
});
```

#### 📝 步骤四：运行接口测试

**1. 单接口测试**
- 点击接口右侧的"发送"按钮
- 查看响应结果
- 检查断言是否通过

**2. 批量运行**
- 创建测试套件
- 选择要运行的接口
- 点击"运行"按钮
- 查看测试报告

**3. 测试报告示例**
```
📊 测试报告 - 2024-01-15 14:30

总计：15个接口
通过：14个 ✅
失败：1个 ❌
跳过：0个 ⏭️

❌ 失败接口：
- 创建申报 - 响应超时（超过30秒）

执行时间：2分35秒
```

---

### 5.3 如何使用Jest为Vue组件写测试

#### 📖 前置知识（小白解释）

```
🧪 Vue组件测试 = "给Vue组件出考题"

就像：
- 给一个计算器组件出题
- 看它显示的数字对不对
- 看用户输入后它会不会响应

Jest就是专门给Vue/React组件出题的工具！
```

#### 📝 步骤一：安装测试依赖

```bash
cd picc-mzmtb-agent

# 安装Jest和Vue测试工具
npm install --save-dev jest @vue/test-utils @babel/core @babel/preset-env babel-jest jest-transform-stub vue-jest
```

#### 📝 步骤二：配置Jest

**创建 jest.config.js：**
```javascript
// 项目根目录
module.exports = {
  // 使用Vue CLI的Jest预设
  preset: '@vue/cli-plugin-unit-jest',
  
  // 测试文件匹配规则
  testMatch: [
    '**/src/**/*.spec.js',
    '**/src/**/*.test.js'
  ],
  
  // 模块名称映射（解决@别名问题）
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$': '<rootDir>/src/utils/fileMock.js'
  },
  
  // 代码覆盖率配置
  collectCoverage: true,
  collectCoverageFrom: [
    'src/**/*.{js,vue}',
    '!src/main.js',
    '!src/router/**/*.js'
  ],
  
  // 覆盖率报告输出目录
  coverageDirectory: 'tests/coverage',
  
  // 报告格式
  coverageReporters: ['html', 'text-summary']
}
```

#### 📝 步骤三：创建测试文件

**场景：测试申报表单组件 DeclareForm.vue**

**DeclareForm.vue 源码（简化版）：**
```vue
<template>
  <div class="declare-form">
    <a-form :form="form" @submit="handleSubmit">
      <a-form-item label="姓名">
        <a-input 
          v-model="form.name" 
          placeholder="请输入姓名"
          name="name"
        />
        <span v-if="errors.name" class="error">{{ errors.name }}</span>
      </a-form-item>
      
      <a-form-item label="身份证号">
        <a-input 
          v-model="form.idCard" 
          placeholder="请输入身份证号"
          name="idCard"
        />
        <span v-if="errors.idCard" class="error">{{ errors.idCard }}</span>
      </a-form-item>
      
      <a-form-item>
        <a-button type="primary" html-type="submit">提交</a-button>
      </a-form-item>
    </a-form>
  </div>
</template>

<script>
export default {
  name: 'DeclareForm',
  data() {
    return {
      form: {
        name: '',
        idCard: ''
      },
      errors: {
        name: '',
        idCard: ''
      }
    }
  },
  methods: {
    validateForm() {
      let isValid = true
      this.errors = { name: '', idCard: '' }
      
      // 验证姓名
      if (!this.form.name) {
        this.errors.name = '姓名为必填项'
        isValid = false
      }
      
      // 验证身份证号格式
      const idCardRegex = /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/
      if (!this.form.idCard) {
        this.errors.idCard = '身份证号为必填项'
        isValid = false
      } else if (!idCardRegex.test(this.form.idCard)) {
        this.errors.idCard = '身份证号格式不正确'
        isValid = false
      }
      
      return isValid
    },
    
    handleSubmit() {
      if (this.validateForm()) {
        this.$emit('submit', this.form)
      }
    }
  }
}
</script>

<style scoped>
.error {
  color: red;
  font-size: 12px;
}
</style>
```

**DeclareForm.spec.js 测试文件：**
```javascript
import { mount } from '@vue/test-utils'
import DeclareForm from '@/components/DeclareForm.vue'

describe('DeclareForm.vue', () => {
  
  // ========== 测试：姓名为必填项 ==========
  it('姓名为空时应显示错误提示', () => {
    const wrapper = mount(DeclareForm)
    
    // 不填写姓名，直接提交
    wrapper.find('button[type="submit"]').trigger('submit')
    
    // 等待DOM更新
    wrapper.vm.$nextTick(() => {
      expect(wrapper.find('.error').text()).toBe('姓名为必填项')
    })
  })
  
  // ========== 测试：身份证号格式验证 ==========
  it('身份证号格式错误时应显示错误提示', () => {
    const wrapper = mount(DeclareForm)
    
    // 填写错误格式的身份证号
    wrapper.find('input[name="idCard"]').setValue('123')
    
    // 提交
    wrapper.find('button[type="submit"]').trigger('submit')
    
    // 验证错误提示
    expect(wrapper.text()).toContain('身份证号格式不正确')
  })
  
  // ========== 测试：正确数据应能提交 ==========
  it('填写正确数据时应触发submit事件', () => {
    const wrapper = mount(DeclareForm)
    
    // 填写正确数据
    wrapper.find('input[name="name"]').setValue('张三')
    wrapper.find('input[name="idCard"]').setValue('110101199001011234')
    
    // 提交
    wrapper.find('button[type="submit"]').trigger('submit')
    
    // 验证submit事件被触发
    expect(wrapper.emitted('submit')).toBeTruthy()
    
    // 验证提交的数据
    const submitEvent = wrapper.emitted('submit')[0][0]
    expect(submitEvent.name).toBe('张三')
    expect(submitEvent.idCard).toBe('110101199001011234')
  })
  
  // ========== 测试：模拟API调用 ==========
  it('提交时应调用API接口', async () => {
    // 模拟API
    const mockSubmit = jest.fn().mockResolvedValue({ success: true })
    
    const wrapper = mount(DeclareForm, {
      mocks: {
        $api: {
          declare: {
            submit: mockSubmit
          }
        }
      }
    })
    
    // 填写表单
    wrapper.find('input[name="name"]').setValue('李四')
    wrapper.find('input[name="idCard"]').setValue('110101199001011234')
    
    // 提交
    wrapper.find('button[type="submit"]').trigger('submit')
    
    // 等待异步操作
    await wrapper.vm.$nextTick()
    
    // 验证API被调用
    expect(mockSubmit).toHaveBeenCalled()
  })
})
```

#### 📝 步骤四：运行测试

**运行单个测试文件：**
```bash
npx jest tests/unit/DeclareForm.spec.js
```

**运行所有测试：**
```bash
npx jest
```

**生成覆盖率报告：**
```bash
npx jest --coverage
```

**查看HTML覆盖率报告：**
```bash
# 报告会生成在 tests/coverage 目录
open tests/coverage/lcov-report/index.html
```

#### 📝 步骤五：测试结果解读

```
 PASS  src/components/DeclareForm.spec.js

 ✓ 姓名为空时应显示错误提示 (23ms)
 ✓ 身份证号格式错误时应显示错误提示 (15ms)
 ✓ 填写正确数据时应触发submit事件 (18ms)
 ✓ 提交时应调用API接口 (45ms)

Test Suites: 1 passed, 1 total
Tests:       4 passed, 4 total
Time:        1.245s

Coverage Report:
┌────────────────────────────────────────────┐
│ File           │ Stmts │ Branches │ Funcs │
├────────────────────────────────────────────┤
│ DeclareForm.vue │ 85%   │ 75%      │ 100%  │
└────────────────────────────────────────────┘
```

---

## 📊 附录：快速参考卡片

### 测试术语速查表

| 术语 | 小白解释 | 适用场景 |
|------|----------|----------|
| 单元测试 | 每个零件单独检查 | Service、工具类 |
| 集成测试 | 把零件组装起来检查 | API、数据库 |
| E2E测试 | 模拟用户走一遍 | 完整业务流程 |
| Mock | 用假零件测试 | 依赖外部服务时 |
| 覆盖率 | 检查了多少零件 | 评估测试质量 |
| 断言 | 验证结果对不对 | 所有测试 |
| CI | 每次提交自动检查 | 持续集成 |

### 测试工具选型建议

| 项目类型 | 推荐工具 | 难度 |
|----------|----------|------|
| Java后端 | JUnit 5 + Mockito | ⭐⭐ |
| Spring Boot | SpringBootTest | ⭐⭐ |
| Vue 2前端 | Jest + Vue Test Utils | ⭐⭐ |
| API测试 | Apifox | ⭐ |
| E2E测试 | Cypress | ⭐⭐ |
| 性能测试 | JMeter | ⭐⭐⭐ |

### 测试覆盖率目标（建议）

| 指标 | 短期目标 | 长期目标 |
|------|----------|----------|
| Service覆盖率 | 40% | 70% |
| Controller覆盖率 | 30% | 60% |
| 前端组件覆盖率 | 20% | 50% |
| 核心业务覆盖率 | 80% | 90% |

---

## 📝 总结

### 当前测试现状
- ❌ **严重缺乏测试覆盖**
- ⚠️ **仅1%的代码有测试保护**
- ⚠️ **业务风险极高**

### 改进优先级
1. 🔴 **紧急**：为支付、申报等核心业务编写测试
2. 🟠 **重要**：补充Service层单元测试
3. 🟡 **一般**：建立API自动化测试
4. 🟢 **建议**：引入E2E测试和性能测试

### 下一步行动
1. 组建测试专项小组
2. 制定测试覆盖率目标
3. 引入测试工具和框架
4. 分批次补充测试代码
5. 建立CI/CD测试流程

---

**文档版本**：v1.0  
**生成日期**：2024年1月  
**文档作者**：测试体系分析工具  
**适用范围**：PICC四个项目团队
