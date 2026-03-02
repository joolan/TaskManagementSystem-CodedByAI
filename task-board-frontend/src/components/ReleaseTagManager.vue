<template>
  <div class="release-tag-manager">
    <div class="tag-management-header">
      
      <el-button type="primary" @click="openAddTagDialog">
        添加标签
      </el-button>
    </div>
    
    <div class="tag-list">
      <el-table :data="releaseStore.releaseTags" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="标签名称" />
        <el-table-column label="标签颜色" width="120">
          <template #default="scope">
            <div class="color-preview" :style="{ backgroundColor: scope.row.color }"></div>
            <span>{{ scope.row.color }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="openEditTagDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDeleteTag(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 添加标签对话框 -->
    <el-dialog
      v-model="addTagDialogVisible"
      title="添加发版标签"
      width="500px"
    >
      <el-form :model="tagForm" :rules="tagRules" ref="tagFormRef" label-width="100px">
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="tagForm.name" placeholder="请输入标签名称" />
        </el-form-item>
        <el-form-item label="标签颜色" prop="color">
          <el-color-picker v-model="tagForm.color" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addTagDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAddTag" :loading="releaseStore.loading">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 编辑标签对话框 -->
    <el-dialog
      v-model="editTagDialogVisible"
      title="编辑发版标签"
      width="500px"
    >
      <el-form :model="tagForm" :rules="tagRules" ref="tagFormRef" label-width="100px">
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="tagForm.name" placeholder="请输入标签名称" />
        </el-form-item>
        <el-form-item label="标签颜色" prop="color">
          <el-color-picker v-model="tagForm.color" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editTagDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleEditTag" :loading="releaseStore.loading">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useReleaseStore } from '../store'
import { ElMessage } from 'element-plus'

const releaseStore = useReleaseStore()

// 标签管理相关
const addTagDialogVisible = ref(false)
const editTagDialogVisible = ref(false)
const tagFormRef = ref(null)
const currentTagId = ref(null)

const tagForm = ref({
  name: '',
  color: '#60a5fa'
})

const tagRules = {
  name: [
    { required: true, message: '请输入标签名称', trigger: 'blur' }
  ],
  color: [
    { required: true, message: '请选择标签颜色', trigger: 'change' }
  ]
}

const fetchTags = async () => {
  try {
    await releaseStore.fetchReleaseTags()
  } catch (error) {
    ElMessage.error('获取发版标签失败')
  }
}

// 将rgb颜色转换为hex格式
const rgbToHex = (rgb) => {
  if (rgb.startsWith('#')) return rgb
  const match = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/)
  if (!match) return rgb
  const r = parseInt(match[1])
  const g = parseInt(match[2])
  const b = parseInt(match[3])
  return '#' + [r, g, b].map(x => {
    const hex = x.toString(16)
    return hex.length === 1 ? '0' + hex : hex
  }).join('')
}

// 打开添加标签对话框
const openAddTagDialog = () => {
  tagForm.value = {
    name: '',
    color: '#60a5fa'
  }
  currentTagId.value = null
  addTagDialogVisible.value = true
}

// 打开编辑标签对话框
const openEditTagDialog = (tag) => {
  tagForm.value = {
    name: tag.name,
    color: tag.color
  }
  currentTagId.value = tag.id
  editTagDialogVisible.value = true
}

// 处理添加标签
const handleAddTag = async () => {
  if (!tagFormRef.value) return
  
  try {
    await tagFormRef.value.validate()
    
    // 转换颜色格式为hex
    const tagData = {
      ...tagForm.value,
      color: rgbToHex(tagForm.value.color)
    }
    
    await releaseStore.createReleaseTag(tagData)
    addTagDialogVisible.value = false
    ElMessage.success('标签添加成功')
  } catch (error) {
    console.error('添加标签失败:', error)
    ElMessage.error('添加标签失败')
  }
}

// 处理编辑标签
const handleEditTag = async () => {
  if (!tagFormRef.value) return
  
  try {
    await tagFormRef.value.validate()
    
    // 转换颜色格式为hex
    const tagData = {
      ...tagForm.value,
      color: rgbToHex(tagForm.value.color)
    }
    
    await releaseStore.updateReleaseTag(currentTagId.value, tagData)
    editTagDialogVisible.value = false
    ElMessage.success('标签更新成功')
  } catch (error) {
    console.error('更新标签失败:', error)
    ElMessage.error('更新标签失败')
  }
}

const handleDeleteTag = async (tagId) => {
  try {
    await releaseStore.deleteReleaseTag(tagId)
    ElMessage.success('标签删除成功')
  } catch (error) {
    ElMessage.error('标签删除失败')
  }
}

onMounted(() => {
  fetchTags()
})
</script>

<style scoped>
.release-tag-manager {

  background-color: #f9f9f9;
  border-radius: 8px;
}

.tag-management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.tag-management-header h3 {
  margin: 0;
}

.tag-list {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.color-preview {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 10px;
  vertical-align: middle;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style>
