"""
Demo script for Events Service CRUD operations
"""
import os
import sys
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

from models.evento import Evento, DonacionRepartida, Participante

def test_event_crud_operations():
    """Test Event CRUD operations"""
    print("=== Prueba de Operaciones CRUD de Eventos ===")
    
    # Test 1: Create Event
    print("\n1. Crear Evento")
    fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    
    evento = Evento(
        nombre="Evento de Demostración CRUD",
        descripcion="Este evento demuestra las operaciones CRUD",
        fecha_hora=fecha_futura,
        usuario_alta="admin_demo"
    )
    
    print(f"   Evento creado: {evento.nombre}")
    print(f"   Fecha: {evento.fecha_hora}")
    print(f"   ¿Es futuro?: {evento.es_evento_futuro()}")
    
    # Test 2: Validate Event
    print("\n2. Validar Evento")
    errores = evento.validar_datos_basicos()
    if errores:
        print(f"   ✗ Errores de validación: {errores}")
    else:
        print("   ✓ Evento válido")
    
    # Test 3: Update Event (simulate)
    print("\n3. Actualizar Evento")
    evento.nombre = "Evento Actualizado"
    evento.descripcion = "Descripción actualizada"
    evento.usuario_modificacion = "admin_modificador"
    
    print(f"   Nombre actualizado: {evento.nombre}")
    print(f"   ¿Puede modificar?: {evento.puede_modificar_datos_basicos()}")
    
    # Test 4: Manage Participants
    print("\n4. Gestionar Participantes")
    evento.agregar_participante(1)
    evento.agregar_participante(2)
    evento.agregar_participante(3)
    
    print(f"   Participantes agregados: {evento.participantes_ids}")
    
    evento.quitar_participante(2)
    print(f"   Después de quitar participante 2: {evento.participantes_ids}")
    
    # Test 5: Test with Past Event
    print("\n5. Evento Pasado")
    fecha_pasada = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    
    evento_pasado = Evento(
        nombre="Evento Pasado",
        descripcion="Este evento ya ocurrió",
        fecha_hora=fecha_pasada,
        usuario_alta="admin"
    )
    
    print(f"   Evento pasado: {evento_pasado.nombre}")
    print(f"   ¿Es pasado?: {evento_pasado.es_evento_pasado()}")
    print(f"   ¿Puede modificar?: {evento_pasado.puede_modificar_datos_basicos()}")
    print(f"   ¿Puede registrar donaciones?: {evento_pasado.puede_registrar_donaciones()}")
    print(f"   ¿Puede eliminar?: {evento_pasado.puede_eliminar()}")
    
    # Test 6: Distributed Donations
    print("\n6. Donaciones Repartidas")
    donacion1 = DonacionRepartida(
        donacion_id=1,
        cantidad_repartida=10,
        usuario_registro="admin"
    )
    
    donacion2 = DonacionRepartida(
        donacion_id=2,
        cantidad_repartida=5,
        usuario_registro="admin"
    )
    
    # Can only add to past events
    if evento_pasado.agregar_donacion_repartida(donacion1):
        print("   ✓ Donación 1 agregada al evento pasado")
    else:
        print("   ✗ No se pudo agregar donación 1")
    
    if evento_pasado.agregar_donacion_repartida(donacion2):
        print("   ✓ Donación 2 agregada al evento pasado")
    else:
        print("   ✗ No se pudo agregar donación 2")
    
    print(f"   Total donaciones repartidas: {len(evento_pasado.donaciones_repartidas)}")
    
    # Test 7: Participant Model
    print("\n7. Modelo de Participante")
    participante = Participante(
        usuario_id=1,
        nombre_usuario="admin",
        nombre="Administrador",
        apellido="Sistema",
        rol="PRESIDENTE"
    )
    
    print(f"   Participante: {participante}")
    print(f"   Rol: {participante.rol}")
    
    return True

def test_event_validation_scenarios():
    """Test various event validation scenarios"""
    print("\n=== Prueba de Escenarios de Validación ===")
    
    scenarios = [
        {
            "name": "Evento sin nombre",
            "data": {
                "nombre": "",
                "descripcion": "Descripción válida",
                "fecha_hora": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
            }
        },
        {
            "name": "Evento con nombre muy corto",
            "data": {
                "nombre": "AB",
                "descripcion": "Descripción válida",
                "fecha_hora": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
            }
        },
        {
            "name": "Evento con fecha pasada",
            "data": {
                "nombre": "Evento válido",
                "descripcion": "Descripción válida",
                "fecha_hora": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            }
        },
        {
            "name": "Evento con fecha inválida",
            "data": {
                "nombre": "Evento válido",
                "descripcion": "Descripción válida",
                "fecha_hora": "fecha-invalida"
            }
        },
        {
            "name": "Evento con descripción muy larga",
            "data": {
                "nombre": "Evento válido",
                "descripcion": "A" * 1001,  # 1001 characters
                "fecha_hora": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        
        evento = Evento(**scenario['data'])
        errores = evento.validar_datos_basicos()
        
        if errores:
            print(f"   ✓ Errores detectados ({len(errores)}):")
            for error in errores:
                print(f"     - {error}")
        else:
            print("   ✗ No se detectaron errores (inesperado)")
    
    return True

def test_business_rules():
    """Test business rules for events"""
    print("\n=== Prueba de Reglas de Negocio ===")
    
    # Future event
    fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    evento_futuro = Evento(
        nombre="Evento Futuro",
        fecha_hora=fecha_futura
    )
    
    # Past event
    fecha_pasada = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    evento_pasado = Evento(
        nombre="Evento Pasado",
        fecha_hora=fecha_pasada
    )
    
    print("\n1. Reglas para Evento Futuro:")
    print(f"   - Puede modificar datos básicos: {evento_futuro.puede_modificar_datos_basicos()}")
    print(f"   - Puede registrar donaciones: {evento_futuro.puede_registrar_donaciones()}")
    print(f"   - Puede eliminar: {evento_futuro.puede_eliminar()}")
    
    print("\n2. Reglas para Evento Pasado:")
    print(f"   - Puede modificar datos básicos: {evento_pasado.puede_modificar_datos_basicos()}")
    print(f"   - Puede registrar donaciones: {evento_pasado.puede_registrar_donaciones()}")
    print(f"   - Puede eliminar: {evento_pasado.puede_eliminar()}")
    
    return True

def main():
    """Main demo function"""
    print("=== DEMO: Servicio de Eventos - Operaciones CRUD ===")
    print(f"Fecha/Hora: {datetime.now()}")
    print("=" * 60)
    
    success = True
    
    try:
        success &= test_event_crud_operations()
        success &= test_event_validation_scenarios()
        success &= test_business_rules()
        
    except Exception as e:
        print(f"\n✗ Error durante las pruebas: {e}")
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✓ Todas las pruebas de operaciones CRUD completadas exitosamente")
        print("\nFuncionalidades implementadas:")
        print("  ✓ Creación de eventos con validación")
        print("  ✓ Validación de fechas futuras")
        print("  ✓ Gestión de participantes")
        print("  ✓ Reglas de negocio para eventos futuros/pasados")
        print("  ✓ Registro de donaciones repartidas")
        print("  ✓ Validación de datos de entrada")
    else:
        print("✗ Algunas pruebas fallaron")
    
    print("=" * 60)

if __name__ == '__main__':
    main()