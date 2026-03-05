package com.taskboard.backend.mapper;

import com.taskboard.backend.model.Requirement;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface RequirementMapper {
    
    Requirement findById(@Param("id") Long id);
    
    List<Requirement> findAll();
    
    int insert(Requirement requirement);
    
    int update(Requirement requirement);
    
    int delete(@Param("id") Long id);
    
    int countMyPendingRequirements(@Param("userId") Long userId, @Param("statusList") List<String> statusList);
    
    int countCreatedInDateRange(@Param("startDate") String startDate, @Param("endDate") String endDate);
    
    int countCompletedInDateRange(@Param("startDate") String startDate, @Param("endDate") String endDate);
}
