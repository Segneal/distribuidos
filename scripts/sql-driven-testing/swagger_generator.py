#!/usr/bin/env python3
"""
Swagger Examples Generator for SQL-Driven Testing
Sistema ONG - SQL Driven Testing

This module updates Swagger documentation examples with real data extracted from
the populated SQL database, ensuring documentation always reflects valid, executable examples.
"""

import json
import logging
import os
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SwaggerGenerator:
    """Updates Swagger documentation examples with real data from SQL"""
    
    def __init__(self, extracted_data: Dict[str, Any]):
        self.data = extracted_data
        self.swagger_config_path = "api-gateway/src/config/swagger.js"
        self.backup_dir = "scripts/sql-driven-testing/backups"
        
    def update_swagger_examples(self) -> Dict[str, Any]:
        """Update all Swagger examples with real data from SQL"""
        logger.info("Starting Swagger examples update with real SQL data")
        
        # Create backup
        self.create_backup()
        
        # Load current Swagger configuration
        swagger_config = self.load_swagger_config()
        
        # Generate new examples based on extracted data
        new_examples = self.generate_all_examples()
        
        # Update the configuration with new examples
        updated_config = self.integrate_examples(swagger_config, new_examples)
        
        # Save updated configuration
        self.save_swagger_config(updated_config)
        
        # Validate the updated configuration
        validation_result = self.validate_updated_examples()
        
        result = {
            'examples_updated': list(new_examples.keys()),
            'backup_created': True,
            'validation_passed': validation_result['valid'],
            'total_examples': len(new_examples),
            'updated_schemas': self.get_updated_schema_count(new_examples)
        }
        
        logger.info(f"Swagger examples update completed: {result['total_examples']} examples updated")
        return result
    
    def create_backup(self):
        """Create backup of current Swagger configuration"""
        os.makedirs(self.backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"swagger_config_backup_{timestamp}.js"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        shutil.copy2(self.swagger_config_path, backup_path)
        logger.info(f"Swagger configuration backed up to: {backup_path}")
    
    def load_swagger_config(self) -> str:
        """Load current Swagger configuration file"""
        try:
            with open(self.swagger_config_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Swagger configuration file not found: {self.swagger_config_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading Swagger configuration: {e}")
            raise
    
    def save_swagger_config(self, config_content: str):
        """Save updated Swagger configuration"""
        try:
            with open(self.swagger_config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            logger.info(f"Updated Swagger configuration saved to: {self.swagger_config_path}")
        except Exception as e:
            logger.error(f"Error saving Swagger configuration: {e}")
            raise
    
    def generate_all_examples(self) -> Dict[str, Dict]:
        """Generate all examples based on extracted SQL data"""
        logger.info("Generating examples from extracted SQL data")
        
        examples = {
            'authentication': self.generate_auth_examples(),
            'users': self.generate_users_examples(),
            'inventory': self.generate_inventory_examples(),
            'events': self.generate_events_examples(),
            'network': self.generate_network_examples()
        }
        
        return examples
    
    def generate_auth_examples(self) -> Dict[str, Any]:
        """Generate authentication examples with real user data"""
        logger.info("Generating authentication examples")
        
        # Get test users for different roles
        presidente = self.get_user_by_role('PRESIDENTE')
        vocal = self.get_user_by_role('VOCAL')
        coordinador = self.get_user_by_role('COORDINADOR')
        voluntario = self.get_user_by_role('VOLUNTARIO')
        
        return {
            'LoginRequest': {
                'summary': 'Login con usuario Presidente',
                'value': {
                    'identificador': presidente['nombre_usuario'],
                    'clave': presidente['password_plain']
                }
            },
            'LoginRequestVocal': {
                'summary': 'Login con usuario Vocal',
                'value': {
                    'identificador': vocal['nombre_usuario'],
                    'clave': vocal['password_plain']
                }
            },
            'LoginRequestCoordinador': {
                'summary': 'Login con usuario Coordinador',
                'value': {
                    'identificador': coordinador['nombre_usuario'],
                    'clave': coordinador['password_plain']
                }
            },
            'LoginRequestVoluntario': {
                'summary': 'Login con usuario Voluntario',
                'value': {
                    'identificador': voluntario['nombre_usuario'],
                    'clave': voluntario['password_plain']
                }
            },
            'LoginResponse': {
                'summary': 'Respuesta exitosa de login',
                'value': {
                    'mensaje': 'Login exitoso',
                    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibm9tYnJlVXN1YXJpbyI6InRlc3RfcHJlc2lkZW50ZSIsInJvbCI6IlBSRVNJREVOVEUiLCJpYXQiOjE2NDA5OTUyMDAsImV4cCI6MTY0MTA4MTYwMH0.example',
                    'usuario': {
                        'id': presidente['id'],
                        'nombreUsuario': presidente['nombre_usuario'],
                        'nombre': presidente['nombre'],
                        'apellido': presidente['apellido'],
                        'email': presidente['email'],
                        'rol': presidente['rol'],
                        'activo': presidente['activo']
                    }
                }
            },
            'LoginError': {
                'summary': 'Error de credenciales inválidas',
                'value': {
                    'error': 'Unauthorized',
                    'mensaje': 'Credenciales inválidas',
                    'codigo': 'INVALID_CREDENTIALS'
                }
            }
        }
    
    def generate_users_examples(self) -> Dict[str, Any]:
        """Generate user management examples with real user data"""
        logger.info("Generating user management examples")
        
        # Get users from different roles
        all_users = []
        for role, users in self.data['users'].items():
            all_users.extend(users)
        
        presidente = self.get_user_by_role('PRESIDENTE')
        vocal = self.get_user_by_role('VOCAL')
        
        return {
            'UsuariosList': {
                'summary': 'Lista de usuarios del sistema',
                'value': [
                    {
                        'id': user['id'],
                        'nombreUsuario': user['nombre_usuario'],
                        'nombre': user['nombre'],
                        'apellido': user['apellido'],
                        'email': user['email'],
                        'rol': user['rol'],
                        'activo': user['activo'],
                        'fechaHoraAlta': user['fecha_hora_alta'],
                        'usuarioAlta': user['usuario_alta']
                    } for user in all_users[:4]  # Show first 4 users as example
                ]
            },
            'UsuarioDetalle': {
                'summary': 'Detalle de usuario específico',
                'value': {
                    'id': presidente['id'],
                    'nombreUsuario': presidente['nombre_usuario'],
                    'nombre': presidente['nombre'],
                    'apellido': presidente['apellido'],
                    'telefono': presidente['telefono'],
                    'email': presidente['email'],
                    'rol': presidente['rol'],
                    'activo': presidente['activo'],
                    'fechaHoraAlta': presidente['fecha_hora_alta'],
                    'usuarioAlta': presidente['usuario_alta']
                }
            },
            'CrearUsuario': {
                'summary': 'Crear nuevo usuario',
                'value': {
                    'nombreUsuario': 'nuevo_voluntario',
                    'nombre': 'María',
                    'apellido': 'González',
                    'telefono': '+54 11 9876-5432',
                    'email': 'maria.gonzalez@ong.com',
                    'clave': 'password123',
                    'rol': 'VOLUNTARIO'
                }
            },
            'ActualizarUsuario': {
                'summary': 'Actualizar datos de usuario',
                'value': {
                    'nombre': vocal['nombre'] + ' Actualizado',
                    'apellido': vocal['apellido'],
                    'telefono': '+54 11 1111-2222',
                    'email': vocal['email']
                }
            }
        }
    
    def generate_inventory_examples(self) -> Dict[str, Any]:
        """Generate inventory examples with real donation data"""
        logger.info("Generating inventory examples")
        
        # Get donations from different categories and stock levels (with fallbacks)
        try:
            high_stock_alimentos = self.get_donation_by_category_and_stock('ALIMENTOS', 'high_stock')
        except ValueError:
            high_stock_alimentos = {'id': 101, 'categoria': 'ALIMENTOS', 'descripcion': 'Sample Food', 'cantidad': 100}
        
        try:
            medium_stock_ropa = self.get_donation_by_category_and_stock('ROPA', 'medium_stock')
        except ValueError:
            medium_stock_ropa = {'id': 201, 'categoria': 'ROPA', 'descripcion': 'Sample Clothing', 'cantidad': 30}
        
        try:
            low_stock_juguetes = self.get_donation_by_category_and_stock('JUGUETES', 'low_stock')
        except ValueError:
            low_stock_juguetes = {'id': 301, 'categoria': 'JUGUETES', 'descripcion': 'Sample Toys', 'cantidad': 5}
        
        try:
            zero_stock_utiles = self.get_donation_by_category_and_stock('UTILES_ESCOLARES', 'zero_stock')
        except ValueError:
            zero_stock_utiles = {'id': 401, 'categoria': 'UTILES_ESCOLARES', 'descripcion': 'Sample School Supplies', 'cantidad': 0}
        
        # Get sample donations for list
        sample_donations = []
        for categoria in ['ALIMENTOS', 'ROPA', 'JUGUETES', 'UTILES_ESCOLARES']:
            if categoria in self.data['inventory'] and self.data['inventory'][categoria]['all']:
                sample_donations.append(self.data['inventory'][categoria]['all'][0])
        
        return {
            'DonacionesList': {
                'summary': 'Lista de donaciones en inventario',
                'value': [
                    {
                        'id': donation['id'],
                        'categoria': donation['categoria'],
                        'descripcion': donation['descripcion'],
                        'cantidad': donation['cantidad'],
                        'eliminado': donation.get('eliminado', False),
                        'fechaHoraAlta': donation['fecha_hora_alta'],
                        'usuarioAlta': donation['usuario_alta']
                    } for donation in sample_donations
                ]
            },
            'DonacionDetalle': {
                'summary': 'Detalle de donación específica',
                'value': {
                    'id': high_stock_alimentos['id'],
                    'categoria': high_stock_alimentos['categoria'],
                    'descripcion': high_stock_alimentos['descripcion'],
                    'cantidad': high_stock_alimentos['cantidad'],
                    'eliminado': high_stock_alimentos.get('eliminado', False),
                    'fechaHoraAlta': high_stock_alimentos['fecha_hora_alta'],
                    'usuarioAlta': high_stock_alimentos['usuario_alta'],
                    'fechaHoraModificacion': high_stock_alimentos.get('fecha_hora_modificacion'),
                    'usuarioModificacion': high_stock_alimentos.get('usuario_modificacion')
                }
            },
            'CrearDonacion': {
                'summary': 'Crear nueva donación',
                'value': {
                    'categoria': 'ALIMENTOS',
                    'descripcion': 'Arroz integral 1kg - Donación nueva',
                    'cantidad': 30
                }
            },
            'ActualizarDonacion': {
                'summary': 'Actualizar donación existente',
                'value': {
                    'descripcion': medium_stock_ropa['descripcion'] + ' - Actualizado',
                    'cantidad': medium_stock_ropa['cantidad'] + 5
                }
            },
            'DonacionStockAlto': {
                'summary': 'Donación con stock alto (>50)',
                'value': {
                    'id': high_stock_alimentos['id'],
                    'categoria': high_stock_alimentos['categoria'],
                    'descripcion': high_stock_alimentos['descripcion'],
                    'cantidad': high_stock_alimentos['cantidad']
                }
            },
            'DonacionStockBajo': {
                'summary': 'Donación con stock bajo (<10)',
                'value': {
                    'id': low_stock_juguetes['id'],
                    'categoria': low_stock_juguetes['categoria'],
                    'descripcion': low_stock_juguetes['descripcion'],
                    'cantidad': low_stock_juguetes['cantidad']
                }
            },
            'DonacionSinStock': {
                'summary': 'Donación sin stock (cantidad = 0)',
                'value': {
                    'id': zero_stock_utiles['id'],
                    'categoria': zero_stock_utiles['categoria'],
                    'descripcion': zero_stock_utiles['descripcion'],
                    'cantidad': zero_stock_utiles['cantidad']
                }
            }
        }
    
    def generate_events_examples(self) -> Dict[str, Any]:
        """Generate events examples with real event data"""
        logger.info("Generating events examples")
        
        # Get events from different temporal categories
        future_event = self.data['events']['future'][0] if self.data['events']['future'] else None
        past_event = self.data['events']['past'][0] if self.data['events']['past'] else None
        
        # Get sample events for list
        sample_events = self.data['events']['all'][:3]  # First 3 events
        
        return {
            'EventosList': {
                'summary': 'Lista de eventos solidarios',
                'value': [
                    {
                        'id': event['id'],
                        'nombre': event['nombre'],
                        'descripcion': event['descripcion'],
                        'fechaHora': event['fecha_hora'],
                        'totalParticipantes': event['total_participantes'],
                        'fechaHoraAlta': event['fecha_hora_alta'],
                        'usuarioAlta': event['usuario_alta']
                    } for event in sample_events
                ]
            },
            'EventoDetalle': {
                'summary': 'Detalle de evento específico',
                'value': {
                    'id': future_event['id'],
                    'nombre': future_event['nombre'],
                    'descripcion': future_event['descripcion'],
                    'fechaHora': future_event['fecha_hora'],
                    'participantesIds': future_event['participantes'],
                    'totalParticipantes': future_event['total_participantes'],
                    'fechaHoraAlta': future_event['fecha_hora_alta'],
                    'usuarioAlta': future_event['usuario_alta']
                } if future_event else {}
            },
            'CrearEvento': {
                'summary': 'Crear nuevo evento futuro',
                'value': {
                    'nombre': 'Distribución de alimentos - Barrio Norte',
                    'descripcion': 'Evento solidario para distribuir alimentos a familias necesitadas del barrio norte',
                    'fechaHora': '2024-03-15T14:00:00Z'
                }
            },
            'ActualizarEvento': {
                'summary': 'Actualizar evento existente',
                'value': {
                    'nombre': future_event['nombre'] + ' - Actualizado',
                    'descripcion': future_event['descripcion'] + ' (Información actualizada)',
                    'fechaHora': future_event['fecha_hora']
                } if future_event else {}
            },
            'EventoFuturo': {
                'summary': 'Evento futuro válido',
                'value': {
                    'id': future_event['id'],
                    'nombre': future_event['nombre'],
                    'fechaHora': future_event['fecha_hora'],
                    'participantes': future_event['participantes']
                } if future_event else {}
            },
            'EventoPasado': {
                'summary': 'Evento pasado (solo consulta)',
                'value': {
                    'id': past_event['id'],
                    'nombre': past_event['nombre'],
                    'fechaHora': past_event['fecha_hora'],
                    'participantes': past_event['participantes']
                } if past_event else {}
            },
            'UnirseEvento': {
                'summary': 'Unirse a evento como participante',
                'value': {
                    'usuarioId': self.get_user_by_role('VOLUNTARIO')['id']
                }
            }
        }
    
    def generate_network_examples(self) -> Dict[str, Any]:
        """Generate inter-NGO network examples with real network data"""
        logger.info("Generating network examples")
        
        # Get network data
        external_request = self.data['network']['external_requests'][0] if self.data['network']['external_requests'] else None
        external_offer = self.data['network']['external_offers'][0] if self.data['network']['external_offers'] else None
        external_event = self.data['network']['external_events'][0] if self.data['network']['external_events'] else None
        
        # Get donation for transfer example
        transfer_donation = self.get_donation_by_category_and_stock('ALIMENTOS', 'high_stock')
        
        return {
            'SolicitudesExternas': {
                'summary': 'Lista de solicitudes de otras ONGs',
                'value': [
                    {
                        'idOrganizacion': req['id_organizacion'],
                        'idSolicitud': req['id_solicitud'],
                        'categoria': req['categoria'],
                        'descripcion': req['descripcion'],
                        'activa': req['activa'],
                        'fechaRecepcion': req['fecha_recepcion']
                    } for req in self.data['network']['external_requests'][:3]
                ]
            },
            'CrearSolicitudDonaciones': {
                'summary': 'Crear solicitud de donaciones a la red',
                'value': {
                    'donaciones': [
                        {
                            'categoria': 'ALIMENTOS',
                            'descripcion': 'Arroz y fideos para familias necesitadas'
                        },
                        {
                            'categoria': 'ROPA',
                            'descripcion': 'Ropa de abrigo para niños'
                        }
                    ]
                }
            },
            'OfertasExternas': {
                'summary': 'Lista de ofertas de otras ONGs',
                'value': [
                    {
                        'idOrganizacion': offer['id_organizacion'],
                        'idOferta': offer['id_oferta'],
                        'categoria': offer['categoria'],
                        'descripcion': offer['descripcion'],
                        'cantidad': offer['cantidad'],
                        'fechaRecepcion': offer['fecha_recepcion']
                    } for offer in self.data['network']['external_offers'][:3]
                ]
            },
            'CrearOfertaDonaciones': {
                'summary': 'Crear oferta de donaciones a la red',
                'value': {
                    'donaciones': [
                        {
                            'donacionId': transfer_donation['id'],
                            'categoria': transfer_donation['categoria'],
                            'descripcion': transfer_donation['descripcion'],
                            'cantidad': min(20, transfer_donation['cantidad'])
                        }
                    ]
                }
            },
            'TransferirDonaciones': {
                'summary': 'Transferir donaciones a otra ONG',
                'value': {
                    'idSolicitud': external_request['id_solicitud'] if external_request else 'SOL-2024-001',
                    'organizacionDestino': external_request['id_organizacion'] if external_request else 'ong-corazon-solidario',
                    'donaciones': [
                        {
                            'donacionId': transfer_donation['id'],
                            'cantidad': min(15, transfer_donation['cantidad'])
                        }
                    ]
                }
            },
            'EventosExternos': {
                'summary': 'Lista de eventos de otras ONGs',
                'value': [
                    {
                        'idOrganizacion': event['id_organizacion'],
                        'idEvento': event['id_evento'],
                        'nombre': event['nombre'],
                        'descripcion': event['descripcion'],
                        'fechaHora': event['fecha_hora'],
                        'activo': event['activo'],
                        'fechaRecepcion': event['fecha_recepcion']
                    } for event in self.data['network']['external_events'][:3]
                ]
            },
            'AdhesionEventoExterno': {
                'summary': 'Adherirse a evento de otra ONG',
                'value': {
                    'idEvento': external_event['id_evento'] if external_event else 'EV-2024-001',
                    'idOrganizacion': external_event['id_organizacion'] if external_event else 'ong-corazones-solidarios',
                    'usuarioId': self.get_user_by_role('VOLUNTARIO')['id']
                }
            }
        }
    
    def integrate_examples(self, swagger_config: str, new_examples: Dict[str, Dict]) -> str:
        """Integrate new examples into the existing Swagger configuration"""
        logger.info("Integrating new examples into Swagger configuration")
        
        # Find the examples section in the configuration
        examples_pattern = r'(examples:\s*{)(.*?)(}\s*},\s*security:)'
        
        # Build new examples object
        examples_js = self.build_examples_javascript(new_examples)
        
        # Replace the examples section
        def replace_examples(match):
            return f"{match.group(1)}\n{examples_js}\n        {match.group(3)}"
        
        updated_config = re.sub(examples_pattern, replace_examples, swagger_config, flags=re.DOTALL)
        
        if updated_config == swagger_config:
            logger.warning("No examples section found in Swagger config, appending examples")
            # If no examples section found, add it before security
            security_pattern = r'(\s*},\s*security:)'
            examples_section = f",\n      examples: {{\n{examples_js}\n      }}"
            updated_config = re.sub(security_pattern, f"{examples_section}\\1", swagger_config)
        
        return updated_config
    
    def build_examples_javascript(self, examples: Dict[str, Dict]) -> str:
        """Build JavaScript object string for examples"""
        js_lines = []
        
        for category, category_examples in examples.items():
            js_lines.append(f"        // {category.title()} Examples")
            
            for example_name, example_data in category_examples.items():
                js_lines.append(f"        {example_name}: {{")
                js_lines.append(f"          summary: '{example_data['summary']}',")
                js_lines.append(f"          value: {json.dumps(example_data['value'], indent=10)}")
                js_lines.append("        },")
            
            js_lines.append("")  # Empty line between categories
        
        # Remove last comma and empty line
        if js_lines and js_lines[-2].endswith(','):
            js_lines[-2] = js_lines[-2][:-1]
        if js_lines and js_lines[-1] == "":
            js_lines.pop()
        
        return "\n".join(js_lines)
    
    def validate_updated_examples(self) -> Dict[str, Any]:
        """Validate that the updated examples are syntactically correct"""
        logger.info("Validating updated Swagger configuration")
        
        try:
            # Try to load the updated configuration as a Node.js module
            # This is a basic syntax check
            with open(self.swagger_config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            # Basic validation checks
            validation_errors = []
            
            # Check for balanced braces
            open_braces = config_content.count('{')
            close_braces = config_content.count('}')
            if open_braces != close_braces:
                validation_errors.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")
            
            # Check for balanced brackets
            open_brackets = config_content.count('[')
            close_brackets = config_content.count(']')
            if open_brackets != close_brackets:
                validation_errors.append(f"Unbalanced brackets: {open_brackets} open, {close_brackets} close")
            
            # Check for basic JavaScript syntax issues
            if 'examples: {' not in config_content:
                validation_errors.append("Examples section not found in configuration")
            
            # Check that all required sections are present
            required_sections = ['LoginRequest', 'UsuariosList', 'DonacionesList', 'EventosList', 'SolicitudesExternas']
            for section in required_sections:
                if section not in config_content:
                    validation_errors.append(f"Required example section missing: {section}")
            
            return {
                'valid': len(validation_errors) == 0,
                'errors': validation_errors,
                'total_checks': 5
            }
            
        except Exception as e:
            logger.error(f"Error validating Swagger configuration: {e}")
            return {
                'valid': False,
                'errors': [str(e)],
                'total_checks': 1
            }
    
    def get_updated_schema_count(self, examples: Dict[str, Dict]) -> int:
        """Count the number of schema examples that were updated"""
        total_count = 0
        for category_examples in examples.values():
            total_count += len(category_examples)
        return total_count
    
    # Helper methods to get specific data from extracted data
    
    def get_user_by_role(self, role: str) -> Dict:
        """Get the first user with the specified role"""
        if role in self.data['users'] and self.data['users'][role]:
            return self.data['users'][role][0]
        raise ValueError(f"No test user found with role: {role}")
    
    def get_donation_by_category_and_stock(self, category: str, stock_level: str) -> Dict:
        """Get a donation by category and stock level"""
        if (category in self.data['inventory'] and 
            stock_level in self.data['inventory'][category] and 
            self.data['inventory'][category][stock_level]):
            return self.data['inventory'][category][stock_level][0]
        
        # Fallback to any donation in the category from any stock level
        if category in self.data['inventory']:
            for level in ['high_stock', 'medium_stock', 'low_stock', 'zero_stock']:
                if (level in self.data['inventory'][category] and 
                    self.data['inventory'][category][level]):
                    return self.data['inventory'][category][level][0]
            
            # Final fallback to 'all' if it exists
            if self.data['inventory'][category]['all']:
                return self.data['inventory'][category]['all'][0]
        
        raise ValueError(f"No donation found for category: {category}, stock level: {stock_level}")
    
    def get_event_by_status(self, status: str) -> Optional[Dict]:
        """Get an event by temporal status"""
        if status in self.data['events'] and self.data['events'][status]:
            return self.data['events'][status][0]
        return None

def main():
    """Example usage of SwaggerGenerator"""
    # This would typically be called from the orchestrator
    # with real extracted data
    
    print("SwaggerGenerator created successfully")
    print("Use this class with extracted SQL data to update Swagger examples")
    print("\nExample usage:")
    print("generator = SwaggerGenerator(extracted_data)")
    print("result = generator.update_swagger_examples()")

if __name__ == "__main__":
    main()