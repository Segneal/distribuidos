"""
Tests for Donacion model
"""
import pytest
from datetime import datetime
from src.models.donacion import Donacion, CategoriaEnum

class TestDonacionModel:
    """Test cases for Donacion model"""
    
    def test_crear_donacion_valida(self):
        """Test creating a valid donation"""
        donacion = Donacion(
            categoria="ALIMENTOS",
            descripcion="Puré de tomates",
            cantidad=10,
            usuario_alta="admin"
        )
        
        assert donacion.categoria == "ALIMENTOS"
        assert donacion.descripcion == "Puré de tomates"
        assert donacion.cantidad == 10
        assert donacion.usuario_alta == "admin"
        assert donacion.eliminado == False
        assert donacion.is_valid() == True
    
    def test_validacion_categoria_requerida(self):
        """Test that categoria is required"""
        donacion = Donacion(
            descripcion="Test",
            cantidad=5,
            usuario_alta="admin"
        )
        
        errors = donacion.validate()
        assert "Categoría es requerida" in errors
        assert donacion.is_valid() == False
    
    def test_validacion_categoria_invalida(self):
        """Test invalid categoria validation"""
        donacion = Donacion(
            categoria="CATEGORIA_INVALIDA",
            descripcion="Test",
            cantidad=5,
            usuario_alta="admin"
        )
        
        errors = donacion.validate()
        assert any("Categoría inválida" in error for error in errors)
        assert donacion.is_valid() == False
    
    def test_validacion_descripcion_requerida(self):
        """Test that descripcion is required"""
        donacion = Donacion(
            categoria="ROPA",
            cantidad=5,
            usuario_alta="admin"
        )
        
        errors = donacion.validate()
        assert "Descripción es requerida" in errors
        assert donacion.is_valid() == False
    
    def test_validacion_descripcion_muy_corta(self):
        """Test descripcion minimum length validation"""
        donacion = Donacion(
            categoria="ROPA",
            descripcion="AB",
            cantidad=5,
            usuario_alta="admin"
        )
        
        errors = donacion.validate()
        assert "Descripción debe tener al menos 3 caracteres" in errors
        assert donacion.is_valid() == False
    
    def test_validacion_cantidad_negativa(self):
        """Test that cantidad cannot be negative"""
        donacion = Donacion(
            categoria="JUGUETES",
            descripcion="Pelota de fútbol",
            cantidad=-1,
            usuario_alta="admin"
        )
        
        errors = donacion.validate()
        assert "Cantidad no puede ser negativa" in errors
        assert donacion.is_valid() == False
    
    def test_validacion_cantidad_cero_valida(self):
        """Test that cantidad can be zero"""
        donacion = Donacion(
            categoria="UTILES_ESCOLARES",
            descripcion="Cuadernos",
            cantidad=0,
            usuario_alta="admin"
        )
        
        assert donacion.is_valid() == True
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        fecha_alta = datetime.now()
        donacion = Donacion(
            id=1,
            categoria="ALIMENTOS",
            descripcion="Arroz",
            cantidad=20,
            eliminado=False,
            fecha_hora_alta=fecha_alta,
            usuario_alta="admin"
        )
        
        dict_data = donacion.to_dict()
        
        assert dict_data['id'] == 1
        assert dict_data['categoria'] == "ALIMENTOS"
        assert dict_data['descripcion'] == "Arroz"
        assert dict_data['cantidad'] == 20
        assert dict_data['eliminado'] == False
        assert dict_data['fecha_hora_alta'] == fecha_alta.isoformat()
        assert dict_data['usuario_alta'] == "admin"
    
    def test_from_dict(self):
        """Test creation from dictionary"""
        fecha_alta = datetime.now()
        dict_data = {
            'id': 1,
            'categoria': 'ROPA',
            'descripcion': 'Camisetas',
            'cantidad': 15,
            'eliminado': False,
            'fecha_hora_alta': fecha_alta.isoformat(),
            'usuario_alta': 'admin'
        }
        
        donacion = Donacion.from_dict(dict_data)
        
        assert donacion.id == 1
        assert donacion.categoria == 'ROPA'
        assert donacion.descripcion == 'Camisetas'
        assert donacion.cantidad == 15
        assert donacion.eliminado == False
        assert donacion.fecha_hora_alta == fecha_alta
        assert donacion.usuario_alta == 'admin'
    
    def test_categoria_enum_values(self):
        """Test that all categoria enum values are valid"""
        valid_categories = [cat.value for cat in CategoriaEnum]
        expected_categories = ['ROPA', 'ALIMENTOS', 'JUGUETES', 'UTILES_ESCOLARES']
        
        assert set(valid_categories) == set(expected_categories)
        
        # Test each category is valid
        for categoria in valid_categories:
            donacion = Donacion(
                categoria=categoria,
                descripcion="Test item",
                cantidad=1,
                usuario_alta="admin"
            )
            assert donacion.is_valid() == True