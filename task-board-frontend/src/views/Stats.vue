<template>
  <div class="stats-container">
    <div class="stats-grid">
      <!-- 任务状态统计 -->
      <el-card class="stats-card">
        <template #header>
          <div class="card-header">
            <span>任务状态统计</span>
          </div>
        </template>
        <div class="chart-container">
          <div ref="taskStatusChartRef" class="chart" style="height: 300px;"></div>
        </div>
      </el-card>
      
      <!-- 项目进度统计 -->
      <el-card class="stats-card">
        <template #header>
          <div class="card-header">
            <span>项目进度统计</span>
          </div>
        </template>
        <div class="progress-stats">
          <div class="progress-item">
            <span class="progress-label">总任务数</span>
            <span class="progress-value">{{ projectProgress.total_tasks || 0 }}</span>
          </div>
          <div class="progress-item">
            <span class="progress-label">已完成任务</span>
            <span class="progress-value">{{ projectProgress.completed_tasks || 0 }}</span>
          </div>
          <div class="progress-item">
            <span class="progress-label">完成率</span>
            <span class="progress-value">{{ projectProgress.completion_rate || 0 }}%</span>
          </div>
          <div class="progress-item">
            <span class="progress-label">逾期任务</span>
            <span class="progress-value overdue">{{ projectProgress.overdue_tasks || 0 }}</span>
          </div>
        </div>
        <div class="chart-container">
          <div ref="projectProgressChartRef" class="chart" style="height: 200px;"></div>
        </div>
      </el-card>
      
      <!-- 用户工作量统计 -->
      <el-card class="stats-card full-width">
        <template #header>
          <div class="card-header">
            <span>用户工作量统计</span>
          </div>
        </template>
        <div class="chart-container">
          <div ref="userWorkloadChartRef" class="chart" style="height: 400px;"></div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useStatsStore } from '../store'
import * as echarts from 'echarts'

const statsStore = useStatsStore()

const taskStatusChartRef = ref(null)
const projectProgressChartRef = ref(null)
const userWorkloadChartRef = ref(null)

const taskStatusChart = ref(null)
const projectProgressChart = ref(null)
const userWorkloadChart = ref(null)

const projectProgress = ref({
  total_tasks: 0,
  completed_tasks: 0,
  completion_rate: 0,
  overdue_tasks: 0
})

const initTaskStatusChart = () => {
  if (!taskStatusChartRef.value) return
  
  taskStatusChart.value = echarts.init(taskStatusChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '任务状态',
        type: 'pie',
        radius: '70%',
        data: statsStore.taskStatusStats.map(item => ({
          value: item.count,
          name: item.status_name,
          itemStyle: {
            color: item.color
          }
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  taskStatusChart.value.setOption(option)
}

const initProjectProgressChart = () => {
  if (!projectProgressChartRef.value) return
  
  projectProgressChart.value = echarts.init(projectProgressChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        data: ['总任务数', '已完成', '逾期任务'],
        axisTick: {
          alignWithLabel: true
        }
      }
    ],
    yAxis: [
      {
        type: 'value'
      }
    ],
    series: [
      {
        name: '数量',
        type: 'bar',
        barWidth: '60%',
        data: [
          projectProgress.value.total_tasks,
          projectProgress.value.completed_tasks,
          projectProgress.value.overdue_tasks
        ],
        itemStyle: {
          color: function(params) {
            const colors = ['#94a3b8', '#10b981', '#ef4444']
            return colors[params.dataIndex]
          }
        }
      }
    ]
  }
  
  projectProgressChart.value.setOption(option)
}

const initUserWorkloadChart = () => {
  if (!userWorkloadChartRef.value) return
  
  userWorkloadChart.value = echarts.init(userWorkloadChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['任务数', '预估工时', '实际工时']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: statsStore.userWorkloadStats.map(item => item.name)
    },
    yAxis: [
      {
        type: 'value',
        name: '数量',
        position: 'left'
      },
      {
        type: 'value',
        name: '工时',
        position: 'right'
      }
    ],
    series: [
      {
        name: '任务数',
        type: 'bar',
        data: statsStore.userWorkloadStats.map(item => item.task_count)
      },
      {
        name: '预估工时',
        type: 'line',
        yAxisIndex: 1,
        data: statsStore.userWorkloadStats.map(item => item.estimated_hours)
      },
      {
        name: '实际工时',
        type: 'line',
        yAxisIndex: 1,
        data: statsStore.userWorkloadStats.map(item => item.actual_hours)
      }
    ]
  }
  
  userWorkloadChart.value.setOption(option)
}

const handleResize = () => {
  taskStatusChart.value?.resize()
  projectProgressChart.value?.resize()
  userWorkloadChart.value?.resize()
}

onMounted(async () => {
  // 加载统计数据
  await statsStore.fetchTaskStatusStats()
  await statsStore.fetchUserWorkloadStats()
  const progressData = await statsStore.fetchProjectProgressStats()
  projectProgress.value = progressData
  
  // 初始化图表
  setTimeout(() => {
    initTaskStatusChart()
    initProjectProgressChart()
    initUserWorkloadChart()
  }, 100)
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  // 销毁图表实例
  taskStatusChart.value?.dispose()
  projectProgressChart.value?.dispose()
  userWorkloadChart.value?.dispose()
  
  // 移除事件监听
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.stats-container {
  padding: 10px;
  background-color: #ffffff;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.stats-card {
  margin-bottom: 0;
}

.full-width {
  grid-column: 1 / -1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  margin-top: 15px;
}

.progress-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 15px;
}

.progress-item {
  text-align: center;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.progress-label {
  display: block;
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
}

.progress-value {
  display: block;
  font-size: 22px;
  font-weight: 600;
  color: #333;
}

.progress-value.overdue {
  color: #ef4444;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .progress-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
