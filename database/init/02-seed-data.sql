-- Seed data for Sistema ONG Backend
-- This script inserts initial test data

USE ong_sistema;

-- Insert test users
INSERT INTO usuarios (nombre_usuario, nombre, apellido, telefono, clave_hash, email, rol, activo, usuario_alta) VALUES
('admin', 'Administrador', 'Sistema', '1234567890', '$2b$12$mOwUhpJHoqZlmW.Y3sOoi.Fm0QQ7w9Y9qpQg2eIFBCHhTwTX9bR2.', 'admin@ong.com', 'PRESIDENTE', true, 'system'),
('vocal1', 'Mar??a', 'Gonz??lez', '1234567891', '$2b$12$mOwUhpJHoqZlmW.Y3sOoi.Fm0QQ7w9Y9qpQg2eIFBCHhTwTX9bR2.', 'vocal@ong.com', 'VOCAL', true, 'admin'),
('coord1', 'Juan', 'P??rez', '1234567892', '$2b$12$mOwUhpJHoqZlmW.Y3sOoi.Fm0QQ7w9Y9qpQg2eIFBCHhTwTX9bR2.', 'coordinador@ong.com', 'COORDINADOR', true, 'admin'),
('vol1', 'Ana', 'L??pez', '1234567893', '$2b$12$mOwUhpJHoqZlmW.Y3sOoi.Fm0QQ7w9Y9qpQg2eIFBCHhTwTX9bR2.', 'voluntario@ong.com', 'VOLUNTARIO', true, 'admin');

-- Insert test donations
INSERT INTO donaciones (categoria, descripcion, cantidad, usuario_alta) VALUES
('ALIMENTOS', 'Arroz 1kg', 50, 'vocal1'),
('ROPA', 'Camisetas talle M', 20, 'vocal1'),
('JUGUETES', 'Pelotas de f??tbol', 10, 'vocal1'),
('UTILES_ESCOLARES', 'Cuadernos rayados', 100, 'vocal1');

-- Insert test events
INSERT INTO eventos (nombre, descripcion, fecha_hora, usuario_alta) VALUES
('Entrega de Alimentos', 'Distribuci??n mensual de alimentos', DATE_ADD(NOW(), INTERVAL 7 DAY), 'coord1'),
('Campa??a de Ropa', 'Entrega de ropa de invierno', DATE_ADD(NOW(), INTERVAL 14 DAY), 'coord1');

-- Insert event participants
INSERT INTO evento_participantes (evento_id, usuario_id) VALUES
(1, 3), -- coordinador en evento 1
(1, 4), -- voluntario en evento 1
(2, 3), -- coordinador en evento 2
(2, 4); -- voluntario en evento 2

-- Note: Password for all test users is 'password123'
-- Hash generated with bcrypt for 'password123': $2b$12$mOwUhpJHoqZlmW.Y3sOoi.Fm0QQ7w9Y9qpQg2eIFBCHhTwTX9bR2. (placeholder)
