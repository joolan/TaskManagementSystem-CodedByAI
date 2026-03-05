package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;
import java.util.List;

@Data
public class User {

    private Long id;

    private String username;

    private String password;

    private String name;

    private String email;

    private Date createdAt = new Date();

    private Date lastLoginAt;

    private Integer failedLoginAttempts = 0;

    private Date lockedUntil;

    // Relationships - 只保留属性定义，不再使用JPA注解
    private List<Role> roles;

    private List<Permission> extraPermissions;

    private List<Menu> extraMenus;

    private List<Task> tasks;

    private List<Task> createdTasks;

    private List<Comment> comments;

    private List<Attachment> attachments;

    private List<Release> createdReleases;

    private List<Requirement> createdRequirements;

    private List<Memo> createdMemos;

    private List<Defect> createdDefects;

    private List<Defect> assignedDefects;

    // 计算用户的所有权限
    public List<Permission> getPermissions() {
        return extraPermissions;
    }
}