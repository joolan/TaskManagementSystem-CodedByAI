<template>
  <div class="welcome-container">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <el-icon :size="48" color="#409EFF"><HomeFilled /></el-icon>
          <h1>欢迎来到{{ systemName }}</h1>
        </div>
      </template>
      
      <div class="welcome-content">
        <div class="welcome-message">
          <h2>您好，{{ userName }}!</h2>
          <p>您已成功登录系统，请从左侧菜单选择您要访问的功能模块。</p>
        </div>
        
        <div class="quick-links" v-if="quickAccessMenus.length > 0">
          <h3>快速访问</h3>
          <el-row :gutter="20">
            <el-col :span="8" v-for="menu in quickAccessMenus" :key="menu.id">
              <el-card 
                shadow="hover" 
                class="quick-link-card"
                @click="navigateTo(menu.path)"
              >
                <div class="quick-link-content">
                  <el-icon :size="32" :color="menu.color || '#409EFF'">
                    <component :is="menu.icon || 'Document'" />
                  </el-icon>
                  <span class="quick-link-title">{{ menu.name }}</span>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
        
        <div class="tips">
          <h3>使用提示</h3>
          <ul>
            <li>点击左侧菜单可以展开/收起子菜单</li>
            <li>鼠标悬停在菜单上可以查看完整菜单名称</li>
            <li>点击菜单项即可打开对应的页面</li>
            <li>已打开的页面会在顶部以标签页形式展示</li>
            <li>可以右键点击标签页进行关闭、刷新等操作</li>
          </ul>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store'
import { HomeFilled, Document, List, DataAnalysis, Setting, Menu } from '@element-plus/icons-vue'

const router = useRouter()
const store = useUserStore()

const systemName = ref(localStorage.getItem('systemName') || '任务系统')
const userName = computed(() => store.user?.username || '用户')

// 快速访问菜单
const quickAccessMenus = ref([])

// 初始化快速访问菜单
const initQuickAccessMenus = () => {
  const menus = store.menus || []
  
  // 获取所有一级菜单 (排除系统管理等后台管理菜单)
  const availableMenus = menus.filter(menu => {
    // 只获取有 component 的菜单 (可以打开页面的菜单)
    if (!menu.component || menu.component === '') {
      return false
    }
    
    // 排除系统管理相关菜单
    if (menu.path && (
      menu.path.startsWith('/system') || 
      menu.path === '/users' ||
      menu.path === '/settings' ||
      menu.path === '/system-settings'
    )) {
      return false
    }
    
    return true
  })
  
  // 定义菜单图标和颜色映射
  const menuConfig = {
    '任务看板': { icon: 'HomeFilled', color: '#67C23A' },
    '工作台': { icon: 'DataAnalysis', color: '#409EFF' },
    '任务管理': { icon: 'List', color: '#E6A23C' },
    '发版管理': { icon: 'Flag', color: '#F56C6C' },
    '需求管理': { icon: 'Document', color: '#909399' },
    '统计分析': { icon: 'DataAnalysis', color: '#67C23A' }
  }
  
  // 取前 6 个菜单作为快速访问
  quickAccessMenus.value = availableMenus.slice(0, 6).map(menu => {
    const config = menuConfig[menu.name] || {}
    return {
      id: menu.id,
      name: menu.name,
      path: menu.path,
      icon: config.icon || 'Document',
      color: config.color || '#409EFF'
    }
  })
}

// 导航到指定页面
const navigateTo = (path) => {
  router.push(path)
}

onMounted(() => {
  initQuickAccessMenus()
})
</script>

<style scoped>
.welcome-container {
  padding: 20px;
  height: calc(100vh - 84px);
  overflow-y: auto;
  background-color: #f5f7fa;
}

.welcome-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.card-header h1 {
  margin: 0;
  font-size: 28px;
  color: #303133;
}

.welcome-content {
  padding: 20px 0;
}

.welcome-message {
  text-align: center;
  margin-bottom: 40px;
}

.welcome-message h2 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 16px;
}

.welcome-message p {
  font-size: 16px;
  color: #606266;
  margin: 0;
}

.quick-links {
  margin-bottom: 40px;
}

.quick-links h3 {
  font-size: 18px;
  color: #303133;
  margin-bottom: 20px;
  text-align: center;
}

.quick-link-card {
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 20px;
}

.quick-link-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.quick-link-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px 0;
}

.quick-link-title {
  font-size: 16px;
  color: #303133;
  font-weight: 500;
}

.tips {
  background-color: #f5f7fa;
  padding: 24px;
  border-radius: 8px;
}

.tips h3 {
  font-size: 18px;
  color: #303133;
  margin-bottom: 16px;
}

.tips ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tips li {
  font-size: 14px;
  color: #606266;
  padding: 8px 0;
  padding-left: 20px;
  position: relative;
}

.tips li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #409EFF;
  font-size: 16px;
}
</style>
