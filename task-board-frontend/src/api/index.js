import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 从本地存储获取token
    const token = localStorage.getItem('token')
    // 检查是否是登录或注册请求，如果是则不需要token
    const isAuthRequest = config.url.includes('/auth/login') || config.url.includes('/auth/register')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    } else if (!isAuthRequest) {
      // 如果不是登录或注册请求且没有token，不发送请求，直接返回一个拒绝的Promise
      return Promise.reject(new Error('No token found'))
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response
  },
  error => {
    // 处理错误
    if (error.response) {
      // 服务器返回错误状态码
      switch (error.response.status) {
        case 401:
          // 未授权，清除token并跳转到登录页
          // 但如果当前已经在登录页面，则不执行跳转，避免刷新
          if (window.location.pathname !== '/login') {
            localStorage.removeItem('token')
            window.location.href = '/login'
          }
          break
        case 403:
          // 禁止访问
          console.error('禁止访问')
          break
        case 404:
          // 资源不存在
          console.error('资源不存在')
          break
        case 500:
          // 服务器错误
          console.error('服务器错误')
          break
        default:
          console.error('请求失败')
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      console.error('网络错误，无法连接到服务器')
    } else {
      // 请求配置错误
      console.error('请求配置错误')
    }
    return Promise.reject(error)
  }
)

// 认证相关API
export const authApi = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  getCurrentUser: () => api.get('/auth/me'),
  getUsers: (params) => api.get('/auth/users', { params }),
  getUsersBasic: (config) => api.get('/auth/users-basic', config),
  getUser: (id, config) => api.get(`/auth/users/${id}`, config),
  createUser: (data) => api.post('/auth/users', data),
  updateUser: (id, data) => api.put(`/auth/users/${id}`, data),
  deleteUser: (id) => api.delete(`/auth/users/${id}`),
  updateUserPassword: (id, data) => api.put(`/auth/users/${id}/password`, data),
  unlockUser: (id) => api.put(`/auth/users/${id}/unlock`),
  getUserSessions: (userId, config) => api.get(`/auth/users/${userId}/sessions`, config),
  revokeSession: (sessionId) => api.delete(`/auth/sessions/${sessionId}`),
  logout: () => api.post('/auth/logout'),
  assignRolesToUser: (userId, roleIds) => api.post(`/auth/users/${userId}/roles`, roleIds),
  getUserMenus: (userId, config) => api.get(`/auth/users/${userId}/menus`, config),
  assignUserMenus: (userId, menuIds) => api.post(`/auth/users/${userId}/menus`, menuIds),
  getUserPermissions: (userId, config) => api.get(`/auth/users/${userId}/permissions`, config),
  assignUserPermissions: (userId, permissionIds) => api.post(`/auth/users/${userId}/permissions`, permissionIds)
}

// 任务相关API
export const taskApi = {
  getTasks: (params) => api.get('/tasks', { params }),
  createTask: (data) => api.post('/tasks', data),
  getTask: (id) => api.get(`/tasks/${id}`),
  updateTask: (id, data) => api.put(`/tasks/${id}`, data),
  deleteTask: (id) => api.delete(`/tasks/${id}`),
  updateTaskStatus: (id, statusId) => api.put(`/tasks/${id}/status`, { status_id: statusId }),
  updateTaskAssignee: (id, assigneeId) => api.put(`/tasks/${id}/assignee`, { assignee_id: assigneeId }),
  
  // 任务关注API
  followTask: (id) => api.post(`/tasks/${id}/follow`),
  unfollowTask: (id) => api.delete(`/tasks/${id}/follow`),
  getTaskFollowStatus: (id) => api.get(`/tasks/${id}/follow-status`),
  getTaskFollowers: (id) => api.get(`/tasks/${id}/followers`),
  
  // 任务工时API
  addTaskHours: (id, data) => api.post(`/tasks/${id}/hours`, data),
  getTaskHours: (id) => api.get(`/tasks/${id}/hours`)
}

// 评论相关API
export const commentApi = {
  getTaskComments: (taskId) => api.get(`/tasks/${taskId}/comments`),
  addTaskComment: (taskId, data) => api.post(`/tasks/${taskId}/comments`, data),
  deleteComment: (id) => api.delete(`/comments/${id}`)
}

// 附件相关API
export const attachmentApi = {
  getTaskAttachments: (taskId) => api.get(`/tasks/${taskId}/attachments`),
  uploadTaskAttachment: (taskId, formData) => api.post(`/tasks/${taskId}/attachments`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  deleteAttachment: (id) => api.delete(`/attachments/${id}`)
}

// 统计相关API
export const statsApi = {
  getTaskStatusStats: () => api.get('/stats/task-status'),
  getUserWorkloadStats: () => api.get('/stats/user-workload'),
  getProjectProgressStats: () => api.get('/stats/project-progress')
}

// 发版相关API
export const releaseApi = {
  // 发版标签API
  getReleaseTags: () => api.get('/releases/tags'),
  createReleaseTag: (data) => api.post('/releases/tags', data),
  updateReleaseTag: (id, data) => api.put(`/releases/tags/${id}`, data),
  deleteReleaseTag: (id) => api.delete(`/releases/tags/${id}`),
  
  // 发版记录API
  getReleases: (params) => api.get('/releases', { params }),
  createRelease: (data) => api.post('/releases', data),
  getRelease: (id) => api.get(`/releases/${id}`),
  updateRelease: (id, data) => api.put(`/releases/${id}`, data),
  deleteRelease: (id) => api.delete(`/releases/${id}`),
  
  // 可用任务API（用于关联到发版）
  getAvailableTasks: () => api.get('/releases/available-tasks'),
  
  // 发版关注API
  followRelease: (id) => api.post(`/releases/${id}/follow`),
  unfollowRelease: (id) => api.delete(`/releases/${id}/follow`),
  getFollowStatus: (id) => api.get(`/releases/${id}/follow-status`),
  getReleaseFollowers: (id) => api.get(`/releases/${id}/followers`)
}

// 消息相关API
export const messageApi = {
  getMessages: (params) => api.get('/messages', { params }),
  getUnreadCount: () => api.get('/messages/unread-count'),
  markAsRead: (id) => api.put(`/messages/${id}/read`)
}

// 需求标签相关API
export const requirementTagApi = {
  getRequirementTags: () => api.get('/requirement-tags'),
  createRequirementTag: (data) => api.post('/requirement-tags', data),
  updateRequirementTag: (id, data) => api.put(`/requirement-tags/${id}`, data),
  deleteRequirementTag: (id) => api.delete(`/requirement-tags/${id}`)
}

// 需求池相关API
export const requirementApi = {
  getRequirements: (params) => api.get('/requirements', { params }),
  createRequirement: (data) => api.post('/requirements', data),
  getRequirement: (id) => api.get(`/requirements/${id}`),
  updateRequirement: (id, data) => api.put(`/requirements/${id}`, data),
  deleteRequirement: (id) => api.delete(`/requirements/${id}`),
  convertToTask: (id, data) => api.post(`/requirements/${id}/convert-to-task`, data)
}

// 数据库备份还原相关API
export const databaseApi = {
  // 数据库备份
  backupDatabase: () => api.post('/database/backup'),
  // 数据库还原
  restoreDatabase: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/database/restore', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  // 获取备份列表
  getBackups: () => api.get('/database/backups'),
  // 删除备份
  deleteBackup: (filename) => api.delete(`/database/backups/${filename}`),
  // 校验备份文件
  validateBackup: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/database/validate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

// 备忘录相关API
export const memoApi = {
  getMyMemos: () => api.get('/memos'),
  createMemo: (data) => api.post('/memos', data),
  getMemo: (id) => api.get(`/memos/${id}`),
  updateMemo: (id, data) => api.put(`/memos/${id}`, data),
  deleteMemo: (id) => api.delete(`/memos/${id}`)
}

// 角色相关API
export const roleApi = {
  getRoles: (config) => api.get('/roles', config),
  createRole: (data) => api.post('/roles', data),
  getRole: (id, config) => api.get(`/roles/${id}`, config),
  updateRole: (id, data) => api.put(`/roles/${id}`, data),
  deleteRole: (id) => api.delete(`/roles/${id}`),
  getRoleMenus: (id, config) => api.get(`/roles/${id}/menus`, config),
  assignRoleMenus: (id, menuIds) => api.post(`/roles/${id}/menus`, menuIds),
  getRolePermissions: (id, config) => api.get(`/roles/${id}/permissions`, config),
  assignRolePermissions: (id, permissionIds) => api.post(`/roles/${id}/permissions`, permissionIds)
}

// 菜单相关API
export const menuApi = {
  getMenus: (config) => api.get('/menus', config),
  getAllMenus: (config) => api.get('/menus/all', config),
  getParentMenuOptions: (config) => api.get('/menus/parent-options', config),
  getAllMenuTree: (config) => api.get('/menus/all-tree', config),
  getMenuTree: (config) => api.get('/menus/tree', config),
  getUserMenus: (config) => api.get('/menus/user', config),
  getMenu: (id) => api.get(`/menus/${id}`),
  createMenu: (data) => api.post('/menus', data),
  updateMenu: (id, data) => api.put(`/menus/${id}`, data),
  deleteMenu: (id) => api.delete(`/menus/${id}`)
}

// 权限相关API
export const permissionApi = {
  getPermissions: () => api.get('/permissions'),
  getPermissionTree: () => api.get('/permissions/tree'),
  createPermission: (data) => api.post('/permissions', data),
  updatePermission: (id, data) => api.put(`/permissions/${id}`, data),
  deletePermission: (id) => api.delete(`/permissions/${id}`)
}

export default api
