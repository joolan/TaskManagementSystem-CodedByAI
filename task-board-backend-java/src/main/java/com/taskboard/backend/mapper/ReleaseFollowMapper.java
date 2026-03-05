package com.taskboard.backend.mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface ReleaseFollowMapper {
    
    int countMyFollowedUncompletedReleases(@Param("userId") Long userId, @Param("statuses") List<String> statuses);
    
    List<Long> findFollowedReleaseIds(@Param("userId") Long userId);
}
