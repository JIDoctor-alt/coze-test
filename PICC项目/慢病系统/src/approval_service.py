"""
PICC人保健康门诊慢特病业务管理信息系统
审批流程服务模块
"""

import re
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

# 模拟数据库
class ApprovalDB:
    """审批数据库模拟"""
    
    _applications: List[Dict] = []
    _approval_records: List[Dict] = []
    _flow_configs: Dict[str, Dict] = {}
    _permissions: Dict[str, Dict] = {}
    
    @classmethod
    def init_data(cls):
        """初始化数据"""
        # 审批流程配置
        cities = ['610300', '130700', '139000', '610600', '611000', 
                  '150700', '610800', '610400', '360400', '140500']
        city_names = ['宝鸡', '张家口', '定州', '延安', '商洛', 
                      '满洲里', '榆林', '杨凌', '九江', '晋城']
        
        for code, name in zip(cities, city_names):
            cls._flow_configs[code] = {
                'flow_code': f'FLOW_DOWNLOAD_{code}',
                'flow_name': f'{name}下载审批流程',
                'city_code': code,
                'city_name': name,
                'approval_levels': 1,
                'expire_hours': 72,
                'status': 1
            }
            
            cls._permissions[code] = {
                'permission_code': f'PERM_APPROVAL_{code}',
                'permission_name': f'审批({name}下载)',
                'city_code': code,
                'city_name': name
            }
    
    @classmethod
    def save_application(cls, app_data: Dict) -> int:
        app_data['id'] = len(cls._applications) + 1
        cls._applications.append(app_data)
        return app_data['id']
    
    @classmethod
    def get_applications(cls) -> List[Dict]:
        return cls._applications
    
    @classmethod
    def save_approval_record(cls, record: Dict) -> int:
        record['id'] = len(cls._approval_records) + 1
        cls._approval_records.append(record)
        return record['id']


# 初始化数据
ApprovalDB.init_data()


class ApprovalStatus(Enum):
    """审批状态"""
    PENDING = 0      # 未审核
    APPROVED = 1     # 审核通过
    REJECTED = 2     # 审核不通过
    CANCELLED = 3    # 已取消
    EXPIRED = 4      # 已过期


class DownloadType(Enum):
    """下载类型"""
    EXPORT_EXCEL = "export_excel"       # 导出Excel
    DOWNLOAD_FILE = "download_file"     # 下载文件
    BATCH_DOWNLOAD = "batch_download"    # 批量下载


@dataclass
class DownloadApplication:
    """下载申请"""
    city_code: str
    city_name: str
    menu_code: str
    menu_name: str
    download_type: DownloadType
    download_purpose: str
    download_conditions: str
    applicant_id: str
    applicant_name: str
    applicant_account: str
    query_params: str = ""
    file_name: str = ""
    file_path: str = ""
    record_count: int = 0


@dataclass
class ApprovalRequest:
    """审批请求"""
    application_no: str
    approval_result: int  # 1-通过, 2-不通过
    approval_comment: str = ""
    approver_id: str = ""
    approver_name: str = ""
    approver_account: str = ""


@dataclass
class ApprovalQuery:
    """审批查询条件"""
    city_code: Optional[str] = None
    menu_code: Optional[str] = None
    applicant_account: Optional[str] = None
    approver_account: Optional[str] = None
    approval_status: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = 1
    page_size: int = 20


class ApprovalService:
    """审批流程服务"""
    
    def __init__(self):
        self.db = ApprovalDB()
    
    def generate_application_no(self) -> str:
        """
        生成申请单号
        格式：DA + 地市编码 + 年月日时分秒 + 随机数
        示例：DA61030020250319123456123
        """
        now = datetime.now()
        date_str = now.strftime('%Y%m%d%H%M%S')
        random_str = str(uuid.uuid4().int)[:6]
        return f"DA{date_str}{random_str}"
    
    def create_download_application(self, 
                                    application: DownloadApplication) -> Tuple[bool, str, Optional[str]]:
        """
        创建下载申请
        
        Args:
            application: 下载申请信息
            
        Returns:
            Tuple[bool, str, Optional[str]]: (是否成功, 消息, 申请单号)
        """
        # 参数校验
        if not application.download_purpose or len(application.download_purpose.strip()) == 0:
            return False, "请填写下载用途", None
        
        if len(application.download_purpose) > 200:
            return False, "下载用途不能超过200字", None
        
        if not application.applicant_id:
            return False, "申请人信息不完整", None
        
        # 生成申请单号
        application_no = self.generate_application_no()
        
        # 保存申请记录
        app_data = {
            'application_no': application_no,
            'city_code': application.city_code,
            'city_name': application.city_name,
            'menu_code': application.menu_code,
            'menu_name': application.menu_name,
            'download_type': application.download_type.value,
            'download_purpose': application.download_purpose,
            'download_conditions': application.download_conditions,
            'query_params': application.query_params,
            'applicant_id': application.applicant_id,
            'applicant_name': application.applicant_name,
            'applicant_account': application.applicant_account,
            'approval_status': ApprovalStatus.PENDING.value,
            'record_count': application.record_count,
            'file_name': application.file_name,
            'file_path': application.file_path,
            'download_count': 0,
            'created_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.db.save_application(app_data)
        
        return True, "下载申请已提交，请等待审批", application_no
    
    def approve_application(self, request: ApprovalRequest) -> Tuple[bool, str]:
        """
        审批下载申请
        
        Args:
            request: 审批请求
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        # 获取申请记录
        applications = self.db.get_applications()
        application = None
        app_index = -1
        
        for i, app in enumerate(applications):
            if app['application_no'] == request.application_no:
                application = app
                app_index = i
                break
        
        if not application:
            return False, "申请记录不存在"
        
        # 检查申请状态
        if application['approval_status'] != ApprovalStatus.PENDING.value:
            return False, f"当前状态不允许审批"
        
        # 校验审批参数
        if not request.approval_result:
            return False, "请选择审批结果"
        
        if request.approval_result == 2 and not request.approval_comment:
            return False, "请填写审批意见"
        
        if len(request.approval_comment or '') > 200:
            return False, "审批意见不能超过200字"
        
        # 更新申请状态
        new_status = (ApprovalStatus.APPROVED.value if request.approval_result == 1 
                      else ApprovalStatus.REJECTED.value)
        
        # 计算过期时间（默认72小时）
        expire_time = datetime.now() + timedelta(hours=72)
        
        self.db._applications[app_index].update({
            'approval_status': new_status,
            'approver_id': request.approver_id,
            'approver_name': request.approver_name,
            'approver_account': request.approver_account,
            'approval_comment': request.approval_comment,
            'approval_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'expire_time': expire_time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # 保存审批记录
        record = {
            'application_no': request.application_no,
            'approver_id': request.approver_id,
            'approver_name': request.approver_name,
            'approver_account': request.approver_account,
            'approval_result': request.approval_result,
            'approval_comment': request.approval_comment,
            'approval_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.db.save_approval_record(record)
        
        result_text = "审核通过" if request.approval_result == 1 else "审核不通过"
        return True, f"已{result_text}"
    
    def query_applications(self, query: ApprovalQuery) -> Dict[str, Any]:
        """
        查询下载申请列表
        
        Args:
            query: 查询条件
            
        Returns:
            Dict: 查询结果
        """
        applications = self.db.get_applications()
        
        # 应用过滤条件
        filtered = applications
        
        if query.city_code:
            filtered = [a for a in filtered if a['city_code'] == query.city_code]
        
        if query.menu_code:
            filtered = [a for a in filtered if a['menu_code'] == query.menu_code]
        
        if query.applicant_account:
            filtered = [a for a in filtered if a['applicant_account'] == query.applicant_account]
        
        if query.approver_account:
            filtered = [a for a in filtered if a.get('approver_account') == query.approver_account]
        
        if query.approval_status is not None:
            filtered = [a for a in filtered if a['approval_status'] == query.approval_status]
        
        if query.start_date:
            filtered = [a for a in filtered 
                       if datetime.strptime(a['created_time'], '%Y-%m-%d %H:%M:%S') >= query.start_date]
        
        if query.end_date:
            filtered = [a for a in filtered 
                       if datetime.strptime(a['created_time'], '%Y-%m-%d %H:%M:%S') <= query.end_date]
        
        # 排序（按创建时间倒序）
        filtered.sort(key=lambda x: x['created_time'], reverse=True)
        
        # 分页
        total = len(filtered)
        start_idx = (query.page - 1) * query.page_size
        end_idx = start_idx + query.page_size
        page_data = filtered[start_idx:end_idx]
        
        return {
            'total': total,
            'page': query.page,
            'page_size': query.page_size,
            'data': page_data
        }
    
    def get_application_detail(self, application_no: str) -> Optional[Dict]:
        """
        获取申请详情
        
        Args:
            application_no: 申请单号
            
        Returns:
            Optional[Dict]: 申请详情
        """
        applications = self.db.get_applications()
        for app in applications:
            if app['application_no'] == application_no:
                return app
        return None
    
    def check_download_permission(self, 
                                  user_id: str, 
                                  user_account: str,
                                  role_code: str,
                                  city_code: str) -> bool:
        """
        检查用户是否有下载权限
        
        Args:
            user_id: 用户ID
            user_account: 用户账号
            role_code: 角色编码
            city_code: 地市编码
            
        Returns:
            bool: 是否有下载权限
        """
        # 管理员有所有权限
        if role_code == 'ROLE_ADMIN' or role_code == 'SUPER_ADMIN':
            return True
        
        # 检查是否有该地市的审批权限配置
        # 实际项目中应从数据库查询用户的具体权限
        return True
    
    def check_approval_permission(self,
                                   user_id: str,
                                   role_code: str,
                                   city_code: str) -> bool:
        """
        检查用户是否有审批权限
        
        Args:
            user_id: 用户ID
            role_code: 角色编码
            city_code: 地市编码
            
        Returns:
            bool: 是否有审批权限
        """
        # 检查该地市是否有审批权限配置
        permission_key = f'PERM_APPROVAL_{city_code}'
        
        if permission_key in self.db._permissions:
            # 实际项目中应检查用户是否被分配了该权限
            # 这里简化处理：只有特定角色有审批权限
            if role_code in ['ROLE_ADMIN', 'SUPER_ADMIN', 'ROLE_APPROVER']:
                return True
        
        return False
    
    def get_city_permissions(self, role_code: str) -> List[Dict]:
        """
        获取角色可审批的地市列表
        
        Args:
            role_code: 角色编码
            
        Returns:
            List[Dict]: 地市权限列表
        """
        if role_code == 'ROLE_ADMIN' or role_code == 'SUPER_ADMIN':
            # 管理员有所有地市的审批权限
            return list(self.db._permissions.values())
        
        # 实际项目中应从数据库查询用户的地市审批权限
        # 这里简化处理：返回空列表
        return []
    
    def validate_download(self,
                          application_no: str,
                          user_account: str) -> Tuple[bool, str]:
        """
        验证下载请求
        
        Args:
            application_no: 申请单号
            user_account: 用户账号
            
        Returns:
            Tuple[bool, str]: (是否允许, 消息)
        """
        application = self.get_application_detail(application_no)
        
        if not application:
            return False, "申请记录不存在"
        
        # 检查申请人是否为当前用户
        if application['applicant_account'] != user_account:
            return False, "只有申请人可以下载"
        
        # 检查审批状态
        if application['approval_status'] != ApprovalStatus.APPROVED.value:
            status_text = {
                0: "待审批",
                2: "审批未通过",
                3: "已取消",
                4: "已过期"
            }.get(application['approval_status'], "未知状态")
            return False, f"当前状态: {status_text}，不允许下载"
        
        # 检查是否过期
        if application.get('expire_time'):
            expire_time = datetime.strptime(application['expire_time'], '%Y-%m-%d %H:%M:%S')
            if datetime.now() > expire_time:
                return False, "下载申请已过期"
        
        return True, "允许下载"
    
    def record_download(self, application_no: str) -> bool:
        """
        记录下载操作
        
        Args:
            application_no: 申请单号
            
        Returns:
            bool: 是否成功
        """
        applications = self.db.get_applications()
        for i, app in enumerate(applications):
            if app['application_no'] == application_no:
                self.db._applications[i]['download_count'] = app.get('download_count', 0) + 1
                self.db._applications[i]['last_download_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                return True
        return False


class DownloadApplicationHelper:
    """下载申请辅助类"""
    
    @staticmethod
    def format_download_conditions(query_params: Dict, field_headers: List[str]) -> str:
        """
        格式化下载范围条件
        
        Args:
            query_params: 查询参数
            field_headers: 字段表头
            
        Returns:
            str: 格式化的条件描述
        """
        conditions = []
        
        # 添加时间范围
        if query_params.get('start_date'):
            conditions.append(f"开始时间：{query_params['start_date']}")
        if query_params.get('end_date'):
            conditions.append(f"截止时间：{query_params['end_date']}")
        
        # 添加其他查询条件
        for key, value in query_params.items():
            if key not in ['start_date', 'end_date'] and value:
                conditions.append(f"{key}：{value}")
        
        # 添加字段列表
        if field_headers:
            conditions.append(f"导出字段：{','.join(field_headers)}")
        
        return "; ".join(conditions)
    
    @staticmethod
    def get_button_text(menu_code: str, button_type: str) -> str:
        """
        获取按钮显示文本
        
        Args:
            menu_code: 菜单编码
            button_type: 按钮类型
            
        Returns:
            str: 按钮文本
        """
        button_texts = {
            'BTN_EXPORT': '导出Excel',
            'BTN_ERROR_DOWNLOAD': '错误数据下载',
            'BTN_PRINT': '打印结算单',
            'BTN_DOWNLOAD': '下载',
            'BTN_BATCH_DOWNLOAD': '批量下载影像件',
            'BTN_BATCH_APPROVAL': '批量下载审批表',
            'BTN_HISTORY_EXPORT': '历史处方导出',
            'BTN_CARD_DOWNLOAD': '慢病凭证下载',
            'BTN_TREATMENT_DOWNLOAD': '治疗通知书下载',
        }
        
        return button_texts.get(button_type, '下载')


# 导出API端点
APPROVAL_ENDPOINTS = [
    {
        'path': '/api/v1/approval/download/apply',
        'method': 'POST',
        'summary': '提交下载申请',
        'description': '提交数据下载/导出审批申请'
    },
    {
        'path': '/api/v1/approval/download/approve',
        'method': 'POST',
        'summary': '审批下载申请',
        'description': '审批下载申请（通过/不通过）'
    },
    {
        'path': '/api/v1/approval/download/list',
        'method': 'GET',
        'summary': '查询下载申请列表',
        'description': '分页查询下载申请列表'
    },
    {
        'path': '/api/v1/approval/download/detail',
        'method': 'GET',
        'summary': '获取申请详情',
        'description': '根据申请单号获取申请详情'
    },
    {
        'path': '/api/v1/approval/permission/check',
        'method': 'POST',
        'summary': '检查审批权限',
        'description': '检查用户是否有指定地市的审批权限'
    },
    {
        'path': '/api/v1/approval/permission/cities',
        'method': 'GET',
        'summary': '获取可审批地市列表',
        'description': '获取用户可审批的地市列表'
    },
    {
        'path': '/api/v1/download/validate',
        'method': 'POST',
        'summary': '验证下载权限',
        'description': '验证用户是否有权下载指定申请'
    },
    {
        'path': '/api/v1/download/record',
        'method': 'POST',
        'summary': '记录下载操作',
        'description': '记录用户的下载操作'
    }
]


if __name__ == '__main__':
    # 测试用例
    service = ApprovalService()
    
    # 测试创建下载申请
    print("=== 创建下载申请测试 ===")
    application = DownloadApplication(
        city_code='610300',
        city_name='宝鸡',
        menu_code='MENU_BJ_006',
        menu_name='慢病申报查询',
        download_type=DownloadType.EXPORT_EXCEL,
        download_purpose='导出数据给医保局',
        download_conditions='时间范围：2026-3-1~2026-3-20; 表头字段：姓名、身份证号、手机号码、疾病类型、疾病名称',
        applicant_id='user001',
        applicant_name='张三',
        applicant_account='zhangsan',
        record_count=100
    )
    
    success, message, app_no = service.create_download_application(application)
    print(f"创建结果: {success}, 消息: {message}, 申请单号: {app_no}")
    
    # 测试审批
    print("\n=== 审批测试 ===")
    if app_no:
        approval_request = ApprovalRequest(
            application_no=app_no,
            approval_result=1,  # 通过
            approval_comment='数据用途合理，同意导出',
            approver_id='approver001',
            approver_name='李审批',
            approver_account='lishenpi'
        )
        
        success, message = service.approve_application(approval_request)
        print(f"审批结果: {success}, 消息: {message}")
    
    # 测试查询
    print("\n=== 查询申请列表测试 ===")
    query = ApprovalQuery(
        city_code='610300',
        page=1,
        page_size=10
    )
    
    result = service.query_applications(query)
    print(f"查询结果: 总数={result['total']}, 页码={result['page']}")
    for app in result['data']:
        print(f"  申请单号: {app['application_no']}, 状态: {app['approval_status']}")
    
    # 测试下载权限验证
    print("\n=== 下载权限验证测试 ===")
    if app_no:
        can_download, msg = service.validate_download(app_no, 'zhangsan')
        print(f"用户zhangsan下载权限: {can_download}, 消息: {msg}")
        
        can_download, msg = service.validate_download(app_no, 'other_user')
        print(f"用户other_user下载权限: {can_download}, 消息: {msg}")
    
    # 测试审批权限检查
    print("\n=== 审批权限检查测试 ===")
    can_approve = service.check_approval_permission('approver001', 'ROLE_ADMIN', '610300')
    print(f"管理员审批宝鸡申请权限: {can_approve}")
    
    cities = service.get_city_permissions('ROLE_ADMIN')
    print(f"管理员可审批地市数量: {len(cities)}")
