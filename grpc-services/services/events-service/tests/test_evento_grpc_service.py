"""
Tests for Event gRPC Service
"""
import pytest
from datetime import datetime, timezone, timedelta
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import grpc

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

from service.evento_service import EventoService
from models.evento import Evento, DonacionRepartida, Participante
from grpc import events_pb2

class TestEventoGRPCService:
    """Test cases for Event gRPC Service"""
    
    @pytest.fixture
    def evento_service(self):
        """Create EventoService instance"""
        return EventoService()
    
    @pytest.fixture
    def mock_context(self):
        """Mock gRPC context"""
        context = Mock()
        return context
    
    @pytest.fixture
    def evento_valido(self):
        """Create a valid event for testing"""
        fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        return Evento(
            id=1,
            nombre="Evento de Prueba",
            descripcion="Descripción del evento de prueba",
            fecha_hora=fecha_futura,
            usuario_alta="admin_test",
            fecha_hora_alta=datetime.now(timezone.utc).isoformat()
        )
    
    def test_crear_evento_exitoso(self, evento_service, mock_context):
        """Test successful event creation via gRPC"""
        fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        request = events_pb2.CrearEventoRequest(
            nombre="Evento gRPC",
            descripcion="Descripción del evento gRPC",
            fechaHora=fecha_futura,
            usuarioCreador="admin_grpc"
        )
        
        # Mock repository
        with patch.object(evento_service.evento_repository, 'crear_evento') as mock_crear:
            evento_creado = Evento(
                id=1,
                nombre=request.nombre,
                descripcion=request.descripcion,
                fecha_hora=request.fechaHora,
                usuario_alta=request.usuarioCreador,
                fecha_hora_alta=datetime.now(timezone.utc).isoformat()
            )
            mock_crear.return_value = evento_creado
            
            response = evento_service.CrearEvento(request, mock_context)
            
            assert response.exitoso == True
            assert "exitosamente" in response.mensaje
            assert response.evento.id == 1
            assert response.evento.nombre == "Evento gRPC"
    
    def test_crear_evento_validacion_error(self, evento_service, mock_context):
        """Test event creation with validation errors"""
        request = events_pb2.CrearEventoRequest(
            nombre="",  # Empty name
            descripcion="Descripción",
            fechaHora="fecha-invalida",  # Invalid date
            usuarioCreador="admin"
        )
        
        response = evento_service.CrearEvento(request, mock_context)
        
        assert response.exitoso == False
        assert "validación" in response.mensaje
    
    def test_crear_evento_error_db(self, evento_service, mock_context):
        """Test event creation with database error"""
        fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        request = events_pb2.CrearEventoRequest(
            nombre="Evento gRPC",
            descripcion="Descripción",
            fechaHora=fecha_futura,
            usuarioCreador="admin"
        )
        
        # Mock repository error
        with patch.object(evento_service.evento_repository, 'crear_evento', return_value=None):
            response = evento_service.CrearEvento(request, mock_context)
            
            assert response.exitoso == False
            assert "Error al crear" in response.mensaje
    
    def test_obtener_evento_exitoso(self, evento_service, mock_context, evento_valido):
        """Test successful event retrieval"""
        request = events_pb2.ObtenerEventoRequest(id=1)
        
        # Mock repository
        with patch.object(evento_service.evento_repository, 'obtener_evento_por_id', return_value=evento_valido):
            response = evento_service.ObtenerEvento(request, mock_context)
            
            assert response.exitoso == True
            assert "exitosamente" in response.mensaje
            assert response.evento.id == 1
            assert response.evento.nombre == evento_valido.nombre
    
    def test_obtener_evento_no_encontrado(self, evento_service, mock_context):
        """Test event retrieval when event not found"""
        request = events_pb2.ObtenerEventoRequest(id=999)
        
        # Mock repository
        with patch.object(evento_service.evento_repository, 'obtener_evento_por_id', return_value=None):
            response = evento_service.ObtenerEvento(request, mock_context)
            
            assert response.exitoso == False
            assert "no encontrado" in response.mensaje
            mock_context.set_code.assert_called_with(grpc.StatusCode.NOT_FOUND)
    
    def test_listar_eventos_exitoso(self, evento_service, mock_context, evento_valido):
        """Test successful events listing"""
        request = events_pb2.ListarEventosRequest(
            pagina=1,
            tamanoPagina=10,
            soloFuturos=False,
            soloPasados=False
        )
        
        eventos = [evento_valido]
        
        # Mock repository
        with patch.object(evento_service.evento_repository, 'listar_eventos', return_value=(eventos, 1)):
            response = evento_service.ListarEventos(request, mock_context)
            
            assert response.exitoso == True
            assert len(response.eventos) == 1
            assert response.totalRegistros == 1
            assert response.eventos[0].nombre == evento_valido.nombre
    
    def test_actualizar_evento_exitoso(self, evento_service, mock_context, evento_valido):
        """Test successful event update"""
        request = events_pb2.ActualizarEventoRequest(
            id=1,
            nombre="Evento Actualizado",
            descripcion="Descripción actualizada",
            fechaHora=evento_valido.fecha_hora,
            usuarioModificacion="admin_modificador"
        )
        
        # Mock repository
        with patch.object(evento_service.evento_repository, 'obtener_evento_por_id', return_value=evento_valido):
            with patch.object(evento_service.evento_repository, 'actualizar_evento') as mock_actualizar:
                evento_actualizado = Evento(
                    id=1,
                    nombre=request.nombre,
                    descripcion=request.descripcion,
                    fecha_hora=request.fechaHora,
                    usuario_modificacion=request.usuarioModificacion
                )
                mock_actualizar.return_value = evento_actualizado
                
                response = evento_service.ActualizarEvento(request, mock_context)
                
                assert response.exitoso == True
                assert "actualizado exitosamente" in response.mensaje
                assert response.evento.nombre == "Evento Actualizado"
    
    def test_actualizar_evento_no_encontrado(self, evento_service, mock_context):
        """Test updating non-existing event"""
        request = events_pb2.ActualizarEventoRequest(
            id=999,
            nombre="Evento",
            descripcion="Descripción",
            fechaHora=(datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            usuarioModificacion="admin"
        )
        
        # Mock repository
        with patch.object(evento_service.evento_repository, 'obtener_evento_por_id', return_value=None):
            response = evento_service.ActualizarEvento(request, mock_context)
            
            assert response.exitoso == False
            assert "no encontrado" in response.mensaje
            mock_context.set_code.assert_called_with(grpc.StatusCode.NOT_FOUND)
    
    def test_actualizar_evento_pasado(self, evento_service, mock_context):
        """Test updating past event (should fail)"""
        fecha_pasada = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        
        evento_pasado = Evento(
            id=1,
            nombre="Evento Pasado",
            fecha_hora=fecha_pasada
        )
        
        request = events_pb2.ActualizarEventoRequest(
            id=1,
            nombre="Evento Actualizado",
            descripcion="Descripción",
            fechaHora=fecha_pasada,
            usuarioModificacion="admin"
        )
        
        # Mock repository
        with patch.object(evento_service.evento_repository, 'obtener_evento_por_id', return_value=evento_pasado):
            response = evento_service.ActualizarEvento(request, mock_context)
            
            assert response.exitoso == False
            assert "eventos futuros" in response.mensaje
            mock_context.set_code.assert_called_with(grpc.StatusCode.FAILED_PRECONDITION)
    
    def test_eliminar_evento_exitoso(self, evento_service, mock_context, evento_valido):
        """Test successful event deletion"""
        request = events_pb2.EliminarEventoRequest(
            id=1,
            usuarioEliminacion="admin"
        )
        
        # Mock repository
        with patch.object(evento_service.evento_repository, 'obtener_evento_por_id', return_value=evento_valido):
            with patch.object(evento_service.evento_repository, 'eliminar_evento', return_value=True):
                response = evento_service.EliminarEvento(request, mock_context)
                
                assert response.exitoso == True
                assert "eliminado exitosamente" in response.mensaje
    
    def test_eliminar_evento_pasado(self, evento_service, mock_context):
        """Test deleting past event (should fail)"""
        fecha_pasada = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        
        evento_pasado = Evento(
            id=1,
            nombre="Evento Pasado",
            fecha_hora=fecha_pasada
        )
        
        request = events_pb2.EliminarEventoRequest(
            id=1,
            usuarioEliminacion="admin"
        )
        
        # Mock repository
        with patch.object(evento_service.evento_repository, 'obtener_evento_por_id', return_value=evento_pasado):
            response = evento_service.EliminarEvento(request, mock_context)
            
            assert response.exitoso == False
            assert "eventos futuros" in response.mensaje
            mock_context.set_code.assert_called_with(grpc.StatusCode.FAILED_PRECONDITION)
    
    def test_agregar_participante_exitoso(self, evento_service, mock_context, evento_valido):
        """Test successful participant addition"""
        request = events_pb2.AgregarParticipanteRequest(
            eventoId=1,
            usuarioId=2,
            usuarioAsignacion="admin"
        )
        
        participante = Participante(
            usuario_id=2,
            nombre_usuario="usuario2",
            nombre="Usuario",
            apellido="Dos",
            rol="VOLUNTARIO"
        )
        
        # Mock repository
        with patch.object(evento_service.evento_repository, 'obtener_evento_por_id', return_value=evento_valido):
            with patch.object(evento_service.evento_repository, 'obtener_participante_info', return_value=participante):
                with patch.object(evento_service.evento_repository, 'agregar_participante', return_value=True):
                    response = evento_service.AgregarParticipante(request, mock_context)
                    
                    assert response.exitoso == True
                    assert "agregado exitosamente" in response.mensaje
                    assert response.participante.usuarioId == 2
    
    def test_agregar_participante_duplicado(self, evento_service, mock_context):
        """Test adding duplicate participant"""
        evento_con_participante = Evento(
            id=1,
            nombre="Evento",
            fecha_hora=(datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            participantes_ids=[2]  # User 2 already participant
        )
        
        request = events_pb2.AgregarParticipanteRequest(
            eventoId=1,
            usuarioId=2,
            usuarioAsignacion="admin"
        )
        
        participante = Participante(
            usuario_id=2,
            nombre_usuario="usuario2",
            nombre="Usuario",
            apellido="Dos",
            rol="VOLUNTARIO"
        )
        
        # Mock repository
        with patch.object(evento_service.evento_repository, 'obtener_evento_por_id', return_value=evento_con_participante):
            with patch.object(evento_service.evento_repository, 'obtener_participante_info', return_value=participante):
                response = evento_service.AgregarParticipante(request, mock_context)
                
                assert response.exitoso == False
                assert "ya es participante" in response.mensaje
    
    def test_quitar_participante_exitoso(self, evento_service, mock_context):
        """Test successful participant removal"""
        evento_con_participante = Evento(
            id=1,
            nombre="Evento",
            fecha_hora=(datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            participantes_ids=[2]  # User 2 is participant
        )
        
        request = events_pb2.QuitarParticipanteRequest(
            eventoId=1,
            usuarioId=2,
            usuarioRemocion="admin"
        )
        
        # Mock repository
        with patch.object(evento_service.evento_repository, 'obtener_evento_por_id', return_value=evento_con_participante):
            with patch.object(evento_service.evento_repository, 'quitar_participante', return_value=True):
                response = evento_service.QuitarParticipante(request, mock_context)
                
                assert response.exitoso == True
                assert "removido exitosamente" in response.mensaje
    
    def test_registrar_donaciones_repartidas_exitoso(self, evento_service, mock_context):
        """Test successful distributed donations registration"""
        fecha_pasada = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        
        evento_pasado = Evento(
            id=1,
            nombre="Evento Pasado",
            fecha_hora=fecha_pasada
        )
        
        request = events_pb2.RegistrarDonacionesRequest(
            eventoId=1,
            donaciones=[
                events_pb2.DonacionRepartidaRequest(
                    donacionId=1,
                    cantidadRepartida=5
                )
            ],
            usuarioRegistro="admin"
        )
        
        donaciones_registradas = [
            DonacionRepartida(
                donacion_id=1,
                cantidad_repartida=5,
                usuario_registro="admin"
            )
        ]
        
        # Mock repository
        with patch.object(evento_service.evento_repository, 'obtener_evento_por_id', return_value=evento_pasado):
            with patch.object(evento_service.evento_repository, 'registrar_donaciones_repartidas', return_value=donaciones_registradas):
                response = evento_service.RegistrarDonacionesRepartidas(request, mock_context)
                
                assert response.exitoso == True
                assert "registraron" in response.mensaje
                assert len(response.donacionesRegistradas) == 1
    
    def test_registrar_donaciones_evento_futuro(self, evento_service, mock_context, evento_valido):
        """Test registering donations for future event (should fail)"""
        request = events_pb2.RegistrarDonacionesRequest(
            eventoId=1,
            donaciones=[
                events_pb2.DonacionRepartidaRequest(
                    donacionId=1,
                    cantidadRepartida=5
                )
            ],
            usuarioRegistro="admin"
        )
        
        # Mock repository
        with patch.object(evento_service.evento_repository, 'obtener_evento_por_id', return_value=evento_valido):
            response = evento_service.RegistrarDonacionesRepartidas(request, mock_context)
            
            assert response.exitoso == False
            assert "eventos pasados" in response.mensaje
            mock_context.set_code.assert_called_with(grpc.StatusCode.FAILED_PRECONDITION)