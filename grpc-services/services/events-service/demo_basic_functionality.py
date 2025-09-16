"""
Demo script for Events Service basic functionality
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
from config.database import db_config

def test_database_connection():
    """Test database connection"""
    print("=== Prueba de Conexión a Base de Datos ===")
    
    try:
        if db_config.test_connection():
            print("✓ Conexión a base de datos exitosa")
            return True
        else:
            print("✗ Error en conexión a base de datos")
            return False
    except Exception as e:
        print(f"✗ Error en conexión: {e}")
        return False

def test_event_model():
    """Test event model functionality"""
    print("\n=== Prueba de Modelo de Evento ===")
    
    # Create future event
    fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    
    evento = Evento(
        nombre="Evento de Prueba",
        descripcion="Este es un evento de prueba para validar funcionalidad",
        fecha_hora=fecha_futura,
        usuario_alta="admin_demo"
    )
    
    print(f"Evento creado: {evento}")
    
    # Test validation
    errores = evento.validar_datos_basicos()
    if errores:
        print(f"✗ Errores de validación: {errores}")
        return False
    else:
        print("✓ Validación de datos básicos exitosa")
    
    # Test business rules
    print(f"¿Es evento futuro? {evento.es_evento_futuro()}")
    print(f"¿Puede modificar datos básicos? {evento.puede_modificar_datos_basicos()}")
    print(f"¿Puede registrar donaciones? {evento.puede_registrar_donaciones()}")
    print(f"¿Puede eliminar? {evento.puede_eliminar()}")
    
    # Test participants
    evento.agregar_participante(1)
    evento.agregar_participante(2)
    print(f"Participantes agregados: {evento.participantes_ids}")
    
    evento.quitar_participante(1)
    print(f"Participantes después de quitar uno: {evento.participantes_ids}")
    
    return True

def test_distributed_donation_model():
    """Test distributed donation model"""
    print("\n=== Prueba de Modelo de Donación Repartida ===")
    
    donacion = DonacionRepartida(
        donacion_id=1,
        cantidad_repartida=10,
        usuario_registro="admin_demo"
    )
    
    print(f"Donación repartida creada: {donacion.to_dict()}")
    
    # Test conversion
    donacion_dict = donacion.to_dict()
    donacion_from_dict = DonacionRepartida.from_dict(donacion_dict)
    
    print(f"Conversión exitosa: {donacion_from_dict.donacion_id == donacion.donacion_id}")
    
    return True

def test_participant_model():
    """Test participant model"""
    print("\n=== Prueba de Modelo de Participante ===")
    
    participante = Participante(
        usuario_id=1,
        nombre_usuario="admin",
        nombre="Administrador",
        apellido="Sistema",
        rol="PRESIDENTE"
    )
    
    print(f"Participante creado: {participante}")
    
    # Test conversion
    participante_dict = participante.to_dict()
    participante_from_dict = Participante.from_dict(participante_dict)
    
    print(f"Conversión exitosa: {participante_from_dict.usuario_id == participante.usuario_id}")
    
    return True

def test_event_validation_errors():
    """Test event validation with errors"""
    print("\n=== Prueba de Validación con Errores ===")
    
    # Test with invalid data
    evento_invalido = Evento(
        nombre="",  # Empty name
        descripcion="A" * 1001,  # Too long description
        fecha_hora="fecha-invalida",  # Invalid date format
        usuario_alta="admin"
    )
    
    errores = evento_invalido.validar_datos_basicos()
    print(f"Errores encontrados ({len(errores)}):")
    for i, error in enumerate(errores, 1):
        print(f"  {i}. {error}")
    
    return len(errores) > 0

def main():
    """Main demo function"""
    print("=== DEMO: Servicio de Eventos - Funcionalidad Básica ===")
    print(f"Fecha/Hora: {datetime.now()}")
    print("=" * 60)
    
    # Test database connection
    if not test_database_connection():
        print("\n⚠️  Advertencia: No se pudo conectar a la base de datos")
        print("   Continuando con pruebas de modelos...")
    
    # Test models
    success = True
    
    success &= test_event_model()
    success &= test_distributed_donation_model()
    success &= test_participant_model()
    success &= test_event_validation_errors()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ Todas las pruebas de funcionalidad básica completadas exitosamente")
    else:
        print("✗ Algunas pruebas fallaron")
    
    print("=" * 60)

if __name__ == '__main__':
    main()