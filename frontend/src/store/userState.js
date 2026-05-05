import { ref, reactive } from "vue";
import router from "@/router";
import { roleLogin } from "@/api/login"
import { clearAllConvoState } from "@/store/convoSwitch"

// --- 保持你原有的变量名 ---
export const isLoggedIn = ref(!!localStorage.getItem('token'))

export const userInfo = ref(JSON.parse(localStorage.getItem('userInfo')) || {
    name: '未登录',
    avatar: '🤔',
    role: 'guest',
})

// 这里的 userState 内部同步
export const userState = reactive({
  token: localStorage.getItem('token') || '',
  userInfo: userInfo.value 
})

export async function login(username, password) {
  try {
    const response = await roleLogin(username, password)
    // 只要后端返回了 token，就执行持久化
    if (response.token) {
      const token = response.token
      const data = {
        id: response.id,
        name: response.name,
        avatar: response.avatar,
        role: response.role,
      }

      // 1. 更新内存状态
      userState.token = token
      userState.userInfo = data
      isLoggedIn.value = true
      userInfo.value = data

      // 2. 写入本地存储（解决刷新丢失的关键）
      localStorage.setItem('token', token)
      localStorage.setItem('userInfo', JSON.stringify(data))

      // 3. 执行跳转
      if (data.role === 'admin') {
        router.push('/admin/knowledge')
      } else {
        router.push('/')
      }
      return true
    }
    return false
  } catch (error) {
    console.error('登录失败:', error)
    return false
  }
}

export function goHome() {
  router.push('/')
}

export function logout() {
  // 1. 清理内存
  userState.token = ''
  userState.userInfo = { name: '未登录', role: 'guest', avatar: '🤔' }
  isLoggedIn.value = false
  userInfo.value = userState.userInfo

  // 2. 清理本地存储
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')

  // 4. 清理对话业务数据
  clearAllConvoState()

  // 3. 返回首页
  router.push('/')
}