package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;
import java.util.List;

@Data
public class Role {

    private Long id;

    private String name;

    private String code;

    private String description;

    private Integer status = 1; // 1: 启用，0: 禁用

    private Date createdAt = new Date();

    private Date updatedAt = new Date();

    // Relationships - 只保留属性定义，不再使用 JPA 注解
    private List<User> users;

    private List<Menu> menus;

    private List<Permission> permissions;
}
