#!/usr/bin/env python3
"""
Sistema ONG Backend - Integration Test Runner
Runs all integration tests and generates comprehensive reports
"""

import os
import sys
import subprocess
import time
import json
import requests
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configuration
API_BASE_URL = "http://localhost:3000"
KAFKA_BROKERS = ["localhost:9092"]
TEST_RESULTS_DIR = "test-results"

class IntegrationTestRunner:
    """Runs and manages integration tests"""
    
    def __init__(self):
        self.results = {
            "start_time": datetime.now().isoformat(),
            "tests": {},
            "summary": {},
            "system_status": {}
        }
        
        # Ensure test results directory exists
        os.makedirs(TEST_RESULTS_DIR, exist_ok=True)
    
    def check_system_status(self):
        """Check if all required services are running"""
        print("🔍 Checking system status...")
        
        status = {
            "api_gateway": False,
            "database": False,
            "kafka": False,
            "grpc_services": {
                "user_service": False,
                "inventory_service": False,
                "events_service": False
            }
        }
        
        # Check API Gateway
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                status["api_gateway"] = True
                health_data = response.json()
                print("✅ API Gateway is running")
                
                # Extract service status from health response if available
                if "services" in health_data:
                    for service, service_status in health_data["services"].items():
                        if service in status["grpc_services"]:
                            status["grpc_services"][service] = service_status
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API Gateway not accessible: {e}")
        
        # Check Kafka (through Docker if available)
        try:
            result = subprocess.run([
                "docker-compose", "exec", "-T", "kafka", 
                "kafka-topics.sh", "--bootstrap-server", "localhost:9092", "--list"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                status["kafka"] = True
                print("✅ Kafka is running")
            else:
                print("❌ Kafka not accessible")
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"❌ Could not check Kafka status: {e}")
        
        # Check Database (through Docker if available)
        try:
            result = subprocess.run([
                "docker-compose", "exec", "-T", "mysql",
                "mysqladmin", "ping", "-h", "localhost"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                status["database"] = True
                print("✅ Database is running")
            else:
                print("❌ Database not accessible")
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"❌ Could not check database status: {e}")
        
        self.results["system_status"] = status
        return status
    
    def run_test_suite(self, test_file, test_name):
        """Run a specific test suite"""
        print(f"\n🧪 Running {test_name}...")
        
        start_time = time.time()
        
        try:
            # Run pytest on the specific test file
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_file,
                "-v",
                "--tb=short",
                "--json-report",
                f"--json-report-file={TEST_RESULTS_DIR}/{test_name.lower().replace(' ', '_')}_results.json"
            ], capture_output=True, text=True, timeout=300)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Parse results
            test_result = {
                "name": test_name,
                "file": test_file,
                "duration": duration,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
            # Try to load JSON report if available
            json_report_file = f"{TEST_RESULTS_DIR}/{test_name.lower().replace(' ', '_')}_results.json"
            if os.path.exists(json_report_file):
                try:
                    with open(json_report_file, 'r') as f:
                        json_report = json.load(f)
                        test_result["detailed_results"] = json_report
                except Exception as e:
                    print(f"⚠️ Could not parse JSON report: {e}")
            
            self.results["tests"][test_name] = test_result
            
            if test_result["success"]:
                print(f"✅ {test_name} completed successfully in {duration:.2f}s")
            else:
                print(f"❌ {test_name} failed in {duration:.2f}s")
                print(f"Error output: {result.stderr}")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_name} timed out after 5 minutes")
            test_result = {
                "name": test_name,
                "file": test_file,
                "duration": 300,
                "return_code": -1,
                "success": False,
                "error": "Test timed out"
            }
            self.results["tests"][test_name] = test_result
            return test_result
            
        except Exception as e:
            print(f"💥 {test_name} crashed: {e}")
            test_result = {
                "name": test_name,
                "file": test_file,
                "duration": 0,
                "return_code": -1,
                "success": False,
                "error": str(e)
            }
            self.results["tests"][test_name] = test_result
            return test_result
    
    def run_all_tests(self):
        """Run all integration test suites"""
        print("=" * 60)
        print("   Sistema ONG Backend - Integration Test Runner")
        print("=" * 60)
        
        # Check system status first
        system_status = self.check_system_status()
        
        # Determine which tests to run based on system status
        test_suites = []
        
        if system_status["api_gateway"]:
            test_suites.extend([
                ("tests/integration/test_complete_flow.py", "Complete System Flow"),
                ("tests/integration/test_auth_flow.py", "Authentication & Authorization")
            ])
        
        if system_status["kafka"]:
            test_suites.append(("tests/integration/test_kafka_integration.py", "Kafka Integration"))
        
        if not test_suites:
            print("❌ No services available for testing. Please start the system first.")
            return False
        
        # Run test suites
        all_passed = True
        for test_file, test_name in test_suites:
            if os.path.exists(test_file):
                result = self.run_test_suite(test_file, test_name)
                if not result["success"]:
                    all_passed = False
            else:
                print(f"⚠️ Test file not found: {test_file}")
                all_passed = False
        
        # Generate summary
        self.generate_summary()
        
        # Save results
        self.save_results()
        
        return all_passed
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.results["tests"])
        passed_tests = sum(1 for test in self.results["tests"].values() if test["success"])
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(test.get("duration", 0) for test in self.results["tests"].values())
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration,
            "end_time": datetime.now().isoformat()
        }
        
        self.results["summary"] = summary
        
        print("\n" + "=" * 60)
        print("   TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Duration: {total_duration:.2f}s")
        
        if failed_tests > 0:
            print("\nFailed Tests:")
            for test_name, test_result in self.results["tests"].items():
                if not test_result["success"]:
                    print(f"  ❌ {test_name}")
                    if "error" in test_result:
                        print(f"     Error: {test_result['error']}")
    
    def save_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"{TEST_RESULTS_DIR}/integration_test_results_{timestamp}.json"
        
        try:
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            print(f"\n📄 Test results saved to: {results_file}")
            
            # Also create a human-readable report
            report_file = f"{TEST_RESULTS_DIR}/integration_test_report_{timestamp}.txt"
            self.generate_text_report(report_file)
            
        except Exception as e:
            print(f"⚠️ Could not save results: {e}")
    
    def generate_text_report(self, report_file):
        """Generate human-readable text report"""
        try:
            with open(report_file, 'w') as f:
                f.write("Sistema ONG Backend - Integration Test Report\n")
                f.write("=" * 50 + "\n\n")
                
                f.write(f"Test Run: {self.results['start_time']}\n")
                f.write(f"Duration: {self.results['summary']['total_duration']:.2f}s\n\n")
                
                f.write("System Status:\n")
                f.write("-" * 20 + "\n")
                status = self.results["system_status"]
                f.write(f"API Gateway: {'✅' if status['api_gateway'] else '❌'}\n")
                f.write(f"Database: {'✅' if status['database'] else '❌'}\n")
                f.write(f"Kafka: {'✅' if status['kafka'] else '❌'}\n")
                
                f.write("\ngRPC Services:\n")
                for service, running in status["grpc_services"].items():
                    f.write(f"  {service}: {'✅' if running else '❌'}\n")
                
                f.write(f"\nTest Results:\n")
                f.write("-" * 20 + "\n")
                
                for test_name, test_result in self.results["tests"].items():
                    status_icon = "✅" if test_result["success"] else "❌"
                    f.write(f"{status_icon} {test_name} ({test_result['duration']:.2f}s)\n")
                    
                    if not test_result["success"] and "error" in test_result:
                        f.write(f"   Error: {test_result['error']}\n")
                
                f.write(f"\nSummary:\n")
                f.write("-" * 20 + "\n")
                summary = self.results["summary"]
                f.write(f"Total Tests: {summary['total_tests']}\n")
                f.write(f"Passed: {summary['passed_tests']}\n")
                f.write(f"Failed: {summary['failed_tests']}\n")
                f.write(f"Success Rate: {summary['success_rate']:.1f}%\n")
            
            print(f"📄 Human-readable report saved to: {report_file}")
            
        except Exception as e:
            print(f"⚠️ Could not generate text report: {e}")

def main():
    """Main function"""
    runner = IntegrationTestRunner()
    
    # Check if pytest-json-report is available
    try:
        import pytest_jsonreport
    except ImportError:
        print("⚠️ pytest-json-report not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest-json-report"])
    
    # Run all tests
    success = runner.run_all_tests()
    
    if success:
        print("\n🎉 All integration tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some integration tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()