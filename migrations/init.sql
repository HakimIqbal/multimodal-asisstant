CREATE DATABASE IF NOT EXISTS multimodal_assistant_db;
USE multimodal_assistant_db;

CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_format VARCHAR(20) NOT NULL,
    text_content MEDIUMTEXT,
    file_url VARCHAR(255), 
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS general_logs (
    id VARCHAR(36) PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    input TEXT NOT NULL,
    output TEXT NOT NULL,
    metadata JSON
);

CREATE TABLE IF NOT EXISTS coder_logs (
    id VARCHAR(36) PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    input TEXT NOT NULL,
    output TEXT NOT NULL,
    metadata JSON
);

CREATE TABLE IF NOT EXISTS rag_logs (
    id VARCHAR(36) PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    input TEXT NOT NULL,
    output TEXT NOT NULL,
    metadata JSON
);