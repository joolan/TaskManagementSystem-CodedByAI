package com.taskboard.backend.mapper;

import com.taskboard.backend.model.ReleaseTag;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface ReleaseTagMapper {
    
    ReleaseTag findById(@Param("id") Long id);
    
    List<ReleaseTag> findAll();
    
    int insert(ReleaseTag releaseTag);
    
    int update(ReleaseTag releaseTag);
    
    int delete(@Param("id") Long id);
}
