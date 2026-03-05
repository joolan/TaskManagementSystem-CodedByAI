package com.taskboard.backend.controller;

import com.taskboard.backend.config.UploadProperties;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import javax.annotation.PostConstruct;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/upload")
public class UploadController {

    @Autowired
    private UploadProperties uploadProperties;

    private String uploadDir;

    @PostConstruct
    public void init() {
        uploadDir = uploadProperties.getUploadDir();
        File dir = new File(uploadDir);
        if (!dir.exists()) {
            dir.mkdirs();
        }
    }

    @PostMapping("/image")
    public ResponseEntity<?> uploadImage(@RequestParam("file") MultipartFile file) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body("文件不能为空");
        }

        String originalFilename = file.getOriginalFilename();
        String fileExtension = getFileExtension(originalFilename);

        if (!isAllowedExtension(fileExtension)) {
            return ResponseEntity.badRequest()
                .body("不支持的文件类型。允许的类型：" + uploadProperties.getAllowedExtensions());
        }

        if (file.getSize() > uploadProperties.getMaxFileSize()) {
            return ResponseEntity.badRequest()
                .body("文件大小超过限制（最大 " + (uploadProperties.getMaxFileSize() / (1024 * 1024)) + "MB）");
        }

        String uniqueFilename = UUID.randomUUID().toString().replace("-", "") + fileExtension;
        Path filePath = Paths.get(uploadDir, uniqueFilename);

        try {
            Files.copy(file.getInputStream(), filePath);

            String fileUrl = "/api/uploads/images/" + uniqueFilename;

            Map<String, Object> result = new HashMap<>();
            result.put("url", fileUrl);
            result.put("filename", uniqueFilename);
            result.put("size", file.getSize());

            return ResponseEntity.ok(result);
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body("文件上传失败：" + e.getMessage());
        }
    }

    private String getFileExtension(String filename) {
        if (filename == null || filename.isEmpty()) {
            return "";
        }
        int lastDotIndex = filename.lastIndexOf('.');
        if (lastDotIndex == -1) {
            return "";
        }
        return filename.substring(lastDotIndex).toLowerCase();
    }

    private boolean isAllowedExtension(String extension) {
        String[] allowedExtensions = uploadProperties.getAllowedExtensionsArray();
        for (String allowed : allowedExtensions) {
            if (allowed.trim().equalsIgnoreCase(extension)) {
                return true;
            }
        }
        return false;
    }
}
