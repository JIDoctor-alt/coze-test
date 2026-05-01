<template>
  <div class="approval-management">
    <!-- 查询条件 -->
    <a-card class="search-card" :bordered="false">
      <a-form layout="inline" :model="queryForm">
        <a-row :gutter="16">
          <a-col :span="6">
            <a-form-item label="地市名称">
              <a-select
                v-model:value="queryForm.cityCode"
                placeholder="请选择地市"
                allowClear
                showSearch
                :filterOption="filterOption"
                @change="handleCityChange"
              >
                <a-select-option v-for="city in cityList" :key="city.code" :value="city.code">
                  {{ city.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="6">
            <a-form-item label="菜单名称">
              <a-select
                v-model:value="queryForm.menuCode"
                placeholder="请先选择地市"
                allowClear
                showSearch
                :filterOption="filterOption"
                :disabled="!queryForm.cityCode"
              >
                <a-select-option v-for="menu in filteredMenuList" :key="menu.code" :value="menu.code">
                  {{ menu.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="6">
            <a-form-item label="下载申请人">
              <a-input
                v-model:value="queryForm.applicantAccount"
                placeholder="请输入申请人账号"
              />
            </a-form-item>
          </a-col>
          <a-col :span="6">
            <a-form-item label="审批人">
              <a-input
                v-model:value="queryForm.approverAccount"
                placeholder="请输入审批人账号"
              />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="6">
            <a-form-item label="申请日期">
              <a-date-picker
                v-model:value="queryForm.startDate"
                placeholder="开始日期"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="6">
            <a-form-item label="至">
              <a-date-picker
                v-model:value="queryForm.endDate"
                placeholder="结束日期"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="6">
            <a-form-item label="审批结果">
              <a-select
                v-model:value="queryForm.approvalStatus"
                placeholder="请选择"
                allowClear
              >
                <a-select-option :value="0">未审核</a-select-option>
                <a-select-option :value="1">审核通过</a-select-option>
                <a-select-option :value="2">审核不通过</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="6">
            <a-form-item>
              <a-space>
                <a-button type="primary" @click="handleQuery">
                  <template #icon><SearchOutlined /></template>
                  查询
                </a-button>
                <a-button @click="handleReset">
                  <template #icon><ReloadOutlined /></template>
                  重置
                </a-button>
              </a-space>
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-card>

    <!-- 申请列表 -->
    <a-card class="table-card" :bordered="false">
      <a-table
        :columns="columns"
        :dataSource="tableData"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        rowKey="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'approvalStatus'">
            <a-tag :color="getStatusColor(record.approvalStatus)">
              {{ getStatusText(record.approvalStatus) }}
            </a-tag>
          </template>
          <template v-if="column.key === 'downloadPurpose'">
            <a-tooltip :title="record.downloadPurpose">
              {{ truncateText(record.downloadPurpose, 10) }}
            </a-tooltip>
          </template>
          <template v-if="column.key === 'action'">
            <a-button
              v-if="record.approvalStatus === 0 && hasApprovalPermission"
              type="link"
              @click="handleApprove(record)"
            >
              审批
            </a-button>
            <a-button
              v-if="record.approvalStatus === 1 && isApplicant(record)"
              type="link"
              @click="handleDownload(record)"
            >
              下载
            </a-button>
            <span v-if="record.approvalStatus === 1 && !isApplicant(record)" class="disabled-btn">
              下载
            </span>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 审批弹窗 -->
    <a-modal
      v-model:visible="approveModalVisible"
      title="审批"
      width="600px"
      :footer="null"
      @cancel="handleCancelApprove"
    >
      <a-descriptions :column="2" bordered size="small">
        <a-descriptions-item label="下载申请人">
          {{ currentRecord?.applicantName }}
        </a-descriptions-item>
        <a-descriptions-item label="申请时间">
          {{ currentRecord?.createdTime }}
        </a-descriptions-item>
        <a-descriptions-item label="下载用途" :span="2">
          {{ currentRecord?.downloadPurpose }}
        </a-descriptions-item>
        <a-descriptions-item label="下载范围条件" :span="2">
          {{ currentRecord?.downloadConditions }}
        </a-descriptions-item>
      </a-descriptions>

      <a-divider>审批</a-divider>

      <a-form
        ref="approveFormRef"
        :model="approveForm"
        :rules="approveRules"
        layout="vertical"
      >
        <a-form-item label="审批结果" name="approvalResult">
          <a-radio-group v-model:value="approveForm.approvalResult">
            <a-radio :value="1">审核通过</a-radio>
            <a-radio :value="2">审核不通过</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item 
          label="审批意见" 
          name="approvalComment"
          :extra="approveForm.approvalResult === 2 ? '审核不通过时必填' : ''"
        >
          <a-textarea
            v-model:value="approveForm.approvalComment"
            placeholder="请输入审批意见"
            :rows="3"
            :maxlength="200"
            showCount
          />
        </a-form-item>
      </a-form>

      <div class="modal-footer">
        <a-space>
          <a-button @click="handleCancelApprove">取消</a-button>
          <a-button type="primary" @click="handleSubmitApprove" :loading="submitLoading">
            提交
          </a-button>
        </a-space>
      </div>
    </a-modal>

    <!-- 下载申请弹窗 -->
    <a-modal
      v-model:visible="applyModalVisible"
      title="下载申请"
      width="600px"
      :footer="null"
      @cancel="handleCancelApply"
    >
      <a-form
        ref="applyFormRef"
        :model="applyForm"
        :rules="applyRules"
        layout="vertical"
      >
        <a-form-item label="下载申请人">
          <a-input :value="currentUser" disabled />
        </a-form-item>
        <a-form-item label="下载用途" name="downloadPurpose">
          <a-textarea
            v-model:value="applyForm.downloadPurpose"
            placeholder="请填写下载用途（200字内）"
            :rows="3"
            :maxlength="200"
            showCount
          />
        </a-form-item>
        <a-form-item label="下载范围条件">
          <a-textarea
            :value="downloadConditions"
            disabled
            :rows="3"
          />
        </a-form-item>
      </a-form>

      <div class="modal-footer">
        <a-space>
          <a-button @click="handleCancelApply">取消</a-button>
          <a-button type="primary" @click="handleSubmitApply" :loading="submitLoading">
            提交
          </a-button>
        </a-space>
      </div>
    </a-modal>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, computed, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import {
  SearchOutlined,
  ReloadOutlined
} from '@ant-design/icons-vue';

interface City {
  code: string;
  name: string;
}

interface Menu {
  code: string;
  name: string;
  cityCode: string;
}

interface Record {
  id: number;
  applicationNo: string;
  cityCode: string;
  cityName: string;
  menuCode: string;
  menuName: string;
  applicantId: string;
  applicantName: string;
  applicantAccount: string;
  createdTime: string;
  downloadPurpose: string;
  downloadConditions: string;
  approvalStatus: number;
  approverName?: string;
  approvalComment?: string;
  approvalTime?: string;
}

export default defineComponent({
  name: 'ApprovalManagement',
  components: {
    SearchOutlined,
    ReloadOutlined
  },
  setup() {
    // 状态
    const loading = ref(false);
    const submitLoading = ref(false);
    const approveModalVisible = ref(false);
    const applyModalVisible = ref(false);
    const currentRecord = ref<Record | null>(null);
    
    // 模拟当前用户
    const currentUser = ref('zhangsan');
    
    // 地市列表
    const cityList = ref<City[]>([
      { code: '610300', name: '宝鸡' },
      { code: '130700', name: '张家口' },
      { code: '139000', name: '定州' },
      { code: '610600', name: '延安' },
      { code: '611000', name: '商洛' },
      { code: '150700', name: '满洲里' },
      { code: '610800', name: '榆林' },
      { code: '610400', name: '杨凌' },
      { code: '360400', name: '九江' },
      { code: '140500', name: '晋城' },
      { code: '610400', name: '咸阳' }
    ]);
    
    // 菜单列表
    const menuList = ref<Menu[]>([
      { code: 'MENU_BJ_006', name: '慢病申报查询', cityCode: '610300' },
      { code: 'MENU_BJ_007', name: '慢病人员导入', cityCode: '610300' },
      { code: 'MENU_DZ_001', name: '综合查询', cityCode: '139000' },
      { code: 'MENU_JC_001', name: '申报综合查询', cityCode: '140500' },
      { code: 'MENU_JJ_001', name: '申报综合查询', cityCode: '360400' },
      { code: 'MENU_YA_001', name: '慢病用户管理', cityCode: '610600' },
      { code: 'MENU_SL_001', name: '人员批量导入', cityCode: '611000' },
      { code: 'MENU_MZL_001', name: '人员批量导入', cityCode: '150700' },
      { code: 'MENU_YL_001', name: '人员批量导入', cityCode: '610800' },
      { code: 'MENU_ZJK_001', name: '慢病申报修改', cityCode: '130700' },
      { code: 'MENU_XY_001', name: '申报综合查询', cityCode: '610400' }
    ]);
    
    // 查询表单
    const queryForm = reactive({
      cityCode: undefined as string | undefined,
      menuCode: undefined as string | undefined,
      applicantAccount: '',
      approverAccount: '',
      startDate: null,
      endDate: null,
      approvalStatus: undefined as number | undefined
    });
    
    // 审批表单
    const approveForm = reactive({
      approvalResult: 1,
      approvalComment: ''
    });
    
    // 申请表单
    const applyForm = reactive({
      downloadPurpose: ''
    });
    
    // 审批表单ref
    const approveFormRef = ref();
    
    // 申请表单ref
    const applyFormRef = ref();
    
    // 分页
    const pagination = reactive({
      current: 1,
      pageSize: 20,
      total: 0,
      showSizeChanger: true,
      showQuickJumper: true,
      showTotal: (total: number) => `共 ${total} 条`
    });
    
    // 表格列定义
    const columns = [
      {
        title: '序号',
        dataIndex: 'id',
        key: 'index',
        width: 60,
        customRender: ({ index }: { index: number }) => {
          return (pagination.current - 1) * pagination.pageSize + index + 1;
        }
      },
      {
        title: '地市名称',
        dataIndex: 'cityName',
        key: 'cityName',
        width: 100
      },
      {
        title: '菜单名称',
        dataIndex: 'menuName',
        key: 'menuName',
        width: 150
      },
      {
        title: '下载申请人',
        dataIndex: 'applicantName',
        key: 'applicantName',
        width: 100
      },
      {
        title: '申请时间',
        dataIndex: 'createdTime',
        key: 'createdTime',
        width: 160
      },
      {
        title: '下载用途',
        dataIndex: 'downloadPurpose',
        key: 'downloadPurpose',
        width: 150
      },
      {
        title: '下载范围条件',
        dataIndex: 'downloadConditions',
        key: 'downloadConditions',
        width: 200,
        ellipsis: true
      },
      {
        title: '审批人',
        dataIndex: 'approverName',
        key: 'approverName',
        width: 100
      },
      {
        title: '审批结果',
        dataIndex: 'approvalStatus',
        key: 'approvalStatus',
        width: 100
      },
      {
        title: '审批意见',
        dataIndex: 'approvalComment',
        key: 'approvalComment',
        width: 150,
        ellipsis: true
      },
      {
        title: '下载时间',
        dataIndex: 'lastDownloadTime',
        key: 'lastDownloadTime',
        width: 160
      },
      {
        title: '操作',
        key: 'action',
        fixed: 'right',
        width: 100
      }
    ];
    
    // 表格数据
    const tableData = ref<Record[]>([]);
    
    // 过滤后的菜单列表
    const filteredMenuList = computed(() => {
      if (!queryForm.cityCode) return [];
      return menuList.value.filter(m => m.cityCode === queryForm.cityCode);
    });
    
    // 是否有审批权限
    const hasApprovalPermission = computed(() => {
      // 实际应根据用户角色和权限判断
      return true;
    });
    
    // 下载范围条件（模拟）
    const downloadConditions = computed(() => {
      return '时间范围：2026-3-1~2026-3-20; 表头字段：姓名、身份证号、手机号码、疾病类型、疾病名称';
    });
    
    // 审批规则
    const approveRules = {
      approvalResult: [
        { required: true, message: '请选择审批结果', trigger: 'change' }
      ],
      approvalComment: [
        { required: true, message: '审核不通过时必须填写审批意见', trigger: 'blur' }
      ]
    };
    
    // 申请规则
    const applyRules = {
      downloadPurpose: [
        { required: true, message: '请填写下载用途', trigger: 'blur' }
      ]
    };
    
    // 方法
    const filterOption = (input: string, option: any) => {
      return option.children[0].children.toLowerCase().indexOf(input.toLowerCase()) >= 0;
    };
    
    const getStatusColor = (status: number) => {
      const colors: Record<number, string> = {
        0: 'orange',
        1: 'green',
        2: 'red'
      };
      return colors[status] || 'default';
    };
    
    const getStatusText = (status: number) => {
      const texts: Record<number, string> = {
        0: '未审核',
        1: '审核通过',
        2: '审核不通过'
      };
      return texts[status] || '未知';
    };
    
    const truncateText = (text: string, length: number) => {
      if (!text) return '';
      return text.length > length ? text.slice(0, length) + '...' : text;
    };
    
    const isApplicant = (record: Record) => {
      return record.applicantAccount === currentUser.value;
    };
    
    const handleCityChange = () => {
      queryForm.menuCode = undefined;
    };
    
    const handleQuery = async () => {
      loading.value = true;
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // 模拟数据
        tableData.value = [
          {
            id: 1,
            applicationNo: 'DA61030020260319123456123',
            cityCode: '610300',
            cityName: '宝鸡',
            menuCode: 'MENU_BJ_006',
            menuName: '慢病申报查询',
            applicantId: 'user001',
            applicantName: '张三',
            applicantAccount: 'zhangsan',
            createdTime: '2026-03-19 10:30:00',
            downloadPurpose: '导出数据给医保局',
            downloadConditions: '时间范围：2026-3-1~2026-3-20; 表头字段：姓名、身份证号、手机号码',
            approvalStatus: 0
          }
        ];
        
        pagination.total = 1;
      } finally {
        loading.value = false;
      }
    };
    
    const handleReset = () => {
      queryForm.cityCode = undefined;
      queryForm.menuCode = undefined;
      queryForm.applicantAccount = '';
      queryForm.approverAccount = '';
      queryForm.startDate = null;
      queryForm.endDate = null;
      queryForm.approvalStatus = undefined;
      handleQuery();
    };
    
    const handleTableChange = (pag: any) => {
      pagination.current = pag.current;
      pagination.pageSize = pag.pageSize;
      handleQuery();
    };
    
    const handleApprove = (record: Record) => {
      currentRecord.value = record;
      approveForm.approvalResult = 1;
      approveForm.approvalComment = '';
      approveModalVisible.value = true;
    };
    
    const handleSubmitApprove = async () => {
      try {
        await approveFormRef.value.validate();
        
        if (approveForm.approvalResult === 2 && !approveForm.approvalComment) {
          message.error('审核不通过时必须填写审批意见');
          return;
        }
        
        submitLoading.value = true;
        
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 500));
        
        message.success(approveForm.approvalResult === 1 ? '已审核通过' : '已审核不通过');
        approveModalVisible.value = false;
        handleQuery();
      } catch (error) {
        console.error('表单验证失败', error);
      } finally {
        submitLoading.value = false;
      }
    };
    
    const handleCancelApprove = () => {
      approveModalVisible.value = false;
    };
    
    const handleDownload = async (record: Record) => {
      // 验证下载权限
      // 实际调用API
      message.success('开始下载文件');
    };
    
    const handleCancelApply = () => {
      applyModalVisible.value = false;
    };
    
    const handleSubmitApply = async () => {
      try {
        await applyFormRef.value.validate();
        
        submitLoading.value = true;
        
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 500));
        
        message.success('下载申请已提交，请等待审批');
        applyModalVisible.value = false;
        handleQuery();
      } catch (error) {
        console.error('表单验证失败', error);
      } finally {
        submitLoading.value = false;
      }
    };
    
    // 暴露方法供外部调用
    const openApplyModal = (downloadInfo?: any) => {
      applyForm.downloadPurpose = '';
      applyModalVisible.value = true;
    };
    
    onMounted(() => {
      handleQuery();
    });
    
    return {
      loading,
      submitLoading,
      approveModalVisible,
      applyModalVisible,
      currentRecord,
      currentUser,
      cityList,
      menuList,
      queryForm,
      approveForm,
      applyForm,
      approveFormRef,
      applyFormRef,
      pagination,
      columns,
      tableData,
      filteredMenuList,
      hasApprovalPermission,
      downloadConditions,
      approveRules,
      applyRules,
      filterOption,
      getStatusColor,
      getStatusText,
      truncateText,
      isApplicant,
      handleCityChange,
      handleQuery,
      handleReset,
      handleTableChange,
      handleApprove,
      handleSubmitApprove,
      handleCancelApprove,
      handleDownload,
      handleCancelApply,
      handleSubmitApply,
      openApplyModal
    };
  }
});
</script>

<style scoped>
.approval-management {
  padding: 16px;
}

.search-card {
  margin-bottom: 16px;
}

.table-card {
  margin-bottom: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
}

.disabled-btn {
  color: #999;
  cursor: not-allowed;
}
</style>
