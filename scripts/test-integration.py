#!/usr/bin/env python3
"""
Integration test script for Sistema ONG Backend
Tests the complete system with live services
"""
import requests
import json
import time
import sys
from datetime import datetime, timedelta

class SystemTester:
    def __init__(self):
        self.base_url = "http://localhost:3000/api"
        self.token = None
        self.test_user_id = None
        self.test_donation_id = None
        self.test_event_id = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def test_health_check(self):
        """Test system health"""
        self.log("Testing system health...")
        try:
            response = requests.get("http://localhost:3000/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ System health check passed", "SUCCESS")
                return True
            else:
                self.log(f"❌ Health check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Health check failed: {e}", "ERROR")
            return False
    
    def test_authentication(self):
        """Test user authentication"""
        self.log("Testing authentication...")
        try:
            # Try to login with default admin user
            login_data = {
                "identificador": "admin@ong.com",
                "clave": "password123"
            }
            
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                if self.token:
                    self.log("✅ Authentication successful", "SUCCESS")
                    return True
                else:
                    self.log("❌ No token received", "ERROR")
                    return False
            else:
                self.log(f"❌ Authentication failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Authentication error: {e}", "ERROR")
            return False
    
    def get_headers(self):
        """Get headers with authentication token"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_user_management(self):
        """Test user CRUD operations"""
        self.log("Testing user management...")
        try:
            # Create a test user
            user_data = {
                "nombreUsuario": f"test_user_{int(time.time())}",
                "nombre": "Test",
                "apellido": "User",
                "telefono": "1234567890",
                "email": f"test_{int(time.time())}@test.com",
                "rol": "VOLUNTARIO"
            }
            
            response = requests.post(
                f"{self.base_url}/usuarios",
                json=user_data,
                headers=self.get_headers()
            )
            
            if response.status_code == 201:
                user = response.json()
                self.test_user_id = user.get('id')
                self.log("✅ User creation successful", "SUCCESS")
                
                # Test user listing
                response = requests.get(f"{self.base_url}/usuarios", headers=self.get_headers())
                if response.status_code == 200:
                    self.log("✅ User listing successful", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ User listing failed: {response.status_code}", "ERROR")
                    return False
            else:
                self.log(f"❌ User creation failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ User management error: {e}", "ERROR")
            return False
    
    def test_inventory_management(self):
        """Test inventory CRUD operations"""
        self.log("Testing inventory management...")
        try:
            # Create a test donation
            donation_data = {
                "categoria": "ALIMENTOS",
                "descripcion": "Test donation",
                "cantidad": 10
            }
            
            response = requests.post(
                f"{self.base_url}/inventario",
                json=donation_data,
                headers=self.get_headers()
            )
            
            if response.status_code == 201:
                donation = response.json()
                self.test_donation_id = donation.get('id')
                self.log("✅ Donation creation successful", "SUCCESS")
                
                # Test inventory listing
                response = requests.get(f"{self.base_url}/inventario", headers=self.get_headers())
                if response.status_code == 200:
                    self.log("✅ Inventory listing successful", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Inventory listing failed: {response.status_code}", "ERROR")
                    return False
            else:
                self.log(f"❌ Donation creation failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Inventory management error: {e}", "ERROR")
            return False
    
    def test_event_management(self):
        """Test event CRUD operations"""
        self.log("Testing event management...")
        try:
            # Create a test event
            future_date = (datetime.now() + timedelta(days=7)).isoformat()
            event_data = {
                "nombre": "Test Event",
                "descripcion": "Test event description",
                "fechaHora": future_date
            }
            
            response = requests.post(
                f"{self.base_url}/eventos",
                json=event_data,
                headers=self.get_headers()
            )
            
            if response.status_code == 201:
                event = response.json()
                self.test_event_id = event.get('id')
                self.log("✅ Event creation successful", "SUCCESS")
                
                # Test event listing
                response = requests.get(f"{self.base_url}/eventos", headers=self.get_headers())
                if response.status_code == 200:
                    self.log("✅ Event listing successful", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Event listing failed: {response.status_code}", "ERROR")
                    return False
            else:
                self.log(f"❌ Event creation failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Event management error: {e}", "ERROR")
            return False
    
    def test_kafka_integration(self):
        """Test Kafka integration with donation requests"""
        self.log("Testing Kafka integration...")
        try:
            # Test donation request
            request_data = {
                "donaciones": [
                    {
                        "categoria": "ALIMENTOS",
                        "descripcion": "Test request"
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/red/solicitudes-donaciones",
                json=request_data,
                headers=self.get_headers()
            )
            
            if response.status_code == 201:
                self.log("✅ Kafka donation request successful", "SUCCESS")
                
                # Wait a bit for message processing
                time.sleep(2)
                
                # Test listing requests
                response = requests.get(f"{self.base_url}/red/solicitudes-donaciones", headers=self.get_headers())
                if response.status_code == 200:
                    self.log("✅ Kafka integration test successful", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Request listing failed: {response.status_code}", "ERROR")
                    return False
            else:
                self.log(f"❌ Kafka request failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Kafka integration error: {e}", "ERROR")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        self.log("Cleaning up test data...")
        try:
            # Delete test user if created
            if self.test_user_id:
                requests.delete(f"{self.base_url}/usuarios/{self.test_user_id}", headers=self.get_headers())
            
            # Delete test donation if created
            if self.test_donation_id:
                requests.delete(f"{self.base_url}/inventario/{self.test_donation_id}", headers=self.get_headers())
            
            # Delete test event if created
            if self.test_event_id:
                requests.delete(f"{self.base_url}/eventos/{self.test_event_id}", headers=self.get_headers())
            
            self.log("✅ Test data cleanup completed", "SUCCESS")
        except Exception as e:
            self.log(f"⚠️  Cleanup error (non-critical): {e}", "WARNING")
    
    def run_all_tests(self):
        """Run all integration tests"""
        self.log("🚀 Starting Sistema ONG Backend Integration Tests")
        self.log("=" * 60)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Authentication", self.test_authentication),
            ("User Management", self.test_user_management),
            ("Inventory Management", self.test_inventory_management),
            ("Event Management", self.test_event_management),
            ("Kafka Integration", self.test_kafka_integration),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            self.log(f"Running {test_name}...")
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log(f"❌ {test_name} failed with exception: {e}", "ERROR")
                failed += 1
            
            self.log("-" * 40)
        
        # Cleanup
        self.cleanup_test_data()
        
        # Results
        self.log("=" * 60)
        self.log(f"🏁 Integration Tests Completed")
        self.log(f"✅ Passed: {passed}")
        self.log(f"❌ Failed: {failed}")
        self.log(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if failed == 0:
            self.log("🎉 All tests passed!", "SUCCESS")
            return True
        else:
            self.log("⚠️  Some tests failed. Check logs for details.", "WARNING")
            return False

def main():
    """Main function"""
    tester = SystemTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()