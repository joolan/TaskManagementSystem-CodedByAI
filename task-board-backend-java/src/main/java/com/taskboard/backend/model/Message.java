package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;

@Data
public class Message {

    private Long id;
    private String messageType;
    private String title;
    private String content;
    private String redirectPath;
    private Long createdBy;
    private Date createdAt;
}
