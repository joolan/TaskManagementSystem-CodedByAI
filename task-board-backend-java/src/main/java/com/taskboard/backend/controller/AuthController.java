package com.taskboard.backend.controller;

import com.taskboard.backend.annotation.RequirePermission;
import com.taskboard.backend.aspect.PermissionAspect;
import com.taskboard.backend.mapper.PermissionMapper;
import com.taskboard.backend.mapper.RoleMapper;
import com.taskboard.backend.mapper.UserMapper;
import com.taskboard.backend.mapper.MenuMapper;
import com.taskboard.backend.mapper.UserSessionMapper;
import com.taskboard.backend.model.Menu;
import com.taskboard.backend.model.Permission;
import com.taskboard.backend.model.Role;
import com.taskboard.backend.model.User;
import com.taskboard.backend.model.UserSession;
import com.taskboard.backend.security.JwtUtils;
import com.taskboard.backend.security.UserDetailsServiceImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private UserDetailsServiceImpl userDetailsService;

    @Autowired
    private JwtUtils jwtUtils;

    @Autowired
    private UserMapper userMapper;

    @Autowired
    private RoleMapper roleMapper;

    @Autowired
    private PermissionMapper permissionMapper;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private UserSessionMapper userSessionMapper;

    @Autowired
    private HttpServletRequest request;

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest loginRequest) {
        // 查找用户信息
        User user = userMapper.findByUsername(loginRequest.getUsername()).orElse(null);
        
        // 获取 IP 地址和用户代理
        String ipAddress = getClientIp();
        String userAgent = request.getHeader("User-Agent");
        
        // 用户不存在
        if (user == null) {
            Map<String, String> response = new HashMap<>();
            response.put("detail", "Incorrect username or password");
            return ResponseEntity.status(401).body(response);
        }
        
        // 检查用户是否被锁定
        if (user.getLockedUntil() != null) {
            // 如果锁定时间已过，解锁用户
            if (user.getLockedUntil().before(new java.util.Date())) {
                user.setLockedUntil(null);
                user.setFailedLoginAttempts(0);
                userMapper.update(user);
            } else {
                // 用户仍被锁定
                Map<String, String> response = new HashMap<>();
                response.put("detail", "Account is locked until " + 
                        new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss")
                            .format(user.getLockedUntil()));
                return ResponseEntity.status(423).body(response);
            }
        }
        
        // 验证密码
        try {
            Authentication authentication = authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(loginRequest.getUsername(), loginRequest.getPassword())
            );
            SecurityContextHolder.getContext().setAuthentication(authentication);
        } catch (Exception e) {
            // 密码验证失败，增加失败次数
            user.setFailedLoginAttempts(user.getFailedLoginAttempts() + 1);
            
            // 检查是否需要锁定 (失败 10 次锁定 30 小时)
            if (user.getFailedLoginAttempts() >= 10) {
                java.util.Calendar calendar = java.util.Calendar.getInstance();
                calendar.add(java.util.Calendar.HOUR, 30);
                user.setLockedUntil(calendar.getTime());
                userMapper.update(user);
                
                Map<String, String> response = new HashMap<>();
                response.put("detail", "Account locked due to too many failed login attempts. Please contact admin.");
                return ResponseEntity.status(423).body(response);
            } else {
                // 更新失败次数
                userMapper.update(user);
                
                // 计算剩余尝试次数
                int remainingAttempts = 10 - user.getFailedLoginAttempts();
                Map<String, String> response = new HashMap<>();
                response.put("detail", "Incorrect username or password. " + 
                        remainingAttempts + " attempts remaining.");
                return ResponseEntity.status(401).body(response);
            }
        }
        
        // 登录成功，重置失败次数和锁定状态
        user.setFailedLoginAttempts(0);
        user.setLockedUntil(null);
        user.setLastLoginAt(new java.util.Date());
        userMapper.update(user);
        
        // 生成 JWT token
        UserDetails userDetails = (UserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        String jwt = jwtUtils.generateToken(userDetails);
        
        // 创建用户会话
        UserSession session = new UserSession();
        session.setUserId(user.getId());
        session.setToken(jwt);
        session.setIpAddress(ipAddress);
        session.setUserAgent(userAgent);
        userSessionMapper.insert(session);
        
        // 构建响应数据 (匹配 Python 接口返回格式)
        Map<String, Object> response = new HashMap<>();
        response.put("id", user.getId());
        response.put("username", user.getUsername());
        response.put("name", user.getName());
        response.put("email", user.getEmail());
        response.put("created_at", user.getCreatedAt());
        response.put("last_login_at", user.getLastLoginAt());
        response.put("token", jwt);
        
        return ResponseEntity.ok(response);
    }

    private String getClientIp() {
        String ip = request.getHeader("X-Forwarded-For");
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("X-Real-IP");
        }
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("Remote-Addr");
        }
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getRemoteAddr();
        }
        return ip;
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody RegisterRequest registerRequest) {
        if (userMapper.findByUsername(registerRequest.getUsername()).isPresent()) {
            return ResponseEntity.badRequest().body("Username already exists");
        }

        if (userMapper.findByEmail(registerRequest.getEmail()).isPresent()) {
            return ResponseEntity.badRequest().body("Email already exists");
        }

        User user = new User();
        user.setUsername(registerRequest.getUsername());
        user.setPassword(passwordEncoder.encode(registerRequest.getPassword()));
        user.setName(registerRequest.getName());
        user.setEmail(registerRequest.getEmail());

        userMapper.insert(user);

        // 生成 token
        UserDetails userDetails = userDetailsService.loadUserByUsername(user.getUsername());
        String jwt = jwtUtils.generateToken(userDetails);

        // 构建响应数据
        Map<String, Object> response = new HashMap<>();
        response.put("id", user.getId());
        response.put("username", user.getUsername());
        response.put("name", user.getName());
        response.put("email", user.getEmail());
        response.put("token", jwt);

        return ResponseEntity.ok(response);
    }

    @GetMapping("/me")
    public ResponseEntity<?> getCurrentUser() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User user = userMapper.findByUsername(username).orElse(null);
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        return ResponseEntity.ok(user);
    }

    @PostMapping("/logout")
    public ResponseEntity<?> logout() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User user = userMapper.findByUsername(username).orElse(null);
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        // 从请求头获取 token
        String token = getTokenFromRequest();
        if (token != null) {
            // 删除对应的会话记录
            UserSession session = userSessionMapper.findByToken(token);
            if (session != null) {
                userSessionMapper.delete(session.getId());
            }
        }

        Map<String, String> response = new HashMap<>();
        response.put("detail", "Logout successful");
        return ResponseEntity.ok(response);
    }

    private String getTokenFromRequest() {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }

    @GetMapping("/me/roles")
    public ResponseEntity<?> getCurrentUserRoles() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User user = userMapper.findByUsername(username).orElse(null);
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }
        
        List<Role> roles;
        // 如果用户是 admin，返回所有角色
        if ("admin".equals(username)) {
            roles = roleMapper.findAll();
        } else {
            // 普通用户返回分配的角色
            roles = roleMapper.findByUserId(user.getId());
        }
        
        // 构建响应数据
        List<Map<String, Object>> result = new ArrayList<>();
        for (Role role : roles) {
            Map<String, Object> roleMap = new HashMap<>();
            roleMap.put("id", role.getId());
            roleMap.put("name", role.getName());
            roleMap.put("description", role.getDescription());
            result.add(roleMap);
        }
        
        return ResponseEntity.ok(result);
    }

    @Autowired
    private MenuMapper menuMapper;
    
    @Autowired
    private javax.sql.DataSource dataSource;

    @GetMapping("/test/password")
    public ResponseEntity<?> testPassword() {
        String rawPassword = "admin123";
        String encodedPassword = passwordEncoder.encode(rawPassword);
        Map<String, String> result = new HashMap<>();
        result.put("raw_password", rawPassword);
        result.put("encoded_password", encodedPassword);
        result.put("matches", String.valueOf(passwordEncoder.matches(rawPassword, encodedPassword)));
        return ResponseEntity.ok(result);
    }

    @GetMapping("/check/admin")
    public ResponseEntity<?> checkAdminUser() {
        try {
            // 使用 Mapper 查询 admin 用户
            User admin = userMapper.findByUsername("admin").orElse(null);
            
            if (admin == null) {
                return ResponseEntity.status(404).body("Admin user not found");
            }
            
            // 查询 admin 用户的角色
            List<Role> roles = roleMapper.findByUserId(admin.getId());
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("admin_id", admin.getId());
            result.put("admin_username", admin.getUsername());
            result.put("admin_name", admin.getName());
            result.put("admin_email", admin.getEmail());
            result.put("roles_count", roles.size());
            result.put("roles", roles);
            result.put("message", roles.size() > 0 ? "Admin user found with roles" : "Admin user found but no roles assigned");
            
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            e.printStackTrace();
            Map<String, String> error = new HashMap<>();
            error.put("error", e.getMessage());
            error.put("type", e.getClass().getName());
            return ResponseEntity.status(500).body(error);
        }
    }

    @PostMapping("/fix/admin")
    public ResponseEntity<?> fixAdminUser() {
        try {
            java.sql.Connection conn = dataSource.getConnection();
            java.sql.Statement stmt = conn.createStatement();
            
            // 查询 admin 用户
            java.sql.ResultSet rs = stmt.executeQuery("SELECT id, username, name, email, password FROM users WHERE username = 'admin'");
            Map<String, Object> adminInfo = new HashMap<>();
            if (rs.next()) {
                adminInfo.put("id", rs.getInt("id"));
                adminInfo.put("username", rs.getString("username"));
                adminInfo.put("name", rs.getString("name"));
                adminInfo.put("email", rs.getString("email"));
                adminInfo.put("password", rs.getString("password").substring(0, 20) + "...");
            } else {
                return ResponseEntity.status(404).body("Admin user not found");
            }
            rs.close();
            
            // 查询 admin 用户的角色
            java.sql.ResultSet rs2 = stmt.executeQuery("SELECT r.name as role_name, r.code as role_code FROM roles r INNER JOIN user_roles ur ON r.id = ur.role_id WHERE ur.user_id = 1");
            List<Map<String, String>> roles = new ArrayList<>();
            while (rs2.next()) {
                Map<String, String> role = new HashMap<>();
                role.put("role_name", rs2.getString("role_name"));
                role.put("role_code", rs2.getString("role_code"));
                roles.add(role);
            }
            rs2.close();
            
            stmt.close();
            conn.close();
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("admin_info", adminInfo);
            result.put("admin_roles", roles);
            result.put("message", roles.size() > 0 ? "Admin user found with roles" : "Admin user found but no roles assigned");
            
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            e.printStackTrace();
            Map<String, String> error = new HashMap<>();
            error.put("error", e.getMessage());
            error.put("type", e.getClass().getName());
            return ResponseEntity.status(500).body(error);
        }
    }

    @GetMapping("/me/permissions")
    public ResponseEntity<?> getCurrentUserPermissions() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User user = userMapper.findByUsername(username).orElse(null);
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }
        
        // 如果用户是 admin，返回所有权限
        if ("admin".equals(username)) {
            List<Permission> allPermissions = permissionMapper.findAll();
            return ResponseEntity.ok(allPermissions);
        }
        
        // 普通用户返回分配的操作权限
        List<Permission> permissions = permissionMapper.findByUserId(user.getId());
        return ResponseEntity.ok(permissions);
    }

    @GetMapping("/users-basic")
    public ResponseEntity<?> getUsersBasic() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        List<User> users = userMapper.findAll();
        List<Map<String, Object>> result = new ArrayList<>();
        for (User user : users) {
            Map<String, Object> userMap = new HashMap<>();
            userMap.put("id", user.getId());
            userMap.put("username", user.getUsername());
            userMap.put("name", user.getName());
            result.add(userMap);
        }
        return ResponseEntity.ok(result);
    }

    @GetMapping("/users")
    @RequirePermission("user:list")
    public ResponseEntity<?> getUsers(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer page_size,
            @RequestParam(required = false) String username,
            @RequestParam(required = false) String name,
            @RequestParam(required = false) Long role_id
    ) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        List<User> allUsers = userMapper.findAll();
        
        // 过滤用户
        List<User> filteredUsers = new ArrayList<>();
        for (User user : allUsers) {
            boolean matches = true;
            
            if (username != null && !username.isEmpty()) {
                if (!user.getUsername().toLowerCase().contains(username.toLowerCase())) {
                    matches = false;
                }
            }
            
            if (name != null && !name.isEmpty()) {
                if (!user.getName().toLowerCase().contains(name.toLowerCase())) {
                    matches = false;
                }
            }
            
            if (role_id != null) {
                List<Role> userRoles = userMapper.findUserRoles(user.getId());
                boolean hasRole = false;
                for (Role role : userRoles) {
                    if (role.getId().equals(role_id)) {
                        hasRole = true;
                        break;
                    }
                }
                if (!hasRole) {
                    matches = false;
                }
            }
            
            if (matches) {
                filteredUsers.add(user);
            }
        }

        // 分页处理
        int total = filteredUsers.size();
        int fromIndex = (page - 1) * page_size;
        int toIndex = Math.min(fromIndex + page_size, total);
        
        List<User> pagedUsers;
        if (fromIndex < total) {
            pagedUsers = filteredUsers.subList(fromIndex, toIndex);
        } else {
            pagedUsers = new ArrayList<>();
        }

        // 构建响应数据
        List<Map<String, Object>> result = new ArrayList<>();
        for (User user : pagedUsers) {
            Map<String, Object> userMap = new HashMap<>();
            userMap.put("id", user.getId());
            userMap.put("username", user.getUsername());
            userMap.put("name", user.getName());
            userMap.put("email", user.getEmail());
            userMap.put("created_at", user.getCreatedAt());
            userMap.put("last_login_at", user.getLastLoginAt());
            userMap.put("failed_login_attempts", user.getFailedLoginAttempts());
            userMap.put("locked_until", user.getLockedUntil());
            
            // 获取用户角色
            List<Role> userRoles = userMapper.findUserRoles(user.getId());
            List<Map<String, Object>> rolesList = new ArrayList<>();
            for (Role role : userRoles) {
                Map<String, Object> roleMap = new HashMap<>();
                roleMap.put("id", role.getId());
                roleMap.put("name", role.getName());
                roleMap.put("description", role.getDescription());
                roleMap.put("status", role.getStatus());
                roleMap.put("created_at", role.getCreatedAt());
                roleMap.put("updated_at", role.getUpdatedAt());
                rolesList.add(roleMap);
            }
            userMap.put("roles", rolesList);
            
            // 获取活跃会话数
            int sessionCount = userMapper.countUserSessions(user.getId());
            userMap.put("session_count", sessionCount);
            
            result.add(userMap);
        }

        Map<String, Object> response = new HashMap<>();
        response.put("items", result);
        response.put("total", total);
        response.put("page", page);
        response.put("page_size", page_size);

        return ResponseEntity.ok(response);
    }

    @GetMapping("/users/{user_id}/menus")
    public ResponseEntity<?> getUserMenus(@PathVariable Long user_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        User user = userMapper.findById(user_id);
        if (user == null) {
            return ResponseEntity.notFound().build();
        }

        // Prevent editing admin user
        if ("admin".equals(user.getUsername())) {
            return ResponseEntity.status(403).body("Cannot edit admin user");
        }

        List<Menu> menus = userMapper.findUserExtraMenus(user_id);
        List<Long> menuIds = new ArrayList<>();
        for (Menu menu : menus) {
            menuIds.add(menu.getId());
        }
        
        return ResponseEntity.ok(menuIds);
    }

    @PostMapping("/users/{user_id}/menus")
    @RequirePermission("user:assign_menus")
    public ResponseEntity<?> assignUserMenus(@PathVariable Long user_id, @RequestBody List<Long> menu_ids) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        User user = userMapper.findById(user_id);
        if (user == null) {
            return ResponseEntity.notFound().build();
        }

        // Prevent editing admin user
        if ("admin".equals(user.getUsername())) {
            return ResponseEntity.status(403).body("Cannot edit admin user");
        }

        // Clear existing extra menus
        userMapper.deleteUserMenus(user_id);

        // Assign new menus
        if (menu_ids != null) {
            for (Long menuId : menu_ids) {
                Menu menu = menuMapper.findById(menuId);
                if (menu != null) {
                    userMapper.insertUserMenu(user_id, menuId);
                }
            }
        }

        Map<String, String> response = new HashMap<>();
        response.put("detail", "Extra menus assigned successfully");
        return ResponseEntity.ok(response);
    }

    @GetMapping("/users/{user_id}/permissions")
    public ResponseEntity<?> getUserPermissions(@PathVariable Long user_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        User user = userMapper.findById(user_id);
        if (user == null) {
            return ResponseEntity.notFound().build();
        }

        // Prevent editing admin user
        if ("admin".equals(user.getUsername())) {
            return ResponseEntity.status(403).body("Cannot edit admin user");
        }

        List<Permission> permissions = userMapper.findUserExtraPermissions(user_id);
        List<Long> permissionIds = new ArrayList<>();
        for (Permission permission : permissions) {
            permissionIds.add(permission.getId());
        }
        
        return ResponseEntity.ok(permissionIds);
    }

    @PostMapping("/users/{user_id}/permissions")
    @RequirePermission("user:assign_permissions")
    public ResponseEntity<?> assignUserPermissions(@PathVariable Long user_id, @RequestBody List<Long> permission_ids) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        User user = userMapper.findById(user_id);
        if (user == null) {
            return ResponseEntity.notFound().build();
        }

        // Prevent editing admin user
        if ("admin".equals(user.getUsername())) {
            return ResponseEntity.status(403).body("Cannot edit admin user");
        }

        // Clear existing extra permissions
        userMapper.deleteUserPermissions(user_id);

        // Assign new permissions
        if (permission_ids != null) {
            for (Long permissionId : permission_ids) {
                Permission permission = permissionMapper.findById(permissionId);
                if (permission != null) {
                    userMapper.insertUserPermission(user_id, permissionId);
                }
            }
        }

        Map<String, String> response = new HashMap<>();
        response.put("detail", "Extra permissions assigned successfully");
        return ResponseEntity.ok(response);
    }

    @PostMapping("/users")
    @RequirePermission("user:create")
    public ResponseEntity<?> createUser(@RequestBody CreateUserRequest createRequest) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        // Check if username already exists
        Optional<User> existingUser = userMapper.findByUsername(createRequest.getUsername());
        if (existingUser.isPresent()) {
            return ResponseEntity.badRequest().body("Username already registered");
        }

        // Check if email already exists
        Optional<User> existingEmail = userMapper.findByEmail(createRequest.getEmail());
        if (existingEmail.isPresent()) {
            return ResponseEntity.badRequest().body("Email already registered");
        }

        // Check if name already exists
        List<User> allUsers = userMapper.findAll();
        for (User user : allUsers) {
            if (user.getName() != null && user.getName().equals(createRequest.getName())) {
                return ResponseEntity.badRequest().body("Name already exists");
            }
        }

        // Create new user
        User newUser = new User();
        newUser.setUsername(createRequest.getUsername());
        newUser.setPassword(passwordEncoder.encode(createRequest.getPassword()));
        newUser.setName(createRequest.getName());
        newUser.setEmail(createRequest.getEmail());

        userMapper.insert(newUser);

        // Build response
        Map<String, Object> response = new HashMap<>();
        response.put("id", newUser.getId());
        response.put("username", newUser.getUsername());
        response.put("name", newUser.getName());
        response.put("email", newUser.getEmail());
        response.put("created_at", newUser.getCreatedAt());
        response.put("last_login_at", newUser.getLastLoginAt());

        return ResponseEntity.ok(response);
    }

    @PutMapping("/users/{user_id}/password")
    public ResponseEntity<?> updateUserPassword(@PathVariable Long user_id, @RequestBody Map<String, String> passwordData) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        User user = userMapper.findById(user_id);
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        String password = passwordData.get("password");
        if (password == null || password.isEmpty()) {
            return ResponseEntity.badRequest().body("Password is required");
        }

        // Update password
        user.setPassword(passwordEncoder.encode(password));
        userMapper.update(user);

        Map<String, String> response = new HashMap<>();
        response.put("detail", "Password updated successfully");
        return ResponseEntity.ok(response);
    }

    @GetMapping("/users/{user_id}/sessions")
    public ResponseEntity<?> getUserSessions(@PathVariable Long user_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        User user = userMapper.findById(user_id);
        if (user == null) {
            return ResponseEntity.notFound().build();
        }

        // Get active sessions for user
        List<UserSession> sessions = userSessionMapper.findActiveByUserId(user_id);
        
        // Build response
        List<Map<String, Object>> result = new ArrayList<>();
        for (UserSession session : sessions) {
            Map<String, Object> sessionMap = new HashMap<>();
            sessionMap.put("id", session.getId());
            sessionMap.put("user_id", session.getUserId());
            sessionMap.put("ip_address", session.getIpAddress());
            sessionMap.put("user_agent", session.getUserAgent());
            sessionMap.put("login_at", session.getLoginAt());
            sessionMap.put("last_activity_at", session.getLastActivityAt());
            sessionMap.put("is_active", session.getIsActive());
            result.add(sessionMap);
        }

        return ResponseEntity.ok(result);
    }

    @DeleteMapping("/sessions/{session_id}")
    @RequirePermission("user:revoke_session")
    public ResponseEntity<?> revokeSession(@PathVariable Long session_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        UserSession session = userSessionMapper.findById(session_id);
        if (session == null) {
            return ResponseEntity.notFound().build();
        }

        // Delete the session
        userSessionMapper.delete(session_id);

        Map<String, String> response = new HashMap<>();
        response.put("detail", "Session revoked successfully");
        return ResponseEntity.ok(response);
    }

    @PostMapping("/users/{user_id}/roles")
    public ResponseEntity<?> assignUserRoles(@PathVariable Long user_id, @RequestBody List<Long> role_ids) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        User user = userMapper.findById(user_id);
        if (user == null) {
            return ResponseEntity.notFound().build();
        }

        // Prevent editing admin user
        if ("admin".equals(user.getUsername())) {
            return ResponseEntity.status(403).body("Cannot edit admin user");
        }

        // Clear existing roles
        userMapper.deleteUserRoles(user_id);

        // Assign new roles
        if (role_ids != null) {
            for (Long roleId : role_ids) {
                Role role = roleMapper.findById(roleId);
                if (role != null) {
                    userMapper.insertUserRole(user_id, roleId);
                }
            }
        }

        Map<String, String> response = new HashMap<>();
        response.put("detail", "Roles assigned successfully");
        return ResponseEntity.ok(response);
    }

    @PutMapping("/users/{user_id}")
    @RequirePermission("user:update")
    public ResponseEntity<?> updateUser(@PathVariable Long user_id, @RequestBody UpdateUserRequest updateRequest) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        User user = userMapper.findById(user_id);
        if (user == null) {
            return ResponseEntity.notFound().build();
        }

        // 不允许修改 username 字段
        if (updateRequest.getUsername() != null && !updateRequest.getUsername().equals(user.getUsername())) {
            return ResponseEntity.badRequest().body("Username cannot be modified");
        }

        // Check if email already exists (excluding current user)
        Optional<User> existingEmail = userMapper.findByEmail(updateRequest.getEmail());
        if (existingEmail.isPresent() && !existingEmail.get().getId().equals(user_id)) {
            return ResponseEntity.badRequest().body("Email already registered");
        }

        // Update user
        user.setName(updateRequest.getName());
        user.setEmail(updateRequest.getEmail());
        if (updateRequest.getPassword() != null && !updateRequest.getPassword().isEmpty()) {
            user.setPassword(passwordEncoder.encode(updateRequest.getPassword()));
        }

        userMapper.update(user);

        // Build response
        Map<String, Object> response = new HashMap<>();
        response.put("id", user.getId());
        response.put("username", user.getUsername());
        response.put("name", user.getName());
        response.put("email", user.getEmail());
        response.put("created_at", user.getCreatedAt());
        response.put("last_login_at", user.getLastLoginAt());

        return ResponseEntity.ok(response);
    }

    @DeleteMapping("/users/{user_id}")
    @RequirePermission("user:delete")
    public ResponseEntity<?> deleteUser(@PathVariable Long user_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        User user = userMapper.findById(user_id);
        if (user == null) {
            return ResponseEntity.notFound().build();
        }

        // Prevent editing admin user
        if ("admin".equals(user.getUsername())) {
            return ResponseEntity.status(403).body("Cannot delete admin user");
        }

        // Delete user roles
        userMapper.deleteUserRoles(user_id);

        // Delete user menus
        userMapper.deleteUserMenus(user_id);

        // Delete user permissions
        userMapper.deleteUserPermissions(user_id);

        // Delete user sessions
        userSessionMapper.deleteByUserId(user_id);

        // Delete user
        userMapper.delete(user_id);

        Map<String, String> response = new HashMap<>();
        response.put("detail", "User deleted successfully");
        return ResponseEntity.ok(response);
    }

    // Request classes
    public static class LoginRequest {
        private String username;
        private String password;

        // getters and setters
        public String getUsername() {
            return username;
        }

        public void setUsername(String username) {
            this.username = username;
        }

        public String getPassword() {
            return password;
        }

        public void setPassword(String password) {
            this.password = password;
        }
    }

    public static class CreateUserRequest {
        private String username;
        private String password;
        private String name;
        private String email;

        // getters and setters
        public String getUsername() {
            return username;
        }

        public void setUsername(String username) {
            this.username = username;
        }

        public String getPassword() {
            return password;
        }

        public void setPassword(String password) {
            this.password = password;
        }

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public String getEmail() {
            return email;
        }

        public void setEmail(String email) {
            this.email = email;
        }
    }

    public static class RegisterRequest {
        private String username;
        private String password;
        private String name;
        private String email;

        // getters and setters
        public String getUsername() {
            return username;
        }

        public void setUsername(String username) {
            this.username = username;
        }

        public String getPassword() {
            return password;
        }

        public void setPassword(String password) {
            this.password = password;
        }

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public String getEmail() {
            return email;
        }

        public void setEmail(String email) {
            this.email = email;
        }
    }

    public static class UpdateUserRequest {
        private String username;
        private String password;
        private String name;
        private String email;

        // getters and setters
        public String getUsername() {
            return username;
        }

        public void setUsername(String username) {
            this.username = username;
        }

        public String getPassword() {
            return password;
        }

        public void setPassword(String password) {
            this.password = password;
        }

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public String getEmail() {
            return email;
        }

        public void setEmail(String email) {
            this.email = email;
        }
    }
}
