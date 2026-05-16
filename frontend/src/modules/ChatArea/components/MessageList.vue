<script setup>
defineProps(['messages'])
import { activeTab } from '@/store/convoSwitch'
import { useMarkdown } from '@/hooks/useMarkDown'

const { render } = useMarkdown()
</script>

<template>
  <!-- 外层容器，确保有垂直间距 -->
  <div class="message-list-wrapper">
    
    <!-- 1. 当前实时对话 (mainchat) -->
    <div v-if="activeTab === 'mainchat'" class="chat-flow">
      <div v-for="(msg, index) in messages" :key="index" :class="['msg-row', msg.role]">
        <div class="avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
        <div class="bubble">
          <div v-if="msg.role === 'ai' && !msg.content" class="typing-indicator">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
          <div v-else class="markdown-body" v-html="render(msg.content)"></div>
          <div v-if="msg.sources && msg.sources.length" class="source-tag">
            参考自: {{ msg.sources.join(', ') }}
          </div>
        </div>
      </div>
    </div>

    <!-- 2. 历史会话1 (history1) -->
    <div v-else-if="activeTab === 'history1'" class="chat-flow">
      <div class="msg-row user">
        <div class="avatar">👤</div>
        <div class="bubble">怎么办理落户？</div>
      </div>
      <div class="msg-row ai">
        <div class="avatar">🤖</div>
        <div class="bubble">准备好身份证、居住证以及房产证前往当地政务中心办理即可。</div>
      </div>
    </div>

    <!-- 3. 历史会话2 (history2) -->
    <div v-else-if="activeTab === 'history2'" class="chat-flow">
      <div class="msg-row user">
        <div class="avatar">👤</div>
        <div class="bubble">测试？</div>
      </div>
      <div class="msg-row ai">
        <div class="avatar">🤖</div>
        <div class="bubble">你好！有什么可以帮你的？</div>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* 容器布局 */
.message-list-wrapper {
  padding: 10px;
  display: flex;
  flex-direction: column;
}

.chat-flow {
  display: flex;
  flex-direction: column;
  gap: 20px; /* 消息之间的间距 */
}

/* 消息行基础样式 */
.msg-row {
  display: flex;
  max-width: 85%;
  align-items: flex-start;
  gap: 10px;
}

/* AI 消息靠左 */
.msg-row.ai {
  align-self: flex-start;
  flex-direction: row;
}

/* 用户消息靠右 */
.msg-row.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

/* 头像样式 */
.avatar {
  font-size: 20px;
  background: #eee;
  width: 35px;
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  flex-shrink: 0;
}

/* 气泡样式 */
.bubble {
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.7;
  white-space: normal; /* 保留换行 */
  word-break: break-word;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
}

/* AI 气泡颜色：白色 */
.ai .bubble {
  background-color: #ffffff;
  color: #333;
  border-radius: 0 12px 12px 12px;
  border: 1px solid #ebeef5;
}

/* 用户气泡颜色：蓝色 */
.user .bubble {
  background-color: #409eff;
  color: #ffffff;
  border-radius: 12px 0 12px 12px;
}

/* 打字中动画 */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 0;
}

.dot {
  width: 6px;
  height: 6px;
  background: #94a3b8;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) { animation-delay: 0s; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* RAG 来源标签样式 */
.source-tag {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #ddd;
  font-size: 11px;
  color: #888;
  font-style: italic;
}

</style>