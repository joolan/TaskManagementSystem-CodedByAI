<template>
  <div class="defect-form-container">
    <div class="form-header">
      <el-button @click="goBack">返回</el-button>
      <h1>{{ isEdit ? '编辑缺陷' : '新增缺陷' }}</h1>
    </div>
    
    <el-form :model="defectForm" :rules="rules" ref="defectFormRef" label-width="120px" v-loading="loading">
      <el-form-item label="缺陷标题" prop="title">
        <el-input v-model="defectForm.title" placeholder="请输入缺陷标题"></el-input>
      </el-form-item>
      
      <el-form-item label="缺陷状态" prop="status">
        <el-select v-model="defectForm.status" placeholder="请选择缺陷状态">
          <el-option label="草稿" value="草稿"></el-option>
          <el-option label="未解决" value="未解决"></el-option>
          <el-option label="已解决" value="已解决"></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="缺陷来源版本" prop="release_id">
        <el-select 
          v-model="defectForm.release_id" 
          placeholder="请选择缺陷来源版本" 
          clearable
          filterable
          :disabled="!!preSelectedReleaseId"
        >
          <el-option 
            v-for="release in releases" 
            :key="release.id" 
            :label="release.title" 
            :value="release.id"
          ></el-option>
        </el-select>
        <div v-if="preSelectedReleaseId" class="hint-text">
          该缺陷已关联到发版：{{ preSelectedReleaseTitle }}
        </div>
      </el-form-item>
      
      <el-form-item label="负责人" prop="assignee_id">
        <el-select v-model="defectForm.assignee_id" placeholder="请选择负责人" clearable filterable>
          <el-option 
            v-for="user in users" 
            :key="user.id" 
            :label="user.name" 
            :value="user.id"
          ></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="缺陷详情" prop="description">
        <CustomRichTextEditor
          v-model="defectForm.description"
          :height="400"
          placeholder="请输入缺陷详情"
        />
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
        <el-button @click="goBack">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'
import CustomRichTextEditor from '../components/CustomRichTextEditor.vue'

const router = useRouter()
const route = useRoute()

const isEdit = ref(false)
const loading = ref(false)
const defectFormRef = ref(null)
const releases = ref([])
const users = ref([])
const preSelectedReleaseId = ref(null)
const preSelectedReleaseTitle = ref('')

const defectForm = reactive({
  title: '',
  description: '',
  status: '草稿',
  release_id: null,
  assignee_id: null
})

const rules = {
  title: [
    { required: true, message: '请输入缺陷标题', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择缺陷状态', trigger: 'change' }
  ]
}

const fetchDefect = async (id) => {
  loading.value = true
  try {
    const response = await api.get(`/defects/${id}`)
    defectForm.title = response.data.title
    defectForm.description = response.data.description
    defectForm.status = response.data.status
    defectForm.release_id = response.data.release_id
    defectForm.assignee_id = response.data.assignee_id
  } catch (error) {
    console.error('获取缺陷详情失败:', error)
    ElMessage.error('获取缺陷详情失败')
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

const fetchUsers = async () => {
  try {
    const response = await api.get('/auth/users-basic')
    users.value = response.data
  } catch (error) {
    console.error('获取用户列表失败:', error)
  }
}

const handleSubmit = async () => {
  if (!defectFormRef.value) return
  
  try {
    await defectFormRef.value.validate()
    
    loading.value = true
    const data = {
      title: defectForm.title,
      description: defectForm.description,
      status: defectForm.status,
      release_id: defectForm.release_id,
      assignee_id: defectForm.assignee_id
    }
    
    if (isEdit.value) {
      await api.put(`/defects/${route.params.id}`, data)
      ElMessage.success('更新成功')
    } else {
      await api.post('/defects', data)
      ElMessage.success('创建成功')
    }
    
    goBack()
  } catch (error) {
    console.error('保存失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('保存失败')
    }
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/defects')
}

onMounted(() => {
  // 检查是否是编辑模式
  if (route.params.id) {
    isEdit.value = true
    fetchDefect(route.params.id)
  }
  
  // 检查是否有预置的发版ID（从发版详情页跳转过来）
  if (route.query.release_id) {
    preSelectedReleaseId.value = parseInt(route.query.release_id)
    defectForm.release_id = preSelectedReleaseId.value
    
    // 获取发版标题
    fetchReleaseTitle(preSelectedReleaseId.value)
  }
  
  fetchReleases()
  fetchUsers()
})

const fetchReleaseTitle = async (releaseId) => {
  try {
    const response = await api.get(`/releases/${releaseId}`)
    preSelectedReleaseTitle.value = response.data.title
  } catch (error) {
    console.error('获取发版标题失败:', error)
  }
}
</script>

<style scoped>
.defect-form-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.form-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  gap: 20px;
}

.form-header h1 {
  margin: 0;
  flex: 1;
}

.hint-text {
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}
</style>
