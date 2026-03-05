package com.taskboard.backend.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.io.File;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Autowired
    private UploadProperties uploadProperties;

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        String uploadDir = uploadProperties.getUploadDir();
        
        // 确保使用绝对路径
        File uploadDirectory = new File(uploadDir);
        if (!uploadDirectory.isAbsolute()) {
            // 如果是相对路径，转换为绝对路径
            uploadDirectory = new File(System.getProperty("user.dir"), uploadDir);
        }
        
        String uploadAbsolutePath = uploadDirectory.getAbsolutePath();
        
        // 添加资源处理器，映射静态文件
        registry.addResourceHandler("/api/uploads/images/**")
                .addResourceLocations("file:" + uploadAbsolutePath + File.separator);
    }
}
