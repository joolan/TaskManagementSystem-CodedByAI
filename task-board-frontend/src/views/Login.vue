<template>
  <div class="login-container">
    <div class="login-form-wrapper">
      <h1 class="login-title">任务管理系统</h1>
      <h2 class="login-subtitle"></h2>
      
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input type="password" v-model="loginForm.password" placeholder="请输入密码" show-password @keyup.enter="handleLogin"></el-input>
        </el-form-item>
        <el-form-item >
          <el-button type="primary" @click="handleLogin" :loading="loading">登录</el-button>

          <el-button type="link" @click="goToRegister" style="margin-left:0px;">注册</el-button>
        </el-form-item>
      </el-form>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../store'
import { useAppStore } from '../store/app'
import axios from 'axios'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref(null)
const loading = ref(false)
const error = ref('')

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    loading.value = true
    error.value = ''
    
    // 立即显示全局加载状态
    const appStore = useAppStore()
    appStore.setGlobalLoading(true, '登录中...')
    
    await userStore.login(loginForm.username, loginForm.password)
    
    // 登录成功后，等待菜单加载完成
    if (userStore.menus.length > 0) {
      // 先跳转路由，不关闭加载动画
      router.push('/board')
    } else {
      // 菜单未加载完成，显示全局加载状态
      appStore.setGlobalLoading(true, '加载菜单中...')
      
      // 等待菜单加载完成
      const checkMenuLoaded = setInterval(() => {
        if (userStore.menus.length > 0) {
          clearInterval(checkMenuLoaded)
          // 先跳转路由，不关闭加载动画
          router.push('/board')
        }
      }, 100)
      
      // 防止无限等待，设置超时
      setTimeout(() => {
        clearInterval(checkMenuLoaded)
        // 先跳转路由，不关闭加载动画
        router.push('/board')
      }, 5000)
    }
  } catch (err) {
    let errorMessage = '登录失败，请检查用户名和密码'
    if (err.response?.data?.detail) {
      // 处理后端返回的错误信息
      errorMessage = err.response.data.detail
      error.value = err.response.data.detail
    } else if (userStore.error) {
      // 使用userStore中的错误信息
      errorMessage = userStore.error
      error.value = userStore.error
    } else {
      error.value = '登录失败，请检查用户名和密码'
    }
    console.error('登录失败:', err)
    console.error('userStore.error:', userStore.error)
    // 使用ElMessage显示错误信息
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
    // 关闭全局加载状态
    const appStore = useAppStore()
    appStore.setGlobalLoading(false)
  }
}

const goToRegister = async () => {
  try {
    // 检查是否允许注册
    const response = await axios.get('/api/settings/allow_registration')
    const allowRegistration = response.data.value === 'true'
    
    if (allowRegistration) {
      router.push('/register')
    } else {
      error.value = '当前系统不允许注册，请联系管理员'
    }
  } catch (err) {
    console.error('检查注册权限失败:', err)
    // 如果获取设置失败，仍然允许跳转到注册页面，由后端进行最终验证
    router.push('/register')
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.login-form-wrapper {
  width: 400px;
  padding: 40px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-title {
  text-align: center;
  margin-bottom: 10px;
  color: #1890ff;
}

.login-subtitle {
  text-align: center;
  margin-bottom: 30px;
  color: #666;
}

.error-message {
  margin-top: 20px;
  padding: 10px;
  background-color: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 4px;
  color: #f5222d;
  text-align: center;
}

.el-form-item {
  margin-bottom: 20px;
}

.el-button {
  width: 100%;
  margin-bottom: 10px;
  display: block;
}
</style>
