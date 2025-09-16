"""
Database configuration and connection management for Inventory Service
"""
import os
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConfig:
    """Database configuration class"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '3306'))
        self.database = os.getenv('DB_NAME', 'ong_sistema')
        self.user = os.getenv('DB_USER', 'ong_user')
        self.password = os.getenv('DB_PASSWORD', 'ong_password')
        self.pool_name = 'inventory_service_pool'
        self.pool_size = int(os.getenv('DB_POOL_SIZE', '5'))
        
        # Create connection pool
        self.connection_pool = self._create_pool()
    
    def _create_pool(self):
        """Create MySQL connection pool"""
        try:
            pool_config = {
                'pool_name': self.pool_name,
                'pool_size': self.pool_size,
                'pool_reset_session': True,
                'host': self.host,
                'port': self.port,
                'database': self.database,
                'user': self.user,
                'password': self.password,
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci',
                'autocommit': False
            }
            
            return pooling.MySQLConnectionPool(**pool_config)
        except mysql.connector.Error as err:
            print(f"Error creating connection pool: {err}")
            raise
    
    def get_connection(self):
        """Get connection from pool"""
        try:
            return self.connection_pool.get_connection()
        except mysql.connector.Error as err:
            print(f"Error getting connection from pool: {err}")
            raise
    
    def test_connection(self):
        """Test database connection"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result[0] == 1
        except mysql.connector.Error as err:
            print(f"Database connection test failed: {err}")
            return False

# Global database configuration instance (lazy initialization)
db_config = None

def get_db_config():
    """Get database configuration instance (lazy initialization)"""
    global db_config
    if db_config is None:
        db_config = DatabaseConfig()
    return db_config