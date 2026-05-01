-- =============================================
-- PICC人保健康门诊慢特病业务管理信息系统
-- 数据库初始化脚本 - 敏感信息脱敏配置表
-- =============================================

-- =============================================
-- 1. 敏感字段脱敏配置表
-- =============================================
DROP TABLE IF EXISTS sec_sensitive_field_config;
CREATE TABLE sec_sensitive_field_config (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    field_code          VARCHAR(50) NOT NULL COMMENT '字段编码',
    field_name          VARCHAR(100) NOT NULL COMMENT '字段名称',
    field_type          VARCHAR(50) NOT NULL COMMENT '字段类型：name-姓名，idcard-身份证，phone-手机号，bankcard-银行卡号，address-地址',
    masking_rule        VARCHAR(50) NOT NULL COMMENT '脱敏规则：first-last-首尾保留，front-仅保留首部，back-仅保留尾部，full-完全隐藏，prefix-suffix-前后缀保留',
    preserve_chars      INT DEFAULT 1 COMMENT '保留字符数（头部）',
    preserve_chars_end INT DEFAULT 4 COMMENT '保留字符数（尾部）',
    mask_char           VARCHAR(10) DEFAULT '*' COMMENT '掩码字符',
    mask_length         INT DEFAULT 6 COMMENT '掩码长度',
    masking_template    VARCHAR(200) COMMENT '自定义脱敏模板',
    city_code           VARCHAR(20) COMMENT '适用地市编码，NULL表示全部适用',
    menu_code           VARCHAR(50) COMMENT '适用菜单编码，NULL表示全部适用',
    priority            INT DEFAULT 100 COMMENT '优先级，数字越小优先级越高',
    status              TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    description         VARCHAR(500) COMMENT '描述说明',
    created_by          VARCHAR(50) COMMENT '创建人',
    created_time        DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_by          VARCHAR(50) COMMENT '更新人',
    updated_time        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted          TINYINT DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    UNIQUE KEY uk_field_code (field_code),
    INDEX idx_field_type (field_type),
    INDEX idx_city_code (city_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='敏感字段脱敏配置表';

-- 初始化敏感字段脱敏规则
INSERT INTO sec_sensitive_field_config (field_code, field_name, field_type, masking_rule, preserve_chars, mask_length, masking_template) VALUES
('NAME', '姓名', 'name', 'first-last', 1, 2, '{first}**'),
('IDCARD', '身份证号', 'idcard', 'front-back', 6, 4, '{front}********{back}'),
('PHONE', '手机号码', 'phone', 'front-back', 3, 4, '{front}****{back}'),
('BANKCARD', '银行卡号', 'bankcard', 'front-back', 6, 4, '{front}****{back}'),
('EMAIL', '邮箱', 'email', 'front-back', 6, 0, '{front}******'),
('ADDRESS', '地址', 'address', 'prefix-suffix', 0, 6, '{province}{city}{mask}');

-- =============================================
-- 2. 菜单敏感字段映射表
-- =============================================
DROP TABLE IF EXISTS sec_menu_field_mapping;
CREATE TABLE sec_menu_field_mapping (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    menu_code           VARCHAR(50) NOT NULL COMMENT '菜单编码',
    menu_name           VARCHAR(100) NOT NULL COMMENT '菜单名称',
    city_code           VARCHAR(20) NOT NULL COMMENT '地市编码',
    city_name           VARCHAR(50) COMMENT '地市名称',
    table_name          VARCHAR(100) COMMENT '数据表名',
    field_code          VARCHAR(50) NOT NULL COMMENT '字段编码（关联sec_sensitive_field_config）',
    field_display_name  VARCHAR(100) COMMENT '字段显示名称',
    column_index        INT COMMENT '列索引位置',
    is_visible          TINYINT DEFAULT 1 COMMENT '是否显示：0-隐藏，1-显示',
    is_masked           TINYINT DEFAULT 1 COMMENT '是否脱敏：0-不脱敏，1-脱敏',
    masking_level       TINYINT DEFAULT 1 COMMENT '脱敏级别：1-普通，2-严格',
    is_required         TINYINT DEFAULT 0 COMMENT '是否必填',
    status              TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    created_by          VARCHAR(50) COMMENT '创建人',
    created_time        DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_by          VARCHAR(50) COMMENT '更新人',
    updated_time        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted          TINYINT DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    UNIQUE KEY uk_menu_field (menu_code, city_code, field_code),
    INDEX idx_menu_code (menu_code),
    INDEX idx_city_code (city_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='菜单敏感字段映射表';

-- 初始化菜单字段映射数据（宝鸡地市示例）
INSERT INTO sec_menu_field_mapping (menu_code, menu_name, city_code, city_name, field_code, field_display_name, column_index) VALUES
-- 慢病初审管理
('MENU_BJ_001', '慢病初审管理', '610300', '宝鸡', 'NAME', '姓名', 1),
('MENU_BJ_001', '慢病初审管理', '610300', '宝鸡', 'IDCARD', '身份证号', 2),
('MENU_BJ_001', '慢病初审管理', '610300', '宝鸡', 'PHONE', '手机号', 3),
-- 慢病体检分配
('MENU_BJ_002', '慢病体检分配', '610300', '宝鸡', 'NAME', '姓名', 1),
('MENU_BJ_002', '慢病体检分配', '610300', '宝鸡', 'IDCARD', '身份证号', 2),
('MENU_BJ_002', '慢病体检分配', '610300', '宝鸡', 'PHONE', '手机号', 3),
-- 慢病专家分配
('MENU_BJ_003', '慢病专家分配', '610300', '宝鸡', 'NAME', '姓名', 1),
('MENU_BJ_003', '慢病专家分配', '610300', '宝鸡', 'IDCARD', '身份证号', 2),
('MENU_BJ_003', '慢病专家分配', '610300', '宝鸡', 'PHONE', '手机号', 3),
-- 慢病用户管理
('MENU_BJ_004', '慢病用户管理', '610300', '宝鸡', 'NAME', '姓名', 1),
('MENU_BJ_004', '慢病用户管理', '610300', '宝鸡', 'PHONE', '电话号码', 2),
-- 体检站点管理
('MENU_BJ_005', '体检站点管理', '610300', '宝鸡', 'NAME', '负责人', 1),
('MENU_BJ_005', '体检站点管理', '610300', '宝鸡', 'PHONE', '联系电话', 2),
('MENU_BJ_005', '体检站点管理', '610300', '宝鸡', 'ADDRESS', '地址', 3),
-- 慢病申报查询
('MENU_BJ_006', '慢病申报查询', '610300', '宝鸡', 'NAME', '姓名', 1),
('MENU_BJ_006', '慢病申报查询', '610300', '宝鸡', 'IDCARD', '证件号', 2),
('MENU_BJ_006', '慢病申报查询', '610300', '宝鸡', 'PHONE', '联系方式', 3),
-- 待发卡管理
('MENU_BJ_007', '待发卡管理', '610300', '宝鸡', 'NAME', '客户名字', 1),
('MENU_BJ_007', '待发卡管理', '610300', '宝鸡', 'IDCARD', '证件号', 2),
('MENU_BJ_007', '待发卡管理', '610300', '宝鸡', 'PHONE', '电话', 3),
-- 人卡绑定管理
('MENU_BJ_008', '人卡绑定管理', '610300', '宝鸡', 'NAME', '投保人', 1),
('MENU_BJ_008', '人卡绑定管理', '610300', '宝鸡', 'IDCARD', '证件号', 2),
('MENU_BJ_008', '人卡绑定管理', '610300', '宝鸡', 'PHONE', '联系方式', 3),
('MENU_BJ_008', '人卡绑定管理', '610300', '宝鸡', 'BANKCARD', '会员卡号', 4),
-- 服务状态修改
('MENU_BJ_009', '服务状态修改', '610300', '宝鸡', 'NAME', '会员姓名', 1),
('MENU_BJ_009', '服务状态修改', '610300', '宝鸡', 'BANKCARD', '会员卡号', 2),
('MENU_BJ_009', '服务状态修改', '610300', '宝鸡', 'IDCARD', '证件号', 3),
('MENU_BJ_009', '服务状态修改', '610300', '宝鸡', 'PHONE', '联系方式', 4),
-- 会员账户信息查询
('MENU_BJ_010', '会员账户信息查询', '610300', '宝鸡', 'NAME', '会员姓名', 1),
('MENU_BJ_010', '会员账户信息查询', '610300', '宝鸡', 'BANKCARD', '会员卡号', 2),
('MENU_BJ_010', '会员账户信息查询', '610300', '宝鸡', 'IDCARD', '证件号', 3),
('MENU_BJ_010', '会员账户信息查询', '610300', '宝鸡', 'PHONE', '联系方式', 4);

-- =============================================
-- 3. 敏感信息查看权限配置表
-- =============================================
DROP TABLE IF EXISTS sec_sensitive_view_permission;
CREATE TABLE sec_sensitive_view_permission (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    role_code           VARCHAR(50) NOT NULL COMMENT '角色编码',
    role_name           VARCHAR(100) NOT NULL COMMENT '角色名称',
    permission_level    TINYINT NOT NULL COMMENT '权限级别：1-仅查看脱敏数据，2-可查看部分明文，3-可查看全部明文',
    allowed_fields      VARCHAR(500) COMMENT '可查看明文的字段列表，逗号分隔',
    city_code           VARCHAR(20) COMMENT '适用地市编码，NULL表示全部适用',
    menu_codes          VARCHAR(500) COMMENT '适用的菜单编码列表，逗号分隔，NULL表示全部',
    valid_start_time    DATETIME COMMENT '权限生效开始时间',
    valid_end_time      DATETIME COMMENT '权限生效结束时间',
    status              TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    created_by          VARCHAR(50) COMMENT '创建人',
    created_time        DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_by          VARCHAR(50) COMMENT '更新人',
    updated_time        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted          TINYINT DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    INDEX idx_role_code (role_code),
    INDEX idx_city_code (city_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='敏感信息查看权限配置表';

-- 初始化角色权限配置
INSERT INTO sec_sensitive_view_permission (role_code, role_name, permission_level, allowed_fields) VALUES
('ROLE_JINGBAN', '经办人', 2, 'NAME,IDCARD,PHONE'),
('ROLE_YISHENG', '医生', 1, ''),
('ROLE_ZHUANJIA', '专家', 2, 'NAME,IDCARD,PHONE'),
('ROLE_ADMIN', '系统管理员', 3, 'NAME,IDCARD,PHONE,BANKCARD,ADDRESS'),
('ROLE_AUDITOR', '审计员', 3, 'NAME,IDCARD,PHONE,BANKCARD,ADDRESS');

-- =============================================
-- 4. 敏感操作日志表
-- =============================================
DROP TABLE IF EXISTS sec_sensitive_operation_log;
CREATE TABLE sec_sensitive_operation_log (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    operation_type      TINYINT NOT NULL COMMENT '操作类型：1-查看明文，2-导出数据，3-批量操作',
    operator_id         VARCHAR(50) NOT NULL COMMENT '操作人ID',
    operator_name       VARCHAR(100) NOT NULL COMMENT '操作人姓名',
    operator_account    VARCHAR(100) NOT NULL COMMENT '操作人账号',
    city_code           VARCHAR(20) COMMENT '地市编码',
    city_name           VARCHAR(50) COMMENT '地市名称',
    menu_code           VARCHAR(50) COMMENT '菜单编码',
    menu_name           VARCHAR(100) COMMENT '菜单名称',
    data_type           VARCHAR(50) COMMENT '数据类型',
    field_list          VARCHAR(500) COMMENT '涉及的字段列表',
    record_count        INT COMMENT '操作的记录数量',
    operation_reason    VARCHAR(500) COMMENT '操作原因',
    ip_address          VARCHAR(50) COMMENT 'IP地址',
    device_info         VARCHAR(200) COMMENT '设备信息',
    request_params      TEXT COMMENT '请求参数',
    operation_result    TINYINT NOT NULL COMMENT '操作结果：0-失败，1-成功',
    failure_reason      VARCHAR(500) COMMENT '失败原因',
    created_time        DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_operator_id (operator_id),
    INDEX idx_operation_type (operation_type),
    INDEX idx_city_code (city_code),
    INDEX idx_menu_code (menu_code),
    INDEX idx_created_time (created_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='敏感操作日志表';

-- =============================================
-- 5. 脱敏加密密钥管理表
-- =============================================
DROP TABLE IF EXISTS sec_encryption_key;
CREATE TABLE sec_encryption_key (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    key_id              VARCHAR(50) NOT NULL COMMENT '密钥ID',
    key_type            VARCHAR(50) NOT NULL COMMENT '密钥类型：AES-对称加密，RSA-非对称加密',
    key_value           TEXT NOT NULL COMMENT '密钥值（加密存储）',
    key_version         INT DEFAULT 1 COMMENT '密钥版本',
    is_active           TINYINT DEFAULT 0 COMMENT '是否当前活跃密钥：0-否，1-是',
    algorithm           VARCHAR(50) DEFAULT 'AES-256-GCM' COMMENT '加密算法',
    key_expire_time     DATETIME COMMENT '密钥过期时间',
    status              TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    description         VARCHAR(500) COMMENT '密钥描述',
    created_by          VARCHAR(50) COMMENT '创建人',
    created_time        DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_by          VARCHAR(50) COMMENT '更新人',
    updated_time        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_key_id (key_id),
    INDEX idx_key_type (key_type),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='脱敏加密密钥管理表';
