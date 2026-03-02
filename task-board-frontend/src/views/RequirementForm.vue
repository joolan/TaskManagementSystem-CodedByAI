<template>
  <div class="requirement-form-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button @click="handleBack">返回</el-button>
            <span>{{ isEdit ? '编辑需求' : '创建需求' }}</span>
          </div>
        </div>
      </template>
      
      <el-form :model="requirementForm" :rules="rules" ref="requirementFormRef" label-width="120px">
        <el-form-item label="需求来源" prop="source">
          <el-input v-model="requirementForm.source" placeholder="请输入需求来源" />
        </el-form-item>
        
        <el-form-item label="需求名称" prop="name">
          <el-input v-model="requirementForm.name" placeholder="请输入需求名称" />
        </el-form-item>
        
        <el-form-item label="需求标签" prop="tag_id">
          <el-select v-model="requirementForm.tag_id" placeholder="请选择需求标签">
            <el-option label="请选择" value=""></el-option>
            <el-option 
              v-for="tag in requirementTags" 
              :key="tag.id" 
              :label="tag.name" 
              :value="tag.id"
            >
              <span class="tag-option" :style="{ backgroundColor: tag.color + '20', color: tag.color }">
                {{ tag.name }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="需求描述" prop="description">
          <CustomRichTextEditor v-model="requirementForm.description" />
        </el-form-item>
        
        <el-form-item label="需求状态" prop="status">
          <el-select v-model="requirementForm.status" placeholder="请选择需求状态">
            <el-option label="草稿" value="草稿"></el-option>
            <el-option label="待评审" value="待评审"></el-option>
            <el-option label="已确认" value="已确认"></el-option>
            <el-option label="已作废" value="已作废"></el-option>
            <!-- 已转任务状态不能手动选择 -->
          </el-select>
        </el-form-item>
        
        <el-form-item label="需求优先级" prop="priority">
          <el-select v-model="requirementForm.priority" placeholder="请选择需求优先级">
            <el-option label="高" value="高"></el-option>
            <el-option label="中" value="中"></el-option>
            <el-option label="低" value="低"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="计划完成日期" prop="planned_completion_date">
          <el-date-picker
            v-model="requirementForm.planned_completion_date"
            type="datetime"
            placeholder="选择计划完成日期"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="实际完成日期" prop="actual_completion_date">
          <el-date-picker
            v-model="requirementForm.actual_completion_date"
            type="datetime"
            placeholder="选择实际完成日期"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">保存</el-button>
          <el-button @click="handleBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import CustomRichTextEditor from '../components/CustomRichTextEditor.vue'
import { requirementApi, requirementTagApi } from '../api/index'
import { useUserStore } from '../store'

const router = useRouter()
const route = useRoute()
const store = useUserStore()

// 状态管理
const requirementForm = ref({
  source: '',
  name: '',
  tag_id: '',
  description: '',
  status: '草稿',
  priority: '中',
  planned_completion_date: '',
  actual_completion_date: ''
})

const requirementFormRef = ref(null)
const requirementTags = ref([])
const submitLoading = ref(false)
const isEdit = computed(() => route.path.includes('/edit/'))
const requirementId = computed(() => route.params.id)

// 表单验证规则
const rules = {
  source: [
    { required: true, message: '请输入需求来源', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入需求名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入需求描述', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择需求状态', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择需求优先级', trigger: 'change' }
  ]
}

// 获取需求标签
const fetchRequirementTags = async () => {
  try {
    const response = await requirementTagApi.getRequirementTags()
    requirementTags.value = response.data
  } catch (error) {
    console.error('获取需求标签失败:', error)
    ElMessage.error('获取需求标签失败')
  }
}

// 获取需求详情
const fetchRequirementDetail = async () => {
  if (!isEdit.value || !requirementId.value) return
  
  try {
    const response = await requirementApi.getRequirement(requirementId.value)
    const requirement = response.data
    requirementForm.value = {
      source: requirement.source,
      name: requirement.name,
      tag_id: requirement.tag_id || '',
      description: requirement.description,
      status: requirement.status,
      priority: requirement.priority,
      planned_completion_date: requirement.planned_completion_date,
      actual_completion_date: requirement.actual_completion_date
    }
  } catch (error) {
    console.error('获取需求详情失败:', error)
    ElMessage.error('获取需求详情失败')
  }
}

// 初始加载
onMounted(async () => {
  await fetchRequirementTags()
  if (isEdit.value) {
    await fetchRequirementDetail()
  }
})

// 处理返回
const handleBack = () => {
  router.push('/requirements')
}

// 处理提交
const handleSubmit = async () => {
  if (!requirementFormRef.value) return
  
  try {
    await requirementFormRef.value.validate()
    submitLoading.value = true
    
    if (isEdit.value && requirementId.value) {
      // 编辑需求
      await requirementApi.updateRequirement(requirementId.value, requirementForm.value)
      ElMessage.success('编辑成功')
    } else {
      // 创建需求
      await requirementApi.createRequirement(requirementForm.value)
      ElMessage.success('创建成功')
    }
    
    router.push('/requirements')
  } catch (error) {
    console.error('保存失败:', error)
    if (error.name === 'ValidationError') {
      // 表单验证失败，不显示错误消息
    } else {
      ElMessage.error('保存失败')
    }
  } finally {
    submitLoading.value = false
  }
}
</script>

<style scoped>
.requirement-form-container {
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

.tag-option {
  display: block;
  padding: 2px 8px;
  border-radius: 4px;
}
</style>
