import { createRouter, createWebHistory } from 'vue-router'
import { userState } from '@/store/userState'

const HomeView = () => import('@/views/HomeView.vue');
const LoginView = () => import('@/views/LoginView.vue');
const Dashborad = () => import('@/views/admin/Dashborad.vue');

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [{
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Dashborad,
    children: [
      {
        path: 'users',
        name: 'UserManage',
        component: () => import('@/views/admin/UserManage/UserManage.vue'),
      },
      {
        path: 'knowledge',
        name: 'KnowledgeBase',
        component: () => import('@/views/admin/KonwledgeBase/KownledgeBase.vue'),
      },
      {
        path: 'resources',
        name: 'ResourceManage',
        component: () => import('@/views/admin/ResourceManage/ResourceManage.vue'),
      }
    ]
  },
  ],
})

router.beforeEach((to) => {
  // 统一从 localStorage 或内存获取最新的 token
  const token = localStorage.getItem('token') || userState.token
  const info = JSON.parse(localStorage.getItem('userInfo')) || userState.userInfo

  // 1. 拦截非法进入后台
  if (to.path.startsWith('/admin')) {
    if (!token || info.role !== 'admin') {
      return '/login' // 没权限直接回登录
    }
  }

  // 2. 防止已登录用户重复进登录页（管理员注册新用户除外）
  if (to.path === '/login' && token && to.query.mode !== 'register') {
    return info.role === 'admin' ? '/admin' : '/'
  }

  return true // 放行
})

export default router
