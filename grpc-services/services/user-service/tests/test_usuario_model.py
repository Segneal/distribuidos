"""
Unit tests for Usuario model
"""
import pytest
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from models.usuario import Usuario, RolUsuario

class TestUsuarioModel:
    """Test cases for Usuario model"""
    
    def test_validar_email_valido(self):
        """Test valid email validation"""
        assert Usuario.validar_email("test@example.com") == True
        assert Usuario.validar_email("user.name@domain.co.uk") == True
        assert Usuario.validar_email("test+tag@example.org") == True
    
    def test_validar_email_invalido(self):
        """Test invalid email validation"""
        assert Usuario.validar_email("invalid-email") == False
        assert Usuario.validar_email("@example.com") == False
        assert Usuario.validar_email("test@") == False
        assert Usuario.validar_email("") == False
    
    def test_validar_nombre_usuario_valido(self):
        """Test valid username validation"""
        assert Usuario.validar_nombre_usuario("test_user") == True
        assert Usuario.validar_nombre_usuario("user123") == True
        assert Usuario.validar_nombre_usuario("TestUser") == True
    
    def test_validar_nombre_usuario_invalido(self):
        """Test invalid username validation"""
        assert Usuario.validar_nombre_usuario("ab") == False  # Too short
        assert Usuario.validar_nombre_usuario("") == False  # Empty
        assert Usuario.validar_nombre_usuario("user-name") == False  # Invalid character
        assert Usuario.validar_nombre_usuario("user@name") == False  # Invalid character
        assert Usuario.validar_nombre_usuario("a" * 51) == False  # Too long
    
    def test_validar_rol_valido(self):
        """Test valid role validation"""
        assert Usuario.validar_rol("PRESIDENTE") == True
        assert Usuario.validar_rol("VOCAL") == True
        assert Usuario.validar_rol("COORDINADOR") == True
        assert Usuario.validar_rol("VOLUNTARIO") == True
    
    def test_validar_rol_invalido(self):
        """Test invalid role validation"""
        assert Usuario.validar_rol("INVALID_ROLE") == False
        assert Usuario.validar_rol("") == False
        assert Usuario.validar_rol("presidente") == False  # Case sensitive
    
    def test_generar_contraseña_aleatoria(self):
        """Test random password generation"""
        password1 = Usuario.generar_contraseña_aleatoria()
        password2 = Usuario.generar_contraseña_aleatoria()
        
        assert len(password1) == 12  # Default length
        assert len(password2) == 12
        assert password1 != password2  # Should be different
        
        # Test custom length
        password3 = Usuario.generar_contraseña_aleatoria(8)
        assert len(password3) == 8
    
    def test_encriptar_y_verificar_contraseña(self):
        """Test password encryption and verification"""
        password = "test_password_123"
        hash_password = Usuario.encriptar_contraseña(password)
        
        assert hash_password != password  # Should be encrypted
        assert Usuario.verificar_contraseña(password, hash_password) == True
        assert Usuario.verificar_contraseña("wrong_password", hash_password) == False
    
    def test_validar_datos_creacion_validos(self):
        """Test valid user creation data"""
        usuario = Usuario(
            nombre_usuario="test_user",
            nombre="Test",
            apellido="User",
            telefono="123-456-7890",
            email="test@example.com",
            rol="VOLUNTARIO"
        )
        
        validacion = usuario.validar_datos_creacion()
        assert validacion['valido'] == True
        assert len(validacion['errores']) == 0
    
    def test_validar_datos_creacion_invalidos(self):
        """Test invalid user creation data"""
        usuario = Usuario(
            nombre_usuario="",  # Invalid: empty
            nombre="",  # Invalid: empty
            apellido="",  # Invalid: empty
            telefono="invalid-phone!@#",  # Invalid: special chars
            email="invalid-email",  # Invalid: format
            rol="INVALID_ROLE"  # Invalid: not in enum
        )
        
        validacion = usuario.validar_datos_creacion()
        assert validacion['valido'] == False
        assert len(validacion['errores']) > 0
    
    def test_to_dict(self):
        """Test converting user to dictionary"""
        usuario = Usuario(
            id=1,
            nombre_usuario="test_user",
            nombre="Test",
            apellido="User",
            email="test@example.com",
            rol="VOLUNTARIO"
        )
        
        user_dict = usuario.to_dict()
        assert user_dict['id'] == 1
        assert user_dict['nombre_usuario'] == "test_user"
        assert user_dict['nombre'] == "Test"
        assert 'clave_hash' not in user_dict  # Should not include by default
        
        # Test including password hash
        user_dict_with_hash = usuario.to_dict(incluir_clave_hash=True)
        assert 'clave_hash' in user_dict_with_hash
    
    def test_from_dict(self):
        """Test creating user from dictionary"""
        user_data = {
            'id': 1,
            'nombre_usuario': 'test_user',
            'nombre': 'Test',
            'apellido': 'User',
            'email': 'test@example.com',
            'rol': 'VOLUNTARIO',
            'activo': True
        }
        
        usuario = Usuario.from_dict(user_data)
        assert usuario.id == 1
        assert usuario.nombre_usuario == 'test_user'
        assert usuario.nombre == 'Test'
        assert usuario.activo == True