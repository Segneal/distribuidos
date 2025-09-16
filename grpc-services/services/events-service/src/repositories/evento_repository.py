"""
Event repository for database operations
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone
import mysql.connector
from mysql.connector import Error

try:
    from ..config.database import db_config
    from ..models.evento import Evento, DonacionRepartida, Participante
except ImportError:
    # For testing or direct execution
    from config.database import db_config
    from models.evento import Evento, DonacionRepartida, Participante

class EventoRepository:
    """Repository for event database operations"""
    
    def __init__(self):
        self.db_config = db_config
    
    def crear_evento(self, evento: Evento) -> Optional[Evento]:
        """Create a new event in database"""
        connection = None
        cursor = None
        
        try:
            connection = self.db_config.get_connection()
            cursor = connection.cursor()
            
            # Insert event
            query = """
                INSERT INTO eventos (nombre, descripcion, fecha_hora, usuario_alta)
                VALUES (%s, %s, %s, %s)
            """
            
            fecha_hora_db = datetime.fromisoformat(evento.fecha_hora.replace('Z', '+00:00'))
            
            cursor.execute(query, (
                evento.nombre,
                evento.descripcion,
                fecha_hora_db,
                evento.usuario_alta
            ))
            
            evento_id = cursor.lastrowid
            connection.commit()
            
            # Retrieve created event
            return self.obtener_evento_por_id(evento_id)
            
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error creating event: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def obtener_evento_por_id(self, evento_id: int) -> Optional[Evento]:
        """Get event by ID"""
        connection = None
        cursor = None
        
        try:
            connection = self.db_config.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Get event data
            query = """
                SELECT id, nombre, descripcion, fecha_hora, 
                       fecha_hora_alta, usuario_alta, 
                       fecha_hora_modificacion, usuario_modificacion
                FROM eventos 
                WHERE id = %s
            """
            
            cursor.execute(query, (evento_id,))
            evento_data = cursor.fetchone()
            
            if not evento_data:
                return None
            
            # Get participants
            participantes_ids = self._obtener_participantes_ids(evento_id, cursor)
            
            # Get distributed donations
            donaciones_repartidas = self._obtener_donaciones_repartidas(evento_id, cursor)
            
            # Create event object
            evento = Evento(
                id=evento_data['id'],
                nombre=evento_data['nombre'],
                descripcion=evento_data['descripcion'],
                fecha_hora=evento_data['fecha_hora'].isoformat() if evento_data['fecha_hora'] else '',
                participantes_ids=participantes_ids,
                donaciones_repartidas=donaciones_repartidas,
                fecha_hora_alta=evento_data['fecha_hora_alta'].isoformat() if evento_data['fecha_hora_alta'] else None,
                usuario_alta=evento_data['usuario_alta'],
                fecha_hora_modificacion=evento_data['fecha_hora_modificacion'].isoformat() if evento_data['fecha_hora_modificacion'] else None,
                usuario_modificacion=evento_data['usuario_modificacion']
            )
            
            return evento
            
        except Error as e:
            print(f"Error getting event by ID: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def listar_eventos(self, pagina: int = 1, tamano_pagina: int = 10, 
                      solo_futuros: bool = False, solo_pasados: bool = False) -> Tuple[List[Evento], int]:
        """List events with pagination and filters"""
        connection = None
        cursor = None
        
        try:
            connection = self.db_config.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Build WHERE clause
            where_conditions = []
            params = []
            
            if solo_futuros:
                where_conditions.append("fecha_hora > NOW()")
            elif solo_pasados:
                where_conditions.append("fecha_hora <= NOW()")
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # Count total records
            count_query = f"SELECT COUNT(*) as total FROM eventos {where_clause}"
            cursor.execute(count_query, params)
            total_registros = cursor.fetchone()['total']
            
            # Get paginated results
            offset = (pagina - 1) * tamano_pagina
            query = f"""
                SELECT id, nombre, descripcion, fecha_hora, 
                       fecha_hora_alta, usuario_alta, 
                       fecha_hora_modificacion, usuario_modificacion
                FROM eventos 
                {where_clause}
                ORDER BY fecha_hora DESC
                LIMIT %s OFFSET %s
            """
            
            params.extend([tamano_pagina, offset])
            cursor.execute(query, params)
            eventos_data = cursor.fetchall()
            
            eventos = []
            for evento_data in eventos_data:
                # Get participants for each event
                participantes_ids = self._obtener_participantes_ids(evento_data['id'], cursor)
                
                # Get distributed donations for each event
                donaciones_repartidas = self._obtener_donaciones_repartidas(evento_data['id'], cursor)
                
                evento = Evento(
                    id=evento_data['id'],
                    nombre=evento_data['nombre'],
                    descripcion=evento_data['descripcion'],
                    fecha_hora=evento_data['fecha_hora'].isoformat() if evento_data['fecha_hora'] else '',
                    participantes_ids=participantes_ids,
                    donaciones_repartidas=donaciones_repartidas,
                    fecha_hora_alta=evento_data['fecha_hora_alta'].isoformat() if evento_data['fecha_hora_alta'] else None,
                    usuario_alta=evento_data['usuario_alta'],
                    fecha_hora_modificacion=evento_data['fecha_hora_modificacion'].isoformat() if evento_data['fecha_hora_modificacion'] else None,
                    usuario_modificacion=evento_data['usuario_modificacion']
                )
                eventos.append(evento)
            
            return eventos, total_registros
            
        except Error as e:
            print(f"Error listing events: {e}")
            return [], 0
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def actualizar_evento(self, evento: Evento) -> Optional[Evento]:
        """Update event in database"""
        connection = None
        cursor = None
        
        try:
            connection = self.db_config.get_connection()
            cursor = connection.cursor()
            
            query = """
                UPDATE eventos 
                SET nombre = %s, descripcion = %s, fecha_hora = %s, 
                    fecha_hora_modificacion = CURRENT_TIMESTAMP, usuario_modificacion = %s
                WHERE id = %s
            """
            
            fecha_hora_db = datetime.fromisoformat(evento.fecha_hora.replace('Z', '+00:00'))
            
            cursor.execute(query, (
                evento.nombre,
                evento.descripcion,
                fecha_hora_db,
                evento.usuario_modificacion,
                evento.id
            ))
            
            if cursor.rowcount == 0:
                return None
            
            connection.commit()
            
            # Return updated event
            return self.obtener_evento_por_id(evento.id)
            
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error updating event: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def eliminar_evento(self, evento_id: int) -> bool:
        """Delete event from database (physical deletion)"""
        connection = None
        cursor = None
        
        try:
            connection = self.db_config.get_connection()
            cursor = connection.cursor()
            
            # Delete event (CASCADE will handle participants and donations)
            query = "DELETE FROM eventos WHERE id = %s"
            cursor.execute(query, (evento_id,))
            
            success = cursor.rowcount > 0
            connection.commit()
            
            return success
            
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error deleting event: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def agregar_participante(self, evento_id: int, usuario_id: int) -> bool:
        """Add participant to event"""
        connection = None
        cursor = None
        
        try:
            connection = self.db_config.get_connection()
            cursor = connection.cursor()
            
            query = """
                INSERT INTO evento_participantes (evento_id, usuario_id)
                VALUES (%s, %s)
            """
            
            cursor.execute(query, (evento_id, usuario_id))
            connection.commit()
            
            return cursor.rowcount > 0
            
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error adding participant: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def quitar_participante(self, evento_id: int, usuario_id: int) -> bool:
        """Remove participant from event"""
        connection = None
        cursor = None
        
        try:
            connection = self.db_config.get_connection()
            cursor = connection.cursor()
            
            query = """
                DELETE FROM evento_participantes 
                WHERE evento_id = %s AND usuario_id = %s
            """
            
            cursor.execute(query, (evento_id, usuario_id))
            connection.commit()
            
            return cursor.rowcount > 0
            
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error removing participant: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def obtener_participante_info(self, usuario_id: int) -> Optional[Participante]:
        """Get participant information from users table"""
        connection = None
        cursor = None
        
        try:
            connection = self.db_config.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT id, nombre_usuario, nombre, apellido, rol
                FROM usuarios 
                WHERE id = %s AND activo = true
            """
            
            cursor.execute(query, (usuario_id,))
            usuario_data = cursor.fetchone()
            
            if not usuario_data:
                return None
            
            return Participante(
                usuario_id=usuario_data['id'],
                nombre_usuario=usuario_data['nombre_usuario'],
                nombre=usuario_data['nombre'],
                apellido=usuario_data['apellido'],
                rol=usuario_data['rol']
            )
            
        except Error as e:
            print(f"Error getting participant info: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def registrar_donaciones_repartidas(self, evento_id: int, 
                                      donaciones: List[DonacionRepartida]) -> List[DonacionRepartida]:
        """Register distributed donations for an event"""
        connection = None
        cursor = None
        
        try:
            connection = self.db_config.get_connection()
            cursor = connection.cursor()
            
            donaciones_registradas = []
            
            for donacion in donaciones:
                query = """
                    INSERT INTO donaciones_repartidas 
                    (evento_id, donacion_id, cantidad_repartida, usuario_registro)
                    VALUES (%s, %s, %s, %s)
                """
                
                cursor.execute(query, (
                    evento_id,
                    donacion.donacion_id,
                    donacion.cantidad_repartida,
                    donacion.usuario_registro
                ))
                
                donaciones_registradas.append(donacion)
            
            connection.commit()
            return donaciones_registradas
            
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error registering distributed donations: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def _obtener_participantes_ids(self, evento_id: int, cursor) -> List[int]:
        """Get participant IDs for an event"""
        try:
            query = """
                SELECT usuario_id 
                FROM evento_participantes 
                WHERE evento_id = %s
            """
            
            cursor.execute(query, (evento_id,))
            results = cursor.fetchall()
            
            return [row['usuario_id'] if isinstance(row, dict) else row[0] for row in results]
            
        except Error as e:
            print(f"Error getting participants: {e}")
            return []
    
    def _obtener_donaciones_repartidas(self, evento_id: int, cursor) -> List[DonacionRepartida]:
        """Get distributed donations for an event"""
        try:
            query = """
                SELECT donacion_id, cantidad_repartida, usuario_registro, fecha_hora_registro
                FROM donaciones_repartidas 
                WHERE evento_id = %s
            """
            
            cursor.execute(query, (evento_id,))
            results = cursor.fetchall()
            
            donaciones = []
            for row in results:
                if isinstance(row, dict):
                    donacion = DonacionRepartida(
                        donacion_id=row['donacion_id'],
                        cantidad_repartida=row['cantidad_repartida'],
                        usuario_registro=row['usuario_registro'],
                        fecha_hora_registro=row['fecha_hora_registro'].isoformat() if row['fecha_hora_registro'] else None
                    )
                else:
                    donacion = DonacionRepartida(
                        donacion_id=row[0],
                        cantidad_repartida=row[1],
                        usuario_registro=row[2],
                        fecha_hora_registro=row[3].isoformat() if row[3] else None
                    )
                donaciones.append(donacion)
            
            return donaciones
            
        except Error as e:
            print(f"Error getting distributed donations: {e}")
            return []
    
    def guardar_evento_externo(self, evento_data: Dict[str, Any]) -> bool:
        """Save external event to database"""
        connection = None
        cursor = None
        
        try:
            connection = self.db_config.get_connection()
            cursor = connection.cursor()
            
            # Check if event already exists
            check_query = """
                SELECT COUNT(*) as count 
                FROM eventos_externos 
                WHERE id_organizacion = %s AND id_evento = %s
            """
            
            cursor.execute(check_query, (
                evento_data.get('idOrganizacion'),
                evento_data.get('idEvento')
            ))
            
            result = cursor.fetchone()
            count = result[0] if isinstance(result, tuple) else result['count']
            
            if count > 0:
                print(f"Evento externo ya existe: {evento_data.get('idOrganizacion')}-{evento_data.get('idEvento')}")
                return True
            
            # Insert external event
            insert_query = """
                INSERT INTO eventos_externos 
                (id_organizacion, id_evento, nombre, descripcion, fecha_hora, fecha_recepcion)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            
            # Parse fecha_hora
            fecha_hora_db = None
            if evento_data.get('fechaHora'):
                try:
                    fecha_hora_db = datetime.fromisoformat(evento_data['fechaHora'].replace('Z', '+00:00'))
                except ValueError:
                    # Try parsing as timestamp
                    fecha_hora_db = datetime.fromtimestamp(float(evento_data['fechaHora']), tz=timezone.utc)
            
            cursor.execute(insert_query, (
                evento_data.get('idOrganizacion'),
                evento_data.get('idEvento'),
                evento_data.get('nombre'),
                evento_data.get('descripcion'),
                fecha_hora_db
            ))
            
            connection.commit()
            
            print(f"Evento externo guardado: {evento_data.get('idOrganizacion')}-{evento_data.get('idEvento')}")
            return True
            
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error saving external event: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def marcar_evento_externo_inactivo(self, id_organizacion: str, id_evento: str) -> bool:
        """Mark external event as inactive"""
        connection = None
        cursor = None
        
        try:
            connection = self.db_config.get_connection()
            cursor = connection.cursor()
            
            query = """
                UPDATE eventos_externos 
                SET activo = false 
                WHERE id_organizacion = %s AND id_evento = %s
            """
            
            cursor.execute(query, (id_organizacion, id_evento))
            connection.commit()
            
            if cursor.rowcount > 0:
                print(f"Evento externo marcado como inactivo: {id_organizacion}-{id_evento}")
                return True
            else:
                print(f"Evento externo no encontrado para marcar inactivo: {id_organizacion}-{id_evento}")
                return False
            
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error marking external event as inactive: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def listar_eventos_externos(self, pagina: int = 1, tamano_pagina: int = 10, 
                               solo_futuros: bool = True) -> Tuple[List[Dict[str, Any]], int]:
        """List external events with pagination"""
        connection = None
        cursor = None
        
        try:
            connection = self.db_config.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Build WHERE clause
            where_conditions = ["activo = true"]
            params = []
            
            if solo_futuros:
                where_conditions.append("fecha_hora > NOW()")
            
            where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # Count total records
            count_query = f"SELECT COUNT(*) as total FROM eventos_externos {where_clause}"
            cursor.execute(count_query, params)
            total_registros = cursor.fetchone()['total']
            
            # Get paginated results
            offset = (pagina - 1) * tamano_pagina
            query = f"""
                SELECT id_organizacion, id_evento, nombre, descripcion, 
                       fecha_hora, fecha_recepcion
                FROM eventos_externos 
                {where_clause}
                ORDER BY fecha_hora ASC
                LIMIT %s OFFSET %s
            """
            
            params.extend([tamano_pagina, offset])
            cursor.execute(query, params)
            eventos_data = cursor.fetchall()
            
            # Convert to list of dictionaries
            eventos = []
            for evento_data in eventos_data:
                evento = {
                    'idOrganizacion': evento_data['id_organizacion'],
                    'idEvento': evento_data['id_evento'],
                    'nombre': evento_data['nombre'],
                    'descripcion': evento_data['descripcion'],
                    'fechaHora': evento_data['fecha_hora'].isoformat() if evento_data['fecha_hora'] else None,
                    'fechaRecepcion': evento_data['fecha_recepcion'].isoformat() if evento_data['fecha_recepcion'] else None
                }
                eventos.append(evento)
            
            return eventos, total_registros
            
        except Error as e:
            print(f"Error listing external events: {e}")
            return [], 0
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()