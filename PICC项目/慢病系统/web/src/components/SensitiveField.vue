<template>
  <div class="sensitive-field">
    <span 
      v-if="!isVisible" 
      class="masked-value"
      :class="{ clickable: canView }"
      @click="toggleVisibility"
      :title="canView ? '点击查看' : ''"
    >
      {{ maskedValue }}
    </span>
    <span 
      v-else 
      class="original-value"
      @click="toggleVisibility"
    >
      {{ displayValue }}
    </span>
    <a-icon 
      v-if="canView"
      :type="isVisible ? 'eye-invisible' : 'eye'"
      class="toggle-icon"
      @click="toggleVisibility"
      :title="isVisible ? '点击隐藏' : '点击查看'"
    />
    <a-icon 
      v-else
      type="lock"
      class="lock-icon"
      title="无权查看"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch } from 'vue';
import { Icon } from 'ant-design-vue';

export interface SensitiveFieldProps {
  value: string;
  fieldCode: string;
  fieldType?: 'name' | 'idcard' | 'phone' | 'bankcard' | 'address' | 'email';
  canView?: boolean;
  permissions?: Record<string, boolean>;
}

export default defineComponent({
  name: 'SensitiveField',
  components: {
    'a-icon': Icon
  },
  props: {
    value: {
      type: String,
      default: ''
    },
    fieldCode: {
      type: String,
      required: true
    },
    fieldType: {
      type: String,
      default: 'name'
    },
    canView: {
      type: Boolean,
      default: true
    },
    permissions: {
      type: Object as () => Record<string, boolean>,
      default: () => ({})
    }
  },
  emits: ['view', 'hide'],
  setup(props, { emit }) {
    const isVisible = ref(false);

    // 脱敏规则
    const maskingRules = {
      name: (val: string) => {
        if (!val) return val;
        if (/^[\u4e00-\u9fa5]+$/.test(val)) {
          // 中文姓名
          return val.length >= 2 ? val[0] + '**' : val + '**';
        }
        return val.length >= 2 ? val[0] + '**' : val + '**';
      },
      idcard: (val: string) => {
        if (!val) return val;
        const clean = val.trim().replace(/[Xx]$/, '');
        if (clean.length <= 10) return clean;
        return clean.slice(0, 6) + '********' + clean.slice(-4);
      },
      phone: (val: string) => {
        if (!val) return val;
        const clean = val.replace(/[\s\-]+/g, '');
        if (clean.length < 7) return clean;
        return clean.slice(0, 3) + '****' + clean.slice(-4);
      },
      bankcard: (val: string) => {
        if (!val) return val;
        const clean = val.replace(/\s/g, '');
        if (clean.length <= 10) return clean;
        const maskLen = clean.length - 10;
        return clean.slice(0, 6) + '*'.repeat(maskLen) + clean.slice(-4);
      },
      address: (val: string) => {
        if (!val) return val;
        if (val.length <= 10) return val;
        return val.slice(0, 10) + '*'.repeat(Math.min(6, val.length - 10));
      },
      email: (val: string) => {
        if (!val || !val.includes('@')) return val;
        const [user, domain] = val.split('@');
        const maskedUser = user.length > 6 ? user.slice(0, 6) + '******' : user + '******';
        return maskedUser + '@' + domain;
      }
    };

    const maskedValue = computed(() => {
      if (!props.value) return '';
      const rule = maskingRules[props.fieldType as keyof typeof maskingRules];
      return rule ? rule(props.value) : props.value;
    });

    const displayValue = computed(() => {
      return props.value;
    });

    const hasPermission = computed(() => {
      if (props.permissions && Object.keys(props.permissions).length > 0) {
        return props.permissions[props.fieldCode] === true;
      }
      return props.canView;
    });

    const toggleVisibility = () => {
      if (!hasPermission.value) {
        return;
      }
      
      isVisible.value = !isVisible.value;
      
      if (isVisible.value) {
        emit('view', {
          fieldCode: props.fieldCode,
          value: props.value
        });
      } else {
        emit('hide', {
          fieldCode: props.fieldCode
        });
      }
    };

    // 监听值变化，重置为隐藏状态
    watch(() => props.value, () => {
      isVisible.value = false;
    });

    return {
      isVisible,
      maskedValue,
      displayValue,
      canView: hasPermission,
      toggleVisibility
    };
  }
});
</script>

<style scoped>
.sensitive-field {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.masked-value {
  color: #999;
  font-family: monospace;
}

.masked-value.clickable {
  cursor: pointer;
}

.masked-value.clickable:hover {
  color: #666;
}

.original-value {
  font-family: monospace;
}

.toggle-icon {
  cursor: pointer;
  color: #1890ff;
  font-size: 14px;
}

.toggle-icon:hover {
  color: #40a9ff;
}

.lock-icon {
  color: #ff4d4f;
  font-size: 12px;
}
</style>
