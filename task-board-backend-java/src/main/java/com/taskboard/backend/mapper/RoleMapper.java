package com.taskboard.backend.mapper;

import com.taskboard.backend.model.Role;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface RoleMapper {
    
    Role findById(@Param("id") Long id);
    
    List<Role> findAll();
    
    List<Role> findByUserId(@Param("userId") Long userId);
    
    int insert(Role role);
    
    int update(Role role);
    
    int delete(@Param("id") Long id);
    
    int deleteRolePermissions(@Param("roleId") Long roleId);
    
    int insertRolePermission(@Param("roleId") Long roleId, @Param("permissionId") Long permissionId);
    
    int deleteRoleMenus(@Param("roleId") Long roleId);
    
    int insertRoleMenu(@Param("roleId") Long roleId, @Param("menuId") Long menuId);
}
