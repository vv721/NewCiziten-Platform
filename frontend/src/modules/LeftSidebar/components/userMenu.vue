<script setup>
import { isLoggedIn, userInfo, logout, userState } from '@/store/userState'
import { useRouter } from 'vue-router'

const router = useRouter()

const handleMenuClick = (command) => {
    if (command === 'login') {
        router.push('/login')
    } else if (command === 'logout') {
        logout()
    } else if (command === 'admin') {
        goToAdmin()
    }
}

const goToAdmin = () => {
    router.push('/admin/knowledge')
}

</script>

<template>
    <el-dropdown class="menuTrigger" trigger="click" @command="handleMenuClick">
        <div>
            <div style="user-select: none;">
                <span>{{ userInfo.avatar }}</span>
                <span>{{ userInfo.name }}</span>
            </div>
        </div>

        <template #dropdown>
            <el-dropdown-menu>
                <el-dropdown-item v-if="!isLoggedIn" command="login">登录</el-dropdown-item>
                <el-dropdown-item
                 v-if="userInfo.role === 'admin'" command="admin">管理员中心</el-dropdown-item>
                <el-dropdown-item command="logout">退出</el-dropdown-item>
            </el-dropdown-menu>
        </template>
    </el-dropdown>
</template>

<style scoped>
    .menuTrigger {
        display: flex;
        width: 100%;
        height: 50px;
        align-items: center;
        justify-content: center;
        background-color: #fff;
    }
</style>
