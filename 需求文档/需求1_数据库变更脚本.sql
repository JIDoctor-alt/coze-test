-- ============================================================
-- 榆林慢病管理 - 申报综合查询导出敏感信息权限控制
-- 数据库变更脚本
-- ============================================================

-- ============================================================
-- 第一步：PersonDivision 表新增字段（如不存在）
-- ============================================================

-- 检查字段是否存在
SELECT column_name FROM user_tab_columns 
WHERE table_name = 'PERSONDIVISION' AND column_name = 'ISEXPORT';

-- 如果不存在则新增字段
ALTER TABLE PersonDivision ADD isexport VARCHAR2(10);
COMMENT ON COLUMN PersonDivision.isexport IS '是否有导出权限 1：是';


-- ============================================================
-- 第二步：privilege_auth_info 表 - 新增权限归属
-- ============================================================

-- 查询是否已存在
SELECT * FROM privilege_auth_info WHERE id = '20260418150001';

-- 新增权限归属
-- id命名逻辑：日期YYYYMMDD + 地市xx + 编号xxxx
-- 榆林地市 = 15
INSERT INTO privilege_auth_info (
    id,
    name,
    code,
    flag,
    shared,
    dr,
    createtime,
    modifytime
) VALUES (
    '20260418150001',                                      -- id: 20260418 + 15 + 0001
    '榆林敏感信息导出权限',                                  -- name
    '20260418150001',                                      -- code: 非医保区划，与id保持一致
    '15',                                                  -- flag: 榆林
    '0',                                                   -- shared: 0-独享
    0,                                                     -- dr: 0-有效
    SYSDATE,
    SYSDATE
);


-- ============================================================
-- 第三步：privilege_auth_menu 表 - 新增父级菜单映射
-- ============================================================

-- 查询是否已存在
SELECT * FROM privilege_auth_menu WHERE auth_id = '20260418150001';

-- 新增菜单映射
-- id命名逻辑：日期yyyymmdd + 编号xxxxxx（6位）
-- parent_menu_id: 1813466762203889664 = 榆林慢病管理
INSERT INTO privilege_auth_menu (
    id,
    auth_id,
    parent_menu_id,
    flag,
    dr,
    createtime,
    modifytime
) VALUES (
    '20260418000001',                                      -- id: 20260418 + 000001
    '20260418150001',                                      -- auth_id: 权限归属id
    '1813466762203889664',                                 -- parent_menu_id: 榆林慢病管理
    '15',                                                  -- flag: 榆林
    0,
    SYSDATE,
    SYSDATE
);


-- ============================================================
-- 第四步：验证配置
-- ============================================================

-- 验证权限归属
SELECT * FROM privilege_auth_info WHERE id = '20260418150001';

-- 验证菜单映射
SELECT * FROM privilege_auth_menu WHERE auth_id = '20260418150001';

-- 验证字段
SELECT column_name, data_type FROM user_tab_columns 
WHERE table_name = 'PERSONDIVISION' AND column_name = 'ISEXPORT';


-- ============================================================
-- 第五步：为账号配置导出权限（可选，通过系统界面配置）
-- ============================================================

-- 方式一：通过系统界面配置（推荐）
-- 在权限管理中为指定账号配置"榆林敏感信息导出权限"

-- 方式二：直接操作数据库
-- UPDATE PersonDivision SET isexport = '1' 
-- WHERE account = '账号名' AND flag = '15' AND dr = 0;
