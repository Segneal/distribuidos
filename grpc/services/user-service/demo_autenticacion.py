#!/usr/bin/env python3
"""
Demo script for authentication and authorization functionality
"""
import sys
import os
import jwt
from datetime import datetime, timedelta, timezone

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.usuario import Usuario, RolUsuario
from service.usuario_service import UsuarioServiceImpl
import user_pb2
from unittest.mock import Mock

def demo_authentication():
    """Demonstrate authentication functionality"""
    print("=" * 60)
    print("DEMO: AUTENTICACIÓN Y AUTORIZACIÓN")
    print("=" * 60)
    
    # Create service instance
    service = UsuarioServiceImpl()
    service.repository = Mock()
    service.jwt_secret = 'demo-secret-key'
    service.jwt_expiration_hours = 24
    
    print("\n1. CREACIÓN DE USUARIOS DE PRUEBA")
    print("-" * 40)
    
    # Create test users for different roles
    usuarios_prueba = [
        Usuario(
            id=1,
            nombre_usuario='presidente',
            nombre='Juan',
            apellido='Pérez',
            email='presidente@ong.com',
            rol=RolUsuario.PRESIDENTE.value,
            activo=True,
            clave_hash=Usuario.encriptar_contraseña('admin123')
        ),
        Usuario(
            id=2,
            nombre_usuario='vocal',
            nombre='María',
            apellido='González',
            email='vocal@ong.com',
            rol=RolUsuario.VOCAL.value,
            activo=True,
            clave_hash=Usuario.encriptar_contraseña('vocal123')
        ),
        Usuario(
            id=3,
            nombre_usuario='coordinador',
            nombre='Carlos',
            apellido='López',
            email='coordinador@ong.com',
            rol=RolUsuario.COORDINADOR.value,
            activo=True,
            clave_hash=Usuario.encriptar_contraseña('coord123')
        ),
        Usuario(
            id=4,
            nombre_usuario='voluntario',
            nombre='Ana',
            apellido='Martínez',
            email='voluntario@ong.com',
            rol=RolUsuario.VOLUNTARIO.value,
            activo=True,
            clave_hash=Usuario.encriptar_contraseña('volun123')
        ),
        Usuario(
            id=5,
            nombre_usuario='inactivo',
            nombre='Pedro',
            apellido='Sánchez',
            email='inactivo@ong.com',
            rol=RolUsuario.VOLUNTARIO.value,
            activo=False,
            clave_hash=Usuario.encriptar_contraseña('inact123')
        )
    ]
    
    for usuario in usuarios_prueba:
        print(f"✓ {usuario.rol}: {usuario.nombre_usuario} ({usuario.email}) - Activo: {usuario.activo}")
    
    print("\n2. PRUEBAS DE AUTENTICACIÓN")
    print("-" * 40)
    
    # Test successful authentication
    def test_authentication(identificador, clave, usuario_esperado):
        service.repository.obtener_usuario_por_identificador.return_value = usuario_esperado
        
        request = user_pb2.AutenticarRequest(
            identificador=identificador,
            clave=clave
        )
        
        context = Mock()
        response = service.AutenticarUsuario(request, context)
        
        if response.exitoso:
            print(f"✓ Autenticación exitosa para {identificador}")
            print(f"  Token generado: {response.token[:50]}...")
            
            # Decode and show token payload
            payload = jwt.decode(response.token, service.jwt_secret, algorithms=['HS256'])
            print(f"  Usuario ID: {payload['user_id']}")
            print(f"  Rol: {payload['role']}")
            print(f"  Expira: {datetime.fromtimestamp(payload['exp'])}")
            return response.token
        else:
            print(f"✗ Autenticación fallida para {identificador}: {response.mensaje}")
            return None
    
    # Test authentication scenarios
    print("\n2.1 Autenticación exitosa:")
    token_presidente = test_authentication('presidente', 'admin123', usuarios_prueba[0])
    token_vocal = test_authentication('vocal@ong.com', 'vocal123', usuarios_prueba[1])
    
    print("\n2.2 Autenticación fallida:")
    test_authentication('presidente', 'wrong_password', usuarios_prueba[0])
    test_authentication('nonexistent', 'any_password', None)
    test_authentication('inactivo', 'inact123', usuarios_prueba[4])
    
    print("\n3. PRUEBAS DE VALIDACIÓN DE TOKENS")
    print("-" * 40)
    
    def test_token_validation(token, usuario_esperado, descripcion):
        if not token:
            print(f"✗ {descripcion}: No hay token para validar")
            return
        
        service.repository.obtener_usuario_por_id.return_value = usuario_esperado
        
        request = user_pb2.ValidarTokenRequest(token=token)
        context = Mock()
        response = service.ValidarToken(request, context)
        
        if response.exitoso:
            print(f"✓ {descripcion}: Token válido")
            print(f"  Usuario: {response.usuario.nombreUsuario} ({response.usuario.rol})")
        else:
            print(f"✗ {descripcion}: {response.mensaje}")
    
    # Test token validation
    test_token_validation(token_presidente, usuarios_prueba[0], "Token de Presidente")
    test_token_validation(token_vocal, usuarios_prueba[1], "Token de Vocal")
    test_token_validation("invalid_token", None, "Token inválido")
    
    # Test expired token
    expired_payload = {
        'user_id': 1,
        'username': 'test',
        'exp': datetime.now(timezone.utc) - timedelta(hours=1),
        'iat': datetime.now(timezone.utc) - timedelta(hours=2)
    }
    expired_token = jwt.encode(expired_payload, service.jwt_secret, algorithm='HS256')
    test_token_validation(expired_token, usuarios_prueba[0], "Token expirado")
    
    print("\n4. PRUEBAS DE AUTORIZACIÓN")
    print("-" * 40)
    
    def test_authorization(token, usuario_esperado, operacion, descripcion):
        if not token:
            print(f"✗ {descripcion}: No hay token para validar")
            return
        
        service.repository.obtener_usuario_por_id.return_value = usuario_esperado
        
        request = user_pb2.ValidarPermisosRequest(
            token=token,
            operacion=operacion
        )
        context = Mock()
        response = service.ValidarPermisos(request, context)
        
        if response.exitoso:
            print(f"✓ {descripcion}: Autorizado")
        else:
            print(f"✗ {descripcion}: {response.mensaje}")
    
    # Test authorization scenarios
    print("\n4.1 Gestión de usuarios (solo PRESIDENTE):")
    test_authorization(token_presidente, usuarios_prueba[0], 'usuarios', "Presidente accediendo a usuarios")
    test_authorization(token_vocal, usuarios_prueba[1], 'usuarios', "Vocal accediendo a usuarios")
    
    print("\n4.2 Gestión de inventario (PRESIDENTE, VOCAL):")
    test_authorization(token_presidente, usuarios_prueba[0], 'inventario', "Presidente accediendo a inventario")
    test_authorization(token_vocal, usuarios_prueba[1], 'inventario', "Vocal accediendo a inventario")
    
    # Create tokens for other roles
    token_coordinador = None
    token_voluntario = None
    
    if len(usuarios_prueba) > 2:
        service.repository.obtener_usuario_por_identificador.return_value = usuarios_prueba[2]
        request = user_pb2.AutenticarRequest(identificador='coordinador', clave='coord123')
        context = Mock()
        response = service.AutenticarUsuario(request, context)
        if response.exitoso:
            token_coordinador = response.token
        
        service.repository.obtener_usuario_por_identificador.return_value = usuarios_prueba[3]
        request = user_pb2.AutenticarRequest(identificador='voluntario', clave='volun123')
        context = Mock()
        response = service.AutenticarUsuario(request, context)
        if response.exitoso:
            token_voluntario = response.token
    
    print("\n4.3 Gestión de eventos (PRESIDENTE, COORDINADOR):")
    test_authorization(token_presidente, usuarios_prueba[0], 'eventos', "Presidente accediendo a eventos")
    test_authorization(token_coordinador, usuarios_prueba[2], 'eventos', "Coordinador accediendo a eventos")
    test_authorization(token_vocal, usuarios_prueba[1], 'eventos', "Vocal accediendo a eventos")
    
    print("\n4.4 Auto-asignación a eventos (solo VOLUNTARIO):")
    test_authorization(token_voluntario, usuarios_prueba[3], 'auto_asignar_eventos', "Voluntario auto-asignándose")
    test_authorization(token_presidente, usuarios_prueba[0], 'auto_asignar_eventos', "Presidente auto-asignándose")
    
    print("\n5. PRUEBAS DE MÉTODOS DE AUTORIZACIÓN EN MODELO")
    print("-" * 40)
    
    print("\n5.1 Permisos por rol:")
    for usuario in usuarios_prueba[:4]:  # Exclude inactive user
        print(f"\n{usuario.rol} ({usuario.nombre_usuario}):")
        print(f"  - Gestión usuarios: {'✓' if usuario.tiene_permiso_para_usuarios() else '✗'}")
        print(f"  - Gestión inventario: {'✓' if usuario.tiene_permiso_para_inventario() else '✗'}")
        print(f"  - Gestión eventos: {'✓' if usuario.tiene_permiso_para_eventos() else '✗'}")
        print(f"  - Participar eventos: {'✓' if usuario.puede_participar_en_eventos() else '✗'}")
        print(f"  - Auto-asignarse eventos: {'✓' if usuario.puede_auto_asignarse_eventos() else '✗'}")
        print(f"  - Gestionar participantes: {'✓' if usuario.puede_gestionar_participantes() else '✗'}")
    
    print("\n5.2 Validación estática de permisos:")
    operaciones = ['usuarios', 'inventario', 'eventos', 'auto_asignar_eventos']
    roles = [RolUsuario.PRESIDENTE.value, RolUsuario.VOCAL.value, 
             RolUsuario.COORDINADOR.value, RolUsuario.VOLUNTARIO.value]
    
    print("\nMatriz de permisos:")
    print(f"{'Operación':<20} {'PRESIDENTE':<12} {'VOCAL':<8} {'COORDINADOR':<12} {'VOLUNTARIO':<10}")
    print("-" * 70)
    
    for operacion in operaciones:
        permisos = []
        for rol in roles:
            tiene_permiso = Usuario.validar_permisos_operacion(rol, operacion)
            permisos.append('✓' if tiene_permiso else '✗')
        
        print(f"{operacion:<20} {permisos[0]:<12} {permisos[1]:<8} {permisos[2]:<12} {permisos[3]:<10}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETADO")
    print("=" * 60)

if __name__ == '__main__':
    demo_authentication()