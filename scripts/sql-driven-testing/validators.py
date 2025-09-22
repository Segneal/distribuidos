#!/usr/bin/env python3
"""
Configuration Validators
Sistema ONG - SQL Driven Testing

Comprehensive validation system for all generated configurations.
Validates Postman collections, Swagger examples, and Kafka scenarios.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PostmanValidator:
    """Validates Postman collections for correctness and completeness"""
    
    def __init__(self):
        self.required_collections = [
            '01-Autenticacion.postman_collection.json',
            '02-Usuarios.postman_collection.json', 
            '03-Inventario.postman_collection.json',
            '04-Eventos.postman_collection.json',
            '05-Red-ONGs.postman_collection.json'
        ]
        
        self.required_auth_requests = [
            'Login Presidente',
            'Login Vocal', 
            'Login Coordinador',
            'Login Voluntario'
        ]
        
        self.required_test_types = ['success', 'error', 'validation', 'authorization']
    
    def validate_collections(self, collections_path: str) -> Dict[str, Any]:
        """Validate all Postman collections"""
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'collections_found': 0,
            'total_requests': 0,
            'test_coverage': {},
            'validation_details': {}
        }
        
        collections_dir = Path(collections_path)
        if not collections_dir.exists():
            results['valid'] = False
            results['errors'].append(f"Collections directory not found: {collections_path}")
            return results
        
        # Check each required collection
        for collection_name in self.required_collections:
            collection_path = collections_dir / collection_name
            collection_result = self._validate_single_collection(collection_path)
            
            results['validation_details'][collection_name] = collection_result
            
            if collection_result['exists']:
                results['collections_found'] += 1
                results['total_requests'] += collection_result['request_count']
                
                if not collection_result['valid']:
                    results['valid'] = False
                    results['errors'].extend([
                        f"{collection_name}: {error}" 
                        for error in collection_result['errors']
                    ])
                
                results['warnings'].extend([
                    f"{collection_name}: {warning}"
                    for warning in collection_result['warnings']
                ])
            else:
                results['valid'] = False
                results['errors'].append(f"Missing collection: {collection_name}")
        
        # Calculate test coverage
        results['test_coverage'] = self._calculate_test_coverage(results['validation_details'])
        
        return results
    
    def _validate_single_collection(self, collection_path: Path) -> Dict[str, Any]:
        """Validate a single Postman collection"""
        result = {
            'exists': False,
            'valid': True,
            'errors': [],
            'warnings': [],
            'request_count': 0,
            'test_scripts_count': 0,
            'variables_used': [],
            'auth_methods': []
        }
        
        if not collection_path.exists():
            return result
        
        result['exists'] = True
        
        try:
            with open(collection_path, 'r', encoding='utf-8') as f:
                collection_data = json.load(f)
            
            # Validate collection structure
            if 'info' not in collection_data:
                result['errors'].append("Missing 'info' section")
                result['valid'] = False
            
            if 'item' not in collection_data:
                result['errors'].append("Missing 'item' section")
                result['valid'] = False
                return result
            
            # Validate requests
            result['request_count'] = len(collection_data['item'])
            
            for item in collection_data['item']:
                item_validation = self._validate_request_item(item)
                
                if item_validation['has_test_script']:
                    result['test_scripts_count'] += 1
                
                result['variables_used'].extend(item_validation['variables'])
                result['auth_methods'].extend(item_validation['auth_methods'])
                
                if item_validation['errors']:
                    result['errors'].extend(item_validation['errors'])
                    result['valid'] = False
                
                result['warnings'].extend(item_validation['warnings'])
            
            # Remove duplicates
            result['variables_used'] = list(set(result['variables_used']))
            result['auth_methods'] = list(set(result['auth_methods']))
            
            # Validate specific collection requirements
            collection_name = collection_path.name
            if collection_name == '01-Autenticacion.postman_collection.json':
                self._validate_auth_collection(collection_data, result)
            
        except json.JSONDecodeError as e:
            result['valid'] = False
            result['errors'].append(f"Invalid JSON: {e}")
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Validation error: {e}")
        
        return result
    
    def _validate_request_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single request item"""
        result = {
            'errors': [],
            'warnings': [],
            'has_test_script': False,
            'variables': [],
            'auth_methods': []
        }
        
        # Check required fields
        if 'name' not in item:
            result['errors'].append("Request missing 'name' field")
        
        if 'request' not in item:
            result['errors'].append("Request missing 'request' field")
            return result
        
        request_data = item['request']
        
        # Validate URL
        if 'url' not in request_data:
            result['errors'].append("Request missing 'url' field")
        else:
            url = request_data['url']
            if isinstance(url, str):
                # Extract variables from URL
                variables = re.findall(r'\{\{([^}]+)\}\}', url)
                result['variables'].extend(variables)
            elif isinstance(url, dict) and 'raw' in url:
                variables = re.findall(r'\{\{([^}]+)\}\}', url['raw'])
                result['variables'].extend(variables)
        
        # Check for authentication
        if 'header' in request_data:
            for header in request_data['header']:
                if header.get('key', '').lower() == 'authorization':
                    auth_value = header.get('value', '')
                    if 'Bearer' in auth_value:
                        result['auth_methods'].append('Bearer Token')
                        # Extract token variable
                        token_vars = re.findall(r'\{\{([^}]+)\}\}', auth_value)
                        result['variables'].extend(token_vars)
        
        # Check for test scripts
        if 'event' in item:
            for event in item['event']:
                if event.get('listen') == 'test':
                    result['has_test_script'] = True
                    break
        
        # Check request body for variables
        if 'body' in request_data and request_data['body']:
            body = request_data['body']
            if isinstance(body, dict) and 'raw' in body:
                body_vars = re.findall(r'\{\{([^}]+)\}\}', body['raw'])
                result['variables'].extend(body_vars)
        
        return result
    
    def _validate_auth_collection(self, collection_data: Dict[str, Any], result: Dict[str, Any]):
        """Validate authentication collection specific requirements"""
        request_names = [item.get('name', '') for item in collection_data.get('item', [])]
        
        for required_request in self.required_auth_requests:
            if not any(required_request in name for name in request_names):
                result['warnings'].append(f"Missing recommended auth request: {required_request}")
    
    def _calculate_test_coverage(self, validation_details: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate test coverage metrics"""
        total_requests = sum(
            details.get('request_count', 0) 
            for details in validation_details.values()
            if details.get('exists', False)
        )
        
        total_with_tests = sum(
            details.get('test_scripts_count', 0)
            for details in validation_details.values()
            if details.get('exists', False)
        )
        
        coverage_percentage = (total_with_tests / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_requests': total_requests,
            'requests_with_tests': total_with_tests,
            'coverage_percentage': round(coverage_percentage, 2)
        }

class SwaggerValidator:
    """Validates Swagger documentation examples"""
    
    def __init__(self):
        self.required_example_categories = [
            'authentication', 'users', 'inventory', 'events', 'network'
        ]
        
        self.required_auth_examples = [
            'LoginRequest', 'LoginResponse', 'LoginError'
        ]
        
        self.required_response_fields = {
            'LoginResponse': ['token', 'usuario', 'rol'],
            'UsuariosList': [],  # Should be array
            'DonacionesList': [],  # Should be array
            'EventosList': []  # Should be array
        }
    
    def validate_swagger_config(self, swagger_config_path: str) -> Dict[str, Any]:
        """Validate Swagger configuration and examples"""
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'examples_found': 0,
            'categories_covered': [],
            'missing_examples': [],
            'validation_details': {}
        }
        
        config_path = Path(swagger_config_path)
        if not config_path.exists():
            results['valid'] = False
            results['errors'].append(f"Swagger config file not found: {swagger_config_path}")
            return results
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            # Parse JavaScript-like content to extract examples
            examples = self._extract_examples_from_config(config_content)
            results['examples_found'] = len(examples)
            
            # Validate each example
            for example_name, example_data in examples.items():
                example_result = self._validate_single_example(example_name, example_data)
                results['validation_details'][example_name] = example_result
                
                if not example_result['valid']:
                    results['valid'] = False
                    results['errors'].extend([
                        f"{example_name}: {error}"
                        for error in example_result['errors']
                    ])
                
                results['warnings'].extend([
                    f"{example_name}: {warning}"
                    for warning in example_result['warnings']
                ])
            
            # Check for required examples
            self._check_required_examples(examples, results)
            
            # Determine categories covered
            results['categories_covered'] = self._determine_categories_covered(examples)
            
        except Exception as e:
            results['valid'] = False
            results['errors'].append(f"Error reading Swagger config: {e}")
        
        return results
    
    def _extract_examples_from_config(self, config_content: str) -> Dict[str, Any]:
        """Extract examples from Swagger configuration content"""
        examples = {}
        
        # Look for examples section
        examples_match = re.search(r'examples:\s*\{([^}]+)\}', config_content, re.DOTALL)
        if not examples_match:
            return examples
        
        examples_content = examples_match.group(1)
        
        # Extract individual examples (simplified parsing)
        example_pattern = r'(\w+):\s*\{([^}]+)\}'
        for match in re.finditer(example_pattern, examples_content):
            example_name = match.group(1)
            example_content = match.group(2)
            
            # Try to extract summary and value
            summary_match = re.search(r'summary:\s*[\'"]([^\'"]+)[\'"]', example_content)
            value_match = re.search(r'value:\s*(\{[^}]+\}|\[[^\]]+\])', example_content)
            
            examples[example_name] = {
                'summary': summary_match.group(1) if summary_match else '',
                'value': value_match.group(1) if value_match else '{}'
            }
        
        return examples
    
    def _validate_single_example(self, example_name: str, example_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single Swagger example"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required fields
        if not example_data.get('summary'):
            result['warnings'].append("Missing summary")
        
        if not example_data.get('value'):
            result['errors'].append("Missing value")
            result['valid'] = False
        
        # Validate specific examples
        if example_name in self.required_response_fields:
            required_fields = self.required_response_fields[example_name]
            if required_fields:
                value_str = str(example_data.get('value', ''))
                for field in required_fields:
                    if field not in value_str:
                        result['warnings'].append(f"Missing recommended field: {field}")
        
        return result
    
    def _check_required_examples(self, examples: Dict[str, Any], results: Dict[str, Any]):
        """Check for required examples"""
        for required_example in self.required_auth_examples:
            if required_example not in examples:
                results['missing_examples'].append(required_example)
                results['warnings'].append(f"Missing required example: {required_example}")
    
    def _determine_categories_covered(self, examples: Dict[str, Any]) -> List[str]:
        """Determine which categories are covered by examples"""
        categories = []
        
        example_names = list(examples.keys())
        
        if any('Login' in name for name in example_names):
            categories.append('authentication')
        
        if any('Usuario' in name for name in example_names):
            categories.append('users')
        
        if any('Donacion' in name for name in example_names):
            categories.append('inventory')
        
        if any('Evento' in name for name in example_names):
            categories.append('events')
        
        if any('Red' in name or 'Solicitud' in name or 'Oferta' in name for name in example_names):
            categories.append('network')
        
        return categories

class KafkaValidator:
    """Validates Kafka test scenarios"""
    
    def __init__(self):
        self.required_topics = [
            'solicitud_donaciones',
            'oferta_donaciones', 
            'transferencia_donaciones',
            'eventos_solidarios',
            'baja_solicitud_donaciones',
            'baja_evento_solidario',
            'adhesion_evento'
        ]
        
        self.required_message_fields = {
            'solicitud_donaciones': ['idOrganizacion', 'donaciones', 'usuarioSolicitante', 'timestamp'],
            'oferta_donaciones': ['idOrganizacion', 'donaciones', 'usuarioOfertante', 'timestamp'],
            'transferencia_donaciones': ['idOrganizacion', 'idSolicitud', 'donaciones', 'usuarioTransferencia', 'timestamp'],
            'eventos_solidarios': ['idOrganizacion', 'idEvento', 'nombre', 'descripcion', 'fechaHora', 'timestamp'],
            'adhesion_evento': ['idOrganizacion', 'participante', 'idEvento', 'organizacionEvento', 'timestamp']
        }
    
    def validate_kafka_scenarios(self, scenarios: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Validate Kafka test scenarios"""
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'topics_found': 0,
            'total_scenarios': 0,
            'scenario_types': {'success': 0, 'error': 0},
            'validation_details': {}
        }
        
        results['topics_found'] = len(scenarios)
        results['total_scenarios'] = sum(len(topic_scenarios) for topic_scenarios in scenarios.values())
        
        # Validate each topic
        for topic_name, topic_scenarios in scenarios.items():
            topic_result = self._validate_topic_scenarios(topic_name, topic_scenarios)
            results['validation_details'][topic_name] = topic_result
            
            if not topic_result['valid']:
                results['valid'] = False
                results['errors'].extend([
                    f"{topic_name}: {error}"
                    for error in topic_result['errors']
                ])
            
            results['warnings'].extend([
                f"{topic_name}: {warning}"
                for warning in topic_result['warnings']
            ])
            
            # Count scenario types
            results['scenario_types']['success'] += topic_result['success_scenarios']
            results['scenario_types']['error'] += topic_result['error_scenarios']
        
        # Check for required topics
        for required_topic in self.required_topics:
            if required_topic not in scenarios:
                results['warnings'].append(f"Missing recommended topic: {required_topic}")
        
        return results
    
    def _validate_topic_scenarios(self, topic_name: str, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate scenarios for a specific topic"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'scenario_count': len(scenarios),
            'success_scenarios': 0,
            'error_scenarios': 0,
            'scenarios_with_tests': 0
        }
        
        for i, scenario in enumerate(scenarios):
            scenario_result = self._validate_single_scenario(topic_name, scenario, i)
            
            if not scenario_result['valid']:
                result['valid'] = False
                result['errors'].extend(scenario_result['errors'])
            
            result['warnings'].extend(scenario_result['warnings'])
            
            # Count scenario types
            if scenario.get('expected_external_response', True):
                result['success_scenarios'] += 1
            else:
                result['error_scenarios'] += 1
            
            # Count scenarios with test assertions
            if scenario.get('test_assertions'):
                result['scenarios_with_tests'] += 1
        
        return result
    
    def _validate_single_scenario(self, topic_name: str, scenario: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Validate a single Kafka scenario"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        scenario_id = f"scenario_{index}"
        
        # Check required scenario fields
        required_scenario_fields = [
            'scenario_name', 'topic', 'message', 'pre_conditions', 
            'post_conditions', 'test_assertions'
        ]
        
        for field in required_scenario_fields:
            if field not in scenario:
                result['errors'].append(f"{scenario_id}: Missing required field '{field}'")
                result['valid'] = False
        
        # Validate message structure
        if 'message' in scenario:
            message_result = self._validate_message_structure(topic_name, scenario['message'])
            if not message_result['valid']:
                result['valid'] = False
                result['errors'].extend([
                    f"{scenario_id}: {error}"
                    for error in message_result['errors']
                ])
            result['warnings'].extend([
                f"{scenario_id}: {warning}"
                for warning in message_result['warnings']
            ])
        
        # Validate conditions and assertions
        for field in ['pre_conditions', 'post_conditions', 'test_assertions']:
            if field in scenario:
                if not isinstance(scenario[field], list):
                    result['errors'].append(f"{scenario_id}: '{field}' should be a list")
                    result['valid'] = False
                elif len(scenario[field]) == 0:
                    result['warnings'].append(f"{scenario_id}: '{field}' is empty")
        
        return result
    
    def _validate_message_structure(self, topic_name: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Kafka message structure"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required fields for this topic
        if topic_name in self.required_message_fields:
            required_fields = self.required_message_fields[topic_name]
            
            for field in required_fields:
                if field not in message:
                    result['errors'].append(f"Missing required message field: {field}")
                    result['valid'] = False
        
        # Validate timestamp format
        if 'timestamp' in message:
            try:
                datetime.fromisoformat(message['timestamp'])
            except ValueError:
                result['errors'].append("Invalid timestamp format")
                result['valid'] = False
        
        # Validate organization ID format
        if 'idOrganizacion' in message:
            org_id = message['idOrganizacion']
            if not isinstance(org_id, str) or not org_id.startswith('ong-'):
                result['warnings'].append("Organization ID should follow 'ong-*' format")
        
        return result

class IntegrationValidator:
    """Validates integration between different configuration types"""
    
    def __init__(self):
        self.postman_validator = PostmanValidator()
        self.swagger_validator = SwaggerValidator()
        self.kafka_validator = KafkaValidator()
    
    def validate_cross_configuration_consistency(
        self, 
        postman_results: Dict[str, Any],
        swagger_results: Dict[str, Any], 
        kafka_results: Dict[str, Any],
        extracted_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate consistency across all configuration types"""
        
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'consistency_checks': {
                'user_data_consistency': True,
                'endpoint_coverage': True,
                'test_data_alignment': True
            },
            'coverage_analysis': {}
        }
        
        # Check user data consistency
        user_consistency = self._validate_user_data_consistency(
            postman_results, swagger_results, kafka_results, extracted_data
        )
        results['consistency_checks']['user_data_consistency'] = user_consistency['valid']
        if not user_consistency['valid']:
            results['valid'] = False
            results['errors'].extend(user_consistency['errors'])
        results['warnings'].extend(user_consistency['warnings'])
        
        # Check endpoint coverage
        endpoint_coverage = self._validate_endpoint_coverage(postman_results, swagger_results)
        results['consistency_checks']['endpoint_coverage'] = endpoint_coverage['valid']
        if not endpoint_coverage['valid']:
            results['valid'] = False
            results['errors'].extend(endpoint_coverage['errors'])
        results['warnings'].extend(endpoint_coverage['warnings'])
        
        # Analyze test coverage
        results['coverage_analysis'] = self._analyze_test_coverage(
            postman_results, swagger_results, kafka_results, extracted_data
        )
        
        return results
    
    def _validate_user_data_consistency(
        self, 
        postman_results: Dict[str, Any],
        swagger_results: Dict[str, Any],
        kafka_results: Dict[str, Any],
        extracted_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that user data is consistent across configurations"""
        
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Extract user roles from extracted data
        expected_roles = set(extracted_data.get('users', {}).keys())
        
        # Check if Postman collections cover all roles
        postman_variables = []
        for collection_details in postman_results.get('validation_details', {}).values():
            if collection_details.get('exists'):
                postman_variables.extend(collection_details.get('variables_used', []))
        
        role_tokens_in_postman = {
            var.replace('_token', '').upper() 
            for var in postman_variables 
            if var.endswith('_token')
        }
        
        missing_roles_in_postman = expected_roles - role_tokens_in_postman
        if missing_roles_in_postman:
            result['warnings'].append(
                f"Roles not covered in Postman: {', '.join(missing_roles_in_postman)}"
            )
        
        return result
    
    def _validate_endpoint_coverage(
        self, 
        postman_results: Dict[str, Any],
        swagger_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that endpoints are covered in both Postman and Swagger"""
        
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # This is a simplified check - in a real implementation,
        # we would extract actual endpoints from both sources
        postman_collections = postman_results.get('collections_found', 0)
        swagger_examples = swagger_results.get('examples_found', 0)
        
        if postman_collections > 0 and swagger_examples == 0:
            result['warnings'].append("Postman collections exist but no Swagger examples found")
        elif postman_collections == 0 and swagger_examples > 0:
            result['warnings'].append("Swagger examples exist but no Postman collections found")
        
        return result
    
    def _analyze_test_coverage(
        self,
        postman_results: Dict[str, Any],
        swagger_results: Dict[str, Any], 
        kafka_results: Dict[str, Any],
        extracted_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze overall test coverage"""
        
        analysis = {
            'postman_coverage': postman_results.get('test_coverage', {}),
            'swagger_categories': swagger_results.get('categories_covered', []),
            'kafka_topics': kafka_results.get('topics_found', 0),
            'data_categories_covered': list(extracted_data.keys()),
            'overall_score': 0
        }
        
        # Calculate overall coverage score (simplified)
        score = 0
        max_score = 100
        
        # Postman test coverage (40% of total)
        postman_coverage = postman_results.get('test_coverage', {}).get('coverage_percentage', 0)
        score += (postman_coverage / 100) * 40
        
        # Swagger categories (30% of total)
        expected_swagger_categories = 5  # auth, users, inventory, events, network
        swagger_coverage = len(swagger_results.get('categories_covered', [])) / expected_swagger_categories
        score += swagger_coverage * 30
        
        # Kafka topics (30% of total)
        expected_kafka_topics = 7
        kafka_coverage = min(kafka_results.get('topics_found', 0) / expected_kafka_topics, 1.0)
        score += kafka_coverage * 30
        
        analysis['overall_score'] = round(score, 2)
        
        return analysis

def run_comprehensive_validation(
    postman_path: str,
    swagger_path: str, 
    kafka_scenarios: Dict[str, Any],
    extracted_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Run comprehensive validation of all configurations"""
    
    logger.info("Starting comprehensive validation")
    
    # Initialize validators
    postman_validator = PostmanValidator()
    swagger_validator = SwaggerValidator()
    kafka_validator = KafkaValidator()
    integration_validator = IntegrationValidator()
    
    # Run individual validations
    postman_results = postman_validator.validate_collections(postman_path)
    swagger_results = swagger_validator.validate_swagger_config(swagger_path)
    kafka_results = kafka_validator.validate_kafka_scenarios(kafka_scenarios)
    
    # Run integration validation
    integration_results = integration_validator.validate_cross_configuration_consistency(
        postman_results, swagger_results, kafka_results, extracted_data
    )
    
    # Compile final results
    final_results = {
        'timestamp': datetime.now().isoformat(),
        'overall_valid': (
            postman_results['valid'] and 
            swagger_results['valid'] and 
            kafka_results['valid'] and 
            integration_results['valid']
        ),
        'validation_results': {
            'postman': postman_results,
            'swagger': swagger_results,
            'kafka': kafka_results,
            'integration': integration_results
        },
        'summary': {
            'total_errors': (
                len(postman_results['errors']) +
                len(swagger_results['errors']) +
                len(kafka_results['errors']) +
                len(integration_results['errors'])
            ),
            'total_warnings': (
                len(postman_results['warnings']) +
                len(swagger_results['warnings']) +
                len(kafka_results['warnings']) +
                len(integration_results['warnings'])
            ),
            'coverage_score': integration_results['coverage_analysis']['overall_score']
        }
    }
    
    logger.info(f"Validation completed. Overall valid: {final_results['overall_valid']}")
    
    return final_results

if __name__ == "__main__":
    # Example usage
    print("Configuration Validators - Sistema ONG SQL Driven Testing")
    print("This module provides comprehensive validation for generated configurations.")