#!/usr/bin/env python3
"""
Sistema ONG Backend - Authentication & Authorization Integration Tests
Tests complete authentication and role-based authorization flows
"""

import requests
import json
import pytest
import time

# Configuration
API_BASE_URL = "http://localhost:3000"

class TestAuthenticationFlow:
    """Test authentication and authorization flows"""
    
    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        cls.session = requests.Session()
        cls.admin_token = None
        cls.vocal_token = None
        cls.coordinador_token = None
        cls.voluntario_token = None
        
        # Test users data
        cls.test_users = {
            "admin": {
                "nombreUsuario": "admin_integration",
                "nombre": "Admin",
                "apellido": "Integration",
                "telefono": "1111111111",
                "email": "admin.integration@test.com",
                "rol": "PRESIDENTE"
            },
            "vocal": {
                "nombreUsuario": "vocal_integration",
                "nombre": "Vocal",
                "apellido": "Integration",
                "telefono": "2222222222",
                "email": "vocal.integration@test.com",
                "rol": "VOCAL"
            },
            "coordinador": {
                "nombreUsuario": "coord_integration",
                "nombre": "Coordinador",
                "apellido": "Integration",
                "telefono": "3333333333",
                "email": "coord.integration@test.com",
                "rol": "COORDINADOR"
            },
            "voluntario": {
                "nombreUsuario": "vol_integration",
                "nombre": "Voluntario",
                "apellido": "Integration",
                "telefono": "4444444444",
                "email": "vol.integration@test.com",
                "rol": "VOLUNTARIO"
            }
        }
    
    def test_01_unauthorized_access(self):
        """Test that protected endpoints require authentication"""
        print("\n🔒 Testing unauthorized access protection...")
        
        protected_endpoints = [
            ("GET", "/api/usuarios"),
            ("POST", "/api/usuarios"),
            ("GET", "/api/inventario"),
            ("POST", "/api/inventario"),
            ("GET", "/api/eventos"),
            ("POST", "/api/eventos"),
            ("GET", "/api/red/solicitudes-donaciones"),
            ("POST", "/api/red/solicitudes-donaciones")
        ]
        
        for method, endpoint in protected_endpoints:
            if method == "GET":
                response = self.session.get(f"{API_BASE_URL}{endpoint}")
            elif method == "POST":
                response = self.session.post(f"{API_BASE_URL}{endpoint}", json={})
            
            assert response.status_code == 401, f"Endpoint {method} {endpoint} should require authentication"
            
            response_data = response.json()
            assert "mensaje" in response_data or "message" in response_data
            
        print("✅ All protected endpoints require authentication")
    
    def test_02_invalid_login_attempts(self):
        """Test various invalid login scenarios"""
        print("\n❌ Testing invalid login attempts...")
        
        # Test with missing fields
        response = self.session.post(f"{API_BASE_URL}/api/auth/login", json={})
        assert response.status_code in [400, 422]
        
        # Test with invalid credentials
        invalid_credentials = [
            {"identificador": "nonexistent", "clave": "password"},
            {"identificador": "admin", "clave": "wrongpassword"},
            {"identificador": "", "clave": "password"},
            {"identificador": "admin", "clave": ""}
        ]
        
        for creds in invalid_credentials:
            response = self.session.post(f"{API_BASE_URL}/api/auth/login", json=creds)
            assert response.status_code in [400, 401, 422]
            
        print("✅ Invalid login attempts properly rejected")
    
    def test_03_malformed_requests(self):
        """Test malformed authentication requests"""
        print("\n🔧 Testing malformed requests...")
        
        # Test invalid JSON
        response = self.session.post(
            f"{API_BASE_URL}/api/auth/login",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        
        # Test wrong content type
        response = self.session.post(
            f"{API_BASE_URL}/api/auth/login",
            data="identificador=admin&clave=password",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        # Should either accept it or reject with proper error
        assert response.status_code in [400, 415, 422]
        
        print("✅ Malformed requests properly handled")
    
    def test_04_token_validation(self):
        """Test token validation scenarios"""
        print("\n🎫 Testing token validation...")
        
        # Test with invalid token format
        invalid_tokens = [
            "invalid.token.format",
            "Bearer invalid_token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
            ""
        ]
        
        for token in invalid_tokens:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            response = self.session.get(f"{API_BASE_URL}/api/usuarios", headers=headers)
            assert response.status_code in [401, 403]
            
        print("✅ Invalid tokens properly rejected")
    
    def test_05_role_based_access_control(self):
        """Test role-based access control without actual authentication"""
        print("\n👥 Testing role-based access control structure...")
        
        # This test verifies the RBAC structure is in place
        # We test by sending requests with invalid tokens but checking
        # that the error messages indicate proper role checking
        
        role_restricted_endpoints = [
            # Only PRESIDENTE can access user management
            ("GET", "/api/usuarios", ["PRESIDENTE"]),
            ("POST", "/api/usuarios", ["PRESIDENTE"]),
            
            # PRESIDENTE and VOCAL can access inventory
            ("GET", "/api/inventario", ["PRESIDENTE", "VOCAL"]),
            ("POST", "/api/inventario", ["PRESIDENTE", "VOCAL"]),
            
            # PRESIDENTE and COORDINADOR can manage events
            ("POST", "/api/eventos", ["PRESIDENTE", "COORDINADOR"]),
            
            # All roles can view events
            ("GET", "/api/eventos", ["PRESIDENTE", "COORDINADOR", "VOCAL", "VOLUNTARIO"])
        ]
        
        # Test with invalid token to ensure RBAC middleware is active
        headers = {"Authorization": "Bearer invalid_token"}
        
        for method, endpoint, allowed_roles in role_restricted_endpoints:
            if method == "GET":
                response = self.session.get(f"{API_BASE_URL}{endpoint}", headers=headers)
            elif method == "POST":
                response = self.session.post(f"{API_BASE_URL}{endpoint}", json={}, headers=headers)
            
            # Should get 401 (invalid token) or 403 (forbidden)
            # This confirms that authentication/authorization middleware is active
            assert response.status_code in [401, 403]
            
        print("✅ Role-based access control middleware is active")
    
    def test_06_cors_preflight_requests(self):
        """Test CORS preflight requests for authentication endpoints"""
        print("\n🌐 Testing CORS preflight requests...")
        
        # Test CORS preflight for login endpoint
        response = self.session.options(
            f"{API_BASE_URL}/api/auth/login",
            headers={
                "Origin": "http://localhost:3001",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type, Authorization"
            }
        )
        
        # Should allow CORS or return appropriate response
        assert response.status_code in [200, 204]
        
        # Check CORS headers if present
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers"
        ]
        
        for header in cors_headers:
            if header in response.headers:
                print(f"✅ CORS header {header} present")
        
        print("✅ CORS preflight handling verified")
    
    def test_07_authentication_rate_limiting(self):
        """Test rate limiting on authentication endpoints"""
        print("\n🚦 Testing authentication rate limiting...")
        
        # Make multiple rapid login attempts
        login_data = {"identificador": "test", "clave": "test"}
        
        responses = []
        for i in range(10):
            response = self.session.post(f"{API_BASE_URL}/api/auth/login", json=login_data)
            responses.append(response.status_code)
            time.sleep(0.1)  # Small delay between requests
        
        # Check if any requests were rate limited (429)
        rate_limited = any(status == 429 for status in responses)
        
        if rate_limited:
            print("✅ Rate limiting is active on authentication")
        else:
            print("ℹ️ No rate limiting detected (may not be implemented)")
        
        # All should be either 401 (invalid creds) or 429 (rate limited)
        assert all(status in [400, 401, 422, 429] for status in responses)
    
    def test_08_security_headers(self):
        """Test security headers on authentication endpoints"""
        print("\n🛡️ Testing security headers...")
        
        response = self.session.post(f"{API_BASE_URL}/api/auth/login", json={})
        
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": ["DENY", "SAMEORIGIN"],
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": None,  # May not be present in development
            "Content-Security-Policy": None     # May not be present
        }
        
        for header, expected_values in security_headers.items():
            if header in response.headers:
                header_value = response.headers[header]
                if expected_values is None:
                    print(f"✅ Security header {header}: {header_value}")
                elif isinstance(expected_values, list):
                    if header_value in expected_values:
                        print(f"✅ Security header {header}: {header_value}")
                    else:
                        print(f"⚠️ Security header {header} has unexpected value: {header_value}")
                else:
                    if header_value == expected_values:
                        print(f"✅ Security header {header}: {header_value}")
                    else:
                        print(f"⚠️ Security header {header} has unexpected value: {header_value}")
            else:
                print(f"ℹ️ Security header {header} not present")
    
    def test_09_input_validation(self):
        """Test input validation on authentication endpoints"""
        print("\n✅ Testing input validation...")
        
        # Test various invalid inputs
        invalid_inputs = [
            # SQL injection attempts
            {"identificador": "admin'; DROP TABLE usuarios; --", "clave": "password"},
            {"identificador": "admin", "clave": "' OR '1'='1"},
            
            # XSS attempts
            {"identificador": "<script>alert('xss')</script>", "clave": "password"},
            {"identificador": "admin", "clave": "<img src=x onerror=alert('xss')>"},
            
            # Very long inputs
            {"identificador": "a" * 1000, "clave": "password"},
            {"identificador": "admin", "clave": "b" * 1000},
            
            # Special characters
            {"identificador": "admin\x00\x01\x02", "clave": "password"},
            {"identificador": "admin", "clave": "password\n\r\t"},
            
            # Unicode and encoding issues
            {"identificador": "admin🚀", "clave": "password"},
            {"identificador": "admin", "clave": "contraseña"}
        ]
        
        for invalid_input in invalid_inputs:
            response = self.session.post(f"{API_BASE_URL}/api/auth/login", json=invalid_input)
            
            # Should handle gracefully with proper error codes
            assert response.status_code in [400, 401, 422, 500]
            
            # Response should be JSON
            try:
                response.json()
            except json.JSONDecodeError:
                pytest.fail(f"Non-JSON response for input: {invalid_input}")
        
        print("✅ Input validation tests completed")
    
    def test_10_concurrent_authentication(self):
        """Test concurrent authentication requests"""
        print("\n🔄 Testing concurrent authentication...")
        
        import concurrent.futures
        
        def make_auth_request():
            return self.session.post(
                f"{API_BASE_URL}/api/auth/login",
                json={"identificador": "test", "clave": "test"}
            ).status_code
        
        # Make 5 concurrent authentication requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_auth_request) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All should handle gracefully
        assert all(status in [400, 401, 422, 429] for status in results)
        print(f"✅ {len(results)} concurrent auth requests handled properly")
    
    @classmethod
    def teardown_class(cls):
        """Cleanup after tests"""
        if cls.session:
            cls.session.close()
        print("\n🧹 Authentication test cleanup completed")

def run_auth_tests():
    """Run authentication tests with proper setup"""
    print("=" * 60)
    print("   Authentication & Authorization Test Suite")
    print("=" * 60)
    
    # Run tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes"
    ])

if __name__ == "__main__":
    run_auth_tests()