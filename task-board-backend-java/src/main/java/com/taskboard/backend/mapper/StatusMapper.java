package com.taskboard.backend.mapper;

import com.taskboard.backend.model.Status;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

@Mapper
public interface StatusMapper {
    
    Status findById(@Param("id") Long id);
    
    List<Status> findAll();
    
    Status findByName(@Param("name") String name);
    
    List<Status> findByNameIn(@Param("names") List<String> names);
    
    List<Map<String, Object>> findTaskStatusStats();
    
    int insert(Status status);
    
    int update(Status status);
    
    int delete(@Param("id") Long id);
}
