<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { login } from '@/store/userState.js'
import { useFocusNavigation } from '@/hooks/useFocusNavigation.js'
import { registerApi } from '@/api/login.js'
import { ElMessage } from 'element-plus'

const route = useRoute()
const { handleKeyDown } = useFocusNavigation()

const usernameRef = ref(null)
const passwordRef = ref(null)

const username = ref('')
const password = ref('')

const isLogin = ref(true)

onMounted(() => {
  if (route.query.mode === 'register') {
    isLogin.value = false
  }
})
const loginForm = reactive({ username: '', password: '' })
const registerForm = reactive({ username: '', password: '', confirmPassword: '' })

const toggleAuth = () => {
    isLogin.value = !isLogin.value
}

const handleLogin = async () => {
    const success = await login(username.value, password.value)
    if (!success) alert('账号或密码错误')
}

const handleRegister = async () => {
    if (!registerForm.username || !registerForm.password) {
        return ElMessage.warning('请填写完整信息');
    }
    if (registerForm.password !== registerForm.confirmPassword) {
        return ElMessage.error('两次输入密码不一致')
    }

    try {
        const res = await registerApi({
            username: registerForm.username,
            password: registerForm.password,
        })
        if (res.status === 'success') {
            ElMessage.success('注册成功')
            toggleAuth()
            registerForm.username = '';
            registerForm.password = '';
            registerForm.confirmPassword = '';
        } else {
            ElMessage.error(res.message)
        }
    } catch (error) {
        ElMessage.error('注册失败')
    }     
}

</script>

<template>
    <div class="auth-container">
        <div class="auth-window">
            <div class="auth-slider" :class="{'show-register': !isLogin}">
                <div class="auth-section login-section">
                    <h2 class="auth-title">登录</h2>

                    <el-form :model="loginForm">
                        <el-input ref="usernameRef" v-model="username" placeholder="请输入账号" 
                         style="margin-bottom: 20px;" @keydown="handleKeyDown($event, passwordRef, null)" />
                        <el-input ref="passwordRef" v-model="password" placeholder="请输入密码" 
                         type="password" show-password style="margin-bottom: 20px;"
                         @keyup.enter="handleLogin" @keydown="handleKeyDown($event, null, usernameRef)" />
                    <el-button type="primary" class="submit-btn" @click="handleLogin">登录</el-button>
                    </el-form>

                    <div class="auth-footer">
                        还没有账户？<span class="link-text" @click="toggleAuth">立即注册</span>
                    </div>
                </div>

                <div class="auth-section register-section">
                    <h2 class="auth-title">注册</h2>
                    <el-form :model="registerForm">
                        <el-input v-model="registerForm.username" placeholder="请输入用户名" />
                        <el-input v-model="registerForm.password" type="password" placeholder="请输入密码"
                         style="margin-bottom: 10px; margin-top: 10px;" />
                        <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请确认密码" />
                        <el-button type="primary" class="submit-btn" @click="handleRegister">注册</el-button>
                    </el-form>
                    <div class="auth-footer">
                        已有账户？<span class="link-text" @click="toggleAuth">返回登录</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.auth-container {
    height: 100vh;
    width: 100vw;
    background: url('/images/login-bg.jpg') center/cover;
    display: flex;
    align-items: center;
    justify-content: center;
}
.auth-window {
    width: 400px;
    height: 500px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
}
.auth-slider {
    display: flex;
    width: 200%;
    height: 100%;
    transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.show-register {
    transform: translateX(-50%);
}
.auth-section {
    width: 50%;
    padding: 40px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.auth-title {
    text-align: center;
    font-size: 2rem;
    margin-bottom: 50px;
}
.submit-btn {
  width: 100%;
  margin-top: 20px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid white;
}
.auth-footer {
  text-align: center;
  margin-top: 30px;
  font-size: 0.9rem;
  color: #272323;
}
.link-text {
    cursor: pointer;
    color: #8892e9;
}
</style>
