# Servicio de Eventos - Sistema ONG Backend

## Propósito y Funcionalidades

### Propósito Principal
El Servicio de Eventos es un microservicio gRPC que gestiona eventos solidarios para la ONG "Empuje Comunitario". Actúa como el núcleo de coordinación de actividades, proporcionando funcionalidades completas de CRUD para eventos, gestión de participantes, registro de donaciones distribuidas y integración con la red de ONGs para eventos externos.

### Arquitectura del Servicio
- **Protocolo**: gRPC para comunicación de alta performance
- **Base de Datos**: MySQL con pool de conexiones optimizado
- **Integración**: Kafka para comunicación con red de ONGs
- **Validaciones**: Reglas de negocio para fechas futuras y participantes
- **Auditoría**: Registro completo de todas las operaciones críticas

## Funcionalidades

### Gestión de Eventos
- **Crear eventos**: Registro de nuevos eventos solidarios con validación de fechas futuras
- **Consultar eventos**: Obtener eventos por ID o listar con paginación y filtros
- **Actualizar eventos**: Modificar eventos futuros (nombre, fecha, participantes) o registrar donaciones en eventos pasados
- **Eliminar eventos**: Eliminación física solo para eventos futuros

### Gestión de Participantes
- **Agregar participantes**: Asignación de miembros a eventos con validación de roles
- **Quitar participantes**: Remoción de participantes con validaciones específicas por rol
- **Auto-asignación**: Voluntarios pueden agregarse/quitarse a sí mismos
- **Limpieza automática**: Eliminación de participantes inactivos

### Registro de Donaciones Distribuidas
- **Registrar distribuciones**: Para eventos pasados, registro de donaciones entregadas
- **Integración con inventario**: Descuento automático del stock disponible
- **Auditoría completa**: Registro de qué, cuándo y quién distribuyó

### Red de ONGs (Kafka Integration)
- **Eventos externos**: Publicación y consumo de eventos de otras organizaciones
- **Adhesiones**: Gestión de participación de voluntarios en eventos externos
- **Sincronización**: Manejo de bajas y actualizaciones de eventos externos

## Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- MySQL 8.0+
- Apache Kafka (para funcionalidades de red de ONGs)
- pip (gestor de paquetes de Python)

### Instalación de Dependencias

```bash
# Navegar al directorio del servicio
cd grpc/services/events-service

# Instalar dependencias
pip install -r requirements.txt
```

### Configuración de Variables de Entorno

1. Copiar el archivo de ejemplo:
```bash
cp .env.example .env
```

2. Editar `.env` con tus configuraciones:
```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ong_sistema
DB_USER=ong_user
DB_PASSWORD=ong_password

# gRPC Configuration
GRPC_PORT=50053

# Kafka Configuration
KAFKA_BROKERS=localhost:9092
KAFKA_GROUP_ID=events-service-group

# Organization Configuration
ORGANIZATION_ID=ong-empuje-comunitario

# Logging
LOG_LEVEL=INFO
```

### Configuración de Base de Datos

1. Asegúrate de que MySQL esté ejecutándose
2. Crea la base de datos y las tablas ejecutando los scripts en `database/init/`
3. Verifica que las siguientes tablas estén creadas:
   - `eventos`
   - `evento_participantes`
   - `donaciones_repartidas`
   - `eventos_externos`

## Uso

### Iniciar el Servidor

```bash
# Desde el directorio del servicio
python src/main.py
```

El servidor gRPC estará disponible en `localhost:50053` (o el puerto configurado).

### Métodos gRPC Disponibles

#### CrearEvento
Crea un nuevo evento solidario con validación de fecha futura.

**Request:**
```protobuf
message CrearEventoRequest {
  string nombre = 1;           // Nombre del evento (requerido)
  string descripcion = 2;      // Descripción detallada
  string fechaHora = 3;        // Fecha y hora en formato ISO (debe ser futura)
  string usuarioCreador = 4;   // Usuario que crea el evento
}
```

**Response:**
```protobuf
message EventoResponse {
  bool exitoso = 1;
  Evento evento = 2;
  string mensaje = 3;
}
```

#### ObtenerEvento
Obtiene un evento específico por ID.

**Request:**
```protobuf
message ObtenerEventoRequest {
  int32 id = 1;  // ID del evento
}
```

#### ListarEventos
Lista eventos con paginación y filtros opcionales.

**Request:**
```protobuf
message ListarEventosRequest {
  int32 pagina = 1;              // Número de página (default: 1)
  int32 tamanoPagina = 2;        // Tamaño de página (default: 10, max: 100)
  bool soloFuturos = 3;          // Filtrar solo eventos futuros (default: false)
  bool soloPasados = 4;          // Filtrar solo eventos pasados (default: false)
  string usuarioParticipante = 5; // Filtrar por participante específico
}
```

#### ActualizarEvento
Actualiza un evento existente. Para eventos futuros permite cambiar datos básicos, para eventos pasados solo permite registrar donaciones distribuidas.

**Request:**
```protobuf
message ActualizarEventoRequest {
  int32 id = 1;                    // ID del evento
  string nombre = 2;               // Nuevo nombre (solo eventos futuros)
  string descripcion = 3;          // Nueva descripción (solo eventos futuros)
  string fechaHora = 4;            // Nueva fecha (solo eventos futuros)
  string usuarioModificacion = 5;  // Usuario que modifica
}
```

#### EliminarEvento
Elimina un evento (solo eventos futuros, eliminación física).

**Request:**
```protobuf
message EliminarEventoRequest {
  int32 id = 1;                   // ID del evento
  string usuarioEliminacion = 2;  // Usuario que elimina
}
```

#### AgregarParticipante
Agrega un participante a un evento con validaciones de rol.

**Request:**
```protobuf
message AgregarParticipanteRequest {
  int32 eventoId = 1;           // ID del evento
  int32 usuarioId = 2;          // ID del usuario a agregar
  string usuarioSolicitante = 3; // Usuario que hace la solicitud
}
```

#### QuitarParticipante
Quita un participante de un evento con validaciones de rol.

**Request:**
```protobuf
message QuitarParticipanteRequest {
  int32 eventoId = 1;           // ID del evento
  int32 usuarioId = 2;          // ID del usuario a quitar
  string usuarioSolicitante = 3; // Usuario que hace la solicitud
}
```

#### RegistrarDonacionesRepartidas
Registra donaciones distribuidas en un evento pasado e integra con el servicio de inventario.

**Request:**
```protobuf
message RegistrarDonacionesRequest {
  int32 eventoId = 1;                              // ID del evento
  repeated DonacionRepartida donaciones = 2;       // Lista de donaciones distribuidas
  string usuarioRegistro = 3;                     // Usuario que registra
}

message DonacionRepartida {
  int32 donacionId = 1;        // ID de la donación del inventario
  int32 cantidadRepartida = 2; // Cantidad distribuida
}
```

## Testing y Ejemplos de Uso

### Ejecutar Pruebas

**Pruebas unitarias:**
```bash
# Ejecutar todas las pruebas
python -m pytest tests/ -v

# Ejecutar pruebas específicas
python -m pytest tests/test_evento_model.py -v
python -m pytest tests/test_evento_crud.py -v
python -m pytest tests/test_evento_grpc_service.py -v

# Ejecutar con cobertura
python -m pytest tests/ --cov=src --cov-report=html
```

**Scripts de demostración:**
```bash
# Demo básico de funcionalidades
python demo_basic_functionality.py

# Demo de operaciones CRUD
python demo_crud_operations.py

# Demo de gestión de participantes
python demo_participant_management.py

# Demo de distribución de donaciones
python demo_distributed_donations.py
```

### Ejemplos de Uso Completos

#### Ejemplo 1: Cliente gRPC Básico

```python
import grpc
import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from grpc import events_pb2, events_pb2_grpc

def main():
    # Conectar al servicio
    channel = grpc.insecure_channel('localhost:50053')
    stub = events_pb2_grpc.EventoServiceStub(channel)
    
    try:
        # 1. Crear evento
        print("=== Creando Evento ===")
        fecha_futura = (datetime.now() + timedelta(days=7)).isoformat()
        
        create_request = events_pb2.CrearEventoRequest(
            nombre="Entrega de Alimentos Mensual",
            descripcion="Distribución de alimentos en el barrio San José",
            fechaHora=fecha_futura,
            usuarioCreador="coordinador1"
        )
        
        create_response = stub.CrearEvento(create_request)
        print(f"Evento creado: {create_response.exitoso}")
        print(f"ID: {create_response.evento.id}")
        print(f"Mensaje: {create_response.mensaje}")
        
        if create_response.exitoso:
            evento_id = create_response.evento.id
            
            # 2. Obtener evento
            print(f"\n=== Obteniendo Evento ID: {evento_id} ===")
            get_request = events_pb2.ObtenerEventoRequest(id=evento_id)
            get_response = stub.ObtenerEvento(get_request)
            
            if get_response.exitoso:
                evento = get_response.evento
                print(f"Nombre: {evento.nombre}")
                print(f"Descripción: {evento.descripcion}")
                print(f"Fecha: {evento.fechaHora}")
                print(f"Participantes: {len(evento.participantesIds)}")
            
            # 3. Agregar participantes
            print(f"\n=== Agregando Participantes ===")
            participantes_test = [2, 3, 4]  # IDs de usuarios de prueba
            
            for usuario_id in participantes_test:
                add_request = events_pb2.AgregarParticipanteRequest(
                    eventoId=evento_id,
                    usuarioId=usuario_id,
                    usuarioSolicitante="coordinador1"
                )
                
                add_response = stub.AgregarParticipante(add_request)
                if add_response.exitoso:
                    print(f"✓ Participante {usuario_id} agregado")
                else:
                    print(f"✗ Error agregando participante {usuario_id}: {add_response.mensaje}")
            
            # 4. Listar eventos
            print("\n=== Listando Eventos ===")
            list_request = events_pb2.ListarEventosRequest(
                pagina=1,
                tamanoPagina=10,
                soloFuturos=True
            )
            
            list_response = stub.ListarEventos(list_request)
            print(f"Total eventos futuros: {list_response.total}")
            
            for evento in list_response.eventos:
                print(f"- ID: {evento.id}, {evento.nombre} ({len(evento.participantesIds)} participantes)")
            
    except grpc.RpcError as e:
        print(f"Error gRPC: {e.code()} - {e.details()}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        channel.close()

if __name__ == "__main__":
    main()
```

#### Ejemplo 2: Gestión Avanzada de Participantes

```python
import grpc
from datetime import datetime, timedelta
from grpc import events_pb2, events_pb2_grpc

def demo_participant_management():
    """Demuestra la gestión avanzada de participantes"""
    channel = grpc.insecure_channel('localhost:50053')
    stub = events_pb2_grpc.EventoServiceStub(channel)
    
    try:
        # 1. Crear evento de prueba
        print("=== Creando Evento para Gestión de Participantes ===")
        fecha_futura = (datetime.now() + timedelta(days=10)).isoformat()
        
        create_request = events_pb2.CrearEventoRequest(
            nombre="Taller de Capacitación",
            descripcion="Taller sobre gestión de recursos comunitarios",
            fechaHora=fecha_futura,
            usuarioCreador="coordinador1"
        )
        
        create_response = stub.CrearEvento(create_request)
        if not create_response.exitoso:
            print(f"Error creando evento: {create_response.mensaje}")
            return
            
        evento_id = create_response.evento.id
        print(f"✓ Evento creado con ID: {evento_id}")
        
        # 2. Simular diferentes tipos de asignaciones
        print("\n=== Simulando Asignaciones por Rol ===")
        
        # Coordinador asigna a otros usuarios
        asignaciones_coordinador = [
            {"usuarioId": 2, "descripcion": "Voluntario 1"},
            {"usuarioId": 3, "descripcion": "Voluntario 2"},
            {"usuarioId": 4, "descripcion": "Vocal 1"}
        ]
        
        for asignacion in asignaciones_coordinador:
            print(f"\nCoordinador asignando a {asignacion['descripcion']} (ID: {asignacion['usuarioId']})")
            
            request = events_pb2.AgregarParticipanteRequest(
                eventoId=evento_id,
                usuarioId=asignacion["usuarioId"],
                usuarioSolicitante="coordinador1"
            )
            
            response = stub.AgregarParticipante(request)
            if response.exitoso:
                print(f"  ✓ Asignación exitosa")
            else:
                print(f"  ✗ Error: {response.mensaje}")
        
        # 3. Simular auto-asignación de voluntario
        print("\n=== Simulando Auto-asignación de Voluntario ===")
        
        auto_request = events_pb2.AgregarParticipanteRequest(
            eventoId=evento_id,
            usuarioId=5,  # ID del voluntario que se auto-asigna
            usuarioSolicitante="voluntario1"  # Mismo usuario
        )
        
        auto_response = stub.AgregarParticipante(auto_request)
        if auto_response.exitoso:
            print("✓ Voluntario se auto-asignó exitosamente")
        else:
            print(f"✗ Error en auto-asignación: {auto_response.mensaje}")
        
        # 4. Verificar participantes actuales
        print("\n=== Verificando Participantes Actuales ===")
        
        get_request = events_pb2.ObtenerEventoRequest(id=evento_id)
        get_response = stub.ObtenerEvento(get_request)
        
        if get_response.exitoso:
            evento = get_response.evento
            print(f"Evento: {evento.nombre}")
            print(f"Total participantes: {len(evento.participantesIds)}")
            print(f"IDs de participantes: {list(evento.participantesIds)}")
        
        # 5. Simular remoción de participantes
        print("\n=== Simulando Remoción de Participantes ===")
        
        # Coordinador quita a un participante
        remove_request = events_pb2.QuitarParticipanteRequest(
            eventoId=evento_id,
            usuarioId=3,  # Quitar voluntario 2
            usuarioSolicitante="coordinador1"
        )
        
        remove_response = stub.QuitarParticipante(remove_request)
        if remove_response.exitoso:
            print("✓ Coordinador quitó participante exitosamente")
        else:
            print(f"✗ Error quitando participante: {remove_response.mensaje}")
        
        # Voluntario se quita a sí mismo
        self_remove_request = events_pb2.QuitarParticipanteRequest(
            eventoId=evento_id,
            usuarioId=5,  # Voluntario se quita a sí mismo
            usuarioSolicitante="voluntario1"
        )
        
        self_remove_response = stub.QuitarParticipante(self_remove_request)
        if self_remove_response.exitoso:
            print("✓ Voluntario se quitó a sí mismo exitosamente")
        else:
            print(f"✗ Error en auto-remoción: {self_remove_response.mensaje}")
        
        # 6. Verificar estado final
        print("\n=== Estado Final del Evento ===")
        
        final_get_request = events_pb2.ObtenerEventoRequest(id=evento_id)
        final_get_response = stub.ObtenerEvento(final_get_request)
        
        if final_get_response.exitoso:
            evento_final = final_get_response.evento
            print(f"Participantes finales: {len(evento_final.participantesIds)}")
            print(f"IDs finales: {list(evento_final.participantesIds)}")
        
    except grpc.RpcError as e:
        print(f"Error gRPC: {e.code()} - {e.details()}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        channel.close()

if __name__ == "__main__":
    demo_participant_management()
```

#### Ejemplo 3: Registro de Donaciones Distribuidas

```python
import grpc
from datetime import datetime, timedelta
from grpc import events_pb2, events_pb2_grpc

def demo_donation_distribution():
    """Demuestra el registro de donaciones distribuidas en eventos pasados"""
    channel = grpc.insecure_channel('localhost:50053')
    stub = events_pb2_grpc.EventoServiceStub(channel)
    
    try:
        # 1. Crear evento en el pasado (para simular evento ya realizado)
        print("=== Creando Evento Pasado para Distribución ===")
        fecha_pasada = (datetime.now() - timedelta(days=2)).isoformat()
        
        # Nota: En producción, no se pueden crear eventos pasados
        # Este ejemplo asume que ya existe un evento pasado
        print("Nota: En este ejemplo asumimos que ya existe un evento pasado")
        
        # Simular que tenemos un evento pasado con ID conocido
        evento_pasado_id = 1  # ID de evento existente
        
        # 2. Registrar donaciones distribuidas
        print(f"\n=== Registrando Donaciones Distribuidas en Evento {evento_pasado_id} ===")
        
        # Preparar lista de donaciones distribuidas
        donaciones_distribuidas = [
            {"donacionId": 1, "cantidadRepartida": 20, "descripcion": "Arroz 1kg"},
            {"donacionId": 2, "cantidadRepartida": 15, "descripcion": "Frijoles 500g"},
            {"donacionId": 3, "cantidadRepartida": 10, "descripcion": "Aceite 1L"}
        ]
        
        # Crear lista de DonacionRepartida para el request
        donaciones_pb = []
        for donacion in donaciones_distribuidas:
            donacion_pb = events_pb2.DonacionRepartida(
                donacionId=donacion["donacionId"],
                cantidadRepartida=donacion["cantidadRepartida"]
            )
            donaciones_pb.append(donacion_pb)
            print(f"Preparando: {donacion['descripcion']} - {donacion['cantidadRepartida']} unidades")
        
        # Registrar las donaciones
        register_request = events_pb2.RegistrarDonacionesRequest(
            eventoId=evento_pasado_id,
            donaciones=donaciones_pb,
            usuarioRegistro="coordinador1"
        )
        
        register_response = stub.RegistrarDonacionesRepartidas(register_request)
        
        if register_response.exitoso:
            print("✓ Donaciones registradas exitosamente")
            print(f"Total donaciones registradas: {len(donaciones_distribuidas)}")
            
            # Mostrar resumen
            total_items = sum(d["cantidadRepartida"] for d in donaciones_distribuidas)
            print(f"Total items distribuidos: {total_items}")
            
        else:
            print(f"✗ Error registrando donaciones: {register_response.mensaje}")
        
        # 3. Verificar el evento actualizado
        print(f"\n=== Verificando Evento Actualizado ===")
        
        get_request = events_pb2.ObtenerEventoRequest(id=evento_pasado_id)
        get_response = stub.ObtenerEvento(get_request)
        
        if get_response.exitoso:
            evento = get_response.evento
            print(f"Evento: {evento.nombre}")
            print(f"Donaciones registradas: {len(evento.donacionesRepartidas)}")
            
            for donacion_repartida in evento.donacionesRepartidas:
                print(f"  - Donación ID {donacion_repartida.donacionId}: "
                      f"{donacion_repartida.cantidadRepartida} unidades "
                      f"(Registrado por: {donacion_repartida.usuarioRegistro})")
        
        # 4. Listar eventos con donaciones distribuidas
        print("\n=== Listando Eventos con Distribuciones ===")
        
        list_request = events_pb2.ListarEventosRequest(
            pagina=1,
            tamanoPagina=10,
            soloPasados=True
        )
        
        list_response = stub.ListarEventos(list_request)
        print(f"Total eventos pasados: {list_response.total}")
        
        for evento in list_response.eventos:
            donaciones_count = len(evento.donacionesRepartidas)
            status = "Con distribuciones" if donaciones_count > 0 else "Sin distribuciones"
            print(f"  - {evento.nombre}: {status} ({donaciones_count} registros)")
        
    except grpc.RpcError as e:
        print(f"Error gRPC: {e.code()} - {e.details()}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        channel.close()

if __name__ == "__main__":
    demo_donation_distribution()
```

### Pruebas de Integración

Para probar el servicio completo:

1. **Preparar el entorno:**
```bash
# Asegúrate de que MySQL esté ejecutándose
sudo systemctl start mysql  # Linux
# o
brew services start mysql   # macOS

# Verificar que la base de datos existe
mysql -u ong_user -p ong_sistema -e "SHOW TABLES;"

# Iniciar Kafka (para funcionalidades de red de ONGs)
docker-compose up -d kafka zookeeper
```

2. **Iniciar el servidor:**
```bash
python src/main.py
```

3. **Ejecutar pruebas:**
```bash
# Pruebas básicas
python demo_basic_functionality.py

# Pruebas CRUD
python demo_crud_operations.py

# Pruebas de participantes
python demo_participant_management.py

# Pruebas de distribución
python demo_distributed_donations.py
```

## Estructura del Proyecto

```
events-service/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── database.py          # Configuración de base de datos
│   ├── kafka/
│   │   ├── __init__.py
│   │   └── kafka_client.py      # Cliente Kafka para red de ONGs
│   ├── models/
│   │   ├── __init__.py
│   │   └── evento.py            # Modelo de datos Evento
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── evento_repository.py # Acceso a datos
│   ├── service/
│   │   ├── __init__.py
│   │   ├── evento_service.py    # Implementación gRPC
│   │   └── server.py            # Servidor gRPC
│   ├── grpc/
│   │   ├── __init__.py
│   │   ├── events_pb2.py        # Generado desde proto
│   │   └── events_pb2_grpc.py   # Generado desde proto
│   ├── __init__.py
│   └── main.py                  # Punto de entrada
├── tests/
│   ├── __init__.py
│   ├── test_evento_model.py     # Pruebas del modelo
│   ├── test_evento_crud.py      # Pruebas CRUD
│   └── test_evento_grpc_service.py # Pruebas del servicio gRPC
├── .env.example                 # Ejemplo de variables de entorno
├── demo_basic_functionality.py  # Demo básico
├── demo_crud_operations.py      # Demo CRUD
├── demo_participant_management.py # Demo participantes
├── demo_distributed_donations.py # Demo distribuciones
├── Dockerfile                   # Imagen Docker
├── requirements.txt             # Dependencias Python
└── README.md                    # Este archivo
```

## Validaciones de Negocio

### Eventos
- **Fecha**: Los eventos solo pueden crearse con fechas futuras
- **Actualización**: Eventos futuros permiten cambios completos, eventos pasados solo registro de donaciones
- **Eliminación**: Solo eventos futuros pueden eliminarse (eliminación física)
- **Participantes**: Solo usuarios activos pueden participar

### Participantes
- **Roles**: Presidente y Coordinador pueden gestionar cualquier participante
- **Voluntarios**: Solo pueden agregarse/quitarse a sí mismos
- **Validación**: No se permiten participantes duplicados
- **Limpieza**: Usuarios inactivos se quitan automáticamente

### Donaciones Distribuidas
- **Solo eventos pasados**: No se pueden registrar distribuciones en eventos futuros
- **Integración**: Descuenta automáticamente del inventario
- **Validación**: Verifica stock disponible antes de registrar
- **Auditoría**: Registra usuario, fecha y hora de cada distribución

## Integración con Otros Servicios

### API Gateway
El API Gateway se conecta a este servicio para exponer endpoints REST que internamente llaman a los métodos gRPC.

### Servicio de Inventario
Integración directa para:
- Validar stock disponible antes de registrar distribuciones
- Descontar automáticamente del inventario al registrar donaciones repartidas
- Mantener auditoría de cambios de stock

### Red de ONGs (Kafka)
El servicio se integra con Kafka para:
- Publicar eventos solidarios para otras ONGs
- Consumir eventos externos de la red
- Gestionar adhesiones de voluntarios a eventos externos
- Sincronizar bajas y actualizaciones de eventos

## Monitoreo y Logs

El servicio registra:
- Conexiones y desconexiones de clientes gRPC
- Creación, modificación y eliminación de eventos
- Cambios en participantes con detalles de usuario
- Registro de donaciones distribuidas con auditoría completa
- Errores de validación y base de datos
- Métricas de rendimiento de operaciones
- Actividad de Kafka (publicación/consumo de mensajes)

## Troubleshooting

### Problemas Comunes

1. **Error de conexión a base de datos**
   - Verifica que MySQL esté ejecutándose
   - Confirma las credenciales en `.env`
   - Asegúrate de que las tablas de eventos existan

2. **Puerto en uso**
   - Cambia `GRPC_PORT` en `.env`
   - Verifica que no haya otro servicio usando el puerto 50053

3. **Errores de validación de fechas**
   - Confirma que las fechas estén en formato ISO válido
   - Verifica que las fechas de eventos sean futuras al crear

4. **Problemas con Kafka**
   - Verifica que Kafka esté ejecutándose en el puerto configurado
   - Confirma la configuración de `KAFKA_BROKERS` en `.env`
   - Revisa los logs para errores de conexión

5. **Errores de participantes**
   - Verifica que los IDs de usuario existan y estén activos
   - Confirma que el usuario solicitante tenga permisos adecuados
   - Revisa que no haya participantes duplicados

## Contribución

Para contribuir al desarrollo:

1. Sigue las convenciones de código Python (PEP 8)
2. Agrega pruebas unitarias para nuevas funcionalidades
3. Actualiza la documentación según sea necesario
4. Asegúrate de que todas las pruebas pasen antes de enviar cambios
5. Considera el impacto en la integración con otros servicios
6. Documenta cualquier cambio en las validaciones de negocio

## Licencia

Este proyecto es parte del Sistema ONG Backend y está sujeto a las mismas condiciones de licencia del proyecto principal.