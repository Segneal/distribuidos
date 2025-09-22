#!/usr/bin/env python3
"""
Test Suite for SwaggerGenerator
Sistema ONG - SQL Driven Testing

Tests for the SwaggerGenerator class to ensure it correctly updates
Swagger documentation examples with real SQL data.
"""

import unittest
import json
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock
from swagger_generator import SwaggerGenerator

class TestSwaggerGenerator(unittest.TestCase):
    """Test cases for SwaggerGenerator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_data = self.create_test_data()
        self.temp_dir = tempfile.mkdtemp()
        self.swagger_config_path = os.path.join(self.temp_dir, "swagger.js")
        
        # Create a mock Swagger configuration file
        self.create_mock_swagger_config()
        
        # Populate 'all' arrays in test data
        self.populate_all_arrays()
        
        # Create SwaggerGenerator instance with test data
        self.generator = SwaggerGenerator(self.test_data)
        self.generator.swagger_config_path = self.swagger_config_path
        self.generator.backup_dir = os.path.join(self.temp_dir, "backups")
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def populate_all_arrays(self):
        """Populate 'all' arrays in test data with items from all stock levels"""
        for categoria in self.test_data['inventory']:
            all_items = []
            for stock_level in ['high_stock', 'medium_stock', 'low_stock', 'zero_stock']:
                all_items.extend(self.test_data['inventory'][categoria][stock_level])
            self.test_data['inventory'][categoria]['all'] = all_items
        
        # Populate events 'all' array
        all_events = []
        for status in ['future', 'past', 'current']:
            all_events.extend(self.test_data['events'][status])
        self.test_data['events']['all'] = all_events
    
    def create_test_data(self):
        """Create mock extracted data for testing"""
        return {
            'users': {
                'PRESIDENTE': [{
                    'id': 1,
                    'nombre_usuario': 'test_presidente',
                    'nombre': 'Juan',
                    'apellido': 'Presidente',
                    'email': 'presidente@test.com',
                    'telefono': '1111111111',
                    'rol': 'PRESIDENTE',
                    'activo': True,
                    'fecha_hora_alta': '2024-01-15T10:30:00',
                    'usuario_alta': 'system',
                    'password_plain': 'test123'
                }],
                'VOCAL': [{
                    'id': 2,
                    'nombre_usuario': 'test_vocal',
                    'nombre': 'María',
                    'apellido': 'Vocal',
                    'email': 'vocal@test.com',
                    'telefono': '2222222222',
                    'rol': 'VOCAL',
                    'activo': True,
                    'fecha_hora_alta': '2024-01-15T10:30:00',
                    'usuario_alta': 'test_presidente',
                    'password_plain': 'test123'
                }],
                'COORDINADOR': [{
                    'id': 3,
                    'nombre_usuario': 'test_coordinador',
                    'nombre': 'Carlos',
                    'apellido': 'Coordinador',
                    'email': 'coordinador@test.com',
                    'telefono': '3333333333',
                    'rol': 'COORDINADOR',
                    'activo': True,
                    'fecha_hora_alta': '2024-01-15T10:30:00',
                    'usuario_alta': 'test_presidente',
                    'password_plain': 'test123'
                }],
                'VOLUNTARIO': [{
                    'id': 4,
                    'nombre_usuario': 'test_voluntario',
                    'nombre': 'Ana',
                    'apellido': 'Voluntario',
                    'email': 'voluntario@test.com',
                    'telefono': '4444444444',
                    'rol': 'VOLUNTARIO',
                    'activo': True,
                    'fecha_hora_alta': '2024-01-15T10:30:00',
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
                        'fecha_hora_alta': '2024-01-15T10:30:00',
                        'usuario_alta': 'test_vocal'
                    }],
                    'medium_stock': [{
                        'id': 102,
                        'categoria': 'ALIMENTOS',
                        'descripcion': 'Fideos - Test Stock Medio',
                        'cantidad': 25,
                        'eliminado': False,
                        'fecha_hora_alta': '2024-01-15T10:30:00',
                        'usuario_alta': 'test_vocal'
                    }],
                    'low_stock': [{
                        'id': 103,
                        'categoria': 'ALIMENTOS',
                        'descripcion': 'Conservas - Test Stock Bajo',
                        'cantidad': 5,
                        'eliminado': False,
                        'fecha_hora_alta': '2024-01-15T10:30:00',
                        'usuario_alta': 'test_vocal'
                    }],
                    'zero_stock': [{
                        'id': 104,
                        'categoria': 'ALIMENTOS',
                        'descripcion': 'Leche - Sin Stock',
                        'cantidad': 0,
                        'eliminado': False,
                        'fecha_hora_alta': '2024-01-15T10:30:00',
                        'usuario_alta': 'test_vocal'
                    }],
                    'all': []  # Will be populated by combining all stock levels
                },
                'ROPA': {
                    'high_stock': [],
                    'medium_stock': [{
                        'id': 201,
                        'categoria': 'ROPA',
                        'descripcion': 'Camisetas M - Test',
                        'cantidad': 30,
                        'eliminado': False,
                        'fecha_hora_alta': '2024-01-15T10:30:00',
                        'usuario_alta': 'test_vocal'
                    }],
                    'low_stock': [],
                    'zero_stock': [],
                    'all': []
                },
                'JUGUETES': {
                    'high_stock': [],
                    'medium_stock': [],
                    'low_stock': [{
                        'id': 301,
                        'categoria': 'JUGUETES',
                        'descripcion': 'Pelotas - Test Stock Bajo',
                        'cantidad': 3,
                        'eliminado': False,
                        'fecha_hora_alta': '2024-01-15T10:30:00',
                        'usuario_alta': 'test_vocal'
                    }],
                    'zero_stock': [],
                    'all': []
                },
                'UTILES_ESCOLARES': {
                    'high_stock': [],
                    'medium_stock': [],
                    'low_stock': [],
                    'zero_stock': [{
                        'id': 401,
                        'categoria': 'UTILES_ESCOLARES',
                        'descripcion': 'Cuadernos - Sin Stock',
                        'cantidad': 0,
                        'eliminado': False,
                        'fecha_hora_alta': '2024-01-15T10:30:00',
                        'usuario_alta': 'test_vocal'
                    }],
                    'all': []
                }
            },
            'events': {
                'future': [{
                    'id': 201,
                    'nombre': 'Evento Test Futuro',
                    'descripcion': 'Evento para testing',
                    'fecha_hora': '2024-12-15T14:00:00',
                    'participantes': [3, 4],
                    'total_participantes': 2,
                    'fecha_hora_alta': '2024-01-15T10:30:00',
                    'usuario_alta': 'test_coordinador'
                }],
                'past': [{
                    'id': 202,
                    'nombre': 'Evento Test Pasado',
                    'descripcion': 'Evento pasado para testing',
                    'fecha_hora': '2024-01-01T14:00:00',
                    'participantes': [4],
                    'total_participantes': 1,
                    'fecha_hora_alta': '2024-01-01T10:30:00',
                    'usuario_alta': 'test_coordinador'
                }],
                'current': [],
                'all': []  # Will be populated
            },
            'network': {
                'external_requests': [{
                    'id_organizacion': 'ong-corazon-solidario',
                    'id_solicitud': 'SOL-001',
                    'categoria': 'ALIMENTOS',
                    'descripcion': 'Arroz para familias',
                    'activa': True,
                    'fecha_recepcion': '2024-01-15T10:30:00'
                }],
                'external_offers': [{
                    'id_organizacion': 'ong-manos-unidas',
                    'id_oferta': 'OF-001',
                    'categoria': 'ROPA',
                    'descripcion': 'Ropa de abrigo',
                    'cantidad': 25,
                    'fecha_recepcion': '2024-01-15T10:30:00'
                }],
                'external_events': [{
                    'id_organizacion': 'ong-esperanza',
                    'id_evento': 'EV-001',
                    'nombre': 'Jornada Solidaria',
                    'descripcion': 'Evento comunitario',
                    'fecha_hora': '2024-12-20T09:00:00',
                    'activo': True,
                    'fecha_recepcion': '2024-01-15T10:30:00'
                }]
            }
        }
    
    def create_mock_swagger_config(self):
        """Create a mock Swagger configuration file"""
        mock_config = '''// Swagger configuration
const swaggerJsdoc = require('swagger-jsdoc');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Sistema ONG API',
      version: '1.0.0'
    },
    components: {
      schemas: {
        Usuario: {
          type: 'object',
          properties: {
            id: { type: 'integer' },
            nombreUsuario: { type: 'string' }
          }
        }
      },
      examples: {
        OldExample: {
          summary: 'Old example',
          value: { test: 'old' }
        }
      }
    },
    security: [
      {
        bearerAuth: []
      }
    ]
  }
};

module.exports = swaggerJsdoc(options);'''
        
        with open(self.swagger_config_path, 'w', encoding='utf-8') as f:
            f.write(mock_config)
    
    def test_generate_auth_examples(self):
        """Test generation of authentication examples"""
        auth_examples = self.generator.generate_auth_examples()
        
        # Check that all required auth examples are generated
        self.assertIn('LoginRequest', auth_examples)
        self.assertIn('LoginRequestVocal', auth_examples)
        self.assertIn('LoginResponse', auth_examples)
        self.assertIn('LoginError', auth_examples)
        
        # Check that examples use real user data
        login_example = auth_examples['LoginRequest']
        self.assertEqual(login_example['value']['identificador'], 'test_presidente')
        self.assertEqual(login_example['value']['clave'], 'test123')
        
        # Check response example includes real user data
        response_example = auth_examples['LoginResponse']
        self.assertEqual(response_example['value']['usuario']['id'], 1)
        self.assertEqual(response_example['value']['usuario']['nombreUsuario'], 'test_presidente')
    
    def test_generate_users_examples(self):
        """Test generation of user management examples"""
        users_examples = self.generator.generate_users_examples()
        
        # Check that all required user examples are generated
        self.assertIn('UsuariosList', users_examples)
        self.assertIn('UsuarioDetalle', users_examples)
        self.assertIn('CrearUsuario', users_examples)
        self.assertIn('ActualizarUsuario', users_examples)
        
        # Check that examples use real user data
        users_list = users_examples['UsuariosList']['value']
        self.assertIsInstance(users_list, list)
        self.assertGreater(len(users_list), 0)
        self.assertEqual(users_list[0]['nombreUsuario'], 'test_presidente')
        
        # Check user detail example
        user_detail = users_examples['UsuarioDetalle']['value']
        self.assertEqual(user_detail['id'], 1)
        self.assertEqual(user_detail['rol'], 'PRESIDENTE')
    
    def test_generate_inventory_examples(self):
        """Test generation of inventory examples"""
        inventory_examples = self.generator.generate_inventory_examples()
        
        # Check that all required inventory examples are generated
        self.assertIn('DonacionesList', inventory_examples)
        self.assertIn('DonacionDetalle', inventory_examples)
        self.assertIn('CrearDonacion', inventory_examples)
        self.assertIn('DonacionStockAlto', inventory_examples)
        self.assertIn('DonacionStockBajo', inventory_examples)
        self.assertIn('DonacionSinStock', inventory_examples)
        
        # Check that examples use real donation data
        donations_list = inventory_examples['DonacionesList']['value']
        self.assertIsInstance(donations_list, list)
        
        # Check high stock example
        high_stock = inventory_examples['DonacionStockAlto']['value']
        self.assertEqual(high_stock['id'], 101)
        self.assertEqual(high_stock['categoria'], 'ALIMENTOS')
        self.assertEqual(high_stock['cantidad'], 100)
        
        # Check low stock example
        low_stock = inventory_examples['DonacionStockBajo']['value']
        self.assertEqual(low_stock['id'], 301)
        self.assertEqual(low_stock['categoria'], 'JUGUETES')
        self.assertEqual(low_stock['cantidad'], 3)
        
        # Check zero stock example
        zero_stock = inventory_examples['DonacionSinStock']['value']
        self.assertEqual(zero_stock['cantidad'], 0)
    
    def test_generate_events_examples(self):
        """Test generation of events examples"""
        events_examples = self.generator.generate_events_examples()
        
        # Check that all required event examples are generated
        self.assertIn('EventosList', events_examples)
        self.assertIn('EventoDetalle', events_examples)
        self.assertIn('CrearEvento', events_examples)
        self.assertIn('EventoFuturo', events_examples)
        self.assertIn('EventoPasado', events_examples)
        
        # Check that examples use real event data
        future_event = events_examples['EventoFuturo']['value']
        self.assertEqual(future_event['id'], 201)
        self.assertEqual(future_event['nombre'], 'Evento Test Futuro')
        
        past_event = events_examples['EventoPasado']['value']
        self.assertEqual(past_event['id'], 202)
        self.assertEqual(past_event['nombre'], 'Evento Test Pasado')
    
    def test_generate_network_examples(self):
        """Test generation of network examples"""
        network_examples = self.generator.generate_network_examples()
        
        # Check that all required network examples are generated
        self.assertIn('SolicitudesExternas', network_examples)
        self.assertIn('CrearSolicitudDonaciones', network_examples)
        self.assertIn('OfertasExternas', network_examples)
        self.assertIn('TransferirDonaciones', network_examples)
        self.assertIn('EventosExternos', network_examples)
        self.assertIn('AdhesionEventoExterno', network_examples)
        
        # Check that examples use real network data
        external_requests = network_examples['SolicitudesExternas']['value']
        self.assertIsInstance(external_requests, list)
        self.assertEqual(external_requests[0]['idOrganizacion'], 'ong-corazon-solidario')
        
        # Check transfer example uses real donation data
        transfer_example = network_examples['TransferirDonaciones']['value']
        self.assertIn('donaciones', transfer_example)
        self.assertIsInstance(transfer_example['donaciones'], list)
    
    def test_build_examples_javascript(self):
        """Test building JavaScript object string for examples"""
        test_examples = {
            'auth': {
                'LoginExample': {
                    'summary': 'Test login',
                    'value': {'user': 'test', 'pass': 'test123'}
                }
            }
        }
        
        js_string = self.generator.build_examples_javascript(test_examples)
        
        # Check that JavaScript is properly formatted
        self.assertIn('// Auth Examples', js_string)
        self.assertIn('LoginExample: {', js_string)
        self.assertIn("summary: 'Test login'", js_string)
        self.assertIn('"user": "test"', js_string)
    
    def test_create_backup(self):
        """Test backup creation functionality"""
        # Create backup
        self.generator.create_backup()
        
        # Check that backup directory was created
        self.assertTrue(os.path.exists(self.generator.backup_dir))
        
        # Check that backup file was created
        backup_files = os.listdir(self.generator.backup_dir)
        self.assertEqual(len(backup_files), 1)
        self.assertTrue(backup_files[0].startswith('swagger_config_backup_'))
        self.assertTrue(backup_files[0].endswith('.js'))
    
    def test_validate_updated_examples(self):
        """Test validation of updated examples"""
        # Update the config with valid examples
        auth_examples = self.generator.generate_auth_examples()
        examples = {'authentication': auth_examples}
        
        # Load and update config
        config = self.generator.load_swagger_config()
        updated_config = self.generator.integrate_examples(config, examples)
        self.generator.save_swagger_config(updated_config)
        
        # Validate
        validation_result = self.generator.validate_updated_examples()
        
        self.assertIsInstance(validation_result, dict)
        self.assertIn('valid', validation_result)
        self.assertIn('errors', validation_result)
        self.assertIsInstance(validation_result['errors'], list)
    
    def test_get_user_by_role(self):
        """Test getting user by role"""
        presidente = self.generator.get_user_by_role('PRESIDENTE')
        self.assertEqual(presidente['id'], 1)
        self.assertEqual(presidente['rol'], 'PRESIDENTE')
        
        vocal = self.generator.get_user_by_role('VOCAL')
        self.assertEqual(vocal['id'], 2)
        self.assertEqual(vocal['rol'], 'VOCAL')
        
        # Test non-existent role
        with self.assertRaises(ValueError):
            self.generator.get_user_by_role('NONEXISTENT')
    
    def test_get_donation_by_category_and_stock(self):
        """Test getting donation by category and stock level"""
        high_stock = self.generator.get_donation_by_category_and_stock('ALIMENTOS', 'high_stock')
        self.assertEqual(high_stock['id'], 101)
        self.assertEqual(high_stock['cantidad'], 100)
        
        low_stock = self.generator.get_donation_by_category_and_stock('JUGUETES', 'low_stock')
        self.assertEqual(low_stock['id'], 301)
        self.assertEqual(low_stock['cantidad'], 3)
        
        # Test fallback to 'all' when specific stock level not found
        medium_stock = self.generator.get_donation_by_category_and_stock('ROPA', 'high_stock')
        self.assertEqual(medium_stock['id'], 201)  # Should fallback to medium_stock item
    
    def test_integration_update_swagger_examples(self):
        """Test the complete integration of updating Swagger examples"""
        # Run the complete update process
        result = self.generator.update_swagger_examples()
        
        # Check result structure
        self.assertIsInstance(result, dict)
        self.assertIn('examples_updated', result)
        self.assertIn('backup_created', result)
        self.assertIn('validation_passed', result)
        self.assertIn('total_examples', result)
        
        # Check that examples were updated
        self.assertGreater(result['total_examples'], 0)
        self.assertTrue(result['backup_created'])
        
        # Check that the file was actually updated
        with open(self.swagger_config_path, 'r', encoding='utf-8') as f:
            updated_content = f.read()
        
        # Should contain new examples
        self.assertIn('LoginRequest:', updated_content)
        self.assertIn('test_presidente', updated_content)
        self.assertIn('DonacionesList:', updated_content)

def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)

if __name__ == '__main__':
    run_tests()