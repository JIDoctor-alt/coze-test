# 业务模块 - 系统用户管理 (systemUserManage.vue)

> 🎯 一句话说明：这是管理"系统账号"的页面，包括新增、编辑、导入、启用/禁用、删除等操作

---

## 这是啥？（小白版）

想象 **用户管理是公司的"员工花名册"**：
- 花名册 = 用户列表
- 新员工入职 = 新增用户
- 员工转岗 = 编辑角色
- 员工离职 = 删除/禁用账号
- 批量导入 = Excel批量添加

---

## 核心代码解析

### template 部分

```html
<template>
    <div class="main-box">
        <!-- 搜索条件 -->
        <searchCard
            :formObj="formObj"
            @search="search"
            :colSpan="6"
            layout="vertical"
            @resetFields="resetFields"
        />
        
        <!-- 用户列表 -->
        <a-card class="card-top card-table">
            <div slot="title">
                <img src="@/assets/images/person_icon.png">系统账号列表
            </div>
            <div slot="extra">
                <!-- 导入按钮 -->
                <a-upload
                    :showUploadList="false"
                    :custom-request="importUserFn"
                    accept=".xls,.xlsx"
                >
                    <a-button>导入</a-button>
                </a-upload>
                <!-- 其他按钮 -->
                <a-button 
                    v-for="item in optionList" 
                    :key="item.key"
                    @click="tableOption(item.key)"
                >
                    {{ item.name }}
                </a-button>
            </div>
            
            <a-table
                :columns="accountColumns"
                :data-source="accountList"
                :pagination="pagination"
                :loading="tableLoading"
                :rowKey="record => record.id"
            >
                <!-- 账号状态 -->
                <div slot="enable" slot-scope="enable, record">
                    {{ record.enable | filterenable }}
                </div>
                
                <!-- 操作列 -->
                <template slot="option" slot-scope="option, record">
                    <a @click="editFn(record)">编辑</a>
                    <a @click="statusChange(record)">
                        {{ record.enable == 1 ? '禁用' : '启用' }}
                    </a>
                    <a @click="deleteFn(record)">删除</a>
                </template>
            </a-table>
        </a-card>
        
        <!-- 新增/编辑弹窗 -->
        <el-container
            :visible="accountVisible"
            :title="accountTitle"
            width="70%"
            @cancel="accountCancel"
        >
            <a-form-model
                ref="ruleForm"
                :model="form"
                :rules="rules"
                :label-col="labelCol"
                :wrapper-col="wrapperCol"
            >
                <a-row v-for="item in formRowList" :key="item.rowname">
                    <div class="form-title">{{ item.rowname }}</div>
                    <a-col :span="24" :lg="{ span: 12 }" 
                           v-for="field in item.fields" :key="field.key">
                        <a-form-model-item :label="field.label" :prop="field.key">
                            <!-- 文本输入 -->
                            <a-input 
                                v-if="field.type=='input'" 
                                v-model="form[field.key]" 
                            />
                            <!-- 下拉选择 -->
                            <DicSelect
                                v-if="field.type=='select'"
                                :value="form[field.key]"
                                :dicType="field.key"
                                @change="changeSelect"
                            />
                            <!-- 角色多选 -->
                            <DicSelect
                                v-if="field.key=='roleIds'"
                                :value="form[field.key]"
                                mode="multiple"
                                :defaultList="rolesList"
                            />
                            <!-- 机构树选择 -->
                            <partOrgTree
                                v-if="field.type=='tree'"
                                :value="form[field.key]"
                                @change="changeTree"
                            />
                        </a-form-model-item>
                    </a-col>
                </a-row>
            </a-form-model>
            
            <div slot="footer" style="text-align: center;">
                <a-button :loading="accountLoading" @click="accountSubmit" type="primary">
                    提交
                </a-button>
                <a-button @click="accountCancel">取消</a-button>
            </div>
        </el-container>
        
        <!-- 确认弹窗 -->
        <el-container
            :visible="confirmVisible"
            :title="confirmTitle"
            width="420px"
            @cancel="confirmVisible=false"
        >
            <p class="msg-text">{{ confirmText }}</p>
            <p class="msg-text">用户名：{{ account }}</p>
            <p class="msg-text">密码：PICChealth@2020</p>
        </el-container>
    </div>
</template>
```

### script 部分

```javascript
import searchCard from "@/mtbnewcomponents/searchCard/index";
import DicSelect from "@/mtbnewcomponents/comSelect";
import partOrgTree from "@/mtbnewcomponents/selectTree/partOrgTree";
import tableMinxins from "@/utils/tableMixins.js";
import tableCon from "./config/config";
import api from "@/api/apiSystem";
import { checkName, checkAccount, checkStr } from "@/mtbnewcomponents/checkApi";

export default {
    components: {
        searchCard,
        DicSelect,
        partOrgTree
    },
    mixins: [tableMinxins],
    data() {
        return {
            // 搜索条件
            formObj: {
                account: "",
                email: "",
                tel: "",
                name: ""
            },
            
            // 表格
            accountColumns: [],
            accountList: [],
            tableLoading: false,
            
            // 分页
            pagination: {
                current: 1,
                pageSize: 10,
                total: 0
            },
            
            // 弹窗
            accountVisible: false,
            accountTitle: "",
            accountLoading: false,
            confirmVisible: false,
            confirmTitle: "",
            confirmText: "",
            
            // 表单
            form: {},
            rules: {},
            labelCol: { span: 6 },
            wrapperCol: { span: 18 },
            formRowList: [],
            rolesList: [],        // 角色列表
            authsList: [],        // 权限列表
            
            // 编辑时保存的ID
            ids: "",
            
            // 导入loading
            importLoading: false,
            
            // 搜索参数
            searchParam: {}
        }
    },
    created() {
        this.initPage();
    },
    methods: {
        // 1. 加载用户列表
        initPage() {
            this.tableLoading = true;
            let params = {
                ...this.searchParam,
                pageNum: this.pagination.current,
                pageSize: this.pagination.pageSize
            };
            
            api.getUserList(params).then(res => {
                if (res.status === 0) {
                    this.accountList = res.data.list || [];
                    this.pagination.total = res.data.total || 0;
                }
            }).finally(() => {
                this.tableLoading = false;
            });
        },
        
        // 2. 查询
        search(values) {
            this.searchParam = values;
            this.pagination.current = 1;
            this.initPage();
        },
        
        // 3. 表格操作
        tableOption(key) {
            switch (key) {
                case 'add':
                    this.addUser();
                    break;
                case 'export':
                    this.exportUser();
                    break;
            }
        },
        
        // 4. 新增用户
        addUser() {
            this.ids = "";
            this.accountTitle = "新增用户";
            this.form = {};  // 清空表单
            this.accountVisible = true;
        },
        
        // 5. 编辑用户
        editFn(row) {
            this.ids = row.id;
            this.accountTitle = "编辑用户";
            
            // 填充表单数据
            api.getUserDetail({ id: row.id }).then(res => {
                if (res.status === 0) {
                    this.form = res.data;
                    this.accountVisible = true;
                }
            });
        },
        
        // 6. 启用/禁用
        statusChange(row) {
            const status = row.enable == 1 ? '禁用' : '启用';
            this.confirmVisible = true;
            this.confirmTitle = "确认框";
            this.confirmText = `确定${status}此用户吗？`;
            this.account = row.account;
            this.ids = row.id;
        },
        
        // 7. 删除用户
        deleteFn(row) {
            this.$confirm({
                title: '确认删除',
                content: '确定删除此用户吗？',
                onOk() {
                    api.deleteUser({ id: row.id }).then(res => {
                        if (res.status === 0) {
                            this.$message.success('删除成功');
                            this.initPage();
                        }
                    });
                }
            });
        },
        
        // 8. 提交表单
        accountSubmit() {
            this.$refs.ruleForm.validate(valid => {
                if (valid) {
                    this.accountLoading = true;
                    
                    let params = { ...this.form };
                    if (this.ids) {
                        params.id = this.ids;
                        // 编辑
                        api.updateUser(params).then(res => {
                            if (res.status === 0) {
                                this.$message.success('修改成功');
                                this.accountVisible = false;
                                this.initPage();
                            }
                        });
                    } else {
                        // 新增
                        api.addUser(params).then(res => {
                            if (res.status === 0) {
                                this.$message.success('新增成功');
                                this.accountVisible = false;
                                this.initPage();
                            }
                        });
                    }
                }
            }).finally(() => {
                this.accountLoading = false;
            });
        },
        
        // 9. 取消弹窗
        accountCancel() {
            this.accountVisible = false;
            this.$refs.ruleForm.resetFields();
        },
        
        // 10. 导入用户
        importUserFn(param) {
            this.importLoading = true;
            const formData = new FormData();
            formData.append('file', param.file);
            
            api.importUser(formData).then(res => {
                if (res.status === 0) {
                    this.$message.success('导入成功');
                    this.initPage();
                }
            }).finally(() => {
                this.importLoading = false;
            });
        }
    }
}
```

---

## 用户数据结构

```javascript
{
    id: "用户ID",
    account: "zhangsan",           // 账号
    name: "张三",                  // 姓名
    email: "zhangsan@picc.com",   // 邮箱
    tel: "13800000000",           // 手机号
    enable: 1,                    // 1启用 0禁用
    roles: [
        { id: "1", name: "初审员" },
        { id: "2", name: "专家" }
    ],
    orgId: "机构ID",
    orgName: "宝鸡市医保局",
    createTime: "2024-01-01",
    updateTime: "2024-01-15"
}
```

---

## 导入模板说明

导入 Excel 文件应包含以下列：
| 列名 | 说明 | 示例 |
|------|------|------|
| account | 账号 * | zhangsan |
| name | 姓名 * | 张三 |
| email | 邮箱 * | xxx@xxx.com |
| tel | 手机号 * | 13800000000 |
| roleIds | 角色ID(逗号分隔) | 1,2 |
| orgId | 机构ID | 1001 |

---

## 知识点

### 🔹 表单验证规则
```javascript
rules: {
    account: [
        { required: true, message: '请输入账号' },
        { validator: validateAccount, trigger: 'blur' }
    ],
    name: [
        { required: true, message: '请输入姓名' },
        { validator: validateName, trigger: 'blur' }
    ]
}
```

### 🔹 多选角色
```javascript
<DicSelect
    mode="multiple"           // 多选模式
    :value="form.roleIds"    // 逗号分隔的ID字符串
/>
```
