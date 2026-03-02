<template>
  <div class="settings-container">
    <div class="settings-content">
      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <span>个人信息</span>
          </div>
        </template>
        <el-form :model="userInfo" :rules="userInfoRules" ref="userInfoFormRef" label-width="100px">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="userInfo.username" disabled></el-input>
          </el-form-item>
          <el-form-item label="姓名" prop="name">
            <el-input v-model="userInfo.name"></el-input>
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="userInfo.email"></el-input>
          </el-form-item>
          <el-form-item label="角色" prop="role">
            <el-input v-model="userInfo.role" disabled></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveUserInfo">保存</el-button>
          </el-form-item>
        </el-form>
      </el-card>
      
      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <span>修改密码</span>
          </div>
        </template>
        <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
          <el-form-item label="当前密码" prop="currentPassword">
            <el-input type="password" v-model="passwordForm.currentPassword" placeholder="请输入当前密码" show-password></el-input>
          </el-form-item>
          <el-form-item label="新密码" prop="newPassword">
            <el-input type="password" v-model="passwordForm.newPassword" placeholder="请输入新密码" show-password></el-input>
          </el-form-item>
          <el-form-item label="确认新密码" prop="confirmPassword">
            <el-input type="password" v-model="passwordForm.confirmPassword" placeholder="请确认新密码" show-password></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="changePassword">保存</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useUserStore } from '../store'

const userStore = useUserStore()

const userInfoFormRef = ref(null)
const passwordFormRef = ref(null)

const userInfo = reactive({
  username: '',
  name: '',
  email: '',
  role: ''
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const userInfoRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const saveUserInfo = async () => {
  if (!userInfoFormRef.value) return
  
  try {
    await userInfoFormRef.value.validate()
    // 这里应该调用更新用户信息的API
    console.log('保存用户信息:', userInfo)
  } catch (error) {
    console.error('保存用户信息失败:', error)
  }
}

const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    // 这里应该调用修改密码的API
    console.log('修改密码:', passwordForm)
    // 重置表单
    Object.assign(passwordForm, {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
  } catch (error) {
    console.error('修改密码失败:', error)
  }
}

const fetchUserInfo = async () => {
  try {
    // 从store中获取用户信息
    const user = userStore.user
    Object.assign(userInfo, {
      username: user.username,
      name: user.name,
      email: user.email,
      role: user.role
    })
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

onMounted(async () => {
  await fetchUserInfo()
})
</script>

<style scoped>
.settings-container {
  padding: 10px;
  background-color: #ffffff;
}

.settings-content {
  max-width: 800px;
}

.settings-card {
  margin-bottom: 15px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
