package com.taskboard.backend.mapper;

import com.taskboard.backend.model.UserSession;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface UserSessionMapper {
    
    UserSession findById(@Param("id") Long id);
    
    UserSession findByToken(@Param("token") String token);
    
    List<UserSession> findByUserId(@Param("userId") Long userId);
    
    List<UserSession> findActiveByUserId(@Param("userId") Long userId);
    
    int insert(UserSession session);
    
    int update(UserSession session);
    
    int delete(@Param("id") Long id);
    
    int deleteByToken(@Param("token") String token);
    
    int deleteByUserId(@Param("userId") Long userId);
    
    int deleteExpiredSessions();
}
