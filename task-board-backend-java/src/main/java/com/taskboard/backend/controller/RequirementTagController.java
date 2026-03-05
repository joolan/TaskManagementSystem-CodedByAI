package com.taskboard.backend.controller;

import com.taskboard.backend.mapper.RequirementTagMapper;
import com.taskboard.backend.model.RequirementTag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/requirement-tags")
public class RequirementTagController {

    @Autowired
    private RequirementTagMapper requirementTagMapper;

    @GetMapping
    public ResponseEntity<?> getRequirementTags() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        List<RequirementTag> tags = requirementTagMapper.findAll();
        return ResponseEntity.ok(tags);
    }

    @GetMapping("/{id}")
    public ResponseEntity<RequirementTag> getRequirementTagById(@PathVariable Long id) {
        RequirementTag tag = requirementTagMapper.findById(id);
        if (tag != null) {
            return ResponseEntity.ok(tag);
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @PostMapping
    public ResponseEntity<?> createRequirementTag(@RequestBody RequirementTag tag) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        requirementTagMapper.insert(tag);
        return ResponseEntity.ok(tag);
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> updateRequirementTag(@PathVariable Long id, @RequestBody RequirementTag tag) {
        RequirementTag existingTag = requirementTagMapper.findById(id);
        if (existingTag != null) {
            tag.setId(id);
            requirementTagMapper.update(tag);
            return ResponseEntity.ok(tag);
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteRequirementTag(@PathVariable Long id) {
        RequirementTag tag = requirementTagMapper.findById(id);
        if (tag != null) {
            requirementTagMapper.delete(id);
            return ResponseEntity.ok().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }
}
