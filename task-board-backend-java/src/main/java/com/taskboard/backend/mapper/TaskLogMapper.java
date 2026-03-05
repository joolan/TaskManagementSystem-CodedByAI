package com.taskboard.backend.mapper;

import com.taskboard.backend.model.TaskLog;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface TaskLogMapper {
    
    TaskLog findById(@Param("id") Long id);
    
    List<TaskLog> findByTaskId(@Param("taskId") Long taskId);
    
    int insert(TaskLog taskLog);
    
    int delete(@Param("id") Long id);
}
