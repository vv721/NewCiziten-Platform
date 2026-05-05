<script setup>
import { convoList, activeConvoId, refreshConvoList, switchConvo, prepNewChat, handleRename, handleDelete } from '@/store/convoSwitch'
import { userState } from '@/store/userState'
import { onMounted } from 'vue'
import { ChatDotRound, More, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'

import userMenu from './components/userMenu.vue'
import SidebarHeader from './components/SidebarHeader.vue'

const initConvoList = async () => {
    const userId = userState.userInfo.id
    if (!userId) {
        convoList.value = []; 
        return;
    }
    try {
        await refreshConvoList(userId)
    } catch (e) {
        console.error("刷新会话列表失败:", error)
    }
}

const handleCommand = (command, item) => {
  if (command === 'rename') {
    // 弹出重命名输入框
    ElMessageBox.prompt('请输入新的会话名称', '重命名', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValue: item.title,
    }).then(({ value }) => {
      if (value) handleRename(item.id, value)
    })
  } else if (command === 'delete') {
    // 弹出删除确认框
    ElMessageBox.confirm(
      '确定要删除该会话及其所有历史记录吗？',
      '删除确认',
      { confirmButtonText: '删除', type: 'warning' }
    ).then(() => {
      handleDelete(item.id)
      ElMessage.success('已成功删除会话')
    })
  }
}

onMounted(() => {
    initConvoList()
})
</script>

<template>
    <div class="leftSidebar-container">
        <SidebarHeader @new-chat="prepNewChat" />

        <div class="sidebar-history">
            <div class="history-label">最近会话</div>
            <div
             v-for="convo in convoList" 
             :key="convo.id"
             :class="['history-item', { active: activeConvoId === convo.id }]"
             @click="switchConvo(convo.id)">
                <el-icon><ChatDotRound /></el-icon>
                <span class="title">{{ convo.title }}</span>
                <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, convo)">
                    <div class="more-btn" @click.stop>
                        <el-icon><More /></el-icon>
                    </div>
                    <template #dropdown>
                        <el-dropdown-item command="rename" :icon="Edit">重命名</el-dropdown-item>
                        <el-dropdown-item command="delete" :icon="Delete" style="color: #f56c6c;">删除</el-dropdown-item>
                    </template>
                </el-dropdown>
            </div>
        </div>

        <div class="sidebar-footer">
            <userMenu />
        </div>
    </div>
</template>

<style scoped>
.leftSidebar-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa; /* 浅灰色背景，区分中栏 */
  border-right: 1px solid #e5e7eb;
}

/* 历史记录滚动区 */
.sidebar-history {
  flex: 1;
  overflow-y: auto;
  padding: 0 12px;
}

.history-label {
  font-size: 12px;
  color: #909399;
  padding: 8px 12px;
  margin-top: 10px;
}

.history-item {
  position: relative; /* 方便定位 */
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  color: #606266;
  transition: all 0.2s;
}

.history-item:hover {
  background-color: #ebedef;
}

.history-item:hover .more-btn {
  opacity: 1;
}

.more-btn:hover {
  background-color: #dcdfe6;
  color: #303133;
}

.history-item.active {
  background-color: #e2e8f0;
  color: #409eff;
  font-weight: 500;
}

.history-item .title {
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1; /* 撑满中间，把按钮推向右侧 */
  margin-right: 4px;
}

.more-btn {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, opacity 0.2s;
  opacity: 0; /* 初始状态隐藏 */
  color: #909399;
}

/* 底部区域 */
.sidebar-footer {
  padding: 12px;
  border-top: 1px solid #e5e7eb;
  margin-top: auto; /* 确保始终在底部 */
}

/* 滚动条美化 */
.sidebar-history::-webkit-scrollbar {
  width: 4px;
}
.sidebar-history::-webkit-scrollbar-thumb {
  background: #dbdcde;
  border-radius: 10px;
}

.el-dropdown-selfdefine.el-tooltip__trigger:focus-visible {
  outline: none;
}
:deep(.el-dropdown) {
  line-height: 0; /* 修复图标偏移 */
}
</style>
