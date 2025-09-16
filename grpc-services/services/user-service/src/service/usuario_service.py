"""
gRPC User Service Implementation
"""
import os
import sys
import jwt
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import grpc
import user_pb2
import user_pb2_grpc
from models.usuario import Usuario, RolUsuario
from config.database import db_config
from config.email import email_config
from repositories.usuario_repository import UsuarioRepository

logger = logging.getLogger(__name__)

class UsuarioServiceImpl(user_pb2_grpc.UsuarioServiceServicer):
    """gRPC User Service Implementation"""
    
    def __init__(self):
        self.repository = UsuarioRepository()
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key')
        self.jwt_expiration_hours = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
    
    def CrearUsuario(self, request, context):
        """Create new user with random password and email notification"""
        try:
            # Create user object from request
            usuario = Usuario(
                nombre_usuario=request.nombreUsuario,
                nombre=request.nombre,
                apellido=request.apellido,
                telefono=request.telefono,
                email=request.email,
                rol=request.rol,
                usuario_alta=request.usuarioCreador
            )
            
            # Validate user data
            validacion = usuario.validar_datos_creacion()
            if not validacion['valido']:
                return user_pb2.UsuarioResponse(
                    exitoso=False,
                    mensaje=f"Datos inválidos: {', '.join(validacion['errores'])}"
                )
            
            # Generate random password
            contraseña_temporal = Usuario.generar_contraseña_aleatoria()
            usuario.clave_hash = Usuario.encriptar_contraseña(contraseña_temporal)
            
            # Create user in database
            usuario_creado = self.repository.crear_usuario(usuario)
            if not usuario_creado:
                return user_pb2.UsuarioResponse(
                    exitoso=False,
                    mensaje="Error al crear usuario en base de datos"
                )
            
            # Send email with temporary password
            email_enviado = email_config.send_password_email(
                usuario.email, 
                usuario.nombre_usuario, 
                contraseña_temporal
            )
            
            if not email_enviado:
                logger.warning(f"Failed to send email to {usuario.email}")
            
            # Convert to protobuf message
            usuario_pb = self._usuario_to_pb(usuario_creado)
            
            return user_pb2.UsuarioResponse(
                exitoso=True,
                mensaje="Usuario creado exitosamente",
                usuario=usuario_pb
            )
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return user_pb2.UsuarioResponse(
                exitoso=False,
                mensaje="Error interno del servidor"
            )
    
    def ObtenerUsuario(self, request, context):
        """Get user by ID"""
        try:
            usuario = self.repository.obtener_usuario_por_id(request.id)
            if not usuario:
                return user_pb2.UsuarioResponse(
                    exitoso=False,
                    mensaje="Usuario no encontrado"
                )
            
            usuario_pb = self._usuario_to_pb(usuario)
            return user_pb2.UsuarioResponse(
                exitoso=True,
                mensaje="Usuario encontrado",
                usuario=usuario_pb
            )
            
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return user_pb2.UsuarioResponse(
                exitoso=False,
                mensaje="Error interno del servidor"
            )
    
    def ListarUsuarios(self, request, context):
        """List users with pagination"""
        try:
            usuarios, total = self.repository.listar_usuarios(
                pagina=request.pagina or 1,
                tamaño_pagina=request.tamanoPagina or 10,
                incluir_inactivos=request.incluirInactivos
            )
            
            usuarios_pb = [self._usuario_to_pb(usuario) for usuario in usuarios]
            
            return user_pb2.ListarUsuariosResponse(
                exitoso=True,
                mensaje=f"Se encontraron {len(usuarios)} usuarios",
                usuarios=usuarios_pb,
                totalRegistros=total
            )
            
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return user_pb2.ListarUsuariosResponse(
                exitoso=False,
                mensaje="Error interno del servidor"
            )
    
    def ActualizarUsuario(self, request, context):
        """Update user (excluding password)"""
        try:
            # Get existing user
            usuario_existente = self.repository.obtener_usuario_por_id(request.id)
            if not usuario_existente:
                return user_pb2.UsuarioResponse(
                    exitoso=False,
                    mensaje="Usuario no encontrado"
                )
            
            # Update fields if provided
            if request.nombreUsuario:
                usuario_existente.nombre_usuario = request.nombreUsuario
            if request.nombre:
                usuario_existente.nombre = request.nombre
            if request.apellido:
                usuario_existente.apellido = request.apellido
            if request.telefono:
                usuario_existente.telefono = request.telefono
            if request.email:
                usuario_existente.email = request.email
            if request.rol:
                usuario_existente.rol = request.rol
            
            usuario_existente.usuario_modificacion = request.usuarioModificacion
            
            # Validate updated data
            validacion = usuario_existente.validar_datos_actualizacion()
            if not validacion['valido']:
                return user_pb2.UsuarioResponse(
                    exitoso=False,
                    mensaje=f"Datos inválidos: {', '.join(validacion['errores'])}"
                )
            
            # Update in database
            usuario_actualizado = self.repository.actualizar_usuario(usuario_existente)
            if not usuario_actualizado:
                return user_pb2.UsuarioResponse(
                    exitoso=False,
                    mensaje="Error al actualizar usuario"
                )
            
            usuario_pb = self._usuario_to_pb(usuario_actualizado)
            return user_pb2.UsuarioResponse(
                exitoso=True,
                mensaje="Usuario actualizado exitosamente",
                usuario=usuario_pb
            )
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return user_pb2.UsuarioResponse(
                exitoso=False,
                mensaje="Error interno del servidor"
            )
    
    def EliminarUsuario(self, request, context):
        """Logical delete user"""
        try:
            resultado = self.repository.eliminar_usuario(request.id, request.usuarioEliminacion)
            if resultado:
                return user_pb2.EliminarUsuarioResponse(
                    exitoso=True,
                    mensaje="Usuario eliminado exitosamente"
                )
            else:
                return user_pb2.EliminarUsuarioResponse(
                    exitoso=False,
                    mensaje="Usuario no encontrado o ya eliminado"
                )
                
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return user_pb2.EliminarUsuarioResponse(
                exitoso=False,
                mensaje="Error interno del servidor"
            )
    
    def AutenticarUsuario(self, request, context):
        """Authenticate user and generate JWT token"""
        try:
            # Find user by username or email
            usuario = self.repository.obtener_usuario_por_identificador(request.identificador)
            
            if not usuario:
                return user_pb2.AutenticarResponse(
                    exitoso=False,
                    mensaje="Usuario/email inexistente"
                )
            
            if not usuario.activo:
                return user_pb2.AutenticarResponse(
                    exitoso=False,
                    mensaje="Usuario inactivo"
                )
            
            # Verify password
            if not Usuario.verificar_contraseña(request.clave, usuario.clave_hash):
                return user_pb2.AutenticarResponse(
                    exitoso=False,
                    mensaje="Credenciales incorrectas"
                )
            
            # Generate JWT token
            token = self._generar_token_jwt(usuario)
            usuario_pb = self._usuario_to_pb(usuario)
            
            return user_pb2.AutenticarResponse(
                exitoso=True,
                mensaje="Autenticación exitosa",
                token=token,
                usuario=usuario_pb
            )
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return user_pb2.AutenticarResponse(
                exitoso=False,
                mensaje="Error interno del servidor"
            )
    
    def ValidarToken(self, request, context):
        """Validate JWT token"""
        try:
            payload = jwt.decode(request.token, self.jwt_secret, algorithms=['HS256'])
            usuario_id = payload.get('user_id')
            
            if not usuario_id:
                return user_pb2.ValidarTokenResponse(
                    exitoso=False,
                    mensaje="Token inválido"
                )
            
            usuario = self.repository.obtener_usuario_por_id(usuario_id)
            if not usuario or not usuario.activo:
                return user_pb2.ValidarTokenResponse(
                    exitoso=False,
                    mensaje="Usuario no válido"
                )
            
            usuario_pb = self._usuario_to_pb(usuario)
            return user_pb2.ValidarTokenResponse(
                exitoso=True,
                mensaje="Token válido",
                usuario=usuario_pb
            )
            
        except jwt.ExpiredSignatureError:
            return user_pb2.ValidarTokenResponse(
                exitoso=False,
                mensaje="Token expirado"
            )
        except jwt.InvalidTokenError:
            return user_pb2.ValidarTokenResponse(
                exitoso=False,
                mensaje="Token inválido"
            )
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return user_pb2.ValidarTokenResponse(
                exitoso=False,
                mensaje="Error interno del servidor"
            )
    
    def ValidarPermisos(self, request, context):
        """Validate user permissions for specific operation"""
        try:
            # Validate token first
            payload = jwt.decode(request.token, self.jwt_secret, algorithms=['HS256'])
            usuario_id = payload.get('user_id')
            
            if not usuario_id:
                return user_pb2.ValidarPermisosResponse(
                    exitoso=False,
                    mensaje="Token inválido"
                )
            
            usuario = self.repository.obtener_usuario_por_id(usuario_id)
            if not usuario or not usuario.activo:
                return user_pb2.ValidarPermisosResponse(
                    exitoso=False,
                    mensaje="Usuario no válido"
                )
            
            # Validate permissions for the requested operation
            tiene_permiso = Usuario.validar_permisos_operacion(usuario.rol, request.operacion)
            
            if not tiene_permiso:
                return user_pb2.ValidarPermisosResponse(
                    exitoso=False,
                    mensaje=f"Usuario no tiene permisos para la operación: {request.operacion}"
                )
            
            usuario_pb = self._usuario_to_pb(usuario)
            return user_pb2.ValidarPermisosResponse(
                exitoso=True,
                mensaje="Usuario autorizado",
                usuario=usuario_pb
            )
            
        except jwt.ExpiredSignatureError:
            return user_pb2.ValidarPermisosResponse(
                exitoso=False,
                mensaje="Token expirado"
            )
        except jwt.InvalidTokenError:
            return user_pb2.ValidarPermisosResponse(
                exitoso=False,
                mensaje="Token inválido"
            )
        except Exception as e:
            logger.error(f"Error validating permissions: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return user_pb2.ValidarPermisosResponse(
                exitoso=False,
                mensaje="Error interno del servidor"
            )
    
    def _generar_token_jwt(self, usuario: Usuario) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': usuario.id,
            'username': usuario.nombre_usuario,
            'email': usuario.email,
            'role': usuario.rol,
            'exp': datetime.now(timezone.utc) + timedelta(hours=self.jwt_expiration_hours),
            'iat': datetime.now(timezone.utc)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def _usuario_to_pb(self, usuario: Usuario) -> user_pb2.Usuario:
        """Convert Usuario model to protobuf message"""
        return user_pb2.Usuario(
            id=usuario.id or 0,
            nombreUsuario=usuario.nombre_usuario,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            telefono=usuario.telefono,
            email=usuario.email,
            rol=usuario.rol,
            activo=usuario.activo,
            fechaHoraAlta=usuario.fecha_hora_alta.isoformat() if usuario.fecha_hora_alta else "",
            usuarioAlta=usuario.usuario_alta,
            fechaHoraModificacion=usuario.fecha_hora_modificacion.isoformat() if usuario.fecha_hora_modificacion else "",
            usuarioModificacion=usuario.usuario_modificacion
        )