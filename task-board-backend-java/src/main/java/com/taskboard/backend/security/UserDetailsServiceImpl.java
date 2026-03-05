package com.taskboard.backend.security;

import com.taskboard.backend.mapper.PermissionMapper;
import com.taskboard.backend.mapper.RoleMapper;
import com.taskboard.backend.mapper.UserMapper;
import com.taskboard.backend.model.Permission;
import com.taskboard.backend.model.Role;
import com.taskboard.backend.model.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

@Service
public class UserDetailsServiceImpl implements UserDetailsService {

    @Autowired
    private UserMapper userMapper;

    @Autowired
    private RoleMapper roleMapper;

    @Autowired
    private PermissionMapper permissionMapper;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        User user = userMapper.findByUsername(username)
                .orElseThrow(() -> new UsernameNotFoundException("User not found with username: " + username));

        List<GrantedAuthority> authorities = new ArrayList<>();

        // 如果是 admin 用户，赋予超级管理员权限
        if ("admin".equals(username)) {
            authorities.add(new SimpleGrantedAuthority("ROLE_ADMIN"));
            authorities.add(new SimpleGrantedAuthority("ROLE_SUPER_ADMIN"));
            authorities.add(new SimpleGrantedAuthority("PERMISSION_ALL"));
        }

        // 添加用户角色
        if (user.getId() != null) {
            List<Role> roles = roleMapper.findByUserId(user.getId());
            if (roles != null) {
                for (Role role : roles) {
                    authorities.add(new SimpleGrantedAuthority("ROLE_" + role.getCode()));
                }
            }

            // 添加用户权限
            List<Permission> permissions = permissionMapper.findByUserId(user.getId());
            if (permissions != null) {
                for (Permission permission : permissions) {
                    authorities.add(new SimpleGrantedAuthority(permission.getCode()));
                }
            }
        }

        return new org.springframework.security.core.userdetails.User(
                user.getUsername(),
                user.getPassword(),
                authorities
        );
    }
}
