package com.taskboard.backend.aspect;

import com.taskboard.backend.annotation.RequirePermission;
import com.taskboard.backend.mapper.PermissionMapper;
import com.taskboard.backend.mapper.UserMapper;
import com.taskboard.backend.model.Permission;
import com.taskboard.backend.model.User;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.reflect.MethodSignature;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

import java.lang.reflect.Method;
import java.util.List;

@Aspect
@Component
public class PermissionAspect {

    @Autowired
    private UserMapper userMapper;

    @Autowired
    private PermissionMapper permissionMapper;

    @Around("@annotation(com.taskboard.backend.annotation.RequirePermission)")
    public Object checkPermission(ProceedingJoinPoint joinPoint) throws Throwable {
        MethodSignature signature = (MethodSignature) joinPoint.getSignature();
        Method method = signature.getMethod();
        
        RequirePermission requirePermission = method.getAnnotation(RequirePermission.class);
        String permissionCode = requirePermission.value();

        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        String username = authentication.getName();
        User user = userMapper.findByUsername(username).orElse(null);
        
        if (user == null) {
            return ResponseEntity.status(404).body("User not found");
        }

        // Admin user has all permissions
        if ("admin".equals(username)) {
            return joinPoint.proceed();
        }

        // Check if user has the required permission
        if (permissionCode != null && !permissionCode.isEmpty()) {
            boolean hasPermission = checkUserPermission(user.getId(), permissionCode);
            
            if (!hasPermission) {
                return ResponseEntity.status(403).body("Forbidden: Insufficient permissions");
            }
        }

        return joinPoint.proceed();
    }

    private boolean checkUserPermission(Long userId, String permissionCode) {
        // Check if user has the permission (through roles or direct assignment)
        List<Permission> permissions = permissionMapper.findByUserId(userId);
        for (Permission permission : permissions) {
            if (permissionCode.equals(permission.getCode())) {
                return true;
            }
        }

        return false;
    }
}
