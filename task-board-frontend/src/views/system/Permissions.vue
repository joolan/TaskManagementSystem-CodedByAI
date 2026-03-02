<template>
  <div class="permission-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>权限管理</span>
          <el-button v-permission="'permission:create'" type="primary" @click="handleAddPermission">
            <el-icon><Plus /></el-icon>
            新增权限
          </el-button>
        </div>
      </template>
      
      <!-- 权限列表 -->
      <el-table :data="permissions" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="权限名称" />
        <el-table-column prop="code" label="权限编码" />
        <el-table-column prop="description" label="权限描述" />
        <el-table-column prop="menu_id" label="所属菜单" width="150">
          <template #default="scope">
            <span>{{ getMenuName(scope.row.menu_id) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button v-permission="'permission:update'" size="small" @click="handleEditPermission(scope.row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button v-permission="'permission:delete'" size="small" type="danger" @click="handleDeletePermission(scope.row.id)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑权限对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入权限名称" />
        </el-form-item>
        <el-form-item label="权限编码" prop="code">
          <el-input v-model="formData.code" placeholder="请输入权限编码" />
        </el-form-item>
        <el-form-item label="权限描述" prop="description">
          <el-input 
            v-model="formData.description" 
            type="textarea" 
            placeholder="请输入权限描述"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="所属菜单" prop="menu_id">
          <el-select v-model="formData.menu_id" placeholder="选择所属菜单" clearable>
            <el-option
              v-for="menu in menuOptions"
              :key="menu.id"
              :label="menu.name"
              :value="menu.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'

const dialogVisible = ref(false)
const dialogTitle = ref('新增权限')
const formRef = ref(null)
const permissions = ref([])
const menuOptions = ref([])

const formData = reactive({
  name: '',
  code: '',
  description: '',
  menu_id: null
})

const rules = {
  name: [{ required: true, message: '请输入权限名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入权限编码', trigger: 'blur' }]
}

// 加载权限列表
const loadPermissions = async () => {
  try {
    const response = await fetch('http://localhost:8001/api/permissions')
    if (response.ok) {
      const data = await response.json()
      permissions.value = data
    } else {
      ElMessage.error('加载权限失败')
    }
  } catch (error) {
    ElMessage.error('网络错误，请稍后重试')
  }
}

// 加载菜单选项
const loadMenus = async () => {
  try {
    const response = await fetch('http://localhost:8001/api/menus')
    if (response.ok) {
      const data = await response.json()
      menuOptions.value = data
    }
  } catch (error) {
    console.error('加载菜单失败:', error)
  }
}

// 根据菜单ID获取菜单名称
const getMenuName = (menuId) => {
  if (!menuId) return ''
  const menu = menuOptions.value.find(item => item.id === menuId)
  return menu ? menu.name : ''
}

// 处理新增权限
const handleAddPermission = () => {
  dialogTitle.value = '新增权限'
  // 重置表单
  Object.assign(formData, {
    name: '',
    code: '',
    description: '',
    menu_id: null
  })
  delete formData.id
  dialogVisible.value = true
}

// 处理编辑权限
const handleEditPermission = (permission) => {
  dialogTitle.value = '编辑权限'
  // 填充表单数据
  Object.assign(formData, {
    id: permission.id,
    name: permission.name,
    code: permission.code,
    description: permission.description,
    menu_id: permission.menu_id
  })
  dialogVisible.value = true
}

// 处理删除权限
const handleDeletePermission = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该权限吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const response = await fetch(`http://localhost:8001/api/permissions/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (response.ok) {
      ElMessage.success('删除成功')
      loadPermissions()
    } else {
      ElMessage.error('删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 处理表单提交
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    const method = formData.id ? 'PUT' : 'POST'
    const url = formData.id ? `http://localhost:8001/api/permissions/${formData.id}` : 'http://localhost:8001/api/permissions'
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(formData)
    })
    
    if (response.ok) {
      ElMessage.success(formData.id ? '更新成功' : '新增成功')
      dialogVisible.value = false
      loadPermissions()
    } else {
      ElMessage.error(formData.id ? '更新失败' : '新增失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
  }
}

onMounted(() => {
  loadPermissions()
  loadMenus()
})
</script>

<style scoped>
.permission-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>