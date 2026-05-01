/**
 * PICC慢特病系统安全功能 - TypeScript类型定义
 */

// =============================================
// 通用类型
// =============================================

export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data?: T;
  success: boolean;
}

export interface PageResult<T> {
  total: number;
  page: number;
  pageSize: number;
  list: T[];
}

export interface PageQuery {
  page?: number;
  pageSize?: number;
}

// =============================================
// 账号安全相关类型
// =============================================

/**
 * 验证结果
 */
export interface ValidationResult {
  isValid: boolean;
  errorMessage?: string;
  errorCode?: string;
  warnings?: string[];
}

/**
 * 审计日志查询参数
 */
export interface AuditLogQuery extends PageQuery {
  accountName?: string;
  logType?: number;
  cityCode?: string;
  startTime?: string;
  endTime?: string;
}

/**
 * 审计日志条目
 */
export interface AuditLogEntry {
  id: number;
  logType: number;
  accountId: string;
  accountName: string;
  realName: string;
  cityCode: string;
  cityName: string;
  operationContent: string;
  operationResult: number;
  ipAddress: string;
  createdTime: string;
}

/**
 * 账号信息
 */
export interface AccountInfo {
  accountId: string;
  accountName: string;
  realName: string;
  cityCode: string;
  cityName: string;
  accountSource: 'jingban' | 'yisheng' | 'zhuanjia';
  phone?: string;
  idCard?: string;
  email?: string;
  status: number;
}

/**
 * 账号创建请求
 */
export interface CreateAccountRequest {
  accountName: string;
  realName: string;
  password: string;
  cityCode: string;
  accountSource: 'jingban' | 'yisheng' | 'zhuanjia';
  phone?: string;
  idCard?: string;
}

// =============================================
// 敏感数据相关类型
// =============================================

/**
 * 字段脱敏配置
 */
export interface FieldMaskingConfig {
  fieldCode: string;
  fieldName: string;
  fieldType: 'name' | 'idcard' | 'phone' | 'bankcard' | 'address' | 'email';
  maskingRule: 'first-last' | 'front-back' | 'prefix-suffix';
  preserveChars: number;
  preserveCharsEnd?: number;
  maskChar: string;
  maskLength?: number;
  example?: {
    original: string;
    masked: string;
  };
}

/**
 * 脱敏请求
 */
export interface MaskRequest {
  data: Record<string, any> | Record<string, any>[];
  cityCode?: string;
  menuCode?: string;
}

/**
 * 脱敏响应
 */
export interface MaskResponse {
  maskedData: Record<string, any> | Record<string, any>[];
}

/**
 * 权限检查请求
 */
export interface PermissionCheckRequest {
  userId: string;
  roleCode: string;
  fieldCodes: string[];
  cityCode?: string;
}

/**
 * 权限检查响应
 */
export interface PermissionCheckResponse {
  [fieldCode: string]: boolean;
}

/**
 * 查看操作日志
 */
export interface ViewOperationLog {
  operatorId: string;
  operatorName: string;
  operatorAccount: string;
  fieldCodes: string[];
  recordCount: number;
  cityCode?: string;
  menuCode?: string;
  reason?: string;
}

// =============================================
// 下载审批相关类型
// =============================================

/**
 * 下载申请状态
 */
export enum ApprovalStatus {
  PENDING = 0,      // 未审核
  APPROVED = 1,     // 审核通过
  REJECTED = 2,     // 审核不通过
  CANCELLED = 3,    // 已取消
  EXPIRED = 4       // 已过期
}

/**
 * 下载类型
 */
export enum DownloadType {
  EXPORT_EXCEL = 'export_excel',
  DOWNLOAD_FILE = 'download_file',
  BATCH_DOWNLOAD = 'batch_download'
}

/**
 * 下载申请
 */
export interface DownloadApplication {
  cityCode: string;
  cityName: string;
  menuCode: string;
  menuName: string;
  downloadType: DownloadType;
  downloadPurpose: string;
  downloadConditions: string;
  queryParams?: string;
}

/**
 * 下载申请查询参数
 */
export interface DownloadApplicationQuery extends PageQuery {
  cityCode?: string;
  menuCode?: string;
  applicantAccount?: string;
  approverAccount?: string;
  approvalStatus?: ApprovalStatus;
  startDate?: string;
  endDate?: string;
}

/**
 * 下载申请记录
 */
export interface DownloadApplicationRecord {
  id: number;
  applicationNo: string;
  cityCode: string;
  cityName: string;
  menuCode: string;
  menuName: string;
  downloadType: DownloadType;
  downloadPurpose: string;
  downloadConditions: string;
  applicantId: string;
  applicantName: string;
  applicantAccount: string;
  createdTime: string;
  approvalStatus: ApprovalStatus;
  approverId?: string;
  approverName?: string;
  approverAccount?: string;
  approvalComment?: string;
  approvalTime?: string;
  expireTime?: string;
  downloadCount?: number;
  lastDownloadTime?: string;
  fileName?: string;
  filePath?: string;
}

/**
 * 审批请求
 */
export interface ApprovalRequest {
  applicationNo: string;
  approvalResult: 1 | 2;  // 1-通过, 2-不通过
  approvalComment?: string;
}

/**
 * 审批权限地市
 */
export interface ApprovalCityPermission {
  cityCode: string;
  cityName: string;
}

/**
 * 下载验证请求
 */
export interface DownloadValidateRequest {
  applicationNo: string;
}

/**
 * 下载验证响应
 */
export interface DownloadValidateResponse {
  canDownload: boolean;
  message: string;
  filePath?: string;
}

// =============================================
// 地市信息类型
// =============================================

/**
 * 地市信息
 */
export interface CityInfo {
  code: string;
  name: string;
  shortCode?: string;
  provinceCode?: string;
  provinceName?: string;
}

// =============================================
// 菜单配置类型
// =============================================

/**
 * 菜单信息
 */
export interface MenuInfo {
  code: string;
  name: string;
  cityCode: string;
  cityName: string;
  parentCode?: string;
  sortOrder?: number;
  icon?: string;
  path?: string;
  requireApproval?: boolean;
}

/**
 * 菜单字段映射
 */
export interface MenuFieldMapping {
  menuCode: string;
  cityCode: string;
  fieldCode: string;
  fieldDisplayName: string;
  columnIndex: number;
  isMasked: boolean;
}

// =============================================
// 用户类型
// =============================================

/**
 * 用户信息
 */
export interface UserInfo {
  userId: string;
  userName: string;
  realName: string;
  roleCode: string;
  roleName: string;
  cityCode?: string;
  cityName?: string;
  permissions?: string[];
}
