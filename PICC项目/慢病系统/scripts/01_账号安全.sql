-- =============================================
-- PICC人保健康门诊慢特病业务管理信息系统
-- 数据库初始化脚本 - 账号安全相关表结构
-- 适用地市：宝鸡、张家口、定州、延安、商洛、满洲里、榆林、杨凌、九江、晋城、咸阳
-- =============================================

-- 创建数据库（如果不存在）
-- CREATE DATABASE IF NOT EXISTS picc_chronic_disease DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE picc_chronic_disease;

-- =============================================
-- 1. 高危账号黑名单表
-- =============================================
DROP TABLE IF EXISTS sec_high_risk_account_blacklist;
CREATE TABLE sec_high_risk_account_blacklist (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    keyword         VARCHAR(50) NOT NULL COMMENT '高危关键词',
    keyword_type    TINYINT DEFAULT 1 COMMENT '关键词类型：1-完全匹配，2-模糊匹配',
    description     VARCHAR(200) COMMENT '描述说明',
    status          TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    created_by      VARCHAR(50) COMMENT '创建人',
    created_time    DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_by      VARCHAR(50) COMMENT '更新人',
    updated_time    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted      TINYINT DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    UNIQUE KEY uk_keyword (keyword)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='高危账号黑名单表';

-- 初始化高危关键词数据
INSERT INTO sec_high_risk_account_blacklist (keyword, keyword_type, description, status) VALUES
('admin', 2, '管理员默认账号', 1),
('system', 2, '系统默认账号', 1),
('root', 2, '根用户默认账号', 1),
('administrator', 2, '管理员账号变体', 1),
('supervisor', 2, '监督员账号', 1);

-- =============================================
-- 2. 账号安全审计日志表
-- =============================================
DROP TABLE IF EXISTS sec_account_audit_log;
CREATE TABLE sec_account_audit_log (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    log_type            TINYINT NOT NULL COMMENT '日志类型：1-创建账号，2-修改账号，3-删除账号，4-登录，5-登出，6-密码修改，7-高危账号拦截，8-权限变更',
    account_id          VARCHAR(50) COMMENT '账号ID',
    account_name        VARCHAR(100) COMMENT '账号名称',
    real_name           VARCHAR(100) COMMENT '真实姓名',
    city_code           VARCHAR(20) COMMENT '地市编码',
    city_name           VARCHAR(50) COMMENT '地市名称',
    role_type           VARCHAR(50) COMMENT '角色类型',
    ip_address          VARCHAR(50) COMMENT 'IP地址',
    device_info         VARCHAR(200) COMMENT '设备信息',
    browser_info        VARCHAR(200) COMMENT '浏览器信息',
    operation_content   TEXT COMMENT '操作内容',
    operation_result    TINYINT COMMENT '操作结果：0-失败，1-成功',
    failure_reason      VARCHAR(500) COMMENT '失败原因',
    related_account     VARCHAR(100) COMMENT '关联账号',
    module_name         VARCHAR(100) COMMENT '模块名称',
    menu_name           VARCHAR(100) COMMENT '菜单名称',
    request_params      TEXT COMMENT '请求参数',
    response_result     TEXT COMMENT '响应结果',
    created_by          VARCHAR(50) COMMENT '创建人',
    created_time        DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    is_deleted          TINYINT DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    INDEX idx_account_name (account_name),
    INDEX idx_log_type (log_type),
    INDEX idx_city_code (city_code),
    INDEX idx_created_time (created_time),
    INDEX idx_operation_result (operation_result)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='账号安全审计日志表';

-- =============================================
-- 3. 用户账号表扩展字段（与现有用户表配合使用）
-- =============================================
DROP TABLE IF EXISTS sec_account_extension;
CREATE TABLE sec_account_extension (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    account_id          VARCHAR(50) NOT NULL COMMENT '账号ID',
    account_name        VARCHAR(100) NOT NULL COMMENT '账号名称',
    real_name           VARCHAR(100) COMMENT '真实姓名',
    id_card_number      VARCHAR(100) COMMENT '身份证号(加密存储)',
    id_card_masked      VARCHAR(100) COMMENT '身份证号(脱敏显示)',
    phone_number        VARCHAR(100) COMMENT '手机号(加密存储)',
    phone_masked        VARCHAR(100) COMMENT '手机号(脱敏显示)',
    email               VARCHAR(100) COMMENT '邮箱(加密存储)',
    email_masked        VARCHAR(100) COMMENT '邮箱(脱敏显示)',
    bank_card_number    VARCHAR(100) COMMENT '银行卡号(加密存储)',
    bank_card_masked    VARCHAR(100) COMMENT '银行卡号(脱敏显示)',
    address             VARCHAR(500) COMMENT '地址(加密存储)',
    address_masked      VARCHAR(500) COMMENT '地址(脱敏显示)',
    account_source      VARCHAR(50) COMMENT '账号来源：jingban-经办端，yisheng-医生端，zhuanjia-专家端',
    city_code           VARCHAR(20) COMMENT '地市编码',
    city_name           VARCHAR(50) COMMENT '地市名称',
    password_hash       VARCHAR(200) COMMENT '密码哈希',
    password_salt       VARCHAR(50) COMMENT '密码盐值',
    password_changed_time DATETIME COMMENT '密码最后修改时间',
    password_expire_time DATETIME COMMENT '密码过期时间',
    is_high_risk        TINYINT DEFAULT 0 COMMENT '是否高危账号：0-否，1-是',
    risk_reason         VARCHAR(500) COMMENT '高危原因',
    status              TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    created_by          VARCHAR(50) COMMENT '创建人',
    created_time        DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_by          VARCHAR(50) COMMENT '更新人',
    updated_time        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted          TINYINT DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    UNIQUE KEY uk_account_id (account_id),
    INDEX idx_account_name (account_name),
    INDEX idx_city_code (city_code),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户账号扩展信息表';

-- =============================================
-- 4. 账号创建规则配置表
-- =============================================
DROP TABLE IF EXISTS sec_account_creation_rule;
CREATE TABLE sec_account_creation_rule (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    rule_code       VARCHAR(50) NOT NULL COMMENT '规则编码',
    rule_name       VARCHAR(100) NOT NULL COMMENT '规则名称',
    rule_type       TINYINT NOT NULL COMMENT '规则类型：1-用户名规则，2-密码规则，3-身份验证规则',
    rule_content    TEXT NOT NULL COMMENT '规则内容(JSON格式)',
    account_source  VARCHAR(50) COMMENT '适用端：jingban-经办端，yisheng-医生端，zhuanjia-专家端，all-全部',
    city_code       VARCHAR(20) COMMENT '适用地市编码，NULL表示全部适用',
    priority        INT DEFAULT 100 COMMENT '优先级，数字越小优先级越高',
    status          TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    description     VARCHAR(500) COMMENT '规则描述',
    created_by      VARCHAR(50) COMMENT '创建人',
    created_time    DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_by      VARCHAR(50) COMMENT '更新人',
    updated_time    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted      TINYINT DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    UNIQUE KEY uk_rule_code (rule_code),
    INDEX idx_rule_type (rule_type),
    INDEX idx_account_source (account_source)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='账号创建规则配置表';

-- 初始化默认规则
INSERT INTO sec_account_creation_rule (rule_code, rule_name, rule_type, rule_content, account_source, description) VALUES
('RULE_USERNAME_001', '用户名高危关键词校验', 1, '{"type":"blacklist","checkMode":"contains","keywords":["admin","system","root"]}', 'all', '用户名不能包含高危关键词admin、system、root'),
('RULE_USERNAME_002', '用户名长度规则', 1, '{"minLength":4,"maxLength":20}', 'all', '用户名长度4-20位'),
('RULE_PASSWORD_001', '密码强度规则', 2, '{"minLength":8,"maxLength":20,"requireUpperCase":true,"requireLowerCase":true,"requireDigit":true,"requireSpecial":true}', 'all', '密码长度8-20位，必须包含大小写字母、数字和特殊字符'),
('RULE_IDCARD_001', '身份证号格式校验', 3, '{"type":"chinaIdCard"}', 'jingban', '经办端需要验证身份证号格式');

-- =============================================
-- 5. 地市信息表
-- =============================================
DROP TABLE IF EXISTS sys_city_info;
CREATE TABLE sys_city_info (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    city_code       VARCHAR(20) NOT NULL COMMENT '地市编码',
    city_name       VARCHAR(50) NOT NULL COMMENT '地市名称',
    city_short_code VARCHAR(10) COMMENT '地市简码',
    province_code   VARCHAR(20) COMMENT '省份编码',
    province_name   VARCHAR(50) COMMENT '省份名称',
    city_type       TINYINT DEFAULT 1 COMMENT '城市类型：1-地级市，2-直辖市，3-自治州',
    sort_order      INT DEFAULT 100 COMMENT '排序',
    status          TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    created_by      VARCHAR(50) COMMENT '创建人',
    created_time    DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_by      VARCHAR(50) COMMENT '更新人',
    updated_time    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted      TINYINT DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    UNIQUE KEY uk_city_code (city_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='地市信息表';

-- 初始化地市数据
INSERT INTO sys_city_info (city_code, city_name, city_short_code, province_code, province_name) VALUES
('610300', '宝鸡', 'BJ', '610000', '陕西省'),
('130700', '张家口', 'ZJK', '130000', '河北省'),
('139000', '定州', 'DZ', '130000', '河北省'),
('610600', '延安', 'YA', '610000', '陕西省'),
('611000', '商洛', 'SL', '610000', '陕西省'),
('150700', '满洲里', 'MZL', '150000', '内蒙古自治区'),
('610800', '榆林', 'YL', '610000', '陕西省'),
('610400', '杨凌', 'YL', '610000', '陕西省'),
('360400', '九江', 'JJ', '360000', '江西省'),
('140500', '晋城', 'JC', '140000', '山西省'),
('610400', '咸阳', 'XY', '610000', '陕西省');
