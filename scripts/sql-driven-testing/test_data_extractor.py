#!/usr/bin/env python3
"""
Test script for SQL Data Extractor
Sistema ONG - SQL Driven Testing

This script tests the data extractor functionality without requiring
a live database connection.
"""

import sys
import os
import json
from unittest.mock import Mock, MagicMock
from data_extractor import SQLDataExtractor, DatabaseConfig

def create_mock_extractor():
    """Create a mock data extractor for testing"""
    db_config = DatabaseConfig(
        host='localhost',
        port=3306,
        database='ong_sistema',
        user='test_user',
        password='test_password'
    )
    
    extractor = SQLDataExtractor(db_config)
    
    # Mock the database connection
    extractor.connection = Mock()
    extractor.connection.is_connected.return_value = True
    
    return extractor

def test_users_extraction():
    """Test user data extraction logic"""
    print("Testing user data extraction...")
    
    extractor = create_mock_extractor()
    
    # Mock cursor and data
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [
        {
            'id': 1,
            'nombre_usuario': 'test_presidente',
            'nombre': 'Juan Carlos',
            'apellido': 'Presidente Test',
            'email': 'presidente@test.com',
            'rol': 'PRESIDENTE',
            'activo': True,
            'telefono': '1111111111',
            'fecha_hora_alta': None,
            'usuario_alta': 'system',
            'password_plain': 'test123'
        },
        {
            'id': 2,
            'nombre_usuario': 'test_vocal',
            'nombre': 'María Elena',
            'apellido': 'Vocal Test',
            'email': 'vocal@test.com',
            'rol': 'VOCAL',
            'activo': True,
            'telefono': '2222222222',
            'fecha_hora_alta': None,
            'usuario_alta': 'test_presidente',
            'password_plain': 'test123'
        }
    ]
    
    extractor.connection.cursor.return_value = mock_cursor
    
    # Test extraction
    users = extractor.extract_users_by_role()
    
    # Verify results
    assert 'PRESIDENTE' in users
    assert 'VOCAL' in users
    assert len(users['PRESIDENTE']) == 1
    assert len(users['VOCAL']) == 1
    assert users['PRESIDENTE'][0]['nombre_usuario'] == 'test_presidente'
    assert users['VOCAL'][0]['nombre_usuario'] == 'test_vocal'
    
    print("✓ User extraction test passed")

def test_inventory_extraction():
    """Test inventory data extraction logic"""
    print("Testing inventory data extraction...")
    
    extractor = create_mock_extractor()
    
    # Mock cursor and data
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [
        {
            'id': 101,
            'categoria': 'ALIMENTOS',
            'descripcion': 'Arroz integral 1kg - Stock Alto',
            'cantidad': 100,
            'eliminado': False,
            'fecha_hora_alta': None,
            'usuario_alta': 'test_vocal',
            'fecha_hora_modificacion': None,
            'usuario_modificacion': None
        },
        {
            'id': 102,
            'categoria': 'ALIMENTOS',
            'descripcion': 'Aceite - Stock Bajo',
            'cantidad': 5,
            'eliminado': False,
            'fecha_hora_alta': None,
            'usuario_alta': 'test_vocal',
            'fecha_hora_modificacion': None,
            'usuario_modificacion': None
        },
        {
            'id': 103,
            'categoria': 'ROPA',
            'descripcion': 'Camisetas - Stock Cero',
            'cantidad': 0,
            'eliminado': False,
            'fecha_hora_alta': None,
            'usuario_alta': 'test_vocal',
            'fecha_hora_modificacion': None,
            'usuario_modificacion': None
        }
    ]
    
    extractor.connection.cursor.return_value = mock_cursor
    
    # Test extraction
    inventory = extractor.extract_inventory_by_category()
    
    # Verify results
    assert 'ALIMENTOS' in inventory
    assert 'ROPA' in inventory
    assert len(inventory['ALIMENTOS']['high_stock']) == 1
    assert len(inventory['ALIMENTOS']['low_stock']) == 1
    assert len(inventory['ROPA']['zero_stock']) == 1
    assert inventory['ALIMENTOS']['high_stock'][0]['cantidad'] == 100
    assert inventory['ALIMENTOS']['low_stock'][0]['cantidad'] == 5
    assert inventory['ROPA']['zero_stock'][0]['cantidad'] == 0
    
    print("✓ Inventory extraction test passed")

def test_test_mappings_extraction():
    """Test test case mappings extraction"""
    print("Testing test case mappings extraction...")
    
    extractor = create_mock_extractor()
    
    # Mock cursor and data
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [
        {
            'endpoint': '/api/auth/login',
            'method': 'POST',
            'test_type': 'success',
            'user_id': 1,
            'resource_id': None,
            'description': 'Login exitoso - Presidente',
            'expected_status': 200,
            'request_body': '{"nombreUsuario":"test_presidente","clave":"test123"}',
            'expected_response_fields': '["token","usuario","rol"]',
            'test_category': 'authentication'
        },
        {
            'endpoint': '/api/usuarios',
            'method': 'GET',
            'test_type': 'authorization',
            'user_id': 4,
            'resource_id': None,
            'description': 'Listar usuarios - Sin permisos',
            'expected_status': 403,
            'request_body': None,
            'expected_response_fields': '["error","message"]',
            'test_category': 'users'
        }
    ]
    
    extractor.connection.cursor.return_value = mock_cursor
    
    # Test extraction
    mappings = extractor.extract_test_case_mappings()
    
    # Verify results
    assert len(mappings) == 2
    assert mappings[0]['endpoint'] == '/api/auth/login'
    assert mappings[0]['test_category'] == 'authentication'
    assert isinstance(mappings[0]['request_body'], dict)
    assert isinstance(mappings[0]['expected_response_fields'], list)
    assert mappings[1]['test_category'] == 'users'
    
    print("✓ Test mappings extraction test passed")

def test_data_integrity_validation():
    """Test data integrity validation"""
    print("Testing data integrity validation...")
    
    extractor = create_mock_extractor()
    
    # Test with valid data
    valid_data = {
        'users': {
            'PRESIDENTE': [{'id': 1, 'nombre_usuario': 'test_presidente'}],
            'VOCAL': [{'id': 2, 'nombre_usuario': 'test_vocal'}],
            'COORDINADOR': [{'id': 3, 'nombre_usuario': 'test_coordinador'}],
            'VOLUNTARIO': [{'id': 4, 'nombre_usuario': 'test_voluntario'}]
        },
        'inventory': {
            'ALIMENTOS': {'all': [{'id': 101}]},
            'ROPA': {'all': [{'id': 102}]},
            'JUGUETES': {'all': [{'id': 103}]},
            'UTILES_ESCOLARES': {'all': [{'id': 104}]}
        },
        'events': {
            'all': [{'id': 201, 'participantes': [1, 2]}]
        },
        'test_mappings': [
            {'test_category': 'authentication', 'user_id': 1, 'resource_id': None},
            {'test_category': 'users', 'user_id': 2, 'resource_id': None},
            {'test_category': 'inventory', 'user_id': 2, 'resource_id': 101},
            {'test_category': 'events', 'user_id': 3, 'resource_id': 201},
            {'test_category': 'network', 'user_id': 2, 'resource_id': None}
        ]
    }
    
    # Should not raise any exception
    extractor.validate_data_integrity(valid_data)
    
    print("✓ Data integrity validation test passed")

def test_utility_methods():
    """Test utility methods"""
    print("Testing utility methods...")
    
    extractor = create_mock_extractor()
    
    # Mock the extract methods to return test data
    extractor.extract_users_by_role = Mock(return_value={
        'PRESIDENTE': [{'id': 1, 'nombre_usuario': 'test_presidente'}]
    })
    
    extractor.extract_inventory_by_category = Mock(return_value={
        'ALIMENTOS': {'all': [{'id': 101, 'descripcion': 'Test donation'}]}
    })
    
    extractor.extract_test_case_mappings = Mock(return_value=[
        {'test_category': 'authentication', 'endpoint': '/api/auth/login'},
        {'test_category': 'users', 'endpoint': '/api/usuarios'}
    ])
    
    # Test utility methods
    user = extractor.get_user_by_id(1)
    assert user is not None
    assert user['id'] == 1
    
    donation = extractor.get_donation_by_id(101)
    assert donation is not None
    assert donation['id'] == 101
    
    auth_cases = extractor.get_test_cases_by_category('authentication')
    assert len(auth_cases) == 1
    assert auth_cases[0]['test_category'] == 'authentication'
    
    login_cases = extractor.get_test_cases_by_endpoint('/api/auth/login')
    assert len(login_cases) == 1
    assert login_cases[0]['endpoint'] == '/api/auth/login'
    
    print("✓ Utility methods test passed")

def main():
    """Run all tests"""
    print("=== SQL Data Extractor Tests ===\n")
    
    try:
        test_users_extraction()
        test_inventory_extraction()
        test_test_mappings_extraction()
        test_data_integrity_validation()
        test_utility_methods()
        
        print("\n✅ All tests passed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())