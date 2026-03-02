<template>
  <div class="requirements-container">
    <el-card>
      <!-- 筛选条件 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filterForm" class="filter-form">
          <el-form-item label="需求状态">
            <el-select v-model="filterForm.status" placeholder="全部" style="width: 200px;" multiple>
              <el-option label="草稿" value="草稿"></el-option>
              <el-option label="待评审" value="待评审"></el-option>
              <el-option label="已确认" value="已确认"></el-option>
              <el-option label="已作废" value="已作废"></el-option>
              <el-option label="已转任务" value="已转任务"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="需求优先级">
            <el-select v-model="filterForm.priority" placeholder="全部" style="width: 76px;">
              <el-option label="全部" value=""></el-option>
              <el-option label="高" value="高"></el-option>
              <el-option label="中" value="中"></el-option>
              <el-option label="低" value="低"></el-option>
            </el-select>
          </el-form-item>
          
        <el-form-item label="需求创建人">
          <el-select v-model="filterForm.created_by" placeholder="全部" style="width: 150px;">
            <el-option label="全部" value=""></el-option>
            <el-option 
              v-for="user in users" 
              :key="user.id" 
              :label="user.name" 
              :value="user.id"
            />
          </el-select>
        </el-form-item>
          <el-form-item label="搜索">
            <el-input 
              v-model="filterForm.search" 
              placeholder="搜索需求名称或描述" 
              clearable
            >
              
            </el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="resetFilter">重置</el-button>
            <el-button v-permission="'requirement:export'" type="success" @click="exportRequirements" :loading="exportLoading">导出</el-button>
          </el-form-item>
          <el-form-item>
            <el-button 
              v-permission="'requirement:create'"
              type="primary" 
              @click="handleCreateRequirement"
            >
              <el-icon><Plus /></el-icon>
              新建需求
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 需求列表 -->
      <div class="requirements-list">
        <el-table :data="requirementsData.items" style="width: 100%">
          <el-table-column prop="id" label="需求ID" width="100" />
          <el-table-column label="需求名称" min-width="200">
            <template #default="scope">
              <el-link type="primary" @click="handleViewRequirement(scope.row.id)">
                {{ scope.row.name }}
              </el-link>
            </template>
          </el-table-column>
          <el-table-column label="需求标签" width="120">
            <template #default="scope">
              <el-tag 
                v-if="scope.row.tag" 
                :style="{ backgroundColor: scope.row.tag.color + '20', color: scope.row.tag.color }"
              >
                {{ scope.row.tag.name }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="source" label="需求来源" width="120" />
          <el-table-column prop="status" label="需求状态" width="100">
            <template #default="scope">
              <el-tag 
                :type="getStatusType(scope.row.status)"
              >
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="priority" label="优先级" width="80">
            <template #default="scope">
              <el-tag 
                :type="getPriorityType(scope.row.priority)"
              >
                {{ scope.row.priority }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="150">
            <template #default="scope">
              {{ formatDateTime(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="planned_completion_date" label="计划完成日期" width="150">
            <template #default="scope">
              {{ formatDate(scope.row.planned_completion_date) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="240" fixed="right">
            <template #default="scope">
              <el-button 
                v-permission="'requirement:update'"
                type="warning" 
                size="small" 
                @click="handleEditRequirement(scope.row.id)"
                :disabled="scope.row.status === '已转任务'"
              >
                编辑
              </el-button>
              <el-button 
                v-permission="'requirement:convert'"
                type="success" 
                size="small" 
                @click="handleConvertToTask(scope.row)"
                :disabled="scope.row.status === '已转任务'"
              >
                转任务
              </el-button>
              <el-button 
                v-permission="'requirement:delete'"
                type="danger" 
                size="small" 
                @click="handleDeleteRequirement(scope.row.id)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <div class="pagination">
          <el-pagination
            :current-page="pagination.page"
            :page-size="pagination.page_size"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="requirementsData.total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </el-card>
    
    <!-- 转任务对话框 -->
    <el-dialog
      v-model="convertToTaskDialogVisible"
      title="转任务"
      width="60%"
    >
      <el-form :model="taskForm" label-width="100px" :rules="taskFormRules" ref="taskFormRef">
        <el-form-item label="任务标题">
          <el-input v-model="taskForm.title" placeholder="请输入任务标题" />
        </el-form-item>
        <el-form-item label="任务描述">
          <CustomRichTextEditor v-model="taskForm.description" />
        </el-form-item>
        <el-form-item label="任务状态" prop="status_id">
          <el-select v-model="taskForm.status_id" placeholder="请选择任务状态" required>
            <el-option 
              v-for="status in taskStatuses" 
              :key="status.id" 
              :label="status.name" 
              :value="status.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人" prop="assignee_ids">
          <el-select v-model="taskForm.assignee_ids" placeholder="请选择负责人" multiple>
            <el-option 
              v-for="user in users" 
              :key="user.id" 
              :label="user.name" 
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="taskForm.priority" placeholder="请选择优先级" required>
            <el-option label="高" value="高" />
            <el-option label="中" value="中" />
            <el-option label="低" value="低" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker
            v-model="taskForm.due_date"
            type="datetime"
            placeholder="选择截止日期"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="convertToTaskDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitConvertToTask">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import api, { requirementApi, requirementTagApi, authApi, taskApi } from '../api/index'
import { useUserStore } from '../store'
import CustomRichTextEditor from '../components/CustomRichTextEditor.vue'
import { exportFile, getFileNameFromResponse } from '../utils/exportFile'

const router = useRouter()
const route = useRoute()
const store = useUserStore()

// 状态管理
const requirementsData = ref({
  items: [],
  total: 0,
  page: 1,
  page_size: 10,
  pages: 0
})

const requirementTags = ref([])
const taskStatuses = ref([
  { id: 1, name: '待办', order_index: 1, color: '#94a3b8' },
  { id: 2, name: '进行中', order_index: 2, color: '#3b82f6' },
  { id: 3, name: '已完成', order_index: 3, color: '#10b981' },
  { id: 4, name: '已暂停', order_index: 4, color: '#f59e0b' },
  { id: 5, name: '已取消', order_index: 5, color: '#ef4444' }
])
const users = ref([])
const isViewer = computed(() => store.user.role === 'viewer')
const exportLoading = ref(false)

// 筛选表单
const filterForm = ref({
  status: [],
  priority: '',
  tag_id: '',
  search: '',
  created_by: ''
})

// 分页
const pagination = ref({
  page: 1,
  page_size: 10
})

// 转任务对话框
const convertToTaskDialogVisible = ref(false)
const currentRequirement = ref(null)
const taskFormRef = ref(null)
const taskForm = ref({
  title: '',
  description: '',
  status_id: '',
  assignee_ids: [],
  priority: '',
  due_date: ''
})

const taskFormRules = ref({
  status_id: [
    {
      required: true,
      message: '请选择任务状态',
      trigger: 'change'
    }
  ],
  priority: [
    {
      required: true,
      message: '请选择优先级',
      trigger: 'change'
    }
  ],
  assignee_ids: [
    {
      required: true,
      message: '请选择负责人',
      trigger: 'change'
    }
  ]
})

// 获取需求列表
const fetchRequirements = async () => {
  try {
    const params = {
      ...filterForm.value,
      page: pagination.value.page,
      page_size: pagination.value.page_size
    }
    
    // 处理status数组
    if (params.status && Array.isArray(params.status) && params.status.length > 0) {
      params.status = params.status.join(',')
    } else if (params.status && !params.status.length) {
      delete params.status
    }
    
    // 移除空值参数
    Object.keys(params).forEach(key => {
      if (!params[key]) {
        delete params[key]
      }
    })
    
    const response = await requirementApi.getRequirements(params)
    requirementsData.value = response.data
  } catch (error) {
    console.error('获取需求列表失败:', error)
    ElMessage.error('获取需求列表失败')
  }
}

// 获取需求标签
const fetchRequirementTags = async () => {
  try {
    const response = await requirementTagApi.getRequirementTags()
    requirementTags.value = response.data
  } catch (error) {
    console.error('获取需求标签失败:', error)
  }
}



// 获取用户列表
const fetchUsers = async () => {
  try {
    const response = await authApi.getUsersBasic()
    users.value = response.data
  } catch (error) {
    console.error('获取用户列表失败:', error)
  }
}

// 处理路由查询参数
const handleRouteQuery = async () => {
  const { filter, status } = route.query
  
  // 重置过滤条件
  filterForm.value = {
    status: [],
    priority: '',
    tag_id: '',
    search: '',
    created_by: ''
  }
  
  // 根据查询参数设置过滤条件
  if (filter === 'my-created') {
    // 我创建的需求 - 设置创建人为当前用户
    filterForm.value.created_by = store.user.id
  }
  
  if (status === 'pending') {
    // 待处理需求 - 设置状态过滤为草稿、待评审、已确认
    filterForm.value.status = ['草稿', '待评审', '已确认']
  }
  
  // 获取需求
  await fetchRequirements()
}

// 初始加载
onMounted(async () => {
  await fetchRequirementTags()
  await fetchUsers()
  await handleRouteQuery()
})

// 处理创建需求
const handleCreateRequirement = () => {
  router.push('/requirement/create')
}

// 处理编辑需求
const handleEditRequirement = (id) => {
  router.push(`/requirement/edit/${id}`)
}

// 处理查看需求
const handleViewRequirement = (id) => {
  router.push(`/requirement/${id}`)
}

// 处理转任务
const handleConvertToTask = (requirement) => {
  currentRequirement.value = requirement
  taskForm.value = {
    title: requirement.name,
    description: requirement.description,
    status_id: '',
    assignee_ids: [],
    priority: requirement.priority,
    due_date: requirement.planned_completion_date
  }
  convertToTaskDialogVisible.value = true
}

// 提交转任务
const submitConvertToTask = async () => {
  if (!currentRequirement.value) return
  
  // 表单验证
  if (!taskFormRef.value) return
  
  try {
    await taskFormRef.value.validate()
    
    await requirementApi.convertToTask(currentRequirement.value.id, taskForm.value)
    ElMessage.success('转任务成功')
    convertToTaskDialogVisible.value = false
    await fetchRequirements()
  } catch (error) {
    if (error.name === 'ValidationError') {
      // 表单验证失败，不显示错误消息，由Element Plus自动处理
      return
    }
    console.error('转任务失败:', error)
    ElMessage.error('转任务失败')
  }
}

// 处理删除需求
const handleDeleteRequirement = (id) => {
  ElMessageBox.confirm('确定要删除这个需求吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  .then(async () => {
    try {
      await requirementApi.deleteRequirement(id)
      ElMessage.success('删除成功')
      await fetchRequirements()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  })
  .catch(() => {
    // 取消删除
  })
}

// 处理搜索
const handleSearch = () => {
  pagination.value.page = 1
  fetchRequirements()
}

// 重置筛选
const resetFilter = () => {
  filterForm.value = {
    status: [],
    priority: '',
    tag_id: '',
    search: '',
    created_by: ''
  }
  pagination.value.page = 1
  fetchRequirements()
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.value.page_size = size
  fetchRequirements()
}

const handleCurrentChange = (current) => {
  pagination.value.page = current
  fetchRequirements()
}

// 计算状态类型
const getStatusType = (status) => {
  const statusMap = {
    '草稿': 'info',
    '待评审': 'warning',
    '已确认': 'primary',
    '已作废': 'danger',
    '已转任务': 'success'
  }
  return statusMap[status] || 'info'
}

// 计算优先级类型
const getPriorityType = (priority) => {
  const priorityMap = {
    '高': 'danger',
    '中': 'warning',
    '低': 'info'
  }
  return priorityMap[priority] || 'info'
}

// 格式化日期时间
const formatDateTime = (dateTime) => {
  if (!dateTime) return '-'
  const date = new Date(dateTime)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

// 格式化日期
const formatDate = (dateTime) => {
  if (!dateTime) return '-'
  const date = new Date(dateTime)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 导出需求
const exportRequirements = async () => {
  if (exportLoading.value) return // 防止重复点击
  
  exportLoading.value = true
  try {
    // 构建查询参数
    const params = {}
    if (filterForm.value.status) params.status = filterForm.value.status
    if (filterForm.value.priority) params.priority = filterForm.value.priority
    if (filterForm.value.tag_id) params.tag_id = filterForm.value.tag_id
    if (filterForm.value.search) params.search = filterForm.value.search
    if (filterForm.value.created_by) params.created_by = filterForm.value.created_by
    
    // 使用axios发送请求，获取二进制数据
    const response = await api.get('/requirements/export', {
      params,
      responseType: 'blob' // 重要：设置响应类型为blob
    })
    
    // 获取文件名
    const fileName = getFileNameFromResponse(response, 'requirements_export.xlsx')
    
    // 导出文件（让用户选择保存位置）
    const success = await exportFile(response.data, fileName)
    
    if (success) {
      ElMessage.success('导出成功')
    }
  } catch (error) {
    console.error('导出需求失败:', error)
    ElMessage.error('导出需求失败，请重试')
  } finally {
    exportLoading.value = false
  }
}
</script>

<style scoped>
.requirements-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f9fafb;
  border-radius: 8px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: end;
}

.tag-option {
  display: block;
  padding: 2px 8px;
  border-radius: 4px;
}

.requirements-list {
  margin-top: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
