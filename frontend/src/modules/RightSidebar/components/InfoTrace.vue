<script setup>
import { ref, computed } from 'vue'
import { uiState } from '@/store/uiState'
import { Reading, Files, ZoomIn } from '@element-plus/icons-vue'
import InfoTraceIntro from '@/modules/RightSidebar/Intro/InfoTraceIntro.vue'

// --- 1. 响应式状态 ---
const traceData = computed(() => uiState.citationList)
const drawerVisible = ref(false)
const activeDetail = ref({ title: '', content: '', source: '', page: '' })

// --- 2. 交互逻辑：打开详情抽屉 ---
const handleShowDetail = (item, index) => {
  activeDetail.value = {
    index: index + 1,
    content: item.content,
    source: item.source,
    page: item.page
  }
  drawerVisible.value = true
}
</script>

<template>
  <div class="trace-container">
    <!-- 顶部标题区 -->
    <div class="trace-header">
      <div class="header-main">
        <el-icon><Reading /></el-icon>
        <span>政策溯源依据</span>
      </div>
    </div>

    <div class="trace-body">
      <!-- 引导页 -->
      <InfoTraceIntro v-if="traceData.length === 0" />
      <!-- 摘要卡片列表 -->
      <div v-else class="trace-list">
        <el-empty v-if="traceData.length === 0" description="暂无引用" :image-size="40" />

        <div 
          v-for="(item, index) in traceData" 
          :key="index" 
          class="summary-card"
          @click="handleShowDetail(item, index)"
        >
          <div class="card-top">
            <span class="index-tag">#{{ index + 1 }}</span>
            <span class="file-name">{{ item.source }}</span>
          </div>
          <!-- 关键点：此处只展示两行预览，强制换行截断 -->
          <div class="preview-text">
            {{ item.content }}
          </div>
          <div class="card-footer">
            <span>第 {{ item.page }} 页</span>
            <el-link type="primary" :underline="'never'" :icon="ZoomIn">查看原文</el-link>
          </div>
        </div>
      </div>
    </div>  

    <!-- 全局证据详情抽屉 -->
    <!-- append-to-body 确保抽屉不会被轮播图容器裁剪 -->
    <el-drawer
      v-model="drawerVisible"
      direction="rtl"
      size="350px"
      :title="'证据详情 #' + activeDetail.index"
      append-to-body
      class="trace-detail-drawer"
    >
      <div class="detail-wrapper">
        <div class="detail-meta">
          <el-tag size="small"><el-icon><Files /></el-icon> {{ activeDetail.source }}</el-tag>
          <span class="page-num">页码：{{ activeDetail.page }}</span>
        </div>
        <!-- 详情区：支持原生纵向滚动，文字想多长就多长 -->
        <div class="full-content">
          {{ activeDetail.content }}
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<style scoped>
/* 容器布局 */
.trace-container {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f8fafc;
}

.trace-header {
  flex-shrink: 0;
  padding: 16px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
}

.header-main {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 14px;
}

/* trace-body 承接剩余高度，约束子元素滚动 */
.trace-body {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

/* 列表滚动区（隐藏滚动条但保留滚动能力） */
.trace-list {
  height: 100%;
  overflow-y: auto;
  padding: 12px;
  scrollbar-width: none;
}

.trace-list::-webkit-scrollbar {
  display: none;
}

/* 摘要卡片：轻量化设计 */
.summary-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.summary-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.card-top {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.index-tag {
  background: #eff6ff;
  color: #3b82f6;
  font-size: 10px;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 4px;
}

.file-name {
  font-size: 12px;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* [核心修正]：强制约束预览文本为2行 */
.preview-text {
  font-size: 13px;
  line-height: 1.5;
  color: #1e293b;
  display: -webkit-box;
  -webkit-line-clamp: 2; /* 只显2行 */
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 8px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #94a3b8;
}

/* 抽屉内样式 */
.detail-wrapper {
  padding: 0 10px;
}

.detail-meta {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.full-content {
  font-size: 14px;
  line-height: 1.8;
  color: #334155;
  white-space: pre-wrap; /* 保持原文档换行 */
  text-align: justify;
}
</style>