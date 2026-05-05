<script setup>
import { ref, onMounted } from 'vue'
import { getDocs, previewDoc, deleteDoc, rebuildIndex } from '@/api/admin'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { ragState } from '@/store/ragState'

const docList = ref([])
const previewVisible = ref(false)
const previewLoading = ref(false)
const chunks = ref([])

const emit = defineEmits(['refresh'])

const loadData = async () => {
  try {
    const res = await getDocs()
    docList.value = res
  } catch (e) {
    console.error("加载文档列表失败:", e)
  }
}

const handlPreview = async (row) => {
  if (row.status !== 'ready') return ElMessage.warning('文档尚未处理完成')

  previewVisible.value = true
  previewLoading.value = true

  try {
    const res = await previewDoc(row.id)
    chunks.value = res // 后端返回的格式：[{content, metadata}, ...]
  } catch (e) {
    ElMessage.error('无法加载预览数据')
  } finally {
    previewLoading.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要永久删除《${row.filename}》吗？这将同步清除物理文件及其在 AI 向量库中的所有索引。`,
    '风险警告',
    { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' }
  ).then(async () => {
    try {
      await deleteDoc(row.id)
      ElMessage.success('知识库关联数据已彻底清除')
      loadData() // 刷新列表
      emit('refresh')
    } catch (e) {
      ElMessage.error('删除失败')
    }
  })
}

const handleRebuild = async (row) => {
  ElMessageBox.confirm(
    `将按当前配置（Size:${ragState.size}, Overlap:${ragState.overlap}）重构索引，是否继续？`,
    '重构确认',
    { type: 'warning' }
  ).then(async () => {
    const loading = ElLoading.service({ text: '正在应用新策略重构中...' })
    try {
      // 直接从 ragState 读取 UI 上的最新值
      await rebuildIndex(row.id, {
        chunk_size: ragState.size,
        chunk_overlap: ragState.overlap,
        strategy: ragState.strategy
      })
      ElMessage.success('重构成功')
      loadData() 
      emit('refresh')
    } catch (e) {
      ElMessage.error('重构失败')
    } finally {
      loading.close()
    }
  })
}

defineExpose({
  loadData
})

onMounted(loadData)
</script>

<template>
  <div class="doc-list-container">
    <el-table :data="docList" border stripe style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="filename" label="文件名" min-width="200" />
      <el-table-column prop="chunk_count" label="分片数" width="100" align="center" />
      <el-table-column label="文件大小" width="120" align="center">
        <template #default="scope">
          {{ scope.row.file_size ? `${scope.row.file_size} MB` : '0 MB' }}
        </template>
      </el-table-column>
      <el-table-column label="解析状态" width="120" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.status === '已就绪' ? 'success' : 'warning'">
            {{ scope.row.status === 'ready' ? '已就绪' : '处理中' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="uploaded_at" label="上传时间" width="180" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="handlPreview(scope.row)">预览切片</el-button>
          <el-button link type="primary" @click="handleRebuild(scope.row)">重构索引</el-button>
          <el-button link type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="previewVisible" title="知识分片预览 (Top 10)" width="70%">
      <div v-loading="previewLoading">
        <el-empty v-if="chunks.length === 0" description="暂无切片数据" />
        <div v-else class="chunk-container">
          <el-card v-for="(chunk, index) in chunks" :key="index" class="chunk-card">
            <template #header>
              <div class="chunk-header">
                <el-tag size="small">分片 #{{ index + 1 }}</el-tag>
                <span class="chunk-meta">来源页码: {{ chunk.metadata.page + 1 }}</span>
              </div>
            </template>
            <p class="chunk-content">{{ chunk.content }}</p>
          </el-card>
        </div>
      </div>
    </el-dialog>
  </div>
  
</template>

<style scoped>
.chunk-container { max-height: 500px; overflow-y: auto; }
.chunk-card { margin-bottom: 15px; }
.chunk-header { display: flex; justify-content: space-between; align-items: center; }
.chunk-meta { font-size: 12px; color: #909399; }
.chunk-content { font-size: 14px; line-height: 1.6; color: #333; white-space: pre-wrap; }
</style>