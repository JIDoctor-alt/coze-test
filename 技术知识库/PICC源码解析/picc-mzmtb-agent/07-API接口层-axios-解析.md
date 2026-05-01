# API接口层解析 - axios 配置

> 🎯 一句话说明：axios 是前后端通信的"快递小哥"，负责发送请求和接收响应

---

## 这是啥？（小白版）

想象 **axios 是餐厅的"服务员"**：
- 你点菜（发送请求）
- 服务员去厨房下单（axios 发请求）
- 厨房做好菜（后端处理）
- 服务员端菜回来（axios 返回响应）

---

## 核心代码解析

### axios.js - 主请求封装

```javascript
import Axios from "axios";
import {message} from 'ant-design-vue';
import qs from 'qs';
import store from '../store/index';
import util from '@/utils/util';

let baseURL = '', token = '', userId = '', cityFlag = '';

// 根据环境设置 baseURL
if (process.env.NODE_ENV === 'development') {
    baseURL = '';  // 开发环境为空，通过代理转发
} else {
    baseURL = process.env.domainName;  // 生产环境使用配置的域名
}

class HttpRequest {
    constructor() {
        this.options = { method: "", url: "" };
        this.queue = {};  // 请求队列
    }
    
    // 请求拦截器
    interceptors(instance, url, apiUrl) {
        // 1. 请求前拦截
        instance.interceptors.request.use(
            config => {
                // 1.1 加密敏感字段
                try {
                    config.data = this.encryptRequestFieldsWithAES(config.data, apiUrl);
                } catch (error) {
                    console.warn('AES加密失败:', error);
                }
                
                // 1.2 从 URL 获取 token 和 userId
                let query = location.href.split('?')[1];
                token = qs.parse(query, { ignoreQueryPrefix: true })["token"];
                
                // 1.3 获取用户信息
                if (util.getUserInfo()) {
                    let logInfoMB = util.getUserInfo();
                    userId = logInfoMB.userId;
                    token = logInfoMB.token;
                }
                
                // 1.4 获取城市标志
                cityFlag = qs.parse(query, { ignoreQueryPrefix: true })["flag"];
                
                // 1.5 设置请求头
                config.headers.common['Authorization'] = token;
                config.headers['token'] = token;
                config.headers['tokenFlag'] = sessionStorage.getItem('tokenFlag');
                config.headers['userId'] = userId || null;
                config.headers['flag'] = cityFlag || 0;
                
                return config;
            },
            error => Promise.reject(error)
        );
        
        // 2. 响应拦截器
        instance.interceptors.response.use(
            res => {
                // 2.1 判断响应状态
                let data = url.includes('downloadListPdfZip') ? res : res.data;
                
                // 2.2 处理业务错误
                if (data.status !== '0') {
                    message.error(data.message || '请求失败');
                }
                
                // 2.3 处理 token 失效
                if (data.code === '401' || data.message?.includes('登录')) {
                    message.error('登录已过期，请重新登录');
                    sessionStorage.clear();
                    window.location.href = '/#/loginMb';
                }
                
                return data;
            },
            error => {
                // 3. 处理 HTTP 错误
                if (error.response) {
                    switch (error.response.status) {
                        case 401:
                            message.error('未授权，请重新登录');
                            break;
                        case 403:
                            message.error('拒绝访问');
                            break;
                        case 404:
                            message.error('请求的资源不存在');
                            break;
                        case 500:
                            message.error('服务器错误');
                            break;
                    }
                }
                return Promise.reject(error);
            }
        );
    }
    
    // 创建请求
    request(options) {
        const instance = Axios.create();
        this.interceptors(instance, options.url);
        return instance(options);
    }
}

export default new HttpRequest();
```

---

## API 接口列表

### 登录相关 (apiLoginMb.js)

| 方法名 | 说明 | 用途 |
|--------|------|------|
| `getCaptchaMb` | 获取图形验证码 | 登录时显示验证码图片 |
| `loginByCaptchaMb` | 验证码登录 | 手机验证码方式登录 |
| `loginOutMb` | 登出 | 退出当前登录 |
| `updatePassWordMb` | 修改密码 | 用户主动修改密码 |
| `resetPasswordMb` | 重置密码 | 忘记密码时重置 |
| `sendUserVerifCodeMb` | 发送验证码 | 发送到手机短信验证码 |
| `getCaptchaImgMB` | 获取图形验证码 | 重置密码时使用 |

### 慢病申报相关 (apiDiseaseDeclare.js)

| 方法名 | 说明 | 用途 |
|--------|------|------|
| `queryDeclareList` | 查询申报列表 | 获取申报数据分页列表 |
| `exportDeclare` | 导出申报数据 | Excel 导出功能 |
| `getCityList` | 获取城市列表 | 联动下拉选择 |
| `queryDeclareDetail` | 查询申报详情 | 获取单条申报详细信息 |

### 初审管理相关 (apiAuditManagement.js)

| 方法名 | 说明 | 用途 |
|--------|------|------|
| `queryMbDeclareListInFirstTrail` | 查询初审列表 | 获取待初审的申报 |
| `updateMbDeclareFirstApprovalInfo` | 初审结论提交 | 通过/不通过/需体检 |
| `firstTrailPassAutoMask` | AI自动初审 | 调用智能审核接口 |

### 专家分配相关 (apiMbExpertAssign.js)

| 方法名 | 说明 | 用途 |
|--------|------|------|
| `getExpertAssignList` | 获取待分配列表 | 体检完成待分配专家 |
| `getExpertList` | 获取专家列表 | 查询可用专家 |
| `manualAssignExpert` | 手动分配专家 | 选择专家进行分配 |
| `autoAssignExpert` | 自动分配专家 | 系统自动分配 |
| `recallExpertAssign` | 撤回分配 | 撤销专家分配 |

### 体检分配相关 (apiMbPhysicalAssign.js)

| 方法名 | 说明 | 用途 |
|--------|------|------|
| `getAssignList` | 获取待分配列表 | 待分配体检的申报 |
| `getOrgList` | 获取体检机构列表 | 查询可用机构 |
| `manualAssignOrg` | 手动分配机构 | 选择机构分配 |
| `recallAssign` | 撤回分配 | 撤销体检分配 |
| `getAssignDetail` | 获取分配详情 | 查看分配信息 |

---

## 请求流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                        请求发送流程                              │
└─────────────────────────────────────────────────────────────────┘

组件中调用:
this.$axios.post('/api/declare/query', params)

    ↓
    
axios 拦截器 (请求前)
    ├─ 加密敏感字段
    ├─ 设置 token 请求头
    ├─ 设置 userId 请求头
    └─ 设置 flag 城市标志

    ↓
    
发送 HTTP 请求到后端

    ↓
    
axios 拦截器 (响应后)
    ├─ 解析响应数据
    ├─ 判断 status 状态码
    ├─ 处理 token 失效
    └─ 处理业务错误提示

    ↓
    
返回给组件 .then(res => {...})

    ↓
    
组件更新页面显示
```

---

## 调用示例

### 组件中调用 API

```javascript
import api from "@/api/apiDiseaseDeclare";

export default {
    methods: {
        // 查询申报列表
        queryDeclare() {
            this.loading = true;
            api.queryDeclareList({
                name: this.formObj.name,
                idcard: this.formObj.idcard,
                pageNum: this.pagination.current,
                pageSize: this.pagination.pageSize
            }).then(res => {
                if (res.status === 0) {
                    this.data = res.data.list;
                    this.pagination.total = res.data.total;
                }
            }).finally(() => {
                this.loading = false;
            });
        },
        
        // 提交审核
        submitAudit(params) {
            return api.updateMbDeclareFirstApprovalInfo(params);
        }
    }
}
```

---

## 知识点

### 🔹 请求拦截器
在请求发送前统一处理：
- 添加 token
- 加密敏感数据
- 显示 loading

### 🔹 响应拦截器
在响应返回后统一处理：
- 统一错误提示
- 处理登录失效
- 格式化数据

### 🔹 环境变量
```javascript
process.env.NODE_ENV
// 'development' 开发环境
// 'test' 测试环境
// 'uatMb' 预发布环境
// 'proMb' 生产环境
```

### 🔹 qs.parse
将 URL 查询字符串转换为对象：
```javascript
qs.parse('token=abc&userId=123')
// → { token: 'abc', userId: '123' }
```
