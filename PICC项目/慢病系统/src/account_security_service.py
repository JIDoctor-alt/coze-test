"""
PICC人保健康门诊慢特病业务管理信息系统
账号安全服务模块
"""

import re
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

# 模拟数据库操作（实际项目中替换为ORM框架如SQLAlchemy）
class DatabaseMock:
    """模拟数据库操作"""
    
    _high_risk_blacklist = [
        {'id': 1, 'keyword': 'admin', 'keyword_type': 2, 'status': 1},
        {'id': 2, 'keyword': 'system', 'keyword_type': 2, 'status': 1},
        {'id': 3, 'keyword': 'root', 'keyword_type': 2, 'status': 1},
    ]
    
    _audit_logs: List[Dict] = []
    
    @classmethod
    def get_blacklist(cls) -> List[Dict]:
        return [item for item in cls._high_risk_blacklist if item['status'] == 1]
    
    @classmethod
    def save_audit_log(cls, log_data: Dict) -> int:
        log_data['id'] = len(cls._audit_logs) + 1
        cls._audit_logs.append(log_data)
        return log_data['id']


class AccountSourceType(Enum):
    """账号来源类型"""
    JINGBAN = "jingban"  # 经办端
    YISHENG = "yisheng"  # 医生端
    ZHUANJIA = "zhuanjia"  # 专家端


class LogType(Enum):
    """日志类型"""
    CREATE_ACCOUNT = 1
    MODIFY_ACCOUNT = 2
    DELETE_ACCOUNT = 3
    LOGIN = 4
    LOGOUT = 5
    PASSWORD_CHANGE = 6
    HIGH_RISK_BLOCKED = 7
    PERMISSION_CHANGE = 8


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class AccountInfo:
    """账号信息"""
    account_id: str
    account_name: str
    real_name: str
    id_card_number: str = ""
    phone_number: str = ""
    email: str = ""
    bank_card_number: str = ""
    address: str = ""
    account_source: AccountSourceType = AccountSourceType.JINGBAN
    city_code: str = ""
    city_name: str = ""
    status: int = 1
    is_high_risk: bool = False
    risk_reason: str = ""


@dataclass
class AuditLogEntry:
    """审计日志条目"""
    log_type: LogType
    account_id: str = ""
    account_name: str = ""
    real_name: str = ""
    city_code: str = ""
    city_name: str = ""
    role_type: str = ""
    ip_address: str = ""
    device_info: str = ""
    browser_info: str = ""
    operation_content: str = ""
    operation_result: int = 1  # 0-失败, 1-成功
    failure_reason: str = ""
    related_account: str = ""
    module_name: str = ""
    menu_name: str = ""
    request_params: str = ""
    response_result: str = ""


class HighRiskAccountValidator:
    """高危账号验证器"""
    
    def __init__(self):
        self.db = DatabaseMock()
    
    def load_blacklist(self) -> List[str]:
        """加载高危关键词黑名单"""
        blacklist = self.db.get_blacklist()
        return [item['keyword'].lower() for item in blacklist]
    
    def validate_account_name(self, account_name: str, city_code: str = "") -> ValidationResult:
        """
        验证账号名称是否包含高危关键词
        
        Args:
            account_name: 待验证的账号名称
            city_code: 地市编码
            
        Returns:
            ValidationResult: 验证结果
        """
        if not account_name:
            return ValidationResult(
                is_valid=False,
                error_message="账号名称不能为空",
                error_code="ACCOUNT_NAME_EMPTY"
            )
        
        # 转为小写进行匹配
        account_name_lower = account_name.lower()
        blacklist = self.load_blacklist()
        
        # 检查是否包含高危关键词
        blocked_keywords = []
        for keyword in blacklist:
            if keyword in account_name_lower:
                blocked_keywords.append(keyword)
        
        if blocked_keywords:
            return ValidationResult(
                is_valid=False,
                error_message=f"账号信息不可包含{','.join(blocked_keywords)}，请修改",
                error_code="HIGH_RISK_KEYWORD_BLOCKED",
                warnings=[f"检测到高危关键词: {','.join(blocked_keywords)}"]
            )
        
        # 检查账号长度
        if len(account_name) < 4:
            return ValidationResult(
                is_valid=False,
                error_message="账号名称长度不能少于4个字符",
                error_code="ACCOUNT_NAME_TOO_SHORT"
            )
        
        if len(account_name) > 20:
            return ValidationResult(
                is_valid=False,
                error_message="账号名称长度不能超过20个字符",
                error_code="ACCOUNT_NAME_TOO_LONG"
            )
        
        # 检查是否包含特殊字符
        if not re.match(r'^[a-zA-Z0-9_-]+$', account_name):
            return ValidationResult(
                is_valid=False,
                error_message="账号名称只能包含字母、数字、下划线和连字符",
                error_code="INVALID_ACCOUNT_NAME_FORMAT"
            )
        
        return ValidationResult(is_valid=True)
    
    def validate_password_strength(self, password: str) -> ValidationResult:
        """
        验证密码强度
        
        Args:
            password: 待验证的密码
            
        Returns:
            ValidationResult: 验证结果
        """
        if not password:
            return ValidationResult(
                is_valid=False,
                error_message="密码不能为空",
                error_code="PASSWORD_EMPTY"
            )
        
        warnings = []
        
        # 长度检查
        if len(password) < 8:
            return ValidationResult(
                is_valid=False,
                error_message="密码长度不能少于8个字符",
                error_code="PASSWORD_TOO_SHORT"
            )
        
        if len(password) > 20:
            return ValidationResult(
                is_valid=False,
                error_message="密码长度不能超过20个字符",
                error_code="PASSWORD_TOO_LONG"
            )
        
        # 复杂度检查
        if not re.search(r'[A-Z]', password):
            warnings.append("建议包含大写字母")
        
        if not re.search(r'[a-z]', password):
            warnings.append("建议包含小写字母")
        
        if not re.search(r'[0-9]', password):
            warnings.append("建议包含数字")
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]', password):
            warnings.append("建议包含特殊字符")
        
        if warnings:
            return ValidationResult(
                is_valid=True,
                warnings=warnings
            )
        
        return ValidationResult(is_valid=True)


class AccountSecurityService:
    """账号安全服务"""
    
    def __init__(self):
        self.validator = HighRiskAccountValidator()
        self.db = DatabaseMock()
    
    def check_high_risk_account(self, account_name: str) -> Tuple[bool, str]:
        """
        检查是否为高危账号
        
        Args:
            account_name: 账号名称
            
        Returns:
            Tuple[bool, str]: (是否高危, 高危原因)
        """
        validation = self.validator.validate_account_name(account_name)
        
        if not validation.is_valid:
            return True, validation.error_message
        
        return False, ""
    
    def generate_secure_account_name(self, 
                                     real_name: str, 
                                     city_code: str,
                                     source_type: AccountSourceType = AccountSourceType.JINGBAN) -> str:
        """
        生成安全的账号名称
        
        根据规则: 地市首字母缩写 + 用户名首字母缩写 + 随机数
        
        Args:
            real_name: 真实姓名
            city_code: 地市编码
            source_type: 账号来源类型
            
        Returns:
            str: 生成的账号名称
        """
        # 地市简码映射
        city_short_codes = {
            '610300': 'BJ',  # 宝鸡
            '130700': 'ZJK',  # 张家口
            '139000': 'DZ',  # 定州
            '610600': 'YA',  # 延安
            '611000': 'SL',  # 商洛
            '150700': 'MZL',  # 满洲里
            '610800': 'YL',  # 榆林
            '610400': 'YL',  # 杨凌
            '360400': 'JJ',  # 九江
            '140500': 'JC',  # 晋城
            '610400': 'XY',  # 咸阳
        }
        
        city_code_prefix = city_short_codes.get(city_code, city_code[:2].upper())
        
        # 获取姓名首字母缩写
        name_prefix = ''.join([char[0].upper() for char in real_name if char and '\u4e00' <= char <= '\u9fff'])
        if not name_prefix:
            name_prefix = real_name[:2].upper()
        
        # 生成随机数
        random_num = ''.join([str(secrets.randbelow(10)) for _ in range(4)])
        
        # 组合账号
        account_name = f"{city_code_prefix.lower()}{name_prefix.lower()}{random_num}"
        
        return account_name
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        密码哈希处理
        
        Args:
            password: 明文密码
            salt: 盐值（可选）
            
        Returns:
            Tuple[str, str]: (密码哈希, 盐值)
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # 使用PBKDF2进行密码哈希
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """
        验证密码
        
        Args:
            password: 待验证的密码
            password_hash: 存储的密码哈希
            salt: 盐值
            
        Returns:
            bool: 验证是否通过
        """
        computed_hash, _ = self.hash_password(password, salt)
        return computed_hash == password_hash
    
    def create_account(self, 
                       account_info: AccountInfo,
                       password: str,
                       ip_address: str = "",
                       device_info: str = "",
                       browser_info: str = "") -> Tuple[bool, str]:
        """
        创建账号
        
        Args:
            account_info: 账号信息
            password: 密码
            ip_address: IP地址
            device_info: 设备信息
            browser_info: 浏览器信息
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        # 验证账号名称
        validation = self.validator.validate_account_name(account_info.account_name, account_info.city_code)
        if not validation.is_valid:
            # 记录审计日志
            self._save_audit_log(
                LogType.HIGH_RISK_BLOCKED,
                account_info.account_name,
                account_info.real_name,
                account_info.city_code,
                f"创建账号失败: {validation.error_message}",
                0,
                ip_address,
                device_info,
                browser_info
            )
            return False, validation.error_message
        
        # 验证密码强度
        password_validation = self.validator.validate_password_strength(password)
        if not password_validation.is_valid:
            return False, password_validation.error_message
        
        # 生成密码哈希
        pwd_hash, salt = self.hash_password(password)
        
        # 保存账号信息（实际项目中保存到数据库）
        # ...
        
        # 记录审计日志
        self._save_audit_log(
            LogType.CREATE_ACCOUNT,
            account_info.account_id,
            account_info.account_name,
            account_info.real_name,
            f"创建账号成功",
            1,
            ip_address,
            device_info,
            browser_info
        )
        
        return True, "账号创建成功"
    
    def _save_audit_log(self,
                       log_type: LogType,
                       account_id: str,
                       account_name: str,
                       real_name: str,
                       operation_content: str,
                       operation_result: int,
                       ip_address: str = "",
                       device_info: str = "",
                       browser_info: str = "",
                       failure_reason: str = "",
                       city_code: str = "",
                       city_name: str = "",
                       module_name: str = "",
                       menu_name: str = "") -> int:
        """
        保存审计日志
        
        Args:
            log_type: 日志类型
            account_id: 账号ID
            account_name: 账号名称
            real_name: 真实姓名
            operation_content: 操作内容
            operation_result: 操作结果
            ip_address: IP地址
            device_info: 设备信息
            browser_info: 浏览器信息
            failure_reason: 失败原因
            city_code: 地市编码
            city_name: 地市名称
            module_name: 模块名称
            menu_name: 菜单名称
            
        Returns:
            int: 日志ID
        """
        log_data = {
            'log_type': log_type.value,
            'account_id': account_id,
            'account_name': account_name,
            'real_name': real_name,
            'city_code': city_code,
            'city_name': city_name,
            'operation_content': operation_content,
            'operation_result': operation_result,
            'failure_reason': failure_reason,
            'ip_address': ip_address,
            'device_info': device_info,
            'browser_info': browser_info,
            'module_name': module_name,
            'menu_name': menu_name,
            'created_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return self.db.save_audit_log(log_data)
    
    def query_audit_logs(self,
                         account_name: Optional[str] = None,
                         log_type: Optional[LogType] = None,
                         city_code: Optional[str] = None,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None,
                         page: int = 1,
                         page_size: int = 20) -> Dict[str, Any]:
        """
        查询审计日志
        
        Args:
            account_name: 账号名称
            log_type: 日志类型
            city_code: 地市编码
            start_time: 开始时间
            end_time: 结束时间
            page: 页码
            page_size: 每页数量
            
        Returns:
            Dict: 查询结果
        """
        # 模拟查询（实际项目中从数据库查询）
        logs = self.db._audit_logs
        
        # 应用过滤条件
        if account_name:
            logs = [log for log in logs if account_name in log.get('account_name', '')]
        
        if log_type:
            logs = [log for log in logs if log.get('log_type') == log_type.value]
        
        if city_code:
            logs = [log for log in logs if log.get('city_code') == city_code]
        
        # 分页
        total = len(logs)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_logs = logs[start_idx:end_idx]
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'data': page_logs
        }


# 导出API端点
ACCOUNT_SECURITY_ENDPOINTS = [
    {
        'path': '/api/v1/account/validate',
        'method': 'POST',
        'summary': '验证账号名称',
        'description': '验证账号名称是否包含高危关键词'
    },
    {
        'path': '/api/v1/account/create',
        'method': 'POST',
        'summary': '创建账号',
        'description': '创建新账号，包含高危账号检测'
    },
    {
        'path': '/api/v1/account/generate',
        'method': 'POST',
        'summary': '生成账号名称',
        'description': '根据姓名和地市生成安全的账号名称'
    },
    {
        'path': '/api/v1/audit/logs',
        'method': 'GET',
        'summary': '查询审计日志',
        'description': '分页查询账号安全审计日志'
    },
    {
        'path': '/api/v1/blacklist/keywords',
        'method': 'GET',
        'summary': '获取高危关键词列表',
        'description': '获取当前配置的高危关键词黑名单'
    },
    {
        'path': '/api/v1/blacklist/keywords',
        'method': 'POST',
        'summary': '添加高危关键词',
        'description': '添加新的高危关键词到黑名单'
    }
]


if __name__ == '__main__':
    # 测试用例
    service = AccountSecurityService()
    
    # 测试高危账号验证
    test_accounts = ['admin', 'admin001', 'system_user', 'root123', 'normal_user', 'ADMIN']
    print("=== 高危账号验证测试 ===")
    for account in test_accounts:
        is_high_risk, reason = service.check_high_risk_account(account)
        status = "高危" if is_high_risk else "安全"
        print(f"账号 '{account}': {status} - {reason if reason else '通过'}")
    
    # 测试密码强度验证
    print("\n=== 密码强度验证测试 ===")
    test_passwords = ['weak', 'WeakPass1!', 'StrongPass123!@#', '12345678']
    for pwd in test_passwords:
        result = service.validator.validate_password_strength(pwd)
        status = "有效" if result.is_valid else "无效"
        print(f"密码 '{pwd}': {status} - {result.error_message or '通过'}")
        if result.warnings:
            print(f"  警告: {', '.join(result.warnings)}")
    
    # 测试生成安全账号名称
    print("\n=== 生成安全账号名称测试 ===")
    test_cases = [
        ('张三', '610300'),
        ('李四', '130700'),
        ('王五', '611000'),
    ]
    for name, city in test_cases:
        account = service.generate_secure_account_name(name, city)
        print(f"姓名: {name}, 地市: {city} -> 账号: {account}")
