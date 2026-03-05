package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;
import java.util.List;

@Data
public class Release {

    private Long id;

    private String title; // 发版主题

    private String description; // 发版详情

    private String status; // 计划中、已发版、延期中、已作废

    private Date plannedReleaseDate; // 预计发版时间

    private Date actualReleaseDate; // 实际发版时间

    private User creator;

    private Date createdAt = new Date();

    private Date updatedAt = new Date();
    
    private Long createdBy; // 创建者 ID

    // Relationships - 只保留属性定义，不再使用 JPA 注解
    private List<Task> tasks;

    private List<ReleaseFollow> follows;

    private List<ReleaseTag> tags;
}