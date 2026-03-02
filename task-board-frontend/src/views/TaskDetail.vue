<template>
  <div>
    <div class="task-detail-container">
    <div class="task-detail-header">
      <el-button @click="goBack">返回</el-button>
      <h1>{{ task.title }}</h1>
      <el-button @click="openTaskLogDialog">任务日志</el-button>
      <el-button v-permission="'task:hours'" @click="openAddHourDialog">工时填报</el-button>
      <el-button v-permission="'task:update'" type="primary" @click="openEditTaskDialog">编辑任务</el-button>
    </div>
    
    <div class="task-detail-content">
      <div class="task-info-section">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>任务信息</span>
              <div class="header-actions">
                <span class="status-badge" :style="{ backgroundColor: task.status?.color }">
                  {{ task.status?.name }}
                </span>
                <el-button 
                  :type="isFollowing ? 'warning' : 'primary'" 
                  @click="toggleFollow"
                  size="small"
                >
                  {{ isFollowing ? '取消关注' : '关注' }}
                </el-button>
              </div>
            </div>
          </template>
          
          <div class="task-info-grid">
            <div class="info-item">
              <span class="info-label">优先级：</span>
              <span class="priority-badge" :class="task.priority">{{ getPriorityText(task.priority) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">创建人：</span>
              <span>{{ task.creator?.name }}</span>
            </div>
            
            <div class="info-item">
              <span class="info-label">创建时间：</span>
              <span>{{ formatDate(task.created_at) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">预计完成时间：</span>
              <span v-if="task.due_date" :class="{ overdue: isOverdue(task.due_date) }">
                {{ formatDate(task.due_date) }}
              </span>
              <span v-else>未设置</span>
            </div>
            <div class="info-item">
              <span class="info-label">实际开始日期：</span>
              <span v-if="task.actual_start_date">{{ formatDate(task.actual_start_date) }}</span>
              <span v-else>未设置</span>
            </div>
            <div class="info-item">
              <span class="info-label">实际完成日期：</span>
              <span v-if="task.actual_completion_date">{{ formatDate(task.actual_completion_date) }}</span>
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
            <div class="info-item">
              <span class="info-label">累计工时：</span>
              <el-button 
                type="text" 
                class="total-hours-button"
                @click="openHourListDialog"
              >
                {{ taskHoursStats.total_hours.toFixed(1) }} 小时
              </el-button>
            </div>
            <div class="info-item">
              <span class="info-label">标签：</span>
              <div v-if="task.tags && task.tags.length > 0" class="tags-list">
              <span 
                v-for="tag in task.tags" 
                :key="tag.id" 
                class="task-tag"
                :style="{ backgroundColor: (tag.color || '#60a5fa') + '20', color: tag.color || '#60a5fa' }"
              >
                {{ tag.name }}
              </span>
            </div>
              <span v-else>无</span>
            </div>
          </div>
          <div class="task-info-grid">
            <div class="info-item full-width ">
              <div class="assignees-header">
                <span class="info-label">负责人：</span>
              <div v-if="task.assignees && task.assignees.length > 0" >
                <el-tag v-for="assignee in task.assignees" :key="assignee.id" size="small" type="primary" class="assignee-tag">
                  {{ assignee.name }}
                </el-tag>
                
              </div>
              <span v-else-if="task.assignee" class="assignee-single">
                {{ task.assignee.name }}
              </span>
              <span v-else class="unassigned">未分配</span>
              </div>
            </div>
          </div>
          <div class="task-info-grid">
            <div class="info-item full-width ">
              <div class="followers-header">
                <span class="info-label">关注人：</span>
              <div v-if="followers.length > 0" >
                <el-tag v-for="follower in followers" :key="follower.id" size="small" type="info" class="follower-tag">
                  {{ follower.name }}
                </el-tag>
              </div>
              <span v-else class="no-followers">暂无关注人</span>
              </div>
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
              <CustomRichTextEditor 
                v-model="task.description"
                :readonly="true"
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
              <el-avatar size="small" class="comment-avatar">{{ getInitial(comment.is_anonymous ? '匿名用户' : comment.user.name) }}</el-avatar>
              <div class="comment-content">
                <div class="comment-header">
                  <div class="comment-header-left">
                    <span class="comment-author">{{ comment.is_anonymous ? '匿名用户' : comment.user.name }}</span>
                    <el-tag v-if="comment.pinned_at" type="danger" size="small" class="pinned-badge">置顶</el-tag>
                  </div>
                  <div class="comment-header-right">
                    <span class="comment-time">{{ formatDateTime(comment.created_at) }}</span>
                    <el-button 
                      v-if="isAdmin" 
                      type="text" 
                      size="small" 
                      @click="togglePinComment(comment.id)"
                      class="pin-button"
                    >
                      {{ comment.pinned_at ? '取消置顶' : '置顶' }}
                    </el-button>
                  </div>
                </div>
                <div class="comment-text">{{ comment.content }}</div>
                <!-- 显示评论附件 -->
                <div v-if="comment.attachments && comment.attachments.length > 0" class="comment-attachments">
                  <div v-for="attachment in comment.attachments" :key="attachment.id" class="comment-attachment-item">
                    <el-icon><Document /></el-icon>
                    <a href="#" @click.prevent="downloadAttachment(attachment.id, attachment.filename)" class="attachment-link">{{ attachment.filename }}</a>
                  </div>
                </div>
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
            <div class="comment-options">
              <el-checkbox v-model="isAnonymousComment" v-if="!isViewer">
                匿名评论
              </el-checkbox>
            </div>
            <div class="comment-upload">
              <el-upload
                class="upload-demo"
                action="#"
                :auto-upload="true"
                :on-change="handleCommentFileChange"
                :file-list="commentFileList"
                multiple
              >
                <el-button size="small">
                  <el-icon><i class="el-icon-upload"></i></el-icon>
                  添加附件
                </el-button>
              </el-upload>
            </div>
            <!-- 评论附件列表 -->
            <div v-if="commentFileList.length > 0" class="comment-attachments-list">
              <div v-for="(attachment, index) in commentFileList" :key="attachment.id" class="comment-attachment-item">
                <el-icon><i class="el-icon-document"></i></el-icon>
                <span class="attachment-filename">{{ attachment.filename }}</span>
                <el-button
                  type="text"
                  size="small"
                  class="attachment-delete"
                  @click="deleteCommentAttachment(index)"
                >
                  <el-icon><i class="el-icon-delete"></i></el-icon>
                  删除
                </el-button>
              </div>
            </div>
            <el-button type="primary" @click="addComment" :disabled="!newComment.trim()">发布评论</el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
  
  <!-- 编辑任务对话框 -->
  <el-dialog
    v-model="editTaskDialogVisible"
    title="编辑任务"
    width="900px"
  >
    <el-form :model="editTaskForm" :rules="taskRules" ref="editTaskFormRef" label-width="120px">
      <el-form-item label="任务标题" prop="title" class="full-width">
        <el-input v-model="editTaskForm.title" placeholder="请输入任务标题"></el-input>
      </el-form-item>
      <el-form-item label="任务描述" prop="description" class="full-width">
        <CustomRichTextEditor v-model="editTaskForm.description" />
      </el-form-item>
      <el-form-item label="负责人" prop="assignee_ids" class="full-width">
        <el-select v-model="editTaskForm.assignee_ids" placeholder="请选择负责人" multiple clearable style="width: 100%">
          <el-option v-for="user in users" :key="user.id" :label="user.name" :value="user.id"></el-option>
        </el-select>
      </el-form-item>
      <div class="form-row">
        <el-form-item label="状态" prop="status_id">
          <el-select v-model="editTaskForm.status_id" placeholder="请选择状态" style="width: 100%" :disabled="isTaskInReleasedRelease">
            <el-option v-for="status in statuses" :key="status.id" :label="status.name" :value="status.id"></el-option>
          </el-select>
          <el-tooltip v-if="isTaskInReleasedRelease" content="任务已关联到已发版的发版记录，禁止修改状态" placement="right">
            <el-icon class="info-icon"><i class="el-icon-question"></i></el-icon>
          </el-tooltip>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="editTaskForm.priority" placeholder="请选择优先级" style="width: 100%">
            <el-option label="高" value="high"></el-option>
            <el-option label="中" value="medium"></el-option>
            <el-option label="低" value="low"></el-option>
          </el-select>
        </el-form-item>
      </div>
      <div class="form-row">
        <el-form-item label="预计完成时间" prop="due_date">
          <el-date-picker v-model="editTaskForm.due_date" type="date" placeholder="请选择预计完成时间" style="width: 100%"></el-date-picker>
        </el-form-item>
        <el-form-item label="实际开始日期" prop="actual_start_date">
          <el-date-picker v-model="editTaskForm.actual_start_date" type="date" placeholder="请选择实际开始日期" style="width: 100%"></el-date-picker>
        </el-form-item>
      </div>
      <div class="form-row">
        <el-form-item label="实际完成日期" prop="actual_completion_date">
          <el-date-picker v-model="editTaskForm.actual_completion_date" type="date" placeholder="请选择实际完成日期" style="width: 100%"></el-date-picker>
        </el-form-item>
        <el-form-item label="预估工时" prop="estimated_hours">
          <el-input type="number" v-model="editTaskForm.estimated_hours" placeholder="请输入预估工时" min="0.5" step="0.5"></el-input>
        </el-form-item>
      </div>
      <div class="form-row">
        <el-form-item label="实际工时" prop="actual_hours">
          <el-input type="number" v-model="editTaskForm.actual_hours" placeholder="请输入实际工时" min="0" step="0.5"></el-input>
        </el-form-item>
      </div>
      <el-form-item label="标签" class="full-width">
        <el-select v-model="editTaskForm.tag_ids" placeholder="请选择标签" multiple clearable style="width: 100%">
          <el-option v-for="tag in tags" :key="tag.id" :label="tag.name" :value="tag.id"></el-option>
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="editTaskDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEditTask">保存</el-button>
      </span>
    </template>
  </el-dialog>
  
  <!-- 任务日志对话框 -->
  <!-- 任务日志对话框 -->
  <el-dialog
    v-model="taskLogDialogVisible"
    title="任务日志"
    width="800px"
  >
    <div class="task-logs-container">
      <div v-if="taskLogs.length === 0" class="no-logs">
        暂无任务日志
      </div>
      <div v-else class="task-logs-timeline">
        <div v-for="(log, index) in taskLogs" :key="log.id" class="task-log-item">
          <div class="timeline-node" :class="getLogNodeClass(log.action_type)" />
          <div class="timeline-line" v-if="index < taskLogs.length - 1"></div>
          <div class="log-content">
            <div class="log-header">
              <div class="log-title">{{ log.title }}</div>
              <div class="log-meta">
                <span class="log-user">{{ log.user.name }}</span>
                <span class="log-time">{{ formatDateTime(log.created_at) }}</span>
              </div>
            </div>
            <div class="log-body">
              <div v-if="isStructuredLog(log.content)" class="structured-log-content">
                <div v-if="hasDescriptionChange(log.content)" class="description-change-line">
                  <span>任务描述发生了修改，</span>
                  <el-button type="text" @click="openDescriptionDiffDialogFromStructured(log.content)" class="view-details-btn">
                    点击查看
                  </el-button>
                </div>
                <div v-if="hasOtherChanges(log.content)" class="other-changes">
                  <div v-for="(change, index) in getOtherChanges(log.content)" :key="index" class="log-content-line">
                    {{ change }}
                  </div>
                </div>
              </div>
              <div v-else class="legacy-log-content">
                <div v-for="(line, index) in log.content.split('\n')" :key="index" class="log-content-line">
                  {{ line }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </el-dialog>
  
  <!-- 描述变更详情对话框 -->
  <el-dialog
    v-model="descriptionDiffDialogVisible"
    title="描述变更详情"
    width="800px"
  >
    <div class="description-diff-container">
      <div class="description-diff-section">
        <div class="diff-section-title">修改前：</div>
        <div class="diff-section-content" v-html="currentDescriptionDiff.old"></div>
      </div>
      <div class="description-diff-section">
        <div class="diff-section-title">修改后：</div>
        <div class="diff-section-content" v-html="currentDescriptionDiff.new"></div>
      </div>
    </div>
  </el-dialog>
  
  <!-- 工时填报对话框 -->
  <el-dialog
    v-model="addHourDialogVisible"
    title="工时填报"
    width="600px"
  >
    <el-form :model="addHourForm" ref="addHourFormRef" label-width="100px">
      <el-form-item label="选择人员" prop="user_ids">
        <el-select 
          v-model="addHourForm.user_ids" 
          placeholder="请选择人员" 
          multiple 
          clearable 
          style="width: 100%"
        >
          <el-option 
            v-for="user in users" 
            :key="user.id" 
            :label="user.name" 
            :value="user.id"
          ></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="工时" prop="hours">
        <div class="hours-input-container">
          <el-input-number 
            v-model="addHourForm.hours" 
            :min="-999" 
            :max="999" 
            :step="0.5"
            :precision="1"
            placeholder="请输入工时"
            style="width: 100%"
          ></el-input-number>
          <el-tooltip content="如选择多个人员，则工时为每个人平均工时" placement="top">
            <el-icon class="info-icon"><QuestionFilled /></el-icon>
          </el-tooltip>
        </div>
      </el-form-item>
      <el-form-item label="备注" prop="remark">
        <el-input 
          v-model="addHourForm.remark" 
          type="textarea" 
          :rows="3" 
          placeholder="请输入备注"
        ></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="addHourDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddHour" :loading="addHourLoading">添加</el-button>
      </span>
    </template>
  </el-dialog>
  
  <!-- 工时记录列表对话框 -->
  <el-dialog
    v-model="hourListDialogVisible"
    title="工时记录"
    width="800px"
  >
    <div class="hour-list-container">
      <div v-if="taskHoursStats.hours_list.length === 0" class="no-hours">
        暂无工时记录
      </div>
      <div v-else class="hour-list">
        <div v-for="hour in taskHoursStats.hours_list" :key="hour.id" class="hour-item">
          <div class="hour-header">
            <div class="hour-user">
              <el-icon><User /></el-icon>
              <span>{{ hour.user.name }}</span>
            </div>
            <div class="hour-meta">
              <span class="hours-amount" :class="{ negative: hour.hours < 0 }">
                {{ hour.hours > 0 ? '+' : '' }}{{ hour.hours.toFixed(1) }} 小时
              </span>
              <span class="hour-creator">填报人：{{ hour.creator.name }}</span>
              <span class="hour-time">{{ formatDateTime(hour.created_at) }}</span>
            </div>
          </div>
          <div v-if="hour.remark" class="hour-remark">
            <span class="remark-label">备注：</span>{{ hour.remark }}
          </div>
        </div>
      </div>
    </div>
  </el-dialog>
  </div>
</template>
<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTaskStore, useUserStore, useReleaseStore } from '../store'
import dayjs from 'dayjs'
import api from '../api'
import { authApi, taskApi } from '../api'
import CustomRichTextEditor from '../components/CustomRichTextEditor.vue'
import { Document, QuestionFilled, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const taskStore = useTaskStore()
const userStore = useUserStore()
const releaseStore = useReleaseStore()

const taskId = computed(() => parseInt(route.params.id))
const isViewer = computed(() => userStore.isViewer)
const isAdmin = computed(() => userStore.isAdmin)
const task = ref({})
const comments = ref([])
const newComment = ref('')
const isAnonymousComment = ref(false)
const commentFileList = ref([]) // 评论附件列表
const editTaskDialogVisible = ref(false)
const taskLogDialogVisible = ref(false)
const descriptionDiffDialogVisible = ref(false)
const editTaskFormRef = ref(null)
const users = ref([])
const taskLogs = ref([])

// 工时相关
const addHourDialogVisible = ref(false)
const hourListDialogVisible = ref(false)
const addHourFormRef = ref(null)
const addHourLoading = ref(false)
const taskHoursStats = ref({
  total_hours: 0,
  hours_list: []
})
const addHourForm = reactive({
  user_ids: [],
  hours: null,
  remark: ''
})

// 关注相关
const isFollowing = ref(false)
const followers = ref([])

// 响应式数据：任务关联的发版记录状态
const taskReleaseStatus = ref('')
const isLoadingReleaseStatus = ref(false)

// 获取任务关联的发版记录状态
const fetchTaskReleaseStatus = async () => {
  if (!task.value.release_id) {
    taskReleaseStatus.value = ''
    return
  }
  
  isLoadingReleaseStatus.value = true
  try {
    const release = await releaseStore.fetchRelease(task.value.release_id)
    taskReleaseStatus.value = release.status
  } catch (error) {
    console.error('获取发版详情失败:', error)
    taskReleaseStatus.value = ''
  } finally {
    isLoadingReleaseStatus.value = false
  }
}

// 计算属性：检查任务是否关联到已发版的发版记录
const isTaskInReleasedRelease = computed(() => {
  return taskReleaseStatus.value === '已发版'
})

const currentDescriptionDiff = ref({
  old: '',
  new: ''
})

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
  tag_ids: [],
  priority: 'medium',
  due_date: null,
  actual_start_date: null,
  actual_completion_date: null,
  estimated_hours: null,
  actual_hours: null
})

// 标签列表
const tags = ref([])

// 当编辑对话框打开时，确保editTaskForm.description与task.description同步
watch(editTaskDialogVisible, (visible) => {
  if (visible) {
    editTaskForm.description = task.value.description || ''
  }
})

// 监听路由参数变化，当任务ID变化时重新加载数据
watch(() => route.params.id, async (newId) => {
  if (newId) {
    await fetchTaskDetail()
    await fetchComments()
    await fetchTaskLogs()
    await fetchFollowStatus()
    await fetchFollowers()
  }
})

// 监听任务关联的发版记录ID变化，重新获取发版记录状态
watch(() => task.value.release_id, async (newReleaseId) => {
  await fetchTaskReleaseStatus()
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

const getLogNodeClass = (actionType) => {
  switch (actionType) {
    case 'create':
      return 'node-create'
    case 'update':
      return 'node-update'
    case 'status_change':
      return 'node-status'
    default:
      return 'node-default'
  }
}

const goBack = () => {
  router.back()
}

const openEditTaskDialog = async () => {
  // 先获取用户列表、标签列表
  await fetchUsers()
  await fetchTags()
  // 获取任务关联的发版记录状态
  await fetchTaskReleaseStatus()
  // 填充编辑表单
  const taskData = {
    title: task.value.title,
    description: task.value.description,
    status_id: task.value.status_id,
    priority: task.value.priority,
    due_date: task.value.due_date,
    actual_start_date: task.value.actual_start_date,
    actual_completion_date: task.value.actual_completion_date,
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
  
  // 处理标签字段
  if (task.value.tags && task.value.tags.length > 0) {
    taskData.tag_ids = task.value.tags.map(tag => tag.id)
  } else {
    taskData.tag_ids = []
  }
  
  Object.assign(editTaskForm, taskData)
  editTaskDialogVisible.value = true
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
    // 获取任务关联的发版记录状态
    await fetchTaskReleaseStatus()
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

const fetchTaskLogs = async () => {
  try {
    const response = await api.get(`/tasks/${taskId.value}/logs`)
    taskLogs.value = response.data
  } catch (error) {
    console.error('获取任务日志失败:', error)
  }
}

const openTaskLogDialog = async () => {
  await fetchTaskLogs()
  taskLogDialogVisible.value = true
}

// 关注相关方法
const fetchFollowStatus = async () => {
  try {
    const response = await taskApi.getTaskFollowStatus(taskId.value)
    isFollowing.value = response.data.is_following
  } catch (error) {
    console.error('获取关注状态失败:', error)
    isFollowing.value = false
  }
}

const fetchFollowers = async () => {
  try {
    const response = await taskApi.getTaskFollowers(taskId.value)
    followers.value = response.data.followers
  } catch (error) {
    console.error('获取关注者列表失败:', error)
    followers.value = []
  }
}

const toggleFollow = async () => {
  try {
    if (isFollowing.value) {
      await taskApi.unfollowTask(taskId.value)
      ElMessage.success('取消关注成功')
    } else {
      await taskApi.followTask(taskId.value)
      ElMessage.success('关注成功')
    }
    // 重新获取关注状态和关注者列表
    await fetchFollowStatus()
    await fetchFollowers()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败，请重试')
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

// 工时相关方法
const fetchTaskHours = async () => {
  try {
    const response = await taskApi.getTaskHours(taskId.value)
    taskHoursStats.value = response.data
  } catch (error) {
    console.error('获取工时数据失败:', error)
  }
}

const openAddHourDialog = async () => {
  await fetchUsers()
  // 默认选择当前登录用户
  const currentUser = userStore.user
  if (currentUser) {
    addHourForm.user_ids = [currentUser.id]
  } else {
    addHourForm.user_ids = []
  }
  addHourForm.hours = null
  addHourForm.remark = ''
  addHourDialogVisible.value = true
}

const openHourListDialog = async () => {
  await fetchTaskHours()
  hourListDialogVisible.value = true
}

const handleAddHour = async () => {
  if (!addHourForm.user_ids || addHourForm.user_ids.length === 0) {
    ElMessage.warning('请至少选择一个人员')
    return
  }
  if (addHourForm.hours === null || addHourForm.hours === undefined) {
    ElMessage.warning('请输入工时')
    return
  }
  
  addHourLoading.value = true
  try {
    await taskApi.addTaskHours(taskId.value, {
      task_id: taskId.value,
      user_ids: addHourForm.user_ids,
      hours: addHourForm.hours,
      remark: addHourForm.remark
    })
    ElMessage.success('工时填报成功')
    addHourDialogVisible.value = false
    // 重新获取工时数据
    await fetchTaskHours()
  } catch (error) {
    console.error('工时填报失败:', error)
    ElMessage.error('工时填报失败，请重试')
  } finally {
    addHourLoading.value = false
  }
}

const addComment = async () => {
  if (!newComment.value.trim()) return
  
  try {
    // 提取评论附件的 ID
    const attachment_ids = commentFileList.value.map(attachment => attachment.id)
    
    const response = await api.post(`/tasks/${taskId.value}/comments`, {
      content: newComment.value,
      attachment_ids: attachment_ids,
      is_anonymous: isAnonymousComment.value
    })
    comments.value.unshift(response.data)
    newComment.value = ''
    isAnonymousComment.value = false
    commentFileList.value = [] // 清空评论附件列表
  } catch (error) {
    console.error('添加评论失败:', error)
  }
}

const togglePinComment = async (commentId) => {
  try {
    const response = await api.put(`/comments/${commentId}/pin`)
    const index = comments.value.findIndex(c => c.id === commentId)
    if (index !== -1) {
      comments.value[index] = response.data
    }
  } catch (error) {
    console.error('置顶评论失败:', error)
  }
}

const deleteCommentAttachment = (index) => {
  // 删除评论附件列表中的附件
  commentFileList.value.splice(index, 1)
}

const handleCommentFileChange = async (file, fileList) => {
  // 处理评论附件上传
  console.log('Comment file selected:', file)
  
  // 只有当文件状态为 ready 时才上传
  if (file.status === 'ready') {
    // 创建 FormData 对象
    const formData = new FormData()
    formData.append('file', file.raw)
    
    try {
      // 调用后端接口上传文件
      const response = await api.post(`/tasks/${taskId.value}/attachments`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      // 添加新附件到评论文件列表
      commentFileList.value.push(response.data)
      
      console.log('Comment file uploaded successfully:', response.data)
    } catch (error) {
      console.error('上传评论附件失败:', error)
    }
  }
}

onMounted(async () => {
  await fetchTaskDetail()
  await fetchTaskReleaseStatus() // 获取任务关联的发版记录状态
  await fetchComments()
  await fetchTaskLogs()
  await fetchFollowStatus()
  await fetchFollowers()
  await fetchTaskHours()
})

// 导入必要的库
import axios from 'axios'

// 下载附件函数
const downloadAttachment = async (attachmentId, filename) => {
  try {
    // 从本地存储获取认证令牌
    const token = localStorage.getItem('token')
    
    // 发起带认证的GET请求
    const response = await axios.get(
      `/api/attachments/${attachmentId}/download`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        responseType: 'blob' // 重要：设置响应类型为blob
      }
    )
    
    // 创建下载链接并触发下载
    // 使用响应中的MIME类型或默认类型
    const contentType = response.headers['content-type'] || 'application/octet-stream'
    const url = window.URL.createObjectURL(new Blob([response.data], { type: contentType }))
    const link = document.createElement('a')
    link.href = url
    
    // 直接使用传入的文件名
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('下载附件失败:', error)
    ElMessage.error('下载附件失败，请重试')
  }
}

// 检测是否为结构化日志
const isStructuredLog = (content) => {
  try {
    const parsed = JSON.parse(content)
    return parsed && typeof parsed === 'object' && ('description' in parsed || 'changes' in parsed)
  } catch (e) {
    return false
  }
}

// 检测是否有描述变更
const hasDescriptionChange = (content) => {
  try {
    const parsed = JSON.parse(content)
    return parsed && parsed.description && (parsed.description.old || parsed.description.new)
  } catch (e) {
    return false
  }
}

// 检测是否有其他变更
const hasOtherChanges = (content) => {
  try {
    const parsed = JSON.parse(content)
    return parsed && parsed.changes && parsed.changes.length > 0
  } catch (e) {
    return false
  }
}

// 获取其他变更列表
const getOtherChanges = (content) => {
  try {
    const parsed = JSON.parse(content)
    return parsed.changes || []
  } catch (e) {
    return []
  }
}

// 从结构化日志中提取修改前的描述内容
const getOldDescription = (content) => {
  try {
    const parsed = JSON.parse(content)
    return parsed.description?.old || ''
  } catch (e) {
    return ''
  }
}

// 从结构化日志中提取修改后的描述内容
const getNewDescription = (content) => {
  try {
    const parsed = JSON.parse(content)
    return parsed.description?.new || ''
  } catch (e) {
    return ''
  }
}

// 从结构化日志打开描述变更详情对话框
const openDescriptionDiffDialogFromStructured = (content) => {
  currentDescriptionDiff.value = {
    old: getOldDescription(content),
    new: getNewDescription(content)
  }
  descriptionDiffDialogVisible.value = true
}

// 打开描述变更详情对话框（兼容旧格式）
const openDescriptionDiffDialog = (content) => {
  currentDescriptionDiff.value = {
    old: getOldDescription(content),
    new: getNewDescription(content)
  }
  descriptionDiffDialogVisible.value = true
}


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

.description-change-line {
  display: flex;
  align-items: center;
}

.view-details-btn {
  color: #409eff;
  font-size: 14px;
  padding: 0;
  margin-left: 5px;
}

.log-content-line {
  margin-bottom: 8px;
  line-height: 1.4;
}

.log-content-line:last-child {
  margin-bottom: 0;
}

.description-diff-container {
  margin-top: 20px;
}

.description-diff-section {
  margin-bottom: 20px;
}

.diff-section-title {
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
}

.diff-section-content {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  min-height: 100px;
  background-color: #f9f9f9;
  white-space: pre-wrap;
  word-break: break-word;
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
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



.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.task-tag {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.assignee-single {
  font-weight: 500;
}


.no-followers {
  color: #999;
  font-style: italic;
}



.assignees-header {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.assignees-count {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.assignee-tag {
  margin-left: 5px;
  white-space: nowrap;
}



.followers-header {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.followers-count {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.follower-tag {
  
  margin-left: 5px;
  white-space: nowrap;
}

.follow-section {
  margin-top: 5px;
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

.comment-attachments-list {
  margin: 10px 0;
  padding: 10px;
  border: 1px solid #f0f0f0;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.comment-attachment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;
  font-size: 12px;
}

.comment-attachment-item:last-child {
  margin-bottom: 0;
}

.comment-options {
  margin: 10px 0;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.comment-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.comment-header-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.pinned-badge {
  margin-left: 8px;
}

.pin-button {
  font-size: 12px;
}

.comment-time {
  font-size: 12px;
  color: #909399;
}

.comment-attachment-item .el-icon {
  color: #909399;
}

.attachment-filename {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attachment-delete {
  color: #f56c6c;
}

.attachment-delete:hover {
  color: #f56c6c;
  background-color: rgba(245, 108, 108, 0.1);
}

.attachment-link {
  color: #409eff;
  text-decoration: none;
}

.attachment-link:hover {
  text-decoration: underline;
}

.comment-upload {
  margin: 10px 0;
}

.overdue {
  color: #dc2626;
  font-weight: 600;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
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

/* 工时相关样式 */
.total-hours-button {
  padding: 0;
  height: auto;
  font-size: inherit;
  color: #409eff;
  text-decoration: underline;
}

.total-hours-button:hover {
  color: #66b1ff;
}

.hours-input-container {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.hours-input-container .el-input-number {
  flex: 1;
}

.info-icon {
  color: #909399;
  cursor: pointer;
  font-size: 16px;
}

.info-icon:hover {
  color: #409eff;
}

.hour-list-container {
  max-height: 600px;
  overflow-y: auto;
}

.no-hours {
  text-align: center;
  color: #909399;
  padding: 40px 0;
}

.hour-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.hour-item {
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
  border: 1px solid #e4e7ed;
}

.hour-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.hour-user {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  color: #303133;
}

.hour-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 12px;
  color: #909399;
}

.hours-amount {
  font-weight: 600;
  font-size: 14px;
  color: #67c23a;
}

.hours-amount.negative {
  color: #f56c6c;
}

.hour-remark {
  font-size: 13px;
  color: #606266;
  padding-top: 8px;
  border-top: 1px solid #e4e7ed;
}

.remark-label {
  font-weight: 500;
  color: #909399;
}
</style>
<style>
/* 任务描述部分的编辑器样式（只读） */
.task-description :deep(.w-e-container) {
  border: none !important;
  background: none !important;
}

.task-description :deep(.w-e-toolbar) {
  display: none !important;
}
/* 任务日志样式 */
.task-logs-container {
  max-height: 600px;
  overflow-y: auto;
}

.no-logs {
  text-align: center;
  color: #909399;
  padding: 40px 0;
}

.task-logs-timeline {
  position: relative;
  padding-left: 30px;
}

.task-log-item {
  position: relative;
  margin-bottom: 30px;
}

.timeline-node {
  position: absolute;
  left: -30px;
  top: 0;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background-color: #dcdfe6;
  transform: translateX(-50%);
  z-index: 1;
}

.timeline-line {
  position: absolute;
  left: -30px;
  top: 16px;
  width: 2px;
  height: calc(100% + 30px);
  background-color: #dcdfe6;
  transform: translateX(-50%);
}

/* 不同类型日志的节点颜色 */
.node-create {
  background-color: #409eff;
}

.node-update {
  background-color: #67c23a;
}

.node-status {
  background-color: #e6a23c;
}

.node-default {
  background-color: #909399;
}

.log-content {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.log-title {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.log-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 12px;
  color: #909399;
}

.log-body {
  margin-top: 10px;
}

.log-content-text {
  font-size: 14px;
  line-height: 1.5;
  color: #606266;
  white-space: pre-wrap;
}

/* 描述字段差异显示样式 */
.description-diff-container {
  margin-top: 8px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.description-diff-section {
  padding: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.description-diff-section:last-child {
  border-bottom: none;
}

.diff-section-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #606266;
}

.diff-section-content {
  line-height: 1.5;
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  min-height: 80px;
}

/* 调整描述内容的样式，确保富文本显示正确 */
.diff-section-content p {
  margin: 0 0 10px 0;
}

.diff-section-content ul,
.diff-section-content ol {
  margin: 0 0 10px 20px;
}

.diff-section-content img {
  max-width: 100%;
  height: auto;
}

.diff-section-content table {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 10px;
}

.diff-section-content table th,
.diff-section-content table td {
  border: 1px solid #ddd;
  padding: 8px;
}

.diff-section-content table th {
  background-color: #f2f2f2;
}

/* 修复wangEditor全屏模式下的层级问题 */
.w-e-full-screen-container {
  z-index: 9999999 !important;
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  background-color: white !important;
}

/*

.w-e-full-screen-container .w-e-toolbar {
  z-index: 10000 !important;
  position: relative !important;
}*/
/*
.w-e-full-screen-container .w-e-text-container {
  z-index: 9999 !important;
  position: relative !important;
}*/


/* 响应式调整 */
@media (max-width: 768px) {
  .task-logs-timeline {
    padding-left: 25px;
  }
  
  .timeline-node {
    left: -25px;
    width: 12px;
    height: 12px;
  }
  
  .timeline-line {
    left: -25px;
    top: 12px;
  }
  
  .log-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .log-meta {
    gap: 10px;
  }
}
</style>
