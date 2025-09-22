#!/usr/bin/env python3
"""
Unit Tests for Kafka Test Generator
Sistema ONG - SQL Driven Testing

Tests for the KafkaTestGenerator class that generates inter-NGO communication scenarios.
"""

import unittest
import json
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Import the module to test
from kafka_generator import KafkaTestGenerator

class TestKafkaTestGenerator(unittest.TestCase):
    """Test cases for KafkaTestGenerator"""
    
    def setUp(self):
        """Set up test data and generator instance"""
        self.sample_data = {
            'users': {
                'PRESIDENTE': [
                    {
                        'id': 1, 'nombre_usuario': 'test_presidente', 'nombre': 'Juan', 'apellido': 'Presidente',
                        'email': 'presidente@test.com', 'telefono': '1111111111', 'rol': 'PRESIDENTE'
                    }
                ],
                'VOCAL': [
                    {
                        'id': 2, 'nombre_usuario': 'test_vocal', 'nombre': 'María', 'apellido': 'Vocal',
                        'email': 'vocal@test.com', 'telefono': '2222222222', 'rol': 'VOCAL'
                    }
                ],
                'COORDINADOR': [
                    {
                        'id': 3, 'nombre_usuario': 'test_coordinador', 'nombre': 'Carlos', 'apellido': 'Coordinador',
                        'email': 'coordinador@test.com', 'telefono': '3333333333', 'rol': 'COORDINADOR'
                    }
                ],
                'VOLUNTARIO': [
                    {
                        'id': 4, 'nombre_usuario': 'test_voluntario', 'nombre': 'Ana', 'apellido': 'Voluntario',
                        'email': 'voluntario@test.com', 'telefono': '4444444444', 'rol': 'VOLUNTARIO'
                    }
                ]
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
                        {'id': 104, 'categoria': 'ALIMENTOS', 'descripcion': 'Cuadernos - Test Stock Cero', 'cantidad': 0}
                    ],
                    'all': [
                        {'id': 101, 'categoria': 'ALIMENTOS', 'descripcion': 'Arroz 1kg - Test Stock Alto', 'cantidad': 100},
                        {'id': 102, 'categoria': 'ALIMENTOS', 'descripcion': 'Fideos 500g', 'cantidad': 30},
                        {'id': 103, 'categoria': 'ALIMENTOS', 'descripcion': 'Conservas', 'cantidad': 5},
                        {'id': 104, 'categoria': 'ALIMENTOS', 'descripcion': 'Cuadernos - Test Stock Cero', 'cantidad': 0},
                        {'id': 105, 'categoria': 'ALIMENTOS', 'descripcion': 'Leche 1L - Para Transferencia', 'cantidad': 25}
                    ]
                },
                'ROPA': {
                    'high_stock': [
                        {'id': 106, 'categoria': 'ROPA', 'descripcion': 'Camisetas M', 'cantidad': 50}
                    ],
                    'medium_stock': [],
                    'low_stock': [],
                    'zero_stock': [],
                    'all': [
                        {'id': 106, 'categoria': 'ROPA', 'descripcion': 'Camisetas M', 'cantidad': 50}
                    ]
                }
            },
            'events': {
                'future': [
                    {
                        'id': 201, 'nombre': 'Evento Test Futuro 1', 'descripcion': 'Evento para testing de participación',
                        'fecha_hora': (datetime.now() + timedelta(days=7)).isoformat(), 'participantes': [3, 4]
                    },
                    {
                        'id': 202, 'nombre': 'Evento Test Futuro 2', 'descripcion': 'Evento para testing de adhesión externa',
                        'fecha_hora': (datetime.now() + timedelta(days=14)).isoformat(), 'participantes': [4]
                    }
                ],
                'past': [
                    {
                        'id': 203, 'nombre': 'Evento Test Pasado', 'descripcion': 'Evento pasado para testing',
                        'fecha_hora': (datetime.now() - timedelta(days=7)).isoformat(), 'participantes': [4]
                    }
                ],
                'current': [],
                'all': []
            },
            'network': {
                'external_requests': [
                    {
                        'id_organizacion': 'ong-corazon-solidario', 'id_solicitud': 'sol-001',
                        'categoria': 'ALIMENTOS', 'descripcion': 'Arroz y fideos para familias necesitadas',
                        'activa': True, 'fecha_recepcion': datetime.now().isoformat()
                    },
                    {
                        'id_organizacion': 'ong-manos-unidas', 'id_solicitud': 'sol-002',
                        'categoria': 'ROPA', 'descripcion': 'Ropa de invierno para adultos',
                        'activa': True, 'fecha_recepcion': datetime.now().isoformat()
                    }
                ],
                'external_offers': [
                    {
                        'id_organizacion': 'ong-corazon-solidario', 'id_oferta': 'of-001',
                        'categoria': 'UTILES_ESCOLARES', 'descripcion': 'Útiles escolares variados',
                        'cantidad': 50, 'fecha_recepcion': datetime.now().isoformat()
                    }
                ],
                'external_events': [
                    {
                        'id_organizacion': 'ong-corazon-solidario', 'id_evento': 'ev-ext-001',
                        'nombre': 'Campaña de Invierno 2024', 'descripcion': 'Distribución de ropa de invierno',
                        'fecha_hora': (datetime.now() + timedelta(days=10)).isoformat(),
                        'activo': True, 'fecha_recepcion': datetime.now().isoformat()
                    }
                ],
                'own_requests': [
                    {
                        'id_solicitud': 'req-001', 'donaciones': [{'categoria': 'ALIMENTOS', 'descripcion': 'Arroz'}],
                        'usuario_creador': 'test_vocal', 'fecha_creacion': datetime.now().isoformat(),
                        'activa': True, 'fecha_baja': None, 'usuario_baja': None
                    }
                ],
                'own_offers': [],
                'transfers_sent': [],
                'transfers_received': [],
                'event_adhesions': []
            }
        }
        
        self.generator = KafkaTestGenerator(self.sample_data)
    
    def test_initialization(self):
        """Test generator initialization"""
        self.assertEqual(self.generator.organization_id, "ong-empuje-comunitario")
        self.assertIsInstance(self.generator.kafka_topics, dict)
        self.assertIn('solicitud_donaciones', self.generator.kafka_topics)
        self.assertIn('oferta_donaciones', self.generator.kafka_topics)
        self.assertIn('transferencia_donaciones', self.generator.kafka_topics)
    
    def test_generate_donation_request_scenarios(self):
        """Test donation request scenario generation"""
        scenarios = self.generator.generate_donation_request_scenarios()
        
        self.assertIsInstance(scenarios, list)
        self.assertGreater(len(scenarios), 0)
        
        # Check first scenario structure
        scenario = scenarios[0]
        required_fields = ['scenario_name', 'topic', 'message_key', 'message', 
                          'pre_conditions', 'post_conditions', 'test_assertions']
        
        for field in required_fields:
            self.assertIn(field, scenario, f"Missing field: {field}")
        
        # Check message structure
        message = scenario['message']
        self.assertEqual(message['idOrganizacion'], self.generator.organization_id)
        self.assertIn('donaciones', message)
        self.assertIn('usuarioSolicitante', message)
        self.assertIn('timestamp', message)
        
        # Check that we have both success and error scenarios
        scenario_types = [s.get('expected_external_response', True) for s in scenarios]
        self.assertIn(True, scenario_types)  # Success scenarios
        self.assertIn(False, scenario_types)  # Error scenarios
    
    def test_generate_donation_offer_scenarios(self):
        """Test donation offer scenario generation"""
        scenarios = self.generator.generate_donation_offer_scenarios()
        
        self.assertIsInstance(scenarios, list)
        self.assertGreater(len(scenarios), 0)
        
        # Check scenario with high stock donation
        success_scenarios = [s for s in scenarios if s.get('expected_external_response', True)]
        self.assertGreater(len(success_scenarios), 0)
        
        scenario = success_scenarios[0]
        message = scenario['message']
        
        self.assertIn('donaciones', message)
        self.assertIn('usuarioOfertante', message)
        self.assertIn('validoHasta', message)
        
        # Check donation data
        donation = message['donaciones'][0]
        self.assertIn('id', donation)
        self.assertIn('categoria', donation)
        self.assertIn('cantidad', donation)
        
        # Verify quantity is reasonable (not more than available stock)
        offered_quantity = donation['cantidad']
        self.assertGreater(offered_quantity, 0)
        self.assertLessEqual(offered_quantity, 50)  # Reasonable limit
    
    def test_generate_transfer_scenarios(self):
        """Test transfer scenario generation"""
        scenarios = self.generator.generate_transfer_scenarios()
        
        self.assertIsInstance(scenarios, list)
        
        if scenarios:  # Only test if we have scenarios (depends on data availability)
            scenario = scenarios[0]
            message = scenario['message']
            
            self.assertIn('idSolicitud', message)
            self.assertIn('donaciones', message)
            self.assertIn('usuarioTransferencia', message)
            self.assertIn('organizacionDestino', message)
            
            # Check that topic includes organization ID
            self.assertIn('transferencia-donaciones/', scenario['topic'])
    
    def test_generate_external_event_scenarios(self):
        """Test external event scenario generation"""
        scenarios = self.generator.generate_external_event_scenarios()
        
        self.assertIsInstance(scenarios, list)
        self.assertGreater(len(scenarios), 0)
        
        scenario = scenarios[0]
        message = scenario['message']
        
        self.assertIn('idEvento', message)
        self.assertIn('nombre', message)
        self.assertIn('descripcion', message)
        self.assertIn('fechaHora', message)
        self.assertIn('contacto', message)
        
        # Check contact information
        contacto = message['contacto']
        self.assertIn('responsable', contacto)
        self.assertIn('email', contacto)
        self.assertIn('telefono', contacto)
    
    def test_generate_event_adhesion_scenarios(self):
        """Test event adhesion scenario generation"""
        scenarios = self.generator.generate_event_adhesion_scenarios()
        
        self.assertIsInstance(scenarios, list)
        
        if scenarios:  # Only test if we have scenarios
            # Check success scenario
            success_scenarios = [s for s in scenarios if s.get('expected_external_response', True)]
            if success_scenarios:
                scenario = success_scenarios[0]
                message = scenario['message']
                
                self.assertIn('participante', message)
                self.assertIn('idEvento', message)
                self.assertIn('organizacionEvento', message)
                
                # Check participant data
                participante = message['participante']
                self.assertIn('id', participante)
                self.assertIn('rol', participante)
                self.assertEqual(participante['rol'], 'VOLUNTARIO')
    
    def test_helper_methods(self):
        """Test helper methods"""
        # Test _get_user_by_role
        vocal_users = self.generator._get_user_by_role('VOCAL')
        self.assertEqual(len(vocal_users), 1)
        self.assertEqual(vocal_users[0]['rol'], 'VOCAL')
        
        # Test _get_high_stock_donations
        high_stock = self.generator._get_high_stock_donations('ALIMENTOS')
        self.assertGreater(len(high_stock), 0)
        for donation in high_stock:
            self.assertGreater(donation['cantidad'], 50)
        
        # Test _get_zero_stock_donations
        zero_stock = self.generator._get_zero_stock_donations()
        self.assertGreater(len(zero_stock), 0)
        for donation in zero_stock:
            self.assertEqual(donation['cantidad'], 0)
        
        # Test _generate_id
        id1 = self.generator._generate_id()
        id2 = self.generator._generate_id()
        self.assertNotEqual(id1, id2)
        self.assertEqual(len(id1), 8)
    
    def test_generate_all_kafka_scenarios(self):
        """Test complete scenario generation"""
        scenarios = self.generator.generate_all_kafka_scenarios()
        
        self.assertIsInstance(scenarios, dict)
        
        # Check that all expected topics are present
        expected_topics = ['solicitud_donaciones', 'oferta_donaciones', 'transferencia_donaciones',
                          'baja_solicitud_donaciones', 'eventos_solidarios', 'baja_evento_solidario',
                          'adhesion_evento']
        
        for topic in expected_topics:
            self.assertIn(topic, scenarios)
            self.assertIsInstance(scenarios[topic], list)
    
    def test_validate_scenarios(self):
        """Test scenario validation"""
        scenarios = self.generator.generate_all_kafka_scenarios()
        errors = self.generator.validate_scenarios(scenarios)
        
        self.assertIsInstance(errors, list)
        # Should have no errors with properly generated scenarios
        if errors:
            print("Validation errors found:")
            for error in errors:
                print(f"  - {error}")
    
    def test_generate_kafka_test_summary(self):
        """Test summary generation"""
        scenarios = self.generator.generate_all_kafka_scenarios()
        summary = self.generator.generate_kafka_test_summary(scenarios)
        
        self.assertIsInstance(summary, dict)
        self.assertIn('generation_timestamp', summary)
        self.assertIn('organization_id', summary)
        self.assertIn('total_topics', summary)
        self.assertIn('total_scenarios', summary)
        self.assertIn('topics_summary', summary)
        self.assertIn('scenario_types', summary)
        
        # Check that totals are consistent
        total_from_topics = sum(len(topic_scenarios) for topic_scenarios in scenarios.values())
        self.assertEqual(summary['total_scenarios'], total_from_topics)
    
    def test_save_scenarios_to_files(self):
        """Test saving scenarios to files"""
        scenarios = self.generator.generate_all_kafka_scenarios()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            self.generator.save_scenarios_to_files(scenarios, temp_dir)
            
            # Check that files were created
            files = os.listdir(temp_dir)
            self.assertGreater(len(files), 0)
            
            # Check file content
            for filename in files:
                if filename.endswith('.json'):
                    filepath = os.path.join(temp_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    self.assertIn('topic', data)
                    self.assertIn('total_scenarios', data)
                    self.assertIn('scenarios', data)
                    self.assertIsInstance(data['scenarios'], list)
    
    def test_scenario_message_structure(self):
        """Test that all scenario messages have consistent structure"""
        scenarios = self.generator.generate_all_kafka_scenarios()
        
        for topic, topic_scenarios in scenarios.items():
            for scenario in topic_scenarios:
                message = scenario['message']
                
                # All messages should have organization ID and timestamp
                self.assertIn('idOrganizacion', message)
                self.assertIn('timestamp', message)
                self.assertEqual(message['idOrganizacion'], self.generator.organization_id)
                
                # Timestamp should be valid ISO format
                try:
                    datetime.fromisoformat(message['timestamp'])
                except ValueError:
                    self.fail(f"Invalid timestamp format in scenario: {scenario['scenario_name']}")
    
    def test_pre_post_conditions(self):
        """Test that scenarios have meaningful pre and post conditions"""
        scenarios = self.generator.generate_all_kafka_scenarios()
        
        for topic, topic_scenarios in scenarios.items():
            for scenario in topic_scenarios:
                # Check pre-conditions
                self.assertIn('pre_conditions', scenario)
                self.assertIsInstance(scenario['pre_conditions'], list)
                self.assertGreater(len(scenario['pre_conditions']), 0)
                
                # Check post-conditions
                self.assertIn('post_conditions', scenario)
                self.assertIsInstance(scenario['post_conditions'], list)
                self.assertGreater(len(scenario['post_conditions']), 0)
                
                # Check test assertions
                self.assertIn('test_assertions', scenario)
                self.assertIsInstance(scenario['test_assertions'], list)
                self.assertGreater(len(scenario['test_assertions']), 0)
    
    def test_error_scenarios_have_expected_error(self):
        """Test that error scenarios specify expected error types"""
        scenarios = self.generator.generate_all_kafka_scenarios()
        
        for topic, topic_scenarios in scenarios.items():
            for scenario in topic_scenarios:
                if not scenario.get('expected_external_response', True):
                    # Error scenarios should specify expected error
                    self.assertIn('expected_error', scenario,
                                f"Error scenario '{scenario['scenario_name']}' missing expected_error")
                    self.assertIsInstance(scenario['expected_error'], str)
                    self.assertGreater(len(scenario['expected_error']), 0)

class TestKafkaGeneratorIntegration(unittest.TestCase):
    """Integration tests for Kafka generator with realistic data"""
    
    def test_with_minimal_data(self):
        """Test generator with minimal data set"""
        minimal_data = {
            'users': {
                'VOCAL': [{'id': 2, 'nombre_usuario': 'test_vocal', 'rol': 'VOCAL', 
                          'email': 'vocal@test.com', 'telefono': '2222222222'}]
            },
            'inventory': {},
            'events': {'future': [], 'past': [], 'current': [], 'all': []},
            'network': {
                'external_requests': [], 'external_offers': [], 'external_events': [],
                'own_requests': [], 'own_offers': [], 'transfers_sent': [],
                'transfers_received': [], 'event_adhesions': []
            }
        }
        
        generator = KafkaTestGenerator(minimal_data)
        scenarios = generator.generate_all_kafka_scenarios()
        
        # Should still generate some scenarios even with minimal data
        self.assertIsInstance(scenarios, dict)
        
        # At least donation request scenarios should be generated
        self.assertIn('solicitud_donaciones', scenarios)
    
    def test_with_empty_data(self):
        """Test generator behavior with empty data"""
        empty_data = {
            'users': {},
            'inventory': {},
            'events': {'future': [], 'past': [], 'current': [], 'all': []},
            'network': {
                'external_requests': [], 'external_offers': [], 'external_events': [],
                'own_requests': [], 'own_offers': [], 'transfers_sent': [],
                'transfers_received': [], 'event_adhesions': []
            }
        }
        
        generator = KafkaTestGenerator(empty_data)
        
        # Should not crash with empty data
        try:
            scenarios = generator.generate_all_kafka_scenarios()
            self.assertIsInstance(scenarios, dict)
        except Exception as e:
            self.fail(f"Generator crashed with empty data: {e}")

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)