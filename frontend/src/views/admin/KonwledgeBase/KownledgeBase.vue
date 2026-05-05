<script setup>
import KnowledgeStats from './components/KnowledgeStats.vue'
import UploadPanel from './components/UploadPanel.vue'
import DocList from './components/DocList.vue'
import { ref } from 'vue'

const statsRef = ref(null)
const listRef = ref(null)

const refreshAll = () => {
  statsRef.value?.loadStats()
  listRef.value?.loadData()
}

const refreshStatsOnly = () => {
  statsRef.value?.loadStats()
}
</script>

<template>
    <div class="knowledge-container">
        <KnowledgeStats ref="statsRef" />
        <UploadPanel @success="refreshAll" />

        <el-card>
            <template #header>
                <span>文档列表</span>
                <el-button type="success" size="small">同步至向量数据库</el-button>
            </template>
            <DocList ref="listRef" @refresh="refreshStatsOnly" />
        </el-card>
    </div>
</template>

<style scoped>
.knowledge-container { padding: 10px; }
.table-header { display: flex; justify-content: space-between; align-items: center; }
</style>
