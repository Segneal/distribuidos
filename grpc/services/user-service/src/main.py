#!/usr/bin/env python3
"""
Main entry point for User Service
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Add current directory to Python path
sys.path.append(os.path.dirname(__file__))

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main function to start the User Service"""
    logger.info("Starting User Service...")
    
    try:
        from service.server import serve
        serve()
    except KeyboardInterrupt:
        logger.info("User Service stopped by user")
    except Exception as e:
        logger.error(f"Error starting User Service: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()