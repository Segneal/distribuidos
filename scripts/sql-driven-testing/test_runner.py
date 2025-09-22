#!/usr/bin/env python3
"""
Comprehensive Test Runner
Sistema ONG - SQL Driven Testing

Orchestrates and runs all types of tests for the SQL-driven testing system:
- Unit tests for individual components
- Integration tests for component interactions
- End-to-end tests against real services
- Validation tests for generated configurations
"""

import unittest
import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import test modules
try:
    from test_data_extractor import main as run_data_extractor_tests
    from test_postman_generator import test_postman_generator
    from test_swagger_generator import run_tests as run_swagger_tests
    from test_kafka_generator import run_tests as run_kafka_tests
    from test_orchestrator import run_tests as run_orchestrator_tests
    from test_integration import run_integration_tests
    from test_end_to_end import run_end_to_end_tests
    from validators import run_comprehensive_validation
except ImportError as e:
    logger.error(f"Failed to import test modules: {e}")
    sys.exit(1)

class TestRunner:
    """Comprehensive test runner for the SQL-driven testing system"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir) if output_dir else Path("test_results")
        self.output_dir.mkdir(exist_ok=True)
        
        self.test_categories = {
            'unit': {
                'description': 'Unit tests for individual components',
                'tests': [
                    ('Data Extractor', self._run_data_extractor_tests),
                    ('Postman Generator', self._run_postman_generator_tests),
                    ('Swagger Generator', self._run_swagger_generator_tests),
                    ('Kafka Generator', self._run_kafka_generator_tests),
                    ('Orchestrator', self._run_orchestrator_tests)
                ]
            },
            'integration': {
                'description': 'Integration tests for component interactions',
                'tests': [
                    ('Integration Suite', self._run_integration_tests)
                ]
            },
            'end_to_end': {
                'description': 'End-to-end tests against real services',
                'tests': [
                    ('End-to-End Suite', self._run_end_to_end_tests)
                ]
            },
            'validation': {
                'description': 'Validation tests for generated configurations',
                'tests': [
                    ('Configuration Validation', self._run_validation_tests)
                ]
            }
        }
        
        self.results = {
            'start_time': None,
            'end_time': None,
            'total_duration': 0,
            'categories': {},
            'summary': {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'skipped_tests': 0,
                'success_rate': 0
            }
        }
    
    def run_all_tests(self, categories: List[str] = None) -> Dict[str, Any]:
        """Run all tests or specified categories"""
        logger.info("Starting comprehensive test run")
        self.results['start_time'] = datetime.now()
        
        categories_to_run = categories or list(self.test_categories.keys())
        
        for category_name in categories_to_run:
            if category_name not in self.test_categories:
                logger.warning(f"Unknown test category: {category_name}")
                continue
            
            logger.info(f"Running {category_name} tests...")
            category_result = self._run_test_category(category_name)
            self.results['categories'][category_name] = category_result
        
        self.results['end_time'] = datetime.now()
        self.results['total_duration'] = (
            self.results['end_time'] - self.results['start_time']
        ).total_seconds()
        
        # Calculate summary
        self._calculate_summary()
        
        # Save results
        self._save_results()
        
        # Print summary
        self._print_summary()
        
        return self.results
    
    def _run_test_category(self, category_name: str) -> Dict[str, Any]:
        """Run all tests in a category"""
        category = self.test_categories[category_name]
        category_result = {
            'description': category['description'],
            'start_time': datetime.now(),
            'tests': {},
            'total_tests': len(category['tests']),
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0
        }
        
        for test_name, test_function in category['tests']:
            logger.info(f"  Running {test_name}...")
            test_result = self._run_single_test(test_name, test_function)
            category_result['tests'][test_name] = test_result
            
            if test_result['status'] == 'passed':
                category_result['passed_tests'] += 1
            elif test_result['status'] == 'failed':
                category_result['failed_tests'] += 1
            elif test_result['status'] == 'skipped':
                category_result['skipped_tests'] += 1
        
        category_result['end_time'] = datetime.now()
        category_result['duration'] = (
            category_result['end_time'] - category_result['start_time']
        ).total_seconds()
        
        return category_result
    
    def _run_single_test(self, test_name: str, test_function) -> Dict[str, Any]:
        """Run a single test function"""
        test_result = {
            'name': test_name,
            'status': 'unknown',
            'start_time': datetime.now(),
            'duration': 0,
            'error': None,
            'details': {}
        }
        
        try:
            start_time = time.time()
            result = test_function()
            test_result['duration'] = time.time() - start_time
            
            if isinstance(result, bool):
                test_result['status'] = 'passed' if result else 'failed'
            elif isinstance(result, dict):
                test_result['status'] = 'passed' if result.get('success', False) else 'failed'
                test_result['details'] = result
            else:
                test_result['status'] = 'passed'  # Assume success if no clear indication
                
        except unittest.SkipTest as e:
            test_result['status'] = 'skipped'
            test_result['error'] = str(e)
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['error'] = str(e)
            logger.error(f"Test {test_name} failed: {e}")
        
        test_result['end_time'] = datetime.now()
        return test_result
    
    def _run_data_extractor_tests(self) -> bool:
        """Run data extractor unit tests"""
        try:
            return run_data_extractor_tests() == 0
        except Exception as e:
            logger.error(f"Data extractor tests failed: {e}")
            return False
    
    def _run_postman_generator_tests(self) -> bool:
        """Run Postman generator unit tests"""
        try:
            return test_postman_generator()
        except Exception as e:
            logger.error(f"Postman generator tests failed: {e}")
            return False
    
    def _run_swagger_generator_tests(self) -> bool:
        """Run Swagger generator unit tests"""
        try:
            # Capture stdout to avoid cluttering output
            import io
            import contextlib
            
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                run_swagger_tests()
            return True
        except SystemExit as e:
            return e.code == 0
        except Exception as e:
            logger.error(f"Swagger generator tests failed: {e}")
            return False
    
    def _run_kafka_generator_tests(self) -> bool:
        """Run Kafka generator unit tests"""
        try:
            # Capture stdout to avoid cluttering output
            import io
            import contextlib
            
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                run_kafka_tests()
            return True
        except SystemExit as e:
            return e.code == 0
        except Exception as e:
            logger.error(f"Kafka generator tests failed: {e}")
            return False
    
    def _run_orchestrator_tests(self) -> bool:
        """Run orchestrator unit tests"""
        try:
            return run_orchestrator_tests()
        except Exception as e:
            logger.error(f"Orchestrator tests failed: {e}")
            return False
    
    def _run_integration_tests(self) -> bool:
        """Run integration tests"""
        try:
            return run_integration_tests()
        except Exception as e:
            logger.error(f"Integration tests failed: {e}")
            return False
    
    def _run_end_to_end_tests(self) -> bool:
        """Run end-to-end tests"""
        try:
            return run_end_to_end_tests()
        except Exception as e:
            logger.error(f"End-to-end tests failed: {e}")
            return False
    
    def _run_validation_tests(self) -> Dict[str, Any]:
        """Run validation tests"""
        try:
            # Create mock data for validation testing
            mock_extracted_data = {
                'users': {
                    'PRESIDENTE': [{'id': 1, 'nombre_usuario': 'test_presidente'}],
                    'VOCAL': [{'id': 2, 'nombre_usuario': 'test_vocal'}]
                },
                'inventory': {
                    'ALIMENTOS': {'all': [{'id': 101, 'categoria': 'ALIMENTOS'}]}
                },
                'events': {'all': [], 'future': [], 'past': []},
                'network': {'external_requests': [], 'external_offers': [], 'external_events': []},
                'test_mappings': [
                    {'endpoint': '/api/auth/login', 'test_category': 'authentication'}
                ]
            }
            
            mock_kafka_scenarios = {
                'solicitud_donaciones': [
                    {
                        'scenario_name': 'Test Scenario',
                        'topic': 'solicitud-donaciones',
                        'message': {'idOrganizacion': 'ong-test', 'timestamp': '2024-01-01T00:00:00Z'},
                        'pre_conditions': ['Test condition'],
                        'post_conditions': ['Test result'],
                        'test_assertions': ['Test assertion']
                    }
                ]
            }
            
            # Run validation with mock data
            validation_results = run_comprehensive_validation(
                postman_path="api-gateway/postman",  # May not exist, but validator handles this
                swagger_path="api-gateway/src/config/swagger.js",  # May not exist
                kafka_scenarios=mock_kafka_scenarios,
                extracted_data=mock_extracted_data
            )
            
            return {
                'success': validation_results.get('overall_valid', False),
                'details': validation_results
            }
            
        except Exception as e:
            logger.error(f"Validation tests failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _calculate_summary(self):
        """Calculate overall test summary"""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        
        for category_result in self.results['categories'].values():
            total_tests += category_result['total_tests']
            passed_tests += category_result['passed_tests']
            failed_tests += category_result['failed_tests']
            skipped_tests += category_result['skipped_tests']
        
        self.results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'skipped_tests': skipped_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
    
    def _save_results(self):
        """Save test results to file"""
        results_file = self.output_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert datetime objects to strings for JSON serialization
        serializable_results = self._make_json_serializable(self.results)
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Test results saved to: {results_file}")
    
    def _make_json_serializable(self, obj):
        """Convert datetime objects to strings for JSON serialization"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        else:
            return obj
    
    def _print_summary(self):
        """Print test summary to console"""
        print("\n" + "=" * 80)
        print("TEST EXECUTION SUMMARY")
        print("=" * 80)
        
        summary = self.results['summary']
        
        print(f"Total Duration: {self.results['total_duration']:.2f} seconds")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']} ✅")
        print(f"Failed: {summary['failed_tests']} ❌")
        print(f"Skipped: {summary['skipped_tests']} ⏭️")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        
        print("\nCATEGORY BREAKDOWN:")
        print("-" * 40)
        
        for category_name, category_result in self.results['categories'].items():
            status_icon = "✅" if category_result['failed_tests'] == 0 else "❌"
            print(f"{status_icon} {category_name.upper()}: "
                  f"{category_result['passed_tests']}/{category_result['total_tests']} passed "
                  f"({category_result['duration']:.2f}s)")
            
            # Show failed tests
            if category_result['failed_tests'] > 0:
                for test_name, test_result in category_result['tests'].items():
                    if test_result['status'] == 'failed':
                        print(f"    ❌ {test_name}: {test_result.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 80)
        
        if summary['failed_tests'] == 0:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"⚠️  {summary['failed_tests']} TEST(S) FAILED")
        
        print("=" * 80)

class ContinuousIntegrationRunner:
    """Runner optimized for CI/CD environments"""
    
    def __init__(self):
        self.test_runner = TestRunner()
    
    def run_ci_tests(self) -> bool:
        """Run tests suitable for CI environment"""
        # In CI, we typically skip end-to-end tests that require external services
        categories_to_run = ['unit', 'integration', 'validation']
        
        logger.info("Running CI test suite (unit + integration + validation)")
        results = self.test_runner.run_all_tests(categories_to_run)
        
        # Return success if no tests failed
        return results['summary']['failed_tests'] == 0
    
    def run_full_tests(self) -> bool:
        """Run full test suite including end-to-end tests"""
        logger.info("Running full test suite (all categories)")
        results = self.test_runner.run_all_tests()
        
        return results['summary']['failed_tests'] == 0

def main():
    """Main entry point for test runner"""
    parser = argparse.ArgumentParser(description='SQL-Driven Testing - Comprehensive Test Runner')
    parser.add_argument(
        '--categories',
        nargs='+',
        choices=['unit', 'integration', 'end_to_end', 'validation'],
        help='Test categories to run (default: all)'
    )
    parser.add_argument(
        '--output-dir',
        default='test_results',
        help='Directory to save test results (default: test_results)'
    )
    parser.add_argument(
        '--ci',
        action='store_true',
        help='Run in CI mode (skip end-to-end tests)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.ci:
        # CI mode
        ci_runner = ContinuousIntegrationRunner()
        success = ci_runner.run_ci_tests()
    else:
        # Regular mode
        test_runner = TestRunner(args.output_dir)
        results = test_runner.run_all_tests(args.categories)
        success = results['summary']['failed_tests'] == 0
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()