# PICC门诊慢特病前端项目组件封装与复用指南

> 项目信息：`picc-mzmtb-agent`
> 技术栈：Vue 2.6 + Vuex 3 + Ant Design Vue + Webpack
> 组件规模：652个Vue文件
> 编写目的：为开发者提供组件复用与封装的最佳实践指导

---

## 📖 目录导航

1. [Part 1：通用组件清单与解析](#part-1通用组件清单与解析)
2. [Part 2：Mixins解析](#part-2mixins解析)
3. [Part 3：高阶封装模式](#part-3高阶封装模式)
4. [Part 4：组件设计模式总结](#part-4组件设计模式总结)
5. [Part 5：新组件开发指南](#part-5新组件开发指南)

---

# Part 1：通用组件清单与解析

## 1.1 组件目录结构

```
src/
├── components/              # 通用业务组件（核心复用组件）
│   ├── myTable/             # 通用表格封装
│   ├── searchCard/           # 搜索表单封装
│   ├── comSelect/            # 下拉选择器封装
│   ├── Modal/                # 弹窗组件集合
│   ├── modalTable/            # 弹窗表格
│   ├── comAlert/             # 提示组件
│   ├── textArea/             # 文本域组件
│   ├── Watermark/            # 水印组件
│   ├── comPrintTable/        # 打印表格组件
│   ├── comAddressSelect/      # 地址选择组件
│   └── ...
├── mtbnewcomponents/          # 新版通用组件
├── mtbcomponents/            # 慢特病业务组件
├── mtbslcomponents/           # 商洛地市组件
└── pages/                    # 业务页面
```

---

## 1.2 通用组件详解

### 📦 1.2.1 myTable 通用表格组件

**组件路径**：`/src/components/myTable/index.vue`

**一句话解释**：封装了分页、选择、筛选等常用功能的表格组件，让表格展示变得像搭积木一样简单。

**小白理解**：就像一个预装好的表格套餐，打开就能用，还自带分页和选择功能。

```vue
<!-- 引入方式 -->
import MyTable from "@/components/myTable";

<!-- 基础使用 -->
<my-table
  :tableTitle="'申报列表'"
  :columns="columns"
  :data="tableData"
  :isPage="true"
  :isSelect="true"
  :loading="loading"
  @tableChange="handleTableChange"
  @selected="handleSelected"
/>
```

#### Props参数表

| 参数名 | 类型 | 必填 | 默认值 | 人话解释 |
|--------|------|------|--------|----------|
| tableTitle | String | 否 | "" | 表格顶部的标题文字 |
| data | Array | 是 | [] | 表格要展示的数据数组 |
| columns | Array | 是 | [] | 表格列的配置（表头） |
| tableSize | String | 否 | "small" | 表格大小，可选small/default |
| typeObj | Array | 否 | [] | 需要转换类型的字段列表 |
| timeObj | Array | 否 | [] | 需要格式化时间的字段 |
| moneyObj | Array | 否 | [] | 需要格式化金额的字段 |
| cardNoObj | Array | 否 | [] | 需要脱敏的卡号字段 |
| isSelect | Boolean | 否 | false | 是否显示选择框 |
| selection | Object | 否 | {} | 选择框配置（单选/多选） |
| isPage | Boolean | 否 | false | 是否显示分页器 |
| loading | Boolean | 否 | false | 是否显示加载中状态 |
| isExtra | Boolean | 否 | false | 是否显示extra插槽 |
| isFooter | Boolean | 否 | false | 是否显示底部插槽 |

#### Events事件表

| 事件名 | 参数 | 说明 |
|--------|------|------|
| tableChange | (flag, selectedRows) | 选择项变化时触发 |
| selected | [record] | 行双击时触发，返回选中的行数据 |

#### Slots插槽表

| 插槽名 | 说明 |
|--------|------|
| extra | 表格右上角的额外内容（通常放按钮） |
| actions | 表格底部的操作按钮区 |

#### 使用示例

```vue
<template>
  <my-table
    :tableTitle="'慢病申报列表'"
    :columns="columns"
    :data="dataSource"
    :isPage="true"
    :isSelect="true"
    :loading="loading"
    @selected="handleRowClick"
  >
    <!-- 右上角按钮 -->
    <template v-slot:extra>
      <a-button type="primary" @click="handleAdd">新增</a-button>
    </template>
  </my-table>
</template>

<script>
export default {
  data() {
    return {
      columns: [
        { title: '姓名', dataIndex: 'name', width: 100 },
        { title: '证件号', dataIndex: 'idcard', width: 180 },
        { title: '状态', dataIndex: 'status', scopedSlots: { customRender: 'status' } }
      ],
      dataSource: [],
      loading: false
    }
  },
  methods: {
    handleRowClick(record) {
      console.log('双击了', record);
    }
  }
}
</script>
```

#### 小白易懵点

1. **数据字段不显示**：检查columns中的dataIndex是否与data中的字段名完全匹配
2. **选择框不生效**：必须设置`:isSelect="true"`才生效
3. **分页不工作**：必须设置`:isPage="true"`并且后端接口支持分页参数
4. **时间格式化无效**：需要在timeObj数组中添加字段名

---

### 📦 1.2.2 searchCard 搜索表单组件

**组件路径**：`/src/components/searchCard/index.vue`

**一句话解释**：封装了常见搜索场景的表单组件，支持输入框、下拉、日期选择等多种控件。

**小白理解**：就像一个万能搜索神器，想要什么搜索条件就加什么字段。

```vue
<searchCard
  :formObj="formObj"
  :fieldList="searchFields"
  :colSpan="6"
  :gutter="30"
  @search="handleSearch"
  @resetFields="handleReset"
/>
```

#### Props参数表

| 参数名 | 类型 | 必填 | 默认值 | 人话解释 |
|--------|------|------|--------|----------|
| formObj | Object | 是 | {} | 表单的初始值对象 |
| fieldList | Array | 是 | [] | 搜索字段配置数组 |
| colSpan | Number | 否 | 6 | 每行放几个搜索项 |
| gutter | Number | 否 | 24 | 搜索项之间的间距 |
| labelAlign | String | 否 | "right" | 标签对齐方式 |
| cardSize | String | 否 | "small" | 卡片大小 |
| formLayout | String | 否 | "horizontal" | 表单布局方式 |

#### fieldList字段配置详解

```javascript
fieldList: [
  {
    key: 'name',           // 字段名（与formObj对应）
    label: '姓名',         // 显示的标签
    type: 'input',         // 控件类型
    require: false,         // 是否必填
    placeholder: '请输入姓名',
    colSpan: 6             // 占用列数
  },
  {
    key: 'declareType',
    label: '申报方式',
    type: 'select',        // 下拉选择
    dicType: 'declareType' // 数据字典类型
  },
  {
    key: 'declareTime',
    label: '申报时间',
    type: 'date-picker',  // 日期选择
    showTime: false
  },
  {
    key: 'status',
    label: '状态',
    type: 'radio'         // 单选按钮组
  }
]
```

#### 支持的控件类型 (type)

| type值 | 控件类型 | 说明 |
|--------|----------|------|
| input | 单行输入框 | 普通文本输入 |
| input-long | 长输入框 | 宽度100%的输入框 |
| select | 下拉选择 | 需要配合dicType使用 |
| date-picker | 日期选择 | 单个日期 |
| date-picker-array | 日期范围 | 起止日期范围 |
| date-picker-time | 日期时间 | 带时分秒 |
| radio | 单选按钮组 | 用于少量选项 |
| checkbox | 多选框 | 用于开关类选项 |
| treeSelect | 树形选择 | 机构树等层级数据 |

#### Events事件表

| 事件名 | 参数 | 说明 |
|--------|------|------|
| search | {...formObj} | 点击搜索按钮，返回所有字段值 |
| resetFields | {fieldsValue} | 点击重置按钮 |
| changeDate | (key, val) | 日期选择变化时触发 |

#### 使用示例

```javascript
// 在页面中使用
export default {
  data() {
    return {
      formObj: {
        name: '',
        idcard: '',
        declareType: undefined,
        declareBeginFrom: null,
        declareBeginTo: null,
        status: ''
      },
      searchFields: [
        { key: 'name', label: '姓名', type: 'input', colSpan: 6 },
        { key: 'idcard', label: '证件号', type: 'input', colSpan: 6 },
        { 
          key: 'declareType', 
          label: '申报方式', 
          type: 'select', 
          dicType: 'declareType',
          colSpan: 6 
        },
        { 
          key: 'declareBeginFrom', 
          label: '申报时间', 
          type: 'date-picker-array',
          colSpan: 10 
        },
        { key: 'status', label: '状态', type: 'radio', colSpan: 6 }
      ]
    }
  },
  methods: {
    handleSearch(formData) {
      // formData 包含所有搜索字段的值
      this.pagination.current = 1;
      this.fetchData(formData);
    },
    handleReset() {
      // 重置后的处理
    }
  }
}
```

#### 小白易懵点

1. **搜索按钮不触发**：确保`fieldList`中的`key`与`formObj`中的字段名一致
2. **日期范围不生效**：使用`date-picker-array`类型，并确保formObj中有对应的两个字段
3. **下拉数据不显示**：需要通过`dicType`指定数据字典类型，或者通过其他方式传入数据源

---

### 📦 1.2.3 comSelect 下拉选择器组件

**组件路径**：`/src/components/comSelect/comSelect.vue`

**一句话解释**：封装了数据字典联动的下拉选择器，根据dicType自动加载并展示选项。

**小白理解**：就像一个会自动查询数据的下拉框，告诉它类型就能显示对应选项。

```vue
<com-select
  v-model="selectedValue"
  dicType="declareStatus"
  placeholder="请选择状态"
  @change="handleChange"
/>
```

#### Props参数表

| 参数名 | 类型 | 必填 | 默认值 | 人话解释 |
|--------|------|------|--------|----------|
| value/v-model | String/Number/Array | 是 | - | 选中的值 |
| dicType | String | 是 | "" | 数据字典类型 |
| placeholder | String | 否 | "请选择" | 未选中时的提示 |
| disabled | Boolean | 否 | false | 是否禁用 |
| allowClear | Boolean | 否 | false | 是否显示清除按钮 |
| showSearch | Boolean | 否 | true | 是否可搜索过滤 |
| labelInValue | Boolean | 否 | false | 返回完整对象还是只返回值 |
| mode | String | 否 | "default" | 多选模式：multiple/tags |
| maxTag | Number | 否 | - | 最多显示多少个标签 |

#### 支持的dicType类型

| dicType值 | 说明 | 示例 |
|-----------|------|------|
| declareStatus | 申报状态 | 待提交、审核中、已通过、已驳回 |
| declareType | 申报方式 | 线上申报、线下申报 |
| serviceStatus | 服务状态 | 启动、停止 |
| personType | 人员身份 | 职工、居民 |
| icdKind | 疾病类型 | 高血压、糖尿病等 |
| accountStatus | 账户状态 | 激活、冻结 |

#### Events事件表

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | (value) | 选中值变化时触发 |
| select | (value, option) | 选中某一项时触发 |
| focus | - | 获取焦点时触发 |

#### 使用示例

```vue
<template>
  <div>
    <!-- 基础用法 -->
    <com-select
      v-model="form.declareType"
      dicType="declareType"
      placeholder="请选择申报方式"
    />
    
    <!-- 多选模式 -->
    <com-select
      v-model="form.diseases"
      dicType="icdKind"
      mode="multiple"
      placeholder="请选择疾病类型"
    />
    
    <!-- 自定义样式 -->
    <com-select
      v-model="form.status"
      dicType="declareStatus"
      :styles="{ width: '200px' }"
    />
  </div>
</template>

<script>
export default {
  data() {
    return {
      form: {
        declareType: undefined,
        diseases: [],
        status: '1'
      }
    }
  }
}
</script>
```

#### 小白易懵点

1. **选项不显示**：确保dicType在组件的keyObj中有定义
2. **值类型不匹配**：后端返回的值类型可能与组件期望的不一致，需要转换
3. **多选时清空无效**：确保v-model绑定的是数组类型

---

### 📦 1.2.4 DragModal 拖拽弹窗组件

**组件路径**：`/src/mtbnewcomponents/Modal/dragModal.vue`

**一句话解释**：可自由拖动、缩放、全屏的增强型弹窗组件。

**小白理解**：就像一个可以拖来拖去、放大缩小的对话框，用起来更灵活。

```vue
<a-drag-modal
  :visible.sync="visible"
  title="申报详情"
  width="70%"
  :footer="true"
  @ok="handleOk"
  @cancel="handleCancel"
>
  <!-- 弹窗内容 -->
  <div>这里是弹窗里的内容</div>
</a-drag-modal>
```

#### Props参数表

| 参数名 | 类型 | 必填 | 默认值 | 人话解释 |
|--------|------|------|--------|----------|
| visible | Boolean | 是 | false | 是否显示弹窗 |
| title | String | 否 | - | 弹窗标题 |
| width | String/Number | 否 | "70%" | 弹窗宽度 |
| footer | Boolean | 否 | true | 是否显示底部按钮 |
| closable | Boolean | 否 | true | 是否显示关闭按钮 |
| loading | Boolean | 否 | false | 确认按钮加载状态 |
| dragstate | Boolean | 否 | true | 是否可拖动 |
| zoomstate | Boolean | 否 | false | 是否显示全屏按钮 |
| confirmText | String | 否 | "" | 确认提示文字 |
| cancelText | String/Boolean | 否 | "取消" | 取消按钮文字，false隐藏 |
| okText | String | 否 | "确认" | 确认按钮文字 |
| selfModalBody | Object | 否 | {} | 自定义body样式 |

#### Events事件表

| 事件名 | 参数 | 说明 |
|--------|------|------|
| ok | - | 点击确认按钮 |
| cancel | - | 点击取消/关闭 |
| update:visible | (val) | 关闭时触发，用于.sync修饰符 |

#### Slots插槽表

| 插槽名 | 说明 |
|--------|------|
| default | 弹窗主体内容 |
| title | 自定义标题区域 |
| footer | 自定义底部区域 |

#### 使用示例

```vue
<template>
  <a-drag-modal
    :visible.sync="modalVisible"
    title="申报详情"
    width="80%"
    :footer="true"
    okText="保存"
    cancelText="返回"
    :selfModalBody="{ padding: '20px' }"
    @ok="handleSave"
    @cancel="modalVisible = false"
  >
    <a-form :form="form">
      <a-form-item label="姓名">
        <a-input v-model="form.name" />
      </a-form-item>
    </a-form>
    
    <!-- 自定义底部 -->
    <template v-slot:footer>
      <a-button @click="modalVisible = false">自定义取消</a-button>
      <a-button type="primary" @click="handleSave">自定义保存</a-button>
    </template>
  </a-drag-modal>
</template>

<script>
export default {
  data() {
    return {
      modalVisible: false,
      form: { name: '' }
    }
  },
  methods: {
    handleSave() {
      // 保存逻辑
      this.modalVisible = false;
    }
  }
}
</script>
```

#### 小白易懵点

1. **弹窗不显示**：检查visible是否为true，以及.sync修饰符是否正确使用
2. **拖动失效**：确保dragstate为true，且弹窗内容正确渲染
3. **底部按钮不显示**：检查footer是否为true，或是否使用了footer插槽覆盖

---

### 📦 1.2.5 Watermark 水印组件

**组件路径**：`/src/components/Watermark/Watermark.vue`

**一句话解释**：为页面添加防伪水印，保护信息安全。

**小白理解**：就像给文件加水印印章，防止别人盗用。

```vue
<watermark text="张三 2024-01-01">
  <div class="content">
    <!-- 需要水印保护的内容 -->
  </div>
</watermark>
```

#### Props参数表

| 参数名 | 类型 | 必填 | 默认值 | 人话解释 |
|--------|------|------|--------|----------|
| text | String | 是 | '' | 水印文字 |
| fontSize | Number | 否 | 16 | 字体大小 |
| gap | Number | 否 | 20 | 水印间距 |

#### 使用示例

```vue
<watermark text="审核员：李四 | 2024-01-15">
  <div class="main-content">
    <p>重要申报资料</p>
  </div>
</watermark>
```

---

### 📦 1.2.6 textArea 文本域组件

**组件路径**：`/src/components/textArea/textArea.vue`

**一句话解释**：带字数统计的文本输入框。

**小白理解**：就像一个会计数的文本框，写了多少字一目了然。

#### Props参数表

| 参数名 | 类型 | 必填 | 默认值 | 人话解释 |
|--------|------|------|--------|----------|
| value/v-model | String | 是 | - | 输入的文字 |
| placeholder | String | 否 | "" | 占位提示文字 |
| disabled | Boolean | 否 | false | 是否禁用 |
| autoSize | Object | 否 | {minRows:3, maxRows:5} | 自动高度 |
| maxLength | Number | 否 | 200 | 最大字符数 |

#### Events事件表

| 事件名 | 参数 | 说明 |
|--------|------|------|
| keyup | Event | 键盘事件 |

#### 使用示例

```vue
<text-area
  v-model="remark"
  placeholder="请输入备注信息"
  :autoSize="{ minRows: 3, maxRows: 6 }"
/>
```

---

### 📦 1.2.7 comAlert 提示组件

**组件路径**：`/src/components/comAlert/comAlert.vue`

**一句话解释**：简单的确认提示弹窗。

**小白理解**：就像一个"确定要删除吗？"的二次确认框。

#### Props参数表

| 参数名 | 类型 | 必填 | 默认值 | 人话解释 |
|--------|------|------|--------|----------|
| visible | Boolean | 是 | false | 是否显示 |
| message | String | 是 | "" | 提示消息 |
| hideModal | Function | 否 | - | 关闭回调 |

#### 使用示例

```vue
<com-alert
  :visible="alertVisible"
  message="确定要删除这条记录吗？"
  @hideModal="alertVisible = false"
/>
```

---

### 📦 1.2.8 modalTable 弹窗表格组件

**组件路径**：`/src/components/modalTable/index.vue`

**一句话解释**：在弹窗中展示可选择的表格数据。

**小白理解**：就像弹出一个选择器，只不过选项是一个表格。

#### Props参数表

| 参数名 | 类型 | 必填 | 默认值 | 人话解释 |
|--------|------|------|--------|----------|
| visible | Boolean | 是 | false | 是否显示 |
| title | String | 否 | "" | 弹窗标题 |
| cardTitle | String | 否 | "" | 卡片标题 |
| orgList | Array | 否 | [] | 表格数据 |
| type | String | 否 | "" | 表格类型标识 |
| ids | String | 否 | "" | 选中的ID |

#### Events事件表

| 事件名 | 参数 | 说明 |
|--------|------|------|
| close | - | 关闭弹窗 |
| confirm | {selectedRows} | 确认选择 |

---

# Part 2：Mixins解析

## 2.1 Mixin概述

**Mixin = 菜谱，照着做就有一道菜**

Mixin是Vue中复用代码的一种方式，它允许你把一组可复用的选项（data、methods、computed、生命周期钩子等）抽离出来，让多个组件"继承"这些功能。

**项目中主要Mixin文件**：

| 文件路径 | 功能描述 |
|----------|----------|
| `/src/utils/tableMixins.js` | 表格配置混入（核心Mixin） |
| `/src/pages/Declare/mixins.js` | 申报公用方法 |

---

## 2.2 tableMixins.js 深度解析

**文件路径**：`/src/utils/tableMixins.js`

**功能**：为表格类页面提供统一的数据结构、方法、过滤器等。

### 2.2.1 data注入项

```javascript
data() {
  return {
    // 弹窗body样式
    selfModalBody: {
      overflow: "auto",
      height: "450px",
    },
    
    // 加载状态
    finishLoading: false,
    
    // 表格尺寸
    size: "small",
    
    // 选中行数据
    selectedRows: null,
    
    // 行选择配置
    rowSelection: {
      type: "radio",  // radio单选 / checkbox多选
      selectedRowKeys: [],
      onChange: (selectedRowKeys, selectedRows) => {
        this.selectedRows = [...selectedRows];
        this.rowSelection.selectedRowKeys = selectedRowKeys;
      }
    },
    
    // 分页配置
    pagination: {
      pageSize: 10,
      current: 1,
      total: 0,
      showTotal: total => `共 ${total} 条数据`,
      showSizeChanger: true,
      pageSizeOptions: ["10", "20", "35", "50"],
      onShowSizeChange: (current, pageSize) => this.onPageSizeChange(current, pageSize),
      onChange: (page, pageSize) => this.onPageChange(page, pageSize)
    },
    
    // 环境变量
    domainName: process.env.domainName,
    picUrl: process.env.picUrl,
    
    // 其他业务状态
    declareSpinning: false,
    isadultAge: true,
    filedMsg: ["name", "mobile", "idcard"]
  }
}
```

### 2.2.2 filters过滤器注入

tableMixins提供了大量的过滤器方法：

| 过滤器名称 | 作用 | 示例 |
|------------|------|------|
| filterDeclareStatus | 申报状态转换 | 待提交→审核中→已通过 |
| filterServeStatus | 服务状态 | 启动/停止 |
| filterSex | 性别转换 | 1→男, 2→女 |
| filterIdtype | 证件类型 | 身份证/护照等 |
| filterMobile | 手机号格式化 | 显示"无"或脱敏 |
| filterCardNo | 卡号脱敏 | 显示后四位 |
| filterMoney | 金额格式化 | 添加千分位 |
| filterDate | 日期格式化 | YYYY-MM-DD |
| filterPassstatus | 年审状态 | 通过/待审 |
| filterIcdkind | 疾病类型 | 高血压/糖尿病等 |

### 2.2.3 使用Mixin的组件列表

以下页面组件使用了tableMixins：

```javascript
// 在组件中使用
import tableMixins from "@/utils/tableMixins";

export default {
  mixins: [tableMixins],  // 混入表格mixin
  data() {
    return {
      // 只需要定义业务相关的数据
      formObj: {},
      columns: []
    }
  }
}
```

**典型使用场景**：

```javascript
// pages/DZChronicDis/diseaseRecheck.vue
import tableMixins from "@/utils/tableMixins";

export default {
  mixins: [tableMixins],
  data() {
    return {
      // 表格列配置
      columns: [...],
      
      // 过滤器字段
      filedObj: ["service_status", "person_type", "sex"],
      timeObj: ["review_date"],
      
      // 分页参数（会与mixin的pagination合并）
      pagination: {
        ...this.pagination,
        current: 1,
        pageSize: 10
      }
    }
  }
}
```

### 2.2.4 生命周期钩子

tableMixins使用的前置路由守卫：

```javascript
beforeRouteUpdate(to, from, next) {
  // 在路由参数变化但组件复用时调用
  // 可用于监听筛选条件变化
}
```

### 2.2.5 小白易懵点

1. **分页不生效**：分页配置在mixin中定义，页面中只需传入`this.pagination`
2. **过滤器不工作**：需要在组件中使用`| filterXxx`语法
3. **selectedRows为空**：确保表格配置了`row-selection`

---

# Part 3：高阶封装模式

## 3.1 API模块封装

### 3.1.1 API文件组织方式

项目采用**按业务域分离**的API组织方式：

```
src/api/
├── axios.js              # 慢病业务请求实例（核心）
├── axiosCenter.js        # 通用中心请求实例
├── axiosjkgl.js          # 健康管理请求实例
├── axiosPower.js          # 权限系统请求实例
├── axiosAuther.js        # 鉴权请求实例
├── apiLogin.js           # 登录相关
├── apiLoginMb.js         # 移动端登录
├── apiChronicDis.js      # 慢病管理
├── apiDeclare.js         # 申报管理
├── apiDiseaseDeclare.js  # 疾病申报
├── apiUserManage.js      # 用户管理
├── apiAuditManagement.js # 审核管理
├── apiSystem.js          # 系统管理
└── ... (70+个API文件)
```

### 3.1.2 Axios实例封装详解

项目有4个不同的Axios实例，服务于不同业务域：

#### axios.js - 慢病业务核心实例

```javascript
// 特点：
// 1. 统一的请求拦截（Token、用户信息）
// 2. AES字段加密（name/idcard/mobile）
// 3. 统一的错误处理
// 4. 响应数据解密

import axios from './axios'

// 使用示例
export const queryDeclareList = param => {
  return axios.request({
    url: `/vipMbDeclareList/queryList`,
    data: param,
    method: 'post'
  })
}
```

#### axiosCenter.js - 通用中心实例

```javascript
// 特点：
// 1. 用于接入通用中心的功能
// 2. 签名鉴权机制
// 3. 环境区分（测试/UAT/生产）
```

#### axiosPower.js - 权限系统实例

```javascript
// 特点：
// 1. 连接权限管理系统
// 2. 独立的token验证
```

### 3.1.3 请求参数加密机制

axios.js中实现了AES字段级加密：

```javascript
// 需要加密的敏感字段
const sensitiveFields = ['name', 'idcard', 'mobile']

// 加密逻辑
encryptRequestFieldsWithAES(data, apiUrl) {
  // 1. 检查接口是否在白名单中
  // 2. 对敏感字段进行AES加密
  // 3. 返回加密后的数据
}

// 响应解密逻辑
decryptSpecificFieldsWithAES(data) {
  // 对响应中的敏感字段进行解密
}
```

### 3.1.4 API封装规范

```javascript
// api/apiDeclare.js
import axios from './axios'

// 单个导出
export const queryList = param => {
  return axios.request({
    url: `/vipMbDeclareForPart/query`,
    data: param,
    method: 'post'
  })
}

// 批量导出
export const getVipMbdeclareFileTypesByDeclareid = param => {
  return axios.request({
    url: `/vipMbDeclareForPart/getVipMbdeclareFileTypesByDeclareid`,
    data: param,
    method: 'post'
  })
}

// 默认导出整个模块
export default {
  queryList,
  getVipMbdeclareFileTypesByDeclareid
}
```

---

## 3.2 路由守卫封装

### 3.2.1 路由配置结构

```javascript
// src/router/index.js
export const staticRoutes = [
  {
    path: "/",
    name: "_index",
    redirect: "/loginMb"
  },
  {
    path: "/home",
    name: "home",
    component: () => import("@/pages/Home"),
    children: [...childrenRoutes]
  },
  {
    path: "/loginMb",
    name: "loginMb",
    component: () => import("@/components/loginMb/index")
  }
]
```

### 3.2.2 全局路由守卫

```javascript
// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 1. 修改页面标题
  if (to.meta.title) {
    document.title = to.meta.title;
  }
  
  // 2. 权限验证
  let logInfoMB = util.getUserInfo();
  if (!logInfoMB) {
    if (to.path == '/loginMb' || to.path == '/resetConfirm') {
      next();
    } else {
      next('/loginMb');
    }
    return;
  }
  
  // 3. 登录后跳转
  next();
})

// 全局后置守卫
router.afterEach((to, from, next) => {
  // 滚动到顶部
  window.scrollTo(0, 0);
})
```

### 3.2.3 路由meta配置

```javascript
{
  path: "/diseaseFirstTrial",
  name: "diseaseFirstTrial",
  meta: {
    title: "慢病初审管理",
    pathName: "/diseaseFirstTrial"
  },
  component: () => import("@/pages/ChronicDis/diseaseFirstTrial")
}
```

---

## 3.3 指令封装

### 3.3.1 v-move 拖拽指令

**文件路径**：`/src/mtbnewcomponents/Modal/move.js`

**功能**：让Modal弹窗可以自由拖动和缩放。

```javascript
// 定义指令
const move = Vue.directive('move', {
  inserted: (el, bindings, vnode) => {
    // 1. 获取弹窗元素
    // 2. 添加拖动事件监听
    // 3. 实现缩放功能
    // 4. 实现全屏切换
  }
})

// 使用方式
<template>
  <div v-move>
    <a-modal ...>弹窗内容</a-modal>
  </div>
</template>
```

**指令功能**：
- 🖱️ 拖动弹窗位置
- ↔️ 边缘拖动缩放
- 🔲 双击头部全屏
- 📐 最小尺寸限制

---

## 3.4 Vuex状态管理封装

### 3.4.1 Store结构

```javascript
// src/store/index.js
const store = new Vuex.Store({
  modules: {
    menu,              // 菜单模块
    activeRouterMatch  // 路由匹配模块
  },
  state: {
    tabList: [],       // 标签页列表
    collapsed: false,  // 菜单折叠状态
    menuData: []       // 菜单数据
  },
  mutations: {
    updateTabList,
    updateCollapsed,
    updateMenu
  },
  plugins: [createPersisted]  // 数据持久化
})
```

### 3.4.2 菜单模块

```javascript
// src/store/modules/menu.js
export default {
  state: {
    menuCollapsed: true,
    userInfo: {},
    permissions: {},
    menu: []
  },
  mutations: {
    toggleMenu(state) {
      state.menuCollapsed = !state.menuCollapsed;
    },
    updateUserInfo(state, data) {
      state.userInfo = data;
    }
  },
  getters: {
    menuCollapsed: state => state.menuCollapsed,
    permissions: state => state.permissions
  }
}
```

---

# Part 4：组件设计模式总结

## 4.1 组件通信模式

### 4.1.1 Props向下传递

**适用场景**：父组件向子组件传递数据

```vue
<!-- 父组件 -->
<child-component
  :title="pageTitle"
  :data-list="tableData"
  :config="tableConfig"
/>
```

**规范**：
- 命名使用小驼峰
- 必填prop使用required
- 复杂对象提供默认值工厂函数

### 4.1.2 $emit向上传递

**适用场景**：子组件向父组件传递事件

```javascript
// 子组件
this.$emit('search', { ...formData });
this.$emit('update:visible', false);
```

```vue
<!-- 父组件 -->
<child-component
  @search="handleSearch"
  @update:visible="visible = $event"
/>
```

### 4.1.3 Vuex全局状态

**适用场景**：跨组件共享状态

```javascript
// store/modules/menu.js
export default {
  state: {
    userInfo: null,
    permissions: {}
  },
  mutations: {
    updateUserInfo(state, data) {
      state.userInfo = data;
    }
  }
}

// 组件中使用
this.$store.commit('updateUserInfo', userData);
```

### 4.1.4 通信模式对比

| 模式 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| Props/Emit | 父子组件 | 清晰、可追踪 | 深层传递麻烦 |
| Vuex | 全局状态 | 共享方便 | 复杂度增加 |
| EventBus | 非层级组件 | 灵活 | 难以追踪 |
| provide/inject | 深层传递 | 减少prop drilling | 耦合度高 |

---

## 4.2 组件组合模式

### 4.2.1 Slot插槽模式

**默认插槽**：
```vue
<!-- 父组件 -->
<modal>
  <div>这是弹窗内容</div>
</modal>

<!-- Modal组件 -->
<template>
  <div class="modal">
    <slot></slot>
  </div>
</template>
```

**具名插槽**：
```vue
<!-- 父组件 -->
<modal>
  <template v-slot:header>
    <h3>自定义标题</h3>
  </template>
  <template v-slot:footer>
    <button>确定</button>
  </template>
</modal>
```

### 4.2.2 Mixin混入模式

```javascript
// mixins/tableConfig.js
export default {
  data() {
    return {
      pagination: {
        current: 1,
        pageSize: 10,
        total: 0
      }
    }
  },
  methods: {
    handlePageChange(page, pageSize) {
      this.pagination.current = page;
      this.fetchData();
    }
  }
}

// 组件中使用
import tableConfig from '@/mixins/tableConfig';
export default {
  mixins: [tableConfig]
}
```

### 4.2.3 组合模式对比

| 模式 | 使用场景 | 建议 |
|------|----------|------|
| Slot | 内容分发 | 优先使用，解耦更彻底 |
| Mixin | 方法复用 | 注意命名冲突 |
| HOC | 增强组件 | 复杂场景使用 |

---

## 4.3 地市差异化组件组织

### 4.3.1 目录结构设计

```
src/
├── mtbcomponents/           # 宝鸡（主版本）
├── mtbnewcomponents/        # 阜新版/通用新版
├── mtbslcomponents/         # 商洛版
└── pages/
    ├── DZChronicDis/        # 地市慢病（包含多个地市）
    │   ├── components/      # 页面级组件
    │   └── config/          # 配置文件
    └── ...
```

### 4.3.2 差异化实现方式

**方式一：条件渲染**
```vue
<template>
  <div>
    <component-a v-if="cityFlag === '0'" />
    <component-b v-else-if="cityFlag === '1'" />
    <component-c v-else />
  </div>
</template>
```

**方式二：动态组件**
```vue
<template>
  <component :is="currentComponent" />
</template>

<script>
export default {
  computed: {
    currentComponent() {
      const map = {
        '0': () => import('./BJComponent.vue'),
        '1': () => import('./FXComponent.vue'),
        '2': () => import('./SLComponent.vue')
      };
      return map[this.cityFlag] || map['0'];
    }
  }
}
</script>
```

**方式三：配置文件驱动**
```javascript
// config/cityConfig.js
export default {
  '0': {  // 宝鸡
    apiHost: '/api/bj',
    features: ['featureA', 'featureB']
  },
  '1': {  // 阜新
    apiHost: '/api/fx',
    features: ['featureA', 'featureC']
  }
}
```

---

## 4.4 表单/表格/搜索通用封装思路

### 4.4.1 搜索表单封装

```javascript
// 抽象搜索配置
const searchConfig = {
  fields: [
    { key: 'name', label: '姓名', type: 'input' },
    { key: 'status', label: '状态', type: 'select', dicType: 'status' }
  ],
  colSpan: 6,
  gutter: 24
}

// 组件中使用
<searchCard
  :formObj="formObj"
  :fieldList="searchConfig.fields"
  :colSpan="searchConfig.colSpan"
  @search="handleSearch"
/>
```

### 4.4.2 表格封装

```javascript
// 表格配置
const tableConfig = {
  columns: [
    { title: '姓名', dataIndex: 'name' },
    { title: '状态', dataIndex: 'status', scopedSlots: { customRender: 'status' } }
  ],
  filters: {
    status: 'filterStatus'
  },
  pagination: {
    pageSize: 10
  }
}
```

### 4.4.3 CRUD页面模板

```vue
<template>
  <div class="page">
    <!-- 搜索区 -->
    <searchCard
      :formObj="searchForm"
      :fieldList="searchFields"
      @search="handleSearch"
      @reset="handleReset"
    />
    
    <!-- 表格区 -->
    <a-table
      :columns="columns"
      :dataSource="dataSource"
      :pagination="pagination"
      :loading="loading"
    >
      <template v-slot:actions="{ record }">
        <a @click="handleView(record)">查看</a>
        <a @click="handleEdit(record)">编辑</a>
        <a @click="handleDelete(record)">删除</a>
      </template>
    </a-table>
    
    <!-- 编辑弹窗 -->
    <edit-modal
      :visible.sync="editVisible"
      :data="currentRecord"
      @success="handleSuccess"
    />
  </div>
</template>
```

---

# Part 5：新组件开发指南

## 5.1 创建通用组件

### 5.1.1 目录规范

```
src/components/
└── YourComponentName/
    ├── index.vue           # 主组件文件
    ├── config.js           # 配置常量（可选）
    └── README.md           # 组件文档（可选）
```

### 5.1.2 组件模板

```vue
<!--
  @Author: YourName
  @Date: 2024-01-01
  @Description: 组件描述
-->
<template>
  <div class="your-component">
    <!-- 组件模板 -->
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'YourComponentName',
  
  // 组件属性
  props: {
    // String类型
    title: {
      type: String,
      default: ''
    },
    // Boolean类型
    disabled: {
      type: Boolean,
      default: false
    },
    // 复杂类型使用工厂函数
    dataList: {
      type: Array,
      default: () => []
    },
    // 必填属性
    value: {
      type: [String, Number],
      required: true
    }
  },
  
  data() {
    return {
      // 组件内部状态
      internalValue: ''
    }
  },
  
  computed: {
    // 计算属性
  },
  
  watch: {
    // 监听器
  },
  
  created() {
    // 生命周期钩子
  },
  
  methods: {
    // 方法
    handleClick() {
      this.$emit('click', this.value);
    }
  }
}
</script>

<style lang="less" scoped>
.your-component {
  // 样式
}
</style>
```

### 5.1.3 组件注册

**全局注册**（在main.js中）：
```javascript
import YourComponent from '@/components/YourComponentName';
Vue.component('YourComponentName', YourComponent);
```

**按需引入**：
```javascript
import YourComponent from '@/components/YourComponentName';

export default {
  components: {
    YourComponent
  }
}
```

---

## 5.2 创建地市差异化组件

### 5.2.1 目录规范

```
src/pages/
└── YourBusiness/
    ├── BJComponent.vue      # 宝鸡版本
    ├── FXComponent.vue      # 阜新版本
    ├── SLComponent.vue      # 商洛版本
    └── index.vue            # 入口组件（自动选择）
```

### 5.2.2 自动选择组件

```vue
<!-- index.vue -->
<template>
  <component :is="currentComponent" v-bind="$attrs" v-on="$listeners" />
</template>

<script>
export default {
  name: 'YourBusinessIndex',
  
  computed: {
    // 获取当前地市标识
    cityFlag() {
      return this.$route.query.flag || '0';
    },
    
    // 根据地市返回对应组件
    currentComponent() {
      const componentMap = {
        '0': () => import('./BJComponent.vue'),  // 宝鸡
        '1': () => import('./FXComponent.vue'), // 阜新
        '2': () => import('./SLComponent.vue')  // 商洛
      };
      
      return componentMap[this.cityFlag] || componentMap['0'];
    }
  }
}
</script>
```

### 5.2.3 差异点管理

```javascript
// config/diffConfig.js
export default {
  '0': {
    // 宝鸡配置
    title: '宝鸡慢病管理',
    apiPath: '/api/bj/declare',
    features: ['A', 'B']
  },
  '1': {
    // 阜新配置
    title: '阜新慢病管理',
    apiPath: '/api/fx/declare',
    features: ['A', 'C']
  }
}

// 组件中使用
import cityConfig from './config/diffConfig';

export default {
  computed: {
    config() {
      return cityConfig[this.cityFlag];
    }
  }
}
```

---

## 5.3 创建可复用业务组件

### 5.3.1 分析复用场景

在创建组件前，问自己：
1. 这个组件会在几个地方使用？
2. 哪些部分是变化的？哪些是固定的？
3. 能否抽离配置项？

### 5.3.2 设计Props接口

```javascript
props: {
  // 基础配置
  title: String,
  width: {
    type: String,
    default: '60%'
  },
  
  // 数据配置
  dataSource: {
    type: Array,
    required: true
  },
  columns: {
    type: Array,
    required: true
  },
  
  // 行为配置
  showPagination: {
    type: Boolean,
    default: true
  },
  showSelection: {
    type: Boolean,
    default: false
  },
  
  // 事件映射
  events: {
    type: Object,
    default: () => ({
      search: 'onSearch',
      select: 'onSelect'
    })
  }
}
```

### 5.3.3 提供Slots

```vue
<!-- 头部插槽 -->
<slot name="header">
  <div class="default-header">默认标题</div>
</slot>

<!-- 操作区插槽 -->
<slot name="actions">
  <a-button @click="$emit('add')">新增</a-button>
</slot>

<!-- 自定义列插槽 -->
<template v-for="col in columns">
  <slot :name="col.scopedSlots?.customRender">
    {{ col.title }}
  </slot>
</template>
```

### 5.3.4 完整示例

```vue
<!-- BusinessTable.vue -->
<template>
  <div class="business-table">
    <div class="header">
      <slot name="header">
        <h3>{{ title }}</h3>
      </slot>
      <div class="actions">
        <slot name="actions"></slot>
      </div>
    </div>
    
    <a-table
      :columns="columns"
      :dataSource="dataSource"
      :pagination="showPagination ? pagination : false"
      :rowSelection="showSelection ? rowSelection : null"
      v-bind="$attrs"
    >
      <!-- 默认插槽透传 -->
      <template v-for="(_, name) in $scopedSlots" v-slot:[name]="slotData">
        <slot :name="name" v-bind="slotData"></slot>
      </template>
    </a-table>
  </div>
</template>

<script>
export default {
  name: 'BusinessTable',
  props: {
    title: String,
    dataSource: Array,
    columns: Array,
    showPagination: Boolean,
    showSelection: Boolean
  },
  data() {
    return {
      pagination: {
        current: 1,
        pageSize: 10,
        total: 0
      },
      rowSelection: {
        type: 'checkbox',
        onChange: (keys, rows) => {
          this.$emit('select', rows);
        }
      }
    }
  },
  methods: {
    // 可添加通用方法
  }
}
</script>
```

---

## 5.4 组件命名规范

### 5.4.1 文件命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 通用组件 | PascalCase + 功能名 | `SearchCard.vue`, `DataTable.vue` |
| 业务组件 | 模块名 + 功能名 | `DeclareForm.vue`, `UserCard.vue` |
| 布局组件 | Layout + 功能名 | `LayoutHeader.vue` |
| 弹窗组件 | 功能名 + Modal | `EditModal.vue`, `ConfirmModal.vue` |

### 5.4.2 组件名规范

```javascript
// PascalCase命名
export default {
  name: 'SearchCard'    // 组件名
}
```

### 5.4.3 Props命名

```javascript
// 小驼峰命名
props: {
  tableTitle: String,      // 表格标题
  dataSource: Array,       // 数据源
  isLoading: Boolean,      // 加载状态
  pageSize: {
    type: Number,
    default: 10
  }
}
```

### 5.4.4 事件命名

```javascript
// 使用kebab-case
this.$emit('update:visible', false);
this.$emit('search-change', params);
this.$emit('row-click', record);
```

---

## 5.5 目录规范总结

```
src/
├── components/              # 通用基础组件
│   ├── myTable/
│   ├── searchCard/
│   └── comSelect/
├── mtbnewcomponents/        # 业务通用组件
│   ├── Modal/
│   └── searchCard/
├── mtbcomponents/           # 宝鸡业务组件
├── mtbslcomponents/          # 商洛业务组件
└── pages/                   # 页面组件
    ├── DZChronicDis/        # 地市差异化页面
    │   ├── components/      # 页面级私有组件
    │   ├── config/          # 页面配置
    │   └── *.vue            # 业务页面
    └── ...
```

---

# 附录：快速参考

## A. 常用组件引入路径

```javascript
// 表格
import MyTable from "@/components/myTable";

// 搜索
import SearchCard from "@/components/searchCard";

// 下拉选择
import ComSelect from "@/components/comSelect";

// 弹窗
import DragModal from "@/mtbnewcomponents/Modal/dragModal";

// Mixin
import TableMixins from "@/utils/tableMixins";
```

## B. 常用API引入路径

```javascript
import api from "@/api/apiChronicDis";
import apiDeclare from "@/api/apiDeclare";
import apiUser from "@/api/apiUserManage";
```

## C. 常用工具函数

```javascript
import util from "@/utils/util";

// 工具函数
util.getUserInfo();      // 获取用户信息
util.formatDate();       // 格式化日期
util.qianfenwei();       // 千分位格式化
```

---

> 📝 **文档版本**：v1.0
> 🕐 **更新日期**：2024年
> 👤 **维护者**：PICC慢特病前端团队
