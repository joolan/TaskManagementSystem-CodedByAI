package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;
import java.util.List;

@Data
public class Tag {

    private Long id;

    private String name;

    private String color = "#60a5fa";

    private Date createdAt = new Date();

    // Relationships - 只保留属性定义，不再使用 JPA 注解
    private List<Task> tasks;
}