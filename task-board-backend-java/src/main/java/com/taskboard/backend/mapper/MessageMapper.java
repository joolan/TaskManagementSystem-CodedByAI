package com.taskboard.backend.mapper;

import com.taskboard.backend.model.Message;
import com.taskboard.backend.model.UserMessage;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface MessageMapper {
    
    Message findById(@Param("id") Long id);
    
    List<Message> findAll();
    
    int insert(Message message);
    
    int delete(@Param("id") Long id);
}
