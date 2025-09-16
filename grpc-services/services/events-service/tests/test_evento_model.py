"""
Tests for Evento model
"""
import pytest
from datetime import datetime, timezone, timedelta
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.evento import Evento, DonacionRepartida, Participante

class TestEvento:
    """Test cases for Evento model"""
    
    def test_crear_evento_valido(self):
        """Test creating a valid event"""
        fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        evento = Evento(
            nombre="Evento de prueba",
            descripcion="Descripción del evento",
            fecha_hora=fecha_futura,
            usuario_alta="admin"
        )
        
        assert evento.nombre == "Evento de prueba"
        assert evento.descripcion == "Descripción del evento"
        assert evento.fecha_hora == fecha_futura
        assert evento.usuario_alta == "admin"
        assert evento.participantes_ids == []
        assert evento.donaciones_repartidas == []
    
    def test_validar_datos_basicos_evento_valido(self):
        """Test validation of valid event data"""
        fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        evento = Evento(
            nombre="Evento válido",
            descripcion="Descripción válida",
            fecha_hora=fecha_futura
        )
        
        errores = evento.validar_datos_basicos()
        assert len(errores) == 0
    
    def test_validar_nombre_obligatorio(self):
        """Test validation of required name"""
        fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        evento = Evento(
            nombre="",
            descripcion="Descripción",
            fecha_hora=fecha_futura
        )
        
        errores = evento.validar_datos_basicos()
        assert any("nombre del evento es obligatorio" in error for error in errores)
    
    def test_validar_nombre_minimo(self):
        """Test validation of minimum name length"""
        fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        evento = Evento(
            nombre="AB",
            descripcion="Descripción",
            fecha_hora=fecha_futura
        )
        
        errores = evento.validar_datos_basicos()
        assert any("al menos 3 caracteres" in error for error in errores)
    
    def test_validar_nombre_maximo(self):
        """Test validation of maximum name length"""
        fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        evento = Evento(
            nombre="A" * 256,  # 256 characters
            descripcion="Descripción",
            fecha_hora=fecha_futura
        )
        
        errores = evento.validar_datos_basicos()
        assert any("no puede exceder 255 caracteres" in error for error in errores)
    
    def test_validar_fecha_obligatoria(self):
        """Test validation of required date"""
        evento = Evento(
            nombre="Evento",
            descripcion="Descripción",
            fecha_hora=""
        )
        
        errores = evento.validar_datos_basicos()
        assert any("fecha y hora del evento es obligatoria" in error for error in errores)
    
    def test_validar_fecha_futura(self):
        """Test validation of future date"""
        fecha_pasada = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        
        evento = Evento(
            nombre="Evento",
            descripcion="Descripción",
            fecha_hora=fecha_pasada
        )
        
        errores = evento.validar_datos_basicos()
        assert any("fecha del evento debe ser futura" in error for error in errores)
    
    def test_validar_formato_fecha_invalido(self):
        """Test validation of invalid date format"""
        evento = Evento(
            nombre="Evento",
            descripcion="Descripción",
            fecha_hora="fecha-invalida"
        )
        
        errores = evento.validar_datos_basicos()
        assert any("Formato de fecha inválido" in error for error in errores)
    
    def test_es_evento_futuro(self):
        """Test checking if event is in the future"""
        fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        evento = Evento(
            nombre="Evento futuro",
            fecha_hora=fecha_futura
        )
        
        assert evento.es_evento_futuro() == True
        assert evento.es_evento_pasado() == False
    
    def test_es_evento_pasado(self):
        """Test checking if event is in the past"""
        fecha_pasada = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        
        evento = Evento(
            nombre="Evento pasado",
            fecha_hora=fecha_pasada
        )
        
        assert evento.es_evento_futuro() == False
        assert evento.es_evento_pasado() == True
    
    def test_puede_modificar_datos_basicos(self):
        """Test if basic data can be modified (future events only)"""
        fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        fecha_pasada = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        
        evento_futuro = Evento(nombre="Evento futuro", fecha_hora=fecha_futura)
        evento_pasado = Evento(nombre="Evento pasado", fecha_hora=fecha_pasada)
        
        assert evento_futuro.puede_modificar_datos_basicos() == True
        assert evento_pasado.puede_modificar_datos_basicos() == False
    
    def test_puede_registrar_donaciones(self):
        """Test if donations can be registered (past events only)"""
        fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        fecha_pasada = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        
        evento_futuro = Evento(nombre="Evento futuro", fecha_hora=fecha_futura)
        evento_pasado = Evento(nombre="Evento pasado", fecha_hora=fecha_pasada)
        
        assert evento_futuro.puede_registrar_donaciones() == False
        assert evento_pasado.puede_registrar_donaciones() == True
    
    def test_puede_eliminar(self):
        """Test if event can be deleted (future events only)"""
        fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        fecha_pasada = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        
        evento_futuro = Evento(nombre="Evento futuro", fecha_hora=fecha_futura)
        evento_pasado = Evento(nombre="Evento pasado", fecha_hora=fecha_pasada)
        
        assert evento_futuro.puede_eliminar() == True
        assert evento_pasado.puede_eliminar() == False
    
    def test_agregar_participante(self):
        """Test adding participant to event"""
        evento = Evento(nombre="Evento", participantes_ids=[1, 2])
        
        # Add new participant
        resultado = evento.agregar_participante(3)
        assert resultado == True
        assert 3 in evento.participantes_ids
        
        # Try to add existing participant
        resultado = evento.agregar_participante(1)
        assert resultado == False
        assert evento.participantes_ids.count(1) == 1
    
    def test_quitar_participante(self):
        """Test removing participant from event"""
        evento = Evento(nombre="Evento", participantes_ids=[1, 2, 3])
        
        # Remove existing participant
        resultado = evento.quitar_participante(2)
        assert resultado == True
        assert 2 not in evento.participantes_ids
        
        # Try to remove non-existing participant
        resultado = evento.quitar_participante(5)
        assert resultado == False
    
    def test_to_dict(self):
        """Test converting event to dictionary"""
        fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        evento = Evento(
            id=1,
            nombre="Evento",
            descripcion="Descripción",
            fecha_hora=fecha_futura,
            participantes_ids=[1, 2],
            usuario_alta="admin"
        )
        
        evento_dict = evento.to_dict()
        
        assert evento_dict['id'] == 1
        assert evento_dict['nombre'] == "Evento"
        assert evento_dict['descripcion'] == "Descripción"
        assert evento_dict['fecha_hora'] == fecha_futura
        assert evento_dict['participantes_ids'] == [1, 2]
        assert evento_dict['usuario_alta'] == "admin"
    
    def test_from_dict(self):
        """Test creating event from dictionary"""
        fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        evento_dict = {
            'id': 1,
            'nombre': "Evento",
            'descripcion': "Descripción",
            'fecha_hora': fecha_futura,
            'participantes_ids': [1, 2],
            'usuario_alta': "admin"
        }
        
        evento = Evento.from_dict(evento_dict)
        
        assert evento.id == 1
        assert evento.nombre == "Evento"
        assert evento.descripcion == "Descripción"
        assert evento.fecha_hora == fecha_futura
        assert evento.participantes_ids == [1, 2]
        assert evento.usuario_alta == "admin"

class TestDonacionRepartida:
    """Test cases for DonacionRepartida model"""
    
    def test_crear_donacion_repartida(self):
        """Test creating distributed donation"""
        donacion = DonacionRepartida(
            donacion_id=1,
            cantidad_repartida=5,
            usuario_registro="admin"
        )
        
        assert donacion.donacion_id == 1
        assert donacion.cantidad_repartida == 5
        assert donacion.usuario_registro == "admin"
        assert donacion.fecha_hora_registro is not None
    
    def test_to_dict(self):
        """Test converting to dictionary"""
        donacion = DonacionRepartida(
            donacion_id=1,
            cantidad_repartida=5,
            usuario_registro="admin"
        )
        
        donacion_dict = donacion.to_dict()
        
        assert donacion_dict['donacion_id'] == 1
        assert donacion_dict['cantidad_repartida'] == 5
        assert donacion_dict['usuario_registro'] == "admin"
        assert 'fecha_hora_registro' in donacion_dict
    
    def test_from_dict(self):
        """Test creating from dictionary"""
        donacion_dict = {
            'donacion_id': 1,
            'cantidad_repartida': 5,
            'usuario_registro': "admin",
            'fecha_hora_registro': "2024-01-01T10:00:00Z"
        }
        
        donacion = DonacionRepartida.from_dict(donacion_dict)
        
        assert donacion.donacion_id == 1
        assert donacion.cantidad_repartida == 5
        assert donacion.usuario_registro == "admin"
        assert donacion.fecha_hora_registro == "2024-01-01T10:00:00Z"

class TestParticipante:
    """Test cases for Participante model"""
    
    def test_crear_participante(self):
        """Test creating participant"""
        participante = Participante(
            usuario_id=1,
            nombre_usuario="admin",
            nombre="Admin",
            apellido="User",
            rol="PRESIDENTE"
        )
        
        assert participante.usuario_id == 1
        assert participante.nombre_usuario == "admin"
        assert participante.nombre == "Admin"
        assert participante.apellido == "User"
        assert participante.rol == "PRESIDENTE"
        assert participante.fecha_asignacion is not None
    
    def test_to_dict(self):
        """Test converting to dictionary"""
        participante = Participante(
            usuario_id=1,
            nombre_usuario="admin",
            nombre="Admin",
            apellido="User",
            rol="PRESIDENTE"
        )
        
        participante_dict = participante.to_dict()
        
        assert participante_dict['usuario_id'] == 1
        assert participante_dict['nombre_usuario'] == "admin"
        assert participante_dict['nombre'] == "Admin"
        assert participante_dict['apellido'] == "User"
        assert participante_dict['rol'] == "PRESIDENTE"
        assert 'fecha_asignacion' in participante_dict
    
    def test_from_dict(self):
        """Test creating from dictionary"""
        participante_dict = {
            'usuario_id': 1,
            'nombre_usuario': "admin",
            'nombre': "Admin",
            'apellido': "User",
            'rol': "PRESIDENTE",
            'fecha_asignacion': "2024-01-01T10:00:00Z"
        }
        
        participante = Participante.from_dict(participante_dict)
        
        assert participante.usuario_id == 1
        assert participante.nombre_usuario == "admin"
        assert participante.nombre == "Admin"
        assert participante.apellido == "User"
        assert participante.rol == "PRESIDENTE"
        assert participante.fecha_asignacion == "2024-01-01T10:00:00Z"