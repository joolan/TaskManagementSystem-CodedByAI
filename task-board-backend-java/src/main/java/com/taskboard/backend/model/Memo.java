package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;

@Data
public class Memo {

    private Long id;

    private String name;

    private String content;

    private Long createdBy;

    private Date createdAt;

    private Date updatedAt;

    // Relationships
    private User creator;
}
