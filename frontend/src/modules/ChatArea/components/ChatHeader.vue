<script setup>
import { computed } from 'vue'
import { activeConvoId, convoList } from '@/store/convoSwitch'

const title = computed(() => {
  if (!activeConvoId.value) return '新会话'
  const convo = convoList.value.find(c => c.id === activeConvoId.value)
  return convo ? convo.title : '新会话'
})
</script>

<template>
  <header class="chat-header">
    <span class="convo-title">{{ title }}</span>
  </header>
</template>

<style scoped>
.chat-header {
  height: 28px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #f1f5f9;
  position: sticky;
  top: 0;
  z-index: 10;
}

.convo-title {
  font-size: 13px;
  font-weight: 500;
  color: #6b7280;
  letter-spacing: 0.3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>