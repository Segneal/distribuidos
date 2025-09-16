# Plan de Implementación - Sistema ONG Backend

- [x] 1. Configurar estructura del proyecto y herramientas base
  - Crear estructura de directorios para microservicios y API Gateway
  - Configurar Docker Compose para MySQL, Kafka y Zookeeper
  - Configurar archivos .gitignore y documentación base
  - _Requerimientos: 14.1, 14.4, 16.1_

- [x] 2. Implementar definiciones gRPC y modelos de datos





- [x] 2.1 Crear archivos .proto para servicios gRPC


  - Definir usuario.proto con servicios de gestión de usuarios
  - Definir inventario.proto con servicios de donaciones
  - Definir evento.proto con servicios de eventos solidarios
  - Generar código Python desde archivos .proto
  - _Requerimientos: 14.2, 14.3_



- [x] 2.2 Crear esquemas de base de datos MySQL





  - Implementar script de migración para tabla usuarios
  - Implementar script de migración para tabla donaciones
  - Implementar script de migración para tabla eventos y relaciones
  - Implementar script de migración para tablas de red de ONGs
  - _Requerimientos: 2.1, 4.1, 5.1, 7.1_
-

- [ ] 3. Implementar servicio de usuarios con gRPC

- [x] 3.1 Crear estructura base del servicio de usuarios



  - Configurar servidor gRPC en Python
  - Implementar conexión a base de datos MySQL
  - Crear modelos de datos para usuarios
  - Configurar encriptación bcrypt para contraseñas
  - Configurar Nodemailer con Ethereal para envío de emails
  - _Requerimientos: 2.1, 2.2, 15.2_

- [x] 3.2 Implementar operaciones CRUD de usuarios
  - Implementar método crearUsuario con generación de clave aleatoria
  - Integrar envío de email con contraseña usando Nodemailer + Ethereal
  - Implementar método obtenerUsuario y listarUsuarios
  - Implementar método actualizarUsuario (sin modificar clave)
  - Implementar método eliminarUsuario (baja lógica)
  - _Requerimientos: 2.1, 2.2, 2.4, 2.5_


- [x] 3.3 Implementar autenticación y autorización


  - Implementar método autenticarUsuario con validación de credenciales
  - Implementar generación y validación de tokens JWT
  - Implementar validación de roles y permisos
  - Crear manejo de errores específicos de autenticación
  - _Requerimientos: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 15.3_

- [x] 4. Implementar servicio de inventario con gRPC





- [x] 4.1 Crear estructura base del servicio de inventario


  - Configurar servidor gRPC en Python
  - Implementar conexión a base de datos MySQL
  - Crear modelos de datos para donaciones
  - Configurar campos de auditoría automáticos
  - _Requerimientos: 4.1, 4.2, 15.1_

- [x] 4.2 Implementar operaciones CRUD de inventario


  - Implementar método crearDonacion con validaciones
  - Implementar método obtenerDonacion y listarDonaciones
  - Implementar método actualizarDonacion (solo descripcion y cantidad)
  - Implementar método eliminarDonacion (baja lógica con confirmación)
  - _Requerimientos: 4.1, 4.3, 4.4, 4.5, 4.6_

- [x] 4.3 Implementar control de stock y validaciones


  - Implementar método actualizarStock para transferencias
  - Implementar método validarStock antes de operaciones
  - Crear validaciones para cantidades negativas
  - Implementar auditoría de cambios de stock
  - _Requerimientos: 4.4, 8.3, 8.4, 8.5_

- [x] 5. Implementar servicio de eventos con gRPC


- [x] 5.1 Crear estructura base del servicio de eventos


  - Configurar servidor gRPC en Python
  - Implementar conexión a base de datos MySQL
  - Crear modelos de datos para eventos y participantes
  - Configurar validaciones de fechas futuras
  - _Requerimientos: 5.1, 5.2_

- [x] 5.2 Implementar operaciones CRUD de eventos


  - Implementar método crearEvento con validación de fecha futura
  - Implementar método obtenerEvento y listarEventos
  - Implementar método actualizarEvento según tipo (futuro/pasado)
  - Implementar método eliminarEvento (solo futuros, eliminación física)
  - _Requerimientos: 5.1, 5.2, 5.3, 5.6_

- [x] 5.3 Implementar gestión de participantes


  - Implementar método agregarParticipante con validaciones de rol
  - Implementar método quitarParticipante con validaciones de rol
  - Implementar lógica para Voluntarios (solo auto-asignación)
  - Implementar eliminación automática de participantes inactivos
  - _Requerimientos: 5.7, 6.1, 6.2, 6.3, 6.4_

- [x] 5.4 Implementar registro de donaciones repartidas


  - Implementar método registrarDonacionesRepartidas para eventos pasados
  - Integrar con servicio de inventario para descontar stock
  - Implementar auditoría de donaciones repartidas
  - Crear validaciones de stock disponible
  - _Requerimientos: 5.4, 5.5_

- [-] 6. Implementar API Gateway con Node.js y Express







- [x] 6.1 Crear estructura base del API Gateway
  - Configurar servidor Express con middleware básico
  - Implementar clientes gRPC para conectar con servicios
  - Configurar middleware de CORS y headers de seguridad
  - Crear estructura de rutas modular
  - _Requerimientos: 14.1_

- [x] 6.2 Implementar middleware de autenticación y autorización



  - Crear middleware de validación de tokens JWT
  - Implementar middleware de autorización por roles
  - Crear middleware de validación de entrada
  - Implementar manejo centralizado de errores
  - _Requerimientos: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 15.4_

- [x] 6.3 Implementar endpoints REST para usuarios






  - Crear POST /api/auth/login con validación de credenciales
  - Crear GET /api/usuarios (solo Presidente)
  - Crear POST /api/usuarios (solo Presidente)
  - Crear PUT /api/usuarios/:id y DELETE /api/usuarios/:id (solo Presidente)
  - _Requerimientos: 3.1, 3.2, 3.3, 2.1, 2.2, 2.4, 2.5_

- [x] 6.4 Implementar endpoints REST para inventario



  - Crear GET /api/inventario (Presidente, Vocal)
  - Crear POST /api/inventario (Presidente, Vocal)
  - Crear PUT /api/inventario/:id (Presidente, Vocal)
  - Crear DELETE /api/inventario/:id (Presidente, Vocal)
  - _Requerimientos: 4.1, 4.3, 4.5, 4.6_

- [x] 6.5 Implementar endpoints REST para eventos






  - Crear GET /api/eventos y POST /api/eventos (Presidente, Coordinador)
  - Crear PUT /api/eventos/:id y DELETE /api/eventos/:id (Presidente, Coordinador)
  - Crear POST /api/eventos/:id/participantes (gestión de participantes)
  - Crear endpoints para Voluntarios (solo consulta y auto-asignación)
  - _Requerimientos: 5.1, 5.2, 5.3, 5.6, 5.7, 6.1, 6.2, 6.3_

- [-] 7. Implementar integración con Kafka para red de ONGs



- [x] 7.1 Configurar productores y consumidores Kafka



  - Configurar cliente Kafka en cada servicio Python
  - Crear productores para publicar mensajes en topics
  - Crear consumidores para procesar mensajes entrantes
  - Implementar manejo de errores y reconexión automática
  - _Requerimientos: 14.4_

- [x] 7.2 Implementar funcionalidades de solicitud de donaciones





  - Crear endpoint POST /api/red/solicitudes-donaciones
  - Implementar publicación en topic "/solicitud-donaciones"
  - Implementar consumidor para procesar solicitudes externas
  - Crear endpoint GET /api/red/solicitudes-donaciones para listar
  - _Requerimientos: 7.1, 7.2, 7.3, 7.4_
-

- [x] 7.3 Implementar funcionalidades de transferencia de donaciones




  - Crear endpoint POST /api/red/transferencias-donaciones
  - Implementar publicación en topic "/transferencia-donaciones/{idOrganizacion}"
  - Implementar consumidor para recibir transferencias
  - Integrar con servicio de inventario para actualizar stock
  - _Requerimientos: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 7.4 Implementar funcionalidades de oferta de donaciones





  - Crear endpoint POST /api/red/ofertas-donaciones
  - Implementar publicación en topic "/oferta-donaciones"
  - Implementar consumidor para procesar ofertas externas
  - Crear endpoint GET /api/red/ofertas-donaciones para consulta
  - _Requerimientos: 9.1, 9.2, 9.3_

- [x] 7.5 Implementar funcionalidades de baja de solicitudes





  - Crear endpoint para dar de baja solicitudes propias
  - Implementar publicación en topic "/baja-solicitud-donaciones"
  - Implementar consumidor para procesar bajas externas
  - Actualizar estado de solicitudes en base de datos
  - _Requerimientos: 10.1, 10.2_

- [x] 7.6 Implementar funcionalidades de eventos externos





  - Implementar publicación en topic "/eventos-solidarios"
  - Implementar consumidor para procesar eventos externos (descartar propios)
  - Crear endpoint GET /api/red/eventos-externos para consulta
  - Implementar publicación y consumo de bajas de eventos
  - _Requerimientos: 11.1, 11.2, 11.3, 11.4, 12.1, 12.2_

- [x] 7.7 Implementar funcionalidades de adhesión a eventos externos





  - Crear endpoint POST /api/red/eventos-externos/adhesion
  - Implementar publicación en topic "/adhesion-evento/{idOrganizador}"
  - Validar que solo Voluntarios puedan adherirse
  - Incluir datos completos del voluntario en mensaje
  - _Requerimientos: 13.1, 13.2, 13.3_

- [x] 8. Implementar documentación y testing





- [x] 8.1 Crear documentación Swagger para API Gateway


  - Configurar Swagger/OpenAPI en Express
  - Documentar todos los endpoints REST con ejemplos
  - Incluir esquemas de request/response
  - Configurar autenticación JWT en Swagger UI
  - _Requerimientos: 14.5_

- [x] 8.2 Implementar pruebas unitarias para servicios


  - Crear pruebas unitarias para servicio de usuarios con pytest
  - Crear pruebas unitarias para servicio de inventario con pytest
  - Crear pruebas unitarias para servicio de eventos con pytest
  - Crear pruebas unitarias para API Gateway con Jest
  - _Requerimientos: 14.6_

- [x] 8.3 Crear colecciones Postman para testing


  - Crear colección Postman para endpoints de autenticación
  - Crear colección Postman para endpoints de usuarios
  - Crear colección Postman para endpoints de inventario
  - Crear colección Postman para endpoints de eventos
  - Crear colección Postman para endpoints de red de ONGs
  - _Requerimientos: 14.6_

- [x] 9. Crear documentación de módulos





- [x] 9.1 Crear README.md para API Gateway


  - Documentar propósito y funcionalidades del API Gateway
  - Incluir instrucciones de instalación y configuración
  - Documentar variables de entorno y dependencias
  - Incluir ejemplos de uso y testing
  - _Requerimientos: 16.1, 16.2, 16.3, 16.4_

- [x] 9.2 Crear README.md para servicio de usuarios


  - Documentar propósito y funcionalidades del servicio
  - Incluir instrucciones de instalación y configuración
  - Documentar métodos gRPC disponibles
  - Incluir ejemplos de uso y testing
  - _Requerimientos: 16.1, 16.2, 16.3, 16.4_

- [x] 9.3 Crear README.md para servicio de inventario


  - Documentar propósito y funcionalidades del servicio
  - Incluir instrucciones de instalación y configuración
  - Documentar métodos gRPC disponibles
  - Incluir ejemplos de uso y testing
  - _Requerimientos: 16.1, 16.2, 16.3, 16.4_

- [x] 9.4 Crear README.md para servicio de eventos


  - Documentar propósito y funcionalidades del servicio
  - Incluir instrucciones de instalación y configuración
  - Documentar métodos gRPC disponibles
  - Incluir ejemplos de uso y testing
  - _Requerimientos: 16.1, 16.2, 16.3, 16.4_

- [x] 10. Configurar despliegue y integración final







- [x] 10.1 Configurar Docker Compose completo



  - Integrar todos los servicios en docker-compose.yml
  - Configurar variables de entorno para cada servicio
  - Configurar volúmenes y redes Docker
  - Crear scripts de inicialización de base de datos


  - _Requerimientos: 14.4_

- [ ] 10.2 Crear scripts de despliegue y testing
  - Crear script deploy.sh para automatizar despliegue
  - Crear script test.sh para ejecutar todas las pruebas


  - Configurar healthchecks básicos para servicios
  - Crear script de limpieza y reset del entorno
  - _Requerimientos: 14.6_

- [ ] 10.3 Realizar testing de integración completo
  - Probar flujo completo de autenticación y autorización
  - Probar operaciones CRUD en todos los módulos
  - Probar integración Kafka con mensajes entre ONGs
  - Validar manejo de errores y casos edge
  - _Requerimientos: 1.6, 15.4, 15.5_