<template>
  <div class="board-container">
    <div class="board-header">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick" class="board-tabs">
        <el-tab-pane label="进行中" name="inProgress"></el-tab-pane>
        <el-tab-pane label="待办" name="todo"></el-tab-pane>
        <el-tab-pane label="已暂停" name="paused"></el-tab-pane>
        <el-tab-pane label="已取消" name="canceled"></el-tab-pane>
        <el-tab-pane label="已完成" name="completed"></el-tab-pane>
        <el-tab-pane label="全部" name="all"></el-tab-pane>
      </el-tabs>
    </div>
    
    <div class="board-grid">
      <div v-for="task in filteredTasks" :key="task.id" class="task-card" @click="openTaskDetail(task.id)" :style="{ borderLeftColor: getStatusColor(task.status_id) }">
        <div class="task-card-header">
          <h4>{{ task.title }}</h4>
          <span class="priority-badge" :class="task.priority">{{ getPriorityText(task.priority) }}</span>
          <el-tag :style="{ backgroundColor: getStatusColor(task.status_id) }" size="small" class="status-tag">
            {{ getStatusName(task.status_id) }}
          </el-tag>
        </div>
        <div v-if="task.tags && task.tags.length > 0" class="task-card-tags">
          <span 
            v-for="tag in task.tags" 
            :key="tag.id" 
            class="task-tag"
            :style="{ backgroundColor: (tag.color || '#60a5fa') + '20', color: tag.color || '#60a5fa' }"
          >
            {{ tag.name }}
          </span>
        </div>
        <div v-if="task.description" class="task-card-description">
          {{ truncateText(task.description, 50) }}
        </div>
        <div class="task-card-footer">
          <div v-if="task.assignees && task.assignees.length > 0" class="task-assignees">
            <el-avatar v-for="assignee in task.assignees" :key="assignee.id" size="small">{{ getInitial(assignee.name) }}</el-avatar>
          </div>
          <div v-else-if="task.assignee" class="task-assignee">
            <el-avatar size="small">{{ getInitial(task.assignee.name) }}</el-avatar>
            <span>{{ task.assignee.name }}</span>
          </div>
          <div v-else class="task-assignee unassigned">
            未分配
          </div>
          <div v-if="task.due_date" class="task-due-date" :class="{ overdue: isOverdue(task.due_date) }">
            {{ formatDate(task.due_date) }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- 创建任务对话框 -->
    <el-dialog
      v-model="createTaskDialogVisible"
      title="创建任务"
      width="600px"
    >
      <el-form :model="newTask" :rules="taskRules" ref="taskFormRef" label-width="80px">
        <el-form-item label="任务标题" prop="title">
          <el-input v-model="newTask.title" placeholder="请输入任务标题"></el-input>
        </el-form-item>
        <el-form-item label="任务描述" prop="description">
          <el-input type="textarea" v-model="newTask.description" placeholder="请输入任务描述" rows="3"></el-input>
        </el-form-item>
        <el-form-item label="状态" prop="status_id">
          <el-select v-model="newTask.status_id" placeholder="请选择状态">
            <el-option v-for="status in statuses" :key="status.id" :label="status.name" :value="status.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="newTask.priority" placeholder="请选择优先级">
            <el-option label="高" value="high"></el-option>
            <el-option label="中" value="medium"></el-option>
            <el-option label="低" value="low"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期" prop="due_date">
          <el-date-picker v-model="newTask.due_date" type="date" placeholder="请选择截止日期" style="width: 100%"></el-date-picker>
        </el-form-item>
        <el-form-item label="预估工时" prop="estimated_hours">
          <el-input type="number" v-model="newTask.estimated_hours" placeholder="请输入预估工时" min="0.5" step="0.5"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createTaskDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleCreateTask">创建</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useTaskStore } from '../store'
import dayjs from 'dayjs'

const router = useRouter()
const taskStore = useTaskStore()

// 计算是否为仅查看角色
const isViewer = computed(() => {
  return taskStore.user?.role === 'viewer'
})

const createTaskDialogVisible = ref(false)
const taskFormRef = ref(null)
const activeTab = ref('inProgress') // 默认展示进行中的看板

const statuses = ref([
  { id: 1, name: '待办', order_index: 1, color: '#94a3b8' },
  { id: 2, name: '进行中', order_index: 2, color: '#3b82f6' },
  { id: 3, name: '已完成', order_index: 3, color: '#10b981' },
  { id: 4, name: '已暂停', order_index: 4, color: '#f59e0b' },
  { id: 5, name: '已取消', order_index: 5, color: '#ef4444' }
])

const newTask = reactive({
  title: '',
  description: '',
  status_id: 1,
  assignee_ids: [],
  priority: 'medium',
  due_date: null,
  estimated_hours: null
})

const taskRules = {
  title: [
    { required: true, message: '请输入任务标题', trigger: 'blur' }
  ],
  status_id: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ]
}

const sortedTasks = computed(() => {
  return [...taskStore.tasks].sort((a, b) => {
    if (a.status_id !== b.status_id) {
      return a.status_id - b.status_id
    }
    return new Date(b.created_at) - new Date(a.created_at)
  })
})

// 根据当前选中的 tab 过滤任务
const filteredTasks = computed(() => {
  switch (activeTab.value) {
    case 'inProgress':
      return sortedTasks.value.filter(task => task.status_id === 2) // 进行中
    case 'todo':
      return sortedTasks.value.filter(task => task.status_id === 1) // 待办
    case 'paused':
      return sortedTasks.value.filter(task => task.status_id === 4) // 已暂停
    case 'canceled':
      return sortedTasks.value.filter(task => task.status_id === 5) // 已取消
    case 'completed':
      return sortedTasks.value.filter(task => task.status_id === 3) // 已完成
    case 'all':
      return sortedTasks.value // 全部
    default:
      return sortedTasks.value.filter(task => task.status_id === 2) // 默认展示进行中
  }
})

const getPriorityColor = (priority) => {
  const colors = {
    high: '#ef4444',
    medium: '#f59e0b',
    low: '#10b981'
  }
  return colors[priority] || '#94a3b8'
}

const getPriorityText = (priority) => {
  const priorityMap = {
    'high': '高',
    'medium': '中',
    'low': '低'
  }
  return priorityMap[priority] || priority
}

const getStatusColor = (statusId) => {
  const status = statuses.value.find(s => s.id === statusId)
  return status ? status.color : '#94a3b8'
}

const getStatusName = (statusId) => {
  const status = statuses.value.find(s => s.id === statusId)
  return status ? status.name : '未知'
}

const getInitial = (name) => {
  return name.charAt(0).toUpperCase()
}

const truncateText = (text, maxLength) => {
  // 去除HTML标签
  const plainText = text.replace(/<[^>]*>/g, '')
  return plainText.length > maxLength ? plainText.substring(0, maxLength) + '...' : plainText
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD')
}

const isOverdue = (dateString) => {
  return dayjs(dateString).isBefore(dayjs(), 'day')
}

const handleTabClick = async (tab) => {
  activeTab.value = tab.props.name
  await fetchTasksByStatus(tab.props.name)
}

const openCreateTaskDialog = () => {
  createTaskDialogVisible.value = true
}

const handleCreateTask = async () => {
  if (!taskFormRef.value) return
  
  try {
    await taskFormRef.value.validate()
    await taskStore.createTask(newTask)
    createTaskDialogVisible.value = false
    Object.assign(newTask, {
      title: '',
      description: '',
      status_id: 1,
      assignee_ids: [],
      priority: 'medium',
      due_date: null,
      estimated_hours: null
    })
  } catch (error) {
    console.error('创建任务失败:', error)
  }
}

const openTaskDetail = (taskId) => {
  router.push(`/task/${taskId}`)
}

// 根据状态获取任务
const fetchTasksByStatus = async (tabName) => {
  let statusId = null
  
  switch (tabName) {
    case 'inProgress':
      statusId = 2 // 进行中
      break
    case 'todo':
      statusId = 1 // 待办
      break
    case 'paused':
      statusId = 4 // 已暂停
      break
    case 'canceled':
      statusId = 5 // 已取消
      break
    case 'completed':
      statusId = 3 // 已完成
      break
    case 'all':
      // 全部任务，不需要状态过滤
      break
    default:
      statusId = 2 // 默认展示进行中
  }
  
  const filters = {}
  if (statusId !== null) {
    filters.status_id = statusId
  }
  
  // 查询对应状态的前1000条记录
  await taskStore.fetchTasks(filters, 1, 1000)
}

onMounted(async () => {
  await fetchTasksByStatus('inProgress') // 默认查询进行中的任务
  await taskStore.fetchStatuses()
})
</script>

<style scoped>
.board-container {
  padding: 10px;
  background-color: #f8fafc;
}

.board-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.board-tabs {
  flex-grow: 0;
}

.board-tabs .el-tabs__header {
  margin-bottom: 15px;
}

.board-tabs .el-tabs__active-bar {
  background-color: #3b82f6;
  height: 3px;
}

.board-tabs .el-tab-pane.is-active .el-tab-pane__inner {
  color: #3b82f6;
  font-weight: 600;
}

.board-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 15px;
}

@media (min-width: 1200px) {
  .board-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .board-grid {
    grid-template-columns: 1fr;
  }
}

.task-card {
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.task-card:hover {
  background-color: rgba(255, 255, 255, 0.95);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.25);
  transform: translateY(-2px) scale(1.01);
  border-color: rgba(59, 130, 246, 0.5);
}

.task-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  gap: 6px;
}

.task-card-header h4 {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  flex: 1;
  color: #1e293b;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.priority-badge {
  font-size: 9px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.priority-badge.high {
  background-color: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.priority-badge.medium {
  background-color: rgba(245, 158, 11, 0.1);
  color: #d97706;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.priority-badge.low {
  background-color: rgba(16, 185, 129, 0.1);
  color: #059669;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.status-tag {
  margin-left: auto;
  color: #ffffff;
  font-size: 10px;
  font-weight: 600;
  border-radius: 12px;
  padding: 2px 8px;
}

.task-card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 8px;
}

.task-tag {
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 500;
}

.task-card-description {
  font-size: 11px;
  color: #64748b;
  margin-bottom: 8px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.task-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 10px;
}

.task-assignee {
  display: flex;
  align-items: center;
  gap: 4px;
}

.task-assignees {
  display: flex;
  align-items: center;
  gap: -6px;
}

.task-assignees .el-avatar {
  margin-left: -6px;
  border: 2px solid #f8fafc;
  background-color: #3b82f6;
  color: white;
  font-size: 10px;
  font-weight: 600;
}

.task-assignees .el-avatar:first-child {
  margin-left: 0;
}

.task-assignee.unassigned {
  color: #94a3b8;
  font-style: normal;
  font-size: 9px;
}

.task-due-date {
  color: #64748b;
  font-size: 9px;
  font-weight: 500;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.task-due-date.overdue {
  color: #dc2626;
  font-weight: 600;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
