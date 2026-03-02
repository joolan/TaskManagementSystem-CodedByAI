<template>
  <div class="release-form">
    <el-form :model="releaseForm" :rules="releaseRules" ref="releaseFormRef" label-width="120px">
      <el-form-item label="发版主题" prop="title">
        <el-input v-model="releaseForm.title" placeholder="请输入发版主题" style="width: 900px; max-width: 100%"></el-input>
      </el-form-item>
      
      <el-form-item label="发版详情" prop="description">
        <div style="width: 900px; max-width: 100%">
          <CustomRichTextEditor
            v-model="releaseForm.description"
            placeholder="请输入发版详情"
            :height="300"
          />
        </div>
      </el-form-item>
      
      <el-form-item label="发版状态" prop="status">
        <el-select v-model="releaseForm.status" placeholder="请选择发版状态" style="width: 200px">
          <el-option label="计划中" value="计划中"></el-option>
          <el-option label="已发版" value="已发版"></el-option>
          <el-option label="延期中" value="延期中"></el-option>
          <el-option label="已作废" value="已作废"></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="预计发版时间" prop="planned_release_date">
        <el-date-picker
          v-model="releaseForm.planned_release_date"
          type="datetime"
          placeholder="选择预计发版时间"
          style="width: 200px"
          format="YYYY-MM-DD HH:mm"
          value-format="YYYY-MM-DDTHH:mm:ss"
        ></el-date-picker>
      </el-form-item>
      
      <el-form-item label="实际发版时间" prop="actual_release_date">
        <el-date-picker
          v-model="releaseForm.actual_release_date"
          type="datetime"
          placeholder="选择实际发版时间"
          style="width: 200px"
          format="YYYY-MM-DD HH:mm"
          value-format="YYYY-MM-DDTHH:mm:ss"
        ></el-date-picker>
      </el-form-item>
      
      <el-form-item label="发版标签" prop="tag_ids">
        <el-select
          v-model="releaseForm.tag_ids"
          multiple
          placeholder="请选择发版标签"
          style="width: 900px; max-width: 100%"
        >
          <el-option
            v-for="tag in releaseTags"
            :key="tag.id"
            :label="tag.name"
            :value="tag.id"
          >
            <div class="tag-option">
              <span class="tag-color" :style="{ backgroundColor: tag.color }"></span>
              <span>{{ tag.name }}</span>
            </div>
          </el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="关联任务" prop="task_ids" >
        <div class="task-association" style="width: 900px; max-width: 100%">
          <TaskSelector
            v-model="releaseForm.task_ids"
            :exclude-task-ids="getExcludedTaskIds()"
            @confirm="handleTasksSelected"
          />
        </div>
        <div v-if="selectedTasksList.length > 0" class="selected-tasks-list">
          <div class="task-table-wrapper">
            <el-table :data="selectedTasksList" size="small" max-height="300" style="width: 100%">
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
              <el-table-column label="截止日期" width="140">
                <template #default="{ row }">
                  {{ formatDate(row.due_date) }}
                </template>
              </el-table-column>
              <el-table-column label="实际完成日期" width="140">
                <template #default="{ row }">
                  {{ formatDate(row.actual_completion_date) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <template #default="{ row }">
                  <el-button type="danger" link @click="removeTask(row.id)">
                    移除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="submitForm">保存</el-button>
        <el-button @click="resetForm">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useReleaseStore, useTaskStore } from '../store'
import CustomRichTextEditor from './CustomRichTextEditor.vue'
import TaskSelector from './TaskSelector.vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  releaseId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['save'])

const releaseStore = useReleaseStore()
const taskStore = useTaskStore()
const releaseFormRef = ref(null)
const releaseTags = ref([])
const selectedTasksList = ref([])
const excludedTaskIds = ref([])

const releaseForm = reactive({
  title: '',
  description: '',
  status: '计划中',
  planned_release_date: '',
  actual_release_date: '',
  tag_ids: [],
  task_ids: []
})

const releaseRules = {
  title: [
    { required: true, message: '请输入发版主题', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择发版状态', trigger: 'change' }
  ],
  planned_release_date: [
    { required: true, message: '请选择预计发版时间', trigger: 'change' }
  ]
}

const fetchReleaseTags = async () => {
  try {
    await releaseStore.fetchReleaseTags()
    releaseTags.value = releaseStore.releaseTags
  } catch (error) {
    console.error('获取发版标签失败:', error)
  }
}

const getPriorityType = (priority) => {
  const priorityMap = {
    '高': 'danger',
    '中': 'warning',
    '低': 'info',
    'high': 'danger',
    'medium': 'warning',
    'low': 'info'
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

const getExcludedTaskIds = () => {
  return excludedTaskIds.value
}

const handleTasksSelected = async (tasks) => {
  selectedTasksList.value = tasks
}

const removeTask = (taskId) => {
  releaseForm.task_ids = releaseForm.task_ids.filter(id => id !== taskId)
  selectedTasksList.value = selectedTasksList.value.filter(task => task.id !== taskId)
}

const loadReleaseData = async () => {
  if (props.releaseId) {
    try {
      const release = await releaseStore.fetchRelease(props.releaseId)
      releaseForm.title = release.title
      releaseForm.description = release.description
      releaseForm.status = release.status
      releaseForm.planned_release_date = release.planned_release_date
      releaseForm.actual_release_date = release.actual_release_date
      releaseForm.tag_ids = release.tags.map(tag => tag.id)
      releaseForm.task_ids = release.tasks.map(task => task.id)
      
      await taskStore.fetchStatuses()
      
      selectedTasksList.value = release.tasks.map(task => ({
        id: task.id,
        title: task.title,
        status_id: task.status_id,
        status: task.status || task.status_info,
        priority: task.priority,
        due_date: task.due_date,
        actual_completion_date: task.actual_completion_date
      }))
    } catch (error) {
      console.error('获取发版详情失败:', error)
    }
  }
}

const submitForm = async () => {
  if (!releaseFormRef.value) return
  
  try {
    await releaseFormRef.value.validate()
    
    const releaseData = {
      ...releaseForm,
      planned_release_date: releaseForm.planned_release_date || null,
      actual_release_date: releaseForm.actual_release_date || null
    }
    
    if (props.releaseId) {
      await releaseStore.updateRelease(props.releaseId, releaseData)
    } else {
      await releaseStore.createRelease(releaseData)
    }
    
    emit('save')
  } catch (error) {
    console.error('保存发版记录失败:', error)
    // 显示后端返回的错误信息
    if (error.response && error.response.data && error.response.data.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('保存失败，请稍后重试')
    }
  }
}

const resetForm = () => {
  if (props.releaseId) {
    loadReleaseData()
  } else {
    Object.assign(releaseForm, {
      title: '',
      description: '',
      status: '计划中',
      planned_release_date: '',
      actual_release_date: '',
      tag_ids: [],
      task_ids: []
    })
  }
}

onMounted(async () => {
  await fetchReleaseTags()
  await loadExcludedTaskIds()
  if (props.releaseId) {
    await loadReleaseData()
  }
})

const loadExcludedTaskIds = async () => {
  try {
    // Fetch all releases to get tasks already associated with other releases
    await releaseStore.fetchReleases({}, 1, 1000)
    const excludedIds = new Set()
    
    releaseStore.releases.forEach(release => {
      // Skip current release if editing
      if (release.id === props.releaseId) return
      
      if (release.tasks) {
        release.tasks.forEach(task => {
          excludedIds.add(task.id)
        })
      }
    })
    
    excludedTaskIds.value = Array.from(excludedIds)
  } catch (error) {
    console.error('获取已关联任务失败:', error)
    excludedTaskIds.value = []
  }
}

watch(() => props.releaseId, (newId) => {
  if (newId) {
    loadReleaseData()
  }
})
</script>

<style scoped>
.release-form {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.tag-option {
  display: flex;
  align-items: center;
}

.tag-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 8px;
}

.task-association {
  display: block;
  width: 100%;
  margin-bottom: 12px;
}

.task-association .el-button {
  width: auto;
}

.selected-tasks-list {
  margin-top: 12px;
}

.task-table-wrapper {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  width: 100%;
  max-width: 900px;
  overflow-x: auto;
}
</style>
