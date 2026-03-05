package com.taskboard.backend.mapper;

import com.taskboard.backend.model.RequirementTag;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface RequirementTagMapper {
    
    RequirementTag findById(@Param("id") Long id);
    
    List<RequirementTag> findAll();
    
    int insert(RequirementTag requirementTag);
    
    int update(RequirementTag requirementTag);
    
    int delete(@Param("id") Long id);
}
