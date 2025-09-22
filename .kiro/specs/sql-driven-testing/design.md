# Design Document

## Overview

El sistema de SQL-Driven Testing centraliza todos los casos de prueba en scripts SQL estructurados, eliminando la complejidad de múltiples generadores de datos. Los scripts SQL contienen casos de prueba completos y realistas para todos los endpoints, y un sistema de extracción automática genera las configuraciones de Postman, Swagger y Kafka testing directamente desde estos datos insertados. Esto garantiza consistencia, simplicidad de mantenimiento y casos de prueba siempre actualizados.

## Architecture

### Flujo Principal
```
Scripts SQL Centralizados
         ↓
    Base de Datos Poblada
         ↓
    Extractor de Datos
         ↓
┌─────────────────────────────────┐
│  Generadores Automáticos        │
├─────────────────────────────────┤
│ • Postman Collections          │
│ • Swagger Examples             │
│ • Kafka Inter-ONG Messages     │
└─────────────────────────────────┘
```

### Estructura de Archivos
```
database/
├── init/
│   ├── 00-create-database.sql
│   ├── 01-create-tables.sql
│   └── 02-test-cases.sql          # ← Casos de prueba centralizados
└── test-scenarios/
    ├── auth-scenarios.sql         # Casos específicos de autenticación
    ├── inventory-scenarios.sql    # Casos de inventario y donaciones
    ├── events-scenarios.sql       # Casos de eventos
    └── network-scenarios.sql      # Casos inter-ONG

scripts/
├── sql-driven-testing/
│   ├── data_extractor.py         # Extrae datos de SQL poblado
│   ├── postman_generator.py      # Genera colecciones Postman
│   ├── swagger_generator.py      # Actualiza ejemplos Swagger
│   ├── kafka_generator.py        # Genera casos inter-ONG
│   └── orchestrator.py           # Coordina toda la generación
└── generate-testing-configs.py   # Script principal
```

## Components and Interfaces

### Script SQL Centralizado (`database/init/02-test-cases.sql`)
```sql
-- ============================================
-- CASOS DE PRUEBA CENTRALIZADOS
-- ============================================

-- Usuarios para diferentes escenarios de testing
INSERT INTO usuarios (id, nombre_usuario, nombre, apellido, telefono, clave_hash, email, rol, activo, usuario_alta) VALUES
-- Casos de éxito por rol
(1, 'test_presidente', 'Juan', 'Presidente', '1111111111', '$2b$10$hash1', 'presidente@test.com', 'PRESIDENTE', true, 'system'),
(2, 'test_vocal', 'María', 'Vocal', '2222222222', '$2b$10$hash2', 'vocal@test.com', 'VOCAL', true, 'test_presidente'),
(3, 'test_coordinador', 'Carlos', 'Coordinador', '3333333333', '$2b$10$hash3', 'coordinador@test.com', 'COORDINADOR', true, 'test_presidente'),
(4, 'test_voluntario', 'Ana', 'Voluntario', '4444444444', '$2b$10$hash4', 'voluntario@test.com', 'VOLUNTARIO', true, 'test_coordinador'),

-- Casos de error - usuarios inactivos
(5, 'test_inactivo', 'Pedro', 'Inactivo', '5555555555', '$2b$10$hash5', 'inactivo@test.com', 'VOLUNTARIO', false, 'test_coordinador'),

-- Casos límite - usuarios con datos mínimos/máximos
(6, 'test_limite_min', 'A', 'B', '1000000000', '$2b$10$hash6', 'min@test.com', 'VOLUNTARIO', true, 'test_coordinador'),
(7, 'test_limite_max', 'NombreMuyLargoParaProbarLimitesDeValidacion', 'ApellidoMuyLargoParaProbarLimitesDeValidacion', '9999999999', '$2b$10$hash7', 'max@test.com', 'VOLUNTARIO', true, 'test_coordinador');

-- Donaciones para testing de inventario
INSERT INTO donaciones (id, categoria, descripcion, cantidad, usuario_alta, fecha_alta) VALUES
-- Casos de éxito - stock suficiente
(101, 'ALIMENTOS', 'Arroz 1kg - Test Stock Alto', 100, 'test_vocal', NOW()),
(102, 'ROPA', 'Camisetas M - Test Stock Medio', 50, 'test_vocal', NOW()),
(103, 'JUGUETES', 'Pelotas - Test Stock Bajo', 5, 'test_vocal', NOW()),
(104, 'UTILES_ESCOLARES', 'Cuadernos - Test Stock Cero', 0, 'test_vocal', NOW()),

-- Casos para testing de transferencias
(105, 'ALIMENTOS', 'Leche 1L - Para Transferencia', 25, 'test_vocal', NOW()),
(106, 'ROPA', 'Pantalones L - Para Transferencia', 15, 'test_vocal', NOW()),

-- Casos límite - cantidades extremas
(107, 'ALIMENTOS', 'Fideos - Cantidad Máxima', 999999, 'test_vocal', NOW()),
(108, 'ROPA', 'Medias - Cantidad Mínima', 1, 'test_vocal', NOW());

-- Eventos para testing
INSERT INTO eventos (id, nombre, descripcion, fecha_hora, usuario_alta, activo) VALUES
-- Casos de éxito - eventos futuros
(201, 'Evento Test Futuro 1', 'Evento para testing de participación', DATE_ADD(NOW(), INTERVAL 7 DAY), 'test_coordinador', true),
(202, 'Evento Test Futuro 2', 'Evento para testing de adhesión externa', DATE_ADD(NOW(), INTERVAL 14 DAY), 'test_coordinador', true),

-- Casos de error - eventos pasados
(203, 'Evento Test Pasado', 'Evento pasado para testing de validaciones', DATE_SUB(NOW(), INTERVAL 7 DAY), 'test_coordinador', true),

-- Casos límite - eventos límite de fecha
(204, 'Evento Test Hoy', 'Evento de hoy para testing', NOW(), 'test_coordinador', true),
(205, 'Evento Test Inactivo', 'Evento inactivo para testing', DATE_ADD(NOW(), INTERVAL 21 DAY), 'test_coordinador', false);

-- Participantes en eventos
INSERT INTO evento_participantes (evento_id, usuario_id) VALUES
(201, 3), -- coordinador en evento futuro
(201, 4), -- voluntario en evento futuro
(202, 4), -- voluntario en evento futuro 2
(203, 4); -- voluntario en evento pasado (para testing de validaciones)

-- ============================================
-- DATOS PARA TESTING INTER-ONG (KAFKA)
-- ============================================

-- Organizaciones externas simuladas (para testing de red)
INSERT INTO organizaciones_externas (id, nombre, activa, fecha_registro) VALUES
('ong-corazon-solidario', 'ONG Corazón Solidario', true, NOW()),
('ong-manos-unidas', 'ONG Manos Unidas', true, NOW()),
('ong-esperanza', 'ONG Esperanza', true, NOW()),
('ong-inactiva', 'ONG Inactiva', false, NOW());

-- Solicitudes de donaciones externas (simulando mensajes Kafka recibidos)
INSERT INTO solicitudes_externas (id, id_organizacion, donaciones_solicitadas, fecha_solicitud, activa) VALUES
('sol-001', 'ong-corazon-solidario', '[{"categoria":"ALIMENTOS","descripcion":"Arroz para familias"}]', NOW(), true),
('sol-002', 'ong-manos-unidas', '[{"categoria":"ROPA","descripcion":"Ropa de invierno"}]', NOW(), true),
('sol-003', 'ong-esperanza', '[{"categoria":"JUGUETES","descripcion":"Juguetes para niños"}]', NOW(), false);

-- Ofertas de donaciones externas
INSERT INTO ofertas_externas (id, id_organizacion, donaciones_ofrecidas, fecha_oferta, activa) VALUES
('of-001', 'ong-corazon-solidario', '[{"categoria":"UTILES_ESCOLARES","descripcion":"Útiles escolares","cantidad":50}]', NOW(), true),
('of-002', 'ong-manos-unidas', '[{"categoria":"ALIMENTOS","descripcion":"Conservas","cantidad":30}]', NOW(), true);

-- Eventos externos (simulando eventos solidarios de otras ONGs)
INSERT INTO eventos_externos (id, id_organizacion, nombre, descripcion, fecha_hora, fecha_recepcion, activo) VALUES
('ev-ext-001', 'ong-corazon-solidario', 'Campaña de Invierno', 'Distribución de ropa de invierno', DATE_ADD(NOW(), INTERVAL 10 DAY), NOW(), true),
('ev-ext-002', 'ong-manos-unidas', 'Jornada Solidaria', 'Evento comunitario de ayuda', DATE_ADD(NOW(), INTERVAL 15 DAY), NOW(), true),
('ev-ext-003', 'ong-esperanza', 'Evento Pasado', 'Evento que ya ocurrió', DATE_SUB(NOW(), INTERVAL 5 DAY), NOW(), false);

-- ============================================
-- METADATOS PARA GENERACIÓN AUTOMÁTICA
-- ============================================

-- Tabla para mapear casos de prueba a endpoints
CREATE TABLE IF NOT EXISTS test_case_mapping (
    endpoint VARCHAR(100),
    method VARCHAR(10),
    test_type ENUM('success', 'error', 'validation', 'authorization'),
    user_id INT,
    resource_id INT,
    description TEXT,
    expected_status INT,
    INDEX idx_endpoint (endpoint),
    INDEX idx_test_type (test_type)
);

-- Mapeo de casos de prueba para autenticación
INSERT INTO test_case_mapping VALUES
('/api/auth/login', 'POST', 'success', 1, NULL, 'Login exitoso - Presidente', 200),
('/api/auth/login', 'POST', 'success', 2, NULL, 'Login exitoso - Vocal', 200),
('/api/auth/login', 'POST', 'success', 3, NULL, 'Login exitoso - Coordinador', 200),
('/api/auth/login', 'POST', 'success', 4, NULL, 'Login exitoso - Voluntario', 200),
('/api/auth/login', 'POST', 'error', 5, NULL, 'Login fallido - Usuario inactivo', 401),
('/api/auth/login', 'POST', 'validation', NULL, NULL, 'Login fallido - Credenciales inválidas', 401);

-- Mapeo de casos de prueba para usuarios
INSERT INTO test_case_mapping VALUES
('/api/usuarios', 'GET', 'success', 1, NULL, 'Listar usuarios - Presidente', 200),
('/api/usuarios', 'GET', 'authorization', 4, NULL, 'Listar usuarios - Sin permisos', 403),
('/api/usuarios/{id}', 'GET', 'success', 1, 2, 'Obtener usuario específico', 200),
('/api/usuarios/{id}', 'GET', 'error', 1, 999, 'Usuario no encontrado', 404);

-- Mapeo de casos de prueba para inventario
INSERT INTO test_case_mapping VALUES
('/api/inventario/donaciones', 'GET', 'success', 2, NULL, 'Listar donaciones', 200),
('/api/inventario/donaciones', 'POST', 'success', 2, NULL, 'Crear donación', 201),
('/api/inventario/donaciones', 'POST', 'authorization', 4, NULL, 'Crear donación - Sin permisos', 403),
('/api/inventario/donaciones/{id}', 'PUT', 'success', 2, 101, 'Actualizar donación', 200),
('/api/inventario/donaciones/{id}', 'PUT', 'error', 2, 999, 'Donación no encontrada', 404);

-- Mapeo de casos de prueba para eventos
INSERT INTO test_case_mapping VALUES
('/api/eventos', 'GET', 'success', 3, NULL, 'Listar eventos', 200),
('/api/eventos', 'POST', 'success', 3, NULL, 'Crear evento futuro', 201),
('/api/eventos', 'POST', 'validation', 3, NULL, 'Crear evento pasado - Error', 400),
('/api/eventos/{id}/participantes', 'POST', 'success', 4, 201, 'Unirse a evento', 200),
('/api/eventos/{id}/participantes', 'POST', 'error', 4, 203, 'Unirse a evento pasado - Error', 400);

-- Mapeo de casos de prueba para red inter-ONG
INSERT INTO test_case_mapping VALUES
('/api/red/solicitudes-donaciones', 'GET', 'success', 2, NULL, 'Listar solicitudes externas', 200),
('/api/red/solicitudes-donaciones', 'POST', 'success', 2, NULL, 'Crear solicitud donaciones', 201),
('/api/red/ofertas-donaciones', 'GET', 'success', 2, NULL, 'Listar ofertas externas', 200),
('/api/red/ofertas-donaciones', 'POST', 'success', 2, 105, 'Crear oferta donaciones', 201),
('/api/red/transferencias-donaciones', 'POST', 'success', 2, 105, 'Transferir donaciones', 200),
('/api/red/eventos-externos', 'GET', 'success', 4, NULL, 'Listar eventos externos', 200),
('/api/red/eventos-externos/adhesion', 'POST', 'success', 4, NULL, 'Adherirse a evento externo', 200),
('/api/red/eventos-externos/adhesion', 'POST', 'authorization', 2, NULL, 'Adhesión - Solo voluntarios', 403);
```

### Extractor de Datos (`scripts/sql-driven-testing/data_extractor.py`)
```python
class SQLDataExtractor:
    """Extrae datos de prueba desde la base de datos poblada por SQL"""
    
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None
    
    def extract_test_data(self) -> Dict[str, Any]:
        """Extrae todos los datos necesarios para generar configuraciones de testing"""
        return {
            'users': self.extract_users_by_role(),
            'inventory': self.extract_inventory_by_category(),
            'events': self.extract_events_by_status(),
            'network': self.extract_network_data(),
            'test_mappings': self.extract_test_case_mappings()
        }
    
    def extract_users_by_role(self) -> Dict[str, Dict]:
        """Extrae usuarios organizados por rol para testing de autorización"""
        query = """
        SELECT id, nombre_usuario, nombre, apellido, email, rol, activo,
               'password123' as password_plain  -- Password conocido para testing
        FROM usuarios 
        WHERE nombre_usuario LIKE 'test_%'
        ORDER BY rol, id
        """
        # Retorna: {'PRESIDENTE': {...}, 'VOCAL': {...}, etc.}
    
    def extract_inventory_by_category(self) -> Dict[str, List]:
        """Extrae donaciones organizadas por categoría y cantidad"""
        query = """
        SELECT id, categoria, descripcion, cantidad, usuario_alta
        FROM donaciones 
        WHERE usuario_alta LIKE 'test_%'
        ORDER BY categoria, cantidad DESC
        """
        # Retorna: {'ALIMENTOS': [...], 'ROPA': [...], etc.}
    
    def extract_events_by_status(self) -> Dict[str, List]:
        """Extrae eventos organizados por estado (futuro, pasado, activo)"""
        query = """
        SELECT e.id, e.nombre, e.descripcion, e.fecha_hora, e.activo,
               GROUP_CONCAT(ep.usuario_id) as participantes
        FROM eventos e
        LEFT JOIN evento_participantes ep ON e.id = ep.evento_id
        WHERE e.usuario_alta LIKE 'test_%'
        GROUP BY e.id
        ORDER BY e.fecha_hora
        """
        # Retorna: {'future': [...], 'past': [...], 'active': [...]}
    
    def extract_network_data(self) -> Dict[str, Any]:
        """Extrae datos para testing de comunicación inter-ONG"""
        return {
            'external_orgs': self.extract_external_organizations(),
            'donation_requests': self.extract_external_donation_requests(),
            'donation_offers': self.extract_external_donation_offers(),
            'external_events': self.extract_external_events()
        }
    
    def extract_test_case_mappings(self) -> List[Dict]:
        """Extrae mapeos de casos de prueba a endpoints"""
        query = """
        SELECT endpoint, method, test_type, user_id, resource_id, 
               description, expected_status
        FROM test_case_mapping
        ORDER BY endpoint, method, test_type
        """
        # Retorna lista de casos de prueba estructurados
```

### Generador de Postman (`scripts/sql-driven-testing/postman_generator.py`)
```python
class PostmanGenerator:
    """Genera colecciones Postman desde datos extraídos de SQL"""
    
    def __init__(self, extracted_data: Dict[str, Any]):
        self.data = extracted_data
        self.base_collection_path = "api-gateway/postman/"
    
    def generate_all_collections(self):
        """Genera todas las colecciones Postman con datos reales"""
        collections = [
            ('01-Autenticacion.postman_collection.json', self.generate_auth_collection),
            ('02-Usuarios.postman_collection.json', self.generate_users_collection),
            ('03-Inventario.postman_collection.json', self.generate_inventory_collection),
            ('04-Eventos.postman_collection.json', self.generate_events_collection),
            ('05-Red-ONGs.postman_collection.json', self.generate_network_collection)
        ]
        
        for filename, generator_func in collections:
            collection = generator_func()
            self.save_collection(filename, collection)
    
    def generate_auth_collection(self) -> Dict:
        """Genera colección de autenticación con usuarios reales"""
        auth_cases = [case for case in self.data['test_mappings'] 
                     if case['endpoint'] == '/api/auth/login']
        
        requests = []
        for case in auth_cases:
            if case['test_type'] == 'success':
                user = self.get_user_by_id(case['user_id'])
                requests.append({
                    "name": f"Login {user['rol']} - {case['description']}",
                    "request": {
                        "method": "POST",
                        "url": "{{base_url}}/api/auth/login",
                        "body": {
                            "raw": json.dumps({
                                "nombreUsuario": user['nombre_usuario'],
                                "clave": user['password_plain']
                            })
                        }
                    },
                    "event": [{
                        "listen": "test",
                        "script": {
                            "exec": [
                                f"pm.test('Status is {case['expected_status']}', function () {{",
                                f"    pm.response.to.have.status({case['expected_status']});",
                                "});",
                                "if (pm.response.code === 200) {",
                                "    const response = pm.response.json();",
                                "    pm.environment.set('auth_token', response.token);",
                                f"    pm.environment.set('{user['rol'].lower()}_token', response.token);",
                                f"    pm.environment.set('{user['rol'].lower()}_id', {user['id']});",
                                "}"
                            ]
                        }
                    }]
                })
        
        return {
            "info": {"name": "01 - Autenticación", "schema": "..."},
            "item": requests
        }
    
    def generate_inventory_collection(self) -> Dict:
        """Genera colección de inventario con donaciones reales"""
        inventory_cases = [case for case in self.data['test_mappings'] 
                          if case['endpoint'].startswith('/api/inventario')]
        
        requests = []
        for case in inventory_cases:
            if case['test_type'] == 'success' and case['resource_id']:
                donation = self.get_donation_by_id(case['resource_id'])
                user = self.get_user_by_id(case['user_id'])
                
                requests.append({
                    "name": f"{case['description']} - {donation['descripcion']}",
                    "request": {
                        "method": case['method'],
                        "url": case['endpoint'].replace('{id}', str(donation['id'])),
                        "header": [{"key": "Authorization", "value": "Bearer {{auth_token}}"}],
                        "body": self.generate_request_body(case, donation) if case['method'] in ['POST', 'PUT'] else None
                    }
                })
        
        return {"info": {"name": "03 - Inventario"}, "item": requests}
```

### Generador de Swagger (`scripts/sql-driven-testing/swagger_generator.py`)
```python
class SwaggerGenerator:
    """Actualiza ejemplos de Swagger con datos reales desde SQL"""
    
    def __init__(self, extracted_data: Dict[str, Any]):
        self.data = extracted_data
        self.swagger_config_path = "api-gateway/src/config/swagger.js"
    
    def update_swagger_examples(self):
        """Actualiza todos los ejemplos de Swagger con datos reales"""
        swagger_config = self.load_swagger_config()
        
        # Actualizar ejemplos de request/response para cada endpoint
        examples = {
            '/api/auth/login': self.generate_auth_examples(),
            '/api/usuarios': self.generate_users_examples(),
            '/api/inventario/donaciones': self.generate_inventory_examples(),
            '/api/eventos': self.generate_events_examples(),
            '/api/red/solicitudes-donaciones': self.generate_network_examples()
        }
        
        # Integrar ejemplos en la configuración de Swagger
        updated_config = self.integrate_examples(swagger_config, examples)
        self.save_swagger_config(updated_config)
    
    def generate_inventory_examples(self) -> Dict:
        """Genera ejemplos de inventario con donaciones reales"""
        high_stock_donation = next(d for d in self.data['inventory']['ALIMENTOS'] if d['cantidad'] > 50)
        low_stock_donation = next(d for d in self.data['inventory']['JUGUETES'] if d['cantidad'] < 10)
        
        return {
            'request_examples': {
                'create_donation': {
                    "categoria": "ALIMENTOS",
                    "descripcion": "Arroz integral 1kg",
                    "cantidad": 25
                },
                'update_donation': {
                    "descripcion": high_stock_donation['descripcion'] + " - Actualizado",
                    "cantidad": high_stock_donation['cantidad'] + 10
                }
            },
            'response_examples': {
                'donation_list': [
                    {
                        "id": high_stock_donation['id'],
                        "categoria": high_stock_donation['categoria'],
                        "descripcion": high_stock_donation['descripcion'],
                        "cantidad": high_stock_donation['cantidad'],
                        "fechaAlta": "2024-01-15T10:30:00Z"
                    },
                    {
                        "id": low_stock_donation['id'],
                        "categoria": low_stock_donation['categoria'],
                        "descripcion": low_stock_donation['descripcion'],
                        "cantidad": low_stock_donation['cantidad'],
                        "fechaAlta": "2024-01-16T14:20:00Z"
                    }
                ]
            }
        }
```

### Generador de Kafka (`scripts/sql-driven-testing/kafka_generator.py`)
```python
class KafkaTestGenerator:
    """Genera casos de prueba para comunicación inter-ONG via Kafka"""
    
    def __init__(self, extracted_data: Dict[str, Any]):
        self.data = extracted_data
        self.organization_id = "ong-empuje-comunitario"
    
    def generate_kafka_test_scenarios(self) -> Dict[str, List]:
        """Genera escenarios de prueba para todos los topics inter-ONG"""
        return {
            'solicitud-donaciones': self.generate_donation_request_scenarios(),
            'oferta-donaciones': self.generate_donation_offer_scenarios(),
            'transferencia-donaciones': self.generate_transfer_scenarios(),
            'eventos-solidarios': self.generate_external_event_scenarios(),
            'baja-evento-solidario': self.generate_event_cancellation_scenarios()
        }
    
    def generate_donation_request_scenarios(self) -> List[Dict]:
        """Genera mensajes de solicitud de donaciones con datos reales"""
        vocal_user = self.data['users']['VOCAL']
        
        scenarios = []
        
        # Escenario 1: Solicitud de alimentos
        scenarios.append({
            'scenario_name': 'Solicitud de Alimentos - Caso Exitoso',
            'topic': 'solicitud-donaciones',
            'message': {
                'idOrganizacion': self.organization_id,
                'donaciones': [
                    {
                        'categoria': 'ALIMENTOS',
                        'descripcion': 'Arroz y fideos para familias necesitadas'
                    },
                    {
                        'categoria': 'ALIMENTOS', 
                        'descripcion': 'Leche en polvo para niños'
                    }
                ],
                'usuarioSolicitante': vocal_user['nombre_usuario'],
                'timestamp': '2024-01-15T10:00:00Z'
            },
            'expected_external_response': True,
            'test_assertions': [
                'Mensaje publicado exitosamente',
                'Otras ONGs pueden ver la solicitud',
                'Datos de contacto incluidos correctamente'
            ]
        })
        
        # Escenario 2: Solicitud con múltiples categorías
        scenarios.append({
            'scenario_name': 'Solicitud Múltiple Categorías',
            'topic': 'solicitud-donaciones',
            'message': {
                'idOrganizacion': self.organization_id,
                'donaciones': [
                    {'categoria': 'ROPA', 'descripcion': 'Ropa de invierno para adultos'},
                    {'categoria': 'JUGUETES', 'descripcion': 'Juguetes educativos'},
                    {'categoria': 'UTILES_ESCOLARES', 'descripcion': 'Útiles para primaria'}
                ],
                'usuarioSolicitante': vocal_user['nombre_usuario'],
                'timestamp': '2024-01-15T11:00:00Z'
            }
        })
        
        return scenarios
    
    def generate_transfer_scenarios(self) -> List[Dict]:
        """Genera escenarios de transferencia con donaciones reales"""
        transfer_donation = next(d for d in self.data['inventory']['ALIMENTOS'] 
                               if 'Transferencia' in d['descripcion'])
        vocal_user = self.data['users']['VOCAL']
        external_org = self.data['network']['external_orgs'][0]
        
        return [{
            'scenario_name': 'Transferencia de Donaciones Exitosa',
            'topic': f"transferencia-donaciones/{external_org['id']}",
            'message': {
                'idOrganizacion': self.organization_id,
                'idSolicitud': 'sol-001',
                'donaciones': [
                    {
                        'id': transfer_donation['id'],
                        'categoria': transfer_donation['categoria'],
                        'descripcion': transfer_donation['descripcion'],
                        'cantidad': min(10, transfer_donation['cantidad'])
                    }
                ],
                'usuarioTransferencia': vocal_user['nombre_usuario'],
                'organizacionDestino': external_org['id'],
                'timestamp': '2024-01-15T15:00:00Z'
            },
            'pre_conditions': [
                f"Donación {transfer_donation['id']} debe tener stock suficiente",
                f"Usuario {vocal_user['nombre_usuario']} debe tener permisos",
                f"Organización {external_org['id']} debe estar activa"
            ],
            'post_conditions': [
                'Stock de donación reducido correctamente',
                'Mensaje enviado a topic específico de organización',
                'Auditoría de transferencia registrada'
            ]
        }]
```

### Orquestador Principal (`scripts/sql-driven-testing/orchestrator.py`)
```python
class TestingOrchestrator:
    """Coordina la generación de todas las configuraciones de testing"""
    
    def __init__(self, config_file: str = None):
        self.config = self.load_config(config_file)
        self.data_extractor = SQLDataExtractor(self.config['database'])
        self.backup_manager = BackupManager()
    
    def generate_all_testing_configs(self, options: Dict[str, bool] = None):
        """Genera todas las configuraciones de testing desde SQL"""
        options = options or {
            'postman': True,
            'swagger': True, 
            'kafka': True,
            'backup': True,
            'validate': True
        }
        
        logger.info("Iniciando generación de configuraciones de testing desde SQL")
        
        # 1. Crear backups si está habilitado
        if options['backup']:
            self.backup_manager.create_backups()
        
        # 2. Extraer datos desde SQL poblado
        logger.info("Extrayendo datos de prueba desde base de datos")
        extracted_data = self.data_extractor.extract_test_data()
        
        # 3. Validar datos extraídos
        if options['validate']:
            self.validate_extracted_data(extracted_data)
        
        # 4. Generar configuraciones
        results = {}
        
        if options['postman']:
            logger.info("Generando colecciones Postman")
            postman_gen = PostmanGenerator(extracted_data)
            results['postman'] = postman_gen.generate_all_collections()
        
        if options['swagger']:
            logger.info("Actualizando ejemplos Swagger")
            swagger_gen = SwaggerGenerator(extracted_data)
            results['swagger'] = swagger_gen.update_swagger_examples()
        
        if options['kafka']:
            logger.info("Generando casos de prueba Kafka")
            kafka_gen = KafkaTestGenerator(extracted_data)
            results['kafka'] = kafka_gen.generate_kafka_test_scenarios()
        
        # 5. Generar reporte de cambios
        report = self.generate_change_report(results)
        
        logger.info("Generación completada exitosamente")
        return report
    
    def validate_extracted_data(self, data: Dict[str, Any]):
        """Valida que los datos extraídos sean consistentes y completos"""
        validations = [
            ('users', self.validate_users_data),
            ('inventory', self.validate_inventory_data),
            ('events', self.validate_events_data),
            ('network', self.validate_network_data),
            ('test_mappings', self.validate_test_mappings)
        ]
        
        for data_type, validator in validations:
            if data_type in data:
                validator(data[data_type])
            else:
                raise ValueError(f"Datos faltantes: {data_type}")
    
    def generate_change_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reporte detallado de cambios realizados"""
        return {
            'timestamp': datetime.now().isoformat(),
            'generated_configs': list(results.keys()),
            'postman_collections': results.get('postman', {}).get('collections_updated', []),
            'swagger_examples': results.get('swagger', {}).get('examples_updated', []),
            'kafka_scenarios': results.get('kafka', {}).get('scenarios_generated', []),
            'total_test_cases': self.count_total_test_cases(results),
            'validation_status': 'passed',
            'backup_location': self.backup_manager.get_latest_backup_path()
        }
```

## Data Models

### Estructura de Datos Extraídos
```python
{
    "users": {
        "PRESIDENTE": {
            "id": 1,
            "nombre_usuario": "test_presidente",
            "nombre": "Juan",
            "apellido": "Presidente", 
            "email": "presidente@test.com",
            "password_plain": "password123",
            "activo": True
        },
        "VOCAL": {...},
        "COORDINADOR": {...},
        "VOLUNTARIO": {...},
        "INACTIVE": {...}  # Para casos de error
    },
    "inventory": {
        "ALIMENTOS": [
            {
                "id": 101,
                "descripcion": "Arroz 1kg - Test Stock Alto",
                "cantidad": 100,
                "usuario_alta": "test_vocal"
            }
        ],
        "ROPA": [...],
        "JUGUETES": [...],
        "UTILES_ESCOLARES": [...]
    },
    "events": {
        "future": [
            {
                "id": 201,
                "nombre": "Evento Test Futuro 1",
                "descripcion": "Evento para testing de participación",
                "fecha_hora": "2024-02-15T10:00:00Z",
                "participantes": [3, 4],
                "activo": True
            }
        ],
        "past": [...],
        "inactive": [...]
    },
    "network": {
        "external_orgs": [
            {
                "id": "ong-corazon-solidario",
                "nombre": "ONG Corazón Solidario",
                "activa": True
            }
        ],
        "donation_requests": [...],
        "donation_offers": [...],
        "external_events": [...]
    },
    "test_mappings": [
        {
            "endpoint": "/api/auth/login",
            "method": "POST",
            "test_type": "success",
            "user_id": 1,
            "resource_id": None,
            "description": "Login exitoso - Presidente",
            "expected_status": 200
        }
    ]
}
```

## Error Handling

### Validación de Datos SQL
- Verificar que todos los casos de prueba necesarios estén insertados
- Validar relaciones de foreign keys entre tablas
- Confirmar que los datos de testing cubran todos los escenarios requeridos

### Generación de Configuraciones
- Manejar errores de formato en colecciones Postman existentes
- Validar sintaxis de ejemplos Swagger antes de actualizar
- Verificar conectividad Kafka antes de generar escenarios

### Consistencia de Datos
- Asegurar que IDs referenciados en configuraciones existan en la base de datos
- Validar que usuarios de prueba tengan los permisos correctos
- Verificar que fechas de eventos sean consistentes con casos de prueba

## Testing Strategy

### Validación de SQL
- Tests que verifican que todos los casos de prueba estén insertados correctamente
- Validación de integridad referencial en datos de prueba
- Tests de cobertura para asegurar que todos los endpoints tengan casos

### Generación de Configuraciones
- Tests unitarios para cada generador (Postman, Swagger, Kafka)
- Tests de integración que validen configuraciones generadas
- Tests de regresión para asegurar que cambios no rompan configuraciones existentes

### End-to-End Testing
- Ejecutar colecciones Postman generadas contra API real
- Validar que ejemplos Swagger sean ejecutables
- Probar escenarios Kafka con brokers de testing

## Configuration

### Variables de Entorno
```bash
# Base de datos (reutiliza configuración existente)
DB_HOST=mysql
DB_PORT=3306
DB_NAME=ong_sistema
DB_USER=ong_user
DB_PASSWORD=ong_password

# Configuración de generación
POSTMAN_COLLECTIONS_PATH=./api-gateway/postman/
SWAGGER_CONFIG_PATH=./api-gateway/src/config/swagger.js
KAFKA_SCENARIOS_PATH=./scripts/kafka-scenarios/

# Opciones de generación
BACKUP_BEFORE_GENERATION=true
VALIDATE_GENERATED_CONFIGS=true
PRESERVE_CUSTOM_TESTS=true
```

### Comando Principal
```bash
# Generar todas las configuraciones
python scripts/generate-testing-configs.py --all

# Generar solo Postman
python scripts/generate-testing-configs.py --postman

# Generar con validación completa
python scripts/generate-testing-configs.py --all --validate --backup

# Regenerar después de cambios en SQL
python scripts/generate-testing-configs.py --refresh

# Restaurar desde backup
python scripts/generate-testing-configs.py --restore --backup-date 2024-01-15
```

## Integration Points

### Con Sistema de Base de Datos Existente
- Reutiliza scripts de inicialización existentes (00-create-database.sql, 01-create-tables.sql)
- Extiende con 02-test-cases.sql para casos de prueba centralizados
- Mantiene compatibilidad con sistema de población de datos actual

### Con Colecciones Postman Existentes
- Preserva estructura y organización de colecciones actuales
- Actualiza solo datos de prueba, mantiene lógica de testing personalizada
- Crea backups automáticos antes de modificaciones

### Con Configuración Swagger Existente
- Integra ejemplos generados con configuración actual de Swagger
- Mantiene documentación personalizada y descripciones
- Actualiza solo secciones de ejemplos de request/response

### Con Sistema Kafka Existente
- Utiliza configuración de brokers y topics existente
- Genera escenarios compatibles con cliente Kafka actual
- Mantiene consistencia con IDs de organización configurados

## Performance Optimization

### Extracción de Datos
- Utiliza consultas SQL optimizadas con índices apropiados
- Implementa cache de datos extraídos para múltiples generaciones
- Procesa datos en lotes para reducir memoria utilizada

### Generación de Configuraciones
- Genera configuraciones en paralelo cuando sea posible
- Utiliza templates para reducir tiempo de generación
- Implementa generación incremental para cambios menores

### Validación y Testing
- Ejecuta validaciones en paralelo para diferentes tipos de datos
- Utiliza sampling para validaciones de gran volumen
- Implementa early-exit en validaciones para fallos rápidos