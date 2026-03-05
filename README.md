# 部门开发任务进度看板系统

一个基于 Vue 3 + FastAPI/Java Spring Boot + MySQL 的前后端分离任务看板系统，用于跟踪和管理部门内的开发任务。

## 技术栈

### 前端
- Vue 3 + Vite
- Vue Router 4
- Pinia 2
- Element Plus
- Axios
- Vuedraggable
- ECharts
- WangEditor 5（富文本编辑器）

### 后端（Python 版本）
- Python 3.9+
- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- JWT
- Pandas（数据导出）
- Openpyxl（Excel 文件生成）

### 后端（Java 版本）✨ 新增
- Java 1.8
- Spring Boot 2.7.x
- Spring Security
- MyBatis 2.3.x
- MySQL
- JWT (JSON Web Token)
- Apache POI（Excel 文件生成）
- Lombok

> **说明**: 本项目现已提供 Java Spring Boot 版本的后端实现，功能与 Python 版本完全对应。查看 Java 后端详细文档，请访问 [task-board-backend-java/README.md](task-board-backend-java/README.md)

## 功能特性

### 核心功能
- 用户认证（登录/注册）
- 任务管理（创建/编辑/删除）
- 看板视图（拖拽调整任务状态）
- 任务详情（评论/附件/关注）
- 任务关注（接收状态变更通知）
- 消息中心（任务状态变更/发版消息通知/缺陷消息通知）
- 富文本编辑器（支持图片上传）
- 缺陷管理（创建/编辑/删除/关联发版版本）
- 统计分析（任务状态/用户工作量/项目进度/我的工时）
- 用户管理（支持多角色分配）
- 菜单管理（动态菜单配置）
- 角色管理（自定义角色创建与权限分配）
- 发版管理
- 需求管理（创建/编辑/转任务）
- 需求标签管理
- 备忘录管理（创建/编辑/删除/查看）
- 数据导出（任务/发版/需求）
- 数据库备份还原（全量备份/结构校验/还原操作）
- 用户会话管理（多地点登录限制/会话列表/踢出登录）
- 任务工时填报（多用户选择/负数工时/工时累计/工时记录）
- 任务日志记录（工时填报自动记录到任务日志）
- 权限控制（接口级权限校验/角色权限管理/超管权限）

### 技术特性
- 前后端分离架构
- RESTful API设计
- JWT认证保护
- 响应式布局
- 数据可视化
- 拖拽交互
- 可复用组件设计
- 事件驱动的消息通知系统
- 细粒度权限控制（基于角色和权限编码）
- 接口级权限校验切片
- 自定义滚动条设计
- 动态菜单管理系统
- 多角色分配机制
- 角色外权限分配支持
- RBAC权限模型实现

## 项目结构

```
.
├── task-board-frontend/        # 前端项目
│   ├── src/
│   │   ├── components/         # 组件
│   │   │   └── CustomRichTextEditor.vue  # 富文本编辑器组件
│   │   ├── views/              # 页面
│   │   ├── router/             # 路由
│   │   ├── store/              # 状态管理
│   │   ├── api/                # API 服务
│   │   └── main.js             # 应用入口
│   ├── package.json            # 前端依赖
│   └── vite.config.js          # Vite 配置
├── task-board-backend/         # 后端项目（Python）
│   ├── routes/                 # API 路由
│   │   ├── menus.py            # 菜单管理路由
│   │   ├── roles.py            # 角色管理路由
│   ├── main.py                 # 后端入口
│   ├── db.py                   # 数据库配置
│   ├── schemas.py              # 数据模型
│   ├── auth.py                 # 认证工具（包含权限校验）
│   ├── requirements.txt        # 后端依赖
│   └── generate_requirements.py # 生成测试数据脚本
├── task-board-backend-java/    # 后端项目（Java Spring Boot）✨ 新增
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/
│   │   │   │   └── com/
│   │   │   │       └── taskboard/
│   │   │   │           └── backend/
│   │   │   │               ├── controller/     # 控制器
│   │   │   │               ├── model/          # 数据模型
│   │   │   │               ├── mapper/         # MyBatis Mapper 接口
│   │   │   │               ├── security/       # 安全相关
│   │   │   │               ├── filter/         # 过滤器
│   │   │   │               ├── aspect/         # AOP 切面（权限校验）
│   │   │   │               └── annotation/     # 自定义注解
│   │   │   └── resources/
│   │   │       ├── application.properties      # 应用配置
│   │   │       └── mapper/                     # MyBatis XML Mapper 文件
│   │   └── test/                               # 测试代码
│   ├── build.gradle        # Gradle 配置
│   ├── gradlew             # Gradle wrapper 脚本
│   └── README.md           # Java 后端详细说明
└── README.md                   # 项目说明
```

## 快速开始

### Python 后端启动

1. 进入后端目录
```bash
cd task-board-backend
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 启动后端服务
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

后端服务将在 `http://localhost:8001` 运行。

### Java 后端启动 ✨ 新增

1. 进入 Java 后端目录
```bash
cd task-board-backend-java
```

2. 配置数据库
   - 创建 MySQL 数据库：`CREATE DATABASE task_board CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`
   - 修改 `src/main/resources/application.properties` 中的数据库连接信息

3. 构建项目
```bash
./gradlew build
```

4. 启动后端服务
```bash
./gradlew bootRun
```
或直接运行 jar 包:
```bash
java -jar build/libs/task-board-backend-0.0.1-SNAPSHOT.jar
```

后端服务将在 `http://localhost:8003` 运行。

> **详细文档**: Java 后端的完整启动说明、API 文档和开发指南，请查看 [task-board-backend-java/README.md](task-board-backend-java/README.md)

### 前端启动

1. 进入前端目录
```bash
cd task-board-frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动前端开发服务器
```bash
npm run dev
```

前端服务将在 `http://localhost:3000` 运行。

## 默认账户

系统初始化时会创建以下默认账户：

- **管理员**：
  - 用户名：admin
  - 密码：admin123
  - 角色：admin

- **开发人员**：
  - 用户名：dev
  - 密码：dev123
  - 角色：dev

## API文档

后端提供了完整的API文档，启动后端服务后可以访问：

- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

### 新增API端点

- **任务关注**：
  - `POST /tasks/{task_id}/follow` - 关注任务
  - `DELETE /tasks/{task_id}/follow` - 取消关注任务
  - `GET /tasks/{task_id}/followers` - 获取任务关注者

- **数据导出**：
  - `GET /tasks/export` - 导出任务数据
  - `GET /releases/export` - 导出发版数据
  - `GET /requirements/export` - 导出需求数据

- **需求管理**：
  - `GET /requirements` - 获取需求列表
  - `POST /requirements` - 创建需求
  - `GET /requirements/{id}` - 获取需求详情
  - `PUT /requirements/{id}` - 更新需求
  - `DELETE /requirements/{id}` - 删除需求
  - `POST /requirements/{id}/convert-to-task` - 需求转任务

- **需求标签**：
  - `GET /settings/requirement-tags` - 获取需求标签
  - `POST /settings/requirement-tags` - 创建需求标签
  - `PUT /settings/requirement-tags/{id}` - 更新需求标签
  - `DELETE /settings/requirement-tags/{id}` - 删除需求标签

- **数据库备份还原**：
  - `POST /database/backup` - 备份数据库
  - `POST /database/restore` - 还原数据库
  - `GET /database/backups` - 获取备份列表
  - `DELETE /database/backups/{filename}` - 删除备份文件
  - `POST /database/validate` - 校验备份文件

- **备忘录管理**：
  - `GET /memos` - 获取用户的备忘录列表
  - `POST /memos` - 创建新备忘录
  - `GET /memos/{id}` - 获取备忘录详情
  - `PUT /memos/{id}` - 更新备忘录
  - `DELETE /memos/{id}` - 删除备忘录

- **用户会话管理**：
  - `GET /auth/users/{user_id}/sessions` - 获取用户的所有活跃会话列表
  - `DELETE /auth/sessions/{session_id}` - 撤销指定的用户会话（踢出登录）

- **任务工时管理**：
  - `POST /tasks/{task_id}/hours` - 为任务填报工时（支持多用户）
  - `GET /tasks/{task_id}/hours` - 获取任务的工时统计和记录列表

- **统计分析**：
  - `GET /stats/overview` - 获取数据概览（包含我的工时统计）

- **菜单管理**：
  - `GET /menus` - 获取菜单列表
  - `POST /menus` - 创建菜单
  - `GET /menus/{id}` - 获取菜单详情
  - `PUT /menus/{id}` - 更新菜单
  - `DELETE /menus/{id}` - 删除菜单

- **角色管理**：
  - `GET /roles` - 获取角色列表
  - `POST /roles` - 创建角色
  - `GET /roles/{id}` - 获取角色详情
  - `PUT /roles/{id}` - 更新角色
  - `DELETE /roles/{id}` - 删除角色
  - `GET /roles/{id}/permissions` - 获取角色权限
  - `POST /roles/{id}/permissions` - 分配角色权限

- **缺陷管理**：
  - `GET /defects` - 获取缺陷列表
  - `POST /defects` - 创建缺陷
  - `GET /defects/{id}` - 获取缺陷详情
  - `PUT /defects/{id}` - 更新缺陷
  - `DELETE /defects/{id}` - 删除缺陷

## 项目部署

### 前端构建

1. 进入前端目录
```bash
cd task-board-frontend
```

2. 构建生产版本
```bash
npm run build
```

构建产物将生成在 `dist` 目录中。

### 后端部署

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 使用生产服务器运行
```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

## 数据库说明

系统使用 SQLite 作为数据库，数据文件存储在 `task-board-backend/task_board.db`。

### 数据库表结构

- **users**：用户信息
- **statuses**：任务状态
- **tasks**：任务信息
- **comments**：任务评论
- **attachments**：任务附件
- **task_follows**：任务关注关系
- **messages**：消息通知
- **releases**：发版信息
- **release_tags**：发版标签
- **requirements**：需求信息
- **requirement_tags**：需求标签
- **memos**：备忘录信息
- **user_sessions**：用户会话信息
- **system_settings**：系统设置信息
- **task_hours**：任务工时记录
- **menus**：菜单信息
- **roles**：角色信息
- **permissions**：权限信息
- **user_roles**：用户-角色关联表
- **role_menus**：角色-菜单关联表
- **role_permissions**：角色-权限关联表
- **user_permissions**：用户-权限关联表
- **user_menus**：用户-菜单关联表
- **defects**：缺陷信息表
- **user_messages**：用户消息关联表

### 数据库备份还原

系统提供了完整的数据库备份还原功能，通过系统设置页面进行操作：

#### 备份功能
- **操作位置**：系统设置 → 数据库备份还原
- **备份方式**：点击「备份数据库」按钮，系统会自动创建全量备份
- **备份文件**：存储在 `task-board-backend/backups` 目录
- **文件名格式**：`task_board_backup_YYYYMMDD_HHMMSS.db`（包含数据库名称和备份时间）
- **备份过程**：显示「备份中……」提示，防止用户进行其他操作

#### 还原功能
- **操作位置**：系统设置 → 数据库备份还原
- **还原方式**：点击「还原数据库」按钮，上传备份文件
- **结构校验**：还原前自动校验当前数据库表和字段是否在备份文件中存在
- **安全措施**：还原前自动备份当前数据库，确保数据安全
- **还原过程**：显示「还原中……」动画提示，防止用户进行其他操作

#### 备份管理
- **查看备份**：系统设置页面显示所有备份文件列表
- **删除备份**：支持删除不需要的备份文件
- **备份文件**：保留在本地，建议定期导出备份文件到外部存储

### 注意事项
1. 备份还原操作需要管理员权限
2. 还原操作会覆盖当前数据库，请谨慎操作
3. 备份文件包含完整的数据库信息，请妥善保管
4. 建议在系统升级或重大操作前进行备份
5. 定期备份数据库，防止数据丢失

### 用户会话管理

系统提供了完整的用户会话管理功能，支持多地点登录限制和会话管理：

#### 多地点登录限制
- **配置位置**：系统设置 → 用户账号多地点同时登录数限制
- **默认限制**：2个同时在线会话
- **限制范围**：1-10个同时在线会话
- **自动踢出**：超过限制时，新登录会自动踢出最早的会话
- **实时验证**：每次API请求都会验证会话有效性

#### 会话列表查看
- **操作位置**：用户管理 → 在线会话数
- **查看方式**：点击用户列表中的"在线会话数"按钮
- **会话信息**：
  - 会话序号
  - 登录时间
  - IP地址
  - 用户代理（浏览器信息）
- **权限要求**：仅管理员可查看

#### 踢出登录
- **操作位置**：用户会话列表弹窗
- **踢出方式**：点击"踢出登录"按钮
- **确认提示**：踢出前显示确认对话框
- **实时生效**：踢出后用户立即无法访问系统
- **权限要求**：仅管理员可操作

#### 会话状态管理
- **会话创建**：用户登录时自动创建新会话
- **会话更新**：每次API请求自动更新最后活动时间
- **会话验证**：每次API请求验证会话是否有效
- **会话撤销**：管理员手动踢出或超过限制自动踢出

### 注意事项
1. 会话管理功能需要管理员权限
2. 踢出会话后，用户需要重新登录
3. 建议根据实际需求调整最大会话数限制
4. 会话信息包含IP地址和用户代理，用于安全审计

## 测试数据生成

项目提供了生成测试数据的脚本，用于快速填充需求数据：

1. 进入后端目录
```bash
cd task-board-backend
```

2. 执行脚本
```bash
python generate_requirements.py
```

脚本将在数据库中插入30条需求记录，包含各种状态和标签。

## 前端布局规范

### 1. 全局布局结构

- **布局模式**：采用Element Plus的Container布局组件
- **侧边栏**：固定宽度200px，背景色#001529，包含系统菜单
- **顶部导航栏**：高度60px，白色背景，显示页面标题、消息中心和用户信息
- **主内容区**：自适应宽度，包含页面内容和操作区域
- **响应式设计**：适配不同屏幕尺寸，在小屏幕设备上自动调整布局

### 2. 页面布局规范

#### 2.1 详情页面布局

- **顶部操作栏**：包含返回按钮、页面标题和操作按钮（如编辑、日志查看等）
- **内容组织**：使用el-card组件组织不同功能区域
- **卡片头部**：自定义布局，左侧显示区域标题，右侧显示状态徽章和操作按钮
- **信息展示**：
  - 使用grid布局（task-info-grid）组织信息项
  - 每个信息项包含标签和值
  - 负责人和关注人区域独占整行显示
  - 使用el-tag组件展示多个人物信息

#### 2.2 列表页面布局

- **搜索过滤区域**：顶部固定，使用el-form:inline布局
  - **样式**：背景色#f5f7fa，内边距20px，圆角4px
  - **下拉选择宽度**：角色选择等下拉框设置固定宽度（如150px），避免选择后内容被遮挡
- **数据展示**：使用el-table组件，支持多选、排序
- **表格操作**：固定宽度的操作列，包含编辑、删除等按钮
- **分页控件**：表格下方使用el-pagination，靠右显示

### 3. 组件使用规范

#### 3.1 基础组件

- **表单**：使用el-form，表单项使用el-form-item
- **按钮**：使用el-button，按功能区分类型（primary、danger、warning等）
- **输入控件**：使用el-input、el-select、el-date-picker等
- **标签**：使用el-tag展示状态和分类信息
- **弹窗**：使用el-dialog展示详情和编辑表单
- **时间线**：自定义时间线组件展示任务日志

#### 3.2 自定义组件

- **富文本编辑器**：CustomRichTextEditor组件，基于WangEditor 5
- **消息中心**：自定义消息下拉弹窗，支持未读消息标记
- **任务日志**：自定义时间线样式，区分不同类型的操作

### 4. 样式规范

#### 4.1 色彩方案

- **主色调**：#409EFF（蓝色）
- **辅助色**：
  - 成功：#67C23A
  - 警告：#E6A23C
  - 危险：#F56C6C
  - 信息：#909399
- **状态颜色**：任务状态使用不同颜色标识
- **标签颜色**：支持自定义颜色，默认#60A5FA

#### 4.2 间距规范

- **卡片间距**：20px
- **组件间距**：15px
- **按钮间距**：10px
- **表单项间距**：20px

#### 4.3 字体规范

- **标题**：24px（页面）、18px（卡片）、16px（区域）
- **正文**：14px
- **辅助文本**：12px
- **字体家族**：-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif

#### 4.4 边框和阴影

- **边框**：1px solid #eaeaea
- **卡片阴影**：0 2px 4px rgba(0, 0, 0, 0.1)
- **弹窗阴影**：0 2px 12px 0 rgba(0, 0, 0, 0.1)

### 5. 交互规范

#### 5.1 通用交互

- **消息通知**：使用ElMessage组件显示操作结果
- **加载状态**：使用el-loading或自定义加载状态
- **确认对话框**：危险操作前显示确认对话框
- **下拉菜单**：用户信息、操作选项等使用el-dropdown

#### 5.2 特殊交互

- **任务关注**：点击关注/取消关注按钮，实时更新关注状态
- **评论系统**：支持匿名评论、附件上传、评论置顶
- **消息中心**：点击消息跳转到对应详情页，支持未读消息标记
- **任务日志**：时间线展示，支持查看描述变更差异
- **数据导出**：点击导出按钮，根据查询条件导出数据

### 6. 前端权限控制规范

#### 6.1 权限指令使用

系统提供了 `v-permission` 指令用于控制按钮的显示/隐藏，基于用户拥有的权限进行判断。

**基本用法**：
```vue
<el-button v-permission="'task:create'">创建任务</el-button>
<el-button v-permission="'task:update'">编辑</el-button>
<el-button v-permission="'task:delete'">删除</el-button>
```

**权限指令特点**：
- 管理员用户（username === 'admin'）默认拥有所有权限，不受权限控制影响
- 非管理员用户只有在拥有对应权限码时才能看到按钮
- 无权限时按钮会自动隐藏（display: none），而非禁用

#### 6.2 权限码命名规范

权限码采用 `模块:操作` 的格式，使用小写字母和冒号分隔：

**模块命名**：
- `task` - 任务管理
- `release` - 发版管理
- `requirement` - 需求管理
- `defect` - 缺陷管理
- `user` - 用户管理
- `role` - 角色管理
- `menu` - 菜单管理
- `permission` - 权限管理

**操作命名**：
- `create` - 创建
- `update` - 更新/编辑
- `delete` - 删除
- `list` - 列表查询
- `export` - 导出
- `assign` - 分配（如角色权限分配）
- `convert` - 转换（如需求转任务）
- `hours` - 工时相关操作

**示例权限码**：
- `task:create` - 创建任务
- `task:update` - 编辑任务
- `task:delete` - 删除任务
- `task:export` - 导出任务
- `release:create` - 创建发版
- `requirement:convert` - 需求转任务
- `defect:export` - 导出缺陷

#### 6.3 按钮权限控制实施规范

**列表页面按钮**：
- 新增/创建按钮：添加 `v-permission="'模块:create'"`
- 导出按钮：添加 `v-permission="'模块:export'"`
- 编辑按钮：添加 `v-permission="'模块:update'"`
- 删除按钮：添加 `v-permission="'模块:delete'"`

**详情页面按钮**：
- 编辑按钮：添加 `v-permission="'模块:update'"`
- 删除按钮：添加 `v-permission="'模块:delete'"`
- 特殊操作按钮：根据实际操作添加对应权限码

**示例**：
```vue
<!-- 任务列表页面 -->
<el-button v-permission="'task:export'" type="success" @click="exportTasks">导出</el-button>
<el-button v-permission="'task:create'" type="primary" @click="goToCreateTask">创建任务</el-button>

<!-- 表格操作列 -->
<el-button v-permission="'task:update'" size="small" @click="goToEditTask(scope.row.id)">编辑</el-button>
<el-button v-permission="'task:delete'" size="small" type="danger" @click="handleDeleteTask(scope.row.id)">删除</el-button>

<!-- 任务详情页面 -->
<el-button v-permission="'task:hours'" @click="openAddHourDialog">工时填报</el-button>
<el-button v-permission="'task:update'" type="primary" @click="openEditTaskDialog">编辑任务</el-button>
```

#### 6.4 权限控制实现原理

**前端实现**：
- 使用自定义指令 `v-permission` 实现
- 指令内部调用 `userStore.hasPermission(permissionCode)` 方法
- `hasPermission` 方法检查：
  1. 如果用户是 admin，返回 true
  2. 否则检查用户权限列表中是否包含该权限码

**后端配合**：
- 后端接口使用 `require_permission` 依赖进行权限校验
- 前后端权限码保持一致
- 后端返回 403 状态码时前端显示权限不足提示

#### 6.5 新增功能时的权限控制步骤

1. **定义权限码**：按照 `模块:操作` 格式定义新的权限码
2. **后端接口**：在对应路由上使用 `require_permission("权限码")` 进行权限校验
3. **数据库**：在权限表中插入新的权限记录，**必须设置正确的 `menu_id`**
4. **前端按钮**：在对应按钮上添加 `v-permission="'权限码'"`
5. **角色分配**：在角色管理中为角色分配新权限

#### 6.6 权限与菜单关联规范

**重要提示**：每个权限（特别是按钮级权限）都应该关联到对应的菜单，通过设置 `menu_id` 字段实现。

**关联规则**：
- 权限的 `menu_id` 应该指向该权限所属的功能菜单
- 例如：`task:export` 权限的 `menu_id` 应该指向「任务管理」菜单的ID
- 这有助于在菜单管理中统一查看和管理该菜单下的所有权限

**示例**：
```python
# 权限与菜单的对应关系
permission_menu_mapping = {
    "defect:export": "缺陷管理",      # menu_id = 17
    "task:export": "任务管理",        # menu_id = 13
    "release:export": "发版管理",     # menu_id = 14
    "requirement:export": "需求管理", # menu_id = 15
}
```

**注意事项**：
- 创建权限时必须赋值 `menu_id`，否则在菜单管理的权限列表中无法正确显示
- 如果权限属于系统级功能（如数据库备份），可以设置 `menu_id` 为系统设置菜单的ID

### 7. 代码规范

- **组件命名**：使用PascalCase命名组件
- **变量命名**：使用camelCase命名变量和函数
- **样式命名**：使用kebab-case命名CSS类
- **代码缩进**：使用4个空格缩进
- **注释规范**：关键逻辑添加注释，组件添加说明

### 8. 最佳实践

1. **布局一致性**：保持页面布局的一致性，使用统一的组件和样式
2. **响应式设计**：考虑不同屏幕尺寸的显示效果
3. **性能优化**：
   - 使用v-if和v-show合理控制组件渲染
   - 避免不必要的计算和渲染
   - 使用虚拟滚动处理大量数据
4. **用户体验**：
   - 提供清晰的视觉反馈
   - 简化操作流程
   - 减少页面加载时间
5. **可维护性**：
   - 组件化开发
   - 模块化组织代码
   - 遵循统一的编码规范

## 注意事项

1. 本项目为开发环境示例，生产环境部署时需要：
   - 修改 `SECRET_KEY` 为安全的随机字符串
   - 配置 HTTPS
   - 优化数据库性能
   - 增加日志记录

2. 附件上传功能使用本地文件系统存储，生产环境建议使用云存储服务。

3. 系统默认使用 SQLite 数据库，生产环境建议使用 PostgreSQL 或 MySQL。

4. 富文本编辑器支持图片上传，最大上传大小为5MB。

5. 导出功能使用Pandas和Openpyxl库生成Excel文件，支持根据查询条件导出所有数据。

## 数据导出功能开发规范

### 1. 导出功能概述

系统支持将列表数据导出为Excel文件，导出功能需要前后端配合实现。

### 2. 后端实现规范

#### 2.1 路由定义

**重要**：导出路由必须在动态路由（如 `/{id}`）之前定义，否则会被动态路由拦截。

```python
# ✅ 正确的路由顺序
@router.get("/export")  # 先定义
async def export_data(...)

@router.get("/{item_id}")  # 后定义
async def get_item(item_id: int, ...)

# ❌ 错误的路由顺序 - 会导致 /export 被当作 item_id 解析
@router.get("/{item_id}")
async def get_item(item_id: int, ...)

@router.get("/export")
async def export_data(...)
```

#### 2.2 导出接口实现

```python
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
import io

@router.get("/export")
async def export_items(
    # 查询参数
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    # 数据库和权限
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("module:export"))
):
    """Export items to Excel"""
    # 1. 构建查询
    query = db.query(Model)
    if status:
        query = query.filter(Model.status == status)
    
    # 2. 获取数据（不分页）
    items = query.all()
    
    # 3. 准备导出数据
    data = []
    for item in items:
        data.append({
            "字段1": item.field1,
            "字段2": item.field2,
        })
    
    # 4. 创建DataFrame
    df = pd.DataFrame(data)
    
    # 5. 生成Excel文件
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='数据列表', index=False)
    output.seek(0)
    
    # 6. 返回流式响应
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
    )
```

#### 2.3 权限控制

导出接口必须添加权限校验：

```python
current_user: User = Depends(require_permission("module:export"))
```

### 3. 前端实现规范

#### 3.1 使用通用导出工具

前端使用 `src/utils/exportFile.js` 提供的工具函数实现导出功能：

```javascript
import { exportFile, getFileNameFromResponse } from '../utils/exportFile'

const exportLoading = ref(false)

const exportData = async () => {
  if (exportLoading.value) return // 防止重复点击
  
  exportLoading.value = true
  try {
    // 1. 构建查询参数
    const params = {}
    if (filterForm.status) params.status = filterForm.status
    
    // 2. 发送请求
    const response = await api.get('/module/export', {
      params,
      responseType: 'blob'
    })
    
    // 3. 获取文件名
    const fileName = getFileNameFromResponse(response, 'default_export.xlsx')
    
    // 4. 导出文件（支持用户选择保存位置）
    const success = await exportFile(response.data, fileName)
    
    if (success) {
      ElMessage.success('导出成功')
    }
  } catch (error) {
    ElMessage.error('导出失败，请重试')
  } finally {
    exportLoading.value = false
  }
}
```

#### 3.2 按钮实现

```vue
<el-button 
  v-permission="'module:export'" 
  type="success" 
  @click="exportData"
  :loading="exportLoading"
>
  导出
</el-button>
```

### 4. 导出工具函数说明

#### 4.1 exportFile

```javascript
export async function exportFile(
  blob,              // 文件内容 Blob
  defaultFileName,   // 默认文件名
  fileType = 'xlsx', // 文件扩展名
  mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)
```

**功能**：
- 支持浏览器：弹出保存对话框让用户选择保存位置（使用 File System Access API）
- 不支持浏览器：自动下载到默认下载位置

**浏览器兼容性**：
- Chrome 86+ / Edge 86+: ✅ 支持选择保存位置
- Firefox / Safari: ❌ 自动下载到默认位置

#### 4.2 getFileNameFromResponse

```javascript
export function getFileNameFromResponse(response, defaultName)
```

从响应头 `Content-Disposition` 中提取文件名，如果没有则使用默认名称。

### 5. 完整开发流程

1. **后端开发**
   - 添加导出路由（注意路由顺序）
   - 实现导出逻辑
   - 添加权限校验
   - 添加权限到数据库

2. **前端开发**
   - 添加导出按钮（带权限控制和 loading 状态）
   - 实现导出函数
   - 使用通用导出工具

3. **权限配置**
   - 在权限表中添加 `module:export` 权限
   - 设置正确的 `menu_id`
   - 在角色管理中分配权限

### 6. 注意事项

1. **路由顺序**：导出路由必须在动态路由之前定义
2. **权限控制**：前后端都要进行权限校验
3. **加载状态**：导出按钮需要添加 loading 状态防止重复点击
4. **文件命名**：后端返回的文件名应包含时间戳，避免重复
5. **数据量**：导出功能不分页，注意大数据量时的性能问题

## 许可证

MIT

> 📋 详细更新日志请查看 [CHANGELOG.md](./CHANGELOG.md)
