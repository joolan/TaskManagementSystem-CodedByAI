package com.taskboard.backend.mapper;

import com.taskboard.backend.model.Attachment;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface AttachmentMapper {
    
    Attachment findById(@Param("id") Long id);
    
    List<Attachment> findAll();
    
    List<Attachment> findByTaskId(@Param("taskId") Long taskId);
    
    List<Attachment> findByCommentId(@Param("commentId") Long commentId);
    
    List<Attachment> findByUserId(@Param("userId") Long userId);
    
    int insert(Attachment attachment);
    
    int update(Attachment attachment);
    
    int delete(@Param("id") Long id);
}
