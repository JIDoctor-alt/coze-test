-- =============================================
-- PICC人保健康门诊慢特病业务管理信息系统
-- 数据库初始化脚本 - 下载审批流程表
-- =============================================

-- =============================================
-- 1. 下载申请表
-- =============================================
DROP TABLE IF EXISTS sec_download_application;
CREATE TABLE sec_download_application (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    application_no      VARCHAR(50) NOT NULL COMMENT '申请单号',
    city_code           VARCHAR(20) NOT NULL COMMENT '地市编码',
    city_name           VARCHAR(50) NOT NULL COMMENT '地市名称',
    menu_code           VARCHAR(50) NOT NULL COMMENT '菜单编码',
    menu_name           VARCHAR(100) NOT NULL COMMENT '菜单名称',
    download_type       VARCHAR(50) NOT NULL COMMENT '下载类型：export_excel-导出Excel, download_file-下载文件, batch_download-批量下载',
    download_purpose     VARCHAR(500) NOT NULL COMMENT '下载用途',
    download_conditions TEXT COMMENT '下载范围条件（查询条件和下载字段）',
    query_params        TEXT COMMENT '查询参数JSON',
    applicant_id        VARCHAR(50) NOT NULL COMMENT '申请人ID',
    applicant_name      VARCHAR(100) NOT NULL COMMENT '申请人姓名',
    applicant_account   VARCHAR(100) NOT NULL COMMENT '申请人账号',
    applicant_dept      VARCHAR(100) COMMENT '申请人部门',
    file_name           VARCHAR(200) COMMENT '生成的文件名',
    file_path           VARCHAR(500) COMMENT '文件存储路径',
    file_size           BIGINT COMMENT '文件大小（字节）',
    record_count        INT COMMENT '导出记录数',
    approval_status     TINYINT DEFAULT 0 COMMENT '审批状态：0-未审核，1-审核通过，2-审核不通过',
    approver_id         VARCHAR(50) COMMENT '审批人ID',
    approver_name       VARCHAR(100) COMMENT '审批人姓名',
    approver_account    VARCHAR(100) COMMENT '审批人账号',
    approval_comment    VARCHAR(500) COMMENT '审批意见',
    approval_time       DATETIME COMMENT '审批时间',
    download_count      INT DEFAULT 0 COMMENT '下载次数',
    last_download_time  DATETIME COMMENT '最后下载时间',
    expire_time         DATETIME COMMENT '审批有效期截止时间',
    status              TINYINT DEFAULT 1 COMMENT '状态：0-已取消，1-待审批，2-已通过，3-已拒绝，4-已过期',
    created_by          VARCHAR(50) COMMENT '创建人',
    created_time        DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_by          VARCHAR(50) COMMENT '更新人',
    updated_time        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted          TINYINT DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    UNIQUE KEY uk_application_no (application_no),
    INDEX idx_city_code (city_code),
    INDEX idx_menu_code (menu_code),
    INDEX idx_applicant_id (applicant_id),
    INDEX idx_approval_status (approval_status),
    INDEX idx_created_time (created_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='下载申请表';

-- =============================================
-- 2. 审批记录表
-- =============================================
DROP TABLE IF EXISTS sec_approval_record;
CREATE TABLE sec_approval_record (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    application_no      VARCHAR(50) NOT NULL COMMENT '关联申请单号',
    approval_level      INT DEFAULT 1 COMMENT '审批级别',
    approver_id         VARCHAR(50) NOT NULL COMMENT '审批人ID',
    approver_name       VARCHAR(100) NOT NULL COMMENT '审批人姓名',
    approver_account    VARCHAR(100) NOT NULL COMMENT '审批人账号',
    approval_role       VARCHAR(100) COMMENT '审批人角色',
    approval_result     TINYINT NOT NULL COMMENT '审批结果：1-通过，2-不通过',
    approval_comment    VARCHAR(500) COMMENT '审批意见',
    approval_time       DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '审批时间',
    ip_address          VARCHAR(50) COMMENT '审批人IP地址',
    device_info         VARCHAR(200) COMMENT '审批人设备信息',
    created_by          VARCHAR(50) COMMENT '创建人',
    created_time        DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_application_no (application_no),
    INDEX idx_approver_id (approver_id),
    INDEX idx_approval_result (approval_result),
    INDEX idx_approval_time (approval_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审批记录表';

-- =============================================
-- 3. 审批流程配置表
-- =============================================
DROP TABLE IF EXISTS sec_approval_flow_config;
CREATE TABLE sec_approval_flow_config (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    flow_code           VARCHAR(50) NOT NULL COMMENT '流程编码',
    flow_name           VARCHAR(100) NOT NULL COMMENT '流程名称',
    flow_type           VARCHAR(50) NOT NULL COMMENT '流程类型：download-下载审批, export-导出审批',
    city_code           VARCHAR(20) COMMENT '适用地市编码，NULL表示全部适用',
    menu_codes          VARCHAR(500) COMMENT '适用的菜单编码列表，逗号分隔，NULL表示全部',
    approval_levels     INT DEFAULT 1 COMMENT '审批级别数量',
    auto_approve        TINYINT DEFAULT 0 COMMENT '是否自动审批：0-否，1-是',
    approval_timeout    INT COMMENT '审批超时时间（小时）',
    expire_hours        INT DEFAULT 72 COMMENT '下载有效期（小时）',
    max_daily_apply     INT DEFAULT 10 COMMENT '每日最大申请次数',
    max_single_records  INT DEFAULT 10000 COMMENT '单次最大导出记录数',
    status              TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    description         VARCHAR(500) COMMENT '流程描述',
    created_by          VARCHAR(50) COMMENT '创建人',
    created_time        DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_by          VARCHAR(50) COMMENT '更新人',
    updated_time        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted          TINYINT DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    UNIQUE KEY uk_flow_code (flow_code),
    INDEX idx_flow_type (flow_type),
    INDEX idx_city_code (city_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审批流程配置表';

-- 初始化审批流程配置
INSERT INTO sec_approval_flow_config (flow_code, flow_name, flow_type, city_code, approval_levels, description) VALUES
('FLOW_DOWNLOAD_BJ', '宝鸡下载审批流程', 'download', '610300', 1, '宝鸡地市下载审批流程'),
('FLOW_DOWNLOAD_ZJK', '张家口下载审批流程', 'download', '130700', 1, '张家口地市下载审批流程'),
('FLOW_DOWNLOAD_DZ', '定州下载审批流程', 'download', '139000', 1, '定州地市下载审批流程'),
('FLOW_DOWNLOAD_YA', '延安下载审批流程', 'download', '610600', 1, '延安地市下载审批流程'),
('FLOW_DOWNLOAD_SL', '商洛下载审批流程', 'download', '611000', 1, '商洛地市下载审批流程'),
('FLOW_DOWNLOAD_MZL', '满洲里下载审批流程', 'download', '150700', 1, '满洲里地市下载审批流程'),
('FLOW_DOWNLOAD_YL', '榆林下载审批流程', 'download', '610800', 1, '榆林地市下载审批流程'),
('FLOW_DOWNLOAD_YLing', '杨凌下载审批流程', 'download', '610400', 1, '杨凌地市下载审批流程'),
('FLOW_DOWNLOAD_JJ', '九江下载审批流程', 'download', '360400', 1, '九江地市下载审批流程'),
('FLOW_DOWNLOAD_JC', '晋城下载审批流程', 'download', '140500', 1, '晋城地市下载审批流程'),
('FLOW_DOWNLOAD_XY', '咸阳下载审批流程', 'download', '610400', 1, '咸阳地市下载审批流程');

-- =============================================
-- 4. 审批权限配置表
-- =============================================
DROP TABLE IF EXISTS sec_approval_permission;
CREATE TABLE sec_approval_permission (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    permission_code     VARCHAR(50) NOT NULL COMMENT '权限编码',
    permission_name     VARCHAR(100) NOT NULL COMMENT '权限名称：审批(XX下载)',
    permission_type     VARCHAR(50) DEFAULT 'approval' COMMENT '权限类型：approval-审批权限',
    city_code           VARCHAR(20) NOT NULL COMMENT '关联地市编码',
    city_name           VARCHAR(50) NOT NULL COMMENT '关联地市名称',
    role_code           VARCHAR(50) COMMENT '关联角色编码',
    role_name           VARCHAR(100) COMMENT '关联角色名称',
    user_ids            VARCHAR(500) COMMENT '授权用户ID列表，逗号分隔',
    menu_codes          VARCHAR(500) COMMENT '授权菜单编码列表，逗号分隔',
    approval_limit      INT COMMENT '审批额度限制',
    status              TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    valid_start_time    DATETIME COMMENT '权限生效开始时间',
    valid_end_time      DATETIME COMMENT '权限生效结束时间',
    created_by          VARCHAR(50) COMMENT '创建人',
    created_time        DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_by          VARCHAR(50) COMMENT '更新人',
    updated_time        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted          TINYINT DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    UNIQUE KEY uk_permission_code (permission_code),
    INDEX idx_city_code (city_code),
    INDEX idx_role_code (role_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审批权限配置表';

-- 初始化审批权限配置
INSERT INTO sec_approval_permission (permission_code, permission_name, permission_type, city_code, city_name, role_code, role_name) VALUES
('PERM_APPROVAL_BJ', '审批(宝鸡下载)', 'approval', '610300', '宝鸡', NULL, NULL),
('PERM_APPROVAL_ZJK', '审批(张家口下载)', 'approval', '130700', '张家口', NULL, NULL),
('PERM_APPROVAL_DZ', '审批(定州下载)', 'approval', '139000', '定州', NULL, NULL),
('PERM_APPROVAL_YA', '审批(延安下载)', 'approval', '610600', '延安', NULL, NULL),
('PERM_APPROVAL_SL', '审批(商洛下载)', 'approval', '611000', '商洛', NULL, NULL),
('PERM_APPROVAL_MZL', '审批(满洲里下载)', 'approval', '150700', '满洲里', NULL, NULL),
('PERM_APPROVAL_YL', '审批(榆林下载)', 'approval', '610800', '榆林', NULL, NULL),
('PERM_APPROVAL_YLing', '审批(杨凌下载)', 'approval', '610400', '杨凌', NULL, NULL),
('PERM_APPROVAL_JJ', '审批(九江下载)', 'approval', '360400', '九江', NULL, NULL),
('PERM_APPROVAL_JC', '审批(晋城下载)', 'approval', '140500', '晋城', NULL, NULL),
('PERM_APPROVAL_XY', '审批(咸阳下载)', 'approval', '610400', '咸阳', NULL, NULL);

-- =============================================
-- 5. 下载审批菜单权限表
-- =============================================
DROP TABLE IF EXISTS sec_download_menu_permission;
CREATE TABLE sec_download_menu_permission (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    menu_code           VARCHAR(50) NOT NULL COMMENT '菜单编码',
    menu_name           VARCHAR(100) NOT NULL COMMENT '菜单名称',
    city_code           VARCHAR(20) NOT NULL COMMENT '地市编码',
    city_name           VARCHAR(50) NOT NULL COMMENT '地市名称',
    button_code         VARCHAR(50) COMMENT '按钮编码',
    button_name         VARCHAR(100) COMMENT '按钮名称',
    button_type         VARCHAR(50) COMMENT '按钮类型：export-导出，download-下载',
    is_approval_required TINYINT DEFAULT 1 COMMENT '是否需要审批：0-否，1-是',
    file_template       VARCHAR(200) COMMENT '文件模板',
    max_records         INT DEFAULT 10000 COMMENT '最大导出记录数',
    status              TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    created_by          VARCHAR(50) COMMENT '创建人',
    created_time        DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_by          VARCHAR(50) COMMENT '更新人',
    updated_time        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted          TINYINT DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    UNIQUE KEY uk_menu_button (menu_code, city_code, button_code),
    INDEX idx_city_code (city_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='下载审批菜单权限表';

-- 初始化下载审批菜单权限（宝鸡地市示例）
INSERT INTO sec_download_menu_permission (menu_code, menu_name, city_code, city_name, button_code, button_name, button_type) VALUES
-- 宝鸡
('MENU_BJ_006', '慢病申报查询', '610300', '宝鸡', 'BTN_EXPORT', '导出Excel', 'export'),
('MENU_BJ_009', '慢病人员导入', '610300', '宝鸡', 'BTN_ERROR_DOWNLOAD', '错误数据下载', 'download'),
('MENU_BJ_010', '慢病人员处方修改', '610300', '宝鸡', 'BTN_EXPORT', '导出Excel', 'export'),
('MENU_BJ_011', '慢病结算信息报表打印', '610300', '宝鸡', 'BTN_PRINT', '打印结算单', 'download'),
('MENU_BJ_012', '慢病卡状态导出', '610300', '宝鸡', 'BTN_EXPORT', '导出Excel', 'export'),
('MENU_BJ_013', '对账导出报表总表', '610300', '宝鸡', 'BTN_EXPORT', '导出Excel', 'export'),
('MENU_BJ_014', '对账导出报表明细', '610300', '宝鸡', 'BTN_EXPORT', '导出Excel', 'export'),
-- 定州
('MENU_DZ_001', '综合查询', '139000', '定州', 'BTN_EXPORT', '导出Excel', 'export'),
-- 晋城
('MENU_JC_001', '申报综合查询', '140500', '晋城', 'BTN_EXPORT', '导出Excel', 'export'),
-- 九江
('MENU_JJ_001', '申报综合查询', '360400', '九江', 'BTN_BATCH_DOWNLOAD', '批量下载影像件', 'download'),
('MENU_JJ_001', '申报综合查询', '360400', '九江', 'BTN_BATCH_APPROVAL', '批量下载审批表', 'download'),
('MENU_JJ_001', '申报综合查询', '360400', '九江', 'BTN_EXPORT', '导出Excel', 'export'),
-- 延安
('MENU_YA_001', '慢病用户管理', '610600', '延安', 'BTN_EXPORT', '导出', 'export'),
('MENU_YA_002', '慢病申报查询', '610600', '延安', 'BTN_EXPORT', '导出Excel', 'export'),
('MENU_YA_003', '数据统计', '610600', '延安', 'BTN_EXPORT', '导出鉴定表', 'export'),
-- 商洛
('MENU_SL_001', '人员批量导入', '611000', '商洛', 'BTN_ERROR_DOWNLOAD', '错误数据下载', 'download'),
('MENU_SL_001', '人员批量导入', '611000', '商洛', 'BTN_EXPORT', '导出Excel', 'export'),
('MENU_SL_002', '申报综合查询', '611000', '商洛', 'BTN_EXPORT', '导出Excel', 'export'),
('MENU_SL_003', '处方管理', '611000', '商洛', 'BTN_HISTORY_EXPORT', '历史处方导出', 'export'),
-- 满洲里
('MENU_MZL_001', '人员批量导入', '150700', '满洲里', 'BTN_ERROR_DOWNLOAD', '错误数据下载', 'download'),
('MENU_MZL_001', '人员批量导入', '150700', '满洲里', 'BTN_EXPORT', '导出Excel', 'export'),
('MENU_MZL_002', '申报综合查询', '150700', '满洲里', 'BTN_CARD_DOWNLOAD', '慢病凭证下载', 'download'),
-- 杨凌
('MENU_YLing_001', '人员批量导入', '610400', '杨凌', 'BTN_ERROR_DOWNLOAD', '错误数据下载', 'download'),
('MENU_YLing_001', '人员批量导入', '610400', '杨凌', 'BTN_EXPORT', '导出Excel', 'export'),
('MENU_YLing_002', '申报综合查询', '610400', '杨凌', 'BTN_TREATMENT_DOWNLOAD', '治疗通知书下载', 'download'),
-- 榆林
('MENU_YL_001', '人员批量导入', '610800', '榆林', 'BTN_ERROR_DOWNLOAD', '错误数据下载审批', 'download'),
('MENU_YL_001', '人员批量导入', '610800', '榆林', 'BTN_EXPORT', '导出认定表', 'export'),
('MENU_YL_002', '申报综合查询', '610800', '榆林', 'BTN_EXPORT', '导出Excel', 'export'),
-- 张家口
('MENU_ZJK_001', '慢病申报修改', '130700', '张家口', 'BTN_EXPORT', '导出Excel', 'export'),
('MENU_ZJK_002', '慢病申报查询', '130700', '张家口', 'BTN_EXPORT', '导出Excel', 'export'),
-- 咸阳
('MENU_XY_001', '申报综合查询', '610400', '咸阳', 'BTN_EXPORT', '导出Excel', 'export'),
('MENU_XY_001', '申报综合查询', '610400', '咸阳', 'BTN_TREATMENT_DOWNLOAD', '待遇认定表下载', 'download');

-- =============================================
-- 6. 审批流程节点表
-- =============================================
DROP TABLE IF EXISTS sec_approval_flow_node;
CREATE TABLE sec_approval_flow_node (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    flow_code           VARCHAR(50) NOT NULL COMMENT '流程编码',
    node_order          INT NOT NULL COMMENT '节点顺序',
    node_name           VARCHAR(100) NOT NULL COMMENT '节点名称',
    node_type           VARCHAR(50) DEFAULT 'manual' COMMENT '节点类型：manual-人工审批，auto-自动审批',
    approver_type       VARCHAR(50) DEFAULT 'role' COMMENT '审批人类型：role-角色，user-指定用户',
    approver_roles      VARCHAR(500) COMMENT '审批人角色列表',
    approver_users      VARCHAR(500) COMMENT '指定审批人ID列表',
    approval_mode       VARCHAR(50) DEFAULT 'single' COMMENT '审批模式：single-单人审批，multi-多人会签',
    approval_ratio      INT DEFAULT 100 COMMENT '通过比例（%）',
    timeout_hours       INT COMMENT '节点超时时间（小时）',
    timeout_action      VARCHAR(50) COMMENT '超时动作：auto_pass-自动通过，auto_reject-自动拒绝，notify-提醒',
    status              TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    created_by          VARCHAR(50) COMMENT '创建人',
    created_time        DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_by          VARCHAR(50) COMMENT '更新人',
    updated_time        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted          TINYINT DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    INDEX idx_flow_code (flow_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审批流程节点表';

-- =============================================
-- 7. 系统操作日志表扩展（存储审批相关操作）
-- =============================================
DROP TABLE IF EXISTS sec_system_operation_log;
CREATE TABLE sec_system_operation_log (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    operation_type      VARCHAR(50) NOT NULL COMMENT '操作类型',
    operation_module    VARCHAR(100) COMMENT '操作模块',
    operation_desc      VARCHAR(500) COMMENT '操作描述',
    operator_id         VARCHAR(50) COMMENT '操作人ID',
    operator_name       VARCHAR(100) COMMENT '操作人姓名',
    operator_account    VARCHAR(100) COMMENT '操作人账号',
    operator_role       VARCHAR(100) COMMENT '操作人角色',
    city_code           VARCHAR(20) COMMENT '地市编码',
    menu_code           VARCHAR(50) COMMENT '菜单编码',
    request_method      VARCHAR(10) COMMENT '请求方法',
    request_url         VARCHAR(500) COMMENT '请求URL',
    request_params      TEXT COMMENT '请求参数',
    response_status     INT COMMENT '响应状态码',
    response_data       TEXT COMMENT '响应数据',
    ip_address          VARCHAR(50) COMMENT 'IP地址',
    user_agent          VARCHAR(500) COMMENT '用户代理',
    execution_time      INT COMMENT '执行时间（毫秒）',
    error_message       VARCHAR(1000) COMMENT '错误信息',
    status              TINYINT DEFAULT 1 COMMENT '状态：0-失败，1-成功',
    created_time        DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_operator_id (operator_id),
    INDEX idx_city_code (city_code),
    INDEX idx_menu_code (menu_code),
    INDEX idx_operation_type (operation_type),
    INDEX idx_created_time (created_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统操作日志表';
