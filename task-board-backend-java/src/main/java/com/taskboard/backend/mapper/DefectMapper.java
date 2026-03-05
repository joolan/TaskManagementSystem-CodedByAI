package com.taskboard.backend.mapper;

import com.taskboard.backend.model.Defect;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface DefectMapper {
    
    Defect findById(@Param("id") Long id);
    
    List<Defect> findAll();
    
    int insert(Defect defect);
    
    int update(Defect defect);
    
    int delete(@Param("id") Long id);
    
    int countMyUncompletedDefects(@Param("userId") Long userId, @Param("statusList") List<String> statusList);
    
    int countCreatedInDateRange(@Param("startDate") String startDate, @Param("endDate") String endDate);
    
    int countCompletedInDateRange(@Param("startDate") String startDate, @Param("endDate") String endDate);
}
