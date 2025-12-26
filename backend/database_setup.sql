-- Create database
CREATE DATABASE IF NOT EXISTS cloud_recommendation_db;
USE cloud_recommendation_db;

-- Create users table
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create recommendations table
CREATE TABLE IF NOT EXISTS recommendation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    provider VARCHAR(50) NOT NULL,
    instance_type VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    price_per_hour DECIMAL(10, 6) NOT NULL,
    vcpu INT NOT NULL,
    ram_gb INT NOT NULL,
    storage_gb INT NOT NULL,
    security_score INT NOT NULL,
    topsis_score DECIMAL(10, 6) NOT NULL,
    ai_explanation TEXT,
    user_requirements JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- Create ratings table
CREATE TABLE IF NOT EXISTS rating (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    recommendation_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (recommendation_id) REFERENCES recommendation(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_recommendation (user_id, recommendation_id)
);

-- Create indexes for better performance
CREATE INDEX idx_user_email ON user(email);
CREATE INDEX idx_recommendation_user ON recommendation(user_id);
CREATE INDEX idx_recommendation_created ON recommendation(created_at);
CREATE INDEX idx_rating_recommendation ON rating(recommendation_id);
CREATE INDEX idx_rating_user ON rating(user_id);

-- Insert sample data (optional)
INSERT INTO user (username, email, password_hash) VALUES 
('demo_user', 'demo@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PZvO.e'),
('test_user', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PZvO.e');

SHOW TABLES;