# 部门开发任务进度看板系统 - Java 后端

一个基于 Spring Boot + MyBatis + MySQL 的后端系统，用于跟踪和管理部门内的开发任务。

## 技术栈

### 后端
- Java 1.8
- Spring Boot 2.7.x
- Spring Security
- MyBatis 2.3.x
- MySQL
- JWT (JSON Web Token)
- Lombok

## 功能特性

### 核心功能
- 用户认证（登录/注册）
- 任务管理（创建/编辑/删除/查询）
- 看板视图（拖拽调整任务状态）
- 任务详情（评论/附件/关注）
- 任务关注（接收状态变更通知）
- 消息中心（任务状态变更/发版消息通知/缺陷消息通知）
- 富文本编辑器（支持图片上传）
- 缺陷管理（创建/编辑/删除/关联发版版本）
- 统计分析（任务状态/用户工作量/项目进度/我的工时/数据概览）
- 用户管理（支持多角色分配）
- 菜单管理（动态菜单配置）
- 角色管理（自定义角色创建与权限分配）
- 发版管理
- 需求管理（创建/编辑/转任务）
- 需求标签管理
- 备忘录管理（创建/编辑/删除/查看）
- 数据导出（任务/发版/需求/缺陷 Excel 导出）
- 数据库备份还原（全量备份/结构校验/还原操作）
- 用户会话管理（多地点登录限制/会话列表/踢出登录）
- 任务工时填报（多用户选择/负数工时/工时累计/工时记录）
- 任务日志记录（工时填报自动记录到任务日志）
- 权限控制（接口级权限校验/角色权限管理/超管权限）
- 高级查询（多条件组合筛选/分页/搜索）

## 项目结构

```
task-board-backend-java/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── taskboard/
│   │   │           └── backend/
│   │   │               ├── controller/     # 控制器
│   │   │               ├── model/          # 数据模型
│   │   │               ├── mapper/         # MyBatis Mapper 接口
│   │   │               ├── security/       # 安全相关
│   │   │               ├── filter/         # 过滤器（请求日志等）
│   │   │               ├── aspect/         # AOP 切面（权限校验）
│   │   │               ├── annotation/     # 自定义注解
│   │   │               └── TaskBoardBackendApplication.java  # 应用入口
│   │   └── resources/
│   │       ├── application.properties      # 应用配置
│   │       └── mapper/                     # MyBatis XML Mapper 文件
│   │           ├── TaskMapper.xml
│   │           ├── UserMapper.xml
│   │           ├── RoleMapper.xml
│   │           ├── PermissionMapper.xml
│   │           ├── MenuMapper.xml
│   │           ├── StatusMapper.xml
│   │           ├── RequirementMapper.xml
│   │           ├── DefectMapper.xml
│   │           ├── ReleaseMapper.xml
│   │           ├── TaskFollowMapper.xml
│   │           ├── ReleaseFollowMapper.xml
│   │           └── ...
│   └── test/
│       └── java/
│           └── com/
│               └── taskboard/
│                   └── backend/
│                       └── TaskBoardBackendApplicationTests.java  # 测试类
├── build.gradle        # Gradle 配置
├── gradlew             # Gradle wrapper 脚本
├── gradlew.bat         # Gradle wrapper 脚本（Windows）
├── README.md           # 项目说明
└── PERMISSIONS_MAPPING.md  # 权限映射文档
```

## 快速开始

### 环境要求
- Java 1.8
- MySQL 5.7+
- Gradle 6.9+

### 数据库配置
1. 创建数据库
```sql
CREATE DATABASE task_board CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
执行/sql/task_board.sql 数据库脚本，恢复测试数据库

2. 修改 `src/main/resources/application.properties` 文件中的数据库配置
```properties
spring.datasource.url=jdbc:mysql://localhost:3306/task_board
spring.datasource.username=root
spring.datasource.password=root
```

### 构建项目
```bash
./gradlew build
```

### 运行项目
```bash
./gradlew bootRun
```

后端服务将在 `http://localhost:8003` 运行。

## 数据访问层说明

本项目使用 **MyBatis** 作为 ORM 框架，采用 XML 映射文件方式配置 SQL 语句。

### Mapper 接口
所有数据访问接口位于 `com.taskboard.backend.mapper` 包下：
- `TaskMapper` - 任务数据访问
- `UserMapper` - 用户数据访问
- `RoleMapper` - 角色数据访问
- `PermissionMapper` - 权限数据访问
- `MenuMapper` - 菜单数据访问
- `StatusMapper` - 状态数据访问
- `RequirementMapper` - 需求数据访问
- `DefectMapper` - 缺陷数据访问
- `ReleaseMapper` - 发版数据访问
- `TaskFollowMapper` - 任务关注数据访问
- `ReleaseFollowMapper` - 发版关注数据访问
- `CommentMapper` - 评论数据访问
- `TaskLogMapper` - 任务日志数据访问
- `MessageMapper` - 消息数据访问
- `MemoMapper` - 备忘录数据访问
- `TagMapper` - 标签数据访问
- `BackupMapper` - 数据库备份数据访问

### XML 映射文件
SQL 语句定义在 `src/main/resources/mapper/` 目录下的 XML 文件中：
- 支持复杂的联表查询
- 支持一对多、多对一关系映射
- 支持动态 SQL
- 启用了下划线转驼峰命名自动映射

### 示例：查询任务列表
```java
// Controller 中调用
@Autowired
private TaskMapper taskMapper;

// 按状态查询任务
List<Task> tasks = taskMapper.findByStatusId(statusId);
```


## API 文档

后端提供了完整的 API 文档，启动后端服务后可以访问：

- Swagger UI: `http://localhost:8003/swagger-ui.html`
- API 文档：`http://localhost:8003/v3/api-docs`

## 部署指南

### 生产环境部署

1. 构建生产版本
```bash
./gradlew build -Pprod
```

2. 运行生产版本
```bash
java -jar build/libs/task-board-backend-0.0.1-SNAPSHOT.jar
```

### 环境变量配置

生产环境部署时，建议通过环境变量配置敏感信息：

- `SPRING_DATASOURCE_URL` - 数据库连接 URL
- `SPRING_DATASOURCE_USERNAME` - 数据库用户名
- `SPRING_DATASOURCE_PASSWORD` - 数据库密码
- `JWT_SECRET` - JWT 密钥（生产环境部署时需要修改）

## 安全配置

1. 生产环境部署时，修改 `application.properties` 文件中的 JWT 密钥：
```properties
jwt.secret=your-secret-key-change-in-production
```

2. 配置 HTTPS：
```properties
server.ssl.key-store=classpath:keystore.p12
server.ssl.key-store-password=password
server.ssl.key-store-type=PKCS12
server.ssl.key-alias=tomcat
```

3. 权限控制：
   - 使用 AOP 切面实现接口级权限校验
   - 通过 `@RequirePermission` 注解标记接口所需权限
   - 支持角色权限管理和用户独立权限分配
   - admin 用户默认拥有所有权限

## 权限管理

系统采用 RBAC（基于角色的访问控制）模型：

### 权限架构
- **用户**：系统使用者，可分配多个角色
- **角色**：权限的集合，可分配给用户
- **菜单权限**：控制用户可访问的菜单项
- **操作权限**：控制用户可执行的接口操作

### 权限注解使用
```java
@GetMapping("/{id}")
@RequirePermission("task:update")
public ResponseEntity<Task> updateTask(@PathVariable Long id, @RequestBody Task task) {
    // 只有拥有 task:update 权限的用户才能访问
}
```

### 默认权限码
- `task:list`, `task:create`, `task:update`, `task:delete`
- `requirement:list`, `requirement:create`, `requirement:update`, `requirement:delete`
- `defect:list`, `defect:create`, `defect:update`, `defect:delete`
- `release:list`, `release:create`, `release:update`, `release:delete`
- `user:list`, `user:create`, `user:update`, `user:delete`
- `role:list`, `role:create`, `role:update`, `role:delete`
- `menu:list`, `menu:create`, `menu:update`, `menu:delete`
- 更多权限码在数据库表 `permissions` 中


## 开发注意事项和常见问题

本文档记录了开发过程中遇到的常见问题和解决方案，供后续开发参考。

### 1. MyBatis 结果映射问题

#### 问题描述

当查询关联表数据时，如果使用了 `resultType` 而不是 `resultMap`，可能导致字段映射失败，特别是下划线命名的数据库字段 (如 `menu_id`) 无法正确映射到驼峰命名的 Java 属性 (如 `menuId`)。

#### 典型案例

**问题代码** (`UserMapper.xml`):
```xml
<!-- 错误：使用 resultType，menu_id 字段映射失败 -->
<select id="findUserExtraPermissions" resultType="com.taskboard.backend.model.Permission">
    SELECT p.*
    FROM permissions p
    INNER JOIN user_permissions up ON p.id = up.permission_id
    WHERE up.user_id = #{userId}
</select>
```

**现象**: `Permission.menuId` 始终返回 `null`

**解决方案**:
```xml
<!-- 正确：使用 resultMap，显式指定字段映射 -->
<select id="findUserExtraPermissions" resultMap="com.taskboard.backend.mapper.PermissionMapper.PermissionResultMap">
    SELECT p.id, p.name, p.code, p.description, p.menu_id
    FROM permissions p
    INNER JOIN user_permissions up ON p.id = up.permission_id
    WHERE up.user_id = #{userId}
</select>
```

**PermissionResultMap 定义** (`PermissionMapper.xml`):
```xml
<resultMap id="PermissionResultMap" type="com.taskboard.backend.model.Permission">
    <id property="id" column="id"/>
    <result property="name" column="name"/>
    <result property="code" column="code"/>
    <result property="description" column="description"/>
    <result property="menuId" column="menu_id"/>  <!-- 关键：下划线转驼峰 -->
</resultMap>
```

#### 最佳实践

1. **优先使用 resultMap**: 特别是查询包含下划线命名字段时
2. **明确列出字段**: 避免使用 `SELECT *`，明确列出需要的字段
3. **跨 Mapper 引用**: 使用完整限定名引用其他 Mapper 的 resultMap
   ```xml
   resultMap="com.taskboard.backend.mapper.PermissionMapper.PermissionResultMap"
   ```

### 2. MyBatis 关联数据加载问题

#### 问题描述

MyBatis 不会自动加载关联对象 (如 User 的 roles 列表)，需要手动查询并设置。

#### 典型案例

**问题代码**:
```java
User user = userMapper.findByUsername(username).orElse(null);
List<Role> roles = user.getRoles(); // 返回 null!
```

**原因**: `findByUsername` 的 resultMap 中没有配置 `<collection>` 来加载 roles 关联

**解决方案**:
```java
// 手动加载用户的角色
List<Role> roles = userMapper.findUserRoles(user.getId());
user.setRoles(roles);

// 现在可以正常使用 roles 了
if (roles != null) {
    // 处理角色相关逻辑
}
```

#### 最佳实践

1. **简单查询**: 使用单独的方法手动加载关联数据
2. **复杂查询**: 在 resultMap 中使用 `<collection>` 或 `<association>` 配置关联加载
3. **性能考虑**: 批量加载关联数据，避免 N+1 查询问题

### 3. 用户菜单权限获取逻辑

1. **四个来源**: 角色菜单、用户额外菜单、角色权限关联菜单、用户额外权限关联菜单
2. **并集处理**: 使用 `Set<Long>` 自动去重
3. **递归父菜单**: 确保菜单树结构完整
4. **状态过滤**: 只返回 `status=1` 的启用菜单

### 4. 调试技巧

#### 添加临时日志

在复杂逻辑中添加调试日志，帮助定位问题

#### 日志输出检查点

1. **数据加载**: 检查关联数据是否正确加载 (如 roles, permissions)
2. **字段映射**: 检查关键字段是否正确映射 (如 menuId)
3. **集合操作**: 检查集合是否正确合并 (如 menuIds)
4. **递归结果**: 检查递归后是否包含所有父级菜单


### 5. 常见错误和解决方案

#### 错误 1: 字段映射失败导致 null

**现象**: Java 对象的某个字段始终为 null

**检查步骤**:
1. 检查 SQL 是否查询了该字段
2. 检查字段名是否符合下划线转驼峰规则
3. 检查是否使用了正确的 resultMap

**解决方案**: 使用 resultMap 显式指定字段映射

#### 错误 2: 关联对象为 null

**现象**: 对象的关联列表 (如 user.getRoles()) 返回 null

**检查步骤**:
1. 检查 resultMap 是否配置了 `<collection>`
2. 检查是否手动加载了关联数据

**解决方案**: 手动调用关联查询方法并设置到对象中

#### 错误 3: 菜单权限不完整

**现象**: 用户菜单缺少某些菜单项

**检查步骤**:
1. 检查是否从所有四个来源收集菜单 ID
2. 检查权限的 menu_id 是否为 null
3. 检查是否递归添加了父级菜单
4. 检查菜单状态过滤条件

**解决方案**: 按照完整流程实现，添加调试日志定位问题

### 6. 开发建议

#### 代码规范

1. **空值检查**: 对可能为 null 的集合和对象进行检查
   ```java
   if (list != null && !list.isEmpty()) {
       // 处理逻辑
   }
   ```

2. **注释说明**: 对复杂逻辑添加详细注释，说明数据来源和处理步骤

#### 性能优化

1. **批量查询**: 一次性加载所有需要的数据，避免多次数据库查询
2. **使用 Map**: 将列表转换为 Map 提高查找效率
   ```java
   Map<Long, Menu> menuMap = new HashMap<>();
   for (Menu menu : allMenus) {
       menuMap.put(menu.getId(), menu);
   }
   ```

3. **避免重复**: 使用 Set 存储 ID 集合，自动去重

#### 测试建议

1. **单元测试**: 对关键方法编写单元测试
2. **集成测试**: 测试完整的业务流程
3. **日志验证**: 开发阶段添加详细日志，验证逻辑正确性

### 7. 接口权限开放说明

某些接口需要让所有登录用户访问 (而非仅管理员),需要进行以下修改:

#### 步骤 1: 移除 @RequirePermission 注解

```java
@GetMapping("/settings")
// @RequirePermission("setting:list")  // 移除此注解
public ResponseEntity<?> getSettings() {
    // ...
}
```

#### 步骤 2: 移除代码中的 admin 检查

```java
@GetMapping("/settings")
public ResponseEntity<?> getSettings() {
    Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
    if (authentication == null || !authentication.isAuthenticated()) {
        return ResponseEntity.status(401).body("Unauthorized");
    }

    // 删除以下 admin 检查代码:
    // String username = authentication.getName();
    // if (!"admin".equals(username)) {
    //     return ResponseEntity.status(403).body("Forbidden: Admin access required");
    // }

    List<SystemSetting> settings = systemSettingMapper.findAll();
    return ResponseEntity.ok(settings);
}
```

#### 权限控制级别

1. **公开接口**: 无需登录即可访问 (如登录接口)
2. **认证接口**: 所有登录用户都可访问 (移除了@RequirePermission 和 admin 检查)
3. **权限接口**: 需要特定权限才能访问 (保留@RequirePermission 注解)
4. **管理员接口**: 仅管理员可访问 (保留 admin 检查逻辑)

### 8. 参考资料

- [MyBatis 官方文档 - Result Maps](https://mybatis.org/mybatis-3/zh/sqlmap-xml.html#Result_Maps)
- [MyBatis 字段映射最佳实践](https://mybatis.org/mybatis-3/zh/sqlmap-xml.html)
- Spring Boot 官方文档
- Python 项目对应接口实现

---

## 更新日志

### 2026-03-05

1. **修复用户菜单权限获取逻辑**
   - 修复 MyBatis 结果映射问题，使用 resultMap 替代 resultType
   - 添加手动加载用户角色逻辑
   - 完善四个来源的菜单权限收集
   - 实现递归添加父级菜单功能

2. **添加开发注意事项文档**
   - 记录 MyBatis 字段映射问题
   - 记录关联数据加载问题
   - 整理用户菜单权限完整实现逻辑
   - 总结常见错误和解决方案
   - 添加接口权限开放说明

---

**维护者**: Task Board Team  
**最后更新**: 2026-03-05
