import axios from "axios"
import { userState } from "@/store/userState"

// 后端地址统一走环境变量，默认本机 8000 端口（见 frontend/.env.example）
export const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const request = axios.create({
    baseURL: BASE_URL,
    timeout: 300000,
})

request.interceptors.response.use(
    response => {
        return response.data
    }
)

export default request


const service = axios.create({
  baseURL: BASE_URL
})

service.interceptors.request.use(config => {
  if (userState.token) {
    config.headers['Authorization'] = `Bearer ${userState.token}`
  }
  return config
})

// 响应拦截：处理 401 (Token 过期或非法)
service.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response && error.response.status === 401) {
      // 发现 Token 验证失败，强制前端登出并跳转
      userState.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export { service }
