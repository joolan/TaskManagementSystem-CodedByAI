<template>
  <div>
    <div class="system-settings-container">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>系统设置</span>
          </div>
        </template>
        
        <!-- 消息提示 -->
        <div v-if="visibleAlert" style="position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 10000; width: 80%; max-width: 600px;">
          <el-alert
            :type="messageType"
            show-icon
            :closable="true"
            @close="visibleAlert = false"
            :effect="'dark'"
          >
            <template #default>
              <div>
                <strong>{{ messageType === 'success' ? '操作成功' : '操作失败' }}</strong>
                <div v-html="message"></div>
              </div>
            </template>
          </el-alert>
        </div>
        
        <div class="settings-item">
          <div class="setting-label">
            <span>允许用户注册</span>
            <el-tooltip content="开启后，用户可以通过注册页面自助注册账号" placement="right">
              <el-icon class="info-icon"><QuestionFilled /></el-icon>
            </el-tooltip>
          </div>
          <div class="setting-control">
            <el-switch
              v-model="allowRegistration"
              active-text="开启"
              inactive-text="关闭"
              @change="handleAllowRegistrationChange"
              :loading="saving"
            />
          </div>
        </div>
        
        <div class="settings-item">
          <div class="setting-label">
            <span>系统名称</span>
          </div>
          <div class="setting-control">
            <el-input
              v-model="siteName"
              placeholder="请输入系统名称"
              style="width: 300px"
            />
            <el-button
              type="primary"
              @click="handleSiteNameChange"
              :loading="saving"
              style="margin-left: 10px"
            >
              保存
            </el-button>
          </div>
        </div>
        
        <div class="settings-item">
          <div class="setting-label">
            <span>用户账号多地点同时登录数限制</span>
            <el-tooltip content="设置同一时间相同用户仅允许在线个数，超过限制后后登录用户会将前面最早登录用户踢下线，确保同时在线数不超过此配置" placement="right">
              <el-icon class="info-icon"><WarningFilled /></el-icon>
            </el-tooltip>
          </div>
          <div class="setting-control">
            <el-input-number
              v-model="maxSessionsPerUser"
              :min="1"
              :max="10"
              style="width: 200px"
            />
            <el-button
              type="primary"
              @click="handleMaxSessionsChange"
              :loading="saving"
              style="margin-left: 10px"
            >
              保存
            </el-button>
          </div>
        </div>
        
        <!-- 任务标签管理 -->
        <div class="settings-item">
          <div class="setting-label">
            <span>任务标签管理</span>
          </div>
          <div class="tag-management">
            <el-button
              type="primary"
              @click="openAddTagDialog"
              style="margin-bottom: 20px"
            >
              添加标签
            </el-button>
            
            <el-table :data="tags" style="width: 100%">
              <el-table-column prop="name" label="标签名称" width="180" />
              <el-table-column prop="color" label="标签颜色" width="120">
                <template #default="scope">
                  <div 
                    class="color-preview" 
                    :style="{ backgroundColor: scope.row.color }"
                  ></div>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="180" fixed="right">
                <template #default="scope">
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="openEditTagDialog(scope.row)"
                  >
                    编辑
                  </el-button>
                  <el-button 
                    type="danger" 
                    size="small" 
                    @click="handleDeleteTag(scope.row.id)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
        
        <!-- 发版标签管理 -->
        <div class="settings-item">
          <div class="setting-label">
            <span>发版标签管理</span>
          </div>
          <div class="tag-management">
            <ReleaseTagManager />
          </div>
        </div>
        
        <!-- 需求标签管理 -->
        <div class="settings-item">
          <div class="setting-label">
            <span>需求标签管理</span>
          </div>
          <div class="tag-management">
            <div class="tag-actions">
              <el-button
                type="primary"
                @click="openAddRequirementTagDialog"
                style="margin-bottom: 20px"
              >
                添加标签
              </el-button>
            </div>
            
            <el-table :data="requirementTags" style="width: 100%">
              <el-table-column prop="name" label="标签名称" width="180" />
              <el-table-column prop="color" label="标签颜色" width="120">
                <template #default="scope">
                  <div 
                    class="color-preview" 
                    :style="{ backgroundColor: scope.row.color }"
                  ></div>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="180" fixed="right">
                <template #default="scope">
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="openEditRequirementTagDialog(scope.row)"
                  >
                    编辑
                  </el-button>
                  <el-button 
                    type="danger" 
                    size="small" 
                    @click="handleDeleteRequirementTag(scope.row.id)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
        
        <!-- 数据库备份还原 -->
        <div class="settings-item">
          <div class="setting-label">
            <span>数据库备份还原</span>
          </div>
          <div class="database-management">
            <div class="database-actions">
              <el-button
                type="primary"
                @click="handleBackupDatabase"
                :loading="backupLoading"
                :disabled="backupLoading || restoreLoading"
              >
                <el-icon><Download /></el-icon>
                备份数据库
              </el-button>
              <el-upload
                ref="uploadRef"
                :auto-upload="false"
                :show-file-list="false"
                :on-change="handleFileChange"
                accept=".db"
                :disabled="backupLoading || restoreLoading"
              >
                <el-button
                  type="warning"
                  :loading="restoreLoading"
                  :disabled="backupLoading || restoreLoading"
                >
                  <el-icon><Upload /></el-icon>
                  还原数据库
                </el-button>
              </el-upload>
            </div>
            
            <div v-if="backupLoading || restoreLoading" class="loading-animation">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>{{ backupLoading ? '备份中……' : '还原中……' }}</span>
              <p class="loading-tip">请勿进行其他操作</p>
            </div>
            
            <el-divider>备份列表</el-divider>
            
            <el-table :data="backups" style="width: 100%" v-loading="backupsLoading">
              <el-table-column prop="filename" label="备份文件名" width="280" />
              <el-table-column prop="size" label="文件大小" width="120">
                <template #default="scope">
                  {{ formatFileSize(scope.row.size) }}
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" width="200">
                <template #default="scope">
                  {{ formatDateTime(scope.row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="scope">
                  <el-button 
                    type="danger" 
                    size="small" 
                    @click="handleDeleteBackup(scope.row.filename)"
                    :disabled="backupLoading || restoreLoading"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 添加标签对话框 -->
    <el-dialog
      v-model="addTagDialogVisible"
      title="添加标签"
      width="500px"
    >
      <el-form :model="tagForm" :rules="tagRules" ref="tagFormRef" label-width="100px">
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="tagForm.name" placeholder="请输入标签名称"></el-input>
        </el-form-item>
        <el-form-item label="标签颜色" prop="color">
          <el-color-picker v-model="tagForm.color" show-alpha></el-color-picker>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addTagDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAddTag">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 编辑标签对话框 -->
    <el-dialog
      v-model="editTagDialogVisible"
      title="编辑标签"
      width="500px"
    >
      <el-form :model="tagForm" :rules="tagRules" ref="tagFormRef" label-width="100px">
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="tagForm.name" placeholder="请输入标签名称"></el-input>
        </el-form-item>
        <el-form-item label="标签颜色" prop="color">
          <el-color-picker v-model="tagForm.color" show-alpha></el-color-picker>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editTagDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleEditTag">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 添加需求标签对话框 -->
    <el-dialog
      v-model="addRequirementTagDialogVisible"
      title="添加需求标签"
      width="500px"
    >
      <el-form :model="requirementTagForm" :rules="tagRules" ref="requirementTagFormRef" label-width="100px">
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="requirementTagForm.name" placeholder="请输入标签名称"></el-input>
        </el-form-item>
        <el-form-item label="标签颜色" prop="color">
          <el-color-picker v-model="requirementTagForm.color" show-alpha></el-color-picker>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addRequirementTagDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAddRequirementTag">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 编辑需求标签对话框 -->
    <el-dialog
      v-model="editRequirementTagDialogVisible"
      title="编辑需求标签"
      width="500px"
    >
      <el-form :model="requirementTagForm" :rules="tagRules" ref="requirementTagFormRef" label-width="100px">
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="requirementTagForm.name" placeholder="请输入标签名称"></el-input>
        </el-form-item>
        <el-form-item label="标签颜色" prop="color">
          <el-color-picker v-model="requirementTagForm.color" show-alpha></el-color-picker>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editRequirementTagDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleEditRequirementTag">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../api'
import ReleaseTagManager from '../components/ReleaseTagManager.vue'
import { requirementTagApi, databaseApi } from '../api/index'
import { ElMessageBox } from 'element-plus'
import { QuestionFilled, WarningFilled, Download, Upload, Loading } from '@element-plus/icons-vue'

// 响应消息
const message = ref('')
const messageType = ref('success')
const visibleAlert = ref(false)

// 监听message变化
watch(() => message.value, (newValue) => {
  //console.log('message变化:', newValue)
  //console.log('messageType:', messageType.value)
  if (newValue) {
    visibleAlert.value = true
  }
})

// 重置消息状态的函数
const resetMessage = () => {
  message.value = ''
  messageType.value = 'success'
  // 不重置visibleAlert，由message变化控制
}

// 确保每次操作前重置消息状态
const prepareOperation = () => {
  resetMessage()
}

// 显示消息的函数
const showMessage = (msg, type = 'success') => {
  message.value = msg
  messageType.value = type
  visibleAlert.value = true
}

// 加载状态
const saving = ref(false)

// 设置值
const allowRegistration = ref(false)
const siteName = ref('')
const maxSessionsPerUser = ref(2)

// 标签管理相关
const tags = ref([])
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

// 需求标签管理相关
const requirementTags = ref([])
const addRequirementTagDialogVisible = ref(false)
const editRequirementTagDialogVisible = ref(false)
const requirementTagFormRef = ref(null)
const currentRequirementTagId = ref(null)

const requirementTagForm = ref({
  name: '',
  color: '#60a5fa'
})

// 数据库备份还原相关
const backupLoading = ref(false)
const restoreLoading = ref(false)
const backupsLoading = ref(false)
const backups = ref([])
const uploadRef = ref(null)

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

// 格式化日期时间（北京时间）
const formatDateTime = (isoString) => {
  const date = new Date(isoString)
  const beijingOffset = 8 * 60
  const localOffset = date.getTimezoneOffset()
  const beijingTime = new Date(date.getTime() + (localOffset + beijingOffset) * 60000)
  
  const year = beijingTime.getFullYear()
  const month = String(beijingTime.getMonth() + 1).padStart(2, '0')
  const day = String(beijingTime.getDate()).padStart(2, '0')
  const hours = String(beijingTime.getHours()).padStart(2, '0')
  const minutes = String(beijingTime.getMinutes()).padStart(2, '0')
  const seconds = String(beijingTime.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

// 加载备份列表
const loadBackups = async () => {
  backupsLoading.value = true
  try {
    const response = await databaseApi.getBackups()
    backups.value = response.data
  } catch (error) {
    console.error('加载备份列表失败:', error)
    message.value = '加载备份列表失败'
    messageType.value = 'error'
  } finally {
    backupsLoading.value = false
  }
}

// 备份数据库
const handleBackupDatabase = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要备份数据库吗？备份过程可能需要一些时间，请勿进行其他操作。',
      '确认备份',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    prepareOperation()
    backupLoading.value = true
    const response = await databaseApi.backupDatabase()
    
    // 检查响应结构
    if (!response.data) {
      throw new Error('服务器返回数据格式错误')
    }
    
    if (response.data.success) {
      showMessage((response.data.message || '备份成功').replace(/\n/g, '<br>'), 'success')
      await loadBackups()
    } else {
      showMessage((response.data.message || '备份失败').replace(/\n/g, '<br>'), 'error')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('备份数据库失败:', error)
      console.log('错误详情:', {
        hasResponse: !!error.response,
        hasResponseData: !!error.response?.data,
        responseStatus: error.response?.status,
        responseData: error.response?.data
      })
      
      // 详细的错误信息处理
      if (error.response) {
        // 接口状态码错误
        const responseData = error.response.data
        
        // 优先检查detail字段
        if (responseData && responseData.detail) {
          showMessage(responseData.detail.replace(/\n/g, '<br>'), 'error')
        } 
        // 其次检查message字段
        else if (responseData && responseData.message) {
          showMessage(responseData.message.replace(/\n/g, '<br>'), 'error')
        }
        // 根据状态码显示通用错误
        else if (error.response.status === 403) {
          showMessage('权限不足，无法操作数据库', 'error')
        } else if (error.response.status === 500) {
          // 500错误时，尝试显示整个data
          if (responseData) {
            try {
              const dataStr = typeof responseData === 'string' 
                ? responseData 
                : JSON.stringify(responseData)
              showMessage(dataStr.replace(/\n/g, '<br>'), 'error')
            } catch (e) {
              showMessage('服务器内部错误，请稍后重试', 'error')
            }
          } else {
            showMessage('服务器内部错误，请稍后重试', 'error')
          }
        } else {
          showMessage(`请求失败 (${error.response.status})`, 'error')
        }
      } else if (error.request) {
        // 请求已发送但没有收到响应
        showMessage('网络错误，无法连接到服务器', 'error')
      } else {
        // 其他错误
        showMessage((error.message || '备份数据库失败').replace(/\n/g, '<br>'), 'error')
      }
      
    }
  } finally {
    backupLoading.value = false
  }
}

// 处理文件选择
const handleFileChange = async (file) => {
  try {
    await ElMessageBox.confirm(
      '确定要还原数据库吗？还原前系统会自动备份当前数据库，还原过程可能需要一些时间，请勿进行其他操作。',
      '确认还原',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    prepareOperation()
    restoreLoading.value = true
    const response = await databaseApi.restoreDatabase(file.raw)
    
    // 检查响应结构
    if (!response.data) {
      throw new Error('服务器返回数据格式错误')
    }
    
    if (response.data.success) {
      showMessage((response.data.message || '还原成功').replace(/\n/g, '<br>'), 'success')
      await loadBackups()
    } else {
      let errorMessage = (response.data.message || '还原失败').replace(/\n/g, '<br>')
      if (response.data.validation_result) {
        const vr = response.data.validation_result
        if (vr.missing_tables && vr.missing_tables.length > 0) {
          errorMessage += `<br>缺失的表: ${vr.missing_tables.join(', ')}`
        }
        if (vr.missing_columns) {
          for (const [table, cols] of Object.entries(vr.missing_columns)) {
            errorMessage += `<br>表 ${table} 缺失的字段: ${cols.join(', ')}`
          }
        }
      }
      showMessage(errorMessage, 'error')
      
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('还原数据库失败:', error)
      
      console.log('错误详情:', {
        hasResponse: !!error.response,
        hasResponseData: !!error.response?.data,
        responseStatus: error.response?.status,
        responseData: error.response?.data
      })
      
      // 详细的错误信息处理
      if (error.response) {
        // 接口状态码错误
        const responseData = error.response.data
        
        // 优先检查detail字段
        if (responseData && responseData.detail) {
          showMessage(responseData.detail.replace(/\n/g, '<br>'), 'error')
        } 
        // 其次检查message字段
        else if (responseData && responseData.message) {
          showMessage(responseData.message.replace(/\n/g, '<br>'), 'error')
        }
        // 根据状态码显示通用错误
        else if (error.response.status === 400) {
          showMessage('请求参数错误，请检查文件格式', 'error')
        } else if (error.response.status === 403) {
          showMessage('权限不足，无法操作数据库', 'error')
        } else if (error.response.status === 500) {
          // 500错误时，尝试显示整个data
          if (responseData) {
            try {
              const dataStr = typeof responseData === 'string' 
                ? responseData 
                : JSON.stringify(responseData)
              showMessage(dataStr.replace(/\n/g, '<br>'), 'error')
            } catch (e) {
              showMessage('服务器内部错误，请稍后重试', 'error')
            }
          } else {
            showMessage('服务器内部错误，请稍后重试', 'error')
          }
        } else {
          showMessage(`请求失败 (${error.response.status})`, 'error')
        }
      } else if (error.request) {
        // 请求已发送但没有收到响应
        showMessage('网络错误，无法连接到服务器', 'error')
      } else {
        // 其他错误
        showMessage((error.message || '还原数据库失败').replace(/\n/g, '<br>'), 'error')
      }
      
    }
  } finally {
    restoreLoading.value = false
    if (uploadRef.value) {
      uploadRef.value.clearFiles()
    }
  }
}

// 删除备份
const handleDeleteBackup = async (filename) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除备份文件 "${filename}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await databaseApi.deleteBackup(filename)
    message.value = '删除备份文件成功'
    messageType.value = 'success'
    await loadBackups()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除备份文件失败:', error)
      message.value = error.response?.data?.detail || '删除备份文件失败'
      messageType.value = 'error'
    }
  }
}

// 加载系统设置
const loadSettings = async () => {
  try {
    const response = await api.get('/settings')
    const settings = response.data
    
    // 查找并设置 allow_registration
    const regSetting = settings.find(s => s.key === 'allow_registration')
    if (regSetting) {
      allowRegistration.value = regSetting.value === 'true'
    }
    
    // 查找并设置 site_name
    const nameSetting = settings.find(s => s.key === 'site_name')
    if (nameSetting) {
      siteName.value = nameSetting.value
    }
    
    // 查找并设置 max_sessions_per_user
    const sessionsSetting = settings.find(s => s.key === 'max_sessions_per_user')
    if (sessionsSetting) {
      maxSessionsPerUser.value = parseInt(sessionsSetting.value)
    }
  } catch (error) {
    console.error('加载系统设置失败:', error)
    message.value = '加载系统设置失败'
    messageType.value = 'error'
  }
}

// 加载标签列表
const loadTags = async () => {
  try {
    const response = await api.get('/tasks/tags/all')
    tags.value = response.data
  } catch (error) {
    console.error('加载标签列表失败:', error)
    message.value = '加载标签列表失败'
    messageType.value = 'error'
  }
}

// 加载需求标签列表
const loadRequirementTags = async () => {
  try {
    const response = await requirementTagApi.getRequirementTags()
    requirementTags.value = response.data
  } catch (error) {
    console.error('加载需求标签列表失败:', error)
    message.value = '加载需求标签列表失败'
    messageType.value = 'error'
  }
}

// 处理允许注册开关变化
const handleAllowRegistrationChange = async (value) => {
  saving.value = true
  try {
    await api.put('/settings/allow_registration', {
      value: value ? 'true' : 'false',
      description: '是否允许用户自助注册'
    })
    message.value = '设置保存成功'
    messageType.value = 'success'
  } catch (error) {
    console.error('保存设置失败:', error)
    message.value = '保存设置失败'
    messageType.value = 'error'
    // 恢复原状态
    allowRegistration.value = !value
  } finally {
    saving.value = false
  }
}

// 处理系统名称变化
const handleSiteNameChange = async () => {
  saving.value = true
  try {
    await api.put('/settings/site_name', {
      value: siteName.value,
      description: '系统名称'
    })
    message.value = '设置保存成功'
    messageType.value = 'success'
  } catch (error) {
    console.error('保存设置失败:', error)
    message.value = '保存设置失败'
    messageType.value = 'error'
  } finally {
    saving.value = false
  }
}

const handleMaxSessionsChange = async () => {
  saving.value = true
  try {
    await api.put('/settings/max_sessions_per_user', {
      value: maxSessionsPerUser.value.toString(),
      description: '同一时间相同用户仅允许在线个数，超过限制后后登录用户会将前面最早登录用户踢下线，确保同时在线数不超过此配置'
    })
    message.value = '设置保存成功'
    messageType.value = 'success'
  } catch (error) {
    console.error('保存设置失败:', error)
    message.value = '保存设置失败'
    messageType.value = 'error'
  } finally {
    saving.value = false
  }
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

// 处理添加标签
const handleAddTag = async () => {
  if (!tagFormRef.value) return
  
  try {
    await tagFormRef.value.validate()
    saving.value = true
    
    // 转换颜色格式为hex
    const tagData = {
      ...tagForm.value,
      color: rgbToHex(tagForm.value.color)
    }
    
    const response = await api.post('/tasks/tags', tagData)
    tags.value.push(response.data)
    addTagDialogVisible.value = false
    message.value = '添加标签成功'
    messageType.value = 'success'
  } catch (error) {
    console.error('添加标签失败:', error)
    message.value = error.response?.data?.detail || '添加标签失败'
    messageType.value = 'error'
  } finally {
    saving.value = false
  }
}

// 处理编辑标签
const handleEditTag = async () => {
  if (!tagFormRef.value) return
  
  try {
    await tagFormRef.value.validate()
    saving.value = true
    
    // 转换颜色格式为hex
    const tagData = {
      ...tagForm.value,
      color: rgbToHex(tagForm.value.color)
    }
    
    const response = await api.put(`/tasks/tags/${currentTagId.value}`, tagData)
    const index = tags.value.findIndex(tag => tag.id === currentTagId.value)
    if (index !== -1) {
      tags.value[index] = response.data
    }
    editTagDialogVisible.value = false
    message.value = '编辑标签成功'
    messageType.value = 'success'
  } catch (error) {
    console.error('编辑标签失败:', error)
    message.value = error.response?.data?.detail || '编辑标签失败'
    messageType.value = 'error'
  } finally {
    saving.value = false
  }
}

// 处理删除标签
const handleDeleteTag = async (tagId) => {
  try {
    await api.delete(`/tasks/tags/${tagId}`)
    tags.value = tags.value.filter(tag => tag.id !== tagId)
    message.value = '删除标签成功'
    messageType.value = 'success'
  } catch (error) {
    console.error('删除标签失败:', error)
    message.value = error.response?.data?.detail || '删除标签失败'
    messageType.value = 'error'
  }
}

// 打开添加需求标签对话框
const openAddRequirementTagDialog = () => {
  requirementTagForm.value = {
    name: '',
    color: '#60a5fa'
  }
  currentRequirementTagId.value = null
  addRequirementTagDialogVisible.value = true
}

// 打开编辑需求标签对话框
const openEditRequirementTagDialog = (tag) => {
  requirementTagForm.value = {
    name: tag.name,
    color: tag.color
  }
  currentRequirementTagId.value = tag.id
  editRequirementTagDialogVisible.value = true
}

// 处理添加需求标签
const handleAddRequirementTag = async () => {
  if (!requirementTagFormRef.value) return
  
  try {
    await requirementTagFormRef.value.validate()
    saving.value = true
    
    // 转换颜色格式为hex
    const tagData = {
      ...requirementTagForm.value,
      color: rgbToHex(requirementTagForm.value.color)
    }
    
    const response = await requirementTagApi.createRequirementTag(tagData)
    requirementTags.value.push(response.data)
    addRequirementTagDialogVisible.value = false
    message.value = '添加需求标签成功'
    messageType.value = 'success'
  } catch (error) {
    console.error('添加需求标签失败:', error)
    message.value = error.response?.data?.detail || '添加需求标签失败'
    messageType.value = 'error'
  } finally {
    saving.value = false
  }
}

// 处理编辑需求标签
const handleEditRequirementTag = async () => {
  if (!requirementTagFormRef.value) return
  
  try {
    await requirementTagFormRef.value.validate()
    saving.value = true
    
    // 转换颜色格式为hex
    const tagData = {
      ...requirementTagForm.value,
      color: rgbToHex(requirementTagForm.value.color)
    }
    
    const response = await requirementTagApi.updateRequirementTag(currentRequirementTagId.value, tagData)
    const index = requirementTags.value.findIndex(tag => tag.id === currentRequirementTagId.value)
    if (index !== -1) {
      requirementTags.value[index] = response.data
    }
    editRequirementTagDialogVisible.value = false
    message.value = '编辑需求标签成功'
    messageType.value = 'success'
  } catch (error) {
    console.error('编辑需求标签失败:', error)
    message.value = error.response?.data?.detail || '编辑需求标签失败'
    messageType.value = 'error'
  } finally {
    saving.value = false
  }
}

// 处理删除需求标签
const handleDeleteRequirementTag = async (tagId) => {
  try {
    await requirementTagApi.deleteRequirementTag(tagId)
    requirementTags.value = requirementTags.value.filter(tag => tag.id !== tagId)
    message.value = '删除需求标签成功'
    messageType.value = 'success'
  } catch (error) {
    console.error('删除需求标签失败:', error)
    message.value = error.response?.data?.detail || '删除需求标签失败'
    messageType.value = 'error'
  }
}

// 页面加载时加载设置和标签
onMounted(() => {
  loadSettings()
  loadTags()
  loadRequirementTags()
  loadBackups()
})
</script>

<style scoped>
.system-settings-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.settings-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.settings-item:last-child {
  border-bottom: none;
}

.setting-label {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #333;
}

.info-icon {
  margin-left: 8px;
  color: #909399;
  cursor: help;
}

.setting-control {
  display: flex;
  align-items: center;
}

.tag-management {
  flex: 1;
  margin-left: 20px;
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
}

.color-preview {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}

.database-management {
  flex: 1;
  margin-left: 20px;
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
}

.database-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.loading-animation {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 20px;
}

.loading-animation .el-icon {
  font-size: 32px;
  color: #409EFF;
  margin-bottom: 10px;
}

.loading-animation span {
  font-size: 16px;
  color: #333;
  margin-bottom: 5px;
}

.loading-tip {
  font-size: 12px;
  color: #909399;
  margin: 0;
}
</style>
