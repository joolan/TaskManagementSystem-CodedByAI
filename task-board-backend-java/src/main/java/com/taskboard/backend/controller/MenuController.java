package com.taskboard.backend.controller;

import com.taskboard.backend.annotation.RequirePermission;
import com.taskboard.backend.mapper.MenuMapper;
import com.taskboard.backend.mapper.PermissionMapper;
import com.taskboard.backend.mapper.RoleMapper;
import com.taskboard.backend.mapper.UserMapper;
import com.taskboard.backend.model.Menu;
import com.taskboard.backend.model.Permission;
import com.taskboard.backend.model.Role;
import com.taskboard.backend.model.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/menus")
public class MenuController {

    @Autowired
    private MenuMapper menuMapper;
    
    @Autowired
    private UserMapper userMapper;
    
    @Autowired
    private PermissionMapper permissionMapper;
    
    @Autowired
    private RoleMapper roleMapper;

    @GetMapping("/user")
    public ResponseEntity<?> getUserMenus() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        
        List<Menu> menus;
        // 如果用户是 admin，返回所有启用的菜单
        if ("admin".equals(username)) {
            List<Menu> allMenus = menuMapper.findAll();
            menus = new ArrayList<>();
            for (Menu menu : allMenus) {
                if (menu.getStatus() != null && menu.getStatus() == 1) {
                    menus.add(menu);
                }
            }
        } else {
            // 普通用户返回用户所有有权限的菜单
            User user = userMapper.findByUsername(username).orElse(null);
            if (user == null) {
                return ResponseEntity.status(404).body("User not found");
            }
            
            // 手动加载用户的角色
            List<Role> roles = userMapper.findUserRoles(user.getId());
            user.setRoles(roles);
            
            // 获取用户可访问的菜单 ID 集合
            Set<Long> menuIds = new HashSet<>();
            
            // 1. 从用户角色菜单表 (role_menus) 获取菜单 ID
            if (roles != null) {
                for (Role role : roles) {
                    List<Long> roleMenuIds = menuMapper.findMenuIdsByRoleId(role.getId());
                    if (roleMenuIds != null) {
                        menuIds.addAll(roleMenuIds);
                    }
                }
            }
            
            // 2. 从用户额外菜单表 (user_menus) 获取菜单 ID
            List<Menu> userExtraMenus = userMapper.findUserExtraMenus(user.getId());
            if (userExtraMenus != null) {
                for (Menu menu : userExtraMenus) {
                    if (menu.getStatus() != null && menu.getStatus() == 1) {
                        menuIds.add(menu.getId());
                    }
                }
            }
            
            // 3. 从用户角色权限表 (role_permissions) 获取功能权限，然后获取对应的菜单 ID
            if (roles != null) {
                for (Role role : roles) {
                    List<Permission> rolePermissions = permissionMapper.findByRoleId(role.getId());
                    if (rolePermissions != null) {
                        for (Permission permission : rolePermissions) {
                            if (permission.getMenuId() != null) {
                                menuIds.add(permission.getMenuId());
                            }
                        }
                    }
                }
            }
            
            // 4. 从用户额外权限表 (user_permissions) 获取功能权限，然后获取对应的菜单 ID
            List<Permission> userExtraPermissions = userMapper.findUserExtraPermissions(user.getId());
            if (userExtraPermissions != null) {
                for (Permission permission : userExtraPermissions) {
                    if (permission.getMenuId() != null) {
                        menuIds.add(permission.getMenuId());
                    }
                }
            }
            
            // 5. 递归添加所有父级菜单
            if (!menuIds.isEmpty()) {
                // 获取所有菜单
                List<Menu> allMenus = menuMapper.findAll();
                Map<Long, Menu> menuMap = new HashMap<>();
                for (Menu menu : allMenus) {
                    menuMap.put(menu.getId(), menu);
                }
                
                // 递归获取所有父级菜单
                Set<Long> finalMenuIds = new HashSet<>();
                for (Long menuId : menuIds) {
                    addParentMenus(menuId, menuMap, finalMenuIds);
                }
                
                // 获取最终需要返回的菜单列表
                menus = new ArrayList<>();
                for (Menu menu : allMenus) {
                    if (finalMenuIds.contains(menu.getId()) && 
                        menu.getStatus() != null && menu.getStatus() == 1) {
                        menus.add(menu);
                    }
                }
            } else {
                menus = new ArrayList<>();
            }
        }
        
        // 构建树形结构
        List<Map<String, Object>> menuTree = buildMenuTree(menus);
        return ResponseEntity.ok(menuTree);
    }
    
    /**
     * 递归添加父级菜单到集合中
     */
    private void addParentMenus(Long menuId, Map<Long, Menu> menuMap, Set<Long> finalMenuIds) {
        if (menuId == null || finalMenuIds.contains(menuId)) {
            return;
        }
        
        Menu menu = menuMap.get(menuId);
        if (menu == null) {
            return;
        }
        
        // 添加当前菜单
        finalMenuIds.add(menuId);
        
        // 递归添加父级菜单
        if (menu.getParentId() != null) {
            addParentMenus(menu.getParentId(), menuMap, finalMenuIds);
        }
    }
    
    /**
     * 构建菜单树形结构
     */
    private List<Map<String, Object>> buildMenuTree(List<Menu> menus) {
        // 使用字典避免重复
        Map<Long, Map<String, Object>> menuDict = new HashMap<>();
        
        for (Menu menu : menus) {
            Map<String, Object> menuMap = new HashMap<>();
            menuMap.put("id", menu.getId());
            menuMap.put("name", menu.getName());
            menuMap.put("path", menu.getPath());
            menuMap.put("component", menu.getComponent());
            menuMap.put("icon", menu.getIcon());
            menuMap.put("order_index", menu.getOrderIndex());
            menuMap.put("parent_id", menu.getParentId());
            menuMap.put("type", menu.getType());
            menuMap.put("external_url", menu.getExternalUrl());
            menuMap.put("target", menu.getTarget());
            menuMap.put("status", menu.getStatus());
            menuMap.put("children", new ArrayList<>());
            
            menuDict.put(menu.getId(), menuMap);
        }
        
        // 构建父子关系
        List<Map<String, Object>> rootMenus = new ArrayList<>();
        for (Map.Entry<Long, Map<String, Object>> entry : menuDict.entrySet()) {
            Map<String, Object> menu = entry.getValue();
            Long parentId = (Long) menu.get("parent_id");
            
            if (parentId == null) {
                // 根菜单
                rootMenus.add(menu);
            } else {
                // 子菜单，添加到父菜单的 children 中
                Map<String, Object> parent = menuDict.get(parentId);
                if (parent != null) {
                    List<Map<String, Object>> children = (List<Map<String, Object>>) parent.get("children");
                    // 避免重复添加
                    boolean exists = false;
                    for (Map<String, Object> child : children) {
                        if (child.get("id").equals(menu.get("id"))) {
                            exists = true;
                            break;
                        }
                    }
                    if (!exists) {
                        children.add(menu);
                    }
                }
            }
        }
        
        // 按 order_index 排序
        rootMenus.sort((m1, m2) -> {
            Integer order1 = (Integer) m1.get("order_index");
            Integer order2 = (Integer) m2.get("order_index");
            return order1.compareTo(order2);
        });
        
        for (Map<String, Object> menu : rootMenus) {
            sortChildren((List<Map<String, Object>>) menu.get("children"));
        }
        
        return rootMenus;
    }
    
    /**
     * 递归排序子菜单
     */
    private void sortChildren(List<Map<String, Object>> children) {
        if (children == null || children.isEmpty()) {
            return;
        }
        
        children.sort((m1, m2) -> {
            Integer order1 = (Integer) m1.get("order_index");
            Integer order2 = (Integer) m2.get("order_index");
            return order1.compareTo(order2);
        });
        
        for (Map<String, Object> menu : children) {
            sortChildren((List<Map<String, Object>>) menu.get("children"));
        }
    }
    
    @GetMapping("/all")
    @RequirePermission("menu:list")
    public ResponseEntity<?> getAllMenus() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        List<Menu> menus = menuMapper.findAll();
        return ResponseEntity.ok(menus);
    }
    
    @GetMapping("/all-tree")
    @RequirePermission("menu:list")
    public ResponseEntity<?> getAllMenusTree() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        List<Menu> menus = menuMapper.findAll();
        List<Map<String, Object>> menuTree = buildMenuTree(menus);
        return ResponseEntity.ok(menuTree);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<?> getMenuById(@PathVariable Long id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        Menu menu = menuMapper.findById(id);
        if (menu != null) {
            return ResponseEntity.ok(menu);
        } else {
            return ResponseEntity.notFound().build();
        }
    }
    
    @GetMapping("/tree")
    @RequirePermission("menu:list")
    public ResponseEntity<?> getMenusTree() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        // 获取所有启用的菜单
        List<Menu> menus = menuMapper.findAll();
        List<Menu> enabledMenus = new ArrayList<>();
        for (Menu menu : menus) {
            if (menu.getStatus() != null && menu.getStatus() == 1) {
                enabledMenus.add(menu);
            }
        }
        
        // 获取所有权限
        List<Permission> permissions = permissionMapper.findAll();
        
        // 按菜单 ID 组织权限
        Map<Long, List<Map<String, Object>>> menuPermissions = new HashMap<>();
        for (Permission permission : permissions) {
            if (permission.getMenuId() != null) {
                menuPermissions.computeIfAbsent(permission.getMenuId(), k -> new ArrayList<>());
                Map<String, Object> permMap = new HashMap<>();
                permMap.put("id", permission.getId());
                permMap.put("name", permission.getName());
                permMap.put("code", permission.getCode());
                permMap.put("description", permission.getDescription());
                permMap.put("menu_id", permission.getMenuId());
                menuPermissions.get(permission.getMenuId()).add(permMap);
            }
        }
        
        // 构建菜单树
        Map<Long, Map<String, Object>> menuDict = new HashMap<>();
        for (Menu menu : enabledMenus) {
            Map<String, Object> menuMap = new HashMap<>();
            menuMap.put("id", menu.getId());
            menuMap.put("name", menu.getName());
            menuMap.put("path", menu.getPath());
            menuMap.put("icon", menu.getIcon());
            menuMap.put("type", menu.getType());
            menuMap.put("order_index", menu.getOrderIndex());
            menuMap.put("parent_id", menu.getParentId());
            menuMap.put("children", new ArrayList<>());
            menuMap.put("permissions", menuPermissions.getOrDefault(menu.getId(), new ArrayList<>()));
            menuDict.put(menu.getId(), menuMap);
        }
        
        // 构建父子关系
        List<Map<String, Object>> menuTree = new ArrayList<>();
        for (Map.Entry<Long, Map<String, Object>> entry : menuDict.entrySet()) {
            Map<String, Object> menu = entry.getValue();
            Long parentId = (Long) menu.get("parent_id");
            
            if (parentId == null) {
                menuTree.add(menu);
            } else {
                Map<String, Object> parent = menuDict.get(parentId);
                if (parent != null) {
                    List<Map<String, Object>> children = (List<Map<String, Object>>) parent.get("children");
                    children.add(menu);
                }
            }
        }
        
        // 按 order_index 排序
        menuTree.sort((m1, m2) -> {
            Integer order1 = (Integer) m1.get("order_index");
            Integer order2 = (Integer) m2.get("order_index");
            return order1.compareTo(order2);
        });
        
        for (Map<String, Object> menu : menuTree) {
            sortChildren((List<Map<String, Object>>) menu.get("children"));
        }
        
        return ResponseEntity.ok(menuTree);
    }
}

