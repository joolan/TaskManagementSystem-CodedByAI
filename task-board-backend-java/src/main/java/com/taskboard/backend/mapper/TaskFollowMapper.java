package com.taskboard.backend.mapper;

import com.taskboard.backend.model.TaskFollow;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface TaskFollowMapper {
    
    int countMyFollowedUncompletedTasks(@Param("userId") Long userId, @Param("statusIds") List<Long> statusIds);
    
    TaskFollow findByTaskIdAndUserId(@Param("taskId") Long taskId, @Param("userId") Long userId);
    
    int insert(TaskFollow taskFollow);
    
    int delete(@Param("id") Long id);
    
    int deleteByTaskIdAndUserId(@Param("taskId") Long taskId, @Param("userId") Long userId);
    
    List<TaskFollow> findByTaskId(@Param("taskId") Long taskId);
    
    List<Long> findFollowedTaskIds(@Param("userId") Long userId);
}
