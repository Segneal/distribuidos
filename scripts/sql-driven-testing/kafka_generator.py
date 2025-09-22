#!/usr/bin/env python3
"""
Kafka Test Generator for Inter-NGO Communication
Sistema ONG - SQL Driven Testing

This module generates Kafka test scenarios for inter-NGO communication
using data extracted from the populated SQL database.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import uuid
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaTestGenerator:
    """Generates Kafka test scenarios for inter-NGO communication"""
    
    def __init__(self, extracted_data: Dict[str, Any]):
        self.data = extracted_data
        self.organization_id = "ong-empuje-comunitario"
        self.kafka_topics = {
            'solicitud_donaciones': 'solicitud-donaciones',
            'oferta_donaciones': 'oferta-donaciones',
            'transferencia_donaciones': 'transferencia-donaciones',
            'baja_solicitud_donaciones': 'baja-solicitud-donaciones',
            'eventos_solidarios': 'eventos-solidarios',
            'baja_evento_solidario': 'baja-evento-solidario',
            'adhesion_evento': 'adhesion-evento'
        }
    
    def generate_all_kafka_scenarios(self) -> Dict[str, List[Dict]]:
        """Generate all Kafka test scenarios for inter-NGO communication"""
        logger.info("Generating Kafka test scenarios for inter-NGO communication")
        
        scenarios = {
            'solicitud_donaciones': self.generate_donation_request_scenarios(),
            'oferta_donaciones': self.generate_donation_offer_scenarios(),
            'transferencia_donaciones': self.generate_transfer_scenarios(),
            'baja_solicitud_donaciones': self.generate_request_cancellation_scenarios(),
            'eventos_solidarios': self.generate_external_event_scenarios(),
            'baja_evento_solidario': self.generate_event_cancellation_scenarios(),
            'adhesion_evento': self.generate_event_adhesion_scenarios()
        }
        
        total_scenarios = sum(len(topic_scenarios) for topic_scenarios in scenarios.values())
        logger.info(f"Generated {total_scenarios} Kafka test scenarios across {len(scenarios)} topics")
        
        return scenarios
    
    def generate_donation_request_scenarios(self) -> List[Dict]:
        """Generate donation request scenarios using real data"""
        logger.info("Generating donation request scenarios")
        
        scenarios = []
        vocal_user = self._get_user_by_role('VOCAL')[0]
        
        # Scenario 1: Single category request - ALIMENTOS
        scenarios.append({
            'scenario_name': 'Solicitud de Alimentos - Caso Exitoso',
            'topic': self.kafka_topics['solicitud_donaciones'],
            'message_key': f"{self.organization_id}-req-{self._generate_id()}",
            'message': {
                'idOrganizacion': self.organization_id,
                'idSolicitud': f"req-{self._generate_id()}",
                'donaciones': [
                    {
                        'categoria': 'ALIMENTOS',
                        'descripcion': 'Arroz y fideos para familias necesitadas'
                    },
                    {
                        'categoria': 'ALIMENTOS', 
                        'descripcion': 'Leche en polvo para programa nutricional'
                    }
                ],
                'usuarioSolicitante': vocal_user['nombre_usuario'],
                'contacto': {
                    'email': vocal_user['email'],
                    'telefono': vocal_user['telefono']
                },
                'timestamp': datetime.now().isoformat()
            },
            'pre_conditions': [
                f"Usuario {vocal_user['nombre_usuario']} debe tener rol VOCAL",
                "Usuario debe estar autenticado",
                "Sistema Kafka debe estar disponible"
            ],
            'post_conditions': [
                'Mensaje publicado exitosamente en topic solicitud-donaciones',
                'Otras ONGs pueden ver la solicitud',
                'Solicitud registrada en tabla solicitudes_propias',
                'Auditoría de solicitud creada'
            ],
            'test_assertions': [
                'Mensaje enviado sin errores',
                'Estructura JSON válida',
                'Campos obligatorios presentes',
                'ID de solicitud único generado'
            ],
            'expected_external_response': True,
            'timeout_seconds': 30
        })
        
        # Scenario 2: Multiple categories request
        scenarios.append({
            'scenario_name': 'Solicitud Múltiple Categorías',
            'topic': self.kafka_topics['solicitud_donaciones'],
            'message_key': f"{self.organization_id}-req-{self._generate_id()}",
            'message': {
                'idOrganizacion': self.organization_id,
                'idSolicitud': f"req-{self._generate_id()}",
                'donaciones': [
                    {'categoria': 'ROPA', 'descripcion': 'Ropa de invierno para adultos'},
                    {'categoria': 'JUGUETES', 'descripcion': 'Juguetes educativos para niños'},
                    {'categoria': 'UTILES_ESCOLARES', 'descripcion': 'Útiles para educación primaria'}
                ],
                'usuarioSolicitante': vocal_user['nombre_usuario'],
                'contacto': {
                    'email': vocal_user['email'],
                    'telefono': vocal_user['telefono']
                },
                'timestamp': datetime.now().isoformat()
            },
            'pre_conditions': [
                f"Usuario {vocal_user['nombre_usuario']} debe tener permisos de solicitud",
                "Conexión a Kafka establecida"
            ],
            'post_conditions': [
                'Solicitud multi-categoría registrada correctamente',
                'Notificación enviada a red de ONGs'
            ],
            'test_assertions': [
                'Todas las categorías incluidas en el mensaje',
                'Formato de mensaje consistente',
                'Timestamp válido'
            ],
            'expected_external_response': True,
            'timeout_seconds': 30
        })
        
        # Scenario 3: Request with validation error
        scenarios.append({
            'scenario_name': 'Solicitud con Error de Validación',
            'topic': self.kafka_topics['solicitud_donaciones'],
            'message_key': f"{self.organization_id}-req-invalid",
            'message': {
                'idOrganizacion': self.organization_id,
                'idSolicitud': f"req-{self._generate_id()}",
                'donaciones': [
                    {'categoria': 'CATEGORIA_INVALIDA', 'descripcion': 'Categoría no válida'}
                ],
                'usuarioSolicitante': vocal_user['nombre_usuario'],
                'timestamp': datetime.now().isoformat()
                # Missing contacto field intentionally
            },
            'pre_conditions': [
                "Sistema debe validar estructura de mensajes"
            ],
            'post_conditions': [
                'Mensaje rechazado por validación',
                'Error registrado en logs'
            ],
            'test_assertions': [
                'Error de validación detectado',
                'Mensaje no procesado',
                'Log de error generado'
            ],
            'expected_external_response': False,
            'expected_error': 'ValidationError',
            'timeout_seconds': 10
        })
        
        return scenarios
    
    def generate_donation_offer_scenarios(self) -> List[Dict]:
        """Generate donation offer scenarios using real inventory data"""
        logger.info("Generating donation offer scenarios")
        
        scenarios = []
        vocal_user = self._get_user_by_role('VOCAL')[0]
        
        # Get high stock donations for offers
        high_stock_alimentos = self._get_high_stock_donations('ALIMENTOS')
        high_stock_ropa = self._get_high_stock_donations('ROPA')
        
        if high_stock_alimentos:
            donation = high_stock_alimentos[0]
            offer_quantity = min(20, donation['cantidad'] // 2)  # Offer half of stock, max 20
            
            scenarios.append({
                'scenario_name': 'Oferta de Alimentos - Stock Alto',
                'topic': self.kafka_topics['oferta_donaciones'],
                'message_key': f"{self.organization_id}-off-{self._generate_id()}",
                'message': {
                    'idOrganizacion': self.organization_id,
                    'idOferta': f"off-{self._generate_id()}",
                    'donaciones': [
                        {
                            'id': donation['id'],
                            'categoria': donation['categoria'],
                            'descripcion': donation['descripcion'],
                            'cantidad': offer_quantity
                        }
                    ],
                    'usuarioOfertante': vocal_user['nombre_usuario'],
                    'contacto': {
                        'email': vocal_user['email'],
                        'telefono': vocal_user['telefono']
                    },
                    'validoHasta': (datetime.now() + timedelta(days=30)).isoformat(),
                    'timestamp': datetime.now().isoformat()
                },
                'pre_conditions': [
                    f"Donación {donation['id']} debe tener stock >= {offer_quantity}",
                    f"Usuario {vocal_user['nombre_usuario']} debe tener permisos",
                    "Stock actual debe ser verificado"
                ],
                'post_conditions': [
                    'Oferta publicada en red inter-ONG',
                    'Stock reservado temporalmente',
                    'Oferta registrada en ofertas_propias'
                ],
                'test_assertions': [
                    'Cantidad ofrecida <= stock disponible',
                    'Fecha de validez futura',
                    'Datos de contacto incluidos'
                ],
                'expected_external_response': True,
                'timeout_seconds': 30
            })
        
        if high_stock_ropa:
            donation = high_stock_ropa[0]
            offer_quantity = min(15, donation['cantidad'] // 3)
            
            scenarios.append({
                'scenario_name': 'Oferta de Ropa - Múltiples Items',
                'topic': self.kafka_topics['oferta_donaciones'],
                'message_key': f"{self.organization_id}-off-{self._generate_id()}",
                'message': {
                    'idOrganizacion': self.organization_id,
                    'idOferta': f"off-{self._generate_id()}",
                    'donaciones': [
                        {
                            'id': donation['id'],
                            'categoria': donation['categoria'],
                            'descripcion': donation['descripcion'],
                            'cantidad': offer_quantity
                        }
                    ],
                    'usuarioOfertante': vocal_user['nombre_usuario'],
                    'contacto': {
                        'email': vocal_user['email'],
                        'telefono': vocal_user['telefono']
                    },
                    'condiciones': 'Retiro coordinado, ropa en buen estado',
                    'validoHasta': (datetime.now() + timedelta(days=15)).isoformat(),
                    'timestamp': datetime.now().isoformat()
                },
                'pre_conditions': [
                    f"Stock de donación {donation['id']} verificado",
                    "Usuario autorizado para ofertas"
                ],
                'post_conditions': [
                    'Oferta visible para otras ONGs',
                    'Condiciones especiales incluidas'
                ],
                'test_assertions': [
                    'Condiciones adicionales presentes',
                    'Validez temporal correcta'
                ],
                'expected_external_response': True,
                'timeout_seconds': 30
            })
        
        # Scenario with insufficient stock (error case)
        zero_stock_donations = self._get_zero_stock_donations()
        if zero_stock_donations:
            donation = zero_stock_donations[0]
            
            scenarios.append({
                'scenario_name': 'Oferta con Stock Insuficiente - Error',
                'topic': self.kafka_topics['oferta_donaciones'],
                'message_key': f"{self.organization_id}-off-error",
                'message': {
                    'idOrganizacion': self.organization_id,
                    'idOferta': f"off-{self._generate_id()}",
                    'donaciones': [
                        {
                            'id': donation['id'],
                            'categoria': donation['categoria'],
                            'descripcion': donation['descripcion'],
                            'cantidad': 10  # Trying to offer more than available (0)
                        }
                    ],
                    'usuarioOfertante': vocal_user['nombre_usuario'],
                    'timestamp': datetime.now().isoformat()
                },
                'pre_conditions': [
                    f"Donación {donation['id']} tiene stock = 0",
                    "Sistema debe validar stock antes de ofertar"
                ],
                'post_conditions': [
                    'Oferta rechazada por stock insuficiente',
                    'Error registrado en auditoría'
                ],
                'test_assertions': [
                    'Error de stock insuficiente detectado',
                    'Oferta no publicada',
                    'Mensaje de error apropiado'
                ],
                'expected_external_response': False,
                'expected_error': 'InsufficientStockError',
                'timeout_seconds': 10
            })
        
        return scenarios
    
    def generate_transfer_scenarios(self) -> List[Dict]:
        """Generate transfer scenarios using real donation and request data"""
        logger.info("Generating transfer scenarios")
        
        scenarios = []
        vocal_user = self._get_user_by_role('VOCAL')[0]
        
        # Get external requests to respond to
        external_requests = self.data['network']['external_requests']
        active_requests = [req for req in external_requests if req['activa']]
        
        if active_requests:
            request = active_requests[0]  # Use first active request
            
            # Find matching donation in our inventory
            matching_donations = self._get_donations_by_category(request['categoria'])
            high_stock_matches = [d for d in matching_donations if d['cantidad'] > 10]
            
            if high_stock_matches:
                donation = high_stock_matches[0]
                transfer_quantity = min(10, donation['cantidad'] // 2)
                
                scenarios.append({
                    'scenario_name': 'Transferencia de Donaciones Exitosa',
                    'topic': f"{self.kafka_topics['transferencia_donaciones']}/{request['id_organizacion']}",
                    'message_key': f"{self.organization_id}-transfer-{request['id_solicitud']}",
                    'message': {
                        'idOrganizacion': self.organization_id,
                        'idSolicitud': request['id_solicitud'],
                        'donaciones': [
                            {
                                'id': donation['id'],
                                'categoria': donation['categoria'],
                                'descripcion': donation['descripcion'],
                                'cantidad': transfer_quantity
                            }
                        ],
                        'usuarioTransferencia': vocal_user['nombre_usuario'],
                        'organizacionDestino': request['id_organizacion'],
                        'mensaje': f"Transferencia en respuesta a solicitud {request['id_solicitud']}",
                        'coordenadas': {
                            'contacto': vocal_user['email'],
                            'telefono': vocal_user['telefono']
                        },
                        'timestamp': datetime.now().isoformat()
                    },
                    'pre_conditions': [
                        f"Solicitud {request['id_solicitud']} debe estar activa",
                        f"Donación {donation['id']} debe tener stock >= {transfer_quantity}",
                        f"Usuario {vocal_user['nombre_usuario']} debe tener permisos de transferencia",
                        f"Organización {request['id_organizacion']} debe estar activa"
                    ],
                    'post_conditions': [
                        f"Stock de donación {donation['id']} reducido en {transfer_quantity}",
                        'Transferencia registrada en transferencias_enviadas',
                        'Mensaje enviado a topic específico de organización',
                        'Auditoría de transferencia creada',
                        'Notificación enviada a organización destino'
                    ],
                    'test_assertions': [
                        'Stock actualizado correctamente',
                        'Mensaje enviado al topic correcto',
                        'Datos de coordinación incluidos',
                        'Timestamp válido'
                    ],
                    'expected_external_response': True,
                    'timeout_seconds': 45
                })
        
        # Scenario with multiple donations transfer
        if len(active_requests) > 1:
            request = active_requests[1]
            matching_donations = self._get_donations_by_category(request['categoria'])
            available_donations = [d for d in matching_donations if d['cantidad'] > 5]
            
            if len(available_donations) >= 2:
                scenarios.append({
                    'scenario_name': 'Transferencia Múltiple - Varias Donaciones',
                    'topic': f"{self.kafka_topics['transferencia_donaciones']}/{request['id_organizacion']}",
                    'message_key': f"{self.organization_id}-multi-transfer-{request['id_solicitud']}",
                    'message': {
                        'idOrganizacion': self.organization_id,
                        'idSolicitud': request['id_solicitud'],
                        'donaciones': [
                            {
                                'id': available_donations[0]['id'],
                                'categoria': available_donations[0]['categoria'],
                                'descripcion': available_donations[0]['descripcion'],
                                'cantidad': min(5, available_donations[0]['cantidad'] // 3)
                            },
                            {
                                'id': available_donations[1]['id'],
                                'categoria': available_donations[1]['categoria'],
                                'descripcion': available_donations[1]['descripcion'],
                                'cantidad': min(3, available_donations[1]['cantidad'] // 4)
                            }
                        ],
                        'usuarioTransferencia': vocal_user['nombre_usuario'],
                        'organizacionDestino': request['id_organizacion'],
                        'mensaje': 'Transferencia parcial de múltiples donaciones',
                        'timestamp': datetime.now().isoformat()
                    },
                    'pre_conditions': [
                        'Múltiples donaciones con stock suficiente',
                        'Solicitud externa válida y activa'
                    ],
                    'post_conditions': [
                        'Stock de múltiples donaciones actualizado',
                        'Transferencia compleja registrada'
                    ],
                    'test_assertions': [
                        'Múltiples donaciones procesadas',
                        'Stock de cada donación actualizado correctamente'
                    ],
                    'expected_external_response': True,
                    'timeout_seconds': 60
                })
        
        # Error scenario - insufficient stock
        if active_requests:
            request = active_requests[0]
            low_stock_donations = self._get_low_stock_donations(request['categoria'])
            
            if low_stock_donations:
                donation = low_stock_donations[0]
                
                scenarios.append({
                    'scenario_name': 'Transferencia con Stock Insuficiente - Error',
                    'topic': f"{self.kafka_topics['transferencia_donaciones']}/{request['id_organizacion']}",
                    'message_key': f"{self.organization_id}-error-transfer-{request['id_solicitud']}",
                    'message': {
                        'idOrganizacion': self.organization_id,
                        'idSolicitud': request['id_solicitud'],
                        'donaciones': [
                            {
                                'id': donation['id'],
                                'categoria': donation['categoria'],
                                'descripcion': donation['descripcion'],
                                'cantidad': donation['cantidad'] + 10  # More than available
                            }
                        ],
                        'usuarioTransferencia': vocal_user['nombre_usuario'],
                        'organizacionDestino': request['id_organizacion'],
                        'timestamp': datetime.now().isoformat()
                    },
                    'pre_conditions': [
                        f"Donación {donation['id']} tiene stock insuficiente",
                        "Sistema debe validar stock antes de transferir"
                    ],
                    'post_conditions': [
                        'Transferencia rechazada',
                        'Stock no modificado',
                        'Error registrado en logs'
                    ],
                    'test_assertions': [
                        'Error de stock insuficiente detectado',
                        'Transferencia no ejecutada',
                        'Stock original preservado'
                    ],
                    'expected_external_response': False,
                    'expected_error': 'InsufficientStockError',
                    'timeout_seconds': 15
                })
        
        return scenarios
    
    def generate_request_cancellation_scenarios(self) -> List[Dict]:
        """Generate request cancellation scenarios"""
        logger.info("Generating request cancellation scenarios")
        
        scenarios = []
        vocal_user = self._get_user_by_role('VOCAL')[0]
        
        # Get our own active requests
        own_requests = self.data['network']['own_requests']
        active_own_requests = [req for req in own_requests if req['activa']]
        
        if active_own_requests:
            request = active_own_requests[0]
            
            scenarios.append({
                'scenario_name': 'Cancelación de Solicitud Propia',
                'topic': self.kafka_topics['baja_solicitud_donaciones'],
                'message_key': f"{self.organization_id}-cancel-{request['id_solicitud']}",
                'message': {
                    'idOrganizacion': self.organization_id,
                    'idSolicitud': request['id_solicitud'],
                    'motivo': 'Necesidad cubierta por otra fuente',
                    'usuarioCancelacion': vocal_user['nombre_usuario'],
                    'timestamp': datetime.now().isoformat()
                },
                'pre_conditions': [
                    f"Solicitud {request['id_solicitud']} debe estar activa",
                    f"Usuario {vocal_user['nombre_usuario']} debe tener permisos",
                    "Solicitud debe pertenecer a nuestra organización"
                ],
                'post_conditions': [
                    'Solicitud marcada como inactiva',
                    'Notificación enviada a red de ONGs',
                    'Auditoría de cancelación registrada'
                ],
                'test_assertions': [
                    'Estado de solicitud actualizado',
                    'Motivo de cancelación registrado',
                    'Timestamp de cancelación válido'
                ],
                'expected_external_response': True,
                'timeout_seconds': 30
            })
        
        return scenarios
    
    def generate_external_event_scenarios(self) -> List[Dict]:
        """Generate external event publication scenarios"""
        logger.info("Generating external event scenarios")
        
        scenarios = []
        coordinador_user = self._get_user_by_role('COORDINADOR')[0]
        
        # Get future events to publish
        future_events = self.data['events']['future']
        
        if future_events:
            event = future_events[0]
            
            scenarios.append({
                'scenario_name': 'Publicación de Evento Solidario',
                'topic': self.kafka_topics['eventos_solidarios'],
                'message_key': f"{self.organization_id}-event-{event['id']}",
                'message': {
                    'idOrganizacion': self.organization_id,
                    'idEvento': f"ev-{event['id']}",
                    'nombre': event['nombre'],
                    'descripcion': event['descripcion'],
                    'fechaHora': event['fecha_hora'],
                    'ubicacion': 'Sede Central - Calle Solidaridad 123',
                    'capacidadMaxima': 50,
                    'tipoParticipacion': 'VOLUNTARIOS',
                    'requisitos': 'Mayor de edad, disponibilidad de 4 horas',
                    'contacto': {
                        'responsable': coordinador_user['nombre_usuario'],
                        'email': coordinador_user['email'],
                        'telefono': coordinador_user['telefono']
                    },
                    'timestamp': datetime.now().isoformat()
                },
                'pre_conditions': [
                    f"Evento {event['id']} debe ser futuro",
                    f"Usuario {coordinador_user['nombre_usuario']} debe tener rol COORDINADOR",
                    "Evento debe estar activo"
                ],
                'post_conditions': [
                    'Evento publicado en red inter-ONG',
                    'Otras ONGs pueden ver el evento',
                    'Voluntarios externos pueden adherirse'
                ],
                'test_assertions': [
                    'Fecha del evento es futura',
                    'Datos de contacto incluidos',
                    'Capacidad máxima especificada'
                ],
                'expected_external_response': True,
                'timeout_seconds': 30
            })
        
        if len(future_events) > 1:
            event = future_events[1]
            
            scenarios.append({
                'scenario_name': 'Evento con Requisitos Específicos',
                'topic': self.kafka_topics['eventos_solidarios'],
                'message_key': f"{self.organization_id}-special-event-{event['id']}",
                'message': {
                    'idOrganizacion': self.organization_id,
                    'idEvento': f"ev-special-{event['id']}",
                    'nombre': event['nombre'],
                    'descripcion': event['descripcion'],
                    'fechaHora': event['fecha_hora'],
                    'ubicacion': 'Centro Comunitario - Av. Esperanza 456',
                    'capacidadMaxima': 30,
                    'tipoParticipacion': 'COORDINADORES_Y_VOLUNTARIOS',
                    'requisitos': 'Experiencia previa en eventos solidarios, certificado de antecedentes',
                    'materialesNecesarios': ['Identificación', 'Ropa cómoda', 'Botiquín personal'],
                    'contacto': {
                        'responsable': coordinador_user['nombre_usuario'],
                        'email': coordinador_user['email'],
                        'telefono': coordinador_user['telefono']
                    },
                    'timestamp': datetime.now().isoformat()
                },
                'pre_conditions': [
                    'Evento con requisitos especiales definidos',
                    'Capacidad limitada configurada'
                ],
                'post_conditions': [
                    'Evento con requisitos publicado',
                    'Filtros de participación aplicados'
                ],
                'test_assertions': [
                    'Requisitos específicos incluidos',
                    'Materiales necesarios listados',
                    'Tipo de participación especificado'
                ],
                'expected_external_response': True,
                'timeout_seconds': 30
            })
        
        return scenarios
    
    def generate_event_cancellation_scenarios(self) -> List[Dict]:
        """Generate event cancellation scenarios"""
        logger.info("Generating event cancellation scenarios")
        
        scenarios = []
        coordinador_user = self._get_user_by_role('COORDINADOR')[0]
        
        # Get future events that could be cancelled
        future_events = self.data['events']['future']
        
        if future_events:
            event = future_events[0]
            
            scenarios.append({
                'scenario_name': 'Cancelación de Evento Solidario',
                'topic': self.kafka_topics['baja_evento_solidario'],
                'message_key': f"{self.organization_id}-cancel-event-{event['id']}",
                'message': {
                    'idOrganizacion': self.organization_id,
                    'idEvento': f"ev-{event['id']}",
                    'motivo': 'Condiciones climáticas adversas',
                    'usuarioCancelacion': coordinador_user['nombre_usuario'],
                    'fechaCancelacion': datetime.now().isoformat(),
                    'mensaje': 'El evento ha sido cancelado por razones de seguridad. Se reprogramará próximamente.',
                    'timestamp': datetime.now().isoformat()
                },
                'pre_conditions': [
                    f"Evento {event['id']} debe estar activo",
                    f"Usuario {coordinador_user['nombre_usuario']} debe tener permisos",
                    "Evento debe ser futuro"
                ],
                'post_conditions': [
                    'Evento marcado como cancelado',
                    'Notificación enviada a red de ONGs',
                    'Participantes externos notificados',
                    'Auditoría de cancelación registrada'
                ],
                'test_assertions': [
                    'Motivo de cancelación incluido',
                    'Mensaje explicativo presente',
                    'Timestamp de cancelación válido'
                ],
                'expected_external_response': True,
                'timeout_seconds': 30
            })
        
        return scenarios
    
    def generate_event_adhesion_scenarios(self) -> List[Dict]:
        """Generate event adhesion scenarios for external events"""
        logger.info("Generating event adhesion scenarios")
        
        scenarios = []
        voluntario_user = self._get_user_by_role('VOLUNTARIO')[0]
        
        # Get external events available for adhesion
        external_events = self.data['network']['external_events']
        future_external_events = [e for e in external_events if e['activo'] and 
                                datetime.fromisoformat(e['fecha_hora']) > datetime.now()]
        
        if future_external_events:
            event = future_external_events[0]
            
            scenarios.append({
                'scenario_name': 'Adhesión a Evento Externo - Voluntario',
                'topic': f"{self.kafka_topics['adhesion_evento']}/{event['id_organizacion']}",
                'message_key': f"{self.organization_id}-adhesion-{event['id_evento']}",
                'message': {
                    'idOrganizacion': self.organization_id,
                    'idEvento': event['id_evento'],
                    'organizacionEvento': event['id_organizacion'],
                    'participante': {
                        'id': voluntario_user['id'],
                        'nombreUsuario': voluntario_user['nombre_usuario'],
                        'nombre': voluntario_user['nombre'],
                        'apellido': voluntario_user['apellido'],
                        'email': voluntario_user['email'],
                        'telefono': voluntario_user['telefono'],
                        'rol': voluntario_user['rol']
                    },
                    'mensaje': f"Voluntario {voluntario_user['nombre']} {voluntario_user['apellido']} se adhiere al evento",
                    'timestamp': datetime.now().isoformat()
                },
                'pre_conditions': [
                    f"Evento {event['id_evento']} debe estar activo",
                    f"Usuario {voluntario_user['nombre_usuario']} debe tener rol VOLUNTARIO",
                    "Evento debe ser futuro",
                    f"Organización {event['id_organizacion']} debe estar activa"
                ],
                'post_conditions': [
                    'Adhesión registrada en adhesiones_eventos_externos',
                    'Notificación enviada a organización del evento',
                    'Participante agregado a lista del evento'
                ],
                'test_assertions': [
                    'Datos completos del participante incluidos',
                    'Mensaje enviado al topic correcto',
                    'Información de contacto presente'
                ],
                'expected_external_response': True,
                'timeout_seconds': 30
            })
        
        # Scenario with authorization error (non-volunteer trying to join)
        if future_external_events and len(self._get_user_by_role('VOCAL')) > 0:
            event = future_external_events[0]
            vocal_user = self._get_user_by_role('VOCAL')[0]
            
            scenarios.append({
                'scenario_name': 'Adhesión a Evento Externo - Error de Autorización',
                'topic': f"{self.kafka_topics['adhesion_evento']}/{event['id_organizacion']}",
                'message_key': f"{self.organization_id}-adhesion-error-{event['id_evento']}",
                'message': {
                    'idOrganizacion': self.organization_id,
                    'idEvento': event['id_evento'],
                    'organizacionEvento': event['id_organizacion'],
                    'participante': {
                        'id': vocal_user['id'],
                        'nombreUsuario': vocal_user['nombre_usuario'],
                        'rol': vocal_user['rol']
                    },
                    'timestamp': datetime.now().isoformat()
                },
                'pre_conditions': [
                    f"Usuario {vocal_user['nombre_usuario']} tiene rol {vocal_user['rol']}",
                    "Solo VOLUNTARIOS pueden adherirse a eventos externos"
                ],
                'post_conditions': [
                    'Adhesión rechazada por falta de permisos',
                    'Error registrado en logs'
                ],
                'test_assertions': [
                    'Error de autorización detectado',
                    'Adhesión no procesada',
                    'Mensaje de error apropiado'
                ],
                'expected_external_response': False,
                'expected_error': 'AuthorizationError',
                'timeout_seconds': 15
            })
        
        return scenarios
    
    # Helper methods
    def _get_user_by_role(self, role: str) -> List[Dict]:
        """Get users by role from extracted data"""
        return self.data['users'].get(role, [])
    
    def _get_high_stock_donations(self, categoria: str = None) -> List[Dict]:
        """Get donations with high stock (>50)"""
        high_stock = []
        inventory = self.data['inventory']
        
        if categoria:
            if categoria in inventory and 'high_stock' in inventory[categoria]:
                high_stock.extend(inventory[categoria]['high_stock'])
        else:
            for cat_data in inventory.values():
                if 'high_stock' in cat_data:
                    high_stock.extend(cat_data['high_stock'])
        
        return high_stock
    
    def _get_zero_stock_donations(self) -> List[Dict]:
        """Get donations with zero stock"""
        zero_stock = []
        inventory = self.data['inventory']
        
        for cat_data in inventory.values():
            if 'zero_stock' in cat_data:
                zero_stock.extend(cat_data['zero_stock'])
        
        return zero_stock
    
    def _get_donations_by_category(self, categoria: str) -> List[Dict]:
        """Get all donations by category"""
        inventory = self.data['inventory']
        if categoria in inventory and 'all' in inventory[categoria]:
            return inventory[categoria]['all']
        return []
    
    def _get_low_stock_donations(self, categoria: str = None) -> List[Dict]:
        """Get donations with low stock (1-9)"""
        low_stock = []
        inventory = self.data['inventory']
        
        if categoria:
            if categoria in inventory and 'low_stock' in inventory[categoria]:
                low_stock.extend(inventory[categoria]['low_stock'])
        else:
            for cat_data in inventory.values():
                if 'low_stock' in cat_data:
                    low_stock.extend(cat_data['low_stock'])
        
        return low_stock
    
    def _generate_id(self) -> str:
        """Generate a unique ID for messages"""
        return str(uuid.uuid4())[:8]
    
    def save_scenarios_to_files(self, scenarios: Dict[str, List[Dict]], output_dir: str = "kafka_scenarios"):
        """Save generated scenarios to JSON files for testing"""
        logger.info(f"Saving Kafka scenarios to {output_dir}")
        
        os.makedirs(output_dir, exist_ok=True)
        
        for topic, topic_scenarios in scenarios.items():
            filename = f"{topic.replace('-', '_')}_scenarios.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'topic': topic,
                    'total_scenarios': len(topic_scenarios),
                    'scenarios': topic_scenarios
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(topic_scenarios)} scenarios for topic '{topic}' to {filepath}")
        
        return output_dir
    
    def generate_kafka_test_summary(self, scenarios: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Generate a summary of all Kafka test scenarios"""
        summary = {
            'generation_timestamp': datetime.now().isoformat(),
            'organization_id': self.organization_id,
            'total_topics': len(scenarios),
            'total_scenarios': sum(len(topic_scenarios) for topic_scenarios in scenarios.values()),
            'topics_summary': {},
            'scenario_types': {
                'success': 0,
                'error': 0,
                'validation': 0,
                'authorization': 0
            }
        }
        
        for topic, topic_scenarios in scenarios.items():
            summary['topics_summary'][topic] = {
                'scenario_count': len(topic_scenarios),
                'scenarios': [s['scenario_name'] for s in topic_scenarios]
            }
            
            # Count scenario types
            for scenario in topic_scenarios:
                if scenario.get('expected_external_response', True):
                    summary['scenario_types']['success'] += 1
                elif 'AuthorizationError' in scenario.get('expected_error', ''):
                    summary['scenario_types']['authorization'] += 1
                elif 'ValidationError' in scenario.get('expected_error', ''):
                    summary['scenario_types']['validation'] += 1
                else:
                    summary['scenario_types']['error'] += 1
        
        return summary
    
    def validate_scenarios(self, scenarios: Dict[str, List[Dict]]) -> List[str]:
        """Validate generated scenarios for completeness and consistency"""
        logger.info("Validating generated Kafka scenarios")
        
        errors = []
        required_fields = ['scenario_name', 'topic', 'message_key', 'message', 'pre_conditions', 
                          'post_conditions', 'test_assertions', 'timeout_seconds']
        
        for topic, topic_scenarios in scenarios.items():
            if not topic_scenarios:
                errors.append(f"No scenarios generated for topic: {topic}")
                continue
            
            for i, scenario in enumerate(topic_scenarios):
                scenario_id = f"{topic}[{i}]"
                
                # Check required fields
                for field in required_fields:
                    if field not in scenario:
                        errors.append(f"Missing field '{field}' in scenario {scenario_id}")
                
                # Validate message structure
                message = scenario.get('message', {})
                if not message.get('idOrganizacion'):
                    errors.append(f"Missing idOrganizacion in scenario {scenario_id}")
                
                if not message.get('timestamp'):
                    errors.append(f"Missing timestamp in scenario {scenario_id}")
                
                # Validate timeout
                timeout = scenario.get('timeout_seconds', 0)
                if not isinstance(timeout, int) or timeout <= 0:
                    errors.append(f"Invalid timeout_seconds in scenario {scenario_id}")
        
        if errors:
            logger.warning(f"Found {len(errors)} validation errors in Kafka scenarios")
        else:
            logger.info("All Kafka scenarios passed validation")
        
        return errors

def main():
    """Main function for testing the Kafka generator"""
    # This would normally be called with real extracted data
    # For testing purposes, we'll create a minimal data structure
    
    sample_data = {
        'users': {
            'VOCAL': [{'id': 2, 'nombre_usuario': 'test_vocal', 'nombre': 'María', 'apellido': 'Vocal', 
                      'email': 'vocal@test.com', 'telefono': '2222222222', 'rol': 'VOCAL'}],
            'COORDINADOR': [{'id': 3, 'nombre_usuario': 'test_coordinador', 'nombre': 'Carlos', 'apellido': 'Coordinador',
                           'email': 'coordinador@test.com', 'telefono': '3333333333', 'rol': 'COORDINADOR'}],
            'VOLUNTARIO': [{'id': 4, 'nombre_usuario': 'test_voluntario', 'nombre': 'Ana', 'apellido': 'Voluntario',
                          'email': 'voluntario@test.com', 'telefono': '4444444444', 'rol': 'VOLUNTARIO'}]
        },
        'inventory': {
            'ALIMENTOS': {
                'high_stock': [{'id': 101, 'categoria': 'ALIMENTOS', 'descripcion': 'Arroz 1kg', 'cantidad': 100}],
                'zero_stock': [{'id': 104, 'categoria': 'ALIMENTOS', 'descripcion': 'Cuadernos', 'cantidad': 0}],
                'all': [{'id': 101, 'categoria': 'ALIMENTOS', 'descripcion': 'Arroz 1kg', 'cantidad': 100}]
            }
        },
        'events': {
            'future': [{'id': 201, 'nombre': 'Evento Test Futuro', 'descripcion': 'Evento para testing', 
                       'fecha_hora': (datetime.now() + timedelta(days=7)).isoformat()}]
        },
        'network': {
            'external_requests': [{'id_organizacion': 'ong-corazon-solidario', 'id_solicitud': 'sol-001', 
                                 'categoria': 'ALIMENTOS', 'activa': True}],
            'external_events': [{'id_organizacion': 'ong-corazon-solidario', 'id_evento': 'ev-ext-001',
                               'nombre': 'Evento Externo', 'descripcion': 'Evento de prueba', 
                               'fecha_hora': (datetime.now() + timedelta(days=10)).isoformat(), 'activo': True}],
            'own_requests': [{'id_solicitud': 'req-001', 'activa': True}]
        }
    }
    
    generator = KafkaTestGenerator(sample_data)
    scenarios = generator.generate_all_kafka_scenarios()
    
    # Validate scenarios
    errors = generator.validate_scenarios(scenarios)
    if errors:
        print("Validation errors found:")
        for error in errors:
            print(f"  - {error}")
    
    # Generate summary
    summary = generator.generate_kafka_test_summary(scenarios)
    print(f"\nGenerated {summary['total_scenarios']} scenarios across {summary['total_topics']} topics")
    
    # Save scenarios
    generator.save_scenarios_to_files(scenarios)
    
    return scenarios

if __name__ == "__main__":
    main()