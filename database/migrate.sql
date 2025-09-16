-- Complete Database Migration Script for Sistema ONG
-- This script creates the database and all required tables

-- Create database
CREATE DATABASE IF NOT EXISTS ong_sistema
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE ong_sistema;

-- Drop existing tables if they exist (for clean migration)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS donaciones_repartidas;
DROP TABLE IF EXISTS evento_participantes;
DROP TABLE IF EXISTS eventos_externos;
DROP TABLE IF EXISTS ofertas_externas;
DROP TABLE IF EXISTS solicitudes_externas;
DROP TABLE IF EXISTS eventos;
DROP TABLE IF EXISTS donaciones;
DROP TABLE IF EXISTS usuarios;
SET FOREIGN_KEY_CHECKS = 1;

-- Create usuarios table
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    clave_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    rol ENUM('PRESIDENTE', 'VOCAL', 'COORDINADOR', 'VOLUNTARIO') NOT NULL,
    activo BOOLEAN DEFAULT true,
    fecha_hora_alta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_alta VARCHAR(50),
    fecha_hora_modificacion TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    usuario_modificacion VARCHAR(50),
    INDEX idx_nombre_usuario (nombre_usuario),
    INDEX idx_email (email),
    INDEX idx_rol (rol),
    INDEX idx_activo (activo)
);

-- Create donaciones table
CREATE TABLE donaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    categoria ENUM('ROPA', 'ALIMENTOS', 'JUGUETES', 'UTILES_ESCOLARES') NOT NULL,
    descripcion TEXT,
    cantidad INT NOT NULL CHECK (cantidad >= 0),
    eliminado BOOLEAN DEFAULT false,
    fecha_hora_alta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_alta VARCHAR(50),
    fecha_hora_modificacion TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    usuario_modificacion VARCHAR(50),
    INDEX idx_categoria (categoria),
    INDEX idx_eliminado (eliminado),
    INDEX idx_cantidad (cantidad)
);

-- Create eventos table
CREATE TABLE eventos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_hora TIMESTAMP NOT NULL,
    fecha_hora_alta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_alta VARCHAR(50),
    fecha_hora_modificacion TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    usuario_modificacion VARCHAR(50),
    INDEX idx_fecha_hora (fecha_hora),
    INDEX idx_nombre (nombre)
);

-- Create evento_participantes table
CREATE TABLE evento_participantes (
    evento_id INT,
    usuario_id INT,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (evento_id, usuario_id),
    FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_evento_id (evento_id),
    INDEX idx_usuario_id (usuario_id)
);

-- Create donaciones_repartidas table
CREATE TABLE donaciones_repartidas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evento_id INT,
    donacion_id INT,
    cantidad_repartida INT NOT NULL CHECK (cantidad_repartida > 0),
    usuario_registro VARCHAR(50),
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
    FOREIGN KEY (donacion_id) REFERENCES donaciones(id),
    INDEX idx_evento_id (evento_id),
    INDEX idx_donacion_id (donacion_id)
);

-- Tables for Inter-NGO Network
CREATE TABLE solicitudes_externas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_organizacion VARCHAR(50) NOT NULL,
    id_solicitud VARCHAR(50) NOT NULL,
    categoria ENUM('ROPA', 'ALIMENTOS', 'JUGUETES', 'UTILES_ESCOLARES') NOT NULL,
    descripcion TEXT,
    activa BOOLEAN DEFAULT true,
    fecha_recepcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_solicitud (id_organizacion, id_solicitud),
    INDEX idx_organizacion (id_organizacion),
    INDEX idx_categoria (categoria),
    INDEX idx_activa (activa)
);

CREATE TABLE ofertas_externas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_organizacion VARCHAR(50) NOT NULL,
    id_oferta VARCHAR(50) NOT NULL,
    categoria ENUM('ROPA', 'ALIMENTOS', 'JUGUETES', 'UTILES_ESCOLARES') NOT NULL,
    descripcion TEXT,
    cantidad INT NOT NULL,
    fecha_recepcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_oferta (id_organizacion, id_oferta),
    INDEX idx_organizacion (id_organizacion),
    INDEX idx_categoria (categoria)
);

CREATE TABLE eventos_externos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_organizacion VARCHAR(50) NOT NULL,
    id_evento VARCHAR(50) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_hora TIMESTAMP NOT NULL,
    activo BOOLEAN DEFAULT true,
    fecha_recepcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_evento (id_organizacion, id_evento),
    INDEX idx_organizacion (id_organizacion),
    INDEX idx_fecha_hora (fecha_hora),
    INDEX idx_activo (activo)
);

-- Table for our own donation requests (for audit purposes)
CREATE TABLE solicitudes_propias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_solicitud VARCHAR(50) UNIQUE NOT NULL,
    donaciones_json TEXT NOT NULL,
    usuario_creador VARCHAR(50) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activa BOOLEAN DEFAULT true,
    fecha_baja TIMESTAMP NULL,
    usuario_baja VARCHAR(50) NULL,
    INDEX idx_solicitud (id_solicitud),
    INDEX idx_usuario_creador (usuario_creador),
    INDEX idx_activa (activa),
    INDEX idx_fecha_baja (fecha_baja)
);

-- Table for our own donation offers (for audit purposes)
CREATE TABLE ofertas_propias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_oferta VARCHAR(50) UNIQUE NOT NULL,
    donaciones_json TEXT NOT NULL,
    usuario_creador VARCHAR(50) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activa BOOLEAN DEFAULT true,
    INDEX idx_oferta (id_oferta),
    INDEX idx_usuario_creador (usuario_creador),
    INDEX idx_activa (activa)
);

-- Table for tracking sent transfers (for audit purposes)
CREATE TABLE transferencias_enviadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_solicitud VARCHAR(50) NOT NULL,
    id_organizacion_solicitante VARCHAR(50) NOT NULL,
    donaciones_json TEXT NOT NULL,
    usuario_transferencia VARCHAR(50) NOT NULL,
    fecha_transferencia TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_solicitud (id_solicitud),
    INDEX idx_organizacion (id_organizacion_solicitante),
    INDEX idx_usuario (usuario_transferencia)
);

-- Table for tracking received transfers (for audit purposes)
CREATE TABLE transferencias_recibidas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_solicitud VARCHAR(50) NOT NULL,
    id_organizacion_donante VARCHAR(50) NOT NULL,
    donaciones_json TEXT NOT NULL,
    fecha_recepcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_solicitud (id_solicitud),
    INDEX idx_organizacion (id_organizacion_donante)
);

-- Insert default admin user (password: 'admin123')
-- Note: In production, this should be changed immediately
INSERT INTO usuarios (nombre_usuario, nombre, apellido, telefono, clave_hash, email, rol, usuario_alta) VALUES
('admin', 'Administrador', 'Sistema', '+54911000000', '$2b$10$rQZ8kHWKQVz7QGQrQVz7QOQrQVz7QGQrQVz7QOQrQVz7QGQrQVz7QO', 'admin@empujecomunitario.org', 'PRESIDENTE', 'system');

COMMIT;