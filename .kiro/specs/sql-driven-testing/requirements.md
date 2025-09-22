# Requirements Document

## Introduction

Este feature simplifica radicalmente la generación de datos de prueba y configuraciones de testing centralizando todos los casos de prueba en scripts SQL. En lugar de mantener múltiples sistemas complejos de generación de datos, insertaremos directamente en los scripts SQL todos los casos de prueba necesarios para cada endpoint, y luego utilizaremos esos datos insertados como fuente única de verdad para generar automáticamente las configuraciones de Postman, Swagger y Kafka testing.

## Requirements

### Requirement 1

**User Story:** Como desarrollador, quiero que todos los casos de prueba estén definidos en scripts SQL centralizados, para que sea fácil mantener y entender todos los escenarios de testing.

#### Acceptance Criteria

1. WHEN se ejecutan los scripts SQL THEN el sistema SHALL insertar casos de prueba completos para todos los endpoints REST
2. WHEN se definen casos de prueba THEN el sistema SHALL incluir escenarios de éxito, error, validación y casos límite para cada endpoint
3. WHEN se insertan datos de prueba THEN el sistema SHALL mantener relaciones consistentes entre usuarios, donaciones, eventos y organizaciones
4. WHEN se crean casos de prueba THEN el sistema SHALL incluir datos específicos para testing de autorización por roles (PRESIDENTE, VOCAL, COORDINADOR, VOLUNTARIO)

### Requirement 2

**User Story:** Como desarrollador, quiero que las configuraciones de Postman se generen automáticamente desde los datos SQL, para que no tenga que mantener manualmente variables de entorno y casos de prueba.

#### Acceptance Criteria

1. WHEN se ejecuta el generador THEN el sistema SHALL extraer automáticamente IDs, tokens y datos de prueba desde la base de datos poblada
2. WHEN se generan colecciones Postman THEN el sistema SHALL crear requests con datos reales extraídos de los scripts SQL
3. WHEN se configuran variables de entorno THEN el sistema SHALL incluir todos los IDs necesarios para testing de cada endpoint
4. WHEN se actualizan las colecciones THEN el sistema SHALL preservar la estructura existente mientras actualiza solo los datos de prueba

### Requirement 3

**User Story:** Como desarrollador, quiero que los casos de prueba de comunicación inter-ONG (Kafka) se generen desde los mismos datos SQL, para que haya consistencia entre testing REST y messaging entre organizaciones.

#### Acceptance Criteria

1. WHEN se generan casos Kafka THEN el sistema SHALL usar los mismos IDs de organizaciones, usuarios y donaciones definidos en SQL
2. WHEN se crean mensajes de prueba THEN el sistema SHALL generar payloads para topics inter-ONG (solicitud-donaciones, oferta-donaciones, eventos-solidarios, transferencia-donaciones)
3. WHEN se configuran scenarios de red THEN el sistema SHALL incluir casos para simular múltiples ONGs interactuando con datos consistentes
4. WHEN se validan mensajes inter-ONG THEN el sistema SHALL verificar que los datos referencien entidades existentes en la base de datos poblada

### Requirement 4

**User Story:** Como desarrollador, quiero que la documentación Swagger se actualice automáticamente con ejemplos reales, para que la documentación siempre refleje casos de uso válidos.

#### Acceptance Criteria

1. WHEN se genera documentación Swagger THEN el sistema SHALL incluir ejemplos de request/response basados en datos SQL reales
2. WHEN se actualizan ejemplos THEN el sistema SHALL usar IDs y datos que existen en la base de datos poblada
3. WHEN se documenten endpoints THEN el sistema SHALL incluir casos de éxito y error con datos específicos
4. WHEN se valide documentación THEN el sistema SHALL verificar que todos los ejemplos sean ejecutables contra la API real

### Requirement 5

**User Story:** Como desarrollador, quiero un comando simple que regenere todas las configuraciones de testing, para que pueda mantener sincronizados los datos de prueba fácilmente.

#### Acceptance Criteria

1. WHEN se ejecuta el comando de regeneración THEN el sistema SHALL actualizar Postman, Swagger y Kafka testing en una sola operación
2. WHEN se detectan cambios en SQL THEN el sistema SHALL identificar qué configuraciones necesitan actualización
3. WHEN se regeneran configuraciones THEN el sistema SHALL crear backups de las configuraciones existentes
4. WHEN se completa la regeneración THEN el sistema SHALL proporcionar un reporte de cambios realizados