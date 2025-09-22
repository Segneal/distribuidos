#!/usr/bin/env python3
"""
Testing Orchestrator for SQL-Driven Testing System
Sistema ONG - SQL Driven Testing

This module coordinates the extraction of data and generation of all testing
configurations in sequence, with automatic backups and comprehensive validation.
"""

import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import traceback

from data_extractor import SQLDataExtractor, DatabaseConfig, create_db_config_from_env
from postman_generator import PostmanGenerator
from swagger_generator import SwaggerGenerator
from kafka_generator import KafkaTestGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BackupManager:
    """Manages backups of testing configurations before modifications"""
    
    def __init__(self, backup_base_dir: str = "scripts/sql-driven-testing/backups"):
        self.backup_base_dir = Path(backup_base_dir)
        self.backup_base_dir.mkdir(parents=True, exist_ok=True)
        self.current_backup_dir = None
    
    def create_backups(self) -> str:
        """Create backups of all current testing configurations"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_backup_dir = self.backup_base_dir / f"backup_{timestamp}"
        self.current_backup_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Creating backups in: {self.current_backup_dir}")
        
        backup_items = [
            # Postman collections
            ("api-gateway/postman", "postman_collections"),
            # Swagger configuration
            ("api-gateway/src/config/swagger.js", "swagger_config.js"),
            # Kafka test scenarios (if they exist)
            ("scripts/sql-driven-testing/kafka_scenarios.json", "kafka_scenarios.json"),
        ]
        
        backed_up_files = []
        
        for source_path, backup_name in backup_items:
            source = Path(source_path)
            if source.exists():
                backup_path = self.current_backup_dir / backup_name
                
                if source.is_dir():
                    shutil.copytree(source, backup_path, dirs_exist_ok=True)
                    backed_up_files.append(f"Directory: {source_path}")
                else:
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, backup_path)
                    backed_up_files.append(f"File: {source_path}")
                
                logger.info(f"Backed up: {source_path} -> {backup_path}")
        
        # Create backup manifest
        manifest = {
            "timestamp": timestamp,
            "backup_directory": str(self.current_backup_dir),
            "backed_up_files": backed_up_files,
            "total_files": len(backed_up_files)
        }
        
        manifest_path = self.current_backup_dir / "backup_manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Backup completed: {len(backed_up_files)} items backed up")
        return str(self.current_backup_dir)
    
    def get_latest_backup_path(self) -> Optional[str]:
        """Get the path to the most recent backup"""
        if self.current_backup_dir:
            return str(self.current_backup_dir)
        
        # Find the most recent backup directory
        backup_dirs = [d for d in self.backup_base_dir.iterdir() 
                      if d.is_dir() and d.name.startswith("backup_")]
        
        if backup_dirs:
            latest_backup = max(backup_dirs, key=lambda d: d.stat().st_mtime)
            return str(latest_backup)
        
        return None
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """Restore configurations from a specific backup"""
        backup_dir = Path(backup_path)
        if not backup_dir.exists():
            logger.error(f"Backup directory not found: {backup_path}")
            return False
        
        try:
            # Load backup manifest
            manifest_path = backup_dir / "backup_manifest.json"
            if manifest_path.exists():
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                logger.info(f"Restoring from backup: {manifest['timestamp']}")
            
            # Restore Postman collections
            postman_backup = backup_dir / "postman_collections"
            if postman_backup.exists():
                postman_target = Path("api-gateway/postman")
                if postman_target.exists():
                    shutil.rmtree(postman_target)
                shutil.copytree(postman_backup, postman_target)
                logger.info("Restored Postman collections")
            
            # Restore Swagger configuration
            swagger_backup = backup_dir / "swagger_config.js"
            if swagger_backup.exists():
                swagger_target = Path("api-gateway/src/config/swagger.js")
                shutil.copy2(swagger_backup, swagger_target)
                logger.info("Restored Swagger configuration")
            
            # Restore Kafka scenarios
            kafka_backup = backup_dir / "kafka_scenarios.json"
            if kafka_backup.exists():
                kafka_target = Path("scripts/sql-driven-testing/kafka_scenarios.json")
                shutil.copy2(kafka_backup, kafka_target)
                logger.info("Restored Kafka scenarios")
            
            logger.info("Backup restoration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring from backup: {e}")
            return False

class ConfigurationValidator:
    """Validates generated testing configurations"""
    
    def __init__(self):
        self.validation_errors = []
        self.validation_warnings = []
    
    def validate_all_configurations(self, generation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all generated configurations"""
        logger.info("Starting comprehensive validation of generated configurations")
        
        self.validation_errors = []
        self.validation_warnings = []
        
        validation_results = {
            'postman': self.validate_postman_collections(generation_results.get('postman', {})),
            'swagger': self.validate_swagger_examples(generation_results.get('swagger', {})),
            'kafka': self.validate_kafka_scenarios(generation_results.get('kafka', {})),
            'overall': {
                'total_errors': 0,
                'total_warnings': 0,
                'validation_passed': True
            }
        }
        
        # Calculate overall validation status
        total_errors = sum(result.get('errors', 0) for result in validation_results.values() if isinstance(result, dict))
        total_warnings = sum(result.get('warnings', 0) for result in validation_results.values() if isinstance(result, dict))
        
        validation_results['overall'] = {
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'validation_passed': total_errors == 0,
            'all_errors': self.validation_errors,
            'all_warnings': self.validation_warnings
        }
        
        if total_errors == 0:
            logger.info(f"Validation passed with {total_warnings} warnings")
        else:
            logger.error(f"Validation failed with {total_errors} errors and {total_warnings} warnings")
        
        return validation_results
    
    def validate_postman_collections(self, postman_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generated Postman collections"""
        logger.info("Validating Postman collections")
        
        errors = 0
        warnings = 0
        
        collections_updated = postman_results.get('collections_updated', {})
        
        # Check that all expected collections were generated
        expected_collections = [
            '01-Autenticacion.postman_collection.json',
            '02-Usuarios.postman_collection.json',
            '03-Inventario.postman_collection.json',
            '04-Eventos.postman_collection.json',
            '05-Red-ONGs.postman_collection.json'
        ]
        
        for collection_name in expected_collections:
            if collection_name not in collections_updated:
                self.validation_errors.append(f"Missing Postman collection: {collection_name}")
                errors += 1
            else:
                # Validate collection file exists and is valid JSON
                collection_path = Path(collections_updated[collection_name])
                if not collection_path.exists():
                    self.validation_errors.append(f"Postman collection file not found: {collection_path}")
                    errors += 1
                else:
                    try:
                        with open(collection_path, 'r', encoding='utf-8') as f:
                            collection_data = json.load(f)
                        
                        # Basic structure validation
                        if 'info' not in collection_data:
                            self.validation_errors.append(f"Invalid Postman collection structure: {collection_name}")
                            errors += 1
                        
                        if 'item' not in collection_data or not collection_data['item']:
                            self.validation_warnings.append(f"Empty Postman collection: {collection_name}")
                            warnings += 1
                        
                    except json.JSONDecodeError as e:
                        self.validation_errors.append(f"Invalid JSON in Postman collection {collection_name}: {e}")
                        errors += 1
        
        # Check environment file
        env_path = Path("api-gateway/postman/Sistema-ONG-Environment.postman_environment.json")
        if not env_path.exists():
            self.validation_warnings.append("Postman environment file not found")
            warnings += 1
        
        return {
            'errors': errors,
            'warnings': warnings,
            'collections_validated': len(expected_collections),
            'collections_found': len([c for c in expected_collections if c in collections_updated])
        }
    
    def validate_swagger_examples(self, swagger_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate updated Swagger examples"""
        logger.info("Validating Swagger examples")
        
        errors = 0
        warnings = 0
        
        # Check if Swagger configuration file exists and is valid
        swagger_path = Path("api-gateway/src/config/swagger.js")
        if not swagger_path.exists():
            self.validation_errors.append("Swagger configuration file not found")
            errors += 1
        else:
            try:
                with open(swagger_path, 'r', encoding='utf-8') as f:
                    swagger_content = f.read()
                
                # Basic validation checks
                if 'examples:' not in swagger_content:
                    self.validation_errors.append("Examples section not found in Swagger configuration")
                    errors += 1
                
                # Check for balanced braces and brackets
                open_braces = swagger_content.count('{')
                close_braces = swagger_content.count('}')
                if open_braces != close_braces:
                    self.validation_errors.append(f"Unbalanced braces in Swagger config: {open_braces} open, {close_braces} close")
                    errors += 1
                
                # Check for required example sections
                required_examples = ['LoginRequest', 'UsuariosList', 'DonacionesList', 'EventosList']
                for example in required_examples:
                    if example not in swagger_content:
                        self.validation_warnings.append(f"Missing Swagger example: {example}")
                        warnings += 1
                
            except Exception as e:
                self.validation_errors.append(f"Error reading Swagger configuration: {e}")
                errors += 1
        
        return {
            'errors': errors,
            'warnings': warnings,
            'examples_updated': swagger_results.get('total_examples', 0),
            'validation_passed': swagger_results.get('validation_passed', False)
        }
    
    def validate_kafka_scenarios(self, kafka_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generated Kafka scenarios"""
        logger.info("Validating Kafka scenarios")
        
        errors = 0
        warnings = 0
        
        scenarios_generated = kafka_results.get('scenarios_generated', {})
        
        # Check that all expected topic scenarios were generated
        expected_topics = [
            'solicitud_donaciones',
            'oferta_donaciones', 
            'transferencia_donaciones',
            'eventos_solidarios'
        ]
        
        for topic in expected_topics:
            if topic not in scenarios_generated:
                self.validation_warnings.append(f"No Kafka scenarios generated for topic: {topic}")
                warnings += 1
            else:
                topic_scenarios = scenarios_generated[topic]
                if not topic_scenarios:
                    self.validation_warnings.append(f"Empty Kafka scenarios for topic: {topic}")
                    warnings += 1
                else:
                    # Validate scenario structure
                    for scenario in topic_scenarios:
                        if not isinstance(scenario, dict):
                            self.validation_errors.append(f"Invalid Kafka scenario structure in topic {topic}")
                            errors += 1
                            continue
                        
                        required_fields = ['scenario_name', 'topic', 'message']
                        for field in required_fields:
                            if field not in scenario:
                                self.validation_errors.append(f"Missing field '{field}' in Kafka scenario: {scenario.get('scenario_name', 'unknown')}")
                                errors += 1
        
        return {
            'errors': errors,
            'warnings': warnings,
            'topics_validated': len(expected_topics),
            'scenarios_generated': sum(len(scenarios) for scenarios in scenarios_generated.values())
        }

class TestingOrchestrator:
    """Coordinates the generation of all testing configurations from SQL data"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file)
        self.backup_manager = BackupManager()
        self.validator = ConfigurationValidator()
        self.data_extractor = None
        self.extracted_data = None
        
        logger.info("Testing Orchestrator initialized")
    
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or environment variables"""
        if config_file and Path(config_file).exists():
            logger.info(f"Loading configuration from: {config_file}")
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.info("Using configuration from environment variables")
            return {
                'database': {
                    'host': os.getenv('DB_HOST', 'localhost'),
                    'port': int(os.getenv('DB_PORT', '3306')),
                    'database': os.getenv('DB_NAME', 'ong_sistema'),
                    'user': os.getenv('DB_USER', 'ong_user'),
                    'password': os.getenv('DB_PASSWORD', 'ong_password')
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
                    'extracted_data_file': 'scripts/sql-driven-testing/extracted_test_data.json',
                    'report_file': 'scripts/sql-driven-testing/generation_report.json'
                }
            }
    
    def generate_all_testing_configs(self, options: Optional[Dict[str, bool]] = None) -> Dict[str, Any]:
        """Generate all testing configurations from SQL data"""
        logger.info("=" * 60)
        logger.info("Starting SQL-Driven Testing Configuration Generation")
        logger.info("=" * 60)
        
        # Merge options with defaults
        generation_options = self.config['generation'].copy()
        if options:
            generation_options.update(options)
        
        try:
            # Step 1: Create backups if enabled
            backup_path = None
            if generation_options.get('backup', True):
                logger.info("Step 1: Creating backups of existing configurations")
                backup_path = self.backup_manager.create_backups()
            else:
                logger.info("Step 1: Skipping backups (disabled)")
            
            # Step 2: Extract data from SQL database
            logger.info("Step 2: Extracting test data from SQL database")
            self._extract_test_data()
            
            # Step 3: Validate extracted data
            if generation_options.get('validate', True):
                logger.info("Step 3: Validating extracted data integrity")
                self._validate_extracted_data()
            else:
                logger.info("Step 3: Skipping data validation (disabled)")
            
            # Step 4: Generate configurations
            logger.info("Step 4: Generating testing configurations")
            generation_results = self._generate_configurations(generation_options)
            
            # Step 5: Validate generated configurations
            validation_results = {}
            if generation_options.get('validate', True):
                logger.info("Step 5: Validating generated configurations")
                validation_results = self.validator.validate_all_configurations(generation_results)
            else:
                logger.info("Step 5: Skipping configuration validation (disabled)")
            
            # Step 6: Generate comprehensive report
            logger.info("Step 6: Generating comprehensive report")
            report = self._generate_comprehensive_report(
                generation_results, 
                validation_results, 
                backup_path,
                generation_options
            )
            
            # Step 7: Save outputs
            self._save_outputs(report)
            
            logger.info("=" * 60)
            logger.info("SQL-Driven Testing Configuration Generation COMPLETED")
            logger.info("=" * 60)
            
            return report
            
        except Exception as e:
            logger.error(f"Error during testing configuration generation: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Create error report
            error_report = {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat(),
                'backup_path': backup_path
            }
            
            return error_report
        
        finally:
            # Always cleanup database connection
            if self.data_extractor:
                self.data_extractor.disconnect()
    
    def _extract_test_data(self):
        """Extract test data from SQL database"""
        # Filter database config to only include supported parameters
        db_params = {
            'host': self.config['database']['host'],
            'port': self.config['database']['port'],
            'database': self.config['database']['database'],
            'user': self.config['database']['user'],
            'password': self.config['database']['password']
        }
        db_config = DatabaseConfig(**db_params)
        self.data_extractor = SQLDataExtractor(db_config)
        
        try:
            self.extracted_data = self.data_extractor.extract_test_data()
            
            # Log extraction summary
            logger.info("Data extraction completed successfully:")
            logger.info(f"  - Users by role: {list(self.extracted_data['users'].keys())}")
            logger.info(f"  - Inventory categories: {list(self.extracted_data['inventory'].keys())}")
            logger.info(f"  - Events: {len(self.extracted_data['events']['all'])} total")
            logger.info(f"  - Test mappings: {len(self.extracted_data['test_mappings'])} cases")
            logger.info(f"  - Network data: {len(self.extracted_data['network']['external_requests'])} external requests")
            
        except Exception as e:
            logger.error(f"Failed to extract test data: {e}")
            raise
    
    def _validate_extracted_data(self):
        """Validate the integrity of extracted data"""
        if not self.extracted_data:
            raise ValueError("No extracted data available for validation")
        
        try:
            # The data extractor already performs validation during extraction
            # This is an additional validation step for orchestrator-specific checks
            
            validation_errors = []
            
            # Check minimum data requirements for each generator
            if not self.extracted_data['users']:
                validation_errors.append("No test users found - required for all generators")
            
            if not self.extracted_data['test_mappings']:
                validation_errors.append("No test case mappings found - required for Postman generation")
            
            if not self.extracted_data['inventory']:
                validation_errors.append("No inventory data found - required for comprehensive testing")
            
            # Check that we have users for all major roles
            required_roles = ['PRESIDENTE', 'VOCAL', 'COORDINADOR', 'VOLUNTARIO']
            missing_roles = [role for role in required_roles if role not in self.extracted_data['users'] or not self.extracted_data['users'][role]]
            if missing_roles:
                validation_errors.append(f"Missing users for roles: {missing_roles}")
            
            if validation_errors:
                error_msg = "Extracted data validation failed:\n" + "\n".join(f"  - {error}" for error in validation_errors)
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.info("Extracted data validation passed")
            
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            raise
    
    def _generate_configurations(self, options: Dict[str, bool]) -> Dict[str, Any]:
        """Generate all requested testing configurations"""
        results = {}
        
        try:
            # Generate Postman collections
            if options.get('postman', True):
                logger.info("Generating Postman collections...")
                postman_generator = PostmanGenerator(self.extracted_data)
                results['postman'] = {
                    'collections_updated': postman_generator.generate_all_collections(),
                    'environment_updated': True,
                    'total_collections': 5
                }
                logger.info(f"Postman generation completed: {len(results['postman']['collections_updated'])} collections")
            
            # Generate Swagger examples
            if options.get('swagger', True):
                logger.info("Updating Swagger examples...")
                swagger_generator = SwaggerGenerator(self.extracted_data)
                results['swagger'] = swagger_generator.update_swagger_examples()
                logger.info(f"Swagger generation completed: {results['swagger']['total_examples']} examples updated")
            
            # Generate Kafka scenarios
            if options.get('kafka', True):
                logger.info("Generating Kafka test scenarios...")
                kafka_generator = KafkaTestGenerator(self.extracted_data)
                kafka_scenarios = kafka_generator.generate_all_kafka_scenarios()
                
                # Save Kafka scenarios to file
                kafka_output_file = "scripts/sql-driven-testing/kafka_scenarios.json"
                with open(kafka_output_file, 'w', encoding='utf-8') as f:
                    json.dump(kafka_scenarios, f, indent=2, ensure_ascii=False)
                
                results['kafka'] = {
                    'scenarios_generated': kafka_scenarios,
                    'output_file': kafka_output_file,
                    'total_scenarios': sum(len(scenarios) for scenarios in kafka_scenarios.values()),
                    'topics_covered': list(kafka_scenarios.keys())
                }
                logger.info(f"Kafka generation completed: {results['kafka']['total_scenarios']} scenarios across {len(results['kafka']['topics_covered'])} topics")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during configuration generation: {e}")
            raise
    
    def _generate_comprehensive_report(self, generation_results: Dict[str, Any], 
                                     validation_results: Dict[str, Any],
                                     backup_path: Optional[str],
                                     options: Dict[str, bool]) -> Dict[str, Any]:
        """Generate comprehensive report of the generation process"""
        
        report = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'generation_options': options,
            'backup_path': backup_path,
            'data_extraction': {
                'total_users': sum(len(users) for users in self.extracted_data['users'].values()),
                'user_roles': list(self.extracted_data['users'].keys()),
                'inventory_categories': list(self.extracted_data['inventory'].keys()),
                'total_donations': sum(len(cat_data['all']) for cat_data in self.extracted_data['inventory'].values()),
                'total_events': len(self.extracted_data['events']['all']),
                'future_events': len(self.extracted_data['events']['future']),
                'past_events': len(self.extracted_data['events']['past']),
                'test_mappings': len(self.extracted_data['test_mappings']),
                'external_requests': len(self.extracted_data['network']['external_requests']),
                'external_offers': len(self.extracted_data['network']['external_offers']),
                'external_events': len(self.extracted_data['network']['external_events'])
            },
            'generation_results': generation_results,
            'validation_results': validation_results,
            'summary': {
                'configurations_generated': list(generation_results.keys()),
                'total_postman_collections': generation_results.get('postman', {}).get('total_collections', 0),
                'total_swagger_examples': generation_results.get('swagger', {}).get('total_examples', 0),
                'total_kafka_scenarios': generation_results.get('kafka', {}).get('total_scenarios', 0),
                'validation_passed': validation_results.get('overall', {}).get('validation_passed', True),
                'total_validation_errors': validation_results.get('overall', {}).get('total_errors', 0),
                'total_validation_warnings': validation_results.get('overall', {}).get('total_warnings', 0)
            }
        }
        
        # Add detailed statistics
        if 'postman' in generation_results:
            postman_stats = generation_results['postman']
            report['postman_details'] = {
                'collections_generated': list(postman_stats['collections_updated'].keys()),
                'environment_updated': postman_stats.get('environment_updated', False)
            }
        
        if 'swagger' in generation_results:
            swagger_stats = generation_results['swagger']
            report['swagger_details'] = {
                'examples_categories': swagger_stats.get('examples_updated', []),
                'backup_created': swagger_stats.get('backup_created', False),
                'validation_passed': swagger_stats.get('validation_passed', False)
            }
        
        if 'kafka' in generation_results:
            kafka_stats = generation_results['kafka']
            report['kafka_details'] = {
                'topics_covered': kafka_stats.get('topics_covered', []),
                'output_file': kafka_stats.get('output_file'),
                'scenarios_by_topic': {
                    topic: len(scenarios) 
                    for topic, scenarios in kafka_stats.get('scenarios_generated', {}).items()
                }
            }
        
        return report
    
    def _save_outputs(self, report: Dict[str, Any]):
        """Save extracted data and generation report to files"""
        try:
            # Save extracted data if configured
            if self.config['output'].get('save_extracted_data', True) and self.extracted_data:
                data_file = self.config['output']['extracted_data_file']
                os.makedirs(os.path.dirname(data_file), exist_ok=True)
                
                with open(data_file, 'w', encoding='utf-8') as f:
                    json.dump(self.extracted_data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Extracted data saved to: {data_file}")
            
            # Save generation report
            report_file = self.config['output']['report_file']
            os.makedirs(os.path.dirname(report_file), exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Generation report saved to: {report_file}")
            
        except Exception as e:
            logger.error(f"Error saving outputs: {e}")
            # Don't raise - this shouldn't fail the entire process
    
    def restore_from_backup(self, backup_path: Optional[str] = None) -> bool:
        """Restore configurations from backup"""
        if not backup_path:
            backup_path = self.backup_manager.get_latest_backup_path()
        
        if not backup_path:
            logger.error("No backup path provided and no recent backups found")
            return False
        
        logger.info(f"Restoring configurations from backup: {backup_path}")
        return self.backup_manager.restore_from_backup(backup_path)
    
    def get_generation_status(self) -> Dict[str, Any]:
        """Get current status of generated configurations"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'postman': self._check_postman_status(),
            'swagger': self._check_swagger_status(),
            'kafka': self._check_kafka_status(),
            'backups': self._check_backup_status()
        }
        
        return status
    
    def _check_postman_status(self) -> Dict[str, Any]:
        """Check status of Postman collections"""
        postman_dir = Path("api-gateway/postman")
        expected_collections = [
            '01-Autenticacion.postman_collection.json',
            '02-Usuarios.postman_collection.json',
            '03-Inventario.postman_collection.json',
            '04-Eventos.postman_collection.json',
            '05-Red-ONGs.postman_collection.json'
        ]
        
        existing_collections = []
        for collection in expected_collections:
            collection_path = postman_dir / collection
            if collection_path.exists():
                stat = collection_path.stat()
                existing_collections.append({
                    'name': collection,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        env_path = postman_dir / "Sistema-ONG-Environment.postman_environment.json"
        env_exists = env_path.exists()
        
        return {
            'collections_found': len(existing_collections),
            'collections_expected': len(expected_collections),
            'environment_exists': env_exists,
            'collections': existing_collections
        }
    
    def _check_swagger_status(self) -> Dict[str, Any]:
        """Check status of Swagger configuration"""
        swagger_path = Path("api-gateway/src/config/swagger.js")
        
        if not swagger_path.exists():
            return {'exists': False}
        
        stat = swagger_path.stat()
        
        # Check for examples section
        with open(swagger_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_examples = 'examples:' in content
        
        return {
            'exists': True,
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'has_examples_section': has_examples
        }
    
    def _check_kafka_status(self) -> Dict[str, Any]:
        """Check status of Kafka scenarios"""
        kafka_path = Path("scripts/sql-driven-testing/kafka_scenarios.json")
        
        if not kafka_path.exists():
            return {'exists': False}
        
        stat = kafka_path.stat()
        
        # Load and analyze scenarios
        with open(kafka_path, 'r', encoding='utf-8') as f:
            scenarios = json.load(f)
        
        total_scenarios = sum(len(topic_scenarios) for topic_scenarios in scenarios.values())
        
        return {
            'exists': True,
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'topics': list(scenarios.keys()),
            'total_scenarios': total_scenarios
        }
    
    def _check_backup_status(self) -> Dict[str, Any]:
        """Check status of backups"""
        backup_dir = Path("scripts/sql-driven-testing/backups")
        
        if not backup_dir.exists():
            return {'backup_dir_exists': False, 'total_backups': 0}
        
        backup_dirs = [d for d in backup_dir.iterdir() 
                      if d.is_dir() and d.name.startswith("backup_")]
        
        backups = []
        for backup in backup_dirs:
            manifest_path = backup / "backup_manifest.json"
            if manifest_path.exists():
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                backups.append({
                    'path': str(backup),
                    'timestamp': manifest.get('timestamp'),
                    'files_backed_up': manifest.get('total_files', 0)
                })
        
        # Sort by timestamp (most recent first)
        backups.sort(key=lambda b: b['timestamp'], reverse=True)
        
        return {
            'backup_dir_exists': True,
            'total_backups': len(backups),
            'recent_backups': backups[:5],  # Show 5 most recent
            'latest_backup': backups[0] if backups else None
        }

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SQL-Driven Testing Configuration Orchestrator')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--no-postman', action='store_true', help='Skip Postman generation')
    parser.add_argument('--no-swagger', action='store_true', help='Skip Swagger generation')
    parser.add_argument('--no-kafka', action='store_true', help='Skip Kafka generation')
    parser.add_argument('--no-backup', action='store_true', help='Skip backup creation')
    parser.add_argument('--no-validate', action='store_true', help='Skip validation')
    parser.add_argument('--restore', help='Restore from backup path')
    parser.add_argument('--status', action='store_true', help='Show current status')
    
    args = parser.parse_args()
    
    orchestrator = TestingOrchestrator(args.config)
    
    if args.restore:
        success = orchestrator.restore_from_backup(args.restore)
        if success:
            print("Backup restoration completed successfully")
        else:
            print("Backup restoration failed")
        return
    
    if args.status:
        status = orchestrator.get_generation_status()
        print(json.dumps(status, indent=2))
        return
    
    # Generate configurations
    options = {
        'postman': not args.no_postman,
        'swagger': not args.no_swagger,
        'kafka': not args.no_kafka,
        'backup': not args.no_backup,
        'validate': not args.no_validate
    }
    
    report = orchestrator.generate_all_testing_configs(options)
    
    if report.get('success', False):
        print("\n" + "=" * 60)
        print("GENERATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"Configurations generated: {', '.join(report['summary']['configurations_generated'])}")
        print(f"Postman collections: {report['summary']['total_postman_collections']}")
        print(f"Swagger examples: {report['summary']['total_swagger_examples']}")
        print(f"Kafka scenarios: {report['summary']['total_kafka_scenarios']}")
        print(f"Validation errors: {report['summary']['total_validation_errors']}")
        print(f"Validation warnings: {report['summary']['total_validation_warnings']}")
        if report.get('backup_path'):
            print(f"Backup created: {report['backup_path']}")
    else:
        print("\n" + "=" * 60)
        print("GENERATION FAILED")
        print("=" * 60)
        print(f"Error: {report.get('error', 'Unknown error')}")
        if report.get('backup_path'):
            print(f"Backup available for restoration: {report['backup_path']}")

if __name__ == "__main__":
    main()    
    def restore_from_backup(self, backup_path: str) -> bool:
        """Restore configurations from a specific backup"""
        try:
            logger.info(f"Restoring configurations from: {backup_path}")
            return self.backup_manager.restore_from_backup(backup_path)
        except Exception as e:
            logger.error(f"Error during restore operation: {e}")
            return False
    
    def count_total_test_cases(self, results: Dict[str, Any]) -> int:
        """Count total test cases generated across all configurations"""
        total = 0
        
        if 'postman' in results:
            total += results['postman'].get('total_collections', 0) * 10  # Estimate requests per collection
        
        if 'swagger' in results:
            total += results['swagger'].get('total_examples', 0)
        
        if 'kafka' in results:
            total += results['kafka'].get('total_scenarios', 0)
        
        return total