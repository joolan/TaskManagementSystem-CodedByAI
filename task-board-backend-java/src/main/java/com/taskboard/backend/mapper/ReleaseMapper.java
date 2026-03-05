package com.taskboard.backend.mapper;

import com.taskboard.backend.model.Release;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface ReleaseMapper {
    
    Release findById(@Param("id") Long id);
    
    List<Release> findAll();
    
    List<Release> findByStatus(@Param("status") String status);
    
    int insert(Release release);
    
    int update(Release release);
    
    int delete(@Param("id") Long id);
    
    int countCreatedInDateRange(@Param("startDate") String startDate, @Param("endDate") String endDate);
    
    int countCompletedInDateRange(@Param("startDate") String startDate, @Param("endDate") String endDate);
}
