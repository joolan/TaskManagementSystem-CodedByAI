package com.taskboard.backend.mapper;

import com.taskboard.backend.model.TaskHour;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface TaskHourMapper {
    
    TaskHour findById(@Param("id") Long id);
    
    List<TaskHour> findByTaskId(@Param("taskId") Long taskId);
    
    List<TaskHour> findByUserId(@Param("userId") Long userId);
    
    int insert(TaskHour taskHour);
    
    int delete(@Param("id") Long id);
}
