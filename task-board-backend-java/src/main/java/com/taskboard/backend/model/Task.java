package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;
import java.util.List;

@Data
public class Task {

    private Long id;

    private String title;

    private String description;

    private Long statusId;
    
    private Status status;

    private Long assigneeId;
    
    private User assignee;

    private String priority; // high, medium, low

    private Date dueDate;

    private Date actualStartDate;

    private Date actualCompletionDate;

    private Double estimatedHours;

    private Double actualHours;

    private User creator;

    private Release release;

    private Date createdAt = new Date();

    private Date updatedAt = new Date();

    // Relationships - 只保留属性定义，不再使用 JPA 注解
    private List<Comment> comments;

    private List<Attachment> attachments;

    private List<TaskLog> logs;

    private List<TaskFollow> follows;

    private List<TaskHour> hours;

    private List<User> assignees;

    private List<Tag> tags;
}