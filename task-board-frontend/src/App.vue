<template>
  <div class="app-container">
    <!-- 全局加载动画 -->
    <div v-if="globalLoading" class="global-loading">
      <div class="loading-content">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <div class="loading-text">{{ loadingText }}</div>
      </div>
    </div>
    
    <!-- 登录状态下显示完整布局 -->
    <template v-if="store.isLoggedIn && !globalLoading">
      <el-container style="height: 100vh;">
        <!-- 侧边栏 -->
        <el-aside :width="isCollapsed ? '64px' : '200px'" style="background-color: #001529; color: #fff; transition: width 0.3s ease; overflow: hidden;">
          <div class="logo" :style="{ padding: isCollapsed ? '20px 0' : '20px' }">
            <h2 v-if="!isCollapsed">{{ systemName }}</h2>
            <h2 v-else style="font-size: 16px;">{{ systemName.charAt(0) }}</h2>
          </div>
          
          <!-- 收起/展开按钮 -->
          <div class="collapse-btn" @click="toggleCollapse">
            <el-icon>
              <component :is="isCollapsed ? 'Expand' : 'Fold'" />
            </el-icon>
          </div>
          
          <!-- 菜单容器，带滚动条 -->
          <div class="menu-container" style="overflow-y: auto; overflow-x: hidden;" @contextmenu.prevent>
            <el-menu
              :default-active="activeMenu"
              :class="['el-menu-vertical-demo', { 'collapse': isCollapsed }]"
              :collapse="isCollapsed"
              background-color="#001529"
              text-color="#fff"
              active-text-color="#409EFF"
              router
              @contextmenu.prevent
            >
              <!-- 动态菜单渲染 -->
              <template v-if="store.menus.length > 0">
                <!-- 一级菜单 -->
                <template v-for="menu in store.menus">
                  <!-- 一级菜单：有子菜单 -->
                  <el-sub-menu v-if="menu.children && menu.children.length > 0" :key="menu.id" :index="menu.path || `menu-${menu.id}`">
                    <template #title>
                      <div @contextmenu.prevent="handleMenuContextMenu($event, menu)">
                        <el-icon v-if="menu.icon">
                          <component :is="menu.icon" />
                        </el-icon>
                        <span v-else class="icon-placeholder">•</span>
                        <span>{{ menu.name }}</span>
                      </div>
                    </template>
                    
                    <!-- 二级菜单 -->
                    <template v-for="child in menu.children">
                      <!-- 二级菜单：有子菜单 -->
                      <el-sub-menu v-if="child.children && child.children.length > 0" :key="child.id" :index="child.path || `submenu-${child.id}`">
                        <template #title>
                          <div @contextmenu.prevent="handleMenuContextMenu($event, child)">
                            <el-icon v-if="child.icon">
                              <component :is="child.icon" />
                            </el-icon>
                            <span v-else class="icon-placeholder">•</span>
                            <span>{{ child.name }}</span>
                          </div>
                        </template>
                        
                        <!-- 三级菜单 -->
                        <el-menu-item
                          v-for="grandchild in child.children"
                          :key="grandchild.id"
                          :index="grandchild.path || `menu-${grandchild.id}`"
                          @contextmenu.prevent="handleMenuContextMenu($event, grandchild)"
                        >
                          <el-icon v-if="grandchild.icon">
                            <component :is="grandchild.icon" />
                          </el-icon>
                          <template #title>{{ grandchild.name }}</template>
                        </el-menu-item>
                      </el-sub-menu>
                      
                      <!-- 二级菜单：无子菜单 -->
                      <el-menu-item 
                        v-else 
                        :key="child.id" 
                        :index="child.path || `submenu-${child.id}`"
                        @contextmenu.prevent="handleMenuContextMenu($event, child)"
                      >
                        <el-icon v-if="child.icon">
                          <component :is="child.icon" />
                        </el-icon>
                        <template #title>{{ child.name }}</template>
                      </el-menu-item>
                    </template>
                  </el-sub-menu>
                  
                  <!-- 一级菜单：无子菜单 -->
                  <el-menu-item 
                    v-else 
                    :key="menu.id" 
                    :index="menu.path || `menu-${menu.id}`"
                    @contextmenu.prevent="handleMenuContextMenu($event, menu)"
                  >
                    <el-icon v-if="menu.icon">
                      <component :is="menu.icon" />
                    </el-icon>
                    <template #title>{{ menu.name }}</template>
                  </el-menu-item>
                </template>
              </template>
              <!-- 默认菜单（当后端菜单未加载时显示） -->
              <template v-else>
                <!-- 加载中提示 -->
                <div style="padding: 20px; text-align: center; color: #ccc;">
                  <el-icon style="font-size: 24px; margin-bottom: 10px;"><Loading /></el-icon>
                  <div>菜单加载中...</div>
                </div>
              </template>

            </el-menu>
            
            <!-- 菜单右键菜单 -->
            <div v-if="menuContextMenuVisible" class="menu-context-menu" :style="{ left: menuContextMenuLeft + 'px', top: menuContextMenuTop + 'px' }">
              <div class="menu-context-menu-item" @click="openInNewTab">
                <el-icon><CopyDocument /></el-icon>
                <span>在新标签页打开</span>
              </div>
            </div>
          </div>
        </el-aside>

        <!-- 主内容区 -->
        <el-container >
          <!-- 顶部导航栏 -->
          <el-header  class="layout-header" style="background-color: #fff; /*border-bottom: 1px solid #eaeaea;*/ display: flex; flex-direction: column; align-items: stretch; height: auto;padding: 0 !important;">
            <div class="layout-navbars-container">
            <!-- 第一行：面包屑导航和用户信息 -->
            <div style="display: flex; justify-content: space-between; align-items: center;  height: 54px; border-bottom: 1px solid rgb(234 234 234 / 40%); background: var(--next-bg-topBar);">
              <!-- 面包屑导航 -->
              <el-breadcrumb separator="/" style="font-size: 14px;margin-left:10px;">
                <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
                <el-breadcrumb-item v-for="(item, index) in breadcrumbItems" :key="index" :to="item.path">{{ item.name }}</el-breadcrumb-item>
              </el-breadcrumb>
              
              <div class="header-right">
                <!-- 消息图标 -->
                <div class="message-icon" @click="toggleMessageDropdown">
                  <el-icon class="icon"><ChatDotRound /></el-icon>
                  <span v-if="unreadCount > 0" class="unread-badge">{{ unreadCount }}</span>
                </div>
                
                <el-dropdown >
                  <span class="user-info">
                    <el-avatar>{{ userInitial }}</el-avatar>
                    <span style="margin-left: 10px;">{{ userName }}</span>
                    <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                  </span>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item v-if="!isViewer" @click="handleSettings">个人设置</el-dropdown-item>
                      <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
            
            <!-- 第二行：Tab标签 -->
            <div style=" /*display:flex;*/justify-content: flex-start; align-items: center;padding: 4px 0; /*padding: 0 10px 5px; border-bottom: 1px solid #eaeaea; */ overflow: hidden; width: 100%;height:40px;">
              <!-- Tab标签 -->
              <div class="el-scrollbar" style="padding: 0 10px; " @contextmenu.prevent="handleTabContainerContextMenu">
                <el-tabs v-model="activeTab" type="card"  @tab-remove="handleTabRemove" @tab-click="handleTabClick">
                  <el-tab-pane
                    v-for="tab in tabs"
                    :key="tab.path"
                    :label="tab.title"
                    :name="tab.path"
                    closable
                  >
                  </el-tab-pane>
                </el-tabs>
                
                <!-- 右键菜单 -->
                <div v-if="contextMenuVisible" class="context-menu" :style="{ left: contextMenuLeft + 'px', top: contextMenuTop + 'px' }">
                  <div class="context-menu-item" @click="closeLeftTabs">关闭左侧标签</div>
                  <div class="context-menu-item" @click="closeRightTabs">关闭右侧标签</div>
                  <div class="context-menu-item" @click="closeAllTabs">关闭全部标签</div>
                  <div class="context-menu-divider"></div>
                  <div class="context-menu-item" @click="openTabInNewWindow">
                    <el-icon><CopyDocument /></el-icon>
                    <span>新标签页打开</span>
                  </div>
                </div>
              </div>
            </div>
            </div>
          </el-header>

          <!-- 消息列表弹窗 -->
          <div v-if="messageDropdownVisible" class="message-dropdown">
            <div class="message-header">
              <h3>消息中心</h3>
              <div class="message-tabs">
                <span 
                  :class="['tab', { active: activeMessageTab === 'unread' }]" 
                  @click="switchMessageTab('unread')"
                >
                  未读消息
                  <span v-if="unreadCount > 0" class="tab-badge">{{ unreadCount }}</span>
                </span>
                <span 
                  :class="['tab', { active: activeMessageTab === 'all' }]" 
                  @click="switchMessageTab('all')"
                >
                  全部消息
                </span>
              </div>
            </div>
            <div class="message-list">
              <div v-if="filteredMessages.length === 0" class="empty-messages">
                {{ activeMessageTab === 'unread' ? '暂无未读消息' : '暂无消息' }}
              </div>
              <div 
                v-for="message in filteredMessages" 
                :key="message.id" 
                :class="['message-item', { unread: !message.is_read }]"
                @click="handleMessageClick(message)"
              >
                <div class="message-content">
                  <div class="message-header-info">
                    <span class="message-type">{{ getMessageTypeText(message.message_type) }}</span>
                    <span class="message-time">{{ formatDate(message.created_at) }}</span>
                  </div>
                  <h4 class="message-title">{{ message.title }}</h4>
                  <p class="message-body">{{ message.content }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 内容区域 -->
          <el-main>
            <router-view v-slot="{ Component }">
              <transition name="fade" mode="out-in">
                <component :is="Component" />
              </transition>
            </router-view>
          </el-main>
        </el-container>
      </el-container>
    </template>
    
    <!-- 未登录状态下只显示路由内容（登录/注册页面） -->
    <template v-else-if="!store.isLoggedIn && !globalLoading">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from './store'
import { useAppStore } from './store/app'
import MenuItem from './components/MenuItem.vue'
import api from './api/index'
import { authApi } from './api/index'
import { ElMessageBox } from 'element-plus'
import { ChatDotRound, ArrowDown, Expand, Fold, Grid, HomeFilled, Document, Flag, List, DataAnalysis, User, Setting, Menu, Loading, CopyDocument } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const store = useUserStore()
const appStore = useAppStore()

// 侧边栏收起状态
const isCollapsed = ref(false)

// 切换侧边栏收起/展开
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

// 系统名称
const systemName = ref(localStorage.getItem('systemName') || '任务系统')

// 消息相关状态
const messageDropdownVisible = ref(false)
const activeMessageTab = ref('unread')
const messages = ref([])
const unreadCount = ref(0)
const messageDropdownTimer = ref(null)
const messagePollingTimer = ref(null)

// Tab标签相关状态
const tabs = ref([])
const activeTab = ref('')

// Tab右键菜单相关状态
const contextMenuVisible = ref(false)
const contextMenuLeft = ref(0)
const contextMenuTop = ref(0)
const currentTab = ref(null)

// 菜单右键菜单相关状态
const menuContextMenuVisible = ref(false)
const menuContextMenuLeft = ref(0)
const menuContextMenuTop = ref(0)
const currentMenu = ref(null)

// 全局加载状态（从appStore获取）
const globalLoading = computed(() => appStore.globalLoading)
const loadingText = computed(() => appStore.loadingText)

// 获取系统名称
const fetchSystemName = async () => {
  if (!store.isLoggedIn) return
  
  try {
    const response = await api.get('/settings')
    const settings = response.data
    const nameSetting = settings.find(s => s.key === 'site_name')
    if (nameSetting) {
      const newSystemName = nameSetting.value || '任务管理系统'
      systemName.value = newSystemName
      localStorage.setItem('systemName', newSystemName)
    }
  } catch (error) {
    console.error('获取系统名称失败:', error)
  }
}

// 应用启动时恢复登录状态
onMounted(async () => {
  const token = localStorage.getItem('token')
  if (token && !store.isLoggedIn) {
    try {
      await store.getCurrentUser()
      await fetchSystemName()
    } catch (error) {
      console.log('Token无效或已过期，需要重新登录')
    }
  }
  
  // 登录后获取消息
  if (store.isLoggedIn) {
    await fetchMessages()
  }
  
  // 点击外部关闭消息弹窗
  document.addEventListener('click', handleClickOutside)
  
  // 启动消息轮询（每5分钟）
  startMessagePolling()
  
  // 初始化Tab标签
  handleRouteChange()
  
  // 监听路由变化
  router.afterEach((to) => {
    handleRouteChange()
    
    // 如果跳转到/board页面，关闭全局加载动画
    if (to.path === '/board' && appStore.globalLoading) {
      setTimeout(() => {
        appStore.setGlobalLoading(false)
      }, 100)
    }
  })
})

// 监听登录状态变化，登录后获取系统名称
watch(() => store.isLoggedIn, async (newValue) => {
  if (newValue) {
    await fetchSystemName()
  }
})

// 清理事件监听器
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('click', closeContextMenu)
  document.removeEventListener('click', closeMenuContextMenu)
  if (messageDropdownTimer.value) {
    clearTimeout(messageDropdownTimer.value)
  }
  if (messagePollingTimer.value) {
    clearInterval(messagePollingTimer.value)
  }
})

// 计算当前激活的菜单
const activeMenu = computed(() => {
  return route.path
})

// 计算是否为仅查看角色
const isViewer = computed(() => {
  return store.user.role === 'viewer'
})

// 计算页面标题
  const pageTitle = computed(() => {
    const titles = {
      '/board': '任务看板',
      '/dashboard': '工作台',
      '/tasks': '任务管理',
      '/releases': '发版管理',
      '/requirements': '需求管理',
      '/stats': '统计分析',
      '/users': '用户管理',
      '/settings': '个人设置',
      '/system-settings': '系统设置',
      '/system/menus': '菜单管理',
      '/system/roles': '角色管理',
      '/system/permissions': '权限管理'
    }
    return titles[route.path] || ' ' //未匹配到路径时返回空字符串展示标题
  })

// 计算用户名和首字母
const userName = computed(() => {
  return store.user?.name || '未登录'
})

const userInitial = computed(() => {
  const name = store.user?.name || '未'
  return name.charAt(0).toUpperCase()
})

// 计算面包屑导航项
const breadcrumbItems = computed(() => {
  const path = route.path
  const items = []
  
  // 首先尝试从菜单树中获取完整的路径
  const menuPath = findMenuPath(path, store.menus)
  if (menuPath && menuPath.length > 0) {
    return menuPath
  }
  
  // 如果菜单树中没有找到，使用默认的面包屑导航
  if (path === '/board') {
    items.push({ name: '任务看板', path: '/board' })
  } else if (path === '/dashboard') {
    items.push({ name: '工作台', path: '/dashboard' })
  } else if (path === '/tasks') {
    items.push({ name: '任务管理', path: '/tasks' })
  } else if (path === '/releases') {
    items.push({ name: '发版管理', path: '/releases' })
  } else if (path === '/requirements') {
    items.push({ name: '需求管理', path: '/requirements' })
  } else if (path === '/stats') {
    items.push({ name: '统计分析', path: '/stats' })
  } else if (path === '/users') {
    items.push({ name: '用户管理', path: '/users' })
  } else if (path === '/settings') {
    items.push({ name: '个人设置', path: '/settings' })
  } else if (path === '/system-settings') {
    items.push({ name: '系统设置', path: '/system-settings' })
  } else if (path === '/system/menus') {
    items.push({ name: '系统管理', path: '/system' })
    items.push({ name: '菜单管理', path: '/system/menus' })
  } else if (path === '/system/roles') {
    items.push({ name: '系统管理', path: '/system' })
    items.push({ name: '角色管理', path: '/system/roles' })
  } else if (path === '/system/permissions') {
    items.push({ name: '系统管理', path: '/system' })
    items.push({ name: '权限管理', path: '/system/permissions' })
  } else if (path.startsWith('/task/')) {
    items.push({ name: '任务管理', path: '/tasks' })
    items.push({ name: '任务详情', path: path })
  } else if (path.startsWith('/release/')) {
    items.push({ name: '发版管理', path: '/releases' })
    items.push({ name: '发版详情', path: path })
  }
  
  return items
})

// 从菜单树中查找菜单路径
const findMenuPath = (path, menus, pathStack = []) => {
  for (const menu of menus) {
    if (menu.path === path) {
      // 找到目标菜单，返回完整路径
      return [...pathStack, { name: menu.name, path: menu.path }]
    }
    if (menu.children && menu.children.length > 0) {
      // 递归查找子菜单
      const found = findMenuPath(path, menu.children, [...pathStack, { name: menu.name, path: menu.path }])
      if (found) {
        return found
      }
    }
  }
  return null
}

// 计算根级菜单
const rootMenus = computed(() => {
  return store.menus.filter(menu => {
    // 根级菜单是那些没有父菜单的菜单
    return !menu.parent_id
  })
})

// 计算过滤后的消息
const filteredMessages = computed(() => {
  if (activeMessageTab.value === 'unread') {
    return messages.value.filter(msg => !msg.is_read)
  }
  return messages.value
})

// 处理路由变化，添加Tab标签
const handleRouteChange = () => {
  const path = route.path
  const title = getPageTitle(path)
  
  // 只添加有效的页面（排除登录、注册等）
  if (title && title !== ' ' && !path.includes('login') && !path.includes('register')) {
    // 检查是否已存在该Tab
    const existingTab = tabs.value.find(tab => tab.path === path)
    if (!existingTab) {
      // 添加新Tab
      tabs.value.push({ path, title })
    }
    // 设置当前激活的Tab
    activeTab.value = path
  }
}

// 根据路径获取页面标题
const getPageTitle = (path) => {
  // 首先从菜单树中查找
  const menuTitle = findMenuTitle(path, store.menus)
  if (menuTitle) {
    return menuTitle
  }
  
  // 如果菜单树中没有找到，使用默认标题
  const titles = {
    '/board': '任务看板',
    '/dashboard': '工作台',
    '/tasks': '任务管理',
    '/releases': '发版管理',
    '/requirements': '需求管理',
    '/stats': '统计分析',
    '/users': '用户管理',
    '/settings': '个人设置',
    '/system-settings': '系统设置',
    '/system/menus': '菜单管理',
    '/system/roles': '角色管理',
    '/system/permissions': '权限管理'
  }
  
  // 处理任务详情和发版详情
  if (path.startsWith('/task/')) {
    return '任务详情'
  }
  if (path.startsWith('/release/')) {
    return '发版详情'
  }
  
  return titles[path] || pageTitle.value
}

// 从菜单树中查找菜单标题
const findMenuTitle = (path, menus) => {
  for (const menu of menus) {
    if (menu.path === path) {
      return menu.name
    }
    if (menu.children && menu.children.length > 0) {
      const found = findMenuTitle(path, menu.children)
      if (found) {
        return found
      }
    }
  }
  return null
}

// 处理Tab点击
const handleTabClick = (tab) => {
  router.push(tab.paneName)
}

// 处理Tab关闭
const handleTabRemove = (path) => {
  const index = tabs.value.findIndex(tab => tab.path === path)
  if (index > -1) {
    tabs.value.splice(index, 1)
    // 如果关闭的是当前激活的Tab，激活前一个或第一个
    if (activeTab.value === path) {
      if (tabs.value.length > 0) {
        activeTab.value = tabs.value[Math.max(0, index - 1)].path
        router.push(activeTab.value)
      } else {
        router.push('/board')
      }
    }
  }
}

// 处理Tab右键菜单
const handleTabContainerContextMenu = (event) => {
  event.preventDefault()
  
  // 获取点击的tab元素
  const target = event.target
  const tabElement = target.closest('.el-tabs__item')
  
  if (!tabElement) {
    // 如果点击的不是tab，不显示右键菜单
    return
  }
  
  // 获取tab的索引
  const tabElements = document.querySelectorAll('.el-tabs__item')
  const tabIndex = Array.from(tabElements).indexOf(tabElement)
  
  if (tabIndex >= 0 && tabIndex < tabs.value.length) {
    currentTab.value = tabs.value[tabIndex]
    contextMenuLeft.value = event.clientX
    contextMenuTop.value = event.clientY
    contextMenuVisible.value = true
    
    // 点击外部关闭右键菜单
    setTimeout(() => {
      document.addEventListener('click', closeContextMenu)
    }, 10)
  }
}

// 关闭右键菜单
const closeContextMenu = () => {
  contextMenuVisible.value = false
  document.removeEventListener('click', closeContextMenu)
}

// 关闭左侧标签
const closeLeftTabs = () => {
  if (!currentTab.value) return
  
  const currentIndex = tabs.value.findIndex(tab => tab.path === currentTab.value.path)
  if (currentIndex > 0) {
    // 保留当前标签和右侧标签
    const tabsToKeep = tabs.value.slice(currentIndex)
    tabs.value = tabsToKeep
    
    // 确保当前标签仍然激活
    if (!tabs.value.some(tab => tab.path === activeTab.value)) {
      activeTab.value = currentTab.value.path
      router.push(activeTab.value)
    }
  }
  
  closeContextMenu()
}

// 关闭右侧标签
const closeRightTabs = () => {
  if (!currentTab.value) return
  
  const currentIndex = tabs.value.findIndex(tab => tab.path === currentTab.value.path)
  if (currentIndex < tabs.value.length - 1) {
    // 保留当前标签和左侧标签
    const tabsToKeep = tabs.value.slice(0, currentIndex + 1)
    tabs.value = tabsToKeep
  }
  
  closeContextMenu()
}

// 关闭全部标签
const closeAllTabs = () => {
  tabs.value = []
  activeTab.value = ''
  router.push('/board')
  closeContextMenu()
}

// 在新标签页打开Tab
const openTabInNewWindow = () => {
  if (!currentTab.value) return
  
  const url = window.location.origin + currentTab.value.path
  window.open(url, '_blank')
  closeContextMenu()
}

// 处理菜单右键菜单
const handleMenuContextMenu = (event, menu) => {
  // 只对有组件路径的菜单项显示右键菜单（有component的菜单才是可打开页面的菜单）
  if (!menu.component || menu.component === '' ) {
    event.preventDefault()
    return
  }
  
  event.preventDefault()
  
  currentMenu.value = menu
  menuContextMenuLeft.value = event.clientX
  menuContextMenuTop.value = event.clientY
  menuContextMenuVisible.value = true
  
  // 点击外部关闭右键菜单
  setTimeout(() => {
    document.addEventListener('click', closeMenuContextMenu)
  }, 10)
}

// 关闭菜单右键菜单
const closeMenuContextMenu = () => {
  menuContextMenuVisible.value = false
  document.removeEventListener('click', closeMenuContextMenu)
}

// 在新标签页打开菜单
const openInNewTab = () => {
  if (!currentMenu.value || !currentMenu.value.path) {
    return
  }
  
  const url = window.location.origin + currentMenu.value.path
  window.open(url, '_blank')
  closeMenuContextMenu()
}

// 处理个人设置
const handleSettings = () => {
  router.push('/settings')
}

// 处理退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '退出确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 显示退出中动画
    appStore.setGlobalLoading(true, '退出中...')
    
    try {
      // 调用后端logout API撤销会话
      await authApi.logout()
    } catch (error) {
      // 即使API调用失败，也要继续执行退出登录操作
      console.error('退出登录API调用失败:', error)
    } finally {
      // 清除Tab标签状态
      tabs.value = []
      activeTab.value = ''
      // 清除本地状态
      store.logout()
      // 直接跳转到登录页，不调用任何其他API
      router.push('/login')
      // 延迟关闭加载动画，确保用户看到退出中提示
      setTimeout(() => {
        appStore.setGlobalLoading(false)
      }, 500)
    }
  } catch {
    // 用户点击取消，不执行任何操作
  }
}

// 消息相关方法
const toggleMessageDropdown = () => {
  messageDropdownVisible.value = !messageDropdownVisible.value
  if (messageDropdownVisible.value) {
    fetchMessages()
  }
}

const switchMessageTab = (tab) => {
  activeMessageTab.value = tab
}

const fetchMessages = async () => {
  if (!store.isLoggedIn) return
  
  try {
    const response = await api.get('/messages')
    messages.value = response.data
    unreadCount.value = response.data.filter(msg => !msg.is_read).length
  } catch (error) {
    console.error('获取消息失败:', error)
  }
}

const handleMessageClick = async (message) => {
  // 标记为已读
  if (!message.is_read) {
    try {
      await api.put(`/messages/${message.id}/read`)
      message.is_read = true
      unreadCount.value--
    } catch (error) {
      console.error('标记消息已读失败:', error)
    }
  }
  
  // 如果有跳转路径，根据路径类型决定跳转行为
  if (message.redirect_path) {
    // 先关闭消息弹窗
    messageDropdownVisible.value = false
    
    // 判断是否为完整URL
    if (message.redirect_path.startsWith('http://') || message.redirect_path.startsWith('https://')) {
      // 完整URL，在新标签页打开
      window.open(message.redirect_path, '_blank')
    } else {
      // 内部路径，在当前页面正常打开
      setTimeout(() => {
        router.push(message.redirect_path)
      }, 100)
    }
  }
}

const getMessageTypeText = (type) => {
  const typeMap = {
    'task_message': '任务消息',
    'system_message': '系统消息',
    'release_message': '发版消息',
    'defect_message': '缺陷消息'
  }
  return typeMap[type] || type
}

const startMessagePolling = () => {
  // 清除可能存在的旧定时器
  if (messagePollingTimer.value) {
    clearInterval(messagePollingTimer.value)
  }
  
  // 设置新的轮询定时器（5分钟）
  messagePollingTimer.value = setInterval(async () => {
    if (store.isLoggedIn) {
      try {
        await fetchMessages()
      } catch (error) {
        console.error('轮询获取消息失败:', error)
      }
    }
  }, 300000) // 5分钟 = 300000毫秒
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleClickOutside = (event) => {
  const messageIcon = document.querySelector('.message-icon')
  const messageDropdown = document.querySelector('.message-dropdown')
  
  if (messageIcon && messageDropdown && !messageIcon.contains(event.target) && !messageDropdown.contains(event.target)) {
    messageDropdownVisible.value = false
  }
}
</script>

<style scoped>
/* 全局重置样式 */
:root {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  overflow-x: hidden;
}

.app-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.el-container {
  overflow: hidden;
}

.el-main {
  padding: 0;
  overflow-y: auto;
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #002140;
}

.logo h2 {
  margin: 0;
  font-size: 18px;
}

/* 全局加载动画样式 */
.global-loading {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-content {
  text-align: center;
  background-color: #fff;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-icon {
  font-size: 48px;
  color: #409EFF;
  animation: spin 1s linear infinite;
}

.loading-text {
  font-size: 16px;
  color: #606266;
  margin-top: 16px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 侧边栏滚动条样式 */
.el-aside {
  overflow: hidden;
}

.menu-container {
  height: calc(100vh - 120px);
}

.menu-container::-webkit-scrollbar {
  width: 6px;
}

.menu-container::-webkit-scrollbar-track {
  background: #001529;
  border-radius: 3px;
}

.menu-container::-webkit-scrollbar-thumb {
  background: #2c3e50;
  border-radius: 3px;
  transition: all 0.3s;
}

.menu-container::-webkit-scrollbar-thumb:hover {
  background: #409EFF;
}

.menu-container::-webkit-scrollbar-corner {
  background: #001529;
}

/* Firefox浏览器滚动条 */
.menu-container {
  scrollbar-width: thin;
  scrollbar-color: #2c3e50 #001529;
}

.menu-container:hover {
  scrollbar-color: #409EFF #001529;
}

.collapse-btn {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px;
  cursor: pointer;
  color: #fff;
  transition: all 0.3s ease;
  border-bottom: 1px solid #002140;
}

.collapse-btn:hover {
  background-color: #002140;
  color: #409EFF;
}

.collapse-btn .el-icon {
  font-size: 18px;
}

.el-menu-vertical-demo {
  border-right: none;
}

/* 菜单收起时的样式 */
.el-menu-vertical-demo.collapse .el-sub-menu__title span:not(.icon-placeholder) {
  display: none !important;
}

/* 确保子菜单展开时文字显示 */
.el-menu-vertical-demo.collapse .el-sub-menu__popup span {
  display: inline !important;
}

/* 确保子菜单标题在展开时显示文字（仅二级及以下菜单） */
.el-menu-vertical-demo.collapse .el-sub-menu.is-opened .el-sub-menu .el-sub-menu__title span:not(.icon-placeholder) {
  display: inline !important;
}

/* 确保一级菜单在收起状态下不显示文字 */
.el-menu-vertical-demo.collapse > .el-sub-menu > .el-sub-menu__title span:not(.icon-placeholder) {
  display: none !important;
}

/* 确保一级菜单即使在hover或展开时也不显示文字 */
.el-menu-vertical-demo.collapse > .el-sub-menu:hover > .el-sub-menu__title span:not(.icon-placeholder),
.el-menu-vertical-demo.collapse > .el-sub-menu.is-opened > .el-sub-menu__title span:not(.icon-placeholder) {
  display: none !important;
}

.header-title h1 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

/* 右键菜单样式 */
.context-menu {
  position: fixed;
  background-color: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 1000;
  min-width: 120px;
}

.context-menu-item {
  padding: 8px 12px;
  cursor: pointer;
  font-size: 13px;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 8px;
}

.context-menu-item:hover {
  background-color: #ecf5ff;
  color: #409eff;
}

.context-menu-item .el-icon {
  font-size: 14px;
}

.context-menu-divider {
  height: 1px;
  background-color: #e4e7ed;
  margin: 4px 0;
}

/* 菜单右键菜单样式 */
.menu-context-menu {
  position: fixed;
  background-color: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 1000;
  min-width: 120px;
}

.menu-context-menu-item {
  padding: 8px 12px;
  cursor: pointer;
  font-size: 13px;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 8px;
}

.menu-context-menu-item:hover {
  background-color: #ecf5ff;
  color: #409eff;
}

.menu-context-menu-item .el-icon {
  font-size: 14px;
}

/* Tab标签样式 */
.tab-container {
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  position: relative;
  margin: 0 auto;
}

.tab-container::-webkit-scrollbar {
  height: 4px;
}

.tab-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 2px;
}

.tab-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.tab-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.tab-container :deep(.el-tabs__header) {
  margin: 0;
  padding: 0;
  height: 32px;
  display: flex;
  align-items: center;
  border: none;
  width: 100%;
}

.tab-container :deep(.el-tabs__nav-wrap) {
  display: flex;
  align-items: center;
  width: 100%;
  overflow: visible;
  flex: 1;
}

.tab-container :deep(.el-tabs__nav-scroll) {
  display: flex;
  align-items: center;
  width: 100%;
  overflow: visible;
  flex: 1;
}

.tab-container :deep(.el-tabs__nav) {
  display: flex;
  align-items: center;
  width: auto;
  border: none;
  gap: 5px;
  flex-shrink: 0;
}

.tab-container :deep(.el-tabs__item) {
  height: 32px;
  line-height: 32px;
  font-size: 14px;
  padding: 0 15px;
  background-color: #f5f7fa;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  margin: 0;
  transition: all 0.3s;
  flex-shrink: 0;
}

.tab-container :deep(.el-tabs__item:hover) {
  background-color: #ecf5ff;
  border-color: #c6e2ff;
  color: #409eff;
}

.tab-container :deep(.el-tabs__item.is-active) {
  background-color: #409eff;
  border-color: #409eff;
  color: #fff;
}

.tab-container :deep(.el-tabs__active-bar) {
  display: none;
}

.tab-container :deep(.el-tabs__close-btn) {
  margin: 0 0 0 8px;
  font-size: 14px;
  color: inherit;
}

.tab-container :deep(.el-tabs__item.is-active .el-tabs__close-btn) {
  color: #fff;
}

.tab-container :deep(.el-tabs__close-btn:hover) {
  color: #909399;
}

.tab-container :deep(.el-tabs__item.is-active .el-tabs__close-btn:hover) {
  color: #fff;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  outline: none;
}

.user-info:focus {
  outline: none;
}

.user-info:focus-visible {
  outline: none;
}

/* 移除下拉菜单的焦点边框 */
.header-right :deep(.el-dropdown__trigger) {
  outline: none;
}

.header-right :deep(.el-dropdown__trigger:focus) {
  outline: none;
}

.header-right :deep(.el-dropdown__trigger:focus-visible) {
  outline: none;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 消息相关样式 */
.message-icon {
  position: relative;
  cursor: pointer;
  font-size: 20px;
  color: #606266;
  padding: 5px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.message-icon:hover {
  background-color: #f5f7fa;
  color: #409EFF;
}

.unread-badge {
  position: absolute;
  top: 0;
  right: 0;
  min-width: 16px;
  height: 16px;
  line-height: 16px;
  font-size: 12px;
  color: #fff;
  background-color: #F56C6C;
  border-radius: 8px;
  text-align: center;
  padding: 0 4px;
  transform: translate(50%, -50%);
}

.message-dropdown {
  position: absolute;
  top: 60px;
  right: 20px;
  width: 400px;
  max-height: 500px;
  background-color: #fff;
  border: 1px solid #eaeaea;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 1000;
  overflow: hidden;
}

.message-header {
  padding: 15px;
  border-bottom: 1px solid #eaeaea;
}

.message-header h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #333;
}

.message-tabs {
  display: flex;
  gap: 10px;
}

.tab {
  padding: 5px 15px;
  border-radius: 15px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.tab:hover {
  background-color: #f5f7fa;
}

.tab.active {
  background-color: #ecf5ff;
  color: #409EFF;
}

.tab-badge {
  position: absolute;
  top: -5px;
  right: 5px;
  min-width: 16px;
  height: 16px;
  line-height: 16px;
  font-size: 12px;
  color: #fff;
  background-color: #F56C6C;
  border-radius: 8px;
  text-align: center;
  padding: 0 4px;
}

.message-list {
  max-height: 400px;
  overflow-y: auto;
}

.empty-messages {
  padding: 40px 20px;
  text-align: center;
  color: #909399;
  font-size: 14px;
}

.message-item {
  padding: 15px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.3s ease;
}

.message-item:hover {
  background-color: #f5f7fa;
}

.message-item.unread {
  background-color: #f0f9ff;
}

.message-header-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.message-type {
  font-size: 12px;
  color: #409EFF;
  background-color: #ecf5ff;
  padding: 2px 8px;
  border-radius: 10px;
}

.message-time {
  font-size: 12px;
  color: #909399;
}

.message-title {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.message-body {
  margin: 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 滚动条样式 */
.message-list::-webkit-scrollbar {
  width: 6px;
}

.message-list::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.message-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.message-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 主内容区滚动条样式 */
.el-main::-webkit-scrollbar {
  width: 8px;
}

.el-main::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.el-main::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.el-main::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.el-tabs--card > .el-tabs__header .el-tabs__nav {
  border-bottom: 1px solid #eaeaea;
}

.el-tabs--card > .el-tabs__header .el-tabs__item {
  border-radius: 4px 4px 0 0;
  margin-right: 8px;
}

.el-tabs--card > .el-tabs__header .el-tabs__item.is-active {
  border-bottom-color: #fff;
}


</style>
