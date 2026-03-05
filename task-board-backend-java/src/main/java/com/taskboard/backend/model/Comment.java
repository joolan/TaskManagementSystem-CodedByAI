package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;
import java.util.List;

@Data
public class Comment {

    private Long id;

    private Long taskId;

    private Task task;

    private Long userId;

    private User user;

    private String content;

    private Integer isAnonymous = 0;

    private Date pinnedAt;

    private Date createdAt = new Date();

    // Relationships - 只保留属性定义，不再使用 JPA 注解
    private List<Attachment> attachments;
}