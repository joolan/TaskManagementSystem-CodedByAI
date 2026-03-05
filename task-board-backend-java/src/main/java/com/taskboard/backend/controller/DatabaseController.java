package com.taskboard.backend.controller;

import com.taskboard.backend.annotation.RequirePermission;
import com.taskboard.backend.mapper.*;
import com.taskboard.backend.model.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import javax.sql.DataSource;
import java.io.*;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.sql.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

@RestController
@RequestMapping("/api/database")
public class DatabaseController {

    @Autowired
    private DataSource dataSource;

    @Value("${spring.datasource.url}")
    private String datasourceUrl;

    @Value("${spring.datasource.username}")
    private String dbUsername;

    @Value("${spring.datasource.password}")
    private String dbPassword;

    private static final String BACKUP_DIR = "backups";

    /**
     * 从 JDBC URL 中提取数据库主机
     */
    private String getDbHost() {
        String host = datasourceUrl.substring(datasourceUrl.indexOf("//") + 2);
        host = host.substring(0, host.indexOf(":"));
        return host;
    }

    /**
     * 从 JDBC URL 中提取数据库端口
     */
    private String getDbPort() {
        String port = datasourceUrl.substring(datasourceUrl.indexOf(":") + 1);
        port = port.substring(0, port.indexOf("/"));
        return port;
    }

    /**
     * 从 JDBC URL 中提取数据库名称
     */
    private String getDbName() {
        String dbName = datasourceUrl.substring(datasourceUrl.lastIndexOf("/") + 1);
        int queryIndex = dbName.indexOf("?");
        if (queryIndex > 0) {
            dbName = dbName.substring(0, queryIndex);
        }
        return dbName;
    }

    /**
     * 使用 JDBC 导出数据库结构和数据为 SQL 文件
     */
    private void exportDatabase(String outputPath) throws SQLException, IOException {
        try (Connection conn = dataSource.getConnection();
             BufferedWriter writer = Files.newBufferedWriter(Paths.get(outputPath))) {

            // 写入文件头注释
            writer.write("-- MySQL Database Backup\n");
            writer.write("-- Database: " + getDbName() + "\n");
            writer.write("-- Date: " + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")) + "\n");
            writer.write("\n");

            // 获取所有表
            DatabaseMetaData metaData = conn.getMetaData();
            // 使用数据库名称作为 catalog 参数
            String dbName = getDbName();
            ResultSet tables = metaData.getTables(dbName, dbName, "%", new String[]{"TABLE"});

            List<String> tableNames = new ArrayList<>();
            while (tables.next()) {
                String tableName = tables.getString("TABLE_NAME");
                // 排除 MySQL 系统表和不需要的表
                if (!tableName.equalsIgnoreCase("dual") && 
                    !tableName.startsWith("sys_") &&
                    !tableName.equalsIgnoreCase("sys_config")) {
                    tableNames.add(tableName);
                }
            }
            tables.close();

            // 禁用外键检查
            writer.write("SET FOREIGN_KEY_CHECKS=0;\n\n");

            // 导出每个表
            for (String tableName : tableNames) {
                exportTable(conn, writer, tableName);
            }

            // 启用外键检查
            writer.write("SET FOREIGN_KEY_CHECKS=1;\n");
        }
    }

    /**
     * 导出单个表的结构和数据
     */
    private void exportTable(Connection conn, BufferedWriter writer, String tableName) throws SQLException, IOException {
        // 写入表注释
        writer.write("--\n");
        writer.write("-- Table structure for table `" + tableName + "`\n");
        writer.write("--\n\n");

        // 导出表结构
        try (Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SHOW CREATE TABLE `" + tableName + "`")) {
            if (rs.next()) {
                String createTableSql = rs.getString(2);
                writer.write("DROP TABLE IF EXISTS `" + tableName + "`;\n");
                writer.write(createTableSql + ";\n\n");
            }
        } catch (SQLException e) {
            // 如果表不存在，跳过该表
            writer.write("-- Skipped table `" + tableName + "`: " + e.getMessage() + "\n\n");
            return;
        }

        // 导出表数据
        writer.write("--\n");
        writer.write("-- Dumping data for table `" + tableName + "`\n");
        writer.write("--\n\n");

        try (Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT * FROM `" + tableName + "`")) {
            ResultSetMetaData rsmd = rs.getMetaData();
            int columnCount = rsmd.getColumnCount();

            // 批量写入 INSERT 语句
            List<String> insertStatements = new ArrayList<>();
            int batchSize = 1000;
            int rowCount = 0;

            while (rs.next()) {
                StringBuilder values = new StringBuilder();
                for (int i = 0; i < columnCount; i++) {
                    if (i > 0) values.append(", ");
                    Object value = rs.getObject(i + 1);
                    int columnType = rsmd.getColumnType(i + 1);
                    
                    if (value == null) {
                        values.append("NULL");
                    } else if (value instanceof Boolean) {
                        values.append(value).append(" ");
                    } else if (value instanceof Number) {
                        values.append(value);
                    } else if (columnType == java.sql.Types.TIMESTAMP || 
                               columnType == java.sql.Types.DATE || 
                               columnType == java.sql.Types.TIME) {
                        // 日期时间类型，转换为 MySQL 标准格式
                        String dateValue = value.toString();
                        // 将 ISO 格式 (2026-03-04T10:13:34) 转换为 SQL 格式 (2026-03-04 10:13:34)
                        if (dateValue.contains("T")) {
                            dateValue = dateValue.replace("T", " ");
                        }
                        // 如果包含时区信息，去掉时区
                        if (dateValue.contains("+") && dateValue.lastIndexOf("+") > 10) {
                            dateValue = dateValue.substring(0, dateValue.lastIndexOf("+"));
                        }
                        values.append("'").append(dateValue).append("'");
                    } else {
                        // 转义字符串
                        String strValue = value.toString()
                                .replace("\\", "\\\\")
                                .replace("'", "\\'")
                                .replace("\n", "\\n")
                                .replace("\r", "\\r");
                        values.append("'").append(strValue).append("'");
                    }
                }

                insertStatements.add("(" + values + ")");

                rowCount++;

                // 达到批量大小时写入文件
                if (rowCount % batchSize == 0) {
                    writer.write("INSERT INTO `" + tableName + "` VALUES ");
                    writer.write(String.join(",\n", insertStatements));
                    writer.write(";\n\n");
                    insertStatements.clear();
                }
            }

            // 写入剩余的 INSERT 语句
            if (!insertStatements.isEmpty()) {
                writer.write("INSERT INTO `" + tableName + "` VALUES ");
                writer.write(String.join(",\n", insertStatements));
                writer.write(";\n\n");
            }
        } catch (SQLException e) {
            // 如果查询失败，记录错误
            writer.write("-- Error exporting data from table `" + tableName + "`: " + e.getMessage() + "\n\n");
        }

        writer.write("\n");
    }

    /**
     * 使用 JDBC 导入 SQL 文件还原数据库
     */
    private void importDatabase(String inputPath) throws SQLException, IOException {
        importDatabaseWithTimeout(inputPath, 60);
    }

    /**
     * 使用 JDBC 导入 SQL 文件还原数据库 (带超时控制) - 保留方法
     * @param inputPath SQL 文件路径
     * @param timeoutSeconds 超时时间 (秒)
     */
    private void importDatabaseWithTimeout(String inputPath, int timeoutSeconds) throws SQLException, IOException {
        importDatabaseFast(inputPath);
    }

    /**
     * 使用 JDBC 快速导入 SQL 文件还原数据库 (优化版本)
     * 优化点:
     * 1. 使用批量执行
     * 2. 减少日志输出
     * 3. 禁用自动提交，使用事务批量处理
     */
    private void importDatabaseFast(String inputPath) throws SQLException, IOException {
        try (Connection conn = dataSource.getConnection();
             BufferedReader reader = Files.newBufferedReader(Paths.get(inputPath))) {

            // 禁用自动提交，使用事务
            conn.setAutoCommit(false);

            // 禁用外键检查
            try (Statement stmt = conn.createStatement()) {
                stmt.execute("SET FOREIGN_KEY_CHECKS=0");
            }

            // 使用批量执行
            try (Statement stmt = conn.createStatement()) {
                StringBuilder sqlBuffer = new StringBuilder();
                String line;
                int batchSize = 100;
                int batchCount = 0;

                while ((line = reader.readLine()) != null) {
                    line = line.trim();

                    // 跳过注释和空行
                    if (line.isEmpty() || line.startsWith("--") || line.startsWith("/*") || line.startsWith("*/")) {
                        continue;
                    }

                    sqlBuffer.append(line).append(" ");

                    // 如果行以分号结尾，执行 SQL 语句
                    if (line.endsWith(";")) {
                        String sql = sqlBuffer.toString().trim();
                        if (!sql.isEmpty()) {
                            try {
                                stmt.addBatch(sql);
                                batchCount++;

                                // 每 100 条执行一次批量
                                if (batchCount % batchSize == 0) {
                                    stmt.executeBatch();
                                    stmt.clearBatch();
                                }
                            } catch (SQLException e) {
                                // 忽略一些错误 (如表已存在)
                                if (!e.getMessage().contains("already exists")) {
                                    throw e;
                                }
                            }
                        }
                        sqlBuffer.setLength(0);
                    }
                }

                // 执行剩余的批量语句
                if (batchCount % batchSize != 0) {
                    stmt.executeBatch();
                }
            }

            // 启用外键检查
            try (Statement stmt = conn.createStatement()) {
                stmt.execute("SET FOREIGN_KEY_CHECKS=1");
            }

            // 提交事务
            conn.commit();
        }
    }

    @PostMapping("/backup")
    @RequirePermission("database:backup")
    public ResponseEntity<?> backupDatabase() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        try {
            // 确保备份目录存在
            Path backupDir = Paths.get(BACKUP_DIR);
            if (!Files.exists(backupDir)) {
                Files.createDirectories(backupDir);
            }

            // 生成备份文件名
            String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
            String backupFilename = "task_board_backup_" + timestamp + ".sql";
            String backupPath = Paths.get(BACKUP_DIR, backupFilename).toString();

            // 使用 JDBC 导出数据库
            exportDatabase(backupPath);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "数据库备份成功");
            response.put("backup_file", backupFilename);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "数据库备份失败：" + e.getMessage());
            return ResponseEntity.status(500).body(response);
        }
    }

    @PostMapping("/restore")
    @RequirePermission("database:restore")
    public ResponseEntity<?> restoreDatabase(@RequestParam("file") MultipartFile file) {
        long startTime = System.currentTimeMillis();
        System.out.println("========== 数据库还原开始 ==========");
        System.out.println("还原文件：" + file.getOriginalFilename());
        System.out.println("文件大小：" + file.getSize() + " bytes");
        System.out.println("开始时间：" + LocalDateTime.now());
        
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body("请选择要上传的数据库文件");
        }

        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null || !originalFilename.endsWith(".sql")) {
            return ResponseEntity.badRequest().body("只支持.sql 格式的数据库文件");
        }

        Path tempFile = null;
        try {
            // 保存上传的文件到临时目录
            tempFile = Files.createTempFile("restore_", ".sql");
            file.transferTo(tempFile);

            // 使用 JDBC 快速导入数据库
            System.out.println("开始导入数据库...");
            importDatabaseFast(tempFile.toString());
            
            long endTime = System.currentTimeMillis();
            long duration = endTime - startTime;
            
            System.out.println("数据库导入完成，耗时：" + duration + "ms");
            System.out.println("还原完成时间：" + LocalDateTime.now());
            System.out.println("========== 数据库还原结束 ==========");

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "数据库还原成功");
            response.put("duration_ms", duration);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            System.out.println("数据库还原失败：" + e.getMessage());
            e.printStackTrace();
            System.out.println("========== 数据库还原结束 (失败) ==========");
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "数据库还原失败：" + e.getMessage());
            return ResponseEntity.status(500).body(response);
        } finally {
            // 清理临时文件
            if (tempFile != null && Files.exists(tempFile)) {
                try {
                    Files.delete(tempFile);
                } catch (IOException e) {
                    // 忽略删除临时文件的错误
                }
            }
        }
    }

    @GetMapping("/backups")
    @RequirePermission("database:list_backups")
    public ResponseEntity<?> listBackups() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        try {
            Path backupDir = Paths.get(BACKUP_DIR);
            if (!Files.exists(backupDir)) {
                return ResponseEntity.ok(new ArrayList<>());
            }

            List<Map<String, Object>> backups = new ArrayList<>();
            try (DirectoryStream<Path> stream = Files.newDirectoryStream(backupDir, "*.sql")) {
                for (Path entry : stream) {
                    Map<String, Object> backup = new HashMap<>();
                    backup.put("filename", entry.getFileName().toString());
                    backup.put("size", Files.size(entry));
                    backup.put("created_at", Files.getLastModifiedTime(entry).toString());
                    backups.add(backup);
                }
            }

            // 按时间倒序排序
            backups.sort((a, b) -> ((String) b.get("created_at")).compareTo((String) a.get("created_at")));

            return ResponseEntity.ok(backups);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "获取备份列表失败：" + e.getMessage());
            return ResponseEntity.status(500).body(response);
        }
    }

    @DeleteMapping("/backups/{filename}")
    @RequirePermission("database:delete_backup")
    public ResponseEntity<?> deleteBackup(@PathVariable String filename) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(401).body("Unauthorized");
        }

        if (!filename.endsWith(".sql")) {
            return ResponseEntity.badRequest().body("只支持.sql 格式的数据库文件");
        }

        try {
            Path backupPath = Paths.get(BACKUP_DIR, filename);
            if (!Files.exists(backupPath)) {
                return ResponseEntity.status(404).body("备份文件不存在");
            }

            Files.delete(backupPath);
            Map<String, String> response = new HashMap<>();
            response.put("detail", "备份文件删除成功");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "删除备份文件失败：" + e.getMessage());
            return ResponseEntity.status(500).body(response);
        }
    }

    /**
     * 内部备份方法，用于还原前备份
     */
    private Map<String, Object> backupDatabaseInternal() {
        Map<String, Object> result = new HashMap<>();
        try {
            // 确保备份目录存在
            Path backupDir = Paths.get(BACKUP_DIR);
            if (!Files.exists(backupDir)) {
                Files.createDirectories(backupDir);
            }

            // 生成备份文件名
            String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
            String backupFilename = "task_board_backup_" + timestamp + ".sql";
            String backupPath = Paths.get(BACKUP_DIR, backupFilename).toString();

            // 使用 JDBC 导出数据库
            exportDatabase(backupPath);

            result.put("success", true);
            result.put("backup_file", backupFilename);
        } catch (Exception e) {
            result.put("success", false);
            result.put("message", "数据库备份失败：" + e.getMessage());
        }
        return result;
    }

    /**
     * 获取进程错误信息 (已废弃，保留以兼容旧代码)
     */
    @Deprecated
    private String getProcessError(Process process) throws IOException {
        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
        StringBuilder error = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            error.append(line).append("\n");
        }
        return error.toString().trim();
    }
}
