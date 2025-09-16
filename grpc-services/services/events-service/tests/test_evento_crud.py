"""
Tests for Event CRUD operations
"""
import pytest
from datetime import datetime, timezone, timedelta
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

from models.evento import Evento, DonacionRepartida
from repositories.evento_repository import EventoRepository

class TestEventoCRUD:
    """Test cases for Event CRUD operations"""
    
    @pytest.fixture
    def mock_db_config(self):
        """Mock database configuration"""
        with patch('repositories.evento_repository.db_config') as mock_config:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_config.get_connection.return_value = mock_connection
            mock_connection.cursor.return_value = mock_cursor
            yield mock_config, mock_connection, mock_cursor
    
    @pytest.fixture
    def evento_repository(self, mock_db_config):
        """Create EventoRepository with mocked database"""
        return EventoRepository()
    
    @pytest.fixture
    def evento_valido(self):
        """Create a valid event for testing"""
        fecha_futura = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        return Evento(
            nombre="Evento de Prueba",
            descripcion="Descripción del evento de prueba",
            fecha_hora=fecha_futura,
            usuario_alta="admin_test"
        )
    
    def test_crear_evento_exitoso(self, evento_repository, mock_db_config, evento_valido):
        """Test successful event creation"""
        mock_config, mock_connection, mock_cursor = mock_db_config
        
        # Mock successful insertion
        mock_cursor.lastrowid = 1
        
        # Mock the obtener_evento_por_id call
        with patch.object(evento_repository, 'obtener_evento_por_id') as mock_obtener:
            evento_creado = Evento(
                id=1,
                nombre=evento_valido.nombre,
                descripcion=evento_valido.descripcion,
                fecha_hora=evento_valido.fecha_hora,
                usuario_alta=evento_valido.usuario_alta,
                fecha_hora_alta=datetime.now(timezone.utc).isoformat()
            )
            mock_obtener.return_value = evento_creado
            
            resultado = evento_repository.crear_evento(evento_valido)
            
            assert resultado is not None
            assert resultado.id == 1
            assert resultado.nombre == evento_valido.nombre
            mock_cursor.execute.assert_called_once()
            mock_connection.commit.assert_called_once()
    
    def test_crear_evento_error_db(self, evento_repository, mock_db_config, evento_valido):
        """Test event creation with database error"""
        mock_config, mock_connection, mock_cursor = mock_db_config
        
        # Mock database error
        mock_cursor.execute.side_effect = Exception("Database error")
        
        resultado = evento_repository.crear_evento(evento_valido)
        
        assert resultado is None
        mock_connection.rollback.assert_called_once()
    
    def test_obtener_evento_por_id_existente(self, evento_repository, mock_db_config):
        """Test getting existing event by ID"""
        mock_config, mock_connection, mock_cursor = mock_db_config
        
        # Mock event data
        fecha_evento = datetime.now(timezone.utc) + timedelta(days=1)
        fecha_alta = datetime.now(timezone.utc)
        
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'nombre': 'Evento Test',
            'descripcion': 'Descripción test',
            'fecha_hora': fecha_evento,
            'fecha_hora_alta': fecha_alta,
            'usuario_alta': 'admin',
            'fecha_hora_modificacion': None,
            'usuario_modificacion': None
        }
        
        # Mock participants and donations
        with patch.object(evento_repository, '_obtener_participantes_ids', return_value=[1, 2]):
            with patch.object(evento_repository, '_obtener_donaciones_repartidas', return_value=[]):
                resultado = evento_repository.obtener_evento_por_id(1)
                
                assert resultado is not None
                assert resultado.id == 1
                assert resultado.nombre == 'Evento Test'
                assert resultado.participantes_ids == [1, 2]
                mock_cursor.execute.assert_called_once()
    
    def test_obtener_evento_por_id_no_existe(self, evento_repository, mock_db_config):
        """Test getting non-existing event by ID"""
        mock_config, mock_connection, mock_cursor = mock_db_config
        
        # Mock no event found
        mock_cursor.fetchone.return_value = None
        
        resultado = evento_repository.obtener_evento_por_id(999)
        
        assert resultado is None
        mock_cursor.execute.assert_called_once()
    
    def test_listar_eventos_sin_filtros(self, evento_repository, mock_db_config):
        """Test listing events without filters"""
        mock_config, mock_connection, mock_cursor = mock_db_config
        
        # Mock count query
        mock_cursor.fetchone.return_value = {'total': 2}
        
        # Mock events data
        fecha_evento1 = datetime.now(timezone.utc) + timedelta(days=1)
        fecha_evento2 = datetime.now(timezone.utc) + timedelta(days=2)
        
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'nombre': 'Evento 1',
                'descripcion': 'Descripción 1',
                'fecha_hora': fecha_evento1,
                'fecha_hora_alta': datetime.now(timezone.utc),
                'usuario_alta': 'admin',
                'fecha_hora_modificacion': None,
                'usuario_modificacion': None
            },
            {
                'id': 2,
                'nombre': 'Evento 2',
                'descripcion': 'Descripción 2',
                'fecha_hora': fecha_evento2,
                'fecha_hora_alta': datetime.now(timezone.utc),
                'usuario_alta': 'admin',
                'fecha_hora_modificacion': None,
                'usuario_modificacion': None
            }
        ]
        
        # Mock participants and donations
        with patch.object(evento_repository, '_obtener_participantes_ids', return_value=[]):
            with patch.object(evento_repository, '_obtener_donaciones_repartidas', return_value=[]):
                eventos, total = evento_repository.listar_eventos()
                
                assert len(eventos) == 2
                assert total == 2
                assert eventos[0].nombre == 'Evento 1'
                assert eventos[1].nombre == 'Evento 2'
    
    def test_listar_eventos_solo_futuros(self, evento_repository, mock_db_config):
        """Test listing only future events"""
        mock_config, mock_connection, mock_cursor = mock_db_config
        
        # Mock count and data queries
        mock_cursor.fetchone.return_value = {'total': 1}
        mock_cursor.fetchall.return_value = []
        
        with patch.object(evento_repository, '_obtener_participantes_ids', return_value=[]):
            with patch.object(evento_repository, '_obtener_donaciones_repartidas', return_value=[]):
                eventos, total = evento_repository.listar_eventos(solo_futuros=True)
                
                # Verify the WHERE clause was added for future events
                calls = mock_cursor.execute.call_args_list
                assert any("fecha_hora > NOW()" in str(call) for call in calls)
    
    def test_actualizar_evento_exitoso(self, evento_repository, mock_db_config, evento_valido):
        """Test successful event update"""
        mock_config, mock_connection, mock_cursor = mock_db_config
        
        # Set event ID for update
        evento_valido.id = 1
        evento_valido.usuario_modificacion = "admin_modificador"
        
        # Mock successful update
        mock_cursor.rowcount = 1
        
        # Mock the obtener_evento_por_id call
        with patch.object(evento_repository, 'obtener_evento_por_id') as mock_obtener:
            evento_actualizado = Evento(
                id=1,
                nombre=evento_valido.nombre,
                descripcion=evento_valido.descripcion,
                fecha_hora=evento_valido.fecha_hora,
                usuario_modificacion=evento_valido.usuario_modificacion,
                fecha_hora_modificacion=datetime.now(timezone.utc).isoformat()
            )
            mock_obtener.return_value = evento_actualizado
            
            resultado = evento_repository.actualizar_evento(evento_valido)
            
            assert resultado is not None
            assert resultado.id == 1
            assert resultado.usuario_modificacion == "admin_modificador"
            mock_cursor.execute.assert_called_once()
            mock_connection.commit.assert_called_once()
    
    def test_actualizar_evento_no_existe(self, evento_repository, mock_db_config, evento_valido):
        """Test updating non-existing event"""
        mock_config, mock_connection, mock_cursor = mock_db_config
        
        # Set event ID for update
        evento_valido.id = 999
        
        # Mock no rows affected
        mock_cursor.rowcount = 0
        
        resultado = evento_repository.actualizar_evento(evento_valido)
        
        assert resultado is None
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
    
    def test_eliminar_evento_exitoso(self, evento_repository, mock_db_config):
        """Test successful event deletion"""
        mock_config, mock_connection, mock_cursor = mock_db_config
        
        # Mock successful deletion
        mock_cursor.rowcount = 1
        
        resultado = evento_repository.eliminar_evento(1)
        
        assert resultado == True
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
    
    def test_eliminar_evento_no_existe(self, evento_repository, mock_db_config):
        """Test deleting non-existing event"""
        mock_config, mock_connection, mock_cursor = mock_db_config
        
        # Mock no rows affected
        mock_cursor.rowcount = 0
        
        resultado = evento_repository.eliminar_evento(999)
        
        assert resultado == False
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
    
    def test_eliminar_evento_error_db(self, evento_repository, mock_db_config):
        """Test event deletion with database error"""
        mock_config, mock_connection, mock_cursor = mock_db_config
        
        # Mock database error
        mock_cursor.execute.side_effect = Exception("Database error")
        
        resultado = evento_repository.eliminar_evento(1)
        
        assert resultado == False
        mock_connection.rollback.assert_called_once()
    
    def test_agregar_participante_exitoso(self, evento_repository, mock_db_config):
        """Test successful participant addition"""
        mock_config, mock_connection, mock_cursor = mock_db_config
        
        # Mock successful insertion
        mock_cursor.rowcount = 1
        
        resultado = evento_repository.agregar_participante(1, 2)
        
        assert resultado == True
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
    
    def test_agregar_participante_duplicado(self, evento_repository, mock_db_config):
        """Test adding duplicate participant"""
        mock_config, mock_connection, mock_cursor = mock_db_config
        
        # Mock database error (duplicate key)
        mock_cursor.execute.side_effect = Exception("Duplicate entry")
        
        resultado = evento_repository.agregar_participante(1, 2)
        
        assert resultado == False
        mock_connection.rollback.assert_called_once()
    
    def test_quitar_participante_exitoso(self, evento_repository, mock_db_config):
        """Test successful participant removal"""
        mock_config, mock_connection, mock_cursor = mock_db_config
        
        # Mock successful deletion
        mock_cursor.rowcount = 1
        
        resultado = evento_repository.quitar_participante(1, 2)
        
        assert resultado == True
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
    
    def test_quitar_participante_no_existe(self, evento_repository, mock_db_config):
        """Test removing non-existing participant"""
        mock_config, mock_connection, mock_cursor = mock_db_config
        
        # Mock no rows affected
        mock_cursor.rowcount = 0
        
        resultado = evento_repository.quitar_participante(1, 999)
        
        assert resultado == False
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
    
    def test_obtener_participante_info_existente(self, evento_repository, mock_db_config):
        """Test getting existing participant info"""
        mock_config, mock_connection, mock_cursor = mock_db_config
        
        # Mock participant data
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'nombre_usuario': 'admin',
            'nombre': 'Administrador',
            'apellido': 'Sistema',
            'rol': 'PRESIDENTE'
        }
        
        resultado = evento_repository.obtener_participante_info(1)
        
        assert resultado is not None
        assert resultado.usuario_id == 1
        assert resultado.nombre_usuario == 'admin'
        assert resultado.rol == 'PRESIDENTE'
        mock_cursor.execute.assert_called_once()
    
    def test_obtener_participante_info_no_existe(self, evento_repository, mock_db_config):
        """Test getting non-existing participant info"""
        mock_config, mock_connection, mock_cursor = mock_db_config
        
        # Mock no participant found
        mock_cursor.fetchone.return_value = None
        
        resultado = evento_repository.obtener_participante_info(999)
        
        assert resultado is None
        mock_cursor.execute.assert_called_once()
    
    def test_registrar_donaciones_repartidas_exitoso(self, evento_repository, mock_db_config):
        """Test successful distributed donations registration"""
        mock_config, mock_connection, mock_cursor = mock_db_config
        
        # Create test donations
        donaciones = [
            DonacionRepartida(donacion_id=1, cantidad_repartida=5, usuario_registro="admin"),
            DonacionRepartida(donacion_id=2, cantidad_repartida=3, usuario_registro="admin")
        ]
        
        resultado = evento_repository.registrar_donaciones_repartidas(1, donaciones)
        
        assert len(resultado) == 2
        assert resultado[0].donacion_id == 1
        assert resultado[1].donacion_id == 2
        assert mock_cursor.execute.call_count == 2
        mock_connection.commit.assert_called_once()
    
    def test_registrar_donaciones_repartidas_error_db(self, evento_repository, mock_db_config):
        """Test distributed donations registration with database error"""
        mock_config, mock_connection, mock_cursor = mock_db_config
        
        # Mock database error
        mock_cursor.execute.side_effect = Exception("Database error")
        
        donaciones = [
            DonacionRepartida(donacion_id=1, cantidad_repartida=5, usuario_registro="admin")
        ]
        
        resultado = evento_repository.registrar_donaciones_repartidas(1, donaciones)
        
        assert len(resultado) == 0
        mock_connection.rollback.assert_called_once()