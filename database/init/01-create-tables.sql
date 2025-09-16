-- Sistema ONG Database Initialization Script
-- This script creates the initial database structure

USE ong_sistema;

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

-- Create auditoria_stock table for stock change tracking
CREATE TABLE auditoria_stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donacion_id INT NOT NULL,
    cantidad_anterior INT NOT NULL,
    cantidad_nueva INT NOT NULL,
    cantidad_cambio INT NOT NULL,
    motivo TEXT,
    usuario_modificacion VARCHAR(50),
    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donacion_id) REFERENCES donaciones(id),
    INDEX idx_donacion_id (donacion_id),
    INDEX idx_fecha_cambio (fecha_cambio),
    INDEX idx_usuario_modificacion (usuario_modificacion)
);

-- Create tables for tracking donation transfers
CREATE TABLE solicitudes_propias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_solicitud VARCHAR(50) UNIQUE NOT NULL,
    donaciones_json JSON NOT NULL,
    usuario_creador VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activa BOOLEAN DEFAULT true,
    fecha_baja TIMESTAMP NULL,
    usuario_baja VARCHAR(50) NULL,
    INDEX idx_id_solicitud (id_solicitud),
    INDEX idx_fecha_creacion (fecha_creacion),
    INDEX idx_activa (activa),
    INDEX idx_fecha_baja (fecha_baja)
);

CREATE TABLE transferencias_enviadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_solicitud VARCHAR(50) NOT NULL,
    id_organizacion_solicitante VARCHAR(50) NOT NULL,
    donaciones_json JSON NOT NULL,
    usuario_transferencia VARCHAR(50),
    fecha_transferencia TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_id_solicitud (id_solicitud),
    INDEX idx_organizacion_solicitante (id_organizacion_solicitante),
    INDEX idx_fecha_transferencia (fecha_transferencia)
);

CREATE TABLE transferencias_recibidas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_solicitud VARCHAR(50) NOT NULL,
    id_organizacion_donante VARCHAR(50) NOT NULL,
    donaciones_json JSON NOT NULL,
    fecha_recepcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_transferencia (id_solicitud, id_organizacion_donante),
    INDEX idx_id_solicitud (id_solicitud),
    INDEX idx_organizacion_donante (id_organizacion_donante),
    INDEX idx_fecha_recepcion (fecha_recepcion)
);

-- Create table for tracking adhesions to external events
CREATE TABLE adhesiones_eventos_externos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_organizacion VARCHAR(50) NOT NULL,
    id_evento VARCHAR(50) NOT NULL,
    usuario_id INT NOT NULL,
    fecha_adhesion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_adhesion (id_organizacion, id_evento, usuario_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_organizacion (id_organizacion),
    INDEX idx_evento (id_evento),
    INDEX idx_usuario_id (usuario_id),
    INDEX idx_fecha_adhesion (fecha_adhesion)
);

-- Create table for tracking own donation offers
CREATE TABLE ofertas_propias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_oferta VARCHAR(50) UNIQUE NOT NULL,
    donaciones_json JSON NOT NULL,
    usuario_creador VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_id_oferta (id_oferta),
    INDEX idx_fecha_creacion (fecha_creacion)
);