package com.taskboard.backend.controller;

import com.taskboard.backend.annotation.RequirePermission;
import com.taskboard.backend.mapper.MenuMapper;
import com.taskboard.backend.mapper.PermissionMapper;
import com.taskboard.backend.mapper.RoleMapper;
import com.taskboard.backend.model.Menu;
import com.taskboard.backend.model.Permission;
import com.taskboard.backend.model.Role;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/roles")
public class RoleController {

    @Autowired
    private RoleMapper roleMapper;
    
    @Autowired
    private MenuMapper menuMapper;

    @Autowired
    private PermissionMapper permissionMapper;

    @GetMapping
    @RequirePermission("role:list")
    public List<Role> getRoles() {
        return roleMapper.findAll();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Role> getRoleById(@PathVariable Long id) {
        Role role = roleMapper.findById(id);
        if (role != null) {
            return ResponseEntity.ok(role);
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @PostMapping
    @RequirePermission("role:create")
    public Role createRole(@RequestBody Role role) {
        roleMapper.insert(role);
        return role;
    }

    @PutMapping("/{id}")
    @RequirePermission("role:update")
    public ResponseEntity<Role> updateRole(@PathVariable Long id, @RequestBody Role role) {
        Role existingRole = roleMapper.findById(id);
        if (existingRole != null) {
            role.setId(id);
            roleMapper.update(role);
            return ResponseEntity.ok(role);
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @DeleteMapping("/{id}")
    @RequirePermission("role:delete")
    public ResponseEntity<Void> deleteRole(@PathVariable Long id) {
        Role role = roleMapper.findById(id);
        if (role != null) {
            roleMapper.delete(id);
            return ResponseEntity.ok().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @PostMapping("/{role_id}/permissions")
    @RequirePermission("role:assign_permissions")
    public ResponseEntity<?> assignPermissionsToRole(
            @PathVariable Long role_id,
            @RequestBody List<Long> permissionIds
    ) {
        // 删除角色原有权限
        roleMapper.deleteRolePermissions(role_id);
        
        // 添加新权限
        for (Long permissionId : permissionIds) {
            roleMapper.insertRolePermission(role_id, permissionId);
        }
        
        return ResponseEntity.ok().build();
    }

    @GetMapping("/{role_id}/permissions")
    public ResponseEntity<?> getRolePermissions(@PathVariable Long role_id) {
        Role role = roleMapper.findById(role_id);
        if (role == null) {
            return ResponseEntity.notFound().build();
        }
        
        List<Permission> permissions = permissionMapper.findByRoleId(role_id);
        return ResponseEntity.ok(permissions);
    }
    
    @PostMapping("/{role_id}/menus")
    @RequirePermission("role:assign_menus")
    public ResponseEntity<?> assignMenusToRole(
            @PathVariable Long role_id,
            @RequestBody List<Long> menuIds
    ) {
        Role role = roleMapper.findById(role_id);
        if (role == null) {
            return ResponseEntity.notFound().build();
        }
        
        // 删除角色原有菜单权限
        roleMapper.deleteRoleMenus(role_id);
        
        // 添加新菜单权限
        if (menuIds != null) {
            for (Long menuId : menuIds) {
                roleMapper.insertRoleMenu(role_id, menuId);
            }
        }
        
        Map<String, String> response = new HashMap<>();
        response.put("message", "菜单权限分配成功");
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/{role_id}/menus")
    public ResponseEntity<?> getRoleMenus(@PathVariable Long role_id) {
        Role role = roleMapper.findById(role_id);
        if (role == null) {
            return ResponseEntity.notFound().build();
        }
        
        List<Menu> menus = menuMapper.findByRoleId(role_id);
        return ResponseEntity.ok(menus);
    }
}