"""
Events gRPC Service Implementation
"""
import grpc
from datetime import datetime, timezone
from typing import List

try:
    import events_pb2, events_pb2_grpc
    from models.evento import Evento, DonacionRepartida, Participante
    from repositories.evento_repository import EventoRepository
    from ..kafka.kafka_client import kafka_client
except ImportError:
    # For testing or direct execution
    import events_pb2, events_pb2_grpc
    from models.evento import Evento, DonacionRepartida, Participante
    from repositories.evento_repository import EventoRepository
    from kafka_client_module.kafka_client import kafka_client

class EventoService(events_pb2_grpc.EventoServiceServicer):
    """gRPC service implementation for events management"""
    
    def __init__(self):
        self.evento_repository = EventoRepository()
    
    def CrearEvento(self, request, context):
        """Create a new event"""
        try:
            # Create event object
            evento = Evento(
                nombre=request.nombre,
                descripcion=request.descripcion,
                fecha_hora=request.fechaHora,
                usuario_alta=request.usuarioCreador
            )
            
            # Validate event data
            errores = evento.validar_datos_basicos()
            if errores:
                return events_pb2.EventoResponse(
                    exitoso=False,
                    mensaje=f"Errores de validación: {'; '.join(errores)}"
                )
            
            # Create event in database
            evento_creado = self.evento_repository.crear_evento(evento)
            
            if not evento_creado:
                return events_pb2.EventoResponse(
                    exitoso=False,
                    mensaje="Error al crear el evento en la base de datos"
                )
            
            # Publish event to Kafka for external ONGs
            try:
                evento_data = {
                    'id': evento_creado.id,
                    'nombre': evento_creado.nombre,
                    'descripcion': evento_creado.descripcion,
                    'fecha_hora': evento_creado.fecha_hora
                }
                kafka_client.publish_external_event(evento_data)
            except Exception as kafka_error:
                print(f"Warning: Could not publish event to Kafka: {kafka_error}")
                # Continue execution even if Kafka fails
            
            # Convert to protobuf
            evento_pb = self._evento_to_protobuf(evento_creado)
            
            return events_pb2.EventoResponse(
                exitoso=True,
                mensaje="Evento creado exitosamente",
                evento=evento_pb
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno del servidor: {str(e)}")
            return events_pb2.EventoResponse(
                exitoso=False,
                mensaje=f"Error interno: {str(e)}"
            )
    
    def ObtenerEvento(self, request, context):
        """Get event by ID"""
        try:
            evento = self.evento_repository.obtener_evento_por_id(request.id)
            
            if not evento:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return events_pb2.EventoResponse(
                    exitoso=False,
                    mensaje=f"Evento con ID {request.id} no encontrado"
                )
            
            evento_pb = self._evento_to_protobuf(evento)
            
            return events_pb2.EventoResponse(
                exitoso=True,
                mensaje="Evento obtenido exitosamente",
                evento=evento_pb
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno del servidor: {str(e)}")
            return events_pb2.EventoResponse(
                exitoso=False,
                mensaje=f"Error interno: {str(e)}"
            )
    
    def ListarEventos(self, request, context):
        """List events with pagination and filters"""
        try:
            pagina = max(1, request.pagina) if request.pagina > 0 else 1
            tamano_pagina = min(100, max(1, request.tamanoPagina)) if request.tamanoPagina > 0 else 10
            
            eventos, total_registros = self.evento_repository.listar_eventos(
                pagina=pagina,
                tamano_pagina=tamano_pagina,
                solo_futuros=request.soloFuturos,
                solo_pasados=request.soloPasados
            )
            
            eventos_pb = [self._evento_to_protobuf(evento) for evento in eventos]
            
            return events_pb2.ListarEventosResponse(
                exitoso=True,
                mensaje=f"Se encontraron {len(eventos)} eventos",
                eventos=eventos_pb,
                totalRegistros=total_registros
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno del servidor: {str(e)}")
            return events_pb2.ListarEventosResponse(
                exitoso=False,
                mensaje=f"Error interno: {str(e)}"
            )
    
    def ActualizarEvento(self, request, context):
        """Update event"""
        try:
            # Get existing event
            evento_existente = self.evento_repository.obtener_evento_por_id(request.id)
            
            if not evento_existente:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return events_pb2.EventoResponse(
                    exitoso=False,
                    mensaje=f"Evento con ID {request.id} no encontrado"
                )
            
            # Check if event can be modified
            if not evento_existente.puede_modificar_datos_basicos():
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                return events_pb2.EventoResponse(
                    exitoso=False,
                    mensaje="Solo se pueden modificar eventos futuros"
                )
            
            # Update event data
            evento_existente.nombre = request.nombre
            evento_existente.descripcion = request.descripcion
            evento_existente.fecha_hora = request.fechaHora
            evento_existente.usuario_modificacion = request.usuarioModificacion
            
            # Validate updated data
            errores = evento_existente.validar_datos_basicos()
            if errores:
                return events_pb2.EventoResponse(
                    exitoso=False,
                    mensaje=f"Errores de validación: {'; '.join(errores)}"
                )
            
            # Update in database
            evento_actualizado = self.evento_repository.actualizar_evento(evento_existente)
            
            if not evento_actualizado:
                return events_pb2.EventoResponse(
                    exitoso=False,
                    mensaje="Error al actualizar el evento en la base de datos"
                )
            
            evento_pb = self._evento_to_protobuf(evento_actualizado)
            
            return events_pb2.EventoResponse(
                exitoso=True,
                mensaje="Evento actualizado exitosamente",
                evento=evento_pb
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno del servidor: {str(e)}")
            return events_pb2.EventoResponse(
                exitoso=False,
                mensaje=f"Error interno: {str(e)}"
            )
    
    def EliminarEvento(self, request, context):
        """Delete event (only future events)"""
        try:
            # Get existing event
            evento = self.evento_repository.obtener_evento_por_id(request.id)
            
            if not evento:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return events_pb2.EliminarEventoResponse(
                    exitoso=False,
                    mensaje=f"Evento con ID {request.id} no encontrado"
                )
            
            # Check if event can be deleted
            if not evento.puede_eliminar():
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                return events_pb2.EliminarEventoResponse(
                    exitoso=False,
                    mensaje="Solo se pueden eliminar eventos futuros"
                )
            
            # Publish event cancellation to Kafka before deletion
            try:
                kafka_client.publish_event_cancellation(request.id)
            except Exception as kafka_error:
                print(f"Warning: Could not publish event cancellation to Kafka: {kafka_error}")
                # Continue execution even if Kafka fails
            
            # Delete event
            eliminado = self.evento_repository.eliminar_evento(request.id)
            
            if not eliminado:
                return events_pb2.EliminarEventoResponse(
                    exitoso=False,
                    mensaje="Error al eliminar el evento de la base de datos"
                )
            
            return events_pb2.EliminarEventoResponse(
                exitoso=True,
                mensaje="Evento eliminado exitosamente"
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno del servidor: {str(e)}")
            return events_pb2.EliminarEventoResponse(
                exitoso=False,
                mensaje=f"Error interno: {str(e)}"
            )
    
    def AgregarParticipante(self, request, context):
        """Add participant to event"""
        try:
            # Get event
            evento = self.evento_repository.obtener_evento_por_id(request.eventoId)
            
            if not evento:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return events_pb2.ParticipanteResponse(
                    exitoso=False,
                    mensaje=f"Evento con ID {request.eventoId} no encontrado"
                )
            
            # Get participant info
            participante_info = self.evento_repository.obtener_participante_info(request.usuarioId)
            
            if not participante_info:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return events_pb2.ParticipanteResponse(
                    exitoso=False,
                    mensaje=f"Usuario con ID {request.usuarioId} no encontrado o inactivo"
                )
            
            # Check if already participant
            if request.usuarioId in evento.participantes_ids:
                return events_pb2.ParticipanteResponse(
                    exitoso=False,
                    mensaje="El usuario ya es participante del evento"
                )
            
            # Add participant
            agregado = self.evento_repository.agregar_participante(request.eventoId, request.usuarioId)
            
            if not agregado:
                return events_pb2.ParticipanteResponse(
                    exitoso=False,
                    mensaje="Error al agregar participante al evento"
                )
            
            # Convert to protobuf
            participante_pb = self._participante_to_protobuf(participante_info)
            
            return events_pb2.ParticipanteResponse(
                exitoso=True,
                mensaje="Participante agregado exitosamente",
                participante=participante_pb
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno del servidor: {str(e)}")
            return events_pb2.ParticipanteResponse(
                exitoso=False,
                mensaje=f"Error interno: {str(e)}"
            )
    
    def QuitarParticipante(self, request, context):
        """Remove participant from event"""
        try:
            # Get event
            evento = self.evento_repository.obtener_evento_por_id(request.eventoId)
            
            if not evento:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return events_pb2.ParticipanteResponse(
                    exitoso=False,
                    mensaje=f"Evento con ID {request.eventoId} no encontrado"
                )
            
            # Check if user is participant
            if request.usuarioId not in evento.participantes_ids:
                return events_pb2.ParticipanteResponse(
                    exitoso=False,
                    mensaje="El usuario no es participante del evento"
                )
            
            # Remove participant
            removido = self.evento_repository.quitar_participante(request.eventoId, request.usuarioId)
            
            if not removido:
                return events_pb2.ParticipanteResponse(
                    exitoso=False,
                    mensaje="Error al quitar participante del evento"
                )
            
            return events_pb2.ParticipanteResponse(
                exitoso=True,
                mensaje="Participante removido exitosamente"
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno del servidor: {str(e)}")
            return events_pb2.ParticipanteResponse(
                exitoso=False,
                mensaje=f"Error interno: {str(e)}"
            )
    
    def RegistrarDonacionesRepartidas(self, request, context):
        """Register distributed donations for past events"""
        try:
            # Get event
            evento = self.evento_repository.obtener_evento_por_id(request.eventoId)
            
            if not evento:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return events_pb2.RegistrarDonacionesResponse(
                    exitoso=False,
                    mensaje=f"Evento con ID {request.eventoId} no encontrado"
                )
            
            # Check if donations can be registered (only past events)
            if not evento.puede_registrar_donaciones():
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                return events_pb2.RegistrarDonacionesResponse(
                    exitoso=False,
                    mensaje="Solo se pueden registrar donaciones en eventos pasados"
                )
            
            # Convert request donations
            donaciones = []
            for donacion_req in request.donaciones:
                donacion = DonacionRepartida(
                    donacion_id=donacion_req.donacionId,
                    cantidad_repartida=donacion_req.cantidadRepartida,
                    usuario_registro=request.usuarioRegistro
                )
                donaciones.append(donacion)
            
            # Register donations
            donaciones_registradas = self.evento_repository.registrar_donaciones_repartidas(
                request.eventoId, donaciones
            )
            
            if not donaciones_registradas:
                return events_pb2.RegistrarDonacionesResponse(
                    exitoso=False,
                    mensaje="Error al registrar las donaciones repartidas"
                )
            
            # Convert to protobuf
            donaciones_pb = [self._donacion_repartida_to_protobuf(d) for d in donaciones_registradas]
            
            return events_pb2.RegistrarDonacionesResponse(
                exitoso=True,
                mensaje=f"Se registraron {len(donaciones_registradas)} donaciones repartidas",
                donacionesRegistradas=donaciones_pb
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno del servidor: {str(e)}")
            return events_pb2.RegistrarDonacionesResponse(
                exitoso=False,
                mensaje=f"Error interno: {str(e)}"
            )
    
    def ListarEventosExternos(self, request, context):
        """List external events from other NGOs"""
        try:
            pagina = max(1, request.pagina) if request.pagina > 0 else 1
            tamano_pagina = min(100, max(1, request.tamanoPagina)) if request.tamanoPagina > 0 else 10
            
            eventos, total_registros = self.evento_repository.listar_eventos_externos(
                pagina=pagina,
                tamano_pagina=tamano_pagina,
                solo_futuros=request.soloFuturos
            )
            
            eventos_pb = [self._evento_externo_to_protobuf(evento) for evento in eventos]
            
            return events_pb2.ListarEventosExternosResponse(
                exitoso=True,
                mensaje=f"Se encontraron {len(eventos)} eventos externos",
                eventos=eventos_pb,
                totalRegistros=total_registros
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno del servidor: {str(e)}")
            return events_pb2.ListarEventosExternosResponse(
                exitoso=False,
                mensaje=f"Error interno: {str(e)}"
            )
    
    def _evento_to_protobuf(self, evento: Evento) -> events_pb2.Evento:
        """Convert Evento model to protobuf"""
        donaciones_pb = [self._donacion_repartida_to_protobuf(d) for d in evento.donaciones_repartidas]
        
        return events_pb2.Evento(
            id=evento.id or 0,
            nombre=evento.nombre,
            descripcion=evento.descripcion,
            fechaHora=evento.fecha_hora,
            participantesIds=evento.participantes_ids,
            donacionesRepartidas=donaciones_pb,
            fechaHoraAlta=evento.fecha_hora_alta or "",
            usuarioAlta=evento.usuario_alta or "",
            fechaHoraModificacion=evento.fecha_hora_modificacion or "",
            usuarioModificacion=evento.usuario_modificacion or ""
        )
    
    def _donacion_repartida_to_protobuf(self, donacion: DonacionRepartida) -> events_pb2.DonacionRepartida:
        """Convert DonacionRepartida model to protobuf"""
        return events_pb2.DonacionRepartida(
            donacionId=donacion.donacion_id,
            cantidadRepartida=donacion.cantidad_repartida,
            usuarioRegistro=donacion.usuario_registro,
            fechaHoraRegistro=donacion.fecha_hora_registro or ""
        )
    
    def _participante_to_protobuf(self, participante: Participante) -> events_pb2.Participante:
        """Convert Participante model to protobuf"""
        return events_pb2.Participante(
            usuarioId=participante.usuario_id,
            nombreUsuario=participante.nombre_usuario,
            nombre=participante.nombre,
            apellido=participante.apellido,
            rol=participante.rol,
            fechaAsignacion=participante.fecha_asignacion or ""
        )
    
    def _evento_externo_to_protobuf(self, evento_externo: dict) -> events_pb2.EventoExterno:
        """Convert external event dict to protobuf"""
        return events_pb2.EventoExterno(
            idOrganizacion=evento_externo.get('idOrganizacion', ''),
            idEvento=evento_externo.get('idEvento', ''),
            nombre=evento_externo.get('nombre', ''),
            descripcion=evento_externo.get('descripcion', ''),
            fechaHora=evento_externo.get('fechaHora', ''),
            fechaRecepcion=evento_externo.get('fechaRecepcion', '')
        )