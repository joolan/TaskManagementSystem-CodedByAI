<template>
  <div class="defect-detail-container">
    <div class="defect-detail-header">
      <el-button @click="goBack">返回</el-button>
      <h1>{{ defect.title }}</h1>
      <el-button v-permission="'defect:update'" type="primary" @click="openEditDialog">编辑</el-button>
      <el-button v-permission="'defect:delete'" type="danger" @click="handleDelete">删除</el-button>
    </div>
    
    <div class="defect-detail-content">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>缺陷信息</span>
            <el-tag :type="getStatusType(defect.status)">
              {{ defect.status }}
            </el-tag>
          </div>
        </template>
        
        <div class="defect-info-grid">
          <div class="info-item">
            <span class="info-label">缺陷ID：</span>
            <span>{{ defect.id }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">创建人：</span>
            <span>{{ defect.creator_name || '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">负责人：</span>
            <span>{{ defect.assignee_name || '未分配' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">缺陷来源版本：</span>
            <span v-if="defect.release_title">{{ defect.release_title }}</span>
            <span v-else>无</span>
          </div>
          <div class="info-item">
            <span class="info-label">创建时间：</span>
            <span>{{ formatDate(defect.created_at) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">更新时间：</span>
            <span>{{ formatDate(defect.updated_at) }}</span>
          </div>
        </div>
      </el-card>
      
      <el-card>
        <template #header>
          <span>缺陷详情</span>
        </template>
        <div class="defect-description" v-html="defect.description"></div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const router = useRouter()
const route = useRoute()

const defect = ref({})
const loading = ref(false)

const fetchDefect = async (id) => {
  loading.value = true
  try {
    const response = await api.get(`/defects/${id}`)
    defect.value = response.data
  } catch (error) {
    console.error('获取缺陷详情失败:', error)
    ElMessage.error('获取缺陷详情失败')
  } finally {
    loading.value = false
  }
}

const openEditDialog = () => {
  router.push(`/defect/${defect.value.id}/edit`)
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm('确定要删除这个缺陷吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.delete(`/defects/${defect.value.id}`)
    ElMessage.success('删除成功')
    goBack()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除缺陷失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const goBack = () => {
  router.push('/defects')
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
  fetchDefect(route.params.id)
})
</script>

<style scoped>
.defect-detail-container {
  padding: 20px;
}

.defect-detail-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 20px;
}

.defect-detail-header h1 {
  margin: 0;
  flex: 1;
}

.defect-detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.defect-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-label {
  font-weight: bold;
  margin-right: 10px;
  min-width: 120px;
}

.defect-description {
  min-height: 200px;
  line-height: 1.6;
}

.defect-description :deep(p) {
  margin-bottom: 10px;
}

.defect-description :deep(img) {
  max-width: 100%;
  height: auto;
}
</style>
