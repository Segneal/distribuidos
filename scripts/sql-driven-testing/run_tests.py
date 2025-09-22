#!/usr/bin/env python3
"""
Simple Test Runner Script
Sistema ONG - SQL Driven Testing

A simple script to run the validation and testing system.
This script provides an easy way to execute tests without complex setup.
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def run_unit_tests():
    """Run unit tests for individual components"""
    print("🧪 Running Unit Tests")
    print("=" * 50)
    
    test_results = {}
    
    # Test Data Extractor
    print("Testing Data Extractor...")
    try:
        from test_data_extractor import main as test_data_extractor
        result = test_data_extractor()
        test_results['data_extractor'] = result == 0
        print(f"  {'✅' if test_results['data_extractor'] else '❌'} Data Extractor")
    except Exception as e:
        test_results['data_extractor'] = False
        print(f"  ❌ Data Extractor: {e}")
    
    # Test Postman Generator
    print("Testing Postman Generator...")
    try:
        from test_postman_generator import test_postman_generator
        result = test_postman_generator()
        test_results['postman_generator'] = result
        print(f"  {'✅' if test_results['postman_generator'] else '❌'} Postman Generator")
    except Exception as e:
        test_results['postman_generator'] = False
        print(f"  ❌ Postman Generator: {e}")
    
    # Test Swagger Generator
    print("Testing Swagger Generator...")
    try:
        import unittest
        from test_swagger_generator import TestSwaggerGenerator
        
        # Run tests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestSwaggerGenerator)
        runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
        result = runner.run(suite)
        
        test_results['swagger_generator'] = result.wasSuccessful()
        print(f"  {'✅' if test_results['swagger_generator'] else '❌'} Swagger Generator")
    except Exception as e:
        test_results['swagger_generator'] = False
        print(f"  ❌ Swagger Generator: {e}")
    
    # Test Kafka Generator
    print("Testing Kafka Generator...")
    try:
        import unittest
        from test_kafka_generator import TestKafkaTestGenerator
        
        # Run tests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestKafkaTestGenerator)
        runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
        result = runner.run(suite)
        
        test_results['kafka_generator'] = result.wasSuccessful()
        print(f"  {'✅' if test_results['kafka_generator'] else '❌'} Kafka Generator")
    except Exception as e:
        test_results['kafka_generator'] = False
        print(f"  ❌ Kafka Generator: {e}")
    
    # Test Orchestrator
    print("Testing Orchestrator...")
    try:
        from test_orchestrator import run_tests
        result = run_tests()
        test_results['orchestrator'] = result
        print(f"  {'✅' if test_results['orchestrator'] else '❌'} Orchestrator")
    except Exception as e:
        test_results['orchestrator'] = False
        print(f"  ❌ Orchestrator: {e}")
    
    return test_results

def run_validation_tests():
    """Run validation tests"""
    print("\n🔍 Running Validation Tests")
    print("=" * 50)
    
    try:
        from validators import run_comprehensive_validation
        
        # Create mock data for validation
        mock_extracted_data = {
            'users': {
                'PRESIDENTE': [{'id': 1, 'nombre_usuario': 'test_presidente', 'rol': 'PRESIDENTE'}],
                'VOCAL': [{'id': 2, 'nombre_usuario': 'test_vocal', 'rol': 'VOCAL'}],
                'COORDINADOR': [{'id': 3, 'nombre_usuario': 'test_coordinador', 'rol': 'COORDINADOR'}],
                'VOLUNTARIO': [{'id': 4, 'nombre_usuario': 'test_voluntario', 'rol': 'VOLUNTARIO'}]
            },
            'inventory': {
                'ALIMENTOS': {'all': [{'id': 101, 'categoria': 'ALIMENTOS', 'cantidad': 100}]},
                'ROPA': {'all': [{'id': 201, 'categoria': 'ROPA', 'cantidad': 50}]},
                'JUGUETES': {'all': [{'id': 301, 'categoria': 'JUGUETES', 'cantidad': 10}]},
                'UTILES_ESCOLARES': {'all': [{'id': 401, 'categoria': 'UTILES_ESCOLARES', 'cantidad': 0}]}
            },
            'events': {
                'all': [{'id': 1, 'nombre': 'Test Event'}],
                'future': [{'id': 1, 'nombre': 'Test Event'}],
                'past': [], 'current': []
            },
            'network': {
                'external_requests': [{'id_solicitud': 'req-1', 'categoria': 'ALIMENTOS'}],
                'external_offers': [{'id_oferta': 'of-1', 'categoria': 'ROPA'}],
                'external_events': [{'id_evento': 'ev-1', 'nombre': 'External Event'}],
                'own_requests': [], 'own_offers': [], 'transfers_sent': [],
                'transfers_received': [], 'event_adhesions': []
            },
            'test_mappings': [
                {'endpoint': '/api/auth/login', 'test_category': 'authentication', 'user_id': 1},
                {'endpoint': '/api/usuarios', 'test_category': 'users', 'user_id': 1},
                {'endpoint': '/api/inventario/donaciones', 'test_category': 'inventory', 'user_id': 2},
                {'endpoint': '/api/eventos', 'test_category': 'events', 'user_id': 3},
                {'endpoint': '/api/red/solicitudes-donaciones', 'test_category': 'network', 'user_id': 2}
            ]
        }
        
        mock_kafka_scenarios = {
            'solicitud_donaciones': [
                {
                    'scenario_name': 'Test Donation Request',
                    'topic': 'solicitud-donaciones',
                    'message': {
                        'idOrganizacion': 'ong-empuje-comunitario',
                        'donaciones': [{'categoria': 'ALIMENTOS', 'descripcion': 'Test'}],
                        'usuarioSolicitante': 'test_vocal',
                        'timestamp': '2024-01-15T10:00:00Z'
                    },
                    'pre_conditions': ['Test condition'],
                    'post_conditions': ['Test result'],
                    'test_assertions': ['Test assertion']
                }
            ],
            'oferta_donaciones': [
                {
                    'scenario_name': 'Test Donation Offer',
                    'topic': 'oferta-donaciones',
                    'message': {
                        'idOrganizacion': 'ong-empuje-comunitario',
                        'donaciones': [{'id': 101, 'categoria': 'ALIMENTOS', 'cantidad': 10}],
                        'usuarioOfertante': 'test_vocal',
                        'timestamp': '2024-01-15T11:00:00Z'
                    },
                    'pre_conditions': ['Test condition'],
                    'post_conditions': ['Test result'],
                    'test_assertions': ['Test assertion']
                }
            ]
        }
        
        # Run validation (using non-existent paths to test error handling)
        validation_results = run_comprehensive_validation(
            postman_path="non_existent_postman_path",
            swagger_path="non_existent_swagger_path",
            kafka_scenarios=mock_kafka_scenarios,
            extracted_data=mock_extracted_data
        )
        
        print(f"  Overall Valid: {'✅' if validation_results['overall_valid'] else '❌'}")
        print(f"  Total Errors: {validation_results['summary']['total_errors']}")
        print(f"  Total Warnings: {validation_results['summary']['total_warnings']}")
        print(f"  Coverage Score: {validation_results['summary']['coverage_score']:.1f}%")
        
        return validation_results['summary']['total_errors'] == 0
        
    except Exception as e:
        print(f"  ❌ Validation Tests: {e}")
        return False

def run_integration_tests():
    """Run integration tests"""
    print("\n🔗 Running Integration Tests")
    print("=" * 50)
    
    try:
        from test_integration import run_integration_tests
        result = run_integration_tests()
        print(f"  {'✅' if result else '❌'} Integration Tests")
        return result
    except Exception as e:
        print(f"  ❌ Integration Tests: {e}")
        return False

def print_summary(unit_results, validation_result, integration_result):
    """Print test summary"""
    print("\n📊 TEST SUMMARY")
    print("=" * 50)
    
    # Unit tests summary
    unit_passed = sum(1 for result in unit_results.values() if result)
    unit_total = len(unit_results)
    print(f"Unit Tests: {unit_passed}/{unit_total} passed")
    
    for test_name, result in unit_results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {test_name.replace('_', ' ').title()}")
    
    # Other tests
    print(f"Validation Tests: {'✅' if validation_result else '❌'}")
    print(f"Integration Tests: {'✅' if integration_result else '❌'}")
    
    # Overall result
    total_passed = unit_passed + (1 if validation_result else 0) + (1 if integration_result else 0)
    total_tests = unit_total + 2
    
    print(f"\nOverall: {total_passed}/{total_tests} test categories passed")
    
    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"⚠️  {total_tests - total_passed} test category(ies) failed")
        return False

def main():
    """Main test execution"""
    print("SQL-Driven Testing - Validation and Testing System")
    print("=" * 60)
    
    # Run unit tests
    unit_results = run_unit_tests()
    
    # Run validation tests
    validation_result = run_validation_tests()
    
    # Run integration tests
    integration_result = run_integration_tests()
    
    # Print summary
    success = print_summary(unit_results, validation_result, integration_result)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())