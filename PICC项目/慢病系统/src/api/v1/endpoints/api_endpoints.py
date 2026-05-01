"""
PICC人保健康门诊慢特病业务管理信息系统
RESTful API 端点定义
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

# =============================================
# API 响应格式定义
# =============================================

class ResponseCode(Enum):
    """响应码"""
    SUCCESS = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    SERVER_ERROR = 500


@dataclass
class ApiResponse:
    """API统一响应格式"""
    code: int
    message: str
    data: Any = None
    success: bool = True
    
    def to_dict(self) -> Dict:
        return {
            'code': self.code,
            'message': self.message,
            'data': self.data,
            'success': self.success
        }
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功") -> 'ApiResponse':
        return ApiResponse(
            code=ResponseCode.SUCCESS.value,
            message=message,
            data=data,
            success=True
        )
    
    @staticmethod
    def error(message: str, code: int = ResponseCode.BAD_REQUEST.value) -> 'ApiResponse':
        return ApiResponse(
            code=code,
            message=message,
            data=None,
            success=False
        )


# =============================================
# API 端点定义
# =============================================

API_ENDPOINTS: List[Dict[str, Any]] = [
    # ---- 账号安全相关 ----
    {
        'group': '账号安全',
        'items': [
            {
                'path': '/api/v1/account/validate',
                'method': 'POST',
                'summary': '验证账号名称',
                'description': '验证账号名称是否包含高危关键词（admin/system/root）',
                'request_body': {
                    'account_name': 'string(required) 账号名称',
                    'city_code': 'string(optional) 地市编码'
                },
                'response': {
                    '200': {'success': True, 'message': '验证通过'},
                    '400': {'success': False, 'message': '账号信息不可包含admin、system、root，请修改'}
                }
            },
            {
                'path': '/api/v1/account/create',
                'method': 'POST',
                'summary': '创建账号',
                'description': '创建新账号，包含高危账号检测和密码强度验证',
                'request_body': {
                    'account_name': 'string(required) 账号名称',
                    'real_name': 'string(required) 真实姓名',
                    'password': 'string(required) 密码',
                    'city_code': 'string(required) 地市编码',
                    'account_source': 'string(required) 账号来源：jingban/yisheng/zhuanjia',
                    'phone': 'string(optional) 手机号',
                    'id_card': 'string(optional) 身份证号'
                },
                'response': {
                    '200': {'success': True, 'message': '账号创建成功', 'data': {'account_id': 'xxx'}},
                    '400': {'success': False, 'message': '创建失败原因'}
                }
            },
            {
                'path': '/api/v1/account/generate',
                'method': 'POST',
                'summary': '生成账号名称',
                'description': '根据姓名和地市生成符合规范的账号名称',
                'request_body': {
                    'real_name': 'string(required) 真实姓名',
                    'city_code': 'string(required) 地市编码',
                    'account_source': 'string(optional) 账号来源'
                },
                'response': {
                    '200': {'success': True, 'data': {'account_name': 'bjzs1234'}}
                }
            },
            {
                'path': '/api/v1/audit/logs',
                'method': 'GET',
                'summary': '查询审计日志',
                'description': '分页查询账号安全审计日志',
                'query_params': {
                    'account_name': 'string(optional) 账号名称',
                    'log_type': 'int(optional) 日志类型',
                    'city_code': 'string(optional) 地市编码',
                    'start_time': 'datetime(optional) 开始时间',
                    'end_time': 'datetime(optional) 结束时间',
                    'page': 'int(default=1) 页码',
                    'page_size': 'int(default=20) 每页数量'
                },
                'response': {
                    '200': {
                        'success': True,
                        'data': {
                            'total': 100,
                            'page': 1,
                            'page_size': 20,
                            'list': []
                        }
                    }
                }
            }
        ]
    },
    
    # ---- 敏感数据相关 ----
    {
        'group': '敏感数据',
        'items': [
            {
                'path': '/api/v1/sensitive/mask',
                'method': 'POST',
                'summary': '脱敏数据',
                'description': '对敏感字段进行脱敏处理',
                'request_body': {
                    'data': 'object/array(required) 待脱敏数据',
                    'city_code': 'string(optional) 地市编码',
                    'menu_code': 'string(optional) 菜单编码'
                },
                'response': {
                    '200': {'success': True, 'data': {'masked_data': {}}}
                }
            },
            {
                'path': '/api/v1/sensitive/config',
                'method': 'GET',
                'summary': '获取脱敏配置',
                'description': '获取敏感字段脱敏配置列表',
                'response': {
                    '200': {
                        'success': True,
                        'data': [
                            {
                                'field_code': 'NAME',
                                'field_name': '姓名',
                                'masking_rule': 'first-last',
                                'example': {'original': '张三', 'masked': '张**'}
                            }
                        ]
                    }
                }
            },
            {
                'path': '/api/v1/sensitive/permission/check',
                'method': 'POST',
                'summary': '检查查看权限',
                'description': '检查用户查看敏感字段的权限',
                'request_body': {
                    'user_id': 'string(required) 用户ID',
                    'role_code': 'string(required) 角色编码',
                    'field_codes': 'array(required) 字段编码列表',
                    'city_code': 'string(optional) 地市编码'
                },
                'response': {
                    '200': {'success': True, 'data': {'NAME': True, 'IDCARD': True, 'PHONE': False}}
                }
            },
            {
                'path': '/api/v1/sensitive/log',
                'method': 'POST',
                'summary': '记录查看操作',
                'description': '记录用户查看敏感数据的操作',
                'request_body': {
                    'operator_id': 'string(required) 操作人ID',
                    'operator_name': 'string(required) 操作人姓名',
                    'operator_account': 'string(required) 操作人账号',
                    'field_codes': 'array(required) 查看的字段列表',
                    'record_count': 'int(required) 记录数量',
                    'city_code': 'string(optional) 地市编码',
                    'menu_code': 'string(optional) 菜单编码',
                    'reason': 'string(optional) 操作原因'
                }
            }
        ]
    },
    
    # ---- 下载审批相关 ----
    {
        'group': '下载审批',
        'items': [
            {
                'path': '/api/v1/approval/download/apply',
                'method': 'POST',
                'summary': '提交下载申请',
                'description': '提交数据下载/导出审批申请',
                'request_body': {
                    'city_code': 'string(required) 地市编码',
                    'menu_code': 'string(required) 菜单编码',
                    'menu_name': 'string(required) 菜单名称',
                    'download_type': 'string(required) 下载类型：export_excel/download_file/batch_download',
                    'download_purpose': 'string(required) 下载用途（200字内）',
                    'download_conditions': 'string(required) 下载范围条件',
                    'query_params': 'string(optional) 查询参数JSON'
                },
                'response': {
                    '200': {'success': True, 'message': '下载申请已提交', 'data': {'application_no': 'DA610300...'}},
                    '400': {'success': False, 'message': '请填写下载用途'}
                }
            },
            {
                'path': '/api/v1/approval/download/approve',
                'method': 'POST',
                'summary': '审批下载申请',
                'description': '审批下载申请（通过/不通过）',
                'request_body': {
                    'application_no': 'string(required) 申请单号',
                    'approval_result': 'int(required) 审批结果：1-通过，2-不通过',
                    'approval_comment': 'string(optional) 审批意见（200字内，不通过必填）'
                },
                'response': {
                    '200': {'success': True, 'message': '已审核通过'},
                    '400': {'success': False, 'message': '请选择审批结果'}
                }
            },
            {
                'path': '/api/v1/approval/download/list',
                'method': 'GET',
                'summary': '查询下载申请列表',
                'description': '分页查询下载申请列表',
                'query_params': {
                    'city_code': 'string(optional) 地市编码',
                    'menu_name': 'string(optional) 菜单名称（模糊搜索）',
                    'applicant_account': 'string(optional) 下载申请人',
                    'approver_account': 'string(optional) 审批人',
                    'approval_status': 'int(optional) 审批状态：0-未审核，1-审核通过，2-审核不通过',
                    'start_date': 'datetime(optional) 申请日期起',
                    'end_date': 'datetime(optional) 申请日期止',
                    'page': 'int(default=1) 页码',
                    'page_size': 'int(default=20) 每页数量'
                },
                'response': {
                    '200': {
                        'success': True,
                        'data': {
                            'total': 100,
                            'page': 1,
                            'page_size': 20,
                            'list': [
                                {
                                    'application_no': 'DA61030020260319xxx',
                                    'city_name': '宝鸡',
                                    'menu_name': '慢病申报查询',
                                    'applicant_name': '张三',
                                    'created_time': '2026-03-19 10:30:00',
                                    'approval_status': 0,
                                    'approval_status_text': '未审核'
                                }
                            ]
                        }
                    }
                }
            },
            {
                'path': '/api/v1/approval/download/detail',
                'method': 'GET',
                'summary': '获取申请详情',
                'description': '根据申请单号获取申请详情',
                'query_params': {
                    'application_no': 'string(required) 申请单号'
                },
                'response': {
                    '200': {
                        'success': True,
                        'data': {
                            'application_no': 'DA610300...',
                            'city_name': '宝鸡',
                            'menu_name': '慢病申报查询',
                            'download_purpose': '导出数据给医保局',
                            'download_conditions': '时间范围：xxx',
                            'approval_status': 1
                        }
                    }
                }
            },
            {
                'path': '/api/v1/approval/permission/cities',
                'method': 'GET',
                'summary': '获取可审批地市列表',
                'description': '获取当前用户可审批的地市列表',
                'response': {
                    '200': {
                        'success': True,
                        'data': [
                            {'city_code': '610300', 'city_name': '宝鸡'},
                            {'city_code': '610600', 'city_name': '延安'}
                        ]
                    }
                }
            },
            {
                'path': '/api/v1/download/validate',
                'method': 'POST',
                'summary': '验证下载权限',
                'description': '验证用户是否有权下载指定申请',
                'request_body': {
                    'application_no': 'string(required) 申请单号'
                },
                'response': {
                    '200': {'success': True, 'message': '允许下载'},
                    '400': {'success': False, 'message': '只有申请人可以下载'}
                }
            }
        ]
    }
]


def generate_api_doc() -> str:
    """生成API接口文档"""
    doc_lines = [
        "# PICC慢特病系统安全功能 API 接口文档",
        "",
        "## 接口概览",
        "",
    ]
    
    for group in API_ENDPOINTS:
        doc_lines.append(f"### {group['group']}")
        doc_lines.append("")
        
        for item in group['items']:
            doc_lines.append(f"#### {item['method']} {item['path']}")
            doc_lines.append(f"**{item['summary']}**")
            doc_lines.append("")
            doc_lines.append(item['description'])
            doc_lines.append("")
            
            if 'request_body' in item:
                doc_lines.append("**请求参数:**")
                doc_lines.append("```json")
                params = {}
                for key, desc in item['request_body'].items():
                    required = 'required' in desc
                    params[key] = {'description': desc.replace('(required)', '').replace('(optional)', '').strip()}
                    if required:
                        params[key]['required'] = True
                import json
                doc_lines.append(json.dumps(params, ensure_ascii=False, indent=2))
                doc_lines.append("```")
                doc_lines.append("")
            
            if 'query_params' in item:
                doc_lines.append("**查询参数:**")
                for key, desc in item['query_params'].items():
                    doc_lines.append(f"- `{key}`: {desc}")
                doc_lines.append("")
            
            if 'response' in item:
                doc_lines.append("**响应示例:**")
                doc_lines.append("```json")
                import json
                example_response = list(item['response'].values())[0]
                doc_lines.append(json.dumps(example_response, ensure_ascii=False, indent=2))
                doc_lines.append("```")
                doc_lines.append("")
            
            doc_lines.append("---")
            doc_lines.append("")
    
    return "\n".join(doc_lines)


if __name__ == '__main__':
    # 生成API文档
    doc = generate_api_doc()
    print(doc)
