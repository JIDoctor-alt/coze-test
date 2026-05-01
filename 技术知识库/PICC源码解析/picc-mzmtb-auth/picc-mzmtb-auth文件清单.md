# picc-mzmtb-auth 文件清单索引

> 📌 auth认证服务完整文件列表，便于快速定位

---

## picchealth-authentication-server (核心服务)

### 启动与配置
| 文件路径 | 一句话说明 |
|----------|-----------|
| `AuthenticationSpringBootApplication.java` | Spring Boot启动入口 |
| `config/MailHealthIndicator.java` | 邮件服务健康检查 |
| `config/MvcInterceptorConfig.java` | MVC拦截器配置 |

### API接口层 (module/api)
| 文件 | 一句话说明 |
|------|-----------|
| `LoginApi.java` | 登录登出核心接口（验证码、登录、修改密码） |

### 业务服务层 (module/service)
| 接口文件 | 实现文件 | 一句话说明 |
|----------|---------|-----------|
| `UserInfoService.java` | `UserInfoServiceImpl.java` | 用户登录核心业务 |
| `MenuInfoService.java` | `MenuInfoServiceImpl.java` | 菜单查询服务 |
| `OrgInfoService.java` | `OrgInfoServiceImpl.java` | 机构信息服务 |
| `OrgSystemService.java` | `OrgSystemServiceImpl.java` | 机构系统关联 |
| `PasswordService.java` | `PasswordServiceImpl.java` | 密码管理服务 |
| `PrivilegeMenuServiceService.java` | `PrivilegeMenuServiceServiceImpl.java` | 菜单服务关联 |
| `RoleResourceService.java` | `RoleResourceServiceImpl.java` | 角色资源关联 |
| `UserRoleInfoService.java` | `UserRoleInfoServiceImpl.java` | 用户角色关联 |
| `VipSecurityCodeService.java` | `VipSecurityCodeServiceImpl.java` | 短信验证码服务 |
| `PrivilegeHyperlinkInfoService.java` | `PrivilegeHyperlinkInfoServiceImpl.java` | 快捷链接服务 |

### 视图对象 (module/vo)
| 文件 | 一句话说明 |
|------|-----------|
| `LoginVo.java` | 登录请求参数（账号、密码、手机号等） |
| `LoginSuccVo.java` | 登录成功返回（Token、菜单等） |
| `CaptchaVo.java` | 验证码返回（图片Base64） |
| `CaptchaCheckForm.java` | 验证码校验表单 |
| `UserVo.java` | 用户信息视图 |
| `CommonVo.java` | 通用响应（code/msg） |
| `GetUserVo.java` | 获取用户请求 |
| `EmailUser.java` | 邮箱用户信息 |
| `JsonMobileActionVo.java` | 手机操作请求（验证码相关） |

### 数据传输对象 (module/dto)
| 文件 | 一句话说明 |
|------|-----------|
| `UserDto.java` | 用户数据传输对象 |
| `CaptchaDto.java` | 验证码数据传输对象 |

### 常量与枚举 (module/constant, module/enums)
| 文件 | 一句话说明 |
|------|-----------|
| `CaptchaConstant.java` | 验证码常量（坐标key、误差值） |
| `ConfigConstant.java` | 配置常量（拼图尺寸等） |
| `CaptchaEnum.java` | 验证码状态枚举 |

### 工具类 (utils)
| 文件/目录 | 一句话说明 |
|----------|-----------|
| `SM4Util.java` | 国密SM4加密解密 |
| `EncryptionUtil.java` | MD5/SHA加密工具 |
| `RedisKeyConf.java` | Redis Key规范定义 |
| `UserUtils.java` | 当前用户信息存取 |
| `SendVerificationCodeUtil.java` | 短信发送工具 |
| `MailSender.java` | 邮件发送工具 |
| `MathUtil.java` | 数学计算工具 |
| `HttpForwardUtil.java` | HTTP转发工具 |
| `UniqueIDGenerator.java` | 唯一ID生成 |
| `ReturnStatusEnum.java` | 返回状态枚举 |
| `captcha/TokenUtil.java` | Token生成工具 |
| `captcha/CaptchaUtil.java` | 拼图验证码生成 |
| `captcha/Base64Util.java` | Base64编解码 |
| `captcha/ImageUtil.java` | 图片处理工具 |
| `captcha/FileUtil.java` | 文件操作工具 |
| `captcha/Md5Util.java` | MD5工具 |
| `captcha/aes.java` | AES加密 |

### 配置切面 (config/aspect)
| 文件 | 一句话说明 |
|------|-----------|
| `LogAudit.java` | 日志审计注解 |

### Swagger配置
| 文件 | 一句话说明 |
|------|-----------|
| `OperationModelsProvider.java` | Swagger操作模型提供者 |
| `OperationParameterReader.java` | Swagger参数读取器 |

### 测试 (test)
| 文件 | 一句话说明 |
|------|-----------|
| `PrivilegeUserTest.java` | 用户权限测试用例 |

---

## picchealth-authentication-db (数据库层)

### 公共模块 (module/publics)

#### 数据访问层 (dao)
| 文件 | 一句话说明 |
|------|-----------|
| `SensitiveWordsDao.java` | 敏感词数据访问 |
| `UpOrgUserDao.java` | 机构用户数据访问 |
| `VipSecurityCodeDao.java` | 验证码数据访问 |

#### 实体类 (po)
| 文件 | 一句话说明 |
|------|-----------|
| `SensitiveWords.java` | 敏感词实体（word字段） |
| `UpOrgUser.java` | 机构用户实体 |
| `VipSecurityCode.java` | 验证码实体（mobile/code/过期时间） |

### 角色模块 (module/role)

#### 数据访问层 (dao)
| 文件 | 一句话说明 |
|------|-----------|
| `PrivilegeRoleInfoDao.java` | 角色信息数据访问 |
| `PrivilegeRoleResourceDao.java` | 角色资源数据访问 |

#### 实体类 (po)
| 文件 | 一句话说明 |
|------|-----------|
| `PrivilegeRoleInfo.java` | 角色信息（roleName等） |
| `PrivilegeRoleResource.java` | 角色资源关联 |

### 系统模块 (module/system)

#### 数据访问层 (dao)
| 文件 | 一句话说明 |
|------|-----------|
| `PasswordDao.java` | 密码数据访问 |
| `PrivilegeHyperlinkInfoDao.java` | 快捷链接数据访问 |
| `PrivilegeMenuInfoDao.java` | 菜单信息数据访问 |
| `PrivilegeMenuServiceDao.java` | 菜单服务关联数据访问 |
| `PrivilegeOrgInfoDao.java` | 机构信息数据访问 |
| `PrivilegeOrgSystemDao.java` | 机构系统关联数据访问 |
| `PrivilegeSystemInfoDao.java` | 系统信息数据访问 |
| `PrivilegeUserInfoDao.java` | 用户信息数据访问 |
| `PrivilegeUserRoleInfoDao.java` | 用户角色关联数据访问 |

#### 实体类 (po)
| 文件 | 一句话说明 |
|------|-----------|
| `Password.java` | 密码实体 |
| `PrivilegeHyperlinkInfo.java` | 快捷链接实体 |
| `PrivilegeMenuInfo.java` | 菜单信息实体 |
| `PrivilegeMenuService.java` | 菜单服务关联实体 |
| `PrivilegeOrgInfo.java` | 机构信息实体 |
| `PrivilegeOrgSystem.java` | 机构系统关联实体 |
| `PrivilegeSystemInfo.java` | 系统信息实体 |
| `PrivilegeUserInfo.java` | **核心用户实体**（账号/密码/姓名等） |
| `PrivilegeUserRoleInfo.java` | 用户角色关联实体 |

#### 数据传输对象 (dto)
| 文件 | 一句话说明 |
|------|-----------|
| `PrivilegeMenuInfoDto.java` | 菜单信息DTO |

---

## 核心文件详细索引

### 登录流程核心文件
```
LoginApi.java → UserInfoServiceImpl.java
                      ↓
            PrivilegeUserInfoDao → 查询用户
                      ↓
            验证码校验 → VipSecurityCodeServiceImpl
                      ↓
            Token生成 → SM4Util.encrypt()
                      ↓
            Redis存储 → RedisUtil.set()
                      ↓
            菜单查询 → MenuInfoServiceImpl
```

### 数据库表对应关系
| 表名 | 实体类 | 用途 |
|------|--------|------|
| `privilege_user_info` | PrivilegeUserInfo | 用户信息 |
| `privilege_menu_info` | PrivilegeMenuInfo | 菜单信息 |
| `privilege_role_info` | PrivilegeRoleInfo | 角色信息 |
| `privilege_user_role_info` | PrivilegeUserRoleInfo | 用户角色关联 |
| `privilege_role_resource` | PrivilegeRoleResource | 角色权限关联 |
| `privilege_org_info` | PrivilegeOrgInfo | 机构信息 |
| `vip_security_code` | VipSecurityCode | 短信验证码 |

---

## 快速查询

### 想改登录逻辑？
→ `module/api/LoginApi.java` + `module/service/impl/UserInfoServiceImpl.java`

### 想加验证码类型？
→ `module/enums/CaptchaEnum.java`

### 想改Token生成规则？
→ `utils/SM4Util.java` + `utils/captcha/TokenUtil.java`

### 想加新字段到用户表？
→ `picchealth-authentication-db/.../PrivilegeUserInfo.java`

### 想改Redis缓存策略？
→ `utils/RedisKeyConf.java` + `utils/redis/RedisUtil.java`（在common模块）

### 想改密码加密方式？
→ `utils/EncryptionUtil.java`
