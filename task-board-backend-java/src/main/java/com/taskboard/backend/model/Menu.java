package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;
import java.util.List;

@Data
public class Menu {

    private Long id;

    private String name;

    private Long parentId; // 父菜单 ID

    private Menu parent;

    private String path; // 路由路径

    private String component; // 组件路径

    private String icon; // 菜单图标

    private Integer orderIndex = 0; // 排序

    private String type = "menu"; // menu: 菜单，external: 外部链接，iframe: 内嵌 iframe

    private String externalUrl; // 外部链接 URL

    private String target; // 打开方式：_blank, _self

    private Integer status = 1; // 1: 启用，0: 禁用

    private Date createdAt = new Date();

    private Date updatedAt = new Date();

    // Relationships - 只保留属性定义，不再使用 JPA 注解
    private List<Menu> children;

    private List<Role> roles;

    private List<User> users;
}