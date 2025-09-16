#!/usr/bin/env python3
"""
Demo script for Stock Control functionality
This script demonstrates stock validation and update operations
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.donacion import Donacion

def demo_stock_scenarios():
    """Demo various stock control scenarios"""
    print("=== Demo: Escenarios de Control de Stock ===")
    
    # Scenario 1: Donation received (stock increase)
    print("\n1. Escenario: Recepción de Donación")
    print("   - Donación actual: 15 unidades de ALIMENTOS")
    print("   - Recibimos: +10 unidades")
    print("   - Stock final esperado: 25 unidades")
    print("   - Motivo: 'Donación recibida de ONG Hermanos Unidos'")
    print("   - Usuario: 'vocal1'")
    
    # Scenario 2: Transfer to another NGO (stock decrease)
    print("\n2. Escenario: Transferencia a otra ONG")
    print("   - Donación actual: 25 unidades de ALIMENTOS")
    print("   - Transferimos: -8 unidades")
    print("   - Stock final esperado: 17 unidades")
    print("   - Motivo: 'Transferencia a ONG Corazón Solidario'")
    print("   - Usuario: 'presidente'")
    
    # Scenario 3: Insufficient stock (should fail)
    print("\n3. Escenario: Stock Insuficiente")
    print("   - Donación actual: 5 unidades de ROPA")
    print("   - Intentamos transferir: -10 unidades")
    print("   - Resultado esperado: ERROR - Stock insuficiente")
    
    # Scenario 4: Stock validation before operation
    print("\n4. Escenario: Validación de Stock")
    print("   - Donación: 20 unidades de JUGUETES")
    print("   - Cantidad requerida: 15 unidades")
    print("   - Resultado esperado: Stock suficiente")
    
    print("\n5. Escenario: Validación de Stock Insuficiente")
    print("   - Donación: 8 unidades de UTILES_ESCOLARES")
    print("   - Cantidad requerida: 12 unidades")
    print("   - Resultado esperado: Stock insuficiente")

def demo_validation_rules():
    """Demo stock validation rules"""
    print("\n=== Demo: Reglas de Validación de Stock ===")
    
    validation_cases = [
        {
            'description': 'Cantidad negativa en donación',
            'donacion': Donacion(categoria="ROPA", descripcion="Camisetas", cantidad=-5, usuario_alta="admin"),
            'expected': 'ERROR - Cantidad no puede ser negativa'
        },
        {
            'description': 'Cantidad cero (válida)',
            'donacion': Donacion(categoria="ALIMENTOS", descripcion="Conservas", cantidad=0, usuario_alta="admin"),
            'expected': 'VÁLIDO - Cantidad cero permitida'
        },
        {
            'description': 'Cantidad positiva',
            'donacion': Donacion(categoria="JUGUETES", descripcion="Pelotas", cantidad=15, usuario_alta="admin"),
            'expected': 'VÁLIDO - Cantidad positiva'
        }
    ]
    
    for i, case in enumerate(validation_cases, 1):
        print(f"\n{i}. {case['description']}")
        donacion = case['donacion']
        errors = donacion.validate()
        
        if errors:
            print(f"   Resultado: ERROR - {', '.join(errors)}")
        else:
            print(f"   Resultado: VÁLIDO")
        
        print(f"   Esperado: {case['expected']}")

def demo_audit_trail():
    """Demo audit trail for stock changes"""
    print("\n=== Demo: Auditoría de Cambios de Stock ===")
    
    audit_examples = [
        {
            'operation': 'Incremento de Stock',
            'donacion_id': 1,
            'cantidad_anterior': 20,
            'cantidad_cambio': +5,
            'cantidad_nueva': 25,
            'motivo': 'Donación recibida de empresa local',
            'usuario': 'vocal1'
        },
        {
            'operation': 'Decremento de Stock',
            'donacion_id': 2,
            'cantidad_anterior': 15,
            'cantidad_cambio': -8,
            'cantidad_nueva': 7,
            'motivo': 'Transferencia a ONG Solidaria',
            'usuario': 'presidente'
        },
        {
            'operation': 'Corrección de Inventario',
            'donacion_id': 3,
            'cantidad_anterior': 12,
            'cantidad_cambio': +3,
            'cantidad_nueva': 15,
            'motivo': 'Corrección por error de conteo',
            'usuario': 'vocal2'
        }
    ]
    
    print("\nEjemplos de registros de auditoría que se crearían:")
    print("-" * 80)
    print(f"{'ID':<3} {'Operación':<20} {'Ant.':<4} {'Cambio':<7} {'Nueva':<5} {'Usuario':<12} {'Motivo':<25}")
    print("-" * 80)
    
    for audit in audit_examples:
        print(f"{audit['donacion_id']:<3} {audit['operation']:<20} {audit['cantidad_anterior']:<4} "
              f"{audit['cantidad_cambio']:+7} {audit['cantidad_nueva']:<5} {audit['usuario']:<12} "
              f"{audit['motivo'][:25]:<25}")

def demo_business_rules():
    """Demo business rules for stock control"""
    print("\n=== Demo: Reglas de Negocio ===")
    
    rules = [
        {
            'rule': 'No se permite stock negativo',
            'example': 'Stock actual: 5, Cambio: -10',
            'result': 'RECHAZADO - Stock resultante sería -5'
        },
        {
            'rule': 'Cambio de stock cero no permitido',
            'example': 'Stock actual: 10, Cambio: 0',
            'result': 'RECHAZADO - El cambio debe ser diferente de cero'
        },
        {
            'rule': 'Motivo requerido para cambios',
            'example': 'Cambio: +5, Motivo: vacío',
            'result': 'RECHAZADO - Motivo es requerido para auditoría'
        },
        {
            'rule': 'Usuario requerido para cambios',
            'example': 'Cambio: -3, Usuario: vacío',
            'result': 'RECHAZADO - Usuario es requerido para auditoría'
        },
        {
            'rule': 'Validación antes de transferencia',
            'example': 'Transferir 8 de 20 disponibles',
            'result': 'APROBADO - Stock suficiente'
        }
    ]
    
    for i, rule in enumerate(rules, 1):
        print(f"\n{i}. {rule['rule']}")
        print(f"   Ejemplo: {rule['example']}")
        print(f"   Resultado: {rule['result']}")

def demo_integration_flow():
    """Demo complete integration flow"""
    print("\n=== Demo: Flujo de Integración Completo ===")
    
    print("\nFlujo típico de transferencia entre ONGs:")
    print("1. ONG A recibe solicitud de transferencia de ONG B")
    print("2. ONG A valida que tiene stock suficiente")
    print("3. Si hay stock, ONG A actualiza su inventario (decremento)")
    print("4. ONG A envía confirmación a ONG B vía Kafka")
    print("5. ONG B recibe confirmación y actualiza su inventario (incremento)")
    print("6. Ambas ONGs registran la operación en auditoría")
    
    print("\nEjemplo práctico:")
    print("- ONG Empuje Comunitario tiene 20 unidades de 'Arroz 1kg'")
    print("- ONG Corazón Solidario solicita 8 unidades")
    print("- Validación: ¿20 >= 8? SÍ")
    print("- ONG Empuje: Stock 20 → 12 (motivo: 'Transferencia a ONG Corazón Solidario')")
    print("- ONG Corazón: Stock 5 → 13 (motivo: 'Recibido de ONG Empuje Comunitario')")
    print("- Auditoría registrada en ambas organizaciones")

def main():
    """Main demo function"""
    print("🎯 Demo del Control de Stock - Servicio de Inventario")
    print("=" * 60)
    
    try:
        demo_stock_scenarios()
        demo_validation_rules()
        demo_audit_trail()
        demo_business_rules()
        demo_integration_flow()
        
        print("\n" + "=" * 60)
        print("✅ Demo de Control de Stock completado exitosamente")
        print("\nFuncionalidades implementadas:")
        print("• ✅ Actualización de stock (incremento/decremento)")
        print("• ✅ Validación de stock antes de operaciones")
        print("• ✅ Prevención de cantidades negativas")
        print("• ✅ Auditoría completa de cambios")
        print("• ✅ Validaciones de entrada robustas")
        print("• ✅ Manejo de errores descriptivo")
        
        print("\nPara probar con gRPC:")
        print("1. Inicia el servidor: python src/main.py")
        print("2. Usa un cliente gRPC para llamar:")
        print("   - ActualizarStock(donacionId, cantidadCambio, usuario, motivo)")
        print("   - ValidarStock(donacionId, cantidadRequerida)")
        
    except Exception as e:
        print(f"\n❌ Error en demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()