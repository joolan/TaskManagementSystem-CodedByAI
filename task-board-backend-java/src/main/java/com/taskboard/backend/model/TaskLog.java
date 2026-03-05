package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;

@Data
public class TaskLog {

    private Long id;

    private Long taskId;
    
    private Task task;

    private Long userId;
    
    private User user;

    private String actionType; // create, update, status_change, etc.

    private String title; // 日志标题

    private String content; // 变更详情

    private Date createdAt = new Date();
}