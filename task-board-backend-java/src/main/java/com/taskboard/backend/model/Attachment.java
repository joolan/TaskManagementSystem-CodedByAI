package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;

@Data
public class Attachment {

    private Long id;

    private Long taskId;

    private Long userId;

    private Long commentId;

    private Task task;

    private User user;

    private Comment comment;

    private String filename;

    private String filePath;

    private Date createdAt = new Date();
}