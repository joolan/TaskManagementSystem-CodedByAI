<template>
  <div class="menu-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>菜单管理</span>
          <el-button v-permission="'menu:create'" type="primary" @click="handleAddMenu">
            <el-icon><Plus /></el-icon>
            新增菜单
          </el-button>
        </div>
      </template>
      
      <!-- 菜单树 -->
      <el-tree
        :data="menuTree"
        :props="treeProps"
        node-key="id"
        default-expand-all
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <span>
              <el-icon v-if="data.icon">
                <component :is="data.icon" />
              </el-icon>
              <span v-else class="icon-placeholder">•</span>
              {{ data.name }}
              <el-tag v-if="data.status === 0" type="info" size="small" class="hidden-badge">已隐藏</el-tag>
            </span>
            <div class="node-actions">
              <el-button v-permission="'menu:update'" size="small" @click.stop="handleEditMenu(data)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button v-permission="'menu:delete'" size="small" type="danger" @click.stop="handleDeleteMenu(data.id)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </template>
      </el-tree>
    </el-card>

    <!-- 新增/编辑菜单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
    >
      <el-tabs v-model="activeTab">
        <!-- 基本信息标签页 -->
        <el-tab-pane label="基本信息" name="basic">
          <el-form :model="formData" :rules="rules" ref="formRef" label-width="80px">
            <el-form-item label="菜单名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入菜单名称" />
            </el-form-item>
            <el-form-item label="上级菜单" prop="parent_id">
              <el-select
                v-model="formData.parent_id"
                filterable
                clearable
                placeholder="请选择上级菜单（可搜索）"
                style="width: 100%"
              >
                <el-option
                  v-for="menu in flatMenuOptions"
                  :key="menu.id"
                  :label="menu.fullName"
                  :value="menu.id"
                  :disabled="menu.disabled"
                >
                  <span :class="{ 'disabled-option': menu.disabled }">
                    {{ menu.fullName }}
                  </span>
                </el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="路由路径" prop="path">
              <el-input v-model="formData.path" placeholder="请输入路由路径" />
            </el-form-item>
            <el-form-item label="组件路径" prop="component">
              <el-input v-model="formData.component" placeholder="请输入组件路径" />
            </el-form-item>
            <el-form-item label="菜单图标" prop="icon">
              <div class="icon-selector">
                <div class="selected-icon" @click="iconDialogVisible = true">
                  <el-icon v-if="formData.icon" :size="24">
                    <component :is="getIconComponent(formData.icon)" />
                  </el-icon>
                  <span v-else class="no-icon">点击选择图标</span>
                  <span v-if="formData.icon" class="icon-name">{{ formData.icon }}</span>
                </div>
              </div>
            </el-form-item>
            <el-form-item label="排序" prop="order_index">
              <el-input-number v-model="formData.order_index" :min="0" />
            </el-form-item>
            <el-form-item label="菜单类型" prop="type">
              <el-select v-model="formData.type" placeholder="选择菜单类型">
                <el-option label="菜单" value="menu" />
                <el-option label="目录" value="catalog" />
                <el-option label="外链" value="external" />
              </el-select>
            </el-form-item>
            <el-form-item label="外部链接" prop="external_url">
              <el-input v-model="formData.external_url" placeholder="请输入外部链接" />
            </el-form-item>
            <el-form-item label="打开方式" prop="target">
              <el-select v-model="formData.target" placeholder="选择打开方式">
                <el-option label="当前窗口" value="_self" />
                <el-option label="新窗口" value="_blank" />
              </el-select>
            </el-form-item>
            <el-form-item label="状态" prop="status">
              <el-switch v-model="formData.status"  />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 功能权限标签页 - 仅在编辑菜单时显示 -->
        <el-tab-pane v-if="formData.id" label="功能权限" name="permissions">
          <div class="permissions-tab">
            <div class="permissions-header">
              <span>按钮权限列表</span>
              <el-button v-permission="'permission:create'" type="primary" size="small" @click="handleAddPermission">
                <el-icon><Plus /></el-icon>
                新增权限
              </el-button>
            </div>

            <!-- 权限列表 -->
            <el-table :data="menuPermissions" style="width: 100%">
              <el-table-column prop="name" label="权限名称" width="180" />
              <el-table-column prop="code" label="权限编码" width="180" />
              <el-table-column prop="description" label="权限描述" />
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="scope">
                  <el-button v-permission="'permission:update'" size="small" @click="handleEditPermission(scope.row)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button v-permission="'permission:delete'" size="small" type="danger" @click="handleDeletePermission(scope.row.id)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
      
      <!-- 权限编辑对话框 -->
      <el-dialog
        v-model="permissionDialogVisible"
        :title="permissionDialogTitle"
        width="500px"
      >
        <el-form :model="permissionForm" :rules="permissionRules" ref="permissionFormRef" label-width="80px">
          <el-form-item label="权限名称" prop="name">
            <el-input v-model="permissionForm.name" placeholder="请输入权限名称" />
          </el-form-item>
          <el-form-item label="权限编码" prop="code">
            <el-input v-model="permissionForm.code" placeholder="请输入权限编码，如：menu:create" />
          </el-form-item>
          <el-form-item label="权限描述" prop="description">
            <el-input
              v-model="permissionForm.description"
              type="textarea"
              placeholder="请输入权限描述"
              :rows="3"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="permissionDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="handleSubmitPermission">确定</el-button>
          </span>
        </template>
      </el-dialog>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 图标选择对话框 -->
    <el-dialog
      v-model="iconDialogVisible"
      title="选择图标"
      width="700px"
    >
      <div class="icon-search">
        <el-input
          v-model="iconSearchQuery"
          placeholder="搜索图标"
          clearable
          prefix-icon="Search"
        />
      </div>
      <div class="icon-grid">
        <div
          v-for="icon in filteredIcons"
          :key="icon"
          class="icon-item"
          :class="{ active: formData.icon === icon }"
          @click="selectIcon(icon)"
        >
          <el-icon :size="24">
            <component :is="icon" />
          </el-icon>
          <span class="icon-label">{{ icon }}</span>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="iconDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="iconDialogVisible = false">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search } from '@element-plus/icons-vue'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { menuApi, permissionApi } from '../../api'

const dialogVisible = ref(false)
const dialogTitle = ref('新增菜单')
const formRef = ref(null)
const menuTree = ref([])
const allMenuTree = ref([])
const activeTab = ref('basic')
const menuPermissions = ref([])

// 图标选择相关
const iconDialogVisible = ref(false)
const iconSearchQuery = ref('')

// 常用图标列表
const commonIcons = [
  'Menu', 'Home', 'Setting', 'User', 'Document', 'Folder', 'Files', 'Tools',
  'Edit', 'Delete', 'Plus', 'Search', 'Check', 'Close', 'Warning', 'Info',
  'Question', 'Star', 'Bell', 'Message', 'ChatDotRound', 'Calendar', 'Clock',
  'Timer', 'Location', 'Map', 'Phone', 'Email', 'Link', 'Share', 'Download',
  'Upload', 'Picture', 'Video', 'Headset', 'Microphone', 'Camera', 'Printer',
  'Monitor', 'Laptop', 'Mobile', 'Tablet', 'DataLine', 'TrendCharts', 'PieChart',
  'Histogram', 'Rank', 'Sort', 'Filter', 'Refresh', 'Loading', 'Switch',
  'Unlock', 'Lock', 'Key', 'Flag', 'Tag', 'Ticket', 'ShoppingCart', 'Wallet',
  'Money', 'Coin', 'PriceTag', 'Discount', 'Present', 'Box', 'Truck', 'Shop',
  'OfficeBuilding', 'School', 'Hospital', 'Bank', 'Hotel', 'Food', 'IceCream',
  'Coffee', 'MilkTea', 'Chicken', 'Dish', 'ForkSpoon', 'KnifeFork', 'Burger',
  'Goblet', 'Wine', 'Grape', 'Apple', 'Orange', 'Cherry', 'Watermelon', 'Pear',
  'Peach', 'Mango', 'Lemon', 'Banana', 'Strawberry', 'Aim', 'FullScreen',
  'ScaleToOriginal', 'Crop', 'Copy', 'DocumentCopy', 'Paperclip', 'Scissors',
  'Magnet', 'Help', 'WarningFilled', 'CircleCheck', 'CircleClose', 'CirclePlus',
  'Remove', 'ZoomIn', 'ZoomOut', 'Top', 'Bottom', 'Back', 'Right', 'TopRight',
  'TopLeft', 'BottomRight', 'BottomLeft', 'ArrowUp', 'ArrowDown', 'ArrowLeft',
  'ArrowRight', 'DArrowLeft', 'DArrowRight', 'DCaret', 'CaretLeft', 'CaretRight',
  'CaretTop', 'CaretBottom', 'Expand', 'Fold', 'More', 'MoreFilled', 'View',
  'Hide', 'FirstAidKit', 'Suitcase', 'SuitcaseLine', 'Umbrella', 'Sunny',
  'Cloudy', 'PartlyCloudy', 'Lightning', 'Pouring', 'HeavyRain', 'Sunrise',
  'Sunset', 'Moon', 'MoonNight', 'Drizzling', 'Ship', 'Finished', 'SuccessFilled',
  'CircleCheckFilled', 'Promotion', 'Management', 'List', 'Operation', 'Open',
  'TurnOff', 'SetUp', 'Goods', 'GoodsFilled', 'ShoppingBag', 'ShoppingTrolley',
  'SoldOut', 'RemoveFilled', 'CirclePlusFilled', 'Collection', 'CollectionTag',
  'Postcard', 'MostlyCloudy', 'PartlyCloudy', 'Sunrise', 'Sunset', 'FirstAidKit',
  'Reading', 'DataBoard', 'PieChart', 'DataAnalysis', 'Collection', 'Notebook',
  'Memo', 'Calendar', 'AlarmClock', 'Timer', 'Watch', 'Stopwatch', 'Clock',
  'Brush', 'PictureFilled', 'PictureRounded', 'Platform', 'Place', 'Position',
  'OfficeBuilding', 'School', 'TableLamp', 'House', 'NoSmoking', 'Smoking',
  'MagicStick', 'BrushFilled', 'Brush', 'ReadingLamp', 'DataLine', 'CollectionTag',
  'Film', 'CameraFilled', 'VideoCamera', 'VideoCameraFilled', 'PhoneFilled',
  'Coordinate', 'Bicycle', 'Truck', 'Ship', 'Basketball', 'Football', 'Soccer',
  'Baseball', 'Trophy', 'Medal', 'GoldMedal', 'SilverMedal', 'BronzeMedal',
  'Mic', 'Stopwatch', 'AlarmClock', 'Timer', 'Pointer', 'IceTea', 'CoffeeCup',
  'ColdDrink', 'GobletFull', 'GobletSquareFull', 'Chicken', 'Dish', 'IceCreamRound',
  'IceCreamSquare', 'Lollipop', 'PotatoStrips', 'Sugar', 'Bowl', 'MilkTea',
  'Pear', 'Apple', 'Orange', 'Cherry', 'Watermelon', 'Grape', 'Refrigerator',
  'KnifeFork', 'Burger', 'Tableware', 'Sugar', 'Dessert', 'IceCream', 'HotWater',
  'IceTea', 'Coffee', 'Tea', 'Mug', 'Goblet', 'Bottle', 'DishDot', 'Food',
  'ForkSpoon', 'KnifeFork', 'Burger', 'Tableware'
]

// 过滤后的图标列表
const filteredIcons = computed(() => {
  if (!iconSearchQuery.value) {
    return commonIcons
  }
  return commonIcons.filter(icon => 
    icon.toLowerCase().includes(iconSearchQuery.value.toLowerCase())
  )
})

// 获取图标组件
const getIconComponent = (iconName) => {
  return ElementPlusIconsVue[iconName] || null
}

// 选择图标
const selectIcon = (icon) => {
  formData.icon = icon
}

// 扁平化菜单树（用于查找）
const flattenMenuTree = (menus, result = []) => {
  for (const menu of menus) {
    result.push(menu)
    if (menu.children && menu.children.length > 0) {
      flattenMenuTree(menu.children, result)
    }
  }
  return result
}

// 获取菜单深度（从根菜单到当前菜单的层级数）
const getMenuDepth = (menuId, flatMenus) => {
  const menu = flatMenus.find(m => m.id === menuId)
  if (!menu) return 0
  if (!menu.parent_id) return 1
  
  const parentDepth = getMenuDepth(menu.parent_id, flatMenus)
  return parentDepth > 0 ? parentDepth + 1 : 1
}

// 获取菜单的最大子菜单深度
const getMaxChildrenDepth = (menuId, flatMenus, visited = new Set()) => {
  if (visited.has(menuId)) return 0
  visited.add(menuId)
  
  let maxDepth = 0
  for (const menu of flatMenus) {
    if (menu.parent_id === menuId) {
      const childDepth = getMaxChildrenDepth(menu.id, flatMenus, new Set(visited))
      maxDepth = Math.max(maxDepth, childDepth + 1)
    }
  }
  return maxDepth
}

// 扁平化的菜单选项（带禁用状态）
const flatMenuOptions = computed(() => {
  const options = []
  const flatMenus = flattenMenuTree(allMenuTree.value)
  
  // 递归扁平化菜单树，生成完整路径名称
  const flattenMenus = (menus, parentPath = '') => {
    for (const menu of menus) {
      const fullName = parentPath ? `${parentPath} / ${menu.name}` : menu.name
      
      // 判断是否禁用
      let disabled = false
      
      // 获取目标菜单的深度
      const targetDepth = getMenuDepth(menu.id, flatMenus)
      
      if (formData.id) {
        // 编辑模式
        // 1. 不能选择自己作为父菜单
        if (menu.id === formData.id) {
          disabled = true
        }
        // 2. 检查选择后是否会导致超过3级
        else {
          // 获取当前编辑菜单的最大子菜单深度
          const childrenDepth = getMaxChildrenDepth(formData.id, flatMenus)
          // 总深度 = 目标菜单深度 + 1（当前菜单）+ 子菜单深度
          const totalDepth = targetDepth + 1 + childrenDepth
          if (totalDepth > 3) {
            disabled = true
          }
        }
      } else {
        // 新增模式：不能选择三级菜单作为父菜单
        if (targetDepth >= 3) {
          disabled = true
        }
      }
      
      options.push({
        id: menu.id,
        name: menu.name,
        fullName,
        disabled
      })
      
      if (menu.children && menu.children.length > 0) {
        flattenMenus(menu.children, fullName)
      }
    }
  }
  
  flattenMenus(allMenuTree.value)
  return options
})

// 权限编辑对话框
const permissionDialogVisible = ref(false)
const permissionDialogTitle = ref('新增权限')
const permissionFormRef = ref(null)
const currentPermissionId = ref(null)

const formData = reactive({
  name: '',
  parent_id: null,
  path: '',
  component: '',
  icon: '',
  order_index: 0,
  type: 'menu',
  external_url: '',
  target: '_self',
  status: 1
})

const permissionForm = reactive({
  name: '',
  code: '',
  description: ''
})

const permissionRules = {
  name: [{ required: true, message: '请输入权限名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入权限编码', trigger: 'blur' }]
}

const rules = {
  name: [{ required: true, message: '请输入菜单名称', trigger: 'blur' }],
  path: [{ required: true, message: '请输入路由路径', trigger: 'blur' }],
  component: [{ required: false, message: '请输入组件路径', trigger: 'blur' }]
}

const treeProps = {
  children: 'children',
  label: 'name'
}

// 加载菜单数据
const loadMenus = async () => {
  try {
    const response = await menuApi.getAllMenus()
    const allMenus = response.data
    
    // 构建菜单树
    const menuDict = {}
    allMenus.forEach(menu => {
      menuDict[menu.id] = {
        ...menu,
        children: []
      }
    })
    
    // 构建父子关系
    const treeData = []
    allMenus.forEach(menu => {
      if (menu.parent_id === null) {
        treeData.push(menuDict[menu.id])
      } else if (menuDict[menu.parent_id]) {
        menuDict[menu.parent_id].children.push(menuDict[menu.id])
      }
    })
    
    menuTree.value = treeData
  } catch (error) {
    ElMessage.error('加载菜单失败')
  }
}

// 加载上级菜单选项
const loadParentMenuOptions = async () => {
  try {
    // 加载完整的三级菜单树
    const treeResponse = await menuApi.getAllMenuTree()
    allMenuTree.value = treeResponse.data
  } catch (error) {
    ElMessage.error('加载上级菜单选项失败')
  }
}

// 处理新增菜单
const handleAddMenu = async () => {
  dialogTitle.value = '新增菜单'
  // 重置表单（先重置id）
  Object.assign(formData, {
    id: null,
    name: '',
    parent_id: null,
    path: '',
    component: '',
    icon: '',
    order_index: 0,
    type: 'menu',
    external_url: '',
    target: '_self',
    status: true
  })
  // 切换到基本信息tab
  activeTab.value = 'basic'
  // 加载上级菜单选项
  await loadParentMenuOptions()
  dialogVisible.value = true
}

// 处理编辑菜单
const handleEditMenu = async (data) => {
  dialogTitle.value = '编辑菜单'
  try {
    // 先设置id，用于过滤菜单选项
    formData.id = data.id
    
    // 先加载上级菜单选项
    await loadParentMenuOptions()
    
    // 调用接口获取菜单详情，确保数据是最新的
    const response = await menuApi.getMenu(data.id)
    const menuDetail = response.data
    
    // 设置表单数据（parent_id 直接使用后端返回的值）
    Object.assign(formData, {
      name: menuDetail.name || '',
      parent_id: menuDetail.parent_id,
      path: menuDetail.path || '',
      component: menuDetail.component || '',
      icon: menuDetail.icon || '',
      order_index: menuDetail.order_index || 0,
      type: menuDetail.type || 'menu',
      external_url: menuDetail.external_url || '',
      target: menuDetail.target || '_self',
      status: menuDetail.status === 1
    })
    
    // 打开对话框
    dialogVisible.value = true
    
    // 加载菜单的功能权限
    loadMenuPermissions(data.id)
  } catch (error) {
    ElMessage.error('获取菜单详情失败')
  }
}

// 加载菜单的功能权限
const loadMenuPermissions = async (menuId) => {
  try {
    // 调用权限API获取所有权限
    const response = await permissionApi.getPermissions()
    // 过滤出与当前菜单关联的权限
    menuPermissions.value = response.data.filter(permission => permission.menu_id === menuId)
  } catch (error) {
    ElMessage.error('加载权限失败')
  }
}

// 处理新增权限
const handleAddPermission = () => {
  permissionDialogTitle.value = '新增权限'
  currentPermissionId.value = null
  // 重置表单
  Object.assign(permissionForm, {
    name: '',
    code: '',
    description: ''
  })
  permissionDialogVisible.value = true
}

// 处理编辑权限
const handleEditPermission = (permission) => {
  permissionDialogTitle.value = '编辑权限'
  currentPermissionId.value = permission.id
  // 填充表单数据
  Object.assign(permissionForm, {
    name: permission.name,
    code: permission.code,
    description: permission.description
  })
  permissionDialogVisible.value = true
}

// 处理删除权限
const handleDeletePermission = async (permissionId) => {
  try {
    await ElMessageBox.confirm('确定要删除该权限吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await permissionApi.deletePermission(permissionId)
    ElMessage.success('删除成功')
    // 重新加载权限列表
    if (formData.id) {
      loadMenuPermissions(formData.id)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 处理提交权限
const handleSubmitPermission = async () => {
  if (!permissionFormRef.value) return
  
  try {
    await permissionFormRef.value.validate()
    
    const permissionData = {
      ...permissionForm,
      menu_id: formData.id // 关联到当前菜单
    }
    
    if (currentPermissionId.value) {
      // 更新权限
      await permissionApi.updatePermission(currentPermissionId.value, permissionData)
      ElMessage.success('更新成功')
    } else {
      // 新增权限
      await permissionApi.createPermission(permissionData)
      ElMessage.success('新增成功')
    }
    
    permissionDialogVisible.value = false
    // 重新加载权限列表
    if (formData.id) {
      loadMenuPermissions(formData.id)
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('操作失败')
  }
}

// 处理删除菜单
const handleDeleteMenu = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该菜单吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await menuApi.deleteMenu(id)
    ElMessage.success('删除成功')
    loadMenus()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 处理表单提交
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    // 准备提交数据
    const submitData = { ...formData }
    // 处理状态值
    submitData.status = submitData.status ? 1 : 0
    
    if (submitData.id) {
      // 更新菜单
      await menuApi.updateMenu(submitData.id, submitData)
      ElMessage.success('更新成功')
    } else {
      // 新增菜单
      await menuApi.createMenu(submitData)
      ElMessage.success('新增成功')
    }
    
    dialogVisible.value = false
    loadMenus()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  loadMenus()
})
</script>

<style scoped>
.menu-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tree-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.node-actions {
  display: flex;
  gap: 8px;
}

.disabled-option {
  color: #c0c4cc;
  cursor: not-allowed;
}

.icon-placeholder {
  margin-right: 24px;
  color: #ccc;
}

.hidden-badge {
  margin-left: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 功能权限标签页样式 */
.permissions-tab {
  padding: 10px 0;
}

.permissions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eaeaea;
}

.permissions-header span {
  font-size: 16px;
  font-weight: 500;
}

/* 图标选择器样式 */
.icon-selector {
  display: flex;
  align-items: center;
}

.selected-icon {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0px 6px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  transition: border-color 0.2s;
  min-height: 40px;
}

.selected-icon:hover {
  border-color: #409eff;
}

.selected-icon .no-icon {
  color: #909399;
  font-size: 14px;
}

.selected-icon .icon-name {
  color: #606266;
  font-size: 14px;
}

.icon-search {
  margin-bottom: 16px;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
  padding: 8px;
  scrollbar-width: thin;
  scrollbar-color: #dcdfe6 #f5f7fa;
}

.icon-grid::-webkit-scrollbar {
  width: 8px;
}

.icon-grid::-webkit-scrollbar-track {
  background: #f5f7fa;
  border-radius: 4px;
}

.icon-grid::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 4px;
}

.icon-grid::-webkit-scrollbar-thumb:hover {
  background: #c0c4cc;
}

.icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 4px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.icon-item:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.icon-item.active {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.icon-item .icon-label {
  margin-top: 4px;
  font-size: 12px;
  color: #606266;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}
</style>