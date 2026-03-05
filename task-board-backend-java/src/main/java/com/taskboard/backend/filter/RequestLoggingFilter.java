package com.taskboard.backend.filter;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import javax.servlet.*;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Enumeration;

@Component
public class RequestLoggingFilter implements Filter {

    private static final Logger logger = LoggerFactory.getLogger(RequestLoggingFilter.class);

    @Override
    public void init(FilterConfig filterConfig) throws ServletException {
        // 初始化方法
    }

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
        HttpServletRequest httpRequest = (HttpServletRequest) request;
        HttpServletResponse httpResponse = (HttpServletResponse) response;

        // 记录请求开始时间
        long startTime = System.currentTimeMillis();

        // 记录请求信息
        StringBuilder requestInfo = new StringBuilder();
        requestInfo.append("[REQUEST] ")
                .append(httpRequest.getMethod())
                .append(" ")
                .append(httpRequest.getRequestURI());

        // 记录请求参数
        Enumeration<String> parameterNames = httpRequest.getParameterNames();
        if (parameterNames.hasMoreElements()) {
            requestInfo.append("?");
            boolean first = true;
            while (parameterNames.hasMoreElements()) {
                String paramName = parameterNames.nextElement();
                if (!first) {
                    requestInfo.append("&");
                }
                requestInfo.append(paramName).append("=");
                // 对于密码等敏感参数，不记录具体值
                if (paramName.equals("password")) {
                    requestInfo.append("******");
                } else {
                    requestInfo.append(httpRequest.getParameter(paramName));
                }
                first = false;
            }
        }

        // 记录请求头
        Enumeration<String> headerNames = httpRequest.getHeaderNames();
        while (headerNames.hasMoreElements()) {
            String headerName = headerNames.nextElement();
            // 对于Authorization头，只记录Bearer前缀，不记录完整token
            if (headerName.equals("Authorization")) {
                String headerValue = httpRequest.getHeader(headerName);
                if (headerValue != null && headerValue.startsWith("Bearer ")) {
                    requestInfo.append(" | ").append(headerName).append("=Bearer ******");
                } else {
                    requestInfo.append(" | ").append(headerName).append("=").append(headerValue);
                }
            } else {
                requestInfo.append(" | ").append(headerName).append("=").append(httpRequest.getHeader(headerName));
            }
        }

        // 记录请求IP
        String clientIP = httpRequest.getRemoteAddr();
        requestInfo.append(" | ClientIP=").append(clientIP);

        logger.info(requestInfo.toString());

        // 继续执行过滤器链
        chain.doFilter(request, response);

        // 记录响应信息
        long endTime = System.currentTimeMillis();
        long executionTime = endTime - startTime;
        logger.info("[RESPONSE] " + httpRequest.getRequestURI() + " | Status=" + httpResponse.getStatus() + " | ExecutionTime=" + executionTime + "ms");
    }

    @Override
    public void destroy() {
        // 销毁方法
    }
}
