package com.taskboard.backend.mapper;

import com.taskboard.backend.model.Tag;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface TagMapper {
    
    Tag findById(@Param("id") Long id);
    
    List<Tag> findAll();
    
    int insert(Tag tag);
    
    int update(Tag tag);
    
    int delete(@Param("id") Long id);
}
