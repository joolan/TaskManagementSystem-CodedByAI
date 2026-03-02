<template>
  <div class="memo-detail-container">
    <div class="memo-header">
      <el-button @click="goBack" size="small">返回</el-button>
      <div class="title-container">
        <h1 v-if="!editingTitle" class="memo-title" @click="startEditTitle">{{ memo.name }}</h1>
        <div v-else class="title-edit">
          <el-input v-model="editingTitleName" placeholder="请输入备忘录名称" />
          <div class="title-edit-actions">
            <el-button size="small" @click="cancelEditTitle">取消</el-button>
            <el-button size="small" type="primary" @click="saveTitle">保存</el-button>
          </div>
        </div>
      </div>
      <div class="memo-actions">
        <el-button type="primary" size="small" @click="saveMemoContent">保存</el-button>
        <el-button type="danger" size="small" @click="handleDeleteMemo">删除</el-button>
      </div>
    </div>
    
    <div class="memo-content">
      <div class="editor-container">
        <!-- 使用自定义富文本编辑器 -->
        <CustomRichTextEditor
          v-model="memoContent"
          :placeholder="'请输入备忘录内容...'"
          :height="400"
          @change="handleContentChange"
        />
      </div>
    </div>
    
    <div class="memo-footer">
      <div class="memo-meta">
        <span>创建时间: {{ memo.created_at ? dayjs(memo.created_at).format('YYYY-MM-DD HH:mm:ss') : '未知' }}</span>
        <span>最后修改: {{ memo.updated_at ? dayjs(memo.updated_at).format('YYYY-MM-DD HH:mm:ss') : '从未修改' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import api, { memoApi } from '../api/index'
import CustomRichTextEditor from '../components/CustomRichTextEditor.vue'

const router = useRouter()
const route = useRoute()
const memoId = route.params.id

// 备忘录状态
const memo = ref({})
const memoContent = ref('')
let autoSaveTimer = null
let lastSavedContent = ''

// 标题编辑状态
const editingTitle = ref(false)
const editingTitleName = ref('')

// 获取备忘录详情
const fetchMemoDetail = async () => {
  try {
    const response = await memoApi.getMemo(memoId)
    memo.value = response.data
    memoContent.value = response.data.content || ''
    lastSavedContent = memoContent.value
  } catch (error) {
    console.error('获取备忘录详情失败:', error)
    ElMessage.error('获取备忘录详情失败，请重试')
  }
}

// 处理内容变化，更新内容变化状态
const handleContentChange = () => {
  // 内容变化时不需要立即保存，由定时保存逻辑处理
}

// 保存备忘录内容
const saveMemoContent = async () => {
  try {
    // 只有当内容发生变化时才保存
    if (memoContent.value !== lastSavedContent) {
      const response = await memoApi.updateMemo(memoId, { content: memoContent.value })
      memo.value = response.data
      lastSavedContent = memoContent.value
      ElMessage.success('保存成功')
    }
  } catch (error) {
    console.error('保存备忘录内容失败:', error)
    ElMessage.error('保存失败，请重试')
  }
}

// 处理删除备忘录
const handleDeleteMemo = () => {
  ElMessageBox.confirm('确定要删除这个备忘录吗？此操作不可撤销。', '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await memoApi.deleteMemo(memoId)
      ElMessage.success('备忘录删除成功')
      // 跳转到仪表盘
      router.push('/dashboard')
    } catch (error) {
      console.error('删除备忘录失败:', error)
      ElMessage.error('删除备忘录失败，请重试')
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 开始编辑标题
const startEditTitle = () => {
  editingTitle.value = true
  editingTitleName.value = memo.value.name
}

// 取消编辑标题
const cancelEditTitle = () => {
  editingTitle.value = false
  editingTitleName.value = memo.value.name
}

// 保存标题
const saveTitle = async () => {
  if (!editingTitleName.value.trim()) {
    ElMessage.error('请输入备忘录名称')
    return
  }
  
  try {
    const response = await memoApi.updateMemo(memoId, { name: editingTitleName.value.trim() })
    memo.value = response.data
    editingTitle.value = false
    ElMessage.success('标题修改成功')
  } catch (error) {
    console.error('修改标题失败:', error)
    ElMessage.error('修改标题失败，请重试')
  }
}

// 返回上一页
const goBack = () => {
  router.push('/dashboard')
}

// 定时自动保存函数
const setupAutoSave = () => {
  // 每2分钟自动保存一次
  autoSaveTimer = setInterval(async () => {
    await saveMemoContent()
  }, 2 * 60 * 1000) // 2分钟
}

// 清理定时器
const cleanupAutoSave = () => {
  if (autoSaveTimer) {
    clearInterval(autoSaveTimer)
    autoSaveTimer = null
  }
}

// 页面加载时获取备忘录详情
onMounted(() => {
  fetchMemoDetail()
  // 设置定时自动保存
  setupAutoSave()
})

// 组件卸载时清理定时器
onBeforeUnmount(() => {
  cleanupAutoSave()
})
</script>

<style scoped>
.memo-detail-container {
  padding: 20px;
  min-height: 100%;
  box-sizing: border-box;
}

.memo-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eaeaea;
}

.memo-header .el-button {
  margin-right: 20px;
}

.title-container {
  flex: 1;
  margin: 0 20px;
}

.memo-title {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
  color: #333;
  cursor: pointer;
  transition: color 0.3s;
}

.memo-title:hover {
  color: #409eff;
}

.title-edit {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-edit .el-input {
  flex: 1;
  max-width: 400px;
}

.title-edit-actions {
  display: flex;
  gap: 5px;
}

.memo-content {
  margin-bottom: 20px;
}

.editor-container {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.memo-footer {
  padding-top: 10px;
  border-top: 1px solid #eaeaea;
}

.memo-meta {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #999;
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .memo-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .memo-header .el-button {
    margin-right: 10px;
  }
  
  .memo-meta {
    flex-direction: column;
    gap: 5px;
  }
}
</style>