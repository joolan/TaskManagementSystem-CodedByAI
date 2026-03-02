<template>
  <div class="task-form-container">
    <div class="task-form-header">
      <el-button @click="goBack">返回</el-button>
      <h1>{{ isEditMode ? '编辑任务' : '创建任务' }}</h1>
    </div>
    
    <div class="task-form-content">
      <el-form :model="taskForm" :rules="rules" ref="taskFormRef" label-width="120px">
        <el-form-item label="任务标题" prop="title" class="full-width">
          <el-input v-model="taskForm.title" placeholder="请输入任务标题"></el-input>
        </el-form-item>
        <el-form-item label="任务描述" prop="description" class="full-width">
          <CustomRichTextEditor v-model="taskForm.description" />
        </el-form-item>
        <el-form-item label="负责人" prop="assignee_ids" class="full-width">
          <el-select v-model="taskForm.assignee_ids" placeholder="请选择负责人" multiple clearable style="width: 100%">
            <el-option v-for="user in users" :key="user.id" :label="user.name" :value="user.id"></el-option>
          </el-select>
        </el-form-item>
        <div class="form-row">
          <el-form-item label="状态" prop="status_id">
            <el-select v-model="taskForm.status_id" placeholder="请选择状态" style="width: 100%" :disabled="isReleased">
              <el-option v-for="status in statuses" :key="status.id" :label="status.name" :value="status.id"></el-option>
            </el-select>
            <el-tooltip v-if="isReleased" content="已关联发版的任务禁止修改状态" placement="right">
              <el-icon class="info-icon"><i class="el-icon-info"></i></el-icon>
            </el-tooltip>
          </el-form-item>
          <el-form-item label="优先级" prop="priority">
            <el-select v-model="taskForm.priority" placeholder="请选择优先级" style="width: 100%">
              <el-option label="高" value="high"></el-option>
              <el-option label="中" value="medium"></el-option>
              <el-option label="低" value="low"></el-option>
            </el-select>
          </el-form-item>
        </div>
        <div class="form-row">
          <el-form-item label="预计完成时间" prop="due_date">
            <el-date-picker v-model="taskForm.due_date" type="date" placeholder="请选择预计完成时间" style="width: 100%"></el-date-picker>
          </el-form-item>
          <el-form-item label="实际开始日期" prop="actual_start_date">
            <el-date-picker v-model="taskForm.actual_start_date" type="date" placeholder="请选择实际开始日期" style="width: 100%"></el-date-picker>
          </el-form-item>
        </div>
        <div class="form-row">
          <el-form-item label="实际完成日期" prop="actual_completion_date">
            <el-date-picker v-model="taskForm.actual_completion_date" type="date" placeholder="请选择实际完成日期" style="width: 100%"></el-date-picker>
          </el-form-item>
          <el-form-item label="预估工时" prop="estimated_hours">
            <el-input type="number" v-model="taskForm.estimated_hours" placeholder="请输入预估工时" min="0.5" step="0.5"></el-input>
          </el-form-item>
        </div>
        <div class="form-row">
          <el-form-item label="实际工时" prop="actual_hours">
            <el-input type="number" v-model="taskForm.actual_hours" placeholder="请输入实际工时" min="0" step="0.5"></el-input>
          </el-form-item>
        </div>
        <el-form-item label="标签" class="full-width">
          <el-select v-model="taskForm.tag_ids" placeholder="请选择标签" multiple clearable style="width: 100%">
            <el-option v-for="tag in tags" :key="tag.id" :label="tag.name" :value="tag.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">保存</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTaskStore, useUserStore, useReleaseStore } from '../store'
import { authApi } from '../api'
import api from '../api'
import CustomRichTextEditor from '../components/CustomRichTextEditor.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const taskStore = useTaskStore()
const userStore = useUserStore()
const releaseStore = useReleaseStore()

const taskFormRef = ref(null)
const loading = ref(false)
const error = ref('')

// 响应式数据：任务关联的发版记录状态
const taskReleaseStatus = ref('')
const isLoadingReleaseStatus = ref(false)

const taskId = computed(() => route.params.id)
const isEditMode = computed(() => !!taskId.value)

const statuses = ref([
  { id: 1, name: '待办', order_index: 1, color: '#94a3b8' },
  { id: 2, name: '进行中', order_index: 2, color: '#3b82f6' },
  { id: 3, name: '已完成', order_index: 3, color: '#10b981' },
  { id: 4, name: '已暂停', order_index: 4, color: '#f59e0b' },
  { id: 5, name: '已取消', order_index: 5, color: '#ef4444' }
])

const users = ref([])

// 标签列表
const tags = ref([])

const taskForm = reactive({
  title: '',
  description: '',
  status_id: 1,
  assignee_ids: [],
  tag_ids: [],
  priority: 'medium',
  due_date: null,
  actual_start_date: null,
  actual_completion_date: null,
  estimated_hours: null,
  actual_hours: null,
  release_id: null
})

// 获取任务关联的发版记录状态
const fetchTaskReleaseStatus = async () => {
  if (!taskForm.release_id) {
    taskReleaseStatus.value = ''
    return
  }
  
  isLoadingReleaseStatus.value = true
  try {
    const release = await releaseStore.fetchRelease(taskForm.release_id)
    taskReleaseStatus.value = release.status
  } catch (error) {
    console.error('获取发版详情失败:', error)
    taskReleaseStatus.value = ''
  } finally {
    isLoadingReleaseStatus.value = false
  }
}

// 计算任务是否关联到已发版的发版记录
const isReleased = computed(() => {
  return taskReleaseStatus.value === '已发版'
})

// TinyMCE编辑器不需要额外的实例创建和监听器，
// 因为它通过v-model直接与数据绑定

const rules = {
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

const goBack = () => {
  router.back()
}

const handleSubmit = async () => {
  if (!taskFormRef.value) return
  
  try {
    await taskFormRef.value.validate()
    loading.value = true
    error.value = ''
    
    if (isEditMode.value) {
      await taskStore.updateTask(taskId.value, taskForm)
    } else {
      await taskStore.createTask(taskForm)
    }
    
    router.push('/board')
  } catch (error) {
    console.error('保存任务失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchTask = async () => {
  if (!isEditMode.value) return
  
  try {
    const task = await taskStore.fetchTask(taskId.value)
    // 处理 assignee_ids 字段
    if (task.assignees && task.assignees.length > 0) {
      // 如果后端返回的是多个 assignees，使用其 ID 数组
      task.assignee_ids = task.assignees.map(assignee => assignee.id)
    } else if (task.assignee_id) {
      // 如果后端返回的是单个 assignee_id，转换为数组
      task.assignee_ids = [task.assignee_id]
      delete task.assignee_id
    } else if (task.assignee) {
      // 如果后端返回的是单个 assignee 对象，使用其 ID
      task.assignee_ids = [task.assignee.id]
      delete task.assignee
    }
    // 处理标签字段
    if (task.tags && task.tags.length > 0) {
      task.tag_ids = task.tags.map(tag => tag.id)
    }
    Object.assign(taskForm, task)
    // 获取任务关联的发版记录状态
    await fetchTaskReleaseStatus()
  } catch (error) {
    console.error('获取任务详情失败:', error)
  }
}

const fetchTags = async () => {
  try {
    const response = await api.get('/tasks/tags/all')
    tags.value = response.data
  } catch (error) {
    console.error('获取标签列表失败:', error)
    // 出错时使用默认标签
    tags.value = [
      { id: 1, name: '前端', color: '#60a5fa' },
      { id: 2, name: '后端', color: '#34d399' },
      { id: 3, name: 'UI/UX', color: '#f472b6' }
    ]
  }
}

const fetchUsers = async () => {
  try {
    // 从 API 获取用户列表
    const response = await authApi.getUsersBasic()
    users.value = response.data
  } catch (error) {
    console.error('获取用户列表失败:', error)
    // 出错时使用模拟数据
    users.value = [
      { id: 1, name: '管理员', username: 'admin', role: 'admin' },
      { id: 2, name: '开发人员', username: 'dev', role: 'dev' },
      { id: 3, name: '项目经理', username: 'pm', role: 'pm' }
    ]
  }
}

onMounted(async () => {
  await fetchUsers()
  await fetchTags()
  if (isEditMode.value) {
    await fetchTask()
  }
})
</script>

<style scoped>
.task-form-container {
  padding: 20px;
}

.task-form-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 15px;
}

.task-form-header h1 {
  flex: 1;
  margin: 0;
  font-size: 24px;
}

.task-form-content {
  max-width: 900px;
}

.full-width {
  width: 100%;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 0;
}

.form-row .el-form-item {
  flex: 1;
  min-width: 0;
}
</style>
