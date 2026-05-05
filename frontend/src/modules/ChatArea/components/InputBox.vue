<script setup>
import { ref } from 'vue'
import { Promotion } from '@element-plus/icons-vue'

const emit = defineEmits(['send'])
const user_input = ref('')

const onSend = () => {
    if (user_input.value.trim()) {
        emit('send', user_input.value)
        user_input.value = ''
    }
}

const handleEnter = (e) => {
  if (e.shiftKey) return
  onSend()
}

</script>

<template>
  <div class="input-wrapper">
    <div class="input-container">
      <el-input 
        v-model="user_input" 
        type="textarea"
        :autosize="{ minRows: 1, maxRows: 3 }"
        placeholder="请输入问题" 
        resize="none"
        class="input-box"
        @keyup.enter="onSend" 
        @keydown.enter.prevent="handleEnter"
      >
      </el-input>
      <div class="action-area">
        <el-button 
          type="primary" 
          circle
          class="send-btn"
          @click="onSend"
        >
          <template #icon>
            <el-icon><Promotion /></el-icon>
          </template>
        </el-button>
      </div>
    </div>
  </div>
 
</template>

<style scoped>
.input-wrapper {
  padding: 10px 20px 30px 20px; /* 底部多留一点空间，显得不拥挤 */
  background-color: transparent;
  display: flex;
  justify-content: center;
}
.input-container {
  width: 100%;
  max-width: 800px; /* 限制最大宽度，更有精致感 */
  background-color: #ffffff;
  border-radius: 23px; /* 大圆角 */
  padding: 8px 12px 8px 20px;
  display: flex;
  align-items: flex-end;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.02); /* 复合阴影 */
  border: 1px solid #e5e7eb;
  transition: box-shadow 0.3s, border-color 0.3s;
  margin: 0 auto;
  /* 居中对齐 */
 }
:deep(.input-box) .el-textarea__inner {
  border: none !important;
  box-shadow: none !important;
  padding: 8px 0;
  font-size: 15px;
  color: #374151;
  background: transparent;
  line-height: 1.6;
}
.action-area {
  display: flex;
  align-items: center;
  padding-bottom: 4px;
  margin-left: 8px;
}
.send-btn {
  width: 36px;
  height: 36px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  transform: scale(1);
}
</style>
