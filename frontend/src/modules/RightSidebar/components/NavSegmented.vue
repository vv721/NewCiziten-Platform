<script setup>
import { computed } from 'vue'
import { uiState } from '@/store/uiState'

// 页面配置，保持与 uiState 中的索引对应
const tabs = [
  { label: '溯源', index: 0 },
  { label: '地图', index: 1 },
  { label: '办事', index: 2 }
]

// 逻辑：计算当前滑块应该偏移的百分比
const activeStyle = computed(() => {
  const percent = (uiState.currentCarouselIndex * 100)
  return {
    transform: `translateX(${percent}%)`,
    width: `${100 / tabs.length}%`
  }
})

const handleTabClick = (index) => {
  uiState.currentCarouselIndex = index
}
</script>

<template>
  <div class="segmented-container">
    <div class="segmented-control">
      <!-- 背景滑块动画层 -->
      <div class="active-bg" :style="activeStyle"></div>
      
      <!-- 选项层 -->
      <div 
        v-for="tab in tabs" 
        :key="tab.index"
        :class="['tab-item', { active: uiState.currentCarouselIndex === tab.index }]"
        @click="handleTabClick(tab.index)"
      >
        {{ tab.label }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.segmented-container {
  padding: 12px 16px 8px;
  background-color: #ffffff;
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.segmented-control {
  position: relative;
  display: flex;
  width: 100%;
  background-color: #f1f5f9; /* 浅灰色底 */
  border-radius: 20px;
  padding: 3px;
  user-select: none;
}

/* 动态滑块样式 */
.active-bg {
  position: absolute;
  top: 3px;
  bottom: 3px;
  left: 0;
  background-color: #ffffff;
  border-radius: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1;
}

.tab-item {
  position: relative;
  flex: 1;
  z-index: 2;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: #64748b;
  cursor: pointer;
  transition: color 0.3s;
}

.tab-item.active {
  color: #3b82f6; /* 激活时变为蓝色 */
  font-weight: 600;
}
</style>