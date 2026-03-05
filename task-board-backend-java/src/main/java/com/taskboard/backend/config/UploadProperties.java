package com.taskboard.backend.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class UploadProperties {

    @Value("${upload.dir:uploads/images}")
    private String uploadDir;

    @Value("${upload.max-file-size:5242880}")
    private long maxFileSize;

    @Value("${upload.allowed-extensions:.jpg,.jpeg,.png,.gif,.webp}")
    private String allowedExtensions;

    public String getUploadDir() {
        return uploadDir;
    }

    public void setUploadDir(String uploadDir) {
        this.uploadDir = uploadDir;
    }

    public long getMaxFileSize() {
        return maxFileSize;
    }

    public void setMaxFileSize(long maxFileSize) {
        this.maxFileSize = maxFileSize;
    }

    public String getAllowedExtensions() {
        return allowedExtensions;
    }

    public void setAllowedExtensions(String allowedExtensions) {
        this.allowedExtensions = allowedExtensions;
    }

    public String[] getAllowedExtensionsArray() {
        return allowedExtensions.split(",");
    }
}
