package com.taskboard.backend.controller;

import com.taskboard.backend.annotation.RequirePermission;
import com.taskboard.backend.mapper.*;
import com.taskboard.backend.model.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import org.springframework.web.multipart.MultipartFile;

import javax.servlet.http.HttpServletResponse;
import java.io.File;
import java.io.IOException;
import java.net.URLEncoder;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

@RestController
@RequestMapping("/api/tasks")
public class TaskController {

    @Autowired
    private TaskMapper taskMapper;
    
    @Autowired
    private UserMapper userMapper;
    
    @Autowired
    private TaskFollowMapper taskFollowMapper;
    
    @Autowired
    private TagMapper tagMapper;
    
    @Autowired
    private TaskHourMapper taskHourMapper;
    
    @Autowired
    private StatusMapper statusMapper;
    
    @Autowired
    private AttachmentMapper attachmentMapper;
    
    @Autowired
    private CommentMapper commentMapper;
    
    /**
     * 解析 ISO 8601 日期字符串为 Date 对象
     */
    private Date parseDate(String dateStr) {
        if (dateStr == null || dateStr.isEmpty()) {
            return null;
        }
        try {
            // 尝试解析 ISO 8601 格式：2026-03-03T12:57:34.468+00:00
            if (dateStr.contains("T")) {
                // 移除时区信息，只保留日期时间部分
                int tIndex = dateStr.indexOf('T');
                int plusIndex = dateStr.indexOf('+', tIndex);
                if (plusIndex > 0) {
                    dateStr = dateStr.substring(0, plusIndex);
                }
                dateStr = dateStr.replace('T', ' ');
                // 移除毫秒部分（如果有）
                int dotIndex = dateStr.indexOf('.');
                if (dotIndex > 0) {
                    dateStr = dateStr.substring(0, dotIndex);
                }
            }
            // 使用 SimpleDateFormat 解析
            java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
            return sdf.parse(dateStr);
        } catch (Exception e) {
            // 如果解析失败，尝试直接解析日期部分
            try {
                java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat("yyyy-MM-dd");
                return sdf.parse(dateStr);
            } catch (Exception e2) {
                return null;
            }
        }
    }
    
    @Autowired
    private TaskLogMapper taskLogMapper;

    @GetMapping
    //@RequirePermission("task:list")
    public ResponseEntity<?> getTasks(
            @RequestParam(required = false) String status_id,
            @RequestParam(required = false) String priority,
            @RequestParam(required = false) String follow_status,
            @RequestParam(required = false) String assignee_id,
            @RequestParam(required = false) String search,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer page_size
    ) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User currentUser = userMapper.findByUsername(username).orElse(null);
        
        // 执行查询
        List<Task> tasks = taskMapper.findAll();
        
        // 状态过滤
        if (status_id != null && !status_id.isEmpty()) {
            List<Long> statusIds = java.util.Arrays.stream(status_id.split(","))
                .map(String::trim)
                .map(Long::parseLong)
                .collect(java.util.stream.Collectors.toList());
            tasks = tasks.stream()
                .filter(task -> statusIds.contains(task.getStatusId()))
                .collect(java.util.stream.Collectors.toList());
        }
        
        // 优先级过滤
        if (priority != null && !priority.isEmpty()) {
            String finalPriority = priority;
            tasks = tasks.stream()
                .filter(task -> finalPriority.equals(task.getPriority()))
                .collect(java.util.stream.Collectors.toList());
        }
        
        // 我的关注过滤
        if (follow_status != null && !follow_status.isEmpty() && currentUser != null) {
            List<Long> followedTaskIds = taskFollowMapper.findFollowedTaskIds(currentUser.getId());
            if ("followed".equals(follow_status)) {
                tasks = tasks.stream()
                    .filter(task -> followedTaskIds.contains(task.getId()))
                    .collect(java.util.stream.Collectors.toList());
            } else if ("unfollowed".equals(follow_status)) {
                tasks = tasks.stream()
                    .filter(task -> !followedTaskIds.contains(task.getId()))
                    .collect(java.util.stream.Collectors.toList());
            }
        }
        
        // 负责人过滤
        if (assignee_id != null && !assignee_id.isEmpty()) {
            Long assigneeId = Long.parseLong(assignee_id);
            tasks = tasks.stream()
                .filter(task -> {
                    if (task.getAssigneeId() != null && task.getAssigneeId().equals(assigneeId)) {
                        return true;
                    }
                    if (task.getAssignees() != null) {
                        for (User assignee : task.getAssignees()) {
                            if (assignee.getId().equals(assigneeId)) {
                                return true;
                            }
                        }
                    }
                    return false;
                })
                .collect(java.util.stream.Collectors.toList());
        }
        
        // 搜索过滤
        if (search != null && !search.isEmpty()) {
            String finalSearch = search.toLowerCase();
            tasks = tasks.stream()
                .filter(task -> {
                    if (task.getTitle() != null && task.getTitle().toLowerCase().contains(finalSearch)) {
                        return true;
                    }
                    if (task.getDescription() != null && task.getDescription().toLowerCase().contains(finalSearch)) {
                        return true;
                    }
                    return false;
                })
                .collect(java.util.stream.Collectors.toList());
        }

        // 分页处理
        int total = tasks.size();
        int fromIndex = (page - 1) * page_size;
        int toIndex = Math.min(fromIndex + page_size, total);
        
        List<Task> pagedTasks;
        if (fromIndex < total) {
            pagedTasks = tasks.subList(fromIndex, toIndex);
        } else {
            pagedTasks = tasks;
        }

        // 构建响应数据
        Map<String, Object> response = new HashMap<>();
        response.put("items", pagedTasks);
        response.put("total", total);
        response.put("page", page);
        response.put("page_size", page_size);

        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Task> getTaskById(@PathVariable Long id) {
        Task task = taskMapper.findById(id);
        if (task != null) {
            return ResponseEntity.ok(task);
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @PostMapping
    @RequirePermission("task:create")
    public Task createTask(@RequestBody Task task) {
        taskMapper.insert(task);
        return task;
    }

    @PutMapping("/{id}")
    @RequirePermission("task:update")
    public ResponseEntity<Task> updateTask(@PathVariable Long id, @RequestBody Map<String, Object> taskUpdate) {
        Task existingTask = taskMapper.findById(id);
        if (existingTask != null) {
            // 更新任务字段
            if (taskUpdate.containsKey("title")) {
                existingTask.setTitle((String) taskUpdate.get("title"));
            }
            if (taskUpdate.containsKey("description")) {
                existingTask.setDescription((String) taskUpdate.get("description"));
            }
            if (taskUpdate.containsKey("status_id")) {
                Object statusIdObj = taskUpdate.get("status_id");
                if (statusIdObj != null) {
                    existingTask.setStatusId(Long.valueOf(statusIdObj.toString()));
                }
            }
            // 处理 assignee_id（单个）
            if (taskUpdate.containsKey("assignee_id")) {
                Object assigneeIdObj = taskUpdate.get("assignee_id");
                if (assigneeIdObj != null) {
                    existingTask.setAssigneeId(Long.valueOf(assigneeIdObj.toString()));
                }
            }
            // 处理 assignee_ids（数组）- 取第一个作为 assignee_id
            if (taskUpdate.containsKey("assignee_ids")) {
                Object assigneeIdsObj = taskUpdate.get("assignee_ids");
                if (assigneeIdsObj instanceof List) {
                    List<?> assigneeIds = (List<?>) assigneeIdsObj;
                    if (!assigneeIds.isEmpty()) {
                        existingTask.setAssigneeId(Long.valueOf(assigneeIds.get(0).toString()));
                    }
                }
            }
            if (taskUpdate.containsKey("priority")) {
                existingTask.setPriority((String) taskUpdate.get("priority"));
            }
            if (taskUpdate.containsKey("due_date")) {
                Object dueDateObj = taskUpdate.get("due_date");
                if (dueDateObj != null) {
                    existingTask.setDueDate(parseDate(dueDateObj.toString()));
                }
            }
            if (taskUpdate.containsKey("actual_start_date")) {
                Object actualStartDateObj = taskUpdate.get("actual_start_date");
                if (actualStartDateObj != null) {
                    existingTask.setActualStartDate(parseDate(actualStartDateObj.toString()));
                }
            }
            if (taskUpdate.containsKey("actual_completion_date")) {
                Object actualCompletionDateObj = taskUpdate.get("actual_completion_date");
                if (actualCompletionDateObj != null) {
                    existingTask.setActualCompletionDate(parseDate(actualCompletionDateObj.toString()));
                }
            }
            if (taskUpdate.containsKey("estimated_hours")) {
                Object estimatedHoursObj = taskUpdate.get("estimated_hours");
                if (estimatedHoursObj != null) {
                    existingTask.setEstimatedHours(Double.valueOf(estimatedHoursObj.toString()));
                }
            }
            if (taskUpdate.containsKey("actual_hours")) {
                Object actualHoursObj = taskUpdate.get("actual_hours");
                if (actualHoursObj != null) {
                    existingTask.setActualHours(Double.valueOf(actualHoursObj.toString()));
                }
            }
            
            // 执行更新
            taskMapper.update(existingTask);
            
            // 处理标签更新
            if (taskUpdate.containsKey("tag_ids")) {
                Object tagIdsObj = taskUpdate.get("tag_ids");
                if (tagIdsObj instanceof List) {
                    List<?> tagIds = (List<?>) tagIdsObj;
                    // 先删除现有的标签关联
                    taskMapper.deleteTaskTags(id);
                    // 添加新的标签关联
                    for (Object tagId : tagIds) {
                        if (tagId != null) {
                            taskMapper.insertTaskTag(id, Long.valueOf(tagId.toString()));
                        }
                    }
                }
            }
            
            // 重新查询完整的任务数据（包含关联对象）
            Task updatedTask = taskMapper.findById(id);
            return ResponseEntity.ok(updatedTask);
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @DeleteMapping("/{id}")
    @RequirePermission("task:delete")
    public ResponseEntity<Void> deleteTask(@PathVariable Long id) {
        Task task = taskMapper.findById(id);
        if (task != null) {
            taskMapper.delete(id);
            return ResponseEntity.ok().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    // 任务关注相关接口
    @PostMapping("/{task_id}/follow")
    @RequirePermission("task:follow")
    public ResponseEntity<?> followTask(@PathVariable Long task_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User currentUser = userMapper.findByUsername(username).orElse(null);
        if (currentUser == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        // 检查任务是否存在
        Task task = taskMapper.findById(task_id);
        if (task == null) {
            return ResponseEntity.status(404).body("Task not found");
        }

        // 检查是否已经关注
        TaskFollow existingFollow = taskFollowMapper.findByTaskIdAndUserId(task_id, currentUser.getId());
        if (existingFollow != null) {
            return ResponseEntity.badRequest().body("Already following this task");
        }

        // 创建关注记录
        TaskFollow taskFollow = new TaskFollow();
        Task taskRef = new Task();
        taskRef.setId(task_id);
        taskFollow.setTask(taskRef);
        taskFollow.setTaskId(task_id);
        
        User userRef = new User();
        userRef.setId(currentUser.getId());
        taskFollow.setUser(userRef);
        taskFollow.setUserId(currentUser.getId());
        
        taskFollow.setCreatedAt(new Date());
        
        taskFollowMapper.insert(taskFollow);

        return ResponseEntity.ok(taskFollow);
    }

    @DeleteMapping("/{task_id}/follow")
    public ResponseEntity<?> unfollowTask(@PathVariable Long task_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User currentUser = userMapper.findByUsername(username).orElse(null);
        if (currentUser == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        // 删除关注记录
        taskFollowMapper.deleteByTaskIdAndUserId(task_id, currentUser.getId());

        return ResponseEntity.ok().build();
    }

    @GetMapping("/{task_id}/followers")
    public ResponseEntity<?> getTaskFollowers(@PathVariable Long task_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        // 检查任务是否存在
        Task task = taskMapper.findById(task_id);
        if (task == null) {
            return ResponseEntity.status(404).body("Task not found");
        }

        List<TaskFollow> followers = taskFollowMapper.findByTaskId(task_id);
        
        // 构建返回结果
        List<Map<String, Object>> followerList = new ArrayList<>();
        for (TaskFollow follow : followers) {
            User user = follow.getUser();
            if (user != null) {
                Map<String, Object> followerInfo = new HashMap<>();
                followerInfo.put("id", user.getId());
                followerInfo.put("username", user.getUsername());
                followerInfo.put("name", user.getName());
                followerList.add(followerInfo);
            }
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("followers", followerList);
        
        return ResponseEntity.ok(result);
    }

    // 任务工时相关接口
    @PostMapping("/{task_id}/hours")
    @RequirePermission("task:add_hours")
    public ResponseEntity<?> addTaskHours(@PathVariable Long task_id, @RequestBody Map<String, Object> hoursData) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User currentUser = userMapper.findByUsername(username).orElse(null);
        if (currentUser == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        // 检查任务是否存在
        Task task = taskMapper.findById(task_id);
        if (task == null) {
            return ResponseEntity.status(404).body("Task not found");
        }

        // 获取请求参数
        List<Integer> userIds = (List<Integer>) hoursData.get("user_ids");
        Double hours = ((Number) hoursData.get("hours")).doubleValue();
        String remark = (String) hoursData.get("remark");

        if (userIds == null || userIds.isEmpty()) {
            return ResponseEntity.badRequest().body("user_ids is required");
        }

        // 为每个用户添加工时记录
        List<TaskHour> taskHours = new ArrayList<>();
        for (Integer userId : userIds) {
            User user = userMapper.findById(userId.longValue());
            if (user == null) {
                return ResponseEntity.badRequest().body("User not found: " + userId);
            }

            TaskHour taskHour = new TaskHour();
            Task taskRef = new Task();
            taskRef.setId(task_id);
            taskHour.setTask(taskRef);
            taskHour.setTaskId(task_id);
            
            User userRef = new User();
            userRef.setId(userId.longValue());
            taskHour.setUser(userRef);
            taskHour.setUserId(userId.longValue());
            
            taskHour.setHours(hours);
            taskHour.setRemark(remark);
            
            User creatorRef = new User();
            creatorRef.setId(currentUser.getId());
            taskHour.setCreator(creatorRef);
            taskHour.setCreatedById(currentUser.getId());
            
            taskHour.setCreatedAt(new Date());
            
            taskHourMapper.insert(taskHour);
            taskHours.add(taskHour);
        }

        // 创建任务日志
        StringBuilder logContent = new StringBuilder();
        logContent.append("填报了工时：").append(hours).append(" 小时\n");
        
        List<String> userNames = new ArrayList<>();
        for (TaskHour th : taskHours) {
            userNames.add(th.getUser().getName());
        }
        logContent.append("涉及人员：").append(String.join(", ", userNames));

        TaskLog log = new TaskLog();
        Task taskRef = new Task();
        taskRef.setId(task_id);
        log.setTask(taskRef);
        log.setTaskId(task_id);
        
        User userRef = new User();
        userRef.setId(currentUser.getId());
        log.setUser(userRef);
        log.setUserId(currentUser.getId());
        
        log.setActionType("update");
        log.setTitle("工时填报");
        log.setContent(logContent.toString());
        log.setCreatedAt(new Date());
        taskLogMapper.insert(log);

        return ResponseEntity.ok(taskHours);
    }

    @GetMapping("/{task_id}/hours")
    public ResponseEntity<?> getTaskHours(@PathVariable Long task_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        List<TaskHour> taskHours = taskHourMapper.findByTaskId(task_id);
        
        // 计算总工时
        double totalHours = 0;
        for (TaskHour th : taskHours) {
            if (th.getHours() != null) {
                totalHours += th.getHours();
            }
        }

        Map<String, Object> result = new HashMap<>();
        result.put("total_hours", totalHours);
        result.put("hours_list", taskHours);
        
        return ResponseEntity.ok(result);
    }

    // 任务导出接口
    @GetMapping("/export")
    @RequirePermission("task:export")
    public void exportTasks(
            @RequestParam(required = false) String status_id,
            @RequestParam(required = false) String priority,
            @RequestParam(required = false) String search,
            HttpServletResponse response
    ) throws Exception {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            response.setStatus(401);
            return;
        }

        // 查询所有任务
        List<Task> tasks = taskMapper.findAll();
        
        // 状态过滤 (支持多选)
        if (status_id != null && !status_id.isEmpty()) {
            List<Long> statusIds = java.util.Arrays.stream(status_id.split(","))
                .map(String::trim)
                .map(Long::parseLong)
                .collect(java.util.stream.Collectors.toList());
            tasks = tasks.stream()
                .filter(task -> statusIds.contains(task.getStatusId()))
                .collect(java.util.stream.Collectors.toList());
        }
        
        // 优先级过滤
        if (priority != null && !priority.isEmpty()) {
            String finalPriority = priority;
            tasks = tasks.stream()
                .filter(task -> finalPriority.equals(task.getPriority()))
                .collect(java.util.stream.Collectors.toList());
        }
        
        // 搜索过滤
        if (search != null && !search.isEmpty()) {
            String finalSearch = search.toLowerCase();
            tasks = tasks.stream()
                .filter(task -> {
                    if (task.getTitle() != null && task.getTitle().toLowerCase().contains(finalSearch)) {
                        return true;
                    }
                    if (task.getDescription() != null && task.getDescription().toLowerCase().contains(finalSearch)) {
                        return true;
                    }
                    return false;
                })
                .collect(java.util.stream.Collectors.toList());
        }

        // 创建工作簿
        Workbook workbook = new XSSFWorkbook();
        Sheet sheet = workbook.createSheet("任务列表");
        
        // 创建标题行
        Row headerRow = sheet.createRow(0);
        String[] headers = {
            "任务 ID", "任务标题", "任务描述", "任务状态", "负责人",
            "优先级", "截止日期", "实际开始日期", "实际完成日期",
            "预估工时", "实际工时", "标签", "创建人", "创建时间", "更新时间"
        };
        
        for (int i = 0; i < headers.length; i++) {
            Cell cell = headerRow.createCell(i);
            cell.setCellValue(headers[i]);
        }
        
        // 填充数据
        int rowNum = 1;
        for (Task task : tasks) {
            Row row = sheet.createRow(rowNum++);
            
            // 收集负责人名称
            String assigneesStr = "未分配";
            if (task.getAssigneeId() != null) {
                User assignee = userMapper.findById(task.getAssigneeId());
                if (assignee != null) {
                    assigneesStr = assignee.getName();
                }
            }
            
            // 收集标签名称
            String tagsStr = "无";
            List<TaskTag> taskTags = taskMapper.findTaskTagsByTaskId(task.getId());
            if (taskTags != null && !taskTags.isEmpty()) {
                List<String> tagNames = new ArrayList<>();
                for (TaskTag taskTag : taskTags) {
                    if (taskTag.getTag() != null) {
                        tagNames.add(taskTag.getTag().getName());
                    }
                }
                if (!tagNames.isEmpty()) {
                    tagsStr = String.join(", ", tagNames);
                }
            }
            
            // 获取状态名称
            String statusName = "";
            if (task.getStatusId() != null) {
                Status status = statusMapper.findById(task.getStatusId());
                if (status != null) {
                    statusName = status.getName();
                }
            }
            
            row.createCell(0).setCellValue(task.getId());
            row.createCell(1).setCellValue(task.getTitle() != null ? task.getTitle() : "");
            row.createCell(2).setCellValue(task.getDescription() != null ? task.getDescription() : "");
            row.createCell(3).setCellValue(statusName);
            row.createCell(4).setCellValue(assigneesStr);
            row.createCell(5).setCellValue(task.getPriority() != null ? task.getPriority() : "");
            row.createCell(6).setCellValue(task.getDueDate() != null ? new java.text.SimpleDateFormat("yyyy-MM-dd").format(task.getDueDate()) : "");
            row.createCell(7).setCellValue(task.getActualStartDate() != null ? new java.text.SimpleDateFormat("yyyy-MM-dd").format(task.getActualStartDate()) : "");
            row.createCell(8).setCellValue(task.getActualCompletionDate() != null ? new java.text.SimpleDateFormat("yyyy-MM-dd").format(task.getActualCompletionDate()) : "");
            row.createCell(9).setCellValue(task.getEstimatedHours() != null ? task.getEstimatedHours() : 0);
            row.createCell(10).setCellValue(task.getActualHours() != null ? task.getActualHours() : 0);
            row.createCell(11).setCellValue(tagsStr);
            row.createCell(12).setCellValue(task.getCreator() != null && task.getCreator().getName() != null ? task.getCreator().getName() : "");
            row.createCell(13).setCellValue(task.getCreatedAt() != null ? new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(task.getCreatedAt()) : "");
            row.createCell(14).setCellValue(task.getUpdatedAt() != null ? new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(task.getUpdatedAt()) : "");
        }
        
        // 自动调整列宽
        for (int i = 0; i < headers.length; i++) {
            sheet.autoSizeColumn(i);
        }
        
        // 设置响应头
        response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
        response.setCharacterEncoding("utf-8");
        String fileName = "tasks_export_" + new java.text.SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date()) + ".xlsx";
        response.setHeader("Content-Disposition", "attachment; filename=" + URLEncoder.encode(fileName, "UTF-8"));
        
        // 写入输出流
        workbook.write(response.getOutputStream());
        workbook.close();
    }

    // 任务评论相关接口
    @GetMapping("/{task_id}/comments")
    public ResponseEntity<?> getTaskComments(@PathVariable Long task_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        List<com.taskboard.backend.model.Comment> comments = commentMapper.findByTaskId(task_id);
        
        // 为每个评论填充 user 和 attachments 信息
        for (com.taskboard.backend.model.Comment comment : comments) {
            // 填充 user 信息
            if (comment.getUserId() != null && comment.getIsAnonymous() == 0) {
                User user = userMapper.findById(comment.getUserId());
                comment.setUser(user);
            } else {
                comment.setUser(null);
            }
            
            // 填充 attachments 信息
            if (comment.getId() != null) {
                List<com.taskboard.backend.model.Attachment> attachments = attachmentMapper.findByCommentId(comment.getId());
                comment.setAttachments(attachments);
            } else {
                comment.setAttachments(new ArrayList<>());
            }
        }
        
        return ResponseEntity.ok(comments);
    }

    @PostMapping("/{task_id}/comments")
    public ResponseEntity<?> createTaskComment(@PathVariable Long task_id, @RequestBody Map<String, Object> commentData) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User user = userMapper.findByUsername(username).orElse(null);
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        // 检查任务是否存在
        Task task = taskMapper.findById(task_id);
        if (task == null) {
            return ResponseEntity.status(404).body("Task not found");
        }

        // 获取请求参数
        String content = (String) commentData.get("content");
        Object attachmentIdsObj = commentData.get("attachment_ids");
        Object isAnonymousObj = commentData.get("is_anonymous");
        Integer isAnonymous = 0;
        if (isAnonymousObj != null) {
            if (isAnonymousObj instanceof Boolean) {
                isAnonymous = ((Boolean) isAnonymousObj) ? 1 : 0;
            } else if (isAnonymousObj instanceof Number) {
                isAnonymous = ((Number) isAnonymousObj).intValue();
            }
        }

        if (content == null || content.isEmpty()) {
            return ResponseEntity.badRequest().body("content is required");
        }

        // 创建评论
        com.taskboard.backend.model.Comment comment = new com.taskboard.backend.model.Comment();
        Task taskRef = new Task();
        taskRef.setId(task_id);
        comment.setTask(taskRef);
        comment.setTaskId(task_id);
        
        User userRef = new User();
        userRef.setId(user.getId());
        comment.setUser(userRef);
        comment.setUserId(user.getId());
        
        comment.setContent(content);
        comment.setIsAnonymous(isAnonymous);
        comment.setCreatedAt(new Date());
        
        commentMapper.insert(comment);
        
        // 处理附件关联
        if (attachmentIdsObj != null && attachmentIdsObj instanceof List) {
            List<Integer> attachmentIds = (List<Integer>) attachmentIdsObj;
            for (Integer attachmentId : attachmentIds) {
                com.taskboard.backend.model.Attachment attachment = attachmentMapper.findById(attachmentId.longValue());
                if (attachment != null) {
                    attachment.setCommentId(comment.getId());
                    attachmentMapper.update(attachment);
                }
            }
        }
        
        // 重新查询评论，返回完整数据
        com.taskboard.backend.model.Comment createdComment = commentMapper.findById(comment.getId());
        if (createdComment != null) {
            // 填充 user 信息
            if (createdComment.getUserId() != null && createdComment.getIsAnonymous() == 0) {
                User creator = userMapper.findById(createdComment.getUserId());
                createdComment.setUser(creator);
            } else {
                createdComment.setUser(null);
            }
            
            // 填充 attachments 信息
            List<com.taskboard.backend.model.Attachment> attachments = attachmentMapper.findByCommentId(createdComment.getId());
            createdComment.setAttachments(attachments);
        }

        return ResponseEntity.ok(createdComment);
    }

    // 任务附件相关接口
    @GetMapping("/{task_id}/attachments")
    public ResponseEntity<?> getTaskAttachments(@PathVariable Long task_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        List<com.taskboard.backend.model.Attachment> attachments = attachmentMapper.findByTaskId(task_id);
        
        // 为每个附件填充 user 信息
        for (com.taskboard.backend.model.Attachment attachment : attachments) {
            if (attachment.getUserId() != null) {
                User user = userMapper.findById(attachment.getUserId());
                attachment.setUser(user);
            }
        }
        
        return ResponseEntity.ok(attachments);
    }

    @PostMapping("/{task_id}/attachments")
    public ResponseEntity<?> uploadTaskAttachment(
            @PathVariable Long task_id,
            @RequestParam("file") MultipartFile file) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User user = userMapper.findByUsername(username).orElse(null);
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        // 检查任务是否存在
        Task task = taskMapper.findById(task_id);
        if (task == null) {
            return ResponseEntity.status(404).body("Task not found");
        }

        // 检查文件是否为空
        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body("File is required");
        }

        try {
            // 创建上传目录
            String uploadDir = "uploads";
            File dir = new File(uploadDir);
            if (!dir.exists()) {
                dir.mkdirs();
            }

            // 生成唯一文件名
            String originalFilename = file.getOriginalFilename();
            String fileExtension = "";
            if (originalFilename != null && originalFilename.contains(".")) {
                fileExtension = originalFilename.substring(originalFilename.lastIndexOf("."));
            }
            String uniqueFilename = UUID.randomUUID().toString() + fileExtension;
            String filePath = Paths.get(uploadDir, uniqueFilename).toString();

            // 保存文件
            Path path = Paths.get(filePath);
            Files.write(path, file.getBytes());

            // 创建附件记录
            com.taskboard.backend.model.Attachment attachment = new com.taskboard.backend.model.Attachment();
            attachment.setTaskId(task_id);
            attachment.setUserId(user.getId());
            attachment.setFilename(originalFilename);
            attachment.setFilePath(filePath);
            attachment.setCreatedAt(new Date());

            attachmentMapper.insert(attachment);

            // 重新查询附件，返回完整数据
            com.taskboard.backend.model.Attachment createdAttachment = attachmentMapper.findById(attachment.getId());
            if (createdAttachment != null) {
                User creator = userMapper.findById(createdAttachment.getUserId());
                createdAttachment.setUser(creator);
            }

            return ResponseEntity.ok(createdAttachment);
        } catch (IOException e) {
            return ResponseEntity.status(500).body("Failed to upload file: " + e.getMessage());
        }
    }

    @GetMapping("/attachments/{attachment_id}/download")
    public ResponseEntity<?> downloadAttachment(@PathVariable Long attachment_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        com.taskboard.backend.model.Attachment attachment = attachmentMapper.findById(attachment_id);
        if (attachment == null) {
            return ResponseEntity.status(404).body("Attachment not found");
        }

        // 检查文件是否存在
        File file = new File(attachment.getFilePath());
        if (!file.exists()) {
            return ResponseEntity.status(404).body("File not found");
        }

        try {
            // 返回文件
            byte[] fileContent = Files.readAllBytes(file.toPath());
            
            Map<String, Object> response = new HashMap<>();
            response.put("filename", attachment.getFilename());
            response.put("content", Base64.getEncoder().encodeToString(fileContent));
            
            return ResponseEntity.ok(response);
        } catch (IOException e) {
            return ResponseEntity.status(500).body("Failed to download file: " + e.getMessage());
        }
    }

    @DeleteMapping("/attachments/{attachment_id}")
    public ResponseEntity<?> deleteAttachment(@PathVariable Long attachment_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User user = userMapper.findByUsername(username).orElse(null);
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        com.taskboard.backend.model.Attachment attachment = attachmentMapper.findById(attachment_id);
        if (attachment == null) {
            return ResponseEntity.status(404).body("Attachment not found");
        }

        // 检查权限 (只有上传者或管理员可以删除)
        if (!attachment.getUserId().equals(user.getId()) && !"admin".equals(username)) {
            return ResponseEntity.status(403).body("Not enough permissions");
        }

        // 删除文件
        File file = new File(attachment.getFilePath());
        if (file.exists()) {
            file.delete();
        }

        // 删除附件记录
        attachmentMapper.delete(attachment_id);

        return ResponseEntity.ok().build();
    }

    // 任务日志相关接口
    @GetMapping("/{task_id}/logs")
    public ResponseEntity<?> getTaskLogs(@PathVariable Long task_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        List<TaskLog> logs = taskLogMapper.findByTaskId(task_id);
        return ResponseEntity.ok(logs);
    }

    // 任务关注状态接口
    @GetMapping("/{task_id}/follow-status")
    public ResponseEntity<?> getTaskFollowStatus(@PathVariable Long task_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User user = userMapper.findByUsername(username).orElse(null);
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        // 检查是否关注
        TaskFollow follow = taskFollowMapper.findByTaskIdAndUserId(task_id, user.getId());
        Map<String, Object> result = new HashMap<>();
        result.put("is_following", follow != null);
        return ResponseEntity.ok(result);
    }

    // 任务标签接口
    @GetMapping("/tags/all")
    public ResponseEntity<?> getAllTags() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        List<Tag> tags = tagMapper.findAll();
        return ResponseEntity.ok(tags);
    }
}
