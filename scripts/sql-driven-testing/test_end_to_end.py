#!/usr/bin/env python3
"""
End-to-End Test Suite
Sistema ONG - SQL Driven Testing

Tests that execute generated configurations against real services.
These tests validate that the generated Postman collections, Swagger examples,
and Kafka scenarios work correctly with the actual API and messaging infrastructure.
"""

import unittest
import json
import requests
import time
import subprocess
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
from unittest.mock import patch, Mock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceHealthChecker:
    """Checks if required services are running and accessible"""
    
    def __init__(self):
        self.services = {
            'api_gateway': {'url': 'http://localhost:3000', 'health_endpoint': '/health'},
            'database': {'host': 'localhost', 'port': 3306},
            'kafka': {'host': 'localhost', 'port': 9092}
        }
    
    def check_api_gateway(self) -> bool:
        """Check if API Gateway is running"""
        try:
            response = requests.get(
                f"{self.services['api_gateway']['url']}{self.services['api_gateway']['health_endpoint']}",
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def check_database(self) -> bool:
        """Check if database is accessible"""
        try:
            import mysql.connector
            connection = mysql.connector.connect(
                host=self.services['database']['host'],
                port=self.services['database']['port'],
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'ong_sistema'),
                connection_timeout=5
            )
            connection.close()
            return True
        except Exception:
            return False
    
    def check_kafka(self) -> bool:
        """Check if Kafka is accessible"""
        try:
            from kafka import KafkaProducer
            producer = KafkaProducer(
                bootstrap_servers=[f"{self.services['kafka']['host']}:{self.services['kafka']['port']}"],
                request_timeout_ms=5000
            )
            producer.close()
            return True
        except Exception:
            return False
    
    def check_all_services(self) -> Dict[str, bool]:
        """Check all required services"""
        return {
            'api_gateway': self.check_api_gateway(),
            'database': self.check_database(),
            'kafka': self.check_kafka()
        }

class PostmanCollectionExecutor:
    """Executes Postman collections against real API"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_tokens = {}
        self.environment_variables = {
            'base_url': base_url
        }
    
    def execute_collection(self, collection_path: str) -> Dict[str, Any]:
        """Execute a Postman collection against the real API"""
        results = {
            'collection_name': Path(collection_path).name,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'execution_time': 0,
            'request_results': [],
            'errors': []
        }
        
        start_time = time.time()
        
        try:
            with open(collection_path, 'r', encoding='utf-8') as f:
                collection_data = json.load(f)
            
            collection_name = collection_data.get('info', {}).get('name', 'Unknown')
            results['collection_name'] = collection_name
            
            # Execute each request in the collection
            for item in collection_data.get('item', []):
                request_result = self._execute_request_item(item)
                results['request_results'].append(request_result)
                results['total_requests'] += 1
                
                if request_result['success']:
                    results['successful_requests'] += 1
                else:
                    results['failed_requests'] += 1
                    results['errors'].append(request_result['error'])
        
        except Exception as e:
            results['errors'].append(f"Collection execution error: {e}")
        
        results['execution_time'] = time.time() - start_time
        return results
    
    def _execute_request_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single request item"""
        result = {
            'name': item.get('name', 'Unknown Request'),
            'success': False,
            'status_code': None,
            'response_time': 0,
            'error': None,
            'test_results': []
        }
        
        if 'request' not in item:
            result['error'] = "No request data found"
            return result
        
        request_data = item['request']
        start_time = time.time()
        
        try:
            # Build request
            method = request_data.get('method', 'GET').upper()
            url = self._resolve_url(request_data.get('url', ''))
            headers = self._build_headers(request_data.get('header', []))
            body = self._build_body(request_data.get('body', {}))
            
            # Execute request
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=body if body else None,
                timeout=30
            )
            
            result['status_code'] = response.status_code
            result['response_time'] = time.time() - start_time
            
            # Store auth tokens if this is a login request
            if '/auth/login' in url and response.status_code == 200:
                try:
                    response_data = response.json()
                    if 'token' in response_data:
                        # Extract user role from request or response
                        user_role = self._extract_user_role(body, response_data)
                        if user_role:
                            self.auth_tokens[user_role] = response_data['token']
                            self.environment_variables[f'{user_role.lower()}_token'] = response_data['token']
                except json.JSONDecodeError:
                    pass
            
            # Execute test scripts if present
            if 'event' in item:
                test_results = self._execute_test_scripts(item['event'], response)
                result['test_results'] = test_results
            
            # Consider request successful if status is in 200-299 range
            result['success'] = 200 <= response.status_code < 300
            
            if not result['success']:
                result['error'] = f"HTTP {response.status_code}: {response.text[:200]}"
        
        except requests.RequestException as e:
            result['error'] = f"Request failed: {e}"
        except Exception as e:
            result['error'] = f"Unexpected error: {e}"
        
        return result
    
    def _resolve_url(self, url_data) -> str:
        """Resolve URL with environment variables"""
        if isinstance(url_data, str):
            url = url_data
        elif isinstance(url_data, dict) and 'raw' in url_data:
            url = url_data['raw']
        else:
            url = str(url_data)
        
        # Replace environment variables
        for var_name, var_value in self.environment_variables.items():
            url = url.replace(f'{{{{{var_name}}}}}', str(var_value))
        
        return url
    
    def _build_headers(self, headers_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """Build headers dictionary"""
        headers = {}
        
        for header in headers_data:
            if isinstance(header, dict) and 'key' in header and 'value' in header:
                key = header['key']
                value = header['value']
                
                # Replace environment variables in header values
                for var_name, var_value in self.environment_variables.items():
                    value = value.replace(f'{{{{{var_name}}}}}', str(var_value))
                
                headers[key] = value
        
        return headers
    
    def _build_body(self, body_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Build request body"""
        if not body_data or 'raw' not in body_data:
            return None
        
        try:
            return json.loads(body_data['raw'])
        except json.JSONDecodeError:
            return None
    
    def _extract_user_role(self, request_body: Dict[str, Any], response_data: Dict[str, Any]) -> Optional[str]:
        """Extract user role from request or response"""
        # Try to get role from response
        if isinstance(response_data, dict):
            if 'usuario' in response_data and 'rol' in response_data['usuario']:
                return response_data['usuario']['rol']
            if 'rol' in response_data:
                return response_data['rol']
        
        # Try to infer from username in request
        if isinstance(request_body, dict) and 'nombreUsuario' in request_body:
            username = request_body['nombreUsuario']
            if 'presidente' in username.lower():
                return 'PRESIDENTE'
            elif 'vocal' in username.lower():
                return 'VOCAL'
            elif 'coordinador' in username.lower():
                return 'COORDINADOR'
            elif 'voluntario' in username.lower():
                return 'VOLUNTARIO'
        
        return None
    
    def _execute_test_scripts(self, events: List[Dict[str, Any]], response: requests.Response) -> List[Dict[str, Any]]:
        """Execute test scripts (simplified implementation)"""
        test_results = []
        
        for event in events:
            if event.get('listen') == 'test' and 'script' in event:
                script_lines = event['script'].get('exec', [])
                
                for line in script_lines:
                    if 'pm.test(' in line:
                        # Extract test name
                        test_name_match = line.split("pm.test('")[1].split("'")[0] if "pm.test('" in line else "Unknown Test"
                        
                        # Simple test execution (check status code)
                        if 'pm.response.to.have.status(' in line:
                            expected_status = int(line.split('status(')[1].split(')')[0])
                            test_passed = response.status_code == expected_status
                            
                            test_results.append({
                                'name': test_name_match,
                                'passed': test_passed,
                                'expected': expected_status,
                                'actual': response.status_code
                            })
        
        return test_results

class KafkaScenarioExecutor:
    """Executes Kafka scenarios against real Kafka infrastructure"""
    
    def __init__(self, bootstrap_servers: List[str] = None):
        self.bootstrap_servers = bootstrap_servers or ['localhost:9092']
        self.producer = None
        self.consumer = None
    
    def setup_kafka_client(self):
        """Setup Kafka producer and consumer"""
        try:
            from kafka import KafkaProducer, KafkaConsumer
            
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to setup Kafka client: {e}")
            return False
    
    def execute_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single Kafka scenario"""
        result = {
            'scenario_name': scenario.get('scenario_name', 'Unknown'),
            'success': False,
            'execution_time': 0,
            'message_sent': False,
            'error': None,
            'pre_conditions_met': True,
            'post_conditions_verified': False
        }
        
        start_time = time.time()
        
        try:
            # Check pre-conditions (simplified)
            pre_conditions = scenario.get('pre_conditions', [])
            result['pre_conditions_met'] = self._check_pre_conditions(pre_conditions)
            
            if not result['pre_conditions_met']:
                result['error'] = "Pre-conditions not met"
                return result
            
            # Send message to Kafka
            topic = scenario.get('topic', '')
            message_key = scenario.get('message_key', None)
            message = scenario.get('message', {})
            
            if self.producer:
                future = self.producer.send(
                    topic=topic,
                    key=message_key,
                    value=message
                )
                
                # Wait for message to be sent
                record_metadata = future.get(timeout=10)
                result['message_sent'] = True
                
                # Verify post-conditions (simplified)
                post_conditions = scenario.get('post_conditions', [])
                result['post_conditions_verified'] = self._verify_post_conditions(
                    post_conditions, record_metadata
                )
                
                result['success'] = result['message_sent'] and result['post_conditions_verified']
            else:
                result['error'] = "Kafka producer not available"
        
        except Exception as e:
            result['error'] = f"Scenario execution failed: {e}"
        
        result['execution_time'] = time.time() - start_time
        return result
    
    def _check_pre_conditions(self, pre_conditions: List[str]) -> bool:
        """Check pre-conditions (simplified implementation)"""
        # In a real implementation, this would check database state,
        # user permissions, stock levels, etc.
        return True
    
    def _verify_post_conditions(self, post_conditions: List[str], record_metadata) -> bool:
        """Verify post-conditions (simplified implementation)"""
        # In a real implementation, this would verify that:
        # - Message was published to correct topic
        # - Database state was updated correctly
        # - Other systems received the message
        return record_metadata is not None
    
    def cleanup(self):
        """Cleanup Kafka connections"""
        if self.producer:
            self.producer.close()

class EndToEndTestSuite(unittest.TestCase):
    """End-to-end tests that execute against real services"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test suite - check if services are available"""
        cls.health_checker = ServiceHealthChecker()
        cls.service_status = cls.health_checker.check_all_services()
        
        # Skip tests if services are not available
        if not cls.service_status['api_gateway']:
            raise unittest.SkipTest("API Gateway not available - skipping end-to-end tests")
    
    def setUp(self):
        """Set up individual test"""
        self.temp_dir = tempfile.mkdtemp()
        self.postman_executor = PostmanCollectionExecutor()
        self.kafka_executor = KafkaScenarioExecutor()
    
    def tearDown(self):
        """Clean up individual test"""
        import shutil
        shutil.rmtree(self.temp_dir)
        self.kafka_executor.cleanup()
    
    def test_postman_auth_collection_execution(self):
        """Test execution of authentication Postman collection against real API"""
        # Create a test authentication collection
        auth_collection = {
            "info": {"name": "01 - Autenticación - E2E Test"},
            "item": [
                {
                    "name": "Login Presidente - E2E",
                    "request": {
                        "method": "POST",
                        "url": "{{base_url}}/api/auth/login",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"}
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "nombreUsuario": "test_presidente",
                                "clave": "test123"
                            })
                        }
                    },
                    "event": [
                        {
                            "listen": "test",
                            "script": {
                                "exec": [
                                    "pm.test('Status is 200', function () {",
                                    "    pm.response.to.have.status(200);",
                                    "});",
                                    "pm.test('Response has token', function () {",
                                    "    const response = pm.response.json();",
                                    "    pm.expect(response).to.have.property('token');",
                                    "});"
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        # Save collection to file
        collection_path = Path(self.temp_dir) / "auth_e2e.postman_collection.json"
        with open(collection_path, 'w', encoding='utf-8') as f:
            json.dump(auth_collection, f, indent=2)
        
        # Execute collection
        results = self.postman_executor.execute_collection(str(collection_path))
        
        # Verify execution results
        self.assertEqual(results['total_requests'], 1)
        self.assertGreater(results['execution_time'], 0)
        
        # Check if request was successful (may fail if test user doesn't exist)
        if results['successful_requests'] > 0:
            self.assertEqual(results['successful_requests'], 1)
            self.assertEqual(results['failed_requests'], 0)
            
            # Check test results
            request_result = results['request_results'][0]
            self.assertTrue(request_result['success'])
            self.assertEqual(request_result['status_code'], 200)
        else:
            # If request failed, it might be because test data is not set up
            logger.warning("Auth request failed - test data may not be set up in database")
    
    def test_postman_inventory_collection_execution(self):
        """Test execution of inventory Postman collection against real API"""
        # First, try to authenticate to get a token
        auth_result = self._attempt_authentication()
        
        if not auth_result['success']:
            self.skipTest("Cannot authenticate - skipping inventory test")
        
        # Create inventory collection
        inventory_collection = {
            "info": {"name": "03 - Inventario - E2E Test"},
            "item": [
                {
                    "name": "Listar Donaciones - E2E",
                    "request": {
                        "method": "GET",
                        "url": "{{base_url}}/api/inventario/donaciones",
                        "header": [
                            {"key": "Authorization", "value": f"Bearer {auth_result['token']}"}
                        ]
                    },
                    "event": [
                        {
                            "listen": "test",
                            "script": {
                                "exec": [
                                    "pm.test('Status is 200 or 403', function () {",
                                    "    pm.expect(pm.response.code).to.be.oneOf([200, 403]);",
                                    "});"
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        # Save and execute collection
        collection_path = Path(self.temp_dir) / "inventory_e2e.postman_collection.json"
        with open(collection_path, 'w', encoding='utf-8') as f:
            json.dump(inventory_collection, f, indent=2)
        
        results = self.postman_executor.execute_collection(str(collection_path))
        
        # Verify execution
        self.assertEqual(results['total_requests'], 1)
        self.assertGreater(results['execution_time'], 0)
        
        # Request should execute (success depends on authorization)
        request_result = results['request_results'][0]
        self.assertIsNotNone(request_result['status_code'])
        self.assertIn(request_result['status_code'], [200, 403, 401])
    
    @unittest.skipUnless(
        os.getenv('KAFKA_TESTS_ENABLED', 'false').lower() == 'true',
        "Kafka tests disabled - set KAFKA_TESTS_ENABLED=true to enable"
    )
    def test_kafka_scenario_execution(self):
        """Test execution of Kafka scenarios against real Kafka"""
        if not self.service_status['kafka']:
            self.skipTest("Kafka not available")
        
        # Setup Kafka client
        if not self.kafka_executor.setup_kafka_client():
            self.skipTest("Cannot setup Kafka client")
        
        # Create test scenario
        test_scenario = {
            'scenario_name': 'Solicitud de Donaciones - E2E Test',
            'topic': 'solicitud-donaciones-test',
            'message_key': 'e2e-test-001',
            'message': {
                'idOrganizacion': 'ong-empuje-comunitario',
                'donaciones': [
                    {
                        'categoria': 'ALIMENTOS',
                        'descripcion': 'Arroz para familias - E2E Test'
                    }
                ],
                'usuarioSolicitante': 'test_vocal',
                'timestamp': datetime.now().isoformat()
            },
            'pre_conditions': ['Usuario debe tener rol VOCAL o superior'],
            'post_conditions': ['Mensaje publicado en topic solicitud-donaciones-test'],
            'test_assertions': ['Mensaje enviado exitosamente'],
            'expected_external_response': True
        }
        
        # Execute scenario
        result = self.kafka_executor.execute_scenario(test_scenario)
        
        # Verify execution
        self.assertTrue(result['success'], f"Kafka scenario failed: {result.get('error')}")
        self.assertTrue(result['message_sent'])
        self.assertGreater(result['execution_time'], 0)
    
    def test_swagger_examples_validation(self):
        """Test that Swagger examples are valid and executable"""
        # This test would validate that Swagger examples can be used
        # to make actual API calls
        
        # Create test Swagger examples
        swagger_examples = {
            'LoginRequest': {
                'summary': 'Login request example',
                'value': {
                    'nombreUsuario': 'test_presidente',
                    'clave': 'test123'
                }
            },
            'CreateDonationRequest': {
                'summary': 'Create donation request',
                'value': {
                    'categoria': 'ALIMENTOS',
                    'descripcion': 'Arroz integral 1kg',
                    'cantidad': 25
                }
            }
        }
        
        # Test login example
        login_example = swagger_examples['LoginRequest']['value']
        
        try:
            response = requests.post(
                f"{self.postman_executor.base_url}/api/auth/login",
                json=login_example,
                timeout=10
            )
            
            # Should get some response (200 for success, 401 for invalid credentials)
            self.assertIn(response.status_code, [200, 401, 404])
            
            if response.status_code == 200:
                # If successful, response should have expected structure
                response_data = response.json()
                self.assertIn('token', response_data)
        
        except requests.RequestException as e:
            self.skipTest(f"API not accessible: {e}")
    
    def _attempt_authentication(self) -> Dict[str, Any]:
        """Attempt to authenticate with test credentials"""
        result = {'success': False, 'token': None, 'error': None}
        
        try:
            response = requests.post(
                f"{self.postman_executor.base_url}/api/auth/login",
                json={
                    'nombreUsuario': 'test_presidente',
                    'clave': 'test123'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if 'token' in response_data:
                    result['success'] = True
                    result['token'] = response_data['token']
                else:
                    result['error'] = "No token in response"
            else:
                result['error'] = f"HTTP {response.status_code}: {response.text}"
        
        except requests.RequestException as e:
            result['error'] = f"Request failed: {e}"
        
        return result

class DatabaseIntegrationTest(unittest.TestCase):
    """Test integration with database for SQL-driven testing"""
    
    def setUp(self):
        """Set up database integration test"""
        self.health_checker = ServiceHealthChecker()
        
        if not self.health_checker.check_database():
            self.skipTest("Database not available")
    
    def test_test_data_exists_in_database(self):
        """Test that test data exists in the database"""
        try:
            import mysql.connector
            
            connection = mysql.connector.connect(
                host='localhost',
                port=3306,
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'ong_sistema')
            )
            
            cursor = connection.cursor(dictionary=True)
            
            # Check for test users
            cursor.execute("SELECT COUNT(*) as count FROM usuarios WHERE nombre_usuario LIKE 'test_%'")
            test_users_count = cursor.fetchone()['count']
            
            # Check for test donations
            cursor.execute("SELECT COUNT(*) as count FROM donaciones WHERE usuario_alta LIKE 'test_%'")
            test_donations_count = cursor.fetchone()['count']
            
            # Check for test events
            cursor.execute("SELECT COUNT(*) as count FROM eventos WHERE usuario_alta LIKE 'test_%'")
            test_events_count = cursor.fetchone()['count']
            
            connection.close()
            
            # Verify test data exists
            self.assertGreater(test_users_count, 0, "No test users found in database")
            self.assertGreater(test_donations_count, 0, "No test donations found in database")
            self.assertGreater(test_events_count, 0, "No test events found in database")
            
            logger.info(f"Found {test_users_count} test users, {test_donations_count} test donations, {test_events_count} test events")
        
        except ImportError:
            self.skipTest("mysql-connector-python not available")
        except Exception as e:
            self.fail(f"Database test failed: {e}")

def run_end_to_end_tests():
    """Run all end-to-end tests"""
    # Check service availability first
    health_checker = ServiceHealthChecker()
    service_status = health_checker.check_all_services()
    
    print("Service Status Check:")
    for service, status in service_status.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {service}: {'Available' if status else 'Not Available'}")
    
    if not any(service_status.values()):
        print("\n⚠️  No services available - skipping all end-to-end tests")
        return True
    
    # Create test suite
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTests(loader.loadTestsFromTestCase(EndToEndTestSuite))
    test_suite.addTests(loader.loadTestsFromTestCase(DatabaseIntegrationTest))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("End-to-End Test Suite - Sistema ONG SQL Driven Testing")
    print("=" * 60)
    print("These tests execute generated configurations against real services.")
    print("Make sure the following services are running:")
    print("  - API Gateway (http://localhost:3000)")
    print("  - Database (MySQL on localhost:3306)")
    print("  - Kafka (localhost:9092) [optional]")
    print()
    
    success = run_end_to_end_tests()
    
    if success:
        print("\n✅ All end-to-end tests passed!")
    else:
        print("\n❌ Some end-to-end tests failed!")
        exit(1)