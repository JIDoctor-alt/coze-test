/**
 * PICC慢特病系统安全功能 - 敏感数据处理工具函数
 */

import type {
  FieldMaskingConfig,
  DownloadApplication,
  ApprovalStatus
} from '../types';

/**
 * 敏感数据脱敏工具类
 */
export class SensitiveDataMasker {
  
  /**
   * 姓名脱敏
   * 规则：保留姓氏，其余用**代替
   * 示例：张三 -> 张**
   */
  static maskName(value: string): string {
    if (!value) return value;
    
    // 判断是否是中文姓名
    if (/^[\u4e00-\u9fa5]+$/.test(value)) {
      return value.length >= 2 ? value[0] + '**' : value + '**';
    }
    
    // 英文或其他姓名
    const parts = value.split(/\s+/);
    if (parts.length === 1) {
      return value.length >= 2 ? value[0] + '**' : value + '**';
    }
    
    return parts[0][0]?.toUpperCase() + '**' || value;
  }
  
  /**
   * 身份证号脱敏
   * 规则：前6位后4位保留，中间用8个*代替
   * 示例：610310199001011234 -> 610310********1234
   */
  static maskIdCard(value: string): string {
    if (!value) return value;
    
    const clean = value.trim().replace(/[Xx]$/, '');
    if (clean.length <= 10) return clean;
    
    return clean.slice(0, 6) + '********' + clean.slice(-4);
  }
  
  /**
   * 手机号脱敏
   * 规则：前3位后4位保留，中间用4个*代替
   * 示例：13812345678 -> 138****5678
   */
  static maskPhone(value: string): string {
    if (!value) return value;
    
    const clean = value.replace(/[\s\-]+/g, '');
    if (clean.length < 7) return clean;
    
    return clean.slice(0, 3) + '****' + clean.slice(-4);
  }
  
  /**
   * 银行卡号脱敏
   * 规则：前6位后4位保留，中间用*代替
   * 示例：6222021234567890123 -> 622202****90123
   */
  static maskBankCard(value: string): string {
    if (!value) return value;
    
    const clean = value.replace(/\s/g, '');
    if (clean.length <= 10) return clean;
    
    const maskLen = clean.length - 10;
    return clean.slice(0, 6) + '*'.repeat(maskLen) + clean.slice(-4);
  }
  
  /**
   * 地址脱敏
   * 规则：保留前10个字符，后面的详细地址脱敏
   * 示例：北京市丰台区西局欣园小区5号楼 -> 北京市丰台区******
   */
  static maskAddress(value: string): string {
    if (!value) return value;
    if (value.length <= 10) return value;
    
    const prefix = value.slice(0, 10);
    const suffixLength = Math.min(6, value.length - 10);
    const suffix = '*'.repeat(suffixLength);
    
    return prefix + suffix;
  }
  
  /**
   * 邮箱脱敏
   * 规则：前6位保留，后面用6个*代替
   * 示例：zhangsan@example.com -> zhangs******@example.com
   */
  static maskEmail(value: string): string {
    if (!value || !value.includes('@')) return value;
    
    const [user, domain] = value.split('@');
    const maskedUser = user.length > 6 
      ? user.slice(0, 6) + '******' 
      : user + '******';
    
    return maskedUser + '@' + domain;
  }
  
  /**
   * 根据字段类型执行脱敏
   */
  static maskByType(value: string, fieldType: string): string {
    switch (fieldType) {
      case 'name':
        return this.maskName(value);
      case 'idcard':
        return this.maskIdCard(value);
      case 'phone':
        return this.maskPhone(value);
      case 'bankcard':
        return this.maskBankCard(value);
      case 'address':
        return this.maskAddress(value);
      case 'email':
        return this.maskEmail(value);
      default:
        return value;
    }
  }
  
  /**
   * 批量脱敏对象中的敏感字段
   */
  static maskRecord(
    record: Record<string, any>,
    fieldMapping: Record<string, string>
  ): Record<string, any> {
    const masked = { ...record };
    
    for (const [originalField, fieldType] of Object.entries(fieldMapping)) {
      if (originalField in masked && masked[originalField]) {
        masked[originalField] = this.maskByType(
          String(masked[originalField]),
          fieldType
        );
      }
    }
    
    return masked;
  }
  
  /**
   * 批量脱敏数组中的记录
   */
  static maskList(
    list: Record<string, any>[],
    fieldMapping: Record<string, string>
  ): Record<string, any>[] {
    return list.map(record => this.maskRecord(record, fieldMapping));
  }
}

/**
 * 脱敏配置常量
 */
export const MASKING_CONFIGS: Record<string, FieldMaskingConfig> = {
  NAME: {
    fieldCode: 'NAME',
    fieldName: '姓名',
    fieldType: 'name',
    maskingRule: 'first-last',
    preserveChars: 1,
    example: { original: '张三', masked: '张**' }
  },
  IDCARD: {
    fieldCode: 'IDCARD',
    fieldName: '身份证号',
    fieldType: 'idcard',
    maskingRule: 'front-back',
    preserveChars: 6,
    preserveCharsEnd: 4,
    example: { original: '610310199001011234', masked: '610310********1234' }
  },
  PHONE: {
    fieldCode: 'PHONE',
    fieldName: '手机号码',
    fieldType: 'phone',
    maskingRule: 'front-back',
    preserveChars: 3,
    preserveCharsEnd: 4,
    example: { original: '13812345678', masked: '138****5678' }
  },
  BANKCARD: {
    fieldCode: 'BANKCARD',
    fieldName: '银行卡号',
    fieldType: 'bankcard',
    maskingRule: 'front-back',
    preserveChars: 6,
    preserveCharsEnd: 4,
    example: { original: '6222021234567890123', masked: '622202****90123' }
  },
  ADDRESS: {
    fieldCode: 'ADDRESS',
    fieldName: '地址',
    fieldType: 'address',
    maskingRule: 'prefix-suffix',
    preserveChars: 10,
    example: { original: '北京市丰台区西局欣园小区5号楼', masked: '北京市丰台区******' }
  },
  EMAIL: {
    fieldCode: 'EMAIL',
    fieldName: '邮箱',
    fieldType: 'email',
    maskingRule: 'front-back',
    preserveChars: 6,
    example: { original: 'zhangsan@example.com', masked: 'zhangs******@example.com' }
  }
};

/**
 * 默认字段映射
 */
export const DEFAULT_FIELD_MAPPING: Record<string, string> = {
  name: 'NAME',
  real_name: 'NAME',
  userName: 'NAME',
  idCard: 'IDCARD',
  idCardNumber: 'IDCARD',
  idcard: 'IDCARD',
  certNo: 'IDCARD',
  phone: 'PHONE',
  phoneNumber: 'PHONE',
  mobile: 'PHONE',
  telephone: 'PHONE',
  bankCard: 'BANKCARD',
  bankCardNumber: 'BANKCARD',
  cardNo: 'BANKCARD',
  address: 'ADDRESS',
  homeAddress: 'ADDRESS',
  email: 'EMAIL'
};

/**
 * 审批状态常量
 */
export const APPROVAL_STATUS = {
  PENDING: 0,
  APPROVED: 1,
  REJECTED: 2,
  CANCELLED: 3,
  EXPIRED: 4
};

export const APPROVAL_STATUS_TEXT: Record<number, string> = {
  [APPROVAL_STATUS.PENDING]: '未审核',
  [APPROVAL_STATUS.APPROVED]: '审核通过',
  [APPROVAL_STATUS.REJECTED]: '审核不通过',
  [APPROVAL_STATUS.CANCELLED]: '已取消',
  [APPROVAL_STATUS.EXPIRED]: '已过期'
};

export const APPROVAL_STATUS_COLOR: Record<number, string> = {
  [APPROVAL_STATUS.PENDING]: 'orange',
  [APPROVAL_STATUS.APPROVED]: 'green',
  [APPROVAL_STATUS.REJECTED]: 'red',
  [APPROVAL_STATUS.CANCELLED]: 'default',
  [APPROVAL_STATUS.EXPIRED]: 'default'
};

/**
 * 高危关键词常量
 */
export const HIGH_RISK_KEYWORDS = [
  'admin',
  'system',
  'root',
  'administrator',
  'supervisor'
];

/**
 * 验证账号名称
 */
export function validateAccountName(accountName: string): { 
  valid: boolean; 
  message?: string 
}> {
  if (!accountName) {
    return { valid: false, message: '账号名称不能为空' };
  }
  
  const lowerName = accountName.toLowerCase();
  
  for (const keyword of HIGH_RISK_KEYWORDS) {
    if (lowerName.includes(keyword)) {
      return {
        valid: false,
        message: `账号信息不可包含${keyword}，请修改`
      };
    }
  }
  
  if (accountName.length < 4) {
    return { valid: false, message: '账号名称长度不能少于4个字符' };
  }
  
  if (accountName.length > 20) {
    return { valid: false, message: '账号名称长度不能超过20个字符' };
  }
  
  if (!/^[a-zA-Z0-9_-]+$/.test(accountName)) {
    return { valid: false, message: '账号名称只能包含字母、数字、下划线和连字符' };
  }
  
  return { valid: true };
}

/**
 * 验证密码强度
 */
export function validatePasswordStrength(password: string): {
  valid: boolean;
  message?: string;
  warnings?: string[];
} {
  const warnings: string[] = [];
  
  if (!password) {
    return { valid: false, message: '密码不能为空' };
  }
  
  if (password.length < 8) {
    return { valid: false, message: '密码长度不能少于8个字符' };
  }
  
  if (password.length > 20) {
    return { valid: false, message: '密码长度不能超过20个字符' };
  }
  
  if (!/[A-Z]/.test(password)) {
    warnings.push('建议包含大写字母');
  }
  
  if (!/[a-z]/.test(password)) {
    warnings.push('建议包含小写字母');
  }
  
  if (!/[0-9]/.test(password)) {
    warnings.push('建议包含数字');
  }
  
  if (!/[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]/.test(password)) {
    warnings.push('建议包含特殊字符');
  }
  
  return {
    valid: true,
    warnings: warnings.length > 0 ? warnings : undefined
  };
}

/**
 * 格式化下载条件描述
 */
export function formatDownloadConditions(
  queryParams: Record<string, any>,
  fieldHeaders: string[]
): string {
  const conditions: string[] = [];
  
  // 添加时间范围
  if (queryParams.startDate) {
    conditions.push(`开始时间：${queryParams.startDate}`);
  }
  if (queryParams.endDate) {
    conditions.push(`截止时间：${queryParams.endDate}`);
  }
  
  // 添加其他查询条件
  for (const [key, value] of Object.entries(queryParams)) {
    if (!['startDate', 'endDate'].includes(key) && value) {
      conditions.push(`${key}：${value}`);
    }
  }
  
  // 添加字段列表
  if (fieldHeaders.length > 0) {
    conditions.push(`导出字段：${fieldHeaders.join('、')}`);
  }
  
  return conditions.join('; ');
}

/**
 * 生成申请单号
 */
export function generateApplicationNo(): string {
  const now = new Date();
  const dateStr = now.toString().slice(0, 19).replace(/[-: ]/g, '').replace(/ GMT.*/, '');
  const randomStr = Math.random().toString(36).substring(2, 8).toUpperCase();
  return `DA${dateStr}${randomStr}`;
}

/**
 * 获取审批状态文本
 */
export function getApprovalStatusText(status: ApprovalStatus): string {
  return APPROVAL_STATUS_TEXT[status] || '未知';
}

/**
 * 获取审批状态颜色
 */
export function getApprovalStatusColor(status: ApprovalStatus): string {
  return APPROVAL_STATUS_COLOR[status] || 'default';
}

/**
 * 截断文本
 */
export function truncateText(text: string, maxLength: number): string {
  if (!text) return '';
  return text.length > maxLength ? text.slice(0, maxLength) + '...' : text;
}
