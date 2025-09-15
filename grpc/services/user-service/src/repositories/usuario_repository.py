"""
User Repository for database operations
"""
import logging
from datetime import datetime
from typing import List, Optional, Tuple
import mysql.connector
from mysql.connector import Error

from models.usuario import Usuario
from config.database import get_db_config

logger = logging.getLogger(__name__)

class UsuarioRepository:
    """Repository for user database operations"""
    
    def crear_usuario(self, usuario: Usuario) -> Optional[Usuario]:
        """Create new user in database"""
        connection = None
        cursor = None
        
        try:
            connection = get_db_config().get_connection()
            cursor = connection.cursor()
            
            # Check if username or email already exists
            cursor.execute(
                "SELECT id FROM usuarios WHERE nombre_usuario = %s OR email = %s",
                (usuario.nombre_usuario, usuario.email)
            )
            
            if cursor.fetchone():
                logger.error(f"User with username '{usuario.nombre_usuario}' or email '{usuario.email}' already exists")
                return None
            
            # Insert new user
            insert_query = """
                INSERT INTO usuarios (
                    nombre_usuario, nombre, apellido, telefono, clave_hash, 
                    email, rol, activo, usuario_alta
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                usuario.nombre_usuario,
                usuario.nombre,
                usuario.apellido,
                usuario.telefono,
                usuario.clave_hash,
                usuario.email,
                usuario.rol,
                usuario.activo,
                usuario.usuario_alta
            ))
            
            # Get the created user ID
            usuario_id = cursor.lastrowid
            connection.commit()
            
            # Fetch and return the created user
            return self.obtener_usuario_por_id(usuario_id)
            
        except Error as e:
            logger.error(f"Database error creating user: {e}")
            if connection:
                connection.rollback()
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating user: {e}")
            if connection:
                connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def obtener_usuario_por_id(self, usuario_id: int) -> Optional[Usuario]:
        """Get user by ID"""
        connection = None
        cursor = None
        
        try:
            connection = get_db_config().get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(
                "SELECT * FROM usuarios WHERE id = %s",
                (usuario_id,)
            )
            
            row = cursor.fetchone()
            if row:
                return self._row_to_usuario(row)
            return None
            
        except Error as e:
            logger.error(f"Database error getting user by ID: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting user by ID: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def obtener_usuario_por_identificador(self, identificador: str) -> Optional[Usuario]:
        """Get user by username or email"""
        connection = None
        cursor = None
        
        try:
            connection = get_db_config().get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(
                "SELECT * FROM usuarios WHERE (nombre_usuario = %s OR email = %s) AND activo = true",
                (identificador, identificador)
            )
            
            row = cursor.fetchone()
            if row:
                return self._row_to_usuario(row)
            return None
            
        except Error as e:
            logger.error(f"Database error getting user by identifier: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting user by identifier: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def listar_usuarios(self, pagina: int = 1, tamaño_pagina: int = 10, 
                       incluir_inactivos: bool = False) -> Tuple[List[Usuario], int]:
        """List users with pagination"""
        connection = None
        cursor = None
        
        try:
            connection = get_db_config().get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Build WHERE clause
            where_clause = "" if incluir_inactivos else "WHERE activo = true"
            
            # Get total count
            count_query = f"SELECT COUNT(*) as total FROM usuarios {where_clause}"
            cursor.execute(count_query)
            total = cursor.fetchone()['total']
            
            # Get paginated results
            offset = (pagina - 1) * tamaño_pagina
            list_query = f"""
                SELECT * FROM usuarios {where_clause}
                ORDER BY fecha_hora_alta DESC
                LIMIT %s OFFSET %s
            """
            
            cursor.execute(list_query, (tamaño_pagina, offset))
            rows = cursor.fetchall()
            
            usuarios = [self._row_to_usuario(row) for row in rows]
            return usuarios, total
            
        except Error as e:
            logger.error(f"Database error listing users: {e}")
            return [], 0
        except Exception as e:
            logger.error(f"Unexpected error listing users: {e}")
            return [], 0
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def actualizar_usuario(self, usuario: Usuario) -> Optional[Usuario]:
        """Update user in database"""
        connection = None
        cursor = None
        
        try:
            connection = get_db_config().get_connection()
            cursor = connection.cursor()
            
            # Check if username or email already exists for other users
            cursor.execute(
                "SELECT id FROM usuarios WHERE (nombre_usuario = %s OR email = %s) AND id != %s",
                (usuario.nombre_usuario, usuario.email, usuario.id)
            )
            
            if cursor.fetchone():
                logger.error(f"Username '{usuario.nombre_usuario}' or email '{usuario.email}' already exists for another user")
                return None
            
            # Update user
            update_query = """
                UPDATE usuarios SET
                    nombre_usuario = %s, nombre = %s, apellido = %s, telefono = %s,
                    email = %s, rol = %s, usuario_modificacion = %s,
                    fecha_hora_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            cursor.execute(update_query, (
                usuario.nombre_usuario,
                usuario.nombre,
                usuario.apellido,
                usuario.telefono,
                usuario.email,
                usuario.rol,
                usuario.usuario_modificacion,
                usuario.id
            ))
            
            if cursor.rowcount == 0:
                logger.error(f"No user found with ID {usuario.id}")
                return None
            
            connection.commit()
            
            # Return updated user
            return self.obtener_usuario_por_id(usuario.id)
            
        except Error as e:
            logger.error(f"Database error updating user: {e}")
            if connection:
                connection.rollback()
            return None
        except Exception as e:
            logger.error(f"Unexpected error updating user: {e}")
            if connection:
                connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def eliminar_usuario(self, usuario_id: int, usuario_eliminacion: str) -> bool:
        """Logical delete user"""
        connection = None
        cursor = None
        
        try:
            connection = get_db_config().get_connection()
            cursor = connection.cursor()
            
            # Update user to inactive
            update_query = """
                UPDATE usuarios SET
                    activo = false,
                    usuario_modificacion = %s,
                    fecha_hora_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s AND activo = true
            """
            
            cursor.execute(update_query, (usuario_eliminacion, usuario_id))
            
            if cursor.rowcount == 0:
                logger.error(f"No active user found with ID {usuario_id}")
                return False
            
            connection.commit()
            return True
            
        except Error as e:
            logger.error(f"Database error deleting user: {e}")
            if connection:
                connection.rollback()
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting user: {e}")
            if connection:
                connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def _row_to_usuario(self, row: dict) -> Usuario:
        """Convert database row to Usuario object"""
        return Usuario(
            id=row['id'],
            nombre_usuario=row['nombre_usuario'],
            nombre=row['nombre'],
            apellido=row['apellido'],
            telefono=row['telefono'],
            email=row['email'],
            rol=row['rol'],
            activo=row['activo'],
            fecha_hora_alta=row['fecha_hora_alta'],
            usuario_alta=row['usuario_alta'],
            fecha_hora_modificacion=row['fecha_hora_modificacion'],
            usuario_modificacion=row['usuario_modificacion'],
            clave_hash=row['clave_hash']
        )