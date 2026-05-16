<script setup>
import { Plus } from '@element-plus/icons-vue'

const emit = defineEmits(['new-chat'])
</script>

<template>
  <div class="sidebar-header">
    <!-- 品牌区 -->
    <div class="brand">
      <span class="logo">🏛️</span>
      <span class="title">新市民智慧服务</span>
    </div>
    
    <!-- 整合进来的按钮 -->
    <button class="new-chat-btn" @click="emit('new-chat')">
      <el-icon><Plus /></el-icon>
      <span>开启新会话</span>
    </button>
  </div>
</template>

<style scoped>
.sidebar-header {
  padding: 24px 16px 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.logo {
  font-size: 20px;
}

.title {
  font-size: 15px;
  font-weight: 600;
  color: #374151;
  letter-spacing: 0.5px;
}

.new-chat-btn {
  width: 100%;
  height: 44px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s ease;
}

.new-chat-btn:hover {
  background-color: #f9fafb;
  border-color: #d1d5db;
  color: #111827;
}

.new-chat-btn:active {
  transform: scale(0.98);
}
</style>