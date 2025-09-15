"""
gRPC Server for User Service
"""
import os
import sys
import grpc
import logging
from concurrent import futures
from dotenv import load_dotenv

# Import generated gRPC code
import user_pb2_grpc
from usuario_service import UsuarioServiceImpl
from config.database import get_db_config
from config.email import email_config

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
    
    # Test email configuration
    if not email_config.test_connection():
        logger.warning("Email configuration test failed. Email functionality may not work.")
    
    # Create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add service to server
    user_pb2_grpc.add_UsuarioServiceServicer_to_server(UsuarioServiceImpl(), server)
    
    # Configure server address
    port = os.getenv('GRPC_PORT', '50051')
    server_address = f'[::]:{port}'
    server.add_insecure_port(server_address)
    
    # Start server
    server.start()
    logger.info(f"User Service gRPC server started on {server_address}")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down User Service gRPC server...")
        server.stop(0)

if __name__ == '__main__':
    serve()