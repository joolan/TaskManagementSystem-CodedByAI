<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <h1>404</h1>
      <h2>页面不存在</h2>
      <p>抱歉，您访问的页面不存在或已被移除。</p>
      <el-button type="primary" @click="goToHome">返回首页</el-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToHome = () => {
  router.push('/board')
}
</script>

<style scoped>
.not-found-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.not-found-content {
  text-align: center;
  padding: 40px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.not-found-content h1 {
  font-size: 72px;
  font-weight: 600;
  color: #1890ff;
  margin-bottom: 20px;
}

.not-found-content h2 {
  font-size: 24px;
  margin-bottom: 15px;
}

.not-found-content p {
  font-size: 16px;
  color: #666;
  margin-bottom: 30px;
}
</style>
