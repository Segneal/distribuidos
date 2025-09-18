# Documentación

Este directorio reúne toda la documentación del proyecto Sistema ONG Backend.

## Estructura

- `api/` - Documentación y especificaciones de la API.
- `architecture/` - Diagramas y documentación de arquitectura.
- `deployment/` - Guías de despliegue y configuración.
- `development/` - Configuración y lineamientos de desarrollo.

## Documentación de la API

La documentación de la API se genera automáticamente con Swagger/OpenAPI y está disponible en:
- Desarrollo: http://localhost:3000/api-docs
- Producción: [URL de producción]/api-docs

## Resumen de la arquitectura

El sistema adopta una arquitectura de microservicios compuesta por:
- API Gateway (Node.js + Express).
- Servicio de usuarios (Python + gRPC).
- Servicio de inventario (Python + gRPC).
- Servicio de eventos (Python + gRPC).
- Base de datos MySQL.
- Apache Kafka para mensajería.

## Cómo empezar

1. Consultá el [README.md](../README.md) principal para ver el inicio rápido.
2. Revisá los README de cada servicio para configuraciones específicas.
3. Analizá la documentación de la API para conocer los endpoints.
4. Seguí las guías de desarrollo antes de contribuir.

## Soporte

Ante dudas sobre la documentación o la arquitectura, contactá al equipo de desarrollo.
