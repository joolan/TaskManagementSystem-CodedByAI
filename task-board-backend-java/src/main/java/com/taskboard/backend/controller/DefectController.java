package com.taskboard.backend.controller;

import com.taskboard.backend.annotation.RequirePermission;
import com.taskboard.backend.mapper.DefectMapper;
import com.taskboard.backend.mapper.UserMapper;
import com.taskboard.backend.model.Defect;
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
@RequestMapping("/api/defects")
public class DefectController {

    @Autowired
    private DefectMapper defectMapper;
    
    @Autowired
    private UserMapper userMapper;

    @GetMapping
    @RequirePermission("defect:list")
    public ResponseEntity<?> getDefects(
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String release_id,
            @RequestParam(required = false) String assignee_id,
            @RequestParam(required = false) String created_by,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer page_size
    ) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        List<Defect> defects = defectMapper.findAll();
        
        // 状态过滤 (支持多选)
        if (status != null && !status.isEmpty()) {
            List<String> statusList = java.util.Arrays.stream(status.split(","))
                .map(String::trim)
                .collect(java.util.stream.Collectors.toList());
            defects = defects.stream()
                .filter(defect -> statusList.contains(defect.getStatus()))
                .collect(java.util.stream.Collectors.toList());
        }
        
        // 来源版本过滤
        if (release_id != null && !release_id.isEmpty()) {
            Long rid = Long.parseLong(release_id);
            defects = defects.stream()
                .filter(defect -> defect.getReleaseId() != null && defect.getReleaseId().equals(rid))
                .collect(java.util.stream.Collectors.toList());
        }
        
        // 负责人过滤
        if (assignee_id != null && !assignee_id.isEmpty()) {
            Long aid = Long.parseLong(assignee_id);
            defects = defects.stream()
                .filter(defect -> defect.getAssigneeId() != null && defect.getAssigneeId().equals(aid))
                .collect(java.util.stream.Collectors.toList());
        }
        
        // 创建人过滤
        if (created_by != null && !created_by.isEmpty()) {
            Long cid = Long.parseLong(created_by);
            defects = defects.stream()
                .filter(defect -> defect.getCreatedBy() != null && defect.getCreatedBy().equals(cid))
                .collect(java.util.stream.Collectors.toList());
        }

        // 分页处理
        int total = defects.size();
        int fromIndex = (page - 1) * page_size;
        int toIndex = Math.min(fromIndex + page_size, total);
        
        List<Defect> pagedDefects;
        if (fromIndex < total) {
            pagedDefects = defects.subList(fromIndex, toIndex);
        } else {
            pagedDefects = defects;
        }

        // 构建响应数据
        Map<String, Object> response = new HashMap<>();
        response.put("items", pagedDefects);
        response.put("total", total);
        response.put("page", page);
        response.put("page_size", page_size);

        return ResponseEntity.ok(response);
    }

    // 缺陷导出接口
    @GetMapping("/export")
    @RequirePermission("defect:export")
    public void exportDefects(
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String release_id,
            @RequestParam(required = false) String assignee_id,
            @RequestParam(required = false) String created_by,
            HttpServletResponse response
    ) throws Exception {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            response.setStatus(401);
            return;
        }

        // 查询所有缺陷
        List<Defect> defects = defectMapper.findAll();
        
        // 状态过滤 (支持多选)
        if (status != null && !status.isEmpty()) {
            List<String> statusList = java.util.Arrays.stream(status.split(","))
                .map(String::trim)
                .collect(java.util.stream.Collectors.toList());
            defects = defects.stream()
                .filter(defect -> statusList.contains(defect.getStatus()))
                .collect(java.util.stream.Collectors.toList());
        }
        
        // 来源版本过滤
        if (release_id != null && !release_id.isEmpty()) {
            Long rid = Long.parseLong(release_id);
            defects = defects.stream()
                .filter(defect -> defect.getReleaseId() != null && defect.getReleaseId().equals(rid))
                .collect(java.util.stream.Collectors.toList());
        }
        
        // 负责人过滤
        if (assignee_id != null && !assignee_id.isEmpty()) {
            Long aid = Long.parseLong(assignee_id);
            defects = defects.stream()
                .filter(defect -> defect.getAssigneeId() != null && defect.getAssigneeId().equals(aid))
                .collect(java.util.stream.Collectors.toList());
        }
        
        // 创建人过滤
        if (created_by != null && !created_by.isEmpty()) {
            Long cid = Long.parseLong(created_by);
            defects = defects.stream()
                .filter(defect -> defect.getCreatedBy() != null && defect.getCreatedBy().equals(cid))
                .collect(java.util.stream.Collectors.toList());
        }

        // 创建工作簿
        org.apache.poi.ss.usermodel.Workbook workbook = new org.apache.poi.xssf.usermodel.XSSFWorkbook();
        org.apache.poi.ss.usermodel.Sheet sheet = workbook.createSheet("缺陷列表");
        
        // 创建标题行
        org.apache.poi.ss.usermodel.Row headerRow = sheet.createRow(0);
        String[] headers = {
            "缺陷 ID", "缺陷标题", "缺陷描述", "状态", "负责人",
            "来源版本", "创建人", "创建时间", "更新时间"
        };
        
        for (int i = 0; i < headers.length; i++) {
            org.apache.poi.ss.usermodel.Cell cell = headerRow.createCell(i);
            cell.setCellValue(headers[i]);
        }
        
        // 填充数据
        int rowNum = 1;
        for (Defect defect : defects) {
            org.apache.poi.ss.usermodel.Row row = sheet.createRow(rowNum++);
            
            // 获取负责人名称
            String assigneeName = "";
            if (defect.getAssigneeId() != null) {
                com.taskboard.backend.model.User assignee = userMapper.findById(defect.getAssigneeId());
                if (assignee != null) {
                    assigneeName = assignee.getName();
                }
            }
            
            // 获取创建人名称
            String creatorName = "";
            if (defect.getCreatedBy() != null) {
                com.taskboard.backend.model.User creator = userMapper.findById(defect.getCreatedBy());
                if (creator != null) {
                    creatorName = creator.getName();
                }
            }
            
            row.createCell(0).setCellValue(defect.getId());
            row.createCell(1).setCellValue(defect.getTitle() != null ? defect.getTitle() : "");
            row.createCell(2).setCellValue(defect.getDescription() != null ? defect.getDescription() : "");
            row.createCell(3).setCellValue(defect.getStatus() != null ? defect.getStatus() : "");
            row.createCell(4).setCellValue(assigneeName);
            row.createCell(5).setCellValue(defect.getReleaseId() != null ? defect.getReleaseId().toString() : "");
            row.createCell(6).setCellValue(creatorName);
            row.createCell(7).setCellValue(defect.getCreatedAt() != null ? new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(defect.getCreatedAt()) : "");
            row.createCell(8).setCellValue(defect.getUpdatedAt() != null ? new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(defect.getUpdatedAt()) : "");
        }
        
        // 自动调整列宽
        for (int i = 0; i < headers.length; i++) {
            sheet.autoSizeColumn(i);
        }
        
        // 设置响应头
        response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
        response.setCharacterEncoding("utf-8");
        String fileName = "defects_export_" + new java.text.SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date()) + ".xlsx";
        response.setHeader("Content-Disposition", "attachment; filename=" + URLEncoder.encode(fileName, "UTF-8"));
        
        // 写入输出流
        workbook.write(response.getOutputStream());
        workbook.close();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Defect> getDefectById(@PathVariable Long id) {
        Defect defect = defectMapper.findById(id);
        if (defect != null) {
            return ResponseEntity.ok(defect);
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @PostMapping
    @RequirePermission("defect:create")
    public ResponseEntity<?> createDefect(@RequestBody Defect defect) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        com.taskboard.backend.model.User user = userMapper.findByUsername(username).orElse(null);
        if (user != null) {
            defect.setCreatedBy(user.getId());
        }
        
        defectMapper.insert(defect);
        return ResponseEntity.ok(defect);
    }

    @PutMapping("/{id}")
    @RequirePermission("defect:update")
    public ResponseEntity<Defect> updateDefect(@PathVariable Long id, @RequestBody Defect defect) {
        Defect existingDefect = defectMapper.findById(id);
        if (existingDefect != null) {
            defect.setId(id);
            defectMapper.update(defect);
            return ResponseEntity.ok(defect);
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @DeleteMapping("/{id}")
    @RequirePermission("defect:delete")
    public ResponseEntity<?> deleteDefect(@PathVariable Long id) {
        Defect defect = defectMapper.findById(id);
        if (defect != null) {
            defectMapper.delete(id);
            return ResponseEntity.ok().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }
}