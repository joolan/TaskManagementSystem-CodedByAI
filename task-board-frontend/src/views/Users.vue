<template>
  <div class="users-container">
    <div class="users-filters">
      <el-form :inline="true" :model="filterForm" class="demo-form-inline">
        <el-form-item label="用户名">
          <el-input v-model="filterForm.username" placeholder="请输入用户名" clearable></el-input>
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="filterForm.name" placeholder="请输入姓名" clearable></el-input>
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="filterForm.role_id" placeholder="全部" clearable style="width: 150px;">
            <el-option label="全部" :value="null"></el-option>
            <el-option 
              v-for="role in roles" 
              :key="role.id" 
              :label="role.name" 
              :value="role.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchUsers">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
          <el-button v-permission="'user:create'" type="primary" @click="openCreateUserDialog">创建用户</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <div class="users-table">
      <el-table :data="users" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="用户ID" width="80"></el-table-column>
        <el-table-column prop="username" label="用户名" width="120"></el-table-column>
        <el-table-column prop="name" label="姓名" width="120"></el-table-column>
        <el-table-column label="角色" width="150">
          <template #default="scope">
            <el-tag v-if="scope.row.username === 'admin'" type="danger" size="small">超级管理员</el-tag>
            <div v-else-if="scope.row.roles && scope.row.roles.length > 0" class="role-tags">
              <el-tag 
                v-for="role in scope.row.roles" 
                :key="role.id" 
                :type="getRoleType(role.name)"
                size="small"
              >
                {{ role.name }}
              </el-tag>
            </div>
            <el-tag v-else type="info" size="small">无角色</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="锁定状态" width="120">
          <template #default="scope">
            <el-tag v-if="isUserLocked(scope.row)" type="danger">已锁定</el-tag>
            <el-tag v-else type="success">正常</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最后登录时间" width="180">
          <template #default="scope">
            {{ formatLastLogin(scope.row.last_login_at) }}
          </template>
        </el-table-column>
        <el-table-column label="在线会话数" width="120">
          <template #default="scope">
            <el-button
              type="primary"
              link
              @click="showUserSessions(scope.row)"
            >
              {{ scope.row.session_count || 0 }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="350">
          <template #default="scope">
            <el-button v-permission="'user:update'" size="small" @click="editUser(scope.row)">编辑</el-button>
            <el-button v-permission="'user:update'" size="small" type="warning" @click="changePassword(scope.row)">修改密码</el-button>
            <el-button v-permission="'user:update'" v-if="isUserLocked(scope.row)" size="small" type="primary" @click="unlockUser(scope.row.id)">解锁</el-button>
            <el-button v-permission="'user:update'" size="small" type="primary" @click="assignUserPermissions(scope.row)">角色外权限指派</el-button>
            <el-button v-permission="'user:delete'" size="small" type="danger" @click="deleteUser(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          :current-page="pagination.currentPage"
          :page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
    
    <!-- 创建用户对话框 -->
    <el-dialog
      v-model="createUserDialogVisible"
      title="创建用户"
      width="600px"
    >
      <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input type="password" v-model="userForm.password" placeholder="请输入密码" show-password></el-input>
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="userForm.name" placeholder="请输入姓名"></el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱"></el-input>
        </el-form-item>
        <el-form-item label="角色" prop="roles">
          <el-select v-model="userForm.roles" multiple placeholder="请选择角色">
            <el-option 
              v-for="role in roles" 
              :key="role.id" 
              :label="role.name" 
              :value="role.id"
            ></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createUserDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleCreateUser">保存</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 编辑用户对话框 -->
    <el-dialog
      v-model="editUserDialogVisible"
      title="编辑用户"
      width="600px"
    >
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editForm.username" placeholder="请输入用户名" :disabled="true"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input type="password" v-model="editForm.password" placeholder="请输入密码（留空则不修改）" show-password></el-input>
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入姓名"></el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" placeholder="请输入邮箱"></el-input>
        </el-form-item>
        <el-form-item v-if="editForm.username !== 'admin'" label="角色" prop="roles">
          <el-select v-model="editForm.roles" multiple placeholder="请选择角色">
            <el-option 
              v-for="role in roles" 
              :key="role.id" 
              :label="role.name" 
              :value="role.id"
            ></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editUserDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleEditUser">保存</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="changePasswordDialogVisible"
      title="修改密码"
      width="500px"
    >
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="80px">
        <el-form-item label="新密码" prop="password">
          <el-input type="password" v-model="passwordForm.password" placeholder="请输入新密码" show-password></el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input type="password" v-model="passwordForm.confirmPassword" placeholder="请确认新密码" show-password></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="changePasswordDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleChangePassword">保存</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 会话列表对话框 -->
    <el-dialog
      v-model="sessionsDialogVisible"
      title="用户会话列表"
      width="800px"
    >
      <el-table :data="userSessions" style="width: 100%">
        <el-table-column prop="id" label="会话序号" width="100"></el-table-column>
        <el-table-column prop="login_at" label="登录时间" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.login_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="150"></el-table-column>
        <el-table-column prop="user_agent" label="用户代理" min-width="200" show-overflow-tooltip></el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button size="small" type="danger" @click="revokeSession(scope.row.id)">踢出登录</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="sessionsDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 用户权限指派对话框 -->
    <el-dialog
      v-model="permissionDialogVisible"
      title="角色外权限指派"
      width="600px"
    >
      <div class="permission-tree">
        <el-tree
          :data="menuTree"
          show-checkbox
          node-key="id"
          :props="treeProps"
          :default-checked-keys="checkedMenuIds"
          ref="menuTreeRef"
        >
          <template #default="{ node, data }">
            <span class="tree-node">
              <el-icon v-if="data.icon && data.type !== 'permission'">
                <component :is="data.icon" />
              </el-icon>
              <span v-else-if="data.type !== 'permission'" class="icon-placeholder">•</span>
              {{ data.name }}
              <el-tag v-if="data.type === 'permission'" size="small" type="info" effect="plain" class="permission-badge">
                功能权限
              </el-tag>
            </span>
          </template>
        </el-tree>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="permissionDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAssignPermissionsSubmit">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox, ElIcon } from 'element-plus'
import { authApi, roleApi, menuApi, permissionApi } from '../api'
import { useUserStore } from '../store'
import axios from 'axios'

const userStore = useUserStore()

// 跟踪组件是否已销毁
const isComponentDestroyed = ref(false)
// 存储取消令牌
const cancelTokens = ref([])

const users = ref([])
const roles = ref([])
const loading = ref(false)
const createUserDialogVisible = ref(false)
const editUserDialogVisible = ref(false)
const changePasswordDialogVisible = ref(false)
const sessionsDialogVisible = ref(false)
const permissionDialogVisible = ref(false)
const userFormRef = ref(null)
const editFormRef = ref(null)
const passwordFormRef = ref(null)
const menuTreeRef = ref(null)
const currentUserId = ref(null)
const currentUser = ref(null)
const userSessions = ref([])
const menuTree = ref([])
const checkedMenuIds = ref([])

const filterForm = reactive({
  username: '',
  name: '',
  role_id: null
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

const treeProps = {
  children: 'children',
  label: 'name'
}

const userForm = reactive({
  username: '',
  password: '',
  name: '',
  email: '',
  roles: []
})

const editForm = reactive({
  username: '',
  password: '',
  name: '',
  email: '',
  roles: []
})

const passwordForm = reactive({
  password: '',
  confirmPassword: ''
})

const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  roles: [
    { required: true, message: '请选择角色', trigger: 'change' },
    { type: 'array', min: 1, message: '至少选择一个角色', trigger: 'change' }
  ]
}

const editRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  roles: []
}

const passwordRules = {
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const getRoleType = (role) => {
  const types = {
    admin: 'danger',
    pm: 'warning',
    dev: 'success',
    viewer: 'info'
  }
  return types[role] || 'info'
}

const formatLastLogin = (lastLoginAt) => {
  if (!lastLoginAt) {
    return '从未登录'
  }
  const date = new Date(lastLoginAt)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const formatDateTime = (dateTime) => {
  if (!dateTime) {
    return '-'
  }
  const date = new Date(dateTime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const showUserSessions = async (user) => {
  try {
    currentUserId.value = user.id
    const response = await authApi.getUserSessions(user.id)
    userSessions.value = response.data
    sessionsDialogVisible.value = true
  } catch (error) {
    console.error('获取用户会话列表失败:', error)
    ElMessage.error('获取用户会话列表失败')
  }
}

const revokeSession = async (sessionId) => {
  try {
    await ElMessageBox.confirm('确定要踢出该会话吗？', '确认踢出', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await authApi.revokeSession(sessionId)
    ElMessage.success('踢出成功')
    
    // 重新加载会话列表
    if (currentUserId.value) {
      const response = await authApi.getUserSessions(currentUserId.value)
      userSessions.value = response.data
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('踢出会话失败:', error)
      ElMessage.error('踢出会话失败')
    }
  }
}

const isUserLocked = (user) => {
  return user.locked_until && new Date(user.locked_until) > new Date()
}

const unlockUser = async (userId) => {
  try {
    const response = await authApi.unlockUser(userId)
    ElMessage.success('解锁用户成功')
    await fetchUsers()
  } catch (error) {
    console.error('解锁用户失败:', error)
    ElMessage.error(error.response?.data?.detail || '解锁用户失败')
  }
}

const openCreateUserDialog = () => {
  // 重置表单
  Object.assign(userForm, {
    username: '',
    password: '',
    name: '',
    email: '',
    roles: []
  })
  createUserDialogVisible.value = true
}

const handleCreateUser = async () => {
  if (!userFormRef.value) return
  
  try {
    await userFormRef.value.validate()
    
    // 分离基本信息和角色信息
    const { roles, ...basicInfo } = userForm
    
    // 先创建用户
    const response = await authApi.createUser(basicInfo)
    
    // 然后分配角色
    await authApi.assignRolesToUser(response.data.id, roles)
    
    ElMessage.success('创建用户成功')
    createUserDialogVisible.value = false
    await fetchUsers()
  } catch (error) {
    console.error('创建用户失败:', error)
    ElMessage.error(error.response?.data?.detail || '创建用户失败')
  }
}

const editUser = (user) => {
  currentUserId.value = user.id
  // 提取用户角色的ID数组
  const roleIds = user.roles && user.roles.length > 0 
    ? user.roles.map(role => role.id)
    : []
  
  Object.assign(editForm, {
    username: user.username,
    password: '',
    name: user.name,
    email: user.email,
    roles: roleIds
  })
  editUserDialogVisible.value = true
}

const handleEditUser = async () => {
  if (!editFormRef.value) return
  
  try {
    await editFormRef.value.validate()
    
    // 分离基本信息和角色信息
    const { roles, ...basicInfo } = editForm
    
    // 先更新基本信息
    await authApi.updateUser(currentUserId.value, basicInfo)
    
    // 如果用户不是admin，再分配角色
    if (editForm.username !== 'admin') {
      await authApi.assignRolesToUser(currentUserId.value, roles)
    }
    
    ElMessage.success('更新用户成功')
    editUserDialogVisible.value = false
    await fetchUsers()
  } catch (error) {
    console.error('更新用户失败:', error)
    ElMessage.error(error.response?.data?.detail || '更新用户失败')
  }
}

const changePassword = (user) => {
  currentUserId.value = user.id
  Object.assign(passwordForm, {
    password: '',
    confirmPassword: ''
  })
  changePasswordDialogVisible.value = true
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    const response = await authApi.updateUserPassword(currentUserId.value, {
      password: passwordForm.password
    })
    ElMessage.success('修改密码成功')
    changePasswordDialogVisible.value = false
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error(error.response?.data?.detail || '修改密码失败')
  }
}

const deleteUser = (userId) => {
  ElMessageBox.confirm('确定要删除这个用户吗？', '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'danger'
  }).then(async () => {
    try {
      const response = await authApi.deleteUser(userId)
      ElMessage.success('删除用户成功')
      await fetchUsers()
    } catch (error) {
      console.error('删除用户失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除用户失败')
    }
  }).catch(() => {
    // 取消删除
  })
}

const fetchRoles = async () => {
  // 检查是否有token
  const token = localStorage.getItem('token')
  if (!token) return
  
  // 创建取消令牌
  const source = axios.CancelToken.source()
  cancelTokens.value.push(source)
  
  try {
    // 检查组件是否已销毁
    if (isComponentDestroyed.value) return
    
    const response = await roleApi.getRoles({ cancelToken: source.token })
    
    // 检查组件是否已销毁
    if (isComponentDestroyed.value) return
    
    if (response.data && Array.isArray(response.data)) {
      roles.value = response.data
    }
  } catch (error) {
    // 忽略取消错误和无token错误
    if (axios.isCancel(error) || error.message === 'No token found') return
    
    console.error('获取角色列表失败:', error)
    // 检查组件是否已销毁
    if (!isComponentDestroyed.value) {
      ElMessage.error('获取角色列表失败')
    }
  }
}

const fetchUsers = async () => {
  const token = localStorage.getItem('token')
  if (!token) return
  
  loading.value = true
  
  try {
    if (isComponentDestroyed.value) return
    
    const params = {
      page: pagination.currentPage,
      page_size: pagination.pageSize
    }
    
    // 添加查询条件
    if (filterForm.username) {
      params.username = filterForm.username
    }
    if (filterForm.name) {
      params.name = filterForm.name
    }
    if (filterForm.role_id) {
      params.role_id = filterForm.role_id
    }
    
    const response = await authApi.getUsers(params)
    
    if (isComponentDestroyed.value) return
    
    if (response.data) {
      if (response.data.items && Array.isArray(response.data.items)) {
        users.value = response.data.items
        pagination.total = response.data.total || 0
      } else if (Array.isArray(response.data)) {
        users.value = response.data
        pagination.total = response.data.length
      } else if (response.data.value && Array.isArray(response.data.value)) {
        users.value = response.data.value
        pagination.total = response.data.value.length
      } else {
        users.value = []
        pagination.total = 0
      }
    }
  } catch (error) {
    if (axios.isCancel(error) || error.message === 'No token found') return
    
    console.error('获取用户列表失败:', error)
    if (!isComponentDestroyed.value) {
      if (error.response?.status === 403) {
        ElMessage.error('您没有足够的权限访问用户管理页面')
        setTimeout(() => {
          window.location.href = '/board'
        }, 1000)
      } else {
        ElMessage.error('获取用户列表失败')
      }
    }
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  Object.assign(filterForm, {
    username: '',
    name: '',
    role_id: null
  })
  pagination.currentPage = 1
  fetchUsers()
}

const handleSizeChange = (val) => {
  pagination.pageSize = val
  pagination.currentPage = 1
  fetchUsers()
}

const handleCurrentChange = (val) => {
  pagination.currentPage = val
  fetchUsers()
}

const initData = async () => {
  // 并行获取角色列表和用户列表
  await Promise.all([
    fetchRoles(),
    fetchUsers()
  ])
}

onMounted(initData)

// 组件销毁时取消所有正在进行的异步操作
onUnmounted(() => {
  // 设置组件已销毁标志
  isComponentDestroyed.value = true
  
  // 取消所有正在进行的异步操作
  cancelTokens.value.forEach(source => {
    source.cancel('Component destroyed')
  })
  
  // 清空取消令牌数组
  cancelTokens.value = []
})

// 加载菜单树数据
const loadMenuTree = async () => {
  // 检查是否有token
  const token = localStorage.getItem('token')
  if (!token) return
  
  // 创建取消令牌
  const source = axios.CancelToken.source()
  cancelTokens.value.push(source)
  
  try {
    // 检查组件是否已销毁
    if (isComponentDestroyed.value) return
    
    const response = await menuApi.getMenuTree({ cancelToken: source.token })
    
    // 检查组件是否已销毁
    if (isComponentDestroyed.value) return
    
    if (response.data) {
      menuTree.value = transformMenuTree(response.data)
    }
  } catch (error) {
    // 忽略取消错误和无token错误
    if (axios.isCancel(error) || error.message === 'No token found') return
    
    console.error('加载菜单树失败:', error)
    // 检查组件是否已销毁
    if (!isComponentDestroyed.value) {
      ElMessage.error('加载菜单树失败')
    }
  }
}

// 转换菜单树数据，为权限ID添加前缀
const transformMenuTree = (menus) => {
  return menus.map(menu => {
    const children = []
    if (menu.children && menu.children.length > 0) {
      children.push(...transformMenuTree(menu.children))
    }
    if (menu.permissions && menu.permissions.length > 0) {
      menu.permissions.forEach(permission => {
        children.push({
          id: `perm_${permission.id}`, // 为权限ID添加前缀，避免与菜单ID冲突
          name: permission.name,
          code: permission.code,
          description: permission.description,
          menu_id: permission.menu_id,
          type: 'permission',
          permissionId: permission.id, // 保存原始权限ID
          children: []
        })
      })
    }
    return {
      id: menu.id,
      name: menu.name,
      path: menu.path,
      icon: menu.icon,
      type: menu.type,
      order_index: menu.order_index,
      parent_id: menu.parent_id,
      children: children,
      permissions: menu.permissions || []
    }
  })
}

// 打开用户权限指派对话框
const assignUserPermissions = async (user) => {
  currentUser.value = user
  currentUserId.value = user.id
  await loadMenuTree()
  
  try {
    // 获取用户的额外菜单权限
    const menuResponse = await authApi.getUserMenus(user.id)
    const menuIds = menuResponse.data
    
    // 获取用户的额外权限
    const permissionResponse = await authApi.getUserPermissions(user.id)
    const permissionIds = permissionResponse.data.map(item => `perm_${item}`) // 为权限ID添加前缀
    
    // 合并菜单ID和权限ID，用于回显
    checkedMenuIds.value = [...menuIds, ...permissionIds]
    
    // 等待 DOM 更新后，手动更新 el-tree 的选中状态
    await nextTick()
    if (menuTreeRef.value) {
      menuTreeRef.value.setCheckedKeys(checkedMenuIds.value)
    }
    
    permissionDialogVisible.value = true
  } catch (error) {
    console.error('加载权限失败:', error)
    ElMessage.error('加载权限失败')
  }
}

// 提交用户权限指派
const handleAssignPermissionsSubmit = async () => {
  try {
    if (!currentUser.value) return
    
    // 获取所有选中的节点
    const checkedNodes = menuTreeRef.value.getCheckedNodes(false, false) // 第一个参数为false，表示获取所有节点；第二个参数为false，表示不包含半选节点
    
    // 分离菜单权限和按钮权限
    const selectedMenuIds = []
    const selectedPermissionIds = []
    
    checkedNodes.forEach(node => {
      if (node.type === 'permission') {
        selectedPermissionIds.push(node.id)
      } else {
        selectedMenuIds.push(node.id)
      }
    })
    
    // 移除权限ID的前缀，只保留原始ID
    const finalPermissionIds = selectedPermissionIds.map(id => {
      if (typeof id === 'string' && id.startsWith('perm_')) {
        return parseInt(id.substring(5))
      }
      return id
    })
    
    await authApi.assignUserMenus(currentUser.value.id, selectedMenuIds)
    await authApi.assignUserPermissions(currentUser.value.id, finalPermissionIds)
    
    ElMessage.success('权限分配成功')
    permissionDialogVisible.value = false
  } catch (error) {
    console.error('权限分配失败:', error)
    ElMessage.error('权限分配失败')
  }
}
</script>

<style scoped>
.users-container {
  padding: 10px;
  background-color: #ffffff;
}

.users-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-bottom: 15px;
}

.users-table {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 15px;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.role-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  align-items: center;
}

.permission-tree {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 10px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-placeholder {
  width: 16px;
  text-align: center;
}

.permission-badge {
  margin-left: 8px;
}

.users-filters {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.users-table {
  background-color: #fff;
  padding: 20px;
  border-radius: 4px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding: 20px;
  background-color: #fff;
  border-radius: 4px;
}
</style>
