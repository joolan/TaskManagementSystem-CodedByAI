<template>
  <div class="tasks-container">
    
    <div class="tasks-filters">
      <el-form :inline="true" :model="filterForm" class="demo-form-inline">
        <el-form-item label="状态">
          <el-select v-model="filterForm.status_id" placeholder="全部" style="width: 200px;" multiple>
            <el-option v-for="status in statuses" :key="status.id" :label="status.name" :value="status.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="filterForm.priority" placeholder="全部" style="width: 76px;">
            <el-option label="全部" value=""></el-option>
            <el-option label="高" value="high"></el-option>
            <el-option label="中" value="medium"></el-option>
            <el-option label="低" value="low"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="我的关注">
          <el-select v-model="filterForm.follow_status" placeholder="全部" style="width: 150px;">
            <el-option label="全部" value=""></el-option>
            <el-option label="我关注的" value="followed"></el-option>
            <el-option label="我未关注的" value="unfollowed"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="负责人">
          <el-select v-model="filterForm.assignee_id" placeholder="全部" style="width: 150px;">
            <el-option label="全部" value=""></el-option>
            <el-option v-for="user in users" :key="user.id" :label="user.name" :value="user.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input v-model="filterForm.search" placeholder="任务标题" clearable></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchTasks">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
          <el-button v-permission="'task:export'" type="success" @click="exportTasks" :loading="exportLoading">导出</el-button>
        </el-form-item>
        <el-form-item>
          <el-button v-permission="'task:create'" type="primary" @click="goToCreateTask">创建任务</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <div class="tasks-table">
      <el-table :data="taskStore.tasks" style="width: 100%">
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column prop="id" label="任务ID" width="80"></el-table-column>
        <el-table-column prop="title" label="任务标题">
          <template #default="scope">
            <div class="task-title-container">
              <router-link :to="`/task/${scope.row.id}`" class="task-title-link">
                {{ scope.row.title }}
              </router-link>
              <div v-if="scope.row.tags && scope.row.tags.length > 0" class="task-tags">
                <span 
                  v-for="tag in scope.row.tags" 
                  :key="tag.id" 
                  class="task-tag"
                  :style="{ backgroundColor: (tag.color || '#60a5fa') + '20', color: tag.color || '#60a5fa' }"
                >
                  {{ tag.name }}
                </span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <span class="status-badge" :style="{ backgroundColor: scope.row.status?.color }">
              {{ scope.row.status?.name }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="优先级" width="100">
          <template #default="scope">
            <span class="priority-badge" :class="scope.row.priority">{{ getPriorityText(scope.row.priority) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="负责人" width="180">
          <template #default="scope">
            <div v-if="scope.row.assignees && scope.row.assignees.length > 0" class="assignees-list">
              <span v-for="assignee in scope.row.assignees" :key="assignee.id" class="assignee-tag">
                {{ assignee.name }}
              </span>
            </div>
            <span v-else-if="scope.row.assignee" class="assignee-single">
              {{ scope.row.assignee.name }}
            </span>
            <span v-else class="unassigned">未分配</span>
          </template>
        </el-table-column>
        <!-- 预估工时 -->
        <el-table-column label="预估工时" width="100">
          <template #default="scope">
            <span v-if="scope.row.estimated_hours">
              <span v-if="scope.row.estimated_hours > 4">
                {{ (scope.row.estimated_hours / 24).toFixed(1) }} 天
              </span>
              <span v-else>
                {{ scope.row.estimated_hours }} h
              </span>
            </span>
            <span v-else></span>
          </template>
        </el-table-column>
        <el-table-column label="截止日期" width="120">
          <template #default="scope">
            <span v-if="scope.row.due_date" :class="{ overdue: isOverdue(scope.row.due_date) }">
              {{ formatDate(scope.row.due_date) }}
            </span>
            <span v-else>未设置</span>
          </template>
        </el-table-column>
        <el-table-column label="是否发版" width="100">
          <template #default="scope">
            <el-tag :type="getReleaseTagType(getReleaseStatus(scope.row))">
              {{ getReleaseStatus(scope.row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button v-permission="'task:update'" size="small" @click="goToEditTask(scope.row.id)">编辑</el-button>
            <el-button v-permission="'task:delete'" size="small" type="danger" @click="handleDeleteTask(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          :current-page="taskStore.currentPage"
          :page-size="taskStore.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="taskStore.totalTasks"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useTaskStore, useUserStore } from '../store'
import dayjs from 'dayjs'
import api, { authApi } from '../api/index'
import { ElMessage } from 'element-plus'
import { exportFile, getFileNameFromResponse } from '../utils/exportFile'

const router = useRouter()
const route = useRoute()
const taskStore = useTaskStore()
const userStore = useUserStore()

const filterForm = ref({
  status_id: [],
  priority: '',
  search: '',
  follow_status: '',
  assignee_id: ''
})

const statuses = ref([
  { id: 1, name: '待办', order_index: 1, color: '#94a3b8' },
  { id: 2, name: '进行中', order_index: 2, color: '#3b82f6' },
  { id: 3, name: '已完成', order_index: 3, color: '#10b981' },
  { id: 4, name: '已暂停', order_index: 4, color: '#f59e0b' },
  { id: 5, name: '已取消', order_index: 5, color: '#ef4444' }
])

const users = ref([])
const exportLoading = ref(false)

const formatDate = (dateString) => {
  return dateString ? dayjs(dateString).format('YYYY-MM-DD') : ''
}

const getPriorityText = (priority) => {
  const priorityMap = {
    'high': '高',
    'medium': '中',
    'low': '低'
  }
  return priorityMap[priority] || priority
}

const isOverdue = (dateString) => {
  return dateString && dayjs(dateString).isBefore(dayjs(), 'day')
}

// 获取任务的发版状态
const getReleaseStatus = (task) => {
  if (!task.release_id) {
    return '未计划'
  }
  return task.release?.status || '未知'
}

// 获取发版状态对应的标签类型
const getReleaseTagType = (status) => {
  const typeMap = {
    '未计划': 'info',
    '计划中': 'primary',
    '已发版': 'success',
    '延期中': 'warning',
    '已作废': 'danger',
    '未知': 'info'
  }
  return typeMap[status] || 'info'
}

const goToCreateTask = () => {
  router.push('/task/create')
}

const goToEditTask = (taskId) => {
  router.push(`/task/edit/${taskId}`)
}

const fetchTasks = async () => {
  // 过滤掉空值参数，避免传递空字符串给后端
  const params = {}
  if (filterForm.value.status_id && filterForm.value.status_id.length > 0) {
    params.status_id = filterForm.value.status_id.join(',')
  }
  if (filterForm.value.priority) params.priority = filterForm.value.priority
  if (filterForm.value.search) params.search = filterForm.value.search
  if (filterForm.value.follow_status) params.follow_status = filterForm.value.follow_status
  if (filterForm.value.assignee_id) params.assignee_id = filterForm.value.assignee_id
  
  await taskStore.fetchTasks(params, taskStore.currentPage, taskStore.pageSize)
}

const resetFilters = () => {
  filterForm.value = {
    status_id: [],
    priority: '',
    search: '',
    follow_status: '',
    assignee_id: ''
  }
  fetchTasks()
}

const handleDeleteTask = async (taskId) => {
  try {
    await taskStore.deleteTask(taskId)
  } catch (error) {
    console.error('删除任务失败:', error)
  }
}

const handleSizeChange = (size) => {
  taskStore.pageSize = size
  taskStore.currentPage = 1 // 重置到第一页
  fetchTasks()
}

const handleCurrentChange = (current) => {
  taskStore.currentPage = current
  fetchTasks()
}

const exportTasks = async () => {
  if (exportLoading.value) return // 防止重复点击
  
  exportLoading.value = true
  try {
    // 构建查询参数
    const params = {}
    if (filterForm.value.status_id) params.status_id = filterForm.value.status_id
    if (filterForm.value.priority) params.priority = filterForm.value.priority
    if (filterForm.value.search) params.search = filterForm.value.search
    
    // 使用axios发送请求，获取二进制数据
    const response = await api.get('/tasks/export', {
      params,
      responseType: 'blob' // 重要：设置响应类型为blob
    })
    
    // 获取文件名
    const fileName = getFileNameFromResponse(response, 'tasks_export.xlsx')
    
    // 导出文件（让用户选择保存位置）
    const success = await exportFile(response.data, fileName)
    
    if (success) {
      ElMessage.success('导出成功')
    }
  } catch (error) {
    console.error('导出任务失败:', error)
    ElMessage.error('导出任务失败，请重试')
  } finally {
    exportLoading.value = false
  }
}

// 处理路由查询参数
const handleRouteQuery = async () => {
  const { filter, status } = route.query
  
  // 重置过滤条件
  filterForm.value = {
    status_id: [],
    priority: '',
    search: '',
    follow_status: '',
    assignee_id: ''
  }
  
  // 根据查询参数设置过滤条件
  if (filter === 'my-assigned') {
    // 我负责的任务 - 设置负责人为当前用户
    if (userStore.user && userStore.user.id) {
      filterForm.value.assignee_id = userStore.user.id
    }
  } else if (filter === 'my-followed') {
    // 我关注的任务 - 设置我的关注为我关注的
    filterForm.value.follow_status = 'followed'
  }
  
  if (status === 'uncompleted') {
    // 未完成任务 - 设置状态过滤为待办、进行中、已暂停
    filterForm.value.status_id = [1, 2, 4] // 待办、进行中、已暂停的状态ID
  }
  
  // 获取任务
  await fetchTasks()
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

onMounted(async () => {
  await taskStore.fetchStatuses()
  await fetchUsers() // 获取用户列表
  // 确保用户信息已加载
  if (!userStore.user.id) {
    try {
      await userStore.getCurrentUser()
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }
  await handleRouteQuery()
})
</script>

<style scoped>
.tasks-container {
  padding: 10px;
  background-color: #ffffff;
}

.tasks-filters {
  margin-bottom: 15px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.tasks-table {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 15px;
}

.pagination {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
}

.task-title-link {
  color: #1890ff;
  text-decoration: none;
}

.task-title-link:hover {
  text-decoration: underline;
}

.status-badge {
  color: #ffffff;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  display: inline-block;
  text-align: center;
  min-width: 60px;
}

.task-description {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 280px;
  color: #666;
  font-size: 13px;
}

.priority-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  text-transform: uppercase;
}

.priority-badge.high {
  background-color: #fee2e2;
  color: #dc2626;
}

.priority-badge.medium {
  background-color: #fef3c7;
  color: #d97706;
}

.priority-badge.low {
  background-color: #d1fae5;
  color: #059669;
}

.unassigned {
  color: #999;
  font-style: italic;
}

.assignees-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.assignee-tag {
  background-color: #e6f7ff;
  color: #1890ff;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.task-title-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.task-tag {
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.assignee-single {
  font-weight: 500;
}

.overdue {
  color: #dc2626;
  font-weight: 600;
}
</style>
