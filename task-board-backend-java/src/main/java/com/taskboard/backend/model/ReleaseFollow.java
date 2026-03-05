package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;

@Data
public class ReleaseFollow {

    private Long id;

    private Release release;

    private User user;

    private Date createdAt = new Date();
}