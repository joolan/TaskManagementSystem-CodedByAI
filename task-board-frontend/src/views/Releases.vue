<template>
  <div class="releases-container">
    
    <div class="releases-filters">
      <el-form :inline="true" :model="filterForm" class="demo-form-inline">
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" style="width: 200px;" multiple>
            <el-option label="计划中" value="计划中"></el-option>
            <el-option label="已发版" value="已发版"></el-option>
            <el-option label="延期中" value="延期中"></el-option>
            <el-option label="已作废" value="已作废"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="我的关注">
          <el-select v-model="filterForm.follow_status" placeholder="全部" style="width: 150px;">
            <el-option label="全部" value=""></el-option>
            <el-option label="我关注的" value="followed"></el-option>
            <el-option label="我未关注的" value="unfollowed"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input v-model="filterForm.search" placeholder="发版主题" clearable></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchReleases">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
          <el-button v-permission="'release:export'" type="success" @click="exportReleases" :loading="exportLoading">导出</el-button>
        </el-form-item>
        <el-form-item>
          <el-button v-permission="'release:create'" type="primary" @click="goToCreateRelease">创建发版</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <div class="releases-table">
      <el-table :data="releaseStore.releases" style="width: 100%">
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column prop="id" label="发版ID" width="80"></el-table-column>
        <el-table-column prop="title" label="发版主题" min-width="200">
          <template #default="scope">
            <router-link :to="`/release/${scope.row.id}`" class="release-title-link">
              {{ scope.row.title }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="发版状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="planned_release_date" label="预计发版时间" width="150">
          <template #default="scope">
            <span v-if="scope.row.planned_release_date">
              {{ formatDate(scope.row.planned_release_date) }}
            </span>
            <span v-else>未设置</span>
          </template>
        </el-table-column>
        <el-table-column prop="actual_release_date" label="实际发版时间" width="150">
          <template #default="scope">
            <span v-if="scope.row.actual_release_date">
              {{ formatDate(scope.row.actual_release_date) }}
            </span>
            <span v-else>未设置</span>
          </template>
        </el-table-column>
        <el-table-column label="发版标签" width="180">
          <template #default="scope">
            <div class="release-tags">
              <el-tag 
                v-for="tag in scope.row.tags" 
                :key="tag.id" 
                :style="{ backgroundColor: tag.color, borderColor: tag.color, color: getTextColor(tag.color) }"
                size="small"
              >
                {{ tag.name }}
              </el-tag>
              <span v-if="!scope.row.tags || scope.row.tags.length === 0">无</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="关联任务数" width="100">
          <template #default="scope">
            {{ scope.row.tasks ? scope.row.tasks.length : 0 }}
          </template>
        </el-table-column>
        <el-table-column label="版本缺陷数" width="100">
          <template #default="scope">
            <el-button 
              type="text" 
              @click="goToDefectsByRelease(scope.row.id)"
              :disabled="!scope.row.defect_count || scope.row.defect_count === 0"
            >
              {{ scope.row.defect_count || 0 }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="创建人" width="120">
          <template #default="scope">
            {{ scope.row.creator ? scope.row.creator.name : '未知' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-tooltip content="创建版本缺陷" placement="top">
              <el-button v-permission="'defect:create'" size="small" type="warning" :icon="Warning" @click="goToCreateDefect(scope.row.id)"></el-button>
            </el-tooltip>
            <el-button v-permission="'release:update'" size="small" @click="goToEditRelease(scope.row.id)">编辑</el-button>
            <el-button v-permission="'release:delete'" size="small" type="danger" @click="handleDeleteRelease(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          :current-page="releaseStore.currentPage"
          :page-size="releaseStore.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="releaseStore.totalReleases"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useReleaseStore } from '../store'
import dayjs from 'dayjs'
import api from '../api/index'
import { ElMessage } from 'element-plus'
import { Warning } from '@element-plus/icons-vue'
import { exportFile, getFileNameFromResponse } from '../utils/exportFile'

const router = useRouter()
const route = useRoute()
const releaseStore = useReleaseStore()

const filterForm = ref({
  status: [],
  search: '',
  follow_status: ''
})

const exportLoading = ref(false)

const formatDate = (dateString) => {
  return dateString ? dayjs(dateString).format('YYYY-MM-DD HH:mm') : ''
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
    // 默认为黑色
    return '#ffffff'
  }
  
  // 计算亮度 (WCAG 公式)
  const brightness = (r * 299 + g * 587 + b * 114) / 1000
  
  // 亮度大于 128 时使用深灰色，否则使用白色
  return brightness > 128 ? '#F2F2F2' : '#ffffff'
}

const goToCreateRelease = () => {
  router.push('/release/create')
}

const goToEditRelease = (releaseId) => {
  router.push(`/release/edit/${releaseId}`)
}

const goToCreateDefect = (releaseId) => {
  router.push(`/defect/create?release_id=${releaseId}`)
}

const goToDefectsByRelease = (releaseId) => {
  router.push(`/defects?release_id=${releaseId}`)
}

const fetchReleases = async () => {
  // 过滤掉空值参数
  const params = {}
  if (filterForm.value.status && filterForm.value.status.length > 0) {
    params.status = filterForm.value.status.join(',')
  }
  if (filterForm.value.search) params.search = filterForm.value.search
  if (filterForm.value.follow_status) params.follow_status = filterForm.value.follow_status
  
  await releaseStore.fetchReleases(params, releaseStore.currentPage, releaseStore.pageSize)
}

const resetFilters = () => {
  filterForm.value = {
    status: [],
    search: '',
    follow_status: ''
  }
  fetchReleases()
}

const handleDeleteRelease = async (releaseId) => {
  try {
    await releaseStore.deleteRelease(releaseId)
  } catch (error) {
    console.error('删除发版失败:', error)
  }
}

const handleSizeChange = (size) => {
  releaseStore.pageSize = size
  releaseStore.currentPage = 1 // 重置到第一页
  fetchReleases()
}

const handleCurrentChange = (current) => {
  releaseStore.currentPage = current
  fetchReleases()
}

const exportReleases = async () => {
  if (exportLoading.value) return // 防止重复点击
  
  exportLoading.value = true
  try {
    // 构建查询参数
    const params = {}
    if (filterForm.value.status) params.status = filterForm.value.status
    if (filterForm.value.search) params.search = filterForm.value.search
    
    // 使用axios发送请求，获取二进制数据
    const response = await api.get('/releases/export', {
      params,
      responseType: 'blob' // 重要：设置响应类型为blob
    })
    
    // 获取文件名
    const fileName = getFileNameFromResponse(response, 'releases_export.xlsx')
    
    // 导出文件（让用户选择保存位置）
    const success = await exportFile(response.data, fileName)
    
    if (success) {
      ElMessage.success('导出成功')
    }
  } catch (error) {
    console.error('导出发版失败:', error)
    ElMessage.error('导出发版失败，请重试')
  } finally {
    exportLoading.value = false
  }
}

// 处理路由查询参数
const handleRouteQuery = async () => {
  const { filter, status } = route.query
  
  // 重置过滤条件
  filterForm.value = {
    status: [],
    search: '',
    follow_status: ''
  }
  
  // 根据查询参数设置过滤条件
  if (filter === 'my-followed') {
    // 我关注的发版 - 设置我的关注为我关注的
    filterForm.value.follow_status = 'followed'
  }
  
  if (status === 'unreleased') {
    // 未发版 - 设置状态过滤为计划中、延期中
    filterForm.value.status = ['计划中', '延期中']
  }
  
  // 获取发版
  await fetchReleases()
}

onMounted(async () => {
  await handleRouteQuery()
})
</script>

<style scoped>
.releases-container {
  padding: 10px;
  background-color: #ffffff;
}

.releases-filters {
  margin-bottom: 15px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.releases-table {
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

.release-title-link {
  color: #1890ff;
  text-decoration: none;
}

.release-title-link:hover {
  text-decoration: underline;
}

.release-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
</style>
