<script setup>
import { ref, reactive, onMounted } from 'vue'
import { 
  fetchAdminResources, 
  fetchAmapSearch, 
  batchImportResources, 
  deleteResource,
  updateResource,
} from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Download, Delete, Edit } from '@element-plus/icons-vue'
import { CATEGORY_OPTIONS, selectedCategory, editDialogView, editForm } from '@/store/resWinState'

// --- 1. 列表与分页状态 ---
const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const queryParams = reactive({
  page: 1,
  size: 12,
  category: '',
  status: null,
  keyword: ''
})

// --- 2. 高德拉取弹窗状态 ---
const pullDialogView = ref(false)
const searchLoading = ref(false)
const amapKeyword = ref('')
const amapResults = ref([])
const selectedFromAmap = ref([])

const emit = defineEmits(['row-click', 'refresh-stats'])

// --- 3. 核心业务逻辑：加载本地数据 ---
const loadData = async () => {
  loading.value = true
  try {
    const res = await fetchAdminResources(queryParams)
    tableData.value = res.items
    total.value = res.total
  } catch (error) {
    ElMessage.error('加载资源列表失败')
  } finally {
    loading.value = false
  }
}

const handleFilter = () => {
  queryParams.page = 1
  loadData()
}

// --- 4. 核心业务逻辑：高德数据采集 ---
const handleAmapSearch = async () => {
  if (!amapKeyword.value) return ElMessage.warning('请输入搜索关键词')
  if (!selectedCategory.value) return ElMessage.warning('请选择入库分类')
  searchLoading.value = true

  try {
    // 调用后端代理的高德搜索接口
    const data = await fetchAmapSearch({
        keyword: amapKeyword.value,
    })
    amapResults.value = data
  } catch (error) {
    console.error('搜索高德数据失败:', error)
    ElMessage.error(`搜索高德数据失败: ${error.message || '未知错误'}`)
  } finally {
    searchLoading.value = false
  }
}

const handleSelectionChange = (val) => {
  selectedFromAmap.value = val
}

const handleImport = async () => {
  if (selectedFromAmap.value.length === 0) return
  if (!selectedCategory.value) {
    return ElMessage.error('入库失败：未指定资源所属分类')
  }
  try {
    const preparedData = selectedFromAmap.value.map(item => ({
      ...item,
      category: selectedCategory.value // 强制覆盖为下拉框选中的分类
    }))

    const res = await batchImportResources(preparedData)
    ElMessage.success(`成功导入 ${res.imported} 条新资源至待审核池`)
    pullDialogView.value = false
    amapResults.value = []
    amapKeyword.value = ''
    loadData() // 刷新列表
    emit('refresh-stats') // 通知父组件刷新顶栏统计
  } catch (error) {
    ElMessage.error('导入操作失败')
  }
}

// --- 5. 核心业务逻辑：数据维护 ---
const handleRowDelete = (row) => {
  ElMessageBox.confirm(`确定要删除资源点【${row.name}】吗？`, '警告', {
    type: 'warning',
    confirmButtonText: '确定删除'
  }).then(async () => {
    await deleteResource(row.id)
    ElMessage.success('删除成功')
    loadData()
    emit('refresh-stats')
  })
}

// 状态标签映射
const statusMap = {
  0: { label: '待审核', type: 'info' },
  1: { label: '已发布', type: 'success' },
  2: { label: '异常', type: 'danger' }
}

const handleEdit = (row) => {
  Object.assign(editForm, row) // 快速拷贝对象属性
  editDialogView.value = true
}

const submitEdit = async () => {
  try {
    // 确保 id 是整数
    const resourceId = parseInt(editForm.id)
    if (isNaN(resourceId)) {
      return ElMessage.error('无效的资源 ID')
    }
    
    // 只传递需要更新的字段，排除 id 和 latlng
    const updateData = {
      name: editForm.name,
      category: editForm.category,
      address: editForm.address,
      phone: editForm.phone,
      tags: editForm.tags,
      description: editForm.description,
      status: editForm.status
    }
    
    await updateResource(resourceId, updateData)
    
    ElMessage.success('操作成功')
    editDialogView.value = false
    loadData()
    emit('refresh-stats')
  } catch (error) {
    console.error("提交失败详情:", error)
    ElMessage.error('更新失败')
  }
}

const handleQuickPublish = async (row) => {
  try {
    await updateResource(row.id, { status: 1 })
    ElMessage.success(`已发布：${row.name}`)
    loadData()
    emit('refresh-stats')
  } catch (e) { /* ... */ }
}

onMounted(loadData)
</script>

<template>
  <div class="resource-table-container">
    <!-- 顶部过滤工具栏 -->
    <div class="toolbar">
      <el-form :inline="true" :model="queryParams" size="default">
        <el-form-item>
          <el-select v-model="queryParams.category" placeholder="分类筛选" clearable @change="handleFilter" style="width: 120px">
            <el-option 
              v-for="opt in CATEGORY_OPTIONS" 
              :key="opt.value" 
              :label="opt.label" 
              :value="opt.value" 
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-select v-model="queryParams.status" placeholder="状态" clearable @change="handleFilter" style="width: 100px">
            <el-option label="待审核" :value="0" />
            <el-option label="已发布" :value="1" />
            <el-option label="异常" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-input 
            v-model="queryParams.keyword" 
            placeholder="搜索资源名称..." 
            clearable 
            @keyup.enter="handleFilter"
            :prefix-icon="Search"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">查询</el-button>
          <el-button type="success" :icon="Download" @click="pullDialogView = true">采集高德数据</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 主数据表格 -->
    <div class="table-container">
      <el-table 
        :data="tableData" 
        v-loading="loading" 
        height="100%" 
        highlight-current-row
        @row-click="(row) => emit('row-click', row)"
      >
        <el-table-column prop="name" label="名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="80" align="center" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status].type" size="small">
              {{ statusMap[row.status].label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="address" label="地址" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" show-overflow-tooltip />
        <el-table-column prop="updated_at" label="更新时间" show-overflow-tooltip />
        <el-table-column prop="modify_by" label="管理员id" show-overflow-tooltip />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <!-- [新按钮]：仅在“待审核”状态显示一键发布 -->
            <el-button 
              v-if="row.status === 0" 
              link 
              type="success" 
              @click.stop="handleQuickPublish(row)"
            >发布</el-button>

            <!-- [新按钮]：编辑详情 -->
            <el-button 
              link 
              type="primary" 
              :icon="Edit" 
              @click.stop="handleEdit(row)"
            >编辑</el-button>

            <el-button 
              link 
              type="danger" 
              :icon="Delete" 
              @click.stop="handleRowDelete(row)" 
            />
          </template>
        </el-table-column>
            <el-button link type="danger" :icon="Delete" @click.stop="handleRowDelete(row)" />
      </el-table>
    </div>

    <!-- 底部分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="queryParams.page"
        :page-size="queryParams.size"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadData"
        background
      />
    </div>

    <!-- 采集数据弹窗 -->
    <el-dialog v-model="pullDialogView" class="res-collect-dialog" title="高德数据实时采集" width="850px" destroy-on-close>
      <div class="amap-search-box">
        <el-input 
          v-model="amapKeyword" 
          placeholder="输入关键词(如:大连 社区卫生中心)" 
          @keyup.enter="handleAmapSearch"
        >
          <template #prepend>
            <el-select v-model="selectedCategory" placeholder="设定入库分类" style="width: 130px">
              <el-option 
                v-for="opt in CATEGORY_OPTIONS" 
                :key="opt.value" 
                :label="opt.label" 
                :value="opt.value" 
              />
            </el-select>
          </template>
          <template #append>
            <el-button :icon="Search" @click="handleAmapSearch" :loading="searchLoading">搜索预览</el-button>
          </template>
        </el-input>
      </div>

      <el-table :data="amapResults" height="350px" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="tags" label="类型" />
        <el-table-column prop="address" label="地址" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="phone" label="电话" width="150" />
      </el-table>

      <template #footer>
        <div class="dialog-footer">
          <span class="selected-count">已选 {{ selectedFromAmap.length }} 项</span>
          <el-button @click="pullDialogView = false">取消</el-button>
          <el-button type="success" :disabled="!selectedFromAmap.length" @click="handleImport">确认入库</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 资源编辑/审查对话框 -->
    <el-dialog 
      v-model="editDialogView" 
      title="资源点详细信息审查" 
      width="550px"
      append-to-body
    >
      <el-form :model="editForm" label-width="100px" size="default">
        <el-form-item label="资源名称">
          <el-input v-model="editForm.name" />
        </el-form-item>
        
        <el-form-item label="所属分类">
          <el-select v-model="editForm.category" style="width: 100%">
            <!-- 复用 resState 里的统一分类选项 -->
            <el-option 
              v-for="opt in CATEGORY_OPTIONS" 
              :key="opt.value" 
              :label="opt.label" 
              :value="opt.value" 
            />
          </el-select>
        </el-form-item>

        <el-form-item label="物理地址">
          <el-input v-model="editForm.address" type="textarea" :rows="2" />
        </el-form-item>

        <el-form-item label="联系电话">
          <el-input v-model="editForm.phone" />
        </el-form-item>

        <el-form-item label="业务标签">
          <el-input v-model="editForm.tags" placeholder="多标签请用分号隔开" />
        </el-form-item>

        <el-form-item label="资源描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>

        <el-form-item label="经纬坐标">
          <el-input v-model="editForm.latlng" disabled>
            <template #append>不可手动修改</template>
          </el-input>
        </el-form-item>

        <el-form-item label="审核状态">
          <el-radio-group v-model="editForm.status">
            <el-radio :value="0">待审核</el-radio>
            <el-radio :value="1">通过/发布</el-radio>
            <el-radio :value="2">异常/废弃</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editDialogView = false">取消</el-button>
        <el-button type="primary" @click="submitEdit">保存并更新</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.resource-table-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-sizing: border-box;
}
.toolbar {
  margin-bottom: 10px;
  flex-shrink: 0;
}
.table-container {
  flex: 1;
  min-height: 0; 
  margin-bottom: 10px;
}
.pagination {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
}
.amap-search-box {
  margin-bottom: 20px;
}
.res-collect-dialog {
  overflow: hidden;
}
:deep(.res-collect-dialog .el-dialog__body) {
  overflow: hidden;
}
.selected-count {
  margin-right: 20px;
  font-size: 13px;
  color: #909399;
}
:deep(.el-table__row) {
  cursor: pointer;
}
</style>