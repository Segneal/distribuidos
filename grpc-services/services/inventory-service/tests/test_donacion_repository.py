"""
Tests for Donacion Repository (without database connection)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.models.donacion import Donacion
from src.repositories.donacion_repository import DonacionRepository

class TestDonacionRepository:
    """Test cases for Donacion Repository"""
    
    def setup_method(self):
        """Setup test environment"""
        self.repository = DonacionRepository()
    
    @patch('src.repositories.donacion_repository.get_db_config')
    def test_crear_donacion_success(self, mock_get_db_config):
        """Test successful donation creation"""
        # Setup mocks
        mock_db_config = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_get_db_config.return_value = mock_db_config
        mock_db_config.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1
        
        # Create test donation
        donacion = Donacion(
            categoria="ALIMENTOS",
            descripcion="Puré de tomates",
            cantidad=10,
            usuario_alta="admin"
        )
        
        # Execute
        result = self.repository.crear_donacion(donacion)
        
        # Verify
        assert result is not None
        assert result.id == 1
        assert result.categoria == "ALIMENTOS"
        assert result.descripcion == "Puré de tomates"
        assert result.cantidad == 10
        assert result.usuario_alta == "admin"
        assert result.fecha_hora_alta is not None
        
        # Verify database calls
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()
    
    @patch('src.repositories.donacion_repository.get_db_config')
    def test_obtener_donacion_por_id_found(self, mock_get_db_config):
        """Test getting donation by ID when found"""
        # Setup mocks
        mock_db_config = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_get_db_config.return_value = mock_db_config
        mock_db_config.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Mock database result
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'categoria': 'ROPA',
            'descripcion': 'Camisetas',
            'cantidad': 5,
            'eliminado': False,
            'fecha_hora_alta': datetime.now(),
            'usuario_alta': 'admin',
            'fecha_hora_modificacion': None,
            'usuario_modificacion': None
        }
        
        # Execute
        result = self.repository.obtener_donacion_por_id(1)
        
        # Verify
        assert result is not None
        assert result.id == 1
        assert result.categoria == 'ROPA'
        assert result.descripcion == 'Camisetas'
        assert result.cantidad == 5
        assert result.eliminado == False
        
        # Verify database calls
        mock_cursor.execute.assert_called_once_with(
            "SELECT id, categoria, descripcion, cantidad, eliminado,\n                       fecha_hora_alta, usuario_alta, fecha_hora_modificacion, \n                       usuario_modificacion\n                FROM donaciones \n                WHERE id = %s",
            (1,)
        )
    
    @patch('src.repositories.donacion_repository.get_db_config')
    def test_obtener_donacion_por_id_not_found(self, mock_get_db_config):
        """Test getting donation by ID when not found"""
        # Setup mocks
        mock_db_config = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_get_db_config.return_value = mock_db_config
        mock_db_config.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        # Execute
        result = self.repository.obtener_donacion_por_id(999)
        
        # Verify
        assert result is None
    
    @patch('src.repositories.donacion_repository.get_db_config')
    def test_listar_donaciones_with_pagination(self, mock_get_db_config):
        """Test listing donations with pagination"""
        # Setup mocks
        mock_db_config = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_get_db_config.return_value = mock_db_config
        mock_db_config.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Mock count result
        mock_cursor.fetchone.return_value = {'total': 25}
        
        # Mock donations result
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'categoria': 'ALIMENTOS',
                'descripcion': 'Arroz',
                'cantidad': 20,
                'eliminado': False,
                'fecha_hora_alta': datetime.now(),
                'usuario_alta': 'admin',
                'fecha_hora_modificacion': None,
                'usuario_modificacion': None
            },
            {
                'id': 2,
                'categoria': 'ROPA',
                'descripcion': 'Pantalones',
                'cantidad': 15,
                'eliminado': False,
                'fecha_hora_alta': datetime.now(),
                'usuario_alta': 'admin',
                'fecha_hora_modificacion': None,
                'usuario_modificacion': None
            }
        ]
        
        # Execute
        donaciones, total = self.repository.listar_donaciones(
            pagina=1, tamano_pagina=10, categoria=None, incluir_eliminados=False
        )
        
        # Verify
        assert len(donaciones) == 2
        assert total == 25
        assert donaciones[0].categoria == 'ALIMENTOS'
        assert donaciones[1].categoria == 'ROPA'
        
        # Verify database calls (should be called twice: count + select)
        assert mock_cursor.execute.call_count == 2
    
    @patch('src.repositories.donacion_repository.get_db_config')
    def test_actualizar_donacion_success(self, mock_get_db_config):
        """Test successful donation update"""
        # Setup mocks
        mock_db_config = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_get_db_config.return_value = mock_db_config
        mock_db_config.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1  # One row affected
        
        # Create test donation
        donacion = Donacion(
            id=1,
            categoria="JUGUETES",
            descripcion="Pelota de fútbol nueva",
            cantidad=5,
            usuario_modificacion="admin2"
        )
        
        # Execute
        result = self.repository.actualizar_donacion(donacion)
        
        # Verify
        assert result is not None
        assert result.id == 1
        assert result.descripcion == "Pelota de fútbol nueva"
        assert result.cantidad == 5
        assert result.usuario_modificacion == "admin2"
        assert result.fecha_hora_modificacion is not None
        
        # Verify database calls
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
    
    @patch('src.repositories.donacion_repository.get_db_config')
    def test_eliminar_donacion_success(self, mock_get_db_config):
        """Test successful donation deletion"""
        # Setup mocks
        mock_db_config = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_get_db_config.return_value = mock_db_config
        mock_db_config.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1  # One row affected
        
        # Execute
        result = self.repository.eliminar_donacion(1, "admin")
        
        # Verify
        assert result == True
        
        # Verify database calls
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
    
    @patch('src.repositories.donacion_repository.get_db_config')
    def test_validar_stock_sufficient(self, mock_get_db_config):
        """Test stock validation with sufficient stock"""
        # Setup mocks
        mock_db_config = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_get_db_config.return_value = mock_db_config
        mock_db_config.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (20,)  # 20 units available
        
        # Execute
        tiene_stock, cantidad_disponible = self.repository.validar_stock(1, 15)
        
        # Verify
        assert tiene_stock == True
        assert cantidad_disponible == 20
        
        # Verify database call
        mock_cursor.execute.assert_called_once_with(
            "SELECT cantidad FROM donaciones WHERE id = %s AND eliminado = FALSE",
            (1,)
        )
    
    @patch('src.repositories.donacion_repository.get_db_config')
    def test_validar_stock_insufficient(self, mock_get_db_config):
        """Test stock validation with insufficient stock"""
        # Setup mocks
        mock_db_config = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_get_db_config.return_value = mock_db_config
        mock_db_config.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (5,)  # Only 5 units available
        
        # Execute
        tiene_stock, cantidad_disponible = self.repository.validar_stock(1, 10)
        
        # Verify
        assert tiene_stock == False
        assert cantidad_disponible == 5
    
    @patch('src.repositories.donacion_repository.get_db_config')
    def test_actualizar_stock_success(self, mock_get_db_config):
        """Test successful stock update"""
        # Setup mocks
        mock_db_config = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_get_db_config.return_value = mock_db_config
        mock_db_config.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Mock current quantity check
        mock_cursor.fetchone.return_value = (10,)  # Current quantity is 10
        mock_cursor.rowcount = 1  # Update successful
        
        # Execute
        nueva_cantidad = self.repository.actualizar_stock(
            donacion_id=1,
            cantidad_cambio=5,
            usuario_modificacion="admin",
            motivo="Transferencia a otra ONG"
        )
        
        # Verify
        assert nueva_cantidad == 15  # 10 + 5
        
        # Verify database calls (should be called 3 times: select, update, audit insert)
        assert mock_cursor.execute.call_count == 3
        mock_connection.commit.assert_called_once()
    
    @patch('src.repositories.donacion_repository.get_db_config')
    def test_actualizar_stock_insufficient(self, mock_get_db_config):
        """Test stock update with insufficient stock"""
        # Setup mocks
        mock_db_config = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()
        
        mock_get_db_config.return_value = mock_db_config
        mock_db_config.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Mock current quantity check
        mock_cursor.fetchone.return_value = (5,)  # Current quantity is 5
        
        # Execute and expect ValueError
        with pytest.raises(ValueError) as exc_info:
            self.repository.actualizar_stock(
                donacion_id=1,
                cantidad_cambio=-10,  # Trying to subtract 10 from 5
                usuario_modificacion="admin",
                motivo="Test"
            )
        
        assert "Stock insuficiente" in str(exc_info.value)
        mock_connection.rollback.assert_called_once()