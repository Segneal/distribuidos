"""
Main entry point for Inventory Service
"""
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service.server import serve

if __name__ == '__main__':
    serve()