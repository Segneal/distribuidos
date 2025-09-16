"""
Donacion model for inventory management
"""
from datetime import datetime
from enum import Enum
from typing import Optional

class CategoriaEnum(Enum):
    """Enum for donation categories"""
    ROPA = "ROPA"
    ALIMENTOS = "ALIMENTOS"
    JUGUETES = "JUGUETES"
    UTILES_ESCOLARES = "UTILES_ESCOLARES"

class Donacion:
    """Donacion model class"""
    
    def __init__(self, id: Optional[int] = None, categoria: str = None, 
                 descripcion: str = None, cantidad: int = 0, eliminado: bool = False,
                 fecha_hora_alta: Optional[datetime] = None, usuario_alta: str = None,
                 fecha_hora_modificacion: Optional[datetime] = None, 
                 usuario_modificacion: str = None):
        self.id = id
        self.categoria = categoria
        self.descripcion = descripcion
        self.cantidad = cantidad
        self.eliminado = eliminado
        self.fecha_hora_alta = fecha_hora_alta
        self.usuario_alta = usuario_alta
        self.fecha_hora_modificacion = fecha_hora_modificacion
        self.usuario_modificacion = usuario_modificacion
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'categoria': self.categoria,
            'descripcion': self.descripcion,
            'cantidad': self.cantidad,
            'eliminado': self.eliminado,
            'fecha_hora_alta': self.fecha_hora_alta.isoformat() if self.fecha_hora_alta else None,
            'usuario_alta': self.usuario_alta,
            'fecha_hora_modificacion': self.fecha_hora_modificacion.isoformat() if self.fecha_hora_modificacion else None,
            'usuario_modificacion': self.usuario_modificacion
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create instance from dictionary"""
        return cls(
            id=data.get('id'),
            categoria=data.get('categoria'),
            descripcion=data.get('descripcion'),
            cantidad=data.get('cantidad', 0),
            eliminado=data.get('eliminado', False),
            fecha_hora_alta=datetime.fromisoformat(data['fecha_hora_alta']) if data.get('fecha_hora_alta') else None,
            usuario_alta=data.get('usuario_alta'),
            fecha_hora_modificacion=datetime.fromisoformat(data['fecha_hora_modificacion']) if data.get('fecha_hora_modificacion') else None,
            usuario_modificacion=data.get('usuario_modificacion')
        )
    
    def validate(self):
        """Validate donation data"""
        errors = []
        
        # Validate categoria
        if not self.categoria:
            errors.append("Categoría es requerida")
        elif self.categoria not in [cat.value for cat in CategoriaEnum]:
            errors.append(f"Categoría inválida. Debe ser una de: {', '.join([cat.value for cat in CategoriaEnum])}")
        
        # Validate descripcion
        if not self.descripcion or not self.descripcion.strip():
            errors.append("Descripción es requerida")
        elif len(self.descripcion.strip()) < 3:
            errors.append("Descripción debe tener al menos 3 caracteres")
        
        # Validate cantidad
        if self.cantidad is None:
            errors.append("Cantidad es requerida")
        elif self.cantidad < 0:
            errors.append("Cantidad no puede ser negativa")
        
        return errors
    
    def is_valid(self):
        """Check if donation is valid"""
        return len(self.validate()) == 0
    
    def __str__(self):
        return f"Donacion(id={self.id}, categoria={self.categoria}, descripcion={self.descripcion}, cantidad={self.cantidad})"
    
    def __repr__(self):
        return self.__str__()