package com.taskboard.backend.controller;

import com.taskboard.backend.annotation.RequirePermission;
import com.taskboard.backend.mapper.PermissionMapper;
import com.taskboard.backend.mapper.UserMapper;
import com.taskboard.backend.model.Permission;
import com.taskboard.backend.model.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/permissions")
public class PermissionController {

    @Autowired
    private PermissionMapper permissionMapper;
    
    @Autowired
    private UserMapper userMapper;

    @GetMapping
    @RequirePermission("permission:list")
    public ResponseEntity<?> getPermissions() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User user = userMapper.findByUsername(username).orElse(null);
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        // 如果是 admin 用户，返回所有权限
        if ("admin".equals(username)) {
            List<Permission> permissions = permissionMapper.findAll();
            return ResponseEntity.ok(permissions);
        }

        // 普通用户返回其角色的权限
        List<Permission> permissions = permissionMapper.findByUserId(user.getId());
        return ResponseEntity.ok(permissions);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Permission> getPermissionById(@PathVariable Long id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body(null);
        }

        Permission permission = permissionMapper.findById(id);
        if (permission != null) {
            return ResponseEntity.ok(permission);
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @PostMapping
    @RequirePermission("permission:create")
    public ResponseEntity<Permission> createPermission(@RequestBody Permission permission) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body(null);
        }

        String username = authentication.getName();
        // 只有 admin 用户可以创建权限
        if (!"admin".equals(username)) {
            return ResponseEntity.status(403).body(null);
        }

        permissionMapper.insert(permission);
        return ResponseEntity.ok(permission);
    }

    @PutMapping("/{id}")
    @RequirePermission("permission:update")
    public ResponseEntity<Permission> updatePermission(@PathVariable Long id, @RequestBody Permission permission) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body(null);
        }

        String username = authentication.getName();
        // 只有 admin 用户可以更新权限
        if (!"admin".equals(username)) {
            return ResponseEntity.status(403).body(null);
        }

        Permission existingPermission = permissionMapper.findById(id);
        if (existingPermission != null) {
            permission.setId(id);
            permissionMapper.update(permission);
            return ResponseEntity.ok(permission);
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @DeleteMapping("/{id}")
    @RequirePermission("permission:delete")
    public ResponseEntity<Void> deletePermission(@PathVariable Long id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).build();
        }

        String username = authentication.getName();
        // 只有 admin 用户可以删除权限
        if (!"admin".equals(username)) {
            return ResponseEntity.status(403).build();
        }

        Permission permission = permissionMapper.findById(id);
        if (permission != null) {
            permissionMapper.delete(id);
            return ResponseEntity.ok().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @GetMapping("/tree")
    public ResponseEntity<?> getPermissionTree() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        List<Permission> permissions = permissionMapper.findAll();

        // 按模块分组构建权限树
        Map<String, Map<String, Object>> permissionDict = new HashMap<>();

        for (Permission permission : permissions) {
            // 按 code 的第一部分分组（例如 "user:read" -> "user"）
            String module = permission.getCode().contains(":") ? permission.getCode().split(":")[0] : "other";

            if (!permissionDict.containsKey(module)) {
                Map<String, Object> moduleMap = new HashMap<>();
                moduleMap.put("id", "module-" + module);
                moduleMap.put("name", module + "模块");
                moduleMap.put("code", module);
                moduleMap.put("description", module + "相关权限");
                moduleMap.put("children", new ArrayList<>());
                permissionDict.put(module, moduleMap);
            }

            Map<String, Object> permMap = new HashMap<>();
            permMap.put("id", permission.getId());
            permMap.put("name", permission.getName());
            permMap.put("code", permission.getCode());
            permMap.put("description", permission.getDescription());

            List<Map<String, Object>> children = (List<Map<String, Object>>) permissionDict.get(module).get("children");
            children.add(permMap);
        }

        return ResponseEntity.ok(new ArrayList<>(permissionDict.values()));
    }
}
