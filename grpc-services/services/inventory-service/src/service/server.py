"""
gRPC Server for Inventory Service
"""
import os
import sys
import grpc
import logging
import signal
from concurrent import futures
from dotenv import load_dotenv

# Add current directory to Python path
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import generated gRPC code
import inventory_pb2_grpc
from .inventario_service import InventarioService
from config.database import get_db_config
from kafka_client_module.kafka_client import kafka_client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def serve():
    """Start gRPC server"""
    # Test database connection
    if not get_db_config().test_connection():
        logger.error("Database connection failed. Exiting...")
        sys.exit(1)
    
    # Initialize Kafka client
    try:
        kafka_client.start()
        logger.info("Kafka client initialized successfully")
    except Exception as e:
        logger.warning(f"Kafka initialization failed: {e}. Service will continue without Kafka functionality.")
    
    # Create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add service to server
    inventory_pb2_grpc.add_InventarioServiceServicer_to_server(InventarioService(), server)
    
    # Configure server address
    port = os.getenv('GRPC_PORT', '50052')
    server_address = f'[::]:{port}'
    server.add_insecure_port(server_address)
    
    # Setup graceful shutdown
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal. Stopping services...")
        kafka_client.stop()
        server.stop(0)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start server
    server.start()
    logger.info(f"Inventory Service gRPC server started on {server_address}")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down Inventory Service gRPC server...")
        kafka_client.stop()
        server.stop(0)

if __name__ == '__main__':
    serve()
