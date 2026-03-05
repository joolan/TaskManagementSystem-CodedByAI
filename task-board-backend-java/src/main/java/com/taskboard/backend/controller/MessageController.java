package com.taskboard.backend.controller;

import com.taskboard.backend.mapper.MessageMapper;
import com.taskboard.backend.mapper.UserMapper;
import com.taskboard.backend.mapper.UserMessageMapper;
import com.taskboard.backend.model.Message;
import com.taskboard.backend.model.User;
import com.taskboard.backend.model.UserMessage;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api")
public class MessageController {

    @Autowired
    private MessageMapper messageMapper;
    
    @Autowired
    private UserMessageMapper userMessageMapper;
    
    @Autowired
    private UserMapper userMapper;

    @GetMapping("/messages")
    public ResponseEntity<?> getUserMessages(@RequestParam(required = false) Boolean is_read) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        com.taskboard.backend.model.User user = userMapper.findByUsername(username).orElse(null);
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        List<UserMessage> userMessages;
        if (is_read != null) {
            userMessages = userMessageMapper.findByUserIdAndReadStatus(user.getId(), is_read ? 1 : 0);
        } else {
            userMessages = userMessageMapper.findByUserId(user.getId());
        }

        // 构建响应数据
        List<Map<String, Object>> result = new ArrayList<>();
        for (UserMessage um : userMessages) {
            Map<String, Object> messageMap = new HashMap<>();
            Message msg = um.getMessage();
            if (msg != null) {
                messageMap.put("id", msg.getId());
                messageMap.put("message_type", msg.getMessageType());
                messageMap.put("title", msg.getTitle());
                messageMap.put("content", msg.getContent());
                messageMap.put("redirect_path", msg.getRedirectPath());
                messageMap.put("created_by", msg.getCreatedBy());
                messageMap.put("created_at", msg.getCreatedAt());
                messageMap.put("is_read", um.getIsRead() == 1);
                messageMap.put("read_at", um.getReadAt());
            }
            result.add(messageMap);
        }

        return ResponseEntity.ok(result);
    }

    @GetMapping("/messages/unread-count")
    public ResponseEntity<?> getUnreadMessageCount() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        com.taskboard.backend.model.User user = userMapper.findByUsername(username).orElse(null);
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        int count = userMessageMapper.countUnread(user.getId());
        Map<String, Object> result = new HashMap<>();
        result.put("unread_count", count);
        return ResponseEntity.ok(result);
    }

    @PutMapping("/messages/{message_id}/read")
    public ResponseEntity<?> markMessageAsRead(@PathVariable Long message_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        com.taskboard.backend.model.User user = userMapper.findByUsername(username).orElse(null);
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        // 查找用户消息
        List<UserMessage> userMessages = userMessageMapper.findByUserId(user.getId());
        UserMessage targetUserMessage = null;
        for (UserMessage um : userMessages) {
            if (um.getMessageId().equals(message_id)) {
                targetUserMessage = um;
                break;
            }
        }

        if (targetUserMessage == null) {
            return ResponseEntity.status(404).body("Message not found");
        }

        // 标记为已读
        targetUserMessage.setIsRead(1);
        targetUserMessage.setReadAt(new Date());
        userMessageMapper.update(targetUserMessage);

        // 返回消息详情
        Message msg = messageMapper.findById(message_id);
        Map<String, Object> result = new HashMap<>();
        result.put("id", msg.getId());
        result.put("message_type", msg.getMessageType());
        result.put("title", msg.getTitle());
        result.put("content", msg.getContent());
        result.put("redirect_path", msg.getRedirectPath());
        result.put("created_by", msg.getCreatedBy());
        result.put("created_at", msg.getCreatedAt());
        result.put("is_read", true);
        result.put("read_at", targetUserMessage.getReadAt());

        return ResponseEntity.ok(result);
    }
}
