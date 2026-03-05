package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;
import java.util.List;

@Data
public class Permission {

    private Long id;

    private String name;

    private String code; // 权限编码

    private String description;

    private Long menuId; // 关联的菜单 ID
    
    private Menu menu; // 关联的菜单

    private Date createdAt = new Date();

    private Date updatedAt = new Date();

    // Relationships - 只保留属性定义，不再使用 JPA 注解
    private List<Role> roles;

    private List<User> users;
}