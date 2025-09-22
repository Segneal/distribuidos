# Postman Collections - Sistema ONG API

Este directorio contiene las colecciones de Postman para testing del API Gateway del Sistema ONG.

## Colecciones Disponibles

1. **01-Autenticacion.postman_collection.json** - Endpoints de autenticación y autorización
2. **02-Usuarios.postman_collection.json** - Gestión de usuarios (solo Presidente)
3. **03-Inventario.postman_collection.json** - Gestión de inventario de donaciones
4. **04-Eventos.postman_collection.json** - Gestión de eventos solidarios
5. **05-Red-ONGs.postman_collection.json** - Funcionalidades de red de ONGs

## Variables de Entorno

Antes de ejecutar las colecciones, configure las siguientes variables de entorno en Postman:

- `base_url`: URL base del API Gateway (ej: `http://localhost:3000`)
- `auth_token`: Token JWT obtenido del login (se actualiza automáticamente)
- `user_id`: ID del usuario autenticado (se actualiza automáticamente)

## Orden de Ejecución

1. Ejecute primero la colección de **Autenticación** para obtener el token
2. Las demás colecciones pueden ejecutarse en cualquier orden
3. Algunos endpoints requieren datos previos (ej: crear usuario antes de actualizarlo)

## Usuarios de Prueba

Las colecciones asumen la existencia de usuarios con diferentes roles:

- **Presidente**: Acceso completo al sistema
- **Vocal**: Acceso a inventario de donaciones
- **Coordinador**: Acceso a gestión de eventos
- **Voluntario**: Acceso limitado a eventos

## Notas Importantes

- Los tokens JWT tienen expiración, renueve el token si recibe errores 401
- Algunos endpoints modifican datos, úselos con precaución en entornos de producción
- Las colecciones incluyen tests automáticos para validar las respuestas