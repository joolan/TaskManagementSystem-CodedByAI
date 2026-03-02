<template>
  <div class="task-selector">
    <el-button type="primary" @click="openDialog">
      <el-icon><Plus /></el-icon>
      添加任务
    </el-button>

    <el-dialog
      v-model="dialogVisible"
      title="选择关联任务"
      width="80%"
      :close-on-click-modal="false"
      @close="handleClose"
    >
      <div class="task-selector-content">
        <div class="filter-bar">
          <el-input
            v-model="filterKeyword"
            placeholder="搜索任务标题"
            clearable
            style="width: 300px"
            @input="handleFilter"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-select
            v-model="filterStatus"
            placeholder="任务状态"
            clearable
            style="width: 150px"
            @change="handleFilter"
          >
            <el-option
              v-for="status in statuses"
              :key="status.id"
              :label="status.name"
              :value="status.id"
            ></el-option>
          </el-select>
          
          <el-select
            v-model="filterPriority"
            placeholder="优先级"
            clearable
            style="width: 150px"
            @change="handleFilter"
          >
            <el-option label="高" value="高"></el-option>
            <el-option label="中" value="中"></el-option>
            <el-option label="低" value="低"></el-option>
          </el-select>
        </div>

        <div class="task-table-container">
          <el-table
            ref="taskTableRef"
            :data="filteredTasks"
            v-loading="loading"
            @selection-change="handleSelectionChange"
            height="400"
            style="width: 100%; max-width: 900px"
          >
            <el-table-column type="selection" width="55"></el-table-column>
            
            <el-table-column prop="id" label="任务ID" width="80"></el-table-column>
            
            <el-table-column prop="title" label="任务标题" min-width="200" max-width="400" show-overflow-tooltip></el-table-column>
            
            <el-table-column label="任务状态" width="100">
              <template #default="{ row }">
                <el-tag :color="row.status?.color || '#909399'" size="small" effect="dark" style="border: none;">
                  {{ row.status?.name || '未知' }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="优先级" width="80">
              <template #default="{ row }">
                <el-tag :type="getPriorityType(row.priority)" size="small">
                  {{ getPriorityName(row.priority) }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="截止日期" width="160">
              <template #default="{ row }">
                {{ formatDate(row.due_date) }}
              </template>
            </el-table-column>
            
            <el-table-column label="实际完成日期" width="160">
              <template #default="{ row }">
                {{ formatDate(row.actual_completion_date) }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="selected-info">
          <span>已选择 {{ selectedTasks.length }} 个任务</span>
        </div>
      </div>

      <template #footer>
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleConfirm" :disabled="selectedTasks.length === 0">
          确认添加 ({{ selectedTasks.length }})
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { useTaskStore } from '../store'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  excludeTaskIds: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'confirm'])

const taskStore = useTaskStore()
const dialogVisible = ref(false)
const loading = ref(false)
const tasks = ref([])
const statuses = ref([])
const selectedTasks = ref([])
const filterKeyword = ref('')
const filterStatus = ref(null)
const filterPriority = ref('')
const taskTableRef = ref(null)

const filteredTasks = computed(() => {
  let result = tasks.value.filter(task => 
    !props.excludeTaskIds.includes(task.id)
  )
  
  if (filterKeyword.value) {
    result = result.filter(task =>
      task.title.toLowerCase().includes(filterKeyword.value.toLowerCase())
    )
  }
  
  if (filterStatus.value) {
    result = result.filter(task => task.status_id === filterStatus.value)
  }
  
  if (filterPriority.value) {
    result = result.filter(task => task.priority === filterPriority.value)
  }
  
  return result
})

const getPriorityType = (priority) => {
  const priorityMap = {
    'high': 'danger',
    'medium': 'warning',
    'low': 'info',
  }
  return priorityMap[priority] || 'info'
}
const getPriorityName = (priority) => {
  const priorityMap = {
    'high': '高',
    'medium': '中',
    'low': '低'
  }
  return priorityMap[priority] || priority
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const openDialog = async () => {
  dialogVisible.value = true
  await loadTasks()
}

const loadTasks = async () => {
  loading.value = true
  try {
    await taskStore.fetchTasks({}, 1, 1000)
    tasks.value = taskStore.tasks
    
    await taskStore.fetchStatuses()
    statuses.value = taskStore.statuses
    
    setTimeout(() => {
      restoreSelection()
    }, 100)
  } catch (error) {
    console.error('加载任务失败:', error)
  } finally {
    loading.value = false
  }
}

const restoreSelection = () => {
  if (taskTableRef.value) {
    taskTableRef.value.clearSelection()
    props.modelValue.forEach(taskId => {
      const task = tasks.value.find(t => t.id === taskId)
      if (task) {
        taskTableRef.value.toggleRowSelection(task, true)
      }
    })
  }
}

const handleFilter = () => {
  
}

const handleSelectionChange = (selection) => {
  selectedTasks.value = selection
}

const handleClose = () => {
  dialogVisible.value = false
  selectedTasks.value = []
  filterKeyword.value = ''
  filterStatus.value = null
  filterPriority.value = ''
}

const handleConfirm = () => {
  const selectedTaskIds = selectedTasks.value.map(task => task.id)
  emit('update:modelValue', selectedTaskIds)
  emit('confirm', selectedTasks.value)
  handleClose()
}

onMounted(() => {
  
})

watch(() => props.modelValue, () => {
  if (dialogVisible.value) {
    restoreSelection()
  }
})
</script>

<style scoped>
.task-selector {
  display: inline-block;
}

.task-selector-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  align-items: center;
}

.task-table-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
}

.selected-info {
  text-align: right;
  color: #606266;
  font-size: 14px;
}
</style>