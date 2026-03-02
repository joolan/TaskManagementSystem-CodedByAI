// 权限控制指令
import { useUserStore } from '../store'

// 检查用户是否有权限
const checkPermission = (permissionCode) => {
  const userStore = useUserStore()
  return userStore.hasPermission(permissionCode)
}

// 权限控制指令
export const permissionDirective = {
  mounted(el, binding) {
    const permissionCode = binding.value
    if (permissionCode && !checkPermission(permissionCode)) {
      el.style.display = 'none'
    }
  },
  updated(el, binding) {
    const permissionCode = binding.value
    if (permissionCode && !checkPermission(permissionCode)) {
      el.style.display = 'none'
    } else {
      el.style.display = ''
    }
  }
}

// 注册指令
export const registerPermissionDirective = (app) => {
  app.directive('permission', permissionDirective)
}