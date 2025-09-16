"""
Integration tests for Usuario CRUD operations
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/grpc'))

from models.usuario import Usuario, RolUsuario
from repositories.usuario_repository import UsuarioRepository

# Import gRPC modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/grpc'))
from service.usuario_service import UsuarioServiceImpl
import user_pb2

class TestUsuarioCRUD:
    """Test cases for Usuario CRUD operations"""
    
    def setup_method(self):
        """Setup test environment"""
        self.service = UsuarioServiceImpl()
        self.mock_context = Mock()
    
    @patch('repositories.usuario_repository.UsuarioRepository.crear_usuario')
    @patch('config.email.email_config.send_password_email')
    def test_crear_usuario_exitoso(self, mock_email, mock_crear):
        """Test successful user creation"""
        # Setup mocks
        usuario_creado = Usuario(
            id=1,
            nombre_usuario="test_user",
            nombre="Test",
            apellido="User",
            telefono="123-456-7890",
            email="test@example.com",
            rol="VOLUNTARIO",
            activo=True,
            usuario_alta="admin"
        )
        mock_crear.return_value = usuario_creado
        mock_email.return_value = True
        
        # Create request
        request = user_pb2.CrearUsuarioRequest(
            nombreUsuario="test_user",
            nombre="Test",
            apellido="User",
            telefono="123-456-7890",
            email="test@example.com",
            rol="VOLUNTARIO",
            usuarioCreador="admin"
        )
        
        # Execute
        response = self.service.CrearUsuario(request, self.mock_context)
        
        # Verify
        assert response.exitoso == True
        assert response.mensaje == "Usuario creado exitosamente"
        assert response.usuario.nombreUsuario == "test_user"
        assert response.usuario.email == "test@example.com"
        mock_crear.assert_called_once()
        mock_email.assert_called_once()
    
    def test_crear_usuario_datos_invalidos(self):
        """Test user creation with invalid data"""
        # Create request with invalid data
        request = user_pb2.CrearUsuarioRequest(
            nombreUsuario="",  # Invalid: empty
            nombre="",  # Invalid: empty
            apellido="User",
            telefono="123-456-7890",
            email="invalid-email",  # Invalid: format
            rol="INVALID_ROLE",  # Invalid: not in enum
            usuarioCreador="admin"
        )
        
        # Execute
        response = self.service.CrearUsuario(request, self.mock_context)
        
        # Verify
        assert response.exitoso == False
        assert "Datos inválidos" in response.mensaje
    
    @patch('repositories.usuario_repository.UsuarioRepository.obtener_usuario_por_id')
    def test_obtener_usuario_existente(self, mock_obtener):
        """Test getting existing user"""
        # Setup mock
        usuario = Usuario(
            id=1,
            nombre_usuario="test_user",
            nombre="Test",
            apellido="User",
            email="test@example.com",
            rol="VOLUNTARIO",
            activo=True
        )
        mock_obtener.return_value = usuario
        
        # Create request
        request = user_pb2.ObtenerUsuarioRequest(id=1)
        
        # Execute
        response = self.service.ObtenerUsuario(request, self.mock_context)
        
        # Verify
        assert response.exitoso == True
        assert response.mensaje == "Usuario encontrado"
        assert response.usuario.id == 1
        assert response.usuario.nombreUsuario == "test_user"
        mock_obtener.assert_called_once_with(1)
    
    @patch('repositories.usuario_repository.UsuarioRepository.obtener_usuario_por_id')
    def test_obtener_usuario_no_existente(self, mock_obtener):
        """Test getting non-existent user"""
        # Setup mock
        mock_obtener.return_value = None
        
        # Create request
        request = user_pb2.ObtenerUsuarioRequest(id=999)
        
        # Execute
        response = self.service.ObtenerUsuario(request, self.mock_context)
        
        # Verify
        assert response.exitoso == False
        assert response.mensaje == "Usuario no encontrado"
        mock_obtener.assert_called_once_with(999)
    
    @patch('repositories.usuario_repository.UsuarioRepository.listar_usuarios')
    def test_listar_usuarios(self, mock_listar):
        """Test listing users"""
        # Setup mock
        usuarios = [
            Usuario(id=1, nombre_usuario="user1", nombre="User", apellido="One", 
                   email="user1@example.com", rol="VOLUNTARIO", activo=True),
            Usuario(id=2, nombre_usuario="user2", nombre="User", apellido="Two", 
                   email="user2@example.com", rol="VOCAL", activo=True)
        ]
        mock_listar.return_value = (usuarios, 2)
        
        # Create request
        request = user_pb2.ListarUsuariosRequest(
            pagina=1,
            tamanoPagina=10,
            incluirInactivos=False
        )
        
        # Execute
        response = self.service.ListarUsuarios(request, self.mock_context)
        
        # Verify
        assert response.exitoso == True
        assert response.totalRegistros == 2
        assert len(response.usuarios) == 2
        assert response.usuarios[0].nombreUsuario == "user1"
        assert response.usuarios[1].nombreUsuario == "user2"
        mock_listar.assert_called_once_with(
            pagina=1, 
            tamaño_pagina=10, 
            incluir_inactivos=False
        )
    
    @patch('repositories.usuario_repository.UsuarioRepository.obtener_usuario_por_id')
    @patch('repositories.usuario_repository.UsuarioRepository.actualizar_usuario')
    def test_actualizar_usuario_exitoso(self, mock_actualizar, mock_obtener):
        """Test successful user update"""
        # Setup mocks
        usuario_existente = Usuario(
            id=1,
            nombre_usuario="test_user",
            nombre="Test",
            apellido="User",
            telefono="123-456-7890",
            email="test@example.com",
            rol="VOLUNTARIO",
            activo=True
        )
        
        usuario_actualizado = Usuario(
            id=1,
            nombre_usuario="updated_user",
            nombre="Updated",
            apellido="User",
            telefono="123-456-7890",
            email="updated@example.com",
            rol="VOCAL",
            activo=True
        )
        
        mock_obtener.return_value = usuario_existente
        mock_actualizar.return_value = usuario_actualizado
        
        # Create request
        request = user_pb2.ActualizarUsuarioRequest(
            id=1,
            nombreUsuario="updated_user",
            nombre="Updated",
            email="updated@example.com",
            rol="VOCAL",
            usuarioModificacion="admin"
        )
        
        # Execute
        response = self.service.ActualizarUsuario(request, self.mock_context)
        
        # Verify
        assert response.exitoso == True
        assert response.mensaje == "Usuario actualizado exitosamente"
        assert response.usuario.nombreUsuario == "updated_user"
        assert response.usuario.nombre == "Updated"
        assert response.usuario.email == "updated@example.com"
        assert response.usuario.rol == "VOCAL"
        mock_obtener.assert_called_once_with(1)
        mock_actualizar.assert_called_once()
    
    @patch('repositories.usuario_repository.UsuarioRepository.obtener_usuario_por_id')
    def test_actualizar_usuario_no_existente(self, mock_obtener):
        """Test updating non-existent user"""
        # Setup mock
        mock_obtener.return_value = None
        
        # Create request
        request = user_pb2.ActualizarUsuarioRequest(
            id=999,
            nombreUsuario="updated_user",
            usuarioModificacion="admin"
        )
        
        # Execute
        response = self.service.ActualizarUsuario(request, self.mock_context)
        
        # Verify
        assert response.exitoso == False
        assert response.mensaje == "Usuario no encontrado"
        mock_obtener.assert_called_once_with(999)
    
    @patch('repositories.usuario_repository.UsuarioRepository.eliminar_usuario')
    def test_eliminar_usuario_exitoso(self, mock_eliminar):
        """Test successful user deletion (logical)"""
        # Setup mock
        mock_eliminar.return_value = True
        
        # Create request
        request = user_pb2.EliminarUsuarioRequest(
            id=1,
            usuarioEliminacion="admin"
        )
        
        # Execute
        response = self.service.EliminarUsuario(request, self.mock_context)
        
        # Verify
        assert response.exitoso == True
        assert response.mensaje == "Usuario eliminado exitosamente"
        mock_eliminar.assert_called_once_with(1, "admin")
    
    @patch('repositories.usuario_repository.UsuarioRepository.eliminar_usuario')
    def test_eliminar_usuario_no_existente(self, mock_eliminar):
        """Test deleting non-existent user"""
        # Setup mock
        mock_eliminar.return_value = False
        
        # Create request
        request = user_pb2.EliminarUsuarioRequest(
            id=999,
            usuarioEliminacion="admin"
        )
        
        # Execute
        response = self.service.EliminarUsuario(request, self.mock_context)
        
        # Verify
        assert response.exitoso == False
        assert response.mensaje == "Usuario no encontrado o ya eliminado"
        mock_eliminar.assert_called_once_with(999, "admin")
    
    @patch('repositories.usuario_repository.UsuarioRepository.obtener_usuario_por_identificador')
    def test_autenticar_usuario_exitoso(self, mock_obtener):
        """Test successful user authentication"""
        # Setup mock
        password = "test_password"
        hash_password = Usuario.encriptar_contraseña(password)
        
        usuario = Usuario(
            id=1,
            nombre_usuario="test_user",
            nombre="Test",
            apellido="User",
            email="test@example.com",
            rol="VOLUNTARIO",
            activo=True,
            clave_hash=hash_password
        )
        mock_obtener.return_value = usuario
        
        # Create request
        request = user_pb2.AutenticarRequest(
            identificador="test_user",
            clave=password
        )
        
        # Execute
        response = self.service.AutenticarUsuario(request, self.mock_context)
        
        # Verify
        assert response.exitoso == True
        assert response.mensaje == "Autenticación exitosa"
        assert response.token != ""
        assert response.usuario.nombreUsuario == "test_user"
        mock_obtener.assert_called_once_with("test_user")
    
    @patch('repositories.usuario_repository.UsuarioRepository.obtener_usuario_por_identificador')
    def test_autenticar_usuario_inexistente(self, mock_obtener):
        """Test authentication with non-existent user"""
        # Setup mock
        mock_obtener.return_value = None
        
        # Create request
        request = user_pb2.AutenticarRequest(
            identificador="nonexistent_user",
            clave="password"
        )
        
        # Execute
        response = self.service.AutenticarUsuario(request, self.mock_context)
        
        # Verify
        assert response.exitoso == False
        assert response.mensaje == "Usuario/email inexistente"
        mock_obtener.assert_called_once_with("nonexistent_user")
    
    @patch('repositories.usuario_repository.UsuarioRepository.obtener_usuario_por_identificador')
    def test_autenticar_usuario_inactivo(self, mock_obtener):
        """Test authentication with inactive user"""
        # Setup mock
        usuario = Usuario(
            id=1,
            nombre_usuario="test_user",
            activo=False  # Inactive user
        )
        mock_obtener.return_value = usuario
        
        # Create request
        request = user_pb2.AutenticarRequest(
            identificador="test_user",
            clave="password"
        )
        
        # Execute
        response = self.service.AutenticarUsuario(request, self.mock_context)
        
        # Verify
        assert response.exitoso == False
        assert response.mensaje == "Usuario inactivo"
        mock_obtener.assert_called_once_with("test_user")
    
    @patch('repositories.usuario_repository.UsuarioRepository.obtener_usuario_por_identificador')
    def test_autenticar_credenciales_incorrectas(self, mock_obtener):
        """Test authentication with incorrect credentials"""
        # Setup mock
        password = "correct_password"
        hash_password = Usuario.encriptar_contraseña(password)
        
        usuario = Usuario(
            id=1,
            nombre_usuario="test_user",
            activo=True,
            clave_hash=hash_password
        )
        mock_obtener.return_value = usuario
        
        # Create request with wrong password
        request = user_pb2.AutenticarRequest(
            identificador="test_user",
            clave="wrong_password"
        )
        
        # Execute
        response = self.service.AutenticarUsuario(request, self.mock_context)
        
        # Verify
        assert response.exitoso == False
        assert response.mensaje == "Credenciales incorrectas"
        mock_obtener.assert_called_once_with("test_user")