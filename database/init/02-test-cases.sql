-- ============================================
-- CASOS DE PRUEBA CENTRALIZADOS
-- Sistema ONG - SQL Driven Testing
-- ============================================

USE ong_sistema;

-- ============================================
-- USUARIOS PARA TESTING POR ROL
-- ============================================

-- Usuarios para casos de éxito por rol (password: test123)
INSERT INTO usuarios (id, nombre_usuario, nombre, apellido, telefono, clave_hash, email, rol, activo, usuario_alta) VALUES
-- Casos de éxito por rol
(1, 'test_presidente', 'Juan Carlos', 'Presidente Test', '1111111111', '.jbTxeM2K5N3L4P6Q7R8S9T0U1V2W3X4Y', 'presidente@test.com', 'PRESIDENTE', true, 'system'),
(2, 'test_vocal', 'María Elena', 'Vocal Test', '2222222222', '.jbTxeM2K5N3L4P6Q7R8S9T0U1V2W3X4Y', 'vocal@test.com', 'VOCAL', true, 'test_presidente'),
(3, 'test_coordinador', 'Carlos Alberto', 'Coordinador Test', '3333333333', '.jbTxeM2K5N3L4P6Q7R8S9T0U1V2W3X4Y', 'coordinador@test.com', 'COORDINADOR', true, 'test_presidente'),
(4, 'test_voluntario', 'Ana Sofía', 'Voluntario Test', '4444444444', '.jbTxeM2K5N3L4P6Q7R8S9T0U1V2W3X4Y', 'voluntario@test.com', 'VOLUNTARIO', true, 'test_coordinador'),

-- Casos de error - usuarios inactivos
(5, 'test_inactivo', 'Pedro Luis', 'Usuario Inactivo', '5555555555', '.jbTxeM2K5N3L4P6Q7R8S9T0U1V2W3X4Y', 'inactivo@test.com', 'VOLUNTARIO', false, 'test_coordinador'),

-- Casos límite - usuarios con datos mínimos/máximos
(6, 'test_limite_min', 'A', 'B', '1000000000', '.jbTxeM2K5N3L4P6Q7R8S9T0U1V2W3X4Y', 'min@test.com', 'VOLUNTARIO', true, 'test_coordinador'),
(7, 'test_limite_max', 'NombreMuyLargoParaProbarLimitesDeValidacionDeNombres', 'ApellidoMuyLargoParaProbarLimitesDeValidacionDeApellidos', '9999999999', '.jbTxeM2K5N3L4P6Q7R8S9T0U1V2W3X4Y', 'max@test.com', 'VOLUNTARIO', true, 'test_coordinador'),

-- Usuarios adicionales para testing de autorización
(8, 'test_vocal_2', 'Laura Patricia', 'Vocal Secundario', '6666666666', '.jbTxeM2K5N3L4P6Q7R8S9T0U1V2W3X4Y', 'vocal2@test.com', 'VOCAL', true, 'test_presidente'),
(9, 'test_coordinador_2', 'Roberto Miguel', 'Coordinador Secundario', '7777777777', '.jbTxeM2K5N3L4P6Q7R8S9T0U1V2W3X4Y', 'coordinador2@test.com', 'COORDINADOR', true, 'test_presidente'),
(10, 'test_voluntario_2', 'Carmen Rosa', 'Voluntario Secundario', '8888888888', '.jbTxeM2K5N3L4P6Q7R8S9T0U1V2W3X4Y', 'voluntario2@test.com', 'VOLUNTARIO', true, 'test_coordinador_2');

-- ============================================
-- DONACIONES PARA TESTING DE INVENTARIO
-- ============================================

INSERT INTO donaciones (id, categoria, descripcion, cantidad, usuario_alta, fecha_hora_alta) VALUES
-- Casos de éxito - stock suficiente por categoría
(101, 'ALIMENTOS', 'Arroz integral 1kg - Stock Alto', 100, 'test_vocal', NOW()),
(102, 'ALIMENTOS', 'Fideos secos 500g - Stock Alto', 85, 'test_vocal', NOW()),
(103, 'ALIMENTOS', 'Leche en polvo 1kg - Para Transferencia', 25, 'test_vocal', NOW()),
(104, 'ALIMENTOS', 'Conservas de atún - Stock Medio', 40, 'test_vocal', NOW()),
(105, 'ALIMENTOS', 'Aceite de girasol 1L - Stock Bajo', 8, 'test_vocal', NOW()),
(106, 'ALIMENTOS', 'Azúcar 1kg - Stock Cero', 0, 'test_vocal', NOW()),

(107, 'ROPA', 'Camisetas talle M - Stock Alto', 50, 'test_vocal', NOW()),
(108, 'ROPA', 'Pantalones talle L - Para Transferencia', 15, 'test_vocal', NOW()),
(109, 'ROPA', 'Camperas de invierno - Stock Medio', 20, 'test_vocal', NOW()),
(110, 'ROPA', 'Medias adulto - Stock Bajo', 5, 'test_vocal', NOW()),
(111, 'ROPA', 'Zapatos deportivos - Stock Cero', 0, 'test_vocal', NOW()),

(112, 'JUGUETES', 'Pelotas de fútbol - Stock Alto', 30, 'test_vocal', NOW()),
(113, 'JUGUETES', 'Muñecas - Stock Medio', 12, 'test_vocal', NOW()),
(114, 'JUGUETES', 'Rompecabezas - Stock Bajo', 3, 'test_vocal', NOW()),
(115, 'JUGUETES', 'Bloques de construcción - Stock Cero', 0, 'test_vocal', NOW()),

(116, 'UTILES_ESCOLARES', 'Cuadernos rayados - Stock Alto', 75, 'test_vocal', NOW()),
(117, 'UTILES_ESCOLARES', 'Lápices de colores - Stock Medio', 25, 'test_vocal', NOW()),
(118, 'UTILES_ESCOLARES', 'Mochilas escolares - Stock Bajo', 4, 'test_vocal', NOW()),
(119, 'UTILES_ESCOLARES', 'Reglas 30cm - Stock Cero', 0, 'test_vocal', NOW()),

-- Casos límite - cantidades extremas
(120, 'ALIMENTOS', 'Fideos - Cantidad Máxima', 999999, 'test_vocal', NOW()),
(121, 'ROPA', 'Medias - Cantidad Mínima', 1, 'test_vocal', NOW()),

-- Donaciones eliminadas (para testing de soft delete)
(122, 'ALIMENTOS', 'Producto Eliminado', 10, 'test_vocal', NOW()),
(123, 'ROPA', 'Ropa Eliminada', 5, 'test_vocal', NOW());

-- Marcar algunas donaciones como eliminadas
UPDATE donaciones SET eliminado = true WHERE id IN (122, 123);

-- ============================================
-- EVENTOS PARA TESTING
-- ============================================

INSERT INTO eventos (id, nombre, descripcion, fecha_hora, usuario_alta, fecha_hora_alta) VALUES
-- Casos de éxito - eventos futuros
(201, 'Evento Test Futuro 1', 'Evento para testing de participación y gestión', DATE_ADD(NOW(), INTERVAL 7 DAY), 'test_coordinador', NOW()),
(202, 'Evento Test Futuro 2', 'Evento para testing de adhesión externa', DATE_ADD(NOW(), INTERVAL 14 DAY), 'test_coordinador', NOW()),
(203, 'Evento Test Futuro 3', 'Evento para testing de múltiples participantes', DATE_ADD(NOW(), INTERVAL 21 DAY), 'test_coordinador_2', NOW()),

-- Casos de error - eventos pasados
(204, 'Evento Test Pasado', 'Evento pasado para testing de validaciones', DATE_SUB(NOW(), INTERVAL 7 DAY), 'test_coordinador', NOW()),
(205, 'Evento Test Muy Pasado', 'Evento muy pasado para testing', DATE_SUB(NOW(), INTERVAL 30 DAY), 'test_coordinador', NOW()),

-- Casos límite - eventos límite de fecha
(206, 'Evento Test Hoy', 'Evento de hoy para testing de límites', NOW(), 'test_coordinador', NOW()),
(207, 'Evento Test Futuro Lejano', 'Evento muy futuro para testing', DATE_ADD(NOW(), INTERVAL 365 DAY), 'test_coordinador', NOW());

-- ============================================
-- PARTICIPANTES EN EVENTOS
-- ============================================

INSERT INTO evento_participantes (evento_id, usuario_id, fecha_asignacion) VALUES
-- Participantes en eventos futuros
(201, 3, NOW()), -- coordinador en evento futuro 1
(201, 4, NOW()), -- voluntario en evento futuro 1
(201, 10, NOW()), -- voluntario 2 en evento futuro 1

(202, 4, NOW()), -- voluntario en evento futuro 2
(202, 9, NOW()), -- coordinador 2 en evento futuro 2

(203, 4, NOW()), -- voluntario en evento futuro 3
(203, 10, NOW()), -- voluntario 2 en evento futuro 3

-- Participantes en eventos pasados (para testing de validaciones)
(204, 4, DATE_SUB(NOW(), INTERVAL 10 DAY)), -- voluntario en evento pasado
(205, 10, DATE_SUB(NOW(), INTERVAL 35 DAY)); -- voluntario 2 en evento muy pasado

-- ============================================
-- DONACIONES REPARTIDAS (PARA TESTING DE EVENTOS)
-- ============================================

INSERT INTO donaciones_repartidas (evento_id, donacion_id, cantidad_repartida, usuario_registro, fecha_hora_registro) VALUES
-- Donaciones repartidas en eventos pasados
(204, 101, 10, 'test_coordinador', DATE_SUB(NOW(), INTERVAL 6 DAY)),
(204, 107, 5, 'test_coordinador', DATE_SUB(NOW(), INTERVAL 6 DAY)),
(205, 102, 15, 'test_coordinador', DATE_SUB(NOW(), INTERVAL 29 DAY)),
(205, 112, 3, 'test_coordinador', DATE_SUB(NOW(), INTERVAL 29 DAY));

-- ============================================
-- DATOS PARA TESTING INTER-ONG (KAFKA)
-- ============================================

-- Solicitudes externas (simulando mensajes Kafka recibidos)
INSERT INTO solicitudes_externas (id_organizacion, id_solicitud, categoria, descripcion, activa, fecha_recepcion) VALUES
('ong-corazon-solidario', 'sol-001', 'ALIMENTOS', 'Arroz y fideos para familias necesitadas', true, NOW()),
('ong-corazon-solidario', 'sol-002', 'ROPA', 'Ropa de invierno para adultos', true, NOW()),
('ong-manos-unidas', 'sol-003', 'JUGUETES', 'Juguetes educativos para niños', true, NOW()),
('ong-manos-unidas', 'sol-004', 'UTILES_ESCOLARES', 'Útiles escolares para primaria', true, NOW()),
('ong-esperanza', 'sol-005', 'ALIMENTOS', 'Leche en polvo para bebés', true, NOW()),
('ong-esperanza', 'sol-006', 'ROPA', 'Ropa para bebés y niños pequeños', false, NOW()),
('ong-inactiva', 'sol-007', 'ALIMENTOS', 'Solicitud de ONG inactiva', true, NOW());

-- Ofertas externas (simulando ofertas de otras ONGs)
INSERT INTO ofertas_externas (id_organizacion, id_oferta, categoria, descripcion, cantidad, fecha_recepcion) VALUES
('ong-corazon-solidario', 'of-001', 'UTILES_ESCOLARES', 'Útiles escolares variados', 50, NOW()),
('ong-corazon-solidario', 'of-002', 'JUGUETES', 'Juguetes didácticos', 20, NOW()),
('ong-manos-unidas', 'of-003', 'ALIMENTOS', 'Conservas y alimentos no perecederos', 30, NOW()),
('ong-manos-unidas', 'of-004', 'ROPA', 'Ropa de verano para niños', 25, NOW()),
('ong-esperanza', 'of-005', 'ALIMENTOS', 'Productos de panadería', 15, NOW()),
('ong-esperanza', 'of-006', 'UTILES_ESCOLARES', 'Libros de texto usados', 40, NOW());

-- Eventos externos (simulando eventos solidarios de otras ONGs)
INSERT INTO eventos_externos (id_organizacion, id_evento, nombre, descripcion, fecha_hora, activo, fecha_recepcion) VALUES
('ong-corazon-solidario', 'ev-ext-001', 'Campaña de Invierno 2024', 'Distribución de ropa de invierno y alimentos calientes', DATE_ADD(NOW(), INTERVAL 10 DAY), true, NOW()),
('ong-corazon-solidario', 'ev-ext-002', 'Jornada Solidaria Navideña', 'Entrega de juguetes y cena navideña', DATE_ADD(NOW(), INTERVAL 45 DAY), true, NOW()),
('ong-manos-unidas', 'ev-ext-003', 'Feria de Útiles Escolares', 'Distribución gratuita de útiles escolares', DATE_ADD(NOW(), INTERVAL 15 DAY), true, NOW()),
('ong-manos-unidas', 'ev-ext-004', 'Maratón Solidaria', 'Evento deportivo con fines benéficos', DATE_ADD(NOW(), INTERVAL 30 DAY), true, NOW()),
('ong-esperanza', 'ev-ext-005', 'Taller de Capacitación', 'Taller de oficios para jóvenes', DATE_ADD(NOW(), INTERVAL 20 DAY), true, NOW()),
('ong-esperanza', 'ev-ext-006', 'Evento Pasado', 'Evento que ya ocurrió', DATE_SUB(NOW(), INTERVAL 5 DAY), false, NOW()),
('ong-inactiva', 'ev-ext-007', 'Evento de ONG Inactiva', 'Evento de organización inactiva', DATE_ADD(NOW(), INTERVAL 25 DAY), true, NOW());

-- ============================================
-- SOLICITUDES Y OFERTAS PROPIAS
-- ============================================

INSERT INTO solicitudes_propias (id_solicitud, donaciones_json, usuario_creador, fecha_creacion, activa) VALUES
('req-001', '[{"categoria":"ALIMENTOS","descripcion":"Arroz y aceite para comedores comunitarios"}]', 'test_vocal', NOW(), true),
('req-002', '[{"categoria":"ROPA","descripcion":"Ropa de invierno para adultos"},{"categoria":"UTILES_ESCOLARES","descripcion":"Cuadernos y lápices"}]', 'test_vocal', NOW(), true),
('req-003', '[{"categoria":"JUGUETES","descripcion":"Juguetes para día del niño"}]', 'test_vocal_2', NOW(), false),
('req-004', '[{"categoria":"ALIMENTOS","descripcion":"Leche en polvo para programa nutricional"}]', 'test_vocal', DATE_SUB(NOW(), INTERVAL 7 DAY), true);

INSERT INTO ofertas_propias (id_oferta, donaciones_json, usuario_creador, fecha_creacion) VALUES
('off-001', '[{"categoria":"ALIMENTOS","descripcion":"Conservas variadas","cantidad":20}]', 'test_vocal', NOW()),
('off-002', '[{"categoria":"ROPA","descripcion":"Camisetas talle M","cantidad":15}]', 'test_vocal', NOW()),
('off-003', '[{"categoria":"JUGUETES","descripcion":"Pelotas de fútbol","cantidad":8}]', 'test_vocal_2', NOW()),
('off-004', '[{"categoria":"UTILES_ESCOLARES","descripcion":"Cuadernos rayados","cantidad":25}]', 'test_vocal', DATE_SUB(NOW(), INTERVAL 3 DAY));

-- ============================================
-- TABLA DE MAPEO DE CASOS DE PRUEBA
-- ============================================

-- Crear tabla para mapear casos de prueba a endpoints específicos
CREATE TABLE IF NOT EXISTS test_case_mapping (
    id INT AUTO_INCREMENT PRIMARY KEY,
    endpoint VARCHAR(200) NOT NULL,
    method ENUM('GET', 'POST', 'PUT', 'DELETE', 'PATCH') NOT NULL,
    test_type ENUM('success', 'error', 'validation', 'authorization', 'edge_case') NOT NULL,
    user_id INT NULL,
    resource_id INT NULL,
    description TEXT NOT NULL,
    expected_status INT NOT NULL,
    request_body JSON NULL,
    expected_response_fields JSON NULL,
    test_category VARCHAR(50) NOT NULL,
    INDEX idx_endpoint (endpoint),
    INDEX idx_test_type (test_type),
    INDEX idx_test_category (test_category),
    FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE SET NULL
);

-- ============================================
-- MAPEO DE CASOS DE PRUEBA PARA AUTENTICACIÓN
-- ============================================

INSERT INTO test_case_mapping (endpoint, method, test_type, user_id, resource_id, description, expected_status, request_body, expected_response_fields, test_category) VALUES
-- Casos de éxito de login
('/api/auth/login', 'POST', 'success', 1, NULL, 'Login exitoso - Presidente', 200, 
 '{"nombreUsuario":"test_presidente","clave":"test123"}', 
 '["token","usuario","rol"]', 'authentication'),
('/api/auth/login', 'POST', 'success', 2, NULL, 'Login exitoso - Vocal', 200, 
 '{"nombreUsuario":"test_vocal","clave":"test123"}', 
 '["token","usuario","rol"]', 'authentication'),
('/api/auth/login', 'POST', 'success', 3, NULL, 'Login exitoso - Coordinador', 200, 
 '{"nombreUsuario":"test_coordinador","clave":"test123"}', 
 '["token","usuario","rol"]', 'authentication'),
('/api/auth/login', 'POST', 'success', 4, NULL, 'Login exitoso - Voluntario', 200, 
 '{"nombreUsuario":"test_voluntario","clave":"test123"}', 
 '["token","usuario","rol"]', 'authentication'),

-- Casos de error de login
('/api/auth/login', 'POST', 'error', 5, NULL, 'Login fallido - Usuario inactivo', 401, 
 '{"nombreUsuario":"test_inactivo","clave":"test123"}', 
 '["error","message"]', 'authentication'),
('/api/auth/login', 'POST', 'validation', NULL, NULL, 'Login fallido - Credenciales inválidas', 401, 
 '{"nombreUsuario":"test_presidente","clave":"wrong_password"}', 
 '["error","message"]', 'authentication');

-- ============================================
-- MAPEO DE CASOS DE PRUEBA PARA USUARIOS
-- ============================================

INSERT INTO test_case_mapping (endpoint, method, test_type, user_id, resource_id, description, expected_status, request_body, expected_response_fields, test_category) VALUES
-- Casos para usuarios
('/api/usuarios', 'GET', 'success', 1, NULL, 'Listar usuarios - Presidente', 200, NULL, '["usuarios","total"]', 'users'),
('/api/usuarios', 'GET', 'authorization', 4, NULL, 'Listar usuarios - Sin permisos (Voluntario)', 403, NULL, '["error","message"]', 'users'),
('/api/usuarios/{id}', 'GET', 'success', 1, 2, 'Obtener usuario específico - Vocal', 200, NULL, '["id","nombreUsuario","nombre","apellido","email","rol"]', 'users'),
('/api/usuarios/{id}', 'GET', 'error', 1, 999, 'Usuario no encontrado', 404, NULL, '["error","message"]', 'users');

-- ============================================
-- MAPEO DE CASOS DE PRUEBA PARA INVENTARIO
-- ============================================

INSERT INTO test_case_mapping (endpoint, method, test_type, user_id, resource_id, description, expected_status, request_body, expected_response_fields, test_category) VALUES
-- Casos para inventario
('/api/inventario/donaciones', 'GET', 'success', 2, NULL, 'Listar donaciones - Vocal', 200, NULL, '["donaciones","total"]', 'inventory'),
('/api/inventario/donaciones', 'POST', 'success', 2, NULL, 'Crear donación - Vocal', 201, '{"categoria":"ALIMENTOS","descripcion":"Arroz integral nuevo","cantidad":50}', '["id","mensaje"]', 'inventory'),
('/api/inventario/donaciones', 'POST', 'authorization', 4, NULL, 'Crear donación - Sin permisos (Voluntario)', 403, '{"categoria":"ALIMENTOS","descripcion":"Intento crear","cantidad":10}', '["error","message"]', 'inventory'),
('/api/inventario/donaciones/{id}', 'GET', 'success', 2, 101, 'Obtener donación específica - Arroz', 200, NULL, '["id","categoria","descripcion","cantidad"]', 'inventory'),
('/api/inventario/donaciones/{id}', 'PUT', 'success', 2, 101, 'Actualizar donación - Cantidad válida', 200, '{"descripcion":"Arroz integral 1kg - Actualizado","cantidad":95}', '["mensaje"]', 'inventory');

-- ============================================
-- MAPEO DE CASOS DE PRUEBA PARA EVENTOS
-- ============================================

INSERT INTO test_case_mapping (endpoint, method, test_type, user_id, resource_id, description, expected_status, request_body, expected_response_fields, test_category) VALUES
-- Casos para eventos
('/api/eventos', 'GET', 'success', 3, NULL, 'Listar eventos - Coordinador', 200, NULL, '["eventos","total"]', 'events'),
('/api/eventos', 'POST', 'success', 3, NULL, 'Crear evento futuro - Coordinador', 201, '{"nombre":"Evento Test Nuevo","descripcion":"Descripción del evento","fechaHora":"2024-12-31T15:00:00Z"}', '["id","mensaje"]', 'events'),
('/api/eventos', 'POST', 'authorization', 4, NULL, 'Crear evento - Sin permisos (Voluntario)', 403, '{"nombre":"Intento Evento","descripcion":"Test","fechaHora":"2024-12-31T15:00:00Z"}', '["error","message"]', 'events'),
('/api/eventos/{id}/participantes', 'POST', 'success', 4, 201, 'Unirse a evento futuro - Voluntario', 200, '{"usuarioId":4}', '["mensaje"]', 'events'),
('/api/eventos/{id}/participantes', 'POST', 'error', 4, 204, 'Unirse a evento pasado - Error', 400, '{"usuarioId":4}', '["error","message"]', 'events');

-- ============================================
-- MAPEO DE CASOS DE PRUEBA PARA RED INTER-ONG
-- ============================================

INSERT INTO test_case_mapping (endpoint, method, test_type, user_id, resource_id, description, expected_status, request_body, expected_response_fields, test_category) VALUES
-- Casos para red inter-ONG
('/api/red/solicitudes-donaciones', 'GET', 'success', 2, NULL, 'Listar solicitudes externas - Vocal', 200, NULL, '["solicitudes","total"]', 'network'),
('/api/red/solicitudes-donaciones', 'POST', 'success', 2, NULL, 'Crear solicitud donaciones - Vocal', 201, '{"donaciones":[{"categoria":"ALIMENTOS","descripcion":"Arroz para comedores"}]}', '["idSolicitud","mensaje"]', 'network'),
('/api/red/ofertas-donaciones', 'POST', 'success', 2, 105, 'Crear oferta donaciones - Con stock', 201, '{"donaciones":[{"id":105,"categoria":"ALIMENTOS","descripcion":"Aceite de girasol","cantidad":5}]}', '["idOferta","mensaje"]', 'network'),
('/api/red/transferencias-donaciones', 'POST', 'success', 2, 103, 'Transferir donaciones - Stock suficiente', 200, '{"idSolicitud":"sol-001","organizacionDestino":"ong-corazon-solidario","donaciones":[{"id":103,"cantidad":10}]}', '["mensaje","transferencia"]', 'network'),
('/api/red/eventos-externos/adhesion', 'POST', 'success', 4, NULL, 'Adherirse a evento externo - Voluntario', 200, '{"idOrganizacion":"ong-corazon-solidario","idEvento":"ev-ext-001"}', '["mensaje"]', 'network');

-- ============================================
-- AUDITORÍA Y TRANSFERENCIAS
-- ============================================

-- Transferencias enviadas
INSERT INTO transferencias_enviadas (id_solicitud, id_organizacion_solicitante, donaciones_json, usuario_transferencia, fecha_transferencia) VALUES
('sol-001', 'ong-corazon-solidario', '[{"id":101,"categoria":"ALIMENTOS","descripcion":"Arroz integral 1kg","cantidad":10}]', 'test_vocal', DATE_SUB(NOW(), INTERVAL 2 DAY)),
('sol-003', 'ong-manos-unidas', '[{"id":112,"categoria":"JUGUETES","descripcion":"Pelotas de fútbol","cantidad":5}]', 'test_vocal', DATE_SUB(NOW(), INTERVAL 1 DAY));

-- Transferencias recibidas
INSERT INTO transferencias_recibidas (id_solicitud, id_organizacion_donante, donaciones_json, fecha_recepcion) VALUES
('req-001', 'ong-corazon-solidario', '[{"categoria":"ALIMENTOS","descripcion":"Aceite de girasol 1L","cantidad":5}]', DATE_SUB(NOW(), INTERVAL 1 DAY)),
('req-002', 'ong-manos-unidas', '[{"categoria":"UTILES_ESCOLARES","descripcion":"Lápices de colores","cantidad":30}]', NOW());

-- Adhesiones a eventos externos
INSERT INTO adhesiones_eventos_externos (id_organizacion, id_evento, usuario_id, fecha_adhesion) VALUES
('ong-corazon-solidario', 'ev-ext-001', 4, NOW()),
('ong-corazon-solidario', 'ev-ext-002', 4, NOW()),
('ong-manos-unidas', 'ev-ext-003', 4, NOW()),
('ong-esperanza', 'ev-ext-005', 10, NOW());

-- Auditoría de stock
INSERT INTO auditoria_stock (donacion_id, cantidad_anterior, cantidad_nueva, cantidad_cambio, motivo, usuario_modificacion, fecha_cambio) VALUES
(101, 110, 100, -10, 'Transferencia a ong-corazon-solidario', 'test_vocal', DATE_SUB(NOW(), INTERVAL 2 DAY)),
(112, 35, 30, -5, 'Transferencia a ong-manos-unidas', 'test_vocal', DATE_SUB(NOW(), INTERVAL 1 DAY)),
(107, 45, 50, 5, 'Recepción de donación externa', 'test_vocal', DATE_SUB(NOW(), INTERVAL 3 DAY)),
(117, 20, 25, 5, 'Recepción de transferencia inter-ONG', 'test_vocal', NOW());

-- ============================================
-- COMENTARIOS FINALES
-- ============================================

-- Este script SQL centraliza todos los casos de prueba necesarios para el testing
-- completo del sistema ONG. Incluye:
--
-- 1. Usuarios de prueba para todos los roles con casos de éxito, error y límite
-- 2. Donaciones de prueba para todas las categorías con diferentes niveles de stock
-- 3. Eventos de prueba con casos futuros, pasados y límite
-- 4. Datos completos para testing de comunicación inter-ONG via Kafka
-- 5. Tabla de mapeo que relaciona cada caso de prueba con endpoints específicos
-- 6. Casos de auditoría y trazabilidad de operaciones
--
-- Los datos insertados permiten generar automáticamente:
-- - Colecciones Postman con datos reales
-- - Ejemplos de Swagger con casos válidos
-- - Escenarios de testing Kafka inter-ONG
-- - Tests de integración end-to-end
--
-- Todos los casos están mapeados a endpoints específicos con sus respectivos
-- códigos de estado esperados, facilitando la generación automática de
-- configuraciones de testing.
--
-- Para usar este script:
-- 1. Ejecutar después de 01-create-tables.sql
-- 2. Los datos estarán disponibles para extracción automática
-- 3. Usar password 'test123' para todos los usuarios de prueba
-- 4. Los IDs están fijos para facilitar referencias en testing

-- ============================================
-- AUDITORÍA Y TRANSFERENCIAS
-- ============================================

-- Transferencias enviadas
INSERT INTO transferencias_enviadas (id_solicitud, id_organizacion_solicitante, donaciones_json, usuario_transferencia, fecha_transferencia) VALUES
('sol-001', 'ong-corazon-solidario', '[{\"id\":101,\"categoria\":\"ALIMENTOS\",\"descripcion\":\"Arroz integral 1kg\",\"cantidad\":10}]', 'test_vocal', DATE_SUB(NOW(), INTERVAL 2 DAY)),
('sol-003', 'ong-manos-unidas', '[{\"id\":112,\"categoria\":\"JUGUETES\",\"descripcion\":\"Pelotas de fútbol\",\"cantidad\":5}]', 'test_vocal', DATE_SUB(NOW(), INTERVAL 1 DAY));

-- Transferencias recibidas
INSERT INTO transferencias_recibidas (id_solicitud, id_organizacion_donante, donaciones_json, fecha_recepcion) VALUES
('req-001', 'ong-corazon-solidario', '[{\"categoria\":\"ALIMENTOS\",\"descripcion\":\"Aceite de girasol 1L\",\"cantidad\":5}]', DATE_SUB(NOW(), INTERVAL 1 DAY)),
('req-002', 'ong-manos-unidas', '[{\"categoria\":\"UTILES_ESCOLARES\",\"descripcion\":\"Lápices de colores\",\"cantidad\":30}]', NOW());

-- Adhesiones a eventos externos
INSERT INTO adhesiones_eventos_externos (id_organizacion, id_evento, usuario_id, fecha_adhesion) VALUES
('ong-corazon-solidario', 'ev-ext-001', 4, NOW()),
('ong-corazon-solidario', 'ev-ext-002', 4, NOW()),
('ong-manos-unidas', 'ev-ext-003', 4, NOW()),
('ong-esperanza', 'ev-ext-005', 10, NOW());

-- Auditoría de stock
INSERT INTO auditoria_stock (donacion_id, cantidad_anterior, cantidad_nueva, cantidad_cambio, motivo, usuario_modificacion, fecha_cambio) VALUES
(101, 110, 100, -10, 'Transferencia a ong-corazon-solidario', 'test_vocal', DATE_SUB(NOW(), INTERVAL 2 DAY)),
(112, 35, 30, -5, 'Transferencia a ong-manos-unidas', 'test_vocal', DATE_SUB(NOW(), INTERVAL 1 DAY)),
(107, 45, 50, 5, 'Recepción de donación externa', 'test_vocal', DATE_SUB(NOW(), INTERVAL 3 DAY)),
(117, 20, 25, 5, 'Recepción de transferencia inter-ONG', 'test_vocal', NOW());

-- ============================================
-- COMENTARIOS FINALES
-- ============================================

-- Este script SQL centraliza todos los casos de prueba necesarios para el testing
-- completo del sistema ONG. Incluye:
--
-- 1. Usuarios de prueba para todos los roles con casos de éxito, error y límite
-- 2. Donaciones de prueba para todas las categorías con diferentes niveles de stock
-- 3. Eventos de prueba con casos futuros, pasados y límite
-- 4. Datos completos para testing de comunicación inter-ONG via Kafka
-- 5. Tabla de mapeo que relaciona cada caso de prueba con endpoints específicos
-- 6. Casos de auditoría y trazabilidad de operaciones
--
-- Los datos insertados permiten generar automáticamente:
-- - Colecciones Postman con datos reales
-- - Ejemplos de Swagger con casos válidos
-- - Escenarios de testing Kafka inter-ONG
-- - Tests de integración end-to-end
--
-- Para usar este script:
-- 1. Ejecutar después de 01-create-tables.sql
-- 2. Los datos estarán disponibles para extracción automática
-- 3. Usar password 'test123' para todos los usuarios de prueba
-- 4. Los IDs están fijos para facilitar referencias en testing
