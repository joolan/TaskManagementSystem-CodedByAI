package com.taskboard.backend.controller;

import com.taskboard.backend.annotation.RequirePermission;
import com.taskboard.backend.mapper.ReleaseMapper;
import com.taskboard.backend.mapper.ReleaseFollowMapper;
import com.taskboard.backend.mapper.ReleaseTagMapper;
import com.taskboard.backend.mapper.UserMapper;
import com.taskboard.backend.model.Release;
import com.taskboard.backend.model.ReleaseTag;
import com.taskboard.backend.model.User;
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
@RequestMapping("/api/releases")
public class ReleaseController {

    @Autowired
    private ReleaseMapper releaseMapper;
    
    @Autowired
    private ReleaseTagMapper releaseTagMapper;
    
    @Autowired
    private UserMapper userMapper;
    
    @Autowired
    private ReleaseFollowMapper releaseFollowMapper;

    @GetMapping
    //@RequirePermission("release:list")
    public ResponseEntity<?> getReleases(
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String follow_status,
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

        List<Release> releases = releaseMapper.findAll();
        
        // 状态过滤 (支持多选)
        if (status != null && !status.isEmpty()) {
            List<String> statusList = java.util.Arrays.stream(status.split(","))
                .map(String::trim)
                .collect(java.util.stream.Collectors.toList());
            releases = releases.stream()
                .filter(release -> statusList.contains(release.getStatus()))
                .collect(java.util.stream.Collectors.toList());
        }
        
        // 我的关注过滤
        if (follow_status != null && !follow_status.isEmpty() && currentUser != null) {
            List<Long> followedReleaseIds = releaseFollowMapper.findFollowedReleaseIds(currentUser.getId());
            if ("followed".equals(follow_status)) {
                releases = releases.stream()
                    .filter(release -> followedReleaseIds.contains(release.getId()))
                    .collect(java.util.stream.Collectors.toList());
            } else if ("unfollowed".equals(follow_status)) {
                releases = releases.stream()
                    .filter(release -> !followedReleaseIds.contains(release.getId()))
                    .collect(java.util.stream.Collectors.toList());
            }
        }
        
        // 搜索过滤
        if (search != null && !search.isEmpty()) {
            String finalSearch = search.toLowerCase();
            releases = releases.stream()
                .filter(release -> {
                    if (release.getTitle() != null && release.getTitle().toLowerCase().contains(finalSearch)) {
                        return true;
                    }
                    if (release.getDescription() != null && release.getDescription().toLowerCase().contains(finalSearch)) {
                        return true;
                    }
                    return false;
                })
                .collect(java.util.stream.Collectors.toList());
        }

        // 分页处理
        int total = releases.size();
        int fromIndex = (page - 1) * page_size;
        int toIndex = Math.min(fromIndex + page_size, total);
        
        List<Release> pagedReleases;
        if (fromIndex < total) {
            pagedReleases = releases.subList(fromIndex, toIndex);
        } else {
            pagedReleases = releases;
        }

        // 构建响应数据
        Map<String, Object> response = new HashMap<>();
        response.put("items", pagedReleases);
        response.put("total", total);
        response.put("page", page);
        response.put("page_size", page_size);

        return ResponseEntity.ok(response);
    }

    // 发版导出接口
    @GetMapping("/export")
    @RequirePermission("release:export")
    public void exportReleases(
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String search,
            HttpServletResponse response
    ) throws Exception {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            response.setStatus(401);
            return;
        }

        // 查询所有发版
        List<Release> releases = releaseMapper.findAll();
        
        // 状态过滤 (支持多选)
        if (status != null && !status.isEmpty()) {
            List<String> statusList = java.util.Arrays.stream(status.split(","))
                .map(String::trim)
                .collect(java.util.stream.Collectors.toList());
            releases = releases.stream()
                .filter(release -> statusList.contains(release.getStatus()))
                .collect(java.util.stream.Collectors.toList());
        }
        
        // 搜索过滤
        if (search != null && !search.isEmpty()) {
            String finalSearch = search.toLowerCase();
            releases = releases.stream()
                .filter(release -> {
                    if (release.getTitle() != null && release.getTitle().toLowerCase().contains(finalSearch)) {
                        return true;
                    }
                    if (release.getDescription() != null && release.getDescription().toLowerCase().contains(finalSearch)) {
                        return true;
                    }
                    return false;
                })
                .collect(java.util.stream.Collectors.toList());
        }

        // 创建工作簿
        org.apache.poi.ss.usermodel.Workbook workbook = new org.apache.poi.xssf.usermodel.XSSFWorkbook();
        org.apache.poi.ss.usermodel.Sheet sheet = workbook.createSheet("发版列表");
        
        // 创建标题行
        org.apache.poi.ss.usermodel.Row headerRow = sheet.createRow(0);
        String[] headers = {
            "发版 ID", "发版标题", "发版描述", "状态", "创建人",
            "创建时间", "更新时间"
        };
        
        for (int i = 0; i < headers.length; i++) {
            org.apache.poi.ss.usermodel.Cell cell = headerRow.createCell(i);
            cell.setCellValue(headers[i]);
        }
        
        // 填充数据
        int rowNum = 1;
        for (Release release : releases) {
            org.apache.poi.ss.usermodel.Row row = sheet.createRow(rowNum++);
            
            // 获取创建人名称
            String creatorName = "";
            if (release.getCreatedBy() != null) {
                com.taskboard.backend.model.User creator = userMapper.findById(release.getCreatedBy());
                if (creator != null) {
                    creatorName = creator.getName();
                }
            }
            
            row.createCell(0).setCellValue(release.getId());
            row.createCell(1).setCellValue(release.getTitle() != null ? release.getTitle() : "");
            row.createCell(2).setCellValue(release.getDescription() != null ? release.getDescription() : "");
            row.createCell(3).setCellValue(release.getStatus() != null ? release.getStatus() : "");
            row.createCell(4).setCellValue(creatorName);
            row.createCell(5).setCellValue(release.getCreatedAt() != null ? new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(release.getCreatedAt()) : "");
            row.createCell(6).setCellValue(release.getUpdatedAt() != null ? new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(release.getUpdatedAt()) : "");
        }
        
        // 自动调整列宽
        for (int i = 0; i < headers.length; i++) {
            sheet.autoSizeColumn(i);
        }
        
        // 设置响应头
        response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
        response.setCharacterEncoding("utf-8");
        String fileName = "releases_export_" + new java.text.SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date()) + ".xlsx";
        response.setHeader("Content-Disposition", "attachment; filename=" + URLEncoder.encode(fileName, "UTF-8"));
        
        // 写入输出流
        workbook.write(response.getOutputStream());
        workbook.close();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Release> getReleaseById(@PathVariable Long id) {
        Release release = releaseMapper.findById(id);
        if (release != null) {
            return ResponseEntity.ok(release);
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @PostMapping
    @RequirePermission("release:create")
    public ResponseEntity<?> createRelease(@RequestBody Release release) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User user = userMapper.findByUsername(username).orElse(null);
        if (user != null) {
            release.setCreatedBy(user.getId());
        }
        
        releaseMapper.insert(release);
        return ResponseEntity.ok(release);
    }

    @PutMapping("/{id}")
    @RequirePermission("release:update")
    public ResponseEntity<Release> updateRelease(@PathVariable Long id, @RequestBody Release release) {
        Release existingRelease = releaseMapper.findById(id);
        if (existingRelease != null) {
            release.setId(id);
            releaseMapper.update(release);
            return ResponseEntity.ok(release);
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @DeleteMapping("/{id}")
    @RequirePermission("release:delete")
    public ResponseEntity<?> deleteRelease(@PathVariable Long id) {
        Release release = releaseMapper.findById(id);
        if (release != null) {
            releaseMapper.delete(id);
            return ResponseEntity.ok().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @PostMapping("/{id}/follow")
    @RequirePermission("release:follow")
    public ResponseEntity<?> followRelease(@PathVariable Long id) {
        // TODO: 实现关注发版的逻辑
        return ResponseEntity.ok().build();
    }

    @DeleteMapping("/{id}/follow")
    public ResponseEntity<?> unfollowRelease(@PathVariable Long id) {
        // TODO: 实现取消关注发版的逻辑
        return ResponseEntity.ok().build();
    }

    @GetMapping("/tags")
    public ResponseEntity<?> getReleaseTags() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        List<ReleaseTag> tags = releaseTagMapper.findAll();
        return ResponseEntity.ok(tags);
    }
}