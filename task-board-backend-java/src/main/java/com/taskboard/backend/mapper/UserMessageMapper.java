package com.taskboard.backend.mapper;

import com.taskboard.backend.model.UserMessage;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface UserMessageMapper {
    
    List<UserMessage> findByUserId(@Param("userId") Long userId);
    
    List<UserMessage> findByUserIdAndReadStatus(@Param("userId") Long userId, @Param("isRead") Integer isRead);
    
    int insert(UserMessage userMessage);
    
    int update(UserMessage userMessage);
    
    int countUnread(@Param("userId") Long userId);
}
