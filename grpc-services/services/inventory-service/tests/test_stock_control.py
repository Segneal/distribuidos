"""
Tests for Stock Control and Validation functionality
"""
import pytest
from unittest.mock import Mock, patch
import grpc
from src.service.inventario_service import InventarioService
from src.inventory_pb2 import (
    ActualizarStockRequest, ValidarStockRequest
)

class TestStockControl:
    """Test cases for Stock Control functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.service = InventarioService()
        self.mock_context = Mock()
    
    @patch('src.service.inventario_service.DonacionRepository')
    def test_actualizar_stock_incrementar(self, mock_repo_class):
        """Test stock increment (receiving donations)"""
        # Setup mock
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.actualizar_stock.return_value = 25  # New quantity after increment
        
        service = InventarioService()
        
        # Create request to increment stock
        request = ActualizarStockRequest(
            donacionId=1,
            cantidadCambio=5,  # Add 5 units
            usuarioModificacion="admin",
            motivo="Donación recibida de otra ONG"
        )
        
        # Execute
        response = service.ActualizarStock(request, self.mock_context)
        
        # Verify
        assert response.exitoso == True
        assert response.mensaje == "Stock actualizado exitosamente"
        assert response.nuevaCantidad == 25
        mock_repo.actualizar_stock.assert_called_once_with(
            donacion_id=1,
            cantidad_cambio=5,
            usuario_modificacion="admin",
            motivo="Donación recibida de otra ONG"
        )
    
    @patch('src.service.inventario_service.DonacionRepository')
    def test_actualizar_stock_decrementar(self, mock_repo_class):
        """Test stock decrement (transferring donations)"""
        # Setup mock
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.actualizar_stock.return_value = 15  # New quantity after decrement
        
        service = InventarioService()
        
        # Create request to decrement stock
        request = ActualizarStockRequest(
            donacionId=1,
            cantidadCambio=-5,  # Remove 5 units
            usuarioModificacion="admin",
            motivo="Transferencia a ONG Solidaria"
        )
        
        # Execute
        response = service.ActualizarStock(request, self.mock_context)
        
        # Verify
        assert response.exitoso == True
        assert response.mensaje == "Stock actualizado exitosamente"
        assert response.nuevaCantidad == 15
        mock_repo.actualizar_stock.assert_called_once_with(
            donacion_id=1,
            cantidad_cambio=-5,
            usuario_modificacion="admin",
            motivo="Transferencia a ONG Solidaria"
        )
    
    @patch('src.service.inventario_service.DonacionRepository')
    def test_actualizar_stock_insuficiente(self, mock_repo_class):
        """Test stock update with insufficient stock"""
        # Setup mock to raise ValueError for insufficient stock
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.actualizar_stock.side_effect = ValueError("Stock insuficiente. Cantidad actual: 3, cambio solicitado: -10")
        
        service = InventarioService()
        
        # Create request that would cause insufficient stock
        request = ActualizarStockRequest(
            donacionId=1,
            cantidadCambio=-10,  # Try to remove 10 units when only 3 available
            usuarioModificacion="admin",
            motivo="Transferencia"
        )
        
        # Execute
        response = service.ActualizarStock(request, self.mock_context)
        
        # Verify
        assert response.exitoso == False
        assert "Stock insuficiente" in response.mensaje
        assert response.nuevaCantidad == 0
    
    @patch('src.service.inventario_service.DonacionRepository')
    def test_actualizar_stock_donacion_no_encontrada(self, mock_repo_class):
        """Test stock update for non-existent donation"""
        # Setup mock
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.actualizar_stock.return_value = None  # Donation not found
        
        service = InventarioService()
        
        # Create request for non-existent donation
        request = ActualizarStockRequest(
            donacionId=999,
            cantidadCambio=5,
            usuarioModificacion="admin",
            motivo="Test"
        )
        
        # Execute
        response = service.ActualizarStock(request, self.mock_context)
        
        # Verify
        assert response.exitoso == False
        assert response.mensaje == "Donación no encontrada"
        self.mock_context.set_code.assert_called_with(grpc.StatusCode.NOT_FOUND)
    
    def test_actualizar_stock_validaciones_entrada(self):
        """Test input validations for stock updates"""
        service = InventarioService()
        
        # Test invalid donation ID
        request = ActualizarStockRequest(
            donacionId=0,  # Invalid ID
            cantidadCambio=5,
            usuarioModificacion="admin",
            motivo="Test"
        )
        response = service.ActualizarStock(request, self.mock_context)
        assert response.exitoso == False
        assert response.mensaje == "ID de donación inválido"
        
        # Test zero change
        request = ActualizarStockRequest(
            donacionId=1,
            cantidadCambio=0,  # Zero change
            usuarioModificacion="admin",
            motivo="Test"
        )
        response = service.ActualizarStock(request, self.mock_context)
        assert response.exitoso == False
        assert response.mensaje == "El cambio de cantidad no puede ser cero"
    
    @patch('src.service.inventario_service.DonacionRepository')
    def test_validar_stock_suficiente(self, mock_repo_class):
        """Test stock validation with sufficient stock"""
        # Setup mock
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.validar_stock.return_value = (True, 20)  # Has sufficient stock, 20 available
        
        service = InventarioService()
        
        # Create validation request
        request = ValidarStockRequest(
            donacionId=1,
            cantidadRequerida=15  # Need 15, have 20
        )
        
        # Execute
        response = service.ValidarStock(request, self.mock_context)
        
        # Verify
        assert response.exitoso == True
        assert response.mensaje == "Stock suficiente"
        assert response.tieneStockSuficiente == True
        assert response.cantidadDisponible == 20
        mock_repo.validar_stock.assert_called_once_with(
            donacion_id=1,
            cantidad_requerida=15
        )
    
    @patch('src.service.inventario_service.DonacionRepository')
    def test_validar_stock_insuficiente(self, mock_repo_class):
        """Test stock validation with insufficient stock"""
        # Setup mock
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.validar_stock.return_value = (False, 5)  # Insufficient stock, only 5 available
        
        service = InventarioService()
        
        # Create validation request
        request = ValidarStockRequest(
            donacionId=1,
            cantidadRequerida=10  # Need 10, only have 5
        )
        
        # Execute
        response = service.ValidarStock(request, self.mock_context)
        
        # Verify
        assert response.exitoso == True
        assert response.mensaje == "Stock insuficiente"
        assert response.tieneStockSuficiente == False
        assert response.cantidadDisponible == 5
    
    @patch('src.service.inventario_service.DonacionRepository')
    def test_validar_stock_donacion_no_encontrada(self, mock_repo_class):
        """Test stock validation for non-existent donation"""
        # Setup mock
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.validar_stock.return_value = (False, 0)  # Not found
        
        service = InventarioService()
        
        # Create validation request
        request = ValidarStockRequest(
            donacionId=999,
            cantidadRequerida=5
        )
        
        # Execute
        response = service.ValidarStock(request, self.mock_context)
        
        # Verify
        assert response.exitoso == False
        assert response.mensaje == "Donación no encontrada"
        assert response.tieneStockSuficiente == False
        assert response.cantidadDisponible == 0
        self.mock_context.set_code.assert_called_with(grpc.StatusCode.NOT_FOUND)
    
    def test_validar_stock_validaciones_entrada(self):
        """Test input validations for stock validation"""
        service = InventarioService()
        
        # Test invalid donation ID
        request = ValidarStockRequest(
            donacionId=-1,  # Invalid ID
            cantidadRequerida=5
        )
        response = service.ValidarStock(request, self.mock_context)
        assert response.exitoso == False
        assert response.mensaje == "ID de donación inválido"
        assert response.tieneStockSuficiente == False
        assert response.cantidadDisponible == 0
        
        # Test negative required quantity
        request = ValidarStockRequest(
            donacionId=1,
            cantidadRequerida=-5  # Negative quantity
        )
        response = service.ValidarStock(request, self.mock_context)
        assert response.exitoso == False
        assert response.mensaje == "La cantidad requerida no puede ser negativa"
        assert response.tieneStockSuficiente == False
        assert response.cantidadDisponible == 0
    
    @patch('src.service.inventario_service.DonacionRepository')
    def test_flujo_completo_transferencia(self, mock_repo_class):
        """Test complete transfer flow: validate then update stock"""
        # Setup mock
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        service = InventarioService()
        
        # Step 1: Validate stock is sufficient
        mock_repo.validar_stock.return_value = (True, 20)  # 20 available
        
        validate_request = ValidarStockRequest(
            donacionId=1,
            cantidadRequerida=8
        )
        
        validate_response = service.ValidarStock(validate_request, self.mock_context)
        
        assert validate_response.exitoso == True
        assert validate_response.tieneStockSuficiente == True
        assert validate_response.cantidadDisponible == 20
        
        # Step 2: Update stock (transfer 8 units)
        mock_repo.actualizar_stock.return_value = 12  # 20 - 8 = 12
        
        update_request = ActualizarStockRequest(
            donacionId=1,
            cantidadCambio=-8,  # Remove 8 units
            usuarioModificacion="admin",
            motivo="Transferencia a ONG Hermanos Unidos"
        )
        
        update_response = service.ActualizarStock(update_request, self.mock_context)
        
        assert update_response.exitoso == True
        assert update_response.mensaje == "Stock actualizado exitosamente"
        assert update_response.nuevaCantidad == 12
        
        # Verify both operations were called
        mock_repo.validar_stock.assert_called_once()
        mock_repo.actualizar_stock.assert_called_once()
    
    @patch('src.service.inventario_service.DonacionRepository')
    def test_auditoria_cambios_stock(self, mock_repo_class):
        """Test that stock changes are properly audited"""
        # Setup mock
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.actualizar_stock.return_value = 30
        
        service = InventarioService()
        
        # Test different types of stock changes
        test_cases = [
            {
                'cambio': 10,
                'motivo': 'Donación recibida de empresa local',
                'usuario': 'vocal1'
            },
            {
                'cambio': -5,
                'motivo': 'Transferencia a ONG Corazón Solidario',
                'usuario': 'presidente'
            },
            {
                'cambio': 3,
                'motivo': 'Corrección de inventario',
                'usuario': 'vocal2'
            }
        ]
        
        for i, case in enumerate(test_cases, 1):
            request = ActualizarStockRequest(
                donacionId=i,
                cantidadCambio=case['cambio'],
                usuarioModificacion=case['usuario'],
                motivo=case['motivo']
            )
            
            response = service.ActualizarStock(request, self.mock_context)
            
            assert response.exitoso == True
            
            # Verify the repository was called with correct audit information
            mock_repo.actualizar_stock.assert_called_with(
                donacion_id=i,
                cantidad_cambio=case['cambio'],
                usuario_modificacion=case['usuario'],
                motivo=case['motivo']
            )
        
        # Verify all calls were made
        assert mock_repo.actualizar_stock.call_count == 3