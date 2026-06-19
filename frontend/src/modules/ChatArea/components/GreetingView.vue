<script setup>
import { messages } from '@/store/convoSwitch'
const emit = defineEmits(['send'])

const suggestions = [
  { icon: '📜', text: '梳理一下大连低保相关信息。' },
  { icon: '🆔', text: '我想去办理护照，怎么走流程？' },
  { icon: '🏥', text: '帮我找一下离我最近的医院。' },
  { icon: '🏠', text: '我想了解大连的失业政策。' }
]

const handleSuggestionClick = (text) => {
  emit('send', text);
}
</script>

<template>
    <div v-if="messages.length === 0" class="greet-view">
        <div class="greet-header">
            <div class="logo">🏢</div>
            <h1>您好，新市民朋友！</h1>
            <p>我是您的智慧政务助手，致力于为您解决政策、办事及资源匹配难题。</p>
        </div>

        <div class="suggestion-grid">
            <div
                v-for="(item, index) in suggestions"
                :key="index"
                class="suggestion-card"
                @click="handleSuggestionClick(item.text)"
            >
                <div class="card-icon">{{ item.icon }}</div>
                <div class="card-text">{{ item.text }}</div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.greet-view {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 80%;
    max-width: 800px;
    margin: 0 auto;
    color: #374151;
}
.greet-header {
    text-align: center;
    margin-bottom: 40px;
}
.greet-header .logo {
    font-size: 48px;
    margin-bottom: 10px;
}
.greet-header h1 {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 15px;
}
.greet-header p {
    color: #6b7280;
    font-size: 16px;
}
.suggestion-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    width: 100%;
}
.suggestion-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 16px 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.2s ease;
}
.suggestion-card:hover {
  background: #f3f4f6;
  border-color: #409eff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.card-icon {
  font-size: 20px;
}
.card-text {
  font-size: 14px;
  color: #4b5563;
  line-height: 1.4;
}
</style>