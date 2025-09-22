#!/usr/bin/env python3
"""
Test suite for the Testing Orchestrator
Sistema ONG - SQL Driven Testing

This module tests the TestingOrchestrator functionality including
backup management, configuration validation, and generation coordination.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import os

from orchestrator import TestingOrchestrator, BackupManager, ConfigurationValidator

class TestBackupManager(unittest.TestCase):
    """Test cases for BackupManager"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.backup_manager = BackupManager(self.temp_dir)
        
        # Create some test files to backup
        self.test_postman_dir = Path(self.temp_dir) / "test_postman"
        self.test_postman_dir.mkdir(parents=True)
        
        test_collection = self.test_postman_dir / "test.postman_collection.json"
        test_collection.write_text('{"info": {"name": "Test Collection"}}')
        
        self.test_swagger_file = Path(self.temp_dir) / "swagger.js"
        self.test_swagger_file.write_text('module.exports = { examples: {} };')
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_create_backups(self):
        """Test backup creation"""
        # Mock the actual paths to use our test files
        with patch('orchestrator.Path') as mock_path:
            def path_side_effect(path_str):
                if "postman" in path_str:
                    return self.test_postman_dir
                elif "swagger.js" in path_str:
                    return self.test_swagger_file
                else:
                    return Path(path_str)
            
            mock_path.side_effect = path_side_effect
            
            backup_path = self.backup_manager.create_backups()
            
            self.assertIsNotNone(backup_path)
            self.assertTrue(Path(backup_path).exists())
            
            # Check that manifest was created
            manifest_path = Path(backup_path) / "backup_manifest.json"
            self.assertTrue(manifest_path.exists())
            
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            self.assertIn('timestamp', manifest)
            self.assertIn('backed_up_files', manifest)
    
    def test_get_latest_backup_path(self):
        """Test getting latest backup path"""
        # Create a backup first
        backup_path = self.backup_manager.create_backups()
        
        latest_path = self.backup_manager.get_latest_backup_path()
        self.assertEqual(backup_path, latest_path)

class TestConfigurationValidator(unittest.TestCase):
    """Test cases for ConfigurationValidator"""
    
    def setUp(self):
        """Set up test environment"""
        self.validator = ConfigurationValidator()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_validate_postman_collections_success(self):
        """Test successful Postman collection validation"""
        # Create test collections
        postman_dir = Path(self.temp_dir) / "postman"
        postman_dir.mkdir(parents=True)
        
        collections = [
            '01-Autenticacion.postman_collection.json',
            '02-Usuarios.postman_collection.json',
            '03-Inventario.postman_collection.json',
            '04-Eventos.postman_collection.json',
            '05-Red-ONGs.postman_collection.json'
        ]
        
        collections_updated = {}
        for collection in collections:
            collection_path = postman_dir / collection
            collection_data = {
                "info": {"name": collection.replace('.postman_collection.json', '')},
                "item": [{"name": "Test Request"}]
            }
            collection_path.write_text(json.dumps(collection_data))
            collections_updated[collection] = str(collection_path)
        
        postman_results = {
            'collections_updated': collections_updated,
            'total_collections': len(collections)
        }
        
        with patch('orchestrator.Path') as mock_path:
            mock_path.side_effect = lambda p: Path(str(p).replace('api-gateway/postman', str(postman_dir)))
            
            result = self.validator.validate_postman_collections(postman_results)
            
            self.assertEqual(result['errors'], 0)
            self.assertEqual(result['collections_found'], 5)
    
    def test_validate_swagger_examples_success(self):
        """Test successful Swagger examples validation"""
        # Create test swagger file
        swagger_file = Path(self.temp_dir) / "swagger.js"
        swagger_content = """
        module.exports = {
            examples: {
                LoginRequest: { summary: 'Login example', value: {} },
                UsuariosList: { summary: 'Users list', value: [] },
                DonacionesList: { summary: 'Donations list', value: [] },
                EventosList: { summary: 'Events list', value: [] }
            },
            security: []
        };
        """
        swagger_file.write_text(swagger_content)
        
        swagger_results = {
            'total_examples': 4,
            'validation_passed': True
        }
        
        with patch('orchestrator.Path') as mock_path:
            mock_path.side_effect = lambda p: swagger_file if 'swagger.js' in str(p) else Path(p)
            
            result = self.validator.validate_swagger_examples(swagger_results)
            
            self.assertEqual(result['errors'], 0)
            self.assertEqual(result['examples_updated'], 4)
    
    def test_validate_kafka_scenarios_success(self):
        """Test successful Kafka scenarios validation"""
        kafka_results = {
            'scenarios_generated': {
                'solicitud_donaciones': [
                    {
                        'scenario_name': 'Test Scenario',
                        'topic': 'solicitud-donaciones',
                        'message': {'test': 'data'}
                    }
                ],
                'oferta_donaciones': [
                    {
                        'scenario_name': 'Test Offer',
                        'topic': 'oferta-donaciones',
                        'message': {'test': 'offer'}
                    }
                ]
            }
        }
        
        result = self.validator.validate_kafka_scenarios(kafka_results)
        
        self.assertEqual(result['errors'], 0)
        self.assertEqual(result['scenarios_generated'], 2)

class TestTestingOrchestrator(unittest.TestCase):
    """Test cases for TestingOrchestrator"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test configuration
        self.test_config = {
            'database': {
                'host': 'localhost',
                'port': 3306,
                'database': 'test_db',
                'user': 'test_user',
                'password': 'test_pass'
            },
            'generation': {
                'postman': True,
                'swagger': True,
                'kafka': True,
                'backup': True,
                'validate': True
            },
            'output': {
                'save_extracted_data': True,
                'extracted_data_file': f'{self.temp_dir}/extracted_data.json',
                'report_file': f'{self.temp_dir}/report.json'
            }
        }
        
        # Mock extracted data
        self.mock_extracted_data = {
            'users': {
                'PRESIDENTE': [{'id': 1, 'nombre_usuario': 'test_presidente', 'rol': 'PRESIDENTE'}],
                'VOCAL': [{'id': 2, 'nombre_usuario': 'test_vocal', 'rol': 'VOCAL'}],
                'COORDINADOR': [{'id': 3, 'nombre_usuario': 'test_coordinador', 'rol': 'COORDINADOR'}],
                'VOLUNTARIO': [{'id': 4, 'nombre_usuario': 'test_voluntario', 'rol': 'VOLUNTARIO'}]
            },
            'inventory': {
                'ALIMENTOS': {'all': [{'id': 1, 'categoria': 'ALIMENTOS', 'cantidad': 100}]},
                'ROPA': {'all': [{'id': 2, 'categoria': 'ROPA', 'cantidad': 50}]}
            },
            'events': {
                'all': [{'id': 1, 'nombre': 'Test Event'}],
                'future': [{'id': 1, 'nombre': 'Test Event'}],
                'past': []
            },
            'network': {
                'external_requests': [{'id_solicitud': 'req-1', 'categoria': 'ALIMENTOS'}],
                'external_offers': [],
                'external_events': []
            },
            'test_mappings': [
                {'endpoint': '/api/auth/login', 'test_category': 'authentication'},
                {'endpoint': '/api/usuarios', 'test_category': 'users'}
            ]
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    @patch('orchestrator.SQLDataExtractor')
    @patch('orchestrator.PostmanGenerator')
    @patch('orchestrator.SwaggerGenerator')
    @patch('orchestrator.KafkaTestGenerator')
    def test_generate_all_testing_configs_success(self, mock_kafka_gen, mock_swagger_gen, 
                                                 mock_postman_gen, mock_sql_extractor):
        """Test successful generation of all testing configurations"""
        
        # Mock the data extractor
        mock_extractor_instance = Mock()
        mock_extractor_instance.extract_test_data.return_value = self.mock_extracted_data
        mock_sql_extractor.return_value = mock_extractor_instance
        
        # Mock the generators
        mock_postman_instance = Mock()
        mock_postman_instance.generate_all_collections.return_value = {
            '01-Autenticacion.postman_collection.json': '/path/to/auth.json'
        }
        mock_postman_gen.return_value = mock_postman_instance
        
        mock_swagger_instance = Mock()
        mock_swagger_instance.update_swagger_examples.return_value = {
            'total_examples': 10,
            'validation_passed': True,
            'backup_created': True
        }
        mock_swagger_gen.return_value = mock_swagger_instance
        
        mock_kafka_instance = Mock()
        mock_kafka_instance.generate_all_kafka_scenarios.return_value = {
            'solicitud_donaciones': [{'scenario_name': 'Test'}]
        }
        mock_kafka_gen.return_value = mock_kafka_instance
        
        # Create orchestrator with test config
        with patch.object(TestingOrchestrator, '_load_config', return_value=self.test_config):
            orchestrator = TestingOrchestrator()
            
            # Mock backup manager
            orchestrator.backup_manager = Mock()
            orchestrator.backup_manager.create_backups.return_value = '/backup/path'
            
            # Generate configurations
            report = orchestrator.generate_all_testing_configs()
            
            # Verify success
            self.assertTrue(report.get('success', False))
            self.assertIn('generation_results', report)
            self.assertIn('validation_results', report)
            self.assertIn('summary', report)
            
            # Verify all generators were called
            mock_extractor_instance.extract_test_data.assert_called_once()
            mock_postman_instance.generate_all_collections.assert_called_once()
            mock_swagger_instance.update_swagger_examples.assert_called_once()
            mock_kafka_instance.generate_all_kafka_scenarios.assert_called_once()
    
    def test_load_config_from_env(self):
        """Test loading configuration from environment variables"""
        with patch.dict(os.environ, {
            'DB_HOST': 'test_host',
            'DB_PORT': '3307',
            'DB_NAME': 'test_db',
            'DB_USER': 'test_user',
            'DB_PASSWORD': 'test_pass'
        }):
            orchestrator = TestingOrchestrator()
            
            self.assertEqual(orchestrator.config['database']['host'], 'test_host')
            self.assertEqual(orchestrator.config['database']['port'], 3307)
            self.assertEqual(orchestrator.config['database']['database'], 'test_db')
    
    def test_validate_extracted_data_success(self):
        """Test successful validation of extracted data"""
        with patch.object(TestingOrchestrator, '_load_config', return_value=self.test_config):
            orchestrator = TestingOrchestrator()
            orchestrator.extracted_data = self.mock_extracted_data
            
            # Should not raise any exception
            orchestrator._validate_extracted_data()
    
    def test_validate_extracted_data_missing_users(self):
        """Test validation failure when users are missing"""
        with patch.object(TestingOrchestrator, '_load_config', return_value=self.test_config):
            orchestrator = TestingOrchestrator()
            orchestrator.extracted_data = {
                'users': {},  # Empty users
                'inventory': self.mock_extracted_data['inventory'],
                'events': self.mock_extracted_data['events'],
                'network': self.mock_extracted_data['network'],
                'test_mappings': self.mock_extracted_data['test_mappings']
            }
            
            with self.assertRaises(ValueError) as context:
                orchestrator._validate_extracted_data()
            
            self.assertIn('No test users found', str(context.exception))
    
    def test_get_generation_status(self):
        """Test getting generation status"""
        with patch.object(TestingOrchestrator, '_load_config', return_value=self.test_config):
            orchestrator = TestingOrchestrator()
            
            # Mock the status check methods
            orchestrator._check_postman_status = Mock(return_value={'collections_found': 5})
            orchestrator._check_swagger_status = Mock(return_value={'exists': True})
            orchestrator._check_kafka_status = Mock(return_value={'exists': True})
            orchestrator._check_backup_status = Mock(return_value={'total_backups': 3})
            
            status = orchestrator.get_generation_status()
            
            self.assertIn('timestamp', status)
            self.assertIn('postman', status)
            self.assertIn('swagger', status)
            self.assertIn('kafka', status)
            self.assertIn('backups', status)

class TestIntegration(unittest.TestCase):
    """Integration tests for the orchestrator system"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up integration test environment"""
        shutil.rmtree(self.temp_dir)
    
    @patch('orchestrator.SQLDataExtractor')
    def test_end_to_end_generation_flow(self, mock_sql_extractor):
        """Test the complete end-to-end generation flow"""
        
        # Mock data extractor with complete test data
        mock_extractor_instance = Mock()
        mock_extractor_instance.extract_test_data.return_value = {
            'users': {
                'PRESIDENTE': [{'id': 1, 'rol': 'PRESIDENTE'}],
                'VOCAL': [{'id': 2, 'rol': 'VOCAL'}],
                'COORDINADOR': [{'id': 3, 'rol': 'COORDINADOR'}],
                'VOLUNTARIO': [{'id': 4, 'rol': 'VOLUNTARIO'}]
            },
            'inventory': {'ALIMENTOS': {'all': [{'id': 1}]}},
            'events': {'all': [{'id': 1}], 'future': [], 'past': []},
            'network': {'external_requests': [], 'external_offers': [], 'external_events': []},
            'test_mappings': [{'endpoint': '/api/test', 'test_category': 'test'}]
        }
        mock_sql_extractor.return_value = mock_extractor_instance
        
        # Create test configuration
        test_config = {
            'database': {'host': 'localhost', 'port': 3306, 'database': 'test', 'user': 'test', 'password': 'test'},
            'generation': {'postman': True, 'swagger': False, 'kafka': False, 'backup': False, 'validate': True},
            'output': {
                'save_extracted_data': True,
                'extracted_data_file': f'{self.temp_dir}/data.json',
                'report_file': f'{self.temp_dir}/report.json'
            }
        }
        
        with patch.object(TestingOrchestrator, '_load_config', return_value=test_config):
            with patch('orchestrator.PostmanGenerator') as mock_postman_gen:
                mock_postman_instance = Mock()
                mock_postman_instance.generate_all_collections.return_value = {'test.json': '/path/test.json'}
                mock_postman_gen.return_value = mock_postman_instance
                
                orchestrator = TestingOrchestrator()
                
                # Run generation
                report = orchestrator.generate_all_testing_configs()
                
                # Verify results
                self.assertTrue(report.get('success', False))
                self.assertIn('postman', report['generation_results'])
                
                # Verify files were created
                self.assertTrue(Path(test_config['output']['extracted_data_file']).exists())
                self.assertTrue(Path(test_config['output']['report_file']).exists())

def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTests(loader.loadTestsFromTestCase(TestBackupManager))
    test_suite.addTests(loader.loadTestsFromTestCase(TestConfigurationValidator))
    test_suite.addTests(loader.loadTestsFromTestCase(TestTestingOrchestrator))
    test_suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("Running Testing Orchestrator Test Suite")
    print("=" * 50)
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        exit(1)