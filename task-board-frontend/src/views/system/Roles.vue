<template>
  <div class="role-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>角色管理</span>
          <el-button v-permission="'role:create'" type="primary" @click="handleAddRole">
            <el-icon><Plus /></el-icon>
            新增角色
          </el-button>
        </div>
      </template>
      
      <!-- 角色列表 -->
      <el-table :data="roles" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="角色名称" />
        <el-table-column prop="description" label="角色描述" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'">
              {{ scope.row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="scope">
            <el-button v-permission="'role:update'" size="small" @click="handleEditRole(scope.row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button v-permission="'role:assign'" size="small" type="primary" @click="handleAssignPermissions(scope.row)">
              <el-icon><Lock /></el-icon>
              权限
            </el-button>
            <el-button
              v-permission="'role:update'"
              size="small"
              :type="scope.row.status === 1 ? 'warning' : 'success'"
              @click="handleToggleStatus(scope.row)"
            >
              <el-icon>
                <SwitchButton v-if="scope.row.status === 1" />
                <Check v-else />
              </el-icon>
              {{ scope.row.status === 1 ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑角色对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色描述" prop="description">
          <el-input 
            v-model="formData.description" 
            type="textarea" 
            placeholder="请输入角色描述"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch v-model="formData.status" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 权限分配对话框 -->
    <el-dialog
      v-model="permissionDialogVisible"
      title="权限分配"
      width="600px"
    >
      <div class="permission-assignment">
        <h4>{{ currentRole?.name }} - 权限分配</h4>
        
        <!-- 菜单和功能权限 -->
        <div class="permission-section">
          <h5>菜单和功能权限</h5>
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
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="permissionDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAssignPermissionsSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Lock, SwitchButton, Check } from '@element-plus/icons-vue'
import { roleApi, menuApi, permissionApi } from '../../api'
import axios from 'axios'

// 跟踪组件是否已销毁
const isComponentDestroyed = ref(false)
// 存储取消令牌
const cancelTokens = ref([])

const dialogVisible = ref(false)
const permissionDialogVisible = ref(false)
const dialogTitle = ref('新增角色')
const formRef = ref(null)
const menuTreeRef = ref(null)
const permissionTreeRef = ref(null)
const roles = ref([])
const menuTree = ref([])
const permissionTree = ref([])
const currentRole = ref(null)
const checkedMenuIds = ref([])
const checkedPermissionIds = ref([])

const formData = reactive({
  name: '',
  description: '',
  status: 1
})

const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }]
}

const treeProps = {
  children: 'children',
  label: 'name'
}

const permissionTreeProps = {
  children: 'children',
  label: 'name'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const loadRoles = async () => {
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
    
    roles.value = response.data
  } catch (error) {
    // 忽略取消错误和无token错误
    if (axios.isCancel(error) || error.message === 'No token found') return
    
    // 检查组件是否已销毁
    if (!isComponentDestroyed.value) {
      ElMessage.error('加载角色失败')
    }
  }
}

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
    
    // 处理菜单树，将权限作为子节点添加
    menuTree.value = transformMenuTree(response.data)
  } catch (error) {
    // 忽略取消错误和无token错误
    if (axios.isCancel(error) || error.message === 'No token found') return
    
    console.error('加载菜单失败:', error)
  }
}

const transformMenuTree = (menus) => {
  return menus.map(menu => {
    // 创建新的子节点数组，避免重复
    const children = []
    
    // 递归处理子菜单
    if (menu.children && menu.children.length > 0) {
      children.push(...transformMenuTree(menu.children))
    }
    
    // 将权限作为子节点添加
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

const loadPermissionTree = async () => {
  try {
    const response = await permissionApi.getPermissionTree()
    permissionTree.value = response.data
  } catch (error) {
    console.error('加载权限失败:', error)
  }
}

const handleAddRole = () => {
  dialogTitle.value = '新增角色'
  Object.assign(formData, {
    name: '',
    description: '',
    status: 1
  })
  delete formData.id
  dialogVisible.value = true
}

const handleEditRole = (role) => {
  dialogTitle.value = '编辑角色'
  Object.assign(formData, {
    id: role.id,
    name: role.name,
    description: role.description,
    status: role.status
  })
  dialogVisible.value = true
}

const handleToggleStatus = async (role) => {
  try {
    const newStatus = role.status === 1 ? 0 : 1
    await roleApi.updateRole(role.id, { status: newStatus })
    ElMessage.success(`角色已${newStatus === 1 ? '启用' : '禁用'}`)
    loadRoles()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleAssignPermissions = async (role) => {
  currentRole.value = role
  await loadMenuTree()
  
  try {
    // 获取角色的菜单权限
    const menuResponse = await roleApi.getRoleMenus(role.id)
    const menuIds = menuResponse.data.map(item => item.id)
    
    // 获取角色的按钮权限
    const permissionResponse = await roleApi.getRolePermissions(role.id)
    const permissionIds = permissionResponse.data.map(item => `perm_${item.id}`) // 为权限ID添加前缀
    
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

const handleAssignPermissionsSubmit = async () => {
  try {
    if (!currentRole.value) return
    
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
    
    await roleApi.assignRoleMenus(currentRole.value.id, selectedMenuIds)
    await roleApi.assignRolePermissions(currentRole.value.id, finalPermissionIds)
    
    ElMessage.success('权限分配成功')
    permissionDialogVisible.value = false
  } catch (error) {
    console.error('权限分配失败:', error)
    ElMessage.error('权限分配失败')
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    if (formData.id) {
      await roleApi.updateRole(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await roleApi.createRole(formData)
      ElMessage.success('新增成功')
    }
    
    dialogVisible.value = false
    loadRoles()
  } catch (error) {
    if (error.response) {
      ElMessage.error(error.response.data.detail || '操作失败')
    } else {
      ElMessage.error('操作失败')
    }
  }
}

onMounted(() => {
  loadRoles()
})

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
</script>

<style scoped>
.role-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.permission-assignment {
  max-height: 500px;
  overflow-y: auto;
}

.permission-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eaeaea;
}

.permission-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.permission-section h5 {
  margin-bottom: 10px;
  font-weight: 600;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-placeholder {
  margin-right: 24px;
  color: #ccc;
}

.permission-badge {
  margin-left: 8px;
  font-size: 12px;
  padding: 0 8px;
  height: 20px;
  line-height: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
