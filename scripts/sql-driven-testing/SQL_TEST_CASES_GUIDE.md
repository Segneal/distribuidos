# SQL Test Cases Structure Guide

## Overview

This guide explains how to structure test cases in SQL scripts and how to add new test cases to the SQL-driven testing system. All test cases are centralized in SQL scripts to maintain consistency and simplify maintenance.

## SQL Test Cases Structure

### Main Test Cases File

The primary test cases are defined in `database/init/02-test-cases.sql`. This file contains:

1. **Test Users** - Users for different roles and scenarios
2. **Test Donations** - Inventory items for various testing scenarios
3. **Test Events** - Events for different temporal states
4. **Inter-NGO Data** - External organizations and communication data
5. **Test Case Mappings** - Endpoint mappings with expected results

### File Organization

```
database/
├── init/
│   ├── 00-create-database.sql     # Database creation
│   ├── 01-create-tables.sql       # Table definitions
│   └── 02-test-cases.sql          # ← Main test cases file
└── test-scenarios/                 # Optional: Additional scenarios
    ├── auth-scenarios.sql          # Authentication-specific cases
    ├── inventory-scenarios.sql     # Inventory-specific cases
    ├── events-scenarios.sql        # Events-specific cases
    └── network-scenarios.sql       # Inter-NGO specific cases
```

## Test Users Structure

### Naming Convention
All test users must have `nombre_usuario` starting with `test_` to be recognized by the extraction system.

### User Categories

```sql
-- SUCCESS CASES - One user per role
INSERT INTO usuarios (id, nombre_usuario, nombre, apellido, telefono, clave_hash, email, rol, activo, usuario_alta) VALUES
(1, 'test_presidente', 'Juan', 'Presidente', '1111111111', '$2b$10$hash1', 'presidente@test.com', 'PRESIDENTE', true, 'system'),
(2, 'test_vocal', 'María', 'Vocal', '2222222222', '$2b$10$hash2', 'vocal@test.com', 'VOCAL', true, 'test_presidente'),
(3, 'test_coordinador', 'Carlos', 'Coordinador', '3333333333', '$2b$10$hash3', 'coordinador@test.com', 'COORDINADOR', true, 'test_presidente'),
(4, 'test_voluntario', 'Ana', 'Voluntario', '4444444444', '$2b$10$hash4', 'voluntario@test.com', 'VOLUNTARIO', true, 'test_coordinador');

-- ERROR CASES - Inactive users, invalid data
(5, 'test_inactivo', 'Pedro', 'Inactivo', '5555555555', '$2b$10$hash5', 'inactivo@test.com', 'VOLUNTARIO', false, 'test_coordinador');

-- EDGE CASES - Boundary values
(6, 'test_limite_min', 'A', 'B', '1000000000', '$2b$10$hash6', 'min@test.com', 'VOLUNTARIO', true, 'test_coordinador'),
(7, 'test_limite_max', 'NombreMuyLargoParaProbarLimitesDeValidacion', 'ApellidoMuyLargoParaProbarLimitesDeValidacion', '9999999999', '$2b$10$hash7', 'max@test.com', 'VOLUNTARIO', true, 'test_coordinador');
```

### Required Fields for Test Users

| Field | Purpose | Requirements |
|-------|---------|--------------|
| `nombre_usuario` | Must start with `test_` | Unique identifier for test users |
| `clave_hash` | Password hash | Use bcrypt format for realistic testing |
| `rol` | User role | Must cover all roles: PRESIDENTE, VOCAL, COORDINADOR, VOLUNTARIO |
| `activo` | Account status | Include both active (true) and inactive (false) users |
| `usuario_alta` | Created by | Reference to another test user for hierarchy testing |

## Test Donations Structure

### Naming Convention
Test donations should have `usuario_alta` starting with `test_` to be recognized by the extraction system.

### Donation Categories

```sql
-- SUCCESS CASES - Different stock levels per category
INSERT INTO donaciones (id, categoria, descripcion, cantidad, usuario_alta, fecha_alta) VALUES
-- High stock (>50)
(101, 'ALIMENTOS', 'Arroz 1kg - Test Stock Alto', 100, 'test_vocal', NOW()),
-- Medium stock (10-50)
(102, 'ROPA', 'Camisetas M - Test Stock Medio', 50, 'test_vocal', NOW()),
-- Low stock (1-9)
(103, 'JUGUETES', 'Pelotas - Test Stock Bajo', 5, 'test_vocal', NOW()),
-- Zero stock
(104, 'UTILES_ESCOLARES', 'Cuadernos - Test Stock Cero', 0, 'test_vocal', NOW());

-- TRANSFER CASES - For inter-NGO testing
(105, 'ALIMENTOS', 'Leche 1L - Para Transferencia', 25, 'test_vocal', NOW()),
(106, 'ROPA', 'Pantalones L - Para Transferencia', 15, 'test_vocal', NOW());

-- EDGE CASES - Extreme quantities
(107, 'ALIMENTOS', 'Fideos - Cantidad Máxima', 999999, 'test_vocal', NOW()),
(108, 'ROPA', 'Medias - Cantidad Mínima', 1, 'test_vocal', NOW());
```

### Stock Level Categories

The system automatically categorizes donations by stock level:

- **High Stock**: `cantidad > 50`
- **Medium Stock**: `10 <= cantidad <= 50`
- **Low Stock**: `1 <= cantidad < 10`
- **Zero Stock**: `cantidad = 0`

### Required Categories

Ensure all donation categories are represented:
- `ALIMENTOS`
- `ROPA`
- `JUGUETES`
- `UTILES_ESCOLARES`

## Test Events Structure

### Event Categories

```sql
-- SUCCESS CASES - Future events (valid for participation)
INSERT INTO eventos (id, nombre, descripcion, fecha_hora, usuario_alta, activo) VALUES
(201, 'Evento Test Futuro 1', 'Evento para testing de participación', DATE_ADD(NOW(), INTERVAL 7 DAY), 'test_coordinador', true),
(202, 'Evento Test Futuro 2', 'Evento para testing de adhesión externa', DATE_ADD(NOW(), INTERVAL 14 DAY), 'test_coordinador', true);

-- ERROR CASES - Past events (should not allow new participation)
(203, 'Evento Test Pasado', 'Evento pasado para testing de validaciones', DATE_SUB(NOW(), INTERVAL 7 DAY), 'test_coordinador', true);

-- EDGE CASES - Boundary dates
(204, 'Evento Test Hoy', 'Evento de hoy para testing', NOW(), 'test_coordinador', true),
(205, 'Evento Test Inactivo', 'Evento inactivo para testing', DATE_ADD(NOW(), INTERVAL 21 DAY), 'test_coordinador', false);
```

### Event Participants

```sql
-- Link users to events for participation testing
INSERT INTO evento_participantes (evento_id, usuario_id) VALUES
(201, 3), -- coordinador in future event
(201, 4), -- voluntario in future event
(202, 4), -- voluntario in another future event
(203, 4); -- voluntario in past event (for validation testing)
```

### Temporal Categories

Events are automatically categorized by temporal status:
- **Future Events**: `fecha_hora > NOW()`
- **Past Events**: `fecha_hora < NOW()`
- **Current Events**: `fecha_hora = NOW()` (approximately)

## Inter-NGO Test Data

### External Organizations

```sql
-- External organizations for network testing
INSERT INTO organizaciones_externas (id, nombre, activa, fecha_registro) VALUES
('ong-corazon-solidario', 'ONG Corazón Solidario', true, NOW()),
('ong-manos-unidas', 'ONG Manos Unidas', true, NOW()),
('ong-esperanza', 'ONG Esperanza', true, NOW()),
('ong-inactiva', 'ONG Inactiva', false, NOW()); -- Inactive for error testing
```

### External Requests and Offers

```sql
-- Donation requests from other NGOs
INSERT INTO solicitudes_externas (id, id_organizacion, donaciones_solicitadas, fecha_solicitud, activa) VALUES
('sol-001', 'ong-corazon-solidario', '[{"categoria":"ALIMENTOS","descripcion":"Arroz para familias"}]', NOW(), true),
('sol-002', 'ong-manos-unidas', '[{"categoria":"ROPA","descripcion":"Ropa de invierno"}]', NOW(), true),
('sol-003', 'ong-esperanza', '[{"categoria":"JUGUETES","descripcion":"Juguetes para niños"}]', NOW(), false); -- Inactive

-- Donation offers from other NGOs
INSERT INTO ofertas_externas (id, id_organizacion, donaciones_ofrecidas, fecha_oferta, activa) VALUES
('of-001', 'ong-corazon-solidario', '[{"categoria":"UTILES_ESCOLARES","descripcion":"Útiles escolares","cantidad":50}]', NOW(), true),
('of-002', 'ong-manos-unidas', '[{"categoria":"ALIMENTOS","descripcion":"Conservas","cantidad":30}]', NOW(), true);
```

## Test Case Mappings

### Mapping Table Structure

```sql
CREATE TABLE IF NOT EXISTS test_case_mapping (
    endpoint VARCHAR(100),           -- API endpoint path
    method VARCHAR(10),              -- HTTP method
    test_type ENUM('success', 'error', 'validation', 'authorization', 'edge_case'),
    user_id INT,                     -- Reference to test user
    resource_id INT,                 -- Reference to test resource (donation, event, etc.)
    description TEXT,                -- Human-readable description
    expected_status INT,             -- Expected HTTP status code
    request_body JSON,               -- Optional: Expected request body
    expected_response_fields JSON,   -- Optional: Expected response fields
    test_category VARCHAR(50),       -- Category: authentication, users, inventory, events, network
    INDEX idx_endpoint (endpoint),
    INDEX idx_test_type (test_type),
    INDEX idx_category (test_category)
);
```

### Test Type Categories

- **success**: Happy path scenarios that should work correctly
- **error**: Error scenarios (not found, invalid data, etc.)
- **validation**: Input validation failures
- **authorization**: Permission/role-based access failures
- **edge_case**: Boundary conditions and edge cases

### Example Mappings

```sql
-- Authentication test cases
INSERT INTO test_case_mapping VALUES
('/api/auth/login', 'POST', 'success', 1, NULL, 'Login exitoso - Presidente', 200, 
 '{"nombreUsuario": "test_presidente", "clave": "test123"}', 
 '["token", "usuario", "rol"]', 'authentication'),
('/api/auth/login', 'POST', 'error', 5, NULL, 'Login fallido - Usuario inactivo', 401, 
 '{"nombreUsuario": "test_inactivo", "clave": "test123"}', 
 '["error", "message"]', 'authentication');

-- Inventory test cases
INSERT INTO test_case_mapping VALUES
('/api/inventario/donaciones', 'GET', 'success', 2, NULL, 'Listar donaciones', 200, 
 NULL, '["donaciones", "total"]', 'inventory'),
('/api/inventario/donaciones/{id}', 'PUT', 'success', 2, 101, 'Actualizar donación', 200, 
 '{"descripcion": "Arroz actualizado", "cantidad": 110}', 
 '["id", "descripcion", "cantidad"]', 'inventory');
```

## Adding New Test Cases

### Step 1: Identify Test Scenario

Before adding new test cases, identify:
1. **Endpoint**: Which API endpoint needs testing
2. **Test Type**: success, error, validation, authorization, or edge_case
3. **User Role**: Which role should execute the test
4. **Resource**: What resource (donation, event, etc.) is involved
5. **Expected Outcome**: HTTP status and response structure

### Step 2: Add Supporting Data

Add any required supporting data first:

```sql
-- Add test user if needed
INSERT INTO usuarios (id, nombre_usuario, nombre, apellido, telefono, clave_hash, email, rol, activo, usuario_alta) VALUES
(10, 'test_new_role', 'Test', 'User', '1234567890', '$2b$10$hash', 'test@example.com', 'VOLUNTARIO', true, 'test_coordinador');

-- Add test donation if needed
INSERT INTO donaciones (id, categoria, descripcion, cantidad, usuario_alta, fecha_alta) VALUES
(110, 'ALIMENTOS', 'Test Item for New Scenario', 25, 'test_vocal', NOW());

-- Add test event if needed
INSERT INTO eventos (id, nombre, descripcion, fecha_hora, usuario_alta, activo) VALUES
(210, 'Test Event for New Scenario', 'Description', DATE_ADD(NOW(), INTERVAL 5 DAY), 'test_coordinador', true);
```

### Step 3: Add Test Case Mapping

```sql
INSERT INTO test_case_mapping VALUES
('/api/new-endpoint', 'POST', 'success', 10, 110, 'New endpoint test case', 201,
 '{"field": "value"}', '["id", "status"]', 'new_category');
```

### Step 4: Validate New Test Case

After adding the test case:

1. **Run data extraction** to verify the new data is picked up:
   ```bash
   python scripts/sql-driven-testing/test_data_extractor.py
   ```

2. **Generate configurations** to see the new test case in action:
   ```bash
   python scripts/generate-testing-configs.py --postman --no-backup
   ```

3. **Validate the generated configuration**:
   ```bash
   python scripts/sql-driven-testing/test_postman_generator.py
   ```

## Best Practices for Test Cases

### 1. Comprehensive Coverage

Ensure each endpoint has test cases for:
- ✅ **Success scenarios** for each user role
- ✅ **Error scenarios** (not found, invalid data)
- ✅ **Authorization failures** (insufficient permissions)
- ✅ **Validation failures** (invalid input)
- ✅ **Edge cases** (boundary conditions)

### 2. Realistic Data

- Use realistic names, descriptions, and values
- Include proper foreign key relationships
- Use appropriate data types and formats
- Include both positive and negative test data

### 3. Clear Descriptions

- Use descriptive names that explain the test scenario
- Include the expected outcome in the description
- Specify the user role and context
- Use consistent naming conventions

### 4. Proper Categorization

- Assign appropriate `test_type` values
- Use consistent `test_category` values
- Group related test cases together
- Maintain logical organization

### 5. Maintainable Structure

- Keep test data separate from production data
- Use consistent ID ranges for test data
- Document complex test scenarios
- Regular cleanup of obsolete test cases

## Common Test Scenarios

### Authentication Scenarios

```sql
-- Success: Login for each role
-- Error: Invalid credentials, inactive user
-- Validation: Missing fields, malformed data
-- Edge: Special characters in username/password
```

### CRUD Operation Scenarios

```sql
-- Success: Create, read, update, delete
-- Error: Not found, duplicate creation
-- Authorization: Insufficient permissions
-- Validation: Invalid data, missing required fields
-- Edge: Boundary values, special characters
```

### Business Logic Scenarios

```sql
-- Success: Valid business operations
-- Error: Business rule violations
-- Edge: Boundary conditions, race conditions
-- Validation: Business constraint violations
```

## Troubleshooting Test Cases

### Common Issues

1. **Test case not appearing in generated configurations**
   - Check that `nombre_usuario` starts with `test_`
   - Verify foreign key relationships are valid
   - Ensure test case mapping references valid user/resource IDs

2. **Data extraction fails**
   - Check SQL syntax in test case definitions
   - Verify all required fields are present
   - Ensure data types match table definitions

3. **Generated tests fail**
   - Verify expected status codes are correct
   - Check that request bodies are valid JSON
   - Ensure response field expectations match API

4. **Inconsistent test results**
   - Check for data dependencies between test cases
   - Verify temporal data (dates) are relative to NOW()
   - Ensure test data isolation

### Debugging Steps

1. **Validate SQL syntax**:
   ```bash
   python scripts/test-sql-syntax.py
   ```

2. **Test data extraction**:
   ```bash
   python scripts/sql-driven-testing/test_data_extractor.py
   ```

3. **Check generated configurations**:
   ```bash
   python scripts/generate-testing-configs.py --validate-only
   ```

4. **Run comprehensive validation**:
   ```bash
   python scripts/sql-driven-testing/test_runner.py
   ```

## Migration from Existing Test Data

If you have existing test data that needs to be migrated to the SQL-driven system:

### Step 1: Analyze Existing Data
- Identify all test scenarios currently in use
- Map existing test data to SQL structure
- Identify gaps in current test coverage

### Step 2: Create Migration Script
```sql
-- Migrate existing users
INSERT INTO usuarios (nombre_usuario, nombre, apellido, ...)
SELECT CONCAT('test_', existing_username), nombre, apellido, ...
FROM existing_test_users;

-- Migrate existing test cases
INSERT INTO test_case_mapping (endpoint, method, test_type, ...)
SELECT endpoint, method, 'success', ...
FROM existing_test_configurations;
```

### Step 3: Validate Migration
- Run data extraction to verify migrated data
- Generate configurations and compare with existing ones
- Test generated configurations against API

### Step 4: Update Documentation
- Document any changes in test scenarios
- Update test case descriptions
- Verify all test categories are covered

This comprehensive approach ensures that your SQL test cases are well-structured, maintainable, and provide complete coverage for your API testing needs.