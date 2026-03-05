package com.taskboard.backend.controller;

import com.taskboard.backend.annotation.RequirePermission;
import com.taskboard.backend.mapper.SystemSettingMapper;
import com.taskboard.backend.model.SystemSetting;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class SettingsController {

    @Autowired
    private SystemSettingMapper systemSettingMapper;

    @GetMapping("/settings")
    public ResponseEntity<?> getSettings() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        List<SystemSetting> settings = systemSettingMapper.findAll();
        return ResponseEntity.ok(settings);
    }

    @GetMapping("/settings/{key}")
    @RequirePermission("setting:get")
    public ResponseEntity<?> getSetting(@PathVariable String key) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        
        // 检查是否为 admin 用户
        if (!"admin".equals(username)) {
            return ResponseEntity.status(403).body("Forbidden: Admin access required");
        }

        SystemSetting setting = systemSettingMapper.findByKey(key).orElse(null);
        if (setting == null) {
            return ResponseEntity.status(404).body("Setting not found");
        }

        return ResponseEntity.ok(setting);
    }

    @PutMapping("/settings/{key}")
    @RequirePermission("setting:update")
    public ResponseEntity<?> updateSetting(@PathVariable String key, @RequestBody Map<String, String> updateData) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        
        // 检查是否为 admin 用户
        if (!"admin".equals(username)) {
            return ResponseEntity.status(403).body("Forbidden: Admin access required");
        }

        SystemSetting setting = systemSettingMapper.findByKey(key).orElse(null);
        if (setting == null) {
            return ResponseEntity.status(404).body("Setting not found");
        }

        String value = updateData.get("value");
        String description = updateData.get("description");

        if (value != null) {
            setting.setValue(value);
        }
        if (description != null) {
            setting.setDescription(description);
        }

        systemSettingMapper.update(setting);
        return ResponseEntity.ok(setting);
    }

    @PostMapping("/settings")
    @RequirePermission("setting:create")
    public ResponseEntity<?> createSetting(@RequestBody Map<String, String> settingData) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        
        // 检查是否为 admin 用户
        if (!"admin".equals(username)) {
            return ResponseEntity.status(403).body("Forbidden: Admin access required");
        }

        String key = settingData.get("key");
        String value = settingData.get("value");
        String description = settingData.get("description");

        // 检查是否已存在
        if (systemSettingMapper.findByKey(key).isPresent()) {
            return ResponseEntity.badRequest().body("Setting with this key already exists");
        }

        SystemSetting newSetting = new SystemSetting();
        newSetting.setKey(key);
        newSetting.setValue(value);
        newSetting.setDescription(description);

        systemSettingMapper.insert(newSetting);
        return ResponseEntity.ok(newSetting);
    }

    @DeleteMapping("/settings/{key}")
    @RequirePermission("setting:delete")
    public ResponseEntity<?> deleteSetting(@PathVariable String key) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        
        // 检查是否为 admin 用户
        if (!"admin".equals(username)) {
            return ResponseEntity.status(403).body("Forbidden: Admin access required");
        }

        SystemSetting setting = systemSettingMapper.findByKey(key).orElse(null);
        if (setting == null) {
            return ResponseEntity.status(404).body("Setting not found");
        }

        systemSettingMapper.deleteByKey(key);
        Map<String, String> response = new HashMap<>();
        response.put("detail", "Setting deleted successfully");
        return ResponseEntity.ok(response);
    }
}
