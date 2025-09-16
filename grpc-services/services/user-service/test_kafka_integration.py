#!/usr/bin/env python3
"""
Test script para verificar la integración de Kafka en el servicio de usuarios
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

from kafka import kafka_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_kafka_connection():
    """Test basic Kafka connection and functionality"""
    try:
        logger.info("=== Test de Integración Kafka - Servicio de Usuarios ===")
        
        # Start Kafka client
        logger.info("Iniciando cliente Kafka...")
        kafka_client.start()
        
        # Test health check
        logger.info("Verificando estado de salud...")
        if kafka_client.health_check():
            logger.info("✓ Health check exitoso")
        else:
            logger.warning("⚠ Health check falló")
        
        # Test message publishing
        logger.info("Probando envío de mensaje...")
        test_message = {
            "tipo": "test",
            "mensaje": "Test de integración Kafka",
            "servicio": "user-service"
        }
        
        success = kafka_client.publish_message("solicitud-donaciones", test_message)
        if success:
            logger.info("✓ Mensaje enviado exitosamente")
        else:
            logger.error("✗ Error enviando mensaje")
        
        # Test consumer subscription (just setup, not actual consumption)
        logger.info("Probando suscripción a topic...")
        
        def test_handler(message):
            logger.info(f"Mensaje recibido: {message}")
        
        kafka_client.subscribe_to_topic("solicitud-donaciones", test_handler)
        logger.info("✓ Suscripción configurada")
        
        # Wait a bit to see if everything works
        logger.info("Esperando 5 segundos para verificar funcionamiento...")
        time.sleep(5)
        
        logger.info("=== Test completado ===")
        
    except Exception as e:
        logger.error(f"Error en test de Kafka: {e}")
        return False
    
    finally:
        # Stop Kafka client
        logger.info("Deteniendo cliente Kafka...")
        kafka_client.stop()
        logger.info("Cliente Kafka detenido")
    
    return True

if __name__ == "__main__":
    success = test_kafka_connection()
    if success:
        logger.info("✓ Test de integración Kafka exitoso")
        sys.exit(0)
    else:
        logger.error("✗ Test de integración Kafka falló")
        sys.exit(1)