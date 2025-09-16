#!/usr/bin/env python3
"""
Demo script showing CRUD operations for User Service
This script demonstrates all the implemented CRUD operations
"""
import sys
import os
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/grpc'))

from models.usuario import Usuario, RolUsuario
from usuario_service import UsuarioServiceImpl
import user_pb2

def demo_crud_operations():
    """Demonstrate all CRUD operations"""
    print("=== Demo: Sistema ONG - User Service CRUD Operations ===\n")
    
    # Initialize service
    service = UsuarioServiceImpl()
    mock_context = MagicMock()
    
    print("1. CREAR USUARIO (Create User)")
    print("-" * 40)
    
    # Mock the repository and email for demo
    with patch('repositories.usuario_repository.UsuarioRepository.crear_usuario') as mock_crear, \
         patch('config.email.email_config.send_password_email') as mock_email:
        
        # Setup mocks
        usuario_creado = Usuario(
            id=1,
            nombre_usuario="juan_perez",
            nombre="Juan",
            apellido="Pérez",
            telefono="11-2345-6789",
            email="juan.perez@ong.com",
            rol="VOLUNTARIO",
            activo=True,
            usuario_alta="admin"
        )
        mock_crear.return_value = usuario_creado
        mock_email.return_value = True
        
        # Create user request
        request = user_pb2.CrearUsuarioRequest(
            nombreUsuario="juan_perez",
            nombre="Juan",
            apellido="Pérez",
            telefono="11-2345-6789",
            email="juan.perez@ong.com",
            rol="VOLUNTARIO",
            usuarioCreador="admin"
        )
        
        response = service.CrearUsuario(request, mock_context)
        
        print(f"✓ Usuario creado exitosamente:")
        print(f"  - ID: {response.usuario.id}")
        print(f"  - Usuario: {response.usuario.nombreUsuario}")
        print(f"  - Nombre: {response.usuario.nombre} {response.usuario.apellido}")
        print(f"  - Email: {response.usuario.email}")
        print(f"  - Rol: {response.usuario.rol}")
        print(f"  - Mensaje: {response.mensaje}")
        print(f"  - Email enviado: {'Sí' if mock_email.called else 'No'}")
    
    print("\n2. OBTENER USUARIO (Get User)")
    print("-" * 40)
    
    with patch('repositories.usuario_repository.UsuarioRepository.obtener_usuario_por_id') as mock_obtener:
        mock_obtener.return_value = usuario_creado
        
        request = user_pb2.ObtenerUsuarioRequest(id=1)
        response = service.ObtenerUsuario(request, mock_context)
        
        print(f"✓ Usuario encontrado:")
        print(f"  - ID: {response.usuario.id}")
        print(f"  - Usuario: {response.usuario.nombreUsuario}")
        print(f"  - Email: {response.usuario.email}")
        print(f"  - Estado: {'Activo' if response.usuario.activo else 'Inactivo'}")
    
    print("\n3. LISTAR USUARIOS (List Users)")
    print("-" * 40)
    
    with patch('repositories.usuario_repository.UsuarioRepository.listar_usuarios') as mock_listar:
        usuarios = [
            Usuario(id=1, nombre_usuario="juan_perez", nombre="Juan", apellido="Pérez", 
                   email="juan.perez@ong.com", rol="VOLUNTARIO", activo=True),
            Usuario(id=2, nombre_usuario="maria_garcia", nombre="María", apellido="García", 
                   email="maria.garcia@ong.com", rol="VOCAL", activo=True),
            Usuario(id=3, nombre_usuario="admin", nombre="Administrador", apellido="Sistema", 
                   email="admin@ong.com", rol="PRESIDENTE", activo=True)
        ]
        mock_listar.return_value = (usuarios, 3)
        
        request = user_pb2.ListarUsuariosRequest(
            pagina=1,
            tamanoPagina=10,
            incluirInactivos=False
        )
        response = service.ListarUsuarios(request, mock_context)
        
        print(f"✓ Usuarios encontrados: {response.totalRegistros}")
        for i, usuario in enumerate(response.usuarios, 1):
            print(f"  {i}. {usuario.nombreUsuario} ({usuario.nombre} {usuario.apellido}) - {usuario.rol}")
    
    print("\n4. ACTUALIZAR USUARIO (Update User)")
    print("-" * 40)
    
    with patch('repositories.usuario_repository.UsuarioRepository.obtener_usuario_por_id') as mock_obtener, \
         patch('repositories.usuario_repository.UsuarioRepository.actualizar_usuario') as mock_actualizar:
        
        usuario_actualizado = Usuario(
            id=1,
            nombre_usuario="juan_perez_updated",
            nombre="Juan Carlos",
            apellido="Pérez",
            telefono="11-2345-6789",
            email="juan.carlos.perez@ong.com",
            rol="COORDINADOR",  # Promoted!
            activo=True
        )
        
        mock_obtener.return_value = usuario_creado
        mock_actualizar.return_value = usuario_actualizado
        
        request = user_pb2.ActualizarUsuarioRequest(
            id=1,
            nombreUsuario="juan_perez_updated",
            nombre="Juan Carlos",
            email="juan.carlos.perez@ong.com",
            rol="COORDINADOR",
            usuarioModificacion="admin"
        )
        
        response = service.ActualizarUsuario(request, mock_context)
        
        print(f"✓ Usuario actualizado:")
        print(f"  - Nuevo usuario: {response.usuario.nombreUsuario}")
        print(f"  - Nuevo nombre: {response.usuario.nombre}")
        print(f"  - Nuevo email: {response.usuario.email}")
        print(f"  - Nuevo rol: {response.usuario.rol}")
    
    print("\n5. AUTENTICAR USUARIO (Authenticate User)")
    print("-" * 40)
    
    with patch('repositories.usuario_repository.UsuarioRepository.obtener_usuario_por_identificador') as mock_obtener:
        # Create user with encrypted password
        password = "mi_contraseña_123"
        hash_password = Usuario.encriptar_contraseña(password)
        
        usuario_auth = Usuario(
            id=1,
            nombre_usuario="juan_perez",
            nombre="Juan",
            apellido="Pérez",
            email="juan.perez@ong.com",
            rol="VOLUNTARIO",
            activo=True,
            clave_hash=hash_password
        )
        mock_obtener.return_value = usuario_auth
        
        request = user_pb2.AutenticarRequest(
            identificador="juan_perez",
            clave=password
        )
        
        response = service.AutenticarUsuario(request, mock_context)
        
        print(f"✓ Autenticación exitosa:")
        print(f"  - Usuario: {response.usuario.nombreUsuario}")
        print(f"  - Token generado: {'Sí' if response.token else 'No'}")
        print(f"  - Token (primeros 20 chars): {response.token[:20]}...")
    
    print("\n6. ELIMINAR USUARIO (Delete User - Logical)")
    print("-" * 40)
    
    with patch('repositories.usuario_repository.UsuarioRepository.eliminar_usuario') as mock_eliminar:
        mock_eliminar.return_value = True
        
        request = user_pb2.EliminarUsuarioRequest(
            id=1,
            usuarioEliminacion="admin"
        )
        
        response = service.EliminarUsuario(request, mock_context)
        
        print(f"✓ Usuario eliminado (baja lógica):")
        print(f"  - Resultado: {response.mensaje}")
        print(f"  - Eliminado por: admin")
    
    print("\n7. VALIDACIÓN DE DATOS")
    print("-" * 40)
    
    # Test data validation
    usuario_invalido = Usuario(
        nombre_usuario="ab",  # Too short
        nombre="",  # Empty
        email="invalid-email",  # Invalid format
        rol="INVALID_ROLE"  # Invalid role
    )
    
    validacion = usuario_invalido.validar_datos_creacion()
    print(f"✓ Validación de datos inválidos:")
    print(f"  - Válido: {validacion['valido']}")
    print(f"  - Errores encontrados: {len(validacion['errores'])}")
    for error in validacion['errores']:
        print(f"    • {error}")
    
    print("\n8. GENERACIÓN DE CONTRASEÑA")
    print("-" * 40)
    
    password1 = Usuario.generar_contraseña_aleatoria()
    password2 = Usuario.generar_contraseña_aleatoria(16)
    
    print(f"✓ Contraseñas generadas:")
    print(f"  - Contraseña 1 (12 chars): {password1}")
    print(f"  - Contraseña 2 (16 chars): {password2}")
    print(f"  - Son diferentes: {'Sí' if password1 != password2 else 'No'}")
    
    print("\n" + "=" * 60)
    print("✅ DEMO COMPLETADO - Todas las operaciones CRUD funcionan correctamente")
    print("=" * 60)

if __name__ == "__main__":
    demo_crud_operations()