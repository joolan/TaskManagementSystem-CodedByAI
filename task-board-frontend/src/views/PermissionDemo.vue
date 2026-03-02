<template>
  <div class="permission-demo">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>权限演示页面</span>
        </div>
      </template>
      
      <div class="demo-content">
        <p>此页面用于演示权限控制功能，以下按钮会根据用户权限动态显示：</p>
        
        <div class="button-group">
          <el-button type="primary" v-permission="'demo:query'">
            <el-icon><Search /></el-icon>
            查询列表
          </el-button>
          <el-button type="success" v-permission="'demo:export'">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
          <el-button type="warning" v-permission="'demo:edit'">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button type="info" v-permission="'demo:updateHours'">
            <el-icon><Timer /></el-icon>
            修改工时
          </el-button>
        </div>
        
        <div class="permission-info">
          <h4>当前用户权限：</h4>
          <el-tag v-for="permission in userPermissions" :key="permission.code" size="small" style="margin: 5px;">
            {{ permission.code }}
          </el-tag>
          <el-empty v-if="userPermissions.length === 0" description="暂无权限" />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../../store'
import { Search, Download, Edit, Timer } from '@element-plus/icons-vue'

const userStore = useUserStore()
const userPermissions = computed(() => userStore.permissions)

onMounted(() => {
  // 可以在这里加载用户权限信息
  if (userStore.isLoggedIn && userStore.permissions.length === 0) {
    userStore.fetchUserPermissions()
  }
})
</script>

<style scoped>
.permission-demo {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.demo-content {
  padding: 20px;
}

.button-group {
  display: flex;
  gap: 10px;
  margin: 20px 0;
  flex-wrap: wrap;
}

.permission-info {
  margin-top: 30px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.permission-info h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #333;
}
</style>