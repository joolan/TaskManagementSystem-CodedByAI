package com.taskboard.backend.mapper;

import com.taskboard.backend.model.Menu;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Set;

@Mapper
public interface MenuMapper {
    
    Menu findById(@Param("id") Long id);
    
    List<Menu> findAll();
    
    List<Menu> findByUserId(@Param("userId") Long userId);
    
    List<Menu> findByRoleId(@Param("roleId") Long roleId);
    
    List<Long> findMenuIdsByRoleId(@Param("roleId") Long roleId);
    
    List<Menu> findByIdsAndStatus(@Param("ids") Set<Long> ids, @Param("status") Integer status);
    
    List<Menu> findParentMenus();
    
    List<Menu> findChildren(@Param("parentId") Long parentId);
    
    int insert(Menu menu);
    
    int update(Menu menu);
    
    int delete(@Param("id") Long id);
}
