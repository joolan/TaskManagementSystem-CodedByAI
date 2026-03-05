import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    redirect: '/welcome'
  },
  {
    path: '/welcome',
    name: 'Welcome',
    component: () => import('../views/Welcome.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/board',
    name: 'Board',
    component: () => import('../views/Board.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('../views/Tasks.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/task/:id',
    name: 'TaskDetail',
    component: () => import('../views/TaskDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/task/create',
    name: 'TaskCreate',
    component: () => import('../views/TaskForm.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/task/edit/:id',
    name: 'TaskEdit',
    component: () => import('../views/TaskForm.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/stats',
    name: 'Stats',
    component: () => import('../views/Stats.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('../views/Users.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/role-management',
    name: 'RoleManagementPage',
    component: () => import('../views/system/Roles.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/menu-management',
    name: 'MenuManagementPage',
    component: () => import('../views/system/Menus.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/system-settings',
    name: 'SystemSettings',
    component: () => import('../views/SystemSettings.vue'),
    meta: { requiresAuth: true }
  },
  // 系统管理路由
  {
    path: '/system',
    name: 'System',
    component: () => import('../views/system/Index.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'menus',
        name: 'MenuManagement',
        component: () => import('../views/system/Menus.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'roles',
        name: 'RoleManagement',
        component: () => import('../views/system/Roles.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'permissions',
        name: 'PermissionManagement',
        component: () => import('../views/system/Permissions.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'defects',
        name: 'DefectManagement',
        component: () => import('../views/Defects.vue'),
        meta: { requiresAuth: true }
      }
    ]
  },

  {
    path: '/defects',
    name: 'Defects',
    component: () => import('../views/Defects.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/defect/:id',
    name: 'DefectDetail',
    component: () => import('../views/DefectDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/defect/create',
    name: 'DefectCreate',
    component: () => import('../views/DefectForm.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/defect/edit/:id',
    name: 'DefectEdit',
    component: () => import('../views/DefectForm.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/releases',
    name: 'Releases',
    component: () => import('../views/Releases.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/release/:id',
    name: 'ReleaseDetail',
    component: () => import('../views/ReleaseDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/release/create',
    name: 'ReleaseCreate',
    component: () => import('../views/ReleaseDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/release/edit/:id',
    name: 'ReleaseEdit',
    component: () => import('../views/ReleaseDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/requirements',
    name: 'Requirements',
    component: () => import('../views/Requirements.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/requirement/create',
    name: 'RequirementCreate',
    component: () => import('../views/RequirementForm.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/requirement/edit/:id',
    name: 'RequirementEdit',
    component: () => import('../views/RequirementForm.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/requirement/:id',
    name: 'RequirementDetail',
    component: () => import('../views/RequirementDetail.vue'),
    meta: { requiresAuth: true }
  },
  // 备忘录详情页
  {
    path: '/memo/:id',
    name: 'MemoDetail',
    component: () => import('../views/MemoDetail.vue'),
    meta: { requiresAuth: true }
  },
  // 权限演示页面
  {
    path: '/demo/permission',
    name: 'PermissionDemo',
    component: () => import('../views/PermissionDemo.vue'),
    meta: { requiresAuth: true }
  },
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const token = localStorage.getItem('token')

  if (requiresAuth && !token) {
    // 需要认证但未登录，跳转到登录页
    next('/login')
  } else if (!requiresAuth && token && to.path === '/login') {
    // 已登录但访问登录页，跳转到首页
    next('/board')
  } else {
    // 其他情况正常跳转
    next()
  }
})

export default router
