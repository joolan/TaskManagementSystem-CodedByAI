<template>
  <!-- 菜单列表 -->
  <template v-for="menu in menuList" :key="menu.id">
    <!-- 有子菜单的菜单项 -->
    <el-sub-menu v-if="menu.children && menu.children.length > 0" :index="menu.path || `menu-${menu.id}`">
      <template #title>
        <el-icon v-if="menu.icon">
          <component :is="menu.icon" />
        </el-icon>
        <span v-else class="icon-placeholder">•</span>
        <span>{{ menu.name }}</span>
      </template>
      
      <!-- 递归渲染子菜单 -->
      <template v-for="child in menu.children" :key="child.id">
        <!-- 子菜单：有子菜单 -->
        <el-sub-menu v-if="child.children && child.children.length > 0" :index="child.path || `menu-${child.id}`">
          <template #title>
            <el-icon v-if="child.icon">
              <component :is="child.icon" />
            </el-icon>
            <span v-else class="icon-placeholder">•</span>
            <span>{{ child.name }}</span>
          </template>
          
          <!-- 渲染三级菜单 -->
          <el-menu-item
            v-for="grandchild in child.children"
            :key="grandchild.id"
            :index="grandchild.path || `menu-${grandchild.id}`"
          >
            <el-icon v-if="grandchild.icon">
              <component :is="grandchild.icon" />
            </el-icon>
            <template #title>{{ grandchild.name }}</template>
          </el-menu-item>
        </el-sub-menu>
        
        <!-- 子菜单：无子菜单 -->
        <el-menu-item v-else :index="child.path || `menu-${child.id}`">
          <el-icon v-if="child.icon">
            <component :is="child.icon" />
          </el-icon>
          <template #title>{{ child.name }}</template>
        </el-menu-item>
      </template>
    </el-sub-menu>
    
    <!-- 无子菜单的菜单项 -->
    <el-menu-item v-else :index="menu.path || `menu-${menu.id}`">
      <el-icon v-if="menu.icon">
        <component :is="menu.icon" />
      </el-icon>
      <template #title>{{ menu.name }}</template>
    </el-menu-item>
  </template>
</template>

<script setup>
import { computed, defineProps } from 'vue'

// 定义组件属性
const props = defineProps({
  // 菜单数据列表
  menus: {
    type: Array,
    default: () => []
  }
})

// 计算菜单列表
const menuList = computed(() => {
  return props.menus || []
})
</script>

<style scoped>
.icon-placeholder {
  margin-right: 10px;
  opacity: 0.6;
}
</style>