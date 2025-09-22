#!/usr/bin/env python3
"""
Test script for PostmanGenerator
Sistema ONG - SQL Driven Testing

This script tests the PostmanGenerator with sample data to ensure it works correctly.
"""

import json
import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from postman_generator import PostmanGenerator

def create_sample_test_data():
    """Create sample test data for testing the PostmanGenerator"""
    return {
        'users': {
            'PRESIDENTE': [{
                'id': 1,
                'nombre_usuario': 'test_presidente',
                'nombre': 'Juan',
                'apellido': 'Presidente',
                'email': 'presidente@test.com',
                'rol': 'PRESIDENTE',
                'activo': True,
                'telefono': '1111111111',
                'fecha_hora_alta': '2024-01-01T10:00:00',
                'usuario_alta': 'system',
                'password_plain': 'test123'
            }],
            'VOCAL': [{
                'id': 2,
                'nombre_usuario': 'test_vocal',
                'nombre': 'María',
                'apellido': 'Vocal',
                'email': 'vocal@test.com',
                'rol': 'VOCAL',
                'activo': True,
                'telefono': '2222222222',
                'fecha_hora_alta': '2024-01-01T10:00:00',
                'usuario_alta': 'test_presidente',
                'password_plain': 'test123'
            }],
            'COORDINADOR': [{
                'id': 3,
                'nombre_usuario': 'test_coordinador',
                'nombre': 'Carlos',
                'apellido': 'Coordinador',
                'email': 'coordinador@test.com',
                'rol': 'COORDINADOR',
                'activo': True,
                'telefono': '3333333333',
                'fecha_hora_alta': '2024-01-01T10:00:00',
                'usuario_alta': 'test_presidente',
                'password_plain': 'test123'
            }],
            'VOLUNTARIO': [{
                'id': 4,
                'nombre_usuario': 'test_voluntario',
                'nombre': 'Ana',
                'apellido': 'Voluntario',
                'email': 'voluntario@test.com',
                'rol': 'VOLUNTARIO',
                'activo': True,
                'telefono': '4444444444',
                'fecha_hora_alta': '2024-01-01T10:00:00',
                'usuario_alta': 'test_coordinador',
                'password_plain': 'test123'
            }]
        },
        'inventory': {
            'ALIMENTOS': {
                'high_stock': [{
                    'id': 101,
                    'categoria': 'ALIMENTOS',
                    'descripcion': 'Arroz 1kg - Test Stock Alto',
                    'cantidad': 100,
                    'eliminado': False,
                    'fecha_hora_alta': '2024-01-01T10:00:00',
                    'usuario_alta': 'test_vocal'
                }],
                'medium_stock': [{
                    'id': 102,
                    'categoria': 'ALIMENTOS',
                    'descripcion': 'Fideos 500g - Test Stock Medio',
                    'cantidad': 25,
                    'eliminado': False,
                    'fecha_hora_alta': '2024-01-01T10:00:00',
                    'usuario_alta': 'test_vocal'
                }],
                'low_stock': [{
                    'id': 103,
                    'categoria': 'ALIMENTOS',
                    'descripcion': 'Leche 1L - Test Stock Bajo',
                    'cantidad': 3,
                    'eliminado': False,
                    'fecha_hora_alta': '2024-01-01T10:00:00',
                    'usuario_alta': 'test_vocal'
                }],
                'zero_stock': [{
                    'id': 104,
                    'categoria': 'ALIMENTOS',
                    'descripcion': 'Azúcar - Test Stock Cero',
                    'cantidad': 0,
                    'eliminado': False,
                    'fecha_hora_alta': '2024-01-01T10:00:00',
                    'usuario_alta': 'test_vocal'
                }],
                'all': []  # Will be populated below
            },
            'ROPA': {
                'high_stock': [{
                    'id': 201,
                    'categoria': 'ROPA',
                    'descripcion': 'Camisetas M - Test Stock Alto',
                    'cantidad': 75,
                    'eliminado': False,
                    'fecha_hora_alta': '2024-01-01T10:00:00',
                    'usuario_alta': 'test_vocal'
                }],
                'medium_stock': [],
                'low_stock': [],
                'zero_stock': [],
                'all': []
            }
        },
        'events': {
            'future': [{
                'id': 301,
                'nombre': 'Evento Test Futuro',
                'descripcion': 'Evento para testing',
                'fecha_hora': '2024-12-31T15:00:00',
                'fecha_hora_alta': '2024-01-01T10:00:00',
                'usuario_alta': 'test_coordinador',
                'participantes': [3, 4],
                'total_participantes': 2
            }],
            'past': [{
                'id': 302,
                'nombre': 'Evento Test Pasado',
                'descripcion': 'Evento pasado para testing',
                'fecha_hora': '2023-12-01T15:00:00',
                'fecha_hora_alta': '2023-11-01T10:00:00',
                'usuario_alta': 'test_coordinador',
                'participantes': [4],
                'total_participantes': 1
            }],
            'current': [],
            'all': []  # Will be populated below
        },
        'network': {
            'external_requests': [{
                'id_organizacion': 'ong-corazon-solidario',
                'id_solicitud': 'sol-001',
                'categoria': 'ALIMENTOS',
                'descripcion': 'Arroz para familias',
                'activa': True,
                'fecha_recepcion': '2024-01-01T10:00:00'
            }],
            'external_offers': [{
                'id_organizacion': 'ong-manos-unidas',
                'id_oferta': 'of-001',
                'categoria': 'UTILES_ESCOLARES',
                'descripcion': 'Útiles escolares',
                'cantidad': 50,
                'fecha_recepcion': '2024-01-01T10:00:00'
            }],
            'external_events': [{
                'id_organizacion': 'ong-esperanza',
                'id_evento': 'ev-001',
                'nombre': 'Campaña de Invierno',
                'descripcion': 'Distribución de ropa',
                'fecha_hora': '2024-12-15T14:00:00',
                'activo': True,
                'fecha_recepcion': '2024-01-01T10:00:00'
            }],
            'own_requests': [],
            'own_offers': [],
            'transfers_sent': [],
            'transfers_received': [],
            'event_adhesions': []
        },
        'test_mappings': [
            {
                'endpoint': '/api/auth/login',
                'method': 'POST',
                'test_type': 'success',
                'test_category': 'authentication',
                'user_id': 1,
                'resource_id': None,
                'description': 'Login exitoso - Presidente',
                'expected_status': 200,
                'request_body': None,
                'expected_response_fields': None
            },
            {
                'endpoint': '/api/usuarios',
                'method': 'GET',
                'test_type': 'success',
                'test_category': 'users',
                'user_id': 1,
                'resource_id': None,
                'description': 'Listar usuarios - Presidente',
                'expected_status': 200,
                'request_body': None,
                'expected_response_fields': None
            }
        ]
    }

def populate_all_arrays(data):
    """Populate 'all' arrays with data from other categories"""
    # Populate inventory 'all' arrays
    for category, category_data in data['inventory'].items():
        all_donations = []
        for stock_level in ['high_stock', 'medium_stock', 'low_stock', 'zero_stock']:
            all_donations.extend(category_data[stock_level])
        category_data['all'] = all_donations
    
    # Populate events 'all' array
    all_events = []
    for status in ['future', 'past', 'current']:
        all_events.extend(data['events'][status])
    data['events']['all'] = all_events
    
    return data

def test_postman_generator():
    """Test the PostmanGenerator with sample data"""
    print("Testing PostmanGenerator...")
    
    # Create sample data
    sample_data = create_sample_test_data()
    sample_data = populate_all_arrays(sample_data)
    
    try:
        # Create generator
        generator = PostmanGenerator(sample_data)
        print("✓ PostmanGenerator created successfully")
        
        # Test individual collection generation
        print("\nTesting individual collection generation:")
        
        # Test auth collection
        auth_collection = generator.generate_auth_collection()
        print(f"✓ Auth collection generated with {len(auth_collection['item'])} requests")
        
        # Test users collection
        users_collection = generator.generate_users_collection()
        print(f"✓ Users collection generated with {len(users_collection['item'])} requests")
        
        # Test inventory collection
        inventory_collection = generator.generate_inventory_collection()
        print(f"✓ Inventory collection generated with {len(inventory_collection['item'])} requests")
        
        # Test events collection
        events_collection = generator.generate_events_collection()
        print(f"✓ Events collection generated with {len(events_collection['item'])} requests")
        
        # Test network collection
        network_collection = generator.generate_network_collection()
        print(f"✓ Network collection generated with {len(network_collection['item'])} requests")
        
        # Test validation scripts generation
        validation_scripts = generator.generate_test_validation_scripts()
        print(f"✓ Validation scripts generated for {len(validation_scripts)} scenarios")
        
        # Test summary generation
        summary = generator.generate_collection_summary()
        print(f"✓ Collection summary generated")
        
        print("\n=== Test Summary ===")
        print(f"Total collections: {summary['total_collections']}")
        print(f"Data sources: {len(sample_data)} categories")
        print(f"Users by role: {len(sample_data['users'])} roles")
        print(f"Inventory categories: {len(sample_data['inventory'])} categories")
        print(f"Test mappings: {len(sample_data['test_mappings'])} cases")
        
        print("\n✅ All tests passed! PostmanGenerator is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_postman_generator()
    sys.exit(0 if success else 1)