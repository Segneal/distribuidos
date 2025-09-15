"""
Tests for authentication and authorization functionality
"""
import pytest
import jwt
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.usuario import Usuario, RolUsuario
from service.usuario_service import UsuarioServiceImpl
import user_pb2


class TestAutenticacion:
    """Test authentication functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.service = UsuarioServiceImpl()
        self.service.repository = Mock()
        self.service.jwt_secret = 'test-secret-key'
        self.service.jwt_expiration_hours = 24
    
    def test_autenticar_usuario_exitoso(self):
        """Test successful user authentication"""
        # Mock user data
        usuario_mock = Usuario(
            id=1,
            nombre_usuario='test_user',
            email='test@ong.com',
            rol=RolUsuario.PRESIDENTE.value,
            activo=True,
            clave_hash=Usuario.encriptar_contraseña('password123')
        )
        
        self.service.repository.obtener_usuario_por_identificador.return_value = usuario_mock
        
        # Create request
        request = user_pb2.AutenticarRequest(
            identificador='test_user',
            clave='password123'
        )
        
        # Mock context
        context = Mock()
        
        # Call method
        response = self.service.AutenticarUsuario(request, context)
        
        # Assertions
        assert response.exitoso is True
        assert response.mensaje == "Autenticación exitosa"
        assert response.token != ""
        assert response.usuario.nombreUsuario == 'test_user'
        
        # Verify token payload
        payload = jwt.decode(response.token, self.service.jwt_secret, algorithms=['HS256'])
        assert payload['user_id'] == 1
        assert payload['username'] == 'test_user'
        assert payload['role'] == RolUsuario.PRESIDENTE.value
    
    def test_autenticar_usuario_inexistente(self):
        """Test authentication with non-existent user"""
        self.service.repository.obtener_usuario_por_identificador.return_value = None
        
        request = user_pb2.AutenticarRequest(
            identificador='nonexistent',
            clave='password123'
        )
        
        context = Mock()
        response = self.service.AutenticarUsuario(request, context)
        
        assert response.exitoso is False
        assert response.mensaje == "Usuario/email inexistente"
        assert response.token == ""
    
    def test_autenticar_usuario_inactivo(self):
        """Test authentication with inactive user"""
        usuario_mock = Usuario(
            id=1,
            nombre_usuario='inactive_user',
            email='inactive@ong.com',
            rol=RolUsuario.VOLUNTARIO.value,
            activo=False,
            clave_hash=Usuario.encriptar_contraseña('password123')
        )
        
        self.service.repository.obtener_usuario_por_identificador.return_value = usuario_mock
        
        request = user_pb2.AutenticarRequest(
            identificador='inactive_user',
            clave='password123'
        )
        
        context = Mock()
        response = self.service.AutenticarUsuario(request, context)
        
        assert response.exitoso is False
        assert response.mensaje == "Usuario inactivo"
        assert response.token == ""
    
    def test_autenticar_contraseña_incorrecta(self):
        """Test authentication with incorrect password"""
        usuario_mock = Usuario(
            id=1,
            nombre_usuario='test_user',
            email='test@ong.com',
            rol=RolUsuario.PRESIDENTE.value,
            activo=True,
            clave_hash=Usuario.encriptar_contraseña('correct_password')
        )
        
        self.service.repository.obtener_usuario_por_identificador.return_value = usuario_mock
        
        request = user_pb2.AutenticarRequest(
            identificador='test_user',
            clave='wrong_password'
        )
        
        context = Mock()
        response = self.service.AutenticarUsuario(request, context)
        
        assert response.exitoso is False
        assert response.mensaje == "Credenciales incorrectas"
        assert response.token == ""
    
    def test_validar_token_valido(self):
        """Test token validation with valid token"""
        # Create valid token
        payload = {
            'user_id': 1,
            'username': 'test_user',
            'email': 'test@ong.com',
            'role': RolUsuario.PRESIDENTE.value,
            'exp': datetime.now(timezone.utc) + timedelta(hours=1),
            'iat': datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, self.service.jwt_secret, algorithm='HS256')
        
        # Mock user data
        usuario_mock = Usuario(
            id=1,
            nombre_usuario='test_user',
            email='test@ong.com',
            rol=RolUsuario.PRESIDENTE.value,
            activo=True
        )
        
        self.service.repository.obtener_usuario_por_id.return_value = usuario_mock
        
        request = user_pb2.ValidarTokenRequest(token=token)
        context = Mock()
        
        response = self.service.ValidarToken(request, context)
        
        assert response.exitoso is True
        assert response.mensaje == "Token válido"
        assert response.usuario.nombreUsuario == 'test_user'
    
    def test_validar_token_expirado(self):
        """Test token validation with expired token"""
        # Create expired token
        payload = {
            'user_id': 1,
            'username': 'test_user',
            'exp': datetime.now(timezone.utc) - timedelta(hours=1),  # Expired
            'iat': datetime.now(timezone.utc) - timedelta(hours=2)
        }
        token = jwt.encode(payload, self.service.jwt_secret, algorithm='HS256')
        
        request = user_pb2.ValidarTokenRequest(token=token)
        context = Mock()
        
        response = self.service.ValidarToken(request, context)
        
        assert response.exitoso is False
        assert response.mensaje == "Token expirado"
    
    def test_validar_token_invalido(self):
        """Test token validation with invalid token"""
        request = user_pb2.ValidarTokenRequest(token="invalid_token")
        context = Mock()
        
        response = self.service.ValidarToken(request, context)
        
        assert response.exitoso is False
        assert response.mensaje == "Token inválido"
    
    def test_validar_permisos_presidente_usuarios(self):
        """Test permission validation for PRESIDENTE accessing users"""
        # Create valid token for PRESIDENTE
        payload = {
            'user_id': 1,
            'username': 'presidente',
            'role': RolUsuario.PRESIDENTE.value,
            'exp': datetime.now(timezone.utc) + timedelta(hours=1),
            'iat': datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, self.service.jwt_secret, algorithm='HS256')
        
        # Mock user data
        usuario_mock = Usuario(
            id=1,
            nombre_usuario='presidente',
            rol=RolUsuario.PRESIDENTE.value,
            activo=True
        )
        
        self.service.repository.obtener_usuario_por_id.return_value = usuario_mock
        
        request = user_pb2.ValidarPermisosRequest(
            token=token,
            operacion='usuarios'
        )
        context = Mock()
        
        response = self.service.ValidarPermisos(request, context)
        
        assert response.exitoso is True
        assert response.mensaje == "Usuario autorizado"
    
    def test_validar_permisos_vocal_usuarios_denegado(self):
        """Test permission validation for VOCAL accessing users (should be denied)"""
        # Create valid token for VOCAL
        payload = {
            'user_id': 2,
            'username': 'vocal',
            'role': RolUsuario.VOCAL.value,
            'exp': datetime.now(timezone.utc) + timedelta(hours=1),
            'iat': datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, self.service.jwt_secret, algorithm='HS256')
        
        # Mock user data
        usuario_mock = Usuario(
            id=2,
            nombre_usuario='vocal',
            rol=RolUsuario.VOCAL.value,
            activo=True
        )
        
        self.service.repository.obtener_usuario_por_id.return_value = usuario_mock
        
        request = user_pb2.ValidarPermisosRequest(
            token=token,
            operacion='usuarios'
        )
        context = Mock()
        
        response = self.service.ValidarPermisos(request, context)
        
        assert response.exitoso is False
        assert "no tiene permisos para la operación: usuarios" in response.mensaje
    
    def test_validar_permisos_vocal_inventario_permitido(self):
        """Test permission validation for VOCAL accessing inventory (should be allowed)"""
        # Create valid token for VOCAL
        payload = {
            'user_id': 2,
            'username': 'vocal',
            'role': RolUsuario.VOCAL.value,
            'exp': datetime.now(timezone.utc) + timedelta(hours=1),
            'iat': datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, self.service.jwt_secret, algorithm='HS256')
        
        # Mock user data
        usuario_mock = Usuario(
            id=2,
            nombre_usuario='vocal',
            rol=RolUsuario.VOCAL.value,
            activo=True
        )
        
        self.service.repository.obtener_usuario_por_id.return_value = usuario_mock
        
        request = user_pb2.ValidarPermisosRequest(
            token=token,
            operacion='inventario'
        )
        context = Mock()
        
        response = self.service.ValidarPermisos(request, context)
        
        assert response.exitoso is True
        assert response.mensaje == "Usuario autorizado"


class TestAutorizacion:
    """Test authorization functionality in Usuario model"""
    
    def test_presidente_permisos_usuarios(self):
        """Test PRESIDENTE has permission for user management"""
        usuario = Usuario(rol=RolUsuario.PRESIDENTE.value)
        assert usuario.tiene_permiso_para_usuarios() is True
    
    def test_vocal_sin_permisos_usuarios(self):
        """Test VOCAL doesn't have permission for user management"""
        usuario = Usuario(rol=RolUsuario.VOCAL.value)
        assert usuario.tiene_permiso_para_usuarios() is False
    
    def test_vocal_permisos_inventario(self):
        """Test VOCAL has permission for inventory management"""
        usuario = Usuario(rol=RolUsuario.VOCAL.value)
        assert usuario.tiene_permiso_para_inventario() is True
    
    def test_voluntario_sin_permisos_inventario(self):
        """Test VOLUNTARIO doesn't have permission for inventory management"""
        usuario = Usuario(rol=RolUsuario.VOLUNTARIO.value)
        assert usuario.tiene_permiso_para_inventario() is False
    
    def test_coordinador_permisos_eventos(self):
        """Test COORDINADOR has permission for event management"""
        usuario = Usuario(rol=RolUsuario.COORDINADOR.value)
        assert usuario.tiene_permiso_para_eventos() is True
    
    def test_voluntario_sin_permisos_eventos(self):
        """Test VOLUNTARIO doesn't have permission for event management"""
        usuario = Usuario(rol=RolUsuario.VOLUNTARIO.value)
        assert usuario.tiene_permiso_para_eventos() is False
    
    def test_voluntario_auto_asignacion_eventos(self):
        """Test VOLUNTARIO can self-assign to events"""
        usuario = Usuario(rol=RolUsuario.VOLUNTARIO.value)
        assert usuario.puede_auto_asignarse_eventos() is True
    
    def test_presidente_no_auto_asignacion_eventos(self):
        """Test PRESIDENTE cannot self-assign to events (manages others)"""
        usuario = Usuario(rol=RolUsuario.PRESIDENTE.value)
        assert usuario.puede_auto_asignarse_eventos() is False
    
    def test_todos_pueden_participar_eventos(self):
        """Test all roles can participate in events"""
        roles = [RolUsuario.PRESIDENTE.value, RolUsuario.VOCAL.value, 
                RolUsuario.COORDINADOR.value, RolUsuario.VOLUNTARIO.value]
        
        for rol in roles:
            usuario = Usuario(rol=rol)
            assert usuario.puede_participar_en_eventos() is True
    
    def test_validar_permisos_operacion_usuarios(self):
        """Test static permission validation for user operations"""
        assert Usuario.validar_permisos_operacion(RolUsuario.PRESIDENTE.value, 'usuarios') is True
        assert Usuario.validar_permisos_operacion(RolUsuario.VOCAL.value, 'usuarios') is False
        assert Usuario.validar_permisos_operacion(RolUsuario.COORDINADOR.value, 'usuarios') is False
        assert Usuario.validar_permisos_operacion(RolUsuario.VOLUNTARIO.value, 'usuarios') is False
    
    def test_validar_permisos_operacion_inventario(self):
        """Test static permission validation for inventory operations"""
        assert Usuario.validar_permisos_operacion(RolUsuario.PRESIDENTE.value, 'inventario') is True
        assert Usuario.validar_permisos_operacion(RolUsuario.VOCAL.value, 'inventario') is True
        assert Usuario.validar_permisos_operacion(RolUsuario.COORDINADOR.value, 'inventario') is False
        assert Usuario.validar_permisos_operacion(RolUsuario.VOLUNTARIO.value, 'inventario') is False
    
    def test_validar_permisos_operacion_eventos(self):
        """Test static permission validation for event operations"""
        assert Usuario.validar_permisos_operacion(RolUsuario.PRESIDENTE.value, 'eventos') is True
        assert Usuario.validar_permisos_operacion(RolUsuario.VOCAL.value, 'eventos') is False
        assert Usuario.validar_permisos_operacion(RolUsuario.COORDINADOR.value, 'eventos') is True
        assert Usuario.validar_permisos_operacion(RolUsuario.VOLUNTARIO.value, 'eventos') is False
    
    def test_validar_permisos_auto_asignar_eventos(self):
        """Test static permission validation for self-assignment to events"""
        assert Usuario.validar_permisos_operacion(RolUsuario.PRESIDENTE.value, 'auto_asignar_eventos') is False
        assert Usuario.validar_permisos_operacion(RolUsuario.VOCAL.value, 'auto_asignar_eventos') is False
        assert Usuario.validar_permisos_operacion(RolUsuario.COORDINADOR.value, 'auto_asignar_eventos') is False
        assert Usuario.validar_permisos_operacion(RolUsuario.VOLUNTARIO.value, 'auto_asignar_eventos') is True


class TestManejadorErroresAutenticacion:
    """Test authentication error handling"""
    
    def setup_method(self):
        """Setup test environment"""
        self.service = UsuarioServiceImpl()
        self.service.repository = Mock()
        self.service.jwt_secret = 'test-secret-key'
    
    def test_autenticar_error_base_datos(self):
        """Test authentication with database error"""
        self.service.repository.obtener_usuario_por_identificador.side_effect = Exception("Database error")
        
        request = user_pb2.AutenticarRequest(
            identificador='test_user',
            clave='password123'
        )
        
        context = Mock()
        response = self.service.AutenticarUsuario(request, context)
        
        assert response.exitoso is False
        assert response.mensaje == "Error interno del servidor"
        context.set_code.assert_called_once()
        context.set_details.assert_called_once()
    
    def test_validar_token_error_base_datos(self):
        """Test token validation with database error"""
        # Create valid token
        payload = {
            'user_id': 1,
            'username': 'test_user',
            'exp': datetime.now(timezone.utc) + timedelta(hours=1),
            'iat': datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, self.service.jwt_secret, algorithm='HS256')
        
        self.service.repository.obtener_usuario_por_id.side_effect = Exception("Database error")
        
        request = user_pb2.ValidarTokenRequest(token=token)
        context = Mock()
        
        response = self.service.ValidarToken(request, context)
        
        assert response.exitoso is False
        assert response.mensaje == "Error interno del servidor"
        context.set_code.assert_called_once()
        context.set_details.assert_called_once()
    
    def test_validar_permisos_error_base_datos(self):
        """Test permission validation with database error"""
        # Create valid token
        payload = {
            'user_id': 1,
            'username': 'test_user',
            'exp': datetime.now(timezone.utc) + timedelta(hours=1),
            'iat': datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, self.service.jwt_secret, algorithm='HS256')
        
        self.service.repository.obtener_usuario_por_id.side_effect = Exception("Database error")
        
        request = user_pb2.ValidarPermisosRequest(
            token=token,
            operacion='usuarios'
        )
        context = Mock()
        
        response = self.service.ValidarPermisos(request, context)
        
        assert response.exitoso is False
        assert response.mensaje == "Error interno del servidor"
        context.set_code.assert_called_once()
        context.set_details.assert_called_once()