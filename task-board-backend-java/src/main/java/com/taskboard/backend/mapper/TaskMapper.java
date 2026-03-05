package com.taskboard.backend.mapper;

import com.taskboard.backend.model.Task;
import com.taskboard.backend.model.TaskTag;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface TaskMapper {
    
    Task findById(@Param("id") Long id);
    
    List<Task> findAll();
    
    List<Task> findByStatusId(@Param("statusId") Long statusId);
    
    List<Task> findByStatusIds(@Param("statusIds") List<Long> statusIds);
    
    int insert(Task task);
    
    int update(Task task);
    
    int delete(@Param("id") Long id);
    
    int countByStatusId(@Param("statusId") Long statusId);
    
    int countMyUncompletedTasks(@Param("userId") Long userId, @Param("statusIds") List<Long> statusIds);
    
    int deleteTaskTags(@Param("taskId") Long taskId);
    
    int insertTaskTag(@Param("taskId") Long taskId, @Param("tagId") Long tagId);
    
    int countCreatedInDateRange(@Param("startDate") String startDate, @Param("endDate") String endDate);
    
    int countCompletedInDateRange(@Param("startDate") String startDate, @Param("endDate") String endDate);
    
    int countByStatusIdInDateRange(@Param("statusId") Long statusId, @Param("startDate") String startDate, @Param("endDate") String endDate);
    
    int countMyCompletedTasks(@Param("userId") Long userId, @Param("statusIds") List<Long> statusIds);
    
    List<Long> getUncompletedStatusIds();
    
    List<TaskTag> findTaskTagsByTaskId(@Param("taskId") Long taskId);
}
