"""
Cliente Kafka para el servicio de eventos
Maneja productores y consumidores para comunicación entre ONGs
"""

import json
import logging
import os
import threading
import time
from typing import Dict, Any, Callable, Optional
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError, NoBrokersAvailable

logger = logging.getLogger(__name__)

class KafkaClient:
    """Cliente Kafka para manejo de productores y consumidores"""
    
    def __init__(self, bootstrap_servers: str = None):
        self.bootstrap_servers = bootstrap_servers or os.getenv('KAFKA_BROKERS', 'localhost:9092')
        self.organization_id = os.getenv('ORGANIZATION_ID', 'ong-empuje-comunitario')
        self.producer = None
        self.consumers = {}
        self.consumer_threads = {}
        self.running = False
        
        # Configuración de reconexión
        self.max_retries = 5
        self.retry_delay = 5  # segundos
        
        logger.info(f"Inicializando KafkaClient con brokers: {self.bootstrap_servers}")
    
    def _create_producer(self) -> KafkaProducer:
        """Crea un productor Kafka con configuración de reconexión"""
        try:
            producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Esperar confirmación de todos los replicas
                retries=3,
                retry_backoff_ms=1000,
                request_timeout_ms=30000,
                api_version=(0, 10, 1)
            )
            logger.info("Productor Kafka creado exitosamente")
            return producer
        except Exception as e:
            logger.error(f"Error creando productor Kafka: {e}")
            raise
    
    def _create_consumer(self, topics: list, group_id: str) -> KafkaConsumer:
        """Crea un consumidor Kafka con configuración de reconexión"""
        try:
            consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                auto_offset_reset='latest',  # Solo mensajes nuevos
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000,
                api_version=(0, 10, 1)
            )
            logger.info(f"Consumidor Kafka creado para topics: {topics}, group: {group_id}")
            return consumer
        except Exception as e:
            logger.error(f"Error creando consumidor Kafka: {e}")
            raise
    
    def start(self):
        """Inicia el cliente Kafka"""
        self.running = True
        
        # Crear productor con reintentos
        for attempt in range(self.max_retries):
            try:
                self.producer = self._create_producer()
                break
            except Exception as e:
                logger.warning(f"Intento {attempt + 1} fallido para crear productor: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error("No se pudo crear el productor después de todos los intentos")
                    raise
        
        logger.info("Cliente Kafka iniciado exitosamente")
        
        # Configurar consumidores para eventos externos
        self.setup_external_events_consumers()
    
    def setup_external_events_consumers(self):
        """Configura consumidores para eventos externos"""
        try:
            # Consumidor para eventos solidarios externos
            self.subscribe_to_topic(
                'eventos-solidarios',
                self.handle_external_event,
                f"{self.organization_id}-eventos-externos-consumer"
            )
            
            # Consumidor para bajas de eventos externos
            self.subscribe_to_topic(
                'baja-evento-solidario',
                self.handle_external_event_cancellation,
                f"{self.organization_id}-baja-eventos-consumer"
            )
            
            logger.info("Consumidores de eventos externos configurados")
            
        except Exception as e:
            logger.error(f"Error configurando consumidores de eventos externos: {e}")
    
    def publish_external_event(self, evento_data: Dict[str, Any]) -> bool:
        """
        Publica un evento solidario en la red de ONGs
        
        Args:
            evento_data: Datos del evento a publicar
            
        Returns:
            bool: True si el evento fue publicado exitosamente
        """
        try:
            mensaje = {
                'idEvento': str(evento_data.get('id')),
                'nombre': evento_data.get('nombre'),
                'descripcion': evento_data.get('descripcion'),
                'fechaHora': evento_data.get('fecha_hora')
            }
            
            return self.publish_message('eventos-solidarios', mensaje, str(evento_data.get('id')))
            
        except Exception as e:
            logger.error(f"Error publicando evento externo: {e}")
            return False
    
    def publish_event_cancellation(self, evento_id: str) -> bool:
        """
        Publica la baja de un evento solidario
        
        Args:
            evento_id: ID del evento a dar de baja
            
        Returns:
            bool: True si la baja fue publicada exitosamente
        """
        try:
            mensaje = {
                'idEvento': str(evento_id),
                'fechaBaja': time.time()
            }
            
            return self.publish_message('baja-evento-solidario', mensaje, str(evento_id))
            
        except Exception as e:
            logger.error(f"Error publicando baja de evento: {e}")
            return False
    
    def handle_external_event(self, message: Dict[str, Any]):
        """
        Maneja eventos solidarios externos recibidos
        
        Args:
            message: Mensaje del evento recibido
        """
        try:
            # Filtrar eventos propios
            if message.get('idOrganizacion') == self.organization_id:
                logger.debug("Ignorando evento propio")
                return
            
            logger.info(f"Procesando evento externo: {message}")
            
            # Importar aquí para evitar dependencias circulares
            from ..repositories.evento_repository import EventoRepository
            
            evento_repo = EventoRepository()
            evento_repo.guardar_evento_externo(message)
            
        except Exception as e:
            logger.error(f"Error procesando evento externo: {e}")
    
    def handle_external_event_cancellation(self, message: Dict[str, Any]):
        """
        Maneja bajas de eventos externos
        
        Args:
            message: Mensaje de baja del evento
        """
        try:
            # Filtrar bajas propias
            if message.get('idOrganizacion') == self.organization_id:
                logger.debug("Ignorando baja de evento propio")
                return
            
            logger.info(f"Procesando baja de evento externo: {message}")
            
            # Importar aquí para evitar dependencias circulares
            from ..repositories.evento_repository import EventoRepository
            
            evento_repo = EventoRepository()
            evento_repo.marcar_evento_externo_inactivo(
                message.get('idOrganizacion'),
                message.get('idEvento')
            )
            
        except Exception as e:
            logger.error(f"Error procesando baja de evento externo: {e}")
    
    def stop(self):
        """Detiene el cliente Kafka y todos los consumidores"""
        self.running = False
        
        # Detener todos los consumidores
        for topic, thread in self.consumer_threads.items():
            logger.info(f"Deteniendo consumidor para topic: {topic}")
            thread.join(timeout=5)
        
        # Cerrar consumidores
        for consumer in self.consumers.values():
            try:
                consumer.close()
            except Exception as e:
                logger.warning(f"Error cerrando consumidor: {e}")
        
        # Cerrar productor
        if self.producer:
            try:
                self.producer.close()
            except Exception as e:
                logger.warning(f"Error cerrando productor: {e}")
        
        logger.info("Cliente Kafka detenido")
    
    def publish_message(self, topic: str, message: Dict[str, Any], key: str = None) -> bool:
        """
        Publica un mensaje en un topic específico
        
        Args:
            topic: Nombre del topic
            message: Mensaje a enviar (será serializado a JSON)
            key: Clave del mensaje (opcional)
            
        Returns:
            bool: True si el mensaje fue enviado exitosamente
        """
        if not self.producer:
            logger.error("Productor no está disponible")
            return False
        
        try:
            # Agregar metadatos del mensaje
            enriched_message = {
                **message,
                'idOrganizacion': self.organization_id,
                'timestamp': time.time()
            }
            
            # Enviar mensaje
            future = self.producer.send(topic, value=enriched_message, key=key)
            record_metadata = future.get(timeout=10)
            
            logger.info(f"Mensaje enviado a topic '{topic}': partition={record_metadata.partition}, offset={record_metadata.offset}")
            return True
            
        except KafkaError as e:
            logger.error(f"Error de Kafka enviando mensaje a topic '{topic}': {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado enviando mensaje a topic '{topic}': {e}")
            return False
    
    def subscribe_to_topic(self, topic: str, handler: Callable[[Dict[str, Any]], None], group_id: str = None):
        """
        Se suscribe a un topic y procesa mensajes con el handler proporcionado
        
        Args:
            topic: Nombre del topic
            handler: Función que procesará cada mensaje recibido
            group_id: ID del grupo de consumidores (opcional)
        """
        if not group_id:
            group_id = f"{self.organization_id}-{topic}-consumer"
        
        def consumer_loop():
            consumer = None
            retry_count = 0
            
            while self.running and retry_count < self.max_retries:
                try:
                    # Crear consumidor
                    consumer = self._create_consumer([topic], group_id)
                    self.consumers[topic] = consumer
                    retry_count = 0  # Reset counter on successful connection
                    
                    logger.info(f"Iniciando consumo de topic: {topic}")
                    
                    # Procesar mensajes
                    for message in consumer:
                        if not self.running:
                            break
                        
                        try:
                            # Filtrar mensajes propios
                            if message.value and message.value.get('idOrganizacion') == self.organization_id:
                                logger.debug(f"Ignorando mensaje propio en topic '{topic}'")
                                continue
                            
                            # Procesar mensaje
                            handler(message.value)
                            
                        except Exception as e:
                            logger.error(f"Error procesando mensaje de topic '{topic}': {e}")
                            # Continuar procesando otros mensajes
                            continue
                
                except NoBrokersAvailable:
                    retry_count += 1
                    logger.warning(f"No hay brokers disponibles. Intento {retry_count}/{self.max_retries}")
                    if retry_count < self.max_retries:
                        time.sleep(self.retry_delay)
                    else:
                        logger.error(f"No se pudo conectar a Kafka después de {self.max_retries} intentos")
                        break
                
                except Exception as e:
                    retry_count += 1
                    logger.error(f"Error en consumidor de topic '{topic}': {e}")
                    if retry_count < self.max_retries:
                        time.sleep(self.retry_delay)
                    else:
                        logger.error(f"Consumidor de topic '{topic}' falló después de {self.max_retries} intentos")
                        break
                
                finally:
                    if consumer:
                        try:
                            consumer.close()
                        except Exception as e:
                            logger.warning(f"Error cerrando consumidor: {e}")
            
            logger.info(f"Consumidor de topic '{topic}' terminado")
        
        # Iniciar hilo del consumidor
        thread = threading.Thread(target=consumer_loop, daemon=True)
        thread.start()
        self.consumer_threads[topic] = thread
        
        logger.info(f"Suscripción a topic '{topic}' iniciada")
    
    def health_check(self) -> bool:
        """
        Verifica el estado de salud de la conexión Kafka
        
        Returns:
            bool: True si la conexión está saludable
        """
        try:
            if not self.producer:
                return False
            
            # Intentar obtener metadatos como health check
            metadata = self.producer.bootstrap_connected()
            return metadata
            
        except Exception as e:
            logger.warning(f"Health check falló: {e}")
            return False

# Instancia global del cliente Kafka
kafka_client = KafkaClient()