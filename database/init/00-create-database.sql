-- Create the main database for Sistema ONG
-- This script should be run first to create the database

CREATE DATABASE IF NOT EXISTS ong_sistema
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Create a dedicated user for the application (optional, for production)
-- CREATE USER IF NOT EXISTS 'ong_user'@'%' IDENTIFIED BY 'ong_password';
-- GRANT ALL PRIVILEGES ON ong_sistema.* TO 'ong_user'@'%';
-- FLUSH PRIVILEGES;

USE ong_sistema;