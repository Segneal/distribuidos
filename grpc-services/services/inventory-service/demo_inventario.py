#!/usr/bin/env python3
"""
Demo script for Inventory Service
This script demonstrates the basic functionality of the inventory service
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.donacion import Donacion, CategoriaEnum

def demo_donacion_model():
    """Demo the Donacion model functionality"""
    print("=== Demo: Modelo Donacion ===")
    
    # Create a valid donation
    print("\n1. Creando donación válida...")
    donacion = Donacion(
        categoria="ALIMENTOS",
        descripcion="Puré de tomates en lata",
        cantidad=24,
        usuario_alta="admin"
    )
    
    print(f"Donación creada: {donacion}")
    print(f"¿Es válida? {donacion.is_valid()}")
    
    # Test validation errors
    print("\n2. Probando validaciones...")
    donacion_invalida = Donacion(
        categoria="CATEGORIA_INVALIDA",
        descripcion="AB",  # Too short
        cantidad=-5,  # Negative
        usuario_alta="admin"
    )
    
    errors = donacion_invalida.validate()
    print(f"Errores de validación: {errors}")
    
    # Test all valid categories
    print("\n3. Probando todas las categorías válidas...")
    for categoria in CategoriaEnum:
        test_donacion = Donacion(
            categoria=categoria.value,
            descripcion=f"Item de {categoria.value.lower()}",
            cantidad=10,
            usuario_alta="admin"
        )
        print(f"  {categoria.value}: {'✓' if test_donacion.is_valid() else '✗'}")
    
    # Test dictionary conversion
    print("\n4. Probando conversión a diccionario...")
    dict_data = donacion.to_dict()
    print(f"Diccionario: {dict_data}")
    
    # Test creation from dictionary
    print("\n5. Probando creación desde diccionario...")
    donacion_from_dict = Donacion.from_dict(dict_data)
    print(f"Donación desde dict: {donacion_from_dict}")
    print(f"¿Son iguales? {donacion.categoria == donacion_from_dict.categoria and donacion.descripcion == donacion_from_dict.descripcion}")

def demo_database_config():
    """Demo database configuration"""
    print("\n=== Demo: Configuración de Base de Datos ===")
    
    try:
        from config.database import get_db_config
        
        print("Obteniendo configuración de base de datos...")
        db_config = get_db_config()
        
        print(f"Host: {db_config.host}")
        print(f"Puerto: {db_config.port}")
        print(f"Base de datos: {db_config.database}")
        print(f"Usuario: {db_config.user}")
        print(f"Pool name: {db_config.pool_name}")
        print(f"Pool size: {db_config.pool_size}")
        
        # Note: We won't test actual connection here as it requires MySQL to be running
        print("\nNota: Para probar la conexión real, asegúrate de que MySQL esté ejecutándose")
        
    except Exception as e:
        print(f"Error al configurar base de datos: {e}")
        print("Esto es normal si MySQL no está ejecutándose")

def main():
    """Main demo function"""
    print("🚀 Demo del Servicio de Inventario")
    print("=" * 50)
    
    try:
        demo_donacion_model()
        demo_database_config()
        
        print("\n" + "=" * 50)
        print("✅ Demo completado exitosamente")
        print("\nPara probar el servicio completo:")
        print("1. Asegúrate de que MySQL esté ejecutándose")
        print("2. Ejecuta: python src/main.py")
        print("3. El servidor gRPC estará disponible en puerto 50052")
        
    except Exception as e:
        print(f"\n❌ Error en demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()