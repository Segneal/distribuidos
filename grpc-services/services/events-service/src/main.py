"""
Events Service gRPC Server
"""
import os
import sys
import logging
import signal
import time
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import grpc AFTER setting up the path to avoid conflicts
import grpc
from concurrent import futures

# Load environment variables
load_dotenv()

import events_pb2_grpc
from service.evento_service import EventoService
from config.database import db_config
from kafka_client_module.kafka_client import kafka_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EventsServer:
    """Events gRPC Server"""
    
    def __init__(self, port: int = 50053):
        self.port = port
        self.server = None
        
    def start_server(self):
        """Start the gRPC server"""
        try:
            # Test database connection
            if not db_config.test_connection():
                logger.error("No se pudo conectar a la base de datos")
                return False
            
            logger.info("Conexión a base de datos establecida")
            
            # Initialize Kafka client
            try:
                kafka_client.start()
                logger.info("Kafka client initialized successfully")
            except Exception as e:
                logger.warning(f"Kafka initialization failed: {e}. Service will continue without Kafka functionality.")
            
            # Create gRPC server
            self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            
            # Add service to server
            evento_service = EventoService()
            events_pb2_grpc.add_EventoServiceServicer_to_server(evento_service, self.server)
            
            # Configure server address
            listen_addr = f'[::]:{self.port}'
            self.server.add_insecure_port(listen_addr)
            
            # Start server
            self.server.start()
            logger.info(f"Servidor de Eventos iniciado en puerto {self.port}")
            logger.info(f"Escuchando en {listen_addr}")
            
            return True
            
        except Exception as e:
            logger.error(f"No se pudo iniciar el servidor: {e}")
            return False
    
    def stop_server(self):
        """Stop the gRPC server"""
        if self.server:
            logger.info("Deteniendo servidor de eventos...")
            kafka_client.stop()
            self.server.stop(grace=5)
            logger.info("Servidor detenido")
    
    def wait_for_termination(self):
        """Wait for server termination"""
        if self.server:
            try:
                self.server.wait_for_termination()
            except KeyboardInterrupt:
                logger.info("Interrupción recibida, deteniendo servidor...")
                self.stop_server()

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Señal {signum} recibida, iniciando apagado...")
    sys.exit(0)

def main():
    """Main function"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Get port from environment
    port = int(os.getenv('EVENTS_SERVICE_PORT', '50053'))
    
    logger.info("=== Servicio de Eventos - Sistema ONG ===")
    logger.info(f"Puerto: {port}")
    logger.info(f"Base de datos: {os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}")
    logger.info("==========================================")
    
    # Create and start server
    server = EventsServer(port)
    
    if server.start_server():
        logger.info("Servidor listo para recibir peticiones...")
        logger.info("Presiona Ctrl+C para detener")
        
        try:
            server.wait_for_termination()
        except KeyboardInterrupt:
            pass
        finally:
            server.stop_server()
    else:
        logger.error("No se pudo iniciar el servidor")
        sys.exit(1)

if __name__ == '__main__':
    main()