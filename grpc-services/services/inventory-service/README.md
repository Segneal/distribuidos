# Servicio de Inventario - Sistema ONG

## Propósito y Funcionalidades

### Propósito Principal
El Servicio de Inventario es un microservicio gRPC que gestiona el inventario de donaciones para la ONG "Empuje Comunitario". Actúa como el núcleo de gestión de recursos, proporcionando funcionalidades completas de CRUD (Crear, Leer, Actualizar, Eliminar) para donaciones, control de stock avanzado, validaciones de negocio robustas y auditoría completa de cambios.

### Arquitectura del Servicio
- **Protocolo**: gRPC para comunicación de alta performance
- **Base de Datos**: MySQL con pool de conexiones optimizado
- **Auditoría**: Registro completo de todas las operaciones críticas
- **Integración**: Kafka para comunicación con red de ONGs
- **Validaciones**: Reglas de negocio estrictas para integridad de datos

## Funcionalidades

### Gestión de Donaciones
- **Crear donaciones**: Registro de nuevas donaciones con validaciones
- **Consultar donaciones**: Obtener donaciones por ID o listar con paginación
- **Actualizar donaciones**: Modificar descripción y cantidad (campos permitidos)
- **Eliminar donaciones**: Baja lógica con confirmación

### Control de Stock
- **Actualizar stock**: Incrementar o decrementar cantidades para transferencias
- **Validar stock**: Verificar disponibilidad antes de operaciones
- **Auditoría**: Registro completo de cambios de stock con motivos

### Categorías Soportadas
- `ROPA`: Prendas de vestir y calzado
- `ALIMENTOS`: Comida y bebidas
- `JUGUETES`: Juguetes y entretenimiento
- `UTILES_ESCOLARES`: Material escolar y educativo

## Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- MySQL 8.0+
- pip (gestor de paquetes de Python)

### Instalación de Dependencias

```bash
# Navegar al directorio del servicio
cd grpc/services/inventory-service

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
GRPC_PORT=50052

# Kafka Configuration (para futuras integraciones)
KAFKA_BROKERS=localhost:9092
KAFKA_GROUP_ID=inventory-service-group

# Logging
LOG_LEVEL=INFO
```

### Configuración de Base de Datos

1. Asegúrate de que MySQL esté ejecutándose
2. Crea la base de datos y las tablas ejecutando los scripts en `database/init/`
3. Verifica que la tabla `auditoria_stock` esté creada para el registro de cambios

## Uso

### Iniciar el Servidor

```bash
# Desde el directorio del servicio
python src/main.py
```

El servidor gRPC estará disponible en `localhost:50052` (o el puerto configurado).

### Métodos gRPC Disponibles

#### CrearDonacion
Crea una nueva donación en el inventario.

**Request:**
```protobuf
message CrearDonacionRequest {
  string categoria = 1;        // ROPA, ALIMENTOS, JUGUETES, UTILES_ESCOLARES
  string descripcion = 2;      // Descripción del item (mín. 3 caracteres)
  int32 cantidad = 3;          // Cantidad (>= 0)
  string usuarioCreador = 4;   // Usuario que crea la donación
}
```

#### ObtenerDonacion
Obtiene una donación específica por ID.

**Request:**
```protobuf
message ObtenerDonacionRequest {
  int32 id = 1;  // ID de la donación
}
```

#### ListarDonaciones
Lista donaciones con paginación y filtros opcionales.

**Request:**
```protobuf
message ListarDonacionesRequest {
  int32 pagina = 1;              // Número de página (default: 1)
  int32 tamanoPagina = 2;        // Tamaño de página (default: 10, max: 100)
  string categoria = 3;          // Filtro por categoría (opcional)
  bool incluirEliminados = 4;    // Incluir donaciones eliminadas (default: false)
}
```

#### ActualizarDonacion
Actualiza una donación existente (solo descripción y cantidad).

**Request:**
```protobuf
message ActualizarDonacionRequest {
  int32 id = 1;                    // ID de la donación
  string descripcion = 2;          // Nueva descripción
  int32 cantidad = 3;              // Nueva cantidad
  string usuarioModificacion = 4;  // Usuario que modifica
}
```

#### EliminarDonacion
Realiza baja lógica de una donación.

**Request:**
```protobuf
message EliminarDonacionRequest {
  int32 id = 1;                   // ID de la donación
  string usuarioEliminacion = 2;  // Usuario que elimina
}
```

#### ActualizarStock
Actualiza el stock de una donación (para transferencias entre ONGs).

**Request:**
```protobuf
message ActualizarStockRequest {
  int32 donacionId = 1;           // ID de la donación
  int32 cantidadCambio = 2;       // Cambio en cantidad (+/-)
  string usuarioModificacion = 3; // Usuario que modifica
  string motivo = 4;              // Motivo del cambio
}
```

#### ValidarStock
Valida si hay stock suficiente para una operación.

**Request:**
```protobuf
message ValidarStockRequest {
  int32 donacionId = 1;        // ID de la donación
  int32 cantidadRequerida = 2; // Cantidad requerida
}
```

## Testing y Ejemplos de Uso

### Ejecutar Pruebas

**Pruebas unitarias:**
```bash
# Ejecutar todas las pruebas
python -m pytest tests/ -v

# Ejecutar pruebas específicas
python -m pytest tests/test_donacion_model.py -v
python -m pytest tests/test_donacion_repository.py -v
python -m pytest tests/test_stock_control.py -v

# Ejecutar con cobertura
python -m pytest tests/ --cov=src --cov-report=html
```

**Scripts de demostración:**
```bash
# Demo básico de funcionalidades
python demo_basic_functionality.py

# Demo de control de stock
python demo_stock_control.py

# Demo de operaciones CRUD
python demo_crud_operations.py
```

### Ejemplos de Uso Completos

#### Ejemplo 1: Cliente gRPC Básico

```python
import grpc
import sys
import os

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from inventory_pb2 import *
from inventory_pb2_grpc import InventarioServiceStub

def main():
    # Conectar al servicio
    channel = grpc.insecure_channel('localhost:50052')
    stub = InventarioServiceStub(channel)
    
    try:
        # 1. Crear donación
        print("=== Creando Donación ===")
        create_request = CrearDonacionRequest(
            categoria="ALIMENTOS",
            descripcion="Arroz integral 1kg",
            cantidad=50,
            usuarioCreador="admin"
        )
        
        create_response = stub.CrearDonacion(create_request)
        print(f"Donación creada: {create_response.exitoso}")
        print(f"ID: {create_response.donacion.id}")
        
        if create_response.exitoso:
            donacion_id = create_response.donacion.id
            
            # 2. Obtener donación
            print(f"\n=== Obteniendo Donación ID: {donacion_id} ===")
            get_request = ObtenerDonacionRequest(id=donacion_id)
            get_response = stub.ObtenerDonacion(get_request)
            
            if get_response.exitoso:
                donacion = get_response.donacion
                print(f"Categoría: {donacion.categoria}")
                print(f"Descripción: {donacion.descripcion}")
                print(f"Cantidad: {donacion.cantidad}")
                print(f"Creado por: {donacion.usuarioAlta}")
            
            # 3. Listar donaciones
            print("\n=== Listando Donaciones ===")
            list_request = ListarDonacionesRequest(
                pagina=1,
                tamanoPagina=10,
                incluirEliminados=False
            )
            
            list_response = stub.ListarDonaciones(list_request)
            print(f"Total donaciones: {list_response.total}")
            
            for donacion in list_response.donaciones:
                print(f"- ID: {donacion.id}, {donacion.categoria}: {donacion.descripcion} (Qty: {donacion.cantidad})")
            
            # 4. Actualizar donación
            print(f"\n=== Actualizando Donación ID: {donacion_id} ===")
            update_request = ActualizarDonacionRequest(
                id=donacion_id,
                descripcion="Arroz integral premium 1kg",
                cantidad=75,
                usuarioModificacion="admin"
            )
            
            update_response = stub.ActualizarDonacion(update_request)
            if update_response.exitoso:
                print("✓ Donación actualizada exitosamente")
                print(f"Nueva descripción: {update_response.donacion.descripcion}")
                print(f"Nueva cantidad: {update_response.donacion.cantidad}")
            
    except grpc.RpcError as e:
        print(f"Error gRPC: {e.code()} - {e.details()}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        channel.close()

if __name__ == "__main__":
    main()
```

#### Ejemplo 2: Control de Stock Avanzado

```python
import grpc
from inventory_pb2 import *
from inventory_pb2_grpc import InventarioServiceStub

def demo_stock_control():
    """Demuestra el control avanzado de stock"""
    channel = grpc.insecure_channel('localhost:50052')
    stub = InventarioServiceStub(channel)
    
    try:
        # 1. Crear donación inicial
        print("=== Creando Donación para Control de Stock ===")
        create_request = CrearDonacionRequest(
            categoria="ROPA",
            descripcion="Camisetas talla M",
            cantidad=100,
            usuarioCreador="admin"
        )
        
        create_response = stub.CrearDonacion(create_request)
        if not create_response.exitoso:
            print(f"Error creando donación: {create_response.mensaje}")
            return
            
        donacion_id = create_response.donacion.id
        print(f"✓ Donación creada con ID: {donacion_id}, Stock inicial: 100")
        
        # 2. Validar stock disponible
        print("\n=== Validando Stock Disponible ===")
        validate_request = ValidarStockRequest(
            donacionId=donacion_id,
            cantidadRequerida=30
        )
        
        validate_response = stub.ValidarStock(validate_request)
        print(f"Stock suficiente para 30 unidades: {validate_response.stockSuficiente}")
        print(f"Stock disponible: {validate_response.stockDisponible}")
        
        # 3. Simular transferencia (reducir stock)
        print("\n=== Simulando Transferencia a Otra ONG ===")
        transfer_request = ActualizarStockRequest(
            donacionId=donacion_id,
            cantidadCambio=-30,  # Reducir 30 unidades
            usuarioModificacion="admin",
            motivo="Transferencia a ONG Hermanos Unidos"
        )
        
        transfer_response = stub.ActualizarStock(transfer_request)
        if transfer_response.exitoso:
            print("✓ Transferencia exitosa")
            print(f"Stock anterior: 100")
            print(f"Stock actual: {transfer_response.stockActual}")
        
        # 4. Simular recepción de donación (aumentar stock)
        print("\n=== Simulando Recepción de Donación ===")
        receive_request = ActualizarStockRequest(
            donacionId=donacion_id,
            cantidadCambio=50,  # Agregar 50 unidades
            usuarioModificacion="admin",
            motivo="Donación recibida de empresa textil"
        )
        
        receive_response = stub.ActualizarStock(receive_request)
        if receive_response.exitoso:
            print("✓ Recepción exitosa")
            print(f"Stock actual: {receive_response.stockActual}")
        
        # 5. Intentar operación que excede stock
        print("\n=== Probando Validación de Stock Insuficiente ===")
        invalid_request = ValidarStockRequest(
            donacionId=donacion_id,
            cantidadRequerida=200  # Más del stock disponible
        )
        
        invalid_response = stub.ValidarStock(invalid_request)
        print(f"Stock suficiente para 200 unidades: {invalid_response.stockSuficiente}")
        if not invalid_response.stockSuficiente:
            print(f"✓ Validación correcta - Stock insuficiente")
            print(f"Requerido: 200, Disponible: {invalid_response.stockDisponible}")
        
        # 6. Intentar reducir más stock del disponible
        print("\n=== Probando Reducción Excesiva de Stock ===")
        excessive_request = ActualizarStockRequest(
            donacionId=donacion_id,
            cantidadCambio=-200,  # Intentar reducir más del disponible
            usuarioModificacion="admin",
            motivo="Prueba de validación"
        )
        
        excessive_response = stub.ActualizarStock(excessive_request)
        if not excessive_response.exitoso:
            print("✓ Validación correcta - Operación rechazada")
            print(f"Mensaje: {excessive_response.mensaje}")
        
    except grpc.RpcError as e:
        print(f"Error gRPC: {e.code()} - {e.details()}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        channel.close()

if __name__ == "__main__":
    demo_stock_control()
```

#### Ejemplo 3: Gestión por Categorías

```python
import grpc
from inventory_pb2 import *
from inventory_pb2_grpc import InventarioServiceStub

def demo_category_management():
    """Demuestra la gestión de inventario por categorías"""
    channel = grpc.insecure_channel('localhost:50052')
    stub = InventarioServiceStub(channel)
    
    # Datos de prueba por categoría
    donaciones_test = [
        {
            "categoria": "ALIMENTOS",
            "items": [
                {"descripcion": "Arroz blanco 1kg", "cantidad": 50},
                {"descripcion": "Frijoles negros 500g", "cantidad": 30},
                {"descripcion": "Aceite vegetal 1L", "cantidad": 25}
            ]
        },
        {
            "categoria": "ROPA", 
            "items": [
                {"descripcion": "Camisetas adulto M", "cantidad": 40},
                {"descripcion": "Pantalones niño talla 8", "cantidad": 20},
                {"descripcion": "Zapatos deportivos varios", "cantidad": 15}
            ]
        },
        {
            "categoria": "UTILES_ESCOLARES",
            "items": [
                {"descripcion": "Cuadernos rayados", "cantidad": 100},
                {"descripcion": "Lápices #2", "cantidad": 200},
                {"descripcion": "Borradores blancos", "cantidad": 50}
            ]
        },
        {
            "categoria": "JUGUETES",
            "items": [
                {"descripcion": "Pelotas de fútbol", "cantidad": 10},
                {"descripcion": "Muñecas variadas", "cantidad": 15},
                {"descripcion": "Juegos de mesa", "cantidad": 8}
            ]
        }
    ]
    
    try:
        # 1. Crear donaciones por categoría
        print("=== Creando Inventario por Categorías ===")
        created_items = {}
        
        for categoria_data in donaciones_test:
            categoria = categoria_data["categoria"]
            print(f"\nCreando items para categoría: {categoria}")
            created_items[categoria] = []
            
            for item in categoria_data["items"]:
                request = CrearDonacionRequest(
                    categoria=categoria,
                    descripcion=item["descripcion"],
                    cantidad=item["cantidad"],
                    usuarioCreador="admin"
                )
                
                response = stub.CrearDonacion(request)
                if response.exitoso:
                    created_items[categoria].append(response.donacion.id)
                    print(f"  ✓ {item['descripcion']}: {item['cantidad']} unidades")
                else:
                    print(f"  ✗ Error: {response.mensaje}")
        
        # 2. Consultar inventario por categoría
        print("\n=== Consultando Inventario por Categoría ===")
        
        for categoria in ["ALIMENTOS", "ROPA", "UTILES_ESCOLARES", "JUGUETES"]:
            print(f"\n--- Categoría: {categoria} ---")
            
            request = ListarDonacionesRequest(
                pagina=1,
                tamanoPagina=50,
                categoria=categoria,
                incluirEliminados=False
            )
            
            response = stub.ListarDonaciones(request)
            if response.exitoso:
                print(f"Total items en {categoria}: {response.total}")
                total_cantidad = 0
                
                for donacion in response.donaciones:
                    print(f"  - {donacion.descripcion}: {donacion.cantidad} unidades")
                    total_cantidad += donacion.cantidad
                
                print(f"  Total unidades en {categoria}: {total_cantidad}")
            else:
                print(f"Error consultando {categoria}: {response.mensaje}")
        
        # 3. Resumen general del inventario
        print("\n=== Resumen General del Inventario ===")
        
        request = ListarDonacionesRequest(
            pagina=1,
            tamanoPagina=1000,  # Obtener todos los items
            incluirEliminados=False
        )
        
        response = stub.ListarDonaciones(request)
        if response.exitoso:
            # Agrupar por categoría
            resumen = {}
            for donacion in response.donaciones:
                categoria = donacion.categoria
                if categoria not in resumen:
                    resumen[categoria] = {"items": 0, "total_unidades": 0}
                
                resumen[categoria]["items"] += 1
                resumen[categoria]["total_unidades"] += donacion.cantidad
            
            print(f"Total de donaciones en inventario: {response.total}")
            print("\nDesglose por categoría:")
            
            for categoria, datos in resumen.items():
                print(f"  {categoria}:")
                print(f"    - Tipos de items: {datos['items']}")
                print(f"    - Total unidades: {datos['total_unidades']}")
        
        # 4. Simular distribución de alimentos
        if "ALIMENTOS" in created_items and created_items["ALIMENTOS"]:
            print("\n=== Simulando Distribución de Alimentos ===")
            
            for donacion_id in created_items["ALIMENTOS"][:2]:  # Primeros 2 items
                # Obtener info actual
                get_request = ObtenerDonacionRequest(id=donacion_id)
                get_response = stub.ObtenerDonacion(get_request)
                
                if get_response.exitoso:
                    donacion = get_response.donacion
                    cantidad_distribuir = min(10, donacion.cantidad)  # Distribuir hasta 10 unidades
                    
                    print(f"\nDistribuyendo {cantidad_distribuir} unidades de: {donacion.descripcion}")
                    
                    update_request = ActualizarStockRequest(
                        donacionId=donacion_id,
                        cantidadCambio=-cantidad_distribuir,
                        usuarioModificacion="coordinador",
                        motivo=f"Distribución en evento solidario - {donacion.descripcion}"
                    )
                    
                    update_response = stub.ActualizarStock(update_request)
                    if update_response.exitoso:
                        print(f"  ✓ Stock actualizado: {donacion.cantidad} → {update_response.stockActual}")
                    else:
                        print(f"  ✗ Error: {update_response.mensaje}")
        
    except grpc.RpcError as e:
        print(f"Error gRPC: {e.code()} - {e.details()}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        channel.close()

if __name__ == "__main__":
    demo_category_management()
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
```

2. **Iniciar el servidor:**
```bash
python src/main.py
```

3. **Ejecutar pruebas:**
```bash
# Pruebas básicas
python demo_basic_functionality.py

# Pruebas de stock
python demo_stock_control.py

# Pruebas por categoría
python demo_category_management.py
```

## Estructura del Proyecto

```
inventory-service/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── database.py          # Configuración de base de datos
│   ├── models/
│   │   ├── __init__.py
│   │   └── donacion.py          # Modelo de datos Donacion
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── donacion_repository.py # Acceso a datos
│   ├── service/
│   │   ├── __init__.py
│   │   ├── inventario_service.py # Implementación gRPC
│   │   └── server.py            # Servidor gRPC
│   ├── __init__.py
│   ├── inventory_pb2.py         # Generado desde proto
│   ├── inventory_pb2_grpc.py    # Generado desde proto
│   └── main.py                  # Punto de entrada
├── tests/
│   ├── __init__.py
│   └── test_donacion_model.py   # Pruebas unitarias
├── .env.example                 # Ejemplo de variables de entorno
├── demo_inventario.py           # Script de demostración
├── Dockerfile                   # Imagen Docker
├── requirements.txt             # Dependencias Python
└── README.md                    # Este archivo
```

## Validaciones de Negocio

### Donaciones
- **Categoría**: Debe ser una de las categorías válidas
- **Descripción**: Requerida, mínimo 3 caracteres
- **Cantidad**: No puede ser negativa
- **Eliminación**: Solo baja lógica, no eliminación física

### Stock
- **Actualización**: No permite cantidades negativas resultantes
- **Auditoría**: Todos los cambios se registran con motivo y usuario
- **Validación**: Verifica disponibilidad antes de operaciones

## Integración con Otros Servicios

### API Gateway
El API Gateway se conecta a este servicio para exponer endpoints REST que internamente llaman a los métodos gRPC.

### Red de ONGs (Kafka)
El servicio se integrará con Kafka para:
- Recibir transferencias de donaciones de otras ONGs
- Enviar confirmaciones de transferencias
- Sincronizar inventarios entre organizaciones

## Monitoreo y Logs

El servicio registra:
- Conexiones y desconexiones de clientes
- Errores de validación y base de datos
- Cambios de stock con auditoría completa
- Métricas de rendimiento de operaciones

## Troubleshooting

### Problemas Comunes

1. **Error de conexión a base de datos**
   - Verifica que MySQL esté ejecutándose
   - Confirma las credenciales en `.env`
   - Asegúrate de que la base de datos `ong_sistema` exista

2. **Puerto en uso**
   - Cambia `GRPC_PORT` en `.env`
   - Verifica que no haya otro servicio usando el puerto 50052

3. **Errores de validación**
   - Revisa que las categorías sean válidas
   - Confirma que las descripciones tengan al menos 3 caracteres
   - Verifica que las cantidades no sean negativas

## Contribución

Para contribuir al desarrollo:

1. Sigue las convenciones de código Python (PEP 8)
2. Agrega pruebas unitarias para nuevas funcionalidades
3. Actualiza la documentación según sea necesario
4. Asegúrate de que todas las pruebas pasen antes de enviar cambios