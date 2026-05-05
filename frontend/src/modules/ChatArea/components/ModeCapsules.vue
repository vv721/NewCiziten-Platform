<script setup>
import { uiState } from '@/store/uiState'
import { 
  MagicStick, 
  Search, 
  Location, 
  Guide 
} from '@element-plus/icons-vue'

// 定义胶囊配置：名称、图标、对应的模式 key
const capsules = [
  { label: '智能分析', mode: 'auto', icon: MagicStick },
  { label: '政策寻踪', mode: 'policy', icon: Search },
  { label: '资源匹配', mode: 'map', icon: Location },
  { label: '办事导航', mode: 'service', icon: Guide }
]

const handleSelect = (mode) => {
  uiState.setMode(mode)
}
</script>

<template>
  <div class="capsules-container">
    <div 
      v-for="item in capsules" 
      :key="item.mode"
      :class="['capsule-item', { active: uiState.activeMode === item.mode }]"
      @click="handleSelect(item.mode)"
    >
      <el-icon class="capsule-icon"><component :is="item.icon" /></el-icon>
      <span class="capsule-label">{{ item.label }}</span>
    </div>
  </div>
</template>

<style scoped>
.capsules-container {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  padding: 2px 0 2px 75px;
  /* 确保在窄屏下可以横向滚动，模仿移动端体验 */
  overflow-x: auto;
  scrollbar-width: none; /* Firefox */
}

.capsules-container::-webkit-scrollbar {
  display: none; /* Chrome/Safari */
}

.capsule-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background-color: rgba(255, 255, 255, 0.6);
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: #4b5563;
  font-size: 13px;
  user-select: none;
}

/* 悬浮效果 */
.capsule-item:hover {
  background-color: #ffffff;
  border-color: #409eff;
  color: #409eff;
  transform: translateY(-1px);
}

/* 选中激活态样式 */
.capsule-item.active {
  background-color: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.capsule-icon {
  font-size: 14px;
}
</style>