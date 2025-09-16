-- Seed data for Sistema ONG Backend
-- This script inserts initial test data

USE ong_sistema;

-- Insert test users
INSERT INTO usuarios (nombre_usuario, nombre, apellido, telefono, clave_hash, email, rol, activo, usuario_alta) VALUES
('admin', 'Administrador', 'Sistema', '1234567890', '$2b$10$rQZ9QmZ9QmZ9QmZ9QmZ9Qu', 'admin@ong.com', 'PRESIDENTE', true, 'system'),
('vocal1', 'María', 'González', '1234567891', '$2b$10$rQZ9QmZ9QmZ9QmZ9QmZ9Qu', 'vocal@ong.com', 'VOCAL', true, 'admin'),
('coord1', 'Juan', 'Pérez', '1234567892', '$2b$10$rQZ9QmZ9QmZ9QmZ9QmZ9Qu', 'coordinador@ong.com', 'COORDINADOR', true, 'admin'),
('vol1', 'Ana', 'López', '1234567893', '$2b$10$rQZ9QmZ9QmZ9QmZ9QmZ9Qu', 'voluntario@ong.com', 'VOLUNTARIO', true, 'admin');

-- Insert test donations
INSERT INTO donaciones (categoria, descripcion, cantidad, usuario_alta) VALUES
('ALIMENTOS', 'Arroz 1kg', 50, 'vocal1'),
('ROPA', 'Camisetas talle M', 20, 'vocal1'),
('JUGUETES', 'Pelotas de fútbol', 10, 'vocal1'),
('UTILES_ESCOLARES', 'Cuadernos rayados', 100, 'vocal1');

-- Insert test events
INSERT INTO eventos (nombre, descripcion, fecha_hora, usuario_alta) VALUES
('Entrega de Alimentos', 'Distribución mensual de alimentos', DATE_ADD(NOW(), INTERVAL 7 DAY), 'coord1'),
('Campaña de Ropa', 'Entrega de ropa de invierno', DATE_ADD(NOW(), INTERVAL 14 DAY), 'coord1');

-- Insert event participants
INSERT INTO evento_participantes (evento_id, usuario_id) VALUES
(1, 3), -- coordinador en evento 1
(1, 4), -- voluntario en evento 1
(2, 3), -- coordinador en evento 2
(2, 4); -- voluntario en evento 2

-- Note: Password for all test users is 'password123'
-- Hash generated with bcrypt for 'password123': $2b$10$rQZ9QmZ9QmZ9QmZ9QmZ9Qu (placeholder)