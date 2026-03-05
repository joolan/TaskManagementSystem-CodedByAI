package com.taskboard.backend.mapper;

import com.taskboard.backend.model.SystemSetting;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Optional;

@Mapper
public interface SystemSettingMapper {
    
    Optional<SystemSetting> findByKey(@Param("key") String key);
    
    List<SystemSetting> findAll();
    
    void insert(SystemSetting setting);
    
    void update(SystemSetting setting);
    
    void deleteByKey(@Param("key") String key);
}
