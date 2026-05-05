<script setup>
import { userInfo, logout, goHome } from '@/store/userState.js'
</script>

<template>
  <el-container style="height: 100vh;">
    <!-- 左侧菜单 -->
    <el-aside width="200px" style="background-color: #304156; color: white;">
      <div style="padding: 20px; text-align: center; font-weight: bold;">管理员控制台</div>
      <el-menu background-color="#304156" text-color="#fff" default-active="$router.path" router>
        <el-menu-item index="/admin/knowledge">📚 知识库管理</el-menu-item>
        <el-menu-item index="/admin/users">👥 用户权限管理</el-menu-item>
        <el-menu-item index="/admin/resources">🚀 资源管理</el-menu-item>
      </el-menu>
    </el-aside>
    
    <!-- 右侧内容区 -->
    <el-container>
      <el-header class="admin-header">
        <span class="greeting">  欢迎回来，{{ userInfo.name }}</span>
        <div class="header-actions">
          <el-button size="small" @click="goHome">返回首页</el-button>
          <el-button type="danger" size="small" plain @click="logout">退出后台</el-button>
        </div>
      </el-header>
      <el-main style="background-color: #f0f2f5;">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 24px 0 28px;
}

.greeting {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 10px;
  margin-right: 8px;
}
</style>

