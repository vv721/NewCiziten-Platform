<script setup>
import InputBox from './components/InputBox.vue'
import MessageList from './components/MessageList.vue'
import GreetingView from './components/GreetingView.vue'
import ModeCapsules from './components/ModeCapsules.vue'
import ChatHeader from './components/ChatHeader.vue'

import { ref, nextTick, watch } from 'vue'
import { sendToAIStream } from '@/api/chat'
import { activeConvoId, refreshConvoList, messages } from '@/store/convoSwitch'
import { userState } from '@/store/userState'
import { uiState } from '@/store/uiState'


const scrollContainer = ref(null)

watch(() => messages.value, async () => {
  await nextTick()
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
  }
}, { deep: true })

const handleSend = async (text) => {
  if (!text || !text.trim()) return
  messages.value.push({ role: 'user', content: text })

  messages.value.push({ role: 'ai', content: '', sources: [] })
  const aiMsg = messages.value[messages.value.length - 1]

  try {
    await sendToAIStream(text, activeConvoId.value, userState.userInfo.id, {
      onMeta: (event) => {
        if (event.ui_command) {
          let data
          if (event.ui_command === 'SHOW_TRACE') data = event.docs_info
          else if (event.ui_command === 'SHOW_PROCESS') data = event.process_data
          else if (event.ui_command === 'SHOW_MAP') data = event.map_data
          uiState.dispatchCommand(event.ui_command, data)
        }
        aiMsg.sources = event.sources || []
      },
      onToken: (token) => {
        aiMsg.content += token
      },
      onDone: (event) => {
        if (!activeConvoId.value && event.convo_id) {
          activeConvoId.value = event.convo_id
          refreshConvoList(userState.userInfo.id)
        }
      },
    })
  } catch (error) {
    console.error('AI response failed:', error)
    aiMsg.content = '抱歉，系统暂时无法处理您的请求，请稍后再试。'
    aiMsg.isError = true
  }
}
</script>

<template>
  <div class="chat-container">
    <div class="chat-header">
      <ChatHeader />
    </div>
    <div class="message-container" ref="scrollContainer">
      <GreetingView @send="handleSend" />
      <MessageList :messages="messages" />
    </div>
    <div class="input-wrapper">
      <div class="capsules-wapper">
        <ModeCapsules />
      </div>
      <InputBox @send="handleSend" />
    </div>
  </div>
</template>

<style scoped>
.chat-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  overflow: hidden;
}
.chat-header {
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.7);
  color: #fff;
}
.message-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}
.input-wrapper {
  height: 20% ;
  padding: 10px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}
.capsules-wapper {
  margin-bottom: 16px;
}
</style>