#!/usr/bin/env python3
"""
SQL Data Extractor for Testing Configuration Generation
Sistema ONG - SQL Driven Testing

This module extracts test data from the populated SQL database to generate
testing configurations for Postman, Swagger, and Kafka scenarios.
"""

import mysql.connector
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    host: str
    port: int
    database: str
    user: str
    password: str

class SQLDataExtractor:
    """Extracts test data from the populated SQL database"""
    
    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.db_config.host,
                port=self.db_config.port,
                database=self.db_config.database,
                user=self.db_config.user,
                password=self.db_config.password,
                autocommit=True
            )
            logger.info("Database connection established successfully")
        except mysql.connector.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Database connection closed")
    
    def test_connection(self) -> bool:
        """Test database connection without extracting data"""
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
        finally:
            self.disconnect()
    
    def extract_test_data(self) -> Dict[str, Any]:
        """Extract all test data needed for configuration generation"""
        logger.info("Starting test data extraction from SQL database")
        
        if not self.connection:
            self.connect()
        
        try:
            data = {
                'users': self.extract_users_by_role(),
                'inventory': self.extract_inventory_by_category(),
                'events': self.extract_events_by_status(),
                'network': self.extract_network_data(),
                'test_mappings': self.extract_test_case_mappings(),
                'audit_data': self.extract_audit_data()
            }
            
            # Validate extracted data integrity
            self.validate_data_integrity(data)
            
            logger.info("Test data extraction completed successfully")
            return data
            
        except Exception as e:
            logger.error(f"Error during data extraction: {e}")
            raise
    
    def extract_users_by_role(self) -> Dict[str, Dict]:
        """Extract users organized by role for authorization testing"""
        logger.info("Extracting users by role")
        
        query = """
        SELECT id, nombre_usuario, nombre, apellido, email, rol, activo,
               telefono, fecha_hora_alta, usuario_alta,
               'test123' as password_plain
        FROM usuarios 
        WHERE nombre_usuario LIKE 'test_%'
        ORDER BY rol, id
        """
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        users = cursor.fetchall()
        cursor.close()
        
        # Organize users by role
        users_by_role = {}
        for user in users:
            role = user['rol']
            if role not in users_by_role:
                users_by_role[role] = []
            
            # Convert datetime objects to strings for JSON serialization
            user_data = dict(user)
            if user_data['fecha_hora_alta']:
                user_data['fecha_hora_alta'] = user_data['fecha_hora_alta'].isoformat()
            
            users_by_role[role].append(user_data)
        
        logger.info(f"Extracted {len(users)} test users across {len(users_by_role)} roles")
        return users_by_role
    
    def extract_inventory_by_category(self) -> Dict[str, List]:
        """Extract donations organized by category and stock levels"""
        logger.info("Extracting inventory by category")
        
        query = """
        SELECT id, categoria, descripcion, cantidad, eliminado,
               fecha_hora_alta, usuario_alta, fecha_hora_modificacion, usuario_modificacion
        FROM donaciones 
        WHERE usuario_alta LIKE 'test_%'
        ORDER BY categoria, cantidad DESC
        """
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        donations = cursor.fetchall()
        cursor.close()
        
        # Organize donations by category and stock level
        inventory = {}
        for donation in donations:
            categoria = donation['categoria']
            if categoria not in inventory:
                inventory[categoria] = {
                    'high_stock': [],    # cantidad > 50
                    'medium_stock': [],  # 10 <= cantidad <= 50
                    'low_stock': [],     # 1 <= cantidad < 10
                    'zero_stock': [],    # cantidad = 0
                    'all': []
                }
            
            # Convert datetime objects to strings
            donation_data = dict(donation)
            if donation_data['fecha_hora_alta']:
                donation_data['fecha_hora_alta'] = donation_data['fecha_hora_alta'].isoformat()
            if donation_data['fecha_hora_modificacion']:
                donation_data['fecha_hora_modificacion'] = donation_data['fecha_hora_modificacion'].isoformat()
            
            # Categorize by stock level
            cantidad = donation['cantidad']
            if cantidad > 50:
                inventory[categoria]['high_stock'].append(donation_data)
            elif cantidad >= 10:
                inventory[categoria]['medium_stock'].append(donation_data)
            elif cantidad >= 1:
                inventory[categoria]['low_stock'].append(donation_data)
            else:
                inventory[categoria]['zero_stock'].append(donation_data)
            
            inventory[categoria]['all'].append(donation_data)
        
        logger.info(f"Extracted {len(donations)} donations across {len(inventory)} categories")
        return inventory
    
    def extract_events_by_status(self) -> Dict[str, List]:
        """Extract events organized by temporal status (future, past, current)"""
        logger.info("Extracting events by status")
        
        query = """
        SELECT e.id, e.nombre, e.descripcion, e.fecha_hora,
               e.fecha_hora_alta, e.usuario_alta,
               GROUP_CONCAT(ep.usuario_id) as participantes_ids,
               COUNT(ep.usuario_id) as total_participantes
        FROM eventos e
        LEFT JOIN evento_participantes ep ON e.id = ep.evento_id
        WHERE e.usuario_alta LIKE 'test_%'
        GROUP BY e.id
        ORDER BY e.fecha_hora
        """
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        events = cursor.fetchall()
        cursor.close()
        
        # Organize events by temporal status
        now = datetime.now()
        events_by_status = {
            'future': [],
            'past': [],
            'current': [],  # events happening today
            'all': []
        }
        
        for event in events:
            # Convert datetime objects to strings and process participants
            event_data = dict(event)
            event_datetime = event['fecha_hora']
            event_data['fecha_hora'] = event_datetime.isoformat()
            event_data['fecha_hora_alta'] = event['fecha_hora_alta'].isoformat()
            
            # Process participants
            if event_data['participantes_ids']:
                event_data['participantes'] = [int(id) for id in event_data['participantes_ids'].split(',')]
            else:
                event_data['participantes'] = []
            del event_data['participantes_ids']
            
            # Categorize by temporal status
            if event_datetime.date() == now.date():
                events_by_status['current'].append(event_data)
            elif event_datetime > now:
                events_by_status['future'].append(event_data)
            else:
                events_by_status['past'].append(event_data)
            
            events_by_status['all'].append(event_data)
        
        logger.info(f"Extracted {len(events)} events: {len(events_by_status['future'])} future, {len(events_by_status['past'])} past, {len(events_by_status['current'])} current")
        return events_by_status
    
    def extract_network_data(self) -> Dict[str, Any]:
        """Extract data for inter-NGO network testing"""
        logger.info("Extracting network data for inter-NGO testing")
        
        network_data = {
            'external_requests': self.extract_external_donation_requests(),
            'external_offers': self.extract_external_donation_offers(),
            'external_events': self.extract_external_events(),
            'own_requests': self.extract_own_requests(),
            'own_offers': self.extract_own_offers(),
            'transfers_sent': self.extract_transfers_sent(),
            'transfers_received': self.extract_transfers_received(),
            'event_adhesions': self.extract_event_adhesions()
        }
        
        return network_data
    
    def extract_external_donation_requests(self) -> List[Dict]:
        """Extract external donation requests (received via Kafka)"""
        query = """
        SELECT id_organizacion, id_solicitud, categoria, descripcion, 
               activa, fecha_recepcion
        FROM solicitudes_externas
        ORDER BY fecha_recepcion DESC
        """
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        requests = cursor.fetchall()
        cursor.close()
        
        # Convert datetime objects
        for request in requests:
            request['fecha_recepcion'] = request['fecha_recepcion'].isoformat()
        
        return requests
    
    def extract_external_donation_offers(self) -> List[Dict]:
        """Extract external donation offers (received via Kafka)"""
        query = """
        SELECT id_organizacion, id_oferta, categoria, descripcion, 
               cantidad, fecha_recepcion
        FROM ofertas_externas
        ORDER BY fecha_recepcion DESC
        """
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        offers = cursor.fetchall()
        cursor.close()
        
        # Convert datetime objects
        for offer in offers:
            offer['fecha_recepcion'] = offer['fecha_recepcion'].isoformat()
        
        return offers
    
    def extract_external_events(self) -> List[Dict]:
        """Extract external events (received via Kafka)"""
        query = """
        SELECT id_organizacion, id_evento, nombre, descripcion, 
               fecha_hora, activo, fecha_recepcion
        FROM eventos_externos
        ORDER BY fecha_hora
        """
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        events = cursor.fetchall()
        cursor.close()
        
        # Convert datetime objects
        for event in events:
            event['fecha_hora'] = event['fecha_hora'].isoformat()
            event['fecha_recepcion'] = event['fecha_recepcion'].isoformat()
        
        return events
    
    def extract_own_requests(self) -> List[Dict]:
        """Extract our own donation requests (sent via Kafka)"""
        query = """
        SELECT id_solicitud, donaciones_json, usuario_creador, 
               fecha_creacion, activa, fecha_baja, usuario_baja
        FROM solicitudes_propias
        ORDER BY fecha_creacion DESC
        """
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        requests = cursor.fetchall()
        cursor.close()
        
        # Process JSON and datetime fields
        for request in requests:
            request['donaciones'] = json.loads(request['donaciones_json'])
            del request['donaciones_json']
            request['fecha_creacion'] = request['fecha_creacion'].isoformat()
            if request['fecha_baja']:
                request['fecha_baja'] = request['fecha_baja'].isoformat()
        
        return requests
    
    def extract_own_offers(self) -> List[Dict]:
        """Extract our own donation offers (sent via Kafka)"""
        query = """
        SELECT id_oferta, donaciones_json, usuario_creador, fecha_creacion
        FROM ofertas_propias
        ORDER BY fecha_creacion DESC
        """
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        offers = cursor.fetchall()
        cursor.close()
        
        # Process JSON and datetime fields
        for offer in offers:
            offer['donaciones'] = json.loads(offer['donaciones_json'])
            del offer['donaciones_json']
            offer['fecha_creacion'] = offer['fecha_creacion'].isoformat()
        
        return offers
    
    def extract_transfers_sent(self) -> List[Dict]:
        """Extract donation transfers sent to other NGOs"""
        query = """
        SELECT id_solicitud, id_organizacion_solicitante, donaciones_json,
               usuario_transferencia, fecha_transferencia
        FROM transferencias_enviadas
        ORDER BY fecha_transferencia DESC
        """
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        transfers = cursor.fetchall()
        cursor.close()
        
        # Process JSON and datetime fields
        for transfer in transfers:
            transfer['donaciones'] = json.loads(transfer['donaciones_json'])
            del transfer['donaciones_json']
            transfer['fecha_transferencia'] = transfer['fecha_transferencia'].isoformat()
        
        return transfers
    
    def extract_transfers_received(self) -> List[Dict]:
        """Extract donation transfers received from other NGOs"""
        query = """
        SELECT id_solicitud, id_organizacion_donante, donaciones_json, fecha_recepcion
        FROM transferencias_recibidas
        ORDER BY fecha_recepcion DESC
        """
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        transfers = cursor.fetchall()
        cursor.close()
        
        # Process JSON and datetime fields
        for transfer in transfers:
            transfer['donaciones'] = json.loads(transfer['donaciones_json'])
            del transfer['donaciones_json']
            transfer['fecha_recepcion'] = transfer['fecha_recepcion'].isoformat()
        
        return transfers
    
    def extract_event_adhesions(self) -> List[Dict]:
        """Extract adhesions to external events"""
        query = """
        SELECT aee.id_organizacion, aee.id_evento, aee.usuario_id, aee.fecha_adhesion,
               u.nombre_usuario, u.nombre, u.apellido, u.rol
        FROM adhesiones_eventos_externos aee
        JOIN usuarios u ON aee.usuario_id = u.id
        ORDER BY aee.fecha_adhesion DESC
        """
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        adhesions = cursor.fetchall()
        cursor.close()
        
        # Convert datetime objects
        for adhesion in adhesions:
            adhesion['fecha_adhesion'] = adhesion['fecha_adhesion'].isoformat()
        
        return adhesions
    
    def extract_test_case_mappings(self) -> List[Dict]:
        """Extract test case mappings for endpoint testing"""
        logger.info("Extracting test case mappings")
        
        query = """
        SELECT endpoint, method, test_type, user_id, resource_id,
               description, expected_status, request_body, expected_response_fields,
               test_category
        FROM test_case_mapping
        ORDER BY test_category, endpoint, method, test_type
        """
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        mappings = cursor.fetchall()
        cursor.close()
        
        # Process JSON fields
        for mapping in mappings:
            if mapping['request_body']:
                mapping['request_body'] = json.loads(mapping['request_body'])
            if mapping['expected_response_fields']:
                mapping['expected_response_fields'] = json.loads(mapping['expected_response_fields'])
        
        logger.info(f"Extracted {len(mappings)} test case mappings")
        return mappings
    
    def extract_audit_data(self) -> Dict[str, List]:
        """Extract audit data for testing traceability"""
        logger.info("Extracting audit data")
        
        query = """
        SELECT donacion_id, cantidad_anterior, cantidad_nueva, cantidad_cambio,
               motivo, usuario_modificacion, fecha_cambio
        FROM auditoria_stock
        ORDER BY fecha_cambio DESC
        """
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        audit_records = cursor.fetchall()
        cursor.close()
        
        # Convert datetime objects
        for record in audit_records:
            record['fecha_cambio'] = record['fecha_cambio'].isoformat()
        
        return {'stock_changes': audit_records}
    
    def validate_data_integrity(self, data: Dict[str, Any]):
        """Validate the integrity of extracted data and foreign key relationships"""
        logger.info("Validating data integrity")
        
        errors = []
        
        # Validate users data
        if not data['users']:
            errors.append("No test users found")
        else:
            total_users = sum(len(users) for users in data['users'].values())
            if total_users < 4:  # Should have at least one user per role
                errors.append(f"Insufficient test users: {total_users} found, expected at least 4")
        
        # Validate inventory data
        if not data['inventory']:
            errors.append("No inventory data found")
        else:
            required_categories = ['ALIMENTOS', 'ROPA', 'JUGUETES', 'UTILES_ESCOLARES']
            missing_categories = [cat for cat in required_categories if cat not in data['inventory']]
            if missing_categories:
                errors.append(f"Missing inventory categories: {missing_categories}")
        
        # Validate events data
        if not data['events']['all']:
            errors.append("No events data found")
        
        # Validate test mappings
        if not data['test_mappings']:
            errors.append("No test case mappings found")
        else:
            # Check that we have mappings for all major categories
            categories = set(mapping['test_category'] for mapping in data['test_mappings'])
            required_categories = ['authentication', 'users', 'inventory', 'events', 'network']
            missing_categories = [cat for cat in required_categories if cat not in categories]
            if missing_categories:
                errors.append(f"Missing test mapping categories: {missing_categories}")
        
        # Validate foreign key relationships
        self.validate_foreign_keys(data, errors)
        
        if errors:
            error_msg = "Data integrity validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Data integrity validation passed")
    
    def validate_foreign_keys(self, data: Dict[str, Any], errors: List[str]):
        """Validate foreign key relationships in the extracted data"""
        
        # Get all user IDs
        all_user_ids = set()
        for role_users in data['users'].values():
            for user in role_users:
                all_user_ids.add(user['id'])
        
        # Get all donation IDs
        all_donation_ids = set()
        for category_data in data['inventory'].values():
            for donation in category_data['all']:
                all_donation_ids.add(donation['id'])
        
        # Validate event participants reference valid users
        for event in data['events']['all']:
            for participant_id in event['participantes']:
                if participant_id not in all_user_ids:
                    errors.append(f"Event {event['id']} references non-existent user {participant_id}")
        
        # Validate test mappings reference valid users and resources
        for mapping in data['test_mappings']:
            if mapping['user_id'] and mapping['user_id'] not in all_user_ids:
                errors.append(f"Test mapping '{mapping['description']}' references non-existent user {mapping['user_id']}")
            
            # For inventory-related mappings, validate donation IDs
            if mapping['test_category'] == 'inventory' and mapping['resource_id']:
                if mapping['resource_id'] not in all_donation_ids:
                    errors.append(f"Test mapping '{mapping['description']}' references non-existent donation {mapping['resource_id']}")
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get a specific user by ID from extracted data"""
        for role_users in self.extract_users_by_role().values():
            for user in role_users:
                if user['id'] == user_id:
                    return user
        return None
    
    def get_donation_by_id(self, donation_id: int) -> Optional[Dict]:
        """Get a specific donation by ID from extracted data"""
        inventory = self.extract_inventory_by_category()
        for category_data in inventory.values():
            for donation in category_data['all']:
                if donation['id'] == donation_id:
                    return donation
        return None
    
    def get_test_cases_by_category(self, category: str) -> List[Dict]:
        """Get test cases filtered by category"""
        mappings = self.extract_test_case_mappings()
        return [mapping for mapping in mappings if mapping['test_category'] == category]
    
    def get_test_cases_by_endpoint(self, endpoint: str) -> List[Dict]:
        """Get test cases filtered by endpoint"""
        mappings = self.extract_test_case_mappings()
        return [mapping for mapping in mappings if mapping['endpoint'] == endpoint]

def create_db_config_from_env() -> DatabaseConfig:
    """Create database configuration from environment variables"""
    return DatabaseConfig(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '3306')),
        database=os.getenv('DB_NAME', 'ong_sistema'),
        user=os.getenv('DB_USER', 'ong_user'),
        password=os.getenv('DB_PASSWORD', 'ong_password')
    )

if __name__ == "__main__":
    # Example usage
    db_config = create_db_config_from_env()
    extractor = SQLDataExtractor(db_config)
    
    try:
        test_data = extractor.extract_test_data()
        
        # Print summary
        print("\n=== Test Data Extraction Summary ===")
        print(f"Users by role: {list(test_data['users'].keys())}")
        print(f"Inventory categories: {list(test_data['inventory'].keys())}")
        print(f"Events: {len(test_data['events']['all'])} total")
        print(f"Test mappings: {len(test_data['test_mappings'])} cases")
        print(f"Network data: {len(test_data['network']['external_requests'])} external requests")
        
        # Save to file for inspection
        output_file = "extracted_test_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)
        print(f"\nTest data saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Failed to extract test data: {e}")
        raise
    finally:
        extractor.disconnect()