package com.taskboard.backend.mapper;

import com.taskboard.backend.model.Comment;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface CommentMapper {
    
    Comment findById(@Param("id") Long id);
    
    List<Comment> findAll();
    
    List<Comment> findByTaskId(@Param("taskId") Long taskId);
    
    int insert(Comment comment);
    
    int update(Comment comment);
    
    int delete(@Param("id") Long id);
}
