"""
Event model and validation for Events Service
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import re

class DonacionRepartida:
    """Model for distributed donations in events"""
    
    def __init__(self, donacion_id: int, cantidad_repartida: int, 
                 usuario_registro: str, fecha_hora_registro: Optional[str] = None):
        self.donacion_id = donacion_id
        self.cantidad_repartida = cantidad_repartida
        self.usuario_registro = usuario_registro
        self.fecha_hora_registro = fecha_hora_registro or datetime.now(timezone.utc).isoformat()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'donacion_id': self.donacion_id,
            'cantidad_repartida': self.cantidad_repartida,
            'usuario_registro': self.usuario_registro,
            'fecha_hora_registro': self.fecha_hora_registro
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DonacionRepartida':
        """Create from dictionary"""
        return cls(
            donacion_id=data['donacion_id'],
            cantidad_repartida=data['cantidad_repartida'],
            usuario_registro=data['usuario_registro'],
            fecha_hora_registro=data.get('fecha_hora_registro')
        )

class Evento:
    """Event model with validation and business logic"""
    
    def __init__(self, id: Optional[int] = None, nombre: str = "", descripcion: str = "",
                 fecha_hora: str = "", participantes_ids: Optional[List[int]] = None,
                 donaciones_repartidas: Optional[List[DonacionRepartida]] = None,
                 fecha_hora_alta: Optional[str] = None, usuario_alta: Optional[str] = None,
                 fecha_hora_modificacion: Optional[str] = None, usuario_modificacion: Optional[str] = None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_hora = fecha_hora
        self.participantes_ids = participantes_ids or []
        self.donaciones_repartidas = donaciones_repartidas or []
        self.fecha_hora_alta = fecha_hora_alta
        self.usuario_alta = usuario_alta
        self.fecha_hora_modificacion = fecha_hora_modificacion
        self.usuario_modificacion = usuario_modificacion
    
    def validar_datos_basicos(self) -> List[str]:
        """Validate basic event data"""
        errores = []
        
        # Validate name
        if not self.nombre or not self.nombre.strip():
            errores.append("El nombre del evento es obligatorio")
        elif len(self.nombre.strip()) < 3:
            errores.append("El nombre del evento debe tener al menos 3 caracteres")
        elif len(self.nombre.strip()) > 255:
            errores.append("El nombre del evento no puede exceder 255 caracteres")
        
        # Validate description
        if self.descripcion and len(self.descripcion) > 1000:
            errores.append("La descripción no puede exceder 1000 caracteres")
        
        # Validate date format
        if not self.fecha_hora:
            errores.append("La fecha y hora del evento es obligatoria")
        else:
            try:
                fecha_evento = datetime.fromisoformat(self.fecha_hora.replace('Z', '+00:00'))
                # Validate future date
                if fecha_evento <= datetime.now(timezone.utc):
                    errores.append("La fecha del evento debe ser futura")
            except ValueError:
                errores.append("Formato de fecha inválido. Use formato ISO 8601")
        
        return errores
    
    def es_evento_futuro(self) -> bool:
        """Check if event is in the future"""
        try:
            fecha_evento = datetime.fromisoformat(self.fecha_hora.replace('Z', '+00:00'))
            return fecha_evento > datetime.now(timezone.utc)
        except ValueError:
            return False
    
    def es_evento_pasado(self) -> bool:
        """Check if event is in the past"""
        return not self.es_evento_futuro()
    
    def puede_modificar_datos_basicos(self) -> bool:
        """Check if basic data can be modified (only future events)"""
        return self.es_evento_futuro()
    
    def puede_registrar_donaciones(self) -> bool:
        """Check if donations can be registered (only past events)"""
        return self.es_evento_pasado()
    
    def puede_eliminar(self) -> bool:
        """Check if event can be deleted (only future events)"""
        return self.es_evento_futuro()
    
    def agregar_participante(self, usuario_id: int) -> bool:
        """Add participant to event"""
        if usuario_id not in self.participantes_ids:
            self.participantes_ids.append(usuario_id)
            return True
        return False
    
    def quitar_participante(self, usuario_id: int) -> bool:
        """Remove participant from event"""
        if usuario_id in self.participantes_ids:
            self.participantes_ids.remove(usuario_id)
            return True
        return False
    
    def agregar_donacion_repartida(self, donacion_repartida: DonacionRepartida) -> bool:
        """Add distributed donation to event"""
        if self.puede_registrar_donaciones():
            self.donaciones_repartidas.append(donacion_repartida)
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'fecha_hora': self.fecha_hora,
            'participantes_ids': self.participantes_ids,
            'donaciones_repartidas': [dr.to_dict() for dr in self.donaciones_repartidas],
            'fecha_hora_alta': self.fecha_hora_alta,
            'usuario_alta': self.usuario_alta,
            'fecha_hora_modificacion': self.fecha_hora_modificacion,
            'usuario_modificacion': self.usuario_modificacion
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Evento':
        """Create event from dictionary"""
        donaciones_repartidas = []
        if 'donaciones_repartidas' in data and data['donaciones_repartidas']:
            donaciones_repartidas = [
                DonacionRepartida.from_dict(dr) for dr in data['donaciones_repartidas']
            ]
        
        return cls(
            id=data.get('id'),
            nombre=data.get('nombre', ''),
            descripcion=data.get('descripcion', ''),
            fecha_hora=data.get('fecha_hora', ''),
            participantes_ids=data.get('participantes_ids', []),
            donaciones_repartidas=donaciones_repartidas,
            fecha_hora_alta=data.get('fecha_hora_alta'),
            usuario_alta=data.get('usuario_alta'),
            fecha_hora_modificacion=data.get('fecha_hora_modificacion'),
            usuario_modificacion=data.get('usuario_modificacion')
        )
    
    def __str__(self) -> str:
        return f"Evento(id={self.id}, nombre='{self.nombre}', fecha_hora='{self.fecha_hora}')"
    
    def __repr__(self) -> str:
        return self.__str__()

class Participante:
    """Participant model for events"""
    
    def __init__(self, usuario_id: int, nombre_usuario: str, nombre: str, 
                 apellido: str, rol: str, fecha_asignacion: Optional[str] = None):
        self.usuario_id = usuario_id
        self.nombre_usuario = nombre_usuario
        self.nombre = nombre
        self.apellido = apellido
        self.rol = rol
        self.fecha_asignacion = fecha_asignacion or datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'usuario_id': self.usuario_id,
            'nombre_usuario': self.nombre_usuario,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'rol': self.rol,
            'fecha_asignacion': self.fecha_asignacion
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Participante':
        """Create from dictionary"""
        return cls(
            usuario_id=data['usuario_id'],
            nombre_usuario=data['nombre_usuario'],
            nombre=data['nombre'],
            apellido=data['apellido'],
            rol=data['rol'],
            fecha_asignacion=data.get('fecha_asignacion')
        )
    
    def __str__(self) -> str:
        return f"Participante(usuario_id={self.usuario_id}, nombre='{self.nombre} {self.apellido}', rol='{self.rol}')"