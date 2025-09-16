"""
Database configuration for Events Service
"""
import os
import mysql.connector
from mysql.connector import Error
from typing import Optional

class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '3306'))
        self.database = os.getenv('DB_NAME', 'ong_sistema')
        self.user = os.getenv('DB_USER', 'ong_user')
        self.password = os.getenv('DB_PASSWORD', 'ong_password')
        self.connection_pool = None
        
    def create_connection_pool(self, pool_name: str = "events_pool", pool_size: int = 5):
        """Create a connection pool for database connections"""
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name=pool_name,
                pool_size=pool_size,
                pool_reset_session=True,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                autocommit=False,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            print(f"Connection pool '{pool_name}' created successfully")
        except Error as e:
            print(f"Error creating connection pool: {e}")
            raise
    
    def get_connection(self):
        """Get a connection from the pool"""
        if not self.connection_pool:
            self.create_connection_pool()
        
        try:
            return self.connection_pool.get_connection()
        except Error as e:
            print(f"Error getting connection from pool: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            connection = self.get_connection()
            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                connection.close()
                return result[0] == 1
        except Error as e:
            print(f"Database connection test failed: {e}")
            return False
        return False

# Global database configuration instance
db_config = DatabaseConfig()