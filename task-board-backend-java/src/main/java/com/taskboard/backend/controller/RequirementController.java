package com.taskboard.backend.controller;

import com.taskboard.backend.annotation.RequirePermission;
import com.taskboard.backend.mapper.RequirementMapper;
import com.taskboard.backend.mapper.RequirementTagMapper;
import com.taskboard.backend.mapper.UserMapper;
import com.taskboard.backend.model.Requirement;
import com.taskboard.backend.model.RequirementTag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import javax.servlet.http.HttpServletResponse;
import java.net.URLEncoder;
import java.util.*;

@RestController
@RequestMapping("/api/requirements")
public class RequirementController {

    @Autowired
    private RequirementMapper requirementMapper;
    
    @Autowired
    private RequirementTagMapper requirementTagMapper;
    
    @Autowired
    private UserMapper userMapper;

    @GetMapping
    @RequirePermission("requirement:list")
    public ResponseEntity<?> getRequirements(
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String priority,
            @RequestParam(required = false) String created_by,
            @RequestParam(required = false) String search,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer page_size
    ) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        List<Requirement> requirements = requirementMapper.findAll();
        
        // 状态过滤 (支持多选)
        if (status != null && !status.isEmpty()) {
            List<String> statusList = java.util.Arrays.stream(status.split(","))
                .map(String::trim)
                .collect(java.util.stream.Collectors.toList());
            requirements = requirements.stream()
                .filter(req -> statusList.contains(req.getStatus()))
                .collect(java.util.stream.Collectors.toList());
        }
        
        // 优先级过滤
        if (priority != null && !priority.isEmpty()) {
            String finalPriority = priority;
            requirements = requirements.stream()
                .filter(req -> finalPriority.equals(req.getPriority()))
                .collect(java.util.stream.Collectors.toList());
        }
        
        // 创建人过滤
        if (created_by != null && !created_by.isEmpty()) {
            Long createdBy = Long.parseLong(created_by);
            requirements = requirements.stream()
                .filter(req -> req.getCreatedBy() != null && req.getCreatedBy().equals(createdBy))
                .collect(java.util.stream.Collectors.toList());
        }
        
        // 搜索过滤
        if (search != null && !search.isEmpty()) {
            String finalSearch = search.toLowerCase();
            requirements = requirements.stream()
                .filter(req -> {
                    if (req.getName() != null && req.getName().toLowerCase().contains(finalSearch)) {
                        return true;
                    }
                    if (req.getDescription() != null && req.getDescription().toLowerCase().contains(finalSearch)) {
                        return true;
                    }
                    return false;
                })
                .collect(java.util.stream.Collectors.toList());
        }

        // 分页处理
        int total = requirements.size();
        int fromIndex = (page - 1) * page_size;
        int toIndex = Math.min(fromIndex + page_size, total);
        
        List<Requirement> pagedRequirements;
        if (fromIndex < total) {
            pagedRequirements = requirements.subList(fromIndex, toIndex);
        } else {
            pagedRequirements = requirements;
        }

        // 构建响应数据
        Map<String, Object> response = new HashMap<>();
        response.put("items", pagedRequirements);
        response.put("total", total);
        response.put("page", page);
        response.put("page_size", page_size);

        return ResponseEntity.ok(response);
    }

    // 需求导出接口
    @GetMapping("/export")
    @RequirePermission("requirement:export")
    public void exportRequirements(
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String priority,
            @RequestParam(required = false) String created_by,
            @RequestParam(required = false) String search,
            HttpServletResponse response
    ) throws Exception {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            response.setStatus(401);
            return;
        }

        // 查询所有需求
        List<Requirement> requirements = requirementMapper.findAll();
        
        // 状态过滤 (支持多选)
        if (status != null && !status.isEmpty()) {
            List<String> statusList = java.util.Arrays.stream(status.split(","))
                .map(String::trim)
                .collect(java.util.stream.Collectors.toList());
            requirements = requirements.stream()
                .filter(req -> statusList.contains(req.getStatus()))
                .collect(java.util.stream.Collectors.toList());
        }
        
        // 优先级过滤
        if (priority != null && !priority.isEmpty()) {
            String finalPriority = priority;
            requirements = requirements.stream()
                .filter(req -> finalPriority.equals(req.getPriority()))
                .collect(java.util.stream.Collectors.toList());
        }
        
        // 创建人过滤
        if (created_by != null && !created_by.isEmpty()) {
            Long createdBy = Long.parseLong(created_by);
            requirements = requirements.stream()
                .filter(req -> req.getCreatedBy() != null && req.getCreatedBy().equals(createdBy))
                .collect(java.util.stream.Collectors.toList());
        }
        
        // 搜索过滤
        if (search != null && !search.isEmpty()) {
            String finalSearch = search.toLowerCase();
            requirements = requirements.stream()
                .filter(req -> {
                    if (req.getName() != null && req.getName().toLowerCase().contains(finalSearch)) {
                        return true;
                    }
                    if (req.getDescription() != null && req.getDescription().toLowerCase().contains(finalSearch)) {
                        return true;
                    }
                    return false;
                })
                .collect(java.util.stream.Collectors.toList());
        }

        // 创建工作簿
        org.apache.poi.ss.usermodel.Workbook workbook = new org.apache.poi.xssf.usermodel.XSSFWorkbook();
        org.apache.poi.ss.usermodel.Sheet sheet = workbook.createSheet("需求列表");
        
        // 创建标题行
        org.apache.poi.ss.usermodel.Row headerRow = sheet.createRow(0);
        String[] headers = {
            "需求 ID", "需求名称", "需求描述", "状态", "优先级",
            "创建人", "创建时间", "更新时间"
        };
        
        for (int i = 0; i < headers.length; i++) {
            org.apache.poi.ss.usermodel.Cell cell = headerRow.createCell(i);
            cell.setCellValue(headers[i]);
        }
        
        // 填充数据
        int rowNum = 1;
        for (Requirement requirement : requirements) {
            org.apache.poi.ss.usermodel.Row row = sheet.createRow(rowNum++);
            
            // 获取创建人名称
            String creatorName = "";
            if (requirement.getCreatedBy() != null) {
                com.taskboard.backend.model.User creator = userMapper.findById(requirement.getCreatedBy());
                if (creator != null) {
                    creatorName = creator.getName();
                }
            }
            
            row.createCell(0).setCellValue(requirement.getId());
            row.createCell(1).setCellValue(requirement.getName() != null ? requirement.getName() : "");
            row.createCell(2).setCellValue(requirement.getDescription() != null ? requirement.getDescription() : "");
            row.createCell(3).setCellValue(requirement.getStatus() != null ? requirement.getStatus() : "");
            row.createCell(4).setCellValue(requirement.getPriority() != null ? requirement.getPriority() : "");
            row.createCell(5).setCellValue(creatorName);
            row.createCell(6).setCellValue(requirement.getCreatedAt() != null ? new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(requirement.getCreatedAt()) : "");
            row.createCell(7).setCellValue(requirement.getUpdatedAt() != null ? new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(requirement.getUpdatedAt()) : "");
        }
        
        // 自动调整列宽
        for (int i = 0; i < headers.length; i++) {
            sheet.autoSizeColumn(i);
        }
        
        // 设置响应头
        response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
        response.setCharacterEncoding("utf-8");
        String fileName = "requirements_export_" + new java.text.SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date()) + ".xlsx";
        response.setHeader("Content-Disposition", "attachment; filename=" + URLEncoder.encode(fileName, "UTF-8"));
        
        // 写入输出流
        workbook.write(response.getOutputStream());
        workbook.close();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Requirement> getRequirementById(@PathVariable Long id) {
        Requirement requirement = requirementMapper.findById(id);
        if (requirement != null) {
            return ResponseEntity.ok(requirement);
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @PostMapping
    @RequirePermission("requirement:create")
    public ResponseEntity<?> createRequirement(@RequestBody Requirement requirement) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        com.taskboard.backend.model.User user = userMapper.findByUsername(username).orElse(null);
        if (user != null) {
            requirement.setCreatedBy(user.getId());
        }
        
        requirementMapper.insert(requirement);
        return ResponseEntity.ok(requirement);
    }

    @PutMapping("/{id}")
    @RequirePermission("requirement:update")
    public ResponseEntity<Requirement> updateRequirement(@PathVariable Long id, @RequestBody Requirement requirement) {
        Requirement existingRequirement = requirementMapper.findById(id);
        if (existingRequirement != null) {
            requirement.setId(id);
            requirementMapper.update(requirement);
            return ResponseEntity.ok(requirement);
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @DeleteMapping("/{id}")
    @RequirePermission("requirement:delete")
    public ResponseEntity<?> deleteRequirement(@PathVariable Long id) {
        Requirement requirement = requirementMapper.findById(id);
        if (requirement != null) {
            requirementMapper.delete(id);
            return ResponseEntity.ok().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @GetMapping("/requirement-tags")
    @RequirePermission("requirement_tag:list")
    public ResponseEntity<?> getRequirementTags() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        List<RequirementTag> tags = requirementTagMapper.findAll();
        return ResponseEntity.ok(tags);
    }
}