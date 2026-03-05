package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;

@Data
public class Defect {

    private Long id;

    private String title;

    private String description;

    private String status = "草稿";

    private Release release;

    private User creator;

    private User assignee;

    private Date createdAt = new Date();

    private Date updatedAt = new Date();
    
    private Long releaseId; // 关联发版 ID
    
    private Long createdBy; // 创建者 ID
    
    private Long assigneeId; // 负责人 ID
}