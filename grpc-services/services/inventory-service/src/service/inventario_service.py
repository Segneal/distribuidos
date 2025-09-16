"""
gRPC service implementation for Inventory Service
"""
import grpc
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from inventory_pb2 import (
    DonacionResponse, ListarDonacionesResponse, EliminarDonacionResponse,
    ActualizarStockResponse, ValidarStockResponse, Donacion
)
from inventory_pb2_grpc import InventarioServiceServicer
from repositories.donacion_repository import DonacionRepository
from models.donacion import Donacion as DonacionModel

class InventarioService(InventarioServiceServicer):
    """gRPC service implementation for inventory management"""
    
    def __init__(self):
        self.donacion_repository = DonacionRepository()
    
    def _donacion_model_to_proto(self, donacion: DonacionModel) -> Donacion:
        """Convert Donacion model to protobuf message"""
        return Donacion(
            id=donacion.id or 0,
            categoria=donacion.categoria or "",
            descripcion=donacion.descripcion or "",
            cantidad=donacion.cantidad or 0,
            eliminado=donacion.eliminado or False,
            fechaHoraAlta=donacion.fecha_hora_alta.isoformat() if donacion.fecha_hora_alta else "",
            usuarioAlta=donacion.usuario_alta or "",
            fechaHoraModificacion=donacion.fecha_hora_modificacion.isoformat() if donacion.fecha_hora_modificacion else "",
            usuarioModificacion=donacion.usuario_modificacion or ""
        )
    
    def CrearDonacion(self, request, context):
        """Create a new donation"""
        try:
            # Create donation model
            donacion = DonacionModel(
                categoria=request.categoria,
                descripcion=request.descripcion,
                cantidad=request.cantidad,
                usuario_alta=request.usuarioCreador,
                eliminado=False
            )
            
            # Validate donation
            validation_errors = donacion.validate()
            if validation_errors:
                return DonacionResponse(
                    exitoso=False,
                    mensaje=f"Errores de validación: {', '.join(validation_errors)}"
                )
            
            # Create donation in database
            created_donacion = self.donacion_repository.crear_donacion(donacion)
            
            if created_donacion:
                return DonacionResponse(
                    exitoso=True,
                    mensaje="Donación creada exitosamente",
                    donacion=self._donacion_model_to_proto(created_donacion)
                )
            else:
                return DonacionResponse(
                    exitoso=False,
                    mensaje="Error al crear la donación"
                )
                
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno del servidor: {str(e)}")
            return DonacionResponse(
                exitoso=False,
                mensaje=f"Error interno: {str(e)}"
            )
    
    def ObtenerDonacion(self, request, context):
        """Get donation by ID"""
        try:
            if request.id <= 0:
                return DonacionResponse(
                    exitoso=False,
                    mensaje="ID de donación inválido"
                )
            
            donacion = self.donacion_repository.obtener_donacion_por_id(request.id)
            
            if donacion:
                return DonacionResponse(
                    exitoso=True,
                    mensaje="Donación encontrada",
                    donacion=self._donacion_model_to_proto(donacion)
                )
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return DonacionResponse(
                    exitoso=False,
                    mensaje="Donación no encontrada"
                )
                
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno del servidor: {str(e)}")
            return DonacionResponse(
                exitoso=False,
                mensaje=f"Error interno: {str(e)}"
            )
    
    def ListarDonaciones(self, request, context):
        """List donations with pagination and filters"""
        try:
            pagina = max(1, request.pagina) if request.pagina > 0 else 1
            tamano_pagina = min(100, max(1, request.tamanoPagina)) if request.tamanoPagina > 0 else 10
            categoria = request.categoria if request.categoria else None
            incluir_eliminados = request.incluirEliminados
            
            donaciones, total_records = self.donacion_repository.listar_donaciones(
                pagina=pagina,
                tamano_pagina=tamano_pagina,
                categoria=categoria,
                incluir_eliminados=incluir_eliminados
            )
            
            donaciones_proto = [self._donacion_model_to_proto(d) for d in donaciones]
            
            return ListarDonacionesResponse(
                exitoso=True,
                mensaje=f"Se encontraron {len(donaciones)} donaciones",
                donaciones=donaciones_proto,
                totalRegistros=total_records
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno del servidor: {str(e)}")
            return ListarDonacionesResponse(
                exitoso=False,
                mensaje=f"Error interno: {str(e)}",
                donaciones=[],
                totalRegistros=0
            )
    
    def ActualizarDonacion(self, request, context):
        """Update donation (only descripcion and cantidad)"""
        try:
            if request.id <= 0:
                return DonacionResponse(
                    exitoso=False,
                    mensaje="ID de donación inválido"
                )
            
            # Get existing donation
            existing_donacion = self.donacion_repository.obtener_donacion_por_id(request.id)
            if not existing_donacion:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return DonacionResponse(
                    exitoso=False,
                    mensaje="Donación no encontrada"
                )
            
            if existing_donacion.eliminado:
                return DonacionResponse(
                    exitoso=False,
                    mensaje="No se puede actualizar una donación eliminada"
                )
            
            # Update only allowed fields
            existing_donacion.descripcion = request.descripcion
            existing_donacion.cantidad = request.cantidad
            existing_donacion.usuario_modificacion = request.usuarioModificacion
            
            # Validate updated donation
            validation_errors = existing_donacion.validate()
            if validation_errors:
                return DonacionResponse(
                    exitoso=False,
                    mensaje=f"Errores de validación: {', '.join(validation_errors)}"
                )
            
            # Update in database
            updated_donacion = self.donacion_repository.actualizar_donacion(existing_donacion)
            
            if updated_donacion:
                return DonacionResponse(
                    exitoso=True,
                    mensaje="Donación actualizada exitosamente",
                    donacion=self._donacion_model_to_proto(updated_donacion)
                )
            else:
                return DonacionResponse(
                    exitoso=False,
                    mensaje="Error al actualizar la donación"
                )
                
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno del servidor: {str(e)}")
            return DonacionResponse(
                exitoso=False,
                mensaje=f"Error interno: {str(e)}"
            )
    
    def EliminarDonacion(self, request, context):
        """Logical deletion of donation"""
        try:
            if request.id <= 0:
                return EliminarDonacionResponse(
                    exitoso=False,
                    mensaje="ID de donación inválido"
                )
            
            # Check if donation exists and is not already deleted
            existing_donacion = self.donacion_repository.obtener_donacion_por_id(request.id)
            if not existing_donacion:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return EliminarDonacionResponse(
                    exitoso=False,
                    mensaje="Donación no encontrada"
                )
            
            if existing_donacion.eliminado:
                return EliminarDonacionResponse(
                    exitoso=False,
                    mensaje="La donación ya está eliminada"
                )
            
            # Perform logical deletion
            success = self.donacion_repository.eliminar_donacion(request.id, request.usuarioEliminacion)
            
            if success:
                return EliminarDonacionResponse(
                    exitoso=True,
                    mensaje="Donación eliminada exitosamente"
                )
            else:
                return EliminarDonacionResponse(
                    exitoso=False,
                    mensaje="Error al eliminar la donación"
                )
                
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno del servidor: {str(e)}")
            return EliminarDonacionResponse(
                exitoso=False,
                mensaje=f"Error interno: {str(e)}"
            )
    
    def ActualizarStock(self, request, context):
        """Update stock quantity for transfers"""
        try:
            if request.donacionId <= 0:
                return ActualizarStockResponse(
                    exitoso=False,
                    mensaje="ID de donación inválido"
                )
            
            if request.cantidadCambio == 0:
                return ActualizarStockResponse(
                    exitoso=False,
                    mensaje="El cambio de cantidad no puede ser cero"
                )
            
            # Update stock
            nueva_cantidad = self.donacion_repository.actualizar_stock(
                donacion_id=request.donacionId,
                cantidad_cambio=request.cantidadCambio,
                usuario_modificacion=request.usuarioModificacion,
                motivo=request.motivo
            )
            
            if nueva_cantidad is not None:
                return ActualizarStockResponse(
                    exitoso=True,
                    mensaje="Stock actualizado exitosamente",
                    nuevaCantidad=nueva_cantidad
                )
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return ActualizarStockResponse(
                    exitoso=False,
                    mensaje="Donación no encontrada"
                )
                
        except ValueError as e:
            return ActualizarStockResponse(
                exitoso=False,
                mensaje=str(e)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno del servidor: {str(e)}")
            return ActualizarStockResponse(
                exitoso=False,
                mensaje=f"Error interno: {str(e)}"
            )
    
    def ValidarStock(self, request, context):
        """Validate if there's enough stock"""
        try:
            if request.donacionId <= 0:
                return ValidarStockResponse(
                    exitoso=False,
                    mensaje="ID de donación inválido",
                    tieneStockSuficiente=False,
                    cantidadDisponible=0
                )
            
            if request.cantidadRequerida < 0:
                return ValidarStockResponse(
                    exitoso=False,
                    mensaje="La cantidad requerida no puede ser negativa",
                    tieneStockSuficiente=False,
                    cantidadDisponible=0
                )
            
            # Validate stock
            tiene_stock_suficiente, cantidad_disponible = self.donacion_repository.validar_stock(
                donacion_id=request.donacionId,
                cantidad_requerida=request.cantidadRequerida
            )
            
            if cantidad_disponible == 0 and not tiene_stock_suficiente:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return ValidarStockResponse(
                    exitoso=False,
                    mensaje="Donación no encontrada",
                    tieneStockSuficiente=False,
                    cantidadDisponible=0
                )
            
            mensaje = "Stock suficiente" if tiene_stock_suficiente else "Stock insuficiente"
            
            return ValidarStockResponse(
                exitoso=True,
                mensaje=mensaje,
                tieneStockSuficiente=tiene_stock_suficiente,
                cantidadDisponible=cantidad_disponible
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno del servidor: {str(e)}")
            return ValidarStockResponse(
                exitoso=False,
                mensaje=f"Error interno: {str(e)}",
                tieneStockSuficiente=False,
                cantidadDisponible=0
            )