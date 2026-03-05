package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;

@Data
public class TaskHour {

    private Long id;

    private Long taskId;
    
    private Task task;

    private Long userId;
    
    private User user;

    private Double hours;

    private String remark;

    private Long createdById;
    
    private User creator;

    private Date createdAt = new Date();
}