package com.taskboard.backend.model;

import lombok.Data;
import java.util.List;

@Data
public class Status {

    private Long id;

    private String name;

    private Integer orderIndex;

    private String color;

    // Relationships - 只保留属性定义，不再使用 JPA 注解
    private List<Task> tasks;
}