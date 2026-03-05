package com.taskboard.backend.model;

import lombok.Data;

@Data
public class TaskTag {

    private Long taskId;
    
    private Long tagId;
    
    // Relationships
    private Tag tag;
}
