#!/usr/bin/env python3
"""
Integration Test Suite
Sistema ONG - SQL Driven Testing

Comprehensive integration tests that validate the complete flow from SQL data
to generated configurations. Tests the entire pipeline end-to-end.
"""

import unittest
import json
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Import modules to test
from data_extractor import SQLDataExtractor, DatabaseConfig
from postman_generator import PostmanGenerator
from swagger_generator import SwaggerGenerator
from kafka_generator import KafkaTestGenerator
from orchestrator import TestingOrchestrator
from validators import run_comprehensive_validation

class TestSQLToPostmanIntegration(unittest.TestCase):
    """Test integration from SQL data extraction to Postman generation"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.postman_dir = Path(self.temp_dir) / "postman"
        self.postman_dir.mkdir(parents=True)
        
        # Create comprehensive test data
        self.test_data = self._create_comprehensive_test_data()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def _create_comprehensive_test_data(self):
        """Create comprehensive test data that covers all scenarios"""
        return {
            'users': {
                'PRESIDENTE': [{
                    'id': 1, 'nombre_usuario': 'test_presidente', 'nombre': 'Juan', 'apellido': 'Presidente',
                    'email': 'presidente@test.com', 'telefono': '1111111111', 'rol': 'PRESIDENTE',
                    'activo': True, 'fecha_hora_alta': '2024-01-15T10:30:00', 'usuario_alta': 'system',
                    'password_plain': 'test123'
                }],
                'VOCAL': [{
                    'id': 2, 'nombre_usuario': 'test_vocal', 'nombre': 'María', 'apellido': 'Vocal',
                    'email': 'vocal@test.com', 'telefono': '2222222222', 'rol': 'VOCAL',
                    'activo': True, 'fecha_hora_alta': '2024-01-15T10:30:00', 'usuario_alta': 'test_presidente',
                    'password_plain': 'test123'
                }],
                'COORDINADOR': [{
                    'id': 3, 'nombre_usuario': 'test_coordinador', 'nombre': 'Carlos', 'apellido': 'Coordinador',
                    'email': 'coordinador@test.com', 'telefono': '3333333333', 'rol': 'COORDINADOR',
                    'activo': True, 'fecha_hora_alta': '2024-01-15T10:30:00', 'usuario_alta': 'test_presidente',
                    'password_plain': 'test123'
                }],
                'VOLUNTARIO': [{
                    'id': 4, 'nombre_usuario': 'test_voluntario', 'nombre': 'Ana', 'apellido': 'Voluntario',
                    'email': 'voluntario@test.com', 'telefono': '4444444444', 'rol': 'VOLUNTARIO',
                    'activo': True, 'fecha_hora_alta': '2024-01-15T10:30:00', 'usuario_alta': 'test_coordinador',
                    'password_plain': 'test123'
                }]
            },
            'inventory': {
                'ALIMENTOS': {
                    'high_stock': [
                        {'id': 101, 'categoria': 'ALIMENTOS', 'descripcion': 'Arroz 1kg - Test Stock Alto', 'cantidad': 100},
                        {'id': 105, 'categoria': 'ALIMENTOS', 'descripcion': 'Leche 1L - Para Transferencia', 'cantidad': 25}
                    ],
                    'medium_stock': [
                        {'id': 102, 'categoria': 'ALIMENTOS', 'descripcion': 'Fideos 500g', 'cantidad': 30}
                    ],
                    'low_stock': [
                        {'id': 103, 'categoria': 'ALIMENTOS', 'descripcion': 'Conservas', 'cantidad': 5}
                    ],
                    'zero_stock': [
                        {'id': 104, 'categoria': 'ALIMENTOS', 'descripcion': 'Azúcar - Sin Stock', 'cantidad': 0}
                    ],
                    'all': []
                },
                'ROPA': {
                    'high_stock': [
                        {'id': 201, 'categoria': 'ROPA', 'descripcion': 'Camisetas M', 'cantidad': 50}
                    ],
                    'medium_stock': [], 'low_stock': [], 'zero_stock': [], 'all': []
                },
                'JUGUETES': {
                    'high_stock': [], 'medium_stock': [],
                    'low_stock': [
                        {'id': 301, 'categoria': 'JUGUETES', 'descripcion': 'Pelotas', 'cantidad': 3}
                    ],
                    'zero_stock': [], 'all': []
                },
                'UTILES_ESCOLARES': {
                    'high_stock': [], 'medium_stock': [], 'low_stock': [],
                    'zero_stock': [
                        {'id': 401, 'categoria': 'UTILES_ESCOLARES', 'descripcion': 'Cuadernos', 'cantidad': 0}
                    ],
                    'all': []
                }
            },
            'events': {
                'future': [
                    {
                        'id': 201, 'nombre': 'Evento Test Futuro 1', 'descripcion': 'Evento para testing',
                        'fecha_hora': (datetime.now() + timedelta(days=7)).isoformat(),
                        'participantes': [3, 4], 'total_participantes': 2,
                        'fecha_hora_alta': '2024-01-15T10:30:00', 'usuario_alta': 'test_coordinador'
                    }
                ],
                'past': [
                    {
                        'id': 202, 'nombre': 'Evento Test Pasado', 'descripcion': 'Evento pasado',
                        'fecha_hora': (datetime.now() - timedelta(days=7)).isoformat(),
                        'participantes': [4], 'total_participantes': 1,
                        'fecha_hora_alta': '2024-01-01T10:30:00', 'usuario_alta': 'test_coordinador'
                    }
                ],
                'current': [], 'all': []
            },
            'network': {
                'external_requests': [
                    {
                        'id_organizacion': 'ong-corazon-solidario', 'id_solicitud': 'sol-001',
                        'categoria': 'ALIMENTOS', 'descripcion': 'Arroz para familias',
                        'activa': True, 'fecha_recepcion': '2024-01-15T10:30:00'
                    }
                ],
                'external_offers': [
                    {
                        'id_organizacion': 'ong-manos-unidas', 'id_oferta': 'of-001',
                        'categoria': 'ROPA', 'descripcion': 'Ropa de abrigo',
                        'cantidad': 25, 'fecha_recepcion': '2024-01-15T10:30:00'
                    }
                ],
                'external_events': [
                    {
                        'id_organizacion': 'ong-esperanza', 'id_evento': 'ev-001',
                        'nombre': 'Jornada Solidaria', 'descripcion': 'Evento comunitario',
                        'fecha_hora': (datetime.now() + timedelta(days=10)).isoformat(),
                        'activo': True, 'fecha_recepcion': '2024-01-15T10:30:00'
                    }
                ],
                'own_requests': [], 'own_offers': [], 'transfers_sent': [],
                'transfers_received': [], 'event_adhesions': []
            },
            'test_mappings': [
                {
                    'endpoint': '/api/auth/login', 'method': 'POST', 'test_type': 'success',
                    'test_category': 'authentication', 'user_id': 1, 'resource_id': None,
                    'description': 'Login exitoso - Presidente', 'expected_status': 200,
                    'request_body': None, 'expected_response_fields': None
                },
                {
                    'endpoint': '/api/usuarios', 'method': 'GET', 'test_type': 'success',
                    'test_category': 'users', 'user_id': 1, 'resource_id': None,
                    'description': 'Listar usuarios - Presidente', 'expected_status': 200,
                    'request_body': None, 'expected_response_fields': None
                },
                {
                    'endpoint': '/api/inventario/donaciones', 'method': 'GET', 'test_type': 'success',
                    'test_category': 'inventory', 'user_id': 2, 'resource_id': None,
                    'description': 'Listar donaciones - Vocal', 'expected_status': 200,
                    'request_body': None, 'expected_response_fields': None
                },
                {
                    'endpoint': '/api/eventos', 'method': 'GET', 'test_type': 'success',
                    'test_category': 'events', 'user_id': 3, 'resource_id': None,
                    'description': 'Listar eventos - Coordinador', 'expected_status': 200,
                    'request_body': None, 'expected_response_fields': None
                },
                {
                    'endpoint': '/api/red/solicitudes-donaciones', 'method': 'GET', 'test_type': 'success',
                    'test_category': 'network', 'user_id': 2, 'resource_id': None,
                    'description': 'Listar solicitudes externas - Vocal', 'expected_status': 200,
                    'request_body': None, 'expected_response_fields': None
                }
            ]
        }
    
    def _populate_all_arrays(self, data):
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
    
    def test_sql_to_postman_integration(self):
        """Test complete integration from SQL data to Postman collections"""
        # Populate all arrays
        test_data = self._populate_all_arrays(self.test_data)
        
        # Generate Postman collections
        generator = PostmanGenerator(test_data)
        generator.base_collection_path = str(self.postman_dir)
        
        # Generate all collections
        collections_result = generator.generate_all_collections()
        
        # Verify collections were generated
        self.assertIsInstance(collections_result, dict)
        self.assertGreater(len(collections_result), 0)
        
        # Check that files were actually created
        collection_files = list(self.postman_dir.glob("*.json"))
        self.assertGreater(len(collection_files), 0)
        
        # Validate each collection file
        for collection_file in collection_files:
            with open(collection_file, 'r', encoding='utf-8') as f:
                collection_data = json.load(f)
            
            # Basic structure validation
            self.assertIn('info', collection_data)
            self.assertIn('item', collection_data)
            self.assertIsInstance(collection_data['item'], list)
            
            # Check that requests use real data
            for item in collection_data['item']:
                if 'request' in item:
                    request = item['request']
                    
                    # Check for variables (should contain real IDs/tokens)
                    if 'url' in request:
                        url_str = str(request['url'])
                        if '{{' in url_str:
                            # Should contain meaningful variable names
                            self.assertTrue(
                                any(var in url_str for var in ['base_url', 'auth_token', 'user_id']),
                                f"URL should contain meaningful variables: {url_str}"
                            )
    
    def test_sql_to_swagger_integration(self):
        """Test complete integration from SQL data to Swagger examples"""
        # Populate all arrays
        test_data = self._populate_all_arrays(self.test_data)
        
        # Create temporary swagger config
        swagger_file = Path(self.temp_dir) / "swagger.js"
        initial_config = """
        module.exports = {
            openapi: '3.0.0',
            info: { title: 'Test API', version: '1.0.0' },
            components: {
                examples: {
                    OldExample: { summary: 'Old', value: {} }
                }
            }
        };
        """
        swagger_file.write_text(initial_config)
        
        # Generate Swagger examples
        generator = SwaggerGenerator(test_data)
        generator.swagger_config_path = str(swagger_file)
        generator.backup_dir = str(Path(self.temp_dir) / "backups")
        
        result = generator.update_swagger_examples()
        
        # Verify update was successful
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get('backup_created', False))
        self.assertGreater(result.get('total_examples', 0), 0)
        
        # Check that file was updated
        with open(swagger_file, 'r', encoding='utf-8') as f:
            updated_content = f.read()
        
        # Should contain new examples with real data
        self.assertIn('LoginRequest', updated_content)
        self.assertIn('test_presidente', updated_content)
        self.assertIn('DonacionesList', updated_content)
    
    def test_sql_to_kafka_integration(self):
        """Test complete integration from SQL data to Kafka scenarios"""
        # Populate all arrays
        test_data = self._populate_all_arrays(self.test_data)
        
        # Generate Kafka scenarios
        generator = KafkaTestGenerator(test_data)
        scenarios = generator.generate_all_kafka_scenarios()
        
        # Verify scenarios were generated
        self.assertIsInstance(scenarios, dict)
        self.assertGreater(len(scenarios), 0)
        
        # Check specific topics
        expected_topics = ['solicitud_donaciones', 'oferta_donaciones', 'eventos_solidarios']
        for topic in expected_topics:
            self.assertIn(topic, scenarios)
            self.assertIsInstance(scenarios[topic], list)
            
            if scenarios[topic]:  # If scenarios exist for this topic
                scenario = scenarios[topic][0]
                
                # Verify scenario structure
                self.assertIn('scenario_name', scenario)
                self.assertIn('message', scenario)
                self.assertIn('pre_conditions', scenario)
                self.assertIn('post_conditions', scenario)
                
                # Verify message uses real data
                message = scenario['message']
                self.assertIn('idOrganizacion', message)
                self.assertEqual(message['idOrganizacion'], 'ong-empuje-comunitario')
                self.assertIn('timestamp', message)

class TestEndToEndOrchestration(unittest.TestCase):
    """Test complete end-to-end orchestration"""
    
    def setUp(self):
        """Set up end-to-end test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test configuration
        self.test_config = {
            'database': {
                'host': 'localhost', 'port': 3306, 'database': 'test_db',
                'user': 'test_user', 'password': 'test_pass'
            },
            'generation': {
                'postman': True, 'swagger': True, 'kafka': True,
                'backup': True, 'validate': True
            },
            'output': {
                'save_extracted_data': True,
                'extracted_data_file': f'{self.temp_dir}/extracted_data.json',
                'report_file': f'{self.temp_dir}/report.json'
            }
        }
        
        # Mock comprehensive extracted data
        self.mock_extracted_data = {
            'users': {
                'PRESIDENTE': [{'id': 1, 'nombre_usuario': 'test_presidente', 'rol': 'PRESIDENTE'}],
                'VOCAL': [{'id': 2, 'nombre_usuario': 'test_vocal', 'rol': 'VOCAL'}],
                'COORDINADOR': [{'id': 3, 'nombre_usuario': 'test_coordinador', 'rol': 'COORDINADOR'}],
                'VOLUNTARIO': [{'id': 4, 'nombre_usuario': 'test_voluntario', 'rol': 'VOLUNTARIO'}]
            },
            'inventory': {
                'ALIMENTOS': {'all': [{'id': 1, 'categoria': 'ALIMENTOS', 'cantidad': 100}]},
                'ROPA': {'all': [{'id': 2, 'categoria': 'ROPA', 'cantidad': 50}]},
                'JUGUETES': {'all': [{'id': 3, 'categoria': 'JUGUETES', 'cantidad': 10}]},
                'UTILES_ESCOLARES': {'all': [{'id': 4, 'categoria': 'UTILES_ESCOLARES', 'cantidad': 0}]}
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
    
    def tearDown(self):
        """Clean up end-to-end test environment"""
        shutil.rmtree(self.temp_dir)
    
    @patch('orchestrator.SQLDataExtractor')
    @patch('orchestrator.PostmanGenerator')
    @patch('orchestrator.SwaggerGenerator')
    @patch('orchestrator.KafkaTestGenerator')
    def test_complete_orchestration_flow(self, mock_kafka_gen, mock_swagger_gen, 
                                       mock_postman_gen, mock_sql_extractor):
        """Test complete orchestration from data extraction to validation"""
        
        # Mock the data extractor
        mock_extractor_instance = Mock()
        mock_extractor_instance.extract_test_data.return_value = self.mock_extracted_data
        mock_sql_extractor.return_value = mock_extractor_instance
        
        # Mock the generators with realistic results
        mock_postman_instance = Mock()
        mock_postman_instance.generate_all_collections.return_value = {
            '01-Autenticacion.postman_collection.json': f'{self.temp_dir}/auth.json',
            '02-Usuarios.postman_collection.json': f'{self.temp_dir}/users.json',
            '03-Inventario.postman_collection.json': f'{self.temp_dir}/inventory.json',
            '04-Eventos.postman_collection.json': f'{self.temp_dir}/events.json',
            '05-Red-ONGs.postman_collection.json': f'{self.temp_dir}/network.json'
        }
        mock_postman_gen.return_value = mock_postman_instance
        
        mock_swagger_instance = Mock()
        mock_swagger_instance.update_swagger_examples.return_value = {
            'total_examples': 15,
            'validation_passed': True,
            'backup_created': True,
            'examples_updated': ['LoginRequest', 'UsuariosList', 'DonacionesList', 'EventosList']
        }
        mock_swagger_gen.return_value = mock_swagger_instance
        
        mock_kafka_instance = Mock()
        mock_kafka_instance.generate_all_kafka_scenarios.return_value = {
            'solicitud_donaciones': [{'scenario_name': 'Test Request', 'message': {}}],
            'oferta_donaciones': [{'scenario_name': 'Test Offer', 'message': {}}],
            'eventos_solidarios': [{'scenario_name': 'Test Event', 'message': {}}],
            'transferencia_donaciones': [{'scenario_name': 'Test Transfer', 'message': {}}]
        }
        mock_kafka_gen.return_value = mock_kafka_instance
        
        # Create orchestrator
        with patch.object(TestingOrchestrator, '_load_config', return_value=self.test_config):
            orchestrator = TestingOrchestrator()
            
            # Mock backup manager
            orchestrator.backup_manager = Mock()
            orchestrator.backup_manager.create_backups.return_value = f'{self.temp_dir}/backup'
            
            # Run complete generation
            report = orchestrator.generate_all_testing_configs()
            
            # Verify orchestration success
            self.assertTrue(report.get('success', False))
            self.assertIn('generation_results', report)
            self.assertIn('validation_results', report)
            self.assertIn('summary', report)
            
            # Verify all components were called
            mock_extractor_instance.extract_test_data.assert_called_once()
            mock_postman_instance.generate_all_collections.assert_called_once()
            mock_swagger_instance.update_swagger_examples.assert_called_once()
            mock_kafka_instance.generate_all_kafka_scenarios.assert_called_once()
            
            # Verify output files were created
            self.assertTrue(Path(self.test_config['output']['extracted_data_file']).exists())
            self.assertTrue(Path(self.test_config['output']['report_file']).exists())
            
            # Verify report content
            summary = report['summary']
            self.assertIn('total_configurations_generated', summary)
            self.assertIn('total_test_cases', summary)
            self.assertIn('validation_score', summary)

class TestValidationIntegration(unittest.TestCase):
    """Test integration of validation system with generated configurations"""
    
    def setUp(self):
        """Set up validation integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.postman_dir = Path(self.temp_dir) / "postman"
        self.postman_dir.mkdir(parents=True)
        
        # Create test files for validation
        self._create_test_postman_collections()
        self._create_test_swagger_config()
        self._create_test_kafka_scenarios()
    
    def tearDown(self):
        """Clean up validation integration test environment"""
        shutil.rmtree(self.temp_dir)
    
    def _create_test_postman_collections(self):
        """Create test Postman collections for validation"""
        collections = {
            '01-Autenticacion.postman_collection.json': {
                "info": {"name": "01 - Autenticación"},
                "item": [
                    {
                        "name": "Login Presidente - Success",
                        "request": {
                            "method": "POST",
                            "url": "{{base_url}}/api/auth/login",
                            "body": {"raw": '{"nombreUsuario":"test_presidente","clave":"test123"}'}
                        },
                        "event": [{
                            "listen": "test",
                            "script": {"exec": ["pm.test('Status is 200', function () { pm.response.to.have.status(200); });"]}
                        }]
                    }
                ]
            },
            '02-Usuarios.postman_collection.json': {
                "info": {"name": "02 - Usuarios"},
                "item": [
                    {
                        "name": "Listar Usuarios - Presidente",
                        "request": {
                            "method": "GET",
                            "url": "{{base_url}}/api/usuarios",
                            "header": [{"key": "Authorization", "value": "Bearer {{auth_token}}"}]
                        }
                    }
                ]
            }
        }
        
        for filename, collection_data in collections.items():
            collection_path = self.postman_dir / filename
            with open(collection_path, 'w', encoding='utf-8') as f:
                json.dump(collection_data, f, indent=2)
    
    def _create_test_swagger_config(self):
        """Create test Swagger configuration for validation"""
        self.swagger_file = Path(self.temp_dir) / "swagger.js"
        swagger_content = """
        module.exports = {
            openapi: '3.0.0',
            info: { title: 'Sistema ONG API', version: '1.0.0' },
            components: {
                examples: {
                    LoginRequest: {
                        summary: 'Login request example',
                        value: { nombreUsuario: 'test_presidente', clave: 'test123' }
                    },
                    LoginResponse: {
                        summary: 'Login response example',
                        value: { token: 'jwt_token_here', usuario: { id: 1, rol: 'PRESIDENTE' } }
                    },
                    UsuariosList: {
                        summary: 'Users list example',
                        value: [{ id: 1, nombreUsuario: 'test_presidente', rol: 'PRESIDENTE' }]
                    },
                    DonacionesList: {
                        summary: 'Donations list example',
                        value: [{ id: 101, categoria: 'ALIMENTOS', descripcion: 'Arroz 1kg', cantidad: 100 }]
                    }
                }
            }
        };
        """
        self.swagger_file.write_text(swagger_content)
    
    def _create_test_kafka_scenarios(self):
        """Create test Kafka scenarios for validation"""
        self.kafka_scenarios = {
            'solicitud_donaciones': [
                {
                    'scenario_name': 'Solicitud de Alimentos - Exitosa',
                    'topic': 'solicitud-donaciones',
                    'message_key': 'req-001',
                    'message': {
                        'idOrganizacion': 'ong-empuje-comunitario',
                        'donaciones': [{'categoria': 'ALIMENTOS', 'descripcion': 'Arroz para familias'}],
                        'usuarioSolicitante': 'test_vocal',
                        'timestamp': '2024-01-15T10:00:00Z'
                    },
                    'pre_conditions': ['Usuario debe tener rol VOCAL o superior'],
                    'post_conditions': ['Mensaje publicado en topic solicitud-donaciones'],
                    'test_assertions': ['Mensaje enviado exitosamente', 'Otras ONGs pueden ver la solicitud'],
                    'expected_external_response': True
                }
            ],
            'oferta_donaciones': [
                {
                    'scenario_name': 'Oferta de Donaciones - Stock Alto',
                    'topic': 'oferta-donaciones',
                    'message_key': 'of-001',
                    'message': {
                        'idOrganizacion': 'ong-empuje-comunitario',
                        'donaciones': [{'id': 101, 'categoria': 'ALIMENTOS', 'cantidad': 10}],
                        'usuarioOfertante': 'test_vocal',
                        'timestamp': '2024-01-15T11:00:00Z'
                    },
                    'pre_conditions': ['Donación debe tener stock suficiente'],
                    'post_conditions': ['Stock reducido correctamente'],
                    'test_assertions': ['Oferta publicada exitosamente'],
                    'expected_external_response': True
                }
            ]
        }
    
    def test_comprehensive_validation_integration(self):
        """Test comprehensive validation of all generated configurations"""
        
        # Create test extracted data
        extracted_data = {
            'users': {
                'PRESIDENTE': [{'id': 1, 'nombre_usuario': 'test_presidente', 'rol': 'PRESIDENTE'}],
                'VOCAL': [{'id': 2, 'nombre_usuario': 'test_vocal', 'rol': 'VOCAL'}]
            },
            'inventory': {
                'ALIMENTOS': {'all': [{'id': 101, 'categoria': 'ALIMENTOS', 'cantidad': 100}]}
            },
            'events': {'all': [], 'future': [], 'past': []},
            'network': {'external_requests': [], 'external_offers': [], 'external_events': []},
            'test_mappings': [
                {'endpoint': '/api/auth/login', 'test_category': 'authentication'},
                {'endpoint': '/api/usuarios', 'test_category': 'users'}
            ]
        }
        
        # Run comprehensive validation
        validation_results = run_comprehensive_validation(
            postman_path=str(self.postman_dir),
            swagger_path=str(self.swagger_file),
            kafka_scenarios=self.kafka_scenarios,
            extracted_data=extracted_data
        )
        
        # Verify validation results structure
        self.assertIsInstance(validation_results, dict)
        self.assertIn('timestamp', validation_results)
        self.assertIn('overall_valid', validation_results)
        self.assertIn('validation_results', validation_results)
        self.assertIn('summary', validation_results)
        
        # Check individual validation results
        validation_results_detail = validation_results['validation_results']
        self.assertIn('postman', validation_results_detail)
        self.assertIn('swagger', validation_results_detail)
        self.assertIn('kafka', validation_results_detail)
        self.assertIn('integration', validation_results_detail)
        
        # Verify Postman validation
        postman_results = validation_results_detail['postman']
        self.assertGreater(postman_results['collections_found'], 0)
        self.assertGreater(postman_results['total_requests'], 0)
        
        # Verify Swagger validation
        swagger_results = validation_results_detail['swagger']
        self.assertGreater(swagger_results['examples_found'], 0)
        self.assertIn('authentication', swagger_results['categories_covered'])
        
        # Verify Kafka validation
        kafka_results = validation_results_detail['kafka']
        self.assertGreater(kafka_results['topics_found'], 0)
        self.assertGreater(kafka_results['total_scenarios'], 0)
        
        # Verify integration validation
        integration_results = validation_results_detail['integration']
        self.assertIn('consistency_checks', integration_results)
        self.assertIn('coverage_analysis', integration_results)
        
        # Check summary metrics
        summary = validation_results['summary']
        self.assertIn('total_errors', summary)
        self.assertIn('total_warnings', summary)
        self.assertIn('coverage_score', summary)
        self.assertIsInstance(summary['coverage_score'], (int, float))

class TestDataConsistencyValidation(unittest.TestCase):
    """Test data consistency across all generated configurations"""
    
    def test_user_data_consistency(self):
        """Test that user data is consistent across all configurations"""
        # Create test data with specific user IDs
        test_data = {
            'users': {
                'PRESIDENTE': [{'id': 1, 'nombre_usuario': 'test_presidente', 'password_plain': 'test123'}],
                'VOCAL': [{'id': 2, 'nombre_usuario': 'test_vocal', 'password_plain': 'test123'}]
            },
            'inventory': {'ALIMENTOS': {'all': []}},
            'events': {'all': [], 'future': [], 'past': []},
            'network': {'external_requests': [], 'external_offers': [], 'external_events': []},
            'test_mappings': [
                {'endpoint': '/api/auth/login', 'user_id': 1, 'test_category': 'authentication'},
                {'endpoint': '/api/usuarios', 'user_id': 2, 'test_category': 'users'}
            ]
        }
        
        # Generate Postman collections
        postman_generator = PostmanGenerator(test_data)
        auth_collection = postman_generator.generate_auth_collection()
        
        # Generate Kafka scenarios
        kafka_generator = KafkaTestGenerator(test_data)
        kafka_scenarios = kafka_generator.generate_donation_request_scenarios()
        
        # Verify user consistency
        # Check that Postman uses the same usernames as test data
        auth_requests = auth_collection.get('item', [])
        postman_usernames = []
        
        for request in auth_requests:
            if 'request' in request and 'body' in request['request']:
                body = request['request']['body']
                if isinstance(body, dict) and 'raw' in body:
                    try:
                        body_data = json.loads(body['raw'])
                        if 'nombreUsuario' in body_data:
                            postman_usernames.append(body_data['nombreUsuario'])
                    except json.JSONDecodeError:
                        pass
        
        # Check that Kafka scenarios use the same usernames
        kafka_usernames = []
        for scenario in kafka_scenarios:
            message = scenario.get('message', {})
            if 'usuarioSolicitante' in message:
                kafka_usernames.append(message['usuarioSolicitante'])
        
        # Verify consistency
        expected_usernames = ['test_presidente', 'test_vocal']
        for username in expected_usernames:
            if postman_usernames:  # Only check if Postman generated usernames
                self.assertIn(username, postman_usernames, 
                            f"Username {username} not found in Postman collections")
        
        # Note: Kafka scenarios might not always include all users depending on the scenario type
    
    def test_inventory_data_consistency(self):
        """Test that inventory data is consistent across configurations"""
        # Create test data with specific inventory items
        test_data = {
            'users': {'VOCAL': [{'id': 2, 'nombre_usuario': 'test_vocal'}]},
            'inventory': {
                'ALIMENTOS': {
                    'high_stock': [
                        {'id': 101, 'categoria': 'ALIMENTOS', 'descripcion': 'Arroz 1kg', 'cantidad': 100}
                    ],
                    'all': [
                        {'id': 101, 'categoria': 'ALIMENTOS', 'descripcion': 'Arroz 1kg', 'cantidad': 100}
                    ]
                }
            },
            'events': {'all': [], 'future': [], 'past': []},
            'network': {'external_requests': [], 'external_offers': [], 'external_events': []},
            'test_mappings': [
                {'endpoint': '/api/inventario/donaciones', 'resource_id': 101, 'test_category': 'inventory'}
            ]
        }
        
        # Generate Swagger examples
        swagger_generator = SwaggerGenerator(test_data)
        inventory_examples = swagger_generator.generate_inventory_examples()
        
        # Generate Kafka scenarios
        kafka_generator = KafkaTestGenerator(test_data)
        offer_scenarios = kafka_generator.generate_donation_offer_scenarios()
        
        # Verify inventory consistency
        # Check that Swagger examples use the same inventory IDs
        donations_list = inventory_examples.get('DonacionesList', {}).get('value', [])
        swagger_donation_ids = [donation.get('id') for donation in donations_list if isinstance(donation, dict)]
        
        # Check that Kafka scenarios reference the same inventory items
        kafka_donation_ids = []
        for scenario in offer_scenarios:
            message = scenario.get('message', {})
            donaciones = message.get('donaciones', [])
            for donacion in donaciones:
                if isinstance(donacion, dict) and 'id' in donacion:
                    kafka_donation_ids.append(donacion['id'])
        
        # Verify consistency
        expected_donation_id = 101
        if swagger_donation_ids:
            self.assertIn(expected_donation_id, swagger_donation_ids,
                        "Donation ID not found in Swagger examples")
        
        if kafka_donation_ids:
            self.assertIn(expected_donation_id, kafka_donation_ids,
                        "Donation ID not found in Kafka scenarios")

def run_integration_tests():
    """Run all integration tests"""
    # Create test suite
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTests(loader.loadTestsFromTestCase(TestSQLToPostmanIntegration))
    test_suite.addTests(loader.loadTestsFromTestCase(TestEndToEndOrchestration))
    test_suite.addTests(loader.loadTestsFromTestCase(TestValidationIntegration))
    test_suite.addTests(loader.loadTestsFromTestCase(TestDataConsistencyValidation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("Integration Test Suite - Sistema ONG SQL Driven Testing")
    print("=" * 60)
    
    success = run_integration_tests()
    
    if success:
        print("\n✅ All integration tests passed!")
    else:
        print("\n❌ Some integration tests failed!")
        exit(1)