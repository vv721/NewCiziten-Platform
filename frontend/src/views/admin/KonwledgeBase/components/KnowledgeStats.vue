<script setup>
import { onMounted, ref } from 'vue'
import { getDocsStatus } from '@/api/admin'

const statsData = ref([
  { title: '载入文档总量', value: '0', unit: '份', key: 'total_docs' },
  { title: '逻辑分片总数', value: '0', unit: 'Chunks', key: 'total_chunks' },
  { title: '向量库索引量', value: '768', unit: 'Dim', key: 'vector_dim' },
  { title: '检索平均耗时', value: '0', unit: 'ms', key: 'avg_latency' }
])

const loadStats = async () => {
  try {
    const res = await getDocsStatus()
    // 根据后端返回的数据更新对应项
    statsData.value[0].value = res.total_docs
    statsData.value[1].value = res.total_chunks
    statsData.value[2].value = res.vector_dim
    statsData.value[3].value = res.avg_latency
  } catch (error) {
    console.error("统计数据同步失败")
  }
}

defineExpose({ loadStats })
onMounted(loadStats)
</script>

<template>
  <el-row :gutter="20" class="stat-container">
    <el-col :span="6" v-for="item in statsData" :key="item.title">
      <el-card shadow="hover" class="stat-card">
        <template #header><span class="stat-title">{{ item.title }}</span></template>
        <div class="stat-value">
          {{ (item.value ?? 0).toLocaleString() }}
          <small class="unit">{{ item.unit }}</small>
        </div>
      </el-card>
    </el-col>
  </el-row>
</template>

<style scoped>
.stat-container { margin-bottom: 20px; }
.stat-card { border-radius: 8px; border: none; box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05); }
.stat-title { font-size: 13px; color: #909399; font-weight: 500; }
.stat-value { font-size: 26px; font-weight: 700; color: #409EFF; display: flex; align-items: baseline; }
.unit { font-size: 12px; color: #999; margin-left: 4px; font-weight: normal; }
</style>

