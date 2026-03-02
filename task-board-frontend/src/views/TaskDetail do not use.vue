<template>
  <div>
  <div class="task-detail-container">
    <div class="task-detail-header">
      <el-button @click="goBack">返回</el-button>
      <h1>{{ task.title }}</h1>
      <el-button type="primary" @click="openEditTaskDialog">编辑任务</el-button>
    </div>
    
    <div class="task-detail-content">
      <div class="task-info-section">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>任务信息</span>
              <span class="status-badge" :style="{ backgroundColor: task.status?.color }">
                {{ task.status?.name }}
              </span>
            </div>
          </template>
          
          <div class="task-info-grid">
            <div class="info-item">
              <span class="info-label">优先级：</span>
              <span class="priority-badge" :class="task.priority">{{ task.priority }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">创建人：</span>
              <span>{{ task.creator?.name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">负责人：</span>
              <div v-if="task.assignees && task.assignees.length > 0" class="assignees-list">
                <span v-for="assignee in task.assignees" :key="assignee.id" class="assignee-tag">
                  {{ assignee.name }}
                </span>
              </div>
              <span v-else-if="task.assignee" class="assignee-single">
                {{ task.assignee.name }}
              </span>
              <span v-else class="unassigned">未分配</span>
            </div>
            <div class="info-item">
              <span class="info-label">创建时间：</span>
              <span>{{ formatDate(task.created_at) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">截止日期：</span>
              <span v-if="task.due_date" :class="{ overdue: isOverdue(task.due_date) }">
                {{ formatDate(task.due_date) }}
              </span>
              <span v-else>未设置</span>
            </div>
            <div class="info-item">
              <span class="info-label">预估工时：</span>
              <span v-if="task.estimated_hours">{{ task.estimated_hours }} 小时</span>
              <span v-else>未设置</span>
            </div>
            <div class="info-item">
              <span class="info-label">实际工时：</span>
              <span v-if="task.actual_hours">{{ task.actual_hours }} 小时</span>
              <span v-else>未设置</span>
            </div>
          </div>
        </el-card>
      </div>
      
      <div class="task-description-section">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>任务描述</span>
            </div>
          </template>
          <div class="task-description">
            <CKEditorModule.Ckeditor
              :editor="editor"
              v-model="task.description"
              :config="{
                toolbar: [],
                readOnly: true
              }"
            />
          </div>
        </el-card>
      </div>
      
      <div class="task-comments-section">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>评论</span>
            </div>
          </template>
          
          <div class="comments-list">
            <div v-for="comment in comments" :key="comment.id" class="comment-item">
              <el-avatar size="small" class="comment-avatar">{{ getInitial(comment.user.name) }}</el-avatar>
              <div class="comment-content">
                <div class="comment-header">
                  <span class="comment-author">{{ comment.user.name }}</span>
                  <span class="comment-time">{{ formatDateTime(comment.created_at) }}</span>
                </div>
                <div class="comment-text">{{ comment.content }}</div>
              </div>
            </div>
            <div v-if="comments.length === 0" class="no-comments">
              暂无评论
            </div>
          </div>
          
          <div class="comment-form">
            <el-input
              type="textarea"
              v-model="newComment"
              placeholder="添加评论..."
              rows="3"
            ></el-input>
            <el-button type="primary" @click="addComment" :disabled="!newComment.trim()">发布评论</el-button>
          </div>
        </el-card>
      </div>
      
      <div class="task-attachments-section">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>附件</span>
            </div>
          </template>
          
          <div class="attachments-list">
            <div v-for="attachment in attachments" :key="attachment.id" class="attachment-item">
              <el-icon><i class="el-icon-document"></i></el-icon>
              <span class="attachment-filename">{{ attachment.filename }}</span>
              <span class="attachment-uploader">{{ attachment.user.name }}</span>
              <span class="attachment-time">{{ formatDateTime(attachment.created_at) }}</span>
            </div>
            <div v-if="attachments.length === 0" class="no-attachments">
              暂无附件
            </div>
          </div>
          
          <div class="attachment-upload">
            <el-upload
              class="upload-demo"
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :file-list="fileList"
              multiple
            >
              <el-button type="primary">
                <el-icon><i class="el-icon-upload"></i></el-icon>
                上传附件
              </el-button>
            </el-upload>
          </div>
        </el-card>
      </div>
    </div>
  </div>
  
  <!-- 编辑任务对话框 -->
  <el-dialog
    v-model="editTaskDialogVisible"
    title="编辑任务"
    width="600px"
  >
    <el-form :model="editTaskForm" :rules="taskRules" ref="editTaskFormRef" label-width="80px">
      <el-form-item label="任务标题" prop="title">
        <el-input v-model="editTaskForm.title" placeholder="请输入任务标题"></el-input>
      </el-form-item>
      <el-form-item label="任务描述" prop="description">
        <CKEditorModule.Ckeditor
          :editor="editor"
          v-model="editTaskForm.description"
          :config="{
            toolbar: [
              'heading',
              '|',
              'bold',
              'italic',
              'underline',
              'strikethrough',
              '|',
              'bulletedList',
              'numberedList',
              '|',
              'outdent',
              'indent',
              '|',
              'alignment',
              '|',
              'link',
              'blockquote',
              'imageUpload',
              '|',
              'insertTable',
              '|',
              'undo',
              'redo'
            ]
          }"
        />
      </el-form-item>
      <el-form-item label="状态" prop="status_id">
        <el-select v-model="editTaskForm.status_id" placeholder="请选择状态">
          <el-option v-for="status in statuses" :key="status.id" :label="status.name" :value="status.id"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="优先级" prop="priority">
        <el-select v-model="editTaskForm.priority" placeholder="请选择优先级">
          <el-option label="高" value="high"></el-option>
          <el-option label="中" value="medium"></el-option>
          <el-option label="低" value="low"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="负责人" prop="assignee_ids">
        <el-select v-model="editTaskForm.assignee_ids" placeholder="请选择负责人" multiple clearable>
          <el-option v-for="user in users" :key="user.id" :label="user.name" :value="user.id"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="截止日期" prop="due_date">
        <el-date-picker v-model="editTaskForm.due_date" type="date" placeholder="请选择截止日期" style="width: 100%"></el-date-picker>
      </el-form-item>
      <el-form-item label="预估工时" prop="estimated_hours">
        <el-input type="number" v-model="editTaskForm.estimated_hours" placeholder="请输入预估工时" min="0.5" step="0.5"></el-input>
      </el-form-item>
      <el-form-item label="实际工时" prop="actual_hours">
        <el-input type="number" v-model="editTaskForm.actual_hours" placeholder="请输入实际工时" min="0" step="0.5"></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="editTaskDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEditTask">保存</el-button>
      </span>
    </template>
  </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTaskStore } from '../store'
import dayjs from 'dayjs'
import api from '../api'
import { authApi } from '../api'
import ClassicEditor from '@ckeditor/ckeditor5-build-classic'
//@ts-ignore 
//import CKEditor from '@ckeditor/ckeditor5-vue'
//import { CKEditor } from '@ckeditor/ckeditor5-vue';
import * as CKEditorModule from '@ckeditor/ckeditor5-vue';

//const ckeditor = CKEditor.component
const editor = ClassicEditor;
const route = useRoute()
const router = useRouter()
const taskStore = useTaskStore()

const taskId = computed(() => parseInt(route.params.id))
const task = ref({})
const comments = ref([])
const attachments = ref([])
const newComment = ref('')
const fileList = ref([])
const editTaskDialogVisible = ref(false)
const editTaskFormRef = ref(null)
const users = ref([])

const statuses = ref([
  { id: 1, name: '待办', order_index: 1, color: '#94a3b8' },
  { id: 2, name: '进行中', order_index: 2, color: '#3b82f6' },
  { id: 3, name: '已完成', order_index: 3, color: '#10b981' },
  { id: 4, name: '已暂停', order_index: 4, color: '#f59e0b' },
  { id: 5, name: '已取消', order_index: 5, color: '#ef4444' }
])

const editTaskForm = reactive({
  title: '',
  description: '',
  status_id: 1,
  assignee_ids: [],
  priority: 'medium',
  due_date: null,
  estimated_hours: null,
  actual_hours: null
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

const getInitial = (name) => {
  return name.charAt(0).toUpperCase()
}

const formatDate = (dateString) => {
  return dateString ? dayjs(dateString).format('YYYY-MM-DD') : ''
}

const formatDateTime = (dateString) => {
  return dateString ? dayjs(dateString).format('YYYY-MM-DD HH:mm') : ''
}

const isOverdue = (dateString) => {
  return dateString && dayjs(dateString).isBefore(dayjs(), 'day')
}

const goBack = () => {
  router.back()
}

const openEditTaskDialog = async () => {
  // 先获取用户列表
  await fetchUsers()
  // 填充编辑表单
  const taskData = {
    title: task.value.title,
    description: task.value.description,
    status_id: task.value.status_id,
    priority: task.value.priority,
    due_date: task.value.due_date,
    estimated_hours: task.value.estimated_hours,
    actual_hours: task.value.actual_hours
  }
  
  // 处理负责人字段
  if (task.value.assignees && task.value.assignees.length > 0) {
    // 如果有多个负责人，使用 assignees 数组
    taskData.assignee_ids = task.value.assignees.map(assignee => assignee.id)
  } else if (task.value.assignee_id) {
    // 如果只有一个负责人 ID，转换为数组
    taskData.assignee_ids = [task.value.assignee_id]
  } else if (task.value.assignee) {
    // 如果有一个负责人对象，使用其 ID
    taskData.assignee_ids = [task.value.assignee.id]
  } else {
    // 没有负责人，使用空数组
    taskData.assignee_ids = []
  }
  
  Object.assign(editTaskForm, taskData)
  editTaskDialogVisible.value = true
}

const handleEditTask = async () => {
  if (!editTaskFormRef.value) return
  
  try {
    await editTaskFormRef.value.validate()
    await taskStore.updateTask(taskId.value, editTaskForm)
    await fetchTaskDetail()
    editTaskDialogVisible.value = false
  } catch (error) {
    console.error('编辑任务失败:', error)
  }
}

const fetchTaskDetail = async () => {
  try {
    const taskDetail = await taskStore.fetchTask(taskId.value)
    task.value = taskDetail
  } catch (error) {
    console.error('获取任务详情失败:', error)
  }
}

const fetchComments = async () => {
  try {
    const response = await api.get(`/tasks/${taskId.value}/comments`)
    comments.value = response.data
  } catch (error) {
    console.error('获取评论失败:', error)
  }
}

const fetchAttachments = async () => {
  try {
    const response = await api.get(`/tasks/${taskId.value}/attachments`)
    attachments.value = response.data
  } catch (error) {
    console.error('获取附件失败:', error)
  }
}

const fetchUsers = async () => {
  try {
    // 从 API 获取用户列表
    const response = await authApi.getUsers()
    // 过滤出角色为 admin、dev 或 pm 的用户
    users.value = response.data.filter(user => {
      return ['admin', 'dev', 'pm'].includes(user.role)
    })
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

const addComment = async () => {
  if (!newComment.value.trim()) return
  
  try {
    const response = await api.post(`/tasks/${taskId.value}/comments`, {
      content: newComment.value
    })
    comments.value.unshift(response.data)
    newComment.value = ''
  } catch (error) {
    console.error('添加评论失败:', error)
  }
}

const handleFileChange = (file, fileList) => {
  // 处理文件上传
  console.log('File selected:', file)
}

onMounted(async () => {
  await fetchTaskDetail()
  await fetchComments()
  await fetchAttachments()
})
</script>

<style scoped>
.task-detail-container {
  padding: 20px;
}

.task-detail-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 15px;
}

.task-detail-header h1 {
  flex: 1;
  margin: 0;
  font-size: 24px;
}

.task-detail-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-badge {
  color: white;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.task-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-label {
  font-weight: 500;
  color: #666;
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
  gap: 8px;
}

.assignee-tag {
  background-color: #e6f7ff;
  color: #1890ff;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.assignee-single {
  font-weight: 500;
}

.task-description {
  line-height: 1.6;
  color: #333;
}

.comments-list {
  margin-bottom: 20px;
}

.comment-item {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.comment-avatar {
  flex-shrink: 0;
}

.comment-content {
  flex: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.comment-author {
  font-weight: 500;
}

.comment-time {
  font-size: 12px;
  color: #999;
}

.comment-text {
  line-height: 1.4;
}

.no-comments {
  text-align: center;
  color: #999;
  padding: 20px 0;
}

.comment-form {
  margin-top: 20px;
}

.attachments-list {
  margin-bottom: 20px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.attachment-filename {
  flex: 1;
}

.attachment-uploader {
  font-size: 12px;
  color: #666;
}

.attachment-time {
  font-size: 12px;
  color: #999;
}

.no-attachments {
  text-align: center;
  color: #999;
  padding: 20px 0;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.overdue {
  color: #dc2626;
  font-weight: 600;
}
</style>
