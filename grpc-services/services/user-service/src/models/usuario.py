"""
User data model and validation for User Service
"""
import re
import bcrypt
import secrets
import string
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class RolUsuario(Enum):
    """User roles enumeration"""
    PRESIDENTE = "PRESIDENTE"
    VOCAL = "VOCAL"
    COORDINADOR = "COORDINADOR"
    VOLUNTARIO = "VOLUNTARIO"

class Usuario:
    """User data model with validation and business logic"""
    
    def __init__(self, id: Optional[int] = None, nombre_usuario: str = "", 
                 nombre: str = "", apellido: str = "", telefono: str = "",
                 email: str = "", rol: str = "", activo: bool = True,
                 fecha_hora_alta: Optional[datetime] = None,
                 usuario_alta: str = "", fecha_hora_modificacion: Optional[datetime] = None,
                 usuario_modificacion: str = "", clave_hash: str = ""):
        self.id = id
        self.nombre_usuario = nombre_usuario
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono
        self.email = email
        self.rol = rol
        self.activo = activo
        self.fecha_hora_alta = fecha_hora_alta
        self.usuario_alta = usuario_alta
        self.fecha_hora_modificacion = fecha_hora_modificacion
        self.usuario_modificacion = usuario_modificacion
        self.clave_hash = clave_hash
    
    @staticmethod
    def validar_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validar_nombre_usuario(nombre_usuario: str) -> bool:
        """Validate username format (alphanumeric, underscore, 3-50 chars)"""
        if not nombre_usuario or len(nombre_usuario) < 3 or len(nombre_usuario) > 50:
            return False
        pattern = r'^[a-zA-Z0-9_]+$'
        return re.match(pattern, nombre_usuario) is not None
    
    @staticmethod
    def validar_rol(rol: str) -> bool:
        """Validate user role"""
        try:
            RolUsuario(rol)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validar_telefono(telefono: str) -> bool:
        """Validate phone number format (optional field)"""
        if not telefono:  # Phone is optional
            return True
        # Allow numbers, spaces, hyphens, parentheses, plus sign
        pattern = r'^[\d\s\-\(\)\+]+$'
        return re.match(pattern, telefono) is not None and len(telefono) <= 20
    
    @staticmethod
    def generar_contraseña_aleatoria(longitud: int = 12) -> str:
        """Generate random password"""
        caracteres = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(caracteres) for _ in range(longitud))
    
    @staticmethod
    def encriptar_contraseña(contraseña: str) -> str:
        """Encrypt password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(contraseña.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verificar_contraseña(contraseña: str, hash_almacenado: str) -> bool:
        """Verify password against stored hash"""
        try:
            return bcrypt.checkpw(contraseña.encode('utf-8'), hash_almacenado.encode('utf-8'))
        except Exception:
            return False
    
    def validar_datos_creacion(self) -> Dict[str, Any]:
        """Validate data for user creation"""
        errores = []
        
        # Validate required fields
        if not self.nombre_usuario:
            errores.append("Nombre de usuario es requerido")
        elif not self.validar_nombre_usuario(self.nombre_usuario):
            errores.append("Nombre de usuario debe tener 3-50 caracteres alfanuméricos")
        
        if not self.nombre:
            errores.append("Nombre es requerido")
        elif len(self.nombre) > 100:
            errores.append("Nombre no puede exceder 100 caracteres")
        
        if not self.apellido:
            errores.append("Apellido es requerido")
        elif len(self.apellido) > 100:
            errores.append("Apellido no puede exceder 100 caracteres")
        
        if not self.email:
            errores.append("Email es requerido")
        elif not self.validar_email(self.email):
            errores.append("Formato de email inválido")
        
        if not self.rol:
            errores.append("Rol es requerido")
        elif not self.validar_rol(self.rol):
            errores.append("Rol inválido. Debe ser: PRESIDENTE, VOCAL, COORDINADOR, VOLUNTARIO")
        
        if not self.validar_telefono(self.telefono):
            errores.append("Formato de teléfono inválido")
        
        return {
            'valido': len(errores) == 0,
            'errores': errores
        }
    
    def validar_datos_actualizacion(self) -> Dict[str, Any]:
        """Validate data for user update"""
        errores = []
        
        # ID is required for updates
        if not self.id:
            errores.append("ID de usuario es requerido para actualización")
        
        # Validate fields if provided
        if self.nombre_usuario and not self.validar_nombre_usuario(self.nombre_usuario):
            errores.append("Nombre de usuario debe tener 3-50 caracteres alfanuméricos")
        
        if self.nombre and len(self.nombre) > 100:
            errores.append("Nombre no puede exceder 100 caracteres")
        
        if self.apellido and len(self.apellido) > 100:
            errores.append("Apellido no puede exceder 100 caracteres")
        
        if self.email and not self.validar_email(self.email):
            errores.append("Formato de email inválido")
        
        if self.rol and not self.validar_rol(self.rol):
            errores.append("Rol inválido. Debe ser: PRESIDENTE, VOCAL, COORDINADOR, VOLUNTARIO")
        
        if not self.validar_telefono(self.telefono):
            errores.append("Formato de teléfono inválido")
        
        return {
            'valido': len(errores) == 0,
            'errores': errores
        }
    
    def to_dict(self, incluir_clave_hash: bool = False) -> Dict[str, Any]:
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'nombre_usuario': self.nombre_usuario,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'telefono': self.telefono,
            'email': self.email,
            'rol': self.rol,
            'activo': self.activo,
            'fecha_hora_alta': self.fecha_hora_alta.isoformat() if self.fecha_hora_alta else None,
            'usuario_alta': self.usuario_alta,
            'fecha_hora_modificacion': self.fecha_hora_modificacion.isoformat() if self.fecha_hora_modificacion else None,
            'usuario_modificacion': self.usuario_modificacion
        }
        
        if incluir_clave_hash:
            data['clave_hash'] = self.clave_hash
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Usuario':
        """Create user from dictionary"""
        return cls(
            id=data.get('id'),
            nombre_usuario=data.get('nombre_usuario', ''),
            nombre=data.get('nombre', ''),
            apellido=data.get('apellido', ''),
            telefono=data.get('telefono', ''),
            email=data.get('email', ''),
            rol=data.get('rol', ''),
            activo=data.get('activo', True),
            fecha_hora_alta=datetime.fromisoformat(data['fecha_hora_alta']) if data.get('fecha_hora_alta') else None,
            usuario_alta=data.get('usuario_alta', ''),
            fecha_hora_modificacion=datetime.fromisoformat(data['fecha_hora_modificacion']) if data.get('fecha_hora_modificacion') else None,
            usuario_modificacion=data.get('usuario_modificacion', ''),
            clave_hash=data.get('clave_hash', '')
        )
    
    def __str__(self) -> str:
        return f"Usuario(id={self.id}, nombre_usuario='{self.nombre_usuario}', email='{self.email}', rol='{self.rol}')"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def tiene_permiso_para_usuarios(self) -> bool:
        """Check if user has permission to manage users (only PRESIDENTE)"""
        return self.rol == RolUsuario.PRESIDENTE.value
    
    def tiene_permiso_para_inventario(self) -> bool:
        """Check if user has permission to manage inventory (PRESIDENTE, VOCAL)"""
        return self.rol in [RolUsuario.PRESIDENTE.value, RolUsuario.VOCAL.value]
    
    def tiene_permiso_para_eventos(self) -> bool:
        """Check if user has permission to manage events (PRESIDENTE, COORDINADOR)"""
        return self.rol in [RolUsuario.PRESIDENTE.value, RolUsuario.COORDINADOR.value]
    
    def puede_participar_en_eventos(self) -> bool:
        """Check if user can participate in events (all roles)"""
        return True  # All active users can participate in events
    
    def es_voluntario(self) -> bool:
        """Check if user is a volunteer"""
        return self.rol == RolUsuario.VOLUNTARIO.value
    
    def puede_auto_asignarse_eventos(self) -> bool:
        """Check if user can self-assign to events (only VOLUNTARIO)"""
        return self.rol == RolUsuario.VOLUNTARIO.value
    
    def puede_gestionar_participantes(self) -> bool:
        """Check if user can manage event participants (PRESIDENTE, COORDINADOR)"""
        return self.rol in [RolUsuario.PRESIDENTE.value, RolUsuario.COORDINADOR.value]
    
    @staticmethod
    def validar_permisos_operacion(rol_usuario: str, operacion: str) -> bool:
        """Validate if user role has permission for specific operation"""
        permisos = {
            'usuarios': [RolUsuario.PRESIDENTE.value],
            'inventario': [RolUsuario.PRESIDENTE.value, RolUsuario.VOCAL.value],
            'eventos': [RolUsuario.PRESIDENTE.value, RolUsuario.COORDINADOR.value],
            'participar_eventos': [RolUsuario.PRESIDENTE.value, RolUsuario.VOCAL.value, 
                                 RolUsuario.COORDINADOR.value, RolUsuario.VOLUNTARIO.value],
            'auto_asignar_eventos': [RolUsuario.VOLUNTARIO.value],
            'gestionar_participantes': [RolUsuario.PRESIDENTE.value, RolUsuario.COORDINADOR.value]
        }
        
        return rol_usuario in permisos.get(operacion, [])