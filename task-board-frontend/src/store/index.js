import { createPinia, defineStore } from 'pinia'
import api from '../api'

const pinia = createPinia()

// 从localStorage恢复用户信息
const savedUser = localStorage.getItem('user')
const savedToken = localStorage.getItem('token')
const savedRoles = localStorage.getItem('roles')
const savedPermissions = localStorage.getItem('permissions')
const savedMenus = localStorage.getItem('menus')

// 用户状态管理
export const useUserStore = defineStore('user', {
  state: () => ({
    user: savedUser ? JSON.parse(savedUser) : {
      id: null,
      username: '',
      name: '',
      role: '',
      email: ''
    },
    token: savedToken || '',
    roles: savedRoles ? JSON.parse(savedRoles) : [],
    permissions: savedPermissions ? JSON.parse(savedPermissions) : [],
    menus: savedMenus ? JSON.parse(savedMenus) : [],
    loading: false,
    error: null
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.user.role === 'admin',
    isPM: (state) => state.user.role === 'pm',
    isDev: (state) => state.user.role === 'dev',
    isViewer: (state) => state.user.role === 'viewer'
  },
  actions: {
    async login(username, password) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/auth/login', {
          username,
          password
        })
        this.user = response.data
        this.token = response.data.token
        localStorage.setItem('token', response.data.token)
        localStorage.setItem('user', JSON.stringify(response.data))
        
        // 登录成功后获取用户权限和菜单
        await this.fetchUserPermissions()
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '登录失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async register(userData) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/auth/register', userData)
        this.user = response.data
        this.token = response.data.token
        localStorage.setItem('token', response.data.token)
        localStorage.setItem('user', JSON.stringify(response.data))
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '注册失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async getCurrentUser() {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/auth/me')
        this.user = response.data
        localStorage.setItem('user', JSON.stringify(response.data))
        
        // 获取用户权限信息
        await this.fetchUserPermissions()
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '获取用户信息失败'
        // 清除无效token
        this.logout()
        throw error
      } finally {
        this.loading = false
      }
    },
    async fetchUserPermissions() {
      this.loading = true
      this.error = null
      try {
        console.log('开始获取用户权限信息')
        
        // 获取用户角色
        console.log('调用接口: /auth/me/roles')
        const rolesResponse = await api.get('/auth/me/roles')
        this.roles = rolesResponse.data
        localStorage.setItem('roles', JSON.stringify(rolesResponse.data))
        console.log('获取角色成功:', rolesResponse.data)
        
        // 获取用户权限
        console.log('调用接口: /auth/me/permissions')
        const permissionsResponse = await api.get('/auth/me/permissions')
        this.permissions = permissionsResponse.data
        localStorage.setItem('permissions', JSON.stringify(permissionsResponse.data))
        console.log('获取权限成功:', permissionsResponse.data)
        
        // 获取用户菜单
        console.log('调用接口: /menus/user')
        const menusResponse = await api.get('/menus/user')
        this.menus = menusResponse.data
        localStorage.setItem('menus', JSON.stringify(menusResponse.data))
        console.log('获取菜单成功:', menusResponse.data)
        
      } catch (error) {
        this.error = error.response?.data?.detail || '获取用户权限失败'
        console.error('获取用户权限失败:', error)
        console.error('错误详情:', error.response)
      } finally {
        this.loading = false
        console.log('权限获取流程结束')
      }
    },
    hasPermission(permissionCode) {
      // 管理员拥有所有权限
      if (this.user.username === 'admin') {
        return true
      }
      // 检查用户是否有该权限
      return this.permissions.some(p => p.code === permissionCode)
    },
    logout() {
      this.user = {
        id: null,
        username: '',
        name: '',
        role: '',
        email: ''
      }
      this.token = ''
      this.roles = []
      this.permissions = []
      this.menus = []
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('roles')
      localStorage.removeItem('permissions')
      localStorage.removeItem('menus')
    }
  }
})

// 任务状态管理
export const useTaskStore = defineStore('task', {
  state: () => ({
    tasks: [],
    statuses: [],
    totalTasks: 0,
    currentPage: 1,
    pageSize: 10,
    loading: false,
    error: null
  }),
  actions: {
    async fetchTasks(filters = {}, page = 1, pageSize = 10) {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/tasks', {
          params: {
            ...filters,
            page,
            page_size: pageSize
          }
        })
        this.tasks = response.data.items
        this.totalTasks = response.data.total
        this.currentPage = response.data.page
        // 保持前端设置的pageSize，不被后端返回值覆盖
        // this.pageSize = response.data.page_size
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '获取任务失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async fetchTask(id) {
      this.loading = true
      this.error = null
      try {
        const response = await api.get(`/tasks/${id}`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '获取任务详情失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async createTask(taskData) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/tasks', taskData)
        // 重新获取当前页数据以包含新创建的任务
        await this.fetchTasks({}, this.currentPage, this.pageSize)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '创建任务失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async updateTask(id, taskData) {
      this.loading = true
      this.error = null
      try {
        const response = await api.put(`/tasks/${id}`, taskData)
        // 重新获取当前页数据以包含更新后的任务
        await this.fetchTasks({}, this.currentPage, this.pageSize)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '更新任务失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async deleteTask(id) {
      this.loading = true
      this.error = null
      try {
        await api.delete(`/tasks/${id}`)
        // 重新获取当前页数据以移除已删除的任务
        await this.fetchTasks({}, this.currentPage, this.pageSize)
      } catch (error) {
        this.error = error.response?.data?.detail || '删除任务失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async updateTaskStatus(id, statusId) {
      this.loading = true
      this.error = null
      try {
        const response = await api.put(`/tasks/${id}/status`, {
          status_id: statusId
        })
        // 重新获取当前页数据以包含更新后的任务
        await this.fetchTasks({}, this.currentPage, this.pageSize)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '更新任务状态失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async updateTaskAssignee(id, assigneeId) {
      this.loading = true
      this.error = null
      try {
        const response = await api.put(`/tasks/${id}/assignee`, {
          assignee_id: assigneeId
        })
        // 重新获取当前页数据以包含更新后的任务
        await this.fetchTasks({}, this.currentPage, this.pageSize)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '分配任务失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async fetchStatuses() {
      this.loading = true
      this.error = null
      try {
        // 这里应该调用获取状态的API，暂时使用模拟数据
        // const response = await api.get('/statuses')
        // this.statuses = response.data
        
        // 模拟数据
        this.statuses = [
          { id: 1, name: '待办', order_index: 1, color: '#94a3b8' },
          { id: 2, name: '进行中', order_index: 2, color: '#3b82f6' },
          { id: 3, name: '已完成', order_index: 3, color: '#10b981' },
          { id: 4, name: '已暂停', order_index: 4, color: '#f59e0b' },
          { id: 5, name: '已取消', order_index: 5, color: '#ef4444' }
        ]
        return this.statuses
      } catch (error) {
        this.error = error.response?.data?.detail || '获取状态失败'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})

// 统计状态管理
export const useStatsStore = defineStore('stats', {
  state: () => ({
    taskStatusStats: [],
    userWorkloadStats: [],
    projectProgressStats: {},
    loading: false,
    error: null
  }),
  actions: {
    async fetchTaskStatusStats() {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/stats/task-status')
        this.taskStatusStats = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '获取任务状态统计失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async fetchUserWorkloadStats() {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/stats/user-workload')
        this.userWorkloadStats = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '获取用户工作量统计失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async fetchProjectProgressStats() {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/stats/project-progress')
        this.projectProgressStats = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '获取项目进度统计失败'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})

// 发版状态管理
export const useReleaseStore = defineStore('release', {
  state: () => ({
    releases: [],
    releaseTags: [],
    availableTasks: [],
    totalReleases: 0,
    currentPage: 1,
    pageSize: 10,
    loading: false,
    error: null
  }),
  actions: {
    // 发版标签相关
    async fetchReleaseTags() {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/releases/tags')
        this.releaseTags = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '获取发版标签失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async createReleaseTag(tagData) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/releases/tags', tagData)
        await this.fetchReleaseTags()
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '创建发版标签失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async updateReleaseTag(tagId, tagData) {
      this.loading = true
      this.error = null
      try {
        const response = await api.put(`/releases/tags/${tagId}`, tagData)
        await this.fetchReleaseTags()
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '更新发版标签失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async deleteReleaseTag(tagId) {
      this.loading = true
      this.error = null
      try {
        await api.delete(`/releases/tags/${tagId}`)
        await this.fetchReleaseTags()
      } catch (error) {
        this.error = error.response?.data?.detail || '删除发版标签失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 发版记录相关
    async fetchReleases(filters = {}, page = 1, pageSize = 10) {
      this.loading = true
      this.error = null
      try {
        const params = {
          ...filters,
          page,
          page_size: pageSize
        }
        const response = await api.get('/releases', { params })
        this.releases = response.data.items
        this.totalReleases = response.data.total
        this.currentPage = response.data.page
        // 保持前端设置的pageSize，不被后端返回值覆盖
        // this.pageSize = response.data.page_size
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '获取发版记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async fetchRelease(releaseId) {
      this.loading = true
      this.error = null
      try {
        const response = await api.get(`/releases/${releaseId}`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '获取发版详情失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async createRelease(releaseData) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/releases', releaseData)
        await this.fetchReleases({}, this.currentPage, this.pageSize)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '创建发版记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async updateRelease(releaseId, releaseData) {
      this.loading = true
      this.error = null
      try {
        const response = await api.put(`/releases/${releaseId}`, releaseData)
        await this.fetchReleases({}, this.currentPage, this.pageSize)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '更新发版记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async deleteRelease(releaseId) {
      this.loading = true
      this.error = null
      try {
        await api.delete(`/releases/${releaseId}`)
        await this.fetchReleases({}, this.currentPage, this.pageSize)
      } catch (error) {
        this.error = error.response?.data?.detail || '删除发版记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 可用任务相关
    async fetchAvailableTasks() {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/releases/available-tasks')
        this.availableTasks = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '获取可用任务失败'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})

export default pinia
