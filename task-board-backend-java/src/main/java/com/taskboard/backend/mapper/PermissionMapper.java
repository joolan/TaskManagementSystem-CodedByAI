package com.taskboard.backend.mapper;

import com.taskboard.backend.model.Permission;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface PermissionMapper {
    
    Permission findById(@Param("id") Long id);
    
    List<Permission> findAll();
    
    List<Permission> findByUserId(@Param("userId") Long userId);
    
    List<Permission> findByRoleId(@Param("roleId") Long roleId);
    
    int insert(Permission permission);
    
    int update(Permission permission);
    
    int delete(@Param("id") Long id);
    
    int deleteRolePermissions(@Param("roleId") Long roleId);
    
    int insertRolePermission(@Param("roleId") Long roleId, @Param("permissionId") Long permissionId);
}
