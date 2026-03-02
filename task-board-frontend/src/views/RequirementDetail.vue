<template>
  <div class="requirement-detail-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button @click="handleBack">返回</el-button>
            <span>需求详情</span>
          </div>
        </div>
      </template>
      
      <div class="requirement-detail">
        <div class="detail-section">
          <h3>基本信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="需求ID">{{ requirementData.id }}</el-descriptions-item>
            <el-descriptions-item label="需求状态">
              <el-tag :type="getStatusType(requirementData.status)">{{ requirementData.status }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="需求来源">{{ requirementData.source }}</el-descriptions-item>
            <el-descriptions-item label="需求名称">{{ requirementData.name }}</el-descriptions-item>
            <el-descriptions-item label="需求标签">
              <el-tag 
                v-if="requirementData.tag" 
                :style="{ backgroundColor: requirementData.tag.color + '20', color: requirementData.tag.color }"
              >
                {{ requirementData.tag.name }}
              </el-tag>
              <span v-else>-</span>
            </el-descriptions-item>
            <el-descriptions-item label="需求优先级">
              <el-tag :type="getPriorityType(requirementData.priority)">{{ requirementData.priority }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建人">{{ requirementData.creator?.name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ requirementData.created_at }}</el-descriptions-item>
            <el-descriptions-item label="计划完成日期">{{ requirementData.planned_completion_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="实际完成日期">{{ requirementData.actual_completion_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="关联任务" span="2">
              <el-link 
                v-if="requirementData.task_id" 
                type="primary" 
                @click="handleViewTask(requirementData.task_id)"
              >
                查看任务 #{{ requirementData.task_id }}
              </el-link>
              <span v-else>-</span>
            </el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="detail-section">
          <h3>需求描述</h3>
          <div class="description-content" v-html="requirementData.description"></div>
        </div>
        
        <div class="action-buttons">
          <el-button 
            type="primary" 
            @click="handleEditRequirement"
            :disabled="isViewer || requirementData.status === '已转任务'"
          >
            编辑
          </el-button>
          <el-button 
            type="success" 
            @click="handleConvertToTask"
            :disabled="isViewer || requirementData.status === '已转任务'"
          >
            转任务
          </el-button>
          <el-button 
            type="danger" 
            @click="handleDeleteRequirement"
            :disabled="isViewer"
          >
            删除
          </el-button>
        </div>
      </div>
    </el-card>
    
    <!-- 转任务对话框 -->
    <el-dialog
      v-model="convertToTaskDialogVisible"
      title="转任务"
      width="60%"
    >
      <el-form :model="taskForm" label-width="100px">
        <el-form-item label="任务标题">
          <el-input v-model="taskForm.title" placeholder="请输入任务标题" />
        </el-form-item>
        <el-form-item label="任务描述">
          <CustomRichTextEditor v-model="taskForm.description" />
        </el-form-item>
        <el-form-item label="任务状态">
          <el-select v-model="taskForm.status_id" placeholder="请选择任务状态">
            <el-option 
              v-for="status in taskStatuses" 
              :key="status.id" 
              :label="status.name" 
              :value="status.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人">
          <el-select v-model="taskForm.assignee_id" placeholder="请选择负责人">
            <el-option 
              v-for="user in users" 
              :key="user.id" 
              :label="user.name" 
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="taskForm.priority" placeholder="请选择优先级">
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
import { requirementApi, authApi } from '../api/index'
import { useUserStore } from '../store'
import api from '../api/index'
import CustomRichTextEditor from '../components/CustomRichTextEditor.vue'

const router = useRouter()
const route = useRoute()
const store = useUserStore()

// 状态管理
const requirementData = ref({})
const taskStatuses = ref([
  { id: 1, name: '待办', order_index: 1, color: '#94a3b8' },
  { id: 2, name: '进行中', order_index: 2, color: '#3b82f6' },
  { id: 3, name: '已完成', order_index: 3, color: '#10b981' },
  { id: 4, name: '已暂停', order_index: 4, color: '#f59e0b' },
  { id: 5, name: '已取消', order_index: 5, color: '#ef4444' }
])
const users = ref([])
const isViewer = computed(() => store.user.role === 'viewer')
const requirementId = computed(() => route.params.id)

// 转任务对话框
const convertToTaskDialogVisible = ref(false)
const taskForm = ref({
  title: '',
  description: '',
  status_id: '',
  assignee_id: '',
  priority: '',
  due_date: ''
})

// 获取需求详情
const fetchRequirementDetail = async () => {
  if (!requirementId.value) return
  
  try {
    const response = await requirementApi.getRequirement(requirementId.value)
    requirementData.value = response.data
  } catch (error) {
    console.error('获取需求详情失败:', error)
    ElMessage.error('获取需求详情失败')
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

// 初始加载
onMounted(async () => {
  await fetchRequirementDetail()
  await fetchUsers()
})

// 处理返回列表
const handleBack = () => {
  router.push('/requirements')
}

// 处理编辑需求
const handleEditRequirement = () => {
  router.push(`/requirement/edit/${requirementId.value}`)
}

// 处理查看任务
const handleViewTask = (taskId) => {
  router.push(`/task/${taskId}`)
}

// 处理转任务
const handleConvertToTask = () => {
  taskForm.value = {
    title: requirementData.value.name,
    description: requirementData.value.description,
    status_id: '',
    assignee_id: '',
    priority: requirementData.value.priority,
    due_date: requirementData.value.planned_completion_date
  }
  convertToTaskDialogVisible.value = true
}

// 提交转任务
const submitConvertToTask = async () => {
  if (!requirementId.value) return
  
  try {
    await requirementApi.convertToTask(requirementId.value, taskForm.value)
    ElMessage.success('转任务成功')
    convertToTaskDialogVisible.value = false
    await fetchRequirementDetail()
  } catch (error) {
    console.error('转任务失败:', error)
    ElMessage.error('转任务失败')
  }
}

// 处理删除需求
const handleDeleteRequirement = () => {
  ElMessageBox.confirm('确定要删除这个需求吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  .then(async () => {
    if (!requirementId.value) return
    
    try {
      await requirementApi.deleteRequirement(requirementId.value)
      ElMessage.success('删除成功')
      router.push('/requirements')
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  })
  .catch(() => {
    // 取消删除
  })
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
</script>

<style scoped>
.requirement-detail-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-left span {
  font-size: 18px;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eaeaea;
}

.requirement-detail {
  margin-top: 20px;
}

.detail-section {
  margin-bottom: 30px;
}

.detail-section h3 {
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: 500;
  color: #333;
  border-left: 4px solid #409EFF;
  padding-left: 10px;
}

.description-content {
  padding: 20px;
  background-color: #f9fafb;
  border-radius: 8px;
  min-height: 200px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
