package com.taskboard.backend.mapper;

import com.taskboard.backend.model.Memo;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface MemoMapper {
    
    Memo findById(@Param("id") Long id);
    
    List<Memo> findAll();
    
    List<Memo> findByCreatedBy(@Param("createdBy") Long createdBy);
    
    int insert(Memo memo);
    
    int update(Memo memo);
    
    int delete(@Param("id") Long id);
}
