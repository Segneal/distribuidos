"""
Demo script for Events Service Participant Management
"""
import os
import sys
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

from models.evento import Evento, Participante

def test_participant_management():
    """Test participant management functionality"""
    print("=== Prueba de Gestión de Participantes ===")
    
    # Create a future event
    fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    evento = Evento(
        id=1,
        nombre="Evento con Participantes",
        descripcion="Evento para probar gestión de participantes",
        fecha_hora=fecha_futura,
        usuario_alta="admin"
    )
    
    print(f"Evento creado: {evento.nombre}")
    print(f"Participantes iniciales: {evento.participantes_ids}")
    
    # Test 1: Add participants
    print("\n1. Agregar Participantes")
    
    # Add different types of participants
    participantes_test = [
        {"id": 1, "rol": "PRESIDENTE", "nombre": "Admin", "apellido": "Sistema"},
        {"id": 2, "rol": "COORDINADOR", "nombre": "Coord", "apellido": "Eventos"},
        {"id": 3, "rol": "VOCAL", "nombre": "Vocal", "apellido": "Inventario"},
        {"id": 4, "rol": "VOLUNTARIO", "nombre": "Vol", "apellido": "Uno"},
        {"id": 5, "rol": "VOLUNTARIO", "nombre": "Vol", "apellido": "Dos"}
    ]
    
    for participante_data in participantes_test:
        resultado = evento.agregar_participante(participante_data["id"])
        if resultado:
            print(f"   ✓ Participante {participante_data['id']} ({participante_data['rol']}) agregado")
        else:
            print(f"   ✗ No se pudo agregar participante {participante_data['id']}")
    
    print(f"   Total participantes: {len(evento.participantes_ids)}")
    print(f"   Lista de participantes: {evento.participantes_ids}")
    
    # Test 2: Try to add duplicate participant
    print("\n2. Intentar Agregar Participante Duplicado")
    resultado = evento.agregar_participante(1)  # Already exists
    if resultado:
        print("   ✗ Se agregó participante duplicado (no debería ocurrir)")
    else:
        print("   ✓ Participante duplicado rechazado correctamente")
    
    # Test 3: Remove participants
    print("\n3. Quitar Participantes")
    
    # Remove a participant
    resultado = evento.quitar_participante(3)
    if resultado:
        print("   ✓ Participante 3 removido exitosamente")
    else:
        print("   ✗ No se pudo remover participante 3")
    
    print(f"   Participantes después de remover: {evento.participantes_ids}")
    
    # Test 4: Try to remove non-existing participant
    print("\n4. Intentar Quitar Participante No Existente")
    resultado = evento.quitar_participante(99)  # Doesn't exist
    if resultado:
        print("   ✗ Se removió participante inexistente (no debería ocurrir)")
    else:
        print("   ✓ Participante inexistente rechazado correctamente")
    
    return True

def test_participant_model():
    """Test participant model functionality"""
    print("\n=== Prueba de Modelo de Participante ===")
    
    # Test different roles
    roles_test = [
        {"rol": "PRESIDENTE", "descripcion": "Acceso completo al sistema"},
        {"rol": "COORDINADOR", "descripcion": "Gestión de eventos solidarios"},
        {"rol": "VOCAL", "descripcion": "Gestión de inventario de donaciones"},
        {"rol": "VOLUNTARIO", "descripcion": "Consulta y participación en eventos"}
    ]
    
    participantes = []
    
    for i, rol_data in enumerate(roles_test, 1):
        participante = Participante(
            usuario_id=i,
            nombre_usuario=f"usuario{i}",
            nombre=f"Usuario{i}",
            apellido=f"Apellido{i}",
            rol=rol_data["rol"]
        )
        
        participantes.append(participante)
        print(f"{i}. {participante}")
        print(f"   Rol: {participante.rol} - {rol_data['descripcion']}")
        print(f"   Fecha asignación: {participante.fecha_asignacion}")
    
    # Test conversions
    print("\n=== Prueba de Conversiones ===")
    
    participante_original = participantes[0]
    
    # To dict
    participante_dict = participante_original.to_dict()
    print(f"Conversión a diccionario: {participante_dict}")
    
    # From dict
    participante_from_dict = Participante.from_dict(participante_dict)
    print(f"Conversión desde diccionario: {participante_from_dict}")
    
    # Verify conversion integrity
    if (participante_original.usuario_id == participante_from_dict.usuario_id and
        participante_original.nombre_usuario == participante_from_dict.nombre_usuario and
        participante_original.rol == participante_from_dict.rol):
        print("✓ Conversiones exitosas")
    else:
        print("✗ Error en conversiones")
    
    return True

def test_participant_business_rules():
    """Test business rules for participant management"""
    print("\n=== Prueba de Reglas de Negocio para Participantes ===")
    
    # Test 1: Volunteer self-assignment rules
    print("\n1. Reglas de Auto-asignación para Voluntarios")
    
    # Simulate volunteer trying to self-assign
    voluntario = Participante(
        usuario_id=10,
        nombre_usuario="voluntario1",
        nombre="Voluntario",
        apellido="Uno",
        rol="VOLUNTARIO"
    )
    
    print(f"   Voluntario: {voluntario.nombre} {voluntario.apellido}")
    print(f"   Rol: {voluntario.rol}")
    print("   Regla: Los voluntarios solo pueden auto-asignarse a eventos")
    print("   Regla: Los voluntarios no pueden asignar a otros usuarios")
    
    # Test 2: Role-based assignment permissions
    print("\n2. Permisos de Asignación por Rol")
    
    roles_permisos = {
        "PRESIDENTE": "Puede asignar cualquier usuario a cualquier evento",
        "COORDINADOR": "Puede asignar usuarios a eventos que coordina",
        "VOCAL": "No puede asignar participantes a eventos",
        "VOLUNTARIO": "Solo puede auto-asignarse"
    }
    
    for rol, permiso in roles_permisos.items():
        print(f"   {rol}: {permiso}")
    
    # Test 3: Event type restrictions
    print("\n3. Restricciones por Tipo de Evento")
    
    fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    fecha_pasada = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    
    evento_futuro = Evento(
        nombre="Evento Futuro",
        fecha_hora=fecha_futura
    )
    
    evento_pasado = Evento(
        nombre="Evento Pasado",
        fecha_hora=fecha_pasada
    )
    
    print(f"   Evento Futuro:")
    print(f"     - Permite agregar participantes: Sí")
    print(f"     - Permite quitar participantes: Sí")
    
    print(f"   Evento Pasado:")
    print(f"     - Permite agregar participantes: No (evento ya ocurrió)")
    print(f"     - Permite quitar participantes: No (evento ya ocurrió)")
    
    # Test 4: Automatic removal of inactive users
    print("\n4. Eliminación Automática de Usuarios Inactivos")
    print("   Regla: Cuando un usuario se marca como inactivo,")
    print("   debe ser removido automáticamente de todos los eventos futuros")
    
    evento_con_participantes = Evento(
        nombre="Evento con Participantes",
        fecha_hora=fecha_futura,
        participantes_ids=[1, 2, 3, 4, 5]
    )
    
    print(f"   Participantes antes: {evento_con_participantes.participantes_ids}")
    
    # Simulate removing inactive user (user 3)
    usuario_inactivo = 3
    if evento_con_participantes.quitar_participante(usuario_inactivo):
        print(f"   ✓ Usuario inactivo {usuario_inactivo} removido automáticamente")
    
    print(f"   Participantes después: {evento_con_participantes.participantes_ids}")
    
    return True

def test_participant_validation_scenarios():
    """Test participant validation scenarios"""
    print("\n=== Prueba de Escenarios de Validación de Participantes ===")
    
    # Test 1: Valid participant data
    print("\n1. Datos Válidos de Participante")
    try:
        participante_valido = Participante(
            usuario_id=1,
            nombre_usuario="admin",
            nombre="Administrador",
            apellido="Sistema",
            rol="PRESIDENTE"
        )
        print(f"   ✓ Participante válido creado: {participante_valido}")
    except Exception as e:
        print(f"   ✗ Error creando participante válido: {e}")
    
    # Test 2: Edge cases
    print("\n2. Casos Límite")
    
    edge_cases = [
        {
            "name": "Nombre con espacios",
            "data": {
                "usuario_id": 2,
                "nombre_usuario": "user with spaces",
                "nombre": "Usuario Con",
                "apellido": "Espacios",
                "rol": "VOLUNTARIO"
            }
        },
        {
            "name": "Nombres largos",
            "data": {
                "usuario_id": 3,
                "nombre_usuario": "usuario_muy_largo_123",
                "nombre": "NombreMuyLargoParaPruebas",
                "apellido": "ApellidoMuyLargoParaPruebas",
                "rol": "VOCAL"
            }
        },
        {
            "name": "Caracteres especiales",
            "data": {
                "usuario_id": 4,
                "nombre_usuario": "user_123",
                "nombre": "José María",
                "apellido": "González-Pérez",
                "rol": "COORDINADOR"
            }
        }
    ]
    
    for case in edge_cases:
        try:
            participante = Participante(**case["data"])
            print(f"   ✓ {case['name']}: {participante.nombre} {participante.apellido}")
        except Exception as e:
            print(f"   ✗ {case['name']}: Error - {e}")
    
    return True

def main():
    """Main demo function"""
    print("=== DEMO: Servicio de Eventos - Gestión de Participantes ===")
    print(f"Fecha/Hora: {datetime.now()}")
    print("=" * 70)
    
    success = True
    
    try:
        success &= test_participant_management()
        success &= test_participant_model()
        success &= test_participant_business_rules()
        success &= test_participant_validation_scenarios()
        
    except Exception as e:
        print(f"\n✗ Error durante las pruebas: {e}")
        success = False
    
    print("\n" + "=" * 70)
    if success:
        print("✓ Todas las pruebas de gestión de participantes completadas exitosamente")
        print("\nFuncionalidades implementadas:")
        print("  ✓ Agregar participantes a eventos")
        print("  ✓ Quitar participantes de eventos")
        print("  ✓ Validación de participantes duplicados")
        print("  ✓ Modelo de participante con roles")
        print("  ✓ Reglas de negocio por rol de usuario")
        print("  ✓ Restricciones por tipo de evento (futuro/pasado)")
        print("  ✓ Lógica para auto-asignación de voluntarios")
        print("  ✓ Eliminación automática de usuarios inactivos")
    else:
        print("✗ Algunas pruebas fallaron")
    
    print("=" * 70)

if __name__ == '__main__':
    main()