import { ref } from "vue";
import { getHistoryMessages, getConvos, renameConvo, deleteConvo } from "@/api/chat";

export const activeTab = ref('mainchat')
export const activeConvoId = ref(null)
export const convoList = ref([])

export const messages = ref([])

export async function switchConvo(id, messageRef) {
    activeConvoId.value = id
    try {
    const history = await getHistoryMessages(id)
    messages.value = history.map(m => ({
      role: m.role,
      content: m.content,
      sources: m.sources ? JSON.parse(m.sources) : [] 
    }))
  } catch (error) {
    console.error("加载历史消息失败:", error)
    messages.value = []
  }
}

export async function refreshConvoList(userId) {
  const data = await getConvos(userId)
  convoList.value = data
}

export function prepNewChat() {
   if (activeConvoId.value === null && messages.value.length === 0) {
    return; 
  }
   activeConvoId.value = null;  // 1. 关键：将 ID 设为 null，触发后端的“自动创建”逻辑
   messages.value = [];         // 2. 清空当前屏幕上的所有气泡
   activeTab.value = 'mainchat'; // 3. 确保 UI 切回实时对话模式
}

export async function handleRename(id, newTitle) {
  try {
    await renameConvo(id, newTitle)
    // 成功后更新本地列表，无需重新请求后端
    const convo = convoList.value.find(c => c.id === id)
    if (convo) convo.title = newTitle
  } catch (e) {
    console.error("重命名失败")
  }
}

export async function handleDelete(id) {
  try {
    await deleteConvo(id)
    // 1. 从本地列表中移除
    convoList.value = convoList.value.filter(c => c.id !== id)
    
    // 2. [关键点]：如果删掉的是当前正打开的会话，立即清空聊天区
    if (activeConvoId.value === id) {
      prepNewChat()
    }
  } catch (e) {
    console.error("删除失败")
  }
}

export function clearAllConvoState() {
  convoList.value = [];       // 清空左侧列表
  messages.value = [];        // 清空当前气泡
  activeConvoId.value = null; // 重置会话ID
  activeTab.value = 'mainchat';// 回到初始页
  console.log("对话业务数据已彻底清空");
}