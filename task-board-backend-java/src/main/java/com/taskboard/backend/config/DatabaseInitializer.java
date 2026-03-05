package com.taskboard.backend.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.sql.Connection;
import java.sql.Statement;

@Component
public class DatabaseInitializer implements CommandLineRunner {

    @Autowired
    private DataSource dataSource;

    @Override
    public void run(String... args) throws Exception {
        createMissingTables();
    }

    private void createMissingTables() {
        String sql = "CREATE TABLE IF NOT EXISTS user_menus (\n" +
                "    user_id INT NOT NULL,\n" +
                "    menu_id INT NOT NULL,\n" +
                "    PRIMARY KEY (user_id, menu_id),\n" +
                "    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,\n" +
                "    FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE\n" +
                ")";

        String sql2 = "CREATE TABLE IF NOT EXISTS user_permissions (\n" +
                "    user_id INT NOT NULL,\n" +
                "    permission_id INT NOT NULL,\n" +
                "    PRIMARY KEY (user_id, permission_id),\n" +
                "    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,\n" +
                "    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE\n" +
                ")";

        String sql3 = "CREATE TABLE IF NOT EXISTS user_sessions (\n" +
                "    id INT AUTO_INCREMENT PRIMARY KEY,\n" +
                "    user_id INT NOT NULL,\n" +
                "    ip_address VARCHAR(45),\n" +
                "    user_agent TEXT,\n" +
                "    login_at DATETIME DEFAULT CURRENT_TIMESTAMP,\n" +
                "    last_activity_at DATETIME DEFAULT CURRENT_TIMESTAMP,\n" +
                "    is_active BOOLEAN DEFAULT TRUE,\n" +
                "    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE\n" +
                ")";

        try (Connection conn = dataSource.getConnection();
             Statement stmt = conn.createStatement()) {
            
            stmt.addBatch(sql);
            stmt.addBatch(sql2);
            stmt.addBatch(sql3);
            
            stmt.executeBatch();
            
            System.out.println("Database tables created successfully");
        } catch (Exception e) {
            System.err.println("Error creating database tables: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
