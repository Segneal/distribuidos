"""
Basic tests for User Service structure
"""
import pytest
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from models.usuario import Usuario, RolUsuario
        from config.database import DatabaseConfig
        from config.email import EmailConfig
        assert True
    except ImportError as e:
        pytest.fail(f"Import error: {e}")

def test_grpc_imports():
    """Test that gRPC modules can be imported"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '../src/grpc'))
        import user_pb2
        import user_pb2_grpc
        assert True
    except ImportError as e:
        pytest.fail(f"gRPC import error: {e}")

def test_usuario_model_creation():
    """Test basic Usuario model creation"""
    from models.usuario import Usuario
    
    usuario = Usuario(
        nombre_usuario="test_user",
        nombre="Test",
        apellido="User",
        email="test@example.com",
        rol="VOLUNTARIO"
    )
    
    assert usuario.nombre_usuario == "test_user"
    assert usuario.nombre == "Test"
    assert usuario.rol == "VOLUNTARIO"

def test_password_generation():
    """Test password generation functionality"""
    from models.usuario import Usuario
    
    password1 = Usuario.generar_contraseña_aleatoria()
    password2 = Usuario.generar_contraseña_aleatoria()
    
    assert len(password1) == 12
    assert len(password2) == 12
    assert password1 != password2

def test_password_encryption():
    """Test password encryption and verification"""
    from models.usuario import Usuario
    
    password = "test_password_123"
    encrypted = Usuario.encriptar_contraseña(password)
    
    assert encrypted != password
    assert Usuario.verificar_contraseña(password, encrypted) == True
    assert Usuario.verificar_contraseña("wrong_password", encrypted) == False