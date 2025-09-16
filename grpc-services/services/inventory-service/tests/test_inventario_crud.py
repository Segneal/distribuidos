"""
Tests for Inventory Service CRUD operations
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import grpc
from src.service.inventario_service import InventarioService
from src.models.donacion import Donacion
from src.inventory_pb2 import (
    CrearDonacionRequest, ObtenerDonacionRequest, ListarDonacionesRequest,
    ActualizarDonacionRequest, EliminarDonacionRequest
)

class TestInventarioCRUD:
    """Test cases for Inventory Service CRUD operations"""
    
    def setup_method(self):
        """Setup test environment"""
        self.service = InventarioService()
        self.mock_context = Mock()
    
    @patch('src.service.inventario_service.DonacionRepository')
    def test_crear_donacion_exitoso(self, mock_repo_class):
        """Test successful donation creation"""
        # Setup mock
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        created_donacion = Donacion(
            id=1,
            categoria="ALIMENTOS",
            descripcion="Puré de tomates",
            cantidad=10,
            usuario_alta="admin"
        )
        mock_repo.crear_donacion.return_value = created_donacion
        
        # Create service with mocked repository
        service = InventarioService()
        
        # Create request
        request = CrearDonacionRequest(
            categoria="ALIMENTOS",
            descripcion="Puré de tomates",
            cantidad=10,
            usuarioCreador="admin"
        )
        
        # Execute
        response = service.CrearDonacion(request, self.mock_context)
        
        # Verify
        assert response.exitoso == True
        assert response.mensaje == "Donación creada exitosamente"
        assert response.donacion.categoria == "ALIMENTOS"
        assert response.donacion.descripcion == "Puré de tomates"
        assert response.donacion.cantidad == 10
        mock_repo.crear_donacion.assert_called_once()
    
    @patch('src.service.inventario_service.DonacionRepository')
    def test_crear_donacion_validacion_error(self, mock_repo_class):
        """Test donation creation with validation errors"""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        service = InventarioService()
        
        # Create invalid request (empty descripcion)
        request = CrearDonacionRequest(
            categoria="ALIMENTOS",
            descripcion="",  # Invalid - empty
            cantidad=10,
            usuarioCreador="admin"
        )
        
        # Execute
        response = service.CrearDonacion(request, self.mock_context)
        
        # Verify
        assert response.exitoso == False
        assert "Errores de validación" in response.mensaje
        mock_repo.crear_donacion.assert_not_called()
    
    @patch('src.service.inventario_service.DonacionRepository')
    def test_obtener_donacion_existente(self, mock_repo_class):
        """Test getting existing donation"""
        # Setup mock
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        existing_donacion = Donacion(
            id=1,
            categoria="ROPA",
            descripcion="Camisetas",
            cantidad=5,
            usuario_alta="admin"
        )
        mock_repo.obtener_donacion_por_id.return_value = existing_donacion
        
        service = InventarioService()
        
        # Create request
        request = ObtenerDonacionRequest(id=1)
        
        # Execute
        response = service.ObtenerDonacion(request, self.mock_context)
        
        # Verify
        assert response.exitoso == True
        assert response.mensaje == "Donación encontrada"
        assert response.donacion.id == 1
        assert response.donacion.categoria == "ROPA"
        mock_repo.obtener_donacion_por_id.assert_called_once_with(1)
    
    @patch('src.service.inventario_service.DonacionRepository')
    def test_obtener_donacion_no_encontrada(self, mock_repo_class):
        """Test getting non-existent donation"""
        # Setup mock
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.obtener_donacion_por_id.return_value = None
        
        service = InventarioService()
        
        # Create request
        request = ObtenerDonacionRequest(id=999)
        
        # Execute
        response = service.ObtenerDonacion(request, self.mock_context)
        
        # Verify
        assert response.exitoso == False
        assert response.mensaje == "Donación no encontrada"
        self.mock_context.set_code.assert_called_with(grpc.StatusCode.NOT_FOUND)
    
    @patch('src.service.inventario_service.DonacionRepository')
    def test_listar_donaciones(self, mock_repo_class):
        """Test listing donations"""
        # Setup mock
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        donaciones = [
            Donacion(id=1, categoria="ALIMENTOS", descripcion="Arroz", cantidad=20, usuario_alta="admin"),
            Donacion(id=2, categoria="ROPA", descripcion="Pantalones", cantidad=15, usuario_alta="admin")
        ]
        mock_repo.listar_donaciones.return_value = (donaciones, 2)
        
        service = InventarioService()
        
        # Create request
        request = ListarDonacionesRequest(
            pagina=1,
            tamanoPagina=10,
            categoria="",
            incluirEliminados=False
        )
        
        # Execute
        response = service.ListarDonaciones(request, self.mock_context)
        
        # Verify
        assert response.exitoso == True
        assert len(response.donaciones) == 2
        assert response.totalRegistros == 2
        assert response.donaciones[0].categoria == "ALIMENTOS"
        assert response.donaciones[1].categoria == "ROPA"
        mock_repo.listar_donaciones.assert_called_once_with(
            pagina=1, tamano_pagina=10, categoria=None, incluir_eliminados=False
        )
    
    @patch('src.service.inventario_service.DonacionRepository')
    def test_actualizar_donacion_exitoso(self, mock_repo_class):
        """Test successful donation update"""
        # Setup mock
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        existing_donacion = Donacion(
            id=1,
            categoria="JUGUETES",
            descripcion="Pelota vieja",
            cantidad=3,
            eliminado=False,
            usuario_alta="admin"
        )
        
        updated_donacion = Donacion(
            id=1,
            categoria="JUGUETES",
            descripcion="Pelota de fútbol nueva",
            cantidad=5,
            eliminado=False,
            usuario_alta="admin",
            usuario_modificacion="admin2"
        )
        
        mock_repo.obtener_donacion_por_id.return_value = existing_donacion
        mock_repo.actualizar_donacion.return_value = updated_donacion
        
        service = InventarioService()
        
        # Create request
        request = ActualizarDonacionRequest(
            id=1,
            descripcion="Pelota de fútbol nueva",
            cantidad=5,
            usuarioModificacion="admin2"
        )
        
        # Execute
        response = service.ActualizarDonacion(request, self.mock_context)
        
        # Verify
        assert response.exitoso == True
        assert response.mensaje == "Donación actualizada exitosamente"
        assert response.donacion.descripcion == "Pelota de fútbol nueva"
        assert response.donacion.cantidad == 5
        mock_repo.obtener_donacion_por_id.assert_called_once_with(1)
        mock_repo.actualizar_donacion.assert_called_once()
    
    @patch('src.service.inventario_service.DonacionRepository')
    def test_actualizar_donacion_no_encontrada(self, mock_repo_class):
        """Test updating non-existent donation"""
        # Setup mock
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.obtener_donacion_por_id.return_value = None
        
        service = InventarioService()
        
        # Create request
        request = ActualizarDonacionRequest(
            id=999,
            descripcion="Nueva descripción",
            cantidad=10,
            usuarioModificacion="admin"
        )
        
        # Execute
        response = service.ActualizarDonacion(request, self.mock_context)
        
        # Verify
        assert response.exitoso == False
        assert response.mensaje == "Donación no encontrada"
        self.mock_context.set_code.assert_called_with(grpc.StatusCode.NOT_FOUND)
        mock_repo.actualizar_donacion.assert_not_called()
    
    @patch('src.service.inventario_service.DonacionRepository')
    def test_actualizar_donacion_eliminada(self, mock_repo_class):
        """Test updating deleted donation"""
        # Setup mock
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        deleted_donacion = Donacion(
            id=1,
            categoria="ROPA",
            descripcion="Camiseta",
            cantidad=1,
            eliminado=True,  # Already deleted
            usuario_alta="admin"
        )
        mock_repo.obtener_donacion_por_id.return_value = deleted_donacion
        
        service = InventarioService()
        
        # Create request
        request = ActualizarDonacionRequest(
            id=1,
            descripcion="Nueva descripción",
            cantidad=10,
            usuarioModificacion="admin"
        )
        
        # Execute
        response = service.ActualizarDonacion(request, self.mock_context)
        
        # Verify
        assert response.exitoso == False
        assert response.mensaje == "No se puede actualizar una donación eliminada"
        mock_repo.actualizar_donacion.assert_not_called()
    
    @patch('src.service.inventario_service.DonacionRepository')
    def test_eliminar_donacion_exitoso(self, mock_repo_class):
        """Test successful donation deletion"""
        # Setup mock
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        existing_donacion = Donacion(
            id=1,
            categoria="UTILES_ESCOLARES",
            descripcion="Cuadernos",
            cantidad=10,
            eliminado=False,
            usuario_alta="admin"
        )
        
        mock_repo.obtener_donacion_por_id.return_value = existing_donacion
        mock_repo.eliminar_donacion.return_value = True
        
        service = InventarioService()
        
        # Create request
        request = EliminarDonacionRequest(
            id=1,
            usuarioEliminacion="admin"
        )
        
        # Execute
        response = service.EliminarDonacion(request, self.mock_context)
        
        # Verify
        assert response.exitoso == True
        assert response.mensaje == "Donación eliminada exitosamente"
        mock_repo.obtener_donacion_por_id.assert_called_once_with(1)
        mock_repo.eliminar_donacion.assert_called_once_with(1, "admin")
    
    @patch('src.service.inventario_service.DonacionRepository')
    def test_eliminar_donacion_ya_eliminada(self, mock_repo_class):
        """Test deleting already deleted donation"""
        # Setup mock
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        deleted_donacion = Donacion(
            id=1,
            categoria="ROPA",
            descripcion="Camiseta",
            cantidad=1,
            eliminado=True,  # Already deleted
            usuario_alta="admin"
        )
        mock_repo.obtener_donacion_por_id.return_value = deleted_donacion
        
        service = InventarioService()
        
        # Create request
        request = EliminarDonacionRequest(
            id=1,
            usuarioEliminacion="admin"
        )
        
        # Execute
        response = service.EliminarDonacion(request, self.mock_context)
        
        # Verify
        assert response.exitoso == False
        assert response.mensaje == "La donación ya está eliminada"
        mock_repo.eliminar_donacion.assert_not_called()
    
    def test_validacion_id_invalido(self):
        """Test validation of invalid IDs"""
        service = InventarioService()
        
        # Test ObtenerDonacion with invalid ID
        request = ObtenerDonacionRequest(id=0)
        response = service.ObtenerDonacion(request, self.mock_context)
        assert response.exitoso == False
        assert response.mensaje == "ID de donación inválido"
        
        # Test ActualizarDonacion with invalid ID
        request = ActualizarDonacionRequest(
            id=-1,
            descripcion="Test",
            cantidad=1,
            usuarioModificacion="admin"
        )
        response = service.ActualizarDonacion(request, self.mock_context)
        assert response.exitoso == False
        assert response.mensaje == "ID de donación inválido"
        
        # Test EliminarDonacion with invalid ID
        request = EliminarDonacionRequest(
            id=0,
            usuarioEliminacion="admin"
        )
        response = service.EliminarDonacion(request, self.mock_context)
        assert response.exitoso == False
        assert response.mensaje == "ID de donación inválido"