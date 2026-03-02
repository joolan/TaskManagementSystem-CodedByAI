<template>
  <div>
    <div class="dashboard-container">
      <!-- 上部区域：我的地盘 -->
      <div class="my-territory">
        <h2 class="section-title">我的地盘</h2>
        <div class="metrics-grid">
          <!-- 我负责的未完成任务 -->
          <div class="metric-card" @click="handleMetricClick('my-tasks')">
            <div class="metric-header">
              <h3>我负责的未完成任务</h3>
              <el-icon><i class="el-icon-loading"></i></el-icon>
            </div>
            <div class="metric-value">{{ metrics.myAssignedTasksCount }}</div>
            <div class="metric-desc">待办、进行中、已暂停</div>
          </div>
          
          <!-- 我关注的未完成任务 -->
          <div class="metric-card" @click="handleMetricClick('my-followed-tasks')">
            <div class="metric-header">
              <h3>我关注的未完成任务</h3>
              <el-icon><i class="el-icon-connection"></i></el-icon>
            </div>
            <div class="metric-value">{{ metrics.myFollowedTasksCount }}</div>
            <div class="metric-desc">待办、进行中、已暂停</div>
          </div>
          
          <!-- 我关注的未发版本 -->
          <div class="metric-card" @click="handleMetricClick('my-followed-releases')">
            <div class="metric-header">
              <h3>我关注的未发版本</h3>
              <el-icon><i class="el-icon-s-flag"></i></el-icon>
            </div>
            <div class="metric-value">{{ metrics.myFollowedReleasesCount }}</div>
            <div class="metric-desc">计划中、延期中</div>
          </div>
          
          <!-- 我创建的待处理需求 -->
          <div class="metric-card" @click="handleMetricClick('my-requirements')">
            <div class="metric-header">
              <h3>我创建的待处理需求</h3>
              <el-icon><i class="el-icon-s-order"></i></el-icon>
            </div>
            <div class="metric-value">{{ metrics.myRequirementsCount }}</div>
            <div class="metric-desc">草稿、待评审、已确认</div>
          </div>
          
          <!-- 我负责的未完成缺陷 -->
          <div class="metric-card" @click="handleMetricClick('my-defects')">
            <div class="metric-header">
              <h3>我负责的未完成缺陷</h3>
              <el-icon><i class="el-icon-warning"></i></el-icon>
            </div>
            <div class="metric-value">{{ metrics.myAssignedDefectsCount }}</div>
            <div class="metric-desc">草稿、未解决</div>
          </div>
          
          <!-- 我的备忘录 -->
          <div class="metric-card">
            <div class="metric-header">
              <h3>我的备忘录</h3>
              <el-icon><i class="el-icon-notebook-2"></i></el-icon>
            </div>
            <div class="metric-value" @click="handleMemoCountClick">{{ metrics.myMemosCount }}</div>
            <div class="metric-desc">
              <el-button type="primary" size="small" @click="handleCreateMemo">新建</el-button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 下部区域：数据概览 -->
      <div class="data-overview">
        <div class="overview-header">
          <h2 class="section-title">数据概览</h2>
          <div class="date-range">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="handleDateRangeChange"
            />
          </div>
        </div>
        
        <div class="overview-content">
          <el-table :data="overviewData" style="width: 100%">
            <el-table-column prop="name" label="数据指标" width="180" />
            <el-table-column prop="uncompleted" label="未完成" />
            <el-table-column prop="completed" label="已完成" />
            <el-table-column prop="other" label="其他" />
          </el-table>
        </div>
      </div>
    </div>
    
    <!-- 备忘录列表弹窗 -->
    <el-dialog
      v-model="showMemoListDialog"
      title="我的备忘录"
      width="600px"
    >
      <el-table :data="memos" style="width: 100%">
        <el-table-column prop="name" label="备忘录名称" width="200" />
        <el-table-column prop="updated_at" label="最后修改时间">
          <template #default="scope">
            {{ scope.row.updated_at ? dayjs(scope.row.updated_at).format('YYYY-MM-DD HH:mm:ss') : '从未修改' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="openMemo(scope.row.id)">打开</el-button>
            <el-button size="small" type="danger" @click="deleteMemo(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
    
    <!-- 新建备忘录弹窗 -->
    <el-dialog
      v-model="showCreateMemoDialog"
      title="新建备忘录"
      width="400px"
    >
      <el-form :model="{ name: newMemoName }" label-width="100px">
        <el-form-item label="备忘录名称">
          <el-input v-model="newMemoName" placeholder="请输入备忘录名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateMemoDialog = false">取消</el-button>
          <el-button type="primary" @click="confirmCreateMemo">创建</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api, { memoApi } from '../api/index'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const router = useRouter()

// 日期范围
const dateRange = ref([])

// 我的地盘数据指标
const metrics = ref({
  myAssignedTasksCount: 0,
  myFollowedTasksCount: 0,
  myFollowedReleasesCount: 0,
  myRequirementsCount: 0,
  myAssignedDefectsCount: 0,
  myMemosCount: 0
})

// 备忘录相关状态
const showMemoListDialog = ref(false)
const showCreateMemoDialog = ref(false)
const newMemoName = ref('')
const memos = ref([])



// 数据概览数据
const overviewData = ref([
  {
    name: '任务',
    uncompleted: 0,
    completed: 0,
    other: 0
  },
  {
    name: '发版',
    uncompleted: 0,
    completed: 0,
    other: 0
  },
  {
    name: '需求',
    uncompleted: 0,
    completed: 0,
    other: 0
  },
  {
    name: '缺陷',
    uncompleted: 0,
    completed: 0,
    other: 0
  },
  {
    name: '我的工时',
    uncompleted: 0,
    completed: 0,
    other: 0
  }
])

// 初始化日期范围为当月1号到当月月底
const initDateRange = () => {
  const now = new Date()
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
  const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0)
  
  // 格式化日期为YYYY-MM-DD格式，使用本地时间
  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  
  dateRange.value = [
    formatDate(startOfMonth),
    formatDate(endOfMonth)
  ]
}

// 获取我的地盘数据
const fetchMyTerritoryData = async () => {
  try {
    const response = await api.get('/stats/dashboard')
    metrics.value = response.data
    // 获取备忘录数量
    try {
      const memoResponse = await memoApi.getMyMemos()
      metrics.value.myMemosCount = memoResponse.data.length
    } catch (memoError) {
      console.error('获取备忘录数量失败:', memoError)
      metrics.value.myMemosCount = 0
    }
  } catch (error) {
    console.error('获取我的地盘数据失败:', error)
  }
}

// 获取数据概览数据
const fetchOverviewData = async () => {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      const [startDate, endDate] = dateRange.value
      if (startDate) params.start_date = startDate
      if (endDate) params.end_date = endDate
    }
    
    const response = await api.get('/stats/overview', { params })
    
    overviewData.value = [
      {
        name: '任务',
        uncompleted: response.data.task.uncompleted,
        completed: response.data.task.completed,
        other: response.data.task.other
      },
      {
        name: '发版',
        uncompleted: response.data.release.uncompleted,
        completed: response.data.release.completed,
        other: response.data.release.other
      },
      {
        name: '需求',
        uncompleted: response.data.requirement.uncompleted,
        completed: response.data.requirement.completed,
        other: response.data.requirement.other
      },
      {
        name: '缺陷',
        uncompleted: response.data.defect?.uncompleted || 0,
        completed: response.data.defect?.completed || 0,
        other: response.data.defect?.other || 0
      },
      {
        name: '我的工时',
        uncompleted: response.data.my_hours?.uncompleted || 0,
        completed: response.data.my_hours?.completed || 0,
        other: response.data.my_hours?.other || 0
      }
    ]
  } catch (error) {
    console.error('获取数据概览数据失败:', error)
  }
}

// 处理指标点击事件
const handleMetricClick = (metricType) => {
  switch (metricType) {
    case 'my-tasks':
      router.push('/tasks?filter=my-assigned&status=uncompleted')
      break
    case 'my-followed-tasks':
      router.push('/tasks?filter=my-followed&status=uncompleted')
      break
    case 'my-followed-releases':
      router.push('/releases?filter=my-followed&status=unreleased')
      break
    case 'my-requirements':
      router.push('/requirements?filter=my-created&status=pending')
      break
    case 'my-defects':
      const userStr = localStorage.getItem('user')
      let userId = ''
      if (userStr) {
        try {
          const user = JSON.parse(userStr)
          userId = user.id || ''
        } catch (e) {
          console.error('解析用户信息失败:', e)
        }
      }
      router.push(`/defects?status=草稿,未解决&assignee_id=${userId}`)
      break
    default:
      break
  }
}

// 处理备忘录数量点击事件
const handleMemoCountClick = async () => {
  if (metrics.value.myMemosCount === 0) {
    ElMessage({ message: '请先创建备忘录', type: 'info' })
  } else {
    await fetchMyMemos()
    // 如果只有一个备忘录，直接打开详情页
    if (memos.value.length === 1) {
      openMemo(memos.value[0].id)
    } else {
      showMemoListDialog.value = true
    }
  }
}

// 处理新建备忘录按钮点击事件
const handleCreateMemo = () => {
  newMemoName.value = ''
  showCreateMemoDialog.value = true
}

// 获取用户的备忘录列表
const fetchMyMemos = async () => {
  try {
    const response = await memoApi.getMyMemos()
    memos.value = response.data
  } catch (error) {
    console.error('获取备忘录列表失败:', error)
    ElMessage.error('获取备忘录列表失败，请重试')
  }
}

// 打开备忘录
const openMemo = (memoId) => {
  // 这里应该跳转到备忘录详情页，或者打开一个新的弹窗显示备忘录内容
  // 暂时先关闭列表弹窗
  showMemoListDialog.value = false
  // 然后跳转到备忘录详情页
  router.push(`/memo/${memoId}`)
}

// 删除备忘录
const deleteMemo = (memoId) => {
  // 这里应该显示一个确认对话框
  ElMessageBox.confirm('确定要删除这个备忘录吗？此操作不可撤销。', '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await memoApi.deleteMemo(memoId)
      ElMessage.success('备忘录删除成功')
      // 重新获取备忘录列表
      await fetchMyMemos()
      // 更新备忘录数量
      metrics.value.myMemosCount = memos.value.length
    } catch (error) {
      console.error('删除备忘录失败:', error)
      ElMessage.error('删除备忘录失败，请重试')
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 确认创建备忘录
const confirmCreateMemo = async () => {
  if (!newMemoName.value.trim()) {
    ElMessage.error('请输入备忘录名称')
    return
  }
  
  try {
    const response = await memoApi.createMemo({ name: newMemoName.value.trim() })
    ElMessage.success('备忘录创建成功')
    // 关闭创建弹窗
    showCreateMemoDialog.value = false
    // 打开备忘录详情页
    router.push(`/memo/${response.data.id}`)
  } catch (error) {
    console.error('创建备忘录失败:', error)
    ElMessage.error('创建备忘录失败，请重试')
  }
}

// 处理日期范围变化
const handleDateRangeChange = (val) => {
  // 确保dateRange的值与组件的值同步，处理null值的情况
  dateRange.value = val === null ? [] : val || []
  // 触发数据更新
  fetchOverviewData()
}

// 页面加载时初始化
onMounted(() => {
  initDateRange()
  fetchMyTerritoryData()
  fetchOverviewData()
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

.section-title {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 20px;
  color: #333;
}

/* 我的地盘样式 */
.my-territory {
  margin-bottom: 40px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.metric-card {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.metric-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.metric-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #606266;
}

.metric-value {
  font-size: 32px;
  font-weight: 600;
  color: #409EFF;
  margin-bottom: 10px;
}

.metric-desc {
  font-size: 14px;
  color: #909399;
}

/* 数据概览样式 */
.data-overview {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.overview-header .section-title {
  margin: 0;
}

.date-range {
  display: flex;
  align-items: center;
}

.overview-content {
  margin-top: 20px;
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .overview-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
}
</style>