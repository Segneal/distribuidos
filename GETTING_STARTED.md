# 🚀 Guía de Inicio Rápido - Sistema ONG Backend

Esta guía está diseñada para alguien que **recién importa el proyecto** y quiere tenerlo funcionando lo más rápido posible.

## ⚡ Inicio en 5 Minutos

### Paso 1: Prerrequisitos (2 minutos)

Asegúrate de tener instalado:

- **Docker Desktop** - [Descargar aquí](https://www.docker.com/products/docker-desktop/)
- **Git** - [Descargar aquí](https://git-scm.com/downloads)

**Verificar instalación:**
```bash
docker --version
docker-compose --version
git --version
```

### Paso 2: Clonar el Proyecto (30 segundos)

```bash
git clone <repository-url>
cd distribuidos
```

### Paso 3: Desplegar Todo (2 minutos)

**En Windows (PowerShell o CMD):**
```cmd
scripts\deploy.bat
```

**En Linux/Mac:**
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Paso 4: Verificar que Funciona (30 segundos)

```bash
# Verificar que todos los servicios están corriendo
docker-compose ps

# Probar la API
curl http://localhost:3000/health
```

**¡Listo!** Tu sistema debería estar funcionando en: http://localhost:3000

---

## 🎯 ¿Qué Acabas de Desplegar?

El script automáticamente configuró:

| Servicio | Puerto | URL | Descripción |
|----------|--------|-----|-------------|
| **API Gateway** | 3000 | http://localhost:3000 | Punto de entrada principal |
| **Documentación** | 3000 | http://localhost:3000/api-docs | Swagger UI interactivo |
| **User Service** | 50051 | gRPC interno | Gestión de usuarios |
| **Events Service** | 50053 | gRPC interno | Gestión de eventos |
| **Inventory Service** | 50052 | gRPC interno | Gestión de inventario |
| **MySQL** | 3308 | localhost:3308 | Base de datos |
| **Kafka** | 9092 | localhost:9092 | Sistema de mensajería |

## 🧪 Primeras Pruebas

### 1. Verificar Estado del Sistema
```bash
# Ver todos los contenedores
docker-compose ps

# Debería mostrar algo como:
# ong-api-gateway         Up (healthy)
# ong-user-service        Up 
# ong-events-service      Up
# ong-inventory-service   Up
# ong-mysql               Up (healthy)
# ong-kafka               Up (healthy)
# ong-zookeeper           Up (healthy)
```

### 2. Probar la API
```bash
# Health check
curl http://localhost:3000/health

# Ver documentación en el navegador
# http://localhost:3000/api-docs
```

### 3. Credenciales por Defecto
- **Usuario**: `admin@ong.com`
- **Contraseña**: `password123`
- **Rol**: PRESIDENTE (acceso completo)

### 4. Primer Login
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@ong.com",
    "password": "password123"
  }'
```

## 🔧 Comandos Útiles

### Ver Logs
```bash
# Logs de todos los servicios
docker-compose logs

# Logs de un servicio específico
docker-compose logs api-gateway
docker-compose logs user-service
docker-compose logs mysql
```

### Reiniciar Servicios
```bash
# Reiniciar todo
docker-compose restart

# Reiniciar un servicio específico
docker-compose restart api-gateway
```

### Detener el Sistema
```bash
# Detener servicios (mantiene datos)
docker-compose stop

# Detener y eliminar contenedores (mantiene datos)
docker-compose down

# Detener y eliminar TODO (incluyendo datos)
docker-compose down -v
```

## 🚨 Solución de Problemas Comunes

### Problema: "Puerto 3000 ya está en uso"
```bash
# Ver qué está usando el puerto
netstat -ano | findstr :3000

# Cambiar el puerto en docker-compose.yml
# Buscar "3000:3000" y cambiar por "3001:3000"
```

### Problema: "Docker no está corriendo"
1. Abrir Docker Desktop
2. Esperar a que inicie completamente
3. Volver a ejecutar `scripts\deploy.bat`

### Problema: "Servicios no inician"
```bash
# Ver logs detallados
docker-compose logs --tail=50

# Reiniciar desde cero
docker-compose down -v
scripts\deploy.bat
```

### Problema: "No puedo acceder a la API"
```bash
# Verificar que el API Gateway esté corriendo
docker-compose ps api-gateway

# Ver logs del API Gateway
docker-compose logs api-gateway

# Verificar conectividad
curl http://localhost:3000/health
```

## 📚 Próximos Pasos

### 1. Explorar la API
- Abre http://localhost:3000/api-docs
- Prueba los endpoints con Swagger UI
- Usa las credenciales por defecto para autenticarte

### 2. Ver Datos de Ejemplo
El sistema viene con datos de ejemplo:
- Usuarios con diferentes roles
- Donaciones de ejemplo
- Eventos de prueba

### 3. Entender la Arquitectura
- Lee el [README.md](README.md) principal
- Explora la estructura de carpetas
- Revisa los archivos de configuración

### 4. Desarrollo
Si quieres modificar el código:
- Cada servicio tiene su propio README
- Los cambios se reflejan automáticamente con Docker
- Usa `docker-compose logs` para debugging

## 🆘 ¿Algo No Funciona?

### Diagnóstico Automático
```bash
# Script de diagnóstico completo
python scripts/health-check.py

# Verificar conectividad paso a paso
python test-system-step-by-step.py
```

### Reinicio Completo
```bash
# En Windows
scripts\reset.bat

# En Linux/Mac
./scripts/reset.sh
```

### Verificar Prerrequisitos
```bash
# Docker
docker --version
docker-compose --version

# Verificar que Docker Desktop esté corriendo
docker ps
```

---

## 🎉 ¡Felicidades!

Si llegaste hasta aquí, tienes un sistema completo de gestión de ONGs funcionando con:

- ✅ API REST completa
- ✅ Base de datos configurada
- ✅ Sistema de mensajería
- ✅ Documentación interactiva
- ✅ Datos de ejemplo

**¡Ahora puedes empezar a explorar y desarrollar!** 🚀

---

### 📞 Soporte

Si tienes problemas:
1. Revisa esta guía
2. Verifica los logs: `docker-compose logs`
3. Ejecuta el diagnóstico: `python scripts/health-check.py`
4. Reinicia desde cero: `scripts\reset.bat`

**El sistema debería funcionar en cualquier máquina con Docker instalado.** 💪