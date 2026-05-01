"""
PICC人保健康门诊慢特病业务管理信息系统
敏感数据处理服务模块
"""

import re
import base64
import json
from datetime import datetime
from typing import Optional, List, Dict, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import os

# 模拟数据库配置（实际项目中替换为ORM框架）
class ConfigDB:
    """模拟配置数据库"""
    
    _field_configs = {
        'NAME': {
            'field_code': 'NAME',
            'field_name': '姓名',
            'field_type': 'name',
            'masking_rule': 'first-last',
            'preserve_chars': 1,
            'mask_length': 2,
            'mask_char': '*',
            'masking_template': '{first}**'
        },
        'IDCARD': {
            'field_code': 'IDCARD',
            'field_name': '身份证号',
            'field_type': 'idcard',
            'masking_rule': 'front-back',
            'preserve_chars': 6,
            'preserve_chars_end': 4,
            'mask_char': '*',
            'masking_template': '{front}********{back}'
        },
        'PHONE': {
            'field_code': 'PHONE',
            'field_name': '手机号码',
            'field_type': 'phone',
            'masking_rule': 'front-back',
            'preserve_chars': 3,
            'preserve_chars_end': 4,
            'mask_char': '*',
            'masking_template': '{front}****{back}'
        },
        'BANKCARD': {
            'field_code': 'BANKCARD',
            'field_name': '银行卡号',
            'field_type': 'bankcard',
            'masking_rule': 'front-back',
            'preserve_chars': 6,
            'preserve_chars_end': 4,
            'mask_char': '*',
            'masking_template': '{front}****{back}'
        },
        'ADDRESS': {
            'field_code': 'ADDRESS',
            'field_name': '地址',
            'field_type': 'address',
            'masking_rule': 'prefix-suffix',
            'preserve_chars': 0,
            'mask_length': 6,
            'mask_char': '*',
            'masking_template': '{province}{city}{mask}'
        },
        'EMAIL': {
            'field_code': 'EMAIL',
            'field_name': '邮箱',
            'field_type': 'email',
            'masking_rule': 'front-back',
            'preserve_chars': 6,
            'preserve_chars_end': 0,
            'mask_char': '*',
            'masking_template': '{front}******'
        }
    }
    
    _menu_field_mappings = {}
    _view_permissions = {}


class FieldType(Enum):
    """敏感字段类型"""
    NAME = "name"           # 姓名
    IDCARD = "idcard"       # 身份证号
    PHONE = "phone"         # 手机号
    BANKCARD = "bankcard"   # 银行卡号
    ADDRESS = "address"     # 地址
    EMAIL = "email"         # 邮箱


class MaskingRule(Enum):
    """脱敏规则"""
    FIRST_LAST = "first-last"       # 首尾保留
    FRONT_BACK = "front-back"       # 前后保留
    FRONT_ONLY = "front"            # 仅保留首部
    BACK_ONLY = "back"              # 仅保留尾部
    FULL_MASK = "full"              # 完全隐藏
    PREFIX_SUFFIX = "prefix-suffix"  # 前后缀保留


@dataclass
class FieldConfig:
    """字段脱敏配置"""
    field_code: str
    field_name: str
    field_type: FieldType
    masking_rule: MaskingRule
    preserve_chars: int = 1
    preserve_chars_end: int = 4
    mask_char: str = '*'
    mask_length: int = 6
    masking_template: str = ""


@dataclass
class MaskingResult:
    """脱敏结果"""
    original_value: str
    masked_value: str
    field_code: str
    field_type: str
    is_masked: bool = True


class SensitiveDataMasker:
    """敏感数据脱敏处理器"""
    
    def __init__(self):
        self.config_db = ConfigDB()
    
    def get_field_config(self, field_code: str) -> Optional[FieldConfig]:
        """获取字段配置"""
        config = self.config_db._field_configs.get(field_code)
        if not config:
            return None
        
        return FieldConfig(
            field_code=config['field_code'],
            field_name=config['field_name'],
            field_type=FieldType(config['field_type']),
            masking_rule=MaskingRule(config['masking_rule']),
            preserve_chars=config.get('preserve_chars', 1),
            preserve_chars_end=config.get('preserve_chars_end', 4),
            mask_char=config.get('mask_char', '*'),
            mask_length=config.get('mask_length', 6),
            masking_template=config.get('masking_template', '')
        )
    
    def mask_name(self, value: str, config: FieldConfig) -> str:
        """
        脱敏处理 - 姓名
        默认规则：保留姓氏，其余用**代替
        示例：张三 -> 张**
        """
        if not value:
            return value
        
        # 判断是否是中文姓名
        if re.match(r'^[\u4e00-\u9fa5]+$', value):
            # 中文姓名
            if len(value) == 1:
                return value + '**'
            elif len(value) >= 2:
                return value[0] + '**'
        else:
            # 英文或其他姓名
            parts = value.split()
            if len(parts) == 1:
                if len(value) <= 2:
                    return value[0] + '**'
                else:
                    return value[0] + '**' + value[-1]
            else:
                # 英文名保留首字母大写，其余小写
                return parts[0][0].upper() + '**'
        
        return value[0] + '**'
    
    def mask_idcard(self, value: str, config: FieldConfig) -> str:
        """
        脱敏处理 - 身份证号
        默认规则：前6位后4位保留，中间用8个*代替
        示例：610310199001011234 -> 610310********1234
        """
        if not value:
            return value
        
        # 移除可能存在的空格或X/x后缀
        clean_value = value.strip().upper().rstrip('X').rstrip('x')
        
        if len(clean_value) <= 10:
            return clean_value
        
        front = clean_value[:6]
        back = clean_value[-4:]
        mask = '*' * 8
        
        return f"{front}{mask}{back}"
    
    def mask_phone(self, value: str, config: FieldConfig) -> str:
        """
        脱敏处理 - 手机号
        默认规则：前3位后4位保留，中间用4个*代替
        示例：13812345678 -> 138****5678
        """
        if not value:
            return value
        
        # 移除可能存在的空格、-等分隔符
        clean_value = re.sub(r'[\s\-]+', '', value)
        
        if len(clean_value) < 7:
            return clean_value
        
        front = clean_value[:3]
        back = clean_value[-4:]
        mask = '*' * 4
        
        return f"{front}{mask}{back}"
    
    def mask_bankcard(self, value: str, config: FieldConfig) -> str:
        """
        脱敏处理 - 银行卡号
        默认规则：前6位后4位保留，中间用*代替
        示例：6222021234567890123 -> 622202****7890123
        """
        if not value:
            return value
        
        # 移除可能存在的空格
        clean_value = re.sub(r'[\s]+', '', value)
        
        if len(clean_value) <= 10:
            return clean_value
        
        front = clean_value[:6]
        back = clean_value[-4:]
        mask_length = len(clean_value) - 10
        mask = '*' * mask_length
        
        return f"{front}{mask}{back}"
    
    def mask_address(self, value: str, config: FieldConfig) -> str:
        """
        脱敏处理 - 地址
        默认规则：保留省+市，详细地址用6个*代替
        示例：北京市丰台区西局欣园小区5号楼 -> 北京市丰台区******
        """
        if not value:
            return value
        
        # 尝试提取省市区信息
        # 简化处理：保留前N个字符，后面的详细地址脱敏
        if len(value) <= 10:
            return value
        
        # 保留前10个字符（通常是省市区信息）
        prefix = value[:10]
        suffix_length = min(6, len(value) - 10)
        suffix = '*' * suffix_length
        
        return prefix + suffix
    
    def mask_email(self, value: str, config: FieldConfig) -> str:
        """
        脱敏处理 - 邮箱
        默认规则：前6位保留，后面用6个*代替
        示例：zhangsan@example.com -> zhangs******@example.com
        """
        if not value:
            return value
        
        if '@' not in value:
            return value
        
        parts = value.split('@')
        if len(parts) != 2:
            return value
        
        username = parts[0]
        domain = parts[1]
        
        if len(username) <= 6:
            masked_username = username + '******'
        else:
            masked_username = username[:6] + '******'
        
        return f"{masked_username}@{domain}"
    
    def mask_value(self, value: str, field_code: str) -> str:
        """
        根据字段类型执行脱敏
        
        Args:
            value: 原始值
            field_code: 字段编码
            
        Returns:
            str: 脱敏后的值
        """
        config = self.get_field_config(field_code)
        if not config:
            return value
        
        if not value:
            return value
        
        field_type = config.field_type
        
        if field_type == FieldType.NAME:
            return self.mask_name(value, config)
        elif field_type == FieldType.IDCARD:
            return self.mask_idcard(value, config)
        elif field_type == FieldType.PHONE:
            return self.mask_phone(value, config)
        elif field_type == FieldType.BANKCARD:
            return self.mask_bankcard(value, config)
        elif field_type == FieldType.ADDRESS:
            return self.mask_address(value, config)
        elif field_type == FieldType.EMAIL:
            return self.mask_email(value, config)
        
        return value
    
    def mask_record(self, record: Dict[str, Any], field_mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        批量脱敏处理记录
        
        Args:
            record: 原始记录
            field_mapping: 字段映射，key为原始字段名，value为字段编码
            
        Returns:
            Dict: 脱敏后的记录
        """
        masked_record = record.copy()
        
        for original_field, field_code in field_mapping.items():
            if original_field in record and record[original_field]:
                masked_record[original_field] = self.mask_value(
                    str(record[original_field]),
                    field_code
                )
        
        return masked_record


class DataEncryptor:
    """数据加密器"""
    
    def __init__(self):
        self._encryption_key = self._load_or_generate_key()
    
    def _load_or_generate_key(self) -> bytes:
        """加载或生成加密密钥"""
        # 实际项目中从密钥管理服务获取
        # 这里使用模拟密钥
        key_str = "PICC_CHRONIC_DISEASE_SECURE_KEY_2024"
        return hashlib.sha256(key_str.encode()).digest()
    
    def encrypt(self, plaintext: str) -> str:
        """
        加密数据
        
        Args:
            plaintext: 明文
            
        Returns:
            str: Base64编码的密文
        """
        if not plaintext:
            return plaintext
        
        # 简化实现，实际应使用AES-256-GCM等加密算法
        key = self._encryption_key
        encrypted = bytes([ord(c) ^ key[i % len(key)] for i, c in enumerate(plaintext)])
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """
        解密数据
        
        Args:
            ciphertext: Base64编码的密文
            
        Returns:
            str: 明文
        """
        if not ciphertext:
            return ciphertext
        
        # 简化实现
        key = self._encryption_key
        encrypted = base64.b64decode(ciphertext.encode())
        decrypted = ''.join([chr(encrypted[i] ^ key[i % len(key)]) for i in range(len(encrypted))])
        return decrypted


class SensitiveDataService:
    """敏感数据处理服务"""
    
    def __init__(self):
        self.masker = SensitiveDataMasker()
        self.encryptor = DataEncryptor()
        self.config_db = ConfigDB()
    
    def mask_sensitive_fields(self, 
                               data: Union[Dict, List[Dict]], 
                               city_code: str = "",
                               menu_code: str = "") -> Union[Dict, List[Dict]]:
        """
        批量脱敏敏感字段
        
        Args:
            data: 待脱敏数据
            city_code: 地市编码
            menu_code: 菜单编码
            
        Returns:
            脱敏后的数据
        """
        # 获取该菜单的字段映射配置
        field_mapping = self._get_field_mapping(city_code, menu_code)
        
        if isinstance(data, list):
            return [self.masker.mask_record(record, field_mapping) for record in data]
        else:
            return self.masker.mask_record(data, field_mapping)
    
    def _get_field_mapping(self, city_code: str, menu_code: str) -> Dict[str, str]:
        """
        获取字段映射配置
        
        Args:
            city_code: 地市编码
            menu_code: 菜单编码
            
        Returns:
            Dict: 字段映射
        """
        # 默认字段映射
        default_mapping = {
            'name': 'NAME',
            'real_name': 'NAME',
            'user_name': 'NAME',
            'id_card': 'IDCARD',
            'id_card_number': 'IDCARD',
            'idcard': 'IDCARD',
            'cert_no': 'IDCARD',
            'phone': 'PHONE',
            'phone_number': 'PHONE',
            'mobile': 'PHONE',
            'telephone': 'PHONE',
            'bank_card': 'BANKCARD',
            'bank_card_number': 'BANKCARD',
            'card_no': 'BANKCARD',
            'address': 'ADDRESS',
            'home_address': 'ADDRESS',
            'email': 'EMAIL',
        }
        
        # 实际项目中应根据city_code和menu_code从数据库查询具体配置
        return default_mapping
    
    def check_view_permission(self, 
                              user_id: str, 
                              role_code: str,
                              field_codes: List[str],
                              city_code: str = "") -> Dict[str, bool]:
        """
        检查用户查看敏感字段的权限
        
        Args:
            user_id: 用户ID
            role_code: 角色编码
            field_codes: 字段编码列表
            city_code: 地市编码
            
        Returns:
            Dict: 每个字段的查看权限
        """
        permissions = {}
        
        # 角色权限配置
        role_permissions = {
            'ROLE_ADMIN': ['NAME', 'IDCARD', 'PHONE', 'BANKCARD', 'ADDRESS', 'EMAIL'],
            'ROLE_JINGBAN': ['NAME', 'IDCARD', 'PHONE'],
            'ROLE_YISHENG': ['NAME', 'IDCARD', 'PHONE'],
            'ROLE_ZHUANJIA': ['NAME', 'IDCARD', 'PHONE'],
            'ROLE_AUDITOR': ['NAME', 'IDCARD', 'PHONE', 'BANKCARD', 'ADDRESS', 'EMAIL'],
        }
        
        allowed_fields = role_permissions.get(role_code, [])
        
        for field_code in field_codes:
            permissions[field_code] = field_code in allowed_fields
        
        return permissions
    
    def log_view_operation(self,
                           operator_id: str,
                           operator_name: str,
                           operator_account: str,
                           field_codes: List[str],
                           record_count: int,
                           city_code: str = "",
                           menu_code: str = "",
                           reason: str = "") -> int:
        """
        记录敏感数据查看操作
        
        Args:
            operator_id: 操作人ID
            operator_name: 操作人姓名
            operator_account: 操作人账号
            field_codes: 查看的字段列表
            record_count: 记录数量
            city_code: 地市编码
            menu_code: 菜单编码
            reason: 操作原因
            
        Returns:
            int: 日志ID
        """
        # 实际项目中保存到数据库
        log_data = {
            'operation_type': 1,  # 查看明文
            'operator_id': operator_id,
            'operator_name': operator_name,
            'operator_account': operator_account,
            'city_code': city_code,
            'menu_code': menu_code,
            'field_list': ','.join(field_codes),
            'record_count': record_count,
            'operation_reason': reason,
            'created_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 模拟保存
        return 1
    
    def get_masking_config(self, field_code: str) -> Optional[Dict]:
        """
        获取字段脱敏配置
        
        Args:
            field_code: 字段编码
            
        Returns:
            Dict: 脱敏配置
        """
        config = self.masker.get_field_config(field_code)
        if not config:
            return None
        
        return {
            'field_code': config.field_code,
            'field_name': config.field_name,
            'field_type': config.field_type.value,
            'masking_rule': config.masking_rule.value,
            'preserve_chars': config.preserve_chars,
            'mask_char': config.mask_char,
        }
    
    def get_all_masking_configs(self) -> List[Dict]:
        """
        获取所有字段脱敏配置
        
        Returns:
            List[Dict]: 配置列表
        """
        configs = []
        for field_code in ConfigDB._field_configs.keys():
            config = self.get_masking_config(field_code)
            if config:
                configs.append(config)
        return configs


# 导出API端点
SENSITIVE_DATA_ENDPOINTS = [
    {
        'path': '/api/v1/sensitive/mask',
        'method': 'POST',
        'summary': '脱敏数据',
        'description': '对敏感字段进行脱敏处理'
    },
    {
        'path': '/api/v1/sensitive/encrypt',
        'method': 'POST',
        'summary': '加密数据',
        'description': '对敏感数据进行加密存储'
    },
    {
        'path': '/api/v1/sensitive/decrypt',
        'method': 'POST',
        'summary': '解密数据',
        'description': '对加密数据进行解密'
    },
    {
        'path': '/api/v1/sensitive/config',
        'method': 'GET',
        'summary': '获取脱敏配置',
        'description': '获取敏感字段脱敏配置列表'
    },
    {
        'path': '/api/v1/sensitive/permission/check',
        'method': 'POST',
        'summary': '检查查看权限',
        'description': '检查用户查看敏感字段的权限'
    },
    {
        'path': '/api/v1/sensitive/log',
        'method': 'POST',
        'summary': '记录查看操作',
        'description': '记录用户查看敏感数据的操作'
    }
]


if __name__ == '__main__':
    # 测试用例
    service = SensitiveDataService()
    
    # 测试各类型数据脱敏
    print("=== 敏感数据脱敏测试 ===")
    
    test_data = {
        'name': '张三',
        'id_card': '610310199001011234',
        'phone': '13812345678',
        'bank_card': '6222021234567890123',
        'address': '北京市丰台区西局欣园小区5号楼1201',
        'email': 'zhangsan@example.com'
    }
    
    print("原始数据:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    # 脱敏处理
    masked_data = service.mask_sensitive_fields(test_data)
    
    print("\n脱敏后数据:")
    for key, value in masked_data.items():
        print(f"  {key}: {value}")
    
    # 测试权限检查
    print("\n=== 权限检查测试 ===")
    permissions = service.check_view_permission(
        user_id='user001',
        role_code='ROLE_JINGBAN',
        field_codes=['NAME', 'IDCARD', 'PHONE', 'BANKCARD']
    )
    for field, has_perm in permissions.items():
        print(f"  {field}: {'有权限' if has_perm else '无权限'}")
    
    # 测试加密解密
    print("\n=== 加密解密测试 ===")
    original = "13812345678"
    encrypted = service.encryptor.encrypt(original)
    decrypted = service.encryptor.decrypt(encrypted)
    print(f"  原始: {original}")
    print(f"  加密: {encrypted}")
    print(f"  解密: {decrypted}")
