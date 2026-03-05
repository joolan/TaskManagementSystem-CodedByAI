package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;

@Data
public class SystemSetting {
    private Long id;
    private String key;
    private String value;
    private String description;
    private Date createdAt;
    private Date updatedAt;
}
