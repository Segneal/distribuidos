#!/usr/bin/env python3
"""
Postman Collection Generator for SQL-Driven Testing
Sistema ONG - SQL Driven Testing

This module generates Postman collections with real test data extracted from SQL database.
It creates requests with actual IDs, tokens, and data that exist in the populated database.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostmanGenerator:
    """Generates Postman collections from SQL-extracted test data"""
    
    def __init__(self, extracted_data: Dict[str, Any]):
        self.data = extracted_data
        self.base_collection_path = Path("api-gateway/postman")
        self.base_url = "{{base_url}}"
        
        # Validate required data
        self._validate_input_data()
    
    def _validate_input_data(self):
        """Validate that required data is present"""
        required_keys = ['users', 'inventory', 'events', 'test_mappings']
        missing_keys = [key for key in required_keys if key not in self.data]
        if missing_keys:
            raise ValueError(f"Missing required data keys: {missing_keys}")
        
        logger.info("Input data validation passed")
    
    def generate_all_collections(self) -> Dict[str, str]:
        """Generate all Postman collections with real data"""
        logger.info("Starting generation of all Postman collections")
        
        collections = [
            ('01-Autenticacion.postman_collection.json', self.generate_auth_collection),
            ('02-Usuarios.postman_collection.json', self.generate_users_collection),
            ('03-Inventario.postman_collection.json', self.generate_inventory_collection),
            ('04-Eventos.postman_collection.json', self.generate_events_collection),
            ('05-Red-ONGs.postman_collection.json', self.generate_network_collection)
        ]
        
        results = {}
        for filename, generator_func in collections:
            try:
                logger.info(f"Generating collection: {filename}")
                collection = generator_func()
                file_path = self.save_collection(filename, collection)
                results[filename] = file_path
                logger.info(f"Successfully generated: {filename}")
            except Exception as e:
                logger.error(f"Failed to generate {filename}: {e}")
                raise
        
        # Update environment with real data
        self.update_environment_variables()
        
        logger.info("All Postman collections generated successfully")
        return results
    
    def generate_auth_collection(self) -> Dict:
        """Generate authentication collection with real user data"""
        logger.info("Generating authentication collection")
        
        auth_cases = [case for case in self.data['test_mappings'] 
                     if case['test_category'] == 'authentication']
        
        requests = []
        
        # Generate login requests for each role
        for role, users in self.data['users'].items():
            if users:  # Ensure we have users for this role
                user = users[0]  # Use first user of each role
                
                # Success case
                requests.append({
                    "name": f"Login Exitoso - {role}",
                    "event": [{
                        "listen": "test",
                        "script": {
                            "exec": [
                                "pm.test('Status code is 200', function () {",
                                "    pm.response.to.have.status(200);",
                                "});",
                                "",
                                "pm.test('Response has token', function () {",
                                "    var jsonData = pm.response.json();",
                                "    pm.expect(jsonData).to.have.property('token');",
                                "    pm.expect(jsonData).to.have.property('usuario');",
                                "    ",
                                "    // Store token for subsequent requests",
                                "    pm.environment.set('auth_token', jsonData.token);",
                                f"    pm.environment.set('{role.lower()}_token', jsonData.token);",
                                f"    pm.environment.set('{role.lower()}_id', jsonData.usuario.id);",
                                "    pm.environment.set('user_id', jsonData.usuario.id);",
                                "    pm.environment.set('user_role', jsonData.usuario.rol);",
                                "});",
                                "",
                                f"pm.test('User has correct role', function () {{",
                                "    var jsonData = pm.response.json();",
                                f"    pm.expect(jsonData.usuario.rol).to.eql('{role}');",
                                "});",
                                "",
                                "pm.test('User data is complete', function () {",
                                "    var jsonData = pm.response.json();",
                                "    pm.expect(jsonData.usuario).to.have.property('id');",
                                "    pm.expect(jsonData.usuario).to.have.property('nombreUsuario');",
                                "    pm.expect(jsonData.usuario).to.have.property('nombre');",
                                "    pm.expect(jsonData.usuario).to.have.property('apellido');",
                                "    pm.expect(jsonData.usuario).to.have.property('email');",
                                "});"
                            ]
                        }
                    }],
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"}
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "identificador": user.get('email', user.get('nombre_usuario', 'test_user')),
                                "clave": user['password_plain']
                            }, indent=2)
                        },
                        "url": {
                            "raw": f"{self.base_url}/api/auth/login",
                            "host": ["{{base_url}}"],
                            "path": ["api", "auth", "login"]
                        }
                    }
                })
        
        # Add error cases
        requests.extend([
            {
                "name": "Login Fallido - Credenciales Incorrectas",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 401', function () {",
                            "    pm.response.to.have.status(401);",
                            "});",
                            "",
                            "pm.test('Response has error message', function () {",
                            "    var jsonData = pm.response.json();",
                            "    pm.expect(jsonData).to.have.property('error');",
                            "    pm.expect(jsonData).to.have.property('mensaje');",
                            "});"
                        ]
                    }
                }],
                "request": {
                    "method": "POST",
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "identificador": list(self.data['users'].values())[0][0]['email'],
                            "clave": "wrongpassword"
                        }, indent=2)
                    },
                    "url": {
                        "raw": f"{self.base_url}/api/auth/login",
                        "host": ["{{base_url}}"],
                        "path": ["api", "auth", "login"]
                    }
                }
            },
            {
                "name": "Login Fallido - Usuario Inexistente",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 401', function () {",
                            "    pm.response.to.have.status(401);",
                            "});",
                            "",
                            "pm.test('Response indicates user not found', function () {",
                            "    var jsonData = pm.response.json();",
                            "    pm.expect(jsonData.mensaje).to.include('inexistente');",
                            "});"
                        ]
                    }
                }],
                "request": {
                    "method": "POST",
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "identificador": "noexiste@test.com",
                            "clave": "password123"
                        }, indent=2)
                    },
                    "url": {
                        "raw": f"{self.base_url}/api/auth/login",
                        "host": ["{{base_url}}"],
                        "path": ["api", "auth", "login"]
                    }
                }
            }
        ])
        
        # Add profile and logout endpoints
        requests.extend([
            {
                "name": "Obtener Perfil - Con Token Válido",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 200', function () {",
                            "    pm.response.to.have.status(200);",
                            "});",
                            "",
                            "pm.test('Response has user data', function () {",
                            "    var jsonData = pm.response.json();",
                            "    pm.expect(jsonData).to.have.property('usuario');",
                            "    pm.expect(jsonData.usuario).to.have.property('id');",
                            "    pm.expect(jsonData.usuario).to.have.property('nombreUsuario');",
                            "    pm.expect(jsonData.usuario).to.have.property('rol');",
                            "});"
                        ]
                    }
                }],
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{auth_token}}"}],
                    "url": {
                        "raw": f"{self.base_url}/api/auth/perfil",
                        "host": ["{{base_url}}"],
                        "path": ["api", "auth", "perfil"]
                    }
                }
            },
            {
                "name": "Obtener Perfil - Sin Token",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 401', function () {",
                            "    pm.response.to.have.status(401);",
                            "});",
                            "",
                            "pm.test('Response indicates missing token', function () {",
                            "    var jsonData = pm.response.json();",
                            "    pm.expect(jsonData.mensaje).to.include('requerido');",
                            "});"
                        ]
                    }
                }],
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": f"{self.base_url}/api/auth/perfil",
                        "host": ["{{base_url}}"],
                        "path": ["api", "auth", "perfil"]
                    }
                }
            },
            {
                "name": "Logout",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 200', function () {",
                            "    pm.response.to.have.status(200);",
                            "});",
                            "",
                            "pm.test('Response confirms logout', function () {",
                            "    var jsonData = pm.response.json();",
                            "    pm.expect(jsonData.mensaje).to.include('Logout exitoso');",
                            "});"
                        ]
                    }
                }],
                "request": {
                    "method": "POST",
                    "header": [{"key": "Authorization", "value": "Bearer {{auth_token}}"}],
                    "url": {
                        "raw": f"{self.base_url}/api/auth/logout",
                        "host": ["{{base_url}}"],
                        "path": ["api", "auth", "logout"]
                    }
                }
            }
        ])
        
        return {
            "info": {
                "_postman_id": "auth-collection-sql-driven",
                "name": "01 - Autenticación",
                "description": "Colección de autenticación generada automáticamente desde datos SQL. Incluye casos de prueba con usuarios reales de la base de datos.",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": requests,
            "variable": [
                {"key": "base_url", "value": "http://localhost:3000"}
            ]
        }
    
    def generate_users_collection(self) -> Dict:
        """Generate users collection with real user data"""
        logger.info("Generating users collection")
        
        user_cases = [case for case in self.data['test_mappings'] 
                     if case['test_category'] == 'users']
        
        requests = []
        
        # Get sample users for different scenarios
        presidente_user = self.data['users']['PRESIDENTE'][0] if 'PRESIDENTE' in self.data['users'] else None
        vocal_user = self.data['users']['VOCAL'][0] if 'VOCAL' in self.data['users'] else None
        coordinador_user = self.data['users']['COORDINADOR'][0] if 'COORDINADOR' in self.data['users'] else None
        voluntario_user = self.data['users']['VOLUNTARIO'][0] if 'VOLUNTARIO' in self.data['users'] else None
        
        # List users - success case (PRESIDENTE)
        if presidente_user:
            requests.append({
                "name": "Listar Usuarios - Presidente (Éxito)",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 200', function () {",
                            "    pm.response.to.have.status(200);",
                            "});",
                            "",
                            "pm.test('Response is array of users', function () {",
                            "    var jsonData = pm.response.json();",
                            "    pm.expect(jsonData).to.be.an('array');",
                            "    if (jsonData.length > 0) {",
                            "        pm.expect(jsonData[0]).to.have.property('id');",
                            "        pm.expect(jsonData[0]).to.have.property('nombreUsuario');",
                            "        pm.expect(jsonData[0]).to.have.property('rol');",
                            "    }",
                            "});"
                        ]
                    }
                }],
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": f"Bearer {{{{presidente_token}}}}"}],
                    "url": {
                        "raw": f"{self.base_url}/api/usuarios",
                        "host": ["{{base_url}}"],
                        "path": ["api", "usuarios"]
                    }
                }
            })
        
        # List users - authorization error (VOLUNTARIO)
        if voluntario_user:
            requests.append({
                "name": "Listar Usuarios - Voluntario (Sin Permisos)",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 403', function () {",
                            "    pm.response.to.have.status(403);",
                            "});",
                            "",
                            "pm.test('Response indicates insufficient permissions', function () {",
                            "    var jsonData = pm.response.json();",
                            "    pm.expect(jsonData.mensaje).to.include('permisos');",
                            "});"
                        ]
                    }
                }],
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{voluntario_token}}"}],
                    "url": {
                        "raw": f"{self.base_url}/api/usuarios",
                        "host": ["{{base_url}}"],
                        "path": ["api", "usuarios"]
                    }
                }
            })
        
        # Get specific user - success case
        if presidente_user and vocal_user:
            requests.append({
                "name": f"Obtener Usuario Específico - ID {vocal_user['id']}",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 200', function () {",
                            "    pm.response.to.have.status(200);",
                            "});",
                            "",
                            "pm.test('Response has correct user data', function () {",
                            "    var jsonData = pm.response.json();",
                            f"    pm.expect(jsonData.id).to.eql({vocal_user['id']});",
                            f"    pm.expect(jsonData.nombreUsuario).to.eql('{vocal_user['nombre_usuario']}');",
                            f"    pm.expect(jsonData.rol).to.eql('{vocal_user['rol']}');",
                            "});"
                        ]
                    }
                }],
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{presidente_token}}"}],
                    "url": {
                        "raw": f"{self.base_url}/api/usuarios/{vocal_user['id']}",
                        "host": ["{{base_url}}"],
                        "path": ["api", "usuarios", str(vocal_user['id'])]
                    }
                }
            })
        
        # Get non-existent user - error case
        requests.append({
            "name": "Obtener Usuario Inexistente - Error 404",
            "event": [{
                "listen": "test",
                "script": {
                    "exec": [
                        "pm.test('Status code is 404', function () {",
                        "    pm.response.to.have.status(404);",
                        "});",
                        "",
                        "pm.test('Response indicates user not found', function () {",
                        "    var jsonData = pm.response.json();",
                        "    pm.expect(jsonData.mensaje).to.include('encontrado');",
                        "});"
                    ]
                }
            }],
            "request": {
                "method": "GET",
                "header": [{"key": "Authorization", "value": "Bearer {{presidente_token}}"}],
                "url": {
                    "raw": f"{self.base_url}/api/usuarios/99999",
                    "host": ["{{base_url}}"],
                    "path": ["api", "usuarios", "99999"]
                }
            }
        })
        
        # Create user - success case (PRESIDENTE)
        if presidente_user:
            requests.append({
                "name": "Crear Usuario - Presidente (Éxito)",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 201', function () {",
                            "    pm.response.to.have.status(201);",
                            "});",
                            "",
                            "pm.test('Response has created user data', function () {",
                            "    var jsonData = pm.response.json();",
                            "    pm.expect(jsonData).to.have.property('id');",
                            "    pm.expect(jsonData).to.have.property('nombreUsuario');",
                            "    pm.expect(jsonData.nombreUsuario).to.eql('nuevo_test_user');",
                            "    pm.environment.set('created_user_id', jsonData.id);",
                            "});"
                        ]
                    }
                }],
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{presidente_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "nombreUsuario": "nuevo_test_user",
                            "nombre": "Nuevo",
                            "apellido": "Usuario",
                            "telefono": "1234567890",
                            "email": "nuevo@test.com",
                            "clave": "password123",
                            "rol": "VOLUNTARIO"
                        }, indent=2)
                    },
                    "url": {
                        "raw": f"{self.base_url}/api/usuarios",
                        "host": ["{{base_url}}"],
                        "path": ["api", "usuarios"]
                    }
                }
            })
        
        return {
            "info": {
                "_postman_id": "users-collection-sql-driven",
                "name": "02 - Usuarios",
                "description": "Colección de usuarios generada automáticamente desde datos SQL. Incluye casos con IDs reales de usuarios existentes.",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": requests,
            "variable": [
                {"key": "base_url", "value": "http://localhost:3000"}
            ]
        }    

    def generate_inventory_collection(self) -> Dict:
        """Generate inventory collection with real donation data"""
        logger.info("Generating inventory collection")
        
        requests = []
        
        # Get sample donations for different scenarios
        high_stock_donation = None
        low_stock_donation = None
        zero_stock_donation = None
        
        for category, donations in self.data['inventory'].items():
            if donations['high_stock'] and not high_stock_donation:
                high_stock_donation = donations['high_stock'][0]
            if donations['low_stock'] and not low_stock_donation:
                low_stock_donation = donations['low_stock'][0]
            if donations['zero_stock'] and not zero_stock_donation:
                zero_stock_donation = donations['zero_stock'][0]
        
        # List donations - success case
        requests.append({
            "name": "Listar Donaciones - Éxito",
            "event": [{
                "listen": "test",
                "script": {
                    "exec": [
                        "pm.test('Status code is 200', function () {",
                        "    pm.response.to.have.status(200);",
                        "});",
                        "",
                        "pm.test('Response is array of donations', function () {",
                        "    var jsonData = pm.response.json();",
                        "    pm.expect(jsonData).to.be.an('array');",
                        "    if (jsonData.length > 0) {",
                        "        pm.expect(jsonData[0]).to.have.property('id');",
                        "        pm.expect(jsonData[0]).to.have.property('categoria');",
                        "        pm.expect(jsonData[0]).to.have.property('descripcion');",
                        "        pm.expect(jsonData[0]).to.have.property('cantidad');",
                        "    }",
                        "});"
                    ]
                }
            }],
            "request": {
                "method": "GET",
                "header": [{"key": "Authorization", "value": "Bearer {{vocal_token}}"}],
                "url": {
                    "raw": f"{self.base_url}/api/inventario/donaciones",
                    "host": ["{{base_url}}"],
                    "path": ["api", "inventario", "donaciones"]
                }
            }
        })
        
        # Create donation - success case
        requests.append({
            "name": "Crear Donación - Vocal (Éxito)",
            "event": [{
                "listen": "test",
                "script": {
                    "exec": [
                        "pm.test('Status code is 201', function () {",
                        "    pm.response.to.have.status(201);",
                        "});",
                        "",
                        "pm.test('Response has created donation data', function () {",
                        "    var jsonData = pm.response.json();",
                        "    pm.expect(jsonData).to.have.property('id');",
                        "    pm.expect(jsonData.categoria).to.eql('ALIMENTOS');",
                        "    pm.expect(jsonData.descripcion).to.eql('Arroz integral 1kg - Test SQL');",
                        "    pm.environment.set('created_donation_id', jsonData.id);",
                        "});"
                    ]
                }
            }],
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Authorization", "value": "Bearer {{vocal_token}}"},
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "categoria": "ALIMENTOS",
                        "descripcion": "Arroz integral 1kg - Test SQL",
                        "cantidad": 25
                    }, indent=2)
                },
                "url": {
                    "raw": f"{self.base_url}/api/inventario/donaciones",
                    "host": ["{{base_url}}"],
                    "path": ["api", "inventario", "donaciones"]
                }
            }
        })
        
        # Create donation - authorization error (VOLUNTARIO)
        requests.append({
            "name": "Crear Donación - Voluntario (Sin Permisos)",
            "event": [{
                "listen": "test",
                "script": {
                    "exec": [
                        "pm.test('Status code is 403', function () {",
                        "    pm.response.to.have.status(403);",
                        "});",
                        "",
                        "pm.test('Response indicates insufficient permissions', function () {",
                        "    var jsonData = pm.response.json();",
                        "    pm.expect(jsonData.mensaje).to.include('permisos');",
                        "});"
                    ]
                }
            }],
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Authorization", "value": "Bearer {{voluntario_token}}"},
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "categoria": "ROPA",
                        "descripcion": "Camiseta M",
                        "cantidad": 10
                    }, indent=2)
                },
                "url": {
                    "raw": f"{self.base_url}/api/inventario/donaciones",
                    "host": ["{{base_url}}"],
                    "path": ["api", "inventario", "donaciones"]
                }
            }
        })
        
        # Update donation - success case with real donation
        if high_stock_donation:
            requests.append({
                "name": f"Actualizar Donación - ID {high_stock_donation['id']} (Éxito)",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 200', function () {",
                            "    pm.response.to.have.status(200);",
                            "});",
                            "",
                            "pm.test('Response has updated donation data', function () {",
                            "    var jsonData = pm.response.json();",
                            f"    pm.expect(jsonData.id).to.eql({high_stock_donation['id']});",
                            "    pm.expect(jsonData.descripcion).to.include('Actualizado');",
                            "});"
                        ]
                    }
                }],
                "request": {
                    "method": "PUT",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{vocal_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "descripcion": f"{high_stock_donation['descripcion']} - Actualizado",
                            "cantidad": high_stock_donation['cantidad'] + 5
                        }, indent=2)
                    },
                    "url": {
                        "raw": f"{self.base_url}/api/inventario/donaciones/{high_stock_donation['id']}",
                        "host": ["{{base_url}}"],
                        "path": ["api", "inventario", "donaciones", str(high_stock_donation['id'])]
                    }
                }
            })
        
        # Get donation by ID - success case
        if low_stock_donation:
            requests.append({
                "name": f"Obtener Donación - ID {low_stock_donation['id']}",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 200', function () {",
                            "    pm.response.to.have.status(200);",
                            "});",
                            "",
                            "pm.test('Response has correct donation data', function () {",
                            "    var jsonData = pm.response.json();",
                            f"    pm.expect(jsonData.id).to.eql({low_stock_donation['id']});",
                            f"    pm.expect(jsonData.categoria).to.eql('{low_stock_donation['categoria']}');",
                            f"    pm.expect(jsonData.descripcion).to.eql('{low_stock_donation['descripcion']}');",
                            "});"
                        ]
                    }
                }],
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{vocal_token}}"}],
                    "url": {
                        "raw": f"{self.base_url}/api/inventario/donaciones/{low_stock_donation['id']}",
                        "host": ["{{base_url}}"],
                        "path": ["api", "inventario", "donaciones", str(low_stock_donation['id'])]
                    }
                }
            })
        
        # Get non-existent donation - error case
        requests.append({
            "name": "Obtener Donación Inexistente - Error 404",
            "event": [{
                "listen": "test",
                "script": {
                    "exec": [
                        "pm.test('Status code is 404', function () {",
                        "    pm.response.to.have.status(404);",
                        "});",
                        "",
                        "pm.test('Response indicates donation not found', function () {",
                        "    var jsonData = pm.response.json();",
                        "    pm.expect(jsonData.mensaje).to.include('encontrada');",
                        "});"
                    ]
                }
            }],
            "request": {
                "method": "GET",
                "header": [{"key": "Authorization", "value": "Bearer {{vocal_token}}"}],
                "url": {
                    "raw": f"{self.base_url}/api/inventario/donaciones/99999",
                    "host": ["{{base_url}}"],
                    "path": ["api", "inventario", "donaciones", "99999"]
                }
            }
        })
        
        # Filter by category
        for category in self.data['inventory'].keys():
            requests.append({
                "name": f"Filtrar Donaciones por Categoría - {category}",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 200', function () {",
                            "    pm.response.to.have.status(200);",
                            "});",
                            "",
                            "pm.test('All donations have correct category', function () {",
                            "    var jsonData = pm.response.json();",
                            "    pm.expect(jsonData).to.be.an('array');",
                            "    jsonData.forEach(function(donation) {",
                            f"        pm.expect(donation.categoria).to.eql('{category}');",
                            "    });",
                            "});"
                        ]
                    }
                }],
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{vocal_token}}"}],
                    "url": {
                        "raw": f"{self.base_url}/api/inventario/donaciones?categoria={category}",
                        "host": ["{{base_url}}"],
                        "path": ["api", "inventario", "donaciones"],
                        "query": [{"key": "categoria", "value": category}]
                    }
                }
            })
            break  # Just add one category filter example
        
        return {
            "info": {
                "_postman_id": "inventory-collection-sql-driven",
                "name": "03 - Inventario",
                "description": "Colección de inventario generada automáticamente desde datos SQL. Incluye casos con IDs reales de donaciones existentes.",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": requests,
            "variable": [
                {"key": "base_url", "value": "http://localhost:3000"}
            ]
        }
    
    def generate_events_collection(self) -> Dict:
        """Generate events collection with real event data"""
        logger.info("Generating events collection")
        
        requests = []
        
        # Get sample events for different scenarios
        future_event = self.data['events']['future'][0] if self.data['events']['future'] else None
        past_event = self.data['events']['past'][0] if self.data['events']['past'] else None
        
        # List events - success case
        requests.append({
            "name": "Listar Eventos - Éxito",
            "event": [{
                "listen": "test",
                "script": {
                    "exec": [
                        "pm.test('Status code is 200', function () {",
                        "    pm.response.to.have.status(200);",
                        "});",
                        "",
                        "pm.test('Response is array of events', function () {",
                        "    var jsonData = pm.response.json();",
                        "    pm.expect(jsonData).to.be.an('array');",
                        "    if (jsonData.length > 0) {",
                        "        pm.expect(jsonData[0]).to.have.property('id');",
                        "        pm.expect(jsonData[0]).to.have.property('nombre');",
                        "        pm.expect(jsonData[0]).to.have.property('fechaHora');",
                        "    }",
                        "});"
                    ]
                }
            }],
            "request": {
                "method": "GET",
                "header": [{"key": "Authorization", "value": "Bearer {{coordinador_token}}"}],
                "url": {
                    "raw": f"{self.base_url}/api/eventos",
                    "host": ["{{base_url}}"],
                    "path": ["api", "eventos"]
                }
            }
        })
        
        # Create event - success case (future date)
        requests.append({
            "name": "Crear Evento Futuro - Coordinador (Éxito)",
            "event": [{
                "listen": "test",
                "script": {
                    "exec": [
                        "pm.test('Status code is 201', function () {",
                        "    pm.response.to.have.status(201);",
                        "});",
                        "",
                        "pm.test('Response has created event data', function () {",
                        "    var jsonData = pm.response.json();",
                        "    pm.expect(jsonData).to.have.property('id');",
                        "    pm.expect(jsonData.nombre).to.eql('Evento Test SQL Generado');",
                        "    pm.environment.set('created_event_id', jsonData.id);",
                        "});"
                    ]
                }
            }],
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Authorization", "value": "Bearer {{coordinador_token}}"},
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "nombre": "Evento Test SQL Generado",
                        "descripcion": "Evento creado automáticamente desde datos SQL",
                        "fechaHora": "2024-12-31T15:00:00Z"
                    }, indent=2)
                },
                "url": {
                    "raw": f"{self.base_url}/api/eventos",
                    "host": ["{{base_url}}"],
                    "path": ["api", "eventos"]
                }
            }
        })
        
        # Create event - validation error (past date)
        requests.append({
            "name": "Crear Evento Pasado - Error de Validación",
            "event": [{
                "listen": "test",
                "script": {
                    "exec": [
                        "pm.test('Status code is 400', function () {",
                        "    pm.response.to.have.status(400);",
                        "});",
                        "",
                        "pm.test('Response indicates validation error', function () {",
                        "    var jsonData = pm.response.json();",
                        "    pm.expect(jsonData.mensaje).to.include('fecha');",
                        "});"
                    ]
                }
            }],
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Authorization", "value": "Bearer {{coordinador_token}}"},
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "nombre": "Evento Pasado Test",
                        "descripcion": "Este evento debería fallar por fecha pasada",
                        "fechaHora": "2020-01-01T10:00:00Z"
                    }, indent=2)
                },
                "url": {
                    "raw": f"{self.base_url}/api/eventos",
                    "host": ["{{base_url}}"],
                    "path": ["api", "eventos"]
                }
            }
        })
        
        # Join event - success case with real future event
        if future_event:
            requests.append({
                "name": f"Unirse a Evento - ID {future_event['id']} (Éxito)",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 200', function () {",
                            "    pm.response.to.have.status(200);",
                            "});",
                            "",
                            "pm.test('Response confirms participation', function () {",
                            "    var jsonData = pm.response.json();",
                            "    pm.expect(jsonData.mensaje).to.include('participación');",
                            "});"
                        ]
                    }
                }],
                "request": {
                    "method": "POST",
                    "header": [{"key": "Authorization", "value": "Bearer {{voluntario_token}}"}],
                    "url": {
                        "raw": f"{self.base_url}/api/eventos/{future_event['id']}/participantes",
                        "host": ["{{base_url}}"],
                        "path": ["api", "eventos", str(future_event['id']), "participantes"]
                    }
                }
            })
        
        # Join event - error case with past event
        if past_event:
            requests.append({
                "name": f"Unirse a Evento Pasado - ID {past_event['id']} (Error)",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 400', function () {",
                            "    pm.response.to.have.status(400);",
                            "});",
                            "",
                            "pm.test('Response indicates event is past', function () {",
                            "    var jsonData = pm.response.json();",
                            "    pm.expect(jsonData.mensaje).to.include('pasado');",
                            "});"
                        ]
                    }
                }],
                "request": {
                    "method": "POST",
                    "header": [{"key": "Authorization", "value": "Bearer {{voluntario_token}}"}],
                    "url": {
                        "raw": f"{self.base_url}/api/eventos/{past_event['id']}/participantes",
                        "host": ["{{base_url}}"],
                        "path": ["api", "eventos", str(past_event['id']), "participantes"]
                    }
                }
            })
        
        # Get event participants
        if future_event:
            requests.append({
                "name": f"Obtener Participantes - Evento {future_event['id']}",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 200', function () {",
                            "    pm.response.to.have.status(200);",
                            "});",
                            "",
                            "pm.test('Response is array of participants', function () {",
                            "    var jsonData = pm.response.json();",
                            "    pm.expect(jsonData).to.be.an('array');",
                            "    if (jsonData.length > 0) {",
                            "        pm.expect(jsonData[0]).to.have.property('usuarioId');",
                            "        pm.expect(jsonData[0]).to.have.property('nombreUsuario');",
                            "    }",
                            "});"
                        ]
                    }
                }],
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{coordinador_token}}"}],
                    "url": {
                        "raw": f"{self.base_url}/api/eventos/{future_event['id']}/participantes",
                        "host": ["{{base_url}}"],
                        "path": ["api", "eventos", str(future_event['id']), "participantes"]
                    }
                }
            })
        
        return {
            "info": {
                "_postman_id": "events-collection-sql-driven",
                "name": "04 - Eventos",
                "description": "Colección de eventos generada automáticamente desde datos SQL. Incluye casos con IDs reales de eventos existentes.",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": requests,
            "variable": [
                {"key": "base_url", "value": "http://localhost:3000"}
            ]
        }
    
    def generate_network_collection(self) -> Dict:
        """Generate network collection with real inter-NGO data"""
        logger.info("Generating network collection")
        
        requests = []
        
        # Get sample data for network operations
        high_stock_donation = None
        for category, donations in self.data['inventory'].items():
            if donations['high_stock']:
                high_stock_donation = donations['high_stock'][0]
                break
        
        external_request = self.data['network']['external_requests'][0] if self.data['network']['external_requests'] else None
        external_offer = self.data['network']['external_offers'][0] if self.data['network']['external_offers'] else None
        external_event = self.data['network']['external_events'][0] if self.data['network']['external_events'] else None
        
        # List external donation requests
        requests.append({
            "name": "Listar Solicitudes Externas - Éxito",
            "event": [{
                "listen": "test",
                "script": {
                    "exec": [
                        "pm.test('Status code is 200', function () {",
                        "    pm.response.to.have.status(200);",
                        "});",
                        "",
                        "pm.test('Response is array of external requests', function () {",
                        "    var jsonData = pm.response.json();",
                        "    pm.expect(jsonData).to.be.an('array');",
                        "    if (jsonData.length > 0) {",
                        "        pm.expect(jsonData[0]).to.have.property('idOrganizacion');",
                        "        pm.expect(jsonData[0]).to.have.property('categoria');",
                        "        pm.expect(jsonData[0]).to.have.property('descripcion');",
                        "    }",
                        "});"
                    ]
                }
            }],
            "request": {
                "method": "GET",
                "header": [{"key": "Authorization", "value": "Bearer {{vocal_token}}"}],
                "url": {
                    "raw": f"{self.base_url}/api/red/solicitudes-donaciones",
                    "host": ["{{base_url}}"],
                    "path": ["api", "red", "solicitudes-donaciones"]
                }
            }
        })
        
        # Create donation request
        requests.append({
            "name": "Crear Solicitud de Donaciones - Vocal (Éxito)",
            "event": [{
                "listen": "test",
                "script": {
                    "exec": [
                        "pm.test('Status code is 201', function () {",
                        "    pm.response.to.have.status(201);",
                        "});",
                        "",
                        "pm.test('Response has created request data', function () {",
                        "    var jsonData = pm.response.json();",
                        "    pm.expect(jsonData).to.have.property('idSolicitud');",
                        "    pm.environment.set('solicitud_id', jsonData.idSolicitud);",
                        "});"
                    ]
                }
            }],
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Authorization", "value": "Bearer {{vocal_token}}"},
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "donaciones": [
                            {
                                "categoria": "ALIMENTOS",
                                "descripcion": "Arroz y fideos para familias necesitadas - SQL Test"
                            },
                            {
                                "categoria": "ROPA",
                                "descripcion": "Ropa de invierno para adultos - SQL Test"
                            }
                        ]
                    }, indent=2)
                },
                "url": {
                    "raw": f"{self.base_url}/api/red/solicitudes-donaciones",
                    "host": ["{{base_url}}"],
                    "path": ["api", "red", "solicitudes-donaciones"]
                }
            }
        })
        
        # List external donation offers
        requests.append({
            "name": "Listar Ofertas Externas - Éxito",
            "event": [{
                "listen": "test",
                "script": {
                    "exec": [
                        "pm.test('Status code is 200', function () {",
                        "    pm.response.to.have.status(200);",
                        "});",
                        "",
                        "pm.test('Response is array of external offers', function () {",
                        "    var jsonData = pm.response.json();",
                        "    pm.expect(jsonData).to.be.an('array');",
                        "    if (jsonData.length > 0) {",
                        "        pm.expect(jsonData[0]).to.have.property('idOrganizacion');",
                        "        pm.expect(jsonData[0]).to.have.property('categoria');",
                        "        pm.expect(jsonData[0]).to.have.property('cantidad');",
                        "    }",
                        "});"
                    ]
                }
            }],
            "request": {
                "method": "GET",
                "header": [{"key": "Authorization", "value": "Bearer {{vocal_token}}"}],
                "url": {
                    "raw": f"{self.base_url}/api/red/ofertas-donaciones",
                    "host": ["{{base_url}}"],
                    "path": ["api", "red", "ofertas-donaciones"]
                }
            }
        })
        
        # Create donation offer with real donation
        if high_stock_donation:
            requests.append({
                "name": f"Crear Oferta de Donaciones - Donación {high_stock_donation['id']}",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 201', function () {",
                            "    pm.response.to.have.status(201);",
                            "});",
                            "",
                            "pm.test('Response has created offer data', function () {",
                            "    var jsonData = pm.response.json();",
                            "    pm.expect(jsonData).to.have.property('idOferta');",
                            "    pm.environment.set('oferta_id', jsonData.idOferta);",
                            "});"
                        ]
                    }
                }],
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{vocal_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "donaciones": [
                                {
                                    "id": high_stock_donation['id'],
                                    "categoria": high_stock_donation['categoria'],
                                    "descripcion": high_stock_donation['descripcion'],
                                    "cantidad": min(10, high_stock_donation['cantidad'])
                                }
                            ]
                        }, indent=2)
                    },
                    "url": {
                        "raw": f"{self.base_url}/api/red/ofertas-donaciones",
                        "host": ["{{base_url}}"],
                        "path": ["api", "red", "ofertas-donaciones"]
                    }
                }
            })
        
        # Transfer donations with real data
        if high_stock_donation and external_request:
            requests.append({
                "name": f"Transferir Donaciones - Solicitud {external_request['id_solicitud']}",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 200', function () {",
                            "    pm.response.to.have.status(200);",
                            "});",
                            "",
                            "pm.test('Response confirms transfer', function () {",
                            "    var jsonData = pm.response.json();",
                            "    pm.expect(jsonData.mensaje).to.include('transferencia');",
                            "});"
                        ]
                    }
                }],
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{vocal_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "idSolicitud": external_request['id_solicitud'],
                            "idOrganizacion": external_request['id_organizacion'],
                            "donaciones": [
                                {
                                    "id": high_stock_donation['id'],
                                    "cantidad": min(5, high_stock_donation['cantidad'])
                                }
                            ]
                        }, indent=2)
                    },
                    "url": {
                        "raw": f"{self.base_url}/api/red/transferencias-donaciones",
                        "host": ["{{base_url}}"],
                        "path": ["api", "red", "transferencias-donaciones"]
                    }
                }
            })
        
        # List external events
        requests.append({
            "name": "Listar Eventos Externos - Éxito",
            "event": [{
                "listen": "test",
                "script": {
                    "exec": [
                        "pm.test('Status code is 200', function () {",
                        "    pm.response.to.have.status(200);",
                        "});",
                        "",
                        "pm.test('Response is array of external events', function () {",
                        "    var jsonData = pm.response.json();",
                        "    pm.expect(jsonData).to.be.an('array');",
                        "    if (jsonData.length > 0) {",
                        "        pm.expect(jsonData[0]).to.have.property('idOrganizacion');",
                        "        pm.expect(jsonData[0]).to.have.property('nombre');",
                        "        pm.expect(jsonData[0]).to.have.property('fechaHora');",
                        "    }",
                        "});"
                    ]
                }
            }],
            "request": {
                "method": "GET",
                "header": [{"key": "Authorization", "value": "Bearer {{voluntario_token}}"}],
                "url": {
                    "raw": f"{self.base_url}/api/red/eventos-externos",
                    "host": ["{{base_url}}"],
                    "path": ["api", "red", "eventos-externos"]
                }
            }
        })
        
        # Join external event with real data
        if external_event:
            requests.append({
                "name": f"Adherirse a Evento Externo - {external_event['id_evento']}",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 200', function () {",
                            "    pm.response.to.have.status(200);",
                            "});",
                            "",
                            "pm.test('Response confirms adhesion', function () {",
                            "    var jsonData = pm.response.json();",
                            "    pm.expect(jsonData.mensaje).to.include('adhesión');",
                            "});"
                        ]
                    }
                }],
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{voluntario_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "idOrganizacion": external_event['id_organizacion'],
                            "idEvento": external_event['id_evento']
                        }, indent=2)
                    },
                    "url": {
                        "raw": f"{self.base_url}/api/red/eventos-externos/adhesion",
                        "host": ["{{base_url}}"],
                        "path": ["api", "red", "eventos-externos", "adhesion"]
                    }
                }
            })
        
        # Authorization error - non-volunteer trying to join external event
        if external_event:
            requests.append({
                "name": "Adherirse a Evento Externo - Vocal (Sin Permisos)",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 403', function () {",
                            "    pm.response.to.have.status(403);",
                            "});",
                            "",
                            "pm.test('Response indicates insufficient permissions', function () {",
                            "    var jsonData = pm.response.json();",
                            "    pm.expect(jsonData.mensaje).to.include('voluntarios');",
                            "});"
                        ]
                    }
                }],
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{vocal_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "idOrganizacion": external_event['id_organizacion'],
                            "idEvento": external_event['id_evento']
                        }, indent=2)
                    },
                    "url": {
                        "raw": f"{self.base_url}/api/red/eventos-externos/adhesion",
                        "host": ["{{base_url}}"],
                        "path": ["api", "red", "eventos-externos", "adhesion"]
                    }
                }
            })
        
        return {
            "info": {
                "_postman_id": "network-collection-sql-driven",
                "name": "05 - Red ONGs",
                "description": "Colección de red inter-ONG generada automáticamente desde datos SQL. Incluye casos con datos reales de organizaciones externas.",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": requests,
            "variable": [
                {"key": "base_url", "value": "http://localhost:3000"}
            ]
        } 
   
    def save_collection(self, filename: str, collection: Dict) -> str:
        """Save a Postman collection to file"""
        file_path = Path(self.base_collection_path) / filename
        
        # Create backup of existing file
        if file_path.exists():
            backup_path = file_path.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            file_path.rename(backup_path)
            logger.info(f"Created backup: {backup_path}")
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save new collection
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved collection: {file_path}")
        return str(file_path)
    
    def update_environment_variables(self) -> str:
        """Update Postman environment with real data from SQL"""
        logger.info("Updating Postman environment variables")
        
        env_file = self.base_collection_path / "Sistema-ONG-Environment.postman_environment.json"
        
        # Create backup
        if env_file.exists():
            backup_path = env_file.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            env_file.rename(backup_path)
            logger.info(f"Created environment backup: {backup_path}")
        
        # Get sample IDs from real data
        sample_user_ids = {}
        for role, users in self.data['users'].items():
            if users:
                sample_user_ids[f'{role.lower()}_id'] = users[0]['id']
        
        sample_donation_id = None
        for category_data in self.data['inventory'].values():
            if category_data['all']:
                sample_donation_id = category_data['all'][0]['id']
                break
        
        sample_event_id = None
        if self.data['events']['all']:
            sample_event_id = self.data['events']['all'][0]['id']
        
        # Create updated environment
        environment = {
            "id": "sistema-ong-env-sql-driven",
            "name": "Sistema ONG - SQL Driven Testing",
            "values": [
                {
                    "key": "base_url",
                    "value": "http://localhost:3000",
                    "description": "URL base del API Gateway",
                    "enabled": True
                },
                {
                    "key": "auth_token",
                    "value": "",
                    "description": "Token JWT obtenido del login (se actualiza automáticamente)",
                    "enabled": True
                },
                {
                    "key": "user_id",
                    "value": "",
                    "description": "ID del usuario autenticado (se actualiza automáticamente)",
                    "enabled": True
                },
                {
                    "key": "user_role",
                    "value": "",
                    "description": "Rol del usuario autenticado (se actualiza automáticamente)",
                    "enabled": True
                }
            ]
        }
        
        # Add role-specific tokens and IDs
        for role in ['presidente', 'vocal', 'coordinador', 'voluntario']:
            environment["values"].extend([
                {
                    "key": f"{role}_token",
                    "value": "",
                    "description": f"Token JWT para usuario {role.title()} (para testing de permisos)",
                    "enabled": True
                },
                {
                    "key": f"{role}_id",
                    "value": sample_user_ids.get(f'{role}_id', ''),
                    "description": f"ID del usuario {role.title()} desde datos SQL",
                    "enabled": True
                }
            ])
        
        # Add resource IDs from real data
        environment["values"].extend([
            {
                "key": "sample_donation_id",
                "value": sample_donation_id or '',
                "description": "ID de donación de ejemplo desde datos SQL",
                "enabled": True
            },
            {
                "key": "sample_event_id",
                "value": sample_event_id or '',
                "description": "ID de evento de ejemplo desde datos SQL",
                "enabled": True
            },
            {
                "key": "created_user_id",
                "value": "",
                "description": "ID del último usuario creado (se actualiza automáticamente)",
                "enabled": True
            },
            {
                "key": "created_donation_id",
                "value": "",
                "description": "ID de la última donación creada (se actualiza automáticamente)",
                "enabled": True
            },
            {
                "key": "created_event_id",
                "value": "",
                "description": "ID del último evento creado (se actualiza automáticamente)",
                "enabled": True
            },
            {
                "key": "solicitud_id",
                "value": "",
                "description": "ID de la última solicitud creada (se actualiza automáticamente)",
                "enabled": True
            },
            {
                "key": "oferta_id",
                "value": "",
                "description": "ID de la última oferta creada (se actualiza automáticamente)",
                "enabled": True
            }
        ])
        
        # Add metadata
        environment.update({
            "_postman_variable_scope": "environment",
            "_postman_exported_at": datetime.now().isoformat() + "Z",
            "_postman_exported_using": "SQL-Driven Testing Generator"
        })
        
        # Save updated environment
        with open(env_file, 'w', encoding='utf-8') as f:
            json.dump(environment, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Updated environment file: {env_file}")
        return str(env_file)
    
    def generate_test_validation_scripts(self) -> Dict[str, List[str]]:
        """Generate validation scripts that check responses against known SQL data"""
        logger.info("Generating test validation scripts")
        
        validations = {}
        
        # User validation scripts
        for role, users in self.data['users'].items():
            if users:
                user = users[0]
                validations[f'validate_user_{role.lower()}'] = [
                    f"pm.test('User ID matches SQL data', function () {{",
                    f"    var jsonData = pm.response.json();",
                    f"    pm.expect(jsonData.usuario.id).to.eql({user['id']});",
                    f"}});",
                    f"pm.test('User role matches SQL data', function () {{",
                    f"    var jsonData = pm.response.json();",
                    f"    pm.expect(jsonData.usuario.rol).to.eql('{user['rol']}');",
                    f"}});",
                    f"pm.test('User email matches SQL data', function () {{",
                    f"    var jsonData = pm.response.json();",
                    f"    pm.expect(jsonData.usuario.email).to.eql('{user.get('email', user.get('nombre_usuario', 'test_user'))}');",
                    f"}};"
                ]
        
        # Donation validation scripts
        for category, donations in self.data['inventory'].items():
            if donations['all']:
                donation = donations['all'][0]
                validations[f'validate_donation_{category.lower()}'] = [
                    f"pm.test('Donation category matches SQL data', function () {{",
                    f"    var jsonData = pm.response.json();",
                    f"    pm.expect(jsonData.categoria).to.eql('{donation['categoria']}');",
                    f"}});",
                    f"pm.test('Donation description matches SQL data', function () {{",
                    f"    var jsonData = pm.response.json();",
                    f"    pm.expect(jsonData.descripcion).to.eql('{donation['descripcion']}');",
                    f"}});",
                    f"pm.test('Donation quantity is valid', function () {{",
                    f"    var jsonData = pm.response.json();",
                    f"    pm.expect(jsonData.cantidad).to.be.a('number');",
                    f"    pm.expect(jsonData.cantidad).to.be.at.least(0);",
                    f"}};"
                ]
        
        # Event validation scripts
        if self.data['events']['all']:
            event = self.data['events']['all'][0]
            validations['validate_event'] = [
                f"pm.test('Event name matches SQL data', function () {{",
                f"    var jsonData = pm.response.json();",
                f"    pm.expect(jsonData.nombre).to.eql('{event['nombre']}');",
                f"}});",
                f"pm.test('Event has valid date format', function () {{",
                f"    var jsonData = pm.response.json();",
                f"    pm.expect(jsonData.fechaHora).to.match(/^\\d{{4}}-\\d{{2}}-\\d{{2}}T\\d{{2}}:\\d{{2}}:\\d{{2}}/);",
                f"}});",
                f"pm.test('Event participants is array', function () {{",
                f"    var jsonData = pm.response.json();",
                f"    if (jsonData.participantes) {{",
                f"        pm.expect(jsonData.participantes).to.be.an('array');",
                f"    }}",
                f"}};"
            ]
        
        return validations
    
    def get_user_by_role(self, role: str) -> Optional[Dict]:
        """Get first user of specified role"""
        users = self.data['users'].get(role.upper(), [])
        return users[0] if users else None
    
    def get_donation_by_category(self, category: str, stock_level: str = 'all') -> Optional[Dict]:
        """Get first donation of specified category and stock level"""
        category_data = self.data['inventory'].get(category.upper(), {})
        donations = category_data.get(stock_level, [])
        return donations[0] if donations else None
    
    def get_event_by_status(self, status: str) -> Optional[Dict]:
        """Get first event of specified status (future, past, current)"""
        events = self.data['events'].get(status, [])
        return events[0] if events else None
    
    def generate_collection_summary(self) -> Dict[str, Any]:
        """Generate summary of all generated collections"""
        summary = {
            'generation_timestamp': datetime.now().isoformat(),
            'total_collections': 5,
            'collections': {
                '01-Autenticacion': {
                    'requests_count': len(self.data['users']) * 2 + 4,  # Login success/error + profile + logout
                    'test_scenarios': ['login_success', 'login_error', 'profile_access', 'logout']
                },
                '02-Usuarios': {
                    'requests_count': 4,  # List, get, create, error cases
                    'test_scenarios': ['list_users', 'get_user', 'create_user', 'authorization_error']
                },
                '03-Inventario': {
                    'requests_count': 6 + len(self.data['inventory']),  # CRUD + filter by category
                    'test_scenarios': ['list_donations', 'create_donation', 'update_donation', 'filter_by_category']
                },
                '04-Eventos': {
                    'requests_count': 6,  # CRUD + join + participants
                    'test_scenarios': ['list_events', 'create_event', 'join_event', 'validation_error']
                },
                '05-Red-ONGs': {
                    'requests_count': 8,  # Network operations
                    'test_scenarios': ['external_requests', 'donation_offers', 'transfers', 'external_events']
                }
            },
            'data_sources': {
                'users_by_role': {role: len(users) for role, users in self.data['users'].items()},
                'inventory_categories': list(self.data['inventory'].keys()),
                'events_total': len(self.data['events']['all']),
                'test_mappings': len(self.data['test_mappings'])
            },
            'environment_variables': {
                'role_tokens': ['presidente_token', 'vocal_token', 'coordinador_token', 'voluntario_token'],
                'resource_ids': ['sample_donation_id', 'sample_event_id'],
                'dynamic_ids': ['created_user_id', 'created_donation_id', 'created_event_id']
            }
        }
        
        return summary

def create_postman_generator_from_extracted_data(extracted_data: Dict[str, Any]) -> PostmanGenerator:
    """Factory function to create PostmanGenerator with extracted data"""
    return PostmanGenerator(extracted_data)

if __name__ == "__main__":
    # Example usage - this would normally be called from the orchestrator
    print("PostmanGenerator module loaded successfully")
    print("Use create_postman_generator_from_extracted_data() to create an instance")
    print("Then call generate_all_collections() to generate Postman collections")