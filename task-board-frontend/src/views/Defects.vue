<template>
  <div class="defects-container">
    
    <div class="defects-filters">
      <el-form :inline="true" :model="filterForm" class="demo-form-inline">
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" style="width: 150px;" clearable multiple>
            <el-option label="草稿" value="草稿"></el-option>
            <el-option label="未解决" value="未解决"></el-option>
            <el-option label="已解决" value="已解决"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="缺陷来源版本">
          <el-select v-model="filterForm.release_id" placeholder="全部" style="width: 200px;" clearable filterable>
            <el-option 
              v-for="release in releases" 
              :key="release.id" 
              :label="release.title" 
              :value="release.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="负责人">
          <el-select v-model="filterForm.assignee_id" placeholder="全部" style="width: 150px;" clearable filterable>
            <el-option 
              v-for="user in users" 
              :key="user.id" 
              :label="user.name" 
              :value="user.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="创建人">
          <el-select v-model="filterForm.created_by" placeholder="全部" style="width: 150px;" clearable filterable>
            <el-option 
              v-for="user in users" 
              :key="user.id" 
              :label="user.name" 
              :value="user.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchDefects">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
          <el-button v-permission="'defect:export'" type="success" @click="exportDefects" :loading="exportLoading">导出</el-button>
        </el-form-item>
        <el-form-item>
          <el-button v-permission="'defect:create'" type="primary" @click="goToCreateDefect">新增缺陷</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <div class="defects-table">
      <el-table :data="defects" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="缺陷ID" width="80"></el-table-column>
        <el-table-column prop="title" label="缺陷标题" min-width="200">
          <template #default="scope">
            <router-link :to="`/defect/${scope.row.id}`" class="defect-title-link">
              {{ scope.row.title }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="release_title" label="缺陷来源版本" width="150">
          <template #default="scope">
            <span v-if="scope.row.release_title">{{ scope.row.release_title }}</span>
            <span v-else>无</span>
          </template>
        </el-table-column>
        <el-table-column prop="assignee_name" label="负责人" width="120">
          <template #default="scope">
            <span v-if="scope.row.assignee_name">{{ scope.row.assignee_name }}</span>
            <span v-else>未分配</span>
          </template>
        </el-table-column>
        <el-table-column prop="creator_name" label="创建人" width="120">
          <template #default="scope">
            {{ scope.row.creator_name || '未知' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="150">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button v-permission="'defect:update'" size="small" @click="goToEditDefect(scope.row.id)">编辑</el-button>
            <el-button v-permission="'defect:delete'" size="small" type="danger" @click="handleDeleteDefect(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        ></el-pagination>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'
import { exportFile, getFileNameFromResponse } from '../utils/exportFile'

const router = useRouter()
const route = useRoute()

const defects = ref([])
const releases = ref([])
const users = ref([])
const loading = ref(false)
const exportLoading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filterForm = reactive({
  status: [],
  release_id: null,
  assignee_id: null,
  created_by: null
})

const fetchDefects = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (filterForm.status && filterForm.status.length > 0) {
      params.status = filterForm.status.join(',')
    }
    if (filterForm.release_id) params.release_id = filterForm.release_id
    if (filterForm.assignee_id) params.assignee_id = filterForm.assignee_id
    if (filterForm.created_by) params.created_by = filterForm.created_by
    
    const response = await api.get('/defects', { params })
    defects.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    console.error('获取缺陷列表失败:', error)
    ElMessage.error('获取缺陷列表失败')
  } finally {
    loading.value = false
  }
}

const fetchReleases = async () => {
  try {
    const response = await api.get('/releases', { params: { page: 1, page_size: 1000 } })
    releases.value = response.data.items
  } catch (error) {
    console.error('获取发版列表失败:', error)
  }
}

// 获取用户基本信息列表（用于下拉选择，只包含id和name）
const fetchUsers = async () => {
  try {
    // 注意：这里使用 /auth/users-basic 接口，只返回用户基本信息（id, name）
    // 不要改成 /users 接口，该接口不存在
    const response = await api.get('/auth/users-basic')
    users.value = response.data
  } catch (error) {
    console.error('获取用户列表失败:', error)
  }
}

const resetFilters = () => {
  filterForm.status = ''
  filterForm.release_id = null
  filterForm.assignee_id = null
  filterForm.created_by = null
  currentPage.value = 1
  fetchDefects()
}

const goToCreateDefect = () => {
  router.push('/defect/create')
}

const goToEditDefect = (id) => {
  router.push(`/defect/edit/${id}`)
}

const handleDeleteDefect = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个缺陷吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.delete(`/defects/${id}`)
    ElMessage.success('删除成功')
    fetchDefects()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除缺陷失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleSizeChange = (size) => {
  pageSize.value = size
  fetchDefects()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchDefects()
}

const exportDefects = async () => {
  if (exportLoading.value) return // 防止重复点击

  exportLoading.value = true
  try {
    // 构建查询参数
    const params = {}
    if (filterForm.status && filterForm.status.length > 0) {
      params.status = filterForm.status.join(',')
    }
    if (filterForm.release_id) params.release_id = filterForm.release_id
    if (filterForm.assignee_id) params.assignee_id = filterForm.assignee_id
    if (filterForm.created_by) params.created_by = filterForm.created_by

    // 使用axios发送请求，获取二进制数据
    const response = await api.get('/defects/export', {
      params,
      responseType: 'blob' // 重要：设置响应类型为blob
    })

    // 获取文件名
    const fileName = getFileNameFromResponse(response, 'defects_export.xlsx')

    // 导出文件（让用户选择保存位置）
    const success = await exportFile(response.data, fileName)

    if (success) {
      ElMessage.success('导出成功')
    }
  } catch (error) {
    console.error('导出缺陷失败:', error)
    ElMessage.error('导出缺陷失败，请重试')
  } finally {
    exportLoading.value = false
  }
}

const getStatusType = (status) => {
  const statusMap = {
    '草稿': 'info',
    '未解决': 'danger',
    '已解决': 'success'
  }
  return statusMap[status] || 'info'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  // 检查是否有预置的查询条件（从发版列表跳转过来）
  if (route.query.release_id) {
    filterForm.release_id = parseInt(route.query.release_id)
  }
  
  // 检查是否有从Dashboard跳转过来的status参数
  if (route.query.status) {
    if (Array.isArray(route.query.status)) {
      filterForm.status = route.query.status
    } else {
      // 处理逗号分隔的多个状态
      if (route.query.status.includes(',')) {
        filterForm.status = route.query.status.split(',')
      } else {
        filterForm.status = [route.query.status]
      }
    }
  }
  
  // 检查是否有从Dashboard跳转过来的assignee_id参数
  if (route.query.assignee_id) {
    filterForm.assignee_id = parseInt(route.query.assignee_id)
  }
  
  fetchDefects()
  fetchReleases()
  fetchUsers()
})
</script>

<style scoped>
.defects-container {
  padding: 20px;
}

.defects-filters {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.defects-table {
  background-color: #fff;
  padding: 20px;
  border-radius: 4px;
}

.defect-title-link {
  color: #409EFF;
  text-decoration: none;
}

.defect-title-link:hover {
  text-decoration: underline;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
