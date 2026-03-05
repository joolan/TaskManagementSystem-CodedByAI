package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;

@Data
public class TaskFollow {

    private Long id;

    private Long taskId;
    
    private Task task;

    private Long userId;
    
    private User user;

    private Date createdAt = new Date();
}