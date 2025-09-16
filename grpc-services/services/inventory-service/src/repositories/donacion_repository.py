"""
Repository for Donacion data access operations
"""
import mysql.connector
from datetime import datetime
from typing import List, Optional, Tuple
from config.database import get_db_config
from models.donacion import Donacion

class DonacionRepository:
    """Repository class for donation data access"""
    
    def __init__(self):
        self.db_config = get_db_config()
    
    def crear_donacion(self, donacion: Donacion) -> Optional[Donacion]:
        """Create a new donation"""
        conn = None
        cursor = None
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            # Set audit fields
            donacion.fecha_hora_alta = datetime.now()
            
            query = """
                INSERT INTO donaciones (categoria, descripcion, cantidad, eliminado, 
                                      fecha_hora_alta, usuario_alta)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            values = (
                donacion.categoria,
                donacion.descripcion,
                donacion.cantidad,
                donacion.eliminado,
                donacion.fecha_hora_alta,
                donacion.usuario_alta
            )
            
            cursor.execute(query, values)
            donacion.id = cursor.lastrowid
            conn.commit()
            
            return donacion
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            print(f"Error creating donation: {err}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def obtener_donacion_por_id(self, donacion_id: int) -> Optional[Donacion]:
        """Get donation by ID"""
        conn = None
        cursor = None
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT id, categoria, descripcion, cantidad, eliminado,
                       fecha_hora_alta, usuario_alta, fecha_hora_modificacion, 
                       usuario_modificacion
                FROM donaciones 
                WHERE id = %s
            """
            
            cursor.execute(query, (donacion_id,))
            result = cursor.fetchone()
            
            if result:
                return Donacion(
                    id=result['id'],
                    categoria=result['categoria'],
                    descripcion=result['descripcion'],
                    cantidad=result['cantidad'],
                    eliminado=result['eliminado'],
                    fecha_hora_alta=result['fecha_hora_alta'],
                    usuario_alta=result['usuario_alta'],
                    fecha_hora_modificacion=result['fecha_hora_modificacion'],
                    usuario_modificacion=result['usuario_modificacion']
                )
            
            return None
            
        except mysql.connector.Error as err:
            print(f"Error getting donation by ID: {err}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def listar_donaciones(self, pagina: int = 1, tamano_pagina: int = 10, 
                         categoria: str = None, incluir_eliminados: bool = False) -> Tuple[List[Donacion], int]:
        """List donations with pagination and filters"""
        conn = None
        cursor = None
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Build WHERE clause
            where_conditions = []
            params = []
            
            if not incluir_eliminados:
                where_conditions.append("eliminado = %s")
                params.append(False)
            
            if categoria:
                where_conditions.append("categoria = %s")
                params.append(categoria)
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # Count total records
            count_query = f"SELECT COUNT(*) as total FROM donaciones {where_clause}"
            cursor.execute(count_query, params)
            total_records = cursor.fetchone()['total']
            
            # Get paginated results
            offset = (pagina - 1) * tamano_pagina
            query = f"""
                SELECT id, categoria, descripcion, cantidad, eliminado,
                       fecha_hora_alta, usuario_alta, fecha_hora_modificacion, 
                       usuario_modificacion
                FROM donaciones 
                {where_clause}
                ORDER BY fecha_hora_alta DESC
                LIMIT %s OFFSET %s
            """
            
            params.extend([tamano_pagina, offset])
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            donaciones = []
            for result in results:
                donacion = Donacion(
                    id=result['id'],
                    categoria=result['categoria'],
                    descripcion=result['descripcion'],
                    cantidad=result['cantidad'],
                    eliminado=result['eliminado'],
                    fecha_hora_alta=result['fecha_hora_alta'],
                    usuario_alta=result['usuario_alta'],
                    fecha_hora_modificacion=result['fecha_hora_modificacion'],
                    usuario_modificacion=result['usuario_modificacion']
                )
                donaciones.append(donacion)
            
            return donaciones, total_records
            
        except mysql.connector.Error as err:
            print(f"Error listing donations: {err}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def actualizar_donacion(self, donacion: Donacion) -> Optional[Donacion]:
        """Update donation (only descripcion and cantidad)"""
        conn = None
        cursor = None
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            # Set modification audit fields
            donacion.fecha_hora_modificacion = datetime.now()
            
            query = """
                UPDATE donaciones 
                SET descripcion = %s, cantidad = %s, fecha_hora_modificacion = %s, 
                    usuario_modificacion = %s
                WHERE id = %s AND eliminado = FALSE
            """
            
            values = (
                donacion.descripcion,
                donacion.cantidad,
                donacion.fecha_hora_modificacion,
                donacion.usuario_modificacion,
                donacion.id
            )
            
            cursor.execute(query, values)
            
            if cursor.rowcount == 0:
                return None  # No rows affected - donation not found or already deleted
            
            conn.commit()
            return donacion
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            print(f"Error updating donation: {err}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def eliminar_donacion(self, donacion_id: int, usuario_eliminacion: str) -> bool:
        """Logical deletion of donation"""
        conn = None
        cursor = None
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            query = """
                UPDATE donaciones 
                SET eliminado = TRUE, fecha_hora_modificacion = %s, 
                    usuario_modificacion = %s
                WHERE id = %s AND eliminado = FALSE
            """
            
            values = (datetime.now(), usuario_eliminacion, donacion_id)
            cursor.execute(query, values)
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            print(f"Error deleting donation: {err}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def actualizar_stock(self, donacion_id: int, cantidad_cambio: int, 
                        usuario_modificacion: str, motivo: str) -> Optional[int]:
        """Update stock quantity (for transfers)"""
        conn = None
        cursor = None
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            # First, get current quantity
            cursor.execute("SELECT cantidad FROM donaciones WHERE id = %s AND eliminado = FALSE", (donacion_id,))
            result = cursor.fetchone()
            
            if not result:
                return None  # Donation not found
            
            current_quantity = result[0]
            new_quantity = current_quantity + cantidad_cambio
            
            # Validate that new quantity is not negative
            if new_quantity < 0:
                raise ValueError(f"Stock insuficiente. Cantidad actual: {current_quantity}, cambio solicitado: {cantidad_cambio}")
            
            # Update quantity
            update_query = """
                UPDATE donaciones 
                SET cantidad = %s, fecha_hora_modificacion = %s, usuario_modificacion = %s
                WHERE id = %s AND eliminado = FALSE
            """
            
            cursor.execute(update_query, (new_quantity, datetime.now(), usuario_modificacion, donacion_id))
            
            if cursor.rowcount == 0:
                return None
            
            # Log the stock change for audit
            audit_query = """
                INSERT INTO auditoria_stock (donacion_id, cantidad_anterior, cantidad_nueva, 
                                           cantidad_cambio, motivo, usuario_modificacion, fecha_cambio)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(audit_query, (
                donacion_id, current_quantity, new_quantity, cantidad_cambio, 
                motivo, usuario_modificacion, datetime.now()
            ))
            
            conn.commit()
            return new_quantity
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            print(f"Error updating stock: {err}")
            raise
        except ValueError as err:
            if conn:
                conn.rollback()
            print(f"Stock validation error: {err}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def validar_stock(self, donacion_id: int, cantidad_requerida: int) -> Tuple[bool, int]:
        """Validate if there's enough stock"""
        conn = None
        cursor = None
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT cantidad FROM donaciones WHERE id = %s AND eliminado = FALSE"
            cursor.execute(query, (donacion_id,))
            result = cursor.fetchone()
            
            if not result:
                return False, 0  # Donation not found
            
            cantidad_disponible = result[0]
            tiene_stock_suficiente = cantidad_disponible >= cantidad_requerida
            
            return tiene_stock_suficiente, cantidad_disponible
            
        except mysql.connector.Error as err:
            print(f"Error validating stock: {err}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()    
def buscar_donaciones_por_categoria_descripcion(self, categoria: str, descripcion: str) -> List[Donacion]:
        """Search for donations by category and description"""
        conn = None
        cursor = None
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT id, categoria, descripcion, cantidad, eliminado,
                       fecha_hora_alta, usuario_alta, fecha_hora_modificacion, usuario_modificacion
                FROM donaciones 
                WHERE categoria = %s AND descripcion = %s AND eliminado = FALSE
                ORDER BY fecha_hora_alta ASC
            """
            
            cursor.execute(query, (categoria, descripcion))
            rows = cursor.fetchall()
            
            donaciones = []
            for row in rows:
                donacion = Donacion(
                    id=row['id'],
                    categoria=row['categoria'],
                    descripcion=row['descripcion'],
                    cantidad=row['cantidad'],
                    eliminado=row['eliminado'],
                    fecha_hora_alta=row['fecha_hora_alta'],
                    usuario_alta=row['usuario_alta'],
                    fecha_hora_modificacion=row['fecha_hora_modificacion'],
                    usuario_modificacion=row['usuario_modificacion']
                )
                donaciones.append(donacion)
            
            return donaciones
            
        except mysql.connector.Error as err:
            print(f"Error searching donations: {err}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()