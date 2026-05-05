import axios from "axios"
import { userState } from "@/store/userState"

const request = axios.create({
    baseURL: 'http://127.0.0.1:8000',
    timeout: 300000,
})

request.interceptors.response.use(
    response => {
        return response.data
    }
)

export default request


const service = axios.create({
  baseURL: 'http://127.0.0.1:8000'
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
