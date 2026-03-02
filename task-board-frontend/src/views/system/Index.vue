<template>
  <div class="system-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统管理</span>
        </div>
      </template>
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical-demo"
        @select="handleMenuSelect"
      >
        <el-menu-item index="menus">
          <el-icon><Menu /></el-icon>
          <span>菜单管理</span>
        </el-menu-item>
        <el-menu-item index="roles">
          <el-icon><UserFilled /></el-icon>
          <span>角色管理</span>
        </el-menu-item>
        <el-menu-item index="permissions">
          <el-icon><Lock /></el-icon>
          <span>权限管理</span>
        </el-menu-item>
      </el-menu>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Menu, UserFilled, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const activeMenu = computed(() => {
  const path = route.path
  if (path.includes('menus')) return 'menus'
  if (path.includes('roles')) return 'roles'
  if (path.includes('permissions')) return 'permissions'
  return 'menus'
})

const handleMenuSelect = (key) => {
  router.push(`/system/${key}`)
}

onMounted(() => {
  // 默认跳转到菜单管理
  if (route.path === '/system') {
    router.push('/system/menus')
  }
})
</script>

<style scoped>
.system-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-menu {
  border-right: none;
}

.el-menu-item {
  height: 60px;
  line-height: 60px;
  font-size: 16px;
}

.el-icon {
  margin-right: 12px;
  font-size: 18px;
}
</style>