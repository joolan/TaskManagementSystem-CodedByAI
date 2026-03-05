package com.taskboard.backend.controller;

import com.taskboard.backend.model.Comment;
import com.taskboard.backend.model.User;
import com.taskboard.backend.model.Attachment;
import com.taskboard.backend.mapper.CommentMapper;
import com.taskboard.backend.mapper.UserMapper;
import com.taskboard.backend.mapper.AttachmentMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/comments")
public class CommentController {

    @Autowired
    private CommentMapper commentMapper;

    @Autowired
    private UserMapper userMapper;

    @Autowired
    private AttachmentMapper attachmentMapper;

    @PutMapping("/{comment_id}/pin")
    public ResponseEntity<?> pinComment(@PathVariable Long comment_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        // 只有 admin 用户可以置顶评论
        if (!"admin".equals(username)) {
            return ResponseEntity.status(403).body("Forbidden");
        }

        // 查找评论
        Comment comment = commentMapper.findById(comment_id);
        if (comment == null) {
            return ResponseEntity.status(404).body("Comment not found");
        }

        // 切换置顶状态
        if (comment.getPinnedAt() != null) {
            comment.setPinnedAt(null);
        } else {
            comment.setPinnedAt(new Date());
        }

        commentMapper.update(comment);

        // 重新查询评论，返回完整数据
        Comment updatedComment = commentMapper.findById(comment_id);
        if (updatedComment != null) {
            // 填充 user 信息
            if (updatedComment.getUserId() != null && updatedComment.getIsAnonymous() == 0) {
                User user = userMapper.findById(updatedComment.getUserId());
                updatedComment.setUser(user);
            } else {
                updatedComment.setUser(null);
            }

            // 填充 attachments 信息
            if (updatedComment.getId() != null) {
                List<Attachment> attachments = attachmentMapper.findByCommentId(updatedComment.getId());
                updatedComment.setAttachments(attachments);
            } else {
                updatedComment.setAttachments(new ArrayList<>());
            }

            return ResponseEntity.ok(updatedComment);
        }

        return ResponseEntity.status(404).body("Comment not found");
    }
}
