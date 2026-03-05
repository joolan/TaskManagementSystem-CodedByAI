package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;

@Data
public class UserSession {

    private Long id;

    private Long userId;

    private String token;

    private String ipAddress;

    private String userAgent;

    private Date loginAt;

    private Date lastActivityAt;

    private Boolean isActive;
}
