package com.taskboard.backend.controller;

import com.taskboard.backend.mapper.*;
import com.taskboard.backend.model.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/stats")
public class StatsController {

    @Autowired
    private TaskMapper taskMapper;
    
    @Autowired
    private UserMapper userMapper;
    
    @Autowired
    private StatusMapper statusMapper;
    
    @Autowired
    private RequirementMapper requirementMapper;
    
    @Autowired
    private DefectMapper defectMapper;
    
    @Autowired
    private TaskFollowMapper taskFollowMapper;
    
    @Autowired
    private ReleaseFollowMapper releaseFollowMapper;
    
    @Autowired
    private ReleaseMapper releaseMapper;

    private List<Long> getUncompletedStatusIds() {
        List<Long> uncompletedStatusIds = new ArrayList<>();
        List<Status> allStatuses = statusMapper.findAll();
        for (Status status : allStatuses) {
            if (!"已完成".equals(status.getName())) {
                uncompletedStatusIds.add(status.getId());
            }
        }
        return uncompletedStatusIds;
    }

    @GetMapping("/dashboard")
    public ResponseEntity<?> getDashboardMetrics() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User user = userMapper.findByUsername(username).orElse(null);
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }
        
        // 获取未完成任务的状态（待办、进行中、已暂停）
        List<Status> uncompletedStatuses = statusMapper.findByNameIn(Arrays.asList("待办", "进行中", "已暂停"));
        List<Long> uncompletedStatusIds = new ArrayList<>();
        for (Status status : uncompletedStatuses) {
            uncompletedStatusIds.add(status.getId());
        }
        
        // 获取已完成状态
        Status completedStatus = statusMapper.findByName("已完成");
        Long completedStatusId = completedStatus != null ? completedStatus.getId() : null;
        
        // 1. 我负责的未完成任务
        int myAssignedTasksCount = taskMapper.countMyUncompletedTasks(user.getId(), uncompletedStatusIds);
        
        // 2. 我关注的未完成任务
        int myFollowedTasksCount = taskFollowMapper.countMyFollowedUncompletedTasks(user.getId(), uncompletedStatusIds);
        
        // 3. 我关注的未发版本
        int myFollowedReleasesCount = releaseFollowMapper.countMyFollowedUncompletedReleases(
            user.getId(), 
            Arrays.asList("计划中", "延期中")
        );
        
        // 4. 我创建的待处理需求
        int myRequirementsCount = requirementMapper.countMyPendingRequirements(
            user.getId(), 
            Arrays.asList("草稿", "待评审", "已确认")
        );
        
        // 5. 我负责的未完成缺陷
        int myAssignedDefectsCount = defectMapper.countMyUncompletedDefects(
            user.getId(), 
            Arrays.asList("草稿", "未解决")
        );
        
        // 构建响应
        Map<String, Object> result = new HashMap<>();
        result.put("myAssignedTasksCount", myAssignedTasksCount);
        result.put("myFollowedTasksCount", myFollowedTasksCount);
        result.put("myFollowedReleasesCount", myFollowedReleasesCount);
        result.put("myRequirementsCount", myRequirementsCount);
        result.put("myAssignedDefectsCount", myAssignedDefectsCount);
        
        return ResponseEntity.ok(result);
    }
    
    @GetMapping("/task-status")
    public ResponseEntity<?> getTaskStatusStats() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        List<Map<String, Object>> stats = statusMapper.findTaskStatusStats();
        
        // 转换为 TaskStatusStats 对象
        List<TaskStatusStats> result = new ArrayList<>();
        for (Map<String, Object> stat : stats) {
            TaskStatusStats taskStatusStats = new TaskStatusStats();
            taskStatusStats.setStatusName((String) stat.get("status_name"));
            taskStatusStats.setCount(((Number) stat.get("count")).intValue());
            taskStatusStats.setColor((String) stat.get("color"));
            result.add(taskStatusStats);
        }
        
        return ResponseEntity.ok(result);
    }

    @GetMapping("/overview")
    public ResponseEntity<?> getOverview(
            @RequestParam(required = false) String start_date,
            @RequestParam(required = false) String end_date
    ) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User user = userMapper.findByUsername(username).orElse(null);
        
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        // 获取已完成状态 ID
        Status completedStatus = statusMapper.findByName("已完成");
        Long completedStatusId = completedStatus != null ? completedStatus.getId() : null;

        // 统计任务数据
        Map<String, Integer> taskStats = new HashMap<>();
        int totalTasks = taskMapper.countCreatedInDateRange(start_date, end_date);
        int completedTasks = completedStatusId != null ? 
            taskMapper.countByStatusIdInDateRange(completedStatusId, start_date, end_date) : 0;
        int uncompletedTasks = totalTasks - completedTasks;
        
        taskStats.put("uncompleted", uncompletedTasks);
        taskStats.put("completed", completedTasks);
        taskStats.put("other", 0);

        // 统计发版数据
        Map<String, Integer> releaseStats = new HashMap<>();
        int totalReleases = releaseMapper.countCreatedInDateRange(start_date, end_date);
        int completedReleases = releaseMapper.countCompletedInDateRange(start_date, end_date);
        int uncompletedReleases = totalReleases - completedReleases;
        
        releaseStats.put("uncompleted", uncompletedReleases);
        releaseStats.put("completed", completedReleases);
        releaseStats.put("other", 0);

        // 统计需求数据
        Map<String, Integer> requirementStats = new HashMap<>();
        int totalRequirements = requirementMapper.countCreatedInDateRange(start_date, end_date);
        int completedRequirements = requirementMapper.countCompletedInDateRange(start_date, end_date);
        int uncompletedRequirements = totalRequirements - completedRequirements;
        
        requirementStats.put("uncompleted", uncompletedRequirements);
        requirementStats.put("completed", completedRequirements);
        requirementStats.put("other", 0);

        // 统计缺陷数据
        Map<String, Integer> defectStats = new HashMap<>();
        int totalDefects = defectMapper.countCreatedInDateRange(start_date, end_date);
        int completedDefects = defectMapper.countCompletedInDateRange(start_date, end_date);
        int uncompletedDefects = totalDefects - completedDefects;
        
        defectStats.put("uncompleted", uncompletedDefects);
        defectStats.put("completed", completedDefects);
        defectStats.put("other", 0);

        // 统计我的工时数据
        Map<String, Integer> myHoursStats = new HashMap<>();
        int myUncompletedHours = taskMapper.countMyUncompletedTasks(user.getId(), getUncompletedStatusIds());
        int myCompletedHours = taskMapper.countMyCompletedTasks(user.getId(), completedStatusId != null ? 
            java.util.Arrays.asList(completedStatusId) : new java.util.ArrayList<>());
        
        myHoursStats.put("uncompleted", myUncompletedHours);
        myHoursStats.put("completed", myCompletedHours);
        myHoursStats.put("other", 0);

        // 构建响应
        Map<String, Object> result = new HashMap<>();
        result.put("task", taskStats);
        result.put("release", releaseStats);
        result.put("requirement", requirementStats);
        result.put("defect", defectStats);
        result.put("my_hours", myHoursStats);

        return ResponseEntity.ok(result);
    }

    @GetMapping("/user-workload")
    public ResponseEntity<?> getUserWorkload(
            @RequestParam(required = false) String start_date,
            @RequestParam(required = false) String end_date
    ) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        List<Map<String, Object>> workload = userMapper.getUserWorkload(start_date, end_date);

        return ResponseEntity.ok(workload);
    }

    @GetMapping("/project-progress")
    public ResponseEntity<?> getProjectProgress() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        // 获取已完成状态 ID
        Status completedStatus = statusMapper.findByName("已完成");
        Long completedStatusId = completedStatus != null ? completedStatus.getId() : null;

        // 统计总任务数
        int totalTasks = taskMapper.findAll().size();

        // 统计已完成任务数
        int completedTasks = 0;
        if (completedStatusId != null) {
            completedTasks = taskMapper.findByStatusId(completedStatusId).size();
        }

        // 计算完成率
        double completionRate = totalTasks > 0 ? 
            Math.round((double) completedTasks / totalTasks * 100) : 0;

        // 统计逾期任务数 (截止日期在今天之前且未完成的任务)
        int overdueTasks = 0;
        List<Task> allTasks = taskMapper.findAll();
        java.util.Date today = new java.util.Date();
        for (Task task : allTasks) {
            if (task.getDueDate() != null && task.getDueDate().before(today)) {
                // 任务未完成 (状态不是已完成)
                if (completedStatusId == null || !completedStatusId.equals(task.getStatusId())) {
                    overdueTasks++;
                }
            }
        }

        // 构建响应
        Map<String, Object> result = new HashMap<>();
        result.put("total_tasks", totalTasks);
        result.put("completed_tasks", completedTasks);
        result.put("completion_rate", completionRate);
        result.put("overdue_tasks", overdueTasks);

        return ResponseEntity.ok(result);
    }
}
