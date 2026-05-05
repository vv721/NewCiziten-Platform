<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchUsers, deleteUser, resetUserPassword } from '@/api/admin.js'
import { userState } from '@/store/userState'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const router = useRouter()
const userList = ref([])
const keyword = ref('')
const roleFilter = ref('')
const loading = ref(false)

const currentAdminId = userState.userInfo?.id

const stats = computed(() => ({
  total: userList.value.length,
  adminCount: userList.value.filter((u) => u.role === 'admin').length,
  totalMsg: userList.value.reduce((sum, u) => sum + (u.msg_count || 0), 0),
}))

const loadUsers = async () => {
  loading.value = true
  try {
    const params = {}
    if (keyword.value) params.keyword = keyword.value
    if (roleFilter.value) params.role = roleFilter.value
    userList.value = await fetchUsers(params)
  } finally {
    loading.value = false
  }
}

const handleAddUser = () => {
  router.push({ path: '/login', query: { mode: 'register' } })
}

const handleDelete = async (row) => {
  if (row.id === currentAdminId) {
    ElMessage.warning('不能删除自己的账户')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${row.username}" 吗？`,
      '删除确认',
      { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' },
    )
    await deleteUser(row.id)
    ElMessage.success(`已删除用户 ${row.username}`)
    loadUsers()
  } catch { /* cancelled */ }
}

const handleResetPassword = async (row) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入新密码（至少4位）', '重置密码', {
      confirmButtonText: '确定', cancelButtonText: '取消', inputType: 'password',
    })
    if (value) {
      await resetUserPassword(row.id, value)
      ElMessage.success(`已重置 ${row.username} 的密码`)
    }
  } catch { /* cancelled */ }
}

onMounted(loadUsers)
</script>

<template>
  <div class="user-manage-container">
    <el-card shadow="never" class="main-card">
      <div class="toolbar">
        <div class="search-row">
          <el-input
            v-model="keyword" placeholder="搜索用户名" clearable :prefix-icon="Search"
            style="width: 220px" @clear="loadUsers" @keyup.enter="loadUsers"
          />
          <el-select v-model="roleFilter" placeholder="角色筛选" clearable style="width: 120px" @change="loadUsers">
            <el-option label="admin" value="admin" />
            <el-option label="user" value="user" />
          </el-select>
          <el-button type="primary" size="small" @click="loadUsers">查询</el-button>
        </div>
        <div class="actions-row">
          <span class="stats-hint">
            共 {{ stats.total }} 位用户，{{ stats.adminCount }} 名管理员，{{ stats.totalMsg }} 条消息
          </span>
          <el-button type="primary" size="small" @click="handleAddUser">添加用户</el-button>
        </div>
      </div>

      <el-table
        :data="userList" border v-loading="loading" style="width: 100%; margin-top: 14px"
        :empty-text="keyword || roleFilter ? '没有匹配的用户' : '暂无用户数据'"
      >
        <el-table-column prop="id" label="ID" width="65" align="center" />
        <el-table-column prop="username" label="用户名" min-width="140" />
        <el-table-column prop="role" label="角色" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" size="small" effect="light">
              {{ row.role }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="convo_count" label="会话" width="70" align="center" />
        <el-table-column prop="msg_count" label="消息" width="70" align="center" />
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" plain @click="handleResetPassword(row)">重置密码</el-button>
            <el-button
              size="small" type="danger" plain
              :disabled="row.id === currentAdminId"
              @click="handleDelete(row)"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.user-manage-container {
  padding: 10px;
}

.main-card {
  border-radius: 8px;
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.search-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.actions-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stats-hint {
  font-size: 13px;
  color: #909399;
}
</style>
