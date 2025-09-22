# Implementation Plan

- [x] 1. Crear script SQL centralizado con casos de prueba completos
  - Crear `database/init/02-test-cases.sql` con usuarios, donaciones, eventos y datos inter-ONG para testing
  - Incluir tabla `test_case_mapping` para mapear casos de prueba a endpoints específicos
  - Insertar casos de éxito, error, validación y autorización para todos los endpoints REST
  - Agregar datos para simular organizaciones externas y comunicación inter-ONG via Kafka
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2. Implementar extractor de datos desde SQL poblado





  - Crear `scripts/sql-driven-testing/data_extractor.py` con clase `SQLDataExtractor`
  - Implementar métodos para extraer usuarios por rol, inventario por categoría, eventos por estado
  - Agregar extracción de datos de red inter-ONG y mapeos de casos de prueba
  - Incluir validación de integridad de datos extraídos y relaciones de foreign keys
  - _Requirements: 2.1, 3.1, 5.2_

- [x] 3. Crear generador automático de colecciones Postman





  - Implementar `scripts/sql-driven-testing/postman_generator.py` con clase `PostmanGenerator`
  - Generar requests con datos reales extraídos de SQL para cada endpoint
  - Crear tests automáticos que validen responses contra datos conocidos de la base de datos
  - Actualizar variables de entorno con IDs, tokens y datos específicos de cada rol de usuario
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 4. Implementar actualizador de ejemplos Swagger





  - Crear `scripts/sql-driven-testing/swagger_generator.py` con clase `SwaggerGenerator`
  - Actualizar ejemplos de request/response en documentación Swagger con datos reales
  - Preservar documentación existente mientras actualiza solo secciones de ejemplos
  - Validar que ejemplos generados sean ejecutables contra la API real
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 5. Desarrollar generador de escenarios Kafka inter-ONG








  - Implementar `scripts/sql-driven-testing/kafka_generator.py` con clase `KafkaTestGenerator`
  - Generar mensajes de prueba para topics inter-ONG usando datos consistentes con SQL
  - Crear escenarios para solicitudes, ofertas, transferencias y eventos entre organizaciones
  - Incluir validaciones de pre y post condiciones para cada escenario de comunicación
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 6. Crear orquestador principal del sistema






  - Implementar `scripts/sql-driven-testing/orchestrator.py` con clase `TestingOrchestrator`
  - Coordinar extracción de datos y generación de todas las configuraciones en secuencia
  - Implementar sistema de backups automáticos antes de modificar configuraciones existentes
  - Agregar validación completa de datos extraídos y configuraciones generadas
  - _Requirements: 5.1, 5.3, 5.4_

- [x] 7. Implementar script principal de línea de comandos





  - Crear `scripts/generate-testing-configs.py` como punto de entrada principal
  - Agregar opciones para generar configuraciones específicas (--postman, --swagger, --kafka)
  - Implementar comando de regeneración completa y restauración desde backups
  - Incluir reporte detallado de cambios realizados y validaciones ejecutadas
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 8. Crear sistema de validación y testing





  - Implementar validadores para cada tipo de configuración generada
  - Crear tests unitarios para extractores y generadores individuales
  - Agregar tests de integración que validen el flujo completo desde SQL hasta configuraciones
  - Incluir tests end-to-end que ejecuten configuraciones generadas contra servicios reales
  - _Requirements: 2.4, 4.4, 5.4_

- [x] 9. Integrar con sistema de base de datos existente





  - Modificar scripts de inicialización para incluir casos de prueba centralizados
  - Actualizar docker-compose para ejecutar nuevo script SQL automáticamente
  - Verificar compatibilidad con sistema de población de datos actual
  - Documentar proceso de migración desde sistema actual de generación de datos
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 10. Crear documentación y guías de uso





  - Documentar estructura de casos de prueba en SQL y cómo agregar nuevos casos
  - Crear guía de uso del sistema de generación automática de configuraciones
  - Incluir ejemplos de comandos y opciones disponibles para diferentes escenarios
  - Agregar troubleshooting para problemas comunes de generación y validación
  - _Requirements: 5.1, 5.2, 5.3, 5.4_