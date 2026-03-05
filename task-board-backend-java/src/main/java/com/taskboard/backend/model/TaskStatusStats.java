package com.taskboard.backend.model;

import lombok.Data;

@Data
public class TaskStatusStats {

    private String statusName;
    
    private Integer count;
    
    private String color;
}
