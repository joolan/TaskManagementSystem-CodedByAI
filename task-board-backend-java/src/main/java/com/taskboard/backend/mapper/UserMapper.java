package com.taskboard.backend.mapper;

import com.taskboard.backend.model.Menu;
import com.taskboard.backend.model.Permission;
import com.taskboard.backend.model.Role;
import com.taskboard.backend.model.User;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;
import java.util.Optional;

@Mapper
public interface UserMapper {
    
    User findById(@Param("id") Long id);
    
    Optional<User> findByUsername(@Param("username") String username);
    
    Optional<User> findByEmail(@Param("email") String email);
    
    List<User> findAll();
    
    int insert(User user);
    
    int update(User user);
    
    int delete(@Param("id") Long id);
    
    List<Menu> findUserExtraMenus(@Param("userId") Long userId);
    
    List<Permission> findUserExtraPermissions(@Param("userId") Long userId);
    
    int deleteUserMenus(@Param("userId") Long userId);
    
    int insertUserMenu(@Param("userId") Long userId, @Param("menuId") Long menuId);
    
    int deleteUserPermissions(@Param("userId") Long userId);
    
    int insertUserPermission(@Param("userId") Long userId, @Param("permissionId") Long permissionId);
    
    List<Role> findUserRoles(@Param("userId") Long userId);
    
    int countUserSessions(@Param("userId") Long userId);
    
    int deleteUserRoles(@Param("userId") Long userId);
    
    int insertUserRole(@Param("userId") Long userId, @Param("roleId") Long roleId);
    
    List<Map<String, Object>> getUserWorkload(@Param("startDate") String startDate, @Param("endDate") String endDate);
}
