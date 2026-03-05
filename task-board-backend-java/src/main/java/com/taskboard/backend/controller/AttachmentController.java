package com.taskboard.backend.controller;

import com.taskboard.backend.model.Attachment;
import com.taskboard.backend.mapper.AttachmentMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.io.IOException;
import java.net.URLEncoder;

@RestController
@RequestMapping("/api/attachments")
public class AttachmentController {

    @Autowired
    private AttachmentMapper attachmentMapper;

    @GetMapping("/{attachment_id}/download")
    public ResponseEntity<?> downloadAttachment(@PathVariable Long attachment_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        // 查找附件
        Attachment attachment = attachmentMapper.findById(attachment_id);
        if (attachment == null) {
            return ResponseEntity.status(404).body("Attachment not found");
        }

        // 检查文件是否存在
        File file = new File(attachment.getFilePath());
        if (!file.exists()) {
            return ResponseEntity.status(404).body("File not found");
        }

        try {
            // 设置响应头
            Resource resource = new FileSystemResource(file);
            return ResponseEntity.ok()
                    .contentType(MediaType.APPLICATION_OCTET_STREAM)
                    .header(HttpHeaders.CONTENT_DISPOSITION, 
                            "attachment; filename=\"" + 
                            URLEncoder.encode(attachment.getFilename(), "UTF-8") + "\"")
                    .body(resource);
        } catch (IOException e) {
            return ResponseEntity.status(500).body("Failed to download file: " + e.getMessage());
        }
    }
}
