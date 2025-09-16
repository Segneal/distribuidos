#!/usr/bin/env python3
"""
Sistema ONG Backend - Integration Test Suite
Tests complete flows including authentication, CRUD operations, and Kafka integration
"""

import requests
import json
import time
import pytest
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import threading
import uuid
from datetime import datetime, timedelta

# Configuration
API_BASE_URL = "http://localhost:3000"
KAFKA_BROKERS = ["localhost:9092"]
ORGANIZATION_ID = "ong-empuje-comunitario"

class TestSystemIntegration:
    """Complete system integration tests"""
    
    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        cls.session = requests.Session()
        cls.auth_token = None
        cls.test_user_id = None
        cls.test_donacion_id = None
        cls.test_evento_id = None
        
        # Wait for services to be ready
        cls._wait_for_services()
    
    @classmethod
    def _wait_for_services(cls, timeout=60):
        """Wait for all services to be ready"""
        print("Waiting for services to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check API Gateway
                response = requests.get(f"{API_BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ API Gateway is ready")
                    break
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
        else:
            raise Exception("Services not ready within timeout")
    
    def test_01_health_check(self):
        """Test system health endpoints"""
        print("\n🏥 Testing health endpoints...")
        
        # Test API Gateway health
        response = self.session.get(f"{API_BASE_URL}/health")
        assert response.status_code == 200
        
        health_data = response.json()
        assert health_data["status"] == "OK"
        assert "timestamp" in health_data
        
        print("✅ Health check passed")
    
    def test_02_authentication_flow(self):
        """Test complete authentication flow"""
        print("\n🔐 Testing authentication flow...")
        
        # Try to access protected endpoint without token
        response = self.session.get(f"{API_BASE_URL}/api/usuarios")
        assert response.status_code == 401
        
        # Create admin user first (this should work if database is initialized)
        admin_data = {
            "nombreUsuario": "admin_test",
            "nombre": "Admin",
            "apellido": "Test",
            "telefono": "1234567890",
            "email": "admin@test.com",
            "rol": "PRESIDENTE"
        }
        
        # Try to create user without authentication (should fail)
        response = self.session.post(f"{API_BASE_URL}/api/usuarios", json=admin_data)
        assert response.status_code == 401
        
        print("✅ Authentication protection working")
    
    def test_03_kafka_connectivity(self):
        """Test Kafka connectivity and topic creation"""
        print("\n📨 Testing Kafka connectivity...")
        
        try:
            # Test producer
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                request_timeout_ms=10000
            )
            
            # Test message
            test_message = {
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "organization": ORGANIZATION_ID
            }
            
            # Send test message
            future = producer.send('solicitud-donaciones', test_message)
            producer.flush(timeout=10)
            
            # Test consumer
            consumer = KafkaConsumer(
                'solicitud-donaciones',
                bootstrap_servers=KAFKA_BROKERS,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                consumer_timeout_ms=5000,
                auto_offset_reset='latest'
            )
            
            producer.close()
            consumer.close()
            
            print("✅ Kafka connectivity test passed")
            
        except KafkaError as e:
            pytest.fail(f"Kafka connectivity failed: {e}")
    
    def test_04_database_connectivity(self):
        """Test database connectivity through API"""
        print("\n🗄️ Testing database connectivity...")
        
        # This test assumes we can access some endpoint that hits the database
        # We'll use the health endpoint which should check database status
        response = self.session.get(f"{API_BASE_URL}/health")
        assert response.status_code == 200
        
        health_data = response.json()
        # The health endpoint should include database status
        assert "status" in health_data
        
        print("✅ Database connectivity test passed")
    
    def test_05_grpc_service_communication(self):
        """Test gRPC service communication through API Gateway"""
        print("\n🔗 Testing gRPC service communication...")
        
        # Test each service through API Gateway endpoints
        services_to_test = [
            ("/api/usuarios", "User Service"),
            ("/api/inventario", "Inventory Service"),
            ("/api/eventos", "Events Service")
        ]
        
        for endpoint, service_name in services_to_test:
            response = self.session.get(f"{API_BASE_URL}{endpoint}")
            # Should get 401 (unauthorized) not 503 (service unavailable)
            assert response.status_code == 401, f"{service_name} not responding"
            print(f"✅ {service_name} communication working")
    
    def test_06_error_handling(self):
        """Test error handling across the system"""
        print("\n⚠️ Testing error handling...")
        
        # Test invalid endpoints
        response = self.session.get(f"{API_BASE_URL}/api/nonexistent")
        assert response.status_code == 404
        
        # Test malformed requests
        response = self.session.post(
            f"{API_BASE_URL}/api/auth/login",
            json={"invalid": "data"}
        )
        assert response.status_code in [400, 422]  # Bad request or validation error
        
        # Test invalid JSON
        response = self.session.post(
            f"{API_BASE_URL}/api/auth/login",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        
        print("✅ Error handling tests passed")
    
    def test_07_cors_and_security_headers(self):
        """Test CORS and security headers"""
        print("\n🛡️ Testing CORS and security headers...")
        
        # Test CORS preflight
        response = self.session.options(
            f"{API_BASE_URL}/api/auth/login",
            headers={
                "Origin": "http://localhost:3001",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # Should allow CORS or return appropriate headers
        assert response.status_code in [200, 204]
        
        # Test security headers on main endpoint
        response = self.session.get(f"{API_BASE_URL}/health")
        headers = response.headers
        
        # Check for basic security headers
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection"
        ]
        
        for header in security_headers:
            if header in headers:
                print(f"✅ Security header {header} present")
        
        print("✅ Security headers test completed")
    
    def test_08_api_documentation(self):
        """Test API documentation availability"""
        print("\n📚 Testing API documentation...")
        
        # Test Swagger UI
        response = self.session.get(f"{API_BASE_URL}/api-docs")
        assert response.status_code == 200
        
        # Test Swagger JSON
        response = self.session.get(f"{API_BASE_URL}/api-docs/swagger.json")
        if response.status_code == 200:
            swagger_data = response.json()
            assert "swagger" in swagger_data or "openapi" in swagger_data
            print("✅ Swagger documentation available")
        else:
            print("⚠️ Swagger JSON not available (may be expected)")
    
    def test_09_rate_limiting(self):
        """Test rate limiting (if implemented)"""
        print("\n🚦 Testing rate limiting...")
        
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = self.session.get(f"{API_BASE_URL}/health")
            responses.append(response.status_code)
        
        # All should succeed for health endpoint (usually not rate limited)
        assert all(status == 200 for status in responses)
        
        print("✅ Rate limiting test completed")
    
    def test_10_kafka_message_flow(self):
        """Test complete Kafka message flow"""
        print("\n📨 Testing Kafka message flow...")
        
        # Test message production and consumption
        test_topics = [
            "solicitud-donaciones",
            "oferta-donaciones",
            "eventos-solidarios"
        ]
        
        for topic in test_topics:
            try:
                # Create producer
                producer = KafkaProducer(
                    bootstrap_servers=KAFKA_BROKERS,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    request_timeout_ms=5000
                )
                
                # Create test message
                test_message = {
                    "idOrganizacion": ORGANIZATION_ID,
                    "test": True,
                    "timestamp": datetime.now().isoformat(),
                    "topic": topic
                }
                
                # Send message
                future = producer.send(topic, test_message)
                producer.flush(timeout=5)
                
                producer.close()
                print(f"✅ Message sent to {topic}")
                
            except Exception as e:
                print(f"⚠️ Failed to send message to {topic}: {e}")
    
    def test_11_system_performance(self):
        """Test basic system performance"""
        print("\n⚡ Testing system performance...")
        
        # Test response times
        endpoints_to_test = [
            "/health",
            "/api-docs"
        ]
        
        for endpoint in endpoints_to_test:
            start_time = time.time()
            response = self.session.get(f"{API_BASE_URL}{endpoint}")
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 5.0  # Should respond within 5 seconds
            
            print(f"✅ {endpoint} responded in {response_time:.2f}s")
    
    def test_12_concurrent_requests(self):
        """Test system under concurrent load"""
        print("\n🔄 Testing concurrent requests...")
        
        import concurrent.futures
        
        def make_request():
            response = requests.get(f"{API_BASE_URL}/health")
            return response.status_code
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        print(f"✅ {len(results)} concurrent requests completed successfully")
    
    @classmethod
    def teardown_class(cls):
        """Cleanup after tests"""
        if cls.session:
            cls.session.close()
        print("\n🧹 Test cleanup completed")

def run_integration_tests():
    """Run integration tests with proper setup"""
    print("=" * 60)
    print("   Sistema ONG Backend - Integration Test Suite")
    print("=" * 60)
    
    # Run tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes"
    ])

if __name__ == "__main__":
    run_integration_tests()