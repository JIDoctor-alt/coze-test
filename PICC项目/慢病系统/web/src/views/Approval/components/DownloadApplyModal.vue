<template>
  <a-modal
    v-model:visible="visible"
    title="下载申请"
    width="500px"
    :footer="null"
    @cancel="handleCancel"
  >
    <a-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      layout="vertical"
    >
      <a-form-item label="下载申请人">
        <a-input :value="applicantName" disabled />
      </a-form-item>

      <a-form-item label="下载用途" name="downloadPurpose">
        <a-textarea
          v-model:value="formData.downloadPurpose"
          placeholder="请填写下载用途，说明数据的使用目的"
          :rows="3"
          :maxlength="200"
          showCount
        />
      </a-form-item>

      <a-form-item label="下载范围条件">
        <div class="download-conditions">
          {{ downloadConditions || '自动获取当前查询条件和导出字段' }}
        </div>
      </a-form-item>

      <a-form-item class="modal-footer">
        <a-space>
          <a-button @click="handleCancel">取消</a-button>
          <a-button type="primary" @click="handleSubmit" :loading="loading">
            提交
          </a-button>
        </a-space>
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, computed, watch } from 'vue';
import { message } from 'ant-design-vue';

interface DownloadApplyModalProps {
  visible: boolean;
  applicantName: string;
  menuCode: string;
  menuName: string;
  cityCode: string;
  cityName: string;
  downloadType: string;
  downloadConditions: string;
  queryParams: Record<string, any>;
}

export default defineComponent({
  name: 'DownloadApplyModal',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    applicantName: {
      type: String,
      default: ''
    },
    menuCode: {
      type: String,
      default: ''
    },
    menuName: {
      type: String,
      default: ''
    },
    cityCode: {
      type: String,
      default: ''
    },
    cityName: {
      type: String,
      default: ''
    },
    downloadType: {
      type: String,
      default: 'export_excel'
    },
    downloadConditions: {
      type: String,
      default: ''
    },
    queryParams: {
      type: Object as () => Record<string, any>,
      default: () => ({})
    }
  },
  emits: ['update:visible', 'success', 'cancel'],
  setup(props, { emit }) {
    const loading = ref(false);
    const formRef = ref();

    const formData = reactive({
      downloadPurpose: ''
    });

    const rules = {
      downloadPurpose: [
        { required: true, message: '请填写下载用途', trigger: 'blur' },
        { max: 200, message: '下载用途不能超过200字', trigger: 'blur' }
      ]
    };

    const handleSubmit = async () => {
      try {
        await formRef.value.validate();
        
        if (!formData.downloadPurpose.trim()) {
          message.error('请填写下载用途');
          return;
        }

        loading.value = true;

        // 构造申请数据
        const applicationData = {
          cityCode: props.cityCode,
          cityName: props.cityName,
          menuCode: props.menuCode,
          menuName: props.menuName,
          downloadType: props.downloadType,
          downloadPurpose: formData.downloadPurpose,
          downloadConditions: props.downloadConditions,
          queryParams: JSON.stringify(props.queryParams)
        };

        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 500));

        // 实际项目中调用API
        // const response = await api.submitDownloadApplication(applicationData);

        message.success('下载申请已提交，请等待审批');
        
        formData.downloadPurpose = '';
        emit('update:visible', false);
        emit('success', applicationData);
      } catch (error) {
        console.error('表单验证失败', error);
      } finally {
        loading.value = false;
      }
    };

    const handleCancel = () => {
      formData.downloadPurpose = '';
      emit('update:visible', false);
      emit('cancel');
    };

    // 监听visible变化，重置表单
    watch(() => props.visible, (newVal) => {
      if (!newVal) {
        formData.downloadPurpose = '';
      }
    });

    return {
      loading,
      formRef,
      formData,
      rules,
      handleSubmit,
      handleCancel
    };
  }
});
</script>

<style scoped>
.download-conditions {
  padding: 8px 12px;
  background: #f5f5f5;
  border-radius: 4px;
  font-size: 13px;
  color: #666;
  line-height: 1.6;
}

.modal-footer {
  margin-bottom: 0;
  text-align: right;
}
</style>
