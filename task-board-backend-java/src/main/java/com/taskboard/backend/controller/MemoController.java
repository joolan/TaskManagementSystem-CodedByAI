package com.taskboard.backend.controller;

import com.taskboard.backend.model.Memo;
import com.taskboard.backend.model.User;
import com.taskboard.backend.mapper.MemoMapper;
import com.taskboard.backend.mapper.UserMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/memos")
public class MemoController {

    @Autowired
    private MemoMapper memoMapper;

    @Autowired
    private UserMapper userMapper;

    @GetMapping
    public ResponseEntity<?> getMemos() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User user = userMapper.findByUsername(username).orElse(null);
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        // 获取当前用户的备忘录列表
        List<Memo> memos = memoMapper.findByCreatedBy(user.getId());
        return ResponseEntity.ok(memos);
    }

    @PostMapping
    public ResponseEntity<?> createMemo(@RequestBody Map<String, Object> memoData) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User user = userMapper.findByUsername(username).orElse(null);
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        // 获取请求参数
        String name = (String) memoData.get("name");
        String content = (String) memoData.get("content");

        if (name == null || name.isEmpty()) {
            return ResponseEntity.badRequest().body("Name is required");
        }

        // 创建备忘录
        Memo memo = new Memo();
        memo.setName(name);
        memo.setContent(content);
        memo.setCreatedBy(user.getId());
        memo.setCreatedAt(new Date());
        memo.setUpdatedAt(new Date());

        memoMapper.insert(memo);

        // 重新查询备忘录，返回完整数据
        Memo createdMemo = memoMapper.findById(memo.getId());
        if (createdMemo != null) {
            User creator = userMapper.findById(createdMemo.getCreatedBy());
            createdMemo.setCreator(creator);
        }

        return ResponseEntity.ok(createdMemo);
    }

    @GetMapping("/{memo_id}")
    public ResponseEntity<?> getMemo(@PathVariable Long memo_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User user = userMapper.findByUsername(username).orElse(null);
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        // 查找备忘录
        Memo memo = memoMapper.findById(memo_id);
        if (memo == null) {
            return ResponseEntity.status(404).body("Memo not found");
        }

        // 检查权限，只能查看自己的备忘录
        if (!memo.getCreatedBy().equals(user.getId()) && !"admin".equals(username)) {
            return ResponseEntity.status(403).body("Forbidden");
        }

        // 填充 creator 信息
        if (memo.getCreatedBy() != null) {
            User creator = userMapper.findById(memo.getCreatedBy());
            memo.setCreator(creator);
        }

        return ResponseEntity.ok(memo);
    }

    @PutMapping("/{memo_id}")
    public ResponseEntity<?> updateMemo(@PathVariable Long memo_id, @RequestBody Map<String, Object> memoData) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User user = userMapper.findByUsername(username).orElse(null);
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        // 查找备忘录
        Memo memo = memoMapper.findById(memo_id);
        if (memo == null) {
            return ResponseEntity.status(404).body("Memo not found");
        }

        // 检查权限，只能更新自己的备忘录
        if (!memo.getCreatedBy().equals(user.getId()) && !"admin".equals(username)) {
            return ResponseEntity.status(403).body("Forbidden");
        }

        // 更新备忘录
        if (memoData.get("name") != null) {
            memo.setName((String) memoData.get("name"));
        }
        if (memoData.get("content") != null) {
            memo.setContent((String) memoData.get("content"));
        }
        memo.setUpdatedAt(new Date());

        memoMapper.update(memo);

        // 重新查询备忘录，返回完整数据
        Memo updatedMemo = memoMapper.findById(memo_id);
        if (updatedMemo != null) {
            User creator = userMapper.findById(updatedMemo.getCreatedBy());
            updatedMemo.setCreator(creator);
        }

        return ResponseEntity.ok(updatedMemo);
    }

    @DeleteMapping("/{memo_id}")
    public ResponseEntity<?> deleteMemo(@PathVariable Long memo_id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User user = userMapper.findByUsername(username).orElse(null);
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        // 查找备忘录
        Memo memo = memoMapper.findById(memo_id);
        if (memo == null) {
            return ResponseEntity.status(404).body("Memo not found");
        }

        // 检查权限，只能删除自己的备忘录
        if (!memo.getCreatedBy().equals(user.getId()) && !"admin".equals(username)) {
            return ResponseEntity.status(403).body("Forbidden");
        }

        memoMapper.delete(memo_id);

        return ResponseEntity.ok().build();
    }
}
