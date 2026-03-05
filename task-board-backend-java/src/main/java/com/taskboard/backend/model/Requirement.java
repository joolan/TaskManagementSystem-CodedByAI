package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;

@Data
public class Requirement {

    private Long id;

    private User creator;

    private Date createdAt = new Date();

    private String source; // 需求来源

    private String name; // 需求名称

    private RequirementTag tag; // 需求标签

    private String description; // 需求描述

    private String status = "草稿"; // 需求状态：草稿、待评审、已确认、已作废、已转任务

    private String priority = "中"; // 需求优先级：高、中、低

    private Date plannedCompletionDate; // 计划完成日期

    private Date actualCompletionDate; // 实际完成日期
    
    private Long createdBy; // 创建者 ID
    
    private Long assigneeId; // 负责人 ID
    
    private Long tagId; // 需求标签 ID
    
    private Long taskId; // 转任务的任务 ID
    
    private Date updatedAt; // 更新时间
}