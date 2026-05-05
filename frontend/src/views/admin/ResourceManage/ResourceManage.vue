<script setup>
import { ref } from 'vue'
import ResourceTable from './components/ResourceTable.vue'
import ResourceMapPreview from './components/ResourceMapPreview.vue'

const selectedResource = ref(null)
const tableRef = ref(null)

// 逻辑接洽：当用户点击表格某一行时，更新选中对象，触发右侧地图联动
const handleRowClick = (row) => {
  selectedResource.value = row
}
</script>


<template>
  <div class="resource-manage-container">
    <!-- 左侧：列表与过滤区 -->
    <div class="table-section">
      <ResourceTable @row-click="handleRowClick" ref="tableRef" />
    </div>

    <!-- 右侧：地图预览区 -->
    <div class="map-preview-section">
      <ResourceMapPreview :active-resource="selectedResource" />
    </div>
  </div>
</template>


<style scoped>
.resource-manage-container {
  display: flex;
  height: calc(100vh - 120px); /* 减去 Header 空间 */
  gap: 20px;
  padding: 10px;
}
.table-section { flex: 7; background: #fff; border-radius: 8px; overflow: hidden; }
.map-preview-section { flex: 3; background: #fff; border-radius: 8px; border: 1px solid #ebeef5; }
</style>