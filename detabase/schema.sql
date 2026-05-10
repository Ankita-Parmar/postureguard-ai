-- ============================================================
-- PostureGuard AI - MySQL Database Schema
-- Run this file to set up your database
-- Command: mysql -u root -p < database/schema.sql
-- ============================================================

-- Create the database
CREATE DATABASE IF NOT EXISTS postureguard;
USE postureguard;

-- ============================================================
-- Table 1: users
-- Stores registered user accounts
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50)  NOT NULL UNIQUE,
    email       VARCHAR(100) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,       -- bcrypt hashed password
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Table 2: posture_sessions
-- Each row = one monitoring session (start → stop)
-- ============================================================
CREATE TABLE IF NOT EXISTS posture_sessions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    session_start   DATETIME DEFAULT CURRENT_TIMESTAMP,
    session_end     DATETIME,
    total_minutes   INT DEFAULT 0,          -- total minutes in session
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- Table 3: posture_records
-- Individual posture snapshots saved every 30 seconds
-- ============================================================
CREATE TABLE IF NOT EXISTS posture_records (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    session_id      INT,
    risk_level      ENUM('low','medium','high') NOT NULL,
    neck_angle      FLOAT,                  -- degrees, forward head angle
    shoulder_diff   FLOAT,                  -- shoulder height asymmetry in px
    nose_y          FLOAT,                  -- nose landmark y position
    recorded_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)    REFERENCES users(id)             ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES posture_sessions(id)  ON DELETE SET NULL
);

-- ============================================================
-- Table 4: alerts
-- Logs every alert sent to a user
-- ============================================================
CREATE TABLE IF NOT EXISTS alerts (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    alert_type  ENUM('posture','stretch','walk') NOT NULL,
    message     VARCHAR(255),
    sent_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- Sample seed data (optional - for testing)
-- ============================================================
INSERT INTO users (username, email, password) VALUES
('demo_user', 'demo@postureguard.com',
 '$2b$12$KIXVs5./QCLlnzj6FoAbCOLGBrAUqKWp5Ll.9k1ZiIUq7IqpGBuIS'); -- password: demo1234

-- ============================================================
-- Useful queries for the dashboard
-- ============================================================

-- Get risk level counts for a user (last 7 days):
-- SELECT risk_level, COUNT(*) as count
-- FROM posture_records
-- WHERE user_id = ? AND recorded_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
-- GROUP BY risk_level;

-- Get daily average posture records:
-- SELECT DATE(recorded_at) as day, risk_level, COUNT(*) as count
-- FROM posture_records WHERE user_id = ?
-- GROUP BY day, risk_level ORDER BY day DESC LIMIT 7;
