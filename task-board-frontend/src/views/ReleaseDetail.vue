<template>
  <div class="release-detail">
    <div class="release-detail-header">
    <el-button  @click="goBack">返回</el-button>
    <div v-if="isCreating || isEditing">
      <h3>{{ isCreating ? '创建发版记录' : '编辑发版记录' }}</h3>
    </div>
    <div v-else-if="releaseId">
      <h3>发版详情</h3>
    </div>
    </div>
    <div v-if="releaseId && !isCreating && !isEditing">
      <el-card v-if="release" class="release-info-card">
        <template #header>
          <div class="card-header">
            <span>{{ release.title }}</span>
            <div class="header-actions">
              <el-tag :type="getStatusType(release.status)">{{ release.status }}</el-tag>
              <el-button 
                v-if="isFollowing" 
                type="warning" 
                size="small" 
                @click="handleUnfollow"
                :loading="followLoading"
              >
                取消关注
              </el-button>
              <el-button 
                v-else 
                type="primary" 
                size="small" 
                @click="handleFollow"
                :loading="followLoading"
              >
                关注
              </el-button>
            </div>
          </div>
        </template>
        
        <div class="release-info">
          <div class="info-item">
            <span class="info-label">创建人：</span>
            <span>{{ release.creator ? release.creator.name : '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">创建时间：</span>
            <span>{{ formatDate(release.created_at) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">预计发版时间：</span>
            <span>{{ release.planned_release_date ? formatDate(release.planned_release_date) : '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">实际发版时间：</span>
            <span>{{ release.actual_release_date ? formatDate(release.actual_release_date) : '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">发版标签：</span>
            <div class="release-tags">
              <el-tag 
                v-for="tag in release.tags" 
                :key="tag.id" 
                :style="{ backgroundColor: tag.color, borderColor: tag.color, color: getTextColor(tag.color) }"
                size="small"
              >
                {{ tag.name }}
              </el-tag>
              <span v-if="!release.tags || release.tags.length === 0">无</span>
            </div>
          </div>
          <div class="info-item">
            <span class="info-label">关注人：</span>
            <div class="followers-list">
              <el-tag 
                v-for="follower in followers" 
                :key="follower.id" 
                size="small"
                type="info"
              >
                {{ follower.user_name }}
              </el-tag>
              <span v-if="!followers || followers.length === 0">暂无关注人</span>
            </div>
          </div>
        </div>
        
        <div class="info-section">
          <h4>发版详情</h4>
          <div class="release-description" v-html="release.description || '无'">
          </div>
        </div>
        
        <div class="info-section">
          <h4>关联任务</h4>
          <el-table :data="release.tasks" style="width: 100%">
            <el-table-column prop="id" label="任务ID" width="80"></el-table-column>
            <el-table-column prop="title" label="任务标题" min-width="150" show-overflow-tooltip></el-table-column>
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
          <div v-if="!release.tasks || release.tasks.length === 0" class="no-data">
            无关联任务
          </div>
        </div>
        
        <div class="card-footer">
          <el-button v-permission="'release:update'" type="primary" @click="goToEdit">编辑</el-button>
        </div>
      </el-card>
    </div>
    
    <div v-if="isCreating || isEditing">
      
      <ReleaseForm 
        :release-id="releaseId" 
        @save="handleSave" 
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useReleaseStore } from '../store'
import { releaseApi } from '../api'
import { ElMessage } from 'element-plus'
import ReleaseForm from '../components/ReleaseForm.vue'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const releaseStore = useReleaseStore()

const releaseId = computed(() => {
  return route.params.id ? parseInt(route.params.id) : null
})

const isCreating = computed(() => {
  return route.path.includes('/create')
})

const isEditing = computed(() => {
  return route.path.includes('/edit')
})

const release = ref(null)
const isFollowing = ref(false)
const followLoading = ref(false)
const followers = ref([])

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusType = (status) => {
  const statusMap = {
    '计划中': 'info',
    '已发版': 'success',
    '延期中': 'warning',
    '已作废': 'danger'
  }
  return statusMap[status] || 'info'
}

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

const getTextColor = (backgroundColor) => {
  // 移除 # 前缀
  const color = backgroundColor.replace('#', '')
  
  // 转换为 RGB
  let r, g, b
  if (color.length === 6) {
    r = parseInt(color.substring(0, 2), 16)
    g = parseInt(color.substring(2, 4), 16)
    b = parseInt(color.substring(4, 6), 16)
  } else if (color.length === 3) {
    r = parseInt(color[0] + color[0], 16)
    g = parseInt(color[1] + color[1], 16)
    b = parseInt(color[2] + color[2], 16)
  } else {
    // 默认为深灰色
    return '#333333'
  }
  
  // 计算亮度 (WCAG 公式)
  const brightness = (r * 299 + g * 587 + b * 114) / 1000
  
  // 亮度大于 128 时使用深灰色，否则使用白色
  return brightness > 128 ? '#F2F2F2' : '#ffffff'
}

const fetchRelease = async () => {
  if (releaseId.value) {
    try {
      const data = await releaseStore.fetchRelease(releaseId.value)
      release.value = data
    } catch (error) {
      console.error('获取发版记录失败:', error)
    }
  }
}

const fetchFollowStatus = async () => {
  if (releaseId.value) {
    try {
      const response = await releaseApi.getFollowStatus(releaseId.value)
      isFollowing.value = response.data.is_following
    } catch (error) {
      console.error('获取关注状态失败:', error)
    }
  }
}

const fetchFollowers = async () => {
  if (releaseId.value) {
    try {
      const response = await releaseApi.getReleaseFollowers(releaseId.value)
      followers.value = response.data
    } catch (error) {
      console.error('获取关注者失败:', error)
    }
  }
}

const handleFollow = async () => {
  if (!releaseId.value) return
  
  followLoading.value = true
  try {
    await releaseApi.followRelease(releaseId.value)
    isFollowing.value = true
    ElMessage.success('关注成功')
  } catch (error) {
    console.error('关注失败:', error)
    ElMessage.error('关注失败')
  } finally {
    followLoading.value = false
  }
}

const handleUnfollow = async () => {
  if (!releaseId.value) return
  
  followLoading.value = true
  try {
    await releaseApi.unfollowRelease(releaseId.value)
    isFollowing.value = false
    ElMessage.success('取消关注成功')
  } catch (error) {
    console.error('取消关注失败:', error)
    ElMessage.error('取消关注失败')
  } finally {
    followLoading.value = false
  }
}

const handleSave = () => {
  router.push('/releases')
}

const goToEdit = () => {
  router.push(`/release/edit/${releaseId.value}`)
}

const goBack = () => {
  router.push('/releases')
}

onMounted(() => {
  if (releaseId.value && !isCreating.value && !isEditing.value) {
    fetchRelease()
    fetchFollowStatus()
    fetchFollowers()
  }
})

// 监听发版ID变化，重新获取数据
watch(() => releaseId.value, (newId) => {
  if (newId && !isCreating.value && !isEditing.value) {
    fetchRelease()
    fetchFollowStatus()
    fetchFollowers()
  }
})
</script>

<style scoped>
.release-detail {
  padding: 20px;

}

.release-detail-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 15px;
}

.release-info-card {
  margin-top: 20px;
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

.release-info {
  margin-bottom: 20px;
}

.info-item {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}

.info-label {
  font-weight: bold;
  width: 120px;
}

.release-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.followers-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.info-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.info-section h4 {
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: bold;
}

.release-description {
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
  white-space: pre-wrap;
}

.no-data {
  padding: 20px;
  text-align: center;
  color: #909399;
  background-color: #f9f9f9;
  border-radius: 4px;
  margin-top: 10px;
}

.card-footer {
  margin-top: 30px;
  text-align: right;
  border-top: 1px solid #f0f0f0;
  padding-top: 20px;
}
</style>
