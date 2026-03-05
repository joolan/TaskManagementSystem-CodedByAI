package com.taskboard.backend.model;

import lombok.Data;
import java.util.Date;

@Data
public class UserMessage {

    private Long id;
    private Long userId;
    private Long messageId;
    private Integer isRead;
    private Date readAt;
    
    // 关联的消息对象
    private Message message;
}
