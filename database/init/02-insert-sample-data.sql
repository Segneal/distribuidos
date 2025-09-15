-- Sample data for Sistema ONG
-- This script inserts initial test data

USE ong_sistema;

-- Insert sample users (password is 'password123' hashed with bcrypt)
INSERT INTO usuarios (nombre_usuario, nombre, apellido, telefono, clave_hash, email, rol, usuario_alta) VALUES
('admin', 'Juan', 'Pérez', '+54911234567', '$2b$10$rQZ8kHWKQVz7QGQrQVz7QOQrQVz7QGQrQVz7QOQrQVz7QGQrQVz7QO', 'admin@empujecomunitario.org', 'PRESIDENTE', 'system'),
('vocal1', 'María', 'González', '+54911234568', '$2b$10$rQZ8kHWKQVz7QGQrQVz7QOQrQVz7QGQrQVz7QOQrQVz7QGQrQVz7QO', 'maria@empujecomunitario.org', 'VOCAL', 'admin'),
('coord1', 'Carlos', 'López', '+54911234569', '$2b$10$rQZ8kHWKQVz7QGQrQVz7QOQrQVz7QGQrQVz7QOQrQVz7QGQrQVz7QO', 'carlos@empujecomunitario.org', 'COORDINADOR', 'admin'),
('voluntario1', 'Ana', 'Martínez', '+54911234570', '$2b$10$rQZ8kHWKQVz7QGQrQVz7QOQrQVz7QGQrQVz7QOQrQVz7QGQrQVz7QO', 'ana@empujecomunitario.org', 'VOLUNTARIO', 'admin');

-- Insert sample donations
INSERT INTO donaciones (categoria, descripcion, cantidad, usuario_alta) VALUES
('ALIMENTOS', 'Arroz 1kg', 50, 'vocal1'),
('ALIMENTOS', 'Fideos 500g', 30, 'vocal1'),
('ROPA', 'Remeras talle M', 20, 'vocal1'),
('ROPA', 'Pantalones talle L', 15, 'vocal1'),
('JUGUETES', 'Pelotas de fútbol', 10, 'vocal1'),
('UTILES_ESCOLARES', 'Cuadernos rayados', 100, 'vocal1'),
('UTILES_ESCOLARES', 'Lápices', 200, 'vocal1');

-- Insert sample events (future dates)
INSERT INTO eventos (nombre, descripcion, fecha_hora, usuario_alta) VALUES
('Entrega de Alimentos - Barrio Norte', 'Distribución de alimentos no perecederos', DATE_ADD(NOW(), INTERVAL 7 DAY), 'coord1'),
('Jornada de Juegos - Plaza Central', 'Actividades recreativas para niños', DATE_ADD(NOW(), INTERVAL 14 DAY), 'coord1'),
('Entrega de Útiles Escolares', 'Distribución de material escolar', DATE_ADD(NOW(), INTERVAL 21 DAY), 'coord1');

-- Insert sample event participants
INSERT INTO evento_participantes (evento_id, usuario_id) VALUES
(1, 2), -- María en evento 1
(1, 4), -- Ana en evento 1
(2, 3), -- Carlos en evento 2
(2, 4), -- Ana en evento 2
(3, 2), -- María en evento 3
(3, 3), -- Carlos en evento 3
(3, 4); -- Ana en evento 3